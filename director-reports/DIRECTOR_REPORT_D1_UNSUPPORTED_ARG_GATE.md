# DIRECTOR REPORT — D1-UNSUPPORTED-ARG-GATE

**Circuit:** D1-UNSUPPORTED-ARG-GATE (MODE C — REPAIR, authorized by the
Director's ruling on PR #252, 2026-11-03, with amendments Q-D1–Q-D4 and
the names-only diagnostics amendment)
**Status:** SUBMITTED — awaiting Director certification. PR UNMERGED by
design (certification gate).
**Base:** `0f6dcb8d4d701c6fd6b47d60da709520a6289404` (main, PR #252 merge;
tree `292a77ac709c6eb1f0f7ead0a84e29d9a34af738`)
**Code head:** `7328cef9b0ed8d93e23ec82c42d7776a5e2eb41a` (branch
`uni/d1-unsupported-arg-gate`; tree
`3830434bcbe29f1e7147c966d449366f6690e79e`). The production fix is
commit `91f9371`; `7328cef` adds suite coverage only — production
code is identical in both.
**Submission head:** the head of the PR branch at submission (this
report + evidence commits on top of the code head; the exact head
and tree are recorded in the Submission Verification addendum at
the end of this report and in the PR description).

## What was wrong (PR #252, Q1 — confirmed class)

Typed arguments on the 33 unregistered Core II Dells (51–99 minus the 17
registered) were never read: the atom executed on its legacy payload and
reported success — under a silent default (`82[Group](name="greens")`
created `group`), with the label silently winning when both were present,
or under a misleading handler failure (`78[Cause]` reported
`malformed_relation` for an empty label instead of refusing its args).

## The repair (form/mandell/chain_exec.py only; +57/−5)

1. **The gate** — in `_run_atom`, the TOAM block gains the missing `else`
   on `has_signature(n)`: when the parsed `atom.args` dict is nonempty,
   the Dell is 51–99, and no typed signature exists, the atom refuses
   BEFORE `execute_core_ii` runs. Error class `UNSUPPORTED_ARGS`
   (Q-D1, its own class — UNKNOWN_ROLE is not overloaded). The
   diagnostic carries **sorted role NAMES only**; raw argument values
   are never echoed in the error, the receipt, the messages, or the
   REPL surface (Director amendment). The receipt is the established
   atom shape `{ok: False, skipped: False, error, reason}` produced by
   the existing `execute_range` wrapping, and chain continuation is the
   existing policy (FlowTo continues, FlowThru blocks) — no new policy.
   Because the gate keys on the parsed args dict at the exact point
   Q6 identified, legacy labels (parens, `=`, quotes, fully arg-shaped
   text after `::` — all parse with `args == {}`) are structurally
   inert, and atoms that never execute (reserved, flow-blocked,
   branch-not-taken) never reach the gate: their args are never
   inspected.
