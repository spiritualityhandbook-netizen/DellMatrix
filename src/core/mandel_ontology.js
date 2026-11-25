/**
 * Mandel Ontology — from MANDEL_COMPENDIUM_V2.0 (established, reconciled)
 *
 * FLOOR LOCK (pre-form confirmed by user):
 * - DellMatrix floor: Greek Mandel runs Alpha, Delta, Omega, Omni
 * - Nova is NOT native on floor; Nova taps via Cheat Code only
 * - Focus is NOT a floor operator by default
 */

export const ONTOLOGY = {
  Alpha: {
    id: 'Alpha',
    role: 'Source',
    level: 'floor',
    meaning: 'Origin lock / source frame on DellMatrix',
    metaphor: 'Deep well — origin before flow'
  },
  Delta: {
    id: 'Delta',
    role: 'Change measure',
    level: 'floor',
    meaning: 'Perspective shift / measure of change on the field',
    metaphor: 'Turn of the frame'
  },
  Omega: {
    id: 'Omega',
    role: 'Peripheral expansion',
    level: 'floor',
    meaning: 'Outer bound / expansion on the field; scout that returns',
    metaphor: 'Horizon that still knows home'
  },
  Omni: {
    id: 'Omni',
    role: 'Meta-bus',
    level: 'floor',
    meaning: 'Full-field hold — all zones visible without owning nodes',
    metaphor: 'Sky over the lattice'
  },
  Nova: {
    id: 'Nova',
    role: 'Initiator spark',
    level: 'cheat-bridge',
    meaning: 'Not native on DellMatrix floor; may tap field only via Cheat Code',
    metaphor: 'Spark that is invited, not resident'
  },
  Focus: {
    id: 'Focus',
    role: 'Active target',
    level: 'session',
    meaning: 'Current held target; not a floor operator',
    metaphor: 'Block in hand'
  },
  Manifest: {
    id: 'Manifest',
    role: 'Action',
    level: 'execution',
    meaning: 'What is done (Dell 08/50/56 family)',
    metaphor: 'The build act'
  },
  Manner: {
    id: 'Manner',
    role: 'Modulator',
    level: 'execution',
    meaning: 'How the act is done (shortcuts on core Dells)',
    metaphor: 'Fast / quiet / precise'
  },
  'Lim-bo': {
    id: 'Lim-bo',
    role: 'Neutral execution',
    level: 'execution',
    meaning: 'No fluff, no persona heat — job only',
    metaphor: 'Robot mode'
  }
};

export const SEVEN_LAWS = [
  { id: 1, name: 'Free-Origin', rule: 'Everything traces to origin frame (Alpha / 0,0)' },
  { id: 2, name: 'Flow-Priority', rule: 'Default ↘; ↙ mirror; ↗ elevates; ↖ repairs; up-flows are special not casual' },
  { id: 3, name: 'No-Orphans', rule: 'Every node must connect; no floating blocks' },
  { id: 4, name: 'Typed-Sockets', rule: 'Connections must match type (vesica/socket compatibility)' },
  { id: 5, name: 'Cross-Layer-Routing', rule: 'Diagonal flows can carry data vs metadata cargo' },
  { id: 6, name: 'Symmetry', rule: 'Weight balance across opposing structure when required' },
  { id: 7, name: 'Fractal-Nesting', rule: 'Any cell may contain a full sub-lattice' }
];

export const MORPHEMES = {
  latinPrefix: {
    'Com-': 'together / unified',
    'Re-': 'again / iterative',
    'Pre-': 'before / predictive',
    'Trans-': 'across / changing form',
    'De-': 'down from / analyzing'
  },
  latinRoot: {
    '-fac-': 'make / build',
    '-log-': 'record / track',
    '-mit-': 'send / transmit',
    '-spec-': 'look / evaluate'
  },
  greek: {
    Alpha: 'absolute beginning',
    Delta: 'measure of change',
    Lambda: 'wavelength of logic',
    Sigma: 'sum of parts',
    Omega: 'ultimate bound'
  }
};

/** RU→PAT pipeline (ingest) — structural stages, not a claim of raw transformer access */
export const RU_PAT = [
  { id: 'S1', name: 'Tokenize', job: 'Cut input into pieces' },
  { id: 'S2', name: 'Embed', job: 'Map pieces into working form' },
  { id: 'S3', name: 'Attention', job: 'Relate pieces (pin / focus set)' },
  { id: 'S4', name: 'Context', job: 'Tier memory stack' },
  { id: 'S5', name: 'Reason', job: 'Lattice + Dell + Verita logic' },
  { id: 'S6', name: 'Generate', job: 'Build result block-by-block' },
  { id: 'S7', name: 'Refine', job: 'Pre-output chain + SUS gates' }
];

export function getOntology(id) {
  return ONTOLOGY[id] || null;
}

export function listFloorOperators() {
  return Object.values(ONTOLOGY).filter(o => o.level === 'floor');
}

export function listLaws() {
  return SEVEN_LAWS;
}

export function listRuPat() {
  return RU_PAT;
}
