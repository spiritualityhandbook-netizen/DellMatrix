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

PENDING at PR opening — self-hosting proof: this
PR's exact-head form-smoke, python-package
(3.10/3.11) and studio-browser-acceptance runs
execute under the pinned actions themselves and
must be terminal PASS before merge (hard gate,
main-session merge only, §32 re-checked
immediately before merge). Filled by the
post-merge records update.

## Questions for the Director

- Q-72-67.1: confirm 72-67 COMPLETED on merge
  (strict 18/72 -> 19/72)? The register row in
  this PR proposes COMPLETED for your
  verification, per the 72-60 pattern.

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
