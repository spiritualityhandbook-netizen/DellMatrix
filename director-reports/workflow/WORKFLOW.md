# DellMatrix three-role workflow — v1

Decision ID: DIR-WF-001. Owner: Director. Authorized by Ace's request to implement the refined Director / Uni / Overseer workflow. Effective as a project directive on delivery; repository tooling becomes available at this change's branch/commit and on main after normal merge. This is process tooling, not a DellMatrix runtime permission grant.

**Objective:** maximize useful, verified progress across Mandell, DellMatrix and DuoBeta while reducing rework, idle handoffs and false closure. The optimization target is accepted behavior and truthful evidence, not more reports, tests, agents, or passes. No workflow can guarantee zero bugs; this one makes failures visible, bounded, recoverable and instructive.

## Start here — three short contracts

| Role | Owns | Must deliver | Must not do |
|---|---|---|---|
| Ace / Overseer | Purpose, priorities, authority envelope, resources, major product tradeoffs | A priority or changed constraint when needed; resolve genuine authority conflicts | Carry full packets repeatedly, arbitrate routine implementation, or be asked again for already-authorized work |
| Uni / Architect and implementer | Architecture within approved contracts; production code, tests, repair, CI, merge and publication | One bounded circuit, evidence packet, accessible report and INDEX update; acknowledgment of Director ruling | Self-certify, hide side effects, weaken tests to preserve a defect, silently expand authority |
| Director / independent reviewer | Contract rulings, independent probes, certification scope, process quality and review queue | A version-bound ruling with evidence, exceptions and next action; publish it in this channel when able | Equate green CI with correctness, silently expand scope, turn hypotheses into causes, or claim background work that did not run |

Ace > Director > Uni remains the project authority chain. The runtime's scoped DirectorSession only recommends; AcceptancePolicy remains the sole runtime acceptance owner. Persona, BIMO, workflow status and swarm opinion confer no runtime permissions. AUTONOMY=NO means no new authority; it does not prohibit execution of Ace's already-authorized queue.

Director may write governance documents and process tools under `director-reports/` for this authorized circuit. Uni remains the production-code writer. No changes to runtime, credentials, repository permissions, rulesets or historical swarm infrastructure are included here.

## The operating loop (ten gates, not 100 recurring forms)

1. **Discover once.** Fetch main INDEX and explicitly advertised report branches. Freeze the report commit and runtime SHA/tree. Review unacknowledged deltas only. A pending report PR is readable but must be labeled branch-only; it is not a merge.
2. **Choose one circuit.** Name problem, intended user-visible behavior, owner, dependency, authority reference and exclusions. Uni has one active production implementation circuit; Director one active review. While CI or review waits, prepare an independent already-authorized next circuit without editing the same ownership boundary concurrently. No unbounded review backlog: after two ready unreviewed circuits, help clear evidence/diagnostics before starting another implementation; Ace may explicitly adjust this operating limit.
3. **Map the affected paths.** List public entry points, canonical handlers, mutable owners, persistence boundaries and consumers. Label touched fields executable, durable, detached evidence, or presentation. Include the next consumer and restart boundary. Do not rebuild the entire system map for an unchanged path.
4. **Challenge the design before implementation.** Four lenses: Custodian (state/recovery), Interpreter (meaning/composition), Sentinel (authority/disclosure), Mechanic (resources/reproducibility). Each contributes a concrete attack, expected observable oracle and scope. These may be separate available agents or explicitly labeled sequential perspectives. Record actual execution and dissent; never fabricate independence. Unanimity is neither necessary nor sufficient. Unresolved material counterexamples block the implicated claim, not unrelated work.
5. **Implement and falsify locally.** Reproduce the old defect, repair in the canonical owner, prove the positive/refusal paths and whole affected-state diff, then test a sequel consumer. Stateful circuits require forward-write and compensation-failure combinations, journal/read/clear failures where applicable, restart and retry. Use synthetic state and protected cleanup. Mutation checks restore the defect; failure must occur for the right assertion. A surviving mutant means improve the test or explain equivalent/non-applicable behavior, never call it killed.
6. **Freeze and reconcile claims.** Every behavioral claim names exact revision, assertion, command, evidence class and reachable artifact. UNKNOWN is valid. Tests pinning bad behavior are observations, not certificates. Separate lint from behavior. Map code changes to docs and limitation records; append dated corrections to history rather than rewriting it.
7. **Integrate under standing gates.** Keep the established runtime gates: full forward, twice, reverse on frozen candidate; exact-head required CI complete and inspected in a separate step before merge; normal merge with candidate-tree equality; fresh-clone verification. During edits use targeted checks first. Reuse valid immutable evidence; repeat full gates only when candidate content, relevant dependency/environment, failure or new concern requires it. Pure report/process changes need applicable validation plus existing required CI; do not claim they prove runtime behavior. Do not change GitHub rulesets or skip currently required checks to accelerate this lane.
8. **Publish an accessible submission.** Commit report and INDEX entry together. Include runtime SHA/tree separately from report SHA. Put requested ruling, exceptions and claim matrix before logs. Use the packet template and validator. Exact-head CI may belong to a different runtime commit than a later docs-only report commit; name both. Report-local paths alone are not evidence access. Use committed logs or immutable reachable artifact links, with digests and retention plans.
9. **Review, rule, acknowledge.** Director reads the delta, executes relevant original counterexamples plus at least one independent boundary probe for substantive changes, and rules CERTIFIED / CERTIFIED_WITH_EXCEPTIONS / PARTIAL / DECLINED / UNAVAILABLE. Distinguish environment failure from demonstrated product defect. Publish a response ID bound to report ID, SHA/tree, claims and exceptions. Uni acknowledges within the next work cycle, cites the response, updates current INDEX status, and maps each required change to a follow-up. Replays of the same response are no-ops. Chat is a fallback transport, not the only durable record.
10. **Learn and continue.** Every returned defect records missed assumption → actual mechanism → guard/test change → owner → closure witness → recurrence check. Prioritize the implicated repair; continue independent authorized work. Review process cost every five closed circuits or after a repeated defect class. Remove redundant controls with a dated rationale; never remove a guard just because it turns red.

