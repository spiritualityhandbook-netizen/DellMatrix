# EIGHT-PART EXECUTION MAP — DellMatrix Grand Plan, consolidated

**Date:** 2026-11-20. **Authority:** Ace ruling, AGENTS.md §46 (restated with
finality 2026-11-20 08:44 CST): the entire detailed plan first, then execution
as **8 PRs — one PR per Grand Plan Part**. No new small standalone PRs; every
remaining object lives in exactly one Part PR below.

**Planning artifact only.** This map assigns and sequences work. It builds
nothing, merges nothing, and grants no credit.

## Sources (all read for this map)

- Canonical register: `director-reports/master_work_list_items.json` at main
  `af2519b6d239ef278397e277210d6da2467c36e5` — 185 rows: **COMPLETE 40 /
  OPEN 84 / PARTIAL 55 / GATED 3 / SANDBOXED 3**. The 40 COMPLETE rows are
  closed and appear nowhere below; the other **145 rows each appear in
  exactly one Part** (coverage proof at the end, machine-checked).
- Grand Plan Edition 1 (Director, merged via PR #486):
  `director-reports/GRAND_PLAN_DIRECTOR_EDITION1_2026-11-18/` — 28 execution
  circuits GP-E01..GP-E28 (`02_EXECUTION_CIRCUITS.md`), 100 Dell baseline
  (`05`), 25 journey acceptances (`06`), decision/unknown register (`03`).
  Each circuit is assigned to exactly one Part below.
- THE GRAND PLAN — UNIFIED TOTAL EDITION (PR #421 head `9e930561`, not yet on
  main): the Part structure 0–VII and each Part's contents.
- Batch Sweep manifest, 2026-11-17 (`hidden_files/sweep/`).
- Live open items as of 2026-11-20: PR #498 (R5), PR #308, PR #294, the
  seven-circuit credit backlog, and the R-family queue.

## Assignment rules (how every row got its Part)

1. Scoreboard / gate / reporting machinery → **Part 0**.
2. Architecture-level machinery (persistence, state, identity, lifecycle,
   learning persistence, host & surface machinery, dock / bridge / simulate /
   rooms / resonance engines, performance, coupling) → **Part I**.
3. Dell & language contracts (per-Dell behavior, English door, control
   contracts, the C4/C5/C7/C9/C10/C11 family slices, D1 deepening,
   symbiosis) → **Part II**.
4. Defect-register & framework entries → **Part III**.
5. Vision, deferred, parked, and sandboxed items → **Part IV**.
6. Cross-register reconciliation work → **Part V**.
7. Rows that *are* open decisions → **Part VI**.
8. Execution-order & final-certification work → **Part VII**.

Judgment-call placements are flagged where they occur and listed again in
the coverage proof. Cross-references never duplicate an assignment: a row's
single home Part is where its register write rides.

## The eight Parts at a glance

| Part | Name | Register rows | Edition 1 circuits | Character |
|---|---|---|---|---|
| 0 | Scoreboard | 3 | GP-E25 | Gate/resume/report machinery |
| I | Architecture | 70 | GP-E05, E13–E19, E21–E24, E26 | The eleven houses' engines |
| II | Dell Plan | 41 | GP-E01–E04, E07–E12, E20 | The 99/100 Dell contracts |
| III | Incompleteness Register | 4 | GP-E06 (+ GP-G01..28 dispositions) | The defect register itself |
| IV | Far Stratum | 19 | GP-E28 | Vision / deferred / parked |
| V | Scoreboard Reconciliation | 3 | — (crosswalk work) | Keeping the two universes honest |
| VI | Unknowns | 2 | — (question families) | Decisions owed by authorities |
| VII | Execution Order | 3 | GP-E27 | The drive + final certification |
| **Total** | | **145** | **28** | |

## Execution model — ALL EIGHT PARTS IN PARALLEL (Ace ruling, 2026-11-20 08:49 CST; AGENTS.md §46.6)

The Parts are **not** built one at a time. All eight lanes start at hour
zero and build simultaneously. Serial exists only where a safety law names
it: **merges** (§32, main-session, one at a time), **state-sharing
regression campaigns** (one at a time, or isolated state directories), and
**shared mutable state** (the register JSON — see the collision plan).
Everything else — planning, building, focused tests in isolated state —
runs at once. Each Part's section therefore marks: what is
**parallel-from-hour-zero**, what **genuinely depends** on another Part
(named), what is **serial-by-law**, and the **collision-avoidance split**
where two lanes would touch the same files. The landing (merge) order at
the end is a merge-queue order only — it does not sequence the builds.

**Register-write collision plan (the one shared file):** every Part PR
flips rows in `director-reports/master_work_list_items.json`. Eight lanes
editing one JSON guarantees conflicts, so: each lane edits **only its own
rows** in its branch; the register JSON is regenerated per Part PR at
landing time against the then-current main (surgical per-row edits,
indent=1, `ensure_ascii=False`, re-render + `--check` byte-identical);
merge order resolves the rest. No lane ever rewrites another lane's rows.

**`form/open.py` collision plan:** Parts I and II both work in the Program
core. The split is by *function region*, named per Part in its package:
Part I owns persistence/save/history/rooms/dock regions; Part II owns
parse/translate/condition/count regions. A lane that needs a region owned
by the other lane files its change as a *patch note in its own Part PR*
for the owning lane to apply at integration — never a direct edit.

---
# PART 0 — THE SCOREBOARD

## (a) Scope in plain terms

The machinery that produces the number everyone argues about: how merges are
gated and reconciled, how interrupted work resumes from a last-good
checkpoint, how the living plan renders, and one owed report. This Part
builds no product capability — it makes every later Part's progress
countable and recoverable.

## (b) Register rows assigned

| MWL # | Short title | IDs | Status |
|---|---|---|---|
| 91 | Strengthen exact-head / merge-tree / post-merge / fresh-clone gate reconciliation | SM-07 | OPEN |
| 92 | Make workflow resumable: last-good checkpoint + completed-circuit records | SM-08 | OPEN |
| 116 | DAF-09 catch-up Director report | G-09 | OPEN |

**Edition 1 circuit assigned:** GP-E25 — Living Grand Plan Blueprint / Muse
Space (design authored in Edition 1 file `04_MUSE_SPACE_DESIGN.md`; build
after check). **Non-row fold-in:** the INDEX dedup (exactly one true
collision — duplicate DD31 rows in `director-reports/INDEX.md`, strike the
stale row) lands as records work in this Part's PR.

## (c) Already done vs. what the Part PR must build

- **Done:** the register-write-inside-the-closing-package pattern is proven —
  PR #500 (merged `af2519b6`) wrote MWL #14 → COMPLETE and MWL #135 →
  scoped PARTIAL inside its own settlement PR, and the board moved 39 → 40
  with no separate settlement lag. The live scoreboard rule (canonical
  register + `master_list.py` at a pinned SHA) is in force.
- **Build:** SM-07's unified gate reconciliation (exact-head + merge-tree +
  post-merge + fresh-clone as one reconciled gate, not four separate
  rituals); SM-08's durable resumability (last-good checkpoint +
  completed-circuit records — the completion envelope made persistent);
  G-09's DAF-09 catch-up Director report (Uni-side writing; its evidence
  depends on Part III row #21); GP-E25's living blueprint surface on top of
  Part V's reconciled data.

## (d) Part PR contents — checklist

- [ ] Gate-reconciliation implementation + tests (SM-07 contract)
- [ ] Resumability checkpoint records + recovery test (SM-08)
- [ ] DAF-09 catch-up report filed (G-09) — text only, no DAF-09 verdict
- [ ] GP-E25 living blueprint / Muse Space build per Edition 1 file 04
- [ ] INDEX dedup (one stale DD31 row struck, byte-verified)
- [ ] Full regression campaign ×3 (serial, main-session) + exact-head CI
- [ ] Register write riding inside: rows #91, #92, #116 status updates
- [ ] §45 evidence package; Director + Keeper confirmations

## (e) Dependencies

- Row #116's report depends on Part III row #21 (DAF-09 evidence state).
- GP-E25 renders Part V's reconciled data — Part V may land after Part 0,
  but E25's *data contract* must be designed against Part V's crosswalk.
- No Ace or Director decision is outstanding for this Part.

---

## (f) Parallel / serial split

- **Parallel from hour zero:** everything in this Part. Gate tooling,
  resumability records, the DAF-09 report text, INDEX dedup, and the
  GP-E25 design/build touch no other lane's files.
- **Genuine dependencies:** none blocking the build. Row #116's report
  *quotes* Part III row #21's evidence state — if Part III's evidence
  moves, the report text updates at integration, not before.
- **Serial by law only:** this Part's merge (one §32 act) and its
  regression campaign slot in the global campaign queue.
- **Collisions:** `form/regress.py` — Part 0 owns all changes to the
  campaign harness itself; other lanes only *run* it. Register JSON —
  own rows only (see header collision plan).

## (g) BUILD-READY PACKAGE — Part 0

- **Branch:** `uni/part-0-scoreboard`
- **Files to create:** `director-reports/GATE_RECONCILIATION_RECORD_2026-11-20.md`;
  `form/gate_reconciliation_test.py`; Muse Space build records under
  `director-reports/` per Edition 1 file 04.
- **Files to modify:** `director-reports/certification_runner.py`;
  `director-reports/master_list.py` (only if the gate contract requires);
  `form/regress.py` (harness changes, Part 0 only); `director-reports/INDEX.md`
  (dedup — one stale DD31 row).
- **Test suites:** new `form/gate_reconciliation_test.py`; existing
  `form/test_isolation_hygiene_test.py`, `form/regress_capture_test.py`;
  register render check (`master_list.py --check`) byte-identical.
- **Campaign:** full ×3 via `python3 -m form.regress` if any `form/*.py`
  changes; records-only remainder rides exact-head CI.
- **Register flips (target, on confirm):** #91 OPEN → COMPLETE;
  #92 OPEN → COMPLETE; #116 OPEN → COMPLETE.
- **Authority asks:** (1) PLAN-CONFIRM — Director + Keeper on this Part's
  package as published; (2) CODE-CONFIRM — scoped, at the Part PR's exact
  head, after terminal CI + campaign receipts.

---
# PART I — ARCHITECTURE: DOCTRINE, HOUSES, SYNCHRONICITY WEB, SEQUENCE, PLACEMENTS

## (a) Scope in plain terms

The engines underneath the Dells: the Efficiency Doctrine (§1), the Eleven
Houses (§2), the Synchronicity Web (§3), the Grand System Sequence builds
(§5), and the head placements. In register terms this is where persistence,
saving, identity, lifecycle, learning, the Dock, Bridge, Exchange, Simulate,
rooms and boxes, the resonance engine, Studio's machinery, performance, and
module coupling all live. It is the largest Part — 70 rows — because most of
the register's PARTIAL rows are bounded repairs to this machinery whose
retained remainders close here.

