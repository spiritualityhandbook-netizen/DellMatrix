# GS-4 REPAIR REPORT — wall-mate enumeration filter, red→green evidence, register row 184 (2026-11-12)

Circuit: GS-4 bounded repair (implementation authorized; **CODE MERGE
HOLD remains** — this PR is evidence, not a merge request executed).
Authority trail: Ace's Growth Selection Doctrine (2026-11-12);
PR #402 grounding + comment 6827580827; PR #403 independent
reproduction; PR #404 prep pack (report
GS4_SANDBOX_CONTRACT_PREP_2026-11-12.md, contract C-1..C-10,
failing-first suite 6/10); Keeper independent challenge CONFIRM
(comment 6828513382); Director scoped ACCEPTANCE mail
1a1d05d91f6401dc; **Director GS-4 SCOPE RULING mail
1a1d077edcbc82e2 (2026-11-12)**: defect accepted, register OPEN,
bounded implementation authorized, code merge HOLD until final
verification. This PR executes ruling §3 exactly, within its bounds.

Branch: `uni/gs4-repair-1112`, parented on the prep head 5a34b1e
(PR #404's head) — the prep records and the failing-first suite are
this branch's ancestry, so the suite's red→green transition is in
one history.

## 1. REQUIREMENT (ruling §3, contract C-1..C-10 as acceptance baseline)

Filter candidate pair enumeration in
`form/dell_matrix/ringed_growth.py` by canonical Plane box
membership / wall-mate admissibility, using the existing authority.
Boxed units grow with box mates; different boxes are strangers;
boxed vs unboxed are strangers. The one filter must prevent BOTH
manifestations: cross-wall pair proposals and boxed-primary drift
importing outside tokens. Add the receipted
`pairs_excluded_cross_sandbox` count. Preserve unboxed output
byte-for-byte and existing `scope_ids` semantics (intersection,
invalid/empty refusal). Do not change default-unset semantics
(GS-3), affinity weights, DCC XI–XV pins, unrelated executor/loader,
or add cross-wall bypass flags. Unbox-then-grow is the only crossing
door. U1–U3 remain UNPROVEN limitations (§7) — not repaired, not
counted as repaired.

## 2. MECHANISM (the whole patch)

One product file changed: `form/dell_matrix/ringed_growth.py`.

- `_wall_key(plane, uid)` (new, module-private): a unit's wall key —
  `None` when unboxed, else its `sandbox_id` — read from the SAME
  Unit fields `Plane.box`/`Plane.unbox` maintain and
  `Plane.enhance_scope` consults. No second store, no new authority,
  no new Dell.
- In `RingedGrowth.run`, per cycle: wall keys are computed once for
  the enumerated id list; a candidate pair `(a, b)` is admitted iff
  `wall_keys[a] == wall_keys[b]` (C-1). A cross-wall pair is skipped
  BEFORE `_affinity` is called — never scored, never gated, never
  drifted from (C-1: an eligibility boundary, not a penalty). This
  closes manifestation (b) at the same point as (a) because the
  drift branch's peer is the enumerated pair's second member
  (`gained = _tokens_uid(plane, b) - _tokens_uid(plane, a)`) — with
  no cross-wall pair enumerated, no outside peer exists to import
  tokens from.
- Receipt (C-7): each step receipt gains
  `pairs_excluded_cross_sandbox: N` (present on every step,
  including the no-live-ideas step at 0, and 0 on unboxed fields);
  the run result gains the cross-cycle total under the same key.
  Silence about exclusions is a contract violation.

Nothing else in the file changed semantically: `_affinity` and its
weights are untouched (the soft `in_scope` term remains for
admissible pairs, where it already agrees with the wall);
`Plane.enhance_scope`, `Plane.box`/`unbox`, `ScopedPlaneView`,
`grow_ideas`, and the Nursery are untouched; no bypass flag,
parameter, or environment switch exists (C-5).

## 3. RED → GREEN EVIDENCE (form/gs4_sandbox_test.py)

Published failing-first on unmodified main @074b30f (PR #404):
6/10, with A1/A2/A3/B2 red verbatim (quoted in the prep report §3).

After the repair, the suite runs **14/14 PASS** (the ten published
checks, plus four checks added by this PR: A1b and B3 pin the C-7
receipt on the boxed and unboxed runs; E1/E2 pin C-3 — mixed boxes
and boxed/unboxed are strangers. B2's assertion is unchanged; its
wording was updated from failing-first framing to its post-repair
meaning — disclosed here and in the commit):

```
=== GS-4 SANDBOX CONTAINMENT ===
  [PASS] A0 wall is real in plane authority :: enhance_scope(in_a)=['in_b']
  [PASS] A1 enumeration excludes cross-wall pairs :: pairs_scanned=4 (10 = all pairs incl. 6 cross-wall; 4 = wall-respecting)
  [PASS] A1b receipt counts excluded cross-sandbox pairs (C-7) :: step=6 total=6 (6 expected)
  [PASS] A2 no proposal parents span the wall :: cross-parented proposals=0 []
  [PASS] A3 no boxed drift offspring carries outside-only tokens :: drift offspring carrying outside-only tokens=[]
  [PASS] B1 unboxed control still scans all pairs :: pairs_scanned=10 (10 expected)
  [PASS] B2 boxed default output differs from unboxed (the wall acts) :: boxed proposals=4 unboxed proposals=10; identical=False
  [PASS] B3 unboxed receipt shows zero exclusions (C-7) :: step=0 (0 expected)
  [PASS] E1 mixed boxes: only unboxed-unboxed pairs scan :: pairs_scanned=3 excluded=7 (3 scanned / 7 excluded expected)
  [PASS] E2 mixed boxes: no proposal crosses any wall :: crossing proposals=[]
  [PASS] C1 scope_ids growth scans only the selected pair :: pairs_scanned=1 (1 expected)
  [PASS] C2 scope_ids growth has zero leaks :: leaks=0
  [PASS] D1 invalid scope ID refuses with ValueError :: ValueError="scope IDs not on plane: ['missing_unit_xyz']"
  [PASS] D2 empty scope grows nothing (no silent fallback to full) :: proposals=0 scope_mode=contextual
GS-4 SANDBOX: 14/14 checks passed
```

The controls that passed before the repair (A0, B1, C1, C2, D1, D2)
still pass: `scope_ids` containment, empty-scope no-fallback, and
invalid-scope ValueError are byte-for-byte the pre-existing behavior
(the filter composes by intersection inside the ScopedPlaneView —
the view presents only selected units, and every presented unit is
unboxed *in the view's boxes state* unless the underlying units are
boxed, in which case C-8 applies within the selection).

## 4. MUTATION CONTROLS (commit first; inverse-edit reverts only)

Real work committed (c6ea8af) before any mutant was applied.

- **Mutant (a) — filter removed** (`if False:` at the admissibility
  test): suite 7/14. The four original reds return — A1
  (pairs_scanned=10), A2 (the same 4 cross-parented proposal ids as
  the published failing-first run), A3 (the same 2 drift offspring
  with the same six outside-only tokens), B2 (boxed == unboxed,
  identical=True) — plus A1b/E1/E2, which pin the repair's own
  behavior. **Killed.**
- **Mutant (b) — admissibility weakened** to "exclude only when both
  units are boxed into different boxes" (boxed/unboxed treated as
  mates): suite 7/14. **A2 and A3 fail again** with the same
  cross-parented proposals and drift offspring — the boxed/unboxed
  stranger rule is load-bearing. E1 discriminates the mutant
  precisely: 9 scanned / 1 excluded (only the different-boxes pair
  in_a×in_b is still excluded). **Killed.**
- Both mutants reverted by inverse edit only; post-revert
  `git diff` on the file is empty (0 lines) and the suite was
  re-run to 14/14 on the restored tree.

## 5. UNBOXED-IDENTITY PROOF (C-4)

Method: the contract field (the suite's field) driven through the
public `Program.grow_ideas(1)` path on disposable owners, dumping
every proposal's full record (pid, kind, label, words, parents,
affinity, reason, origin, harmony, graph_coherence) plus gate
counts, fog count, and step receipts — once on the unpatched prep
base, once on the repaired tree.

- Unboxed run: proposal records **identical** (all 10, every field);
  gate counts, fog_cut, proposed_new/evolved identical; the step
  receipt is identical modulo the one added key
  (`pairs_excluded_cross_sandbox: 0`).
- Boxed run after repair: `pairs_scanned=4`,
  `pairs_excluded_cross_sandbox=6`; 4 proposals, all within-wall:
  `[in_a, in_b]` (inside pair), `[out_a, out_b]` (outside pair),
  `[out_a]` and `[out_b]` (outside single-parent drift — lawful:
  both parents and tokens are outside the wall together). No boxed
  unit's offspring carries any outside material.

Proposal IDs are content-derived (`_slug(label, seed)`), so record
equality is a byte-for-byte output claim, not a sampling claim.

## 6. FOCUSED REGRESSION (this PR; full campaign is a main-session step)

All runs via the canonical runner (`form.regress --passk <entry> 1`,
isolated copy semantics) on the repaired tree; DCC XI–XV
**unmodified** (no file in `form/mandell/` is touched by this PR):

| Suite | Result |
|---|---|
| form.mandell.dcc_xi_test | GREEN |
| form.mandell.dcc_xii_test | GREEN |
| form.mandell.dcc_xiii_test | GREEN |
| form.mandell.dcc_xiv_test | GREEN |
| form.mandell.dcc_xv_test | GREEN |
| form.mandell.dcc_xv_cross_process_test | GREEN |
| form.growth_persistence_test:smoke | GREEN |
| form.mandell.view_rooms_growth_test:smoke | GREEN |
| form.mandell.growth_unit_identity_test:smoke | GREEN |
| form.mandell.p3_r31_affinity_proof | GREEN |
| form.mandell.p3_r35_integration_proof | GREEN |
| form.mandell.p3_r36_graph_harmony_proof | GREEN |
| form.resonance_lifecycle_gate_test | GREEN |
| form.mandell.resonance_command_test:smoke | GREEN |
| form.nursery_confirm_race_test | GREEN |
| form.mandell.d1_recon1_scope_test | GREEN |
| form.lm1_harvest_test:smoke (22) | GREEN |
| form.lm1_import_test:smoke (55) | GREEN |
| form.lm2_splitter_test:smoke (66) | GREEN |
| form.c7schema_test:smoke (33) | GREEN |
| form.mandell.d1_proof_cards_test | GREEN |
| form.gs4_sandbox_test:smoke (14) | GREEN |
| form.dell_matrix.ringed_growth module self-test | 3/3 PASS (run directly; it is not a regress LIST entry) |

The DCC-XI–XV baseline pins (full-plane behavior on unboxed fields,
`scope_mode == "full"`) hold unmodified — as C-10 predicted, they
are reachable only through unboxed behavior, which §5 proves
unchanged. No pin was re-pinned; no conflict surfaced.

The full regression campaign (fwd / --twice / --order rev at the PR
head) is NOT run in this lane: the box is serial for campaigns and
the ruling's sequence (§5 of the ruling) places the campaign,
exact-head CI verification, and the merge transaction in the main
session. Exact-head CI state is reported in the PR body.

## 7. REGISTER (ruling §2)

Canonical data read on this branch's base first: 183 rows,
sequential 1..183, no gaps. No existing row covers GS-4 (row 144 is
DD-17 / C6.Boxes — standing/named sandbox *management*, a different
item; the prep PR proposed text but assigned no number). Per the
ruling, the next verified free extension row was assigned:

- **MWL 184 — "GS-4 Growth Sandbox Integrity / cross-wall
  enumeration"**, status **OPEN** / confirmed defect, **no
  completion credit**. 183 (LM-2) was not reused; 180/181/182 remain
  SANDBOXED.
- Items diff (exact): ONE item appended (n=184); no other item
  changed. (The JSON file also gains a trailing newline at EOF.)
- Generated register: `MASTER_WORK_LIST.md` regenerated with
  `master_list.py --out`; the generator's own `--check` verifies
  the committed render is byte-identical to a fresh render.
  Headline moves only by the denominator: 38/180 COMPLETE = 21.1%
  → **38/181 COMPLETE = 21.0%**; OPEN 85 → 86; the new row renders
  under its own block "Growth Selection — GS-4 (PR #402)".
- The defect dial does NOT move to FIXED on this PR: per the
  ruling, no dial movement until merged-main proof.

## 8. LIMITATIONS — U1 / U2 / U3 (UNPROVEN; verbatim-honest)

The following remain **UNPROVEN**. They are **not repaired** by this
circuit and are **not counted as repaired** anywhere in this report
or the register row. Per ruling §4 they are follow-up probe work;
if they expose new leaks, the evidence returns with a bounded scope
extension — this patch is not silently widened to cover them.

- **U1 — Post-growth mutation surfaces: UNPROVEN.** `grow_ideas`
  does more than `run()`: after it returns, duo.evolve runs on the
  owner's state, nature forces plant/grow over plane units, and the
  opt-in `auto_confirm_grow` path confirms PENDING proposals into
  live units. Whether forces or confirm can move outside material
  INTO a boxed unit's live content (as opposed to growth proposals)
  was NOT probed in this circuit. This repair governs RingedGrowth
  proposal generation only.
- **U2 — Docked-session synthesis semantics: UNPROVEN.** With a
  docked Psalm (`session.synthesize([a, b])`), the filter bounds
  WHICH pairs reach the dock — cross-wall pairs never reach it —
  but what the docked mind authors for an admissible pair is
  outside token-level proof; by doctrine its output is PENDING and
  read, not proven. No claim is made about docked content beyond
  pair admissibility.
- **U3 — Multi-cycle compounding: UNPROVEN.** All repair evidence
  (suite, identity proof, mutants) runs `cycles=1`. The code-read
  argument from the prep — proposals from cycle 1 remain PENDING
  and do not become plane units inside `run()`, so the pair set
  does not grow within `run()` — was not re-proven by probe in
  this circuit. If a caller confirms proposals BETWEEN grow calls,
  the confirmed units are ordinary plane units for the next call
  and the wall question re-applies to their boxing state at that
  time; that interaction is untested.

Further honesty notes: test realism of the behavioral evidence is
INTEGRATION (public `Program.grow_ideas` path on disposable
owners) — the same level as both reproductions, stated, not
upgraded. Merged ≠ certified: the CODE MERGE HOLD stands until
Keeper final confirmation naming the head, Director final code
disposition, the main-session campaign, and the §32 transaction.

## 9. PR #404 DISPOSITION (disclosed)

PR #404 (prep) carried the instruction of its moment, including the
line the Director has since superseded in effect: "Do not merge a
red failing-first suite as a standalone records PR." This repair PR
is branched FROM the prep head and turns that suite green, which is
exactly the resolution the ruling directs — the red suite never
merges standalone; it merges, if the authorities so rule, only as
the ancestry of this green repair. Final handling of #404 itself
(close as superseded vs. auto-close on this PR's merge, since the
prep commit 5a34b1e is this branch's parent) is left to the main
session and the authorities; nothing in this PR merges anything.

## 10. ASKS

1. **Keeper:** independent final confirmation naming this PR's
   head (the #404 records-only stamp does not certify code, per
   the ruling).
2. **Director:** final code disposition on this evidence.
3. **Both:** merge remains on HOLD until (1) + (2), the
   main-session full campaign at the head, exact-head terminal CI,
   and the §32 fresh-mail transaction. Register row 184 stays OPEN
   until merged-main proof; narrow credit, if any, only after.

## 11. CORRECTION — malformed boxed wall-key fail-open (Director review mail 1a1d0990c34b0d99, 2026-11-12)

**Finding (Director, code inspection).** `_wall_key` returns `None`
for BOTH (a) a genuinely unboxed unit and (b) a unit with
`sandboxed=True` but `sandbox_id=None`/absent. `Plane.enhance_scope`
refuses boxed membership in state (b) (its `u.sandboxed and
u.sandbox_id` test falls through to the unboxed-peer list), but
RingedGrowth's `None == None` equality ADMITTED the malformed unit
as a wall-mate of genuinely unboxed peers — a fail-open boundary
under malformed/restored state.

**Reproduction verdict: REPRODUCED.** Five failing-first checks
(F1–F5) were added to `form/gs4_sandbox_test.py` and run against the
pre-correction head 119b58f. Verbatim failing output (suite 14/19):

```
  [FAIL] F1 malformed boxed unit is refused, never wall-mate of unboxed :: refused=[] proposals_touching_malf=5 pairs_scanned=15 excluded_cross=0
  [FAIL] F2 malformed unit: no outside-token drift to or from it :: drift_from_malf=[]
  [FAIL] F3 unknown sandbox_id is refused (fail-closed) :: refused=[] proposals_touching_ghost=0
  [FAIL] F4 membership-inconsistent unit is refused; its claimed-mate pair never scores :: refused=[] stale_pair_proposals=1 pairs_scanned=7
  [FAIL] F5 well-formed unboxed peers still grow beside refused units :: pairs_scanned=7 (6 = the pairs among the 4 unboxed units; stale_a's 4 cross-wall pairs excluded, stale_b refused outright)
GS-4 SANDBOX: 14/19 checks passed
```

Reading of the reds, precisely: in the F1 field (one malformed unit
+ five unboxed), ALL 15 pairs scanned and **5 proposals carry the
malformed unit in their parents** — it paired with unboxed peers
exactly as the Director's inspection predicted. F2's red is
entangled with F1's by construction (its conjunction requires zero
malf-parented proposals at all; the drift sub-clause itself observed
no drift offspring — `drift_from_malf=[]` — because in that field
the malformed unit's pairs gated to Solstice crosses, not drift;
the pairing admission is the leak, and F2 stays red until both
halves hold). F3's red is the *silence*: the unknown-id unit paired
with nobody in that run (its key isolates it by accident of
equality), but no refusal existed — correction converts the
accident into a guaranteed, receipted refusal. F4's red is a
proposal parented `{stale_a, stale_b}`: the unit the Sandbox record
does NOT list scored with its claimed mate. F5's red is F4's
consequence (7 scanned vs 6 lawful).

**State taxonomy (examined BEFORE fixing, against Plane's own
code).** `Plane.box()` (plane.py:182-196) sets the unit fields and
appends membership together; `Plane.unbox()` (:198-207) clears both
sides together. Every permutation of the public box API was traced,
including re-boxing a unit into a second sandbox (box() does not
remove it from the first box's member_ids — the stale listing keeps
the unit's CURRENT claim verified, and enhance_scope/graph_view key
off the unit's current sandbox_id, so the stale listing is inert)
and REPL group add/remove/delete (repl.py:1442/1448/1473 — all via
box/unbox). **No box-API path produces a state where a unit's
sandboxed/sandbox_id claim disagrees with its CURRENT box's
membership.** The malformed states are therefore NOT canonically
legitimate live states; they are corruption-class states that are
nevertheless REACHABLE, through exactly these doors:

- **S1 `sandboxed=True, sandbox_id=None`/empty/non-string** —
  verbatim restore: `form/persist_rest.py:506-507` restores
  `unit.sandboxed = bool(...)` and `unit.sandbox_id = u.get(...)`
  with NO validation (blank_cube pack restore :63-64 identical).
  A save whose unit record carries `sandboxed: true` with a null /
  missing / empty id restores into S1 exactly. Canonical verdict on
  this shape already exists: `form/mandell/unit_containment.py`
  `_malformed_sandbox` (F1, Director review 2026-11-04) defines it
  as malformed and refuses such endpoints outright.
- **S2 `sandbox_id` names no Sandbox record** — restore rebuilds
  `plane.sandboxes` ONLY from the saved `sandboxes` map
  (persist_rest.py:512-519); a unit record referencing an id absent
  from that map (hand-edited save, partially-written pair, older
  save shape) restores into S2. (The reverse divergence — a Sandbox
  record listing a unit whose flag is False — is inert for growth:
  `_wall_key` reads the unit side, and the unboxed unit pairs as
  unboxed, consistent with Plane.display/enhance_scope.)
- **S3 membership inconsistency (unit claims box X; X's member_ids
  omits it)** — the restore asymmetry produces it directly: unit
  fields restore from the UNITS map (:506-507) while Sandbox records
  rebuild from the SANDOXES map's members lists (:512-519) — two
  independently-authored maps in one save; any divergence between
  them restores into S3. Also producible by direct member_ids
  record edits. Direction (ii) (record lists a unit that does not
  claim the box) is inert for growth, per S2's note.

So: legitimate through NO supported operation; reachable through
restore of divergent saved state. The repair therefore refuses —
it does not "repair" the state, invent membership, or collapse the
unit to unboxed.

**Repair (same circuit, wall-key logic only,
`form/dell_matrix/ringed_growth.py`).**

- `_malformed_boxed(plane, uid)` (new): True iff the unit claims
  sandbox isolation (`sandboxed` truthy) AND its claim fails
  verification against the canonical Plane box authority —
  sandbox_id not a non-empty string (the unit_containment F1
  definition, reused, not reinvented), OR no Sandbox record under
  that id, OR the record's member_ids does not contain the unit.
- In `run()`, per cycle, the malformed set is computed BEFORE the
  wall-key equality test; any pair touching a malformed unit is
  refused (never scored), counted in `pairs_excluded_malformed_box`.
- Receipt (bounded, explicit, in the existing C-7 style): each step
  receipt gains `pairs_excluded_malformed_box: N` and
  `malformed_box_units_refused: [ids]` (also present, zero/empty, on
  the no-live-ideas step); the run result gains the cross-cycle
  total `pairs_excluded_malformed_box` and the run-union
  `malformed_box_units_refused` list. Silence remains a violation.

**Post-fix behavior (suite 19/19).** F1: `refused=['malf']`, 0
proposals touch it, `pairs_scanned=10` (the five genuinely unboxed
units' pairs — the malformed unit's 5 pairs refused). F3:
`refused=['ghost']`, 0 proposals. F4: `refused=['stale_b']`,
`stale_a` (listed member) NOT refused, claimed-mate pair never
scores, `pairs_scanned=6`. All 14 prior checks unchanged and green.

**Receipt counts on the corrected head.** Well-formed fields:
`malformed_box_units_refused=[]` and
`pairs_excluded_malformed_box=0` on every step and result — the
unboxed-identity proof of §5 was re-run post-correction: the
unboxed run's 10 proposal records are again identical to the
pre-patch records in every field (pid, kind, label, words, parents,
affinity, reason, origin, harmony, graph_coherence), gate counts
and fog count identical; step receipts are identical modulo the
added GS-4 keys, whose values on this field are 6-excluded (boxed
run) / 0 (unboxed run) for cross-sandbox and 0 / empty for the
malformed refusal on both runs.

**Mutation control.** Real correction committed first (0405445);
the fail-closed branch was then disabled by inverse edit
(`malformed = set()` at the computation site): suite returned to
EXACTLY the failing-first state — 14/19 with F1–F5 red and
byte-identical details (proposals_touching_malf=5, pairs_scanned=15
and 7). Reverted by inverse edit; `git diff` empty; suite re-run
19/19 on the restored tree. **Killed.**

**Focused regression at the corrected head.** DCC-XI..XV
unmodified: dcc_xi, dcc_xii, dcc_xiii, dcc_xiv, dcc_xv,
dcc_xv_cross_process — all GREEN. The §6 focused set re-run:
growth_persistence, view_rooms_growth, growth_unit_identity,
p3_r31_affinity_proof, p3_r35_integration_proof,
p3_r36_graph_harmony_proof, resonance_lifecycle_gate,
resonance_command, nursery_confirm_race, d1_recon1_scope,
lm1_harvest (22), lm1_import (55), lm2_splitter (66), c7schema
(33), d1_proof_cards, gs4_sandbox (19) — all GREEN; ringed_growth
module self-test 3/3. Full campaign (fwd/twice/rev) remains a
main-session step at the corrected head, per the review's own
sequence.

**Scope honesty.** The correction touches ONLY the wall-key /
enumeration logic of `ringed_growth.py` plus the suite and this
report. It does not change Plane, persist, or containment; the S2
reverse divergence (record lists a non-claiming unit) is documented
inert above and deliberately NOT acted on — no second authority, no
state rewriting, no healing of saved state. U1/U2/U3 remain
UNPROVEN (§8 unchanged). MWL 184 remains OPEN, no credit. CODE
MERGE HOLD continues.
