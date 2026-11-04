# DIRECTOR REPORT — CORE-I-UNSUPPORTED-ARG-GATE

Circuit: CORE-I-UNSUPPORTED-ARG-GATE (Director Mode C — REPAIR,
Core I contract ruling on PR #256, 2026-11-03)
Status: **SUBMITTED** — implementation PR held UNMERGED for
Director certification.
Base: db61de0a1a1391c83237a0fab016d814f0c10af0 (main; PRs #255
and #256 merged)
Code head: 74d077e408141254614b26433d68dceaa0e0317a

## 1. What was built

The Core I counterpart of the certified Core II gate (PR #253):
typed arguments on an **unregistered Core I Dell now refuse
explicitly** instead of being silently ignored, under the
Director's per-atom correction.

The refusal lives at the canonical funnel,
`form/mandell/executor.py::execute_seed`, as a single guard
inserted after seed parsing and **before every dispatch**
(core_i_ops intercept, live_identity, leaf). The guard fires
only when ALL of the following hold for the seed being executed:

- the parsed seed is a **single atom** — the only shape this
  entry point ever dispatches itself;
- that atom's Dell is in Core I range (0–50);
- the atom carries nonempty parsed `args`;
- the Dell has **no registered typed signature**.

Refusal result: `ok=False`,
`error = "UNSUPPORTED_ARGS: <sorted role names>"`, and a TOAM
message mirroring the certified Core II wording ("Dell
NN[Term] has no registered typed signature; typed arguments
refused before execution (roles: …)"). Echo header lines are
built from `redacted_seed`, matching leaf disclosure discipline.

**Why this is per-atom and can never reject a whole chain:**
multi-atom seeds are never judged at the funnel — they route
to chain_exec, which re-enters `execute_seed(..., _leaf=True)`
once per Core I atom with that atom's own args re-emitted
(AF-1's established transport). Each executing atom is judged
on its own args at its own execution. The Director's
adversarial example executes fully (suite §3, check 1):

```
03[Logic] > 55[Set](key="tempo", value="120")   → ok, store tempo=120
```

One validation authority; no second gate in chain_exec, the
leaf, or core_i_ops. Typed-signature count stays **17**; no
signatures were added; no parser changes; no Core II changes;
`translate.py`'s English Intent.args channel untouched.

## 2. Contract points, as executed

1. **Failing-first tests for all 50 unregistered Core I Dells**
   across single-atom, chained, intercept, and live-identity
   paths — new suite `form/core_i_arg_gate_test.py` (92 checks),
   registered in `form/regress.py`. On the pristine base the
   final suite scores **21/92**: every refusal check red, every
   preservation check green. After the fix: **92/92**.
2. **Per-atom refusal before mutation** — the sweep asserts a
   business-state snapshot identical before/after for each of
   the 50 Dells, plus the intercept and live-identity sets.
3. **Preserved:** Dell 8's registered contract (valid wiring,
   INVALID_VALUE, UNKNOWN_ROLE, ARGUMENT_CONFLICT — never
   reclassified as UNSUPPORTED_ARGS), all valid Core II typed
   calls, and legitimate label-only execution (including
   `06[Cycle] :: 3` still running ×3, and arg-shaped text inside
   a label staying a label).
4. **Role names only** — canary checks on a leaf Dell, an
   intercept Dell, and 41[Sanitize]: the refusal's own
   diagnostics (error, receipts, appended messages) name the
   role and never the planted value. Mutant M5 (values echoed)
   disclosed the canary in all three and scored 22/92.
5. **Flow/skip behavior preserved:** FlowTo continuation after
   a refusal; the FlowThru fence (a Core I atom with args
   behind a `>>` block receipts `flow_thru_block` skipped —
   its args are never inspected, per the Q4 law); reserved
   atoms (151) unchanged on both paths; ManifestSet (•)
   members each refuse per-atom with the expansion mechanism
   intact, and arg-free members execute as on base.
6. **AF-1 check 7 amended under the ruling:** refusal parity
   replaces silent-success parity (single refusal == chain
   receipt refusal, partner atom still executes). The AF-1
   header keeps its historical contract text and gains a
   dated amendment note citing this ruling. AF-1 suite:
   **13/13** (and it catches the _leaf-gap mutant, §4).
7. **Count stays 17** — asserted live from the signature
   registry inside the suite's scope checks.
8. **Zero mutation + honest receipts** — snapshot-verified in
   the sweep, intercept, live, and ManifestSet sections; chain
   receipts carry the refusal error class per atom.

## 3. The mixed-chain adversarial set (required)

- Director's example (above): full execution, Set effect
  stands, no UNSUPPORTED_ARGS anywhere in the result.
- Typed Core II first, Core I with args second: the Set effect
  stands; Tone refuses on its own args.
- Core I with args sandwiched between two valid Core II atoms:
  both Core II effects stand; the middle atom refuses per-atom.
- Chain parity sample across all four execution families
  (leaf 43, intercept 37, live 21, plain 05): chained receipt
  error is byte-identical to the single-atom refusal.

## 4. Mutants (all killed, inverse-reverted, diff verified empty)

| Mutant | Defect restored | Result |
|---|---|---|
| M1 | Gate keyed on primary Dell + any atom's args (whole-chain rejection — the Director's catch) | 86/92; his example red, parity ×4 red |
| M2 | Gate dropped on the `_leaf` re-entry path | 85/92; parity red; AF-1 12/13 |
| M3 | Gate relocated below the intercept dispatch | 74/92; exactly the 8 intercept Dells bypass |
| M4 | `has_signature` condition dropped (Dell 8 refuses) | 86/92; AF-1 4/13 |
| M5 | Refusal error echoes raw values | 22/92; canary disclosed in all 3 canary checks |

## 5. Regression and verification

- New suite: 21/92 (base) → **92/92** (fixed). AF-1 13/13.
  Core II gate suite 45/45 (certified code untouched).
- Full regression, candidate tree, sequential, isolated
  worktree state: **227/227 GREEN forward, 227/227 GREEN
  --twice (both passes), 227/227 GREEN --order rev**. (227 =
  226 + the new suite.) No daf09 anomaly appeared in any leg;
  no differential was needed.
- Fresh clone at the PR code head (74d077e, cloned from
  GitHub): **227/227 GREEN, exit 0** (fresh_clone.log).
- Exact-head CI (direct gh query, separate step): verified
  for the final submission head in the verification addendum
  below.
- Evidence bundle: `director-reports/evidence/core-i-arg-gate/`
  with `MANIFEST.sha256` (no self-hash entry; `sha256sum -c`
  verified from the committed tree).

## 6. Deviations and notes

- One suite assertion was corrected in-flight: the first REPL
  check required the literal string `UNSUPPORTED_ARGS` in the
  REPL output; the REPL prints the gate's TOAM refusal *line*
  (as it does for the certified Core II gate), not the
  error-class field. The check now asserts the printed refusal
  lines for both probed Dells. Re-verified failing-first: the
  final suite scores 21/92 on pristine base with the corrected
  assertion (the refusal lines are absent there).
- Dell 37's invisible REPL error message was NOT touched
  (separate hygiene item, already in the findings register).
- The gate adds one behavioral surface worth naming: any
  internal caller that constructs single-atom Core I seeds
  with typed args now receives a refusal instead of silent
  execution. The full regression (227 suites) is green, and
  PR #256 verified the English translator emits typed args
  only onto registered Dells; no internal breakage was found.

## Anticipated probes

- *"Does the gate fire for a single Core II atom at the
  funnel?"* No — the range fence (0–50) excludes it; Core II
  singles route to chain_exec's certified gate. The Core II
  suite (45/45) runs unchanged in regression.
- *"What about a Core I atom with args as a control-head body
  member?"* Control bodies execute through execute_range →
  _run_atom → the same _leaf re-entry, so the atom refuses
  per-atom with ordinary failure receipts; frame semantics
  are chain_exec's, unchanged. (No Core I control heads exist
  in 60–66; heads are Core II.)
- *"Chainlink (2v2) mixed pairs?"* Each proto atom's args ride
  its own member atoms; members re-enter singly. The
  ManifestSet section covers the same-Dell expansion; AF-1
  checks 3–5 cover typed chainlink members (Dell 8 + Core II)
  and remain green.
- *"Studio?"* gui_api rides execute_seed; a Studio user typing
  Core I args now sees an honest refusal receipt instead of a
  fake success — the intended contract, visible in the 26/26
  gui_api suite staying green (it uses no unregistered Core I
  args).

## Questions for the Director

1. **Certification scope:** does this circuit certify as the
   Core I counterpart of PR #253's bounded certificate
   (tested execution paths), with the same stated boundaries
   (business-state zero-mutation; names-only governing new
   diagnostics; the preexisting seed echo not a secrecy
   guarantee)?
2. **Q-C3 follow-up:** the English `Intent.args` channel
   review was ruled a separate bounded review — should it be
   sequenced next, or does Track D bridge planning take
   priority now that both argument gates are repaired?
3. **Dell 37 hygiene item:** bundle it with the Q-C3 review
   (both are small Core I honesty repairs), or keep it as its
   own micro-circuit?
