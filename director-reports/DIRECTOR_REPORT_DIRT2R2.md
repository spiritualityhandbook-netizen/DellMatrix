# DIRECTOR REPORT — DIR-T2-R2: plant-to-node identity in the growth lens

**Status: SUBMITTED — awaiting Director ruling (not certified).**
Responds to: DIR-2026-11-02-CONSOLIDATED-R1, new finding
DIR-T2-R2 (execution order #1), applying C-Q3 (design approved)
and C-Q4 (ambiguous accepted).

## Ruling requested

Certify (or decline) the bounded claim: in the growth lens, a
GrowthForce stage is attributed to a node ONLY where
plant-to-node identity is proven — exact identity retained at
the canonical plant owner (`idea_full` alongside the truncated
display key), proven-identity matching in the visual consumer,
legacy records held to prefix-only ambiguity, and one plant
record per exact identity at the owner. Scope: the DIR-T2-R2
counterexample class (omitted-node stage theft through a
shared 80-char prefix) plus the identity cases enumerated in
the suite. No claim is made about identical-full-label units
(see Limits).

## The defect (as found)

At 067ca1e, `GrowthForce.plant` stored only `idea=label[:80]`;
the lens matched plants to nodes by that truncated key and the
T2 detector marked ambiguity only for labels visible in the
supplied node list. The Director's counterexample — plant A
grown to branch, supply ONLY unplanted node B sharing A's
prefix — silently presented A's stage as B's `growth_force`
fact. Reproduced by executed failing-first probe at 067ca1e
(probe_prefix_output.txt: B got stage='branch', source='growth_force').

## The fix (one implementation change)

1. `form/dell_matrix/forces.py` — `GrowthForce.plant` (the
   canonical plant owner) retains the exact identity as
   `idea_full` next to the unchanged truncated display key,
   and returns the existing record when the same exact
   identity is re-planted (one identity = one record; the four
   production dedupe sites that compare full labels against
   truncated keys would otherwise mint divergent duplicates
   of long-label plants on every invocation).
2. `form/dell_matrix/view_rooms.py` — the growth lens matches
   by proven identity only: idea_full == node label resolves
   (agreeing exact plants resolve; disagreeing -> ambiguous);
   a plant whose idea_full differs from the node's label is
   provably another unit's and contributes nothing (node
   reports "unplanted"); a legacy plant without idea_full
   resolves exactly only where its stored key equals the
   node's full label and is prefix-only "ambiguous"
   everywhere else, regardless of stage agreement (C-Q4).
   The lens still only READS GrowthForce records — no
   view-owned growth mechanism was introduced.

Migration/consumer analysis (C-Q3 precondition) is in the
packet and evidence bundle: persisted ForceField state stores
growth counts only, so no on-disk plant records required
migration; legacy in-process/hand-built records keep working
under the conservative rule; existing growth history and the
display key are untouched.

## Evidence (bundle: director-reports/evidence/dirt2r2/)

- Failing-first probe at 067ca1e: 0/5, exit 1
  (probe_prefix_output.txt). Post-fix: 5/5, exit 0
  (probe_postfix_output.txt). Probe source: dirt2r2_probe.py.
- Suite form/mandell/view_rooms_growth_test.py: 26/26
  (13 unchanged preserved checks; 2 checks with verdicts
  legitimately changed by provable identity, justified in the
  packet; 11 new R2 checks including the Director's
  counterexample, the legacy rule, C-Q4, both-visible own-plant
  resolution, owner idempotence, and a Program/view_status
  production-path case).
- Defect-restoring mutant (pre-fix 067ca1e lens branch
  restored verbatim): probe 1/5, suite 17/26 — failures
  exactly the 9 R2 attribution checks, with the theft visible
  (B = 'branch'/'growth_force') in lens, legacy, and
  production cases (mutant_output.txt). A partial mutant
  (lens ignores idea_full only) scored probe 3/5, suite 20/26
  (mutant_partial_output.txt).
  Mutants reverted by inverse edit; tree verified identical
  to the fix commit.
- Full regression ×3 on fix commit ab0a897: 221/221 GREEN
  each leg (forward / --twice / --order rev, sequential; zero
  FAIL lines; growth suite 26/26 inside every leg).
- Exact-head CI on ab0a897: COMPLETE SUCCESS (Python package
  run 41486068793; Form smoke run 41486068804), verified from
  terminal gh output in a separate step after the PR opened.
- Merge: PR #225 merged as
  c3cc550c3eee0033db7818266c3d4f39171b276c; the merged tree's
  form/ content is identical to the candidate's (only delta:
  PR #224's response-archive file). Fresh clone at c3cc550:
  probe 5/5, regression 221/221 GREEN, exit 0.

## Anticipated probes

- "Does B-alone now report ambiguous instead?" No: with a
  full-identity plant the verdict is "unplanted" — the only
  plant is provably A's. With a LEGACY record it is
  "ambiguous". Both are in the suite.
- "Can a legacy record still steal a short label?" Only where
  stored key == node label exactly (the C-Q3 constraint-(b)
  rule); an exactly-80-char legacy key is indistinguishable
  from a genuine 80-char label — disclosed under Limits.
- "Did plant() idempotence change any other behavior?"
  grow_all/map/status/to_dict read only stage/idea/height;
  no suite in the full regression depends on duplicate
  appends (regression results above).

## Limits (stated, not hidden)

- Identical full labels: two distinct units sharing one
  identical label remain ONE lens identity. No canonical unit
  id reaches the lens boundary (nodes carry plane ids, plants
  carry no unit id), so C-Q3's preferred ID matching is not
  available at this boundary today; full-label identity is
  the strongest provable identity here.
- Legacy exactly-80-char corner as above; every post-fix
  record carries idea_full and closes it.

## Questions for the Director

- Q1: Is the "unplanted" verdict for the full-identity
  omitted-node case (vs "ambiguous") the intended reading of
  the closed supplied-plants universe? (Dissent recorded in
  the ground document; Uni ruled "unplanted" on T2's existing
  contract.)
- Q2: Should a future circuit wire canonical unit ids into
  plant records (planting from plane units) to close the
  identical-label limit, or is full-label identity the
  accepted boundary for the growth lens?