## (b) Register rows assigned

| MWL # | Short title | IDs | Status |
|---|---|---|---|
| 25 | Dispose remaining per-scope admission/registry certification requests | 72-07 / SM-04 | PARTIAL |
| 34 | Reconcile legacy flow executor with canonical chain ownership | 72-16 / SM-15 / DD-08 | GATED |
| 44 | Stress per-member ManifestSet + typed chainlink transport | 72-26 / SM-21 | PARTIAL |
| 46 | Audit Program/Nursery pair-atomic save + fresh-process load | 72-28 / SM-35 / DD-06 | GATED |
| 47 | Stress checkpoint sealing, rollback, directory-sync failure | 72-29 / SM-36 / DD-04 | PARTIAL |
| 48 | Challenge Exchange journaled import/recovery + receipt disposal | 72-30 / SM-33 / SM-34 / G-03 | PARTIAL |
| 49 | Check Nursery optimistic concurrency + duplicate confirmation | 72-31 / SM-31 / DD-09 | PARTIAL |
| 50 | Validate semantic-graph journals against derived Program effects | 72-32 / SM-25 / DD-05 | PARTIAL |
| 51 | Verify supersession crash + acceptance lineage across restart | 72-33 / SM-30 | PARTIAL |
| 52 | Test owner namespace collision + foreign-state rejection | 72-34 / DD-12 | PARTIAL |
| 53 | Recheck atomic-write orphan-temp + rollback cleanup bounds | 72-35 | PARTIAL |
| 54 | Roundtrip persistent envelopes under corrupt/unknown versions | 72-36 / DD-10 | PARTIAL |
| 55 | Plan + verify the Plane-to-Idea bridge / Track D | 72-37 / SM-27 / SM-28 | PARTIAL |
| 56 | Reconcile Idea + semantic-graph node identity through lifecycle | 72-38 / SM-26 | PARTIAL |
| 57 | Prove nested Idea parent/child + promotion invariants | 72-39 / G-01 / SM-26 / SM-28 | PARTIAL |
| 58 | Enforce active/faded/superseded participation across all consumers | 72-40 / SM-29 / DD-13 | PARTIAL |
| 60 | Stress knowledge selection, scope, lineage, dependencies | 72-42 / SM-37 | PARTIAL |
| 61 | Trace cause/depend/provenance explanations to real graph evidence | 72-43 / SM-38 / SM-64 (theme) | PARTIAL |
| 62 | Test resonance/harmony-to-Nursery proposals at the human gate | 72-44 | PARTIAL |
| 63 | Preserve epistemic source/status through views + spatial consumers | 72-45 | PARTIAL |
| 65 | Stress stale field-snapshot + agent reconnect boundaries | 72-47 | PARTIAL |
| 66 | Exercise agent host-bound idempotency, retries, conflicting envelopes | 72-48 / SM-45 | PARTIAL |
| 67 | Challenge AcceptancePolicy delegation, expiry, revocation chains | 72-49 / SM-32 | PARTIAL |
| 68 | Prove DirectorSession remains recommendations-only | 72-50 / SM-46 | PARTIAL |
| 69 | Reconcile DuoBeta outcome evidence + learning ledger persistence | 72-51 / SM-41 | PARTIAL |
| 70 | Test learned-score saturation + opt-out reversibility | 72-52 / SM-42 | PARTIAL |
| 71 | Harden provider errors, prompt/output validation, protected values | 72-53 / SM-43 | PARTIAL |
| 72 | Keep selfgrow auxiliary ledger isolated from canonical state | 72-54 | PARTIAL |
| 76 | Regression-test Studio Host/Origin/token + malformed HTTP | 72-58 / SM-51 | PARTIAL |
| 77 | Test Studio state refresh, stale owner state, receipt reconstruction | 72-59 | PARTIAL |
| 79 | Improve Studio keyboard, focus, constrained viewport behavior | 72-61 / SM-56 | PARTIAL |
| 81 | Stress 2D spatial placement, rendering, restore invariants | 72-63 / SM-40 | PARTIAL |
| 83 | Protect Form as source of truth vs frozen JS/preform drift | 72-65 / SM-63 | PARTIAL |
| 84 | Deepen changed-file lint + Python-version compatibility checks | 72-66 / SM-61 | PARTIAL |
| 87 | Create repeatable low-memory + large-state performance baselines | 72-69 / SM-59 / SM-60 | PARTIAL |
| 88 | Incrementally reduce oversized live-module coupling, no behavior change | 72-70 | OPEN |
| 89 | End-to-end protected-value canaries across outward evidence surfaces | 72-71 / SM-20 | PARTIAL |
| 97 | Confirm BIMO/persona views remain advisory; cannot bypass host-bound authority | SM-47 | OPEN |
| 98 | Improve traceability from runtime behavior to receipts, outcomes, persisted evidence | SM-64 | OPEN |
| 118 | Q1 family implementation — journaled Exchange import/recovery transactions | DD-07 / PR #294 / Q1 | GATED |
| 121 | C2 bounded candidate: graded-input-to-verdict invariant test on one real canonical path | C2.Candidate (Director R1, §14.9) | OPEN |
| 122 | C2 relatedness model — resonance exposes with-whom / how-strong / why over agreed fixtures | C2.Relatedness | OPEN |
| 123 | C2 development-coupled growth — growth responds to agreed development evidence; attention the sma… | C2.Growth | OPEN |
| 124 | C2 targeted Pulse — Pulse obeys selected targets and exclusions | C2.TargetedPulse | OPEN |
| 125 | C2 decline-coupled Decay | C2.Decay | OPEN |
| 126 | C2 fusion — Merge carries parent substance and provenance while preserving parents | DD-15 / C2.Fusion | OPEN |
| 127 | C2 partition — Split keeps each resonating cluster intact; zero/one cluster and ties handled hone… | DD-16 / C2.Partition | OPEN |
| 128 | C2 enhancement outcome — Enhance redefined per Ace's ruling | DD-23 / C2.EnhancementOutcome | OPEN |
| 129 | C2 temperature design — Temp as a typed intensity control per consumer, not a secret global switch | DD-19 / C2.TemperatureDesign | OPEN |
| 131 | Mirror gains the true compare — pair comparison through the C3 comparator, honest pagination | C3.MirrorCompare | OPEN |
| 132 | Trace covers the entire current process — full retrieval beyond 512 entries without silent loss; … | DD-52 / C3.Trace | OPEN |
| 133 | Failure doors — Analyze / Revert / Retry per Ace's failure doctrine: Retry targets an identified … | DD-32 / C3.FailureDoors | OPEN |
| 134 | Rooms are Ace's to close — chosen-room operations cannot overwrite another room's later work; ses… | DD-53 / C3.Rooms | OPEN |
| 135 | Undo and redo like a real program — 30-step adjustable window, new-write tail invalidation, histo… | DD-54 / C3.Undo | PARTIAL |
| 136 | Alpha / history member + close ceremony — old generations freeze/confirm/restore under new code; … | C3.Alpha | OPEN |
| 144 | Boxes — standing/named sandboxes: owner put/take, multiple boxes, the standing private box, all a… | DD-17 / C6.Boxes | OPEN |
| 145 | Freeze — room/item pause: paused items stay visible, retain contents/position, stop aging/growth/… | DD-22 / C6.Freeze | OPEN |
| 146 | Scope/Group integration — the 53<->82 partnership as one pair; a named Group is never automatical… | C6.ScopeGroup | OPEN |
| 147 | Placement — idea/body/both, AUTO/BIND: replacement retains intended position; child placement res… | C6.Placement / DD-50 (grounding note) | OPEN |
| 154 | Resident Psalm — visible start/stop, bounded work, proposal-only output; presence grants no autho… | C8.Resident | OPEN |
| 155 | Multi-Psalm / BIMO execution design — persona execution needs actual instance semantics and Ace-a… | C8.MultiPsalm | OPEN |
| 164 | Bridge ledger — the ledger of all bridges: reports dock/Exchange facts without taking over their … | DD-34 / C12.Ledger | OPEN |
| 165 | Exchange front door — local Exchange export/import door: preview binds to payload, imports stay P… | C12.ExchangeDoor | OPEN |
| 166 | Room-to-room bridge — preview/transfer between rooms, only after C3 room semantics are settled; n… | C12.RoomBridge | OPEN |
| 167 | Simulate: explicit effect inventory — the declared inventory of effects a simulation must account… | C13.Inventory | OPEN |
| 168 | Simulate: isolated executor adapter — the actual supported command executes against an isolated c… | DD-21 / C13.Executor | OPEN |
| 169 | Simulate: supported dry-run — a bounded supported subset FIRST; per-atom outcomes and scoped diff… | C13.DryRun | OPEN |
| 170 | Simulate: parallel preview — per-arm preview shows each arm and its conflicts, never one blended … | C13.ParallelPreview | OPEN |
| 173 | Coordinated history retention/compaction contract — bounded navigable undo vs durable evidence; r… | C3 design prerequisite (§14.7/§14.8) | OPEN |
| 185 | Sandbox dock-landing + confirm-placement wall blindness — CONFIRMED sandbox-boundary defect famil… | U-PROBE / PR #410 / GS-4 residual | OPEN |

**Row clusters (for navigation):** H7 Memory / persistence — #46, #47, #53,
#54, #173; H8 Doors / admission / host boundaries — #25, #52, #65, #66,
#118; save & journal transactions — #48, #49, #50, #51; Field / placement /
Idea machinery — #55, #56, #57, #144–#147; Gate & Growth — #58, #60, #62,
#67, #185; semantic graph & views — #61, #63; learning persistence — #69,
#70, #72; Studio & surfaces machinery — #76, #77, #79, #81; instruments —
#83, #84, #87, #89, #98; spine / flow / coupling — #34, #44, #88; persona &
Dock — #97, #154, #155; C2 Resonance Core — #121–#129; C3 Failure & Time —
#131–#136; C12 Bridge — #164–#166; C13 Simulate — #167–#170.

**Edition 1 circuits assigned (13):** GP-E05 (R5 history loss + R27
presentation boundaries), GP-E13 (semantic/Plane identity & state
ownership), GP-E14 (one bounded Simulate mechanism), GP-E15 (save/recovery
& atomic cross-owner writes), GP-E16 (rooms, boxes, user undo, staged
edits), GP-E17 (Exchange/Bridge/referential integrity), GP-E18 (geometry
admission & Tree L1–L5), GP-E19 (resonance/harmony candidate engine),
GP-E21 (DuoBeta learning & rollback), GP-E22 (HCN R3 builder interface),
GP-E23 (Dock & Psalm Matrix), GP-E24 (Studio/Console & human surfaces),
GP-E26 (product audit / security / offline / performance).

