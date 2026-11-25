# STEP 13 GROUND — Gate 0 reconciliation + FULL pairwise re-derivation at the repaired freeze

Prepared 2026-11-01 by proactivity research (grounding only; no code
changed, no sweep run). Base at preparation: main f24f7b4 (PR #199
merge, DIR-F14 report publication). DIR-F15 is in flight in the
continuation cycle (failing-first 20/24 with exactly W1-W4 failing;
suite-fixed 24/24; regress legs 1-3 logging 218/218 GREEN at
preparation time — the cycle owns F15's closure and report; this
grounding does not touch it).

Queue position: step 13 runs AFTER DIR-F15 + step 10 (B11/B12/B18)
+ step 11 (public-contract wording) all close, at the resulting
repaired freeze. It is the last evidence circuit before step 14
(the admission packet: ONE packet, an INDEX over the per-circuit
Director reports, requesting A1/A2/typed/full-registry re-rulings)
and step 15 (Ace's elementary report). Ground files already exist
for DIR-F13, DIR-F14, DIR-F15, step 10 and step 11; none existed
for step 13 before this one (checked: no step13* files anywhere
in the goal hidden_files or workspace root).

Register contract (DIRECTOR_FINDINGS_REGISTER.md, Execution
order + DIR-WF-001 answers): "Step 13: reconcile Gate 0 record,
re-run/rederive pairwise at the new frozen head after repairs."
Director Q3 answer (settled, not open): "step 13 = FULL
9,900-pair re-derivation at the repaired freeze with a diff
against the historical ledger." A sampled or partial re-run
does NOT satisfy Q3.

## What step 13 is — and is not

IS: (1) a Gate 0 record reconciliation at the new head;
(2) a complete fresh execution of all 9,900 ordered pairs +
100 identity rows at ONE frozen repaired HEAD, under the same
battery/world/classifier discipline that makes the result
comparable to the frozen v1 ledger; (3) a row-by-row diff
against that v1 ledger with every class change explained.
IS NOT: a repair circuit (a DEFECT row found here opens its
own bounded circuit; step 13 does not fix in place and keep
sweeping — see Stop rule below); not a re-mining of Gate 3D
laws (see Laws); not a rewrite of any frozen artifact.

## Inputs — frozen artifacts (verify hashes, never edit)

- Gate 0 freeze record: ~/workspace/GATE_0_FREEZE.md.
  Baseline commit 11933da, tree 45d31ce, regress 198/198 x3.
  Registry composite 541c03e419b975dcb... (sha256 of the JSON
  map of per-file sha256 for registry.py, DELL_PROOF_CARDS.md,
  signatures.py). Census gate0_census.json sha256
  2629568746c30a157...; world W fingerprint
  39f502c4a3aa7c18408552be54fc21bcc3ead0041c07885d5a9ecb66d1546c36
  (9-seed recipe in the census JSON `world` field).
  Held-out partition seed 17759033593353963452 (commitment
  sha256 b83a4be2870bb3ab...) — frozen; any change re-opens
  Gate 0.
- Historical ledger (the diff target):
  hidden_files/gate4_ledger_v1.json, schema symbiosis-ledger/1.0,
  ledger_sha256 43fe6967ecb980ceccb... (per
  GATE_4_LEDGER_SCHEMA_V1.md). Totals: FUNCTIONAL 2,047;
  FUNCTIONAL_INDEPENDENT 6,682; INTENDED_CLASH 1,163;
  UNIQUE_CANDIDATE 8; DEFECT 0. Identity (corrected):
  91 IDEMPOTENT / 9 HONEST_REFUSAL / 0 FAILURE (raw 91/8/1
  preserved in the header; the 1 raw FAILURE is the 87->87
  R4 overlay, see Classifier traps).
- Harness: hidden_files/gate2_sweep.py (classifier v2 core +
  v3 with the gate2_rederive.py R3/R4 overlay), gate1_pilot.py
  (INV invocation table), gate0_census.py (world/snapshot/
  channels). Evidence label: PUBLIC_ENTRY_PATH (execute_seed).
- Gate 3D law register: ~/workspace/GATE_3D_LAW_REGISTER_V1.md
  — 16 laws, cleared the pre-registered bar in two consecutive
  held-out rounds (R1 0.997, R2 0.985) ON THE PRE-REPAIR ROWS.

## Gate 0 reconciliation — concrete checklist

The register's phrase is "reconcile Gate 0 record". Read as:
prove the frozen record still describes what it claims, and
record how the new freeze relates to it. Deliverables:
1. Re-hash every Gate 0 artifact named in GATE_0_FREEZE.md
   (census, harness, the three registry files AT 11933da in a
   detached checkout — not at the new head) and confirm the
   recorded sha256 values match. A mismatch is a finding,
   not an edit: the freeze record is historical evidence.
2. Recompute the registry composite AT THE NEW FREEZE HEAD
   and record it as the step 13 baseline identity, alongside
   (never instead of) the Gate 0 composite.
3. Confirm the world W recipe from the census JSON rebuilds
   a world whose snapshot fingerprint is still
   39f502c4... at the new head BEFORE any pair runs. If the
   fingerprint moved, the battery/world changed under the
   repairs (e.g. a Dell in the 9-seed recipe changed
   behavior) — STOP and classify that first; a sweep run on
   a different world produces a diff that cannot be read.
4. State the freeze HEAD precisely: full SHA + tree, the
   regress count/green state at that HEAD, and whether
   report-publication (docs-only) merges are inside or
   outside the freeze. Recommendation: freeze at the main
   HEAD after step 11's implementation merge; docs-only
   report merges after it do not move the code freeze, and
   the ground for step 14 should say so explicitly.

## CRITICAL TRAPS (verified first-hand in the harness code)

1. STALE BLOCK SKIP — gate2_sweep.py is block-resumable:
   "Each block is written as its own ledger file; existing
   block files are skipped". OUTDIR is hidden_files/sweep/,
   which still holds the ORIGINAL Gate 2 block_00..block_99
   JSON files. A naive re-run would skip every block and
   "re-derive" the old ledger without executing anything —
   a false-green re-derivation. The step 13 run MUST use a
   fresh output directory (e.g. hidden_files/step13_sweep/)
   or an explicit OUTDIR override, and the packet must prove
   execution happened (per-block mtimes / secs fields /
   row-level spot re-execution), not merely that 100 block
   files exist.
2. OWNER / PERSISTENT STATE — the sweep uses OWNER
   "Gate2Sweep" and Program() loads persisted state
   (AGENTS.md section 9: a new Program is NOT fresh/empty).
   Gate 0 discipline was a fresh census owner + cleanup
   verified ZERO state-dir residue after runs. Step 13
   needs its own owner name (recommend "Step13Sweep") and
   the same zero-residue verification before and after;
   reusing "Gate2Sweep" risks inheriting residue from the
   Gate 2 era and silently contaminating row outcomes.
3. CLASSIFIER VOCABULARY DRIFT — gate2_sweep.py's
   DESIGNED_PREFIXES table is the Gate 2 era list
   (acceptance_policy_denied, bridge_unavailable,
   embed_unavailable, catch_illegal, commit_without_try,
   replace_occupied, group_missing, ...). The repair wave
   introduced NEW honest-refusal shapes the table has never
   seen: DIR-F13's malformed Loop-count refusal, DIR-F14's
   Catch with nothing pending, step 9's missing-baseline
   Diff refusal, step 10's missing-group Ungroup refusal
   shape and Resolve miss shape, step 6's gated Decay
   refusal surfacing. Any designed refusal missing from the
   table is classified as failure/DEFECT — the sweep would
   report the repairs themselves as defects. Pre-sweep
   deliverable: reconcile DESIGNED_PREFIXES against every
   repair circuit's suite error vocabulary, one witness row
   per added prefix (a pair whose B Dell produces the new
   refusal, shown classified INTENDED_CLASH/honest, not
   DEFECT). Changing the classifier is a HARNESS change:
   record it as classifier v4 with the diff from v3 stated,
   and re-run the v1-era sanity rows to show v4 agrees with
   v3 on rows whose Dells were untouched by repairs.
4. R3/R4 OVERLAYS DO NOT CARRY OVER — gate2_rederive.py's
   corrections were battery errata against the OLD code:
   standalone rows for 86 and 41 recomputed under battery
   v0.1, the 87 identity reclassification (R4: 87->87's
   replace_missing is a designed refusal). At the new head
   86/87 behavior has itself been repaired (steps 4/9).
   Step 13 measures fresh; NO overlay is applied to new
   rows. In the diff, the 92 v1 overlay rows are expected
   to move — they are explained by construction, listed
   separately, not counted as new changes.
5. LONG-CHAIN SURVIVAL — TOOLS.md house law: long chains
   launched from a cron/scheduled session die with the
   session; chains launched as background exec from the
   MAIN session survive. The Gate 2 sweep is exactly that
   class of job. Step 13's sweep + regress legs run from
   the main session, FOREGROUND-or-main-session background,
   with ALL logs under
   hidden_files/step13_logs/ (never only /tmp — VM
   replacement wipes /tmp; TOOLS.md 2026-10-31 rule). The
   continuation cron's job is to VERIFY liveness by log
   growth, never to launch a second concurrent sweep.
6. SINGLE CONCURRENCY — protocol rule from the cycle body:
   never run a second suite/chain/sweep while one is
   progressing. Block-resume (in a NEW output dir) is the
   recovery path after an interruption, with the envelope
   updated before ending any run that leaves it in flight.

## Expected diff — repairs that SHOULD move rows

The v1 ledger is a PRE-REPAIR baseline (Gate 2 totals were
measured before the AF fix program completed its Director-
order successors and before every step 6-11 + DIR-F repair).
A diff of zero would be the suspicious result. Changed rows
must be bucketed in the diff report as:
(a) EXPLAINED-BY-REPAIR — the row's A or B Dell (or the
    shared channel it exercises) was a repair target:
    AF-1..AF-6 seam fixes; step 2 DAF-09 (regress harness,
    may move no pair rows — say so if so); steps 3/3b/3c
    DAF-02 redaction/state; step 4 DAF-01/DAF-07 operand
    transport (85/87/88 rows + Dell 55); step 5/5b Exchange
    durability; step 6 leaf honesty (Decay/Loop/Merge/
    Split/Translate rows); step 7 control verdicts
    (Branch/Join/Any/partial rows); step 8 transactions
    (Try/Catch/Commit/Revert rows); step 9 Diff/Set +
    DIR-F15 membership (89 rows, esp. pairs whose B=89
    follows an A that stores or deletes a None — note the
    standard battery may not seed None values; see Open
    questions); DIR-F12 journal receipt; DIR-F13 Loop
    count grammar (13 rows + Cycle/macro siblings if the
    circuit's failure-class fix landed there); DIR-F14
    Catch consumption (94 rows: any pair running Catch
    twice in one frame); step 10 Resolve/Ungroup/Compose
    (76/83/99 rows); step 11 — WORDING ONLY, mechanism
    unchanged: any row moving under step 11 alone is
    UNEXPLAINED by definition.
(b) EXPLAINED-BY-OVERLAY — the 92 R3/R4 rows + 87 identity.
(c) UNEXPLAINED — everything else. Each unexplained class
    change gets a minimal reproducer (A seed, B seed,
    before/after outcome) before step 14 assembles; an
    unexplained change is a finding, never silently
    absorbed into the new totals.
New totals are reported next to v1 totals, never instead
of them. The 8 v1 UNIQUE_CANDIDATE rows are named
individually in the diff: persists / resolved-by-repair
(which one) / changed-to-what.

## Laws (Gate 3D) — scope fence

The 16 laws were mined and held-out-validated on pre-repair
rows with the frozen partition seed. Q3 settles step 13 as
re-derivation + diff; it does NOT order re-mining. Ground
rule: score the EXISTING laws against the new rows as
evidence (same partition seed, same prediction scripts —
gate3d_predict/score pattern), report hit/miss per law,
and do NOT re-mine or move the bar inside step 13. A law
that fails on repaired rows is an explained-or-unexplained
diff input (a repair may have legitimately changed the
behavior the law described); re-mining, if wanted, is a
separate Director/Ace decision after step 14.

## Stop rule

If the sweep produces DEFECT rows (after the classifier-v4
reconciliation in Trap 3): finish the sweep (the full
matrix is the evidence), classify each DEFECT as
repair-regression vs pre-existing-but-unmeasured vs
harness artifact with a reproducer, and STOP before
step 14. Each real defect opens its own bounded circuit
under the standing closure discipline; step 14's packet
must not be assembled over unexplained DEFECT rows.

## Deliverables (for the step 13 Director report + step 14)

- This ground's Gate 0 reconciliation checklist, executed,
  with hashes and the new registry composite.
- step13 ledger: NEW artifact (recommend
  hidden_files/step13_ledger_v2.json) with its own schema
  freeze note (GATE_4_LEDGER_SCHEMA_V1.md pattern);
  symbiosis-ledger/1.0 is FROZEN for v1 and is not edited.
  Open: does the Gate 4 chunk-2 regress ledger suite
  (39/39 at b352e39, pins v1) get a v2 companion suite or
  stay v1-only as historical evidence? Recommend companion
  — step 14 should not rest on an unintegrated artifact.
- Diff report: totals table (v1 vs v2, pairs + identity),
  bucketed change lists (a)/(b)/(c) above, unique-candidate
  dispositions, law scorecard.
- Director report in the standing shape (ruling/identity/
  exceptions first; Anticipated probes; numbered Questions)
  published to director-reports/ with INDEX row — HELD for
  the Director's return under Trinity-asleep; nothing
  certified.

## Open questions left for SWAT (deliberately undecided)

1. Freeze point: implementation-complete HEAD after step 11
   (recommendation in checklist item 4) vs after step 11's
   report publication merge. Pick one and record it BEFORE
   the sweep starts; moving it mid-sweep invalidates rows.
2. None-valued store states: the standard battery's world W
   and INV invocations may never store a None, in which
   case DIR-F15's repaired membership distinction is
   invisible to the sweep and 89's rows cannot confirm it.
   Is a battery EXTENSION (a None-seeding A Dell row set)
   in step 13 scope, or does F15's own suite remain the
   sole evidence? Recommend: extension as a clearly
   separated supplementary row set, never mixed into the
   9,900 comparable rows — comparability of the main diff
   outranks coverage inside it.
3. Classifier v4: the DESIGNED_PREFIXES reconciliation
   (Trap 3) — SWAT must own the per-prefix witness list;
   this ground names the risk and the method, not the
   final prefix list, which must be built from the repair
   circuits' actual suite vocabularies at freeze time.
4. Identity rows: v1's lens is R1 idempotence (execute
   twice). Repairs to Catch/Compose/Diff make second
   execution newly meaningful (a second Catch now honestly
   finds nothing pending). Are identity rows re-run under
   the identical R1 lens for comparability (recommend:
   yes, identically) with semantic notes appended where a
   class stayed the same for a different reason?
5. Cost: Gate 0 froze a cost FORMULA and no projections.
   Gate 2's per-row `secs` give measured pilot data; the
   circuit may state measured duration after the fact.
   No projected sweep hours are to be promised to Ace
   before the run (Gate 0 section 7 discipline stands).

## What this grounding did NOT do

No sweep, census, or reproducer was executed (a sweep from
this research run would violate the single-concurrency and
main-session-chain rules while DIR-F15 is in flight).
Classifier prefix gaps are identified from the harness
source + repair-circuit contracts, not from executed rows;
the per-prefix witness list is circuit work (Open Q3).
gate3d law scripts were inventoried, not re-run.
