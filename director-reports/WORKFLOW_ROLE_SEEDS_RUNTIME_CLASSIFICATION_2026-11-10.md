# WORKFLOW ROLE SEEDS v1 — RUNTIME CLASSIFICATION (2026-11-10)

Addendum to `WORKFLOW_ROLE_SEEDS_IMPLEMENTATION_2026-11-10.md`,
answering the Director's MODE C implementation directive (email
receipt 1a1c6b673a26de6e, relayed by Ace 2026-11-10): parsing a seed
does not make its instructions executable — so every one of the 31
seeds was EXECUTED through the canonical front door in the WFROLES1
field and every atom classified by what the program actually did:

- **EXECUTED_OK** (relabeled from REAL per the Director's 2026-11-10 instruction) — the atom executed and performed its operation (`ok`) in that run. Three atoms are additionally flagged **RUN_CONDITIONAL** in the JSON: their class depends on session/field state (see the evidence addendum).
- **DESCRIPTIVE** — the atom was skipped: it carries a label/prose
  argument with no executable binding; the program reports it not
  executed (ok=False, skipped=True) rather than pretending.
- **REFUSED** — the atom executed and the program refused it by name
  (a grammar/authority boundary: prose conditions, prose targets,
  invalid loop counts, and the like).

| Seed | atoms | EXECUTED_OK | DESCRIPTIVE | REFUSED | chain ok |
|---|---|---|---|---|---|
| ACE_OVERSEER_FULL (master) | 38 | 13 | 24 | 1 | no |
| DIRECTOR_HOURLY_FULL (master) | 32 | 7 | 25 | 0 | YES |
| KEEPER_FASTLANE_FULL (master) | 24 | 11 | 11 | 2 | no |
| UNI_CONTINUOUS_FULL (master) | 33 | 29 | 0 | 4 | no |
| PSALM_DOCKED_FULL (master) | 26 | 7 | 17 | 2 | no |
| ACE_SELF (lens) | 6 | 5 | 0 | 1 | no |
| ACE_OTHERS (lens) | 5 | 2 | 3 | 0 | YES |
| ACE_WORKFLOW (lens) | 5 | 4 | 0 | 1 | no |
| ACE_DIRECTIVE (lens) | 5 | 3 | 0 | 2 | no |
| ACE_FAILURE_PATH (failure) | 4 | 3 | 0 | 1 | no |
| DIRECTOR_SELF (lens) | 5 | 4 | 0 | 1 | no |
| DIRECTOR_OTHERS (lens) | 5 | 3 | 1 | 1 | no |
| DIRECTOR_WORKFLOW (lens) | 5 | 4 | 0 | 1 | no |
| DIRECTOR_DIRECTIVE (lens) | 5 | 3 | 0 | 2 | no |
| DIRECTOR_FAILURE_PATH (failure) | 4 | 3 | 0 | 1 | no |
| KEEPER_SELF (lens) | 4 | 4 | 0 | 0 | YES |
| KEEPER_OTHERS (lens) | 4 | 4 | 0 | 0 | YES |
| KEEPER_WORKFLOW (lens) | 4 | 3 | 0 | 1 | no |
| KEEPER_DIRECTIVE (lens) | 4 | 3 | 0 | 1 | no |
| KEEPER_FAILURE_PATH (failure) | 4 | 3 | 0 | 1 | no |
| UNI_SELF (lens) | 4 | 4 | 0 | 0 | YES |
| UNI_OTHERS (lens) | 4 | 3 | 1 | 0 | YES |
| UNI_WORKFLOW (lens) | 4 | 3 | 0 | 1 | no |
| UNI_DIRECTIVE (lens) | 4 | 3 | 0 | 1 | no |
| UNI_FAILURE_PATH (failure) | 4 | 3 | 0 | 1 | no |
| GEMINI_SELF (lens) | 4 | 4 | 0 | 0 | YES |
| GEMINI_OTHERS (lens) | 4 | 4 | 0 | 0 | YES |
| GEMINI_WORKFLOW (lens) | 4 | 3 | 0 | 1 | no |
| GEMINI_DIRECTIVE (lens) | 4 | 3 | 0 | 1 | no |
| GEMINI_FAILURE_PATH (failure) | 4 | 2 | 0 | 2 | no |
| INTERLOCK_MAP (interlock) | 10 | 8 | 0 | 2 | no |
| **TOTAL** | **272** | **158** | **82** | **32** | — |

Full per-atom detail is published in this PR
(`WORKFLOW_ROLE_SEEDS_RUNTIME_CLASSIFICATION.json`, relabeled per
§2 of the evidence addendum) and retained in the goal workspace.

## Authority isolation — supported by before/after snapshots (evidence addendum §3)

The directive's safety boundary states that a written Guard, Commit,
or Merge atom cannot independently grant permissions. The execution
evidence demonstrates exactly that: the seeds' sovereign-looking
atoms (95[Commit] in the Ace master, 21[Merge] in the Uni and Psalm
masters, 92[Guard], 91[Assert] throughout) were processed as ordinary
atoms — several DESCRIPTIVE, several REFUSED — and conferred nothing.
Across all 31 executions: no Nursery proposal was confirmed, no merge
occurred, no permission changed, no state outside the dedicated
WFROLES1 field was touched — the snapshot form of this evidence
(hash-compared before/after, confirmed 0 -> 0) is in the evidence
addendum, §3. WORKFLOW v1 authority remained controlling
throughout; the seeds operated strictly inside it.

## Reading of the result

The seeds are semantic scores written in Mandell. Run 1, exactly:
EXECUTED_OK 58.1% (158/272), DESCRIPTIVE 30.1% (82/272), REFUSED
11.8% (32/272). The descriptive atoms carry meaning for a reader —
human or docked AI — without a mechanical binding; the refused atoms
meet an honest refusal at a named boundary. That is the truthful runtime classification the
directive required: the Mandell is real, its executable subset is
proven, and its descriptive subset is not pretending to be machinery.

## Verification run 2 — reproducibility check (2026-11-10, ~12:50 CST)

At the Director's MODE A finding (counts documented, independent
verification required before certification), Uni re-executed all 31
seeds in a fresh load of WFROLES1 and published the full per-atom
data in this PR (`WORKFLOW_ROLE_SEEDS_RUNTIME_CLASSIFICATION.json`).

