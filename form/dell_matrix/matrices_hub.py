#!/usr/bin/env python3
"""
Matrices Hub — inventory of all useful matrices living in form/.

Bridges LEGACY src/ concepts into one discoverable registry.
Grow/evolve the program by ticking forces, duo, and pillars together.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# Every matrix surface available in form/ runtime
MATRICES: List[Dict[str, Any]] = [
    {"id": "plane", "name": "Idea Plane", "kind": "core", "module": "form.dell_matrix.plane",
     "desc": "Ideas with skins, detail, goals, zoom pages"},
    {"id": "lattice", "name": "Harmonic Lattice", "kind": "core", "module": "form.dell_matrix.harmonic_lattice",
     "desc": "Cube/sphere/core/flower perceptions on one lattice"},
    {"id": "sacred_geometry", "name": "Sacred Geometry", "kind": "matrix", "module": "form.dell_matrix.sacred_geometry",
     "desc": "Flower of Life · Vesica/Verita · Voynich rings · Fractals"},
    {"id": "flower_of_life", "name": "Flower of Life", "kind": "matrix", "module": "form.dell_matrix.sacred_geometry",
     "desc": "Equal circles · Seed/FoL/Fruit · vesica pairs"},
    {"id": "verita", "name": "Vesica / Verita", "kind": "matrix", "module": "form.dell_matrix.sacred_geometry",
     "desc": "Truth-of-meet strength between ideas and FoL centers"},
    {"id": "voynich_rings", "name": "Voynich Rings", "kind": "growth", "module": "form.dell_matrix.sacred_geometry",
     "desc": "Seed→Token→Body→Lens→Evolve · organizational only"},
    {"id": "fractals", "name": "Fractals", "kind": "matrix", "module": "form.dell_matrix.sacred_geometry",
     "desc": "Rule 90 · bounded orbit · complex z²+c · Sierpinski"},
    {"id": "main_field", "name": "Main Field", "kind": "core", "module": "form.dell_matrix.main_field",
     "desc": "Shared third field — merge without clobber"},
    {"id": "resonance", "name": "Resonance", "kind": "core", "module": "form.dell_matrix.resonance",
     "desc": "Pulse scores between ideas"},
    {"id": "nursery", "name": "Nursery", "kind": "growth", "module": "form.dell_matrix.nursery",
     "desc": "Quarantine — confirm before live"},
    {"id": "ringed_growth", "name": "Ringed Growth", "kind": "growth", "module": "form.dell_matrix.ringed_growth",
     "desc": "Controlled growth engine → nursery only"},
    {"id": "forces", "name": "Nature Forces", "kind": "matrix", "module": "form.dell_matrix.forces",
     "desc": "Water · Growth · Breath · Gravity · Time · Weather · Space"},
    {"id": "personas", "name": "Personas Pack", "kind": "agents", "module": "form.dell_matrix.personas",
     "desc": "Full roster · 11 agents · categories · vision lenses"},
    {"id": "persona_matrix", "name": "Persona Matrix", "kind": "matrix", "module": "form.dell_matrix.personas",
     "desc": "Spatial map of all personas by category axes"},
    {"id": "bimo", "name": "BIMO Fusion Body", "kind": "agents", "module": "form.dell_matrix.personas",
     "desc": "Multi-slot dock · fuse · pilot Mathelody"},
    {"id": "view_rooms", "name": "View Rooms", "kind": "lens", "module": "form.dell_matrix.view_rooms",
     "desc": "Growth · Water · Force · Network · Personal · Shared · Ancient Psalms"},
    {"id": "workshops", "name": "Workshops", "kind": "workbench", "module": "form.dell_matrix.workshops",
     "desc": "Matrix · Perspective · Mandel · Persona · BIMO · Psalms · Forces"},
    {"id": "pillars", "name": "6-Pillar Audit", "kind": "audit", "module": "form.dell_matrix.pillars",
     "desc": "Standing · Spect · Tonea · Spirea · ManDetail · Omegate"},
    {"id": "vision", "name": "Directional Vision", "kind": "perception", "module": "form.dell_matrix.vision",
     "desc": "Cone look · persona/skin lenses"},
    {"id": "companion", "name": "AI Companion", "kind": "entity", "module": "form.dell_matrix.companion",
     "desc": "First-class AI agent on the map"},
    {"id": "avatar", "name": "Avatar Body", "kind": "entity", "module": "form.avatar.body",
     "desc": "Body FSM · walk · run · strafe · facing"},
    {"id": "graph", "name": "Graph View", "kind": "visual", "module": "form.dell_matrix.graph_view",
     "desc": "Nodes + enhance/vesica/sandbox edges"},
    {"id": "visual", "name": "Snapshot Visual", "kind": "visual", "module": "form.dell_matrix.visual",
     "desc": "Offline HTML matrix panel"},
    {"id": "live", "name": "Live Visual", "kind": "visual", "module": "form.dell_matrix.live_visual",
     "desc": "Two-way localhost visual bridge"},
    {"id": "ascii_bodies", "name": "ASCII Bodies", "kind": "visual", "module": "form.dell_matrix.ascii_bodies",
     "desc": "Stick/block/shadow/robot figures by facing"},
    {"id": "duobeta", "name": "DuoBeta Growth", "kind": "growth", "module": "form.duobeta.growth",
     "desc": "Generation ledger · 5 structural rings"},
    {"id": "mandell", "name": "Mandell Origin", "kind": "language", "module": "form.mandell",
     "desc": "Floor · seeds · polyglot · phrases"},
    {"id": "blank_cube", "name": "Blank Cube", "kind": "core", "module": "form.dell_matrix.blank_cube",
     "desc": "Clean session gift with welcome unit"},
    {"id": "gates", "name": "Control Gates", "kind": "safety", "module": "form.dell_matrix.enhance_gate",
     "desc": "Enhance · Sandbox · Ambient — default OFF"},
    {"id": "inspire", "name": "Inspire Pack", "kind": "workbench", "module": "form.dell_matrix.inspire_pack",
     "desc": "Attend · multilook · slopes · prefs · glyph · script (offline)"},
    {"id": "english_brain", "name": "English Brain", "kind": "language", "module": "form.mandell.english_brain",
     "desc": "Natural English normalize · 150-loop mastery"},
    {"id": "self_model", "name": "Self Model", "kind": "audit", "module": "form.dell_matrix.self_model",
     "desc": "Program self-understanding · capability mastery · evolve ledger"},
    {"id": "first_person", "name": "First Person Walk", "kind": "perception", "module": "form.dell_matrix.first_person",
     "desc": "Cube-to-cube centerpoint walk · Mandell steps"},
]


def list_matrices(kind: Optional[str] = None) -> List[Dict[str, Any]]:
    if not kind:
        return [dict(m) for m in MATRICES]
    k = kind.lower().strip()
    return [dict(m) for m in MATRICES if m.get("kind") == k or m.get("id") == k]


def matrix_summary() -> str:
    by: Dict[str, int] = {}
    for m in MATRICES:
        by[m["kind"]] = by.get(m["kind"], 0) + 1
    parts = [f"{k}={n}" for k, n in sorted(by.items())]
    return f"{len(MATRICES)} matrices · " + " · ".join(parts)


def evolve_program(program, detail: str = "evolve") -> Dict[str, Any]:
    """
    Grow the program one generation:
    - DuoBeta generation++
    - Force field tick
    - Pillar re-audit
    - Optional ring note
    """
    out: Dict[str, Any] = {"ok": True, "detail": detail}
    if hasattr(program, "duo"):
        out["duo"] = program.duo.evolve(detail)
    if hasattr(program, "forces"):
        nodes = program.nodes_payload() if hasattr(program, "nodes_payload") else []
        out["forces"] = program.forces.tick(nodes, owner=getattr(program, "owner", "Operator"))
    if hasattr(program, "note_seed"):
        program.note_seed(13, "Loop", "evolve")
    try:
        from form.dell_matrix.pillars import audit_program
        out["pillars"] = audit_program(program)
    except Exception as e:
        out["pillars_error"] = str(e)
    out["generation"] = getattr(getattr(program, "duo", None), "generation", 0)
    return out


def smoke() -> bool:
    print("=== MATRICES HUB SMOKE ===")
    ok = len(MATRICES) >= 18 and "forces" in {m["id"] for m in MATRICES}
    print(f"[{'PASS' if ok else 'FAIL'}] {matrix_summary()}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
