# SYSTEM-002 / Q-S2.1 — Nursery LABEL silent-truncation repair (build packet)

- **Circuit:** Q-S2.1 (sibling of SYS-C29 / PR #429), authorized by Director mail **1a1df5bdadd2125e** (2026-11-15): *"AUTHORIZE NEXT BOUNDED REPAIR for Nursery label silent truncation (dock admits 200, store cuts 80), subject to first proving the precise public-path mismatch and defining the admitted label contract. Preserve admitted labels losslessly, refuse invalid inputs before mutation; regression/mutant proof. Do not fold into frozen #429 candidate."*
- **Base:** main `17ae4ce86743d9c5ff848a1b48111119d9bf9a32`
- **Branch:** `uni/sysc29-label` (this packet rides the build commit; mutants + ×3 campaign are main-session steps, per the SYS-C29 division of labor)
- **Scope:** `form/dell_matrix/nursery.py` only (plus the new suite + regress registration). No new persistence authority. Not folded into PR #429.

---

## 1. The admitted label contract (defined before implementation, per the Director's terms)

- **Admitted:** a string label of at most **200 chars** — the bound the inference dock itself enforces by explicit refusal (`form/dell_matrix/inference_dock.py:43` `MAX_LABEL_CHARS = 200`; `validate_proposal_output` and `validate_semantic_output` both require `1 <= len(label) <= 200` after strip and pass the label through whole). Admitted labels are stored **in full, exactly** — in memory and on disk.
- **Beyond the bound:** `Nursery.add()` raises **`NurseryLabelError`** BEFORE any mutation or save — no ID computed, no proposal stored, no bytes written. On the dock's public path this surfaces as the dock's existing explicit refusal (`{"ok": False, "reason": "nursery_failure", "detail": "NurseryLabelError"}` — both dock call sites, inference_dock.py:1272 and :1948, already wrap `add()` that way), never as a crash and never as silent loss.
- **Unchanged:** non-string labels keep their prior behavior (the guard is `isinstance(label, str)`, mirroring SYS-C29's words guard); no lower bound is newly imposed at the Nursery (the dock enforces ≥1 on its path; other callers guard emptiness themselves — see Q-L.1).
- **Identity:** proposal IDs derive from `_slug(label, seed)` over the FULL label (28-char slug prefix + SHA-256 digest of the whole text), so no existing flow's IDs change; the repair restores label fidelity only.

## 2. Failing-first (on unmodified main @ 17ae4ce)

Rerunnable script: `hidden_files/label_repro.py`; receipt: `hidden_files/label_repro_2026-11-15.md`. Method: `validate_proposal_output` admits a label → the admitted label is handed to `Nursery.add()` on an isolated temp nursery file → stored label compared in memory and in the persisted JSON.

| Input label | Dock admits | Stored (memory) | Stored (disk) | Error? |
|---|---|---|---|---|
| 81 chars | whole (81) | **80** | **80** | none — SILENT LOSS |
| 150 chars | whole (150) | **80** | **80** | none — SILENT LOSS |
| 200 chars | whole (200) | **80** | **80** | none — SILENT LOSS |

Defect site: `form/dell_matrix/nursery.py` in `Nursery.add()`: `label=label[:80]`. The cut sits 120 chars BELOW the admitted bound, so content the system explicitly admitted was destroyed with no error — the same defect class as SYS-C29's words cut, one field over.

## 3. Caller check (contract safety — completed before implementation)

Every production caller of `Nursery.add()` in `form/` was traced to the label it actually passes:

| Caller | Label passed | Bound at the caller | Verdict |
|---|---|---|---|
| `inference_dock.py:1272`, `:1948` | provider output after `validate_proposal_output` / `validate_semantic_output` | 1..200 enforced by refusal before `add()` | The admitted contract itself; `add()` exceptions already surface as explicit `nursery_failure` refusals |
| `exchange.py:767` | imported packet `seed["label"]` | `validate_packet` → `_str(seed["label"], 120, …)` **raises** ExchangeError if >120 | ≤120 ✓ |
| `ringed_growth.py:548` | `f"Restore {organ}"` | organ identifiers, short by construction | ✓ |
| `ringed_growth.py:684` | `_combine_label(a, b)` = `a[:22] + " × " + b[:22]` | ≤ ~47 chars | ✓ |
| `ringed_growth.py:715` | `_evolve_label(...)` = `f"{label} → {tip}"[:70]` | ≤70 chars | ✓ |
| `mandell/supersession.py:649` | `(label or f"revision of {old.label}")[:80]` | caller pre-cuts to 80 itself | ✓ |
| `dell_matrix/auto_growth.py:133` (`_nursery_auto`) | pass-through parameter | **no in-module production caller exists**; the only callers found are tests passing short literals (≤25 chars) | ✓ no habitual >200 |
| `mandell/core_i_ops.py:872` (Dell 37 default "add idea") | free user text (`lab = label.strip()` via the executor front door) | unbounded human input — not a machine caller | ✓ a >200 user label becomes an explicit refusal instead of today's silent cut — the mandated behavior change |

**No production caller habitually passes labels over 200 chars.** The stop condition in the build brief was not triggered; the refusal contract is safe to impose.

## 4. Implementation (`form/dell_matrix/nursery.py`, +28/−1)

- New `NurseryLabelError(ValueError)` beside the existing nursery errors, with the defect history in its docstring.
- New module constant `MAX_LABEL_CHARS = 200`, commented as the same bound the dock enforces. (Duplicated by value, not imported: `nursery.py` must not import `inference_dock` — the dock depends on the Nursery, so an import would be circular.)
- `Nursery.add()`: the bound check runs first in the method body — before `_slug`, before the `Proposal` is constructed, before any save. `label=label[:80]` → `label=label`.
- Nothing else changed: the words slice (SYS-C29's field, PR #429), reason, origin, detail, goals handling are byte-identical to base.

**Union-refresh disclosure:** PR #429 (SYS-C29) changes the adjacent `words=` line inside the same `Proposal(...)` constructor call. When #429 lands, this branch will need a union-refresh; the reconciliation is mechanical (two independent one-line field changes: `label=label` here, `words=words` there) and no semantic conflict exists.

## 5. Tests

- **New suite** `form/nursery_label_bound_test.py` — **15/15 PASS**: L0 bound equals the dock bound (200); L1 admitted 200 stored exactly in memory AND on disk; L2 boundary 80 exact / **81 exact** (the first length the old cut destroyed); L4 unicode 120 chars exact (chars, not bytes); L7 the public-path seam — a 150-char label admitted by the dock's own validator lands whole; L3 201 chars refused explicitly with in-memory count unchanged, **disk bytes byte-identical (3875 → 3875)**, fresh load unchanged, and the instance still usable afterwards; L5 legacy 80-char record loads intact and round-trips through a later save; L6 fresh-process reload exact-compares every stored label. Registered in `form/regress.py` LIST (286 → 287 entries, exactly once, no duplicates; LIST import-verified).
- **Neighbor suites** — every regress LIST entry whose module imports the Nursery class directly, each in its own process via `smoke()`, sequential: **54/54 PASS** (including `nursery_confirm_race`, `persist_full_roundtrip`, `manifestset_isolation`, `lineage_authority`, `owner_namespace_collision`, the DCC-XV–XIX family). Zero failures — nothing to diagnose.
- **Mutants:** main-session step (per the circuit division of labor), not run by this lane.

## 6. Anticipated probes

- *"Add a 500-char label directly"* → `NurseryLabelError` before mutation; the nursery file is byte-identical afterwards (L3 pins the 201 case; the mechanism is length-only).
- *"Dock a 200-char label end to end"* → admitted by the validators, stored whole (L1 + L7 pin the two halves of that path).
- *"What happens to labels already stored at 80 in existing owner files?"* → they load unchanged (L5); the repair is prospective — it cannot restore characters the old cut already destroyed, and it fabricates none.
- *"Does a refused label poison the Nursery instance?"* → no: L3 adds successfully after the refusal on the same instance.
- *"Non-string label?"* → prior behavior preserved by the `isinstance` guard; disclosed here rather than silently redefined.

## 7. Questions for the Director

- **Q-L.1:** Should the Nursery also refuse EMPTY labels (a lower bound), or is the dock's 1-char floor plus each caller's own guard sufficient? This circuit imposed no lower bound — adding one is a separate contract decision because `core_i_ops` already refuses empty labels with its own message.
- **Q-L.2:** Confirm the bound-by-value duplication (`nursery.MAX_LABEL_CHARS = 200` mirroring `inference_dock.MAX_LABEL_CHARS = 200`, each commented to the other) as the standing pattern — it is the same shape SYS-C29 used for words, and importing the dock constant from `nursery.py` would be circular.

*No MWL credit is claimed by this packet. Lifecycle: BUILT (this branch). Certification / final-check / merge: the authorities' and the main session's steps, in that order.*
