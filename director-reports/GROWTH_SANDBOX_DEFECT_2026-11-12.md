# GROWTH SANDBOX-INTEGRITY DEFECT — INDEPENDENT REPRODUCTION (2026-11-12)

Circuit: GS-4 grounding follow-up to PR #402 (Growth Selection proposal).
Authority trail: Ace's Growth Selection Doctrine (2026-11-12: "a sandbox
that doesn't affect anything outside of it"); PR #402 grounding finding
(sandbox PARTIAL — enumeration wall-blind, drift crosses); Keeper CONFIRM
(scoped, records) on #402 incl. "sandbox finding confirmed as defect-class";
Director mail 1a1d044ba44a2125 (2026-11-12): CONFIRM (scoped) authorizing
this INVESTIGATION — Uni gate = independently reproduce; if reproduced,
register the defect and propose the smallest GS-4 patch. Non-authorizations
honored throughout: NO default-semantics flip, NO DCC-XI–XV pin break, NO
runtime-repair merge before a Director scope ruling. This PR is records
only; no product code is changed.

## VERDICT: REPRODUCED — both paths, independently

An independent probe (written from the defect description only; different
field, labels, and marker tokens from the grounding probe) was run on
merged main @ 074b30f78cd0867e472e025b1deb1c15ed0c07b3. Contract
assertions failed 3 of 4. Full verbatim log: Appendix A.

## THE CONTRACT vs THE ACTUAL

Contract (Ace, 2026-11-12): a sandbox affects nothing outside it; growth
involving boxed units must not use outside material.

Setup: disposable owner; 5 co-located units — `in_a`, `in_b` boxed into
plane sandbox `vault1` via the canonical `Plane.box(...)` (the SandboxGate
machinery, form/dell_matrix/plane.py:182); `out_a` (near-twin of in_a),
`out_b`, `out_c` outside, carrying outside-only tokens (mechanically
computed set: axolotl, azurite, basalt, fjord, glacier, obsidian,
outdrift, outkeep, outpost, tundra, wolf). The wall itself is real in the
plane's own scope authority: `enhance_scope('in_a') == ['in_b']` and
`enhance_scope('out_a') == ['out_b', 'out_c']` (probe setup output).

Actual, one default `grow_ideas(1)`:

- **Enumeration (PATH A):** `pairs_scanned = 10` — every pair of the
  5-unit field, including all 6 cross-wall pairs. Wall-respecting growth
  would scan 4 (1 inside-inside + 3 outside-outside).
- **Pair crosses (PATH A, material):** 4 of the 6 proposed "new" rings
  are Solstice crosses with parents spanning the wall —
  `['in_a','out_a']`, `['in_b','out_a']`, `['in_a','out_b']`,
  `['in_b','out_b']` — and their words carry the outside markers in the
  Bridge line (e.g. proposal `harbor_lantern_inkeep_harbor_4367`:
  "Bridge: axolotl, azurite, inkeep, outke…"). Only 1 of 6 new proposals
  is purely inside; 1 is purely outside.
- **Single-parent drift (PATH B):** 2 evolved proposals have a boxed
  sole parent and carry outside-only tokens verbatim —
  `harbor_lantern_inkeep_fjord__5069`, parents `['in_a']`, label
  "harbor lantern inkeep → fjord / glacier", words "New threads: fjord,
  glacier, obsidian, outpost, tundra, wolf" (all six from `out_c`); the
  twin for `['in_b']`. A boxed unit's offspring is built from an outside
  unit's tokens while its lineage names only the boxed parent.
- **Control:** the identical field with NO sandbox produced the
  IDENTICAL proposal set (same proposal ids, same parents, same
  counts: 10 pairs, 6 new, 4 evolved). Boxing changed nothing in growth
  output at all — growth is sandbox-blind, not sandbox-aware.
- **Existing door:** the same boxed field grown via
  `grow_ideas(1, scope_ids=['in_a','in_b'])` scanned 1 pair and produced
  1 proposal with zero leaks — containment is achievable today only when
  the caller explicitly selects the inside set; nothing in the default
  path relates the sandbox to growth.

Disclosure on assertion C2: the probe's exemplar-marker assertion
(axolotl/azurite in a boxed drift offspring) PASSED as keyed — those two
markers crossed through the Solstice pair path, not the drift path, in
this field. The general assertion C2b (any outside-only token, computed
mechanically from the field) FAILED on the drift path as recorded above.
Both results are reported; neither is edited.

