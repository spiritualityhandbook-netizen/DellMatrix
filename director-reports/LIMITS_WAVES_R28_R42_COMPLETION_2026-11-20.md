# GP-E06 — LIMITS WAVES R28–R42 COMPLETION RECORD (2026-11-20)

**Circuit:** GP-E06 (Edition 1, 02_EXECUTION_CIRCUITS.md) — the
merged R2–R26 matrix is not the end of the 42-row census; the
wave-completion record for R28–R42 at current main was still owed
(several wave verdicts predate later repairs). This record is that
completion: every row R28–R42 re-probed against current main and
classified. Delivered in Part III's successor code-stage PR under
Director disposition 7057289921 (PR #502). No code PR is created
for a disproven defect, and no defect is built here: confirmed
LIVE_DEFECTs are filed below as patch notes to their home Parts.

**Probe base:** main `c6ee38d97ce929850f1321004db681b2a6f619ca`
(branch `uni/part-3-code-stage`, exact base of this PR).
**Method:** fresh-main source verification of every wave-pinned
site at the base above (sites re-located where files moved into
`form/dell_matrix/`), plus fresh behavioural probes where the
probe is a pure public-path call (R29, R38). Wave-era behavioural
probes (LIMITS_VERIFICATION_WAVE6/7/8_2026-11-15.md, PRs #449 /
#484) are cited where a stateful Program probe would be
campaign-class work; those citations are labelled as wave
evidence, not re-run here. Classifications use the GP-E06
vocabulary: ALREADY_FIXED / FAITHFUL_GUARD / UNRULED_VALUE /
LIVE_DEFECT / DORMANT / EVIDENCE_GAP.

## Per-row verdicts

| Row | Classification | Fresh-main receipt |
|---|---|---|
| R28 — forces/grow insertion-ordered partial vision | **LIVE_DEFECT** | `form/open.py` parallel-forces block (grow path): plants `list(plane.units.items())[:12]`, water flows `[:3]`, insertion-ordered, and `result["forces"] = self.forces.status()` carries no skipped-set count or names. Wave 6 behavioural probe (16-unit plane: 8 planted / 3 flowed, exclusion permanent) stands; the source pattern is unchanged at this base. |
| R29 — create field caps | **LIVE_DEFECT** | Behavioural probe at this base via the public parse path `form/idea_create.py:parse_create_line`: label 100 chars → 80, detail 2500 chars → 2000, returned dict keys carry no truncation marker or total; `goals[:12]` source-verified in the same return dict. Wave 6 narrowing stands (strength sub-claim refuted there; words-500 site dead, operative preview bound 120). |
| R30 — checkpoint current+previous | **FAITHFUL_GUARD** | `form/mandell/checkpoint_generation.py:288` `_retain_current_and_previous` intact: returns `{"kept": [...], "removed": n}` receipt; on an unreadable pointer it deletes nothing (`"pointer unreadable; nothing deleted"`). Documented DCC-XVIII conservative design; do not increase retention blindly. |
| R31 — coordinator audit 500 eviction, no dropped counter | **LIVE_DEFECT** | `form/dell_matrix/agent_coordinator.py:113` `_MAX_AUDIT_RECORDS = 500`; eviction loop at :606 (`while len(records) > _MAX_AUDIT_RECORDS`) drops from the front; no `dropped` counter exists anywhere in the module at this base. Wave 6 probe (505 captures → 500 retained, loss uncounted) stands. |
| R32 — Studio JS second 400-edge cut beneath payload 480 | **LIVE_DEFECT** (narrowed) | Payload half is a FAITHFUL_GUARD: `form/dell_matrix/live_visual.py:266-267` discloses `edges_total` / `edges_shown` against `_EDGE_CAP = 480` (:192). The Studio draw slice persists: `form/dell_matrix/assets/js/core.js:288` `edges.slice(0, 400)` draws 400 of the payload's 480 with no on-canvas disclosure — the coverage line overstates the canvas by up to 80. |
| R33 — growth fog 72 | **FAITHFUL_GUARD** | `form/dell_matrix/ringed_growth.py:46` `FOG_MAX_LABEL_LEN = 72`, gate at :373. Both live label constructors stay below it: `_combine_label` (:395) caps inputs at 22+22 chars (~47 composed), `_evolve_label` (:402) caps at `[:70]`. The >72 arm remains unreachable from live callers (wave 7 finding re-verified in source); skips that do occur are counted in aggregate `fog_cut`. Do not "repair" an unreachable defect. |
| R34 — BIMO committed config silent retirement | **LIVE_DEFECT** | `form/dell_matrix/bimo_forge.py:51` `_MAX_CONFIGURATIONS = 10`; no dropped/retired/evicted counting exists in `bimo_forge.py` or `session_kit.py` at this base. Wave 7 probe (12 valid configurations → newest 10 kept, retired record preserved/counted/named nowhere; the dock later refuses the retired name as "unknown") stands. |
| R35 — scrub_context 2000 | **DORMANT** | Whole-tree grep at this base: `scrub_context` (`form/dell_matrix/inference_dock.py:332`) is referenced only by its own recursion (:343/:346). No production caller; the live path `validate_context` preserves scalars whole (wave 7 probe). Latent hazard if ever wired; not a live limit. |
| R36 — context-node 1000, inconsistent char budget | **UNRULED_VALUE** | `form/dell_matrix/inference_dock.py:359-360`: `_MAX_CONTEXT_NODES = 1000` beside `_MAX_CONTEXT_CHARS = 100000`; enforcement at :391-395 refuses whole with the explicit error `bad_context: nodes exceed 1000`. The refusal is honest and stable (no silent loss — not a defect); the node budget is inconsistent with its char sibling by ~5× for small-scalar contexts and no ruling names the value. |
| R37 — validated 11-slot BIMO 1287-char framing cut to 1200 | **LIVE_DEFECT** | `form/dell_matrix/inference_dock.py:1105` (`_bimo_framing`, :1074): `return "\n".join(lines)[:1200]` — the silent mid-line cut persists at this base, no marker, while the session record carries the configuration as worn. Wave 8 probe (1,287-char validated framing returned as exactly 1,200, last slot severed mid-word) stands. |
| R38 — Bridge result to_dict text 8000 | **LIVE_DEFECT** | Behavioural probe at this base: `ProviderResult("claude", True, text=20000 chars).to_dict()` (`form/llm/bridge.py:48`) returns text of exactly 8,000 chars; the dict's keys (`provider/ok/text/error/meta`) carry no length, total, or truncation flag. The in-memory result is whole; the loss is created silently at the serialization boundary every consumer reads. |
| R39 — Claude output cap 2048, dropped stop_reason | **LIVE_DEFECT** | `form/llm/bridge.py:425`: the `_claude` payload hard-codes `"max_tokens": 2048`; `dispatch()` (:233) threads model/timeout/max_bytes only — no caller can reach the bound; no `stop_reason` handling exists in `bridge.py` at this base, so a `max_tokens` truncation returns as an ordinary result. The 2048 value itself is UNRULED (noted); the defect is the non-propagation. |
| R40 — research windows 24, words 400 | **DORMANT** | Windows verified in source: `form/dell_matrix/internet_gate.py:404` `ideas: unique[:24]`, :371/:387 `words: ...[:400]`; the surface discloses totals (wave 8). No production caller reaches `search_far_wide` at this base — grep finds only the module itself and `form/mandell/gate_hardening_test.py`, whose header states "No Program/REPL caller reaches search_far_wide today". An unconsumed contract, not a live Nursery starvation. |
| R41 — lattice shape {12,14} | **FAITHFUL_GUARD** | `form/dell_matrix/harmonic_core.py:34` `ALLOWED_SIZES = (SIZE_CHROMATIC, SIZE_HARMONIC)`; `normalize_size` (:48-53) snaps, declared in the module docstring and smoke-pinned in-module (:191-192); `set_lattice_size` returns the actual size plus the allowed set and all cells survive (wave 8 probe). A declared shape policy on an unbounded store; keep unless separately ruled. |
| R42 — all_entities Nursery ghosts 12 | **ALREADY_FIXED** | The [:12] ghost cap is gone: `form/open.py:558-570` (`all_entities`) iterates `self.ranked_proposals()` whole, and the in-source comment names the defect ("the historical [:12] cap silently presented 12 as the count (the R42 defect: 15 pending -> 12 ghost entries, no total)"). Repaired by the C5R.1 work (AC-1.2: EVERY pending proposal appears as a ghost) after the wave-8 verdict. |

## Patch notes filed (LIVE_DEFECTs — builds belong to home Parts)

Per the GP-E06 circuit contract, no defect below is built in
Part III. Each is filed here as a patch note to its home Part
under the Eight-Part placement map; the surface is named exactly
so the home lane can pick it up without re-probing:

- **R28** → home: the `form/open.py` growth/forces surface
  (Parts I/II seam per the placement map's open.py split).
  Ask: truthful continuation or a skipped-set receipt on the
  parallel-forces pass; first-N must not permanently monopolize.
- **R29** → home: the Nursery idea-create surface
  (`form/idea_create.py`). Ask: disclose or refuse on cap
  contact (label 80 / detail 2000 / goals 12), never silent cut.
- **R31** → home: the coordinator surface
  (`form/dell_matrix/agent_coordinator.py`). Ask: counted loss
  or explicit archival at the 500 eviction (the family's PP2b /
  AF-4 count-at-the-loss-site pattern).
- **R32 (Studio slice only)** → home: the Studio surface
  (`form/dell_matrix/assets/js/core.js:288`). Ask: draw the
  payload's shown count, or disclose drawn/shown/total on the
  canvas; the payload half needs nothing.
- **R34** → home: the BIMO forge surface
  (`form/dell_matrix/bimo_forge.py`, `form/repl.py` commit
  site). Ask: one persistence circuit covering all
  producer/commit/restore sites; retired committed
  configurations get a receipt and an escape (R30 pattern),
  legacy configs preserved.
- **R37** → home: the dock framing surface
  (`form/dell_matrix/inference_dock.py` `_bimo_framing`). Ask:
  emit the whole valid configuration or refuse wearing it;
  never a partial persona.
- **R38** → home: the bridge surface (`form/llm/bridge.py`
  `ProviderResult.to_dict`). Ask: preserve the text or mark
  incompleteness explicitly (length/total/flag) so no dependent
  action treats cropped as complete.
- **R39** → home: the bridge surface (`form/llm/bridge.py`
  `_claude` / `dispatch`). Ask: propagate truncation/completion
  status (`stop_reason`) into the result meta, and make the
  output bound caller-configurable within safe bounds.

## Counts

15 rows probed: LIVE_DEFECT = R28, R29, R31, R32 (narrowed to
the Studio slice), R34, R37, R38, R39 (**8**); FAITHFUL_GUARD =
R30, R33, R41 (**3**); UNRULED_VALUE = R36 (**1**); DORMANT =
R35, R40 (**2**); ALREADY_FIXED = R42 (**1**). Total
8+3+1+2+1 = **15**. No row is left EVIDENCE_GAP: every wave-era
verdict was either re-verified in current source or superseded
by a named later repair (R42).

*Evidence class: source-verified at c6ee38d9 for all 15 rows;
behaviourally probed at this base for R29 and R38; wave-era
behavioural probes cited (not re-run) for the stateful rows.
This record claims no implementation credit for any row.*
