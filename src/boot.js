/**
 * DellMatrix boot entry
 * Foundation + default snap-ins + stigmergic + five-ring
 */

import { bootDellMatrix } from './snapins/index.js';
import { createStigmergic } from './core/stigmergic.js';
import { createFiveRingBind } from './core/five_ring_bind.js';
import { listDellFunctions, listFlows } from './core/dell_functions.js';
import { listCategories } from './core/agent_categories.js';
import { auditFromLattice } from './core/six_pillar_audit.js';

export function startDellMatrix(options = {}) {
  const dm = bootDellMatrix(options);

  // Attach always-on foundation helpers
  dm.stigmergic = createStigmergic();
  dm.fiveRing = createFiveRingBind();

  dm.status = function status() {
    return {
      foundation: dm.getFoundationState(),
      snapIns: dm.listSnapIns(),
      active: dm.listActive(),
      stigmergic: dm.stigmergic.snapshot(),
      fiveRing: dm.fiveRing.snapshot(),
      dellCount: listDellFunctions().length,
      flows: listFlows(),
      categories: listCategories().map(c => c.id),
      audit: auditFromLattice(dm.lattice.getSnapshot())
    };
  };

  return dm;
}

export default startDellMatrix;
