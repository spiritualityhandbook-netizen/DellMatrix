# ops/swarm — DellMatrix Multi-Agent Production Orchestration

**Status:** bootstrap (MPC-004 / SWARM-BOOT-001)
**AUTONOMY: NO.** This is production infrastructure around DellMatrix, not DellMatrix self-modification.

## Problem

Production packets were manually carried between specialists (Director, Oracle, Argus, Null, Prism, Uni). Manual transport is slow, lossy, and error-prone.

## What this is

The smallest shared production-run state + deterministic state machine that lets all specialists operate from one authoritative run record:

- `run_schema.json` — machine-readable RUN state (single source of truth per run)
- `state_machine.py` — deterministic phase transitions + termination invariant
- `run_store.py` — load/save/append evidence with provenance; fresh-process reload
- `roles/*.md` — persistent specialist contracts
- `runs/<run_id>/` — one directory per production run (manifest, evidence, packets)

## What this is NOT

- Not a second DellMatrix evidence engine. Run evidence is production-process evidence (who ran what, what CI said, what was decided), not Mandell semantic truth.
- Not autonomous. Every authority-expanding action (merge, destructive migration, semantic reassignment, autonomy change) requires a recorded human Director/Ace decision. The state machine *refuses* terminal COMPLETE without it.
- Not fake automation. See AGENT_INTERFACE_DISCOVERY in the MPC-004 packet: cross-session invocation is FILE_MEDIATED + HUMAN_TRIGGER_REQUIRED. The harness reduces the trigger to: "run_id + directive", never a full packet retype.

## Invocation reality (verified)

| Specialist | In-session (this runtime) | Cross-session |
|---|---|---|
| ORACLE | DIRECTLY_INVOCABLE via subagent.spawn | FILE_MEDIATED + HUMAN_TRIGGER_REQUIRED |
| ARGUS | DIRECTLY_INVOCABLE via subagent.spawn | FILE_MEDIATED + HUMAN_TRIGGER_REQUIRED |
| NULL | DIRECTLY_INVOCABLE via subagent.spawn | FILE_MEDIATED + HUMAN_TRIGGER_REQUIRED |
| PRISM | DIRECTLY_INVOCABLE via subagent.spawn | FILE_MEDIATED + HUMAN_TRIGGER_REQUIRED |
| UNI | this agent | FILE_MEDIATED + HUMAN_TRIGGER_REQUIRED |

Cross-session protocol: the run directory is the message. Director issues `run_id` + decision; Uni (or any operator with repo access) advances the run; specialists read `runs/<run_id>/manifest.json`, write evidence packets to `runs/<run_id>/evidence/<agent>/`, and the reconciler ingests them.

## Minimal human trigger

To advance a run cross-session, a human pastes/issues exactly:
```
SWARM RUN <run_id> → <directive/decision>
```
The operator loads `runs/<run_id>/manifest.json` and continues from the recorded phase. No packet retyping.

## Termination invariant

A run may NOT become COMPLETE merely because code exists, tests pass, CI passes, or a PR merges. Completion requires STATE + EVIDENCE + AUTHORITY + CONTINUATION. If `director_decision_required` is true, terminal COMPLETE is forbidden until a Director decision is recorded. Enforced in `state_machine.py`, tested in `tests/test_harness.py`.

## Dual-mode continuity (MPC-004 R1 addendum)

Two production profiles, one run state, one set of laws:

- **SWARM_MODE** — Director + Oracle + Argus + Null + Prism + Uni. Specialist parallelism permitted. AUTONOMY NO.
- **CORE_MODE** — Director + Uni. Director assumes the four specialist roles internally via the established self-directive. No reduction in evidence/verification standards. AUTONOMY NO.

Invariants (tested in `tests/test_modes.py`):
1. Mode is explicit and persisted (`mode` + `mode_history` in the manifest).
2. SWARM→CORE and CORE→SWARM change exactly one field — no history reconstruction; evidence, contradictions, UNKNOWNs, candidate SHAs, CI state, and next directive survive.
3. Specialist availability is never a DellMatrix runtime dependency (`form/` does not import `ops.swarm`).
4. Losing specialists changes parallelism, not laws (`production_laws_for_mode` identical).
5. Interrupted SWARM → `set_mode(CORE)` + `assume_obligations()` preserves delivered evidence and marks unresolved obligations ASSUMED_BY_DIRECTOR.
