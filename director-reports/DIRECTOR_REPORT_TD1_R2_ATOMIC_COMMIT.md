# DIRECTOR REPORT — TD-1-R2: Atomic Owner-State Commit Protection

**Date:** 2026-11-04
**From:** Uni Ω (via Ace / Overseer)
**Circuit:** TD-1-R2 (repair directive from the Director's TD-1-R1
review, PR #284 archive)
**Base:** main `d58fbf2` (post-Water). **Status:** SUBMITTED FOR
REVIEW at one frozen candidate; TD-2 not started.

## The defect being repaired, in the Director's own framing

R1's fingerprint gate is an optimistic version check, not a fully
atomic compare-and-swap: validation and final replacement were
separate moments, and two writers could both pass the comparison
before either saved. R1 was accepted WITHIN VERIFIED SCOPE; TD-1
certification was deferred on exactly this guarantee, and TD-2
stayed unauthorized until it closes.

## What R2 builds

**One new authority, `form/owner_state_lock.py`** — the
repository's first file lock, deliberately singular (used by both
callers below, never re-implemented per caller):

- A kernel-held `flock` per owner on a lock file in the state
  directory's `.locks/` subfolder, named from the canonical state
  file via the same `persist._path` authority. Different owners
  use different files and never block each other.
- **The lock file is NEVER unlinked**: unlinking a lock file
  splits the lock across inodes and silently re-opens the race.
  Kernel-held also means a holder that dies — including SIGKILL —
  releases automatically; there is no stale-lock file to guess at.
  (The subfolder placement is a regression finding: a lock file
  sitting beside the state file was flagged as residue by three
  suites' owner-cleanup contracts. The never-unlink rule is
  unchanged; only the folder moved.)
- **Bounded acquisition**: 10.0 s of polling, then
  `OwnerLockBusy`. An unbounded wait turns contention into a
  hang; a zero wait turns normal contention into spurious
  failures. The bound is part of this contract.
- **Fail-closed platform rule** (§31.2 applied): if neither
  `fcntl` nor `msvcrt` locking exists, acquisition raises
  `OwnerLockUnavailable`. It never falls back to running
  unlocked.
- Re-entrancy is per process+thread by depth count, so bind's
  inner save joins bind's own transaction.

**Bind** (`unit_binding.bind_unit_to_idea`): the complete R1
protocol — entry read, F1 unreadable refusal, stamp/staleness,
persisted-pointer authority, mint, commit gate, save — now runs
inside the lock as one transaction. A lock that stays busy past
the bound refuses the bind as `BindingRefused(state_locked)`
before any mutation. R1's fingerprint gate is retained, now as
the detector for writers outside the funnel (below).

**Ordinary saves** (`persist_rest.save`): a save to the
CANONICAL owner path runs inside the same lock — no canonical
save bypasses the transaction — and under it a binding guard
refuses the one silent harm the directive names. The guard is
currency-aware (this shape is the product of two full-regression
rounds, detailed under Evidence):

- A **current** instance (its R1 version stamp matches the
  canonical file it last loaded/saved) is authoritative: its
  in-memory bindings are the latest intent, including
  deliberately clearing a pointer, and it saves freely.
- A **stale or unstamped** instance may save only if it carries
  every persisted (unit → idea_id) binding identically; losing
  or re-pointing one it never saw raises `BindingLossSaveError`.
- Absent or unparseable canonical state carries no readable
  bindings, so a live instance's save over corrupt bytes remains
  the repair path (load still refuses to load such a file; bind
  still refuses to mint over it).

Non-canonical paths (explicit temp or checkpoint files) are
outside the transaction: they are not the canonical state.

## "No lost bindings" — pinned meaning

The lock serializes writers; it does not merge them. The loser
of a race receives an EXPLICIT refusal, reloads, retries, and
succeeds. Verified end state (suite check 9): after the retry,
the canonical state carries BOTH bindings. R2 never claims both
racing writers succeed in one pass.

## Evidence (labels per the realism ladder)

- **Failing-first:** on pristine main, the new suite fails at
  check 1 — a stale instance's ordinary save proceeds silently
  and the binding is lost (the exact defect the Director cited).
  Behavioral, not import-level.