The 100-pass ledger is a one-time design refinement record for this workflow, not 100 required steps per circuit. Its gates are deliberately collapsed into these ten operations.

## Channel and status model

`director-reports/INDEX.md` is the discovery hub. Reports are immutable historical submissions; subsequent addenda/rulings are new records. The current INDEX can summarize the latest disposition while linking the earlier record. Workspace ledgers and local AGENTS instructions are mirrors, not inaccessible superior law. Uni's referenced workspace AGENTS §31 rules were not present in repository AGENTS.md; their operative principles are published here.

Keep three independent axes:

| Axis | Values | Meaning |
|---|---|---|
| Delivery | PLANNED / IMPLEMENTING / VERIFIED / MERGED | What was built and integrated |
| Review | NOT_SUBMITTED / SUBMITTED / IN_REVIEW / RULED / ACKNOWLEDGED | Where the handoff is |
| Certification | UNKNOWN / CERTIFIED / CERTIFIED_WITH_EXCEPTIONS / PARTIAL / DECLINED | Director's bounded judgment |

Merged-but-uncertified is valid. A new commit never silently inherits blanket certification. A previously certified subclaim is not reopened without a relevant change or counterexample. Review queue entries carry finding IDs; those are stable across report revisions. Use `supersedes` to connect revisions. No second runtime ledger or reactivation of `ops/swarm` is introduced.

Director writes replies under `director-reports/responses/` (one response per circuit/workflow decision), publishing via a normal branch/PR when able. Uni merges governance/report changes through current CI gates, acknowledges and updates INDEX. Director publication is not self-certification of its process code. Review that code independently before integration. This first workflow PR demonstrates the same rule.

There is no always-running Director or automatic cross-session invocation installed. Uni files per circuit, including overnight; Ace can trigger a review with **“Review Director INDEX.”** When tools are unavailable, deliver one portable response and exact target; do not invent an acknowledgment. An actual scheduler requires a separate explicit setup, not a sentence claiming polling.

## Evidence packet and executable preflight

Copy `packet-template.json`. Fill it; run:

```bash
python director-reports/workflow/validate_packet.py path/to/packet.json --gate submit
python director-reports/workflow/validate_packet.py path/to/packet.json --gate merge --repo .
python director-reports/workflow/validate_packet.py path/to/packet.json --gate close --repo .
python director-reports/workflow/test_validate_packet.py
```

The CLI rejects malformed identities, unsupported evidence claims, stale head associations, missing or non-success required CI, ungrounded certification fields, unresolved claimed fixes, inaccessible local-only references and false closure structure. `--repo` checks named Git objects and trees. A passing CLI means **packet consistency**, not truthful tests, authenticated authorship, GitHub protection, permission to merge, or certification. Evidence bytes, artifact accessibility, review identity, CI provider provenance and actual execution still require verification. JSON `actor: Director` and SHA-256 digests are assertions, not digital signatures.

