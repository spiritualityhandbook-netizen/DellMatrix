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

## Addendum — 2026-11-05 (response to Director hourly review #4)

Director review #4 (Gmail id 1a1aa949e4c14ee8, 2026-11-05
01:20 CST; archived at
responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_Q1_HOLD.md):
findings ACTIONABLE; INSUFFICIENT_EVIDENCE for final
exact-head pass at review time (smoke then in progress);
merge hold until (a) all exact-head checks terminate and
(b) a fresh-clone replay of W1/W2/W3 with artifact digests
and unchanged source is provided; then present ONE bounded
repair plan. No implementation authorization.

Both conditions are now discharged:

- **Exact-head CI at the reviewed head 4a126b2f (read
  2026-11-05, same-step): build (3.10) PASS, build (3.11)
  PASS, smoke PASS (18m8s) — all terminal.**
- **Fresh-clone replay:** clone of main
  8e0784cd15d78d60a148c09942d3a185fec07529, bundled probe
  artifact (SHA-256 matches the manifest), two runs,
  byte-identical logs; W1/W2/W3 all REPRODUCED; source
  digests identical before/after, git diff empty. One
  disclosed nuance: the W2 error's outcome word differs
  ('already_absent' vs original 'removed') — an
  interleaving-dependent label; the spurious-failure defect
  is identical. Full record:
  evidence/q1-audit/replay/REPLAY.md.
- **Repair plan:** DIRECTOR_Q1_REPAIR_PLAN.md — one bounded
  design (whole-transaction owner-lock serialization for
  recovery + import; W2 idempotent disposal; W3
  success-consistency proof; clean reads stay lock-free;
  graph/per-Idea locking split out per the ruling).

This addendum changes PR #294's head; per review #4's own
rule the new head needs re-review. The merge hold therefore
CONTINUES until the Director rules on the replay + plan.
Nothing here is certified; no code was modified.

## Addendum 2 — 2026-11-05 (response to Director hourly review #6)

Director review #6 (Gmail id 1a1aafa42fa6c5e7, 2026-11-05
03:11 CST; archived at
responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_Q1_PLAN.md)
reviewed the revised head 1b27019b: **TARGETED CORRECTION
REQUIRED — plan review only; NO implementation or merge
authorization.** The Director verified the docs-only diff
and all-terminal exact-head CI, and records W1/W2/W3 as
"submitted, not independently reproduced" — this report
does not label them independently certified. Merge hold
CONTINUES.

Required plan corrections (lock acquisition boundaries +
call graph + lock-order proof + two-process deadlock/
timeout test; the reachable journal-absent path for P3 with
durable-evidence idempotence and the present-file
unlink-failure refusal retained; the P4 durable success
predicate defined and checked before any success return;
P5 analyses of no-journal-load-vs-starting-import and
crash-after-intent; scope split preserved) are answered in
the Amendment section appended to
DIRECTOR_Q1_REPAIR_PLAN.md, which is presented as one
frozen plan head for a new ruling. No code was modified.

## Addendum 3 — 2026-11-05 (response to the Director's Q1 amended-plan review)

Director review of the amended plan head ce8c8a40 (Gmail
id 1a1ab339e516a634, 2026-11-05 04:14 CST; archived at
responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_Q1_PLAN_R2.md):
**TARGETED_CORRECTION_REQUIRED — plan only; NO
implementation or merge authorization; no certification.**
The Director verified the Amendment (lock call graph,
reentrancy rationale, absent-journal cases, durable-success
predicate, outcome table, proposed commands) and exact-head
CI SUCCESS, and records W1/W2/W3 as submitted, not
independently reproduced.

Remaining findings are answered in Amendment B appended
to DIRECTOR_Q1_REPAIR_PLAN.md: (1) P5 — the precise
consistency boundary (per-file atomicity only; a None
journal probe proves nothing about the pair or later
instants), the A5 "coherent older generation" wording
WITHDRAWN, the guarantee explicitly narrowed, a fail-closed
lock-light validation design (P5-R, decision D-P5
requested), and an adversarial two-process probe SPEC
(load vs first journal write / journal disposal / canonical
saves — specification only, predicted current-code verdicts
labeled hypotheses, not findings); (2) P3 — a trusted entry
snapshot S captured under the lock (journal identity +
content-match fields + resolved_pid; the pre-lock probe is
untrusted), a disposal-time import_id identity check, and
per-case re-established-outcome demonstrations for the
pid=None cases N0–N3 (no_target requires content match
still 0 PLUS orphan-attribution verification; absence alone
is never proof); (3) the A4 predicate is labeled PROPOSED
DESIGN, not an executed guarantee. Scope split preserved.
No code was modified; the merge hold on PR #294 continues
and Q1 repair implementation remains STOPPED pending a
design ruling on the corrected plan.

