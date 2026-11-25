# ORPHAN DISPOSITIONS — Completeness-Law Investigation Leg (2026-11-15)

**Mode:** READ-ONLY investigation. No code changed, nothing committed.
**Base:** current `main` at **56b6d9cb40cb68d3f50e4c39537769b242cb13a7**
(merge of PR #430, 2026-11-15 07:44:45 -0600), verified in a fresh clone
(`hidden_files/orphan_probe_clone`, working tree clean at start and finish).
All file:line citations are at this head. Probes ran on a throwaway owner
(`ORPHANPROBE2`) inside the isolated clone; the probe created no state
directory and left no residue.

**Verdicts, one line each:**

1. `suggest_preferred` — production-bypassed since birth; its role was
   inherited by ASI-I's `bounded_learned_score`. **STAND DOWN BY DECISION**
   (executable reference + test-contract fixture), with one adjacent doc
   overstatement to correct in the same circuit.
2. `persona_matrix_status()` — write-on-read **PROVEN** by probe
   (in-memory only; no durable-state risk). **DEFECT (hygiene class)**,
   with a load-bearing lazy-sync nuance that shapes the repair.
3. `AutoGrowth._nursery_auto` — no-production-caller claim **CONFIRMED**;
   the dormancy is a ruled charter state with a mechanical tripwire, not
   neglect. **STAND DOWN BY DECISION — receipt already exists**; the only
   gap is a missing completeness-register row.

---

## Item 1 — DuoBeta `suggest_preferred()`

### Trace evidence

- **Definition:** `form/mandell/duobeta_learn.py:352`
  (`def suggest_preferred(program, dell, knowledge_ids) -> List[str]`).
  Ranks knowledge candidates by the transparent raw-integer score
  success − failure − blocked from `preference_index`
  (`duobeta_learn.py:327`); no learning → original order; ties → stable.
  Its docstring: *"This is the bounded 'future selection' DBEL-I
  influences. The certified 37 selector is untouched."*
- **Every caller in the tree (closed-world grep, all file types):**
  tests only —
  `form/mandell/dbel_i_test.py:320, 323, 327, 390, 435` (line 435 embeds
  it in a cross-process probe string) and
  `form/mandell/wo54_learning_test.py:48, 73, 79`.
  No production caller, no internal caller inside `duobeta_learn.py`,
  no REPL command, registry entry, or dynamic reference anywhere.
- **Doc references:** `duobeta_learn.py:89, 95, 395` (the saturation
  contract's normative ordering references — "See suggest_preferred");
  `docs/DCC_KNOWLEDGE_SCOPE.md:1225, 1243, 1258`;
  `director-reports/SYSTEM_001_2026-11-14/SYSTEM_GAP_AND_CONFLICT_LEDGER.md:197`
  (entry X-7, "production-bypassed selector") and
  `SYSTEM_MASTER_ARCHITECTURE.md:29`.
- **History:** introduced by commit `5b2f66c` (NBD-Ω-007, DBEL-I).
  `git log -S "suggest_preferred"` across the whole history touches only
  `duobeta_learn.py`, its test suites, and docs — **it never had a
  production caller**; nothing was removed from under it.
- **What it was for:** DBEL-I's "future selection influence" query — the
  surface through which accepted DuoBeta learning would reorder future
  knowledge selection, advisory only ("influence != authority —
  `suggest_preferred` advises; selectors decide",
  `docs/DCC_KNOWLEDGE_SCOPE.md:1258`).
- **What replaced it:** ASI-I (NBD-Ω-008, commit `44c38c5`) closed the
  production learning loop through a different member of the same module:
  the production selector `form/mandell/knowledge_selector.py:326-338`
  imports and consumes **`bounded_learned_score`** (`duobeta_learn.py:381`)
  — a per-candidate saturated score applied after the hard laws and the
  `max_selected` limit. The third member, `preference_index`, remains
  production-live on its own: `form/mandell/knowledge_influence.py:478`
  and `form/mandell/runtime_observe.py:664-666`. `suggest_preferred` is
  the only dead member of the trio. Production test comments state the
  bypass explicitly: `form/mandell/asi_i_test.py:221` ("Execution after
  learning → Outcome V1 (production path, not suggest_preferred)") and
  `form/mandell/wo54_consumers_test.py:5` ("the real selector (not merely
  suggest_preferred)").

### Disposition: STAND DOWN BY DECISION

Stated reason (Ace's activation clause — a stand-down needs a reason, not
neglect):

1. **It is an executable reference, not dead weight.** The saturation
   contract in the same file defines its ordering semantics by pointing
   at this function (raw integers have perfect strict ordering; the
   saturated float is display/influence only). Retiring it orphans the
   normative reference two production docstrings rely on.
2. **It is the contract fixture for the learning law.** `dbel_i_test`
   and `wo54_learning_test` pin the DBEL-I / WO-5.4 contract through it:
   influence OFF → baseline order, influence ON → learned order,
   tie-stability, cross-process identity. `bounded_learned_score` cannot
   absorb those pins unchanged — it is a per-item saturated-float API
   and cannot express whole-list ranking; re-basing the suites on it
   would weaken the evidence for the very contract production depends on.
3. **REVIVE is the one wrong answer.** Wiring `suggest_preferred` into a
   live path would create a second selection authority beside
   `knowledge_selector` — the exact duplication the authority laws
   prohibit — to deliver influence production already receives through
   ASI-I.
4. **Activation condition (when it would wake):** a future surface that
   needs a whole-list learned ranking *not* routed through the Dell-37
   contextual selector. No such surface exists or is planned.

**Adjacent defect (doc, not code):** `docs/DCC_KNOWLEDGE_SCOPE.md`'s
learning-law diagram still names `suggest_preferred` as the FUTURE
SELECTION INFLUENCE query — the design doc presents the bypassed surface
as the production influence path. SYSTEM_001 ledger X-7 already reached
the same stand-down shape ("it survives as a test fixture for the
learning contract, which is a lawful role only if recorded as one");
this report is that recording on the Uni side.

### Bounded circuit if the Director authorizes it

Records/annotations only; zero behavior change:

1. Add a stand-down status block to the `suggest_preferred` docstring
   (`duobeta_learn.py:352`): production influence = ASI-I /
   `bounded_learned_score` via `knowledge_selector`; this function =
   reference implementation + DBEL-I/WO-5.4 contract fixture; activation
   condition as above.
2. Correct the learning-law diagram in `docs/DCC_KNOWLEDGE_SCOPE.md`
   (the `:1225` line) to name ASI-I / `bounded_learned_score` as the
   production influence and `suggest_preferred` as the reference/test
   surface.
3. Enter the stand-down in the completeness register with this trace.
4. Verification: `dbel_i_test` and `wo54_learning_test` smokes pass
   **unedited** (any required test edit falsifies the "no behavior
   change" claim and stops the circuit).

---

## Item 2 — `persona_matrix_status()` write-on-read

### The claim

PR comment 6821351909 (PR #397 changed-caller/contract audit, item 5)
proposed a findings-register row: `Program.persona_matrix_status()`
writes `persona_matrix.active` on read; `personas_status()` nests it,
making `Program.status()` write-on-read transitively; the same write
exists in `persona_matrix_ascii()`. **The proposed row is accurate in
every particular tested.**

### Trace evidence

- **The write:** `form/open.py:748`, inside
  `persona_matrix_status` (`form/open.py:747-749`):
  `self.persona_matrix.active = self.persona_lens` executes before
  `return self.persona_matrix.to_dict()`. Identical assignment at
  `form/open.py:752`, inside `persona_matrix_ascii`
  (`form/open.py:751-754`).
- **The written field:** `PersonaMatrix.active`
  (`form/dell_matrix/personas.py:355-358`) — an in-memory attribute of a
  small view object (`cells()` / `render_ascii()` / `to_dict()`).
- **Transitive wrappers:** `personas_status()` (`form/open.py:807-817`)
  nests the call for its `"matrix"` key (`open.py:815`);
  `Program.status()` (`form/open.py:2147`) aggregates both
  (`open.py:2177`).
- **Production callers of the writing wrappers:**
  `form/dell_matrix/live_visual.py:238` (visual snapshot), `:582`
  (ascii) and `:583` (status) for the matrix display;
  `form/repl.py:2422` (ascii, REPL `matrix personas`);
  plus the two `open.py` nestings above.
- **Known avoiders (the harm is already routed around, twice):**
  C7.Schema's board reads `persona_matrix.to_dict()` directly and
  documents why (`form/dell_matrix/schema_board.py:41, 151, 169`);
  C13 Simulate's baseline capture excludes it by name
  (`form/dell_matrix/simulate_board.py:29`); the impurity is
  digest-pinned by `form/c7schema_test.py` test 7 (docstring `:31`,
  setup `:209`).

### Probe (throwaway owner `ORPHANPROBE2`, fresh clone, state hashed
before/after each call)

| Step | Setup | Result |
|---|---|---|
| S1→S2 | lens set via sanctioned `set_persona_lens("melody")` (syncs both fields) | status call is a **no-op**; returned active `melody` |
| S3→S4 | lens assigned directly (`p.persona_lens = "manny"`); matrix still showed stale `melody` | **ONE status call flipped `persona_matrix.active` `melody` → `manny`**; the read manufactured the agreement it then reported |
| S5→S6 | lens `aetheris`, matrix.active reset to `None` | `personas_status()` flipped it `None` → `aetheris` (nested write confirmed) |
| S7→S8 | lens `oracle`, matrix.active `None` | `persona_matrix_ascii()` flipped it `None` → `oracle` |
| disk | owner state dir hashed around a status call | **untouched** — the call performs no save and creates no state |

### Bounds of the write (why severity is low)

- **In-memory only.** `PersonaMatrix` is never serialized.
  `form/persist.py:357` persists `persona_lens`;
  `form/persist_rest.py:597` restores the lens and `:627` rebuilds
  `PersonaMatrix(active=persona_lens)` at load. The mutation therefore
  cannot reach disk as matrix state and cannot survive a reload as
  anything other than the lens value itself. No durable corruption is
  possible from this write.
- **The output is always lens-consistent after the call** — the harm is
  not wrong output; it is that a read creates the state it reports, so
  two reads of the same program can disagree depending on whether a
  wrapper ran in between (probe S3's direct `to_dict()` said `melody`
  while the lens was already `manny`).

### The mechanism nuance the register proposal did not name

Every production writer of `persona_lens` syncs the matrix in the same
breath — `set_persona_lens` (`open.py:730-737`), `bimo_fuse`
(`open.py:776-777`), the REPL pilot paths (`form/repl.py:2476-2477`,
`4177-4190`, which even restores `prior_matrix` on rollback) — **except
one**: the Studio/visual `bimo pilot` handler,
`form/dell_matrix/live_visual.py:604-607`, assigns
`program.persona_lens = out["pilot"]` and does **not** touch
`persona_matrix.active`. For that path, the wrapper's write is the
de-facto lazy sync — and the sync happens inside live_visual's own
display call (`:583`). The write-on-read is therefore **load-bearing
for exactly one unsynced writer**; purifying the readers without
syncing that writer would leave the Studio matrix display stale after
`bimo pilot`.

### Classification: DEFECT (hygiene class)

Pre-existing (not a C7 defect), undeclared at its definition site — the
only documentation of the mutation lives in *other* modules' warnings,
so it is not "by-design with receipt": no receipt exists. It is a real
defect of the read-purity class with bounded blast radius (in-memory,
non-durable, output-consistent), already costing two boards a bypass
each.

### Bounded repair circuit if the Director authorizes it

1. **Failing-first:** a purity check in the c7schema t7 style — assign
   the lens directly, digest the program around
   `persona_matrix_status()` / `persona_matrix_ascii()` /
   `personas_status()`; today it goes red on `persona_matrix.active`.
2. **Sync the one unsynced writer:** at `live_visual.py:606`, set
   `program.persona_matrix.active = out["pilot"]` beside the lens
   assignment (mirroring `repl.py:2476-2477`).
3. **Purify the readers:** delete the assignment lines at
   `open.py:748` and `open.py:752`; both wrappers return
   `to_dict()` / `render_ascii()` purely. (The sanctioned writer
   `set_persona_lens` and load-time derivation at
   `persist_rest.py:627` already keep the fields in agreement on every
   other path.)
4. **Regression:** c7schema_test (t7 must stay green — the board's
   bypass remains lawful, merely no longer necessary), the live_visual
   / Studio visual suites, the REPL matrix-personas path, the Bimo
   pilot suites (incl. pp4_bimo_dock), then the canonical regress ×3.
5. **Register:** land the row proposed in comment 6821351909 with the
   repair receipt appended, so the hygiene item closes with its
   evidence chain intact.

---

## Item 3 — `AutoGrowth._nursery_auto`

### The claim (Q-S2.1 label circuit)

`AutoGrowth._nursery_auto` has NO production caller (tests only).
**CONFIRMED** on current main, with a richer context than "orphan":
the dormancy is a ruled, mechanically tripwired state.

### Trace evidence

- **Definition:** `form/dell_matrix/auto_growth.py:126`
  (`AutoGrowth._nursery_auto`, class at `:99`). It loads the
  `AutoGrow` owner's persisted Program (`_load_owner_program`, `:167`),
  adds a Nursery proposal (kind `"auto"`), then disposes of it:
  auto-confirm via `Program.confirm_proposal(..., _producer="auto_growth")`
  only when the opt-in flag, the injected judge's thresholds, and the
  AcceptancePolicy producer gate all pass — otherwise auto-reject. It is
  the one machine path that *disposes of* proposals.
- **Callers of `_nursery_auto` (closed-world grep):** its definition,
  the module docstring (`auto_growth.py:5`), and tests only —
  `form/dell_matrix/pp2_autonomy_charter_test.py:163, 170, 180`,
  `form/lineage_authority_test.py:172, 187, 202, 270, 284, 299, 312`,
  and an existence pin at `form/mandell/p8_sd5_test.py:204`.
- **No wiring of any kind:** zero `AutoGrowth(` constructions outside
  tests; zero non-test imports of `form.dell_matrix.auto_growth` (the
  only non-test hit is `form/open.py:1689`, which merely names the
  `"auto_growth"` producer-id string for the AcceptancePolicy gate —
  naming is not wiring, as the charter test itself notes). No internal
  caller remains in `auto_growth.py`. No dynamic-dispatch path found
  (the tree's `importlib` uses target unrelated modules).
- **What it was for:** WO-5.1's automated Nursery producer — the
  disposition engine of the continuous-growth orchestration.
- **Why it is dormant — two recorded decisions, not neglect:**
  1. **SD-5 trim** (module docstring, `auto_growth.py:5-20`): the
     orchestration that called it (`step` / `run_continuous` /
     `harvest_net` / `next_query` / `_judge`) was RETIRED — it had no
     production caller and its judging coupled to retired modules —
     while `_nursery_auto` was deliberately **KEPT** as "the canonical
     auto-propose path", contract-proven by `lineage_authority_test.py`.
     The growth judge is now the docked semantic layer (SD-1..SD-4) and
     the growth engine is RingedGrowth. `p8_sd5_test.py:204` pins the
     disposition mechanically (`autogrowth_keeps_only_live_authority`:
     `_nursery_auto` present; `step` / `_judge` / `harvest_net` absent).
  2. **PP2 Autonomy Charter** (Ace's rule, 2026-10-27: decide what is
     automatic vs authority-confirmed; nothing outside authority's
     awareness): `pp2_autonomy_charter_test.py` pins the dormancy with
     a static scan (`_check_dormancy`) over every production file — if
     anyone imports the module, constructs `AutoGrowth`, or touches
     `_nursery_auto`, the suite turns red and "the charter must be
     re-ruled". The same suite pins its disposition behavior in its own
     owner (flag OFF → even a perfect judge is auto-rejected; flag ON →
     confirm *attempt*, still denied by the policy gate without a
     producer opt-in).
- **Sub-finding (an orphan inside the kept file):**
  `_commit_ledger` (`auto_growth.py:172`) has **no caller anywhere**
  since SD-5 retired its orchestration caller; `_load_ledger` /
  `_save_ledger` (`:58`, `:75`) serve only it. The read side stays
  test-consumed: `ledger_dropped_total()` (`:66`) is exercised by
  `form/dell_matrix/pp2b_rulings_test.py:225-236`.

### Disposition: STAND DOWN BY DECISION — receipt already exists

Uniquely among the three items, this stand-down is not waiting for a
receipt: the PP2 charter, the SD-5 docstring, and two mechanical pins
(the dormancy scan and the SD-5 disposition check) *are* the receipt,
and they are load-bearing — the dormancy scan is a live tripwire, not a
memorial.

- **RETIRE** would require re-ruling the PP2 charter and deleting the
  contract-proven canonical auto-propose path the charter deliberately
  preserves dormant-but-proven. Nothing in the evidence suggests the
  charter's judgment has been revisited.
- **REVIVE** is prohibited without a charter re-rule: Ace's autonomy
  rule bars automatic disposition outside authority's awareness, and
  AcceptancePolicy denies machine producers by default.
- **Activation condition:** a Director/Ace charter re-rule that names a
  production growth surface for machine proposals, with the producer
  opt-in granted through AcceptancePolicy. The dormancy scan turning
  red is the designed signal that such a re-rule is due.

**Remaining honest gap:** the completeness register carries no row for
this stand-down, so orphan sweeps keep re-flagging a ruled dormancy as
if it were neglect (this investigation is at least the second time —
the Q-S2.1 circuit flagged it first). The fix is a register row, not
code.

### Bounded circuit if the Director authorizes it

Register-only; zero code change:

1. Enter the stand-down in the completeness register citing: PP2
   Autonomy Charter (Ace, 2026-10-27), the SD-5 trim record
   (`auto_growth.py:5-20`), the dormancy scan
   (`pp2_autonomy_charter_test.py` `_check_dormancy`), the SD-5 pin
   (`p8_sd5_test.py:204`), and this trace.
2. One micro-disposition for the Director to rule inside the same row:
   `_commit_ledger` + `_load_ledger` + `_save_ledger` — recommendation:
   **keep as one unit with the ledger surface**. `_commit_ledger` is
   the ledger's only writer and the PP2b rulings pin the ledger's
   eviction accounting (`dropped_total`); retiring the writer while
   keeping the reader would strand the surface in a state no decision
   chose. If the Director prefers otherwise, retire the writer trio
   together and keep `_read_ledger_file` / `ledger_dropped_total` as
   the read-only remainder — never the writer alone.

---

## Anticipated probes

- **"Prove `suggest_preferred` never had a production caller."**
  `git log -S "suggest_preferred"` over full history touches only
  `duobeta_learn.py`, `dbel_i_test.py`, `wo54_learning_test.py`, and
  docs; ASI-I (`44c38c5`) built the production loop on
  `bounded_learned_score` in the commit immediately following DBEL-I
  (`5b2f66c`). The selector file was never among the touched files.
- **"Prove purifying the persona readers breaks nothing."** The one
  dependency is named with its fix: `live_visual.py:606` is the sole
  unsynced lens writer (full production assignment grep in Item 2);
  every other writer syncs, load re-derives, and the two boards that
  bypass the wrappers today keep working because `to_dict()` is
  unchanged. The failing-first purity check in the circuit is the
  instrument that would catch any missed consumer.
- **"Could `_nursery_auto` be reached through the dock or a provider?"**
  No import path exists: the dock's producer surface is its own
  `propose()` path into `Nursery.add`; the closed-world grep shows the
  module's name in production only as a policy-gate string
  (`open.py:1689`), and the charter's dormancy scan would have turned
  red on any wiring since 2026-10-27.
- **"Is `suggest_preferred` reachable through a Dell atom or the REPL?"**
  No registry, executor, or REPL reference exists anywhere in the tree
  (all-file-types grep). Its only executors are its two test suites.

## Questions for the Director

- **Q-OD.1 (Item 1):** Ratify the stand-down + doc-correction circuit
  for `suggest_preferred` (docstring status block +
  `DCC_KNOWLEDGE_SCOPE.md` influence line + register row, zero behavior
  change) — or direct retirement with re-basing of `dbel_i_test` /
  `wo54_learning_test` onto `bounded_learned_score`, accepting the
  weaker whole-list ranking evidence?
- **Q-OD.2 (Item 2):** Authorize the two-half hygiene repair (sync the
  `live_visual.py:606` writer + purify both readers) as one bounded
  circuit with the failing-first purity check? And: is any authority
  surface known to *depend* on `status()` re-syncing the matrix after a
  direct lens assignment, beyond the Studio `bimo pilot` path named
  here?
- **Q-OD.3 (Item 3):** Record the completeness-register row for the
  `_nursery_auto` stand-down (charter + SD-5 citations) so the orphan
  sweep stops re-flagging a ruled dormancy? Within the same row, rule
  the `_commit_ledger` micro-disposition: keep-as-unit (recommended) or
  retire the writer trio?
- **Q-OD.4 (all items):** Should stand-down rows carry a revisit
  trigger (e.g., "re-examine at the next census") so a recorded
  stand-down cannot silently become the next decade's neglect?

---

*Evidence classes: Item 1 — code trace + git history (FACT). Item 2 —
code trace + executed probe on a throwaway owner (FACT, probe table
above). Item 3 — code trace + charter/test records (FACT). Dispositions
are Uni recommendations; certification and credit remain the
authorities'.*
