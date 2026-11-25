/**
 * Map old DuoBeta names → new foundation locations
 */

export const LEGACY_MAP = {
  // Old concern → New home
  'kernel boot': 'src/boot.js + src/unify.js',
  'harmonic cube / 5-ring memory': 'src/core/harmonic_cube_5ring.js + src/core/five_ring_bind.js',
  'mandell parse/execute': 'src/mandell_language.js (legacy) + src/core/dell_functions.js (new catalog)',
  'english command loop': 'src/execute_preform.js (legacy front) → should call createUnifiedRuntime()',
  'personas': 'src/snapins/personas_pack.js + src/core/persona_guidance.js',
  'evolution cycles': 'src/autonomous_evolution.js (legacy) under dm.legacy.load',
  'psalms': 'src/psalm_genesis.js (legacy) + workshops psalms',
  'station / multi-agent canvas': 'src/snapins/mandel_station.js + src/core/shared_canvas.js',
  'forces': 'src/forces/* + src/core/force_slots.js',
  'verita/smith': 'src/core/smith_map.js + src/snapins/smith_pack.js',
  'lattice living graph': 'src/core/dual_lattice.js (canonical)'
};

export function describeUnification() {
  return {
    rule: 'Foundation owns boot. Legacy attaches via dm.legacy.load(name).',
    canonicalLattice: 'src/core/dual_lattice.js',
    canonicalBoot: 'src/unify.js → createUnifiedRuntime()',
    map: LEGACY_MAP
  };
}
