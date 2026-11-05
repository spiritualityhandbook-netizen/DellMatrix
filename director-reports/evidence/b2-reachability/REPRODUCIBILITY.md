# B-2 Reachability — Reproducibility Bundle (G-02)

Supplied per Director hourly review 2026-11-04 23:34 CST
(INSUFFICIENT_EVIDENCE on PR #292 at head 99b925b): the actual
probe script, the complete JSON output with SHA-256, the input
63-ID list, deterministic rerun instructions, and an independent
replay at the exact base head.

Base of the original probe: main
843a44c5d63f8b0c6359c4f57764a3851eb16d68 (TD-2 merge, PR #291).
Replay head (this bundle's branch base): the same 843a44c —
PR #292 is docs-only over that base, so the code under probe is
identical at the replay head and at the original probe base.

## Files

- `b2_deep_probe.py` — the probe (see its docstring for tiers).
  SHA-256: e9e5bf23e9ede96a33e9a60af7632c3127d44ddfec22e77247f32f26a14299b1
- `b2_deep_probe.json` — complete output of the replay below
  (63 target rows with every phrase's misroute accounting, plus
  the 4 positive-control rows).
  SHA-256: 78da09e64a25547289f7d1804da8f53ada5afde49907b65687075f4cb5cca8dc
- `MANIFEST.sha256` — digests for both files (`sha256sum -c`).

Original working-paper artifacts (Cycle 6, goal hidden_files):
script SHA-256 8296b5ceefbc2bce024854eb182c165f4a975130f49463d1f99f75531547b982,
JSON SHA-256 7cd37a3e5f8bd545a0dfbcdca10cde52fe1efb70ef938076e3482356621474fb.
The replay's 63 target rows are byte-equivalent in content to
the original JSON's rows (verified programmatically: targets,
route_found_deep, still_no_route and all 63 rows identical);
the JSON differs only by the added `positive_controls` section.

## Input: the 63 Dell IDs

0, 1, 2, 3, 16, 17, 18, 20, 22, 26, 30, 33, 36, 39, 41, 43, 44,
45, 49, 52, 53, 54, 55, 57, 59, 60, 61, 62, 63, 64, 65, 66, 67,
68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83,
85, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99

These are the SM-14 census NO_ROUTE_FOUND rows, embedded in the
script as TARGETS_63 (no external census file is needed).

## Rerun instructions (deterministic)

From a checkout of this PR's head:

```sh
python3 director-reports/evidence/b2-reachability/b2_deep_probe.py
sha256sum -c director-reports/evidence/b2-reachability/MANIFEST.sha256
```

The script resolves the repo root relative to its own location
(override with B2_REPO=/path/to/checkout), inserts it on
sys.path, runs the real translate() over the embedded tiers,
and rewrites b2_deep_probe.json beside itself. Expected stdout:

```text
targets 63; route_found_deep []
still_no_route: [0, 1, 2, 3, 16, 17, 18, 20, 22, 26, 30, 33, 36, 39, 41, 43, 44, 45, 49, 52, 53, 54, 55, 57, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 85, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
controls: [(8, 'create testitem'), (12, 'test testitem'), (51, 'select testitem'), (28, 'restore testitem')]
total phrases (targets): 1694
total errors (targets): 0
```

Disclosed differences from the Cycle-6 original script: repo
root resolved relative to the file (was a hardcoded worktree
path); the 63-ID list embedded (was read from an external
SM-14 census JSON); positive controls recorded in the output
(were a separate unrecorded run). Tier construction, frames,
routing rule and per-Dell logic are unchanged.

## Expected vs observed (replay, SUSX100,000 Cycle 8, 2026-11-05)

| Check | Expected (Cycle 6 claim) | Observed (replay) |
|---|---|---|
| Targets probed | 63 | 63 |
| Tested phrases (targets) | 1,694 | 1,694 |
| translate() errors | 0 | 0 |
| Routes found deep | 0 of 63 | 0 of 63 |
| Control 8 Create | route via "create testitem" | "create testitem" |
| Control 12 Test | route via "test testitem" | "test testitem" |
| Control 51 Select | route via "select testitem" | "select testitem" |
| Control 28 Rollback | route via manor verb "restore testitem" | "restore testitem" |

Bounded claim unchanged: this is per-Dell evidence relative to
the SM-14 + B-2 tiers, not a proof that no conceivable English
sentence routes to these Dells. No English-route implementation
is authorized by this bundle.
