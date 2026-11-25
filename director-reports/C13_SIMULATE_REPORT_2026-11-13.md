# C13 SIMULATE — CIRCUIT REPORT (DD-21)

Date: 2026-11-13. Branch: `uni/c13-simulate-1113`. Base: main
`6d5f821be412e3abd3736e748b855f1d99fb7b7b` (PR #408 merge).
Build head at submission: see PR head (records commit rides last).
Status: SUBMITTED — awaiting disposition. Merged != certified.
MWL rows 167–170 stay OPEN; no credit self-applied (Q-C13.7).

## 1. Contract (plan card + tour §12.16 + Ace ruling 2026-11-09 + DD-21)

Dell 31 Simulate becomes a real rehearsal. Executing Simulate with
a seed/chain argument must: (1) run that seed through the canonical
executor/front door against an ISOLATED COPY of the current program
state (disposable Program bound to copied state in a throwaway
location — profile_board.py precedent; no new persistence authority,
no new store, no second executor); (2) return an honest receipt
carrying per-atom outcomes AND a scoped diff of what WOULD change
(created/modified/removed units, proposals, history delta of the
copy — C3.Diff spirit, not a raw dump); (3) leave LIVE state
bit-identical, including history; (4) honor its argument (previously
ignored entirely); (5) fail honestly — an unparseable/refused seed
rehearses as a refusal receipt, never a fake success; an unexecuted
atom reports ok=False skipped=True with its reason.

## 2. BEFORE evidence (probe-executed on unmodified main @6d5f821)

Grounding probes P1–P6 (hidden_files/c13/GROUNDING.md §3) reproduced
the defect class first-hand:

- `31[Simulate]` returns a bare status echo built on
  `program.status()`; its own history grows 14 → 15 — the arm calls
  `note_seed` and appends `31[Simulate]` under the printed banner
  "no mutation" (G2, the headline defect).
- `31[Simulate] :: 08[Create] :: never_created` creates NOTHING and
  reports ok=True: the argument is ignored entirely (G1).
- Chain form `31[Simulate] > 08[Create]` executes the Create LIVE
  (unit appears; history +2): Simulate rehearses nothing and
  shields nothing (P3).
- `format_explain("31[Simulate]")` claims "(dry-run — no state
  change)" — false while the arm appends history. The same false
  claim rides the Dell card (`dell_cards.py`) and the semantic
  router's simulate evidence string; both corrected in this PR.
- The live `program.status()` read is a write-on-read surface
  (persona_matrix_status writes `persona_matrix.active`);
  the new path never calls it (G5).

## 3. Failing-first (suite written before the build)

`form/c13_simulate_test.py`, 15 checks mapped from the grounding's
10-check sketch (checks 6 and 7 split into outcome + isolation
halves). Run against BEFORE code (base executor_leaf restored in a
scratch clone):

    C13 SIMULATE: 2/15 checks passed — 13 FAIL / 2 PASS

Red verbatim (evidence: c13build/evidence/failing_first_red.txt):
t1, t2, t3, t4, t5b, t6, t6b, t7, t7b, t8, t9, t10, t12 FAIL;
t5 (real-run sanity) and t11 (parse-refusal receipt) PASS — the
refusal machinery already existed; the rehearsal did not. The
sketch predicted checks 1–8 red and the no-mutation guard (9)
green; reality: 13 red including the determinism and cross-owner
checks, because the BEFORE arm appends different history on every
call. Recorded as observed, not as predicted.

## 4. Mechanism (smallest change satisfying the contract)

New module `form/dell_matrix/simulate_board.py` (the harness sits
beside the existing authorities, mirroring profile_board.py):

- Copy: `copy.deepcopy(program)`, rebound to a disposable owner
  (`<owner>__simclone`) — plane/graph/duo-brain deep-copied with
  it; `_owner` rebound across program, graph and nursery; the
  Nursery object is REPLACED with one bound to the copy's owner
  file (the old binding pointed at the live nursery file — a
  same-process deepcopy of the binding is not isolation for
  file-backed surfaces). No persistence authority added; nothing
  is saved; the copy is discarded.
- Execution: the canonical front door `execute_seed` runs the
  seed text against the copy. One executor, no fork.
- Effect inventory (refused BEFORE dispatch, named on the
  receipt): durable/external atoms 27 Checkpoint, 28 Load,
  36 Summon, 44 Publish, 47 Embed — the C7 class-3 / Dell 47
  precedent (their effects are not state-local even on a copy);
  every Core II atom (51–99) and reserved atom — the copy carries
  no Core II attach, so any outcome would be fiction
  (`unsupported_domain:core_ii`, never a fake success); nested
  Simulate (31) — recursion refused by name.
- Diff: unit registry snapshot (id → kind/sandbox/label digest/
  segments/children/detail length) + proposal snapshot
  (id/status/label) + history length, taken on the copy before
  and after; the board reports `units_created/removed/modified`,
  `proposals_added/changed`, `history_delta`.
