# DIRECTOR REPORT — Snapshot retrieval repair (Q-SC.3 as amended): coverage truth, bounded retrieval, cross-process source identity, lifecycle revalidation

**Circuit status: BUILD + EVIDENCE COMPLETE — certification requested
(Q-SNAP.1). Director-authorized implementation (08:08 CST ruling,
Gmail 1a1bb7d8dde15388, Q-SC.3, as amended in the Mode D review and
restated in the 15:38 CST ruling, Gmail 1a1bd1931ed0e054, archived
with this PR). No new 72-objective completion is claimed; strict
confirmed remains 19/72.**

## 1. The defect (verified at base 61f10b3)

`AgentCoordinator.snapshot_for` sliced the FIRST 200 Nursery
proposals and the FIRST 200 Plane units, in collection order, and
returned no coverage counts, no truncation marker, no source
identity, and no retrieval path. Dock verbs resolve targets only
from that snapshot, so any idea past position 200 was unreachable
(`unknown_target`) no matter how legitimate the request. Proven
live in the Email Matrix field (1,052 units): the DistroKid
payment-decline target sits at position 219 and was omitted, while
the Stripe target at position 107 was present — the pair was
unrelatable through the verbs. Failing-first suite result at base:
**2/16** (the two control checks pass; all 14 defect checks fail).

## 2. The repair (one bounded circuit, as amended)

- **Coverage truth.** `snapshot_for` now returns a coverage block
  — `ideas_total`, `ideas_returned`, `units_total`,
  `units_returned`, `truncated` — computed over the FULL
  collections, so a caller can always see when it is looking at a
  window rather than the field.
- **Trustworthy cross-process source identity.** The snapshot
  carries `source_identity`: a deterministic digest over the full
  source collections. It is NOT a runtime generation counter (the
  amendment explicitly superseded that design): the same identity
  is computed by a separate OS process over the same source state,
  and it changes when the source content changes (proven by the
  cross-process and stale-source checks).
- **Bounded retrieval.** `retrieve_for` fetches caller-named
  stable IDs beyond the slice: at most **16 IDs per round**,
  duplicates deduped, absent IDs reported as absent (never
  invented), and every returned record passes the SAME outward
  sanitization as the snapshot (inside/outside-slice twins proven
  equal).
- **One retrieval round + lifecycle revalidation in the dock.**
  When a dock verb's target is missing from the snapshot,
  DockedSession performs ONE retrieval round, then revalidates
  the target's lifecycle before incorporation: changed content,
  deletion, fading, and supersession are refused honestly rather
  than incorporated stale (deletion check: a deleted target is
  refused as `unknown_target`, not resurrected).
- The suite `form/snapshot_retrieval_test.py` (16 checks: control
  + T1–T7 incl. cross-process identity, duplicate IDs, hard bound
  with no partial result, lifecycle parity, deletion
  revalidation) is registered in `form/regress.py` — the
  canonical suite count moves 259 → 260.

## 3. Evidence

- Failing-first at base 61f10b3: **2/16** (controls only).
- Post-repair: **16/16 PASS** at the branch head — re-verified
  terminally by the 20:01 CST cycle in a clean clone, and again
  16/16 by the main session after rebase onto current main
  (fa2f9c4; the rebase moved no product code — main advanced by
  docs-only PRs #334/#335).
- Mutant: with the dock retrieval round disabled, the suite falls
  to **12/16** — the retrieval checks kill the mutant.
- Neighbour suites (cycle-verified): p5_sd2 24/24, track_c 29/29,
  p7_sd4 17/17, p4_sd1 19/19.
- Full regression ×3, main-session chain at head 36d1231 (the
  pre-rebase implementation commit; code-identical after rebase):
  **260/260 GREEN in all three legs** — forward, `--twice`,
  `--order rev` — chain 22:47→23:22 CST 2026-11-08, RC=0 ×3.
  Logs: `director-reports/evidence/snapshot-retrieval/`
  (chain.log, leg1.log, leg2.log, leg3.log).
- Disclosure (process slip, Uni's): during this circuit's mutant
  step, the mutant was initially reverted with `git checkout --`
  on uncommitted work — the forbidden pattern (AGENTS working
  rules). The affected work was rebuilt from scratch and
  re-verified before commit; no unverified code rides this PR.

## 4. Limits (unchanged from the authorization)

- The guarantee is RETRIEVAL REACHABILITY of caller-named stable
  IDs — not exhaustive enumeration and not pairwise coverage.
  Candidate search remains snapshot-bounded and discloses its
  coverage via the coverage block.
- One retrieval round per verb resolution; the 16-ID bound is a
  hard refusal with no partial result.
- No other snapshot consumer (e.g. Studio views) changed behavior
  in this circuit (see Q-SNAP.2).

## Anticipated probes

- *"Is source_identity just the generation counter renamed?"* No.
  The suite computes identity in a separate process over the same
  persisted source and requires equality, and requires it to
  CHANGE after a source edit — a per-process counter fails both.
- *"Can retrieval bypass lifecycle or authorization?"* The checks
  prove parity: retrieved records pass the same sanitization, and
  faded/replaced/deleted targets are refused at revalidation,
  inside and outside the slice alike.
- *"Why is the regress cited at the pre-rebase head?"* Because
  that is the head it ran at (36d1231). The rebase onto fa2f9c4
  touched no product code (docs-only main movement), the full
  suite re-ran 16/16 post-rebase, and this PR's own exact-head CI
  re-proves the tree before merge.

## Questions for the Director

- **Q-SNAP.1** — Certification requested for the bounded Q-SC.3
  repair as scoped above (coverage truth + bounded retrieval +
  cross-process source identity + lifecycle revalidation).
- **Q-SNAP.2** — Should the same retrieval reachability be
  extended to other snapshot consumers (Studio views) as a
  separate circuit, or is the dock-verb scope the intended final
  boundary for v1?
