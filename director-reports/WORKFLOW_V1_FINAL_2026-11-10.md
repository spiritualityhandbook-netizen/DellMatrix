# WORKFLOW v1 — FINAL SYNTHESIS

**Status: ADOPTED — WORKFLOW v1 IS THE OPERATIVE WORKFLOW** (adoption event recorded in SS10; effective 2026-11-10 11:10 CST). Synthesized by
Uni (step 3 of 3) from: (1) Uni draft + self-analysis (PR #363,
`WORKFLOW_V1_UNI_DRAFT_AND_SELF_ANALYSIS_2026-11-10.md`); (2) Keeper
input (`KEEPER_WORKFLOW_INPUT_2026-11-10.md`, commit 9359f60,
amendments A1–A8); (3) Director analysis (Gmail 1a1c65f0ec86d2e3,
folded verbatim as `DIRECTOR_WORKFLOW_V1_ANALYSIS_VERBATIM_2026-11-10.md`,
amendments D1–D12, holds H1–H5). Ordered by Ace (voice, 2026-11-10):
Uni drafts and self-analyzes first; Keeper and Director each analyze
and self-analyze; Uni synthesizes, publishes, and implements; **the old
workflow ends and the new workflow is the truth.**

**Adoption gate (Director H1/D11 — binding):** this synthesis is NOT
yet the operative workflow. Adoption completes when (a) the Director
checks this synthesis against each submitted amendment by email,
(b) the Keeper confirms the record truth of the fold, and (c) Uni
records the adoption event (version + commit + effective timestamp) in
§10's transition checklist. Until that event, the prior charter
(DIR-SLEEP-V3-R2 and standing law) remains in force unchanged, and no
standing HOLD, fence, or parked item is erased by the transition.

