# LM-0 — LatinMandell Census — CONFIRMED EDITION

**Date:** 2026-11-11 (candidate census compiled 2026-11-11; confirmation applied 2026-11-11)  
**Status:** CONFIRMED BY ACE — 2026-11-11. This is the confirmed LM-0 record.  
**Source document:** `LM0_CENSUS_2026-11-11.md` — the candidate census, preserved unchanged. This edition carries its tables over and executes Ace's rulings on them; nothing was silently dropped.  
**Scope:** Confirmation and reclassification only. No code was changed and no data table was imported.  
**Governing design:** `LATINMANDELL_BUILD_PLAN_2026-11-11.md`, especially §§2.5, 3, 4.6–4.8.

---

# CONFIRMATION — ACE'S RULINGS APPLIED

Ace's instruction, verbatim (2026-11-11):

> "Confirm the census and make categories for anything that needs its own and promote and put everything in its correct category. Some may end up in multiple categories"

The rulings below (R1–R13) execute that instruction. §11 of this edition maps every ambiguity the census named (A1–A22) to the ruling that disposes of it.

## The rulings

- **R1 — NEW CATEGORY: OPERATOR.** The auxiliaries and modals (the candidate census's §7A, 27 rows) are confirmed members of a new category, **OPERATOR**. They carry tense, aspect, modality, and question-and-negation machinery; their predisposed meanings stand as drafted (e.g. *must* = function-must-necessity-or-strong-inference). They were never FLUFF and never content.
- **R2 — NEW CATEGORY: FOCUS.** The focus and additive particles (the candidate census's §7B, 6 rows: *only, even, just, also, too, as well*) are confirmed members of a new category, **FOCUS**. They restrict, add, or shift focus; moving *only* changes truth conditions.
- **R3 — Articles promoted to POINT.** ***the* → POINT-known** ("point-known — the identifiable one"). ***a/an* → POINT-indefinite** ("point-indefinite-one"); the *a/an* spelling difference is vowel-sound allomorphy — one meaning, not two. The three rows now live in POINT §2G.
- **R4 — FLUFF is CONFIRMED EMPTY.** The category definition is retained — a candidate with no referential, relational, conditional, negative, question, focus, or structural job — and its membership is **zero** after the R3 promotions. Empty FLUFF is the promotion rule succeeding, not a gap: the rule said any "fluff" word carrying even a small job gets promoted, and applied honestly it emptied the drawer.
- **R5 — NEGATE-partial confirmed.** The broad/partial negatives (census §4B, 7 rows) are confirmed as the named subclass **NEGATE-partial** of NEGATE; every gloss carries degree or frequency (*hardly* = almost-reverse-degree-or-amount; *rarely* = almost-reverse-frequency). **A11 applied:** bare *few* = NEGATE-partial; *a few* = POINT-positive — a cross-listed construction pair, with the rule stated at both rows (§2E, §4B).
- **R6 — LINK-discourse confirmed.** The discourse links (census §1D, 18 rows) are confirmed as the named subclass **LINK-discourse** of LINK. The words remain adverbs grammatically — the subclass names the JOB (linking discourse), not a part-of-speech claim.
- **R7 — Expletives ruled.** Dummy *it* and existential *there* are confirmed as **POINT-form with a NO-REFERENT flag** (§2F): the form occupies a pointing slot, the referent is explicitly none. They are never resolved to a fake referent, and never filed as FLUFF.
- **R8 — Multi-category membership is LAW.** A form may hold membership in multiple categories; the parse records the USE. The confirmed use-rules:
  - **Relatives** (*who, which, that, where, when,* …): POINT is the referential home; LINK is a use; ASK applies **only** in genuine questions. (§2D)
  - ***that*:** POINT as demonstrative and relative; LINK as complementizer. (§1B, §2B, §2D)
  - ***whether / if*:** CONDITION for conditional clauses; ASK-construction or LINK for indirect questions, decided by the governing construction — never by spelling alone. (§3)
  - ***when / whenever / once*:** temporal by default (a spine relation); CONDITION only when the clause supplies the governing case for the main clause. (§3)
  - ***without*:** LINK home (preposition, §1E) + NEGATE-absence feature (§4C) + CONDITION use in counterfactual frames (§3).
  - ***neither / nor*:** POINT (determiner/pronoun) + NEGATE (negative force) + LINK (correlative construction). (§1C, §2E, §4A)
  - **The *-ever* family:** ASK only in genuine interrogative syntax; otherwise POINT free-relative or LINK concessive, by construction. (§5)
  Each rule is also stated at the head of every table it affects.
- **R9 — Preposition scope.** The 166 contemporary/general LINK-preposition rows (§1E) are **CONFIRMED for the first build**. The archaic/dialectal/specialized reservoir (§1F) stays **named and UNCONFIRMED** — visible, not absorbed, not deleted.
- **R10 — Infinitive *to* is FUNCTION-structural.** It is a spine structure marker, not a member of any small-word category. (Directional *to* is LINK, §1E.) Complementizer *that* is per R8.
- **R11 — ASK includes constructions.** The question constructions — the *how* + measure compounds, inversion patterns, and tag patterns (§5) — are confirmed as ASK members forming a **construction layer** for LM-2. Question formation is not vocabulary lookup alone.
- **R12 — Numerals and generic pointing.** Numerals, multipliers, and fractions are confirmed as **compositional patterns filed in POINT** (§2E) — patterns, not enumerations. Singular *they* and generic *one* are confirmed as POINT with **referent-type features** (§2A); spelling alone never settles number or referent.
- **R13 — Morpheme side: evidence confirmed, positions NOT settled.** The census counts are confirmed as **LM-1's starting evidence only**: `morpheme.py` 54 typed assignments / 52 normalized union / 57 flat unique pieces; `latinmandell.py` 53 surface roots / 65 unique Latin citation forms; ontology 14 entries contributing *lambda* and *sigma* as new labels; preform 15 candidates, **NOT in use**. Position conflicts (*dell*, *man*, *re*) and project-piece candidates are **LM-1 rulings, NOT settled here**. The free ~1,693-entry roots list is **NOT imported** (LM-1; CC BY-SA discipline).
- **R14 — DESIGN NOTE (Ace addendum, 2026-11-11): pure meaning.** In this system every token's full meaning is defined in advance by the tables; delivery — by computer, AI, nature, or human — may be sloppy, but sloppiness is a surface phenomenon and never makes a token meaningless. FLUFF's emptiness follows from the design itself: the parse recovers designed meaning through sloppy delivery (see §6).

## The category system as confirmed

| category | job | confirmed members |
|---|---|---:|
| LINK (incl. subclass LINK-discourse) | joins words, phrases, clauses, or discourse units; links a complement by a relation | 233 |
| POINT | points at, stands for, or narrows down a referent — including POINT-form with a NO-REFERENT flag | 117 |
| CONDITION | opens a condition, hypothesis, exception, requirement, or counterfactual frame | 34 |
| NEGATE (incl. subclass NEGATE-partial) | reverses, denies, excludes — or partially weakens — a claim | 37 |
| ASK (incl. construction layer) | opens a question and names the shape of the answer wanted | 34 |
| OPERATOR | carries tense, aspect, modality, and question/negation machinery | 27 |
| FOCUS | restricts, adds, or shifts focus | 6 |
| FLUFF | *(definition retained; membership zero — R4)* | 0 |
| **Total cross-listed rows** | | **488** |

## Final recount — the arithmetic

Candidate census: LINK 233 + POINT 114 + CONDITION 34 + NEGATE 37 + ASK 34 + FLUFF 3 + Boundary 33 = **488**.

Confirmation **moves** rows; it creates none and deletes none:

- FLUFF's 3 rows → POINT (R3): POINT 114 + 3 = **117**; FLUFF = **0**.
- The 33 boundary rows → OPERATOR 27 (§7A) + FOCUS 6 (§7B) (R1, R2).

Confirmed: 233 + 117 + 34 + 37 + 34 + 27 + 6 + 0 = **488**. The grand total still counts **cross-listed rows, not unique spellings** — multi-category membership is law (R8), so the total reconciling to 488 is a check on this edition, not a claim that English has 488 closed-class words.

## What confirmation does and does not do

- Confirmed small-word tables are the input to **LM-2**.
- Confirmed morpheme counts are **LM-1's starting evidence only** — not a finished morpheme table (R13).
- The §1F reservoir stays unconfirmed (R9). Unconfirmed material never passes forward as if it were confirmed.
- A handful of rows still carry notes that argue with their confirmed placement. They are **kept**, and the tensions are listed in §14 FLAGS rather than silently edited away.

---

# HOW TO READ THIS CONFIRMED EDITION

- **Confirmed member** means the row's category and drafted meaning stand as ruled by Ace (R1–R13). Rows are confirmed unless a section says otherwise — the §1F reservoir is the standing exception: named, **UNCONFIRMED**.
- **Drafted meaning** is written in the plan's terse style: `and = join-both`, `unless = condition-except`, `why = asks-for-cause`. These predisposed meanings are the confirmed starting tables for LM-2.
- **Source** uses short source keys defined in §12 (Source and License Accounting). A section-level source supports ordinary members of that section; non-obvious candidates carry a note.
- **Notes/ambiguity** name dual uses, register limits, and promotions. A note is part of the record, not decoration. Where a note still argues with the confirmed placement, the row is kept and the tension is listed in §14 FLAGS.
- **Multi-category membership is law (R8).** The same spelling can legitimately appear in more than one table when its job changes by use — *neither*, *whether*, *when*, *without*, and the relative pronouns are the clearest examples. The parse records the use.
- **Subclasses** (LINK-discourse, NEGATE-partial) name a job inside a category; they are not new top-level categories and not part-of-speech claims.
- **Reservoir** means attested or listed material held visible for a later ruling — not confirmed membership.
- Multiword candidates count as one construction when they work as one unit.
- Productive patterns — especially numerals and `how + adjective/adverb` — are counted once as patterns; pretending to enumerate an open pattern would be false exhaustiveness.

---

# 1. LINK

**Job:** joins words, phrases, clauses, or discourse units, or links a complement to the rest of the sentence.

**Section sources:** Lancaster University closed-class inventory; ELT Concourse function-word inventory; Martin Weisser's word-class treatment; Quillbot on correlative conjunctions; Wikipedia, “List of English prepositions.” See Source and License Accounting for full citations and license status.

## 1A. Coordinating conjunctions

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| and | join-both | PLAN §4.7; LAN-CLOSED | Core coordinator; also starts correlative frames. |
| or | choice-either | PLAN §4.7; LAN-CLOSED | Core coordinator; also closes *either/whether* frames. |
| but | join-contrast | ELT-FUNCTION | Coordinator; unrelated preposition use means *except* — see preposition table. |
| yet | join-contrast-still | ELT-FUNCTION | Coordinator or time adverb; conjunction use belongs here. |
| nor | join-negative-other | ELT-FUNCTION; GRAM-NEG | Negative coordinator; dual-class with NEGATE. |
| so | link-result | ELT-FUNCTION | Coordinator in informal/general use; also degree/result uses. |
| for | link-reason | ELT-FUNCTION | Formal coordinator use; far more often a preposition. Use-sensitive. |

## 1B. Subordinating and clause-linking conjunctions

**Use rules (R8):** *that* as complementizer is LINK here; its demonstrative use is POINT (§2B) and its relative use is POINT home + LINK use (§2D). *Whether/if* introducing indirect questions are classified by the governing construction (CONDITION §3 / ASK §5), not by spelling.

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| because | link-cause | LAN-CLOSED | Clear reason link. |
| since | link-cause-or-time-from | LAN-CLOSED | Cause and time uses; do not confuse with CONDITION. |
| as | link-as-role-time-cause-or-manner | LAN-CLOSED | Highly polyfunctional; classification must follow use. |
| now that | link-new-cause | ELT-FUNCTION | Multiword reason link. |
| seeing that | link-given-cause | ELT-FUNCTION | Formal/given-reason link. |
| seeing as | link-given-cause | ELT-FUNCTION | Informal variant of *seeing that*. |
| although | link-contrast-despite | LAN-CLOSED | Concessive link. |
| though | link-contrast-despite | LAN-CLOSED | Concessive link; sentence-final adverb use is discourse, not this row. |
| even though | link-strong-contrast-despite | ELT-FUNCTION | Stronger factual concession than *even if*. |
| while | link-time-or-contrast | LAN-CLOSED | Temporal or concessive/contrastive; conditional-like use is borderline. |
| whereas | link-contrast | ELT-FUNCTION | Formal contrast link. |
| whilst | link-time-or-contrast | ELT-FUNCTION | Chiefly British/formal variant of *while*. |
| after | link-time-after | LAN-CLOSED | Clause-link use; also preposition/adverb. |
| before | link-time-before | LAN-CLOSED | Clause-link use; also preposition/adverb. |
| until | link-time-up-to | LAN-CLOSED | Clause-link use; also preposition. |
| till | link-time-up-to | LAN-CLOSED | Informal variant of *until* in this use. |
| as soon as | link-time-immediately-after | ELT-FUNCTION | Primarily temporal; condition-like sequence use named in CONDITION. |
| as far as | link-extent-or-topic | ELT-FUNCTION | Often in *as far as X is concerned*; not a spatial preposition in this construction. |
| as if | link-as-if-manner-or-comparison | ELT-FUNCTION | Comparison/manner link; can introduce an unreal comparison. |
| as though | link-as-if-manner-or-comparison | ELT-FUNCTION | Variant of *as if*. |
| so that | link-purpose-or-result | ELT-FUNCTION | Purpose versus result must be read from context. |
| in order that | link-purpose | ELT-FUNCTION | Formal purpose link. |
| lest | link-negative-purpose | ELT-FUNCTION | “So that … not”; NEGATE-adjacent but its clause job is linking purpose. |
| that | link-clause-content | LAN-CLOSED | Complementizer/relative uses; relative use dual-classes with POINT. |
| than | link-comparison-after | ELT-FUNCTION | Comparison link; also listed as a preposition in some inventories. |
| like | link-comparison-like | ELT-FUNCTION | Conjunction use is common but disputed in formal grammar; preposition use is separate. |

## 1C. Correlative pairs and paired constructions

**Use rules (R8):** *neither … nor* is a triple member — POINT for *neither* as determiner/pronoun (§2E), NEGATE for the negative force (§4A), LINK here for the correlative construction. *Whether … or* belongs to CONDITION or ASK by governing construction (§3, §5).

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| both … and | join-both-pair | QUI-CORREL | Core correlative pair. |
| either … or | choice-either-pair | QUI-CORREL | Core correlative pair. |
| neither … nor | join-negative-pair | QUI-CORREL; GRAM-NEG | Core negative pair; dual-class with NEGATE and POINT for *neither*. |
| not only … but also | join-add-emphasis-pair | QUI-CORREL | Core correlative pair; initial *not* does not negate the whole claim. |
| whether … or | alternative-pair | QUI-CORREL | Alternative frame; dual-class with CONDITION/ASK by construction. |
| as … as | comparison-equal-pair | QUI-CORREL | Extended correlative/comparison construction. |
| as many … as | comparison-equal-count-pair | QUI-CORREL | Productive comparison frame. |
| as much … as | comparison-equal-amount-pair | QUI-CORREL | Productive comparison frame. |
| just as … so | comparison-parallel-pair | QUI-CORREL | Extended correlative construction. |
| no sooner … than | time-immediate-pair | QUI-CORREL; GRAM-NEG | Negative/time pair; also named under NEGATE boundary. |
| hardly … when | time-immediate-pair | QUI-CORREL; GRAM-NEG | Partial-negative/time pair. |
| scarcely … when | time-immediate-pair | QUI-CORREL; GRAM-NEG | Partial-negative/time pair. |
| rather … than | preference-pair | QUI-CORREL | Disputed as a true correlative; retained as a paired construction candidate. |
| so … that | degree-result-pair | QUI-CORREL | Degree in first clause, result in second. |
| such … that | kind-result-pair | QUI-CORREL | Kind/degree-result construction. |
| the … the | comparison-proportional-pair | QUI-CORREL | Comparative correlative: *the more … the better*. Productive pattern. |

## 1D. Conjunctive / discourse links — LINK-discourse subclass (CONFIRMED, R6)

These words and phrases link discourse, but they are not all conjunctions in strict grammar. **CONFIRMED (R6): they are members of LINK in the named subclass LINK-discourse.** The subclass names the JOB — linking discourse — not a part-of-speech claim; the words remain adverbs grammatically. **Use rule (R8):** *otherwise* also carries a CONDITION use (the consequence if not, §3) — the parse records the use; its discourse home is here.

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| however | link-contrast-discourse | ELT-FUNCTION | Discourse adverb; also degree use in *however much*. |
| therefore | link-result-discourse | ELT-FUNCTION | Discourse/result adverb. |
| thus | link-result-discourse | ELT-FUNCTION | Result/manner adverb. |
| hence | link-result-discourse | ELT-FUNCTION | Result adverb; also time-from-now use. |
| consequently | link-result-discourse | ELT-FUNCTION | Result adverb. |
| moreover | link-add-discourse | ELT-FUNCTION | Addition adverb. |
| furthermore | link-add-discourse | ELT-FUNCTION | Addition adverb. |
| nevertheless | link-contrast-despite-discourse | ELT-FUNCTION | Concessive discourse adverb. |
| nonetheless | link-contrast-despite-discourse | ELT-FUNCTION | Concessive discourse adverb. |
| meanwhile | link-time-parallel-discourse | ELT-FUNCTION | Parallel-time discourse adverb. |
| instead | link-replacement-discourse | ELT-FUNCTION | Replacement adverb; phrase *instead of* is in the preposition table. |
| otherwise | link-negative-condition-discourse | ELT-FUNCTION | “If not” discourse consequence; also CONDITION boundary. |
| besides | link-add-discourse | ELT-FUNCTION | Adverb use; preposition uses are separate. |
| accordingly | link-result-discourse | ELT-FUNCTION | Result adverb. |
| likewise | link-similar-discourse | ELT-FUNCTION | Similarity/addition adverb. |
| similarly | link-similar-discourse | ELT-FUNCTION | Similarity adverb. |
| finally | link-sequence-last-discourse | ELT-FUNCTION | Sequence adverb; also eventual-time use. |
| then | link-sequence-next | ELT-FUNCTION | Sequence/result use; primarily temporal adverb in other uses. |


## 1E. Linking prepositions — contemporary/general inventory

A preposition is LINK here because it attaches a complement and expresses a relation — place, time, direction, role, cause, topic, exception, comparison, accompaniment, and similar relations. The drafted meaning names the central relation; it is not a claim that one gloss covers every idiom.

**Confirmation status (R9):** these 166 contemporary/general rows are CONFIRMED for the first build. **Use rule (R8):** *without* has its home here in LINK; it also carries a NEGATE-absence feature (§4C) and a CONDITION use in counterfactual frames (§3) — the parse records the use.

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| aboard | link-on-board | WIKI-PREP | Single-word preposition. |
| about | link-about-topic-or-around | WIKI-PREP | Single-word preposition. |
| above | link-above-higher-than | WIKI-PREP | Single-word preposition. |
| abreast | link-side-by-side-with | WIKI-PREP | Single-word preposition. |
| absent | link-absent-without | WIKI-PREP | Single-word preposition. |
| across | link-across-from-side-to-side | WIKI-PREP | Single-word preposition. |
| after | link-after-in-time-or-behind | WIKI-PREP | Single-word preposition. |
| against | link-against-contact-or-opposition | WIKI-PREP | Single-word preposition. |
| aloft | link-aloft-above | WIKI-PREP | Single-word preposition. |
| along | link-along-length-of | WIKI-PREP | Single-word preposition. |
| alongside | link-beside-alongside | WIKI-PREP | Single-word preposition. |
| amid | link-amid-middle-of | WIKI-PREP | Single-word preposition. |
| amidst | link-amid-middle-of | WIKI-PREP | Single-word preposition. |
| among | link-among-group | WIKI-PREP | Single-word preposition. |
| amongst | link-among-group | WIKI-PREP | Single-word preposition. |
| anti | link-against-opposed-to | WIKI-PREP | Single-word preposition. |
| apropos | link-regarding-topic | WIKI-PREP | Single-word preposition. |
| around | link-around-surrounding-or-near | WIKI-PREP | Single-word preposition. |
| round | link-around-surrounding | WIKI-PREP | Single-word preposition. |
| as | link-as-role-or-capacity | WIKI-PREP | Role/capacity and comparison uses; clause-link uses are in §1B. |
| aslant | link-slanting-across | WIKI-PREP | Single-word preposition. |
| astride | link-astride-across-both-sides | WIKI-PREP | Single-word preposition. |
| at | link-at-point | WIKI-PREP | Single-word preposition. |
| atop | link-on-top-of | WIKI-PREP | Single-word preposition. |
| bar | link-except-for | WIKI-PREP | Single-word preposition. |
| barring | link-except-unless | WIKI-PREP | Single-word preposition. |
| before | link-before-in-time-or-place | WIKI-PREP | Single-word preposition. |
| behind | link-behind-at-back-of | WIKI-PREP | Single-word preposition. |
| below | link-below-lower-than | WIKI-PREP | Single-word preposition. |
| beneath | link-beneath-under | WIKI-PREP | Single-word preposition. |
| beside | link-beside-at-side-of | WIKI-PREP | Single-word preposition. |
| besides | link-in-addition-to-or-except | WIKI-PREP | Single-word preposition. |
| between | link-between-two-or-more | WIKI-PREP | Single-word preposition. |
| beyond | link-beyond-farther-than | WIKI-PREP | Single-word preposition. |
| but | link-except-for | WIKI-PREP | Preposition use means except; coordinator use is in §1A. |
| by | link-by-agent-means-near-or-no-later-than | WIKI-PREP | Single-word preposition. |
| chez | link-at-home-or-business-of | WIKI-PREP | Borrowed/formal; general but specialized. |
| circa | link-about-approximately-at | WIKI-PREP | Single-word preposition. |
| concerning | link-concerning-about | WIKI-PREP | Single-word preposition. |
| contra | link-against-in-opposition | WIKI-PREP | Single-word preposition. |
| counting | link-including-in-count | WIKI-PREP | Single-word preposition. |
| cum | link-with-combined-with | WIKI-PREP | Single-word preposition. |
| despite | link-despite-contrast | WIKI-PREP | Single-word preposition. |
| down | link-down-direction-or-lower | WIKI-PREP | Single-word preposition. |
| during | link-during-through-time | WIKI-PREP | Single-word preposition. |
| effective | link-effective-from-date | WIKI-PREP | Single-word preposition. |
| ere | link-before-in-time | WIKI-PREP | Archaic/formal; retained in the contemporary list only because the source inventory lists it — Ace may move it to reservoir. |
| except | link-except-excluding | WIKI-PREP | Single-word preposition. |
| excepting | link-except-excluding | WIKI-PREP | Single-word preposition. |
| excluding | link-excluding-not-counting | WIKI-PREP | Single-word preposition. |
| failing | link-for-lack-of | WIKI-PREP | Single-word preposition. |
| following | link-following-after-or-as-result | WIKI-PREP | Single-word preposition. |
| for | link-for-purpose-recipient-or-duration | WIKI-PREP | Preposition uses are broader than its formal coordinator use. |
| from | link-from-source-origin | WIKI-PREP | Single-word preposition. |
| in | link-in-inside-or-within-time | WIKI-PREP | Single-word preposition. |
| including | link-including-as-part | WIKI-PREP | Single-word preposition. |
| inside | link-inside-within | WIKI-PREP | Single-word preposition. |
| into | link-into-entering-or-changing-to | WIKI-PREP | Single-word preposition. |
| less | link-less-minus | WIKI-PREP | Single-word preposition. |
| like | link-like-similar-to | WIKI-PREP | Preposition use is standard; conjunction use is usage-sensitive. |
| minus | link-minus-subtracted | WIKI-PREP | Single-word preposition. |
| modulo | link-modulo-excepting-or-under-relation | WIKI-PREP | Single-word preposition. |
| near | link-near-close-to | WIKI-PREP | Single-word preposition. |
| next | link-next-beside | WIKI-PREP | Single-word preposition. |
| notwithstanding | link-despite-contrast | WIKI-PREP | Single-word preposition. |
| of | link-of-part-source-or-belonging | WIKI-PREP | Plan starter example: part-of / belonging; source/material senses also occur. |
| off | link-off-away-from-or-not-on | WIKI-PREP | Single-word preposition. |
| offshore | link-offshore-away-from-shore | WIKI-PREP | Single-word preposition. |
| on | link-on-surface-topic-or-time | WIKI-PREP | Single-word preposition. |
| onto | link-onto-moving-to-surface | WIKI-PREP | Single-word preposition. |
| opposite | link-opposite-facing | WIKI-PREP | Single-word preposition. |
| out | link-out-outside-or-away | WIKI-PREP | Single-word preposition. |
| outside | link-outside-exterior-to | WIKI-PREP | Single-word preposition. |
| over | link-over-above-across-or-more-than | WIKI-PREP | Single-word preposition. |
| pace | link-with-due-respect-to | WIKI-PREP | Single-word preposition. |
| past | link-past-beyond-or-after | WIKI-PREP | Single-word preposition. |
| pending | link-pending-until-or-awaiting | WIKI-PREP | Single-word preposition. |
| per | link-per-each-or-by-means | WIKI-PREP | Single-word preposition. |
| plus | link-plus-added-to | WIKI-PREP | Single-word preposition. |
| post | link-after-in-time | WIKI-PREP | Single-word preposition. |
| pre | link-before-in-time | WIKI-PREP | Single-word preposition. |
| pro | link-for-in-support-of | WIKI-PREP | Single-word preposition. |
| qua | link-in-capacity-of | WIKI-PREP | Formal capacity marker. |
| re | link-regarding-about | WIKI-PREP | Business/formal “regarding.” |
| regarding | link-regarding-about | WIKI-PREP | Single-word preposition. |
| respecting | link-regarding-about | WIKI-PREP | Single-word preposition. |
| sans | link-without-lacking | WIKI-PREP | Formal/humorous; NEGATE boundary because it marks absence. |
| save | link-except-for | WIKI-PREP | Single-word preposition. |
| saving | link-except-for | WIKI-PREP | Single-word preposition. |
| short | link-short-of-less-than | WIKI-PREP | Single-word preposition. |
| since | link-since-from-time-or-cause | WIKI-PREP | Single-word preposition. |
| sub | link-under-formal | WIKI-PREP | Formal/technical “under.” |
| than | link-than-comparison-after | WIKI-PREP | Some grammars classify this only as a conjunction; retained because standard preposition inventories list it. |
| through | link-through-passing-across-or-by-means | WIKI-PREP | Single-word preposition. |
| throughout | link-throughout-all-of | WIKI-PREP | Single-word preposition. |
| till | link-until-up-to-time | WIKI-PREP | Single-word preposition. |
| times | link-times-multiplied-by | WIKI-PREP | Single-word preposition. |
| to | link-to-destination-direction-or-recipient | WIKI-PREP | Single-word preposition. |
| touching | link-concerning-about | WIKI-PREP | Single-word preposition. |
| toward | link-toward-in-direction-of | WIKI-PREP | Single-word preposition. |
| towards | link-toward-in-direction-of | WIKI-PREP | Single-word preposition. |
| under | link-under-below-or-subject-to | WIKI-PREP | Single-word preposition. |
| underneath | link-underneath-below | WIKI-PREP | Single-word preposition. |
| unlike | link-unlike-different-from | WIKI-PREP | Single-word preposition. |
| until | link-until-up-to-time | WIKI-PREP | Single-word preposition. |
| unto | link-to-formal-or-archaic | WIKI-PREP | Single-word preposition. |
| up | link-up-direction-or-along | WIKI-PREP | Single-word preposition. |
| upon | link-on-formal | WIKI-PREP | Single-word preposition. |
| versus | link-versus-against-or-compared-with | WIKI-PREP | Single-word preposition. |
| via | link-via-by-way-of | WIKI-PREP | Single-word preposition. |
| vice | link-in-place-of | WIKI-PREP | Single-word preposition. |
| vis-à-vis | link-in-relation-to-or-facing | WIKI-PREP | Formal relation/comparison marker. |
| wanting | link-lacking-without | WIKI-PREP | Single-word preposition. |
| with | link-with-accompaniment-means-or-having | WIKI-PREP | Accompaniment/instrument/attribute relations; not one narrow gloss. |
| within | link-within-inside-or-before-limit | WIKI-PREP | Single-word preposition. |
| without | link-without-absence-or-not-having | WIKI-PREP | Core absence preposition; NEGATE and CONDITION boundary uses are named separately. |
| worth | link-worth-value-of | WIKI-PREP | Single-word preposition. |
| according to | link-according-to-basis-or-report | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| across from | link-opposite-across-from | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| ahead of | link-ahead-before-or-in-front-of | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| along with | link-together-with | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| apart from | link-apart-from-except-or-separate | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| as for | link-as-for-topic | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| as of | link-as-of-from-date | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| as per | link-as-per-according-to | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| as regards | link-regarding-about | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| as to | link-as-to-about-or-concerning | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| aside from | link-aside-from-except-or-besides | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| away from | link-away-from-source | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| because of | link-because-of-cause | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| counter to | link-counter-to-opposite | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| except for | link-except-for-exclusion | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| instead of | link-instead-of-replacement | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| near to | link-near-to-close | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| next to | link-next-to-beside | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| out of | link-out-of-source-inside-or-lack | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| outside of | link-outside-of-exterior | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| owing to | link-owing-to-cause | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| up against | link-up-against-contact-or-opposition | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| up to | link-up-to-as-far-or-until | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| by means of | link-by-means-of-method | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| in accordance with | link-in-accordance-with-rule | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| in addition to | link-in-addition-to-extra | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| in case of | link-in-case-of-condition-or-event | WIKI-PREP | Complex preposition naming an event contingency; close CONDITION boundary. |
| in front of | link-in-front-of-before | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| in lieu of | link-in-lieu-of-instead | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| in place of | link-in-place-of-instead | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| in spite of | link-in-spite-of-despite | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| on account of | link-on-account-of-cause | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| on behalf of | link-on-behalf-of-for-another | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| on top of | link-on-top-of-above-or-in-addition | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| with the exception of | link-with-exception-of-excluding | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| due to | link-due-to-cause | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| in terms of | link-in-terms-of-frame | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| in regard to | link-regarding-about | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| with regard to | link-regarding-about | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| by way of | link-by-way-of-route-or-method | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| in the light of | link-in-light-of-considering | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| in view of | link-in-view-of-considering | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| on the basis of | link-on-basis-of-ground | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| for the sake of | link-for-sake-of-benefit-or-purpose | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| with respect to | link-with-respect-to-regarding | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| at the expense of | link-at-expense-of-cost | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| in exchange for | link-in-exchange-for-trade | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| prior to | link-prior-to-before | WIKI-PREP | Complex preposition construction; counted as one candidate. |
| subsequent to | link-subsequent-to-after | WIKI-PREP | Complex preposition construction; counted as one candidate. |

## 1F. LINK reservoir — named, not silently absorbed

**Status under confirmation (R9): UNCONFIRMED.** These forms stay visible — not absorbed into the confirmed table, not deleted. They are not part of the 488 confirmed rows.

The standard preposition inventory also contains a large archaic, dialectal, legal, nautical, or otherwise specialized reservoir. Named examples include **abaft, abeam, ablow, aboon, acrost, adown, afore, athwart, betwixt, dehors, forby, gainst, intil, outwith, sith, thwart,** and **yond**. These are **not counted in the 166 contemporary/general preposition rows** and are not proposed as first-build membership. They remain visible as prior-art candidates if Ace later wants historical or dialect coverage.

English also has a small postposition-like reservoir — notably **ago** in *two days ago*, plus separated uses such as **apart** and **aside** — where the relational word follows its complement. These are not counted as ordinary prepositions above.

**LINK subtotal (CONFIRMED):** 7 coordinating + 26 clause-linking + 16 correlative + 18 discourse (LINK-discourse subclass, R6) + 166 prepositions (R9) = **233 rows**.

---

# 2. POINT

**Job:** points at, stands for, or narrows down a person, thing, place, time, quantity, or previously introduced referent.

**Section sources:** Lancaster University closed-class inventory; ELT Concourse function-word inventory; Wikipedia, “English pronouns”; standard determiner ordering (predeterminer / central determiner / postdeterminer). See Source and License Accounting.

## 2A. Personal and possessive pronoun paradigm

Each surface form is a separate row because LatinMandell classifies tokens, not lemmas.

**Referent-type rule (R12):** singular *they* and generic *one* are CONFIRMED as POINT with referent-type features — *they* may point to a group, a known singular person, or an unspecified person; *one* may be a generic pronoun, a numeral, a determiner, or a substitute noun. Spelling alone never settles number or referent; the parse records the feature.

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| I | point-speaker-subject | WIKI-PRON | First person singular subject. |
| me | point-speaker-object | WIKI-PRON | First person singular object/complement. |
| my | point-speaker-own-before-noun | WIKI-PRON | Possessive determiner. |
| mine | point-speaker-own-standalone | WIKI-PRON | Independent possessive. |
| myself | point-speaker-self | WIKI-PRON | Reflexive/intensifier. |
| we | point-speaker-group-subject | WIKI-PRON | First person plural subject; group boundary can be vague. |
| us | point-speaker-group-object | WIKI-PRON | First person plural object/complement. |
| our | point-speaker-group-own-before-noun | WIKI-PRON | Possessive determiner. |
| ours | point-speaker-group-own-standalone | WIKI-PRON | Independent possessive. |
| ourselves | point-speaker-group-self | WIKI-PRON | Reflexive/intensifier. |
| you | point-hearer-subject-or-object | WIKI-PRON | Second person; singular/plural ambiguity is real. |
| your | point-hearer-own-before-noun | WIKI-PRON | Possessive determiner. |
| yours | point-hearer-own-standalone | WIKI-PRON | Independent possessive. |
| yourself | point-hearer-self-singular | WIKI-PRON | Reflexive/intensifier. |
| yourselves | point-hearer-self-plural | WIKI-PRON | Reflexive/intensifier. |
| he | point-male-third-subject | WIKI-PRON | Third person masculine subject. |
| him | point-male-third-object | WIKI-PRON | Third person masculine object/complement. |
| his | point-male-third-own | WIKI-PRON | Both possessive determiner and independent possessive uses. |
| himself | point-male-third-self | WIKI-PRON | Reflexive/intensifier. |
| she | point-female-third-subject | WIKI-PRON | Third person feminine subject. |
| her | point-female-third-object-or-own-before-noun | WIKI-PRON | Object pronoun and possessive determiner share the form. |
| hers | point-female-third-own-standalone | WIKI-PRON | Independent possessive. |
| herself | point-female-third-self | WIKI-PRON | Reflexive/intensifier. |
| it | point-thing-third-subject-or-object | WIKI-PRON | Ordinary referential use here; dummy/weather use is separately flagged in §2F. |
| its | point-thing-third-own-before-noun | WIKI-PRON | Possessive determiner; do not confuse with contraction *it's*. |
| itself | point-thing-third-self | WIKI-PRON | Reflexive/intensifier. |
| they | point-third-group-or-unknown-subject | WIKI-PRON | Plural and singular/unknown-referent uses. |
| them | point-third-group-or-unknown-object | WIKI-PRON | Plural and singular/unknown-referent uses. |
| their | point-third-group-or-unknown-own-before-noun | WIKI-PRON | Possessive determiner. |
| theirs | point-third-group-or-unknown-own-standalone | WIKI-PRON | Independent possessive. |
| themselves | point-third-group-self | WIKI-PRON | Reflexive/intensifier. |
| themself | point-third-unknown-self | WIKI-PRON | Singular reflexive variant; usage varies. |
| one | point-generic-person | WIKI-PRON | Generic pronoun use; numeral/determiner uses are separate. |
| one's | point-generic-person-own | WIKI-PRON | Generic possessive. |
| oneself | point-generic-person-self | WIKI-PRON | Generic reflexive. |

## 2B. Demonstratives and deictic determiners

**Use rule (R8):** *that* here is the POINT demonstrative. The same form as complementizer is LINK (§1B); as a relative it is POINT home + LINK use (§2D). One form, membership by use.

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| this | point-near-singular | PLAN §4.7; WIKI-PRON | Near demonstrative, pronoun or determiner. |
| that | point-far-singular | PLAN §4.7; WIKI-PRON | Far demonstrative; complementizer/relative uses dual-class with LINK. |
| these | point-near-plural | WIKI-PRON | Near demonstrative plural. |
| those | point-far-plural | WIKI-PRON | Far demonstrative plural. |
| such | point-that-kind-or-degree | ELT-FUNCTION | Determiner/pronoun-like; can participate in *such … that*. |
| yon | point-far-visible | WIKI-PREP; ELT-FUNCTION | Archaic/dialectal reservoir candidate. |
| yonder | point-far-place-or-visible | ELT-FUNCTION | Archaic/dialectal reservoir candidate; often adverbial. |

## 2C. Reciprocals

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| each other | point-each-to-other | WIKI-PRON | Reciprocal construction; counted as one. |
| each other's | point-each-to-other-own | WIKI-PRON | Reciprocal possessive. |
| one another | point-each-to-other-group | WIKI-PRON | Reciprocal construction; often preferred for groups. |
| one another's | point-each-to-other-group-own | WIKI-PRON | Reciprocal possessive. |

## 2D. Relative forms — POINT home, LINK use (CONFIRMED, R8)

These forms point back to an antecedent. Their clause-linking job is real, so the classification is **POINT home + LINK use** — **CONFIRMED as law (R8): multi-category membership is recorded, and the parse records the USE.** They become ASK only in genuine questions; interrogative rows are cross-listed in §5.

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| who | point-back-person-subject | WIKI-PRON | Relative or interrogative. |
| whom | point-back-person-object | WIKI-PRON | Relative or interrogative; formal object form. |
| whose | point-back-own | WIKI-PRON | Relative/interrogative possessive; antecedent need not be a person in modern use. |
| which | point-back-thing-or-choice | WIKI-PRON | Relative or interrogative. |
| what | point-back-thing-unspecified | WIKI-PRON | Free-relative and interrogative uses; standard restrictive-relative use is limited. |
| where | point-back-place | WIKI-PRON | Relative adverb; interrogative use in ASK. |
| when | point-back-time | WIKI-PRON | Relative adverb; temporal/CONDITION ambiguity in other uses. |
| why | point-back-reason | WIKI-PRON | Relative use as in *the reason why*; interrogative use in ASK. |
| whoever | point-back-any-person | WIKI-PRON | Free-relative or concessive; genuine question use is rare. |
| whomever | point-back-any-person-object | WIKI-PRON | Free-relative object form. |
| whatever | point-back-any-thing | WIKI-PRON | Free-relative, determiner, or concessive; not automatically ASK. |
| whichever | point-back-any-choice | WIKI-PRON | Free-relative/determiner or concessive. |
| wherever | point-back-any-place | WIKI-PRON | Free-relative/concessive adverb. |
| whenever | point-back-any-time | WIKI-PRON | Free-relative/concessive adverb; temporal/CONDITION boundary. |
| however | point-back-any-manner-or-degree | WIKI-PRON | Free-relative/concessive use; discourse-contrast use is in LINK. |

## 2E. Indefinite pronouns and determiner-like POINT forms

**Pattern rule (R12):** numerals, multipliers, and fractions in this table are CONFIRMED as compositional PATTERNS filed in POINT — patterns, not enumerations; LM-1/LM-2 parse their composition. **Pair rule (R5):** *a few* is POINT-positive; bare *few* is NEGATE-partial (§4B) — a cross-listed construction pair, with the rule stated at both rows.

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| someone | point-unspecified-person | WIKI-PRON | Indefinite pronoun. |
| somebody | point-unspecified-person | WIKI-PRON | Indefinite pronoun. |
| something | point-unspecified-thing | WIKI-PRON | Indefinite pronoun. |
| somewhere | point-unspecified-place | WIKI-PRON | Indefinite place form. |
| anyone | point-any-person | WIKI-PRON | Indefinite; common in questions/negatives and free-choice uses. |
| anybody | point-any-person | WIKI-PRON | Indefinite pronoun. |
| anything | point-any-thing | WIKI-PRON | Indefinite pronoun. |
| anywhere | point-any-place | WIKI-PRON | Indefinite place form; negative contexts can mean no place. |
| everyone | point-every-person | WIKI-PRON | Universal indefinite. |
| everybody | point-every-person | WIKI-PRON | Universal indefinite. |
| everything | point-every-thing | WIKI-PRON | Universal indefinite. |
| everywhere | point-every-place | WIKI-PRON | Universal place form. |
| no one | point-no-person | WIKI-PRON; GRAM-NEG | Also a NEGATE construction; POINT home because it supplies the referent class. |
| no-one | point-no-person | WIKI-PRON; GRAM-NEG | Hyphenated variant; counted separately as a surface candidate. |
| nobody | point-no-person | WIKI-PRON; GRAM-NEG | Also NEGATE. |
| nothing | point-no-thing | WIKI-PRON; GRAM-NEG | Also NEGATE. |
| nowhere | point-no-place | WIKI-PRON; GRAM-NEG | Also NEGATE. |
| all | point-all-or-whole | ELT-FUNCTION | Predeterminer, determiner, or pronoun depending on use. |
| both | point-two-together | ELT-FUNCTION | Predeterminer/determiner/pronoun; starts correlative frame. |
| half | point-half-part | ELT-FUNCTION | Predeterminer/fraction pattern. |
| each | point-each-separately | ELT-FUNCTION | Distributive determiner/pronoun. |
| every | point-every-separately-all | ELT-FUNCTION | Distributive determiner. |
| either | point-one-of-two | ELT-FUNCTION | Determiner/pronoun; correlative and NEGATE-adjacent uses. |
| neither | point-not-one-of-two | ELT-FUNCTION; GRAM-NEG | Determiner/pronoun; NEGATE and LINK correlative dual-class. |
| any | point-any-or-no-particular | ELT-FUNCTION | Determiner/pronoun; polarity-sensitive uses. |
| some | point-some-unspecified-amount-or-part | ELT-FUNCTION | Determiner/pronoun. |
| no | point-no-amount-or-instance | ELT-FUNCTION; GRAM-NEG | Determiner use; answer/negation use in NEGATE. |
| another | point-other-one | ELT-FUNCTION | Determiner/pronoun. |
| other | point-other-or-rest | ELT-FUNCTION | Determiner/adjective-like form. |
| others | point-other-ones | WIKI-PRON | Independent plural form. |
| enough | point-enough-sufficient | ELT-FUNCTION | Determiner/pronoun/adverb uses. |
| few | point-few-small-number | ELT-FUNCTION | Positive small quantity. Pair rule (R5): *a few* = POINT-positive (this table); bare *few* = NEGATE-partial (§4B). Not a full negative. |
| fewer | point-fewer-smaller-number | ELT-FUNCTION | Comparative quantifier. |
| less | point-less-smaller-amount | ELT-FUNCTION | Comparative quantifier; preposition use is separate. |
| little | point-little-small-amount | ELT-FUNCTION | Amount use; size adjective use is FUNCTION/content, and degree use is NEGATE-partial boundary. |
| many | point-many-large-number | ELT-FUNCTION | Quantifier. |
| more | point-more-greater-amount-or-number | ELT-FUNCTION | Comparative quantifier/determiner. |
| most | point-most-greatest-part | ELT-FUNCTION | Superlative quantifier/determiner. |
| much | point-much-large-amount | ELT-FUNCTION | Quantifier. |
| several | point-several-more-than-two | ELT-FUNCTION | Quantifier/pronoun. |
| none | point-none-no-amount-or-one | WIKI-PRON; GRAM-NEG | Pronoun; also NEGATE. |
| ones | point-ones-substitute-plural | WIKI-PRON | Substitute pronoun use, as in *the red ones*. |
| same | point-same-identical | ELT-FUNCTION | Usually in *the same*; identity-pointing job. |
| certain | point-certain-some-known | ELT-FUNCTION | Indefinite-specific determiner use; certainty adjective use is separate. |
| double | point-double-two-times | ELT-FUNCTION | Multiplier predeterminer pattern representative. |
| twice | point-twice-two-times | ELT-FUNCTION | Multiplier predeterminer use in phrases such as *twice the size*. |
| three times | point-multiplier-pattern | ELT-FUNCTION | Representative of the open multiplier pattern; not a single word. |
| one-third | point-fraction-pattern | ELT-FUNCTION | Representative of the open fraction pattern. |
| cardinal numerals | point-exact-number-pattern | ELT-FUNCTION | Open productive pattern: one, two, three, … — pattern row, not an enumeration. |
| ordinal numerals | point-order-position-pattern | ELT-FUNCTION | Open productive pattern: first, second, third, … — pattern row, not an enumeration. |

## 2F. Expletive / dummy forms — CONFIRMED POINT-form with NO-REFERENT flag (R7)

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| it — dummy/weather/time | point-form-no-clear-referent | WIKI-PRON | In *it is raining / it is late*. **CONFIRMED (R7): POINT-form with a NO-REFERENT flag** — the form occupies a pointing slot and the referent is explicitly none; never resolved to a fake referent, never FLUFF. |
| there — existential | point-form-place-opening-no-clear-referent | WIKI-PRON | In *there is/are*, distinct from pointing *there* (“that place”). **CONFIRMED (R7): POINT-form with a NO-REFERENT flag** — never resolved to a fake referent, never FLUFF. |
| there — deictic place | point-far-place | WIKI-PRON | Ordinary pointing use, separate from existential *there*. |

## 2G. Articles — promoted from FLUFF (R3)

The three article rows lived in FLUFF in the candidate census. Ace's confirmation promotes all three (R3): each carries a real pointing job.

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| the | point-known — the identifiable one | PLAN §4.7; ELT-FUNCTION | Promoted out of FLUFF (R3). Definiteness is a pointing job: the referent is marked as identifiable. |
| a | point-indefinite-one | PLAN §4.7; ELT-FUNCTION | Promoted out of FLUFF (R3). Introduces one unspecified countable referent. |
| an | point-indefinite-one | PLAN §4.7; ELT-FUNCTION | Vowel-sound allomorph of *a* (R3): the spelling difference is allomorphy — one meaning, not two. |

**POINT subtotal (CONFIRMED):** 35 paradigm + 7 demonstrative + 4 reciprocal + 15 relative-form + 50 indefinite/determiner-pattern + 3 expletive/deictic + 3 articles promoted (R3) = **117 rows**. The indefinite/determiner subtotal includes productive pattern rows, so it is a census-row count, not a claim that English has only 50 such forms.


---

# 3. CONDITION

**Job:** opens a condition, hypothesis, exception, requirement, or counterfactual frame.

**Section sources:** PLAN §4.7; Mango Languages, “How to form conditional sentences without ‘if’?”; standard conditional-construction inventories reflected in the research sweep. Temporal uses are named rather than silently converted into conditions.

**Use rules (R8):** *if / whether* — CONDITION for conditional clauses; indirect questions are ASK-construction or LINK by the governing construction, never by spelling alone. *When / whenever / once* — temporal by default (a spine relation, not a category membership); CONDITION only when the clause supplies the governing case for the main clause. *Without* — LINK home (§1E) plus a NEGATE-absence feature (§4C); its row here is the counterfactual CONDITION use.

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| if | condition-open | PLAN §4.7 | Canonical condition opener; also introduces indirect yes/no questions. |
| even if | condition-even-under | MANGO-COND | Concessive condition: the result holds even under the stated case. |
| only if | condition-only-under | MANGO-COND | Restrictive necessary condition. |
| if only | wish-or-regret-open | MANGO-COND | Borderline: often a wish/regret, not an ordinary condition. Retain as a candidate, not a core opener. |
| if not | condition-if-not | MANGO-COND | Negative condition fragment/construction. |
| if so | condition-if-true | MANGO-COND | Anaphoric condition fragment: “if that is true.” |
| unless | condition-except | PLAN §4.7; MANGO-COND | Core exception condition: “if … not / except when.” |
| whether | condition-or-alternative-open | MANGO-COND | In condition-like use, alternatives matter; in indirect questions, see ASK/LINK ambiguity. |
| whether … or | condition-alternative-frame | MANGO-COND | Paired alternative frame. |
| provided | condition-provided-that | MANGO-COND | Short form of *provided that*. |
| provided that | condition-provided-that | MANGO-COND | Requirement condition. |
| providing | condition-providing-that | MANGO-COND | Short form of *providing that*. |
| providing that | condition-providing-that | MANGO-COND | Requirement condition. |
| on condition that | condition-explicit-requirement | MANGO-COND | Explicit requirement construction. |
| as long as | condition-while-and-if | MANGO-COND | Duration plus condition are fused in many uses. |
| so long as | condition-while-and-if | MANGO-COND | Variant of *as long as*. |
| in case | condition-in-case-precaution | MANGO-COND | Precaution condition; not identical to causal *because*. |
| in the event that | condition-if-event-happens | MANGO-COND | Formal event condition. |
| assuming | condition-assume-that | MANGO-COND | Short form of *assuming that*. |
| assuming that | condition-assume-that | MANGO-COND | Supposition opener. |
| suppose | condition-suppose-that | MANGO-COND | Imperative-like supposition opener. |
| supposing | condition-supposing-that | MANGO-COND | Supposition opener. |
| supposing that | condition-supposing-that | MANGO-COND | Explicit supposition construction. |
| given | condition-given-that | MANGO-COND | Short form; also ordinary preposition/participle uses. |
| given that | condition-given-that | MANGO-COND | Treats a proposition as the working premise. |
| granted | condition-granted-that | MANGO-COND | Short form; often concessive (“admittedly”) as well as conditional. |
| granted that | condition-granted-that | MANGO-COND | Explicit granted-premise construction. |
| but for | condition-counterfactual-without | MANGO-COND | “If it were not for …”; NEGATE/LINK boundary. |
| without | condition-counterfactual-absence | MANGO-COND; WIKI-PREP | In *without your help, we would have failed*, absence supplies a counterfactual condition. Ordinary preposition use remains LINK/NEGATE boundary. |
| otherwise | condition-if-not-consequence | ELT-FUNCTION; MANGO-COND | Marks the consequence if the condition fails; not a simple opener. |
| or else | condition-if-not-consequence | MANGO-COND | Threat/result alternative construction; informal in many uses. |
| once | condition-once-after | ELT-FUNCTION | Temporal by default; conditional when a completed trigger licenses the result. Use-sensitive. |
| when | condition-when-case-arises | PLAN research sweep | Temporal by default; conditional in generic/future cases. Do not file all uses here. |
| whenever | condition-or-time-every-or-any-time | PLAN research sweep | Temporal, generic-conditional, and free-relative uses overlap. |

**CONDITION subtotal (CONFIRMED):** **34 rows.**

---

# 4. NEGATE

**Job:** reverses, denies, excludes, or weakens a claim.

**Section sources:** Grammarly, “Negatives and Double Negatives”; ScriGroup negation reference distinguishing core negatives from broad negatives; PLAN §4.7. Negative affixes and negative content verbs are deliberately not smuggled into this small-word table; see the notes after the table.

## 4A. Core negatives

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| not | reverse | PLAN §4.7 | Canonical clausal negation. |
| n't | reverse-clitic | GRAM-NEG | Negative clitic in *don't, can't, won't,* etc.; a construction piece, not an independent word. |
| never | reverse-always | PLAN §4.7 | “At no time.” |
| no | reverse-or-no-instance | GRAM-NEG | Answer negator and determiner; determiner use is cross-listed in POINT. |
| none | reverse-amount-or-one | GRAM-NEG | “Not any / not one”; also POINT pronoun. |
| no one | reverse-person-any | GRAM-NEG | Negative person construction; also POINT. |
| no-one | reverse-person-any | GRAM-NEG | Hyphenated variant of *no one*. |
| nobody | reverse-person-any | GRAM-NEG | Negative person pronoun; also POINT. |
| nothing | reverse-thing-any | GRAM-NEG | Negative thing pronoun; also POINT. |
| nowhere | reverse-place-any | GRAM-NEG | Negative place form; also POINT. |
| neither | reverse-one-of-two | GRAM-NEG | Negative determiner/pronoun and correlative first half; POINT/LINK dual-class. |
| nor | join-reverse-other | GRAM-NEG | Negative coordinator, usually after *neither* or another negative. |
| none of | reverse-part-of-group | GRAM-NEG | Partitive negative construction. |
| no longer | reverse-continuing-state | GRAM-NEG | “Not anymore.” |
| no more | reverse-additional-or-continuing | GRAM-NEG | Can mean not any more quantity or no longer; context decides. |
| not at all | reverse-emphatic-degree-zero | GRAM-NEG | Negative degree phrase. |
| by no means | reverse-emphatic-certainly-not | GRAM-NEG | Formal emphatic negative phrase. |
| in no way | reverse-emphatic-manner-zero | GRAM-NEG | Emphatic negative phrase. |
| on no account | reverse-emphatic-never-permitted | GRAM-NEG | Formal emphatic negative phrase. |
| under no circumstances | reverse-emphatic-no-case | GRAM-NEG | Formal emphatic negative phrase. |

## 4B. Partial / broad negatives — NEGATE-partial subclass (CONFIRMED, R5)

These do not fully reverse a claim. Filing them as ordinary `reverse` would be false precision. **CONFIRMED (R5): this is the named subclass NEGATE-partial of NEGATE, and every gloss carries degree or frequency.**

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| hardly | almost-reverse-degree-or-amount | GRAM-NEG | “Almost not.” |
| scarcely | almost-reverse-degree-or-amount | GRAM-NEG | “Almost not”; also “only just” in some uses. |
| barely | almost-reverse-with-small-margin | GRAM-NEG | “Only just / almost not,” depending on the predicate. |
| rarely | almost-reverse-frequency | GRAM-NEG | “Not often,” not “never.” |
| seldom | almost-reverse-frequency | GRAM-NEG | “Not often,” not “never.” |
| little | almost-reverse-amount | GRAM-NEG | Degree/amount use only, as in *little is known*. Ordinary size/amount pointing uses are in POINT/FUNCTION by use. |
| few | small-positive-not-many | GRAM-NEG | CONFIRMED pair rule (R5/A11): bare *few* = NEGATE-partial (this row); *a few* = POINT-positive (§2E). A cross-listed construction pair — the rule is stated at both rows. Not a core negative. |

## 4C. NEGATE boundary candidates

**Use rules (R8):** *without* — LINK home (§1E), NEGATE-absence feature here, CONDITION use in counterfactual frames (§3). *Not only* belongs to the FOCUS construction family (§8; §1C), not to the core negatives, despite containing *not*.

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| without | absence-not-having | WIKI-PREP; GRAM-NEG | Preposition home in LINK; negative force comes from absence. Counterfactual use is in CONDITION. |
| sans | absence-not-having-formal | WIKI-PREP | Formal/humorous “without”; LINK preposition with negative absence force. |
| no sooner | reverse-time-completion-pair-opener | QUI-CORREL; GRAM-NEG | Only in *no sooner … than*; temporal construction, not a standalone negator. |
| not only | focus-add-not-simple-reverse | QUI-CORREL | In *not only … but also*, the construction adds rather than denies. Not a core negative despite containing *not*. |
| never mind | dismiss-or-reverse-importance | GRAM-NEG | Idiom candidate: “disregard that / it does not matter.” Register/idiom status needs Ace's eye if it is to be included. |
| no way | reverse-emphatic-refusal | GRAM-NEG | Informal emphatic refusal/denial construction. |
| not necessarily | reverse-required-inference | GRAM-NEG | Denies necessity, not the underlying possibility. Useful modal-negative construction. |
| not really | weaken-or-reverse-claim | GRAM-NEG | Conversational partial denial/qualification. |
| not yet | reverse-completion-so-far | GRAM-NEG | Denies completion up to the reference time; temporal as well as negative. |
| not now | reverse-present-time | GRAM-NEG | Construction candidate; may be compositional rather than predisposed. Ace may reject it as a separate row. |

**Deliberately not in NEGATE:** negative affixes (*un-, non-, in-/im-/il-/ir-, dis-, -less*) belong to the morpheme side and LM-1 decomposition; negative content verbs (*fail, refuse, deny, avoid,* etc.) are FUNCTION/content words, not predisposed small words.

**NEGATE subtotal (CONFIRMED):** 20 core + 7 partial (NEGATE-partial subclass, R5) + 10 boundary = **37 rows.**

---

# 5. ASK

**Job:** opens a question and names the shape of the answer wanted.

**Section sources:** PLAN §4.7; Quillbot, “What Is an Interrogative?” and “Interrogative Pronouns”; Wikipedia, “English pronouns.” Genuine question use is separated from relative/free-relative use.

**Use rules (R8, R11):** the *-ever* family is ASK **only** in genuine interrogative syntax — otherwise POINT free-relative or LINK concessive, by construction. **CONFIRMED (R11): ASK includes a construction layer** — the *how* + measure compounds, the inversion patterns, and the tag patterns in this table are ASK members as constructions; LM-2 treats question formation as constructions, not vocabulary lookup alone.

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| why | asks-for-cause | PLAN §4.7 | Core interrogative; relative use in *the reason why* is POINT/LINK by use. |
| who | asks-for-person | PLAN §4.7 | Core interrogative pronoun. |
| whom | asks-for-person-object | QUI-INTERROG | Formal object form. |
| whose | asks-for-owner-or-relation | QUI-INTERROG | Interrogative possessive/determiner. |
| what | asks-for-thing | PLAN §4.7 | Core interrogative pronoun/determiner. |
| which | asks-for-choice | PLAN §4.7 research sweep | Asks for a selection from a set. |
| when | asks-for-time | PLAN §4.7 | Core interrogative; do not confuse temporal-relative or conditional uses. |
| where | asks-for-place | PLAN §4.7 | Core interrogative. |
| how | asks-for-method-or-manner | PLAN §4.7 | Also asks about degree/condition in compounds and idioms. |
| how come | asks-for-cause-informal | QUI-INTERROG | Distinct construction; asks why, with an uninverted clause in ordinary use. |
| what for | asks-for-purpose | QUI-INTERROG | Purpose question construction. |
| where from | asks-for-source-place | QUI-INTERROG | Source/origin question construction. |
| what if | asks-hypothetical-case | PLAN research sweep | Opens a hypothetical, often with CONDITION overlap. |
| whoever | asks-or-points-any-person | QUI-INTERROG | Genuine standalone question use exists but free-relative/concessive uses are more common; use-sensitive. |
| whomever | asks-or-points-any-person-object | QUI-INTERROG | Mostly free-relative; interrogative use is rare/formal. |
| whosever | asks-or-points-any-owner | QUI-INTERROG | Rare; free-relative/possessive candidate. |
| whatever | asks-or-points-any-thing | QUI-INTERROG | Genuine question use must be separated from free-relative, determiner, and concessive uses. |
| whichever | asks-or-points-any-choice | QUI-INTERROG | Genuine question use must be separated from free-relative/concessive uses. |
| whenever | asks-or-points-any-time | QUI-INTERROG | Often temporal/free-relative rather than a direct question. |
| wherever | asks-or-points-any-place | QUI-INTERROG | Genuine question use exists; free-relative/concessive uses are common. |
| however | asks-degree-or-points-any-manner | QUI-INTERROG | In *however did you…?* it intensifies a question; ordinary contrast use is LINK, concessive use is POINT/LINK. |
| how many | asks-for-count | QUI-INTERROG | Countable quantity construction. |
| how much | asks-for-amount-or-price | QUI-INTERROG | Uncountable amount/price construction. |
| how often | asks-for-frequency | QUI-INTERROG | Frequency construction. |
| how long | asks-for-duration-or-length | QUI-INTERROG | Duration or physical length; context decides. |
| how far | asks-for-distance-or-extent | QUI-INTERROG | Distance or figurative extent. |
| how soon | asks-for-time-until | QUI-INTERROG | Earliest/expected time construction. |
| how old | asks-for-age | QUI-INTERROG | Age construction. |
| how + adjective/adverb | asks-for-degree-pattern | QUI-INTERROG | Productive pattern: *how big, how fast, how well,* etc. Counted once. |
| isn't it / aren't I / didn't you — tag-question pattern | asks-for-confirmation-pattern | GRAM-NEG; PLAN research sweep | Productive polarity-tag pattern; counted once as a construction pattern, not as individual auxiliary rows. |
| do/does/did — question-support pattern | asks-open-support-pattern | ELT-FUNCTION | Auxiliary support pattern for questions; the auxiliaries themselves are confirmed OPERATOR (§7), not ASK words. |
| is/are/was/were — inversion pattern | asks-open-inversion-pattern | ELT-FUNCTION | Be-inversion question pattern; counted as a construction, not a word. |
| can/could/will/would — modal-question pattern | asks-open-modal-pattern | ELT-FUNCTION | Modal-inversion question pattern; counted as a construction, not a word. |
| eh / huh — tag particles | asks-for-confirmation-particle | PLAN research sweep | Dialectal/informal candidates; register status needs Ace's ruling before inclusion in a core table. |

**ASK subtotal (CONFIRMED):** **34 rows**, including construction and pattern rows (construction layer, R11). Those rows are honest census units: English question formation is partly constructional and cannot be reduced to wh-words alone.

---

# 6. FLUFF — CONFIRMED EMPTY (R4)

**Category definition (retained):** a candidate with no referential, relational, conditional, negative, question, focus, or structural job.

**Membership: ZERO.** FLUFF stands as a confirmed category with no members.

## The three promotions that emptied it

The candidate census filed exactly three rows here. All three carried a real pointing job, and Ace's confirmation promotes all three (R3). They now live in POINT §2G:

| former FLUFF row | drafted meaning in the census | confirmed home | ruling |
|---|---|---|---|
| the | glue-definite-article — disputed | POINT §2G — point-known, "the identifiable one" | R3 |
| a | point-indefinite-one — promotion candidate | POINT §2G — point-indefinite-one | R3 |
| an | point-indefinite-one — promotion candidate | POINT §2G — point-indefinite-one (allomorph of *a*) | R3 |

**Empty FLUFF is the promotion rule succeeding, not a gap.** The FLUFF PROMOTION RULE said: any "fluff" word found carrying even a small job is promoted to its real category, recorded. Applied honestly, it emptied the category. The category stays defined so that a future candidate with genuinely no job has a lawful home — and so that nothing is ever filed here merely to avoid classifying it.

**Design note (R14, Ace addendum 2026-11-11):** there is actually very little fluff anywhere — the point of this system is PURE MEANING. Every token's full meaning is defined in advance by these tables. The computer, the AI, nature, and the human may all deliver sloppily, but sloppy delivery is a surface phenomenon; by design the full meaning is still defined, and sloppiness never makes a token meaningless. FLUFF's emptiness therefore follows from the design itself, not only from the promotions above: the parse recovers designed meaning through sloppy delivery.

## Candidates considered and not filed as FLUFF

| candidate / family | drafted meaning | source | confirmed treatment |
|---|---|---|---|
| infinitive *to* | function-infinitive-marker | ELT-FUNCTION | **FUNCTION-structural (R10):** a spine structure marker, not a category member. (Directional *to* is LINK §1E.) |
| complementizer *that* | link-clause-content | LAN-CLOSED | LINK (§1B); demonstrative and relative uses are POINT (R8). |
| possessive marker *'s* | function-possession-marker | ELT-FUNCTION | A clitic/morphological marker, not a standalone small word for this census. |
| dummy *it / there* | point-form-no-referent | WIKI-PRON | **Ruled (R7):** POINT-form with a NO-REFERENT flag (§2F). Never FLUFF. |
| auxiliary/modal family | operator-family | ELT-FUNCTION | **OPERATOR (§7) — a category of their own (R1).** Never FLUFF. |
| focus particles | focus-family | ELT-FUNCTION | **FOCUS (§8) — a category of their own (R2).** Never FLUFF. |

**FLUFF subtotal (CONFIRMED): 0 rows.**

---

# 7. OPERATOR — CONFIRMED CATEGORY (R1)

**Job:** carries the sentence machinery — tense, aspect, modality, question support, and negation support.

In the candidate census these 27 rows sat in a boundary section, because none of the original six categories could hold them honestly: they are not glue and not content. **CONFIRMED (R1): they are members of the new category OPERATOR**, with the predisposed operator meanings as drafted. Their question-formation PATTERNS are separately ASK constructions (§5, R11); the auxiliaries themselves are OPERATOR.

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| be | function-be-operator | ELT-FUNCTION | Base auxiliary/copula form; paradigm forms follow. |
| am | function-be-speaker-present | ELT-FUNCTION | First-person present form. |
| is | function-be-third-present | ELT-FUNCTION | Third-person present form. |
| are | function-be-plural-or-hearer-present | ELT-FUNCTION | Present plural / second-person form. |
| was | function-be-past-singular | ELT-FUNCTION | Past form. |
| were | function-be-past-plural-or-subjunctive | ELT-FUNCTION | Past plural and irrealis uses. |
| been | function-be-perfect-participle | ELT-FUNCTION | Perfect/progressive participle. |
| being | function-be-progressive-participle | ELT-FUNCTION | Progressive/passive participle. |
| have | function-have-perfect-operator | ELT-FUNCTION | Perfect auxiliary; possession verb use is content/FUNCTION by use. |
| has | function-have-perfect-third-present | ELT-FUNCTION | Third-person perfect auxiliary. |
| had | function-have-perfect-past | ELT-FUNCTION | Past perfect auxiliary. |
| do | function-do-support-operator | ELT-FUNCTION | Question/negation/emphasis support; lexical “perform” use is separate. |
| does | function-do-support-third-present | ELT-FUNCTION | Third-person support form. |
| did | function-do-support-past | ELT-FUNCTION | Past support form. |
| can | function-can-ability-or-permission | ELT-FUNCTION | Modal. |
| could | function-could-ability-possibility-or-polite | ELT-FUNCTION | Modal; past-ability and possibility uses differ. |
| may | function-may-permission-or-possibility | ELT-FUNCTION | Modal. |
| might | function-might-possibility | ELT-FUNCTION | Modal. |
| must | function-must-necessity-or-strong-inference | ELT-FUNCTION | Obligation and inference uses differ. |
| shall | function-shall-future-or-obligation | ELT-FUNCTION | Modal; formal/first-person/legal uses vary. |
| should | function-should-advice-expectation-or-condition | ELT-FUNCTION | Modal; conditional protasis use in formal inversion is an additional boundary. |
| will | function-will-future-or-volition | ELT-FUNCTION | Modal. |
| would | function-would-conditional-polite-or-past-habit | ELT-FUNCTION | Modal. |
| ought to | function-ought-duty-or-expectation | ELT-FUNCTION | Semi-modal construction. |
| used to | function-used-to-past-habit | ELT-FUNCTION | Semi-modal construction. |
| need — modal use | function-need-necessity | ELT-FUNCTION | Modal use in *needn't / need he go?*; ordinary verb use is separate. |
| dare — modal use | function-dare-challenge-or-courage | ELT-FUNCTION | Modal use in *daren't / dare he…?*; ordinary verb use is separate. |

# 8. FOCUS — CONFIRMED CATEGORY (R2)

**Job:** restricts, adds, or shifts focus — *only* limits scope, *even* marks the unexpected end of a scale, *also / too / as well* add a parallel item.

In the candidate census these 6 rows sat in the boundary section beside the auxiliaries. **CONFIRMED (R2): they are members of the new category FOCUS.** They were never FLUFF (census A16): moving *only* changes truth conditions, and *even* adds a scalar expectation.

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| only | focus-exclusive-or-limit | ELT-FUNCTION | Restricts scope; placement changes meaning. Not FLUFF. |
| even | focus-unexpected-or-scalar | ELT-FUNCTION | Scalar focus particle; also adjective “level/flat” is unrelated. |
| just | focus-exact-limit-or-recent | ELT-FUNCTION | Can mean merely, exactly, or a moment ago; use-sensitive. |
| also | focus-add-same-kind | ELT-FUNCTION | Additive focus/discourse particle. |
| too | focus-add-same-kind | ELT-FUNCTION | Additive use here; degree “excessively” use is separate. |
| as well | focus-add-same-kind | ELT-FUNCTION | Additive construction. |

**OPERATOR subtotal (CONFIRMED): 27 rows. FOCUS subtotal (CONFIRMED): 6 rows.** Together these are the 33 rows the candidate census held as "boundary not forced into the six" — the boundary is now closed by R1 and R2: both families have categories of their own.

---

# 9. MORPHEME SIDE

**Confirmation status (R13):** the counts in this section are CONFIRMED as LM-1's starting evidence only — an inventory, not a finished morpheme table. Position conflicts (*dell*, *man*, *re*) and project-piece candidates are **LM-1 rulings, NOT settled here**. The preform candidates (§9.5) remain **NOT IN USE**. The free ~1,693-entry roots list (§9.8) is **NOT imported**; any LM-1 import follows CC BY-SA discipline.

## 9.1 What was counted — and what was not

The morpheme census separates four different things that are easy to conflate:

1. **Typed affix assignments** in `morpheme.py` — a label assigned as prefix, root, or suffix.
2. **Surface-root entries** in `latinmandell.py` — whole English words mapped to a Latin citation form, sense, and Dell.
3. **Ontology entries** in `src/core/mandel_ontology.js` — a smaller Latin/Greek operator inventory.
4. **Preform candidate pieces** — design-history candidates that are explicitly not in use.

A Latin citation string is not automatically one atomic morpheme. Some citation strings contain variants separated by `/`, phrases, or Greek material. LM-0 counts them transparently and does not silently convert them into atomic pieces.

## 9.2 `form/mandell/morpheme.py` — typed inventory

### Prefixes — 24 declared assignments

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| ad | toward / additive direction | IN-MORPHEME | Project table label; LM-1 must confirm the gloss against the source file. |
| aequi | equal- | IN-MORPHEME | Latin-style equality piece. |
| alpha | alpha / beginning-operator | IN-MORPHEME | Greek operator placed in the prefix set. |
| com | together-with | IN-MORPHEME | Also appears in the ontology source as *Com-*. |
| con | together-with | IN-MORPHEME | Variant/related to *com-*; assimilation variants belong to LM-1. |
| de | down / reverse / away | IN-MORPHEME | Ontology gloss varies slightly; see conflicts. |
| delta | delta / change-operator | IN-MORPHEME | Greek operator placed in the prefix set. |
| fu | project-piece — gloss to reconfirm in LM-1 | IN-MORPHEME | Non-classical/project-specific candidate; do not invent a classical etymology. |
| im | in / into / not — by root | IN-MORPHEME | Assimilated negative/locative prefix family; LM-1 must split senses if needed. |
| iso | equal-same | IN-MORPHEME | Greek equality piece. |
| man | hand / control / execution | IN-MORPHEME | Preform *Man-* has a related but different protocol/operator gloss; see conflicts. |
| nova | new- | IN-MORPHEME | Whole-word-like project piece. |
| nud | project-piece — gloss to reconfirm in LM-1 | IN-MORPHEME | Non-classical/project-specific candidate. |
| nur | nurture / care stem-piece | IN-MORPHEME | Related to flat extra *nurture*; segmentation must be confirmed. |
| ob | against / toward / facing | IN-MORPHEME | Classical-style prefix. |
| omega | omega / end-operator | IN-MORPHEME | Greek operator placed in the prefix set. |
| omni | all- | IN-MORPHEME | Latin-style totality piece. |
| over | over / excess / above | IN-MORPHEME | English-form prefix piece. |
| post | after- | IN-MORPHEME | Temporal/positional prefix. |
| pre | before- | IN-MORPHEME | Also appears in the ontology source. |
| re | again / back | IN-MORPHEME | Cross-type duplicate: also a suffix in the same file. |
| sub | under- | IN-MORPHEME | Positional prefix. |
| syn | together- | IN-MORPHEME | Greek together piece. |
| trans | across / changing form | IN-MORPHEME | Also appears in ontology and preform candidates. |

### Roots — 19 declared assignments

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| birth | birth / origin event | IN-MORPHEME | English whole-word-like root; project sense must govern. |
| cor | heart / core | IN-MORPHEME | Latin-style root. |
| dell | nested unit / operator cell / protected pocket | IN-MORPHEME | Cross-type duplicate: also a suffix; preform also proposes it as a prefix. |
| fac | make / do | IN-MORPHEME | Also in ontology as *-fac-*. |
| gen | generate / birth / kind | IN-MORPHEME | Latin/Greek generation family. |
| log | reason / record / trace | IN-MORPHEME | Ontology wording differs; see variants. |
| lumen | light / illumination | IN-MORPHEME | Related light family with *lux*. |
| lux | light | IN-MORPHEME | Related light family with *lumen*. |
| mand | command / order / entrust | IN-MORPHEME | Project-central root; related flat forms *mandel/mandell/commandell*. |
| men | mind / think | IN-MORPHEME | Mind root candidate. |
| mend | repair / correct | IN-MORPHEME | Close surface neighbor of *mand/men*; segmentation risk. |
| mit | send | IN-MORPHEME | Also in ontology as *-mit-*. |
| ordo | order / arrangement | IN-MORPHEME | Latin-style root. |
| plete | fill / complete | IN-MORPHEME | Project segmentation of the completion family; confirm in LM-1. |
| pulse | pulse / beat signal | IN-MORPHEME | English whole-word-like root; project sense must govern. |
| spec | look / evaluate | IN-MORPHEME | Also in ontology as *-spec-*. |
| struct | build / arrange | IN-MORPHEME | Structure family root. |
| tu | you / addressee stem | IN-MORPHEME | Short project piece; high segmentation-collision risk. |
| voc | voice / call | IN-MORPHEME | Voice family root. |

### Suffixes — 11 declared assignments

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| ce | project suffix — gloss to reconfirm in LM-1 | IN-MORPHEME | Short form; segmentation risk. |
| dell | fragment / nested cell / protected pocket | IN-MORPHEME | Cross-type duplicate of the root *dell*. |
| er | agent / doer | IN-MORPHEME | English agent suffix family. |
| ex | out / former — by use | IN-MORPHEME | Positional behavior must be confirmed; surface form also works as a standalone piece. |
| ing | ongoing action/process | IN-MORPHEME | English participle/gerund suffix. |
| ment | result / means / state | IN-MORPHEME | Noun-forming suffix family. |
| mut | change | IN-MORPHEME | Change piece placed in the suffix set. |
| re | loop / again / return frame | IN-MORPHEME | Cross-type duplicate of prefix *re*, with a related but not identical gloss. |
| term | boundary / end / named unit | IN-MORPHEME | Termination/naming piece. |
| tion | action / result | IN-MORPHEME | Noun-forming suffix family. |
| ure | action / result / state | IN-MORPHEME | Noun-forming suffix family. |

### Flat whole-form extras — 5

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| mandel | whole-form project piece | IN-MORPHEME | Do not decompose silently; it is a project whole form. |
| mandell | whole-form project piece | IN-MORPHEME | Canonical project spelling; whole-form extra. |
| nurture | whole-form care/growth word | IN-MORPHEME | Related to prefix *nur* but listed as a whole form. |
| commandell | whole-form project compound | IN-MORPHEME | Contains recognizable project pieces but is stored whole. |
| omnifacure | whole-form project compound | IN-MORPHEME | Contains recognizable pieces but is stored whole. |

**Arithmetic:** 24 prefix assignments + 19 root assignments + 11 suffix assignments = **54 typed assignments**. The normalized label union across the typed sets is **52**, because *re* and *dell* each occur in two types. Adding the five flat extras gives **57 flat unique pieces**. This supports the build plan's “~57 pieces” description, provided “pieces” means the flat lookup union — not 57 prefixes/roots/suffixes of one type.

## 9.3 `form/mandell/latinmandell.py` — surface-root inventory

- **53 English surface-word entries** were counted.
- Each entry maps an English word to a Latin form, a sense, and a Dell.
- Splitting the Latin citation strings on `/` produced **68 citation variants as written** and **65 unique Latin citation forms**.
- These are **not** 65 atomic morphemes. Some citation strings are phrases or Greek material — examples named during extraction include *recedere ad tutum* and *logos*.
- `form/mandell/polyglot.py` adds Latin phrase patterns but no separate atomic morpheme table beyond this material.

**Confirmed treatment (R13):** treat the 53 entries as surface-root evidence for LM-1 harvesting, not as a finished prefix/root/suffix inventory.

## 9.4 `src/core/mandel_ontology.js` — ontology inventory

| group | candidates | drafted meaning | source | notes/ambiguity |
|---|---|---|---|---|
| Latin prefixes | Com-, Re-, Pre-, Trans-, De- | together; again/back; before; across/changing; down/away | IN-ONTOLOGY | All five overlap labels already in `morpheme.py`. |
| Latin roots | -fac-, -log-, -mit-, -spec- | make/do; record/reason; send; look/evaluate | IN-ONTOLOGY | All four overlap labels already in `morpheme.py`. |
| Greek operators | Alpha, Delta, Lambda, Sigma, Omega | beginning; change; operator placeholder; sum/aggregate; end | IN-ONTOLOGY | *Alpha, Delta,* and *Omega* overlap `morpheme.py`; *Lambda* and *Sigma* are the two new normalized labels. |

**Count:** 14 entries. **New normalized labels relative to `morpheme.py`:** **2** (*lambda*, *sigma*). A normalized label union of the `morpheme.py` flat set and this ontology set is therefore **59**, but that is a cross-source label union, not a confirmed morpheme table.

## 9.5 Preform affix lexicon — candidates only

Source: `preform/pages/21_AFFIX_LEXICON_STARTER.md`. The file is explicitly **NOT IN USE**. Status under confirmation (R13): CONFIRMED as candidates only — still NOT IN USE. Admission to any working table still requires the Manual gate in LM-1.

### Proposed prefixes — 10 candidate rows

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| Man- / Mandel- | protocol / operator domain | IN-PREFORM-AFFIX | Two surface variants in one row. Related to *man* in `morpheme.py`, but the gloss differs: protocol/operator domain versus hand/control/execution. |
| Dell- | Dell/unit domain | IN-PREFORM-AFFIX | Positional conflict: *dell* is already a root and suffix in `morpheme.py`. |
| Form- | form / structure domain | IN-PREFORM-AFFIX | New label relative to `morpheme.py`. |
| Evolu- | evolution / unfolding | IN-PREFORM-AFFIX | New label; whole-stem-like candidate. |
| Harmoni- | harmony / coordination | IN-PREFORM-AFFIX | New label; whole-stem-like candidate. |
| Mirror- | mirror / reflection | IN-PREFORM-AFFIX | New label; English whole-word-like candidate. |
| Proso- | prosody / expression-facing | IN-PREFORM-AFFIX | New label; gloss must be confirmed from the preform record in LM-1. |
| Pure- | pure / unmixed | IN-PREFORM-AFFIX | New label; English whole-word-like candidate. |
| Recur- | recur / repeat | IN-PREFORM-AFFIX | New label; related in sense to *re* but not the same piece. |
| Trans- | across / change | IN-PREFORM-AFFIX | Overlaps existing *trans* and is broadly consistent. |

### Proposed suffixes — 5 candidate rows

| candidate | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| -dell | Dell/unit ending | IN-PREFORM-AFFIX | Duplicates the existing *dell* label in another proposed position. |
| -ell | small/derived ending candidate | IN-PREFORM-AFFIX | Segmentation ambiguity: *-ell* is contained in *dell*. |
| -cell | cell/unit ending | IN-PREFORM-AFFIX | New label; overlaps the semantic field of *dell*. |
| -factors | factors/components ending | IN-PREFORM-AFFIX | New label; plural whole-word-like suffix candidate. |
| -man | person/operator ending | IN-PREFORM-AFFIX | Positional conflict: *man* is already a prefix in `morpheme.py`. |

## 9.6 Leight / Loure — the two lawful ways a new piece enters

Source: `preform/LANGUAGE_PREFORM.md`.

| mechanism | drafted meaning | source | notes/ambiguity |
|---|---|---|---|
| Leight | create-new-piece-from-scratch | IN-PREFORM-LANG | Used when no defined piece exists. Requires a standalone definition, the Manual/Manuall and Mandellafactors gate, and Architect number-confirmation. |
| Loure | adopt-existing-non-Latin-affix-sense | IN-PREFORM-LANG | Adopts an already-defined non-Latin affix sense into Latin-Mandel. Requires the Manual gate and a clash/test against the existing category; it must not silently overwrite true terms. |

Classical etymology is **not** the gate. A standalone definition, Manual classification, and True Mandel / Architect confirmation are the gate.

## 9.7 Duplicates, overlaps, and sense conflicts across in-repo sources

| piece / family | finding | recommendation |
|---|---|---|
| re | Prefix in `morpheme.py` (“again/back/iterative”) and suffix in the same file (“loop/again/return frame”); also an ontology prefix. | Do not merge the glosses silently. LM-1 should either confirm two positional entries or one entry with two positional frames. |
| dell | Root and suffix in `morpheme.py`; proposed prefix in the preform lexicon. | Highest positional-conflict piece in the in-repo census. Ace/LM-1 must rule which positions are lawful. |
| man | Prefix in `morpheme.py` (“hand/control/execution”); *Man-/Mandel-* in preform means protocol/operator domain; *-man* is proposed as a suffix. | Treat as three candidate uses, not one settled piece. |
| trans | Prefix in `morpheme.py`, ontology prefix, and preform prefix candidate; broad gloss is consistent: across/change. | Lowest-conflict overlap; still requires confirmation before table use. |
| log | `morpheme.py` wording centers trace/reason; ontology wording centers record/track. | Compatible family, different emphasis. LM-1 should write one gloss with both jobs named or split senses deliberately. |
| spec | Both sources support look/evaluate. | Low-conflict overlap. |
| de | `morpheme.py` includes down/analytical/reverse/intensive; ontology wording is closer to down-from/analyzing. | Compatible but broader in `morpheme.py`; confirm the final sense set. |
| alpha / delta / omega | Greek operators appear in the `morpheme.py` prefix set and the ontology Greek-operator set. | Positional classification differs: prefix versus operator. LM-1 must not call that a mere duplicate without ruling the role. |
| lambda / sigma | Present in ontology, absent from the `morpheme.py` flat set. | Only two genuinely new normalized labels from the ontology source. |
| lumen / lux | Two light-family roots in `morpheme.py`. | Related but separately listed; do not collapse without a ruling. |
| mand / men / mend | Visually and phonetically close project-central pieces with different jobs. | High segmentation-collision risk; LM-1 needs explicit boundary tests. |
| nur / nurture | A short piece and a whole-form extra share the care/growth family. | Confirm whether *nurture* is decomposed or remains whole. |
| -ell / dell | Proposed *-ell* is contained inside *dell*. | Longest-match and boundary rules will matter; flag for LM-1 tests. |
| birth / pulse / nurture | Whole-word-like English entries sit inside the morpheme inventory. | They may be lawful project pieces, but they are not classical bound morphemes. Label them project pieces rather than pretending otherwise. |
| fu / nud / tu / ce | Very short or project-specific pieces. | High false-split risk in English words; LM-1 needs negative examples as well as positive ones. |

## 9.8 Free roots table — summarized, not imported

The build plan identifies the Wikipedia/Wiktionary **“List of Greek and Latin roots in English”** as the large free harvest source.

| field | census finding |
|---|---|
| Approximate size | **About 1,693 Greek/Latin root entries** |
| Fields carried | Root form including allomorph variants; English meaning; origin language; etymology/root origin; English examples |
| LM-0 treatment | **Summarized only. No rows imported.** |
| LM-1 consequence | Any import is a derived-data act and must carry attribution and share-alike handling under the source license terms stated in the plan: **CC BY-SA**. |
| Main risk | Root entries include variants and historical forms; the count is not a count of clean, unique, modern segmentation pieces. LM-1 still needs deduplication, allomorph handling, and collision tests. |


---

# 10. COUNTS SUMMARY (CONFIRMED)

## 10.1 Predisposed small-word census — confirmed

| category | rows | composition |
|---|---:|---|
| LINK | **233** | 7 coordinating conjunctions; 26 clause-linking conjunctions; 16 correlative constructions; 18 discourse links (LINK-discourse subclass, R6); 166 contemporary/general prepositions (confirmed for the first build, R9) |
| POINT | **117** | 35 personal/possessive paradigm forms; 7 demonstratives; 4 reciprocals; 15 relative forms; 50 indefinite/determiner/pattern rows; 3 expletive/deictic rows (NO-REFERENT flag, R7); 3 articles promoted from FLUFF (R3) |
| CONDITION | **34** | Core, formal, supposition, precaution, counterfactual, and temporal-boundary constructions |
| NEGATE | **37** | 20 core; 7 partial/broad (NEGATE-partial subclass, R5); 10 boundary |
| ASK | **34** | 17 core/compound word rows; 8 *how*-construction rows; 4 other question constructions; 5 question-formation/tag pattern rows (construction layer, R11) |
| OPERATOR | **27** | Auxiliaries and modals — new category (R1); the candidate census's §7A boundary rows |
| FOCUS | **6** | Focus and additive particles — new category (R2); the candidate census's §7B boundary rows |
| FLUFF | **0** | Confirmed empty (R4): all three candidate rows promoted to POINT (R3) |
| **Total** | **488** | Deliberately cross-listed rows; not a unique-surface-form count (multi-category membership is law, R8) |

**Reconciliation:** candidate census 488 = LINK 233 + POINT 114 + CONDITION 34 + NEGATE 37 + ASK 34 + FLUFF 3 + Boundary 33. Confirmation moved FLUFF's 3 rows to POINT (114 + 3 = 117) and split the 33 boundary rows into OPERATOR 27 + FOCUS 6. No row was created or deleted: 233 + 117 + 34 + 37 + 34 + 27 + 6 + 0 = **488**.

### What the total does not mean

- It does **not** mean English has exactly 488 closed-class items.
- It does **not** mean every confirmed row carries the same build priority; confirmation settles category and meaning, while LM-1/LM-2 sequencing is a routing question.
- Productive systems — numerals, multipliers, fractions, question inversion, tags, and `how + adjective/adverb` — are represented as patterns.
- The archaic/dialectal preposition reservoir is named but not row-counted.
- Cross-listed forms are evidence that classification must be use-sensitive; deleting the duplicates to make a prettier total would destroy information Ace needs.

## 10.2 Morpheme-side summary (confirmed as LM-1 starting evidence only, R13)

| inventory | prefixes | roots | suffixes | other / total |
|---|---:|---:|---:|---|
| `morpheme.py` typed assignments | 24 | 19 | 11 | **54 assignments** |
| `morpheme.py` normalized typed-label union | — | — | — | **52 unique labels** |
| `morpheme.py` flat extras | — | — | — | **5 whole-form extras** |
| `morpheme.py` flat unique pieces | — | — | — | **57** |
| `latinmandell.py` | — | **53 English surface-root entries** | — | **68 Latin citation variants as written; 65 unique citation forms** |
| `mandel_ontology.js` | 5 Latin | 4 Latin | — | **5 Greek operators; 14 total entries** |
| Cross-source normalized label union, `morpheme.py` flat + ontology | — | — | — | **59 labels** — union only, not a confirmed table |
| Preform affix lexicon | 10 candidate rows | — | 5 candidate rows | **15 candidate rows**, not in use |
| Free Greek/Latin roots list | — | **about 1,693 entries** | — | Summarized only; not imported |

---

# 11. RULINGS APPLIED — EVERY CENSUS AMBIGUITY, DISPOSED

The candidate census named 22 ambiguities (A1–A22) and asked Ace to rule. Ace's confirmation instruction (quoted in the front matter) and rulings R1–R13 dispose of every one. Status key: **APPLIED** = this edition was changed to execute it; **CONFIRMED** = the census treatment stands as ruled; **DEFERRED-TO-LM-1** = explicitly not settled here.

| ambiguity | ruling | status | what happened |
|---|---|---|---|
| A1. Auxiliaries and modals have no honest home in the six | R1 | APPLIED | OPERATOR category created; the 27 auxiliary/modal rows are confirmed members (§7). |
| A2. Discourse adverbs link, but are not all conjunctions | R6 | CONFIRMED | LINK-discourse subclass confirmed (§1D); the subclass names the job, not a part of speech. |
| A3. Relatives are POINT + LINK; ASK only in questions | R8 | APPLIED | Multi-category membership is law; the rule is stated at §2D, §1B, and §5. |
| A4. *That* is demonstrative, complementizer, and relative | R8 | APPLIED | POINT demonstrative/relative home; LINK complementizer use; rules at §1B, §2B, §2D. |
| A5. *Whether* versus *if* | R8 | APPLIED | CONDITION for conditional clauses; indirect questions classified by the governing construction; rule at §3. |
| A6. *When / whenever / once* — temporal first, conditional sometimes | R8 | APPLIED | Temporal by default (a spine relation); CONDITION only when the clause supplies the governing case; rule at §3. |
| A7. *The* — FLUFF or POINT-known | R3 | APPLIED | POINT-known chosen; the row moved to POINT §2G. |
| A8. *A/an* — promotion to POINT-indefinite | R3 | APPLIED | POINT-indefinite; both rows moved to POINT §2G; the spelling difference is allomorphy — one meaning. |
| A9. Dummy *it* and existential *there* | R7 | APPLIED | POINT-form with a NO-REFERENT flag (§2F); never resolved to a fake referent, never FLUFF. |
| A10. Broad negatives need a partial subclass | R5 | CONFIRMED | NEGATE-partial subclass confirmed (§4B); glosses carry degree/frequency. |
| A11. *Few* versus *a few* | R5 | APPLIED | Bare *few* = NEGATE-partial; *a few* = POINT-positive; the pair rule is stated at both rows (§2E, §4B). |
| A12. *Without* crosses LINK, NEGATE, and CONDITION | R8 | APPLIED | LINK home (§1E) + NEGATE-absence feature (§4C) + CONDITION counterfactual use (§3); rules stated at all three tables. |
| A13. *Neither / nor* | R8 | APPLIED | POINT for determiner/pronoun use, NEGATE for the negative force, LINK for the paired construction; rule at §1C. |
| A14. The *-ever* family is not automatically ASK | R8 | APPLIED | ASK only in genuine interrogative syntax; otherwise POINT free-relative or LINK concessive; rule at §5. |
| A15. *How* compounds and question formation exceed the wh-word list | R11 | CONFIRMED | ASK construction layer confirmed (§5); LM-2 treats question formation as a construction layer. |
| A16. Focus particles are real operators | R2 | APPLIED | FOCUS category created — stronger than the census recommendation (FUNCTION/focus): the 6 focus rows are confirmed members (§8). |
| A17. Preposition scope and register | R9 | CONFIRMED | The 166-row contemporary/general inventory is confirmed for the first build (§1E); the reservoir stays named and UNCONFIRMED (§1F). |
| A18. Complementizer and infinitive markers test the meaning of FLUFF | R10 | APPLIED | Infinitive *to* = FUNCTION-structural spine marker; complementizer *that* per R8. FLUFF's strict definition is retained — and the category is empty (R4). |
| A19. Morpheme position conflicts: *dell, man,* and *re* | R13 | DEFERRED-TO-LM-1 | Counts confirmed as evidence; positions are NOT settled here (§9, esp. §9.7). LM-1 rules position by position. |
| A20. Whole-word-like and very short project pieces | R13 | DEFERRED-TO-LM-1 | Kept as project-piece candidates; positive and negative segmentation tests belong to LM-1 (§9.7). |
| A21. Numerals and multipliers are patterns, not a finite word list | R12 | CONFIRMED | Compositional patterns filed in POINT (§2E); LM-1/LM-2 parse their composition. |
| A22. Singular *they* and generic *one* | R12 | CONFIRMED | POINT home with referent-type features (§2A); spelling alone settles neither number nor referent. |

**R4** (FLUFF confirmed empty) maps to no single A-item: it is the joint outcome of R3's promotions and A18's strict definition — what the promotions leave behind is an honestly empty category.

---

# 12. SOURCE AND LICENSE ACCOUNTING

## 12.1 Source keys used in the tables

| key | source | how LM-0 used it | license / rights note |
|---|---|---|---|
| PLAN | `LATINMANDELL_BUILD_PLAN_2026-11-11.md` | Governing categories, starter examples, formula, census scope, harvest and license law | Project record. |
| LAN-CLOSED | Lancaster University, “Closed Class Words” — https://www.lancaster.ac.uk/fass/projects/stylistics/topic2a/3checksheet.htm | Closed-class framing and examples for determiners, pronouns, prepositions, and conjunctions | Read and cited as a reference; no dataset imported. No reuse license is asserted by this census. |
| ELT-FUNCTION | ELT Concourse, “Function words” — https://teflconcourse.com/training/initial/grammarl2/functionwords | Compact function-word inventory across conjunctions, determiners, prepositions, and pronouns | Read and cited as a reference; no dataset imported. No reuse license is asserted by this census. |
| WEISSER-WC | Martin Weisser, “Word Classes” — http://martinweisser.org/courses/lexicology/word_classes.html | Support for closed-class treatment of determiners, pronouns, prepositions/particles, and conjunctions | Read and cited as a reference; no dataset imported. |
| WIKI-PREP | Wikipedia, “List of English prepositions” — https://en.wikipedia.org/wiki/List%20of%20English%20prepositions | Prototypical, intransitive, conjunctive, postposition, complex, and archaic/specialized preposition sections | Wikipedia text is available under CC BY-SA terms; LM-0 cites and summarizes the inventory rather than importing a data table. Any later derived import must preserve attribution/share-alike obligations. |
| WIKI-PRON | Wikipedia, “English pronouns” — https://en.m.wikipedia.org/wiki/English_pronouns#Determinative | Pronoun paradigms, determinative uses, reciprocals, relatives, and indefinite families | Same CC BY-SA caution as WIKI-PREP. |
| QUI-CORREL | Quillbot, “Correlative Conjunctions” — https://quillbot.com/blog/parts-of-speech/correlative-conjunctions/?preview=true | Core correlative pairs and extended/disputed paired constructions | Editorial reference read and cited; no dataset imported. |
| QUI-INTERROG | Quillbot, “What Is an Interrogative?” — https://quillbot.com/blog/sentence-and-word-structure/interrogatives/ ; “Interrogative Pronouns” — https://quillbot.com/blog/pronouns/interrogative-pronouns/ | Interrogative pronouns, adverbs, determiners, *-ever* compounds, and *how* constructions | Editorial reference read and cited; no dataset imported. |
| MANGO-COND | Mango Languages, “How to form conditional sentences without ‘if’?” — https://articles.mangolanguages.com/resources/learn/grammar/english/how-to-form-conditional-sentences-without-if | Non-*if* condition openers and conditional constructions | Editorial reference read and cited; no dataset imported. |
| GRAM-NEG | Grammarly, “Negatives and Double Negatives” — https://www.grammarly.com/blog/grammar/negatives/ ; ScriGroup negation reference returned in the research sweep | Core negatives, negative phrases, and the core-versus-broad-negative distinction | Editorial references read and cited; no dataset imported. |
| IN-MORPHEME | `form/mandell/morpheme.py` in the DellMatrix repository | Typed prefix/root/suffix inventory and flat extras | In-repo project material; repository root LICENSE in the inspected clone is MIT. Census extraction only. |
| IN-LATINMANDELL | `form/mandell/latinmandell.py`; neighboring `form/mandell/polyglot.py` | 53 surface-root entries, citation-form count, phrase-pattern check | In-repo project material; census extraction only. |
| IN-ONTOLOGY | `src/core/mandel_ontology.js` | 14-entry Latin/Greek morpheme-operator inventory | In-repo project material; census extraction only. |
| IN-PREFORM-AFFIX | `preform/pages/21_AFFIX_LEXICON_STARTER.md` | 15 affix candidate rows | In-repo design history, explicitly **NOT IN USE**; candidates only. |
| IN-PREFORM-LANG | `preform/LANGUAGE_PREFORM.md` | Leight and Loure admission mechanisms | In-repo design history and gate law as summarized in the governing plan. |

## 12.2 Harvest-source license flags carried forward to LM-1

| source / dataset named in the plan | LM-0 treatment | license status / action |
|---|---|---|
| Wikipedia/Wiktionary “List of Greek and Latin roots in English” | Summarized only; about 1,693 entries; fields named; **no import** | Plan states **CC BY-SA**; attribution and share-alike must follow any LM-1 derived data. |
| BAWF | Named as prior art / possible cross-check only | Public/open release was reported, but no license file was found in the plan's research. **Not free to copy.** Verify terms before any import; otherwise cross-check only. |
| MorphoLex | Named as a research dataset lead | Research dataset; cite it and verify redistribution terms before import. |
| UniMorph / umLabeller | Named as project leads | Use only under the projects' own terms; verify at import time. |
| SIGMORPHON | Named as a research lead | Open research release per plan; verify the release terms for the exact data used. |
| CLTK | Named as a tooling/library lead | Plan records **MIT**; still verify the exact package/version at use time. |
| Whitaker's Words — ArchimedesDigital/open_words port | Named as a tooling/data lead | Plan records **MIT** for the port; verify the exact repository and version at use time. |
| Any public repository with no license | May be **named** as prior art in a census | **Not free to use.** No-license material is not copied or imported. |

## 12.3 What was not imported

LM-0 imported **none** of the following:

- the roughly 1,693-entry Greek/Latin roots list;
- any Wiktionary category dump;
- BAWF data;
- MorphoLex data;
- any no-license repository's data.

The tables above are an original census compilation: candidates were selected and glossed for LatinMandell's categories, with sources cited for the inventories and non-obvious classifications.

---

# 13. VERDICT — LM-0 CONFIRMED

**LM-0 is CONFIRMED.** The candidate census, Ace's rulings R1–R13, and this edition together form the confirmed LM-0 record.

What confirmation settled:

- **Eight categories stand:** LINK (with the LINK-discourse subclass), POINT, CONDITION, NEGATE (with the NEGATE-partial subclass), ASK (with a construction layer), OPERATOR, FOCUS — and FLUFF, confirmed empty. The two families the six categories could not honestly hold now have categories of their own, exactly as Ace ordered.
- **Multi-category membership is law (R8):** a form may hold several memberships, and the parse records the use. The 488-row total is a cross-listed row count that reconciles exactly with the candidate census — confirmation moved rows and created two categories; it created and deleted no rows.
- **The morpheme counts are confirmed as LM-1's starting evidence only (R13).** Position conflicts (*dell, man, re*) and project-piece candidates are LM-1's rulings to make, not this document's.
- **The preposition reservoir (§1F) stays named and UNCONFIRMED (R9):** visible, not absorbed, not deleted.
- **The free roots harvest remains untouched** — about 1,693 entries, summarized only. Any import is LM-1's act, under CC BY-SA discipline.

**Next lawful step:** LM-1 routing (Director) on the confirmed morpheme evidence (§9), with LM-2's small-word tables taken as confirmed from this edition (LM-2's construction layer per R11). Nothing unconfirmed passes forward as if it were confirmed.

---

# 14. FLAGS — rows kept under a ruling whose own note still argues otherwise

Confirmation discipline: these rows are KEPT exactly where the rulings place them. The tension is flagged here, not silently edited away. A later LM-1/LM-2 pass — or Ace — may resolve them; nothing here blocks routing.

| # | row / place | tension |
|---|---|---|
| F1 | *ere* — LINK §1E | Its own note calls it archaic/formal and floats moving it to the reservoir, but R9 confirms the 166-row §1E inventory as listed for the first build — and *ere* is one of the 166 as listed. Kept in LINK; flagged as the one §1E row whose register argues for §1F. |
| F2 | *yon, yonder* — POINT §2B | Their notes label them "archaic/dialectal reservoir candidates," yet they sit inside POINT's confirmed rows rather than in a named reservoir. Kept in POINT under the confirmation; flagged because §1F's reservoir discipline was never extended to POINT. |
| F3 | *eh / huh* — tag particles, ASK §5 | The row's note says register status "needs Ace's ruling before inclusion in a core table." The confirmation includes the row as an ASK member; the register caveat stands unrepealed in its note. Kept; flagged. |
| F4 | *never mind, not now* — NEGATE §4C | Their notes say inclusion needs Ace's eye, and that Ace may reject *not now* as a separate row. The confirmation keeps both as NEGATE boundary rows; the caveats stand. Kept; flagged. |
| F5 | *if only* — CONDITION §3 | Its note retains it "as a candidate, not a core opener" (usually a wish/regret opener). It is confirmed as a CONDITION row, but its own note denies it core-opener status. Kept as a borderline member; flagged. |

— END OF LM-0 CONFIRMED EDITION —
