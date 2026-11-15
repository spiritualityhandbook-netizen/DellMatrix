# SYSTEM-002 / Q-S2.2 — Nursery reason silent-truncation repair

*Bounded circuit under SYSTEM-002, executed 2026-11-15 by Uni (build lane). Base: main `17ae4ce86743d9c5ff848a1b48111119d9bf9a32`, branch `uni/sysc29-reason`. Sibling circuits: SYS-C29 words repair (PR #429, in flight) and the Q-S2.1 label repair (separate branch) — this diff is based on MAIN's nursery.py and keeps its hunks minimal; a later union-refresh reconciles the three.*

## 1. Contract

The admitted reason bound is **1,000 chars** — the bound the inference dock enforces by explicit refusal at all three admission points (host reason in `propose()`, inference_dock.py:1120-1122; host reason at the semantic-verb entry, :1637-1642; model reason in `validate_semantic_output`, :605-608) and the codebase's only named reason constant, `director_session.py:43 MAX_REASON_CHARS = 1000`.

1. `Nursery.add()` stores admitted reasons **losslessly to 1,000**; a reason beyond 1,000 raises `NurseryReasonError` (a `ValueError` subclass, nursery.py) **before any mutation or save** — no proposal is created, no bytes change. This mirrors the SYS-C29 words pattern (module constant `MAX_REASON_CHARS = 1000` + dedicated error).
2. The dock-session evidence validator is reconciled to the same bound in this circuit (section 3 — it guards the *same* proposal reason).
3. Producer pre-cuts are removed where the producer's reason is not bounded by construction (section 4); the store, not the call site, enforces the bound. **No silent truncation remains anywhere on the reason path.**

## 2. Failing-first (on unmodified main @ 17ae4ce)

Rerunnable reproduction (Nursery loaded on an isolated temp path; a dock-admitted 1,000-char reason passed to `Nursery.add()` exactly as the dock paths pass `chosen_reason`):

```
admitted reason length: 1000
stored reason length:   160
stored == admitted:     False
fresh-load length:      160
DEFECT REPRODUCED: reason silently cut (1000 -> 160), no error raised
```

After the repair, the same script reports `stored == admitted: True`, stored and fresh-load lengths 1,000.

## 3. The dock_session mechanism + reconciliation decision

**What the ≤160 validator guards — the same proposal reason.** Evidence:

- `dock_session.py`'s own module docstring (lines 21-23): the record holds, per proposal, *"the reason exactly as stored"*.
- The entry is written by `inference_dock._record_evidence` (inference_dock.py:1332-1356), which copies `"reason": prop.reason` — the stored Nursery proposal's reason, verbatim, no transformation.
- `_is_valid_entry` (dock_session.py:143) then required `_bounded_str(e.get("reason"), 160)` for a persisted evidence entry to be valid.

So the validator's 160 was the store's silent cut wearing a uniform: had the store alone been repaired, every docked proposal with an admitted 161-1,000-char reason would have produced a session-evidence entry its own validator declared invalid — the defect would have moved, not closed.

**Decision: reconciled.** `_is_valid_entry` now bounds the entry reason by the shared admitted bound, imported from the store authority: `from form.dell_matrix.nursery import MAX_REASON_CHARS` (dock_session.py). No truncation was introduced anywhere as a "reconciliation": entries carry the full stored reason, and an entry whose reason exceeds 1,000 is invalid — a state the repaired store can no longer produce. History-tier compaction is unaffected (digest entries drop `reason` entirely, dock_session.py `_DIGEST_FIELDS`). Import check: dock_session is imported lazily by its consumers and nursery.py imports nothing from dock_session; `form.dell_matrix.dock_session`, `form.persist`, `form.persist_rest`, and `form.dell_matrix.inference_dock` all import cleanly after the change (verified first-hand).

## 4. Producer dispositions

| Producer | Site | Disposition |
|---|---|---|
| Inference dock, propose path | inference_dock.py:1272 | Passes host/derived reason admitted at ≤1,000 — no pre-cut existed; now stored whole. |
| Inference dock, semantic-verb path | inference_dock.py:1948 | Passes host/model reason admitted at ≤1,000 — no pre-cut; now stored whole. |
| AutoGrowth | auto_growth.py:138 | **Pre-cut removed.** `f"auto:{source}:{judge.get('reason','')}"[:160]` — the embedded judge reason is LLM free text, *not* bounded by construction. The full reason now passes to the store; a judge reason pushing the total past 1,000 surfaces as AutoGrowth's existing explicit `auto_error` status (its add is wrapped in a catch-all), never a silent cut. |
| Exchange import | exchange.py:712-716 | **Pre-cut removed.** The composed reason (author origin + replication counts + lint labels) is fixed-*format* but *not* bounded by construction: `author_origin` alone is admitted to 200 (validate_packet), and lint labels run to 5 per receipt over up to `MAX_RECEIPTS = 50` receipts — a degenerate packet's reason can exceed 1,000. It now passes whole; such a packet is refused explicitly at the store (surfacing through exchange's existing landing-failure path) instead of being silently cut to 160. |
| Supersession | supersession.py:654 | **Left, with evidence.** `reason=f"supersedes {old_id}"[:160]` — `old_id` is a Nursery proposal ID produced by `_slug` (nursery.py): slugified prefix ≤28 chars + `_` + a ≤4-digit digest suffix, plus add()'s `_<count>` collision suffix. The whole composed string is bounded by construction at well under 160 chars, so the slice can never fire; removing it would be a cosmetic hunk in another circuit's file (Q-S2.3 territory), not a repair. |
| RingedGrowth | ringed_growth.py:548/684/715 | No pre-cut exists; fixed-format numeric f-strings, bounded by construction, well under the bound. Untouched. |
| Core I ops | core_i_ops.py:872 | Passes no reason (default `""`). Untouched. |

