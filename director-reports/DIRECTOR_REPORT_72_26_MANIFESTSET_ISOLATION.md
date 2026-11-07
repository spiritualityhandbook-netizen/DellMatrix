# DIRECTOR REPORT — 72-26: ManifestSet Member Isolation — One Member's Failure Touches Nothing Else

Circuit: 72-26 (Master Objective Register §6.7) — "Prove
ManifestSet member isolation (P1/E) (= SM-21)." Remaining
action on the row: "ManifestSet member-isolation proof
(one failing member, valid members execute, exact
receipts)." Acceptance: "One member's failure cannot
mutate sibling definitions or the set's receipt
accounting."

Executed as an EVIDENCE circuit under Sleep Protocol v2.
Branch: uni/72-26-manifestset-isolation, base main
130c0c6d3fd10cf4cc1c38ca2431b86a3038d959 (PR #322 merge).
Suite SHA: d4dc62e224fd38055c4c15345d1d893f410cdcbd.
NO production code changed. NO defect found.

## 1. Result (FACT)

A ManifestSet atom (label members separated by the
bullet U+2022, form/mandell/seed.py) expands into one
atom per member; each member is judged on its own at its
own re-entry. Prior coverage proves the per-member ARG
GATE (core_i_arg_gate_test, d1_unsupported_arg_gate_test:
every member refuses typed args per-atom, zero mutation)
and one shared-args Replace case (af1_chain_args_test).
What remained unproven was EXECUTION-TIME isolation. A
dedicated 18-check suite
(form/manifestset_isolation_test.py, registered in
form/regress.py — canonical count 253) proves it at the
public entry path (probe: hidden_files/72-26_probe.py):

- Mixed Delete set (Alpha present, Beta missing, Gamma
  present): receipts are exactly one per member, in
  member order — [ok, delete_missing:Beta, ok] — and
  BOTH sibling deletions commit. A member failure
  neither blocks the members after it nor rolls back
  the members before it. The chain error is the failing
  member's own error; chain_ran holds one entry per
  member; partial is True.
- All-fail set: every member carries its OWN error
  (delete_missing:X, delete_missing:Y); the chain error
  is the LAST member's, per the standing last-leaf
  summary contract (72-19/72-20); partial is False;
  nothing mutates.
- Mixed Patch set (second Dell family): [ok,
  patch_miss:Beta]; the sibling patch commits.
- Shared-args Replace chainlink: the rename commits
  exactly once and the second member honestly fails
  replace_missing:data (the error names the ARG, per
  AF-1). Reversed member order produces the same single
  rename, with receipts interleaved MEMBER-MAJOR across
  the linked atoms ([87 ok, 51 ok, 87 fail, 51 ok]) —
  chainlink expansion is pair-sequential, and the
  accounting shows it exactly.
- Inside a Sequence frame, a member failure is an
  executed failure (the Join judges it: join_fail)
  while the Sequence's later member still runs; inside
  an unchosen Branch arm, EVERY member of the set is
  skipped (one skipped receipt per member) and nothing
  mutates.
- Create sets are accounting-checked only (three
  receipts, chain_ran per member): no honest per-member
  failure mode exists for Create — duplicate members do
  not refuse — so no Create failure case is claimed.

## 2. Verification

- Suite: 18/18 at base (pins observed contract).
- Mutant: the set collapses to its first member at
  parse (proto members truncated to members[:1] in
  form/mandell/seed.py) -> 3/18: fifteen checks fail
  (every per-member receipt, sibling-effect,
  interleaving, frame, and accounting check);
  inverse-reverted, tree clean, 18/18.
- Regression at the suite SHA (logs
  hidden_files/72-26_logs/run1/): TERMINAL GREEN 253/253 x3 (fwd / --twice / --order rev; LEG1_RC=LEG2_RC=LEG3_RC=0, CHAIN_DONE present; the new suite runs inside the harness at 18/18)
- CI at the final PR head: __FINAL_CI__

## 3. Records carried in this PR

- This report + INDEX row.
- DIRECTOR_REPORT_72_25_DEFINE_COMPOSE_NONPUBLICATION.md:
  the CI/merge receipt placeholder completed
  (final-head CI all terminal PASS — Python package 42352059072, browser-acceptance 42352059058, Form smoke 42352059054 PASS 18m14s; PR #322 merged 130c0c6d3fd10cf4cc1c38ca2431b86a3038d959, tree 9976b9ea888784536bfb1e593fb4c3751f58d4fe; merged-main CI terminal SUCCESS — package 42353340739, Form smoke 42353340804).
- Register: 72-26 row updated (member-isolation proof
  landed; status stays PARTIAL for SM-21's wider scope).

## Anticipated probes

- "Is the Replace second-member failure a defect (the
  rename 'should' apply per member)?" — No: the args
  are shared by design (one rename instruction riding
  every member); after the first member renames the
  key, the key is gone, and replace_missing:<arg> is
  the honest per-member verdict. AF-1 pinned this
  contract; this circuit adds the reversed-order and
  receipt-interleaving evidence.
- "Does a member failure abort the set under any
  composition?" — Not in any probed composition:
  bare chain, Sequence frame, and chainlink all
  continue per member. The unchosen-arm case never
  executes any member (all skipped), which is the
  Branch contract, not an abort.

## Questions for the Director

- Q-72-26.1: Confirm the member-isolation proof
  satisfies 72-26's remaining action (row stays PARTIAL
  for SM-21's wider scope), or name the set composition
  you still want proven.
