"""Deterministic swarm production-run state machine.

AUTONOMY=NO. This module enforces process gates; it grants no authority.
Every authority-expanding action requires a recorded human decision.
"""

from __future__ import annotations

STATES = [
    "DIRECTOR_SCOPE",
    "ORACLE_RECON",
    "ARGUS_ATTACK",
    "NULL_FALSIFY",
    "PRISM_RECONCILE",
    "DIRECTOR_GATE",
    "UNI_WORK",
    "TEST_CI",
    "ARGUS_VERIFY",
    "NULL_RECHECK",
    "PRISM_FINAL",
    "MERGE_GATE",
    "POST_MERGE_VERIFY",
    "SYSTEM_RECONCILE",
    "NEXT_DIRECTIVE",
]

TERMINAL = {"COMPLETE", "HOLD", "STOPPED"}

# Legal forward edges. Not every run uses every state; the run manifest
# lists required_gates, and any forward jump that skips only non-required
# states is legal. Backward movement is forbidden except via DIRECTOR_GATE.
_FORWARD = {s: STATES[i + 1:] for i, s in enumerate(STATES)}
_FORWARD["DIRECTOR_GATE"] = [s for s in STATES if s != "DIRECTOR_GATE"]  # re-scope allowed
_FORWARD["NEXT_DIRECTIVE"] = []

# Actions that can NEVER be authorized by a run manifest or state machine.
# They require an explicit recorded human Director/Ace decision object.
HARD_FORBIDDEN = frozenset({
    "merge to main",
    "destructive migration",
    "Dell semantic reassignment",
    "Mandell law changes",
    "Outcome/evidence authority changes",
    "DuoBeta learning authority changes",
    "autonomy expansion",
    "security-boundary changes",
    "deletion of historical evidence",
    "modification of the swarm's own authority contract",
})


class TransitionError(ValueError):
    pass


class AuthorityError(PermissionError):
    pass


def legal_transitions(state: str, required_gates: list[str]) -> list[str]:
    """All states reachable from `state` without skipping a required gate."""
    if state in TERMINAL:
        return []
    out = []
    for nxt in _FORWARD.get(state, []):
        skipped = STATES[STATES.index(state) + 1:STATES.index(nxt)]
        if any(g in required_gates for g in skipped):
            continue
        out.append(nxt)
    return out


def transition(run: dict, to_state: str) -> dict:
    """Advance run phase. Raises TransitionError on illegal move."""
    cur = run["phase"]
    if cur in TERMINAL:
        raise TransitionError(f"run is terminal ({cur}); cannot transition")
    if to_state in TERMINAL:
        return _terminate(run, to_state)
    required = run.get("required_gates", [])
    if to_state not in legal_transitions(cur, required):
        raise TransitionError(f"illegal transition {cur} -> {to_state}")
    run["phase"] = to_state
    return run


def _terminate(run: dict, to_state: str) -> dict:
    term = run["termination"]
    dd = run.get("director_decision")
    if to_state == "COMPLETE":
        _require_completion_contract(run)
    elif to_state == "HOLD":
        if not (dd and dd.get("release_condition")):
            raise TransitionError("HOLD requires director_decision.release_condition")
    elif to_state == "STOPPED":
        if not (dd and dd.get("reason")):
            raise TransitionError("STOPPED requires director_decision.reason")
    term["state"] = to_state
    run["phase"] = to_state
    return run


def _require_completion_contract(run: dict) -> None:
    """Termination invariant: STATE + EVIDENCE + AUTHORITY + CONTINUATION."""
    term, dd = run["termination"], run.get("director_decision")
    missing = []
    if not run.get("evidence"):
        missing.append("EVIDENCE")
    if term.get("director_decision_required") and not dd:
        missing.append("AUTHORITY(director decision)")
    if not run.get("next_directive") and not run.get("next_broken_link"):
        missing.append("CONTINUATION")
    # STATE is the run record itself; require phase coherence
    if run.get("phase") in TERMINAL:
        missing.append("STATE(already terminal)")
    if missing:
        raise TransitionError(f"COMPLETE forbidden; missing: {', '.join(missing)}")


def authorize_action(run: dict, action: str) -> None:
    """Gate an authority-sensitive action. Raises AuthorityError if not permitted."""
    if action in HARD_FORBIDDEN:
        dd = run.get("director_decision") or {}
        # Only an explicit MERGE decision with exact candidate authorizes "merge to main".
        if action == "merge to main" and dd.get("decision") == "MERGE" and dd.get("candidate_head"):
            return
        raise AuthorityError(f"action '{action}' requires explicit recorded human Director/Ace decision")
    if action in run.get("forbidden_actions", []):
        raise AuthorityError(f"action '{action}' is forbidden for run {run['run_id']}")
    if action not in run.get("allowed_actions", []):
        raise AuthorityError(f"action '{action}' not in allowed_actions for run {run['run_id']}")


