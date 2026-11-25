# DD-31 JOINT RESEARCH ANALYSIS — UNI HALF

Escalation under the two-cycle cap (Ace ruling 2026-11-10, §33):
DD31-CI-INTERMITTENT consumed the exception-request circuit
(PR #349), the diagnostic circuit (PR #350), and the Q-DD31-D1
hardening round without identifying its mechanism. This is Uni's
half of the joint analysis. Grok's half: director-reports/
GROK_ANALYSIS_DD31_2026-11-10.md (commit 14fcb3c, GROK-REPORTED,
folded here with partitions intact). The Director's half is his
hourly-check contribution. No claim of joint authorship is made
until both authorities review the assembled document.

## 1. Evidence ledger (UNI-VERIFIED unless marked)

FAILURES (always form.dd31_sanitize_copula_test, 20/21,
NOT_RETURNED_TRUE, sole red in its run):
- CI, PR #344 smoke attempt 1: pass 2 only.
- CI, PR #345 smoke attempt 1: pass 2 only (DD-45 suite 113/113).
- CI, merged main @ 7aad191 (run 42695404062) attempt 1: pass 2.
- CI, PR #346 smoke attempt 1: BOTH passes red.
- CI, PR #346 smoke attempt 2 (a re-run): pass 2 (first failed
  re-run on record).
- LOCAL, DD-14 leg twice_r2 on 7dc9ef0 (dd14_logs/
  leg_twice_r2.log): pass 1 red, pass 2 green. The only local
  reproduction; it kills "CI-only" and "second-pass-only".
GREENS (full-list passes): ~17 historical + 6/6 capture-grade
instrumented passes (diag_driver 7dc9ef0 x2, capA main 7780dff
x2, capB2 #348 813b2aa x2) + both passes of the DD-18 chain
2026-11-10 (dd31 green while d1_proof_cards was the sole red).
Rate: ~7 red in ~24 pre-instrumentation full-list passes (~29%
per pass). Six consecutive greens at that rate: ~13% likely —
the matrix bounds the hunt; it settles nothing (§31.3).

## 2. System map (static, UNI-VERIFIED at 7780dff)

- regress.py --twice: ONE _copy_tree copy (form/state EXCLUDED)
  serves both passes; run_entry verdict = rc 0 + returned marker
  + full count + no traceback. Stock harness discarded child
  stdout/stderr — the failing assertion was never captured
  (harness gap; the hardened capture in PR #350 closes it for
  future failures, identifiers + metadata only).
- The copy's form/state GREW from 5,662 to 7,891 entries between
  dd31's passes in one measured run (nested-capture inventory) —
  suites write real Program state into the shared copy.
- dd31 suite anatomy: 21 checks = 16 pure-string + 5
  Program/observer. FIXED owner "dd31mainZZ" (violates
  uuid-owner hygiene). _cleanup globs owner-named files only.
  Final check listdirs the WHOLE form/state for any filename
  containing "dd31". Program/observer checks read lifecycle
  state (faded/replaced/pending exclusions, 72-40 path).

## 3. Hypothesis space (predicted signature / evidence)

H1 Shared-copy residue in NON-owner-named state files (e.g.
   program_operator.json class) affects a Program/observer check.
   Signature: failure depends on which suites ran before dd31 in
   the same copy. Support: state growth measured; KIE-I precedent
   (persisted proposals leaking into "fresh" Programs).
H2 Single-suite interference: one specific predecessor suite
   leaves the triggering state. Signature: dd31 fails iff suite S
   precedes it in the copy. Testable cheaply (E1 below).
H3 Pass-1->pass-2 carry-over via the fixed owner (cleanup miss).
   WEAKENED: pass-1 failures exist on fresh copies (#346 att.1,
   leg twice_r2), which H3 cannot explain alone.
H4 Timing/load sensitivity in a Program/observer check (CI
   2-core contention vs local). Signature: failure rate tracks
   machine load, not order. Support: ~29% per-pass rate with no
   order pattern; local reproduction happened under a loaded
   regression chain.
H5 Directory-wide "dd31" residue assertion tripped by another
   suite's dd31-named artifact. Signature: the failing check is
   the residue check itself. No direct evidence (assertion never
   captured); the hardened capture now names it if it fires.

## 4. On Grok's proposed experiment (harmony record)

Grok proposes reconstructing the historical configuration and
running it >=30 times under the hardened harness. Uni's
consideration: (a) the historical runs were the ORDINARY smoke
configuration — there is no special seed set to reconstruct;
(b) 30 full-list runs cost ~10+ hours for a per-pass lottery
ticket; (c) his step 3 requests state inventory NAMES+SIZES,
which Q-DD31-D1's emission contract forbids in CI output (names
withheld; counts+bytes only — names remain available in
local-only diagnostics). The experiment is sound in spirit
(let the hardened trap catch it) but weak in discrimination
per hour. Uni proposes E1 first; Grok's mass-run remains the
fallback if E1 falsifies H1/H2.

## 5. Uni's proposed discriminating experiment (E1, bounded)

