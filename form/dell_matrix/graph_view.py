#!/usr/bin/env python3
"""
GraphView — NBD (equation after OneProgramBoot).

09[Show] > 15[Map] >> 47[Embed] :: GraphView

Not a full GUI app. Working **UI contract**:
plane → view graph (nodes, edges, sandboxes, perspective, zoom)
so any front-end (or richer ASCII) can bind without rewriting matrix logic.

Run:
  python -m form.dell_matrix.graph_view --smoke
  python -m form.dell_matrix.graph_view --demo
"""

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
        }


@dataclass
class ViewEdge:
    """Resonance / enhance edge (who can affect whom on plane)."""

    source: str
    target: str
    kind: str  # enhance | sandbox | vesica

    def to_dict(self) -> Dict[str, Any]:
        return {"source": self.source, "target": self.target, "kind": self.kind}


@dataclass
class GraphView:
    """Bindable view model of Dell Matrix plane."""

    perspective: str
    zoom: Optional[str]
    nodes: List[ViewNode] = field(default_factory=list)
    edges: List[ViewEdge] = field(default_factory=list)
    sandboxes: Dict[str, List[str]] = field(default_factory=dict)
    floor: List[str] = field(default_factory=lambda: list(FLOOR))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "DellMatrixGraphView",
            "version": 1,
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
            lines.append(f"|  ({n.x:.1f},{n.y:.1f}) [{n.skin}] {n.label} <{flag}>")
        lines.append("| EDGES")
        for e in self.edges:
            lines.append(f"|  {e.source} -{e.kind}-> {e.target}")
        if self.sandboxes:
            lines.append(f"| BOXES {self.sandboxes}")
        lines.append("+" + "-" * 48 + "+")
        return "\n".join(lines)


def build_view(plane: Plane) -> GraphView:
    assert_floor_intact()
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
            )
        )
        for other in plane.enhance_scope(uid):
            edges.append(ViewEdge(source=uid, target=other, kind="enhance"))
        if u.sandboxed and u.sandbox_id:
            edges.append(ViewEdge(source=uid, target=u.sandbox_id, kind="sandbox"))

    # vesica pairs among connected (simple: each pair of connected units)
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
    print("=== GRAPH VIEW SMOKE ===")
    r: List[bool] = []

    def rec(name: str, ok: bool, detail: str = "") -> None:
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    cube = give("UITest")
    cube.place_idea("a", "A", words="one", skin=Skin.CUBE, x=0, y=0)
    cube.place_idea("b", "B", words="two", skin=Skin.SEED, x=1, y=0)
    cube.session.plane.box(["a"], "s1")
    v = build_view(cube.session.plane)
    rec("type", v.to_dict()["type"] == "DellMatrixGraphView")
    rec("nodes", len(v.nodes) >= 2)  # welcome + a + b
    rec("enhance edges", any(e.kind == "enhance" for e in v.edges))
    rec("sandbox edges", any(e.kind == "sandbox" for e in v.edges))
    rec("floor", v.floor == list(FLOOR))
    rec("ascii", "GraphView" in v.ascii())
    rec("json", "nodes" in json.dumps(v.to_dict()))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def demo() -> None:
    print("09[Show] > 15[Map] >> 47[Embed] :: GraphView")
    print("English: Plane → bindable view graph.\n")
    cube = give("Demo")
    cube.place_idea("biz", "Business", words="CRM", skin=Skin.BUILDING, x=1)
    cube.place_idea("music", "Music", words="Ep4", skin=Skin.SEED, x=-1)
    cube.place_idea("cube1", "HarmonicCube", skin=Skin.CUBE, y=1)
    cube.session.plane.box(["cube1"], "sandbox_A")
    cube.session.plane.set_perspective(Perspective.FLOWER)
    v = build_view(cube.session.plane)
    print(v.ascii())
    print(json.dumps(v.to_dict(), indent=2))


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()


if __name__ == "__main__":
    main()
