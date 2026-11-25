/**
 * harmonic_cube_5ring.js
 * 
 * Practical implementation of Harmonic Cube + 5-Ring feedback system
 * with self-understanding meta-layer.
 * 
 * This is real, runnable code. No mysticism. Just a tiered memory system
 * with recursive feedback processing and self-inspection/adjustment.
 */

import fs from 'node:fs';

class HarmonicCube {
  constructor() {
    this.memory = {
      shem: new Map(),
      gem: new Map(),
      rememory: new Map(),
      sub: new Map(),
      plannedFog: new Map()
    };

    this.delta = 0.1;
    this.stats = {
      totalStored: 0,
      totalRetrieved: 0,
      totalPromoted: 0,
      totalFogged: 0
    };
  }

  store(tier, key, value) {
    if (!this.memory[tier]) {
      throw new Error(`Invalid tier: ${tier}`);
    }

    this.memory[tier].set(key, {
      value,
      timestamp: Date.now(),
      accessCount: 0,
      lastAccessed: Date.now()
    });

    this.stats.totalStored++;
  }

  retrieve(key) {
    for (const [tierName, tierMap] of Object.entries(this.memory)) {
      if (tierMap.has(key)) {
        const item = tierMap.get(key);
        item.accessCount++;
        item.lastAccessed = Date.now();
        this.stats.totalRetrieved++;

        if (item.accessCount > 5 && tierName !== 'shem') {
          this.promote(key, tierName);
        }

        return item.value;
      }
    }
    return null;
  }

  promote(key, fromTier) {
    const item = this.memory[fromTier].get(key);
    if (!item) return;

    this.memory[fromTier].delete(key);
    this.stats.totalPromoted++;

    if (fromTier === 'plannedFog') {
      this.memory.gem.set(key, item);
    } else if (fromTier === 'rememory') {
      this.memory.gem.set(key, item);
    } else if (fromTier === 'gem') {
      this.memory.shem.set(key, item);
    } else {
      this.memory.shem.set(key, item);
    }
  }

  decayUnused(maxAgeMs = 1000 * 60 * 5) {
    const now = Date.now();
    for (const [tierName, tierMap] of Object.entries(this.memory)) {
      if (tierName === 'plannedFog') continue;

      const keysToMove = [];
      for (const [key, item] of tierMap) {
        if (now - item.lastAccessed > maxAgeMs) {
          keysToMove.push(key);
        }
      }

      keysToMove.forEach(key => {
        const item = tierMap.get(key);
        tierMap.delete(key);
        this.memory.plannedFog.set(key, item);
        this.stats.totalFogged++;
      });
    }
  }

  getMemorySizes() {
    return Object.fromEntries(
      Object.entries(this.memory).map(([tier, map]) => [tier, map.size])
    );
  }

  getStats() {
    return {
      ...this.stats,
      memorySizes: this.getMemorySizes()
    };
  }

  toJSON() {
    return {
      memory: Object.fromEntries(
        Object.entries(this.memory).map(([tier, map]) => [tier, Array.from(map.entries())])
      ),
      delta: this.delta,
      stats: { ...this.stats }
    };
  }

  loadState(state) {
    if (!state) return this;
    this.delta = state.delta ?? this.delta;
    this.stats = { ...this.stats, ...(state.stats || {}) };
    this.memory = {
      shem: new Map(state.memory?.shem || []),
      gem: new Map(state.memory?.gem || []),
      rememory: new Map(state.memory?.rememory || []),
      sub: new Map(state.memory?.sub || []),
      plannedFog: new Map(state.memory?.plannedFog || [])
    };
    return this;
  }
}

class FiveRingSystem {
  constructor(options = {}) {
    this.cube = new HarmonicCube();
    this.rings = {
      herbal: [],
      astro: [],
      bio: [],
      pharma: [],
      recipe: []
    };

    this.delta = options.delta ?? 0.1;
    this.maxRingSize = options.maxRingSize ?? 50;
    this.auditInterval = options.auditInterval ?? 10;
    this.stateVersion = 'FiveRingSystem_v2';

    this.stats = {
      cyclesRun: 0,
      itemsProcessed: 0,
      selfAudits: 0,
      lastDecision: 'idle'
    };
  }

