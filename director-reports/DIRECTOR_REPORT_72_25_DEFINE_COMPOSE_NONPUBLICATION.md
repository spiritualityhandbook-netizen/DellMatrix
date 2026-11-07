# DIRECTOR REPORT — 72-25: Failed Runs Publish Nothing — Proven Set-Wide

Circuit: 72-25 (Master Objective Register §6.7) — "Prove
Define/Alias/Compose failed-run non-publication (P1/E)
(= SM-19)." No remaining-action text beyond the row title;
original acceptance: "Failed composition must not publish
a partially built semantic object."

Executed as an EVIDENCE circuit under Sleep Protocol v2.
Branch: uni/72-25-define-compose-nonpublication, base main
374d7de51c4f62516bee88cc50224f7d1c033aca (PR #321 merge).
Suite SHA: 5cbb93dd25af4b720960f0eba2c2b7aa42188c42.
NO production code changed. NO defect found.

## 1. Result (FACT)

Step 10 (B18) repaired Compose's publication order and
its suite proves the in-memory core; the registry
spectrum suite proves Alias failure non-mutation. What
remained unproven was the SET-WIDE contract on the
surfaces those suites do not reach. A dedicated 15-check
suite (form/define_compose_nonpublication_test.py,
registered in form/regress.py — canonical count 252)
proves them at the public entry path (probe:
hidden_files/72-25_probe.py):

- A Compose whose define-run fails MID-BODY (Count ran,
  Diff failed) publishes nothing — not just failures at
  the first atom.
- Invoking an attempted-and-failed name is
  indistinguishable from invoking a never-defined name
  (both malformed_composition): no ghost object survives
  a failed run.
- Non-publication is visible ACROSS verbs: an Alias to
  a failed Compose name fails alias_missing and stores
  nothing — the name does not exist to point at — while
  an Alias to a published name binds normally.
- A failed redefinition retains the prior body, and the
  retained body remains invocable.
- A Define inside an unchosen Branch arm never
  executes, so nothing is published; the taken arm
  executes normally. A standalone Define publishes.
- Non-publication SURVIVES persistence: after the
  canonical save + load cycle (persist_rest.save /
  persist_rest.load — the path the REPL reloads
  through), the failed names (drop, part) are absent
  from the restored state and still uninvocable, while
  the successful sibling (keep) and its Alias are
  present and the composition runs.

## 2. Verification

- Suite: 15/15 at base (pins observed contract).
- Mutant: publish-on-failure restored in the Compose
  arm (the pre-B18 behavior) -> 5/15, exactly the ten
  non-publication checks fail (mid-body, single-failure,
  ghost-invoke, cross-verb Alias, redefinition
  retention, invocability, and all four persistence
  checks); inverse-reverted, tree clean, 15/15.
- Regression at the suite SHA (logs
  hidden_files/72-25_logs/run1/): TERMINAL GREEN 252/252 x3 (fwd / --twice / --order rev; LEG1_RC=LEG2_RC=LEG3_RC=0, CHAIN_DONE present; the new suite runs inside the harness at 15/15)
- CI at the final PR head: __FINAL_CI__

## 3. Records carried in this PR

- This report + INDEX row.
- responses/DIRECTOR_REVIEW_EMAIL_2026-11-07_72_21_
  CONDITIONAL_PASS.md: archive of your 72-21 ruling
  (bounded technical PASS conditional on terminal CI —
  condition satisfied before merge; Q-72-21.1 YES).
- DIRECTOR_REPORT_72_21_LOOP_BOUNDS.md: the CI/merge
  receipt placeholder completed (final-head CI all
  terminal PASS — Python package 42347757572,
  browser-acceptance 42347757620, Form smoke 42347757733
  PASS 19m28s; PR #321 merged
  374d7de51c4f62516bee88cc50224f7d1c033aca, tree
  a41690b0c3e2f027432edd3e01532f106eb1d818; merged-main
  CI terminal SUCCESS — package 42349137986, Form smoke
  42349137956).
- Register: 72-25 row updated (non-publication proof
  landed; status stays PARTIAL).

## Anticipated probes

- "Does the run's own side effect persist while the
  name does not?" — Yes, by B18's stated design ("the
  run's own effects persist; no rollback is implied"):
  publication is the gated act, not the execution. This
  suite pins the publication side set-wide; the
  effects-persist side is Step 10's recorded contract.
- "Is open_program a counterexample (it loads without
  compositions)?" — No: open_program is the light
  test-scaffolding constructor; the canonical load is
  persist_rest.load (the REPL's reload path,
  form/repl.py), which restores compositions and
  aliases. The suite's persistence leg uses the
  canonical path deliberately and says so.

## Questions for the Director

- Q-72-25.1: Confirm the set-wide non-publication proof
  satisfies 72-25's acceptance (row stays PARTIAL for
  SM-19's wider scope), or name the failed-run surface
  you still want proven.
