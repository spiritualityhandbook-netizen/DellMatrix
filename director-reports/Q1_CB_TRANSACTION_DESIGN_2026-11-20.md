# Q1 C-B TRANSACTION DESIGN — Exchange Import/Recovery Pair Consistency

**Part I (Architecture) — plan-stage design artifact, 2026-11-20.**
Branch `uni/part-1-architecture`, base main
`af2519b6d239ef278397e277210d6da2467c36e5`.
Register anchor: MWL **#118** (Q1 family, **GATED** — PR #294 GATE HOLD).
Authority source: Director ruling **7040542941** (C-B/C-A split, Q-E2
minimum) and `DIRECTOR_Q1_REPAIR_PLAN.md` on the PR #294 branch
(Amendments D/F; A3 P3 journal-absent path; A5/B1 P5 consistency
boundary + P5-R fail-closed validation; mutants M1/M2/M3).

> **Gate statement.** This document is DESIGN ONLY. C-B *code* is not
> authorized and none is written in this PR. The failing-first prep
> suite ships as `form/q1_cb_exchange_recovery_prep_test_spec.py`
> (see §7 for the `_spec` naming rule). PR #294 never merges under
> the GATE HOLD. The exact ask this design supports is named in §8.

---

## 1. The defect family (measured, current main)

The Exchange import path (`form/dell_matrix/exchange.py`:
`import_packet` :692, `recover_exchange_import` :589,
`_dispose_import_journal` :544, `_clear_import_journal` :431,
`_raw_state_files` :457, `record_receipt` :909) writes a pair —
the imported proposal/seed state plus its journal — without a
transaction contract that survives interruption coherently. The
prep suite (7 cases, CROSS_PROCESS children) measured on current
main, 2026-11-20:

| Case | Verdict | Measured detail |
|---|---|---|
| CB-W1 | **FAIL** | Recovery removes the journal AND erases the completion marker: `saver=saved, recover=removed, marker_after_recovery=False`. After recovery, no durable witness remains that the pair-write committed — silent evidence loss. |
| CB-W2 | **FAIL** | Recovery raises a spurious `ExchangeError` over a clean, fully-written state — recovery cannot distinguish "complete pair, stale journal" from "torn pair". |
| CB-W3 | **FAIL** | Importer reports `ok=True` while the landed pair is incoherent: `proposal=False, seed=True, receipts=True, coherent=False` — success is claimed for a half-landed import. |
| CB-W2F | PASS | Fault-injected disposal failure fails closed; journal retained for retry/audit. |
| CB-P3 | PASS | Idempotent disposal: first recovery call returns `removed`, second returns `none` — disposing a completed journal twice has exactly one effect. |
| CB-P5 | PASS | No journal at all: recovery returns `none` with zero writes (purity of the absent path). |
| CB-P5D | PASS | Corrupt journal: `ExchangeError` raised, journal bytes retained as evidence (fail-closed, no silent discard). |

Net: **4/7** — the three failures are one failure class: *the
import/recovery pair has no declared commit boundary, so recovery
guesses — and guesses wrong in both directions (erases evidence on
success, errors on clean state, blesses torn state).*

## 2. The C-B contract (what the repair must prove)

C-B is the **Exchange-local** transaction: one import, one owner,
the proposal/seed pair plus its journal. Four properties:

- **P3 — Journal identity + idempotent disposal.** The journal is
  the import's identity: it names the import id, the pair members,
  and the intended final state. Disposal happens exactly once,
  only after the completion marker is durable; a second disposal
  attempt is a `none` no-op (CB-P3 shape), never an error and
  never a second effect.
- **P5 — Fail-closed two-file consistency.** A fresh load/recovery
  exposes the pair as OLD_ONLY or NEW_PAIR (the Q-E2 minimum,
  §5), never a hybrid. Any state that cannot be classified —
  corrupt journal (P5-D), unreadable member, marker/pair mismatch —
  fails closed with the journal retained as evidence (CB-P5D
  shape), never silently discarded or silently blessed.
- **Marker durability.** The completion marker is written BEFORE
  journal disposal and is NOT erased by recovery (repairs CB-W1):
  recovery may consume the journal; the marker is the audit
  witness and survives until the pair itself is superseded.
- **No false success.** `import_packet` returns `ok=True` only
  when the landed pair verifies coherent against the journal's
  declared final state (repairs CB-W3); recovery over a clean
  complete pair is a no-op success, not an error (repairs CB-W2).

## 3. Lock-order table (owner lock discipline)

All C-B operations serialize on the per-owner state lock
(`form/owner_state_lock.py`). Acquisition order is total and
acyclic; inner helpers assume the lock is held and never
re-acquire (the lock is not re-entrant by design; the outermost
operation owns it).

| Step | Holder | Acquires / does | Releases |
|---|---|---|---|
| 1 | `import_packet` | owner lock → write journal (import id, pair members, declared final state) + fsync → write pair members → write completion marker + fsync → dispose journal (idempotent) | owner lock |
| 2 | `recover_exchange_import` | owner lock → read journal → classify pair (§4) → converge (complete / roll back / fail closed) → dispose journal only if marker durable | owner lock |
| 3 | load path (fresh process) | owner lock → if journal present, run step 2 classification BEFORE exposing any pair member | owner lock |
| 4 | `_dispose_import_journal` | (assumes lock held) delete journal iff marker present and durable; else retain + report | — |
| 5 | `_clear_import_journal` | (assumes lock held) legacy clear path — must route through step 4's condition, never unconditional `os.remove` | — |

