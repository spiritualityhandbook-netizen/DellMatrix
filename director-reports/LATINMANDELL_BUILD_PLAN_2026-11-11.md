# LATINMANDELL BUILD PLAN — The Forced Morpheme Pass

### Ace directive, 2026-11-11 (voice): "Implement that as a plan that we're actually doing, not a proposal. We're doing that."
### Status: ACTIVE BUILD PLAN — entered into the Dell plan (§15 pointer). Execution: Uni, through Director-routed circuits under standing law.

---

## 1. THE OBJECTIVE (Ace's intent, recorded 2026-11-11)

LatinMandell becomes the **forced first pass of all English
understanding** in DellMatrix:

1. A person (or a docked AI) writes regular English.
2. The system **forces** decomposition of that English into its
   **Latin morphemes** — the 2/3/4/5-letter meaning pieces.
3. Each morpheme carries a **fixed meaning**; the word's meaning is
   the composed stack of its pieces — understood exactly, quickly,
   and cheaply, instead of being re-derived whole at full cost.
4. The composed meaning is what **selects and routes to the
   Dells** — morpheme sense → Dell — closing the loop:
   English → Latin morphemes → composed meaning → Dell chain.

Done means: English entering the program passes through
LatinMandell *by construction*, the way every chain passes
through the parser — not as an optional explainer beside the road.

## 1.5 ACE REFINEMENTS (voice, 2026-11-11, after the plan was ordered — these govern the build)

- **A LENS, NOT A SOURCE OF TRUTH.** LatinMandell helps the AI
  understand English — parse it more easily and readily. It is
  *pretty accurate*, not truth. Whatever it cannot process, the
  AI still understands through its own natural resources, its own
  way. **Not everything must be processed through LatinMandell**;
  it makes understanding easier where it applies. The "forced
  pass" of LM-4 therefore means a forced *first read* with honest
  pass-through — UNRESOLVED material flows onward to natural
  understanding, never blocked, never faked.
- **FUNCTION, NOT JUST WORDS.** Broken into Latin morphemes,
  English becomes *function*: you can tell what is fluff and what
  is actually function, what it means, and relate that function
  to **Dells — or to functions elsewhere in the program** that are
  not Dells. LM-3's composition therefore classifies each piece
  as function-bearing or fluff, and maps function to Dells *or*
  program functions.
