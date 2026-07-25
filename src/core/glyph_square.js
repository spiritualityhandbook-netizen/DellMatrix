/**
 * Glyph squaring — coherence growth
 * C_{n+1} = C_n² + Δ
 * Squaring a glyph-state multiplies internal structure by itself:
 * features reinforce, noise drops, influence rises.
 */

export function squareGlyphState(state = {}) {
  const features = state.features || {};
  const squared = {};
  for (const [k, v] of Object.entries(features)) {
    const n = Number(v) || 0;
    squared[k] = Number((n * n).toFixed(4));
  }
  const coherenceIn = Number(state.coherence) || 0.5;
  const coherenceOut = Math.min(1, Number((coherenceIn * coherenceIn + 0.05).toFixed(4)));
  return {
    ...state,
    features: squared,
    coherence: coherenceOut,
    influence: Number(((state.influence || 1) * (state.influence || 1)).toFixed(4)),
    squared: true
  };
}

export function applyDelta(state, delta = {}) {
  const features = { ...(state.features || {}) };
  for (const [k, v] of Object.entries(delta.features || {})) {
    features[k] = Number(((Number(features[k]) || 0) + Number(v)).toFixed(4));
  }
  const coherence = Math.min(
    1,
    Math.max(0, (Number(state.coherence) || 0) + (Number(delta.coherence) || 0))
  );
  return {
    ...state,
    features,
    coherence,
    deltaApplied: true
  };
}

/** One orbit step: square then add delta */
export function orbitStep(state, delta = {}) {
  return applyDelta(squareGlyphState(state), delta);
}
