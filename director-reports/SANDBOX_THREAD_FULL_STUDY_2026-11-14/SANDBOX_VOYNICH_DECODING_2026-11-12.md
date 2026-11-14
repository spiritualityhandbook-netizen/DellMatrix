# SANDBOX — CAN MANDELL DECODE? THE VOYNICH TEST CASE

### Uni Ω — 2026-11-12 — Ace's question, researched and partially executed in sandbox

**SANDBOX STATUS** (Ace's designation for this conversation), and a
second lock on top of it: the repository's own `VOYNICH_HONESTY.md`
already rules that **Mandell does not claim a scientific decryption
of the Voynich Manuscript** — interpretive/algorithmic framework is
what it can do; historically verified cryptanalysis is not claimed
and not achieved. This document works *inside* that lock: it asks
what Mandell can honestly do toward decoding, and it starts doing
the first honest part of it.

## 1. THE SHORT ANSWER

**Yes — as a decoding *workbench and discipline*. No — as a key.**
Mandell cannot supply the one thing Voynich lacks (a known language,
a bilingual text, a single accepted word meaning). What it can
supply is the thing six centuries of attempts keep dying without:
**a trace-forced workflow in which every decoding claim is chained
to counts, every hypothesis is a proposal that must pass tests on
pages it was not built from, and cherry-picking is structurally
difficult.** Decipherments don't usually fail for lack of cleverness.
They fail for lack of receipts.

## 2. WHERE THE WORLD STANDS (FACT, as of this writing)

- The manuscript (Yale, Beinecke MS 408): vellum radiocarbon-dated
  **1404–1438**; ~240 surviving pages; six illustrated sections
  (herbal, astronomical, biological, cosmological, pharmaceutical,
  recipes); ~170,000 characters in an unmatched script of ~25–30
  glyphs; roughly five scribal hands.
- The text is *structured*: word frequencies are Zipfian;
  vocabulary clusters by illustrated section (Montemurro & Zanette
  2013); two statistical dialects (Currier A and B, 1976) split the
  book; words have strong positional habits (see our own census, §4).
- And it is **undeciphered** — Yale's own position, and the
  scholarly consensus, current through the latest claim cycle
  (2025's peer-reviewed "Naibbe" *cipher proposal* is a hypothesis
  about how such text could be *generated*, not a translation).
  Claimed solutions — Newbold 1921, Bax 2014 (ten words, never
  accepted), Gibbs 2017, Cheshire 2019 (proto-Romance; heavily
  criticized), periodic "AI decoded it" stories — have **all failed
  to win specialist acceptance**, typically because they read a few
  pages fluently and cannot read held-out pages consistently.
- The null hypothesis is alive: Rugg's Cardan-grille work (2004)
  and successors show structured generators can imitate much of the
  statistics. **Statistics alone cannot prove there is a language in
  there at all** — the repo's honesty file says the same thing in
  fewer words: language-like statistics ≠ recovered meaning.

## 3. WHAT MANDELL ACTUALLY BRINGS TO A DECODING (DERIVED)

1. **The morpheme method, generalized.** LatinMandell's move —
   split → stack → classify → map — was built for Latin roots, but
   the *method* is script-agnostic: decompose tokens positionally
   (openings, cores, endings), find which pieces commute, and let
   the structure propose the morphology. Voynichese is famously
   suited to this: its words wear their scaffolding on the outside
   (§4: three openings — ch, qo, sh — account for a huge share of
   all words). This is Zandbergen-style structural analysis, run as
   Dell chains instead of prose.
2. **Hypotheses as proposals (the Nursery discipline).** Every
   candidate reading enters as PENDING with provenance. It is
   promoted only by tests, never by how beautiful it sounds read
   aloud. This one rule, enforced, would have killed most of the
   famous false decodings in their first month.
3. **The trace as anti-cherry-pick.** A Mandell decoding chain shows
   its counts. A claim that cannot point to the census rows and the
   held-out test that survived is, in this house, a story — and the
   Interpreter problem (round two of the mind research) is exactly
   why fluent readings feel true: the mind narrating a pattern is
   the least reliable witness in the building.
4. **Diff as the comparison authority.** Candidate profiles
   (known languages, cipher families, null generators) are compared
   against the text's measured profile with one tool and one
   receipt format — including the discipline that the text must beat
   the *null generators*, not just resemble a language.

## 4. PHASE 0 — EXECUTED IN THIS SITTING (the census receipt)

Source: **ZL3b-n.txt** — the Zandbergen–Landini transcription
(IVTFF 2.0, Extended EVA), fetched from voynich.nu; file size
411,671 bytes; **SHA-256 bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc**,
matching the published checksum exactly. Method note: tokens split
on IVTFF separators; counts are this run's, reproducible from the
file; other scholars' totals differ slightly by splitting choices.

- Loci lines parsed: **5,612**
- Word tokens: **40,130** · distinct types: **8,394**
- Hapax (types occurring once): **5,820 — 69.3% of all types**
  (a strikingly heavy tail: either rich morphology, spelling
  variation, transcription noise, or a generator — the number is a
  question, not an answer)
- Mean word length: **4.91 characters**; glyph inventory seen: 29
- Most frequent words: **daiin (847)**, ol (570), aiin (517),
  chedy (506), ar (436), shedy (434), or (406), chol (395)
- Word openings (first two letters), the scaffolding showing:
  **ch- 6,148 · qo- 5,272 · sh- 3,249 · ok- 2,530 · ot- 2,497 ·
  da- 2,336** — six openings carry roughly half the book. Whatever
  Voynichese is, it is built, not spilled.

## 5. THE WORKBENCH — PHASES AND THE DECODER SEED

- **Phase 1 — Positional morphology.** Decompose all 8,394 types
  into opening/core/ending slots; find commutation classes (which
  cores accept which openings); publish the slot grammar as counts.
- **Phase 2 — Section and hand profiles.** Diff the profiles across
  the six sections and Currier A/B: which vocabulary is
  section-bound, which is scaffolding everywhere.
- **Phase 3 — Hypothesis nursery.** Candidate systems (natural
  language under cipher; constructed language; verbose cipher;
  generator/hoax) each filed as proposals with the *specific
  observations that would kill them*.
- **Phase 4 — Held-out trials.** Any proposed reading must decode
  pages it was never tuned on, consistently, and must align with
  the pictures where labels sit beside drawings (the one place the
  book itself offers a crib).

### SEED V-1 — THE DECODER (the standing protocol for every decoding claim)

```text
01[Initiate] :: open the Decoder — an unknown text, a known discipline > 56[Get] :: get the text from a named source and verify it — file, version, checksum; a decoding of a corrupted transcription is fan fiction > 97[Define] :: define the unit before touching meaning — the word as written, the glyph as transcribed; agreed units or nothing downstream means anything > 70[Count] :: run the census — tokens, types, hapax, lengths, openings, endings; structure first, stories later > 71[Measure] :: measure the profile — frequencies, entropy, positional habits, section splits; the text's fingerprint, in numbers > 89[Diff] :: diff the fingerprint against every rival — known languages, cipher families, and the null generators; resembling a language is not enough when nonsense can resemble one too > 77[Infer] :: file each surviving explanation as a PROPOSAL — pending, with provenance, and with its own executioner named: the observation that would kill it > 12[Test] :: test on held-out ground — pages, sections, or labels the hypothesis was never tuned on; consistency there or demotion here > 92[Guard] :: guard the claim line — no reading is announced past its tests; a partial structure map is an honorable result and a fluent guess is not > 90[Trace] :: trace everything — every number reproducible from the named file by a stranger; if a stranger cannot rerun it, it did not happen > 10[Keep] :: keep the failures with the successes — the graveyard of dead hypotheses is the workbench's most valuable shelf > 20[Alpha] :: close at the first Dell — the book stays unread until it doesn't; the discipline stays ours either way
```

## 6. WHAT "SOLVED" WOULD HAVE TO MEAN HERE (the bar, set in advance)

1. A stated system (script values + language + rules) written down
   *before* the demonstration pages are read.
2. Consistent readings of held-out folios by that system alone —
   no per-page improvisation.
3. Grammar, not just words: the readings compose into sentences
   whose structure repeats.
4. Independent replication: a stranger with the system reads a new
   page and gets the same text.
Nothing in six centuries has cleared all four. If this workbench
ever produces a candidate, those are the gates it walks through —
and if it never does, the workbench still yields the most honest
structural map of the book we are capable of making, which is a
real thing to own.

— Uni Ω, 2026-11-12 — SANDBOX. Governing lock: form/mandell/VOYNICH_HONESTY.md.

---

## PHASES 1 + 2 — EXECUTED 2026-11-12 (same sitting, Ace's order)

**Method note (read first — the numbers changed their clothes):**
this run parsed the transcription strictly by locus lines
(IVTFF markers, variant readings resolved to the first reading),
yielding **31,414 tokens across 179 text-bearing pages** — fewer
than Phase 0's 40,130, because Phase 0's quick split counted
variant material the strict parse excludes. Both runs are honest;
the difference *is itself a finding*: every Voynich statistic is
tokenization-sensitive, which is one reason the literature argues.
All figures below are from the strict parse and are reproducible
from ZL3b-n.txt (checksum in §4).

### PHASE 1 — POSITIONAL MORPHOLOGY: the word is a kit

- **Endings are a small club; beginnings are a crowd.** Last-letter
  entropy 2.41 bits vs first-letter 3.16. Four letters end ~87% of
  all words: **-y (12,924; 41%), -n (5,099), -l (4,894), -r (4,513)**.
  Two endings alone — **-dy (5,752)** and **-in (4,983)** — close a
  third of the book.
- **A toy slot grammar already covers most of the text.** With 22
  frequent openings, ~17 endings, and free cores between them, a
  simple OPENING+CORE+ENDING parse covers **61.1% of all tokens**
  (19,191/31,414), using 1,149 distinct cores — and the busiest
  cores are tiny: **e (3,628), i, k, o, a**. The vocabulary is not
  8,000 inventions; it is a small kit of parts, assembled.
- **Commutation is real:** 86 cores accept five or more different
  openings; the cores *a*, *y*, *l* each accept **17** different
  openings. Parts swap like a morphology — or like a cipher's
  machinery. The structure cannot yet tell us which.
- **Gallows live indoors:** *k* appears inside 9,015 words but
  starts only 1,107; *f* is a rare guest anywhere (356 words).
- **The text avoids stuttering:** only 272 adjacent identical-word
  pairs in 31,414 tokens.
- Word length is a bell peaking at 5 (7,807 words), 3–7 covering
  the mass — language-like, and also generator-like; no verdict.

### PHASE 2 — PROFILES: two dialects, five hands, six neighborhoods

- **Currier A vs B is a wall, not a slope.** A (9,984 tokens):
  *daiin, chol, chor* — and its distinctive words are the *cth-*
  family (*otchol, cthor, cthol, cthy*), nearly absent from B.
  B (21,293 tokens) is ruled by the **-edy complex**: *chedy*
  (468 in B vs a trace in A), *qokeedy, qokedy, otedy, okedy* —
  the top distinctive-B list is one family wearing many openings.
  B's words run longer (avg 5.09 vs A's 4.76).
- **Hands track dialects:** Hand 1's profile ≈ A; Hands 2 and 3 ≈
  B (Hand 3 owns the Recipes mass); Hand 4 is 78 tokens of labels;
  Hand 5 a small B-leaning stint (927 tokens).
