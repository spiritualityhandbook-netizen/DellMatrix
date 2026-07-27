# 08 — Face-State Cycles

Status: TRUE · Code Phase 3 Artifact 8

## Structural growth (not a drop)

This artifact explicitly extends:
- `07_EXPRESSION_FIELD` (Tone + Show mapping)
- `06_AVATAR_FSM` (body-first Avatar)

and is registered on the new living page:
- `pages/10_CODE_PHASE3_LIVING.md`

## What it adds

- `FaceCycle` — named sequence or pulse of Expressions
- `FaceStateController` — attaches to Avatar, advances frames via `tick()`
- Default cycles: idle, focus_pulse, joy_seq, resolute

Still offline and static-frame. Timed ASCII animation player comes next.

## Law

Body remains first. Expression is a readable face-state layer that mind and later animation can observe.