- **HARVEST BEFORE IMPORT (Ace's observation, verified true).**
  Latin morphemes already exist split up across the codebase —
  form/, src/, preform/ (inventory in §2.5). LM-1 harvests and
  reconciles the in-repo material FIRST; the external table
  fills the gaps. Preform material is design history (NOT IN
  USE): it enters as *candidates* under the preform's own
  Leight/Loure rules (Manual gate + Architect confirm), never as
  silent authority.

## 2. CURRENT STATE (verified 2026-11-11, code + live runs)

- `form/mandell/latinmandell.py` (360 lines): 53 surface roots
  (word → Latin root + sense + Dell), explain/deepen/root_of,
  seed_for_root, customize() with customs persisted (save/load v7).
- `form/mandell/morpheme.py` (190 lines): ~57 prefix/root/suffix
  pieces with senses; hyphen decomposition (Com-man-dell →
  together · control/hand · nested unit — verified live).
- The English→Mandell translator (`translate.py`) **never calls**
  LatinMandell. LatinMandell routes no execution. It explains;
  it does not parse arbitrary English.
- This gap — intent vs implementation — is what this plan closes.

### 2.5 THE SCATTERED INVENTORY (repo search, 2026-11-11 — Ace's instinct verified)

Morpheme material found across the repository (GitHub code
search: 17 files carry "morpheme"; inventories below are the
ones holding actual split pieces):

| Where | What is there |
|---|---|
| `form/mandell/latinmandell.py` + `polyglot.py` | The live layer: 53 roots with Latin forms + senses + Dell numbers |
| `form/mandell/morpheme.py` | ~57 prefix/root/suffix pieces with senses (Com/man/dell among them) |
| `src/core/mandel_ontology.js` | A MORPHEMES table: 5 Latin prefixes (Com-, Re-, Pre-, Trans-, De-), 4 Latin roots (-fac-, -log-, -mit-, -spec-), 5 Greek operators (Alpha/Delta/Lambda/Sigma/Omega) |
| `preform/pages/21_AFFIX_LEXICON_STARTER.md` | Starter affix lexicon: 10 prefixes (Man-, Dell-, Form-, Evolu-, Harmoni-, Mirror-, Proso-, Pure-, Recur-, Trans-) + 5 suffixes (-dell, -ell, -cell, -factors, -man), each with a sense sketch |
| `preform/LANGUAGE_PREFORM.md` | The creation law for new pieces: **Leight** (define new Latin-Mandel units; Manual gate + Architect number-confirm) and **Loure** (adopt a non-Latin word's defined affix sense into Latin-Mandel) |
| `preform/PHASE3_LANGUAGE_COMPONENTS.md`, `MANUAL_EXTRACT.md`, `IDEAS_HARMONIC_MATRIX_EXTRACT.md`, `pages/09_PHASE3_INTAKE.md`, `docs/MANDEL_COMPENDIUM_V2_ESTABLISHED.md`, `form/mandell/MANDEL_LANG_V0.md` | Mentions/design context, no separate tables found |

Honest measure: the scatter is real but it is *fragments* — tens
of pieces per location, with overlaps — not a hidden complete
table. Combined unique in-repo material is on the order of a
hundred-odd pieces. That is exactly why LM-1 is harvest-then-
import: the in-repo pieces (especially Ace's own affixes and the
Leight/Loure law) are the seed crystal; the free external table
supplies the thousands around them.

## 3. SOURCES WE STAND ON (researched 2026-11-11; credit given in code, docs, and receipts)

| Source | What we take | License / terms |
|---|---|---|
| Wikipedia/Wiktionary — *List of Greek and Latin roots in English* | The core morpheme table: ~1,693 Greek-Latin root morphemes **with meanings**, allomorphs, example words | CC BY-SA — attribution + share-alike on derived data |
| BAWF (British and American Word Families, cgg-projects) | Cross-check corpus: ~378k English words with classical-root attribution | Open release; **repo shows no license file — verify terms before importing data; if unverifiable, use as cross-check only, never as copied data** |
| MorphoLex | Pre-segmented English words (~68k) as segmentation ground truth for tests | Research dataset — cite; verify redistribution terms before bundling |
| UniMorph / umLabeller | Large English morphological divisions (~611k words) for coverage testing | UniMorph project terms |
| SIGMORPHON 2022 Segmentation (github.com/sigmorphon) | Gold segmentation datasets + evaluation method (best English systems ~94% F1) | Open research release |
| CLTK — Classical Language Toolkit (cltk/cltk) | Latin-side morphology/lemmatization reference where Latin forms need parsing | MIT — use freely with attribution |
| Whitaker's Words (ArchimedesDigital/open_words port) | Latin stem/ending decomposition reference | MIT port — attribution |

**Standing caution (recorded):** a public repository with no
license is NOT free to use. Anything whose terms cannot be
verified is excluded or used read-only as a cross-check, and the
exclusion is recorded. Credits live in a `CREDITS` block in the
module and in the plan record — Ace's instruction: "if it's free,
I don't mind and we'll just give that person the credit."

## 4. THE BUILD — FIVE CIRCUITS (LM series; two-cycle cap applies per §33)

### LM-1 — THE TABLE (data foundation)
- Import the Wikipedia/Wiktionary roots list into a versioned
  LatinMandell data table: morpheme, allomorphs, meaning, example
  words — with the CC BY-SA attribution recorded in-file.
- Grow the built-in morpheme set from ~57 pieces to the full
  table (~1,693 roots + the prefix/suffix families), keeping
  Ace's existing 53 roots and customs as the first-class seed set
  (his entries win any conflict; conflicts logged, never silent).
- Acceptance: table loads; every entry has meaning + provenance;
  a spot battery of 100 known words resolves to correct roots.

### LM-2 — THE SPLITTER (English → morphemes)
- Build the decomposition engine on the existing morpheme.py
  authority (extend, never duplicate): greedy longest-match over
  the LM-1 table + allomorph rules; unknown material is returned
  as an honest UNRESOLVED piece, never guessed.
- Validate against MorphoLex/SIGMORPHON gold segmentations;
  publish the score (target: meet or beat the ~94% F1 class on
  the gold sample; whatever the real score is, it ships printed
  on the receipt).
- Acceptance: battery over gold data scored and recorded;
  Com-man-dell-class hyphen forms keep working byte-for-byte.

### LM-3 — THE COMPOSER (morphemes → meaning → Dell)
- Compose the stacked sense of a decomposed word/phrase in the
  existing explain/deepen shape (the receipt format already
  proven live), extended from dictionary words to ANY English
  the splitter can resolve.
- Extend the sense → Dell mapping from Ace's 53 hand-bound roots
  across the full table, using the composed senses; ambiguous
  compositions return ranked candidates with the ambiguity named
  (PROJECTION discipline — a composition is a reading, not a fact).
- Acceptance: a battery of ordinary English directives decomposes
  and lands on the Dell a human judge picks, at a recorded rate;
  failures are listed, not averaged away.

### LM-4 — THE TOLL BOOTH (wiring the forced pass)
- Route the English entry path THROUGH LatinMandell: the
  translator consumes LM-3's composed meanings as its input
  representation (extending the existing translate authority —
  no second translator, no parallel path).
- Undocked path: deterministic composition. Docked path: the
  docked AI receives the morpheme decomposition as its forced
  first step (the AI breaks English down the LatinMandell way
  because the input arrives already broken).
- Acceptance: end-to-end through the public REPL path — English
  in, morpheme trace shown, Dell chain executed, receipt carries
  the decomposition; a bypass attempt (raw English reaching the
  executor undecomposed) is impossible on the wired path and the
  test proves it.

### LM-5 — THE METER (TokenCount harmony, per DD-30)
- TokenCount reports LatinMandell as its own system: morpheme
  tokens per directive, longhand-vs-shorthand savings measured,
  beside seed atoms, Mandell Emoji glyphs, and the docked
  provider's own tokenizer counts.
- Acceptance: one directive reported in all systems side by side,
  numbers from the real counters.

## 4.6 THE FORMULA (Ace, 2026-11-11: "a nice little formula to parse English in that way")

The lens is one formula, applied to every word, then to every
sentence. It is the heart of LM-2 and LM-3; the circuits exist
to make this formula run.

### The word formula

```text
   WORD  =  PREFIX*  +  ROOT  +  SUFFIX*

   SENSE(word)  =  STACK( sense of each piece, in order )

   PARSE(word)  =  SPLIT  ×  STACK  ×  CLASSIFY  ×  MAP
```

- **SPLIT** — the word is cut into its Latin morphemes by
  longest-match against the table, allomorph-aware (the same
  root in its variant spellings counts as the same piece).
  A piece that matches nothing is carried as UNRESOLVED —
  visible in the output, never silently dropped (Refinement A:
  UNRESOLVED flows to the AI's natural understanding).
- **STACK** — the pieces' fixed senses are stacked in order
  into one composed sense: prefix(es) aim the root, the root
  carries the core, suffix(es) land it. Example, from the live
  table: *transform* → trans (across) + form (shape) =
  "change form across a boundary."
- **CLASSIFY** — every piece and the composed whole are tagged
  FUNCTION or FLUFF (Refinement B): function pieces carry the
  doing; fluff pieces carry grammar, glue, and decoration.
  The parse reports both, so what a sentence *does* is
  separable from how it is *dressed*.
- **MAP** — the composed function is related to a Dell, or to
  another function in the program, or honestly to neither
  (ranked candidates with ambiguity named, per LM-3).
- Multiplication, as in the Dell anatomy: a word whose SPLIT
  finds nothing contributes no STACK; the formula returns
  UNRESOLVED for that word instead of a fabricated product.
  An honest zero keeps the sentence's arithmetic true.

### The sentence formula

```text
   PARSE(sentence)  =  PARSE(each word)  +  the function spine
   the function spine  =  the FUNCTION words, in order,
                          fluff folded around them
```

The spine is what the sentence is *doing*; it is the primary
input to Dell selection in LM-4, with the full stack kept as
the auditable trace.

### The levels (Ace: "understand what is being said on many levels")

One parse yields all levels at once — this is the lens:

| Level | What the AI sees |
|---|---|
| L1 SURFACE | the English word as written |
| L2 PIECES | its Latin morphemes, hyphen-split (Com-man-dell) |
| L3 SENSE | the stacked composed meaning of the pieces |
| L4 FUNCTION | what the word *does*; function vs fluff |
| L5 RELATION | the Dell (or program function) the function maps to |

### The honesty measure

```text
   COVERAGE(parse)  =  resolved pieces ÷ total pieces
```

Every parse carries its coverage. A 1.0 parse is fully read
through the lens; a 0.6 parse says exactly which 40% the AI is
understanding by its own natural means instead. Coverage is
printed on the receipt (LM-4) and counted by the Meter (LM-5) —
the lens reports its own clarity, which is what makes it a
lens and not a claim of truth.

### Worked example (built from live table entries)

```text
   "transform the idea"
   transform → trans(across) + form(shape)
             → L3 "change form across a boundary"
             → L4 FUNCTION: change-of-form → L5 Dell 04 Evolve
   idea      → idea/forma (form held in mind) → Dell 08 Create (the held form)
   the       → FLUFF (grammar glue; carried, not mapped)
   Spine: [change-form → Evolve] acting on [held-form → idea]
```

## 4.7 THE SMALL WORDS — PREDISPOSED CATEGORIES (Ace, 2026-11-11: the last piece of the design)

The morpheme formula governs content words. The little words —
*and, of, this, my, if, or, not* — do not decompose; they are
**predisposed**: each carries a fixed raw meaning set in advance,
and they live in **their own categories**. Nothing in a sentence
is left unaccounted: content words are read through morphemes,
small words through their category, and true fluff is declared
as fluff. What LatinMandell hands the AI is then the **raw
meaning of everything** — the pure raw meaning of what something
is, token by token.

### The categories (v1; each word's raw meaning is predisposed, in the table, beside the morphemes)

| Category | Raw job | Members (starter set) | Predisposed raw meanings (examples) |
|---|---|---|---|
| **LINK** | joins things together | and, or, of, with, to, by | and = join-both · or = choice-either · of = part-of / belonging |
| **POINT** | points at a thing or a person | this, that, my, your, it, I, you | this = point-near · my = point-at-speaker + own · that = point-far |
| **CONDITION** | opens a condition | if, unless, whether | if = condition-open · unless = condition-except |
| **NEGATE** | reverses what follows | not, no, never | not = reverse · never = reverse-always |
| **ASK** | opens a question and names the shape of the answer it wants (Ace, 2026-11-11) | why, who, what, when, where, how | why = asks-for-cause · who = asks-for-person · what = asks-for-thing · when = asks-for-time · where = asks-for-place · how = asks-for-method |
| **FLUFF** | carries no raw meaning for the parse | the, a, an (articles as predisposed glue) | declared, carried, never mapped |

### Consequences for the formula (§4.6 amended)

- CLASSIFY now sorts every token into exactly one of:
  FUNCTION (content, via morphemes) · LINK · POINT · CONDITION ·
  NEGATE · ASK · FLUFF · UNRESOLVED. An ASK token additionally
  lets the parse name what a sentence is *missing*: a why whose
  spine carries no cause is an unanswered question shape, and
  the receipt can say so. The small words are small but
  they are **not** fluff by default — *not* reverses a sentence,
  *if* conditions it, *my* aims it at the speaker; the categories
  keep those jobs visible instead of letting them wash out.
- Two honesty scores replace the single coverage number:
  **ACCOUNTED** = tokens carrying a class ÷ all tokens (the
  design's aim: every token accounted, fluff included — fluff
  is a *declared* class, not an omission), and
  **MORPHEME-RESOLVED** = content tokens resolved via
  morphemes ÷ content tokens (the lens's clarity on the words
  it reads by pieces). Both print on the receipt.
- The predisposed table is part of LM-1's harvest: small-word
  categories are seeded from Ace's examples above and extended
  by the same Leight/Loure discipline as morphemes — new small
  words enter by category + predisposed meaning + confirm,
  never by silent default.

## 4.8 THE PRE-PLAN CENSUS (Ace, 2026-11-11: "in the plan we do that pre-plan and we search for everything that could possibly be in that category that's not currently listed")

Before any LM circuit builds, a **pre-plan census** runs — LM-0.
The starter sets in §4.7 are examples Ace named in conversation;
they are NOT the categories' membership. The census searches for
**everything that could possibly belong to each category and is
not currently listed**, so the predisposed tables are complete
by search, not by whoever happened to speak first.

### Census scope (per category)

- **LINK** — every English conjunction and joining preposition:
  coordinators, subordinators, correlatives (either/or,
  neither/nor, both/and), and the preposition family (of, to,
  with, by, for, from, into, over, under, between…) — each with
  its join-type as the predisposed meaning.
- **POINT** — every pronoun and determiner-pointer: personal
  (I, you, he, she, it, we, they), possessive (my, your, his,
  her, its, our, their), demonstrative (this, that, these,
  those), reflexive (myself, yourself…) — each predisposed with
  *who or what it points at* and its distance/ownership marks.
- **CONDITION** — if, unless, whether, provided, supposing,
  once, as-long-as, in-case, and every other conditional opener
  the search finds.
- **NEGATE** — not, no, never, none, nothing, nobody, nowhere,
  neither, nor, hardly, scarcely, without — every reversal and
  denial form, with its reversal scope sketched.
- **ASK** — why, who, whom, whose, what, when, where, which,
  how, and the compound forms (how-many, how-much, how-often,
  how-far…) — each with its asks-for shape.
- **FLUFF** — the articles and pure glue the census confirms
  carry no raw meaning for the parse; anything found to carry
  even a small job is *promoted out of FLUFF* into its proper
  category, with the promotion recorded.
- **Morpheme side (rides with LM-1's harvest)** — the same
  sweep discipline against the repo inventory (§2.5) and the
  free roots table: pieces present in any source but missing
  from our table are listed as candidates, never silently
  absorbed.

### Census method and law

- Sources: standard closed-class/function-word inventories,
  Wiktionary category listings, corpus frequency lists, the
  in-repo documents (§2.5) — searched broadly, per Ace's
  research discipline; a candidate found anywhere is *listed*,
  with its source.
- Every candidate leaves the census with: its category, a
  drafted predisposed raw meaning, and its source. Ambiguous
  memberships (a word that could sit in two categories) are
  named as ambiguities with a recommended home — not averaged.
- **Ace confirms the census tables.** Predisposed meanings are
  definitions, and definitions are the Architect's — the same
  Leight discipline as new morphemes: census proposes, Ace
  disposes. Unconfirmed candidates stay candidates; the build
  uses only confirmed tables.
- The census is a *pre-plan*: it produces the tables LM-1
  imports and LM-2/LM-3 build against. It is LM-0 in the build
  order and runs first.

## 4.9 MANDELLMOJI — INCORPORATED INTO MANDELL

> **FINAL FORM — Ace ruling, 2026-11-11 ~11:42 CST (supersedes
> the tone-only revision of ~11:41, which itself superseded the
> first framing below; both retained as history):** **Keep
> Mandellmoji as it is — glyph + Dell reference — and ADD tone
> to it.** A Mandellmoji is a way to use a tone and a Dell *at
> the same time*: each entry in the canonical table carries
> THREE things — the **glyph**, the **Dell** it references,
> and a **predisposed tone** (the vibe that glyph radiates,
> applied through 05[Tone] when the glyph is used). Writing
> 🌱08 invokes 08[Create] *in 🌱's tone* — growth, patience,
> beginnings — in a single token. The density Ace wanted and
> the tone Ace wanted are the same object: the glyph was
> always radiating a vibe; the design now says so on the
> record. Consequences: the §4.9 incorporation law below
> stands as written (one table, reference not authority,
> names mirrored, density earns the seat, Meter counts it),
> PLUS every glyph's table entry gains its tone field,
> predisposed and Ace-confirmed under the census discipline,
> and LM-6 (the Glyph Door) teaches the front door to resolve
> a glyph to Dell + tone together. Tone still colors delivery
> and stance only — never semantics, never truth.
>
> **REVISION — Ace ruling, 2026-11-11 ~11:41 CST (superseded by
> the FINAL FORM above; retained as history):**
> Mandellmoji is asleep in the codebase and not really
> connecting, so its job is CHANGED: **Mandellmoji focuses on
> VIBE — it applies to TONE, Dell 05[Tone] (manor "Vibe /
> style", verified live in the registry).** When you use a
> Mandell emoji, you change the tones up. Emojis are tone
> carriers — a happy face, a sad face, a plant — and that goes
> into tone. The one-token-dense-directive role is RETIRED for
> Mandellmoji (density lives with LatinMandell/TokenCount);
> the glyph layer's one job is setting and shifting the tone
> of a chain.
>
> Revised design law:
> - A tone glyph is a **predisposed tone** (same discipline as
>   the §4.7 small words): each glyph carries a fixed vibe —
>   warmth, sorrow, growth, urgency, calm… — set in advance,
>   in one tone table, confirmed by Ace.
> - A glyph placed on a seed/chain **sets or shifts its tone**
>   through Dell 05[Tone]'s contract; the executor's semantics
>   are untouched. Tone colors *delivery and stance* — how the
>   work speaks and leans — never the product's truth (per the
>   epistemic doctrine: tone is not a source of truth, and a
>   glyph can never smuggle a semantic change).
> - LM-6 is redesigned accordingly: **THE TONE DIAL** — one
>   canonical tone-glyph table (the scattered 15 are harvested
>   as *candidates* and re-read for the vibe each glyph carries,
>   stale Dell-manor names retired with the old framing), the
>   front door learns to read a tone glyph as a Tone setting on
>   its chain, and the Meter counts tone glyphs as tone, not as
>   compressed directives.
> - Census discipline applies: the tone vocabulary is swept
>   and listed (LM-0-style) before Ace confirms the table.

(Ace ruling, 2026-11-11: "it just needs to be used as reference… emojis that can carry a whole lot of functionality within one token… we need to incorporate that into Mandell… that's powerful. That's grand. So we need that.")

Mandellmoji is not a side system and not a separate plan. By
Ace's ruling it is **incorporated into Mandell itself** as the
language's **glyph reference layer**: a glyph is a *reference* —
one small character that carries a whole lot of functionality
(a Dell, and at the dense end a whole seed/directive) inside a
single token. Its power is compression-by-reference: the glyph
points at the full meaning the way a Dell number points at its
contract.

### Incorporation law

- **Reference, not a second authority.** A glyph resolves
  through the canonical parser to the exact Dell/seed it
  references; execution is unchanged. 🌱08 *is* 08[Create]
  written in one token — the glyph is an input alias promoted
  from the display alias it already is in the grammar, never a
  parallel execution path, never a second registry.
- **One table.** Today's scatter (seed.py's 2 flow glyphs;
  gate_discipline.py's 15 compound glyphs; the reserved address
  775 "Mandellmoji — compound visual seed") reconciles into ONE
  canonical glyph table under the parser's house.
- **Names mirror the present.** The 15-glyph table's stale
  manors (71 "Grow", 60 "Nature", 82 "Vision", 99 "Omega", …)
  are corrected against the current registry and the Dell plan
  — the plan stands, the table catches up (§: Dell-plan mirror
  rule). Glyph assignments for 08/13/14/18/25 already agree.
- **A glyph earns its place by density.** Not one emoji per
  Dell by default: a glyph is warranted where one character
  honestly carries a whole directive or a heavily-used atom.
  Growth beyond the 15 runs the LM-0 census discipline —
  searched, listed, confirmed — never decorative sprawl.
- **Counted in the Meter.** Under the shorthand law (§12.87a /
  DD-30), the glyph form is its own counted system in LM-5:
  the same directive longhand vs glyph-hand, savings reported
  honestly per system.

### Syntax law (Ace, 2026-11-11 ~11:44 CST: "properly syntaxed so that it's easy to use and it's intuitive when you see it")

- **Canonical form: GLYPH + NUMBER, no space** — 🌱08, 🔗14,
  🔄13. This is the form the existing table already uses; the
  incorporation keeps it as *the* form. One glance reads it:
  the **picture** says what it is and how it leans, the
  **number** gives the exact address. Intuition rule: a glyph
  must *picture* its Dell (a seedling for Create, a link for
  Bind, circling arrows for Loop) — a glyph you have to
  memorize against its picture fails the seat.
- **It stands where its atom stands.** A glyph form occupies
  the atom slot in a chain, flowing exactly as `08[Create]`
  does; nothing about chain punctuation changes.
- **Tone rides with position.** A glyph in an atom slot tones
  that atom; a glyph leading a chain tones the whole chain.
  No separate tone syntax is invented — position is the
  syntax, so the written form stays one glance deep.
- **Round-trip rule.** Every glyph form expands on demand to
  `NN[Dell] + tone name`, and every numbered atom with a glyph
  compresses to it. Reading either direction must be lossless
  and obvious.
- **Unknown glyph = honest refusal**, never a guessed Dell —
  the honest-atom law applies to glyphs exactly as to atoms.

### Circuit

- **LM-6 THE GLYPH DOOR** — reconcile the scatter into the one
  table (stale names corrected), teach the front door to READ
  glyphs as input aliases resolving to canonical atoms (parse
  parity test: glyph form ≡ numbered form, same product or the
  glyph refuses), wire the Meter's glyph count. Entry
  precondition: LM-3's mapping exists (a glyph references what
  the composer can name). The census/reconcile half may run
  early, alongside LM-0/LM-1.

## 4.10 LM-7 — THE FRACTAL ZOOM (+ THE HARMONIZATION LAW)

**Status: ADOPTED INTO THE PLAN by Ace, 2026-11-11 15:02 CST**
("Write the fractal-zoom storey into the plan (§15)").
Origin: Ace, voice, 2026-11-11 12:24–12:25 CST — the
fractal-zoom vision, then the harmonization law. Draft of
record: FRACTAL_ZOOM_DRAFT_2026-11-11.md (folded here as-is in
substance). Adoption is NOT implementation authorization:
LM-7 routes through the Director like every LatinMandell
circuit and sits after LM-3/LM-4 in the queue order.

### What Ace ordered (his words, compressed without loss)

- Using weights and fractaling, the AI should be able to
  fractal OUT to understand the meaning of the entire writing
  script; fractal IN to understand the paragraph, then the
  sentences, then the words, then the morphemes; and zoom back
  OUT in reverse to understand the whole script deeply.
- From that deep understanding: what needs to be done to the
  paragraph, which Dells need to be activated, and how things
  relate to each other on a super deep scale — weighing things,
  using neural-network weights and schema, using the Dells.
- Harmonization: we are not just building parts, we are
  harmonizing everything together as one program. When you ask
  DellMatrix something, or do something within it, it considers
  all practical parts that relate — and knows what should be
  used and what should NOT be used.

### Why the design is honest (grounding, verified 2026-11-11)

- The formula (§4.6) is already scale-free: PARSE = SPLIT ×
  STACK × CLASSIFY × MAP is defined per word, then per sentence
  (the function spine). The Zoom is the same formula pointed up
  two more floors — paragraph and script — not a new mechanism.
- Weights exist in two honest kinds, kept separate: **neural
  weights** (the docked AI's deep pattern-reading; DellMatrix
  does not own these — the dock supplies them) and **structural
  weights** (Dell 74[Weight], "Assign relative influence", and
  the program state's weights slice, Diff-compared since
  PR #384). These say what matters most on each floor, in a
  form a receipt can show.
- The word "fractal" exists in the codebase today but is
  picture-pattern tooling only (form/dell_matrix/
  sacred_geometry.py — Rule 90/Mandelbrot/shells, its own note:
  "not scientific proof"; a display label in pillars.py).
  **No meaning-zoom exists yet.** Nobody may cite the
  picture-fractals as evidence for this storey.

### The storey

Precondition: LM-3's composed senses and LM-4's Dell selection
exist. The Zoom extends the §4.6 level table (L1–L5) upward:

| Level | What the AI sees |
|---|---|
| L1 SURFACE | the English word as written |
| L2 PIECES | its Latin morphemes, hyphen-split |
| L3 SENSE | the stacked composed meaning of the pieces |
| L4 FUNCTION | what the word does; function vs fluff |
| L5 RELATION | the Dell (or program function) it maps to |
| L6 SPINE | the sentence's function spine (already in §4.6) |
| L7 PARAGRAPH | stacked spines + inter-sentence relations (cause, contrast, sequence), weighted |
| L8 SCRIPT | the whole writing's stacked meaning: its aim, its parts' relations, what it calls for |

- **ZOOM IN** = apply SPLIT downward: script → paragraphs →
  spines → words → morphemes.
- **ZOOM OUT** = read the STACK upward in reverse; every floor
  keeps its receipt, so a claim at L8 can be traced to the
  morphemes at L2 that carry it.
- **Weights at every floor:** each floor's pieces carry a
  74[Weight] influence; scaffolding floors weigh low,
  meaning-bearing floors weigh high. The docked AI's neural
  reading and the structural weights are reported side by
  side, never blended into one unlabeled number.
- **Honesty carries up, never averages away:** ACCOUNTED and
  MORPHEME-RESOLVED are computed per floor. An UNRESOLVED piece
  at L2 shows as a visible gap at L8 — the script-level reading
  states its own coverage instead of bluffing completeness
  (multiplicative law: a zero floor contributes no fabricated
  product).
- **Output of a full zoom:** (a) the script's deep meaning,
  floor by floor; (b) what needs to be done to a given
  paragraph, and why; (c) the Dell set the writing calls for,
  with the relations between them (which cause, which depend,
  which merely decorate).

### The Ideas Axis (Ace amendment, 2026-11-11 15:03 CST)

The Zoom runs on **ideas**, not only on writing. Ace's ruling:
the fractal zoom works with the full matrix, zooms into one
idea, then into the contents of that idea — hand in hand with
LatinMandell — because the majority of everything in the field
breaks down into tokens of words and letters, and symbols.
Pictures, files, and other attachments come into play too, but
the majority is text, and text is what the zoom reads natively.

- **Field zoom (the idea floors):** MATRIX (the whole field,
  all ideas and their relations) → IDEA (one idea, its stacked
  contents) → CONTENTS (the idea's text, symbols, and
  attachments) → then the word floors take over: sentences →
  words → morphemes (L6→L2). Zooming OUT reverses: morphemes →
  words → the idea's meaning → the idea's place and weight in
  the whole field.
- **Relations between ideas are floors too:** an idea's links,
  causes, dependencies, and groupings (the same slices Dell
  89[Diff] compares) are its L5/L7 relations at field scale —
  the zoom reads *why this idea sits where it sits*, not only
  what it says.
- **Symbols ride the text floors:** Mandellmoji glyphs (§4.9)
  and other symbols are tokens with predisposed meanings
  (LM-0 discipline); they classify and stack like words.
- **Non-text contents — honest ceiling:** a picture or file
  inside an idea is zoomed through what the program can
  checkably read — its name, type, captions, metadata, and any
  text it carries. The *content* of an image (what it depicts)
  is the docked AI's residue, exactly as idiom is (§5 ceilings):
  the zoom reports the attachment's presence and text-layer
  facts and marks the visual layer as dock-read, never as
  program-read. No fabricated description.
- **One zoom, two axes:** writing and ideas are the same
  mechanism at different scales — a script is a field of
  paragraphs; the matrix is a field of ideas. The falsification
  tests apply on both axes (an idea-level claim must trace to
  the idea's contents; a field-level claim to specific ideas).

### The Harmonization Law (Ace, same messages)

- One program, not a pile of parts: any question or action
  inside DellMatrix is answered against **all practical parts
  that relate**, not only the part named in the request.
- Knowing what NOT to use is half the intelligence. Already law
  in the machine, inherited by the Zoom: STORED ≠ ELIGIBLE ≠
  SELECTED ≠ ROUTABLE ≠ USED. A Dell the zoom surfaces is a
  *candidate*; eligibility and selection gates still decide,
  and a refusal is reported honestly, per atom, never smoothed
  into a success.
- Harmonization is a selection discipline, not a merge of
  authorities: no second router, selector, or ledger is created
  by this storey (AGENTS.md §23).

### Falsification tests (what would prove this storey wrong)

1. **Trace test:** pick any L8 claim from a real zoom; if it
   cannot be traced down through L7/L6/L5 to specific L2
   morphemes, the zoom is narration, not mechanism — FAIL.
2. **Ablation test:** remove the top-weighted sentence from a
   paragraph; the L7 reading must change in the direction the
   weights predict. If it doesn't, the weights are decoration.
3. **Refusal test:** feed a script whose honest Dell set is
   empty (pure greeting, no function spine); the zoom must
   return "no Dells called for" rather than inventing work.
4. **Coverage test:** a script with a planted UNRESOLVED word
   must show lowered coverage at every floor above it.

### What LM-7 does NOT do

- Does not authorize any implementation by itself; Director
  routing governs, as for every circuit.
- Does not change the build order: LM-0 (closed, Ace-confirmed)
  → LM-1 → LM-2 → LM-3 → LM-4 → LM-5 → LM-6 → LM-7.
- Does not claim the neural half: deep pattern-reading belongs
  to the docked AI; DellMatrix supplies the checkable skeleton,
  the structural weights, and the receipts.

## 5. GOVERNANCE AND SEQUENCING

- Owner: **Uni builds** (only Uni touches code). Circuits run as
  Director-routed bounded circuits like every Dell circuit: plan
  first, failing-first tests, isolated state, exact-head evidence,
  Director/Keeper dispositions before anything is called done.
- Order: LM-0 (the Census, §4.8) → LM-1 → LM-2 → LM-3 → LM-4 →
  LM-5 → LM-6 (the Glyph Door, §4.9 FINAL FORM 2026-11-11
  ~11:42 CST: glyph = Dell + tone in one token; its table
  reconcile + tone census may run early alongside LM-0/LM-1) →
  LM-7 (the Fractal Zoom + Harmonization Law, §4.10, ADOPTED by
  Ace 2026-11-11 15:02 CST). LM-0 is the next executable action; its one Ace-touch is
  confirming the census tables it produces (definitions are the
  Architect's), and it blocks nothing else in the project while
  it waits.
- The existing LatinMandell behaviors (explain, deepen, customize,
  the Latin door) are **kept** — this plan extends the authority;
  it does not replace it. Customs persist across the table import.
- Honest ceilings, stated now: English contains Germanic and
  other non-Latin stock; those words will decompose partially or
  not at all, and the system must say so per word (UNRESOLVED is a
  lawful output). Morpheme composition gives a *reading* of a
  word's meaning — strong for Latin-derived vocabulary, weaker
  for idiom; idiom stays the docked AI's residue, as ruled for
  Translate in DD-36.
- Entry into force: this plan is ACTIVE at Ace's word
  (2026-11-11). It joins the master work list as the LM series;
  the Director receives it through the Dell plan (§15) and the
  review queue like every other circuit family.

— Uni Ω, 2026-11-11