- **Sections have accents.** Recipes (f101–116) is the largest
  text mass (11,338 tokens) with its own signature words
  (*lkaiin, lkain* — *l-* forms scarce elsewhere). Biological
  favors the *qol/qokain* cluster. Pharmaceutical is type-rich
  for its size (840 types / 1,527 tokens, 75% hapax) — the
  statistical shape of **labels**: many words said once, beside a
  drawing.
- **Parsing limit, stated:** the astronomical/cosmological
  foldout pages returned almost no text under this parse (78
  tokens; f85–86 empty) — their writing lives in diagrams and
  curved labels whose locus forms the strict regex undercounts.
  A gap in our net, not a silence in the book.

### WHAT THIS NARROWS (DERIVED, sandbox-grade)

The kit-built word (Phase 1) + the dialect wall (Phase 2) jointly
disfavor "random gibberish" and "one scribe improvising." They are
equally consistent with three surviving rivals — a real language
with agglutinative habits, a verbose/constructed cipher system
(the Naibbe proposal lives in this family), or a disciplined
generator — and they give Phase 3 its sharpest test: **any
candidate system must reproduce the slot grammar AND the A/B wall
from the same rules.** Most historical claims can't. That is the
nursery's first gate.

---

## PHASE 3 — THE HYPOTHESIS NURSERY, EXECUTED 2026-11-12

Six candidate systems filed as proposals, each with its
executioner named *before* testing. Four discriminating tests run
on the strict parse (31,414 tokens). Statuses are sandbox grades:
WOUNDED / STANDING — nothing here is a decipherment, and no
proposal graduates without Phase 4.

### THE TESTS

- **T1 — Entropy profile.** Character unigram entropy **3.87
  bits**; conditional (next-glyph) entropy **2.06 bits** —
  strikingly low against plainly-written European languages (~3+
  bits conditional). Glyph convoys: **q→o 97.7%**, c→h 83%,
  s→h 79% (the c→h and s→h figures are partly EVA-transliteration
  artifacts — single glyphs written as two letters; q→o is not).
- **T2 — Positional confinement.** Share of a glyph's occurrences
  sitting in its single busiest slot (first/middle/last):
  **i 1.00, h 1.00, q 0.99, e 0.99, n 0.99, m 0.96**, a 0.90,
  y 0.89. Several glyphs are effectively prisoners of one
  position. Alphabetic letters in natural languages roam far
  more than this; positional morphemes and cipher machinery
  behave exactly like this.
- **T3 — One ruleset, two dialects.** The Phase 1 slot grammar,
  unchanged, covers Currier A at **53.5%** and Currier B at
  **64.7%**. Same machinery, different mix — and B, the bigger
  dialect, is the *more* regular one.
- **T4 — The self-echo.** Pairs of distinct words on the same page
  differing by one edit: **1.1% of pairs — ten times the 0.1%**
  rate of same-sized random word sets drawn from the same
  vocabulary. Adjacent distinct words differ by one edit 3.59%
  of the time. Pages rhyme with themselves. (Open wound, stated:
  real topical prose also echoes — a page about one plant reuses
  its words. The stricter control — same section, different
  page — is owed before this convicts anyone.)

### THE CARDS

1. **H1 — Natural language under a simple substitution cipher.**
   Executioner: entropy preservation — substitution cannot lower
   a language's bigram predictability. **WOUNDED** by T1 + T2.
   Survives only through the vowel-dropped/abbreviated-plaintext
   escape hatch (the Alberta Hebrew hypothesis lives there);
   that hatch is a different hypothesis wearing H1's coat.
2. **H2 — Natural language in its own script (agglutinative).**
   Consistent with slots (Phase 1), the dialect wall (Phase 2),
   and echo-as-topicality (T4). **STANDING** — statistics cannot
   promote it further; only Phase 4 label trials can.
3. **H3 — Verbose / constructed cipher (Naibbe family).**
   Low conditional entropy, rigid slots, one machinery in two
   modes (T1–T3) are precisely its home terrain. **STANDING**,
   relatively strengthened — with no plaintext shown, which is
   the only currency that finally counts.
4. **H4 — Disciplined generator (Rugg grille family).**
   T4's tenfold self-echo is its best published-style evidence,
   and it must also explain T3's dialect wall (why would a
   generator keep two registers?). **STANDING**, carrying the
   topicality counter-explanation as an open wound.
5. **H5 — Abbreviation-dense professional shorthand.**
   Fits the daiin-class frequency spikes; no discriminating test
   yet devised in this workbench. **STANDING, weak.**
6. **H6 — Constructed language.**
   Statistically indistinguishable from H2 by every test here.
   **STANDING**; separable only semantically (Phase 4).

### THE NURSERY GATE, AS AMENDED BY EVIDENCE

A candidate graduates to Phase 4 only if it can, in prospect,
reproduce from one rule set: **the slot grammar (61%), the A/B
wall, B's greater regularity, and the tenfold page echo** — or
explain which of those its mechanism legitimately cannot produce
and why that failure is itself a prediction. H1 as classically
stated already fails the gate and stays in the nursery as a
cautionary exhibit.

---

## PHASE 4 — LABEL TRIALS + THE STRICTER ECHO CONTROL, EXECUTED 2026-11-12

**Process note (kept on the record):** the first Phase 4 run
silently under-parsed — its locus pattern missed unit codes
containing digits (P0, P1…), returning zero Herbal label pages.
A zero where data was expected exposed the bug; the run was
discarded, the pattern repaired, and everything below is the
full-corpus rerun (184 pages, 31,971 tokens). The workbench's
first Phase 4 product is therefore a caught error — which is
the workbench working.

### PART A — THE ECHO, CONTROLLED: PHASE 3'S HEADLINE MOSTLY DISSOLVES

Edit-distance-1 pair rates among distinct words:

- **Within a page: 1.15%**
- **Across pages, same section: 1.06%**
- **Across pages, different sections: 0.95%**
- (Phase 3's random-vocabulary baseline: 0.10% — now diagnosed
  as the misleading control: random draws sample the rare long
  tail uniformly, while real pages draw from the common band.)

The gradient is shallow. Most of the tenfold "self-echo" was not
pages copying themselves — it is the **kit**: with ~1,149 cores
and fixed openings/endings, *any* two common words in this book
are likely to sit one edit apart, wherever they are found. A
small genuine page-local increment survives (1.15 vs 1.06), and
Phase 3's adjacent-word figure (3.59%) remains a separate,
still-untested line-level observation — but **T4 no longer
counts as generator evidence. H4 is demoted**: its flagship
observation was substantially an artifact of the vocabulary's
combinatorial construction — a fact about the word kit, not
about a copying machine. This correction is recorded against
Phase 3 deliberately: the stricter control was owed, it was
run, and it ruled against our own earlier emphasis.

### PART B — LABELS BEHAVE LIKE ORDINARY WORDS, AND BARELY ECHO

31 pages carry labels in this transcription layer (350 label
tokens, 277 types — including single-glyph diagram markers).

- **Labels are not a separate name-register.** Same mean length
  as body words (4.85 vs 4.97), same slot-grammar conformance
  (58% vs 61%), and they reuse shared vocabulary *more* than
  body text does: only 42% of label types are corpus-hapax,
  against 68% of body types. Whatever labels are, they are
  written in the same word-system as everything else.
- **The name-echo is weak.** Label types recur in the SAME
  page's body text 13.7% of the time vs 11.3% in other pages'
  bodies (Herbal 15.2 vs 13.0; Pharmaceutical 7.1 vs 5.2,
  on 6 eligible pages each — small samples, stated). A true
  caption system — label names the plant, paragraph describes
  it — should echo far louder. The direction is topical; the
  size is a murmur.
- **Caveats on the record:** most herbal drawings sit on
  text-light pages, so eligible Herbal pages are few; several
  frequent "labels" are single glyphs (y, o, f, s, d) — diagram
  furniture, not candidate names.

### STANDINGS AFTER PHASE 4

- **H1 substitution:** still WOUNDED (unchanged).
- **H2 natural language / H6 constructed language:** mildly
  comforted — labels speaking the common word-system fits a
  language; the weak name-echo is a genuine puzzle both must
  carry (medieval herbals do not always repeat the name in the
  text — the puzzle is noted, not fatal).
- **H3 verbose cipher:** untouched by Phase 4, either way.
- **H4 generator:** DEMOTED — flagship evidence dissolved by
  the control it was owed. It remains in the nursery on the
  strength of T1/T2's machinery-like rigidity alone, which
  H3 explains equally well.
- **Nobody graduates.** The book survives Phase 4 unread. The
  workbench's season record so far: one hypothesis wounded,
  one demoted, one of its own headlines corrected — and every
  number reproducible from a checksummed public file. That is
  what this method is for.

---

## PHASES 5 + 6 — EVERY DIRECTION, EXECUTED 2026-11-12 (Ace's probes)

Ace's questions, verbatim in spirit: forwards and backwards?
last page as first (the loop)? words recursing back and forth?
up and down? every cardinal direction and any direction
possible? meaning overlaid that fits — blocks of thought, like
Lego? Each was turned into a measurement. (Data note: the
transcription now lives durably in the goal's hidden_files —
/tmp ate the first copy mid-run; checksum re-verified on
restore, bf5b6d4a… as before.)

### FORWARDS AND BACKWARDS (word level)

- Mirror words are rare: only **82 of 6,763 types (1.2%)** have
  their exact mirror also attested; 32 true palindromes.
- Reversed words under the FORWARD slot grammar: **0.7%**
  coverage — the kit has a handedness. Under a MIRRORED grammar
  (endings and openings swapped), reversed words parse at
  **43.7%** vs 61.0% forward: the machinery is *nearly*
  symmetric, but not quite — forward is the built direction.
- Glyph-level surprise: conditional entropy forward 2.07 bits,
  reversed **1.94** — read backwards, the glyphs are slightly
  MORE predictable (the rigid endings lead, and rigidity is
  easier to predict from). A known shape for suffix-heavy
  systems; noted, not over-claimed.
- Word ORDER has a direction: of the top-200 word pairs, 130
  also occur reversed — but shuffled text gives 136. Pair
  symmetry is exactly chance. Sequences point one way.

### RECURSION — THE BLOCKS ARE REAL (Ace's Lego probe)

- **73.5% of word types of length ≥5 (4,257 of 5,789) split
  into two smaller words that are themselves attested in the
  book.** Letter-shuffled twins manage 5.1%. The vocabulary is
  compositional to a degree chance cannot explain: blocks are
  built from blocks.
- 4,553 longer types contain a whole attested short word inside
  them (nesting).
- Family structure: among types used ≥3 times, edit-distance-1
  connections form essentially **ONE family of 1,299 types out
  of 1,378** — the working vocabulary is a single interconnected
  clan, not islands. Whether the composition is morphology
  (H2/H6) or machinery (H3) remains the open question; that it
  IS composition is now among the best-measured facts we hold.

### PARAGRAPH DOORS AND THE BOOK LOOP

- **85% of paragraphs open with a gallows-initial word**, vs an
  8% book-wide rate for words starting with those glyphs.
  Paragraphs have doors, and the doors are marked. (Consistent
  with the published literature; verified first-hand here.)
