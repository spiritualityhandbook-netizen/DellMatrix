/**
 * Dual Lattice Kernel (Advanced)
 * Flower of Life dual lattice + Ancient_Psalms operators
 * - Sphere contact lattice (resonance / growth)
 * - Cube address lattice (perspective / phone)
 * - Retrograde traversal (↖)
 * - Ledger shells + sum merge
 * - Compression tokens
 */

export class LatticeNode {
  constructor({ id, label = '', content = null, radius = 1 } = {}) {
    this.id = id || `node-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`;
    this.label = label;
    this.content = content;
    this.radius = radius;
    this.sphere = { x: 0, y: 0, z: 0 };
    this.cube = { i: 0, j: 0, k: 0 };
    this.shell = 0;
    this.stage = 'seed';
    this.height = 0;
    this.contacts = [];
    this.mass = 1;
    this.shellType = 'standard'; // standard | ledger
    this.token = null; // compression token (Wadi-style)
    this.amount = null; // ledger quantity
    this.createdAt = new Date().toISOString();
    this.plantedBy = null;
    this.tags = [];
  }

  toJSON() {
    return {
      id: this.id,
      label: this.label,
      sphere: { ...this.sphere },
      cube: { ...this.cube },
      shell: this.shell,
      shellType: this.shellType,
      stage: this.stage,
      height: this.height,
      mass: this.mass,
      token: this.token,
      amount: this.amount,
      contactCount: this.contacts.length
    };
  }
}

export function computeVesica(nodeA, nodeB) {
  const dx = nodeA.sphere.x - nodeB.sphere.x;
  const dy = nodeA.sphere.y - nodeB.sphere.y;
  const dz = nodeA.sphere.z - nodeB.sphere.z;
  const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
  const r1 = nodeA.radius;
  const r2 = nodeB.radius;
  const sum = r1 + r2;
  const diff = Math.abs(r1 - r2);
  if (distance >= sum) return { distance, strength: 0, type: 'separate' };
  if (distance <= diff) return { distance, strength: 1, type: 'contained' };
  const strength = Number((1 - (distance - diff) / (sum - diff)).toFixed(4));
  return { distance, strength, type: 'vesica' };
}

export function hexShellOffsets(shell) {
  if (shell === 0) return [{ x: 0, y: 0 }];
  const offsets = [];
  let x = shell;
  let y = 0;
  const directions = [
    { x: -1, y: 1 }, { x: -1, y: 0 }, { x: 0, y: -1 },
    { x: 1, y: -1 }, { x: 1, y: 0 }, { x: 0, y: 1 }
  ];
  for (const dir of directions) {
    for (let step = 0; step < shell; step += 1) {
      offsets.push({ x, y });
      x += dir.x;
      y += dir.y;
    }
  }
  return offsets;
}

export function axialToCube(q, r) {
  return { i: q, j: -q - r, k: r };
}

export class DualLattice {
  constructor(options = {}) {
    this.nodes = new Map();
    this.centerId = null;
    this.unitRadius = options.unitRadius ?? 1;
    this.shellSpacing = options.shellSpacing ?? 2;
    this.resonanceLog = [];
    this.generation = 0;
    this.negativeSpace = { channels: [], activeForces: [] };
    this.traversalMode = 'forward'; // forward | retrograde
  }

  addNode({ id, label, content, plantedBy, shellType = 'standard', amount = null } = {}) {
    const node = new LatticeNode({
      id,
      label: label || content || 'untitled',
      content,
      radius: this.unitRadius
    });
    node.plantedBy = plantedBy || null;
    node.shellType = shellType;
    node.amount = amount;
    node.token = this._compressToken(node.label);

    if (!this.centerId) {
      this.centerId = node.id;
      node.shell = 0;
      node.sphere = { x: 0, y: 0, z: 0 };
      node.cube = { i: 0, j: 0, k: 0 };
    } else {
      this._placeOnShell(node);
    }

    this.nodes.set(node.id, node);
    this._updateContacts(node);
    this.generation += 1;
    return node;
  }

  /** Wadi-style compression: first meaningful character / short token */
  _compressToken(label) {
    if (!label) return null;
    const cleaned = String(label).trim();
    if (!cleaned) return null;
    // Acrophonic-inspired: first letter + length hint
    return (cleaned[0] || '?').toUpperCase() + cleaned.length;
  }

  _placeOnShell(node) {
    let shell = 1;
    while (shell < 50) {
      const offsets = hexShellOffsets(shell);
      const occupied = new Set(
        Array.from(this.nodes.values())
          .filter(n => n.shell === shell)
          .map(n => `${n.cube.i},${n.cube.j},${n.cube.k}`)
      );
      for (const off of offsets) {
        const cube = axialToCube(off.x, off.y);
        const key = `${cube.i},${cube.j},${cube.k}`;
        if (!occupied.has(key)) {
          node.shell = shell;
          node.cube = cube;
          const spacing = this.shellSpacing;
          node.sphere = {
            x: spacing * (Math.sqrt(3) * off.x + (Math.sqrt(3) / 2) * off.y),
            y: spacing * ((3 / 2) * off.y),
            z: 0
          };
          return;
        }
      }
      shell += 1;
    }
    node.shell = shell;
    node.sphere = { x: shell * this.shellSpacing, y: 0, z: 0 };
    node.cube = axialToCube(shell, 0);
  }

