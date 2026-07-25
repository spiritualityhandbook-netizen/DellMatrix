/**
 * Nature Forces System for DellMatrix
 * 
 * Forces are modular matrices that snap into the main matrix.
 * Each force affects growth, resonance, and synchronization.
 * Ideas flow like water. Growth is plant-like. Resonance is heartbeat.
 * Anyone can create new forces. Forces evolve with use.
 */

export class ForceMatrix {
  constructor({ name, type, intensity = 0.5, description = '' } = {}) {
    this.id = `force-${name.toLowerCase()}-${Date.now().toString(36)}`;
    this.name = name;
    this.type = type; // water | gravity | growth | breath | weather | time | space | custom
    this.intensity = Math.max(0, Math.min(1, intensity));
    this.description = description;
    this.createdAt = new Date().toISOString();
    this.resonanceLog = [];
    this.syncEvents = [];
    this.active = true;
    this.evolutionLevel = 1;
    this.contributors = []; // people who shaped this force
  }

  apply(target, context = {}) {
    throw new Error('ForceMatrix.apply() must be implemented by subclass');
  }

  recordResonance(event) {
    this.resonanceLog.push({
      ...event,
      timestamp: new Date().toISOString(),
      intensity: this.intensity
    });
    if (this.resonanceLog.length > 100) this.resonanceLog.shift();
  }

  evolve(amount = 0.05) {
    this.evolutionLevel = Number((this.evolutionLevel + amount).toFixed(3));
    this.intensity = Math.min(1, this.intensity + amount * 0.1);
    return this.evolutionLevel;
  }

  toJSON() {
    return {
      id: this.id,
      name: this.name,
      type: this.type,
      intensity: this.intensity,
      description: this.description,
      evolutionLevel: this.evolutionLevel,
      active: this.active,
      resonanceCount: this.resonanceLog.length,
      syncCount: this.syncEvents.length
    };
  }
}

/**
 * WATER FORCE
 * Ideas are water. They flow, take form, merge, evaporate, rain.
 * Synchronization happens when streams meet.
 */
export class WaterForce extends ForceMatrix {
  constructor(options = {}) {
    super({
      name: 'Water',
      type: 'water',
      intensity: options.intensity ?? 0.7,
      description: 'Ideas flow like water. They take the shape of any container. Streams merge into rivers. Resonance is the meeting of currents.'
    });
    this.streams = []; // active idea streams
    this.pools = [];   // settled idea pools
  }

  // Place an idea as a water droplet / stream
  flow(idea, source = 'unknown') {
    const stream = {
      id: `stream-${Date.now().toString(36)}`,
      idea: typeof idea === 'string' ? idea : idea.content || idea.label || String(idea),
      source,
      volume: 1,
      form: 'stream', // stream | pool | mist | river
      createdAt: new Date().toISOString(),
      merges: []
    };
    this.streams.push(stream);
    this.recordResonance({ type: 'flow', streamId: stream.id, idea: stream.idea });
    return stream;
  }

  // Two streams meet → synchronization (resonance)
  merge(streamIdA, streamIdB) {
    const a = this.streams.find(s => s.id === streamIdA);
    const b = this.streams.find(s => s.id === streamIdB);
    if (!a || !b) return null;

    const merged = {
      id: `river-${Date.now().toString(36)}`,
      idea: `${a.idea} ⇄ ${b.idea}`,
      source: 'merge',
      volume: a.volume + b.volume,
      form: 'river',
      parents: [a.id, b.id],
      createdAt: new Date().toISOString()
    };

    a.merges.push(merged.id);
    b.merges.push(merged.id);
    this.streams.push(merged);

    this.syncEvents.push({
      type: 'water-merge',
      streams: [streamIdA, streamIdB],
      result: merged.id,
      timestamp: new Date().toISOString()
    });

    this.recordResonance({ type: 'sync', event: 'merge', result: merged.idea });
    this.evolve(0.08);
    return merged;
  }

  // Settle a stream into a pool (stable idea)
  settle(streamId) {
    const stream = this.streams.find(s => s.id === streamId);
    if (!stream) return null;
    stream.form = 'pool';
    this.pools.push(stream);
    this.recordResonance({ type: 'settle', streamId });
    return stream;
  }

