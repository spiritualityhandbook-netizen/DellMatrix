# Context Horizon — memory plane (Origin)

Date: 2026-08-01  
Authority: high-S only · offline acceptance · English primary door

---

## Purpose

Name the three-tier memory model that already matches live `persist.py` (v7).

Context Horizon is the **matrix memory plane**: what is hot, what is warm, what is cold.

It is documentation + operational guidance. It does **not** introduce SilentInject, browser WebSockets, or Gemini-specific orchestration.

---

## Three tiers

| Tier | Role | Live mapping |
|------|------|--------------|
| **Hot** | Active session state | In-memory `Program` (plane, lattice, avatar, nursery, history) |
| **Warm** | Recent durable session | Last `save` file under `form/state/program_*.json` |
| **Cold** | Archive / recovery | Checkpoints `program_*_cp_*.json` + any explicit archive |

### Binding rules (Origin-safe)

- Hot ⇕ Warm — normal `save` / `load` cycle (user-visible)
- Hot → Cold — `checkpoint` (or scheduled save) writes a stamped snapshot
- Cold → Hot — explicit `load` from a checkpoint path (user-visible recovery)

No invisible mid-conversation rewrite of context. Recovery is always operator-triggered.

---

## Essence summary (optional compression note)

When a session is large, a future optional **essence** extract may summarize:

- owner, floor, lattice size/form, pending nursery count, last N history lines, key unit labels

Essence is a **read-only recovery aid**, not a hidden inject.  
Max practical size target: small enough to paste or load cleanly offline.

---

## Fog pattern (token / coherence budget)

**Fog** = session nearing practical limits (history long, lattice dense, REPL noisy).

Guidance only:

| Signal | Action |
|--------|--------|
| Soft warning | Prefer `distill`, `rank`, `confirm`/`reject`, or `save` |
| Hard pressure | `checkpoint` then continue, or `load` a clean checkpoint |
| Recovery | Explicit load from Cold; operator sees the restore |

**Rejected for Origin:** SilentInject, invisible context refresh, browser-as-replica assumptions.

---

## Relation to acceptance path

```
create → grow → confirm → sphere → save → load → visual
```

`save` / `load` / `checkpoint` are the Horizon operators already live in persist v7.

---

## Laws

1. English primary daily door  
2. Offline acceptance must not depend on network or external models  
3. Growth stays in Nursery until confirm  
4. Floor lock + honesty gates unchanged  
5. High-S only — no scope expansion into multi-instance Gemini orchestration

See: `form/persist.py` · `form/CORE_SCOPE.md` · `docs/START_HERE.md`
