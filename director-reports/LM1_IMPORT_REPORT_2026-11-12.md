# LM-1 BOUNDED EXTERNAL IMPORT — CIRCUIT REPORT — 2026-11-12

Circuit: LM-1 external import. Source: Wikipedia "List of Greek and
Latin roots in English" (CC BY-SA 4.0), hub revision 1378877227,
24 letter pages each pinned by revision id. Build PR #393, MERGED
2026-11-12T06:07:58Z as c6f6fb57bb34f0a5bc8b3571e3fb22a7490f1e2d
(candidate head c7bdc8a2e95df0bc9def66c96f7849c39800b901).

## BEFORE → AFTER (capability)

BEFORE: the morpheme table on main was the in-repo harvest only —
158 rows in lm_table_v1.json (PR #389), no external stratum. Pieces
outside the harvest (e.g. `cred`) resolved to nothing.

AFTER: form/mandell/lm_table_v2.json carries the 158 v1 rows
VERBATIM plus an `external_wikipedia` stratum of 2,087 piece rows
at the LOWEST precedence (customs > ace_seed > inrepo >
inrepo_force > inrepo_legacy > candidate > external_wikipedia).
form/mandell/lm_table.py remains the single read path (v2
preferred, v1 fallback, external never wins). On merged main,
lookup('cred') returns the external row through that one path.
This is a data-availability capability only: no runtime consumer
(LM-2 split composition, translator wiring) is activated by this
circuit.

## AUTHORIZATION CHAIN

1. LM-1 proposal, PR #386 MERGED as ded0ead (records only).
2. Ace license unlock, 2026-11-11 18:27 CST: the external table
   import is APPROVED with attribution. Terms: CC BY-SA 4.0 —
   attribution AND ShareAlike. Creator credited = the Wikipedia
   contributor community (CREDITS.md; attribution record
   director-reports/LM1_IMPORT_ATTRIBUTION_2026-11-11.md).
3. Boundary, PR #391 MERGED as 610fb13: pinned revids for the hub
   and all 24 letter pages (/W and /Y confirmed nonexistent
   standalone); import = collection, ZERO adapted rows;
   segregation = traceability ONLY. Director rulings folded:
   Q-B1 (format normalization = non-expressive changes only);
   Q-B2 as corrected (SOURCE LINEAGE flows into every composed
   output; outputs are unchanged-quote / derived-adaptation /
   independent; derived adaptations under CC BY-SA; FAIL-CLOSED
   default; incomplete lineage may NOT be bulk-exported);
   Q-B3 (no-GFDL accepted). Keeper precise stamp naming the head
   (comment 6813264539).
4. Execution design, PR #392 MERGED as 4e556c4 (corrected head
   38e7dd7): five Director corrections incl. positive/structural
   Q-LM1.10 enforcement, strict cardinality ledger, partial-
   coverage honesty, build-time-only export helper, v1
   byte-identical + one loader path.
5. Import GO: Director mail 1a1cd7d53c3ec395 (conditions
   fulfilled 2026-11-11 21:17 CST).
6. Build, PR #393 (branch uni/lm1-import-1111), then two
   correction rounds (below).
7. FINAL scoped PASS + conditional Uni merge authorization:
   Director mail 1a1ce3d4cd722401, REAFFIRMED in Director mail
   1a1ce5a1885841eb (read in full by the main session). §32
   freshness triage ran in the merge step; merged
   2026-11-12T06:07:58Z.

## LEDGER (final, unchanged through both corrections)

- Source rows: 1,693 = parsed 1,684 + invalid 9 (1 cross-reference
  stub + 8 empty-Meaning source rows) + license-excluded 0.
- External piece rows imported: 2,087.
- v2 total: 2,245 rows (158 v1 verbatim + external stratum).
- Coverage: COMPLETE. All 25 revids matched their pins.
- v1 table sha256 59c63a40f8d274254a7589b9a2e6ef49dba712eb880ca5
  ac144b005bb8da8849 — identical before and after every step.

