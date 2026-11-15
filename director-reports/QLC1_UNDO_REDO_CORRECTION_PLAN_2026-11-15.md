# Q-LC.1 — UNDO/REDO CORRECTION: PLAN-COMPLETE PLANNING PACKET

*Produced 2026-11-15 by Uni (main-session planning lane), under the Director's
2026-11-15 FULL EXE ruling: "Authorize bounded 30-and-adjustable correction
planning; no blanket cap implementation" (limits-census question Q-LC.1,
published in PR #427). PLANNING ONLY — no product code was changed for this
packet and nothing here is committed to the repository. Every code claim below
was verified first-hand at main `17ae4ce86743d9c5ff848a1b48111119d9bf9a32`
(clone read at that exact HEAD), not copied from the census.*

*Sources: Limits Census item R4 (hidden_files/limits_census/CENSUS.md:53 and
:399 — the census's only outright ruling-violation); Ace ruling DD-54 (the
project plan, §12.86a); the code at the pin above.*

---

## 0. GROUND TRUTH — VERIFIED FIRST-HAND AT THE PIN

| Claim | Verdict | Evidence at main 17ae4ce |
|---|---|---|
| Undo is hard-coded at 32 | **TRUE** | `form/dell_matrix/needs.py:197-198`, inside `push_action()` (def :194): `while len(st) > 32: st.pop(0)`. The literal `32` is the whole mechanism. |
| No named constant exists | **TRUE** | Whole-word grep for `UNDO` across production `form/**/*.py`: zero hits. |
| No setting adjusts it | **TRUE** | The trim reads no field, setting, or config; the literal is the only input. |
| The drop is silent | **TRUE** | `push_action` counts nothing and receipts nothing. Contrast the snapshot stack, which counts its drops (`snapshots_dropped_total`, core_ii_exec.py:55,79). The action stack's loss is invisible everywhere, including `history_report` (needs.py:311, shows the last 8 entries, never depth-vs-bound). |
| REDO does not exist | **TRUE** | Whole-word grep for `redo` over `form/`, `gui/`, `src/`, `preform/` (`*.py`, `*.js`, `*.html`, `*.ts`): **zero hits**. (Substring hits are only "BikeShare**Doc**k" in one test file.) No redo command in the REPL help or dispatch, no redo door in live_visual, no Redo Dell, nothing in gui/server.py. DD-54 §2 records the same: 'the word "redo" appears NOWHERE in the production code'. |
| Ace ruled 30-and-adjustable (DD-54) | **TRUE** | §12.86a of the plan (quoted in §2 below). The coded 32 is not even the ruled 30. |

One reconciliation the census did not state: **two different stacks exist**,
and DD-54 was written primarily against the other one. This packet maps both
(§1) and scopes the correction precisely (§6): Q-LC.1 corrects the user-facing
session undo — the R4 violation. The snapshot stack's retirement into the
same setting is DD-54's wider C3.Undo scope, named as a non-goal here.

---

## 1. MECHANISM MAP

### 1.1 The session action stack (the R4 site — this circuit's target)

- **Home of the bound:** `form/dell_matrix/needs.py:197-198` in
  `push_action(program, entry)` — append, then pop(0) while len > 32.
- **The stack:** `program.action_stack`, a dataclass field on Program
  (`form/open.py:193`, `List[Dict[str, Any]]`), lazily bound by
  `_stack()` (needs.py:188-191). **Per Program instance = per owner.**
  **Session-only:** `action_stack` is EPHEMERAL_BY_DESIGN
  (form/mandell/runtime_observe.py:548) — never serialized, never saved.
  A restart empties it; nothing about it survives save/load.
- **What it bounds:** the inverses of the session's place/edit actions.
  Entry shapes (all small dicts):
  - `{"kind": "place", "id", "label", "ts"}` — carries NO restorable unit
    record (matters for redo, §3).
  - `{"kind": "edit_detail", "id", "old", "new", "ts"}` and
    `{"kind": "edit_goals", "id", "old", "new", "ts"}` — carry both sides.
