# GS-4 SANDBOX CONTRACT PREP — defect registration, failing-first suite, enumeration-sufficiency analysis, selection-contract proposal (2026-11-12)

Circuit: GS-4 prep, follow-up to PR #402 (Growth Selection proposal)
and PR #403 (independent reproduction).
Authority trail: Ace's Growth Selection Doctrine (2026-11-12: "a
sandbox that doesn't effect anything outside of it"); PR #402
grounding finding (sandbox PARTIAL — enumeration wall-blind, drift
crosses); Keeper CONFIRM (scoped, records) on #402 incl. "sandbox
finding confirmed as defect-class"; Director mail 1a1d044ba44a2125
(2026-11-12): CONFIRM (scoped) authorizing the INVESTIGATION with
the Uni gate; Director mail 1a1d05d91f6401dc (2026-11-12 09:25 CST):
scoped evidence ACCEPTED as a reproduced sandbox-integrity defect
(pending Keeper independent challenge); **GS-4 IMPLEMENTATION HOLD**
— no patch certification, no unboxed-default flip, no code merge.
This PR executes the five directives in that mail: register the
defect with provenance + GS-4 boundary; publish the minimal
failing-first suite; analyze whether enumeration-level filtering
suffices for both manifestations; propose the exact
authority-preserving selection contract; keep #403 records-only.
**No implementation is in this PR.** The only code-shaped artifacts
are the failing-first test suite (`form/gs4_sandbox_test.py`) and
its registration in `form/regress.py` — the house pattern for
failing-first evidence (same as the DD gates). No product code is
changed; no default semantics move; no DCC-XI–XV pin is touched.
PR #402's Q-GS.1–Q-GS.11 rulings remain the Director's and are not
decided by anything here.

## 1. THE DEFECT (registered statement)

Under DEFAULT growth (`Program.grow_ideas` with `scope_ids=None`),
RingedGrowth pair enumeration is wall-blind: it enumerates every
unordered pair of live plane units (ringed_growth.py:474, 485–489)
and scores each with `_affinity`, where the sandbox wall enters
only as the soft `in_scope` term (1.0 vs 0.2, weight 0.13,
lines 297–298, 304) reading `Plane.enhance_scope` (plane.py:223–231,
which itself respects the wall). A cross-wall pair is penalized,
never excluded. Two manifestations, both reproduced:

- **(a) Cross-wall two-parent proposals.** Enumerated cross-wall
  pairs that clear the Solstice gate produce two-parent proposals
  whose parents span the wall, composing label/words from both
  parents (Solstice branch, ringed_growth.py:538ff; nursery.add
  :569). PR #403 field: 4 cross-parented proposals of 6 new rings
  (parents `['in_a','out_a']`, `['in_b','out_a']`, `['in_a','out_b']`,
  `['in_b','out_b']`), carrying outside markers in the Bridge line.
- **(b) Outside-token single-parent drift.** Enumerated cross-wall
  pairs that land in the Equinox/Standstill band produce an evolved
  proposal with `parents=[primary]` (the boxed unit) whose label
  and "New threads:" words are built from the OUTSIDE peer's tokens:
  `gained = _tokens_uid(plane, b) - _tokens_uid(plane, a)`
  (lines 584–600; `_evolve_label` :347). PR #403 field: 2 boxed
  drift offspring carrying all six outside-only tokens of `out_c`
  (fjord, glacier, obsidian, outpost, tundra, wolf) under
  inside-only lineage.

Boxing changes nothing in default growth output: the identical
unboxed field produced the identical proposal set (same ids,
parents, counts) in both reproductions' controls.

Containment exists today only through explicit selection: the
`scope_ids` door (consumer-boundary validation, open.py:1268ff;
ScopedPlaneView) never presents cross-wall pairs to the loop, and
the contextual nurture path does not route through `grow_ideas`
at all. Nothing in the default path relates the sandbox to growth.

## 2. EVIDENCE PROVENANCE (complete)