  apply(target, context = {}) {
    // Water softens rigid structures and increases flow between nodes
    if (target && typeof target === 'object') {
      target.flowability = (target.flowability || 0) + this.intensity * 0.2;
      target.form = target.form || 'fluid';
    }
    return { applied: 'water', intensity: this.intensity, effect: 'increased flow' };
  }

  getState() {
    return {
      ...this.toJSON(),
      streams: this.streams.length,
      pools: this.pools.length,
      activeStreams: this.streams.filter(s => s.form === 'stream' || s.form === 'river').length
    };
  }
}

/**
 * GROWTH FORCE (Plant / Tree)
 * Ideas grow like plants. Seed → sprout → stem → leaves → fruit.
 * Visible stages. Easy to see what grew and when.
 */
export class GrowthForce extends ForceMatrix {
  constructor(options = {}) {
    super({
      name: 'Growth',
      type: 'growth',
      intensity: options.intensity ?? 0.65,
      description: 'Ideas grow like trees. Seed becomes sprout becomes branch becomes fruit. Growth is visible and staged.'
    });
    this.plants = []; // growing idea plants
  }

  plant(idea, planter = 'unknown') {
    const plant = {
      id: `plant-${Date.now().toString(36)}`,
      idea: typeof idea === 'string' ? idea : idea.content || idea.label || String(idea),
      planter,
      stage: 'seed', // seed → sprout → stem → branch → leaf → fruit → seed
      height: 0,
      age: 0,
      watered: 0,
      sunlight: 0,
      createdAt: new Date().toISOString(),
      history: [{ stage: 'seed', at: new Date().toISOString() }]
    };
    this.plants.push(plant);
    this.recordResonance({ type: 'planted', plantId: plant.id, idea: plant.idea });
    return plant;
  }

  grow(plantId, factors = {}) {
    const plant = this.plants.find(p => p.id === plantId);
    if (!plant) return null;

    const water = factors.water ?? 0.3;
    const sun = factors.sun ?? 0.3;
    const nutrients = factors.nutrients ?? 0.2;

    plant.watered += water;
    plant.sunlight += sun;
    plant.age += 1;
    plant.height = Number((plant.height + (water + sun + nutrients) * this.intensity).toFixed(2));

    const stages = ['seed', 'sprout', 'stem', 'branch', 'leaf', 'fruit'];
    const stageIndex = stages.indexOf(plant.stage);
    const nextThreshold = (stageIndex + 1) * 1.5;

    if (plant.height >= nextThreshold && stageIndex < stages.length - 1) {
      plant.stage = stages[stageIndex + 1];
      plant.history.push({ stage: plant.stage, at: new Date().toISOString(), height: plant.height });
      this.recordResonance({ type: 'growth-stage', plantId, stage: plant.stage });
      this.evolve(0.05);
    }

    return plant;
  }

  // Get a clear visual of all growth
  getGrowthMap() {
    return this.plants.map(p => ({
      idea: p.idea,
      stage: p.stage,
      height: p.height,
      age: p.age,
      visual: this.renderPlant(p)
    }));
  }

  renderPlant(plant) {
    const stageArt = {
      seed: '·',
      sprout: '🌱',
      stem: '｜',
      branch: 'Ｙ',
      leaf: '🌿',
      fruit: '🍎'
    };
    return `${stageArt[plant.stage] || '?'} ${plant.idea.slice(0, 40)} [${plant.stage} h=${plant.height}]`;
  }

  apply(target) {
    if (target && typeof target === 'object') {
      target.growthPotential = (target.growthPotential || 0) + this.intensity * 0.25;
    }
    return { applied: 'growth', intensity: this.intensity };
  }
}

/**
 * BREATH FORCE (Recursive in / out)
 * The matrix breathes. Inhale gathers. Exhale releases.
 * Heartbeat rhythm. Synchronization is shared rhythm.
 */
