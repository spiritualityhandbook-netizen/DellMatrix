#!/usr/bin/env python3
"""
Brain — logic modules + Verita as one mind.

Uses:
  verita.verita_of_one  — integrity of a single idea
  verita.verita_of_pair — truth-of-overlap between two ideas
  decision_shells       — soft grade before Boolean
  matrix_body           — organ sense
  gate_discipline       — Mandell route
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import time

from form.dell_matrix.verita import (
    VeritaField,
    verita_of_one,
    verita_of_pair,
    vesica_strength,
)


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

    def judge_one(self, label: str, **kwargs) -> Dict[str, Any]:
        return self.verita.evaluate_one(label, **kwargs)

    def think(
        self,
        context: str,
        *,
        ideas: Optional[List[Dict[str, Any]]] = None,
        candidates: Optional[List[Tuple[str, str]]] = None,
        scores: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        body = self.body_view()
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
            pairs.append(self.verita.evaluate_link(a, b))

        missing = body.get("missing") or []
        vital_hit = any(m in missing for m in (
            "floor", "nursery", "lattice", "gate", "nature", "verita", "brain",
        ))
        if vital_hit and soft.get("gate") == "Solstice":
            soft = dict(soft)
            soft["gate"] = "Standstill"
            soft["note"] = "vital organ missing · Solstice deferred"

        weak_solos = [s for s in solos if not s.get("accept")]
        if weak_solos and soft.get("gate") == "Solstice":
            soft = dict(soft)
            soft["gate"] = "Equinox"
            soft["note"] = "weak solo ideas present · prefer densify over new rings"

        report = {
            "context": (context or "")[:160],
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
                "organs_used": ["verita_solo", "verita_pair", "decision_shells", "body", "gate"],
                "law": "sense → solo/pair verita → soft-decide → residue/accept → route",
            },
            "ts": time.time(),
        }
        self.history.append({"context": report["context"], "gate": soft.get("gate"), "ts": report["ts"]})
        return report


BRAIN = Brain()


def think(context: str, **kwargs) -> Dict[str, Any]:
    return BRAIN.think(context, **kwargs)


def smoke() -> bool:
    print("=== BRAIN SMOKE (solo+pair) ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    b = Brain()
    s = b.judge_one("Restore floor skeleton", words="vital densify", goals=["coherence"])
    rec("solo_judge", s.get("accept") is True)
    fog = b.judge_one("??")
    rec("solo_fog", fog.get("accept") is False)

    out = b.think(
        "body and verita as mind",
        ideas=[
            {"label": "Restore floor", "words": "skeleton vital", "goals": ["whole body"]},
            "??",
        ],
        candidates=[("Restore floor", "floor skeleton"), ("zzz", "qqq")],
        scores=[0.5, 0.4],
    )
    rec("think_solo_section", "solo_verita" in out and len(out["solo_verita"]) == 2)
    rec("think_pair_section", "pair_verita" in out)
    rec("mind_law", "solo/pair" in out["mind"]["law"])

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
