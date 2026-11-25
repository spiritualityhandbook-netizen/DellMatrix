# STEP 13 PACKET — Gate 0 reconciliation + pairwise re-derivation at the repaired freeze

Circuit: Director order step 13 (Director section 8.13; Director
Q3 ruling, register: step 13 = FULL 9,900-pair re-derivation at
the repaired freeze with a diff against the historical ledger).
Mode: Trinity process, Director asleep — implemented+verified
only; nothing certified; report held SUBMITTED for his return.

## 1. Repaired freeze (verified 2026-11-01, this run, via gh + git)

- Frozen head: **c94e2237ed9e52da02593e7c79a6d787cf9a21ff**
  (PR #205 merge, Step 11 Director report publication).
- Frozen tree: **dc306f059164559bdf881bde2a47cb7987591ff5**
  (merge tree == candidate tree a74a6e4's tree, verified).
- Code identity note: the delta 195fafa -> c94e223 is
  director-reports/ only (verified by git diff --stat: report
  file + INDEX). The repaired CODE head is therefore 195fafa
  (Step 11 implementation merge; tree fc87d85); c94e223 is the
  frozen presentation head. Regress at freeze: 220 entries.
- Worktree: ~/workspace/nbd-omega-step13, branch
  uni/step13-rederive, at c94e223, clean at creation.
- All repair closures land before this freeze (per Director
  handoff): steps 2-11, 3b/3c, 5b, DAF-09 pidfd hardening,
  DIR-F12/F13/F14/F15 — all merged before the freeze.

## 2. Gate 0 reconciliation (step 13, first half)

FACTS (program record, no invention):
- Gate 0 froze baseline 11933da (tree 45d31ce) on 2026-10-30
  (GATE_0_FREEZE.md): census sha256 26295687…, registry
  composite 541c03e4…, held-out seed 17759033593353963452.
  Gate 0 verdict PASS WITH FLAGS (AF-1..AF-6 flagged, not
  pre-fixed, per Ace's 2026-10-30 ruling).
- Gate 2 ran the full sweep at that baseline (189.1 s summed;
  totals raw: FUNCTIONAL 2049, FUNCTIONAL_INDEPENDENT 6592,
  INTENDED_CLASH 1163, UNIQUE_CANDIDATE 95, DEFECT 1 raw).
- Gate 3 re-derivation (classifier v3, R3+R4 overlay,
  gate2_rederived.json, 92 pair changes + identity 87 fix)
  produced the corrected totals frozen in ledger v1
  (GATE_4_LEDGER_SCHEMA_V1.md): FUNCTIONAL 2047,
  FUNCTIONAL_INDEPENDENT 6682, INTENDED_CLASH 1163,
  UNIQUE_CANDIDATE 8, DEFECT 0; identity 91/9/0.
  Ledger v1 sha256 43fe6967…, baseline label PRE_AF.
- Report #2 said Gate 0 was closed; PR #162 (Gate 4 chunk 2,
  merged b352e39) later contained ledger canaries / the
  symbiosis ledger regress suite — LATER work under the
  symbiosis program's own authority (Ace's approved
  SYMBIOSIS_PAIRWISE_MASTER_PLAN execution order,
  2026-10-29 ~22:10 CDT), NOT a Gate 0 re-opening and NOT
  unauthorized work. The historical record is stated as-is:
  Gate 0 stayed closed; the canaries belong to Gate 4
  chunk 2's regress-integration scope.
- AF-1..AF-6 were repaired AFTER the Gate 0/2 baseline
  (PRs #157-#161), and steps 2-11 + DIR-F wave repaired the
  Director's B/DAF contracts after that. Ledger v1 is
  therefore explicitly HISTORICAL PRE_AF evidence: its rows
  describe 11933da behavior, not current behavior. That is
  exactly why this step re-derives at the repaired freeze
  instead of certifying from v1.
- The held-out partition seed and Gate 3D law register are
  historical artifacts of the PRE_AF lineage; step 13 does
  NOT re-run the law prediction test (no new law claim) —
  it re-derives pair classifications and diffs them.

## 3. SWAT Director's-eye pre-mortem (BEFORE sweep execution)

Recorded 2026-11-01, this run. Director's-eye attacks and
the method answers:

- P1 "You reused the stale Gate 0 census as B-alone baseline,
  so half your diffs are baseline skew (the B=86 artifact
  all over again)." -> Census is RECOMPUTED at the frozen
  head with the unmodified gate0_census.py apparatus
  (GATE0_ROOT=step13 worktree, GATE0_OUT=step13 census);
  the sweep's pilot copy loads ONLY that new census.
  Historical census file is never touched.
- P2 "You edited the classifier mid-sweep to make new
  refusals come out INTENDED_CLASH." -> Classifier is the
  historical v2/v3 sweep code VERBATIM for the raw run.
  New designed refusals created by the repair circuits
  (e.g. step 10 ungroup_missing:*, step 6/DIR-F13 Loop
  count refusals, step 9 Diff baseline errors) will surface
  raw as NOT_POSSIBLE / A_FAILED / SEAM_FAILURE where the
  old prefix table lacks them; each such row class is then
  dispositioned in a separate v4 OVERLAY re-derivation
  (before-values asserted, like R3/R4) with the repair
  packet cited per prefix. Raw ledger is never rewritten.
- P3 "A static hash + 26 canaries is not 9,900 pairs." ->
  Full sweep: 100 blocks, 9,900 ordered pairs + 100 identity
  rows, same battery v0.1 invocations (pilot INV with the
  86 erratum and 41 canary scrubbing), public entry path
  execute_seed only, oracles = full-state snapshot diffs +
  store delta + selected-in-plane check (beyond ok=True).
- P4 "Repairs changed standalone behavior; your pair diff
  will blame pairs for solo changes." -> The diff report
  separates (a) standalone census changes 11933da -> freeze
  (per-Dell ok/error/writes/sensitive_to), (b) pair class
  changes attributable to a changed standalone baseline,
  (c) residual pair-only changes. No class change is
  reported without its attribution bucket.
- P5 "Sweep owner state contaminated the run." -> Isolated
  synthetic owner Gate2Sweep (harness's own), cleanup()
  before/after; bystander discipline from Gate 1/2 retained
  in the harness; canary strings hash-only in ledgers
  (scrub() unchanged); zero residue verified after run.
- P6 "Cron-launched sweep died and you called partial
  blocks a result." -> Sweep is block-resumable and writes
  per-block ledgers under hidden_files/step13_harness/;
  a missing block is NO RESULT for that block, never a
  pass; the sweep step is run foreground or from the main
  session per TOOLS.md, and block files + counts are
  verified before any total is claimed.

SWAT unanimity (implementation method, not a truth gate —
DIR-WF-001 amendment; dissent would be recorded):
- CUSTODIAN: census recomputed at freeze, historical files
  immutable, overlay before-assertions required. AGREE.
- INTERPRETER: raw-then-overlay preserves representation
  honesty; attribution buckets (a)/(b)/(c) required. AGREE.
- SENTINEL: isolated owner, canary scrubbing unchanged,
  no destructive probe against real state. AGREE.
- MECHANIC: block-resumable, per-block ledgers durable
  under hidden_files (not /tmp), totals recomputed from
  raw rows only. AGREE.
Unanimity 4/4 on the METHOD above, recorded before any
step 13 execution.

## 4. Execution plan (closure discipline)

1. Census at freeze (gate0_census.py verbatim) ->
   hidden_files/step13_harness/gate0_census_main.json
   (step13 copy dir; historical census untouched) +
   standalone diff vs historical census.
2. Harness copies (gate0/gate1/gate2 verbatim except:
   pilot CENSUS path resolves inside the copy dir, which
   holds the NEW census; sweep OUTDIR = copy dir's
   sweep13/) -> raw sweep 100 blocks + identity.
3. Aggregation recomputed from raw rows; totals + diff
   vs ledger v1 (per-pair class changes, attribution).
4. v4 overlay re-derivation for new designed prefixes
   (before-asserted), if raw rows require it; totals
   re-verified after overlay.
5. Ledger v2 freeze (new file, schema v1 rules:
   gate4_ledger_v1.json never edited) + symbiosis ledger
   regress suite expectations reviewed — if the repo
   suite pins v1 totals as CURRENT truth, that is a
   finding to fix in this circuit (v1 stays historical;
   suite must pin v1 as historical + v2 as current).
6. Packet closure + Director report
   DIRECTOR_REPORT_STEP13_REDERIVATION.md (Anticipated
   probes + Questions) published to director-reports/.
   Step 13 is evidence/re-derivation, not a code circuit
   unless step 5 surfaces a repo defect; any code change
   then follows the full per-circuit discipline
   (failing-first, mutants, regress x3, PR, separate-step
   CI, merge tree equality, fresh-clone).

## 5. Status

- 2026-11-01 17:30 CST run: Step 11 publication closed
  (PR #205 merged c94e223, tree equality verified);
  freeze established; this packet + pre-mortem recorded.
  NEXT: census at freeze.

## 6. Closure addendum (2026-11-01, this run)

FREEZE: c94e223 (tree dc306f0); code head 195fafa.

CENSUS AT FREEZE: gate0_census.py verbatim, GATE0_ROOT=
step13 worktree; new census sha256 c2288818… (historical
26295687…). Standalone diff vs 11933da: **3/100 rows** —
13 Loop sensitive_to narrowed [store, groups, scope no
longer outcome-changing]; 16 Decay ok->False 'enhance OFF'
(Step 6 B1 honest EnhanceGate refusal); 83 Ungroup
ok->False 'ungroup_missing:squad' (Step 10 named-missing
refusal). All three are repaired-contract effects.

RAW SWEEP (classifier verbatim, census = new): 100 blocks
+ identity, 193 s, exit 0; files
hidden_files/step13_harness/sweep/ (101). Raw totals:
FI 6287, F 1992, IC 1163, A_FAILED 184, NOT_POSSIBLE 181,
UNIQUE 93, DEFECT 0, SEAM_FAILURE 0. Identity raw:
89 IDEMPOTENT / 9 HONEST_REFUSAL / 2 FAILURE (16, 83).
Canary check: no G0CANARY string raw in any sweep file.
Zero owner residue after run; worktree clean.

OVERLAY (step13_rederive.py; before-asserted; raw never
edited): 454 pair changes — R5/R6 designed-prefix
(ungroup_missing / 'enhance OFF' -> INTENDED_CLASH) 365;
R86/41 baseline correction (census 86 row was
delete_missing:probe under the pre-erratum invocation;
corrected standalone ok=True; B=86/B=42 rows re-run) 89.
Identity overlay: 2 (16->16, 83->83 -> HONEST_REFUSAL).
FINAL TOTALS: FUNCTIONAL 1989, FUNCTIONAL_INDEPENDENT
6375, INTENDED_CLASH 1528, UNIQUE_CANDIDATE 8,
DEFECT 0, SEAM_FAILURE 0, NOT_POSSIBLE 0, A_FAILED 0.
Identity final: 89 IDEMPOTENT / 11 HONEST_REFUSAL /
0 FAILURE. The 8 UNIQUE rows are EXACTLY the historical
Gate 3 genuine residue (07/22/29/38->51, 85/86/87->42,
93->95).

DIFF VS LEDGER V1: 369 pair class changes — 365 FI/F ->
INTENDED_CLASH (the 16/83 honest refusals composing),
3 F->FI + 1 FI->F residuals, all explained:
55->13 and 82->13 (F->FI) follow Dell 13's narrowed
sensitivity (store/groups perturbations no longer change
Loop's outcome — Step 6/DIR-F13 count-grammar lineage);
93->55 (FI->F) is Step 8's tx channel: Set inside a Try
frame now writes core_ii.tx (B writes store+tx vs store
alone historically); store effect identical (probe
added), both ok, no corruption — a genuine composition
change with a named mechanism, not a defect.
Identity diffs vs v1: exactly 16->16 and 83->83
(IDEMPOTENT -> HONEST_REFUSAL, the same refusals).

LEDGER V2: hidden_files/gate4_ledger_v2.json,
ledger_sha256 de5354f0… (same canonical-hash method as
v1; verified after write). V1 file untouched (schema
versioning rules honored).

REPO SUITE REVIEW: form/mandell/symbiosis_ledger_test.py
pins v1 as FROZEN HISTORICAL identity (docstring: PRE_AF,
pins drift of the RECORD; full re-derivation expressly a
Gate/milestone event not claimed by the per-PR suite).
It does NOT present v1 as current truth, so no repo code
change is required by step 13; regress at the freeze
already carries it green (220/220 at 195fafa, code
identical at c94e223). A v2 pin update is a possible
small follow-on circuit — raised as Q1 in the Director
report, NOT silently done.

STATUS: Step 13 IMPLEMENTED-VERIFIED (evidence circuit;
no product code changed). NOT certified. Director
report DIRECTOR_REPORT_STEP13_REDERIVATION.md follows;
step 14 (admission INDEX packet) is next.
