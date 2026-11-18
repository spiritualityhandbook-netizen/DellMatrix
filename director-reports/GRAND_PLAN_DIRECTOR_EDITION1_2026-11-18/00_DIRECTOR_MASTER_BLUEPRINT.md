# THE GRAND PLAN — DIRECTOR DESIGNED EDITION 1
## Architecture, product law, scope, and phase gates

**Authority:** Ace / Overseer. **Author and designer:** Director. **Independent design challenger:** Uni. **Independent evidence checker:** Keeper. **Product implementation and merge actor:** Uni.  
**Design base:** merged main a8786f9c40cdeaaa8fe9ebeb6705a64d52490269, 2026-11-18. **Earlier planning source:** PR #421 at 35d3acd94f91173e28542bdf8575aa4df0e75693. **G2 update checked main:** b73b1d29ce25f33575f7f70d86e278ea0bd0d1ba; merged #420/#433 and FI-010..019 addendum in file 09. Original source-pin is retained as a dated design baseline, not falsely called current main.  
**Artifact status:** complete AUTHOR PROPOSAL, not yet Uni-checked, Keeper-certified, Ace-adopted, or product implemented. Draft PR only. It supersedes the *delegation of planning work* in Director comment 6977643158: Director authors; Uni checks. It does **not** supersede any standing production authority, hold, or completed record.

## 0. Why this edition exists

The previous unified plan reconciled five historical plans, but it was built from an older work-list render and older code. It described a 224-active-item model without an accepted current-main one-to-one crosswalk; some claims now lag actual code. The living blueprint preview was sixteen sampled records, not an audited live system. This edition supplies the missing architecture and executable circuit design itself. Uni is to verify, challenge, and implement *after* the appropriate gates, not invent the plan.

**Standing source truth:** live generated Master Work List has 185 numbered records, three SANDBOXED and therefore 182 active, 39 COMPLETE, 54 PARTIAL, 86 OPEN, three GATED. This is the published 39/182 = 21.4% baseline, not proof that every latest merged change is credited. Source JSON is snapshotted without status mutation in 01_SOURCE_CROSSWALK_CANDIDATES.json. The old PR #421 formula becomes 185 - 3 sandbox - 4 proposed aliases + 49 proposed additions = **227 candidate active**, NOT an adopted new denominator; new MWL-183/184/185 and newer changes may overlap additions. The original 224 and modern 227 are both candidate accounting, not SCOREBOARD. Never promote either by arithmetic alone.

## 1. Target product: one fractal idea world, not a suite of disconnected screens

The product has five interacting layers:

1. **Meaning:** one canonical owner-bound Idea per identity, with text, detail, goals, provenance, lifecycle and typed associations. A child Idea remains a distinct object; parent containment is a typed semantic edge. Promote a nested Idea to a root by a checked graph operation, not by copying its text or destroying its links.
2. **Action:** English/LatinMandell/Mandell seeds resolve into typed Dells; each executable Dell has declared preconditions, effects, failures and a receipt. Unsupported functionality refuses visibly. No guessed interpretation can mutate state.
3. **Space:** the Plane stores a projection of canonical identities and positions; SpatialAuthority decides position changes. Rooms, boxes, Flower, Tree, cloud, star, page, map and window are interchangeable perspectives or explicitly typed containers. No perspective becomes a second semantic source of truth.
4. **Growth:** resonance/harmony derive candidate connections from admitted evidence. Generated candidates enter Nursery PENDING by default. An AI, persona, Psalm, DuoBeta, agent or workflow may suggest, rank, draft or simulate, but never gain human acceptance authority merely by participating. Any **future** strict automatic confirmation is a previously human-configured and receipted Nursery gate under FI-011 after its own authority review, not an AI acting as human.
5. **Witness:** Studio, Console, Muse Space, visual perspectives, reports and outside bridges show exact source, scope, time and evidence. The local/offline engine remains useful without an external AI or network.

