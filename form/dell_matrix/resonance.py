#!/usr/bin/env python3
"""
ResonanceAct L3.

35[Discover] > 05[Tone] >> 14[Bind] :: Resonance

Connected units enhance peers. Sandbox isolates.
L3: pulse history, optional decay, clear, richer harmonize.

Run:
  python -m form.dell_matrix.resonance --smoke
  python -m form.dell_matrix.resonance --demo

CONCEPT SEPARATION (GDP-001 Phase 3, 3.1.2): this module's ``pulse`` is
DIFFUSION over the resonance graph — score/tag accumulation propagated
across enhance-scope edges over time. ``ringed_growth._affinity`` is a
DIFFERENT concept: one-shot PAIR SCORING (deterministic composite of
harmonic/Jaccard/spatial/scope/goal terms) used to rank idea pairs for
growth-ring proposals. Keep both; do not merge pulse into affinity or
affinity into pulse.

RESONANCE vs VERITA FIREWALL (GDP-001 Phase 3, 3.1.5): Resonance =
pulse/diffusion over the resonance graph + pair affinity for growth.
Verita (form.dell_matrix.verita) = solo integrity + pair coherence scoring
(vesica overlap). They are PARALLEL mechanisms with distinct contracts.
Merging them is prohibited (established architectural decision: Verita/Smith
ancestry must not be merged with other mechanisms merely for sharing
imagery or a name).
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
    from form.dell_matrix import faded_policy  # P3 R3.5.2: faded-state exclusion
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix import faded_policy  # P3 R3.5.2: faded-state exclusion


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
    """Diffuse resonance scores/tags across enhance-scope edges (one step).

    Faded-state policy (P3 R3.5.2, repaired consolidated): faded units
    have zero effective influence. They neither send nor receive, they
    get no new score/tag entries, and — because ``state`` is routinely
    reused across pulses — any scores/tags they RETAINED from before
    they faded are dropped at pulse time so they cannot influence
    future diffusion or downstream consumers (e.g. score_of, status,
    graph views). History is preserved: the pulse is still counted and
    the exclusion is recorded in ``state.log``; ``state.log`` is never
    pruned here (use ``clear`` to reset). All-faded input yields empty
    scores/tags, never an exception.
    """
    assert_floor_intact()
    state = state or ResonanceState()
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")

    # P3 R3.5.2: faded-state exclusion (logic only). Faded units are
    # excluded from propagation: they neither send nor receive. They get
    # no score/tag entries at all. All-faded input yields an empty
    # result, never an exception.
    faded_ids = {uid for uid, u in plane.units.items()
                 if faded_policy.is_faded(u)}
    # Reused state may retain scores/tags for units that faded AFTER
    # their last active pulse. Drop those retained entries so faded
    # units exert zero effective influence going forward; keep the log
    # (history is preserved, not rewritten).
    for uid in set(state.scores) | set(state.tags):
        if uid in faded_ids:
            state.scores.pop(uid, None)
            state.tags.pop(uid, None)
            state.log.append(f"{ts} {uid}: faded, retained scores/tags excluded")
    for uid in plane.units:
        if uid in faded_ids:
            continue
        state.scores.setdefault(uid, 0.0)
        state.tags.setdefault(uid, {})

    for uid, u in plane.units.items():
        if uid in faded_ids:
            continue
        peers = [p for p in plane.enhance_scope(uid) if p not in faded_ids]
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
    """Resonance-state write for one pair of plane units (not a harmony metric).

    Honest description (R3.2.2): bumps both units' resonance scores by
    ``amount`` and records cross-tags in ``state`` when the units are in
    mutual enhance scope; fails closed ({"ok": False, ...}) for missing
    units or units outside mutual scope. This is a state-mutating
    resonance operation owned by the pulse/diffusion subsystem
    (live caller: EnhanceGate.harmonize <- idea_grow.py), NOT the R3.2
    set-coherence metric harmony_score (form/dell_matrix/harmony.py),
    which is stateless and operates on idea sets. Name kept for
    compatibility; behavior unchanged.
    """
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