The tool is implemented and tested in this workflow change. It is not yet a GitHub-required check. Uni must use it as a procedural preflight on new submissions. A future required-check integration is a separately reviewable hygiene change; it must not grant write privileges to untrusted PR code or relax existing gates. Historical packets are not retroactively failed for lacking new fields.

Runtime claim closure requires all relevant blockers resolved or explicitly excluded from the certified scope by the Director. Platform unavailability must not be renamed PASS. Required behavioral CI must actually succeed even if GitHub itself allows neutral/skipped results. Candidate change triggers evidence applicability review; it does not reset Ace's authorization to do the named work.

## System-specific review map

Read only the affected row and its consumers; the map is orientation, not a certificate. Source baseline for this workflow study: `87be4de`.

| System | Canonical source | Required boundary question |
|---|---|---|
| English / Mandell | `form/mandell/semantic_router.py`, `seed.py`, `executor.py`, `chain_exec.py` | Do raw, English and typed routes preserve operands, reject ambiguity and reach the same owner? |
| Dells / controls | `query_ops.py`, `spectrum_ops.py`, `control_runtime.py`, `core_ii_exec.py` | Does the next consumer see exact executable state? Do skip/failure/iteration receipts match occurrences? |
| Ideas / acceptance / lifecycle | `form/dell_matrix/acceptance_policy.py`, `confirm_lineage.py`, `faded_policy.py` | Does explicit authority bind this content at writer stages? Are denied/compensated and accepted states distinguishable? |
| Persistence / recovery | `form/persist_rest.py`, confirmation/checkpoint/recovery owners | Does restart expose only a verified result? Does evidence outlive failed compensation? |
| Exchange | `form/dell_matrix/exchange.py` | Are original payload, receipt provenance, capacity, eviction order, journal and restart behavior consistent? |
| Outcomes / DuoBeta | `form/mandell/execution_observer.py`, `outcome_ledger.py`, `duobeta_learn.py` | Is execution evidence separate from truth and permission? Can a receipt repair affect learning downstream? |
| Dock / BIMO / design loop | `inference_dock.py`, `dock_session.py`, `director_session.py`, `design_loop.py` | Does persona remain presentation, advice remain advice and proposal remain pending until canonical acceptance? |
| Internet / disclosure | `internet_gate.py`, `form/mandell/redaction.py` | Is each destination authorized before connection, each surface redacted without changing executable state? |
| Unknowns / limitations | `form/dell_matrix/unknowns.py`, `form/mandell/limitation_knowledge.py` | Is missing evidence visible? Is an old probe dated rather than represented as current? |
| Visuals | `form/mandell/flow_visual.py`, `form/dell_matrix/visual.py` | Does the display derive from truthful state/receipts and stay within the 2D presentation contract? |
| Verification infrastructure | `form/regress.py`, `.github/workflows/` | Are timeouts isolated, cleanup truthful, environment identified and CI correctly described? |

Unqualified filenames in a row share its named package. The full-registry proof catalogue is 100 Dells in the present repository; historical 51-Dell instructions do not erase current Core II. Typed-count statements must come from the frozen registry rather than memory. Standalone coverage is not pairwise coverage, and a finite pairwise fixture space is not all programs.

## Failure/discrepancy protocol

Freeze the failing revision and preserve logs; block only the affected claim. Record OS/kernel/architecture/Python, filesystem/mount where relevant, PID namespace and pidfd capability for process tests, command, timing, dependency versions, state fixtures and cleanup result. Never publish credentials or real secrets. Use synthetic markers.

For conflicting runs, keep both outcomes. Separate observed facts, plausible hypotheses and a discriminating experiment. Readiness/reparenting/termination must be witnessed; sleeps alone do not prove ordering. Changed fixtures must preserve the original assertion. A locally green rerun does not resolve a remote red. Director may certify a narrower independently supported scope while keeping the discrepant claim UNRESOLVED.

If a verified primitive is unavailable, do not downgrade silently to an unsafe primitive. Report cleanup outcome independently from the original failure. Persist recovery evidence before claiming compensation complete. Restoration must be observed after restart where durability is claimed. Historical non-live evictions or external side effects must remain disclosed even after successful local rollback.

Swarm disagreement does not trigger a new approval ritual. Uni owns routine reconciliation; Director decides contract ambiguity; Ace decides true product/authority tradeoffs. After two failed presentations of the same mechanism, stop polishing the same patch: perform a focused joint contract/owner review and a minimal reproducer before the next implementation. This is a redesign checkpoint, not a requirement for Ace to restart the work.

