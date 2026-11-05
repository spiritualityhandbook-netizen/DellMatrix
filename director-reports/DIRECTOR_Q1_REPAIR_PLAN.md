# Q1 Bounded Repair Plan — Exchange/Recovery Owner-Lock Serialization

Status: PLAN ONLY — presented under Director hourly review #4
(Gmail id 1a1aa949e4c14ee8, 2026-11-05 01:20 CST). **No
implementation is authorized by the audit ruling; this plan
is the deliverable the ruling ordered.** It answers the audit
report's Q1-1/Q1-3 by recommending one design; the Director
chooses. **Amended under Director hourly review #6 (Gmail id
1a1aafa42fa6c5e7, 2026-11-05 03:11 CST —
TARGETED_CORRECTION_REQUIRED, plan review only, NO
implementation or merge authorization): see the Amendment
section at the end of this document for the call graph, lock
ordering, outcome table, and bounded verification commands
the ruling ordered.**

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

## Amendment — response to Director hourly review #6 (2026-11-05)

Review #6 (Gmail id 1a1aafa42fa6c5e7, 2026-11-05 03:11 CST;
archived at responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_Q1_
PLAN.md) ruled TARGETED_CORRECTION_REQUIRED on the plan at
head 1b27019b: plan review only; no implementation or merge
authorization; W1/W2/W3 remain "submitted, not independently
reproduced" and are not labeled independently certified
anywhere in this plan. The four corrections are answered
below. All code references are to the audited base 8e0784c
(`form/dell_matrix/exchange.py`, `form/persist_rest.py`,
`form/owner_state_lock.py`) and were re-read for this
amendment.

### A1. Call graph and exact lock acquisition boundaries (correction 1)

Entry points and the precise acquisition/release points:

```
persist_rest.load(owner)
  └─ core_i_recovery recoveries            [OUT OF SCOPE — unchanged]
  └─ exchange.recover_exchange_import(owner)
       1. j = _read_import_journal(owner)          (probe, NO lock)
       2. j is None        → return "none"         (P5 fast path)
       3. j present        → ACQUIRE owner_state_lock(owner)
       4. j2 = _read_import_journal(owner)          (re-read under lock)
          j2 is None      → P3-absent path (A3 below)
          j2 differs      → decide from j2, never from the stale probe
       5. _raw_state_files → decide (completed / no_target /
          already_absent / removed) — the existing decision
          logic, unchanged
       6. atomic_write_json (nursery and/or program file)
       7. _durable_import_state verify (fresh re-read)
       8. _dispose_import_journal (amended P3, A3)
       9. RELEASE lock (context-manager exit, incl. on raise)

exchange.import_packet(program, packet)
  owner := program.owner        (exchange.py:731 — the ONLY
                                 owner source; packet-supplied
                                 owner fields are never trusted)
  Phase 0 (NO lock, NO canonical mutation):
       validate_packet → protected-values screen →
       _preflight_import → lint_packet →
       unresolved-journal precheck (_read_import_journal;
       a present journal refuses the import, as today)
  Phase 1: ACQUIRE owner_state_lock(owner) — immediately
       before the first durable mutation, i.e. before
       _write_import_journal. NOTHING above this line writes
       a canonical file, so a refusal or crash in Phase 0
       leaves no evidence behind.
  Phase 2 (inside the lock, order unchanged from today):
       _write_import_journal(intent, pid=None)
       → program.nursery.add(...)            [landing]
       → _write_import_journal(phase=landed, pid)
       → record_receipt(..., _defer_save=True) × n
       → record_seed_payload(..., _defer_save=True)
       → program.save()                      [final save]
       → P4 durable success predicate (A4) — fresh re-read;
         failure routes to _fail_import compensation,
         ok=False, journal retained per compensation state
       → _clear_import_journal (disposal reported as the
         separate journal_retained fact, per DIR-F12)
       → return ok=True (only reachable past the predicate)
  Phase 3: RELEASE lock.
```

