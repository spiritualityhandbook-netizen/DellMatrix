# Mandel Lang V0 — Origin intake (high‑S only)

Source: Mandel Syntactic Codex.  
Policy: `form/MODE_FORM.md` — implement high‑S only.

## Implemented

| Piece | Module |
|-------|--------|
| 7 Core Rules | `rules_v0.py` |
| Morpheme delimiter protocol | `morpheme.py` |
| Operator → Dell map | `operators_v0.py` |
| Personas V7 (doc) | `personas_v7.md` |

## Not implemented (low‑S)

- Full 40-column visual grid compiler
- Diagonal cross-layer runtime engine
- AIOps / OpenTelemetry agent stack
- Autonomic self-healing deployment agents

## Quick use

```python
from form.mandell.morpheme import explain_morphemes, force_mandell_morphemes
from form.mandell.rules_v0 import status as rules_status
from form.mandell.operators_v0 import lookup, seed_for

force_mandell_morphemes("Commandell")  # Com-man-dell
explain_morphemes("Com-man-dell")
lookup("[->]")
seed_for("[=]", "node")
```

## Constraint density law (Codex Part IV)

Explicit structural rules (Floor, Dells, Nursery, these 7 rules) prune invalid paths  
better than unconstrained token search. That is why Mandell exists.
