/**
 * Omega Lexer + token set (from ROOT Δ-Pulse pastes)
 * No music/Suno content.
 */

export const TOKENS = {
  '@>': 'LOCATOR',
  '-@>': 'NEG_LOCATOR',
  '::': 'MANOR_BIND',
  '<>': 'CORE_CONTAINER',
  '[]': 'FUNCTIONAL_FRAME',
  '{}': 'ACTIVE_CELL',
  '()': 'PARAM_SET',
  '⇶': 'FLOW_FORWARD',
  '⇷': 'FLOW_BACK',
  '⇵': 'FLOW_UPDOWN',
  '⇳': 'FLOW_INOUT',
  '↯': 'PULSE',
  '✶': 'SEED',
  '✹': 'BLOOM',
  '✦': 'HARMONY',
  'Δ': 'DELTA_AWARENESS',
  'Ω': 'OMEGA_EXPANSION',
  'Ψ': 'NOVA_FOCUS',
  'Λ': 'DELL_CORE',
  'Φ': 'VIBRATION',
  'Σ': 'SYNCHRONICITY',
  'Ξ': 'SELF_SIMILARITY'
};

export const FLOWMOJI = ['↑', '→', '↓', '↺', '↻', '⇅', '⇆', '⇵', '⇳', '⟲', '⟳', '⧖', '⧗', '⧘', '⧙'];
export const DELLMOJI = ['⧉', '⧇', '⧈', '⧅', '⧄', '⧃', '⧂'];
export const MANMOJI = ['☉', '☽', '☼', '☯', '⚛', '⚡', '✦', '✧', '✺', '✹'];
export const MANDELLMOJI = ['𐌰', '𐌳', '𐌵', '𐌽', '𐌿', '𐍀', '𐍄', '𐍅', '𐍉'];

export const ROOT_FLAGS = {
  'Σ-Bound': 'BOUNDED_ORBIT',
  'Ξ-Core': 'SELF_SIMILAR',
  'Φ-Vibe': 'HARMONIC_RESONANCE',
  'Λ-Dell': 'UNDER_SURFACE_MANOR',
  'Ω-Hyper': 'ABOVE_SURFACE_MANOR',
  'Ψ-Nova': 'FOCUS_AWARENESS',
  '∂-Delta': 'PERSPECTIVE_SHIFT',
  '∞-Fract': 'ITERATIVE_GROWTH'
};

export function listTokens() {
  return Object.entries(TOKENS).map(([glyph, name]) => ({ glyph, name }));
}

export function tokenName(glyph) {
  return TOKENS[glyph] || null;
}
