# WORKFLOW ROLE SEEDS v1 — IMPLEMENTATION (2026-11-10)

Circuit: ROLE-SEEDS-IMPL (Ace order, 2026-11-10 ~12:25 CST: "Implement
this asap — it is the Mandell for the workflow"). Source:
`director-reports/WORKFLOW_ROLE_SEEDS_V1_2026-11-10.md` (copy of the
draft Ace approved; 31 seeds / 272 atoms). Cycle count for the seeds
item: cycle 2 (draft = cycle 1, parse-verified only).

## What "implemented" means here — and what it does not

The seeds now EXIST INSIDE DellMatrix as first-class program content
in a dedicated owner field, `WFROLES1`, and the five master seeds have
been EXECUTED through the program's canonical front door with receipts
published below. Nothing was merged into product code; no product code
changed. The field state lives in the program's own persistence
(`form/state`, owner WFROLES1, on the Uni machine — state files are
not repository content). Certification remains the authorities' act.

## Landing (persistence layer) — VERIFIED

All 31 seeds were added to the WFROLES1 Nursery as PENDING proposals
(origin `ace_workflow_seeds_v1`, full seed text in each proposal's
detail), then the program was saved and re-loaded in a FRESH process:
**31 pending proposals present, labels verified** (5 masters, 20 lens,
5 failure paths, 1 interlock). Proposals-first is the landing the
draft's own §7 recommended; Ace's confirm is the sovereign step that
promotes any of them — Uni did not self-confirm any.

First-pass note (disclosed): the initial landing mislabeled one lens
seed (an extractor miss on the Keeper's DIRECTIVE lens heading). The
staging field — created minutes earlier by this same run, holding only
this run's unconfirmed artifacts — was re-landed cleanly before any
confirmation existed. The final field is the clean landing.

## Execution (front door) — RECEIPTS

Each master seed was executed via `execute_seed` (PUBLIC_ENTRY_PATH)
in the WFROLES1 field. `atom_results` counts match each seed's text
atom count exactly (full coverage). "Skipped" = atoms the program
reports as not executed (label-only atoms carry no executable
binding); "failed" = atoms that executed and refused/errored.

| Master seed | atoms | ok | skipped | failed | chain ok | first failure |
|---|---|---|---|---|---|---|
| ACE_OVERSEER_FULL | 38 | 13 | 24 | 1 | no | atom 11: condition_unparseable |
| DIRECTOR_HOURLY_FULL | 32 | 7 | 25 | 0 | YES | — |
| KEEPER_FASTLANE_FULL | 24 | 11 | 11 | 2 | no | atom 7: condition_unparseable |
| UNI_CONTINUOUS_FULL | 33 | 29 | 0 | 4 | no | atom 20: invalid_loop_count |
| PSALM_DOCKED_FULL | 26 | 7 | 17 | 2 | no | atom 3: scope_unknown:receive the command and its scope — who commanded it, through which rung of the chain, over exactly what field |

The Director master runs end-to-end (chain ok). The others stop at
named honest refusals — the program's known grammar boundaries, not
seed defects: prose conditions on Assert/Guard atoms refuse
`condition_unparseable` (the DD-42 law working as designed), a prose
Loop label refuses `invalid_loop_count`, a prose Scope target refuses
`scope_unknown`. The seeds are semantic scores; the program executes
what it can bind and refuses the rest BY NAME. Uni did not edit Ace's
seeds to make them pass — any grammar-level revision of the seeds is
Ace's call as their author.

Additionally, DIRECTOR_HOURLY_FULL was executed through the literal
REPL (`python3 -m form.repl --owner WFROLES1`, separate OS process,
exit 0) — REAL_USER_PATH-tier evidence for the run path; the REPL
trace shows the field state inline (`nursery=31`).

## Compose layer — NOT EXPRESSIBLE for these seeds (finding)

Named-composition publication was attempted for all 31 seeds and
published NONE, for two stacked grammar reasons, both verified:
(1) composition names are single simple identifiers (underscore names
fail parsing at the name); (2) with valid short names, a Compose body
passed as one seed string is split by the chain parser on ` > ` — the
canonical Compose body grammar is a short atom list (e.g.
`keep=70[Count]`, `part=70,89`), not a long prose-labeled chain, and
publication additionally requires a clean define-run (72-25 law).
Long role chains therefore cannot be stored as compositions through
the current surface; they live as Nursery proposals (above) and run
directly through the front door. Recorded as a capability boundary,
not worked around.

## Item state (WORKFLOW v1 §4)

Lifecycle: IMPLEMENTED + VERIFIED locally (proposals persisted across
a fresh process; masters executed with receipts; REPL run clean).
Certification: PENDING — Keeper CONFIRM and Director final check
requested on this PR. Final-check: NOT_YET_DUE. Blockers: none.
NEEDS_OVERSEER: Ace's Nursery confirm of the 31 proposals (his
sovereign step, at his pace — not a queue blocker).

## Questions for the authorities

Q-SEEDS.1 (Director): is proposals-first + direct front-door execution
the accepted implementation shape for role seeds, or is a composition-
grammar extension (long-chain bodies) wanted as its own circuit?
Q-SEEDS.2 (Keeper): record-truth check on the receipts table above
against the evidence file retained in the goal workspace
(`hidden_files/impl_roles_evidence.json`).
