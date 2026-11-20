# PART VII PLAN — EXECUTION ORDER AND THE IN-PROGRESS SET

**Stage:** PLAN (stage 1 of plan → confirm → code → confirm, AGENTS.md §46).
**Branch:** `uni/part-7-execution-order` · **Base:** main
`af2519b6d239ef278397e277210d6da2467c36e5`.
**Governing map:** `director-reports/EIGHT_PART_EXECUTION_MAP_2026-11-20.md`
(carried into the repo on this PR, verbatim, so the Director's enhancement
pass works from the repo record). Part VII's section and its (g)
BUILD-READY PACKAGE are followed exactly; where the package scoped
something as "later" that is designable now without an authority gate,
this plan designs it now and says so (§5.2's J-16..J-25 oracles, §5.4's
walked-idea script, §3's proof scoring, §8's bundle structure).
**Authority posture:** Ace sovereign; Director + Keeper co-equal
certification/veto authorities; Uni sole code-toucher and merge actor.
**This PR contains no production code, no register JSON edits, no
campaigns, no merges.** Register flips are PROPOSED in §9 only.

---

## 1. Scope and assignments

Part VII is the order itself, the drive that runs it, and the final
proof. Its PR is the last of the eight to *close*, because certification
is definitionally last; its builds start at hour zero like every lane.

### 1.1 Register rows (verbatim titles from the register at base)

