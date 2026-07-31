#!/usr/bin/env python3
"""
Growth Engine — powerful evolution, controlled by Nursery quarantine.

Rules:
1. Only ACTIVE (confirmed) matrix ideas participate in resonance.
2. Growth can be aggressive: many new + evolved proposals.
3. All proposals go into the Nursery (Void / Op-Box).
4. Nursery ideas cannot grow and cannot influence anything.
5. User must confirm before anything enters the live matrix.
6. Nothing is ever lost from the active matrix during growth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple
import math
import re

from form.dell_matrix.nursery import Nursery, Proposal
from form.dell_matrix.plane import Plane

_TOKEN = re.compile(r"[a-z0-9_]{3,}", re.I)


def _tokens(label: str, words: str) -> Set[str]:
    raw = f"{label} {words}".lower()
    return {m.group(0).lower() for m in _TOKEN.finditer(raw)}


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _dist(plane: Plane, a: str, b: str) -> float:
    ua, ub = plane.units.get(a), plane.units.get(b)
    if not ua or not ub:
        return 99.0
    return math.hypot(ua.x - ub.x, ua.y - ub.y)


def _affinity(plane: Plane, a: str, b: str) -> Dict[str, float]:
    ua, ub = plane.units[a], plane.units[b]
    ta, tb = _tokens(ua.label, ua.words), _tokens(ub.label, ub.words)
    jac = _jaccard(ta, tb)
    dist = _dist(plane, a, b)
    spatial = 1.0 / (1.0 + dist)
    # sandboxed units still exist but grow weaker across walls
    scope = set(plane.enhance_scope(a))
    in_scope = 1.0 if b in scope else 0.25
    aff = jac * 0.55 + spatial * 0.25 + in_scope * 0.20
    return {
        "affinity": aff,
        "jaccard": jac,
        "distance": dist,
        "shared": float(len(ta & tb)),
    }


def _combine_label(a: str, b: str) -> str:
    """Create a readable new concept name from two parents."""
    aa = a.strip()[:24]
    bb = b.strip()[:24]
    if aa.lower() == bb.lower():
        return f"{aa} (deepened)"
    return f"{aa} × {bb}"


def _evolve_label(label: str, shared: Set[str]) -> str:
    tip = " / ".join(sorted(shared)[:2]) if shared else "expanded"
    return f"{label} → {tip}"[:70]


@dataclass
class GrowthEngine:
    nursery: Nursery = field(default_factory=Nursery.load)
    min_affinity: float = 0.12
    max_new_per_cycle: int = 12
    max_evolved_per_cycle: int = 8

    def run(self, plane: Plane, cycles: int = 1) -> Dict[str, Any]:
        """
        Scan active matrix only. Propose new + evolved ideas into Nursery.
        Never mutates active matrix ideas away. Never loses them.
        """
        report: List[Dict[str, Any]] = []
        created_new = 0
        created_evolved = 0

        for cycle in range(max(1, cycles)):
            ids = list(plane.units.keys())
            if len(ids) < 1:
                report.append({"cycle": cycle + 1, "ok": False, "reason": "no ideas yet"})
                continue

            pairs: List[Tuple[str, str, Dict[str, float]]] = []
            for i, a in enumerate(ids):
                for b in ids[i + 1 :]:
                    aff = _affinity(plane, a, b)
                    if aff["affinity"] >= self.min_affinity:
                        pairs.append((a, b, aff))

            pairs.sort(key=lambda t: -t[2]["affinity"])

            new_this = 0
            evo_this = 0

            # --- New ideas from strong resonance ---
            for a, b, aff in pairs:
                if new_this >= self.max_new_per_cycle:
                    break
                ua, ub = plane.units[a], plane.units[b]
                ta, tb = _tokens(ua.label, ua.words), _tokens(ub.label, ub.words)
                shared = ta & tb
                unique = (ta | tb) - shared

                label = _combine_label(ua.label, ub.label)
                words = (
                    f"Resonance of '{ua.label}' and '{ub.label}'. "
                    f"Shared: {', '.join(sorted(shared)[:6]) or 'none'}. "
                    f"Bridge: {', '.join(sorted(unique)[:8]) or 'none'}."
                )
                prop = self.nursery.add(
                    label=label,
                    words=words,
                    kind="new",
                    parents=[a, b],
                    affinity=aff["affinity"],
                    reason=f"resonance jac={aff['jaccard']:.2f} dist={aff['distance']:.1f}",
                )
                new_this += 1
                created_new += 1

            # --- Evolve existing ideas (as proposals only) ---
            # Rank ideas by how much they resonate with others
            strength: Dict[str, float] = {i: 0.0 for i in ids}
            touch: Dict[str, Set[str]] = {i: set() for i in ids}
            for a, b, aff in pairs:
                strength[a] += aff["affinity"]
                strength[b] += aff["affinity"]
                touch[a].add(b)
                touch[b].add(a)

            ranked = sorted(strength.items(), key=lambda kv: -kv[1])
            for uid, score in ranked:
                if evo_this >= self.max_evolved_per_cycle:
                    break
                if score < self.min_affinity:
                    continue
                u = plane.units[uid]
                peers = touch.get(uid, set())
                peer_tokens: Set[str] = set()
                for pid in peers:
                    peer = plane.units.get(pid)
                    if peer:
                        peer_tokens |= _tokens(peer.label, peer.words)
                own = _tokens(u.label, u.words)
                gained = peer_tokens - own
                if not gained and not peers:
                    continue
                label = _evolve_label(u.label, gained or own)
                words = (
                    f"Evolution of '{u.label}'. "
                    f"Influenced by: {', '.join(sorted(peers)[:6]) or 'self'}. "
                    f"New threads: {', '.join(sorted(gained)[:8]) or 'deepening'}."
                )
                self.nursery.add(
                    label=label,
                    words=words,
                    kind="evolved",
                    parents=[uid],
                    affinity=score,
                    reason=f"evolved from active idea strength={score:.2f}",
                )
                evo_this += 1
                created_evolved += 1

            report.append(
                {
                    "cycle": cycle + 1,
                    "ok": True,
                    "active_ideas": len(ids),
                    "resonant_pairs": len(pairs),
                    "proposed_new": new_this,
                    "proposed_evolved": evo_this,
                }
            )

        return {
            "ok": True,
            "cycles": cycles,
            "proposed_new": created_new,
            "proposed_evolved": created_evolved,
            "nursery": self.nursery.summary(),
            "steps": report,
        }
