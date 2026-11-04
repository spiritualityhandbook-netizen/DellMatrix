# DIRECTOR REVIEW — TD-1-R1

Mode D | PR #283 | Main 6f1f651
(As forwarded by Ace.)

## R1 repair accepted within verified scope

The reviewed code closes both previously identified defects in
the tested paths.

* F1 — Corrupt state: Refusal occurs before Idea creation,
  preserving the damaged file.
* F2 — Intervening saves: SHA-256 fingerprints detect changes
  before the commit gate. The deterministic overlapping-writer
  test proves that the losing bind does not overwrite the winner
  in that tested interleaving.
* Regression: The report records 10/10 new checks, 24/24
  original TD-1 checks, and 233/233 x3.

The remaining limitation is material: the fingerprint comparison
is separate from the final file replacement. Two writers can
both pass the comparison before either saves. This is an
optimistic version check, not a fully atomic compare-and-swap.

Therefore, the repair is accepted, but unrestricted
concurrent-writer safety is not certified.

## Director decision

TD-1 certification: DEFERRED on the final concurrency guarantee.
No further changes are required for F1 or for the already-proven
F2 interleaving.

TD-2: Implementation remains unauthorized until the
concurrent-write guarantee is closed. The previously authorized
Water persistence repair may proceed independently.

## Directive — TD-1-R2

TARGET: Atomic owner-state commit protection.

Repair: Protect validation and final replacement within one
enforceable owner-scoped transaction. Ensure ordinary Program
saves cannot bypass the protection or silently overwrite a newer
binding.

Verify: Two genuine competing processes, racing binds, stale
ordinary saves, failed commits, lock recovery, and no lost
bindings.

Boundaries: Preserve existing binding semantics. No SemanticGraph
writes, containment, bulk migration, or unrelated persistence
redesign.

Evidence: Failing-first reproduction, targeted regression, full
regression x3, exact-head CI, fresh clone.

STOP: Submit one frozen candidate for certification.

Progress: TD-1 now has durable Idea bindings, validated targets,
corruption refusal, rollback, stale-instance detection, and
conflict detection at the tested commit gate. The remaining work
is to make the concurrency guarantee enforceable through the
actual save operation.