- **Suite `form/track_d_td1_r2_test.py`: 23/23** (registered,
  canonical count 235), including **CROSS_PROCESS** evidence:
  genuine subprocesses coordinated by barrier files with bounded
  waits — same-unit race (exactly one binds, exactly one shell
  minted, persisted pointer is the winner's), different-units
  race (one refused, reload+retry, both bindings persist),
  a SIGKILLed lock holder's lock recovering within the bound,
  a live holder producing bind's `state_locked` refusal and a
  contender's bounded busy, an ordinary save provably unable to
  bypass a held lock, re-entrant bind+save under an outer lock,
  two-owner non-blocking, a failed commit releasing the lock,
  the binding-keyed refusal and its narrowed other half (a stale
  save losing NO binding proceeds), a current instance's
  deliberate pointer-clear saving cleanly, F1 re-pinned under
  the lock, and zero SemanticGraph writes (file hashes).
- **Mutants, four, each killed by its own target:** binding
  guard removed → check 1 dies; lock removed from bind → the
  state_locked check dies (bind charges into a doomed save and
  fails as BindingFailed instead of refusing cleanly); lock
  removed from save → the save-bypass check dies; currency
  bypass removed → the deliberate-clear check dies with the
  exact BindingLossSaveError signature full regression caught.
- **Regression rounds (the scoping evidence, reported in full):**
  Round 1 (general stale refusal): **229/235 RED** — six suites
  in three classes, each classified: legitimate whole-state
  flows (snapshot restore, generation rollback, unbound
  two-instance authoring) broken by the over-broad refusal;
  lock-file residue; one coverage registration. The save rule
  was narrowed to the directive's exact harm (bindings).
  Round 2 (binding-keyed refusal): **234/235 RED in all three
  legs**, sole red TD-1 — deterministic in-chain, green via its
  `__main__` path, red via `smoke()`; root-caused to TD-1's
  round-trip contract deliberately clearing a pointer before
  saving. The guard became currency-aware (above).
  Round 3 (final): **235/235 GREEN ×3** (fwd / `--twice` /
  `--order rev`). TD-1 24/24 and R1 10/10 unchanged throughout.
  (TD-1's `__main__` count assertion also fails on pristine
  main; `smoke()` is its regress contract and is green on both —
  pre-existing, out of scope, noted for the record.)
- **Exact-head CI:** runs on this frozen candidate; merging is
  gated on its terminal PASS under the hard merge gate.

## Boundary — what the fence does NOT cover (stated, not implied)

The lock fences the canonical funnel: bind and ordinary saves
through `persist_rest.save`. Direct canonical writes that are
NOT ordinary saves remain outside it: **Exchange import**
(`form/dell_matrix/exchange.py`, own journal/recovery),
**core_i_recovery** journal-driven writes, and checkpoint
generation member files. For those paths the R1 fingerprint
gate remains the detector on the bind side, but no atomicity is
claimed for them here. Whether they should be pulled under the
lock is a scope decision (Q1). "No path can bypass" is
explicitly NOT claimed.

Also same-machine scope only: kernel flock coordinates
processes on one machine/filesystem; no multi-host claim
(mirroring atomic_write's own stated boundary).

One further honest limit of the save-side guard: it protects
BINDINGS, not all state. Two stale instances authoring unbound
state remain last-writer-wins under the lock's serialization —
that is the pre-R2 product semantics for unbound state, and the
directive's named harm is the binding. If the Director wants
general lost-update refusal for all state, the legitimate-flow
classifications from Round 1 are the design input for that
separate decision (Q3).

## SWAT pre-mortem outcomes (abridged)

Fork bombs / self-deadlock: bind's inner save joins by depth
count (check 7). REPL/Studio hangs: acquisition is bounded at
10 s with an honest busy error instead of an infinite wait.
Suites saving from two instances alternately: classified by the
regression rounds above — currency decides, no suite is exempted
by name. Lock-file litter: one small file per owner in `.locks/`,
never unlinked by design.

## Anticipated probes

- **"Does checkpoint() nest safely?"** checkpoint calls save;
  under bind's outer lock it joins by depth count; the
  regression covers checkpoint suites.
- **"What stops two threads in one process racing?"**
  Re-entrancy is per-thread: different threads contend for the
  real kernel lock (suite check 4 proves a contending thread's
  busy refusal; check 4b proves a save cannot bypass a held
  lock).
- **"Why is the corrupt-save path not a hole?"** The guard
  compares bindings; unreadable bytes carry none. Overwriting
  VALID newer state while dropping its bindings is refused
  unconditionally for any writer that did not itself produce
  the current version.
- **"Is the 10 s bound right for the Studio server?"** Saves
  and binds are short transactions; the bound only fires under
  pathological contention, where an honest refusal beats a hang.

## Questions for the Director

- **Q1.** Should Exchange import and core_i_recovery's journal
  writes be pulled under the owner-state lock in a follow-on
  circuit, or is the funnel fence (bind + ordinary saves) the
  intended permanent boundary?
- **Q2.** With the concurrent-write guarantee closed, is TD-1
  now certifiable, and is TD-2 (owner-visible binding surface)
  authorized to proceed?
- **Q3.** Is binding-scoped lost-update protection the intended
  permanent save contract, or should general stale-state refusal
  be designed separately against the Round 1 flow
  classifications?
