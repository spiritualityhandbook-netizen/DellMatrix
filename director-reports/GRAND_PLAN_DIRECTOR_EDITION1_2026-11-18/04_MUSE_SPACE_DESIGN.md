# LIVING GRAND PLAN BLUEPRINT / MUSE SPACE — DIRECTOR'S COMPLETE DESIGN
## Edition 1: evidence-backed planning world, not a decorative chart

**Original:** Edition 0 sample HTML, sixteen records and seven views, explicitly an incomplete preview. **New requirement:** an exhaustive navigable plan/implementation map fed by current canonical records, with honest evidence and pending edits. **Design status:** authored for Uni independent check, no code/build authorization from this file.

## 1. Purpose and boundary

The user can enter the Grand Plan as a navigable world: see what DellMatrix **is**, what it **should be**, which components are already real, how every plan object connects, what blocks a particular circuit, how progress is proven, and which part can be worked next. The application is a **witness and drafting surface**, not an alternate GitHub/Program source of truth.

Muse Space is not the product's canonical Idea graph unless Ace subsequently authorizes a typed import. It renders planning objects sourced from repository records. The ordinary user-facing Matrix's ideas and the planning world's work items are distinct typed objects; never implicitly place development tickets into the live Nursery of personal ideas.

## 2. Canonical input pipeline

Inputs, resolved at one pinned GitHub revision:

- Master Work List: master_work_list_items.json (185 rows, 182 active), its canonical generator and rendered Markdown.
- The current Grand Plan design, proposed #421 source, GP-G/FAR items and aliases.
- Dell registry 00..99 and dispatcher/contract coverage.
- SYSTEM-001 SYS-C01..C44 contract list (dated baseline) plus later scoped receipts.
- Director Review Queue, PR head/status, exact-head CI, Keeper/Director/Uni comments and merge receipts.
- Feature Intake FI-001..FI-009, Unknowns UU-1..15, DC-1..11, decisions, hold fences.
- Current runtime/census/test evidence and, where available, linked artefact hashes.
- Optional visual-perspective manifests and source-specified geometry fixture references.

**One snapshot reducer** produces a READ MODEL with fields: schema_version, github_snapshot_time, source_main_sha, source_blob_shas, retrieval_coverage, unresolved_sources, nodes, typed_edges, belts, contradictions, perspectives, derived_metrics. All facts use source refs; missing GitHub data yields EVIDENCE_UNAVAILABLE, never a fabricated stable count. The reducer is deterministic: same canonical source bytes and selection parameters → same content identity. It is read-only against GitHub; untrusted source text cannot control scripts or host permissions.

**Snapshot freshness:** static exported version carries the exact pin and is labeled AS_OF. Live connected view revalidates all sources and the remote main SHA; a changed main or PR HEAD marks affected evidence STALE until re-read. When offline, display the pinned snapshot and age; disable actions that require current authority.

## 3. Node schema and identity law

Nodes are typed, stable and namespace-prefixed:
- WORK: mwl:001..185, plus GP candidate IDs gp:g01, far:01, seq:x11.
- DELL: dell:00..99. Reserved addresses 100..999 are registered separately, never counted as active Core Dells.
- CONTRACT: sys:c01..c44 and future versioned contracts.
- COMPONENT: path-backed module/function with exact Git blob/line range.
- CIRCUIT: gp:e01..e28 and existing named circuits, with source identifier and version.
- DECISION: uu:01..15, dc:01..11, FI and Q-prefixed decision IDs.
- EVIDENCE: sha/blob, suite/CI run, test fixture, PR review/merge receipt.
- PR: repo + number + exact HEAD; branch HEAD changes create a new evidence version but keep PR stable ID.
- PERSPECTIVE: map, room, Tree, Flower, list, zoom, sequence.
- ACTOR/ROLE: Ace, Director, Keeper, Uni, docked Psalm, without exporting personal credentials.

Every node includes id, type, label, user-readable description, canonical_owner, status_domain, status, source URIs, source SHA, evidence_grade, last_reviewed_at, relations, dependencies, acceptance_contract, proposed_slices, measured_vs_projected, visibility/permission. **Never use a plain title as an identity.**

Status is **multidimensional**: PLAN readiness, CODE implementation lifecycle, CERTIFICATION scope, RUNTIME availability, RISK severity, and sovereign gate. A record can be PLAN_READY / CODE_PARTIAL / CERT_SCOPED / RUNTIME_OFFLINE at once. Status in one dimension never overwrites another or causes a count change.

## 4. Typed edge law

