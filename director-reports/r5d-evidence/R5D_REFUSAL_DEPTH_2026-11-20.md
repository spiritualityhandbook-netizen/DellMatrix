# R5-D REFUSAL DEPTH — per-method assertions, actual-save-format parity, thread/process isolation

Evidence for PR #498, answering Director 7032773180 (2026-11-20 01:00 CST).
Suite: `form/r5d_refusal_depth_test.py` — **R5RD 36/94 PASS, exit 1 (failing-first)**,
two in-clone runs identical modulo uuid; logs `r5d_rd_run1.txt` / `r5d_rd_run2.txt`.
ZERO product code changed.

## 1. Per-method refusal battery (84 checks: 7 methods × 2 scenarios × 6 assertions)

For each S7 method, at entry cap (10,000 entries) AND at byte cap+1, the battery asserts:
typed refusal, full-history digest unchanged, serialized-state bytes unchanged,
**per-method subsystem digest unchanged**, state-dir file set/sha256 unchanged,
thread count unchanged.

Result today: 28/84 PASS — only `files_unchanged` and `threads_unchanged` pass
(no S7 call writes files or spawns threads). Every `typed_refusal`,
`history_unchanged`, `state_unchanged`, and `subsystem_unchanged` check FAILS:
no refusal exists, and each call mutates before/regardless of its note.

Pre-note mutation map (source-verified, `form/open.py`) — the subsystem digest
covers exactly what each method touches first:

| method | first effect | order |
|---|---|---|
| radial_drift | `apply_radial_soft_forget(lattice, keys)` — cells + KeyLedger | mutation BEFORE note |
| internet_on | creates `InternetGate` + `turn_on()` | mutation BEFORE note |
| internet_off | `turn_off()` | mutation BEFORE note |
| sandbox_on | note, then `sandbox.apply_on(plane)` | NOTE FIRST |
| sandbox_off | note, then `sandbox.apply_off(plane)` | NOTE FIRST |
| enhance_on | `enhance.turn_on()` | mutation BEFORE note |
| enhance_off | `enhance.turn_off()` | mutation BEFORE note |

The radial_drift subsystem probe is non-vacuous: the suite seeds a far-shell
cell (`lattice.put(30, 30, 1, label="seedcell", content="seedpayload")`,
shell 30 ≥ outer_shell 6); a running call keys it, soft-forgets its content,
and bumps the ledger — the digest catches all three.

## 2. Legitimate no-note early return — preserved

`internet_off` with **no gate** returns `{"ok": True, "on": False}` with no
note, no gate creation, no error — even at entry cap. Check
`early_return_internet_off_no_gate_preserved` PASSES today. It is the only
legitimate no-note early return among S7 (source-verified); the R5-D build
must NOT convert it into a refusal. The other six have no Program-level
no-note early return.

## 3. Byte-equivalence vs the ACTUAL save format (Director's caveat — answered)

Actual save path: `persist_rest.save → _write_program_file →
atomic_write.atomic_write_json`, serializer `json.dumps(payload, indent=2)`
over `persist.serialize(program)`.

- **ensure_ascii axis: PARITY HOLDS.** `atomic_write_json` omits the argument;
  the Python default is `True`, byte-identical to the canonical
  parameterization (proven empirically on a non-ASCII payload).
- **File formula: PROVEN.** A real save file equals
  `json.dumps(serialize(p), indent=2).encode("utf-8")` byte-for-byte
  (17,282B = 17,282B). No `sort_keys` — insertion order.
- **Segment parity: FAILS by construction.** The history segment inside the
  file is NOT the canonical top-level dumps of the history list: nesting
  adds exactly 2 bytes per interior line — measured delta 12B at n=5,
  predicted 2·(n+1) = 12B. Exact byte-equivalence between the admission
  formula and file bytes is therefore not a valid certification target.
- **Truncation divergence: the decisive fact.** `serialize()` persists only
  `history[-24:]` (persist.py:378). Demonstrated both directions: a logical
  history of 2,400,152 canonical bytes (formula: REFUSE, over the
  2,097,152 cap) persists as a 1,920,122-byte slice (under cap). **The
  R5-C cap binds the logical in-memory history at admission time; it never
  measures bytes the save format writes.** The build contract must state
  this explicitly; certifying "byte parity with the save format" would
  certify a quantity the system never produces.

## 4. Concurrency guarantees — isolated by thread vs process

- **Threads (INTEGRATION, in-process):** 4 threads × S7 at entry cap —
  0/28 refused, state unstable. FAIL, as designed. Even once refusals
  exist, thread safety holds only if preflight+note form one critical
  section; no lock exists in `open.py`/`persist.py` today.
- **Processes (CROSS_PROCESS, separate OS processes):** 3 subprocesses,
  same owner, history at cap, concurrent saves to a shared path.
  All 3 executed (rc 0, parseable reports); 0 refused in any process;
  each child independently evicted its in-memory history to 24 on note.
  The shared file remained a valid whole generation
  (`mp_shared_file_valid_after_concurrent_saves` PASS — the
  atomic_write guarantee holds under concurrent writers).
  **Cross-process admission coordination is ABSENT**: each process holds
  independent in-memory state; the only cross-process fence is
  `owner_state_lock` around canonical save, which does not re-check
  admission. Any R5-D guarantee statement must be scoped: admission is
  per-process unless a future build adds coordination.

## 5. Honest limits

Subsystem digests cover the named pre-note subsystems above; unrelated
program state is covered by the full serialized-state comparison.
Power-loss behavior: NOT tested here (UNKNOWN, per P6). The thread leg
is a test design, not a thread-safety proof. All FAILs are expected
failing-first observations on current main (7027419), not safety
certifications.
