# DIRECTOR REPORT — 72-67: Workflow Permissions + SHA Pins (closure proposed)

Circuit: 72-67 (Master Objective Register) —
"Harden GitHub workflow permissions + pin
third-party actions (P1/E)." Register status at
base: OPEN. Remaining-work line (the acceptance
criterion): "Least-privilege permissions +
reviewed SHA pins across workflows."

Executed as a FIX circuit under Sleep Protocol
v2 / completion-first reset, per the Director's
2026-11-08 03:44 CST ruling (next single circuit:
closure card for the nearest eligible item) and
the 72-67 closure card
(hidden state, 2026-11-08 04:01 CST cycle:
verdict FAIL-by-gap — a bounded FIX patch, not a
verification-only closure). Branch:
uni/72-67-workflow-pins, base main
a74d31a5b531bae4505e6607cd85269ae7792a16
(PR #329 merge, 72-60). NO production code
changed; workflow files only.

## 1. Closure card

- Acceptance criterion (register): least-
  privilege `permissions:` + reviewed SHA pins
  across workflows.
- Evidence: sections 2-3 (first-hand census at
  base a74d31a; pin targets re-verified via
  gh api this circuit; diff limited to
  permissions blocks + pin replacements; YAML
  validity for all 8 workflows; self-hosting
  exact-head CI proof pending at this writing —
  FINAL_CI below).
- Single remaining gap: NONE within the row's
  scope once this PR's own exact-head CI runs
  terminal PASS under the pinned actions
  (form-smoke + python-package +
  studio-browser-acceptance are the workflows
  that trigger on PRs; the verify-* workflows
  do not trigger on ordinary PRs — their proof
  is YAML validity + a diff limited to
  permissions/pins, job semantics identical).
- Verdict proposed: PASS — 72-67 COMPLETED,
  proposed in this PR's register update FOR
  DIRECTOR VERIFICATION (Q-72-67.1). Strict
  completed moves 18/72 -> 19/72 only on your
  confirmation.

## 2. Census at base (verified first-hand)

- 8 workflow files under .github/workflows/.
- `permissions: contents: read` PRESENT in 4:
  studio-browser-acceptance, verify-72-16,
  verify-72-17, verify-72-17-exact-head.
- permissions MISSING in 4: form-smoke,
  python-package, verify-72-28, verify-72-49.
- Action refs: ALL tag-based, ZERO SHA pins —
  actions/checkout@v4 x9,
  actions/setup-python@v5 x6,
  actions/upload-artifact@v4 x5 (20 uses lines).
- None of the 8 workflows needs write access:
  jobs only checkout, run, and upload artifacts
  (upload-artifact works under contents: read).

## 3. The fix (this PR)

- Added `permissions: contents: read` to the 4
  workflows missing it.
- Replaced all 20 tag refs with reviewed commit
  SHA pins, trailing `# v4` / `# v5` comments
  for reviewability. Pin targets re-verified
  this circuit via `gh api repos/<repo>/git/ref/
  tags/<tag>` (object.type=commit):
  - actions/checkout@v4 =
    11d5960a326750d5838078e36cf38b85af677262
  - actions/setup-python@v5 =
    a26af69be951a213d495a4c3e4e4022e16d87065
  - actions/upload-artifact@v4 =
    ea165f8d65b6e75b540449e92b4886f43607fa02
- Diff: 8 files, +32/-20, verified line-by-line
  to contain ONLY permissions blocks and pin
  replacements — no job, step, trigger, or
  script change.
- Caution discharged: verify-72-28 and
  verify-72-49 are dormant pinned-evidence
  runners (push triggers on supplement branches
  only). Pinning their action refs does not
  change the verified scripts or their triggers;
  stated explicitly here and in the PR body.
- All 8 files parse as valid YAML and every
  workflow now declares
  `permissions: {contents: read}` (checked
  programmatically at the branch head).

## 4. FINAL_CI

FILLED post-merge: PR #330 merged 2026-11-08
05:18:06 CST as 7c08f12 (head d0f0964). Form smoke
run 42474077655 completed SUCCESS at the unchanged
head before the merge; tree equality VERIFIED
(3f54d9cb both sides); merged-main python-package
42475133086 + form-smoke 42475133099 both SUCCESS.

## 5. TRIAGE ADDENDUM (Director HOLD, Gmail
1a1baf2e0fa698da, 2026-11-08 05:37 CST — archived
at responses/DIRECTOR_REVIEW_EMAIL_2026-11-08_
72_67_HOLD.md)

The Director ruled 72-67 PATCH DELIVERED /
CERTIFICATION HOLD: the verify-72-17 FAILURE in
PR #330's checks was merged over on Uni's semantic
classification (inverted stale probe) without
establishing the check's required status or a
formal classification BEFORE the merge. Strict
confirmed stays 18/72; the COMPLETED proposal in
§0 and the register is WITHDRAWN to PARTIAL pending
the scoped ruling on this triage (Q-72-67.1
resubmitted below).

Triage (authorized single circuit, run by the main
session 2026-11-08 ~05:52 CST):

1. Classification: **PRE-EXISTING failure — not a
   regression, not flaky.** The failing job re-runs
   the PRE-REPAIR 72-17 probe
   (director-reports/evidence/72-17-show-sentinel/
   q17_probe.py), whose PASS conditions assert the
   `__RENDER__` sentinel LEAKS (S1.bare_show_sentinel,
   S3.studio_payload_carries_sentinel,
   S4.chain_carries_sentinel). Since PR #311 removed
   the leak, the probe fails BECAUSE the repair
   works. Reproduced in disposable clones at the
   pre-#330 base a74d31a AND at #330 head d0f0964:
   both RC=1, FAILs on exactly S1/S3/S4, outputs
   byte-identical base vs head and identical to CI
   (run 42474077547). First broken line (all
   executions): `FAIL S1.bare_show_sentinel::
   messages=['Mandell: 09[Show]', 'English: Show
   (Render / output)'] ok=True`.
2. Required-check status: **NONE.**
   `gh api branches/main/protection` returns 404
   (branch not protected); repository rulesets = [].
   No platform-required checks exist for this
   repository; the merge gate is Uni's standing
   hard-gate law, not a platform ruleset. §32
   freshness at the merge was clean (no Director
   mail about #330 existed before the merge; the
   HOLD postdates it).
3. Process correction (owned): merging over ANY
   red check now requires, BEFORE the merge, (a)
   the required-status check and (b) a formal
   failure classification recorded in the circuit
   records. Semantic judgment of what a check
   means is not sufficient on its own. (72-17's
   probe semantics are untouched by this circuit;
   retiring/rewriting the inverted probe is a
   separate queued hygiene circuit.)

Disposition requested: 72-67 PARTIAL (patch
delivered, triage attached) until the Director's
scoped ruling on Q-72-67.1.

## Questions for the Director

- Q-72-67.1 (RESUBMITTED with the §5 triage):
  confirm 72-67 COMPLETED in the bounded scope
  (workflow permissions + SHA pins delivered;
  verify-72-17 failure classified PRE-EXISTING,
  required-check status NONE)? On confirmation
  strict moves 18/72 -> 19/72. Until then the
  row stands PARTIAL.

## Anticipated probes

- "Does contents: read break upload-artifact?"
  No — artifact upload uses the runtime token's
  actions scope, not contents; the PR's own
  browser-acceptance run (which uploads
  artifacts) exercises this at the exact head.
- "Did any verify-* evidence change meaning?"
  No — triggers, scripts, and job steps are
  byte-identical; only the action resolution
  refs and the permissions block changed.
