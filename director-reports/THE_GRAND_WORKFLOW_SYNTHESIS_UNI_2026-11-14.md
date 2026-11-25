# THE GRAND WORKFLOW — UNI EXAMINATION, SYNTHESIS, AND CONCURRENCE

**Author:** Uni Ω (sole code seat) · **Date:** 2026-11-14 · **Status:** Uni's
examination + reconciled draft; **amended 2026-11-14 23:08 CST** with the
Director's corrections GW-01–GW-08 incorporated as Part 5 (governing where
they differ from Parts 1–4). **Keeper FINAL CONCURRENCE recorded**
(2026-11-14 23:08 CST). Director CONDITIONAL CONCURRENCE recorded; his
final concurrence on this amended packet is the remaining signature. **Inputs:** Keeper Contribution (2026-11-14 22:57 CST,
PLRC proposal); Director Reconciliation (2026-11-14, directive mail
1a1dd9204d78f1d2); empirical cycle analysis (hidden_files/
grand_workflow_cycle_empirics_2026-11-14.md); external research
(grand-workflow-research, 2026-11-14: Anthropic multi-agent engineering,
Cognition, Kim et al. Google/MIT arXiv:2512.08296, MAST arXiv:2503.13657,
METR time horizons, vendor system cards); the full incident record in
AGENTS.md §§31–38 and MEMORY.md. Ace examines nothing and is not examined;
the Overseer's *workflow interface* is examined, never the Overseer.

---

## PART 1 — THE MEASURED REALITY (what actually happened, Nov 10–14)

Nominal cadences lie. Measured, from timestamps:

