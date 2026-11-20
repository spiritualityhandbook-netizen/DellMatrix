# R5-D IMPLEMENTATION PREPARATION — serializer parity, preflight placement, concurrency model

Evidence for PR #498, answering Director 7038363820 (2026-11-20 05:30 CST),
bounded preparation items (1)–(3). Item (4) — applicable refusal assertions
green on a separately authorized implementation head — is NOT discharged
here; it awaits the Director's bounded implementation authorization
(at most S7). ZERO product code changed. All line numbers verified against
`form/` sources at evidence head 75661b6 / main 1f58c7d on 2026-11-20.

## 1. Save-serializer parity vs the logical full-history cap (item 1)

Actual save path (source-verified):

- `Program.save` — `form/open.py:2164`
- `persist_rest.save` — `form/persist_rest.py:120`, canonical write under
  `owner_state_lock` at `persist_rest.py:155-156`
  (`form/owner_state_lock.py:135`)
- serializer: `persist.serialize(program)` — `form/persist.py:190`;
  the persisted payload carries `"history": list(...) [-24:]` at
  `form/persist.py:378`
- writer: `atomic_write_json` (`form/persist_rest.py:103-105`), i.e.
  `json.dumps(payload, indent=2)`; `ensure_ascii` omitted → Python
  default `True`

Established by the refusal-depth suite (R5RD §3, evidence 75661b6):

- A real save file equals `json.dumps(serialize(p), indent=2)` encoded
  UTF-8 byte-for-byte (17,282B = 17,282B, insertion order, no sort_keys).
- Segment parity FAILS by construction: the history segment inside the
  file is nested, adding exactly 2 bytes per interior line (measured
  delta 12B at n=5 = predicted 2·(n+1)). Byte-equivalence between the
  admission formula and file bytes is therefore NOT a valid
  certification target.
- Truncation divergence is decisive: a logical history of 2,400,152
  canonical bytes (over the 2,097,152 cap → formula REFUSE) persists as
  a 1,920,122-byte slice (under cap), because `serialize()` keeps only
  `history[-24:]`.

**Contract for the implementation head:** the R5-C cap binds the LOGICAL
in-memory history at admission time — canonical
`json.dumps(full_history, indent=2, ensure_ascii=True)` UTF-8 bytes over
the complete history list — never the bytes the save format writes.
Two eviction points must be addressed by the R5 build (per the retention
design on PR #498), and neither is touched by this preparation:
`Program.note` truncates to `history_max` (`form/open.py:130`
`history_max: int = 24`; `form/open.py:345-349`), and `serialize()`
slices `[-24:]` (`form/persist.py:378`); load also slices
(`form/persist_rest.py:643`).

## 2. Preflight placement contract — per S7 method (item 2)

Admission point for every S7 method is its single `note_seed` call.
The preflight (entry-count + logical-byte check over the history as it
would stand after the note) must run BEFORE the method's first effect —
which differs per method (source-verified in `form/open.py`):

| method | def line | first effect | preflight insertion point |
|---|---|---|---|
| radial_drift | 1113 | `apply_radial_soft_forget(lattice, keys)` at 1115, BEFORE `note_seed` at 1116 | first statement of the method body |
| internet_on | 1216 | gate creation (1218-1220) + `turn_on()`, BEFORE `note_seed` | first statement of the method body |
| internet_off | 1224 | no-gate early return at 1225-1226; else `turn_off()` BEFORE `note_seed` | AFTER the no-gate early return, BEFORE `turn_off()` |
| sandbox_on | 2055 | `note_seed` FIRST (2056), then `sandbox.apply_on(plane)` | first statement, before `note_seed` |
| sandbox_off | 2062 | `note_seed` FIRST (2063), then `sandbox.apply_off(plane)` | first statement, before `note_seed` |
| enhance_on | 2066 | `enhance.turn_on()` at 2067, BEFORE `note_seed` at 2068 | first statement of the method body |
| enhance_off | 2070 | `enhance.turn_off()` at 2071, BEFORE `note_seed` at 2072 | first statement of the method body |

Preserved early return: `internet_off` with no gate returns
`{"ok": True, "on": False}` with no note, no gate creation, no error —
even at cap (R5RD check `early_return_internet_off_no_gate_preserved`
PASSES today). It is the only legitimate no-note early return among S7;
the build must NOT convert it into a refusal, which is why its preflight
sits after that return.

Executable assertion form: the R5RD battery
(`form/r5d_refusal_depth_test.py`, 84 checks = 7 methods × 2 cap
scenarios × 6 assertions: typed refusal, history digest, serialized
state, per-method subsystem digest, state-dir files, thread count) is
the executable specification of "preflight-before-first-mutation +
no-mutation/filesystem change on refusal". Today 28/84 PASS (files +
threads only); on an authorized implementation head the applicable
checks are the item-(4) gate and must go green there — they are not
claimed green here.

