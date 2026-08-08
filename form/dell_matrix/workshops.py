#!/usr/bin/env python3
"""
Workshop Rooms — form/ runtime (ported + expanded from src/snapins/workshops.js).

Matrix · Perspective · Mandel · Persona · BIMO · Psalms · Forces
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

WORKSHOPS: Dict[str, Dict[str, Any]] = {
    "matrix": {
        "id": "matrix",
        "name": "Matrix Workshop",
        "description": "Flower of Life / sphere mode, shells, grid snap",
        "can_edit": ["form", "shell-view", "sphere-mode", "flower-mode", "grid-snap"],
        "commands": [
            {"label": "Cube form", "cmd": "cube"},
            {"label": "Sphere form", "cmd": "sphere"},
            {"label": "Core form", "cmd": "core"},
            {"label": "Flower form", "cmd": "flower"},
            {"label": "Show lattice", "cmd": "lattice"},
            {"label": "Shell 0", "cmd": "shell 0"},
            {"label": "Shell 1", "cmd": "shell 1"},
            {"label": "Grid snap on", "cmd": "snap on"},
            {"label": "Grid snap off", "cmd": "snap off"},
            {"label": "Matrices list", "cmd": "matrices"},
        ],
    },
    "perspective": {
        "id": "perspective",
        "name": "Perspective Workshop",
        "description": "Duals, view rooms, page zoom, vision lenses",
        "can_edit": ["dual", "page", "lens", "persona", "view-room"],
        "commands": [
            {"label": "Toggle dual", "cmd": "toggle"},
            {"label": "Look", "cmd": "look"},
            {"label": "Unzoom page", "cmd": "unzoom"},
            {"label": "Lens clear", "cmd": "lens clear"},
            {"label": "Lens seed", "cmd": "lens seed"},
            {"label": "View growth", "cmd": "view growth"},
            {"label": "View water", "cmd": "view water"},
            {"label": "View network", "cmd": "view network"},
            {"label": "Rooms list", "cmd": "rooms"},
        ],
    },
    "mandel": {
        "id": "mandel",
        "name": "Mandel Workshop",
        "description": "Language bridge — explain, seeds, polyglot",
        "can_edit": ["commands", "syntax", "explain"],
        "commands": [
            {"label": "Explain create", "cmd": "explain create"},
            {"label": "Patterns", "cmd": "patterns"},
            {"label": "Phrases", "cmd": "phrases"},
            {"label": "Lang list", "cmd": "lang list"},
            {"label": "Help more", "cmd": "help more"},
        ],
    },
    "persona": {
        "id": "persona",
        "name": "Persona Workshop",
        "description": "Full roster + persona matrix — directives, abilities, lenses",
        "can_edit": ["directives", "abilities", "limits", "personality", "emoji", "role"],
        "commands": [
            {"label": "Full roster", "cmd": "personas"},
            {"label": "Persona matrix", "cmd": "matrix personas"},
            {"label": "Manny", "cmd": "persona manny"},
            {"label": "Melody", "cmd": "persona melody"},
            {"label": "Aetheris", "cmd": "persona aetheris"},
            {"label": "Mathelody", "cmd": "persona mathelody"},
            {"label": "The Ancient", "cmd": "persona the_ancient"},
            {"label": "Translator", "cmd": "persona translator"},
            {"label": "Della", "cmd": "persona della"},
            {"label": "Mansplainer", "cmd": "persona mansplainer"},
            {"label": "Dell", "cmd": "persona dell"},
            {"label": "Oracle", "cmd": "persona oracle"},
            {"label": "BIMO body", "cmd": "persona bimo"},
            {"label": "Persona clear", "cmd": "persona clear"},
            {"label": "Guide me", "cmd": "guide"},
        ],
    },
    "bimo": {
        "id": "bimo",
        "name": "BIMO Workshop",
        "description": "Fusion body — dock all personas into slots, fuse multi-thread guidance",
        "can_edit": ["slots", "fusion-rules", "docking", "pilot"],
        "commands": [
            {"label": "BIMO status", "cmd": "bimo"},
            {"label": "Dock defaults", "cmd": "bimo defaults"},
            {"label": "Fuse all", "cmd": "bimo fuse"},
            {"label": "Pilot Mathelody", "cmd": "bimo pilot mathelody"},
            {"label": "Persona matrix", "cmd": "matrix personas"},
            {"label": "Clear slots", "cmd": "bimo clear"},
            {"label": "AI follow", "cmd": "ai follow"},
            {"label": "Entities", "cmd": "entities"},
            {"label": "Look", "cmd": "look"},
        ],
    },
    "psalms": {
        "id": "psalms",
        "name": "Psalms Workshop",
        "description": "Ancient structural operators — ledger, reverse walk, tokens (not decipherment)",
        "can_edit": ["content", "theme", "archetype", "strength"],
        "commands": [
            {"label": "Ancient view", "cmd": "view ancient_psalms"},
            {"label": "Persona Ancient", "cmd": "persona the_ancient"},
            {"label": "Lattice", "cmd": "lattice"},
            {"label": "Entities", "cmd": "entities"},
        ],
    },
    "forces": {
        "id": "forces",
        "name": "Forces Workshop",
        "description": "Nature forces — water, growth, breath, gravity, time, weather",
        "can_edit": ["intensity", "active-set", "weather"],
        "commands": [
            {"label": "Forces status", "cmd": "forces"},
            {"label": "Force tick", "cmd": "force tick"},
            {"label": "Grow plants", "cmd": "force growth"},
            {"label": "Water flow", "cmd": "force water"},
            {"label": "Breath", "cmd": "force breath"},
            {"label": "Weather rain", "cmd": "weather rain"},
            {"label": "Weather clear", "cmd": "weather clear"},
            {"label": "Evolve program", "cmd": "evolve"},
        ],
    },
}


def list_workshops() -> List[Dict[str, Any]]:
    return [dict(w) for w in WORKSHOPS.values()]


def get_workshop(workshop_id: str) -> Optional[Dict[str, Any]]:
    key = (workshop_id or "").lower().strip()
    aliases = {"psalm": "psalms", "force": "forces", "personas": "persona"}
    key = aliases.get(key, key)
    return WORKSHOPS.get(key)


def smoke() -> bool:
    print("=== WORKSHOPS SMOKE ===")
    ok = len(list_workshops()) >= 7 and get_workshop("matrix") is not None and get_workshop("forces") is not None
    print(f"[{'PASS' if ok else 'FAIL'}] workshops={len(list_workshops())}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
