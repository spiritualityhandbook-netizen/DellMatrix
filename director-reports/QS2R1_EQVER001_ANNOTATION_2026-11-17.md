# Q-S2R.1 — EQ-VER-001 entry-level annotation (records only)

Date: 2026-11-17. Circuit: Q-S2R.1 follow-on from PR #451.
Authority: Director §42 post-merge decisions on PR #451, comment
6946046074 — "append a scoped current-state annotation rather than
rewrite history. No CODE credit."

## Change

One file: `docs/DELLMATRIX_EQUATION_LEDGER.md`, EQ-VER-001 (§2).

- The entry's historical `Classification: DUPLICATE` line stands
  unedited (ledger append-only law, §12; old text/provenance preserved).
- A scoped current-state annotation is appended directly to the entry:
  the current relationship is **delegated-canonical** — the §13 R4-A1
  append records DEDUP = EXECUTED; `verita.vesica_strength` is a
  delegating adapter; `sacred_geometry.vesica` (EQ-GEO-001) is the one
  live authority.

## Evidence (re-verified this circuit at main dc328b8d)

- `form/dell_matrix/verita.py:45` — `from form.dell_matrix import sacred_geometry`.
- `form/dell_matrix/verita.py:56` — `vesica_strength` defined as a thin
  compatibility wrapper; docstring names `sacred_geometry.vesica`
  (EQ-GEO-001) "live authority"; delegation call at :96.
- Ledger §13 R4-A1 append (already on main) records the same
  classification with its 2026-11-15 first-hand evidence.

## Scope / credits

Records only. No code changed. No PLAN/CODE credit claimed.
Q-S2R.2 (VERITA-JUDGE classification schema proposal), Q-S2R.3
(R4-A7 source-comment CODE circuit) and Q-S2R.4 (seven-bearer naming
audit plan) remain separate Uni-owned follow-ons, untouched here.
