# MPC-009 COMPLETION PACKET
PARALLEL PRODUCT CONTINUATION + EXTERNAL AUDIT ISOLATION

Date: 2026-10-03
Authority: ACE > DIRECTOR > UNI / ADAPTIVE SUSX100 > REPOSITORY
Autonomy: NO
Director decision: PROCEED
External auditor: Claude Sonnet 5.5 (independent, read-only; no Uni
conclusions fed; no implementation changed for the audit; no waiting).

---

## A. PR #67 — MERGED

PR67_SECURITY_CLASSIFICATION: EVALUATION_UNAVAILABLE_QUOTA
Evidence (exact head 329f8435254d774ef8f82aa07c13e48120fc68cf):
check-run 111230594570 (run 37132625310), 2026-10-03T15:16:16Z:
`SessionModelError: You have exceeded your monthly quota`,
statusCode 402, errorCode "quota", configurationError false.
"Error creating PR review request" — the AI reviewer never analyzed
the diff. Inspected directly from the run log, not inferred.
Python 3.11 exact-head state: SUCCESS (run 37132623419).
Python 3.10 exact-head: SUCCESS. Smoke exact-head: SUCCESS.

PR67_EXACT_DELTA (af48f75 → 329f843, proven by exact git diff):
1 file added: MPC_008_PACKET.md (241 insertions). Zero modifications to
any other file. Documentation-only PROVEN, not inferred.

Bounded substitute review over the exact delta: PASS — markdown-only,
zero executable/embed patterns, zero secret patterns, all referenced
SHAs exist in-repo. Additionally, the code head af48f75 itself received
a REAL github-advanced-security PASS (check-run 111229676975,
completed/success) — the code was AI-reviewed clean; the delta adds no code.

Directive condition met (quota + doc-only + clean) → MERGED.

PR67_MERGE_SHA: 73102cdd66b2c4c74b0bc5f2a935a0a6185b4357
(2026-10-03T15:23:45Z)
POST_MERGE_MAIN: 73102cdd66b2c4c74b0bc5f2a935a0a6185b4357 (verified via
ls-remote)
POST_MERGE_TREE: de9b8d75074a793ab3e29f31d25c2d81c604f46f (fresh clone)
Fresh-clone public behavior at merge head: "resume" → "Session loaded.";
"make a macro" → honest refusal; "create an idea called macro" → idea
created. All as certified.

---

## B. DELL87 — DIRECTOR RULING IMPLEMENTED

DELL87_FINAL_CLASSIFICATION: KEY RENAME (provisional authority confirmed)

DELL87_AUTHORITY_EVIDENCE (bounded historical/current check):
- Mechanism at introduction (f913307, earliest): `st.store[new or old] =
  st.store.pop(old)` — key rename from day one. Never value substitution.
- Registry wording "Atomic substitution old to new" written at the same
  time (58966de) — contemporaneous loose wording, not a separate semantic.
- Tests (spectrum_closure_test) explicitly pin key-rename + rollback.
- Signature roles already describe keys ("Existing key to replace").
- No commit in history proves substitution was intentionally canonical.
  No contradiction found → no STOP triggered.

REGISTRY_CORRECTION_IF_ANY: form/mandell/core_ii.py:43 —
"Atomic substitution old to new" → "Atomic key rename old to new";
synonyms "Replace Swap Substitute" → "Replace Rename Key".
Behavior untouched per ruling. spectrum_closure 57/57, semantic_route
59/59 after the change. ("Fractal" stale name in gate_discipline.py:90
left for C-R1-009.)

---

## C/D. PLACE / UID COLLISION — INVESTIGATED, CORRECTED, CERTIFIED

UID_IDENTITY_INVARIANT (derived from runtime, persistence, tests, history —
not invented):
- UID = program-local unique identity = `plane.units` dict key.
- Persistent across save/load (serialized as the dict key).
- Referenced by: lineage parents (uid lists), sandbox member_ids,
  zoom_target, lattice content=id, keys.remember meta.id.