**Non-row fold-ins:** CH-17 evidence sweep (the 11-house caller/writer/
source counterexample — tracked evidence debt from the G3 PASS; this Part's
opening evidence act); the R5-D build (register anchor #173, below); the
PR #294 C-B prep (register anchor #118, below); R14 residual
(`exchange.py:739` detail `[:2000]` cut — H8/C12 cluster); R4-A7
source-comment repair (H10 instrument hygiene); H-4 pulse rename
(`form/open.py` pulse labels + `schema_board.py`; pairs with row #124
C2.TargetedPulse — Director approval required, failing-first test first);
30-video placements P01 (H10+H6), P02 (H7 — inside existing persistence,
no new component), P03 (H10 + ledger + Nursery), P04 (H5), P05 (H5+H2 —
**blocked**: needs the not-yet-existing frozen holdout dataset), P06 (H9
geometry fixtures), P08 (SEQ2/HCN — **blocked**: frozen R3 blueprint not
yet retrieved; that retrieval is GP-E22's first step); credit settlements
for merged circuits #413 (C13 Simulate, anchors #167–#170) and #417
(FLOW_CONTRACT execution profiles) — code already merged, identity/credit
decisions ride this Part's register package per Director triage 7040622309.

## (c) Already done vs. what the Part PR must build

- **Done / landed as bounded work:** most rows are PARTIAL with the bounded
  repair already merged (named in each row's register title — e.g. DD-04
  checkpoint family in #47, DD-05 graph journal in #50, DD-09 in #49,
  DD-13 in #58). R5-C policy is ADOPTED (Director FINAL BINDING 7026062701)
  and its records are landing via PR #498. The #294 design disposition
  exists: C-B/C-A split with a Q-E2 minimum OLD_ONLY/NEW_PAIR set, and
  C-B *prep/tests only* are authorized.
- **Build:** the retained remainder of every PARTIAL row above; the OPEN
  rows' first builds (C2 family #121–#129, C3 #131–#134/#136, C6
  #144–#147, C12 #164–#166, C13 #167–#170, #173's retention/compaction
  contract, #185's repair split); GP-E13–E19, E21–E24, E26 per Edition 1
  specs.
- **Hard gates inside this Part (do not cross):**
  - **R5-D (GP-E05 implementation) — HOLD.** Prep is complete (failing-first
    suite, caller census 111, S7 smallest subset named: radial_drift,
    internet_on/off, sandbox_on/off, enhance_on/off). Unlock path, in
    order: Keeper challenge of prep head `13b33fa` → Director bounded
    implementation authorization (at most S7) → only then code, inside
    this Part PR.
  - **Q1 / PR #294 (row #118, GATED) — never merge under the GATE HOLD.**
    C-B failing-first prep and tests are authorized; C-B *code* is not.
  - Rows #34 and #46 (both GATED) keep their gates: legacy-flow ownership
    reconciliation and the pair-atomic everyday-save defect close only
    under their recorded dispositions.

## (d) Part PR contents — checklist

- [ ] CH-17 evidence sweep completed and filed (opens the Part)
- [ ] Per-cluster builds + failing-first tests for every row remainder
- [ ] R5-D code **only if** the two-step unlock above has fired (else the
      Part PR carries R5-D as design + prep records and #173 stays open)
- [ ] #294 C-B prep/tests (no C-B production code, no merge of #294)
- [ ] H-4 pulse rename (if Director-approved) + INDEX-adjacent label fixes
- [ ] P01–P04, P06 placements built at their houses; P05/P08 carried as
      blocked-with-named-blocker, not silently dropped
- [ ] Regression campaigns ×3 per state-sharing cluster (serial, one at a
      time) + exact-head CI at the Part head
- [ ] Register write riding inside: all 70 rows' status updates, incl.
      #413/#417 credit settlements as decided by the authorities
- [ ] §45 evidence package; Director + Keeper confirmations

## (e) Dependencies

- **NEEDS_DIRECTOR:** R5-D bounded implementation authorization (after the
  Keeper challenge); Q1 C-B code authorization (row #118); H-4 rename
  approval.
- **NEEDS_OVERSEER:** row #155 (multi-Psalm / BIMO) — persona execution
  needs an Ace-approved roster before any build.
- Depends on **Part II** for settled Dell contracts consumed by C12/C13
  (Simulate executes Dells; Bridge reports Dell facts) and on **Part VI**
  answers Q-FI012.* (elastic intake waves touching H7/H8) and Q-GS.*
  (row #185's queued repair split).
- Row #166 (room-to-room bridge) depends on row #134 (C3 Rooms) inside
  this same Part — sequence C3 before C12 inside the PR.

---

## (f) Parallel / serial split

- **Parallel from hour zero:** CH-17 sweep; every cluster's failing-first
  tests and isolated-state builds; C2/C3/C6/C12/C13 design+build in their
  own modules; P01–P04/P06 placements; #294 C-B prep/tests; R5-D prep
  records. None of this waits on another Part.
- **Genuine dependencies (named):** C13 Simulate's *final integration*
  consumes Part II's settled Dell contracts (GP-E14 executes Dells) — the
  mechanism builds in parallel; only its contract-conformance pass waits
  for Part II's GP-E07 audit output. Row #166 waits on row #134 (same
  Part). P08 waits on GP-E22's R3 blueprint retrieval (same Part).
  R5-D *code* waits on the Keeper challenge + Director authorization
  (authority dependency, not a Part dependency).
- **Serial by law only:** all state-sharing campaigns (this Part carries
  the heaviest campaign load — its clusters queue in the single global
  campaign line); the merge.
- **Collisions:** `form/open.py` — Part I owns the persistence / save /
  history / rooms / dock / growth regions; Part II owns parse /
  translate / condition / count regions (patch-note protocol in the
  header). `form/persist*.py`, `form/owner_state_lock.py`,
  `form/lifecycle.py`, `form/grow.py`, `form/dell_matrix/confirm_lineage.py`,
  `form/dell_matrix/dock_session.py` — Part I exclusive. Register JSON —
  own rows only.

## (g) BUILD-READY PACKAGE — Part I

- **Branch:** `uni/part-1-architecture`
- **Files to modify:** `form/open.py` (Part I regions only),
  `form/persist.py`, `form/persist_rest.py`, `form/persist_core_ii.py`,
  `form/owner_state_lock.py`, `form/lifecycle.py`, `form/grow.py`,
  `form/accept.py`, `form/dell_matrix/core.py`,
  `form/dell_matrix/confirm_lineage.py`, `form/dell_matrix/dock_session.py`,
  `form/dell_matrix/director_session.py`,
  `form/dell_matrix/acceptance_policy.py`, `form/dell_matrix/atomic_write.py`,
  `form/dell_matrix/embed_bind.py`, `form/duobeta/` (learning cluster).
- **Files to create:** per-cluster failing-first suites —
  `form/c2_resonance_engine_test.py`, `form/c3_witness_time_test.py`,
  `form/c6_boxes_freeze_test.py`, `form/c12_bridge_ledger_test.py`
  (extending existing `form/c13_simulate_test.py`,
  `form/sm35_pair_atomic_test.py`, `form/gs4_sandbox_test.py`,
  `form/r5d_history_retention_test.py`); evidence under
  `director-reports/r5d-evidence/` and a CH-17 report in `director-reports/`.
- **Test suites to run:** the full existing persistence/save battery
  (`persist_full_roundtrip_test`, `checkpoint_generation_stress_test`,
  `graph_journal_crash_test`, `supersession_lineage_restart_test`,
  `water_persistence_test`, `atomic_write_boundaries_test`,
  `owner_namespace_collision_test`, `nursery_confirm_race_test`,
  `growth_persistence_test`, `confirm_placement_test`,
  `resonance_lifecycle_gate_test`, `c13_simulate_test`,
  `duobeta_live_test`, `studio_security_test`, `gui_api_test`) plus the
  new cluster suites, each printing its own final tally line last.
- **Campaign:** ×3 per state-sharing cluster, strictly one campaign at a
  time globally; logs under the goal's `hidden_files/`; SIGINT/SIGQUIT
  reset to SIG_DFL in the driver.
- **Register flips (targets, on confirm):** PARTIAL rows → COMPLETE where
  the retained remainder closes (cluster-by-cluster in the PR); OPEN rows
  → PARTIAL or COMPLETE per evidence; **#34, #46, #118 stay GATED** unless
  their recorded dispositions fire inside this Part; #173 → PARTIAL on
  the retention contract landing (COMPLETE only with R5-D built);
  #185 → PARTIAL on the dock-landing circuit (full close awaits Part VI
  Q-U answers).
- **Authority asks:** (1) PLAN-CONFIRM — Director + Keeper on this
  package; (2) CODE-CONFIRM — scoped at exact head after campaigns + CI;
  (3) standing separate asks already owed: Keeper challenge of R5-D prep
  `13b33fa`, then Director bounded R5-D authorization (at most S7);
  Director Q1 C-B *code* authorization (not requested by the prep).

---
# PART II — THE DELL PLAN: THE 99 DELLS

## (a) Scope in plain terms

Every Dell's contract, proven Dell by Dell: the Core I (00–50) and Core II
(51–99) families F1–F30 of the Unified Edition, the English door that
translates human language into those contracts, and the §14.3 family
slices that are Dell-level contracts (C4 Reference, C5 Nursery door, C7
Measure, C9 Translate, C10 Harmonic stamps, C11 Editing/Shelf/Manifest).
This is the language gate: Edition 1 puts its circuits first because
everything in Part I that *executes* Dells consumes these contracts.

## (b) Register rows assigned

| MWL # | Short title | IDs | Status |
|---|---|---|---|
| 11 | Parallel must mean parallel — concurrency design slice | DD-43 / C1.ConcurrencyDesign | OPEN |
| 12 | While/Until | Q-DD42.2 | OPEN |
| 13 | Loop 13 receipted grammar follow-up | Q-DD44.2 | OPEN |
| 24 | Review English Intent.args as a separate end-to-end contract | 72-06 / SM-11 / DD-01 / DD-02 | PARTIAL |
| 28 | Stress Seed grammar + error precedence | 72-10 / SM-58 | PARTIAL |
| 29 | Reconcile English create + direct REPL handlers with canonical Mandell | 72-11 / SM-12 / SM-13 | PARTIAL |
| 30 | Deepen reachability for already-supported English actions only | 72-12 / G-02 / SM-14 | PARTIAL |
| 31 | Audit 17 typed-signature error/coercion contracts | 72-13 / SM-17 / SM-19 | PARTIAL |
| 35 | Remove/relabel literal Show placeholder output — message-layer R-B repair Director-confirmed boun… | 72-17 / DD-03 | PARTIAL |
| 36 | Audit message-only Dell descriptions for truthful operations | 72-18 / SM-23 | PARTIAL |
| 37 | Preserve first-failure provenance through mixed chain receipts | 72-19 | PARTIAL |
| 38 | Challenge Branch/Parallel/Sequence/Join reported guarantees | 72-20 / SM-18 | PARTIAL |
| 39 | Stress Until/While/ForEach bounds + nested control inheritance | 72-21 / SM-18 | PARTIAL |
| 41 | Challenge Commit/Revert exact state + side-effect boundaries | 72-23 | PARTIAL |
| 43 | Protect Define/Alias/Compose against failed-run persistence | 72-25 | PARTIAL |
| 45 | Recheck Guard/Assert failure propagation across control frames | 72-27 | PARTIAL |
| 95 | Strengthen Dell 08 naming, slug collision, skin, legacy-label regression coverage | SM-22 | OPEN |
| 96 | Reverify reserved-address refusal / honest unsupported behavior of Bridge and Embed | SM-24 | OPEN |
| 113 | Symbiosis pairwise compatibility: 100×99 ordered pairs + standalone, classified with evidence; co… | G-06 | PARTIAL |
| 114 | Full-registry D1 deepening: per-Dell deep-contract circuits until ALL 100 Dells reach a high stan… | G-07 | PARTIAL |
| 137 | Zipper — Compress + Expand as one circuit: Compress preserves a resolvable source link; Expand re… | DD-20 / C4.Zipper | OPEN |
| 138 | Inject by reference + Reference dereferencing — Inject adds a reference, not a duplicate; cycles/… | DD-26 / C4.InjectRef | OPEN |
| 139 | Distill = essence — uses actual words/detail/goals, carries provenance and disclosed omissions, u… | DD-28 / C4.Distill | OPEN |
| 140 | Nursery ranking formula — exactly S = 0.40 LINK + 0.25 ACE + 0.20 FRESH + 0.15 NOVEL; top five pe… | C5.Formula | PARTIAL |
| 141 | Switchable Plane ranking — Rank measure is switchable per Ace's ruling | C5.PlaneRank | OPEN |
| 142 | One search machinery, two faces — Discover + Resolve: stable ordered pages reach every authorized… | DD-25 / DD-49 / C5.Search | OPEN |
| 143 | Nursery door policy — auto-passage stays OFF until Ace supplies standards and scope; Cycle never … | DD-27 / C5.Door | OPEN |
| 149 | Profile is the speedometer — named stages with monotonic timing, environment/workload identity, o… | DD-39 / C7.Profile | OPEN |
| 150 | Token accounting + shorthand in harmony | DD-30 / C7.Tokens | PARTIAL |
| 151 | Universal measurement family + incorporation sweep — Measure / Threshold / Weight-Normalize with … | DD-46 / DD-47 / DD-48 / C7.MeasureFamily | OPEN |
| 156 | Translate: honest no-intent — unknown text produces no invented Show seed; receipts name determin… | DD-35 / C9.NoIntent | OPEN |
| 157 | Translate dual-mode / Adapt incorporation — Adapt adoption ruled by Ace | DD-36 / C9.DualMode | OPEN |
| 158 | Harmonic stamps — item-attached stamps with provenance in stable order; moving an item never sile… | DD-24 / C10.Stamp | OPEN |
| 159 | Harmonic lenses — harmony organization/retrieval + derived lens modes; views rearrange DISPLAY on… | C10.Lenses | OPEN |
| 160 | The private shelf / little notebook — Macro read back as one seed; Ace's private notebook design | DD-38 / C11.Shelf | OPEN |
| 161 | Idea editing system — go inside, edit the parts, propose the change: contained-part drafts indepe… | DD-41 / C11.Edit | OPEN |
| 162 | Manifest split — Confirm is the yes, Manifest is the walk: confirmed-but-unmanifested is explicit… | DD-40 / C11.Manifest | OPEN |
| 163 | Universal Move — Move moves anything movable: dispatches by explicit object class to EXISTING eng… | DD-50 / C11.Move | OPEN |
| 177 | FRESH aging — RULED by Ace 2026-11-10: proposals age at 3/7/14-day marks and fade at 30 days ONLY… | Q-N3 | OPEN |
| 178 | Embed provider — RULED by Ace 2026-11-10: provider-agnostic dock capability | Embed provider (§14.8) | OPEN |
| 179 | Distill mode — RULED by Ace 2026-11-10: conditional — a docked AI distills when one is docked, th… | Distill mode (§14.8) | OPEN |

**Edition 1 circuits assigned (11):** GP-E01 (R24 — English translation
must not rewrite operands), GP-E02 (R23 — outcome evidence completeness +
reachable search), GP-E03 (R17/R19 — **built and credited**, see below),
GP-E04 (R25 — **built**, credit pending), GP-E07 (whole addressed-Dell
execution audit), GP-E08 (typed English/LM/Seed admission; anchor row
#24), GP-E09 (shared conditional engine; DD-42 residual), GP-E10 (DD-43
Parallel as real isolated arms), GP-E11 (eight thin-spec elder Dells),
GP-E12 (quantification & inference), GP-E20 (Nursery full behavior; C5).

**Non-row fold-ins:** the PR #308 oracle modernization (anchor row #24 —
the verify-72-06 oracle is modernized *inside this Part*: historical
artifacts preserved byte-for-byte, a current-main delta document added, a
NEW REPL current-contract probe added, the 5 changed checks classified —
E19/E20 Class E defect gone, A5 silent clamp removed, D17/D18 dead-arg
production gone); #433 Phase T prototype design (FI-010, Dell Plan gate
design); credit settlements for merged circuits #401 (C7.Profile,
anchor row #149), #416 + #439 (the LM-4 pair — LatinMandell toll booth +
resource guard on the English entry path), #429 + #457 (SYS-C29 / C5R.1 —
the G-20 Nursery-store family, anchored to the C5 cluster rows
#140–#143).

## (c) Already done vs. what the Part PR must build

- **Done:** GP-E03 is closed — R17's row (#14) is COMPLETE via PR #500;
  R19/R19-SIB are credited with no register row (Director identity ruling
  7027783108) and never become board points. GP-E04 (R25) is built and
  merged (`c13428cb`); its Keeper credit CONFIRM is an authority act
  outstanding, recorded in this Part's package. GP-E01 and GP-E02 specs
  are ACCEPTED with defects reproduced — they are build-ready today.
- **Build:** GP-E01, GP-E02; the GP-E07 addressed-Dell audit (evidence
  first, then per-Dell repair gates); GP-E08 typed admission closing row
  #24's remainder; GP-E09 conditional engine (rows #11–#13 family);
  GP-E10 Parallel arms (row #11); GP-E12 (rows #149–#151); GP-E20 Nursery
  behavior (rows #140–#143 + ruled rows #177 FRESH aging, #178 Embed
  provider, #179 Distill mode — noting #179 overlaps row #139, see
  conflicts); the C4 rows #137–#139, C9 #156–#157, C10 #158–#159, C11
  #160–#163; D1 deepening #114 and symbiosis classification #113; the
  PARTIAL remainders of rows #28–#31, #35–#39, #41, #43, #45, #150.

## (d) Part PR contents — checklist

- [ ] GP-E01 + GP-E02 builds with failing-first suites (specs accepted)
- [ ] GP-E07 audit evidence + per-Dell repair gates executed
- [ ] #308 oracle modernization bundle (delta doc + new REPL probe +
      5-check classification; historical artifacts untouched)
- [ ] C4/C5/C7/C9/C10/C11 family builds + suites
- [ ] #433 Phase T prototype design record
- [ ] Campaign ×3 + exact-head CI
- [ ] Register write riding inside: all 41 rows' updates + the
      #401/#416/#429/#439/#457 credit settlements as decided
- [ ] §45 package; Director + Keeper confirmations

## (e) Dependencies

- **NEEDS_OVERSEER:** row #143 (C5.Door) — Nursery auto-passage stays OFF
  until Ace supplies standards and scope; GP-E11 — the eight elder Dells
  carry Ace's semantic gate (Edition 1's own text).
