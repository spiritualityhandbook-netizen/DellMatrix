# R6.5 COMPLETION PACKET — Separation Enforcement (AMEND-6)

**Directive:** GDP_PHASE_6_R65_SEPARATION_ENFORCEMENT (MODE=C)
**AMEND Directives:** COMPLETE_REAL_SEPARATION_CIRCUIT → FINISH_EXISTING_EXECUTABLE_PROOF → FINISH_NONVACUOUS_EXISTING_CONTROLS → COMPLETE_ASSERTIONS_WITH_CANONICAL_EVIDENCE → CLOSE_REPORT_TO_CODE_DISAGREEMENT
**AMEND-6 Directive:** GDP_R65_FINISH_EXISTING_ISOLATION_AND_RETURN_FOR_ADMISSION (MODE=C)
**Authorization:** GDP_R65_AUTHORIZATION_RECONCILIATION (2026-10-09 16:17 CDT)
**Date:** 2026-10-09
**Status:** CANDIDATE READY FOR DIRECTOR REVIEW (NOT CERTIFIED — DO NOT MERGE)

## Exact Identity

- **Branch:** `gdp-phase6-r65-separation`
- **Head:** `05c256f08407b4ba2e142d62a96d8e801481a8b5`
- **Tree:** `8698039d8f85087ad44ad6d5305de4492905de6f`
- **Base:** `0ceb3113beb8ce93e6bca422b9bddad12984feac` (R6.4 MERGED)
- **Base tree:** `7ab8c67b1a4ba742fb971d7039ac5b3755366cd5`

**Historical identities:**
- AMEND-3: `4e196a8` / `c452167`
- AMEND-4: `fcf22d9` / `d876929`
- AMEND-5: `2daec8f` / `891dea4`

## Objective → Owner → Evidence Map

| # | Objective | Owner (R6.1–R6.4) | Evidence |
|---|-----------|-------------------|----------|
| 6.5.1 | PERSONA != PERMISSION | `agent_coordinator.py` (R6.4) | Behavioral: matched requests before/after persona change; canonical state unchanged |
| 6.5.2 | BIMO = descriptive, not authority | `personas.py` (presentation) + `acceptance_policy.py` (R6.1) | `effective_capabilities` labeled presentation-only; labels != grants proven |
| 6.5.3 | PERSPECTIVE != TRUTH | `perspective_views.py` + coordinator snapshot (R6.4) | View mutation does not touch canonical; exact pid keys used |
| 6.5.4 | Behavior != authority | `agent_authority.py` (R6.2) + coordinator (R6.4) | Unauthorized confirm denies; agent cannot mint authority |
| 6.5.5 | Human sovereignty | `acceptance_policy.py` (R6.1) via grant issuance | Every protected op requires host-issued grant |

## Sensitivity (Real, Executed)

Three independently prepared equivalent PENDING fixtures (UUID owners).

**Before EACH attempt:**
- Assert `prop.status == "pending"` (exact)
- Assert `pid not in program.cube.session.plane.units` (exact absence)

**Normal/Restored denial:** Must deny; reassert both conditions after.
**Weakened success:** Assert `status=="confirmed"` + exact unit via `plane.units[pid]`.

## Audit Preservation (Executed)

- Capture SPECIFIC committed record (request_id="r65-restart-confirm", result="committed").
- Require nonempty; do NOT swallow errors.
- Both children compare: request_id, subject, target, AND result.
- Negative controls: empty expectations fail; changed result fails.

## Restart (Real, Two Children)

**Child 1 (mutating):** Fresh OS process. Denies old grant, reissues, confirms, saves.
**Child 2 (verification-only):** Separate OS process. No mutation. Verifies exact Idea, proposal, audit.
Both require `returncode==0`.

## Isolation (AMEND-6)

**Mechanism:** Disposable repository copies. No guessed file deletion.

1. **Via form.regress:** The regression runner copies the entire source tree to a
   private temp directory (`tempfile.mkdtemp(prefix="dm_regress_")`), runs tests
   with cwd in the copy, then removes via `shutil.rmtree`. All `form/state/`
   writes go to the copy. (See `form/regress.py::_copy_tree`.)

2. **Direct execution:** `main()` detects if not in an isolated copy (via
   `.dm_regress_copy` or `.r65_isolated` markers). If not, creates a disposable
   copy via `tempfile.TemporaryDirectory(prefix="r65_isolated_")`, copies the
   repo (excluding `.git`), marks with `.r65_isolated`, re-executes the suite
   there with `PYTHONPATH` set. `TemporaryDirectory` cleanup failures propagate
   as exceptions (not swallowed).

**Per-case uniqueness:** Each test case uses UUID-suffixed owners
(e.g., `r65s1_a1b2c3d4`) to prevent collision within the isolated environment.

**Proof:** Suite executed twice; sentinel files in `form/state/` unchanged;
no test artifacts leaked to the original repo; temp directories removed.

**Limits:** Isolation is at the filesystem level (disposable copies). The test
does not redirect production `_STATE_DIR` (hardcoded in `form/persist.py`);
instead, it runs in a copy where `form/state/` is fresh. This does not alter
production persistence architecture.

## Delta-20

All 20 established categories mapped. See `R65_RESEARCH_DELTA20.md`.

**Re-examined for AMEND-6:**
- **Contradiction:** The previous packet claimed "canonical cleanup for every
  case" while code used guessed globs with swallowed failures. This contradiction
  is resolved: packet now describes disposable-copy isolation accurately.
- **Persistence:** Test artifacts are confined to disposable copies; production
  `form/state/` is not modified by the suite. Verified via sentinel test.
- **Public-path evidence:** The suite runs via `form.regress` (public regression
  entry) and via direct `python3 form/mandell/r65_separation_test.py` (which
  self-isolates). Both paths verified.
- **Recovery/failure handling:** Cleanup failures propagate via
  `TemporaryDirectory` (no `except Exception: pass`). Behavioral failures are
  preserved and reported; cleanup errors would also fail the test with explicit
  diagnostic.

Other categories retained where unaffected by the isolation correction.

**Note:** Research records ADAPT/REJECT dispositions. Primary-source citation
verification was limited; do not overstate.

## Verification

- `python3 form/mandell/r65_separation_test.py`: **72/72** (in isolated copy)
- `python3 -m form.regress --twice`: **111/111 GREEN**
- `python3 -m form.regress --order rev`: **111/111 GREEN**
- Exact-head CI: [pending push]

## Costs

- 1 presentation utility (`effective_capabilities`, labeled non-enforcing)
- 1 test file (72 checks) + 2 child scripts
- Documentation files
- Zero changes to R6.1–R6.4 runtime behavior (additive only)

## Limits

- Single-host enforcement (per R6.4; no distributed).
- Human sovereignty via trusted-host grant issuance.
- Does not cover UI/UX, distributed systems, or Phase-7.
- Scanning: EVALUATION_UNAVAILABLE (Copilot quota 402).
- Performance: no measured baseline.

## Authorization

- **Implementation:** GDP_PHASE_6_R65_SEPARATION_ENFORCEMENT (MODE=C), 2026-10-09 15:10 CDT.
- **Reconciliation:** GDP_R65_AUTHORIZATION_RECONCILIATION, 2026-10-09 16:17 CDT.
- **AMEND-6:** GDP_R65_FINISH_EXISTING_ISOLATION_AND_RETURN_FOR_ADMISSION (MODE=C).
- **Record:** `R65_AUTHORIZATION.md`; ledger.

---

**END OF R6.5 COMPLETION PACKET (CANDIDATE)**
