# Mandell Core II

Status: FORMALIZED in Form registry + parser + resolver + Core II runtime.
Not a claim of full-operator maturity. Full operator = 15-layer audit + tests.

## Namespaces

| Range | Name | Status |
|---|---|---|
| 00–50 | CORE_I | Active Form spine (locked names) |
| 51–99 | CORE_II | Instruction architecture (this change) |
| 100–999 | ADDRESS | Reserved until DVS promotion |

Former `gate_discipline.EXTENDED_DELL_RESERVE` names (Harmonic, Chess, Nature, Omega, …)
are preserved in `form/mandell/address_space.py` and are **not** production-active.

## Core II primitives

51 Select · 52 Filter · 53 Scope · 54 Query · 55 Set · 56 Get
57 Compare · 58 Match · 59 Route · 60 Branch · 61 Join
62 Parallel · 63 Sequence · 64 Until · 65 While · 66 ForEach
67 Any · 68 All · 69 None · 70 Count · 71 Measure
72 Limit · 73 Threshold · 74 Weight · 75 Normalize
76 Resolve · 77 Infer · 78 Cause · 79 Depend · 80 Context
81 Reference · 82 Group · 83 Ungroup · 84 Copy · 85 Move
86 Delete · 87 Replace · 88 Patch · 89 Diff · 90 Trace
91 Assert · 92 Guard · 93 Try · 94 Catch · 95 Commit
96 Revert · 97 Define · 98 Alias · 99 Compose

## Laws

- Number = semantic family. Bracket term = manifest modifier.
- Unknown / low-confidence modifier falls back to canonical name.
- Low DVS concept becomes Manifest or Macro, not a new number.
- Do not declare 100–999 active unless registry + parser + executor + state + persistence + UI + tests exist.
- Branch presence is not completion.

## Example compression

Long:

`35[Discover] > 18[Mirror] > 39[Schema] > 12[Test]`

Core II first-class:

`90[Trace]`

Conditional nursery:

`53[Scope] > 52[Filter] > 66[ForEach] > 12[Test] > 60[Branch] > 50[Manifest]`

Reusable:

`97[Define] :: Complete=35>18>39>12`
`99[Compose] :: Complete`
