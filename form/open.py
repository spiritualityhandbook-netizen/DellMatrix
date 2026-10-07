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
    from form.dell_matrix.spatial_authority import SpatialAuthority
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
    from form.dell_matrix.spatial_authority import SpatialAuthority
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
    # WO-5.1: Session-scoped acceptance policy. Default DENY.
    acceptance_policy: Any = field(default_factory=lambda: None, init=False)
    # WO-5.4: Learning gates. Default ON (influence) / ON (recording).
    # learning_influence: when False, selectors return baseline order.
    # learning_record: when False, evidence is not recorded.
    learning_influence: bool = True
    learning_record: bool = True
    avatar: Avatar = field(init=False)
    face: FaceController = field(init=False)
    kaomoji: Any = field(init=False)
    nursery: Nursery = field(init=False)
    growth: RingedGrowth = field(init=False)
    lattice: HarmonicLattice = field(init=False)
    keys: KeyLedger = field(default_factory=KeyLedger)
    history: List[str] = field(default_factory=list)
    history_max: int = 24
    # DCC-XX: durable execution-outcome evidence (Outcome Record V1).
    # outcome_id -> outcome record; outcome_seq is the per-owner durable
    # sequence counter used for stable outcome identity. Persisted via
    # the program payload; sealed into checkpoint generations. This is
    # OBSERVATION, never truth: no outcome ever mutates knowledge truth,
    # verification, disposition, revision, or dependency authority.
    outcome_records: Dict[str, Dict[str, Any]] = field(
        default_factory=dict, repr=False, compare=False)
    outcome_seq: int = field(default=0, repr=False, compare=False)
    # TPP-I: Temporal Presence Projection (NBD-Ω-048).
    # Presence metadata for ideas: {unit_id: {presence, pinned, created_seq}}.
    # Persisted via existing Program persistence. Not a second database.
    lifecycle: Dict[str, Any] = field(default_factory=dict, repr=False, compare=False)
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
    # Phase 4: canonical spatial authority (sole decider of post-placement
    # Idea positions; Plane remains the position store).
    spatial: SpatialAuthority = field(default_factory=SpatialAuthority)
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
    # Owner-bound Mandell language {cells, customs}; None = never loaded/bound (form.mandell.language.bind)
    language: Optional[Dict[str, Any]] = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        assert_floor_intact()
        self.cube = give(self.owner)
        self.duo = DuoBeta(matrix=self.matrix)
        self.avatar = Avatar(name=self.owner)
        self.face = FaceController()
        self.kaomoji = build_default_registry()
        # WO-5.1: Initialize session-scoped acceptance policy (default DENY).
        from form.dell_matrix.acceptance_policy import AcceptancePolicy
        self.acceptance_policy = AcceptancePolicy()
        from form.dell_matrix.nursery import owner_nursery_path
        # Private injection hook for generation-member loads: when open_program
        # is given a staged Nursery, __post_init__ uses it instead of reading
        # the owner's live nursery file, so a committed generation can be
        # staged even if the live file is absent or corrupt.
        _injected = getattr(self, "_init_nursery", None)
        # SWAT BREAK 1 FIX: Only when a Nursery is INJECTED, check for journals.
        # If a confirmation or supersession journal exists, the live state
        # is uncertain. The injected object bypasses file-based recovery,
        # which would expose unhealed hybrids. Fail closed.
        # Ordinary construction (no injection) MUST run recovery; do not block it.
        if _injected is not None:
            from form.mandell.core_i_recovery import _confirm_journal_path, _supersede_journal_path
            import os as _os
            if _os.path.isfile(_confirm_journal_path(self.owner)):
                from form.mandell.core_i_recovery import RollbackRecoveryError
                raise RollbackRecoveryError(
                    "Program: confirmation journal exists for owner; "
                    "injected Nursery bypasses recovery (fail closed)"
                )
            if _os.path.isfile(_supersede_journal_path(self.owner)):
                from form.mandell.core_i_recovery import RollbackRecoveryError
                raise RollbackRecoveryError(
                    "Program: supersession journal exists for owner; "
                    "injected Nursery bypasses recovery (fail closed)"
                )
        if _injected is None:
            # R3: Run confirmation-intent recovery before loading live nursery.
            # Recovers from RECORDED INTENT (journal), not inferred visibility.
            # Preserves legitimate historical records without journals.
            #
            # R3-FINAL-ADMISSION req. 2: If recovery cannot execute, do NOT
            # expose unverified live Nursery state. Fail closed.
            # The injected-generation path (above) is preserved; it does not
            # use the live file and has its own documented contract.
            from form.mandell.core_i_recovery import recover_confirmation_intent
            from form.mandell.core_i_recovery import recover_supersede_intent
            # If ImportError occurs, it propagates (fail closed).
            # Do NOT catch and continue; unverified state must not be exposed.
            recover_confirmation_intent(self.owner)
            recover_supersede_intent(self.owner)
        self.nursery = _injected if _injected is not None else Nursery.load(owner_nursery_path(self.owner))
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
        """One force pulse + canonical spatial dynamics (Phase 4).

        ForceField.tick keeps bookkeeping (breath, growth, water, wells,
        weather). Position integration is decided SOLELY by the canonical
        spatial authority (bounded, damped, deterministic, lifecycle-gated).
        The legacy NatureBridge writer is retired; its admitted math
        (attract with min-dist clamp) lives on as a calculator inside the
        authority.
        """
        report = self.forces.tick(self.nodes_payload(), owner=self.owner)
        # Canonical spatial dynamics (Phase 4 authority).
        try:
            spatial = self.spatial.tick(self)
            report["spatial"] = spatial
        except Exception as e:
            report["spatial"] = {"ok": False, "error": str(e)}
        # Legacy nature-physics path: retired as an independent writer.
        # Kept as a no-op record so callers/tests observing the key do not
        # break; it must not move units.
        report["nature"] = {"ok": True, "retired": True,
                            "note": "position integration moved to "
                                    "SpatialAuthority.tick (Phase 4)"}
        self.note_seed(25, "Pulse", "force_tick")
        return report

    def force_status(self) -> Dict[str, Any]:
        return self.forces.status()

    def spatial_settle(self, max_ticks: int = None) -> Dict[str, Any]:
        """Run bounded dynamics to equilibrium or honest non-convergence."""
        from form.dell_matrix.spatial_authority import MAX_SETTLE_TICKS
        return self.spatial.settle(
            self, max_ticks=MAX_SETTLE_TICKS if max_ticks is None
            else max_ticks)

    def spatial_explain(self, idea_id: str) -> Dict[str, Any]:
        """Why an idea occupies its current location (4.1.5)."""
        return self.spatial.explain(self, idea_id)

    def force_growth(self) -> Dict[str, Any]:
        """IAC-I: Canonical growth-force activation. Extracted from live_visual."""
        self.forces.activate("growth")
        for u in list(self.cube.session.plane.units.values())[:8]:
            known = {pl["idea"] for pl in self.forces.growth.plants}
            if u.label not in known:
                self.forces.growth.plant(u.label, self.owner)
        self.forces.growth.grow_all(0.6)
        lines = self.forces.growth.map()[:8]
        self.note_seed(25, "Pulse", "force_growth")
        return {"ok": True, "lines": lines}

    def force_water(self) -> Dict[str, Any]:
        """IAC-I: Canonical water-force activation. Extracted from live_visual."""
        self.forces.activate("water")
        for u in list(self.cube.session.plane.units.values())[:3]:
            self.forces.water.flow(u.label, self.owner)
        extra = ""
        if len(self.forces.water.streams) >= 2:
            m = self.forces.water.merge_last_two()
            if m:
                extra = f"\n  Merged → {m['idea'][:60]}"
        self.note_seed(25, "Pulse", "force_water")
        return {
            "ok": True,
            "streams": len(self.forces.water.streams),
            "pools": len(self.forces.water.pools),
            "extra": extra,
        }

    def force_breath(self) -> Dict[str, Any]:
        """IAC-I: Canonical breath-force activation. Extracted from live_visual."""
        self.forces.activate("breath")
        r = self.forces.breath.heartbeat(len(self.cube.session.plane.units))
        self.note_seed(25, "Pulse", "force_breath")
        return {"ok": True, "cycle": r['inhale']['cycle'], "phase": self.forces.breath.phase}

    def force_gravity(self) -> Dict[str, Any]:
        """IAC-I: Canonical gravity-force activation. Extracted from live_visual."""
        self.forces.activate("gravity")
        wells = self.forces.gravity.set_wells_from_scores(self.nodes_payload())
        labels = ", ".join(w["label"] for w in wells[:8]) or "—"
        self.note_seed(25, "Pulse", "force_gravity")
        return {"ok": True, "labels": labels}

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
        """Vesica/Verita coherence-of-meet edges between ideas."""
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
        # Phase 4: coordinate selection is decided by the canonical spatial
        # authority (deterministic placement + explanation). Explicit x/y
        # from the caller (user authority) is honored; otherwise the
        # authority computes placement (barycentric-from-neighbors or
        # neutral spiral). The raw (0,0) default is never used silently.
        # Explicit coordinates (including explicit 0.0) are always honored;
        # only absent coordinates go to the authority. The old silent
        # (0,0)-redirect is removed: it dishonestly overrode explicit user
        # intent.
        plane = self.cube.session.plane
        x = kwargs.get("x", None)
        y = kwargs.get("y", None)
        if x is None or y is None:
            # Ask the authority for a deterministic placement. It reuses
            # the _next_open_xy spiral contract when no graph information
            # applies, and records the explanation.
            spot = self.spatial.place(self, id, label)
            kwargs["x"], kwargs["y"] = spot["x"], spot["y"]
        else:
            # Explicit coordinates: honored exactly, but still recorded
            # by the authority (explanation with cause="explicit") so
            # every placement is traceable.
            spot = self.spatial.place(self, id, label,
                                      x=float(x), y=float(y))
            kwargs["x"], kwargs["y"] = spot["x"], spot["y"]
        u = self.cube.place_idea(id, label, **kwargs)
        # strong idea fields
        if "detail" in kwargs and kwargs.get("detail") is not None:
            u.detail = str(kwargs.get("detail") or "")
        if "goals" in kwargs and kwargs.get("goals") is not None:
            g = kwargs.get("goals")
            u.goals = list(g) if isinstance(g, (list, tuple)) else [str(g)]
        self.sandbox.maybe_auto_box(self.cube.session.plane, id)
        # Phase 4: the lattice is a DERIVED projection, not an independent
        # truth. Rebuild it deterministically from Plane (replaces the old
        # lossy one-way mirror, which drifted silently).
        try:
            if hasattr(self.lattice, "rebuild_from_plane"):
                self.lattice.rebuild_from_plane(self.cube.session.plane)
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
        """Enable/disable auto-confirm-all after each grow (grow mode).

        WO-5.1: Enabling grants a scoped session opt-in for the "grow_auto"
        producer. Disabling revokes it. Opt-in is visible, revocable, audited,
        and expires at session end.
        """
        self.auto_confirm_grow = bool(on)
        policy = getattr(self, "acceptance_policy", None)
        if policy is not None:
            if self.auto_confirm_grow:
                policy.grant_opt_in(
                    "grow_auto",
                    scope=f"session:{policy.session_id}",
                    note="User enabled 'auto confirm on' in REPL",
                )
            else:
                policy.revoke_opt_in("grow_auto")
        self.note_seed(13, "Loop", f"auto_confirm_grow_{'on' if self.auto_confirm_grow else 'off'}")
        return self.auto_confirm_grow

    def grow_ideas(self, cycles: int = 1, scope_ids=None,
                   include_superseded: bool = False) -> Dict[str, Any]:
        """Run RingedGrowth.

        DCC-XI: scope_ids optionally constrains the consumer to exactly
        the given unit IDs via a read-only ScopedPlaneView. None (default)
        preserves historical full-plane behavior for baseline growth.

        WO-5.3: include_superseded=True enables explicit historical use.
        Ordinary growth (default) excludes SUPERSEDED.
        """
        from form.mandell.knowledge_selector import ScopedPlaneView
        if not self.enhance.on:
            self.enhance.turn_on()
        plane = self.cube.session.plane
        scope_mode = "full"
        if scope_ids is not None:
            # Validate scope at the consumer boundary: every ID must be
            # a live plane unit. Never silently broaden.
            missing = [sid for sid in scope_ids if sid not in plane.units]
            if missing:
                raise ValueError(f"scope IDs not on plane: {missing}")
            plane = ScopedPlaneView(plane, scope_ids)
            scope_mode = "contextual"
        # P3 R3.6: attach the owner's Phase-2 graph as a read-only signal
        # for RingedGrowth (graph_coherence over proposal pairs). Best
        # effort: a missing/unreadable/corrupt graph degrades to the
        # defined neutral (no graph signal), reported honestly — growth
        # must not crash on unrelated graph state.
        graph = None
        graph_state = "none"
        try:
            from form.mandell.semantic_graph import SemanticGraph
            graph = SemanticGraph.load(self.owner)
            graph_state = "attached"
        except Exception:
            graph = None
            graph_state = "unavailable"
        result = self.growth.run(plane, cycles=cycles, graph=graph, program=self,
                                 include_superseded=include_superseded)
        result["scope_mode"] = scope_mode
        result["graph_signal"] = graph_state
        result["scope_ids"] = list(scope_ids) if scope_ids is not None else None
        self.duo.evolve(f"13[Loop] :: RingedGrow x{cycles}")
        # Nature forces grow in parallel (visible stages)
        if hasattr(self, "forces"):
            for uid, u in list(plane.units.items())[:12]:
                known = {p["idea"] for p in self.forces.growth.plants}
                if u.label not in known:
                    self.forces.growth.plant(u.label, self.owner)
            for _ in range(max(1, cycles)):
                self.forces.growth.grow_all(0.5)
            if "water" in self.forces.active:
                for u in list(plane.units.values())[:3]:
                    self.forces.water.flow(u.label, self.owner)
            self.forces.time.advance()
            result["forces"] = self.forces.status()
        # Auto-confirm-all grow mode: accept every pending nursery proposal
        # WO-5.1: Requires active opt-in for "grow_auto" producer.
        if getattr(self, "auto_confirm_grow", False):
            pending = list(self.list_proposals())
            ok_n = 0
            fail_n = 0
            labels: List[str] = []
            for prop in pending:
                res = self.confirm_proposal(prop["id"], _producer="grow_auto")
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

    def harmony_of(self, ideas) -> float:
        """Harmony of an idea set (GDP-001 Phase 3, R3.2.5 public path).

        Thin public wrapper over the canonical metric
        form.dell_matrix.harmony.harmony_score: "the degree to which a set
        of ideas forms a coherent, non-redundant whole", in [0, 1].

        Accepts an iterable of Idea objects, plane unit ID strings
        (resolved against this program's cube plane; unit tokens come
        from the unit's real label/words/detail/goals), or a mix.

        Canonical lifecycle (P3 closeout): Unit IDs are resolved through
        the owner-aware canonical boundary
        (form.dell_matrix.canonical_lifecycle). Only units with active
        canonical lifecycle participate; faded/superseded/unknown units
        are excluded (fail-closed). Unknown unit IDs fail closed to 0.0
        (never raises). Stateless: computes from current content, writes
        nothing.
        """
        from form.dell_matrix.harmony import harmony_score
        from form.dell_matrix import canonical_lifecycle

        class _PlaneUnitView:
            """Adapter: exposes a plane unit through the idea token interface.

            Token sources only. Lifecycle was resolved canonically at the
            ID level (is_active check above); this adapter reports "active"
            because the unit passed the canonical boundary. This is not
            dynamic injection — it's the verified result.
            """

            def __init__(self, unit):
                self.title = getattr(unit, "label", "") or ""
                self._unit = unit
                # Canonical verification already passed at ID resolution.
                self.idea_state = "active"

            def get_active_properties(self):
                u = self._unit
                props = {}
                for name in ("words", "detail"):
                    v = getattr(u, name, "")
                    if v:
                        props[name] = v
                goals = getattr(u, "goals", None) or []
                if goals:
                    props["goals"] = " ".join(str(g) for g in goals)
                return props

        if ideas is None or isinstance(ideas, (str, bytes)):
            return 0.0
        try:
            items = list(ideas)
        except TypeError:
            return 0.0
        plane = self.cube.session.plane
        resolved = []
        for it in items:
            if isinstance(it, str):
                # Canonical lifecycle boundary: resolve (program, unit_id)
                # via inspect_revision. Inactive/unreadable -> excluded.
                # Unknown unit ID -> fail closed to 0.0 (entire result).
                unit = plane.units.get(it)
                if unit is None:
                    return 0.0
                if not canonical_lifecycle.is_active(self, it):
                    continue
                resolved.append(_PlaneUnitView(unit))
            else:
                resolved.append(it)
        return harmony_score(resolved)


    def ranked_proposals(self) -> List[Dict[str, Any]]:
        props = self.list_proposals()
        # P3 R3.6: harmony + graph coherence, persisted on each proposal by
        # RingedGrowth.run, are consumed here as tie-breakers — this is the
        # real consumer that reads the scores (repl, visual, and the
        # executor leaf all render this ordering). Preference blending is
        # untouched: harmony only orders proposals the preference model
        # scores equally (blended ties), then graph coherence.
        def _rank_key(p: Dict[str, Any]):
            return (
                -float(p.get("blended", p.get("affinity", 0)) or 0),
                -float(p.get("harmony", 0) or 0),
                -float(p.get("graph_coherence", 0) or 0),
            )
        try:
            # Preference blend ≠ pure affinity imitation (NVIDIA-inspired)
            ranked = self.inspire.prefs.rank_proposals(props)
            ranked.sort(key=_rank_key)  # stable: keeps pref order, breaks ties
            return ranked
        except Exception:
            return sorted(props, key=lambda p: (
                -float(p.get("affinity", 0) or 0),
                -float(p.get("harmony", 0) or 0),
                -float(p.get("graph_coherence", 0) or 0),
            ))

    def _acceptance_data_for(self, pid: str,
                             operation: str = "confirm") -> dict:
        """Canonical acceptance-relevant data for a proposal.

        Director 2026-10-05: canonical JSON serialization + SHA-256;
        no delimiter concatenation. Covers identity, owner, content,
        parents, goals, and applicable revision metadata.
        """
        from form.dell_matrix.acceptance_policy import acceptance_data
        prop = self.nursery.proposals.get(pid)
        content = {
            "label": getattr(prop, "label", "") if prop else "",
            "words": getattr(prop, "words", "") if prop else "",
            "detail": getattr(prop, "detail", "") if prop else "",
        }
        parents = list(getattr(prop, "parents", []) or []) if prop else []
        goals = list(getattr(prop, "goals", []) or []) if prop else []
        revision = {
            "supersedes_id": getattr(prop, "supersedes_id", None),
            "superseded_by_id": getattr(prop, "superseded_by_id", None),
            "revision_root_id": getattr(prop, "revision_root_id", None),
            "revision_number": getattr(prop, "revision_number", None),
            "lifecycle_state": getattr(prop, "lifecycle_state", None),
        } if prop else {}
        owner = getattr(self, "owner", "") or ""
        return acceptance_data(pid, owner, content, parents,
                               goals=goals, revision=revision)

    def make_review_context(self, pid: str, reviewer: str,
                            operation: str = "confirm") -> dict:
        """Issue a bound review approval for a proposal.

        Director 2026-10-05: issuance is RECORDED in the session policy.
        The returned context references the recorded approval_id; a
        matching dict alone is not evidence of issuance. Bound to
        operation, target, reviewed data hash, and session.
        """
        from form.dell_matrix.acceptance_policy import canonical_hash
        policy = getattr(self, "acceptance_policy", None)
        if policy is None:
            raise RuntimeError("acceptance policy missing")
        data = self._acceptance_data_for(pid, operation)
        issued = policy.issue_approval(operation=operation, target=pid,
                                        reviewer=reviewer, data=data)
        return issued["context"]

    def acceptance_data_hash(self, pid: str,
                             operation: str = "confirm") -> str:
        """Canonical hash of current acceptance-relevant data for pid."""
        from form.dell_matrix.acceptance_policy import canonical_hash
        return canonical_hash(self._acceptance_data_for(pid, operation))

    def make_supersede_context(self, old_id: str, reviewer: str,
                               words: str, label: str = None) -> dict:
        """Issue a bound approval for a supersession operation.

        Director 2026-10-05 (whole-circuit): binds predecessor version +
        proposed successor data (label/words). The approval is recorded in
        the session policy; the context references the issuance.
        """
        from form.dell_matrix.acceptance_policy import canonical_hash
        policy = getattr(self, "acceptance_policy", None)
        if policy is None:
            raise RuntimeError("acceptance policy missing")
        pred_hash = self.acceptance_data_hash(old_id, "supersede")
        # Label must match _supersede_impl's successor creation logic:
        # explicit label, else "revision of {old label}".
        old_prop = self.nursery.proposals.get(old_id)
        eff_label = label or f"revision of {getattr(old_prop, 'label', old_id)}"
        succ_hash = canonical_hash({"label": eff_label, "words": words or ""})
        data = {"predecessor": pred_hash, "successor": succ_hash}
        issued = policy.issue_approval(operation="supersede", target=old_id,
                                        reviewer=reviewer, data=data)
        return issued["context"]

    def confirm_proposal(self, pid: str, _producer: str = "unknown",
                         _review_context: dict = None,
                         _operation: str = "confirm",
                         _subject: str = None) -> Dict[str, Any]:
        """Canonical confirmation with acceptance policy (WO-5.1).

        Args:
            pid: Proposal ID.
            _producer: Producer ID for policy check (e.g., "repl_user",
                "auto_growth", "code_evolution"). Defaults to "unknown".
            _review_context: Review context referencing an approval ISSUED
                by this session's policy (see make_review_context), or an
                R6.1 capability grant ({"grant_id": ...}).
            _operation: Operation the approval must bind to (default
                "confirm"; composite ops use derived approvals).
            _subject: R6.1 trusted subject binding for the grant path.
                Established by trusted dispatch code, never by the
                caller's payload. Required when _review_context carries a
                grant_id; ignored by the human-approval/opt-in paths.

        Returns:
            {"ok": True, ...} on success.
            {"ok": False, "reason": "acceptance_policy_denied", ...} if denied.
        """
        # WO-5.1 / Director 2026-10-05: Policy check at canonical boundary.
        # Missing policy fails CLOSED (not open).
        policy = getattr(self, "acceptance_policy", None)
        if policy is None:
            return {
                "ok": False,
                "reason": "acceptance_policy_denied",
                "detail": "No acceptance policy configured (fail closed).",
                "pid": pid,
                "producer": _producer,
            }
        prop = self.nursery.proposals.get(pid)
        if prop is None:
            return {
                "ok": False,
                "reason": "not found or not pending",
                "pid": pid,
            }
        # Canonical data hash at check time.
        data_hash = self.acceptance_data_hash(pid, _operation)
        decision = policy.check(_producer, pid, _review_context,
                                proposal_version=data_hash,
                                operation=_operation,
                                subject=_subject, owner=self.owner)
        if not decision.get("allowed"):
            return {
                "ok": False,
                "reason": "acceptance_policy_denied",
                "detail": decision.get("detail"),
                "pid": pid,
                "producer": _producer,
            }
        # Director 2026-10-05 (final): live validation at the EXECUTION
        # boundary. The initial check above gates entry; this final check
        # validates live permission (revocation, source chain) and reviewed
        # data immediately before the protected mutation. A full policy
        # check — not just a hash comparison — so revocation between
        # authorization and execution denies with no accepted transition.
        live_hash = self.acceptance_data_hash(pid, _operation)
        live = policy.check(_producer, pid, _review_context,
                            proposal_version=live_hash,
                            operation=_operation,
                            subject=_subject, owner=self.owner)
        if not live.get("allowed"):
            # No mutation has occurred; proposal remains pending and
            # retryable. Staged work (none yet) needs no recovery.
            return {
                "ok": False,
                "reason": "acceptance_policy_denied",
                "detail": live.get("detail") or
                          "Live validation failed at execution boundary.",
                "pid": pid,
                "producer": _producer,
            }
        from form.dell_matrix.confirm_lineage import confirm_proposal as _confirm_proposal
        # Director 2026-10-05 (boundary): carry the approved operation into
        # the writer as an immutable snapshot. The writer validates live
        # policy and reviewed-data integrity before placement and before
        # durable publish.
        # R6.1: the trusted subject binding rides the snapshot so writer
        # stages re-validate the same binding (no re-derivation from
        # caller input inside the writer).
        _auth = {
            "producer": _producer,
            "pid": pid,
            "operation": _operation,
            "data_hash": live_hash,
            "review_context": _review_context,
            "subject": _subject,
        }
        return _confirm_proposal(self, pid, _auth=_auth)

    def confirm_rollback(self, generation_id=None,
                         _review_context: dict = None,
                         _subject: str = None,
                         _producer: str = "unknown") -> Dict[str, Any]:
        """Authority-mediated checkpoint rollback (R6.3).

        The canonical mediated rollback. Every exposed path (Dell28,
        REPL revert/restore, agent endpoint, direct Program calls)
        routes through here. An owner string alone denies.

        Sequence (mirrors confirm_proposal's two-check pattern):
        1. Freeze the restore target (CURRENT resolved once; manifest
           + member fingerprints bound; private staging, no activation).
        2. Entry authority check (policy.check, operation=
           "checkpoint.rollback"). Denial = zero mutation.
        3. Safety checkpoint of live state (retention keeps the frozen
           target). Failure = zero rollback mutation.
        4. Live revalidation = THE COMMIT DECISION (full policy check;
           revocation/chain/target/operation re-verified; frozen target
           re-validated). Denial = safe, no rollback.
        5. Intent journal records the authorized outcome (no handles).
        6. Canonical core_i_recovery.rollback to the frozen target.
        7. Verify restoration (CURRENT names target; members match).
        8. Clear intent; mark this (now stale) instance; return receipt.

        After the commit decision, restart completes the recorded
        outcome without the session credential (recover_rollback_intent).

        Returns {"ok": True, "generation_id", "compensating_generation_id",
        ...} or {"ok": False, "reason", "detail"}.
        """
        from form.dell_matrix import rollback_authority as ra
        from form.dell_matrix.acceptance_policy import canonical_hash

        policy = getattr(self, "acceptance_policy", None)
        if policy is None:
            return {"ok": False, "reason": "acceptance_policy_denied",
                    "detail": "No acceptance policy configured (fail closed)."}
        # 1. Freeze the target before any writes.
        try:
            frozen = ra.freeze_rollback_target(self.owner, generation_id)
        except ra.RollbackTargetError as exc:
            return {"ok": False, "reason": "rollback_target_invalid",
                    "detail": str(exc)[:300]}
        target_gid = frozen["generation_id"]
        # Content binds the frozen target AND live state at entry.
        live_fp = ra._live_fingerprints(self.owner)
        content_hash = canonical_hash(
            ra.rollback_content(frozen, live_fp))
        # 2. Entry authority check. Zero mutation on denial.
        decision = policy.check(
            _producer, target_gid, _review_context,
            proposal_version=content_hash,
            operation=ra.ROLLBACK_OPERATION,
            subject=_subject, owner=self.owner)
        if not decision.get("allowed"):
            return {"ok": False, "reason": "acceptance_policy_denied",
                    "detail": decision.get("detail"),
                    "generation_id": target_gid}
        # 3. Safety checkpoint (retention preserves the frozen target).
        from form.mandell.core_i_recovery import checkpoint as _checkpoint
        import time as _time
        stamp = (f"pre-rollback-{target_gid}-"
                 f"{_time.strftime('%Y%m%dT%H%M%S', _time.gmtime())}")
        try:
            comp_gid = _checkpoint(self, stamp=stamp,
                                   keep_extra={target_gid})
        except Exception as exc:
            return {"ok": False, "reason": "safety_checkpoint_failed",
                    "detail": f"{type(exc).__name__}: {str(exc)[:200]}",
                    "generation_id": target_gid}
        # 4. Live revalidation = the commit decision. Full policy check
        # (revocation, chain, subject, owner, target, operation) plus
        # frozen-target re-validation, immediately before the protected
        # transition. Uses entry-captured live fingerprints: the safety
        # checkpoint above is part of the authorized flow, not drift.
        live = policy.check(
            _producer, target_gid, _review_context,
            proposal_version=content_hash,
            operation=ra.ROLLBACK_OPERATION,
            subject=_subject, owner=self.owner)
        if not live.get("allowed"):
            return {"ok": False, "reason": "acceptance_policy_denied",
                    "detail": live.get("detail") or
                    "Live validation failed at execution boundary.",
                    "generation_id": target_gid,
                    "compensating_generation_id": comp_gid}
        try:
            frozen2 = ra.freeze_rollback_target(self.owner, target_gid)
        except ra.RollbackTargetError as exc:
            return {"ok": False, "reason": "acceptance_policy_denied",
                    "detail": f"Target changed after authorization: {exc}",
                    "generation_id": target_gid,
                    "compensating_generation_id": comp_gid}
        if frozen2["members"] != frozen["members"]:
            return {"ok": False, "reason": "acceptance_policy_denied",
                    "detail": "Target fingerprints changed after "
                             "authorization.",
                    "generation_id": target_gid,
                    "compensating_generation_id": comp_gid}
        # 5. Intent journal records the authorized outcome (no handles).
        from form.mandell.core_i_recovery import (
            write_rollback_intent, clear_rollback_intent,
            recover_rollback_intent)
        write_rollback_intent(self.owner, target_gid, comp_gid,
                              frozen["members"])
        # 6. Canonical rollback to the frozen target. The mediation token
        # is minted HERE — after the live revalidation (commit decision) —
        # and validated inside rollback() before any state access.
        from form.mandell.core_i_recovery import rollback as _rollback
        _mediation = {"operation": ra.ROLLBACK_OPERATION,
                      "owner": self.owner,
                      "generation_id": target_gid,
                      "via": live.get("via"),
                      "compensating_generation_id": comp_gid}
        try:
            restored = _rollback(self.owner, target_gid,
                                 _mediation=_mediation)
        except Exception as exc:
            # Journal preserved: recovery will complete or fail closed.
            return {"ok": False, "reason": "rollback_failed",
                    "detail": f"{type(exc).__name__}: {str(exc)[:200]}",
                    "generation_id": target_gid,
                    "compensating_generation_id": comp_gid}
        # 7. Verify complete restoration before success. The canonical
        # rollback converges live files to the target generation; CURRENT
        # still names the latest committed generation (the safety
        # checkpoint) — that is the existing invariant, preserved.
        # Verification: the restored state loads through the production
        # path, and the live nursery bytes match the target's sealed
        # nursery member exactly.
        try:
            from form import persist_rest
            probe = persist_rest.load(self.owner, activate=False)
            if probe is None:
                raise ValueError("restored program failed to load")
            import hashlib as _hl
            from form.dell_matrix.nursery import owner_nursery_path
            _h = _hl.sha256()
            with open(owner_nursery_path(self.owner), "rb") as _f:
                for _c in iter(lambda: _f.read(65536), b""):
                    _h.update(_c)
            if _h.hexdigest() != frozen["members"].get("nursery"):
                raise ValueError("live nursery does not match target "
                                 "generation member")
        except Exception as exc:
            return {"ok": False, "reason": "restoration_unverified",
                    "detail": f"{type(exc).__name__}: {str(exc)[:200]}",
                    "generation_id": target_gid,
                    "compensating_generation_id": comp_gid}
        # 8. Clear intent; mark this (now stale) instance; receipt.
        clear_rollback_intent(self.owner)
        self._post_rollback_stale = True
        return {"ok": True, "generation_id": target_gid,
                "compensating_generation_id": comp_gid,
                "via": decision.get("via"),
                "restored": True}

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


def open_program(owner: str = "Operator", _nursery=None) -> Program:
    """Open a Program for ``owner``.

    ``_nursery`` is a private injection hook for generation-member staging:
    the provided Nursery is used instead of the owner's live nursery file,
    which is never consulted on that path.
    """
    if _nursery is None:
        return Program(owner=owner)
    prog = Program.__new__(Program)
    prog._init_nursery = _nursery
    try:
        prog.__init__(owner)
    finally:
        try:
            del prog._init_nursery
        except AttributeError:
            pass
    return prog


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
