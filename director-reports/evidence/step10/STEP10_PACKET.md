# STEP 10 PACKET — consistency circuit: B11 Resolve, B12 Ungroup, B18 Compose

Status: GROUND + SWAT PRE-MORTEM + FAILING-FIRST COMPLETE
2026-11-01. Implementation NOT yet started.
Base: main 6c90039 (PR #201 merge; DIR-F repair wave complete,
all repair closures landed before the step 13 freeze).
Worktree: ~/workspace/nbd-omega-step10 (fresh clone at 6c90039).
Ground: hidden_files/step10_ground.md (prepared 2026-11-01 at
da9e0b2) — RE-VERIFIED at 6c90039 this cycle: the only
spectrum_ops.py delta since da9e0b2 is DIR-F15 (Diff, n==89)
and DIR-F14 (Catch, n==90); query_ops.py and registry.py are
unchanged. The B11/B12/B18 defect sites are byte-identical.

## Defect sites (read first-hand at 6c90039)

- B11: form/mandell/query_ops.py n==76 — resolve_manifest on
  Resolve's own term; result_cell(matched=True) UNCONDITIONALLY.
- B12: form/mandell/spectrum_ops.py n==83 —
  members = st.groups.pop(name, []) — missing group is
  indistinguishable from an existing empty group.
- B18: form/mandell/spectrum_ops.py n==99 define branch —
  st.compositions[name] = body (line 504) BEFORE
  _run_compose (line 505); a failed define-run is published,
  and a failed redefinition destroys the prior valid body.

## Failing-first probe (hidden_files/step10_probe.py)

Run on UNFIXED 6c90039, public seed path (form.open.Program +
execute_seed), synthetic owners, cleanup verified (no state
files left). 5/14 contract lines hold; 9 defect witnesses FAIL:

- W-R1 ':: Select' -> value=Resolve conf 1.00 (target ignored)
- W-R2 ':: 51' -> Select at conf 0.40 (manifest fallback)
- W-R3 ':: bogusname' -> Resolve conf 1.00 matched=True
- W-R4 bare -> self-resolution conf 1.00 matched=True
- W-R5 ':: \u00b2' -> Resolve conf 1.00 (no crash on the CURRENT
  handler — its int() is try-wrapped; the crash lives in
  registry.lookup, verified separately below)
- W-R5b ':: Loop' -> Resolve conf 1.00
- W-U1 Ungroup ':: nosuchgroup' -> ok=True released=0
- W-C1 define badone=89[Diff] -> ok=False baseline_missing
  AND comps={'badone': '89[Diff]'} (published despite failure)
- W-C2 redefine keep=89[Diff] (prior keep=82[Group]) ->
  ok=False AND comps['keep']=='89[Diff]' (prior body LOST)

Controls PASS on unfixed code (must stay green): existing
empty group ungroups ok released=0 (seeded directly —
82[Group] snapshots selection/ids and is never empty on a
fresh program); populated ungroup adopts members into an
empty selection; valid define good=70[Count] stores and
runs; self-reference -> compose_cycle, nothing stored.

Probe-form lessons (recorded, not defects):
- A Compose body containing a nested '::' label does not
  parse as one seed ("unexpected at 15") — witnesses use
  single verbatim atoms (70[Count], 82[Group], 89[Diff]).
- 89[Diff] is a reliable run-failure body only with no
  store baseline; 82[Group] captures none, 55[Set] does.

## registry.lookup hazard (first-hand, python3 at 6c90039)

- lookup('\u00b2') RAISES ValueError (s.isdigit() is True,
  int() raises) — the DIR-F13 failure class, live in the
  shared authority the B11 repair must consult.
- lookup('9'*5000) RAISES ValueError (4300-digit int limit).
- lookup('Select') -> dell 51 record; lookup('Bindell') ->
  Bind dell 14 (NAMED alias); lookup('151') -> RESERVED_
  NOT_ACTIVE record (Harmonic, dell 151).

## SWAT Director's-eye pre-mortem (before implementation)

Personas applied: Custodian, Interpreter, Sentinel,
Mechanic. Agreement 4/4 on the repair shapes below;
unanimity is recorded as method, NOT as a truth gate
(DIR-WF-001 amendment); the anticipated probes are the
claims' real test.

