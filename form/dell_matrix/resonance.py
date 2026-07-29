#!/usr/bin/env python3
"""
ResonanceAct — NBD (equation after GraphView).

35[Discover] > 05[Tone] >> 14[Bind] :: Resonance

Connected units on the plane **actively enhance** each other:
- shared resonance score rises
- tag crumbs move across the enhance scope
- sandboxed units only enhance inside their box

This is DuoBeta-style synchronicity as runnable behavior (not only edges on a graph).

Run:
  python -m form.dell_matrix.resonance --smoke
  python -m form.dell_matrix.resonance --demo
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
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
    """Per-unit living resonance (personal plane memory)."""

    scores: Dict[str, float] = field(default_factory=dict)  # unit_id -> score
    tags: Dict[str, Dict[str, float]] = field(default_factory=dict)  # unit_id -> tag -> weight
    log: List[str] = field(default_factory=list)

    def score_of(self, unit_id: str) -> float:
        return float(self.scores.get(unit_id, 0.0))


def _tokens(label: str, words: str) -> List[str]:
    raw = f"{label} {words}".replace("[", " ").replace("]", " ")
    out = []
    for t in raw.split():
        t = t.strip().lower()
        if len(t) > 2 and not t.startswith("pulled:"):
            out.append(t)
    return out


def pulse(plane: Plane, state: Optional[ResonanceState] = None) -> ResonanceState:
    """
    One resonance pulse across the plane.
    Each unit enhances its enhance_scope peers (not itself).
    """
    assert_floor_intact()
    state = state or ResonanceState()

    # ensure keys
    for uid in plane.units:
        state.scores.setdefault(uid, 0.0)
        state.tags.setdefault(uid, {})

    for uid, u in plane.units.items():
        peers = plane.enhance_scope(uid)
        toks = _tokens(u.label, u.words)
        if not peers:
            state.log.append(f"{uid}: no peers (boxed or alone)")
            continue
        for peer_id in peers:
            # raise peer score
            state.scores[peer_id] = state.scores.get(peer_id, 0.0) + 0.25
            # move tag crumbs
            bucket = state.tags.setdefault(peer_id, {})
            for t in toks:
                bucket[t] = bucket.get(t, 0.0) + 0.15
            state.log.append(f"{uid} -enhance-> {peer_id} (+0.25, tags={toks[:4]})")

    return state


def harmonize_pair(plane: Plane, a_id: str, b_id: str, state: Optional[ResonanceState] = None) -> Dict[str, Any]:
    """
    Explicit pair resonance (vesica-style). Only if each is in the other's scope
    (both connected, or both in same sandbox).
    """
    assert_floor_intact()
    state = state or ResonanceState()
    a, b = plane.units.get(a_id), plane.units.get(b_id)
    if not a or not b:
        return {"ok": False, "reason": "missing unit"}
    scope_a, scope_b = set(plane.enhance_scope(a_id)), set(plane.enhance_scope(b_id))
    if b_id not in scope_a or a_id not in scope_b:
        return {"ok": False, "reason": "not in mutual enhance scope (boxed apart?)"}

    state.scores[a_id] = state.scores.get(a_id, 0.0) + 0.5
    state.scores[b_id] = state.scores.get(b_id, 0.0) + 0.5
    mid = f"relation({a.label}⊗{b.label})"
    for uid in (a_id, b_id):
        bucket = state.tags.setdefault(uid, {})
        bucket[mid.lower()] = bucket.get(mid.lower(), 0.0) + 0.5
    state.log.append(f"vesica {a_id}⊗{b_id} → {mid}")
    return {"ok": True, "middle": mid, "scores": {a_id: state.score_of(a_id), b_id: state.score_of(b_id)}}


def status(state: ResonanceState) -> Dict[str, Any]:
    return {
        "self": "ResonanceAct",
        "floor": list(FLOOR),
        "scores": dict(state.scores),
        "tags": {k: dict(v) for k, v in state.tags.items()},
        "log_tail": state.log[-12:],
    }


def smoke() -> bool:
    print("=== RESONANCE SMOKE ===")
    r: List[bool] = []

    def rec(name: str, ok: bool, detail: str = "") -> None:
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    cube = give("R")
    # remove welcome noise for clean scopes optional — keep and place two ideas
    cube.place_idea("biz", "Business", words="crm routes", skin=Skin.BUILDING, x=1)
    cube.place_idea("music", "Music", words="melody ep4", skin=Skin.SEED, x=-1)
    plane = cube.session.plane
    st = ResonanceState()
    st = pulse(plane, st)
    rec("pulse raises scores", st.score_of("biz") > 0 and st.score_of("music") > 0, str(st.scores))
    rec("tags moved", any("crm" in st.tags.get("music", {}) or "melody" in st.tags.get("biz", {}) for _ in [0]), str(st.tags))

    # box music — should not enhance biz anymore from music, and biz may still hit welcome etc.
    plane.box(["music"], "alone")
    st2 = ResonanceState()
    st2 = pulse(plane, st2)
    # music sandboxed alone → no peers
    rec("boxed alone no peers", st2.score_of("music") == 0.0 or "no peers" in "".join(st2.log))

    # two inside same box enhance each other only
    cube.place_idea("art", "Art", words="logo", skin=Skin.SPHERE, x=0, y=1)
    plane.box(["music", "art"], "studio")
    st3 = ResonanceState()
    st3 = pulse(plane, st3)
    rec("sandbox mutual", st3.score_of("music") > 0 and st3.score_of("art") > 0, str(st3.scores))
    # biz should not receive music/art tags from sandbox pulse in a strict read — enhance_scope of music is only art
    rec("vesica mutual", harmonize_pair(plane, "music", "art", st3).get("ok") is True)
    rec("vesica blocked to outside", harmonize_pair(plane, "music", "biz", ResonanceState()).get("ok") is False)
    rec("floor", status(st)["floor"] == list(FLOOR))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def demo() -> None:
    print("35[Discover] > 05[Tone] >> 14[Bind] :: Resonance")
    print("English: Connected units enhance each other; box isolates.\n")
    cube = give("Demo")
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
