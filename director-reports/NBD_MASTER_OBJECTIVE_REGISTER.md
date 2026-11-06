# NBD MASTER OBJECTIVE REGISTER — DellMatrix / Mandell / DuoBeta

**Date:** 2026-11-04 · **Mode:** A — Planning / Reconciliation (Director Addendum, 2026-11-04)
**Baseline:** main `7e593e0a5b5a47a36111734e35b6464f61b511b6` (verified at reconciliation).
**Authority:** ACE (Overseer) > DIRECTOR > UNI. This register authorizes nothing by itself.

## How to read this register

- **IDs.** `72-nn` = the original 72-item inventory (2026-11-03, stored verbatim at `DELLMATRIX_ORIGINAL_72_INVENTORY_2026-11-03.md`). `SM-nn` = SUS Ω-64 inventory items that do not duplicate a 72 item. `V-nn` = Ace's vision objectives (2026-11-04). `G-nn` = standing objectives established by rulings/directives outside both inventories. Duplicates are folded into one entry with all source references preserved.
- **Status.** ACTIVE (authorized, underway) / COMPLETED (verified closure: implementation on main AND a proving suite or Director certification) / PARTIAL (real mechanism + evidence, acceptance not fully exercised) / OPEN (unstarted or unverified) / INVESTIGATION (evidence-gathering class) / BLOCKED (awaiting a decision, environment, or dependency) / DEFERRED (future objective, not authorized) / DECLINED (historical record, not reactivated).
- **Certification is recorded separately from implementation status.** Merged ≠ tested ≠ certified ≠ real-world validated.
- **Authorization.** Only three work lines are authorized at this register's date: **TD-2** (active circuit), **B-2** (parallel investigation), and the **Q1 Exchange/recovery boundary audit**. Everything else requires its own authorization.

## Reconciled totals

| Source series | Entries | Completed | Partial | Open | Investigation | Blocked | Deferred/Declined |
|---|---|---|---|---|---|---|---|
| 72-item inventory | 72 | 16 | 49 | 3 | 3 | 1 | 0 |
| SUS Ω-64 (unique after dedupe) | 8 | 0 | 0 | 8 | 0 | 0 | 0 |
| Vision (V) | 13 | 0 | 0 | 0 | 0 | 1 | 12 |
| Standing (G) | 10 | 0 | 0 | 4 | 0 | 1 | 2 (+3 active: G-01, G-02, G-03 counted OPEN-authorized) |

SUS Ω-64 disposition after dedupe (for traceability): 11 COMPLETED (SM-01, 03, 05, 06, 11, 16, 39, 49, 50, 62, 54 — folded into 72-01, 72-08, 72-02, 72-08, 72-06, 72-05, 72-04/41, 72-55/56/57, 72-55, 72-64, 72-04 respectively), SM-04 PARTIAL (folded into 72-07), SM-28 PARTIAL (folded into 72-37), SM-35 PARTIAL (folded into 72-28), SM-02 INVESTIGATION (folded into 72-03, BLOCKED), SM-20 INVESTIGATION closed-by-ruling (folded into 72-71), SM-57 INVESTIGATION closed-no-defect (folded into 72-68), 47 OPEN of which 39 fold into 72 items and 8 remain unique below.

## ACTIVE — authorized work

