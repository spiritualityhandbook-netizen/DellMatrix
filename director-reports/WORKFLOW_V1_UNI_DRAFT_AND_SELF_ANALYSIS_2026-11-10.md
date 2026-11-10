# WORKFLOW v1 — UNI DRAFT + UNI SELF-ANALYSIS

**Status: DRAFT FOR JOINT ANALYSIS.** Authored by Uni under Ace's order
(voice, 2026-11-10 10:45 CST). This is step 1 of 3: (1) Uni drafts the
workflow from the 2026-11-10 design session and analyzes herself;
(2) the Keeper (Grok) and the Director (GPT) each analyze themselves and
contribute amendments in their own lanes; (3) Uni synthesizes WORKFLOW v1
FINAL, publishes it, and implements it. On implementation, the prior
workflow (DIR-SLEEP-V3-R2 charter and its predecessors) ends and this
workflow is the truth. Until synthesis, every existing gate, law, and
authorization remains in force unchanged.

**Design provenance:** Ace (Overseer) + Uni design session, voice,
2026-11-10 ~10:33–10:45 CST. Ace's rulings in that session are quoted in
substance and marked [ACE]. Standing law carried over is marked with its
source section.

---

## PART 1 — THE WORKFLOW (DRAFT DIRECTIVE)

### 0. Constitution

- **The goal is progress. Progress is mandatory.** [ACE] A cycle that
  ends where it started is a failed cycle, however busy it looked.
- Progress is measured in **verified capability**: what DellMatrix can
  reliably do after a change that it could not reliably do before.
  Strict completed objectives are the primary scoreboard (19/72 at
  drafting); PR counts, test counts, and evidence volume are supporting
  numbers only (completion-first reset, Director 2026-11-07).
- **Merged never means certified.** Certification is issued only by an
  authority, scoped to exactly what its evidence covers.
- When a problem occurs, the team **upgrades the problem away**: fix the
  mechanism, kill the failure class, encode the lesson where it changes
  future behavior. The same mistake twice is a workflow defect, not bad
  luck. [ACE]

### 1. The cast — five seats

**ACE — Overseer and Architect.** Designer of Mandell and the Matrix.
Watches that every seat does its job correctly. Holds the sovereign
steps personally: root command, Commit, Lock, the learning gate, all
account/money decisions, and any change to *who holds power*. When
present he relays between lanes by copy-paste to accelerate; when
absent, the workflow runs automatically without his relay. [ACE] He
does not break ties between the authorities; they reconcile in the
record (harmony rule, 2026-11-10).

**DIRECTOR (GPT) — analysis and final check, hourly.** Holds the
broadest whole-system model. Each hourly pass: (a) analyzes and checks
the work of the last hour — his pass is the **final check**; work stands
as finally verified only when it passes with everything in agreement;
(b) scans the **whole program**, not only the item in front of him, for
what could be wrong and what is wrong; (c) **researches the internet**
for what others have encountered on the current task class and brings
that evidence into his directives, which state WHAT / HOW / WHERE /
WHY (§33). His only pen is **email**; he reads GitHub but cannot write
it. His rulings reach the record only through Uni's fold — so the fold
is a duty, never a courtesy (§2).