export class BreathForce extends ForceMatrix {
  constructor(options = {}) {
    super({
      name: 'Breath',
      type: 'breath',
      intensity: options.intensity ?? 0.6,
      description: 'The matrix breathes. Inhale gathers ideas. Exhale releases and shares. Heartbeat creates shared rhythm.'
    });
    this.phase = 'inhale'; // inhale | exhale
    this.cycle = 0;
    this.beatLog = [];
    this.rhythm = 1.0; // beats per cycle
  }

  inhale(ideas = []) {
    this.phase = 'inhale';
    this.cycle += 1;
    const gathered = ideas.map(idea => ({
      idea: typeof idea === 'string' ? idea : idea.content || String(idea),
      gatheredAt: new Date().toISOString()
    }));
    this.beatLog.push({ phase: 'inhale', cycle: this.cycle, count: gathered.length });
    this.recordResonance({ type: 'inhale', cycle: this.cycle, count: gathered.length });
    return { phase: 'inhale', cycle: this.cycle, gathered };
  }

  exhale(count = 1) {
    this.phase = 'exhale';
    this.beatLog.push({ phase: 'exhale', cycle: this.cycle, released: count });
    this.recordResonance({ type: 'exhale', cycle: this.cycle });
    this.evolve(0.03);
    return { phase: 'exhale', cycle: this.cycle, released: count };
  }

  heartbeat() {
    // One full breath cycle
    const inResult = this.inhale();
    const outResult = this.exhale();
    return { inhale: inResult, exhale: outResult, rhythm: this.rhythm };
  }

  apply(target) {
    if (target && typeof target === 'object') {
      target.rhythm = this.rhythm;
      target.breathPhase = this.phase;
    }
    return { applied: 'breath', phase: this.phase, cycle: this.cycle };
  }

  getRhythmState() {
    return {
      phase: this.phase,
      cycle: this.cycle,
      rhythm: this.rhythm,
      recentBeats: this.beatLog.slice(-6)
    };
  }
}

/**
 * GRAVITY FORCE
 * Important ideas pull others toward them.
 * Mass = how many connections / how much resonance.
 */
export class GravityForce extends ForceMatrix {
  constructor(options = {}) {
    super({
      name: 'Gravity',
      type: 'gravity',
      intensity: options.intensity ?? 0.55,
      description: 'Ideas have mass. Heavy ideas pull lighter ones. Clusters form around gravity wells of meaning.'
    });
    this.wells = []; // gravity wells (important ideas)
  }

  createWell(idea, mass = 1) {
    const well = {
      id: `well-${Date.now().toString(36)}`,
      idea: typeof idea === 'string' ? idea : idea.content || String(idea),
      mass: Math.max(0.1, mass),
      pulled: [],
      createdAt: new Date().toISOString()
    };
    this.wells.push(well);
    this.recordResonance({ type: 'well-created', wellId: well.id });
    return well;
  }

  pull(wellId, ideaId) {
    const well = this.wells.find(w => w.id === wellId);
    if (!well) return null;
    well.pulled.push(ideaId);
    well.mass += 0.1;
    this.recordResonance({ type: 'pull', wellId, ideaId });
    return well;
  }

  apply(target) {
    if (target && typeof target === 'object') {
      target.mass = (target.mass || 1) * (1 + this.intensity * 0.1);
    }
    return { applied: 'gravity', wells: this.wells.length };
  }
}

/**
 * TIME FORCE
 * Things age. Some ideas ripen. Some decay. Cycles matter.
 */
export class TimeForce extends ForceMatrix {
  constructor(options = {}) {
    super({
      name: 'Time',
      type: 'time',
      intensity: options.intensity ?? 0.5,
      description: 'Everything ages. Ideas ripen or fade. Cycles create rhythm across the matrix.'
    });
    this.clock = 0;
    this.events = [];
  }

  tick(amount = 1) {
    this.clock += amount;
    this.events.push({ tick: this.clock, at: new Date().toISOString() });
    this.recordResonance({ type: 'tick', clock: this.clock });
    return this.clock;
  }

  age(item) {
    if (!item) return null;
    item.age = (item.age || 0) + 1;
    item.lastAged = this.clock;
    return item;
  }

  apply(target) {
    if (target) this.age(target);
    return { applied: 'time', clock: this.clock };
  }
}

