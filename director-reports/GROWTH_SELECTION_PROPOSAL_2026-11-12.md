# GROWTH SELECTION — PROPOSAL: scoped growth under Ace's selection doctrine

**Date:** 2026-11-12 · **Prepared by:** Uni (proposal only — no code changed,
no build authorized or started by this document)
**Governing directive:** Ace, main chat, 2026-11-12 — growth must NOT consider
the entire matrix by default; the whole field is in scope only when ALL is
explicitly selected (full doctrine in §1).
**Grounding:** DISCOVER > VERIFY > CLASSIFY executed against merged main
(post-#397 clone @ `2e46272`; drift check vs current origin/main `48eb9b7`:
the two intervening commits touch ONLY `director-reports/KEEPER_WATERMARK.md`
— zero drift in any growth file). Probe: disposable owners, executed, state
artifacts removed after. PR #401 (C7.Profile) is a branch, NOT on main; its
board is cited from its branch clone and labeled as such wherever used.
**Two-cycle note:** this doctrine is a NEW item — cycle 0 (grounding +
proposal). No prior cycles consumed; the cap clock starts at the first
build cycle.
**Register note:** this PR adds NO master-list (MWL) row. A register row
for the growth-scope item is PROPOSED as text in §8 for the authorities to
place. No completion credit is claimed for anything in this document.

---

## 1. THE DOCTRINE (Ace, 2026-11-12)

Ace's words, in substance verbatim:

> "Growth should not consider the entire matrix unless all is selected. It
> should work with Select to select what is considered, and it should work
> with families and groups if selected. It can consider resonating ideas
> only if chosen. It can be grouped by any category, group, relationships
> in any category. It can grow a single idea and all within it, a project
> with the ideas in it, a sandbox that doesn't affect anything outside of
> it. You should have flexibility and selection options."

Restated as a contract:

- The **considered set is chosen**, never defaulted to the whole field.
  The whole matrix is in scope **only when ALL is explicitly selected**.
- Growth works **with SELECT**: selection is the mechanism that decides
  what growth may consider.
- Named selectors: **families**, **groups**, **resonating-ideas-only**
  (only if chosen), **any category**, **grouping by any category**,
  **relationships in any category**, **a single idea and all within it**,
  **a project with its ideas**, **a sandbox that affects nothing outside
  it**.
- Headline: **flexibility and selection options**.

One finding in this proposal bears directly on the doctrine and is stated
plainly in §4: today's growth does **not** honor the sandbox clause —
pair enumeration is wall-blind and single-parent drift crosses the wall
outright. That is filed as a defect-class finding, not softened into a
design preference.

---

## 2. CURRENT SCOPING REALITY (verified)

### 2.1 The one consumer and its two modes

`Program.grow_ideas(cycles=1, scope_ids=None, include_superseded=False,
session=None)` — `form/open.py:1268`. It is the ONLY production caller of
`RingedGrowth.run` (`form/dell_matrix/ringed_growth.py:392`; other call
sites are proof scripts).

- **Default (`scope_ids=None`):** the real plane is passed whole;
  `scope_mode="full"`, `scope_ids=None` on the receipt.
- **Scoped (`scope_ids=[...]`):** validated at the consumer boundary —
  every ID must be a live plane unit or
  `ValueError("scope IDs not on plane: [...]")` (code comment states the
  law: *"Never silently broaden"*). The plane is wrapped in
  `ScopedPlaneView` (`form/mandell/knowledge_selector.py:74`): a per-call,
  never-persisted, read-only view whose `.units` is a snapshot dict of
  exactly the requested subset. All other attribute access delegates to
  the real plane, which is safe because the SOLE pair-enumeration point
  is `list(plane.units.keys())` inside `RingedGrowth.run`.
- **Superseded handling:** inside `_affinity` (ringed_growth.py:~274) via
  the canonical lifecycle boundary — ordinary growth excludes
  faded/SUPERSEDED units (affinity forced to 0.0 → gate "None");
  `include_superseded=True` is the explicit historical mode (WO-5.3).
- **Empty scope is already lawful:** `scope_ids=[]` →
  `scope_mode="contextual"`, cycle reports "no live ideas", 0 proposals,
  NO fallback to full (probe §2.3; also DCC-XI Control C).

### 2.2 RingedGrowth consumption