## Productivity and learning scorecard

Track: circuit start→submission→ruling→acknowledgment; active time versus CI/review wait; reopen rate; repeated failure class; duplicate-run reason; production contracts closed; and remaining scope at risk. First five closed circuits establish a baseline. No claimed percentage improvement before measurement. Do not rank people by test count or conceal defects to meet a clean-review target. Discovery of a real defect is useful progress when it produces a durable guard.

Improve one bottleneck at a time. Keep the short report short; append raw logs once and link them. Reuse artifact hashes and frozen evidence rather than copying giant reports. Bounded four-lens review is the default for state/authority changes; docs-only work uses relevant checks without staging a fake swarm. Full pair sweep happens at the planned repaired freeze, not after every edit.

## Rulings on Uni's personal report

Source: `director-reports/DIRECTOR_PERSONAL_REPORT_2026-10-31.md` on `uni/director-channel`, read during this circuit. That report is process input, not a certification submission.

| Item | Decision |
|---|---|
| P1 pre-mortem | ADOPT WITH AMENDMENT: distinct attacks/oracles and dissent; unanimity is not a truth gate. |
| P2 claim reconciliation | ADOPT: exact-head claim/assertion matrix; delete or downgrade unsupported claims. |
| P3 failure matrix | ADOPT PROPORTIONATELY: all relevant durable boundaries plus failed compensation, restart and retry for stateful circuits; no invented persistence tests for prose-only changes. |
| P4 environment disclosure | ADOPT: sensitivity and repetition count; unresolved conflicts stay unresolved until discriminated. |
| Q1 step 6 completeness | Existing B1/B2/B3/B4/B6 contracts are the minimum. Add positive/refused state agreement and reload wherever those operations persist; no undisclosed expanded product behavior. |
| Q2 report shape | YES: requested ruling/identity/exceptions first, then claims, anticipated probes, questions and artifact links. Ask only questions that unblock a decision; default routine choices to Uni. |
| Q3 step 13 | FULL 9,900 ordered-pair re-derivation at the final repaired freeze, diff against historical ledger, reachable raw artifact, fixtures/oracles and classifications. Targeted reruns during repair are useful but not a replacement. Reuse the established plan, do not invent universal correctness. |
| Q4 overnight | Keep per-circuit filing. Execute already-authorized independent work; no claim of automatic Director polling or certification during absence. |

## Initiation / current handoff

This workflow circuit does not rule on newly submitted product repairs. Initial study froze at 87be4de. The final discovery refresh found main ea44bb8 and new steps 6–8. Their separate dispositions are in responses/DIR-REVIEW-2026-11-01.md; this workflow does not replace those rulings or reopen unrelated certificates.

Uni: review and merge this process-only PR through existing required CI, acknowledge DIR-WF-001, publish the personal report if still branch-only, and use the packet fields/preflight beginning with the next submission. Preserve current runtime gates. Mirror only the published version into local instructions and cite its commit. Do not restart completed circuits or regenerate old reports. Record unimplemented integration items explicitly: required-check wiring and long-term productivity validation are not installed or proven here.

Ace: choose the highest-value outcome and material constraints; otherwise use **“Review Director INDEX”** when you want the next review. Intervene only for authority/resource/product tradeoffs or priority changes. You do not need to relay entire reports, collect routine CI screenshots or approve every already-authorized step. Your acceptance criterion is useful behavior with honest limits, not a claim that no undiscovered bug exists.

## Research basis and limits

Research informed the design; it did not validate DellMatrix itself. Accessed during this workflow circuit; dates in sources are source metadata, not predictions.

- [DORA: WIP limits](https://dora.dev/capabilities/wip-limits/) supports visible bounded work, bottleneck reduction and measuring flow. Our specific one-active/two-ready operating limits are a project choice, not a DORA requirement.
- [Google SRE: learning from failure](https://sre.google/workbook/postmortem-culture/) supports owned, prioritized, verifiable follow-up actions. Our recurrence guard links implement that principle locally.
- [GitHub: required check troubleshooting](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks) explains head/test-merge distinctions and accepted check states. DellMatrix's SUCCESS-only behavioral evidence rule is deliberately stricter than GitHub's generic skipped/neutral acceptance.

See `REFINEMENTS.md` for all 100 cumulative design passes and `VALIDATION.md` for executed process-tool checks and actual swarm dispositions. No 100 measured runtime improvements or simulated production successes are claimed.
