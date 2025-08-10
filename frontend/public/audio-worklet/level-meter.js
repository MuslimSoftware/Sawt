/* Combines N inputs → one loudness number */
class LevelMeter extends AudioWorkletProcessor {
    process(inputs) {
      let sumSq = 0, count = 0;
      for (const input of inputs) {
        const chan = input[0];
        if (!chan) continue;
        for (let i = 0; i < chan.length; i++) {
          sumSq += chan[i] * chan[i];
        }
        count += chan.length;
      }
      if (count) this.port.postMessage(Math.sqrt(sumSq / count));
      return true;
    }
  }
  registerProcessor('level-meter', LevelMeter);
  