Per cycle: `ids = list(plane.units.keys())`, then ALL unordered pairs
(C(n,2)) are scored by `_affinity` (harmonic/Jaccard/spatial/in-scope/
goal/body composite) and gated: Solstice ≥ 0.28 (new cross), Equinox ≥
0.16 / Standstill ≥ 0.10 (single-parent drift: the proposal is parented
by one unit but gains the OTHER pair member's tokens,
ringed_growth.py:~584), below = None. Caps: max_new=10, max_evolved=8 per
run. Proposals land in the shared Nursery as PENDING (inert until
confirmed — "live matrix untouched"). Receipt per cycle carries
`live_ideas` and `pairs_scanned` — the consideration count is directly
observable.

### 2.3 Probe evidence (5 placed ideas + 'welcome' seed unit = 6 units)

| Call | scope_mode | live | pairs_scanned | proposed |
|---|---|---|---|---|
| `grow_ideas(1)` (default) | full | 6 | **15** (all pairs) | 3 new + 8 evolved |
| `grow_ideas(1, scope_ids=[A1,A2])` | contextual | 2 | **1** | 1 new, parents ⊆ scope, scope echoed verbatim |
| default, A1+A2 boxed in a sandbox | full | 6 | **15** (wall-blind) | see §4 — cross-wall drift |
| `scope_ids=["missing_unit_xyz"]` | — | — | — | `ValueError: scope IDs not on plane: ['missing_unit_xyz']` |
| `scope_ids=[]` | contextual | 0 | 0 | 0 proposals, no fallback |

The scoping door works exactly as designed where it is used: an explicit
two-unit scope considered exactly **1 pair** instead of 15, a missing ID
**refused** rather than widened, and an empty scope stayed empty rather
than falling back to the full field.

### 2.4 Who calls grow_ideas with what

