# 72-06 — DATED CURRENT-MAIN DELTA (2026-11-20)

Per Director disposition 7040506653 on PR #308. This delta is a SEPARATE
dated appendix. Every historical artifact of the 2026-11-05 census
(q06_probe.py, q06_repl_probe.py, their run logs, ENUMERATION.md,
MANIFEST.sha256) is preserved byte-for-byte and verified by hash; the
historical outcomes below are labeled HISTORICAL and are no longer
current product behavior.

## Pins

- Historical census: 2026-11-05, Director Mode A authorizations
  (18:41 / 19:26 CST). The census report does not record an exact
  product SHA; the historical pin SHA is therefore UNKNOWN and is not
  invented here.
- Branch base before this amendment: main `8f733b2e51b45d4f88fb6e36fd1945942d091ebe`
  (PR head `bc0b7ee2ac0548efd82dd00afffef9f091ba02f3`).
- Current main at measurement: `af2519b6d239ef278397e277210d6da2467c36e5`
  (after PR #500 merge). The branch was rebased losslessly onto it;
  product code under `form/` is identical between the two mains for
  every path probed here (the intervening commits touch only the MWL
  register, the Keeper watermark, and the #500 settlement records).

## Why the old oracle went red

verify-72-06 run 44741502041 at bc0b7ee read 16/21: the historical
probe passes a check only when the 2026-11-05 claim reproduces
exactly. Uni reproduced 16/21 locally (7040381868) and again this
cycle; the same five checks differ. Each is classified below from
first-hand measurement at BOTH the census path
(translate -> route_intent, PUBLIC_ENTRY_PATH) and the bare REPL
(python3 -m form.repl, cross-process, REAL_USER_PATH).

## The five changed claims

### E19 — 'cycle three times' (Class E word-count)
- HISTORICAL (2026-11-05): spelled-out count silently defaulted to 1;
  executed `06[Cycle] :: 1` with ok=True.
- CURRENT: args count=3, seed `06[Cycle] :: 3`, ok=True; REPL prints
  `Cycle x3`, RESULT ok=True.
- CLASSIFICATION: **ALREADY_FIXED**.

### E20 — 'grow three' (Class E word-count)
- HISTORICAL: cycles defaulted to 1; `Loop: requested 1, executed 1`.
- CURRENT: args cycles=3, seed `13[Loop] :: 3`; REPL prints
  `Loop: requested 3, executed 3`, RESULT ok=True.
- CLASSIFICATION: **ALREADY_FIXED**.

### A5 — 'cycle 9' producer clamp
- HISTORICAL: translate clamped 9 -> 5 inside args itself
  (seed `06[Cycle] :: 5`).
- CURRENT: producer preserves count=9 (args + seed `06[Cycle] :: 9`).
  The bound now lives at EXECUTION and is reported truthfully:
  REPL 'grow 9' prints `Loop: requested 9, executed 5. (clamped to
  1..5)` with ok=True; REPL 'cycle 9' prints `Cycle x5` — the output
  claims only the executed count, never the requested 9.
- CLASSIFICATION: **INTENTIONAL_GUARD** (silent producer transform
  removed per the explicit-bounds doctrine; execution bound enforced
  and stated, requested-vs-executed semantics truthful).

### D17 — 'zoom tokyo' dead arg
- HISTORICAL: args produced `ref='tokyo'`, absent from the mandel,
  consumed nowhere; REPL served the operand only by raw-line re-parse.
- CURRENT: translate produces NO args ({}); route_intent refuses
  explicitly — routed=False, ok=False, empty seed, error
  "no verified correspondence for ('zoom', Dell 15) — refusing to
  guess". REPL handler refuses in the open: `Could not zoom: not
  found: tokyo`. Refusal mutates no owner state (idea-count snapshot
  unchanged in the probe).
- CLASSIFICATION: **INTENTIONAL_GUARD** (dead-arg production gone;
  fail-closed refusal replaces it).

### D18 — 'weather rain' dead arg
- HISTORICAL: args produced `condition='rain'`, absent from the
  mandel, consumed nowhere.
- CURRENT: translate produces NO args ({}); route_intent refuses
  explicitly — routed=False, ok=False, error "no verified
  correspondence for ('weather', Dell 25) — refusing to guess".
  The REPL direct handler still serves the raw line in the open,
  printing `Weather → rain` (a display echo; no RESULT line, no
  executed chain, no state claim).
- CLASSIFICATION: **INTENTIONAL_GUARD** (dead-arg production gone;
  router fail-closed; REPL echo is a direct handler, not an arg
  consumer).

No LIVE_DEFECT and no NEW_LIMIT was found among the five at the
paths probed. The remaining 16 census checks reproduce exactly as
censused (verified by the preserved probe's local 16/21 run).

## New current-contract oracle

- `q06_current_probe.py` — programmatic current contract, 7/7
  (E19, E20, A5, D17, D18 + digit controls; refusal nonmutation
  asserted). Logs: q06_current_run1.log / q06_current_run2.log
  (identical hashes — deterministic at this path).
- `q06_current_repl_probe.py` — bare-REPL current contract, 8/8
  (W1, W2, C1, C2, G9, C9, Z1, WX; fresh owner per case, probe
  removes its own owner state afterwards). Logs:
  q06_current_repl_run1.log / q06_current_repl_run2.log.
- `CURRENT_MANIFEST.sha256` — hashes of the six new files. The
  historical MANIFEST.sha256 is untouched and still verifies.

## Workflow change (verify-72-06.yml)

The workflow no longer executes the historical probes against the
live product. It now (a) verifies the preserved historical artifact
hashes via MANIFEST.sha256 plus the new files via
CURRENT_MANIFEST.sha256, WITHOUT reasserting the old semantics, and
(b) executes the two NEW current-contract probes at the exact head.
No assertion was skipped or weakened to force green: the historical
checks that changed are replaced by current-contract checks that pin
the measured current behavior, and the historical record stands
unchanged beside them.

## Credit note

Records/investigation only. This modernization invents no repair and
claims no CODE or MWL credit. If a real-user count defect had
remained, it would have been filed as a separate failing-first CODE
circuit; none remains at the probed paths.
