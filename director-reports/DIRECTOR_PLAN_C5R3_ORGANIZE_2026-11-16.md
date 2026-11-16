# DIRECTOR PLAN — C5R.3 ORGANIZE: Canonical Nursery metadata and human operations

**Status:** PLAN DRAFT — awaiting Uni and Keeper independent source checks, not implementation authorization or completed PLAN credit.
**Author:** Director (ChatGPT), 2026-11-16.
**Plan authority:** `director-reports/C5_REPLAN_2026-11-15.md`, §3.3, §4 and AC-3.1–AC-3.3.
**Dependency:** C5R.1 HOLD merged; C5R.2 SEE is the planned browsing/search spine. This design must not collide with Uni's current production work.
**Single production coder/merger:** Uni. **Second reviewer:** Keeper. **Sovereign:** Ace.

## 1. Verified present code and missing behavior

In `form/dell_matrix/nursery.py`, `Proposal` persists `id`, `label`, `words`, `kind`, `parents`, `affinity`, `reason`, `created`, `status`, `origin`, `detail`, `goals`, lifecycle and scoring fields. It has **no** topic, tags or cluster fields today. `Nursery.save` writes a single owner-scoped JSON file atomically and checks a last-seen signature to refuse lost updates; `Nursery.load` stages proposal objects before applying the decoded state. The same file contains a reserved `__conflict_dispositions__` section under the DCC-XIX arrangement. Do not replace that section, reinterpret it as a proposal, or write a new sidecar.

`Program.list_proposals()` in `form/open.py` currently returns pending items; the REPL `proposals` read path exposes no organization editing. The existing `Program.confirm_proposal` is protected by acceptance-policy and placement choices; C5R.3 never bypasses or changes this protection.

## 2. One-store additive schema and provenance

Extend the existing `Proposal` record additively with:

- `topic: str` (default empty / unclassified for old records);
- `tags: List[str]` (default a fresh empty list for each object);
- `cluster: Optional[str]` (default null).

Proposed names are design-level, not a code mandate. Provide explicit input-shape and resource bounds as typed refusals. Never silently slice topic/tag strings, discard invalid tags, or convert malformed storage into a seemingly valid empty value. A corrupted field in persisted JSON must fail closed before publishing a partially loaded Nursery. Pre-feature files load with defaults; their historical bytes and semantic content are not overwritten just by opening or listing them.

**Automatic seeding — binding AC-3.2 correction (R3):** At **creation of every NEW proposal**, automatically derive and **persist** initial topic from the source proposal's `kind`/`origin`, in the **same canonical Nursery owner-file transaction** as the new proposal and with an item-specific durable receipt. No human edit or review is needed merely to seed metadata. The initial rule must be deterministic and documented (recommended: normalized, validated `kind` as primary topic; validated origin family as fallback; explicit `unclassified` fallback with reason; no silent truncation). Preserve exact source values in provenance, and never claim an inferred topic is human-authored. Add validated, backward-compatible per-record provenance (e.g. `topic_source=derived`, source fields, version of seed rule, time/creation receipt identifier) or a reserved, validated same-file receipt section. Never create a second datastore or write a ghost receipt after a failed save. A new proposal's seed and provenance must either both persist or neither persist. A human override is stored as a later, separate actor-attributed edit with before/after proof and `topic_source=human` while retaining the seed history. For **LEGACY** proposals, old records load with unchanged bytes/defaults; read-only grouping may show a clearly nonpersisted `DERIVED` effective-topic projection, but browsing must not trigger a migration. Their first persistent organization change is explicitly authorized and receipted. Missing source fields receive an explicit unclassified seed/receipt, not false provenance. This reconciles the draft with the governing AC-3.2 requirement that creation seeding be automatic and receipted.

Choose and document tag uniqueness and normalization. Recommended baseline: compare normalized tags for duplicate detection while preserving the exact accepted user-visible spelling in the stored record, or reject duplicates with a named explanation; either way do not silently rewrite a user's data. Cluster is an organization reference, not a new containment/Plane authority. Prove that editing it cannot reparent any live Idea or bypass the canonical graph.

## 3. Trusted human edit boundary

Create one bounded organization mutation operation in the existing Nursery/Program path and one REPL command family for a trusted human. The operation must:

1. Resolve the proposal by stable ID and trusted owner scope, validate that it exists, and authenticate the human action using the existing trusted command/session boundary (never trust actor text supplied by an untrusted proposal).
2. Validate every requested field and the entire proposed new organization state before changing a value.
3. Capture before and after representations, changing **only** topic/tags/cluster. Preserve `id`, `label`, `words`, `reason`, `detail`, `goals`, `parents`, `status`, lineage, and confirmation/placement history byte-identically.
4. Persist through the single canonical `Nursery.save` with optimistic-concurrency protection. A changed owner file yields `NurseryConflictError`, not overwrite. If persistence fails, restore in-memory organization to the previous state; leave the old on-disk generation intact. Beware exceptions after partial staging: use a copy-on-write or explicit rollback mechanism consistent with existing Nursery transaction patterns.
5. Emit an item-specific receipt recording trusted actor, owner, proposal ID, operation, before/after, any original automatic derivation/provenance, saved generation identity, and outcome. On NEW proposal creation, the automatic seed has an itemized `system_seed` provenance/receipt in the **same atomic owner transaction**; it is not misattributed to a human editor. A refused operation is also a truthful receipt, never a success.
6. Keep organization methods inaccessible to docked AI direct-setter paths. A later AI organizer (C5R.6) may create **PENDING suggestions only**; acceptance of organization suggestions must go through a specifically approved, human reviewed C5R.5 path.

