/**
 * Dual Lattice Kernel
 *
 * Foundation from Flower of Life examination:
 * - Sphere / hexagonal contact lattice  → resonance, growth, living connection
 * - Cube / orthogonal address lattice   → perspective, navigation, lookup
 *
 * Rules encoded:
 * 1. Equal units (same radius / same cell size)
 * 2. Any node can become the center
 * 3. Resonance = vesica (shared lens), not a thin line
 * 4. Negative space is a real medium (forces flow here)
 * 5. Growth expands in radial shells
 * 6. Phone UI uses square projection of the living lattice
 */

const PHI = (1 + Math.sqrt(5)) / 2;
const HEX_ANGLE = Math.PI / 3; // 60 degrees

/**
 * A single node that exists on both lattices at once.
 */
export class LatticeNode {
  constructor({ id, label = '', content = null, radius = 1 } = {}) {
    this.id = id || `node-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`;
    this.label = label;
    this.content = content;
    this.radius = radius;

    // Sphere lattice position (continuous)
    this.sphere = { x: 0, y: 0, z: 0 };

    // Cube lattice address (discrete)
    this.cube = { i: 0, j: 0, k: 0 };

    // Growth
    this.shell = 0;          // radial shell from current center
    this.stage = 'seed';     // seed | sprout | stem | branch | leaf | fruit
    this.height = 0;

    // Resonance
    this.contacts = [];      // { nodeId, vesicaStrength, distance }
    this.mass = 1;           // for gravity

    // Metadata
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
      stage: this.stage,
      height: this.height,
      mass: this.mass,
      contactCount: this.contacts.length
    };
  }
}

/**
 * Vesica (shared lens) between two nodes.
 * Strength is how deeply the two spheres overlap relative to radius.
 */
export function computeVesica(nodeA, nodeB) {
  const dx = nodeA.sphere.x - nodeB.sphere.x;
  const dy = nodeA.sphere.y - nodeB.sphere.y;
  const dz = nodeA.sphere.z - nodeB.sphere.z;
  const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);

  const r1 = nodeA.radius;
  const r2 = nodeB.radius;
  const sum = r1 + r2;
  const diff = Math.abs(r1 - r2);

  // No overlap
  if (distance >= sum) {
    return { distance, strength: 0, type: 'separate' };
  }
  // One inside the other without touch
  if (distance <= diff) {
    return { distance, strength: 1, type: 'contained' };
  }

  // Proper vesica: overlap strength 0..1
  // 1 when centers coincide (max), 0 when just touching
  const strength = Number((1 - (distance - diff) / (sum - diff)).toFixed(4));
  return { distance, strength, type: 'vesica' };
}

/**
 * Hexagonal ring offsets for shell n (2D first, then lift to 3D).
 * Shell 0 = center only.
 * Shell 1 = 6 neighbors, etc.
 */
