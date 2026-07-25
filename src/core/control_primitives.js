/**
 * Origin Control Primitives — ESTABLISHED
 * + Compendium V2 alignment hooks (RU-PAT refine stage = preOutputChain)
 */

export const TIER = {
  LAW: 0,
  SESSION: 1,
  TURN: 2
};

export class TierMemory {
  constructor() {
    this.law = [];
    this.session = [];
    this.turn = [];
  }

  add(tier, entry) {
    const item = { entry, at: new Date().toISOString() };
    if (tier === TIER.LAW) this.law.push(item);
    else if (tier === TIER.SESSION) this.session.push(item);
    else this.turn.push(item);
    return item;
  }

  clearTurn() {
    this.turn = [];
  }

  snapshot() {
    return {
      law: [...this.law],
      session: [...this.session],
      turn: [...this.turn]
    };
  }

  stack() {
    return [
      ...this.law.map(x => ({ tier: 0, ...x })),
      ...this.session.map(x => ({ tier: 1, ...x })),
      ...this.turn.map(x => ({ tier: 2, ...x }))
    ];
  }
}

export class PersonaContract {
  constructor(spec = {}) {
    this.name = spec.name || 'Unnamed';
    this.voice = spec.voice || {};
    this.directives = spec.directives || [];
    this.abilities = spec.abilities || [];
    this.limits = spec.limits || [];
    this.locked = true;
  }

  assertLimit(text = '') {
    const hits = [];
    for (const lim of this.limits) {
      if (typeof lim === 'string' && lim.startsWith('never:') && text.includes(lim.slice(6))) {
        hits.push(lim);
      }
    }
    return { ok: hits.length === 0, hits };
  }

  snapshot() {
    return {
      name: this.name,
      voice: this.voice,
      directives: [...this.directives],
      abilities: [...this.abilities],
      limits: [...this.limits],
      locked: this.locked
    };
  }
}

export class PinSet {
  constructor(pins = []) {
    this.pins = new Set(pins);
  }

  pin(text) {
    this.pins.add(String(text));
    return this.list();
  }

  unpin(text) {
    this.pins.delete(String(text));
    return this.list();
  }

  list() {
    return [...this.pins];
  }

  enforceSummary() {
    return this.list().map(p => ({ pin: p, status: 'LOCKED' }));
  }
}

export const HARD_GATES = {
  TRUTH: 'No false scientific/paranormal claims; projections labeled',
  ZERO_FLUFF: 'Every line must route, bind, test, show, or decide',
  FOG_TOOL_ONLY: 'Fog intentional, named, removable',
  MANDEL_ENGLISH: 'Mandel inside; English out unless requested',
  LATTICE: 'Dual Lattice + Verita double-gate + orbit law',
  COMPLETENESS: 'Answer ask; state done vs not done',
  ACHIEVABILITY: 'Prefer runnable/pastable/explicit placement',
  PERSONA_LIMITS: 'Persona limits are hard',
  ANTI_DEFAULT: 'No generic autopilot AI voice',
  NO_ORPHANS: 'Every node must connect (Compendium Law 3)',
  FLOOR_LOCK: 'Nova not on floor; Focus not floor operator'
};

export function runHardGates(ctx = {}) {
  const fails = [];
  if (ctx.claimsScienceDecipherment) fails.push('TRUTH');
  if (ctx.hasFluff) fails.push('ZERO_FLUFF');
  if (ctx.decorativeFog) fails.push('FOG_TOOL_ONLY');
  if (ctx.englishInsideEngine) fails.push('MANDEL_ENGLISH');
  if (ctx.breaksLattice) fails.push('LATTICE');
  if (ctx.incomplete) fails.push('COMPLETENESS');
  if (ctx.unachievable) fails.push('ACHIEVABILITY');
  if (ctx.personaLimitBroken) fails.push('PERSONA_LIMITS');
  if (ctx.genericAutopilot) fails.push('ANTI_DEFAULT');
  if (ctx.hasOrphanNodes) fails.push('NO_ORPHANS');
  if (ctx.novaOnFloor || ctx.focusAsFloorOp) fails.push('FLOOR_LOCK');
  return {
    ok: fails.length === 0,
    fails,
    gates: HARD_GATES
  };
}

export function preOutputChain({ pins, persona, gateCtx, antiDefault = true } = {}) {
  const steps = [];
  const pinList = pins instanceof PinSet ? pins.list() : (pins || []);
  steps.push({ step: 'pins', ok: true, pins: pinList });

  let personaOk = true;
  if (persona instanceof PersonaContract && gateCtx && gateCtx.draftText) {
    const r = persona.assertLimit(gateCtx.draftText);
    personaOk = r.ok;
    steps.push({ step: 'persona_limits', ok: r.ok, hits: r.hits || [] });
  } else {
    steps.push({ step: 'persona_limits', ok: true, skipped: !persona });
  }

  const gates = runHardGates(gateCtx || {});
  steps.push({ step: 'hard_gates', ok: gates.ok, fails: gates.fails });

  const antiOk = antiDefault ? !(gateCtx && gateCtx.genericAutopilot) : true;
  steps.push({ step: 'anti_default', ok: antiOk });

  const ok = steps.every(s => s.ok);
  return { ok, steps, action: ok ? 'ALLOW_DISPLAY' : 'REJECT_AND_REPAIR' };
}

export class ControlPlane {
  constructor(options = {}) {
    this.memory = new TierMemory();
    this.pins = new PinSet(options.pins || [
      'Foundation owns boot',
      'Mandel inside / English out',
      'Verita double-gate',
      'Orbit C^2 + Δ_known + Δ_unknown',
      'No scientific decipherment claims',
      'Floor: Alpha Delta Omega Omni only',
      'Nova via Cheat only'
    ]);
    this.persona = options.persona ? new PersonaContract(options.persona) : null;
    this.antiDefault = true;
  }

  snapshot() {
    return {
      memory: this.memory.snapshot(),
      pins: this.pins.enforceSummary(),
      persona: this.persona ? this.persona.snapshot() : null,
      hardGates: HARD_GATES,
      antiDefault: this.antiDefault
    };
  }

  check(gateCtx = {}) {
    return preOutputChain({
      pins: this.pins,
      persona: this.persona,
      gateCtx,
      antiDefault: this.antiDefault
    });
  }
}

export function createControlPlane(options) {
  return new ControlPlane(options);
}