**User acceptance scenario:** create an Idea, add goals/details, nest under another Idea, promote it to an independent root without breaking its family, fade a detail while preserving history, discover a cross-Idea proposal, inspect its reason, choose confirm/reject and correct placement, reload and find exactly the same identities and relationships from a different perspective. Repeat once with an AI absent; once with an AI providing suggestions only; once under interrupted saves. A user-visible claim of completion requires all three categories of proof, not screenshots.

## 2. Eleven houses: ownership and concrete closure

| House | Responsibilities | Authority and closure proof |
|---|---|---|
| H1 Spine | Registry of addressed Dells, parser/AST, typed signatures, English↔LM, control and effect dispatch | One matching contract per 00–99 address; typed/legacy equivalence, explicit refusal, deterministic execution receipt |
| H2 Field | Idea identity, SemanticGraph containment and associations, Plane Unit binding, room/sandbox membership | ID stability, no dangling/cyclic containment, no inferred relationships from co-location; cross-load check |
| H3 Body | Perspective-independent idea representation, skins, avatars and projections | Each view reads canonical ID; view switching does not alter meaning/ownership |
| H4 Forces and witnesses | SpatialAuthority, gravity/weather, resonance, harmony, Verita and evidence | Mathematics admitted separately; active/faded participation rules; every output names input and authority |
| H5 Gate and growth | Nursery, Lens, search/organization, confirmation, revisions, human gates, DuoBeta | No unreviewed suggestion becomes confirmed; owner-scoped atomic save and retry behavior |
| H6 Senses and dynamics | Measurements, Tree/Flower geometry, Chord, Nerve, temporal/spatial readings | Derived value with units, provenance, assumptions, falsifier; no causal or semantic upgrade from geometry |
| H7 Memory | Owner state, journals, checkpoints, rollback, outcome evidence, snapshot and action histories | Exact generation identity; crash/restart paths; no hybrid save; explicitly distinct histories |
| H8 Doors | REPL, host/API, dock, Exchange, Bridge, room boundaries, offline/provider adapters | Exact permission at every boundary; timeout, retry, fail-closed, no foreign mutation |
| H9 Surfaces | Studio, Console, rooms, Nursery cards, five pages, Muse Space | Public-path parity; navigation and accessibility; no phantom live actors, no fabricated nodes |
| H10 Instruments | Tests, regression, CI, performance, profiler, error/coverage and certificate records | Failing-first, source+runtime proof, precise head, 3-leg campaign where stateful, merged-main confirmation |
| H11 Archive | Superseded plans, terminal decisions, rejected proposals, retired code and evidence | Historical facts immutable and navigable; history is not a second live-state authority |

**Dependency:** H1/H2/H7 are the unbreakable spine. H4/H6/H5 consume that spine. H8 gates external actions. H3/H9 present it. H10/H11 measure and preserve truth. A feature spanning houses must name *one* canonical writer and all read-model consumers.

## 3. Canonical data and mutation constitution

**Idea:** identity belongs to canonical Idea; lifecycle is ACTIVE, FADED (history retained; excluded from active inference/forces), or SUPERSEDED (successor relation and prior value recoverable). Do not claim these exact enums exist in each current module until checked; they are the desired semantic states. Never use label, screen coordinate or appearance as identity.

**Containment:** SemanticGraph CONTAINS is at most one active parent per child, with no cycles; association, lineage, dependence and references are distinct edge types. Promotion removes/changes the containment edge with a journal, retains separate lineage/association edges, and preserves object ID.

**Projection:** Plane Unit carries the canonical idea_id pointer. SpatialAuthority alone decides movements after placement. A unit without an Idea pointer cannot silently present itself as a canonical Idea; an Idea without a Plane unit must remain discoverable in semantic/read-model views. A snapshot is an observation, not live identity.

**Proposal:** Nursery Proposal has its own proposal ID, owner, status and provenance. Pending is quarantined from canonical graph and resonance. Confirmation is an authenticated, typed, receipted operation; mixed-parent placement requires explicit selection; automatic confirmation defaults sandbox-first under existing policy. A rejected proposal is not erased merely to hide it from the UI.

