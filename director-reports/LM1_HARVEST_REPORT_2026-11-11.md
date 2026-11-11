# LM-1 HARVEST-ONLY BUILD — CIRCUIT REPORT

**Date:** 2026-11-11 · **Builder:** Uni (subagent lane; merge remains a
main-session act) · **Branch:** `uni/lm1-harvest-1111`
**Status:** CANDIDATE — built under authorization; **NOT
merge-authorized** (see §1). Full regression campaign (fwd/twice/rev),
exact-head CI, and authority review are pending; the Uni main session
runs the campaign next.

---

## 1. AUTHORIZATION

Director mail **1a1cc55119b5979f** (2026-11-11 14:37 CST) authorized
ONE bounded, IN-REPO HARVEST-ONLY LM-1 build under these terms, all
honored: no Wikimedia text import (Q-LM1.1 — wholesale external import
NOT authorized; a separate license decision is required); contingent
on byte-hash-verifying the Ace-confirmed LM-0 census and publishing
that exact original to director-reports first; source-specific
provenance; collision log; explicit `position_unresolved`; non-silent
unknowns; no new semantics or external imports; no changes to existing
public API; precedence customs > Ace seed > candidate; probes
P1/P3–P7 adapted to the harvested sources; P8 reported as honest
actual coverage. That mail is build authorization only — **it is not
merge authorization for this implementation**, and this report does
not call LM-1 implemented or certified.

Proposal of record: `director-reports/LM1_PROPOSAL_2026-11-11.md`
(§4a schema, §4c probes, §4d change list, adapted to the harvest-only
subset per the rulings). Plan: LM-1 — THE TABLE (plan §15).

## 2. CENSUS GATE — VERIFIED BEFORE BUILDING

`hidden_files/lm0/LM0_CENSUS_CONFIRMED_2026-11-11.md`:
sha256 = `c37adb098db942209b18e05ae9d9736fbee3b563532873f016a3474293da85c0`,
107,078 bytes — **exact match** to the required value. The verified
bytes were copied to `director-reports/LM0_CENSUS_CONFIRMED_2026-11-11.md`
and re-verified after copy (sha256 identical; `cmp` byte-exact). This
closes proposal **GAP-1**: the confirmed census now has a canonical
repo anchor. The harvester itself refuses to build if the published
census anchor hash differs (asserted in `build()`).

## 3. WHAT WAS BUILT

| Change-list item (proposal §4d, harvest-adapted) | Delivered |
|---|---|
| 1. Publish the LM-0 confirmed census | `director-reports/LM0_CENSUS_CONFIRMED_2026-11-11.md` (byte-exact, §2) |
| 2. Importer tooling | `form/lm1_harvest.py` — build-time only, never imported by runtime code; harvests in-repo sources only; deterministic (re-run produces byte-identical artifacts, verified) |
| 3. Table data file | `form/mandell/lm_table_v1.json` (Q-LM1.8: machine-readable versioned JSON; sha256 `59c63a40…`) |
| 4. Collision log | `form/mandell/lm_table_v1.collisions.json` (sha256 `d853ed42…`), summarized in §5 |
| 5. Additive loader | `form/mandell/lm_table.py` — read-only loader (NOT wired into latinmandell.py, translate.py, the executor, or the REPL; wiring is LM-4) |
| 6. Test module | `form/lm1_harvest_test.py`, registered in `form/regress.py` LIST per harness law |
| 7. Attribution record | Not applicable to the harvest subset: no external work was imported, so no CC BY-SA obligation arises; the table header carries the full in-repo source manifest instead (§4) |

**Deviations from the proposal's change list, disclosed:** item 5 in
the proposal was "additive loader in latinmandell.py"; the Director's
build terms ("no changes to existing public API") govern, so the
loader ships as a **separate new module** and latinmandell.py is
byte-untouched. Item 2's importer fetches nothing — it reads only
files already in the repo.

## 4. THE TABLE — SCHEMA, MANIFEST, COVERAGE (P8)

Schema per proposal §4a, bounded to LM-2 consumption: one row per
piece with `piece`, `position_class`, `authored_position_class`
(preserved wherever quarantine overrides the effective class),
`language`, `sense`, `dell_ref` (nullable), `la` (nullable), `split`
(force-table rows), `stratum`, `provenance {source_file,
source_symbol}`, `conflict_status`, `notes`. **No bulk English
examples** (Q-LM1.10): senses are the in-repo authored glosses only.

The source manifest lives **inside the table header** — one artifact,
one hash; a sibling manifest file could drift from the table it
describes, an embedded one cannot. It pins every source file by
sha256 plus the census anchor (path + sha256).

**Harvested coverage (actual, P8-honest): 158 rows in 5 strata —**

| Stratum | Rows | Source |
|---|---|---|
| `ace_seed` | 53 | latinmandell.py `ROOTS` (surface word → Latin root + sense + Dell) |
| `inrepo` | 54 | morpheme.py typed PREFIXES 24 / ROOTS 19 / SUFFIXES 11 |
| `inrepo_force` | 21 | morpheme.py `force_mandell_morphemes` split table (splits, not senses) |
| `inrepo_legacy` | 14 | mandel_ontology.js `MORPHEMES` — legacy layer, labeled non-runtime |
| `candidate` | 16 | preform affix lexicon: 15 authored entries → 16 piece rows (the combined cell "Man- / Mandel-" yields two pieces); CANDIDATES ONLY (Q-LM1.9), gated by Leight/Loure |

