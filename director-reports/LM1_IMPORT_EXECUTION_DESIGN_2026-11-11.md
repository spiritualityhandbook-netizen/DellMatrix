# LM-1 IMPORT — BOUNDED EXECUTION DESIGN (for final HOLD disposition)

Submitted by Uni (main session) per Director mail 1a1cd41952e441fa.
DESIGN ONLY — this document authorizes nothing and copies nothing. The
import runs only after a separate explicit Director code-circuit GO on
this design. Governing boundary: LM1_IMPORT_LICENSE_BOUNDARY_2026-11-11.md
(PR #391, conditionally acceptable as an engineering boundary). Ace's
policy permission is on record (PR #390, merged 49b81dd).

## 1. What the circuit builds (and nothing more)

- A build-time importer, `form/lm1_import.py` (same pattern as the
  merged harvester: build-time only, never imported by runtime code),
  which reads pinned Wikipedia wikitext and emits ONE new artifact:
  `form/mandell/lm_table_v2.json`. **lm_table_v1.json stays
  byte-untouched**; the loader learns to read v2 when present (v1
  remains the fallback), with the external rows in a new lowest
  stratum `external_wikipedia`.
- `CREDITS.md` at the repository root (Ace's instruction): contributor
  community, source work, hub revision, license URL.
- The attribution record `director-reports/LM1_IMPORT_ATTRIBUTION_*.md`
  + the manifest embedded in the v2 header (per-page revids, retrieval
  timestamps, per-page license check results, source byte hashes).
- `form/lm1_import_test.py`, registered in the regress LIST.

Expected volume: ~1,693 data rows from the 24 pinned letter pages
(hub revid 1378877227; per-page revids as tabled in the boundary §1).
Any material deviation from the pinned set aborts the build.

## 2. Gates inside the build (fail closed, in order)

1. **Revision pin check.** Fetched page revid must equal the manifest
   pin; mismatch → abort, no partial table.
2. **Per-page license check.** Each page's license is verified from the
   API/site terms at fetch time and recorded; a page not confirmed
   CC BY-SA 4.0 is EXCLUDED and the exclusion reported — never worked
   around. No GFDL election.
3. **No copied examples (Q-LM1.10).** The parser takes the roots
   table's own columns (root, origin/language, gloss) and structurally
   cannot emit the examples column; a test greps the artifact for
   example-column markers.
4. **Zero adapted rows or fail closed.** Rows carry content unchanged;
   the only transforms are the boundary's format normalizations, each
   written to a per-row changed-fields log with a trace to the pinned
   original. Any transform outside that list aborts the build for the
   whole run (not a per-row skip).
5. **Per-row provenance.** Every external row carries source_page,
   source_revid, license, changed_fields. A row missing any field
   fails the artifact validation.
6. **Collision quarantine + lowest precedence.** New collisions with
   in-repo pieces join the v2 collisions file as
   `position_unresolved`; lookups annotate ALL strata and never let
   the external stratum win silently (loader precedence:
   customs > ace_seed > inrepo > inrepo_force > candidate >
   external_wikipedia).

## 3. Lineage and export behavior (boundary §4, implemented)

- The loader's row objects expose their provenance; the composition
  layer (when LM-2/LM-3 wire it — NOT in this circuit) will record
  source lineage per output. THIS circuit ships the lineage DATA
  MODEL and its tests at the table level: every external row is
  lineage-complete by construction (gate 5), and an export helper
  classifies a row set as unchanged quote / derived adaptation /
  independent and REFUSES bulk export of any set containing a row
  with incomplete lineage.
- Preserved nuance (Director, mail 1a1cd41952e441fa): the default
  DERIVED ADAPTATION classification for uncertain lineage is a
  conservative notice, NOT permission to export; where lineage is
  incomplete, bulk export is refused outright. Actual derivative
  status remains case-specific; neither segregation nor an
  attribution header alone confines downstream obligations.

## 4. Test design (form/lm1_import_test.py)

- T1 provenance completeness: every external row has page+revid+
  license; manifest revids match the boundary table.
- T2 examples absent: no example-column content in the artifact.
- T3 zero adapted: adapted flag false on all imported rows;
  changed-fields entries use only the allowed normalization list.
- T4 precedence: a piece present in both in-repo and external strata
  resolves with the external row annotated lowest, never winning.
- T5 quarantine: known collision pieces (dell/man/re/alpha/delta/
  omega) remain position_unresolved; a synthetic new collision joins
  quarantine.
- T6 lineage/export: export of a complete-lineage set classifies and
  carries notices; export of a set with one provenance field stripped
  is REFUSED (incomplete-lineage refusal).
- T7 v1 integrity: lm_table_v1.json sha256 unchanged by the build.
- Mutants (inverse-edit revert, committed work first): M1 drop
  provenance writing → T1/T6 fail. M2 raise external precedence → T4
  fails. M3 allow an unlisted transform → T3 fails.

## 5. Circuit gates and receipts

Standard v1 conveyor: failing-first probes (the v2 loader path refuses
honestly before the build: absent v2 = v1 behavior, stated in tests) →
build → mutants → regress ×3 sequential from the main session → PR →
exact-head CI → Keeper SWAT/confirm → Director disposition → §32 merge
transaction → fresh-clone verification. The PR description carries the
full decision trail and the honest scope: a data import under license,
no LM-2/LM-3 wiring, no runtime behavior change beyond table lookup
coverage. No MWL credit is claimed by the design; any credit is the
authorities' call at closure.

## 6. What is NOT in this circuit

No splitter/composer changes (LM-3), no small-word table wiring
(LM-2 — which remains the next LM implementation circuit unless the
Director re-sequences), no Studio surface, no second table authority
(v2 supersedes v1 by the loader's single read path, v1 retained as
the fallback artifact).
