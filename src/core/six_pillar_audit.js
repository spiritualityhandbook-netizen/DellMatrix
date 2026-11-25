/**
 * 6-Pillar Evaluation Matrix (structural audit scores 0..1)
 * Standing · Spect · Tonea · Spirea · ManDetail · Omegate
 */

export function scorePillars(input = {}) {
  const clamp = (v) => Math.max(0, Math.min(1, Number(v) || 0));

  const standing = clamp(input.standing ?? 0.75);   // comprehension depth
  const spect = clamp(input.spect ?? 0.7);         // observation / scan
  const tonea = clamp(input.tonea ?? 0.6);         // voice / modularity
  const spirea = clamp(input.spirea ?? 0.7);       // creative growth loop
  const mandetail = clamp(input.mandetail ?? 0.8); // fractal zoom / detail
  const omegate = clamp(input.omegate ?? 0.75);    // predictive lock

  const average = Number(((standing + spect + tonea + spirea + mandetail + omegate) / 6).toFixed(3));
  const pass = average >= 0.95;

  return {
    standing,
    spect,
    tonea,
    spirea,
    mandetail,
    omegate,
    average,
    pass,
    label: pass ? 'PASS' : 'BELOW_THRESHOLD'
  };
}

export function auditFromLattice(latticeSnapshot = {}) {
  const nodeCount = latticeSnapshot.nodeCount || 0;
  const resonance = (latticeSnapshot.recentResonance || []).length;
  return scorePillars({
    standing: Math.min(1, 0.5 + nodeCount * 0.05),
    spect: Math.min(1, 0.4 + resonance * 0.1),
    tonea: 0.65,
    spirea: Math.min(1, 0.5 + (latticeSnapshot.generation || 0) * 0.02),
    mandetail: 0.8,
    omegate: 0.7
  });
}
