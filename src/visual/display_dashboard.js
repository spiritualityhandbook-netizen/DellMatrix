import { MandellKernel } from '../mandell_kernel.js';
import { createWorkspaceContext } from '../core/workspace_context.js';
import { createPersonaGuidance } from '../core/persona_guidance.js';
import { createVisualDashboard } from './dashboard.js';

function main() {
  const workspaceContext = createWorkspaceContext();
  const personaGuidance = createPersonaGuidance();

  const kernel = new MandellKernel({
    name: 'DellMatrixVisual',
    workspaceContext,
    personaGuidance
  });

  kernel.registerDefaultPersonas();
  kernel.createMathelodyPersona({ psalms: kernel.psalms });
  kernel.createBlankCube('Visual-Demonstration-Cube');
  kernel.createFusionMode('duo', ['Manny', 'Melody']);
  kernel.createFusionMode('trio', ['Manny', 'Melody', 'Aetheris']);

  const dashboard = createVisualDashboard(kernel);

  console.clear();
  console.log(dashboard.render());
  console.log('\n═══ INTERACTIVE VIEWS ═══\n');
  console.log('Available modes: overview, cube, roster, sanctuary\n');

  dashboard.setMode('roster');
  console.log(dashboard.render());
}

main();
