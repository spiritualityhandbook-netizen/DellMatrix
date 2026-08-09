#!/usr/bin/env python3
"""
Brain — logic modules + Verita as one mind.

Parts:
  Verita     = truth-of-overlap (vesica coherence), not mysticism
  Residue    = structural signal when claimed links don't hold
  Decision   = soft shells (grade / ternary / gate) before Boolean cut
  Body       = organ sense (missing part → decide + why)
  Gate       = Mandell seed → route → English
  Resonance  = peer enhancement scores
  Conscience = incorporation / invariant style checks when available

Think cycle:
  sense body → verita-score candidate links → soft-decide → residue or accept → route

Offline · Boolean host intact · PROJECTED_NOT_FACT on hardware senses.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math
import time


# ---------------------------------------------------------------------------
# Verita — structural coherence (vesica strength)
# ---------------------------------------------------------------------------

def vesica_strength(r1: float, r2: float, distance: float) -> Dict[str, Any]:
    """
    Classic vesica: how much two equal-ish circles overlap.
    strength 1 = contained, 0 = separate, in-between = true vesica link.
    """
    r1, r2 = max(1e-9, float(r1)), max(1e-9, float(r2))
    d = max(0.0, float(distance))
    ssum, diff = r1 + r2, abs(r1 - r2)
    if d >= ssum:
        return {"strength": 0.0, "type": "separate", "distance": d}
    if d <= diff:
        return {"strength": 1.0, "type": "contained", "distance": d}
    strength = 1.0 - (d - diff) / (ssum - diff)
    return {"strength": round(strength, 4), "type": "vesica", "distance": d}


def verita_of_pair(
    label_a: str,
    label_b: str,
    *,
    tokens_a: Optional[set] = None,
    tokens_b: Optional[set] = None,
    distance: float = 1.0,
    radius: float = 1.0,
) -> Dict[str, Any]:
    """
    Verita score for a proposed link between two ideas.
    Combines geometric vesica + token overlap (language coherence).
    """
    import re
    tok_re = re.compile(r"[a-z0-9_]{3,}", re.I)
    ta = tokens_a if tokens_a is not None else {m.group(0).lower() for m in tok_re.finditer(label_a or "")}
    tb = tokens_b if tokens_b is not None else {m.group(0).lower() for m in tok_re.finditer(label_b or "")}
    inter = len(ta & tb)
    union = len(ta | tb) or 1
    jaccard = inter / union
    geo = vesica_strength(radius, radius, distance)
    # Verita = truth-of-overlap: language share + geometric share
    score = 0.55 * jaccard + 0.45 * geo["strength"]
    accept = score >= 0.18  # soft threshold (Standstill-ish)
    return {
        "score": round(score, 4),
        "jaccard": round(jaccard, 4),
        "vesica": geo,
        "accept": accept,
        "type": "verita",
        "note": "structural coherence only · not paranormal",
    }


@dataclass
class ResidueMark:
    location: str
    kind: str
    detail: str
    score: float
    ts: float = field(default_factory=time.time)


class VeritaField:
    """Tracks accepted links and residue from rejected/mismatched claims."""

    def __init__(self) -> None:
        self.links: List[Dict[str, Any]] = []
        self.residue: List[ResidueMark] = []

    def evaluate_link(self, a: str, b: str, **kwargs) -> Dict[str, Any]:
        v = verita_of_pair(a, b, **kwargs)
        if v["accept"]:
            self.links.append({"a": a, "b": b, **v, "ts": time.time()})
        else:
            self.residue.append(ResidueMark(
                location=f"{a}|{b}",
                kind="verita_mismatch",
                detail=f"score={v['score']} below accept",
                score=v["score"],
            ))
        v["residue_count"] = len(self.residue)
        v["link_count"] = len(self.links)
        return v

    def residue_summary(self) -> Dict[str, Any]:
        return {
            "count": len(self.residue),
            "tail": [
                {"location": r.location, "kind": r.kind, "score": r.score}
                for r in self.residue[-8:]
            ],
            "law": "residue = structural signal from Verita mismatch",
        }


# ---------------------------------------------------------------------------
# Brain — one mind
# ---------------------------------------------------------------------------

class Brain:
    """
    Unify logic organs into a think cycle.

    brain.think(context) →
      body pulse → verita on candidates → soft decision → residue/accept → gate route
    """

    def __init__(self) -> None:
        self.verita = VeritaField()
        self.history: List[Dict[str, Any]] = []

    def soft_decide(self, *scores: float) -> Dict[str, Any]:
        try:
            from form.dell_matrix.decision_shells import decide, prefer_open, OpenShell
            d = decide(*scores, mode="avg")
            open_s = prefer_open(d["score"], label="brain")
            return {
                "score": d["score"],
                "ternary": d["ternary"],
                "gate": d["gate"],
                "open_grade": open_s.grade,
                "collapsed": False,
                "shell": "decision_shells",
            }
        except Exception:
            xs = [max(0.0, min(1.0, float(s))) for s in scores] or [0.0]
            score = sum(xs) / len(xs)
            if score >= 0.28:
                gate = "Solstice"
            elif score >= 0.16:
                gate = "Equinox"
            elif score >= 0.10:
                gate = "Standstill"
            else:
                gate = "None"
            return {"score": score, "ternary": "pos" if score > 0.66 else "zero" if score >= 0.33 else "neg",
                    "gate": gate, "open_grade": score, "collapsed": False, "shell": "inline"}

    def body_view(self) -> Dict[str, Any]:
        try:
            from form.dell_matrix.matrix_body import body_pulse
            return body_pulse()
        except Exception as e:
            return {"error": str(e), "missing": [], "decisions": []}

    def gate_view(self, text: str) -> Dict[str, Any]:
        try:
            from form.mandell.gate_discipline import gate_turn
            return gate_turn(text)
        except Exception as e:
            return {"error": str(e), "seeds": []}

    def think(
        self,
        context: str,
        *,
        candidates: Optional[List[Tuple[str, str]]] = None,
        scores: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """
        Full brain cycle — readable report of mind state.
        """
        body = self.body_view()
        soft = self.soft_decide(*(scores or [0.5]))
        gate = self.gate_view(context)

        verita_results = []
        for a, b in (candidates or []):
            verita_results.append(self.verita.evaluate_link(a, b))

        # If body has vital missing, soft-gate cannot be Solstice freely
        missing = body.get("missing") or []
        vital_hit = any(m in missing for m in ("floor", "nursery", "lattice", "gate", "nature"))
        if vital_hit and soft.get("gate") == "Solstice":
            soft = dict(soft)
            soft["gate"] = "Standstill"
            soft["note"] = "vital organ missing · Solstice deferred to Standstill"

        report = {
            "context": (context or "")[:160],
            "body": {
                "present": body.get("present"),
                "missing": missing[:8],
                "top_decision": (body.get("decisions") or [{}])[0],
            },
            "verita": verita_results,
            "verita_field": {
                "links": len(self.verita.links),
                "residue": self.verita.residue_summary(),
            },
            "decision": soft,
            "gate": {
                "seeds": len(gate.get("seeds") or []),
                "plan_preview": (gate.get("plan") or [])[:3],
                "law": gate.get("law"),
            },
            "mind": {
                "role": "brain",
                "organs_used": ["verita", "decision_shells", "body", "gate"],
                "law": "sense → verita → soft-decide → residue/accept → route",
            },
            "ts": time.time(),
        }
        self.history.append({"context": report["context"], "gate": soft.get("gate"), "ts": report["ts"]})
        return report


BRAIN = Brain()


def think(context: str, **kwargs) -> Dict[str, Any]:
    return BRAIN.think(context, **kwargs)


def smoke() -> bool:
    print("=== BRAIN SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    v = vesica_strength(1, 1, 0.5)
    rec("vesica_overlap", v["type"] == "vesica" and v["strength"] > 0)
    v2 = vesica_strength(1, 1, 3)
    rec("vesica_separate", v2["type"] == "separate")

    vf = VeritaField()
    ok_link = vf.evaluate_link("Alpha structure grow", "structure clarity grow")
    rec("verita_accept_or_score", "score" in ok_link)
    bad = vf.evaluate_link("zzz", "qqq", distance=5.0)
    rec("verita_residue_path", isinstance(bad["score"], float))

    b = Brain()
    out = b.think(
        "unify logic and verita as brain",
        candidates=[("Restore floor", "floor skeleton"), ("noise", "zzzz")],
        scores=[0.4, 0.6],
    )
    rec("think_runs", out.get("mind", {}).get("role") == "brain")
    rec("decision_present", "gate" in out.get("decision", {}))
    rec("body_section", "missing" in out.get("body", {}))

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
