# 04 — Thin Runtime Stub

Status: TRUE · Code Phase 2 Artifact 4

## Purpose

Offline evaluator that looks up DELL and FLOW nodes against the True registry
and returns structured results. No side effects. Pure lookup + structure.

## Core API

- `get_dell(num)` → registry entry or None
- `get_flow(symbol)` → flow entry or None
- `evaluate_node(node)` → result dict
- `evaluate_ast(ast)` → list of result dicts
- `evaluate_text(text)` → full pipeline (tokenize → parse → evaluate)

## Decisions

| Axis | Choice | Reason |
|------|--------|--------|
| Language | Python 3 | Continuity + offline |
| Side effects | None | Keeps dual-output and offline purity |
| Registry source | 01_REGISTRY_DATA.json | Single source of truth already written |
| Scope | Lookup only | Full execution engine belongs later |

## Next cells still open in Code Phase 2

- Grid / coordinate layer
- Avatar FSM stub
- Static expression field