| Caller | Call | Scope today |
|---|---|---|
| Executor Dell **6 Cycle** (executor_leaf.py:165) | `grow_ideas(n)`, n = count label 1..5 | FULL |
| Executor Dell **13 Loop** (executor_leaf.py:240) | `grow_ideas(executed)` with B2 count-refusal law | FULL |
| REPL English "grow" intent | semantic_router → the Dells above | FULL |
| REPL connect-session `grow` verb (repl.py:4430) | `grow_ideas(cycles, session=docked)` | FULL |
| REPL onboarding/demo path (repl.py:444) | `grow_ideas(1)` | FULL |
| Core I ops **"use idea \<pid\> to grow"** (core_i_ops.py:426) | `grow_ideas(1, include_superseded=True)` then post-filters offspring by parentage | **FULL plane for a single-idea intent** |
| Core I ops **grow_contextual** (Dell 37; core_i_ops.py:730) | select_for_context → eligibility (confirmed + revision-active + participation + dependency-valid) → conflict quarantine → disposition → lineage → `grow_ideas(1, scope_ids=routable_ids)` | SELECTED (context text; top-5 default) |
| Internal loops: accept.py:32, invariants.py:68 (`grow_ideas(3)`), code_evolution.py:141, function_150_loop.py:220, program_evolve_150_loop.py:124, live_host.py:56, live_visual.py:904, visual_evolve_loop.py:892, program_strength.py:47, ancient/stonehenge_seed.py:178 | bare | FULL |
| Profile benchmark growth stage (PR #401 branch, NOT main) profile_board.py:121 | `grow_ideas(1)` on a DISPOSABLE program | FULL (on throwaway state) |

**The default end-to-end:** bare growth turns the EnhanceGate ON if it
was off, attaches the owner's SemanticGraph as a read-only signal, runs
RingedGrowth over every live unit pair, then UNCONDITIONALLY fires
`duo.evolve("13[Loop] :: RingedGrow x{cycles}")`, plants/grows nature
forces over the (possibly scoped) view's first 12 units into the owner's
persistent forces state, optionally auto-confirms all pending proposals
(opt-in `auto_confirm_grow`), and note_seeds Dell 13. DuoBeta's evolve
signal and the note_seed are scope-blind; forces planting follows the
view.

---

## 3. SELECTOR INVENTORY — per Ace's named selectors

Classification: EXISTS (resolution mechanism present and usable) /
PARTIAL (machinery present, bridge or semantics missing) / ABSENT.
**No selector is claimed beyond this classification.**

| Ace's selector | Class | Basis (one line) |
|---|---|---|
| Families | **PARTIAL** | Idea "family" exists only as lineage grouping (reporting, never a selection input); Dell families classify Dells, not ideas |
| Groups | **EXISTS** (mechanism) / not bridged | Dell 82 named unit-ID collections + Dell 53 scope law exist; growth never reads them |
| Any category / grouping by category | **ABSENT** as a system; PARTIAL via fixed facets | `Unit` has no category/tag/topic field; skin/origin/lifecycle/sandbox/goals facets exist today |
| Relationships in any category | **EXISTS** (graph) / bridge needed | SemanticGraph's 5-type edge vocabulary is the relationship-category system; resolution must cross the TD-1 Idea-ID binding |
| Resonating ideas only (if chosen) | **PARTIAL** | Affinity gates and resonance pulse both computable; neither is wired as a selection, and the two notions are lawfully distinct |
| A single idea and all within it | **EXISTS** (pieces) / composition needed | TD-1/TD-2 containment bridge pieces exist; the composed WITHIN resolver does not |
| A project with its ideas | **ABSENT** (honest) | No project construct exists anywhere in state |
| A sandbox affecting nothing outside it | **PARTIAL** | Membership selection resolves trivially; growth itself is wall-blind — see the §4 finding |

### (a) FAMILIES — PARTIAL
- *Idea families:* the only family structure over ideas is **lineage**:
  `knowledge_lineage.lineage_groups(program, unit_ids)` groups units by
  shared derivation root; `selected_root_ids` unions roots. Already
  computed in the grow_contextual receipt — but as REPORTING, never as a
  selection input. A FAMILY(root) resolver is a thin wrap over this.
- *Dell families:* registry manors (`form/mandell/registry.py` — one manor
  string per Dell), CORE_I/CORE_II namespaces, Core II dispatch families
  (registry.py:187), persona categories. These classify DELLS, not ideas;
  they cannot select a growth set. If Ace meant idea families, lineage is
  the v1 candidate (Q-GS.7).

### (b) GROUPS — EXISTS (mechanism) / not bridged to growth
- Dell **82 Group** (spectrum_ops.py:223): `st.groups[name] = list(st.selected
  or all plane ids)` — named collections of PLANE UNIT IDs in Core II
  state, persisted in snapshots (spectrum_ops.py:22,41; C3.Diff treats
  "groups" as a content slice).
- Dell **53 Scope** + `scope_universe` (core_ii_exec.py:~100): scope is
  `"plane"` (default) or a group name; membership = group ∩ plane in
  plane order; unknown scope REFUSES — *"never silently widen to the
  whole plane"* (Director ruling, D1 reconciliation R1, 2026-10-29).
  This is the codebase's own scope-selection precedent, with a ruling
  behind it.
- BUT: RingedGrowth/grow_ideas never read `st.groups` or `st.scope`.
  GROUP(name) resolution for growth = reuse `scope_universe`'s membership
  rule; the store and the law already exist.

### (c) CATEGORIES — ABSENT as a system; PARTIAL via fixed facets
- `Unit` (plane.py:48) has NO category/tag/topic field: id, label, words,
  detail, goals, skin, x/y, sandboxed/sandbox_id, manifest, parents,
  origin, lineage_version, idea_id. `Proposal` (nursery.py:87) likewise:
  kind (new|evolved|design|auto), status, origin, lifecycle/revision
  fields.
- Facets a resolver could target TODAY without new state: **skin**
  (cube/sphere/core/flower/building/words/circle), **origin**,
  **lifecycle state**, **sandbox membership**, **goals** (free-text, not
  a category).
- A user-defined category/tag on ideas does not exist anywhere (grep:
  no category field in plane/nursery/idea_persist). Building one is new
  state = separate decision (Q-GS.8).

### (d) RELATIONSHIPS IN A CATEGORY — EXISTS (graph) / bridge needed
- `SemanticGraph` (form/mandell/semantic_graph.py) is the sole
  relationship authority: closed type vocabulary — CONTAINS, RELATED_TO,
  DEPENDS_ON, REFERENCES, DERIVED_FROM (RelationshipType, :51) — i.e.
  the relationship "categories" already exist as edge types. Queries:
  `by_type(t)`, `outgoing(id, type)`, `incoming(id, type)`,
  `association_neighbors(id)`, `find_path(...)`.
- Edges join **canonical Idea IDs**, not plane unit IDs. Resolution to a
  growth set must cross the TD-1 binding (Unit.idea_id) both ways;
  unbound units/ideas are unreachable by this selector (fail-closed,
  named).

### (e) RESONATING-ONLY — PARTIAL
- Two computable notions exist today; neither is wired as a selection:
  1. **Affinity gates** — a pair "resonates" in growth's own terms at
     Standstill ≥ 0.10 / Equinox ≥ 0.16 / Solstice ≥ 0.28
     (ringed_growth.py:42). RESONATING(seed) = units whose `_affinity`
     to the seed passes a chosen gate is computable from existing code.
  2. **Resonance pulse** — `form/dell_matrix/resonance.py` pulse =
     diffusion over enhance-scope edges producing per-unit scores
     (EnhanceGate.pulse returns `scores`). Concept-separation law
     (resonance.py header, GDP-001 3.1.2): pulse ≠ affinity; do not
     merge them. Pulse also has side effects (session budget, state),
     so using it AS selection is a decision, not an implementation
     detail (Q-GS.4).
- The grow_contextual path is resonance-adjacent (token-overlap
  relevance) but is a relevance selection, not a resonance selection.

### (f) SINGLE IDEA + ALL WITHIN IT — EXISTS (pieces) / composition needed
- Containment authority: SemanticGraph `children` / `live_children` /
  `descendants` / `ancestors` (:1103–1149) over Idea IDs; TD-2 unit
  layer (unit_containment.py: nest/promote/reparent +
  `containment_view` :455) with SemanticGraph the ONLY containment
  authority (certified scope).
- WITHIN(unit) resolution: unit → `idea_id` binding →
  `descendants(idea)` → Idea IDs → units bound to them, + the unit
  itself. Bindings are OPTIONAL (`binding_census`, unit_binding.py:325)
  — an unbound unit has no within-set beyond itself; partially-bound
  descendant sets resolve with exclusions named (EKC-I resolution
  style). Fail-closed points are identifiable today; the composed
  resolver does not exist yet.

### (g) PROJECT — ABSENT (honest)
- No project construct exists in state: no Project class, no project_id,
  no projects collection (grep across form/open.py, persist_rest.py,
  idea_persist.py, plane, nursery — the only "project" hits are
  *projection*, a different word). Nothing to resolve PROJECT(name)
  against. What it would take: a definition from Ace (Q-ACE-GS.1) — a
  curated named set (≈ GROUP), a containment root (WITHIN(root) already
  covers it), or a workspace/owner — then either reuse an existing store
  or a new persisted construct (separate circuit, not a resolver branch).

### (h) SANDBOX — PARTIAL (two different things share the name)
1. **Plane sandboxes (membership):** `Plane.sandboxes: Dict[str, Sandbox]`
   (plane.py:84; Sandbox = id + label + member_ids), `plane.box(ids, id)`,
   SandboxGate (Dell 23 Lock; auto-box on place when on). SANDBOX(id) as
   a *selection* resolves trivially from member_ids. Resonance already
   respects the wall: `enhance_scope` (plane.py:223) returns co-members
   only for a boxed unit. Growth does not — see §4.
2. **Disposable-program isolation (the Profile pattern):** a throwaway
   owner whose entire state is discarded (profile_board.py, PR #401
   branch). This DOES affect nothing outside — because the program
   itself is the sandbox. It exists as a pattern, not as a growth mode
   on a live program. On a live program, even a perfectly scoped grow
   still lands PENDING proposals in the real nursery (inert by design),
   fires duo.evolve, and plants forces — effects outside any selection
   (Q-GS.6).

---

## 4. THE SANDBOX FINDING — defect-class finding, stated plainly

**Finding: growth's enumeration is wall-blind. A plane sandbox does not
bound what growth considers, and growth effects cross the wall.**

Evidence (probe, §2.3): with 2 of 6 units boxed in a sandbox, a default
`grow_ideas(1)` still reported **pairs_scanned = 15** — every pair in the
field, including every cross-wall pair. Cross-wall pairs are only
*penalized* (the in-scope affinity term is 0.2 instead of 1.0,
ringed_growth.py:~247); they are not excluded. Worse, single-parent
**DRIFT crosses the wall outright**: the probe's boxed unit
`plant growth depends on water` produced an evolved proposal
`→ cooking / heat` whose gained tokens came from an OUTSIDE unit
(mechanism: ringed_growth.py:~584 — a drift proposal is parented by one
unit but gains the other pair member's tokens).

Consequence against the doctrine: **"a sandbox that doesn't affect
anything outside it" is NOT today's growth behavior.** Resonance honors
the wall (enhance_scope is co-members only); growth does not. This is
filed as a defect-class finding discovered by the grounding probe, not
as a design preference and not as a selector gap.

**Proposed register treatment (text proposed; numbering and placement
are the authorities' to assign):**

> **DD-NEW — SANDBOX INTEGRITY IN GROWTH.** Plane sandbox walls do not
> bind RingedGrowth. Pair enumeration inside `grow_ideas` is wall-blind
> (C(n,2) over every live unit regardless of sandbox membership;
> cross-wall pairs merely penalized in the in-scope affinity term), and
> single-parent DRIFT crosses the wall outright: a boxed unit's evolved
> proposal can gain tokens from a unit outside its sandbox
> (ringed_growth.py ~584; probe evidence 2026-11-12, GROWTH SELECTION
> grounding). Ace's doctrine (2026-11-12) requires a sandbox that
> doesn't affect anything outside it; that is not today's behavior.
> Defect-class finding. Proposed repair slice: GS-4 (enumeration-level
> cross-wall exclusion, pair + drift). Status: PROPOSED — awaiting
> Director disposition (new DD row vs. a facet of the growth-selection
> item).

A related but distinct question — whether a *scoped* grow on a live
program may still land PENDING proposals in the real nursery, fire
duo.evolve, and plant forces (effects outside any selection) — is NOT
part of this finding; it is routed as Q-GS.6.

---

## 5. COLLISION MAP

1. **Baseline-compatibility pins (the default is under test contract):**
   DCC-XI Control D is literally named *"BASELINE COMPATIBILITY:
   ordinary growth keeps full-plane behavior"* (dcc_xi_test.py:132
   asserts `scope_mode == "full"` — "baseline stays full-plane"); same
   pin at dcc_xii_test.py:314, dcc_xiii_test.py:362, dcc_xiv_test.py:366,
   dcc_xv_test.py:472. **A default flip re-pins these DELIBERATELY, in
   the open, or it is a silent contract break.** This is the largest
   single blast-radius item in the default question (§6).
2. **DD-08 / 72-16 — GATED, intersects, do not design over it.** 72-16
   is the legacy flow_executor vs canonical chain authority divergence
   (DIRECTOR_REPORT_72_16_FLOW_AUTHORITY). Its B4 defect is exactly
   about growth operands: the flow path's `_args_from_label` has no
   `grow` case and silently rewrites `13[Loop] :: 3` → `13[Loop] :: 1` —
   *"a different program than the caller wrote."* Consequences: (i) any
   scope grammar must ride the CANONICAL chain/executor path only;
   enriching Loop/Cycle operands widens the gated R-2 item's blast
   radius; (ii) R-2 remains design-review-only (plan §13.3); this
   proposal designs nothing over it.
3. **Plan §13.3 sit-down gate:** "growth" is named among the Ace
   sit-down clusters whose DESIGN is sit-down-gated. Ace's 2026-11-12
   ruling IS the Overseer speaking on that cluster — grounding proceeds;
   design choices route as Q-GS below rather than being taken
   unilaterally.
4. **Eligibility asymmetry (existing, must not be papered over):** the
   CONTEXT branch reaches the consumer only after selector eligibility
   (confirmed + revision-active + participation + dependency-valid),
   conflict quarantine, disposition, lineage. The `scope_ids` branch
   takes ANY live plane unit (placed or confirmed) with only the
   lifecycle gate inside `_affinity`. A grammar resolver inherits this
   asymmetry unless the Director orders it unified (Q-GS.11).
5. **DuoBeta coupling:** `duo.evolve` fires per grow regardless of
   scope. Under the information ladder
   (STORED≠ELIGIBLE≠SELECTED≠…≠LEARNED), a selection bounds what is
   CONSIDERED; whether it should also bound the learning signal is a
   policy question (folds into Q-GS.6), not a default.
6. **Profile benchmark (PR #401):** its growth stage calls full-plane
   `grow_ideas(1)` on disposable state — under the doctrine it must name
   ALL explicitly. Its whole purpose is timing the full tick, so ALL is
   the honest spec there (Q-GS.10).
7. **No intersection:** Q1/C-A persistence gate (save path — growth
   scoping touches no save/load semantics), DAF-09 (withheld;
   untouched), DD-06/07 (gated; untouched).

---

## 6. DESIGN SKETCH (smallest faithful shape — NOT built)

**One resolver, one existing door.** A single function
`resolve_growth_scope(program, spec) -> List[str]` returning unit IDs,
fed into the EXISTING `scope_ids` parameter of `grow_ideas`. No second
growth path, no RingedGrowth change in the resolver slice. Resolution is
fail-closed in the codebase's own idiom (EKC-I resolutions; Core II
scope_unknown refusal; grow_ideas' "never silently broaden"): an
unresolvable name, an empty result, or an unbound bridge target is an
honest refusal with the reason on the receipt — never a fallback to
full.

```
scope := ALL
       | IDS(id, ...)
       | CONTEXT(text)                 # existing Dell-37 selection, named
       | FAMILY(lineage_root_id)
       | GROUP(name)                   # Core II st.groups via scope_universe rule
       | SANDBOX(sandbox_id)           # plane.sandboxes member_ids
       | WITHIN(unit_id)               # unit + bound descendants (TD-1/TD-2)
       | RELATIONS(kind, from_id)      # kind in the 5 graph types
       | RESONATING(seed_id [, gate])  # affinity-to-seed >= gate
       | CATEGORY(facet=value)         # facets that exist: skin|origin|lifecycle
       | scope + scope                 # union
       | scope & scope                 # intersection
       # PROJECT(name) — NO BRANCH until a project construct exists
```

Receipt: the resolved spec text, per-branch resolved counts, exclusions
with reasons, and the final ID list join the existing `scope_mode` /
`scope_ids` fields (scope_mode gains the spec kind, e.g. "selected").
ALL is spelled, never implied: `ALL` resolves to every live unit ID and
goes through the same view as any other selection (identical behavior to
today's full mode, but chosen).

**The default question (presented, not decided).** Bare growth with no
selection:

- **(a) Refuse with guidance** — "name a selection, or say ALL." Purest
  reading of Ace's ruling. Blast radius: every bare caller in §2.4
  breaks until migrated — Dells 6/13 bare chains (incl. role seeds and
  the test suites that pin them), the REPL grow verb + demo, the dock
  grow verb, "use idea to grow", and ~10 internal loops (program_evolve,
  live_host, invariants, …) each need an explicit scope decision.
  Internal autonomous loops arguably SHOULD each become a deliberate
  ALL — but that is ~10 separate semantic decisions, not one migration.
  Plus the five DCC baseline pins (§5.1) re-pinned deliberately.
- **(b) Default to a named small scope** (e.g. contextual top-5, or the
  current focus) — every bare caller silently changes behavior;
  proposals users used to get stop appearing. Silent semantic change is
  the failure class this codebase's laws exist to prevent. NOT
  recommended.
- **(c) Bridge: bare = ALL, but named as such** — receipt says
  `scope_mode="full (default-all, unselected)"`, with a time-boxed
  migration to (a). Least breakage, weakest doctrine compliance: a
  default-all is precisely what Ace ruled against, so (c) is legitimate
  only as a Director/Ace-sanctioned bridge with an expiry, never as the
  resting state.

---

## 7. PROPOSED CIRCUIT SLICING

- **GS-1 RESOLVER:** grammar + `resolve_growth_scope` + additive
  `scope=` on grow_ideas (bare default UNCHANGED in this slice);
  failing-first per selector + refusal/empty cases; receipt provenance.
- **GS-2 SURFACES:** Dell 6/13 operand + REPL/dock grow verbs accept a
  scope (canonical chain path ONLY — DD-08 flag); decide the Core II
  st.scope bridge (Q-GS.3).
- **GS-3 DEFAULT FLIP:** per Q-GS.1 ruling; caller migration; DCC
  baseline controls re-pinned deliberately with the ruling cited.
- **GS-4 SANDBOX INTEGRITY:** enumeration-level cross-wall exclusion
  (pair + drift) in RingedGrowth so SANDBOX means "affects nothing
  outside"; side-effect audit (forces/evolve) per Q-GS.6.
- **PROJECT:** blocked on Q-ACE-GS.1 + a construct; separate proposal.

---

## 8. PROPOSED REGISTER ROW (text only — authorities place it)

No MWL row is added by this PR. If the authorities want the item on the
master list, the proposed text is:

> **GROWTH SELECTION (Ace doctrine, 2026-11-12):** growth considers only
> a selected set; whole field only on explicit ALL. Resolver + surfaces
> + default rule + sandbox integrity (GS-1..GS-4); PROJECT pending
> Q-ACE-GS.1. Status: OPEN — grounding + proposal published
> 2026-11-12; cycle 0.

The §4 sandbox finding's register treatment (new DD row vs. facet) is
likewise the authorities' placement call.

---

## 9. QUESTIONS

**For the Director:**

- **Q-GS.1 Default:** bare growth = refuse-with-guidance (a), bridge
  (c), or other? Migration policy for the ~10 internal autonomous loops
  — each a deliberate ALL, or scoped by their own context?
- **Q-GS.2 Grammar home:** additive `scope=` parameter vs a typed
  scope_ids; receipt provenance shape (spec text + per-branch counts +
  exclusions)?
- **Q-GS.3 Core II bridge:** should growth honor `st.scope` (Dell 53)
  when set — one scope authority shared with spectrum ops, or
  growth-local resolution only (two scope systems risk)?
- **Q-GS.4 RESONATING:** affinity-to-seed at which gate (0.10/0.16/0.28)?
  Seed-required, or set-internal (all pairs within the candidate set)?
  May selection run a resonance pulse (side effects) or must it stay
  pulse-free (affinity only)?
- **Q-GS.5 WITHIN edge law:** unbound unit → self-only + named, or
  refuse? Partially-bound descendant sets → resolve with exclusions
  named (EKC-I style) — confirm.
- **Q-GS.6 SANDBOX semantics:** selection-only (PENDING proposals in the
  real nursery, evolve/forces untouched) vs isolation (no effects
  outside — GS-4 + side-effect scoping)? Which does the doctrine
  require at v1?
- **Q-GS.7 FAMILY:** lineage-root grouping as the v1 meaning of
  "family" — confirm, or name the intended structure.
- **Q-GS.8 CATEGORY:** v1 facets (skin/origin/lifecycle) only, or is a
  user-defined category/tag field on units wanted (new state)?
- **Q-GS.9 "Use idea to grow":** migrate from full-plane + post-filter
  to WITHIN(pid)-based scope? Preserve its deliberate
  include_superseded?
- **Q-GS.10 Profile benchmark:** growth stage names ALL explicitly on
  disposable state — confirm intended shape.
- **Q-GS.11 Eligibility:** unify the scope_ids branch under the
  contextual branch's eligibility/conflict/disposition gates, or keep
  the documented asymmetry (any live unit selectable by explicit
  ID/group/etc.)?

**For Ace (genuinely his; routed via the review queue, non-blocking):**

- **Q-ACE-GS.1 What is a "project"?** A named set you curate (≈ a
  group), a root idea whose contents are the project (WITHIN already
  covers it), or a separate workspace? PROJECT selection cannot be
  built until this has a shape.
- **Q-ACE-GS.2** When you say "grow" with no selection picked, what
  should happen at the surface: stop and ask you to pick (or say ALL),
  or grow what you're currently looking at? (The user-facing face of
  Q-GS.1.)

---

## VERDICT (grounding)

Ace's doctrine is implementable mostly from existing machinery: the
scoped-consumption door (ScopedPlaneView + scope_ids), a named-group
store with a refuse-on-unknown scope law (Core II), lineage grouping,
the SemanticGraph type vocabulary + TD-1/TD-2 containment bridge, plane
sandbox membership, and affinity gates all EXIST. What does not exist:
the unified resolver, any surface grammar for scope on the growth entry,
a project construct (ABSENT), a user category system (ABSENT), sandbox
integrity inside growth (today's wall is a weight, and drift crosses
it), and a ruling on the bare-growth default — whose flip carries the
largest blast radius in the item (5 test pins + every bare caller).
No conflict with a certified behavior was found; the one gated
intersection (DD-08 / 72-16) is flagged, not designed over.

**Asks:** Director — rule Q-GS.1–Q-GS.11 and dispose of the §4 sandbox
finding (register placement). Keeper — confirm or challenge the
grounding classifications and the finding. Ace — Q-ACE-GS.1/Q-ACE-GS.2
at his convenience (non-blocking).
