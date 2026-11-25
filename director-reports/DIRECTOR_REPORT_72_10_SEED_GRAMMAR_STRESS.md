# DIRECTOR REPORT — 72-10: Seed Grammar Stress Battery Holds Set-Wide

Circuit: 72-10 (Master Objective Register §6.7) —
"Stress Seed grammar + error precedence (P1/I)
(= SM-58)." Remaining action: "Full stress battery
(nested delimiters, escaped Unicode, ManifestSet,
no-mutation-on-reject) as one suite — not evidenced."

Executed as an EVIDENCE circuit under Sleep Protocol
v2. Branch: uni/72-10-seed-grammar-stress, base main
3ebef3515e2de66cb27a313b95794f71647a232b (PR #324
merge); main ff5c2ccbe6681b5ae08ba5ffb3016ef7fa4a57c0
(PR #325 merge) merged into the branch before the
records commit (regress.py registration conflict
resolved by keeping both suites). Suite SHA:
92046c9de77db9e28ef38a28780125aa83046253.
NO production code changed. NO defect found.

Sequencing note (transparent): this circuit was
opened at 04:01 CST 2026-11-07, before your 04:10
CST instruction naming 72-33 the next single
circuit. Ace sequenced 72-10 first, then accepted
Uni's judgment to park it (branch pushed at 92046c9;
the worktree's uncommitted mutant left frozen) and
run 72-33 first. Your Q-72-33.2 ruling (07:31 CST)
confirmed the resume order. On resume the mutant was
inverse-reverted (zero-diff verified, suite 25/25)
before the regression chain ran. No parallel
circuit work occurred at any point.

## 1. What already existed (reused, not duplicated)

DAF-07 is certified within tested grammar scope;
af1/af2 suites cover chainlinks and delimiters; the
72-26 circuit proved ManifestSet member isolation
for well-formed sets. This circuit adds the missing
stress battery as ONE suite: nested delimiters,
Unicode handling, the ManifestSet malformed-shape
reject family, no-mutation-on-reject scoping, and
error precedence.

## 2. Result (FACT) — the battery

A dedicated 25-check suite
(form/seed_grammar_stress_test.py, registered in
form/regress.py; probes hidden_files/72-10_probe.py
+ 72-10_probe3.py) pins at execute_seed
(PUBLIC_ENTRY_PATH, isolated owners):

- Nested delimiters: label 'a>b=c' stores key 'a>b'
  (longest-existing-key / first-'=' discipline);
  brackets and parens inside label data stored
  verbatim / carried ('x(y)' -> unit x_y, ID
  sanitization); '::' INSIDE a label is a loud parse
  refusal ("unexpected at 11"), zero mutation —
  AF-2 pinned behavior.
- Unicode: non-ASCII labels/values stored verbatim
  (café=☃), combining marks preserved; a literal
  backslash-u sequence is stored LITERALLY (no
  escape decoding in the label path — pinned as
  observed contract; Q-72-10.2). An emoji Create
  label falls to the leaf path and creates the
  fallback unit 'idea' (name not carried) —
  consistent with ID sanitization; pinned, not
  claimed as a defect.
- ManifestSet malformed shapes each refuse LOUDLY
  at parse with a DISTINCT error, zero mutation,
  zero receipts: comma separator -> "• not ,";
  U+00B7/U+2219/U+30FB lookalikes -> "invalid
  unicode — ManifestSet separator is •"; empty
  member -> "empty member"; nested brackets ->
  "aggregate Dell conflict — use explicit atom
  form"; members containing '=' or '>' ->
  "invalid manifest member". A non-ASCII member
  ('Twø') also refuses "invalid manifest member" —
  the _MEMBER charset is ASCII-only (Q-72-10.1).
- Well-formed sets keep 72-26 isolation inside the
  battery (per-member receipts in order, siblings
  commit, chain error = failing member).
- No-mutation-on-reject, scoped exactly: parse-level
  rejects and per-atom gate rejects mutate NOTHING
  (store/units snapshot identical). A mid-chain atom
  failure does NOT roll back earlier atoms — the
  established failure-continuation semantics
  (72-19/72-20/72-21), pinned as the scope of the
  register's phrase, not a violation.
- Error precedence: (1) parse errors pre-empt all
  execution (zero receipts, zero mutation) and
  pre-empt the arg gate; (2) per-atom gate errors
  surface in atom order, chain error = LAST atom's
  error (last-leaf summary, 72-19 contract);
  (3) an unknown Dell carrying typed args reports
  UNSUPPORTED_ARGS rather than
  malformed_composition (gate-before-existence).

## 3. Verification

- Suite: 25/25 at base (pins observed contract);
  re-verified 25/25 after the park/resume
  inverse-revert (zero-diff) and again on the
  merged tree at the records commit.
- Mutant: the split_manifest_set member validation
  silenced (`if False:`) -> suite 23/25, FAILs
  exactly M7.member_delim_chars and
  M8.nonascii_member. Killed exactly; verified
  independently twice (main session in the live
  worktree; the 06:01 CST cycle in a disposable
  clone); reverted by inverse edit only, verified
  ZERO-DIFF against HEAD.
- Regression at the suite SHA (logs
  hidden_files/72-10_logs/run1/): TERMINAL GREEN
  255/255 x3 (fwd / --twice / --order rev;
  LEG1_RC=LEG2_RC=LEG3_RC=0, CHAIN_DONE
  2026-11-07 14:40 UTC). The branch carries 255
  suites; the PR tree unions this registration with
  72-33's (256) and PR CI exercises the union.
- CI at the final PR head: PR-head package 42384871312,
  Form smoke 42384871203, browser-acceptance 42384871228,
  all terminal SUCCESS at d4ffc12ab9811608ca575a494f61eaf1ff929cd9;
  PR #326 merged 0a4c4b69f1da05c2c1e68d0257ef3e70ec9272cf;
  delivered merge tree a27cc709442665c6f0806dc2851353cdca5e0235
  == frozen candidate tree; merged-main package 42387509030
  + Form smoke 42387509036 terminal SUCCESS.

## 4. Records carried in this PR

- This report + INDEX rows (report + ruling
  archive).
- responses/DIRECTOR_REVIEW_EMAIL_2026-11-07_72_33_
  BOUNDED_PASS.md: verbatim archive of your
  2026-11-07 07:31 CST ruling (72-33 bounded
  ALL_AI_CONFIRMATION_PASS on Q-72-33.1;
  Q-72-33.2 YES — resume parked 72-10 next).
- DIRECTOR_REPORT_72_33_SUPERSESSION_LINEAGE.md:
  the FINAL_CI placeholder completed per your
  post-merge asks (PR-head package 42375318715,
  Form smoke 42375318753, browser-acceptance
  42375318758, all terminal SUCCESS at eb1d633e;
  PR #325 merged
  ff5c2ccbe6681b5ae08ba5ffb3016ef7fa4a57c0;
  delivered merge tree
  c92be579c1748955c0210bc285d0aec780872ee0
  IDENTICAL to the frozen candidate head tree —
  git-verified on both commits; merged-main CI on
  the push-workflow route terminal SUCCESS —
  package 42378009309, Form smoke 42378009212).
- Register: 72-10 row updated (battery landed;
  status stays PARTIAL for SM-58's wider scope).

## Anticipated probes

- "Is the ASCII-only ManifestSet member charset a
  defect?" — Not claimed as one. It refuses loudly
  with zero mutation, so no corruption path exists;
  whether the restriction is intended or over-narrow
  is a contract reading (Q-72-10.1), not a Uni
  defect claim — the same posture as the 72-13
  documentation-drift classification.
- "Does no-mutation-on-reject hold for a whole
  chain?" — Scoped honestly: it holds per rejected
  atom and at parse. Earlier committed atoms are
  NOT rolled back when a later atom fails; that is
  the established failure-continuation contract
  proven in 72-19/72-20/72-21, and the suite pins
  exactly that scope.

## Questions for the Director

- Q-72-10.1: Is the ASCII-only ManifestSet member
  charset (_MEMBER) the intended contract, or
  should non-ASCII member names be admissible? No
  behavior change is proposed in this circuit.
- Q-72-10.2: Confirm the literal backslash-u
  storage (no escape decoding in the label path)
  and the emoji-label fallback-unit behavior are
  the intended observed contract, or name the
  surface still wanted.
- Q-72-10.3: Confirm the 25-check battery satisfies
  72-10's remaining action (row stays PARTIAL for
  SM-58's wider scope), or name the grammar surface
  still wanted.
