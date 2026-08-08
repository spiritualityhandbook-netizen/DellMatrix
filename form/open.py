#!/usr/bin/env python3
"""One program — Form front door with Avatar + Ringed Growth Nursery + HarmonicLattice."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact, floor_status
    from form.mandell.manifest import manifest_from_dell
    from form.mandell.harmonic_truths import status as truths_status
    from form.dell_matrix.core import DellMatrix
    from form.dell_matrix.snap import SnapCandidate
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.main_field import MainField
    from form.dell_matrix.blank_cube import give, BlankCube
    from form.dell_matrix.enhance_gate import EnhanceGate
    from form.dell_matrix.ambient_gate import AmbientGate
    from form.dell_matrix.sandbox_gate import SandboxGate
    from form.dell_matrix.nursery import Nursery
    from form.dell_matrix.ringed_growth import RingedGrowth
    from form.dell_matrix.harmonic_lattice import HarmonicLattice
    from form.dell_matrix.harmonic_core import (
        KeyLedger, normalize_size, pulse_status, apply_radial_soft_forget,
        SIZE_CHROMATIC, SIZE_HARMONIC,
    )
    from form.dell_matrix.perception import Form
    from form.dell_matrix.companion import AICompanion
    from form.dell_matrix.vision import compute_vision, format_look_report
    from form.dell_matrix.actions_registry import normalize_mode, actions_for_mode
    from form.dell_matrix.workshops import list_workshops, get_workshop
    from form.dell_matrix.forces import ForceField
    from form.dell_matrix.personas import (
        get_persona, list_personas, persona_guidance, normalize_persona_id,
        BIMOBody, PersonaMatrix, render_roster, list_categories, PERSONAS,
    )
    from form.dell_matrix.view_rooms import get_room, list_rooms, filter_nodes_for_room, render_room_ascii
    from form.dell_matrix.pillars import audit_program, format_audit
    from form.dell_matrix.matrices_hub import list_matrices, matrix_summary, evolve_program
    from form.dell_matrix.ascii_bodies import render_body, list_bodies
    from form.dell_matrix.inspire_pack import (
        InspireState, attention_rank, procedural_glyph, procedural_idea_card,
        run_matrix_script, route_cost,
    )
    from form.dell_matrix.self_model import (
        SelfKnowledge, know_self, reflect_lines, evolve_with_understanding,
        close_gaps, inventory as self_inventory,
    )
    from form.duobeta.growth import DuoBeta
    from form.avatar import Avatar, FaceController, Expression, build_default_registry
except ImportError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact, floor_status
    from form.mandell.manifest import manifest_from_dell
    from form.mandell.harmonic_truths import status as truths_status
    from form.dell_matrix.core import DellMatrix
    from form.dell_matrix.snap import SnapCandidate
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.main_field import MainField
    from form.dell_matrix.blank_cube import give, BlankCube
    from form.dell_matrix.enhance_gate import EnhanceGate
    from form.dell_matrix.ambient_gate import AmbientGate
    from form.dell_matrix.sandbox_gate import SandboxGate
    from form.dell_matrix.nursery import Nursery
    from form.dell_matrix.ringed_growth import RingedGrowth
    from form.dell_matrix.harmonic_lattice import HarmonicLattice
    from form.dell_matrix.harmonic_core import (
        KeyLedger, normalize_size, pulse_status, apply_radial_soft_forget,
        SIZE_CHROMATIC, SIZE_HARMONIC,
    )
    from form.dell_matrix.perception import Form
    from form.dell_matrix.companion import AICompanion
    from form.dell_matrix.vision import compute_vision, format_look_report
    from form.dell_matrix.actions_registry import normalize_mode, actions_for_mode
    from form.dell_matrix.workshops import list_workshops, get_workshop
    from form.dell_matrix.forces import ForceField
    from form.dell_matrix.personas import (
        get_persona, list_personas, persona_guidance, normalize_persona_id,
        BIMOBody, PersonaMatrix, render_roster, list_categories, PERSONAS,
    )
    from form.dell_matrix.view_rooms import get_room, list_rooms, filter_nodes_for_room, render_room_ascii
    from form.dell_matrix.pillars import audit_program, format_audit
    from form.dell_matrix.matrices_hub import list_matrices, matrix_summary, evolve_program
    from form.dell_matrix.ascii_bodies import render_body, list_bodies
    from form.dell_matrix.inspire_pack import (
        InspireState, attention_rank, procedural_glyph, procedural_idea_card,
        run_matrix_script, route_cost,
    )
    from form.dell_matrix.self_model import (
        SelfKnowledge, know_self, reflect_lines, evolve_with_understanding,
        close_gaps, inventory as self_inventory,
    )
    from form.duobeta.growth import DuoBeta
    from form.avatar import Avatar, FaceController, Expression, build_default_registry


@dataclass
class Program:
    owner: str = "Operator"
    matrix: DellMatrix = field(default_factory=DellMatrix)
    main: MainField = field(default_factory=MainField)
    enhance: EnhanceGate = field(default_factory=EnhanceGate)
    ambient: AmbientGate = field(default_factory=AmbientGate)
    sandbox: SandboxGate = field(default_factory=SandboxGate)
    network_url: str = ""
    # Opt-in internet (default OFF · Origin offline law)
    internet: Any = None
    cube: BlankCube = field(init=False)
    duo: DuoBeta = field(init=False)
    avatar: Avatar = field(init=False)
    face: FaceController = field(init=False)
    kaomoji: Any = field(init=False)
    nursery: Nursery = field(init=False)
    growth: RingedGrowth = field(init=False)
    lattice: HarmonicLattice = field(init=False)
    keys: KeyLedger = field(default_factory=KeyLedger)
    history: List[str] = field(default_factory=list)
    history_max: int = 24
    # UX / entity layer (Phases A–E)
    companion: AICompanion = field(default_factory=AICompanion)
    ux_mode: str = "builder"  # beginner | builder | depth
    skin_filter: Optional[str] = None
    persona_lens: Optional[str] = None
    grid_snap: bool = False
    active_workshop: Optional[str] = None
    click_mode: str = "inspect"  # inspect | confirm
    camera_follow: bool = True
    show_nursery_ghosts: bool = True
    user_trail: List[List[float]] = field(default_factory=list)
    # src/ matrices ported into form/
    forces: ForceField = field(default_factory=ForceField)
    active_view: str = "growth"  # view room id
    body_style: str = "stick"  # ascii body: stick|block|shadow|robot
    bimo: BIMOBody = field(default_factory=BIMOBody)
    persona_matrix: PersonaMatrix = field(default_factory=PersonaMatrix)
    # First-person matrix walk (inside centerpoints)
    center_f: int = 0  # up/down lattice axis (frequency / height)
    look_pitch: str = "level"  # down | level | up
    view_mode: str = "first_person"  # first_person | map (legacy cone map)
    # Offline inspire pack (video-distilled pedagogy — no network models)
    inspire: InspireState = field(default_factory=InspireState)
    # Structural self-understanding + evolution ledger (not sentience)
    self_knowledge: SelfKnowledge = field(default_factory=SelfKnowledge)
    # Undo stack for place/edit (needs module)
    action_stack: List[Dict[str, Any]] = field(default_factory=list)
    # Grow mode: when True, grow_ideas auto-confirms all pending nursery proposals
    auto_confirm_grow: bool = False

    def __post_init__(self):
        assert_floor_intact()
        self.cube = give(self.owner)
        self.duo = DuoBeta(matrix=self.matrix)
        self.avatar = Avatar(name=self.owner)
        self.face = FaceController()
        self.kaomoji = build_default_registry()
        self.nursery = Nursery.load()
        self.growth = RingedGrowth(nursery=self.nursery)
        self.lattice = HarmonicLattice(size=SIZE_CHROMATIC)
        if not hasattr(self, "keys") or self.keys is None:
            self.keys = KeyLedger()
        if not hasattr(self, "companion") or self.companion is None:
            self.companion = AICompanion()
        if not hasattr(self, "forces") or self.forces is None:
            self.forces = ForceField()
        if not hasattr(self, "bimo") or self.bimo is None:
            self.bimo = BIMOBody()
        if not hasattr(self, "persona_matrix") or self.persona_matrix is None:
            self.persona_matrix = PersonaMatrix()
        if not hasattr(self, "inspire") or self.inspire is None:
            self.inspire = InspireState()
        if not hasattr(self, "self_knowledge") or self.self_knowledge is None:
            self.self_knowledge = SelfKnowledge()
        if not hasattr(self, "internet") or self.internet is None:
            try:
                from form.dell_matrix.internet_gate import InternetGate
                self.internet = InternetGate()
            except Exception:
                self.internet = None
        for name, kind, dell, term in (
            ("PlaneSurface", "tool", 15, "Plane"),
            ("MainField", "main", 21, "MainThird"),
            ("BlankCube", "cube", 8, "BlankCube"),
            ("GraphView", "tool", 9, "GraphView"),
            ("EnhanceGate", "tool", 32, "EnhanceGate"),
            ("Persist", "tool", 10, "Persist"),
            ("Visual", "tool", 9, "Visual"),
            ("SharedMain", "main", 21, "SharedMain"),
            ("AmbientGate", "tool", 25, "Ambient"),
            ("IdeaGrow", "growth", 13, "IdeaGrow"),
            ("SandboxGate", "tool", 23, "Sandbox"),
            ("NetworkMain", "main", 21, "Network"),
            ("Nursery", "growth", 23, "Nursery"),
            ("RingedGrowth", "growth", 13, "RingedGrowth"),
            ("Avatar", "entity", 2, "Avatar"),
            ("AICompanion", "entity", 2, "Companion"),
            ("HarmonicLattice", "lattice", 15, "Lattice"),
            ("KeyLedger", "memory", 10, "Keep"),
            ("LiveVisual", "tool", 9, "LiveVisual"),
            ("Workshops", "tool", 9, "Workshops"),
            ("NatureForces", "matrix", 25, "Forces"),
            ("Personas", "agents", 5, "Personas"),
            ("PersonaMatrix", "matrix", 15, "PersonaMatrix"),
            ("BIMO", "agents", 21, "BIMO"),
            ("ViewRooms", "lens", 9, "ViewRooms"),
            ("SixPillars", "audit", 32, "Pillars"),
            ("MatricesHub", "tool", 15, "Matrices"),
            ("InspirePack", "tool", 9, "Inspire"),
            ("SelfModel", "audit", 35, "SelfModel"),
            ("InternetGate", "tool", 25, "Internet"),
            ("CodeEvolution", "growth", 13, "CodeEvolution"),
        ):
            self.matrix.snap(
                SnapCandidate(
                    name=name, kind=kind,
                    manifest=manifest_from_dell(dell, term),
                    payload={"owner": self.owner},
                )
            )
        self.duo.evolve("01[Initiate] > 15[Map] >> 09[Show] :: Open")

    def note(self, action: str) -> None:
        text = (action or "").strip()[:120]
        self.history.append(text)
        if len(self.history) > self.history_max:
            self.history = self.history[-self.history_max :]

    def note_seed(self, dell: int, term: str, label: str = "") -> None:
        body = f"{dell:02d}[{term}]"
        if label:
            body = f"{body} :: {label[:40]}"
        self.note(body)

    def macro_seed(self, n: int = 5) -> str:
        recent = self.history[-max(1, n) :]
        if not recent:
            return "48[Macro] :: empty"
        return f"48[Macro] :: {' > '.join(recent)}"[:200]

    def replay(self, n: int = 3) -> List[str]:
        return list(self.history[-max(1, n) :])

    def replay_exec(self, n: int = 3) -> Dict[str, Any]:
        from form.mandell.seed import looks_like_seed
        from form.mandell.executor import execute_seed

        items = self.replay(n)
        ran, skipped = [], []
        for item in items:
            seed = item
            if looks_like_seed(seed) or (len(seed) >= 3 and seed[:2].isdigit() and "[" in seed):
                try:
                    res = execute_seed(self, seed)
                    ran.append({"seed": seed, "ok": bool(res.get("ok"))})
                except Exception as e:
                    ran.append({"seed": seed, "ok": False, "error": str(e)})
            else:
                skipped.append(item)
        return {"ok": True, "ran": ran, "skipped": skipped, "n": n}

    def distill_label(self, text: str) -> str:
        tokens = [t for t in (text or "").replace("_", " ").split() if len(t) > 2]
        if not tokens:
            return "distill"
        seen = []
        for t in tokens:
            tl = t.lower()
            if tl not in seen:
                seen.append(tl)
            if len(seen) >= 4:
                break
        return "_".join(seen)[:40]

    def avatar_status(self) -> Dict[str, Any]:
        b = self.avatar.body
        return {
            "body": self.avatar.status(),
            "face": self.face.status(),
            "describe": self.avatar.describe(),
            "look": self.face.show(),
            "pos": list(b.pos),
            "facing": b.facing.name if hasattr(b.facing, "name") else str(b.facing),
            "posture": b.posture.name.lower() if hasattr(b.posture, "name") else "stand",
            "locomotion": b.locomotion.name.lower() if hasattr(b.locomotion, "name") else "idle",
        }

    def _push_user_trail(self) -> None:
        """Append trail only when position actually changes (no idle pollution)."""
        pos = [float(self.avatar.body.pos[0]), float(self.avatar.body.pos[1])]
        if self.user_trail:
            lx, ly = self.user_trail[-1]
            if abs(lx - pos[0]) < 0.01 and abs(ly - pos[1]) < 0.01:
                return
        self.user_trail.append(pos)
        while len(self.user_trail) > 16:
            self.user_trail.pop(0)

    def apply_grid_snap(self) -> None:
        """Snap avatar to integer grid when grid_snap and form is cube/square."""
        if not self.grid_snap:
            return
        form = self.lattice.perception.form.value
        if form not in ("cube", "square"):
            return
        x, y = self.avatar.body.pos
        self.avatar.body.pos = (int(round(x)), int(round(y)))

    def nodes_payload(self) -> List[Dict[str, Any]]:
        scores = self.scores()
        out = []
        for uid, u in self.cube.session.plane.units.items():
            x = float(getattr(u, "x", 0) or 0)
            y = float(getattr(u, "y", 0) or 0)
            sc = float(scores.get(uid, 0.0))
            import math
            z = round(math.hypot(x, y) * 0.35 + sc * 0.25, 3)
            out.append({
                "id": uid,
                "label": u.label,
                "words": getattr(u, "words", "") or "",
                "detail": getattr(u, "detail", "") or "",
                "goals": list(getattr(u, "goals", []) or []),
                "skin": u.skin.value if hasattr(u.skin, "value") else str(u.skin),
                "x": x, "y": y, "z": z,
                "sandboxed": bool(getattr(u, "sandboxed", False)),
                "score": sc,
            })
        return out

    def look_around(self) -> Dict[str, Any]:
        """Directional vision from avatar facing (offline + live)."""
        b = self.avatar.body
        pos = [float(b.pos[0]), float(b.pos[1])]
        facing = b.facing.name if hasattr(b.facing, "name") else str(b.facing)
        ai = self.companion.to_dict()
        nodes = self.nodes_payload()
        vision = compute_vision(
            pos, facing, nodes,
            other=ai,
            skin_filter=self.skin_filter,
            persona=self.persona_lens,
        )
        # Multi-scale vision memory (DeepMind-inspired hierarchy, offline)
        try:
            mv = self.inspire.vision_mem.observe(nodes, pos, facing)
            self.inspire.last_multivision = mv
            vision["multiscale"] = {
                name: {"count": layer.get("count"), "nearest": layer.get("nearest"), "ids": layer.get("ids")}
                for name, layer in (mv.get("layers") or {}).items()
            }
            vision["vision_memory"] = mv.get("recent") or []
        except Exception:
            pass
        self.note_seed(9, "Show", "look")
        return vision

    def look_report(self) -> List[str]:
        lines = format_look_report(self.look_around())
        ents = self.all_entities()
        by_kind: Dict[str, int] = {}
        for e in ents:
            k = str(e.get("kind") or "?")
            by_kind[k] = by_kind.get(k, 0) + 1
        lines.append(
            "Entities: "
            + " · ".join(f"{k}={n}" for k, n in sorted(by_kind.items()))
        )
        # multi-scale layers
        ms = (self.inspire.last_multivision or {}).get("layers") or {}
        if ms:
            parts = []
            for name in ("near", "mid", "far"):
                layer = ms.get(name) or {}
                parts.append(f"{name}={layer.get('count', 0)}")
            lines.append("Multi-scale vision: " + " · ".join(parts))
        room = get_room(self.active_view)
        if room:
            lines.append(f"View room: {room.get('emoji', '')} {room.get('name')} — {room.get('description')}")
        if self.persona_lens:
            pe = get_persona(self.persona_lens)
            if pe:
                lines.append(f"Persona: {pe.get('emoji')} {pe.get('name')} · {pe.get('focus')}")
        # body art under look (sprite-animated when walking)
        for bline in self.body_art().splitlines():
            lines.append("  " + bline)
        return lines

    def all_entities(self) -> List[Dict[str, Any]]:
        """Inventory of every entity on stage — ideas, YOU, AI, nursery ghosts, lattice form."""
        out: List[Dict[str, Any]] = []
        b = self.avatar.body
        out.append({
            "kind": "avatar",
            "id": "you",
            "label": self.owner,
            "pos": [float(b.pos[0]), float(b.pos[1])],
            "facing": b.facing.name if hasattr(b.facing, "name") else str(b.facing),
            "posture": b.posture.name.lower() if hasattr(b.posture, "name") else "stand",
            "locomotion": b.locomotion.name.lower() if hasattr(b.locomotion, "name") else "idle",
            "holding": b.holding,
            "look": self.face.show() if hasattr(self, "face") else "",
        })
        ai = self.companion.to_dict()
        out.append({
            "kind": "companion",
            "id": "ai",
            "label": ai.get("label") or ai.get("name") or "AI",
            "pos": list(ai.get("pos") or [0, 0]),
            "facing": ai.get("facing"),
            "mode": ai.get("mode"),
            "doing": ai.get("doing"),
        })
        scores = self.scores()
        for uid, u in self.cube.session.plane.units.items():
            out.append({
                "kind": "idea",
                "id": uid,
                "label": u.label,
                "skin": u.skin.value if hasattr(u.skin, "value") else str(u.skin),
                "pos": [float(u.x), float(u.y)],
                "score": float(scores.get(uid, 0.0)),
                "sandboxed": bool(u.sandboxed),
                "zoomed": uid == self.cube.session.plane.zoom_target,
            })
        for prop in self.ranked_proposals()[:12]:
            out.append({
                "kind": "nursery_ghost",
                "id": prop.get("id"),
                "label": prop.get("label"),
                "affinity": prop.get("affinity"),
                "status": "pending",
            })
        lat = self.lattice.status() if hasattr(self, "lattice") else {}
        out.append({
            "kind": "lattice",
            "id": "lattice",
            "label": f"form={lat.get('form', '?')}",
            "form": lat.get("form"),
            "cells": lat.get("cells") or len(getattr(self.lattice, "cells", {}) or {}),
            "size": getattr(self.lattice, "size", None),
        })
        if self.active_workshop:
            out.append({
                "kind": "workshop",
                "id": self.active_workshop,
                "label": self.active_workshop,
            })
        return out

    def zoom_to(self, ref: str) -> Dict[str, Any]:
        """Zoom plane page to idea by id or label."""
        plane = self.cube.session.plane
        ref = (ref or "").strip()
        if not ref:
            return {"ok": False, "reason": "empty"}
        if ref in plane.units:
            plane.zoom_in(ref)
            self.note_seed(15, "Map", f"zoom_{ref}")
            return {"ok": True, "id": ref, "page": self.page_card(ref)}
        for uid, u in plane.units.items():
            if u.label.lower() == ref.lower():
                plane.zoom_in(uid)
                self.note_seed(15, "Map", f"zoom_{uid}")
                return {"ok": True, "id": uid, "page": self.page_card(uid)}
        return {"ok": False, "reason": f"not found: {ref}"}

    def unzoom(self) -> Dict[str, Any]:
        self.cube.session.plane.zoom_out()
        self.note_seed(15, "Map", "unzoom")
        return {"ok": True, "zoom": None}

    def page_card(self, unit_id: Optional[str] = None) -> Dict[str, Any]:
        """Full idea end-page — no loose ends: content + doors to next useful actions."""
        plane = self.cube.session.plane
        uid = unit_id or plane.zoom_target
        if not uid or uid not in plane.units:
            return {"ok": False, "reason": "no zoom target"}
        u = plane.units[uid]
        scores = self.scores()
        shell = self.lattice.perception.shell(float(u.x), float(u.y), 0.0)
        label = u.label
        skin = u.skin.value if hasattr(u.skin, "value") else str(u.skin)
        neighbors = plane.neighbors(uid)
        glyph = ""
        try:
            glyph = procedural_glyph(f"{label}:{skin}", 11, 5)
        except Exception:
            glyph = ""
        doors = [
            {"label": "Unzoom overview", "cmd": "unzoom"},
            {"label": "Look here", "cmd": "look"},
            {"label": "Multi-look", "cmd": "multilook"},
            {"label": f"Attend {label}", "cmd": f"attend {label}"},
            {"label": "Glyph card", "cmd": f"glyph {label}"},
            {"label": "Home", "cmd": "home"},
            {"label": "Nearest", "cmd": "nearest"},
            {"label": "Proposals", "cmd": "proposals"},
            {"label": "Save", "cmd": "save"},
        ]
        if neighbors:
            nid = neighbors[0]
            nlab = plane.units[nid].label if nid in plane.units else nid
            doors.insert(1, {"label": f"Next idea · {nlab}", "cmd": f"zoom {nid}"})
        return {
            "ok": True,
            "id": uid,
            "label": label,
            "skin": skin,
            "x": u.x, "y": u.y,
            "words": u.words or "",
            "detail": getattr(u, "detail", "") or "",
            "goals": list(getattr(u, "goals", []) or []),
            "score": float(scores.get(uid, 0.0)),
            "sandboxed": bool(u.sandboxed),
            "neighbors": neighbors,
            "shell": shell,
            "form": self.lattice.perception.form.value,
            "glyph": glyph,
            "doors": doors,
            "complete": True,
            "end": "idea_page",
        }

    def open_page(self, ref: Optional[str] = None) -> Dict[str, Any]:
        """
        Always reach an idea end-page.
        - ref given → zoom to id/label
        - already zoomed → refresh card
        - else → nearest idea to avatar (or first live unit)
        """
        plane = self.cube.session.plane
        ref = (ref or "").strip()
        if ref:
            out = self.zoom_to(ref)
            if out.get("ok"):
                out["opened"] = True
                out["auto"] = False
            return out
        # already on a page?
        if plane.zoom_target and plane.zoom_target in plane.units:
            card = self.page_card()
            return {"ok": True, "id": plane.zoom_target, "page": card, "opened": False, "auto": False}
        # pick nearest to avatar
        b = self.avatar.body
        ax, ay = float(b.pos[0]), float(b.pos[1])
        best_id = None
        best_d = 1e18
        for uid, u in plane.units.items():
            d = (float(u.x) - ax) ** 2 + (float(u.y) - ay) ** 2
            # prefer non-welcome if tied-ish
            if d < best_d or (abs(d - best_d) < 0.01 and best_id and "welcome" in str(best_id).lower()):
                best_d = d
                best_id = uid
        if not best_id:
            return {
                "ok": False,
                "reason": "no ideas yet — create an idea called <name> or grow ideas 1",
            }
        out = self.zoom_to(best_id)
        out["opened"] = True
        out["auto"] = True
        return out

    def format_page_end(self, card: Optional[Dict[str, Any]] = None) -> str:
        """Human end-page text for REPL / live result sheet."""
        card = card if card is not None else self.page_card()
        if not card or not card.get("ok"):
            return card.get("reason") if isinstance(card, dict) else "No page open"
        lines = [
            f"══ Idea page · {card.get('label')} ══",
            f"  id={card.get('id')}  skin={card.get('skin')}  shell={card.get('shell')}  "
            f"score={float(card.get('score') or 0):.2f}  form={card.get('form')}",
            f"  pos=({card.get('x')}, {card.get('y')})",
            f"  words: {card.get('words') or '—'}",
            f"  detail: {card.get('detail') or '—'}",
            f"  goals: {', '.join(card.get('goals') or []) or '—'}",
            f"  neighbors: {', '.join(card.get('neighbors') or []) or '—'}",
        ]
        if card.get("glyph"):
            lines.append("  glyph:")
            for gl in str(card["glyph"]).splitlines():
                lines.append("    " + gl)
        doors = card.get("doors") or []
        if doors:
            lines.append("  doors (next):")
            for d in doors[:8]:
                lines.append(f"    · {d.get('label')}:  {d.get('cmd')}")
        lines.append("  end · page complete · unzoom to leave")
        return "\n".join(lines)

    def set_ux_mode(self, mode: str) -> str:
        self.ux_mode = normalize_mode(mode)
        self.note_seed(4, "Transform", f"mode_{self.ux_mode}")
        return self.ux_mode

    def set_skin_filter(self, skin: Optional[str]) -> Optional[str]:
        if not skin or skin.lower() in ("clear", "off", "none", "all"):
            self.skin_filter = None
        else:
            self.skin_filter = skin.lower().strip()
        return self.skin_filter

    def set_persona_lens(self, name: Optional[str]) -> Optional[str]:
        if not name or name.lower() in ("clear", "off", "none"):
            self.persona_lens = None
            if hasattr(self, "persona_matrix"):
                self.persona_matrix.active = None
        else:
            key = normalize_persona_id(name)
            self.persona_lens = key or name.lower().replace(" ", "_").strip()
            if hasattr(self, "persona_matrix") and key:
                self.persona_matrix.active = key
            # if BIMO slot exists, dock this persona into its slot
            pe = get_persona(key) if key else None
            if pe and hasattr(self, "bimo") and pe.get("bimo_slot"):
                self.bimo.dock(pe["bimo_slot"], key)
        return self.persona_lens

    def personas_roster(self) -> List[str]:
        return render_roster(self.persona_lens)

    def persona_matrix_status(self) -> Dict[str, Any]:
        self.persona_matrix.active = self.persona_lens
        return self.persona_matrix.to_dict()

    def persona_matrix_ascii(self) -> List[str]:
        self.persona_matrix.active = self.persona_lens
        return self.persona_matrix.render_ascii()

    def bimo_status(self) -> Dict[str, Any]:
        return self.bimo.status()

    def bimo_dock(self, slot: str, persona: str) -> Dict[str, Any]:
        out = self.bimo.dock(slot, persona)
        if out.get("ok"):
            self.note_seed(21, "Merge", f"bimo_{slot}")
        return out

    def bimo_undock(self, slot: str) -> Dict[str, Any]:
        return self.bimo.undock(slot)

    def bimo_defaults(self) -> Dict[str, Any]:
        out = self.bimo.dock_defaults()
        self.note_seed(21, "Merge", "bimo_defaults")
        return out

    def bimo_fuse(self, context: str = "") -> Dict[str, Any]:
        out = self.bimo.fuse(context or f"view={self.active_view} persona={self.persona_lens or '—'}")
        # when fused, set lens to pilot for vision soft-sort
        if out.get("ok") and out.get("pilot"):
            self.persona_lens = out["pilot"]
            self.persona_matrix.active = out["pilot"]
        self.note_seed(21, "Merge", "bimo_fuse")
        return out

    def bimo_clear(self) -> Dict[str, Any]:
        return self.bimo.clear()

    def set_view(self, room_id: str) -> Dict[str, Any]:
        room = get_room(room_id)
        if not room:
            return {"ok": False, "reason": f"unknown room: {room_id}", "rooms": list_rooms()}
        self.active_view = room["id"]
        self.note_seed(9, "Show", f"view_{room['id']}")
        return {"ok": True, "view": room}

    def view_status(self) -> Dict[str, Any]:
        room = get_room(self.active_view) or get_room("growth")
        nodes = self.nodes_payload()
        filtered = filter_nodes_for_room(self.active_view, nodes, owner=self.owner, scores=self.scores())
        return {
            "active": room,
            "rooms": list_rooms(),
            "nodes": filtered,
            "ascii": render_room_ascii(self.active_view, nodes),
        }

    def personas_status(self) -> Dict[str, Any]:
        active = get_persona(self.persona_lens) if self.persona_lens else None
        return {
            "active": active,
            "list": list_personas(),
            "categories": list_categories(),
            "count": len(PERSONAS),
            "bimo": self.bimo.status() if hasattr(self, "bimo") else {},
            "matrix": self.persona_matrix_status() if hasattr(self, "persona_matrix") else {},
        }

    def guide(self, context: str = "") -> List[str]:
        return persona_guidance(self.persona_lens, context or f"view={self.active_view}")

    def set_body_style(self, style: str) -> str:
        s = (style or "stick").lower().strip()
        if s not in list_bodies():
            s = "stick"
        self.body_style = s
        return self.body_style

    def body_art(self) -> str:
        """ASCII body with optional p5play-inspired walk/idle sprite cycles."""
        b = self.avatar.body
        facing = b.facing.name if hasattr(b.facing, "name") else "N"
        loc = b.locomotion.name.lower() if hasattr(b.locomotion, "name") else "idle"
        try:
            sp = self.inspire.sprite
            sp.body_type = self.body_style
            sp.facing = facing
            if loc in ("walk", "jog", "run"):
                sp.set_action("walk")
            elif loc in ("jump",):
                sp.set_action("jump")
            else:
                sp.set_action("idle")
            return sp.step()
        except Exception:
            return render_body(self.body_style, facing)

    def force_tick(self) -> Dict[str, Any]:
        report = self.forces.tick(self.nodes_payload(), owner=self.owner)
        self.note_seed(25, "Pulse", "force_tick")
        return report

    def force_status(self) -> Dict[str, Any]:
        return self.forces.status()

    def set_weather(self, condition: str) -> str:
        c = self.forces.weather.set_condition(condition)
        self.note_seed(25, "Pulse", f"weather_{c}")
        return c

    def evolve(self, detail: str = "evolve") -> Dict[str, Any]:
        """Grow the whole program one generation — duo + forces + pillars."""
        return evolve_program(self, detail=detail)

    def know_self(self) -> Dict[str, Any]:
        """Structural self-understanding: inventory + mastery + gaps."""
        return know_self(self)

    def reflect(self) -> List[str]:
        """Human self-report end-page (what I am + how well I know it)."""
        return reflect_lines(self)

    def self_map(self) -> Dict[str, Any]:
        """Live inventory snapshot."""
        return self_inventory(self)

    def evolve_understood(self, detail: str = "self evolve") -> Dict[str, Any]:
        """Know → close gaps → evolve generation → re-audit."""
        return evolve_with_understanding(self, detail=detail)

    def close_self_gaps(self) -> Dict[str, Any]:
        """Warm cold capabilities and structural gaps."""
        return close_gaps(self)

    def evolve_loop(self, cycles: int = 12, detail: str = "loop") -> Dict[str, Any]:
        """Run N understand+evolve cycles (bounded; full 150 via module)."""
        n = max(1, min(150, int(cycles)))
        rows = []
        for i in range(1, n + 1):
            rows.append(self.evolve_understood(f"{detail}/{i}"))
        return {
            "ok": True,
            "cycles": n,
            "generation": self.duo.generation,
            "mastery": self.self_knowledge.to_dict().get("avg_mastery"),
            "pillars": self.audit(),
            "last": rows[-1] if rows else {},
        }

    def audit(self) -> Dict[str, Any]:
        return audit_program(self)

    def audit_lines(self) -> List[str]:
        return format_audit(self.audit())

    def matrices(self, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        return list_matrices(kind)

    def matrices_summary(self) -> str:
        return matrix_summary()

    def enter_workshop(self, workshop_id: str) -> Dict[str, Any]:
        w = get_workshop(workshop_id)
        if not w:
            return {"ok": False, "reason": f"unknown workshop: {workshop_id}", "list": list_workshops()}
        self.active_workshop = w["id"]
        self.note_seed(9, "Show", f"workshop_{w['id']}")
        return {"ok": True, "workshop": w}

    def leave_workshop(self) -> Dict[str, Any]:
        prev = self.active_workshop
        self.active_workshop = None
        return {"ok": True, "left": prev}

    def workshops_status(self) -> Dict[str, Any]:
        active = get_workshop(self.active_workshop) if self.active_workshop else None
        return {"active": active, "list": list_workshops()}

    def first_person(self) -> Dict[str, Any]:
        """First-person view from current centerpoint (inside the block/sphere)."""
        from form.dell_matrix.first_person import first_person_view
        # always snap to integer centerpoints
        self.grid_snap = True
        self.apply_grid_snap()
        return first_person_view(self)

    def fp_move(self, direction: str = "forward") -> Dict[str, Any]:
        from form.dell_matrix.first_person import move_fp
        return move_fp(self, direction)

    def fp_turn(self, direction: str = "right") -> Dict[str, Any]:
        from form.dell_matrix.first_person import turn_fp
        return turn_fp(self, direction)

    def fp_look(self, pitch: str = "level") -> Dict[str, Any]:
        from form.dell_matrix.first_person import look_fp
        return look_fp(self, pitch)

    def fp_goto(self, h: int, v: int, f: int = 0) -> Dict[str, Any]:
        from form.dell_matrix.first_person import goto_center
        return goto_center(self, h, v, f)

    def flower_draw_data(self) -> List[Dict[str, Any]]:
        """Flower of Life centers — always available for draw when form is flower, else empty list of pts."""
        from form.dell_matrix.sacred_geometry import flower_draw_payload
        if self.lattice.perception.form.value != "flower":
            return []
        payload = flower_draw_payload(rings=2, radius=1.0, include_vesica=True, include_fruit=True)
        return payload.get("centers") or []

    def flower_geometry(self, rings: int = 2) -> Dict[str, Any]:
        """Full FoL package: centers, circles, vesicas, fruit."""
        from form.dell_matrix.sacred_geometry import flower_draw_payload
        return flower_draw_payload(rings=rings, radius=1.0, include_vesica=True, include_fruit=True)

    def verita_edges(self) -> List[Dict[str, Any]]:
        """Vesica/Verita truth-of-meet edges between ideas."""
        from form.dell_matrix.sacred_geometry import verita_between_nodes
        return verita_between_nodes(self.nodes_payload())

    def voynich_status(self) -> Dict[str, Any]:
        from form.dell_matrix.sacred_geometry import voynich_status
        return voynich_status(self)

    def voynich_ascii(self) -> List[str]:
        from form.dell_matrix.sacred_geometry import voynich_ascii, voynich_status
        return voynich_ascii(voynich_status(self))

    def fractal_status(self, steps: int = 12) -> Dict[str, Any]:
        from form.dell_matrix.sacred_geometry import (
            rule90, rule90_ascii, complex_orbit, fractal_shells, sierpinski_points,
        )
        from form.mandell.bounded_orbit import coherence_report
        return {
            "rule90": rule90(33, steps),
            "rule90_ascii": rule90_ascii(33, min(16, steps)),
            "bounded_orbit": coherence_report(0.3, 0.2, 6),
            "complex_orbit": complex_orbit(c_real=-0.4, c_imag=0.6, steps=steps),
            "shells": fractal_shells(5),
            "sierpinski": [{"x": x, "y": y} for x, y in sierpinski_points(3)],
        }

    def geometry_status(self) -> Dict[str, Any]:
        from form.dell_matrix.sacred_geometry import geometry_status
        return geometry_status(self)

    def geometry_ascii(self) -> List[str]:
        from form.dell_matrix.sacred_geometry import geometry_ascii
        return geometry_ascii(self)

    def shell_rings_data(self, max_shell: int = 4) -> List[Dict[str, Any]]:
        """Rings for radial forms; cube/square get max-norm; flower/fractal get phi shells."""
        form = self.lattice.perception.form.value
        if form == "flower":
            from form.dell_matrix.sacred_geometry import fractal_shells
            # mild fractal shells under FoL
            return [{"shell": s, "radius": float(s), "metric": "flower"} for s in range(1, max_shell + 1)]
        if form in ("core", "sphere", "circle", "cube", "square"):
            return [{"shell": s, "radius": float(s), "metric": form} for s in range(1, max_shell + 1)]
        return []

    def set_lattice_size(self, size: int) -> Dict[str, Any]:
        """12 = chromatic default · 14 = Harmonic form geometry."""
        s = normalize_size(size)
        self.lattice.size = s
        self.note_seed(15, "Map", f"size_{s}")
        return {"ok": True, "size": s, "allowed": [SIZE_CHROMATIC, SIZE_HARMONIC]}

    def radial_drift(self, outer_shell: int = 6) -> Dict[str, Any]:
        """Soft-forget far-shell payloads; keys remain (Existence rule)."""
        out = apply_radial_soft_forget(self.lattice, self.keys, outer_shell=outer_shell)
        self.note_seed(16, "Decay", f"drift_{outer_shell}")
        return out

    def place(self, id: str, label: str, **kwargs):
        # Auto-spread when x/y omitted or stacked at origin — keeps entities visually distinct
        plane = self.cube.session.plane
        x = kwargs.get("x", None)
        y = kwargs.get("y", None)
        if x is None and y is None:
            kwargs["x"], kwargs["y"] = self._next_open_xy()
        elif (float(kwargs.get("x", 0) or 0) == 0.0 and float(kwargs.get("y", 0) or 0) == 0.0
              and any(abs(u.x) < 0.01 and abs(u.y) < 0.01 for u in plane.units.values())):
            kwargs["x"], kwargs["y"] = self._next_open_xy()
        u = self.cube.place_idea(id, label, **kwargs)
        # strong idea fields
        if "detail" in kwargs and kwargs.get("detail") is not None:
            u.detail = str(kwargs.get("detail") or "")
        if "goals" in kwargs and kwargs.get("goals") is not None:
            g = kwargs.get("goals")
            u.goals = list(g) if isinstance(g, (list, tuple)) else [str(g)]
        self.sandbox.maybe_auto_box(self.cube.session.plane, id)
        try:
            h = int(round(getattr(u, "x", 0) or 0))
            v = int(round(getattr(u, "y", 0) or 0))
            self.lattice.put(
                h, v, 0, content=id, label=label,
                tags=["idea"] + ([kwargs.get("words")] if kwargs.get("words") else []),
            )
        except Exception:
            pass
        try:
            self.keys.remember(label or id, meta={"id": id}, payload=kwargs.get("words") or label)
        except Exception:
            pass
        self.note_seed(8, "Create", label)
        return u

    # ─── Needs surface (strong create · edit · undo · nbd · ready) ───

    def create_strong(self, raw: str) -> Dict[str, Any]:
        from form.dell_matrix.needs import parse_and_place
        return parse_and_place(self, raw)

    def set_idea_detail(self, ref: str, detail: str) -> Dict[str, Any]:
        from form.dell_matrix.needs import set_detail
        return set_detail(self, ref, detail)

    def set_idea_goals(self, ref: str, goals_raw: str) -> Dict[str, Any]:
        from form.dell_matrix.needs import set_goals
        return set_goals(self, ref, goals_raw)

    def idea_info(self, ref: str) -> Dict[str, Any]:
        from form.dell_matrix.needs import idea_info
        return idea_info(self, ref)

    def undo(self) -> Dict[str, Any]:
        from form.dell_matrix.needs import undo_last
        return undo_last(self)

    def history_lines(self, n: int = 16) -> List[str]:
        from form.dell_matrix.needs import history_report
        return history_report(self, n)

    def what_next(self) -> str:
        from form.dell_matrix.needs import format_next
        return format_next(self)

    def ready(self) -> Dict[str, Any]:
        from form.dell_matrix.needs import ready_checklist
        return ready_checklist(self)

    def ready_lines(self) -> List[str]:
        from form.dell_matrix.needs import format_ready
        return format_ready(self).splitlines()

    # ─── Internet (opt-in) + Code Evolution root ─────────────────────

    def internet_on(self) -> Dict[str, Any]:
        if not self.internet:
            from form.dell_matrix.internet_gate import InternetGate
            self.internet = InternetGate()
        out = self.internet.turn_on()
        self.note_seed(25, "Pulse", "internet_on")
        return out

    def internet_off(self) -> Dict[str, Any]:
        if not self.internet:
            return {"ok": True, "on": False}
        out = self.internet.turn_off()
        self.note_seed(32, "Pause", "internet_off")
        return out

    def internet_status(self) -> Dict[str, Any]:
        if not self.internet:
            return {"on": False}
        return self.internet.status()

    def net_fetch(self, url: str) -> Dict[str, Any]:
        if not self.internet:
            return {"ok": False, "error": "no internet gate"}
        return self.internet.fetch_url(url)

    def net_research(self, topic: str) -> Dict[str, Any]:
        if not self.internet:
            return {"ok": False, "error": "no internet gate"}
        return self.internet.research_topic(topic)

    def ce_status(self) -> str:
        from form.dell_matrix.code_evolution import format_status
        return format_status(self)

    def ce_develop(self, cycles: int = 8, internet: bool = False) -> Dict[str, Any]:
        from form.dell_matrix.code_evolution import develop_loop
        return develop_loop(self, cycles=cycles, internet=internet, grow_cycles=2)

    def ce_ensure(self) -> Dict[str, Any]:
        from form.dell_matrix.code_evolution import ensure_root
        return ensure_root(self)

    def _next_open_xy(self) -> Tuple[float, float]:
        """Spiral search for an empty grid cell so new ideas do not stack on YOU/each other."""
        occupied = set()
        for u in self.cube.session.plane.units.values():
            occupied.add((int(round(u.x)), int(round(u.y))))
        # reserve avatar home so YOU and ideas stay distinct
        occupied.add((0, 0))
        for ring in range(1, 12):
            for dx in range(-ring, ring + 1):
                for dy in range(-ring, ring + 1):
                    if max(abs(dx), abs(dy)) != ring:
                        continue
                    if (dx, dy) not in occupied:
                        return float(dx), float(dy)
        n = len(self.cube.session.plane.units) + 1
        return float(n), 0.0

    def set_auto_confirm_grow(self, on: bool) -> bool:
        """Enable/disable auto-confirm-all after each grow (grow mode)."""
        self.auto_confirm_grow = bool(on)
        self.note_seed(13, "Loop", f"auto_confirm_grow_{'on' if self.auto_confirm_grow else 'off'}")
        return self.auto_confirm_grow

    def grow_ideas(self, cycles: int = 1) -> Dict[str, Any]:
        if not self.enhance.on:
            self.enhance.turn_on()
        result = self.growth.run(self.cube.session.plane, cycles=cycles)
        self.duo.evolve(f"13[Loop] :: RingedGrow x{cycles}")
        # Nature forces grow in parallel (visible stages)
        if hasattr(self, "forces"):
            for uid, u in list(self.cube.session.plane.units.items())[:12]:
                known = {p["idea"] for p in self.forces.growth.plants}
                if u.label not in known:
                    self.forces.growth.plant(u.label, self.owner)
            for _ in range(max(1, cycles)):
                self.forces.growth.grow_all(0.5)
            if "water" in self.forces.active:
                for u in list(self.cube.session.plane.units.values())[:3]:
                    self.forces.water.flow(u.label, self.owner)
            self.forces.time.advance()
            result["forces"] = self.forces.status()
        # Auto-confirm-all grow mode: accept every pending nursery proposal
        if getattr(self, "auto_confirm_grow", False):
            pending = list(self.list_proposals())
            ok_n = 0
            fail_n = 0
            labels: List[str] = []
            for prop in pending:
                res = self.confirm_proposal(prop["id"])
                if res.get("ok"):
                    ok_n += 1
                    labels.append(res.get("label") or prop.get("label") or prop.get("id"))
                else:
                    fail_n += 1
            result["auto_confirm"] = {
                "on": True,
                "confirmed": ok_n,
                "failed": fail_n,
                "labels": labels[:20],
            }
            result["nursery_pending"] = len(self.list_proposals())
            result["ideas_now"] = len(self.cube.session.plane.units)
        else:
            result["auto_confirm"] = {"on": False, "confirmed": 0, "failed": 0, "labels": []}
        self.note_seed(13, "Loop", f"growx{cycles}")
        return result

    def list_proposals(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.nursery.pending()]

    def ranked_proposals(self) -> List[Dict[str, Any]]:
        props = self.list_proposals()
        try:
            # Preference blend ≠ pure affinity imitation (NVIDIA-inspired)
            return self.inspire.prefs.rank_proposals(props)
        except Exception:
            return sorted(props, key=lambda p: -float(p.get("affinity", 0)))

    def confirm_proposal(self, pid: str) -> Dict[str, Any]:
        prop = self.nursery.confirm(pid)
        if not prop:
            return {"ok": False, "reason": "not found or not pending"}
        self.place(prop.id, prop.label, words=prop.words, skin=Skin.SEED)
        try:
            text = " ".join([
                str(prop.label or ""),
                str(getattr(prop, "words", "") or ""),
                str(getattr(prop, "detail", "") or ""),
            ])
            aff = float(getattr(prop, "affinity", 1.0) or 1.0)
            self.inspire.prefs.observe_confirm(text, aff)
        except Exception:
            pass
        self.note_seed(50, "Manifest", prop.label)
        return {"ok": True, "id": prop.id, "label": prop.label, "kind": prop.kind}

    def reject_proposal(self, pid: str) -> Dict[str, Any]:
        prop = self.nursery.reject(pid)
        if not prop:
            return {"ok": False, "reason": "not found or not pending"}
        try:
            text = " ".join([
                str(prop.label or ""),
                str(getattr(prop, "words", "") or ""),
                str(getattr(prop, "detail", "") or ""),
            ])
            self.inspire.prefs.observe_reject(text)
        except Exception:
            pass
        self.note_seed(24, "Unlock", "reject")
        return {"ok": True, "id": prop.id, "label": prop.label}

    def sandbox_on(self, all_units: bool = True) -> Dict[str, Any]:
        self.note_seed(23, "Lock", "sandbox_on")
        if all_units:
            return self.sandbox.apply_on(self.cube.session.plane)
        self.sandbox.turn_on()
        return {"ok": True, "on": True}

    def sandbox_off(self) -> Dict[str, Any]:
        self.note_seed(24, "Unlock", "sandbox_off")
        return self.sandbox.apply_off(self.cube.session.plane)

    def enhance_on(self) -> None:
        self.enhance.turn_on()
        self.note_seed(25, "Pulse", "enhance_on")

    def enhance_off(self) -> None:
        self.enhance.turn_off()
        self.note_seed(32, "Pause", "enhance_off")

    def pulse(self) -> Dict[str, Any]:
        out = self.enhance.pulse(self.cube.session.plane)
        # Score calculus: record slopes over time
        try:
            self.inspire.scores.push(self.scores())
            out = dict(out or {})
            out["slopes"] = self.inspire.scores.slopes()
        except Exception:
            pass
        self.note_seed(25, "Pulse")
        return out

    def scores(self) -> Dict[str, float]:
        return dict(self.enhance.state.scores)

    # ─── Inspire Pack surface (offline, video-distilled) ─────────────────

    def multilook(self) -> Dict[str, Any]:
        """Explicit multi-scale vision pass (near / mid / far + memory)."""
        b = self.avatar.body
        pos = [float(b.pos[0]), float(b.pos[1])]
        facing = b.facing.name if hasattr(b.facing, "name") else str(b.facing)
        mv = self.inspire.vision_mem.observe(self.nodes_payload(), pos, facing)
        self.inspire.last_multivision = mv
        self.note_seed(9, "Show", "multilook")
        return mv

    def attend(self, query: str = "", top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Soft attention over live ideas + nursery (LLM-from-scratch pedagogy).
        Cosine bag-of-embeddings ranking — educational stub, not a real LLM.
        """
        q = (query or "").strip() or "growth seed idea"
        docs: List[Dict[str, str]] = []
        for n in self.nodes_payload():
            docs.append({
                "id": str(n.get("id")),
                "label": str(n.get("label") or n.get("id")),
                "text": " ".join([
                    str(n.get("label") or ""),
                    str(n.get("words") or ""),
                    str(n.get("detail") or ""),
                    str(n.get("skin") or ""),
                ]),
            })
        for p in self.list_proposals():
            docs.append({
                "id": f"nursery:{p.get('id')}",
                "label": str(p.get("label") or p.get("id")),
                "text": " ".join([
                    str(p.get("label") or ""),
                    str(p.get("words") or ""),
                    str(p.get("detail") or ""),
                ]),
            })
        ranked = attention_rank(q, docs, top_k=top_k)
        self.inspire.last_attention = ranked
        self.note_seed(9, "Show", "attend")
        return ranked

    def slopes_report(self) -> List[str]:
        return self.inspire.scores.report()

    def prefs_status(self) -> Dict[str, Any]:
        return self.inspire.prefs.status()

    def glyph(self, seed: str = "") -> str:
        """Procedural glyph card — zero external art assets."""
        label = (seed or self.owner or "matrix").strip()
        # try match live idea
        skin = "cube"
        score = 0.0
        for n in self.nodes_payload():
            if label.lower() in str(n.get("label") or "").lower() or label == str(n.get("id")):
                skin = str(n.get("skin") or "cube")
                score = float(n.get("score") or 0)
                label = str(n.get("label") or label)
                break
        self.note_seed(9, "Show", "glyph")
        return procedural_idea_card(label, skin=skin, score=score)

    def run_script(self, script: str) -> Dict[str, Any]:
        """Verse-inspired mini matrix script (batch offline commands)."""
        self.note_seed(13, "Loop", "script")
        return run_matrix_script(self, script)

    def inspire_status(self) -> Dict[str, Any]:
        return self.inspire.status()

    def command_cost(self, cmd: str) -> str:
        return route_cost(cmd)

    def save(self, path: Optional[str] = None) -> str:
        from form.persist import save as persist_save
        self.nursery.save()
        self.note_seed(10, "Keep")
        return persist_save(self, path)

    def visual(self) -> Dict[str, str]:
        from form.dell_matrix.visual import write_visual
        self.note_seed(9, "Show", "visual")
        return write_visual(
            self.cube.session.plane,
            owner=self.owner,
            scores=self.scores(),
            avatar=self.avatar_status(),
            nursery=self.ranked_proposals(),
            rings=list(self.duo.rings),
            form=self.lattice.perception.form.value,
            skin=self.lattice.perception.skin_name(),
            companion=self.companion.to_dict(),
            ux_mode=self.ux_mode,
            page=self.page_card() if self.cube.session.plane.zoom_target else None,
            vision=self.look_around(),
            program=self,
        )

    def live_visual(self, port: int = 8765) -> Dict[str, Any]:
        """Start localhost two-way visual bridge. Opt-in. Snapshot remains default."""
        from form.dell_matrix.live_visual import start_live
        self.note_seed(9, "Show", "live_visual")
        return start_live(self, port=port, background=True)

    @staticmethod
    def load(owner: str = "Operator", path: Optional[str] = None) -> "Program":
        from form.persist import load as persist_load
        return persist_load(owner, path)

    def render(self) -> str:
        scores = self.scores()
        plane_txt = self.cube.session.plane.render(scores=scores)
        av = self.avatar_status()
        ns = self.nursery.summary()
        form_name = self.lattice.perception.form.value
        ks = self.keys.status() if hasattr(self, "keys") else {}
        ai = self.companion.to_dict()
        force_active = ",".join(self.forces.active) if hasattr(self, "forces") else "—"
        pillars = self.audit() if hasattr(self, "audit") else {}
        lines = [
            f"+- DellMatrix · owner={self.owner} -+",
            f"| Floor: {' · '.join(FLOOR)} (LOCKED)",
            f"| {av['look']}  {av['describe']}",
            f"| AI {ai['name']} @ {ai['pos']} face {ai['facing']} mode={ai['mode']} · {ai['doing']}",
            f"| ideas={len(self.cube.session.plane.units)}  nursery={ns['pending']}  gen={self.duo.generation}",
            f"| lattice form={form_name} cells={len(self.lattice.cells)}  size={self.lattice.size}",
            f"| mode={self.ux_mode} snap={self.grid_snap} lens={self.skin_filter or '—'} persona={self.persona_lens or '—'}",
            f"| view={self.active_view} workshop={self.active_workshop or '—'} body={self.body_style}",
            f"| forces=[{force_active}] weather={self.forces.weather.condition if hasattr(self, 'forces') else '—'}",
            f"| pillars={pillars.get('label', '—')} avg={pillars.get('average', '—')}  {self.matrices_summary()}",
            f"| click={self.click_mode} follow_cam={self.camera_follow}",
            f"| keys={ks.get('keys', 0)} payload={ks.get('with_payload', 0)}  (permanent keys)",
            f"| rings: {' → '.join(self.duo.rings)}  (Voynich-inspired)",
        ]
        for bline in self.body_art().splitlines():
            lines.append(f"| {bline}")
        for ln in plane_txt.splitlines():
            if ln.startswith("+-"):
                continue
            lines.append(ln if ln.startswith("|") else f"| {ln}")
        lines.append("+" + "-" * 52 + "+")
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        return {
            "owner": self.owner,
            "floor": floor_status(),
            "truths": truths_status(),
            "avatar": self.avatar_status(),
            "companion": self.companion.to_dict(),
            "inspire": self.inspire_status() if hasattr(self, "inspire_status") else {},
            "self_knowledge": self.self_knowledge.to_dict() if hasattr(self, "self_knowledge") else {},
            "nursery": self.nursery.summary(),
            "ideas": len(self.cube.session.plane.units),
            "rings": list(self.duo.rings),
            "enhance": self.enhance.status(),
            "lattice": self.lattice.status(),
            "keys": self.keys.status() if hasattr(self, "keys") else {},
            "pulse": pulse_status(),
            "history_len": len(self.history),
            "ux_mode": self.ux_mode,
            "grid_snap": self.grid_snap,
            "skin_filter": self.skin_filter,
            "persona_lens": self.persona_lens,
            "active_workshop": self.active_workshop,
            "click_mode": self.click_mode,
            "camera_follow": self.camera_follow,
            "actions": actions_for_mode(self.ux_mode),
            "active_view": self.active_view,
            "body_style": self.body_style,
            "forces": self.forces.status() if hasattr(self, "forces") else {},
            "personas": self.personas_status(),
            "bimo": self.bimo_status() if hasattr(self, "bimo") else {},
            "persona_matrix": self.persona_matrix_status() if hasattr(self, "persona_matrix") else {},
            "pillars": self.audit(),
            "matrices": self.matrices_summary(),
            "generation": self.duo.generation,
        }

    def smoke_ux(self) -> bool:
        """Quick A–E surface check."""
        self.place("ux_a", "UxA", words="test", x=0, y=2)
        v = self.look_around()
        z = self.zoom_to("UxA")
        self.enter_workshop("matrix")
        self.set_ux_mode("depth")
        self.companion.step(1)
        return bool(v.get("in_view_ids") is not None and z.get("ok") and self.active_workshop == "matrix")


def open_program(owner: str = "Operator") -> Program:
    return Program(owner=owner)


def smoke() -> bool:
    print("=== OPEN SMOKE ===")
    r = []
    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))
    p = open_program("Smoke")
    p.place("a", "AlphaIdea", words="one")
    rec("key remembered", p.keys.has_key("AlphaIdea"))
    p.set_lattice_size(14)
    rec("size 14", p.lattice.size == 14)
    p.set_lattice_size(12)
    out = p.grow_ideas(1)
    rec("grow", out.get("ok") is True)
    rec("truths", "truths" in p.status())
    rec("pulse constants", "subkey_pulse" in p.status().get("pulse", {}))
    paths = p.visual()
    rec("visual", "html" in paths)
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    print(open_program().render())


if __name__ == "__main__":
    main()