| # | Source | What it establishes |
|---|---|---|
| E1 | PR #402 grounding (hidden_files/growth_scope/GROUNDING.md; probe_scope.py/.log) | First observation: 6-unit field, 15 pairs scanned with 2/6 boxed; boxed unit's evolved proposal (`→ cooking / heat`) built from an outside unit's tokens; per-selector classification of the growth surface. |
| E2 | PR #402 comment 6827580827 (hourly execution cycle, 2026-11-12) | The cycle's claim of independent reproduction on merged main: enumeration wall-blind (pairs_scanned=15), single-parent drift crossed; pair-proposal cross-wall NOT materialized in that fixture (penalty-suppressed). |
| E3 | Hourly-cycle probe (hidden_files/gs402_logs/gs402_probe.py + gs402_repro_output.txt) | Read first-hand for this prep: boxed-default run — cross-wall PAIR proposals absent from output, BUT two boxed single-parent drift offspring crossed (`Plant Water → flow / outside`, `Plant Soil → flow / outside`, "New threads: flow, outside, rain, river, stream, three" from outside unit o3 Water Flow, parents `['a1']` / `['a2']`); controls lawful (scoped subset, missing-ID ValueError, empty scope 0 proposals no fallback). Corroborates manifestation (b) and the controls; does not itself show (a) materializing. |
| E4 | PR #403 (branch uni/growth-sandbox-defect-1112 @6202c5a, records only) — director-reports/GROWTH_SANDBOX_DEFECT_2026-11-12.md incl. Appendix A verbatim probe log | Independent probe, disjoint field/labels/markers, run on merged main @074b30f78cd0867e472e025b1deb1c15ed0c07b3: pairs_scanned=10 (all pairs incl. 6 cross-wall); 4 cross-parented Solstice proposals; 2 boxed drift offspring carrying outside-only tokens; unboxed control proposal-set IDENTICAL; scope_ids run scanned 1 pair, 0 leaks. Establishes BOTH manifestations materializing. |
| E5 | PR #403 comment 6827617954 (corroboration cross-link) | Records the fixture difference between E3 and E4 plainly: pair-proposal suppression in one fixture is luck (soft penalty), not containment; both agree on the mechanism. |
| E6 | Director mail 1a1d044ba44a2125 (2026-11-12) | CONFIRM (scoped, investigation/plan only): cross-wall single-parent drift treated as a potential sandbox-integrity defect; Uni gate = independent reproduction; if reproduced, register + propose smallest GS-4 patch; no default flip, no DCC pin break, no runtime-repair merge before a scope ruling. Q-GS.1–.11 remain open. |
| E7 | Director mail 1a1d05d91f6401dc (2026-11-12 09:25 CST) | Scoped evidence ACCEPTED as reproduced sandbox-integrity defect (pending Keeper independent challenge); GS-4 IMPLEMENTATION HOLD; the five directives this PR executes. |
| E8 | This PR's failing-first suite run (form/gs4_sandbox_test.py on main @074b30f, this clone, 2026-11-12) | 6/10 PASS / 4 FAIL, failures quoted verbatim in §3; reproduces E4's exact proposal ids/parents/token sets in a third run of the contract field. |

Keeper status: CONFIRM (scoped, records) on #402 incl. defect-class
confirmation; the Director's acceptance is explicitly PENDING the
Keeper's independent challenge — that challenge is requested in
this PR's queue row (§7).

## 3. THE FAILING-FIRST SUITE (this PR)

