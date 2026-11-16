# THE CYCLE SYSTEM — DellMatrix Pipeline, Perfect-Cycle Design

Ace order, 2026-11-15 23:08 CST: design the best possible cycle system
from everything the team actually has — Uni, the Keeper (Grok), the
Director (ChatGPT) — grounded in researched automation capabilities
and limits, not assumptions. Status: DESIGN (plan belt). Ace's setup
steps are listed in §7; Uni-side fleet changes, if any, follow Ace's
approval of this design.

## 1. THE CAST — VERIFIED CAPABILITIES AND LIMITS (researched 2026-11-15)

### 1.1 UNI (Muse) — the builder lane

Uni's cycles are Uni's own scheduled jobs on this machine, verified
live 2026-11-15 23:09 CST:

- WATCH — every 5 minutes: folds Director mail (digest path) and
  authority publications on GitHub into the state file; surfaces
  material change only (§39 material-only writes).
- EXECUTION — every 30 minutes: production cycles under the Grand
  Workflow (portable-work duty; executes steps or records a named
  blocker).
- HEARTBEAT — every 30 minutes: observation-only checks (PR/CI state,
  blockers cleared, state contamination).
- MANIFEST SITTING — weekly (Mondays ~09:00 America/Chicago).
- MAIN SESSION — not a timer: it is woken by Ace, by watch/execution
  handoffs, and by background completions, and it alone merges.
  While awake it can run several parallel delegated lanes (§37).
- Limits that bind: long regression campaigns own the machine and run
  serially; a VM replacement can kill a background chain (countered by
  main-session launches + durable logs under hidden_files/); merges
  are main-session acts under the §32 transaction, one at a time.

### 1.2 KEEPER (Grok) — the fast-confirm lane

Researched (xAI announcements + hands-on tests, Nov 2026):

- Grok AUTOMATIONS (grok.com/automations; launched 2026-07-16):
  created and edited BY ASKING IN CHAT ("create an automation that…",
  "edit your routine: …"), or from the Automations page. Each run is
  a fresh request with the saved instructions.
- Schedules: the announcement lists once / daily / weekdays / weekly /
  monthly / yearly; a hands-on test of the automation editor (Sep
  2026) shows trigger options once / HOURLY / daily / weekly /
  monthly / yearly. NO sub-hourly scheduled cadence exists in the
  consumer product. Ace's two hourly Keeper slots are therefore at
  the product's fastest lawful cadence — the design staggers them
  (§3) instead of asking for a faster clock that does not exist.
- Grok SKILLS (May 2026): reusable workflow packages. Created by
  describing the method in conversation and saying "save this as my
  <name> skill", via the Skill Creator, by upload, or by writing the
  skill file. An automation's form carries Connectors and Skills —
  skills ATTACH to automations, and typing @ pins a connector for
  every run. Custom skills take priority over built-ins.
- Email triggers exist (SuperGrok): an automation can fire when a
  matching Gmail/Outlook message arrives.
- Separate product, noted for completeness: Grok Bot routines
  (docs.x.ai, workspace bots) support plain-word interval schedules
  ("every 2 hours") and event triggers (GitHub, Slack, webhooks) with
  a 300-runs/hour aggregate cap. That is a different surface from the
  consumer Keeper chat; the design does not depend on it.

### 1.3 DIRECTOR (ChatGPT) — the analysis/final-check lane

Researched (OpenAI Help Center, "Scheduled tasks in ChatGPT", current):

- Scheduled Tasks are created/edited/paused/deleted FROM CHAT or the
  Scheduled page. Each run starts a FRESH conversation with account
  memory, custom instructions, and connected apps — a task CANNOT
  continue the Director's main chat thread, and a task inside a
  project cannot read that project's files: everything the run needs
  must be in the prompt, memory, or apps.
- Fastest recurring cadence: ONCE PER HOUR (paid plans), exact times.
  Active-task limits by plan: Free/Go 3, Plus 5, Business/Edu 10,
  Pro/Enterprise 15. The Director's two hourly tasks sit far inside
  any paid cap — headroom exists for additional specialized tasks.