- Live proof: a fingerprint (plane serialization + history +
  SHA-256 of the live program, program-backup and nursery state
  files) is taken before and after; the receipt's
  `live_unchanged` is that comparison, and the board self-reports
  failure if it ever differs.
- Parse/refusal: a seed the front door refuses yields
  `ok=False, parse_refused=True` with the refusal text — a
  refusal receipt, never a success.

Chain integration (`form/mandell/chain_exec.py`): in this
grammar a control head owns the atoms that follow it in its
segment (the DeepFlowBy rule — `13[Loop] :: 3 > 55[Store]`
executes Store under Loop). Dell 31 is wired as a REHEARSAL HEAD
on exactly that rule: the atoms after Simulate in its range are
its operand — rehearsed on the copy, never executed live. Their
receipts ride `atom_results` marked `simulated=True`; the chain
result carries the full board receipt under `simulate`.
`execute_seed("31[Simulate] :: 08[Create] :: alpha > 20[Link]
:: alpha")` therefore rehearses the canonical Create+Link form.

Two funnel touches, both disclosed:
- `form/mandell/executor.py` — the PP3 unknown-noting pass skips
  atoms whose result is marked `simulated` (they never
  encountered the live program; noting them as unknowns would
  corrupt the live unknown register).
- `form/mandell/executor_leaf.py` arm 31 — bare/label-only
  Simulate is honestly unexecuted (`no_argument`), following
  Dell 45's "nothing to translate" precedent. The status() read
  and the note_seed self-append are GONE.

Records honesty: the Dell 31 card note (`dell_cards.py`) and the
router's simulate evidence string (`semantic_router.py`) no
longer claim "no persistence / no state change" for the old arm;
they describe the rehearsal.

## 5. AFTER evidence

- `form/c13_simulate_test.py`: **16/16** (the 15 failing-first
  checks + t5b no-fingerprint-drift and t11b data-label honesty,
  added during the build when probes refined two checks).
  Registered in `form/regress.py` LIST (280 entries, import-
  verified: exactly the 279 of main + c13_simulate_test).
- Public-path demonstration (REPL-equivalent execute_seed on a
  loaded program): BEFORE — status echo + history 2 → 3, the
  rehearsed unit never created. AFTER — receipt names atoms
  [8 Create: ok, 20 Link: ok] and diff `units_created:
  [c13_demo_unit]`, `live_unchanged: True`, live history and
  plane bit-identical (evidence: demo_before_after.txt).
- Neighboring suites (16 run, all green after §7 re-pins):
  c3diff 24/24, c7schema 33/33, dd14_loop_body 11/11,
  dd45_chain_parse_refusal 113/113, af1_chain_args 13/13,
  step3b_sanitize_chain 21/21, loop_bounds 27/27,
  flow_executor 28/28, d1_registry_leaf4 36/36,
  core_i_arg_gate 92/92, seed_grammar_stress 25/25,
  checkpoint_generation_stress 15/15, gs4_sandbox 19/19,
  semantic_route 59/59, d1_registry_leaf3 44/44.
- Single fwd regress pass at the build head: see §9.

## 6. Mutants (real work committed first; inverse-edit reverts)

- M-A (restore a history write to LIVE state during rehearsal):
  KILLED — t3_live_bit_identical, t4_no_history_entry,
  t6b_live_untouched_by_failed_sim, t9_deterministic_receipts
  fail (12/16).
- M-B (run the seed against live state instead of the copy):
  KILLED — t2, t3, t4, t5, t6b, t8, t9 fail (9/16): the diff
  comes back empty while live state actually mutates; both the
  isolation and the diff checks catch it.
Both mutants reverted by inverse edit; tree verified clean
against the commit; suite back to 16/16.

## 7. Re-pins of the superseded placeholder contract (disclosed)

Two pre-existing suites pinned the OLD arm verbatim; DD-21
supersedes that contract, so the pins move with it — minimal
edits, same shape as the codebase's own Dell 28 precedent
("routes correctly, honestly not ok"):

- `form/mandell/d1_registry_leaf3_test.py` — the 31 pin expected
  the status-echo messages exactly; it now pins bare Simulate
  as honestly unexecuted (no_argument) with units/scores/
  sandbox AND history unchanged (history is newly assertable
  precisely because the old arm appended to it). 44/44.
- `form/mandell/semantic_route_test.py` — selects_dell_31 now
  asserts routed + dell 31 + not ok (bare carries no operand);
  read_simulate_no_mutation asserts routed + not ok + domain
  snapshot equal + the refusal named. The no-mutation property
  itself is unchanged and stronger. 59/59.

## 8. Grounding corrections (where the contract source was wrong)

1. Chain shape: the grounding framed the operand as a SIBLING
   chain (`31[Simulate] > 08[Create] > …`). In the canonical
   grammar the atoms after a control head are the head's
   OPERAND (DeepFlowBy). A chain whose Simulate sibling then
   executes Create live cannot satisfy the contract, and
   refusing all post-Simulate chains would contradict the
   dialect-A authorities. The build follows the grammar: the
   following atoms ARE the rehearsal. (Sibling atoms BEFORE
   Simulate in a chain still execute live, normally.)