- **NEEDS_DIRECTOR:** row #12 — Q-DD42.2, the While/Until infix-condition
  plan-reading question (also registered in Part VI).
- Part I's C13/C12 integration passes consume this Part's GP-E07 output —
  a downstream dependency *of Part I on this Part*, not a blocker here.

## (f) Parallel / serial split

- **Parallel from hour zero:** GP-E01/E02 builds, the #308 bundle, every
  family slice (C4/C5/C7/C9/C10/C11) in its own modules, the GP-E07 audit
  (read-only evidence), all failing-first suites.
- **Genuine dependencies:** GP-E07's repair gates depend on its own audit
  output (intra-Part sequence, not a cross-Part wait). Nothing in this
  Part waits on another Part to start.
- **Serial by law only:** campaigns (global queue) and the merge.
- **Collisions:** `form/open.py` — Part II owns the parse / translate /
  condition / count regions; Part I owns the rest (patch-note protocol).
  `form/repl.py` — Part II primary (the #308 probe is a REPL contract
  probe); Part I lanes do not edit `repl.py`. Nursery store files
  (`form/dell_matrix/` Nursery modules) — Part II owns the C5 door/
  ranking surface; Part I owns confirm *placement* machinery
  (`confirm_lineage.py`) — the GS-4 boundary between them is row #185
  (Part I) vs rows #140–#143 (Part II), split by file as named here.

## (g) BUILD-READY PACKAGE — Part II

- **Branch:** `uni/part-2-dell-plan`
- **Files to modify:** `form/open.py` (Part II regions only),
  `form/repl.py`, `form/dell_matrix/core.py` (Dell contracts — shared
  with Part I by region: Part II owns contract definitions, Part I owns
  state machinery; conflicts resolved by the patch-note protocol).
- **Files to create:** `form/r24_operand_integrity_test.py`,
  `form/r23_outcome_evidence_test.py` (or the suites' house names per
  Edition 1 specs); the #308 delta document + REPL probe under
  `director-reports/` (72-06 evidence directory); per-family suites for
  C4/C7/C9/C10/C11 remainders.
- **Test suites to run:** existing `form/translate_intent_args_test.py`,
  `form/translate_word_counts_test.py`, `form/translate_dead_args_test.py`,
  `form/typed_signature_contracts_test.py`,
  `form/seed_grammar_stress_test.py`, `form/dd42_predicate_infix_test.py`,
  `form/step7_control_verdicts_test.py`, `form/step8_transactions_test.py`,
  `form/guard_assert_propagation_test.py`,
  `form/define_compose_nonpublication_test.py`,
  `form/first_failure_provenance_test.py`, `form/c7profile_test.py`,
  `form/c7schema_test.py`, `form/nursery_c5r*_test.py` family,
  `form/r25_extra_operand_test.py`, `form/eval_predicate_surplus_test.py`.
