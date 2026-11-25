# DIRECTOR REPORT — TRACK D PLANE-TO-IDEA BRIDGE PLAN

Circuit: TRACK D — PLANE-TO-IDEA BRIDGE, BOUNDED PLANNING
Authority: Director Mode D disposition 2026-11-03 ("After
integration, proceed with bounded Track D Plane-to-Idea bridge
planning"). Planning only: NO implementation, NO production code,
NO test changes in this circuit.
Base: main 2740c22cbece8f57eb0d312027f9a5817ef1944c (PRs #255–#259
merged). Branch: uni/track-d-bridge-planning.
Status: SUBMITTED for Director ruling.

Decided architecture (Director ruling 2026-11-03, NOT re-litigated
here): Option A — bind Plane units to canonical Ideas through a
controlled bridge. SemanticGraph remains the ONLY containment
authority. Plane becomes a navigable perspective over canonical
Ideas, not a second containment system.

## 0. Headline

No premise of option A is falsified. The census re-verifies the
sleep-run grounding at this base (all Track D layer files are
byte-identical from the grounding base b6dd46b to 2740c22 —
evidence: carryover_diff.log), and a live probe at this base
(16/16, INTEGRATION) demonstrates the exact point of failure and
both candidate identity mechanics. Option A is mechanically
feasible with machinery that already exists; the design below
adds ONE additive field, ONE Program-level bridge surface, and no
new authority. Uni's recommendation: recorded-mapping binding
(S1), minted lazily at first bridge use, with the canonical Idea
as a title-only identity shell (§2).

## 1. Current-state census (evidence)

### 1.1 What a Plane unit is today

- Representation: `Unit` dataclass, form/dell_matrix/plane.py:48-62:
  id, label, words, detail, goals, skin, x, y, sandboxed,
  sandbox_id, manifest, parents, origin, lineage_version. There is
  NO lifecycle state and NO history on the unit: it exists or it
  has been removed. `parents` is LINEAGE (derivation), assigned
  only via lineage.assign_lineage inside Plane.place
  (plane.py:96-133); lineage is not containment (sleep-run census,
  re-verified).
- Identity: caller-supplied string, minted by exactly one
  canonical authority — form/idea_create.py:82-110 (slug_id:
  label slug, ≤40 chars; unique_unit_id: per-Plane `_n` dedup,
  per-door prefixes). Two minting doors matter: direct creation
  (Dell 8 [Create] / Program.place, open.py:1087) and Nursery
  confirmation, which places the unit UNDER THE PROPOSAL'S ID
  (confirm_lineage.py:221-222) — identity is continuous from
  PENDING proposal to live unit. Probe-verified live at this base
  (probe_bridge_gap.log: `bathroom_3098` proposal → unit of the
  same id, via the REPL's human-approval route, repl.py:2641-2644).
- Lifecycle: creation via Plane.place / Program.place
  (spatial-authority coordinates, open.py:1087-1136; auto-boxing
  may apply); mutation is in-place and unversioned (move,
  set_skin, set_detail, set_goals — plane.py:148-174); grouping is
  Sandbox (flat member_ids, box/unbox, plane.py:176-201 —
  isolation, not nesting); deletion is Plane.remove
  (plane.py:139-146: unbox + delete; lineage references in other
  units are NOT rewritten). Plane also carries VIEW state
  (perspective, zoom_target, focus — plane.py:203-215) that is
  navigation, not structure.
- Persistence: units serialize explicitly into the per-owner
  program file (form/persist.py:166-189, 265-268 →
  form/state/program_<owner>.json, checkpoint copies alongside).
  Restore is Program.load → persist load (the REPL's path,
  repl.py:1581) and the blank-cube restore re-places each unit
  with restore=True (blank_cube.py:61). Probe-verified asymmetry:
  Program.load restores unit ids exactly; a fresh Program(owner)
  construction does NOT restore plane units (welcome seed only),
  while the Nursery DOES auto-load in __init__ (open.py:258). A
  binding stored in the unit record inherits the unit record's
  exact save/load/checkpoint semantics — no new behavior.

### 1.2 What a canonical Idea is today

- Representation: form/mandell/idea.py — stable id
  (`Idea.__init__`, idea.py:202-203: caller-supplied id OR a fresh
  UUID), versioned properties, a 9-state lifecycle
  (LifecycleState, idea.py:33-43: ACTIVE, FADED, SUPERSEDED,
  PROPOSED, ACCEPTED, REJECTED, ARCHIVED, DELETED, RESTORED),
  bitemporal history, provenance, change events. The Idea carries
  NO nesting state by design (grep: zero hits; probe-verified).
- Persistence: per-owner directory form/state/ideas_<owner>/, one
  file per Idea (idea_persist.py:28-37: `idea_<safe>_<sha16>.json`),
  atomic writes, fail-closed load with id-vs-content verification
  (idea_persist.py:48-97).
- Containment: SemanticGraph (form/mandell/semantic_graph.py),
  the single edge store. CONTAINS invariant: at most one ACTIVE
  containment parent per child, no self-containment, no cycles
  (type-level, Phase-2 law). API: nest (L985, idempotent for the
  same parent; a different second parent is refused — reparent
  required), unnest/promote (L1011, supersedes the edge, identity
  untouched), reparent (L1029, atomic supersede+activate, one
  save). Queries: parent/children/live_children/ancestors/
  descendants/breadcrumb/is_top_level/roots (L1076+). Persistence
  is an append-only per-owner relationship log
  (graph_<owner>.json) with a fail-closed journal; current state
  is a deterministic fold. Graph position never defines identity.
- Two graph laws the bridge inherits verbatim: (a) EVERY
  relationship endpoint is gated on the Idea EXISTING
  (_gate_endpoints, semantic_graph.py:867-871, called by nest) —
  the graph refuses to relate ids that have no persisted Idea;
  (b) Idea lifecycle transitions do NOT create, modify, or remove
  graph edges (explicit composition rule, semantic_graph.py
  comment at L1076-1090) — edges are historical facts; live views
  compose lifecycle themselves (live_children is the provided
  convenience). Structure propagation (_propagate_structure)
  touches only DEPENDS_ON count-derivations and records partial
  failure explicitly as FAILED; a plain CONTAINS nest does not
  rewrite the Idea's own properties.

### 1.3 Exactly where the two systems fail to meet

- NO binding exists in either direction: no unit field names an
  Idea; no Idea names a unit; Program contains no save_idea /
  load_idea call and no graph mutation surface. Program's only
  graph use is a READ-ONLY SemanticGraph.load for RingedGrowth
  coherence (open.py:1292-1293), which scores proposal pairs AS IF
  their ids were canonical ids — for real owners the graph is
  empty, so the signal is the defined neutral 0.0 ("no graph
  evidence"), honestly. No de-facto aliasing exists in production.
- The failure is live and exact (probe, this base): on a fresh
  throwaway owner with units `house`/`rooms` placed,
  `SemanticGraph.nest("rooms", "house", HUMAN)` raises
  GraphInvariantError: "relationship source house is not an
  existing idea". The graph's own endpoint gate makes a
  graph-node-only binding (unit ids as bare graph nodes)
  IMPOSSIBLE: containment requires persisted Idea records for
  both endpoints. Any honest bridge must mint Ideas.
- User-visible operations today: Plane side — place/create,
  confirm-from-Nursery, move/edit, box/unbox, remove, zoom,
  lineage inspection (REPL `lineage <id or label>`), Studio
  canvas/store views. Canonical side — nest/unnest/reparent and
  the navigation queries are reachable ONLY from Python
  proofs/tests (caller census: exclusively p2_* proofs; no REPL
  command, no Dell, no GUI surface executes nesting).

### 1.4 Persisted-state census (all worktree state, read-only)

Method: census_state.py scanned every ~/workspace/*/form/state
(11,745 owner keys — overwhelmingly test/campaign owners, counts
aggregate per-owner copies across worktrees; full dump in the
circuit's working files, compact extract in the evidence bundle).
Findings:

- 9,156 owner keys hold Plane units (21,799 unit records in
  aggregate); only 28 owner keys hold ANY canonical Ideas (205
  total); only 3 owner keys hold both — R3AUTH and the r63a
  rollback-replay rigs, all test state, none of them bound (their
  Ideas are unconnected test artifacts) and none with a CONTAINS
  edge.
- Across ALL persisted graph logs: 54 relationship entries total,
  of which 16 are `contains` — EVERY one under Phase-2 proof
  owners (P2D, P2DBG*, P2ROOT, P2SMOKE). No owner that runs the
  live program has a single containment edge.
- The default user owner ("Operator") holds units (the welcome
  seed and a handful across copies), ZERO canonical Ideas, ZERO
  graph entries.
- Canonical ids in the wild are mostly UUIDs, but non-UUID
  explicit ids already exist (r63a rigs: 7) — the canonical
  namespace is NOT UUID-exclusive today. (Load-bearing for §2/S2.)
- Evidence hygiene note: the first census pass read the graph
  log's wrong key (`entries` instead of `relationships`) and
  reported 0 CONTAINS; the count was re-run with the correct key
  before any design weight was put on it (graph_type_census.log).
  The corrected numbers above are the only ones this packet uses.

### 1.5 What Studio / nodes_payload exposes today

- Program.nodes_payload (open.py:419-445) emits per unit: id,
  label, words, detail, goals, skin, x, y, z (derived), sandboxed,
  score. NO parents/lineage, NO origin, NO binding or containment
  field (probe-verified key list). Its consumers are spatial/score
  machinery (vision, forces, gravity, verita) plus the Studio.
- Studio's Growth view does NOT consume nodes_payload today:
  gui/server.py:219-229 (_growth_payload) fabricates nodes from
  growth-lens PLANTS ONLY (ids `plant-<n>`), returns empty when
  there are no plants, and only then applies filter_nodes_for_room
  (form/dell_matrix/view_rooms.py:79). This is Studio Gap 3 —
  verified still open at this base by direct read. It is a
  SEPARATE defect: this plan notes the interaction (§6) and does
  not design its fix.

## 2. Identity model

The binding question decomposes into WHERE the mapping is stored
and WHEN the Idea is minted. Three storage strategies were priced
against identity stability, history preservation, lifecycle
independence, and the sole-authority law; mint timing is priced
separately below.

### S1 — Recorded mapping: additive field on the Unit (RECOMMENDED)

The Unit gains one additive optional field (working name
`idea_id: Optional[str] = None`) carrying the canonical Idea's
UUID. The Idea is minted as an IDENTITY SHELL: title from the
unit's label at mint time, provenance recording the bridge mint;
NO unit content (words/detail/goals) is copied — content truth
stays on the Plane, structure truth stays in the graph, the Idea
is the identity anchor and the home of canonical lifecycle/
history for structure events.

- Identity stability: the mapping is explicit and survives
  save/load/checkpoint/rollback WITH the unit record (single
  existing fail-closed persistence path — persist.py serializes
  units explicitly, so the field rides the same atomic write;
  no cross-file consistency window for the pointer itself).
- History preservation: binding is born with the unit record and
  is checkpointed with it. The reverse direction (Idea → unit) is
  DERIVED at load by scanning units — never stored, so it can
  never diverge.
- Lifecycle independence: a unit exists unbound (idea_id=None) —
  the normal state of every unit today. An Idea exists without a
  unit (the entire canonical universe today). Unit removal
  deletes the pointer with the record; the Idea and its graph
  edges remain as canonical history, per the graph's own
  lifecycle composition law (§1.2b). Rollback of the program to a
  generation where the unit was unbound leaves the minted Idea
  ORPHANED (unreferenced) — orphaned history, census-detectable,
  never a dangling live pointer, because liveness is defined by
  the unit record alone. Re-binding after rollback mints a FRESH
  Idea; the unit's canonical identity changes across that
  rollback+rebind — named here as a known boundary, not hidden.
- Sole authority: the field is a POINTER, not a containment copy.
  Nothing about containment is stored on the Plane; all
  containment reads resolve through SemanticGraph at read time.

### S2 — Shared identity: Idea minted with id := unit id

Mechanically proven possible at this base (probe: an Idea minted
with idea_id=<proposal slug> nests by unit id). Zero mapping
state; graph queries take unit ids directly; RingedGrowth
coherence would start resolving unit/proposal ids.

Rejected, for four reasons: (1) Namespace conflation — unit ids
are lossy label slugs (≤40 chars, `_n` dedup decided by
Plane-local state); making Plane naming decisions define
canonical identity inverts the layering (the graph's law is that
position never defines identity; S2 makes a LABEL derivation
define it). (2) The canonical namespace is not clean: non-UUID
explicit ids already exist in persisted canonical state (§1.4),
so a slug collision with a pre-existing unrelated Idea is a real,
if small, class — S2 would silently MERGE two objects' histories
under one id. (3) Silent influence change: RingedGrowth's
graph_coherence (a proposal-ranking tie-break signal) would
activate for unit ids without any consumer review — STORED would
become USED by accident, against the information-influence law.
(4) Renames/relabels and the `_n` dedup make the canonical id
depend on the order units happened to be created — an identity
that encodes creation accidents.

### S3 — Separate append-only bridge log

A third per-owner artifact recording bind/unbind events with
provenance, folded like the graph log.

Rejected for v1 (kept as the documented fallback if binding
HISTORY is ever ruled a first-class requirement): it is the only
strategy whose state can diverge from BOTH stores it joins —
program checkpoint/rollback restores the unit universe but not
the bridge log (and vice versa), manufacturing half-bound states
as a routine outcome of a supported operation. It also builds a
second journal/fold machinery beside the graph's, to record a
mapping that S1 carries for free inside an existing atomic write.
Its one genuine advantage — a provenance history of binding
events — is partially recoverable under S1 from the Idea's own
provenance/change events (the mint is recorded canonically).

### Mint timing (sub-decision of S1)

- EAGER at creation (every place/confirm mints): rewrites every
  creation door (Create Dell, confirm, import, restore, dev
  loops) and forces a failure-semantics decision onto the
  sovereign creation step (may Create fail because a mint
  failed?). Rejected.
- EXPLICIT-ONLY (a bind op the user must run first): honest but
  makes every first nest a two-step ceremony; kept as part of the
  surface (bind is inspectable) but not the only path.
- LAZY at first bridge use (RECOMMENDED): nest/promote/reparent
  on an unbound unit binds it (and its counterpart) first, as
  part of the same operation, with the mint ordered before the
  graph append (§3). Creation paths are untouched; every existing
  unit is bindable on demand; "migration" dissolves into a
  per-unit idempotent protocol (§3) instead of a bulk event.

RECOMMENDATION: S1 + lazy minting, with an explicit bind op for
inspection. Questions Q-TD1/Q-TD2 put both choices to the
Director as his ruling points.

## 3. Migration design

Under S1 + lazy minting there is NO bulk migration event. The
migration is three separately reviewable parts:

(a) SCHEMA step (the only state-format change): the additive
Unit field. Legacy program files load unchanged (missing field →
None), following the project's proven additive pattern (Nursery
Proposal records load legacy files by the same default-fill
mechanism, nursery.py:84-145). The field must round-trip through
EVERY unit serialization path: persist.py's explicit unit dict
(L167-182), the blank-cube restore (blank_cube.py:61), and the
checkpoint/generation machinery — TD-1's contract (§5) tests each
path by name, because a field that survives save/load but drops
out of a checkpoint restore would manufacture unbound-after-
rollback units silently.

(b) BIND protocol (per unit, idempotent, ordered for failure):
  1. If unit.idea_id is set and idea_exists(it) → already bound;
     return it (no-op).
  2. If unit.idea_id is set but the Idea is MISSING → half-bound
     state H1: the op REFUSES and reports (never silently
     rebinds — a missing canonical record is a persistence
     integrity event, and quiet repair would hide it).
  3. Otherwise mint the shell Idea (fresh UUID), save_idea FIRST,
     then set unit.idea_id, then the program's normal save. A
     crash between save_idea and the program save leaves an
     ORPHANED shell (no pointer exists) — harmless, census-
     detectable, and the next bind simply mints again. The
     pointer is written LAST, so no ordering produces a dangling
     pointer from a live unit to a never-saved Idea.
  Bind is a Program-level operation with HUMAN provenance; it is
  never performed by load/restore paths (fail-closed load law:
  loading must not write).

(c) OPTIONAL bulk bind: if the Director wants existing owners'
  units bound in bulk, that is a separate explicit command
  circuit (TD-4, §5) — per named owner, dry-run census first,
  never a load-time side effect, never across the test-state
  sprawl (21,799 aggregate unit records are mostly rigs; bulk
  binding them would mint thousands of shells for dead tests).

Verification model (any circuit that binds): per-owner census
before/after — unit count, bound count, orphan-shell count (Ideas
in ideas_<owner>/ referenced by no unit AND not part of the
pre-existing canonical set), spot identity checks (bind a named
unit, reload via Program.load, confirm the same idea_id; nest,
reload the graph fresh, confirm breadcrumb by unit label).
Fail-closed properties: H1 (pointer to missing Idea) and its
mirror H2 (a shell minted by the bridge for a unit that no longer
exists — indistinguishable from rollback orphans; treated as
history, never auto-deleted, because canonical history is not
the bridge's to erase) are both ENUMERATED states with defined
handling, not surprises.

## 4. Operation surface

Home: Program (form/open.py) gains the bridge methods — Program
is the live program's authority, already owns the Plane, the
Nursery, and the read-only graph load (open.py:1292-1293). The
bridge extends existing authorities only:

- SemanticGraph — UNCHANGED. All containment mutation goes
  through nest/unnest/reparent with Provenance(source=HUMAN,
  activity naming the surface). Its gates, journal, and fold are
  the containment truth.
- idea_persist — UNCHANGED. Shell minting is save_idea of a
  constructed Idea; nothing else.
- Plane — ONE additive field; NO containment methods, NO children
  structure, NO cached parent/children anywhere on the Plane.
- Program — NEW bridge surface (working names): bind_unit(id),
  nest_units(child_id, parent_id), promote_unit(id),
  reparent_unit(id, new_parent_id), containment_view(id) → a
  DERIVED read (unit's parent/children/ancestors/breadcrumb
  resolved via binding + graph queries, composed with unit
  existence and Idea lifecycle — the live_children composition
  pattern), binding_census() → bound/unbound/orphan counts.

Semantics the ops must honor: lazy bind of BOTH endpoints inside
nest/reparent (bind order before graph append; a graph refusal —
cycle, second parent — leaves the bindings in place: bound-but-
unnested is a normal state, not an error residue); ops refuse on
H1; ops compose Idea lifecycle honestly — the graph gates only on
existence, so the BRIDGE decides lifecycle policy (proposed v1:
nest/promote/reparent refuse when either endpoint's Idea is
DELETED, with the refusal named; ARCHIVED/FADED are posed as
Q-TD4); sandbox interplay — proposed v1: nesting is refused
across a sandbox boundary and for sandboxed units (sandbox is
isolation; containment crossing it would leak structure across
the isolation line) — posed as Q-TD7.

First user surface: REPL commands over unit labels/ids (the
`lineage` command is the precedent — users hold unit ids, never
canonical ids), so nest/promote operate on UNIT ids and resolve
bindings internally. A Dell verb is NOT proposed for v1 (making
containment seed-executable is a scope expansion with its own
contract questions). Studio consumption comes through the derived
read model only (§6).

FORBIDDEN, by design: any Plane-local containment store or cache
(including a persisted nodes_payload); any graph write except
through Program bridge methods; any cross-owner binding (graph,
ideas, and program files are all per-owner; a nest whose
endpoints resolve under different owners is refused); any
unbind/delete of a canonical Idea by the bridge (the bridge
never erases canonical history); binding of Nursery proposals
(PENDING records are not units; containment accepts live units
only).

## 5. Sequencing — bounded circuits for separate authorization

- TD-1 BINDING FOUNDATION. Schema + bind only, no containment.
  Adds the Unit field end-to-end (dataclass, persist
  serialization, blank-cube restore, checkpoint round-trips),
  Program.bind_unit + binding_census, REPL-visible binding state
  (read-only). Contract: legacy state loads byte-equivalent
  semantics; bind is idempotent; crash-ordering probe (kill
  between mint and program save) yields an orphan, never a
  dangling pointer; H1 refusal proven; ZERO graph writes.
  Riskiest assumption: the field survives EVERY restore path
  (checkpoint, generation rollback, confirm compensation).
  Cheapest falsifier: a round-trip probe scripted over each
  restore path the confirm_lineage machinery enumerates.
- TD-2 CONTAINMENT OPS. nest/promote/reparent at Program level +
  REPL surface, lazy binding inside ops, provenance HUMAN.
  Contract: the grounding probe's scenarios re-run THROUGH UNITS
  (3-deep nest, breadcrumb by label, promote preserves unit AND
  Idea identity, second-parent refusal demands explicit
  reparent); sandbox-boundary and H1 refusals proven; a removed
  parent unit leaves graph history intact while the live view
  composes it away. Riskiest assumption: two lazy mints + one
  journaled graph append compose into an operation whose failure
  modes are all in the enumerated set. Cheapest falsifier:
  fault-injection between each pair of steps (mint A / mint B /
  append) with state census after each kill.
- TD-3 PERSPECTIVE NAVIGATION. Derived containment in
  nodes_payload (computed at read, never stored), Plane render
  breadcrumb for a zoomed contained unit, REPL navigation
  (breadcrumb/children by label), Studio Growth consumption.
  PREREQUISITE DECISION: Studio's Growth payload defect (Gap 3)
  must be fixed for Studio to consume ANY node payload — either
  as its own prior micro-circuit (TD-3a) or sequenced before
  TD-3's Studio leg; the REPL/Plane legs do not depend on it.
  Riskiest assumption: derived-at-read stays consistent with the
  graph fold under the program's single-process mutation model.
  Cheapest falsifier: payload-vs-graph differential probe after
  each op in a scripted nest/promote/reparent sequence.
- TD-4 (OPTIONAL, Director's call — Q-TD9) BULK BIND for named
  existing owners: explicit command, dry-run census, per-owner.
  Riskiest assumption: named-owner scoping actually excludes rig
  state. Falsifier: dry-run output itself.
- TD-5 (LATER, separate ruling) Exchange containment travel and
  any dock/learning consumer of containment (§6) — NOT part of
  the v1 line.

Each circuit: failing-first suite, mutants, regress ×3
sequential, exact-head CI, fresh clone, certification stop —
the standing closure discipline.

## 6. Interactions

- Studio Growth + Gap 3: Gap 3 (gui/server.py:219-229, plants-
  only payload) is independent of the bridge, but the bridge's
  read model should land in nodes_payload — the ONE node
  projection — so the growth lens, Studio, and spatial consumers
  all read the same derived shape. Until Gap 3 is fixed, Studio
  honestly shows planted ideas only; the bridge must not be
  demoed through a fabricated Studio payload.
- Inference dock: proposals stay PENDING and UNBOUND; dock verbs
  (comprehend/relate_field) neither bind nor nest. Confirmation
  creates the unit (identity = proposal id); binding remains
  lazy from that moment. Containment context enriching
  relate_field is a FUTURE consumer question (TD-5), not v1 —
  dock output remains proposals under the sovereign gate.
- DuoBeta / learning: containment is STRUCTURE, not learning.
  Bridge ops are user acts; their receipts (if surfaced through
  seeds) are OBSERVED records. Nothing in the bridge writes to
  DuoBeta, outcomes-as-learning, or any LEARNED state — the
  OBSERVED ≠ LEARNED separation is untouched. One DISCLOSED
  signal interaction: RingedGrowth's graph_coherence reads the
  graph with canonical ids; under S1 it stays neutral for
  proposal pairs (proposal ids ≠ Idea ids), so the bridge does
  NOT silently change proposal ranking. Making coherence
  binding-aware is a separate consumer change requiring its own
  review precisely because it is an influence path.
- Exchange: v1 packets carry proposals + receipts (build_packet
  over a proposal id, exchange.py:235); containment is not in
  the packet format and does not travel. An imported proposal
  confirms into a LOCAL unit with NO binding and NO foreign
  edges; if its label later nests, it binds locally like any
  unit. Whether Ideas-with-containment should ever travel —
  and what receipts would carry (a CONTAINS edge is a claim
  about two identities the receiver may not hold) — is Q-TD6,
  deferred to TD-5 by design.
- Symbiosis/composition: containment adds a relation the
  9,900-pair ledger never classified. This plan claims nothing
  about pair reclassification; any symbiosis consequence is
  downstream evidence work, not a bridge design input.

## 7. Risks and anticipated probes

Anticipated Director probes, with the design's answers:
- "Show me the second authority." There is none: containment
  bytes exist ONLY in graph_<owner>.json; the unit field is a
  pointer; every containment read resolves through the graph at
  read time; nodes_payload containment fields (TD-3) are derived
  per call and never persisted.
- "Where does history die?" Unit removal (pre-existing behavior)
  and nowhere in the bridge: the bridge never deletes Ideas,
  never supersedes edges except through graph ops, and treats
  orphans as history. Program rollback can orphan shells —
  enumerated, census-visible, not silent.
- "Identity collision." S1 mints fresh UUIDs into a namespace
  the graph already keys on; unit slugs never enter the
  canonical namespace (that was S2, rejected with the persisted
  non-UUID precedents cited).
- "Partial migration / half-bound states." H1 (pointer without
  Idea) refuses-and-reports; the mint ordering makes dangling
  pointers unreachable by construction and leaves only orphan
  shells, which are inert. The kill-between-steps probe is in
  TD-1/TD-2 contracts, not left as a promise.
- "Load-time surprises." Nothing binds at load; restore paths
  are read-only for the bridge. A state file from before TD-1
  and one from after differ by one optional field.
- "The welcome unit / rig state." Lazy binding treats every
  unit uniformly; nothing is bound until a user nests it, so
  the seeded welcome unit and all rig state stay unbound unless
  acted on.
- Fractal claims: NONE. The graph gives arbitrary-depth trees;
  no recursive/self-similar semantics are claimed anywhere in
  this plan (per the grounding's UNESTABLISHED classification).

Residual risks accepted by the design: (R1) the Idea shell's
title is a mint-time snapshot — a unit relabel makes the shell's
title stale (the shell is an anchor, not a mirror; consumers
must read labels from the Plane). (R2) Two Programs open on one
owner (the standing multi-instance state hazard) can race a
lazy bind exactly as they can race any program save today —
the bridge adds no new class here, and Nursery-style disk-sig
conflict detection is NOT extended by v1. (R3) Derived reverse
lookup (Idea → unit) is a scan; at current unit counts this is
trivially cheap, and it is a read model, not a store.

## 8. Questions for the Director

- Q-TD1: Binding strategy — approve S1 (recorded mapping, field
  on the Unit, fresh-UUID shell)? S2 and S3 are priced and
  rejected in §2; if either is preferred, the circuit order in
  §5 changes materially.
- Q-TD2: Mint timing — approve LAZY minting at first bridge use
  (with an explicit bind op for inspection), over eager-at-
  creation or explicit-only?
- Q-TD3: Shell content contract — approve title+provenance ONLY
  (no content mirror), so content truth remains Plane-side?
- Q-TD4: Lifecycle coupling — confirm the graph's existing rule
  as bridge policy (edges are history; unit removal never
  rewrites them), and rule the bridge's op policy for non-ACTIVE
  Ideas: refuse on DELETED (proposed), and on ARCHIVED/FADED —
  refuse, or allow as history-preserving ops?
- Q-TD5: Half-bound H1 (unit points at a missing Idea) —
  refuse-and-report (proposed), or authorize a sovereign
  `rebind` op in TD-2 that mints a replacement shell and records
  the substitution in the new shell's provenance?
- Q-TD6: Exchange — confirm containment travel is OUT of v1
  scope (deferred to a TD-5 ruling), including the case where
  both endpoints of a nested pair are exported?
- Q-TD7: Sandbox boundary — approve v1 refusal of nesting for
  sandboxed units and across sandbox boundaries, or rule a
  different composition between isolation and containment?
- Q-TD8: First user surface — approve REPL-first (TD-2), Studio
  consumption in TD-3 after the Gap 3 prerequisite decision
  (TD-3a as its own micro-circuit, or folded into TD-3)?
- Q-TD9: Bulk bind — skip entirely (lazy only, proposed), or
  authorize TD-4 as an optional later circuit for named owners?

## Evidence

In-PR bundle: director-reports/evidence/track-d-bridge-plan/
- probe_bridge_gap.py + probe_bridge_gap.log — live probe at
  base 2740c22, INTEGRATION (public Program API + canonical
  authorities driven directly; NOT a user path, NOT
  cross-process): 16/16 PASS, throwaway owner, exact cleanup
  (0 state entries remain).
- census_state.py + census_summary.json — persisted-state
  census (compact extract; full dump retained in the circuit's
  working files). graph_type_census.log — the corrected
  relationship-type count.
- carryover_diff.log — byte-identity of all Track D layer files
  from the sleep-run grounding base (b6dd46b) to this base.
- MANIFEST.sha256 — digests of the bundle files (the manifest
  does not list itself); sha256sum -c verifies cleanly.
Sleep-run grounding: hidden_files/track_d_grounding/GROUNDING.md
(probe 19/19, p2_graph_test 61/61 at b6dd46b) and
BRIDGE_DESIGN_GROUND.md (the design questions this packet
answers), both carried as hypotheses and re-verified here.