2. G3's substrate citation: the Nursery binds in
   `Program.__init__` (open.py:163–166), not the cited line;
   and the "37[Nurture] snapshot flow" is not the copy
   mechanism — the build uses deepcopy + disposable-owner
   rebind (profile_board precedent) with an explicit Nursery
   rebind, which the grounding named as the alternative.
3. Sketch check 6's vehicle (`53[Try]`) cannot exist inside a
   rehearsal: Try is Core II and the whole chain refuses at
   the gate. Failed-atom evidence uses a failing Core I atom
   (212[CaptureImage] → capture_unavailable) + the inventory
   refusals instead.
4. "Refused before dispatch per the Core I per-atom gate":
   the funnel has no durable-effect gate; the inventory lives
   in the board (Dell 47's own arm precedent), named as such.
5. Failing-first count: 13 red / 2 green of 15, not "~8 of 10"
   (the sketch's checks expand to 15 assertions; determinism
   and cross-owner checks were also red — the old arm's
   history append poisons both).

## 9. Regression

Single fwd pass at head fd04fb6: see the PR body for the
terminal line (the ×3 campaign is the main session's step
after this lane returns, per circuit order).

## 10. Limitations (not claimed)

- Core II atoms cannot be rehearsed in v1 (refused by name):
  the copy carries no `core_ii_exec` attach. Lifting this is a
  scoping question, not a silent gap.
- `units_removed` is implemented in the diff but not suite-
  pinned in v1 (created/modified/proposals/history are).
- Unit text bodies are not diffed (registry-level fields only);
  a rehearsal that only rewrites a unit's words shows as a
  detail-length change at most.
- No wall-clock cost field on the receipt; deepcopy cost on
  very large fields is unmeasured (Q-C13.6).
- Seed text that parses as a DATA-path label (e.g. a lone
  fragment) is treated as data by the front door, never
  executed; the receipt reports it as such (kind=seed) rather
  than as a chain — honest, but a caller expecting a parse
  refusal for near-miss atom text will not get one (t11b).
- REPL presentation of the board (a `simulate` command that
  prints the diff) is NOT built — Q-C13.5.

## 11. Questions for the Director (carried verbatim from grounding)

- Q-C13.1: Per-atom identity and scoping of the 27/28 boundary
  (canonical checkpoint_ids; wrapped-seed nonce per Decision 2).
- Q-C13.2: Simulate vs Dell 88 Patch — teach Patch to refuse
  when a seed wraps Simulate, or permit and re-verify?
- Q-C13.3: Is Dell 13 Loop-as-body acceptable as the sole v1
  iteration form, or is a bounded loop language (dialect B) a
  C13 deliverable?
- Q-C13.4: Diff baseline = applied-profile state (post-27
  restores) — confirm no additional baseline law needed.
- Q-C13.5: Should the board be callable from REPL commands
  beyond seed execution (e.g. a `simulate` command printing
  the diff)?
- Q-C13.6: Canonical copy substrate for CI scale — in-memory
  deepcopy vs MAIN-bearing restore; cost law for large fields.
- Q-C13.7: MWL rows 167–170 credit shape on merge (one row per
  fragment vs the C13 slice as one completion).

## 12. Anticipated probes

- "Simulate a seed containing 10[Keep] / 37[Nurture] / 47[Embed]
  and show nothing moved": Keep/Nurture run on the copy only
  (fingerprint incl. state-file SHA-256 unchanged — t3/t10);
  Embed is refused before dispatch by name (t7/t7b).
- "The copy's nursery writes — where do they land?": a fresh
  Nursery object bound to the disposable owner's file path;
  the live nursery file's hash is inside the fingerprint and
  verified unchanged (t10 is the cross-owner control).
- "A rehearsal inside a rehearsal?": refused by name,
  ok=False skipped=True (t13).
- "Receipt determinism": two identical simulations produce
  identical receipts modulo volatile stamps (ids/timestamps);
  t9 compares the board dicts directly and passes BECAUSE the
  board carries no wall-clock fields.
- "Mixed chain — atoms before Simulate": they execute live
  (normal chain semantics); the board covers only Simulate's
  operand range. Named here so the boundary is not discovered
  by accident.
- "Why is bare Simulate not ok=True with an empty diff?":
  Director Decision 1 (an unexecuted atom never reports
  ok=True) + Dell 45's nothing-to-translate precedent.

## 13. Ask

Director + Keeper: disposition on the C13 slice at this head;
rulings on Q-C13.1–Q-C13.7 (Q-C13.7 decides the MWL 167–170
credit shape — none is self-applied). Merge only via the main
session under the hard gate + §32 after both dispositions.

## 14. FINISH — post-interruption completion (2026-11-13, finish lane)

The build lane was interrupted after pushing head fb22bed (build
9fae03e, re-pins fd04fb6, this report) but before opening the PR.
The main session verified the pushed state first-hand and a finish
lane completed the circuit. One residual defect was found and
repaired; no product code was changed by the finish lane.

### 14.1 Residual defect: d1_proof_cards census pin (DD-21 fallout)

At fb22bed, in a FRESH clone, form.mandell.d1_proof_cards_test was
RED 4/6 — exactly two failures: (1) the bare-invocation census
(the live survey now yields 24 failures including
31: 'no_argument', the C13 contract; the pin still carried the
superseded placeholder census of 23 with Dell 31 executed);
(2) committed DELL_PROOF_CARDS.md != fresh render. Main @d930322
is 6/6 on the same suite — the defect is branch-carried, from the
build's Dell 31 change; §7's re-pins covered d1_registry_leaf3
and semantic_route but not this suite.

Diagnosis: the pins live in d1_proof_cards_test.py
(EXPECTED_BARE_FAILURES + the census assertion). The canonical
regeneration path for the cards file is the renderer itself —
dell_cards.build_all_cards(owner_prefix="D1CardT") +
render_cards_md written to form/mandell/DELL_PROOF_CARDS.md, the
same functions the suite uses (precedent: 77b815d, "no hand
edits"). Delta evidence: a fresh render on main @d930322 vs a
fresh render on this branch differ in exactly four lines, all
Dell-31 consequences — the census header (77/23 -> 76/24), the
row-31 outcome (executed -> failed: no_argument), and the Dell 31
deep-note line (the C13 note the build commit already carried in
dell_cards.py). The committed-vs-fresh diff on the branch is the
identical four lines. No other Dell's render moved.

Repair (commit 61c9b3a, following the DD-44 census precedent
0773d13): EXPECTED_BARE_FAILURES gains 31: "no_argument" with a
C13 (DD-21) comment; the census assertion becomes 76 executed /
24 named failures; DELL_PROOF_CARDS.md regenerated through the
canonical renderer — byte-identical to the branch's pre-repair
fresh render. Change surface: exactly those two files.

### 14.2 Finish-lane verifications (all in fresh clones)

- Clone 1 @fb22bed + repair (pre-commit): d1_proof_cards 6/6,
  c13_simulate 16/16, d1_registry_leaf3 44/44, gs4_sandbox 19/19,
  dock_proposal_b 17/17.
- Clone 2 @61c9b3a (pushed repair head): the same five suites,
  same counts, all green; the live demo receipt reproduced —
  rehearsal of 08[Create] :: demo_new > 07[Link] :: demo_base
  reports both atoms ok and would_create [demo_new,
  link_demo_base], history_delta +2 on the copy only; live units,
  live history and the durable state directory are byte-identical
  afterward (receipt self-check live_fingerprint_unchanged=True);
  a 27[Checkpoint] rehearsal is refused refused_external_effect
  and the state directory remains byte-identical.

### 14.3 Observation O-FIN.1 — for the Director's disposition

Isolated probes (separate processes, fresh owners) show the
front-door execution of a 31[Simulate]-headed chain materializes
the live program's Core II section in its serialized form
(core_ii.present False -> True, all-default empty content), the
first time such a chain runs on a program whose Core II was
never materialized. Direct run_simulation calls do NOT do this,
and neither do real Create chains; the trigger is the executor's
front-door path around the arm, not the rehearsal board. Nothing
else moves: no units, proposals or history change, the durable
state directory is byte-identical, and once materialized the
serialized form is bit-stable across repeated simulations
(verbatim isolated reruns). The shipped suite's bit-identity
windows do not isolate this one-time lazy materialization (its
fingerprint windows run on programs that have already simulated).
No repair was attempted — it is outside the finish lane's tasked
defect and predates it (a property of build commit 9fae03e's
executor wiring). The Director is asked to rule whether this is
an accepted lazy-default materialization (the same defaults any
Core II touch would produce) or a repair item against the
"bit-identical" wording of the C13 contract. An earlier combined
multi-owner diagnostic of the finish lane's appeared to show
sim-after-sim fingerprint instability; it did NOT reproduce in
isolated verbatim reruns and is discarded as instrument
contamination (§30) — the isolated reruns are the evidence of
record.

## 15. Q-C13.O-FIN.1 — REPAIR (Director mail 1a1d4c6cfd564a73; CODE MERGE HOLD)

The Director ruled §14.3's observation a contract violation, not
an accepted lazy default: O-FIN.1 is repaired in this circuit.
Branch union-refreshed onto main 1211cdaa first (see §15.6);
all evidence below is at the union head or later.

### 15.1 Reproduction (failing-first, Director's scope)

Minimal reproduction on a fresh UNMATERIALIZED Program (virgin
owner per case; serialized live state = `persist.serialize`
canonical JSON — the suite's own fingerprint; reading it never
attaches, persist_core_ii.serialize_core_ii is a pure
getattr/isinstance probe). Five-case probe at the union head,
pre-fix:

| case | path | core_ii.present | serialized state |
|---|---|---|---|
| A | front-door `31[Simulate] :: 08[Create] :: x` | False -> **True** | **changed** |
| B | direct `run_simulation(...)` | False -> False | identical |
| C | front-door single-atom `08[Create]` (leaf) | False -> False | own unit only |
| D | front-door LIVE `08[Create] > 07[Link]` chain | False -> **True** | chain's own effects |
| E | A repeated on an already-materialized program | True -> True | identical |

Pinned in `form/c13_simulate_test.py` as checks 14-17 on virgin
owners (serialized state captured before ANY front-door call —
the shipped fingerprint windows start after earlier front-door
runs, which is why they never isolated the transition):

- t14 (case A): FAILING-FIRST — at the union head pre-fix,
  `present_after=True fp_equal=False`, suite 19/20.
- t15 (case E), t16 (case B control), t17 (case C control):
  pass pre-fix, as designed — they are the regression guards
  for the repair, not the repro.

Precision note on §14.3: "real Create chains do not trigger it"
was grounded on the single-atom Create probe. Case D shows a
live MULTI-atom chain DOES materialize Core II — that is the
chain machinery's standing design for real chains (flow state
lives in CoreIIState) and is PRESERVED by this repair, per the
Director's scope (fix the Simulate path; normal chains behave
exactly as today, pinned by the core_ii suites in §15.5). The
defect is specific to Simulate-headed chains, whose atoms never
execute live.

