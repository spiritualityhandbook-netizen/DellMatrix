# PART IV — THE FAR STRATUM: DETAILED PLAN (2026-11-20)

**Lane:** Part IV build lane, Eight-Part Program (AGENTS.md §46; Ace
ruling 2026-11-20 — whole program in parallel, 8 PRs; GO-BIG amendment
2026-11-20 08:54 CST: maximum content buildable under current
authorizations, full-depth designs, nothing skeletal).
**Branch:** `uni/part-4-far-stratum`
**Base:** main `af2519b6d239ef278397e277210d6da2467c36e5`
**Stage:** PLAN (plan → confirm → code → confirm). This PR is the plan
stage: design records only. **No production code, no campaigns, no
register JSON edits.** Register flips are PROPOSED below, not made.

## 1. Stratum law (binds every item in this Part)

§7 of the Grand Plan was OPENED by Ace 2026-11-14 ("this will for sure
be implemented") and is adopted at sequence step 7: **the Far Stratum
begins only after the Grand Synchronization (Part VII) closes.**
"Opened" means *in the plan*, not built; the opening dissolved no
gate — every §7 build still passes its own Director/Keeper
certification in its turn, and no §7 item enters the §4 closing
condition or may delay any earlier step. Everything in the stratum is
derived, advisory, or a study until its own circuit says otherwise;
the stratum inherits every firewall in §§1–6.

**The design/build split (applies per item, stated in every package):**

- **DESIGNS PROCEED NOW**, in parallel, at full depth — this PR.
- **BUILDS WAIT** on Part VII's Grand Synchronization closing, plus
  each item's own authorization (and Ace's act where flagged
  NEEDS_OVERSEER). No build is proposed in this PR for any V/FAR item.

## 2. Contents of this PR

