# DIRECTOR REPORT — STEP 6 LEAF HONESTY (B1/B2/B3/B4/B6)

Evidence submitted for a bounded ruling. A report is evidence,
never a certificate. Merged != certified.

## Ruling this answers

Director audit §5 behavior rulings, order step 6:
- B1 Decay FIX: when the enhance/growth gate refuses, report
  refusal, leave scores unchanged, do not say scores decayed.
- B2 Loop FIX: Loop uses Cycle's finite 1..5 bound; report
  requested and executed counts and any clamp; malformed labels
  handled explicitly; no accidental unbounded loop.
- B3 Merge FIX: fewer than two resolved required sources refuses
  missing_source; zero-source invocation must not choose the
  last two units; preserve ambiguity refusal and zero mutation.
- B4 Split FIX: bare, unknown or misspelled source refuses
  missing_source; ambiguity refuses; never silently select the
  last unit.
- B6 Translate FIX: empty input reports nothing_to_translate,
  with no fabricated Show intent and no side effects.
Step 6 general: preserve positive behavior; zero mutation on
refusal.

## Frozen candidate

Candidate: 1968414de8279a3d26d1c0c340c8905ed0d4abb8
Candidate tree: ed9cdeb44f2e8c32115502a4c55f1d86b5ad9bef
Base: main 809d5a2a5379cae4706f57933c9104b9cc241d35 (PR #182 merge)
PR: #184 — merged as 2059d6a083b40d1065eb837454eff763a553dc1b
  (2026-11-01T06:10:52Z)
Merge tree: ed9cdeb44f2e8c32115502a4c55f1d86b5ad9bef == candidate tree
Merge parents: 809d5a2 + 1968414

## Defects (verified at 809d5a2, public path)

Failing-first probe (hidden_files/step6_probe.py) on unmodified
code reproduced ALL FIVE defects:
- B1: Decay returned ok=True, "Scores decayed ×0.5.", with
  scores unchanged (gate had refused).
- B2: Loop::7 ran 7 cycles (unbounded vs Cycle's 1..5);
  Loop::bogus silently ran 1 cycle.
- B3: bare Merge merged the last two units (vals[-2:] fallback).
- B4: Split::nosuchthing split the last unit (last-unit fallback).
- B6: translate("") / bridge("") / bare Translate leaf all
  fabricated a Show intent.
On fixed code every probe line flips to the honest contract.

## Fix (SWAT unanimity 4/4 recorded BEFORE implementation)

Packet: STEP6_LEAF_HONESTY_PACKET.md — Custodian, Interpreter,
Sentinel, Mechanic all AGREE, with a Director's-eye pre-mortem
recorded before implementation. Files: form/executor_leaf.py,
form/dell_matrix/live_identity.py, form/dell_matrix/translate.py,
new suite form/step6_leaf_honesty_test.py (registered in regress;
211 -> 212 entries), plus pinned-exhibit amendments (leaf2,
leaf3, leaf4, cac_i, core_i_maturity, p0r3, d1_proof_cards) and
DELL_PROOF_CARDS.md regenerated (81 bare executed / 19 named
failures; diff confined to Dells 16/22/45 rows, counts, and the
five deep notes).

- B1: the leaf captures EnhanceGate.decay()'s result. ok=False ->
  ok=False, error = the gate reason ("enhance OFF"), message
  "Decay refused: enhance OFF — scores unchanged."; no note_seed.
  The manual fallback branch (object without decay()) respects
  the same gate. Positive path unchanged.
- B2: empty label -> requested 1; digit label -> requested int;
  executed = clamp(requested, 1, 5), enforced BEFORE grow_ideas
  runs. Message reports "Loop: requested <r>, executed <e>." plus
  "(clamped to 1..5)" when they differ. Non-digit non-empty label
  -> ok=False, error "invalid_loop_count", zero growth.
- B3: merge_live's vals[-2:] fallback DELETED. Fewer than two
  resolved sources -> missing_source, zero mutation. Ambiguity
  branch untouched (ambiguous_source identity preserved).
- B4: split_live's last-unit fallback DELETED. No resolved
  source -> missing_source, zero mutation. Ambiguity untouched.
- B6: translate() entry guard — empty/whitespace input returns
  Intent(action="nothing_to_translate", dell=None, term="",
  args={}, mandel="", english=""). bridge("") inherits the
  intent; the leaf renders ok=False / nothing_to_translate.
  Non-empty Translate path unchanged. One guard at translate()'s
  entry — no second empty-check authority downstream.

## Evidence

- Suite STEP6_LEAF_HONESTY: 34/34. Every refusal asserts zero
  mutation (units, scores, nursery) in memory and, for Decay,
  on reloaded persisted state.
- Mutants (defect-restoring; each reverted by inverse edit and
  the suite re-verified 34/34 after the last revert):
  M1 Decay gate ignored 31/34 (exactly the B1 refusal checks);
  M2 Loop clamp removed 32/34; M3 Merge fallback restored
  31/34; M4 Split fallback restored 31/34; M5 Translate guard
  removed 31/34 (translate/bridge checks; the leaf's own empty
  check still held the leaf line).
- Neighborhoods green: leaf2 33/33, leaf3 44/44, leaf4 36/36,
  leaf cluster 22/22, cac 177/177, core_i_maturity 22/22,
  p0r3 80/80, lineage 46/46, unified 37/37, r2 honesty 27/27,
  symbiosis ledger 39/39, semantic route 59/59, proof cards 6/6.
- Regress x3 on candidate 1968414 (logs hidden_files/
  step6_logs/): fwd 212/212 GREEN, --twice 212/212 GREEN x2,
  --order rev 212/212 GREEN; step6 suite 34/34 in every leg.
- Exact-head CI verified COMPLETE in a SEPARATE step before
  merge (2026-11-01 01:10 CDT cycle run, after a prior check
  found smoke IN_PROGRESS): package run 41278472192 SUCCESS
  completed 2026-11-01T05:51:14Z; smoke run 41278472182 SUCCESS
  completed 2026-11-01T06:07:40Z. An Advanced Security code
  scanning run (41278474448) also completed success; per
  standing law any evaluation that could not run would be
  recorded EVALUATION_UNAVAILABLE — none is claimed beyond
  what ran.
- Fresh-clone regress at merge 2059d6a: 212/212 GREEN
  (log hidden_files/step6_logs/freshclone_regress.log;
  step6 suite 34/34).

## Limitations

- Loop labels are the leaf invocation surface; counts are
  proven against nursery deltas in the suite, not against
  arbitrary chain compositions (chain-level refusal reporting
  is the step 7/8 surface, not claimed here).
- B1's manual-branch control uses a stub enhance object
  without decay(); real Program enhance objects take the
  gate path, which is covered directly.
- Claims are bounded to the executed paths above; no
  whole-registry or whole-program claim is made.

## Bounded ruling requested

That B1, B2, B3, B4 and B6 be ruled on within the scope
presented: the five leaf contracts above, as implemented at
2059d6a, with the suite, mutant, regress, CI and fresh-clone
evidence cited. No broader certification is requested.

## Anticipated probes

Attacks Uni expects, with their evidence:
1. Diff persisted state after a refused Decay / Merge / Split
   (not just messages). Covered: the suite asserts scores and
   units unchanged in memory and, for Decay, after reload.
2. Enter through the OTHER paths — chain execution of a
   refused Decay/Loop, translate via bridge() / to_mandell() /
   the English REPL path with empty or whitespace input.
   Covered for bridge("") and the bare/whitespace leaf (suite);
   the chain-atom reporting surface is step 7/8 scope and is
   NOT claimed here — a finding there would be a pre-mortem
   partial hit, recorded as such.
3. Refusal identity: ambiguous Merge token must still report
   ambiguous_source, not collapse to missing_source. Covered:
   ambiguity checks preserved in the suite for both Merge and
   Split.
4. Decay refusal bypass via the manual fallback branch
   (no-decay-attr object). Covered: stub control in the suite;
   the branch applies the same gate verdict.
5. Loop extreme labels (100, 999999, 0, -3, "3.5", " 7 ") —
   executed count proven against nursery delta, not the
   message alone. Covered: clamp + refusal checks assert the
   nursery delta equals executed x per-cycle delta; 0 and
   negative labels clamp/refuse per the digit/non-digit split
   ("-3" is non-digit -> invalid_loop_count refusal, zero
   growth).
A Director finding outside this list will be named as a
pre-mortem miss in the next report.

## Questions for the Director

Q1. Loop label " 7 " (whitespace-padded digit): the suite's
contract treats labels as given (non-digit -> refusal). Should
padded digits be trimmed and accepted (requested 7, executed
5), or is refusal the intended contract? Unblocks: a one-line
label-normalization decision in executor_leaf. Uni recommends
refusal stands — labels are exact invocation syntax elsewhere
in the registry, and silent trimming creates a second parsing
authority.
Q2. B1's refusal message surfaces the gate's own reason string
("enhance OFF"). Should refusal reasons from gates be a stable
public contract (safe for callers to match on), or display
text only, with the stable contract being ok=False + scores
unchanged? Unblocks: whether step 11 wording pass may reword
gate reasons freely. Uni recommends display text only; the
machine contract is the verdict and the unchanged state.
