import fs from 'node:fs';
import path from 'node:path';

export class WorkspaceContext {
  constructor(rootDir = process.cwd()) {
    this.rootDir = rootDir;
    this.manifest = this.loadManifest();
    this.files = this.indexFiles();
    this.zones = this.defineZones();
  }

  loadManifest() {
    const manifestPath = path.join(this.rootDir, 'workspace_manifest.json');
    if (fs.existsSync(manifestPath)) {
      return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    }
    return { projectName: 'DellMatrix', modules: [] };
  }

  indexFiles() {
    const files = {};
    const recurse = (dir) => {
      if (!fs.existsSync(dir)) return;
      const entries = fs.readdirSync(dir);
      entries.forEach((entry) => {
        if (entry.startsWith('.') || entry === 'node_modules') return;
        const fullPath = path.join(dir, entry);
        try {
          const stat = fs.statSync(fullPath);
          if (stat.isDirectory()) recurse(fullPath);
          else files[path.relative(this.rootDir, fullPath)] = { path: path.relative(this.rootDir, fullPath), type: 'file' };
        } catch (err) {}
      });
    };
    recurse(this.rootDir);
    return files;
  }

  defineZones() {
    return {
      runtime: { path: 'src', description: 'Core runtime and execution' },
      core: { path: 'src/core', description: 'Core infrastructure layer' },
      visual: { path: 'src/visual', description: 'Visual and UI layer' },
      docs: { path: 'docs', description: 'Documentation and preform materials' },
      tests: { path: 'tests', description: 'Test suite' }
    };
  }

  getZone(filepath) {
    const normalized = filepath.replace(/\\/g, '/');
    for (const [zoneName, zone] of Object.entries(this.zones)) {
      if (normalized.startsWith(zone.path)) return { name: zoneName, ...zone };
    }
    return null;
  }
}

export function createWorkspaceContext(rootDir) {
  return new WorkspaceContext(rootDir);
}