## MECHANISM

- form/lm1_import.py — build-time ONLY importer; 9 fail-closed
  gates. Not imported by any runtime path.
- Pair publication: the importer builds and validates fully in
  memory, stages fsynced temp files, re-checks the v1 hash BEFORE
  publish, retains `.prev` copies, and publishes collisions
  first, the table LAST as the single commit point. The v2 table
  header's `pair` block binds the collisions bytes and the
  canonical rows bytes to one content-derived `generation` id.
- Loader: form/mandell/lm_table.py reads each artifact's bytes
  EXACTLY ONCE per load (`_load_snapshot()`), verifies the pair
  binding against those bytes, and returns parses from the same
  bytes. A mismatched pair raises PairInconsistentError — the
  loader never serves a mixed pair and never silently downgrades
  to v1. Absence of the v2 artifacts keeps the legacy empty
  contract.
- Disclosure: rightsinfo substantiation is site-level license
  basis; all 25 pinned pages' wikitext was sha-verified and
  scanned — no license-exception marker found. No legal certainty
  is claimed beyond that.

## CORRECTION ROUNDS

CORRECTION 1 — two-file atomicity (Director mail
1a1cdca2f4dd89fe, CORRECTION_REQUIRED / MERGE HOLD): the original
build wrote the pair via two separate atomic replaces (the pair
itself not atomic) and re-checked the v1 hash only AFTER publish.
Repaired at head 24d0ba8 per the mechanism above. BEFORE probes
P1–P3 were behavioral (crash between replaces served a mixed
pair silently; mid-build v1 mutation detected only post-publish;
tampered collisions served as-is). Disclosed deviation: literal
previous-generation service at the canonical paths is impossible
with in-place replacement; the contract is met via the Director's
accepted alternative (fail-closed + tested recovery + `.prev`
copies + git history). The generation-directory layout question
remains open — see Q-LM1-IMP.2.

CORRECTION 2 — pair-read race (Director mail
1a1cdee092fdf580, HOLD REMAINS): load_collisions() verified via
load_table() and then opened the collisions file a SECOND time —
a TOCTOU window in which a concurrent replace could return an
unverified generation. Repaired at head c7bdc8a by the
single-snapshot loader (above). Failing-first T-F battery
(deterministic open-counting hook injecting generation-whole
replaces at exact open points): pre-fix 53/55 with T-F1 + T-F2
RED; post-fix 55/55. The Director's scoped review (mail
1a1ce02eabdcaffc) ACCEPTED the repair as addressing the flaw in
scope, as a recovery/fail-closed protocol — NOT atomic pair
publication. This report uses the same wording.

Documented, NOT fixed: the importer re-checks the v1 hash before
publish without holding any lock, so a concurrent writer to the
v1 file inside that narrow window is a documented residual risk
— see Q-LM1-IMP.3.

## EVIDENCE

- Import suite form/lm1_import_test.py: 55/55 at the merged head
  (T1–T10 plus T-A injected failure between replaces, T-B
  subprocess SIGKILL mid-publish, T-C v1 mutation aborts
  publishing nothing, T-D hand-corruptions, T-E re-run converges
  in/cross-process, T-F pair-read race battery).
- Mutants killed: M-A, M-B (correction 1); M-C (second read
  restored → T-F RED), M-D (verification dropped → 48/55).
- Terminal regression campaign at head c7bdc8a (main session,
  SIG-reset runner): fwd REGRESS FINAL GREEN 275/275 EXIT 0;
  --twice pass 1 + pass 2, 275/275 GREEN EXIT 0; --order rev
  GREEN EXIT 0. Packet: PR #393 comment 6815407485.
- Disclosed aborted campaigns (NO RESULT, partial logs): the
  94fc39d campaign killed on HOLD 1 (~21:32 CST); the 24d0ba8
  campaign killed on HOLD 2 (~22:05 CST).
