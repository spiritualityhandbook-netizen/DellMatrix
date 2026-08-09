#!/usr/bin/env python3
"""
Floor Spirit — whole spirit from all four pillars.

FLOOR = (Alpha, Delta, Omega, Omni)  — immutable, more foundational than matrix.

  Alpha  origin orientation · bigger picture why · begin
  Delta  change pressure · Δ_known + Δ_unknown · difference that grows
  Omega  cycle close · completion · terminal integrity · end that seals
  Omni   all-parts at once · no organ excluded · universal scope

Together they are one spirit. Verita judges local; Floor Spirit licenses the whole.
Nova is NOT Floor (cheat-only edge).

Structural only — not paranormal claim.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import re
import time

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
except Exception:
    FLOOR = ("Alpha", "Delta", "Omega", "Omni")

    def assert_floor_intact(candidates=None) -> bool:
        if list(FLOOR) != ["Alpha", "Delta", "Omega", "Omni"]:
            raise RuntimeError("Floor integrity failure")
        return True

_TOKEN = re.compile(r"[a-z0-9_]{3,}", re.I)

PILLAR_ROLES = {
    "Alpha": {
        "role": "origin_orientation",
        "dell": 20,
        "asks": "Toward what whole?",
        "keywords": {
            "origin", "alpha", "why", "whole", "orientation", "purpose",
            "begin", "floor", "coherent", "offline", "body", "one",
        },
    },
    "Delta": {
        "role": "change_pressure",
        "dell": 4,  # Change / transform pressure (orbit fuel)
        "asks": "What known gap and unknown fuel move us?",
        "keywords": {
            "delta", "change", "grow", "restore", "densify", "missing",
            "gap", "known", "unknown", "evolve", "pressure", "diff",
            "handicap", "heal", "fix",
        },
    },
    "Omega": {
        "role": "cycle_close",
        "dell": 99,
        "asks": "What completes and seals without false finish?",
        "keywords": {
            "omega", "complete", "seal", "close", "cycle", "terminal",
            "finish", "audit", "integrity", "lock", "done", "solstice",
            "confirm", "nursery",
        },
    },
    "Omni": {
        "role": "all_parts_scope",
        "dell": 73,  # mind-wide / all-organs scope (symbolic)
        "asks": "Are all organs included — none excluded?",
        "keywords": {
            "omni", "all", "every", "organ", "body", "universal",
            "together", "none", "excluded", "full", "entire", "system",
            "matrix", "spirit", "pillar",
        },
    },
}

DEFAULT_ORIENTATION = (
    "Floor Alpha Delta Omega Omni locked · "
    "one body coherent offline-capable intelligence · "
    "problem means missing organ · Verita judges local · "
    "Delta fuels restore and densify · Omega seals honest cycles · "
    "Omni refuses any excluded organ · Alpha holds the why"
)


def _tokens(text: str) -> Set[str]:
    return {m.group(0).lower() for m in _TOKEN.finditer(text or "")}


@dataclass
class PillarVoice:
    name: str
    role: str
    score: float
    grade: str
    aligned: bool
    shared: List[str] = field(default_factory=list)
    asks: str = ""


@dataclass
class FloorOrientation:
    statement: str = DEFAULT_ORIENTATION
    priorities: List[str] = field(default_factory=lambda: [
        "floor_intact",
        "alpha_why",
        "delta_restore_gaps",
        "omega_honest_close",
        "omni_no_organ_excluded",
        "offline_first",
        "local_verita",
        "goal_biased_growth",
    ])
    updated_ts: float = field(default_factory=time.time)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "statement": self.statement,
            "priorities": list(self.priorities),
            "floor": list(FLOOR),
            "updated_ts": self.updated_ts,
        }


class FloorSpirit:
    """Whole spirit: Alpha + Delta + Omega + Omni as one."""

    def __init__(self, orientation: Optional[FloorOrientation] = None):
        assert_floor_intact()
        self.orientation = orientation or FloorOrientation()
        self.log: List[Dict[str, Any]] = []

    def set_orientation(self, statement: str, priorities: Optional[List[str]] = None) -> Dict[str, Any]:
        self.orientation.statement = (statement or "").strip() or DEFAULT_ORIENTATION
        if priorities:
            self.orientation.priorities = list(priorities)
        self.orientation.updated_ts = time.time()
        return self.orientation.as_dict()

    def pillar_alignment(self, text: str) -> Dict[str, PillarVoice]:
        t = _tokens(text)
        out: Dict[str, PillarVoice] = {}
        for name, meta in PILLAR_ROLES.items():
            keys: Set[str] = set(meta["keywords"])
            inter = t & keys
            # base from keyword hits
            score = min(1.0, len(inter) / 3.0)
            # slight credit if orientation priorities appear
            for p in self.orientation.priorities:
                stem = p.split("_")[0]
                if stem in t or stem in text.lower():
                    if name.lower() in p or stem in {"floor", "body", "organ", "verita", "restore"}:
                        score = min(1.0, score + 0.08)
            # directional always mildly supports Delta + Alpha
            directional = {"restore", "grow", "heal", "densify", "unify", "whole"}
            if t & directional:
                if name in ("Alpha", "Delta"):
                    score = max(score, 0.34)
            score = round(score, 4)
            if score >= 0.45:
                grade, aligned = "aligned", True
            elif score >= 0.25:
                grade, aligned = "partial", True
            else:
                grade, aligned = "quiet", False
            out[name] = PillarVoice(
                name=name,
                role=meta["role"],
                score=score,
                grade=grade,
                aligned=aligned,
                shared=sorted(inter)[:8],
                asks=meta["asks"],
            )
        return out

    def whole_alignment(self, text: str) -> Dict[str, Any]:
        voices = self.pillar_alignment(text)
        scores = [v.score for v in voices.values()]
        avg = round(sum(scores) / max(1, len(scores)), 4)
        # Omni-weighted: if text claims "all" but body will check organs separately
        active = sum(1 for v in voices.values() if v.aligned)
        if avg >= 0.40 and active >= 2:
            grade, aligned = "aligned", True
        elif avg >= 0.25 or active >= 1:
            grade, aligned = "partial", True
        else:
            grade, aligned = "drift", False
        return {
            "score": avg,
            "grade": grade,
            "aligned": aligned,
            "active_pillars": active,
            "voices": {
                n: {
                    "role": v.role,
                    "score": v.score,
                    "grade": v.grade,
                    "aligned": v.aligned,
                    "asks": v.asks,
                    "shared": v.shared,
                }
                for n, v in voices.items()
            },
            "floor": list(FLOOR),
        }

    def license_verita(self, verita_report: Dict[str, Any], subject_text: str) -> Dict[str, Any]:
        """
        Verita listens to whole Floor spirit.
        Local reject stays reject.
        Local accept needs at least partial Floor alignment.
        """
        align = self.whole_alignment(subject_text)
        local_accept = bool(verita_report.get("accept"))
        local_score = float(verita_report.get("score") or 0.0)

        if not local_accept:
            final_accept = False
            reason = "verita_local_reject"
        elif not align["aligned"]:
            final_accept = False
            reason = "floor_drift · locally coherent but not serving Alpha·Delta·Omega·Omni"
        else:
            final_accept = True
            reason = "verita_ok · floor_aligned"

        out = {
            "final_accept": final_accept,
            "reason": reason,
            "verita": {
                "accept": local_accept,
                "score": local_score,
                "type": verita_report.get("type"),
                "grade": verita_report.get("grade"),
            },
            "floor_spirit": align,
            "combined_score": round(0.50 * local_score + 0.50 * align["score"], 4),
            "law": "Verita local · Floor Spirit licenses whole · Alpha Delta Omega Omni",
        }
        self.log.append({
            "subject": subject_text[:80],
            "final_accept": final_accept,
            "reason": reason,
            "combined_score": out["combined_score"],
            "ts": time.time(),
        })
        return out

    def bigger_picture(self, body_report: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """All four pillars speak on current body state."""
        body = body_report or {}
        missing = list(body.get("missing") or [])
        vital = {
            "floor", "pillars", "plane", "lattice", "nursery", "forces",
            "nature", "ringed_growth", "gate", "brain", "verita", "english_brain",
        }
        vital_missing = [m for m in missing if m in vital]

        alpha_msg = (
            "Hold the why: one coherent offline body — restore before invent."
            if vital_missing else
            "Alpha clear: orientation can support Solstice-class growth."
        )
        delta_msg = (
            f"Delta pressure on gaps: {', '.join(vital_missing[:5])}"
            if vital_missing else
            "Delta: known gaps small — fuel unknown carefully."
        )
        omega_msg = (
            "Omega: do not seal a cycle while vital organs missing."
            if vital_missing else
            "Omega: honest close allowed when audits pass."
        )
        omni_msg = (
            f"Omni: {len(missing)} organs still out of the circle — none may stay excluded forever."
            if missing else
            "Omni: full organ presence in this host view."
        )

        return {
            "floor": list(FLOOR),
            "origin": "FloorSpirit",
            "orientation": self.orientation.as_dict(),
            "vital_missing": vital_missing,
            "body_present": body.get("present"),
            "voices": {
                "Alpha": alpha_msg,
                "Delta": delta_msg,
                "Omega": omega_msg,
                "Omni": omni_msg,
            },
            "advice": alpha_msg if vital_missing else omni_msg,
            "law": "Whole spirit = Alpha + Delta + Omega + Omni",
        }

    def status(self) -> Dict[str, Any]:
        assert_floor_intact()
        return {
            "floor": list(FLOOR),
            "pillars": {n: {"role": m["role"], "dell": m["dell"], "asks": m["asks"]} for n, m in PILLAR_ROLES.items()},
            "orientation": self.orientation.as_dict(),
            "log_tail": self.log[-5:],
            "nova": "Cheat only · not Floor",
        }


FLOOR_SPIRIT = FloorSpirit()

# Compatibility: Alpha was the first face of the spirit
ALPHA = FLOOR_SPIRIT


def license(verita_report: Dict[str, Any], subject_text: str) -> Dict[str, Any]:
    return FLOOR_SPIRIT.license_verita(verita_report, subject_text)


def bigger_picture(body_report: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return FLOOR_SPIRIT.bigger_picture(body_report)


def smoke() -> bool:
    print("=== FLOOR SPIRIT SMOKE (Alpha·Delta·Omega·Omni) ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    rec("floor_tuple", list(FLOOR) == ["Alpha", "Delta", "Omega", "Omni"])
    sp = FloorSpirit()
    w = sp.whole_alignment("restore floor organ whole body offline coherent grow densify")
    rec("whole_partial_or_better", w["aligned"])
    rec("four_voices", set(w["voices"]) == {"Alpha", "Delta", "Omega", "Omni"})

    good = sp.license_verita(
        {"accept": True, "score": 0.74, "type": "verita_solo", "grade": "strong"},
        "Restore floor skeleton vital organ densify coherent offline body grow",
    )
    rec("licenses_restore", good["final_accept"] is True)

    bad = sp.license_verita(
        {"accept": True, "score": 0.7, "type": "verita_solo", "grade": "strong"},
        "zzz qqq spam noise",
    )
    rec("blocks_spam", bad["final_accept"] is False)

    pic = sp.bigger_picture({"missing": ["floor", "nursery", "lattice"], "present": 6})
    rec("four_advice", set(pic["voices"]) == {"Alpha", "Delta", "Omega", "Omni"})
    rec("vital_in_picture", "floor" in pic["vital_missing"])

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