  normalizeInput(input) {
    if (typeof input === 'string') {
      return { id: input, type: 'text', data: input };
    }

    if (input && typeof input === 'object') {
      return {
        ...input,
        id: input.id || `input_${Date.now()}`,
        type: input.type || 'normal',
        data: input.data ?? input.value ?? JSON.stringify(input),
        metadata: input.metadata || {}
      };
    }

    return { id: `input_${Date.now()}`, type: 'unknown', data: String(input ?? '') };
  }

  process(input) {
    this.stats.cyclesRun++;
    this.stats.itemsProcessed++;

    const normalized = this.normalizeInput(input);
    const result = {
      input: normalized,
      steps: [],
      coherence: 0,
      ringData: {},
      transformation: null,
      decision: null
    };

    this.rings.herbal.push(normalized);
    result.steps.push({ ring: 'herbal', action: 'stored' });

    const phaseValue = this.rings.herbal.length * this.delta;
    this.rings.astro.push(phaseValue);
    result.steps.push({ ring: 'astro', action: 'phase_applied', value: phaseValue.toFixed(3) });

    const coherence = this.calculateCoherence();
    this.rings.bio.push(coherence);
    result.steps.push({ ring: 'bio', action: 'coherence_checked', value: coherence.toFixed(3) });

    const transformed = {
      id: `${Date.now()}_${this.stats.itemsProcessed}`,
      original: normalized,
      coherence,
      phase: phaseValue,
      delta: this.delta,
      timestamp: Date.now()
    };
    this.rings.pharma.push(transformed);
    this.rings.recipe.push(transformed);

    const decision = this.decideAction(coherence);
    this.stats.lastDecision = decision.action;
    result.decision = decision;

    if (coherence > 0.7) {
      this.cube.store('shem', transformed.id, transformed);
    } else if (coherence > 0.45) {
      this.cube.store('gem', transformed.id, transformed);
    } else {
      this.cube.store('rememory', transformed.id, transformed);
    }

    result.coherence = coherence;
    this.delta = Math.max(0.05, Math.min(0.25, coherence * 0.08));

    if (this.stats.cyclesRun % this.auditInterval === 0) {
      result.selfUnderstanding = this.understandSelf();
    }

    return result;
  }

  calculateCoherence() {
    const ringLengths = Object.values(this.rings).map(arr => arr.length);
    const totalItems = ringLengths.reduce((sum, len) => sum + len, 0);
    if (totalItems === 0) return 0;

    const targetSize = this.maxRingSize / 5;
    const balancePenalty = ringLengths.reduce((sum, len) => sum + Math.abs(len - targetSize), 0) / (ringLengths.length * targetSize);
    const volumeScore = Math.min(1, totalItems / this.maxRingSize);
    return Math.max(0, Math.min(1, (volumeScore * 0.6) + ((1 - balancePenalty) * 0.4)));
  }

  decideAction(coherence) {
    if (coherence < 0.35) return { action: 'recalibrate', reason: 'coherence below stable threshold' };
    if (coherence < 0.7) return { action: 'observe', reason: 'coherence is developing' };
    return { action: 'stabilize', reason: 'coherence is healthy' };
  }

  understandSelf() {
    this.stats.selfAudits++;
    const coherence = this.calculateCoherence();
    return {
      timestamp: Date.now(),
      cyclesRun: this.stats.cyclesRun,
      coherence: coherence.toFixed(3),
      delta: this.delta.toFixed(3),
      cubeMemory: this.cube.getMemorySizes(),
      assessment: coherence > 0.75 ? 'stable' : 'evolving'
    };
  }

  maintain() {
    this.cube.decayUnused();
  }

  getState() {
    return {
      version: this.stateVersion,
      stats: this.stats,
      coherence: this.calculateCoherence().toFixed(3),
      delta: this.delta.toFixed(3),
      ringSizes: Object.fromEntries(
        Object.entries(this.rings).map(([k, v]) => [k, v.length])
      ),
      cubeSizes: this.cube.getMemorySizes()
    };
  }
}

export { HarmonicCube, FiveRingSystem };