- No intentional uid-sharing mechanism exists; no unit-rename mechanism
  exists (Dell87 renames Mandell store keys — a different namespace).
- Scope: program-local (per-owner programs), not global.
- Raw-Mandell silent overwrite violated this invariant while references
  kept pointing at the uid → ALIAS/CORRUPTION class.

PLACE_COLLISION_PROBE_MATRIX (UNI probes + ARGUS attack round, scope-labeled):
| case | path | result |
|---|---|---|
| unique UID | raw / English | NO EFFECT (unchanged) |
| duplicate UID same process | raw seed ×2 | pre-fix: OVERWRITE (detail wiped, count unchanged); post-fix: DEDUPLICATION (X_1, original intact) |
| duplicate UID after save+reload | raw | pre-fix: OVERWRITE; post-fix: DEDUPLICATION |
| duplicate UID cross-process | raw, same owner | pre-fix: OVERWRITE (verified via saved JSON); post-fix: dedup |
| same name variants ("same thing"/"same_thing") | raw | COLLISION → pre-fix OVERWRITE; post-fix DEDUPLICATION |
| 24-char truncation collision | raw | pre-fix OVERWRITE; post-fix DEDUPLICATION |
| English duplicate | English | DEDUPLICATION (pre-existing parse_and_place guard) |
| English-dedup-slot invasion (raw X_1 after English X_1) | raw | pre-fix: OVERWRITE of English unit; post-fix: DEDUPLICATION |
| Dell14 Bind / Dell15 Map / Dell7 Link duplicates | raw | pre-fix: OVERWRITE (all via leaf place_idea); post-fix: DEDUPLICATION |
| empty/whitespace label | raw seed | REJECTION (honest "Seed error") |
| case variants (CaseKey/casekey) | raw | NO EFFECT (case-sensitive, distinct uids) |
| 53-flood same name | both paths | pre-fix: OVERWRITE at n>50 break (both paths); post-fix: 53 units, DEDUPLICATION |
| Outcome honesty | raw dedup | pre-fix: silent/misleading; post-fix: receipt names actual uid |

PLACE_COLLISION_CLASSIFICATION: VERIFIED → CORRECTED → CERTIFIED.
Pre-fix, the raw-Mandell path was a confirmed live silent-data-loss vector
(8 overwrite vectors incl. cross-process and English-slot invasion), with
receipts indistinguishable from fresh creation.

## NULL / ARGUS

NULL_RESULTS: fix NECESSARY (real harm, publicly reachable, violates
verified invariant); PROVEN no existing guard can serve (chain walk of all
six raw-path steps — no guard; parse_and_place's guard is on a disjoint
route and parses English, not Mandell; plane.place must stay
overwrite-capable for restore); mirror-loop MINIMAL (all 13 leaf call
sites are creations; restore bypasses the leaf). One refinement adopted:
include the loop cap verbatim (later superseded — see below).
ARGUS_ATTACKS: 20+ vectors across two eras (pre-guard c14cd79, post-guard
1813649): duplicates, Bind/Map/Link handlers, truncation collisions,
case/unicode/dots, slot invasion, 53-floods, cross-process, reference
rebinding, English-dedup defeat attempts.
ARGUS_RESULTS: pre-guard: 8 OVERWRITE vectors confirmed. Post-guard:
common case closed (DEDUPLICATION). Two residuals found → both remedied:
(1) n>50 break hole inherited from parse_and_place → 53rd creation
overwrote on BOTH paths; (2) raw dedup receipt claimed the requested name
while delivering X_1 (vector-9 honesty class).

## IMPLEMENTATION_IF_AUTHORIZED

Authorized by directive D (unambiguous invariant + raw-Mandell violation →
smallest existing-authority guard) + NULL gate + ARGUS residuals.
form/mandell/executor_leaf.py (leaf place_idea):
- uid derivation unchanged; added dedup loop mirroring parse_and_place
  (converges on established guard, no second identity system).
- Removed the `n>50: break` cap (loop provably terminates: n strictly
  increases over a finite unit set; the break left a colliding uid).
