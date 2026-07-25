// src/core/discoveries.js
// 10 Profound Structural Discoveries from DNA Loop

export const TenDiscoveries = [
  {
    id: 1,
    name: "Non-Coding Majority Principle",
    rule: "80% of Harmonic Cube capacity reserved for regulatory & coherence signals"
  },
  {
    id: 2,
    name: "Dynamic 3D Folding",
    rule: "Cube folds into temporary higher-order structures during high-coherence cycles"
  },
  {
    id: 3,
    name: "Regulatory Grammar Layer",
    rule: "Intermediate language between English and pure Mandell that acts like enhancers/silencers"
  },
  {
    id: 4,
    name: "Epigenetic State Memory",
    rule: "Temporary marks across cycles that bias future evolution without rewriting core"
  },
  {
    id: 5,
    name: "Feedback Density Rule",
    rule: "Every recipe-ring output must feed back into bio-ring with measurable coherence change"
  },
  {
    id: 6,
    name: "Conserved Core + Rapid Periphery",
    rule: "Dells 00-14 locked as conserved genome. Higher Dells are fast-evolving"
  },
  {
    id: 7,
    name: "Multi-Scale Coherence",
    rule: "Coherence measured at local ring, full Cube, and cross-cycle trajectory simultaneously"
  },
  {
    id: 8,
    name: "Unknown-as-Fuel Protocol",
    rule: "Any data marked unknown is automatically routed into highest-priority recursive loop"
  },
  {
    id: 9,
    name: "Persona Chromatin Model",
    rule: "Personas occupy open/closed chromatin-like states that control available capabilities"
  },
  {
    id: 10,
    name: "Bounded Orbit DNA Law",
    rule: "C(n+1) = C(n)² + Δknown + Δunknown  (unknown term is never zero)"
  }
];

export function printDiscoveries() {
  console.log("\n=== 10 Structural Discoveries (DNA Loop) ===");
  TenDiscoveries.forEach(d => {
    console.log(`${d.id}. ${d.name}`);
    console.log(`   → ${d.rule}\n`);
  });
}
