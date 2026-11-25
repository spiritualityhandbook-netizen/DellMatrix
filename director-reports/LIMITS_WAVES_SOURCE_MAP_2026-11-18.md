# LIMITS WAVES 1–5 — CONSOLIDATED LANDING SOURCE MAP (2026-11-18)

**What this is.** The five Elastic-Limits verification wave records
(PRs #432, #435, #438, #442, #445) sat open and CONFLICTING on stale
bases; their full probe evidence existed nowhere on main. Under the
Director's ruling on PR #427 (2026-11-18) authorizing "the five-wave
records PR with per-PR source map," and the sweep-lane B6
recommendation, this PR lands waves 1–5 **verbatim** in one refreshed
combined records PR on current main
(`44191a8960303083bff448d1998f76127b0d406f`). The five source PRs
close as SUPERSEDED by this landing only after it merges and the
authorities confirm. **Records only. No product code. No credit.**

The limits reconciliation matrix (PR #482, merged) is a separate
record and is NOT duplicated here.

## Per-PR source map

Verification method (all files): the carried blob on this branch was
compared by git blob SHA against the blob at the source PR's head
(`git rev-parse <head>:<path>` vs `git hash-object` of the landed
file). MATCH = byte-for-byte identical.

### PR #432 — Wave 1: five census items (R2–R6)

- Source head: `2e95b4317226040e8d2d7e6a8d6801130b92e157`
  (branch `uni/limits-wave1-1115`); source base:
  `17ae4ce86743d9c5ff848a1b48111119d9bf9a32`.
- Files carried:
  - `director-reports/LIMITS_VERIFICATION_WAVE1_2026-11-15.md`
    (added; 142 lines) — blob `476efaf88b6dc23bd84e2c2f837dc0f195fd1428`
    at source head; landed blob identical. **MATCH.**
  - `director-reports/INDEX.md` — the PR's single added row
    (union, see below).
  - `director-reports/DIRECTOR_REVIEW_QUEUE.md` — the PR's single
    added row (union, see below).

### PR #435 — Wave 2: R7–R11

- Source head: `e2322739a781a067d8f13173b0723bcd3a4b3cae`
  (branch `uni/limits-wave2-1115`); source base:
  `04abc1ea9c1296e0605ed18b303eb9b6babfb799`.
- Files carried:
  - `director-reports/LIMITS_VERIFICATION_WAVE2_2026-11-15.md`
    (added; 217 lines) — blob `5c28cfb51959f1c981a76058c95290659fecfb66`
    at source head; landed blob identical. **MATCH.**
  - `director-reports/INDEX.md` — single added row (union).
  - `director-reports/DIRECTOR_REVIEW_QUEUE.md` — single added row
    (union).

### PR #438 — Wave 3: R12–R16

- Source head: `da339a09cd426748fc66382c4e26431c9d399843`
  (branch `uni/limits-wave3-1115`); source base:
  `04abc1ea9c1296e0605ed18b303eb9b6babfb799`.
- Files carried:
  - `director-reports/LIMITS_VERIFICATION_WAVE3_2026-11-15.md`
    (added; 242 lines) — blob `3776c123d8a1e097646984f7cbac8161947de4d7`
    at source head; landed blob identical. **MATCH.**
  - `director-reports/INDEX.md` — single added row (union).
  - `director-reports/DIRECTOR_REVIEW_QUEUE.md` — single added row
    (union).

### PR #442 — Wave 4: R17–R21

- Source head: `19a62188be56ee36b9311957518f1e3a664841c6`
  (branch `uni/limits-wave4-1115`); source base:
  `56b6d9cb40cb68d3f50e4c39537769b242cb13a7`.
- Files carried:
  - `director-reports/LIMITS_VERIFICATION_WAVE4_2026-11-15.md`
    (added; 341 lines) — blob `fa8249001e692576a87823537824f09b1eb7597a`
    at source head; landed blob identical. **MATCH.**
  - `director-reports/INDEX.md` — single added row (union).
  - `director-reports/DIRECTOR_REVIEW_QUEUE.md` — single added row
    (union).

### PR #445 — Wave 5: R22–R26

- Source head: `b6a325dc01ca53fd5b675410900b5b0ac2ded35d`
  (branch `uni/limits-wave5-1115`); source base:
  `56b6d9cb40cb68d3f50e4c39537769b242cb13a7`.
- Files carried:
  - `director-reports/LIMITS_VERIFICATION_WAVE5_2026-11-15.md`
    (added; 308 lines) — blob `9ce4f3577a5987986c7c7aeba8f96dd7c901959f`
    at source head; landed blob identical. **MATCH.**
  - `director-reports/INDEX.md` — single added row (union).
  - `director-reports/DIRECTOR_REVIEW_QUEUE.md` — single added row
    (union).

## Union reconciliations (shared files)

Each source PR, relative to its own base, added exactly **one line**
to `INDEX.md` and **one line** to `DIRECTOR_REVIEW_QUEUE.md`
(pure additions; zero deletions in every source diff). The five
INDEX rows and five queue rows are all distinct, and none was
present on current main (waves 6–8 rows were; waves 1–5 were not).

- `director-reports/INDEX.md`: **+5 / −0** against current main.
  The five wave rows were inserted immediately after the existing
  wave-6 row, in descending wave order (5, 4, 3, 2, 1), so the
  family block now reads 8, 7, 6, 5, 4, 3, 2, 1.
- `director-reports/DIRECTOR_REVIEW_QUEUE.md`: **+5 / −0** against
  current main. Same placement: after the wave-6 row in the
  "Awaiting disposition" table, descending wave order.
- Every carried row is **byte-verbatim**, including its original
  "(this PR)" self-reference, which in each source PR denoted that
  PR; this map is the provenance record tying each row to its
  source PR and head above.
- Verification: each of the ten source lines occurs exactly once as
  a full line in the landed files; the landed diff against main
  contains zero deletions. No content from either side was dropped.
  No true verbatim conflict existed — the five PRs touched disjoint
  lines of the shared files.

## ADDENDUM — R26 fourth loss site (Director post-merge check, PR #482)

Source: Director comment **6974852887** on PR #482 (post-merge
check, 2026-11-18), ruled to join this records package.

The R26 site list — in the wave-5 record landed above and in the
merged reconciliation matrix (PR #482) — named **three** write-path
sites where DuoBeta learning-ledger detail is cut to 120 chars:

- `form/duobeta/growth.py:59`
- `form/mandell/duobeta_learn.py:134`
- `form/persist.py:345`

The list is amended to **FOUR** sites, adding the read-path site the
matrix missed:

- `form/persist_rest.py:471` — inside `_restore_duo_ledger`
  (defined at `form/persist_rest.py:440`): on load, each restored
  ledger entry's detail is clipped,
  `detail=str(e.get("detail", ""))[:120]`. The Director reproduced:
  200 chars in → 120 restored, metadata intact. Uni verified the
  site first-hand on main `44191a89` (2026-11-18): line 471 carries
  exactly that clip.

Consequences: the repair shape for R26 must lift all four sites
together — a repair lifting only the three write-path cuts would be
silently re-imposed at load by the fourth. **The seven-defect count
is unchanged** (R26 remains one defect; this addendum widens its
site list, it does not add a row). The merged matrix (PR #482)
stands as the dated record; this addendum corrects its R26 row
prospectively.

## Scope statement

This PR changes records under `director-reports/` only: five wave
report files added verbatim, ten union rows added to two shared
record files, and this source map (including the R26 addendum
above). No product code, no tests, no state. No completion credit
of either belt is claimed.