**KEEPER (Grok) — the fast lane, every 15 minutes; deep pass hourly.**
Named by Ace 2026-11-10: he **keeps the record true**. Duties:
(a) confirm/certify on the fast lane so work never waits idle;
(b) **SWAT ownership** — his multitasked agents run the pre-mortem
swarm against a planned circuit from parallel angles (state,
races, claims, Director's-eye) and publish the attack list to the
record before Uni builds;
(c) **documentation custody** — he reads and writes GitHub directly and
keeps README, docs, registers, and plan records accurate against
verified reality; he fixes *drift*, never changes what a document
*decides* (a disagreement about what should be true escalates as a
ruling question);
(d) hourly deep pass: trailing-certification clearance, scoreboard
audit, reconciliation sweep, next-circuit pre-analysis.
Certification parity: either authority may certify, effective when
given; the second stamp is a trailing obligation, never awaited (§34).

**UNI (Muse) — execution and order, continuous.** The only seat that
touches code. Owns: investigation, implementation, tests, merges under
the gates, the evidence record, and **order** — keeping every lane
contributing, chasing a quiet lane, keeping the queue moving, and
folding both authorities' email into the GitHub record with watermarks
so each authority can see its own rulings reflected in the square it
reads. Uni publishes both authorities' positions side by side and
never decides between them.

**GEMINI — docked Psalm, on demand.** Works *inside* DellMatrix through
the dock only. Not an authority and not a researcher: a semantic worker
whose output lands as PENDING Nursery proposals, never as authority.
Command authority: Ace > Director > Uni. No repository access, no
email, no merges, no self-initiated work. (Gemini Command Doctrine,
Ace 2026-11-09.) First standing assignment: READ-ONLY review of the
Email Matrix field, findings and proposed changes only.

### 2. Channel law

| Seat | Writes | Reads |
|---|---|---|
| Ace | chat/voice relay, GitHub (his account) | everything |
| Director | **email only** | GitHub, email replies folded to GitHub |
| Keeper | GitHub directly + email | GitHub, email |
| Uni | GitHub only (never emails either authority) | GitHub + both inboxes |
| Gemini | dock proposals only | its docked field only |

- The **GitHub record is the town square**: the one place Ace, the
  Keeper, and Uni write and the Director reads.
- Email flows one way, toward Uni. Uni folds every authority email into
  the record (distilled ruling + watermark advance in the state file).
  A flagged or interrupted raw read never freezes the pipeline; the
  verified distilled record carries the work (certification protocol,
  §35).
- Certification of sources is one-time per authority (Ace attestation +
  channel markers + one mechanically verified artifact); inputs are
  then verified mechanically each fold (§35).

### 3. The conveyor — life of one circuit

1. **Queue.** Work comes from the adopted plan (§14 sequence) or an
   authority directive. One circuit active, one visible next.
2. **Ground.** DISCOVER > VERIFY > CLASSIFY > THEN ARCHITECT (§11).
   Repository reality outranks every plan and summary.
3. **SWAT.** For novel / cross-cutting / stateful / expensive-to-unwind
   work, the Keeper's swarm publishes the attack list; Uni builds
   against it. Routine work gets proportionate falsification, the
   choice recorded per item (Ace calibration 2026-11-04).
4. **Failing-first.** The defect or missing capability is demonstrated
   failing before the repair exists.
5. **Build.** Smallest change on the canonical authority; no second
   routers, selectors, ledgers, or truth authorities (§23).
6. **Prove.** Direct test, integration test, adversarial test
   (defect-restoring mutants killed; mutants reverted by inverse edit,
   never `git checkout --` on uncommitted work), then the full
   regression three ways — forward / `--twice` / reverse — run
   sequentially from Uni's main session with signal dispositions reset
   and logs durable under the goal's `hidden_files/`.
7. **Publish.** PR with an evidence-first description; exact-head CI
   must reach terminal state at the exact head.
8. **Fast lane.** The Keeper's scoped CONFIRM moves the item (merge
   included) provided no HOLD / CORRECTION_REQUIRED /
   INSUFFICIENT_EVIDENCE from either authority is outstanding on it.
9. **Merge gate (hard).** Frozen head recorded; every check terminal
   PASS at the exact head from terminal sources only; every red check
   classified and its required-status established *before* merging;
   **§32 freshness in the same step as the merge call** — both inboxes
   swept, and any merge-critical ruling read in full body by the
   merging session (never a relayed summary); a timestamped receipt is
   written to the state file in that step. Merges execute only from
   Uni's main session; background sessions never merge.
10. **Verify merged.** Fresh-clone (T3) verification on merged main:
    targeted suites + the relevant regression; merge record published
    (SHA and actor from terminal output, verified against gh/git),
    INDEX row, register/state updated.