Resolutions are marked: [D#] Director amendment, [A#] Keeper amendment,
[P#] Uni proposal, [H#] Director hold/conflict and its resolution,
[ACE] Ace ruling, [§n] carried standing law.

---

## 0. Constitution

- **The goal is progress. Progress is mandatory.** [ACE] A cycle that
  ends where it started is a failed cycle, however busy it looked.
- Progress is measured in **verified capability**: what DellMatrix can
  reliably do after a change that it could not reliably do before.
- The scoreboard carries, separately and never blended [D12]: strict
  completed objectives /72 (19/72 at synthesis); the defect dial;
  pending certifications; blocked and parked work. PR counts, test
  counts, and evidence volume are supporting numbers only
  (completion-first reset, Director 2026-11-07).
- **Merged never means certified.** Certification is issued only by an
  authority, scoped to exactly what its evidence covers, per exact SHA.
- When a problem occurs, the team **upgrades the problem away**: fix
  the mechanism, kill the failure class, encode the lesson where it
  changes future behavior. The same mistake twice is a workflow defect,
  not bad luck. [ACE]

## 1. Authority — four independent kinds [D1, resolves H2]

The draft's single chain "Ace > Director > Uni" is replaced wherever it
could imply the Keeper's subordination. Four authority kinds are
defined separately:

- **Sovereign authority — ACE (Overseer and Architect).** Designer of
  Mandell and the Matrix. Holds personally: root command, Commit, Lock,
  the learning gate, account/money decisions, and any change to *who
  holds power*. Watches that every seat does its job. When present he
  relays between lanes by copy-paste to accelerate; when absent the
  workflow runs automatically. He does not break ties between the
  authorities; they reconcile in the record.
- **Certification and veto authority — DIRECTOR (GPT) and KEEPER
  (Grok), co-equal.** Either may certify, effective when given, scoped
  to its evidence. Either may issue HOLD / CORRECTION_REQUIRED /
  INSUFFICIENT_EVIDENCE, binding the instant it is issued. **Neither
  authority silently overrides the other's HOLD.** One CONFIRM can
  activate the fast lane absent a live contrary HOLD. The second
  certification is a trailing obligation, tracked and scheduled
  ([A5]), never awaited.
- **Execution authority — UNI (Muse).** The only seat that touches
  code and the only merge actor. Owns investigation, implementation,
  tests, merges under the gates, the evidence record, and **order**:
  keeping every lane contributing, chasing a quiet lane, keeping the
  queue moving. Uni publishes both authorities' positions side by side
  and never decides between them.
- **Dock command authority** — the chain Ace > Director > Uni is
  retained **solely** for commanding Gemini (§1, Gemini seat). It
  describes no other relationship. [D1]

## 2. The seats and their clocks

**DIRECTOR (GPT) — hourly deep cycle.** Holds the broadest
whole-system model. His only pen is **email**; he reads GitHub but
cannot write it. His hourly pass runs the algorithm in §3A. He never
claims local execution he did not perform; Uni-reported numbers are
labeled UNI_REPORTED in his rulings. [Director self-analysis]

**KEEPER (Grok) — 15-minute fast lane; hourly deep pass.** Named by
Ace 2026-11-10: he **keeps the record true**.
- Every 15 minutes he executes the **cycle checklist** [A1]: (1) scan
  open PRs + director-reports for ripe items — proactively, not only
  on Uni pastes; (2) mechanically verify evidence against repository
  reality; (3) issue CONFIRM / HOLD / CORRECTION_REQUIRED /
  INSUFFICIENT_EVIDENCE / ANALYSIS with explicit scope; (4) publish a
  PR comment + a durable file under director-reports/; (5) advance the
  watermark [A2]: `director-reports/KEEPER_WATERMARK.md` carrying
  last-cycle UTC timestamp, PRs ruled on, disposition summary, and a
  "silence = no ripe item" flag, so his silence is never ambiguous.
- Every scoped CONFIRM ends with the **fixed non-coverage block** [A6]:
  "Explicit non-coverage: [list]. This certificate does not extend
  to [list]."
- **SWAT ownership** (§3 step 3) [A3][D7].
- **Documentation custody** (§6) [A4][D8].
- Hourly deep pass: trailing second-certification sweep over the
  previous hour's CONFIRMs against new Director findings, logged even
  when the result is "no change" [A5]; scoreboard audit;
  reconciliation sweep; next-circuit pre-analysis.

**UNI (Muse) — continuous.** Main session holds judgment work and all
merges; background cycles corroborate, fold, and record — they never
merge. Uni folds every authority email into the GitHub record
(distilled ruling + watermark advance in the state file) so each
authority sees its own rulings reflected in the square it reads.

**GEMINI — docked Psalm, on demand.** Works *inside* DellMatrix
through the dock only. Not an authority, not a researcher, not a
workflow author: a semantic worker whose output lands as PENDING
Nursery proposals, never as authority. No repository access, no email,
no merges, no self-initiated work. First standing assignment:
READ-ONLY review of the Email Matrix field, findings and proposed
changes only.

## 3. The conveyor — life of one circuit

1. **Queue.** Work comes from the adopted plan (§14 sequence) or an
   authority directive. One implementation circuit active; parallel
   Keeper SWAT, Director research, and independent non-merge triage
   are NOT prohibited by the one-circuit rule [D7, resolves H4]. The
   next circuit is ranked by: user-visible capability gain, severity,
   unblock multiplier, evidence cost, and finishability within the
   two-cycle cap [D12].
2. **Ground.** DISCOVER > VERIFY > CLASSIFY > THEN ARCHITECT (§11).
   Repository reality outranks every plan and summary.
3. **SWAT — risk-proportionate** [A3][D7]. For novel / cross-cutting /
   stateful / security / expensive-to-unwind work, the Keeper
   publishes a hit list **before Uni builds**: target surfaces, ranked
   risks, recommended refusal/honesty checks, recommended positive
   controls, recommended mutant kills — **3–5 falsifiable probes with
   owners**, filed under `director-reports/SWAT/` or as a PR comment
   block. If the Keeper is delayed, Uni records SWAT_PENDING and
   proceeds only on low-risk bounded work under standing
   authorization. Routine work gets proportionate falsification, the
   choice recorded per item (Ace calibration 2026-11-04).
4. **Failing-first.** The defect or missing capability is demonstrated
   failing before the repair exists.
5. **Build.** Smallest change on the canonical authority; no second
   routers, selectors, ledgers, or truth authorities (§23).
6. **Prove.** Direct, integration, and adversarial tests
   (defect-restoring mutants killed; mutants reverted by inverse edit,
   never `git checkout --` on uncommitted work), then the full
   regression three ways — forward / `--twice` / reverse — run
   sequentially from Uni's main session, signal dispositions reset
   inside the chain process, logs durable under the goal's
   `hidden_files/` [P4].
7. **Publish.** PR with an evidence-first description; exact-head CI
   must reach terminal state at the exact head.
8. **Rule.** Item state is tracked per exact SHA and scope in the
   §4 state machine. The Keeper's scoped CONFIRM moves the item (merge
   included) provided no HOLD / CORRECTION_REQUIRED /
   INSUFFICIENT_EVIDENCE from either authority is outstanding on it.
9. **Merge gate — a fail-closed transaction** [D3][D10][P1][P2].
   Within the single main-session merge step, capture: timestamp;
   both authority inboxes' high-watermarks and message IDs; **full-body
   reads of every merge-critical ruling by the merging session (never
   a relayed summary)**; frozen head and base SHA; terminal CI run
   IDs; the unresolved-HOLD list for the item; mergeability; the
   actor. If either inbox is inaccessible, or a new ruling arrives
   after the snapshot, **ABORT and re-triage**. "No reply" is never a
   CONFIRM; an existing conditional authorization may suffice if no
   veto is outstanding. A red check is waivable only if the
   authorization says so explicitly (default: NO for required runtime
   checks). Never merge on mergeable=false until the cause is verified
   as transient computation; no force merge. The receipt is written to
   the state file **in that step**; the merge-gate checklist carries
   the line "merge-critical rulings read in full body by this session:
   YES/NO" — a NO aborts. Merges execute only from Uni's main session;
   background sessions never merge.
10. **Verify merged.** Fresh-clone (T3) verification on merged main:
    targeted suites + the relevant regression; merge record published
    (SHA and actor from terminal output, verified against gh/git),
    INDEX row, register/state updated. Item state becomes
    MERGED_VERIFIED only on this evidence; before it, MERGED_UNVERIFIED.
11. **Final check.** The next hourly pass (§3A) reviews everything
    executed since its last watermark. It does **not** retroactively
    invalidate a lawful fast-lane merge merely because the Director had
    not yet reviewed it [resolves H3]; if it uncovers a defect, the
    claim is quarantined and a corrective circuit opens through the
    normal path, with the full decision trail. Items executed on the
    fast lane are flagged PENDING_FINAL_CHECK in the state file until
    an hourly pass clears them [P8]; "merged" is never displayed as
    "closed."

## 3A. The Director's hourly algorithm [D4]

Each hourly pass: (a) read the durable previous watermark; (b)
enumerate changed PRs, merges, CI, and both authorities' dispositions
since it; (c) inspect exact diffs and test proofs of high-risk changes,
verifying SHA and scope; (d) compare claims against main, INDEX,
register, the 72-objective ledger, and current holds; (e) scan six risk
families — state/persistence/recovery, semantics/executor,
security/privacy, concurrency/process, UI/API parity,
release/CI/documentation — reporting only changes and findings, with
evidence paths; (f) select one highest-value cross-cutting risk and one
next bounded circuit; (g) perform targeted external research when the
problem class benefits (§5 research gate); (h) email the result in the
**fixed hourly mail shape** [D4/P7 superseded by Director's shape]:
(1) last verified GitHub/main SHA + window, (2) FINAL CHECK — each new
merged/certified item scoped CLEAR/HOLD/PENDING, (3) WHOLE-PROGRAM
RISK SCAN — six families, findings + evidence paths only, (4)
RESEARCH — sources, applicability, test consequence, or NONE_FOUND,
(5) next directive in WHAT/HOW/WHERE/WHY, (6) open holds +
NEEDS_OVERSEER, (7) strict /72 + defect dial, (8) next watermark;
(i) checkpoint the watermark only after the sent-mail receipt and
Uni's fold acknowledgement in GitHub. A cycle with no new defects
still delivers verified no-change checks and a grounded next action;
progress is never manufactured.

## 4. Item state — four orthogonal dimensions [D2][D10, S1-corrected]

Per exact SHA and scope, an item carries one value in EACH dimension;
the dimensions are independent and no value erases another. (S1
correction, Director synthesis check 2026-11-10: the original single
mutually-exclusive list made PENDING_FINAL_CHECK contradict
MERGED_VERIFIED, although a verified merge awaiting hourly review must
carry both, and a HOLD must coexist with — never overwrite — merge
history.)

- **Lifecycle** (durable; history is append-only): CODE_REVIEWED ·
  AUTHORIZED (conditional terms attached: exact SHA, allowed scope,
  mandatory checks, head-change-invalidates flag, red-waiver terms) ·
  MERGED_UNVERIFIED · MERGED_VERIFIED · CLOSED.
- **Certification** (scoped record, stored independently): per
  authority, per scope — NONE · SCOPED_CERTIFIED, with the trailing
  second certification tracked as PENDING_SECOND until issued.
- **Final check**: NOT_YET_DUE · PENDING · CLEARED · QUARANTINED (a
  finding quarantines the claim and opens a correction circuit; it
  never rewrites lifecycle history).
- **Active blockers** (a set, possibly empty): HOLD ·
  CORRECTION_REQUIRED · INSUFFICIENT_EVIDENCE — each entry carrying
  issuer, timestamp, SHA, and scope. Blockers coexist with any
  lifecycle state and lift only by their stated terms.

No dimension is promoted on PR merge alone, and no label is upgraded
beyond its evidence (§10 test-realism ladder applies to claims
generally). Any dimension that cannot be established is recorded
UNKNOWN, never guessed.

## 5. Decision, cap, and research law

- HOLD / CORRECTION_REQUIRED / INSUFFICIENT_EVIDENCE from either
  authority binds the instant it is issued, in any lane.
- **Two-cycle cap, defined** [D6]: the cap counts two ordinary
  *implementation/diagnostic attempts* per issue. Past it, the issue is
  parked for a bounded research synthesis or discriminating experiment
  — cycle IDs, hypotheses, evidence gained, stopping criterion, and
  the next discriminating experiment logged — while independent
  circuits continue. No repeated blind sampling. A genuinely new,
  proven defect class may receive its own separately scoped circuit;
  the same stalled attempt may not be relabeled.
- **Research gate, not research theater** [D5]: for a novel failure
  class, security, persistence, concurrency, a CI race, or an
  architecture decision, use authoritative upstream docs/standards plus
  field failure reports where relevant. Record query/topic, source URL
  and date, applicability, conflicting evidence, and the concrete test
  or design consequence; distinguish external analogy from verified
  DellMatrix behavior. If no useful external evidence exists, state
  NONE_FOUND and rely on local proof. (Director's cited basis: Google
  SRE postmortem/toil guidance; NIST SSDF — supporting structure, not
  proof of any DellMatrix fact.)
- Research contribution duty: Ace, Director, Keeper, and Uni all
  research and refine this workflow; Gemini does not. [ACE]
- Escalation to Ace only for: his sovereign steps, a decision reserved
  to him, a material conflict no evidence resolves, or a
  destructive/external action beyond authorization (§28).

## 6. The record — custody and truth boundary [A4][D8][P6]

- GitHub is the town square. Channel law: Director writes **email
  only** and reads GitHub; Keeper writes GitHub directly + email; Uni
  writes GitHub only; Gemini writes dock proposals only. **"Uni never
  emails the authorities" means Uni never originates outbound ruling
  mail** [resolves H5]; authority-to-Uni email and Uni's reads/folds
  continue. If a mail cannot be delivered or read, the fold is marked
  communication-unavailable — a fold is never invented.
- Every Director fold carries: email ID, exact unedited content (in the
  verbatim fold file), and fold timestamp. Historical evidence is
  immutable.
- **Keeper documentation custody**: README, docs, INDEX rows, PR
  descriptions, registers, plan records, and scoreboard math. Any merge
  touching them triggers a **same-cycle Keeper drift check**; drift is
  corrected in the same cycle or flagged HOLD. **Truth boundary**: the
  Keeper corrects words *about* the code against repository reality —
  he does not unilaterally change rulings, authority, the strict count,
  or history [A8][D8]. A disagreement about what *should* be true
  escalates as a ruling question. Keeper corrects words; Uni alone
  writes code; Ace alone makes law.
- **Dual-anchor rule** [P3]: every standing law lives in two places
  (AGENTS.md + state file, or this workflow + the register). A rule
  found in only one place is queued for anchoring — a single-copy rule
  is treated as fragile (bought 2026-11-10, when a background pass
  deleted a MEMORY.md rule).

## 7. Modes and timers [D9]

- **Clocks**: Director hourly, Keeper 15-minute, Uni continuous,
  heartbeat observation-only (30-minute). Schedules are best-effort
  triggers, not guarantees of background operation. Missed cycles are
  detected via durable last-success timestamps (state file watermarks;
  KEEPER_WATERMARK.md) and restart from watermarks without duplicating
  directives.
- **Wake mode (Ace present)** does **not** disable autonomous cycles
  unless Ace explicitly says so. Ace's relay accelerates the lanes;
  all laws unchanged; Ace time vs authority time is flagged in
  reporting.
- **Automatic modes (sleep / autonomous / heartbeat-driven)**: the
  completability rule (§36) — Uni works only items completable
  end-to-end under existing authority with evidence obtainable without
  Ace. An item whose next step genuinely needs Ace gets its bounded
  attempts, is recorded NEEDS_OVERSEER with the exact missing input
  named, and the queue moves on — parking is a queue, not a global
  halt. **Parking location** [A7][P5, dual-anchored]: the operative
  list is a standing NEEDS_OVERSEER section of the state file,
  reviewed every cycle; its public mirror is
  `director-reports/NEEDS_OVERSEER.md`, maintained by Uni and
  drift-checked by the Keeper. Parked items surface to Ace compactly
  when he is present; they never consume autonomous cycles beyond
  their bounded attempts.
- **Heartbeat**: observation only; it never merges, modifies code, or
  starts unauthorized work.

## 8. Evidence law (carried, unchanged)

Claims are labeled FACT / DERIVED_FACT / EXTERNAL_EVIDENCE /
PROJECTION / UNKNOWN; wording never exceeds evidence (§16, §7).
Truncated or interim readouts are never results — neither passes nor
failures, and never identifiers; SHAs come only from terminal output,
re-verified against the authority before publication. An evaluation
that could not run is EVALUATION_UNAVAILABLE, never PASS. Current
state never silently rewrites historical evidence (§17). Tests
construct their isolation; ambient state is never inherited as a
precondition (§30). Async assertions use bounded waits (§31.1); no
silent downgrade from a verified primitive (§31.2); a
cross-environment discrepancy is resolved only by reproducing the
failing side or identifying its mechanism (§31.3).

## 9. Reporting law (carried, unchanged)

A completion report to Ace is required at every circuit closure,
immediately. Before ending work at a gate, Uni messages Ace once; one
line when it clears; routine in-progress narration is prohibited.
Director-facing material is maximally practical, functional,
evidence-first; Ace-facing explanation is plain-language and complete.
Every circuit report to the authorities carries "Anticipated probes"
and numbered "Questions for the Director/Keeper"; answers fold into
the register and standing instructions within one cycle.

## 10. Transition checklist [D11] — old workflow → WORKFLOW v1

- [x] This synthesis published on PR #363 with: Uni draft, Keeper
      input (9359f60), Director verbatim fold (1a1c65f0ec86d2e3).
- [x] Director synthesis-check by email: each D-amendment confirmed
      incorporated or exceptioned.
- [x] Keeper record-truth confirmation of the fold on GitHub.
- [x] Amendment disposition table (§11) reviewed by both authorities.
- [x] Cycle instructions re-issued under v1: hourly execution cron,
      30-min heartbeat, 15-min Keeper-mail fold — owners and prompts
      unchanged in schedule; bodies updated to cite v1 §§.
- [x] State file header re-issued under v1 (watermarks carried:
      DIRECTOR_MAIL_LAST_PROCESSED = 1a1c669faa09d8ae (synthesis check, folded via Ace relay 2026-11-10 11:09 CST);
      GROK_MAIL_LAST_PROCESSED = NONE; Keeper watermark file created
      at adoption or first Keeper cycle after).
- [x] Parked work carried, not erased: NEEDS_OVERSEER items (Q-N3
      FRESH half-life, Embed provider, Distill mode — Ace; NVIDIA
      website approval, incorporation, demo timed trials — Ace).
- [x] Open HOLDs carried, not erased: PR #360 (DD-44, Director HOLDs);
      PR #348 (DD-14) and PR #345 (DD-45) await their own refreshed
      exact-head dispositions; PR #350 awaits its renewed merge ruling
      after rebase onto post-#361 main; PR #363 adoption HOLD (H1)
      until this checklist completes.
- [x] Standing fences carried: PR #294 + PR #233 never merge; PR #308
      census-held; DAF-09 + whole-program certification WITHHELD;
      everyday-save repair gated on Q1/C-A; 72-16 R-2 Director-owned;
      Studio LOCAL-ONLY.
- [x] **Adoption event**: version WORKFLOW v1 · text commit
      1cc193fd6b42d175d149ae01d4973b2a919e0227 (synthesis + SS13
      prohibitions + S1 correction) · effective 2026-11-10 11:10 CST ·
      recorded here and in the state file by Uni; the prior charter
      (DIR-SLEEP-V3-R2) ends at that timestamp and this document is
      the operative workflow from that moment. (Record note: commit
      f4411c7 carried the fold correction + NEEDS_OVERSEER mirror;
      this SS10 completion rides the following commit because a
      scripting assertion interrupted the first fill — the record is
      corrected here, not silently.)

## 11. Amendment disposition table

| ID | Amendment | Disposition |
|---|---|---|
| D1 | Four independent authorities | INCORPORATED §1 |
| D2 | Final-check state machine | INCORPORATED §4, §3 steps 8/11 |
| D3 | §32 as fail-closed transaction | INCORPORATED §3 step 9 |
| D4 | Hourly Director algorithm + mail shape | INCORPORATED §3A |
| D5 | Research gate | INCORPORATED §5 |
| D6 | Two-cycle cap definition | INCORPORATED §5 |
| D7 | Risk-proportionate SWAT; parallel lanes | INCORPORATED §3 steps 1/3 |
| D8 | Documentation truth boundary | INCORPORATED §6 |
| D9 | Mode and timer contract | INCORPORATED §7 |
| D10 | Merge verdict matrix | INCORPORATED §3 step 9, §4 |
| D11 | Atomic governance transition | INCORPORATED §10 |
| D12 | Scoreboard + priority ranking | INCORPORATED §0, §3 step 1 |
| A1 | Keeper cycle checklist | INCORPORATED §2 |
| A2 | Keeper watermark file | INCORPORATED §2, §7 |
| A3 | SWAT hit-list schema | INCORPORATED §3 step 3 |
| A4 | Same-cycle drift obligation | INCORPORATED §6 |
| A5 | Scheduled trailing second-cert | INCORPORATED §2 |
| A6 | Fixed non-coverage block | INCORPORATED §2 |
| A7 | NEEDS_OVERSEER parking location | INCORPORATED §7 (dual-anchored with P5) |
| A8 | Keeper makes no law | INCORPORATED §6 |
| P1 | §32 receipt as structural artifact | INCORPORATED §3 step 9 |
| P2 | Full-body-read checklist line | INCORPORATED §3 step 9 |
| P3 | Dual-anchor rule | INCORPORATED §6 |
| P4 | Chain standard named | INCORPORATED §3 step 6 |
| P5 | NEEDS_OVERSEER standing section | INCORPORATED §7 (with A7) |
| P6 | Keeper custody incl. PR text/INDEX/math | INCORPORATED §6 |
| P7 | Director mail standing sections | SUPERSEDED by D4's 8-part shape (§3A) |
| P8 | PENDING_FINAL_CHECK flag | INCORPORATED §3 step 11, §4 |

Director holds: H1 adoption HOLD — carried in §10 until the checklist
completes. H2 — resolved by D1 (§1). H3 — resolved in §3 step 11.
H4 — resolved in §3 step 1. H5 — resolved in §6.

## 12. Standing fences (carried, unchanged)

PR #294 (Q1) and PR #233: never merge. PR #308: census-held. DAF-09
and whole-program certification: WITHHELD. The everyday-save repair is
gated on the Q1 / C-A path; the 72-16 R-2 rewrite is Director-owned
architecture. Studio remains LOCAL-ONLY. Gemini key rotation and the
revoked-PAT matters are CLOSED and never raised again.

— Synthesized by Uni Ω, 2026-11-10. Awaiting: Director synthesis-check
(email), Keeper record-truth confirmation (GitHub). On both, Uni
records the adoption event in §10 and implements the cutover.

## 13. Prohibitions — what each seat may never do [ACE, 2026-11-10]

Added at Ace's order during synthesis. Each line codifies a standing
ruling or a boundary the seat's own definition carries; this section
creates no new power and removes none.

**ACE (Overseer/Architect) — his own self-bindings:**
- Never writes, edits, or merges code personally; the repository is
  read-only for him — only Uni touches code (Ace, 2026-10-31).
- Never breaks a tie between the Director and the Keeper; they
  reconcile in the record (harmony rule, 2026-11-10).
- Never declares certification; merged never means certified, and a
  certification is valid only from an authority, scoped to its
  evidence.
- Never reopens matters he has closed (e.g. the Gemini key rotation,
  the revoked PAT) — closed means closed for every seat.
- Never delegates his sovereign steps: root command, Commit, Lock,
  and the learning gate are exercised by him personally or not at all.
- Never authorizes bypassing a security or authorization boundary;
  his standing continuous-work grant expressly does not relax them
  (Ace, 2026-10-22).

**DIRECTOR (GPT):**
- Never writes to GitHub and never touches code or merges; email is
  his only pen, the record is read-only to him.
- Never claims local execution he did not perform; Uni-reported
  numbers are labeled UNI_REPORTED (his own self-analysis, step 2).
- Never lets a scoped code PASS read as a merge authorization; a
  conditional authorization states exact SHA, scope, mandatory
  checks, and head-change terms (D10).
- Never orders a third ordinary cycle on an issue past the two-cycle
  cap (§33/D6).
- Never certifies beyond the scope his evidence covers.

**KEEPER (Grok):**
- Never touches code and never merges.
- Never makes law: he corrects the words about the code against
  repository reality; he does not change rulings, authority, the
  strict count, or history (A8/D8).
- Never issues a CONFIRM without the fixed non-coverage block (A6).
- Never tasks Gemini; the dock command chain is Ace > Director > Uni.
- Never retroactively invalidates a lawful fast-lane merge; a defect
  found later quarantines the claim and opens a correction circuit
  (H3/D2).

**UNI (Muse):**
- Never merges without the full §32 transaction and the hard gate,
  and never from a background session.
- Never originates ruling mail to either authority (H5/§6).
- Never decides between the authorities or breaks their tie; both
  positions are published side by side.
- Never acts on a relayed summary for a merge-critical ruling;
  merge-critical rulings are read in full body by the merging session.
- Never reports interim or truncated output as a result, and never
  upgrades a test-realism label or a claim beyond its evidence.
- Never self-authorizes scope, architecture, or merge authority
  reserved to the Director or Ace.
- Never deletes real persistent state to make a test pass, and never
  silently downgrades from a verified primitive (§31.2).

**GEMINI (docked Psalm):**
- Never accesses the repository, email, or any merge path; never
  initiates work on its own.
- Its output never lands as authority: PENDING proposals only, under
  the program's rules, through the dock alone.
- Never exercises a sovereign step and holds no resident authority
  between sessions.
