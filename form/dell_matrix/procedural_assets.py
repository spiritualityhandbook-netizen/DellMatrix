#!/usr/bin/env python3
"""
Procedural assets — zero external art pipeline.

From: "How I released a game that has no assets" (Zanzlanz)
  · Everything drawable is generated from rules + seeds
  · No PNG/sprite dependency for core matrix UI frames

  skin_glyph(label, skin)
  node_sprite(node) → ASCII/SVG-ish cell
  plane_sheet(nodes) → multi-cell frame
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import hashlib

_SKIN_CHARS = {
    "core": "◆",
    "edge": "◇",
    "vital": "●",
    "fog": "·",
    "growth": "※",
    "force": "⚡",
    "none": "□",
}

_SKIN_SVG_FILL = {
    "core": "#4af",
    "edge": "#8a8",
    "vital": "#f64",
    "fog": "#666",
    "growth": "#4f8",
    "force": "#ff4",
    "none": "#444",
}


def _seed(s: str) -> int:
    return int(hashlib.sha1(s.encode("utf-8")).hexdigest()[:8], 16)


def skin_glyph(label: str = "", skin: str = "none") -> str:
    skin = (skin or "none").lower()
    base = _SKIN_CHARS.get(skin, _SKIN_CHARS["none"])
    # slight variant from label hash
    h = _seed(label or skin)
    variants = {0: base, 1: base, 2: base + "·", 3: "·" + base}
    return variants[h % 4]


def node_sprite(node: Dict[str, Any]) -> Dict[str, Any]:
    label = str(node.get("label") or node.get("id") or "?")
    skin = str(node.get("skin") or "none")
    glyph = skin_glyph(label, skin)
    h = _seed(label + skin)
    return {
        "glyph": glyph,
        "label": label[:24],
        "skin": skin,
        "fill": _SKIN_SVG_FILL.get(skin, "#555"),
        "pattern": h % 7,
        "asset": "procedural",  # never external file
    }


def plane_sheet(nodes: List[Dict[str, Any]], *, cols: int = 8) -> Dict[str, Any]:
    sprites = [node_sprite(n) for n in nodes[:64]]
    rows = []
    line = []
    for i, s in enumerate(sprites):
        line.append(s["glyph"])
        if len(line) >= cols:
            rows.append(" ".join(line))
            line = []
    if line:
        rows.append(" ".join(line))
    ascii_frame = "\n".join(rows) if rows else "(empty plane)"
    return {
        "ok": True,
        "count": len(sprites),
        "ascii": ascii_frame,
        "sprites": sprites,
        "law": "zero external assets · all glyphs procedural",
        "source_idea": "game_with_no_assets",
    }


def smoke() -> bool:
    print("=== PROCEDURAL ASSETS SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)
    s = node_sprite({"label": "Lattice", "skin": "core"})
    rec("sprite", s["glyph"] and s["asset"] == "procedural")
    sheet = plane_sheet([
        {"label": "A", "skin": "core"},
        {"label": "B", "skin": "edge"},
        {"label": "C", "skin": "vital"},
    ])
    rec("sheet", sheet["ok"] and sheet["count"] == 3)
    print(sheet["ascii"])
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
