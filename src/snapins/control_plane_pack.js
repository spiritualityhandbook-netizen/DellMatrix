/**
 * Control Plane snap-in — origin ABCC primitives established on foundation
 */

import { createControlPlane } from '../core/control_primitives.js';

export const controlPlaneSnapIn = {
  id: 'control-plane',
  type: 'control',
  name: 'Control Plane',
  description: 'Tier memory, persona contract, pre-output chain, hard gates, pin set, anti-default',

  attach(foundation) {
    foundation.control = createControlPlane();
    // Seed Tier-0 law from DellMatrix constants
    foundation.control.memory.add(0, 'DellMatrix foundation owns boot');
    foundation.control.memory.add(0, 'Greek Mandel scale ops: Alpha Delta Omega Omni');
    foundation.control.memory.add(0, 'Nova taps floor only via Cheat Code');
    foundation.control.memory.add(0, 'Structural ancient ops only — no decipherment claims');
  },

  detach(foundation) {
    delete foundation.control;
  },

  api: {
    snapshot(foundation) {
      return foundation.control ? foundation.control.snapshot() : null;
    },
    check(foundation, gateCtx) {
      return foundation.control ? foundation.control.check(gateCtx) : { ok: false, error: 'control plane off' };
    },
    pin(foundation, text) {
      if (!foundation.control) return null;
      return foundation.control.pins.pin(text);
    },
    addLaw(foundation, entry) {
      if (!foundation.control) return null;
      return foundation.control.memory.add(0, entry);
    }
  }
};

export default controlPlaneSnapIn;