**Transaction:** all mutation requests perform AUTHENTICATE → PARSE → RESOLVE → PREFLIGHT → VALIDATE FULL REQUEST → PREVIEW if appropriate → COMMIT THROUGH EXISTING CANONICAL DOOR → PERSIST/RECOVER → RECEIPT → DERIVED VIEW UPDATE. Failure before commit must leave durable and live state unchanged. No arbitrary multi-file atomicity claim: Program/Nursery pair-save remains a separate gated Q1 problem until its crash proof closes. For operations spanning that gate, prefer explicit refusal or staging, not an optimistic success.

**Operation receipt (design-level common envelope; reuse existing ledgers where possible):** operation_id, owner, actor_class, authority_grant_id (if any), input_digest, exact raw_operand_reference or explicit privacy-safe redaction, resolved typed AST, affected stable IDs, pre_generation, post_generation, per-field completeness/coverage, state_effect_class, result enum, specific refusal code, source/provenance, timestamp, code/contract version. External outward receipts must not leak protected content. This is a common *schema contract*, not permission to create a second persistence authority.

**Undo/history:** session action undo/redo and Core II snapshot/Revert are distinct today. Both must be represented honestly. Redo replays one action stream; new user writes invalidate the redo tail; no silent inverse eviction. Q-LC.1 landed but does not imply arbitrary room-wide undo or crash-durable action stacks. Durable evidence is separate from reversible action history. Never silently merge or duplicate histories.

**Failure contract:** success means the requested effect occurred exactly; a partial/substituted/dry-run effect is flagged as such. A missing data source is UNKNOWN/UNAVAILABLE, never false or empty by invention. Refusals are typed and non-mutating; failed writes preserve retry identity. Every hard limit either refuses with a named bound, explicitly announces a limited observation with total+continuation, or retains full admitted data. A test pin preserving misleading behavior must be challenged and intentionally re-pinned, not treated as an immutable product law.

## 4. The minimum real user experience (the product to certify)

**Five contexts:** Plane (world and perspectives), Nursery (proposals and organization), Dells (operations/meaning), Dell Playground (safe preview/training), Psalm Matrix (AI instances and their advisory permissions). A Console is an overlay/tooling view, not a sixth datastore. Preserve current Idea/path and owner context when moving among pages. Every item displays canonical identity or an explicitly labeled provisional/derived ID.

**Perspectives:** 2D SKY, room, Tree, cloud, circle, Flower, table, page, cube, sphere and later sonification read the same semantic state, with a local view transform. Different camera arrangements are permitted; semantic labels/status/links are not permitted to disagree. Empty state is empty, not a synthesized decorative Idea.

**Nursery primary decision surface:** full browse, search, topic/tags/cluster, Lens ranking, source explanation, pending/confirmed/rejected, explicit confirm/reject/modify, provenance, mixed-parent wall choice. Paginated views must expose item total, shown range, continuation, cursor-invalidated-on-generation-change, and filter/sort identity. Lens scores are transparent (0.40 LINK, 0.25 ACE, 0.20 FRESH, 0.15 NOVEL) and missing inputs are marked, not invented. Current C5 SEE/ORGANIZE/LENS implementation is real; this plan asks for completion and cross-surface verification, NOT rebuilding it.

**Human gesture contracts:** every gesture identifies what it changes, its undo/recovery path, and permission required. Dragging a projected unit requests a canonical spatial move; dragging a nested Idea in a semantic outline requests a graph reparent with a preview. These are different operations. AI suggestions enter pending drafts. Room and box scope labels cannot be used as a privilege grant.

**Offline:** local reading, creation, edit, tree/graph operations, safe simulation, search, pending review, save/load, and deterministic ranking work without AI. AI-required operations report PROVIDER_UNAVAILABLE and retain the draft/retry path. Bridges, embeddings and research are opt-in capabilities with explicit provider evidence.

## 5. The PLAN and CODE belts (do not mix them)

