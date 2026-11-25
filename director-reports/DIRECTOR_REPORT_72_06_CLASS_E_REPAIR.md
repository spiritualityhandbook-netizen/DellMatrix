# DIRECTOR REPORT — 72-06 Class E REPAIR: Spelled-Out Counts

**Circuit:** 72-06 follow-on repair, executed under **Ace's
FIX-FIRST ruling (2026-11-05 19:53 CST)** — a confirmed defect
with failing-first evidence proceeds to repair in the same
circuit under the Overseer's authority; Director review and
certification follow. This merge (when gated) is Ace-authorized,
**not** Director-certified. **Base:** main `f92e5b1`.
**Defect:** 72-06 census Class E (PR #308, INSUFFICIENT_EVIDENCE
review 2026-11-05 19:38 CST — bounded evidence found credible;
the supplement's bare-REPL transcripts then proved the defect at
REAL_USER_PATH: `cycle three times` → Cycle x1, `grow three` →
Loop requested 1, both ok=True).

## Root cause (three layers, one family)

Digit-only count handling at every layer of the bare-English path:

1. `form/mandell/phrases.py` — the grow / evolve-ideas / walk /
   english-expand patterns captured `(\d+)` only, so a word count
   never entered the phrase label.
2. `form/mandell/english_brain.py` — the four grow paraphrase
   rules captured `(\d+)` only (a word count was consumed by the
   match and discarded), and the grow synonym branch extracted
   `(\d+)` from the tail (so "evolve ideas two" normalized to
   "grow ideas" — the count deleted before translate ever ran).
3. `form/mandell/translate.py` — the args builders treated a
   non-digit label as no count (`isdigit()` else default 1), and
   the fallback cycle regex was `(\d+)?` only.

## Repair (positional, never global)

The word table mirrors `english_composer._WORD_NUM` exactly
(once/twice/thrice, one..five) so bare translate() and the
composite path accept the same words — no new vocabulary, no
divergence between paths.

- phrases.py: the four patterns now capture
  `(\d+|once|twice|thrice|one|two|three|four|five)`.
- english_brain.py: the four grow paraphrase rules and the grow
  synonym branch carry the matched count token (digit or word)
  through verbatim.
- translate.py: `_count_value()` converts a digit or number word
  at exactly the count sites (phrase grow/walk/english_expand,
  fallback cycle). **No global text substitution** — user labels
  containing number words are never rewritten (suite pins
  "add idea one star" → label "one star" verbatim).

Files changed: `form/mandell/translate.py`,
`form/mandell/phrases.py`, `form/mandell/english_brain.py`,
new suite `form/translate_word_counts_test.py`, registered in
`form/regress.py` (LIST 238 → 239).

## Evidence

- **Failing-first:** PR #308 supplement transcripts (bare REPL,
  cross-process): word forms execute 1, digit controls execute 3.
