# Q-S2R.2 — VERITA-JUDGE classification-field schema PROPOSAL (records only)

Date: 2026-11-17. Circuit: Q-S2R.2 follow-on from PR #451.
Authority: Director Q-S2R answers on PR #451, comment 6946046074 —
VERITA-JUDGE is a test-surface participant only, not a live production
caller; its math stays labeled unvalidated; Uni owes a
classification-labeling proposal for Keeper check before adoption.
This document is that proposal. **It adopts nothing and changes no
classification.** Adoption requires Keeper check + Director ruling.

## Problem

The ledger's single `Classification:` line per equation entry bundles
two independent claims into one token:

- a **validation** claim (are the constants/formula derived or
  validated?), and
- a **participation** claim (who actually calls this at runtime?).

EQ-VER-002/003/004 currently read `ACTIVE_UNVALIDATED — live on the
auto-growth gate path / brain paths`. The liveness half of that text
was superseded on current-main evidence (ledger Append C, 2026-11-15):
the named production callers do not exist in the repository. Because
the two claims share one field, correcting the liveness claim appears
to touch the validation claim — and the Director's ruling requires
that `ACTIVE_UNVALIDATED` never be auto-converted. The schema below
separates the fields so each claim can be corrected on its own
evidence without moving the other.

## Proposed schema (per equation entry, ledger §2 style)

Two orthogonal fields replace the bundled prose claim. The existing
`Classification:` line is preserved verbatim as history (append-only
law); the new fields are appended per entry at adoption time.

### Field 1 — `Participation:`

How the mechanism demonstrably participates, on caller evidence only:

| Value | Meaning | Evidence required |
|---|---|---|
| `PRODUCTION_LIVE` | A production (non-test, non-proof) in-tree module imports/calls it on a user-reachable path | Caller file:line + entry-path trace |
| `PROOF_TEST_ONLY` | Imported/called only by proof, test, or invariant surfaces | Exhaustive import/caller search at a named main SHA |
| `CONTRACT_SOURCE_ONLY` | No direct caller, but it is the named source of a data contract (e.g. a score key) that other code consumes | Contract definition site + consumer site |
| `NO_CALLER_FOUND` | Search found no caller and no contract role | Same exhaustive search |
| `UNKNOWN` | Search incomplete, or external/dynamic producers cannot be excluded | Named gap in the search |

A mechanism may carry two values when both are demonstrated (e.g.
`PROOF_TEST_ONLY + CONTRACT_SOURCE_ONLY`). `UNKNOWN` is the default
for any entry that has not had its own caller-search receipt; absence
of a search is never recorded as `NO_CALLER_FOUND`.

### Field 2 — `Validation:`

| Value | Meaning |
|---|---|
| `VALIDATED` | Constants/formula derived or covered by a validation test in the repo |
| `UNVALIDATED` | Designer-chosen policy constants, no derivation, no validation test |

`Validation:` is **never derived from `Participation:`** and never
auto-converted. The historical token `ACTIVE_UNVALIDATED` maps, only
at a per-entry adoption ruling, to `Validation: UNVALIDATED` plus
whatever `Participation:` that entry's own evidence proves. No bulk
conversion.

### Field 3 — `Evidence:` (per field assignment)

`main <sha>` · search scope (static imports / call sites / dynamic
import scan / contract-key producers) · test receipts (suite + count)
· date. A field assignment without an evidence line is not adopted.

## Worked example — VERITA-JUDGE (EQ-VER-002/003/004), NOT adopted

Caller search executed by Uni 2026-11-17 at main
dc328b8d3ae0eb45136de2d8e1ed8dfceeaa04e3:

- Static imports of `form.dell_matrix.verita`: only
  `form/equation_ledger_invariants_test.py:22` (test),
  `form/mandell/p3_r34_geometry_proof.py:108,202` (proof),
  `form/dell_matrix/p3_wiring_test.py:79` (function-local, test).
  No production module imports it.
- `verita_of_one` / `verita_of_pair` / `VeritaField` call sites
  outside `verita.py`: only `p3_r34_geometry_proof.py` (proof). That
  file's comment cites a `brain.py` consumer; `brain.py`,
  `flash_path.py`, `matrix_awake.py`, and `free_matrix_150_audit.py`
  are all ABSENT repo-wide (find, 2026-11-17).
- Dynamic imports: no `importlib`/`__import__` path to verita found.
- Judge-dict contract: `form/dell_matrix/auto_growth.py:116` consumes
  `judge.get("verita_score")` at its MIN_VERITA gate (:39) but does
  not import or call verita.py (its header :13 says so); the only
  in-tree producers of `verita_score` dicts are test fixtures
  (`form/lineage_authority_test.py`,
  `form/dell_matrix/pp2_autonomy_charter_test.py`).
- Test receipts at dc328b8d, run by Uni this circuit:
  `form.equation_ledger_invariants_test` ALL PASS 14/14;
  `form.dell_matrix.p3_wiring_test` 26/26 PASS;
  `form.lineage_authority_test` 66/66 PASS.

Proposed assignment (for Keeper check, not adopted):
EQ-VER-002/003/004 → `Participation: PROOF_TEST_ONLY +
CONTRACT_SOURCE_ONLY`, `Validation: UNVALIDATED` (unchanged from the
current token's validation half). EQ-VER-001's participation follows
its delegated-canonical status (Q-S2R.1, PR #469) and is out of this
proposal's scope.

## Migration rules (proposed)

1. Per-entry only, each with its own caller-search receipt at a named
   main SHA. No repository-wide sweep converts entries in bulk.
2. Historical `Classification:` text is never edited; the new fields
   are appended (ledger append-only law).
3. Any entry whose producers may be external or dynamic defaults to
   `Participation: UNKNOWN` until the gap is named and closed.
4. Surfaces that report a verita value (firewall §8) label which
   mechanism they report; this schema does not rename any mechanism
   (renaming remains the separate R4-A2 / Q-S2R.4 scope).

## Scope / credits

Records only. No code changed, no ledger text changed by this PR, no
classification changed. No PLAN/CODE credit. Next: Keeper check of
this proposal; adoption, if any, is a Director ruling followed by a
per-entry append circuit. Q-S2R.3/R4-A7 (source-comment CODE circuit)
and Q-S2R.4 (seven-bearer naming-audit plan) remain separate.
