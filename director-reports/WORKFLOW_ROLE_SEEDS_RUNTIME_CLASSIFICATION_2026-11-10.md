# WORKFLOW ROLE SEEDS v1 — RUNTIME CLASSIFICATION (2026-11-10)

Addendum to `WORKFLOW_ROLE_SEEDS_IMPLEMENTATION_2026-11-10.md`,
answering the Director's MODE C implementation directive (email
receipt 1a1c6b673a26de6e, relayed by Ace 2026-11-10): parsing a seed
does not make its instructions executable — so every one of the 31
seeds was EXECUTED through the canonical front door in the WFROLES1
field and every atom classified by what the program actually did:

- **REAL** — the atom executed and performed its operation (`ok`).
- **DESCRIPTIVE** — the atom was skipped: it carries a label/prose
  argument with no executable binding; the program reports it not
  executed (ok=False, skipped=True) rather than pretending.
- **REFUSED** — the atom executed and the program refused it by name
  (a grammar/authority boundary: prose conditions, prose targets,
  invalid loop counts, and the like).

| Seed | atoms | REAL | DESCRIPTIVE | REFUSED | chain ok |
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

Full per-atom detail is retained in the goal workspace
(`hidden_files/impl_roles_evidence.json` +
`hidden_files/impl_roles_classification.json`).

## Authority isolation — PROVEN by the runs themselves

The directive's safety boundary states that a written Guard, Commit,
or Merge atom cannot independently grant permissions. The execution
evidence demonstrates exactly that: the seeds' sovereign-looking
atoms (95[Commit] in the Ace master, 21[Merge] in the Uni and Psalm
masters, 92[Guard], 91[Assert] throughout) were processed as ordinary
atoms — several DESCRIPTIVE, several REFUSED — and conferred nothing.
Across all 31 executions: no Nursery proposal was confirmed, no merge
occurred, no permission changed, no state outside the dedicated
WFROLES1 field was touched. WORKFLOW v1 authority remained controlling
throughout; the seeds operated strictly inside it.

## Reading of the result

The seeds are semantic scores written in Mandell. In the program,
roughly two atoms in five perform a real operation, about a third are
descriptive (they carry meaning for a reader — human or docked AI —
without a mechanical binding), and the rest meet an honest refusal at
a named boundary. That is the truthful runtime classification the
directive required: the Mandell is real, its executable subset is
proven, and its descriptive subset is not pretending to be machinery.
