# 06 — Avatar FSM Stub

Status: TRUE · Code Phase 2 Artifact 6

## Purpose

Minimal body-first finite-state machine for the Avatar.
Implements the Phase 3 intake contract:

- Lives on (x, y) plane (uses Grid from Artifact 5)
- 8-directional facing
- Locomotion + posture FSM
- Reach tiers
- Pick up / place down
- Dual thread law: Body first. Mind always reads real body state.

## Core types

- `Facing` — N NE E SE S SW W NW
- `Posture` — STAND SIT BEND JUMP
- `Locomotion` — IDLE WALK JOG RUN
- `Reach` — CLOSE AWAY FAR
- `BodyState` — stable snapshot
- `Avatar` — body primitives + read_body()

## Law enforced

Body methods mutate state.  
`read_body()` is the only interface mind is allowed to use later.

## Next (last open cell in Code Phase 2)

Static expression field
