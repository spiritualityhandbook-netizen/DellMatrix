// src/execute_preform.js
// Main entry point - DellMatrix

import { FiveRingSystem } from './core/harmonic_cube_5ring.js';
import { understandEnglish } from './core/english_brain.js';
import { activateDNAProfile } from './core/dna_profile.js';
import { printDiscoveries } from './core/discoveries.js';

console.log("========================================");
console.log("   DellMatrix | Manellody Apex Online");
console.log("========================================\n");

const ringSystem = new FiveRingSystem();

// Activate DNA profile on start
activateDNAProfile(ringSystem);
printDiscoveries();

console.log("\nType plain English commands (or 'help'):\n");

import readline from 'node:readline';
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.on('line', (input) => {
  const result = understandEnglish(input);
  console.log(result.message);

  if (result.command === 'grow' || result.command === 'evolve') {
    const out = ringSystem.process({ type: 'evolution_cycle', source: 'manellody' });
    console.log(`Coherence: ${out.coherence.toFixed(3)}`);
  }
});
