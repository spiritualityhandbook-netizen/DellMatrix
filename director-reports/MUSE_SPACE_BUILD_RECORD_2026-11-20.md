# MUSE SPACE BUILD RECORD — GP-E25 data contract (Part 0, 2026-11-20)

**Status:** DESIGN + DATA CONTRACT at plan stage. GP-E25's own
terms govern: "D authored in 04; B after check" (Edition 1 file
`02_EXECUTION_CIRCUITS.md`). The design of record is Edition 1
file `04_MUSE_SPACE_DESIGN.md`; this record fixes the data
contract Part 0 will build against and the slice order. The Space
itself is built after the authorities' check (this Part's
PLAN-CONFIRM), not in the plan-stage PR.

## 1. What GP-E25 is

A read-only, navigable, materialized view of the canonical plan
and work records: PLAN and CODE belts, the relationship web, the
execution sequence, a future view, and a Sync Mirror (Edition 1
file 02). It is a **witness and drafting surface**, never an
alternate source of truth: it never writes work-list status,
merge, or credit, and its planning objects are distinct typed
objects from the live Nursery's personal ideas (file 04 section 1).

## 2. Canonical inputs (resolved at one pinned revision)

Per file 04 section 2: `master_work_list_items.json` (185 rows,
182 active) with its generator and rendered Markdown; the current
Grand Plan design and GP-G / FAR items and aliases; the Dell
registry 00..99 with dispatcher/contract coverage; SYSTEM-001
SYS-C01..C44 plus later scoped receipts; the Director Review
Queue, PR head/status, exact-head CI, authority comments and merge
receipts; Feature Intake FI-001..FI-019 (with FI-013..FI-017
original goal-workspace bytes explicitly flagged missing where
they are, and FI-017 represented as source-reported design, never
as coded or credited); Unknowns UU-1..15, DC-1..11, decisions and
hold fences; runtime/census/test evidence with artefact hashes
where available.

**Part V dependency (named, not blocking):** Part V owns scoreboard
reconciliation — the crosswalk lineage that begins at Edition 1
file `01_SOURCE_CROSSWALK_CANDIDATES.json`. GP-E25 **consumes**
Part V's reconciled crosswalk as an input; it never reconciles
anything itself. Where Part V's output has not landed, the reducer
takes the crosswalk candidates as PROPOSED-class input and labels
every derived edge accordingly (see section 4).

## 3. The snapshot reducer (build slice S1)

One deterministic reducer: same canonical source bytes + same
selection parameters → same content identity (a hash over the
canonical read model). Read-only against GitHub. Untrusted source
text cannot control scripts or host permissions. Missing GitHub
data yields `EVIDENCE_UNAVAILABLE`, never a fabricated count.

Read model fields (file 04 section 2): `schema_version`,
`github_snapshot_time`, `source_main_sha`, `source_blob_shas`,
`retrieval_coverage`, `unresolved_sources`, `nodes`,
`typed_edges`, `belts`, `contradictions`, `perspectives`,
`derived_metrics`. Every fact carries source refs.

## 4. Identity, status, and edge law (summary of record)

Nodes are typed and namespace-prefixed (`mwl:`, `dell:`, `sys:`,
`gp:`, `far:`, decision/evidence/PR/perspective/actor classes) —
never a plain title as identity (file 04 section 3). Status is
**multidimensional** — PLAN readiness, CODE lifecycle,
CERTIFICATION scope, RUNTIME availability, RISK severity,
sovereign gate — and a status in one dimension never overwrites
another or moves a count. Edges are typed (IMPLEMENTS,
REQUIREMENT_OF, DEPENDS_ON, PRODUCES, EVIDENCED_BY, VERIFIED_AT,
BLOCKED_BY, ALIAS_OF, SUPERSEDES, FEEDS, DISPLAYED_AS,
REVIEWED_BY), each with provenance and confidence class
VERIFIED / INFERRED / PROPOSED; inferred edges never enter
canonical counts or executable dependency gates until a reviewer
confirms them (file 04 section 4).

## 5. Build slices (code stage, in order)

- **S1 — snapshot reducer.** Offline, standard-library, pinned
  revision; emits the read model + content identity. Acceptance:
  byte-identical output across two runs on identical inputs, in a
  fresh clone.
- **S2 — static exported view.** The seven views of file 04
  section 5 (Blueprint Map, Two Belts, Connection Web, Sequence,
  Sync Mirror, Future View with persistent PROJECTION watermark,
  Pending Edits) rendered from one snapshot, labeled `AS_OF` with
  the exact pin. Two Belts keep independent denominators; the
  canonical MWL number displays as its own strict count.
- **S3 — live revalidation.** A changed main or PR head marks
  affected evidence STALE until re-read; offline shows the pinned
  snapshot and its age and disables actions that require current
  authority.
- **Out of scope until separately authorized:** Pending Edits
  submission. Drafts stay local and owner-scoped; submission only
  through an authenticated, reviewed connector pathway that has
  been independently validated (file 04 section 5G). No slice of
  GP-E25 writes to the register, to GitHub, or to the Nursery.

## 6. Acceptance

File 04's 15-case UI acceptance, run against the built surface at
its exact head, plus the S1 determinism proof. GP-E25 carries no
register row of its own in Part 0's assignment and claims no MWL
credit; its completion is recorded in this Part's closing package
as a circuit delivery, and any register treatment is Part V's /
the landing session's act, not this lane's.
