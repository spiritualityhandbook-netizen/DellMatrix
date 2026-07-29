#!/usr/bin/env python3
"""
ResonanceAct L3.

35[Discover] > 05[Tone] >> 14[Bind] :: Resonance

Connected units enhance peers. Sandbox isolates.
L3: pulse history, optional decay, clear, richer harmonize.

Run:
  python -m form.dell_matrix.resonance --smoke
  python -m form.dell_matrix.resonance --demo
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin
    from form.dell_matrix.blank_cube import give
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin
    from form.dell_matrix.blank_cube import give


@dataclass
class ResonanceState:
    scores: Dict[str, float] = field(default_factory=dict)
    tags: Dict[str, Dict[str, float]] = field(default_factory=dict)
    log: List[str] = field(default_factory=list)
    pulse_count: int = 0
    level: int = 3

    def score_of(self, unit_id: str) -> float:
        return float(self.scores.get(unit_id, 0.0))

    def top_tags(self, unit_id: str, n: int = 5) -> List[tuple]:
        bucket = self.tags.get(unit_id, {})
        return sorted(bucket.items(), key=lambda kv: -kv[1])[:n]


def _tokens(label: str, words: str) -> List[str]:
    raw = f"{label} {words}".replace("[", " ").replace("]", " ")
    out = []
    for t in raw.split():
        t = t.strip().lower()
        if len(t) > 2 and not t.startswith("pulled:"):
            out.append(t)
    return out


def pulse(
    plane: Plane,
    state: Optional[ResonanceState] = None,
    *,
    amount: float = 0.25,
    tag_amount: float = 0.15,
) -> ResonanceState:
    assert_floor_intact()
    state = state or ResonanceState()
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")

    for uid in plane.units:
        state.scores.setdefault(uid, 0.0)
        state.tags.setdefault(uid, {})

    for uid, u in plane.units.items():
        peers = plane.enhance_scope(uid)
        toks = _tokens(u.label, u.words)
        if not peers:
            state.log.append(f"{ts} {uid}: no peers")
            continue
        for peer_id in peers:
            state.scores[peer_id] = state.scores.get(peer_id, 0.0) + amount
            bucket = state.tags.setdefault(peer_id, {})
            for t in toks:
                bucket[t] = bucket.get(t, 0.0) + tag_amount
            state.log.append(f"{ts} {uid} -enhance-> {peer_id} (+{amount})")

    state.pulse_count += 1
    state.log.append(f"{ts} pulse #{state.pulse_count} complete")
    return state


def decay(state: ResonanceState, factor: float = 0.9) -> ResonanceState:
    """Multiply all scores/tags by factor (0-1). Floor-safe."""
    assert_floor_intact()
    factor = max(0.0, min(1.0, factor))
    state.scores = {k: v * factor for k, v in state.scores.items()}
    state.tags = {
        uid: {t: w * factor for t, w in bucket.items()}
        for uid, bucket in state.tags.items()
    }
    state.log.append(f"decay factor={factor}")
    return state


def clear(state: ResonanceState) -> ResonanceState:
    state.scores.clear()
    state.tags.clear()
    state.log.append("clear")
    return state


def harmonize_pair(
    plane: Plane,
    a_id: str,
    b_id: str,
    state: Optional[ResonanceState] = None,
    *,
    amount: float = 0.5,
) -> Dict[str, Any]:
    assert_floor_intact()
    state = state or ResonanceState()
    a, b = plane.units.get(a_id), plane.units.get(b_id)
    if not a or not b:
        return {"ok": False, "reason": "missing unit"}
    scope_a, scope_b = set(plane.enhance_scope(a_id)), set(plane.enhance_scope(b_id))
    if b_id not in scope_a or a_id not in scope_b:
        return {"ok": False, "reason": "not in mutual enhance scope"}

    state.scores[a_id] = state.scores.get(a_id, 0.0) + amount
    state.scores[b_id] = state.scores.get(b_id, 0.0) + amount
    mid = f"relation({a.label}⊗{b.label})"
    for uid, other in ((a_id, b), (b_id, a)):
        bucket = state.tags.setdefault(uid, {})
        bucket[mid.lower()] = bucket.get(mid.lower(), 0.0) + amount
        for t in _tokens(other.label, other.words):
            bucket[t] = bucket.get(t, 0.0) + amount * 0.3
    state.log.append(f"vesica {a_id}⊗{b_id} → {mid}")
    return {
        "ok": True,
        "middle": mid,
        "scores": {a_id: state.score_of(a_id), b_id: state.score_of(b_id)},
        "top_a": state.top_tags(a_id, 3),
        "top_b": state.top_tags(b_id, 3),
    }


def status(state: ResonanceState) -> Dict[str, Any]:
    return {
        "self": "ResonanceAct",
        "level": state.level,
        "pulse_count": state.pulse_count,
        "floor": list(FLOOR),
        "scores": dict(state.scores),
        "tags": {k: dict(v) for k, v in state.tags.items()},
        "log_tail": state.log[-12:],
    }


def smoke() -> bool:
    print("=== RESONANCE L3 SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    cube = give("R", clean=True)
    cube.place_idea("biz", "Business", words="crm routes", skin=Skin.BUILDING, x=1)
    cube.place_idea("music", "Music", words="melody ep4", skin=Skin.SEED, x=-1)
    plane = cube.session.plane
    st = ResonanceState()
    st = pulse(plane, st)
    rec("level 3", st.level == 3)
    rec("pulse count", st.pulse_count == 1)
    rec("scores", st.score_of("biz") > 0 and st.score_of("music") > 0)
    before = st.score_of("biz")
    st = decay(st, 0.5)
    rec("decay", st.score_of("biz") == before * 0.5)
    st = pulse(plane, st)
    rec("pulse 2", st.pulse_count == 2)
    h = harmonize_pair(plane, "biz", "music", st)
    rec("harmonize", h.get("ok") is True and "top_a" in h)
    plane.box(["music"], "alone")
    st2 = pulse(plane, ResonanceState())
    rec("boxed alone", "no peers" in "".join(st2.log))
    clear(st)
    rec("clear", st.score_of("biz") == 0.0)
    rec("floor", status(st)["floor"] == list(FLOOR))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def demo() -> None:
    print("35[Discover] > 05[Tone] >> 14[Bind] :: Resonance L3")
    cube = give("Demo", clean=True)
    cube.place_idea("biz", "Business", words="crm", skin=Skin.BUILDING, x=1)
    cube.place_idea("music", "Music", words="song", skin=Skin.SEED, x=-1)
    st = pulse(cube.session.plane)
    print(json.dumps(status(st), indent=2))
    print(harmonize_pair(cube.session.plane, "biz", "music", st))


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()


if __name__ == "__main__":
    main()