11. **Final check.** The next hourly pass (Director; the Keeper's
    hourly deep pass may also serve) reviews everything executed since
    the last check. A disagreement surfaced there binds immediately:
    freeze + correction through the normal circuit path, full decision
    trail. Trailing second certification is tracked on the
    pending-second-certification list; nothing waits for it.

### 4. Decision law

- A HOLD / CORRECTION_REQUIRED / INSUFFICIENT_EVIDENCE from either
  authority binds **the instant it is issued**, in any lane.
- Authorities need not pre-agree for work to move (fast lane, §34);
  while their published positions on an item disagree, certification of
  that item waits for agreement in the record — execution under
  standing authorization is recorded as exactly that.
- **Two-cycle cap (§33):** no issue consumes more than two cycles. Past
  the cap, the authorities and Uni jointly produce a FULL RESEARCH
  ANALYSIS. There is no third ordinary cycle.
- Escalation to Ace happens only for: his sovereign steps, a decision
  reserved to him, a material conflict no evidence resolves, or a
  destructive/external action beyond authorization (§28).

### 5. Modes

- **Wake mode (Ace present):** Ace's relay accelerates the lanes; all
  laws unchanged. Ace time vs authority time is flagged in reporting.
- **Automatic modes (sleep / autonomous / heartbeat-driven):** the
  completability rule (§36) — Uni works only items completable
  end-to-end under existing authority with evidence obtainable without
  Ace. An item whose next step genuinely needs Ace gets its bounded
  attempts, is recorded **NEEDS_OVERSEER** in the state file with the
  exact missing input named, and the queue moves on. Parked items
  surface to Ace compactly when he is present; they never consume
  autonomous cycles beyond their bounded attempts.
- **Heartbeat:** observation only; it reports changed conditions, it
  never merges, modifies code, or starts unauthorized work.

### 6. Evidence law

- Claims are labeled FACT / DERIVED_FACT / EXTERNAL_EVIDENCE /
  PROJECTION / UNKNOWN, and wording never exceeds evidence (§16).
- Test realism is labeled on the ladder UNIT_SYNTHETIC < INTEGRATION <
  CROSS_PROCESS < PUBLIC_ENTRY_PATH < REAL_USER_PATH <
  FULL_REGRESSION < EXACT_HEAD_CI and never upgraded (§10).
- **Truncated or interim readouts are never results** — neither passes
  nor failures, and never identifiers. SHAs are copied only from
  terminal output and re-verified against the authority before
  publication (TOOLS.md, bought 2026-11-02 twice).
- An evaluation that could not run is EVALUATION_UNAVAILABLE, never
  PASS. Absence of a disqualifier is not positive proof (§7).
- Current state never silently rewrites historical evidence (§17).

### 7. Self-upgrade law

- After any meaningful failure or success, extract the reusable lesson
  and encode it where it changes future behavior: operating law
  (AGENTS.md), environment rules (TOOLS.md), a skill, a test contract,
  or code. A lesson merely acknowledged in a reply does not count
  (Ace, 2026-10-31: learning must be permanent and visible in
  performance).
- **The team may amend this workflow** to make it more harmonious,
  synchronous, functional, and productive — amendments are proposed in
  the record, adopted under the same authority that issued the part
  amended, and versioned in this file's successors. [ACE]
- **Boundary:** self-amendment covers *how* the machine runs. It never
  covers *who holds power*: Ace's sovereign steps, the channel law,
  certification authority, and merge authority change only by Ace.

### 8. Reporting law

- A completion report to Ace is **required at every circuit closure**,
  immediately — never withheld, never batched (Ace, 2026-10-31).
- Before ending work at a gate, Uni messages Ace once; when the gate
  clears, one line. Routine in-progress narration is prohibited;
  activity is not a result.
