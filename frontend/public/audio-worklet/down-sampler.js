/* sample-accurate 48→16 kHz + Int16 PCM */
class VoiceActivityDetector extends AudioWorkletProcessor {
  constructor(options) {
    super();
    this.voiceThreshold = options?.processorOptions?.voiceThreshold || 0.08;
    this.silenceDelayMs = options?.processorOptions?.silenceDelayMs || 600;
    this.lastVoiceTime = 0;
    this.isSpeaking = false;
  }

  process([input]) {
    const chan = input[0];
    if (!chan) {
        console.log("[VoiceActivityDetector] No channel");
        return true;
    }

    // --- RMS volume
    let sumSq = 0;
    for (let i = 0; i < chan.length; i++) sumSq += chan[i] * chan[i];
    const rms = Math.sqrt(sumSq / chan.length);

    // --- VAD
    const now = currentTime * 1000;
    if (rms > this.voiceThreshold) {
      this.lastVoiceTime = now;
      if (!this.isSpeaking) {
        this.isSpeaking = true;
        this.port.postMessage({ event: 'start' });
      }
    }

    // --- send audio if speaking
    if (this.isSpeaking) {
      const step = Math.round(sampleRate / 16_000);
      const pcm = new Int16Array(Math.ceil(chan.length / step));
      for (let i = 0; i < pcm.length; i++) {
        pcm[i] = Math.max(-1, Math.min(1, chan[i * step])) * 0x7fff;
      }
      this.port.postMessage({ audio: pcm.buffer }, [pcm.buffer]);
    }

    // --- stop event
    if (this.isSpeaking && now - this.lastVoiceTime > this.silenceDelayMs) {
      this.isSpeaking = false;
      this.port.postMessage({ event: 'stop' });
    }
    
    return true;
  }
}

registerProcessor('down-sampler', VoiceActivityDetector);
