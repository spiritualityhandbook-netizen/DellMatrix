# 100 cumulative workflow design passes

Each pass challenges one failure mode, retains a concrete process change, assigns an owner and names the verification. The cumulative ledger was structurally checked after each addition. These are design refinements, not 100 measured productivity gains or 100 executed product scenarios. Practical operation remains the ten gates in WORKFLOW.md. The chain hashes identify this design history; they do not authenticate it.

| Pass | Theme / failure challenge | Retained change | Verification | Owner |
|---|---|---|---|---|
| 001 | Purpose: Activity mistaken for progress | Count closed user-visible contracts, not prose or suite totals | Five-circuit scorecard | Ace |
| 002 | Scope: Whole-project task expands without bounds | Name one active circuit and its exclusions | Scope field and dependency review | Uni |
| 003 | Authority: Routine work repeatedly asks permission | Carry the existing authorization reference forward | No new start approval for same scope | Director |
| 004 | Authority: Persona treated as permission | Keep AcceptancePolicy and project roles separate | Permission-negative runtime test where touched | Uni |
| 005 | Ownership: Two writers change the same boundary | One production implementation owner per circuit | Owner map and branch coordination | Uni |
| 006 | Review: Implementation certifies itself | Director owns independent bounded certification | Reject Uni certification actor | Director |
| 007 | Status: Merge presented as certificate | Separate delivery, review and certification axes | Merged with UNKNOWN is accepted by validator | Uni |
| 008 | Identity: Certificate follows later code automatically | Bind each ruling to full runtime SHA and tree | Target-mismatch rejection | Director |
| 009 | Human role: Ace becomes packet courier | Use INDEX discovery and durable response IDs | Ace can trigger with one short request | Director |
| 010 | Historical law: Archived swarm becomes a second authority | Reuse principles, do not reactivate ops/swarm | Runtime remains independent of process tools | Director |
| 011 | Discovery: Report exists only on a local machine | Publish reachable artifact before SUBMITTED | Local-only report reference rejected | Uni |
| 012 | Discovery: Branch report mistaken for merged report | Record exact report commit and branch-only status | INDEX names publication state | Uni |
| 013 | Publication: Report and index become inconsistent | Commit report and INDEX update together | Path exists in same publication revision | Uni |
| 014 | Versioning: New submission erases old evidence | Append superseding report and stable finding IDs | Historical records remain reachable | Uni |
| 015 | Acknowledgment: Ruling must be repeated | Record response ID and fold-in in next cycle | Acknowledgment names implementation or open remainder | Uni |
| 016 | Idempotence: Repeated INDEX reading starts duplicate work | Deduplicate by response ID and finding revision | Repeated response produces no new task | Uni |
| 017 | Channel: Chat answer never reaches durable record | Publish Director response or explicit transport fallback | Response path and acknowledgment | Director |
| 018 | Local mirrors: Workspace law differs from public law | Mirror published workflow version and commit | Version/hash cited in next report | Uni |
| 019 | Accessibility: CI artifact expires before review | Record digest and durable log retention path | Reviewer can retrieve evidence bytes | Uni |
| 020 | Cadence: Overnight filing implies automatic review | Per-circuit publication with explicit human/session trigger | No background-review claim | Director |
| 021 | WIP: Too many circuits compete for attention | One active implementation and one active review | Visible queue with ownership | Both |
| 022 | Backlog: Review debt grows without bound | At two ready circuits help clear evidence bottleneck | Ready-count checked at next pull | Uni |
| 023 | Waiting: CI wait causes idle progress | Prepare independent authorized next work | No concurrent conflicting mutation | Uni |
| 024 | Priorities: Easy work displaces blocking failures | Rank dependency and user impact above convenience | Queue order has rationale | Director |
| 025 | Units: Circuit too large to review | Split by canonical mechanism and outcome | One repair can be falsified independently | Uni |
| 026 | Duplication: Same logs recopied into many reports | Link immutable artifacts once | Report references reusable evidence IDs | Uni |
| 027 | Timing: Wall time mistaken for active work | Record active, CI-wait and review-wait separately | Scorecard distinguishes bottleneck | Both |
| 028 | Measurement: Invented productivity percentage | Establish first-five-circuit baseline | No gain claim before observations | Director |
| 029 | Coverage cost: Full sweep repeated per tiny edit | Targeted feedback during edits, full gates at freeze | Rerun reason recorded | Uni |
| 030 | Rule pruning: Process complexity grows forever | Review controls every five closed circuits | Dated removal rationale retains necessary guard | Director |
| 031 | Premortem: Swarm agrees with preferred design | Ask four distinct falsification questions | Attack and oracle per lens | Uni |
| 032 | Independence: Sequential personas called independent agents | State actual reviewer arrangement | No fabricated independence | Director |
| 033 | Dissent: Unanimity suppresses a real counterexample | Retain dissent and resolve material claims | Counterexample disposition linked | Both |
| 034 | Blind test: Reviewer only repeats author checklist | Add one independent boundary probe | Director report names own probe | Director |
| 035 | State class: Display repair changes live operands | Label executable versus evidence fields | Canonical-state equality plus redacted output | Uni |
| 036 | Sequel: Immediate repair breaks next consumer | Exercise the next consumer after operation | Get to Set and Revert-style control | Uni |
| 037 | Entry points: Helper test stands in for public path | Name and execute claimed public door | Raw, English or API path explicitly scoped | Uni |
| 038 | Canonical owner: Fix creates a second executor | Repair existing owner and delegate | Source path map checked | Uni |
| 039 | Refusal: ok=False assumed to mean zero mutation | Compare all affected owners on refusal | Before/after exact state diff | Uni |
| 040 | Success: ok=True treated as durable proof | Reload canonical state for durability claim | Fresh-process witness | Uni |
| 041 | Persistence: A mutable owner omitted from rollback | List every write boundary and recovery owner | Owner-to-boundary map | Uni |
| 042 | Compensation: Only forward failure tested | Inject compensation-write failure too | Error plus durable retained-state assertion | Uni |
| 043 | Journal: Attempted clear reported as cleared | Observe journal state after clear/restart | Journal-after evidence | Uni |
| 044 | Recovery: Helper succeeds but load exposes partial state | Test actual load boundary before exposure | Public restart refusal or resolved state | Uni |
| 045 | Retry: Recovery makes later retry duplicate work | Test retry after injected failure | One coherent landed outcome | Uni |
| 046 | Side effects: Rollback hides non-live evictions | Disclose retained irreversible consequences | Counter and retained-state diff | Uni |
| 047 | Capacity: Overflow denied after proposal landing | Preflight all required owners | Zero-mutation capacity refusal | Uni |
| 048 | Retention: Reload changes eviction victim | Use explicit ordering and tie policy | Victim identity before/after reload | Uni |
| 049 | Provenance: Global loss count implies complete proposal | Track proposal-specific provenance or refusal | Expected receipts versus exported receipts | Uni |
| 050 | Corruption: Malformed recovery evidence silently discarded | Preserve evidence and fail closed | Malformed journal/load negative control | Uni |
| 051 | Parsing: Duplicate roles silently overwrite | Reject before dictionary construction | Duplicate-role negative control | Uni |
| 052 | Transport: Delimiter lowering loses target identity | Preserve structured roles into canonical handler | Colliding-neighbor exact-state probe | Uni |
| 053 | Scope boundary: Missing group widens selection | Fail closed on invalid/dangling scope | Outsider exclusion after Ungroup | Uni |
| 054 | Control: Skipped atoms disappear from receipts | Account per occurrence and reason | Repeated-Dell and zero-iteration checks | Uni |
| 055 | Join: Block verdict precedes child results | Evaluate actual completed frame results | Captured failure reflected at close | Uni |
| 056 | Transactions: Sticky error hides root cause | Scope error ownership to active transaction | Nested Try/Catch/Commit controls | Uni |
| 057 | Diff: Missing baseline claims unchanged state | Report unavailable baseline honestly | Set visibility and repeated-read checks | Uni |
| 058 | Composition: Failed definition remains published | Publish definition after successful execution | Failed redefinition preserves prior binding | Uni |
| 059 | Learning: Execution outcome treated as truth | Keep observation, eligibility and acceptance distinct | Negative learning evidence controls | Uni |
| 060 | Visuals: Display tells a different execution story | Render canonical receipt truth | Executed/skipped/failed visual consumer check | Uni |
| 061 | Network: Allowed first URL authorizes redirect chain | Authorize actual destination at each hop | Blocked hop gets zero requests | Uni |
| 062 | Secret handling: Redaction removes one echo only | Trace all outbound and persisted evidence surfaces | Synthetic marker absent at each boundary | Uni |
| 063 | Privacy semantics: Redaction corrupts rollback data | Redact detached copies only | Exact checkpoint restoration | Uni |
| 064 | Fallback: Verified primitive fails then unsafe fallback runs | Expose unavailable outcome without weaker operation | Capability-failure negative control | Uni |
| 065 | Identity: Numeric identifier reused by another object | Bind operations to current stable identity | Stale identity refusal | Uni |
| 066 | Process test: Sleep is mistaken for readiness | Capture readiness and ordering witnesses | Timestamped causal trace | Uni |
| 067 | Cleanup: Test verdict hides cleanup failure | Record original and cleanup outcomes separately | Incomplete cleanup remains visible | Uni |
| 068 | Environment: Local green closes remote red | Keep discrepancy UNRESOLVED until discriminated | Both environments and experiment linked | Both |
| 069 | Hypothesis: Plausible timing story stated as cause | Label hypothesis until experiment distinguishes it | Observation/hypothesis/result table | Director |
| 070 | Capability: Unavailable provider called passed | Separate doubles, live providers and unavailable checks | Evidence class and limits visible | Uni |
| 071 | Evidence: Claim lacks an assertion | Map every supported claim to evidence IDs | Missing-reference rejection | Uni |
| 072 | Classification: Source reading called execution | Use EXECUTED/SOURCE/REPORTED/UNKNOWN | Source cannot satisfy executed claim | Director |
| 073 | Lint: Python package lint called runtime proof | Label CI job purpose accurately | CI-only evidence cannot prove execution | Both |
| 074 | Count: Repeated suites inflate independent properties | State overlap and fixture scope | No additive duplicate proof totals | Director |
| 075 | Mutants: Mutant survives yet check called strong | Record failure at intended assertion | Survivor blocks that nonvacuity claim | Uni |
| 076 | Completeness: 100 cards imply all combinations | Separate standalone and pairwise evidence | Coverage dimensions explicit | Director |
| 077 | Pairwise: Old ledger reused after semantic changes | Re-derive final 9900 pairs at repaired freeze | Exact-head full artifact and diff | Uni |
| 078 | Benchmark: Storage difference called code regression | Match storage/workload and operation boundaries | Runtime identity and measured bytes/saves | Uni |
| 079 | Artifacts: Hash treated as authenticated author | Verify authorship separately from integrity | Validator says no authority granted | Director |
| 080 | Logs: Lost terminal output claimed durable evidence | Label observed-but-lost and provide surviving rerun | Artifact link exists for claimed log | Uni |
| 081 | CI identity: Old-head green accepted after new push | Require matching candidate head | Stale CI rejected | Uni |
| 082 | CI state: Queued/cancelled/skipped counted as success | Require completed SUCCESS for behavioral gate | Non-success required check rejected | Uni |
| 083 | Freeze: Base movement changes merge content | Refresh freeze or document reviewed delta | Candidate and merge tree comparison | Uni |
| 084 | Merge authority: Green checks treated as authorization | Link standing merge authority separately | Missing authority rejected | Uni |
| 085 | Fresh clone: Worktree-only state hides missing files | Verify merge from fresh checkout | Fresh-clone evidence link | Uni |
| 086 | Docs lane: Publication reruns become runtime evidence | Separate process/docs and runtime lanes | No new product certificate from docs CI | Director |
| 087 | Certificate scope: Open defect buried in full certificate | Use partial/exception scope or decline | Full certificate rejects open findings | Director |
| 088 | Review cost: Whole program reread for small repair | Load target and its affected consumers only | Review scope and source map | Director |
| 089 | Unknowns: Missing check silently omitted | Represent UNKNOWN or UNAVAILABLE explicitly | Limits and next evidence action | Uni |
| 090 | Continuation: Repair completion waits for new start ritual | Proceed within authorized dependencies | Next action names owner without redundant permission | Both |
| 091 | Recurrence: Lesson is only stronger wording | Add invariant, test, owner and verification link | Guard changed in next report | Uni |
| 092 | Repetition: Same mechanism fails presentation twice | Hold focused contract/owner redesign checkpoint | Minimal reproducer before next patch | Both |
| 093 | Acknowledged debt: Exception disappears from next packet | Carry open exception IDs until disposition | INDEX status reconciliation | Uni |
| 094 | Local truth: README stale date treated as current behavior | Bind public claims to source version | Dated correction rather than historical rewrite | Uni |
| 095 | Swarm limits: Four agents unavailable means fake signoff | Use labeled sequential lenses or disclose missing check | Actual participation log | Director |
| 096 | Activation: Draft tool described as enforced CI | State implemented versus wired-required-check status | Deployment status explicit | Director |
| 097 | Adoption: New format retroactively blocks old reports | Apply format prospectively with compatibility | Existing certificates preserved | Director |
| 098 | Rollback workflow: New process causes more delay than benefit | Measure and revise one bottleneck at a time | Versioned process amendment | Both |
| 099 | Handoff: User cannot tell who acts next | End each ruling with owner and next action | Ace gets concise progress/directive | Director |
| 100 | Whole system: Local optimization harms program progress | Reconcile value, risk, evidence and waiting together | Five-circuit review and scoped next priority | Ace |

Final cumulative revision: `58ba575aa212f20b12ca83b804670c3755a1e1ffb1d575e4418f4db2249593cc`. Machine-readable ledger: [refinements.json](refinements.json).
