/**
 * Geometric ring/path registry
 * Inspired by documented crop-circle *geometry* only:
 * circles, rings, nested rings, paths, grids.
 *
 * Scientific consensus: vast majority of crop circles are human-made.
 * We use the geometry as lattice pattern language — no paranormal claim.
 */

export const GEO_PATTERNS = {
  single_circle: {
    id: 'single_circle',
    meaning: 'One center, one boundary',
    lattice: 'shell 0 + rim'
  },
  ring: {
    id: 'ring',
    meaning: 'Annulus around center',
    lattice: 'shell n as ring'
  },
  nested_rings: {
    id: 'nested_rings',
    meaning: 'Concentric shells',
    lattice: 'shells 0..N Flower growth'
  },
  path_curve: {
    id: 'path_curve',
    meaning: 'Directed trail between nodes',
    lattice: 'walkFrom / Voyage route'
  },
  radial_burst: {
    id: 'radial_burst',
    meaning: 'Lines from center outward',
    lattice: 'center + spokes to shell nodes'
  },
  grid_overlay: {
    id: 'grid_overlay',
    meaning: 'Orthogonal address over radial life',
    lattice: 'cube address + sphere contact (Dual Lattice)'
  }
};

export function listGeoPatterns() {
  return Object.values(GEO_PATTERNS);
}