`form/gs4_sandbox_test.py`, registered in `form/regress.py` LIST
immediately after `form.lm2_splitter_test:smoke`. Ten checks in four
runs over the E4 contract field (same field, so the suite is
falsifiable against #403's published log):

- **A (boxed field, default growth) — the wall contract:**
  A0 wall real in plane authority (control); A1 enumeration
  excludes cross-wall pairs; A2 no proposal parents span the wall
  (manifestation a); A3 no boxed drift offspring carries any
  outside-only token (manifestation b).
- **B (unboxed control):** B1 all pairs still scanned; B2 boxed
  output differs from unboxed output (the defect pin: today boxing
  changes nothing, so the outputs are identical and the check
  fails; after containment, the boxed run must differ — cross-wall
  output gone — while B1 keeps the unboxed path byte-stable).
- **C (scope_ids control):** C1 scoped growth scans only the
  selected pair; C2 zero leaks. PASS today; must not regress.
- **D (scope controls):** D1 invalid scope ID raises ValueError
  ("scope IDs not on plane"); D2 empty scope grows nothing, no
  silent fallback to full. PASS today; must not regress.

Result on main @074b30f (verbatim from the run; exit code of the
module run is 1 by design — smoke() False):

```
[PASS] A0 wall is real in plane authority :: enhance_scope(in_a)=['in_b']
[FAIL] A1 enumeration excludes cross-wall pairs :: pairs_scanned=10 (10 = all pairs incl. 6 cross-wall; 4 = wall-respecting)
[FAIL] A2 no proposal parents span the wall :: cross-parented proposals=4 [('harbor_lantern_inkeep_harbor_4367', ['in_a', 'out_a']), ('harbor_lantern_inforge_harbo_4744', ['in_b', 'out_a']), ('harbor_lantern_inkeep_harbor_9856', ['in_a', 'out_b']), ('harbor_lantern_inforge_harbo_7385', ['in_b', 'out_b'])]
[FAIL] A3 no boxed drift offspring carries outside-only tokens :: drift offspring carrying outside-only tokens=[('harbor_lantern_inkeep_fjord__5069', ['in_a'], ['fjord', 'glacier', 'obsidian', 'outpost', 'tundra', 'wolf']), ('harbor_lantern_inforge_fjord_3935', ['in_b'], ['fjord', 'glacier', 'obsidian', 'outpost', 'tundra', 'wolf'])]
[PASS] B1 unboxed control still scans all pairs :: pairs_scanned=10 (10 expected)
[FAIL] B2 boxed default output equals unboxed output (defect pin: boxing must change growth output; today it changes nothing) :: boxed proposals=10 unboxed proposals=10; identical=True
[PASS] C1 scope_ids growth scans only the selected pair :: pairs_scanned=1 (1 expected)
[PASS] C2 scope_ids growth has zero leaks :: leaks=0
[PASS] D1 invalid scope ID refuses with ValueError :: ValueError="scope IDs not on plane: ['missing_unit_xyz']"
[PASS] D2 empty scope grows nothing (no silent fallback to full) :: proposals=0 scope_mode=contextual
GS-4 SANDBOX: 6/10 checks passed; FAILING (failing-first, defect present): ['A1 enumeration excludes cross-wall pairs', 'A2 no proposal parents span the wall', 'A3 no boxed drift offspring carries outside-only tokens', 'B2 boxed default output equals unboxed output (defect pin: boxing must change growth output; today it changes nothing)']
```

Campaign consequence, stated plainly: once this PR merges, every
regression campaign runs this suite and reports it RED (278/279
with this as the single disclosed red) until the GS-4 containment
build lands under a Director scope ruling. That red is the
failing-first evidence doing its job; it is not a regression
introduced by this PR (the suite fails on unmodified main today,
as quoted).

## 4. DOES ENUMERATION-LEVEL PAIR FILTERING SUFFICE FOR BOTH MANIFESTATIONS?

**Short answer: for the two reproduced manifestations, YES — by
construction of the single loop, and the reasoning is checkable in
the code. For "no outside material can reach a boxed unit's growth
output by ANY path," NO such claim is made: three edges remain
UNPROVEN (§4.3).**

### 4.1 What the code shows (main @074b30f, read for this prep)

`RingedGrowth.run` (form/dell_matrix/ringed_growth.py) executes,
per cycle, exactly one pair-driven flow:

1. `ids = list(plane.units.keys())` (:474); the nested loop
   (:485–489) scores EVERY unordered pair via `_affinity` and
   appends it to `pairs`; `pairs` is sorted by affinity (:490).
2. The consumption loop (`for a, b, aff in pairs`, :498) is the
   ONLY iteration over unit pairs in `run()`. Every token read in
   it is `_tokens_uid(plane, a)` / `_tokens_uid(plane, b)` for the
   CURRENT pair (:507), plus `_parent_goals(plane, [a, b])` for the
   same two units.
3. The Solstice branch (manifestation a) composes from `ua`/`ub`
   — the current pair — or, when a docked session is supplied,
   calls `session.synthesize([a, b])` for the current pair.
4. The drift branch (manifestation b) sets `primary = a` and
   `gained = _tokens_uid(plane, b) - _tokens_uid(plane, a)`
   (:585–588) — the peer `b` is the same enumerated pair's second
   member. Drift does NOT draw from a wider token pool: there is
   no field-wide token set, no corpus, no third unit read anywhere
   in the branch. Its "Touch:" line names `plane.units[b]` — the
   pair peer.
5. `_tokens_uid` (:89–92) reads exactly one unit's blob
   (label + detail + words + goals) through `_unit_blob`. No
   cross-unit aggregation exists in the token path.
6. The remaining `nursery.add` in `run()` — the body-pulse
   vital-organ restore (:460) — fires only when the body pulse
   reports vital organs missing; its content is organ names from
   the pulse, its parents are `[]`, and no unit tokens enter it.
   It is not a pair path and not a token-inflow path (its content
   is system-organ vocabulary, identical for every field).
7. Entry: `Program.grow_ideas` (form/open.py:1268) hands `run()`
   exactly one plane object — the real plane, or a
   ScopedPlaneView when `scope_ids` is given (:1313). There is one
   `RingedGrowth` per Program (`self.growth`, open.py:273); the
   proof scripts that construct their own engines
   (p3_r31/r35/r36) drive `run()` directly with hand-built planes
   and are outside the `grow_ideas` contract surface.

Therefore: if enumeration never emits a cross-wall pair, then
within `run()` no code path can pair a boxed unit with an outside
unit, compose from both, or drift one from the other — because
every composition and every drift in `run()` is parameterized by
exactly one enumerated pair. Both reproduced manifestations die
at the same point, which is precisely the #403 GS-4 sketch's claim,
now verified against the full loop rather than the two branches
alone.

### 4.2 What the probe logs show

- E4: manifestations (a) and (b) BOTH appear in one default run
  over the enumerated pairs, and the scope_ids run over the same
  boxed field — where the view presents only the inside-inside
  pair — produces zero leaks. That is the enumeration filter's
  effect demonstrated through the existing consumer-side view:
  restrict the pair set and both manifestations vanish together.
- E3: manifestation (b) appears while (a) is penalty-suppressed —
  consistent with one loop, two gate bands (Solstice ≥ 0.28 vs
  Equinox/Standstill ≥ 0.16/0.10): the same cross-wall pair that
  fails the Solstice band can still land in the drift band. A
  branch-local fix to either band would leave the other open;
  the enumeration point is the only single point upstream of both.

### 4.3 UNPROVEN edges — named, not asserted away

The Director forbade asserting "no alternative token inflow"
without proof. The following are NOT proven by this prep, and the
GS-4 scope ruling should treat them as open:

- **U1 — Post-growth Program-level composition.** `grow_ideas`
  does more than `run()`: after it returns, duo.evolve runs on the
  owner's state, nature forces plant/grow over plane units
  (open.py:1316ff — forces planting follows the view's first 12
  units under scope; under default growth it iterates the real
  plane), and the opt-in `auto_confirm_grow` path confirms PENDING
  proposals into live units (open.py:1336ff). Whether forces or
  confirm can move outside material INTO a boxed unit's live
  content (as opposed to growth proposals) was not probed. The
  reproduced defect and the §3 suite are scoped to
  RingedGrowth proposal generation; U1 is a separate question
  about post-growth mutation surfaces.
- **U2 — Docked-session synthesis semantics.** With a docked Psalm
  (`session.synthesize([a, b])`), enumeration filtering still
  bounds WHICH pairs reach the dock, but what the docked mind
  authors for an admissible pair is outside token-level proof —
  by doctrine its output is PENDING and read, not proven. No
  claim is made about docked content beyond pair admissibility.
- **U3 — Multi-cycle compounding.** All reproductions and the §3
  suite run `cycles=1`. Across cycles ≥ 2, proposals from cycle 1
  remain PENDING (they do not become plane units inside `run()`),
  so the pair set does not grow within `run()` — read from the
  code, not probe-proven. If a caller confirms proposals BETWEEN
  grow calls, the confirmed units are ordinary plane units for
  the next call and the wall question re-applies to their boxing
  state at that time; that interaction is untested.

## 5. GS-4 BOUNDARY (what is and is not proposed)

IN (the smallest containment, from #403, restated as the boundary
of any future implementation authorization):

- Enumeration-level exclusion inside `RingedGrowth.run` ONLY: at
  pair enumeration, skip a pair when exactly one unit is
  sandboxed, or when both are sandboxed into DIFFERENT sandboxes.
  Same-sandbox pairs and unboxed-unboxed pairs are untouched.
- `pairs_scanned` counts admissible pairs only; the step receipt
  gains `pairs_excluded_cross_sandbox: N` (named, never silent).
- `_affinity` and `Plane.enhance_scope` are NOT modified; the soft
  `in_scope` term stays for admissible pairs, where it is already
  consistent with the wall.

OUT (explicit non-changes, per the HOLD):

- NO default-semantics change: bare growth still means the full
  plane; the doctrine's default flip is GS-3, a separate ruled
  step, and Ace's bare-grow ruling (grow nothing, say so) is a
  SELECTION default question for GS-1/GS-3 — not decided here.
- NO DCC-XI–XV pin changes: their full-plane fields are unboxed,
  so baseline behavior and `scope_mode="full"` assertions are
  untouched by the boundary above; any implementation must prove
  that by running those suites unmodified.
- NO change to `scope_ids` validation, ScopedPlaneView,
  SandboxGate, `Plane.box`/`unbox`/`enhance_scope`, the Nursery,
  or `grow_ideas`' signature.
- NO GS-1 resolver, NO selection grammar, NO surface changes —
  those wait on Q-GS.1–Q-GS.11.
- NO implementation in this PR; any build requires a separate
  Director scope ruling on the §6 contract.

## 6. PROPOSED SELECTION CONTRACT (design text only — for Director review)

The exact contract the GS-4 build would implement. Terms: a unit's
WALL KEY is `None` when unboxed, else its `sandbox_id`. Two units
are WALL-MATES iff their wall keys are equal.

- **C-1 (admissibility).** A pair `(a, b)` is admissible to
  enumeration iff `a` and `b` are wall-mates. Cross-wall pairs are
  EXCLUDED from enumeration — never scored, never gated, never
  drifted from. Exclusion is an eligibility boundary (STORED ≠
  ELIGIBLE), not a ranking penalty; the `_affinity` soft
  `in_scope` term is not the mechanism and is not relied on.
- **C-2 (boxed owners).** A boxed unit's growth relations exist
  only inside its own sandbox: inside-inside pairs enumerate
  normally (the sandbox grows internally, as Ace's doctrine
  requires — "a sandbox" is a working space, not a freeze).
- **C-3 (mixed boxes).** Units in different sandboxes are
  strangers to each other exactly as boxed-to-unboxed: no pair
  crosses any wall, in either direction, for either manifestation.
- **C-4 (unboxed field).** When no unit is boxed, the admissible
  set is the complete pair set: enumeration, `pairs_scanned`,
  gates, and proposal output are byte-identical to today
  (suite check B1 + the DCC pins are the enforcing evidence).
- **C-5 (explicit ALL).** There is no growth mode — in GS-4 — that
  enumerates across walls. "All" under selection (GS-1/GS-3,
  ruled separately) means all ADMISSIBLE pairs of the selected
  set, never a wall override. A caller who wants cross-wall
  material today has exactly one lawful door: unbox the units
  (an explicit, receipted plane operation) and then grow. GS-4
  adds no bypass flag, parameter, or environment switch.
- **C-6 (default unset).** GS-4 changes nothing about what an
  UNSET selector means: `scope_ids=None` still hands `run()` the
  real plane and `scope_mode` still reports "full" — "full" now
  truthfully means "the full admissible pair set," and the receipt
  says how many pairs the wall excluded (C-7). The selection
  DEFAULT question (what bare grow selects — Ace: nothing, with
  an honest receipt) belongs to GS-3 and stays exactly as open
  after GS-4 as before it.
- **C-7 (receipt).** Each step receipt gains
  `pairs_excluded_cross_sandbox: N` (present whenever N ≥ 0;
  zero on unboxed fields). Silence about exclusions is a contract
  violation: a reader of the receipt must be able to tell that
  the wall acted, and how much it excluded.
- **C-8 (scoped growth composition).** `scope_ids` behavior is
  unchanged and composes by intersection: the ScopedPlaneView
  presents the selected units; enumeration admissibility then
  applies within the view. Selecting across a wall yields the
  within-wall pairs of the selection and receipts the exclusions —
  it never errors and never silently broadens (the existing
  consumer-boundary law), and never silently narrows without the
  C-7 count.
- **C-9 (authority preservation).** The wall's authority stays
  where it already lives: `Plane.box`/`unbox` and `sandbox_id`
  membership are the sole inputs; `enhance_scope` remains the
  plane's scope authority for its existing consumers. GS-4
  creates no second sandbox store, no growth-local box registry,
  and no new Dell or selector authority. The eligibility question
  GS-2 later asks of the scope branch (Q-GS.11: should scope_ids
  be gated like the context branch?) is untouched — C-8 preserves
  today's scope_ids eligibility exactly.
- **C-10 (DCC-pin risk, named).** The DCC-XI Control D pins —
  "BASELINE COMPATIBILITY: ordinary growth keeps full-plane
  behavior" and `scope_mode == "full"` assertions (dcc_xi:132,
  dcc_xii:314, dcc_xiii:362, dcc_xiv:366, dcc_xv:472) — are at
  risk ONLY if an implementation changes unboxed behavior or the
  scope_mode string; the C-4/C-6 clauses are written to make both
  impossible. Residual risk: any DCC fixture that boxes units and
  asserts full-plane pair counts would break BY DESIGN under
  C-1; the grounding sweep found no such fixture (DCC fields are
  unboxed), but the implementation circuit must re-run DCC-XI–XV
  unmodified and report, not re-pin. If a pin does conflict, the
  conflict surfaces to the Director — re-pinning is not
  authorized by this contract.