  setCenter(nodeId) {
    const newCenter = this.nodes.get(nodeId);
    if (!newCenter) return null;
    this.centerId = nodeId;
    const ox = newCenter.sphere.x;
    const oy = newCenter.sphere.y;
    const oz = newCenter.sphere.z;
    for (const node of this.nodes.values()) {
      node.sphere.x -= ox;
      node.sphere.y -= oy;
      node.sphere.z -= oz;
      const dist = Math.sqrt(node.sphere.x ** 2 + node.sphere.y ** 2 + node.sphere.z ** 2);
      node.shell = Math.round(dist / this.shellSpacing);
    }
    newCenter.shell = 0;
    return newCenter;
  }

  _updateContacts(node) {
    node.contacts = [];
    for (const other of this.nodes.values()) {
      if (other.id === node.id) continue;
      const vesica = computeVesica(node, other);
      if (vesica.strength > 0) {
        node.contacts.push({
          nodeId: other.id,
          strength: vesica.strength,
          distance: vesica.distance,
          type: vesica.type
        });
        const existing = other.contacts.find(c => c.nodeId === node.id);
        if (existing) {
          existing.strength = vesica.strength;
          existing.distance = vesica.distance;
        } else {
          other.contacts.push({
            nodeId: node.id,
            strength: vesica.strength,
            distance: vesica.distance,
            type: vesica.type
          });
        }
        if (vesica.type === 'vesica' && vesica.strength > 0.15) {
          this.resonanceLog.push({
            a: node.id,
            b: other.id,
            strength: vesica.strength,
            at: new Date().toISOString()
          });
        }
      }
    }
  }

  /** Retrograde traversal ↖ — walk contacts in reverse order (Rongorongo-inspired) */
  setTraversalMode(mode = 'forward') {
    this.traversalMode = mode === 'retrograde' ? 'retrograde' : 'forward';
    return this.traversalMode;
  }

  walkFrom(nodeId, steps = 5) {
    const start = this.nodes.get(nodeId);
    if (!start) return [];
    const path = [start.id];
    let current = start;
    for (let i = 0; i < steps; i += 1) {
      if (!current.contacts.length) break;
      const ordered = [...current.contacts].sort((a, b) => b.strength - a.strength);
      const pick = this.traversalMode === 'retrograde'
        ? ordered[ordered.length - 1]
        : ordered[0];
      if (!pick || path.includes(pick.nodeId)) break;
      path.push(pick.nodeId);
      current = this.nodes.get(pick.nodeId);
      if (!current) break;
    }
    return path;
  }

  /** Ledger shell: add item with quantity (Linear A/B inspired) */
  addLedgerItem({ label, amount = 1, plantedBy } = {}) {
    return this.addNode({
      label,
      amount: Number(amount) || 1,
      shellType: 'ledger',
      plantedBy
    });
  }

  /** KU-RO style sum merge of ledger nodes */
  sumLedger(nodeIds = []) {
    let total = 0;
    const labels = [];
    for (const id of nodeIds) {
      const n = this.nodes.get(id);
      if (n && n.shellType === 'ledger') {
        total += Number(n.amount) || 0;
        labels.push(n.label);
      }
    }
    const sumNode = this.addNode({
      label: `TOTAL:${labels.slice(0, 3).join('+')}`,
      amount: total,
      shellType: 'ledger',
      plantedBy: 'system'
    });
    sumNode.tags.push('KU-RO', 'sum');
    return { total, sumNode: sumNode.toJSON() };
  }

  grow(nodeId, amount = 0.5) {
    const node = this.nodes.get(nodeId);
    if (!node) return null;
    node.height = Number((node.height + amount).toFixed(2));
    const stages = ['seed', 'sprout', 'stem', 'branch', 'leaf', 'fruit'];
    const idx = stages.indexOf(node.stage);
    const threshold = (idx + 1) * 1.2;
    if (node.height >= threshold && idx < stages.length - 1) {
      node.stage = stages[idx + 1];
    }
    return node;
  }

  getShell(shellNumber) {
    return Array.from(this.nodes.values()).filter(n => n.shell === shellNumber);
  }

  projectToSquare(nodeId, gridSize = 9) {
    const node = this.nodes.get(nodeId);
    if (!node) return null;
    const all = Array.from(this.nodes.values());
    let maxR = 1;
    for (const n of all) {
      const r = Math.sqrt(n.sphere.x ** 2 + n.sphere.y ** 2);
      if (r > maxR) maxR = r;
    }
    const nx = node.sphere.x / maxR;
    const ny = node.sphere.y / maxR;
    const col = Math.floor(((nx + 1) / 2) * (gridSize - 1));
    const row = Math.floor(((ny + 1) / 2) * (gridSize - 1));
    return {
      nodeId,
      col: Math.max(0, Math.min(gridSize - 1, col)),
      row: Math.max(0, Math.min(gridSize - 1, row)),
      gridSize,
      shell: node.shell,
      stage: node.stage,
      vesicaCount: node.contacts.length,
      token: node.token
    };
  }

  attachForce(forceName) {
    if (!this.negativeSpace.activeForces.includes(forceName)) {
      this.negativeSpace.activeForces.push(forceName);
    }
    return this.negativeSpace.activeForces;
  }

  getSnapshot() {
    const center = this.centerId ? this.nodes.get(this.centerId) : null;
    const shells = {};
    for (const node of this.nodes.values()) {
      if (!shells[node.shell]) shells[node.shell] = [];
      shells[node.shell].push(node.toJSON());
    }
    return {
      generation: this.generation,
      nodeCount: this.nodes.size,
      centerId: this.centerId,
      centerLabel: center ? center.label : null,
      traversalMode: this.traversalMode,
      shells,
      recentResonance: this.resonanceLog.slice(-10),
      activeForces: this.negativeSpace.activeForces
    };
  }

  listNodes() {
    return Array.from(this.nodes.values()).map(n => n.toJSON());
  }
}

export function createDualLattice(options = {}) {
  return new DualLattice(options);
}
