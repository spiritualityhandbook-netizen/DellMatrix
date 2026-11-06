# DIRECTOR REPORT — 72-36: Nested Core II Version Validation

Circuit: 72-36 (Master Objective Register §6.7). Bounded repair
authorized by the Director (Ace relay 2026-11-06; restated in the
2026-11-06 16:00 CST ruling email, Gmail 1a1b2e03ade83232):
"Begin 72-36 immediately: reject unsupported explicit nested
Core II versions before activation; prove valid v1, missing
legacy block, and prior binding/files preserved on refusal."

Branch: uni/72-36-core-ii-version-validation, base main
20856817e520e28f7d22ef84a3523aea5bbb831c (PR #314 merge).
Production code SHA: c101b6131be24fef7e289e3ec135eece0c972e5c
(db1e9563 suite+repair, c101b613 cross-process worker fix —
suite file only). Records commit + final PR head: see the PR.

## 1. Defect (FACT)

The public loader `persist_rest.load(owner, path=...,
activate=False)` accepted a nested `core_ii` member carrying
ANY explicit version and bound its contents, because
`restore_core_ii` (form/persist_core_ii.py) never validated the
member's version: it selected the member, shortcut on
`present is False`, and bound field-by-field. The outer Program
envelope has enforced a strict version contract since RTPH-I
(`_validate_envelope_version`, form/persist_rest.py:258-289);
the nested member had none.

Reproduction (the Director's, on main; Uni's scoping probe
hidden_files/72-36_probe.py at merged main 20856817, verbatim
shape): save a valid envelope; replace only its `core_ii`
member with {"version":V,"present":true,"store":
{"director_probe":"future"}}. At the unrepaired base, the
marker BOUND for V in {999, true, "1", null, -1, 0, 2, 1.0} —
8/8 unsupported values accepted.

## 2. Grounding decisions (evidence-named)

- Q1 — supported explicit versions = {1} ONLY. Git archaeology
  over 1,536 commits (hidden_files/72-36_q1_history_addendum):
  CORE_II_STATE_VERSION=1 introduced 2026-09-28 in 3e541a9
  together with both stamping sites; never bumped; no shipped
  fixture/state file carries any other version. The envelope's
  legacy 1-6 range was NOT borrowed — it is proven for the
  envelope, not for this member. (Caveat recorded in the
  addendum: live user state files outside the clone were not
  searched.)
- Q2 — a present block with NO version field REFUSES. The
  writer has stamped a version since the member's first
  commit, so a versionless present block was never emitted by
  a real writer; the envelope's missing-version leniency
  exists because pre-version envelopes really were emitted
  (v1-v6 lineage) — no such lineage exists for this member.
  The agent_local precedent (persist_rest.py:821-850: missing
  version on a present section is malformed) matches.
- Q3 — validation runs BEFORE the present:False shortcut. A
  future schema claiming "absent" is still an unknown schema;
  its absence claim is not proven absence. Cost: zero real
  files (only v1 was ever emitted; present:False with v1 —
  the emitted absent-state shape — loads normally).
- Non-dict member — a present member of the wrong shape
  ("not-a-dict", null) REFUSES. Wrong shape is malformed, not
  proven absence (the absence-proof discipline of 72-31: an
  existence collapse must never feed an absence decision).
  CONSEQUENCE, NAMED: form/mandell/core_ii_persist_test.py
  pinned the old silent fallback
  (malformed_loads/malformed_fallback asserted a non-dict
  member loads to a default state). That pin asserted the
  defect; it is corrected in this circuit to
  malformed_refused + malformed_file_unchanged, with the
  correction commented at the case. Suite remains 20/20.
- Q4 — refusal surface is ProgramLoadError (the loader's
  established fail-closed error, form/persist_rest.py:241),
  raised inside the staged load: load() builds private objects
  before the swap, so a raise leaves the bound owner, working
  copy, and every file untouched (load() never writes).

## 3. Repair (form/persist_core_ii.py only)

New `_validate_core_ii_member(raw)`, invoked from
`restore_core_ii` at both member-selection paths (envelope
member; bare block where data itself carries "present"):

- not a dict -> ProgramLoadError ("not an object")
- "version" missing -> ProgramLoadError ("no version field")
- version is bool or not an int -> ProgramLoadError
  ("non-integer version") — the bool trap (True == 1) is
  excluded explicitly, mirroring _validate_envelope_version
- version != 1 -> ProgramLoadError ("is not supported")

No other production file changed. The bind section's existing
field-level leniency is untouched: unknown fields and
malformed field values inside a supported v1 block behave
exactly as before (pinned by controls EXTRAFIELD and
FIELDLEVEL, and by core_ii_persist_test's
bad_store_ignored / unknown_field_ignored).

## 4. Evidence

Suite: form/core_ii_version_validation_test.py (new, 60
checks, registered in form/regress.py — canonical count 245).

- Failing-first at unrepaired merged main: probe 8/8
  unsupported versions BOUND; suite shape at introduction
  20/59 (every refusal-family check red; all controls and
  file-bytes checks green).
- Post-repair: 60/60 PASS — for each of the 8 values:
  public-load refusal (ProgramLoadError naming core_ii),
  tampered-file bytes unchanged, restore-level refusal with
  the prior in-memory binding preserved; plus NOVERSION,
  NONDICT, NULLMEMBER, FALSE999 families; BARE999 on the
  bare-block path; CROSSPROCESS refusal in a fresh
  interpreter (worker prints ProgramLoadError, rc=0).
- Controls green: V1 public roundtrip; ABSENT member loads
  default state; FALSE1 (present:False, v1) loads default;
  EXTRAFIELD (unknown field in v1) binds; FIELDLEVEL (store
  as a list inside v1) keeps field leniency; BARE1 bare v1
  block binds; RETRY (valid file still binds after every
  refusal).
- Mutant: validator body disabled (early return) -> suite
  20/60, exactly the control/bytes pass set; inverse-reverted;
  tree clean; suite back to 60/60.
- Neighbour: form/mandell/core_ii_persist_test.py 20/20 with
  the corrected pin (18/20 against the repair before the pin
  correction — failures were exactly the two defect-pin
  checks).
- Fresh clone from GitHub at c101b61 (clean tree): new suite
  60/60; core_ii_persist_test 20/20.

Regression (T3, at production code SHA c101b61; logs
hidden_files/72-36_logs/run1/): TERMINAL GREEN 245/245 x3 (fwd / --twice / --order rev; LEG1_RC=LEG2_RC=LEG3_RC=0, CHAIN_DONE present)

Merged-main CI for the base: PR #314 merge commit 20856817 —
Python package SUCCESS (run 42301441631); Form smoke
Python package SUCCESS (run 42301441631) and Form smoke SUCCESS (run 42301441652), both terminal at the merge commit.

CI at the final PR head: __FINAL_CI__

## 5. Register / records carried in this PR

- This report + INDEX row.
- responses/DIRECTOR_REVIEW_EMAIL_2026-11-06_72_31_PASS.md —
  the Director's 2026-11-06 16:00 CST ruling archive
  (ALL_AI_CONFIRMATION_PASS for PR #314 at 33b60c3; sleep-mode
  GO; 72-36/72-35 orders), carried per his instruction
  ("Carry the ruling in the next circuit records").
- Register: 72-36 row updated (bounded repair landed; status
  token unchanged — broader serialization/migration design
  remains the Director's); 72-31 row: PR #314 MERGED
  20856817 under the confirmation above; defect dial DD-09
  (72-31 confirm-race family) is FIXED.

## Anticipated probes

- "Why refuse a versionless present block instead of the
  envelope's legacy accept?" — §2 Q2: the leniency is earned
  by an emitted lineage; the member has none (stamped from
  its first commit). If a real versionless file exists
  outside the repository, it now fails closed with a naming
  error instead of silently binding — the fail-closed side
  of the trade, chosen deliberately.
- "present:False + 999 worked before (loaded default) — is
  refusing it a behavior break?" — §2 Q3: no emitted file
  can carry it; the refusal prevents an unknown schema from
  asserting absence.
- "Does the bare-block tightening affect generation staging?"
  — the only production caller passes the full envelope
  (persist_rest.py:970); staged loads use _load_impl with
  the same envelope. The bare-block path has no production
  caller; v1 bare blocks bind exactly as before (BARE1).
- "Field leniency inconsistent with member strictness?" —
  deliberate layering, mirroring the envelope: schema version
  is a hard gate; fields inside a supported schema stay
  lenient (existing pins preserved).

## Questions for the Director

- Q-36.1: Confirm the bounded repair at the PR's final head,
  or state the correction. (Merged under Sleep Protocol v2's
  hard gate on your authorization; this question asks for
  the certification ruling, which remains yours.)
- Q-36.2: Ratify or reverse the two judgment calls in §2 —
  Q2 (versionless present block refuses) and the non-dict
  refusal replacing the pinned silent fallback. Both are
  small, local reversals if you rule otherwise.
- Q-36.3: 72-35 (atomic-write failure boundaries) is next
  per your order; no question — noting the queue position.
