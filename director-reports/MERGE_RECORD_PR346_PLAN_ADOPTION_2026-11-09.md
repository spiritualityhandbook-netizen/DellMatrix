# MERGE RECORD — PR #346: SS14 plan adoption (docs-only, Director scoped exception)

Date: 2026-11-09 (CST). Actor: Uni, main session (coordinated
execution/merge owner). Authority: DIR-SLEEP-V3-R2 (Ace grant,
2026-11-09) + Director Decision 1, ruling of 2026-11-09 19:07 CST
(Gmail 1a1c2ff67f44310b) — #346 DOCS-ONLY EXCEPTION, SCOPED
AUTHORIZATION.

## Requirement
Adopt the SS14 working-plan candidate (second evolution folding
DIR-PLAN-E2-2026-11-09) as the program plan under the SS13.7
protocol, step 5 reconciliation. Director verified the published
revision and diff, accepted all four Uni refinements, and approved
adoption.

## Candidate and merge identity
- Base: 7aad1912d4530dc10afc9b82c5d7f41af849c19b (main at merge;
  re-verified against origin/main in the merge step).
- Head: 1db852a89dac056e42fea3d28b528e3d64b5bc39 (exact, unchanged).
- Diff: ONE file — director-reports/ACE_FUTURE_DEVELOPMENT_PLAN.md
  (+803/-4; 799 net added lines including four in-place
  replacements). No executable code changes.
- Merge: PR #346 MERGED as 6e7860538054a005f3383779d0ab99c08f5b20c8.

## Checks and failed attempts
- Python package (build 3.10 + 3.11), run 42723652663: SUCCESS.
- Form smoke, run 42723652972: FAILURE on both attempts; sole red
  form.dd31_sanitize_copula_test (20/21 NOT_RETURNED_TRUE).
  - Attempt 1, job 129523638242: pass 1 RED 262/263 AND pass 2 RED
    262/263 (dd31 20/21 both passes).
  - Attempt 2, job 129531946563: pass 1 GREEN 263/263; pass 2 RED
    262/263 (dd31 20/21).
  The specific failed assertion was NOT printed in the CI summary
  (harness retains only each suite's last line); recorded as an
  evidence limitation, not reconstructed.
- Resolution: Director Decision 1 exception (below). The smoke is
  NOT converted to GREEN by this record or by the merge.

## Exception (Director Decision 1, scoped)
Rationale (Director's): the candidate changes documentation only;
the DD31 runtime failure also appears on a separate runtime
candidate (PR #345 tree) and on delivered main, so no plausible
change path exists from this plan text into DD31 execution.
Residual risk: the underlying DD31 second-pass failure is
unresolved, and existing main may be affected. Scope: ONLY this
one Markdown plan at this reviewed head. The exception does not
validate DD31, authorize runtime code merges, or certify broader
product behavior.

## Mail freshness (SS32 receipt)
Pre-merge triage executed 2026-11-10T01:10:55Z immediately before
the merge; newest Director mail = the 19:07 CST R2 ruling itself
(Gmail 1a1c2ff67f44310b); no contrary or newer ruling existed.

## Uni-reported vs independently checked evidence
- Uni-reported: the SS14 candidate's contents, the diff totals,
  the flicker datapoints (including the local reproduction and
  the 19:07 CST instrumented non-reproduction, 264/264 both
  passes on the DD-14 candidate tree).
- Independently checked by the Director: GitHub state of #344,
  #346, #345; both smoke attempt transcripts for run 42723652972;
  the DD31 failure's independence from #345's code.

## Remaining limitations and standing dispositions
- DD31-CI-INTERMITTENT: OPEN, mechanism UNKNOWN; now a named
  reliability circuit (capture/classify; FIX-FIRST if a non-gated
  defect is reproduced; otherwise bounded disposition request).
- PR #345 (DD-45 runtime code): REMAINS MERGE HOLD (Decision 2);
  no waiver; a green rerun alone cannot certify it.
- Strict completion: 19/72 unchanged. SS14 is now the working
  plan. DAF-09 and whole-program certification remain withheld.
- Merged-main smoke after this merge: NOT claimed here; it runs
  under its own workflow and is reported from its own terminal
  output when observed.