Nested calls under the held lock — behavior of each:

- `program.save()` → `persist.save` → `persist_rest.save`
  → `owner_state_lock(owner)`: a NESTED acquisition by the
  same process+thread. Per the lock module's stated
  contract, nested acquisitions join by depth count; the
  kernel flock is taken once and released when the
  outermost context exits. No second flock, no self-deadlock.
- `program.nursery.add(...)` → `Nursery.save()`: takes NO
  lock of its own (direct `atomic_write_json` to the
  nursery path). It is serialized because the importer
  holds the owner lock across the whole transaction; no
  in-scope writer can interleave. This plan does NOT add a
  lock acquisition inside Nursery.save (that would be the
  silent widening correction 4 forbids — Nursery.save as a
  general writer stays out of scope).
- `record_receipt` / `record_seed_payload` with
  `_defer_save=True`: perform no saves at all during
  landing (existing AF-6 deferral).
- `_compensate_import` (failure path, inside the lock):
  calls `program.nursery.save()` (no own lock, as above)
  and `program.save()` (nested reentrant join, as above),
  then judges by `_durable_import_state` re-read.
- TD-1 `bind` / TD-2 containment ops acquire the SAME
  single lock at their own entry points: they contend with
  an import/recovery (bounded wait → `OwnerLockBusy`,
  fail-closed), they never nest with it.

Lock-order proof: the design acquires exactly ONE distinct
lock — the per-owner `owner_state_lock`. Deadlock requires
at least two distinct locks acquired in inconsistent order
across participants; with one lock there is no order pair
and no cycle, within a process or across processes. Every
nested acquisition above is either a same-thread reentrant
join of that one lock or no acquisition at all. Cross-
process contention therefore resolves in exactly two ways:
the bounded wait expires (`OwnerLockBusy`, nothing
mutated), or the holder finishes/dies and the kernel
releases the flock (the lock file is never unlinked, per
module law, so no inode split). `OwnerLockUnavailable`
(no kernel mechanism) fails closed before any mutation —
there is no unlocked fallback anywhere in this design
(§31.2).

Two-process deadlock/timeout test (added to the evidence
contract below): process A acquires the owner lock through
a test seam and holds it; process B attempts (i) a
journal-present recovery and (ii) an import — each must
raise `OwnerLockBusy` within LOCK_TIMEOUT_S (10s) plus a
stated margin (assert elapsed < 15s), must mutate nothing
(canonical files byte-identical, no journal written by the
import attempt), and must not hang. A is then SIGKILLed
mid-hold; B's retry must acquire and complete, proving
kernel release on holder death.

### A2. Scope split preserved (correction 4)

Unchanged from the original plan and restated as binding on
the amendment: SemanticGraph and per-Idea writer locking,
and `core_i_recovery`'s journal writers/recoveries (which
run before Exchange recovery inside `load()`), remain
separate audited proposals. Nothing in A1–A4 wraps, orders,
or otherwise touches them; the call graph shows them only
to mark the boundary.

### A3. P3 — the reachable journal-absent path (correction 2)

The reviewer is correct that under P1/P2 a peer recovery
cannot dispose the journal mid-transaction. The journal-
absent-at-disposal case is nevertheless reachable through
the transaction's OWN legitimate disposers, via the
probe-then-lock gap P5 deliberately keeps:

1. **Importer self-disposal.** Recovery probes the journal
   (exists — an import is in flight or just finished) and
   then waits on the lock. The importer, holding the lock,
   completes and disposes its own journal on the success
   path (the final `_clear_import_journal` in
   `import_packet`) or on a fully-compensated failure path
   (`_fail_import` clears when compensation is complete).
   The waiting recovery then acquires the lock and re-reads:
   the journal is gone — disposed by its owner, not by a
   peer recovery.
2. **Ordered peer recovery.** Two loads probe the same
   journal; the first to acquire the lock completes the
   outcome and disposes; the second acquires afterwards and
   finds absence. Serialization orders them; it does not
   refresh the second's probe.
