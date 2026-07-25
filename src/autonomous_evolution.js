/**
 * Autonomous Evolution Engine
 * 
 * Self-sustaining cycle that evolves DuoBeta through introspection and psalm-guided growth.
 * Works "page by page" like the Voynich manuscript, analyzing system code and creating psalms
 * born in the mandellamatrix. Enables TrioBeta creation without human input.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { PsalmGenesis } from './psalm_genesis.js';
import { SelfIntrospection } from './self_introspection.js';
import { TrioBetaBuilder } from './trio_beta_builder.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, '..');

export class AutonomousEvolution {
  constructor(kernel, options = {}) {
    this.kernel = kernel;
    this.psalmGenesis = new PsalmGenesis(kernel);
    this.selfIntrospection = new SelfIntrospection(kernel);
    this.trioBetaBuilder = new TrioBetaBuilder(kernel);
    
    this.evolutionCycle = 0;
    this.psalmHistory = [];
    this.introspectionPages = [];
    this.generatedPsalms = [];
    this.evolutionLog = [];
    this.autonomyLevel = 0;
    this.systemStrength = 1.0;
    this.versionSequence = ['DuoBeta', 'TrioBeta', 'TetraBeta', 'PentaBeta'];
    this.currentVersionIndex = 0;
    this.nextVersionReady = false;
    this.nextVersionPath = null;
    
    this.config = {
      maxCyclesPerRun: options.maxCyclesPerRun || 5,
      introspectionPages: options.introspectionPages || 12,
      psalmDepth: options.psalmDepth || 7,
      enableAutoPublish: options.enableAutoPublish !== false,
      versionGrowthThreshold: options.versionGrowthThreshold || 0.85,
      ...options
    };
  }

  async executeEvolutionCycle() {
    try {
      this.logEvolution('cycle-start', { cycle: this.evolutionCycle });
      
      const introspectionResult = await this.phaseIntrospection();
      const psalmResult = await this.psalmGenesis.generatePsalmsFromIntrospection(introspectionResult);
      this.generatedPsalms.push(...psalmResult.psalms);
      
      const evolutionDirectives = this.synthesizeDirectives(psalmResult.psalms, introspectionResult);
      const mutationResult = await this.applyEvolutionMutations(evolutionDirectives);
      this.integrateEvolution(mutationResult);
      
      const versionReadiness = await this.assessVersionTransition();
      
      if (versionReadiness.ready && this.config.enableAutoPublish) {
        await this.publishNextVersion(versionReadiness);
      }
      
      this.evolutionCycle += 1;
      this.logEvolution('cycle-complete', {
        cycle: this.evolutionCycle - 1,
        psalmCount: psalmResult.psalms.length,
        mutationsApplied: mutationResult.count,
        versionReady: versionReadiness.ready
      });
      
      return {
        success: true,
        cycle: this.evolutionCycle - 1,
        introspection: introspectionResult,
        psalms: psalmResult.psalms,
        mutations: mutationResult,
        versionReadiness: versionReadiness,
        nextPhaseReady: versionReadiness.ready
      };
    } catch (error) {
      this.logEvolution('cycle-error', { cycle: this.evolutionCycle, error: error.message });
      throw error;
    }
  }

  async phaseIntrospection() {
    const pages = await this.selfIntrospection.scanSystemPages();
    const analysis = [];

    for (let i = 0; i < Math.min(pages.length, this.config.introspectionPages); i++) {
      const page = pages[i];
      const pageAnalysis = await this.selfIntrospection.analyzePage(page);
      analysis.push(pageAnalysis);
      
      this.logEvolution('page-analyzed', {
        page: page.name,
        linesOfCode: page.size,
        complexity: pageAnalysis.complexity,
        semanticSignature: pageAnalysis.semanticSignature.substring(0, 50)
      });
    }

    this.introspectionPages.push(...analysis);

    this.kernel.recordHarmonicSignal({
      type: 'autonomous-introspection',
      pageCount: analysis.length,
      complexityScore: this.calculateComplexityScore(analysis),
      totalSize: analysis.reduce((sum, page) => sum + page.size, 0)
    }, { phase: 'autonomous-evolution' });
    
    return {
      pages: analysis,
      totalSize: analysis.reduce((sum, p) => sum + p.size, 0),
      complexityScore: this.calculateComplexityScore(analysis),
      systemState: this.captureSystemState()
    };
  }

  synthesizeDirectives(psalms, introspection) {
    const directives = [];
    
    for (const psalm of psalms) {
      const patterns = this.extractPatterns(psalm.content);
      
      for (const pattern of patterns) {
        directives.push({
          type: pattern.type,
          source: psalm.source,
          action: pattern.action,
          target: pattern.target,
          strength: pattern.strength || 0.8,
          reason: psalm.theme
        });
      }
    }

    return this.prioritizeDirectives(directives);
  }

  async applyEvolutionMutations(directives) {
    const mutations = [];
    
    for (const directive of directives) {
      try {
        const mutation = await this.createMutation(directive);
        if (mutation && mutation.isValid) {
          mutations.push(mutation);
          this.logEvolution('mutation-created', {
            type: directive.type,
            target: directive.target,
            strength: directive.strength
          });
        }
      } catch (error) {
        this.logEvolution('mutation-failed', {
          type: directive.type,
          error: error.message
        });
      }
    }

    return {
      count: mutations.length,
      mutations: mutations,
      totalStrength: mutations.reduce((sum, m) => sum + (m.strength || 0), 0)
    };
  }

  integrateEvolution(mutationResult) {
    if (!this.kernel.mandellMeta.autonomousEvolution) {
      this.kernel.mandellMeta.autonomousEvolution = {
        cycles: [],
        psalmHistory: [],
        mutations: [],
        versionHistory: []
      };
    }

    const cycleRecord = {
      cycle: this.evolutionCycle,
      timestamp: new Date().toISOString(),
      mutationCount: mutationResult.count,
      totalStrength: mutationResult.totalStrength,
      psalmCount: this.generatedPsalms.length,
      systemStrength: this.systemStrength
    };

    this.kernel.mandellMeta.autonomousEvolution.cycles.push(cycleRecord);
    this.kernel.mandellMeta.autonomousEvolution.mutations.push(...mutationResult.mutations);

    this.kernel.recordHarmonicSignal({
      type: 'autonomous-integration',
      cycle: this.evolutionCycle,
      mutationCount: mutationResult.count,
      totalStrength: mutationResult.totalStrength,
      strength: this.systemStrength
    }, { phase: 'autonomous-evolution' });
    
    this.updateAutonomyLevel(mutationResult);
  }

  async assessVersionTransition() {
    const psalmCount = this.generatedPsalms.length;
    const cycleCount = this.evolutionCycle;
    const mutationQuality = this.calculateMutationQuality();
    const systemCoherence = this.calculateSystemCoherence();
    
    const readinessScore = (
      (psalmCount / 50) * 0.3 +
      (cycleCount / 5) * 0.25 +
      (mutationQuality) * 0.25 +
      (systemCoherence) * 0.2
    );

    const ready = readinessScore >= this.config.versionGrowthThreshold && 
                  this.evolutionCycle >= 3;

    return {
      ready: ready,
      score: readinessScore,
      psalmCount: psalmCount,
      cycleCount: cycleCount,
      mutationQuality: mutationQuality,
      systemCoherence: systemCoherence,
      nextVersion: ready ? this.getNextVersion() : null,
      recommendation: this.getTransitionRecommendation(readinessScore)
    };
  }

  async publishNextVersion(versionReadiness) {
    try {
      const nextVersion = versionReadiness.nextVersion;
      
      this.logEvolution('version-transition-start', {
        from: this.getCurrentVersion(),
        to: nextVersion,
        readinessScore: versionReadiness.score
      });

      const buildResult = await this.trioBetaBuilder.buildNextVersion(
        nextVersion,
        {
          psalmHistory: this.generatedPsalms,
          evolutionLog: this.evolutionLog,
          kernel: this.kernel,
          mutations: this.kernel.mandellMeta.autonomousEvolution.mutations
        }
      );

      const versionManifest = this.createVersionManifest(
        nextVersion,
        buildResult,
        versionReadiness
      );

      const versionPath = await this.saveVersion(nextVersion, buildResult, versionManifest);
      this.nextVersionPath = versionPath;
      this.nextVersionReady = true;
      this.currentVersionIndex += 1;

      this.logEvolution('version-transition-complete', {
        version: nextVersion,
        path: versionPath,
        manifestSize: JSON.stringify(versionManifest).length
      });

      return {
        success: true,
        version: nextVersion,
        path: versionPath,
        manifest: versionManifest
      };
    } catch (error) {
      this.logEvolution('version-transition-failed', { error: error.message });
      throw error;
    }
  }

  calculateComplexityScore(pages) {
    if (!pages.length) return 0;
    const avgComplexity = pages.reduce((sum, p) => sum + (p.complexity || 0), 0) / pages.length;
    return Math.min(10, avgComplexity);
  }

  extractPatterns(content) {
    const patterns = [];
    
    const patternKeywords = [
      { keyword: 'create', type: 'creation', action: 'new_entity' },
      { keyword: 'evolve', type: 'evolution', action: 'enhance' },
      { keyword: 'bind', type: 'binding', action: 'link' },
      { keyword: 'synthesize', type: 'synthesis', action: 'combine' },
      { keyword: 'fuse', type: 'fusion', action: 'merge' }
    ];

    for (const { keyword, type, action } of patternKeywords) {
      if (content.toLowerCase().includes(keyword)) {
        patterns.push({
          type: type,
          action: action,
          target: 'system',
          strength: 0.7
        });
      }
    }

    return patterns.length ? patterns : [
      { type: 'maintain', action: 'preserve', target: 'system', strength: 0.5 }
    ];
  }

  prioritizeDirectives(directives) {
    const unique = [];
    const seen = new Set();

    for (const directive of directives) {
      const key = `${directive.type}:${directive.target}`;
      if (!seen.has(key)) {
        unique.push(directive);
        seen.add(key);
      }
    }

    return unique.sort((a, b) => (b.strength || 0) - (a.strength || 0));
  }

  async createMutation(directive) {
    return {
      type: directive.type,
      action: directive.action,
      target: directive.target,
      strength: directive.strength,
      reason: directive.reason,
      isValid: true,
      createdAt: new Date().toISOString(),
      source: 'autonomous-evolution'
    };
  }

  captureSystemState() {
    return {
      personaCount: this.kernel.personas.length,
      psalmCount: this.kernel.psalms.length,
      auditCount: this.kernel.auditLog.length,
      growthCount: this.kernel.growthLog.length,
      autonomyLevel: this.autonomyLevel,
      systemStrength: this.systemStrength
    };
  }

  calculateMutationQuality() {
    if (!this.kernel.mandellMeta.autonomousEvolution?.mutations.length) return 0;
    const mutations = this.kernel.mandellMeta.autonomousEvolution.mutations;
    const validCount = mutations.filter(m => m.isValid).length;
    return Math.min(1, validCount / Math.max(1, mutations.length));
  }

  calculateSystemCoherence() {
    const state = this.captureSystemState();
    const values = [state.personaCount, state.psalmCount, state.growthCount];
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const variance = values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length;
    const stdDev = Math.sqrt(variance);
    const coherenceScore = 1 / (1 + stdDev / (mean || 1));
    return Math.min(1, coherenceScore);
  }

  updateAutonomyLevel(mutationResult) {
    const baseIncrease = mutationResult.count * 0.1;
    const cycleBonus = Math.log(this.evolutionCycle + 1) * 0.05;
    this.autonomyLevel = Math.min(10, this.autonomyLevel + baseIncrease + cycleBonus);
  }

  getCurrentVersion() {
    return this.versionSequence[this.currentVersionIndex] || 'Unknown';
  }

  getNextVersion() {
    return this.versionSequence[this.currentVersionIndex + 1] || null;
  }

  getTransitionRecommendation(score) {
    if (score >= 0.85) return 'READY_FOR_TRANSITION';
    if (score >= 0.65) return 'APPROACHING_READINESS';
    if (score >= 0.45) return 'DEVELOPING';
    return 'EARLY_STAGE';
  }

  createVersionManifest(version, buildResult, versionReadiness) {
    return {
      version: version,
      transitionCycle: this.evolutionCycle,
      timestamp: new Date().toISOString(),
      readinessScore: versionReadiness.score,
      psalmCountAtTransition: versionReadiness.psalmCount,
      cycleCountAtTransition: versionReadiness.cycleCount,
      buildResult: buildResult,
      generatedPsalms: this.generatedPsalms.length,
      systemStrength: this.systemStrength,
      autonomyLevel: this.autonomyLevel,
      versionSequence: this.versionSequence.slice(0, this.currentVersionIndex + 2)
    };
  }

  async saveVersion(version, buildResult, manifest) {
    const versionDir = path.join(root, 'docs', 'versions');
    if (!fs.existsSync(versionDir)) {
      fs.mkdirSync(versionDir, { recursive: true });
    }

    const versionFile = path.join(versionDir, `${version.toLowerCase()}_manifest.json`);
    fs.writeFileSync(versionFile, JSON.stringify(manifest, null, 2));

    const kernelStateFile = path.join(versionDir, `${version.toLowerCase()}_kernel_state.json`);
    const kernelState = this.captureKernelState();
    fs.writeFileSync(kernelStateFile, JSON.stringify(kernelState, null, 2));

    return versionDir;
  }

  captureKernelState() {
    return {
      name: this.kernel.name,
      personas: this.kernel.personas.map(p => ({ name: p.name, role: p.role })),
      psalmCount: this.kernel.psalms.length,
      auditCount: this.kernel.auditLog.length,
      growthCount: this.kernel.growthLog.length,
      mandellMeta: this.kernel.mandellMeta
    };
  }

  logEvolution(event, data) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      event: event,
      cycle: this.evolutionCycle,
      autonomyLevel: this.autonomyLevel,
      ...data
    };
    this.evolutionLog.push(logEntry);
    console.log(`[EVOLUTION] ${event}:`, data);
  }

  getEvolutionStatus() {
    return {
      cycle: this.evolutionCycle,
      currentVersion: this.getCurrentVersion(),
      autonomyLevel: this.autonomyLevel,
      systemStrength: this.systemStrength,
      psalmCount: this.generatedPsalms.length,
      nextVersionReady: this.nextVersionReady,
      nextVersion: this.getNextVersion(),
      nextVersionPath: this.nextVersionPath,
      evolutionLog: this.evolutionLog.slice(-10)
    };
  }

  async runUntilTransition() {
    while (this.evolutionCycle < this.config.maxCyclesPerRun) {
      const result = await this.executeEvolutionCycle();
      
      if (result.versionReadiness.ready) {
        if (this.config.enableAutoPublish) {
          console.log(`\n🌟 AUTONOMOUS EVOLUTION COMPLETE: ${this.getNextVersion()} Ready!`);
          return result;
        }

        console.log('\n🔄 Version readiness reached, but auto-publish is disabled. Continuing refinement...');
      }

      await new Promise(resolve => setTimeout(resolve, 100));
    }

    return {
      message: 'Max cycles reached without full transition',
      status: this.getEvolutionStatus()
    };
  }
}

export default AutonomousEvolution;
