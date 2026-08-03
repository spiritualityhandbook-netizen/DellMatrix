# NBD Log

## 2026-08-02 — Lupe5 correction · continuous Δ_known fuel

| Item | Result |
|------|--------|
| Mode | Lupe5 |
| Lattice | Code Evolution |
| Problem fixed | “Exhausted” wording removed — Δ_known is permanent fuel |
| Operator | GrowthResidue added (combines existing shells into new soft operators) |
| Boolean | Substrate intact |
| PROJECTED_NOT_FACT | Unknown remains open; known never closes |
| Floor / Nursery | Untouched |
| Push | This commit |

```bash
python -m form.dell_matrix.decision_shells
```

Prior: ResourceShell · ConstructiveShell · ProbabilisticShell · VariableShell · DEV stable
