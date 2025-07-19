use std::ffi::{CString, CStr};
use std::os::raw::{c_char, c_int};
use std::io::{self, Read};
use anyhow::Result;
use clap::Parser;

// Direct FFI bindings to Whisper
#[link(name = "whisper")]
extern "C" {
    fn whisper_init_from_file(path_model: *const c_char) -> *mut std::ffi::c_void;
    fn whisper_free(ctx: *mut std::ffi::c_void);
    fn whisper_full(
        ctx: *mut std::ffi::c_void,
        params: whisper_full_params,
        samples: *const f32,
        n_samples: c_int,
    ) -> c_int;
    fn whisper_full_n_segments(ctx: *mut std::ffi::c_void) -> c_int;
    fn whisper_full_get_segment_text(ctx: *mut std::ffi::c_void, i_segment: c_int) -> *const c_char;
}

#[repr(C)]
struct whisper_full_params {
    strategy: c_int,
    n_threads: c_int,
    n_max_text_ctx: c_int,
    offset_ms: c_int,
    duration_ms: c_int,
    translate: bool,
    no_context: bool,
    no_timestamps: bool,
    single_segment: bool,
    print_special: bool,
    print_progress: bool,
    print_timestamps: bool,
    print_tokens: bool,
    token_timestamps: bool,
    speed_up: bool,
    output_txt: bool,
    output_vtt: bool,
    output_srt: bool,
    output_wts: bool,
    output_csv: bool,
    output_jsn: bool,
    output_lrc: bool,
    output_word_timestamps: bool,
    word_thold: f32,
    max_len: c_int,
    max_tokens: c_int,
    audio_ctx: c_int,
    tdrz_enable: bool,
    initial_prompt: *const c_char,
    prompt_tokens: *const whisper_token,
    prompt_n_tokens: c_int,
    language: *const c_char,
    detect_language: bool,
    suppress_blank: bool,
    suppress_non_speech_tokens: bool,
    temperature: f32,
    max_initial_timestamp: f32,
    length_penalty: f32,
    temperature_inc: f32,
    entropy_thold: f32,
    logprob_thold: f32,
    no_speech_thold: f32,
    greedy: whisper_greedy,
    beam_search: whisper_beam_search,
    best_of: c_int,
    beam_size: c_int,
    patience: f32,
    length_penalty_beam: f32,
    group_size: c_int,
}

#[repr(C)]
struct whisper_greedy {
    best_of: c_int,
}

#[repr(C)]
struct whisper_beam_search {
    beam_size: c_int,
    n_best: c_int,
    patience: f32,
    length_penalty: f32,
}

type whisper_token = c_int;

fn transcribe_audio(audio: &[f32]) -> Result<String> {
    // Ensure audio is in the correct format (16kHz, mono, float32)
    let resampled_audio = resample_to_16khz(audio, 16000);
    
    // Convert to C string for model path
    let model_path = CString::new("/app/models/ggml-base.en.bin")?;
    
    // Initialize Whisper context
    let ctx = unsafe {
        whisper_init_from_file(model_path.as_ptr())
    };
    
    if ctx.is_null() {
        return Err(anyhow::anyhow!("Failed to initialize Whisper context"));
    }
    
    // Set up parameters - explicitly disable GPU and VAD to avoid QEMU issues
    let params = whisper_full_params {
        strategy: 0, // WHISPER_SAMPLING_GREEDY
        n_threads: 1, // Use single thread to avoid emulation issues
        n_max_text_ctx: 16384,
        offset_ms: 0,
        duration_ms: 0,
        translate: false,
        no_context: false,
        no_timestamps: false,
        single_segment: true, // Force single segment to avoid VAD issues
        print_special: false,
        print_progress: false,
        print_timestamps: false,
        print_tokens: false,
        token_timestamps: false,
        speed_up: false,
        output_txt: false,
        output_vtt: false,
        output_srt: false,
        output_wts: false,
        output_csv: false,
        output_jsn: false,
        output_lrc: false,
        output_word_timestamps: false,
        word_thold: 0.0,
        max_len: 0,
        max_tokens: 0,
        audio_ctx: 0,
        tdrz_enable: false,
        initial_prompt: std::ptr::null(),
        prompt_tokens: std::ptr::null(),
        prompt_n_tokens: 0,
        language: std::ptr::null(),
        detect_language: false,
        suppress_blank: false,
        suppress_non_speech_tokens: false,
        temperature: 0.0,
        max_initial_timestamp: 1.0,
        length_penalty: 1.0,
        temperature_inc: 0.0,
        entropy_thold: 2.4,
        logprob_thold: -1.0,
        no_speech_thold: 999.0, // Very high value to disable VAD
        greedy: whisper_greedy { best_of: 1 },
        beam_search: whisper_beam_search {
            beam_size: 5,
            n_best: 5,
            patience: 1.0,
            length_penalty: 1.0,
        },
        best_of: 1,
        beam_size: 5,
        patience: 1.0,
        length_penalty_beam: 1.0,
        group_size: 1,
    };
    
    // Run transcription
    let result = unsafe {
        whisper_full(ctx, params, resampled_audio.as_ptr(), resampled_audio.len() as c_int)
    };
    
    if result != 0 {
        unsafe { whisper_free(ctx) };
        return Err(anyhow::anyhow!("Whisper transcription failed"));
    }
    
    // Get the result
    let n_segments = unsafe { whisper_full_n_segments(ctx) };
    if n_segments == 0 {
        unsafe { whisper_free(ctx) };
        return Ok("".to_string());
    }
    
    // Concatenate all segments
    let mut result = String::new();
    for i in 0..n_segments {
        let text_ptr = unsafe { whisper_full_get_segment_text(ctx, i) };
        if !text_ptr.is_null() {
            let text = unsafe { CStr::from_ptr(text_ptr) };
            if let Ok(text_str) = text.to_str() {
                result.push_str(text_str);
                result.push(' ');
            }
        }
    }
    
    // Clean up
    unsafe { whisper_free(ctx) };
    
    Ok(result)
}