**Caller audit for the refusal:** no production caller habitually passes reasons over 1,000 chars. The dock paths and `DirectorSession.directive()` (director_session.py:187-221, itself bounded by `MAX_REASON_CHARS`) enforce 1,000 before the store; every other producer is short by construction or named above. The refusal therefore fires only on genuinely out-of-contract input.

## 5. Implementation (4 product files)

- `form/dell_matrix/nursery.py`: `MAX_REASON_CHARS = 1000` + `NurseryReasonError(ValueError)`; `add()` refuses an oversize string reason before ID computation, mutation, or save; `reason=reason[:160]` → `reason=reason`. No other behavior changes.
- `form/dell_matrix/dock_session.py`: entry-reason bound 160 → shared `MAX_REASON_CHARS` (imported from nursery), with the mechanism recorded in a comment.
- `form/dell_matrix/auto_growth.py`: `[:160]` pre-cut removed (comment records why).
- `form/dell_matrix/exchange.py`: `[:160]` pre-cut removed (comment records why, incl. the degenerate-packet refusal consequence).
- `form/nursery_reason_bound_test.py` (new suite) + one registration line in `form/regress.py` (LIST 286 → 287, entry exactly once, no duplicates; on-disk coverage check passes).

Out of scope and untouched: `words[:240]` and `label[:80]` in the same `add()` (SYS-C29 / Q-S2.1 own them), `origin[:120]`, `detail[:2000]`, `goals` bounds (bound-consistent guards per the SYS-C29 classification), supersession's `[:160]` (section 4), and the Q-S2.3 caller words pre-cuts.

## 6. Tests

- **New suite** `form/nursery_reason_bound_test.py` — **12/12 PASS**: R1 admitted-1,000 exact (memory + disk); R2 boundaries 160/161 exact (161 was cut before); R3 1,001 refused with `NurseryReasonError`, in-memory count unchanged, disk bytes byte-identical (1354 → 1354), fresh load unchanged; R4 unicode 600-char reason exact; R5 legacy 160-char record loads intact and round-trips through a later save; R6 dock_session validator accepts a 500-char reason end-to-end (record built via `new_record` + `append_proposal`, the shapes `_record_evidence` writes) and still refuses a 1,001-char entry; R7 fresh-process reload exact-compares every stored reason.
- **Neighbor suites** (85 suites: every regress suite importing the Nursery class directly, every dock_session suite, and every suite importing the changed producers — each in its own process via `smoke()`, sequential): **84/85 PASS** in the concurrent run. The single failure, `form.dell_matrix.pp4_bimo_dock_test` (RESULT False at 164s), **passes on isolated rerun at the same head** (RESULT True, 89s): pp4 spawns subprocess suites and the first run executed while several sibling lanes/campaigns were running suites concurrently on the shared VM — classified as concurrency interference in the measurement, not a product failure, and recorded here rather than silently re-run into a green.

## 7. Anticipated probes

- *"File a docked proposal with a 900-char reason; show the reviewer the full text."* — stored whole by `add()` (R1/R2 pattern); the session-evidence entry validates (R6 pattern at 500; the bound is the shared constant, so 900 behaves identically).
- *"What happens at exactly 1,000 / 1,001 through the dock?"* — the dock refuses 1,001 itself (`bad_reason`) before the store is reached; the store's refusal is the second, independent gate for non-dock callers (R3).
- *"Does an old session record with a ≤160 reason still validate?"* — yes: 160 ≤ 1,000; R5 covers the Nursery-side legacy shape, and the validator change only widens acceptance for full entries (digests never carried reason).
- *"Did you just move the cut into the producers?"* — no producer slices reason anymore except supersession's provably-dead slice (section 4); grep `[:160]` over the reason path returns only that one site plus unrelated display previews in other modules.

## 8. Questions for the Director

- Q-S2.2-R.1: the exchange consequence in section 4 — a degenerate packet (50 receipts, all fields absent) whose composed reason exceeds 1,000 now fails the landing explicitly instead of landing with a cut reason. Uni reads this as the contract working (refusal over silent loss). Confirm or direct a different disposition for that corner.
- Q-S2.2-R.2: supersession's dead `[:160]` was left as another circuit's cosmetic hunk. Confirm it should ride the Q-S2.3 supersession circuit rather than this one.

*No MWL credit is claimed by this circuit. Merge follows the standing gates (main-session diff review, mutants, ×3 campaign, exact-head CI, authority stamps, §32) — none executed by this build lane.*
