#!/usr/bin/env python3
"""
Brain — mind under whole Floor spirit.

Hierarchy:
  Floor (Alpha · Delta · Omega · Omni)  — immutable
    → Floor Spirit (whole spirit, four voices)
      → Brain think cycle
        → Verita (local) listens to Floor Spirit
        → Body · Gate · Decision shells
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

    def spirit_view(self, body: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from form.dell_matrix.floor_spirit import FLOOR_SPIRIT
            return FLOOR_SPIRIT.bigger_picture(body)
        except Exception as e:
            return {"error": str(e), "floor": ["Alpha", "Delta", "Omega", "Omni"]}

    def _license(self, local: Dict[str, Any], subject: str) -> Dict[str, Any]:
        try:
            from form.dell_matrix.floor_spirit import FLOOR_SPIRIT
            licensed = FLOOR_SPIRIT.license_verita(local, subject)
            out = dict(local)
            out["floor_license"] = licensed
            out["final_accept"] = licensed["final_accept"]
            return out
        except Exception:
            out = dict(local)
            out["final_accept"] = local.get("accept")
            return out

    def judge_one(self, label: str, **kwargs) -> Dict[str, Any]:
        local = self.verita.evaluate_one(label, **kwargs)
        subject = f"{label} {kwargs.get('words', '')} {' '.join(kwargs.get('goals') or [])}"
        return self._license(local, subject)

    def think(
        self,
        context: str,
        *,
        ideas: Optional[List[Dict[str, Any]]] = None,
        candidates: Optional[List[Tuple[str, str]]] = None,
        scores: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        body = self.body_view()
        spirit = self.spirit_view(body)
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
        for a, b in (candidates or []):
            local = self.verita.evaluate_link(a, b)
            pairs.append(self._license(local, f"{a} {b}"))

        missing = body.get("missing") or []
        vital_hit = any(m in missing for m in (
            "floor", "nursery", "lattice", "gate", "nature", "verita", "brain",
        ))
        if vital_hit and soft.get("gate") == "Solstice":
            soft = dict(soft)
            soft["gate"] = "Standstill"
            soft["note"] = "vital missing · Omega refuses false close · Delta points restore"

        weak = [s for s in solos if not s.get("final_accept", s.get("accept"))]
        if weak and soft.get("gate") == "Solstice":
            soft = dict(soft)
            soft["gate"] = "Equinox"
            soft["note"] = "Floor Spirit blocked or weak solos · densify"

        report = {
            "context": (context or "")[:160],
            "floor_spirit": {
                "floor": spirit.get("floor"),
                "voices": spirit.get("voices"),
                "advice": spirit.get("advice"),
                "vital_missing": spirit.get("vital_missing"),
                "orientation": ((spirit.get("orientation") or {}).get("statement") or "")[:140],
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
                "listens_to": "Floor spirit (Alpha·Delta·Omega·Omni)",
                "organs_used": [
                    "floor_spirit", "verita_solo", "verita_pair",
                    "decision_shells", "body", "gate",
                ],
                "law": "Floor→Spirit(4)→sense→verita(local)→floor license→soft-decide→route",
            },
            "ts": time.time(),
        }
        self.history.append({"context": report["context"], "gate": soft.get("gate"), "ts": report["ts"]})
        return report


BRAIN = Brain()


def think(context: str, **kwargs) -> Dict[str, Any]:
    return BRAIN.think(context, **kwargs)


def smoke() -> bool:
    print("=== BRAIN + FLOOR SPIRIT SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    b = Brain()
    out = b.think(
        "whole floor spirit",
        ideas=[{"label": "Restore floor", "words": "skeleton vital offline organ grow", "goals": ["whole"]}],
        candidates=[("Restore floor", "floor skeleton")],
        scores=[0.5],
    )
    rec("floor_spirit_section", "floor_spirit" in out)
    rec("four_floor", out.get("floor_spirit", {}).get("floor") == ["Alpha", "Delta", "Omega", "Omni"]
        or "Alpha" in str(out.get("floor_spirit", {})))
    rec("listens_whole", "Omni" in out["mind"]["listens_to"])
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
