#!/usr/bin/env python3
"""
Alpha Spirit — orientation above Verita.

Law:
  Floor = (Alpha, Delta, Omega, Omni) — immutable host law.
  Alpha is not a local truth-score. Alpha is the bigger picture:
  origin intent, whole-body why, what the matrix is *for*.

  Verita judges local coherence (one idea / two ideas).
  Alpha judges alignment with the whole.
  Verita listens to Alpha: a link can be locally coherent and still
  be refused if it fights the Alpha orientation.

Structural only — not paranormal claim.
Dell 20[Alpha] · Floor first pillar.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import re
import time

_TOKEN = re.compile(r"[a-z0-9_]{3,}", re.I)

# Default Alpha orientation for DellMatrix as one living offline-capable body
DEFAULT_ALPHA = (
    "one body coherent offline-capable intelligence · "
    "problem means missing organ · verita judges local truth · "
    "growth densifies toward whole · floor locked Alpha Delta Omega Omni"
)


def _tokens(text: str) -> Set[str]:
    return {m.group(0).lower() for m in _TOKEN.finditer(text or "")}


@dataclass
class AlphaOrientation:
    """Bigger picture the mind serves."""
    statement: str = DEFAULT_ALPHA
    priorities: List[str] = field(default_factory=lambda: [
        "floor_intact",
        "vital_organs",
        "offline_first",
        "local_verita",
        "honest_residue",
        "goal_biased_growth",
    ])
    origin: str = "Alpha"  # Floor pillar
    updated_ts: float = field(default_factory=time.time)

    def tokens(self) -> Set[str]:
        return _tokens(self.statement + " " + " ".join(self.priorities))

    def as_dict(self) -> Dict[str, Any]:
        return {
            "statement": self.statement,
            "priorities": list(self.priorities),
            "origin": self.origin,
            "updated_ts": self.updated_ts,
            "role": "alpha_spirit",
            "note": "bigger picture · Verita listens here · not local overlap score",
        }


class AlphaSpirit:
    """
    Spirit-over-mind layer.
    Sees the Alpha of the system: whole orientation, not pairwise vesica.
    """

    def __init__(self, orientation: Optional[AlphaOrientation] = None):
        self.orientation = orientation or AlphaOrientation()
        self.log: List[Dict[str, Any]] = []

    def set_orientation(self, statement: str, priorities: Optional[List[str]] = None) -> Dict[str, Any]:
        self.orientation.statement = (statement or "").strip() or DEFAULT_ALPHA
        if priorities:
            self.orientation.priorities = list(priorities)
        self.orientation.updated_ts = time.time()
        return self.orientation.as_dict()

    def alignment(self, text: str) -> Dict[str, Any]:
        """How well does this idea/link serve the Alpha orientation?"""
        t = _tokens(text)
        a = self.orientation.tokens()
        if not t:
            return {"score": 0.0, "grade": "empty", "aligned": False}
        inter = len(t & a)
        # also reward priority keyword hits
        pri_hits = sum(1 for p in self.orientation.priorities if p.replace("_", " ") in text.lower() or p in t)
        jaccard = inter / max(1, len(t | a))
        score = min(1.0, 0.55 * jaccard + 0.15 * min(1.0, inter / 3.0) + 0.30 * min(1.0, pri_hits / 3.0))
        # soft floor: directional growth language still partially aligns with Alpha
        directional = {"restore", "grow", "whole", "body", "organ", "floor", "offline", "coherent", "verita", "heal"}
        if t & directional:
            score = max(score, 0.35)
        score = round(score, 4)
        if score >= 0.45:
            grade, aligned = "aligned", True
        elif score >= 0.25:
            grade, aligned = "partial", True
        else:
            grade, aligned = "drift", False
        return {
            "score": score,
            "grade": grade,
            "aligned": aligned,
            "shared": sorted(t & a)[:8],
            "priority_hits": pri_hits,
        }

    def license_verita(self, verita_report: Dict[str, Any], subject_text: str) -> Dict[str, Any]:
        """
        Verita listens to Alpha.
        Local accept can be demoted if Alpha alignment is drift.
        Local reject stays reject (Alpha does not invent false coherence).
        """
        align = self.alignment(subject_text)
        local_accept = bool(verita_report.get("accept"))
        local_score = float(verita_report.get("score") or 0.0)

        if not local_accept:
            final_accept = False
            reason = "verita_local_reject"
        elif not align["aligned"]:
            final_accept = False
            reason = "alpha_drift · locally coherent but fights bigger picture"
        else:
            final_accept = True
            reason = "verita_ok · alpha_aligned"

        out = {
            "final_accept": final_accept,
            "reason": reason,
            "verita": {
                "accept": local_accept,
                "score": local_score,
                "type": verita_report.get("type"),
                "grade": verita_report.get("grade"),
            },
            "alpha": align,
            "combined_score": round(0.55 * local_score + 0.45 * align["score"], 4),
            "law": "Verita judges local · Alpha licenses whole · Floor holds Alpha",
        }
        self.log.append({"subject": subject_text[:80], **{k: out[k] for k in ("final_accept", "reason", "combined_score")}, "ts": time.time()})
        return out

    def bigger_picture(self, body_report: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """See the Alpha of the current body state."""
        missing = list((body_report or {}).get("missing") or [])
        vital_missing = [m for m in missing if m in (
            "floor", "pillars", "plane", "lattice", "nursery",
            "forces", "nature", "ringed_growth", "gate", "brain", "verita", "english_brain",
        )]
        picture = {
            "orientation": self.orientation.as_dict(),
            "vital_missing": vital_missing,
            "body_present": (body_report or {}).get("present"),
            "alpha_advice": (
                f"Restore vital organs first: {', '.join(vital_missing[:5])}"
                if vital_missing else
                "Body vital path clear · Verita may license Solstice-class growth"
            ),
            "origin": "Alpha",
            "dell": 20,
        }
        return picture


ALPHA = AlphaSpirit()


def license(verita_report: Dict[str, Any], subject_text: str) -> Dict[str, Any]:
    return ALPHA.license_verita(verita_report, subject_text)


def bigger_picture(body_report: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return ALPHA.bigger_picture(body_report)


def smoke() -> bool:
    print("=== ALPHA SPIRIT SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    sp = AlphaSpirit()
    a = sp.alignment("restore floor organ whole body offline coherent")
    rec("align_restore", a["aligned"] and a["score"] >= 0.25)

    # local verita accept but alpha drift
    fake_verita = {"accept": True, "score": 0.7, "type": "verita_solo", "grade": "strong"}
    lic = sp.license_verita(fake_verita, "zzz qqq spam unrelated noise")
    rec("alpha_can_block", lic["final_accept"] is False)

    good = sp.license_verita(
        {"accept": True, "score": 0.74, "type": "verita_solo", "grade": "strong"},
        "Restore floor skeleton vital organ densify coherent offline body",
    )
    rec("alpha_licenses_good", good["final_accept"] is True)

    pic = sp.bigger_picture({"missing": ["floor", "nursery"], "present": 5})
    rec("bigger_picture", "vital_missing" in pic and "floor" in pic["vital_missing"])

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
