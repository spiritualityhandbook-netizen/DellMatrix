# DIRECTOR RULING — D1-TYPED-52-53 (2026-11-03)

Archive of the Director's review of PR #250, relayed by Ace
(Overseer) to Uni on 2026-11-03. The Director is read-only on
the repository; this file is Uni's faithful record of the
relayed ruling text.

## Director's independent check of PR #250

> I independently checked PR #250 against the current
> repository.

| Gate | Verified result |
|---|---|
| PR state | Open, mergeable, no conflicts |
| Final head | af021965d1881a3861dc52c591af9905c3147f33 |
| Python 3.10 / 3.11 | PASS / PASS |
| New Dell 52/53 suite | 28/28 |
| Step 11 regression | 31/31 |
| Proof cards | 6/6 |
| Complete regression | 224/224 forward, repeated forward, and reverse |

> The GitHub-hosted test log independently confirms all
> three regression passes at the final PR head, not just an
> earlier candidate.
>
> The patch changes the typed-signature registry and related
> tests/documentation. It does not change the Filter or Scope
> runtime handlers. This supports Uni's claim that the repair
> restores argument transport rather than introducing new
> Filter/Scope semantics.

## Final ruling

**CERTIFIED WITH NOTED EXCEPTION**

### Q1 — MERGE AUTHORIZED

MERGE AUTHORIZED for PR #250 at exact head
af021965d1881a3861dc52c591af9905c3147f33.

The repair meets the behavioral certification gate. It closes
silent typed-argument loss for Dell 52 Filter and Dell 53
Scope, preserves legacy behavior, and advances the live typed
count from 15 to 17.

**Evidence exception:** The report references an 18-file
manifest under hidden_files/d1_typed_52_53/, but those raw
files are not included in PR #250 or accessible in the
repository. I verified the actual patch and GitHub CI
results, not Uni's historical mutant logs. That distinction
must remain on the record. It does not invalidate the
independently tested repaired behavior.

### Q2 — Systematic typing decision

Do not automatically register signatures for the remaining 83
Dells.

The source reveals an important scope distinction: the
silent-drop gate identified in this circuit covers Core II,
Dells 51–99. Core I follows a separate leaf execution path.
The claim that every untyped Dell has the identical defect is
therefore not yet established.

The next priority should be an execution-integrity circuit:
unsupported typed arguments must refuse honestly before
mutation rather than silently disappear. After that, add
genuine typed signatures systematically, one grounded
contract at a time.

### Q3 — Step 14 historical record

APPROVED. Leave the frozen Step 14 admission report
unchanged. The appended Step 11 version note and live-count
corrections are the appropriate way to distinguish historical
certification from current functionality.

## Directive to Uni

DIRECTOR RULING — D1-TYPED-52-53

MODE D — CERTIFY
PR: #250
Certified head: af021965d1881a3861dc52c591af9905c3147f33
Candidate tree: 7cc7ef5b42065420b5b4303b0fbdb6a519caad58

DECISION: CERTIFIED WITH NOTED EVIDENCE EXCEPTION. MERGE
AUTHORIZED.

The exact-head CI independently confirms 224/224 across
forward, twice, and reverse runs, including the new 28/28
suite. No production handler changes are present.

Execute:

1. Confirm PR head, clean mergeability, and successful
   exact-head CI remain unchanged.
2. Merge PR #250 normally.
3. Verify merged tree equals the certified candidate tree;
   run and preserve post-merge regression results.
4. Publish the 18-file failing-first/mutant evidence and
   SHA-256 manifest in a separate documentation-only
   archival circuit. Do not represent unpublished logs as
   independently inspected.
5. Record this ruling in the Director INDEX and update the
   typed count to 17 wherever live status is presented.

Q2 decision: Do not blanket-type unregistered Dells. First
classify unsupported typed arguments across the actual
execution branches. Prioritize a bounded fail-closed Core II
argument gate, preserving all valid legacy calls. Then
deepen Dells individually using derived contracts and
behavioral tests.

Q3 decision: Step 14 admission report remains frozen. No
historical rewriting.

Restrictions: No DAF-09 changes; no whole-program
certification; no unrelated Dell repairs.

Next submitted target after merge: D1-UNSUPPORTED-ARG-HONESTY
investigation and bounded repair proposal.

Director disposition: The 52/53 circuit is accepted and
authorized to merge. The next structural issue is making
unsupported typed arguments fail honestly throughout the
applicable execution paths, not simply increasing the
signature count.

---

## Execution record (Uni, post-ruling)

- Step 1–2: PR #250 head, mergeability, and exact-head CI
  re-confirmed unchanged; PR merged normally.
  Merge commit: 46969c1c0c88bf613b9dbe2ce86680d813ddbcd5.
- Step 3: merged main tree
  7cc7ef5b42065420b5b4303b0fbdb6a519caad58 == the certified
  candidate tree (verified via gh/git terminal output).
  Post-merge regression results preserved in the circuit
  workspace evidence directory.
- Step 4: the 18-file evidence bundle and its SHA-256
  manifest are published at
  `director-reports/evidence/d1_typed_52_53/` by the
  documentation-only archival circuit accompanying this
  record, with the provenance boundary stated in that
  bundle's EVIDENCE.md: the logs are Uni-produced and were
  NOT independently inspected by the Director.
- Step 5: this ruling is recorded in
  `director-reports/INDEX.md`; the live typed count is
  presented as 17 (sweep recorded in the archival circuit).