- Honest receipt: `Created idea: "X" (id: X_1)` when dedup fires.
form/dell_matrix/needs.py (parse_and_place):
- Removed the same `n>50: break` cap (same failure class, sibling fix;
  English 53-flood also silently overwrote).
plane.place() deliberately NOT guarded (restore authority depends on
overwrite-by-uid after units.clear()).

FILES_CHANGED (branch mpc-009-work vs merged main 73102cd):
- form/mandell/core_ii.py (Dell87 registry wording)
- form/mandell/executor_leaf.py (dedup guard + cap removal + honest receipt)
- form/dell_matrix/needs.py (cap removal)

TEST_RESULTS: dcc_vi 12/12, semantic_route 59/59, core_i_maturity 20/20,
spectrum_closure 57/57, dcc_xviii 89/89, harness 17/17, modes 13/13,
susx100 24/25 (tripwire "no Dell semantics changed" correctly fires on
the Director-authorized edits — flagged for human review, as designed).
E-proofs: duplicate raw placement cannot destroy (incl. 53-flood both
paths); unique placement unchanged; English dedup unchanged; save/load
preserves deduped identities; rollback valid; Outcome names actual uid;
references resolve to original uid (NO EFFECT under dedup).
CI_RESULTS: branch pushed (7110bfa); PR not yet opened for MPC-009.
CANDIDATE_HEAD: 7110bfa
PR_STATE: no MPC-009 PR opened yet (Director merge decision required;
per AUTONOMY=NO, no PR opened without explicit instruction — branch
mpc-009-work pushed and ready).

---

## CAPABILITY_BEFORE / AFTER

BEFORE: raw-Mandell seeds could silently destroy units by UID collision
(8 vectors, cross-process, invisible in receipts); Dell87 registry
misdescribed the mechanism; PR #67 unmerged.
AFTER: all creation paths deduplicate honestly (receipt names the real
uid); no silent overwrite at any flood depth on either path; Dell87
registry matches the mechanism; PR #67 merged and post-merge verified.

## F. CLAUDE_AUDIT_ISOLATION_CONFIRMED

No architecture or product change was made because of the external audit.
No Uni conclusions were fed to Claude. No waiting occurred. Evidence
preserved in exact current form (probe matrices, receipts, diffs above)
for Director's CLAUDE BLIND vs RUNTIME vs SUSX100 vs INTENDED comparison.
No pre-emptive defense prepared.

---

## G. RECONCILIATION

R1_DEBT_RECALCULATED:
- C-R1-001 taxonomy: OPEN (Director)
- C-R1-003 registry 90/94/95: OPEN
- C-R1-004 Dell37: OPEN
- C-R1-005 Dell87: RESOLVED (KEY RENAME ruled; registry corrected)
- C-R1-006 conditional slot: OPEN (narrowed)
- C-R1-007: RESOLVED (MPC-008)
- C-R1-008: CLOSED_FALSIFIED
- C-R1-009 stale names: OPEN (low; "Fractal" remains in gate_discipline.py:90)
- place-collision: RESOLVED (corrected + certified)

NEXT_BROKEN_LINK: C-R1-004 (Dell37) — the oldest remaining unresolved
R1 item with no active investigation.
NEXT_PRODUCT_CLUSTER (bounded, for Director authorization): open MPC-009
PR for the three-file branch (Dell87 wording + collision guard + cap
removals), run exact-head CI, then take up Dell37 per R1 evidence.

CONTRADICTIONS: none.
UNKNOWNS:
- Director merge decision for MPC-009 branch (7110bfa)
- Claude external audit report (not yet arrived; isolation preserved)
- GitHub AI security quota restoration (persistent EVALUATION_UNAVAILABLE)

---

AUTONOMY: NO
DIRECTOR_DECISION_REQUIRED: YES
Decisions queued:
1. Open/merge PR for MPC-009 branch 7110bfa (collision guard + Dell87 wording).
2. Authorize next product cluster (Dell37 per R1).

STOP.