- **Producers (every push routes through the one `push_action` choke point):**
  - `parse_and_place()` — needs.py:44 (the strong-create path,
    "create an idea called …").
  - `set_detail()` — needs.py:131; `set_goals()` — needs.py:143.
  - The REPL place path — form/repl.py:3101-3102.
- **The consumer:** `undo_last(program)` (needs.py:241-308) pops ONE entry
  per call (multi-step undo = repeated calls). Place → delegates to the
  canonical removal authority `plane.remove` (form/dell_matrix/plane.py:174)
  plus lattice-ref cleanup; revision-owned units are REFUSED
  (`revision_authority`, via `_revision_owned`, needs.py:201) — undo never
  bypasses supersession. Edits → restore the entry's `old` value. Missing
  units refuse honestly. Evidence of each undo lands in the persisted
  `program.history` via `note_seed` — the stack itself is not the record.
  Governing law on the mechanism's own face (needs.py:242-247, PAC-I):
  undo is "a SESSION/UI reversal convenience… explicitly NONCANONICAL as a
  history authority."
- **Doors (how a real user reaches the bound):**
  - Program API: `Program.undo()` — form/open.py:1169-1171 → `undo_last`.
  - REPL: `python3 -m form.repl --owner <name>`; commands `undo` /
    `undo last` — form/repl.py:2266-2268. Help advertises it
    (repl.py:236: "history [n] · history find <text> · undo · replay [n]").
  - Studio session surface: live_visual's command handler takes
    `undo` / `undo last` / `u` — form/dell_matrix/live_visual.py:741-745,
    same `program.undo()` underneath.
  - Display: `history_report` (needs.py:311) shows the stack's last 8.
  - **The user story of the defect:** in the REPL or Studio, create/edit 33
    times; the 33rd push silently evicts the 1st inverse. From then on the
    first action can never be undone, and nothing — no counter, no receipt,
    no display — ever says it happened.
- **Not this mechanism:** `replay [n]` (repl.py:1312-1318 →
  `p.replay_exec(n)`) re-executes recorded history; it is not a forward
  walk over undone steps and is not redo. `dynamic_view_switch.undo()`
  (form/dell_matrix/dynamic_view_switch.py:129) undoes view-mode switches
  from its own history — a namesake on a separate surface, out of scope.

### 1.2 The Core II snapshot stack (DD-54's named authority — mapped, not touched)

- **Bound:** `SNAPSHOTS_CAP = 64`, a named constant
  (form/mandell/core_ii_exec.py:8), enforced in the ONE append path
  `append_snapshot()` (core_ii_exec.py:74-79; callers: the `shot()` op,
  core_ii_exec.py:137, and the chain_exec DeltaFlow checkpoint,
  chain_exec.py:289). Oldest-first trim; drops are COUNTED
  (`snapshots_dropped_total`).
- **Contents:** `CoreIIState.snap()` dicts (core_ii_exec.py:58-65) — Core II
  state (store/groups/defs/aliases/compositions/…), NOT plane units.
  Session-only: `snapshots` is absent from CORE_II_DURABLE
  (form/persist_core_ii.py:9ff).