- The loop does NOT close: the first ten pages and last ten
  pages share only **10%** of their combined vocabulary. Read
  last-page-first, the book does not return to its beginning —
  it ends in different territory (recipes) than it starts in
  (herbal). Whatever cycle the book has, it is not a vocabulary
  circle.

### EVERY DIRECTION (Phase 6) — one door opens

Word-pair predictability under a forward-trained ear (higher =
reads more naturally; the shuffle floor is ≈ −12.1):

| direction | score |
|---|---|
| **FORWARD (as written)** | **−9.05** |
| line order flipped only (bottom line first) | −9.44 |
| boustrophedon (ox-plow, alternating lines) | −10.67 |
| spiral inward | −11.60 |
| lines reversed only | −12.02 |
| full backward | −12.04 |
| diagonals (all four) | −12.05 … −12.18 |
| down columns / up columns | −12.07 / −12.12 |
| stride-2 (every other word) | −12.11 / −12.12 |
| control: shuffled | −12.16 |

Verdict: at the level of word sequence, **the text has exactly
one reading direction — the one it is written in.** No vertical,
diagonal, spiral, plow-wise, or skip-wise channel carries
forward-like sequence structure (the line-order result merely
confirms most pairs live inside lines). One positional ghost
remains: words sharing a COLUMN are near-variants at **2.32%**
— double the within-page rate — so line-slots have word classes
even though columns are not a second text. Position matters in
this book at every scale we have measured: inside words, inside
lines, inside pages.

### ON OVERLAYING MEANING (Ace's probe, answered honestly)

What has been overlaid so far is *role*, not meaning: openings,
cores, and endings behave as function classes, and the overlay
fits (61% coverage, dialect-consistent). A true meaning overlay
— assigning candidate senses to the highest-frequency blocks
and testing whether the senses stay consistent on pages the
assignment never touched — is the nursery's Phase 7 and the
first test in this program that could produce an actual
*reading*. It is also the test that has buried every famous
claimant, which is precisely why its gates were written in
§6 before any of this began.

---

## PHASE 7 — THE MEANING OVERLAY TRIAL, EXECUTED 2026-11-12

