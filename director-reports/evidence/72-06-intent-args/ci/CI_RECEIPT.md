# CI RECEIPT — PR #308 at the frozen original head 3f2c556

- Head: 3f2c556e0afe8949618583f7e724036ab78b8e1e
- build (3.10) PASS 38s, build (3.11) PASS 24s — run 42144404978
  (the CI package the Director's review verified).
- Form smoke PASS 14m14s — run 42144404966 (the run the
  Director's 19:38 review saw IN_PROGRESS; terminal result:
  SUCCESS). This discharges the review's "confirm terminal
  smoke" item for the frozen head.
- The supplement head re-runs all standard checks plus the new
  verify-72-06 job (exact-head assertion + manifest + 21/21 +
  bare-REPL 4/4); that run is the live exact-head proof for the
  final head. ci/ files are receipts, not part of MANIFEST.sha256.