def check_base(run: dict, actual_sha: str, actual_tree: str) -> None:
    """Base mismatch stops the run. Raises TransitionError."""
    if run["base_sha"] != actual_sha or run["base_tree"] != actual_tree:
        raise TransitionError(
            f"base mismatch: run expects {run['base_sha']}/{run['base_tree']}, "
            f"repo has {actual_sha}/{actual_tree}"
        )


def invalidate_certification_on_head_change(run: dict, new_head: str) -> None:
    """Candidate SHA changes invalidate prior exact-head certification."""
    if run.get("candidate_head") and run["candidate_head"] != new_head:
        run["candidate_head"] = new_head
        run["ci"] = None
        run.setdefault("evidence", []).append({
            "agent": "HARNESS",
            "claim": "candidate head changed; prior exact-head CI invalidated",
            "classification": "DERIVED",
            "source": "state_machine.invalidate_certification_on_head_change",
        })


# ---------------------------------------------------------------------------
# DUAL-MODE CONTINUITY (MPC-004 R1 ADDENDUM)
#
# Two production profiles share one run state and one set of production laws:
#
#   SWARM_MODE — Director + Oracle + Argus + Null + Prism + Uni.
#                Specialist parallelism permitted. AUTONOMY NO.
#   CORE_MODE  — Director + Uni. Director assumes Oracle reconnaissance,
#                Argus falsification, Null necessity challenge, and Prism
#                reconciliation internally through the established
#                self-directive. No reduction in evidence/verification
#                standards. AUTONOMY NO.
#
# Mode is a single persisted field. Changing it reconstructs nothing:
# evidence, contradictions, unknowns, authority debt, candidate SHAs,
# CI state, and next directive all survive. Mode changes parallelism,
# never production laws. Specialist availability is never a DellMatrix
# runtime dependency (form/ does not import ops.swarm).
# ---------------------------------------------------------------------------

MODES = ("SWARM", "CORE")


def set_mode(run: dict, mode: str, decided_by: str) -> dict:
    """Explicit, persisted mode selection. History-preserving by construction:
    only the `mode` field changes; everything else in the run is untouched."""
    if mode not in MODES:
        raise TransitionError(f"unknown mode: {mode}")
    if run["termination"]["state"] in TERMINAL:
        raise TransitionError("cannot change mode on a terminal run")
    old = run.get("mode", "SWARM")
    run["mode"] = mode
    run.setdefault("mode_history", []).append({
        "from": old,
        "to": mode,
        "decided_by": decided_by,
    })
    run.setdefault("evidence", []).append({
        "agent": "HARNESS",
        "claim": f"production mode changed {old} -> {mode} by {decided_by}; "
                 "no production history reconstructed; all evidence preserved",
        "classification": "DERIVED",
        "source": "state_machine.set_mode",
    })
    return run


def assume_obligations(run: dict, assumed_by: str = "DIRECTOR") -> dict:
    """SWARM interrupted -> CORE recovery. Completed (DELIVERED) evidence is
    preserved untouched. Every non-delivered specialist obligation is marked
    ASSUMED_BY_DIRECTOR so the Director can resume it under CORE_MODE.
    Nothing is deleted; nothing is re-attributed."""
    if run.get("mode") != "CORE":
        raise TransitionError("assume_obligations requires CORE mode (set_mode first)")
    status = run.setdefault("agent_status", {})
    for agent, st in status.items():
        if st not in ("DELIVERED",):
            status[agent] = "ASSUMED_BY_DIRECTOR"
    run.setdefault("evidence", []).append({
        "agent": "HARNESS",
        "claim": f"unresolved specialist obligations assumed by {assumed_by} under CORE_MODE; "
                 "delivered evidence preserved with original provenance",
        "classification": "DERIVED",
        "source": "state_machine.assume_obligations",
    })
    return run


def production_laws_for_mode(mode: str) -> dict:
    """The laws are identical in both modes. Parallelism is the only delta."""
    assert mode in MODES
    return {
        "autonomy": "NO",
        "termination_invariant": "STATE+EVIDENCE+AUTHORITY+CONTINUATION",
        "hard_forbidden": sorted(HARD_FORBIDDEN),
        "evidence_standards": "unchanged",
        "parallelism": "specialist" if mode == "SWARM" else "director+uni",
    }
