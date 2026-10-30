> STATUS: PROBE-ONLY — the module this file documents is import-probed by live code (form/dell_matrix/organ_atlas.py, via MatrixBody organ sensing): its presence is checked, but no function in it is ever called and none of its behavior is used. The design described here is preform-era and is NOT part of the production runtime's behavior. The production runtime is form/ (verified at commit 11933da, 2026-10-30).

# 13 — Thinks Thread (Code Phase 3 Artifact 13)

Status: TRUE

## Purpose
Async cognitive layer that obeys the page 09 law:

> Body first. Thinks second. Thinks always reads real body state.

## Contract
- `observe(avatar)` — mandatory refresh of BodySnapshot before thinking
- `think(content, intent?, **payload)` — may emit a high-level Intent
- `next_intent()` — body executor pulls intents
- Thinks never mutates body directly
- `try_execute` is the only body-side bridge

## Intents
IDLE · MOVE · TURN · PICK · PLACE · STOW · DRAW · SET_REACH · EXPRESS · NOTE

## Growth
- Ready to plug into ReachInventory and ASCII Animation for richer intents
- GodWorkSpace can display `thinks.status()` and recent notes