- **Consumer:** Revert (Dell 96) — form/mandell/spectrum_ops.py:599:
  `_restore(st, st.snapshots.pop())`. It POPS: the state it came from is
  discarded, exactly the behavior DD-54 §2 describes ("today's Revert pops
  one snapshot and the future it came from is discarded").

---

## 2. THE DD-54 RULING — TERMS, AND WHAT "ADJUSTABLE" MUST MEAN

Ace ruling, 2026-11-09, plan §12.86a ("DD-54 — UNDO AND REDO LIKE A REAL
PROGRAM"; also carried as MWL row 135). Verbatim substance:

> "undo something, then redo it, for as many steps — starting with up to 30
> steps / iterations, and the depth must be modifiable and adjustable, like
> Photoshop or Word." RULED: (1) MULTI-STEP UNDO: the session keeps a real
> undo history. Starting depth: 30 steps. The depth is ADJUSTABLE by Ace (a
> setting, not a constant — today's SNAPSHOTS_CAP=64 hard constant retires
> into it; DD-44's Limit (72) is the natural bounding authority to settle in
> design). (2) REDO EXISTS: after undoing, redo walks forward again through
> the same steps… (3) LINEAR HISTORY, NO BRANCHING… a new edit after an undo
> discards the redo tail. (4) ONE HISTORY AUTHORITY: the existing snapshot
> stack… grows into the undo/redo history — no second undo mechanism…
> (6) UNDO WALKS STATE, NEVER RECORDS… (7) THE SHADOWING DIES…

For the bounded Q-LC.1 correction, "adjustable" is satisfied only if ALL of
the following hold (each is testable, §5):

- **By whom:** Ace — i.e., the owner of the owner-state. The setting is
  **per-owner**: one owner's depth never affects another's.
- **Through what surface:** the same doors undo already has — a command on
  the undo surface in both shells (`undo depth` to read, `undo depth <n>`
  to set, in form/repl.py and form/dell_matrix/live_visual.py), backed by a
  Program attribute (`Program.undo_depth`) so the API and tests reach the
  same value. No new Dell number (DD-54 §4 invents none).
- **Persisted where:** with the owner's persisted program state, so the
  choice survives save/load for that owner. The SETTING persists; the
  stacks themselves stay ephemeral (a restored session starts with empty
  undo/redo stacks at the owner's chosen depth — restoring stale inverses
  across a restart is precisely what must not happen). Any owner that has
  never set it reads the default.
- **Default:** exactly **30** — Ace's ruled starting depth, not 32, not 64.
- **Semantics:** a change takes effect immediately. Shrinking trims the live
  stack oldest-first and the command's reply REPORTS how many inverses were
  dropped (the current defect's essence is the silent drop; the correction
  may not reintroduce it at the settings door). Growing never resurrects
  dropped entries. Out-of-range values REFUSE with the reason named (below
  1; above the §4 safety ceiling) — DellMatrix refuses honestly rather than
  silently clamping an intent it was given (the FlowRefusal precedent).

Scope note on DD-54 §1/§4: the ruling's "SNAPSHOTS_CAP=64 retires into it"
and "one history authority" describe the full DD-54/C3.Undo end-state. This
bounded circuit does not retire SNAPSHOTS_CAP and does not unify the stacks
(§6 non-goals); it corrects the R4 violation on the session undo and gives
that undo the redo DD-54 §2 demands, inside the session convenience's own
PAC-I boundary (noncanonical, ephemeral, records untouched). Whether the
two depths later unify is a named design question for the C3.Undo circuit —
flagged, not silently decided here.

---

## 3. REDO — ABSENCE PROOF AND INTEGRATION SHAPE

**Absence (verified at the pin, §0):** the word `redo` appears nowhere in
production code across `form/`, `gui/`, `src/`, `preform/`; no command,
method, Dell, or UI door answers to it. The only forward-ish surface,
`replay`, re-executes history — it cannot re-apply an undone step, and
after an undo the step it would need is gone from the stack entirely
(`undo_last` pops and discards).

**What a redo must integrate with:** the same history the undo consumes —
the session action stack (§1.1). Concretely, the build must:

1. **Feed a redo tail from undo.** On a SUCCESSFUL `undo_last`, the popped
   entry moves to a per-Program redo stack (ephemeral, beside
   `action_stack`). Refused undos (revision-owned, already-gone, empty)
   feed nothing — nothing was reverted.
2. **Close the place-entry gap.** Edit entries already carry `new`, so redo
   re-applies a known value. Place entries carry only {id, label, ts}, and
   undo DELETES the unit via `plane.remove` — after that, nothing remains
   to re-place. The build must capture the unit's full restorable record
   (label, words, detail, goals, skin, x, y) from `plane.units[uid]`
   BEFORE removal and store it on the redo entry. This is the one real
   data-shape change redo forces; it is named here so the build cannot
   discover it mid-circuit.
3. **Re-apply through canonical doors.** Redo of an edit re-applies `new`
   to the live unit (missing unit → honest refusal). Redo of a place
   re-places the captured record through the canonical place path — never
   a backdoor insert — and refuses visibly, mutating nothing, if the id
   has been re-taken or the unit has since entered revision ownership.
4. **Tail invalidation (DD-54 §3).** ANY new `push_action` — from any of
   the four producers, all of which route through the one choke point —
   clears the redo stack. Step back, make a different move, the forward
   path is gone.
5. **Bound semantics (redo's own):** the redo tail can only ever hold what
   undo popped since the last new action, so its natural maximum is the
   effective depth itself; the build applies the same depth trim to the
   redo stack (dropping from the far, oldest-redoable end) so
   undo + redo together never hold more than the depth the owner set.
   Redo is session-only and walks state, never records (DD-54 §6 applies
   symmetrically); its evidence note mirrors undo's `note_seed` pattern.
6. **Door:** `redo` beside `undo` in repl.py and live_visual.py, backed by
   `Program.redo()` → a `redo_last()` beside `undo_last()` in needs.py.
   Empty redo tail answers "nothing to redo" in the same shape undo
   answers "nothing to undo".

---

## 4. SAFETY ANALYSIS — WHAT THE CAP PROTECTS, AND THE CAP THAT MUST SURVIVE

**What the 32 actually protects today (honestly, very little):**
- *Memory:* almost nothing. Entries are small dicts; edit entries carry
  detail/goals strings, so a pathological entry is a few KB. 32 vs 30 vs
  200 entries is not a memory story at any plausible scale.
- *Staleness — the real function:* the stack is a set of inverses recorded
  at action time. Edit inverses restore `old` BLINDLY over whatever the
  unit holds now, and most writers never push actions (only
  parse_and_place / set_detail / set_goals / the REPL place path do —
  DD-54 §5 records the coverage gap). A deep stack therefore widens the
  window in which a confident, wrong restoration can overwrite intervening
  work done through untracked paths. The existing refusals bound this
  only partly (revision-owned and missing units refuse; a merely-changed
  unit does not). **The cap is a staleness bound first, a memory bound
  second.**
- *Correctness of replay:* none — undo does not replay; it applies
  per-entry inverses. Nothing in the mechanism depends on the number 32.

**30 vs 32 vs unbounded:**
- 30 vs 32: no material safety difference in either direction. The move is
  ruling-fidelity (Ace ruled 30; the code says 32), not capacity.
- Unbounded (the doctrine's elastic instinct, applied naively): session
  memory grows linearly per action (small, but a weeks-long session is
  exactly DellMatrix's use), and the stale-inverse window grows without
  limit — the failure mode is not a crash, it is a plausible-looking wrong
  restore. Unbounded is therefore WRONG for this mechanism even under the
  Elastic Limits Doctrine: the bound mechanism is retained; what changes
  is who sets it and that its losses are receipted.

**The safety cap that must be preserved (Director's condition):** even
with adjustability, a named absolute ceiling stands above the setting:
- `UNDO_DEPTH_MAX` — a named constant; a set above it refuses with the
  ceiling named (§2). **Proposed value: 200**, to be settled in design
  with DD-44's Limit (72) as the bounding authority, exactly as DD-54 §1
  directs. Reasoning: ~6.7× the ruled default (generous headroom under the
  doctrine), worst-case memory still in low MB, and the stale-inverse
  reach stays within a window a user can plausibly remember creating.
- The floor is 1, with refusal below it (a 0-depth "undo" is a
  contradiction, not a setting).
- Drops AT the working bound become observable as part of this correction:
  a drop counter on the Program (the snapshot stack's
  `snapshots_dropped_total` is the in-codebase precedent) and the depth
  shown by `history_report` / `undo depth` — no silent loss at any value
  of the setting.

---

## 5. FAILING-FIRST SKETCH — TESTS THE BUILD CIRCUIT RUNS RED FIRST

New suite (proposed `form/mandell/undo_redo_depth_test.py`, `smoke()`,
registered in form/regress.py LIST beside the PAC-I suites at lines 91/95;
isolated owner state throughout). Each test names its result on UNMODIFIED
main — the build starts from these reds:

- **T1 — Default is 30.** Fresh owner/Program; perform 31 undoable actions
  through the real producer paths; exactly 30 inverses remain and the
  FIRST action is the one that became un-undoable (prove by undoing to
  exhaustion and naming which actions reversed). *Today: FAILS — 32
  remain; the drop happens at 33.*
- **T2 — Adjustability round-trips.** Via the user surface: set depth 5 →
  a 30-deep stack trims to 5 and the reply reports 25 dropped; set depth
  50 → no dropped entry resurrects; save the owner, reload → depth still
  50 and both stacks empty; a second owner still reads 30. Refusals:
  depth 0 and depth 201 (above the ceiling) refuse with reasons and change
  nothing. *Today: FAILS — no setting exists at all.*
- **T3 — Drops at the bound are observable.** At depth 30, push 31; the
  drop counter reads 1 and the depth display shows 30/30. *Today: FAILS —
  no counter, no display, silent pop.*
- **T4 — Redo re-applies, in order.** Place B; edit B's detail; undo
  (detail back to old); undo (B removed); redo → B exists again with the
  detail as captured at its removal (the pre-edit value); redo → detail
  equals the edit's `new`. Final state equals the pre-undo state exactly.
  *Today: FAILS — no redo surface exists.*
- **T5 — Tail invalidation.** Undo once; perform a NEW action; redo
  answers "nothing to redo" and state equals the post-new-action state.
  *Today: FAILS — no redo surface exists.*
- **T6 — Redo bound semantics.** Depth 3; 3 actions; 3 undos; redo tail
  holds exactly 3; three redos succeed; a fourth answers "nothing to
  redo". Shrink depth to 2 with a 3-deep redo tail → tail trims to 2,
  far end first. *Today: FAILS.*
- **T7 — Refusal honesty survives (regression pin, green today, must stay
  green).** Undo of a revision-owned unit still refuses
  `revision_authority`; redo of a place whose id was re-taken refuses and
  mutates nothing; undo/redo on empty stacks answer their honest
  nothings. The existing PAC-I suites (form.mandell.pac_i_test,
  form.mandell.pac_i_proofs_test) stay green unmodified.
- **T8 — Records untouched.** Across a place/edit/undo/redo sequence, no
  frame/commit state changes and `program.history` grows only by the
  existing note_seed evidence pattern (DD-54 §6: state walks, records
  don't). *Today: PASSES for undo; the redo half is new surface the build
  must keep inside the same law.*

Neighbor set for the build's focused verification: pac_i_test,
pac_i_proofs_test, plus the REPL and live_visual command suites that pin
the undo doors, and the persist suites (the setting's persistence must not
disturb the save pair — see §6 risk checks).

---

## 6. THE BOUNDED CIRCUIT PROPOSAL

**Contract.** On the session action stack only: (a) the bound becomes a
named constant defaulting to Ace's ruled **30**, read from a per-owner
adjustable setting under a named safety ceiling (`UNDO_DEPTH_MAX`,
proposed 200, settled with Limit (72)/DD-44 in design); (b) every drop at
the bound is counted and displayable — no silent loss at any setting;
(c) **redo exists** for the session undo with the §3 integration shape and
bound semantics; (d) all existing refusal honesty (revision-owned, missing
unit, empty stack) is preserved verbatim.

**Files touched (proposed, minimal):**
- `form/dell_matrix/needs.py` — `UNDO_DEPTH` / `UNDO_DEPTH_MAX` constants;
  `push_action` reads the effective depth, counts drops, clears the redo
  tail; `undo_last` feeds the redo tail (with the §3.2 place-record
  capture); new `redo_last()`; `history_report` shows depth + drop count.
- `form/open.py` — `Program.undo_depth` (default 30) + `Program.redo()`
  beside `undo()`; the redo-stack field beside `action_stack` (:193).
- `form/repl.py` + `form/dell_matrix/live_visual.py` — the `redo` command
  and the `undo depth` read/set surface beside the existing undo doors;
  help text updated (repl.py:236 line).
- The owner's persisted-state vehicle (persist_rest save/load path) —
  carries `undo_depth` only; both stacks stay ephemeral. (Exact key/field
  placement settled in the build's grounding, against the existing saved
  field set — no new file, no second store.)
- New suite `form/mandell/undo_redo_depth_test.py` + one line in
  `form/regress.py` LIST. Circuit packet + INDEX/queue rows ride the
  circuit PR per standing protocol.

**Test plan.** §5's T1-T8 failing-first (reds recorded on unmodified main
before any edit), then the standard closure: defect-restoring mutants
(restore the literal 32 → T1 must die; remove tail invalidation → T5 must
die; drop the place-record capture → T4 must die), focused neighbors
above, then the ×3 regression campaign and exact-head CI under the usual
gates.

**Risks.**
- *Place-record capture size:* redo entries for places carry a full unit
  record — still small (one unit's fields), bounded by the same depth.
- *Settings persistence touching the save pair:* the everyday-save path
  has its own open defect family (DD-06/Q1); adding one scalar field must
  be proven not to widen it — the persist neighbor suites are in the
  focused set for exactly this reason, and the field rides the existing
  vehicle rather than a new write path.
- *Two depths in the codebase:* after this circuit, the session undo is
  30-and-adjustable while SNAPSHOTS_CAP stays 64. That is a deliberate,
  documented intermediate state (DD-54's unification is C3.Undo scope);
  the packet and the `undo depth` display must say which history they
  govern so the pair is never conflated.

**Keeper pre-plan risk check items (stateful paths) — requested with this
plan:**
1. **Save/load convergence:** a save taken mid-undo-sequence, then reload,
   must yield empty stacks at the persisted depth — no resurrected
   inverses, no lost setting; the save pair's atomicity story unchanged.
2. **Redo re-place vs walls/lineage:** a unit removed from a sandbox box
   or with confirm-lineage state must not reappear via redo outside its
   wall or lineage — re-place goes through the canonical place path and
   its gates, or refuses.
3. **Revision parity:** a unit that ENTERED a revision chain between undo
   and redo must refuse redo exactly as it would refuse undo
   (supersession is never bypassed in either direction).
4. **Open-room composition (DD-54 §6's named design question):** session
   undo/redo while a transaction frame/room is open — Keeper/Director to
   rule whether the session doors defer/refuse while a frame is open;
   the §12.86 shadowing exhibit is the case to answer. This plan takes no
   position; the build does not start that question silently.
5. **Snapshot non-interference:** Revert (spectrum_ops.py:599) and
   `append_snapshot` behavior byte-identical before/after; the two stacks
   share no state.
6. **Multi-owner isolation:** depth setting and both stacks are strictly
   per-owner (per-owner state); no cross-owner read or trim.
7. **Producer completeness:** all four `push_action` producers feed the
   trim + tail invalidation; any OTHER path found placing/editing units
   without pushing is a scope-expanding finding — stop and report, do not
   silently widen coverage (DD-54 §5 claims coverage per-writer, from
   tests, never in blanket).

**Explicit non-goals.** No change to SNAPSHOTS_CAP or any other census cap
(no blanket cap implementation, per the Director's condition); no
unification of the action stack with the snapshot stack and no retirement
of Revert's pop semantics (full DD-54 / C3.Undo circuit, separately
authorized); no new Dell number; no branching or tree history (DD-54 §3
forbids it); no expansion of undo coverage to the Ring-2 writers (DD-54
§5 — future per-writer circuits); `dynamic_view_switch` undo untouched;
no persistence of either stack across restarts.

**Asks.** Director: rule the circuit in this shape (including the
UNDO_DEPTH_MAX value and the §6.4 open-room question) or direct
corrections. Keeper: pre-plan risk check on the seven items above. No Ace
action — DD-54 is already his ruling; this plan executes its bounded R4
slice. No MWL credit is claimed by this packet; MWL row 135 (DD-54 /
C3.Undo) stays OPEN.
