# README COUNT POINTER — RECEIPTS for PR #301 head 38b3780 (2026-11-05)

Re-presenting PR #301 at its UNCHANGED head
38b378034c4a207532de5956ba0d4484a57325f6 with the receipts
the Director's review (2026-11-05 12:08 CST, Gmail
1a1ace6218f657da; INSUFFICIENT_EVIDENCE, HOLD #301)
required. PR #301 itself is not amended; it remains HELD
under AGENTS.md s.32 pending the Director's re-check.

## 1. Terminal exact-head smoke

Form smoke run 42079792281 at head
38b378034c4a207532de5956ba0d4484a57325f6: status completed,
conclusion **success** (verified via gh at the run record;
it was IN_PROGRESS at the Director's inspection, PASS at
12:17 CST). Python package run 42079792114: SUCCESS
(Director-verified in the review).

## 2. Bounded grep/scan — no remaining numeric suite-count claim

Full preserved output: scan_output.txt (this directory).
Method: enumerate every README line containing "suite" and
every occurrence of the historical literals 230/236/237/238
at the exact head, and read every digit-bearing line.

- Lines containing "suite": exactly 5 — L568 and L607 (the
  two pointer lines; NO numeral attached to the registry
  claim), L575/L590 (generic "suites", no number), L620 (a
  shell comment "# full suite", no number).
- Literals 230 / 236 / 237 / 238: ABSENT everywhere.
- All digit-bearing lines classified: section numbers, the
  Dell registry table (00–99), dates, commit anchors, the
  9,900 symbiosis pair count, Python 3.10+, example I/O.
  None asserts a suite count.

**VERDICT: no present-tense numeric suite-count claim
remains in README at this head.**

## 3. Pointer resolution

At head 38b3780: `python3 -c "from form.regress import
LIST; print(len(LIST))"` → **238**. LIST (form/regress.py,
line 38) is the registry the harness executes (its own
contract: LIST + discovered form/**/*_test.py, deduped,
must cover every intended entry). README's pointer names
exactly this authority ("count = length of LIST"), and it
resolves.

## Disposition

Receipts supplied; PR #301 stays HELD. Confirmation and
any merge authorization remain the Director's; nothing
here treats CI green as certification.
