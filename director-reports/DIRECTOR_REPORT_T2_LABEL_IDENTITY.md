# DIRECTOR REPORT — T2 label identity: ambiguous plant keys

**Status: SUBMITTED for Director ruling. Nothing certified by
submission. Merged != certified.**

## Ruling requested / scope identity / exceptions FIRST

- **Scope:** form/dell_matrix/view_rooms.py growth-room lens
  only (plus its suite). Follow-on to the T2 WIRE disposition
  the Director accepted in principle in DIR-2026-11-02-R1,
  executing R1 Priority 3. GrowthForce (forces.py) is NOT
  modified; no competing growth engine is introduced.
- **Ruling requested:** certify (or decline) the bounded claim:
  *when the truncated plant key (label[:80], the only textual
  identity plant() stores) cannot pick out one node — distinct
  full labels in the node list collapse to it, or the supplied
  plants disagree on its stage — the growth lens reports
  stage=None with stage_source="ambiguous" instead of
  attributing one plant's stage to another node. Unique labels,
  agreeing duplicate plants, and identical-label duplicate
  nodes resolve exactly as before.*
- **Exceptions / non-claims:** T6's focus_areas contract is
  separate and untouched. Whether GrowthForce.plant should
  also retain the full idea is posed as Q1 below, NOT done —
  it changes the canonical growth record's shape.
- **Evidence accessibility (R1 Priority 2 pattern):** raw
  evidence in-repo at `director-reports/evidence/t2label/`
  (probe source, pre/post-fix outputs) with SHA-256 digests
  below.

## The defect (Director's scenario; reproduced before fixing)

plant() stores idea=label[:80]. The lens matched nodes to
plants by that key, first-wins. Probe at base ec78242 (real
GrowthForce, plant grown to "branch"):
- node A (the planted label): branch / growth_force — correct.
- node B (a DIFFERENT label sharing the 80-char prefix, never
  planted): branch / growth_force — one plant's stage
  attributed to another node, presented as authoritative.
- Plants disagreeing on one key (seed vs branch), single node:
  seed / growth_force — first-wins coin-flip presented as fact.

## Fix

View layer only: plant keys truncated symmetrically; a key is
ambiguous when the supplied plants conflict on its stage or
2+ distinct full labels in the node list collapse to it;
ambiguous keys yield stage=None / stage_source="ambiguous".
All other resolution paths byte-identical in behavior.

## Tests

- Suite form/mandell/view_rooms_growth_test.py: 9 preserved
  checks untouched + part_ambiguous (6 checks): truncation
  witness; collided planted node claims no stage; sibling
  cannot steal; plant-conflict ambiguous; agreeing duplicates
  resolve; identical-label duplicates resolve. 15/15.
- Mutant (ambiguity branch disabled): 12/15 — failures exactly
  the 3 honesty checks, with the stolen values visible
  (branch/growth_force, branch/growth_force, seed/growth_force).
  Reverted by inverse edit; tree verified identical.
- Full regression on c64478c: 221/221 x3 (forward / --twice /
  --order rev). Exact-head CI on c64478c: COMPLETE SUCCESS
  (Python package 41459367883; Form smoke 41459367895).
  Merged as 7486963 (PR #220); the merged tree's form/ content
  is identical to the candidate's (the only delta vs the
  candidate tree is PR #219's director-reports corrections,
  merged in between). Fresh-clone at 7486963: probe PASS;
  regress 221/221 GREEN (first attempt reached 200/221 with
  zero failures before a VM replacement killed it — NO RESULT,
  re-run in full).

## Evidence files (director-reports/evidence/t2label/)

| ID | File | SHA-256 (first 16) | What it shows |
|----|------|--------------------|----------------|
| E1 | probe_prefix_output.txt | 15bf21eb0fd8833f | failing-first at ec78242 |
| E2 | probe_postfix_output.txt | 246a6b9e8cf72bee | passed-after at merge 7486963 (fresh clone) |
| E3 | t2label_probe.py | f852ef88ecf2f5e1 | the probe source (repo root resolved from its own path) |

Environment limits: pure-Python lens fixtures plus the real
GrowthForce; no process or timing surface. The production-path
checks (Program.view_status) remain in the suite, unchanged.

## Anticipated probes

- "Does ambiguous hide a stage the node legitimately owns?"
  Yes, deliberately: when two distinct labels share a key, the
  lens cannot prove which node the plant belongs to — even the
  truly-planted node reports ambiguous. That is the honest
  price of the truncated store; Q1 is the structural remedy.
- "Two plants, same key, same stage, two colliding nodes?"
  Still ambiguous (node-side collision is independent of plant
  agreement): the stage value would coincidentally match, but
  the node↔plant identity remains unprovable.
- "Callers passing plant dicts with full-length ideas?" Plant
  keys are now truncated symmetrically ([:80]) so hand-built
  fixtures behave like real plant() records.

## Questions for the Director

- Q1: Should GrowthForce.plant retain the full idea (e.g. an
  additional idea_full field alongside the truncated display
  key) so future views can match exactly and retire most
  ambiguity? Uni did not do it under P3: it changes the
  canonical growth record's shape and every consumer of
  plant["idea"] must be re-audited.
- Q2: Is the node-side rule (collision => ambiguous even when
  all candidate plants agree on stage) the intended honesty
  boundary, or should agreeing-stage collisions resolve?
