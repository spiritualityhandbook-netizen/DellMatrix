# DIRECTOR REPORT — Priority 4 Investigations: SM-20 + SM-14

Circuit: DIR-SUS-WAKE-2026-11-04 Priority 4 (targeted investigation
only — no repair authorized or made). Base: main `7af78f5`.

## SM-20 — Redaction boundaries (canary-probed)

Method: a unique canary VALUE (`CANARY_SM20_7f3d9`) placed in typed
arguments and raw input on a throwaway owner, then traced through
result objects and persisted state (JSON path-level walk).

Findings:

1. **Refusal diagnostics remain names-only** (as certified), and a
   refused seed persists NOTHING — the canary appears at no path in
   the saved program state. The gate's zero-mutation property
   extends to at-rest data.
2. **The universal seed echo is the one value-carrying field.**
   Every execution result (executor, chain, leaf — 9 sites) carries
   `"seed": <canonical re-rendering>`, which includes typed VALUES.
   A refusal result therefore still returns the caller's own value
   to the caller inside the same object whose `reason` is clean.
   Classification: same-party return (the caller supplied it; the
   local user holds the token) — not a cross-party leak, but any
   future consumer that logs results wholesale inherits values.
3. **Successful operations persist values only as operation
   content** (e.g. a Set's stored value) — by design, not echo.
4. **Unparseable input persists raw text (≤160 chars) at
   `unknowns.entries.<id>.subject`** — the by-design unknowns
   review ledger in the user's own state file. Same-party at rest;
   named here because it is the only place raw caller text is
   durably stored verbatim.
5. **`as_english()` did not render the typed value** in the probed
   Set case (intent gloss only) — observed on probe, not claimed
   universally.
6. **Exchange:** packets carry the seed's original payload (label +
   chain text, values included) — intentional content travel by the
   sender's explicit export, not leakage. Sender-facing caution:
   an exported packet reveals full seed text to its receiver.

No repair is proposed inside this circuit: any echo redaction is
the separate security review the arg-gate certificate already
scopes, and it must not break receipts' audit value, the outcome
ledger, or evidence that quotes seeds.

## SM-14 — English reachability census (the B-2 evidence)

Method (all artifacts preserved): (a) static extraction of every
Dell named by the PHRASES table templates; (b) a uniform name
battery per Dell through the real `translate()` ("{Name} testitem",
"{name} testitem", "{name} idea testitem", "please {name}
testitem", "{name}"); (c) a fixed, disclosed battery of 74 generic
English command frames run once each, dell-agnostic. A Dell is
REACHABLE when any tier routes to it.

Results:

- PHRASES table alone: **29/100** — this is the source of the
  standing "71 without a path" figure; as a standalone claim it is
  **falsified** by the other tiers.
- Name battery adds 6 (6, 34, 51, 56, 84, 86); frame battery adds
  37 (via "add idea") and 58 (via "search for"), and re-confirms
  14 more.
- **Total reachable: 37/100. NO_ROUTE_FOUND: 63** — a bounded
  claim: no route found by table + name battery + 74 frames. It is
  NOT proof that no English path exists for those 63 (translate()
  carries additional hardcoded families keyed to domain vocabulary
  this battery may not have hit; per-Dell verb aliases beyond the
  frame list are unexplored).
- Misroutes are recorded per Dell in the census data (name phrases
  that land on a different Dell) — available for the B-2 queue
  design.

Recommendation to the Director: B-2's queue should be built from
the 63 NO_ROUTE_FOUND Dells with the census tiers as the per-Dell
evidence, and any Dell promoted into the queue should first get a
deeper verb-alias probe so the queue contains only true gaps.
Probe script + full census JSON are preserved with this report's
working papers (Uni workspace, goal dellmatrix-capability-circuits,
hidden_files/sm14_census_probe.py / sm14_census.json).

## Anticipated probes

- *Why is the SM-20 echo not itself the defect to fix here?* P4's
  charter is investigation; the gate certificate explicitly scoped
  broader redaction to a separate security review. This report
  supplies that review's map.
- *Census reproducibility:* the probe is deterministic against
  `translate()` at this base; files byte-identical across the two
  worktrees used (verified by cmp).