3. **Retained-journal completion.** An import that returned
   ok=True with `journal_retained=True` (DIR-F12: disposal
   failed, success stood) leaves the journal for the next
   load; the first recovery to run establishes "completed"
   and disposes; any concurrently-probed second recovery
   finds absence as in (2).

Amended disposal rule (replaces P3's case (a) mechanics;
the rule's intent is unchanged): inside the lock,
`_dispose_import_journal` first re-reads the journal.

- Journal PRESENT → unlink; unlink failure raises
  `ExchangeError` exactly as today (present-file
  unlink-failure refusal RETAINED, unchanged).
- Journal ABSENT → disposal counts as accomplished ONLY IF
  the recovery re-establishes its already-decided outcome
  from durable state, using the journal snapshot it read at
  entry (step 4's re-read, or the probe copy when the lock
  was uncontended): for "removed"/"already_absent"/
  "no_target", `_durable_import_state(owner, pid)` must
  show no proposal, no seed, zero receipts for the pid (for
  "no_target", the journal's label/origin/detail_sha256
  must match no nursery proposal — the same content match
  recovery already uses to resolve a pid=None journal);
  for "completed", the full completeness predicate (A4)
  must hold. If the durable re-establishment CONTRADICTS
  the outcome, recovery raises `ExchangeError` (evidence
  changed under it; fail closed, state not exposed) — it
  never treats absence itself as the proof (Positive
  Evidence Law).

### A4. P4 — the durable success predicate, checked before any success return (correction 3, first half)

Predicate `IMPORT_DURABLE(owner, journal)`, evaluated on a
FRESH re-read of both canonical files (`_raw_state_files` +
the recovery completeness computation, reused — not a new
implementation), all inside the lock:

- the nursery file holds proposal `pid`, and (when the
  journal's pid was resolved from a pid=None intent) the
  proposal's label/origin/detail match the journal's
  label/origin/`detail_sha256`;
- the program file's `exchange_seeds` entry for `pid`
  matches the journal on label/chain/keep, on
  author_origin/created/registry, on requirements, and on
  receipts_expected/receipts_hash;
- the program file's `exchange_receipts` for `pid` number
  exactly `receipts_expected` and their digest equals
  `receipts_hash`.

(This is precisely the completeness computation
`recover_exchange_import` already performs to rule
"completed"; P4 makes the importer prove the same fact
about its own transaction instead of assuming it from a
save returning.)

Ordering guarantee: in `import_packet`, the predicate is
evaluated AFTER the final `program.save()` and BEFORE
journal disposal and BEFORE the return statement — there is
no success return path that skips it, including the
DIR-F12 path: if the predicate passes and disposal then
fails, the result is ok=True with `journal_retained=True`
(disposal is a separate fact, and durability was already
proven); if the predicate fails, the result is ok=False
via `_fail_import` compensation with the discrepancy
disclosed, regardless of disposal.

### A5. P5 analyses (correction 3, second half)

**Load sees no journal while an import is starting.** The
import's Phase 0 (validation, protected screen, preflight,
lint, journal precheck) mutates no canonical file, and the
journal write — the first durable mutation — happens only
after lock acquisition. A load probing in that window sees
the complete pre-import generation: recovery returns
"none" (unjournaled state is never touched — recorded-
intent law) and the load exposes that older generation
coherently. It may be stale relative to the in-flight
import by the time it is used; this design claims NO
cross-file atomicity for the no-journal fast path — only
that what it exposes is one complete, unjournaled
generation, never a torn import.

**Crash after journal intent, before durable landing.**
The journal (phase="intent", pid=None) is on disk; the
import never returned, so no success was ever reported.
Two sub-cases at the next load's recovery (under the lock):
(a) crash before `nursery.add` persisted — the journal's
label/origin/`detail_sha256` content match finds no
proposal → outcome "no_target", journal disposed, nothing
removed; (b) crash after `nursery.add` persisted but
before the phase="landed" journal update — the content
match resolves the landed proposal's pid uniquely (more
than one match raises, refusing to guess), the completeness
predicate fails (no seed/receipts yet), and recovery
removes the proposal and disposes ("removed"). A crash
after landing but before the final save is the same shape
with pid already journaled. In every sub-case the import
is judged from durable evidence, never from the crashed
process's memory, and ok=True for it is impossible.

