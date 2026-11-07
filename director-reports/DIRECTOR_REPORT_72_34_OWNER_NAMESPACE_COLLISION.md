# DIRECTOR REPORT — 72-34: Owner namespace collision — DEFECT CONFIRMED (candidate DD-12)

Circuit: 72-34 — Test owner namespace collision + foreign-state
rejection (P1/E). Remaining register action at open: "Normalized
owner-name collision case specifically."

## 1. Verdict

DEFECT CONFIRMED (candidate DD-12). For two DISTINCT raw owner
names that normalize to the same safe name, live owner isolation
fails on every behavioral axis tested: silent foreign adoption
on load, nursery cross-leak on construction, and silent
cross-owner destruction on save — in-process and cross-process.
The foreign-state rejection proven for distinct owners
(persist_full_roundtrip) never fires for colliding owners,
because the shared file IS the default path and its stored
owner field is adopted as the resolved owner before any
comparison with the requested owner can reject it.

No production code changed by this circuit. Classification and
repair shape are asked, not assumed (Q-72-34.1, Q-72-34.2).

## 2. Mechanism (repository reality, main 0a4c4b69)

Canonical sanitizer form/persist.py:49:

    _safe_owner(owner) = every char not alnum/'-'/'_' -> '_',
    empty -> "operator". Case preserved.

Distinct raw owners collide: "a/b" == "a_b" == "a b" == "a.b".

ALL live owner-state paths key on _safe_owner ALONE:
program_<safe>.json (+ _cp_ checkpoints), nursery_<safe>.json,
ideas_<safe>/ + ideas_<safe>.json, graph_<safe>.json
(+ .journal), and the core_i_recovery journals
(rollback_/confirm_/checkpoint_/supersede_/exchange_import_
<safe>.journal.json).

ONE collision-safe surface exists: checkpoint_generation
._owner_ns = <safe>.<sha256(owner)[:12]>, built for exactly
this hazard (DCC-XVIII); dcc_xviii_test P.collision_* proves
generation isolation and notes in a comment that the live
canonical files collide — "pre-existing Persistence V2
behavior, out of scope here." 72-34 owns that remainder.

Load resolution: persist_rest.load -> _validate_program_data
returns the FILE's owner (Q-016); _load_impl binds the program
to the resolved owner. For distinct owners that path is
reachable only via an explicit foreign path (pinned). For
colliding owners the shared file is the default path, so the
substitution is silent.

## 3. Evidence

Failing-first suite form/owner_namespace_collision_test.py
(12 checks) at unrepaired main: **5/12 PASS, rc=1** — controls
K1 (collision premise), K2 (generation namespace disjoint),
K3 (non-colliding pair isolated), K4 (explicit-path foreign
resolution), Z (cleanup) all PASS; defect checks ALL FAIL:
D1 load returns the other owner, no refusal; D2 the other
owner's marker state is adopted; D2X the same in a fresh OS
process (CROSS_PROCESS); D3 open_program construction leaks
the other owner's nursery proposal; D4 save under the second
owner overwrites the first owner's file (subsequent load of
the FIRST owner returns the second owner's state — the first
owner's saved state is silently destroyed); D5 both
directions.

Independently reproduced by Uni's main session in a disposable
clone at the suite SHA: identical 5/12, identical failure set.
Probe (hidden_files/72-34_probe.py) agrees on every axis,
including the checkpoint control: commit under owner X ->
has_checkpoint(X) True, has_checkpoint(Y) False.

Suite design note: shape-agnostic. A repair may namespace the
live paths (the _owner_ns precedent) OR refuse foreign state
loudly at load/save/construction; either passes the suite.
Silent adoption is the only failing shape. The suite is
deliberately NOT registered in form/regress.py — it is
failing-first evidence; the canonical regression is untouched
by this circuit and remains 256 suites green at main.

## 4. Records carried in this PR

- This report + INDEX rows (report + ruling archive).
- responses/DIRECTOR_REVIEW_EMAIL_2026-11-07_72_10_
  BOUNDED_PASS.md: verbatim archive of your 2026-11-07
  09:25 CST ruling (72-10 bounded ALL_AI_CONFIRMATION_PASS
  on Q-72-10.3; Q-72-10.1 charset preserved; Q-72-10.2
  observed-only).
- DIRECTOR_REPORT_72_10_SEED_GRAMMAR_STRESS.md: the
  FINAL_CI placeholder completed per your post-merge asks
  (PR-head package 42384871312, Form smoke 42384871203,
  browser-acceptance 42384871228, all terminal SUCCESS at
  d4ffc12a; PR #326 merged
  0a4c4b69f1da05c2c1e68d0257ef3e70ec9272cf; delivered
  merge tree a27cc709442665c6f0806dc2851353cdca5e0235 ==
  frozen candidate tree; merged-main package 42387509030
  + Form smoke 42387509036 terminal SUCCESS).
- Register: 72-34 row updated (collision case evidenced,
  defect recorded); row stays PARTIAL. Strict stays 17/72.

CI at the final PR head: __FINAL_CI__

## 5. Anticipated probes

- "Is any real user affected today?" Owners in production use
  are simple names (e.g. Ace's) that do not collide with each
  other; the hazard fires when two distinct owner strings
  normalize together — realistic for derived/programmatic
  owner names (paths, emails, "First Last" vs "First_Last").
  The defect is a correctness/isolation hole in the canonical
  persistence contract, not a claim of observed data loss.
- "Why not refuse at _safe_owner?" Refusal changes load/save
  semantics for names that currently work alone; it is one of
  the two shapes in Q-72-34.2, not a unilateral choice.
- "Does Exchange inherit this?" exchange_import journals key
  on the same safe name (census above); any repair shape must
  cover them or explicitly scope them out.

## 6. Questions for the Director

- Q-72-34.1 (classification): is the repair a GATE-bucket item
  (it touches persistence path naming / load-save semantics),
  or a bounded FIX-FIRST repair by analogy with the DCC-XVIII
  generation-namespacing fix? Uni does not self-classify.
- Q-72-34.2 (repair shape): (a) hash-namespace the live paths
  like _owner_ns, with a legacy migration story for existing
  safe-name files; or (b) refuse loudly when a load/save would
  bind a raw owner to a file whose stored owner differs while
  sharing its safe name; or (c) another shape you prefer?
- Q-72-34.3: may this evidence PR merge on your bounded
  confirmation, as with 72-33/72-10, leaving the repair to its
  own circuit once classified?
