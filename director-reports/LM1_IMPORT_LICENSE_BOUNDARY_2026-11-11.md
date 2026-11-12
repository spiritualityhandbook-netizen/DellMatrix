# LM-1 IMPORT — CONCRETE ATTRIBUTION / LICENSE / DISTRIBUTION BOUNDARY

Submitted by Uni (main session) for Director ruling, per Director mail
1a1cd2c1abd8f162 and execution mail 1a1cd35269a51910. Records-only review
packet. Nothing in this document imports rows, touches product code, or
lifts the IMPORT EXECUTION HOLD; the HOLD lifts only by Director ruling on
this boundary. Ace's policy permission (PR #390 record, as amended) is
accepted by both authorities; this page defines HOW the copying may be
done compliantly, for the Director to rule on.

## 1. Source and provenance (verified from live API responses)

Source work: "List of Greek and Latin roots in English", English Wikipedia.
License: Creative Commons Attribution-ShareAlike 4.0 International —
https://creativecommons.org/licenses/by-sa/4.0/ (deed) and
https://creativecommons.org/licenses/by-sa/4.0/legalcode (legal code).
Author for attribution purposes: the Wikipedia contributor community of
the listed pages (no individual creator exists or is implied).

Pinned revisions, retrieved 2026-11-11 via the MediaWiki API
(prop=revisions, wikitext). Hub page: "List of Greek and Latin roots in
English", pageid 3620462, revid **1378877227**. Letter pages (24):

| Page | Revid |
|---|---|
| /A | 1377897064 |
| /B | 1275596589 |
| /C | 1360815995 |
| /D | 1346448644 |
| /E | 1301146259 |
| /F | 1222950818 |
| /G | 1371511202 |
| /H | 1347769344 |
| /I | 1350925285 |
| /J | 1369713942 |
| /K | 1299697880 |
| /L | 1320808977 |
| /M | 1318218716 |
| /N | 1307355515 |
| /O | 1277566959 |
| /P | 1381251622 |
| /Q | 1271579775 |
| /R | 1181415582 |
| /S | 1360399905 |
| /T | 1381965170 |
| /U | 1253371142 |
| /V | 1320485430 |
| /X | 1106460130 |
| /Z | 1276421824 |

No standalone /W or /Y pages exist (API returns them "missing"); those
letters' rows live inside the combined-range pages. Boundary condition:
the build imports ONLY from pages whose revid is pinned in its source
manifest; before copying, the build re-verifies each page's license via
the site terms/API at fetch time and records it in the manifest — no
presumption that every linked source is covered identically. If a page's
license at fetch time is not CC BY-SA 4.0, that page is excluded and the
exclusion is reported, not worked around. GFDL: no GFDL election
(Q-LM1.7 stands); Wikipedia text is used under CC BY-SA only.

## 2. Attribution — where it lives, so it travels with the material

Attribution is supplied in a reasonable manner in FOUR places, so no
distribution of the rows can plausibly lose it:

1. **Program credits (Ace's instruction):** a `CREDITS.md` at the
   repository root naming the contributor community, the source work,
   the pinned hub revision, and the license URL.
2. **Attribution record:** `director-reports/LM1_IMPORT_ATTRIBUTION_*.md`
   plus a machine-readable attribution block embedded in the table
   artifact's header, next to the source manifest (per-page revids,
   retrieval date, license URL).
3. **Per-row provenance:** every external row carries source_page,
   source_revid, and license fields in the table itself; a row exported
   without its provenance fields is a defect, tested for.
4. **Change indication:** the manifest records the changes made to the
   source material (see §3): mechanical normalization only, example
   columns dropped (Q-LM1.10), fields mapped to the stratum schema.

## 3. The collection-versus-adaptation decision

