# LM-2 THE SPLITTER — CIRCUIT REPORT — 2026-11-12

Circuit: LM-2 THE SPLITTER (LatinMandell plan §15). Build PR #395,
MERGED 2026-11-12 as c414e710ea63d5c799d1b66d2b92a7d051507f18
(candidate head 4d0de79cca6925771fd3a4563d6b42341eb48a9a).

## BEFORE → AFTER (capability)

BEFORE: form/mandell/morpheme.py could look pieces up, but no
function could split an arbitrary English word into morpheme
pieces against the LM tables. Composition had no split evidence
to stand on: `root_of('transportation')` returned only a suffix
hint with the root sense lost, and there was no receipt stating
how much of a word was actually accounted for by table material.

AFTER: `split_word(word)` in form/mandell/morpheme.py splits a
word into pieces with receipts, in a fixed order of authority:
(1) census-whole — a word present whole in the LM-0 census
artifact (form/mandell/lm0_census_v1.json, 488 rows / 441 unique,
built by form/lm2_census_build.py, pinning the census source
sha256 c37adb09…); (2) a table-recorded split; (3) a guarded
greedy longest-match over table pieces. Each piece carries the
FULL `lookup()` row set with stratum + precedence_rank — no
second selector. Every split returns two honesty receipts:
`accounted` (fraction of the word covered by pieces) and
`morpheme_resolved` (fraction covered by pieces whose governing
rows are position-resolved). On merged main, `biology` splits
to [bio, logy] with accounted 1.0 through the real v2 pair
(LM-1 import), and `incredible` reports its middle honestly
UNRESOLVED — substring visibility is not composition material.
split_word is a lens function: it is not wired into the
executor or the translator (LM-4's circuit, not this one).

## AUTHORITY TRAIL

1. Director HOLD + proof list, mail 1a1ce1ed1a8c42c5, items
   (a)–(f). Proof circuit at bc3fd3b (suite 48/48; PR comment
   6815382123): census independently recounted 488/488 as a
   multiset; the v1 pin REBUILT byte-identical, not hand-edited;
   ambiguity and punctuation behavior pinned as-is; the cache
   stated plainly as PER-PROCESS; legacy parity byte-identical
   dumps, base vs branch. The proof circuit surfaced FINDING A9
   (below).
2. CORRECTION 1 — Director mail 1a1ce5a1885841eb: CORRECTION
   REQUIRED / MERGE HOLD on A9. Repaired at af139d1.
3. CORRECTION 2 — Director mail 1a1ce8ae4b5c8fe3 (2026-11-12
   00:55 CST): an independent Director code finding on
   quarantine eligibility, FIX-FIRST. Repaired at 4d0de79.
4. Director CONDITIONAL SCOPED PASS, mail 1a1ceddc6e1f5001
   (2026-11-12 02:26 CST): PASS on the implementation and both
   repairs at exact head 4d0de79; merge authorized once a Keeper
   confirmation expressly naming 4d0de79 landed (acknowledging
   the S17 quarantine repair + campaign evidence), then §32
   freshness + unchanged head/base + terminal checks in the
   merge step. A Keeper pre-stamp (comment 6820601355) named
   the head but left the campaign outstanding; Uni published
   the discharge packet (comment 6822094118).
5. Keeper FINAL STAMP, comment 6823425709, expressly naming
   4d0de79. §32 merge transaction executed in the merge step
   (freshness triage in-step; head/base unchanged; CI terminal);
   merge-gate receipt comment 6823500967. MERGED as c414e71.

## CORRECTION ROUNDS

CORRECTION 1 — FINDING A9, census section inheritance: 101 of
488 census rows (ASK 34, CONDITION 34, OPERATOR 27, FOCUS 6)
carried a `section` label inherited from the preceding category
— the census builder never reset `section` at category
boundaries, so the artifact claimed provenance it did not have.
Repair (af139d1; PR comment 6816536441): the builder resets
section at boundaries; an absent marker is `null`. The
regenerated artifact's field diff against the old is EXACTLY
101 rows, all `section` → null; the (word, category, meaning)
multiset is identical; the source pin is unchanged.
Failing-first S15 RED → GREEN; an independent span-first parser
reproduces the artifact 488/488; mutant killed. The branch was
rebased onto merged main c6f6fb5 (one regress LIST conflict
hand-resolved; LIST = 276, import-verified). REAL-v2
composition battery S16 added: biology → [bio, logy] accounted
1.0; `cred` resolves via the external stratum; a corrupted v2
pair raises PairInconsistentError out of split_word. Gold
expectations re-derived against v2, with the v1 derivations
pinned in `_V1_DELTA`; the lm1_import_test T7 pin updated (one
line; trail in the PR comment).

CORRECTION 2 — quarantine eligibility: the LM-1 harvest
quarantined rows whose position is unresolved
(`position_unresolved`); such rows keep their senses visible in
lookup() but must never drive positional decisions. The
Director found that `_lm2_loads()`, `_lm2_known_middle()` and
`_lm2_slot_kind()` let `authored_position_class` drive position
for exactly those rows — the quarantine leaked. Failing-first
with REAL rows (S17, RED 60/66): `struct` (external stratum,
position_unresolved, authored prefix) drove `structure` →
[struct(prefix), ure(root)]; `fa` drove the known-middle of
"defa"; `prim` was consumed in "primeval"; the piece inventory
leaked prefixes {struct, prim, fa, cor} and suffixes {cry, re,
dell}. Repair (4d0de79; PR comment 6817364353): ONE predicate,
`_lm2_position_eligible(row)` — a row is position-eligible only
when its OWN position_class is resolved — reused by all four
consumers. Quarantined rows keep their full senses and
annotations in lookup(); recorded splits are untouched. After:
`structure` → [stru(prefix, resolved), ct(UNRESOLVED),
ure(suffix)]. Gold set: exactly 1/49 re-derived (structure);
mov/sin/ev were verified as RESOLVED position_class='prefix'
rows (not quarantined), so movement/singing/evolve stand;
INTERNAL gold re-earned 49/49. Two mutants killed (predicate
loosened → 65/66; inventory union restored → 62/66).
Disclosed necessity: the morpheme.py edit required a harvest
re-run; the v1 delta is exactly one header pin line, and the
lm1_import_test T7 pin moved with it (45b42d65…), trail on the
PR.

## EVIDENCE

- Splitter suite form/lm2_splitter_test.py: 66/66 at the merged
  head (registered; branch LIST 276). Neighbour suites at the
  same head: lm1_harvest 22/22, lm1_import 55/55, lm_table 4/4,
  morpheme 6/6.
- Terminal regression campaign at 4d0de79 (main session,
  SIG-reset runner): fwd GREEN 276/276 EXIT 0; --twice pass 1 +
  pass 2, 276/276 GREEN EXIT 0; --order rev GREEN 276/276
  EXIT 0. Final packet: PR comment 6818432412. Disclosed: the
  first --twice attempt died mid-leg in a VM replacement (NO
  RESULT); only the missing legs were relaunched.
- Exact-head CI at 4d0de79: TERMINAL ALL-PASS (Form smoke,
  Python package, Studio browser acceptance). PR MERGEABLE /
  CLEAN at the merge step.
- Merged-main verification (fresh clone at c414e71, main
  session): splitter 66/66, harvest 22/22, import 55/55; live
  `split_word('biology')` → [bio, logy], accounted 1.0, through
  the real v2 pair on merged main; `incredible` middle honestly
  unresolved.

## TWO-CYCLE ACCOUNTING (WORKFLOW v1 §5)

Recorded honestly, for the authorities' disposition. This
circuit consumed: cycle 1, the build; cycle 2, the A9 census
correction; and a third touch, the quarantine-eligibility
repair. Both corrections belong to one honesty failure class —
a surface (artifact metadata in A9; authored annotations in
correction 2) claiming more authority than the underlying
evidence supported. A strict reading of the §5 cap puts this
circuit at/over two cycles on that class. Mitigating facts, for
the record and not as argument: both corrections were
Director-directed FIX-FIRST rounds inside one circuit (not
separate circuits), each was proven failing-first with real
rows, and neither changed the split contract. The reusable
lesson Uni has recorded: generated-artifact field inheritance
and quarantine-eligibility consumption are failing-first checks
that belong in the ORIGINAL build of any LM circuit; LM-3
(PR #398) carries an explicit quarantine-eligibility check in
its failing-first set for this reason. Whether this accounting
closes the circuit or requires a joint research note on the
class is the authorities' call — Q-LM2.2.

## SCOPE BOUNDARIES — WHAT THIS DOES NOT ESTABLISH

- NOT LM-3: no composition, no gloss, no sense selection.
  LM-3 THE COMPOSER is a separate circuit (PR #398).
- NOT LM-4: split_word is not wired into the translator or any
  executor path; nothing in the runtime calls it yet.
- NOT an external-gold claim: gold expectations are internal,
  re-derived against the v2 table with v1 derivations pinned.
- The split cache is PER-PROCESS; no cross-process or
  persistence claim is made.
- NO Master Work List credit is taken by this circuit or by
  this records PR. The proposal below is a proposal only.

## MWL CREDIT PROPOSAL (bounded; decision = the authorities')

The Director's conditional PASS (mail 1a1ceddc6e1f5001)
instructed Uni to propose bounded MWL credit AFTER merge +
register publication. Proposal: LM-2 THE SPLITTER be entered as
its OWN new COMPLETE row in the Master Work List, scoped
exactly to what merged: `split_word` (census-whole →
table-recorded → guarded greedy), the lm0_census_v1.json
artifact, the full-row-set receipts (accounted /
morpheme_resolved), and the quarantine-eligibility predicate.
Uni proposes a discrete row rather than attachment to the LM-1
rows because the failure surface, the suite, and the evidence
are separately falsifiable — the same reasoning that kept LM-1
harvest and LM-1 import as distinct records. If the authorities
prefer attachment to the LM family rows, Uni will apply that
instead. Nothing is claimed in this PR; the headline does not
move on Uni's word.

## Questions for the Director

- Q-LM2.1: MWL credit for LM-2 — a new discrete COMPLETE row
  as proposed above, attachment to the LM family rows, or no
  credit?
- Q-LM2.2: Two-cycle accounting (above): is the circuit closed
  with the accounting on record, or is a joint research note on
  the honesty failure class required before LM-3 proceeds past
  its own gate?
- Carried, NOT duplicated: Q-LM1-IMP.1 / .2 / .3 (LM-1 import
  credit; generation-directory layout; the v1 concurrent-writer
  window) remain the authorities' from the LM-1 import report
  (PR #396) and are not re-asked here.

## Anticipated probes

- "Can a quarantined row still influence a split?" Its senses
  remain visible in lookup() output and in piece row sets —
  that is the LM-1 design (visibility ≠ eligibility). It cannot
  drive position, known-middle, slot kind, or the piece
  inventory: one predicate gates all four consumers, pinned by
  S17 with real rows and two killed mutants.
- "Did correction 2 change any recorded split?" No. Recorded
  splits are a separate path and were untouched; the gold set
  moved exactly 1/49, and that one (structure) moved TOWARD
  honesty — the middle is now named UNRESOLVED instead of being
  silently carried by a quarantined row.
- "Is the census artifact trustworthy now?" The A9 diff is
  exactly the 101 inherited labels, nothing else; the multiset
  of (word, category, meaning) is unchanged; an independent
  span-first parser reproduces all 488 rows; the source pin
  never moved.
- "Why should the campaign be believed after a VM kill?" The
  killed --twice attempt is recorded as NO RESULT, not a pass;
  the terminal campaign at the merged head has all three legs
  GREEN with exit codes in the packet, and merged-main
  verification was re-run independently on a fresh clone.

## Ace's move

Nothing needed from Ace. Next step owner: the authorities —
review of this records PR through the normal passes; Q-LM2.1
and Q-LM2.2 dispositions at their convenience. LM-3 (PR #398)
proceeds under Uni in parallel.
