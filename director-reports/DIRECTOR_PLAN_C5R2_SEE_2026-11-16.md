# DIRECTOR PLAN — C5R.2 SEE: Complete Nursery visibility

**Status:** PLAN DRAFT — independently reviewable, not approved implementation or completed PLAN credit.
**Author:** Director (ChatGPT), 2026-11-16.
**Plan authority:** \`director-reports/C5_REPLAN_2026-11-15.md\`, §3.2, §4, AC-2.1–AC-2.4.
**Dependency:** C5R.1 HOLD must be merged and its read-path/count invariants retained; C5R.3 ORGANIZE comes afterward.
**Owner of production changes and merges:** Uni. **Independent proofreader:** Keeper. **Overseer:** Ace.

## 1. Source-grounded problem

The canonical proposal store is the owner-specific \`Nursery.proposals\` dictionary in \`form/dell_matrix/nursery.py\`. \`Nursery.pending()\` selects only pending items; \`Nursery.summary()\` reports pending and all-status totals. Current persisted records include pending, confirmed and rejected. Archive/restore is **not implemented** and belongs to later C5R.5.

\`Program.list_proposals()\` in \`form/open.py\` returns pending proposals only; \`Program.ranked_proposals()\` orders those proposals through the current preference/affinity ranking. In \`form/repl.py\`, \`_show_proposals()\` prints at most 20, while \`rank\` prints at most 12. C5R.1 made those counts truthful, but did **not** provide stable pagination, complete field search, or all-status browsing. Do not mistake an honest subset for complete access.

## 2. Single read authority

Add one *read-only* query service over the existing owner-bound Nursery store; Program provides a thin wrapper, and the REPL calls that wrapper. Do **not** add a sidecar store, new proposal authority, writable search index, or second ranking implementation. Querying must never call \`save\`, \`confirm\`, \`reject\`, or any confirmation/placement operation.

Every response includes: owner binding, canonical snapshot/version identity, requested filter and sort, matching \`total\`, returned \`shown\`, exact stable proposal IDs, page size, \`next_cursor\` or exhausted flag, and explicitly named missing IDs when relevant. Empty results say \`shown=0, total=0\`, never an unexplained blank screen.

### 2.1 Stable pages and freshness

- Define a complete deterministic key such as \`(created, id)\`; ID must be the final tie-break. Status and filter semantics are explicit.
- A fixed unchanged snapshot, same filter and same sort yields byte-identical ordered IDs. A 1,000-proposal traversal returns exactly all matching IDs, once each.
- Cursor binds owner, filter, sort, last key and snapshot/version. Cursor changes from an incompatible query, malformed cursor, or stale underlying generation produce typed refusals, not partial success.
- \`Nursery._seen\` currently represents a saved/loaded owner-file SHA-256. Investigate freshness against external writers before adopting it as the query generation: an old in-memory instance must never pretend to represent a new on-disk version. A changed generation between pages yields \`STALE_CURSOR\` with restart guidance, never gaps or repeats.
- Page size is a transparent bounded work parameter, **not** retention control. Refuse invalid or excessive page sizes explicitly; never silently reduce the requested size.
- No cross-owner cursor use. The cursor is not an authorization token; owner checks must originate in the trusted Program boundary.

### 2.2 Search all fields

Start with deterministic Unicode \`casefold\` substring matching (document any normalization choices). Read canonical saved values, not label-only search. Cover ID, label, words, kind, parent IDs, reason, origin, detail, each goal, created, status and persisted lineage/supersession IDs. Document a policy for numeric affinity/harmony and future organization fields; do not silently claim coverage of a field not indexed. Organization fields, once actually implemented in C5R.3, are included by the same field enumerator.

Two proposals with identical labels remain separate hits by stable ID. Search covers **all current statuses**, including rejected; it must not implicitly restrict to pending.

### 2.3 ID-set retrieval

Use direct lookups in the owner Nursery dictionary, never the G-11 path with its known >16-ID restriction. For requested sequences of 1, 16, 17, 100 and 1,000 IDs, return the found set in declared order and individually named missing IDs. Define whether duplicate input IDs are retained or deduplicated and expose that policy. No hidden cap, phantom successes, or silent truncation.

### 2.4 Canonical public door

Add narrow, nonconflicting REPL forms for browse, search and retrieve-by-ID, plus help text. Keep existing \`proposals\`/\`nursery\`/\`pending\` and \`rank\` commands backward compatible. Print the filter, shown/total, stable IDs and a usable continuation command. Do not invent \`archived\` status before C5R.5. Confirming an item stays exclusively in the existing acceptance-policy path.

## 3. Failing-first tests and acceptance matrix

**Proposed new registered suite:** \`form/nursery_c5r2_see_test.py\`. Pin the BEFORE behavior: existing REPL cannot navigate past the first 20 proposals, rank stops at 12, and complete field-search is unavailable.

- **AC-2.1:** At least 1,000 canonical proposals; mixed pending/confirmed/rejected; duplicate labels; tied created stamps. Traverse all matching pages. Assert exact set and stable order on two runs, no repeats/missing IDs, immutable item payloads.
- **AC-2.1 freshness:** Mutate the canonical owner file through a separate legitimate instance between pages. Cursor must refuse as stale; retry from the beginning succeeds. Malformed and cross-owner cursors refuse without information leakage.
- **AC-2.2:** Search term in every supported stored text field; distinct IDs with identical labels both appear. Include Unicode casefold cases; named nonexistent IDs are reported individually.
- **AC-2.3:** Unfiltered browse, status-filtered browse, rank, existing proposals, all-empty results and full-search results print truthful \`shown/total\` and filter semantics through the **real REPL dispatch path**.
- **AC-2.4:** Direct ID retrieval across 16→17→100→1,000 items, with mixed found and missing IDs; no G-11 field cap inherited.
- **Read-only safety:** Compare the raw Nursery file digest, proposal status map, count and all record content before/after querying. No write, confirmation, reject, removal or reshaping.
- **Compatibility:** Legacy persisted Nursery data loads, and pre-existing C5R.1/family suites remain green. New suite registered in canonical \`form/regress.py\`.

Use deliberate defect-restoring mutants (remove cursor version guard; truncate results; collapse equal labels; omit a searchable field), and require the suite to reject each. Avoid asserting fabricated wall-clock performance. Before any implementation is admitted: failing-first → bounded repair → focused/neighbor suites → quiet full regression forward/twice/reverse at the **final head** → exact-head CI → Keeper independent confirmation → Director disposition → Uni-only §32 merge → merged-main verification.

## 4. Explicit exclusions and open review questions

This slice provides discovery, browsing and search, not topic/tag editing, ranked formula S, archive/restore, duplicate-merge operations, or AI organizer authority. Those remain C5R.3–C5R.6.

**Uni + Keeper must independently decide before execution:** (1) cursor version is file SHA versus canonical snapshot hash, with a first-hand test of an external-writer stale instance; (2) REPL grammar avoiding existing command prefixes; (3) numeric-field search interpretation and whether to search nontext data; (4) default sort and memory/resource bound with honest refusal. Record answers with code anchors, not opinions.

**Proofread result required:** SOURCE_MATCH / CORRECTION_REQUIRED / EVIDENCE_MISSING, exact source paths, and AC-by-AC acceptance before marking this a ready PLAN object. No PLAN or CODE completion credit is granted by this draft or its PR.