Do not create an independent undo stack. Q-LC.1/DD-54 is the single historical undo/redo authority. If its interface is not yet usable, make the dependency explicit and do not falsely label this slice as reversible via a shadow log.

## 4. Views and exact coverage

Expose view/group/filter capabilities through the C5R.2 read service, never a separate organization database. Include `topic`, each `tag`, and `cluster` in complete-field search once the fields are present.

- Topic and cluster groups are mutually exclusive partitions only if the implementation chooses exactly one value per proposal; include an explicit unclassified/null group.
- Tags can overlap, so sum of tag-group membership may exceed the unique proposal count. Display **both** group membership and global distinct total to prevent fake inventory.
- Every filter and group states its actual shown/total coverage, even if empty. All proposal statuses remain reachable; do not filter to pending except when explicitly requested.
- Sorting and paging must remain stable with C5R.2's snapshot semantics after an edit. A successful edit invalidates stale cursors rather than silently mixing generations.
- A topic/tag/cluster field is never a retention bucket; low-priority, untagged or aged proposals remain stored, visible and confirmable through the unchanged human approval gate.

## 5. Failing-first suite, mutants, and done-definition

**Proposed suite:** `form/nursery_c5r3_organize_test.py`, registered in `form/regress.py` after implementation approval. Build evidence must first show the existing Program/REPL cannot edit topic/tag/cluster and the Proposal schema lacks these fields.

Acceptance:
- **AC-3.1:** Save/load round-trip on 1,000 mixed legacy/new proposals (all current statuses) with byte-exact accepted Unicode topic, tags and cluster. Legacy records load without data-loss or implicit write. Corrupt metadata records produce typed load refusal; no partially loaded in-memory Nursery.
- **AC-3.2 (R3):** For each newly created proposal, a deterministic, automatic kind/source topic seed and its `system_seed` provenance receipt **persist atomically**. Load a new proposal in a fresh process and assert saved topic/provenance/receipt byte-exact; injected save failure must leave **neither** a proposal nor a detached seed receipt. Human overrides create separate actor-attributed before/after edit receipts, preserve the original `DERIVED` history and change only organization fields; proposal content/confirmation status remain unchanged. Legacy load or read-only browse must not create persisted seeds or change disk SHA. Malformed inputs refuse before mutation with preserved disk SHA.
- **AC-3.2 atomicity:** Two owner instances attempting stale writes: second refuses with unchanged disk digest. Inject a save failure after local staging: in-memory metadata reverts and canonical on-disk bytes remain previous generation, allowing a coherent retry.
- **AC-3.3:** Group by topic, tag or cluster over all 1,000 records; prove partition totals and overlap disclosure as defined, stable paged IDs, correct empty/unclassified groups, full-field search of every organization attribute at the public REPL door.
- **Authority:** An AI-originated command or malformed suggestion payload cannot directly edit metadata, reject/confirm a proposal or place anything on the Plane. There is no alternate setter/sidecar.
- **Compatibility:** Existing C5R.1 holding/read-path suites, C5R.2 visibility suite and Nursery/confirmation family remain green. Preserve the DCC-XIX reserved-section semantics.

Use mutants that remove a validation/refusal, silently truncate a tag, bypass concurrency, mutate status during edits, or omit rollback; each must fail a permanent check. Require full exact-head regression forward/twice/reverse, exact-head CI, independent Keeper review, Director scope disposition, §32 before any authorized Uni-only merge, plus merged-main proof. Tests and source review occur at a separately authorized implementation turn; a draft itself never earns CODE credit.

## 6. Unresolved design reviews and exclusions

**Uni and Keeper must examine:** trusted human identity path; the existing save/recovery protocol and error injection seam; the **mandatory persisted automatic seed + durable creation receipt** and its same-file atomicity (choice of per-record provenance vs reserved receipts section, and deterministic kind/origin precedence); compatibility with current REPL command parsing; Q-LC.1 single undo/redo authority; overlap of metadata names with the future C5R.6 suggestion section. An on-read `DERIVED` label for legacy records does **not** substitute for the mandatory new-proposal automatic seed.

**Excluded from this slice:** Formula S/other ordering lenses (C5R.4), duplicate merge with reversible tombstones and archive/restore (C5R.5), AI suggestion acceptance (C5R.6), and any automatic confirm. Topic is **organization metadata, not a survival gate**. No project/Plane containment is changed.

**Plan-review output contract:** Uni and Keeper return SOURCE_MATCH / CORRECTION_REQUIRED / EVIDENCE_MISSING for each claimed code boundary, a revised explicit acceptance checklist, and a dependency/conflict map before changing this draft's status to reviewed. Do not inflate the PLAN 242 or CODE 198 belts; one object can close only under the established counting and verification law.