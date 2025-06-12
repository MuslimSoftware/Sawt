use std::ffi::{CString, CStr};
use std::os::raw::c_char;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use std::collections::VecDeque;
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use anyhow::Result;

extern "C" {
    fn whisper_transcribe(
        model_path: *const c_char,
        audio_data: *const f32,
        num_samples: usize,
    ) -> *const c_char;

    fn whisper_free_result(ptr: *const c_char);
}

#[derive(Clone)]
struct AudioConfig {
    sample_rate: u32,
    channels: u16,
    chunk_size: usize,
}

struct VoiceActivityDetector {
    energy_threshold: f32,
    speech_frames: usize,
    silence_frames: usize,
    min_speech_frames: usize,
    min_silence_frames: usize,
    is_speech_active: bool,
}

impl VoiceActivityDetector {
    fn new() -> Self {
        Self {
            energy_threshold: 0.0005, // Lower threshold for better sensitivity
            speech_frames: 0,
            silence_frames: 0,
            min_speech_frames: 5,    // ~100ms at 48kHz with 1024 samples per frame
            min_silence_frames: 50,  // ~1000ms (1 second) of silence to end speech
            is_speech_active: false,
        }
    }
    
    fn calculate_energy(&self, samples: &[f32]) -> f32 {
        samples.iter().map(|&s| s * s).sum::<f32>() / samples.len() as f32
    }
    
    fn process_frame(&mut self, samples: &[f32]) -> VadResult {
        let energy = self.calculate_energy(samples);
        
        if energy > self.energy_threshold {
            self.speech_frames += 1;
            self.silence_frames = 0;
            
            if !self.is_speech_active && self.speech_frames >= self.min_speech_frames {
                self.is_speech_active = true;
                return VadResult::SpeechStart;
            }
        } else {
            self.silence_frames += 1;
            // Don't reset speech_frames immediately - allow for brief pauses
            if self.silence_frames > self.min_silence_frames / 2 {
                self.speech_frames = 0;
            }
            
            if self.is_speech_active && self.silence_frames >= self.min_silence_frames {
                self.is_speech_active = false;
                return VadResult::SpeechEnd;
            }
        }
        
        if self.is_speech_active {
            VadResult::Speech
        } else {
            VadResult::Silence
        }
    }
}

#[derive(Debug, PartialEq)]
enum VadResult {
    Silence,
    Speech,
    SpeechStart,
    SpeechEnd,
}

struct ContinuousRecorder {
    audio_buffer: VecDeque<f32>,
    speech_buffer: Vec<f32>,
    vad: VoiceActivityDetector,
    config: AudioConfig,
    max_buffer_size: usize,
    recording_speech: bool,
    speech_start_time: Option<Instant>,
    max_speech_duration: Duration,
}

impl ContinuousRecorder {
    fn new(config: AudioConfig) -> Self {
        let max_buffer_size = config.sample_rate as usize * 30; // 30 seconds max
        
        Self {
            audio_buffer: VecDeque::with_capacity(max_buffer_size),
            speech_buffer: Vec::new(),
            vad: VoiceActivityDetector::new(),
            config,
            max_buffer_size,
            recording_speech: false,
            speech_start_time: None,
            max_speech_duration: Duration::from_secs(10), // Max 10 seconds per speech segment
        }
    }
    
    fn process_audio_chunk(&mut self, samples: &[f32]) -> Option<Vec<f32>> {
        // Add to circular buffer
        for &sample in samples {
            if self.audio_buffer.len() >= self.max_buffer_size {
                self.audio_buffer.pop_front();
            }
            self.audio_buffer.push_back(sample);
        }
        
        // Voice activity detection
        let vad_result = self.vad.process_frame(samples);
        
        match vad_result {
            VadResult::SpeechStart => {
                println!("🎤 Speech detected, recording...");
                self.recording_speech = true;
                self.speech_start_time = Some(Instant::now());
                self.speech_buffer.clear();
                
                // Include some pre-speech audio for better transcription
                let pre_speech_samples = (self.config.sample_rate as f32 * 0.3) as usize; // 300ms
                let start_idx = if self.audio_buffer.len() > pre_speech_samples {
                    self.audio_buffer.len() - pre_speech_samples
                } else {
                    0
                };
                
                for i in start_idx..self.audio_buffer.len() {
                    if let Some(&sample) = self.audio_buffer.get(i) {
                        self.speech_buffer.push(sample);
                    }
                }
            }
            VadResult::Speech => {
                if self.recording_speech {
                    self.speech_buffer.extend_from_slice(samples);
                    
                    // Check for maximum speech duration
                    if let Some(start_time) = self.speech_start_time {
                        if start_time.elapsed() > self.max_speech_duration {
                            println!("⏰ Maximum speech duration reached, processing...");
                            self.recording_speech = false;
                            self.speech_start_time = None;
                            
                            if !self.speech_buffer.is_empty() {
                                let speech_audio = self.speech_buffer.clone();
                                self.speech_buffer.clear();
                                return Some(speech_audio);
                            }
                        }
                    }
                }
            }
            VadResult::SpeechEnd => {
                if self.recording_speech {
                    let duration = self.speech_start_time
                        .map(|start| start.elapsed())
                        .unwrap_or(Duration::from_secs(0));
                    
                    println!("🔇 Speech ended after {:.1}s, processing...", duration.as_secs_f32());
                    self.recording_speech = false;
                    self.speech_start_time = None;
                    
                    if !self.speech_buffer.is_empty() {
                        let speech_audio = self.speech_buffer.clone();
                        self.speech_buffer.clear();
                        return Some(speech_audio);
                    }
                }
            }
            VadResult::Silence => {
                // Continue silence
            }
        }
        
        None
    }
}

