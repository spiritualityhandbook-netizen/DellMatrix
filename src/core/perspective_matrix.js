/**
 * Perspective Matrix
 *
 * Built on the Dual Lattice.
 * Switching perspective = choosing a center + choosing a lens.
 * Same lattice, different view.
 */

import { createDualLattice } from './dual_lattice.js';

export const LENSES = {
  growth: {
    id: 'growth',
    name: 'Growth',
    description: 'See stages and height of every node as plants'
  },
  water: {
    id: 'water',
    name: 'Water',
    description: 'See streams, rivers, pools and merges'
  },
  force: {
    id: 'force',
    name: 'Force',
    description: 'See gravity wells, breath phase, weather'
  },
  network: {
    id: 'network',
    name: 'Network',
    description: 'See contacts and vesica strengths'
  },
  personal: {
    id: 'personal',
    name: 'Personal',
    description: 'Only nodes you planted'
  },
  shared: {
    id: 'shared',
    name: 'Shared',
    description: 'Nodes that resonated with others'
  }
};

export class PerspectiveMatrix {
  constructor(lattice = null) {
    this.lattice = lattice || createDualLattice();
    this.activeLens = 'growth';
    this.viewHistory = [];
  }

  /**
   * Switch which node is the center of view.
   */
  lookFrom(nodeId) {
    const center = this.lattice.setCenter(nodeId);
    this.viewHistory.push({
      type: 'center',
      nodeId,
      at: new Date().toISOString()
    });
    return center;
  }

  /**
   * Switch lens (how you interpret the same lattice).
   */
  setLens(lensId) {
    if (!LENSES[lensId]) return this.activeLens;
    this.activeLens = lensId;
    this.viewHistory.push({
      type: 'lens',
      lens: lensId,
      at: new Date().toISOString()
    });
    return this.activeLens;
  }

  /**
   * Render current view according to active lens.
   */
  render() {
    const snapshot = this.lattice.getSnapshot();
    const nodes = this.lattice.listNodes();

    switch (this.activeLens) {
      case 'growth':
        return {
          lens: 'growth',
          center: snapshot.centerLabel,
          items: nodes.map(n => ({
            id: n.id,
            label: n.label,
            stage: n.stage,
            height: n.height,
            shell: n.shell,
            visual: this._stageArt(n.stage) + ' ' + n.label
          }))
        };

      case 'water':
        return {
          lens: 'water',
          center: snapshot.centerLabel,
          items: nodes.map(n => ({
            id: n.id,
            label: n.label,
            form: n.stage === 'seed' ? 'droplet' : n.contactCount > 2 ? 'river' : 'stream',
            contacts: n.contactCount
          }))
        };

      case 'network':
        return {
          lens: 'network',
          center: snapshot.centerLabel,
          items: nodes.map(n => ({
            id: n.id,
            label: n.label,
            contacts: n.contactCount,
            shell: n.shell
          })),
          recentResonance: snapshot.recentResonance
        };

      case 'force':
        return {
          lens: 'force',
          center: snapshot.centerLabel,
          activeForces: this.lattice.negativeSpace.activeForces,
          nodes: nodes.length
        };

      case 'personal':
        return {
          lens: 'personal',
          items: nodes.filter(n => n.plantedBy) // simplified
        };

      case 'shared':
        return {
          lens: 'shared',
          items: nodes.filter(n => n.contactCount > 0),
          resonanceEvents: snapshot.recentResonance
        };

      default:
        return { lens: this.activeLens, snapshot };
    }
  }

  _stageArt(stage) {
    const art = {
      seed: '·',
      sprout: '🌱',
      stem: '｜',
      branch: 'Ｙ',
      leaf: '🌿',
      fruit: '🍎'
    };
    return art[stage] || '?';
  }

  /**
   * Phone-friendly square grid of current view.
   */
  toPhoneGrid(gridSize = 9) {
    const nodes = this.lattice.listNodes();
    const grid = Array.from({ length: gridSize }, () =>
      Array.from({ length: gridSize }, () => null)
    );

    for (const n of nodes) {
      const proj = this.lattice.projectToSquare(n.id, gridSize);
      if (proj) {
        grid[proj.row][proj.col] = {
          id: n.id,
          label: n.label,
          stage: n.stage
        };
      }
    }
    return { gridSize, grid, lens: this.activeLens, center: this.lattice.centerId };
  }

  getState() {
    return {
      activeLens: this.activeLens,
      availableLenses: Object.keys(LENSES),
      lattice: this.lattice.getSnapshot(),
      historyLength: this.viewHistory.length
    };
  }
}

export function createPerspectiveMatrix(lattice) {
  return new PerspectiveMatrix(lattice);
}