## 3. Thread/process concurrency model + demonstrated guarantees (item 3)

**Threads (INTEGRATION, in-process).** One `Program` instance = one
in-memory history list shared by all caller threads. No lock exists in
`form/open.py` / `form/persist.py` today. Demonstrated (R5RD §4):
4 threads × S7 at entry cap → 0/28 refused, state unstable.
Guarantee the build must provide and demonstrate: preflight + note form
ONE critical section under a per-Program lock, so the check-and-append
is atomic against concurrent S7 calls on the same instance; the R5RD
thread leg is the demonstration harness (target: all applicable
refusals fire, serialized state stable). No guarantee is claimed today.

**Processes (CROSS_PROCESS, separate OS processes).** Each process
holds independent in-memory state; there is NO shared admission state.
Demonstrated (R5RD §4): 3 subprocesses, same owner, history at cap,
concurrent saves to a shared path — all executed, 0 refused, and the
shared file remained a valid whole generation
(`mp_shared_file_valid_after_concurrent_saves` PASS): the
`atomic_write` guarantee holds under concurrent writers, and canonical
saves serialize through `owner_state_lock`
(`form/persist_rest.py:155-156`), which does NOT re-check admission.

**Scoped guarantee statement for the S7 build:** admission guarantees
are PER-PROCESS (and, with the lock above, per-instance thread-safe).
Cross-process admission coordination is ABSENT and is NOT promised by
the S7 scope; atomic file replacement is not atomic admission
(Director 7033305002). Any wider guarantee requires a separate design
and authorization.

## 4. What remains (item 4 — not discharged)

- Director bounded R5-D implementation authorization (at most S7) on a
  separate implementation head.
- On that head: R5RD applicable refusal assertions green, exact-head CI
  terminal, refreshed Keeper review.
- Power-loss behavior remains UNKNOWN (not tested in any R5-D suite).

---

# REVISION 2026-11-20 — answering Director 7038920405 requirements (2)–(4)

Zero product code. All line numbers re-verified against `form/` sources
at evidence head 7aea4c2 / main 1f58c7d on 2026-11-20. Requirement (1) —
Keeper independent challenge of 7aea4c2 — remains a Keeper act; this
revision extends the challenge surface to include §§5–7 below.

## 5. Enforceable lock scope (requirement 2)

Director's correction stands: locking only preflight+note is
INSUFFICIENT, because on radial_drift, internet_on, internet_off and
enhance_on/off the method's effects precede its note. The specified
scope is therefore the WHOLE method body:

**Chosen mechanism — per-Program reentrant admission lock.**
- Each `Program` instance owns one `threading.RLock` (admission lock),
  created with the instance.
