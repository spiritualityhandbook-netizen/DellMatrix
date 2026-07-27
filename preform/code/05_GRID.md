# 05 — Grid / Coordinate Layer

Status: TRUE · Code Phase 2 Artifact 5

## Purpose

Minimal offline (x, y) plane.  
Provides the spatial foundation that Avatar FSM and expression fields will later occupy.

## Core

- `Grid` — sparse, origin-centered
- `Cell` — holds optional content + meta
- Movement, neighbors (4 or 8), bounds, occupied list
- Helpers: `place_dell`, `place_text`

## Decisions

| Axis | Choice | Reason |
|------|--------|--------|
| Storage | Sparse dict | Only materialize written cells |
| Origin | (0, 0) default | Matches Body · Heart · Mind plane from Phase 3 intake |
| Rendering | None | Pure data; visual comes later |
| Direction | 4-default, 8-optional | Matches 8-directional facing planned for Avatar |

## Next cells still open in Code Phase 2

- Avatar FSM stub
- Static expression field
