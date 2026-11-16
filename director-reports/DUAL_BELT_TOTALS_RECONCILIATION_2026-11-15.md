# DUAL-BELT TOTALS LEDGER — ROW-LEVEL RECONCILIATION — 2026-11-15

Requested by the Director (EXE 2026-11-15, relayed by Ace 19:06 CST):
a row-level reproducible check of the ledger's totals before his
acceptance and the Keeper's terminal records stamp. The check
re-derives every figure independently from the PR #424 crosswalk and
the ledger CSV (dual_belt_totals_ledger_2026-11-15.csv, this PR) and
compares. Method: script parse of both sources; no hand counts.

## RESULT — ALL CHECKS PASS

```
PASS  crosswalk CARRIED rows: got 175, expected 175
PASS  crosswalk CARRIED-SANDBOXED rows: got 3, expected 3
PASS  crosswalk REMOVED rows: got 4, expected 4
PASS  crosswalk MWL COMPLETE: got 35, expected 35
PASS  ledger total rows: got 242, expected 242
PASS  ledger basis rows: got 224, expected 224
PASS  ledger appendix rows: got 18, expected 18
PASS  duplicate ids: got 0, expected 0
PASS  sandboxed MWL-#180/181/182 in basis: got 0, expected 0
PASS  removed MWL-#171/177/178/179 in basis: got 0, expected 0
PASS  basis CODE class: got 188, expected 188
PASS  basis PLAN class: got 17, expected 17
PASS  basis RECORDS class: got 19, expected 19
PASS  basis COMPLETE: got 37, expected 37
PASS  basis PARTIAL: got 62, expected 62
PASS  basis OPEN: got 122, expected 122
PASS  basis GATED: got 3, expected 3
NOTE  the 37 register-COMPLETE split by class: {'CODE': 32, 'RECORDS': 5} — register COMPLETE is a register state, NOT belt completion; belt completion is counted only under Ace's 2026-11-15 model from its adoption (today's movement: PLAN 10 / CODE 4).
PASS  appendix CODE class: got 10, expected 10
NOTE  CODE denominator derivation: 188 basis CODE + 10 appendix CODE (FI-003, FI-004, FI-007, FI-010, C5R.1, C5R.2, C5R.3, C5R.4, C5R.5, C5R.6) = 198.
PASS  PLAN denominator: got 242, expected 242
PASS  CODE denominator: got 198, expected 198
NOTE  PR #421 HOLD: untouched by this ledger; the ledger classifies the basis the crosswalk reconciled and retires nothing.
RECONCILIATION: ALL CHECKS PASS
```

## THE DERIVATIONS, IN WORDS

- **224** = 175 MWL rows carried active by the crosswalk + 49 unified
  additions (section 4 register 22, Far Stratum section 7 net 22,
  section 5 sequence 5). The 3 sandboxed MWL rows (#180-182) and the 4
  proven duplicates (#171, #177, #178, #179) are verified ABSENT from
  the basis (checks above) — present only in the ledger's Appendix B.
- **188 CODE + 17 PLAN + 19 RECORDS = 224.** Classification rules and
  per-row judgment notes are in the ledger itself (section 2 and the
  table's Note column).
- **PLAN denominator 242** = 224 basis + 18 appendix objects
  (FI-001..FI-012, C5R.1-C5R.6). Every object passes plan completion,
  so every object is on the PLAN belt.
- **CODE denominator 198** = 188 basis CODE-class + 10 appendix
  CODE-class (FI-003, FI-004, FI-007, FI-010, C5R.1, C5R.2, C5R.3,
  C5R.4, C5R.5, C5R.6). The 8 remaining appendix objects are PLAN or
  RECORDS class and never enter the code queue.
- **37 register-COMPLETE does NOT mean 37 code-complete.** The 37
  split 32 CODE-class + 5 RECORDS-class, and register COMPLETE is a
  register state carried from the MWL render — not a belt completion.
  Belt completions are counted only under Ace's 2026-11-15 model from
  its adoption: today's movement is PLAN 10 / CODE 4, nothing more.
- **PR #421's HOLD is untouched.** This ledger classifies the basis
  the crosswalk reconciled; it retires nothing and replaces no
  scoreboard.

Reproduction: parse MWL_UNIFIED_CROSSWALK_2026-11-15.md section 1
(disposition prefixes) and the CSV in this PR; count by register,
belt_class, and status fields.
