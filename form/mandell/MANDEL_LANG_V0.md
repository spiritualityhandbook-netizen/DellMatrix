> STATUS: IN USE — describes live code in form/ at commit 11933da. Doc verified against code 2026-10-30.

# Mandel Lang V0 — Origin intake (high‑S only)

Source: Mandel Syntactic Codex.  
Policy: `form/MODE_FORM.md` — implement high‑S only.

## Implemented

| Piece | Module |
|-------|--------|
| 7 Core Rules | `rules_v0.py` — **not present in this tree at commit 11933da** (the rules survive as the design statement in the Constraint density law below) |
| Morpheme delimiter protocol | `morpheme.py` |
| Operator → Dell map | `operators_v0.py` — **not present in this tree at commit 11933da**; the live operator→Dell mapping is the registry, `form/mandell/registry.py` |
| Personas V7 (doc) | `personas_v7.md` |

## Not implemented (low‑S)

- Full 40-column visual grid compiler
- Diagonal cross-layer runtime engine
- AIOps / OpenTelemetry agent stack
- Autonomic self-healing deployment agents

## Quick use

```python
from form.mandell.morpheme import explain_morphemes, force_mandell_morphemes

force_mandell_morphemes("Commandell")  # Com-man-dell
explain_morphemes("Com-man-dell")
```

(The `rules_v0` / `operators_v0` imports from the original v0 intake are gone — those modules are not present in this tree; see the table above.)

## Constraint density law (Codex Part IV)

Explicit structural rules (Floor, Dells, Nursery, these 7 rules) prune invalid paths  
better than unconstrained token search. That is why Mandell exists.
