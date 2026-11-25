# DIRECTOR REPORT — 72-35: Atomic-Write Failure Boundaries

Circuit: 72-35 (Master Objective Register §6.7) — "Recheck
atomic-write orphan-temp + rollback cleanup bounds." Remaining
action as registered: "Boundary-by-boundary failure injection
(write/fsync/replace) as a dedicated suite." Executed as an
EVIDENCE circuit under Sleep Protocol v2 on the Director's
order (2026-11-06 16:48 CST ruling: "immediately begin 72-35
atomic-write orphan-temp/rollback failure-injection circuit").

Branch: uni/72-35-atomic-write-boundaries, base main
4900829a00d63eb63a87304011a39b68309089f4 (PR #315 merge).
Suite SHA: 776d519b7dfc2b83f485fa7c517709bc57905c44.
NO production code changed by this circuit.

## 1. Result (FACT)

A dedicated 67-check suite (form/atomic_write_boundaries_
test.py, registered in form/regress.py — canonical count 246)
injects failures at every atomic-write boundary the register
names and pins the resulting bounds. At the unrepaired base
the suite passes 67/67: NO defect was found in the write
machinery. Every documented bound of Persistence V2
(form/dell_matrix/atomic_write.py) holds under direct
injection. The one substantive finding is a wiring bound,
§3 — a fact about cleanup reach, not a write-correctness
defect.

Coverage was mapped first to avoid duplicating dcc_xvii
(save-level hooks, sweep dead/live, save-level crashes),
checkpoint_generation_stress (fsync error type, member-copy
abort, dir-fsync receipt at the commit level) and sm35
(everyday pair). The suite pins only the gaps, listed in its
docstring.

## 2. Bounds proven

- Helper boundary matrix (JSON + bytes entries): serialize
  failure / unserializable payload / temp_write / replace
  each raise AtomicWriteError (never a raw OSError) with the
  predecessor canonical bytes intact. Temp disposition per
  boundary: cleaned on ordinary failure; the temp_write hook
  leaves a PARTIAL temp BY DESIGN (the crash simulation),
  whose content is verified to be a strict prefix of the
  intended blob — a partial temp can never be mistaken for a
  complete generation, and loaders read only the canonical
  path.
- fsync failure (real os.fsync raising): AtomicWriteError,
  predecessor intact, AND the temp is cleaned — the cleanup
  half of this boundary was not asserted by any prior suite.
- Bytes helper: non-bytes input refuses without touching the
  target; a 1 KB binary (non-UTF8) blob lands byte-exact —
  the fingerprint property generation member copies rely on;
  dir-fsync degradation receipt is honest on both entries
  (False under dir_fsync_fail, True normally).
- Crash lifecycle, cross-process at the helper level:
  crash_before_replace exits 42 with the predecessor
  canonical and exactly ONE dead-pid orphan temp;
  crash_after_replace exits 42 with the NEW bytes canonical
  and no temp; a real SIGKILL during slow_write (4 MB blob,
  temp observed mid-write under a bounded wait) leaves the
  predecessor canonical and one partial orphan.
- Sweep semantics: removes dead-pid temps only; keeps
  live-pid temps, foreign files, and the canonical file; a
  temp whose pid field does not parse is scanned but NEVER
  removed; a temp naming a live-but-unrelated pid is kept
  (the safe direction — the sweep can strand a temp, it
  cannot delete a live writer's temp); a missing directory
  reports zeros without raising.
- Aborted generation commit (rollback half): a commit
  aborted at member_program raises CheckpointCommitError,
  the CURRENT pointer does not move (verified through the
  tri-state reader: ("verified", G1)), the orphan set is
  EXACTLY the already-sealed prefix (the nursery member
  only), and no manifest exists for the aborted generation —
  it can never be loaded or mistaken for committed state.
  The next successful commit's retention GC reaps the
  aborted orphans while retaining current AND previous
  generations complete (4/4 members each).

## 3. Finding — the wiring bound (no repair proposed here)

`sweep_stale_tmps` has NO production caller. Census pinned
executably by the suite (AST scan of form/**/*.py excluding
tests and the defining module): zero call sites. Orphan
.dmtmp temps are therefore removed only when something
explicitly calls the sweep (today: tests). Generation-MEMBER
orphans have an automatic reaper (the retention GC, §2);
raw .dmtmp orphans do not — after a real crash they persist
in the state directory until a manual sweep. They are inert:
no loader reads them, and the sweep's liveness discipline is
proven above. Whether to wire a sweep into a production path
(program open / load) is a persistence-path design decision;
per the GATE discipline this circuit proposes nothing and
changes nothing — Q-35.1 asks for the ruling.

## 4. Verification

- Suite: 67/67 at base and at the suite SHA.
- Mutants (each inverse-reverted, tree clean, suite back to
  67/67): M1 sweep ignores pid liveness -> 65/67, exactly
  E1.sweep.keeps_live_pid + E4.live_unrelated_pid.kept fail.
  M2 no temp cleanup on write/fsync failure -> 66/67,
  exactly B1.fsync_fail.temp_cleaned fails.
- Regression at the suite SHA (logs
  hidden_files/72-35_logs/run1/): TERMINAL GREEN 246/246 x3 (fwd / --twice / --order rev; LEG1_RC=LEG2_RC=LEG3_RC=0, CHAIN_DONE present; the new suite runs inside the harness at 67/67)
- CI at the final PR head: ALL TERMINAL PASS at final head 803fb84 — Python package run 42313372252 (3.10 + 3.11), Studio Browser Acceptance run 42313372226, Form smoke run 42313372264 (PASS, 19m6s). PR #316 MERGED 2026-11-06: merge commit 28719de02e3c78807aa4d6329d57a5e4881d5beb, tree 3e10b90512902b72892a0767aec1d46ff168ebf5; merged-main CI terminal SUCCESS (Python package run 42315407459, Form smoke run 42315407553). Director verdict (2026-11-06 18:04 CST, archived in the G-04 circuit records): ALL_AI_CONFIRMATION_PASS for the bounded evidence deliverable; Q-35.2 YES; Q-35.1 sweep stays manual, no production wiring authorized.

## 5. Records carried in this PR

- This report + INDEX row.
- responses/DIRECTOR_REVIEW_EMAIL_2026-11-06_72_36_
  CONDITIONAL_GO.md — the Director's 72-36 ruling archive
  (INSUFFICIENT_EVIDENCE timing hold + conditional FIX-FIRST
  GO; Q-36.2 ratified), per his standing carry instruction.
- DIRECTOR_REPORT_72_36_CORE_II_VERSION_VALIDATION.md:
  the CI/merge receipt placeholder completed (final-head CI
  all terminal PASS — package 42306577802, browser-
  acceptance 42306577701, smoke 42306577750; merged
  4900829a00d63eb63a87304011a39b68309089f4, tree
  68be01a17b797a156af6f3eedaa0dd41ba2e72cb; merged-main CI terminal SUCCESS (Python package run 42308917018, Form smoke run 42308917046 — pairing corrected 2026-11-06: the original receipt swapped the two run IDs; both runs were terminal SUCCESS, so the substantive claim was unaffected)).
- Register: 72-35 row updated (dedicated boundary suite
  landed; status stays PARTIAL — the row's wider scope is
  not exhausted by one suite, and the wiring question is
  open). Defect dial: no new defect; DD-10 (72-36) recorded
  FIXED in the 72-36 closure.

## Anticipated probes

- "Why no failing-first?" — this circuit's registered
  deliverable is the injection suite itself (an evidence
  circuit, like 72-28's proof circuit). It was run at the
  unrepaired base first; had any bound failed, the failure
  would have been the failing-first evidence and any repair
  on the save path would have gone to the GATE bucket, not
  Fix-First. The mutants prove the suite is not vacuous: it
  kills both a liveness-blind sweep and a cleanup-skipping
  writer with exact profiles.
- "Is the un-swept orphan a leak?" — bounded and inert: one
  partial temp per crashed write, never read as state, in
  the state directory only. The count grows only with
  crashes. The question is housekeeping reach, Q-35.1.
- "Unparsable-pid temps are never swept — forever?" — yes,
  by conservative design: the name pattern is helper-owned
  and strict; a name that does not parse is not provably the
  helper's to delete. Pinned as observed (E2).

## Questions for the Director

- Q-35.1: Should sweep_stale_tmps be wired into a production
  path (e.g., program open), kept manual, or left as-is?
  Any wiring is a persistence-path change and will be run
  as its own gated circuit on your ruling.
- Q-35.2: Confirm the 72-35 evidence closes the register's
  "dedicated suite" remaining action for this row (the row
  stays PARTIAL for its wider scope), or state what further
  boundary evidence you require.