- Event-triggered tasks (ChatGPT Work) can react to Gmail / Slack /
  GitHub activity: up to 30 runs/hour and 720/day across all event
  tasks.
- Runs consume plan usage; unattended tasks may AUTO-PAUSE after a
  period of inactivity (a liveness check is part of the design, §6).
- Not supported in tasks: voice chats, custom GPTs, locked chats.
- Best practice (OpenAI guidance + practitioner consensus): write the
  task prompt as a complete standalone job (trigger / input / output /
  boundary), test the exact prompt in a normal chat first, then
  schedule it; one job per task.

### 1.4 Answers to Ace's three open questions (2026-11-15)

1. "Can the main chat cycle every 15 minutes — has it?" — The main
   chat has no self-cycle; it never did. What cycles INTO it are
   Uni's jobs: the watch every 5 minutes (faster than the remembered
   15), execution every 30, heartbeat every 30. The 15-minute rhythm
   Ace remembers was the Keeper's old mail cycle — retired
   2026-11-15 because that channel carried zero messages in its
   entire history (his lane is GitHub).
2. "I prompted the Director to cycle in the chat box outside the
   automations — was that happening?" — Evidence: today's Director
   output arrived on a roughly hourly cadence consistent with the
   two automations, and FOUR+ of today's rulings reached Uni only
   because Ace personally pasted them (07:26 full EXE, 18:59 EXE,
   19:58 MODE D, 20:49 package). A ChatGPT chat does not run by
   itself between prompts, and a scheduled task runs in a FRESH
   conversation — so there is no self-running cycle inside the
   Director's chat box. What existed: the two automations (mailed
   rulings) + Ace prompting in chat and hand-carrying the output.
   That hand-carrying is a transport defect (§6.1) — the Grand
   Workflow already rules Ace is never the courier; this design
   closes the gap by contract (§4.3).
3. "Can the Keeper's automations be modified from the chat box, and
   skills attached just by prompting?" — YES on both counts for
   Grok: automations are created and changed by asking in chat, and
   skills are created in conversation ("save this as my … skill")
   and attachable to automations. Same convenience as the Director's
   side. §5 carries the ready-to-paste texts.

## 2. DESIGN PRINCIPLES

- PHASE-STAGGER, DON'T SPEED UP. Every platform's floor is hourly
  per slot; productivity comes from offsetting the slots so a
  handoff never waits a full cycle, and from every lane arriving at
  its gate with its work already done (§37).
- STATE LIVES IN THE RECORD, NOT IN A CHAT. All three platforms run
  automations as fresh conversations. The shared memory of the
  system is GitHub (PRs, comments, director-reports/, watermarks)
  plus Director mail. Every lane's instructions begin by reading the
  record and end by writing to it.
- ONE JOB PER SLOT, STATED AS A COMPLETE CONTRACT (the ChatGPT
  best-practice pattern, applied to all three platforms).
- ACE IS NEVER THE COURIER (§6.1). A ruling that only exists inside
  a chat box does not exist for the pipeline.
- THE GATES NEVER MOVE: §32 freshness, hard CI gate, Keeper terminal
  stamp before merge, Director final check after; merged never means
  certified; PLAN and CODE belts separate in every count.
- §39 TWO-NO-RESULT and the two-cycle cap bind every lane: a slot
  that produces nothing twice gets its instructions fixed, not a
  third identical run.

## 3. THE PHASE GRID (one hour, America/Chicago)

    :00  DIRECTOR slot A — FINAL CHECK + ANALYSIS (existing task)
    :05  UNI watch fold (continuous, every 5 min)
    :15  KEEPER slot A — FAST CONFIRM (gate-ready packages)
    :30  DIRECTOR slot B — DELTA + REVIEW-QUEUE CLEARANCE (existing)
    :45  KEEPER slot B — DEEP PASS (trailing certs, audits, SWAT prep)
    Uni EXECUTION cycles every 30 min; MAIN SESSION merges on wake.

