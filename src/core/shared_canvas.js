/**
 * Shared Canvas — single truth file all personas read/write
 * Mandel Station multi-agent coordination
 */

export class SharedCanvas {
  constructor() {
    this.version = 1;
    this.updatedAt = new Date().toISOString();
    this.beads = []; // units of work / detail
    this.logs = {
      Manny: [],
      Melody: [],
      Aetheris: [],
      Mathelody: [],
      The_Ancient: [],
      system: []
    };
    this.locks = {}; // beadId -> personaName
  }

  write(persona, entry) {
    const bead = {
      id: `bead-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 5)}`,
      persona: persona || 'system',
      entry,
      at: new Date().toISOString()
    };
    this.beads.push(bead);
    if (!this.logs[persona]) this.logs[persona] = [];
    this.logs[persona].push(bead);
    this.version += 1;
    this.updatedAt = bead.at;
    return bead;
  }

  read(persona = null) {
    if (persona) return this.logs[persona] || [];
    return this.beads;
  }

  latest(n = 10) {
    return this.beads.slice(-n);
  }

  snapshot() {
    return {
      version: this.version,
      updatedAt: this.updatedAt,
      beadCount: this.beads.length,
      latest: this.latest(5)
    };
  }
}

export function createSharedCanvas() {
  return new SharedCanvas();
}
