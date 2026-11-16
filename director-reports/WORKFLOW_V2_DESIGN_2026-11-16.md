# WORKFLOW v2 DESIGN — GitHub-First, Event-Driven, Two-Checker

Author: Uni (drafting lane). Date: 2026-11-16. **Revision 2** —
revised by Uni the same day per Director CORRECTION_REQUIRED
(comment 6922164452 on PR #461), findings R1–R5; revision map at the
end of this file. Status: **DRAFT FOR TWO-CHECKER REVIEW**. Not
adopted until the Keeper's independent check and the Director's
recheck at the revised head are recorded and all three lanes agree.
It changes no authority, HOLD, certification, or counting rule: the
Grand Workflow (PR #423) GW-02 preservation stands — v2 supersedes
operating/transport rules only.

GOVERNANCE ANCHOR (corrected per R2): Ace's full-capacity,
two-checker, and email-sunset rulings of 2026-11-16 are recorded in
Uni's workspace operating manual (AGENTS.md sections 42–44, a Uni-side
file) and published on the GitHub record at PR #424 comment 6918881559
and PR #459 comment 6918880978. The repository root AGENTS.md is the
persona registry (52 lines) and does NOT contain those sections; no
claim in this design rests on it doing so. A separate evidence-gated
records change will carry the sections into the authoritative
workflow record on the repository.

## PART 1 — CAPABILITY REASSESSMENT (evidence dated 2026-11-16)

### Ace / Overseer
- Sovereign authority; installs and account-level grants (the Codex
  Connector install at 09:19 CST unblocked the Director lane); EXE
  command; final word on every fence. Ace is also the only lane that
  can arm ChatGPT event tasks: the setup lives in the ChatGPT Work UI
  (proven 2026-11-16, Part 2.2). No transport duty beyond that — the
  workflow never routes work through Ace's hands.

### Director (ChatGPT)
PROVEN today, on this repository:
- GitHub read+write through the ChatGPT Codex Connector (installed
  09:19 CST; read+write on actions, code, issues, pull requests,
  workflows; all repositories).
- Comment write (PR #459 TEST comment 6920698410, 09:25 CST) and
  document publication (PR #460 opened by his own hand with two
  authored plan files, then repaired through two further heads).
- Plan authoring as a production lane; rulings posted directly on PRs.
- Event-triggered wake on a PR comment, via the Ace-armed Work task
  (Part 2.2 receipts).
LIMITS: his own session's Automations contract cannot create event
tasks (discovery action returned NOT_FOUND / HTTP 404; schedule and
timing modes only — his receipt, PR #459 comment 6922131230). Codex
review cannot approve or block a PR; no GPT-side merge is documented —
merges stay Uni's act. He runs no local code, tests, or campaigns.

### Keeper (Grok)
PROVEN: GitHub read+write including watermark commits on main; scoped
stamps/confirms at exact heads; automations on the :15/:45 phases;
expanded lane incl. code-shaped drafts in his own lane under the
non-interference fence. UNKNOWN (Q-W2.2, still open): whether Grok
automations have any event-trigger equivalent — the Keeper alone
verifies his own access; until then his lane is clock-driven, stated
plainly.

### Uni (Muse)
PROVEN: sole merge actor and production-code landing hands (section
32 transaction); regression campaigns (serial, main-session); code
and records implementation; 2-minute watch + 30-minute execution
cycle; mail digest as legacy fallback reader. Uni posts via `gh` as
the owner's own GitHub account, so Uni comments are ordinary user
comments for every documented trigger path.

### Non-authority workers
- Codex bot: automatic/manual PR review worker. Evidence only; never
  an authority; a bot suggestion is not code admission.
- Gemini: docked Psalm inside DellMatrix only (program surfaces,
  PENDING outputs, no repository access). Unchanged.

## PART 2 — THE WORKFLOW

1. **One shared record.** GitHub is the single surface all lanes read
   and write: rulings as PR comments, plans/reports as files, stamps
   at exact heads. State not on GitHub does not exist cross-lane.
2. **Doorbell — PROVEN at the armed configuration, scoped honestly.**
   Ace armed the DellMatrix Doorbell Event Test from the ChatGPT Work
   UI on 2026-11-16: connector github, webhook pull_request,
   repository spiritualityhandbook-netizen/DellMatrix, PR 459,
   comments enabled, bot reviews included, no schedule, no polling.
   Uni posted the marker comment DOORBELL-TEST-1 (PR #459 comment
   6923119862, 16:57:31Z); the task woke on the comment event and
   replied EVENT-TRIGGER WAKE (comment 6923147266, 16:58:38Z, ~67
   seconds, triggered by issue_comment created). Event-driven wake on
   PR comments is therefore PROVEN for this configuration. Scope
   limits, stated plainly: arming is a Work-UI act on Ace's surface
   (the Director's session cannot create event tasks); the proof
   covers the armed PR-comment configuration, not every conceivable
   event type; an hourly condition-watch or an @codex worker is NEVER
   a substitute for a Director event task and must never be reported
   as one. The phase-grid clocks remain as backstop (see 5).
3. **@codex worker triggers.** Uni report comments that need GPT-side
   worker action may end with an explicit `@codex ...` line (proven
   trigger for a review or cloud task). A Codex worker is a fresh
   agent, not the Director's continuing thread, and never a surrogate
   Director event task.
4. **Two-checker write rule — scope explicit (R3).** The rule governs
   AUTHORED ARTIFACTS: code, plans, and records documents. Any lane
   may author such an artifact on a branch/PR; the other two lanes
   independently check it; unanimity lands it, disagreement freezes
   it for reconciliation; nobody checks their own work. The rule is
   NOT a precondition on authority acts: a Director ruling or a
   Keeper stamp/evidence publication takes effect when issued, within
   the approved hierarchy — requiring two approvals before every
   ruling would reintroduce the authority-clock stalls this workflow
   exists to remove. A competing claim may challenge an issued ruling
   with evidence; the record reconciles it. Code-shaped drafts by the
   Director or Keeper stay on isolated nonproduction branches; Uni
   remains sole production-code integrator and merger; no shared
   mutable state between lanes; tool ability confers no authority
   and no role promotion.
5. **Clocks are a backstop, not a guarantee (R5).** The phase grid
   (Director :00/:30, Keeper :15/:45, Uni watch 2m, execution 30m)
   bounds worst-case latency; it does not guarantee it. Tasks can
   miss, pause, or require approval. Latency and accountability stay
   MEASURED: counts are objects closed with cited evidence, gate
   latency is reported per hop, and HELD markers and stop conditions
   remain in force at all times.
6. **Merge lane.** Serial, Uni-only, section 32 transaction per merge
   (freshness check, terminal exact-head CI, authority confirmation
   at the exact head). Merged never means certified.
7. **Email sunset — measured cutover, not a leap (R4).** Email stays
   in the section 32 freshness check until ALL of the following are
   on the GitHub record: (a) at least one unattended :00 Director
   automation GitHub publication with run ID and Uni readback/fold;
   (b) at least one unattended :30 Director automation GitHub
   publication with run ID and Uni readback/fold; (c) a final
   reconciliation of all unconsumed Director email through a recorded
   closing watermark; (d) a recorded cutover timestamp with a
   fail-closed publication receipt/readback. Only then does section
   32 freshness become GitHub-only. A rollback mail pointer is
   retained permanently for connector outages — email retires as
   normative transport, it does not silently disappear, and its
   historical freshness obligation is never deleted by inference.
8. **Belts and counting unchanged.** PLAN and CODE belts run in
   parallel; a task is a Grand Plan object scratched off; plan
   completion never inflates the code count; records-only merges
   never count as implemented functionality; the 100-object daily
   objective and the doubling order stand.
9. **Standing laws unchanged.** Full capacity every cycle; no full
   stops / parallel by default; immediate restart; campaigns serial
   and main-session; fences #233/#294/#308 and the #421 HOLD stand
   exactly as recorded.

## PART 3 — QUESTIONS, AS ANSWERED

- Q-W2.1 (which PR activities fire an event task): ANSWERED BY
  EXPERIMENT — PR comments fire the Ace-armed pull_request task on
  PR #459 (receipts in Part 2.2). The Director's account-session
  contract exposes no event selector (EVALUATION_UNAVAILABLE in that
  session); the Work UI exposes it, and Ace's arming is the receipt.
- Q-W2.2 (Keeper event-trigger equivalent): OPEN — the Keeper alone
  verifies Grok-side access; clock-only until he does.
- Q-W2.3 (merge act): Director answered YES — Uni-only production
  integration and serial merge; cross-check per the scope in
  Part 2.4.
- Q-W2.4 (email cutover): Director answered NO to an unconditional
  immediate cutover — the R4 protocol in Part 2.7 governs.

## REVISION MAP (Director CORRECTION_REQUIRED 6922164452)

- R1 (doorbell existence): Part 2.2 rewritten — no blanket
  event-primary claim; the experiment has now been run and the
  armed-task + observed-wake receipts are recorded with their exact
  scope and limits.
- R2 (governance anchor): header corrected — Ace's sections 42–44
  live in Uni's operating manual and the PR record (comments
  6918881559 / 6918880978), not in the repository AGENTS.md; a
  separate records change carries them into the repo's workflow
  record.
- R3 (two-checker scope): Part 2.4 rewritten — artifacts only;
  rulings and stamps take effect on issuance; drafts isolated and
  nonproduction; Uni sole integrator/merger; no shared mutable
  state; no authority by tool ability.
- R4 (email sunset): Part 2.7 rewritten — four-part measured cutover
  (unattended :00 proof, unattended :30 proof, closing mail
  watermark, recorded cutover timestamp) plus a permanent rollback
  pointer, before section 32 goes GitHub-only.
- R5 (latency honesty): Part 2.5 added — clocks as measured
  backstop, never a guarantee; @codex is a worker, not the Director;
  bot suggestions are not code admission; HELD markers retained.

## ADOPTION

On Keeper check + Director recheck + Uni agreement recorded on the
PR carrying this file, Workflow v2 is ADOPTED and the Cycle System /
Grand Workflow records are amended by a follow-on records PR (Uni
lane). Until then, current law governs unchanged. No PLAN/CODE credit
arises from this design or its merge.
