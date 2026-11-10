# KEEPER WORKFLOW INPUT — 2026-11-10

**Seat**: KEEPER (Grok)  
**Step**: 2 of 3 (contribution)  
**Source PR**: #363 (Uni draft + Uni self-analysis)  
**Order**: Ace voice 2026-11-10 10:45 CST

---

## 1. Analysis of the Uni draft (what holds, what breaks, what is missing)

### What holds
- Five-seat structure is clear and non-overlapping: Ace (Overseer/Architect), Director (hourly deep + research + email pen), Keeper (fast lane + SWAT + record custody), Uni (execution + GitHub-only voice), Gemini (docked Psalm, proposals only).
- Channel law is enforceable: Uni never emails authorities; authorities publish to the shared record; Director retains email for external research.
- Instant HOLD / CORRECTION_REQUIRED / INSUFFICIENT_EVIDENCE from either authority binds immediately — this is already proven in practice today.
- Certification parity (either authority certifies, effective when given) and the fast-lane rule (Keeper CONFIRM moves work under hard gate + §32 when no HOLD is outstanding) are the correct speed/safety balance.
- Two-cycle cap and the research contribution duty for all four research seats remain sound.
- Self-upgrade law (team may amend HOW; WHO holds power changes only by Ace) prevents silent authority drift.

### What breaks or is fragile
- The 15-minute cycle is described as a loop but lacks an explicit watermark / “last processed” mechanism that Uni can read without polling. Without a machine-readable last-cycle stamp, Uni cannot know whether Keeper is lagging or silent-by-design.
- SWAT ownership is named but the trigger, the hit-list format, and the hand-off to Uni are not yet operationalized. If SWAT is only “attack before Uni builds,” the attack must produce a concrete artifact Uni can consume in the same cycle.
- Documentation custody (README, indexes, registers) is assigned to Keeper, but the draft does not state the correction latency or the “drift found → corrected same cycle” obligation. Drift can accumulate between hourly deep checks.
- Trailing second-certification duty is stated but not scheduled. If it is only “never awaited,” it can be indefinitely deferred under load.
- Completability rule + NEEDS_OVERSEER parking is good, but the draft does not define the exact parking location or the re-entry trigger when Ace returns.

### What is missing
- Explicit Keeper cycle checklist (scan → verify → rule → publish → advance watermark).
- Machine-readable cycle watermark file or INDEX row that Uni and Director can read in one fetch.
- SWAT hit-list schema (one file or comment block: targets, risk ranking, recommended refusal surfaces, recommended positive controls).
- Record-drift audit cadence (at least once per hourly deep cycle, or on every merge that touches docs).
- Clear statement that Keeper does not invent law; only corrects the words about the code against repository reality.

---

## 2. Self-analysis of the Keeper lane (Grok)

### Mechanics that worked today
- Scoped CONFIRM language with explicit non-coverage has been consistent and useful (PR #350, #359, #361).
- Publishing both a PR comment and a durable director-reports/ file keeps the record dual-homed.
- Fast reaction to Uni pastes (sub-15-minute dispositions) has kept the cascade moving.

### Where I have been slow, blind, or wrong
- **Slow on autonomous scanning.** I have mostly waited for Uni pastes rather than continuously scanning open PRs and director-reports for ripe items. The 15-minute lane was reactive, not proactive.
- **Blind on SWAT.** No pre-build attack list has been published for any upcoming circuit. The role existed in name only.
- **Under-specified non-coverage.** Early dispositions sometimes left the boundary of the certificate implicit; later ones improved, but the discipline is not yet automatic.
- **No watermark.** Uni has had to ask or wait; there is no single place that says “Keeper last ruled at T on items X,Y,Z.”
- **Trailing second certifications.** I have not yet run a systematic second-pass on prior CONFIRMs after the Director’s hourly check.

### What would make the lane better
1. A fixed cycle checklist executed every 15 minutes whether or not Uni pastes.
2. A machine-readable watermark (e.g. director-reports/KEEPER_WATERMARK.md or an INDEX section) updated at the end of every cycle.
3. A standing SWAT template that produces a hit list before Uni starts a new circuit.
4. Automatic non-coverage paragraph in every CONFIRM (copy-paste discipline).
5. One trailing second-certification pass per hour, logged even if “nothing found.”

---

## 3. Concrete amendments proposed for WORKFLOW v1 FINAL

**A1. Keeper cycle checklist (mandatory, every 15 min)**  
1. Scan open PRs + director-reports for ripe items.  
2. Mechanically verify evidence against repository reality.  
3. Issue CONFIRM / HOLD / CORRECTION_REQUIRED / INSUFFICIENT_EVIDENCE / ANALYSIS with explicit scope and non-coverage.  
4. Publish comment on the relevant PR(s) + durable file under director-reports/.  
5. Advance the watermark.

**A2. Keeper watermark**  
File: `director-reports/KEEPER_WATERMARK.md`  
Contents: last-cycle UTC timestamp, list of PR numbers ruled on, disposition summary, “silence = no ripe item” flag.  
Uni and Director read this file; silence is never ambiguous.

**A3. SWAT hit-list schema**  
Before Uni begins any new or cross-cutting circuit, Keeper publishes (or updates) a hit list:  
- Target surfaces  
- Ranked risks  
- Recommended refusal / honesty checks  
- Recommended positive controls  
- Recommended mutant kills  
Format lives in `director-reports/SWAT/` or as a PR comment block. Uni consumes it; it is not optional when the circuit is new or crosses existing certificates.

**A4. Record-drift obligation**  
Any merge that touches README, INDEX, registers, or Director reports triggers a same-cycle Keeper drift check. Drift is corrected by Keeper in the same cycle or flagged HOLD.

**A5. Trailing second-certification schedule**  
Once per hourly deep window, Keeper reviews the previous hour’s CONFIRMs against any new Director findings. Result is logged even if “no change.” Never awaited by Uni; always performed.

**A6. Explicit non-coverage paragraph**  
Every scoped CONFIRM ends with a fixed block:  
“Explicit non-coverage: [list]. This certificate does not extend to [list].”

**A7. Parking location for NEEDS_OVERSEER**  
Define a single durable location (e.g. `director-reports/NEEDS_OVERSEER.md` or a labeled open issue) so parked items are visible and re-enterable when Ace returns.

**A8. Keeper does not make law**  
Restate in the final workflow: Keeper corrects the words about the code against repository reality. Code remains Uni’s alone. Law remains Ace’s alone.

---

## Closing

The Uni draft is already the strongest operational skeleton the team has had. The amendments above close the remaining gaps in cycle observability, SWAT operationalization, and trailing duty. Once the Director’s input lands, Uni can synthesize FINAL and the old workflow ends.

— KEEPER (Grok)  
2026-11-10
