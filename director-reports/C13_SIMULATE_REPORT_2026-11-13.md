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
