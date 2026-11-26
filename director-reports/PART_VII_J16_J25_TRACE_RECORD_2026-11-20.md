# PART VII — J16–J25 SOURCE→TEST TRACE RECORD — 2026-11-20

PR #502 (Part VII — Execution Order), branch `uni/part-7-execution-order`.
Method: independent source investigation (Lane C, 2026-11-20) with anchors
verified in source and tests, followed by execution runs of every mapped
suite at the Part VII head (Lane C2 finish, same night). A journey is
VERIFIED only where source and an executing test agree; discrepancies are
recorded as found, never smoothed over.

## Companion evidence built this circuit

- `director-reports/PART_VII_DAG_EDGE_LEDGER_2026-11-20.json` —
  machine-checkable transcription of `08_DEPENDENCY_DAG.json`:
  28 nodes, 53 edges, topological order carried, authority gates recorded
  verbatim and marked non-edges, source pinned by sha256
  `8e0f75b9ff50bc9acfb37008899fa72c18cbd7b9c0de85573a080fd976da8a26`.
  Divergences annotated per plan §7 / Director D1–D4 (7044797269):
  D1 = E13→E22, E14→E22, E15→E22; D2 = E13→E14; D3 = E20→E23;
  D4 = structural (exact 18-node §5-unmapped set).
- `form/dag_edge_ledger_test.py` — suite `DAG_EDGE_LEDGER`, registered in
  `form/regress.py` LIST this circuit. Results: **31/31 GREEN**;
  harness `--passk form.dag_edge_ledger_test:smoke 3` → **3/3 GREEN**
  (31/31 in each fresh copy). Mutation check: removing the divergent
  D2 edge (GP-E13→GP-E14) dropped the suite to **28/31** with exactly
  the expected failures (`edge_count_53`, `edge_sets_equal`,
  `divergent_edges_annotated_exactly`); inverse-edit revert restored
  **31/31** and the ledger's 53 edges. Coverage includes one negative
  bypass test per divergent edge (5 edges, refused-without /
  control-with) and §5-bypass demonstrations for D1/D2/D3: a §5-only
  evaluator waves the state through; the Edition 1 ledger refuses.

## Journey verdicts

| Journey | Verdict | Execution tally (this record) | Anchors |
|---|---|---|---|
| J-16 Nested Idea → promote | VERIFIED | `form.track_d_td2_test` **33/33 GREEN** | `form/mandell/unit_containment.py:359` promote_unit (supersedes CONTAINS edge, history preserved); `form/open.py:1477`; TD-2 promote checks :181-196, REPL promote :412 |
| J-17 Undo/redo | VERIFIED (session scope) — SCOPE DISCREPANCY vs journey file 06 | `form.mandell.undo_redo_depth_test` **53/53** | `form/open.py:193/199` stacks are in-memory fields; `form/dell_matrix/needs.py:337/428`. File 06's "across save vs session boundary" exceeds the settled Q-LC.1 session-local contract; cross-boundary retention is row #135's retained remainder, not an implementation failure |
| J-18 Cross-owner isolation / stale write | VERIFIED | `form.owner_namespace_collision_test` **12/12 PASS** | Suite D1–D5 + cross-process D2X, save-preserves-other; stale confirm refused in `form/nursery_confirm_race_test.py` (SM-31 lost_update_explicit); `form/graph_journal_crash_test.py` D2/D3 stale-dependent convergence |
| J-19 Exchange/import | PARTIAL — discrepancy | `form.step5_exchange_boundary_test` **20/20**; `form.step5b_exchange_durability_test` **21/21** | Content preservation + PENDING-only landing verified: `form/dell_matrix/exchange.py` build_packet :235, import_packet :692 (never confirms, protected-material screening, journal fail-closed). **Duplicate-replay idempotency NOT found**: import_id is a fresh uuid per import; no content-addressed dedupe in source and no replay test exists |
| J-20 Offline / no-AI session | PARTIAL — probe leg now executed | Piped REPL probe (this record): `printf 'personas\nmatrix personas\n' \| python3 -m form.repl --owner j20probe` → banner "Offline", roster + matrix rendered locally, clean EOF exit 0 | `form/dell_matrix/internet_gate.py:5` DEFAULT OFF for pure offline runs; REPL is a local process. Still no single suite executing the full J-20 session script end-to-end |
| J-21 Nursery at scale | VERIFIED (suite level) | `form.nursery_c5r1_holding_test` **13/13 PASS**; `form.nursery_c5r2_see_test` **44/44 PASS** | c5r1 :111-117 seeds 1,000 proposals; c5r2 :185-201 shown/total reconcile at 1,000. "Visual" = the SEE public browse path, not a GUI |
| J-22 Provider outage / reconnect | PARTIAL — discrepancy | No suite run: no anchor exists for the reconnect leg | Outage leg verified by source: `form/dell_matrix/inference_dock.py:79,1303-1313` sanitized provider_failure refusals; `form/dock_proposal_b_test.py`. **Reconnect / no-duplicate-confirmation leg: no source or test anchor found** |
| J-23 Plan change sync → Muse Space | DISCREPANCY — NOT BUILT in repo | — | GP-E25 appears only in the execution map + Part VII plan (records). No implementing source exists in `form/` on current main |
| J-24 Low-memory / portable workload | PARTIAL — discrepancy | Not re-run this circuit (benchmark existence is Lane C census) | C7.Profile timing benchmark exists (`form/c7profile_test.py`, DD-39, measured stage timings); **the GP-E26 memory-capped 0/1/100/1000 ladder probe is not built as a suite** — GP-E26 appears only in records |
| J-25 Protected-value canary | VERIFIED (mechanism) | `form.core_i_arg_gate_test` **92/92** | Repo-wide search for `CANARYZZ_9f3e_UNIQ` returns exactly 2 files (`form/core_i_arg_gate_test.py:58`, `form/d1_unsupported_arg_gate_test.py:68`), asserted absent from error blobs/gate lines. The single-canary all-surfaces packet (receipts/API/history/logs as one artifact) is rehearsal-stage work, not yet assembled |

## Open discrepancies carried forward (not closed by this record)

1. J-19: exchange duplicate-replay idempotency — no dedupe mechanism, no
   replay test. Build item.
2. J-22: reconnect / no-duplicate-confirmation leg — no source or test
   anchor. Build item.
3. J-23 / GP-E25: NOT BUILT — records only, no `form/` source. This is
   Part 0's GP-E25 S1–S3 scope; Part VII records the absence, it does
   not absorb the build.
4. J-24 / GP-E26: memory-capped ladder suite not built. Build item.
5. J-17: journey file 06 wording exceeds the settled Q-LC.1 session-local
   contract; the excess belongs to row #135's retained remainder.
6. J-20: full-session script suite still absent; the REPL probe above is
   a leg, not the whole journey.
7. J-25: all-surfaces canary packet not yet assembled as one artifact.

## Evidence class

Suite tallies above are direct module runs in the Part VII clone at the
branch head (INTEGRATION / HIGH-FIDELITY DISPATCH class), plus the
harness `--passk` fresh-copy proof for the new ledger suite. The J-20
probe is a real piped-stdin REPL process (PUBLIC_ENTRY_PATH leg). No ×3
campaign was run in this circuit; no credit is claimed by this record —
it is evidence for the Part VII plan-confirm package.
