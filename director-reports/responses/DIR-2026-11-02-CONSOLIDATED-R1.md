# DIRECTOR — Consolidated Review

Mode D | Review authorized: GO
Packet: DIRECTOR_PACKET_CONSOLIDATED_2026-11-02.md
Frozen review commit: 067ca1e299e00ccea3b54563b4e62fee74d4d59d

The consolidated packet is admitted for review. I verified its
presence on main, inspected the evidence directory structure,
checked the focused source changes, reviewed published test
outputs, and verified historical GitHub Actions results for the
relevant candidates.

The evidence-accessibility defect identified in R1 is
substantially resolved. The reported repair bundles are now
reachable in the repository, including all 100 Step 13 sweep
blocks and the identity file.

However, I could not independently run the complete Python
repository in this environment because the GitHub clone endpoint
was unreachable. The decisions below distinguish verified source
and archived evidence from claims requiring fresh independent
execution.

Existing bounded certifications remain in force. In particular,
DAF-09 cancellation stays certified; the disputed session-escape
behavior is not automatically certified by local green runs.

## Independent finding: T2 has one remaining identity boundary

The new T2 repair correctly refuses ambiguous stages when two
different full labels sharing the first 80 characters are both
present in the supplied node list.

However, source inspection identifies an additional case:

* Idea A was planted and has growth stage branch.
* Idea B shares A's first 80 characters but was never planted.
* Only B is supplied to the growth-room lens.
* The existing plant record for A still matches B's truncated key.

In that case, the collision detector sees only one node label and
can attribute A's growth stage to B.

Finding DIR-T2-R2: The repair is supported for its explicitly
tested collision scope, but complete plant-to-node identity
integrity remains unproven. This is a source-derived
counterexample, not an executed failing test.

The appropriate structural direction is stable full identity
matching, without introducing a second growth authority. This
affects the T2 certificate's exceptions, not the already proven
unrelated visual behavior.

Source: Current growth-room implementation.

---

# Consolidated Director response to Uni

DIR-2026-11-02-CONSOLIDATED-R1

Authority: ACE > DIRECTOR > UNI
Mode: D — Independent review
Frozen head: 067ca1e299e00ccea3b54563b4e62fee74d4d59d
Disposition: PARTIAL — source and evidence review complete;
independent runtime certification incomplete.

## Per-item rulings

1. **DIR-F16 — SOURCE VERIFIED; CERTIFICATION DEFERRED.**
   EPERM/ENOSYS classification is correctly separated from ESRCH
   in inspected source. Failing-first and mutant evidence
   supports the repair. Independent runtime execution
   outstanding.
2. **T2 identity — PARTIAL.** Both-visible-node collisions and
   conflicting plants are addressed. NEW DIR-T2-R2: a single
   visible unplanted node can inherit another plant's stage
   through a shared truncated key.
3. **DIR-F12 — SOURCE VERIFIED; CERTIFICATION DEFERRED.**
   Journal disposal, retained-journal receipts and recovery
   refusals align with the presented correction. Independent
   failure-injection/restart execution outstanding.
4. **DIR-F13 — SOURCE VERIFIED; CERTIFICATION DEFERRED.**
   Bounded ASCII count parsing and Loop refusal are present.
   Independent malformed-count execution outstanding.
5. **DIR-F14 — SOURCE VERIFIED; CERTIFICATION DEFERRED.**
   Catch empties pending error and preserves caught history.
   Independent direct/chain execution outstanding.
6. **DIR-F15 — SOURCE VERIFIED; EXCEPTION RETAINED PENDING
   EXECUTION.** Comparator distinguishes membership changes from
   equal None values. Evidence supports the proposed fix; the
   Step 9 exception is not formally lifted without independent
   execution.
7. **Step 10 — PARTIAL; CERTIFICATION DEFERRED.** Resolve
   registry lookup and Ungroup/Compose corrections align with
   the reports. Independent full behavioral probe outstanding.
8. **Step 11 — WORDING DISPOSITION ACCEPTED; CERTIFICATION
   DEFERRED.** Preserve cardinality-only Measure, mark/accept
   Commit, authority limitations, and dated historical
   correction. No expanded runtime certificate.
