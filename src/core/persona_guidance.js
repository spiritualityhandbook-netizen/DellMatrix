/**
 * Persona Guidance — includes The_Ancient for Ancient_Psalms
 */

export class PersonaGuidance {
  constructor(workspace = {}) {
    this.workspace = workspace;
    this.roles = this.defineRoles();
  }

  defineRoles() {
    return {
      Manny: {
        emoji: '🕵️',
        title: 'Logic Checker',
        where: 'src/mandell_kernel.js, tests/',
        what: 'Verify determinism, test correctness, audit regressions',
        why: 'Kernel must stay mathematically sound.',
        zones: ['runtime', 'tests'],
        focus: 'validation, structure, edge cases'
      },
      Melody: {
        emoji: '❀',
        title: 'Growth Guide',
        where: 'src/execute_preform.js, docs/',
        what: 'Guide evolution steps, track emergence',
        why: 'Growth follows preform pillars and phase plans.',
        zones: ['runtime', 'docs'],
        focus: 'emergence, evolution, fractal patterns'
      },
      Aetheris: {
        emoji: '🌫️',
        title: 'Aether Weaver',
        where: 'src/core/',
        what: 'Morphology, semantic nets, zone coherence',
        why: 'Workspace structure must stay transparent.',
        zones: ['core', 'runtime'],
        focus: 'synthesis, morphology, coherence'
      },
      Mathelody: {
        emoji: '🕵️❀🌫️',
        title: 'Apex Fusion',
        where: 'entire workspace',
        what: 'Fuse perspectives, execute tru-fusion',
        why: 'Resolves conflict and synthesizes.',
        zones: ['runtime', 'core', 'visual', 'docs', 'tests'],
        focus: 'unity, integration, recursive execution'
      },
      The_Ancient: {
        emoji: '🪨',
        title: 'Structural Pattern Keeper',
        where: 'src/core/dual_lattice.js, Perspective: ancient_psalms',
        what: 'Extract structural operators from historical scripts; run retrograde walks; manage ledger shells and compression tokens',
        why: 'Ancient patterns supply lawful operators (ledger, retrograde, compression) without claiming scientific decipherment.',
        zones: ['core', 'runtime'],
        focus: 'structural pattern, glyph-weight, reverse-boustrophedon state',
        category: 'Ancient_Psalms',
        ability: 'Reverse Boustrophedon — forward, backward, inverted traversal without losing lattice state'
      }
    };
  }

  getGuidanceForPersona(personaName) {
    const role = this.roles[personaName];
    if (!role) return null;
    return {
      persona: personaName,
      emoji: role.emoji,
      title: role.title,
      responsibilities: { where: role.where, what: role.what, why: role.why },
      zones: role.zones,
      focus: role.focus,
      category: role.category || null,
      ability: role.ability || null
    };
  }

  getAllGuidance() {
    return Object.keys(this.roles).map(name => this.getGuidanceForPersona(name));
  }
}

export function createPersonaGuidance(workspace) {
  return new PersonaGuidance(workspace);
}
