/**
 * Neural architecture patterns → DellMatrix structural analogs
 * (design metaphors for the lattice — not a trained neural net claim)
 */

export const NEURAL_PATTERNS = {
  residual: {
    name: 'Residual connection',
    meaning: 'Skip path + main path; add together',
    latticeAnalog: 'stigmergic residue + current node state; orbit C_n^2 + deltas'
  },
  attention: {
    name: 'Attention',
    meaning: 'Weight focus over context',
    latticeAnalog: 'center node + active lens + vesica strengths as attention weights'
  },
  inductiveBias: {
    name: 'Inductive bias',
    meaning: 'Built-in assumptions that guide learning',
    latticeAnalog: 'Dual Lattice law, Verita double-gate, Flower shell packing'
  },
  multiHead: {
    name: 'Multi-head attention',
    meaning: 'Several focus patterns in parallel',
    latticeAnalog: 'multiple lenses / personas attending same lattice at once'
  },
  normalization: {
    name: 'Normalization',
    meaning: 'Stabilize magnitudes',
    latticeAnalog: 'unit-circle Verita projection; coherence clamp 0..1'
  }
};

export function listNeuralPatterns() {
  return Object.values(NEURAL_PATTERNS);
}