- Every S7 method acquires the admission lock as its FIRST act (for
  `internet_off`: before the no-gate early-return check, so the gate
  test itself is inside the section) and holds it continuously through,
  in order: (a) preflight (entry-count + logical-byte check over the
  history as it would stand after this method's note), (b) ALL of the
  method's effects, (c) the history append via `note`/`note_seed`.
  Refusal raises/returns BEFORE any effect executes, while holding the
  lock, so a refused call is atomic: no effect, no append.
- Reservation/rollback was considered and REJECTED as the primary
  mechanism: S7 effects include non-transactional subsystem mutations
  (lattice soft-forget, gate creation + turn_on, enhance toggles) with
  no existing undo path; a lock that prevents interleaving is the
  enforceable primitive the codebase already patterns elsewhere
  (`owner_state_lock`, form/owner_state_lock.py:135).

**Other history writers — census (source-verified).** In
`form/open.py` the ONLY mutator of `Program.history` is
`Program.note` (open.py:345–349: append, then truncate to
`history_max`), and `note_seed` (open.py:351) funnels into it
(open.py:365 `self.note(body)`). Every other writer — all ~35
`note_seed` call sites in open.py — reaches history exclusively
through that funnel. The only other assignment is load-time restore
(`persist_rest.py:643`), which runs before the instance serves calls.
Therefore:
- `note()` itself acquires the same admission lock (reentrant, so an
  S7 method already holding it does not self-deadlock). Consequence:
  no non-S7 writer can append between an S7 preflight and its append,
  and the check-and-append pair is atomic against EVERY history writer
  on the instance, not only against other S7 calls.
- `Program.save`'s serializer reads history (`persist.py:378`); the
  build must snapshot the history list under the admission lock so a
  save cannot observe a half-appended state. The canonical-save
  `owner_state_lock` (persist_rest.py:155–156) continues to govern the
  file transaction; it is a different lock for a different boundary
  and neither substitutes for the other.

**Demonstration harness (for the authorized head):** the R5RD thread
leg (4 threads × S7 at cap) must show all applicable refusals firing
with serialized state stable, PLUS a mixed-writer leg (S7 calls racing
non-S7 `note_seed` calls) showing no append interleaves a refused S7
call. Neither is claimed green today.

## 6. Per-process-only admission — user/API boundary statement (requirement 3)

The user/API boundary for this design is the `Program` method surface
itself: the REPL and every public entry path invoke these methods
directly on one in-process instance. The admission guarantee is
therefore stated AT that boundary, verbatim for the build's user-facing
contract:

> History admission (entry cap + logical byte cap) is enforced
> PER PROCESS, on the single `Program` instance serving your calls in
> that process. It is NOT a global limit for an owner. A second
> process opened on the same owner holds an independent history,
> admits independently up to the same caps, and saves whole
> generations to the same canonical file; the last save wins the
> whole generation (atomic replacement, persist_rest.save /
> atomic_write_json). Cross-process outcomes — lost updates between
> processes and combined admissions exceeding what one process would
> allow — are a KNOWN HAZARD of multi-process use, explicitly outside
> the S7 guarantee. No shared-owner global safety is claimed.

`owner_state_lock` serializes canonical saves between processes; it
does not re-check admission and does not convert per-process admission
into cross-process admission (Director 7033305002: atomic file
replacement is not atomic admission).

## 7. Failing-first receipts, power-loss UNKNOWN, truncation accounting (requirement 4)

**Failing-first receipts — preserved, not superseded.** R5RD at
75661b6: 36/94 PASS, exit 1 (per-method battery 28/84; files+threads
legs only). R5SS at 04fced4: 15/40 PASS / 25 FAIL, including the
save/load truncation checks failing. This revision changes no receipt
and claims no new pass; the receipts are the baseline the authorized
implementation head must turn green.

**Truncation accounting — every silent truncation on the history path
(source-verified):**

| # | point | effect today |
|---|---|---|
| T1 | `Program.note`, open.py:346 | each entry text cut to 120 chars (`[:120]`) |
| T2 | `Program.note`, open.py:348–349 | list cut to last `history_max` = 24 entries (open.py:130) |
| T3 | `persist.serialize`, persist.py:378 | persisted payload keeps only `history[-24:]` |
| T4 | load restore, persist_rest.py:643 | each restored entry re-cut to 120 chars AND list cut to last 24 |

Consequence stated plainly: until the R5 build removes/replaces
T2–T4 per the retention design on PR #498, ANY admission-side
retention above 24 entries is destroyed at note time (T2), never
reaches disk beyond 24 (T3), and cannot be restored beyond 24 (T4) —
admission correctness and save/load correctness are separate gates,
and the item-(4) green run must cover both. T1 (120-char entry cut)
is an entry-shape rule, retained or changed only as the retention
design specifies; it is named here so it is never silent again.

**Power loss — UNKNOWN, bounded by what the write path proves.**
`atomic_write_json` (form/dell_matrix/atomic_write.py:123) serializes
fully BEFORE touching the target, writes a sibling temp, fsyncs, and
`os.replace`s; directory fsync is best-effort and its outcome is
exposed (`_last_dir_fsynced`). From that mechanism alone:
- Power loss BEFORE the replace boundary: the previous complete
  generation remains the canonical file. No partial generation is
  exposed through the replace boundary.
- Power loss AFTER replace: the new complete generation is the file,
  subject to the platform's fsync durability (directory fsync
  best-effort → durability of the rename itself is platform-dependent).
- What remains UNKNOWN and is NOT claimed: (a) admissions held only in
  memory and never saved are lost on power loss — there is no journal,
  so the count/content of lost admissions is UNKNOWN; an admission
  receipt is NOT a durability receipt; (b) no R5-D suite has cut power
  or killed a process mid-save, so mid-save crash behavior at the
  exact replace boundary is demonstrated only by the atomic_write
  mechanism's existing tests, not by any R5-D evidence. The authorized
  head's evidence must either add a kill-mid-save leg or carry this
  UNKNOWN forward explicitly.

## 8. Revised remaining gate

- (1) Keeper independent challenge — now covering 7aea4c2 AND this
  revision (lock scope §5, boundary statement §6, truncation/power-loss
  accounting §7).
- Director bounded R5-D implementation authorization (at most S7) on a
  separate implementation head, thereafter.
- On that head: R5RD applicable assertions green (incl. the mixed-
  writer thread leg, §5), exact-head CI terminal, refreshed Keeper
  review. Power-loss UNKNOWN carried or closed per §7.
