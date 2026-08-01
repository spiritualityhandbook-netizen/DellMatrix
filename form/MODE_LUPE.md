# Lupe Mode

Standing operating law from 2026-08-01.

## Syntax

- `Lupe x N` or `Lupe N` or `Loop a N` or `Nbd5` / `Nbdx10`
- Bare `NBD` = compute optimal X, then execute that many

## Optimal X (locked law)

When user says **NBD** (no number):

1. Compute

\[
E(X) = \frac{X \cdot M}{C \cdot (1 + k(X - A)_+^2)}
\]

| Symbol | Meaning |
|--------|---------|
| A | Attention window ≈ 7 |
| M | Relatedness of next cluster (0–1) |
| C | Cost per item (~3–6 tool cycles) |
| k | Regression weight (~0.15) |

2. Choose X at peak E

| Mode | X |
|------|---|
| Steady (default) | **5** |
| Linked subsystem | **8** |
| Hard max same surface | **10** |
| Never default | **>10** |

3. Execute that many next-best directives

## Default

Minimum **5** on every future directive unless higher N named or bare NBD selects otherwise.

## Law

Every directive under Lupe must:
1. Touch real code or docs in the repo
2. Push
3. Keep Floor + Dual Lattice + Mandell Origin intact
4. Prefer RingedGrowth for any growth step
5. Leave an NBD_LOG stamp

Lupe is removable only by explicit user command.