export function hexShellOffsets(shell) {
  if (shell === 0) return [{ x: 0, y: 0 }];

  const offsets = [];
  // Start at +x and walk the hex ring
  let x = shell;
  let y = 0;

  const directions = [
    { x: -1, y: 1 },
    { x: -1, y: 0 },
    { x: 0, y: -1 },
    { x: 1, y: -1 },
    { x: 1, y: 0 },
    { x: 0, y: 1 }
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

/**
 * Convert axial hex (q, r) to cube coordinates (i, j, k) with i+j+k=0.
 */
export function axialToCube(q, r) {
  const i = q;
  const k = r;
  const j = -i - k;
  return { i, j, k };
}

/**
 * Dual Lattice Kernel
 */
export class DualLattice {
  constructor(options = {}) {
    this.nodes = new Map();
    this.centerId = null;           // current perspective center
    this.unitRadius = options.unitRadius ?? 1;
    this.shellSpacing = options.shellSpacing ?? 2; // center-to-center distance = 2*radius for perfect packing
    this.resonanceLog = [];
    this.generation = 0;            // Flower generation count
    this.negativeSpace = {          // forces live here
      channels: [],
      activeForces: []
    };
  }

  /**
   * Add a node. If no center exists, this node becomes center.
   */
  addNode({ id, label, content, plantedBy } = {}) {
    const node = new LatticeNode({
      id,
      label: label || content || 'untitled',
      content,
      radius: this.unitRadius
    });
    node.plantedBy = plantedBy || null;

    if (!this.centerId) {
      this.centerId = node.id;
      node.shell = 0;
      node.sphere = { x: 0, y: 0, z: 0 };
      node.cube = { i: 0, j: 0, k: 0 };
    } else {
      // Place on next available shell position
      this._placeOnShell(node);
    }

    this.nodes.set(node.id, node);
    this._updateContacts(node);
    this.generation += 1;
    return node;
  }

  /**
   * Place node on the lowest shell that still has open slots.
   */
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
          // Sphere position from axial hex
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
    // Fallback: put far out
    node.shell = shell;
    node.sphere = { x: shell * this.shellSpacing, y: 0, z: 0 };
    node.cube = axialToCube(shell, 0);
  }

  /**
   * Any node can become the center. Recompute shells and relative view.
   */
  setCenter(nodeId) {
    const newCenter = this.nodes.get(nodeId);
    if (!newCenter) return null;

    this.centerId = nodeId;

    // Translate all sphere positions so new center is at origin
    const ox = newCenter.sphere.x;
    const oy = newCenter.sphere.y;
    const oz = newCenter.sphere.z;

    for (const node of this.nodes.values()) {
      node.sphere.x -= ox;
      node.sphere.y -= oy;
      node.sphere.z -= oz;

      // Recompute shell from distance to origin
      const dist = Math.sqrt(
        node.sphere.x ** 2 + node.sphere.y ** 2 + node.sphere.z ** 2
      );
      node.shell = Math.round(dist / this.shellSpacing);
    }

    newCenter.shell = 0;
    return newCenter;
  }

  /**
   * Update contact list (vesicas) for a node against all others.
   */
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
        // Symmetric update
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

  /**
   * Recompute all contacts (after center shift or bulk change).
   */
  recomputeAllContacts() {
    for (const node of this.nodes.values()) {
      node.contacts = [];
    }
    const list = Array.from(this.nodes.values());
    for (let i = 0; i < list.length; i += 1) {
      for (let j = i + 1; j < list.length; j += 1) {
        const vesica = computeVesica(list[i], list[j]);
        if (vesica.strength > 0) {
          list[i].contacts.push({
            nodeId: list[j].id,
            strength: vesica.strength,
            distance: vesica.distance,
            type: vesica.type
          });
          list[j].contacts.push({
            nodeId: list[i].id,
            strength: vesica.strength,
            distance: vesica.distance,
            type: vesica.type
          });
        }
      }
    }
  }

  /**
   * Grow a node one stage (plant growth mapped onto lattice node).
   */
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

  /**
   * Get all nodes in a given shell relative to current center.
   */
  getShell(shellNumber) {
    return Array.from(this.nodes.values()).filter(n => n.shell === shellNumber);
  }

  /**
   * Square projection for phone viewport.
   * Maps sphere x,y into a square grid index for UI.
   */
  projectToSquare(nodeId, gridSize = 9) {
    const node = this.nodes.get(nodeId);
    if (!node) return null;

    // Normalize position into -1..1 then into 0..gridSize-1
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
      gridSize
    };
  }

  /**
   * Snapshot for Perspective Matrix and UI.
   */
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
      shells,
      recentResonance: this.resonanceLog.slice(-10),
      negativeSpaceChannels: this.negativeSpace.channels.length
    };
  }

  /**
   * Register a force into negative space.
   */
  attachForce(forceName) {
    if (!this.negativeSpace.activeForces.includes(forceName)) {
      this.negativeSpace.activeForces.push(forceName);
    }
    return this.negativeSpace.activeForces;
  }

  listNodes() {
    return Array.from(this.nodes.values()).map(n => n.toJSON());
  }
}

export function createDualLattice(options = {}) {
  return new DualLattice(options);
}
