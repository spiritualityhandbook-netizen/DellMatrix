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
the ruling ordered. **Further corrected under the Director's
review of the amended plan at head ce8c8a40 (Gmail id
1a1ab339e516a634, 2026-11-05 04:14 CST —
TARGETED_CORRECTION_REQUIRED, plan only): see Amendment B
at the end of this document (P5 consistency boundary +
P5-R fail-closed validation + adversarial probe spec; P3
trusted entry snapshot + pid=None/no_target evidence cases;
A4 predicate labeled proposed design only). **Further
corrected under the Director's Amendment B review at head
2bf7d9a4 (Gmail id 1a1ab862b9532954, 2026-11-05 05:44 CST
— TARGETED_CORRECTION_REQUIRED, plan only, hold
implementation and merge): see Amendment C at the end of
this document (writer taxonomy corrected by transaction
shape T1–T4; B2 P5-C-i rationale and B1 soundness claim
withdrawn for two-step T3 writers; contract decision
D-P5-2 — serialize T3 as a separate circuit vs exclude
T3 and narrow the load contract, recommended; P5-D/P5-E
counterexample spec; P3 retained).**

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

## Amendment B — corrected plan, response to the Director's Q1 amended-plan review (2026-11-05)

Director review of the amended plan at head ce8c8a40
(Gmail id 1a1ab339e516a634, 2026-11-05 04:14 CST; archived
at responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_Q1_PLAN_R2.md)
ruled **TARGETED_CORRECTION_REQUIRED — PLAN ONLY; NO
implementation or merge authorization; no certification.**
Verified by the Director: the Amendment's lock call graph,
reentrancy rationale, absent-journal cases, durable-success
predicate, outcome table, and proposed test commands; exact-
head CI SUCCESS; no product-code change. W1/W2/W3 remain
submitted audit evidence, not independently reproduced.

Remaining findings, answered in order: (1) P5's no-journal
fast path lacks a precise consistency boundary — B1/B2;
(2) P3's journal-absent recovery lacks a trusted entry
snapshot and per-case re-established outcomes for
pid=None/no_target — B3; (3) the A4 predicate's status —
B0. All code references below are to the audited base
8e0784c, re-read for this amendment; PR #294 is docs-only,
so the audited code is unchanged at ce8c8a40.

### B0. Status of the A4 predicate — proposed design only

The Director is correct, and this plan now states it
without qualification: **the A4 `IMPORT_DURABLE` predicate
is a PROPOSED DESIGN, not an executed guarantee.** No code
in the repository implements it as the importer's success
gate today (`import_packet` at the audited base returns
ok=True after `program.save()` + journal disposal, with no
post-save completeness re-read — exchange.py:842ff); no
test, probe, or mutant has exercised the predicate as
specified in A4. It becomes a guarantee only if the future
repair circuit implements it and its evidence contract
(A7, extended in B4) passes and the Director certifies that
scope. Everywhere this plan says "the predicate holds /
must hold," read "the design requires the predicate to be
evaluated and to hold" — a requirement on future code, not
a property of current code.

### B1. P5 — the precise consistency boundary, the narrowed guarantee, and the fail-closed validation (P5-R)

**Definitions.** The canonical pair is (nursery file at
`owner_nursery_path(owner)`, program file at
`persist._path(owner)`). A *file generation* is the byte
content installed by one `atomic_write_json` call. A *pair
generation* is a pair of file generations that coexisted
as the durable result of one completed transaction
boundary (a completed import, a completed recovery, or a
quiescent state with no transaction in flight).

**What the existing mechanisms actually prove** (source-
grounded, audited base):

- `atomic_write_json` (form/dell_matrix/atomic_write.py)
  guarantees, per single file: a reader sees the previous
  complete generation or the new complete generation,
  never a torn file. Its own contract states the limit
  verbatim in substance: "Not a database: no transactions
  across multiple files." It proves NOTHING about a pair.
- `_read_import_journal(owner) is None`
  (exchange.py:404ff) proves exactly one fact: at the
  probe instant, no file existed at the journal path. It
  proves nothing about any later instant, nothing about
  either canonical file's generation, and nothing about a
  writer whose first journal write has not landed yet.
- The fast path takes NO lock. It therefore does not
  serialize against even the writers that DO take
  `owner_state_lock` today: `persist_rest.save` on the
  canonical path (persist_rest.py:156) can replace the
  program file while a fast-path load is between its
  journal probe and its pair reads, and the load cannot
  tell.