fn resample_to_16khz(input: &[f32], input_sample_rate: u32) -> Vec<f32> {
    if input_sample_rate == 16000 {
        return input.to_vec();
    }
    
    let ratio = input_sample_rate as f64 / 16000.0;
    let output_len = (input.len() as f64 / ratio) as usize;
    let mut output = Vec::with_capacity(output_len);
    
    for i in 0..output_len {
        let src_index = (i as f64 * ratio) as usize;
        if src_index < input.len() {
            output.push(input[src_index]);
        }
    }
    
    output
}

fn transcribe_audio(audio: &[f32]) -> Result<String> {
    let model_path = CString::new("../library/models/ggml-base.en.bin")?;
    
    unsafe {
        let result_ptr = whisper_transcribe(
            model_path.as_ptr(), 
            audio.as_ptr(), 
            audio.len()
        );
        
        let result = CStr::from_ptr(result_ptr).to_string_lossy().into_owned();
        whisper_free_result(result_ptr);
        
        Ok(result)
    }
}

fn start_continuous_recording() -> Result<()> {
    let host = cpal::default_host();
    let device = host.default_input_device()
        .ok_or_else(|| anyhow::anyhow!("No input device available"))?;
    
    println!("🎯 Sawt Continuous Voice Recognition");
    println!("Using input device: {}", device.name()?);
    
    let config = device.default_input_config()?;
    let sample_rate = config.sample_rate().0;
    let channels = config.channels();
    
    println!("Audio config: {}Hz, {} channel(s)", sample_rate, channels);
    
    let stream_config = cpal::StreamConfig {
        channels,
        sample_rate: config.sample_rate(),
        buffer_size: cpal::BufferSize::Default,
    };
    
    let audio_config = AudioConfig {
        sample_rate,
        channels,
        chunk_size: 1024,
    };
    
    let recorder = Arc::new(Mutex::new(ContinuousRecorder::new(audio_config.clone())));
    let recorder_clone = recorder.clone();
    
    let stream = device.build_input_stream(
        &stream_config,
        move |data: &[f32], _: &cpal::InputCallbackInfo| {
            let mut recorder = recorder_clone.lock().unwrap();
            
            // Convert stereo to mono if needed
            let mono_samples: Vec<f32> = if channels == 2 {
                data.chunks(2).map(|chunk| chunk[0]).collect()
            } else {
                data.to_vec()
            };
            
            // Process the audio chunk
            if let Some(speech_audio) = recorder.process_audio_chunk(&mono_samples) {
                // Speech segment detected, transcribe it
                let resampled = resample_to_16khz(&speech_audio, sample_rate);
                
                if resampled.len() > 8000 { // At least 0.5 seconds of audio
                    match transcribe_audio(&resampled) {
                        Ok(transcription) => {
                            let text = transcription.trim();
                            if !text.is_empty() && text.len() > 2 {
                                println!("🗣️  '{}' ({}ms)", text, speech_audio.len() * 1000 / sample_rate as usize);
                            }
                        }
                        Err(e) => eprintln!("Transcription error: {}", e),
                    }
                }
            }
        },
        |err| eprintln!("Audio stream error: {}", err),
        None,
    )?;
    
    println!("🎤 Listening continuously... Speak naturally!");
    println!("Press Ctrl+C to stop");
    
    stream.play()?;
    
    // Keep the stream alive
    loop {
        std::thread::sleep(Duration::from_millis(100));
    }
}

fn main() -> Result<()> {
    start_continuous_recording()
}
