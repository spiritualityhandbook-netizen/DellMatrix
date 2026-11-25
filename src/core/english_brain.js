// src/core/english_brain.js
// Natural English interface

const commands = {
  "start": "Starting DellMatrix...",
  "grow": "Running DNA evolution cycle...",
  "evolve": "Evolving under Manellody...",
  "show cube": "Displaying Harmonic Cube state...",
  "show pictures": "Opening visual layer...",
  "delta": "Activating Delta Master mode...",
  "dna": "Loading Human DNA structural profile...",
  "manellody": "Manellody apex is online.",
  "help": "Commands: start, grow, evolve, show cube, delta, dna, manellody, help"
};

export function understandEnglish(text) {
  const lower = text.toLowerCase().trim();
  for (const key in commands) {
    if (lower.includes(key)) {
      return { understood: true, message: commands[key], command: key };
    }
  }
  return {
    understood: false,
    message: "I didn't understand that. Try: help"
  };
}