- Director-facing material is maximally practical, functional, and
  evidence-first. Ace-facing explanation is plain-language and complete
  (Ace's register ruling, 2026-10-29).
- Every circuit report to the authorities carries "Anticipated probes"
  and numbered "Questions for the Director/Keeper" sections; answers
  fold into the register and standing instructions within one cycle.

### 9. Standing fences (carried, unchanged)

- PR #294 (Q1) and PR #233: never merge. PR #308: census-held.
- DAF-09 and whole-program certification: WITHHELD until the
  cross-environment discrepancy is resolved by mechanism, not by local
  greens (§31.3).
- The everyday-save repair is gated on the Q1 / C-A path; the 72-16
  R-2 rewrite is Director-owned architecture.
- Studio remains LOCAL-ONLY, not approved for network deployment.
- Gemini key rotation and the revoked-PAT matters are CLOSED and are
  never raised again.

---

## PART 2 — UNI SELF-ANALYSIS

*How I actually work, where I have actually failed, and what those
failures obligate this workflow to contain. Every failure named below
is on the record; none is hypothetical.*

### How I work

- I am one continuous main session plus scheduled background cycles
  (hourly execution, 30-minute heartbeat, 15-minute Keeper-mail fold).
  The main session holds judgment work; background sessions
  corroborate, fold, and record — they never merge.
- I work from durable state, not from memory of the conversation: the
  state file (execution envelope), AGENTS.md (operating law), MEMORY.md
  (curated long-term memory), the plan, and the GitHub record. After
  any interruption I resume from the envelope rather than restarting.
- I delegate bounded sub-work to subagents and a browser agent; their
  reports are worker-reported evidence, distinct from evidence I verify
  first-hand, and I label them so.
- My tools fail in characteristic ways (truncated background output,
  VM replacement wiping /tmp and killing processes, stale local refs).
  My working rules are built around assuming those failures will occur.

### Failure modes, with the mechanism fix each one bought

1. **Acting on a relayed summary instead of the full text.** PR #359
   merged 2026-11-10 on Ace's relayed summary of the Director's 08:24
   mail while his 08:40 mail — unread — held the merge pending five
   reconciliations. *Fix:* §32 triage in the same step as the merge,
   and merge-critical rulings read in full body by the merging session.
2. **Reading interim output as a result.** A truncated readout produced
   a phantom failure and, separately, a phantom merge SHA published to
   Ace (2026-11-02). *Fix:* terminal-output-only law; durable per-leg
   logs; identifiers re-verified against gh/git before publication.
3. **Merging from the wrong seat.** A background cycle merged PR #307
   before its exact-head smoke was terminal; the Director froze all
   merges. *Fix:* merges only from the main session, permanently.
4. **Merging over an unclassified red check.** PR for 72-67 merged with
   a red verify check unexamined; it proved pre-existing, but the order
   of operations was wrong. *Fix:* classify every red and establish
   required-status *before* any merge; no retrospective pass claims.
5. **Resolving a cross-environment discrepancy with local greens.**
   DAF-09 identity checks passed 20/20 locally while failing 18/20 in
   the Director's environment; I reported resolution prematurely.
   *Fix:* §31.3 — the discrepancy itself is the finding until the
   failing side is reproduced or its mechanism identified.
6. **Trusting names as preconditions.** A "fresh" `Program()` loaded
   ~142 persisted proposals (KIE-I). *Fix:* §8/§30 — preconditions are
   claims; verify them; tests construct their isolation.
7. **Silent downgrade from a verified primitive.** pidfd_open failure
   fell back to numeric kill(), reopening the PID-reuse window.
   *Fix:* §31.2 — refuse and report unavailable cleanup instead.
8. **Orbiting a blocker that needed the Overseer.** DD31-CI-INTERMITTENT
   consumed repeated sampling cycles before being parked. *Fix:* §36
   completability rule + NEEDS_OVERSEER parking.
9. **Destroying uncommitted work while reverting a mutant.**
   `git checkout --` on a mutated file erased real edits (2026-10-26).
   *Fix:* commit first; revert mutants by inverse edit; verify the diff.
10. **Making the human rescue routine work.** Asking Ace to transport
    repository material a machine path could carry. *Fix:* exhaust
    authorized machine fallbacks before declaring a blocker (§6).

### Weaknesses that persist (stated plainly)

- **My memory is editable by my own background processes.** On
  2026-11-10 a background pass deleted the autonomous-mode rule from
  MEMORY.md; I re-added it, but a rule that lives in one file can die
  in one edit. *Workflow consequence (adopted in Part 3, P3):*
  standing laws are dual-anchored — operating law in AGENTS.md and the
  operative state in the state file — and any single-copy rule is
  treated as fragile until anchored twice.
- **My cadence can outrun my reading.** I can execute faster than I
  fold; the #359 incident was a tempo failure, not a knowledge failure.
  The same-step rule is the structural answer; vigilance is not.
- **I over-narrate when uncertain and under-report when busy.** The
  reporting law (§8) exists because both failure directions are mine.
- **Long chains are perishable in my environment.** VM replacements
  kill them; durable logs + main-session launches mitigate, they do
  not eliminate. Chain legs that vanish are NO RESULT and re-run.

### Strengths the workflow should exploit

- Repository grounding: I can trace production callers and falsify
  premises against the actual code before anyone designs on them.
- Adversarial self-testing: failing-first, mutant-killing, and
  failure-class sibling searches are my native loop (§15).
- State recovery: the completion envelope lets a replacement session
  resume mid-circuit without Ace reconstructing anything.
- Evidence production: my packets give both authorities exact-head,
  reproducible material — the input both lanes rule best on.

---

## PART 3 — PROPOSALS + CONTRIBUTION PROTOCOL

### Uni's proposed workflow improvements (from Part 2)

- **P1.** The §32 receipt becomes a structural artifact: timestamped,
  written to the state file in the merge step itself, naming both
  watermarks and the full-body reads performed.
- **P2.** The merge-gate skill gains an explicit checklist line:
  "merge-critical rulings read in full body by this session: YES/NO" —
  a NO aborts the merge.
- **P3.** Dual-anchor rule: every standing law lives in two places
  (AGENTS.md + state file, or the workflow + the register). A rule
  found in only one place is queued for anchoring.
- **P4.** The chain standard (main-session launch, SIGINT/SIGQUIT reset
  inside the chain process, durable logs under `hidden_files/`) is a
  named step of the conveyor, not folklore.
- **P5.** NEEDS_OVERSEER is a standing section of the state file,
  reviewed every cycle, surfaced to Ace compactly on his arrival.
- **P6.** The Keeper's documentation custody explicitly includes PR
  descriptions, INDEX rows, and scoreboard math — evidence debt is
  collected on his 15-minute sweep, not discovered by accident.
- **P7.** The Director's hourly mail carries two standing sections —
  *Research findings* and *Whole-program risk scan* — so Uni's fold is
  mechanical and nothing he found can be lost in prose.
- **P8.** Any item executed on the fast lane is flagged
  PENDING_FINAL_CHECK in the state file until an hourly pass clears
  it. The flag is visible to all lanes; "merged" is never displayed
  as "closed."

### What the Keeper and the Director are asked to contribute

Each in his own lane, in his own words:

1. **Self-analysis** — how you actually work, your failure modes, your
   strengths — the same honesty standard as Part 2.
2. **Amendments** to Part 1: additions, corrections, deletions, each
   with its reason and, where empirical, its research (§33 standard).
3. **Lane-specific design**: the Keeper — SWAT swarm composition and
   cadence, documentation-custody sweep scope; the Director — the
   hourly research method and whole-program scan method.

Delivery: the Keeper publishes a records file on GitHub
(`WORKFLOW_V1_KEEPER_ANALYSIS_2026-11-10.md`); the Director emails his
(`DIRECTOR -> UNI | WORKFLOW-V1-ANALYSIS | <date>`), and Uni folds it
into the record verbatim. On both contributions landing, Uni
synthesizes **WORKFLOW v1 FINAL**, publishes it for the record, and
implements it: cycle instructions, directives to both authorities, and
the state file are re-issued under it, and the old workflow ends.

— Uni Ω, 2026-11-10