2. **Control heads (Q-D2 Option A)** — `_run_control` dispatches the
   head through `_run_atom`, so a gate refusal arrives as the head
   receipt. A structural short-circuit ahead of every kind branch
   then: marks the frame `fail` with the refusal as its error, gives
   every body occurrence an honest `_skip_receipt` ("control head
   refused: …; body occurrence not executed"), keeps iterations at 0,
   and sets the chain state error only if none was recorded. The Join
   still closes the frame and publishes the failed frame normally.
   This is not a receipt cosmetic: the body dispatch (including the
   While/Until bounded loops and the ForEach member loop) is never
   entered.
3. **Join (Dell 61)** — a Join carrying unsupported args is itself
   gate-refused in `_run_atom` before the core Join arm runs. In
   `_run_control`'s Join accounting, when the Join receipt's error is
   an `UNSUPPORTED_ARGS` refusal, the frame/chain error names that
   refusal instead of the generic `join_fail` — under the same guards
   as the existing law: an earlier recorded refusal is never
   overwritten (first root cause preserved), and the closure is never
   faked successful.

No signatures were added (typed count stays **17**), no handler,
parser, Core I, or `flow_executor` code changed (Q-D3, Q-D4).

## Evidence (all in-PR at `director-reports/evidence/d1-unsupported-arg-gate/`)

- **Failing-first:** the new suite `form/d1_unsupported_arg_gate_test.py`
  run against the unchanged base executor: **20/43, exit 1**
  (`red_run.log`) — every gate-behavior check red, every preservation
  check (legacy corpus, registered behavior, skip semantics, the J3
  pre-existing-refusal frame semantics) green on the base. The final
  45-check suite (two ManifestSet checks added after probe-grounding
  the member grammar) was re-verified against the base executor:
  **21/45, exit 1** (`red_run_v2.log`) — the typed ManifestSet check
  red on base, the legacy ManifestSet check green on base (it is a
  preservation check).
- **Base probe:** `probe_base.py` / `probe_base.log` — base behavior of
  every shape the suite pins (label grammar, control frames, the
  bound-reached While/Until behavior the gate replaces with refusal).
- **After the fix:** suite **45/45, exit 0** (`green_run_v2.log`;
  the 43-check version's green + post-mutant runs are `green_run.log`
  / `post_mutant_green.log`). Adjacent suites: `d1_typed_52_53`
  28/28, `af1_chain_args` 13/13 (the AF-1 Core I parity pin —
  unchanged).
- **Coverage shape:** the 33-Dell sweep derives the untyped set LIVE
  from the canonical registry + signature source and pins it against
  drift; every refusal case asserts business-state snapshot equality
  (store, groups, selected, scope, defs, aliases, compositions,
  causes, last_result, Plane units, control steps). The suite covers:
  all 33 Dells; family witnesses (82/97/78 incl. sorted multi-role
  names and the banished `malformed_relation`); FlowTo/FlowThru
  continuation; registered regressions (52/53/55 incl. precedence and
  ARGUMENT_CONFLICT); the Q6 legacy corpus; reserved 151 and
  flow-blocked atoms (args never inspected); all six control heads +
  Else-arm, nested, and flow-blocked-head cases; Join J1/J2/J3; the
  canary disclosure test; ManifestSet members; and a literal REPL
  transcript (REAL_USER_PATH).
- **Canary scoping (interpretation flagged for the Director):** the
  no-raw-value assertion covers every diagnostic surface the REFUSAL
  generates — top-level error, all receipts, and all refusal-appended
  messages. The one place the caller's value still appears is the
  universal seed-echo header (`Mandell:` / `English:` lines and the
  result's `seed` field), which reproduces the user's own input text
  for EVERY chain, success or refusal, pre-dating this circuit. The
  suite asserts that scoping explicitly (the echo contains the
  canary; no refusal diagnostic does). See Question 1.
- **Mutants (all killed, each reverted by inverse edit with an empty
  `git diff` verified; logs `mutant_m1..m5.log`):**
  M1 gate without the signature condition → registered-Dell checks red;
  M2 gate without the args-nonempty condition → 15 red (legacy labels
  refuse); M3 diagnostics echo values → 14 red (canary disclosed);
  M4 head short-circuit removed → 10 red (bodies execute under refused
  heads); M5 Join overwrites the recorded refusal → exactly J2 red.
  Scope note: mutants ran against the 43-check suite; the two
  ManifestSet checks were added afterward with their own
  failing-first verification (above). Production code is unchanged
  between the mutant runs and the final code head.
- **Regression ×3 sequential** on the final code tree (`7328cef`):
  forward **225/225 GREEN** (exit 0, `regress_fwd.log`); `--twice`
  **225/225 GREEN in both passes** (exit 0, `regress_twice.log`);
  `--order rev` **225/225 GREEN** (exit 0, `regress_rev.log`). The
  new suite's entry reads 45/45 in every leg.
- **Evidence bundle:** 16 files at
  `director-reports/evidence/d1-unsupported-arg-gate/` with
  `MANIFEST.md` (SHA-256, 16/16 verified; manifest digest
  `048d7c8311e4ab915587560cbe22324429510c5eb2a8b163f236ea3d82a7f8a1`;
  the bundle was extended by the Submission Verification addendum
  to include the fresh-clone regress log).

## Anticipated probes

- *Does the gate fire for atoms inside control bodies?* Yes — body
  atoms dispatch through the same `_run_atom` (J2's body refusal is
  exactly that), with the frame's first-root-cause law preserving the
  earliest refusal.
- *A refused head inside a larger chain — does the chain continue?*
  Per the existing atom-failure policy: the frame fails, occurrences
  after the Join continue under FlowTo (pinned by the nested-head
  check: trailing `55[Set]` executes) and block under FlowThru.
- *ManifestSet / chainlink members?* Args ride every member atom
  (PR #252, Q6); each member refuses individually — pinned in the
  suite.
- *Studio `/api/execute`?* It rides `execute_seed` (code-verified in
  PR #252, Q5), so the gate applies identically; no separate Studio
  change was made or needed.
- *Why is the head short-circuit keyed on the error string?*
  `UNSUPPORTED_ARGS` is produced by exactly one site (the gate), and
  the head receipt is the only channel `_run_control` has for the
  head's verdict; the alternative (a new out-of-band flag) would add
  a second signal path through every receipt consumer.
- *Frame bookkeeping on refusal:* `last_frame`/`frames` DO record the
  refused frame — that is the refusal's own receipt trail, not
  business state; the zero-mutation claim is scoped to business state
  and the suite's snapshot says exactly which fields it covers.

## Questions for the Director

1. **Canary scoping:** is the seed-echo exclusion (the caller's own
   input text in the universal result header) the correct reading of
   the names-only amendment, or should the echo itself be treated as
   a diagnostic surface for refused chains?
2. **Head short-circuit placement:** the short-circuit sits ahead of
   all kind branches in `_run_control` and lets the Join close the
   frame normally. Is publishing a failed frame (rather than no
   frame) the desired record for a refused head?
3. Sequencing confirmation: after this gate, the stated priority is
   Studio security + browser acceptance, then the Core I contract
   review from the AF-1 pin, then Track D bridge planning — proceed
   in that order on certification?

## Submission verification

Exact-head CI on the submission head and a fresh-clone run at that
head are executed after the PR opens; their verdicts are appended
to this section by a documentation-only addendum commit (the
addendum changes no code or tests) before certification is
requested. The PR description records the final head and its CI
state.

### Addendum — verification verdicts (2026-11-03)

- **Submission head verified:** `44905d6f90c205d4d64f01ae0f30dc16c9910d8c`,
  tree `03ef51bd5a932d254472fffb585d99883cc5052f` (PR #253 OPEN,
  MERGEABLE, base `0f6dcb8` — confirmed by direct `gh pr view`).
- **Exact-head CI on `44905d6`:** Python package run `41677891772`
  — **SUCCESS**; Form smoke run `41677891668` — **SUCCESS** (both
  verified by direct `gh run view` on the exact head, terminal
  state).
- **Fresh-clone at `44905d6`:** cloned from GitHub, checked out at
  the exact head/tree above; full regress **225/225 GREEN**,
  exit 0, the new suite's entry 45/45 (`freshclone_regress.log`,
  added to the evidence bundle with this addendum; manifest
  regenerated 16/16).
- This addendum commit is documentation-only (this report + the
  bundle's fresh-clone log + manifest). CI on the resulting final
  head is verified separately and recorded in the PR description.
