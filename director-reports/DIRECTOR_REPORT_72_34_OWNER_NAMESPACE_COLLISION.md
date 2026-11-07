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
Silent adoption is the only failing shape.

CORRECTION (same circuit, before review): the suite was
initially committed UNREGISTERED, and PR-head Form smoke at
6c3fd95 failed RED on the harness completeness law —
form/regress.py treats every discovered test file as an
intended entry (OMITTED INTENDED ENTRY), so an on-disk suite
outside the list is itself a regression failure. That was
Uni's miss in grounding, not a product behavior. The suite is
now registered in form/regress.py (and exposes smoke() =
main() == 0 per the harness contract). Consequence, stated
plainly: the regression on THIS branch runs 257 entries with
exactly this one entry RED by design (5/12, the 7 defect
checks) until the repair lands; PR CI smoke is likewise RED
on the defect entry itself. The PR therefore cannot go green
— and cannot merge — until the repair lands under your
classification, or you direct it held open as an evidence
record (the #308 pattern). At main the canonical regression
remains 256 suites green; this branch's red is the defect's
own signature, nothing else.

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

## 7. Repair (Director ruling 2026-11-07 11:32 CST, Gmail
1a1b711ea7532e1d — archived in responses/ with this PR)

Classification per Q-72-34.1: bounded FIX-FIRST refusal, this
PR only. Shape per Q-72-34.2: fail-closed raw-owner identity
checks anchored on the program file's stored raw `owner`
field — the one live surface whose identity binding is
already trustworthy (the Q-016 file-owner resolution reads
the same field). No renaming, no migration, no deletion.

Mechanism (3 production files, +81 lines):
- form/persist.py: OwnerCollisionError(RuntimeError);
  stored_program_owner(path) returns the stored raw owner or
  None (absent / unreadable / no owner field — legacy without
  reliable identity is NOT treated as proven foreign);
  assert_program_owner_access(owner, path, context) raises
  only on a PROVEN mismatch (stored owner present and !=
  requested). The check never writes bytes.
- form/persist_rest.py: save() asserts access on the
  canonical target under owner_state_lock before any write;
  load() asserts on the DEFAULT path BEFORE any recovery
  journal is replayed or state adopted. An explicit path
  keeps the pinned Q-016 behavior (resolves to file owner;
  suite K4).
- form/open.py: Program.__post_init__ asserts access before
  recovery replay or nursery read on live construction (the
  injected sealed-generation-member path is exempt — bound
  to a sealed member, never the live file).

Neighbor contract update (form/mandell/dcc_xviii_test.py):
the P collision control previously documented the live
collision as "pre-existing, out of scope"; it now asserts
the repaired behavior — live construction of the second
colliding owner is REFUSED (OwnerCollisionError) while the
generation namespaces remain disjoint. 90/90 green.

Results:
- Suite: 12/12 PASS at the repaired tree (from failing-first
  5/12; the 7 defect checks now pass by refusal, controls
  unchanged). Verified first-hand by the main session and
  two cycle runs; cross-process check D2X included.
- Refusals are non-destructive: the guard raises before any
  write; refused load/save/construction leaves stored bytes
  untouched (suite D4/D5 assert the first owner's state
  survives intact and loadable under its exact name).
- Regression at the repaired tree: TERMINAL GREEN 257/257
  x3 (fwd / --twice / --order rev; LEG1_RC=LEG2_RC=
  LEG3_RC=0, CHAIN_DONE 2026-11-07 15:29 CST; logs
  hidden_files/72-34_logs/run1/; the collision suite runs
  inside the harness and is green on every leg).
- Mutant verification: EVALUATION_UNAVAILABLE. The
  guard-silencing mutant edit was refused by the execution
  environment's safety tooling in three separate sessions
  (12:01 and 14:01 cycles, and twice in the main session on
  the sibling 72-10 circuit); the edit never executed and was
  never routed around. The suite's non-vacuity rests on its
  failing-first signature instead: the identical suite,
  byte-for-byte, scores 5/12 with exactly the 7 defect checks
  failing against the unrepaired tree at this PR's base —
  the before/after pair is the mutation evidence of record.
  If you require the in-place mutant as well, it needs a
  session whose tooling permits the edit.

Narrow remaining gap (reported per Q-72-34.2, NOT closed):
identity checks anchor on the program file. Graph and ideas
files carry their own stored owner but have no standalone
guard; their reads are covered only insofar as the exercised
flows pass the program-file anchor first. The nursery file
carries NO owner field at all: a colliding nursery file with
no program file present has no identity binding to check,
so construction would not refuse on nursery evidence alone.
Closing those needs per-surface identity stamps (a write-
format change) or the gated namespace work — both outside
this bounded refusal. Same-owner and non-colliding legacy
paths are untouched and covered by controls K3/K4 and the
full regression.

## 8. Ask

Bounded re-ruling on this final head: confirm DD-12 FIXED
within the refusal scope above (with the named nursery /
standalone-surface gap retained), or direct the gap closed
first under separate authorization. FINAL_CI is completed
in the next circuit's records per standing practice.
