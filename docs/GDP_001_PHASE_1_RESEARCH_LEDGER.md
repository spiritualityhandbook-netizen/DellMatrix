# GDP-001 Phase 1 — Research Ledger

**Date:** 2026-10-03
**Requirement:** Minimum 6 useful sources.

## 1. Event Sourcing (Martin Fowler)

**Source:** https://github.com/osvaldojramos/dotnet-senior-study-guide/blob/HEAD/08-architecture-and-patterns/15-event-sourcing.md
**Claim used:** "Capture all changes to an application state as a sequence of events." State derived by replaying events; append-only log is source of truth.
**Why applicable:** Idea history must preserve what happened, not just current state. Supersession/fade are events, not overwrites.
**What was rejected:** Full CQRS/event-store infrastructure — overkill for Phase 1. We use the principle (append-only versions) without the distributed machinery.
**DellMatrix consequence:** PropertyVersion list is append-only; current state derived by scanning versions. No destructive UPDATE.

## 2. W3C PROV (Provenance Data Model)

**Source:** http://en.wikipedia.org/wiki/Surrogate_key (see also https://en.wikipedia.org/wiki/W3C_Prov)
**Claim used:** Entity/Activity/Agent triad. Provenance = information about entities, activities, and agents involved in producing data, used to assess quality/reliability.
**Why applicable:** "WHY DOES THIS INFORMATION EXIST HERE?" requires structured provenance, not storytelling.
**What was rejected:** Full RDF/PROV-O ontology — too heavy. We use a lightweight Python dataclass with the same triad.
**DellMatrix consequence:** Provenance dataclass with source/activity/agent/derived_from. The `explain()` method derives answers from stored provenance.

## 3. Bitemporal Data (Datomic/SQL:2011)

**Source:** https://github.com/elh/bitemporal
**Claim used:** Two independent time axes: valid time (when fact was true) vs transaction time (when recorded). Never conflate.
**Why applicable:** "bathrooms=2 was true from T1 to T2" is different from "we recorded it at T3". Supersession needs both.
**What was rejected:** Full bitemporal query engine — Phase 1 uses the two timestamps on each version without a temporal query language.
**DellMatrix consequence:** PropertyVersion has valid_from/valid_to (valid time) and transaction_time. History queries can distinguish.

## 4. Reactive Dependency Tracking (Adapton/Signals)

**Source:** https://github.com/angelmunoz/mibo/blob/HEAD/src/Mibo.Adaptive/docs/archive/2026-08-04-SIGNALS-COMPARISON.md
**Claim used:** Dependency graphs with automatic tracking; when a source changes, only affected dependents recompute. Adapton: demand-driven incremental computation with named memoization.
**Why applicable:** Live Matrix Law requires information-change-driven processing, not UI-driven. Dependency-aware propagation (1.5.4).
**What was rejected:** Full incremental computation engine — Phase 1 establishes the hook (`_on_information_change`); later phases deepen.
**DellMatrix consequence:** The `_on_information_change` seam. Phase 1 records the event; future phases add dependency graph.

## 5. Soft Delete Pattern

**Source:** https://metabase.com/glossary/soft-delete
**Claim used:** Mark as deleted (is_deleted/deleted_at) rather than removing. Preserves history, enables recovery, maintains referential integrity.
**Why applicable:** FADED != DELETED. DELETED != ERASED. Phase-0 contracts require history preservation.
**What was rejected:** Database-level soft-delete with query filters — we use lifecycle states on versions, not a global flag.
**DellMatrix consequence:** LifecycleState enum with FADED, ARCHIVED, DELETED as distinct states. Faded/deleted data remains queryable via history.

## 6. Surrogate Keys (Entity Identity)

**Source:** http://en.wikipedia.org/wiki/Surrogate_key
**Claim used:** Surrogate key (UUID) has no business meaning; insulates identity from data changes. In temporal DBs, distinguish surrogate (row) from business key (entity).
**Why applicable:** "Renaming an Idea does not create a different Idea." Identity must survive content changes.
**What was rejected:** Sequential integer IDs — not suitable for distributed/offline. UUID v4 chosen.
**DellMatrix consequence:** Idea.id is UUID v4, stable across rename/save/load. Property versions also have UUIDs for stable references.
