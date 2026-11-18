# 100 CORE DELL ADDRESSES — DIRECTOR CONTRACT CATALOG

**Source:** main a8786f9c40cdeaaa8fe9ebeb6705a64d52490269, form/mandell/registry.py (00–50), core_ii.py (51–99). **These are Director-designed minimum operational contracts**, NOT evidence that current product code fulfills each. A registry route marked ACTIVE is reachability, not completion. The old "99 Dells" label is inconsistent with **51 Core I + 49 Core II = 100 addresses**; update the plan nomenclature, not the code addresses. Address 151 remains a reserved case, not a Core Dell.

**Proof:** S = successful public invocation, explicit invalid/missing refusal, deterministic receipt and nonmutation when read-only; M = S plus identity, state generation, restart or rollback/fault injection, and owner boundary proof. Every row also needs a typed argument signature, actual code handler, failure enum, current implementation class and exact-head evidence before certification.

| # | Name | Registry manor | Dispatch family | Director proposed minimum operational contract | Proof |
|---:|---|---|---|---|---|
| 00 | Nova | Origin / fresh start | Core I leaf | Read or initialize declared owner origin; never wipe existing state silently | S |
| 01 | Initiate | Root command / entry | Core I leaf | Open typed execution session bound to owner, scope and grants | S |
| 02 | Persona | Identity / role | Core I leaf | Apply persona to presentation or role without permission escalation | S |
| 03 | Logic | Rules / constraints | Core I leaf | Evaluate declared logical predicate without guessing missing tokens | S |
| 04 | Transform | Convert / reshape | Core I leaf | Transform supplied value with named format and before and after receipt | S |
| 05 | Tone | Vibe / style | Core I leaf | Change style or tone of a view without rewriting canonical meaning | S |
| 06 | Cycle | Rhythm / timing | Core I leaf | Advance declared temporal cycle with explicit bounded units | S |
| 07 | Link | Connect / reference | Core I leaf | Propose explicit typed link across valid canonical endpoints only | S |
| 08 | Create | Instantiate | Core I leaf | Create canonical Idea with complete admitted fields and persistent identity | M |
| 09 | Show | Render / output | Core I leaf | Render exact current object or view with honest coverage and no ghosts | S |
| 10 | Keep | Pin / persist | Core I leaf | Save named generation via canonical writer; return durable state receipt | M |
| 11 | Architect | Schema / blueprint | Core I leaf | Validate draft architecture against schema before production mutation | S |
| 12 | Test | Validate / assert | Core I leaf | Execute declared assertion using observed outcome, never invented PASS | S |
| 13 | Loop | Iterate until | Core I leaf | Repeat exact named body a declared number of times; stop on first failure | M |
| 14 | Bind | Attach / semantic edge | Core I leaf | Bind named roles or IDs under typed endpoint checks; no implicit containment | M |
| 15 | Map | Coordinate / index | Core I leaf | Map source objects to declared coordinates without inventing identity | M |
| 16 | Decay | Discard / expire | Core I leaf | Apply declared decay to eligible targets with preserved prior evidence | M |
| 17 | Shadow | Background parallel | Core I leaf | Run authorized advisory shadow operation without uncontrolled writes | M |
| 18 | Mirror | Compare / diff | Core I leaf | Compare canonical objects with explicit missing versus null semantics | S |
| 19 | Drive | Direction / intensity | Core I leaf | Apply explicitly bounded influence to named consumer; show actual amount | M |
| 20 | Alpha | Close / finalize | Core I leaf | Close verified generation with archival record, never silent finalize | M |
| 21 | Merge | Two → one | Core I live_identity | Merge parent substance and provenance while retaining recoverable source IDs | M |
| 22 | Split | One → parts | Core I live_identity | Split source into distinct typed pieces preserving parent and lineage | M |
| 23 | Lock | Sandbox switch over units (sandboxed=True on every live unit; not per-unit immutability, not a permission grant) | Core I leaf | Sandbox named unit scope, not reinterpret as permission or immutability | M |
| 24 | Unlock | Release lock | Core I leaf | Release protected sandbox only with matching owner and grant | M |
| 25 | Pulse | Broadcast outward | Core I leaf | Diffuse selected evidence-backed resonance; enforce exclusions and lifecycle | M |
| 26 | Temp | Cold / Warm / Hot planes | Core I leaf | Set typed temperature for specific consumer, not hidden global enhance | M |
| 27 | Checkpoint | Snapshot state | Core I closable | Seal checkpoint with integrity, generation ID and restart retrieval | M |
| 28 | Rollback | Authority-mediated checkpoint restore (bare use denied; freeze + grant + confirm_rollback required) | Core I closable | Rollback only with frozen grant and confirmation, no partial restore | M |
| 29 | Compress | Shrink payload | Core I leaf | Compress reversible representation linked to recoverable full source | M |
| 30 | Expand | Unfold | Core I leaf | Expand valid source/version; refuse missing or stale source | M |
| 31 | Simulate | Dry-run | Core I leaf | Simulate declared effect set in isolated copy, never live | S |
| 32 | Pause | Halt | Core I leaf | Pause named work without deleting any data or allowing background mutation | M |
| 33 | Resume | Continue | Core I leaf | Resume eligible paused state idempotently with permission check | M |
| 34 | Stamp | Time/order mark | Core I closable | Attach stable provenance-bearing time or order stamp to exact object | M |
| 35 | Discover | Scan structure | Core I closable | Discover complete eligible set through ranked pages and truthful totals | S |
| 36 | Inject | Load into scope | Core I leaf | Inject typed validated reference or data into authorized scope | M |
| 37 | Nurture | Nursery lifecycle | Core I closable | Nurture quarantined proposal through human gate with no auto approval | M |
| 38 | Distill | Summarize | Core I leaf | Distill source meaning with precise omissions and offline fallback | S |
| 39 | Schema | Validate shape | Core I leaf | Validate declared schema and refuse invalid shape before mutation | S |
| 40 | TokenCount | Cost measure | Core I closable | Count tokens using declared tokenizer/model; distinguish measured and estimate | S |
| 41 | Sanitize | Strip secrets | Core I leaf | Sanitize protected values in outward paths and retained evidence | S |
| 42 | Retry | Re-attempt | Core I leaf | Retry named failed attempt within bounded idempotency policy | M |
| 43 | Fallback | Safe path | Core I leaf | Choose declared fallback for typed failure without claiming original success | M |
| 44 | Bridge | Honest refusal - no external tool provider bound (bridge_unavailable, offline) | Core I closable | Bridge through verified provider grant or return bridge_unavailable | S |
| 45 | Translate | EN ↔ Mandell | Core I leaf | Translate admitted text and typed roles losslessly or refuse ambiguity | S |
| 46 | Rank | Score | Core I leaf | Rank eligible evidence using versioned weights and disclosed missing inputs | S |
| 47 | Embed | Honest refusal - no embedding provider bound (embed_unavailable, representation none) | Core I closable | Embed through compatible provider/vector space or return embed_unavailable | S |
| 48 | Macro | Shortcut sequence | Core I leaf | Expand versioned macro from exact stored seed; no implicit execution | M |
| 49 | Profile | Benchmark | Core I leaf | Profile tagged stages with monotonic clock, workload and memory identity | S |
| 50 | Manifest | Make real / bring into form | Core I leaf | Manifest accepted plan through canonical operation, distinguishing yes from action | M |
| 51 | Select | Select target(s) from current scope | Core II chain | Select explicit stable IDs within authorized scope and return coverage | S |
| 52 | Filter | Reduce a set by conditions | Core II chain | Filter selected set by shared typed predicate, not free-text truthiness | S |
| 53 | Scope | Establish execution/context boundary | Core II chain | Apply typed execution scope without privilege escalation | S |
| 54 | Query | Retrieve information without mutation | Core II chain | Query canonical source without mutation, distinguish missing and empty, page results | S |
| 55 | Set | Assign an explicit value/state | Core II chain | Set typed value with exact owner and optimistic conflict detection | M |
| 56 | Get | Retrieve explicit value/state | Core II chain | Get typed value or return missing instead of fabricated zero | S |
| 57 | Compare | Structured comparison between >=2 targets | Core II chain | Compare exact two typed operands; refuse surplus shorthand tokens | S |
| 58 | Match | Pattern/semantic matching | Core II chain | Match declared pattern with grammar, full operand and clear no-match | S |
| 59 | Route | Choose/direct execution path (in a Branch chain a 59 atom is consumed as the Else marker, never as Route) | Core II chain | Route to explicit target; in Branch grammar distinguish Else token | S |
| 60 | Branch | Conditional divergence | Core II chain | Branch only on shared predicate verdict; record skipped branch | M |
| 61 | Join | Rejoin divergent execution paths | Core II chain | Join compatible branch results; refuse conflicting writes | M |
| 62 | Parallel | Execute operations in listed order - sequential, not concurrent; a sibling failure is captured and the remaining operations still run | Core II chain | Run isolated parallel arms with read/write sets; human-confirm canonical merge | M |
| 63 | Sequence | Explicit ordered execution | Core II chain | Sequence exact atoms with first failure and skipped-result receipts | M |
| 64 | Until | Continue until condition becomes true | Core II chain | Until condition true with explicit iteration budget and exhaustion | M |
| 65 | While | Continue while condition remains true | Core II chain | While shared predicate true with no silent alternative cap | M |
| 66 | ForEach | Apply operation across collection | Core II chain | ForEach eligible declared member or honest continuation | M |
| 67 | Any | Existential/set-any condition | Core II chain | Any over defined set with explicit empty and missing-source semantics | S |
| 68 | All | Universal/set-all condition | Core II chain | All over defined set, disclose vacuous truth on empty set | S |
| 69 | None | Explicit absence/zero-match condition | Core II chain | None over defined set, distinguish no matches from no data | S |
| 70 | Count | Cardinality - not token count | Core II chain | Count cardinality of named set with authoritative scope | S |
| 71 | Measure | Count selected-set cardinality only (kind/unit label is annotation, not a property measurement; property vocabulary deferred) | Core II chain | Measure typed quantity and unit with provenance, not relabeled count | S |
| 72 | Limit | Establish maximum/minimum/range | Core II chain | Validate explicit min/max/range and reject incoherent bounds | S |
| 73 | Threshold | Trigger/qualify at boundary | Core II chain | Threshold typed comparable value; no dropped extra tokens | S |
| 74 | Weight | Assign relative influence | Core II chain | Weight eligible dimension by visible coefficient and source | M |
| 75 | Normalize | Convert differing scales/forms to common basis | Core II chain | Normalize same-unit values, refuse zero range and incompatible units | S |
| 76 | Resolve | Resolve ambiguity/conflict/reference | Core II chain | Resolve ambiguous reference with evidence or human choice | S |
| 77 | Infer | Derive unstated result from evidence/rules | Core II chain | Infer proposed result from premises with uncertainty and falsifier | S |
| 78 | Cause | Encode causal relationship | Core II chain | Record causal claim only with admitted evidence separate from association | M |
| 79 | Depend | Encode dependency/prerequisite | Core II chain | Write typed depends-on edge and reconcile propagation | M |
| 80 | Context | Establish semantic contextual frame | Core II chain | Establish semantic context frame, not trusted permission boundary | S |
| 81 | Reference | Address existing object/state without copying | Core II chain | Dereference stable object under owner grants with cycle/missing handling | S |
| 82 | Group | Treat multiple targets as one collection | Core II chain | Create named semantic group preserving members, not automatic sandbox | M |
| 83 | Ungroup | Release collection while preserving members | Core II chain | Ungroup preserving member identities and provenance | M |
| 84 | Copy | Duplicate without consuming original | Core II chain | Copy object with new identity and explicit source lineage | M |
| 85 | Move | Relocate ownership/location/state (overwrites an existing destination) | Core II chain | Move typed target through owning authority retaining identity | M |
| 86 | Delete | Explicit controlled removal | Core II chain | Delete with recoverable tombstone and no dangling edges | M |
| 87 | Replace | Key rename old to new (refuses an occupied destination - replace_occupied, no mutation) | Core II chain | Replace key after occupied-destination check preserving history | M |
| 88 | Patch | Partial targeted modification | Core II chain | Patch declared fields atomically with stale-generation refusal | M |
| 89 | Diff | Produce exact change-set | Core II chain | Diff complete state in stable order, including absent versus null | S |
| 90 | Trace | Follow provenance/execution/data path | Core II chain | Trace origin-to-outcome with full paginated evidence | S |
| 91 | Assert | Require invariant; fail if false | Core II chain | Assert parsed predicate true; false or missing cannot stamp PASS | S |
| 92 | Guard | Prevent execution unless conditions hold | Core II chain | Guard protected operation before dispatch on typed condition | S |
| 93 | Try | Begin recoverable/failable operation | Core II chain | Try establish recoverable frame and failure identity | M |
| 94 | Catch | Handle failure/error class | Core II chain | Catch only matching failure within declared Try frame | M |
| 95 | Commit | Mark/accept current live state (live mark/accept only - no atomic isolation, no staging area; Revert covers only the Try checkpoint fields) | Core II chain | Commit allowed scope without falsely promising cross-file atomicity | M |
| 96 | Revert | Undo a mutation/change-set | Core II chain | Revert supported Try or snapshot fields and disclose exclusions | M |
| 97 | Define | Create reusable semantic definition | Core II chain | Define reusable versioned semantics without surprise execution | M |
| 98 | Alias | Bind alternate expression to existing semantic identity | Core II chain | Alias existing canonical target with ambiguity and cycle refusal | M |
| 99 | Compose | Create reusable higher-order operation from Dells | Core II chain | Compose explicitly bounded typed operations with no implicit eight-step work | M |

