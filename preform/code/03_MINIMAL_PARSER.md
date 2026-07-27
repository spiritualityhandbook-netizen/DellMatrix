# 03 — Minimal Parser + AST Stub

Status: TRUE · Code Phase 2 Artifact 3

## Purpose

Consume the token stream produced by `02_TINY_LEXER` and produce a simple, offline AST.

## Decisions

| Axis | Choice | Reason |
|------|--------|--------|
| Language | Python 3 (stdlib) | Continuity with Tiny Lexer, offline purity |
| Form | Pure functions `parse(tokens)` + `parse_text(text)` | Minimal surface |
| AST shape | Flat list of typed nodes (with optional flow attachment) | Enough for Phase 2; nested SEQ can be added later |
| Scope | Structure only | No runtime, no eval, no side effects |
| Dual boundary | TEXT nodes remain English / display side | Language Law preserved |

## Node kinds

- `DELL` — numbered operator (0–50), may carry an attached flow
- `FLOW` — standalone flow symbol
- `LEIGHT` / `LOURE` — create / change path markers
- `TEXT` — collapsed English / display content

## Next cells in Code Phase 2

- Runtime stub (very thin evaluator)
- Grid / coordinate layer
- Avatar FSM stub
- Static expression field

All remain offline-first.
