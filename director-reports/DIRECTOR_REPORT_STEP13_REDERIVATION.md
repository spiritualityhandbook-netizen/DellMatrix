# DIRECTOR REPORT — STEP 13: GATE 0 RECONCILIATION + PAIRWISE RE-DERIVATION

Ruling requested: bounded — accept the Step 13
re-derivation as the current pairwise evidence at the
repaired freeze (superseding ledger v1 AS CURRENT
EVIDENCE only; v1 remains the historical PRE_AF record),
and rule on Q1 below.
Identity: frozen head c94e2237ed9e52da02593e7c79a6d787cf9a21ff,
tree dc306f059164559bdf881bde2a47cb7987591ff5 (code head
195fafa; the delta is director-reports/ only, verified).
Exceptions first: DEFECT 0 and SEAM_FAILURE 0 in raw and
final classes; the 8 UNIQUE_CANDIDATE rows are unchanged
from Gate 3's genuine residue; no pair is certified by
this report — it is evidence submitted for re-ruling at
step 14. Director asleep: held SUBMITTED.

## Gate 0 reconciliation (Director 8.13, first half)
Gate 0 closed at 11933da (PASS WITH FLAGS, AF-1..6).
PR #162's ledger canaries were Gate 4 chunk 2 work under
Ace's symbiosis execution order — later scope, not a
Gate 0 re-opening and not unauthorized work. Ledger v1
(43fe6967…) is PRE_AF historical evidence. Full text:
STEP13_PACKET.md §2.

## Method (SWAT pre-mortem + 4/4 method unanimity first)
Census recomputed at the freeze with the verbatim Gate 0
apparatus (new census sha c2288818…); sweep classifier
verbatim for the raw run; new designed prefixes
dispositioned only in a before-asserted v4 overlay
(R5/R6 + the Gate 2 R86/41 baseline-correction precedent);
raw ledgers never edited; oracles are full-state snapshot
diffs + store deltas + selected-in-plane, not ok=True.

## Results
Standalone changes 11933da -> freeze: 3/100 (13 Loop
sensitivity narrowed; 16 Decay and 83 Ungroup now return
their Step 6 / Step 10 designed refusals standalone).
Raw sweep (9,900 pairs + 100 identity, 193 s, 101 block
files): FI 6287, F 1992, IC 1163, A_FAILED 184,
NOT_POSSIBLE 181, UNIQUE 93, DEFECT 0, SEAM 0.
Overlay: 454 pair + 2 identity before-asserted changes.
FINAL: F 1989, FI 6375, IC 1528, UNIQUE 8, DEFECT 0;
identity 89 IDEMPOTENT / 11 HONEST_REFUSAL / 0 FAILURE.
Diff vs v1: 369 pair changes; the three non-clash
residuals are mechanism-explained (55->13, 82->13 from
13's sensitivity narrowing; 93->55 from Step 8's tx
channel — Set inside Try now writes core_ii.tx, store
effect identical). Ledger v2: gate4_ledger_v2.json,
sha de5354f0254cf87b1f3e0d1df30006d70eb846ffdc774b989e0bb4a0cfc2bafd.
Canary discipline: no raw canary in any sweep file; zero
owner residue; worktree clean. Repo symbiosis suite pins
v1 as historical identity only — no code change needed.

## Limitations
Single-machine, synthetic world W, battery v0.1
invocations — same evidence class as Gate 2 (PUBLIC_
ENTRY_PATH), not real-use proof. Sensitivity is measured
against the census outcome signature; 13's narrowing is
reported as measured, its internal cause attributed to
the Step 6/DIR-F13 Loop lineage, not separately proven.

## Anticipated probes
- "Overlay = classifier massage?" Raw totals are
  published above and preserved in step13_harness/sweep/;
  every overlay change carries its before class and rule
  (step13_rederived.json, 454+2 entries).
- "Why is INTENDED_CLASH up 365?" Because two Dells that
  used to falsely succeed standalone (16, 83) now refuse
  by design in every composition — the increase IS the
  Step 6/10 honesty repairs, counted.
- "93->55 flipped — regression?" B's store effect is
  byte-identical; the added write is core_ii.tx, Step 8's
  frame-ownership channel. Named, bounded, intended.
- "Census for 41?" Corrected alongside 86 per the Gate 2
  precedent; its corrected row changed no class outside
  the B=42 re-run set (89 baseline-correction changes are
  all B=86/B=42 rows).

## Questions for the Director
- Q1: Should a small follow-on circuit add ledger v2 pins
  to form/mandell/symbiosis_ledger_test.py (keeping the v1
  historical pins), or should v2 pins wait for the step 14
  ruling? Uni recommends: wait — pinning an uncertified
  ledger into the per-PR suite before your ruling would
  invert the authority order. (Unblocks: whether that
  circuit is queued before step 14.)
- Q2: Is the v4 overlay rule set (R5/R6 designed prefixes
  from the Step 6/10 contracts) the correct disposition,
  or should 'enhance OFF' / ungroup_missing rows remain
  NOT_POSSIBLE as a permanent scar? Uni recommends the
  overlay: both errors are the gates' own designed
  refusal reasons, cited to code + packets. (Unblocks:
  the class vocabulary step 14 presents.)