| MWL # | Title (verbatim) | IDs | Status at base |
|---|---|---|---|
| 27 | Harden Director–Uni next-best circuit handoff (= SM-07; workflow adopted; standing practice, no completion certificate) | 72-09 / SM-07 (twin claim — see the map's coverage note) | PARTIAL |
| 112 | Whole-program certification + REAL_USER_PATH claims — register BLOCKED: certification WITHHELD by the Director; depends 72-03 (DAF-09) + 72-07 (A2) | G-05 | OPEN (BLOCKED) |
| 115 | SUSX100,000 execution run — the standing completion drive itself (Ace GO 2026-11-04; run concluded in wake mode, queue continues; the register's DEFERRED label is superseded by its own 2026-11-04 supersession note) | G-08 | PARTIAL |

### 1.2 Edition 1 circuit

**GP-E27 — public journey certification / Grand Synchronization (E/B).**
Edition 1 file 02, verbatim substance: execute SYSTEM-001 J-01..J-15
plus found missing journeys against a fresh current main, at least one
real Studio/REPL path for each relevant behavior; every case carries
ordinary success, invalid refusal, restart, corruption/interruption,
owner/wall isolation, cross-perspective parity and measured performance;
report (i) component scoped certifications, (ii) independent
whole-journey certifications, (iii) all-product readiness as *different
quantities*. "A row is not CERTIFIED because its source compiles."
Edition 1 file 06 extends the journey set to **J-01..J-25** and states:
"Grand Synchronization demands J-01..J-25 where adopted scope includes
each, not 15 alone." The DAG (file 08) places GP-E27 at phase 8 with
depends_on = GP-E08, E10, E11, E12, E16, E17, E18, E19, E21, E22, E23,
E24, E26 — i.e., the rehearsal's subject matter is the built system of
Parts I + II (and IV's records), never a design-stage artifact.

### 1.3 Non-row work

- The **merge-queue record** for all eight Part PRs (§2.3).
- The **§5 sequence readiness record** (SEQ1–SEQ6 vs. actual closures, §6).
- The **sequence-divergence reconciliation** (Unified §5 vs. Edition 1
  §6/DAG), presented in full with a recommendation, flagged for Director
  confirmation (§7).

---

## 2. The landing machinery

### 2.1 Landing order — verified against dependencies

Map order (merge queue only; builds are parallel): **0 → V → III → II →
I → VI → IV → VII**. Verified pair by pair against the dependencies
named in the map's Part sections and the Edition 1 DAG:

1. **0 first.** Part 0 owns the scoring machinery every other lane's
   evidence runs through (`certification_runner.py`, `form/regress.py`,
   the INDEX dedup). If the harness changed after other Parts proved
   themselves against it, their tallies would be stale proof. Landing 0
   first freezes the instrument before the program is measured with it.
2. **V second.** Part V owns `master_list.py` and the reconciliation
   evidence (the seven-circuit backlog's identity decisions, the
   crosswalk). Part 0's own flips and every later lane's register write
   render through this tooling; the reconciliation evidence must be on
   main before lanes start flipping rows against it.
3. **III third.** The incompleteness register is records + one probe;
   landing it early puts the program's honest debt list on main before
   the big code Parts land, so Parts II/I land against a current debt
   record, not a stale one. Its conditional campaign is small and books
   early in the campaign queue (§2.5).
4. **II before I.** Part II (Dell Plan, 41 rows) owns the parse /
   translate / condition / count regions of `form/open.py` and the Dell
   contract definitions in `form/dell_matrix/core.py`; Part I owns the
   persistence / save / history / rooms / dock / growth regions and the
   state machinery those contracts execute against. Neither build
   depends on the other's *merge*, but II's contracts are the smaller,
   more definitional surface: landing them first means I's heavier
   machinery (70 rows, the heaviest campaign load) integrates against
   settled contract definitions, and any cross-region patch note flows
   II → I in the direction the map's collision plan already assumes.
5. **VI after I — with one watch item.** Part VI is decision packets +
   the Q.8 probe (2 rows, no campaign). Its *packets* are confirmed at
   the plan-confirm stage, before any code lands, so no Part I build
   waits on VI's merge. The watch item: if a VI packet's decision
   changes a premise inside an already-landed Part I item, the
   correction rides Part I's owning lane as a patch note into the next
   landing — it never reopens I's PR. With that rule stated, VI's
   position after I is safe; moving it earlier would buy nothing
   because its gates are confirm-stage, not merge-stage.
6. **IV seventh.** Part IV is design records only (19 rows, no
   campaign, no product code). Its records must be on main before
   VII's certification bundle is complete (the bundle inventories the
   Far Stratum's disposition), and nothing else depends on IV's merge.
   Seventh is the latest safe slot and keeps records churn away from
   the code Parts' landing window.
7. **VII last.** This Part's PR carries the merge-queue receipts for
   the other seven, the rehearsal receipts, and the certification
   evidence bundle. It cannot close before the things it records
   exist. Definitionally last.

**Verdict: the map's order stands — no correction.** Every genuine
cross-Part dependency (VII on I + II closures and IV records; IV builds
on VII's SEQ6 rehearsal; all lanes on 0's instrument and V's register
tooling) is satisfied by the order as given.

### 2.2 Per-PR landing protocol (§32 transaction, applied to each Part PR)

Executed by the main session only, one merge at a time, fail-closed:

1. **Freshness:** re-read the PR and both authorities' latest acts;
   any unread HOLD / CORRECTION_REQUIRED / INSUFFICIENT_EVIDENCE on
   that PR stops the merge until folded and surfaced.
2. **Exact-head evidence:** terminal CI at the exact head (every check
   named, run IDs recorded); campaign receipts at the same head for
   code Parts.
3. **Authority acts at the exact head:** Director disposition +
   Keeper CONFIRM, both scoped to the head being merged (a stamp on a
   superseded head is void — the #498 lesson).
4. **Merge-tree zero-loss witness:** compute the merge against
   then-current main; confirm no file outside the Part's declared
   territory changes, and the register diff touches only the Part's
   own rows (§2.4).
5. **Merge** (merge commit; Uni's act).
6. **Merged-main proof:** post-merge smoke on the new main; the full
   failed log is captured *before* any re-run (the #496 lesson).
7. **Receipt:** the landing receipt (§2.3) is written into this Part's
   merge-queue record with requirement, candidate + merge SHAs, Uni
   evidence, authority reviews, failures/resolutions, confirmation
   authority, limitations, and the scoreboard change.
8. **Scoreboard restatement:** after each landing, the board is
   restated from the canonical register at the new main — never from
   the landing lane's branch render.

### 2.3 Merge-queue record (this Part's non-row deliverable)

A single table, maintained in
`director-reports/GRAND_SYNCHRONIZATION_REHEARSAL_2026-11-20.md`'s
landing annex at code stage (interim updates ride this PR's comments),
one row per Part PR: Part · branch · head SHA at confirm · Director
act (ID) · Keeper act (ID) · campaign receipt · merge SHA · merged-main
smoke run ID · register rows flipped · board after landing. The record
is complete when all eight rows are filled; row 8 is this PR itself,
filled by the main session at its own landing and closed by the
Director's final check.

### 2.4 Register landing protocol (the one shared file)

Per the map's collision plan, binding on all eight lanes and restated
here as the queue's operating rule:

- Each lane edits **only its own rows** in its branch; no lane ever
  rewrites another lane's rows.
- At landing, the Part's row edits are **regenerated against
  then-current main**: surgical per-row edits to
  `director-reports/master_work_list_items.json` (indent=1,
  `ensure_ascii=False` — indent=2 reformats the whole file and is a
  known defect), then `master_list.py --out MASTER_WORK_LIST.md` and
  `--check` byte-identical before the merge executes.
- A lane whose register edit cannot be regenerated cleanly against
  current main does not merge; the discrepancy is a map defect, the
  lane stops, the split is amended, work resumes.
- This Part's own proposed flips are in §9; the JSON is not edited at
  plan stage.

### 2.5 Campaign queue (serial law)

State-sharing regression campaigns run **strictly one at a time**
globally (isolated state directories only where a suite explicitly
supports them; separate worktrees do NOT soften this). Drivers reset
SIGINT/SIGQUIT to SIG_DFL before running (background-shell inheritance
defect, 2026-11-09). Logs live under the owning goal's `hidden_files/`,
never only `/tmp`. A killed leg is NO RESULT and re-runs immediately
from the last verified state (immediate-restart law). Default queue
order, booked as clusters reach proof stage:

| Slot | Campaign | Why here |
|---|---|---|
| 1 | Part 0 ×3 (if `form/` changes) | The instrument proves itself before it scores others |
| 2 | Part III conditional legs (verify-72-17 probe) | Small; clears the debt record early |
| 3 | Part V conditional legs | Register tooling proven before lanes flip rows with it |
| 4 | Part II ×3 | Dell-plan contracts proven before I integrates against them |
| 5..k | Part I per-cluster ×3 (heaviest) | Cluster order inside the lane: persistence/save first, then rooms/dock, then growth/confirm — state-machinery before the surfaces that ride it |
| Last | **Part VII program-final ×3** | Definitionally last: runs against the fully merged post-Parts main |

Booking rule: a lane books its slot when its cluster is proof-ready,
not before; a lane's *building* never waits on the queue — only its
campaign does. No campaign starts while another runs, including
"quick" standalone probes against shared state.

---

## 3. Row #27 — Director–Uni handoff hardening: the standing-practice proof

**State of the row:** the workflow is adopted (Grand Workflow v1.0,
Cycle System, §32/§45 gates) and operating; what remains is not another
document but *proof of standing practice* — the row's own title says
"standing practice, no completion certificate." This plan designs that
proof now (it was designable without any authority gate; the package
scoped it as a "proof record" without specifying its method).

**Proof set:** the eight Part PRs themselves. Each Part's passage
through plan → confirm → code → confirm → §32 landing is one handoff
cycle of exactly the machinery row #27 exists to harden, executed under
the current rules, on the record. No synthetic exercise is needed and
none would prove as much.

**Per-handoff completeness checklist** (scored from the GitHub record,
per handoff): (1) requirement stated with authority citation;
(2) §45 package complete at presentation (exact head + main, terminal
CI with run IDs, Director disposition quoted/linked, diff scope,
underlying evidence + limitations, exact ask); (3) both authority acts
at the exact head that merged; (4) freshness re-checked in the merge
step; (5) zero-loss merge-tree witness; (6) merged-main proof with
failed logs captured before any re-run; (7) landing receipt with the
full decision trail; (8) board restated from main after landing.

**Scoring and the flip proposal:** the proof record (code-stage file:
the handoff section of `director-reports/DIRECTOR_REVIEW_QUEUE.md`,
which the package names as this Part's modify target) scores each of
the eight handoffs against the checklist and reports the count plainly
(n/8 complete trails, with every gap named, not averaged away).
**Proposed flip: #27 PARTIAL → COMPLETE when the record shows all
eight Part handoffs executed under the protocol with complete trails**
— or, if a handoff's trail has a gap, the row stays PARTIAL with the
gap named in the row at this Part's landing; the authorities confirm
the flip at CODE/RECORDS-CONFIRM like every other row. The proof
record deliberately includes the pre-program handoffs of 2026-11-19/20
(the settlement arc) as a *baseline appendix*, labeled historical —
they are evidence the machinery was already operating, not part of the
n/8 score.

## 4. Row #115 — the SUSX100,000 drive: closing terms

The drive is the standing completion run (Ace GO 2026-11-04) whose
current incarnation is the Eight-Part Program itself. **Closing terms
proposed:** the drive's execution work is complete when (a) all eight
Part PRs have landed (or been closed by an authority act with a
receipt), (b) the program-final ×3 campaign has run against the
resulting main, and (c) the certification evidence bundle (§8) has been
presented to the Director — *presented*, not granted. On those terms
**this plan proposes #115 PARTIAL → COMPLETE at this Part's landing**,
with the row's completion text naming the certification outcome
separately and truthfully, whatever it is.

**Flagged for Director confirmation at PLAN-CONFIRM:** the alternative
reading — that the drive cannot be COMPLETE while row #112's
certification is withheld, because the drive's purpose is the program
and the program is not certified — is honestly available. Uni's
recommendation is the first reading (the drive's product is execution;
certification is a distinct authority act with its own row), but the
choice is the Director's, and §9 carries the flip as PROPOSED, not
assumed. If the Director rules the second reading, #115 stays PARTIAL
at landing with the blocker named as #112, and nothing else in this
plan changes.

## 5. GP-E27 — the Grand Synchronization rehearsal, designed at full depth

### 5.1 Subject and entry conditions

The rehearsal executes against **merged main after Parts 0–VI and IV's
records have landed** (the DAG's GP-E27 dependency set, realized as
merged Parts), in a fresh clone at the exact merged-main SHA, with
isolated state directories per journey family. Entry conditions, all
verified before the first journey runs: (i) merge-queue record shows
seven landing receipts; (ii) the program-final campaign slot is booked
(the rehearsal's state-sharing legs join that queue — §2.5); (iii) the
harness suites (§5.2) exist and pass in isolated state against the
*pre-Parts* main as a labeled BASELINE run (baseline grades are
evidence about the harness, never about the product; a journey that
cannot run at baseline for a missing feature is recorded NOT BUILT at
baseline, which is a finding, not a failure of the harness).

### 5.2 The 25 journeys — harness families and per-journey oracles

Harness: new suites under `form/` as `journey_*_test.py`, one per
family. Each suite follows the harness tally contract (its own final
tally line printed LAST — `JOURNEY_<FAMILY>` — and `smoke()` true only
on full pass; sub-FULL grades are recorded in the rehearsal record,
never laundered through the tally). Every journey executes at
**PUBLIC_ENTRY_PATH minimum** (`python3 -m form.repl --owner <name>` or
the Studio/API surface where the journey is a surface journey);
REAL_USER_PATH is claimed only where the literal supported user path
is what ran, and the packet says which.

| Family suite | Journeys | Oracle source |
|---|---|---|
| `journey_chain_test.py` | J-01 Chain, J-02 Refusal | File 06 detailed |
| `journey_language_test.py` | J-03 English → LatinMandell | File 06 detailed |
| `journey_idea_lifecycle_test.py` | J-04 Create/persist Idea, J-16 Promote, J-17 Undo/redo boundary | J-04 detailed; J-16/J-17 designed §5.2.1 |
| `journey_confirm_test.py` | J-05 Human confirm, J-21 Visual Nursery at scale | J-05 detailed; J-21 designed |
| `journey_rollback_test.py` | J-06 Rollback | File 06 detailed |
| `journey_views_test.py` | J-07 Cross-view space, J-08 Tree 3D, J-13 Studio coherence, J-23 Plan-change sync | J-07/J-08/J-13 detailed; J-23 designed |
| `journey_growth_test.py` | J-09 Resonance to Nursery, J-14 Scoped growth | File 06 detailed |
| `journey_dock_test.py` | J-10 AI assist, J-22 Outage/reconnect | J-10 detailed; J-22 designed |
| `journey_hcn_test.py` | J-11 HCN orchestration | File 06 detailed (status NOT BUILT until GP-E22 lands) |
| `journey_crash_test.py` | J-12 Crash-save | File 06 detailed |
| `journey_exchange_test.py` | J-18 Cross-owner isolation, J-19 Exchange/import | Designed §5.2.1 |
| `journey_offline_test.py` | J-20 Offline session | Designed §5.2.1 |
| `journey_index_test.py` | J-15 Dell index | File 06 detailed |
| `journey_perf_test.py` | J-24 Portable/low-memory | Designed §5.2.1 (GP-E26 method) |
| `journey_canary_test.py` | J-25 Protected-value canary | Designed §5.2.1 |

For J-01..J-15 the rehearsal executes file 06's stated action, visible
outcome, and failure/recovery/consistency oracle verbatim — this plan
does not paraphrase them into weaker form; the rehearsal record quotes
the oracle beside the result.

#### 5.2.1 Oracles designed now for J-16..J-25 (file 06 names these journeys in one line each; their oracles were designable without any authority gate, so they are designed here, in file 06's pattern)

- **J-16 Nested Idea → promote:** create a nested Idea via the public
  path, promote to top-level; expected: association/lineage preserved,
  old history intact after cold reload, stable canonical ID unchanged.
  Negative: promotion by a non-owner refuses; promotion that would
  break a wall refuses with receipt.
- **J-17 Undo/redo across the save/session boundary:** create + edit
  an Idea and its detail, undo/redo within the session, save, cold
  reload, and verify the exact retained history the Q-LC.1 contract
  promises. Scope honesty: Q-LC.1's settled credit is session-local;
  the room/multi-actor remainder (register row #135's retained scope)
  is an explicitly uncovered case in the packet, not a silent pass.
- **J-18 Cross-owner / cross-room isolation + stale write:** owner B
  cannot read or mutate owner A's room content through any public
  path; a write carrying a stale generation refuses with a diagnosed
  receipt and mutates nothing.
- **J-19 Exchange/import:** export a full Idea, import it elsewhere;
  expected: content preserved whole (no silent truncation at any cut
  site), placement PENDING until confirmed, and a duplicate replay of
  the same import produces no duplicate (idempotency receipt).
- **J-20 Offline / no-AI session:** with networking disabled and no
  docked provider, run a full local session (create, grow, confirm,
  save, reload); every surface labels its source truthfully and no
  step silently requires the network.
- **J-21 Visual Nursery at scale:** seed a large proposal set (1,000
  proposals), browse with shown/total on every view, confirm and
  reject through the visual path; counts reconcile exactly with the
  store after cold reload; the docked organizer, if present, proposes
  only PENDING suggestions (confirmation remains the human's).
- **J-22 Provider outage / reconnect:** dock a provider, sever it
  mid-session, reconnect; expected: no duplicate confirmation, grant
  state consistent, in-flight suggestion either completed once or
  refused with receipt — never landed twice.
- **J-23 Plan-change sync into Muse Space:** change the plan record,
  sync; the Space shows the new state with provenance, and a stale
  mirror is labeled stale — never presented as current truth.
- **J-24 Portable / low-memory:** fresh process under a measured
  memory cap runs the standard workload (0/1/100/1000 Ideas ladder per
  GP-E26's profile method); report CPU, peak RSS, p50/p95 latency,
  disk growth. No budget is asserted from unmeasured code: baseline
  first, SLO proposed from measurement.
- **J-25 Protected-value canary:** exactly one outer protected-value
  canary is passed through receipts, API, history, tests, and logs;
  the packet proves by search receipts that the canary appears only
  where the design authorizes and nowhere else.

### 5.3 Evidence packet (per journey, file 06's contract verbatim)

Fields: `journey_id, feature_scope, source_main_sha, PR/head if
applicable, public_action, owner, input_fixture_digest, raw command/log
(redacted where needed), expected_state_diff, observed_state_diff,
refusal_class, persistence_generation, cold_restart, consumer_views,
test_suite, CI run, checker, Director disposition, completion_status,
uncovered_cases, timestamp`. Packets are stored as the rehearsal
record's annexes in this PR at code stage; stable paths, immutable
references, no private tokens. **Grades** (file 06): NOT_RUN,
PARTIAL_SCOPE, FULL_SCOPE_PASS, FAIL, BLOCKED_BY_AUTHORITY,
UNSUPPORTED_BY_DESIGN. FULL_SCOPE_PASS only when every mandatory step
has executable public-path proof at the same relevant head.

### 5.4 The walked idea (Unified SEQ6 checklist item iii), scripted now

One idea, created fresh in the rehearsal, walked the full §5 journey
with a receipt at every arrow: **BORN** (created via the English door,
receipt: canonical ID + seed) → **CONFIRMED** (human-path confirmation
from PENDING, receipt: confirmer + wall inheritance) → **PLACED**
(placement into its room/box per the placement law, receipt: position
+ membership) → **READ** (retrieved through SEE with shown/total,
receipt: rendered record equals stored record) → **MOVED** (moved
within the space, receipt: position diff, identity unchanged) →
**RELATED** (a typed relation drawn to a second idea, receipt: graph
edge in canonical state, visible identically in 2D/text views) →
**LEARNED ABOUT** (an outcome recorded against it through the DuoBeta
observation path — observation only, receipt: outcome record;
learning claimed only if the authorized lifecycle runs, otherwise the
receipt says OBSERVED, NOT LEARNED) → **REMEMBERED** (cold restart;
the idea, its relations, and its history reload byte-faithful,
receipt: generation + diff-empty proof) → **WITNESSED** (the idea
rendered from the Psalm Matrix surface, receipt: surface capture
matching canonical state) → **MEASURED** (the footprint receipt
(C-1.6) attached for the walk, receipt: retained/omitted counts
disclosed). Any arrow that cannot execute stops the walk at that
arrow with the grade recorded; the walk is never narrated past a
failed arrow.

### 5.5 SEQ6 checklist (i)–(v) — evidence mapping

| SEQ6 item (Unified C-SEQ6, operative checklist) | Rehearsal evidence |
|---|---|
| (i) §4 register closed per its condition — every OPERATIVE G-01..G-28 COMPLETE, OWNED-AND-CLOSED, or RETIRED WITH A RECEIPT (G-29/G-30 quarantined in §7, outside the condition per SD-GP-01) | Part III's register state at rehearsal head, rendered and cited per item; any item not meeting the condition is listed as an open condition, not smoothed over |
| (ii) §3 web's MECHANISM-grade connections demonstrated live | The C-WEB cluster demonstrations (A–K) executed or graded per cluster; PROJECTION-grade connections are reported as projections, never as mechanism proof |
| (iii) One idea walked the full §5 journey | §5.4's ten-arrow receipt chain |
| (iv) Witnessed from the Psalm Matrix | The WITNESSED arrow + the rehearsal observed from the Matrix surface (SEQ4's surface, Part I's build) |
| (v) Footprint receipt attached | C-1.6 receipt for the rehearsal run itself |

### 5.6 The three quantities (never blended)

The rehearsal record reports, separately: **(i) component scoped
certifications** — per-circuit authority dispositions as they stand;
**(ii) independent whole-journey certifications** — the 25 journey
grades from §5.3; **(iii) all-product readiness** — the §7-condition
assessment in §8. A green (i) does not imply (ii); a green (ii) does
not grant (iii). Readiness is the Director's act (§8), not a sum.

### 5.7 Execution protocol and failure law

Fresh clone at the exact merged-main SHA; isolated state per family;
drivers reset SIGINT/SIGQUIT; full logs captured before any re-run;
a failed journey gets a diagnosis and a disposition — never a hopeful
re-run (two-no-result law: a second identical failure stops the leg
for mechanism investigation). The rehearsal's final leg is the
program-final ×3 campaign (§2.5). If a journey's subject feature was
not built by its owning Part, the grade is NOT BUILT /
UNSUPPORTED_BY_DESIGN as applicable — the rehearsal reports the
program as it is.

---

## 6. The §5 sequence readiness record — design

Code-stage section of the rehearsal record; one row per Unified step,
each mapped to its Edition 1 counterpart, its owning Part(s), the
closure evidence, and a status that is filled from evidence at
rehearsal time (all rows read NOT YET ASSESSED at plan stage):

| Unified §5 step | Edition 1 counterpart | Owning Part(s) | Closure evidence required |
|---|---|---|---|
| SEQ1 Dell Plan gate | P1 Dell Plan (+ P0 Integrity beneath it) | II (gate), 0 (integrity) | Dell audit closed (GP-E07); count discrepancy (99 vs 100) settled as evidence by Part II |
| SEQ1.5 Census X11 | P1.5 Runtime X11 | I / III | Census on current main, row-level, with the second-seat pass |
| SEQ2 HCN build (frozen R3) | P5 HCN R3 | I (GP-E22) | Frozen-R3 contract reproduced, then orchestration receipts (J-11) |
| SEQ3 The Dock live | P6 Dock/Psalm (first half) | I (GP-E23) | 12-dock inventory live, receipt/permission real, offline graceful (J-10) |
| SEQ4 Psalm Matrix surface | P6 Dock/Psalm (second half) | I | Docked AI on real ground, human-gated suggestions only (J-10, J-22) |
| SEQ5 Windowed Workspace | P7 Surfaces | I (GP-E24/E25/E26) | Studio/Console/Space coherence (J-13, J-23), measured performance (J-24) |
| SEQ6 Grand Synchronization | P8 Grand Synchronization | VII (GP-E27) | §5 of this plan, executed |
| §7 Far Stratum (step 7) | P9 Far Stratum | IV (designs), future turns (builds) | Opens only after SEQ6 closes; each Far build certifies in its own turn (GP-E28) |

## 7. Sequence divergence — Unified §5 vs. Edition 1, reconciled

**The two orders, in full.** *Unified §5* (eight steps): Dell Plan
gate → Census X11 (1.5) → HCN → Dock → Psalm Matrix → Windowed
Workspace → Grand Synchronization → §7 Far Stratum. *Edition 1 §6*
(eleven phases, with the file-08 DAG as its machine form): P0
Integrity → P1 Dell Plan → P1.5 Runtime X11 → P2 Language and state →
P3 Spatial/Tree → P4 Resonance/Nursery → P5 HCN R3 → P6 Dock/Psalm →
P7 Surfaces → P8 Grand Synchronization → P9 Far Stratum. Edition 1 §6
states its own concurrency rule: "Sequence is a dependency DAG, not a
requirement to leave all unrelated lanes idle."

**The concrete divergences:**

- **D1 — HCN's position.** Unified: step 2, immediately after the
  census, before the Dock. Edition 1: P5 — after Language/state (P2),
  Spatial/Tree (P3), and Resonance/Nursery (P4); the DAG puts GP-E22
  (HCN) at phase 5 with depends_on = GP-E07, E13, E14, E15. These are
  genuinely different claims about what HCN needs beneath it.
- **D2 — Simulate (GP-E14).** Edition 1's DAG stages it at phase 1
  (depends_on = GP-E13 only) — early. Unified §5 has **no Simulate
  step at all**: Simulate exists in the Unified Edition only as a
  house cluster (C13, Part I's territory), never as a sequence step.
- **D3 — Dock/Psalm granularity.** Unified: two steps (SEQ3 Dock,
  SEQ4 Psalm Matrix). Edition 1: one phase (P6 Dock/Psalm), with the
  DAG separating them anyway (GP-E23 phase 6, depends_on = GP-E20 +
  GP-E22).
- **D4 — Phases with no Unified step.** Edition 1's P0 Integrity, P2
  Language and state, P3 Spatial/Tree, and P4 Resonance/Nursery have
  no SEQ counterparts; the Unified Edition distributes that work
  inside its steps and houses rather than sequencing it. Conversely
  the Unified census (SEQ1.5) and Edition 1's P1.5 agree in substance.

**Recommendation (for Director confirmation at PLAN-CONFIRM):** adopt
**Edition 1's DAG as the dependency truth** for build readiness — it
is the finer-grained, machine-checked artifact, and its own text
already dissolves the sequencing conflict ("a dependency DAG, not a
requirement to leave unrelated lanes idle") — and adopt the **Unified
§5 order as the demonstration order** for the readiness record (§6)
and the rehearsal's public narrative, since §5 is Ace's unified
presentation of the program and SEQ6's checklist is written against
it. Under the parallel-lane model neither order sequences the builds;
what the reconciliation fixes is which document a readiness claim
cites. On D1 specifically: HCN's *build* follows the DAG (its
dependencies are real: GP-E14/E15 contracts beneath it), while the
readiness record reports HCN at its SEQ2 row with the DAG phase noted
— the divergence is recorded, not hidden. **This recommendation is a
plan-stage proposal; the Director confirms or corrects it. Uni does
not treat it as settled until he does.**

## 8. Row #112 — the certification path (the Director is the blocker; planned around, never around him)

**Register truth, stated plainly:** certification is **WITHHELD by
the Director**; the row depends on 72-03 (DAF-09) + 72-07 (A2). DAF-09
remains UNRESOLVED — a session-escape discrepancy that §31 law
forbids resolving on local evidence; it closes, if it closes, by the
Director's independent reproduction. Nothing in this plan works
around that: no scoped self-certification, no certification inferred
from merges, green campaigns, or journey grades, no rewording of the
row to make the block disappear.

**What this Part builds:** the complete evidence bundle the Director
would certify *on*, so that his act — whenever and however he rules —
is a decision on evidence, not on summaries. Code-stage file:
`director-reports/CERTIFICATION_EVIDENCE_BUNDLE_2026-11-20.md`,
structured against Edition 1 §7's completion conditions:

| §7 condition | Bundle section (evidence source) |
|---|---|
| (a) All adopted user-visible contracts have independently checked implementation and recovery | Per-contract dispositions: Part II's Dell audit + Part I's circuit records, each with its checker named |
| (b) All live user journeys performable without hidden steps or phantom outcomes | §5's 25 journey grades + walked-idea receipt chain |
| (c) No confirmed silent-loss / false-success / open authority bypass remains | Part III's incompleteness register state + Part 0's gate results; every residual named, none averaged away |
| (d) Observed performance and offline behavior meet measured budgets | J-20 + J-24 packets (measured; budgets as measured, SLO proposals labeled as proposals) |
| (e) Canonical registers and read models agree | Part V's reconciliation + the post-landing register render at the bundle's main SHA, `--check` byte-identical |
| (f) Every out-of-scope future feature and sovereign decision explicitly named | Part IV's Far Stratum dispositions + Part VI's decision packets + the open-question inventory, each with its owner |
| (g) Merged-main final check performed; MWL regenerated under authority | §2.3's merge-queue record (eight receipts) + the final campaign receipt |

**The path, step by step:** (1) Parts 0–VI + IV land (§2.1 order);
(2) the rehearsal executes (§5) and the program-final campaign runs;
(3) Uni assembles the bundle at the resulting exact main SHA and
presents it with a §45 package whose ask is the certification
decision itself; (4) the Keeper independently checks the bundle's
evidence (his role on every prior gate); (5) **the Director rules** —
certify, certify in scope, or withhold with reasons. Only step (5)
flips row #112, and only in the form his ruling takes. If he
withholds, the bundle and the row both record it, the program's other
rows stand as they are, and the bundle remains the standing evidence
base for any later ruling. **Part VII's success criteria do not
include certification being granted** — they include the bundle being
complete, honest, and presented.

**REAL_USER_PATH claims discipline:** any claim in the bundle labeled
REAL_USER_PATH is backed by a literal supported-user-path execution
in a journey packet; anything proven at a lower tier is labeled at
its true tier (the evidence ladder is never upgraded for
presentation).

## 9. Proposed register changes (PROPOSED ONLY — the JSON is not edited in this PR)

At this Part's landing, regenerated per §2.4, and only as the
evidence and the authorities' acts allow:

- **#27:** PARTIAL → COMPLETE, title annotation appended: standing-
  practice proof = the eight Part handoffs scored n/8 in the
  DIRECTOR_REVIEW_QUEUE record (flip only at n/8 with complete
  trails; otherwise the row stays PARTIAL with gaps named).
- **#115:** PARTIAL → COMPLETE on the §4 closing terms (all Parts
  landed/closed-by-act + final campaign run + bundle presented),
  certification outcome named separately in the title annotation —
  **subject to the Director's PLAN-CONFIRM ruling on the §4 reading.**
- **#112:** NO flip proposed. The row changes only by the Director's
  certification act, in his words, at his time.

## 10. Code-stage file manifest (per the (g) package; nothing here is created at plan stage except this plan)

- CREATE `director-reports/GRAND_SYNCHRONIZATION_REHEARSAL_2026-11-20.md`
  (rehearsal record + §6 readiness record + §2.3 landing annex).
- CREATE `director-reports/CERTIFICATION_EVIDENCE_BUNDLE_2026-11-20.md` (§8).
- CREATE the 15 `form/journey_*_test.py` harness suites (§5.2).
- MODIFY `director-reports/DIRECTOR_REVIEW_QUEUE.md` (row #27's
  standing-practice proof record, §3).
- MODIFY `director-reports/master_work_list_items.json` — own rows
  only (§9), at landing, per §2.4.
- CARRIED ON THIS PR (plan stage): this plan +
  `director-reports/EIGHT_PART_EXECUTION_MAP_2026-11-20.md` (the
  governing map, verbatim, for the Director's enhancement pass).

## 11. Dependencies, gates, limitations

- **NEEDS_DIRECTOR:** (1) PLAN-CONFIRM of this plan, including the §7
  reconciliation recommendation and the §4 row-#115 reading;
  (2) CODE/RECORDS-CONFIRM at exact head at code stage; (3) the
  row #112 certification decision (§8) — requested only when the
  bundle's prerequisites exist. The Director is also final-check
  authority for GP-E27.
- **NEEDS_KEEPER:** PLAN-CONFIRM (this stage); independent check of
  the rehearsal evidence and the certification bundle (code stage).
- **NEEDS_OVERSEER:** none for the builds. Ace receives the
  certification outcome; Sitting #002 (Mon 2026-11-23, ≥42/≥39)
  remains the weekly truth instrument and is unaffected by this Part.
- **Genuine dependencies:** rehearsal *executions* on merged Parts I +
  II; the bundle on Part IV's records landing; Part IV's future Far
  *builds* on this Part's SEQ6 rehearsal closing (the program's one
  true cross-Part build dependency).
- **Limitations, stated:** this plan certifies nothing; journey
  oracles for J-16..J-25 are Uni designs in file 06's pattern, open
  to Director correction at PLAN-CONFIRM; DAF-09's state at bundle
  time will be whatever the Director's own reproduction has
  established — if it is still unresolved, the bundle says so and
  condition (c)'s section carries it as a named residual.

## 12. The ask

Director + Keeper **PLAN-CONFIRM** for Part VII as presented here —
including the §7 reconciliation recommendation and the §4 closing-terms
reading — in the one-bundle presentation of the eight Part plans. On
PLAN-CONFIRM, this lane proceeds to the code stage exactly as
specified; row #112 is not asked about, certified, or worked around
at any stage of this Part.
