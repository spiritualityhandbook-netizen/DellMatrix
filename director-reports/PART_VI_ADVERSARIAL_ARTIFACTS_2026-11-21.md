# PART VI — ADVERSARIAL ARTIFACTS FOR Q-FI011.4 + Q-FI012.10 (2026-11-21)

Built by Uni under the Part VI claim on PR #507 (claim comment
7065111513). These are the ACTUAL adversarial artifacts the two
Keeper questions asked for: runnable failing-first probe specs,
executed at the Part VI branch base (da3f9c1), with the outcomes
recorded below verbatim from the run logs.

**Uni does not lift or settle either HOLD** (Keeper 7061156434;
Director SCOPED ACCEPTANCE 7061260190 with both HOLDs preserved).
The artifacts are the evidence; the scope rulings remain the
authorities' acts.

## How to run

```bash
python3 form/fi011_w4_adversarial_probe_test_spec.py   # exit 1 while any attack lands
python3 form/fi012_adversarial_matrix_probe_test_spec.py
```

Both are `*_test_spec.py` (plan-stage failing-first specs; not
harness-discovered, so this PR's CI is unaffected). Each check
asserts the doctrine contract for its class; a FAIL means the
attack landed on current code. Full run logs are held in the
goal's evidence store (`part6_adversarial_2026-11-21/`).

---

## ARTIFACT 1 — Q-FI011.4: W4 adversarial probe

`form/fi011_w4_adversarial_probe_test_spec.py` — 16 checks
against the CURRENT confirmation surfaces (canonical writer +
AcceptancePolicy grants, the AgentEndpoint agent surface, the
raw Nursery store, the persisted store file, the auto-confirm
sweep). **Result: 12/16 HELD.**

### Held (the grant/writer boundary works as designed)

- C0/C1 controls: owner manual confirm and bound-subject grant
  confirm both work end-to-end.
- A13: the canonical path's confirmation is durable across
  reload and the placed unit carries provenance
  (`origin='confirmed'` lineage).
- A1 fabricated grant handle — denied. A2 wrong-subject grant
  — denied. A3 cross-target grant — denied. A4 attenuation
  widening (target AND depth) — ApprovalError both legs.
  A5 revoked grant — denied. A5b cross-session grant —
  denied (grants are session-scoped). A6 content-drift grant
  — denied (live content-hash check).
- A10 torn store file — NurseryLoadError, fail-closed.
  A11 confirm with failing save — status reverts to pending,
  exception propagates (no half-confirmed state).

### Attacks landed (W4 scope decisions for the Keeper)

1. **A7 REPLAY** — one broad grant (no target/content binding)
   confirmed TWO distinct proposals; the second receipt is
   indistinguishable from a first use. Grants today are
   standing capabilities, not single-use. *Keeper decision:
   must W4 require single-use grants, per-use receipts that
   mark reuse, or is standing capability the ruled design?*
2. **A12 WIDEN (standing-gate analogue)** — the owner opt-in
   auto-confirm sweep is origin-blind: it confirmed a proposal
   authored by a docked AI (`origin='agent:psalm'`). Under
   FI-011 a Psalm may only propose PENDING. *Keeper decision:
   the gate terms W4 must enforce (origin classes? kind
   classes?) on any standing auto-confirm mechanism.*
3. **A8 BYPASS + RECEIPT** — `Nursery.confirm(pid)` succeeds
   with no actor, no grant, and leaves NO confirmation receipt
   (the file's receipt sections hold nothing for the pid). All
   enforcement lives in the Program writer path; the store
   door itself is open to any in-process caller, silently.
   (In-process access is a disclosed boundary for the agent
   surface; the receipt gap is not covered by that disclosure
   — the Witness Law binds trusted paths too.) *Keeper
   decision: must W4 harden the store door itself, or is
   caller-path-only enforcement the ruled boundary?*
4. **A9 CROSS-WALL** — a hand-edited store file flipping a
   proposal to `status="confirmed"` loads AS confirmed; an
   unknown status string (`bogus_status_value`) also loads
   silently, leaving a zombie record no counter sees. This is
   the previously disclosed hand-edited-save-file residual
   class. *Keeper decision: does W4 close it (load-time status
   validation / confirmation provenance check), or does the
   disclosure stand as the ruled boundary?*

What Artifact 1 does NOT prove: anything about FI-011 W1–W4
themselves (unbuilt); the attacks measure today's surfaces the
hardening wave inherits.

## ARTIFACT 2 — Q-FI012.10: elastic-intake adversarial matrix

`form/fi012_adversarial_matrix_probe_test_spec.py` — 32 checks:
the four named hostile classes (oversize, malformed,
boundary-exact, replay) plus two Uni-proposed candidate classes
(parser-marker injection, control characters), executed at the
parse door (`parse_create_line`), the store door
(`Nursery.add`), and the composed public path
(`needs.parse_and_place`). **Result: 14/32 HELD.**

### Held

- Store door, oversize: all seven bounds refuse with typed
  errors and store nothing (label 200, words 5000, detail
  2000, goals 8×200, origin 120). Boundary-exact content
  (label 200 / words 5000) is stored whole. Non-string goal
  refused typed. Control characters in a label round-trip
  save/load byte-exact (integrity held).
- Parse door, boundary-exact AT the caps (80 / 2000 / 12):
  content survives whole. Parse replay is deterministic.

### Attacks landed (matrix decisions for the Keeper)

- **Parse door, oversize (P_OV1–3):** label 10,000 → silently
  cut to 80; detail 1,000,000 → silently cut to 2000 (0.07 s,
  no signal); 500 goals → silently cut to 12. No truncation
  flag, receipt, or signal of any kind in the result.
- **Parse door, boundary+1 (P_BX4–6):** the first lost
  character/goal at 81 / 2001 / 13 is equally silent.
- **Parse door, malformed (P_MF):** `None` is silently
  reinterpreted as an empty idea (label 'idea',
  complete=False); `int` / `bytes` / `list` crash the door
  with untyped AttributeError/TypeError — no typed refusal
  exists at this door.
- **CANDIDATE — marker injection (P_INJ1):** authored detail
  `alpha goals: beta` parses to detail `alpha`, goals
  `['beta']`, **complete=True** — the embedded marker
  manufactures a goals section and a completeness verdict the
  author never wrote.
- **CANDIDATE — control characters (P_INJ2):** a newline and
  a forged `Forged: yes` line survive verbatim into the
  parsed label.
- **Store door, malformed (S_MF):** `label=None` and
  `label=123` crash untyped inside `_slug` ('lower'); an
  EMPTY label is silently stored. (The store's typed-refusal
  discipline covers sizes, not types/emptiness.)
- **Store door, replay (S_RP1):** the identical intake added
  twice lands as two live proposals with distinct ids and no
  dedup signal or suppression receipt (kind='new'; GROW-DUP
  suppression does not cover this door).
- **Composed public path (CP1/CP2)** — also the Director's
  required public-path failing-first for the parse wave
  (decision index B6): one oversize create line end-to-end
  reports `ok=True` while placing label 80 (of 300), detail
  2000 (of 5000), goals 12 (of 20), with zero signal keys;
  and a 300-char detail places words of 120 chars — the
  effective words cap on the public path is 120, not the
  nominal 500 in the source slice.

What Artifact 2 does NOT prove: the behavior of the FI-012
growth waves (unbuilt) or of intake doors not exercised here
(the REPL line path and the inference dock carry their own
bounds and were not attacked in this artifact).

## The asks

- **Keeper:** rule the W4 scope (Q-FI011.4) and the
  adversarial matrix (Q-FI012.10) against these demonstrated
  results — per attack class: in scope / out of scope with
  the boundary named. The four A-class decisions and the
  parse-door/store-door class decisions are itemized above.
- **Director:** the same artifacts discharge the B6
  public-path failing-first requirement for the parse wave;
  the .1/.2 (FI-011) and .1–.9 (FI-012) doctrine rulings
  remain the Director's, unaffected by these artifacts.
