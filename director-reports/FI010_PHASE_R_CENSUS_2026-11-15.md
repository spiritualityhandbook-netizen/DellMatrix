# FI-010 PHASE R — MORPHOLOGY CENSUS

*LatinMandell Full Morphology (Ace directive 2026-11-14). Phase R = research + census BEFORE any table extension. Study executed 2026-11-15 by Uni (subagent lane), READ-ONLY: no code changed, nothing committed. Probes ran `form.mandell.morpheme.split_word` from g31proof_clone at main `17ae4ce86743d9c5ff848a1b48111119d9bf9a32` (the current main tip at study time).*

---

## 0. HEADLINE

The current morpheme table is a **Latin/Greek affix-and-root list, not a morphology of English.** Measured on a 71-word battery spanning every stratum and process FI-010 names:

| Verdict | Count | Share | Mean `accounted` |
|---|---|---|---|
| CORRECT | 4 | 5.6% | 1.00 |
| PARTIAL | 15 | 21.1% | 0.43 |
| WRONG | 18 | 25.4% | **0.65** |
| UNRESOLVED | 34 | 47.9% | 0.00 |

Three findings dominate:

1. **Germanic inflection — the commonest morphology in English — is entirely absent.** `walked`, `dogs`, `children`, `sheep` all score 0.00 as single UNRESOLVED pieces. The splitter cannot parse the two most frequent word-formation processes in the language it claims to parse.
2. **The honesty score rewards false parses.** WRONG words average *higher* `accounted` (0.65) than PARTIAL words (0.43). Twelve words score a perfect 1.00; **eight of the twelve are false** — `ran` resolves whole as **"frog"**, `men` as **"mind"**, `lab` as Greek *lab-* "grasp, seize", `oxen` as *o-* "against" + *xen-* "foreign", `better` as the letter name "B, b" + "rub, wear". A 1.00 on this machinery currently means "the table had a row", not "the parse is true".
3. **Whole strata do not exist in the table.** Old Norse scores 0.00 on six of seven probe words (`sky`, `window`, `husband`, `law`, `egg`, `knife`); the French stratum survives only as Latin leftovers inside it. The table's own composition explains why: of 2,245 rows, 2,087 (93%) are the LM-1 `external_wikipedia` Latin/Greek import; position classes are **2,025 prefix / 74 root / 74 whole_form / 18 suffix** — a prefix list with almost no suffix inventory, no inflection, no allomorphy, no suppletion links, no process representation of any kind.

The known exhibits reproduce exactly: `maybe` 0.0, `kinda` 0.0, `perhaps` PARTIAL 0.43 (*per-* caught, *haps* unresolved), `possibly` WRONG (greedy *po-* "drink").

**License bottom line** (detail in §4): the lawful feedstock exists. UniMorph (inflection paradigms) and MorphyNet (derivational segmentation) are importable with attribution/share-alike conditions; DBnary/Wiktionary and the existing Wikipedia lists are importable under CC BY-SA; WordNet/OEWN is permissive. MorphoLex is **CC BY-NC-SA 4.0** — the NC term is an Ace decision, not a Uni one. CELEX is non-free and excluded. SIGMORPHON's best use is as held-out **gold** for Phase D measurement, not as a table source.

---

## 1. METHOD

- **Instrument:** `split_word(word)` (LM-2, `form/mandell/morpheme.py`), the production splitter, run unmodified against the shipped table (`lm_table_v2.json` via the one loader, `form/mandell/lm_table.py`; strata precedence customs > ace_seed > inrepo > inrepo_force > inrepo_legacy > candidate > external_wikipedia) plus the LM-0 census (441 entries).
- **Table census (measured, same run):** 2,245 rows; 1,998 distinct pieces; strata — external_wikipedia 2,087, inrepo 54, ace_seed 53, inrepo_force 21, inrepo_legacy 14, candidate 16; position classes — prefix 2,025, root 74, whole_form 74, suffix 18, position_unresolved 52, operator 2.
- **Battery:** 71 words, chosen to cover every stratum × process cell FI-010 names, including the four known exhibits from the 2026-11-14 explainer (maybe / kinda / perhaps / possibly).
- **Verdicts** (judged against the true etymological stack, not against the table):
  - **CORRECT** — the returned stack is the true stack (segmentation and morpheme identities right), or an honest whole-form classification where no stack exists (conversion, census-classified suppletive).
  - **PARTIAL** — at least one returned piece is the correct morpheme (a truncated stem form counts, flagged in the note) with no false morpheme asserted; the rest is honestly UNRESOLVED.
  - **WRONG** — at least one resolved piece is a false morpheme: a greedy short-row match whose sense is not this word's morpheme (the *po-* "drink" standard). A WRONG verdict means the parse *misinforms*, which is worse than silence.
  - **UNRESOLVED** — no resolved piece (accounted 0.0, single UNRESOLVED piece). Honest silence.
