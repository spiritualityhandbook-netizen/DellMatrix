#!/usr/bin/env python3
"""
Intrinsic agent — reward for novelty, not only imitation.

From: NVIDIA / RL research theme "copying humans isn't enough"
  · Pure imitation → shortcuts
  · Intrinsic curiosity: prefer unseen organs, new skins, unexplored centers
  · Anti-shortcut: reject actions that only repeat last trail

Works with companion + free_matrix walk without needing neural nets.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import time


@dataclass
class IntrinsicAgent:
    seen_cells: Set[Tuple[int, int]] = field(default_factory=set)
    seen_labels: Set[str] = field(default_factory=set)
    last_action: str = ""
    curiosity_score: float = 0.0
    history: List[Dict[str, Any]] = field(default_factory=list)

    def observe(self, program, sight: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        novelty = 0.0
        new_labels = []
        nodes = []
        if sight:
            nodes = sight.get("nodes") or []
            if not nodes and isinstance(sight.get("vision"), dict):
                nodes = (sight["vision"] or {}).get("nodes") or []
        for n in nodes:
            lab = str(n.get("label") or n.get("id") or "")
            if lab and lab not in self.seen_labels:
                self.seen_labels.add(lab)
                new_labels.append(lab)
                novelty += 1.0
        # position novelty
        try:
            body = getattr(getattr(program, "avatar", None), "body", None)
            if body is not None:
                pos = getattr(body, "pos", (0, 0))
                cell = (int(pos[0]), int(pos[1]))
                if cell not in self.seen_cells:
                    self.seen_cells.add(cell)
                    novelty += 0.5
        except Exception:
            pass
        self.curiosity_score += novelty
        rec = {
            "novelty": novelty,
            "new_labels": new_labels[:8],
            "curiosity_total": round(self.curiosity_score, 2),
            "cells_explored": len(self.seen_cells),
            "labels_seen": len(self.seen_labels),
            "ts": time.time(),
        }
        self.history.append(rec)
        return rec

    def propose_action(self, program) -> Dict[str, Any]:
        """Prefer exploration actions over pure repeat."""
        candidates = ["forward", "left", "right", "back", "turn_left", "turn_right", "look_up"]
        # anti-shortcut: avoid identical repeat
        ranked = []
        for c in candidates:
            penalty = 1.0 if c == self.last_action else 0.0
            score = 1.0 - penalty
            # bias toward movement when few cells explored
            if len(self.seen_cells) < 8 and c in ("forward", "left", "right"):
                score += 0.5
            ranked.append((score, c))
        ranked.sort(reverse=True)
        best = ranked[0][1]
        return {
            "action": best,
            "scores": ranked[:5],
            "law": "intrinsic curiosity · avoid pure imitation shortcut",
            "source_idea": "nvidia_copying_humans_not_enough",
        }

    def step(self, program) -> Dict[str, Any]:
        prop = self.propose_action(program)
        action = prop["action"]
        result: Dict[str, Any] = {"ok": False}
        try:
            from form.dell_matrix import free_matrix as fm
            if action == "turn_left":
                result = fm.turn(program, "left")
            elif action == "turn_right":
                result = fm.turn(program, "right")
            elif action == "look_up":
                result = fm.look(program, "up")
            elif action in ("forward", "back", "left", "right"):
                result = fm.walk(program, action if action != "back" else "back")
            else:
                result = fm.walk(program, "forward")
        except Exception as e:
            result = {"ok": False, "error": str(e)}
        self.last_action = action
        sight = {}
        try:
            from form.dell_matrix import free_matrix as fm
            sight = fm.see(program, "companion", "first")
        except Exception:
            pass
        obs = self.observe(program, sight)
        return {"action": action, "result": result, "observe": obs, "proposal": prop}

    def to_dict(self) -> Dict[str, Any]:
        """Versioned behavioral snapshot. Observations only.

        Never includes permissions, grant handles, or credentials (the
        agent holds none). Payloads are bounded.
        """
        return {
            "version": AGENT_LOCAL_VERSION,
            "seen_cells": [list(c) for c in list(self.seen_cells)[:_MAX_SEEN_CELLS]],
            "seen_labels": [str(l)[:_MAX_LABEL_LEN] for l in list(self.seen_labels)[:_MAX_SEEN_LABELS]],
            "last_action": str(self.last_action)[:64],
            "curiosity_score": float(self.curiosity_score),
            "history": [dict(r) for r in self.history[-_MAX_HISTORY:]],
        }

    @classmethod
    def from_dict(cls, data: Any, subject: str = "?") -> "IntrinsicAgent":
        """Restore from a versioned snapshot. Fail closed on malformed.

        Directive §4: explicit null (data is None) is malformed, not
        absence. Genuine absence is handled by callers via sentinel
        (for_agent, the loader); they construct IntrinsicAgent() directly
        and never pass an unverified None here. Versions are strict ints:
        bool, float, str, NaN, and coercion are rejected.
        """
        if data is None:
            raise AgentLocalLoadError(
                f"agent-local state for {subject!r}: explicit null is "
                "malformed, not absence")
        if not isinstance(data, dict):
            raise AgentLocalLoadError(
                f"agent-local state for {subject!r}: expected dict, "
                f"got {type(data).__name__}")
        if "version" not in data:
            raise AgentLocalLoadError("agent-local version: absent key")
        version = _strict_int(data["version"], "version", subject)
        if version != AGENT_LOCAL_VERSION:
            raise AgentLocalLoadError(
                f"unsupported agent-local version: {version}")
        clean = _validate_agent_state_dict(data, subject)
        inst = cls()
        inst.seen_cells = set(clean["seen_cells"])
        inst.seen_labels = set(clean["seen_labels"])
        inst.last_action = clean["last_action"]
        inst.curiosity_score = clean["curiosity_score"]
        inst.history = clean["history"]
        return inst


def for_agent(program: Any, subject: str) -> IntrinsicAgent:
    """Return the agent-local IntrinsicAgent for (owner, subject).

    Behavioral state is isolated per subject within the owner's program:
    two agents never share seen cells, labels, action history, or
    curiosity. The instance is cached on the program for the session;
    durable state persists through the canonical program payload
    (agent_local section).

    Directive §4: a sentinel distinguishes genuine absence (subject key
    missing -> fresh default) from explicit null (subject key present
    with null value -> AgentLocalLoadError). from_dict never receives
    an unverified None.

    Movement behavior stays distinct from knowledge acceptance: this
    agent explores (observe/propose_action/step); it never confirms
    proposals or holds grants.
    """
    if not isinstance(subject, str) or not subject:
        raise ValueError("subject must be non-empty str")
    cache = getattr(program, "agent_local_agents", None)
    if cache is None or not isinstance(cache, dict):
        cache = {}
        program.agent_local_agents = cache
    inst = cache.get(subject)
    if inst is None:
        stored = getattr(program, "agent_local_states", None)
        if not isinstance(stored, dict):
            stored = {}
        raw = stored.get(subject, _MISSING)
        if raw is _MISSING:
            # Genuine absence: no stored record for this subject.
            inst = IntrinsicAgent()
        elif raw is None:
            # Explicit null stored record is malformed, not absence.
            raise AgentLocalLoadError(
                f"agent-local state for {subject!r}: explicit null "
                "is malformed, not absence")
        else:
            inst = IntrinsicAgent.from_dict(raw, subject)
        cache[subject] = inst
    return inst


def sync_agent_to_program(program: Any, subject: str) -> None:
    """Write an agent's current behavioral state into the program payload
    staging (agent_local_states) so the next save/checkpoint persists it."""
    cache = getattr(program, "agent_local_agents", None) or {}
    inst = cache.get(subject)
    if inst is None:
        return
    states = getattr(program, "agent_local_states", None)
    if not isinstance(states, dict):
        states = {}
        program.agent_local_states = states
    states[subject] = inst.to_dict()


def sync_all_agents_to_program(program: Any) -> None:
    """Canonical hook: synchronize every live agent's observations into the
    program payload staging before save/checkpoint serialization.

    Called by the normal save path (form.persist.serialize); callers never
    need to invoke sync_agent_to_program manually.

    Directive §4: no broad suppression. All live snapshots are STAGED and
    validated BEFORE any stored state is replaced; a failure raises and
    leaves the previous staged state untouched. Declared retention
    (to_dict truncation) is separate from input validation (from_dict
    rejection) — the staged snapshot must round-trip cleanly.
    """
    cache = getattr(program, "agent_local_agents", None) or {}
    staged: Dict[str, Dict[str, Any]] = {}
    for subject in list(cache.keys()):
        inst = cache.get(subject)
        if inst is None:
            continue
        # May raise: nothing has been mutated yet.
        snap = inst.to_dict()
        # The staged snapshot must round-trip through strict validation.
        IntrinsicAgent.from_dict(snap, subject)
        staged[subject] = snap
    # All staged OK; write into stored state. Subjects with stored state
    # but no live instance this session are preserved untouched.
    states = getattr(program, "agent_local_states", None)
    if not isinstance(states, dict):
        states = {}
        program.agent_local_states = states
    for subject, snap in staged.items():
        states[subject] = snap


# Module-global compatibility instance (pre-R6.4 interface). Prefer
# for_agent(program, subject) for isolated per-agent behavioral state.
AGENT = IntrinsicAgent()


AGENT_LOCAL_VERSION = 1

# Bounds for stored behavioral payloads (directive §4: bound stored payloads).
_MAX_SEEN_CELLS = 1024
_MAX_SEEN_LABELS = 256
_MAX_HISTORY = 32
_MAX_LABEL_LEN = 120
_MAX_HISTORY_VALUE_LEN = 256
_MAX_HISTORY_KEYS = 16

_MISSING = object()


class AgentLocalLoadError(ValueError):
    """Malformed agent-local state. Fail closed; malformed is not absence."""


def _strict_int(value: Any, name: str, subject: str) -> int:
    """Strict integer: rejects bool, float, str, NaN, coercion."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise AgentLocalLoadError(
            f"agent-local {name} for {subject!r}: expected int, "
            f"got {type(value).__name__}")
    return value


