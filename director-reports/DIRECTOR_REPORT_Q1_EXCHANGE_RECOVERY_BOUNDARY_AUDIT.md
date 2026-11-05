# Director Report — Q1 Exchange/Recovery Boundary Audit (G-03)

Status: SUBMITTED (Uni evidence; certification is the Director's)
Base audited: main 8e0784cd15d78d60a148c09942d3a185fec07529
(mapping at aeca07c; relevant code identical at 8e0784c)
Date: 2026-11-05 (SUSX100,000 sleep run, Cycles 10–11)
SWAT calibration: proportionate falsification — audit only, no
modification. NO code was changed by this circuit.

## Question

TD-1-R2 put canonical saves, binding, and containment inside
`form.owner_state_lock`. The Director's Q1 (Mode D review,
2026-11-04): Exchange/recovery writes must EVENTUALLY respect
the same boundary — audit first, no modification without a
ruling; preserve journal ordering / crash safety; no
indiscriminate lock-wrapping.

## Inventory (FACT, source-read)

LOCKED: `persist_rest.save` (canonical path only),
`unit_binding.bind`, `unit_containment` ops — and, by
inheritance, any `SemanticGraph.save()` / `Nursery.save()`
those funnels perform while holding the lock (reentrant).

UNLOCKED writers of canonical files:
1. `persist_rest.load` runs five recorded-intent recoveries
   BEFORE exposing state, several writing canonical files via
   `atomic_write_json`: the four `core_i_recovery` recoveries
   and `exchange.recover_exchange_import` — the last is a
   read-modify-write of BOTH canonical files (whole raw dicts).
2. `exchange.import_packet`: journal writes are direct;
   `Nursery.save()` (nursery file) never takes the lock; the
   one final `program.save()` is locked.
3. `core_i_recovery` journal/staging writes, and its nursery
   heals at load (canonical nursery file).
4. NEW in this cycle's sweep (61 `atomic_write_json` sites
   classified; full grep in evidence): `SemanticGraph.save()`
   writes a FOURTH canonical file, `graph_<owner>.json`, with
   no lock at the graph layer — lock coverage depends entirely
   on the caller. Same class: graph journal writes and
   `idea_persist.save_idea` (per-idea files). Sealed-generation
   writes (checkpoint manifest/pointer/members), checkpoint
   copy files, staging files, and export packets are NOT live
   canonical state and are out of scope.

Already disclosed, not hidden: the R2 report and the
`persist_rest.save` docstring state this boundary verbatim.

What is sound: per-file atomicity everywhere; import journal
ordering (intent before mutation, disposal only after durable
verification); fail-closed recovery (state is never exposed
over unresolved evidence); the lock is reentrant per
process+thread, so wrapping load recovery would not
self-deadlock same-process callers.

## Probe evidence — W1/W2/W3 are CONFIRMED, not hypotheses

Probe: `evidence/q1-audit/q1_probe.py` (SHA-256 in
`evidence/q1-audit/MANIFEST.sha256`), run twice at the audited
base with identical verdicts (`q1_probe_verdicts.json`).
Genuine child OS processes; coordination seams ONLY pause at
real code boundaries (`exchange._raw_state_files` after its
real read returns; `exchange.record_receipt` on first call
during a real import). A seam changes no logic and holds no
lock — it makes the code's own window deterministic.
Evidence label: CROSS_PROCESS with disclosed seams.

- **W1 — CONFIRMED, silent data loss.** A recovery process
  read a partial-import snapshot; a second process committed
  a marker unit through the LOCKED `persist_rest.save` funnel
  (marker verified on disk); recovery then wrote its stale
  whole-dict snapshot back. Final program file: marker GONE.
  Recovery itself reported "removed" — its job succeeded
  while erasing a newer locked save's unrelated change.
- **W2 — CONFIRMED, spurious load failure.** Two processes
  recovered the same partial import concurrently. State ended
  clean and the journal disposed, but ONE recoverer raised
  `ExchangeError` ("recovery established 'removed' but the
  import journal could not be cleared" — the other process
  had disposed it). A concurrent load fails closed spuriously
  over already-clean state: availability harm, not corruption.
- **W3 — CONFIRMED, success-reported incoherence.** An import
  paused after landing (journal + nursery proposal durable,
  final save pending); a second process loaded — recovery
  removed the proposal from the nursery file and disposed the
  journal (loader outcome "loaded"). The importer then
  finished and returned `ok=True` (`journal_retained=True`
  disclosed). Final files DISAGREE: the program file holds
  the import's `exchange_seeds` + `exchange_receipts` for the
  pid; the nursery file has NO such proposal — orphaned
  exchange entries under a successful import result.

## Options for the Director (audit presents; does not choose)

- **O1:** wrap the five load-time recoveries in
  `owner_state_lock` inside `persist_rest.load`. Smallest
  change; cross-process loads serialize with saves. Risk:
  load can newly raise `OwnerLockBusy` — a new failure
  surface for every reader. (W2's disposal race also needs a
  disposal-idempotence answer under any option.)
- **O2:** lock only the recovery WRITES (recover functions
  acquire when a journal requires a write). Keeps pure loads
  lock-free; more call sites to keep honest.
- **O3:** leave recovery unlocked; guard import's final save
  with a journal/epoch check (refuse/resync if recovery
  removed the import mid-flight). Fixes W3's reported
  success; W1/W2 remain.
- **O4:** status quo + documented boundary (R2 already
  discloses it), if the Director accepts the priced windows
  for the single-user localhost scope.

## Anticipated probes

1. "Is W1 reachable without your seam?" The seam pauses after
   a real read; between that read and the writeback the code
   holds no lock and performs no fingerprint recheck — any
   interleaving in that interval, however narrow in wall
   time, has the same effect. The window is structural, not
   timing luck.
2. "Does W3's `journal_retained=True` make it honest?" It
   discloses the disposal fact; it does not disclose that the
   proposal was removed or that the final files disagree.
   `ok=True` remains the headline a caller acts on.
3. "Why not also fence the graph file here?" Scope: Q1 names
   Exchange/recovery. The graph-layer finding is reported as
   a sibling of the same class for the Director to route.

## Questions for the Director

- Q1-1: Which option (O1–O4), or combination (e.g. O1+W2
  disposal idempotence), should the repair circuit implement?
- Q1-2: Should the graph file (`SemanticGraph.save`) and
  per-idea files join the same repair circuit, or a separate
  one?
- Q1-3: Is a spurious `OwnerLockBusy` on load (O1's cost)
  acceptable for readers, or must load stay lock-free for the
  no-journal common case (pointing to O2)?

STOP: no modification without the ruling on Q1-1.