### 15.2 Attachment point (isolated)

`form/mandell/chain_exec.py`, two unconditional entry attaches
of `core_ii_exec.attach(program)` (core_ii_exec.py:82-87: sets
`program.core_ii = CoreIIState()` when absent):

- `execute_chain` — the `attach(program)` immediately after the
  chain state dict is built (line 805 pre-fix numbering).
- `execute_range` — line 305 pre-fix, `st = attach(program)` at
  range entry.

A Simulate-headed seed (`31[Simulate] :: <operand>`, >= 2 atoms)
routes front-door -> `execute_chain` -> `execute_range`, where
the Dell 31 branch hands the operand to
`simulate_board.run_simulation` and consumes the range. The
rehearsal branch never reads the flow state `st`; the ONLY
`st` consumers in `execute_range` are the `_apply_flow` call
(only for i > start — never reached before the branch consumes
the range) and the post-control-head refresh (line 377, real
execution only). The board itself never attaches to the live
program (case B). So the materialization is purely the chain
machinery's entry ensure, paid by a chain that executes
nothing live.

### 15.3 Fix (smallest; chain_exec.py only; commit e6382df)

1. `execute_chain`: the entry attach is skipped iff the seed
   is Simulate-headed (`len(seed.atoms) >= 2 and
   int(seed.atoms[0].dell) == 31`, chain_exec.py:801-804).
   Every other chain — parse-refused, Core I, Core II, control —
   attaches exactly as before.
