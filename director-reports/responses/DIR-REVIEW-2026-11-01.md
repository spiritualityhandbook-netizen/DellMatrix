# DIR-REVIEW-2026-11-01 — incremental product rulings

Director; 2026-11-01. Mode D: read, independently probe and rule. No production code changed. Discovery freeze: main `ea44bb8cc69be26278695c841380b7b7f0d6db99`. These are bounded engineering certificates, not guarantees of universal correctness or whole-program completion.

## Evidence and identity

[Exact candidate/merge identities and equal trees](../workflow/evidence/identities.json) were checked with Git objects for all five submissions. [GitHub observations](../workflow/evidence/ci-observations.json) independently show both required workflows completed SUCCESS when queried by each candidate SHA. Pre-merge timing, mutant results, full regression and fresh-clone runs remain Uni's reported evidence; they were not independently repeated in this review. No unavailable scanner is counted as PASS.

Director executed:

- At `87be4de`: DAF09 19/22; step5b 21/21; step5 boundary 20/20; AF34 counters 19/19; repair_r4 16/16. Source inspected for journal, compensation and load recovery.
- At clean detached `ea44bb8`: step6 34/34, step7 28/28, step8 22/22. These are current-descendant observations, not falsely labeled exact historical-candidate executions. Relevant implementation changes and question contracts were read.
- Additional boundary probes at `ea44bb8`: failed journal deletion receipt, Unicode Loop count, consecutive Catch. Reproducer and raw observations are [published here](../workflow/evidence/review_probes.py), [output here](../workflow/evidence/boundary-probes.log). These probes are independent additions to the submitted suites.
- Raw suite outputs: [DAF09](../workflow/evidence/daf09.log), [step5b](../workflow/evidence/step5b.log), [step6](../workflow/evidence/step6.log), [step7](../workflow/evidence/step7.log), [step8](../workflow/evidence/step8.log).

## Step 5b / DAF-06 / A1

**DAF-06: CERTIFIED WITH NOTED EXCEPTIONS. A1 Exchange: CERTIFIED WITH NOTED EXCEPTIONS as repaired at `484453f`, independently exercised at `87be4de`.** This does not retroactively certify the defective original #117 tree. Supported scope: validated bounded packets, original payload and receipts preserved, capacity admission, failed final save not returned as success, failed compensation retained, and journaled restart resolving partial imports before exposure. Prior DAF-04/05 and #125 bounded certificates remain applicable within their scopes.

**DIR-F12 (P2), OPEN — journal-deletion reporting.** `_clear_import_journal` returns False on unlink failure, but `_fail_import` ignores it and reports `journal_retained=False` after complete compensation. The independent injected deletion-failure probe reproduces this exact false receipt. Recovery's completed/removed/already_absent/no_target exits and successful import also ignore deletion outcome; those exits are SOURCE observations, not independently injected end-to-end claims.

Exception: journal disposal/retention reporting on deletion failure is not certified. Durable compensation success and journal disposal are separate facts. Uni: keep verified compensation complete when true, but report the actual retained journal, preserve retry/recovery visibility, and do not claim successful disposal when unlink fails. Add real-file unlink-failure witnesses covering failure compensation, successful landing, and restart; restored unlink must permit a safe retry. Keep a single journal owner. Do not remove durable data simply to make this bookkeeping check green.

Other exceptions remain: single-owner/single-flight operation; native/reconstructed provenance honestly labeled; historical damaged imports not reconstructed; counted non-live eviction is not undone; no true multi-machine, hostile-filesystem, universal crash-timing or distributed-transaction proof. A2 and whole-program closure remain pending.

## DAF-09 pidfd hardening

**PARTIAL: safe refusal/no numeric fallback mechanism accepted within its tested controls; session-escape certificate WITHHELD at `87be4de`.** Cancellation's existing bounded certificate is unchanged.

Independent result: **19/22**, versus submitted 22/22. Failures: escaping grandchild post-timeout marker; identity positive control (`kill_report=refused`); pidfd-failure unavailable-report control (`refused: [(22, None)]`, unavailable empty). Raw output is retained. The pidfd-open non-signalling control passed. Do not call this a newly demonstrated unsafe numeric fallback: that fallback is removed. Do not call the environment discrepancy resolved.

