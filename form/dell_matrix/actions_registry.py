#!/usr/bin/env python3
"""
Single action registry for snapshot visual, live visual, and help.

Modes (progressive disclosure):
  beginner — core acceptance path
  builder  — lattice + avatar + nursery power
  depth    — full system + workshops + polyglot hints
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# mode levels: beginner < builder < depth
_MODE_RANK = {"beginner": 0, "builder": 1, "depth": 2}

ACTIONS: List[Dict[str, Any]] = [
    {"group": "Start", "mode": "beginner", "items": [
        {"label": "Tutorial", "cmd": "tutorial", "hint": "Guided acceptance path"},
        {"label": "Help", "cmd": "help", "hint": "Top commands"},
        {"label": "Status", "cmd": "status", "hint": "Where you are · gen · pillars"},
        {"label": "Know self", "cmd": "self", "hint": "What the program is (self-model)"},
        {"label": "Live panel", "cmd": "live", "hint": "Two-way localhost visual (opt-in)"},
        {"label": "Mode beginner", "cmd": "mode beginner", "hint": "Simple menus"},
        {"label": "Mode builder", "cmd": "mode builder", "hint": "Full matrix tools"},
        {"label": "Mode depth", "cmd": "mode depth", "hint": "Workshops + lenses"},
    ]},
    {"group": "Ideas", "mode": "beginner", "items": [
        {"label": "Create strong idea", "cmd": "create an idea called Focus detail: what this is for goals: ship one loop; stay honest", "hint": "label + detail + goals"},
        {"label": "Create idea (name)", "cmd": "create an idea called ", "hint": "Add a name — then set detail/goals"},
        {"label": "Grow ideas", "cmd": "grow ideas 2", "hint": "Ringed growth → Nursery only"},
        {"label": "Show proposals", "cmd": "proposals", "hint": "View Nursery quarantine"},
        {"label": "Rank", "cmd": "rank", "hint": "Sort by affinity"},
        {"label": "What next", "cmd": "what next", "hint": "Live NBD — best next step"},
        {"label": "Ready?", "cmd": "ready", "hint": "Acceptance checklist"},
        {"label": "Undo", "cmd": "undo", "hint": "Undo last place/edit"},
        {"label": "History", "cmd": "history", "hint": "Recent program notes"},
        {"label": "Show matrix", "cmd": "show me", "hint": "Print live state"},
        {"label": "Look", "cmd": "look", "hint": "What you see from facing"},
        {"label": "Entities", "cmd": "entities", "hint": "List all entities on stage"},
    ]},
    {"group": "Nursery", "mode": "beginner", "items": [
        {"label": "Confirm idea", "cmd": "confirm ", "hint": "Paste proposal id after"},
        {"label": "Reject idea", "cmd": "reject ", "hint": "Paste proposal id after"},
        {"label": "Confirm all", "cmd": "confirm all", "hint": ""},
        {"label": "Reject all", "cmd": "reject all", "hint": ""},
        {"label": "Auto confirm grow ON", "cmd": "auto confirm all grow mode", "hint": "Grow then confirm all pending"},
        {"label": "Auto confirm grow OFF", "cmd": "auto confirm off", "hint": "Grow leaves proposals in nursery"},
        {"label": "Grow mode status", "cmd": "grow mode", "hint": "Show auto_confirm_grow"},
    ]},
    {"group": "Lattice", "mode": "builder", "items": [
        {"label": "Cube", "cmd": "cube", "hint": "Cubic shell metric"},
        {"label": "Sphere", "cmd": "sphere", "hint": "Radial metric"},
        {"label": "Core", "cmd": "core", "hint": "Seed shells"},
        {"label": "Flower", "cmd": "flower", "hint": "Flower of Life"},
        {"label": "FoL geometry", "cmd": "flower geometry", "hint": "Centers · vesicas · fruit"},
        {"label": "Verita edges", "cmd": "verita", "hint": "Vesica truth-of-meet"},
        {"label": "Voynich rings", "cmd": "voynich", "hint": "Structural 5-ring (not decrypt)"},
        {"label": "Fractal Rule90", "cmd": "fractal", "hint": "Sierpinski CA + orbit"},
        {"label": "Geometry", "cmd": "geometry", "hint": "Full sacred-geometry status"},
        {"label": "Toggle dual", "cmd": "toggle", "hint": "cube↔sphere etc."},
        {"label": "Lattice", "cmd": "lattice", "hint": "ASCII lattice status"},
        {"label": "Grid snap on", "cmd": "snap on", "hint": "Avatar snaps to grid when cube"},
        {"label": "Grid snap off", "cmd": "snap off", "hint": ""},
    ]},
    {"group": "Pages", "mode": "builder", "items": [
        {"label": "Idea page", "cmd": "page", "hint": "Open nearest idea end-page (or current zoom)"},
        {"label": "Unzoom", "cmd": "unzoom", "hint": "Leave idea page → overview"},
        {"label": "Recenter", "cmd": "recenter", "hint": "Camera back to user"},
        {"label": "Workshops page", "cmd": "workshops", "hint": "Full workbench index"},
        {"label": "Inspire page", "cmd": "inspire", "hint": "Offline pack status"},
    ]},
    {"group": "Avatar", "mode": "beginner", "items": [
        {"label": "Walk", "cmd": "walk forward", "hint": "W"},
        {"label": "Jog", "cmd": "jog", "hint": "J"},
        {"label": "Run", "cmd": "run", "hint": "Shift+W / R"},
        {"label": "Backstep", "cmd": "backstep", "hint": "S"},
        {"label": "Strafe left", "cmd": "strafe left", "hint": "Shift+A"},
        {"label": "Strafe right", "cmd": "strafe right", "hint": "Shift+D"},
        {"label": "Turn left", "cmd": "turn left", "hint": "A"},
        {"label": "Turn right", "cmd": "turn right", "hint": "D"},
        {"label": "Sit", "cmd": "sit down", "hint": ""},
        {"label": "Stand", "cmd": "stand up", "hint": ""},
        {"label": "Look", "cmd": "look", "hint": "Q · vision cone"},
        {"label": "Smile", "cmd": "smile", "hint": ""},
        {"label": "How do I look?", "cmd": "how do I look", "hint": ""},
    ]},
    {"group": "AI", "mode": "builder", "items": [
        {"label": "AI walk", "cmd": "ai walk", "hint": ""},
        {"label": "AI look", "cmd": "ai look", "hint": ""},
        {"label": "AI follow", "cmd": "ai follow", "hint": "E"},
        {"label": "AI wander", "cmd": "ai wander", "hint": ""},
        {"label": "AI manual", "cmd": "ai manual", "hint": ""},
        {"label": "AI status", "cmd": "ai status", "hint": ""},
    ]},
    {"group": "Workshops", "mode": "depth", "items": [
        {"label": "Matrix workshop", "cmd": "workshop matrix", "hint": "Forms · shells · zoom"},
        {"label": "Perspective workshop", "cmd": "workshop perspective", "hint": "Lenses · duals"},
        {"label": "Mandel workshop", "cmd": "workshop mandel", "hint": "Language · seeds"},
        {"label": "Persona workshop", "cmd": "workshop persona", "hint": "Agent directives"},
        {"label": "Forces workshop", "cmd": "workshop forces", "hint": "Nature forces"},
        {"label": "BIMO workshop", "cmd": "workshop bimo", "hint": "Fusion body"},
        {"label": "Psalms workshop", "cmd": "workshop psalms", "hint": "Ancient operators"},
        {"label": "Leave workshop", "cmd": "workshop leave", "hint": ""},
        {"label": "List workshops", "cmd": "workshops", "hint": ""},
    ]},
    {"group": "View rooms", "mode": "builder", "items": [
        {"label": "Rooms list", "cmd": "rooms", "hint": "All view rooms"},
        {"label": "View growth", "cmd": "view growth", "hint": "Plant stages"},
        {"label": "View water", "cmd": "view water", "hint": "Streams & pools"},
        {"label": "View force", "cmd": "view force", "hint": "Forces in voids"},
        {"label": "View network", "cmd": "view network", "hint": "Edges"},
        {"label": "View personal", "cmd": "view personal", "hint": "Your plantings"},
        {"label": "View shared", "cmd": "view shared", "hint": "Resonant ideas"},
        {"label": "View psalms", "cmd": "view ancient_psalms", "hint": "Ledger / reverse"},
    ]},
    {"group": "Forces", "mode": "builder", "items": [
        {"label": "Forces status", "cmd": "forces", "hint": "Nature force field"},
        {"label": "Force tick", "cmd": "force tick", "hint": "Pulse all active forces"},
        {"label": "Evolve program", "cmd": "evolve", "hint": "Gen++ · forces · pillars"},
        {"label": "Weather rain", "cmd": "weather rain", "hint": "New seeds atmosphere"},
        {"label": "Weather clear", "cmd": "weather clear", "hint": ""},
        {"label": "Weather storm", "cmd": "weather storm", "hint": "Shake stuck ideas"},
    ]},
    {"group": "Personas", "mode": "builder", "items": [
        {"label": "Full roster", "cmd": "personas", "hint": "All personas by category"},
        {"label": "Persona matrix", "cmd": "matrix personas", "hint": "Spatial agent map"},
        {"label": "Manny", "cmd": "persona manny", "hint": "PragLog · logic"},
        {"label": "Melody", "cmd": "persona melody", "hint": "EvoLog · growth"},
        {"label": "Aetheris", "cmd": "persona aetheris", "hint": "AutoLog · coherence"},
        {"label": "Mathelody", "cmd": "persona mathelody", "hint": "AgentLog · fusion"},
        {"label": "The Ancient", "cmd": "persona the_ancient", "hint": "Ancient Psalms"},
        {"label": "Translator", "cmd": "persona translator", "hint": "Lang bridge"},
        {"label": "Della", "cmd": "persona della", "hint": "DellLog · quality"},
        {"label": "Mansplainer", "cmd": "persona mansplainer", "hint": "Plain English"},
        {"label": "Dell", "cmd": "persona dell", "hint": "Executor"},
        {"label": "Oracle", "cmd": "persona oracle", "hint": "Pattern watch"},
        {"label": "Guide me", "cmd": "guide", "hint": "Active persona guidance"},
        {"label": "Persona clear", "cmd": "persona clear", "hint": ""},
    ]},
    {"group": "BIMO", "mode": "depth", "items": [
        {"label": "BIMO status", "cmd": "bimo", "hint": "Fusion body slots"},
        {"label": "Dock defaults", "cmd": "bimo defaults", "hint": "Fill all slots"},
        {"label": "Fuse", "cmd": "bimo fuse", "hint": "Multi-thread synthesis"},
        {"label": "Pilot Mathelody", "cmd": "bimo pilot mathelody", "hint": "Set fusion pilot"},
        {"label": "Clear BIMO", "cmd": "bimo clear", "hint": "Empty slots"},
        {"label": "BIMO workshop", "cmd": "workshop bimo", "hint": "Open workbench"},
    ]},
    {"group": "Lenses", "mode": "depth", "items": [
        {"label": "Lens clear", "cmd": "lens clear", "hint": "See all skins"},
        {"label": "Lens seed", "cmd": "lens seed", "hint": "Filter vision to seed"},
        {"label": "Lens flower", "cmd": "lens flower", "hint": "Filter vision to flower"},
    ]},
    {"group": "Code Evolution", "mode": "builder", "items": [
        {"label": "CE status", "cmd": "ce status", "hint": "Code Evolution root checklist"},
        {"label": "CE develop", "cmd": "ce develop", "hint": "Full matrix loop on Code Evolution root"},
        {"label": "CE develop + net", "cmd": "ce develop net", "hint": "Develop with internet research ON"},
        {"label": "Internet ON", "cmd": "internet on", "hint": "Opt-in network (default OFF)"},
        {"label": "Internet OFF", "cmd": "internet off", "hint": "Back to offline Origin"},
        {"label": "Internet status", "cmd": "internet", "hint": "Gate state + allowed hosts"},
        {"label": "CE research ternary", "cmd": "ce research ternary logic", "hint": "Wikipedia summary (needs internet on)"},
        {"label": "Page Code Evolution", "cmd": "page code_evolution", "hint": "Open root idea page"},
    ]},
    {"group": "Inspire", "mode": "builder", "items": [
        {"label": "Attend growth", "cmd": "attend growth seed", "hint": "Soft attention over ideas (offline)"},
        {"label": "Multi-look", "cmd": "multilook", "hint": "Near/mid/far vision memory"},
        {"label": "Score slopes", "cmd": "slopes", "hint": "Δscore/Δt calculus"},
        {"label": "Prefs", "cmd": "prefs", "hint": "Confirm/reject preference ledger"},
        {"label": "Glyph card", "cmd": "glyph", "hint": "Procedural art (no assets)"},
        {"label": "Script demo", "cmd": "script look; status; pulse", "hint": "Batch matrix script"},
        {"label": "Inspire status", "cmd": "inspire", "hint": "Pack summary"},
    ]},
    {"group": "System", "mode": "beginner", "items": [
        {"label": "Enhance ON", "cmd": "enhance on", "hint": ""},
        {"label": "Enhance OFF", "cmd": "enhance off", "hint": ""},
        {"label": "Pulse", "cmd": "pulse", "hint": ""},
        {"label": "Save", "cmd": "save", "hint": ""},
        {"label": "Status", "cmd": "status", "hint": ""},
        {"label": "Audit pillars", "cmd": "audit", "hint": "6-pillar health"},
        {"label": "Know self", "cmd": "self", "hint": "Program self-understanding report"},
        {"label": "Self map", "cmd": "self map", "hint": "Matrices · snaps · routes inventory"},
        {"label": "Close gaps", "cmd": "close gaps", "hint": "Warm cold capabilities"},
        {"label": "Self evolve", "cmd": "self evolve", "hint": "Know → close → evolve one gen"},
        {"label": "Evolve loop ×12", "cmd": "evolve loop 12", "hint": "12 understand+evolve cycles"},
        {"label": "Matrices", "cmd": "matrices", "hint": "All matrices inventory"},
        {"label": "English expand ×150", "cmd": "english expand 150", "hint": "Full 150-cycle English enhance"},
        {"label": "English expand ×50", "cmd": "english expand 50", "hint": "Shorter understanding growth"},
        {"label": "English status", "cmd": "english status", "hint": "Mastery & learned paraphrases"},
        {"label": "How to talk", "cmd": "english help", "hint": "Natural English examples"},
        {"label": "Visual snapshot", "cmd": "visual", "hint": "Offline HTML panel"},
    ]},
]


def normalize_mode(mode: Optional[str]) -> str:
    m = (mode or "builder").lower().strip()
    return m if m in _MODE_RANK else "builder"


def actions_for_mode(mode: str = "builder") -> List[Dict[str, Any]]:
    """Filter ACTIONS by progressive disclosure mode."""
    rank = _MODE_RANK[normalize_mode(mode)]
    out: List[Dict[str, Any]] = []
    for g in ACTIONS:
        g_rank = _MODE_RANK.get(g.get("mode", "beginner"), 0)
        if g_rank > rank:
            continue
        items = list(g.get("items") or [])
        if items:
            out.append({"group": g["group"], "mode": g.get("mode", "beginner"), "items": items})
    return out


def actions_flat(mode: str = "builder") -> List[Dict[str, str]]:
    flat: List[Dict[str, str]] = []
    for g in actions_for_mode(mode):
        for item in g["items"]:
            flat.append({
                "group": g["group"],
                "label": item["label"],
                "cmd": item["cmd"],
                "hint": item.get("hint") or "",
            })
    return flat


def help_lines(mode: str = "builder") -> str:
    lines = [f"Actions (mode={normalize_mode(mode)})"]
    for g in actions_for_mode(mode):
        lines.append(f"  [{g['group']}]")
        for item in g["items"]:
            hint = f"  — {item['hint']}" if item.get("hint") else ""
            lines.append(f"    {item['label']}: {item['cmd']}{hint}")
    return "\n".join(lines)


def smoke() -> bool:
    print("=== ACTIONS REGISTRY SMOKE ===")
    b = actions_for_mode("beginner")
    d = actions_for_mode("depth")
    ok = len(b) >= 4 and len(d) > len(b)
    print(f"[{'PASS' if ok else 'FAIL'}] mode filtering beginner={len(b)} depth={len(d)}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
