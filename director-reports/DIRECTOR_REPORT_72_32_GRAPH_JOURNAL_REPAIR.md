# DIRECTOR REPORT — 72-32 REPAIR: Semantic-Graph Journal Crash Windows vs Derived Program Effects

**Circuit:** 72-32 repair, executed under **Ace's FIX-FIRST
ruling (2026-11-05 19:53 CST)** and Sleep Protocol v2 queue
item 4 (second item of the §6.6 persistence batch). This merge
(when gated) is Ace-authorized, **not** Director-certified.
**Base:** main `bb82da3` (merge of PR #312). **Objective:**
"Validate semantic-graph journals against derived Program
effects (P1/E) (= SM-25)". **Gap closed by this circuit:** the
crash windows between the graph write and the derived-effect
(idea) write, and the multi-hop inter-hop window, named in the
register.

**Also in this PR (per the Director's 2026-11-06 02:44 CST
directive):** the bounded ALL_AI_CONFIRMATION_PASS for the
72-29 checkpoint repair is recorded in the 72-29 register
line, and that ruling is archived verbatim at
`responses/DIRECTOR_REVIEW_EMAIL_2026-11-06_72_29_PASS.md`.
No records-only PR was opened for it.

## Investigation (probes at main bb82da3)

Existing coverage in `form/mandell/p2_dsc1_journal_proof.py`
pins journal INTEGRITY only (embedded-entry validation,
outgoing validation, strict version types, invalid-journal
fail-closed + bytes preserved + valid-control replay) and was
NOT duplicated. Probes (`hidden_files/72-32_probe.py` +
`72-32_probe2.py`, terminal, isolated owners, fresh-process
loads) confirmed the controls HOLD (journal-only crash
converges edge + derived; graph-saved crash converges;
both-committed replay idempotent; mid-batch crash converges
both dependents; corrupt dependent at replay -> explicit
FAILED + status failed; duplicate-seq ensure_edge ->
GraphValidationError with journal bytes preserved). Three
defect classes were CONFIRMED:

- **D1 — a journaled `sync_dependent` whose edge is missing
  at replay is SILENTLY SKIPPED** by
  `_sync_dependent_by_ids`: journal cleared, derived effect
  never applied, `propagation_status` reports
  "synchronized", no FAILED record. A journaled derived
  effect vanishes into a success report — a direct violation
  of the fail-closed-together law (a propagation failure is
  never represented as successful propagation; graph
  relationship + derived effect either both commit or
  neither, or fail-closed recovery converges
  deterministically before state is exposed).
- **D2 — the same replay path UNCONDITIONALLY deletes a
  pre-existing FAILED ledger entry** after the no-op sync:
  an explicit failure is upgraded to "synchronized" with no
  effect applied (probe-verified: status_before failed ->
  after load synchronized, failures []).
- **D3 — multi-hop inter-hop crash window:**
  `_recompute_dependent` commits a hop's derived write
  (`save_idea`, ~line 1847) BEFORE the next hop is journaled
  (`_propagate_property`, ~line 1853). The post-crash state
  (source + hop1 at 100, hop2 stale 42, no journal, no
  ledger) loads as status "synchronized", failures [],
  downstream still 42 — stale-while-synchronized with no
  recovery record.

**GATE classification:** the repairs are local to
`form/mandell/semantic_graph.py` replay/propagation paths.
They do not touch the everyday Program/Nursery pair save
path, Q1 locking, or pair atomicity. => FIX circuit, **T3
evidence tier** (stateful, cross-process). If the Director
rules graph journaling is save-path, the same suite +
grounding convert to the GATE packet unchanged (Q-32R.2).

## Repair (bounded)

- `_sync_dependent_by_ids` now returns whether the sync
  actually applied. `_replay_journal` records an explicit
  FAILED ledger entry for an unapplicable sync instead of
  silently succeeding, and only clears a stale FAILED entry
  on a real success (D1 + D2).
- `_recompute_dependent` journals downstream MIRROR hops
  BEFORE committing the upstream derived write (outside
  replay), and `propagation_status` detects a stale MIRROR
  value (read-only comparison) and returns "failed" instead
  of "synchronized" (D3).
- New suite `form/graph_journal_crash_test.py` (12 checks,
  CROSS_PROCESS) registered in `form/regress.py`
  (LIST 242 -> 243).
- **Suite-contract fix (in-circuit, disclosed):** the suite
  as first committed defined `main()` but no `smoke()` entry
  point, while the regress harness invokes `smoke()`. The
  first regress chain therefore ran RED 242/243 on every leg
  with the sole failure `AttributeError: module
  'form.graph_journal_crash_test' has no attribute 'smoke'`
  — a defect in the circuit's own test, NOT in the product
  repair (the suite never executed in those legs). Fixed by
  adding a `smoke() -> bool` wrapper (commit `e364644`),
  verified through BOTH entry points (standalone `__main__`
  12/12 rc=0 and the harness path GREEN 12/12), and the full
  regress x3 was re-run from scratch (run3, below). Run1 is
  recorded as RED evidence of the suite-contract defect;
  run2 was killed at ~24s by a VM replacement (NO RESULT);
  neither is cited as regress evidence for the repair.

Files changed (repair commits): `form/mandell/semantic_graph.py`,
`form/graph_journal_crash_test.py` (new), `form/regress.py`.
Records in this PR: this report, INDEX rows, the 72-32 and
72-29 register lines, and the verbatim archive of the
Director's 2026-11-06 02:44 CST 72-29
ALL_AI_CONFIRMATION_PASS ruling (rides this PR per his
directive to record it in the next ordinary report update).

## Evidence

- **Failing-first:** suite run at unrepaired head (branch
  commit `93df778` on main `bb82da3`): **8/12 PASS, exit 1**
  — all 7 control checks + cleanup PASS; all 4 defect checks
  FAIL (D1 x2, D2, D3).
- **Suite after repair:** `form/graph_journal_crash_test.py`
  **12/12 PASS, rc=0** (re-run at branch head `e364644`
  before this report commit: 12/12, rc=0). Neighbours:
  p2_dsc1_journal_proof 200/200, p2_dsc1_r3_listener 30/30,
  p2_r1_adversarial 27/27, p2_graph_test 61/61,
  p2_microgate 11/11.
- **Mutant:** restoring the silent skip (return True on a
  missing edge) -> suite **9/12** (the exact D1 x2 + D2
  profile). Reverted by **inverse edit only**; suite back
  to 12/12; diff clean (repair diff at commit time: 2 files,
  +92/-8, plus the suite and its later smoke() wrapper).
- **Regression:** full regress x3 sequential — **ALL
  TERMINAL GREEN** at branch head `e364644` (logs in the
  goal workspace, `hidden_files/72-32_logs/run3/`): leg 1
  (order=fwd) 243/243 GREEN, `LEG1_RC=0`; leg 2 (order=fwd,
  twice) pass 1 243/243 + pass 2 243/243 GREEN,
  `LEG2_RC=0`; leg 3 (order=rev) 243/243 GREEN,
  `LEG3_RC=0`; `CHAIN_DONE`. (Run1 RED on the suite-contract
  defect and run2 VM-killed are disclosed above and are NOT
  counted.)
- **Register:** the 72-32 line records this repair; its
  status prefix stays **PARTIAL** pending the Director's
  confirmation — no status the evidence does not support is
  claimed, and 72-32 is not counted COMPLETED. The 72-29
  line additionally records the Director's bounded
  ALL_AI_CONFIRMATION_PASS of 2026-11-06 02:44 CST; 72-29
  likewise stays PARTIAL, per that ruling.

## Anticipated probes

- *"Does recording FAILED for an unapplicable sync change
  load semantics?"* — the load still succeeds and exposes
  state; what changes is honesty: the journaled effect that
  did not apply is now visible in the persisted propagation
  ledger and in `propagation_status`, instead of being
  reported as synchronized. The designed explicit-failure
  path (corrupt dependent, W5b) already behaved this way;
  D1/D2 now match it.
- *"Is the D3 stale-MIRROR status check a repair or just
  detection?"* — both halves are in the repair: downstream
  hops are journaled before the upstream commit (so a crash
  leaves a replayable journal), AND status detects a stale
  MIRROR value read-only for states crafted or created
  before the journaling fix. The suite's D3 check builds
  exactly the pre-fix post-crash state and requires
  "failed", not "synchronized".
- *"Why did the first regress chain run RED?"* — the
  circuit's own suite lacked the harness `smoke()` entry
  point; disclosed in full above. The product repair was
  never implicated (the suite never executed), the fix was
  verified through both entry points, and the x3 was
  re-run from scratch.
- *"Is this the save path (GATE)?"* — no everyday-save, Q1
  locking, or pair-atomicity semantics change; see the GATE
  classification above and Q-32R.2.

## Questions for the Director

- Q-32R.1: Certification review of this bounded 72-32
  repair is requested; the merge proceeds under Ace's
  FIX-FIRST authority and is labeled accordingly.
- Q-32R.2: Does the Director concur with the FIX (not GATE)
  classification for semantic-graph journal replay /
  propagation repairs that do not touch the everyday-save
  pair path or Q1 locking? If not, this circuit's evidence
  converts to the GATE packet unchanged.