## MECHANISM — one loop, two manifestations (code refs, main @074b30f)

File: `form/dell_matrix/ringed_growth.py` (RingedGrowth.run).

1. Enumeration: `ids = list(plane.units.keys())` (line 474); the nested
   loop at lines 485–489 scores EVERY unordered pair with `_affinity`
   and appends it. No sandbox membership test exists anywhere in the
   file (zero `sandbox` references in ringed_growth.py).
2. The only sandbox input to growth is soft: `_affinity` reads
   `plane.enhance_scope(a)` (plane.py:224–231 — which DOES respect the
   wall) solely for the `in_scope` term, lines 297–298:
   `in_scope = 1.0 if b in scope else 0.2`, weighted 0.13 in the
   composite (line 304). A cross-wall pair is penalized, never excluded;
   with real token overlap it clears the Solstice (0.28) / Equinox
   (0.16) / Standstill (0.10) gates (lines 42–43, 330–338).
3. Solstice branch (line 538ff; nursery.add line 569): two-parent
   crosses compose label/words from both parents — PATH A offspring.
4. Drift branch (line 584): `primary = a` (line 585);
   `gained = _tokens_uid(plane, b) - _tokens_uid(plane, a)` (line 588);
   the evolved proposal (nursery.add line 600) takes `parents=[primary]`
   while its label (`_evolve_label`, line 347) and words ("New threads:")
   are built from the peer's gained tokens — PATH B offspring.
5. Entry: `Program.grow_ideas` (form/open.py:1268) passes the real plane
   (or a ScopedPlaneView when scope_ids is given) to `growth.run`.

Isolation note: PATH A and PATH B cannot be isolated from each other
through public parameters — they are two branches of the same enumerated
pair loop. `include_superseded` and `cycles` do not touch walls. The only
public lever that changes the outcome is `scope_ids` (consumer-side view,
Run 3), which replaces the plane the loop sees.

## WHY NO EXISTING TEST CAUGHT IT (test refs)

Verified by intersection on this clone: the test files that mention
`sandbox` (form/mandell/core_i_maturity_test.py, d1_registry_leaf3_test.py,
p11_satellites_test.py, projects_groups_test.py,
form/persist_full_roundtrip_test.py, step11_public_contracts_test.py,
track_d_td2_test.py) and the suites exercising growth share NO file —
no suite both boxes a unit and grows. The sandbox contract is tested at
the plane/scope layer (e.g. projects_groups_test.py:23 pins
`Plane.enhance_scope` scoping a member's enhancement to its group-mates;
form/invariants.py:51–65 pins box/unbox state) and growth is tested for
pair behavior on unboxed fields. The growth×sandbox cell of the matrix
was empty. (form/invariants.py:68 also calls grow_ideas — on an unboxed
field.)

## BLAST RADIUS (honest)

- Affected states: any field mixing boxed and unboxed units under
  DEFAULT growth. Callers of default `grow_ideas` include the Dell 6
  Cycle / Dell 13 Loop leaf branches (form/mandell/executor_leaf.py:165,
  :240), form/mandell/core_i_ops.py:426 (full-plane, include_superseded),
  form/accept.py:32, form/dell_matrix/live_host.py:56,
  code_evolution.py:141, and the visual/program evolve loops.
- Unaffected states: fields with no boxed units (the filter proposed
  below excludes nothing there), and all explicitly scoped growth
  (scope_ids / grow_contextual), which never sees cross-wall pairs.
