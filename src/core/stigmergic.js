/**
 * Stigmergic Phase Engine — environmental residue
 * State left in the environment so later passes can read it.
 * Grid = cold facts. Wave = creative / probabilistic.
 */

export class StigmergicEngine {
  constructor() {
    this.grid = new Map(); // cold factual residue
    this.wave = [];        // creative residue trail
    this.phase = 'grid';   // grid | wave
    this.pass = 0;
  }

  setPhase(phase) {
    this.phase = phase === 'wave' ? 'wave' : 'grid';
    return this.phase;
  }

  leaveResidue(key, value, kind = 'grid') {
    const entry = {
      key,
      value,
      kind,
      pass: this.pass,
      at: new Date().toISOString()
    };
    if (kind === 'wave') {
      this.wave.push(entry);
      if (this.wave.length > 200) this.wave.shift();
    } else {
      this.grid.set(key, entry);
    }
    return entry;
  }

  readResidue(key) {
    return this.grid.get(key) || null;
  }

  readWave(n = 20) {
    return this.wave.slice(-n);
  }

  nextPass() {
    this.pass += 1;
    return this.pass;
  }

  snapshot() {
    return {
      phase: this.phase,
      pass: this.pass,
      gridSize: this.grid.size,
      waveSize: this.wave.length,
      recentWave: this.readWave(5)
    };
  }
}

export function createStigmergic() {
  return new StigmergicEngine();
}
