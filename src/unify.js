/**
 * UNIFY — single front door for DellMatrix
 *
 * Era A (new): foundation + dual lattice + snap-ins
 * Era B (legacy DuoBeta): execute_preform, autonomous_evolution, psalm_genesis, etc.
 *
 * Rule: Foundation is truth. Legacy attaches; it does not own boot.
 */

import { startDellMatrix } from './boot.js';
import { attachForceSystem } from './core/force_slots.js';
import { createFormatRouter } from './core/format_router.js';
import { createOracle } from './core/oracle_protocol.js';

/**
 * Build the unified runtime.
 * Returns foundation-centered object with legacy hooks namespaced.
 */
export function createUnifiedRuntime(options = {}) {
  const dm = startDellMatrix(options);

  // Attach systems that belong on foundation
  try { attachForceSystem(dm); } catch (_) {}
  dm.formatRouter = createFormatRouter();
  dm.oracle = createOracle();

  // Legacy namespace — load only when requested so boot stays light
  dm.legacy = {
    available: [
      'execute_preform',
      'autonomous_evolution',
      'psalm_genesis',
      'self_introspection',
      'trio_beta_builder',
      'mandell_kernel',
      'mandell_language'
    ],
    loaded: {},
    async load(name) {
      if (this.loaded[name]) return this.loaded[name];
      const map = {
        execute_preform: () => import('./execute_preform.js'),
        autonomous_evolution: () => import('./autonomous_evolution.js'),
        psalm_genesis: () => import('./psalm_genesis.js'),
        self_introspection: () => import('./self_introspection.js'),
        trio_beta_builder: () => import('./trio_beta_builder.js'),
        mandell_kernel: () => import('./mandell_kernel.js'),
        mandell_language: () => import('./mandell_language.js')
      };
      if (!map[name]) throw new Error(`Unknown legacy module: ${name}`);
      const mod = await map[name]();
      this.loaded[name] = mod;
      return mod;
    }
  };

  dm.unified = true;
  dm.era = {
    foundation: 'active',
    legacy: 'compat-attached'
  };

  return dm;
}

export default createUnifiedRuntime;
