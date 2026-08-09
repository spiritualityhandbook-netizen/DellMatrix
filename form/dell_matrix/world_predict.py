#!/usr/bin/env python3
"""
World predict — infer what is not yet in view.

From: DeepMind-style "AI sees the world" / predictive world models
  · Current sight is partial
  · Predict likely unseen nodes from structure, skins, residue, delta
  · Label all predictions PROJECTED_NOT_FACT

  predict_unseen(program, sight)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
import math


def _seen_ids(sight: Dict[str, Any]) -> Set[str]:
    ids: Set[str] = set()
    nodes = sight.get("nodes") or []
    if not nodes and isinstance(sight.get("vision"), dict):
        nodes = (sight["vision"] or {}).get("nodes") or []
    for n in nodes:
        ids.add(str(n.get("id") or n.get("label") or ""))
    return {i for i in ids if i}


def _all_nodes(program) -> List[Dict[str, Any]]:
    try:
        from form.dell_matrix.perspective_views import _nodes_from_program
        return _nodes_from_program(program)
    except Exception:
        return []


def predict_unseen(program, sight: Optional[Dict[str, Any]] = None, *, limit: int = 12) -> Dict[str, Any]:
    """
    Given partial sight, list plane nodes not in view + soft reasons.
    Never claims fact — honesty tag always on.
    """
    if sight is None:
        try:
            from form.dell_matrix.free_matrix import see
            sight = see(program, "user", "first")
        except Exception:
            sight = {}

    seen = _seen_ids(sight)
    all_n = _all_nodes(program)
    predicted = []
    for n in all_n:
        nid = str(n.get("id") or n.get("label") or "")
        if not nid or nid in seen:
            continue
        skin = str(n.get("skin") or "")
        reason = "outside_current_cone"
        if skin in ("vital", "core"):
            reason = "high_priority_structure_not_in_view"
        predicted.append({
            "id": nid,
            "label": n.get("label"),
            "skin": skin,
            "x": n.get("x"),
            "y": n.get("y"),
            "reason": reason,
            "honesty": "PROJECTED_NOT_FACT",
        })
        if len(predicted) >= limit:
            break

    # delta-driven hypothetical gaps
    hypothetical = []
    try:
        from form.dell_matrix.matrix_body import body_pulse
        from form.dell_matrix.delta_pressure import from_body
        body = body_pulse()
        delta = from_body(body)
        for gap in (body.get("missing") or [])[:5]:
            hypothetical.append({
                "label": f"missing_organ:{gap}",
                "reason": "delta_vital_gap",
                "top_action": (delta.get("top_action") or {}).get("action"),
                "honesty": "PROJECTED_NOT_FACT",
            })
    except Exception:
        pass

    return {
        "ok": True,
        "seen_count": len(seen),
        "predicted_unseen": predicted,
        "hypothetical_gaps": hypothetical,
        "count": len(predicted),
        "law": "predict beyond view · never claim as observed fact",
        "source_idea": "deepmind_world_model_sees",
        "honesty": "PROJECTED_NOT_FACT",
    }


def smoke() -> bool:
    print("=== WORLD PREDICT SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    class FakePlane:
        def all_nodes(self):
            return [
                {"id": "a", "label": "Seen", "x": 1, "y": 0, "skin": "core"},
                {"id": "b", "label": "Hidden", "x": 9, "y": 9, "skin": "vital"},
            ]

    class P:
        plane = FakePlane()

    sight = {"nodes": [{"id": "a", "label": "Seen"}]}
    out = predict_unseen(P(), sight)
    rec("ok", out.get("ok") is True)
    rec("finds_hidden", any(p.get("id") == "b" for p in out.get("predicted_unseen") or []))
    rec("honesty", out.get("honesty") == "PROJECTED_NOT_FACT")
    print(out.get("predicted_unseen"))
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