- **Campaign:** ×3 in the global serial queue + exact-head CI.
- **Register flips (targets, on confirm):** #24 PARTIAL → COMPLETE
  (with the modernized oracle as its verification instrument); #149
  PARTIAL → COMPLETE via the #401 settlement; #140 PARTIAL → COMPLETE;
  remaining PARTIAL rows → COMPLETE per remainder closure; OPEN rows →
  PARTIAL/COMPLETE per evidence; **#143 stays OPEN until Ace's door
  standards land** (flagged, not silently held).
- **Authority asks:** (1) PLAN-CONFIRM — Director + Keeper on this
  package; (2) CODE-CONFIRM — scoped at exact head; (3) Keeper scoped
  CODE CREDIT CONFIRM for R25/GP-E04 at `c13428cb` (already packaged,
  7040793444); (4) Director ruling on Q-DD42.2 (row #12).

---
# PART III — THE INCOMPLETENESS REGISTER (GP-G01..GP-G28)

## (a) Scope in plain terms

The defect register itself: the Unified Edition's §4 list of 28 known
incompletenesses (GP-G01..GP-G28), the MWL rows that *are* register-level
defects rather than builds, and the limits-wave completion circuit. This
Part's PR is mostly evidence and disposition records — the *code* that
closes most G-items rides in Parts I and II, where the register rows live;
this Part proves the register is complete, current, and honestly
dispositioned.

## (b) Register rows assigned

| MWL # | Short title | IDs | Status |
|---|---|---|---|
| 21 | Independently reproduce DAF-09 session-escape cleanup | 72-03 / SM-02 | OPEN |
| 120 | Historical verify-72-17 reproducer hygiene: give the stale pre-repair probe an explicit/manual hi… | 72-67 follow-up | OPEN |
| 172 | Beyond-72 extension register framework | F1/F4 | OPEN |
| 174 | Guard/Catch wording hygiene — a separate bounded hygiene opportunity | C1 hygiene (§14.7) | OPEN |

**Edition 1 circuit assigned:** GP-E06 — remaining limits waves R28–R42
(census class E; builds per confirmed defect, which land in the defects'
home Parts I/II — this Part carries the wave-completion record).

**Non-row work:** disposition records for all 28 GP-G items (G-01 Space,
G-02 Weather, G-03 Gravity Wells, G-04 Water & Growth, G-05 Forces
Restore, G-06 Resonance Log Cap, G-07 Route, G-08 Reference, G-09 True
Compare, G-10 Measure, G-11 Parallel, G-12 suggest_preferred, G-13
logistic_map, G-14 limitation_knowledge, G-15 Dell 151 [Harmonic], G-16
DuoBeta Rollback, G-17 Selfgrow, G-18 gate_discipline, G-19 Equation
Ledger class, G-20 Nursery Store cut, G-21 Everyday Save Pair, G-22
Studio __RENDER__, G-23 'Harmonic' name, G-24 *_150_loop harnesses, G-25
Tree/Chord/Nerve, G-26 Smith's Flow, G-27 LatinMandell LM-4..7, G-28 Tree
Variants) — each marked: closed-by (Part/row), still-open-in (Part/row),
or no-MWL-row (record only). Per Unified Part V §3a, only 6 of the 28 map
to MWL rows; the other 22 exist only here.

## (c) Already done vs. what the Part PR must build

- **Done:** limits waves 1–8 verification records landed (through PR
  #484/#449); several G-items' underlying defects are already repaired
  inside Parts I/II rows (G-20's repairs via the SYS-C29 family, G-21 =
  row #46's subject, G-12/G-16/G-17 = rows #69/#70/#72 subjects).
- **Build:** the G-item disposition ledger itself; row #21's evidence
  chain (DAF-09 session-escape — the register records it BLOCKED: the
  Director's independent reproduction is the missing act, and §31 law
  forbids resolving DAF-09 on local evidence); row #120's reproducer
  hygiene (the stale pre-repair verify-72-17 probe gets an explicit
  historical/manual profile); row #172's extension-register framework
  (F1/F4: new objectives get distinct IDs checked against both registers);
  row #174's Guard/Catch wording hygiene (bounded, contract-preserving);
  GP-E06's wave-completion record for R28–R42.

## (d) Part PR contents — checklist

- [ ] GP-G01..28 disposition ledger (new register-adjacent record)
- [ ] DAF-09 evidence chain updated; status stays as the evidence says
- [ ] verify-72-17 reproducer hygiene (row #120)
- [ ] Extension framework record (row #172) + wording hygiene (row #174)
- [ ] GP-E06 completion record; per-defect builds confirmed landed in
      Parts I/II or explicitly carried as still-open
- [ ] Register write riding inside: rows #21, #120, #172, #174 updates
- [ ] §45 package; Director + Keeper confirmations

## (e) Dependencies

- **NEEDS_DIRECTOR:** row #21 — DAF-09 closes only on the Director's
  independent reproduction/verification; Uni-side evidence is necessary
  but never sufficient. This also gates Part VII's row #112.
- No Ace decision outstanding. No dependency on any other Part's build;
  the disposition ledger *reads* Parts I/II states at integration time.

## (f) Parallel / serial split

- **Parallel from hour zero:** the entire Part — it is evidence, hygiene,
  and records work in its own files.
- **Genuine dependencies:** none for building; the ledger's *final*
  dispositions snapshot Parts I/II at landing.
- **Serial by law only:** the merge; a campaign only if row #174's
  hygiene touches product code (then it joins the global queue).
- **Collisions:** none with product-code lanes. Register JSON — own rows
  only. The verify-72-17 probe file is Part III exclusive (Part II's
  #308 work covers verify-72-06, a different probe).

## (g) BUILD-READY PACKAGE — Part III

- **Branch:** `uni/part-3-incompleteness-register`
- **Files to create:** `director-reports/GP_G_REGISTER_DISPOSITIONS_2026-11-20.md`;
  `director-reports/EXTENSION_REGISTER_FRAMEWORK_2026-11-20.md`.
- **Files to modify:** the verify-72-17 historical probe (explicit
  manual profile; path per row #120's record in `director-reports/`);
  Guard/Catch wording sites **only** under row #174's bounded hygiene
  contract.
- **Test suites:** `form/dd45_chain_parse_refusal_test.py` and the
  Guard/Catch contract suites (hygiene must prove no behavior change);
  DAF-09 suites (`form/daf09_timeout_tree_test.py`) run for evidence,
  never as a local resolution.
- **Campaign:** ×3 only if product code changes; otherwise exact-head CI.
- **Register flips (targets, on confirm):** #120 OPEN → COMPLETE;
  #172 OPEN → COMPLETE; #174 OPEN → COMPLETE; **#21 stays OPEN** until
  the Director's independent DAF-09 act lands (its target is evidence
  completeness, not closure).
- **Authority asks:** (1) PLAN-CONFIRM — Director + Keeper; (2)
  CODE/RECORDS-CONFIRM at exact head; (3) Director: DAF-09 independent
  reproduction (the standing owed act behind row #21 and Part 0's #116).

---
# PART IV — THE FAR STRATUM (FAR-1..FAR-20, THE READER, G-29/G-30/G-31)

## (a) Scope in plain terms

Everything deferred, visionary, or parked: the V vision objectives (the
Nursery as a visual, spatial, playful place — cards, shapes, SKY, ROOM,
the Psalm Matrix page, the AI-talk place), the Human Surface track, the
Far Stratum research lines (FAR-1..20, the Reader, the provisional
G-29..31), the declined Exchange Phase G, the parked waves study, and
Ace's own sandboxed side items. Ace opened §7 on 2026-11-14 ("this will
for sure be implemented") — opened means *in the plan*, not built: by the
Unified Edition's own law this stratum begins only after the Grand
Synchronization (Part VII) closes, and every item still passes its own
certification in its turn.

## (b) Register rows assigned

| MWL # | Short title | IDs | Status |
|---|---|---|---|
| 99 | Nursery proposal CARDS | V-01 | OPEN |
| 100 | Custom idea shapes in the Nursery | V-02 | OPEN |
| 101 | AI-suggested looks | V-03 | OPEN |
| 102 | Nursery as THE primary decision screen | V-04 | OPEN |
| 103 | SKY perspective | V-05 | OPEN |
| 104 | ROOM perspective | V-06 | OPEN |
| 105 | Navigation: zoom + tap-to-glide; recursive exploration of ideas within ideas — DEFERRED; depends … | V-07 | OPEN |
| 106 | Page set: Plane, Nursery, Dells, Dell Playground, Psalm Matrix — transitions preserve current ide… | V-08 | OPEN |
| 107 | Navigation placement RESEARCHED online before implementation — DEFERRED; precedes any V-08 build | V-09 | OPEN |
| 108 | PSALM MATRIX: the AI page — Psalms + personas + status + docking visible there; no second authori… | V-10 | OPEN |
| 109 | AI-talk place: pure English, NOT a chat box — a new interaction concept to invent — DEFERRED | V-11 | OPEN |
| 110 | Human-validation gates: | V-12 | OPEN |
| 111 | Reserved neural research: weight-space programming / targeted enhancement of a less powerful AI —… | V-13 | OPEN |
| 117 | Exchange Phase G | G-10 | OPEN |
| 171 | Human Surface track | H track | OPEN |
| 176 | Literal wave-field instrument — INNOVATE_DEFERRED, parked | Waves study (§14.9) | OPEN |
| 180 | NVIDIA Inception website — SANDBOXED by Ace 2026-11-10: real-life side mission, NOT DellMatrix wo… | NVIDIA (website) | SANDBOXED |
| 181 | NVIDIA Inception incorporation — SANDBOXED by Ace 2026-11-10: real-life side mission, NOT DellMat… | NVIDIA (incorporation) | SANDBOXED |
| 182 | Live-model demo step 6 — parked by Ace 2026-11-10 until he is at a computer; he will run the time… | Live-model demo step 6 | SANDBOXED |

**Edition 1 circuit assigned:** GP-E28 — Far Stratum as future
independent units (design/evidence class; no product code until its
phase gate).

**Non-row fold-ins:** FI-017's full development (the docked-Gemini role
at three depths — Nursery operator, knowledge conductor, resident
developer; intake Ace 2026-11-16, confirmed in his words 2026-11-17;
register row of record lives in the goal-workspace decision register,
not the MWL — this Part carries its development paper and any
plan-belt build the Director places); 30-video placement P07 (model
editing / hyperchaotic control — DEFERRED by the Director, retained only
as negative examples inside P03/P04 in Part I); the FAR-1..20 / Reader /
G-29..31 design records from Unified Part IV.

## (c) Already done vs. what the Part PR must build

- **Done:** the vision is fully written down (Unified Part IV + the V
  rows' register text + Edition 1's journey acceptances); FI-017's
  intake and placement are settled; the 30-video study is complete
  (29/30 transcripts; V18 has no captions — unresolved by evidence, not
  neglect).
- **Build (this Part's PR):** design-complete, build-ready packages for
  each V row and FAR line — placements, dependencies, and acceptance
  terms — so that when the phase gate opens, builds start without
  re-planning. **No product code for V/FAR items lands in this Part PR**
  unless the Grand Synchronization has closed and the item's own
  authorization has fired; the PR is the stratum's complete design +
  evidence body, with FI-017's development paper as its one build-class
  deliverable (paper only, per its intake fences: a docked AI never
  confirms/rejects/deletes/lands; Nursery confirmation stays Ace's).
- **Parked by Ace, untouched:** rows #180, #181 (NVIDIA side missions —
  not DellMatrix work) and #182 (live-model demo — Ace runs it himself
  at a computer). They are listed here so the coverage is complete;
  this Part does not work them.

## (d) Part PR contents — checklist

- [ ] Per-row design packages for #99–#111 (V-01..V-13), each with
      dependencies (V-03→V-01, V-05/V-06→#105 family, V-09 research
      before any V-08 build) and acceptance terms
- [ ] H track (#171) consolidated surface plan, cross-filed with the
      V rows it shares (Nursery cards/shapes)
- [ ] FAR-1..20 + Reader + G-29..31 design records refreshed against
      current main
- [ ] FI-017 development paper (full, per the Sweep manifest's C2)
- [ ] #117 carried as DECLINED with its history intact; #176 carried
      as parked research with its revisit condition stated
- [ ] Register write riding inside: status notes only — **no V/FAR row
      flips to COMPLETE from design work** (counting law: plan ≠ code)
- [ ] §45 package; Director + Keeper confirmations

## (e) Dependencies

- **NEEDS_OVERSEER:** unparking or authorizing any V row build, the
  H track build, or rows #180–#182 — all Ace's acts. Row #110 (V-12)
  requires Ace personally working the Matrix as one of its two
  validation gates.
- **Phase dependency (named):** V/FAR *builds* depend on Part VII's
  Grand Synchronization rehearsal closing (Unified §7 law). The design
  packages do not.
- Depends on Part I's GP-E23 (Dock) and Part II's C5 rows for FI-017's
  operating surfaces when its build turn comes.

## (f) Parallel / serial split

- **Parallel from hour zero:** all design packages, the FI-017 paper,
  the FAR design refresh — paper lanes touch no product code.
- **Genuine dependencies:** builds (not designs) on Part VII's
  synchronization, as above.
- **Serial by law only:** the merge. No campaigns (no product code).
- **Collisions:** none — this Part writes records and design files
  exclusively. Register JSON — status notes on own rows only.

## (g) BUILD-READY PACKAGE — Part IV

- **Branch:** `uni/part-4-far-stratum`
- **Files to create:** `director-reports/FAR_STRATUM_DESIGN_PACKAGES_2026-11-20.md`;
  `director-reports/FI017_DEVELOPMENT_2026-11-20.md`;
  `director-reports/VISION_SURFACE_PLAN_2026-11-20.md` (V rows + H track).
- **Files to modify:** none in `form/`. Register JSON (notes only).
- **Test suites:** none (no product code). Verification = cross-reference
  check of every design package against its register row + Unified
  Part IV entry.
- **Campaign:** none.
- **Register flips:** none targeted. Rows stay OPEN / SANDBOXED by
  design; the PR's register write records the design-complete state in
  row text where the authorities confirm it.
- **Authority asks:** (1) PLAN-CONFIRM — Director + Keeper on the
  design packages; (2) RECORDS-CONFIRM at exact head. Build
  authorizations for individual V/FAR items are *future* asks, named
  per item in its package, gated on Part VII + Ace where flagged.

---
# PART V — THE SCOREBOARD RECONCILIATION (EVIDENCE FOR PART 0)

## (a) Scope in plain terms

Keeping the two universes — the canonical MWL register (182) and the
Grand Plan census (224) — reconciled forever, so the board can never
silently lag the work again (the exact failure Ace caught on 2026-11-20,
settled by PR #500). This Part is deliberately small: most reconciliation
already landed (#478, #479, #500). What remains is the *automation and
format* layer that keeps it true without a human settlement drive.

## (b) Register rows assigned

| MWL # | Short title | IDs | Status |
|---|---|---|---|
| 90 | Automate morning-report reconciliation, staleness, next-best recommendations | 72-72 / SM-09 (theme) | PARTIAL |
| 93 | Standardize morning Director report format | SM-09 | OPEN |
| 94 | Connect NBD ranking to real report status, dependencies, improvement candidates; deterministic st… | SM-10 | OPEN |

**Edition 1 circuits assigned:** none — Edition 1 has no reconciliation
circuit; its file `01_SOURCE_CROSSWALK_CANDIDATES.json` is this Part's
primary input (a *candidate* crosswalk, never adopted as-is).

**Non-row work:** the MWL × Edition 1 × Unified census crosswalk brought
to current main and kept there; disposition of the 49 unadopted Grand
Plan census candidates (the 224's non-MWL items — each: adopt into the
register by authority ruling, or record as census-only permanently);
the flagged duplicate pairs from Unified Part V §4b (judgment pairs NOT
deducted in the primary count — each gets a ruling or a permanent
flag); the Sitting #002 evidence pack (Mon 2026-11-23, ≥42 primary /
≥39 secondary on the canonical 182 basis).

## (c) Already done vs. what the Part PR must build

- **Done:** the canonical rule itself (register + `master_list.py` at a
  pinned SHA, STALE/UNVERIFIED labeling); the #421 reconciliation (224
  relabeled internal census); the #500 settlement mechanism.
- **Build:** row #90's morning-report reconciliation automation
  (staleness detection + next-best recommendations tied to real status);
  row #93's standardized report format (its own register note says it
  folded operationally into #90 — the pair closes together, counted
  once, see conflicts); row #94's NBD ranking connection (ranking reads
  real report status, dependencies, and improvement candidates —
  deterministic stale-candidate handling); the crosswalk + candidate
  dispositions above.

## (d) Part PR contents — checklist

- [ ] Morning-report reconciliation automation + staleness tests (#90)
- [ ] Standard report format implementation (#93, paired with #90)
- [ ] NBD ranking ↔ status connection (#94)
- [ ] Crosswalk refreshed at the Part head's main pin; candidate
      dispositions recorded (no silent adoptions)
- [ ] Sitting #002 evidence pack prepared
- [ ] Register write riding inside: rows #90, #93, #94 updates
- [ ] §45 package; Director + Keeper confirmations

## (e) Dependencies

- **NEEDS_DIRECTOR:** adoption of any of the 49 census candidates into
  the register (a ruling, not a Uni act); rulings on the §4b flagged
  duplicate pairs.
- Consumes every other Part's register writes at integration — this
  Part's automation is what *detects* drift in theirs; it does not
  block them.

## (f) Parallel / serial split

- **Parallel from hour zero:** all of it — format, automation, crosswalk.
- **Genuine dependencies:** none for building. The Sitting #002 pack
  snapshots the board as of 2026-11-23.
- **Serial by law only:** the merge; campaign only if the automation
  lands as product code in `form/` (then it joins the global queue).
- **Collisions:** `director-reports/master_list.py` — Part V owns
  render/automation changes; Part 0 owns gate changes to
  `certification_runner.py` — the two files are different, the split is
  by file. NBD register files (`director-reports/NBD_*.md`) — Part V
  exclusive. Register JSON — own rows only.

## (g) BUILD-READY PACKAGE — Part V

- **Branch:** `uni/part-5-scoreboard-reconciliation`
- **Files to create:** `director-reports/CROSSWALK_CURRENT_2026-11-20.md`;
  `director-reports/CENSUS_CANDIDATE_DISPOSITIONS_2026-11-20.md`.
- **Files to modify:** `director-reports/master_list.py` (automation
  hooks only), `director-reports/NBD_MASTER_OBJECTIVE_REGISTER.md`,
  `director-reports/NBD_OBJECTIVE_RECONCILIATION.md`; morning-report
  tooling where it lives in the goal workspace (not the repo) for
  row #90's automation.
- **Test suites:** render determinism check (`master_list.py --check`
  byte-identical at the pin); staleness-detection tests for the #90
  automation; ranking-determinism tests for #94.
- **Campaign:** ×3 only if `form/` code changes; otherwise CI.
- **Register flips (targets, on confirm):** #90 PARTIAL → COMPLETE;
  #93 OPEN → COMPLETE (paired with #90, one closure); #94 OPEN →
  PARTIAL or COMPLETE per the ranking-connection evidence.
- **Authority asks:** (1) PLAN-CONFIRM — Director + Keeper; (2)
  CODE/RECORDS-CONFIRM at exact head; (3) Director rulings on candidate
  adoptions + §4b pairs (rolling, not blocking the PR).

---
# PART VI — THE UNIFIED UNKNOWNS REGISTER

## (a) Scope in plain terms

Every question that only an authority can answer, prepared so answering
is cheap: each question packaged with its evidence, its options, a Uni
recommendation, and the exact list of work it unblocks. This Part builds
almost nothing — it is the decision register. Its PR closes when the
answers land; until then it is the standing, evidence-backed ask list
for Ace and the Director, replacing questions scattered across months of
comments.

## (b) Register rows assigned

| MWL # | Short title | IDs | Status |
|---|---|---|---|
| 119 | Atomic-write sweep wiring decision | Q-35.1 / 72-35 follow-up | OPEN |
| 175 | Q-SNAP.3 launch/signal-hardening proposal — proposal-only product change if still desired; no G-1… | Q-SNAP.3 / F6 | OPEN |

**Edition 1 circuits assigned:** none — Edition 1's decision register
(file `03_DECISION_AND_UNKNOWN_REGISTER.md`: ruled/disproven items,
fifteen unified unknowns with Director design decisions, SYSTEM-001
DC-1..11, sovereign packets E) is this Part's sibling source; where
Edition 1 already records a Director design decision, this Part carries
the *closure evidence*, not a re-ask.

**The question families (non-row, each with its unblock list):**

| Family | Owed by | Unblocks |
|---|---|---|
| Q-GS.1–Q-GS.11 (growth selection) | Director/Ace per item | Part I row #185's queued repair split (Q-U.2 dock-landing already authorized as a bounded circuit; Q-U.3 confirm-placement inheritance; Q-U.4 manual-confirm cross-wall semantics — **Ace sovereignty ruling**; Q-U.5 auto-confirm sweep) |
| Q-FI011.1 / .2 / .4 (.3 answered: sandbox-first default) | Ace/Director | Nursery auto-confirm gates — Part II C5 door cluster (#143's neighborhood) |
| Q-FI012.1–.10 (minus .3) | Director | FI-012 elastic-intake waves W1–W5 — Part I H7/H8 builds; **Q.8's census probe is owed by Uni** and is this Part's one build item |
| Q-FI016.1 | UNKNOWN (owner not established) | FI-016 placement |
| Q-DD42.2 | Director | Part II row #12 (While/Until infix refusal surface) |
| Q-DD18.2 | Director (dormant) | Pulse-receipt follow-up — Part I H-4 cluster |
| R21's DD-54 question (SNAPSHOTS_CAP retirement) | Director | Part I row #135's retained remainder scope |
| DAF-09 | Director (independent reproduction) | Part III row #21; Part 0 row #116; Part VII row #112 certification |

## (c) Already done vs. what the Part PR must build

- **Done:** Q-FI011.3 answered; Q-U.2 authorized; the questions
  themselves are inventoried (this map's table is the inventory).
- **Build:** one evidence packet per family (question, evidence,
  options, recommendation, unblocks); the Q-FI012.8 census probe (Uni
  build, M-34); row #119's decision record (Q-35.1 — `sweep_stale_tmps`
  has no production caller: wire it, or record the orphan-temp cleanup
  as manual-only by ruling); row #175's proposal disposition
  (Q-SNAP.3 launch/signal hardening — proposal-only unless ruled).

## (d) Part PR contents — checklist

- [ ] Per-family evidence packets (new decision record file)
- [ ] Q-FI012.8 census probe built + run, results filed
- [ ] Row #119 + #175 disposition records drafted for ruling
- [ ] Register write riding inside: #119, #175 updates **as ruled**
      (no self-answering: unruled rows stay OPEN with the packet cited)
- [ ] §45 package; the asks below transmitted with it

## (e) Dependencies

- This Part *is* dependencies: every family names its authority above.
  **NEEDS_OVERSEER:** Q-U.4 (manual-confirm cross-wall semantics — Ace's
  sovereignty call) and the Ace-side Q-FI011 items. **NEEDS_DIRECTOR:**
  all other families.
- Nothing in Parts 0–V *starts* blocked on this Part; specific
  remainders (named in Parts I/II) close when answers land.

## (f) Parallel / serial split

- **Parallel from hour zero:** all packets and the census probe.
- **Genuine dependencies:** closures depend on authority answers —
  rolling, by design; the lane never idles waiting, it prepares the
  next family.
- **Serial by law only:** the merge.
- **Collisions:** none (records + one probe suite). Register JSON —
  own rows only, and only as ruled.

## (g) BUILD-READY PACKAGE — Part VI

- **Branch:** `uni/part-6-unknowns`
- **Files to create:** `director-reports/UNKNOWNS_DECISION_PACKETS_2026-11-20.md`;
  `form/fi012_q8_census_probe_test.py` (the Q.8 probe suite).
- **Files to modify:** none in `form/` except the probe; register JSON
  as ruled.
- **Test suites:** the Q.8 probe; no other suites (no product change).
- **Campaign:** none (probe runs standalone, isolated state).
- **Register flips (targets):** #119 OPEN → COMPLETE **if ruled**
  (else stays OPEN with packet cited); #175 OPEN → COMPLETE if the
  proposal is ruled in or formally retired (else OPEN, packet cited).
- **Authority asks:** (1) PLAN-CONFIRM — Director + Keeper on the
  packet set; (2) the per-family rulings themselves (Ace: Q-U.4 +
  Q-FI011 Ace items; Director: the rest), transmitted as one bundle
  with per-question packets; (3) RECORDS-CONFIRM at exact head.

---
# PART VII — EXECUTION ORDER AND THE IN-PROGRESS SET

## (a) Scope in plain terms

The order itself, the drive that runs it, and the final proof: the
standing SUSX100,000 completion drive (the execution system this map is
part of), the Director–Uni handoff hardening, the §5 sequence's closing
acts — the Grand Synchronization rehearsal over the 25 journey
acceptances — and whole-program certification. This Part's PR is the
last to *close*, because certification is definitionally last; its
builds (handoff, drive records, rehearsal harness) start at hour zero
like every other lane.

## (b) Register rows assigned

| MWL # | Short title | IDs | Status |
|---|---|---|---|
| 27 | Harden Director–Uni next-best circuit handoff | 72-09 / SM-07 (twin claim — see coverage note) | PARTIAL |
| 112 | Whole-program certification + REAL_USER_PATH claims — register BLOCKED: certification WITHHELD by… | G-05 | OPEN |
| 115 | SUSX100,000 execution run — the standing completion drive itself | G-08 | PARTIAL |

**Edition 1 circuit assigned:** GP-E27 — public journey certification /
Grand Synchronization (the 25 journeys of Edition 1 file
`06_JOURNEY_ACCEPTANCE.md` are this Part's acceptance checklist).

**Non-row work:** the merge-queue record for all eight Part PRs (landing
order: **0 → V → III → II → I → VI → IV → VII** — a merge order only,
chosen so tooling and reconciliation land before the big code Parts,
Part IV's records land before certification, and this Part's PR, which
carries the certification record, merges last); the §5 sequence
readiness record (SEQ1 Dell Plan gate → SEQ1.5 Census → SEQ2 HCN →
SEQ3 Dock → SEQ4 Psalm Matrix → SEQ5 Workspace → SEQ6 Grand
Synchronization) mapped against what Parts I/II actually closed.

## (c) Already done vs. what the Part PR must build

- **Done:** the drive itself runs (row #115 is the standing execution
  run — its PARTIAL status is the honest state of a drive mid-flight);
  the Grand Workflow and Cycle System are adopted and operating.
- **Build:** row #27's handoff hardening remainder (workflow adopted;
  the row closes on standing-practice proof, not another document);
  the GP-E27 rehearsal — all 25 journeys executed at PUBLIC_ENTRY_PATH
  or better against the post-Parts system; row #112's certification
  record. **Row #112 stays BLOCKED until the Director certifies**:
  certification is currently WITHHELD, with DAF-09 (Part III row #21)
  unresolved as a named cause. This Part prepares everything
  certification needs; it cannot grant it.

## (d) Part PR contents — checklist

- [ ] Handoff-hardening proof record (row #27)
- [ ] Merge-queue record for the eight Part PRs (landing receipts)
- [ ] 25-journey rehearsal execution + receipts (GP-E27)
- [ ] §5 sequence readiness record (SEQ1–SEQ6 vs. actual closures)
- [ ] Certification evidence bundle for row #112 (bundle only —
      the certification act is the Director's)
- [ ] Register write riding inside: rows #27, #115, #112 updates as
      the evidence and the Director's act allow
- [ ] §45 package; Director + Keeper confirmations

## (e) Dependencies

- **NEEDS_DIRECTOR:** row #112 — whole-program certification (withheld;
  DAF-09 named). Also the final-check authority for GP-E27.
- **NEEDS_OVERSEER:** none for the builds; Ace receives the
  certification outcome.
- Genuinely depends on Parts I + II closures for the rehearsal's
  subject matter, and on Part IV's records landing before the
  certification bundle is complete (Far Stratum *builds*, in their own
  future turns, depend on this Part's SEQ6 rehearsal closing — the one
  true cross-Part build dependency in the program).

## (f) Parallel / serial split

- **Parallel from hour zero:** handoff proof work, drive records,
  rehearsal harness construction, journey test scaffolding.
- **Genuine dependencies:** the rehearsal *executions* run against the
  merged results of Parts I/II (they rehearse the built system);
  certification follows everything.
- **Serial by law only:** all merges (this Part's record is the merge
  queue itself); the rehearsal's state-sharing legs join the global
  campaign queue.
- **Collisions:** none in product code. This Part writes records and
  the rehearsal harness (new files) only.

## (g) BUILD-READY PACKAGE — Part VII

- **Branch:** `uni/part-7-execution-order`
- **Files to create:** `director-reports/GRAND_SYNCHRONIZATION_REHEARSAL_2026-11-20.md`;
  `director-reports/CERTIFICATION_EVIDENCE_BUNDLE_2026-11-20.md`;
  journey harness suites under `form/` as new `journey_*_test.py`
  files (one per journey family, per Edition 1 file 06).
- **Files to modify:** `director-reports/DIRECTOR_REVIEW_QUEUE.md`
  (handoff record); register JSON (own rows).
- **Test suites:** the 25 journey acceptances at PUBLIC_ENTRY_PATH+;
  the full regression campaign as the rehearsal's final leg.
- **Campaign:** the program-final ×3 campaign — last in the global
  queue by definition.
- **Register flips (targets):** #27 PARTIAL → COMPLETE on standing-
  practice proof; #115 PARTIAL → COMPLETE when the drive's own terms
  close; **#112 stays OPEN/BLOCKED until the Director certifies** —
  its flip is an authority act, not a lane target.
- **Authority asks:** (1) PLAN-CONFIRM — Director + Keeper; (2)
  CODE/RECORDS-CONFIRM at exact head; (3) Director: whole-program
  certification decision on the evidence bundle (row #112), requested
  only when Parts I–VI + IV records have landed and DAF-09's state is
  whatever the Director's own reproduction established.

---
# THE PARALLEL EXECUTION — ALL EIGHT LANES AT ONCE

## Lane table (all start at hour zero)

| Lane | Branch | Rows | Primary territory (exclusive files) | Campaign load |
|---|---|---|---|---|
| Part 0 | `uni/part-0-scoreboard` | 3 | `certification_runner.py`, `form/regress.py`, INDEX | ×3 if `form/` changes |
| Part I | `uni/part-1-architecture` | 70 | `form/persist*.py`, `owner_state_lock.py`, `lifecycle.py`, `grow.py`, `confirm_lineage.py`, `dock_session.py`, `form/duobeta/` | Heaviest — per-cluster ×3 |
| Part II | `uni/part-2-dell-plan` | 41 | `form/repl.py`, translate/condition regions, Nursery door surface | ×3 |
| Part III | `uni/part-3-incompleteness-register` | 4 | verify-72-17 probe, register-adjacent records | Conditional |
| Part IV | `uni/part-4-far-stratum` | 19 | Design records only | None |
| Part V | `uni/part-5-scoreboard-reconciliation` | 3 | `master_list.py`, `NBD_*.md` | Conditional |
| Part VI | `uni/part-6-unknowns` | 2 | Decision packets + Q.8 probe | None |
| Part VII | `uni/part-7-execution-order` | 3 | Rehearsal harness (new files), records | Program-final ×3 |

## The three serial resources (the only queues in the program)

1. **Merges** — §32, main session, one at a time. Landing order:
   0 → V → III → II → I → VI → IV → VII.
2. **State-sharing campaigns** — one at a time globally (or isolated
   state directories per lane where the suite supports it). Campaign
   slots are booked by lanes as their clusters reach proof stage; a
   lane never blocks another lane's *building*, only its campaign slot.
3. **The register JSON** — one file, eight editors: per-lane row
   ownership + landing-time regeneration (header collision plan).

## Collision matrix (every shared file, and its split)

| Shared file / surface | Lanes | Split |
|---|---|---|
| `director-reports/master_work_list_items.json` | All | Own rows only; regenerate + `--check` at landing |
| `form/open.py` | I, II | By function region (I: persistence/save/history/rooms/dock/growth; II: parse/translate/condition/count); cross-region changes via patch notes in the owning lane's PR |
| `form/dell_matrix/core.py` | I, II | II owns Dell contract definitions; I owns state machinery; patch-note protocol |
| `form/regress.py` | 0 (owner), all (users) | Only Part 0 edits it; all lanes run it |
| `director-reports/master_list.py` | V (owner), 0 | Part V owns automation; Part 0's gate work uses it read-only |
| Nursery store modules | I, II | II owns door/ranking surface; I owns `confirm_lineage.py` placement machinery (the GS-4 seam, row #185 vs #140–#143) |
| `director-reports/INDEX.md` | 0, all | Part 0 owns the dedup; other lanes append their rows at landing only |

No other product file is claimed by more than one lane. Collisions
discovered mid-build despite this plan are a map defect: the lane stops,
the split is amended in this document, then work resumes — collisions
are never resolved by racing.

---

# COVERAGE PROOF

**Method:** every row of `master_work_list_items.json` at main
`af2519b6` was machine-checked against this map's assignments
(script-verified, exactly-once): 185 rows total; 40 COMPLETE rows are
closed and excluded by rule; the remaining **145 rows each appear in
exactly one Part table above** — 84 OPEN + 55 PARTIAL + 3 GATED +
3 SANDBOXED = 145. Per-Part counts: **Part 0: 3 · Part I: 70 ·
Part II: 41 · Part III: 4 · Part IV: 19 · Part V: 3 · Part VI: 2 ·
Part VII: 3.** Edition 1 circuits: all 28 (GP-E01..GP-E28) assigned
exactly once (Part I: 13, Part II: 11, Part 0: 1, Part III: 1,
Part IV: 1, Part VII: 1).

**Rows that could not be placed: none.**

**Judgment-call placements (stated openly):** #116 (DAF-09 report →
Part 0, reporting machinery; its subject defect #21 sits in Part III);
#27 (handoff → Part VII, execution machinery); #112 (certification →
Part VII, the final act); #90/#93/#94 (morning-report/NBD family →
Part V, reconciliation instruments rather than Part 0's gates); #185
(GS-4 defect → Part I, growth/confirm machinery, though its question
family lives in Part VI); #180–#182 (Ace's sandboxed items → Part IV,
the parking stratum; they are not DellMatrix work and no lane works
them); #171 (H track → Part IV with the V rows it shares content with).

**Fold-in inventory check (non-row items from the brief, each placed):**
PR #498 R5 records → already landing (Part I carries R5-D); PR #308 →
Part II (anchor #24); PR #294 C-B prep → Part I (anchor #118);
seven-circuit backlog → #413/#417 Part I, #401/#416/#429/#439/#457
Part II; R23/R24 → Part II (GP-E02/GP-E01); R21 → Part VI (question) +
Part I (#135 remainder); R14 residual → Part I; CH-17 → Part I;
Phase B remainder → R4-A7 Part I, H-4 Part I, INDEX dedup Part 0,
#433 Phase T Part II; FI-017 → Part IV; 30-video P01–P06/P08 → Part I,
P07 → Part IV; Q families → Part VI.

---

# CONFLICTS & AMBIGUITIES — EDITION 1 vs. THE UNIFIED EDITION

1. **Scoreboard basis.** The Unified Part 0 originally presented a
   224-item census as the scoreboard; the canonical basis is the MWL's
   182 (Director's live-scoreboard ruling, reconciled into PR #421's
   head text). Edition 1's blueprint still speaks in its own totals.
   *This map follows the canonical register everywhere.*
2. **Colliding namespaces.** Unified §4 register = GP-G01..28;
   Edition 1 circuits = GP-E01..GP-E28; Unified internal circuits =
   C-H/C-WEB/C-SEQ IDs; register rows = MWL numbers with DD/SM/G/Q
   aliases. No shared key exists; Edition 1's file 01 crosswalk is
   *candidates only*, never adopted. Part V owns making one crosswalk
   canonical.
3. **99 vs. 100 Dells.** Unified Part II is titled "the 99 Dells";
   Edition 1 file 05 is a *100* Dell baseline and register row #114
   says "ALL 100 Dells". The discrepancy stands unresolved in the
   sources — Part II's GP-E07 audit must settle the count as evidence,
   not by choosing a title.
4. **Sequence divergence.** The Unified §5 order (Dell gate → Census →
   HCN → Dock → Psalm Matrix → Workspace → Grand Synchronization) vs.
   Edition 1's phase ordering (file 00 §6), which stages Simulate
   (GP-E14) and Dock (GP-E23) differently relative to the sequence
   steps. This map follows the Unified order for Parts and Edition 1
   for circuit specs; the parallel-lane model makes the divergence
   mostly moot for builds, but Part VII's readiness record must
   reconcile the two explicitly.
5. **Two incompleteness registers that are not the same list.** Only 6
   of Unified GP-G01..28 map to MWL rows (Unified Part V §3a); 22 G
   items have no row and can never move the board, and most MWL 72-rows
   have no G item. Part III carries both truths at once.
6. **Double-filed work.** Register #139 (C4.Distill) and #179 (Distill
   mode, Ace-ruled) overlap; #93 (SM-09) declares itself folded into
   #90 (72-72). Part II and Part V respectively must close each pair
   once, with the duplicate cited — never two completions for one body
   of work.
7. **FI work has no Unified Part.** Edition 1 files FI-010..FI-019
   (file 09); the Unified Edition has no FI Part. FI-017's placement in
   Part IV is a Uni placement decision by stratum logic, not a source
   ruling — flagged for Director confirmation.
8. **GP-E05's priority contradiction.** Edition 1 files R5 in the
   *first* execution wave; its register anchor (#173) is a §14.7 design
   prerequisite and its implementation is HOLD-gated behind two
   authority acts. The parallel model dissolves the scheduling
   conflict (prep proceeds in Part I's lane from hour zero), but the
   *priority* contradiction in the sources stands — flagged for the
   Director.
9. **Certification conditions.** Edition 1 file 00 §7 states
   program-level completion conditions; the Unified Edition adds the
   sitting system (Sitting #002, Mon 2026-11-23, ≥42/≥39) that
   Edition 1 predates. Both are carried: sittings govern weekly truth,
   §7 conditions govern program closure (Part VII).

---

*End of map. The eight build-ready packages above are the launch
surface: on this map's acceptance, eight lanes open the eight branches
and build in parallel under the serial laws named here.*

---

## GOVERNING LAW MIRROR — AGENTS.md §46 + §32 (added 2026-11-20, Director 7044797269)

The Director's Part VII FULL/DEEP disposition (7044797269) found a
provenance gap: all eight Part packages cite AGENTS.md §46, but the
repository's own record did not carry the section. The governing
texts are mirrored here verbatim from the workspace AGENTS.md (Ace
rulings) so the in-repo record carries the law it cites. The mirror
is a copy for provenance; the workspace AGENTS.md remains the
governing source, and any divergence resolves in its favor.

### §46. EIGHT-PART / EIGHT-PR EXECUTION RULE (Ace ruling, restated 2026-11-20)

Ace ordered this before and restated it with finality on 2026-11-20:
the drip of small one-item PRs is over.

1. PLAN WHOLE FIRST. The entire detailed plan exists before execution:
   every remaining object assigned to its Grand Plan Part.
2. EIGHT PRs. Execution runs as one PR per Grand Plan Part —
   0 Scoreboard, I Architecture, II Dell Plan, III Incompleteness
   Register, IV Far Stratum, V Scoreboard Reconciliation, VI Unknowns,
   VII Execution Order — each PR carrying a WHOLE SECTION of the plan,
   built and proven as one body of work.
3. NO NEW SMALL PRs. A standalone little circuit PR is a defect under
   this rule. Work that arises mid-flight folds into its Part's PR;
   it does not spawn its own PR. Records landings already built and
   stamp-ready when this rule was restated finish as records.
4. NO UNBOUNDED SWEEP PHASE. The Batch Sweep Law's phase (A) — sweep
   non-Part work first — has NO open-ended run: the non-Part pile is
   frozen at whatever stands when a Part starts; leftovers fold INTO
   their Part. A sweep that never empties is how the Parts starved
   2026-11-17 → 2026-11-20; never again. If the Parts have not started,
   that fact is reported to Ace as a stall, not hidden behind busy
   small-item progress.
5. WITHIN A PART: plan -> confirm -> code -> confirm (Batch Sweep Law
   section C), campaigns still serial and one at a time, merges still
   section 32 main-session acts. The Part PR is the unit of delivery;
   the register write rides inside the Part PR.
6. WHOLE, IN PARALLEL — NOT ONE TASK (Ace, 2026-11-20 08:49 CST):
   anything that presents as "just one thing" is re-analyzed into the
   whole it belongs to before work starts. The 8 Parts are planned as
   ONE body and built in PARALLEL lanes simultaneously — not one Part
   at a time. Serial only where a safety law names it (merges,
   state-sharing campaigns, shared mutable state); everything else —
   planning, building, testing in isolated state — goes at once.
   Correct whole-planning up front is what makes parallel execution
   safe; collisions between lanes are planned away in the map, never
   discovered mid-build.

### §32. PRE-MERGE FRESHNESS GATE (Ace ruling, 2026-11-05) — operative form

Before merging ANY PR: (1) check for Director review newer than the
recorded watermark; (2) fold in every new ruling first; (3) if a new
ruling carries HOLD, INSUFFICIENT_EVIDENCE, CORRECTION_REQUIRED, or
any disposition other than an explicit confirmation FOR THAT PR,
STOP — do not merge that PR; (4) only then apply the hard CI gate
and merge. The gate is a freshness check, not a permission change:
no merge may outrun an unread ruling about its own PR. Operative
amendment (Workflow v2, PR #461, in force 2026-11-18; AGENTS.md
§44): the freshness check runs on the GitHub record; email is
exception-only transport and the mail digest is retained as rollback
only. Merges are main-session acts, one at a time, on terminal
evidence at the exact final head.