## Required current-code certification overlay

Uni adds a parallel exact-head evidence matrix with row for each of the 100 addresses: registry/handler code path and blob SHA, admitted typed and legacy operand forms, actual successful and refusal behavior, state effect, persistence owner, exact public-path test and exception test, Keeper stamp, Director ruling, and post-merge evidence. Use VERIFIED / IMPLEMENTED_UNVERIFIED / PARTIAL / CONTRADICTED / ABSENT / HONEST_REFUSAL. This authored table does not import current CODE completion or MWL credit.

**High-blast-radius groups:** predicate/shorthand 57/60/73/91/92; Parallel/Join 62/61; transaction 95/96; identity/persistence 08/10/14; loop/Compose 13/99; resonance 16/17/25/26/32/33; measurement 70–75. Handle those via the fully specified GP-E04/E09/E10/E11/E12/E15/E19 circuits. Bridge 44 and Embed 47 are legitimate honest offline refusals until a provider is bound. Eight thin-spec elders 00, 03, 07, 10, 11, 12, 14, 19 retain Ace's substantive semantic gate.

The combined pair and triple exploration FI-006 is a distinct testing program, not proof that all combinations are already exercised. Record ordered-pair/triple coverage, specific fixtures, excluded/impossible cases, exact inputs, falsifiers, time/cost, and stable results. No all-combinations certificate from sampling.