PLAN stages: INTAKE → SOURCE-PINNED → CONTRACT-DESIGNED → DEPENDENCIES-RESOLVED → UNI-CHALLENGED → KEEPER-CHECKED → AUTHORITY-ADOPTED.

CODE stages: ABSENT → FAILING-FIRST → BUILT → REGRESSION-READY → EXACT-HEAD-CI-PASS → KEEPER-CONFIRMED → DIRECTOR-AUTHORIZED → MERGED → MERGED-MAIN-CERTIFIED.

A PLAN gate is not a CODE gate. Neither PLAN readiness nor a merged PR awards MWL COMPLETE. One canonical work object may have multiple implementation slices, each with separate exact-head evidence, while still counting as one agreed work object for the scoreboard.

**Design closure rule:** an entry is EXECUTION-READY only when its user-observable contract, failure semantics, owners, test oracle, dependencies and decision authority are explicit. If a sovereign choice is pending, mark GATED_BY_ACE and provide a non-destructive, independently useful slice that does not depend on the answer. A fully written design may still be UNADOPTED.

## 6. Build ordering and concurrency

1. **P0 Integrity:** current source crosswalk, exact-main census, short silent-loss and false-success repairs, queue/ledger coherence. Fix first; no progress by hiding defects.
2. **P1 Dell Plan:** all 100 addresses audited. Prioritize predicate, control/Parallel, resonance and thin-spec elders; keep existing honest refusals until contract and provider exist.
3. **P1.5 Runtime X11:** dynamic reachability, real owner/writer census, independent second-seat review; do not confuse static no-importer with dead code.
4. **P2 Language and state:** English/LM typed role equivalence, Idea/graph/Plane binding, Q1 crash-safe persistence, histories, lineage, Exchange.
5. **P3 Spatial/Tree:** Keeper FCC fixture reproduction then Director mathematical admission; geometry-only scaffold before any real-content semantics.
6. **P4 Resonance/Nursery:** evidence-backed pair scoring and proposals, Lens SEE/ORGANIZE completeness, acceptance, DuoBeta/learning.
7. **P5 HCN R3:** reproduce frozen architecture contract, then build orchestration against stable interfaces, no fabricated availability.
8. **P6 Dock/Psalm:** 12-dock inventory and provider adapters, real receipt/permission, human-gated suggestions, graceful offline.
9. **P7 Surfaces:** consistent Studio/Console, SKY/ROOM/Tree, Muse Space with all-source map and read-only sync mirror.
10. **P8 Grand Synchronization:** end-to-end public journeys, crash/fault/security, multiowner, two-device/portable-state and resource profiling.
11. **P9 Far Stratum:** only after P8 gates and any explicit scope promotion; research and generated estimates remain labeled.

Sequence is a dependency DAG, not a requirement to leave all unrelated lanes idle. Analyze independent packages concurrently; serialize shared-state campaigns, conflicting canonical writers and the sole Uni merge lane. Existing §32 freshness, current-main zero loss, exact-head CI, Keeper/Director role checks and all HOLD fences remain binding.

## 7. Completion conditions for the whole Grand Plan

The product is not complete when every available unit test passes. It is complete only when: (a) all adopted user-visible contracts have independently checked implementation and recovery, (b) all live user journeys can be performed without hidden steps or phantom outcomes, (c) no confirmed silent-loss/false-success/open authority bypass remains, (d) observed performance and offline behavior meet measured budgets, (e) current canonical registers and read models agree, (f) each out-of-scope future feature and every sovereign decision is explicitly named rather than implied implemented, (g) the merged-main final-check is performed and the Master Work List is regenerated under authority.

**Read next:** 01 machine crosswalk; 02 executable circuits; 03 decisions; 04 living Muse Space; 05 full 100-address Dell registry; 06 public journeys; 07 Uni review; 08 acyclic DAG; **09 FI-010..FI-019 intake (new G2); 10 G2 challenge dispositions (new G2)**. The original PR #421 file remains source evidence; this edition is a correction proposal until review.