Allowed edge classes:
- IMPLEMENTS: code/component → contract/work item.
- REQUIREMENT_OF: contract → objective.
- DEPENDS_ON: circuit/plan → prerequisite.
- PRODUCES: operation/contract → receipt/output.
- EVIDENCED_BY: claim → immutable evidence.
- VERIFIED_AT: evidence → commit/run.
- BLOCKED_BY: circuit → active authority or missing-proof gate.
- ALIAS_OF: distinct labels → exactly same work identity, pending verified equivalence.
- SUPERSEDES: newer plan/version → older plan/version, preserving history.
- FEEDS: admissible output → named consumer contract.
- DISPLAYED_AS: semantic object → projection, explicitly not a semantic relation.
- REVIEWED_BY: specific head/scope → recorded checker disposition.

Each edge carries provenance and confidence class VERIFIED/INFERRED/PROPOSED. Inferred edges must never be included in canonical counts or executable dependency gates until a reviewer confirms them. The Connection Web can visualize inferred links with a distinct dotted style and source rationale; never promote by styling alone. Reject dangling refs, cycles where a DAG is required, conflicting aliases and role-free authority grants.

## 5. Seven working views, plus drill-down

**A. Blueprint Map.** Searchable, grouped hierarchy: 11 Houses → phase → work objects → contracts → modules → tests. Show every audited record, not sampled highlights. Selecting a card opens provenance, exact current status, last checked SHA, required actions, and connected objects. Graph labels have stable short IDs plus readable names. The map never implies everything is visible at once: viewport disclosure shows drawn/available.

**B. Two Belts.** Separate PLAN and CODE columns with independent denominators and a common work-ID join. PLAN counts adopted contract-complete items; CODE counts independently certified implemented items; the canonical MWL count stays displayed as its own strict number, not their average. A plan with no code must be visually clear; a merged code PR without post-merge certification remains uncredited. Do not display historical "242 PLAN / 198 CODE" as current unless independently re-derived from matching canonical inputs.

**C. Connection Web.** Interactive typed graph: change layout without changing nodes; inspect dependencies, overlap/collision risks, contradiction edges, bounded 2- and 3-component interactions; filter by verified vs proposed links. Reachable neighbors are paginated. If a graph links every Dell to another, it reports coverage counts and sampling, never claims tested compatibility.

**D. Sequence.** Phase-gated plan 0–9 with dependency-critical path and independent parallel lanes. Each lane shows next missing exact gate, expected concrete result, owner, and deferred work. The "next best" recommendation is deterministic over explicit dependencies/severity/available reviewer capacity, not a magic numerical priority.

**E. Sync Mirror.** Show contract CLAIM vs current CODE observation vs CHECKER evidence vs last merge vs visible STATUS. Classes AGREES / STALE / CONTRADICTED / UNVERIFIED / SOURCE_UNAVAILABLE. Examples: historical 35/224 compared with current 39/182; Core I/II registry 100 addresses versus plan label "99"; predicate infix false-success historical defect versus current explicit refusal; Nursery C5 implementation beyond old plan; DuoBeta R26 already merged. Each discrepancy links to an exact proof and an action, not automatic edits.

**F. Future View.** Visual projection of intended capability when a plan family closes. PROJECTION watermark is persistent; unbuilt Tree/HCN/AI scene is NEVER presented as currently navigable live functionality. Future source trace remains available for comparison, without making projected relationships authoritative.

**G. Pending Edits.** User can propose EDIT, LINK, IDEA, PROMOTION, NOTE and DECISION on a plan node, with before/after, rationale, citations, actor, target ID, source generation, affected contract and invalidation impact. Local drafts never modify canonical truth or grant CODE completion. Export JSON and/or submit through the existing reviewed GitHub PR workflow **only after an authenticated reviewed connector pathway is independently validated**. Offline drafts remain PENDING with owner-scoped storage; do not claim submitted if action failed.

**Drill-down:** a recursive "zoom into item" follows parent/child and dependency edges without collapsing identity. Breadcrumbs preserve exact canonical node IDs. A selected item can show an interactive dependency DAG, failure cases, source code links, tests and a side-by-side PLAN/CODE status. An Ace-only gate shows the safe alternate paths that remain executable meanwhile.

## 6. Interaction model

- Tap/select object: opens read-only inspector; never mutates state.
- Zoom: changes local view/level only. Back/forward restores item and filter.
- Drag in planning map: adjusts a LOCAL layout pin, not a logical dependency or timeline.
- Add dependency: creates a PENDING typed-edge proposal with evidence and target; requires checker review before inclusion in authoritative sequence.
- Edit contract: creates a versioned draft; identifies every downstream consumer and changed test oracle. Existing adopted contract remains in force until a decision.
- Mark "complete": disabled as a direct edit. Offer "submit certification evidence" with exact contract/head/test/merge records; authority accepts via normal gates.
- Compare versions: show old/current plan texts and status; no silent overwrite.
- Group/cluster: read model organization only; do not change User Idea graph or Nursery ownership.
- Launch next circuit: display precise packet and link to existing GitHub flow; never auto-merge/auto-grant because a visualization suggested it.
- Auth and access: plan editing subject from trusted session identity, not free-text proposal.actor; protected values and secrets redacted before export; external links sanitized.

