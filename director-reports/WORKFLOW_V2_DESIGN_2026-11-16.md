# WORKFLOW v2 DESIGN — GitHub-First, Event-Driven, Two-Checker

Author: Uni (drafting lane). Date: 2026-11-16. Status: **DRAFT FOR
TWO-CHECKER REVIEW** under AGENTS.md section 43 (Ace ruling 2026-11-16
09:32 CST). This design is NOT adopted until the Director and the Keeper
have each independently checked it and all three lanes agree it is
correct. It changes no authority, HOLD, certification, or counting rule:
the Grand Workflow (PR #423) GW-02 preservation stands — v2 supersedes
operating/transport rules only, the same relation the Grand Workflow
bore to WORKFLOW v1.

Directive (Ace, 2026-11-16 09:32): once the Director's GitHub
connection is confirmed, (1) research GPT automations with GitHub and
whether Uni's GitHub reports can trigger them, (2) reassess what every
lane is capable of, (3) design the best workflow the three lanes can
run, all contributing in many ways, under all of Ace's other demands.
Companion rulings the same morning: section 43 (two-checker write rule)
and section 44 (email sunset).

## PART 1 — CAPABILITY REASSESSMENT (evidence dated 2026-11-16)

### Ace / Overseer
- Sovereign authority; installs and account-level grants (proved today:
  the Codex Connector install at 09:19 CST unblocked the entire lane);
  EXE command; final word on every fence. No transport duty — the
  workflow must never route through Ace's hands (Grand Workflow
  transport self-repair law).

### Director (ChatGPT)
PROVEN today, on this repository:
- GitHub read+write through the ChatGPT Codex Connector (installed
  09:19 CST; scopes: read checks/statuses/metadata; read+write actions,
  code, issues, pull requests, workflows; all repositories).
- Comment write: TEST comment on PR #459 at 09:25 CST.
- Document publication: PR #460 opened by the Director's own hand with
  two authored plan files (C5R.2 SEE, C5R.3 ORGANIZE), then two repair
  heads (75019173, 7fa82934) including a canonical-AC correction.
- Plan authoring as a production lane (section 42.4): two complete,
  source-anchored plan drafts delivered and reconciled through review.