2. `execute_range`: the entry attach is deferred iff the range
   is LED by Dell 31 (chain_exec.py:317-322); the `_apply_flow`
   call site (chain_exec.py:328-333) ensures the state on
   demand, so `st` is a real CoreIIState at every actual use.
   This also covers Simulate-led ranges nested inside Loop /
   control bodies.
3. Receipt shape preserved: for the skipped case the result's
   `core_ii` snapshot is a DETACHED `CoreIIState().snap()`
   (chain_exec.py:903-904) — content-identical to what the
   pre-fix attach-then-snap produced — so consumers of the
   chain receipt see no shape change while the live program
   stays untouched.

No new authority, no second executor, no board change. The
Simulate arm never required the ensure: it rehearses on the
board's isolated copy, where materialization is the copy's own
business.

### 15.4 Verification (both cases + controls)

Post-fix: suite 20/20. The five-case probe re-run post-fix:
A present stays False, fingerprint identical; B, C unchanged;
D (live chain) still materializes — preserved by design;
E still identical. Demo receipt (fresh owner, single-atom base
Create, then front-door `31[Simulate] :: 08[Create] ::
demo_new > 07[Link] :: demo_base`): serialized BEFORE sha256
`9d9e9f5be83b999eec33f165e09605036c75ff3bd0f246c79c2477d7be2983a0`
== AFTER (same hash), core_ii present after: False, durable
state directory byte-identical, rehearsal receipt names
would_create demo_new + link_demo_base. Durable-file and
history invariants are pinned by the suite's existing checks
3/4/7b (state-dir snapshot + history equality) and re-verified
by the new t14-t16 fingerprint windows.

### 15.5 Mutant + focused suites

MUTANT M-OFIN1 (real fix committed first at e6382df; inverse
edit): the Simulate-head skip in `execute_chain` neutralized
(`_sim_headed = False`, unconditional attach restored — the
pre-fix behavior at the same point). Result: t14 FAILS with
exactly the pre-fix signature (`present_after=True
fp_equal=False`), suite 19/20; t15-t17 stay green. Reverted by
the inverse edit; post-restore diff empty; suite 20/20 again.

