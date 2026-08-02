# Polyglot + LatinMandell

## Hierarchy

| Layer | Languages / module | Role |
|-------|-------------------|------|
| **Primary door** | English | Full phrase dictionary + docs + REPL |
| **Core Mandell root** | **Latin (LA)** + `latinmandell.py` | Morphology · deeper meaning · custom functions |
| **Foundation doors** | Spanish (ES), French (FR) | Complete Origin command maps |

```
LA / ES / FR phrase  →  English intent  →  Mandell seed  →  executor
English / any surface word  →  LatinMandell root  →  sense + Dell hint
```

## LatinMandell law

LatinMandell is **core**, not flavor.

It does three jobs:

1. **Deeper meaning** — morphology and Latin roots open English (and other tongues)
2. **Function clarity** — roots point at Dells (operators)
3. **Customization** — bind new words/functions through LatinMandell labels

### Deeper meaning

```python
from form.mandell.latinmandell import explain, root_of, deepen

explain("create grow manifest")
root_of("transform")
# → la: transformare · sense: change form across a boundary · dell: 4
```

### Customize function

```python
from form.mandell.latinmandell import customize, root_of

customize("lumen", dell=9, term="Show", sense="light made visible", la="lumen")
root_of("lumen")
# → custom binding → Dell 09[Show]
```

### Speak Latin at the door

```
la crea ideam nomine negotium
la cresce 2
la sphaera
la serva
```

## Foundation complete

| Code | Status |
|------|--------|
| `en` | Primary full |
| `la` | **Core Mandell** + morphology layer |
| `es` / `fr` | Foundation doors complete |

Gate: polyglot_tests ≥ 0.90 per foundation language.  
LatinMandell: `python -m form.mandell.latinmandell` smoke.

## Horizon

More modern languages on request. Worldwide bridge = horizon.  
LatinMandell depth + EN/LA/ES/FR doors = **core complete**.