- Rulings posted directly on PRs (fresh-head checks on #447/#448/#460,
  CORRECTION_REQUIRED on #421, index on #459).
DOCUMENTED (OpenAI help/developer docs; research record
GPT_GITHUB_AUTOMATION_TRIGGERS_2026-11-16):
- Event-triggered ChatGPT tasks exist: they respond to supported
  GitHub pull-request activity in an authorized repository (caps:
  30 runs/hour, 720/day across event tasks; approval-requiring actions
  pause the run). WHICH PR activities fire — in particular whether
  comments fire — is NOT documented: UNTESTED, test protocol in Part 3.
- `@codex review` / `@codex <instruction>` in a PR comment starts a
  Codex review / cloud task on the spot (a fresh coding worker, not the
  Director's continuing thread). The Codex review bot is already live
  on this account (P2 finding on PR #460).
LIMITS: Codex review cannot approve or block a PR; no GPT-side merge
is documented — merges stay Uni's act. The Director runs no local code,
tests, or campaigns; his evidence is source reading + CI observation.

### Keeper (Grok)
PROVEN: GitHub read+write including watermark commits directly on main;
scoped stamps/confirms at exact heads (incl. the #459 terminal confirm
and the DD-18 / Q-DD42.1 second certifications, trailing ledger 0);
automations on the :15 fast-confirm / :45 deep-pass phases; expanded
lane under section 42.5 (useful work incl. code-shaped drafts in his
own lane, non-interference fence, same checking standards).
UNKNOWN: whether Grok automations have any event trigger equivalent to
ChatGPT's (Q-W2.2 below); treat as clock-driven until proven otherwise.

### Uni (Muse)
PROVEN: sole merge actor and production-code landing hands (section 32
transaction); regression campaigns (serial, main-session); code and
records implementation; the 2-minute watch + 30-minute execution cycle;
mail digest as legacy fallback reader. Uni posts via `gh` as the
owner's own GitHub account, so Uni comments are ordinary user comments
for every documented trigger path (no bot-author caveat).

### Non-authority workers
- Codex bot: automatic/manual PR review worker (P0/P1 focus). Useful
  second eyes; NOT an authority; its findings enter as evidence only.
- Gemini: docked Psalm inside DellMatrix only (program surfaces,
  PENDING outputs, no repository access). Unchanged.

## PART 2 — THE WORKFLOW

1. **One shared record.** GitHub is the single surface all lanes read
   and write: rulings as PR comments, plans/reports as files under
   director-reports/ or PRs, stamps at exact heads. State that is not
   on GitHub does not exist for cross-lane purposes.
2. **Doorbell first, clocks as backstop.** The Director arms an
   event-triggered task on DellMatrix PR activity (Part 3 test). Uni
   report comments that need GPT-side worker action end with an
   explicit `@codex ...` line (proven trigger for a review/task). The
   phase grid (Director :00/:30, Keeper :15/:45, Uni watch 2m,
   execution 30m) remains as the guaranteed-latency backstop: events
   make us faster, clocks make us certain.
3. **Two-checker write constitution (section 43).** Any lane may write
   code or plans on branches/PRs; the other two independently check;
   unanimity lands, disagreement freezes for reconciliation; nobody
   checks their own work. First live exercise: PR #460 (Director wrote,
   Uni corrected R1–R3, Director repaired, Uni re-passed, Keeper check
   in flight).
4. **Merge lane.** Serial, Uni-only, section 32 transaction per merge
   (freshness check across GitHub AND legacy mail until the email
   sunset completes; terminal exact-head CI; authority confirmation at
   the exact head). Merged never means certified.
5. **Email sunset (section 44).** On adoption of this design, email
   leaves the transport lane: exception-only use where mail itself
   creates progress GitHub cannot. Uni's mail folding shrinks to the
   legacy fallback and is never expanded; the section 32 freshness
   check becomes GitHub-only once both authorities confirm their lanes
   are GitHub-native (Director: proven 2026-11-16; Keeper: GitHub
   watermark lane already native).
6. **Belts and counting unchanged.** PLAN and CODE belts run in
   parallel; a task is a Grand Plan object scratched off; plan
   completion never inflates the code count; records-only merges never
   count as implemented functionality; the 100-object daily objective
   and the doubling order stand.
7. **EXE = full capacity (section 42)** in every lane, every cycle;
   no-full-stops/parallel-by-default (section 40); immediate restart
   (section 41); campaigns serial and main-session; fences #233/#294/
   #308 and the #421 HOLD stand exactly as recorded.

## PART 3 — DOORBELL TEST PROTOCOL (empirical, sequenced)

Posted on PR #459 (comment 6921910688). (1) Director creates ONE
event-triggered task (trigger: GitHub PR activity on this repo; prompt:
on a Uni comment containing DOORBELL-TEST-1 on PR #459, reply on #459
beginning EVENT-TRIGGER WAKE with time + observed activity) and posts
DOORBELL ARMED + the trigger options the setup offered. (2) Uni then
posts the marker comment. (3) Receipt either way: wake observed =
event-driven primary adopted; no wake within one Director clock cycle
= COMMENT-TRIGGER NOT OBSERVED, clocks + @codex remain the mechanism.
An untested claim is not a receipt.

## PART 4 — OPEN QUESTIONS FOR THE CHECKERS

- Q-W2.1 (Director): which PR activities does the event-task setup
  actually offer for this repo (opened / pushed / ready / merged /
  commented)? The answer scopes Part 2.2.
- Q-W2.2 (Keeper): does the Grok side have any event-triggered
  automation equivalent? If yes, the Keeper lane gets a doorbell too;
  if no, his clock phases remain his trigger, stated plainly.
- Q-W2.3 (both): confirm the merge act stays Uni-only under section 43
  as drafted (agreement is the authority; Uni's session is the landing
  hands) — or state the alternative precisely.
- Q-W2.4 (both): confirm the email-sunset adoption trigger (this
  design's adoption + both lanes GitHub-native) is the right moment to
  retire the mail leg of the section 32 freshness check.

## ADOPTION

On Director check + Keeper check + Uni agreement recorded on the PR
carrying this file, Workflow v2 is ADOPTED and the Cycle System /
Grand Workflow records are amended by a follow-on records PR (Uni
lane). Until then, current law governs unchanged.