def _strict_float(value: Any, name: str, subject: str) -> float:
    """Strict finite float: rejects bool, str, NaN, Inf, coercion."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AgentLocalLoadError(
            f"agent-local {name} for {subject!r}: expected number, "
            f"got {type(value).__name__}")
    f = float(value)
    import math as _math
    if not _math.isfinite(f):
        raise AgentLocalLoadError(
            f"agent-local {name} for {subject!r}: non-finite number")
    return f


def _validate_agent_state_dict(data: Any, subject: str) -> Dict[str, Any]:
    """Validate one agent's stored behavioral state. Raises AgentLocalLoadError.

    AMEND §5: absent keys (via membership) differ from explicit null;
    versions are strict ints (no bool/float/coercion); NaN/Inf rejected;
    the FULL payload is validated (not a sliced prefix); nested history
    content is bounded.
    """
    if not isinstance(data, dict):
        raise AgentLocalLoadError(
            f"agent-local state for {subject!r} is not a dict")

    # seen_cells: full-list validation; over-bound length is malformed
    # (not silently truncated).
    cells = data.get("seen_cells", _MISSING)
    if cells is _MISSING:
        cells = []
    elif cells is None:
        raise AgentLocalLoadError("seen_cells: explicit null is malformed")
    if not isinstance(cells, list):
        raise AgentLocalLoadError("seen_cells is not a list")
    if len(cells) > _MAX_SEEN_CELLS:
        raise AgentLocalLoadError("seen_cells exceeds bound")
    clean_cells = []
    for c in cells:
        if (isinstance(c, (list, tuple)) and len(c) == 2
                and not isinstance(c[0], bool) and isinstance(c[0], (int, float))
                and not isinstance(c[1], bool) and isinstance(c[1], (int, float))):
            import math as _math
            if not _math.isfinite(float(c[0])) or not _math.isfinite(float(c[1])):
                raise AgentLocalLoadError("seen_cells entry non-finite")
            clean_cells.append((int(c[0]), int(c[1])))
        else:
            raise AgentLocalLoadError("seen_cells entry malformed")

    labels = data.get("seen_labels", _MISSING)
    if labels is _MISSING:
        labels = []
    elif labels is None:
        raise AgentLocalLoadError("seen_labels: explicit null is malformed")
    if not isinstance(labels, list):
        raise AgentLocalLoadError("seen_labels is not a list")
    if len(labels) > _MAX_SEEN_LABELS:
        raise AgentLocalLoadError("seen_labels exceeds bound")
    clean_labels = []
    for lab in labels:
        if not isinstance(lab, str):
            raise AgentLocalLoadError("seen_labels entry is not a str")
        if len(lab) > _MAX_LABEL_LEN:
            raise AgentLocalLoadError("seen_labels entry exceeds bound")
        clean_labels.append(lab)

    last_action = data.get("last_action", _MISSING)
    if last_action is _MISSING:
        last_action = ""
    elif last_action is None:
        raise AgentLocalLoadError("last_action: explicit null is malformed")
    if not isinstance(last_action, str):
        raise AgentLocalLoadError("last_action is not a str")
    if len(last_action) > 64:
        raise AgentLocalLoadError("last_action exceeds bound")

    curiosity_raw = data.get("curiosity_score", _MISSING)
    if curiosity_raw is _MISSING:
        curiosity = 0.0
    elif curiosity_raw is None:
        raise AgentLocalLoadError("curiosity_score: explicit null is malformed")
    else:
        curiosity = _strict_float(curiosity_raw, "curiosity_score", subject)

    history = data.get("history", _MISSING)
    if history is _MISSING:
        history = []
    elif history is None:
        raise AgentLocalLoadError("history: explicit null is malformed")
    if not isinstance(history, list):
        raise AgentLocalLoadError("history is not a list")
    if len(history) > _MAX_HISTORY:
        raise AgentLocalLoadError("history exceeds bound")
    clean_history = []
    for rec in history:
        if not isinstance(rec, dict):
            raise AgentLocalLoadError("history entry is not a dict")
        if len(rec) > _MAX_HISTORY_KEYS:
            raise AgentLocalLoadError("history entry exceeds key bound")
        clean_rec = {}
        for k, v in rec.items():
            if not isinstance(k, str):
                raise AgentLocalLoadError("history key is not a str")
            if len(k) > 64:
                raise AgentLocalLoadError("history key exceeds bound")
            ks = k
            if isinstance(v, str):
                if len(v) > _MAX_HISTORY_VALUE_LEN:
                    raise AgentLocalLoadError("history value exceeds bound")
                clean_rec[ks] = v
            elif isinstance(v, bool):
                raise AgentLocalLoadError("history value bool not allowed")
            elif isinstance(v, (int, float)):
                import math as _math
                if not _math.isfinite(float(v)):
                    raise AgentLocalLoadError("history value non-finite")
                clean_rec[ks] = v
            elif v is None:
                clean_rec[ks] = None
            elif isinstance(v, list):
                # Directive §4: no str() normalization of arbitrary
                # objects; no nonfinite values; no malformed containers.
                # Each item must be a valid scalar or None, else reject.
                if len(v) > 16:
                    raise AgentLocalLoadError("history list value too long")
                clean_list = []
                for x in v:
                    if isinstance(x, str):
                        if len(x) > _MAX_HISTORY_VALUE_LEN:
                            raise AgentLocalLoadError(
                                "history list item exceeds bound")
                        clean_list.append(x)
                    elif isinstance(x, bool):
                        raise AgentLocalLoadError(
                            "history list item bool not allowed")
                    elif isinstance(x, (int, float)):
                        import math as _math
                        if not _math.isfinite(float(x)):
                            raise AgentLocalLoadError(
                                "history list item non-finite")
                        clean_list.append(x)
                    elif x is None:
                        clean_list.append(None)
                    else:
                        raise AgentLocalLoadError(
                            "history list item type "
                            f"{type(x).__name__} not allowed")
                clean_rec[ks] = clean_list
            else:
                raise AgentLocalLoadError(
                    f"history value type {type(v).__name__} not allowed")
        clean_history.append(clean_rec)

    return {
        "seen_cells": clean_cells,
        "seen_labels": clean_labels,
        "last_action": last_action,
        "curiosity_score": curiosity,
        "history": clean_history,
    }


def smoke() -> bool:
    print("=== INTRINSIC AGENT SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)
    a = IntrinsicAgent()
    class Body:
        pos = (0, 0)
    class P:
        avatar = type("A", (), {"body": Body()})()
    obs = a.observe(P(), {"nodes": [{"label": "NewThing"}]})
    rec("novelty", obs["novelty"] >= 1.0)
    prop = a.propose_action(P())
    rec("propose", "action" in prop)
    a.last_action = prop["action"]
    prop2 = a.propose_action(P())
    rec("anti_shortcut", prop2["action"] != a.last_action or len(prop2["scores"]) > 1)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