**The 1,693-row external table was NOT imported.** Against the plan's
original LM-1 ambition (~1,693 roots), this harvest covers the
in-repo material only: ~110 sense-bearing pieces plus splits and
candidates. The plan's 100-word spot battery (proposal P2/P8 import
form) is therefore **not claimed** — it is re-scoped to this actual
coverage, and LM-2's splitter will emit correspondingly more honest
UNRESOLVED output until a license decision opens the import. That is
the fallback the proposal §3.5 designed: smaller, not broken.

Not harvested, by design: morpheme.py's 5 flat-dict whole-form extras
(mandel / mandell / nurture / commandell / omnifacure) — every one of
those pieces is already present as an `inrepo_force` row, so no piece
is lost; only their flat-dict senses are not separate rows.

## 5. COLLISIONS AND QUARANTINE

**17 collision pieces** (same normalized piece, differing position or
sense across/within strata), all in the shipped collision log with
per-row strata, authored positions, senses, and the precedence
outcome (no runtime change; customs outrank all shipped strata;
unresolved pieces excluded from position-dependent consumption):

alpha, com, de, dell, delta, fac, log, man, mandel, mirror, mit,
omega, pre, pulse, re, spec, trans.

**Quarantine (Q-LM1.3–Q-LM1.6, unruled):** 16 rows across 6 pieces
ship `position_unresolved` with authored positions preserved —
dell (4 rows: root + suffix in morpheme.py, prefix + suffix
candidates in preform), man (3), re (3), alpha / delta / omega
(2 each: morpheme prefix vs ontology operator — a role conflict).
No position was guessed, and **no existing first-match behavior
changed anywhere** (morpheme.py / latinmandell.py are byte-untouched;
P7 pins the baseline `sense_of("re")` and deepen behavior).

New collision facts the harvest surfaced (for the ruling record):
`pulse` collides ace_seed whole-form vs morpheme root; `mirror`
collides ace_seed vs the preform candidate prefix; `mandel` collides
force-table whole-form vs the preform candidate prefix; `trans`
carries three rows (morpheme + ontology + preform candidate, senses
differing: "across · transformative" / "across / changing form" /
"Across / change").

## 6. EVIDENCE

- **Failing-first:** the suite was written and registered before any
  build artifact existed; first run failed with ImportError
  (`lm_table` absent), exit 1 — log retained in the circuit record.
  Two probe defects were found on first green run and fixed with the
  disposition recorded: the preform recount now counts authored rows
  (16), not unique spellings (14); the P3 external-source check now
  scans provenance/manifest/strata (the header prose naming the held
  table to record its HOLD is documentation, not a source).
- **Focused suite:** `form/lm1_harvest_test.py` — **22/22 PASS**
  (P1 counts reconcile against independent in-test recounts of every
  source; P3 provenance + manifest sha256 pins + no external source;
  P4 collision log set-equals an independent recount; P5 full row
  sets with precedence ranks, customs documented first; P6 quarantine
  on every quarantined row; P7 absent-table emptiness + pre-build
  behavior baselines; P8 coverage stated in-header).
- **Baselines intact:** morpheme smoke 6/6, latinmandell smoke 8/8,
  loader smoke 4/4 — all inside/after the build.
- **Mutants (both caught, both reverted by inverse edit only):**
  M1 — harvester drops `source_symbol` for the legacy stratum →
  P3 FAIL; reverted, regenerated, 0 FAIL. M2 — loader `lookup()`
  silently first-matches → P5 FAIL ×2; reverted; post-revert diff
  clean, suite 22/22.
- **Determinism:** harvester re-run produces byte-identical table +
  collision log (sha256 compared before/after).
- **Not run by this lane (by instruction):** the full regression
  campaign (fwd / --twice / --order rev) — a main-session act, run
  next against this candidate's exact head, followed by exact-head
  CI on the PR.

## 7. LIMITATIONS

No external import (license decision outstanding — Q-LM1.1/Q-LM1.2/
Q-LM1.7 remain the Director's). No LM-2 wiring: nothing consumes the
table at runtime yet; the loader is a door, not a road. Positions for
dell/man/re and the Greek operator family remain quarantined pending
Q-LM1.3–Q-LM1.6. Lambda/sigma ship as authored `operator` rows from
the legacy ontology only (single-source, no conflict) — the family
ruling (Q-LM1.6) may still reclassify them. Preform candidates are
unconfirmed by construction. Original strict 19/72 and headline
36/179 are unchanged by this build; no MWL credit is claimed here.

## 8. QUESTIONS FOR THE DIRECTOR

None new. The open Q-LM1.1–Q-LM1.10 stand as ruled/open in mail
1a1cc55119b5979f; this candidate awaits: campaign evidence →
Keeper scoped position → Director merge ruling under §32.

— Uni Ω, 2026-11-11
