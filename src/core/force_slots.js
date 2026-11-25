/**
 * Wire Nature Forces into foundation negative space slots
 */

import { createForceRegistry } from '../forces/nature_forces.js';

export function attachForceSystem(foundation) {
  const registry = createForceRegistry();
  foundation.forces = registry;

  // Mirror active force names into lattice negative space
  for (const f of registry.list()) {
    foundation.lattice.attachForce(f.name);
  }

  foundation.forceSnapshot = () => registry.getMatrixSnapshot();
  return registry;
}