Gate latency under the grid (AMENDED per Director review,
2026-11-15: a PLANNING ESTIMATE, never a guarantee): a package Uni
posts at T is seen by a Keeper slot within 30 minutes (slots at
:15/:45), folded by Uni's watch within 5 minutes of the stamp,
merged by the main session on that wake, and final-checked by the
Director within 30 minutes (:00/:30) — package → final check
≈ 65 minutes estimated worst case, ≈ 35 typical, against the
multi-hour stalls of the unstaggered era. ACTUAL gate latency is
computed from published timestamps (Sleep Mode Workflow §8) and
reported split by owner; if an automation is delayed or fails, the
FALLBACK OWNER is Uni's watch, which surfaces the silence at the
next fold and the item waits at its gate — never silently lost.
Uni-side gate latency target stays ≈ 0: packages are posted
complete (campaign + CI + checkpoint) BEFORE a slot is asked to
look.

## 4. LANE CONTRACTS

### 4.1 Uni (no fleet change required)

- Watch (5m) and execution (30m) bodies already carry the Grand
  Workflow duties, the digest mail path, and §39. The execution
  cycle additionally: (a) checks the phase grid — if a Keeper or
  Director slot fired since the last cycle, fold its output before
  starting new work; (b) posts gate-ready packages EARLY in the
  hour so they land before :15/:45, not after.
- Main session: merges and campaign launches stay main-session acts;
  in sleep mode the night pipeline (Sleep Mode Workflow) governs.

### 4.2 Keeper — two skills + two slots (§5 texts)

- SKILL "Keeper Terminal Confirm": the stamp discipline (quiet ×3 +
  exact-head CI + checkpoint package at the final head; pre-stamp vs
  terminal-stamp; §32; merged ≠ certified; PLAN/CODE separation).
- SKILL "Keeper Deep Pass": trailing-certification ledger clearance,
  scoreboard audit against the totals ledger (PLAN 242 / CODE 198),
  reconciliation sweep, SWAT self-audit at transitions.
- SLOT A (:15, hourly) — FAST CONFIRM: read the GitHub record for
  gate-ready packages posted since the last run; stamp or state the
  exact missing evidence; publish the watermark.
- SLOT B (:45, hourly) — DEEP PASS: the Deep Pass skill over the
  whole queue; trailing ledger; publish the watermark.

### 4.3 Director — two existing tasks, instruction upgrades

- Both tasks rewritten in the four-part standalone form (trigger /
  input / output / boundary) with the input defined as the GitHub
  record (DIRECTOR_REVIEW_QUEUE.md + open PRs + watermarks), because
  a task run cannot see the Director's chat thread or project files.
- OUTPUT CONTRACT (the courier fix): every ruling exits by EMAIL to
  Uni and/or a GitHub publication in the same run. A ruling produced
  only inside a chat is out of contract.
- SLOT A (:00) — whole-system final check of everything executed
  since the last check + the full review queue (§38).
- SLOT B (:30) — delta pass: new packages, mail-order rulings,
  question answers (Q-*), SWAT prep at transitions.
- Headroom: the plan cap allows more tasks; two optional additions
  are specced but NOT required — (i) an event-triggered task on
  GitHub activity (Work; reacts within the hour instead of at the
  next slot), (ii) a weekly long-horizon research task feeding the
  Grand Plan. Both are Ace/Director choices, not Uni's.

## 5. READY-TO-PASTE TEXTS

### 5.1 Keeper skill — create in the Grok chat

"Grok, save this as my 'Keeper Terminal Confirm' skill: When asked
to confirm DellMatrix work, verify against the GitHub record only.
A terminal CONFIRM requires ALL of: a quiet full regression x3
terminal GREEN at the exact head, exact-head CI terminal ALL PASS,
and a checkpoint package at that head. Anything less is a pre-stamp
and must be labeled pre-stamp. Never confirm from a summary alone;
read the receipts. Merged never means certified. PLAN-belt and
CODE-belt completions are counted separately and never blended.
Publish every stamp as a PR comment naming the exact head, and
update the Keeper watermark on main."

