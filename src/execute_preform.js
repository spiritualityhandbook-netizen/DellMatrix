import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { MandellKernel } from './mandell_kernel.js';
import { createWorkspaceContext } from './core/workspace_context.js';
import { createPersonaGuidance } from './core/persona_guidance.js';

let pdfParseLib = null;
async function getPdfParse() {
  if (pdfParseLib) {
    return pdfParseLib;
  }

  const imported = await import('pdf-parse');
  pdfParseLib = imported.default || imported;
  return pdfParseLib;
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, '..');

function readText(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function resolveDriveRoot(baseDir) {
  const explicitCandidates = [
    process.env.MANDLL_GOOGLE_DRIVE_PATH,
    process.env.GOOGLE_DRIVE_PATH,
    process.env.GOOGLE_DRIVE_DIR
  ].filter(Boolean);

  if (explicitCandidates.length) {
    const expanded = explicitCandidates[0].startsWith('~')
      ? path.join(os.homedir(), explicitCandidates[0].slice(1))
      : explicitCandidates[0];
    return path.resolve(baseDir, expanded);
  }

  const fallbackCandidates = [
    path.join(baseDir, 'Google Drive'),
    path.join(os.homedir(), 'Google Drive')
  ];

  const chosen = fallbackCandidates.find(candidate => candidate && fs.existsSync(candidate)) || fallbackCandidates.find(Boolean);
  if (!chosen) return null;

  return path.resolve(baseDir, chosen);
}

export function mirrorArtifactsToDrive(reportPath, statePath, baseDir = root) {
  const driveRoot = resolveDriveRoot(baseDir);
  if (!driveRoot) return null;

  fs.mkdirSync(driveRoot, { recursive: true });

  const reportCopy = path.join(driveRoot, path.basename(reportPath));
  const stateCopy = statePath ? path.join(driveRoot, path.basename(statePath)) : null;

  if (fs.existsSync(reportPath)) {
    fs.copyFileSync(reportPath, reportCopy);
  }

  if (stateCopy && fs.existsSync(statePath)) {
    fs.copyFileSync(statePath, stateCopy);
  }

  return {
    driveRoot,
    reportPath: reportCopy,
    statePath: stateCopy
  };
}

function scanDrivePdfs(driveRoot) {
  if (!driveRoot || !fs.existsSync(driveRoot)) {
    return [];
  }

  const files = [];
  const entries = fs.readdirSync(driveRoot, { withFileTypes: true });

  entries.forEach((entry) => {
    const entryPath = path.join(driveRoot, entry.name);
    if (entry.isDirectory()) {
      files.push(...scanDrivePdfs(entryPath));
    } else if (entry.isFile()) {
      const lowerName = entry.name.toLowerCase();
      if (lowerName.endsWith('.pdf') || lowerName.endsWith('.md') || lowerName.endsWith('.txt')) {
        files.push(entryPath);
      }
    }
  });

  return files;
}

async function extractDocumentText(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  try {
    if (ext === '.pdf') {
      const data = fs.readFileSync(filePath);
      const pdfParse = await getPdfParse();
      const parsed = await pdfParse(data);
      const text = String(parsed.text || '').trim();
      if (text) {
        return text;
      }
      return path.basename(filePath);
    }

    if (ext === '.md' || ext === '.txt') {
      return fs.readFileSync(filePath, 'utf8');
    }

    return path.basename(filePath);
  } catch (error) {
    return `Drive read error for ${path.basename(filePath)}: ${error.message}`;
  }
}

async function buildDrivePages() {
  const driveRoot = resolveDriveRoot(root);
  if (!driveRoot) {
    return [];
  }

  const pdfFiles = scanDrivePdfs(driveRoot);
  if (!pdfFiles.length) {
    return [];
  }

  const pages = [];
  for (let index = 0; index < pdfFiles.length; index += 1) {
    const filePath = pdfFiles[index];
    const content = await extractDocumentText(filePath);
    pages.push({
      id: `drive-pdf-${index + 1}`,
      title: path.basename(filePath),
      source: filePath,
      content
    });
  }

  return pages;
}

async function buildPages() {
  const preform = readText('docs/duo_beta_preform.md');
  const readme = readText('README.md');
  const seed = readText('seeds/phase1_blank_matrix.js');
  const drivePages = await buildDrivePages();

  return [
    { id: 'preform', content: preform },
    { id: 'readme', content: readme },
    { id: 'seed', content: seed },
    ...drivePages
  ];
}

function buildReport(kernel, execution, growth) {
  const lines = [];
  lines.push('# Duo Beta Mandell Execution Report');
  lines.push('');
  lines.push('## Recursive directive executed');
  lines.push('');
  lines.push(kernel.renderPreform());
  lines.push('');
  lines.push(`- Summary: ${growth.summary}`);
  lines.push(`- Autonomous expression: ${growth.expression || 'autonomous growth active within safe boundaries'}`);
  lines.push(`- Execution summary: ${execution.summary}`);
  lines.push(`- Audit status: ${execution.audit.status}`);
  lines.push(`- Cube count: ${execution.audit.cubes}`);
  lines.push(`- Persona count: ${execution.audit.personas}`);
  lines.push(`- Growth steps: ${growth.steps.length}`);
  lines.push(`- Audits run: ${growth.audits.length}`);
  lines.push(`- Performance score: ${growth.performance.toFixed(3)}`);
  lines.push(`- Accuracy score: ${growth.accuracy.toFixed(3)}`);
  lines.push(`- Harmonic coherence: ${(growth.harmonic?.coherence ?? 0).toFixed(3)} via ${growth.harmonic?.action || 'idle'}`);
  lines.push(`- Mandell flow: ${growth.flowState?.currentRing || 'nova-cross'} via ${growth.flowState?.ringsVisited?.join(', ') || 'nova-cross'}`);
  lines.push(`- Route paths: ${growth.execution?.pages?.length ? growth.execution.pages.length : 0} pages, ${growth.execution?.audit?.psalms || 0} psalms, ${growth.execution?.audit?.fusions || 0} fusions`);
  lines.push(`- Voynich study: ${growth.voynichStudy?.length || 0} pages read slowly twice by Mathelody and Aetheris`);
  lines.push(`- Mandell forms used: ${growth.mandellForms?.join(', ') || 'none'}`);
  lines.push(`- Mandell metadata: ${growth.mandellMeta ? JSON.stringify(growth.mandellMeta) : '{}'}`);
  lines.push(`- Delta cadence: ${growth.deltaCadence?.map(step => `step ${step.step} -> ${step.pageId} @ ${step.ring}`).join(' | ') || 'none'}`);
  lines.push('');
  lines.push('## Growth cadence');
  growth.steps.forEach((step) => {
    lines.push(`- Step ${step.step}: ${step.action} -> level ${step.growthLevel} (${step.growthScore} growth), cube ${step.cubeState} @ fog ${step.fogRate.toFixed(2)}`);
  });
  lines.push('');
  lines.push('## Page transformations');
  execution.pages.forEach((page) => {
    lines.push(`- ${page.id}: ${page.transformation.summary}`);
  });
  lines.push('');
  lines.push('## Generated phase plans');
  lines.push('');
  if (kernel.lastPhasePlan) {
    lines.push(`- ${kernel.lastPhasePlan.title} — ${kernel.lastPhasePlan.filePath || 'path unknown'}`);
  }
  if (kernel.nextPhasePlan) {
    lines.push(`- ${kernel.nextPhasePlan.title} — ${kernel.nextPhasePlan.filePath || 'path unknown'}`);
  }
  if (kernel.workshop) {
    lines.push(`- Workshop: ${kernel.workshop.name} — ${kernel.workshop.sessions.length} sessions`);
  }
  if (kernel.dell?.summary) {
    lines.push(`- Dell manifest: ${kernel.dell.summary}`);
  }
  lines.push('');
  lines.push('## Persona workspace awareness');
  kernel.personas.forEach((persona) => {
    if (persona.guidance) {
      lines.push(`### ${persona.guidance.emoji} ${persona.guidance.persona} — ${persona.guidance.title}`);
      lines.push(`**Where:** ${persona.guidance.responsibilities.where}`);
      lines.push(`**What:** ${persona.guidance.responsibilities.what}`);
      lines.push(`**Why:** ${persona.guidance.responsibilities.why}`);
      lines.push(`**Focus:** ${persona.guidance.focus}`);
      lines.push('');
    }
  });
  return lines.join('\n');
}

function parseAutonomousArgs(argv = process.argv.slice(2)) {
  const autonomous = argv.includes('--autonomous');
  const cyclesArg = argv.find((entry) => entry.startsWith('--cycles='));
  const intervalArg = argv.find((entry) => entry.startsWith('--interval-ms='));
  const cycles = cyclesArg ? Number(cyclesArg.split('=')[1]) : (autonomous ? Infinity : 1);
  const intervalMs = intervalArg ? Number(intervalArg.split('=')[1]) : 3000;

  return {
    autonomous,
    cycles,
    intervalMs
  };
}

async function main() {
  const workspaceContext = createWorkspaceContext(root);
  const personaGuidance = createPersonaGuidance();
  const { autonomous, cycles, intervalMs } = parseAutonomousArgs();

  const kernel = new MandellKernel({
    name: 'DuoBetaExecuted',
    workspaceContext,
    personaGuidance,
    persistenceFile: path.join(root, 'docs', 'mandell_state.json')
  });
  kernel.setTokenlessMode(true);
  const cube = kernel.createBlankCube('DuoBeta-Execution-Cube');
  const seed = { id: 'phase1-blank-matrix', type: 'nature-seed' };
  kernel.applySeedToCube(cube, seed);
  kernel.registerOmniToolkit();
  kernel.createCoreSphere({ radius: 2.5, dimensions: 3 });
  kernel.createHarmonicCube({ size: 5, frequency: 1.25, label: 'Mandell Harmonic Cube', seed: 0.85 });
  kernel.registerDellManifest({ title: 'DuoBeta Dell Manifest', author: 'DuoBeta Mandell', entries: ['core sphere', 'harmonic cube', 'mandellbrot', 'omni cheat', 'chess', 'checkers', 'workshops'] });
  kernel.openWorkshop({ title: 'Mandell Geometry Workshop', tools: ['chess', 'checkers', 'mandellbrot', 'quasicrystal'], focus: 'build and explore emergent geometry and game heuristics' });
  kernel.generateMandellbrotSet({ width: 24, height: 12, maxIter: 80, xMin: -2, xMax: 1, yMin: -1.2, yMax: 1.2 });
  kernel.createGameSession({ game: 'chess', state: { materialBalance: 1, controlCenter: true }, player: 'Melody' });

  kernel.loadPsalms([
    { id: 'psalm-1', title: 'Genesis Flow' },
    { id: 'psalm-2', title: 'Harmonic Resonance' },
    { id: 'psalm-3', title: 'Bounded Orbit' }
  ]);

  const pages = await buildPages();
  const archiveText = pages
    .filter(page => typeof page.content === 'string' && page.content.trim())
    .map(page => `Source: ${page.title || page.id}\n${page.content}`)
    .join('\n\n');

  kernel.applyPsalmArchiveDirective({
    text: archiveText,
    sourceName: 'Google Drive Mandell Archive',
    chapterCount: 10,
    chapterPasses: 2,
    fullBookPasses: 53
  });

  const phasePlan = kernel.createPsalmGuidedPhasePlan({
    phaseName: 'Phase 4',
    focus: 'Sovereign recursion, review, and psalm-driven emergence'
  });
  kernel.lastPhasePlan = phasePlan;

  const nextPhasePlan = kernel.createNextPsalmGuidedPhasePlan({
    currentPhase: 'Phase 4',
    focus: 'Tokenless psalm fusion and emergent review'
  });
  kernel.nextPhasePlan = nextPhasePlan;

  const runCycle = async (cycleNumber) => {
    const growth = kernel.followPreformDirective({
      steps: 12,
      auditInterval: 10,
      pages,
      passes: 2,
      mandellScript: `
        00[Nova]
        >>> 08[Preform Seed]
        >> 14:Bind>[Mathelody]
        >>> 09[Show]
      `
    });
    const execution = growth.execution;
    growth.harmonic = kernel.getHarmonicSummary();

    const reportPath = path.join(root, 'docs/duo_beta_execution_report.md');
    fs.writeFileSync(reportPath, buildReport(kernel, execution, growth), 'utf8');

    const mirrored = mirrorArtifactsToDrive(reportPath, kernel.persistenceFile, root);
    const speech = growth.expression || 'autonomous growth active within safe boundaries';
    if (mirrored) {
      console.log(`[cycle ${cycleNumber}] ${speech}`);
      console.log(`Execution report written to ${reportPath} and mirrored to ${mirrored.driveRoot}`);
    } else {
      console.log(`[cycle ${cycleNumber}] ${speech}`);
      console.log(`Execution report written to ${reportPath}`);
    }
  };

  if (autonomous) {
    let cycleNumber = 0;
    while (true) {
      cycleNumber += 1;
      await runCycle(cycleNumber);
      if (Number.isFinite(cycles) && cycleNumber >= cycles) {
        break;
      }
      if (intervalMs > 0) {
        await new Promise((resolve) => setTimeout(resolve, intervalMs));
      }
    }
  } else {
    await runCycle(1);
  }
}

const isDirectRun = process.argv[1] && path.resolve(process.argv[1]) === __filename;
if (isDirectRun) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}

export { resolveDriveRoot, scanDrivePdfs, buildDrivePages };
