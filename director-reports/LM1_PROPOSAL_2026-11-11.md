# LM-1 — THE TABLE: RESEARCH & PROPOSAL PACKAGE

**Date:** 2026-11-11 · **Prepared by:** Uni (research/proposal only — no code changed, no data imported, no PR)
**Governing directive:** Director mail 1a1cc1c381c84852 (2026-11-11 13:35 CST) — LM-1 package requires SOURCE IDENTIFICATION of the LM-0 census and a PROVENANCE/LICENSE GATE on the external roots table before any import; restated for the Keeper verbatim in the same mail.
**Plan of record:** `LATINMANDELL_BUILD_PLAN_2026-11-11.md` §4 (LM-1 — THE TABLE) and §3 (sources/licenses).
**Structure:** evidence first (§§1–3), proposal second (§4), numbered ruling questions at the end (§4e).

---

## 1. LM-0 SOURCE IDENTIFICATION

The LM-1 build consumes two LM-0 outputs: the confirmed small-word tables (input to LM-2) and the confirmed morpheme-side counts (LM-1's starting evidence, R13). The canonical LM-0 record is the **confirmed edition**:

| Fact | Value (verified 2026-11-11 by direct read + hash) |
|---|---|
| File | `LM0_CENSUS_CONFIRMED_2026-11-11.md` |
| Locations | `~/workspace/goals/dellmatrix-capability-circuits/files/` and `hidden_files/lm0/` — the two copies are **byte-identical** |
| SHA-256 | `c37adb098db942209b18e05ae9d9736fbee3b563532873f016a3474293da85c0` |
| Size | 1,155 lines / 107,078 bytes |
| Source document it confirms | `LM0_CENSUS_2026-11-11.md` (the candidate census; 1,186 lines / 98,906 bytes; preserved unchanged) |

**Confirmation trail.** Ace's ruling (2026-11-11, quoted verbatim in the edition): *"Confirm the census and make categories for anything that needs its own and promote and put everything in its correct category. Some may end up in multiple categories."* The edition executes it as rulings **R1–R13** (two new categories OPERATOR/FOCUS; articles promoted to POINT; FLUFF confirmed empty; NEGATE-partial and LINK-discourse subclasses; multi-category membership is law) plus **R14**, Ace's same-day design-note addendum (pure meaning defined in advance; sloppy delivery never makes a token meaningless). R13 governs LM-1 specifically: *the morpheme counts are confirmed as LM-1's starting evidence only; position conflicts are LM-1 rulings, NOT settled by LM-0; the free roots list is NOT imported by LM-0.*

**488-row arithmetic — verified.** Candidate census: LINK 233 + POINT 114 + CONDITION 34 + NEGATE 37 + ASK 34 + FLUFF 3 + Boundary 33 = **488**. Confirmation moves rows and creates/deletes none (FLUFF's 3 → POINT; the 33 boundary rows → OPERATOR 27 + FOCUS 6): confirmed **LINK 233 + POINT 117 + CONDITION 34 + NEGATE 37 + ASK 34 + OPERATOR 27 + FOCUS 6 + FLUFF 0 = 488**. The total counts cross-listed rows, not unique spellings (R8).

**GAP-1 (blocking for a canonical build, proposed fix in §4d item 1): the confirmed census is NOT in the GitHub repository.** Verified 2026-11-11: `git ls-tree -r origin/main` (main @ `08f8ceb94fdf1f2ed443d767aea1d2c209c0eb67`) contains **zero** LM-0 files — the census exists only in the goal workspace (`files/` + `hidden_files/lm0/`). LM-1 therefore has no canonical repo anchor to cite, diff against, or pin. §4d item 1 proposes publishing the confirmed edition to `director-reports/` in the LM-1 circuit's first change, so the table's provenance chain terminates at a repo commit.

---

## 2. IN-REPO MORPHEME EVIDENCE INVENTORY

Repository state inspected: clone at merged main `76afea8` lineage; `form/`, `src/`, `preform/` verified **byte-identical** between `76afea8` and latest `origin/main` `08f8ceb` (the intervening commits are director-reports records only), so every code fact below holds at current main.

### 2.1 `form/mandell/morpheme.py` (190 lines) — the typed piece inventory

**Recount, executed against the module (not read off the census):** PREFIXES **24**, ROOTS **19**, SUFFIXES **11** → **54 typed assignments**. Label overlaps: `re` ∈ prefixes ∩ suffixes; `dell` ∈ roots ∩ suffixes; prefixes ∩ roots = ∅ → normalized union **52**. The flat `MORPHEMES` dict adds 5 whole-form extras (*mandel, mandell, nurture, commandell, omnifacure*) → **57 flat unique pieces**. All census figures (54 / 52 / 57) reproduce exactly. A separate hardcoded `force_mandell_morphemes` table carries **21 whole-word split entries** (Commandell → Com-man-dell, etc.).

**Duplicate/ambiguity rule currently in force — fixed precedence, silently applied.** `sense_of()` checks PREFIXES → ROOTS → SUFFIXES → flat dict and returns the first hit; `explain_morphemes()` classifies kind in the same order. Demonstrated live on current code: `sense_of("re")` returns the **prefix** sense ("again · iterative · back") — the suffix sense ("loop / again · return frame") is unreachable through that path; `explain("Com-man-dell")` classifies *dell* as **root**, shadowing its suffix entry. No conflict is ever surfaced to a caller.

**Production callers (traced, not filename-inferred):** `latinmandell.py` (lazy imports inside `root_of`/`_morph_depth`) and `form/repl.py` (imports at lines 22/39; the morpheme handler at line 370). Nothing else imports it outside tests.

**Boundaries — what it does NOT do:** `split_delimited()` splits **only** on explicit delimiters (`-_/`); verified live: `split_delimited("transform")` → `["transform"]`. There is no segmentation of undelimited words beyond the 21-entry force table. Docstring law: "Does not reprogram host BPE." Module smoke: **6/6 PASS** (run 2026-11-11).

**Provenance:** owner-authored founding material — commits `00f6d15` (2026-08-01, "Origin: Mandel Codex high-S slice"), `dae4015`, `31964f2` (both 2026-08-01, lexicon expansion/densification), all by the repository owner. **GAP-2:** no Director-circuit approval artifact for these rows exists in-repo; they predate the current circuit record. They stand as the Architect's own seed material — which is precisely why the standing ruling gives them win-priority (§3.4) — but the proposal does not invent a gate record for them.

### 2.2 `form/mandell/latinmandell.py` (360 lines) — the surface-root layer

**Verified by execution:** `ROOTS` = **53 English surface-root entries**, each carrying `{la, sense, dell}` — every one of the 53 has a Dell number (none null). Latin citation forms: **68 as written / 65 unique** (duplicated citations: *forma* ×2 — idea, schema; *ordinare* ×2 — map, rank; *servare* ×2 — keep, save). All census figures reproduce exactly.

**Customs:** `_CUSTOM` module dict; `customize()` binds `{label, la, dell, term, sense, surface}`; persistence flows through `form/mandell/language.py` (`export_customs`/`import_customs`) and `form/persist.py` (state **VERSION = 7**, `persist.py:39`; serialized as `latinmandell_customs`, `persist.py:371`). **Customs win:** `root_of()` consults `_CUSTOM` before builtin `ROOTS`, and hyphen morphology before both. Module smoke: **8/8 PASS** (run 2026-11-11).

**Production callers (traced):** the REPL door — `form/repl.py` `_handle_latinmandell` (line 332; dispatched line 2626) exposing explain/deepen/customize; `form/mandell/activation.py:127` (`explain_dell()` → `explain()`); `language.py`/`persist.py` for customs. Remainder are tests.

**Boundaries — explanatory only, verified:** `form/mandell/translate.py` contains **zero** references to `latinmandell` or `morpheme` (grep count 0) — the translator never calls either module; nothing in the execution path routes through them. `root_of()` returns `None` for unknown words (honest at the single-word level), **but** `deepen()` returns only the words that resolved and silently drops the rest — verified live: `deepen("anchor the law and keep the trace")` → only *keep* (servare) returned; the five unresolved tokens are absent, not flagged. LM-1's schema (§4a) must not let LM-2 inherit that silence. A 7-ending suffix-hint fallback (-tion/-sion/-ment/-able/-ible/-ous/-ive) composes senses for unlisted words.

**Provenance:** owner commits `aadb280` (2026-08-01) and `e573a97` (2026-08-02, "la door in REPL, explain/deepen/customize, persist customs v7"). Same GAP-2 note as §2.1.

### 2.3 `form/mandell/polyglot.py` (218 lines) — NOT a morpheme source

`LA_MAP` holds ~19 Latin command-phrase regex patterns (creare/servare/onerare…) mapping Latin intake phrases to English command glosses, plus language metadata (`FOUNDATION_LANGS`, `CORE_LANGS = ("la",)`). It contains **no prefix/root/suffix inventory** and contributes **zero rows** to the morpheme evidence base; its only direct importer is its own test module. Recorded here so the build does not re-discover it as a candidate table: it corroborates Latin surface forms for command verbs, nothing more.

### 2.4 `src/core/mandel_ontology.js` (134 lines) — legacy layer, 14 entries

`MORPHEMES` (line 86): 5 Latin prefixes (Com-, Re-, Pre-, Trans-, De-), 4 Latin roots (-fac-, -log-, -mit-, -spec-), 5 Greek operators (Alpha, Delta, Lambda, Sigma, Omega) = **14 entries**. Against `morpheme.py`'s normalized labels it contributes exactly **2 new labels: *lambda*, *sigma***. Authority note: `src/` is an earlier generation, **not** the production runtime (`form/` is); no production Python path consumes this file. Its rows are evidence/candidates for LM-1, not live data.

### 2.5 Preform material — candidates only, gated by Leight/Loure

`preform/pages/21_AFFIX_LEXICON_STARTER.md`: 10 proposed prefixes + 5 proposed suffixes = **15 candidate rows**, each prefix tagged with an admission path. `preform/LANGUAGE_PREFORM.md` states the creation law. Both files carry **NOT IN USE** status (design history; production runtime is `form/`).

- **Leight** (create-path, aligns 08[Create]): define a NEW Latin-Mandel unit from scratch. Gate: Manual/Manuall + Mandellafactors; each part needs a standalone definition; **Architect number-confirm → True registry**.
- **Loure** (change-path, aligns 04[Evolve]): ADOPT a non-Latin word's already-defined affix sense into Latin-Mandel. Gate: Manual + clash/test against the existing category; must not silently overwrite true terms.
- Standing rule: classical etymology is **not** the gate; standalone definition + Manual classification + Architect confirmation is.

### 2.6 Position conflicts — OPEN QUESTIONS for LM-1 (from LM-0 A19 / census §9.7; NOT resolved here)

| Piece | Conflict (all positions attested in-repo) |
|---|---|
| **dell** | ROOT and SUFFIX in `morpheme.py` (glosses differ: "nested unit · operator cell · protected pocket" vs "fragment · nested cell · protected pocket"); proposed PREFIX in the preform lexicon ("Operator-bearing"). Census: the highest positional-conflict piece in the inventory. |
| **man** | PREFIX in `morpheme.py` ("control · hand · execution"); preform *Man-/Mandel-* means protocol/operator domain (a different gloss); *-man* proposed as SUFFIX in preform ("Term-only (Dellman)"). Three candidate uses, not one settled piece. Near-neighbor **mand** is a ROOT ("command · order · execute") — a segmentation-collision risk on top of the position question. |
| **re** | PREFIX ("again · iterative · back") and SUFFIX ("loop / again · return frame") in the same file, plus ontology prefix (Re- "again / iterative"). Current code silently resolves to the prefix sense (§2.1). Census options: two positional entries, or one entry with two positional frames. |

Secondary, same family (recorded in census §9.7, carried into §4e): *alpha/delta/omega* are prefixes in `morpheme.py` but Greek **operators** in the ontology (role conflict, not mere duplication); *log* gloss emphasis differs across sources (trace/reason vs record/track); *mand/men/mend* are visually close project-central pieces (boundary-test risk); *-ell* is contained in *dell*; *nur/nurture* (piece vs whole-form); very short pieces *fu/nud/tu/ce* carry false-split risk and need negative examples.

---

## 3. EXTERNAL TABLE — PROVENANCE AND LICENSE GATE

### 3.1 The source, as it actually exists today (fetched live 2026-11-11)

The plan and census name "Wikipedia's *List of Greek and Latin roots in English*". The live structure is a **four-level citation chain**, not one page:

- **Hub:** `https://en.wikipedia.org/wiki/List_of_Greek_and_Latin_roots_in_English` — pageid 3620462, current revision **1378877227** (2026-10-06T17:38:10Z). The hub itself holds no table; it points to three range pages.
- **Range pages:** A–G (rev 1353827304, 2026-05-12), H–O (rev 1280989339, 2025-03-17), P–Z (rev 1296298036, 2025-06-19) — transclusion hubs.
- **24 letter pages** (A–V, X, Z; **no W or Y pages exist**) carry the actual tables. Each is edited independently; revisions span 2022-08-24 (X, rev 1106460130) to 2026-10-25 (T, rev 1381965170). The full per-letter revision manifest is Appendix A — an import must pin **24 revisions**, not one.

**Row count — counted, with method.** Each letter page contains exactly one wikitable. Counting data rows in the wikitext (row chunks after the header row, per letter) gives **1,693 data rows total** — an exact match to the census's "~1,693" estimate. Cross-validation: rendered-HTML `<tr>` counts on two spot-checked letters (K: 7, X: 7) match the wikitext counts exactly. **Row ≠ piece:** each row's Root cell groups a head form with its allomorphs (the pages' own collation note: root groups are "collated under the head item"); extracting the bolded forms per row gives **≈2,096 root forms** (approximate — bold-markup extraction; stated uncertainty ±~2%). LM-2 will consume forms, so both numbers matter: **1,693 rows / ≈2,096 forms**.

**Fields per entry** (header row, verbatim): `Root | Meaning in English | Origin language | Etymology (root origin) | English examples` — 5 fields: root forms (head + allomorphs in one cell), English gloss, origin language, etymology (with dictionary references — L&S, LSJ — embedded as citations), and English example words.

**GAP-3 (design constraint):** row-level anchors are only partially available — some rows carry HTML ids (e.g. `id="ac1-"`), coverage unknown. A row-level source trace therefore cannot rely on upstream anchors; §3.3 designs around page-revision + row-ordinal + head-form keys instead.

### 3.2 The license — evidence, quoted

Wikipedia text is **not** public domain and "free" does not mean unconditioned. From **Wikipedia:Copyrights** (fetched 2026-11-11):

- License: *"Most of Wikipedia's text and many of its images are co-licensed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA) and the GNU Free Documentation License (GFDL)"* — the operative version is **CC BY-SA 4.0**.
- Permission exists but is conditioned: *"Everyone already has permission to edit and reuse article text under open content licenses by the authors, as long as their use complies with the licensing terms, gives proper attribution, and licenses any changes under the same terms."*
- **Attribution** (Reusers' obligations): *"provide credit to the authors either by including a) a hyperlink (where possible) or URL to the page or pages you are re-using, b) [an equivalent stable copy], or c) a list of all authors."*
- **Copyleft/ShareAlike:** *"If you make modifications or additions to the page you re-use, you must license them under the Creative Commons Attribution-ShareAlike 4.0 International License or later."*
- **Indicate changes:** *"you must indicate in a reasonable fashion that the original work has been modified."*
- **Licensing notice:** *"Each copy or modified version that you distribute must include a licensing notice stating that the work is released under CC BY-SA and either a) a hyperlink or URL to the text of the license or b) a copy of the license."*

The CC BY-SA 4.0 deed states the ShareAlike term directly: *"If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original"* — plus Attribution and **No additional restrictions**.

**What this means for a derived table (analysis — flagged as analysis, not legal advice):**

1. Re-schematizing 1,693 rows into LM-1's row shape is a modification/adaptation of the reused pages. The **imported stratum** — the imported rows and transformations of them — must be distributed under **CC BY-SA 4.0 (or later)**, with attribution (links to the 24 letter pages), a change indication, and the licensing notice carried in the distributed table itself.
2. **Copyleft reach:** ShareAlike attaches to the adapted material. It does not, by its own terms, relicense Ace's independent pre-existing material (his 53 roots, `morpheme.py` pieces, customs) merely for sitting in an adjacent row. But if the combined table is distributed as one intermingled work — merged glosses, strata indistinguishable — the safe reading collapses toward licensing the whole table BY-SA. Two compliant shapes exist: **(a) segregation by design** — per-row provenance + license fields keep the imported stratum identifiable and BY-SA, while Ace's strata keep project terms (recommended in §4a); **(b) one-table BY-SA** — license the entire combined table CC BY-SA 4.0, which extends copyleft over Ace's contributed glosses inside the table. Choosing between (a) and (b) is a ruling, not an implementation detail → Q-LM1.2.
3. **Redistribution is the trigger and DellMatrix will redistribute:** the table ships inside the repository (root LICENSE is **MIT**, verified — so the BY-SA data file must carry its own notice and must not be silently blanketed by the repo's MIT grant).
4. Facts-vs-expression does not rescue a wholesale import: individual facts (a root's meaning) are not copyrightable, but a 1,693-row wholesale lift takes the compilation's selection, arrangement, and gloss wording — its expression. The proposal does not rely on "the facts are free" for a bulk import. (Wikipedia:Copyrights itself notes copyright "governs the creative expression of ideas, not the ideas or information themselves" — relevant to hand-reformulated entries, not to a bulk table lift.)
5. GFDL: the pages are dual-licensed; building on the CC BY-SA grant alone is the clean path (GFDL election → Q-LM1.7).

**Alternatives/complements assessed:** **Wiktionary** — same license family, verified: *"The original texts of Wiktionary entries are dual-licensed to the public under both the Creative Commons Attribution-ShareAlike 4.0 International License (CC-BY-SA) and the GNU Free Documentation License."* It is lemma-shaped, not table-shaped — a verification complement for individual roots, not a substitute source for the table. **CLTK / Whitaker's Words** — tooling only; the plan (§3) records **MIT** for CLTK and for the ArchimedesDigital/open_words port (attribution; verify exact package/version at use time). Neither is an LM-1 data source. Project law stands: a public repo with **no license is NOT free to use** — no no-license source appears anywhere in this proposal.

### 3.3 Row-level source-trace design (proposal)

Every imported row carries, in the table itself: `source_page` (letter page title), `source_revid` (the pinned revision imported from), `source_row_ordinal` (row index within that page's table at that revision), `head_form` (the row's head root form), `import_batch` (date + importer version), and `transforms` (what the importer changed — e.g. "gloss verbatim", "examples trimmed", "allomorphs split to forms[]"). The table ships with a **source manifest**: the 24 pinned page revisions (Appendix A is the pre-import snapshot of exactly this), the license notice, the attribution block (page URLs), and the change indication. A refresh re-pins revisions and diffs the manifest — upstream drift is a reviewed event, never a silent overwrite.

### 3.4 Collision handling (proposal; standing ruling applied)

Standing ruling (plan §LM-1, restated in the directive's ancestry): **Ace's 53 roots + customs WIN conflicts; conflicts logged, never silent.** Design: when an imported form collides with an Ace-stratum piece (same normalized form, any position), the Ace entry keeps the seat; the imported row is retained as a **demoted alternate** with `conflict_status = collision_logged` and a pointer to the winning entry; every collision is written to a **published collision log** (build artifact in the circuit record — form, both senses, both provenances, disposition). A build that produces collisions it did not log fails its own probes (§4c, P3).

### 3.5 NO-IMPORT FALLBACK (what LM-1 delivers if the license gate fails)

If the ruling is NO (or Ace declines whole-table BY-SA and segregation is rejected), LM-1 ships a **harvest-only table**: the in-repo strata alone — `morpheme.py` 57 flat pieces (54 typed), `latinmandell.py` 53 surface roots, ontology's 2 new labels as candidates, preform 15 rows held at candidate status pending Leight/Loure — in the §4a schema with full provenance, position conflicts still quarantined as `position_unresolved`. Consequences, stated honestly: the table is ~110 confirmed pieces instead of ~1,693 rows; the plan's 100-word spot battery is re-scoped to the harvest's actual coverage; LM-2's splitter ships with a much smaller dictionary and correspondingly more honest UNRESOLVED output. The fallback is a complete, lawful LM-1 — smaller, not broken.

---

## 4. BOUNDED LM-1 PROPOSAL

### 4a. Schema — the table's row shape (bounded to what LM-2 THE SPLITTER will consume)

One row per **piece** (forms split out of grouped upstream rows; the upstream row survives as the trace unit):

| field | content |
|---|---|
| `piece` | the surface form (e.g. `trans-`, `-fac-`, `servare`) |
| `position_class` | `prefix` \| `root` \| `suffix` \| `operator` \| `whole_form` — a piece whose position is under a §2.6 conflict carries the conflict in `conflict_status`, not a guessed class |
| `allomorphs` | sibling forms of the same piece (from the upstream row's grouped cell, or Ace-stratum variants) |
| `language` | `Latin` \| `Greek` \| `project` (Mandell-native pieces) |
| `sense` | the gloss (Ace-stratum wording wins on collision per §3.4) |
| `dell` | Dell number or null — present on Ace's 53 roots today; null elsewhere until LM-3 |
| `examples` | English example words (upstream column; trimming recorded in `transforms`) |
| `provenance` | `{stratum, source_id, source_revid, license}` — stratum ∈ `ace_seed` (morpheme.py / latinmandell.py), `ace_custom`, `wikimedia_import`, `ontology_candidate`, `preform_candidate` |
| `conflict_status` | `clean` \| `collision_logged` \| `position_unresolved` |
| `notes` | free record (etymology citations preserved for imported rows) |

Table-level header: source manifest (pinned revisions per §3.3), attribution block, CC BY-SA licensing notice for the imported stratum, generator/importer version, row + form counts. **Nothing in the schema serves LM-3 composition, LM-4 wiring, or UX** — those circuits extend it under their own rulings.

### 4b. Migration compatibility — existing behavior is the floor

- `latinmandell.py` and `morpheme.py` public behavior is **preserved**: `explain` / `deepen` / `customize` / `seed_for_root` / `split_delimited` / `force_mandell_morphemes` semantics and output shapes unchanged; the Com-man-dell hyphen path returns byte-identical parts.
- The table is **additive data**. If the table file is absent, the modules behave exactly as today (builtin dicts only) — no hard dependency is introduced.
- **Customs still win:** lookup order remains customs → Ace seed → imported stratum; persist **v7** customs format is untouched (no state migration).
- The in-module dicts are NOT deleted or rewritten by LM-1; the table is the growing authority beside them, and any later consolidation is a separate circuit.

### 4c. Failing-first probes the build circuit will run (enumerated)

- **P1 — Harvest reconcile:** table row/form counts reconcile exactly against the pinned source manifest (24 revids; expected 1,693 upstream rows at the Appendix A revisions, or a manifest-diff explaining any drift). A silent count mismatch fails the build.
- **P2 — License manifest completeness:** every `wikimedia_import` row carries `source_page` + `source_revid` + `license`; the table header carries the attribution block + BY-SA notice + change indication. One unlicensed or untraced imported row fails the build.
- **P3 — Collision log non-silent:** a planted collision (test form colliding with an Ace piece) must appear in the collision log with the Ace entry winning; total logged collisions must equal total detected collisions.
- **P4 — Customs win:** a test custom bound over an imported piece resolves to the custom in `root_of` — before and after the table loads.
- **P5 — UNRESOLVED honesty:** a word with no table coverage returns unresolved/None exactly as today — the table must never manufacture a parse (probe set includes known-uncovered words).
- **P6 — Position quarantine:** `dell`, `man`, `re` (and any piece under an unruled §2.6 conflict) ship with `conflict_status = position_unresolved` and are excluded from position-dependent consumption until ruled — a probe asserts none of them carries a guessed single position.
- **P7 — Regression:** `latinmandell.smoke()` 8/8 and `morpheme.smoke()` 6/6 still pass; hyphen-form parity (Com-man-dell and the 21 force-table words) byte-identical; the new suite is registered in `form/regress.py` LIST per harness law.
- **P8 — Spot battery:** the plan's acceptance battery — 100 known words resolve to their correct roots against the table (harvest-only fallback: battery re-scoped to actual coverage, with the re-scope printed on the receipt, per §3.5).

### 4d. PROPOSED CHANGE LIST (numbered; each item scoped)

1. **Publish the LM-0 confirmed census** (`LM0_CENSUS_CONFIRMED_2026-11-11.md`, sha256 `c37adb09…`) to `director-reports/` — records-only; closes GAP-1; gives LM-1 its canonical repo anchor.
2. **Build-time importer script** (new file, tooling only — never imported by runtime code): fetches the 24 letter pages at the pinned revisions, emits the table + source manifest + collision log; deterministic output (same pins → same bytes).
3. **The LM-1 table data file** (new; location/format per Q-LM1.8): the §4a schema, all strata, license header per §3.2.
4. **Collision log artifact** (new, published with the circuit record): every §3.4 collision with disposition; empty is a claim the probes must prove, not a default.
5. **Additive loader in `latinmandell.py`** (code, minimal): load the table when present, merge at lookup time under the §4b order (customs → seed → import); absent table = today's behavior. No existing function signature or output shape changes.
6. **New test module** `form/lm1_table_test.py` implementing P1–P8, registered in `form/regress.py` LIST with a `smoke()` entry point per harness law.
7. **Attribution/CREDITS record**: table header block + a `director-reports/` record naming the 24 source pages, their pinned revisions, the CC BY-SA 4.0 license and notice URL, and the change indication — satisfying §3.2's redistribution obligations at ship time.

**Explicitly EXCLUDED from this change list:** any change to a Dell's meaning, name, or number; the `dell`/`man`/`re` position rulings (they are §4e questions — the build ships them quarantined per P6, it does not settle them); any LM-2 splitter/runtime work; the LM-4 toll-booth wiring; any UX/Studio work; any change to `morpheme.py`'s or `latinmandell.py`'s existing dicts or semantics.

### 4e. QUESTIONS FOR THE DIRECTOR (numbered)

- **Q-LM1.1 — LICENSE GATE:** Does the import proceed under CC BY-SA 4.0 on the evidence in §3.2 — or does the gate fail and LM-1 ship the §3.5 harvest-only fallback?
- **Q-LM1.2 — Combined-table shape:** If the gate passes, is the combined table licensed by **segregation** (per-row provenance/license; imported stratum BY-SA, Ace strata under project terms — §4a as designed) or as **one CC BY-SA table** (copyleft extended over Ace's in-table glosses)?
- **Q-LM1.3 — `dell` position:** Which positions are lawful for *dell* — root, suffix, proposed prefix, or a ruled subset? (Highest-conflict piece; census §9.7.)
- **Q-LM1.4 — `man` position:** Are the three attested uses (morpheme.py prefix "hand/control/execution"; preform *Man-/Mandel-* "protocol/operator domain"; preform *-man* suffix) three pieces, one piece with frames, or a subset — and how does the ruling treat the *mand* root boundary?
- **Q-LM1.5 — `re` position:** Two positional entries (prefix / suffix), or one entry with two positional frames? (Current code silently prefers the prefix sense.)
- **Q-LM1.6 — Greek operator family:** Do *alpha/delta/omega* (and ontology-only *lambda/sigma*) enter the table as `operator` position_class, as prefixes, or as held candidates? This decides whether the schema's `operator` class is populated in LM-1.
- **Q-LM1.7 — GFDL election:** Build on the CC BY-SA grant alone (recommended §3.2.5), or is dual-license (GFDL) handling required for any DellMatrix distribution channel?
- **Q-LM1.8 — Table file:** Format and home for the table data file — a JSON data file under `form/mandell/` (loader-native), or another ruled location/format?
- **Q-LM1.9 — Preform candidates:** Do the 15 preform rows enter LM-1 as `preform_candidate` stratum (visible, unconfirmed), or are they held out entirely until a Leight/Loure admission circuit runs?
- **Q-LM1.10 — Examples column:** Import the upstream English-examples field in full, trimmed, or not at all? (It is the bulkiest and most expression-dense column; §3.2.4 applies.)

### 4f. Anticipated probes

- **"1,693 rows is not 1,693 pieces."** Correct and pre-answered: rows group allomorphs; the form count is ≈2,096 (±~2%, bold-markup method, Appendix A pins). The schema splits forms into rows-per-piece with the upstream row as trace unit.
- **"Upstream will drift between ruling and import."** By design: the importer pins revisions (§3.3); P1 fails on unexplained drift; a refresh is a reviewed manifest diff, never a silent overwrite.
- **"Meanings are facts — why is this a license question at all?"** §3.2.4: a wholesale lift takes selection, arrangement, and gloss wording (expression/compilation), not bare facts. The gate exists precisely so the project never has to argue this after the fact.
- **"Does the BY-SA file poison the MIT repo?"** No — licenses attach per work; the repo root MIT grant covers the code, the data file carries its own notice (§3.2.3). Q-LM1.2 decides the in-table shape.
- **"Why not just use Wiktionary / CLTK?"** §3.2: Wiktionary is the same license family and lemma-shaped (a complement, not a table); CLTK/Whitaker's are MIT *tooling*, not a roots table.
- **"Deepen() drops unresolved words silently — doesn't the table make that worse?"** The gap is real (§2.2) and is LM-2's to close; LM-1's obligation — met by `conflict_status` + full provenance in the schema — is to give LM-2 data honest enough to surface it.
- **"The census isn't in the repo — is this whole package anchored on a workspace file?"** Yes, today; that is GAP-1, and change-list item 1 closes it as the circuit's first act rather than papering over it.

---

## APPENDIX A — SOURCE MANIFEST (pre-import snapshot, fetched 2026-11-11)

Citation chain: hub `List of Greek and Latin roots in English` (pageid 3620462, rev **1378877227**, 2026-10-06) → range pages A–G (rev 1353827304, 2026-05-12), H–O (rev 1280989339, 2025-03-17), P–Z (rev 1296298036, 2025-06-19) → 24 letter pages:

| Letter | Revision | Date | | Letter | Revision | Date |
|---|---|---|---|---|---|---|
| A | 1377897064 | 2026-10-01 | | N | 1307355515 | 2025-08-23 |
| B | 1275596589 | 2025-02-13 | | O | 1277566959 | 2025-02-25 |
| C | 1360815995 | 2026-06-23 | | P | 1381251622 | 2026-10-21 |
| D | 1346448644 | 2026-03-31 | | Q | 1271579775 | 2025-01-24 |
| E | 1301146259 | 2025-07-18 | | R | 1181415582 | 2023-10-22 |
| F | 1222950818 | 2024-05-08 | | S | 1360399905 | 2026-06-21 |
| G | 1371511202 | 2026-08-26 | | T | 1381965170 | 2026-10-25 |
| H | 1347769344 | 2026-04-08 | | U | 1253371142 | 2024-10-25 |
| I | 1350925285 | 2026-04-24 | | V | 1320485430 | 2025-11-04 |
| J | 1369713942 | 2026-08-16 | | X | 1106460130 | 2022-08-24 |
| K | 1299697880 | 2025-07-09 | | Z | 1276421824 | 2025-02-18 |
| L | 1320808977 | 2025-11-06 | | | | |
| M | 1318218716 | 2025-10-22 | | | | |

Count method: one wikitable per letter page; data rows counted from wikitext row chunks after the header (`Root | Meaning in English | Origin language | Etymology (root origin) | English examples`); total **1,693 rows**; rendered-HTML spot checks (K, X) matched exactly. Root forms ≈2,096 by bold-form extraction from each row's Root cell (approximate). No W or Y letter pages exist.

**Gaps marked in this package:** GAP-1 — LM-0 census not in the GitHub repo (§1; fix = change-list item 1). GAP-2 — no in-repo approval artifact for the 2026-08 founding morpheme rows (§2.1). GAP-3 — upstream row anchors only partially available; trace design uses page-revision + row-ordinal + head-form (§3.1).

— END OF LM-1 PROPOSAL —
