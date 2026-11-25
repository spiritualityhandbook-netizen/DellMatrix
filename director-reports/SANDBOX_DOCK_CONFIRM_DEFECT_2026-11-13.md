# SANDBOX DOCK/CONFIRM DEFECT — cross-wall proposals land via the inference dock, and confirm placement is wall-blind for every caller

**Status: SUBMITTED — defects reproduced; NO repair authorized or implemented by this record; no MWL credit claimed.**

## 0. Provenance

- Evidence produced by the overnight U-probe lanes (2026-11-13) against merged main
  `6d5f821be412e3abd3736e748b855f1d99fb7b7b`, closing out the three edges the GS-4
  repair (PR #405/#406/#407, MWL 184) named UNPROVEN: U1 post-growth mutation,
  U2 docked-session synthesis, U3 multi-cycle compounding.
- Probes ran with isolated per-owner state inside a throwaway clone; no probe
  touched the live program state. Probe scripts and logs are preserved outside
  the repo in the goal workspace (`hidden_files/u_probes/`: `u1_probe.py/.log`,
  `u2_probe.py/.log`, `u3_probe.py/.log`, `u_common.py`;
  `manual_confirm/manual_confirm_probe.py/.log`, `manual_confirm/reload_diag.py/.log`).
  This record is self-contained: the decisive facts, counts, and file:line
  citations are embedded inline.
- Shared fixture (same field as `form/gs4_sandbox_test.py`, the PR #403 field):
  `in_a`/`in_b` boxed into sandbox `vault1`; `out_a` (near-twin), `out_b`
  (moderate), `out_c` (distant) unboxed.
- Static counts re-verified by Uni at main `6d5f821`: the string `sandbox`
  occurs **0 times** in `form/dell_matrix/inference_dock.py`, **0 times** in
  `form/dell_matrix/agent_coordinator.py`, and **0 times** in
  `form/dell_matrix/confirm_lineage.py`.

## 1. Headline

The GS-4 wall holds on exactly one path: growth enumeration. Every other way a
proposal can be authored or made live is wall-blind:

| Path | Wall consulted? | Result |
|---|---|---|
| RingedGrowth enumeration (GS-4 repair) | YES — wall-mate filter | cross-wall pairs excluded before scoring; receipted |
| Inference dock DIRECT verbs (synthesize / relate / relate_field) | NO | cross-wall PENDING proposals land (§2) |
| Auto-confirm sweep (`set_auto_confirm_grow(True)`, opt-in) | NO | cross-wall proposal becomes a LIVE unit; boxed-parent offspring placed UNBOXED (§3) |
| Manual confirm (REPL `confirm <id>`) | NO | same placement writer; boxed-parent offspring placed UNBOXED; mixed-parent cross-wall confirm succeeds (§4) |

Leaked artifacts from the dock alone are PENDING-only. Liveness requires a
confirm path — the auto-confirm sweep or a manual confirm — and the confirm
placement writer is the single shared point where all of them go live
wall-blind (§4, convergence).

## 2. Finding 1 — U2 LEAK: dock direct verbs author cross-wall PENDING proposals

**Realism: INTEGRATION** — the repository's own scripted-FakeProvider dock
harness (the pattern of `form/dock_proposal_b_test.py`; no provider credential,
no network). The scripted provider acts as a compliant docked judge returning
schema-valid output whose parents are exactly the targets it was shown — the
maximal acceptance a real model's output could receive. The landing path is
provider-agnostic: whatever it accepts here, it accepts from any docked
provider, because no wall check exists anywhere on it.

Mechanism:

- Neither the dock nor the coordinator mentions walls: `sandbox` occurs
  0 times in `form/dell_matrix/inference_dock.py` and 0 times in
  `form/dell_matrix/agent_coordinator.py` (verified at `6d5f821`).
- The field snapshot shown to the docked AI carries no wall fields. Probe log:
  `snapshot unit entry keys: ['detail', 'goals', 'label', 'uid', 'words', 'x', 'y']`
  and `snapshot carries any wall field: False`. A docked AI cannot see walls,
  and the host does not enforce them on landing.
- Landing validation checks only parents-subset conditions (the judge's
  parents must be a subset of the shown targets) — never wall membership.

Reproduced (decisive log lines, `u2_probe.log`):

- `U2a synthesize([in_a, out_a])` → `LANDED pid=docked_cross_7748 status=pending parents=['in_a', 'out_a']` — cross-wall (vault1 × unboxed).
- `U2b relate(in_a, out_c)` → `LANDED pid=docked_cross_7748_1 status=pending parents=['in_a', 'out_c']` — cross-wall.
- `U2c relate_field(in_a)` → pre-filter candidates wall-blind:
  `candidates shown to judge (target first): ['in_a', 'in_b', 'out_a', 'out_b']`,
  `outside-wall candidates shown: ['out_a', 'out_b']` →
  `LANDED pid=docked_cross_7748_2 status=pending parents=['in_a', 'in_b', 'out_a', 'out_b']`.
- Final nursery census: 3 of 7 proposals `SPANS_WALL=True`, all three from the
  direct verbs, all `status=pending`, origin `dock:agent-a:fake:fake:valid`.

**CONTROL — the growth path is SAFE.** The same probe's growth leg
(`grow_ideas(session=...)`) shows RingedGrowth handing only wall-mate pairs to
`session.synthesize`: `docked_pairs` are exactly `(in_a, in_b)` and
`(out_a, out_b)`; `docked cross-wall pairs: []`;
`pairs_excluded_cross_sandbox=6`. The GS-4 filter works where it lives; the
dock's direct verbs simply never pass through it.

## 3. Finding 2 — U1c LEAK: the opt-in auto-confirm sweep confirms everything, wall-blind

`Program.set_auto_confirm_grow(True)` is a public setter (default `False`).
With it on, the post-growth sweep confirms **all** pending proposals with no
wall check. Probe log (`u1_probe.log`), over a field where a cross-wall
proposal `seeded_cross_wall_cross_511` (parents `['in_a', 'out_a']`) was
seeded pending:

- `auto_confirm receipt: {'on': True, 'confirmed': 5, 'failed': 0, ...}`
- `seeded proposal after grow: status=confirmed`;
  `seeded proposal confirmed_into_unit: True` — the cross-wall proposal became
  a **LIVE** plane unit: `parents=['in_a', 'out_a'], sandboxed=False, sandbox_id=None`.
- Second manifestation in the same sweep: the offspring of the two vault1-boxed
  parents landed **UNBOXED** — `NEW UNIT harbor_lantern_inkeep_harbor_1843:
  parents=['in_a', 'in_b'] sandboxed=False sandbox_id=None`.

The sweep is not a separate writer: it calls `Program.confirm_proposal`
itself (`form/open.py:1342`, `_producer='grow_auto'`), so this is the §4
placement defect reached automatically.

## 4. Finding 3 — manual-confirm blast radius: placement is wall-blind by construction for EVERY caller

**Realism: PUBLIC_ENTRY_PATH** — the probe invokes the exact call the REPL
confirm verb makes (`form/repl.py:2852-2856`:
`p.confirm_proposal(pid, _producer="repl_user",
_review_context=p.make_review_context(pid, "repl_user"))`).

Three cases, one seeded pending proposal each, confirm via that call
(`manual_confirm_probe.log`; placement re-verified after `Program.load`
reload — see `reload_diag.log` — so the result is persisted state, not an
in-memory artifact):

- **Case A — both parents boxed** (`parents=['in_a', 'in_b']`, both vault1):
  `confirm_proposal return: {"ok": true, ...}`; placed unit
  `{'sandboxed': False, 'sandbox_id': None, 'parents': ['in_a', 'in_b'], 'origin': 'confirmed'}`;
  `sandboxes AFTER (reloaded): {'vault1': ['in_a', 'in_b']}` — the offspring of
  two boxed parents is placed **outside the box** and is NOT added to the
  box's membership.
- **Case B — mixed parents, cross-wall** (`parents=['in_a', 'out_a']`):
  confirm **SUCCEEDS** — no wall check anywhere; placed unboxed with
  cross-wall parents.
- **Case C — both parents outside (control)** (`parents=['out_a', 'out_b']`):
  placed unboxed, as expected. The control isolates the defect: placement
  behaves identically in all three cases — it never looks at the parents'
  walls at all.

**Convergence — one shared writer.** `Program.confirm_proposal`
(`form/open.py:1670`) delegates (`form/open.py:1748/1764`) to
`confirm_lineage.confirm_proposal` (`form/dell_matrix/confirm_lineage.py:109`),
whose placement step (`confirm_lineage.py:233-236`) calls
`program.place(...)` with **no sandbox arguments**. `sandbox` occurs 0 times
in `confirm_lineage.py`. The auto-confirm sweep (§3) reaches the same writer
via `form/open.py:1342`. Every confirm caller — REPL user, grow_auto sweep,
any programmatic caller — inherits the same wall-blind placement. There is
exactly one place a placement rule would have to live, and today it has none.

## 5. Boundaries that HOLD (scope limits of this record)

- **U1 default path HOLDS (PUBLIC_ENTRY_PATH).** With auto-confirm off (the
  default), the post-run `duo.evolve` / nature-forces stage never writes back
  to plane units: full-field diff EMPTY over 4 cycles (`UNIT DIFF after
  grow_ideas(1): EMPTY`, `UNIT DIFF after +3 cycles (vs original): EMPTY`;
  sandbox records equal throughout; proposals accumulated 4 → 16 with
  `cross_wall=[] drift=[]`). Probe verdict: `U1 CORE (default path) VERDICT:
  HOLDS`.
- **U3 HOLDS (PUBLIC_ENTRY_PATH).** The GS-4 filter composes across 5 growth
  cycles with save/reload between cycles: every cycle
  `pairs_scanned=4 excluded=6`, `cross_wall=0 drift=0`, no unit added/removed,
  walls and sandbox membership unchanged after each reload; proposals 4 → 20,
  all wall-clean. Probe verdict: `U3 VERDICT: HOLDS`. **Honest limit:**
  compounding *through confirmed offspring* was exercised only via U1c (§3),
  not via U3 — U3 never confirmed anything.
- **Dock leaks are PENDING-only.** Nothing in §2 is live until a confirm path
  (§3 or §4) acts on it. The dock defect is an authoring/landing defect; the
  confirm defect is what makes it (and any other cross-wall pending, however
  authored) live and misplaced.
- Nothing here re-opens GS-4's repaired scope: growth enumeration remains
  wall-safe, and the U1/U3 scoped credits under MWL 184 stand as bounded.
  This record covers two surfaces GS-4 never claimed: dock landing and
  confirm placement.

## 6. Failing-first sketches for a future repair suite (in words — no suite is implemented by this record)

1. **Dock landing refusal case.** Dock a scripted session; call
   `synthesize` on a cross-wall parent pair. Assert: no proposal lands; the
   receipt is a named refusal (fail-closed, GS-4 style) and the nursery count
   is unchanged. Control: a wall-mate pair still lands PENDING.
2. **Boxed-parent placement inheritance case.** Seed a pending proposal whose
   parents are both in the same box; confirm through the REPL-identical call.
   Assert: the offspring is placed IN that box (`sandboxed=True`,
   `sandbox_id` = the parents' box) and appears in the box's `member_ids`
   after reload.
3. **Mixed-parent case.** Seed a pending proposal with one boxed and one
   unboxed parent; confirm. Assert the behavior the Director rules under
   Q-U.4 (refusal, or unboxed placement carrying a warning receipt) — the
   assertion is written to the ruling, not before it.
4. **Sweep case.** Enable `set_auto_confirm_grow(True)` with a seeded
   cross-wall pending proposal present; run growth. Assert the sweep does
   not make the cross-wall proposal live (per the Q-U.5 ruling: refused at
   confirm under the placement rule, or skipped with a receipt naming it),
   while wall-clean pendings still confirm.

## 7. Questions for the Director

- **Q-U.1** — Acceptance + register placement: are the three findings accepted
  as reproduced, and where do they register — a new DD row, a GS-5 item, or
  facets of the existing sandbox register line?
- **Q-U.2** — Dock repair scope: should landing validation refuse cross-wall
  parent sets at the dock (GS-4 fail-closed precedent, receipted refusal)?
  And should the field snapshot carry wall fields so a docked AI can SEE
  walls and reason about them, rather than only being refused after the fact?
- **Q-U.3** — Confirm placement rule: offspring of same-wall parents inherits
  that wall — including box `member_ids` bookkeeping on placement — confirm
  as the repair contract?
- **Q-U.4** — Mixed-parentage confirm: refuse / land unboxed with a warning
  receipt / caller's choice? Note: this touches Ace's manual-confirm
  sovereignty — a refusal rule would let the program override an explicit
  human confirm. Flagged **ACE-RELEVANT**; the Director may route it to Ace.
- **Q-U.5** — Auto-confirm sweep: should it inherit the confirm placement
  rule only, or additionally skip-and-receipt cross-wall pendings so the
  sweep's receipt names what it did not confirm?

## 8. Status

SUBMITTED — defects reproduced (U2 INTEGRATION; U1c opt-in sweep;
manual-confirm PUBLIC_ENTRY_PATH; U1-default and U3 boundaries verified
HOLDING at PUBLIC_ENTRY_PATH). NO repair authorized or implemented by this
record. No MWL credit claimed. U1/U3 scoped credits from GS-4 (MWL 184)
unaffected as bounded.