Focused suites (regress-style per-entry subprocess runs at the
repair head; 22/22 green): c13_simulate 20/20;
d1_proof_cards 6/6; d1_registry_leaf3 44/44; gs4_sandbox
19/19; dock_proposal_b 17/17; core_ii_smoke 36/36;
core_ii_persist 20/20; core_ii_version_validation 60/60;
flow_executor 28/28; control_runtime 38/38; dd14_loop_body
11/11; dd45_chain_parse_refusal 113/113; dd45_recon 20/20;
step7_control_verdicts 28/28; dirf13_loop_count 17/17;
af1_chain_args 13/13; step3b_sanitize_chain 21/21;
loop_bounds 27/27; semantic_route 59/59; p10_flow_grammar
12/12; pp5_flow_visual 8/8; first_failure_provenance 39/39.
The serial same-head fwd/twice/rev campaign, exact-head CI and
§32 remain the main session's, after this refreshed PR.

### 15.6 LIST reconciliation (union-refresh onto main 1211cdaa)

Merge of origin/main (1211cdaa) into uni/c13-simulate-1113 =
union commit 1d3eac0. Records conflicts resolved by whole-file
set-union, verified by multiset comparison (not conflict
blocks alone): INDEX.md = main's 261 lines (duplicates kept
as-is) + 1 branch-only line (this report's row) = 262;
DIRECTOR_REVIEW_QUEUE.md auto-merge verified multiset-exact
(main 111 + 1 branch-only C13 row = 112). No product-code
conflicts. regress LIST counts, import-verified at each rev:
main 279; branch 280 (branch-only entry:
`form.c13_simulate_test:smoke`); merged tree 280 == sorted set
union, no duplicates.

### 15.7 Residuals

- Q-C13.1-.7 untouched by this repair; still pending the
  Director's evidence-specific disposition. No MWL 167-170
  credit is claimed here.
- A Simulate atom in a NON-head position of a real chain still
  rides the chain machinery's standing attach (the chain has
  real live atoms; its materialization is today's behavior,
  preserved deliberately per §15.1 case D).
- Independent patch review and Keeper confirmation remain
  required before merge; the CODE MERGE HOLD stands until the
  Director lifts it.

## 16. Bisect of the nondeterministic 19/20 (2026-11-13)

### 16.1 Reproduction

At head 16b8bad the c13 suite failed 19/20 in three independent
environments: exact-head CI smoke (run 43423796181, BOTH the 3.10
and 3.11 passes, sole failing entry of 280), the main-session
campaign forward leg in the repair clone (279/280), and standalone
runs in a clean clone (hourly cycle §30 differential: run 1 20/20,
run 2 in the same tree 19/20, sole fail t9). A second full regress
in the campaign clone returned 280/280 — the failure is
nondeterministic, single-check, and migrates between checks.
Locally observed failing set across all runs at 16b8bad: t3, t6b,
t7b, t9, t10, t14, t15, t16. In every failing run the isolation
contract itself held: Simulate wrote nothing live (t14's
present_after=False, beta_absent=True class facts intact).

### 16.2 Why CI's exact failing check is unknowable

CI's regress capture strips per-check FAIL detail (its scraper
regex expects `FAIL name:`; the suite prints `[FAIL] name |`).
The failing check under CI is therefore not recoverable from the
CI record; the local failing set above is the evidence base.

### 16.3 Mechanism 1 — wall-clock inside the fingerprint (primary)

`persist.serialize` stamps `"saved":
datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`
(form/persist.py:301, second resolution). At 16b8bad both the
suite's `_fingerprint` and the board's `_live_fingerprint` hashed
the full serialization INCLUDING `saved`. Any before/after pair
straddling a one-second boundary differs with zero state change.

Deterministic proof (dwell experiment, suite t3 window, same code
path, dwell inserted between the paired serializes):

| dwell | fails |
|-------|-------|
| 0.0s  | 0/12  |
| 0.35s | 4/10  |
| 1.2s  | 12/12 (sole serialized diff: `.saved`) |

Ambient rate ~1/40 per window; under regress/CI each window
stretches (thousands of state files hashed, board deepcopies), so
a straddle in at least one window per run is likely — exactly one
check fails, identity varies. String-level confirmation at the
board: three captured `live_fingerprint_unchanged` flips (t1 sim,
a t9 det sim, the t6 failing-merge sim) each differ in EXACTLY
one blob region — `saved`, one second apart (full-blob character
diffs of 1, 1, and 2 characters; blob hashes match the board's
returned hashes at every position; files leg equal throughout).

### 16.4 Mechanism 2 — whole-directory snapshot scope

The suite's `_dir_snapshot()` hashed EVERY top-level file in the
shared `form/state/`, compared by t3, t7b, t10. Diagnostic runs
named the differing files — all other owners' artifacts, incl. a
`.dmtmp` sibling caught mid-atomic-write
(`checkpoint_preserve_CR_12_after_both_nursery.json`,
`graph_P2SUSX99.*`, `nursery_DD14A682D606D.json`,
`checkpoint_CR_11_after_pointer_*`,
`exchange_import_Step5Adm.journal.json.dmtmp.*`). Under a real
regress the private copy's state dir holds ~4,958 files before
c13 runs. The bit-identity contract covers the simulated owner's
state and writes BY the simulation (§30); unrelated suites'
files in a shared directory are ambient state the suite does
not own.