| ID | Objective | Status | Certification | Evidence | Next action |
|---|---|---|---|---|---|
| G-01 (= 72-39, SM-26/28) | TD-2 containment operations: Program-level nest / promote / reparent through canonical bindings, REPL-first; SemanticGraph sole containment authority | **ACTIVE** — authorized (Director Mode D, 2026-11-04); not yet built | None (not submitted) | Graph API verified present (`form/mandell/semantic_graph.py`: nest/unnest/reparent + navigation); TD-1 foundation CERTIFIED (foundation for bindings) | Build TD-2 to ONE frozen candidate, then STOP for Director certification |
| G-02 (= 72-12, SM-14) | B-2: deeper per-Dell English reachability validation for the 63 NO_ROUTE_FOUND Dells | **ACTIVE** — authorized investigation (parallel queue) | Investigations ACCEPTED (2026-11-04); B-2 held PROVISIONAL pending per-Dell evidence | Census (PR #280): 37/100 reachable, 63 NO_ROUTE_FOUND; "71 unreachable" claim retired | Per-Dell verb-alias probes; no Dell promoted to an implementation queue without its probe |
| G-03 (= 72-30 audit leg, SM-33/34) | Q1: Exchange/recovery owner-boundary AUDIT (audit only; no modification) | **ACTIVE** — audit authorized (Mode D Q1, 2026-11-04); modification NOT authorized | n/a | TD-1-R2 certified scope excludes Exchange writes (documented fence) | Perform the audit; report before any modification proposal |

## The 72-item inventory, reconciled (72-01 … 72-36)

| ID | Objective (origin: 72-inventory 2026-11-03; priority/class as inventoried) | Status | Certification | Present evidence | Next action |
|---|---|---|---|---|---|
| 72-01 | Finalize Studio browser acceptance on integrated revision (P0/C) (= SM-01) | COMPLETED | CERTIFIED WITH NOTED EXCEPTIONS | PR #258; 16/16 Chromium on integrated revision; driver later extended (SM-49/SM-54) | Retained exceptions only (no human session; no network deployment) |
| 72-02 | Reconcile merged Core I gate with INDEX/archival status (P0/C) (= SM-05) | COMPLETED | CERTIFIED WITH NOTED BOUNDARIES | PR #259 merged at the inventory's own baseline 4df2246; INDEX row carries disposition; suite 92/92 registered | None |
| 72-03 | Independently reproduce DAF-09 session-escape cleanup (P0/C) (= SM-02) | **BLOCKED** | Session-escape WITHHELD | Director's independent result stands 19/22; Uni local suite 23/23 post-ESRCH (different check set, §31.3 — does not resolve) | Director-environment reproduction per his instrumentation directive |
| 72-04 | Close or precisely retain identical-label/unit-ID ambiguity in Growth lenses (P1/C) (= SM-39, SM-54) | COMPLETED | T2 CERTIFIED W/ EXCEPTIONS; limitation LIFTED for unit-keyed path incl. round-trip | PRs #220/#225/#276/#277; unit-identity + persistence suites registered | Legacy label-only ambiguity retained as documented boundary |
| 72-05 | Repair Dell 37 REPL failure visibility (P1/C) (= SM-16) | COMPLETED | CERTIFIED (bounded) | PR #263; suite 13/13 incl. literal REPL subprocess | None within scope |
| 72-06 | Review English Intent.args as separate end-to-end contract (P1/C) (= SM-11) | PARTIAL | SM-11 CERTIFIED (bounded: count-args class); Class E spelled-out-count defect FIXED (PR #309 merged, Director SCOPED_PASS 2026-11-05 22:30 CST); Class D zombie zoom/weather args repaired (mandel carries operand, dead ref/condition args retired; suite 21/21, mutant killed, regress x3 240/240 GREEN) | `translate_intent_args_test` proves the confirmed dropped-count class; census in PR #308 (Director-confirmed bounded investigation) not yet merged; full-contract review ordered in ruling Q-C3 has no report | Bounded Intent.args census circuit |
| 72-07 | Dispose remaining per-scope admission/registry certification requests (P1/C) (= SM-04) | PARTIAL | PARTIAL ADMISSION (A1 retained; A2 NOT certified; A3 demonstrated scopes only) | Step 14 report + INDEX sync (PR #270) | Further disposition is Director-time; restrictions preserved |
| 72-08 | Preserve CI-only #233 + long-lived certification artifacts (P1/C) (= SM-03, SM-06) | COMPLETED | DIR-CERT-2026-11-02 stands on this mechanism | Verified live: PR #233 OPEN, DO NOT MERGE, CONFLICTING (expected); evidence bundle in-repo; artifact expiry 2027-02-01 with durable in-repo copy | Standing preservation duty (compliant) |
| 72-09 | Harden Director–Uni next-best circuit handoff (P1/E) (= SM-07) | PARTIAL | Workflow ADOPTED (DIR-WF-001); no completion certificate (process item) | WORKFLOW.md + validate_packet.py exist; hard terminal-green merge gate is standing law (post Cycle-5 incident) | Standing practice, not a circuit |
| 72-10 | Stress Seed grammar + error precedence (P1/I) (= SM-58) | PARTIAL | DAF-07 CERTIFIED within tested grammar scope | PR #165; af1/af2 suites (chainlinks, delimiters) | Full stress battery (nested delimiters, escaped Unicode, ManifestSet, no-mutation-on-reject) as one suite — not evidenced |
| 72-11 | Reconcile English create + direct REPL handlers with canonical Mandell (P1/I) (= SM-12, SM-13) | INVESTIGATION | Core I contract review ACCEPTED (investigation, not closure) | Partial parity transcripts (PR #256); D1 recon suites | Bounded English-vs-Mandell comparison census; prove differences before any routing change |
| 72-12 | Deepen reachability for already-supported English actions only (P2/E) | PARTIAL | See G-02 | Census done (37/63); deepening = B-2, authorized and active (G-02) | B-2 execution |
| 72-13 | Audit 17 typed-signature error/coercion contracts (P1/I) (= SM-17, SM-19) | PARTIAL | D1-TYPED-52-53 CERTIFIED W/ EXCEPTION; both arg gates CERTIFIED W/ BOUNDARIES | 17 typed Dells (8, 51–58, 67–69, 84–88); deep audit exists for 52/53 only | Per-signature contract audit across all 17; no signature expansion without authorization |
| 72-14 | Strengthen Core I single/chain/intercept/live refusal parity (P1/E) | COMPLETED | CERTIFIED WITH NOTED BOUNDARIES | PR #259 suite incl. literal REPL session: mixed chain, neighbours execute, refusals visible | None within scope (refusal paths only; Core I typed function not certified) |
| 72-15 | Challenge Core II unsupported-role control-head short circuits (P1/E) | COMPLETED | CERTIFIED WITH NOTED BOUNDARIES | PR #253; suite 45/45; heads 60/62–66 never execute bodies on refusal; Join preserves refusal | None within scope |
| 72-16 | Reconcile legacy flow executor with canonical chain ownership (P2/I) (= SM-15) | INVESTIGATION | None | Caller census answered this pass: `english_composer.py` is a LIVE caller of flow_executor (not dead legacy); gate ruling Q-D4 excluded it | Behavior comparison vs chain_exec + no-second-authority determination |
| 72-17 | Remove/relabel literal Show placeholder output (P2/I) | INVESTIGATION — COMPLETE 2026-11-05 (DIRECTOR_REPORT_72_17_SHOW_SENTINEL): sentinel __RENDER__ intercepted cleanly by the REPL (real render shown); USER-VISIBLE in the Studio console raw-JSON dump — bounded defect confirmed. REPAIR (R-B) 2026-11-06 (DIRECTOR_REPORT_72_17_RENDER_DIRECTIVE_REPAIR): structured result directive='render' replaces the token in messages; suite 15/15, mutant killed, regress x3 GREEN 241/241; merged under Ace FIX-FIRST (Ace-authorized, NOT Director-certified), confirmation requested Q-17R.1 | None | Adjacent honesty evidence only (Step 6); bare `09[Show]` not probed | One-probe investigation |
| 72-18 | Audit message-only Dell descriptions for truthful operations (P2/I) (= SM-23) | PARTIAL | None specific | Proof cards classify 17[Shadow]/43[Fallback] truthfully with actual effects | Systematic audit of all comparable message-only operators |
| 72-19 | Preserve first-failure provenance through mixed chain receipts (P1/E) | PARTIAL | Step 7 CERTIFIED W/ EXCEPTIONS; Step 8 PARTIAL | PRs #186/#188; per-frame provenance proven | Final composition proof retained as outstanding in the dispositions table |
| 72-20 | Challenge Branch/Parallel/Sequence/Join reported guarantees (P1/I) (= SM-18) | PARTIAL | Step 7 CERTIFIED W/ EXCEPTIONS (bounded) | Join/Until/ForEach proven; chain_exec sequential by construction | Set-wide guarantee recheck + explicit no-true-concurrency contract statement |
| 72-21 | Stress Until/While/ForEach bounds + nested control inheritance (P1/I) (= SM-18) | PARTIAL | DIR-F13 CERTIFIED W/ EXCEPTIONS; Step 7 bounded | Until/ForEach bounds proven | While-specific bounds; nested skip inheritance |
| 72-22 | Reverify Try/Catch error consumption + same-frame reuse (P1/E) | COMPLETED | CERTIFIED WITH NOTED EXCEPTIONS | PR #198; suite 25/25 (consume-once, caught_history, no resurrection) | None within scope |
| 72-23 | Challenge Commit/Revert exact state + side-effect boundaries (P1/I) | PARTIAL | Step 8 PARTIAL; Step 11 wording CERTIFIED W/ EXCEPTIONS | PRs #188/#204; no atomic/ACID claim exists or is permitted | Failure-injection boundary circuit if directed |
| 72-24 | Stress Diff/Set missing-vs-None + baseline handling (P1/E) | COMPLETED | Step 9 + DIR-F15 CERTIFIED W/ EXCEPTIONS; null-membership exception LIFTED | PRs #190/#200; suite 24/24 | None within scope |
| 72-25 | Protect Define/Alias/Compose against failed-run persistence (P1/E) | PARTIAL | Step 10 CERTIFIED W/ EXCEPTIONS (Compose only) | PR #202; Compose run-before-publish proven | Define/Alias failed-run non-publication + save/reload survival check |
| 72-26 | Stress per-member ManifestSet + typed chainlink transport (P1/E) (= SM-21) | PARTIAL | AF-1 parity pinned within Core I certificate scope | Chainlink per-member transport proven | ManifestSet member-isolation proof (one failing member, valid members execute, exact receipts) |
| 72-27 | Recheck Guard/Assert failure propagation across control frames (P2/E) | PARTIAL | None specific | Per-Dell/registry coverage exists | Dedicated frame-propagation recheck |
| 72-28 | Audit Program/Nursery pair-atomic save + fresh-process load (P0/E) (= SM-35) | PARTIAL | TD-1-R2 CERTIFIED within canonical save/bind scope | persist_rest + crash matrix + DCC-XVII; R2 owner lock | Pair-atomic crash proof between Program and Nursery staged writes (never a hybrid) — not evidenced as one closed proof |
| 72-29 | Stress checkpoint sealing, rollback, directory-sync failure (P1/E) (= SM-36) | PARTIAL | None | checkpoint_generation + rollback suites; eager-convergence law | Failed-fsync / directory-sync / missing-generation injection pass |
| 72-30 | Challenge Exchange journaled import/recovery + receipt disposal (P0/E) (= SM-33, SM-34) | PARTIAL | DAF-04/05, Step 5b/DAF-06/A1, DIR-F12 all CERTIFIED W/ EXCEPTIONS | PRs #166/#178/#193; durability suite 21/21; journal-receipt suite 20/20 | **Q1 boundary audit (G-03, authorized)** — Exchange writes sit outside the R2 owner lock |
| 72-31 | Check Nursery optimistic concurrency + duplicate confirmation (P1/E) (= SM-31) | PARTIAL | None | Confirm crash matrix proves crash windows + stale-journal refusal | Two live stale instances racing confirm — not directly evidenced |
| 72-32 | Validate semantic-graph journals against derived Program effects (P1/E) (= SM-25) | PARTIAL | None | p2_dsc1 journal proof (integrity, fail-closed recovery) | Crash between graph write and derived-effect write, proven to fail closed together |
| 72-33 | Verify supersession crash + acceptance lineage across restart (P1/E) (= SM-30) | PARTIAL | None | supersession_failure_test exercises compensation + fresh-process recovery | Present suite evidence for ruling, or extend lineage assertions |
| 72-34 | Test owner namespace collision + foreign-state rejection (P1/E) | PARTIAL | None | Cross-owner isolation + foreign-state refusal proven (persist_full_roundtrip) | Normalized owner-name collision case specifically |
| 72-35 | Recheck atomic-write orphan-temp + rollback cleanup bounds (P2/E) | PARTIAL | DCC-XVII repair ACCEPTED w/ documentation exception (provisional) | atomic_write: sibling temp + fsync + replace; temps marked and swept | Boundary-by-boundary failure injection (write/fsync/replace) as a dedicated suite |
| 72-36 | Roundtrip persistent envelopes under corrupt/unknown versions (P1/I) | PARTIAL | None | Core II envelope roundtrips at version 1; unknown fields ignored by design | Malformed/unknown VERSION refusal without partial activation |

## The 72-item inventory, reconciled (72-37 … 72-72)

| ID | Objective (origin: 72-inventory 2026-11-03) | Status | Certification | Present evidence | Next action |
|---|---|---|---|---|---|
| 72-37 | Plan + verify the Plane-to-Idea bridge / Track D (P1/E) (= SM-27, SM-28) | PARTIAL | TD-1 CERTIFIED WITH NOTED BOUNDARIES; TD-1-R2 CERTIFIED (save/bind scope) | PRs #278/#283/#286; binding + R1 + R2 suites registered (24/10/23) | Containment half = TD-2 (G-01, ACTIVE) |
| 72-38 | Reconcile Idea + semantic-graph node identity through lifecycle (P1/I) (= SM-26) | PARTIAL | None for the item as a whole | Graph + Idea modules present; identity-adjacent suites registered | End-to-end reconciliation proof (rename/create/save-reload/supersede/graph refs, duplicate/orphan assertions) |
| 72-39 | Prove nested Idea parent/child + promotion invariants (P2/I) | PARTIAL | None (TD-2 not submitted) | Graph containment API verified present; graph suite registered | = TD-2 (G-01): Program-level ops + proofs (3-level nesting, second-parent refusal, sandbox isolation) |
| 72-40 | Enforce active/faded/superseded participation across all consumers (P1/E) (= SM-29) | PARTIAL | None | canonical_lifecycle boundary exists, fail-closed on UNKNOWN/malformed, named consumers covered | Consumer census proving EVERY resonance consumer routes through the boundary |
| 72-41 | Reconcile GrowthForce label identity with stable Plane unit IDs (P1/C) | COMPLETED | T2 limitation LIFTED within unit-keyed path incl. round-trip | PR #276 (SM-54) + PR #220; growth unit-identity suites registered | Retained: legacy label-only records ambiguous by design |
| 72-42 | Stress knowledge selection, scope, lineage, dependencies (P1/E) (= SM-37) | PARTIAL | None | Selector present; KIE-I eligibility proven; several suites reference it | Dedicated stress suite asserting the full exclusion set as one contract |
| 72-43 | Trace cause/depend/provenance explanations to real graph evidence (P2/E) (= SM-38, SM-64 theme) | PARTIAL | None | knowledge_influence present; referenced by kie_i_test only (eligibility scope) | Explanation audit: every why_used/why_not_used resolves to graph evidence |
| 72-44 | Test resonance/harmony-to-Nursery proposals at the human gate (P2/I) | PARTIAL | None (Track C covers dock verbs, not resonance candidates) | resonance.py present; PENDING-gate machinery proven on the dock line | Gate-specific suite on the resonance path (pending-until-approval; rejected cannot alter accepted) |
| 72-45 | Preserve epistemic source/status through views + spatial consumers (P1/E) | PARTIAL | None | perspective_views + UNKNOWN-preservation suites registered | Spatial-consumer leg of the acceptance |
| 72-46 | Verify dock COMPREHEND/relate_field through policy + Nursery (P1/E) (= SM-44) | COMPLETED | ACCEPTED WITH LIMITATIONS (scripted judge; integration contract, not live-model quality) | PRs #248/#249; track_c_dock_verbs_test registered | Live-model semantic quality unproven and unclaimed |
| 72-47 | Stress stale field-snapshot + agent reconnect boundaries (P1/E) | PARTIAL | None | agent_coordinator present; coverage incidental via dock suites | Dedicated stale-snapshot + reconnect authority suite |
| 72-48 | Exercise agent host-bound idempotency, retries, conflicting envelopes (P1/E) (= SM-45) | PARTIAL | None | agent_coordinator + dock_transport suites | Conflicting-envelope refusal as a named proof (duplicate id + conflicting payload) |
| 72-49 | Challenge AcceptancePolicy delegation, expiry, revocation chains (P0/E) (= SM-32) | PARTIAL | None | acceptance_policy present; charter/dock suites reference it | **P0 gap:** revocation-chain invalidation across restart + retry as one contract |
| 72-50 | Prove DirectorSession remains recommendations-only (P1/E) (= SM-46) | PARTIAL | None | director_session present; exercised indirectly via charter/session suites | Negative-path suite: a recommendation can never confirm a proposal |
| 72-51 | Reconcile DuoBeta outcome evidence + learning ledger persistence (P1/E) (= SM-41) | PARTIAL | None | duobeta_learn present; three suites registered (existence verified; assertion-level coverage of the full chain not verified) | Assertion-level audit: Observe→Propose→Gate→Apply→Save/Reload = exactly one bounded durable effect |
| 72-52 | Test learned-score saturation + opt-out reversibility (P2/E) (= SM-42) | PARTIAL | None | Same suites as 72-51 | Dedicated saturation / opt-out-restores-baseline suite |
| 72-53 | Harden provider errors, prompt/output validation, protected values (P0/E) (= SM-43) | PARTIAL | SM-20 investigation ACCEPTED; NO redaction build authorized | inference_dock present; sanitize/InternetGate suites; SM-20 surface map (PR #280) | **P0 gap:** hostile/malformed provider-output hardening end-to-end; any build needs Director authorization |
| 72-54 | Keep selfgrow auxiliary ledger isolated from canonical state (P2/I) | PARTIAL | None | selfgrow present; isolation asserted inside wiring/satellite suites | Dedicated isolation proof with explicit error classification |
| 72-55 | Trigger real-browser acceptance for relevant Form runtime changes (P1/E) (= SM-49, SM-50) | COMPLETED | CERTIFIED WITH NOTED EXCEPTIONS (PR #258 boundary) | studio-browser-acceptance workflow triggers on gui/** + the Form runtime Studio drives; PR #262 widened triggers | Exceptions retained (automated Chromium, not a human session) |
| 72-56 | Add browser refusal / PARTIAL / skipped-atom acceptance paths (P1/E) (= SM-49) | COMPLETED | Covered by SM-49 certified-with-exceptions acceptance (29/29) | browser_acceptance.py SM-49 section verified in source | None within scope |
| 72-57 | Drive Growth + Console tabs in browser acceptance (P1/E) (= SM-49) | COMPLETED | Same as 72-56 | Same driver, real UI path | None within scope |
| 72-58 | Regression-test Studio Host/Origin/token + malformed HTTP (P0/E) (= SM-51) | PARTIAL | CERTIFIED for trusted single-user localhost (network deployment prohibited) | PR #255; studio_security_test registered | Standing regression obligation for any future gui/server.py change |
| 72-59 | Test Studio state refresh, stale owner state, receipt reconstruction (P1/I) | PARTIAL | None | gui_api_test drives the real server (execute→state round-trip, growth fidelity) | Refresh/reopen legs: reopened sessions agree with canonical owner state, no phantom status |
| 72-60 | Prove identical executable semantics across GUI/API/REPL/Python (P1/E) (= SM-52) | PARTIAL | None | gui_api_test proves GUI/API through the public paths | REPL leg of the four-way equivalence |
| 72-61 | Improve Studio keyboard, focus, constrained viewport behavior (P2/E) (= SM-56) | PARTIAL | None | Keydown/focus handling present in app.js; viewport meta present; NO @media rules found in style.css (grep — unverified either way) | Constrained-viewport verification + browser-acceptance leg |
| 72-62 | Reconcile offline visual snapshot with canonical state; clear non-live label (P2/E) (= SM-55) | COMPLETED | None | visual.py labels output as snapshot in source; visual_ux_test asserts the wording | None within the stated acceptance |
| 72-63 | Stress 2D spatial placement, rendering, restore invariants (P2/I) (= SM-40) | PARTIAL | None | spatial_authority present; placement/lattice suites registered | Invariant set (finite coords, reserved origin, collision, restore) as one contract keyed to spatial_authority |
| 72-64 | Refresh stale in-use docs + README suite-count claims (P1/C) (= SM-62) | **OPEN** | None | SM-62 closed this at its revision (230); LIVE discrepancy verified in this pass: README still claims 230 suites, canonical LIST is now **235** | Small docs circuit: refresh counts from current main; preserve historical counts as history |
| 72-65 | Protect Form as source of truth vs frozen JS/preform drift (P2/E) (= SM-63) | PARTIAL | None | CORE_SCOPE.md documents src//preform/ as frozen; coverage suite guards registration, not imports | Automated import-drift guard (fail if live Form imports a frozen authority) |
| 72-66 | Deepen changed-file lint + Python-version compatibility checks (P2/E) (= SM-61) | PARTIAL | None | CI runs flake8 hard gate (E9,F63,F7,F82) + advisory exit-zero pass on 3.10/3.11 | Decide whether the advisory pass graduates — workflow call |
| 72-67 | Harden GitHub workflow permissions + pin third-party actions (P1/E) | **OPEN** | None | Verified in this pass: actions referenced by tag (checkout@v4, setup-python@v5), no SHA pins, no permissions: block found in form-smoke.yml | Least-privilege permissions + reviewed SHA pins across workflows |
| 72-68 | Reconcile regression discovery, suite registration, mutation detection (P1/E) (= SM-57) | COMPLETED | SM-57 investigation ACCEPTED (TIMEOUT verdict ruled defensible) | regress.py contract is self-enforcing (RED unless LIST covers every form/**/*_test.py); regress_coverage_test registered; --passk exists | None within the stated acceptance |
| 72-69 | Create repeatable low-memory + large-state performance baselines (P2/E) (= SM-59, SM-60) | PARTIAL | None | p2_perf_baseline.py exists (small-scale) but is NOT in the regress LIST or any workflow | Budgeted, repeatable harness with identical-workload comparison |
| 72-70 | Incrementally reduce oversized live-module coupling, no behavior change (P2/E) | **OPEN** | None | form/repl.py measured 4,583 lines in this pass; no bounded refactor evidenced | One bounded boundary at a time, characterization tests first — own circuit when authorized |
| 72-71 | End-to-end protected-value canaries across outward evidence surfaces (P1/E) (= SM-20) | PARTIAL | SM-20 investigation ACCEPTED; NO redaction build authorized | redaction.py + sanitize suites; SM-20 canary map (PR #280): seed echo is the one value-carrying field (same-party return); refusal diagnostics names-only | Full canary sweep not built; bounded by the SM-20 ruling — further work needs Director authorization |
| 72-72 | Automate morning-report reconciliation, staleness, next-best recommendations (P1/E) (= SM-09) | PARTIAL | None | validate_packet.py + its test exist in director-reports/workflow/; NOT wired into any GitHub workflow (grep-verified) | Decide CI wiring vs scheduled local run — workflow decision |

## SUS Ω-64 unique entries (no 72-item twin)

| ID | Objective (origin: SUS Ω-64 inventory, 2026-11-03) | Status | Certification | Present evidence | Next action |
|---|---|---|---|---|---|
| SM-07 | Strengthen exact-head / merge-tree / post-merge / fresh-clone gate reconciliation | OPEN | None | Inventory scope only; NOT_YET_ASSESSED in the run | Bounded workflow circuit when authorized |
| SM-08 | Make workflow resumable: last-good checkpoint + completed-circuit records | OPEN | None | Partially embodied in practice (completion envelopes, cycle checkpoints) — not verified as an objective | Formalize or accept practice |
| SM-09 | Standardize morning Director report format | OPEN | None | Embodied in the Ω-64 morning report; "not separately verified" per the run record | Folded operationally into 72-72's automation question |
| SM-10 (= SM-48) | Connect NBD ranking to real report status, dependencies, improvement candidates; deterministic stale-candidate detection | OPEN | None | Internal duplicate pair in the source inventory (SM-10 ≡ SM-48) — counted once here | Deterministic ranking circuit when authorized |
| SM-22 | Strengthen Dell 08 naming, slug collision, skin, legacy-label regression coverage | OPEN | None | D1 recon suites touch Dell 8 Create; this strengthening scope unassessed | Dell-08 deepening circuit |
| SM-24 | Reverify reserved-address refusal / honest unsupported behavior of Bridge and Embed | OPEN | None | Step 11 honesty line is adjacent evidence, not this scope | Bounded honesty recheck |
| SM-47 | Confirm BIMO/persona views remain advisory; cannot bypass host-bound authority | OPEN | None | personas.py BIMO metadata verified descriptive (slots never confer authority — agent_coordinator); no dedicated proof suite for this scope | Advisory-boundary proof; also a Psalm Matrix (V-10) prerequisite fact |
| SM-64 | Improve traceability from runtime behavior to receipts, outcomes, persisted evidence | OPEN | None | Theme overlaps 72-43/72-71; this end-to-end traceability scope unassessed | Traceability circuit when authorized |

## V — Ace's vision objectives (origin: Ace voice session + written plan, 2026-11-04; submitted PR #288)

All V items: **authorization = NOT AUTHORIZED — submitted for Director routing.** Technical and future-vision work are separately classified per the addendum: this section is the future-vision class.

| ID | Objective | Status | Certification | Present evidence | Next action |
|---|---|---|---|---|---|
| V-01 | Nursery proposal CARDS (visual, glanceable; confirm / reject / modify) | DEFERRED | n/a | Canonical Nursery machinery exists (nursery.py: pending/confirmed/rejected, dock-fed, per-owner); only the card presentation is future | Director routing |
| V-02 | Custom idea shapes in the Nursery (circle, square/box, triangle, custom-drawn outline) | DEFERRED | n/a | No shape machinery exists | Director routing; depends V-01 |
| V-03 | AI-suggested looks (semantic icons + shape language with category meaning) as Nursery proposals ONLY | DEFERRED | n/a | Dock proposal inlet exists (PENDING only) | Director routing; depends V-01 |
| V-04 | Nursery as THE primary decision screen (painting/building feel, fun, organized, never an info dump) | DEFERRED | n/a | Ace: most important page in the program | Director routing; design review before build |
| V-05 | SKY perspective (2D; ideas as clouds/shapes; persistent positions; same canonical data as ROOM) | DEFERRED | n/a | 2D spatial authority exists (72-63 partial); no SKY presentation | Director routing; depends 72-63 invariants |
| V-06 | ROOM perspective (3D; walkable; stackable/openable boxes; never stagnant-looking) | DEFERRED | n/a | No 3D presentation exists | Director routing |
| V-07 | Navigation: zoom + tap-to-glide; recursive exploration of ideas within ideas | DEFERRED | n/a | Ace liked tap-to-glide; step-by-step coordinate stepping rejected | Depends G-01 (containment data), V-05/V-06 |
| V-08 | Page set: Plane, Nursery, Dells, Dell Playground, Psalm Matrix — transitions preserve the current idea/context | DEFERRED | n/a | Studio exists as a local application (different, certified-local scope) | Director routing; depends V-09 |
| V-09 | Navigation placement RESEARCHED online before implementation (Ace's correction of his own top-bar instinct) | DEFERRED | n/a | No research performed yet | Research precedes any V-08 build |
| V-10 | PSALM MATRIX: the AI page — Psalms + personas + status + docking visible there; docking happens there; builds on BIMO/persona machinery, no second authority | DEFERRED | n/a | personas.py incl. Ancient_Psalms; BIMO slots descriptive, never authority (verified) | Director routing; depends SM-47 fact base |
| V-11 | AI-talk place: pure English, NOT a chat box — a new interaction concept to invent | DEFERRED | n/a | No concept exists | Invention + Director review |
| V-12 | Human-validation gates: (a) a real AI docked live AND (b) Ace personally working the Matrix — both required before any usability acceptance; bumps mapped on paper first | **BLOCKED** | n/a | Rule recorded (Ace, 2026-11-04): automated tests alone never constitute this validation | Awaits V-circuits + live dock |
| V-13 | Reserved neural research: weight-space programming / targeted enhancement of a less powerful AI (Director's item, via Ace) | DEFERRED (long-term) | n/a | No work exists or is authorized | NO IMPLEMENTATION AUTHORIZED |

## G — Standing objectives (origin: rulings and Ace directives outside both inventories)

| ID | Objective | Status | Certification | Present evidence | Next action |
|---|---|---|---|---|---|
| G-04 | Gravity wells + evolution-scalar restoration (ForceField): wells serialize but never restore; gravity/space/time/weather evolution_level resets to 1.0 | OPEN | None; Water CERTIFIED separately (PR #285) — not this item | SM-39 report's contrary claim corrected by dated addendum (2026-11-04) | Separate future circuit; Director's preferred design: restore wells as snapshots, recompute on ticks. No combined ForceField repair authorized |
| G-05 | Whole-program certification + REAL_USER_PATH claims | **BLOCKED** | WITHHELD (Director) | Bounded certifications stand exact-head only | Depends 72-03 (DAF-09) + 72-07 (A2) |
| G-06 | Symbiosis pairwise compatibility: 100×99 ordered pairs + standalone, classified with evidence; composition laws via held-out prediction test | OPEN | None | Plan approved + execution ordered (Ace, 2026-10-29); partially executed; execution state in the goal workspace | Resume as its own circuit when sequenced; retroactive — no grandfathering |
| G-07 | Full-registry D1 deep-contract circuits: all 100 Dells to a high standard | OPEN | Per-Dell certifications as issued | Standing Ace directive (2026-10-29); many Dells deepened, registry incomplete; exhibits: scope-label gap (51/53), result-cell matched-type inconsistency | Continue per-Dell circuits when sequenced |
| G-08 | SUSX100,000 sleep run (execution vehicle, not a product objective) | DEFERRED — NOT STARTED | n/a | Proposal filed (PR #288); Director suggestions requested | Starts ONLY on Ace's explicit GO; ends on "wake up"; Director suggestions fold in first |
| G-09 | DAF-09 catch-up Director report | OPEN | n/a | Owed per the 2026-10-31 reporting cadence | Uni-side writing; distinct from the 72-03 investigation |
| G-10 | Exchange Phase G (cloud perspectives) | DECLINED (deferred by adoption, Ace 2026-10-26) | n/a | Historical record; not reactivated | None |

## Register maintenance

This register is reconciled against the source set named in `NBD_OBJECTIVE_RECONCILIATION.md` §1. It is a living planning document: statuses change only on new verified evidence or a Director ruling, recorded with the same evidence discipline used to build it.

---

## SUPERSESSION — 2026-11-04 21:25 CST (Director hourly review, PR #289)

Appended per the Director's instruction; the as-of text above is NOT rewritten.

- **G-08 is now ACTIVE / OVERSEER GO RECEIVED.** Ace said "SLEEP MODE SUS 100,000 — GO" at 2026-11-04 21:20 CST. The run (SUSX100,000) is RUNNING under hidden_files/SUSX100000_DIRECTIVE.md, NBD-ordered from this register, until Ace says "wake up." The "DEFERRED — NOT STARTED" status in the G table above is superseded as of the GO.
- **This register is ACCEPTED WITH NOTED EXCEPTIONS (document inventory scope only)** — Director hourly review of PR #289, exact head 2112dd9. Not a certificate of full historical completeness (the §1 coverage limit stands; the primary-text census remains open), not runtime certification, not a merge authorization.
- Standing fences reaffirmed in the same review: TD-2 = one frozen candidate; DAF-09 unresolved; V-13 (neural) deferred; 72-64 README drift open.
