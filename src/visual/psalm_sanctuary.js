export class PsalmSanctuary {
  constructor(psalms = []) {
    this.psalms = psalms;
  }

  renderSanctuary() {
    const lines = ['', '═══ PSALM SANCTUARY ═══', ''];
    this.psalms.forEach((p, i) => {
      lines.push(`${i + 1}. ${p.title || p.id}`);
      if (p.role) lines.push(`   Role: ${p.role}`);
    });
    if (!this.psalms.length) lines.push('(No psalms loaded)');
    return lines.join('\n');
  }

  renderNexusInfo() {
    return `\nPsalm Nexus: ${this.psalms.length} psalms active in the matrix.`;
  }

  toJSON() {
    return { psalms: this.psalms };
  }
}

export function createPsalmSanctuary(psalms) {
  return new PsalmSanctuary(psalms);
}