- Exact-head CI at c7bdc8a, terminal SUCCESS: package run
  43153970333, smoke run 43153970352, browser-acceptance run
  43153970344. Local merge-tree trial vs main 8c6937b: exit 0,
  zero conflict markers.
- Keeper scoped CONFIRM naming c7bdc8a: comment 6815181136
  (2026-11-11 23:05 CST).
- Merged-main verification (fresh clone at c6f6fb5, main
  session): lm1_import_test 55/55; lm1_harvest_test 22/22;
  lm_table smoke 4/4; lookup('cred') returns the
  external_wikipedia row through the single loader path; full
  forward regression on merged main GREEN EXIT 0.

## TRANSPARENCY — THE FLAGGED READ

The main session's first full-body read of Director mail
1a1ce3d4cd722401 was flagged by the runtime safety layer, which
directed that its contents not be acted on. Uni complied: no
merge was executed on that read, no state was advanced on it,
and the stop was surfaced to Ace in the main chat. The merge
proceeded only after the Director's reaffirmation arrived in
mail 1a1ce5a1885841eb (read in full by the main session, no
flag) AND every gate was independently verified through gh and
local terminal evidence (head, CI, Keeper stamp, campaign). The
episode is disclosed on PR #393: merge-gate receipt comment
6816147703; identifier correction comment 6816184304 (a prose
typo in two Uni comments printed the head as …def99c96f…; the
actual head, taken programmatically from gh for the merge
itself, is …def66c96f…; no evidence was affected).

## SCOPE BOUNDARIES — WHAT THIS DOES NOT ESTABLISH

- NOT atomic pair publication. The contract is fail-closed
  recovery with a single commit point and verified reads.
- NOT general concurrency safety (the documented v1
  concurrent-writer window stands, unfixed).
- NOT runtime activation: no LM-2/LM-3 composition, no
  translator wiring. LM-2 split composition is PR #395,
  currently in its own A9 correction round.
- NOT a license or legal certification of any downstream use;
  Q-B2 lineage rules govern composed outputs separately.
- NO Master Work List credit is claimed by Uni for this
  circuit. Whether the import earns credit is the authorities'
  call — Q-LM1-IMP.1.

## Questions for the Director

- Q-LM1-IMP.1: Does the LM-1 import circuit earn Master Work
  List credit, and if so, against which item(s)?
- Q-LM1-IMP.2: Is a generation-directory layout for pair
  publication still required, or is the fail-closed + `.prev` +
  git-history protocol the standing answer for this artifact
  class?
- Q-LM1-IMP.3: The documented pre-publish v1-check
  concurrent-writer window (no lock held): accept as documented
  risk for a build-time-only tool, or schedule a lock?

## Anticipated probes

- "Is the pair published atomically?" No. Publication is
  staged, fsynced, single-commit-point (table last) with `.prev`
  retention; reads are single-snapshot and pair-verified, so a
  reader sees one consistent generation or PairInconsistentError
  — never a silent mix, never a silent v1 fallback. Atomicity
  was not claimed in the ruling and is not claimed here.
- "Can the external stratum shadow harvested rows?" No. It sits
  at the lowest precedence in the single loader path; the 158
  v1 rows are byte-identical in v2 (sha-verified), and lookup
  returns full row sets with stratum + precedence rank visible.
- "What happens if the v2 pair is corrupted on disk?" The loader
  raises PairInconsistentError (T-D/T-F evidence, incl.
  single-character corruption of either member). It does not
  serve v1 instead.
- "Did the corrections change the imported data?" No. All four
  artifact hashes were unchanged by correction 2, and the ledger
  (1,693 = 1,684 + 9 + 0; 2,087 piece rows; 2,245 total) is
  identical at every head from the original build to the merge.

## Ace's move

Nothing needed from Ace. Next step owner: the authorities —
review of this records PR through the normal passes; LM-2
(PR #395) continues in its A9 correction round under Uni.
