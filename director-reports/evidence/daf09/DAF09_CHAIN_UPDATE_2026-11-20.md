# DAF-09 EVIDENCE CHAIN UPDATE — Part III code stage (2026-11-20)

Row #21 (DAF-09 session-escape, = SM-02). Delivered in Part III's
successor code-stage PR under Director disposition 7057289921
(PR #502). **This update completes the evidence chain only. It
proposes NO flip: row #21 stays OPEN. DAF-09 is never resolved on
local evidence (§31.3); closure remains the Director's
independent reproduction/verification act.** All results below
are UNI-REPORTED evidence.

## The discrepancy, stated exactly

- The Director's independent reproduction stands at **19/22**:
  in his environment, 3 of the (then) 22 timeout-tree checks fail
  — the session-escape cleanup behaviour differs (descendants of
  a timed-out run not observed dead/cleaned the way the suite
  expects).
- Every Uni-side run on record, in this VM, is full-green at its
  suite size (22/22 in the 2026-11-01 era; 31/31 at the current
  suite size, including the runs below).
- The delta is therefore **environment-dependent cleanup /
  process-identity timing**, not a code difference: the same
  suite bytes pass here and fail there. The instrumented
  investigation (Course 1) localized one real mechanism of this
  class locally — pidfd_open racing an already-dead witness
  (ESRCH at open, runs 4 and 7, 21/22 under saturation) — and
  that mechanism was repaired (ESRCH-at-open classification,
  PR #210). Whether the Director's 3 failing checks are that
  same mechanism in his environment is UNKNOWN from here; only
  his re-run can say.

## Every reproduction attempt on record

| # | Attempt | Environment | Result |
|---|---|---|---|
| 1 | Timeout-tree suite development runs (DAF09_TIMEOUT_TREE_PACKET) | Uni VM, 2026-10-31 era | Suite built to 22 checks; local green |
| 2 | Identity hardening investigation (DAF09_IDENTITY_PACKET) | Uni VM | Identity contract hardened; local green |
| 3 | pidfd hardening + fresh-clone regress legs (`pidfd_reg1_fwd.log`, `pidfd_reg2_twice.log`, `pidfd_reg3_rev.log`, `pidfd_freshclone_regress.log`) | Uni VM, fresh clone | Regress legs green |
| 4 | Director's independent reproduction | **Director's environment** | **19/22 — the standing discrepancy (§31.3)** |
| 5 | Instrumented investigation runs 1–7 (`instr_run*.jsonl`; idle + saturated) | Uni VM, instrumented driver, suite bytes untouched | Runs 1–3, 5, 6 green; runs 4 and 7 (saturated) 21/22 — ESRCH-at-open race witnessed (pid 35111 instance in run 7) |
| 6 | ESRCH-at-open repair verification (PR #210, merged 4ba052c; candidate a15e099) | Uni VM + exact-head CI | Suite 23/23; mutant 22/23 (exactly the new control); regress 220/220 ×3; fresh-clone regress at merge 220/220 |
| 7 | ESRCH regress legs (`esrch_regress_leg1-3.log`, `esrch_freshclone_regress.log`) | Uni VM, fresh clone | Green |
| 8 | Q2 post-check runs 1–4 (`post_post*.jsonl`; idle + saturated, NBD-4) | Uni VM | Recorded in DAF09_POSTCHECK_PACKET; no new discrepancy class |
| 9 | **This code stage** — `python3 -m form.daf09_timeout_tree_test` at branch base c6ee38d9 | Uni VM, part_clone_3 | **31/31, exit 0** (`part3_codestage_timeout_tree_2026-11-20.log`) |
| 10 | **This code stage** — instrumented driver run 1 (`daf09instr_driver.py`, suite main() unchanged) at c6ee38d9 | Uni VM, part_clone_3 | **Exit 0, DAF09_TIMEOUT_TREE: 31/31** (`part3_codestage_instr_run1_2026-11-20.jsonl` + `.stdout.log`, 153 JSONL events) |

Attempts 9–10 are the code-stage re-runs required by
PART_III_PLAN §2 (evidence only, logs preserved in this
directory). The full regress-chain legs are main-session serial
campaign work and were not re-run inside this Part's lane; the
historical legs stand at rows 3 and 7.

## State of the chain

- Local evidence: complete and current at c6ee38d9 (suite 31/31
  direct + instrumented).
- Director's independent act: still owed; his 19/22 stands
  until he re-runs. Nothing in this update asks him to accept
  local greens as resolution — §31.3 forbids it, and Part 0
  row #116 / Part VII row #112 inherit this row's state, so a
  wrong move here would propagate to three Parts.
- Certification: whole-program certification remains WITHHELD
  with DAF-09 as a named blocker (unchanged by this update).

*Files added to this bundle by this update (manifest rows added
to EVIDENCE.md in the same PR): this update, the two run logs,
and the instrumented run's JSONL + stdout log.*
