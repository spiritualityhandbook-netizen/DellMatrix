/**
 * DellMatrix Foundation
 *
 * This is the permanent core. It does not snap out.
 * Everything else (view rooms, workshops, extra forces, personas)
 * snaps INTO this foundation.
 *
 * Foundation includes:
 * - Dual Lattice (nodes, vesicas, shells, center)
 * - Growth stages
 * - Negative space
 * - Nature force slots
 * - Snap-in registry
 */

import { createDualLattice } from './dual_lattice.js';

export class DellMatrixFoundation {
  constructor(options = {}) {
    this.name = options.name || 'DellMatrix';
    this.lattice = createDualLattice(options.lattice || {});
    this.snapIns = new Map(); // id -> snap-in module
    this.activeSnapIns = new Set();
    this.createdAt = new Date().toISOString();
  }

  /** Register a modular piece (room, workshop, force pack, etc.) */
  registerSnapIn(mod) {
    if (!mod || !mod.id) throw new Error('Snap-in requires an id');
    this.snapIns.set(mod.id, {
      id: mod.id,
      type: mod.type || 'generic', // view | workshop | force | persona-pack | language
      name: mod.name || mod.id,
      description: mod.description || '',
      attach: typeof mod.attach === 'function' ? mod.attach : null,
      detach: typeof mod.detach === 'function' ? mod.detach : null,
      api: mod.api || {},
      meta: mod.meta || {}
    });
    return this.snapIns.get(mod.id);
  }

  /** Snap a module into the foundation */
  snapIn(id) {
    const mod = this.snapIns.get(id);
    if (!mod) return { ok: false, error: `Snap-in not found: ${id}` };
    if (this.activeSnapIns.has(id)) return { ok: true, already: true, id };

    if (mod.attach) {
      mod.attach(this);
    }
    this.activeSnapIns.add(id);
    return { ok: true, id, type: mod.type, name: mod.name };
  }

  /** Remove a module from the foundation */
  snapOut(id) {
    const mod = this.snapIns.get(id);
    if (!mod) return { ok: false, error: `Snap-in not found: ${id}` };
    if (!this.activeSnapIns.has(id)) return { ok: true, already: false, id };

    if (mod.detach) {
      mod.detach(this);
    }
    this.activeSnapIns.delete(id);
    return { ok: true, id, snappedOut: true };
  }

  listSnapIns() {
    return Array.from(this.snapIns.values()).map(m => ({
      id: m.id,
      type: m.type,
      name: m.name,
      description: m.description,
      active: this.activeSnapIns.has(m.id)
    }));
  }

  listActive() {
    return this.listSnapIns().filter(m => m.active);
  }

  getSnapIn(id) {
    return this.snapIns.get(id) || null;
  }

  /** Foundation-only snapshot (no snap-in UI state) */
  getFoundationState() {
    return {
      name: this.name,
      createdAt: this.createdAt,
      lattice: this.lattice.getSnapshot(),
      registeredSnapIns: this.snapIns.size,
      activeSnapIns: Array.from(this.activeSnapIns)
    };
  }
}

export function createFoundation(options = {}) {
  return new DellMatrixFoundation(options);
}
