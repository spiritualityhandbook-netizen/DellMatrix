# PART III — THE INCOMPLETENESS REGISTER: DETAILED PLAN (2026-11-20)

**Program:** DellMatrix Eight-Part Program (AGENTS.md §46; Ace ruling
2026-11-20, GO-BIG amendment 08:54 CST — maximum content buildable under
current authorizations; nothing skeletal).
**Part:** III — The Incompleteness Register (GP-G01..GP-G28).
**Stage:** PLAN (plan → confirm → code → confirm). This PR is the plan
stage. It also carries, built NOW because they are records products that
need no authority gate: the complete disposition ledger
(`GP_G_REGISTER_DISPOSITIONS_2026-11-20.md`) and the extension-register
framework (`EXTENSION_REGISTER_FRAMEWORK_2026-11-20.md`).
**Branch:** `uni/part-3-incompleteness-register`.
**Base:** main `af2519b6d239ef278397e277210d6da2467c36e5`.
**Scope:** MWL rows #21, #120, #172, #174 (all OPEN) + Edition 1 circuit
GP-E06 + disposition entries for each of GP-G01..GP-G28.
**Production code in this PR:** NONE. Code-stage items (#120 probe
profile, #174 wording) are carried as exact, bounded proposals in §3–§4
below and execute only after PLAN-CONFIRM, per the stage law.
**Register JSON:** NOT edited in this PR. Flips are PROPOSED in §7 and
ride inside this Part's PR at the code/records-confirm stage, per-row,
per the map's collision plan.

---

## 1. What this Part is

The defect register itself. Two registers of incompleteness exist and
they barely overlap:

- the **Unified Edition §4 register**: GP-G01..GP-G28 (28 known
  incompletenesses, filed 2026-11-13/14), and
- the **Master Work List**: 185 rows, of which only **6** carry the same
  work as a G-item (topical mapping, Unified Part V §3a).

The other **22 G-items have no MWL row** — they exist only in the §4
register, are invisible to the scoreboard, and would silently fall out
of the program if the MWL were treated as the whole truth. The
disposition ledger (deliverable 2) is therefore this Part's core
product: every G-item, with evidence of its current state, a proposed
disposition, and the authority that decides it.

**Numbering-collision warning (standing):** the MWL's own source IDs
also use "G-" numbers for a *different* register (e.g. MWL row #15's
source ID "G-04" is not GP-G04). All mappings in this Part are TOPICAL
(same defect/work), never by ID. This collision is itself an instance
of the disease GP-G23 names.

**Stale-base caveat (U-A1):** the §4 register's code-anchored claims
rest on the read-only inventory at clone HEAD `05859c0` (2026-11-04).
They are FACT for 2026-11-04 and UNPROVEN for current main until
re-measured (Census X11, sequence step 1.5). Every ledger entry states
which side of that line its evidence sits on.

**Closing condition this Part serves (Grand Plan §4, as reworded under
SD-GP-01):** the Grand Synchronization rehearsal may not be declared
until every operative item GP-G01..GP-G28 is COMPLETE,
OWNED-AND-CLOSED in its own lane, or RETIRED WITH A RECEIPT in the
register. This Part's ledger is the instrument that makes that
condition checkable.

---

## 2. Row #21 — DAF-09 session-escape (72-03 / SM-02) — OPEN, BLOCKED by law

**Register text (verbatim, current main):** "Independently reproduce
DAF-09 session-escape cleanup (= SM-02; register BLOCKED — Director's
independent 19/22 stands; local greens do not resolve it, §31.3)".

**State of the evidence:**
- DAF-09 = the session-escape discrepancy: cleanup behaviour observed
  to differ between the Director's independent reproduction (19/22)
  and local runs (green). §31.3 / §31 law: DAF-09 is NEVER resolved on
  local evidence. Uni-side greens are necessary evidence, never
  sufficient.
- Whole-program certification is currently WITHHELD with DAF-09 as a
  named blocker; Part 0 row #116 (the owed DAF-09 catch-up Director
  report) quotes this row's evidence state, and Part VII row #112
  (certification) is gated on it. A wrong move here propagates to
  three Parts; the only lawful move is completeness of the evidence
  chain.