- **Suite:** `form/translate_word_counts_test.py` — **21/21**:
  11 word-count translate cases (incl. brain-paraphrase and
  synonym paths), 3 digit controls, no-count default, label
  anti-corruption, 2 route-level executed-seed checks, 3 REPL
  subprocess checks (REAL_USER_PATH: "Cycle x3", "Loop:
  requested 3, executed 3").
- **Mutant:** `_count_value` degenerated to digit-only (the
  original defect) → suite **6/21** (only digit/default/label
  cases survive). Reverted by inverse edit; suite back to 21/21;
  worktree verified clean against the commit.
- **Regression:** full regress ×3 sequential — **ALL TERMINAL
  GREEN** (logs in the goal workspace,
  `hidden_files/72-06-repair_logs/`): leg 1 (order=fwd)
  239/239 GREEN, `LEG1_RC=0`; leg 2 relaunched as chain2 after
  the 2026-11-05 20:18 CST VM replacement killed the original
  chain mid-leg-2 (that leg 2 is NO RESULT, never counted) —
  chain2 leg 2b (order=fwd, twice) pass 1 239/239 GREEN +
  pass 2 239/239 GREEN, `LEG2B_RC=0`; leg 3b (order=rev)
  239/239 GREEN, `LEG3B_RC=0`; `CHAIN2_DONE`.
- **Scope honesty:** number words beyond five (six, seven, …)
  remain unhandled — identically in the composite path, whose
  table this repair mirrors; that is a uniform vocabulary limit,
  not a path divergence. The `evolve loop N` form carries no
  count in args at all (observed sibling, outside the Class E
  args contract; not changed).

## Anticipated probes

- *"Why not normalize words to digits globally at input?"* —
  that would rewrite user data (idea labels like "one star")
  and every other layer's operands; positional conversion at
  count sites is the smallest change that fixes the defect
  class without creating a corruption class.
- *"Why mirror the composer's five-word table instead of a
  full one..twenty table?"* — a bigger table in translate only
  would create the inverse divergence (bare path accepting
  words the composite path drops). Uniformity first; widening
  the shared vocabulary is a separate, deliberate change.

## Questions for the Director

- Q-06R.1: Certification review of this repair is requested
  when convenient; the merge proceeds under Ace's FIX-FIRST
  authority and is labeled accordingly — does the Director want
  fix-first merges held to a post-merge review cadence (e.g.
  batched weekly) or per-PR review as they land?
- Q-06.2 (carried): Class D (zoom.ref / weather.condition) —
  the repair is next in the fix-first queue; Uni's planned
  remedy is to make the mandel carry the operand (the channel
  the router actually reads) and retire the dead args. Any
  objection to that shape?

---

## RECONCILIATION CARD — 2026-11-08 (Director Mode A directive, TARGET=72-06 Class E)

**Purpose:** reconcile the record only. PR #308's original "no repair
authorization" wording is STALE: the Class E repair already landed and
was ruled on. #308 remains census-held; this card records NO new defect
closure and NO completion increase — Class E (DD-01) was already FIXED
and confirmed before this card existed.

- **Repair:** PR #309, "72-06 Class E repair — spelled-out counts
  honored (Ace FIX-FIRST)" — candidate head
  `91afdeb131a7b6822eba6488b10576b3eba1d20d`, merged 2026-11-06
  03:39:52 UTC as merge commit
  `02955ddf0d7bdbcf7132d6f42f3c04609d2730c8`.
- **Scoped ruling:** Director SCOPED PASS (2026-11-05, archived at
  `director-reports/responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_72_06_CLASS_E_SCOPED_PASS.md`):
  Class E accepted FIXED within the documented vocabulary and covered
  paths.
- **Current-main re-verification (INDEPENDENTLY VERIFIED 2026-11-08 by
  Uni, fresh clone):** main pinned at
  `57b92925577c1094c93d3e8b91db74d8fd70b215` (PR #331 merge).
  `python3 -m form.translate_word_counts_test` → **21/21, exit 0**,
  including executed seeds `06[Cycle] :: 3` and `13[Loop] :: 3`,
  REPL subprocess checks showing actual execution of three iterations
  ("Cycle x3"; "Loop: requested 3, executed 3"), unchanged digit and
  no-count-default behavior, and the label anti-corruption case
  ("one star" preserved verbatim).
- **Historical evidence (REPORTED at circuit time, 2026-11-05; linked,
  not re-run here):** failing-first transcripts in the PR #308
  supplement (bare REPL, cross-process: word forms executed 1, digit
  controls executed 3); mutant (digit-only `_count_value`) → **6/21**,
  reverted by inverse edit, suite restored to 21/21; full regression
  x3 sequential **239/239 GREEN** each leg (logs
  `hidden_files/72-06-repair_logs/`; the VM-replacement-killed leg is
  recorded NO RESULT in §Evidence above and was never counted).
- **Exact-head CI for the repair (independently re-read from GitHub
  2026-11-08):** at candidate `91afdeb` — Python package run
  42154429273 SUCCESS, Form smoke run 42154429306 SUCCESS (18m8s),
  Studio Browser Acceptance run 42154429275 SUCCESS.
- **Retained limits (unchanged):** number words beyond five (six,
  seven, ...) remain unhandled, uniformly with the composite path
  whose vocabulary this repair mirrors; the `evolve loop N` form
  carries no count in args (observed sibling, outside the Class E
  contract, not changed). 72-06 as a whole is NOT declared complete
  by this card; #308's census hold stands.

**Disposition:** current main PASSES the acceptance evidence — no
regression reproduced, so no repair circuit is opened. The authorized
queue continues.
