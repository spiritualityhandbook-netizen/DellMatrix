#!/usr/bin/env python3
"""
Ringed Growth Engine — revolutionary but controlled.

Synthesizes:
- Voynich 5 rings: Seed → Token → Body → Lens → Evolve
- Stonehenge gates: growth only fires on alignment (threshold + ring law)
- Aetheris: FOG cut — only clear, structural proposals pass
- Ancient: full lineage preserved on every proposal
- Manelody: harmonic affinity (not only word overlap)
- DuoBeta: generation ledger + self-understand
- Nursery: all output quarantined until user confirms

Law:
1. Only live matrix ideas participate.
2. Proposals never auto-enter the matrix.
3. Nursery ideas cannot grow or influence.
4. Nothing in the live matrix is lost.
5. Every proposal carries parent lineage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import math
import re

from form.dell_matrix.nursery import Nursery
from form.dell_matrix.plane import Plane

# Voynich / DuoBeta structural rings
RINGS = ("Seed", "Token", "Body", "Lens", "Evolve")

_TOKEN = re.compile(r"[a-z0-9_]{3,}", re.I)

# Stonehenge-style alignment thresholds (practical solstice markers)
SOLSTICE_AFFINITY = 0.28   # strong alignment → new concept allowed
EQUINOX_AFFINITY = 0.16    # medium → evolved form allowed
STANSTILL_AFFINITY = 0.10  # weak → only deepen existing (still proposed)

# Aetheris FOG filters — reject unclear / pure noise proposals
FOG_MIN_LABEL_LEN = 3
FOG_MAX_LABEL_LEN = 72
FOG_BANNED_FRAGMENTS = ("asdf", "test123", "xxx", "???", "null", "undefined")


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
    """Manelody-style harmonic score: shared core + complementary tension."""
    if not a and not b:
        return 0.0
    jac = _jaccard(a, b)
    # complementarity: unique tokens that could bridge
    only_a, only_b = a - b, b - a
    bridge = min(len(only_a), len(only_b))
    tension = bridge / (1.0 + len(a | b))
    # harmonic mean bias toward balanced pairs
    if jac <= 0 and tension <= 0:
        return 0.0
    return (2 * jac * (jac + tension)) / (2 * jac + tension + 1e-9)


def _dist(plane: Plane, a: str, b: str) -> float:
    ua, ub = plane.units.get(a), plane.units.get(b)
    if not ua or not ub:
        return 99.0
    return math.hypot(ua.x - ub.x, ua.y - ub.y)


def _affinity(plane: Plane, a: str, b: str) -> Dict[str, float]:
    ua, ub = plane.units[a], plane.units[b]
    ta, tb = _tokens(ua.label, ua.words), _tokens(ub.label, ub.words)
    jac = _jaccard(ta, tb)
    harm = _harmonic(ta, tb)
    dist = _dist(plane, a, b)
    spatial = 1.0 / (1.0 + dist)
    scope = set(plane.enhance_scope(a))
    in_scope = 1.0 if b in scope else 0.2
    # blended score (Manelody + space + scope)
    aff = harm * 0.45 + jac * 0.25 + spatial * 0.15 + in_scope * 0.15
    return {
        "affinity": aff,
        "jaccard": jac,
        "harmonic": harm,
        "distance": dist,
        "shared": float(len(ta & tb)),
    }


def _aetheris_clear(label: str, words: str) -> bool:
    """FOG cut — reject low-clarity proposals."""
    lab = (label or "").strip()
    if len(lab) < FOG_MIN_LABEL_LEN or len(lab) > FOG_MAX_LABEL_LEN:
        return False
    low = lab.lower()
    if any(b in low for b in FOG_BANNED_FRAGMENTS):
        return False
    if lab.count("?") > 2 or lab.count("!") > 3:
        return False
    # must have at least one real token
    if not _tokens(lab, words):
        return False
    return True


def _ring_phase(affinity: float) -> str:
    """Stonehenge gate: which ring event fired."""
    if affinity >= SOLSTICE_AFFINITY:
        return "Solstice"   # strong → new concept
    if affinity >= EQUINOX_AFFINITY:
        return "Equinox"    # medium → evolve
    if affinity >= STANSTILL_AFFINITY:
        return "Standstill" # weak → deepen only
    return "None"


def _combine_label(a: str, b: str) -> str:
    aa, bb = a.strip()[:22], b.strip()[:22]
    if aa.lower() == bb.lower():
        return f"{aa} (deepened)"
    return f"{aa} × {bb}"


def _evolve_label(label: str, gained: Set[str]) -> str:
    tip = " / ".join(sorted(gained)[:2]) if gained else "expanded"
    return f"{label} → {tip}"[:70]


@dataclass
class RingedGrowth:
    """
    Full pipeline:
      Seed (live ideas)
        → Token (extract patterns)
        → Body (form candidates)
        → Lens (Aetheris FOG + Stonehenge gates)
        → Evolve (Nursery proposals with Ancient lineage)
    """

    nursery: Nursery = field(default_factory=Nursery.load)
    max_new: int = 10
    max_evolved: int = 8

    def run(self, plane: Plane, cycles: int = 1) -> Dict[str, Any]:
        report: List[Dict[str, Any]] = []
        total_new = 0
        total_evo = 0
        fog_cut = 0
        gate_counts = {"Solstice": 0, "Equinox": 0, "Standstill": 0, "None": 0}

        for cycle in range(max(1, cycles)):
            ids = list(plane.units.keys())
            if len(ids) < 1:
                report.append({"cycle": cycle + 1, "ok": False, "reason": "no live ideas"})
                continue

            # --- Ring 1–2: Seed + Token — pair scan ---
            pairs: List[Tuple[str, str, Dict[str, float]]] = []
            for i, a in enumerate(ids):
                for b in ids[i + 1 :]:
                    aff = _affinity(plane, a, b)
                    pairs.append((a, b, aff))
            pairs.sort(key=lambda t: -t[2]["affinity"])

            new_this = 0
            evo_this = 0

            # --- Ring 3–5: Body → Lens → Evolve ---
            for a, b, aff in pairs:
                gate = _ring_phase(aff["affinity"])
                gate_counts[gate] = gate_counts.get(gate, 0) + 1

                if gate == "None":
                    continue

                ua, ub = plane.units[a], plane.units[b]
                ta, tb = _tokens(ua.label, ua.words), _tokens(ub.label, ub.words)
                shared = ta & tb
                unique = (ta | tb) - shared

                if gate == "Solstice" and new_this < self.max_new:
                    label = _combine_label(ua.label, ub.label)
                    words = (
                        f"[Ring:Evolve] Solstice resonance. "
                        f"Parents: {ua.label} + {ub.label}. "
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
                        reason=f"Solstice harm={aff['harmonic']:.2f} jac={aff['jaccard']:.2f}",
                    )
                    new_this += 1
                    total_new += 1

                elif gate in ("Equinox", "Standstill") and evo_this < self.max_evolved:
                    # evolve the stronger parent
                    primary = a if aff["affinity"] >= 0 else b
                    u = plane.units[primary]
                    peer = plane.units[b if primary == a else a]
                    gained = _tokens(peer.label, peer.words) - _tokens(u.label, u.words)
                    label = _evolve_label(u.label, gained or shared)
                    words = (
                        f"[Ring:Evolve] {gate} evolution. "
                        f"From: {u.label}. Touch: {peer.label}. "
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
                        reason=f"{gate} harm={aff['harmonic']:.2f}",
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
            "law": "proposals quarantined · live matrix untouched · lineage preserved",
        }
