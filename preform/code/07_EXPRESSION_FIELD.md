# 07 — Static Expression Field

Status: TRUE · Code Phase 2 Artifact 7 (final cell)

## Purpose

Static face-state / tone / kaomoji field that attaches to the Avatar.
Maps into Dell 05 (Tone) and Dell 09 (Show) as specified in Phase 3 intake.

## Core

- `Expression` enum — neutral, focus, joy, calm, intense, curious, resolute, soft
- `EXPRESSION_MAP` — kaomoji + tone + show tags
- `ExpressionField` — set / get / as_show / as_tone

## Decisions

| Axis | Choice | Reason |
|------|--------|--------|
| Scope | Static only | Animation cycles belong to Code Phase 3 |
| Mapping | Tone (05) + Show (09) | Direct from Phase 3 intake |
| Extensibility | custom dict | Allows later packs without breaking core |

## Code Phase 2 status

All cells complete:
- Parser + AST stub
- Thin runtime stub
- Grid / coordinate layer
- Avatar FSM stub
- Static expression field
