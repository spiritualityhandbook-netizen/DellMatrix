# LIMITS VERIFICATION — WAVE 1 (2026-11-15)

Read-only verification of the first five HINDERS-US items in the Limits Census register
(`hidden_files/limits_census/CENSUS.md`, inventoried at main `a9e8b561`), re-verified
first-hand at **current main `17ae4ce86743d9c5ff848a1b48111119d9bf9a32`** (g31proof_clone,
clean tree). No code changed; nothing committed. Probes ran against the clone's own
`form/` tree with isolated stub programs / a throwaway probe owner (state removed after).

**Skip note:** register item **R1** (Nursery stored-words cut, `words[:240]`) is first in
the register but is excluded per the wave brief — already repaired as SYS-C29 (PR #429).
Wave 1 therefore covers **R2–R6**.

---

## R2 — Dock prompt bound 8,000 + validator ceiling 100,000

- **Census sites:** inference_dock.py:46; validator :1918-1922.
- **Sites today:** `DEFAULT_MAX_PROMPT_CHARS = 1000000` at `form/dell_matrix/inference_dock.py:54`
  (was 8,000); the `dock()` validator at `inference_dock.py:2023-2027` now caps
  `max_prompt_chars` at `DEFAULT_MAX_PROMPT_CHARS` itself, under a comment citing the
  Elastic Limits Doctrine ("the prompt bound's legal range rises with its default").
  Enforcement points (refuse `prompt_too_large`) at `inference_dock.py:1114, :1168, :1187, :1849`.
- **Probe (functional, at 17ae4ce):**
  - `dock(program, …, max_prompt_chars=100001)` — **admitted** (the census-era 100,000
    validator ceiling would have raised `DockError`).
  - Default-bound session `propose()` with a 9,000-char prompt → `ok=True` (refused
    `prompt_too_large` at the census-era 8,000 default).
- **Scope honesty:** `DEFAULT_MAX_RESPONSE_CHARS` is still 8,000
  (`inference_dock.py:55`) — that is register item **R8**, not R2, and is not covered
  by this disposition. `_MAX_CONTEXT_CHARS` remains 100,000 (`inference_dock.py:360`);
  the census carried it as its own GUARDS-US row, and R2's specific harm (zero headroom:
  no legal session bound could admit a legal context's assembled prompt) is discharged
  now that the prompt bound may be set to 1,000,000.
- **DISPOSITION: ALREADY-FIXED** — by PR #416 (LM-4), merged on main; both halves of the
  census sketch (raise the default; raise the validator range to admit it) are in the code.

## R3 — The docked mind's snapshot vision stack: 200 + 200 + 16 + 512 + 8×128

- **Sites today (all unmoved):** `form/dell_matrix/agent_coordinator.py:110`
  (`_MAX_SNAPSHOT_IDEAS = 200`), `:111` (`_MAX_SNAPSHOT_UNITS = 200`), `:112`
  (`_MAX_RETRIEVE_IDS = 16`), `:119` (`_MAX_STR_LEN = 512`); snapshot slices at
  `agent_coordinator.py:784` and `:787` (`list(...)[:_MAX_SNAPSHOT_*]`, census lines
  unmoved); entry cuts at `:692-693, :700, :710-711, :715`; goals windows at `:702, :717`;
  retrieve hard error at `:847-850`.
- **Mechanism:** `HostCoordinator.snapshot_for` windows the Nursery proposals and Plane
  units a docked Psalm can see to the first 200 of each (insertion order); every entry's
  label/words/detail is cut to 512 chars and goals to 8×128; fetching beyond the window
  is capped at 16 ids per `retrieve_for` round with a hard `CoordinatorError` and no
  partial result. The coverage block reports the truncation truthfully (post-PR #336
  machinery, unchanged).
- **Probe (functional, stub program at 17ae4ce):**
  - 251 proposals / 250 units → coverage `{ideas_total: 251, ideas_returned: 200,
    units_total: 250, units_returned: 200, truncated: True}`.
  - Single-entry probe: label 600 → **512**, words 5,000 → **512**, detail 3,000 → **512**,
    goals 10×200 → **8×128**.
  - `retrieve_for` with 17 distinct ids → `CoordinatorError: retrieve_for bound exceeded:
    at most 16 ids per round` — no partial result.
- **DISPOSITION: CONFIRMED-HINDERS** — every sub-bound binds exactly as the census
  described, at realistic scale (the 1,052-unit Email Matrix field exceeds the windows
  ~5×). *Failing-first sketch for the repair circuit:* build a coordinator over a
  251+-unit field; assert (a) `snapshot_for` coverage returns all units or pages with a
  continuation the dock actually consumes, and (b) `retrieve_for` with 17+ ids returns
  all requested entries (partial results + coverage instead of a hard error) — both fail
  today at the sites above.

## R4 — Undo: 32 hard-coded where Ace ruled 30-and-adjustable; redo does not exist

- **Sites today (unmoved):** `form/dell_matrix/needs.py:197-198` —
  `while len(st) > 32: st.pop(0)` inside `push_action`, operating on
  `Program.action_stack` (`form/open.py:193`); reached via `Program.undo()` →
  `needs.undo_last` (`needs.py:241`). The bound is a bare literal: no named constant,
  no per-owner setting.
- **Probe (functional):** 33 `push_action` calls on a stub program → stack length **32**,
  the first entry (n=0) silently evicted; the 33rd action makes the 1st un-undoable.
- **Redo:** `grep -rn "redo" form/ --include="*.py"` returns no implementation
  (`form/repl.py` count: 0). There is no redo path to probe.
- **DISPOSITION: CONFIRMED-HINDERS** — unchanged since the census, and still the
  register's outright ruling-violation: Ace ruled **30 steps, adjustable**; the code has
  **32, hard-coded**, and redo is absent capability, not a tuned bound.
  *Failing-first sketch:* push 33 actions through the public undo path; assert the depth
  equals the ruled setting (default 30, adjustable per owner) and that entry #1's
  undoability follows the setting, not a literal — fails today at `needs.py:197-198`;
  a companion assertion for a redo surface fails today because none exists.

## R5 — Program history capped at 24, enforced three times independently

- **Sites today:** in memory — `form/open.py:130` (`history_max: int = 24`) and the trim
  at `open.py:340-341`; at save — `form/persist.py:373`
  (`"history": list(...) [-24:]`, a second, independent literal); at load —
  `form/persist_rest.py:632` (`p.history = [str(h)[:120] for h in hist][-24:]`, a third
  literal, plus a 120-char per-entry cut). `Program.note()` itself also cuts each entry
  to 120 chars at `open.py:338`. (The REPL display default is now n=16 at
  `form/repl.py:2290` — a display parameter over the same 24-entry store.)
- **Probe (functional, real Program at 17ae4ce):** 25 `note()` calls → `len(history) ==
  24`, first surviving entry `action-01` (action-00 evicted); a 200-char note is stored
  at exactly **120** chars.
- **DISPOSITION: CONFIRMED-HINDERS** — any session noting >24 actions permanently loses
  the earliest; `replay`/`macro` can never reach them; the three enforcements are still
  three independent literals, so no single change lifts the bound.
  *Failing-first sketch:* note 25 actions, save, reload; assert all 25 survive the round
  trip — fails today at the first trim (`open.py:340-341`), and would still fail at
  `persist.py:373` / `persist_rest.py:632` if only the in-memory site were lifted.

## R6 — MAX_PARENTS=4 and relate_field's illusory limit (judge sees ≤3)

- **Sites today:** `MAX_PARENTS = 4` at `form/dell_matrix/inference_dock.py:555`
  (census: :547); semantic-output enforcement at `:611`; synthesize target guard
  `2 <= len(ids) <= MAX_PARENTS` at `:1503` (docstring at `:1497`: "Author a genuinely
  new idea from 2..4 field entries"); relate_field shown cap at `:1730` —
  `shown = min(limit, MAX_PARENTS - 1)` — under the site's own comment at `:1726-1729`
  conceding "at most MAX_PARENTS - 1 candidates can go to the judge, however large
  `limit` is" (documented limit range 1..20, default 5).
- **Probe (functional):** `validate_semantic_output` with a schema-valid judgment
  carrying **5 parents → REJECTED** (`ProviderError: parents must be a bounded list of
  strings`); the identical judgment with **4 parents → ADMITTED**. The relate_field
  shown-cap itself is inline arithmetic inside the verb (not separately callable);
  that half rests on code reading of `:1726-1730`, labeled as such.
- **DISPOSITION: CONFIRMED-HINDERS** — synthesis across 5+ field entries is impossible
  by construction, and on a field of any size the field-relating judge ever sees at
  most 3 candidates; the documented `limit` (up to 20) does not mean what it says.
  *Failing-first sketch:* on a field with ≥20 scored candidates, call relate_field with
  `limit=20` and assert the judge is shown >3 candidates; call synthesize with 5 target
  ids and assert acceptance — both fail today (`:1730` shown=3; `:1503` bad_targets).

---

## Wave summary

| Item | Site today (main 17ae4ce) | Disposition | One-line basis |
|---|---|---|---|
| R2 — dock prompt bound + validator ceiling | inference_dock.py:54; validator :2023-2027 | **ALREADY-FIXED** | Default now 1,000,000 and validator range rises with it (PR #416); probe: 100,001 admitted, 9,000-char prompt ok at default |
| R3 — snapshot vision stack 200/200/16/512/8×128 | agent_coordinator.py:110-112, :119 | **CONFIRMED-HINDERS** | Probe: 251→200 returned, entry fields cut to 512, goals 8×128, retrieve_for(17) hard-errors with no partial result |
| R4 — undo 32 hard-coded, no redo | needs.py:197-198 | **CONFIRMED-HINDERS** | Probe: 33 pushes → 32 kept, oldest silently evicted; no named constant/setting vs ruled 30-and-adjustable; zero redo in form/ |
| R5 — program history 24 ×3 enforcements | open.py:130/:340-341; persist.py:373; persist_rest.py:632 | **CONFIRMED-HINDERS** | Probe: 25 notes → 24 kept, first lost; entries cut to 120; three independent literals still enforce the same cap |
| R6 — MAX_PARENTS=4 / relate_field shown ≤3 | inference_dock.py:555; :1503; :1730 | **CONFIRMED-HINDERS** | Probe: 5-parent judgment rejected, 4 admitted; shown = min(limit, 3) however large the field or limit |

**Queued for wave 2 (next five in register order):**
R7 — flag defeats itself at field scale (inference_dock.py 40-neighbour index) ·
R8 — dock response bound 8,000 discards whole responses (inference_dock.py:55 today) ·
R9 — whole-output schema rejections (one long field kills the entire docked output) ·
R10 — exchange replication caps (50/packet, 200 stored, refusal at 200 live) ·
R11 — Ace's review surfaces show 20 of N / 12 of N (repl.py pending/ranked slices).