| File | Contents |
|---|---|
| `director-reports/PART_IV_PLAN_2026-11-20.md` | This plan: every assigned row + GP-E28, splits, verification, asks |
| `director-reports/FAR_STRATUM_DESIGN_PACKAGES_2026-11-20.md` | Full-depth design packages: the Reader, FAR-1..FAR-20, G-29/G-30/G-31, COMBO-9 note, P07 deferral record |
| `director-reports/VISION_SURFACE_PLAN_2026-11-20.md` | Full-depth design packages: V-01..V-13 (rows #99–#111), the H track (#171) consolidated, #176 parked-research filing |
| `director-reports/FI017_DEVELOPMENT_2026-11-20.md` | FI-017 full development paper (the Part's one build-class deliverable — paper only) |

## 3. Row-by-row plan (19 register rows + GP-E28)

Design/build split key: **D-NOW** = design proceeds in this PR;
**B-VII** = build waits on Part VII Grand Synchronization + own
authorization; **PARKED** = no work proposed (Ace's act only).

| MWL # | Item | Status | Current state (evidence) | This PR (design) | Build gate |
|---|---|---|---|---|---|
| 99 | V-01 Nursery proposal CARDS | OPEN | Register: DEFERRED, not authorized. No card surface exists; Nursery work runs through text doors (C5R.2 SEE / C5R.4 lens, Part II territory) | Full card design package: data model, action parity with existing doors, glanceability rules (VISION §1) | B-VII + Ace unpark |
| 100 | V-02 Custom idea shapes | OPEN | DEFERRED; depends V-01. No shape metadata exists | Shape vocabulary as view-only metadata package (VISION §2) | B-VII + Ace; after V-01 design |
| 101 | V-03 AI-suggested looks | OPEN | DEFERRED; depends V-01. Suggestions-as-proposals only, per register | Proposals-only suggestion pipeline design (VISION §3) | B-VII + Ace; after V-01 design |
| 102 | V-04 Nursery as THE primary decision screen | OPEN | DEFERRED. Nursery is a store + doors today, not the primary screen | Decision-first information-architecture package (VISION §4) | B-VII + Ace; acceptance only via #110 gates |
| 103 | V-05 SKY perspective | OPEN | DEFERRED. No 2D spatial perspective exists | SKY view spec: persistent positions as view state, canonical-data parity with ROOM (VISION §5) | B-VII + Ace |
| 104 | V-06 ROOM perspective | OPEN | DEFERRED. No 3D perspective exists | ROOM view spec: walkable, stackable/openable boxes, anti-stagnation motion design (VISION §6) | B-VII + Ace |
| 105 | V-07 Navigation: zoom + tap-to-glide, recursive exploration | OPEN | DEFERRED; depends G-01, V-05/V-06 | Navigation interaction package incl. ideas-within-ideas recursion (VISION §7) | B-VII + Ace; after V-05/V-06 designs |
| 106 | V-08 Page set (Plane, Nursery, Dells, Dell Playground, Psalm Matrix) | OPEN | DEFERRED; depends V-09 | Five-page set + context-preserving transition spec (VISION §8) | B-VII + Ace; **V-09 research precedes any V-08 build** |
| 107 | V-09 Navigation placement RESEARCHED before implementation | OPEN | DEFERRED; precedes any V-08 build | Full research protocol designed now: questions, method, rubric, deliverable shape (VISION §9) | Research executes in this Part's design lane before V-08 build authorization is sought |
| 108 | V-10 PSALM MATRIX page | OPEN | DEFERRED; depends SM-47 fact base. Sequence step 4 (C-SEQ4) is its main-line ancestor | AI-page package: Psalms + personas + status + docking, reads-only over existing authorities, no second authority (VISION §10) | B-VII + Ace |
| 109 | V-11 AI-talk place (pure English, NOT a chat box) | OPEN | DEFERRED; "a new interaction concept to invent" — no concept exists | Invention brief at full depth: constraints, candidate concept directions, evaluation criteria (VISION §11) | B-VII + Ace; concept selection is a Director/Ace act |
| 110 | V-12 Human-validation gates | OPEN | Register: BLOCKED — awaits V-circuits + live dock + Ace's own session | Validation-gate protocol designed now: gate (a) live docked AI, gate (b) Ace personally working the Matrix; evidence format (VISION §12) | Gate (b) is Ace's personal act — NEEDS_OVERSEER by construction |
| 111 | V-13 Reserved neural research (weight-space programming) | OPEN | DEFERRED (long-term); **NO IMPLEMENTATION AUTHORIZED** | Reserved-research charter only: what a future authorization request must contain. No design of the research itself, no prototype (VISION §13) | Ace authorization, none sought here |
| 117 | Exchange Phase G (cloud perspectives) | OPEN | Register: **DECLINED** (deferred by adoption, Ace 2026-10-26); historical record, not reactivated | Carried as DECLINED with history intact (FAR packages §G-10 note). No design work proposed | None — reactivation would be Ace's act |
| 171 | H track — Human Surface track | OPEN | Register: cross-cutting, separately authorized, no UI build started | Consolidated surface plan cross-filed with the V rows it shares + H-only items (identity page, AGE surfacing, animated face Dell 05, Show) (VISION §14) | B-VII + Ace (separately authorized per register) |
| 176 | Literal wave-field instrument | OPEN | INNOVATE_DEFERRED, parked (§14.9); fences: read-only + nonauthoritative if ever built; never feeds resonance scores, Nursery admission, vote weights, or threshold decisions; any semantic path is an Ace-owned architecture decision | Parked-research filing at full depth: the display-only SKY rendering option + fences verbatim + revisit condition (VISION §15) | Ace architecture decision only |
| 180 | NVIDIA Inception website | SANDBOXED | SANDBOXED by Ace 2026-11-10: real-life side mission, NOT DellMatrix work; parked indefinitely, help on his request only | **Disposition: remain parked. No work proposed.** Listed for coverage completeness | Ace's request only |
| 181 | NVIDIA Inception incorporation | SANDBOXED | SANDBOXED by Ace 2026-11-10: real-life side mission, NOT DellMatrix work; parked indefinitely | **Disposition: remain parked. No work proposed** | Ace's request only |
| 182 | Live-model demo step 6 | SANDBOXED | Parked by Ace 2026-11-10 until he is at a computer; he will run the timed trials himself; no scheduling | **Disposition: remain parked. No work proposed** | Ace runs it himself |

**Edition 1 circuit GP-E28** — Far Stratum as future independent units
(D/E class; no product code until phase gate). GP-E28's spec (Edition 1
file 02) is carried as this Part's circuit frame: the Reader reads only
observed recorded streams, never claimed private inner thoughts;
FAR-1..20, G-29, the Nerve χ / Estimator / Conservation / Entropy /
Sounding Field use typed units, uncertainty, witness, and falsifier;
the earlier ideal χ result is not a real irregular-world model; the
Estimator starts with a deterministic, explicitly incomplete
least-squares baseline only after data and appropriate projection
admission, with Kalman/Bayes as alternate experimental candidates,
never secret product defaults; no fourth-floor Tree, geometry-based
causal assertion, code promotion, or sonification in core execution
before the Grand Synchronization and each own gate. Every design
package in this PR is written to GP-E28's discipline: typed unit,
uncertainty stated, witness named, falsifier stated.

**Non-row fold-ins:**

- **FI-017 full development** — `FI017_DEVELOPMENT_2026-11-20.md`.
  **Placement flag (stated openly): FI-017's placement in Part IV is a
  Uni placement decision by stratum logic, not a source ruling** (the
  Unified Edition has no FI Part; Edition 1 files FI-010..FI-019 in its
  file 09). It is presented here **flagged for Director confirmation**
  (Ask 2). The paper is this Part's one build-class deliverable —
  paper only, per its intake fences.
- **30-video P07** (model editing / hyperchaotic control) — DEFERRED
  by the Director, all lanes; retained only as negative examples
  inside P03/P04 (Part I). Part IV carries the deferral record (FAR
  packages §P07). No design work proposed; revisit only on Director
  un-deferral.
- **FAR-1..20 / Reader / G-29..31 design records** — refreshed against
  current main `af2519b6` in the FAR packages file (the Unified §7
  refinement was written against main `d59649a8`; every status claim
  re-checked: `spatial_audio.py` and `fourier.py` toeholds still
  present and still callerless in the product; G-31's built scope
  still merged via PR #417; FAR-17 receipt unchanged).

## 4. Failing-first discipline for a design-stage Part

No product code exists in this stage, so failing-first takes its
design-stage form, applied in this PR and binding on the future build
stage:

1. **Design-stage verification (executed for this PR):** mechanical
   cross-reference check — every assigned MWL row (#99–#111, #117,
   #171, #176, #180–#182) and every FAR/Reader/G item appears in the
   design files with a design/build split stated; every design package
   carries the GP-E28 quartet (typed unit, uncertainty, witness,
   falsifier). A package missing any element fails the check and does
   not ship in this PR.
2. **Build-stage failing-first specs (written NOW, per package):**
   each design package names the failing-first test its future build
   must write first — fixture, expected failure at base, pass shape —
   so the build stage inherits its tests from the plan instead of
   inventing them under pressure. These specs are part of what
   PLAN-CONFIRM confirms.

## 5. Campaign terms

**None.** No product code in this Part at plan stage, and the Part's
eventual build stage is design/evidence class under GP-E28 — any
future item whose build touches `form/` joins the global campaign
queue under the serial law at that time, under its own authorization.
CI on this PR (records-only) is the only machine check.

## 6. Register flips — PROPOSED (none made in this PR)

Counting law: plan ≠ code; **no V/FAR row flips to COMPLETE from
design work.** Proposed register treatment, to be executed only at
this PR's landing and only as the authorities confirm:

- Rows #99–#111, #171, #176: status unchanged (OPEN); a row-text note
  recording "design package complete — Part IV PR, 2026-11-20;
  build gated on Part VII + own authorization" may be appended **only
  where Director + Keeper RECORDS-CONFIRM directs it**.
- Row #117: unchanged; DECLINED history intact.
- Rows #180–#182: unchanged (SANDBOXED); no note proposed.
- GP-E28: no register row exists; none is created by this Part.

## 7. Dependencies

- **Part VII (Grand Synchronization)** — builds only, as §1. Designs
  have no dependency on any Part.
- **Part I GP-E23 (Dock)** and **Part II C5 rows** — FI-017's operating
  surfaces when its build turn comes (named in the FI-017 paper).
- **NEEDS_OVERSEER (Ace):** unparking or authorizing any V-row build;
  the H-track build; row #110 gate (b) (Ace personally working the
  Matrix); rows #180–#182 (his side missions / his own demo run);
  row #111 (any authorization at all); row #176 (any semantic path).
- **NEEDS_DIRECTOR:** FI-017 placement confirmation (Ask 2); FAR-6
  Residue Rule adoption as binding design law (future ask, packaged in
  FAR §FAR-6); V-11 concept selection (future).

## 8. Exact authority asks (this PR)

1. **PLAN-CONFIRM — Director + Keeper**, on Part IV as a whole, in the
   one-bundle presentation of the Eight-Part Program: the design
   packages for rows #99–#111/#171/#176, the FAR/Reader/G-29..31
   packages, the FI-017 development paper, and GP-E28's framing —
   including the per-item design/build splits and the build-stage
   failing-first specs.
2. **Director: confirm or correct FI-017's placement in Part IV**
   (Uni placement by stratum logic; not a source ruling).
3. **Keeper: independent source audit of FI-017's intake record**
   (goal-workspace SYSTEM_DECISION_REGISTER row 127) — outstanding
   since Edition 1 (its file 09/10 gate); Uni's source-equivalence
   report stands at PR #486 comment 6980158056.
4. **RECORDS-CONFIRM at exact head** at this PR's landing (§32,
   main-session merge; Part IV lands seventh in the program landing
   order 0 → V → III → II → I → VI → IV → VII).
5. **Future asks, named now, NOT requested in this PR:** per-item
   build authorizations after Part VII closes (each package names its
   own); FAR-6 adoption (Director design-law decision); V-11 concept
   selection; row #110's gates when V-builds complete.

## 9. Limitations

- Design records only: nothing in this PR demonstrates any V/FAR
  capability; readiness grades are quoted from the Unified §7
  refinement and re-checked against current main, never upgraded.
- The Unified §7 source files (sandbox studies) live in the goal
  workspace, not the repo; this PR's packages cite them by name and
  date and quote their operative findings — the full study texts are
  not reproduced.
- FI-017's original intake source is the goal-workspace decision
  register (row 127); its Keeper-side independent audit is still
  outstanding (Ask 3) — the FI-017 paper is written citation-based on
  that row and Edition 1 file 09, and says so on its face.
