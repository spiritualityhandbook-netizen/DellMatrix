/**
 * Smith Map — structural incorporation of Smith Chart ideas
 * Source concept: Veritasium "The Scariest Chart in Electrical Engineering"
 * (impedance matching, reflection, conformal map of infinity into a unit circle)
 *
 * Creative system mapping only — not an RF calculator claim.
 *
 * Laws borrowed:
 * 1. Every connection has impedance-like resistance to flow + reactance (phase/tension)
 * 2. Mismatch creates reflection (energy bounces back — weak vesica / standing noise)
 * 3. Match characteristic impedance → reflection → 0 → clean flow
 * 4. Infinite possibility plane maps into a finite unit circle (phone viewport / Flower)
 * 5. Every point holds TWO values at once: impedance AND reflection coefficient
 * 6. Stub = small branch added to cancel mismatch without destroying the main line
 */

export function complexAdd(a, b) {
  return { r: a.r + b.r, x: a.x + b.x };
}

export function complexMag(z) {
  return Math.sqrt(z.r * z.r + z.x * z.x);
}

/**
 * Reflection coefficient Γ from load impedance ZL and characteristic Z0
 * Γ = (ZL - Z0) / (ZL + Z0)  (complex, simplified with real Z0)
 */
export function reflectionCoefficient(ZL, Z0 = { r: 50, x: 0 }) {
  // Simplified real-line friendly form + imaginary keep
  const num = { r: ZL.r - Z0.r, x: ZL.x - Z0.x };
  const den = { r: ZL.r + Z0.r, x: ZL.x + Z0.x };
  const denMag2 = den.r * den.r + den.x * den.x || 1;
  const gamma = {
    r: (num.r * den.r + num.x * den.x) / denMag2,
    x: (num.x * den.r - num.r * den.x) / denMag2
  };
  const mag = Math.min(1, complexMag(gamma));
  return { gamma, mag, matched: mag < 0.05 };
}

/**
 * Map normalized impedance into unit-circle coordinates (Smith-style)
 * Returns { u, v } inside unit disk for plotting on phone / Flower viewport
 */
export function impedanceToUnitCircle(ZL, Z0 = { r: 50, x: 0 }) {
  const { gamma, mag } = reflectionCoefficient(ZL, Z0);
  // Γ plane IS the unit circle map
  return {
    u: gamma.r,
    v: gamma.x,
    mag,
    inside: mag <= 1
  };
}

/**
 * Node impedance from lattice properties
 * resistance ~ inverse of contact strength / openness
 * reactance ~ stage tension / shell distance mismatch
 */
export function nodeImpedance(node, Z0r = 50) {
  const contacts = node.contactCount || (node.contacts ? node.contacts.length : 0);
  const height = node.height || 0;
  const shell = node.shell || 0;
  // More contacts → lower resistance (easier flow)
  const r = Math.max(1, Z0r * (1 / (1 + contacts * 0.35)));
  // Shell + unfinished growth → reactance (phase tension)
  const x = (shell * 8) + (Math.max(0, 3 - height) * 5);
  return { r: Number(r.toFixed(2)), x: Number(x.toFixed(2)) };
}

/**
 * Match two nodes: compute reflection, suggest stub (small corrective branch)
 */
export function matchNodes(nodeA, nodeB, Z0 = { r: 50, x: 0 }) {
  const ZA = nodeImpedance(nodeA, Z0.r);
  const ZB = nodeImpedance(nodeB, Z0.r);
  // Treat B as load seen from A
  const { gamma, mag, matched } = reflectionCoefficient(ZB, ZA);
  const circle = impedanceToUnitCircle(ZB, ZA);

  // Stub suggestion: cancel reactance of load
  const stub = {
    type: 'stub',
    action: ZB.x > 0 ? 'add-series-capacitance' : 'add-series-inductance',
    cancelX: Number((-ZB.x).toFixed(2)),
    note: 'Small branch to cancel mismatch without killing main flow'
  };

  return {
    ZA,
    ZB,
    reflectionMag: mag,
    matched,
    gamma,
    unitCircle: circle,
    stub,
    flowQuality: matched ? 'clean' : mag < 0.3 ? 'partial' : 'standing-wave-risk'
  };
}

/**
 * Standing-wave residue: when mismatch is high, leave noise in stigmergic wave lane
 */
export function standingWaveResidue(matchResult) {
  if (matchResult.matched) return null;
  return {
    kind: 'standing-wave',
    reflectionMag: matchResult.reflectionMag,
    flowQuality: matchResult.flowQuality,
    at: new Date().toISOString()
  };
}

export class SmithMap {
  constructor(Z0 = { r: 50, x: 0 }) {
    this.Z0 = Z0;
    this.history = [];
  }

  inspectNode(node) {
    const Z = nodeImpedance(node, this.Z0.r);
    const circle = impedanceToUnitCircle(Z, this.Z0);
    return { nodeId: node.id, label: node.label, Z, circle };
  }

  match(nodeA, nodeB) {
    const result = matchNodes(nodeA, nodeB, this.Z0);
    this.history.push({ ...result, at: new Date().toISOString() });
    return result;
  }

  /** Project many nodes onto unit circle for phone Flower viewport */
  projectAll(nodes = []) {
    return nodes.map(n => this.inspectNode(n));
  }
}

export function createSmithMap(Z0) {
  return new SmithMap(Z0);
}
