/**
 * 25 Master Dell Functions + 4 Dimensional Flows
 * From Mandel_OS v12 unified codex — structural operators only
 */

export const FLOWS = {
  primary:    { id: 'primary',    symbol: '↘', meaning: 'Default execution path' },
  negative:   { id: 'negative',   symbol: '↙', meaning: 'Mirror / counter-logic / adversarial test' },
  complex:    { id: 'complex',    symbol: '↗', meaning: 'Scope elevation / metadata' },
  retrograde: { id: 'retrograde', symbol: '↖', meaning: 'Recursion / error-correction / reverse walk' }
};

export const DELL_FUNCTIONS = {
  '00': { name: 'Nova',      meaning: 'Initialize / reset origin' },
  '01': { name: 'Solo',      meaning: 'Single-agent focus' },
  '02': { name: 'Duo',       meaning: 'Two-agent pairing' },
  '03': { name: 'Tree',      meaning: 'Trinity / three-agent bind' },
  '04': { name: 'Change',    meaning: 'Transform state' },
  '05': { name: 'Describe',  meaning: 'Inspect / describe' },
  '06': { name: 'Ask',       meaning: 'Query' },
  '07': { name: 'Negate',    meaning: 'Invert / oppose' },
  '08': { name: 'Create',    meaning: 'Manifest new node / seed' },
  '09': { name: 'Show',      meaning: 'Reveal / render' },
  '10': { name: 'Keep',      meaning: 'Persist / hold' },
  '11': { name: 'Switch',    meaning: 'Change center / lens / persona' },
  '12': { name: 'Test',      meaning: 'Validate / check' },
  '13': { name: 'Loop',      meaning: 'Recurse / cycle' },
  '14': { name: 'Bind',      meaning: 'Connect / vesica / link' },
  '15': { name: 'Guard',     meaning: 'Constraint / protect' },
  '16': { name: 'Merge',     meaning: 'Fuse / sum / combine' },
  '17': { name: 'Split',     meaning: 'Separate / branch' },
  '18': { name: 'Rank',      meaning: 'Order / priority' },
  '19': { name: 'Sense',     meaning: 'Feel / intensity' },
  '20': { name: 'Void',      meaning: 'Clear / empty slot' },
  '21': { name: 'Route',     meaning: 'Path / direction' },
  '22': { name: 'Cast',      meaning: 'Project / emit form' },
  '23': { name: 'Seal',      meaning: 'Lock state' },
  '24': { name: 'Emit',      meaning: 'Output signal' },
  '25': { name: 'Catch',     meaning: 'Receive / capture' }
};

export function getDell(code) {
  const key = String(code).padStart(2, '0');
  return DELL_FUNCTIONS[key] || null;
}

export function listDellFunctions() {
  return Object.entries(DELL_FUNCTIONS).map(([code, v]) => ({ code, ...v }));
}

export function listFlows() {
  return Object.values(FLOWS);
}