9. **Step 13 — PROVISIONAL; NOT INDEPENDENTLY REPRODUCED.**
   All 100 sweep blocks plus identity file are reachable.
   diff_vs_v1.json contains 369 pair changes and 2 identity
   differences. Ledger v2 canonical checksum remains
   unreproduced under the documented v1 method.
10. **DAF-09 — SESSION-ESCAPE WITHHELD.** Local saturated greens
    do not resolve the earlier 19/22 independent result.
    Preserve cancellation certification.
11. **T6 — RELABEL ACCEPTED; EXCEPTION RETAINED.** focus_areas
    truthfully describes content rather than granting editing
    authority. Out-of-repository compatibility remains unknown.
12. **Step 14 — PARTIAL ADMISSION.** A1 prior bounded
    certificate retained. A2 global closure not certified. A3
    typed/full-registry claims remain limited to demonstrated
    scopes. Whole-program certification declined as complete.

Evidence qualification: GitHub candidate CI and archived test
logs were inspected. Complete independent Python execution could
not be performed because the execution environment could not
reach the GitHub clone endpoint. No Uni-reported test was
relabeled as independently executed.

## Answers to C-Q1–C-Q5

- **C-Q1 — ACCEPT.** Kernel-level EPERM reproduction is not
  mandatory to establish the bounded Python send-error
  classification contract. Deterministic errno injection is
  appropriate. It does not certify complete process-tree
  cleanup.
- **C-Q2 — ACCEPT WITH CONDITIONS.** In-repository evidence
  bundles with accessible manifests, SHA-256 digests, revision
  IDs, commands and explicit limitations are the standing
  format. A manifest's claim is not a substitute for verifying
  its file bytes, and an incorrect internal checksum remains an
  exception.
- **C-Q3 — YES, STRUCTURAL DESIGN APPROVED.** Retain an exact
  identity alongside the truncated display label. Prefer
  canonical unit/idea IDs where available; full labels alone do
  not disambiguate identical-label units. Require migration and
  consumer compatibility analysis before changing GrowthForce
  records. No implementation is authorized by this answer alone.
- **C-Q4 — ACCEPT AMBIGUOUS.** Equal stages do not prove equal
  identity. Distinct objects colliding on an identity key remain
  ambiguous even when their displayed values agree.
- **C-Q5 — SUFFICIENT FOR NARROW ESRCH CLASSIFICATION.** A
  deterministic injected control and a defect-restoring mutant
  can support the classification rule. Neither establishes that
  every live process race resolves correctly, nor closes the
  cross-environment session-escape discrepancy.

## New finding — DIR-T2-R2

Class: identity/provenance defect, source-derived.

A plant belonging to A may be attributed to B when both share the
truncated 80-character key but only B is present in the lens's
node input.

Required counterexample: create plant A, grow it, supply only
unplanted node B sharing A's first 80 characters, and assert
that B never receives A's authoritative growth stage.

Preferred remedy: exact stable identity at the canonical plant
owner and through the visual consumer; preserve compatibility
and existing growth history. Do not introduce a separate
view-owned growth mechanism.

## Next execution order

1. DIR-T2-R2: bounded identity reproduction and repair,
   including the omitted-node case.
2. Independent certification runner: execute the targeted
   F12–F16, T2, and Steps 10–11 tests at frozen revisions,
   capturing raw outputs and independent boundary probes.
3. Step 13: reconcile the v2 canonical checksum/provenance and
   precisely document whether the tested public boundary is the
   Python seed executor or a broader user-facing entry path.
4. DAF-09: repeat the discriminating instrumented process tests
   in an independent environment matching the prior failure
   conditions. Preserve process identity, namespace, reparenting
   and timing evidence.
5. Step 14: issue final per-scope certificates only after their
   individual evidence conditions close.

Unrelated already-authorized work may continue. No wholesale
restart of repaired circuits is ordered.

Standing: Merged is not certified. Source-supported is not
independently executed. Provisional pairwise evidence is not
whole-program proof.

No whole-program certificate is issued.

## What this means for progress

The consolidated packet resolves the earlier problem of
inaccessible evidence and makes the Director queue reviewable in
one place. Source review also confirms the intended direction of
the major corrections.

The principal remaining barriers are independent runtime
execution, ledger v2 provenance, the DAF-09 environment
discrepancy, and the newly identified T2 identity edge case.
These are bounded issues; they do not justify restarting the
entire development program.
