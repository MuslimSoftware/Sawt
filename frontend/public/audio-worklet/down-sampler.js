/* 48 kHz → 16 kHz Int16 PCM + VAD */
class VoiceActivityDetector extends AudioWorkletProcessor {
  static get parameterDescriptors() { return []; }

  constructor({ processorOptions = {} } = {}) {
    super();

    const {
      voiceThreshold = 0.06,
      silenceTimeoutMs = 1000,
      preBufferMs = 500,
      speakingGraceMs = 100,
    } = processorOptions;

    this.voiceThreshold = voiceThreshold;
    this.silenceTimeout = silenceTimeoutMs;
    this.speakingGrace = speakingGraceMs;

    const BLOCK_MS = 128 / sampleRate * 1000; // 128-sample render quantum
    this.maxPreBufferSize = Math.ceil(preBufferMs / BLOCK_MS);

    /* state */
    this.isSpeaking     = false;
    this.lastVoiceTime  = 0;
    this.preBuffer      = new Array(this.maxPreBufferSize).fill(null);
    this.preBufPos      = 0;   // circular write index
    this.preBufFilled   = 0;   // how many valid buffers we have
  }

  /* ----- helpers ----- */

  /** fast RMS of a Float32Array */
  rms(ch) {
    let sum = 0;
    for (let i = 0; i < ch.length; ++i) sum += ch[i] * ch[i];
    return Math.sqrt(sum / ch.length);
  }

  /** 48 kHz Float32 → 16 kHz Int16 */
  downsample(ch) {
    const step = Math.round(sampleRate / 16_000);       // 3 when SR = 48 kHz
    const out  = new Int16Array(Math.ceil(ch.length / step));
    for (let i = 0, j = 0; i < ch.length; i += step, ++j) {
      const s = Math.max(-1, Math.min(1, ch[i]));
      out[j] = (s * 0x7fff) | 0;
    }
    return out;
  }

  /** store one PCM buffer in the circular pre-buffer */
  stash(buf) {
    this.preBuffer[this.preBufPos] = buf;
    this.preBufPos = (this.preBufPos + 1) % this.maxPreBufferSize;
    this.preBufFilled = Math.min(this.preBufFilled + 1, this.maxPreBufferSize);
  }

  /** emit pre-buffered audio oldest-first, then clear */
  flushPrebuffer() {
    const msgs = [];
    const start = (this.preBufPos - this.preBufFilled + this.maxPreBufferSize) % this.maxPreBufferSize;
    for (let i = 0; i < this.preBufFilled; ++i) {
      const idx = (start + i) % this.maxPreBufferSize;
      const b = this.preBuffer[idx];
      if (b) msgs.push(b);
    }
    this.preBufFilled = 0;
    return msgs;
  }

  /* ----- main loop ----- */
  process([input]) {
    const ch = input?.[0];
    if (!ch) return true;                          // nothing to do

    const now = currentTime * 1000;                // to ms
    const rms = this.rms(ch);
    const pcm = this.downsample(ch);

    if (this.isSpeaking) {
      this.port.postMessage({ audio: pcm.buffer }, [pcm.buffer]);
      if (rms > this.voiceThreshold) {
        this.lastVoiceTime = now;
      } else if ((now - this.lastVoiceTime) > this.silenceTimeout) {

        this.isSpeaking = false;
        this.port.postMessage({ event: 'stop' });
      }
    } else { // not speaking
      this.stash(pcm.buffer.slice(0));
      if (rms > this.voiceThreshold) {
        if ((now - this.lastVoiceTime) < this.speakingGrace) {
          // grace period: we were recently speaking, so don't bother with a new 'start' event
          this.isSpeaking = true;
        } else {
          this.isSpeaking = true;
          this.lastVoiceTime = now;
          this.port.postMessage({ event: 'start' });

          /* emit pre-speech audio once */
          for (const b of this.flushPrebuffer()) {
            this.port.postMessage({ audio: b }, [b]);
          }
        }
        // also send the current frame
        this.port.postMessage({ audio: pcm.buffer }, [pcm.buffer]);
      }
    }

    return true;
  }
}

registerProcessor('down-sampler', VoiceActivityDetector);
