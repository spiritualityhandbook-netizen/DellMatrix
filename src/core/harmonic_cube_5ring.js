// src/core/harmonic_cube_5ring.js
// Harmonic Cube + 5-Ring System (DNA-mapped)

export class HarmonicCube {
  constructor() {
    this.memory = {
      shem: new Map(),
      gem: new Map(),
      rememory: new Map(),
      sub: new Map(),
      plannedFog: new Map()
    };
    this.delta = 0.1;
  }

  store(tier, key, value) {
    if (!this.memory[tier]) throw new Error(`Invalid tier: ${tier}`);
    this.memory[tier].set(key, { value, timestamp: Date.now(), accessCount: 0 });
  }

  getState() {
    return {
      delta: this.delta,
      tiers: Object.fromEntries(
        Object.entries(this.memory).map(([k, v]) => [k, v.size])
      )
    };
  }
}

export class FiveRingSystem {
  constructor() {
    this.cube = new HarmonicCube();
    this.rings = {
      herbal: [],
      astro: [],
      bio: [],
      pharma: [],
      recipe: []
    };
    this.coherence = 0;
  }

  process(input) {
    this.rings.herbal.push(input);
    const phase = this.rings.herbal.length * this.cube.delta;
    this.rings.astro.push(phase);

    this.coherence = Math.min(1, this.rings.herbal.length / 50);
    this.rings.bio.push(this.coherence);

    const transformed = { ...input, coherence: this.coherence, phase };
    this.rings.pharma.push(transformed);
    this.rings.recipe.push(transformed);

    if (this.coherence > 0.7) {
      this.cube.store('shem', `dna_${Date.now()}`, transformed);
    }

    return { coherence: this.coherence, rings: this.getRingSizes() };
  }

  getRingSizes() {
    return Object.fromEntries(
      Object.entries(this.rings).map(([k, v]) => [k, v.length])
    );
  }
}