Uni next action: preserve the exact 22 checks; instrument identity acquisition at witness time and signal time, `/proc` visibility, namespace identity, reparenting, marker timestamps and the outcome path. Separate missing identity from changed identity and pidfd unavailability. Provide a minimal positive process fixture proving it is visible in the same namespace as the observer before judging cleanup. A direct self-starttime probe succeeds here; that alone does not establish descendant visibility. Classify unsupported environments explicitly; no blind sleeps or unsafe numeric fallback. Do not change a failed cleanup assertion into a pass. Continue independent authorized circuits while this bounded investigation remains open.

## Step 6 leaf honesty

**PARTIALLY CERTIFIED at `2059d6a`, observed at `ea44bb8`.** B1 Decay, B3 Merge, B4 Split and B6 empty Translate are certified within the submitted contracts. B2's ordinary decimal 1..5 clamping is supported; complete malformed-count handling is declined.

**DIR-F13 (P2), OPEN — Loop Unicode digit exception.** Public input `13[Loop] :: ²` raises `ValueError` instead of an honest refusal. `str.isdigit()` accepts characters that `int()` cannot parse. Uni: define accepted count grammar, parse/refuse safely before growth, avoid unbounded conversion for huge counts, and test superscript digits, accepted decimal digits, malformed text and oversized decimal strings. Refusal must execute zero cycles and leave the program usable; preserve ordinary clamping and count receipts. This is a contract gap found in current code, not a claim that this patch introduced it.

## Step 7 control verdicts

**CERTIFIED WITH NOTED EXCEPTIONS at `625bb69`, observed at `ea44bb8`: B7, B8, B9 and DAF-08 within the submitted control/receipt contracts.** Source inspection and the 28/28 independent suite support actual-result Join evaluation, bounded Until empty-condition agreement, empty ForEach, and explicit skipped occurrences. Arbitrary nesting/composition completeness remains for the planned pairwise and symbiosis work, not this certificate.

Q1: ACCEPT `partial` as occurrence-level incompleteness (omission OR failure), with `ok` the separate success verdict. Consumers must not infer failure from partial alone.

Q2: ACCEPT an empty executed child set as a successful Join under both current policies, with skipped children still visible. This is a deliberate **Join policy**, not existential Any's Boolean rule and not evidence that a child succeeded. Preserve `Any(empty)=False`. State the distinction in step 11 wording; retain the empty/skipped-positive controls. No code change requested by these two answers.

## Step 8 transactions

**PARTIALLY CERTIFIED at `1607f33`, observed at `ea44bb8`.** B15 innermost failed-frame marking and root-cause preservation certified within the tested entry paths. B17 mark/accept mechanism and 93/94/95 wording accepted within the declared checkpoint field set; remaining public-surface reconciliation stays step 11. B16 frame ownership and isolation from pre-Try global errors supported; full consumption contract declined.

**DIR-F14 (P2), OPEN — consumed Catch error can be consumed again.** `Try; Delete absent; Catch; Catch` reports `Catch delete_missing:absent` twice. `caught_error` is archival evidence, but `frame.error` retains the consumed error and the next Catch treats it as pending. Uni: explicitly distinguish pending from consumed error; a second Catch with no new failure reports no error and preserves caught history. New post-Catch failure becomes a new pending root cause; nested isolation, failed-Commit evidence, and commit eligibility must remain correct. Test repeated Catch, new failure after Catch, and nested frames through direct and chain paths.

Q1: ACCEPT a new post-Catch failure as a new root cause; it must not erase the prior caught evidence. Q2: ACCEPT the requested bounded wording scope; cross-surface wording remains step 11.

## Ordered handoff

1. Acknowledge this response and DIR-WF-001; update INDEX and the findings register without rewriting original submissions.
2. Record DIR-F12/F13/F14 with owner Uni and the exact reproducers above. Apply a bounded failure matrix and consumer/sequel probe before each repair. Use separate mechanism circuits or explain an evidence-preserving grouping.
3. DAF-09 remains a discriminating-environment investigation, not a proven universal code defect. Capture evidence rather than repeat the same 22/22 claim.
4. Continue already-authorized independent steps 9–11. New repair closures must land before the final repaired freeze and step 13 re-derivation.
5. Re-present only changed claims; preserve unaffected certificates. A2, full-registry composition and whole-program certification remain pending the reconciled final packet.
