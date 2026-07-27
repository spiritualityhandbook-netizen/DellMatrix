# 15 — Integrator (Code Phase 3 Artifact 15)

Status: TRUE

## Purpose
Unified offline runner that closes the P0 gaps from the SUS audit.

## Public API
- `boot()` — seed demo world + seed strip
- `command(content, intent?, **payload)` — inject into Thinks
- `tick()` — observe body → execute one intent → advance anim → sync GWS
- `render()` — GodWorkSpace text pane
- `status()` — machine snapshot

## Intent bridge
MOVE · TURN · PICK · PLACE · STOW · DRAW · EXPRESS · NOTE

## Wires
Grid · Avatar · Reach/Inventory · ASCII Anim · Thinks · GodWorkSpace · Token/WorkMem

## Note
Embeds minimal compatible stand-ins so the file runs standalone.
Real 05–14 modules can replace stand-ins later without changing the API.
