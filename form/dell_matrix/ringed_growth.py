#!/usr/bin/env python3
"""Ringed Growth — sole public growth path. Body pulse first. Goals bias affinity."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import math
import re

from form.dell_matrix.nursery import Nursery
from form.dell_matrix.plane import Plane

RINGS = ("Seed", "Token", "Body", "Lens", "Evolve")
_TOKEN = re.compile(r"[a-z0-9_]{3,}", re.I)

SOLSTICE_AFFINITY = 0.28
EQUINOX_AFFINITY = 0.16
STANSTILL_AFFINITY = 0.10
FOG_MIN_LABEL_LEN = 3
FOG_MAX_LABEL_LEN = 72
FOG_BANNED_FRAGMENTS = ("asdf", "test123", "xxx", "???", "null", "undefined")


def _body_pulse_safe() -> Dict[str, Any]:
    """Sense organs before proposing rings. Never crash growth on body failure."""
    try:
        from form.dell_matrix.matrix_body import body_pulse
        return body_pulse()
    except Exception as e:
        return {
            "ok": False,
            "error": f"{type(e).__name__}: {e}",
            "missing": [],
            "decisions": [],
            "law": "body pulse unavailable — growth continues cautious",
        }


def _vital_block(body: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """If vital organs missing, block Solstice (new rings) until restore path is clear."""
    missing = list(body.get("missing") or [])
    vital_names = {
        "floor", "nursery", "lattice", "plane", "forces",
        "ringed_growth", "english_brain", "gate", "nature",
    }
    vital_missing = [m for m in missing if m in vital_names]
    # ringed_growth is this module — if listed missing only due to probe path, ignore self
    vital_missing = [m for m in vital_missing if m != "ringed_growth"]
    return (len(vital_missing) > 0, vital_missing)


def _unit_blob(plane: Plane, uid: str) -> str:
    u = plane.units.get(uid)
    if not u:
        return ""
    if hasattr(u, "full_text"):
        return u.full_text()
    goals = " ".join(getattr(u, "goals", []) or [])
    detail = getattr(u, "detail", "") or ""
    return f"{u.label} {detail} {u.words} {goals}"


def _tokens_uid(plane: Plane, uid: str) -> Set[str]:
    return {m.group(0).lower() for m in _TOKEN.finditer(_unit_blob(plane, uid))}


def _tokens(label: str, words: str) -> Set[str]:
    raw = f"{label} {words}".lower()
    return {m.group(0).lower() for m in _TOKEN.finditer(raw)}


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _harmonic(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 0.0
    jac = _jaccard(a, b)
    only_a, only_b = a - b, b - a
    bridge = min(len(only_a), len(only_b))
    tension = bridge / (1.0 + len(a | b))
    if jac <= 0 and tension <= 0:
        return 0.0
    return (2 * jac * (jac + tension)) / (2 * jac + tension + 1e-9)


def _dist(plane: Plane, a: str, b: str) -> float:
    ua, ub = plane.units.get(a), plane.units.get(b)
    if not ua or not ub:
        return 99.0
    return math.hypot(ua.x - ub.x, ua.y - ub.y)


def _goal_boost(plane: Plane, a: str, b: str) -> float:
    ua, ub = plane.units.get(a), plane.units.get(b)
    if not ua or not ub:
        return 0.0
    ga = {t.lower() for g in (getattr(ua, "goals", []) or []) for t in _TOKEN.findall(g)}
    gb = {t.lower() for g in (getattr(ub, "goals", []) or []) for t in _TOKEN.findall(g)}
    if not ga and not gb:
        return 0.0
    if not ga or not gb:
        return 0.05
    return 0.12 * _jaccard(ga, gb)


def _body_goal_boost(body: Dict[str, Any], label_a: str, label_b: str) -> float:
    """Boost affinity when idea text touches missing organ names (heal path)."""
    missing = [m.lower() for m in (body.get("missing") or [])]
    if not missing:
        return 0.0
    blob = f"{label_a} {label_b}".lower()
    hits = sum(1 for m in missing if m in blob or m.replace("_", " ") in blob)
    return min(0.15, 0.05 * hits)


def _affinity(plane: Plane, a: str, b: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
    ta, tb = _tokens_uid(plane, a), _tokens_uid(plane, b)
    jac = _jaccard(ta, tb)
    harm = _harmonic(ta, tb)
    dist = _dist(plane, a, b)
    spatial = 1.0 / (1.0 + dist)
    scope = set(plane.enhance_scope(a))
    in_scope = 1.0 if b in scope else 0.2
    gboost = _goal_boost(plane, a, b)
    ua, ub = plane.units.get(a), plane.units.get(b)
    bboost = 0.0
    if body is not None and ua and ub:
        bboost = _body_goal_boost(body, ua.label, ub.label)
    aff = harm * 0.40 + jac * 0.22 + spatial * 0.13 + in_scope * 0.13 + gboost + bboost
    return {
        "affinity": aff,
        "jaccard": jac,
        "harmonic": harm,
        "distance": dist,
        "shared": float(len(ta & tb)),
        "goal_boost": gboost,
        "body_boost": bboost,
    }


def _aetheris_clear(label: str, words: str) -> bool:
    lab = (label or "").strip()
    if len(lab) < FOG_MIN_LABEL_LEN or len(lab) > FOG_MAX_LABEL_LEN:
        return False
    low = lab.lower()
    if any(b in low for b in FOG_BANNED_FRAGMENTS):
        return False
    if lab.count("?") > 2 or lab.count("!") > 3:
        return False
    if not _tokens(lab, words):
        return False
    return True


def _ring_phase(affinity: float) -> str:
    if affinity >= SOLSTICE_AFFINITY:
        return "Solstice"
    if affinity >= EQUINOX_AFFINITY:
        return "Equinox"
    if affinity >= STANSTILL_AFFINITY:
        return "Standstill"
    return "None"


def _combine_label(a: str, b: str) -> str:
    aa, bb = a.strip()[:22], b.strip()[:22]
    if aa.lower() == bb.lower():
        return f"{aa} (deepened)"
    return f"{aa} × {bb}"


def _evolve_label(label: str, gained: Set[str]) -> str:
    tip = " / ".join(sorted(gained)[:2]) if gained else "expanded"
    return f"{label} → {tip}"[:70]


def _parent_goals(plane: Plane, ids: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for i in ids:
        u = plane.units.get(i)
        if not u:
            continue
        for g in getattr(u, "goals", []) or []:
            g = g.strip()
            if g and g.lower() not in seen:
                seen.add(g.lower())
                out.append(g)
    return out[:8]


@dataclass
class RingedGrowth:
    nursery: Nursery = field(default_factory=Nursery.load)
    max_new: int = 10
    max_evolved: int = 8

    def run(self, plane: Plane, cycles: int = 1) -> Dict[str, Any]:
        report: List[Dict[str, Any]] = []
        total_new = 0
        total_evo = 0
        fog_cut = 0
        gate_counts = {"Solstice": 0, "Equinox": 0, "Standstill": 0, "None": 0}
        body_snapshots: List[Dict[str, Any]] = []

        for cycle in range(max(1, cycles)):
            # --- BODY PULSE FIRST — sense organs before proposing rings ---
            body = _body_pulse_safe()
            blocked, vital_missing = _vital_block(body)
            body_snapshots.append({
                "cycle": cycle + 1,
                "present": body.get("present"),
                "missing": body.get("missing"),
                "top_decision": (body.get("decisions") or [{}])[0],
                "solstice_blocked": blocked,
                "vital_missing": vital_missing,
            })

            # If vital organs missing, propose nursery restore ideas instead of free Solstice
            if blocked and vital_missing:
                for organ in vital_missing[:3]:
                    label = f"Restore {organ}"
                    words = (
                        f"[Ring:Body] Vital organ '{organ}' missing. "
                        f"Body decision: densify_or_restore. "
                        f"Goal: {body.get('goal', 'coherence')}. "
                        f"Law: problem = missing organ."
                    )
                    if _aetheris_clear(label, words):
                        self.nursery.add(
                            label=label,
                            words=words,
                            kind="evolved",
                            parents=[],
                            affinity=0.5,
                            reason=f"body_pulse vital_missing={organ}",
                        )
                        total_evo += 1

            ids = list(plane.units.keys())
            if len(ids) < 1:
                report.append({
                    "cycle": cycle + 1,
                    "ok": False,
                    "reason": "no live ideas",
                    "body": body_snapshots[-1],
                })
                continue

            pairs: List[Tuple[str, str, Dict[str, float]]] = []
            for i, a in enumerate(ids):
                for b in ids[i + 1 :]:
                    aff = _affinity(plane, a, b, body=body)
                    pairs.append((a, b, aff))
            pairs.sort(key=lambda t: -t[2]["affinity"])

            new_this = 0
            evo_this = 0

            for a, b, aff in pairs:
                gate = _ring_phase(aff["affinity"])
                gate_counts[gate] = gate_counts.get(gate, 0) + 1
                if gate == "None":
                    continue

                # Revised law: Solstice (new rings) paused while vital organs missing
                if gate == "Solstice" and blocked:
                    continue

                ua, ub = plane.units[a], plane.units[b]
                ta, tb = _tokens_uid(plane, a), _tokens_uid(plane, b)
                shared = ta & tb
                unique = (ta | tb) - shared
                parent_goals = _parent_goals(plane, [a, b])
                goal_line = (
                    f"Goals toward: {'; '.join(parent_goals)}. "
                    if parent_goals
                    else "Goals: (parents had none — prefer adding goals on live ideas). "
                )

                if gate == "Solstice" and new_this < self.max_new:
                    label = _combine_label(ua.label, ub.label)
                    words = (
                        f"[Ring:Evolve] Solstice resonance. "
                        f"Parents: {ua.label} + {ub.label}. "
                        f"{goal_line}"
                        f"Shared: {', '.join(sorted(shared)[:5]) or '—'}. "
                        f"Bridge: {', '.join(sorted(unique)[:6]) or '—'}. "
                        f"Lineage: {a}|{b}."
                    )
                    if not _aetheris_clear(label, words):
                        fog_cut += 1
                        continue
                    self.nursery.add(
                        label=label,
                        words=words,
                        kind="new",
                        parents=[a, b],
                        affinity=aff["affinity"],
                        reason=f"Solstice harm={aff['harmonic']:.2f} goals={aff.get('goal_boost', 0):.2f}",
                    )
                    new_this += 1
                    total_new += 1

                elif gate in ("Equinox", "Standstill") and evo_this < self.max_evolved:
                    primary = a
                    u = plane.units[primary]
                    peer = plane.units[b]
                    gained = _tokens_uid(plane, b) - _tokens_uid(plane, a)
                    label = _evolve_label(u.label, gained or shared)
                    words = (
                        f"[Ring:Evolve] {gate} evolution. "
                        f"From: {u.label}. Touch: {peer.label}. "
                        f"{goal_line}"
                        f"New threads: {', '.join(sorted(gained)[:6]) or 'deepening'}. "
                        f"Lineage: {primary}."
                    )
                    if not _aetheris_clear(label, words):
                        fog_cut += 1
                        continue
                    self.nursery.add(
                        label=label,
                        words=words,
                        kind="evolved",
                        parents=[primary],
                        affinity=aff["affinity"],
                        reason=f"{gate} harm={aff['harmonic']:.2f} goals={aff.get('goal_boost', 0):.2f}",
                    )
                    evo_this += 1
                    total_evo += 1

            report.append(
                {
                    "cycle": cycle + 1,
                    "ok": True,
                    "live_ideas": len(ids),
                    "pairs_scanned": len(pairs),
                    "proposed_new": new_this,
                    "proposed_evolved": evo_this,
                    "rings": list(RINGS),
                    "body": body_snapshots[-1],
                    "solstice_blocked": blocked,
                }
            )

        return {
            "ok": True,
            "engine": "RingedGrowth",
            "rings": list(RINGS),
            "cycles": cycles,
            "proposed_new": total_new,
            "proposed_evolved": total_evo,
            "fog_cut": fog_cut,
            "gates": gate_counts,
            "nursery": self.nursery.summary(),
            "steps": report,
            "body_pulses": body_snapshots,
            "law": (
                "body pulse first · vital gaps block Solstice · "
                "proposals quarantined · goal-biased · live matrix untouched"
            ),
        }


def smoke() -> bool:
    print("=== RINGED GROWTH SMOKE ===")
    r = []
    def rec(n, ok, d=""):
        print(f"[{len(r)+1}] {n}: {'PASS' if ok else 'FAIL'}" + (f" | {d}" if d else ""))
        r.append(bool(ok))
    # body pulse path alone
    body = _body_pulse_safe()
    rec("body_pulse_callable", isinstance(body, dict))
    blocked, vital = _vital_block({"missing": ["floor", "fourier"]})
    rec("vital_block_floor", blocked and "floor" in vital)
    rec("fourier_not_vital_block", "fourier" not in vital)
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
