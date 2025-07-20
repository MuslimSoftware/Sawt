/* sample-accurate 48→16 kHz + Int16 PCM */
class VoiceActivityDetector extends AudioWorkletProcessor {
  constructor(options) {
    super();
    const opts = options?.processorOptions || {};
    this.voiceThreshold = opts.voiceThreshold || 0.08;
    this.silenceTimeout = opts.silenceTimeout || 500;
    this.lastVoiceTime = 0;
    this.isSpeaking = false;
  }

  calculateRMS(channel) {
    let sum = 0;
    for (let i = 0; i < channel.length; i++) sum += channel[i] * channel[i];
    return Math.sqrt(sum / channel.length);
  }

  downsamplePCM(channel) {
    const step = Math.round(sampleRate / 16000);
    const pcm = new Int16Array(Math.ceil(channel.length / step));
    for (let i = 0; i < pcm.length; i++) {
      pcm[i] = Math.max(-1, Math.min(1, channel[i * step])) * 0x7fff;
    }
    return pcm;
  }

  process([input]) {
    const now = currentTime * 1000;
    const channel = input[0];
    if (channel) {
      const rms = this.calculateRMS(channel);
      if (rms > this.voiceThreshold) {
        this.lastVoiceTime = now;
        if (!this.isSpeaking) {
          this.isSpeaking = true;
          this.port.postMessage({ event: 'start' });
        }
      }
      if (this.isSpeaking) {
        const pcm = this.downsamplePCM(channel);
        this.port.postMessage({ audio: pcm.buffer }, [pcm.buffer]);
      }
    }
    if (this.isSpeaking && now - this.lastVoiceTime > this.silenceTimeout) {
      this.isSpeaking = false;
      this.port.postMessage({ event: 'stop' });
    }
    return true;
  }
}

registerProcessor('down-sampler', VoiceActivityDetector);
