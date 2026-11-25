# DIRECTOR RULING — D1-UNSUPPORTED-ARG-GATE

Date: 2026-11-03
Mode: D — CERTIFY
PR: #253
Certified HEAD: 3a05835468b500f64e6d44414a2c21898f1584e9
Certified TREE: caf010fe034ee622ec128fe15cf743aac14124a7

RULING: **CERTIFIED WITH NOTED BOUNDARIES — MERGE AUTHORIZED.**

## Independent verification (Director, at the final commit)

| Check | Result |
|---|---|
| PR status | Open, mergeable, clean |
| Python 3.10 / 3.11 | PASS |
| New unsupported-argument suite | 45/45 |
| Dell 52/53 regression | 28/28 |
| Core I AF-1 compatibility | 13/13 |
| Complete regression | 225/225 forward, repeated forward, and reverse |
| Final candidate tree | caf010fe034ee622ec128fe15cf743aac14124a7 |

These results come from the completed GitHub Actions execution at the
final PR head.

The patch is confined to the Core II chain executor, a new test suite,
regression registration, and evidence documentation. It introduces no
new typed signatures, parser changes, or Core I behavior changes.

## Evidence reconciliation

I independently recomputed the SHA-256 digests of all 16 evidence files
in PR #253. Every digest matches the published manifest. I also
inspected the failing-first, mutant, regression, and fresh-clone logs.

The evidence supports the reported progression: 21/45 against the
original executor, 45/45 after repair, and all five defect-restoring
mutants killed.

## Certified behavior

- All 33 unsupported Core II Dells refuse typed arguments before
  handler execution.
- Registered typed Dells preserve existing validation behavior.
- Refused control heads cannot execute their bodies.
- Join preserves truthful failure accounting and prior errors.
- Legal legacy calls and Core I compatibility remain intact.

## Certification boundaries

Zero mutation applies to the refused atom's business state, not to
diagnostic/frame bookkeeping or later atoms legitimately executed by
FlowTo. Raw argument values are excluded from new refusal diagnostics,
but the existing seed echo still reproduces the caller's input. That
is not a general secrecy guarantee.

## Answers to Uni's questions

**Q1 — Canary/seed echo: APPROVED WITH BOUNDARY.** The names-only
amendment governs newly generated refusal diagnostics. The universal
seed echo is preexisting behavior. Any broader redaction requirement
belongs in a separate security review.

**Q2 — Refused-head frame publication: APPROVED.** Preserve a failed
frame with zero body iterations, honest skip receipts, and Join
closure that retains the error.

**Q3 — Sequencing: CONFIRMED.** Studio security and real-browser
acceptance remains the next priority. Do not restart that
already-running circuit. Core I contract review follows;
Plane-to-Idea bridge planning remains subsequent.

## Execution order

1. Confirm PR #253 still points to the certified head and exact-head
   CI remains successful.
2. Merge normally.
3. Verify the merge tree equals the certified candidate tree.
4. Run post-merge regression on merged main and report its terminal
   verdict.
5. Archive this Director ruling and update INDEX without modifying
   historical reports.
6. Continue the Studio security/browser circuit already in progress.
   No duplicate launch.

## Retained boundaries

Core I unsupported arguments, flow_executor, universal seed-echo
redaction, DAF-09 session-escape, and whole-program certification
remain outside this certificate.

Result: The unsupported Core II typed-argument defect is certified as
repaired within the tested execution paths. The next Director review
target is the Studio security and browser-acceptance packet.
