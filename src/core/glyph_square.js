/**
 * Glyph orbit / coherence growth — evolved formula
 *
 *   C_{n+1} = C_n² + Δ_known + Δ_unknown
 *
 * Squaring reinforces existing structure (coherence growth).
 * Δ_known  = measured / already-mapped contribution
 * Δ_unknown = residual / undiscovered contribution (drives exploration)
 */

export function squareGlyphState(state = {}) {
  const features = state.features || {};
  const squared = {};
  for (const [k, v] of Object.entries(features)) {
    const n = Number(v) || 0;
    squared[k] = Number((n * n).toFixed(4));
  }
  const coherenceIn = Number(state.coherence) || 0.5;
  // pure square term on coherence (before deltas)
  const coherenceSquared = Number((coherenceIn * coherenceIn).toFixed(4));
  return {
    ...state,
    features: squared,
    coherence: coherenceSquared,
    influence: Number(((state.influence || 1) * (state.influence || 1)).toFixed(4)),
    squared: true
  };
}

/**
 * Apply known + unknown deltas after squaring
 * deltaKnown / deltaUnknown may include { features, coherence, influence }
 */
export function applyKnownUnknown(state, deltaKnown = {}, deltaUnknown = {}) {
  const features = { ...(state.features || {}) };

  for (const [k, v] of Object.entries(deltaKnown.features || {})) {
    features[k] = Number(((Number(features[k]) || 0) + Number(v)).toFixed(4));
  }
  for (const [k, v] of Object.entries(deltaUnknown.features || {})) {
    features[k] = Number(((Number(features[k]) || 0) + Number(v)).toFixed(4));
  }

  const c0 = Number(state.coherence) || 0;
  const cKnown = Number(deltaKnown.coherence) || 0;
  const cUnknown = Number(deltaUnknown.coherence) || 0;
  const coherence = Math.min(1, Math.max(0, Number((c0 + cKnown + cUnknown).toFixed(4))));

  const i0 = Number(state.influence) || 1;
  const iKnown = Number(deltaKnown.influence) || 0;
  const iUnknown = Number(deltaUnknown.influence) || 0;
  const influence = Number((i0 + iKnown + iUnknown).toFixed(4));

  return {
    ...state,
    features,
    coherence,
    influence,
    deltaKnown: true,
    deltaUnknown: true
  };
}

/**
 * One full orbit step:
 *   C_{n+1} = C_n² + Δ_known + Δ_unknown
 */
export function orbitStep(state, deltaKnown = {}, deltaUnknown = {}) {
  const squared = squareGlyphState(state);
  return applyKnownUnknown(squared, deltaKnown, deltaUnknown);
}

export function formulaLabel() {
  return 'C_{n+1} = C_n^2 + Δ_known + Δ_unknown';
}
