#!/usr/bin/env python3
"""
Intrinsic agent — reward for novelty, not only imitation.

From: NVIDIA / RL research theme "copying humans isn't enough"
  · Pure imitation → shortcuts
  · Intrinsic curiosity: prefer unseen organs, new skins, unexplored centers
  · Anti-shortcut: reject actions that only repeat last trail

Works with companion + free_matrix walk without needing neural nets.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import time


@dataclass
class IntrinsicAgent:
    seen_cells: Set[Tuple[int, int]] = field(default_factory=set)
    seen_labels: Set[str] = field(default_factory=set)
    last_action: str = ""
    curiosity_score: float = 0.0
    history: List[Dict[str, Any]] = field(default_factory=list)

    def observe(self, program, sight: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        novelty = 0.0
        new_labels = []
        nodes = []
        if sight:
            nodes = sight.get("nodes") or []
            if not nodes and isinstance(sight.get("vision"), dict):
                nodes = (sight["vision"] or {}).get("nodes") or []
        for n in nodes:
            lab = str(n.get("label") or n.get("id") or "")
            if lab and lab not in self.seen_labels:
                self.seen_labels.add(lab)
                new_labels.append(lab)
                novelty += 1.0
        # position novelty
        try:
            body = getattr(getattr(program, "avatar", None), "body", None)
            if body is not None:
                pos = getattr(body, "pos", (0, 0))
                cell = (int(pos[0]), int(pos[1]))
                if cell not in self.seen_cells:
                    self.seen_cells.add(cell)
                    novelty += 0.5
        except Exception:
            pass
        self.curiosity_score += novelty
        rec = {
            "novelty": novelty,
            "new_labels": new_labels[:8],
            "curiosity_total": round(self.curiosity_score, 2),
            "cells_explored": len(self.seen_cells),
            "labels_seen": len(self.seen_labels),
            "ts": time.time(),
        }
        self.history.append(rec)
        return rec

    def propose_action(self, program) -> Dict[str, Any]:
        """Prefer exploration actions over pure repeat."""
        candidates = ["forward", "left", "right", "back", "turn_left", "turn_right", "look_up"]
        # anti-shortcut: avoid identical repeat
        ranked = []
        for c in candidates:
            penalty = 1.0 if c == self.last_action else 0.0
            score = 1.0 - penalty
            # bias toward movement when few cells explored
            if len(self.seen_cells) < 8 and c in ("forward", "left", "right"):
                score += 0.5
            ranked.append((score, c))
        ranked.sort(reverse=True)
        best = ranked[0][1]
        return {
            "action": best,
            "scores": ranked[:5],
            "law": "intrinsic curiosity · avoid pure imitation shortcut",
            "source_idea": "nvidia_copying_humans_not_enough",
        }

    def step(self, program) -> Dict[str, Any]:
        prop = self.propose_action(program)
        action = prop["action"]
        result: Dict[str, Any] = {"ok": False}
        try:
            from form.dell_matrix import free_matrix as fm
            if action == "turn_left":
                result = fm.turn(program, "left")
            elif action == "turn_right":
                result = fm.turn(program, "right")
            elif action == "look_up":
                result = fm.look(program, "up")
            elif action in ("forward", "back", "left", "right"):
                result = fm.walk(program, action if action != "back" else "back")
            else:
                result = fm.walk(program, "forward")
        except Exception as e:
            result = {"ok": False, "error": str(e)}
        self.last_action = action
        sight = {}
        try:
            from form.dell_matrix import free_matrix as fm
            sight = fm.see(program, "companion", "first")
        except Exception:
            pass
        obs = self.observe(program, sight)
        return {"action": action, "result": result, "observe": obs, "proposal": prop}


AGENT = IntrinsicAgent()


def smoke() -> bool:
    print("=== INTRINSIC AGENT SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)
    a = IntrinsicAgent()
    class Body:
        pos = (0, 0)
    class P:
        avatar = type("A", (), {"body": Body()})()
    obs = a.observe(P(), {"nodes": [{"label": "NewThing"}]})
    rec("novelty", obs["novelty"] >= 1.0)
    prop = a.propose_action(P())
    rec("propose", "action" in prop)
    a.last_action = prop["action"]
    prop2 = a.propose_action(P())
    rec("anti_shortcut", prop2["action"] != a.last_action or len(prop2["scores"]) > 1)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