Run 2 totals: **161 EXECUTED_OK (59.2%) / 82 DESCRIPTIVE (30.1%) / 29 REFUSED (10.7%)** (272). Reproduction: 269/272 = 98.9%.
Against run 1 (158 / 82 / 32): **269 of 272 atoms reproduced their
class exactly**; DESCRIPTIVE is identical (82). Three atoms are
STATE-SENSITIVE, named here rather than averaged away:

1. `KEEPER_FASTLANE_FULL` atom 11, 89[Diff] — run 1 REFUSED
   (`baseline_missing`); run 2 EXECUTED_OK. Precondition NOT
   established: the evidence addendum (§1) excludes new-field,
   checkpoint, save+reload, maturity, label-text, and chain-position
   conditions, and the run-2 result did not reproduce on re-run.
   Recorded RUN_CONDITIONAL / PRECONDITION UNKNOWN.
2. `UNI_FAILURE_PATH` atom 0, 94[Catch] — run 1 REFUSED
   (`catch_illegal`); run 2 EXECUTED_OK.
3. `GEMINI_FAILURE_PATH` atom 0, 94[Catch] — same flip.

CORRECTION (2026-11-10, per the Director's MODE D documentation
requirement): an earlier version of this section explained the two
Catch flips with a DERIVED "live caught-failure context" theory.
That theory was FALSIFIED by the controlled tests in the evidence
addendum (§1): Catch refuses after in-chain and cross-chain
failures, and executes only inside an OPEN TRY ROOM (rooms persist
across chains in a session until closed) — proven by conditions
A/B/C/D and probes P1/P2/P3 there. The falsified text is removed
and replaced by this correction; the addendum carries the full
test record. Run 1's numbers stand above as the implementation
record; this run is the reproducibility evidence. Certification
of either set remains the Director's act.
