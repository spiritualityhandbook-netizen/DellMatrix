/**
 * Mandel Station (Omni-Station) — snap-in
 * One workspace: multi-persona dispatcher + shared canvas + dual-layer view
 */

import { createSharedCanvas } from '../core/shared_canvas.js';

export const mandelStationSnapIn = {
  id: 'mandel-station',
  type: 'station',
  name: 'Mandel Station',
  description: 'Single command center — personas, shared canvas, surface + logic layers',

  attach(foundation) {
    foundation._station = {
      canvas: createSharedCanvas(),
      mode: 'surface', // surface | logic
      dispatcher: true
    };
  },

  detach(foundation) {
    delete foundation._station;
  },

  api: {
    canvas(foundation) {
      return foundation._station?.canvas || null;
    },
    setMode(foundation, mode) {
      if (!foundation._station) return null;
      foundation._station.mode = mode === 'logic' ? 'logic' : 'surface';
      return foundation._station.mode;
    },
    dispatch(foundation, persona, directive) {
      const canvas = foundation._station?.canvas;
      if (!canvas) return null;
      return canvas.write(persona, {
        type: 'directive',
        text: directive
      });
    },
    status(foundation) {
      const s = foundation._station;
      if (!s) return null;
      return {
        mode: s.mode,
        canvas: s.canvas.snapshot()
      };
    }
  }
};

export default mandelStationSnapIn;