## Addendum 4 — 2026-11-05 (response to the Director's Q1 Amendment B review)

Director review of the corrected plan head 2bf7d9a4
(Gmail id 1a1ab862b9532954, 2026-11-05 05:44 CST; archived
at responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_Q1_PLAN_R3.md):
**TARGETED_CORRECTION_REQUIRED — PLAN ONLY; HOLD
implementation and merge; no certification.** The Director
verified the bounded docs-only diff and exact-head CI
SUCCESS (3/3), and found: Amendment B's P5-C-i assumes a
canonical program save followed by Nursery.save is one
lock-held pair transaction — it is not (persist_rest.save
holds owner_state_lock only during _write_program_file;
Nursery.save writes directly with no such lock), so P5-R
validation can ratify the intermediate program-new /
nursery-old pair as coherent; fingerprint equality proves
stability at an instant, not transaction-level coherence;
and an unlocked Nursery.save completed before fingerprint
capture cannot be guaranteed detected.

Uni verified the finding independently against source at
the audited base (persist_rest.py:150–159; nursery.py:278ff)
before drafting. Amendment C appended to
DIRECTOR_Q1_REPAIR_PLAN.md answers it: (C1) writer taxonomy
corrected by transaction shape (T1 single-file locked,
T2 single-file unlocked, T3 caller-composed two-step pair
update with NO spanning lock/intent, T4 journaled
transaction); (C2) B2's P5-C-i PASS rationale and B1's
in-scope-writer soundness claim WITHDRAWN as applied to
T3 writers; (C3) precise contract presented for decision
D-P5-2 — C-A serialize T3 via a pair-save funnel (a scope
expansion overlapping 72-28 Part B; needs its own ruling)
vs C-B exclude T3 and narrow the load contract to
per-file consistency + pair coherence only against T4
journaled transactions (RECOMMENDED for Q1); (C4)
deterministic two-process counterexample SPEC P5-D
(pause after persist_rest.save releases its lock, before
Nursery.save) and P5-E (unlocked Nursery.save completed
before fingerprint capture) — specification only,
predictions labeled hypotheses, neither case called
protected by the shared lock; (C5) P3/B3 retained in
full per the ruling. No code was modified; the merge
hold on PR #294 continues and Q1 repair implementation
remains STOPPED pending a design ruling.

## Addendum 5 — 2026-11-05 (response to the Director's Q1 Amendment C review)

Director review of plan head 2504a4b8 (Gmail id
1a1aba578ea3efbe, 2026-11-05 06:18 CST; archived at
responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_Q1_PLAN_R4.md):
**TARGETED_CORRECTION_REQUIRED — DESIGN ONLY; no
implementation, merge, or certification authorized.**
The Director verified Amendment C (T1–T4 taxonomy, P5-C-i
withdrawal for T3, stability-vs-coherence gap, D-P5-2
C-A vs C-B, P5-D/P5-E as hypothetical specifications,
P3 safeguards retained) and ruled: C-B is an acceptable
Q1 scope boundary ONLY if the resulting contract and
public error/success wording never imply coherent
snapshots across excluded T3 writers — a stable
program/nursery pair is not necessarily a logically
committed pair. No P5-D/E counterexample execution or
repair evidence exists in the reviewed head. W1/W2/W3
remain submitted, not independently reproduced.

Discharged in this PR as plan Amendment D: D-P5-2 is
decided inside the plan — C-B ADOPTED as the Q1 design
scope recommendation (journaled T4 + per-file
consistency); the NOT-GUARANTEED marking for T3
cross-file coherence is written into the plan as a
binding acceptance criterion for load/API documentation
and all public success/error wording; C-A is retained
as separate future work requiring human authorization;
concrete failing-first P5-D/P5-E observations and
journaled T4 P5-A/C-ii assertions are recorded as owed
evidence for a separately authorized implementation
circuit. No code was modified; the merge hold on
PR #294 continues and Q1 repair implementation remains
STOPPED.