- **Reproduction:** the battery is the word list in §2 with the true stacks printed beside the machine stacks; re-running `split_word` over it at the pinned commit reproduces every number in this file.

---
## 2. MEASURED COVERAGE BATTERY — 71 words

| Word | True stack | Machine stack (split_word) | Acc | Verdict | Note |
|---|---|---|---|---|---|
| walked | walk + -ed (PAST) | walked[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | no -ed anywhere in the parse path |
| dogs | dog + -s (PL) | dogs[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | no plural -s rule or row |
| children | child + -r- + -en (double PL) | children[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | double plural (child + -r- + -en) invisible |
| went | go + PAST (suppletive wend-) | went[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | suppletion: no go+PAST link exists |
| ran | run ablaut a (PAST) | ran[whole] | 1.00 | **WRONG** | resolved WHOLE as 'frog' (external row) — false friend at acc 1.00 |
| geese | goose ablaut ee (PL) | ge[prefix] + ese[UNRESOLVED] (unres) | 0.40 | **WRONG** | ge- 'earth' false prefix; ablaut plural invisible |
| better | good + COMP (suppletive bet-) | bet[prefix] + ter[root] | 1.00 | **WRONG** | bet = letter name 'B, b'; ter = 'rub, wear' — suppletive comparative read as noise |
| sang | sing ablaut a | sang[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | ablaut invisible |
| feet | foot ablaut ee (PL) | feet[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | ablaut plural invisible |
| men | man ablaut e (PL) | men[whole] | 1.00 | **WRONG** | resolved WHOLE as 'mind' (inrepo root) — the plural of man read as a Greek/Latin root |
| oxen | ox + -en (PL) | o[prefix] + xen[root] | 1.00 | **WRONG** | o- 'against' + xen- 'foreign' — the -en plural carved into Greek |
| was | be + PAST (suppletive) | was[whole] | 1.00 | **CORRECT** | LM-0 census whole classification 'function-be-past-singular' — honest, no stack claimed |
| sheep | sheep + zero PL | sheep[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | zero plural invisible |
| teeth | tooth ablaut ee (PL) | teeth[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | ablaut plural invisible |
| unhappiness | un- + happy + -ness (y->i) | un[prefix] + happiness[UNRESOLVED] (unres) | 0.18 | **PARTIAL** | un- boundary right but the only table row for un is 'one' (sense wrong); nested happy+-ness invisible |
| kingdom | king + -dom | kingdom[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | -dom not in suffix inventory |
| friendship | friend + -ship | friendship[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | -ship not in suffix inventory |
| strength | strong + -th (ablaut o->e) | st[prefix] + rength[UNRESOLVED] (unres) | 0.25 | **WRONG** | st- 'stand' false prefix; strong+-th invisible |
| darkness | dark + -ness | da[prefix] + rkness[UNRESOLVED] (unres) | 0.25 | **WRONG** | da- 'learn' false prefix; -ness missing |
| teacher | teach + -er | teach[UNRESOLVED] (unres) + er[suffix] | 0.29 | **PARTIAL** | -er correct; teach itself unresolved |
| hopeful | hope + -ful | hopeful[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | -ful missing |
| careless | care + -less | careless[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | -less missing |
| replay | re- + play | rep[prefix] + lay[UNRESOLVED] (unres) | 0.50 | **WRONG** | rep- 'crawl, creep' beats the true re- — greedy longest-match picks the false row |
| unhappy | un- + happy | un[prefix] + happy[UNRESOLVED] (unres) | 0.29 | **PARTIAL** | un- boundary right, sense row is 'one'; happy unresolved |
| quickly | quick + -ly | qui[prefix] + ckly[UNRESOLVED] (unres) | 0.43 | **WRONG** | qui- 'rest' false prefix; -ly missing |
| baker | bake + -er (e-drop) | ba[prefix] + ker[UNRESOLVED] (unres) | 0.40 | **WRONG** | ba- 'to step' false prefix; bake+-er with e-drop invisible |
| maybe | may + be | maybe[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | known exhibit: may+be compound invisible |
| breakfast | break + fast | breakfast[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | compound invisible |
| sunflower | sun + flower | su[prefix] + nflow[UNRESOLVED] (unres) + er[suffix] | 0.44 | **WRONG** | su- 'below/sew' false; -er carved out of 'flower' |
| blackbird | black + bird | blackbird[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | compound invisible |
| keyboard | key + board | keyboard[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | compound invisible |
| waterfall | water + fall | waterfall[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | compound invisible |
| kinda | kind + of (clipped compound/phrase) | kinda[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | known exhibit: kind+of clipping-compound invisible |
| perhaps | per- + hap(s) (Norse happ loan) | per[prefix] + haps[UNRESOLVED] (unres) | 0.43 | **PARTIAL** | known exhibit: per- caught (true boundary), [haps] = ON happ unresolved |
| google | Google (proper noun -> verb, zero) | google[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | conversion (proper noun -> verb) has no representation |
| run | run (verb -> noun, zero) | run[whole] | 1.00 | **CORRECT** | ace_seed whole_form 'move with urgency' — honest whole; conversion process itself unrepresented |
| beauty | beau- (Fr bel) + -ty | be[prefix] + auty[UNRESOLVED] (unres) | 0.33 | **WRONG** | be- 'bless' false prefix; beau- + -ty invisible |
| government | govern + -ment (Fr gouvernement) | gov[prefix] + ern[UNRESOLVED] (unres) + ment[suffix] | 0.70 | **PARTIAL** | gov = truncated govern stem (sense 'govern' right), -ment correct; ern stranded |
| question | quest + -ion (Lat via Fr) | ques[UNRESOLVED] (unres) + tion[suffix] | 0.50 | **PARTIAL** | -tion correct; ques(t) stem unresolved |
| fashion | Fr facon < Lat factio | fashion[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | opaque loan, no whole row |
| army | Fr armee < Lat armata | army[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | opaque loan, no whole row |
| village | ville + -age (Fr) | vill[prefix] + age[UNRESOLVED] (unres) | 0.57 | **PARTIAL** | vill- = villa stem (sense 'country house' right); -age suffix missed |
| dance | Fr danser (Germanic loan into Fr) | da[prefix] + nce[UNRESOLVED] (unres) | 0.40 | **WRONG** | da- 'learn' false prefix |
| preview | pre- + view (Lat videre via Fr vue) | pre[prefix] + view[UNRESOLVED] (unres) | 0.43 | **PARTIAL** | pre- correct; view unresolved (Fr vue < Lat videre unrecorded) |
| incredible | in- + cred + -ible (Lat credere) | in[prefix] + credible[UNRESOLVED] (unres) | 0.20 | **PARTIAL** | in- negation row present (2nd row); cred/credible never segmented — -ible path dead |
| transport | trans- + port (Lat portare) | trans[prefix] + port[root] | 1.00 | **CORRECT** | the battery's clean Latin win: trans- 'across' + port 'carry' |
| possibly | poss(e) + -ible + -ly (Lat posse 'be able') | po[prefix] + ssibly[UNRESOLVED] (unres) | 0.25 | **WRONG** | known exhibit: po- 'drink' (Greek) greedy false split of poss(e)+-ible+-ly |
| structure | struct + -ure (Lat struere) | stru[prefix] + ct[UNRESOLVED] (unres) + ure[suffix] | 0.78 | **PARTIAL** | stru- = struere stem (sense right), -ure correct; ct stranded |
| data | dat- + -a (Lat dare, PL participle) | data[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | Latin plural participle invisible |
| agenda | ag- + -enda (Lat agere, gerundive PL) | ag[prefix] + enda[UNRESOLVED] (unres) | 0.33 | **PARTIAL** | ag- = agere present stem (sense 'do' right, kind mislabeled prefix); gerundive -enda missing |
| biology | bio- + -logy (Gk bios + logos) | bio[prefix] + logy[root] | 1.00 | **CORRECT** | clean Greek win: bio- 'life' + -logy |
| philosophy | philo- + -sophy (Gk philosophia) | phil[prefix] + osophy[UNRESOLVED] (unres) | 0.40 | **PARTIAL** | phil- = philo- truncated (sense 'love' right); -sophy missing, osophy stranded |
| crisis | Gk krisis whole loan | crisis[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | whole Greek loan, no row |
| physics | Gk physica whole loan (via Lat) | physics[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | whole Greek loan, no row |
| democracy | demo- + -cracy (Gk demos + kratos) | dem[prefix] + ocracy[UNRESOLVED] (unres) | 0.33 | **PARTIAL** | dem- truncated demo- ('people' present as 2nd row; governing row says 'build'); -cracy missing |
| telephone | tele- + -phone (Gk) | tele[prefix] + phone[UNRESOLVED] (unres) | 0.44 | **PARTIAL** | tele- 'far' present (2nd row); -phone missing — and 'phone' alone is 0.0 too |
| theatre | Gk theatron whole loan (via Lat/Fr) | thea[prefix] + tre[UNRESOLVED] (unres) | 0.57 | **PARTIAL** | thea- = theaomai stem (sense 'view' right); tre stranded |
| sky | ON sky whole loan | sky[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | ON whole loan, no row — stratum absent |
| window | ON vindauga whole loan (vindr + auga) | window[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | ON vindr+auga historical compound invisible |
| husband | ON husbondi whole loan (hus + bondi) | husband[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | ON hus+bondi historical compound invisible |
| law | ON lag whole loan | law[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | ON whole loan, no row |
| egg | ON egg whole loan | egg[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | ON whole loan, no row |
| knife | ON knifr whole loan | knife[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | ON whole loan, no row |
| anger | ON angr whole loan | an[prefix] + ger[root] | 1.00 | **WRONG** | an- 'again/against' + ger- 'bear, carry' — a Norse whole loan carved into Latin/Greek noise |
| brunch | br(eakfast) + (l)unch blend | brunch[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | blend invisible |
| smog | sm(oke) + (f)og blend | smog[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | blend invisible |
| lab | laboratory clipped | lab[whole] | 1.00 | **WRONG** | resolved WHOLE as Greek lab- 'grasp, seize' — clipped 'laboratory' read as a classical root |
| flu | influenza clipped | flu[whole] | 1.00 | **WRONG** | resolved WHOLE as Latin flu- 'flow' — clipped 'influenza' read as a classical prefix |
| phone | telephone clipped (also Gk phone 'sound' homograph) | phone[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | the clipping is 0.0 while its own source word (telephone) is PARTIAL |
| motel | mo(tor) + (ho)tel blend | motel[UNRESOLVED] (unres) | 0.00 | **UNRESOLVED** | blend invisible |
| sitcom | sit(uation) + com(edy) blend | sit[prefix] + com[root] | 1.00 | **WRONG** | sit = 'food, grain' + com 'together' at acc 1.00 — both clipped halves falsely sensed |

Reading the table: `Acc` is the splitter's own `accounted` score (resolved chars / total chars). Compare the Acc column against the Verdict column — the disagreement between them *is* the census finding: the score measures table-row coverage, not parse truth.

---

## 3. STRATA × PROCESS COVERAGE MAP

COVERED = the battery shows the cell working. PARTIAL = some battery evidence works, named gaps remain. ABSENT = no battery evidence, or only false evidence. Every cell cites its battery evidence; "false" means the only hits were WRONG verdicts.

| Stratum | Inflection | Derivation | Compounding | Conversion | Suppletion | Ablaut | Clipping | Blending |
|---|---|---|---|---|---|---|---|---|
| **Germanic core** | **ABSENT** — walked/dogs/children/sheep all 0.00; no -ed/-s/-en machinery exists | **PARTIAL** — un-, -er fire (unhappy, teacher); -ness/-dom/-ship/-ful/-less/-ly all missing (kingdom, friendship, hopeful, careless, darkness) | **ABSENT** — maybe/breakfast/blackbird/keyboard/waterfall 0.00; sunflower false | **ABSENT** — no zero-derivation representation; run whole by ace_seed accident, google 0.00 | **ABSENT** — went 0.00; better WRONG; was saved only by the LM-0 census, not by any link | **ABSENT** — sang/feet/teeth 0.00; ran/geese WRONG | **ABSENT** — lab/flu WRONG (false classical roots); phone 0.00 | **ABSENT** — brunch/smog/motel 0.00; sitcom WRONG |
| **Old Norse** | ABSENT — no Norse cell applies; loans enter as whole lexemes and even that fails (below) | ABSENT — no evidence | ABSENT — window (vindr+auga), husband (hus+bondi) historical compounds both 0.00 | ABSENT — no evidence | ABSENT — n/a in loans, no links | ABSENT — n/a | ABSENT — no evidence | ABSENT — no evidence |
| **French** | ABSENT — no evidence | **PARTIAL** (weak) — government (-ment ✓, stem truncated), village (stem sense ✓, -age missed), question (-tion ✓ via Latin); beauty/fashion/army 0.00 | ABSENT — no evidence | ABSENT — no evidence | ABSENT — no evidence | ABSENT — n/a | ABSENT — no evidence | ABSENT — no evidence |
| **Latin** | **PARTIAL** (marginal) — agenda's ag- stem hit; data 0.00; Latin plural/gerundive morphology unrepresented | **PARTIAL** — transport CORRECT; preview/incredible/question PARTIAL; -ible path dead (credible never segmented), -ure/-tion work | **PARTIAL** — the prefix-compound layer is the table's one real strength: trans-/pre-/in- rows exist and fire correctly | ABSENT — no evidence | ABSENT — posse → possibly WRONG is the cell's only contact | ABSENT — n/a in loans | ABSENT — no evidence | ABSENT — no evidence |
| **Greek** | ABSENT — crisis 0.00; no Greek plural machinery (crises untested, no mechanism exists to test) | **PARTIAL** — biology CORRECT; philosophy/democracy/telephone/theatre PARTIAL: combining forms present but truncated (phil-, dem-), and -sophy/-cracy/-phone suffixes missing | **PARTIAL** — combining-form compounds are the same evidence as derivation here: bio+logy works end-to-end, longer forms strand remainders (osophy, ocracy) | ABSENT — no evidence | ABSENT — no evidence | ABSENT — n/a | ABSENT (false) — phone 0.00; lab/flu are Greek/Latin false friends, not coverage | ABSENT — no evidence |
| **Other borrowing** | ABSENT | ABSENT | ABSENT | ABSENT | ABSENT | ABSENT | ABSENT (false) — flu (Italian via influenza) WRONG | ABSENT |

**Worst gaps, ranked:**

1. **Germanic inflection: total absence.** The highest-frequency morphology in English has no rules, no rows, no allomorphs. This is the single largest capability hole FI-010 exists to close.
2. **The false-friend hazard is structural, not incidental.** 2,025 of 2,245 rows are classed "prefix", many of them 1–3 letters (ge, da, ba, po, st, su, qui, rep, o, be). Greedy longest-match over that inventory guarantees short Germanic words get carved into classical noise. 18/71 WRONG, concentrated exactly there. Any Phase T table growth that adds more short rows without a splitter guard makes this *worse*.
3. **Old Norse is not a stratum.** Six of seven probes at 0.00 and the seventh (anger) actively false. French survives only where Latin shows through it.
4. **Suffix inventory: 18 rows.** -ness, -dom, -ship, -ful, -less, -ly, -age, -ible, -sophy, -cracy, -phone, -enda are all missing. Derivation — the process Ace's own examples stress (unhappiness 0.18) — is suffix-driven, and the suffix shelf is nearly empty.
5. **No process layer at all.** Nothing in the table or the splitter represents a *process*: no inflection rules, no allomorph selection (bake→baker's e-drop, happy→happiness's y→i are both invisible), no suppletion links, no zero-derivation marker, no blend/clipping records. The table knows pieces; English is made of processes acting on pieces.

---

## 4. SOURCE + LICENSE AUDIT

LM-1 law: **license checked BEFORE import.** Each source: what it offers, its license in plain terms, lawfulness of import into DellMatrix with attribution, verdict. DellMatrix's own distribution posture matters for two terms below: the shipped table is distributed (GitHub, public), and rows composed from external glosses already carry per-row license + provenance in the LM-3 lineage (the loader's `external_wikipedia` rows cite source_revid + license CC BY-SA 4.0).

### 4.1 MorphoLex (Sánchez-Gutiérrez et al. 2018)
- **Offers:** derivational morphology for ~70,000 English words (MorphoLex-En): manual morpheme segmentation, morphological family size, derivational affix identification, process annotation (affixation / conversion / compounding are recorded in the resource's morphological variables), plus frequency data (subtitle frequencies via the English Lexicon Project lineage). This is the closest existing thing to the battery's gold standard for derivation + compounding.
- **License:** **CC BY-NC-SA 4.0** (stated in the UniSegments 1.0 resource survey, LREC 2022, and in the ACL 2024 tokenizer-benchmark resource table). Plain terms: use and adapt with attribution, derivatives under the same license, **non-commercial only**.
- **Import lawfulness:** lawful ONLY if DellMatrix's use is non-commercial. The NC term is a fact about Ace's project, not about the data — Uni cannot self-certify it. Even evaluation-only use (as Phase D gold) is a "use" under the license, though a non-commercial one if the project is.
- **Verdict: IMPORTABLE-WITH-CONDITIONS** — condition precedent is Ace's ruling that the project's use is non-commercial (Q-R.1). Until then: do not import rows; gold-use also held.

### 4.2 SIGMORPHON shared-task data
- **Offers:** (lemma, inflected form, feature bundle) triples for English inflection (verbs especially), as train/dev/test splits per year; the 2022 task adds morpheme-segmentation data. It is *sampled from UniMorph/Wiktionary*, not an independent lexicon.
- **License:** task pages state the pattern explicitly (2020 G2P task: "The code is released under the Apache License 2.0. The data is released under the Creative Commons Attribution-ShareAlike 3.0 Unported License inherited from Wiktionary itself."). Per-year inflection repos do not all carry their own LICENSE file — the upstream terms (CC BY-SA 3.0 via Wiktionary/UniMorph) are the operative ones, but each year's repo must be checked at import time.
- **Import lawfulness:** lawful with attribution + share-alike on the derived data, per-file check required.
- **Verdict: IMPORTABLE-WITH-CONDITIONS — but recommended as GOLD, not as a source.** Its unique value over UniMorph is curated held-out test sets: exactly what FI-010 Phase D needs to *measure* both weighing modes. Importing it as table feedstock would duplicate UniMorph with less coverage.

### 4.3 UniMorph (English)
- **Offers:** inflection paradigms: (lemma, form, UniMorph feature bundle) triples extracted and normalized from Wiktionary — English v4.0 validation F1 83.4 against UD treebanks (UniMorph 4.0 paper). This is the natural feedstock for the Germanic inflection hole: walked/dogs/children are *rows waiting to be linked*, and irregulars (went, geese, feet) appear as paradigm cells of their lemmas.
- **License:** per-language repos vary; the 2022 release is surveyed as **CC BY 4.0** (ACL 2024 benchmark resource table), while many per-language repos state **CC BY-SA 3.0**. The English repo's own LICENSE/README at the pinned commit was not read line-by-line in this study — that read is the named verification step.
- **Import lawfulness:** lawful under either variant with attribution; if the eng dataset is the SA variant, the derived stratum must be distributed under CC BY-SA (the LM-1 machinery already carries per-row license, so this is representable).
- **Verdict: IMPORTABLE-WITH-CONDITIONS** — pin the exact eng release, read its LICENSE file at that commit before import (Q-R.2), carry its license per-row.

### 4.4 Wiktionary via DBnary (or dumps/wiktextract)
- **Offers:** the raw material behind most of the above: English entries with inflection tables, etymology sections (the only audited source that *names strata* — "From Old Norse…", "Borrowed from French…" — in structured etymon chains), derived terms, and pronunciation. DBnary serves it as OntoLex RDF, refreshed twice monthly; wiktextract/kaikki.org serves JSONL extracts of the same source.
- **License:** DBnary states its own terms on its project page: "DBnary is derived from Wiktionary and is distributed under **Creative Commons Attribution-ShareAlike 3.0**." Wiktionary text itself is CC BY-SA (4.0 for current dumps) + GFDL dual-licensed; the CC path is the usable one.
- **Import lawfulness:** lawful with attribution + share-alike, same posture as the LM-1 Wikipedia import already in production.
- **Verdict: IMPORTABLE.** Primary use in Phase T: **stratum labels and whole-loan rows** (sky/window/husband as ON whole_form rows with etymon provenance) and etymology-verified stacks for the battery's PARTIAL tail — the one source that can say *which* stratum a piece belongs to.

### 4.5 CELEX
- **Offers:** the classic lexical database (English/German/Dutch): lemmas, inflectional and derivational morphology, phonology, frequencies — historically the gold standard MorphoLex was built to succeed.
- **License:** **non-free** (UniSegments survey lists CELEX 2.0 as "non-free"); distributed under a paid LDC license whose terms do not permit redistribution of the data inside a shipped product.
- **Import lawfulness:** not lawful to import into a distributed DellMatrix table without a license whose terms would still bar redistribution.
- **Verdict: NOT-IMPORTABLE.** Excluded from Phase T. (Its *design* — lemma + paradigm + derivation in one record — remains a free idea; ideas are not data.)

### 4.6 WordNet (Princeton) / Open English WordNet
- **Offers:** synsets and lemmas; for morphology specifically: **derivationally related form** links, morphosemantic links, and the Morphy exception files (irregular noun/verb/adjective/adverb forms — a ready-made irregular-inflection list: geese, feet, went-class verbs are enumerated there).
- **License:** Princeton WordNet license — permissive custom terms: "Permission to use, copy, modify and distribute this software and database and its documentation **for any purpose and without fee or royalty** is hereby granted", provided the copyright notice and disclaimer appear on all copies; Princeton's name may not be used in advertising. Open English WordNet (the maintained successor) is **CC BY 4.0**.
- **Import lawfulness:** lawful, commercial use included, with the notice carried.
- **Verdict: IMPORTABLE.** Cheapest lawful source for the irregular/suppletion seed list and derivational links; no segmentation, so it feeds links, not stacks.

### 4.7 DELAF-style lists (LADL/Unitex DELA)
- **Offers:** DELAS (lemmas + inflection codes) → DELAF (every inflected form, its lemma, category, and inflectional features). The English DELA is a large form inventory (~296,606 simple-word entries / 150,145 distinct lemmas per the Unitex resource pages). What it does NOT offer: segmentation — DELAF tells you *walked* belongs to *walk*, never where the morpheme boundary sits.
- **License:** **LGPLLR** (LGPL for Linguistic Resources): Unitex/GramLab states "The language resources included in Unitex/GramLab are distributed under the LGPLLR license", under which readable versions of the resources can be obtained. Plain terms: free use including commercial; the resource and modifications to it stay under LGPLLR; readable form must remain obtainable.
- **Import lawfulness:** lawful with conditions (attribution; derived dictionary data remains LGPLLR-licensed).
- **Verdict: IMPORTABLE-WITH-CONDITIONS — but low value for FI-010.** A form→lemma inventory duplicates what UniMorph gives with feature bundles; no boundaries, no strata. Not recommended for Phase T; noted so the omission is a decision, not an oversight.

### 4.8 Wikipedia morpheme lists (the LM-1 precedent)
- **Offers:** the Latin/Greek prefix/root/suffix lists already imported: 2,087 of the current table's 2,245 rows, with per-row source_revid provenance.
- **License:** **CC BY-SA 4.0**, already ruled on by Ace (2026-11-11) and already flowing through the loader's lineage (LM-3 marks stacks DERIVED_ADAPTATION when an external row governs).
- **Verdict: IMPORTABLE (proven in production).** Its limits are content limits, not license limits: it is a classical-affix list, which is why §3 looks the way it does. Phase T should grow *other* strata from *other* sources rather than more of this one.

### 4.9 Additional lead found during the audit — MorphyNet
Not on the mandated list; recorded because it is the missing derivation source. MorphyNet (Batsuren et al. 2021): derivational relations + segmentation derived from Wiktionary for 15 languages including English (~219k English entries in the benchmark survey), **CC BY-SA 3.0** (both surveys agree). Verdict if the Director admits it: IMPORTABLE-WITH-CONDITIONS (attribution + SA on the derived stratum). It is the only audited source whose segmentations cover derived words *across* strata — precisely the PARTIAL belt in §2 (government, incredible, unhappiness-class words at scale).

### License verdicts, one line each

| Source | License | Verdict |
|---|---|---|
| MorphoLex | CC BY-NC-SA 4.0 | IMPORTABLE-WITH-CONDITIONS (Ace must rule the use non-commercial first) |
| SIGMORPHON data | CC BY-SA 3.0 (upstream, per-task check) | IMPORTABLE-WITH-CONDITIONS — use as Phase D gold, not feedstock |
| UniMorph (eng) | CC BY 4.0 / CC BY-SA 3.0 (per-repo; verify at pin) | IMPORTABLE-WITH-CONDITIONS |
| Wiktionary via DBnary | CC BY-SA 3.0 (DBnary) / CC BY-SA (Wiktionary) | IMPORTABLE |
| CELEX | non-free (LDC) | **NOT-IMPORTABLE** |
| WordNet / OEWN | Princeton permissive / CC BY 4.0 | IMPORTABLE |
| DELAF (Unitex DELA) | LGPLLR | IMPORTABLE-WITH-CONDITIONS (low value — no segmentation) |
| Wikipedia lists (LM-1) | CC BY-SA 4.0 | IMPORTABLE (already in production) |
| MorphyNet (lead) | CC BY-SA 3.0 | IMPORTABLE-WITH-CONDITIONS (if admitted) |

---

## 5. PHASE T SHAPE — the smallest lawful extension through the ONE loader

Design constraint (FI-010 as registered): **no second morpheme authority.** Everything below enters through `form/mandell/lm_table.py`'s load path and is consumed by `morpheme.py`'s existing splitter/composer. New data arrives as new *strata* and one new *layer*, never as a new table path.

### 5.1 What feeds which stratum

| New material | Source | Lands as | Fixes (battery) |
|---|---|---|---|
| English inflection paradigms (lemma, form, features) | UniMorph eng (pinned, license-verified) | inflection layer (5.2), not piece rows | walked, dogs, children, sheep |
| Irregular + suppletive form lists | WordNet/OEWN exception files + UniMorph paradigm cells | suppletion/allomorph records in the inflection layer | went, geese, feet, teeth, men, sang |
| Derivational segmentation across strata | MorphyNet (if admitted), else DBnary derived-terms + Ace-curated seed | new stratum rows (`external_morphynet`) with `split` records, ranked between `candidate` and `external_wikipedia` | government, incredible, unhappiness, kingdom, friendship (-ness/-dom/-ship enter as suffix rows with splits) |
| Stratum labels + whole-loan rows | DBnary/Wiktionary etymology | whole_form rows in per-source strata (`external_dbnary`) carrying an `origin_stratum` field (ON / Fr / Lat / Gk / …) | sky, window, husband, law, egg, knife, fashion, army, crisis, physics |
| Classical combining-form completions (-sophy, -cracy, -phone, -logy-class suffixes) | existing Wikipedia lists, extended harvest | more `external_wikipedia` suffix rows | philosophy, democracy, telephone |
| Derivational family + process gold | MorphoLex | **held out** (Phase D gold) unless/until Q-R.1 resolves | measures, never feeds |

### 5.2 Inflection as rules + allomorphs, not rows

Inflected forms must NOT become piece-table rows (a `walked` row would teach the splitter nothing about `talked`). The inflection layer is a **pair-bound sidecar** beside the v2 table — same loader family, same generation-binding discipline as the v2 table/collisions pair — holding three record kinds:

1. **Rules** (regular): feature bundle → stem transformation + affix, with allomorph selection stated as data: plural {-s / -es / -en / zero}, past {-ed with doubling / e-drop / y→i variants}, participle, comparative. A rule is a record, judged like a row: provenance + license attached.
2. **Stem-change classes** (ablaut): enumerated class records (sing/sang/sung, foot/feet pattern classes) — the class IS the record; members link lemma ↔ form with the class id. No fake segmentation is minted: `feet` parses as foot + PL via the class link, and the receipt says so.
3. **Suppletion links**: (form, lemma, feature bundle, link_type=suppletive). The honest stack for `went` is **go + PAST (suppletive)**: `split_word` returns two pieces — the lemma piece (resolved via the link, kind `root`, annotation `suppletive_link`) and a feature piece (kind `inflection`, text `PAST`). `accounted` counts the form as accounted *by link*, and the receipt distinguishes link-resolution from segmentation-resolution so the honesty score never confuses the two. `was` already shows the acceptable shape: the LM-0 census classifies it whole as be-past; the suppletion link generalizes that honesty into a stack.

`split_word` consults the inflection layer BEFORE the greedy piece matcher (a whole-form link beats a greedy carve — this is also the false-friend guard for the worst cases: `ran` resolves as run + PAST by class link, never as "frog"). Whether that consultation order is a Phase T deliverable or a separate LM-2 amendment is Q-R.4.

### 5.3 What Phase T does NOT do

- No new loader, no new table file format beyond the pair-bound sidecar pattern the loader already verifies.
- No NC data (MorphoLex) in any shipped artifact until Q-R.1 is ruled.
- No CELEX data, ever, under current terms.
- No blended confidence: link-resolved, segment-resolved, and unresolved stay three distinct receipt states (LM-2/LM-3 honesty discipline).
- No splitter rewrite: the greedy matcher stays; Phase T adds the layer it consults first and the rows it was missing. The false-friend guard beyond whole-form links (e.g. minimum-length competition for short pieces) is named, not smuggled in (Q-R.4).

---

## 6. OPEN QUESTIONS FOR THE DIRECTOR / ACE

- **Q-R.1 (Ace):** Is DellMatrix's use non-commercial within the meaning of CC BY-NC-SA 4.0? If yes, MorphoLex becomes available as Phase D gold (and, with SA accepted, as feedstock). If no or undecided, MorphoLex stays entirely unused and Phase D gold is SIGMORPHON + a hand-built Ace/Director set.
- **Q-R.2 (Director):** UniMorph eng — which pinned release, and does its LICENSE at that pin read CC BY 4.0 or CC BY-SA 3.0? If SA 3.0: may an SA-3.0 stratum ship inside the same table as the SA-4.0 external stratum (per-row licenses already coexist in the lineage), or must SA-3.0 material live in the pair-bound sidecar to keep license families physically separate?
- **Q-R.3 (Director):** Inflection layer as a pair-bound sidecar (recommended in §5.2) vs. rows in the main table — confirm the sidecar shape before Phase T builds the importer.
- **Q-R.4 (Director):** Splitter consultation order (inflection/suppletion links before greedy match) and any short-piece guard — inside Phase T's scope, or a separate LM-2 amendment circuit with its own failing-first receipts (the `ran` = "frog" exhibit is the failing-first candidate either way)?
- **Q-R.5 (Director):** Admit MorphyNet (CC BY-SA 3.0) as the derivation feedstock (§4.9), or restrict Phase T derivation to DBnary + curated seed (slower, thinner)?
- **Q-R.6 (Director/Ace):** Do Germanic irregulars also enter the LM-0 census as whole entries (the `was` pattern, Ace-confirmed census process), or is the inflection layer their only home? The two homes have different authorities (census = Ace-confirmed; layer = imported data) — the study recommends the layer only, census untouched, but the precedent cuts the other way and the call is not Uni's.

---

## 7. SOURCES CITED

Battery + table census: measured in-repo at main `17ae4ce` (this study, §1–§3). License and content facts:

- MorphoLex license + size; UniMorph license; MorphyNet license — resource tables in *Greed is All You Need: An Evaluation of Tokenizer Inference Methods* (ACL 2024, arXiv:2403.01289) and *Towards Universal Segmentations: UniSegments 1.0* (LREC 2022) — both list MorphoLex CC BY-NC-SA 4.0, MorphyNet CC BY-SA 3.0, CELEX non-free.
- UniMorph content + English quality — *UniMorph 4.0: Universal Morphology* (LREC 2022, arXiv:2205.03608): paradigms extracted from Wiktionary; English v4.0 F1 83.4 vs UD.
- SIGMORPHON data licensing — SIGMORPHON 2020 G2P task page (sigmorphon.github.io/sharedtasks/2022/G2P): code Apache 2.0; data CC BY-SA 3.0 "inherited from Wiktionary itself".
- DBnary license + content — DBnary project page (kaiko.getalp.org): "derived from Wiktionary and is distributed under Creative Commons Attribution-ShareAlike 3.0"; GETALP resource listing (lig-getalp.imag.fr) confirms CC BY-SA 3.0, twice-monthly releases.
- WordNet license — Princeton WordNet license text (wordnet.princeton.edu, "License and Commercial Use of WordNet"): use/copy/modify/distribute for any purpose without fee or royalty, notice on all copies. Open English WordNet under CC BY 4.0 (WNDB_License.txt, globalwordnet/english-wordnet).
- DELA/DELAF license + English size — Unitex/GramLab language-resources page (unitexgramlab.org): resources distributed under the LGPLLR license, readable versions obtainable; English dictionary ~296,606 simple words / 150,145 distinct lemmas.
- LM-1 precedent — in-repo: `form/mandell/lm_table.py` header (Ace license ruling 2026-11-11, PR #390–#393) and the table header's attribution/manifest fields.

*End of Phase R census. Phase T does not start on this document alone: Q-R.1–Q-R.6 carry the decisions it depends on.*