- `persist_rest.load` reads the pair at two separate
  moments: the program file in `_load_impl`, and the live
  nursery file later, during Program preparation
  (`_prepare_program` → Program construction against the
  owner's live nursery file). Nothing ties those two reads
  to one pair generation. (Load's own docstring already
  states the intended contract for the rollback gate — "a
  reader never accepts a hybrid program/nursery pair";
  the Exchange fast path is precisely where that contract
  is currently unguarded.)

**Concurrent writers at the audited base** (the boundary
is stated against this exact set):

| Writer | Pair files touched | Lock today |
|---|---|---|
| `import_packet` | journal write → nursery via `Nursery.save` → program via `program.save()` → journal clear | journal/nursery/journal-clear UNLOCKED; program save locked |
| `recover_exchange_import` (journal present) | nursery + program via direct `atomic_write_json`, then journal dispose | UNLOCKED |
| `persist_rest.save` (canonical) | program file only | LOCKED |
| `Nursery.save` (direct callers) | nursery file only | UNLOCKED |
| `core_i_recovery` recoveries | own journals/files — OUT OF SCOPE per A2, boundary unchanged | — |

**Withdrawn claim.** A5's first bullet said a no-journal
load probing during an import's Phase 0 "exposes that
older generation coherently." That wording is WITHDRAWN
as unproven: Phase 0 mutates nothing, but the load's pair
reads happen AFTER the probe, and the importer can pass
from Phase 0 into journal-write → nursery landing →
program save while those reads are in flight. The exposed
pair can then be nursery-generation N+1 with
program-generation N (proposal present, its seed/receipts
absent) or the reverse skew across an ordinary save —
a hybrid pair that never existed as a completed
transaction's result.

**Narrowed guarantee (what P5 may claim after this
correction, and no more).** A lock-free no-journal load,
WITHOUT the validation in P5-R below, guarantees only:
(i) each individual file it reads is one complete file
generation (atomic_write's per-file contract), and
(ii) Exchange recovery itself wrote nothing. It does NOT
guarantee the pair is a pair generation. Any wording in
the original P5 or A5 that implies pair coherence for the
unvalidated fast path is superseded by this paragraph.

**P5-R — fail-closed validation (the design this
corrected plan proposes).** The fast path becomes
lock-LIGHT, not lock-free; the "clean reads stay clean"
preference is preserved as "no lock is held while reading,"
not as "no lock is ever taken":

1. Probe: `j1 = _read_import_journal(owner)`. Present →
   the locked A1 recovery path, unchanged. Absent →
   capture pair fingerprints F1 = (SHA-256 of the nursery
   file's bytes or ABSENT, SHA-256 of the program file's
   bytes or ABSENT).
2. Read the pair exactly as load does today (program file,
   then live nursery file), retaining the SHA-256 of the
   bytes actually consumed for each file.
3. Validate under a brief `owner_state_lock(owner)`
   acquisition (bounded wait; `OwnerLockBusy` /
   `OwnerLockUnavailable` → the load FAILS CLOSED and
   exposes nothing — §31.2, no unlocked fallback):
   under the lock, re-probe the journal and re-fingerprint
   both files from disk. Exposure is authorized only if
   ALL of: journal still absent; disk fingerprints equal
   F1; disk fingerprints equal the consumed bytes'
   fingerprints. The lock is then released; the loaded
   in-memory state is the validated pair.
   Soundness, scoped exactly: at the validation instant,
   under the one lock, the disk pair IS the consumed pair
   and no journal exists; every in-scope pair writer
   (repaired import, repaired recovery, canonical save)
   holds that same lock across its pair mutations, so none
   was mid-transaction at that instant, and the consumed
   pair is therefore a pair generation. Fingerprint
   equality across steps 1–3 additionally proves no
   completed replacement intervened between the initial
   capture and validation.
4. Any validation failure (journal appeared, either
   fingerprint differs) → discard the consumed pair and
   perform ONE locked retry: acquire the lock, run
   recovery's probe under the lock (journal present →
   the A1 recovery transaction), read the pair under the
   lock, release, expose. If the retry cannot complete
   (lock busy/unavailable, journal still unresolved), the
   load fails closed. There is no second retry and no
   unvalidated exposure.
5. Boundary of the proof, stated plainly: writers
   OUTSIDE the repaired scope can still replace a file
   between validation and a later re-read — in particular
   direct `Nursery.save` callers and the out-of-scope
   `core_i_recovery` paths (A2). P5-R DETECTS their
   completed writes that land before the validation
   instant (fingerprint mismatch → locked retry/fail
   closed); it does not and cannot prevent them, and the
   guarantee above is claimed only against the in-scope
   writer set. A write-and-byte-identical-restore cycle
   completed entirely inside the step 1–3 window is
   indistinguishable by fingerprinting; P5-R closes it
   only insofar as in-scope writers cannot execute such a
   cycle without holding the lock validation waits for —
   for out-of-scope writers this residual is DISCLOSED,
   not claimed away.

**Decision requested (D-P5).** The Director is asked to
rule P5-R (lock-light validation; pair coherence claimed
only as scoped above) versus the alternative the review
offered: keep loads fully lock-free and accept the
narrowed guarantee as the whole contract (per-file
atomicity only; hybrid pairs possible under concurrency
and explicitly not promised against). This plan
RECOMMENDS P5-R: pair coherence is load's own stated
contract, and the cost is one brief bounded lock
acquisition per load. Absent a ruling for the alternative,
the repair circuit implements P5-R.

### B2. Adversarial two-process probe SPEC for P5 (specification only — not executed by this amendment)

Harness law for all three sub-probes (repair-circuit
failing-first evidence; the audit probe `q1_probe.py` is
the precedent): two GENUINE child OS processes; an
isolated per-probe state directory/owner; coordination
seams ONLY pause a process at a real code boundary (the
named call sites below) and change no logic; no lock is
held by a seam unless the code under test holds it;
verdicts are computed from the bytes on disk and the
loader's exposed state, never from a participant's memory;
two full runs must produce identical verdicts.

- **P5-A — load races the FIRST journal write.**
  Setup: quiescent pair, no journal. Loader L calls
  `persist_rest.load`; seam pauses L immediately after
  `recover_exchange_import` returns "none" (the fast-path
  decision point). Importer I then runs a complete
  `import_packet` (journal write → nursery landing →
  journal pid update → deferred records → program save →
  journal clear). L resumes and finishes loading.
  Verdict: FAIL if L exposes a hybrid pair (nursery holds
  the imported proposal while the program side lacks its
  seed/receipts, or the program side holds them while the
  proposal is absent) or any pair other than the exact
  pre-import pair or the exact post-import pair. Repaired-
  code PASS requires: pre-import pair exactly, OR
  post-import pair exactly, OR one locked retry, OR a
  fail-closed load error — never a hybrid.
- **P5-B — load races journal DISPOSAL.** Two sub-cases,
  seam at `_clear_import_journal` in each of its disposing
  callers: (B-i) importer success path (exchange.py:842):
  I pauses after the journal file is removed and before
  `import_packet` returns; L runs a full load in the
  window — it must expose the exact post-import pair
  (disposal is not a state change; the pair was already
  durable). (B-ii) recovery path (`_dispose_import_journal`,
  exchange.py:542ff): R has established outcome "removed"
  for a partial import and written both canonical files;
  R pauses after the unlink, before returning; L loads —
  it must expose the exact recovered pair and must NOT
  raise a spurious disposal error (the W2 linkage).
  Verdict FAIL on any hybrid pair, any spurious error, or
  L resurrecting the removed proposal.
- **P5-C — load races CANONICAL SAVES.** (C-i) Locked
  saver: process S runs `persist_rest.save` for a program
  whose logical update also requires a following
  `Nursery.save`; seam pauses S after the program file's
  atomic replacement, before the nursery replacement; L
  loads in the window. (C-ii) Unlocked nursery saver: S
  replaces the nursery file via `Nursery.save` while L is
  between its program read and its nursery read (seam at
  L's pair-read boundary). Verdict FAIL if L exposes a
  hybrid pair without detection. Repaired-code PASS:
  C-i is prevented/validated by the shared lock (S holds
  it; L's validation cannot pass mid-save); C-ii — an
  out-of-scope writer — must at minimum be DETECTED
  (fingerprint mismatch → locked retry or fail closed);
  silently exposing the hybrid is FAIL even though
  prevention is out of scope.
  Status of expectations: on CURRENT code the predicted
  verdicts are FAIL for P5-A and P5-C (no lock, no
  validation — argued from the code above) and PASS for
  P5-B-i. These are HYPOTHESES for the repair circuit's
  failing-first run, NOT confirmed findings; this
  amendment executed no probe.

### B3. P3 — trusted entry snapshot and the pid=None / no_target evidence cases

**Trusted entry snapshot S.** The pre-lock probe copy is
UNTRUSTED: it may decide only whether to acquire the lock
(A1 step 1–3); it never decides an outcome and never
authorizes a disposal. The FIRST action after lock
acquisition in recovery is to capture S, and every
subsequent decision in that recovery is taken from S and
from fresh under-lock re-reads, never from the probe:

```
S = {
  journal:        parsed journal dict as read under the lock,
  journal_sha256: SHA-256 of the journal file's raw bytes,
  import_id:      journal["import_id"],
  nursery_sha256: SHA-256 of the nursery file's bytes (or ABSENT),
  program_sha256: SHA-256 of the program file's bytes (or ABSENT),
  candidates:     pid=None content-match result computed on the
                  under-lock nursery snapshot (B3 cases below),
  resolved_pid:   the single candidate, when exactly one exists,
}
```

**Disposal-time identity check (new, binding on the
design).** Immediately before any disposal counts as
accomplished, recovery re-reads the journal under the
lock: present with `import_id == S.import_id` → unlink;
unlink failure raises `ExchangeError` exactly as today
(retained from A3, unchanged). Present with a DIFFERENT
`import_id` → that file is another transaction's evidence:
recovery MUST NOT dispose it, MUST NOT treat its own
outcome as disposed, and raises `ExchangeError`
(journal_retained; state not exposed). Absent → disposal
counts as accomplished ONLY via the re-establishment
demonstration for the decided outcome (table below),
computed on a fresh under-lock re-read and tied to S
(the same journal fields, the same resolved_pid) — never
from absence alone, and never from the probe copy.

**The pid=None cases.** At the audited base a journal has
`pid: None` from `_write_import_journal(phase="intent")`
until the post-landing update writes the resolved pid
(exchange.py:736ff, 786ff). Recovery resolves the target
by content match over the nursery snapshot: label ==
journal label AND origin == journal origin AND
SHA-256(detail) == journal `detail_sha256`
(exchange.py:617ff). The cases, with the re-established
outcome each must DEMONSTRATE (from S + a final under-lock
re-read) before a "no_target" or absent-journal disposal
stands:

| Case | Snapshot facts | Decided outcome | Required demonstration before disposal stands |
|---|---|---|---|
| N0 | candidates == 0; journal status "in_progress" | no_target | Final re-read content match is STILL 0 candidates against S's label/origin/detail_sha256; AND no attributable orphan entries: by `import_packet`'s call order, record_receipt/record_seed_payload run only AFTER a successful nursery landing and the journal's pid update, so a never-landed import can have left no seed/receipt entries — this step verifies the premise instead of assuming it: every exchange_seeds/exchange_receipts entry present in the final program file must carry a pid that IS a proposal in the final nursery snapshot or was already present in S's program snapshot as a pre-existing entry. Any unattributable entry CONTRADICTS no_target → raise, journal retained, state not exposed. Absence of the journal alone demonstrates none of this. |
| N1 | candidates == 0; journal status "compensation_incomplete" | no_target ONLY on proof | S's journal `failure` record (stage + compensation_errors, written by `_mark_journal_incomplete`) is carried into the recovery result; final re-read content match still 0; AND the orphan check from N0 passes with one addition: any orphan seed/receipt entries found are attributed by their own `pid` field — if such entries exist, the case is NOT no_target: that pid becomes the resolved_pid and the resolved-pid path (removal + durable verify) governs. If attribution is impossible → raise, journal retained. |
| N2 | candidates == 1 | resolved-pid outcome (completed / removed / already_absent per the existing decision logic) | The outcome's own demonstration, tied to S.resolved_pid (not a fresh search, which could resolve differently on changed state): "completed" → the A4 predicate (B0: proposed design) on a fresh re-read for S.resolved_pid; "removed" → `_durable_import_state(owner, S.resolved_pid)` shows proposal absent, seed absent, receipts 0 on the final re-read; "already_absent" → the same all-absent demonstration. For the journal-absent-at-disposal variant (A3's three reachable paths), the SAME demonstration for the SAME S.resolved_pid is what counts disposal as accomplished. |
| N3 | candidates > 1 | NO outcome — raise | Existing behavior retained: `ExchangeError` (refusing to guess), journal retained, state not exposed, S's candidate list recorded in the error details. N3 has NO absent-journal re-establishment path: if the journal later disappears, only an in-scope disposer could have removed it (the complete caller set of `_clear_import_journal` / `_dispose_import_journal` at the audited base is inside exchange.py: importer success, importer landing-failure, `_fail_import`, and recovery disposal itself), and a recovery that never disposed cannot claim the outcome from that absence — a subsequent load takes a NEW snapshot and decides from it; it does not inherit N3 as resolved. External deletion of the journal file is outside the model (the same boundary as external deletion of any canonical file) and is disclosed as such. |

**What changes from A3.** A3's rule ("absence counts only
with durable re-establishment") is retained but is now
anchored: the re-establishment is computed against the
TRUSTED snapshot S (journal identity + content-match
fields + resolved_pid captured under the lock), the
disposal-time identity check forbids disposing another
transaction's journal, and N0/N1 replace "no_target by
content match" with content match PLUS the orphan-
attribution verification. The present-file unlink-failure
refusal is unchanged.

### B4. Evidence contract additions (for the future repair circuit; nothing here is executed by this amendment)

- The B2 probe spec (P5-A, P5-B-i/ii, P5-C-i/ii) joins
  A7's commands as mandatory failing-first evidence: the
  probe must FAIL on unrepaired code where B2 predicts
  failure and PASS on repaired code, two runs with
  identical verdicts, before any merge consideration.
- P3 suite checks for N0, N1 (incl. the orphan-attribution
  branch), N2 (each outcome), N3 — each asserting the
  demonstration was actually computed (e.g., by fault
  injection that makes the final re-read contradict the
  outcome and requires the raise).
- Mutants added: M4 — disposal trusts the pre-lock probe
  copy / skips the import_id identity check (killed by a
  journal-swap check: journal replaced by a different
  import_id between snapshot and disposal must raise and
  must not dispose); M5 — P5-R validation removed (killed
  by P5-A and P5-C); M6 — N0 orphan check removed (killed
  by the N1 orphan-attribution check).
- A4's predicate checks remain as specified in A4/A7,
  labeled proposed-design requirements until implemented.

### B5. Scope and disposition

Scope split preserved verbatim (A2): SemanticGraph,
per-Idea, and `core_i_recovery` locking remain separate
audited proposals; B1's boundary table lists them only to
mark the boundary. No code was modified by this
amendment; no implementation, merge, or certification is
claimed or requested. The plan, as corrected by Amendment
B, is presented as ONE new frozen plan head for a design
ruling. Decisions requested: **D-P5** (B1: adopt P5-R
lock-light validation — recommended — or rule the
narrowed per-file-only guarantee as the whole contract);
acknowledgement that B3's snapshot + per-case
demonstrations satisfy the P3 correction; and the
standing R1–R4 / Q1-1 design question for the repair
shape as a whole. The #294 MERGE HOLD continues; Q1 repair
implementation remains STOPPED pending that ruling.

## Amendment C — response to the Director's Q1 Amendment B review (2026-11-05 05:44 CST)

Director review of the corrected plan at head 2bf7d9a4
(Gmail id 1a1ab862b9532954, 2026-11-05 05:44 CST; archived
at responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_Q1_PLAN_R3.md)
ruled **TARGETED_CORRECTION_REQUIRED — PLAN ONLY; HOLD
implementation and merge; no certification.** Verified by
the Director: the bounded diff is documentation/evidence,
exact-head CI SUCCESS (3/3), and Amendment B's withdrawals,
P5-R proposal, probe specs, and P3 snapshot anchoring are
design specifications, not executed repairs.

**The finding is accepted, and Uni verified it
independently against source at the audited base before
drafting this amendment** (source unchanged at 2bf7d9a4;
PR #294 is docs-only):

- `persist_rest.save`, canonical path
  (form/persist_rest.py:150–159): the `owner_state_lock`
  context wraps ONLY `_refuse_if_binding_loss` and
  `_write_program_file` — i.e., the program file's own
  write. The lock is RELEASED when `save()` returns. It
  never spans any following write.
- `Nursery.save` (form/dell_matrix/nursery.py:278ff):
  takes NO `owner_state_lock` at all. Its only concurrency
  guard is a per-instance on-disk signature check
  (`_disk_sig` vs `self._seen`, NurseryConflictError),
  followed by a direct `atomic_write_json` of the nursery
  file.
- Therefore a logical update performed as
  `persist_rest.save(...)` followed by `Nursery.save()`
  (or the reverse order) is TWO independent single-file
  transactions with a durable, observable intermediate
  state between them, during which NO lock is held by
  anyone. Callers composing the pair this way exist at
  the audited base, e.g. form/dell_matrix/
  confirm_lineage.py (persist_rest.save at :419/:461 with
  nursery.save at :424/:459) and the Exchange import path
  itself (exchange.py:525, program.nursery.save inside
  the import sequence whose program half is a separate
  save).

### C1. Corrected writer taxonomy (supersedes B1's table)

B1's table listed writers by file touched and "lock
today," which invited the false inference that a LOCKED
program save plus a following nursery save inherits the
lock. The taxonomy is now by TRANSACTION SHAPE:

| Class | Shape | Lock / intent spanning the whole shape | Examples at audited base |
|---|---|---|---|
| T1 | Single-file write | The write itself is the transaction; canonical program saves hold `owner_state_lock` for that one write only | `persist_rest.save` (program file) |
| T2 | Single-file write, unlocked | Per-instance signature check only; no owner lock | `Nursery.save` (nursery file) |
| T3 | Caller-composed TWO-STEP logical pair update: a T1 and a T2 (either order) issued as one logical operation | **NONE.** No lock, journal, or intent record spans the two steps; the intermediate pair (one file new, one old) is durable and observable | confirm_lineage pair saves; the ordinary save path characterized independently by the 72-28 probes (H1 CONFIRMED both orders at main ed4ac00: an interrupted T3 leaves a hybrid live pair a fresh load exposes) |
| T4 | Journaled transaction with an intent record and a recovery path | The journal/intent IS the transaction boundary (its lock discipline is A1's subject) | Exchange import/recovery; checkpoint seal (72-28 CP0–CP4: never hybrid) |

Only T4 has a transaction-level pair boundary today.
T3 has none, and no wording in this plan may describe a
T3 update as "lock-held," "in-scope for the shared lock,"
or protected by P5-R validation.

### C2. Withdrawals (Amendment B text superseded)

1. **B2's P5-C-i repaired-code PASS rationale is
   WITHDRAWN.** It claimed the shared lock prevents /
   validates C-i because "S holds it; L's validation
   cannot pass mid-save." For a T3 saver that is false:
   after `persist_rest.save` returns, S holds nothing,
   and L's validation can pass in the inter-step window
   and ratify the intermediate hybrid as coherent.
2. **B1 step 3's soundness claim is WITHDRAWN as applied
   to T3 writers.** It asserted every in-scope pair
   writer "holds that same lock across its pair
   mutations, so none was mid-transaction at that
   instant." A T3 writer holds the lock across NEITHER
   step jointly; at the validation instant it can be
   exactly mid-logical-transaction with no lock held.
   The claim survives ONLY for T4 transactions after the
   A1 repair (repaired import/recovery holding the lock
   across their whole transaction) and for T1's single
   file.
3. **The general principle, stated plainly:** fingerprint
   equality across a read window proves the pair was
   STABLE during that window — no completed replacement
   intervened. Stability is not transaction-level
   coherence: a stable intermediate state of a T3 update
   is still an intermediate state. Equality of
   fingerprints at validation cannot prove semantic pair
   coherence for any writer without a common transaction.

### C3. The precise proposed contract (decision D-P5-2)

The Director's two offered shapes, made precise:

- **Option C-A — serialize T3.** A canonical pair-save
  funnel holds `owner_state_lock` across BOTH single-file
  writes of a logical pair update (the T1 save joins
  reentrantly; Nursery.save is invoked inside the same
  lock acquisition), and every in-scope caller composing
  a pair update is migrated to the funnel. Only then may
  a load claim pair coherence against T3 writers, and
  only for funnel users; direct T1/T2 callers remain
  outside the claim. This is a REAL scope expansion
  beyond the Q1 Exchange/recovery boundary: it touches
  persist_rest, Nursery, and their callers, and it
  overlaps the 72-28 Part B question (ordinary-path pair
  atomicity), which the Director has not ruled a repair
  for either. C-A therefore cannot be folded into the Q1
  repair by Uni's choice; it needs its own ruling.
- **Option C-B — exclude T3 and narrow the contract
  (RECOMMENDED for the Q1 circuit).** The load contract
  after the Q1 repair is stated as exactly:
  (i) per-file consistency for every load — each file
  exposed is one complete file generation
  (atomic_write's contract); (ii) pair coherence is
  claimed ONLY against T4 transactions (Exchange
  import/recovery under the A1 lock discipline, and the
  checkpoint seal) — the writers the Q1 repair actually
  serializes, where a transaction boundary exists to
  validate against; (iii) T3 two-step updates are
  EXPLICITLY EXCLUDED: a load concurrent with a T3
  update may expose its intermediate pair, and that
  exposure is a documented contract boundary, not a
  defect the Q1 repair claims to close; (iv) P5-R
  lock-light validation is retained ONLY as a detector
  for the T4 scope (journal appearance + fingerprint
  drift during the read window → locked retry / fail
  closed); it is NOT represented as proving coherence
  against T2/T3 writers. The unlocked-Nursery case in
  C4/P5-E is the standing counterexample that fixes this
  boundary.

**Decision requested (D-P5-2):** rule C-B as the Q1 load
contract (recommended), or rule C-A as a separately
scoped circuit (in which case the Q1 repair proceeds
under C-B's contract in the interim, and C-A is queued
with the 72-28 Part B question). The earlier D-P5
decision is superseded by D-P5-2; P5-R as originally
scoped in Amendment B is NOT presented for adoption.

### C4. Deterministic two-process counterexample SPEC (specification only — not executed by this amendment)

Harness law as in B2 (genuine child OS processes,
isolated owner/state dir, seams pause only at real code
boundaries and change no logic, verdicts from disk bytes
+ the loader's exposed state, two identical runs
required). Both cases are T3; NEITHER is protected by the
shared lock, and this plan does not call them protected.

- **P5-D — the inter-step window.** Writer W performs
  one logical pair update as a T3: it adds a unit whose
  program-side record references a nursery proposal,
  calls `persist_rest.save(program)` to completion, and
  the seam pauses W AFTER save() has returned (lock
  released, program file = new generation) and BEFORE
  `Nursery.save()` is called (nursery file = old
  generation). Loader L then runs a full
  `persist_rest.load`. Assert the ACTUAL result.
  Predicted verdict on current code (HYPOTHESIS, argued
  from C1's source facts, not a finding): L succeeds and
  exposes the intermediate pair — program-new /
  nursery-old. Asserted additionally against the FUTURE
  repaired code as a contract test: under C-B, L exposing
  that pair is CONTRACT-CONFORMING (T3 excluded) and the
  test pins the boundary so it can never be silently
  upgraded to a coherence claim; under a future C-A
  funnel, the same seam placed around the funnel call
  must instead show L blocked/retried or exposed only to
  a complete pair generation. The counterexample's
  force: any validation that PASSES in this window
  (P5-R as written in Amendment B would, the pair being
  stable) is thereby proven to certify stability, not
  coherence.
- **P5-E — unlocked nursery write completed BEFORE
  fingerprint capture.** Writer W performs the
  nursery-first half of a T3 update via a direct
  `Nursery.save()` and it COMPLETES; only then does
  loader L begin (journal probe + initial fingerprints
  F1). W's program half has not run. L validates.
  Predicted verdict (HYPOTHESIS, same status as P5-D):
  every fingerprint agrees at every step — the write is
  indistinguishable from a quiescent state — yet the
  exposed pair is the T3 intermediate (nursery-new /
  program-old). No fingerprint scheme can detect this
  case; detection would require a transaction/intent
  record the T3 writer never wrote. P5-E is the reason
  C3 claims detection only where a transaction boundary
  exists.

### C5. What is retained unchanged

- **P3 (B3) is retained in full:** the trusted entry
  snapshot S captured under the lock, the disposal-time
  `import_id` identity check, and the N0–N3 per-case
  re-established-outcome demonstrations. The Director's
  review ordered them retained; nothing in the P5
  correction touches them (P3 governs the T4 journal
  path, where a transaction boundary exists).
- B0 (A4 predicate = proposed design only), the A1 lock
  call graph for the T4 import/recovery transaction, the
  scope split (A2: SemanticGraph / per-Idea /
  core_i_recovery remain separate proposals), and the
  B4 evidence contract — extended so the repair circuit's
  failing-first set includes P5-D and P5-E with the
  C-B/C-A verdict semantics of C4, and mutant M5 is
  re-scoped: P5-R validation removed must be killed by
  the T4-scope probes (P5-A / P5-C-ii), NOT by P5-D/E,
  which pin the contract boundary rather than the
  validation.

### C6. Disposition

No code was modified by this amendment; no probe was
executed; P5-D/P5-E predictions are labeled hypotheses
for the repair circuit's failing-first run. The plan, as
corrected by Amendment C, is presented as ONE new frozen
plan head for a design ruling. Decisions requested:
**D-P5-2** (C3); acknowledgement that C1/C2 satisfy the
writer-taxonomy correction and that B3/P3 stands
retained. The #294 MERGE HOLD continues; Q1 repair
implementation remains STOPPED pending that ruling.

## Amendment D — response to the Director's Q1 Amendment C review (2026-11-05 06:18 CST)

Director review of plan head 2504a4b8 (Gmail id
1a1aba578ea3efbe, 2026-11-05 06:18 CST; archived verbatim at
responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_Q1_PLAN_R4.md):
**TARGETED_CORRECTION_REQUIRED — DESIGN ONLY.** Verified by
the Director: Amendment C's T1–T4 writer taxonomy, the
withdrawal of the P5-C-i pair-coherence assertion for T3,
the fingerprint-stability vs cross-file-coherence gap,
D-P5-2 (C-A vs C-B), P5-D/P5-E labeled hypothetical
specifications (not executed probes), and P3 journal
identity safeguards retained. No implementation, merge, or
certification is authorized by the review. W1/W2/W3 remain
SUBMITTED, not independently reproduced.

### D1. D-P5-2 decided as the design recommendation: C-B

Per the Director's directive ("Proceed with C-B as the Q1
design scope recommendation"), decision D-P5-2 is closed
inside this plan: **C-B is adopted.** Q1's repair scope is
the journaled T4 transactions (import / recovery) plus
per-file consistency for every other load. T3
caller-composed two-step pair updates are EXCLUDED from
Q1's coherence scope.

### D2. Mandatory NOT-GUARANTEED marking (binding wording)

The Director's condition on accepting C-B: the resulting
contract and public error/success wording must NEVER imply
coherent snapshots across excluded T3 writers. Any
implementation circuit, and the load/API documentation it
touches, MUST carry this marking in substance:

- Cross-file (program + nursery) pair coherence across T3
  writers is **NOT GUARANTEED**.
- A stable program/nursery pair is NOT necessarily a
  logically committed pair; fingerprint equality proves
  stability at an instant, never transaction coherence
  (the Director's finding, retained verbatim in substance).
- Pair coherence is claimed ONLY against T4 journaled
  transactions, where a transaction/intent boundary
  exists; every other load's guarantee is per-file
  consistency (each file a complete generation or a
  fail-closed refusal), nothing more.
- No success or error message, docstring, or acceptance
  criterion may describe an unvalidated or per-file load
  as exposing a coherent pair snapshot.

This marking is an acceptance criterion for the future
implementation circuit, not optional documentation polish.

### D3. C-A deferred — separate work, human authorization

C-A (serializing T3 pair updates through a canonical
pair-save funnel / spanning transaction) is retained as
SEPARATE FUTURE WORK requiring human authorization
(Ace/Director). It is not part of Q1, and it overlaps the
72-28 Part B question (ordinary-save pair atomicity),
whose repair likewise remains unruled. Nothing in this
plan builds, prototypes, or pre-authorizes C-A.

### D4. Evidence owed when an implementation circuit is presented

The Director orders, for the moment a SEPARATELY
AUTHORIZED implementation circuit is presented:
concrete FAILING-FIRST P5-D and P5-E observations
(executed two-process counterexamples with disk-byte
verdicts — not the C4 specifications alone) and journaled
T4 assertions for P5-A and P5-C-ii. Until that circuit
exists, P5-D/P5-E remain hypothetical specifications and
no P5-D/E counterexample execution or repair evidence
exists — this plan does not claim otherwise.

### D5. Retained and disposition

P3/B3 (trusted entry snapshot, disposal-time import_id
identity check, N0–N3 per-case demonstrations) and B0
(the A4 success predicate is PROPOSED DESIGN, not an
executed guarantee) are retained unchanged.

No code was modified by this amendment; no probe was
executed. The plan, as corrected by Amendment D, is
presented as ONE new frozen plan head for a design
ruling. The #294 MERGE HOLD continues; Q1 repair
implementation remains STOPPED pending a separately
authorized implementation circuit and the Director's
ruling on this head.

## Amendment E — 72-28 incorporated per the Director's Mode A assessment (2026-11-05)

Director Mode A assessment on 72-28 (2026-11-05, relayed by
Ace via copy-paste; archived at
responses/DIRECTOR_MODE_A_ASSESSMENT_2026-11-05_72_28.md):
the everyday-save defect demonstrated by 72-28 stays OPEN —
closing the proof circuit does not close the product defect.
Directive: keep PR #294 on hold; incorporate the 72-28
findings into Q1's transaction design, explicitly
distinguish ordinary saves from checkpoints, and provide a
failing-first regression for hybrid-state visibility. Do not
automatically merge Q1 merely because its design is
accepted. No certification or merge authorization issued.

### E1. What 72-28 demonstrated (evidence, not hypothesis)

72-28 (SM-35; PR #298 merged as MERGED_VERIFIED_BY_UNI,
merge a585a6d; evidence supplement PR #299) proved with
genuine child-process crash probes (two identical runs) and
suite form/sm35_pair_atomic_test.py (45/45 at b893931):

- An interrupted ORDINARY pair save (crash between the
  program save and the nursery save, either order) leaves a
  HYBRID live pair that a fresh load EXPOSES — no recovery,
  no refusal (H1-A/H1-B).
- The CHECKPOINT seal path never exposed a hybrid at the
  enumerated seams CP0-CP4 (OLD_ONLY via preserved-pair
  restore, or NEW_PAIR).

Director disposition on the proof itself:
INSUFFICIENT_EVIDENCE for independent confirmation
(2026-11-05 09:32 CST review; supplement supplied in PR
#299). The findings are incorporated here as Uni's
demonstrated results pending that confirmation.

### E2. Ordinary saves vs checkpoints — the design distinction

The transaction design now states the distinction the
findings turn on:

| | Ordinary save (persist_rest.save + nursery save, caller-composed) | Checkpoint seal (commit_checkpoint) |
|---|---|---|
| Intent journal | NONE | write_checkpoint_intent BEFORE the first durable write |
| Preserved pair | NONE | live pair preserved pre-seal |
| Load-time recovery | recover_checkpoint_intent runs, but with no journal for this write there is nothing to converge from | journal drives restore/convergence (recover_checkpoint_intent; second call site form/open.py:255 — unchanged per the 72-28 review, pending separately scoped review) |
| Crash between the two file writes | hybrid pair EXPOSED on fresh load (demonstrated, E1) | never hybrid at CP0-CP4 (demonstrated, E1) |
| Q1 class | T3 (caller-composed two-step pair update) | T4-like journaled transaction |

Consequences for this plan:

1. Amendment D's C-B adoption is UNCHANGED, and D2's
   NOT-GUARANTEED marking is strengthened from a design
   boundary to a DEMONSTRATED behavior for the ordinary-save
   path: cross-file pair coherence across T3 writers is not
   merely unguaranteed, it is observably violated by an
   interrupted ordinary save.
2. The Q1 repair scope (journaled T4 transactions plus
   per-file consistency) does NOT fix the ordinary-save
   hybrid exposure. No wording in this plan, the audit
   report, or any implementation circuit may imply it does.
3. The only designed route to ordinary-save pair atomicity
   remains C-A (canonical pair-save funnel / spanning
   transaction), retained by D3 as separate future work
   requiring human authorization. 72-28 Part B is the same
   question and is DEFERRED into this design per the Mode A
   directive — it is not separately tracked anymore.

### E3. Failing-first regression for hybrid-state visibility (provided, RED)

Artifact: director-reports/evidence/q1-audit/
q1_hybrid_visibility_probe.py — an evidence-bundle probe
(adapted from the 72-28 probe geometry: genuine child OS
processes, os._exit(42) between the two ordinary saves,
fresh-process load, on-disk hash classification). It asserts
the post-repair C-A contract: after an interrupted ordinary
pair save, a fresh load must expose OLD_ONLY or NEW_PAIR,
never HYBRID. Inconclusive verdicts (setup/crash/view
failure) exit 2 — never a pass.

Executed at this plan head's base (main a585a6d code),
2026-11-05, two runs, identical:

- q1_hybrid_visibility_run1.log: H1-A HYBRID, H1-B HYBRID,
  "CONTRACT VIOLATED", exit 1.
- q1_hybrid_visibility_run2.log: identical, exit 1.

This RED is the expected failing-first state. The probe is
NOT product code, is NOT registered in form/regress.py, and
changes no behavior. When a C-A circuit is separately
authorized, this probe is its failing-first seed: the
circuit's acceptance requires it green (exit 0) plus the
SM-35 suite still green. Under C-B as adopted, the probe
stays RED by design and the D2 marking governs all public
wording.

### E4. Status and disposition (Amendment E)

- The everyday-save hybrid defect is OPEN (Director ruling,
  Mode A). 72-28's proof circuit is closed; the defect is
  not.
- PR #294 remains HELD. Design acceptance — including any
  future acceptance of this amendment — is NOT a merge
  authorization (the Director's explicit warning, recorded;
  Ace's standing rule merges Director CONFIRMATIONS, and an
  accept-with-hold is not one).
- Q1 repair implementation remains STOPPED pending a
  separately authorized implementation circuit. Amendment E
  changes design and evidence only: no product code was
  modified; the one executed artifact is the E3 probe,
  whose RED result is recorded above.

### E5. Questions for the Director (added by Amendment E)

Q-E1. With 72-28 incorporated, should the eventual
implementation authorization be sought for C-B alone
(journaled T4 scope, ordinary-save hybrid exposure left
OPEN under the D2 marking), or should C-A be scoped as a
companion circuit so the demonstrated defect has a repair
path on the register?
Q-E2. Is the E3 probe's contract (fresh load exposes
OLD_ONLY or NEW_PAIR after an interrupted ordinary save)
the correct acceptance shape for a future C-A circuit, or
should C-A's contract additionally require that the hybrid
never reaches disk-visible state at any instant (a stronger
property than load-time convergence)?

## Amendment F — Director ruling on Amendment E recorded (2026-11-05)

Director review of plan head 8d9d71f5 (Gmail id
1a1aca1b2fd53ec9, 2026-11-05 10:54 CST; archived verbatim at
responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_Q1_AMENDMENT_E.md):
**TARGETED CORRECTION / DESIGN HOLD** — not implementation
authorization, not certification. Verified by the Director:
Amendment E's T3/T4 distinction, the OPEN hybrid exposure,
the proposed failing-first C-A contract with two reported
RED runs, and the statement that C-B does not fix
ordinary-save hybrid exposure. The probe and its logs are
submitted evidence, not Director-executed.

### F1. Disposition (unchanged hold, restated as binding)

- C-B is retained as the separately bounded Q1 design scope.
- The ordinary-save hybrid defect remains OPEN.
- C-A remains separately authorized future repair work; it
  is not authorized by this ruling or by Amendment E.
- The E3 RED probe is NOT a passing regression, NOT merge
  authorization, and NOT evidence of repair. It is a
  failing-first artifact only.
- PR #294 stays HELD. No source changes or merges are
  authorized.

### F2. Preconditions for any future C-A implementation request

Before a C-A implementation circuit may even be REQUESTED,
Uni must supply, and the request must carry:

1. A reproducible INDEPENDENT failing-first run of the
   hybrid-visibility probe at a pinned code SHA (the
   verify_72_28 pattern: pinned script + independently
   executed receipt, e.g. GitHub Actions at the exact head —
   Uni's local RED logs alone do not satisfy this).
2. Verification of the probe's clean setup and
   fresh-process visibility (the probe's owners start from
   no pre-existing state; the classifying view runs in a
   genuine fresh process; inconclusive verdicts fail the
   run, never pass it).
3. An explicit acceptance definition, chosen and stated in
   the request: whether C-A acceptance requires LOAD-TIME
   CONVERGENCE ONLY (a fresh load never exposes a hybrid;
   a transient hybrid may exist on disk between the two
   writes) or NO DISK-VISIBLE HYBRID AT ANY INSTANT (the
   stronger property). This answers Q-E2 procedurally: the
   definition is part of the request, decided before
   implementation is sought — it is not yet chosen.

### F3. Effect on Amendment E's questions

- Q-E1 is answered in substance: C-B proceeds (when
  authorized) as the bounded scope; C-A is a separate
  companion question with its own authorization — the two
  are not merged into one request.
- Q-E2 is carried into F2(3) as a precondition.

No code was modified by this amendment; no probe was
executed. The plan, as corrected by Amendment F, remains
frozen under the design hold pending the Director's further
ruling.