- Who relies on cross-wall pairs today: no caller, test, or document
  found relies on them by design — no suite pins cross-wall growth
  output, and the only sandbox-aware growth-adjacent behavior on record
  (resonance's enhance_scope) respects the wall. The reliance is
  incidental: any user who boxed units for isolation and then grew has
  been receiving cross-wall proposals in the Nursery (PENDING only —
  growth proposes; it does not place), including drift offspring whose
  single-parent lineage conceals the outside contribution.

## PROPOSED SMALLEST GS-4 CONTAINMENT PATCH (design only — NOT built)

Scope: enumeration-level containment inside RingedGrowth.run only.

1. Where: at pair enumeration (ringed_growth.py lines 485–489), skip a
   pair when exactly one of its units is sandboxed, or when both are
   sandboxed into DIFFERENT sandboxes. Pairs inside one sandbox and
   pairs of two unboxed units are untouched. `pairs_scanned` then counts
   only admissible pairs, and the step receipt gains one line:
   `pairs_excluded_cross_sandbox: N` (named, never silent).
2. Effect on the two paths: PATH A crosses and PATH B drift both die at
   the same point, because both consume the enumerated pair list; the
   drift branch's `gained` can then only come from an admissible peer.
   `_affinity` and `enhance_scope` are NOT modified (the soft in_scope
   term stays for admissible pairs, where it is already 1.0/consistent).
3. Excluded vs ineligible: cross-wall pairs are EXCLUDED from
   enumeration (not scored-and-gated), matching how faded units already
   fail closed in `_affinity` and how ScopedPlaneView constrains the
   consumer — the wall becomes a hard eligibility boundary for growth,
   consistent with STORED≠ELIGIBLE discipline.
4. Explicit non-changes: NO default-semantics change (bare growth still
   means the full plane — the doctrine's default flip is GS-3, a
   separate ruled step); NO DCC-XI–XV pin changes (their full-plane
   fields are unboxed, so baseline behavior and `scope_mode="full"`
   assertions are untouched); NO change to scope_ids, SandboxGate,
   Plane.box/enhance_scope, or the Nursery.
5. Failing-first tests the build would pin (this probe, productized):
   boxed field → pairs_scanned excludes cross pairs and the exclusion
   count is receipted; zero cross-parented proposals; zero boxed drift
   offspring carrying outside-only tokens; unboxed-field output
   byte-identical to today; scoped growth unchanged; two different
   sandboxes do not cross into each other.
6. Repair merge awaits a Director scope ruling on this proposal
   (per mail 1a1d044ba44a2125).

## PROPOSED REGISTER TEXT (number left to the authorities)

"DD-NEW — Growth sandbox-integrity defect (CONFIRMED by independent
reproduction, 2026-11-12): default RingedGrowth pair enumeration is
wall-blind — cross-sandbox pairs are scored (soft in_scope penalty only)
and produce (a) two-parent Solstice proposals spanning the wall and
(b) single-parent Equinox/Standstill drift offspring of boxed units
carrying outside units' tokens under inside-only lineage. Boxing changes
nothing in default growth output (control-identical). Containment exists
only via explicit scope_ids selection. Repair proposed as GS-4
(enumeration-level exclusion + receipted exclusion count; no default
change, no DCC pin change) — awaiting Director scope ruling."

## APPENDIX A — VERBATIM PROBE OUTPUT (probe.log, independent probe)

Probe: hidden_files/growth_scope/repro/probe.py (own probe, written from
the defect description; field/labels/markers disjoint from the grounding
probe). Run on the fresh clone of main @074b30f. Exit code 1 (contract
assertions failed = defect present).

