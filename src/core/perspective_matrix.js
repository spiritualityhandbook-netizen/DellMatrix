/**
 * Perspective Matrix (Advanced)
 * Lenses + Ancient_Psalms room + enriched phone grid
 */

import { createDualLattice } from './dual_lattice.js';

export const LENSES = {
  growth: {
    id: 'growth',
    name: 'Growth',
    description: 'Stages and height as plants'
  },
  water: {
    id: 'water',
    name: 'Water',
    description: 'Streams, rivers, pools'
  },
  force: {
    id: 'force',
    name: 'Force',
    description: 'Gravity, breath, weather in voids'
  },
  network: {
    id: 'network',
    name: 'Network',
    description: 'Vesica contacts and strength'
  },
  personal: {
    id: 'personal',
    name: 'Personal',
    description: 'Only what you planted'
  },
  shared: {
    id: 'shared',
    name: 'Shared',
    description: 'Nodes that resonated'
  },
  ancient_psalms: {
    id: 'ancient_psalms',
    name: 'Ancient Psalms',
    description: 'Ledger shells, retrograde walk, compression tokens, historical structural operators',
    emoji: '🏺📜🗿'
  }
};

export class PerspectiveMatrix {
  constructor(lattice = null) {
    this.lattice = lattice || createDualLattice();
    this.activeLens = 'growth';
    this.viewHistory = [];
    this.activePersona = null;
  }

  lookFrom(nodeId) {
    const center = this.lattice.setCenter(nodeId);
    this.viewHistory.push({ type: 'center', nodeId, at: new Date().toISOString() });
    return center;
  }

  setLens(lensId) {
    if (!LENSES[lensId]) return this.activeLens;
    this.activeLens = lensId;
    this.viewHistory.push({ type: 'lens', lens: lensId, at: new Date().toISOString() });
    // When entering Ancient Psalms, attach structural forces into voids
    if (lensId === 'ancient_psalms') {
      this.lattice.attachForce('Water');
      this.lattice.attachForce('Time');
      this.lattice.attachForce('Gravity');
    }
    return this.activeLens;
  }

  setPersona(personaName) {
    this.activePersona = personaName;
    return this.activePersona;
  }

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
            visual: `${this._stageArt(n.stage)} ${n.label}`
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
          activeForces: snapshot.activeForces,
          nodes: nodes.length
        };

      case 'ancient_psalms':
        return {
          lens: 'ancient_psalms',
          emoji: '🏺📜🗿',
          center: snapshot.centerLabel,
          traversalMode: snapshot.traversalMode,
          persona: this.activePersona || 'The_Ancient',
          items: nodes.map(n => ({
            id: n.id,
            label: n.label,
            token: n.token,
            shellType: n.shellType,
            amount: n.amount,
            shell: n.shell,
            stage: n.stage,
            vesicaCount: n.contactCount
          })),
          operators: ['ledger-shell', 'retrograde-walk', 'compression-token', 'sum-merge']
        };

      case 'personal':
        return {
          lens: 'personal',
          items: nodes.filter(n => n.plantedBy)
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
    const art = { seed: '·', sprout: '🌱', stem: '｜', branch: 'Ｙ', leaf: '🌿', fruit: '🍎' };
    return art[stage] || '?';
  }

  /** Phone grid enriched with shell, stage, vesica count, token */
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
          stage: n.stage,
          shell: n.shell,
          vesicaCount: n.contactCount,
          token: n.token,
          shellType: n.shellType
        };
      }
    }
    return {
      gridSize,
      grid,
      lens: this.activeLens,
      center: this.lattice.centerId,
      traversalMode: this.lattice.traversalMode
    };
  }

  getState() {
    return {
      activeLens: this.activeLens,
      availableLenses: Object.keys(LENSES),
      activePersona: this.activePersona,
      lattice: this.lattice.getSnapshot(),
      historyLength: this.viewHistory.length
    };
  }
}

export function createPerspectiveMatrix(lattice) {
  return new PerspectiveMatrix(lattice);
}