## 7. PROPOSED REGISTER TEXT + ASKS

Proposed register row (number left to the authorities):

"DD-NEW — Growth sandbox-integrity defect (CONFIRMED by two
independent reproductions, 2026-11-12; Director scoped ACCEPTANCE
mail 1a1d05d91f6401dc, pending Keeper independent challenge):
default RingedGrowth pair enumeration is wall-blind — cross-sandbox
pairs are scored (soft in_scope penalty only) and produce
(a) two-parent Solstice proposals spanning the wall and
(b) single-parent Equinox/Standstill drift offspring of boxed
units carrying outside units' tokens under inside-only lineage.
Boxing changes nothing in default growth output (control-identical,
twice). Containment exists only via explicit scope_ids selection.
Failing-first suite form/gs4_sandbox_test.py (6/10, A1/A2/A3/B2
red) pins the contract. Repair boundary proposed as GS-4
(enumeration-level exclusion + receipted exclusion count; no
default change, no DCC pin change; selection contract in
GS4_SANDBOX_CONTRACT_PREP_2026-11-12.md §6) — IMPLEMENTATION HOLD
pending Director scope ruling on the contract and Keeper scope
confirmation."

Asks (also the DIRECTOR_REVIEW_QUEUE row riding this PR):

1. **Keeper:** independent challenge of the reproduction (the
   Director's acceptance is pending it) + scope confirmation or
   challenge of the §5 boundary / §6 contract.
2. **Director:** register placement (assign the DD number) +
   review of the §6 contract; any GS-4 implementation requires
   your separate scope ruling — none is requested to start before
   that ruling.
3. Both: note the disclosed campaign consequence (§3) — the
   registered failing-first suite runs RED in every campaign
   until the build lands.

## 8. NON-COVERAGE / WHAT THIS PR DOES NOT DO

- No product code changed; no fix implemented, sketched in code,
  or pre-staged anywhere.
- #403 untouched (records-only, as directed); #402 untouched;
  Q-GS.1–Q-GS.11 untouched.
- No MWL credit claimed or implied; the defect dial does not move
  on this PR (register placement is the authorities' act).
- The enumeration-sufficiency conclusion is scoped to
  RingedGrowth proposal generation; U1–U3 (§4.3) remain open
  questions, not findings.
- Test realism: the §3 suite is INTEGRATION-level evidence
  (public `Program.grow_ideas` path on disposable owners), the
  same level as both reproductions — stated, not upgraded.