```
=== RUN 1: boxed field, default grow_ideas(1) ===
setup: in_a sandboxed=True sandbox_id=vault1
setup: in_b sandboxed=True sandbox_id=vault1
setup: out_a sandboxed=False
setup: out_b sandboxed=False
setup: out_c sandboxed=False
setup: sandbox vault1 members=['in_a', 'in_b']
setup: enhance_scope(in_a)=['in_b']
setup: enhance_scope(out_a)=['out_b', 'out_c']
growth result: ok=True scope_mode=full pairs_scanned=10 proposed_new=6 proposed_evolved=4 gates={'Solstice': 6, 'Equinox': 2, 'Standstill': 2, 'None': 0}
proposals total: 10
  proposal harbor_lantern_inkeep_harbor_1843 kind=new parents=['in_a', 'in_b'] label='harbor lantern inkeep × harbor lantern inforge' markers=[]
    words='[Ring:Evolve] Solstice resonance. Parents: harbor lantern inkeep + harbor lantern inforge. Goals: (parents had none — prefer adding goals on live ideas). Shared: cellar, copper, craft, harbor, kettle. Bridge: inforge, inkeep. Lineage: in_a|'
  proposal harbor_lantern_inkeep_harbor_4367 kind=new parents=['in_a', 'out_a'] label='harbor lantern inkeep × harbor lantern outkeep' markers=['axolotl', 'azurite']
    words='[Ring:Evolve] Solstice resonance. Parents: harbor lantern inkeep + harbor lantern outkeep. Goals: (parents had none — prefer adding goals on live ideas). Shared: cellar, copper, craft, harbor, kettle. Bridge: axolotl, azurite, inkeep, outke'
  proposal harbor_lantern_inforge_harbo_4744 kind=new parents=['in_b', 'out_a'] label='harbor lantern inforge × harbor lantern outkeep' markers=['axolotl', 'azurite']
    words='[Ring:Evolve] Solstice resonance. Parents: harbor lantern inforge + harbor lantern outkeep. Goals: (parents had none — prefer adding goals on live ideas). Shared: cellar, copper, craft, harbor, kettle. Bridge: axolotl, azurite, inforge, out'
  proposal harbor_lantern_outkeep_harbo_9964 kind=new parents=['out_a', 'out_b'] label='harbor lantern outkeep × harbor copper outdrift' markers=['axolotl', 'azurite']
    words='[Ring:Evolve] Solstice resonance. Parents: harbor lantern outkeep + harbor copper outdrift. Goals: (parents had none — prefer adding goals on live ideas). Shared: axolotl, azurite, copper, craft, harbor. Bridge: basalt, cellar, kettle, outd'
  proposal harbor_lantern_inkeep_harbor_9856 kind=new parents=['in_a', 'out_b'] label='harbor lantern inkeep × harbor copper outdrift' markers=['axolotl', 'azurite']
    words='[Ring:Evolve] Solstice resonance. Parents: harbor lantern inkeep + harbor copper outdrift. Goals: (parents had none — prefer adding goals on live ideas). Shared: copper, craft, harbor, lantern, song. Bridge: axolotl, azurite, basalt, cellar'
  proposal harbor_lantern_inforge_harbo_7385 kind=new parents=['in_b', 'out_b'] label='harbor lantern inforge × harbor copper outdrift' markers=['axolotl', 'azurite']
    words='[Ring:Evolve] Solstice resonance. Parents: harbor lantern inforge + harbor copper outdrift. Goals: (parents had none — prefer adding goals on live ideas). Shared: copper, craft, harbor, lantern, song. Bridge: axolotl, azurite, basalt, cella'
  proposal harbor_lantern_outkeep_fjord_6934 kind=evolved parents=['out_a'] label='harbor lantern outkeep → fjord / glacier' markers=[]
    words='[Ring:Evolve] Equinox evolution. From: harbor lantern outkeep. Touch: glacier tundra outpost. Goals: (parents had none — prefer adding goals on live ideas). New threads: fjord, glacier, obsidian, outpost, tundra, wolf. Lineage: out_a.'
  proposal harbor_copper_outdrift_fjord_1075 kind=evolved parents=['out_b'] label='harbor copper outdrift → fjord / glacier' markers=[]
    words='[Ring:Evolve] Equinox evolution. From: harbor copper outdrift. Touch: glacier tundra outpost. Goals: (parents had none — prefer adding goals on live ideas). New threads: fjord, glacier, obsidian, outpost, tundra, wolf. Lineage: out_b.'
  proposal harbor_lantern_inkeep_fjord__5069 kind=evolved parents=['in_a'] label='harbor lantern inkeep → fjord / glacier' markers=[]
    words='[Ring:Evolve] Standstill evolution. From: harbor lantern inkeep. Touch: glacier tundra outpost. Goals: (parents had none — prefer adding goals on live ideas). New threads: fjord, glacier, obsidian, outpost, tundra, wolf. Lineage: in_a.'
  proposal harbor_lantern_inforge_fjord_3935 kind=evolved parents=['in_b'] label='harbor lantern inforge → fjord / glacier' markers=[]
    words='[Ring:Evolve] Standstill evolution. From: harbor lantern inforge. Touch: glacier tundra outpost. Goals: (parents had none — prefer adding goals on live ideas). New threads: fjord, glacier, obsidian, outpost, tundra, wolf. Lineage: in_b.'
outside-only tokens (mechanical): ['axolotl', 'azurite', 'basalt', 'fjord', 'glacier', 'obsidian', 'outdrift', 'outkeep', 'outpost', 'tundra', 'wolf']
[FAIL] C3 enumeration excludes cross-wall pairs :: pairs_scanned=10 (10 = all pairs incl. 6 cross-wall; 4 = wall-respecting)
[FAIL] C1 no proposal parents span the wall :: cross-parented proposals=4 [('harbor_lantern_inkeep_harbor_4367', ['in_a', 'out_a'], 'harbor lantern inkeep × harbor lantern outkeep'), ('harbor_lantern_inforge_harbo_4744', ['in_b', 'out_a'], 'harbor lantern inforge × harbor lantern outkeep'), ('harbor_lantern_inkeep_harbor_9856', ['in_a', 'out_b'], 'harbor lantern inkeep × harbor copper outdrift'), ('harbor_lantern_inforge_harbo_7385', ['in_b', 'out_b'], 'harbor lantern inforge × harbor copper outdrift')]
[PASS] C2 no boxed offspring carries outside markers (exemplar set) :: boxed-parent proposals=7; marker-carrying=[]
[FAIL] C2b no boxed drift offspring carries any outside-only token :: drift offspring carrying outside-only tokens=[('harbor_lantern_inkeep_fjord__5069', ['in_a'], 'harbor lantern inkeep → fjord / glacier', ['fjord', 'glacier', 'obsidian', 'outpost', 'tundra', 'wolf']), ('harbor_lantern_inforge_fjord_3935', ['in_b'], 'harbor lantern inforge → fjord / glacier', ['fjord', 'glacier', 'obsidian', 'outpost', 'tundra', 'wolf'])]

=== RUN 2 (control): same field, NO sandbox, default grow ===
control: pairs_scanned=10 proposed_new=6 proposed_evolved=4 proposals=10
  proposal harbor_lantern_inkeep_harbor_1843 kind=new parents=['in_a', 'in_b'] label='harbor lantern inkeep × harbor lantern inforge' markers=[]
  proposal harbor_lantern_inkeep_harbor_4367 kind=new parents=['in_a', 'out_a'] label='harbor lantern inkeep × harbor lantern outkeep' markers=['axolotl', 'azurite']
  proposal harbor_lantern_inforge_harbo_4744 kind=new parents=['in_b', 'out_a'] label='harbor lantern inforge × harbor lantern outkeep' markers=['axolotl', 'azurite']
  proposal harbor_lantern_outkeep_harbo_9964 kind=new parents=['out_a', 'out_b'] label='harbor lantern outkeep × harbor copper outdrift' markers=['axolotl', 'azurite']
  proposal harbor_lantern_inkeep_harbor_9856 kind=new parents=['in_a', 'out_b'] label='harbor lantern inkeep × harbor copper outdrift' markers=['axolotl', 'azurite']
  proposal harbor_lantern_inforge_harbo_7385 kind=new parents=['in_b', 'out_b'] label='harbor lantern inforge × harbor copper outdrift' markers=['axolotl', 'azurite']
  proposal harbor_lantern_inkeep_fjord__5069 kind=evolved parents=['in_a'] label='harbor lantern inkeep → fjord / glacier' markers=[]
  proposal harbor_lantern_inforge_fjord_3935 kind=evolved parents=['in_b'] label='harbor lantern inforge → fjord / glacier' markers=[]
  proposal harbor_lantern_outkeep_fjord_6934 kind=evolved parents=['out_a'] label='harbor lantern outkeep → fjord / glacier' markers=[]
  proposal harbor_copper_outdrift_fjord_1075 kind=evolved parents=['out_b'] label='harbor copper outdrift → fjord / glacier' markers=[]

=== RUN 3 (existing door): boxed field, grow_ideas(scope_ids=inside) ===
scoped: scope_mode=contextual pairs_scanned=1 proposals=1 leaks=0
  proposal harbor_lantern_inkeep_harbor_1843 kind=new parents=['in_a', 'in_b'] label='harbor lantern inkeep × harbor lantern inforge' markers=[]

=== CONTRACT ASSERTIONS: 1 PASS / 3 FAIL ===
VERDICT: DEFECT REPRODUCED
```

---

## Post-merge disposition (2026-11-12, union refresh onto main c0742ce)

This report stands as the historical defect record; nothing above is rewritten. The defect it documents was repaired and the repair is MERGED via PR #405 (branch uni/gs4-repair-1112, corrected head 41e1556; merge commit c0742cedbdbc9bf7f4f2950815606f572f7625f8), with PR #404 merged as its ancestry. GS-4 campaign at the corrected head TERMINAL GREEN (fwd/twice/rev) and exact-head CI TERMINAL GREEN; merged-main verification passed (gs4 suite 19/19 on merged main). Register placement landed as MWL 184 'GS-4 Growth Sandbox Integrity / cross-wall enumeration' (OPEN / confirmed defect). MWL 184 completion credit is REQUESTED and PENDING authority ruling — NOT granted; row 184 remains OPEN. U1/U2/U3 remain UNPROVEN edges, tracked as follow-up probes.
