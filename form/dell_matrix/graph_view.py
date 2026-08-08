#!/usr/bin/env python3
"""GraphView — UI contract; optional scores in payload (NBD x10)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Perspective, Skin
    from form.dell_matrix.blank_cube import give
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Perspective, Skin
    from form.dell_matrix.blank_cube import give


@dataclass
class ViewNode:
    id: str
    label: str
    skin: str
    x: float
    y: float
    words: str
    sandboxed: bool
    sandbox_id: Optional[str]
    connected: bool
    score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "skin": self.skin,
            "x": self.x,
            "y": self.y,
            "words": self.words,
            "sandboxed": self.sandboxed,
            "sandbox_id": self.sandbox_id,
            "connected": self.connected,
            "score": self.score,
        }


@dataclass
class ViewEdge:
    source: str
    target: str
    kind: str

    def to_dict(self) -> Dict[str, Any]:
        return {"source": self.source, "target": self.target, "kind": self.kind}


@dataclass
class GraphView:
    perspective: str
    zoom: Optional[str]
    nodes: List[ViewNode] = field(default_factory=list)
    edges: List[ViewEdge] = field(default_factory=list)
    sandboxes: Dict[str, List[str]] = field(default_factory=dict)
    floor: List[str] = field(default_factory=lambda: list(FLOOR))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "DellMatrixGraphView",
            "version": 2,
            "floor": self.floor,
            "perspective": self.perspective,
            "zoom": self.zoom,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "sandboxes": self.sandboxes,
        }

    def ascii(self) -> str:
        lines = [
            f"+- GraphView · {self.perspective} zoom={self.zoom or 'overview'} -+",
            f"| Floor: {' · '.join(self.floor)}",
            "| NODES",
        ]
        for n in self.nodes:
            flag = "box" if n.sandboxed else "on"
            sc = f" sc={n.score:.2f}" if n.score else ""
            lines.append(f"|  ({n.x:.1f},{n.y:.1f}) [{n.skin}] {n.label} <{flag}>{sc}")
        lines.append("| EDGES")
        for e in self.edges:
            lines.append(f"|  {e.source} -{e.kind}-> {e.target}")
        if self.sandboxes:
            lines.append(f"| BOXES {self.sandboxes}")
        lines.append("+" + "-" * 48 + "+")
        return "\n".join(lines)


def build_view(plane: Plane, scores: Optional[Dict[str, float]] = None) -> GraphView:
    assert_floor_intact()
    scores = scores or {}
    nodes: List[ViewNode] = []
    edges: List[ViewEdge] = []
    for uid, u in plane.units.items():
        nodes.append(
            ViewNode(
                id=uid,
                label=u.label,
                skin=u.skin.value,
                x=u.x,
                y=u.y,
                words=u.words,
                sandboxed=u.sandboxed,
                sandbox_id=u.sandbox_id,
                connected=not u.sandboxed,
                score=float(scores.get(uid, 0.0)),
            )
        )
        for other in plane.enhance_scope(uid):
            edges.append(ViewEdge(source=uid, target=other, kind="enhance"))
        if u.sandboxed and u.sandbox_id:
            edges.append(ViewEdge(source=uid, target=u.sandbox_id, kind="sandbox"))

    # Verita / vesica edges from real proximity (not all-pairs spam)
    try:
        from form.dell_matrix.sacred_geometry import verita_between_nodes
        node_dicts = [n.to_dict() for n in nodes if n.connected]
        for ve in verita_between_nodes(node_dicts, max_dist=3.5, min_verita=0.2):
            edges.append(ViewEdge(
                source=str(ve["source"]),
                target=str(ve["target"]),
                kind="vesica",
            ))
            # stash verita on a side channel via kind suffix for consumers that care
            # (ViewEdge is simple; live visual re-computes strength from geometry)
    except Exception:
        connected_ids = [n.id for n in nodes if n.connected]
        for i, a in enumerate(connected_ids):
            for b in connected_ids[i + 1 :]:
                edges.append(ViewEdge(source=a, target=b, kind="vesica"))

    sandboxes = {sid: list(sb.member_ids) for sid, sb in plane.sandboxes.items()}
    return GraphView(
        perspective=plane.perspective.value,
        zoom=plane.zoom_target,
        nodes=nodes,
        edges=edges,
        sandboxes=sandboxes,
    )


def smoke() -> bool:
    print("=== GRAPH VIEW V2 SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    cube = give("G", clean=True)
    cube.place_idea("a", "A", words="one", skin=Skin.CUBE)
    cube.place_idea("b", "B", words="two", skin=Skin.SEED, x=1)
    v = build_view(cube.session.plane, scores={"a": 1.25})
    rec("type", v.to_dict()["type"] == "DellMatrixGraphView")
    rec("score on node", any(n.score == 1.25 for n in v.nodes))
    rec("version 2", v.to_dict()["version"] == 2)
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    cube = give("Demo", clean=True)
    cube.place_idea("x", "X", skin=Skin.CUBE)
    print(build_view(cube.session.plane).ascii())


if __name__ == "__main__":
    main()