How the Director would break this (anticipated probes):
1. Resolve ':: 076' / leading zeros, ':: Select' with
   trailing words, mixed case ':: sElEcT', a NAMED alias,
   ':: 151' (reserved), ':: 999', ':: \u00b2', a 5000-digit
   label — each must be a clean hit or a clean miss,
   never a crash, never conf 0.40, never matched=True
   on a miss.
2. Resolve inside a chain / after a Get — last_result
   cell agreement between message and cell (step 3c
   lesson: consumers read the cell, not the message).
3. Ungroup the active scope group (R1 contract must
   survive: pop + warning + Select scope_unknown after);
   Ungroup refusal inside Try — does the B15 hook mark
   the frame failed like other spectrum refusals?
   Assert the observed behavior, either way.
4. Compose redefinition whose new body REFERENCES the
   name being redefined (directly or via an alias/def
   chain): parse stack starts as {name}, so this stays
   compose_cycle pre- and post-repair — assert it.
5. Compose failed define-run WITH live effects (body
   mutates, then fails): effects persist outside a Try;
   neither message nor report may imply rollback.
   Inside Try + Revert, the established _ckpt/_restore
   contract (compositions covered) governs — assert.
6. lookup hardening blast radius: seed.py, manifest.py,
   operator_bridge.py call lookup; hardening must only
   convert crashes into None (misses), never change a
   previously-successful resolution.

## Decisions on the ground's open questions (SWAT 4/4)

Q1 Resolve miss shape — Get (56) precedent, verified in
  code: atom ok=True; cell matched=False, confidence=0.0,
  error="missing", message "Resolve {label}=MISSING".
  Bare (no label): matched=False, conf 0.0,
  error="target_required". Hit: value=canonical name,
  matched=True, conf 1.00, predicate=requested label,
  message carries the dell number.
Q2 Reserved/alias scope — hits ONLY for dell 0-99
  (active registry). Reserved records (>=100 or
  RESERVED_NOT_ACTIVE) are honest misses. NAMED aliases
  resolving to 0-99 are hits at conf 1.00 (same record;
  canonical name published).
Q3 Guard locality — harden registry.lookup ITSELF
  (ASCII-digit check + length bound + int() guard):
  it is the shared authority and the crash class is
  DIR-F13's; call-site-only guarding would leave the
  other callers exposed. The Resolve handler treats
  None as a miss and never calls int() on the label.
Q4 Ungroup errors — named missing: ok=False,
  err=f"ungroup_missing:{name}" (family: delete_missing:,
  alias_missing), zero mutation, no scope warning.
  Bare with groups: last group (preserved). Bare with
  NO groups: ok=False, err="ungroup_missing:empty".
  Existing empty group: ok=True released=0 (distinct).
Q5 Compose publication — run first; publish/replace
  ONLY on success. Failure keeps the run's own error;
  message states "not published" and, when a prior
  binding exists, that the previous definition was
  retained. No rollback language outside transactions.

## Next executable action

Implement per the decisions above in nbd-omega-step10
(branch uni/step10-consistency): query_ops n==76 via
hardened registry.lookup; registry.lookup digit guard;
spectrum_ops n==83 membership refusal; n==99
run-before-publish. Suite form/step10_consistency_test.py
(probe witnesses + transaction/scope/cycle neighborhoods),
mutants M-R/M-U/M-C (defect-restoring, must fail the new
checks), regress x3, packet closure, PR, exact-head CI in
a separate step, merge with tree equality, fresh-clone
regress, ledger + POST_PLAN + register, Director report
DIRECTOR_REPORT_STEP10_CONSISTENCY.md published to
director-reports/ (held for the Director — he is asleep;
nothing is certified in his absence).

## Closure addendum — 2026-11-01

IMPLEMENTED-VERIFIED (awaiting Director ruling; he is
asleep — nothing certified). Candidate 262705f (tree
e12fad3), branch uni/step10-consistency, base 6c90039.
Commits: 89be6a1 (repairs + suite) + 262705f (exhibit
re-pins, below).

