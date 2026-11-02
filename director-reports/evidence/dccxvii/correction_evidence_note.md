# Correction evidence — plain run 30 and U-probe iter 2 (written 2026-11-02, post-closure)

## What the terminal loop delivery showed (after the circuit closed)
plain_summary.log final lines: run 29 rc=0 (18:33:48Z), run 30 rc=1
(18:33:53Z), "FAILURE at plain run 30", LOOP_DONE. The investigator had
concluded "30/30 green" from INTERIM tails before LOOP_DONE existed —
the truncated-readout failure mode (TOOLS.md rule) inside this very
investigation.

## Plain run 30 failure = investigator contamination, NOT a suite flake
plain_run_030.log: control R (confirm_proposal -> checkpoint seal)
died with AtomicWriteError: os.replace FileNotFoundError — its temp
graph_DCCXVII_R....dmtmp.34177.6b2cd739 was DELETED mid-write by an
external actor. At that moment the U-probe campaign (launched early by
the investigator on the false belief the plain loop had finished) was
running CONCURRENTLY against the same worktree form/state, and its
per-iteration clean_tmps() deletes ALL *.dmtmp.* in that directory.
u_probe_plain.log mtime 18:33:53.214 vs plain_run_030.log 18:33:53.308
— same instant. Two campaigns, one state dir: the exact invalid
configuration the mandate prohibited (sequential only).

## Consequence for the U-probe iteration-2 "reproduction"
U-probe iter 2 overlapped plain runs 29/30, which run the SAME U
scenarios with the SAME owner names (DCCXVII_U_sigkill_mid_write ->
identical nursery path and temp glob). Two writers racing one nursery
path fully explains the observed artifact (canonical = a completed G2,
no temp). The iteration-2 event is therefore RETRACTED as a clean
reproduction of the CI failure.

## What survives (clean, sequential evidence)
- The CI event itself (suites sequential in a private copy there).
- The verdict-line deduction placing the failure in control U.
- The margin quantification (timing probe ran alone, single-writer):
  ~1.24s write window vs fixed 0.5s kill delay => ~0.7s parent
  scheduling slack decides pass/fail. Structural, code-readable.
- Mutant B (ran alone, deterministic): forced late kill + vacuous
  verification reproduces the exact B-check failure signature against
  a completed G2. Mutant B2: verification catches late kills.
- Clean pre-fix campaigns: 85 sequential U-probe iterations (60 + 25)
  and 29 sequential standalone runs with ZERO failures — consistent
  with a ~2% scheduling-hiccup rate, NOT a reproduction.
- All post-fix validation (60/60 probe, regress 221/221 x3,
  exact-head CI, fresh-clone 221/221) ran sequentially: unaffected.

## Classification after correction
Mechanism verdict UNCHANGED (test-side, 31.1 class) but its evidence
basis is restated honestly: structural proof (code + measured margin)
+ deterministic defect-restoring mutant + CI signature. The claim
"reproduced locally" is withdrawn; under clean sequential conditions
the flake did NOT reproduce in 114 pre-fix suite/U executions.
