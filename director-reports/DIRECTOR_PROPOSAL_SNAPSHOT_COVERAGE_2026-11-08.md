# DIRECTOR PROPOSAL — Snapshot coverage: bounded retrieval / paging beyond position 200 (2026-11-08)

Status: PROPOSAL ONLY — prepared under the Director's
authorization to prepare and publish (Email Matrix review,
2026-11-08). No implementation. Implementation ruling follows
this concrete scope.

## 1. THE DEFECT, MEASURED

`AgentCoordinator.snapshot_for` (form/dell_matrix/
agent_coordinator.py:109-110, 686+) builds the docked model's
field view as the FIRST 200 Nursery proposals and FIRST 200
Plane units, sliced separately in collection order. It exposes
no coverage counts, no truncation marker, and no way to request
any other window. The semantic verbs (relate / synthesize /
relate_field / comprehend) resolve targets and candidates ONLY
inside that snapshot.

Live measurement (Email Matrix, owner EMAILFIELD8B0610,
1,049 units at the relate run): snapshot = 200 units + 200
ideas. The DistroKid target `problem_with_your_distrokid__1598`
sits at collection position 219 → `relate_field` returned
`unknown_target` for an idea that exists and is authorized.
All 8 DistroKid-labeled units (positions 219–350+) were
invisible. Raising the cap cannot fix this class: any fixed
cap N leaves position N+1 unreachable, and prompt budgets
forbid unbounded snapshots.

## 2. INTENDED GUARANTEE (recorded, per the directive)

**Retrieval reachability.** Any single authorized idea (unit or
proposal) in the owner's field is reachable by its stable ID
for target resolution and relation judgment, regardless of its
collection position. Relations may span windows (one target
inside the default slice, one retrieved).

Explicitly NOT claimed: exhaustive enumeration of the corpus
inside one prompt, and NOT exhaustive pairwise comparison.
Whole-corpus pairwise relation remains a batched, host-driven
process (as the Email Matrix relate pass already is), not a
snapshot property.

## 3. DESIGN (bounded; one PR when ruled)

D1. **Coverage block in every snapshot.** `snapshot_for` adds
`coverage: {units_total, units_returned, ideas_total,
ideas_returned, truncated: bool, generation: int}`. Consumers
(and receipts) can finally state what the model could see.
No behavior change to the slices themselves.

D2. **Scoped retrieval call.** A coordinator method
`snapshot_for(..., include_ids=[...])` — or a sibling
`retrieve_for(subject, ids)` — returns sanitized entries for
explicitly requested stable IDs (bounded: ≤ 16 IDs per call,
same per-entry bounds as the snapshot), each marked
`source: "retrieved"`. DockedSession's target resolution for
the semantic verbs consults the default snapshot first, then
ONE retrieval round for unresolved target IDs named by the
caller (the human/host names the IDs; the model does not gain
search authority). Candidate pre-filtering for relate_field
stays snapshot-bounded in v1 (recorded limit).

D3. **Stable IDs + stale-snapshot handling.** Every snapshot /
retrieval response carries the field `generation` (a counter
incremented on any Plane/Nursery mutation of that owner —
confirm, reject, add, delete). A verb receipt records the
generation it judged against; a confirm that lands against a
changed generation re-validates the proposal's parents at the
existing confirm boundary (which already re-checks parentage)
and otherwise proceeds — no new lock, no second authority.

D4. **Preserved boundaries (non-negotiable in the design).**
Outward sanitization applies to retrieved entries identically
(snapshot_for's fail-closed sanitization path is reused, not
re-implemented). Owner/agent authority unchanged: retrieval is
scoped to the requesting agent's own owner field; unknown or
cross-owner IDs return absent, never data. Lifecycle
eligibility unchanged: retrieved PENDING proposals are
judgeable; faded/superseded/confirmed handling matches the
existing snapshot rules. Pending-until-human-approval is
untouched: retrieval changes what the model can SEE, never
what it can apply.

## 4. FAILING-FIRST TESTS (written before implementation)

New registered suite (form/regress.py), disposable owners,
scripted provider + one real-shaped provider case:

- T1 (reachability): build a field of 250 units; target the
  unit at position 240 by ID through relate_field → lands
  PENDING. Fails-first today with unknown_target.
- T2 (cross-window relation): target A inside the slice,
  target B beyond it; synthesize([A, B]) lands PENDING with
  parents exactly [A, B]. Fails-first today.
- T3 (coverage truth): snapshot coverage counts equal the
  live census (units_total / ideas_total exact; truncated
  true when totals exceed returns). Fails-first today (no
  coverage block exists).
- T4 (sanitization parity): plant a protected-material canary
  in a beyond-200 unit's detail; retrieval of that unit shows
  the screened form (or refuses), never the canary.
- T5 (authority): retrieval of a nonexistent ID and of
  another owner's ID both return absent; no data leaks; the
  verb reports unknown_target for them.
- T6 (lifecycle parity): a faded/superseded beyond-200 entry
  is excluded exactly as its in-slice twin is.
- T7 (staleness): mutate the field between snapshot and verb
  call; the receipt records the pre-mutation generation and
  the confirm boundary re-validates parents (stale parent →
  honest refusal, not a corrupt apply).
- Regression: r62 + p5 dock suites, SD suites, full regress
  ×3 sequential; harness count +1 for the new suite.

## 5. COST / RISK NOTES

- Prompt size stays bounded: retrieval adds at most 16
  bounded entries to a verb call; default slices unchanged.
- No persistence format change; generation is runtime state
  derivable from the existing mutation points.
- The one new surface is read-only visibility for the dock —
  no new write path, no new authority.

## Questions for the Director

- Q-SC.1: Is retrieval reachability (§2) the intended
  guarantee, or is exhaustive enumeration also required?
- Q-SC.2: D2's one-retrieval-round limit for caller-named
  target IDs — acceptable, or should relate_field's candidate
  pre-filter also page (larger scope)?
- Q-SC.3: Authorize implementation as one FIX circuit at T2
  evidence tier on ruling?