## 7. Architecture for fast, low-memory operation

Use a generated indexed JSON snapshot rather than rescanning the repository on each pan/zoom. Lazy-load node neighborhoods and search pages, maintain stable sort, cache by snapshot SHA. The underlying authoritative data remains in GitHub; transient UI state stores selection, camera, filters and pending draft only. Renderer can sample edges but must disclose drawn/shown/total and allow progressive exploration. Do not duplicate the current Studio's silent second edge slice. Keep a static accessible list/table alternative for slow devices and screen readers. No live polling claim without an actual implemented task/connector.

Read-model validation: duplicate stable ID, dangling typed edge, missing reference, missing source SHA, stale evidence at changed head, illegal status transition, invalid source scope and cycle in implementation DAG all fail pre-render or yield a named partial snapshot; never quietly discard bad rows. Cache invalidation is source-SHA-based, not time-guessed.

## 8. Sync and generation math

At every supported refresh:
1. Capture exact main and PR HEAD map with retrieval timestamp.
2. Parse generated MWL JSON and verify row count/number continuity/status table.
3. Parse proposal-source additions and crosswalk, but keep them outside canonical denominator unless adopted.
4. Fold PR/CI/review evidence only where exact head and scope match.
5. Rebuild typed edges and validate references, contract status and gated decisions.
6. Publish read snapshot atomically; retain previous good snapshot if update fails, display SOURCE_ERROR.
7. Materialize diff and Sync Mirror discrepancies with cited before/after and owner.

Derived progress: CODE_COMPLETE / code_scope_total and PLAN_COMPLETE / plan_scope_total each use explicit definitions and separate exact source. MWL_COMPLETE / MWL_active_total remains 39/182 at the pinned base. Change in total must be explained by specific item row additions/aliases, not a number typed in a heading.

## 9. Fifteen UI acceptance scenarios

| Test | User action | Required evidence |
|---|---|---|
| M-01 | Load snapshot | Exact main, source SHAs, 185 row identities, 3 sandboxed, 182 active, 39 complete |
| M-02 | Open every MWL card | 185 unique stable IDs, full title and status, no duplicate label-key collision |
| M-03 | Filter PLAN vs CODE | Independent counts, no merged=certified or historical denominator substitution |
| M-04 | Search Dell 00 and Dell 99 | Both exist; 100 core addresses; 151 marked reserved example |
| M-05 | Follow contract to code | Source provenance and verified-vs-proposed edge visible |
| M-06 | Change PR head in fixture | Previous exact-head stamp becomes STALE, not disappeared or current |
| M-07 | Lose GitHub during refresh | Previous snapshot remains labeled AS_OF, mutating submission blocked |
| M-08 | Query 1,000+ graph edges | drawn/shown/total truthful; continuation available; no second silent cut |
| M-09 | Browse Tree/FAR projection | Clear PROJECTION watermark, no real semantic claims |
| M-10 | Drag map node | Layout-only; no canonical ID/edge mutation |
| M-11 | Draft edit + export | Pending provenance+before/after serialized, no GitHub credit change |
| M-12 | Fake "mark complete" | No direct completion mutation; gates and evidence submission required |
| M-13 | Insert cycle in dependency fixture | Typed validator refuses and shows exact cycle |
| M-14 | Protected text in PR description | Safe escaping/redaction; no script execution or secret export |
| M-15 | Navigate on narrow/keyboard view | Search, inspector, tabs, evidence, return path all usable |

Run each as current-main pinned fixtures and in a real browser; verify precise status and screenshots where applicable. Include negative permission tests, language/emoji labels, screen-reader summaries, keyboard focus and reduced-motion setting. Report M-01..15 individual evidence and failures.

## 10. Delivery and role split

The Director has specified the full schema, views, source contracts, edits, sync, and tests. **Uni checks:** (1) existing interface reuse and API realism, (2) no unaccounted rows or unsafe role crossing, (3) whether one read-model generator can be built with no second authority, (4) performance/resource budget and adversarial sources, (5) every M-01..15 contract. Report ACCEPT / COUNTEREXAMPLE / MISSING_SOURCE for each. Keeper independently verifies head and authority fences. Only after this design check does Uni implement the bounded read-only generator, then UI, then optional reviewed draft submission as separate circuits. No drag/drop or edit path is permitted to bypass the PLAN/CODE and merge gates.
