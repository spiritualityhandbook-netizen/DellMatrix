export class PersonaRoster {
  constructor(personas = []) {
    this.personas = personas;
  }

  renderRoster() {
    const lines = ['', '═══ PERSONA ROSTER ═══', ''];
    this.personas.forEach(p => {
      const status = p.active ? '● ACTIVE' : '○ idle';
      lines.push(`${p.emoji || '◌'} ${p.name} — ${status}`);
      lines.push(`   Role: ${p.role || 'agent'} | Focus: ${p.focus || 'general'}`);
      lines.push('');
    });
    return lines.join('\n');
  }

  renderCompact() {
    return 'Personas: ' + this.personas.map(p => `${p.emoji || '◌'} ${p.name}`).join(' | ');
  }

  toJSON() {
    return { personas: this.personas };
  }
}

export function createPersonaRoster(personas) {
  return new PersonaRoster(personas);
}