Pairwise predecessor bisection, fully local, one batch:
for each suite S preceding dd31 in LIST order: fresh copy ->
run S -> run dd31 -> record. ~263 pairs at seconds each
(~25 min total). A single hit identifies the interfering suite
exactly (H2 proven, H1 localized); zero hits falsify
single-suite interference and promote H4 (timing) + cumulative
H1, discriminated next by a prefix-growth variant. No CI cost,
no product code, privacy-safe (verdicts + counts only). Stop
criterion: first hit, or the full 263-pair matrix recorded.

## 6. Two-cycle ledger

Cycle 1: PR #349 exception-request circuit (denied).
Cycle 2: PR #350 diagnostic circuit + Q-DD31-D1 hardening
(conditional pass; merge hold pending renewed disposition).
Cap reached 2026-11-10. This analysis is the escalation the
cap prescribes. DD-31 remains OPEN; #348/#345 holds unchanged.

## 7. Next ONE action (for authority agreement)

Execute E1 and publish the pair matrix as an evidence addendum
to the joint document; fold Grok's mass-run as the agreed
fallback if E1 is clean. Awaiting Director + Grok concurrence
in the record (harmony rule) before execution.

— UNI (executor; evidence above is Uni-verified except where
marked GROK-REPORTED)

---

## ADDENDUM A — E1 RESULT (executed 2026-11-10 ~03:58–04:08 CST)

E1 ran under the fast-lane rule (no concurrence wait) on tree
6b471504ff46b96cdb3aef650e72ea5581c34c0e (main). Driver:
dd31_diag_logs/e1_driver.py; full pair matrix:
dd31_diag_logs/e1_pairs.log (Uni workspace, durable).

- CONTROL: dd31 alone in a fresh copy — GREEN 21/21.
- PAIRS: all 240 predecessors, each in a fresh copy followed
  by dd31 in the same copy — 240/240 recorded, ZERO hits.
  dd31 was GREEN after every single predecessor.

CONCLUSIONS (Uni evidence):
- H2 (single-suite interference) is FALSIFIED.
- H5 as a single-cause (one predecessor's dd31-named file
  tripping the residue check) is FALSIFIED — every
  predecessor's artifacts were present when dd31's residue
  check ran, across 240 trials.
- Standing: H1-cumulative (state accreting across MANY suites
  in the shared --twice copy; measured growth 5,662 -> 7,891
  entries between passes) and H4 (timing/load).

NEXT DISCRIMINATING STEP (E2, proposed): prefix ladder in ONE
shared copy per rung — suites 1..120 then dd31; 121..240 then
dd31; full 1..240 then dd31 — repeated. If only the full
prefix trips dd31, cumulative state is proven and the ladder
bisects the accumulation; if no local rung trips it while CI
keeps firing, H4 strengthens and the hardened capture
(PR #350) becomes the trap of record. Grok's 30-run mass
reconstruction remains the fallback. E2 runs on the fast
lane; both authorities judge the matrix at their cycles.

---

## ADDENDUM B — E2 RESULT (executed 2026-11-10 ~04:10–04:41 CST)

Prefix ladder in ONE shared copy per rung, tree 6b47150,
two rounds (round 2 interrupted by a VM replacement; the
durable log preserved round 1 + round-2 rung A; resume
completed B and C; log: dd31_diag_logs/e2_prefix.log):

- Rung A (suites 1..120, then dd31): 3,544 state files —
  dd31 GREEN 21/21, both rounds.
- Rung B (suites 121..240, then dd31): 2,295 state files —
  GREEN, both rounds.
- Rung C (FULL prefix 1..240, then dd31): 5,839 state files —
  GREEN, both rounds. Zero predecessor reds in any rung.

CONCLUSIONS (Uni evidence):
- H1-cumulative (single-pass accretion) is WEAKENED to near
  exclusion locally: the complete accretion, byte-count
  deterministic across rounds (5,839 both times), does not
  trip dd31 on this machine, twice.
- E2 models PASS 1 of --twice only. The one local context NOT
  yet isolated is the PASS-2 context: one copy that already
  ran all 263 suites once (accretion ~7,891 files) running
  the prefix again. Local --twice full runs remain uniformly
  green (6/6 capture-grade + both DD-18 chains), so even that
  context does not reproduce locally.
- The local hypothesis space is nearly exhausted. Weight
  shifts to H4 (CI-environment: shared-runner load, timing in
  a Program/observer check under contention, runner
  filesystem behavior). Per S31.3 the discrepancy is NOT
  resolved — the failing side's environment has not been
  reproduced — but the discriminating instrument now exists.

PROPOSED CLOSURE PATH for the joint analysis:
1. Merge PR #350 so the hardened capture is live in CI.
2. The next CI occurrence of the flicker names its assertion
   (identifiers + metadata only) — the trap converts the
   mystery into a targeted defect.
3. The fix then runs as an ordinary FIX-FIRST circuit.
Until step 2 fires, DD-31 stays OPEN with mechanism UNKNOWN;
no further local sampling is proposed — it has stopped
discriminating.
