# DIRECTOR RULING — CORE I CONTRACT (PR #256)

Date: 2026-11-03
Mode: B — REVIEW COMPLETE
PR: #256
Reviewed head: 3f858d91871d62b999f48a0a0b7f3e1d27a7cd98

DECISION: **O1 APPROVED. INVESTIGATION ACCEPTED.**

PR #256 documentation-only merge AUTHORIZED, subject to unchanged
head, successful CI, and merge-tree verification. Evidence
integrity independently verified: 27/27 SHA-256 matches.

## Findings accepted

- 50 of 51 Core I Dells silently ignore parsed typed arguments.
- Dell 8 [Create] is the sole registered exception.
- The 51-Dell single-versus-chain parity sweep reports no
  differences.
- `06[Cycle](cycles="3")` versus `06[Cycle] :: 3` demonstrates a
  misleading behavioral difference, not merely a documentation
  inconsistency.

## Contract decision

O1 — reject silent argument loss. Core I should refuse unsupported
typed arguments explicitly, consistent with the certified Core II
rule.

## Critical correction — gate placement

The proposed condition must not reject a whole chain based on its
first Dell. Example: `03[Logic] > 55[Set](key="tempo", value="120")`
contains a Core I atom followed by a valid typed Core II atom; a
gate keyed on the primary Dell would incorrectly reject the valid
Set. The correct implementation is per executing Core I atom at the
common `execute_seed` entry point:

- On single-atom Core I dispatch, refuse unsupported arguments
  before mutation.
- On chained Core I dispatch, rely on the existing per-atom
  re-entry through `execute_seed(..., _leaf=True)`.
- Never refuse a whole chain merely because another atom has typed
  arguments.
- Preserve skip semantics and existing chain continuation.

This keeps one validation authority without introducing the reverse
of the AF-1 parity defect.

## Rulings table

| Item | Ruling |
|---|---|
| O1 — Uniform refusal | APPROVED, with per-atom correction |
| O2 — Document silent ignore | DECLINED |
| O3 — Hybrid role collision | DECLINED |
| Q-C1 — Contract then repair | APPROVED; separate implementation circuit authorized |
| Q-C2 — Seed echo | Preserve existing boundary; new diagnostics contain role names only |
| Q-C3 — English Intent.args | Separate bounded contract review required |

The AF-1 check 7 amendment is expressly authorized: replace the old
silent-success expectation with single/chain refusal parity.
Preserve its historical documentation.

The Dell 37 missing REPL error message is a verified adjacent
finding: record it for its own hygiene item; do not mix that repair
into the argument gate.

## Next circuit — CORE-I-UNSUPPORTED-ARG-GATE (Mode C, REPAIR AUTHORIZED)

Target: Core I unsupported typed-argument refusal at the canonical
`executor.execute_seed` entry point.

1. Failing-first tests for all 50 unregistered Core I Dells across
   single-atom, chained, intercept, and live-identity paths.
2. Refuse per executing Core I atom, before mutation; never reject
   a mixed chain merely because its primary Dell is Core I.
3. Preserve Dell 8's registered contract, all valid Core II typed
   calls, and legitimate label-only execution.
4. UNSUPPORTED_ARGS with sorted role names only; no raw values in
   new diagnostics.
5. Preserve FlowTo, FlowThru, skipped-atom, ManifestSet, and
   chainlink behavior.
6. Amend AF-1 check 7 under this ruling: refusal parity replaces
   silent-success parity.
7. Typed-signature count stays 17; no new signatures.
8. Prove no mutation by refused atoms; honest receipts.
9. Defect-restoring mutants; forward/twice/reverse regression;
   exact-head CI; fresh-clone verification.
10. Submit the implementation PR unmerged with durable evidence.

Required adversarial regression: mixed chains containing a Core I
atom and a valid typed Core II atom must not suffer whole-chain
rejection. STOP: Director certification required before merge.

## Adjacent queue

- Record Dell 37's invisible REPL error for separate hygiene repair.
- Review the English Intent.args channel independently; do not
  treat it as SeedAtom.args.
- Proceed to Track D Plane-to-Idea bridge planning after the
  bounded Core I repair.
- Preserve DAF-09 WITHHELD and whole-program NOT CERTIFIED.

Executed: PR #256 merged as db61de0; report and evidence bundle
byte-identical on merged main (verified by path-restricted diff).
