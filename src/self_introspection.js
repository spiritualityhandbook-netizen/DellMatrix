/**
 * Self-Introspection Engine
 * 
 * Analyzes the system's own code "page by page" like the Voynich manuscript.
 * Creates understanding of the system's structure and semantics through self-examination.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, '..');

export class SelfIntrospection {
  constructor(kernel) {
    this.kernel = kernel;
    this.pageCache = new Map();
    this.semanticCache = new Map();
  }

  async scanSystemPages() {
    const pages = [];
    
    const zones = [
      'src/mandell_kernel.js',
      'src/mandell_language.js',
      'src/execute_preform.js',
      'src/core/mandell_toolkit.js',
      'src/core/persona_guidance.js',
      'src/core/workspace_context.js',
      'package.json',
      'README.md',
      'AGENTS.md',
      'docs/duo_beta_preform.md'
    ];

    for (const zone of zones) {
      const fullPath = path.join(root, zone);
      if (fs.existsSync(fullPath)) {
        try {
          const content = fs.readFileSync(fullPath, 'utf8');
          pages.push({
            name: zone,
            filePath: zone,
            fullPath: fullPath,
            content: content,
            size: content.length,
            lines: content.split('\n').length,
            type: this.detectFileType(zone)
          });
        } catch (error) {
          console.error(`Failed to read ${zone}:`, error.message);
        }
      }
    }

    return pages;
  }

  detectFileType(filePath) {
    if (filePath.endsWith('.js')) return 'code-javascript';
    if (filePath.endsWith('.json')) return 'config-json';
    if (filePath.endsWith('.md')) return 'documentation';
    return 'unknown';
  }

  async analyzePage(page) {
    const cacheKey = page.filePath;
    if (this.semanticCache.has(cacheKey)) {
      return this.semanticCache.get(cacheKey);
    }

    const analysis = {
      filePath: page.filePath,
      type: page.type,
      size: page.size,
      lines: page.lines,
      complexity: this.calculateComplexity(page),
      semanticSignature: this.extractSemanticSignature(page),
      patterns: this.findPatterns(page),
      themes: this.extractThemes(page),
      dependencies: this.findDependencies(page),
      personasPresent: this.findPersonaReferences(page),
      semanticDensity: this.calculateSemanticDensity(page),
      evolutionReadiness: this.assessEvolutionReadiness(page),
      keyFunctions: this.extractKeyFunctions(page),
      semanticWeight: this.calculateSemanticWeight(page)
    };

    this.semanticCache.set(cacheKey, analysis);
    return analysis;
  }

  calculateComplexity(page) {
    if (page.type.startsWith('documentation') || page.type.startsWith('config')) {
      return page.lines / 100;
    }

    let complexity = 0;
    const content = page.content;

    const nestingLevel = Math.max(
      (content.match(/{/g) || []).length,
      (content.match(/\(/g) || []).length
    ) / 10;

    const functionCount = (content.match(/function|const.*=.*=>|async|class/gi) || []).length;
    const classCount = (content.match(/class|export/gi) || []).length;

    complexity = Math.min(10, (nestingLevel * 2 + functionCount * 0.5 + classCount));
    return parseFloat(complexity.toFixed(2));
  }

  extractSemanticSignature(page) {
    const keywords = [
      { pattern: /kernel|core|foundation/gi, meaning: 'CORE_SYSTEM', weight: 1.0 },
      { pattern: /persona|agent|actor/gi, meaning: 'PERSONA_LAYER', weight: 0.9 },
      { pattern: /psalm|evolution|growth/gi, meaning: 'EVOLUTION_ENGINE', weight: 0.9 },
      { pattern: /execute|run|preform/gi, meaning: 'EXECUTION_LAYER', weight: 0.85 },
      { pattern: /workspace|context|manifest/gi, meaning: 'CONTEXT_LAYER', weight: 0.8 },
      { pattern: /audit|test|verify/gi, meaning: 'VERIFICATION_LAYER', weight: 0.75 },
      { pattern: /ring|memory|state/gi, meaning: 'MEMORY_SYSTEM', weight: 0.8 }
    ];

    const signatures = [];
    for (const { pattern, meaning, weight } of keywords) {
      const matches = page.content.match(pattern);
      if (matches) {
        signatures.push({
          meaning: meaning,
          weight: weight,
          frequency: matches.length
        });
      }
    }

    signatures.sort((a, b) => (b.weight * b.frequency) - (a.weight * a.frequency));
    return signatures.map(s => s.meaning).slice(0, 3).join(' -> ');
  }

  findPatterns(page) {
    const patterns = [];

    if (page.content.includes('export class')) patterns.push('object-oriented');
    if (page.content.includes('async') || page.content.includes('Promise')) patterns.push('asynchronous');
    if (page.content.includes('this.kernel') || page.content.includes('kernel.')) patterns.push('kernel-coupled');
    if (page.content.includes('map') && page.content.includes('filter')) patterns.push('functional');

    return patterns;
  }

  extractThemes(page) {
    const themes = [];

    if (page.content.includes('evolv') || page.content.includes('growth')) themes.push('evolution');
    if (page.content.includes('persona') || page.content.includes('agent')) themes.push('persona-system');
    if (page.content.includes('create') || page.content.includes('manifest')) themes.push('creation');
    if (page.content.includes('bind') || page.content.includes('fuse') || page.content.includes('synthesis')) themes.push('binding');
    if (page.content.includes('audit') || page.content.includes('verify') || page.content.includes('test')) themes.push('verification');
    if (page.content.includes('memory') || page.content.includes('state') || page.content.includes('ring')) themes.push('memory');

    return themes;
  }

  findDependencies(page) {
    const deps = new Set();
    const importRegex = /import\s+.*\s+from\s+['"]([^'"]+)['"]/g;
    let match;

    while ((match = importRegex.exec(page.content)) !== null) {
      if (!match[1].startsWith('node:')) {
        deps.add(match[1]);
      }
    }

    return Array.from(deps);
  }

  findPersonaReferences(page) {
    const personas = [];
    const personaNames = ['Manny', 'Melody', 'Aetheris', 'Mathelody', 'Manelody'];

    for (const persona of personaNames) {
      if (page.content.includes(persona)) {
        personas.push(persona);
      }
    }

    return personas;
  }

  calculateSemanticDensity(page) {
    const semanticKeywords = ['persona', 'kernel', 'psalm', 'evolution', 'ring', 'mandate', 'manifest', 'audit', 'fusion'];
    const matches = semanticKeywords.reduce((count, keyword) => {
      return count + (page.content.toLowerCase().match(new RegExp(keyword, 'g')) || []).length;
    }, 0);

    const density = matches / Math.max(1, page.lines);
    return Math.min(1, density);
  }

  assessEvolutionReadiness(page) {
    let readiness = 0.5;

    const docRatio = (page.content.match(/\/\//g) || []).length / Math.max(1, page.lines);
    readiness += docRatio * 0.3;

    if (/export class/.test(page.content)) readiness += 0.15;
    if (page.filePath.includes('test')) readiness += 0.2;

    return Math.min(1, readiness);
  }

  extractKeyFunctions(page) {
    const functions = [];
    const functionRegex = /(?:export\s+)?(?:async\s+)?(?:function|const)\s+(\w+)/g;
    let match;

    while ((match = functionRegex.exec(page.content)) !== null) {
      if (match[1] && !match[1].match(/^[A-Z]/)) {
        functions.push(match[1]);
      }
    }

    return functions.slice(0, 10);
  }

  calculateSemanticWeight(page) {
    let weight = 0;

    if (page.filePath.includes('kernel')) weight += 0.3;
    if (page.filePath.includes('core')) weight += 0.2;
    if (page.filePath.includes('preform')) weight += 0.2;
    if (page.filePath.includes('test')) weight += 0.15;
    if (page.type.includes('documentation')) weight += 0.15;
    if (page.size > 5000) weight += 0.1;

    return Math.min(1, 0.2 + weight);
  }

  clearCache() {
    this.semanticCache.clear();
    this.pageCache.clear();
  }
}

export default SelfIntrospection;
