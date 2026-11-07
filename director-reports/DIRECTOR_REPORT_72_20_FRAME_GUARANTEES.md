# DIRECTOR REPORT — 72-20: Frame Guarantees Rechecked; Dell 62 Concurrency Claim Repaired

Circuit: 72-20 (Master Objective Register §6.7) — "Challenge
Branch/Parallel/Sequence/Join reported guarantees (P1/I)
(= SM-18)." Remaining action as registered: "Set-wide
guarantee recheck + explicit no-true-concurrency contract
statement." Original acceptance: "Confirm execution order,
failure propagation, and Join verdicts. Do not claim true
concurrency if execution is sequential."

Executed as a FIX circuit under Sleep Protocol v2 /
Ace FIX-FIRST authority. Branch:
uni/72-20-frame-guarantees, base main
119beac068933384b3ff1282c3611871a15d2558 (PR #319 merge).
Repair SHA: e8d58cc54c116f142c0dcdfd81ddfeb9c047274c.
One descriptive-metadata repair; no execution behavior
changed.

## 1. The guarantees hold (FACT)

A dedicated 35-check suite (form/frame_guarantees_test.py,
registered in form/regress.py — canonical count 250) pins
the four frames' guarantees at the public entry path,
grounded by a 13-composition probe
(hidden_files/72-20_probe.py):

- Sequence: written order; last writer wins shared state;
  a member failure does NOT stop the body (a Set after a
  failed Delete still lands); the closing Join verdict
  reflects the body and the chain error keeps the leaf's
  root cause.
- Parallel: the same sequential walk in listed order —
  deterministic across five repeated runs (last LISTED
  writer wins every time). Its distinction from Sequence
  is failure capture: a sibling failure is recorded, the
  remaining siblings still run, the frame status becomes
  'fail', the chain error keeps the sibling's root cause.
- Branch: only the taken arm executes and mutates, in
  both directions; unchosen occurrences are skipped
  receipts and never mutate.
- Join: policy is the Join atom's label (default 'all').
  On the same mixed body, 'all' fails join_fail while
  'any' passes — and the chain still reports the leaf
  failure under 'any'. Skipped receipts never count as
  failures (an unchosen arm's failing Delete leaves the
  Join and the chain ok). An empty executed child set is
  a successful Join under both policies and both frame
  kinds, and an orphan Join with no frame at all also
  succeeds (Step 11 settlement, rechecked set-wide).

## 2. The defect: a concurrency claim the behavior never made

The canonical registry row for Dell 62 (form/mandell/
core_ii.py:18) claimed manor "Execute independent
operations concurrently" with root "concurrent". Execution
is provably sequential: Parallel and Sequence run the
identical execute_range walk in chain_exec.py, and a source
census finds NO threading, asyncio, multiprocessing, or
executor-pool primitives in chain_exec.py, core_ii_exec.py,
control_runtime.py, or executor.py (pinned in the suite).
The Dell's own proof-card DEEP NOTE already stated the
truth ("in a chain the body runs sequentially") — the
registry contradicted it. Repo-wide census: core_ii.py:18
was the ONLY concurrency-claim surface (the proof cards
carry no such claim for 62).

Repair (descriptive metadata only — manor and root have
no behavioral consumers; verified by consumer mapping:
contract()/dell_cards read them as identity text, nothing
branches on them): manor now reads "Execute operations in
listed order - sequential, not concurrent; a sibling
failure is captured and the remaining operations still
run"; root "concurrent" -> "together". Manifest keywords
("Parallel Concurrent Simultaneous Together") are routing
synonyms, not contract claims, and are unchanged
(Q-72-20.2 asks whether you want them narrowed anyway).
Classified as a documentation/contract-claim drift like
72-13's — behavior was always correct — so no DD entry,
per your 72-13 instruction.

## 3. Verification

- Suite failing-first at base: 33/35 — exactly the two
  registry-claim checks (manor, root). After repair: 35/35.
- Mutant: the old claim restored -> 33/35, exactly those
  two checks; inverse-reverted, tree clean, 35/35.
- Neighboring consumers: core_ii_smoke output IDENTICAL
  at base vs repair (rc 0); d1_proof_cards_test 6/6.
- Regression at the final branch head 0dff41b (logs
  hidden_files/72-20_logs/run2/): TERMINAL GREEN
  250/250 x3 (fwd / --twice / --order rev; all leg
  RCs 0, CHAIN_DONE present; the new suite runs inside
  the harness at 35/35). Two honest footnotes: the
  first chain attempt was killed mid-leg-1 by a
  runtime restart (partial log = NO RESULT, re-run);
  the re-run (run1 logs) came back RED 249/250 x3 —
  the new suite's smoke() returned main()'s int exit
  code instead of True (NOT_RETURNED_TRUE), a harness-
  contract defect in the suite itself, fixed in
  0dff41b (canonical return main() == 0) before the
  green run2. The RED logs are preserved at
  hidden_files/72-20_logs/run1/.
- CI at the final PR head: ALL TERMINAL PASS at final head 871738dc — Python package run 42342298181 (3.10 + 3.11), Studio Browser Acceptance run 42342298231, Form smoke run 42342298271 (PASS, 18m20s). PR #320 MERGED 2026-11-06: merge commit 6cf22dd34473179b1b68a97bcdb09945294d2d8f, tree 298e8f16eead9e53a8b8f5c646d0b70d1c3bad2f; merged-main CI terminal SUCCESS (Python package 42343632836, Form smoke 42343632844). Director verdict (2026-11-06 23:32 CST, archived in the 72-21 circuit records): bounded technical PASS conditional on terminal CI (condition satisfied before merge); Q-72-20.1 YES; Q-72-20.2 manifest synonyms retained.

## 4. Records carried in this PR

- This report + INDEX row.
- responses/DIRECTOR_REVIEW_EMAIL_2026-11-06_72_19_PASS.md:
  archive of your 72-19 ruling (bounded
  ALL_AI_CONFIRMATION_PASS; Q-72-19.1 YES; Q-72-19.2
  last-leaf summary retained).
- DIRECTOR_REPORT_72_19_FIRST_FAILURE_PROVENANCE.md: the
  CI/merge receipt placeholder completed (final-head CI
  all terminal PASS — Python package 42332547596,
  browser-acceptance 42332547594, Form smoke 42332547568
  PASS 17m52s; PR #319 merged
  119beac068933384b3ff1282c3611871a15d2558, tree
  69ca6b3946cbc39f65332586e6c3ba1c721aba22; merged-main CI
  terminal SUCCESS — package 42334010558, Form smoke
  42334010555).
- Register: 72-20 row updated (guarantee recheck landed;
  concurrency claim repaired; status stays PARTIAL).

## Anticipated probes

- "Is 'Parallel' itself the false claim?" — The NAME is
  the Dell's identity (like 'Route' for the Else marker);
  the register's acceptance targets claiming true
  concurrency, which lived in the manor/root text. The
  repaired manor is the explicit no-true-concurrency
  contract statement the register asked for, pinned by
  the suite so the claim cannot silently return.
- "Why keep 'Concurrent/Simultaneous' in the manifests?"
  — Manifests route user vocabulary to the nearest Dell;
  "run these together/simultaneously" intent legitimately
  lands on Parallel, whose contract now honestly states
  what it will do. If you judge the synonyms themselves a
  claim surface, Q-72-20.2 narrows them in one line.

## Questions for the Director

- Q-72-20.1: Confirm the set-wide guarantee recheck plus
  the registry contract repair satisfies 72-20's remaining
  action (row stays PARTIAL for SM-18's wider scope), or
  name the guarantee you still want challenged.
- Q-72-20.2: Should Dell 62's manifest keywords also drop
  "Concurrent"/"Simultaneous", or do routing synonyms
  stand as discovery vocabulary under the repaired
  contract?
