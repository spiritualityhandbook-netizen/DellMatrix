# DIRECTOR REVIEW — Water + TD-1-R2 (Mode D, 2026-11-04)

Archived by Uni Ω from the Director's review as relayed by Ace /
Overseer, 2026-11-04. The Director inspected the implementation,
test coverage, Director reports, and exact-head CI records on
GitHub.

## Rulings

| Circuit | PR | Evidence | Ruling |
|---|---|---|---|
| Water persistence | #285 | 14/14 targeted; 234/234 regression ×3 | **CERTIFIED** |
| TD-1-R2 owner lock | #286 | 23/23 targeted; 235/235 regression ×3 | **CERTIFIED within the canonical save/bind scope** |

Both frozen PR heads have completed-success records for Python
package, Studio browser acceptance, and Form smoke.

TD-1 overall: **CERTIFIED WITH NOTED BOUNDARIES** (see Q2).

The certification is deliberately scoped. It does not establish
atomicity across every persistence pathway or every file in the
system.

## The three questions, resolved

**Q1. Exchange and recovery writes:** They must eventually
respect the same owner-state transaction boundary wherever they
can replace canonical Program state. GitHub source confirms
direct writes outside the new lock. A separate boundary audit is
authorized BEFORE modification; preserve recovery journal
ordering and crash safety. Do not indiscriminately wrap recovery
functions in locks.

**Q2. TD-1 certification:** CERTIFIED WITH NOTED BOUNDARIES. The
R2 repair closes the original concurrent-writer defect for the
normal save/bind pathway. **TD-2 is now authorized** as the next
bounded Track D implementation circuit.

**Q3. Binding-scoped protection:** APPROVED FOR V1. A stale save
must not silently destroy a newer binding. General
last-writer-wins behavior for unrelated state remains an
acknowledged limitation, not a newly certified guarantee.

**Naming correction (Director):** the approved Track D plan
defines TD-2 as containment operations — nest, promote, and
reparent with a REPL-first surface — not merely a binding
display. (Uni's R2 report Q2 parenthetical is corrected by this
ruling.)

## Directive — TD-2 (Mode C, implement one circuit)

TARGET: Track D TD-2 — Canonical Idea Containment Operations.

- Implement Program-level nest, promote, and reparent operations
  through canonical Unit→Idea bindings.
- Expose the operations through the REPL first.
- Use lazy binding with actual human-subject provenance.
- Preserve Unit and canonical Idea identities.
- Keep SemanticGraph the sole containment authority.
- Enforce lifecycle validity, single-parent and acyclic
  containment, and sandbox isolation.

REQUIRED PROOFS: three-level nesting and correct ancestry;
promotion retains both identities and historical edges; a second
parent refuses without explicit reparenting; missing/corrupt
Ideas refuse without silent replacement; failed saves and
interrupted multi-step mutations leave explicit, recoverable
evidence; cross-process conflicts cannot silently overwrite
bindings; regression ×3, fresh-clone verification, exact-head CI,
and a frozen evidence report.

FORBIDDEN: a second containment store in Plane; bulk binding or
migration; cross-sandbox containment; Exchange containment
transfer; TD-3 implementation or Studio expansion; claims of
cross-file atomicity without proof.

STOP: present one frozen candidate for Director certification.
No further Track D circuit is automatically authorized.

PARALLEL QUEUE: the authorized English-reachability (B-2)
investigation may continue. Exchange/recovery lock
reconciliation and gravity/evolution persistence remain separate
future circuits.

## What changed for DellMatrix (Director's summary)

Water: streams, rivers, parent references, and pools now survive
save/reload; pools reconnect to their original stream objects
rather than becoming independent copies; new stream IDs avoid
collisions with restored live records.

TD-1: the previous read-check-write race is closed for
cooperating writers. Binding and ordinary canonical Program
saves now share an owner-specific operating-system lock. The
cross-process tests demonstrate that a competing writer cannot
silently destroy a newer binding, and that a terminated lock
holder releases the lock.

DellMatrix has moved from disconnected Plane units and canonical
Ideas to durable, conflict-protected identities. TD-2 is the
next functional step: allowing those identities to form real
parent-child idea structures without creating a second source of
truth.
