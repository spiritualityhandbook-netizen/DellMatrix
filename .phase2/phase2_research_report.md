# Phase 2 External Research Report — Fractal Semantic Graph

**Role:** advisory only. Verified DellMatrix runtime remains the authority.
**Date:** 2026-10-03
**Scope:** local-first, offline, single-user Python; hundreds–thousands of nodes; Chromebook-class hardware.
**Rule honored:** no recommendation to import a graph database or framework.

---

## A. Graph data models

### A1. Labeled Property Graph (LPG) — the working model

**Sources:**
- ISO/IEC 39075:2024 (GQL) — first ISO database language standard since SQL; standardizes the property graph: nodes and edges, each with labels and key/value properties. (via https://github.com/ghchinoy/binder/blob/HEAD/docs/lpg-inmemory-primer.md, accessed 2026-10-03)
- Angles et al., "Edge-Labelled Graphs and Property Graphs — a comparison from the user perspective" (arXiv 2204.06277, 2022): Cypher permits several distinct edges with the same label between the same two nodes; edge properties avoid RDF*'s nesting-order problem because role and time can simply co-exist as property names on one edge.
- SeleneDB GQL overview (https://github.com/jscott3201/selenedb/blob/HEAD/docs/guides/gql/overview.md): concrete in-memory model — edge = (id u64, source, target, label, properties, created_at). Both nodes and edges are first-class with identity.

**Falsifiable claims:**
- An edge-ID → edge map gives **O(1) edge lookup by identity**; adjacency lists give **O(out-degree) traversal** per hop. At DellMatrix scale (10²–10³ nodes), both are trivially fast; the design choice is about semantics, not performance.
- Cypher/GQL convention: **every edge is directed and has exactly one type label**. Multiple edges of the same type between the same endpoints are legal and distinguished by edge ID — this is exactly why edges need identity independent of (source, type, target).

**Failure mode (community):** the binder LPG primer notes the classic confusion — storing relationship attributes on endpoint nodes loses the semantic association of *which* fact the attribute qualifies. Provenance "who said this, when, how confident" belongs on the edge.

### A2. RDF and why not

**Sources:**
- W3C PROV primer (http://www.w3.org/TR/prov-primer/); RDF-star WG minutes (https://www.w3.org/2024/07/26-rdf-star-minutes.html, 2024); Champin, "RDF goes meta" (Eurecom talk slides, 2022-06-15, https://perso.liris.cnrs.fr/pierre-antoine.champin/2022/eurecom/Slides/?full).
- Hartig & Thompson RDF* (2014) via Champin: alternatives to statement-level metadata (plain reification = 4–5 triples per statement; named graphs) are verbose and lose the original triple.

**Falsifiable claims:**
- Plain RDF reification costs **~4 triples per annotated statement** (subject/predicate/object/statement node + metadata), vs 1 edge with properties in LPG.
- RDF-star (`<<s p o>> :since 2020`) converges toward LPG edge properties, but as of the 2024 WG minutes the mapping of LPG edge *identity* (two identical edges) to RDF-star was still under active debate — i.e., the standards world has not settled edge identity; LPG implementations simply assign internal IDs.

**Verdict: REJECT RDF/RDF-star as the model; ADOPT LPG semantics** (typed directed edges with internal IDs and property maps). The RDF-star debate confirms that edge identity is the hard part, and LPG solves it by fiat: every edge gets an ID.

### A3. When edges need their own identity

**Sources:** RDF-star WG discussion (Souri: "Each LPG edge has a unique id: say e1, e2 — for identical (s)-[:p]->(o)"); sarib-lang decision D-017 (https://github.com/syedsaribsultan/sarib-lang/blob/HEAD/decisions/decision-log.md): "An edge = (id, type, family, source, target, order?, anchor?, properties, status, provenance). Edges have identity and properties like nodes — the labeled-property-graph advantage."

**Falsifiable claims:**
- Edge identity is *required* when: (a) the same (source, type, target) can occur more than once (e.g., two separate derivations); (b) provenance/history must attach to the relationship rather than its endpoints; (c) relationships must be addressable by operations (supersede, remove, restore).
- Edge identity is *unnecessary overhead* when relationships are pure structural facts never individually referenced. DellMatrix needs (b) and (c) — so identity is required.

**Verdict: ADOPT — every relationship is an identified object** (relationship_id UUID, type, source_id, target_id, properties, status, provenance). This directly satisfies "A GRAPH EDGE MUST HAVE AN EXPLICIT SEMANTIC TYPE" and the Phase-2 change-event integration.

### A4. Higher-order relationships (2.3.4)

**Sources:** Angles et al. §14.2.1 (RDF* nesting-order problem); RDF-star "reference cycles are not allowed in an RDF-star triple" (arXiv 2304.13097).

**Claim:** If a relationship itself needs identity/provenance/history, the smallest correct model is to make the *edge itself* the identified object (A3) — not to introduce hyperedges. Hyperedges (edges about edges) reintroduce the nesting-order and cycle problems the literature documents. Only if an edge must be an *endpoint* of another edge is a hyperedge warranted; nothing in Phase 2 requires that.

**Verdict: REJECT hyperedges for Phase 2; ADAPT edge-as-identified-object** to carry provenance/history. Revisit only if Phase 3 geometry demands it.

---

## B. Hierarchical containment + cross-links

### B1. Storage models: adjacency list vs materialized path vs nested sets vs closure table

**Sources:**
- nested-tree design doc (https://github.com/joshuabradley012/nested-tree): adjacency list = simple writes/moves, expensive recursive subtree queries; materialized path = fast subtree/ancestor queries, moves require updating all descendants; nested sets = optimal static reads, costly inserts/moves (renumbering), difficult ordering.
- OPA-ABAC ADR-0008 (https://github.com/void3110/spring-boot-starter-opa-abac/blob/HEAD/docs/architecture/adr/0008-hierarchical-resource-authorization.md): "Nested-set is bad under writes (renumbering); a closure table is the most flexible but its storage and write/move cost exceed materialized-path for our read-heavy, occasionally-moved tree. Adjacency-list + ltree is the sweet spot."
- Railsware blog (https://railsware.com/blog/storing-tree-structures-in-the-rdbms/): nested-set insert/update "will affect half of records in a table" on average.

**Falsifiable claims (at DellMatrix scale):**
- Adjacency list (parent pointer per node): insert/move = **O(1)**; ancestors = **O(depth)** walk; descendants/subtree = **O(subtree)** DFS.
- Materialized path (denormalized path string per node): ancestors/breadcrumb = **O(1)** read; reparent = **O(subtree)** rewrite — the dominant correctness risk (OPA-ABAC ADR calls it out explicitly: "atomic subtree rewrite on re-parent — the dominant correctness risk").
- Nested sets: subtree query = **O(1)** range check; insert/move = **O(n)** renumbering. **REJECT** for a mutable local graph.
- At hundreds–thousands of nodes, O(depth)/O(subtree) traversals are microseconds; no denormalization is needed for performance. Denormalization only buys constant factors at the cost of a second write path that can diverge.

**Verdict: ADOPT adjacency list (single `parent_id` per Idea) as the single containment authority; ADAPT by deriving breadcrumbs/paths on read** (O(depth)), never storing them. This directly implements "one active containment parent" and makes "NO SILENT IDENTITY CHANGE DURING REPARENTING" trivial: reparenting changes one pointer; the Idea ID never moves.

### B2. Cycle prevention

**Sources:** cycle-detection literature (DFS 3-coloring / Kahn's: **O(V+E)** time, O(V) space — multiple sources incl. https://github.com/neeshant-pandey/pattern-based-dsa/blob/HEAD/04-Graph-Traversal-Patterns/Pattern-20-DFS-Cycle-Detection/README.md).

**Falsifiable claim:** For *containment insert* specifically (single-parent tree), the full O(V+E) scan is unnecessary. The check "would making P the parent of X create a cycle?" reduces to "is P reachable from X by following parent pointers?" — a walk of length ≤ depth, i.e. **O(depth)**. Reject self-containment as the depth-0 case. This is cheaper and simpler than general cycle detection and is provably sufficient for a single-parent containment invariant.

**Verdict: ADOPT — pre-insert reachability walk on the parent chain** (fail closed on self-parent or ancestor-parent). Full DFS/Kahn's reserved for validating *loaded* graph state (E), not the hot path.

### B3. Reparenting with identity preservation

**Sources:** OPA-ABAC ADR (atomic subtree rewrite as re-parent event); git's model (content identity independent of path) as practitioner precedent.

**Claims:**
- Identity preservation is structural, not procedural: if the Idea's UUID never appears in the containment record as anything but a reference, reparenting *cannot* change identity. The failure mode "identity loss during promotion" only exists if identity is derived from position (e.g., path-based IDs) — so: **never derive identity from position**.
- Promotion/reparenting history = append to a relationship-history log (see C), not a mutation of the Idea.

**Verdict: ADAPT — containment edge carries its own lifecycle history** (created → active → superseded/reparented); the Idea record is untouched by reparenting except its parent pointer.

### B4. Containment vs association vs lineage vs spatial

The directive's laws (CONTAINMENT != ASSOCIATION; LINEAGE != CONTAINMENT; SPATIAL NEARNESS != SEMANTIC RELATIONSHIP) match the literature's sharpest warnings:
- Railsware/nested-tree docs show what happens when one structure is overloaded: moves corrupt reads.
- The sarib-lang D-018 decision ("thin core; semantic types are optional namespaced vocabulary") supports: **one edge table, a closed controlled vocabulary of edge types**, with `CONTAINS` as a structurally special type (single active parent invariant) and everything else as associations.

**Verdict: ADOPT — single relationship store, typed edges, containment enforced as a type-level invariant** (≤1 active CONTAINS edge per child), not as a separate structure. This is the "ONE canonical semantic graph authority" the directive demands.

---

## C. Provenance and temporal relationships

### C1. PROV-O as vocabulary (not as implementation)

**Sources:** W3C PROV-O Recommendation 2013-04-30 (https://www.w3.org/TR/2013/REC-prov-o-20130430/); PROV primer (http://www.w3.org/TR/prov-primer/); opure ADR-0023 (https://github.com/h4zey86/opure/blob/HEAD/adr/ADR-0023-project-memory-lifecycle-and-provenance.md): "A complete RDF or OWL implementation is not required to apply the model."

**Adoptable concepts (adapted, not imported):**
- `wasDerivedFrom`: entity→entity derivation. Maps to DellMatrix dependency edges.
- `wasInvalidatedBy`: "the start of destruction, cessation, or expiry of an existing entity by an activity" — maps to relationship removal/supersession with a recorded cause.
- **Qualified relations** (`prov:qualifiedX` pattern): "restates any binary relation as an intermediate resource, so extra attributes (time, role, plan) can be attached to the relation itself" — this is the standards-blessed version of A3's identified edge.
- Revision: "the result of each revision is a new entity" — maps to: relationship state changes create new history entries, never mutate the old.

**Verdict: ADAPT the vocabulary** (derived_from, invalidated_by/superseded_by, qualified-relation-as-object). **REJECT importing PROV-O/RDF serialization** — DellMatrix already has a Provenance record; extend it, don't replace it.

### C2. Bitemporal pattern for relationship history

**Sources:** SQL:2011 temporal (via https://github.com/ekgardt/llm-wiki/blob/HEAD/docs/research/2026-08-28-bitemporal-claims.md): valid time (application-written) vs system/transaction time (system-written, never by application); half-open intervals `[start, end)` so adjacent records "snap together without special case logic"; CHECK start < end.
- wolfdb research (https://github.com/atom00blue/wolfdb/blob/HEAD/docs/research/04-bitemporal-modeling.md): "Correct invalidation, not destructive overwrite… the old fact is closed, not deleted."
- arXiv 2607.26520 (graph-native bitemporal memory): on update, close current version (`tx_to` set), create new version; on delete, close both clocks; **no versions physically removed**.
- macrame (https://github.com/opticswolf/macrame): append-only transaction log + rebuildable `links_current` projection; "current state is not stored, it is derived."

**Falsifiable claims:**
- Append-only relationship log + derived "current" projection gives: full history, auditability, and rebuild-from-log recovery **for free**. Cost: current-state queries filter on status — O(edges) scan at small scale, or an index on (child_id, status).
- Half-open intervals eliminate gap/overlap edge cases in history queries.

**Verdict: ADAPT — relationship history as append-only log with (valid_from, valid_to, recorded_at) and status; current state derived.** This is the strongest structural answer to "PROMOTION CHANGES CONTAINMENT, NOT IDENTITY" and "preserve reparenting history."

### C3. Tombstones vs soft-delete (failure modes)

**Sources (practitioner, failure-modes only):**
- HN thread "Avoiding the soft delete anti-pattern" (https://news.ycombinator.com/item?id=40326815): soft-delete is "an ad hoc, informally-specified, bug-ridden, slow implementation of half of Event Sourcing" (Greenspun's tenth rule, quoted); counterpoint: "if entity might be resurrected, what you thought as deletion was something else (suspending, archiving)" — model it as an explicit FSM state.
- AWS DynamoDB blog (https://aws.amazon.com/blogs/database/timestamp-writes-for-write-hedging-in-amazon-dynamodb/): tombstone = version marking soft delete; required so "older data might effectively recreate it"; keep timestamp + TTL.
- Medium historization (https://medium.com/@andymadson/storing-data-history-without-regretting-it-7a082b9f7936): "Model deletes intentionally. SCD2 and history-mode replication often represent deletes explicitly with soft-delete flags, end-dating, or tombstone events. If you ignore deletes, your history will lie." Also: define time semantics explicitly; idempotent merges; retention policy.

**Verdict: ADAPT — relationship removal = explicit terminal history entry** (status=REMOVED with timestamp, cause, provenance), never physical deletion; the entry doubles as the tombstone that prevents resurrection-by-replay. This matches DellMatrix's existing lifecycle-state philosophy (FADED/ARCHIVED, not deleted).

---

## D. Incremental / dependency-aware computation

### D1. The core principle: change-local recomputation

**Sources:**
- DBToaster, Ahmad et al. (arXiv 1207.0137, 2012): viewlet transform — "M(D+ΔD) = M(D) + ΔQ(D,ΔD)"; the delta query "often has a simpler structure than Q and involves smaller delta updates instead of large base tables." Tens of thousands of complete view refreshes/second.
- Simons Institute, Dan Olteanu, "Incremental View Maintenance" Parts 1–2 (https://www.classcentral.com/course/youtube-incremental-view-maintenance-1-206312 and /incremental-view-maintenance-2-206311) — technical lecture series; also the semi-ring query algebra lecture (https://www.classcentral.com/course/youtube-a-semi-ring-based-query-algebra-for-incremental-view-maintenance-and-query-compilation-270446): delta queries closed under a universal difference operator.
- DBToaster backend (https://github.com/erlfilho/dbtoaster-backend): compiles one trigger program per base relation per query.

**Adapted claim for DellMatrix:** The directive already scopes this correctly — "Do not build Differential Dataflow itself. Use the principle: change-local recomputation." The DBToaster lesson that transfers: **for each change, compute the affected set from declared dependencies, then apply a per-change delta function** — never recompute the whole derived graph.

### D2. Dirty-marking with early cutoff (the small correct mechanism)

**Sources:**
- Adapton (Hammer et al., PLDI 2014) via gofish design doc (https://github.com/gofish-graphics/gofish-graphics/blob/HEAD/apps/docs/docs/internals/design/incremental-layout.md): demand-driven — `set` only *signals* change (dirty flags); recomputation deferred to demand; **cutoff nodes stop propagation when the recomputed value equals the old one**.
- Salsa / rustc red-green (same source): on input change, query cached result is "red"; re-run dependencies first; if all produce values equal to before, mark "green" **without re-running** — "early cutoff"/"backdating." "You can delete [the incremental layer] and the system still works, just slower."
- librainian issue #93 (https://github.com/nateschmiedehaus/librainian/issues/93): practitioner implementation plan — BFS dirty-marking from changed nodes + result-hash early cutoff + lazy recompute on query.
- Vue 3.4+ computed semantics (http://dev.to/parsajiravand/vue-computed-what-it-caches-and-when-it-reruns-1e03): invalidation (dependency write) and recomputation (next read) are separate moments; since 3.4, "a computed only propagates to *its* dependents when the recomputed value actually differs."

**Falsifiable claims:**
- Dirty-mark then recompute-in-dependency-order with equality cutoff gives **O(affected)** work per change, where affected = nodes reachable via declared dependency edges whose inputs actually changed value. If no declared dependency exists, propagation count is legitimately zero (directive's requirement).
- Cutoff correctness requires **value equality, not identity**: recompute-then-compare; if equal, stop. This is what makes "change-local" honest rather than "recompute everything reachable."
- Deterministic ordering: process the dirty set in **topological order** of the dependency DAG (Kahn's, O(V+E) on the affected subgraph only). Deterministic order ⇒ deterministic propagation results ⇒ testable.

**Failure mode (practitioner):** the gofish doc's key lesson — "the machinery is genuinely small; the design work is choosing the node granularity and the cutoff points." And from the React/Vue world: over-broad dependencies cause recomputation on unrelated changes (the exact "global recomputation disguised as dependency propagation" the directive warns about). Dependencies must be **declared per derived value**, narrow (depend on the specific unit, not the whole Idea).

**Verdict: ADAPT — dependency-indexed dirty propagation:**
1. Derived graph state registers explicit dependencies on (idea_id, property/unit) — declared, not inferred.
2. On information change: BFS/DFS over *declared* dependency edges from the changed unit → affected set.
3. Recompute affected derived values in topological order; equality cutoff stops propagation.
4. Record propagation as processing evidence (extends IdeaChangeEvent or a derived RelationshipChangeEvent — the directive's 2.3/2.5 integration point).
5. **REJECT** full self-adjusting-computation machinery (Acar's DDG/timestamps, differential dataflow) — orders of magnitude beyond need.

### D3. What "derived graph state" means at this scale

Concrete DellMatrix candidates: breadcrumb/path caches, descendant counts, dependency-derived summaries, cross-link indexes. All are **pure functions of declared inputs** — the Salsa framing ("the program is a set of pure queries over inputs with revision counters") applies directly: DellMatrix already has version IDs as revision counters.

**Verdict: ADOPT the Salsa framing** — derived state = pure function of (versioned inputs); cached with (input_version_ids, result); recompute iff inputs changed. This unifies with Phase-1 PropertyVersion identity with zero new concepts.

---

## E. Graph integrity / security

### E1. Dangling edges and transactional atomicity

**Sources:**
- Neo4j selection guide (https://neo4j.com/blog/graph-database/16-things-to-consider-when-selecting-the-right-graph-database/): "When only part of a transaction completes but other parts fail, a graph database can be left in a corrupted state in which dangling relationships point nowhere… Subsequent graph updates and changes can easily spread the corruption."
- SQL Server edge constraints (https://learn.microsoft.com/bg-bg/sql/relational-databases/tables/graph-edge-constraints?view=sql-server-linux-ver15): edge tables by default enforce nothing; `CONNECTION` constraints enforce that endpoints exist in the proper node tables and that "a node can't be dropped, if any edge is referencing that node."
- thinkmind ICCGI 2016 (http://www.thinkmind.org/articles/iccgi_2016_3_40_10068.pdf): "the level of [integrity constraint] support [in graph DBMSs] is currently minimal and mostly theoretical" — i.e., **the application layer must enforce integrity**.

**Falsifiable claims:**
- Integrity must be enforced at **mutation time** (reject edge to nonexistent endpoint; reject node deletion while referenced, or define cascade semantics explicitly) **and at load time** (validate persisted graph; fail closed on dangling references). Mutation-time-only is insufficient because persisted state can be hand-edited or partially written.
- DellMatrix's existing checkpoint transaction (Phase 0: journaled two-file rollback) is the atomicity mechanism — graph mutations must participate in the same transaction, never a sidecar.

**Verdict: ADOPT — validate endpoints on every mutation; validate full graph on load (fail closed); graph state inside the checkpoint transaction.**

### E2. Containment-specific invariants

From B2 + E1, the check suite before any containment mutation:
1. both endpoints exist (no dangling);
2. not self-containment;
3. no containment cycle (O(depth) ancestor walk);
4. type is legal; transition is legal;
5. at most one active CONTAINS edge per child (duplicate → defined idempotency contract: no-op-with-receipt vs error).

**Verdict: ADOPT as a pre-mutation invariant gate** producing processing evidence on both success and rejection.

### E3. Malformed persisted graph recovery (fail-closed)

**Sources:** Phase-0/Phase-1 precedent (fail closed when recovery cannot establish proven state); Medium historization ("define time semantics explicitly… idempotent merges"); GitLab 2017 postmortem (https://medium.com/@warstories/a-post-mortem-on-the-day-gitlab-lost-six-hours-of-data-9e041f64db91): "Backups that cannot be restored are not backups" — practitioner failure evidence that untested recovery paths are fiction.

**Claims:**
- Load path: schema-validate every relationship record (required fields, known type, existing endpoints, acyclic containment); **first invalid record → whole graph load fails closed** (never "load the good parts" — partial loads create the dangling/corrupt states E1 warns about).
- Crash-boundary: graph mutations go through the same journaled transaction as Ideas; test by killing mid-write and proving fail-closed or full recovery.

**Verdict: ADOPT fail-closed whole-graph validation on load** (consistent with Phase-0/1 contracts).

### E4. Unauthorized mutation / cross-owner

DellMatrix already has owner isolation (Phase 1). The graph authority must enforce: a relationship mutation is authorized iff the mutator owns **both** endpoint Ideas (or the operation is explicitly cross-owner-authorized). Owner namespace collisions are prevented by UUIDs.

**Verdict: ADAPT existing owner-isolation to relationship mutations** — no new auth model.

---

## Cross-area synthesis: the smallest correct mechanism

| Concern | Mechanism |
|---|---|
| Node | canonical Phase-1 Idea (UUID) — unchanged |
| Edge | identified object: (rel_id, type, source_id, target_id, properties, status, provenance, valid_from/valid_to, recorded_at) |
| Containment | `CONTAINS` edge type with ≤1 active per child; parent pointer derivable; O(depth) cycle check on insert |
| History | append-only relationship log; current state derived; terminal REMOVED entries as tombstones |
| Provenance | extend Phase-1 Provenance; PROV-O vocabulary adapted (derived_from, invalidated_by) |
| Propagation | declared (idea, unit) → derived-value dependency index; dirty-mark affected; topological recompute; equality cutoff; evidence recorded |
| Integrity | pre-mutation invariant gate; whole-graph fail-closed validation on load; inside checkpoint transaction |
| Query | outgoing/incoming/by-type/neighbors from edge indexes: `by_source`, `by_target`, `by_type`, `by_id` — four dicts, O(1)/O(degree) |

---

## Top 5 most consequential findings

1. **Edges must be identified objects (A3).** The RDF-star WG's still-open debate over LPG edge identity confirms this is the hard problem; LPG solves it by fiat (internal IDs). DellMatrix needs edge identity for provenance-on-relationships, duplicate (source,type,target) pairs, and supersede/remove/restore operations. Everything else follows from this one decision.
2. **Adjacency list + O(depth) cycle check beats every fancier tree encoding (B1/B2).** Nested sets are O(n) on move; materialized paths make reparenting the dominant correctness risk; at 10²–10³ nodes, parent-pointer walks are microseconds. One `parent_id`, derived breadcrumbs.
3. **Append-only relationship log with derived current state (C2).** Bitemporal/SQL:2011 + event-sourcing practice: never overwrite, close intervals half-open, terminal REMOVED entries as tombstones. Gives promotion/reparenting history, auditability, and rebuild-from-log recovery for free.
4. **Dirty-mark + topological recompute + equality cutoff (D2).** Adapton/Salsa/Vue-3.4 converge on the same small mechanism: separate invalidation from recomputation, stop when the value is unchanged. This is the honest, testable implementation of "recompute only legitimately affected derived state" — and "zero propagation" is a legitimate outcome.
5. **Integrity lives in the application layer and at load time (E1/E3).** Graph DBMSs barely enforce constraints (thinkmind); Neo4j's own docs warn partial transactions spread corruption. DellMatrix must gate every mutation AND fail-closed-validate the whole graph on load, inside the existing checkpoint transaction.

## Top 3 architecture recommendations

1. **One relationship store, typed identified edges, containment as a type-level invariant.** Single `relationships` collection: `(rel_id, type, source, target, props, status, provenance, valid_from/valid_to, recorded_at)`. `CONTAINS` edges carry the ≤1-active-parent invariant; associations are unrestricted. Four in-memory indexes (`by_id`, `by_source`, `by_target`, `by_type`). No second authority — Plane.parents/Nursery.parents become migration inputs or derived projections.
2. **Relationship lifecycle = append-only log; current graph = derived projection.** Every create/supersede/remove/reparent/promote appends a history entry; nothing is destructively overwritten; removals are terminal tombstone entries. Checkpoint persists the log; "current" is rebuilt by a deterministic fold. This makes promotion-with-history, rollback coherence, and fresh-process identical truth nearly free.
3. **Dependency propagation = declared dependency index + dirty topological recompute with equality cutoff.** Derived graph state registers explicit `(idea_id, unit)` dependencies; on change, mark affected, recompute in topological order, stop when values are equal, record propagation evidence via the Phase-1 event mechanism. No differential-dataflow machinery; no token-similarity; zero-propagation is a valid, tested outcome.
