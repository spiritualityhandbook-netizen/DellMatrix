export class VisualCube {
  constructor(cube = {}) {
    this.id = cube.id || `cube-${Math.random().toString(36).slice(2, 8)}`;
    this.name = cube.name || 'Harmonic Cube';
    this.state = cube.state || 'blank';
    this.fogRate = cube.fogRate || 0.08;
    this.nodes = this.initializeNodes();
    this.links = [];
    this.visibility = 'balanced';
  }

  initializeNodes() {
    return [
      { id: 'core-emergence', label: 'Emergence Seed', type: 'seed', visible: true, x: 0, y: 0 },
      { id: 'harmony-zone', label: 'Harmony Zone', type: 'zone', visible: true, x: 1, y: 0 },
      { id: 'fog-boundary', label: 'Fog Boundary', type: 'boundary', visible: this.state !== 'blank', x: 0, y: 1 },
      { id: 'psalm-nexus', label: 'Psalm Nexus', type: 'psalms', visible: true, x: -1, y: 0 }
    ];
  }

  renderASCII() {
    const lines = [];
    lines.push(`╔═══════════════════════════════╗`);
    lines.push(`║ ${this.name.padEnd(27)} ║`);
    lines.push(`║ State: ${this.state.padEnd(21)} ║`);
    lines.push(`║ Fog: ${(this.fogRate * 100).toFixed(0)}%${' '.repeat(22)} ║`);
    lines.push(`╠═══════════════════════════════╣`);
    lines.push(`║ Nodes: ${this.nodes.length}                       ║`);
    lines.push(`║ Links: ${this.links.length}                       ║`);
    lines.push(`║ Visible Nodes: ${this.nodes.filter(n => n.visible).length}              ║`);
    lines.push(`╚═══════════════════════════════╝`);
    return lines.join('\n');
  }

  renderNodeMap() {
    const lines = ['', 'Node Map:'];
    this.nodes.forEach(node => {
      const marker = node.visible ? '◉' : '◯';
      lines.push(`  ${marker} [${node.type}] ${node.label}`);
    });
    return lines.join('\n');
  }
}

export function createVisualCube(cube) {
  return new VisualCube(cube);
}