- **Imported rows are a COLLECTION/AGGREGATION.** Row content (root form,
  origin/language, meaning gloss as published in the table's own columns)
  is carried UNCHANGED. Format normalization (Director Q-B1, conditionally
  accepted) covers ONLY changes without expressive semantic effect:
  whitespace cleanup, HTML/wikitext markup stripping, field mapping into
  the stratum schema, dropping the example columns per Q-LM1.10. Every
  normalized row keeps a changed-fields log and a trace back to the
  pinned original text. Gloss or punctuation alterations are NOT
  presumed non-adaptations; any substantive rewriting is reviewed
  case-by-case and, if it changes expressive content, produces an
  ADAPTED row under the next bullet instead.
- **ADAPTED rows are a separate, flagged class.** Any transformation
  beyond mechanical normalization (re-glossing, merging or splitting
  senses, translating glosses, reclassifying a piece's position) produces
  an ADAPTED row, marked `adapted: true` in its provenance with the
  transformation named. The import build creates ZERO adapted rows.
  Adapted rows, if a later circuit ever creates them, are licensed
  CC BY-SA 4.0 when distributed, and that circuit needs its own ruling.
- The external stratum sits inside a larger table beside in-repo strata
  (segregated, lowest precedence: customs > ace_seed > inrepo >
  inrepo_force > candidate > external_wikipedia). Segregation is an
  engineering safeguard enabling traceability; per the amended ruling
  record, it is NOT claimed to legally confine ShareAlike consequences —
  distribution follows §4 regardless of internal layout.

## 4. Distribution — exports, APIs, derivative datasets, releases

Any distribution surface that carries external rows carries the license
with them:

- **Exports / files:** the attribution record (§2.2) accompanies any
  exported table or dataset containing external rows; the license URL
  and the contributor-community credit are in the export's header or a
  NOTICE file beside it.
- **API responses / program outputs:** a response that returns external
  rows returns their provenance fields with them (§2.3); bulk endpoints
  additionally return the license URL. (Single-gloss lookups by a user
  carry the row's own provenance; no separate ceremony is invented.)
- **Source lineage (Director Q-B2, correction applied):** every output
  composed or derived at runtime (LM-2/LM-3 senses, stacks, parses)
  records its SOURCE LINEAGE — the set of rows that materially
  contributed to it (stratum, piece, and for external rows the source
  page + revid). Lineage is part of the output's own record, not a
  side note; an output whose lineage cannot be established is
  INCOMPLETE and may not be bulk-exported until it is.
- **Output classification:** each distributed output is classified by
  its lineage: (a) UNCHANGED QUOTE — verbatim row content; the row
  rules above apply. (b) DERIVED ADAPTATION — output whose expressive
  content derives from one or more external rows (including a sense
  composed by stacking external glosses, in whole or in part);
  distributed under CC BY-SA 4.0 with attribution and source
  availability, exactly as an adapted row. Being generated by software
  does NOT remove an output from this class. (c) INDEPENDENT — output
  with no external-row lineage; no obligation from this source arises
  (other sources' terms may still apply). FAIL-CLOSED DEFAULT: when
  classification is uncertain — lineage incomplete, contribution
  ambiguous — the output is treated as a DERIVED ADAPTATION, and a
  release or derived output may still require case-specific assessment;
  segregation remains traceability, never an automatic legal shield.
- **API responses / exports of composed outputs:** a response or export
  carrying composed outputs includes each output's classification and,
  for classes (a) and (b), its lineage summary and the CC BY-SA notice.
- **Generated derivative datasets:** a dataset built substantially from
  external rows — or from DERIVED ADAPTATION outputs — is distributed
  under CC BY-SA 4.0, with the attribution record included and the
  corresponding source (the stratum artifact + manifest + this
  boundary) available with it or by a working link in the dataset's
  notice.
- **Bundled releases:** any release bundle containing the table includes
  CREDITS.md and the attribution record; the external stratum's
  ShareAlike notice appears in the bundle's license notices.
- **ShareAlike source availability:** where ShareAlike applies to a
  distributed adaptation (none are created by the import; see §3), the
  corresponding source form accompanies the distribution or is reachable
  via the notice's link, and the adaptation is itself offered under
  CC BY-SA 4.0.

## 5. Standing constraints carried into the build

- Position collisions (dell/man/re/alpha/delta/omega and any new
  collisions the external rows create) remain QUARANTINED
  (`position_unresolved`); the external stratum never overrides in-repo
  strata and never silently first-matches.
- Q-LM1.10 stands: no bulk English example text imported; upstream
  references are preserved as references, not copied expression.
- The Keeper's earlier absolute-segregation assertion is not adopted as
  a legal conclusion (Director, mail 1a1cd35269a51910); this boundary
  deliberately does not rely on it.
- This boundary is an engineering compliance design for Director ruling,
  not legal advice and not a legal certification.

## 6. Questions for the Director

- Q-B1: Does the Director accept mechanical normalization (§3) as
  non-adaptation, with the manifest's change indication as sufficient
  notice? Uni position: yes — format only, content unchanged.
- Q-B2: CORRECTED per Director ruling (mail 1a1cd3c03a107d9e). Uni's
  original position — that a program-composed sense is categorically
  outside CC BY-SA — is WITHDRAWN. The corrected rule is §4's lineage
  system: source lineage flows into every composed output; outputs are
  classified unchanged quote / derived adaptation / independent by
  lineage; derived adaptations distribute under CC BY-SA 4.0; uncertain
  classification fails closed to derived adaptation. Amended text
  submitted for final Director disposition.
- Q-B3: Confirm no-GFDL-election (Q-LM1.7) carries into the import
  unchanged.

Ruling requested: approve this boundary (with any corrections), which
lifts the IMPORT EXECUTION HOLD for one bounded import circuit under the
standard gates; LM-2 harvested-only remains the next implementation
circuit unless the Director re-sequences.
