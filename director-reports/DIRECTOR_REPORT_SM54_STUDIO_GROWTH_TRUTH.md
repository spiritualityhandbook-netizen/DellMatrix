# DIRECTOR REPORT — SM-54 Studio Growth Truthfulness

Circuit: DIR-SUS-WAKE-2026-11-04 Priority 1 · Mode: implementation under
Director directive · Base: `58ad041` (main after PR #261 integration)

## Defect (verified before repair)

`gui/server.py _growth_payload` fabricated the Growth node inventory
from the growth force's plant list: one invented node per plant
(`{"id": unit_id or "plant-%d", "label": idea_full or idea,
"score": 0.0}`). It never called `Program.nodes_payload()`.
Consequences, both directions dishonest:

- a Plane idea that was never planted could NEVER appear in the
  Studio Growth view — the view silently read as "these are all the
  ideas there are";
- a plant with no Plane unit (e.g. planted by label from the REPL)
  appeared in the Studio as a node that does not exist in the Plane.

## Repair (minimal, consumer-only; no new subsystem)

`_growth_payload` now serves the canonical projection —
`Program.nodes_payload()` (the same projection first_person,
live_visual, matrices_hub and sacred_geometry consume) — through the
certified `filter_nodes_for_room("growth", ...)` lens, preserving
unit id, label, score and the lens's epistemic `stage` /
`stage_source`. One addition, `_growth_available()`, mirrors
`_plants()`' own resolution chain: when the growth force cannot be
read at all, the lens receives `plants=None` and stamps
`stage_source="unavailable"`; a readable force with no matching
plant stamps `"unplanted"`; zero plane units yields an empty node
list (genuinely empty). The payload shape `{nodes, plant_count}` is
unchanged. Legacy label-keyed plants attribute exactly as before via
the lens's DIR-T2-R2 rules; SM-39 uid-keyed plants attribute by unit
id. `view_rooms.py` was NOT modified.

## Evidence

- **Failing-first:** the rewritten `form/gui_api_test.py` growth
  block aborts on pristine code at "growth nodes are exactly the
  canonical plane units" (the check helper raises on first failure).
- **Targeted:** GUI-API **33/33 GREEN** after the repair (was 26
  checks; +9 growth-truthfulness checks, −1 replaced, +3 unit-level
  three-state checks net as counted by the suite). Studio security
  suite unaffected: 36/36.
- **Mutant:** removing the availability distinction (always passing
  the plant list) kills exactly the "unavailable, not unplanted"
  check; restored.
- **Amended check, disclosed:** the pre-existing assertion
  "/api/growth is honestly empty for a plantless owner"
  (`nodes == []`) encoded the fabricated behavior — a plantless
  owner still has plane units. It is replaced, under this directive,
  by "plantless owner's units appear unplanted, not hidden", with
  the amendment explained in the test source.
- **Regression:** full `form.regress` ×3 sequential at the code
  head — forward GREEN 230/230, `--twice` GREEN, `--order rev`
  GREEN 230/230. (The first rev leg was killed at 191/230 by a VM
  replacement — uptime evidence — and re-run in full; the partial
  log is preserved and labeled NO RESULT.)
- **Browser:** `gui/browser_acceptance.py` +2 checks (29 → 31): an
  unplanted unit created through the real UI is carded by the Growth
  view, and its card's stage text is exactly "stage: —" (no stage
  claim). Genuine-Chromium proof is the PR's browser-acceptance CI
  run at the frozen head (see PR).
- **API proof:** the gui_api_test growth block runs over real HTTP
  against the real server and the real Program (integration level).

## Remaining exceptions / boundaries

- No human browser session; automated Chromium (CDP) only, per the
  standing ruling.
- `nodes_payload()` is the canonical projection; any field it does
  not carry (e.g. a unit's lifecycle status — Plane units have none)
  is not invented here. "Available epistemic status" = the lens's
  stage/stage_source, preserved verbatim.
- Studio Gap 3 is CLOSED by this circuit (the TD-3 prerequisite is
  satisfied).

## Questions for the Director

1. None blocking. TD-3's Studio leg is unblocked on this repair;
   TD-1 (separately authorized) does not depend on it.
