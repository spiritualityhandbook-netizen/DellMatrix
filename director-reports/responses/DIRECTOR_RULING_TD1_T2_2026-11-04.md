# DIRECTOR REVIEW — November 4, 2026

Mode D — TD-1 certification review and outstanding dispositions
(As forwarded by Ace. Verified main: 0bbefec · TD-1 frozen
candidate: b3ae6f1.)

## Five priorities delivered

GitHub confirms the completion and integration of the November 4
work.

| Circuit | GitHub result | Director review |
| --- | --- | --- |
| SM-54 | PR #276 merged | Studio Gap 3 closed |
| SM-39 | PR #277 merged | Growth persistence evidence accepted |
| TD-1 | PR #278 merged | Certification review below |
| SM-20 / SM-14 | PR #280 merged | Investigations accepted |
| SM-39 correction | PR #281 merged | Correction accepted |

The TD-1 frozen commit has completed-success GitHub Actions
records for the Python package, Form smoke, and Studio browser
acceptance. The submitted evidence also reports 24/24 targeted
checks and 232/232 regression suites in all three passes.

The implementation work is real. The remaining question is exactly
which guarantees the evidence proves.

## 1. TD-1 — accepted, certification deferred

The architecture is consistent with the authorization. The
targeted tests demonstrate valid bindings, persistence,
missing-target refusal, rollback, and sequential stale-instance
detection.

However, source review identified two remaining issues:

* Corrupt-state handling: _persisted_pointer() returns None when
  the persisted Program file is unreadable. The subsequent save
  does not itself validate that existing file. This creates a
  potential path for overwriting corrupt state.
* Concurrent binding: The conflict check occurs before Idea
  creation and Program save, without a lock or compare-and-swap
  guarantee. Two simultaneously binding instances could both pass
  the check. The existing test covers sequential staleness, not
  this race.

Evidence: unit_binding.py · TD-1 tests

Ruling: TD-1's demonstrated mechanisms are accepted. Full
concurrent-instance safety is not certified. These are
source-review findings requiring failing-first reproduction.
TD-2 remains unauthorized.

## 2. T2 — certification exception lifted within the repaired scope

Scoped certification granted.

The previously missing persistence evidence is now present, and
the implementation supports separate unit-ID-keyed growth records
surviving save/reload with their identities and stages intact.

**DIRECTOR RULING: CERTIFIED WITH NOTED EXCEPTIONS.**

The identical-label limitation is lifted for the tested
unit-ID-keyed growth path, including its persistence round-trip.

Retained boundaries: legacy label-only ambiguity, unrelated
ForceField losses, Exchange transport, and untested execution
paths. The correction addendum is accepted and supersedes the
false comparative claim in the original report.

## 3. B-2 and SM-20 — investigation dispositions

B-2: The 71-unreachable claim is retired. Accept the reproducible
bounded finding of 37 reachable and 63 with no route found by the
disclosed probe battery. Authorize deeper per-Dell reachability
validation before promoting any of the 63 into an implementation
queue. Do not equate a missing probe result with proven
impossibility.

SM-20: Investigation accepted. The unsupported-argument refusal
diagnostics are names-only, but the universal result seed echo
retains caller-supplied values. Unparseable input can also enter
the separate unknowns ledger, and explicit Exchange exports carry
seed content. No redaction implementation is authorized from this
investigation alone.

## 4. ForceField — sibling defects confirmed

The correction establishes additional serialization/restoration
asymmetry. Water records and stream IDs have the most immediate
identity risk.

Director disposition: Authorize one bounded Water persistence
repair after TD-1-R1. Preserve stream/pool relationships and
ensure identifiers are not reused after reload. For gravity
wells, the preferred subsequent design is to restore the already
serialized records as saved snapshots, then allow normal
score-based recomputation on future ticks. Evolution scalar
restoration also requires regression tests. No combined repair
is authorized yet.

## Next directive — TD-1-R1

MODE C · TARGET: TD-1 conflict and corruption guard

Finding: Current source does not prove fail-closed corrupt-state
behavior or simultaneous-writer safety.

Repair: Introduce an enforceable owner-state concurrency guard or
atomic version check across binding validation and save. Refuse
unreadable persisted state before minting. Reconcile existing
in-memory pointers against canonical persisted pointers.

Verify: Failing-first corrupt-file and overlapping-writer tests,
no silent overwrite, zero graph writes, full regression ×3,
exact-head CI, and fresh-clone verification.

Stop: Submit a frozen candidate and independent evidence. Do not
expand into containment or TD-2.

Program status: The November 4 priorities have produced real,
merged improvements. The next work is targeted closure of two
TD-1 guarantees, not another broad redevelopment cycle.