/**
 * WEATHER FORCE
 * Atmosphere of the matrix. Clear, stormy, foggy, rainy.
 * Rain brings new seeds. Storms shake loose stuck ideas.
 */
export class WeatherForce extends ForceMatrix {
  constructor(options = {}) {
    super({
      name: 'Weather',
      type: 'weather',
      intensity: options.intensity ?? 0.5,
      description: 'The atmosphere of the matrix. Clear skies reveal. Rain brings seeds. Storms release stuck energy.'
    });
    this.condition = 'clear'; // clear | cloudy | rain | storm | fog
    this.history = [];
  }

  setCondition(condition) {
    const valid = ['clear', 'cloudy', 'rain', 'storm', 'fog'];
    if (!valid.includes(condition)) return this.condition;
    this.condition = condition;
    this.history.push({ condition, at: new Date().toISOString() });
    this.recordResonance({ type: 'weather-change', condition });
    return this.condition;
  }

  rain(seedCount = 3) {
    this.setCondition('rain');
    const seeds = Array.from({ length: seedCount }, (_, i) => ({
      id: `rain-seed-${Date.now()}-${i}`,
      type: 'weather-seed',
      plantedBy: 'rain'
    }));
    this.recordResonance({ type: 'rain', seeds: seedCount });
    return seeds;
  }

  apply(target) {
    return { applied: 'weather', condition: this.condition };
  }
}

/**
 * SPACE FORCE
 * Distance and nearness. Some ideas sit close. Some far.
 * Proximity increases chance of resonance.
 */
export class SpaceForce extends ForceMatrix {
  constructor(options = {}) {
    super({
      name: 'Space',
      type: 'space',
      intensity: options.intensity ?? 0.5,
      description: 'Ideas occupy space. Nearness increases chance of meeting. Distance creates perspective.'
    });
    this.positions = new Map(); // ideaId → {x, y, z}
  }

  place(ideaId, coords = { x: 0, y: 0, z: 0 }) {
    this.positions.set(ideaId, { ...coords, placedAt: new Date().toISOString() });
    return this.positions.get(ideaId);
  }

  distance(idA, idB) {
    const a = this.positions.get(idA);
    const b = this.positions.get(idB);
    if (!a || !b) return Infinity;
    return Math.sqrt(
      (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2
    );
  }

  apply(target) {
    return { applied: 'space', positions: this.positions.size };
  }
}

/**
 * FORCE REGISTRY
 * The main matrix holds all forces. Forces snap in and out.
 * Anyone can register a new custom force.
 */
export class ForceRegistry {
  constructor() {
    this.forces = new Map();
    this.initializeDefaultForces();
  }

  initializeDefaultForces() {
    this.register(new WaterForce());
    this.register(new GrowthForce());
    this.register(new BreathForce());
    this.register(new GravityForce());
    this.register(new TimeForce());
    this.register(new WeatherForce());
    this.register(new SpaceForce());
  }

  register(force) {
    this.forces.set(force.name.toLowerCase(), force);
    return force;
  }

  get(name) {
    return this.forces.get(name.toLowerCase()) || null;
  }

  list() {
    return Array.from(this.forces.values()).map(f => f.toJSON());
  }

  // Apply all active forces to a target
  applyAll(target, context = {}) {
    const results = [];
    for (const force of this.forces.values()) {
      if (force.active) {
        results.push(force.apply(target, context));
      }
    }
    return results;
  }

  // Get a clear visual snapshot of all forces and growth
  getMatrixSnapshot() {
    const water = this.get('water');
    const growth = this.get('growth');
    const breath = this.get('breath');
    const weather = this.get('weather');

    return {
      timestamp: new Date().toISOString(),
      forces: this.list(),
      water: water ? water.getState() : null,
      growth: growth ? growth.getGrowthMap() : [],
      breath: breath ? breath.getRhythmState() : null,
      weather: weather ? weather.condition : 'unknown',
      totalResonanceEvents: Array.from(this.forces.values())
        .reduce((sum, f) => sum + f.resonanceLog.length, 0)
    };
  }
}

export function createForceRegistry() {
  return new ForceRegistry();
}
