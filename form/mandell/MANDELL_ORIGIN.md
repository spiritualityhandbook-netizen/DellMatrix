# Mandell — Origin Priority

**Mandell is the Origin.**  
DellMatrix exists to host and exercise Mandell.

---

## Goal

A practical **bridge language**:

- Human ↔ Computer
- Surface languages ↔ same Dell operator layer
- **LatinMandell** reveals deeper meaning via morphology and roots
- Words and functions can be **customized** through LatinMandell
- Readable by humans · executable by machines

---

## Layers (now)

| Layer | Module | Role |
|-------|--------|------|
| Floor | `floor.py` | Alpha · Delta · Omega · Omni |
| Dells | `registry.py` | Operators 00–50 + Core II 51–99 |
| Seeds | `seed.py` | `08[Create] > 15[Map] :: name` |
| ManifestSet | `seed.py` | `08[Create•Map•Keep]` Chain |
| Chainlink | `seed.py` | `08[A•B] > 12[X•Y]` → (A>X)•(B>Y) |
| Phrases | `phrases.py` | Stable English → seed dictionary |
| Patterns | `patterns.py` | Math/nature teachable forms |
| Bridge | `bridge.py` | EN ↔ Mandell |
| **LatinMandell** | `latinmandell.py` | **Core** morphology · sense · customize |
| Polyglot | `polyglot.py` | LA/ES/FR → English → Mandell |
| Executor | `executor.py` | Dense Dell runtime coverage |

---

## LatinMandell (core)

Latin is not a side translation. It is the **morphological depth layer**:

- Understand deeper meanings of English and other languages
- Map surface words → Latin root → sense → Dell
- Customize new word/function bindings without breaking Floor law

```
explain("create grow save")
customize("lumen", dell=9, sense="light made visible")
la crea ideam nomine negotium
```

See `POLYGLOT.md` and `latinmandell.py`.

---

## Laws

1. Structure inside · surface language outside  
2. Every important action is a Dell  
3. Compose with flow — don’t invent chaos  
4. Math/nature patterns are first-class and teachable  
5. **LatinMandell is core** — morphology and custom function are Origin tools  
6. Both humans and the runtime must be able to read the seed
7. Number = Dell family · Bracket = Manifest domain · `•` = ManifestSet separator
8. Emoji is display alias · Unicode-aware canonical grammar is executable truth
9. Chain and Chainlink are grammar operators (no new Dell number without DVS)
10. FlowSet longest match first: `>>>` `>>` `>` `:>` `<:` `<:>` `::` `:` `<<[Delta]`
11. LatinMandell resolves Morphology > Context > Canonical
12. Existing seeds stay valid

---

## Chain and Chainlink

```
08[Create•Map•Keep]
=> 08[Create] > 08[Map] > 08[Keep]

08[Create•Map] > 12[Test•Keep]
=> (Create>Test)•(Map>Keep)
```

Mandellmoji (display only): Chain ⛓️‍💥 · Chainlink ⛓️

Separator is `•` (U+2022). Not `,`. Not `_`.

---

## Compression cells

- **Mandellacell** — reusable named seed (`define_cell` / `expand_cell`)
- **DeltaDirective** — send only new work against a verified HEAD
- **EvidenceCell** — HEAD · SHA · tests · failures · unresolved

---

## Control 60-66

```
60[true] > TRUE_BODY > 59[Else] > FALSE_BODY > 61[Join]
```

- Missing `59[Else]` is a valid single-arm branch
- Two `59[Else]` markers in one branch fail explicitly
- Nesting is allowed for Branch, Parallel, Sequence, Until, While, ForEach
- Depth cap is 4; loop cap is `72[Limit]` or 8
- Parallel is deterministic same-process collection, not threads
- Control frames / flow traces are runtime-only and are not persisted in v7

---

## Core II 51-99

Runtime locality is closed at 51-99. 100-999 stay reserved.

- Query/reason 51-59 and 67-79 share `predicate.py`
- Control 60-66 consumes the same predicate engine
- Object/audit 80-90 mutate typed state
- Transaction 93-96 uses an explicit frame: id · checkpoint · staged · status · error · depth
- Abstraction 97-99 stores definitions; Compose runs the normal executor
- `last_result`, frames, flow traces, tx, snapshots, staged, and limit are transient
- Store/defs/aliases/compositions/groups/refs/causes/deps/weights are durable

Grammar truth is Unicode-aware. The ManifestSet separator is `•` (U+2022). Emoji is display alias only.
