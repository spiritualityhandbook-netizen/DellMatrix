# GDP-001 Phase 0 — Performance Baseline (GDP-V1)

**Branch:** gdp-phase0-work (integrated) · **Date:** 2026-10-03 · **Machine:** Uni VM (linux)
**Purpose:** detect future regressions. Do NOT prematurely optimize against this.

| Metric | Value | Method |
|---|---|---|
| REPL startup (fresh process, `look`) | 0.45 s | wall, 1 run |
| Representative command (`stamp` via translate+route_intent) | 0.014 s | mean of 5, warm |
| save (persist_rest.save, small program) | 0.027 s | wall |
| load (persist_rest.load) | 0.004 s | wall |
| checkpoint commit | 0.134 s | wall |
| rollback | 0.001 s | wall (small generation; R1 measured 0.009–0.014 s on larger) |
| max RSS (loaded program process) | 28.5 MB | ru_maxrss |
| full regress fwd (81 suites) | ~115 s | wall |
| R1 contract micro-bench (200-unit program) | save 0.032–0.040 s, load 0.005–0.027 s, commit 0.135–0.168 s, rollback 0.009–0.014 s | docs/PERSISTENCE_CONTRACT.md |

Future phases compare against this baseline. A >2× regression on any metric without architectural justification is a defect.