Classification: (a) — suite-isolation defects in
form/c13_simulate_test.py plus the same exposure inside the
board's self-check. Not a contaminating suite; not a product
race. d1_proof_cards_test exonerated (Dell 31 census outcome is
parse-level deterministic); confirm_crash_matrix writes nothing
into c13's windows under sequential regress (used only as the
coupling-reproduction vehicle: pre-fix pairing failed 2/3 and
3/3; post-fix 3/3 PASS).

### 16.5 The apparent third mechanism — attribution artifact

Early captures suggested a residual flip source beyond
mechanisms 1+2: t9 receipt pairs differing only in
`live_fingerprint_unchanged` and `lines[5]` (diag3 iter12 and
iter33; t9_mismatch.json), at points where a separate fp-pair
table seemed to clear the t9 sims themselves. String-level
capture (§16.3) closes this: every flip ever captured at blob
level — including a flip inside a t9 det sim itself
(blob_flip_2) — is `saved` and only `saved`, and the t9 window
is subject to mechanism 1 twice over, because t9 compares the
FULL receipts of its two sims byte-for-byte (suite
c13_simulate_test.py, the r1/r2 `json.dumps` comparison): one
straddle inside either sim's board window flips exactly one
receipt's `live_fingerprint_unchanged` (and its `lines[5]`)
and the pair differs, while the paired suite-side checks are
unaffected. The residual appearance came from the diagnostic
harness pairing fp calls to sims by global index under a
sim-count assumption that does not hold (prescan-refused sims
never reach the fp pair; 10 executed sims = 20 calls, not
11/22; diag3b iter33's table marks the t9 pairs equal and pair
4 unequal on that indexing), so which sim a given straddle
belonged to was misattributed — the straddle that failed t9
need not be the pair the table flagged, and vice versa. The
earlier `.agenda` attribution does not survive re-verification:
no `agenda` key exists anywhere in the serialization path at
either head (grep + AST scan of persist.serialize's literal
keys; fixed 46-key top-level set, invariant across 99 Dell
seeds, 149 registry heads, save/load roundtrip, and consecutive
full smokes). No third mechanism is claimed. The board's
`_live_files` leg (live owner's program + nursery file hashes)
was captured at every blob-level flip: equal (both files
absent) in all three; no in-window writer of live-owner files
was ever observed. Post-fix corroboration: at bd09b0b (board
fingerprint excludes `saved`), 60 consecutive in-process smokes
ran 780 sims with zero `live_fingerprint_unchanged` flips
(§16.10).

### 16.6 Repair (commit bd09b0b)

Files: form/c13_simulate_test.py, form/dell_matrix/simulate_board.py.

- Suite `_state_fingerprint`: serialize once, pop the top-level
  `saved` stamp, hash. Every other serialized field still
  compared bit-for-bit; t14–t17 keep their exact strength.
- Board `_live_fingerprint`: same exclusion, in the product
  self-check (the identical exposure inside one sim call —
  leaving it would have kept the receipt's own
  `live_fingerprint_unchanged` nondeterministic).
- Suite snapshot scoped to suite-owned names (`_dir_snapshot
  (owners)`: owners C13SimT1–T9 plus any name containing
  `C13Sim`, covering the board's disposable owners
  `C13Sim{pid}_{counter}`), used at t3, t7b, t10 in place of the
  whole-directory snapshot. `_cleanup` unchanged.

### 16.7 Mutants

- M-OFIN1 (inverse-edit restore of unconditional Core II attach
  at both chain_exec sites): t14 FAILS (present_after=True,
  fp_equal=False). Reverted clean; diff empty.
- M-BOARD (board appends to live history before fp_after):
  7 checks FAIL (t3, t4, t6b, t9, t14, t15, t16). Reverted clean.
- M-WRITE (scheduled stray write of program_C13SimT1.json during
  a sim): inconclusive as designed (write landed after the
  compare window); the scoped-snapshot contract was instead
  proven directly by A/B — an own-owner file enters the scoped
  snapshot; a foreign-owner file (program_ForeignOwnerX.json)
  does not and leaves it unchanged.
- Post-fix dwell battery: 1.2s dwell 10/10 PASS (pre-fix 0/12);
  a real state change is still caught by `_state_fingerprint`.

### 16.8 Director addendum probes (mail 1a1d51dfd3862eaa), at bd09b0b

- P-A mixed chain `08[Create]:: probe_live_a > 31[Simulate]::
  08[Create]:: probe_ghost` on a virgin owner: ok=True, simulate
  receipt ok/executed; core_ii_present=True (the standing attach
  for a real chain is NOT suppressed by the O-FIN.1 deferral),
  live_a_on_plane=True, ghost_on_plane=False, history_len=1.
  Live atoms before Simulate attach/materialize as standing
  behavior; the Simulate segment stayed rehearsal-only.
- P-B(i) ranged `13[Loop]:: 2 > 31[Simulate]:: 08[Create]::
  probe_loop_ghost`: ok=True, simulate executed;
  core_ii_present=True — inherits the chain's standing attach,
  exactly the §15.7 disclosed residual; ghost_on_plane=False,
  history_len=1, no crash.
- P-B(ii) nested `31[Simulate]:: 31[Simulate]:: 08[Create]::
  probe_nest`: refused_nested_simulate (ok=False),
  core_ii_present=False, nest_on_plane=False, history_len=0.
  Its fp difference was diffed to a single serialized field:
  `unknowns.entries` — the PP3 register (form/mandell/
  executor.py:140–157; form/dell_matrix/unknowns.py
  register_encounter, entry_id=uuid4().hex) records "Dell 31 did
  not execute: …" on the LIVE program for the refused inner atom.
  That is designed encounter bookkeeping, not an isolation
  breach (no Core II, no plane/nursery writes). Recorded as an
  observation; not patched.
- P-CTL control, pure real chain `08[Create]:: probe_ctl_a >
  07[Link]:: welcome`: ok=True, core_ii_present=True,
  ctl_a_on_plane=True — normal path unbroken.

### 16.9 Evidence-integrity disclosure

This lane's early warm iterations (warm_prefix/warmb/warmc logs)
ran three drivers CONCURRENTLY against one checkout,
cross-contaminating each other; those [FAIL] logs are concurrency
artifacts of the harness, not regress evidence, and are not
relied on. The valid chain: private-copy prefix runs (259
entries OK; c13 20/20 ×3 in the quiet copy), filesystem watcher
during a quiet diagnostic window (0 external events), sequential
coupling runs, serialized diffs, dwell experiments, and the
string-level blob captures of §16.3/§16.5. A VM replacement
(~13:02Z) wiped /tmp; all relied-on artifacts live under the
goal's hidden_files/c13bisect/.

### 16.10 Verification at the final head

- (i) Suite standalone in a fresh tree at bd09b0b: 20/20,
  EXIT=0 (fresh_standalone.log). Plus 60 consecutive in-process
  smokes at the fixed head: 780 sims, zero
  `live_fingerprint_unchanged` flips (lfu_capture.log).
- (ii) Full `python3 -m form.regress` (fwd) in the bisect clone
  at bd09b0b (regress_run1.log): `REGRESS: 280/280 -> GREEN` /
  `REGRESS FINAL: GREEN (order=fwd)`, EXIT 0 (280 OK, 0 FAIL).
- (iii) Second full regress, same tree, back-to-back
  (regress_run2.log): `REGRESS: 280/280 -> GREEN` /
  `REGRESS FINAL: GREEN (order=fwd)`, EXIT 0 (280 OK, 0 FAIL).
  Both runs executed at the bisect-fix commit bd09b0b; this
  records commit changes records only.

### 16.11 Final head and scope

FINAL HEAD: [AT-COMMIT] (this records commit; its full SHA is stated in the PR #413 bisect-return comment and in DIRECTOR_REVIEW_QUEUE.md — a commit cannot contain its own hash). Parent (bisect fix): bd09b0b7229fed8d48f8d14dee0e49c1039fd441. Bisect-fix scope (bd09b0b):
form/c13_simulate_test.py, form/dell_matrix/simulate_board.py.
Cumulative PR #413 scope (15 files vs main 1211cdaa, the union base): director-reports/C13_SIMULATE_REPORT_2026-11-13.md, director-reports/DIRECTOR_REVIEW_QUEUE.md, director-reports/INDEX.md, form/c13_simulate_test.py, form/dell_matrix/simulate_board.py, form/mandell/DELL_PROOF_CARDS.md, form/mandell/chain_exec.py, form/mandell/d1_proof_cards_test.py, form/mandell/d1_registry_leaf3_test.py, form/mandell/dell_cards.py, form/mandell/executor.py, form/mandell/executor_leaf.py, form/mandell/semantic_route_test.py, form/mandell/semantic_router.py, form/regress.py. This section,
once committed, is the immutable statement of that head and
scope.

### 16.12 Attempt history

- 16b8bad: CI smoke run 43423796181 FAILED (c13 19/20, both
  passes); campaign forward leg RED identically (279/280);
  second campaign-clone regress GREEN 280/280 (nondeterminism
  signature). O-FIN.1 repair e6382df stands as a scoped repair
  candidate for verification (Director, mail 1a1d51dfd3862eaa) —
  not certification, not merge authorization.
- bd09b0b: bisect repair (this section). Verification at
  bd09b0b: fresh-tree standalone 20/20 EXIT 0; two consecutive
  full regress runs in the same tree, back-to-back, both
  280/280 GREEN EXIT 0 (§16.10). Exact-head CI and the
  main-session x3 campaign run at the final records head and
  are still owed at the time of this commit; the PR remains
  under the Director's CODE MERGE HOLD.