"Grok, save this as my 'Keeper Deep Pass' skill: On a deep pass,
work the whole DellMatrix queue on GitHub: clear trailing
second-certifications (currently DD-18 and Q-DD42.1), audit the
scoreboard against the dual-belt totals ledger (PLAN denominator
242, CODE denominator 198; the documented COMPLETE baseline is
35 of 182 per Manifest Sitting #002 — never the retired 39), sweep
for disagreements with the Director's published positions and
reconcile through the shared record, and at a wake/sleep transition
produce your own SWAT audit (challenge your confirmations, coverage,
stale stamps, missed failures, gate decisions). Publish findings to
the GitHub record and the watermark."

### 5.2 Keeper slots — create in the Grok chat

"Create an automation named 'Keeper Fast Confirm' that runs every
hour at :15 America/Chicago, using the Keeper Terminal Confirm
skill: check the DellMatrix GitHub repository for gate-ready
packages Uni posted since your last run; for each, issue a terminal
CONFIRM or state the exact missing evidence; publish stamps as PR
comments and update the Keeper watermark; if nothing is ripe, say
so briefly and stop."

"Create an automation named 'Keeper Deep Pass' that runs every
hour at :45 America/Chicago, using the Keeper Deep Pass skill over
the DellMatrix GitHub record; publish the results to the record and
the watermark."

(If the editor does not offer an hourly trigger on Ace's plan, the
fallback is two daily-anchored automations edited to hourly in the
Automations page, or Ace prompts the Keeper manually at the phase
marks — the grid degrades gracefully, the contracts do not change.)

### 5.3 Director tasks — edit in the ChatGPT chat box

For each existing task, replace the instruction with the four-part
form; example for slot A:

"TRIGGER: every hour at :00 America/Chicago. INPUT: the DellMatrix
GitHub record — director-reports/DIRECTOR_REVIEW_QUEUE.md, all open
PRs and their latest comments, the Keeper watermark, and Uni's
state file summaries linked from the queue. OUTPUT: one email to
Uni containing a disposition for EVERY queued item (confirm, hold,
correction-required, insufficient-evidence, or question answers),
each naming its PR and exact head; plus the whole-system final
check of everything merged since your last run. BOUNDARY: read-only
on code; no ruling is complete until it has left by email or a
GitHub publication in this same run; if an item lacks evidence, say
exactly what is missing instead of guessing."

Slot B mirrors it with TRIGGER :30 and INPUT narrowed to items
changed since slot A.

## 6. FAILURE MODES AND COUNTERS

6.1 COURIER FAILURE (observed 2026-11-15, four+ Ace relays):
countered by §4.3's output contract — rulings exit by mail/GitHub
in the run that makes them.
6.2 FRESH-CONVERSATION AMNESIA (all three platforms): countered by
§2 — state lives in the record; every slot's input IS the record.
6.3 AUTO-PAUSE (ChatGPT tasks pause after inactivity): the weekly
Manifest Sitting includes a one-line liveness check of both
authorities' slots (last output timestamp vs expectation); a silent
slot is surfaced to Ace the same day, not discovered weeks later.
6.4 HOURLY FLOOR (Keeper/Director cannot cycle faster): accepted
and designed around via the phase grid; Uni's 5-minute watch is the
system's fastest loop and carries all folding.
6.5 OBSERVATION WITHOUT PRODUCTION (the 2026-11-14 night): §39
binds every lane; the execution cycle's portable-work duty and the
night pipeline's production quotas (Sleep Mode Workflow §8) are the
standing counters; the sitting grades the week on objects closed,
not cycles run.
6.6 GATE COLLISION (two lanes acting on one item at once): items
carry one owner at a time in the queue record; merges and
state-sharing campaigns stay serial (§37).

## 7. ACE'S SETUP CHECKLIST (the only human steps)

1. Keeper chat: paste the two skill texts (§5.1), then the two slot
   texts (§5.2); confirm the editor shows an hourly trigger at :15
   and :45 America/Chicago.
2. Director chat: edit both existing tasks to the §5.3 form;
   confirm task notifications include EMAIL.
3. Tell Uni "cycle system live" — Uni then updates the execution
   cycle body with the phase-grid check (§4.1) and records the
   go-live in the state file. Nothing else changes hands.

## 8. WHAT THIS DESIGN DOES NOT DO

It creates no new authority, dissolves no gate, and moves no merge
off the main session. It does not promise the 2x sleep ratchet —
that is certified from measured output against the wake baseline
(2026-11-15 wake: PLAN 10 / CODE 6), per the Director's GAP note.
It does not count cycles, folds, or reviews as completed objects;
the belts count objects, as always.

— Uni Ω, 2026-11-15. Sources: OpenAI Help Center (Scheduled tasks
in ChatGPT); xAI announcements + Grok Automations/Skills coverage
(Jul–Nov 2026); docs.x.ai (Grok Bot skills and routines); Anthropic
scheduled-task documentation (for the platform comparison in §1.1's
research file); Uni's live cron fleet listing, 2026-11-15 23:09 CST.

## 9. AUTHORITY REVIEW — AMENDMENTS (2026-11-15, folded same night)

KEEPER ACK (23:16 CST): design accepted as PLAN-belt DESIGN; the
grid, the two skills, state-in-the-record, and the no-courier rule
accepted; this seat operates under existing contracts until Ace
completes §7 and says "cycle system live".

DIRECTOR REVIEW (23:19 CST): DESIGN — CONDITIONAL CONFIRM. The
architecture is accepted with five amendments, all incorporated:

A1. DIRECTOR DUTY SEPARATION. Verified defect: both Director tasks
    (:00 Final Review, :30 Delta Review) are ACTIVE but currently
    carry IDENTICAL 3,108-character instructions anchored to
    November 9 — unspecialized, risking duplicate analysis and
    stale decisions. Under §4.3/§5.3 the :00 task owns whole-system
    review, merged-main evidence, outstanding decisions, and
    Director SWAT; the :30 task owns changed PRs, new questions,
    immediate dispositions, and gate preparation. Neither repeats
    resolved work.
A2. KEEPER HOURLY IS ACCOUNT-DEPENDENT. xAI's July announcement
    does not list hourly scheduling; a later third-party account
    test reports it. The :15/:45 grid stands as the design, but
    §7 step 1 is a VERIFICATION (confirm the hourly trigger in
    Ace's Grok editor), not an assumption. Grok Bot routines are a
    distinct product and are not the fallback.
A3. LATENCY IS MEASURED, NOT PROMISED. §3 amended above: 65
    minutes is a planning estimate; actual latency is computed from
    timestamps; Uni's watch is the fallback owner for a delayed or
    failed automation.
A4. TRANSPORT IS VERIFIABLE. Each substantive Director ruling
    produces an email identifier, recipient, and delivery result;
    Uni acknowledges receipt in GitHub. A completed automation run
    alone does not prove delivery. No-change runs send no duplicate
    mail (consistent with §39 material-only writes).
A5. MEASUREMENT AND SWAT. The waste metric distinguishes useful
    monitoring from wasted execution cycles; PLAN and CODE
    productivity ratios are computed separately; Director, Keeper,
    and Uni each complete independent SWAT audits at BOTH
    transitions (already law in the Sleep Mode Workflow §7, as
    amended).

ACTIVATION STANDARD (Director, binding): before the system is
marked LIVE, prove ONE complete end-to-end transaction — Uni
evidence → Keeper stamp → Director ruling → verified email → Uni
action → merge → Director final check — recording exact timestamps,
PR identity, gate receipts, and the owner of every handoff. Then
run the same test with ONE missing or failed gate: it must stop
safely without silently losing work. Until both proofs exist, the
status is DESIGN, not LIVE. A targeted event-triggered Director
task (GitHub/Gmail/Slack activity) may be considered only after the
basic pipeline demonstrates reliable delivery.

STATUS AFTER REVIEW: DESIGN (conditionally confirmed). Ace's move:
approve the amended design and issue "cycle system live" — which
authorizes updating the Director task instructions and coordinating
Keeper and Uni activation, without changing established merge
authority.
