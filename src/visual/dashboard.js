import { createVisualCube } from './cube_renderer.js';
import { createPersonaRoster } from './persona_roster.js';
import { createPsalmSanctuary } from './psalm_sanctuary.js';

export class VisualDashboard {
  constructor(kernel = null) {
    this.kernel = kernel;
    this.cube = kernel?.cubes[0] ? createVisualCube(kernel.cubes[0]) : null;
    this.roster = createPersonaRoster(kernel?.personas || []);
    this.sanctuary = createPsalmSanctuary(kernel?.psalms || []);
    this.mode = 'overview';
  }

  updateFromKernel(kernel) {
    this.kernel = kernel;
    if (kernel.cubes[0]) this.cube = createVisualCube(kernel.cubes[0]);
    this.roster = createPersonaRoster(kernel.personas);
    this.sanctuary = createPsalmSanctuary(kernel.psalms);
  }

  setMode(mode) {
    if (['overview', 'cube', 'roster', 'sanctuary'].includes(mode)) this.mode = mode;
  }

  render() {
    const sections = [];
    switch (this.mode) {
      case 'overview': sections.push(this.renderOverview()); break;
      case 'cube':
        sections.push(this.cube?.renderASCII() || 'No cube initialized');
        sections.push(this.cube?.renderNodeMap() || '');
        break;
      case 'roster': sections.push(this.roster.renderRoster()); break;
      case 'sanctuary':
        sections.push(this.sanctuary.renderSanctuary());
        sections.push(this.sanctuary.renderNexusInfo());
        break;
      default: sections.push('Unknown mode.');
    }
    return sections.join('\n');
  }

  renderOverview() {
    const lines = [];
    lines.push('');
    lines.push('╔═══════════════════════════════════════════════════════╗');
    lines.push('║            DELL MATRIX VISUAL DASHBOARD               ║');
    lines.push('╚═══════════════════════════════════════════════════════╝');
    lines.push('');
    if (this.cube) lines.push(this.cube.renderASCII());
    lines.push('');
    lines.push(this.roster.renderCompact());
    lines.push('');
    if (this.kernel?.activePersona) {
      lines.push(`Active Persona: ${this.kernel.activePersona.emoji} ${this.kernel.activePersona.name}`);
    }
    lines.push(`Tokenless mode: ${this.kernel?.tokenlessMode ? 'enabled' : 'disabled'}`);
    lines.push(`Psalms Available: ${this.sanctuary.psalms.length}`);
    lines.push(`Fusion Modes: ${this.kernel?.fusions.length || 0}`);
    return lines.join('\n');
  }
}

export function createVisualDashboard(kernel) {
  return new VisualDashboard(kernel);
}
