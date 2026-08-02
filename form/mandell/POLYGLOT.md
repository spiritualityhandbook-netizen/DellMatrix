# Polyglot + LatinMandell

## Hierarchy

| Layer | Languages / module | Role |
|-------|-------------------|------|
| **Primary door** | English | Full phrase dictionary + docs + REPL |
| **Core Mandell root** | **LatinMandell (LA)** | Morphology · deeper meaning · custom functions |
| **Foundation doors** | Spanish (ES), French (FR) | Complete Origin command maps |

```
LA / ES / FR phrase  →  English intent  →  Mandell seed  →  executor
English / any surface word  →  LatinMandell root  →  sense + Dell hint
Hyphen tokens (Com-man-dell) → morpheme senses combined
```

## LatinMandell law

LatinMandell is **core**, not flavor. It is a **new-age variation**:

- Uses **classic Latin** when useful, intuitive, practical
- Otherwise uses **morphology** (`-` separated tokens) to comprehend meaning
- Maps surface → sense → Dell
- `customize` bindings **persist** with save/load v7

### REPL (Strong)

```
explain create
explain Com-man-dell
deepen create grow save
morph Commandell
customize lumen dell 9 sense light made visible
customs
la crea ideam nomine negotium
la cresce 2
la sphaera
la serva
```

### API

```python
from form.mandell.latinmandell import explain, root_of, deepen, customize

explain("create grow manifest")
root_of("transform")
root_of("Com-man-dell")  # hyphen morphology
customize("lumen", dell=9, sense="light made visible")
```

## Foundation complete

| Code | Status |
|------|--------|
| `en` | Primary full |
| `la` | **Core** door + morphology layer — REPL wired |
| `es` / `fr` | Foundation doors complete |

Gate: polyglot_tests ≥ 0.90 per foundation language.  
LatinMandell: `python -m form.mandell.latinmandell` smoke.

## Horizon

More modern languages on request. Worldwide bridge = horizon.
