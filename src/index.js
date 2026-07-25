/**
 * DellMatrix public entry — UNIFIED
 * Always boot foundation first. Legacy is optional compat.
 */

export { createUnifiedRuntime } from './unify.js';
export { startDellMatrix } from './boot.js';
export { bootDellMatrix } from './snapins/index.js';
export { createFoundation } from './core/foundation.js';
export { createDualLattice } from './core/dual_lattice.js';
export { createFormatRouter } from './core/format_router.js';
export { createOracle } from './core/oracle_protocol.js';
