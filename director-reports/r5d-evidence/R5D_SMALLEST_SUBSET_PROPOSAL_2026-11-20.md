# R5-D SMALLEST GENUINELY SIDE-EFFECT-FREE INITIAL SUBSET — proposal

Prepared 2026-11-20 (susx100000-execution), answering Director
7032352360 (00:30 CST delta on PR #498): "propose the smallest
genuinely side-effect-free initial implementation subset, prove
exact canonical UTF-8 sanitized byte admission and no
state/filesystem changes on refusal, and separate process-thread
TOCTOU from unproven multi-process behavior." Evidence only;
ZERO product code; R5-D IMPLEMENTATION HOLD untouched.

## The proposed initial subset: S7 (7 callers)

From the 10 named at 8170967, exactly 7 survive the
side-effect-free test on BOTH subset runs (r5d_subset_run1/run2)
plus source inspection (form/open.py at main 7027419):

| caller | line | files_same at-cap/over (both runs) | only history entry (fixed literal) |
|---|---|---|---|
| radial_drift | 1113 | True / True | `16[Decay] :: drift_6` |
| internet_on | 1216 | True / True | `25[Pulse] :: internet_on` |
| internet_off | 1224 | True / True | `32[Pause] :: internet_off` |
| sandbox_on | 2055 | True / True | `23[Lock] :: sandbox_on` |
| sandbox_off | 2062 | True / True | `24[Unlock] :: sandbox_off` |
| enhance_on | 2066 | True / True | `25[Pulse] :: enhance_on` |
| enhance_off | 2070 | True / True | `32[Pause] :: enhance_off` |

Each caller's ONLY history write is one note_seed with a FIXED
literal label (no caller-supplied text), so its eventual noted
bytes are deterministic and exactly computable in advance — the
precondition for exact byte admission. None writes files, opens
sockets, or starts threads/servers.

## Excluded from the initial subset (3), with evidence

- save (2164): files_same=False at cap AND over in both runs —
  persist_save writes the canonical program file; a disk write
  is its purpose. Belongs to the save/load contract; promotion
  requires proving preflight precedes the disk write (Director
  7032352360), a separate proof owed with that contract.
- visual (2169): files_same=False at cap in both runs —
  write_visual writes snapshot files. Same save/load-adjacent
  contract as save; not promotable on this subset's evidence.
- live_visual (2188): files_same=True in both runs is a
  SNAPSHOT BLIND SPOT, not proof of no side effects —
  start_live (form/dell_matrix/live_visual.py:1619ff) starts an
  HTTPServer listener on localhost in a daemon thread, an
  external effect the state-dir snapshot cannot see. Excluded
  on source evidence; the new suite's exclusion probe observes
  the listener directly.

Accounting unchanged: S7 ⊂ 10 ⊂ 25 INVENTORY-CLEAN; the other
15 CLEAN (4 arg-required, 11 non-Program callers) remain
unpromoted and unclaimed, and all 10 SKIPs stand as documented.

## Entry-point preflight contract (per caller)

Refusal must be computed at METHOD ENTRY, before the caller's
first mutation — which differs per caller (source order):

- radial_drift: before apply_radial_soft_forget (precedes note)
- internet_on: before InternetGate creation / turn_on
- internet_off: before turn_off (no-note early return preserved)
- sandbox_on / sandbox_off: note is the first mutation, but
  preflight still precedes it (apply_on/apply_off must not run
  on refusal)
- enhance_on / enhance_off: before enhance.turn_on/turn_off

## Exact admission formula (R5-C policy, 7026062701)

Admit iff BOTH: entries_after ≤ 10,000 AND canonical_bytes_after
≤ 2,097,152, where canonical_bytes = len(json.dumps(history,
indent=2, ensure_ascii=True).encode("utf-8")) computed on the
history AFTER sanitize_text is applied to the new entry
(sanitize-before-measure) and including the exact eventual
entry. First-reached cap binds; exact fit admitted; no eviction.
Admission is measured in canonical BYTES, never characters:
under ensure_ascii=True a BMP non-ASCII char costs 6 bytes
(\uXXXX) and an astral char 12 (surrogate pair) — the new suite
proves byte-measurement by straddling the byte cap with
equal-char-length labels of different canonical byte lengths.

## TOCTOU separation (honest labels)

- THREAD (in-process): 4 threads × S7 at cap — every call
  refused, serialized state identical afterwards. This is the
  only concurrency evidence claimed (INTEGRATION label).
- MULTI-PROCESS writers: NOT TESTED by this suite and NOT
  claimed. Recorded UNKNOWN. No S7 verdict depends on it; a
  future cross-process proof is a separate obligation.

## Restart / legacy separation

Restart round-trip and legacy cap+50 findings from 8170967
(at-cap history does not survive save->load whole; legacy
loads truncated) belong to the SAVE/LOAD contract, not to S7:
S7 contains no save/load caller. They remain build-contract
requirements for that later phase and are carried, not
discharged, by this proposal. The new suite includes ONE
clearly-labeled saveload check so the separation is executable,
not just prose.

## Proof suite

form/r5d_smallest_subset_test.py (failing-first on 7027419):
3 exclusion probes (expected PASS today — they prove the
excluded effects exist), 28 S7 checks (entry-cap refusal-clean,
entry-cap−1 admitted, byte-cap exact-fit admitted, byte-cap+1
refusal-clean), 3 byte-exactness checks (bytes-not-chars,
sanitize-before-measure straddle, sanitize canary at cap),
1 thread-TOCTOU check, 1 labeled saveload check, controls +
cleanup. NO product code changed.
