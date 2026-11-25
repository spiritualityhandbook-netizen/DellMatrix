# DCC-XVII sigkill flake — investigation + repair packet (2026-11-02)

## CORRECTION (same day, post-closure — read first)

Two evidence claims in the original packet were wrong and are
corrected here; the verdict and the repair stand on the restated
basis below. (1) "Standalone suite ×31 all GREEN" is FALSE: the
30-run loop's final run (run 30) FAILED — the investigator concluded
"30/30" from interim tails before the loop's terminal output existed
(the truncated-readout failure mode). Run 30's failure was itself
caused by the investigator launching the U-probe campaign while the
loop was still running: two campaigns shared one form/state, and the
probe's clean_tmps() deleted run 30's in-flight temp mid-replace
(plain_run_030.log; timestamps coincide to ~0.1 s). (2) The U-probe
iteration-2 failure is RETRACTED as a clean reproduction: it ran
concurrently with plain runs 29/30, whose own U scenarios use the
SAME owner names and nursery paths — two writers racing one path
explain its artifact. Under clean sequential conditions the flake
did NOT reproduce in 114 pre-fix executions (85 U-probe iterations +
29 standalone runs). The mechanism verdict now rests on: the CI
event + verdict-line deduction, the measured scheduling margin
(single-writer timing probe), and the deterministic defect-restoring
mutant (late kill + vacuous verification => the exact failure
signature against a completed G2). Full correction evidence:
hidden_files/dccxvii_logs/correction_evidence_note.md.

## Verdict

**TEST-SIDE nondeterminism, identified to mechanism and repaired.**
The test asserted a timing premise it never verified (kill lands
mid-write). When that premise fails, the save has completed and the
canonical file holds a COMPLETE new generation — the product's
contract state — while the test still demands the old one. The
deterministic mutant (below) proves this path produces the exact CI
failure signature; no product-contract violation has ever been
observed in any dcc_xvii failure.

## The CI event

Form smoke run 41493670559 on main 081dd35: suite passed at 17:43Z and
17:48Z inside the same job, failed on the reverse-order leg at 17:59Z —
`rc=1 last=80/81 NOT_RETURNED_TRUE TRACEBACK`, REGRESS 220/221.
Full job log recovered via gh api (logs in hidden_files/dccxvii_logs/).
The traceback body is NOT in the CI log: form/regress.py captures suite
output and prints only the verdict line (an evidence-handling limit,
noted for the record).

