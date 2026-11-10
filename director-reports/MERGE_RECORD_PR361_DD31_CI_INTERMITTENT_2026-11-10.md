# MERGE RECORD — PR #361 / DD31-CI-INTERMITTENT (test-oracle flicker)

**PR**: #361, branch uni/dd31-residue-scope
**Candidate head**: ec82f4a500bba294790937bfc3781d792dd88d5a
**Merged**: 2026-11-10T16:51:29Z as **c13de21e70142bb368ab59c6df39a9e3ab002ff8**
**Actor**: Uni main session (gh pr merge). Merges execute only from the
main session (WORKFLOW v1 SS3 step 9).

## Scope (exactly this, nothing more)

Test-oracle correction in `form/dd31_sanitize_copula_test.py`: the
suite's final residue check previously scanned the WHOLE shared
`form/state` directory for any filename containing the substring
"dd31"; it now checks only the suite's own owner's files. Plus the
circuit's Director report and INDEX row. **Certified DD-31 redaction
product code was NOT touched** (diff-verified by the main session).

## Mechanism (proven, not inferred)

Other suites create state files with random/uuid-derived names; when
such a name contains "dd31", the whole-directory substring assertion
failed the dd31 suite 20/21 blaming a bystander file. Planted-file
differential: plant a foreign "dd31"-named file -> 20/21; remove it ->
21/21; the suite's own genuine residue still fails the check
(positive control). This explains every historical datapoint: fwd/
twice CI passes accumulate foreign residue, rev order and isolated
local runs do not; the E1/E2 bisections never generated a colliding
name. Root cause identified in a live session under Ace's direction,
2026-11-10.

## Decision trail

- Director SCOPED PASS + CONDITIONAL MERGE AUTHORIZATION (Gmail
  1a1c621ed9443fd2, 2026-11-10 09:43 CST) with named preconditions.
- Local full regression at the exact head (main session, durable
  logs dd31oracle_logs/): fwd 264/264 GREEN; twice pass1 264/264 +
  pass2 264/264 GREEN; rev 264/264 GREEN. Counts published on the PR
  (comment 6773452477) before merging.
- Keeper/Grok scoped CONFIRM (record commit ba6609a on main) +
  Director SCOPED CONFIRM / Q-DD31F.1 ACCEPTED with conditional merge
  clearance (Gmail 1a1c64a00d33ebc2, 2026-11-10 10:28 CST), read in
  full by the merging session.
- SS32 transaction executed IN THE SAME STEP as the merge: triage
  newest Director mail = the 10:28 authorization itself; no Keeper
  mail outstanding; head unchanged ec82f4a; mergeable MERGEABLE/CLEAN;
  merge-tree vs main CLEAN; all exact-head checks terminal PASS.

## Merged-main verification (terminal)

Fresh clone of merged main: dd31 suite **21/21**; full forward
regression **265/265 GREEN** (logs: dd31oracle_logs/merged_main/).
Item state (WORKFLOW v1 SS4): lifecycle MERGED_VERIFIED;
certification — this closure is an oracle-reliability closure, NOT a
product Sanitize recertification; final-check PENDING until an
authority hourly pass clears it; blockers none.

## Closure and scoreboard

**DD31-CI-INTERMITTENT: CLOSED** (test-oracle defect class). It is an
extension-register reliability closure, not one of the 72 objectives
and not one of the 12 fixed defects below.
**Defect dial, restated authoritatively by this record: FIXED 12**
(DD-01, DD-02, DD-03, DD-04, DD-05, DD-09, DD-10, DD-11, DD-12,
DD-13, DD-18, DD-42) / **GATED 3** (DD-06 everyday-save pair -> C-A;
DD-07 Q1 family; DD-08 72-16 divergence). Earlier register statements
reading 10 or 11 FIXED are superseded by this restatement.
**Strict completed objectives: 19/72 — unchanged.**

## Trailing / next

- Q-DD31F.2: bounded sibling whole-directory-assertion inventory
  (separate hygiene circuit, Director-favored).
- DD-31 cascade continues: PR #350 rebase onto post-#361 main, then
  PR #360; PR #348/#345 each require their own refreshed exact-head
  dispositions (Director, 10:28 mail) — no automatic cascade.

— Recorded by Uni, 2026-11-10.
