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
        why: 'The kernel must be mathematically sound and testable.',
        zones: ['runtime', 'tests'],
        focus: 'validation, structure, edge cases'
      },
      Melody: {
        emoji: '❀',
        title: 'Growth Guide',
        where: 'src/execute_preform.js, docs/',
        what: 'Guide evolution steps, track emergence, expand preform rhythm',
        why: 'Growth follows the preform pillars and phase plans.',
        zones: ['runtime', 'docs'],
        focus: 'emergence, evolution, fractal patterns'
      },
      Aetheris: {
        emoji: '🌫️',
        title: 'Aether Weaver',
        where: 'src/core/',
        what: 'Understand system morphology, weave persona semantic nets',
        why: 'Workspace structure must be transparent and coherent.',
        zones: ['core', 'runtime'],
        focus: 'synthesis, morphology, coherence'
      },
      Mathelody: {
        emoji: '🕵️❀🌫️',
        title: 'Apex Fusion',
        where: 'entire workspace',
        what: 'Fuse all perspectives, execute tru-fusion mode',
        why: 'Mathelody resolves conflicts and synthesizes.',
        zones: ['runtime', 'core', 'visual', 'docs', 'tests'],
        focus: 'unity, integration, recursive execution'
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
      focus: role.focus
    };
  }
}

export function createPersonaGuidance(workspace) {
  return new PersonaGuidance(workspace);
}
