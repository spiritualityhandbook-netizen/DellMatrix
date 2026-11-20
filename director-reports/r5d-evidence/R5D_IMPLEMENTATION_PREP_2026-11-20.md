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