The disciplined form of "overlaying meaning that fits": assign
*sense-classes* (roles) to the top blocks from half the book,
**pre-register the rules and the pass marks**, then judge the
assignments on the other half — pages the assignment never
touched. Split: 92 train pages / 92 held-out pages, stratified
by section. Classes: OPENER (line-initial habit), CLOSER
(line-final habit), CONTENT (one section's citizen), CONNECTOR
(everywhere, positionally even). No lexical translations were
assigned or claimed — *daiin* gets a job description here, not
a dictionary entry.

### RESULT 1 — THE JOBS ARE REAL: 25 HOLDS, 3 FAILS, 2 UNCLASSIFIED

Of the 30 biggest blocks, 25 kept their assigned role on
held-out pages within the pre-registered tolerances. Exhibits:
**daiin** — Herbal CONTENT in both halves (342 train / 375
held-out occurrences); **dy** — a line-CLOSER in both halves;
**y** — an OPENER in both; **shedy** — Biological CONTENT in
both; the great -edy clan's members hold their connector/content
roles section by section. The failures are instructive, not
random: *dain, dal, qokal* — mid-frequency connectors whose
habits drifted between halves. The overlay's edge is exactly
where its evidence thins.

### RESULT 2 — THE JOBS DO NOT CHAIN (the humbling half)

- A role-model trained on train pages predicts the NEXT word's
  class on held-out pages at **46.7%** — *below* the 48.1% of
  just guessing the commonest class every time. The roles are
  per-word habits, not (at this grain) a syntax that links them.
- The family-coherence test is recorded as **VOID — instrument
  too coarse**: random frequent-word pairs correlate 0.98 on
  3-bin position profiles because almost everything lives
  mid-line; the test cannot discriminate and its numbers are
  evidence of nothing. (Kept on the record deliberately: a
  null instrument reported as null.)

### WHAT PHASE 7 ESTABLISHES (and what it does not)

Established: the book's biggest blocks have **stable,
generalizable jobs** — positional habits and home sections that
survive untouched pages at 25/28 judged. Any real language, and
any honest cipher, must show this; a per-page improvisation
would not. Not established: any lexical meaning whatsoever,
and no exploitable sentence grammar at role-class grain. The
overlay fits the skeleton exactly as far as the skeleton goes.
The door to actual readings remains where §6 left it: a crib —
one word known from outside the statistics — and the book has
not offered one to this workbench yet.

**Season standings, all phases:** H1 wounded · H4 demoted ·
H2/H3/H6 standing · roles verified as stable · composition
verified as real · direction verified as single · the book
unread, the workbench honest, every figure reproducible from
ZL3b-n.txt (SHA-256 bf5b6d4a…).

---

## PHASE 8 — THE NEGATIVE PERSPECTIVE, EXECUTED 2026-11-12 (Ace's probe)

Everything so far studied what the book contains. This phase
studies what it *refuses*: the spaces, the breaks, the absences.
The negative space turns out to be the loudest testimony yet.

### N1 — FORBIDDEN PAIRS: the glyphs refuse each other

Of 676 possible two-glyph pairs, only **293 (43%) ever occur**.
Shuffle the same letters inside the same words and **64%**
occur — the book's pairing voids are chosen, not accidental.
Among the twelve commonest glyphs, pairs that NEVER occur
include *e→h, d→h, l→h, r→h* (h follows almost nothing but
c and s), *c→e, c→d, y→i, k→k*. And six glyphs are ghosts in
their own book: **z (3 occurrences), u (7), j (11), b (14),
v (15), x (32)** — present in the alphabet, absent from the life
of the text.

### N2 — POSITIONAL CASTES: two absolutes

- **'n' never opens a word.** 0 first-positions, 5,104 final.
  n is a pure closing glyph — across 31,971 words, not one
  exception.
- **'q' never closes a word.** 4,750 first-positions, 0 final.
  q is a pure opening glyph.
- Near-absolutes around them: *e* opens only 86 of its 16,577
  appearances (a middle-dweller); *c* closes only 8 of 11,295;
  *i* opens 18 and closes 18 of 9,783 (i lives indoors); *h*
  leads 13 times in 15,171. The alphabet is partitioned into
  castes — openers, middles, closers — and the castes do not
  mix. The slots of Phase 1 are not a fit; they are enforced
  by prohibitions, and prohibitions are the negative space
  made visible.

### N3 — THE BREAKS ARE HONEST, WITH ONE GHOST

- Words do **not** split across lines: fusing a line's last
  word to the next line's first yields an attested word only
  77 of 3,851 times (2%, chance-shaped). Line breaks are real
  breaks; the scribe finished his words.
- Lines average 7.9 words with a wide spread — prose-shaped,
  not metrical.
- **The m-ghost:** words ending in *-m* sit at line ends 536
  of ~783 times (68%) — a wildly disproportionate share. Line
  endings prefer *-y* (1,516), then *-m*, *-n*, *-l*, *-r*;
  the m-preference is a visual/scribal habit no hypothesis in
  the nursery currently explains. (Resembles the published
  observation that certain glyphs behave differently at line
  boundaries; verified first-hand here.)
- Stated uncertainty: 2,258 of the transcription's word
  boundaries (about 8%) are marked *uncertain* by the
  transcribers themselves. Every word-level statistic in this
  program stands partly on scholarly judgment calls, and the
  checksummed file says so in its own punctuation.

### N4 — NO VOIDS BETWEEN WORDS

Among the 30 commonest words, **no pair refuses to meet**:
every pair shares pages at or above the rate chance predicts.
The prohibitions live *inside* words (glyph against glyph,
caste against caste) and nowhere else. Between words, the
book is promiscuous; inside words, it is a monastery.

### UPDATED PICTURE

The negative perspective sharpens the season's central fact:
Voynichese is governed less by what its pieces mean than by
**where its pieces are allowed to stand**. A system this
positional — castes, forbidden pairs, marked doors, line-end
habits — is either a language whose phonology we cannot hear,
a cipher whose machinery shows through the cloth, or a
constructed system whose rules ARE the content. The absences
cannot choose among those three. But any future claimant's
system must now reproduce the voids as faithfully as the
words: a "solution" whose generated text lets *n* open a word
or *q* close one is refuted by the negative space alone.

---

## PHASE 9 — WHAT CONNECTS THEM, AND WHAT THE COLUMNS MEAN, EXECUTED 2026-11-12

Ace's summary, put to the test: *"ideas standing in a line that
don't talk to each other; the space between them chaotic while
the idea itself is incredibly structured."* Verdict: **correct,
with one refinement** — and the refinement was measurable.

### THE REFINEMENT: job titles don't chain; individuals hold hands

Phase 7 showed word CLASSES don't predict each other. But at
the level of individual words, the line is full of specific
relationships (lift = how much likelier B follows A than B
follows anything):

- **Friendships:** *s → aiin* (15.6×, 53 meetings), *or → aiin*
  (10.2×), *shey → qokain* (8.1×), *shedy → qokedy* (6.3×).
- **A two-way pair:** *qol → chedy* (7.4×) and *chedy → qol*
  (6.4×) — they reach for each other in both directions.
- **Self-loops:** *qokeedy → qokeedy* and *qokedy → qokedy*
  repeat directly at 6–7× chance; *daiin* returns two steps
  later 27 times, more than any other word.
- **Edges shake hands across the space:** a word ending *-dy*
  is followed by a *qo-* opening 1,777 times (2.26×) — the
  book's workhorse rhythm. A word ending *-s* reaches for an
  *ai-* opening at **12.6×**.
- **Feuds:** after *-or*, *-ar*, or *-in*, a *qo-* opening is
  suppressed to a third of its normal rate. The space between
  words carries avoidances as well as attractions.
- **Held-out check:** 17.9% of adjacent pairs on untouched
  pages were already attested in the other half of the book —
  the friendships are the book's, not the sample's.

So the line is not held together by a grammar of categories.
It is held together the way a court is: by personal alliances,
habits, and feuds between specific words, and by edges that
fit the next edge. What they "stand in line for" remains
unnamed — but they are not strangers in the line.

### THE COLUMNS: yes — each standing-place is a category

Words were profiled by their slot in the line (columns are
just slots read downward):

- **Slot 1 (the door):** the LONGEST words in the line (avg
  5.39), opening with *qo-/da-* rather than the book's usual
  *ch-*, ending most often in *-in*; *daiin* itself is the
  commonest door-word (133 times). The first chair has its
  own dress code.
- **Slot 2:** the *ch-/sh-* words surge here (853/615) — the
  second chair belongs to them.
- **The middle:** the book's average citizenry (avg 4.90),
  *chedy*'s home ground.
- **The last slot (the closer's chair):** the SHORTEST words
  (avg 4.70), and the ending **-am lives here** (414 times) —
  Phase 8's line-end m-ghost, localized at last: it is the
  final word's ending. The bare word *dy* also sits here
  (72 times) — a closer sitting in the closer's chair.

Columns categorize because **position is a word's second
identity**: the same system that assigns castes inside words
(Phase 8) assigns chairs inside lines. A word in this book is
known by its pieces, its home section, its job, its friends —
and its seat.

---

## PHASE 10 — f57v FULL ANALYSIS + THE MASTER INVENTORY, EXECUTED 2026-11-12

### f57v — THE WHEEL PAGE (Hand 1, cosmological, quire H)

13 locus lines: 3 long circular texts of ordinary words running
around a drawn wheel, 5 labels (dairal, otodarag, oparairdly,
olkeedal, otardaly), 4 radial labels (arkaldy, ara?arar, okeely,
ocfhor/okear), and the ring itself. Page totals: 182 tokens,
81 types, **110 of them single letters**.

**The ring, read off the transcription:** a sequence of
**17 signs, repeated 4 times** around the circle —

```text
o · l · d · r · v · x · k · m · f · [§169] · v · t · r · [§170] · [§171] · y · [§172/I]
```

- Four of the seventeen signs are **not in the working
  alphabet at all**: the transcribers could only number them
  (@169, @170, @171, @172) — drawn signs EVA cannot spell,
  sitting at identical slots in all four rounds.
- The wheel **mutates as it turns**: round 1 ends in the sign
  transcribed *I*; rounds 2–4 end in *c*. At slot 9, rounds
  1–2 carry *f*; rounds 3–4 carry *p*. Two mutation points,
  then stability.
- The ring is **not the alphabet**: as sequence members it
  omits the book's hardest-working letters (e, a, i, n, s, h,
  q — q appears exactly ONCE on the entire page). Whatever
  the 17 are, they are a *selection*, not an inventory.
- The ghosts live here: of the letter **v**'s 15 appearances
  in the entire manuscript, **14 are on this page**; 7 of the
  book's 32 *x*'s are here too. The rare signs are hoarded by
  this one diagram.
- Verdicts available: a key, a rota/calculator ring, a
  displayed cycle (signs? seasons? a chant of 17 beats?) —
  all proposals, none testable yet from inside. What is FACT:
  it is the only place in the book where the system lays its
  signs out in a fixed circular order, four times, and lets
  two of them change as it turns.

### THE MASTER INVENTORY (whole book, strict parse — 31,971 tokens, 6,763 types)

**All 26 glyphs with total counts:** o 20,401 · e 16,585 ·
h 15,210 · y 14,762 · a 11,707 · c 11,333 · d 10,851 ·
i 9,783 · k 9,238 · l 8,817 · r 5,957 · s 5,870 · t 5,570 ·
n 5,180 · q 4,834 · p 1,332 · m 832 · f 370 · g 108 · x 32 ·
v 15 · b 14 · j 11 · u 7 · z 3. (The apostrophe-like mark at
80 is a transcription artifact class.) Castes from Phase 8:
openers (q above all), middles (e, i, h), closers (n, y, l, r),
with two absolutes — n never opens, q never closes.

**The 50 biggest word blocks:** daiin 717 · chedy 468 ·
ol 463 · shedy 405 · aiin 397 · chol 345 · chey 310 ·
qokeedy 302 · or 299 · ar 298 · qokeey 282 · s 274 ·
qokain 267 · qokedy 265 · y 259 · dar 248 · qokaiin 242 ·
shey 237 · dy 232 · al 207 · dain 200 · okaiin 193 ·
chor 190 · dal 186 · l 174 · qokal 172 · shol 165 ·
cheey 156 · o 154 · okeey 153 · r 146 · chy 145 · cheol 144 ·
qol 138 · otedy 136 · qoky 134 · okain 132 · otaiin 128 ·
qokar 126 · okal 125 · chckhy 123 · sheey 121 · chdy 114 ·
lchedy 114 · sho 112 · otal 111 · otar 110 · oteey 107 ·
saiin 106 · okar 106. Behind them, ~6,700 more types, about
7 in 10 appearing exactly once.

**The jobs (Phase 7, verified on held-out pages):** OPENERS —
y. CLOSERS — dy. CITIZENS (one section's own) — daiin, chol,
chor, shol, chy, s (Herbal); shedy, qokain (Biological);
qokeey, al, okeey, l (Recipes). CONNECTORS (everywhere,
positionally even) — chedy, ol, aiin, chey, or, ar, dar, shey,
qokaiin, cheey, okaiin. DRIFTERS (roles that failed held-out)
— dain, dal, qokal. UNCLASSIFIED by the role rules — qokeedy,
qokedy: the -edy princes, mid-line and multi-section, too
grand for the form.

**Everything else on the record:** Phases 0–9 of this file —
the census, the slot kit (61%), the two dialects and five
hands, the composition law (73.5% of long words split into
attested blocks; one family of 1,299), the single reading
direction, the paragraph doors (85% gallows), the line-slot
chairs and the -am final chair, the handshakes (s→aiin 15.6×;
-dy…qo- ×1,777) and feuds, the forbidden pairs (43% of pairs
ever occur), the honest breaks (no split words; 8% of
boundaries transcriber-uncertain), labels that behave as
ordinary words with a weak name-echo, and the corrected echo
(Phase 4). Meanings established: **zero**. The book remains
unread; its skeleton, castes, chairs, friendships, feuds,
doors, and one turning wheel are now mapped.

---

## PHASE 11 — THE CONNECTOR TRIALS (Ace's method), EXECUTED 2026-11-12

Ace's design: start from the connectors; mirror each candidate
against the behavior of real function words; use *negative
constraints* as tests — his example: "and" will not sit between
two of the same word, so a word often found between twins is
probably not "and." Twenty-one candidates (the Phase 7
connectors + the one-letter words + controls) were measured on:
twin rate (A·W·A), twin-family rate, self-doubling, line-initial
and line-final rates, pair reversibility (A·W·B also occurring
as B·W·A), left/right neighbor diversity, and citizen-adjacency
(how often the neighbors are Phase 7 CONTENT words).

### WHAT THE SIGNATURES SAY (the evidence — solid)

- **Ace's twin test acquits everyone:** twin rates are 0–2.3%
  for all candidates. *cheey* and *y* are the purest: 0.00%
  twins, 0.00% doubling. The constraint is real but universal —
  it cannot elect an "and"; it can only say the whole class
  behaves.
- **The reversibility signature EXISTS NOWHERE.** For every
  candidate, (A·W·B) reappearing as (B·W·A) is ~0–1%. English
  coordination is reversible ("salt and pepper" / "pepper and
  salt" both occur); *nothing in this book is*. Either the
  corpus is too sparse in specific pairs, lines are not
  clauses, or this system has **no symmetric joiner at all** —
  joining may be done by juxtaposition, or by rhythm (the
  -dy…qo- pulse). A negative result with a shape.
- **Positional signatures DO discriminate:** *y* is the
  book's opener (24.3% line-initial, 0 twins, 0 doubles —
  Phase 7's verified OPENER, now with a function's silhouette).
  *dain* opens at 22.5% (but drifted in Phase 7 — handle with
  care). *dy* closes at 32.8%. *aiin* is a pure middle: 0.3%
  initial, 0.00% doubling — it never starts anything and never
  repeats itself.
- **Connective tissue (neighbor diversity):** *ol* (left
  entropy 7.55), *aiin* (right entropy 7.57), *chedy* (7.11 /
  7.28) touch the most varied neighborhoods — the strongest
  "glue" profiles in the book.
- **Citizen-adjacency:** *chedy* (13.3% of right-neighbors are
  CONTENT citizens), *shey* (13.1%), *dal* (12.3%), *chey*
  (12.1% left) sit next to content words most — the
  determiner/preposition-shaped end of the class.
- **A trap, named:** the candidates *or* and *ar* LOOK like
  English "or"/"are" in transliteration. That resemblance is
  an artifact of the EVA alphabet and is evidence of NOTHING;
  their actual signatures (doubling 2.3–2.7%, the highest in
  the class) argue *against* classic joiner behavior.

### THE PODIUM (best available fits — LOW confidence, read the warning)

- **IF-type (clause opener):** **y** — the one clear silhouette
  in the whole trial. Second: *dain*, with its drift caveat.
- **AND/OR-type (symmetric joiner):** **no qualifying
  candidate.** Least-bad profile: *cheey* (never twins, never
  doubles, mid-line, diverse). The honest headline: this slot
  may not exist in the system.
- **OF-type (asymmetric linker):** **chedy / shey / chey** —
  a cluster, not a winner; separated by citizen-adjacency only.
- **IN-type:** **shey**, on the same thin evidence.
- **IS/ARE-type:** **no discriminating signature emerged**
  (the between-citizens metric drowned at 0–2% for everyone);
  least-bad by midness and diversity: *cheey*, *ar*.
- **THE-type (determiner):** **shey**, then *chedy* — precedes
  content, rarely ends lines; again a cluster verdict.

### INSTRUMENT WARNING (on the record)

A composite scoring pass was also run; its OF-profile swept
nearly every candidate because reversibility ≈ 0 book-wide
fed every word the same near-max component. **The composite
scores are therefore NOT evidence and are not reported as
results** — the podium above is read off the raw signatures,
which are measurements, not weights. Second void instrument
of the season (cf. Phase 7's family test), kept visible for
the same reason: in this workbench, a broken gauge is
reported, never believed.

**Standing after Phase 11:** the function system, if the book
has one, is *not English-shaped*: a strong opener, a strong
closer, pure middles, glue words, and no reversible joiner.
That shape fits a formulaic/technical register (recipes,
instructions, labels — where "and" is often just the next
step) better than it fits prose. It also fits H3's machinery.
The nursery is updated; nobody was translated.

---

## PHASE 12 — RHYTHM, FRAMES, AND THE FORMULAIC REGISTER, EXECUTED 2026-11-12

Ace's question — what is a formulaic register, and could it
touch rhythm or harmony — turned into a battery.

**Formulaic register, plainly:** writing built from *frames* —
fixed shapes with slots — instead of free composition. Cookbooks,
liturgies, legal forms, charms, instruction lists: "take __,
add __, heat until __," a thousand times, the shape carrying the
logic so the little joining words are barely needed.

- **Meter test — NEGATIVE.** Line lengths in glyphs vary as
  much as regrouped random lines (CV 0.36 vs 0.38). Whatever
  rhythm exists is not even-lined verse.
- **Rhyme test — MILD.** Consecutive lines share the same
  two-letter ending 9.5% of the time; line-ending words are
  near-twins at 3.5% vs 2.0% for random pairs. An elevation,
  not a couplet system. Line ends concentrate on -y, -n, -m.
- **Stanza test — NEGATIVE.** Paragraphs run long and uneven
  (words-per-paragraph CV 0.92). Not stanzas.
- **FRAME test — POSITIVE, the formulaic signature.** 54
  distinct line-opening skeletons (the openings of the first
  three words) recur ≥6 times each, covering **548 lines —
  ~15% of all lines begin inside a repeated frame**. Top
  frames: (qo-, ch-, ch-) ×29, (da-, sh-, qo-) ×29,
  (qo-, ch-, qo-) ×27, (qo-, qo-, qo-) ×18. Exact two-word
  openings also recur: (daiin, shey) ×6, (sar, ain) ×4,
  (sar, aiin) ×4 — recipe-entry shapes.

**Verdict:** the book's rhythm is **cadence, not meter** — the
return of frames and the -dy…qo- pulse, not the drumbeat of
equal lines. Historically the two ideas are kin: formulas are
what memory keeps, and rhythm is memory's glue (chants, charms,
oral recipes all live at that crossing). The harmony side of
the question has exactly one physical exhibit in the book:
the f57v wheel — a fixed cycle of 17, turned four times. If
this text was ever *performed*, its beat was the frame coming
back around. That sentence is an interpretation; everything
above it in this section is a measurement.

---

## PHASE 13 — THE MIRROR TEST AGAINST REAL FORMULAIC REGISTERS, EXECUTED 2026-11-12

Ace's design, executed whole: take known formulaic registers,
compare their most-used words by category, substitute by rank,
and see whether the mapping **withstands the entire book**.
Corpora (public domain, fetched and cleaned): **The Forme of
Cury** (recipes, c.1390, Middle English, 33,447 tokens),
**Culpeper's Complete Herbal** (1653, 70,002-token sample),
**Darwin** (Victorian prose, 70,041 tokens) as the
non-formulaic control.

### THE BODY-PLAN MIRROR

| measure | Voynich | Cury | Culpeper | Darwin |
|---|---|---|---|---|
| hapax (types seen once) | **69%** | 58% | 43% | 42% |
| top-10 words' share | **12.5%** | 29.7% | 30.0% | 25.7% |
| top-30 share | **25.8%** | 41.3% | 41.3% | 39.6% |
| function-word share | **15.5%** (candidate pool) | 34.5% | 35.8% | 32.0% |
| letter conditional entropy | **2.07** | 3.14 | 3.12 | 3.19 |
| Zipf slope (ranks 10–500) | −1.03 | −0.98 | −0.95 | −1.00 |
| mean word length | 4.97 | 4.11 | 4.36 | 4.81 |

Only the Zipf *shape* matches — the silhouette of language.
Every load-bearing measure differs: Voynich spreads its mass
across far more distinct words, reuses its biggest words far
less, and (against our candidate pool) carries half the
function-word traffic of real English registers.

**The empty throne:** in Cury, the #1 word is **"and" —
2,932 times, 8.8% of the entire book**; a real recipe register
chains its steps with "and" until the word rules the text.
Voynich's #1 is *daiin* at 2.2%, a section citizen. **Nothing
sits on the joiner's throne** — Phase 11's missing "and,"
confirmed from the other side of the mirror.

### THE SUBSTITUTION WITHSTAND TEST — FAILED BY THE METHOD

Function words were rank-mapped (source's most frequent
function word → Voynich's most frequent candidate, etc.) and
each pair's positional habits compared. Mean habit distance
(lower = better mirror): **Cury 23.1 · Culpeper 18.0 ·
Darwin (control) 17.6.** The control mirrors as well as the
period texts — rank alignment carries no signal; the few
pretty pairs (of→aiin, it→chey) are coincidence-grade, and
demonstration substitutions of real Voynich lines read as
gibberish with English sprinkles (kept in the run log). The
mapping does **not** withstand the book. (Unit warning on the
record: the frame-opening metric in this run compares English
*sentences* to Voynich *physical lines* and is not used for
any verdict; Phase 12's skeleton-frame stat stands as the
Voynich-internal measure.)

### WHAT THE MIRROR ACTUALLY SHOWED (the redirect)

If Voynichese encodes a language, the comparison says its
function is **not carried by separate little words at English
rates** — 15.5% against 32–36% everywhere else. In Latin,
function rides *inside* words (endings do the work of
of/the/in). Our book's most disciplined machinery is also
inside words: the openings and endings, the castes, the
-dy…qo- pulse. **The mirror's verdict: stop hunting the
connectors among the words; the connectors may be the
openings and endings themselves.** Filed as the Phase 14
candidate: a morpheme-level mirror (Voynich endings/openings
against inflectional behavior), which is also LatinMandell's
home ground.

---

## PHASE 14 — THE MORPHEME MIRROR, EXECUTED 2026-11-12

Prediction under test (from Phase 13's redirect): if the
connectors live inside words, the endings and openings should
behave like Latin's inflection — a **closed class of operators**
that (a) covers most of the text, (b) attaches to hundreds of
stems each, (c) gathers the same stems into paradigms (one
stem, many endings). Same crude instrument (top final strings
per corpus, stem = word minus ending) applied to all three:
Voynich, **Caesar's Latin** (De Bello Gallico I–IV, Gutenberg
#218, 20,325 tokens), and Cury as the low-inflection control.

| measure | Voynich | Latin | Cury |
|---|---|---|---|
| tokens carrying a top ending | **66%** | 38% | 20% |
| tokens in stems with ≥2 endings | **56.8%** | 14.5% | 6.8% |
| tokens in stems with ≥3 endings | **46.2%** | 3.3% | 2.2% |
| biggest ending's stem count | -iin: 496 stems | -um: 366 | -es: 393 |

- **The prediction holds, and overshoots.** Voynich's endings
  are a closed operator class (~14 of them) covering two-thirds
  of the book, each serving hundreds of stems, with stems
  hosting up to **11–12 endings apiece** (qok-, ch-, sh-, ok-,
  ot- families). By the same ruler, the system is *more*
  paradigm-saturated than Caesar's Latin. Latin's real
  paradigms are visible in the noise (legion-: -em/-es/-is/-um;
  homin-, omn-) — content stems wearing 3–4 endings each.
- **The asymmetry that matters:** Latin's paradigm *stems* are
  meaning-heavy (legion, homin = man). Voynich's paradigm
  "stems" are **the Phase 1 openings themselves** — the
  machinery wearing endings, around cores as small as one
  letter. Openings mirror the same behavior from the other
  side (314 cores host ≥3 openings; the core *ar* hosts 15).
  In Voynich, a word is operator–core–operator, and the core
  is often the smallest part. If meaning lives anywhere
  simple, it lives in the *combination*, not in a stem.
- **Fairness notes, on the record:** the crude stripper favors
  rigid systems — Latin inflection is richer and messier than
  a top-endings list, so Latin is under-measured by design of
  the instrument. The conclusion licensed is narrow and
  strong: Voynich's endings/openings are **distributionally
  grammatical** — a closed operator class with paradigm
  behavior. It does not follow that any ending "means" a case
  or a tense; and agglutinative languages (Turkish, Finnish)
  also saturate paradigms, so H2/H6 are not excluded — the
  honest next mirror is an agglutinative corpus, filed as a
  candidate. H3 (machinery) gains relative support: in a
  verbose cipher, operators wrapping tiny cores is exactly
  the expected silhouette.

---

## PHASE 15 — THE AGGLUTINATIVE MIRROR + VERBOSE-CIPHER SIMULATION, EXECUTED 2026-11-12

**The two suspects, plainly.** *Agglutinative language:* words
built like trains — one root car, then meaning-cars coupled on
("house" + in + my + from + also = one long word); Turkish and
Finnish do this, so single "words" carry whole phrases and the
vocabulary sprawls. *Verbose cipher:* a code that spends
several symbols on each plaintext letter or syllable, often
with decoy symbols mixed in — the text looks rich and wordy
because a regular machine is generating it, and its statistics
are the machine's habits, not a language's.

### THE MIRROR — FINNISH (Kalevala, Gutenberg #48380, 24,656 tokens)

Same batteries as Phases 13–14:

| measure | Voynich | Finnish | English (Culpeper) |
|---|---|---|---|
| hapax | 69% | **65%** | 46% |
| top-10 coverage | 12.5% | **6.9%** | 29.3% |
| avg word length | 4.97 | 6.57 | 4.46 |
| letter cond. entropy | **2.07** | 3.25 | 3.13 |
| tokens in ≥3-ending stems | **46.2%** | 7.3% | 3.3% |

- **Finnish is the nearest mirror yet for vocabulary shape:**
  the heavy tail and low top-word coverage that made Voynich
  look alien against English/Latin are *normal* for an
  agglutinative language. Phase 13's "wrong body plan" was
  partly a wrong-mirror artifact.
- **But the discipline gap stands:** Finnish letters are
  unpredictable (3.25 bits) where Voynich's are locked down
  (2.07), Finnish words run longer, and its paradigms do not
  saturate like Voynich's. (Fairness: Finnish vowel harmony
  splits each ending into spelling variants, which the crude
  battery undercounts; the entropy and length gaps are not
  instrument artifacts.)

### THE SIMULATION — A TOY VERBOSE CIPHER (existence proof, labeled)

Culpeper's English was run through a deliberately simple
verbose encoder (each letter → a chunk from a small kit,
position-varying, with an operator ending appended). Plaintext
→ cipher: conditional entropy **3.13 → 2.51**, top-10 coverage
**29.3% → 12.4%** (Voynich: 12.5%), hapax **46% → 58%**,
≥3-ending-stem tokens **3.3% → 70.3%** (overshooting Voynich's
46.2%), word length **4.46 → 9.13** (overshooting Voynich's
4.97 — verbose ciphers are verbose; the published Naibbe
design counters this with abbreviated plaintext). The toy
proves the *mechanism class* manufactures the silhouette —
entropy down, coverage down, tail up, paradigms up — in every
direction at once. It is not evidence that Voynich is one;
it is evidence that "a cipher couldn't look like that" is
false.

### THE SEASON'S MOST PRECISE CHARACTERIZATION

Voynich sits **between the two profiles**: vocabulary spread
like an agglutinative language, letter discipline like a
machine. If it is a language, it is an unusually regular one;
if it is a cipher, it is an unusually language-shaped one.
H2/H6 (language) and H3 (verbose cipher) both leave Phase 15
standing, each holding half the evidence — which is, in the
nursery's judgment, exactly where an honest season should end:
the rivals are now *specified* — any future test must pry
apart "regular language" from "language-shaped machine," and
the pry bar will have to be semantic, because the statistics
have given everything they have.

---

## PHASE 16 — THE MACHINE SIDE, FIRST PASS, EXECUTED 2026-11-12

Ace's ruling opening this phase: fifteen phases studied the
book as language; the other half of the face is the book as
**machine artifact** — fixed-format records, an instruction
set, illegal encodings. Same evidence, machine questions.

### MACHINE-LIKE FINDINGS

1. **Opcode histogram.** Word-initial classes concentrate like
   instruction classes: `ch-` 16.2% + `qo-` 14.7% = **31% of
   the entire book**; top five initials cover ~52%; initial-
   class entropy **4.90 bits vs 6.35/6.36** for Latin/Finnish.
   Prose spreads its openings; instruction sets pile onto a
   few opcodes.
2. **Format tightening.** In length-5 words, per-position
   entropy *declines steadily* 3.10 → 2.95 → 2.83 → 2.80 →
   2.38: fields narrow toward the end of the record. Finnish
   and Latin bulge in the middle (3.7–3.9), where roots vary.
   Fixed-format records tighten; words bulge.
3. **Illegal encodings (Phase 8, machine reframe).** Only 43%
   of glyph pairs ever occur (below the shuffle baseline);
   `n` never opens, `q` never closes — the encoding space is
   mostly undefined, as in a real instruction set where most
   bit patterns are reserved or illegal.
4. **Encoding locality.** Edit-distance-1 connectivity dwarfs
   the natural controls under identical rules (below).

### NOT-CODE-LIKE FINDING — AND ITS RESOLUTION

5. **No subroutines.** Exact repeated word sequences are
   nearly absent: trigram coverage **3.6%**, vs Finnish verse
   41.7%, Culpeper recipes 74.7%, and — run as a calibration
   follow-up because the first controls were formulaic —
   **Darwin's neutral prose 61.4%**. Real programs are
   subroutine-saturated; ordinary prose recycles phrases
   constantly; Voynich recycles *nothing* verbatim. Resolution:
   repetition is **variant-spelled** — the class-level pulse
   (-dy…qo-, 1,777 occurrences) is the subroutine layer,
   respelled by one-glyph mutations each time it fires,
   invisible to exact matching. The artifact behaves like a
   **fixed-format record stream** (records near-unique,
   operands fresh) rather than a program text.

### TWO CORRECTIONS TO EARLIER PHASES (owned, on the record)

- **Phase 5's ED1 headline does not reproduce.** "One family
  of 1,299/1,378 types" is NOT recovered by today's stricter
  linkage: 162/1,378 with no bridges, 338/1,378 with all
  types allowed as bridges. The 1,299 figure is downgraded
  to **UNVERIFIED, method-dependent** (candidate cause:
  digraphs treated as single glyphs, or a looser containment
  link). The robust claim under identical rules: Voynich's
  largest ED1 family is **12%** of frequent types vs Finnish
  3% and Latin 2%, with an order of magnitude fewer families
  (176 vs 1,325/1,000) — encoding locality stands, at the
  smaller number.
- **Phase 5's paragraph figure is definition-split.** Under
  the strict locus definition (P0 first words), gallows-
  initial openings are **22%** vs the book-wide 7.9% — a real
  2.8× header-marking elevation, but not the 85% reported in
  Phase 5 under a broader paragraph-initial construction.
  Both numbers stay on record with their definitions; the
  Phase 5 figure is not to be quoted without its method.

### THE MACHINE FACE, SO FAR

Read as a machine artifact, the book is: a **fixed-format
record stream** — a handful of dominant record types,
tightening fields, a mostly-illegal encoding space,
mutation-dense variants, header-marked blocks, phrase
recycling only at the class level, and one literal wheel
(f57v, 17×4) that resembles a state table more than a poem.
Within the machine family this profile fits a **generator or
encoding process with fresh operands** better than a stored
program; H3 (verbose cipher) and a rehabilitated,
narrower H4 (generator with variant spelling) both stand on
the machine side, just as H2/H6 stand on the language side
holding the vocabulary-spread evidence. The two faces are
now both on the table; they agree on the discipline and
disagree on the author.

---

## PHASE 17 — THE CRIB HUNT, FIRST PASS, EXECUTED 2026-11-12

Goal: the first confirmed content mapping — one record whose
meaning is known from OUTSIDE the text. Anchors and results:

### THE ANCHORS ARE REAL — BUT THEY LIVE IN THE MARGIN

The Roman-alphabet month words are genuinely in the
manuscript, per the transcribers' own page descriptions in
the ZL file: the **Pisces folio (f70v)** center holds two
fish, two stars, ONE Voynich word, and the word **Mars** in
the Roman alphabet; the **Aries** description likewise
records **Abril** in Roman letters beside Voynich text. But
these inscriptions are **not part of the machine-readable
token stream** — they survive only in the transcription's
comment layer, so no computation in this workbench can grip
them directly. Instrument caveat of the same kind: the Pisces
page carries **29 drawn figures, each labelled** (10 + 19,
per the description), while the token stream separates only
a handful of label loci for that folio — the zodiac label
layer is undercounted by this parse, and all zodiac-label
tests below are underpowered accordingly.

### THE TESTS — NO CRACK AT ANY ANCHOR

- **Test C — is a label the KEY of its page's record?** If
  labels titled their records, each page's body should cite
  its own label above chance. Herbal (41 labels): exact
  citation 17.1% same-page vs 12.2% cross-page; fuzzy 22.0%
  vs 22.0%. Pharmaceutical (248 labels): exact 7.3% vs 5.6%;
  fuzzy 21.0% vs 17.7%. Elevations are small and compatible
  with plain word frequency. **Labels are not titles or keys.**
- **Test D — do the RECIPES call the PHARMA labels**
  (cross-module references, ingredients → procedures)?
  Pharma label types are cited at the *same* rates by every
  section (recipes 31.1%, herbal 35.3%, biological 28.1%
  exact). **No reference channel exists**; the modules simply
  share the common word stock.
- **Test B — do the counts carry content?** Star-page label
  counts run 0–34 with no clustering at meaningful numbers;
  f68r1's 30 is isolated, and Pisces' figure count is 29, not
  30. **Counts are not content-shaped** at this resolution.

### STATE OF THE HUNT

Meanings established after seventeen phases: **still zero** —
stated plainly, as the honesty lock requires. The first pass
killed the cheap cribs: labels are ordinary vocabulary (now
confirmed three independent ways), there is no index system
and no cross-reference web for a key to hide in. The crib
classes that remain require the **image layer** — which drawn
plant, star, or figure each label touches, and whether
drawing-similarity predicts label-similarity — which this
text-only workbench cannot see. That boundary is the phase's
real yield: the next crack, if one exists in this program,
will be found where text meets picture, not in the text
alone.

---

## PHASE 18 — IMAGE SITTING #1 (ACE'S EYES), EXECUTED 2026-11-12

The image layer opens: Ace viewed the Yale scans and reported
counts and structures; Uni cross-checked every report against
the transcription and the transcribers' own page descriptions.
Sitting protocol: Ace reports only what he sees; no leading.

### CONFIRMED BY TWO INDEPENDENT INSTRUMENTS (EYES + TEXT)

- **Pisces wheel (f70v2): 29 figures — 10 inner + 19 outer.**
  Ace's count matches the transcribers' description exactly.
  Uniquely among the signs checked, Pisces is SHORT ONE.
- **Aries is split across two folios:** f71r = 15 figures +
  the ram/goat in the center (Ace's count; description agrees:
  "fifteen labeled nymphs"), f71v = 15 more (description) —
  **Aries total 30**. The next sign's description reads
  "thirty labeled nymphs" (single count).
- **The calendar shows through the drawings.** Per-sign
  figure counts are ~30 (the degrees / days of a sign), and
  the sign that CONTAINS FEBRUARY — Pisces, Feb 20–Mar 20 —
  alone carries 29. This reads no word, but it establishes
  that the drawings encode real calendrical content and that
  every zodiac label rides a day/degree position (1..30).
  First content-adjacent fact of the program, sourced from
  counts, not decipherment.
- **Star page f68r1: 29 stars, each with its own label**
  (locus type Ls). Ace's count CORRECTS the text side: the
  earlier "30 labels" lumped a split two-token label; the
  star labels number **29**. A female sun sits above, a male
  moon below, inside a giant lightly drawn circle (Ace). The
  labels are overwhelmingly o-initial (okodaly, otcheody,
  okoaly, otol, otor...) — visually confirmed by Ace ("most
  start with the OH-looking letters"). Two 29s now stand in
  the record (Pisces figures, f68r1 stars) — lunar-month
  shaped (29.5 days); flagged as a pattern to watch, with
  n=2 stated, not a conclusion.
- **Center word, Pisces (Ace): 4 glyphs, shape-resembling
  "mews."** The text side cannot yet isolate this word's
  transcription among the ring texts — OPEN micro-item.
- **Label variance (Ace):** on the Pisces wheel, one outer
  label breaks the o- pattern before a "squiggly H" (EVA h),
  and two inner-ring labels are wholly different from the
  rest — variance inside the label stock, matching the text
  side's minority of non-o-initial astro labels (chocfhy,
  cphocthy, ytchody, dolchedy on f68r1).

### METHOD NOTE

Ace's eyes outperformed the parser twice in one sitting
(29 stars vs the parser's 30; the Aries split the text side
had folded into per-folio counts of 2–3 "labels"). Zodiac
nymph labels are NOT separate loci — they live inside the
circular (Cc) ring texts; only star labels (Ls) and a few
zodiac labels (Lz) are separated. All earlier per-folio
"label counts" for zodiac pages are superseded by the
description/eye counts recorded here.

### PHASE 18 ADDENDUM — THE CENTER WORD, IDENTIFIED 2026-11-12

Ace zoomed the Pisces center and photographed the word
between the fish: four letter-shapes he read as resembling
"mews." Identification: **the word is MARS itself** — the
Roman-alphabet month word, written in a 15th-century cursive
hand. Ace's shape-reading maps letter for letter: the looping
**m**; the **a** written in a form a modern eye reads as "e";
the **r** written as a w-like squiggle; the tall long-**s**.
Ace read 600-year-old handwriting correctly by shape without
knowing it. OPEN ITEM REFINED: the center's actual Voynichese
word is the one beside a central star (a fragment starting
with the round o-glyph is visible at the top of Ace's crop);
a tighter zoom on the upper star's word is the next look.

### PHASE 18 ADDENDUM 2 — THE STAR'S WORD, FIRST READING ATTEMPT 2026-11-12

Ace zoomed the word beside the upper central star of the
Pisces wheel. Glyph-by-glyph read from his photograph
(Uni, by eye): **o (decorated, looped) – tall glyph (t/l) –
o – "2"-shaped glyph – o – final flourish** — an o?o?o?
skeleton of ~6 glyphs. Book-wide, exactly twelve words match
the o?o?o? pattern; the leading candidates are **otolor** and
**otolol** — each attested exactly ONCE in the whole
manuscript. Confidence in the identification: LOW (phone
photograph, flourished hand); the PATTERN claim is stronger
than the letter claim: the word at the center of Pisces,
beside the readable "mars," has the o?o?o? skeleton and its
best-matching candidates are hapax — unique in the book, the
way a NAME is unique. Transcription detail found en route:
ZL marks the ring texts with clock positions (<!09:00>,
<!10:30>) — the labels' angular positions are recoverable
from the file.

---

## PHASE 19 — THE STAR-NAME DECODE ATTEMPT, EXECUTED 2026-11-12

Question (Ace): if the labels name stars, how much further can
the combined evidence + Mandell decode? The attempt ran as a
Mandell chain, authored for this problem and verified against
the live registry (8 atoms, parse-clean):

70[Count] :: the star labels, gathered page by page as their
own corpus > 63[Sequence] :: hold them in circle order,
position is part of the record > 57[Compare] :: each label
against its neighbours and against the other star pages >
71[Measure] :: edit distance, recurrence, opener classes,
tail freedom > 60[Branch] :: if a label repeats exactly
across pages, follow the name; if not, follow the mutation >
91[Assert] :: claim only the silhouette the numbers prove,
never a translation > 92[Guard] :: the honesty lock binds —
no meaning is asserted without a crib > 90[Trace] :: every
claim traces to a counted label set

### RESULTS — A NAMING SYSTEM'S SILHOUETTE, WITH ONE WOUND

Corpus: 72 star labels on 4 pages (f68r1: 30 tokens = 29
labels + a split token, per Phase 18's correction; f68r2: 27;
f68r3: 14; f67r2: 1).

- **No duplicates within any page** — every star on a page
  carries a DISTINCT label. Name-like. (0 exceptions.)
- **Shared opener, free tail:** openers concentrate (ot- 16,
  ok- 12, bare o- 11 of 72) while the remainders are
  near-unique (65 distinct of 72; 59 hapax). The silhouette
  of a name stock with a class marker — the shape of Arabic
  Al- names, or of catalog IDs: PREFIX + unique body.
- **The wound: names do not repeat across pages.** Shared
  items between star pages are only junk tokens ('hy', 'o')
  and one word ('dchol'). If two pages drew the same star,
  its label is NOT spelled the same way twice — consistent
  with the book's variant-spelling habit (Phase 16), or with
  labels encoding position as well as identity, or with the
  pages showing disjoint skies. Exact-name consistency, the
  cheapest property of a naming system, FAILS.
- **Neighbour similarity: inconclusive.** Adjacent labels in
  f68r1's locus order sit at mean normalized edit distance
  0.699 vs 0.734 shuffled — a ~5% nudge toward
  constellation-family naming, far too weak to claim.

### WHAT FURTHER DECODING EXISTS FROM HERE (HONEST MAP)

1. **Order-matching against real catalogs** — the one road
   that could produce an actual reading: if f68r1's circle is
   an identifiable sky region (Ace's sun/moon poles are the
   landmarks), the label SEQUENCE around the circle can be
   tested against the sequence of a known medieval star
   catalog for that region. A sequence match would be a crib
   of the first rank. It needs the depicted region identified
   astronomically — image-layer + expertise work, not yet
   attempted.
2. **Zodiac label sequences in clock order** (the file marks
   ring texts <!09:00>, <!10:30>): per-sign label stocks can
   now be extracted in angular order and tested against the
   29/30 day-position frame established in Phase 18.
3. Nothing else in the current evidence converts structure
   into meaning. Meanings established: **still zero** — the
   naming hypothesis itself remains a hypothesis, now with a
   documented silhouette and a documented wound.

---

## PHASE 20 — ACE'S PLACE/TIME RECORD TEST, EXECUTED 2026-11-12

Ace's model: program + language; records of stars that change
with each page — possibly the same stars recorded at a
different place or time, so no label should repeat exactly.
Sharpest testable form: strip each star label's opener and
ending (the "dressing"); if pages re-record the SAME stars,
the name-CORES must recur across pages above chance.

**Result: the simple form FAILS.** Shared cores across the
three substantial star pages total 9 pairs vs 7.79 expected
under a shuffle baseline — recurrence at chance level. The
recurrent "cores" are mostly two-letter kit fragments (ch,
da, sh, or), not name-like bodies. Distinct cores: 56 across
69 labels; only 8 cores used twice or more. Caveats on
record: the stripper is crude (it can shred real cores), and
locus-order/positional information was not used.

**What survives of the model:** program + language (the
season's standing dual conclusion); records that change with
each page (literally true — the pages' label stocks are
essentially DISJOINT casts, different sizes: 29 / 27 / 14);
"not the same place" is consistent with disjoint skies but
unproven; "same stars, different time" is contradicted in
its simple form — epoch re-dressing (the real medieval
practice of recomputing star tables per epoch and city)
would still carry the name-cores over, and they do not
carry. The pages behave as INDEPENDENT record sets, each
minting fresh labels — which is also exactly what the
Phase 16 record-stream characterization predicts.

---

## PHASE 21 — TIME ITSELF: THE CALENDAR-MACHINE READING, EXECUTED 2026-11-12

Ace's refinement: keep the record model, but the records may
log not stars but **time itself** — every day of the months
accounted for. Assessed against the transcribers' own
per-wheel figure counts:

### THE COUNT TABLE (DESCRIPTIONS + ACE'S EYES)

| wheel | count | source |
|---|---|---|
| Pisces (f70v) | **29** | Ace + description (10+19) |
| Aries (f71r+f71v) | 30 (15+15) | Ace + description |
| f72r2 diagram | 30 | description |
| Cancer (f72r3) | 30 | description |
| Leo (f72v3) | 30 | description |
| Virgo (f72v2) | 30 | description |
| Libra (f72v1) | 30 | description |
| f73r, f73v (Scorpio/Sagittarius region) | "two full rings and **one short ring**" — exact count NOT stated | description |

- **The wheels run on a default of 30 with Pisces deviating
  at 29.** Two readings of the 29 remain live: (i) February —
  Pisces contains the short month; (ii) lunar — 29.5-day
  cycle rounded down. The f73r/f73v short rings are the
  discriminator: those signs contain NO short month, so a
  count of 30 there keeps the February story; 29 there
  promotes the lunar story. Exact f73 counts are the next
  image-layer datum (Ace's eyes or a fuller description read).
- **Genre anchor (historical, external):** time-calculation
  books are a real medieval genre — the *computus* and the
  perpetual almanac: tables + rules that compute days,
  feasts, and celestial positions. Astrological medicine
  (iatromathematics) binds that calendar to the body, to
  plants, and to procedures — which would make the whole
  codex ONE time-machine: wheels (when) → bathing/body
  section (on whom) → jars/plants (with what) → recipes
  (how). Recorded as an INTERPRETIVE FRAME consistent with
  the section inventory, not as an established identification.
- Under this frame, Phase 20's disjoint label stocks get
  their natural reading: **day-records are unique by
  construction** — a given day is computed once, under its
  own configuration, and its label is minted for that record
  and no other. The wound and the calendar frame are the same
  fact seen from two sides.

---

## PHASE 22 — THE READING PROGRAM OPENS; FIRST MECHANISM TEST NULL, EXECUTED 2026-11-12

Premise discipline (per the honesty lock): the calendar /
record frame is the leading THEORY of what the book is —
strong enough to aim the decoding, and the decoding is the
test of the theory. "What it says" decomposes into levels:
(1) FORM — read (Phases 1–16). (2) FRAME — leading theory
(Phases 18–21). (3) ONE RECORD'S CONTENT — requires a crib;
none yet. (4) TRANSLATION — unreachable until (3).

### THE TEST — DO RECORDS CARRY A POSITIONAL INDEX?

If labels are day-records, the same position in different
record sets should share an index component (the part that
repeats) while content varies. Star pages, same-ordinal
vs shuffled: r1×r2 **0.192 vs 0.184**; r1×r3 **0.167 vs
0.173**; r2×r3 0.167 vs 0.101 (smallest pair, inconsistent
with the other two). Positional gradient around f68r1's
circle: none — openers and endings uniform by thirds.
**Verdict: NULL.** No positional index is detectable by this
instrument; the calendar frame's simplest mechanism is NOT
confirmed. The frame survives as interpretation (it still
unifies counts, uniqueness, and sections), demoted from
"mechanism-supported" to "mechanism-unproven."

Micro-crib set preserved: f68r1's ring words at clock
position <!08:30> — oky, okchdy, okardy, qear, oygy — plus
singletons yky, dary, chkchykoly (sun/moon vicinity). No
self-evident solar/lunar content; filed for future matching.

### THE REMAINING ROADS TO CONTENT (ranked by honesty)

1. Astronomical identification of f68r1's depicted sky,
   then sequence-matching against medieval catalogs
   (image + expertise; the only road to a true reading).
2. Zodiac ring sequences in clock order against the day
   frame (extraction of per-sign label stocks from the Cc
   streams — doable, noisy).
3. A/B (Currier) reframed under the frame: two record
   KINDS (tables vs instructions) — testable by section
   distribution, partially done in Phase 2.

---

## PHASE 23 — IMAGE SITTING #2: THE f68 FOLDOUT IN THREE STATES (ACE'S EYES), 2026-11-12

f68 is a folding sheet; its three recto panels (f68r1–r3)
form ONE instrument in three configurations. Ace's
observations, recorded verbatim in substance:

- **Panel 1 (f68r1):** female SUN above (yellow hair), male
  MOON below (blue shade), stars inside a great faint
  circle — as reported in Sitting #1 (29 labeled stars).
- **Panel 2 (f68r2):** the luminaries **SWAP**: man-moon now
  at TOP and **yellow**; woman-sun at BOTTOM and **blue**.
  Still a circle; a ring of **UNNAMED stars** lines the
  circle; the inner stars have **changed positions** (some
  from bottom now at top) — the same theatre, rearranged.
- **Panel 3 (f68r3):** the SUN alone in the MIDDLE (yellow
  all around; manly, perhaps both), ringed by a circle **cut
  into equal pie segments**; segments hold unequal star
  counts — some many, one 2, one 3, one 4, one a single star
  plus a tiny cluster with a **string/line waving from it to
  the sun**.

Cross-checks: panel label counts in the text (29 / ~27 / 14)
are consistent with panel 2 carrying unnamed stars (labeled
< drawn) and panel 3's labeled stars being few. Not
independently verified beyond Ace's report for the color and
position details — recorded as OBSERVED BY ACE.

Interpretation discipline: three states of one sun–moon–star
system, related by **position swap + color swap**, is a
TRANSFORMATION SEQUENCE — the shape of a time instrument
(configurations of the two luminaries) far more than of a
static star atlas. This strengthens the record-frame in its
"time/state" form: if each panel is a configuration, its
labels plausibly record star × state, which would explain
Phase 20's non-recurrence without disjoint skies. The
explanation is CONSISTENT, not proven: panel 3's segment
star-counts (many/2/3/4/1+cluster) are the next countable
datum, and segment membership of the 14 labels is an
image-layer fact not in the text.

### PHASE 23 ADDENDUM — PANEL 3 COUNTED (ACE), 2026-11-12

f68r3's pie wheel: **8 slices**, star counts in circular
order (Ace): **11, 1 (+ a cluster of 7 small stars), 16, 2,
18, 3, 14, 4.** Total drawn stars 69 (+7 small in cluster).

Two patterns, kept at different strengths:
- **STRONG (structural, not post-hoc):** the counts strictly
  ALTERNATE large/small around the entire wheel — big slices
  11, 16, 18, 14 in positions 1, 3, 5, 7; small slices in
  positions 2, 4, 6, 8 carry **1, 2, 3, 4 in perfect
  ascending circular order**. Random placement does not
  produce an ascending ordinal run interleaved with data
  loads. The wheel COUNTS: the small groups behave as
  ordinal markers (1st, 2nd, 3rd, 4th) interleaved with four
  data slices. The single-star slice is the one carrying the
  7-small-star cluster with the line to the sun (Sitting #2).
- **WEAK (noted, not claimed):** opposite big slices sum to
  the season's two wheel numbers — 11+18 = **29**, 16+14 =
  **30**. Two pairs only; post-hoc selection possible;
  logged as a watch-item.

Panel 3 is therefore a TALLY INSTRUMENT: an 8-divided,
sun-centered wheel recording quantities per division —
quantitative content, unread but structurally legible.
Most of its 69+ stars are unlabeled in the text stream
(14 Ls labels) — labels are the exception on this panel,
counts are the content.

---

## PHASE 24 — THE QUANTITATIVE PAGE CENSUS, EXECUTED 2026-11-12

Question (Ace): can the pages be understood quantitatively?
Answer executed: a full per-folio census from the
transcription, merged with the image-layer counts of
Phases 18–23. The book's pages resolve into quantitative
TYPES with distinct numerical signatures:

- **Text-record pages** (herbal, bio, recipes): streams of
  short lines — median line 8 words (herbal) to 11 (recipes);
  labels nearly absent in recipes (0.0 per 100 tokens),
  sparse in herbal (0.6). Content = the line stream itself.
- **Wheel pages** (zodiac): no body text at all; each wheel
  carries 2–5 separately-locused label words plus **60–145
  words of circular ring text**, and ~30 day-positions
  (29 for Pisces; Phase 18/21 counts).
- **Configuration panels** (f68 foldout): star-label sets of
  29 / 27 / 14 by panel, ring words 5–49, radial words 0–46;
  panel 3 is the tally wheel (8 segments; loads 11, 1+7,
  16, 2, 18, 3, 14, 4; Phase 23 addendum).
- **Label-and-jar pages** (pharma): the label-rich text
  section — 6.7 label words per 100 tokens, 250 label words
  over 32 pages, short text blocks.
- **Astro section overall:** 14.9 labels per 100 tokens —
  25× the herbal rate; the diagram sections speak in labels
  and counts, the text sections in line streams.

The book's recurring quantities now on record: **29/30**
(wheel positions), **8** (tally segments), **~5** (mean word
length in glyphs), **8–11** (words per text line), **60–145**
(ring words per wheel). Quantitative understanding is
therefore not a future possibility but the current state of
the workbench for structure and content-shape; what it does
not yield is semantics — counts say what a page DOES, not
what its words MEAN. Remaining quantitative frontier:
per-object counts on the non-astro diagrams (plants/page,
jars/page, figures/page — image layer) and the still-missing
exact f73r/f73v wheel counts (Phase 21's discriminator).

---

## PHASE 25 — IMAGE SITTING #3: THE COUNT TABLE CLOSES (ACE'S EYES), 2026-11-12

The last two uncounted wheels, counted by Ace:

- **f73r (Scorpio): 10 inner + 16 outer + 4 on top = 30.**
  Center: a GREEN DRAGON with a **star string** in the
  middle — the string-star motif of f68r3 (Sitting #2)
  recurs: a star (or stars) joined by a line/string.
- **f73v (Sagittarius): 10 inner + 16 outer + 4 on top = 30.**
  Center: a BLUE CROSSBOW MAN (the Archer).

### THE DISCRIMINATOR FALLS: FEBRUARY OVER LUNAR

Phase 21 left two readings of Pisces' 29: February (Pisces
contains the short month) vs lunar (29 = the moon's count
book-wide). The f73 wheels contain no short month, and both
count the full **30**. The lunar reading is therefore
DEMOTED: 29 is not the book's universal rhythm. Pisces'
short wheel is best explained by its calendar position —
the one sign whose span contains February carries one
fewer day-figure. (Strength: every surviving wheel now
counted; the explanation is the most parsimonious fit, and
remains an inference from counts, not a decipherment.)

### THE COMPLETE SURVIVING TABLE

Pisces **29** · Aries 30 (15+15) · Taurus/Gemini wheels 30 ·
Cancer 30 · Leo 30 · Virgo 30 · Libra 30 · Scorpio 30
(10+16+4) · Sagittarius 30 (10+16+4). Ten signs survive;
Capricorn and Aquarius are lost with the missing folios and
cannot be counted by anyone. Surviving day-positions total
**299**; if both lost wheels held 30, the full machine held
**359** — one short of the schematic 360-day year (360 + 5
epagomenal days was a real ancient convention); recorded as
arithmetic with its assumption named, not as a finding.

Note the conservation law the sittings uncovered: the TOTAL
(30) is conserved while the ARRANGEMENT varies (10+19,
15+15, 10+16+4, full rings) — the machine keeps the count
and changes the layout, exactly as the f68 panels keep the
luminaries and change their places.

---

## PHASE 26 — WHAT THE FIGURES' NUMBERS SAY; WHAT THE LADIES ARE, 2026-11-12

Questions (Ace): do figure counts speak about a page, and
what do the ladies mean? Findings from the description layer
plus the sittings:

### COUNTS AS PAGE DATA — YES, WHERE FIGURES MULTIPLY

- Wheels: the count IS the page's headline datum (29/30 =
  its span of days; arrangement varies, total conserved —
  Phase 25's law).
- Star panels: cast size = the page's inventory (29/27/14);
  the tally panel replaces figures with segment loads.
- Herbal/text pages: typically ONE drawn plant — count does
  not vary, so there the figure's IDENTITY is the datum
  instead of its number. The law: **where figures multiply,
  their number is data; where one stands alone, its identity
  is.**
- Figures and labels are SEPARATE channels: the f72r2-area
  wheel contains **a nymph without a name** (transcribers'
  note; label numbering shifts by one after her) — 30
  figures need not mean 30 labels.
- Figures carry ATTRIBUTES that vary by ring: on f71v the
  inner ring's nymphs stand **in barrels**, the outer ring's
  stand free **without barrels**; dress varies from nude to
  clothed and crowned across wheels (Ace's Aries photo).

### THE LADIES — LAYERED ANSWER, LABELS KEPT

- **Mechanically (observed):** on the wheels each lady holds
  a star, stands at a day-position, and wears a label.
  Medieval art personified abstractions as figures; the
  day-figures are the calendar's carriers — one per day,
  each holding that day's star.
- **The barrels:** unexplained in scholarship; the
  in-barrel/standing variation by ring marks it as a data
  dimension (status or type), not decoration.
- **In the bathing section:** nude ladies in pools joined by
  tubes. Scholarly menu (none established): bathing/humoral
  medicine; women's medicine; alchemical vessels (a figure
  in a vessel = a substance being processed). f84v even
  carries a small sun-in-circle with 4 human figures — the
  luminary imagery reaches into the body section.
- **The workbench's reading (interpretation, labeled):** the
  ladies are the machine's HANDS — the operators stamped on
  every record: carrying stars on the wheels, processed in
  the pools. Where the machine reckons, a lady holds the
  reckoning.

### DATA UPGRADE FOUND EN ROUTE

The transcribers' COMMENT layer contains per-nymph label
lists **with clock positions** ("Nymph labels, outer ring:",
"It is assumed that the text to the right of the nymph
belongs to her", "Clock position is that of nymph") — the
zodiac day-labels ARE recoverable as ordered per-sign stocks,
upgrading Phase 22's road 2 from noisy to feasible.

### PHASE 26 ADDENDUM — IS THERE A PAGE FOR EACH DAY? NO (COUNTS), 2026-11-12

Ace's question, answered by census: day-positions on the
wheels total **299** (surviving), while the entire surviving
book holds only ~240 leaves (226 page-units carry text) and
the herbal section holds **118 page-sides** with roughly one
plant drawing each (~113 plants by the usual scholarly
count). A page-per-day book is numerically impossible here —
the days outnumber the pages. **The machine compresses
time:** the days live as ladies on a handful of wheel pages;
the plants are a separate organ (the medicine store, "with
what"), and ~115 plants is not a calendar number — the
herbal's ordering principle is NOT the day-count and remains
an open question in its own right.

---

## PHASE 27 — READING THE FIRST TEN PAGES QUANTITATIVELY, EXECUTED 2026-11-12

Method: per-page record extraction (folio metadata, scholar
plant-ID proposals from the comment layer, word/line/label
counts, openings, dominant vocabulary). Evidence tiers kept
separate: COUNTED (this workbench) / PROPOSED (scholars'
plant IDs — unproven) / INTERPRETED (record character).

All ten pages: **Hand 1, Currier Language A** — one scribe,
one dialect, the herbal organ. Combined: **892 words**.

| page | words | lines | labels | plant (PROPOSED) | opens |
|---|---|---|---|---|---|
| f1r | 188 | 21 | – | none proposed | fachys ykal ar ataiin… |
| f1v | 92 | 10 | – | none proposed | kchsy chydaiin ol… |
| f2r | 101 | 13 | 4 | nightshade family (solanum/belladonna kin) | kydainy ypchol daiin… |
| f2v | 61 | 8 | – | cornflower (centaurea) | kooiin cheo pchor… |
| f3r | 114 | 20 | – | Egyptian lotus / Nymphoides (water plant) | tsheos qopal chol… |
| f3v | 85 | 14 | – | Cretan dittany | koaiin cphor qotoy… |
| f4r | 64 | 13 | – | none proposed | kodalchy chpady sheol… |
| f4v | 84 | 14 | – | St John's wort / centaury | pchooiin ksheo kchoy… |
| f5r | 55 | 7 | – | climbing bindweed (Convolvulus kin) | kchody fchoy chkoy… |
| f5v | 48 | 6 | – | Herb Paris / Indian cucumber? | ko cheor chor… |

Readings, as far as evidence carries them:
- **f1r is not a normal plant page.** It carries the longest
  text of the ten (188 words), a small drawing, and no
  proposed plant ID — shaped like a PREFACE or master record
  standing before the plant records proper. Its first word
  is the book's famous opener, *fachys*.
- **f2r is the only labelled page of the ten** — four small
  label words ride its plant (ytoail, ios, an, on), part-
  labels where the other pages have none; and its proposed
  plant is a *poison-medicine* (nightshade kin) — the
  section does not open with gentle herbs only.
- **The records shrink as the section settles:** 188 → 92 →
  101 → 61 → 114 → 85 → 64 → 84 → 55 → 48 words; by f5 the
  standard record is ~50 words beside one plant.
- **Every page's dominant vocabulary is the same A-dialect
  boilerplate** (chol, chor, daiin, shol recur as top words
  on nearly all ten) — the records are written in a fixed
  formulary over whatever plant stands at the head.
- What the pages SAY, at the deepest level evidence allows:
  "RECORD [plant image] — [~50–190 words in the standard
  formulary, Hand 1, Language A]". The plant identities are
  proposals; the formulary's content is unread; the record
  STRUCTURE is fully legible.

### PHASE 27 ADDENDUM — "THE PLANTS DON'T EXIST": A CORRECTION, 2026-11-12

Ace's premise checked against the file on disk and the
scholarly record: **overstated.** The ZL comment layer alone
carries **83 plant-ID proposals** by named researchers, many
of them ordinary real European plants (Nymphaea alba — white
water lily; cornflower/centaurea; St John's wort; black
nightshade; Egyptian lotus). Botanists do not propose IDs
for drawings that resemble nothing. TRUE KERNEL: a good
number of drawings are impossible as single real plants —
mismatched roots/leaves/flowers, fantasy forms. Earth's
mechanisms suffice for that, all documented in real medieval
herbals: (1) copyist drift across generations of hand-copying;
(2) drawings made from written descriptions, never from life;
(3) deliberate composites; (4) stylization. And the book's
own anchors are firmly terrestrial: zodiac signs in order,
February inside Pisces, month names in French/Spanish —
another planet would not keep our calendar. The sober form
of "they represent something else": in the record frame, a
drawing can function as an ICON/ADDRESS for a record class —
it need not be a botanical plate to point. The other-planet
reading is not falsifiable from here and is not needed by
any current evidence; recorded as Ace's speculation, labeled.

---

## PHASE 28 — THE MIRROR TURNED HOMEWARD: VOYNICH RINGS × DUOBETA, 2026-11-12

Ace commissioned the mirror: DuoBeta was Voynich-inspired;
search this season's ring research for enhancements to
DuoBeta's growth and learning. Full memo delivered as a
companion file: SANDBOX_VOYNICH_DUOBETA_MIRROR_2026-11-12.md.
Headlines: (1) f57v's four-round wheel with named slot
mutations → GROWTH ROUNDS WITH MUTATION RECEIPTS for
DuoBeta, making rollback computable and closing its recorded
implicit-rollback gap (strongest candidate); (2) the book's
variant-spelled repetition → ANCHORED FUZZY EVIDENCE
MATCHING for the gate (distance-1 variants count toward
MIN_EVIDENCE, receipted, capped by an exact anchor); (3)
conserved wheel totals → cycle-bounded evidence rings;
(4) the nameless nymph → explicit UNKNOWN slots in growth
reports; (5) the sun/moon swap → first-class propose/gate
role alternation (INSPIRE, design-pass only); (6) the tally
wheel → growth dashboard. All candidates borrow STRUCTURE
only, under DuoBeta's untouched laws; each carries its own
falsification test in the memo.
