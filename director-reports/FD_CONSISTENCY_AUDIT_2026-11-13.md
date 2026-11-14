# BOUNDARY F-d CONSISTENCY AUDIT — unit sandbox state consumers

**Status: SUBMITTED — awaiting the Director's findings acceptance and a
bounded repair-scope ruling. No repair is authorized or implemented by
this record. Records only: no code, no test, no register change.**

## Provenance

Read-only audit executed overnight 2026-11-13 against main at
**6d5f821be412e3abd3736e748b855f1d99fb7b7b** (PR #408 merge commit), in a
fresh clone (origin https://github.com/spiritualityhandbook-netizen/DellMatrix).
No code changed by the audit; nothing in the audit clone was committed or
pushed. This report publishes the audit's findings unchanged.

The audit was commissioned by the Director's GS-4 ruling: Boundary F-d
(`sandboxed=False` with a stale `sandbox_id` = UNBOXED) was documented
during the GS-4 circuit for a separate consistency audit. The audit asked
whether every consumer of unit sandbox state agrees with the canonical
rule — both of its cases.

## Canonical rule under audit (Director F-d ruling, GS-4)

The wall key is the pair `(sandboxed, sandbox_id)`:

- `sandboxed=False` + stale non-empty `sandbox_id` → **UNBOXED** (the id is
  inert; the unit is a wall-mate of genuinely unboxed units).
- `sandboxed=True` + missing/invalid `sandbox_id` (None, empty, non-string)
  → **MALFORMED**, fail-closed: refused, never silently collapsed to unboxed.

Canonical definers: `form/mandell/unit_containment.py` —
`_isolation_key` (lines 99–103: `(sandboxed, sandbox_id if sandboxed else
None)`, so a stale id on a flag-False unit keys exactly as unboxed) and
`_malformed_sandbox` (lines 106–117), enforced by `_check_sandbox`
(lines 120–144, raises `ContainmentRefused` before any binding).

## Method

Grep sweep over `form/**/*.py` (non-test) for `.sandboxed`,
`.sandbox_id`, `sandboxes`, `_malformed_sandbox`, `box(`/`unbox(`/
`enhance_scope(`, plus a full-file `sandbox` mention sweep to catch indirect
readers; every hit read in context. Three states were additionally
probe-verified at runtime in the audit clone (in-memory Planes only):
the F-d stale state, the malformed state `(True, None)`, and the
membership-inconsistent state `(True, valid id, record exists, unit not in
member_ids)`.

## Consumer table

| # | Consumer | Location | Rule it implements | Verdict |
|---|----------|----------|--------------------|---------|
| 1 | Containment gate `_malformed_sandbox` / `_isolation_key` / `_check_sandbox` | form/mandell/unit_containment.py:99–144 | The canonical rule itself: pair key; flag-False ignores the id; flag-True + invalid id refused before any binding | CONSISTENT (definer) |
| 2 | Growth pair filter `_wall_key` / `_malformed_boxed` + pair enumeration | form/dell_matrix/ringed_growth.py:95–150, 579–584 | Pair admitted iff wall keys equal; malformed refused BEFORE the equality test (receipts `malformed_box_units_refused`, `pairs_excluded_malformed_box`). Agrees with canonical on both F-d pair cases (probe: stale → not malformed, key None; `(True,None)` → malformed). EXTENDS canonical: also refuses when the id names no Sandbox record or the record's `member_ids` omits the unit — a state containment's definition does not cover (probe: containment `_malformed_sandbox`=False, growth `_malformed_boxed`=True) | CONSISTENT (documented fail-closed extension; cross-authority divergence on the membership state noted below) |
| 3 | `Plane.box` / `Plane.unbox` (maintainer) | form/dell_matrix/plane.py:182–207 | Sets/clears BOTH fields and the Sandbox record's `member_ids` together; no state reachable through this API violates the pair rule | CONSISTENT |
| 4 | `Plane.enhance_scope` | form/dell_matrix/plane.py:223–230 | Boxed branch requires `u.sandboxed and u.sandbox_id`; EVERYTHING else falls into the unboxed branch. Probe at `(True, None)`: `enhance_scope(bad) = ['free1','free2']` — the malformed unit receives a full unboxed scope while `_malformed_sandbox(bad)` is True. Asymmetric: as a PEER the same unit is excluded from others' unboxed scopes (peer filter `not o.sandboxed`, probe: `enhance_scope(free1) = ['free2']`). F-d stale case correct (probe: unboxed scope) | **INCONSISTENT** — brief case (b): `sandboxed=True` + missing id silently treated as unboxed |
| 5 | Resonance (peer scoring + mutual-scope gate) | form/dell_matrix/resonance.py:134, 197 | Reads no sandbox fields directly; consumes `enhance_scope` for peer spread and for the "not in mutual enhance scope" refusal | **INCONSISTENT by inheritance** from #4: a malformed unit spreads/receives resonance as an unboxed unit |
| 6 | Growth affinity `in_scope` term | form/dell_matrix/ringed_growth.py:352 (also :281) | Scoring-only term over `enhance_scope(a)`; pair ADMISSION is decided earlier by #2's wall keys, and malformed units are refused before scoring, so no safety conclusion inherits #4's divergence for admitted pairs | CONSISTENT (noted inheritance, no live effect) |
| 7 | Graph view builder `build_view` | form/dell_matrix/graph_view.py:97, 125–134 | `connected = not u.sandboxed` (flag only — matches F-d: flag-False + stale id → connected); sandbox edge requires `u.sandboxed and u.sandbox_id` (pair); enhance edges via #4. A `(True,None)` unit renders flag "box", not connected, no sandbox edge — fail-closed direction, no refusal (view layer draws no safety conclusion) | CONSISTENT (noted) |
| 8 | `Plane.render` zoomed state line | form/dell_matrix/plane.py:270 | `'SANDBOX '+u.sandbox_id if u.sandboxed else 'CONNECTED'` — flag only, concatenates the id unchecked. Probe: zoomed render of a `(True, None)` unit raises `TypeError: can only concatenate str (not "NoneType") to str`. F-d stale case renders CONNECTED correctly | **INCONSISTENT** — malformed state crashes the display path instead of an honest line/refusal |
| 9 | `Unit.display` | form/dell_matrix/plane.py:69 | `[box:{sandbox_id}]` if flag else `[connected]` — F-d case correct; `(True,None)` renders the misleading literal `[box:None]` (no crash) | CONSISTENT (noted display inaccuracy on malformed state) |
| 10 | REPL group add/remove (`_handle_group_command`) | form/repl.py:1434, 1437, 1445 | Membership decided by `unit.sandbox_id == sb.id` ALONE (add, :1434) and `unit.sandbox_id != sb.id` (remove, :1445); only the "in another group" check (:1437) reads the pair. On the F-d state (flag-False + stale id equal to an existing group's id, unit NOT in that group's `member_ids`): add refuses with "already in group" — the unit is canonically unboxed and not a member. Remove on the same state proceeds to `plane.unbox` (harmless, state-converging, but the "was in group" premise is false) | **INCONSISTENT** — brief case (a): `sandbox_id` presence/equality alone treated as boxed/member |
| 11 | SandboxGate `apply_off` (+ `Program.sandbox_on/off` wrappers) | form/dell_matrix/sandbox_gate.py:60–69; form/open.py:1953–1963 | Unboxes every unit whose FLAG is set (`plane.unbox` clears both fields + membership). A flag-False unit's stale id is never cleared by an "unbox everything" pass — the stale id survives `apply_off` | CONSISTENT (noted hygiene gap; no wall conclusion drawn) |
| 12 | Program restore (unit flags + Sandbox records) | form/persist_rest.py:506–507, 512–519 | Restores `sandboxed`/`sandbox_id` VERBATIM, unvalidated; then rebuilds Sandbox records via `plane.box(members, sid)`, which re-boxes listed members (converging those) but cannot converge a unit claiming a box with no record or no membership — such claims survive restore exactly as saved | PRODUCER / NEUTRAL — draws no conclusion; it is the named source of every divergent state (matches `_malformed_boxed`'s own docstring) |
| 13 | BlankCube pack restore `from_pack` | form/dell_matrix/blank_cube.py:63–67 | Identical pattern to #12: verbatim flag restore (:63–64), records rebuilt via `plane.box` (:67) | PRODUCER / NEUTRAL (same note as #12) |
| 14 | Save serializer | form/persist.py:232–233, 245–247 | Copies the pair + records verbatim; no conclusion | CONSISTENT |
| 15 | BlankCube `export` serializer | form/dell_matrix/blank_cube.py:40–41 | Verbatim pair + records; no conclusion | CONSISTENT |
| 16 | Program status serializers (×2) | form/open.py:547, 639 | Emit `bool(u.sandboxed)` only, as display payload; no id, no wall conclusion | CONSISTENT |
| 17 | Visual node payload `_nodes_payload` | form/dell_matrix/visual.py:365 | Verbatim flag into the view payload (consumed by #7/#18); no conclusion of its own | CONSISTENT |
| 18 | Voynich ring assignment `voynich_ring_for_unit` | form/dell_matrix/sacred_geometry.py:281 | Reads the dict flag only to assign a structural metaphor ring; no wall/isolation conclusion | CONSISTENT (noted: metaphor only) |
| 19 | Main-field snapshots | form/dell_matrix/main_field.py:111–112, 136–137 | Flag is one field of an equality snapshot tuple; no wall conclusion | CONSISTENT |
| 20 | `give_blank` empty-plane path | form/give_blank.py:33 | Clears units and Sandbox records wholesale together; no per-unit conclusion | CONSISTENT |

Out of scope after inspection (mention-only, no unit sandbox state read):
`matrices_hub.py:59` (edge-kind label), `matrix_body.py:53` /
`organ_atlas.py:160` (trading-package comments), `organ_atlas.py:40–42`
(module atlas metadata), `dell_cards.py:557–560`, `registry.py:38`,
`english_brain.py:181–182`, `phrases.py:49–50`, `polyglot.py:58–59,102–103`,
`translate.py:46–47` (Dell 23/24 Lock/Unlock command vocabulary routing to
`Program.sandbox_on/off`, audited at #11), `executor_leaf.py:363–366`
(same routing), `visual.py:212–213` (edge-kind styling),
`checkpoint_generation.py:40` (doc comment).

## Counts

- Consumers enumerated: **20**
- CONSISTENT: **14** (#1, 2, 3, 6, 7, 9, 11, 14, 15, 16, 17, 18, 19, 20 —
  several with noted limitations that draw no wrong wall conclusion)
- INCONSISTENT: **4** (#4 `enhance_scope`, #5 resonance by inheritance,
  #8 `Plane.render`, #10 REPL group membership)
- PRODUCER / NEUTRAL: **2** (#12, #13 restore paths)

## Bottom line

**NOT all consumers agree with the canonical rule — but the F-d case itself
is unanimous.** Every consumer probed or read treats
`sandboxed=False` + stale `sandbox_id` as UNBOXED, exactly as ruled
(containment key, growth wall key, `enhance_scope`, render, display,
graph view). No consumer resurrects a stale id into a wall.

The divergences concentrate on the OTHER canonical case — the malformed
claim `sandboxed=True` + missing/invalid id, which the restore paths
(#12/#13) can produce verbatim from a hand-edited or partially-written
save:

1. **`Plane.enhance_scope` (plane.py:227) silently unboxes it** (probe:
   scope = all non-sandboxed units), contradicting the fail-closed refusal
   in containment (unit_containment.py:121) and growth
   (ringed_growth.py:584). It is also self-asymmetric: the same unit is
   excluded as a peer from others' scopes. Resonance inherits the
   divergence (#5). Growth's pair admission does NOT inherit it (walled
   first, #2/#6).
2. **`Plane.render` (plane.py:270) crashes** with `TypeError` on the same
   state when the unit is zoomed (probe-verified).
3. **REPL group membership (repl.py:1434/1445) reads `sandbox_id` alone** —
   the one consumer that also misfires on the F-d stale state itself:
   flag-False + stale id equal to a group's id is told "already in group"
   although it is canonically unboxed and absent from `member_ids`.

Secondary note (not an F-d violation): on the membership-inconsistent
state (`True`, valid id, record exists, unit not in `member_ids`),
containment and growth disagree — containment's `_malformed_sandbox`
covers only id validity, so its isolation keys would let the unit bind to
a genuine member of the same box; growth refuses it as malformed.
Growth's extension is documented as deliberate (Director correction,
mail 1a1d0990c34b0d99); the asymmetry between the two authorities is
recorded here for the Director, not resolved by this audit.

## Proposed failing-first sketches (NOT implemented — audit is read-only)

- **Sketch 1 (enhance_scope):** place units B, C unboxed; place unit A and
  set `A.sandboxed=True, A.sandbox_id=None` exactly as verbatim restore
  would leave it. Assert `enhance_scope(A)` must not equal the unboxed
  scope `[B, C]` while `_malformed_sandbox(A)` is True. Currently returns
  `[B, C]` → red.
- **Sketch 2 (render):** same malformed unit A; `plane.zoom_in(A)`;
  assert `plane.render()` returns a string. Currently raises `TypeError`
  → red.
- **Sketch 3 (REPL group):** create group G via the box authority; place
  unit U unboxed, then set `U.sandboxed=False, U.sandbox_id=G.id` with U
  absent from G's `member_ids` (the F-d state, restore-reachable). Run
  `group add U to G`. Expected under the canonical rule: U is unboxed, so
  the add proceeds and boxes it. Currently refuses "already in group" →
  red.

## Questions for the Director

- **Q-FD.1 (acceptance):** Do you accept the audit's findings as stated —
  the F-d case unanimous; three inconsistencies (#4 `Plane.enhance_scope`
  with #5 resonance by inheritance, #8 `Plane.render`, #10 REPL group
  membership), all around the malformed claim except #10, which also
  misfires on the F-d stale state itself?
- **Q-FD.2 (bounded repair scope):** Which of the three inconsistencies
  are in scope for a repair circuit — all three, or a named subset? Is
  the resonance inheritance (#5) discharged by repairing its source
  (#4), or does it need its own pinned check?
- **Q-FD.3 (repair rule):** Should the repair follow the GS-4 fail-closed
  precedent — refuse the malformed claim at the consumer (as containment
  and growth already do) — or another stated rule (e.g. an honest
  non-wall display line for the render path instead of a refusal)?

No repair is requested to start before these rulings. No MWL credit is
claimed by this record.
