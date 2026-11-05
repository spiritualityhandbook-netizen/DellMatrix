# Q1 Audit — Fresh-Clone Replay of W1/W2/W3 (Director review #4 order)

Executed by Uni during SUSX100,000 Cycle 12, 2026-11-05, in
response to Director hourly review #4 (Gmail id
1a1aa949e4c14ee8, 2026-11-05 01:20 CST): "provide a fresh-clone
replay of W1/W2/W3 with artifact digests and unchanged source."

## Method

- Fresh clone: `git clone
  https://github.com/spiritualityhandbook-netizen/DellMatrix`
  into a disposable directory, 2026-11-05 ~02:05 CST.
- Clone HEAD: 8e0784cd15d78d60a148c09942d3a185fec07529
  (== current main; PR #294 is docs-only, so the code under
  probe is exactly main's code).
- Probe: the PR-bundled `q1_probe.py` artifact itself, copied
  out of `director-reports/evidence/q1-audit/`; its SHA-256
  (below) matches MANIFEST.sha256 — the replay ran the exact
  submitted artifact, not a working-paper variant.
- Two full runs (`parent` mode, genuine child OS processes,
  coordination seams only, per-owner isolated state inside
  the clone's own `form/state`):

      python3 q1_probe.py parent --workdir <coorddir>

## Source digests — before and after (UNCHANGED)

Recorded in the clone before run 1 and re-recorded after
run 2. `git rev-parse HEAD` identical, `git diff` = 0 lines,
`git status --porcelain` empty for tracked files.

| file | SHA-256 |
|---|---|
| form/dell_matrix/exchange.py | fcf16ab0321952e15f5e72349168763fb13bdbce16265acd9350e8b9b85dba84 |
| form/persist_rest.py | ac5d711da630355e57d3d7175052ad04b765cd8c823a95dfb884990e159ccd21 |
| form/open.py | cc42dbedb4642706801c3b4878eda0ab22a9f258401d3ed1a45d7514bb36f429 |
| q1_probe.py (bundled artifact) | 7f7653ae7c12dd0be0f904a117740e7c69b62508bd875488b68248d895fc93bc |

## Replay artifacts (this directory)

| file | SHA-256 |
|---|---|
| q1_replay_run1.log | e39a1ad65aa284d1504e8d36d849ca140a69368b1d4873ea57b1ec9e1727f750 |
| q1_replay_run2.log | e39a1ad65aa284d1504e8d36d849ca140a69368b1d4873ea57b1ec9e1727f750 |
| q1_replay_verdicts.json | 800d6c33240cf2153b99ec9394f1552b4c2871a7e54588895eed641cc24adf9c |

The two run logs are byte-identical to each other, and the
two verdict sets are identical.

## Verdicts — all three windows REPRODUCED

- **W1 CONFIRMED again:** marker present after the locked
  save (true), absent after the recovery writeback (false);
  finding string identical: "recovery writeback erased the
  locked save's marker unit".
- **W2 CONFIRMED again:** one recovery returned
  "removed"/"already_absent" (see nuance), the other raised
  the spurious `ExchangeError` ("…but the import journal
  could not be cleared; recovery evidence retained for
  retry"); final state clean, journal disposed.
- **W3 CONFIRMED again:** importer returned ok=True with
  journal_retained disclosed; final program file holds the
  seed + receipts, final nursery file holds NO proposal —
  the ok=True incoherence reproduces exactly.

## One disclosed nuance vs the original bundle

Field-for-field, the replay verdicts differ from the
original `q1_probe_verdicts.json` in exactly ONE string: the
W2 error message's established-outcome word — original
"'removed'", replay "'already_absent'". Which of the two
concurrent recoveries establishes which outcome label
depends on the interleaving; the defect itself (a spurious
`ExchangeError` raised over cleanly removed state, failing
the load closed) is identical in both. No other field
differs.

## Exact-head CI (PR #294, head 4a126b2f, read same-step)

build (3.10) PASS, build (3.11) PASS, smoke PASS (18m8s) —
all terminal. The Director's "wait for all exact-head checks
to terminate" condition is met at the reviewed head; this
addendum changes the head, so the new head needs re-review
(per the review's own rule) and the merge hold continues
until the Director rules on the replay + repair plan.