Deduction from the verdict line (suite stderr empty — no `err=` suffix;
smoke() completed and returned False with exactly one failed check; a
traceback string present in suite stdout): the only code that prints
child stderr to stdout is `_run_u_scenario`, so the failed check was in
control U (checks 73–81 of 81; #80 = U.repeated,
#81 = U.program_crash_before_replace).

Test file and regress.py are byte-identical between 081dd35 and the
investigation base main d162687 — reproduction at current main is valid.

## Mechanism

`U.sigkill_mid_write` choreography (pre-fix): parent polls every 50 ms
for the child's `.dmtmp` temp, sleeps a fixed 0.5 s, sends SIGKILL, then
process B unconditionally asserts mid-write outcomes (canonical == G1
bytes, loads G1, exactly one partial temp). Nothing verified the kill
actually landed mid-write (A's returncode never inspected; "survived"
outcome ignored).

Measured margin (instrumented probe, 15 iterations): expected payload
4,015,402 bytes = 62 slow-write chunks × 20 ms ≈ 1.24 s write window
after temp creation; at the parent's kill moment the temp held only
0.72–1.84 MB (18–46%). Pass requires parent detection lag + 0.5 s sleep
+ overshoot < ~1.24 s, i.e. ≲0.7 s of parent scheduling slack. On a
loaded CI runner that slack is occasionally exceeded (~1 failure per 42
suite executions across the last 14 main smoke runs; the only failure).

This is the AGENTS.md §31.1 defect class: an asynchronous effect (kill
lands mid-write) asserted from a fixed sleep with no bounded wait on,
or verification of, the effect.

## Reproduction attempts (local, main d162687, worktree nbd-omega-dccxvii)

- Clean sequential pre-fix campaigns: standalone suite 29/29 GREEN in
  the uncontaminated portion of the loop (see CORRECTION for run 30);
  U-probe census 60/60 and 25/25 GREEN. The flake did not reproduce
  under clean sequential local conditions — consistent with a ~2%
  per-execution rate requiring a scheduling hiccup.
- Deterministic defect demonstration (Mutant B, below): forcing the
  kill to land after the save completes, with verification disabled,
  reproduces the exact failure signature
  (`canonical_is_g1_bytes`/`loads_g1`/`partial_temp_exists` false,
  canonical = complete G2) on iteration 1. Combined with the measured
  margin (~0.7 s of parent scheduling slack decides the outcome),
  this establishes the mechanism without relying on a chance
  reproduction.

## Repair (PR #229, branch uni/dccxvii-sigkill-sync, base d162687)

`form/mandell/dcc_xvii_test.py`, `_run_u_scenario` sigkill branch only:

1. Kill triggered by OBSERVED state: temp present with ≥ 65,536 bytes
   (first slow_write chunk flushed) while the child is alive — polled
   every 5 ms under a bounded 60 s deadline. No fixed sleep.
2. Interruption VERIFIED after the kill: returncode == −SIGKILL, temp
   still present, 0 < temp size < expected size.
3. A verified miss retries with a fresh wiped attempt (max 3). Process
   B and every assertion unchanged; B runs only after a proven
   mid-write kill (which also guarantees B's `.size`/`.g1` inputs
   exist — closing the sibling path where a mistimed kill crashed B).
4. Exhaustion fails loudly with diagnostics ("SIGKILL mid-write could
   not be established in 3 bounded attempts") — a harness failure,
   never a false contract verdict against the product.

All 81 checks preserved (names and count identical).

## Validation

- Fixed suite standalone: 81/81.
- Fixed U-probe: **60/60 iterations GREEN, zero missed windows** (the
  state trigger landed mid-write first-attempt every time).
- Mutant B (deterministic): late kill (2.0 s delay) + vacuous
  verification ⇒ reproduces the EXACT original signature
  `FAILED ['canonical_is_g1_bytes', 'loads_g1', 'partial_temp_exists']`
  on iteration 1. The verification is load-bearing.
- Mutant B2: late kill with verification intact ⇒ every miss detected
  (rc=0, temp_size=None), retried, scenario fails only as a loud
  establishment failure after 3 attempts; B's assertions never ran
  against the wrong generation.
- Mutant A (pre-fix file restored): 25/25 green — inconclusive
  statistically in that window (honestly recorded); the defect's
  observed instance is the CI event, and Mutant B carries the
  deterministic restoration proof.
- Full regression ×3 sequential on d3dc6da (logs regress_leg{1,2,3}):
  leg 1 fwd 221/221 GREEN; leg 2 --twice 221/221 GREEN pass1 + pass2;
  leg 3 --order rev 221/221 GREEN. dcc_xvii 81/81 in every leg.
- Exact-head CI on PR #229 (head d3dc6da, verified from terminal gh
  output in a separate step): Python package COMPLETE SUCCESS,
  Form smoke COMPLETE SUCCESS.
- PR #229 merged (normal merge) as 2d92c98 — verified via gh pr view
  and git log on origin/main; merge tree contains fix commit d3dc6da.
- Fresh-clone regress at merge head 2d92c98: 221/221 GREEN,
  dcc_xvii 81/81 (freshclone_regress.log).

## Evidence

Logs under ~/workspace/goals/dellmatrix-capability-circuits/hidden_files/
dccxvii_logs/: ci_job_full_clean.log (CI job log), plain_summary.log
+ plain_run_030.log (loop run 30 — investigator contamination, see
CORRECTION), u_probe_plain.log (iter-2 event — RETRACTED as
reproduction, see CORRECTION), correction_evidence_note.md,
u_probe_census.log (60× pre-fix), sigkill_timing.log (margin probe),
u_probe_fixed.log (60× fixed), mutant_a_revert.log, mutant_b.log,
mutant_b2.log, regress_leg{1,2,3}_*.log.
Ground + SWAT pre-mortem: hidden_files/dccxvii_ground.md.

## Notes / limits

- The CI traceback's exact sub-path (which U scenario, A- vs B-side)
  is unrecoverable because regress discards suite stdout. The
  mechanism accounts for the failing side by structural proof +
  measured margin + deterministic mutant (§31.3), NOT by a chance
  local reproduction (none occurred in 114 clean pre-fix executions)
  and NOT by local greens.
- Recommendation (not implemented, out of circuit scope): regress
  verdict lines could include the failing suite's last stdout lines
  so future flakes carry their traceback.
