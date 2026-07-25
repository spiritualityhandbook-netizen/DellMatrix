/**
 * Format Super-Router
 * Surfaces: TOML | YAML | JSON | HCL
 * Canonical core: plain JSON-compatible tree
 * Learns via residue (zone → format success/fail)
 */

export const FORMATS = ['toml', 'yaml', 'json', 'hcl'];

export const DEFAULT_ZONE_FORMAT = {
  settings: 'toml',
  foundation: 'toml',
  persona: 'yaml',
  workshop: 'yaml',
  document: 'yaml',
  snapshot: 'json',
  interchange: 'json',
  api: 'json',
  snapin: 'hcl',
  module: 'hcl',
  blocks: 'hcl',
  unknown: 'json'
};

export class FormatResidue {
  constructor() {
    this.wins = new Map(); // key zone|format → count
    this.fails = new Map();
  }

  key(zone, format) {
    return `${zone}|${format}`;
  }

  record(zone, format, ok) {
    const k = this.key(zone, format);
    const bag = ok ? this.wins : this.fails;
    bag.set(k, (bag.get(k) || 0) + 1);
    return { zone, format, ok, count: bag.get(k) };
  }

  score(zone, format) {
    const k = this.key(zone, format);
    const w = this.wins.get(k) || 0;
    const f = this.fails.get(k) || 0;
    return w - f;
  }

  snapshot() {
    return {
      wins: Object.fromEntries(this.wins),
      fails: Object.fromEntries(this.fails)
    };
  }
}

export class FormatRouter {
  constructor(policy = DEFAULT_ZONE_FORMAT) {
    this.policy = { ...policy };
    this.residue = new FormatResidue();
  }

  /** Choose format for a zone, biased by residue */
  choose(zone = 'unknown') {
    const z = this.policy[zone] ? zone : 'unknown';
    const base = this.policy[z] || 'json';

    // If another format has clearly better residue score, prefer it
    let best = base;
    let bestScore = this.residue.score(z, base);
    for (const fmt of FORMATS) {
      const s = this.residue.score(z, fmt);
      if (s > bestScore) {
        best = fmt;
        bestScore = s;
      }
    }
    return { zone: z, format: best, baseDefault: base, residueScore: bestScore };
  }

  success(zone, format) {
    return this.residue.record(zone, format, true);
  }

  failure(zone, format) {
    return this.residue.record(zone, format, false);
  }

  /** Canonical is always a JSON-compatible object */
  toCanonical(value) {
    return JSON.parse(JSON.stringify(value));
  }

  /**
   * Lightweight surface markers (not full parsers).
   * Real TOML/YAML/HCL parsing can be added via libs later offline.
   * JSON is fully supported now.
   */
  detectSurface(text = '') {
    const t = String(text).trim();
    if (!t) return 'unknown';
    if (t.startsWith('{') || t.startsWith('[')) return 'json';
    if (/^\s*\w+\s*=\s*/m.test(t) && t.includes('[')) return 'toml';
    if (/^\s*\w+\s*\{/m.test(t)) return 'hcl';
    if (/:\s/m.test(t) || /^-\s/m.test(t)) return 'yaml';
    return 'unknown';
  }

  parseJSON(text) {
    return this.toCanonical(JSON.parse(text));
  }

  serializeJSON(canonical) {
    return JSON.stringify(this.toCanonical(canonical), null, 2);
  }

  /** Round-trip test for JSON surface (Voyman retrograde) */
  roundTripJSON(canonical) {
    try {
      const text = this.serializeJSON(canonical);
      const back = this.parseJSON(text);
      const ok = JSON.stringify(back) === JSON.stringify(this.toCanonical(canonical));
      return { ok, text, back };
    } catch (e) {
      return { ok: false, error: String(e.message || e) };
    }
  }

  status() {
    return {
      policy: this.policy,
      formats: FORMATS,
      residue: this.residue.snapshot()
    };
  }
}

export function createFormatRouter(policy) {
  return new FormatRouter(policy);
}
