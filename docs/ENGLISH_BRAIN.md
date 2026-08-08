# English Brain — natural language understanding

**Module:** `form/mandell/english_brain.py`  
**Loop command:** `english expand 50`

## What it does

1. **Strip** politeness / fillers (`please`, `can you`, `i want to`, …)
2. **Paraphrase** everyday wording → stable Mandell phrases
3. **Synonym rewrite** leading verbs (`spawn` → create, `cultivate` → grow)
4. **Match** against phrase dictionary + translate fallbacks
5. **Expand loop** — grow mastery over N cycles (default **50**)

## 50-cycle directive results (baseline run)

```
cycles=50
tests=3050
hits≈3015
final_rate≈98.9%
mastery: place/grow/walk/look/save/show/proposals/sphere/evolve ≈ 0.99
```

## Commands

```text
you> english expand 50     # loop understanding growth 50×
you> english status        # cycles · learned · mastery
you> english help          # natural phrasing examples
you> please create an idea called garden
you> what do i see
you> save my work
you> switch to sphere
you> grow the program
```

## Law

Structural surface only — not AGI, not free chat. Maps English → intents under Floor + Nursery law.
