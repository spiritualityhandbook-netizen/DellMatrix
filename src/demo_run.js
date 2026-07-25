/**
 * One-shot demo — plant nodes, ledger, retrograde, status
 */

import { startDellMatrix } from './boot.js';
import { attachForceSystem } from './core/force_slots.js';

const dm = startDellMatrix();
attachForceSystem(dm);

const a = dm.lattice.addNode({ label: 'first idea', plantedBy: 'Ace' });
const b = dm.lattice.addNode({ label: 'second idea', plantedBy: 'Ace' });
dm.lattice.grow(a.id, 1.5);
dm.lattice.grow(b.id, 0.8);

const g = dm.lattice.addLedgerItem({ label: 'grain', amount: 12, plantedBy: 'Ace' });
const o = dm.lattice.addLedgerItem({ label: 'oil', amount: 3, plantedBy: 'Ace' });
const sum = dm.lattice.sumLedger([g.id, o.id]);

dm.lattice.setTraversalMode('retrograde');
const path = dm.lattice.walkFrom(a.id, 4);

dm.stigmergic.leaveResidue('last-demo', { path, sum: sum.total }, 'grid');
dm.fiveRing.place('herbal', { label: 'first idea' });
dm.fiveRing.place('recipe', { label: 'total grain+oil', amount: sum.total });

console.log('--- DellMatrix Demo ---');
console.log('Nodes:', dm.lattice.listNodes().length);
console.log('Center:', dm.lattice.centerId);
console.log('Retrograde path:', path);
console.log('Ledger sum:', sum.total);
console.log('Active snap-ins:', dm.listActive().map(s => s.id));
console.log('Forces:', dm.forceSnapshot().forces.map(f => f.name));
console.log('Audit:', dm.status().audit);
console.log('Five-ring:', dm.fiveRing.snapshot().counts);
