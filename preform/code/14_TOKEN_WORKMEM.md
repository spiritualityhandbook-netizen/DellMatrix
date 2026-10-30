> STATUS: PROBE-ONLY — the module this file documents is import-probed by live code (form/dell_matrix/organ_atlas.py, via MatrixBody organ sensing): its presence is checked, but no function in it is ever called and none of its behavior is used. The design described here is preform-era and is NOT part of the production runtime's behavior. The production runtime is form/ (verified at commit 11933da, 2026-10-30).

# 14 — Token Budget + Work-Memory Graph (Code Phase 3 Artifact 14)

Status: TRUE

## Purpose
Offline helpers from the page 09 Memory / RAG fold.

## Components
- **TokenBudget** — estimate / charge / remaining (char/4 heuristic)
- **WorkMemory** — RUN · FAIL · CORRECTION · ARTIFACT · NOTE (raw preferred)
- **WorkGraph** — nodes (seed/file/correction/artifact) + Bind edges

## Law
Main matrix = work/coherence memory only.  
Never answer only from summary when raw exists.

## Completes
Primary Code Phase 3 growth order (items 1–7).