**Plan (this Part's code stage):**
1. Re-run the DAF-09 evidence suites at the Part's exact head for
   evidence only — `form/daf09_timeout_tree_test.py` and the
   session-escape reproduction chain — with logs preserved under the
   Part's evidence directory; results recorded as UNI-REPORTED
   evidence, explicitly NOT a resolution.
2. Update the evidence chain record: every reproduction attempt to
   date, its environment, its result, and the exact delta between the
   Director's 19/22 and local results, so the Director's independent
   act starts from a complete file.
3. **No flip proposed.** Row #21 stays OPEN until the Director's
   independent reproduction/verification lands. Its target at this
   Part's confirm is *evidence completeness*, not closure.

**Deciding authority:** Director (independent reproduction — the
standing owed act). Keeper: trailing verification of the evidence
chain's completeness.

---

## 3. Row #120 — verify-72-17 reproducer hygiene (72-67 follow-up) — OPEN

**Register text (verbatim):** "Historical verify-72-17 reproducer
hygiene: give the stale pre-repair probe an explicit/manual historical
purpose, keeping the current repair regression active (queued hygiene
circuit from the 72-67 closure)".

**Evidence (current main, verified in this lane's clone):**
- The stale pre-repair probes are the two GitHub workflows
  `.github/workflows/verify-72-17.yml` and
  `.github/workflows/verify-72-17-exact-head.yml` — exact-head
  certification vehicles for the 72-17 Render-directive repair
  (director-reports/DIRECTOR_REPORT_72_17_RENDER_DIRECTIVE_REPAIR.md;
  DIRECTOR_REPORT_72_17_SHOW_SENTINEL.md; evidence under
  `director-reports/evidence/72-17-show-sentinel/`).
- They still present as live verification machinery although the
  repair they certified is long landed; a reader cannot tell they are
  historical. (Part II's #308 work covers verify-72-06 — a different
  probe; no collision.)

**Proposal (code stage, exact and bounded — NOT executed in this PR):**
1. Both workflows: triggers reduced to `workflow_dispatch` only
   (explicit/manual), workflow `name:` prefixed `HISTORICAL —`, and a
   header comment added stating: the repair certified, the PR/record
   that landed it, and that the current repair regression is the
   in-tree suite set (the 72-17 suites under `form/`), not these
   workflows.
2. No job steps change; no workflow is deleted (the historical
   certification record stays runnable by hand).
3. Proof at code stage: workflow YAML parses; the in-tree 72-17
   regression suites run green at exact head; exact-head CI on the
   Part PR.

**Flip proposed (on confirm):** #120 OPEN → COMPLETE.
**Deciding authority:** Director + Keeper (CODE/RECORDS-CONFIRM at
exact head).

---

## 4. Row #174 — Guard/Catch wording hygiene (C1 hygiene, §14.7) — OPEN

**Register text (verbatim):** "Guard/Catch wording hygiene — a
separate bounded hygiene opportunity (preserved contract; not a
silent behavior change)".

**Subject:** Dell 92 Guard and Dell 94 Catch — the verdict pair
(ACE_FUTURE_DEVELOPMENT_PLAN §12.82: Guard asks "may this PROCEED?";
Catch consumes what Guard/Try leave active). Their user-facing
wording has accreted across registry text, Dell cards, and message
strings; the hygiene aligns the *wording* while preserving the
contract exactly.

**Site census (this lane, current main — the bounded site list):**
- Registry text: `form/mandell/core_ii.py:48` (Dell 92 Guard entry:
  "Prevent execution unless conditions hold", aliases "Guard Unless
  OnlyIf").
- Dell card text: `form/mandell/dell_cards.py:775` (Dell 92 deep note).
- User-facing messages: the Guard verdict strings (e.g. "Guard ALLOW
  default", "Guard BLOCK block" — as pinned by
  `form/mandell/d1_registry_spectrum_test.py:273-285`).
- Contract suites that pin behaviour: `form/dd45_chain_parse_refusal_test.py`,
  `form/guard_assert_propagation_test.py`,
  `form/dirf14_catch_consumed_test.py`,
  `form/mandell/d1_registry_spectrum_test.py`.

**Contract (binding on the code stage):**
1. Wording only. No semantic token, refusal code, verdict, default,
   or side effect changes. Any diff that alters a pinned behaviour
   string's *meaning* is out of scope and stops the item.
2. Exact wording diffs are presented in the code-stage PR body before
   application; nothing lands on a summary description.
3. Proof: the four contract suites above green at exact head, run
   before and after, with the tally contract honoured (each suite's
   own final tally line last). If any product code changes, the ×3
   campaign rule applies and the campaign joins the global serial
   queue — it does not run inside this Part's lane concurrently.

**Flip proposed (on confirm):** #174 OPEN → COMPLETE.
**Deciding authority:** Director + Keeper (CODE-CONFIRM at exact
head). If the confirmed wording touches any Ace-sovereign surface
text, that line is carved out and parked NEEDS_OVERSEER rather than
forced.

---

## 5. Row #172 — Beyond-72 extension register framework (F1/F4) — OPEN

**Register text (verbatim):** "Beyond-72 extension register framework
(Director F1/F4): new extension objectives get distinct IDs checked
against the current register, mapping to existing rows WITHOUT
renumbering the original 72; no duplicate closure credit".

**Delivered in this PR:** `EXTENSION_REGISTER_FRAMEWORK_2026-11-20.md`
— the framework itself, complete: ID assignment rules, the two-register
collision check, the no-renumbering law, the no-duplicate-credit law,
and the 22 no-row G-items worked as its first exhibits.

**Flip proposed (on confirm):** #172 OPEN → COMPLETE (the framework is
the deliverable; its *use* is standing discipline thereafter).
**Deciding authority:** Director (framework is a Director F1/F4
instrument) + Keeper confirm.

---

## 6. GP-E06 — remaining limits waves R28–R42 (Edition 1 circuit)

**Circuit text (Edition 1, 02_EXECUTION_CIRCUITS.md):** "The merged
R2–R26 matrix is NOT the end of the 42-row census. Reconcile Waves 6–8
current main before any new implementation credit… For each:
independent fresh-main source+public-path probe, classify ALREADY_FIXED
/ FAITHFUL_GUARD / UNRULED_VALUE / LIVE_DEFECT / DORMANT /
EVIDENCE_GAP, and create no code PR for a disproven defect."

**Already done:** waves 1–8 verification records landed (PR #484,
#449); the R2–R26 reconciliation matrix is merged. What remains is the
*wave-completion record for R28–R42 at current main* — several wave
verdicts predate later repairs and have never been re-probed against
af2519b6.

**Plan (code stage):** for each row below, a fresh-main
source+public-path probe in an isolated clone, the classification, and
the receipt. Confirmed LIVE_DEFECTs do NOT get built in this Part:
each is filed as a patch note to its home Part (per the map's
collision plan) and recorded in the completion record as carried-open
with its home named. This Part creates no code PR for a disproven
defect and no code PR at all for GP-E06.

| Row | Subject (per Edition 1) | Wave-era note carried into the probe |
|---|---|---|
| R28 | forces/grow insertion-ordered partial vision | prove fair/complete work or truthful continuation; first-N must not permanently monopolize a growth pass |
| R29 | create field caps | validate against public paths; wave 6 withdrew the earlier strength sub-claim |
| R30 | checkpoint current+previous | documented GUARD; do not increase retention blindly |
| R31 | coordinator audit 500 eviction, no dropped counter | counted loss / explicit archival policy or fail-closed |
| R32 | Studio JS second 400-edge cut beneath payload 480 | show drawn/shown/total or remove the silent second slice without stalling rendering |
| R33 | growth fog 72 | both live callers already below 72 in wave 7; do not "repair" an unreachable defect without new proof |
| R34 | BIMO committed config silent retirement | fix all producer/commit/restore sites in ONE persistence circuit (home Part files the build); preserve legacy configs |
| R35 | scrub_context 2000 | no active caller in wave 7; classify DORMANT rather than live leakage unless re-proven |
| R36 | context-node 1000, inconsistent char budget | choose compatible units, refuse explicitly; no false 5x capacity claim |
| R37 | validated 11-slot BIMO 1287-char framing cut to 1200 | emit whole valid configuration or refuse wearing it; never partial persona |
| R38 | Bridge result to_dict text 8000 | preserve or explicitly mark incomplete; no dependent action on cropped-as-complete |
| R39 | Claude output cap 2048, dropped stop_reason | provider contract must propagate truncation/completion status; caller-configurable within safe bounds |
| R40 | research windows 24, words 400 | no production caller at wave pass; potential/unsupported, not a live Nursery starvation claim |
| R41 | lattice shape {12,14} | guarded/test-pinned; keep unless separately ruled |
| R42 | all_entities Nursery ghosts 12 | disclose coverage + continuation with current ownership; do not fabricate missing live nodes |

**Deliverable at code stage:** `LIMITS_WAVES_R28_R42_COMPLETION_2026-11-20.md`
(probe receipts + classification per row) riding in this Part's PR,
plus patch notes filed for any confirmed LIVE_DEFECT.
**Deciding authority:** Director + Keeper (RECORDS-CONFIRM of the
completion record; per-defect build credit is decided in the home
Parts, never here).

---

## 7. Proposed register flips (NOT applied in this PR)

Applied at the code/records-confirm stage, per-row surgical edits,
only on the authorities' confirm:

| Row | From → To | Basis |
|---|---|---|
| #120 | OPEN → COMPLETE | §3 proposal executed + proof |
| #172 | OPEN → COMPLETE | §5 framework (delivered in this PR) confirmed |
| #174 | OPEN → COMPLETE | §4 wording hygiene executed under its contract + suites |
| #21 | OPEN → OPEN (no flip) | evidence chain completed; closure awaits the Director's independent DAF-09 act |

GP-G ledger closures (COMPLETE / OWNED-AND-CLOSED / RETIRED WITH
RECEIPT) take effect as register-record entries in the ledger document
itself on PLAN-CONFIRM; they move no MWL numbers (22 of the items have
no row to flip) and claim no duplicate credit for the 6 mapped items —
their credit lives in their home rows.

---

## 8. Dependencies, collisions, serial constraints

- **NEEDS_DIRECTOR:** row #21 — DAF-09 independent reproduction (also
  gates Part 0 #116 and Part VII #112). GP-G25 Tree leg — admission
  ruling after Keeper THL-SM-02 reproduction. GP-G22 — R-B repair
  authorization. GP-G04 — the Q-Frc1 fork (label vs persist).
- **NEEDS_KEEPER:** THL-SM-02 independent reproduction (GP-G25 Tree).
- **No Ace decision outstanding** for this Part's own rows. (GP-G27's
  LM-7 authorization is an Ace/Director item tracked in the ledger;
  it does not gate this Part's PR.)
- **Collisions:** none with product-code lanes in the plan stage.
  Register JSON at landing: rows #21/#120/#172/#174 only. The
  verify-72-17 probe files are Part III exclusive.
- **Serial by law:** this Part's merge (§32); a ×3 campaign only if
  §4's hygiene ends up touching product code — then it joins the
  global queue.
- **Ledger snapshot rule:** the ledger's dispositions read Parts I/II
  row states at af2519b6; at this Part's landing they are re-snapshotted
  against the then-current main and any drift is recorded, not silently
  absorbed.

## 9. Limitations

- §4 evidence base is stale (U-A1): ledger entries that rest on the
  05859c0 inventory are marked as such; Census X11 re-measurement may
  move individual G-item states, and the ledger carries a standing
  amendment slot for census receipts rather than pretending finality.
- GP-G19's DISCONNECTED entry list is not enumerated in any source
  (U-A5); the ledger records the class and the owed enumeration, not
  an invented list.
- GP-G15's registry contract is unopened in every source (U-A3); the
  ledger records UNKNOWN, per the register's own verdict.
- DAF-09: this plan deliberately produces evidence, not a verdict.
