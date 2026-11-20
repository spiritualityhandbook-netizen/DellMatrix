# GATE RECONCILIATION RECORD — SM-07 design record (Part 0, 2026-11-20)

**Status:** DESIGN RECORD at plan stage. Part 0 — The Scoreboard,
branch `uni/part-0-scoreboard`, base main
`af2519b6d239ef278397e277210d6da2467c36e5`. Register row #91
(SM-07): "Strengthen exact-head / merge-tree / post-merge /
fresh-clone gate reconciliation". Per-merge reconciliation records
in this format begin when the reconciler is adopted at code stage;
this document fixes the contract they will follow.

## 1. The defect this closes

The merge gate today is four separate rituals plus a freshness
check, held together by prose (AGENTS.md section 32), a skill
(`verify_merge_gate_before_merging`), and operator discipline.
Each leg is performed, but the legs are never *reconciled* into one
verdict over one frozen candidate, and a leg can be performed
without leaving a retrievable record. Standing proof of the class:
the PR #340 section-32 receipt disclosure (INDEX, recorded
2026-11-09) — Uni's pre-merge freshness check WAS performed and
left **no independently retrievable timestamped receipt**, so the
gate could not be reconstructed after the fact. Under the contract
below, that merge's bundle is REFUSED (`MAIL_UNCHECKED`): a check
that leaves no evidence is, for reconciliation purposes, a check
that did not happen.

## 2. The reconciled gate — one verdict over one frozen candidate

The candidate is frozen first: PR number, head SHA, tree SHA. Any
new commit is a new candidate and the gate re-runs in full. The
reconciler consumes ONE evidence bundle and returns ONE verdict.
Legs:

| Leg | Question it answers | Terminal source |
|---|---|---|
| exact-head | Did every required check reach a terminal state AT this head, and what is each red check's classification? | completed CI runs / check records at the exact head |
| merge-tree | Does the frozen head merge into current main cleanly? | merge-tree computation + PR mergeable state |
| mail freshness | Has every authority ruling newer than the processed watermark been read, and is the newest disposition for THIS PR a confirmation-class act? | reviewer mail channel + GitHub rulings, watermark recorded in the bundle |
| post-merge | Did the merge land as the recorded commit, and are post-merge checks green? | repository authority (`gh pr view`, main HEAD) |
| fresh-clone | Does the merged revision verify in a clean clone (suites + register render)? | a fresh clone's own run record at the merged revision |

Doctrine, inherited from `certification_runner.py`'s own header:
the reconciler is an **execution instrument, not a certificate**.
A RECONCILED verdict says the evidence reconciles; certification
remains the authorities' act.

## 3. Bundle schema (v1)

```json
{
  "phase": "pre" | "post",
  "pr": 0,
  "head": "<sha>", "tree": "<sha>",
  "frozen_head": "<sha>", "frozen_tree": "<sha>",
  "checks": [{"name": "...", "status": "completed|...",
              "conclusion": "success|failure|...",
              "run_id": 0,
              "sources": {"ci": "...", "pr_view": "..."}}],
  "merge_tree": {"clean": true, "conflicts": []},
  "mail_freshness": {"watermark_checked": "<mail id>",
                     "newest_ruling_id": "<comment/mail id>",
                     "newest_ruling_disposition": "CONFIRM|..."},
  "red_classifications": {"<check name>":
                          "pre-existing|candidate-caused|unexplained"},
  "allow_preexisting": false,
  "post_merge": {"merged": true, "merge_commit": "<sha>",
                 "expected_merge_commit": "<sha>",
                 "main_head_after": "<sha>",
                 "post_checks": ["... same shape as checks ..."]},
  "fresh_clone": {"ran": true, "revision": "<sha>",
                  "result": "success|failure"}
}
```

`post_merge` and `fresh_clone` are required in phase `post` and
ignored in phase `pre`. Every other field is required in both.

## 4. Refusal codes (fail-closed; a verdict is REFUSED if any apply)

| Code | Meaning |
|---|---|
| `BUNDLE_INCOMPLETE` | a required field is absent or the phase is unknown |
| `HEAD_DRIFT` / `TREE_DRIFT` | bundle head/tree differ from the frozen candidate |
| `CHECK_NOT_TERMINAL` | a check is running, pending, or partly reported |
| `CHECK_FAILED_UNCLASSIFIED` | a red check has no recorded classification |
| `CHECK_FAILED_CANDIDATE` | a red check is classified candidate-caused |
| `CHECK_FAILED_PREEXISTING_UNAUTHORIZED` | pre-existing red without the governing authorization flag |
| `SOURCE_DISAGREEMENT` | two sources disagree on a check's conclusion |
| `MERGE_TREE_CONFLICT` | merge-tree is not clean |
| `MAIL_UNCHECKED` | no mail-freshness leg in the bundle |
| `MAIL_HOLD` | newest ruling for this PR is HOLD / CORRECTION_REQUIRED / INSUFFICIENT_EVIDENCE |
| `POST_MERGE_MISMATCH` | merge commit, main head, or a post-merge check disagrees with the record |
| `FRESH_CLONE_MISSING` | fresh-clone leg did not run |
| `FRESH_CLONE_FAILED` | fresh-clone verification failed |
| `FRESH_CLONE_REVISION` | fresh-clone proof is at a revision other than the merge commit |

Malformed input (including `None`) returns REFUSED with
`BUNDLE_INCOMPLETE`; the reconciler never raises.

## 5. Worked example — PR #500 reconstructed (not a reconciler run)

PR #500 (Lane C settlement, records-only) merged 2026-11-20 under
Director predelegation 7040655646. Its terminal record, expressed
as a post-phase bundle: frozen head
`c6d08396eaf95e0fbb11bc10463799ac8ecd24b5`; checks terminal SUCCESS
at that head (Python package run 44743326348; Form smoke run
44743326259); Keeper scoped RECORDS CONFIRM as review 5993988265
at the exact head; freshness — no PR comments after the confirm
(14:10:38Z) at merge time; merge commit
`af2519b6d239ef278397e277210d6da2467c36e5` (14:13:47Z); merged-main
CI SUCCESS (Form smoke run 44751438260, Python package run
44751438156); fresh-clone register verification —
`master_list.py --check` byte-identical, board 40/182. On this
evidence the reconciler's contract returns RECONCILED. This is a
human reconstruction from terminal records, labeled as such; the
first machine-issued verdict comes at code stage.

## 6. Per-merge record format (from code-stage adoption on)

Each merge files, inside its closing package: the frozen candidate
(PR, head, tree), the bundle (or a durable link to it), the
verdict with any refusal codes and their resolutions, the
classification of every red check, the watermark checked and the
newest ruling considered, the merge commit, and the post-merge +
fresh-clone results. A merge with no filed reconciliation record
is, by this contract, an unreconciled merge — visible as such on
the scoreboard.
