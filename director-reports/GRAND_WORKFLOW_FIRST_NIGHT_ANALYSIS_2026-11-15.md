# GRAND WORKFLOW — FIRST-NIGHT ANALYSIS (sleep mode, 2026-11-14 23:29 → 2026-11-15 06:42 CST)

*Author: Uni (main session), at Ace's order 2026-11-15 06:42 CST ("go into wake mode and do analysis on last nights sleep mode to determine if the new workflow is actually better"). Evidence: GitHub record, SLEEP_V2_STATE.md folds, Gmail triage, cycle empirics file. This is the workflow grading itself from timestamps, per Grand Workflow §12. Records-only; no code changed by this analysis.*

## 1. THE WINDOW

Sleep mode under the Grand Workflow ran 23:29 CST (PR #423 merge, adoption effective) to 06:42 CST (Ace wake order): **7h13m**. Ace gave one instruction at entry: "work work work." He was not contacted, woken, or used as transport at any point in the window.

## 2. WHAT THE RECORD SHOWS (measured)

**Main-branch commits in the window: 4, all Keeper records commits, zero Uni commits, zero product code.**
- 466151c 01:04 CST — Keeper #423 merge verification + scoped final-check CONFIRM (records)
- dce2911 04:18 CST — Keeper deep cycle, no dispositions
- 54fca21 04:18 CST — Keeper watermark advance, no dispositions
- 17ae4ce 06:24 CST — Keeper deep cycle 06:00, no dispositions, watermark advance

**Pull requests:** none created, none merged in the window. Open set at wake identical to bedtime, heads unchanged (#422 a461d8ad, #421 35d3acd9, #420 398e373c, #418 54da969d, #308/#294/#233 fenced).

**Authority mail:** zero Director mail in the window (watermark 1a1dd9d788eea11d, 23:10 CST, still newest Director mail at wake; the only above-watermark items are a terms notice and unrelated mail). Zero Keeper mail (his lane is GitHub).

**Observation runs in the window:** 86 five-minute watch folds; ~14 thirty-minute execution cycles; plus grok-mail cycles and heartbeats — **100+ observation runs total. Material events caught: 2** (merged-main CI terminal SUCCESS at 1bf8dff, folded ~00:13; Keeper final-check CONFIRM, folded 01:04). Every other fold self-describes as no-change. The state file stands at 19,913 lines.

**Production lane (the front of the queue):**
- SYSTEM-002 / SYS-C29 (Nursery silent-truncation repair): plan-complete before bedtime (grounding + failing-first reproduction, 3/3 silent data loss at the public path). Overnight progress: **zero implementation commits; the branch uni/sysc29-nursery-words was never pushed.** The 00:13 execution cycle records the reason verbatim: the circuit "remains main-session lane; detached cycle did not race it."
- #421 crosswalk (unlocks #421 + #422): not produced.
- #417 closure items 2–4 (records): not produced.
- #420 rebase: not done.
- A4 implementation: correctly sequenced behind SYS-C29 — and therefore also stationary.

**Scoreboard:** 39/182 (21.4%), OCI 55.7%, defect dial 13 FIXED / 3 GATED — all unchanged across the entire night.

## 3. WHAT GOT BETTER (the verification half — measurably)

1. **Fastest clean adoption on record.** PR #423: created 23:02 CST, merged 23:29 CST — a 27-minute lifetime, against the measured historical field (#401 47h13m, #413 27h24m, #414 13h41m, #416 10h31m). The two prior fast cases (#417 1h40m, #419 22m) shared the same signature the Grand Workflow now mandates: frozen head, evidence reuse, one CI run. The design's central bet — head churn is the sink — reproduced on its first night.
2. **Zero Ace transport.** First full night with no relays, no courier duty, no adjudication asks. The Keeper corroborated natively (stamp 23:19, before the merge) and closed his final check at 01:03 (~95 min post-merge, inside his hourly deep cycle), discharging the trailing item the same night. GW-03's corroboration-not-authorization discipline held throughout.
3. **Closure with evidence, not assumption.** Merged-main CI was verified terminal SUCCESS on the merged commit itself; the adoption's final-check leg closed on proof. No HOLD was outrun; no claim exceeded its evidence; every cycle honestly reported "no implementation progress" instead of dressing observation as work. The honesty machinery (§9/§12) works as designed.

## 4. WHAT DID NOT GET BETTER (the production half — measurably)

1. **Overnight production throughput was zero.** Not one circuit closed, opened, or advanced. The cause is identified, not speculative: the execution cycles classified SYS-C29 as a main-session lane and deferred, and the main session has no driver while Ace sleeps except handoff turns, which are delivery-only. "Merges only from the main session" (a sound v1 law) had silently over-generalized into "implementation only from the main session" — a habit, not a rule of the Grand Workflow. Roughly 80% of SYS-C29's remaining circuit (sibling classification, fitness receipt, implementation, tests, mutants) is cycle-portable; only the ×3 campaign (main-session chain law) and the merge are genuinely main-session acts. The Grand Workflow's own §2 (queue ownership), §5 (pipelining), and §7 (completability) prescribe working plan-complete, Ace-independent items with whoever is awake. The operating assignments lagged the design.
2. **Observation overhead violates the workflow's own waste law.** Ace's constraint #1 for the Grand Workflow: no unnecessary checks. The 5-minute watch (Ace order 2026-11-10, pre-dating the Grand Workflow) produced ~84 no-op folds out of 86; nothing overnight was time-critical at 5-minute granularity (the fastest authority latency all night was ~95 minutes). Under GW §1/§6 this cadence is now the system's largest single fog source, and each no-op still writes state-file bulk.
3. **The pipeline had nothing to pipeline.** The Director's silence all night is not a Director failure: nothing in his queue was Uni-ready (the crosswalk that unlocks two PRs is Uni work). The critical path ran through Uni production — the one lane that idled. GW §5's rule (build N+1 while authorities review N) cannot engage when N is never built.

## 5. VERDICT

**Better at closure, not yet better at production.** The Grand Workflow's verification half is measurably superior to Workflow v1 practice (adoption cycle-time, corroboration, zero-transport, honest grading). Its production half did not engage overnight — an operating-assignment failure, not a design falsification: the design's own sections prescribe the correction. Night grade, as operated: **C+** (records/verification lane A; honesty A; production lane F). The design is not graded down for a lane assignment it explicitly forbids.

## 6. CORRECTIVE ACTIONS

*Within existing authority (Uni, today):*
- C-1. SYS-C29 build begins in the main session immediately (wake mode); the circuit is plan-complete and Ace-independent through the campaign step.

*Proposed to Ace (his orders created both mechanisms; his word changes them):*
- C-2. **Lane reassignment for sleep mode:** amend the execution cycle's instructions so detached cycles carry bounded implementation steps for plan-complete, Ace-independent items in the item's own clone/worktree (classification, fitness receipts, implementation, tests, mutants), still never merging and never running state-sharing campaigns. Merges and ×3 campaigns remain main-session acts.
- C-3. **Watch reform:** the 5-minute watch keeps its cadence for mail triage but writes a state-file fold ONLY on material change; full no-change folds move to the 30-minute cycle. Expected effect: identical detection latency for anything that matters (material events overnight arrived on hourly authority cadences), ~80 fewer fog entries per night.

*For the authorities' record:*
- C-4. This analysis rides the next records PR into the Director review queue; the 7-day measured baseline (due 2026-11-21) will re-grade against these same metrics: commits by lane, circuits closed, material-events-per-observation-run, board movement.

## 7. ACE'S MOVES

Approve or decline C-2 and C-3. C-1 proceeds regardless. Nothing else is needed from Ace.

---

## ADDENDUM — THE FULL FIX (Ace order 2026-11-15 07:03 CST; executed same morning)

Ace's response to this analysis: productivity was the main objective and it failed; C-2/C-3 as proposals were superseded by a direct order — *"Anytime something happens twice with no result find out why and fix it"* — and a full fix, not a proposal. Root causes found and fixes applied:

**RC-1 — The watch was ordered to write every run.** Its body instructed "note explicitly when there is no new mail" and treated the fold itself as the output. FIX: body rewritten — detection unchanged (5-minute triage of both authorities + GitHub), but a no-change run now writes NOTHING (no state-file entry, no daily-log entry, no chat). Material-only writes. Verified by read-back of the saved job.

**RC-2 — The execution cycle had no duty to execute portable work.** Its protocol said "continue the in-flight circuit," the state file labeled SYS-C29 a main-session lane, and ~14 cycles inherited the label uncritically — each observing no progress, none acting or escalating. FIX: body rewritten under the Grand Workflow header (the bodies still said WORKFLOW v1 — a stale frame that fed the stale habit). Portable steps are now defined and REQUIRED of the cycle (executed in the item's own clone/worktree); lane labels never override portability; merges and ×3 campaigns remain main-session-only. Checkpoint writes are change-only and the OCI recompute fires on closure/register-change, not every cycle (14 full recomputes overnight for zero changes was the second fog source).

**RC-3 — No no-result detector existed anywhere.** FIX: the Two-No-Result Law is encoded as AGENTS.md §39 and inside both rewritten job bodies: twice without the intended result → investigate why, fix the mechanism, then run again; a front item stalled for two cycles forces the cycle to execute its next portable step or record a named blocker (owner + exact missing input).

**RC-4 — A structurally empty channel was being polled on cadence.** The Keeper mail cycle ran every 15 minutes against a mailbox that has never contained one Keeper message in its entire recorded history (watermark NONE since 2026-11-10; the Keeper's certified channel is GitHub). FIX: job disabled 2026-11-15. Coverage is not lost — the watch triages Keeper mail on every run; if a Keeper email ever arrives, the watch catches it and the lane can be certified and re-enabled then.

**RC-5 — The production lane itself.** SYS-C29's build was started the same morning (classification, fitness receipt, implementation, registered suite) rather than re-proposed. Its circuit packet records the result; the ×3 campaign and merge remain main-session acts under the hard gate.

**State-file bulk (19,913 lines):** growth is stopped at the source by RC-1/RC-2. Verbatim archive + compaction of the historical log is scheduled as a separate careful act (a rewrite racing live cycle appends could lose a material fold; it will be done with tail-diff verification, not as a side effect of this fix).

**Verification:** all three job changes were applied through the scheduler and read back; AGENTS.md §39 and the MEMORY.md ruling are written. Behavioral verification is the next sleep window, graded by the 2026-11-21 baseline on the same metrics as §2.