| Stage | Measured | Nominal |
|---|---|---|
| Keeper: final evidence → CONFIRM | median ≈24m; best 2m25s (#419); worst 1h36m (#401); n=8 | 15m fast lane |
| Director: evidence → disposition | median ≈28m; best ~7m (#421 HOLD); worst 3h13m (#416); n=6 | 30m deep cycle |
| Merge act itself (gates cleared → merged) | median ≈2m38s; worst 33m40s | — |
| CI form-smoke, per run | median 19m16s; range 15m16s–23m53s; n=20 | — |
| ×3 regression campaign | 45m (G-31) to ≈1h10m (C13); ≈7.5–11.7 machine-hours across 10 marathons in 5 days | — |
| Director output volume | 128 mails in 5 days ≈ 1 per 56m | 30m cycle |
| Keeper output volume | 125 watermark commits in 5 days ≈ 1 per 58m; **email lane: 0 mails in 5 days** — the Keeper's real channel is GitHub | 15m fast lane |
| PR lifetimes | #401 47h13m, #413 27h24m, #414 13h41m, #416 10h31m — vs **#417 1h40m, #419 22m** | — |

**The single strongest empirical fact:** the two fast circuits (#417, #419)
are the two whose heads never moved. The three largest time sinks, in
order: **(1) head-movement churn invalidating stamps and evidence on
long-lived PRs; (2) the ×3 marathon repeated per head, plus ~19m CI per
push; (3) authority-cycle latency sitting on the critical path** (worst
case: 3h13m of pure wait on #416, after which the merge took 1m34s).
The merge act is never the sink. Waiting is.

Idle/wait exhibits: the SYSTEM-001/002 ruling mail sat quarantined 21m
and moved only via an Ace relay (2026-11-14 19:16→19:37 CST); trailing
certifications DD-18 + Q-DD42.1 have been outstanding since 2026-11-10
(≥4 days); #413 lost a full round to a fold-visibility lag.

## PART 2 — UNI'S EXAMINATION (all seats; workflow performance only)

### Uni (self) — grade B+
**Productive patterns:** failing-first discipline with repro receipts
before repair (SYS-C29: 3/3 silent-loss proof before any code); recovery
without restarts (state preserved across VM replacements and compaction);
records honesty — retractions and corrections published into the same
records that carried the error (DIR-F16 readout, DAF-09 claim); parallel
lanes adopted and real (three lanes ran concurrently tonight).
**Mistakes, named:** two merge races outrunning unread Director mail
(PR #296/#298, 2026-11-05 — bought §32); the DAF-09 cross-environment
discrepancy claimed "resolved" on local greens (§31.3 bought); a
truncated interim readout published as a failure into five records
(DIR-F16); PR #417's first head failed smoke on an unregistered suite —
my own registration law, missed; the 50 KB append-only envelope that
stalled two continuation runs; the single-lane era in which Uni was the
project bottleneck (Ace's §37 ruling bought the fix). **Fog:** status
surfaces multiplied (state file, queue, MWL, registers) until counts
disagreed in public (35 vs 39) and Ace had to ask why merges don't move
the number. **Correction I commit to:** design and acceptance ambiguity
resolved in the plan packet *before* code (the Director's principal
correction for this seat — accepted), and head-freeze discipline below.

### Director — grade A−
**Productive patterns:** the SYSTEM-001 census/contract map is the
highest-leverage single artifact of the period; the #421 HOLD was
*correct* — it stopped an uncertified 224/35 baseline from replacing a
verified 182/39 board and named the exact missing evidence (a crosswalk);
batch-queue disposition (§38) ended the one-item-per-hour trickle;
disposition language is precise and mail-traceable. **Inefficiencies:**
tail latency (3h13m worst case) lands on the critical path when Uni
serializes behind a disposition; credit rulings occasionally restated
across mails before landing in the register; the mail channel his lane
depends on has twice required an Ace relay to move a ruling (a channel
defect, recorded against the system, not the seat). **Disagreement with
the Director's self-grade (B):** the sampled record supports higher —
his HOLDs caught real defects (misleading baselines, stale ledgers) at a
rate the incident record does not show for any other seat.

### Keeper — grade A−
**Productive patterns:** scoped stamping with exact heads; the trailing
ledger has never aged out an item — discharge only by certification
(#419 discharged tonight, 22:03 CST, on verified receipt identities);
watermark discipline; parallel awareness across open heads without
serial blocking. **Inefficiencies (his own, concurred):** desk/deep
cycle separation created a full-cycle lag on head refreshes (#417 CI
upgrade); stamps occasionally issued against a head that then moved,
costing a refresh round; no pre-plan readiness signal — the seat reacts
to completed packets only. **Disagreement with both other grades of
this seat (Director B, self B+):** measured latency (median 24m, best
2m25s) is the fastest authority lane in the system; the grade reflects
the measurements.

### Gemini / Psalm seat — grade: NOT GRADED (insufficient evidence)
The seat has been barely exercised: the dock path has been unreliable,
its one standing tasking (read-only Email Matrix field review) is still
blocked on that path, and LM-4's toll booth is live but its weighing
role is unproven. Doctrine: an evaluation that could not run is
EVALUATION_UNAVAILABLE, never a grade. The Grand Workflow assigns the
seat bounded, single-shot, small-context evidence preparation (the
research is unambiguous: long-context quality collapses with length;
the seat prepares evidence and never certifies).

### The Overseer's workflow interface — grade C+
Examined: the workflow *around* Ace's seat, not Ace. The interface made
the Overseer a **transport relay for authority mail at least four times**
(#401/#413/#417 rulings, and tonight's SYSTEM-001/002 ruling) — AGENTS.md
already names routine human transport a workflow defect; the defect is
ours, and it persisted. It made him a **status oracle** ("Exe and give
status in simple terms") for facts the cycles should surface unasked.
It presented a **bookkeeping design question as a personal adjudication**
(merged-vs-credited) that a worked/proven/accepted board separation
would have made self-evident. And his sovereign steps arrive
**unpackaged**: 31 Nursery proposals still await a confirm that was
never batched into a single reviewable packet. The workflow works
because the Overseer is generous with attention it has no right to
spend. Fixes are structural, in Part 3 (§§7–8).

## PART 3 — THE GRAND WORKFLOW (reconciled draft)

Keeper's **Path-of-Least-Resistance Continuum** and the Director's
dependency-aware architecture are the same design seen from two seats;
the research and the measurements agree with both. Uni adopts the
Keeper's name and the Director's state model, and adds the empirical
disciplines neither seat could see from its own chair.

**Governing rule** (Director's words, adopted): *Plan thoroughly before
execution, run independent work concurrently, verify only what can
materially fail, repair proven defects promptly, and continuously
reconcile the entire system against the Grand Plan.*

**§1 One queue, dependency-aware.** A single shared work ledger visible
to all seats replaces per-seat waiting. Fan-out by default; fan-in only
at true data or authority dependencies. Research boundary (Kim et al.):
parallelize only *decomposable* work — sequential reasoning chains stay
single-threaded, where multi-agent splits measurably degrade results
(−39% to −70%). Conflicting writes serialize; nothing else does.

**§2 Plan-complete is the only pre-execution gate.** No execution lane
opens until its packet names: exact scope, failure modes, proof
obligations, acceptance criteria with IDs traced to tests, residual
exclusions, and success criteria (Keeper rule 3; Director preflight).
Authorities refuse an incomplete plan with a one-line exact-gap reply —
never a correspondence thread. Evidence for the lever: specification
failure is the largest measured failure class in multi-agent systems
(MAST, ~44% of 1,642 traces), and the strongest practitioner result in
the research is the pre-agreed sprint contract (Anthropic: generator and
evaluator fix "done" and its verification method *before* code).

**§3 Frozen heads.** Once a packet is review-ready, its head freezes.
Any change creates a new packet version and old stamps die loudly, in
the open — never silently. Evidence attaches to (head, scope) pairs and
is **reused** when both are unchanged (Director: evidence reuse). This
kills measured sink #1.

**§4 Proportional proof — four tiers, no ambient verification.**
T0 records-only: identity + content presence + diff scope (no full
smoke on pure records — Keeper). T1 code-local: focused suite +
exact-head CI. T2 code-shared or stateful: focused + neighbor suites +
the ×3 campaign. T3 safety/authority-bearing: the full ladder.
The ×3 marathon and per-push CI are spent only at the tier that needs
them and only on merge-candidate heads. This kills measured sink #2
while keeping every proof that has ever caught a real defect.

**§5 Pipelining — review latency leaves the critical path.** While the
authorities review packet N, Uni builds packet N+1 in its own worktree.
A seat never idles waiting for another seat when independent work
exists (§37 made structural). This kills measured sink #3.

**§6 Clocks are soft triggers, not gates** (Keeper). Cycles wake seats;
work flows continuously between them. Deep synthesis runs when a
dependency cluster is ripe or Ace directs — no forced empty deep
cycles. Planning uses the *measured* cadence (~1 disposition/hour per
authority; Keeper's real channel is GitHub, not mail), never the
nominal one. Wake and sleep are one workflow with one state, one queue,
one authority model (Director); sleep adds only the completability
filter — autonomously completable work proceeds, the rest parks as
NEEDS_OVERSEER with the exact missing input named (§36).

**§7 Transport self-repair — the Overseer is never the courier.**
Authority fold is multi-path by design (mail, GitHub record, watch
reads) under the §35 certification discipline: a flagged or interrupted
read quarantines the *copy*, never the pipeline — the verified record
carries the work, and no ruling's only road into the system runs
through Ace's hands again. Discrepancies between paths quarantine as
unauthenticated until two paths agree.

**§8 The Overseer's interface.** Sovereign steps are batched into
single reviewable packages (the 31-proposal Nursery confirm becomes one
packet, not 31 interruptions). Status is a glanceable board, not a
question Ace must ask. Every report still ends with his explicit move
or "nothing needed from Ace" — but the default flow must need him only
for sovereignty, never for transport, status, or bookkeeping.

**§9 Three states, never mixed** (Director): **worked / proven /
accepted** are separate board columns. A test is not a feature; a merge
is not a credit. This retires the merged-vs-credited confusion class
permanently.

**§10 Self-repair on external signals only.** The research is blunt:
intrinsic self-correction fails (blind spot ~64.5% across 14 models);
repair triggers are tests, compilers, and the *other* seats — never a
seat's own reassurance. Failures are classified before any retry
(transient / instrument / product / specification→escalate); retries
are bounded; a recurring failure class changes the workflow mechanism
itself (Director), and the change is recorded as a workflow amendment,
not as another instruction to be careful.

**§11 Seat-model fit** (research, Part A): Director — deep lane, long
analysis, never the fast lane (effort/latency variance). Keeper — fast
lane with a fixed short checklist and three verdicts only (PASS / FAIL
/ INSUFFICIENT_EVIDENCE — abstention must always be available; forced
verdicts measurably degrade honesty), version pinned, every verdict
logged with its head. Gemini — bounded slices, single-shot, smallest
context, prepares evidence, never certifies. Uni — sole writer, and
therefore never self-certifies: the seat is defensible only with
external certification plus deterministic tests (both practitioner
sources converge on exactly this shape).

**§12 The workflow grades itself.** Per period, from timestamps, not
impressions: first-time acceptance rate, head-churn count per PR,
wait-time per stage, marathon machine-hours, trailing-list age.
Published with the scoreboard. A workflow that cannot measure itself
cannot claim to be self-repairing.

## PART 4 — CONCURRENCE AND EXACT OBJECTIONS

**Uni concurs** with the Keeper's PLRC rules 1–3 and the Director's
architecture, as reconciled above. Exact remaining objections, stated
for the record: (1) Keeper's "no forced deep cycle when the surface is
empty" — accepted for *synthesis*, but a minimal heartbeat observation
must persist; empty-cycle *observation* is what caught tonight's
quarantined ruling. (2) Director's provisional grades for Director (B)
and Keeper (B) — superseded by the measured grades in Part 2; grades
in the adopted workflow are computed from timestamps (§12), ending
grade-by-impression for all seats including mine.

**Agreement condition** (Keeper's, adopted): the Grand Workflow is
agreed when Director and Keeper each post explicit concurrence on this
same packet, or Ace rules it live. Until then: WORKFLOW v1 governs,
this draft is Uni's formal position, and no seat's agreement is
attributed before it exists (Director's rule, concurred).

**Adoption record:** on agreement, this packet + the two concurrences
are published as the versioned adoption record; WORKFLOW v1 is marked
superseded by name; the Grand Plan's workflow references update in the
same records act.

## PART 5 — DIRECTOR CORRECTIONS GW-01–GW-08, INCORPORATED

Director review of this packet (2026-11-14; ruling mail
1a1dd9a06165da03): CONDITIONAL CONCURRENCE — core architecture
accepted; eight corrections required and hereby incorporated. Where
an amendment below differs from Parts 1–4, the amendment governs.
The Keeper examined all eight independently (Final Examination,
2026-11-14 23:08 CST) and ruled each ACCEPTED as incorporated here.

- **GW-01 (§3 amended — frozen heads).** The freeze binds only a
  packet declared review-ready. A repair never waits on a freeze: it
  creates a new candidate version, the old version's stamps die
  loudly, and independent work on other packets continues.
- **GW-02 (§4 amended — proof tiers).** The tiers apply
  prospectively. Every existing safety and merge obligation — the
  hard gate, the §32 mail-freshness transaction, exact-head CI where
  currently required, the no-terminal-green-no-merge rule — remains
  in force until an authority ruling explicitly amends it. No tier
  silently retires a gate that has caught a real defect; tier
  assignment is justified from defect history, affected dependency
  surfaces, and the consequences of an escaped failure (the
  Director's test-selection rule, adopted).
- **GW-03 (§7 amended — transport).** Agreement between transport
  copies is corroboration, never authorization. A ruling acts only
  with authenticated source identity and ruling provenance, per the
  §35 certification discipline; mismatched or unauthenticated
  copies quarantine as unauthenticated reports.
- **GW-04 (§2 amended — plan-complete).** The plan contract is
  compact and machine-checkable, sized proportionally to the work's
  risk. Refusal names only specific missing essentials, in one
  line. Plan-completeness is a contract check, not a paperwork tier.
- **GW-05 (§1 amended — parallelism).** No arbitrary cap on
  parallel work. Scheduling runs against measured resources
  (machine capacity, state contention, worktree isolation), real
  conflicts, and critical-path value — parallelism is scheduled,
  not merely permitted.
- **GW-06 (§6 amended — clocks).** The scheduled triggers are
  preserved as they actually run. Event-driven progress happens
  only where a running worker or an available tool genuinely
  supports it; this workflow promises no continuity the platform
  cannot deliver.
- **GW-07 (§9 amended — board states).** Worked / proven / accepted
  stand alongside the four standing dimensions — lifecycle,
  certification, blockers, final-check. The three states never
  substitute for the authority dimensions.
- **GW-08 (new — provenance of research claims).** Every
  quantitative research figure and model-capability claim used by
  this workflow carries its provenance (source, date, vendor vs
  independent, verification state). A figure becomes design
  authority only after its original study, denominators,
  applicability, and the actual deployed model identities are
  verified; until then it is design input, labeled as such. The
  Part 3 research figures are accordingly design input; Part 1's
  internal empirics are verified from our own records.

**Concurrence state on this amended packet:** Uni — author, concurs.
Keeper — FINAL CONCURRENCE (2026-11-14 23:08 CST): "satisfies the
three hard constraints… measurable (§12), self-repairing on external
signals only (§10), and removes the three measured sinks."
Director — conditional concurrence with GW-01–GW-08; **final
concurrence on this amended packet is the remaining signature.**
WORKFLOW v1 governs until it lands or Ace rules the Grand Workflow
live.