Repairs (all per the SWAT 4/4 decisions Q1-Q5):
- registry.lookup: ASCII-digit check + length bound
  (10) + int() guard — superscript/oversized digit-like
  labels are misses (None), never ValueError; every
  previously-successful resolution verified unchanged
  (suite L3).
- query_ops n==76: Resolve resolves its label via the
  hardened lookup; hits only for dells 0-99 (reserved
  records are misses); hit cell value=canonical name,
  matched=True, conf 1.00, message carries the dell
  number; miss cell matched=False conf 0.00
  error="missing"; bare error="target_required"; atom
  ok stays True (Get precedent).
- spectrum_ops n==83: named missing group refuses
  ungroup_missing:<name> with zero mutation; bare with
  no groups refuses ungroup_missing:empty; existing
  empty group still ok released=0; scope warning +
  Select scope_unknown preserved; refusal inside Try
  marks the frame failed and Catch consumes it.
- spectrum_ops n==99 define branch: run-before-publish;
  failure stores nothing / retains prior body; messages
  state "not published" / "previous definition
  retained"; no rollback language.

Suite: form/step10_consistency_test.py 34/34, added to
regress (entries 218 -> 219). Failing-first probe on
fixed code: 13/14 — the single FAIL is the probe's own
W-C2 expected-string typo (setup stored "82[Group]";
that exact body WAS retained); the suite asserts the
actual body. Mutants (defect-restoring, on committed
code, reverted by inverse restore + re-verified):
M-R 28/34 (fails exactly R7,R9-R13), M-U 31/34
(U1,U8,U9), M-C 32/34 (C1,C3); restored suite 34/34.

Sequel found by regress leg 1 (215/219 on 89be6a1):
four suites pinned the OLD defective behavior as
exhibits. Re-pinned to the repaired contracts in
262705f, supersessions recorded in place:
d1_registry_coreii_b_test (76/83 exhibits),
d1_registry_spectrum_test (99 exhibit: failing define
now NOT stored; executing the never-stored name fails
malformed_composition), d1_proof_cards_test (bare
survey 80/20 -> 79/21: bare Ungroup is a new honest
failure ungroup_missing:empty) + DELL_PROOF_CARDS.md
re-rendered (only Dell 83's bare line changed),
core_ii_smoke higher_order (Compose body is now a
CORE_II chain 51>70 that genuinely runs on the stub
harness — the old CORE_I-mix body only ever "passed"
because storage preceded its crashing run).
Neighborhoods all green (step9 24/24, step8 22/22,
step7 28/28, dirf13 17/17, dirf14 25/25, step3b 21/21,
step3c 24/24, step4 27/27, d1 query 15/12/14/17/14).

Regress x3 on 262705f: fwd 219/219 GREEN
(step10_logs/reg2_leg1_fwd.log); --twice both passes
219/219 GREEN (reg2_leg2_twice.log); --order rev
219/219 GREEN (reg2_leg3_rev.log). The first attempt's
leg 1 on 89be6a1 (215/219 RED, log reg_leg1_fwd.log)
is retained as the sequel evidence above.

Remaining at this addendum: PR + exact-head CI verified
in a SEPARATE step -> merge (tree equality) ->
fresh-clone regress -> ledger + POST_PLAN + register
-> Director report published to director-reports/.

## Final closure — 2026-11-01 (merge + fresh-clone)

PR #202 MERGED as e15c6a0 (merge tree e12fad3 ==
candidate tree e12fad3; parents 6c90039 + 262705f).
Exact-head CI on 262705f verified COMPLETE SUCCESS in
a SEPARATE step before merge (package 41352876100
SUCCESS 21:36:55Z; smoke 41352876419 SUCCESS completed
21:48:03Z; PR CLEAN/MERGEABLE on fresh verification).
Fresh-clone regress at merge e15c6a0: 219/219 GREEN
(step10_logs/freshclone_regress.log). Ledger row +
POST_PLAN note + register entry (B11/B12/B18 ->
IMPLEMENTED-VERIFIED) done. Director report
DIRECTOR_REPORT_STEP10_CONSISTENCY.md written;
publication to director-reports/ via docs PR follows
in a separate step. NOT certified — awaiting Director
ruling (he is asleep).