### A6. Outcome table (review #6 order)

| Case | Without the repair (audit evidence) | With this plan |
|---|---|---|
| W1: recovery vs locked save | CONFIRMED silent loss — recovery writeback erased the save's marker unit | Recovery and save serialize on the one lock; recovery re-reads under the lock after the save commits; the marker survives. Probe verdict required: marker present. |
| W2: load vs load recovery | CONFIRMED spurious `ExchangeError` over clean state (peer disposed the journal; unlink-false raised) | Second recovery re-reads under the lock; absence is accepted ONLY with durable re-establishment of the outcome (A3); no spurious failure over proven-clean state. |
| W3: import vs load-recovery | CONFIRMED ok=True with orphaned program entries, proposal removed | Import holds the lock across journal→land→save→predicate→dispose; a load's recovery runs wholly before or wholly after. ok=True only past the A4 predicate. Final files agree, or the import reports ok=False. |
| Crash after intent, before landing | Journal retained; recovery resolves by content match (existing behavior, unlocked) | Same resolution, now under the lock; "no_target"/"removed" per A5; no success ever reported for the crashed import. |
| Crash mid-import (landed, final save pending) | Recovery could interleave with a still-live importer (W3 shape) | Live importer holds the lock — recovery waits (bounded) instead of judging a moving target; crashed importer releases via kernel, recovery judges durable state. |
| Failed unlink, journal PRESENT | `ExchangeError`, journal retained (existing `_dispose_import_journal`) | UNCHANGED — retained verbatim (A3). Fault-injection check must still raise. |
| Lock busy (peer holds > 10s) | n/a (no lock taken) | `OwnerLockBusy`, fail-closed, NOTHING mutated; load exposes no state; import refuses before its journal write. |
| Lock unavailable (no kernel mechanism) | n/a | `OwnerLockUnavailable`, fail-closed; never an unlocked fallback (§31.2). |

### A7. Bounded verification commands (for the future repair circuit)

Plan-level specification — these are the commands the
repair circuit must run and record terminal output for;
they are NOT run by this amendment (no implementation
exists yet, and none is authorized):

```
# failing-first / post-repair probe (seams unchanged),
# two runs, verdicts must be identical:
timeout 300 python3 director-reports/evidence/q1-audit/q1_probe.py
timeout 300 python3 director-reports/evidence/q1-audit/q1_probe.py

# repair suite incl. the A1 two-process deadlock/timeout
# test (OwnerLockBusy < 15s, zero mutation, post-SIGKILL
# acquisition) and the present-journal unlink fault
# injection (must still raise):
timeout 600 python3 -m form.<repair_suite_module>

# full regression, sequential, three orders:
timeout 3600 python3 -m form.regress
timeout 3600 python3 -m form.regress --twice
timeout 3600 python3 -m form.regress --order rev

# fresh clone at the candidate head, suite only:
git clone https://github.com/spiritualityhandbook-netizen/DellMatrix /tmp/q1-repair-fresh
timeout 600 python3 -m form.<repair_suite_module>   # run inside the clone
```

Plus the original evidence contract (unchanged): mutants
M1 (lock narrowed to the final write — killed by W1), M2
(P3 idempotence removed — killed by W2), M3 (P4 predicate
skipped — killed by W3); terminal exact-head CI under the
hard merge gate; any changed head needs re-review.

### Amendment disposition

The plan, as amended, is presented as ONE frozen plan head
for a new ruling. Risks R1–R4 stand as written. No code was
modified by this amendment; no implementation, merge, or
certification is claimed or requested beyond the ruling on
the amended plan.