fn resample_to_16khz(input: &[f32], input_sample_rate: u32) -> Vec<f32> {
    if input_sample_rate == 16000 {
        return input.to_vec();
    }
    
    let ratio = input_sample_rate as f64 / 16000.0;
    let output_len = (input.len() as f64 / ratio) as usize;
    let mut output = Vec::with_capacity(output_len);
    
    for i in 0..output_len {
        let input_idx = (i as f64 * ratio) as usize;
        if input_idx < input.len() {
            output.push(input[input_idx]);
        }
    }
    
    output
}

fn bytes_to_f32_audio(bytes: &[u8]) -> Vec<f32> {
    // Convert bytes to f32 audio samples
    // Assuming 16-bit PCM audio
    let mut audio = Vec::with_capacity(bytes.len() / 2);
    for i in (0..bytes.len()).step_by(2) {
        if i + 1 < bytes.len() {
            let sample = ((bytes[i + 1] as i16) << 8) | (bytes[i] as i16);
            audio.push(sample as f32 / 32768.0);
        }
    }
    audio
}

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Path to Whisper model file
    #[arg(short, long, default_value = "/app/models/ggml-base.en.bin")]
    model: String,
    
    /// Test transcription with a simple audio file
    #[arg(short, long)]
    test: bool,
    
    /// Transcribe audio from stdin
    #[arg(short, long)]
    stdin: bool,
}

fn main() -> Result<()> {
    let args = Args::parse();
    
    if args.stdin {
        // Read audio data from stdin
        let mut audio_data = Vec::new();
        io::stdin().read_to_end(&mut audio_data)?;
        
        if audio_data.is_empty() {
            return Err(anyhow::anyhow!("No audio data received"));
        }
        
        // Convert bytes to f32 audio
        let audio_samples = bytes_to_f32_audio(&audio_data);
        
        // Transcribe the audio
        match transcribe_audio(&audio_samples) {
            Ok(transcription) => {
                if !transcription.trim().is_empty() {
                    println!("{}", transcription.trim());
                }
            }
            Err(e) => {
                eprintln!("Transcription failed: {}", e);
                std::process::exit(1);
            }
        }
    } else if args.test {
        println!("Testing basic functionality...");
        
        // Create a simple test audio signal (1 second of 440Hz sine wave)
        let sample_rate = 16000;
        let duration = 1.0; // 1 second
        let frequency = 440.0; // 440Hz
        let num_samples = (sample_rate as f32 * duration) as usize;
        
        let mut test_audio = Vec::with_capacity(num_samples);
        for i in 0..num_samples {
            let t = i as f32 / sample_rate as f32;
            let sample = (2.0 * std::f32::consts::PI * frequency * t).sin() * 0.1;
            test_audio.push(sample);
        }
        
        println!("Testing transcription with {} samples...", test_audio.len());
        match transcribe_audio(&test_audio) {
            Ok(transcription) => {
                println!("Transcription result: '{}'", transcription);
                if transcription.trim().is_empty() {
                    println!("Note: Empty transcription is expected for a pure sine wave (no speech content)");
                }
            }
            Err(e) => {
                eprintln!("Transcription failed: {}", e);
            }
        }
    } else {
        println!("Backend service ready. Use --test to run a test transcription.");
        println!("Use --stdin to transcribe audio from stdin.");
    }
    
    Ok(())
}

