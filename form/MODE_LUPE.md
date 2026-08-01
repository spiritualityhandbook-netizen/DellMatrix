# Lupe Mode

Standing operating law from 2026-08-01.

## Syntax

- `Lupe x N` or `Lupe N` or `Loop a N` or `loop a x N`
- N = minimum number of full passes / implementations required on the current directive block.

## Default

Minimum **5** on every future directive unless a higher N is named.

Examples:
- `Lupe 5` → at least 5 passes
- `NBD x 10` → execute next 10 best directives in one block
- `Lupe x 1` → single pass allowed

## Law

Every directive under Lupe must:
1. Touch real code or docs in the repo
2. Push
3. Keep Floor + Dual Lattice + Mandell Origin intact
4. Prefer RingedGrowth for any growth step
5. Leave an NBD_LOG stamp

Lupe is removable only by explicit user command.
