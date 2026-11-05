# Q1 Bounded Repair Plan — Exchange/Recovery Owner-Lock Serialization

Status: PLAN ONLY — presented under Director hourly review #4
(Gmail id 1a1aa949e4c14ee8, 2026-11-05 01:20 CST). **No
implementation is authorized by the audit ruling; this plan
is the deliverable the ruling ordered.** It answers the audit
report's Q1-1/Q1-3 by recommending one design; the Director
chooses.

## Scope (bounded, exactly the ruled circuit)

IN: `form/dell_matrix/exchange.py` — `import_packet`,
`recover_exchange_import`, `_dispose_import_journal`,
`_clear_import_journal`, and the load-boundary call site in
`form/persist_rest.load` insofar as it invokes Exchange
recovery.

OUT (per the ruling, separate proposals): SemanticGraph and
per-Idea writer locking (graph inventory item);
`core_i_recovery` journal writers (checkpoint / rollback /
confirmation / supersede recoveries run earlier in `load()`
and keep their current fail-closed semantics untouched);
Nursery.save as a general writer (it is fenced here only as
part of the import/compensation path).

## Design

**P1 — Serialize the whole recovery transaction, not the
final write.** `recover_exchange_import(owner)` executes its
full read → validate → decide → write → verify → dispose
sequence inside `owner_state_lock(owner)`
(`form/owner_state_lock.py`: kernel flock per owner, bounded
wait, fail-closed `OwnerLockBusy` / `OwnerLockUnavailable`,
NEVER an unlocked fallback). Because the canonical save
funnel (`persist_rest.save`) and TD-1 bind/containment
already hold the same lock, a recovery can no longer hold a
stale snapshot across a locked save — W1's window closes
structurally. If the lock cannot be acquired, recovery
refuses and `load` fails closed (state not exposed), the
same failure vocabulary TD-1-R2 already established.

**P2 — Serialize the import transaction on the same lock.**
`import_packet` holds `owner_state_lock(owner)` across
journal-write → land (nursery + program saves) → durable
verify → journal disposal. A load-boundary recovery then
either runs before the journal exists (no-op "none") or
after the import transaction completes (it judges durable,
complete state) — it can never interleave mid-import, which
closes W3's window. The journal is still written BEFORE
landing (recorded-intent law) and retained on failure with
the existing `compensation_incomplete` marking; the lock is
kernel-held and released on process death, so a crashed
holder cannot wedge later recovery, and lock files are never
unlinked (existing module law).

**P3 — W2 idempotent disposal (mandatory separate check).**
Inside the lock, `_dispose_import_journal` distinguishes two
cases `_clear_import_journal` currently conflates:
(a) the journal file is already absent AND a durable
re-check under the lock shows the established outcome's
end-state — disposal is treated as accomplished
(idempotent; a peer recovery finished it); (b) the journal
is present but unlink fails — the existing `ExchangeError`
still raises, journal retained as evidence. A journal that
exists with unresolved durable state is never silently
dropped: case (a) requires the outcome to be re-established
from the canonical files first, not inferred from absence
(Positive Evidence Law).

**P4 — W3 success-consistency proof (mandatory).**
`import_packet` may return ok=True only after a post-
transaction durable re-read — under the same lock, reusing
the recovery completeness predicate (`_durable_import_state`
+ journal match) — shows proposal + seed + receipts all
present and matching the journal. Any disagreement routes
through the existing `_compensate_import` path and returns
ok=False with `journal_retained` and the durable-state
discrepancy disclosed. ok=True with orphaned program entries
becomes impossible by construction, not by disclosure.

**P5 — Clean reads stay clean.** With no journal present,
`recover_exchange_import` remains a single file probe and
returns "none" WITHOUT acquiring the lock: the no-journal
common-case load stays lock-free (answering Q1-3 in favor of
readers). The lock is acquired only when a journal exists —
precisely the case where a write may follow. (An import
starting concurrently is safe: its own P2 lock acquisition
and journal-first write mean a load either sees no journal
and unjournaled state — which recovery law never touches —
or sees the journal and serializes.)

## What is deliberately NOT in this design

- No wrapping of only the final write (the ruling forbids
  it: it leaves stale snapshots — P1 exists because of that).
- No change to journal format, ordering, or crash-safety
  semantics; no change to compensation behavior beyond P4's
  routing.
- No graph/per-Idea locking (separate proposal per ruling).
- No new lock mechanism: `owner_state_lock` is reused; no
  second authority.

## Evidence contract for the future repair circuit

Per the ruling, all mandatory: failing-first W1/W2/W3 using
this audit's probe (`q1_probe.py`, seams unchanged — on
repaired code W1's marker must survive, W2 must produce no
spurious error, W3 must end coherent-or-honestly-failed);
two real OS processes; regress ×3 sequential; fresh clone;
terminal exact-head CI. Mutants: (M1) lock narrowed to the
final write only — must be killed by W1; (M2) P3 idempotence
removed — killed by the W2 check; (M3) P4 proof skipped —
killed by the W3 check. A W2 fault-injection check (unlink
failure with journal present) must still raise, proving P3
did not weaken fail-closed disposal.

## Risks / open questions for the Director

- R1: P2 holds the owner lock for the whole import
  (receipt-count bounded today; a pathological packet could
  hold it toward the bounded-wait timeout for concurrent
  savers, which then fail closed). Acceptable?
- R2: the `core_i_recovery` recoveries that run BEFORE
  Exchange recovery in `load()` stay outside this lock in
  this circuit — their windows vs Exchange recovery are
  narrower (different files) but not audited here. Confirm
  they belong to the separate inventory proposal.
- R3: Q1-1 — confirm this design (audit options O1+O2
  combined, scoped to Exchange only) is the authorized
  repair shape, or select another option.
- R4: Q1-2 — graph/per-Idea locking stays a separate
  circuit, per the ruling's split. Confirmed in this plan;
  no action requested beyond acknowledgement.