Deadlock argument: one lock, one holder class, no nested
acquisition, no second lock introduced by C-B. Reentrancy rule:
public entry points acquire; private helpers (`_`-prefixed) never
do. This is the same discipline the R5-D prep revision adopted
for `Program.note` (full-method lock scope) — one pattern, two
surfaces, no new lock authority.

## 4. P5 consistency boundary — classification table

Recovery/load classifies the on-disk pair into exactly one row;
only the first two rows expose state:

| Journal | Marker | Pair members | Class | Action |
|---|---|---|---|---|
| absent | any | any | NO_IMPORT | expose pair as-is (CB-P5: zero writes) |
| present | present, matches journal | both verify vs declared final state | NEW_PAIR | dispose journal, expose new pair (CB-P3 first call) |
| present | absent | both still at pre-import state | OLD_ONLY | dispose journal, expose old pair |
| present | absent | torn / partial | TORN | converge to OLD_ONLY by restoring pre-import members from journal payload; if restore impossible → FAIL_CLOSED |
| present | present | any member mismatches marker/journal | INCOHERENT | FAIL_CLOSED: raise `ExchangeError`, retain journal (CB-P5D shape) |
| corrupt/unreadable | — | — | UNREADABLE | FAIL_CLOSED: raise, retain bytes as evidence |
| absent | present | pair mismatches marker | INCOHERENT | FAIL_CLOSED (marker without journal is evidence of external interference) |

**P5-R (fail-closed validation, per repair-plan Amendment A5/B1):**
classification reads BOTH members and the marker before deciding;
a read error on any input is UNREADABLE, never a guess. **P5-D**
(corrupt journal) and the marker-without-journal row are the
adverse cases the validation exists for; both retain evidence.

## 5. C-A separation + the Q-E2 minimum

Director ruling 7040542941 splits the Q1 family:

- **C-B (this design):** the Exchange import/recovery transaction
  only. Bounded, one owner, one pair, one journal.
- **C-A (separately scoped, NOT authorized, NOT designed here):**
  the ordinary `Program.save` pair (program + nursery files) has
  the same missing commit boundary — measured by
  `form/sm35_ca_qe2_test_spec.py`: after an interrupted ordinary
  save, a fresh load exposes **HYBRID** in both crash windows
  (0/2, verdict=HYBRID ×2, 2026-11-20). C-A needs its own scoping
  and authorization; nothing in C-B's landing may be read as
  covering it, and MWL #46 stays **GATED**.

The **Q-E2 minimum** both must meet: *a fresh load exposes
OLD_ONLY or NEW_PAIR, never HYBRID.* A transient on-disk hybrid
during the write window is acceptable; what is forbidden is a
reader exposing it. Readers that bypass the recovery boundary
(direct file reads outside the load path) are explicitly NOT
covered by the guarantee — the guarantee binds at the load
authority, the same boundary discipline as the checkpoint path
(SM-35 A/B cases, GREEN today).

## 6. Mutant set (the design must kill all three)

From `DIRECTOR_Q1_REPAIR_PLAN.md`; the code-stage suite must fail
under each mutant and pass without it:

- **M1 — lock narrowed:** owner lock released before journal
  disposal → interleaved import/recovery tears the pair.
  Killed by: a concurrency case racing import vs recovery.
- **M2 — P3 removed:** disposal without the marker-durability
  condition → CB-W1 evidence loss returns. Killed by CB-W1.
- **M3 — P4 skipped:** classification skips one pair member →
  torn pair classified as NEW_PAIR. Killed by a torn-pair case
  (CB-W3 shape with the tear in the un-read member).

## 7. Prep artifact + naming

The failing-first suite was authored as
`q1_cb_exchange_recovery_prep_test.py` per the Part I package and
is shipped in this PR as
**`form/q1_cb_exchange_recovery_prep_test_spec.py`** — identical
content. Reason: `form/regress.py`'s `intended_entries()` = LIST
+ every discovered `form/**/*_test.py`; an unregistered failing
suite turns CI smoke RED as an omitted/red entry (failure class
proven on PR #503, smoke run 44758805458). **Code-stage step
zero** for C-B: rename back to `*_test.py` and register in
`form/regress.py` LIST in the same commit that lands the repair.

Per-case expected outcomes after the C-B repair: W1 PASS (marker
survives recovery), W2 PASS (clean pair = no-op success), W3 PASS
(importer refuses or converges — never `ok=True` over an
incoherent pair), W2F/P3/P5/P5D unchanged PASS — **7/7**, plus the
M1 concurrency case and the M3 torn-pair case added at code stage
(9 cases total).

## 8. Exact ask

Director **C-B code authorization** (bounded to
`form/dell_matrix/exchange.py` + `form/owner_state_lock.py`
discipline above), requested only when the Director rules on this
design; the prep and design are complete without it. MWL #118
stays **GATED** until that authorization fires; #294 never merges.
