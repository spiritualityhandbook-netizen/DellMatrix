#!/usr/bin/env python3
"""
Brain — mind under Alpha spirit.

Hierarchy:
  Floor (Alpha·Delta·Omega·Omni)
    → Alpha spirit (bigger picture / orientation)
      → Brain think cycle
        → Verita (local judgment) listens to Alpha
        → Body organs · Gate · Decision shells
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import time

from form.dell_matrix.verita import VeritaField


class Brain:
    def __init__(self) -> None:
        self.verita = VeritaField()
        self.history: List[Dict[str, Any]] = []

    def soft_decide(self, *scores: float) -> Dict[str, Any]:
        try:
            from form.dell_matrix.decision_shells import decide, prefer_open
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
            tern = "pos" if score > 0.66 else "zero" if score >= 0.33 else "neg"
            return {
                "score": score, "ternary": tern, "gate": gate,
                "open_grade": score, "collapsed": False, "shell": "inline",
            }

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

    def alpha_view(self, body: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from form.dell_matrix.alpha_spirit import ALPHA
            return ALPHA.bigger_picture(body)
        except Exception as e:
            return {"error": str(e), "origin": "Alpha"}

    def judge_one(self, label: str, **kwargs) -> Dict[str, Any]:
        local = self.verita.evaluate_one(label, **kwargs)
        subject = f"{label} {kwargs.get('words', '')} {' '.join(kwargs.get('goals') or [])}"
        try:
            from form.dell_matrix.alpha_spirit import ALPHA
            licensed = ALPHA.license_verita(local, subject)
            local = dict(local)
            local["alpha_license"] = licensed
            local["final_accept"] = licensed["final_accept"]
        except Exception:
            local["final_accept"] = local.get("accept")
        return local

    def think(
        self,
        context: str,
        *,
        ideas: Optional[List[Dict[str, Any]]] = None,
        candidates: Optional[List[Tuple[str, str]]] = None,
        scores: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        body = self.body_view()
        alpha = self.alpha_view(body)
        soft = self.soft_decide(*(scores or [0.5]))
        gate = self.gate_view(context)

        solos = []
        for idea in (ideas or []):
            if isinstance(idea, str):
                solos.append(self.judge_one(idea))
            elif isinstance(idea, dict):
                solos.append(self.judge_one(
                    str(idea.get("label") or ""),
                    words=str(idea.get("words") or ""),
                    goals=list(idea.get("goals") or []),
                    detail=str(idea.get("detail") or ""),
                ))

        pairs = []
        try:
            from form.dell_matrix.alpha_spirit import ALPHA
        except Exception:
            ALPHA = None  # type: ignore
        for a, b in (candidates or []):
            local = self.verita.evaluate_link(a, b)
            if ALPHA is not None:
                lic = ALPHA.license_verita(local, f"{a} {b}")
                local = dict(local)
                local["alpha_license"] = lic
                local["final_accept"] = lic["final_accept"]
            else:
                local["final_accept"] = local.get("accept")
            pairs.append(local)

        missing = body.get("missing") or []
        vital_hit = any(m in missing for m in (
            "floor", "nursery", "lattice", "gate", "nature", "verita", "brain",
        ))
        if vital_hit and soft.get("gate") == "Solstice":
            soft = dict(soft)
            soft["gate"] = "Standstill"
            soft["note"] = "vital organ missing · Solstice deferred · Alpha advice restore first"

        weak_solos = [s for s in solos if not s.get("final_accept", s.get("accept"))]
        if weak_solos and soft.get("gate") == "Solstice":
            soft = dict(soft)
            soft["gate"] = "Equinox"
            soft["note"] = "weak or alpha-blocked ideas · densify before new rings"

        report = {
            "context": (context or "")[:160],
            "alpha": {
                "origin": alpha.get("origin", "Alpha"),
                "advice": alpha.get("alpha_advice"),
                "vital_missing": alpha.get("vital_missing"),
                "orientation": (alpha.get("orientation") or {}).get("statement", "")[:120],
            },
            "body": {
                "present": body.get("present"),
                "missing": missing[:10],
                "top_decision": (body.get("decisions") or [{}])[0],
            },
            "solo_verita": solos,
            "pair_verita": pairs,
            "verita_field": {
                "solos_ok": len(self.verita.solos),
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
                "listens_to": "Alpha spirit",
                "organs_used": ["alpha", "verita_solo", "verita_pair", "decision_shells", "body", "gate"],
                "law": "Floor→Alpha→sense→verita(local)→alpha license→soft-decide→route",
            },
            "ts": time.time(),
        }
        self.history.append({"context": report["context"], "gate": soft.get("gate"), "ts": report["ts"]})
        return report


BRAIN = Brain()


def think(context: str, **kwargs) -> Dict[str, Any]:
    return BRAIN.think(context, **kwargs)


def smoke() -> bool:
    print("=== BRAIN + ALPHA SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    b = Brain()
    s = b.judge_one("Restore floor skeleton", words="vital densify coherent offline", goals=["whole body"])
    rec("solo_licensed", "final_accept" in s)
    out = b.think(
        "alpha over verita",
        ideas=[{"label": "Restore floor", "words": "skeleton vital offline", "goals": ["whole"]}],
        candidates=[("Restore floor", "floor skeleton")],
        scores=[0.5],
    )
    rec("alpha_section", "alpha" in out and out["mind"].get("listens_to") == "Alpha spirit")
    rec("law_has_alpha", "Alpha" in out["mind"]["law"])
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
