/**
 * Smith Chart pack — snap-in
 * Unit-circle match view + reflection-aware connections
 */

import { createSmithMap, standingWaveResidue } from '../core/smith_map.js';

export const smithPackSnapIn = {
  id: 'smith-pack',
  type: 'view',
  name: 'Smith Map',
  description: 'Impedance match, reflection coefficient, unit-circle projection, stub suggestions',

  attach(foundation) {
    foundation.smith = createSmithMap();
    // Add smith as a view-style mode flag
    foundation._smithActive = true;
  },

  detach(foundation) {
    delete foundation.smith;
    delete foundation._smithActive;
  },

  api: {
    match(foundation, idA, idB) {
      const a = foundation.lattice.nodes.get(idA);
      const b = foundation.lattice.nodes.get(idB);
      if (!a || !b || !foundation.smith) return null;
      const result = foundation.smith.match(a, b);
      if (foundation.stigmergic && !result.matched) {
        const residue = standingWaveResidue(result);
        if (residue) foundation.stigmergic.leaveResidue(`sw-${idA}-${idB}`, residue, 'wave');
      }
      return result;
    },
    project(foundation) {
      if (!foundation.smith) return [];
      return foundation.smith.projectAll(foundation.lattice.listNodes());
    }
  }
};

export default smithPackSnapIn;
