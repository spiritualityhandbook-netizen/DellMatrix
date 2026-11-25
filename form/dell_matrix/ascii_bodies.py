#!/usr/bin/env python3
"""
ASCII body pack — ported from src/visual/ascii_bodies.js into form/.
Agents as rotatable / walkable text figures.
"""

from __future__ import annotations

from typing import Dict, List

DIRS: Dict[str, List[str]] = {
    "N":  ["  o  ", " /|\\ ", " / \\ "],
    "NE": ["  o  ", " /|> ", " / \\ "],
    "E":  ["  o  ", "  |\\ ", " / \\ "],
    "SE": ["  o  ", "  |> ", " \\ \\ "],
    "S":  ["  o  ", " \\|/ ", " / \\ "],
    "SW": ["  o  ", " <|  ", " / / "],
    "W":  ["  o  ", " /|  ", " / \\ "],
    "NW": ["  o  ", " /|\\ ", " / \\ "],
}

BODIES: Dict[str, Dict] = {
    "stick": {"name": "Stick", "frames": DIRS},
    "block": {
        "name": "Block",
        "frames": {
            "N": ["  O  ", " [|] ", " / \\ "],
            "E": ["  O  ", "  |] ", " / \\ "],
            "S": ["  O  ", " [|] ", " / \\ "],
            "W": ["  O  ", " [|  ", " / \\ "],
        },
    },
    "shadow": {
        "name": "Shadow",
        "frames": {
            "N": ["  °  ", " /|\\ ", " / \\ "],
            "E": ["  °  ", "  |\\ ", " / \\ "],
            "S": ["  °  ", " \\|/ ", " / \\ "],
            "W": ["  °  ", " /|  ", " / \\ "],
        },
    },
    "robot": {
        "name": "Robot",
        "frames": {
            "N": [" [==] ", " |00| ", " /||\\ "],
            "E": [" [==] ", " |00| ", "  ||\\ "],
            "S": [" [==] ", " |00| ", " /||\\ "],
            "W": [" [==] ", " |00| ", " /||  "],
        },
    },
}


def render_body(body_type: str = "stick", facing: str = "N") -> str:
    body = BODIES.get(body_type) or BODIES["stick"]
    frames = body["frames"]
    face = str(facing or "N").upper()
    frame = frames.get(face) or frames.get("N") or DIRS["N"]
    # fallback diagonals for bodies without 8-way
    if face not in frames:
        if face in ("NE", "SE") and "E" in frames:
            frame = frames["E"]
        elif face in ("NW", "SW") and "W" in frames:
            frame = frames["W"]
    return "\n".join(frame)


def list_bodies() -> List[str]:
    return list(BODIES.keys())


def smoke() -> bool:
    print("=== ASCII BODIES SMOKE ===")
    art = render_body("stick", "N")
    ok = "o" in art and len(list_bodies()) == 4
    print(f"[{'PASS' if ok else 'FAIL'}] stick N")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
