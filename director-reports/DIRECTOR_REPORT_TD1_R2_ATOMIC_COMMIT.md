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

- A kernel-held `flock` per owner on a lock file beside the
  canonical state file (`program_<owner>.json.lock`), derived
  from the same `persist._path` authority. Different owners use
  different files and never block each other.
- **The lock file is NEVER unlinked**: unlinking a lock file
  splits the lock across inodes and silently re-opens the race.
  Kernel-held also means a holder that dies — including SIGKILL —
  releases automatically; there is no stale-lock file to guess at.
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
CANONICAL owner path runs inside the same lock, and under it a
saver whose version stamp no longer matches the canonical file's
valid state is refused with `StaleStateSaveError` — an ordinary
save can no longer silently overwrite newer state, including a
newer binding. Unstamped instances (fresh, constructed,
checkpoint-restored) carry no baseline and save as before;
non-canonical paths (explicit temp/checkpoint files) are outside
the transaction, as they are not the canonical state.

**Two bounded allowances on the stale rule, disclosed:**
an ABSENT canonical file (nothing exists to protect — a
delete-then-replace by another writer leaves a file behind,
which the fingerprint rule then catches), and a file that exists
but does NOT parse (corrupt bytes carry no readable state and no
binding to lose; a live instance is the only recovery source and
its save is the repair). Bind's own rules are stricter and
unchanged: bind still refuses to mint over corruption (F1) and
never resurrects a vanished file. These allowances exist because
the first R2 draft refused both — and the R1 suite's own
corrupt-state REPAIR step (rewriting canonical state from a live
instance after external corruption) proved to be a legitimate
recovery flow the stricter rule broke. The mechanism was
corrected, not the suite.

## "No lost bindings" — pinned meaning

The lock serializes writers; it does not merge them. The loser
of a race receives an EXPLICIT refusal, reloads, retries, and
succeeds. Verified end state (check 9): after the retry, the
canonical state carries BOTH bindings. R2 never claims both
racing writers succeed in one pass.

## Evidence (labels per the realism ladder)

- **Failing-first:** on pristine main, the new suite fails at
  check 1 — a stale instance's ordinary save proceeds silently
  (the exact lost-update the Director cited). Behavioral, not
  import-level.
- **Suite `form/track_d_td1_r2_test.py`: 20/20** (registered,
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
  the corrupt-save repair allowance, F1 re-pinned under the
  lock, and zero SemanticGraph writes (file hashes).
- **Mutants, three, each killed by its own target:** stamp
  refusal removed → check 1 dies; lock removed from bind → the
  state_locked check dies (bind charges into a doomed save and
  fails as BindingFailed instead of refusing cleanly); lock
  removed from save → the save-bypass check dies.
- **Neighbors unchanged:** TD-1 24/24, TD-1-R1 10/10.
- **Regression ×3 and exact-head CI:** [FINAL NUMBERS AT FREEZE]

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

## SWAT pre-mortem outcomes (abridged)

Fork bombs / self-deadlock: bind's inner save joins by depth
count (check 7). REPL/Studio hangs: acquisition is bounded at
10 s with an honest busy error instead of an infinite wait.
Suites that save from two instances alternately: the full
regression ×3 is the arbiter — any suite depending on a stale
save surfacing as a refusal rather than a pass is reported
above, not quietly exempted. Lock-file litter: one small file
per owner, never unlinked by design.

## Anticipated probes

- **"Does checkpoint() nest safely?"** checkpoint calls save;
  under bind's outer lock it joins by depth count; the
  regression covers checkpoint suites.
- **"What stops two threads in one process racing?"**
  Re-entrancy is per-thread: different threads contend for the
  real kernel lock (check 4 proves a contending thread's busy
  refusal).
- **"Why is the corrupt-save allowance not a hole?"** It
  applies only when the on-disk bytes do not parse as state at
  all — there is no newer binding in unreadable bytes to lose;
  overwriting VALID newer state is refused unconditionally.
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
