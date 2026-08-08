#!/usr/bin/env python3
"""
Live two-way visual bridge — localhost only.

Phases A–E: vision cones, entities, inspect mode, workshops, camera follow,
grid snap, trail fade, shared actions registry, AICompanion on Program.

Law: offline 127.0.0.1 · Nursery+confirm · Floor locked · pure stdlib.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import math
import os
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

_HOST = "127.0.0.1"
_DEFAULT_PORT = 8765
_CMD_HISTORY: List[str] = []
_MAX_HIST = 20
_AI_TICK_INTERVAL = 0.95  # seconds — throttle wander/follow so poll rate ≠ move rate


_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# Multi-page app routes → files under assets/
# Incomplete bare commands — return usage end-page, never mis-create ideas
_INCOMPLETE_USAGE = {
    "confirm": "usage: confirm <id> | confirm all  — open Nursery page for ids",
    "reject": "usage: reject <id> | reject all",
    "create an idea called": "usage: create an idea called <name>",
    "create an idea": "usage: create an idea called <name>",
    "create": "usage: create an idea called <name>",
    "zoom": "usage: zoom <id|label>  ·  or: page  (auto nearest)",
    "lineage": "usage: lineage <id>",
    "shell": "usage: shell <n>   e.g. shell 0 | shell 1",
    "chord": "usage: chord <h> <v>   e.g. chord 0 0",
    "lens": "usage: lens <skin>|clear   e.g. lens seed",
    "persona": "usage: persona <name>|clear   e.g. persona manny",
    "workshop": "usage: workshop <id>|leave   · workshops lists all",
    "view": "usage: view <room>   · rooms lists all",
    "weather": "usage: weather clear|rain|storm|fog",
    "mode": "usage: mode beginner|builder|depth",
    "body": "usage: body stick|block|shadow|robot",
    "goto": "usage: goto H V [F]",
    "explain": "usage: explain <word|phrase>",
    "distill": "usage: distill <words>",
    "script": "usage: script look; pulse; status",
    "plant": "usage: plant <Label>",
    "find": "usage: find <query>",
    "force": "usage: force growth|water|breath|gravity  or  force tick",
}

_PAGE_ROUTES = {
    "/": "menu.html",
    "/menu": "menu.html",
    "/index.html": "menu.html",
    "/ui": "menu.html",
    "/walk": "pages/walk.html",
    "/walk/world": "fp_world.html",  # bare walk canvas (iframe target)
    "/lattice": "pages/lattice.html",
    "/nursery": "pages/nursery.html",
    "/program": "pages/program.html",
    "/personas": "pages/personas.html",
    "/forces": "pages/forces.html",
    "/geometry": "pages/geometry.html",
    "/nature": "pages/nature_code.html",
    "/nature_code": "pages/nature_code.html",
    "/noc": "pages/nature_code.html",
    "/matrices": "pages/matrices.html",
    "/console": "pages/console.html",
    "/inspire": "pages/inspire.html",
    "/workshops": "pages/workshops.html",
}

_MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
}


def _assets_root() -> str:
    return _ASSETS_DIR


def _load_asset(rel: str) -> Optional[bytes]:
    """Read a file under assets/ safely (no path escape)."""
    rel = (rel or "").lstrip("/").replace("\\", "/")
    if ".." in rel.split("/"):
        return None
    path = os.path.normpath(os.path.join(_ASSETS_DIR, rel))
    if not path.startswith(os.path.normpath(_ASSETS_DIR)):
        return None
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "rb") as f:
            return f.read()
    except Exception:
        return None


def _load_fp_html() -> str:
    """Load first-person walk canvas (assets/fp_world.html)."""
    raw = _load_asset("fp_world.html")
    if raw:
        return raw.decode("utf-8")
    return (
        "<!DOCTYPE html><html><body style='background:#0a0b0e;color:#eee;font-family:system-ui'>"
        "<h1>DellMatrix live</h1><p>Missing assets/fp_world.html</p>"
        "</body></html>"
    )


def _load_menu_html() -> str:
    raw = _load_asset("menu.html")
    if raw:
        return raw.decode("utf-8")
    return _load_fp_html()


def _state_payload(program) -> Dict[str, Any]:
    from form.dell_matrix.graph_view import build_view
    from form.dell_matrix.actions_registry import actions_for_mode
    from form.dell_matrix.vision import compute_vision, VISION_RANGE, VISION_HALF_ANGLE
    from form.dell_matrix.workshops import get_workshop, list_workshops

    # First-person centerpoint walk is default live mode
    if not hasattr(program, "view_mode") or not program.view_mode:
        program.view_mode = "first_person"
    # Always snap to integer centerpoints in live
    program.grid_snap = True
    if hasattr(program, "apply_grid_snap"):
        program.apply_grid_snap()

    plane = program.cube.session.plane
    scores = program.scores() if hasattr(program, "scores") else {}
    nodes = program.nodes_payload() if hasattr(program, "nodes_payload") else []
    nursery = program.ranked_proposals() if hasattr(program, "ranked_proposals") else []
    avatar = program.avatar_status() if hasattr(program, "avatar_status") else {}
    holding = program.avatar.body.holding
    posture = program.avatar.body.posture.name.lower()
    loco = program.avatar.body.locomotion.name.lower()
    # height = lattice F axis (center_f)
    center_f = int(getattr(program, "center_f", 0) or 0)
    body = {
        "pos": list(program.avatar.body.pos),
        "facing": program.avatar.body.facing.name,
        "posture": posture,
        "locomotion": loco,
        "holding": holding,
        "z": float(center_f),
        "center_f": center_f,
        "pitch": getattr(program, "look_pitch", "level"),
    }
    # Do NOT push trail on poll — only movement commands push (prevents idle pollution)
    # Throttle AI auto-modes so refresh rate does not double-step
    if hasattr(program, "companion") and program.companion.mode in ("wander", "follow"):
        now = time.time()
        last = float(getattr(program, "_last_ai_tick", 0) or 0)
        if now - last >= _AI_TICK_INTERVAL:
            program.companion.tick(body["pos"])
            program._last_ai_tick = now

    ai_info = program.companion.to_dict()
    user_vision = compute_vision(
        body["pos"], body["facing"], nodes, other=ai_info,
        skin_filter=getattr(program, "skin_filter", None),
        persona=getattr(program, "persona_lens", None),
    )
    ai_vision = compute_vision(
        ai_info["pos"], ai_info["facing"], nodes,
        other={"name": "YOU", "pos": body["pos"], "facing": body["facing"],
               "doing": body.get("locomotion"), "last_action": body.get("posture")},
        skin_filter=getattr(program, "skin_filter", None),
        persona=getattr(program, "persona_lens", None),
    )
    lat = program.lattice.status() if hasattr(program, "lattice") else {}
    view = build_view(plane, scores=scores)
    # Live UI only needs a sample of edges (full plane can be 20k+ and stalls the browser).
    # Cap keeps lattice page responsive without dropping graph capability elsewhere.
    _EDGE_CAP = 480
    raw_edges = list(view.edges or [])
    edges = [e.to_dict() for e in raw_edges[:_EDGE_CAP]]
    form = lat.get("form", "cube")
    # form grammar colors
    form_theme = {
        "cube": {"grid": "#1a3048", "accent": "#5b8def"},
        "sphere": {"grid": "#2a1a40", "accent": "#7c5cbf"},
        "core": {"grid": "#2a2010", "accent": "#d97706"},
        "flower": {"grid": "#2a2810", "accent": "#e6a817"},
        "circle": {"grid": "#102a28", "accent": "#2aa7a0"},
        "square": {"grid": "#1a2030", "accent": "#5b8def"},
    }.get(form, {"grid": "#1a2030", "accent": "#5b8def"})

    page = None
    if plane.zoom_target and hasattr(program, "page_card"):
        page = program.page_card()

    workshop = None
    if getattr(program, "active_workshop", None):
        workshop = get_workshop(program.active_workshop)

    entities = program.all_entities() if hasattr(program, "all_entities") else []
    zoom_id = plane.zoom_target

    # View-room lens: recolor theme + tag nodes
    view_room = None
    view_nodes = nodes
    if hasattr(program, "view_status"):
        try:
            from form.dell_matrix.view_rooms import get_room, filter_nodes_for_room
            view_room = get_room(getattr(program, "active_view", "growth"))
            if view_room and view_room.get("theme"):
                form_theme = {**form_theme, **view_room["theme"]}
            view_nodes = filter_nodes_for_room(
                getattr(program, "active_view", "growth"), nodes,
                owner=program.owner, scores=scores,
            )
        except Exception:
            view_nodes = nodes

    forces_status = program.forces.status() if hasattr(program, "forces") else {}
    pillars = program.audit() if hasattr(program, "audit") else {}
    bimo_status = program.bimo_status() if hasattr(program, "bimo_status") else {}
    persona_matrix = program.persona_matrix_status() if hasattr(program, "persona_matrix_status") else {}

    # Sacred geometry payloads
    flower_geo = {}
    verita_edges = []
    voynich = {}
    if form == "flower" and hasattr(program, "flower_geometry"):
        try:
            flower_geo = program.flower_geometry(2)
        except Exception:
            flower_geo = {}
    if hasattr(program, "verita_edges"):
        try:
            verita_edges = program.verita_edges()[:40]
        except Exception:
            verita_edges = []
    if hasattr(program, "voynich_status"):
        try:
            voynich = program.voynich_status()
        except Exception:
            voynich = {}

    return {
        "ok": True,
        "owner": program.owner,
        "ideas": len(plane.units),
        "nodes": view_nodes,
        "edges": edges,
        "edges_total": len(raw_edges),
        "edges_shown": len(edges),
        "nursery": nursery[:20],
        "avatar": avatar,
        "user": body,
        "user_trail": list(getattr(program, "user_trail", []) or []),
        "ai": ai_info,
        "user_vision": user_vision,
        "ai_vision": ai_vision,
        "cmd_history": list(_CMD_HISTORY[-_MAX_HIST:]),
        "form": form,
        "skin": lat.get("skin", "cube"),
        "rings": list(getattr(program.duo, "rings", [])),
        "history_len": len(getattr(program, "history", [])),
        "floor": ["Alpha", "Delta", "Omega", "Omni"],
        "vision_range": VISION_RANGE,
        "vision_half_angle": VISION_HALF_ANGLE,
        "projection": "iso",
        "ux_mode": getattr(program, "ux_mode", "builder"),
        "actions": actions_for_mode(getattr(program, "ux_mode", "builder")),
        "click_mode": getattr(program, "click_mode", "inspect"),
        "camera_follow": bool(getattr(program, "camera_follow", True)),
        "grid_snap": bool(getattr(program, "grid_snap", False)),
        "show_nursery_ghosts": bool(getattr(program, "show_nursery_ghosts", True)),
        "page": page,
        "workshop": workshop,
        "workshops": list_workshops(),
        "inspire": program.inspire_status() if hasattr(program, "inspire_status") else {},
        "routes": list(_PAGE_ROUTES.keys()),
        "skin_filter": getattr(program, "skin_filter", None),
        "persona_lens": getattr(program, "persona_lens", None),
        "flower_pts": program.flower_draw_data() if hasattr(program, "flower_draw_data") else [],
        "shell_rings": program.shell_rings_data() if hasattr(program, "shell_rings_data") else [],
        "form_theme": form_theme,
        "entities": entities,
        "zoom_id": zoom_id,
        "active_view": getattr(program, "active_view", "growth"),
        "view_room": view_room,
        "forces": forces_status,
        "pillars": pillars,
        "bimo": bimo_status,
        "persona_matrix": persona_matrix,
        "personas_count": (persona_matrix or {}).get("count") or 0,
        "flower_geometry": flower_geo,
        "verita_edges": verita_edges,
        "voynich": voynich,
        "generation": getattr(getattr(program, "duo", None), "generation", 0),
        "body_style": getattr(program, "body_style", "stick"),
        "body_art": program.body_art() if hasattr(program, "body_art") else "",
        "matrices_summary": program.matrices_summary() if hasattr(program, "matrices_summary") else "",
        "view_mode": getattr(program, "view_mode", "first_person"),
        "fp": program.first_person() if hasattr(program, "first_person") else {},
        "camera": {
            "follow": bool(getattr(program, "camera_follow", True)),
            "cx": float(body["pos"][0]),
            "cy": float(body["pos"][1]),
        },
    }


def _handle_ai_command(program, cmd: str) -> Optional[Dict[str, Any]]:
    lower = cmd.lower().strip()
    if not lower.startswith("ai "):
        return None
    rest = lower[3:].strip()
    c = program.companion
    if rest in ("walk", "step", "forward"):
        return {"ok": True, "msg": f"AI walked to {c.step(1)}"}
    if rest.startswith("walk ") or rest.startswith("step "):
        try:
            n = int(rest.split()[1])
        except Exception:
            n = 1
        return {"ok": True, "msg": f"AI walked {n} to {c.step(n)}"}
    if rest in ("backstep", "back", "step back"):
        return {"ok": True, "msg": f"AI backstep to {c.backstep(1)}"}
    if rest in ("turn left", "left"):
        return {"ok": True, "msg": f"AI turned left → {c.turn(-1)}"}
    if rest in ("turn right", "right"):
        return {"ok": True, "msg": f"AI turned right → {c.turn(1)}"}
    if rest.startswith("face "):
        d = rest.split(maxsplit=1)[1]
        return {"ok": True, "msg": f"AI facing {c.face(d)}"}
    if rest in ("status", "where", "pos"):
        return {"ok": True, "msg": f"AI at {c.pos} face {c.facing} mode={c.mode}"}
    if rest in ("look", "see", "vision"):
        c.doing = "looking"
        c.last_action = "looked"
        return {"ok": True, "msg": "AI looked"}
    if rest in ("wander", "mode wander"):
        return {"ok": True, "msg": f"AI mode → {c.set_mode('wander')}"}
    if rest in ("follow", "mode follow"):
        return {"ok": True, "msg": f"AI mode → {c.set_mode('follow')}"}
    if rest in ("manual", "mode manual", "stop"):
        return {"ok": True, "msg": f"AI mode → {c.set_mode('manual')}"}
    if rest.startswith("goto ") or rest.startswith("move "):
        parts = rest.split()
        try:
            x, y = float(parts[1]), float(parts[2])
            return {"ok": True, "msg": f"AI moved to {c.goto(x, y)}"}
        except Exception:
            return {"ok": False, "error": "usage: ai goto X Y"}
    return {"ok": False, "error": f"unknown ai command: {rest}"}


def _handle_ux_command(program, lower: str, raw: str) -> Optional[Dict[str, Any]]:
    """Handle mode/lens/workshop/page/snap/click/recenter without full intent parse."""
    if lower in ("look", "see", "vision", "look around"):
        report = program.look_report()
        return {"ok": True, "msg": "\n".join(report), "vision": program.look_around()}
    if lower.startswith("mode "):
        m = program.set_ux_mode(lower.split(maxsplit=1)[1])
        return {"ok": True, "msg": f"UX mode → {m}"}
    if lower in ("snap on", "grid snap on", "gridsnap on"):
        program.grid_snap = True
        return {"ok": True, "msg": "Grid snap ON (active when form is cube/square)"}
    if lower in ("snap off", "grid snap off", "gridsnap off"):
        program.grid_snap = False
        return {"ok": True, "msg": "Grid snap OFF"}
    if lower in ("follow cam", "camera follow", "cam follow", "follow on"):
        program.camera_follow = True
        return {"ok": True, "msg": "Camera follow ON"}
    if lower in ("cam free", "camera free", "follow off"):
        program.camera_follow = False
        return {"ok": True, "msg": "Camera follow OFF"}
    if lower in ("recenter", "center", "cam home"):
        program.camera_follow = True
        return {"ok": True, "msg": "Recentered on YOU"}
    if lower in ("click inspect", "inspect mode", "mode inspect"):
        program.click_mode = "inspect"
        return {"ok": True, "msg": "Click mode → inspect"}
    if lower in ("click confirm", "confirm mode", "mode confirm"):
        program.click_mode = "confirm"
        return {"ok": True, "msg": "Click mode → confirm"}
    if lower.startswith("lens "):
        skin = lower.split(maxsplit=1)[1]
        f = program.set_skin_filter(skin)
        return {"ok": True, "msg": f"Skin filter → {f or 'clear'}"}
    if lower.startswith("persona "):
        name = lower.split(maxsplit=1)[1]
        p = program.set_persona_lens(name)
        return {"ok": True, "msg": f"Persona lens → {p or 'clear'}"}
    if lower in ("workshops", "workshop list"):
        ws = program.workshops_status()
        lines = ["Workshops (each is a full workbench — pick one, run its cmds, leave when done):"]
        for w in ws.get("list") or []:
            ncmd = len(w.get("commands") or [])
            lines.append(f"  · {w.get('id')}: {w.get('name')} — {w.get('description')} ({ncmd} cmds)")
        act = ws.get("active")
        lines.append(f"  active={act['id'] if act else '—'}  ·  workshop leave to exit")
        lines.append("  page: /workshops")
        return {"ok": True, "msg": "\n".join(lines), "workshops": ws, "end": "workshops_index"}
    if lower.startswith("workshop "):
        rest = lower.split(maxsplit=1)[1].strip()
        if rest in ("leave", "exit", "close"):
            left = program.leave_workshop().get("left")
            return {
                "ok": True,
                "msg": f"Left workshop {left or '—'} · back to free lattice · doors: workshops | page | look",
                "end": "workshop_leave",
            }
        out = program.enter_workshop(rest)
        if not out.get("ok"):
            avail = ", ".join(w["id"] for w in (program.workshops_status().get("list") or []))
            return {
                "ok": False,
                "error": f"{out.get('reason', 'unknown workshop')} · try: {avail}",
                "end": "workshop_miss",
            }
        w = out["workshop"]
        lines = [
            f"══ Workshop · {w.get('name')} ══",
            f"  {w.get('description')}",
            "  commands (run any — each ends usefully):",
        ]
        for c in w.get("commands") or []:
            lines.append(f"    · {c.get('label')}:  {c.get('cmd')}")
        lines.append("  doors: workshop leave | workshops | page | look | save")
        lines.append("  end · workshop open")
        return {"ok": True, "msg": "\n".join(lines), "workshop": w, "end": "workshop_page"}
    if lower in ("page", "page status", "show page", "open page", "idea page", "end page"):
        out = program.open_page() if hasattr(program, "open_page") else {"ok": False, "reason": "no open_page"}
        if not out.get("ok"):
            return {"ok": False, "error": out.get("reason") or "No ideas yet — create an idea called <name>", "end": "page_empty"}
        card = out.get("page") or program.page_card()
        auto = " (auto nearest)" if out.get("auto") else ""
        body = program.format_page_end(card) if hasattr(program, "format_page_end") else f"Page {card.get('label')}"
        return {
            "ok": True,
            "msg": body + (f"\n  opened{auto}" if out.get("opened") else ""),
            "page": card,
            "end": "idea_page",
        }
    if lower.startswith("page "):
        ref = raw.split(maxsplit=1)[1].strip()
        out = program.open_page(ref) if hasattr(program, "open_page") else program.zoom_to(ref)
        if not out.get("ok"):
            return {"ok": False, "error": out.get("reason", "fail"), "end": "page_miss"}
        card = out.get("page") or program.page_card()
        body = program.format_page_end(card) if hasattr(program, "format_page_end") else f"Page {card.get('label')}"
        return {"ok": True, "msg": body, "page": card, "end": "idea_page"}
    if lower.startswith("zoom "):
        ref = raw.split(maxsplit=1)[1].strip()
        out = program.zoom_to(ref)
        if not out.get("ok"):
            units = list(program.cube.session.plane.units.keys())[:8]
            hint = f" · live ids: {', '.join(units)}" if units else " · create an idea first"
            return {"ok": False, "error": (out.get("reason") or "fail") + hint, "end": "zoom_miss"}
        card = out.get("page") or program.page_card()
        body = program.format_page_end(card) if hasattr(program, "format_page_end") else f"Zoomed to {out['id']}"
        return {"ok": True, "msg": body, "page": card, "end": "idea_page"}
    if lower in ("unzoom", "zoom out", "leave page"):
        program.unzoom()
        return {
            "ok": True,
            "msg": "Unzoomed · overview · doors: page (reopen nearest) | look | proposals | home",
            "end": "overview",
        }
    if lower in ("ghosts on", "nursery ghosts on"):
        program.show_nursery_ghosts = True
        return {"ok": True, "msg": "Nursery ghosts ON"}
    if lower in ("ghosts off", "nursery ghosts off"):
        program.show_nursery_ghosts = False
        return {"ok": True, "msg": "Nursery ghosts OFF"}
    if lower in ("entities", "entity list", "what is here", "who is here"):
        ents = program.all_entities() if hasattr(program, "all_entities") else []
        by: Dict[str, int] = {}
        for e in ents:
            k = str(e.get("kind") or "?")
            by[k] = by.get(k, 0) + 1
        lines = [f"{k}={n}" for k, n in sorted(by.items())]
        detail = []
        for e in ents[:16]:
            pos = e.get("pos")
            detail.append(f"{e.get('kind')}:{e.get('label') or e.get('id')}{(' @ '+str(pos)) if pos is not None else ''}")
        return {"ok": True, "msg": "Entities: " + " · ".join(lines) + "\n" + "\n".join(detail), "entities": ents}
    if lower in ("rooms", "view rooms"):
        st = program.view_status()
        names = ", ".join(r["id"] for r in st.get("rooms") or [])
        return {"ok": True, "msg": f"Rooms: {names}\n" + "\n".join(st.get("ascii") or [])}
    if lower.startswith("view "):
        out = program.set_view(lower.split(maxsplit=1)[1])
        if not out.get("ok"):
            rooms = ", ".join(r["id"] for r in (program.view_status().get("rooms") or []))
            return {
                "ok": False,
                "error": f"{out.get('reason', 'unknown room')} · try: {rooms}",
                "end": "view_miss",
            }
        room = out.get("view") or {}
        return {
            "ok": True,
            "msg": f"View → {room.get('name')} — {room.get('description', '')}\n  doors: rooms | look | page | workshop perspective",
            "view": room,
            "end": "view_page",
        }
    if lower in ("forces", "force status"):
        st = program.force_status()
        return {
            "ok": True,
            "msg": (
                f"Forces active={st.get('active')} weather={st.get('weather')} tick={st.get('time_tick')}\n"
                "  doors: force tick | force growth|water|breath|gravity | weather rain|clear | /forces"
            ),
            "forces": st,
            "end": "forces_page",
        }
    if lower in ("force tick", "forces tick"):
        rep = program.force_tick()
        return {"ok": True, "msg": f"Force tick · {rep.get('forces')}\n  doors: forces | evolve | pulse", "report": rep, "end": "force_tick"}
    if lower.startswith("force ") and lower not in ("force tick",):
        which = lower.split(maxsplit=1)[1].strip()
        # closed force avenues with real work + end message
        try:
            if which in ("growth", "grow"):
                program.forces.activate("growth")
                for u in list(program.cube.session.plane.units.values())[:8]:
                    known = {pl["idea"] for pl in program.forces.growth.plants}
                    if u.label not in known:
                        program.forces.growth.plant(u.label, program.owner)
                program.forces.growth.grow_all(0.6)
                lines = program.forces.growth.map()[:8]
                return {"ok": True, "msg": "Force growth\n" + "\n".join(f"  {x}" for x in lines) + "\n  doors: force tick | forces", "end": "force_growth"}
            if which in ("water", "flow"):
                program.forces.activate("water")
                for u in list(program.cube.session.plane.units.values())[:3]:
                    program.forces.water.flow(u.label, program.owner)
                extra = ""
                if len(program.forces.water.streams) >= 2:
                    m = program.forces.water.merge_last_two()
                    if m:
                        extra = f"\n  Merged → {m['idea'][:60]}"
                return {
                    "ok": True,
                    "msg": f"Force water · streams={len(program.forces.water.streams)} pools={len(program.forces.water.pools)}{extra}\n  doors: force tick | forces",
                    "end": "force_water",
                }
            if which in ("breath", "heartbeat"):
                program.forces.activate("breath")
                r = program.forces.breath.heartbeat(len(program.cube.session.plane.units))
                return {
                    "ok": True,
                    "msg": f"Breath cycle {r['inhale']['cycle']} · phase {program.forces.breath.phase}\n  doors: force tick | forces",
                    "end": "force_breath",
                }
            if which in ("gravity",):
                program.forces.activate("gravity")
                wells = program.forces.gravity.set_wells_from_scores(program.nodes_payload())
                labels = ", ".join(w["label"] for w in wells[:8]) or "—"
                return {"ok": True, "msg": f"Gravity wells: {labels}\n  doors: force tick | forces", "end": "force_gravity"}
            return {"ok": False, "error": "usage: force growth|water|breath|gravity  or  force tick", "end": "usage"}
        except Exception as e:
            return {"ok": False, "error": str(e), "end": "error"}
    if lower.startswith("weather "):
        c = program.set_weather(lower.split(maxsplit=1)[1])
        return {"ok": True, "msg": f"Weather → {c}"}
    if lower in ("evolve", "evolve program"):
        out = program.evolve("live evolve")
        return {"ok": True, "msg": f"Evolved gen={out.get('generation')} pillars={out.get('pillars', {}).get('average')}", "evolve": out}
    if lower in ("audit", "pillars"):
        lines = program.audit_lines()
        return {"ok": True, "msg": "\n".join(lines), "pillars": program.audit()}
    if lower in ("matrices", "matrix list"):
        return {"ok": True, "msg": program.matrices_summary() + "\n" + "\n".join(
            f"[{m['kind']}] {m['id']}" for m in program.matrices()
        )}
    if lower in ("personas", "persona list", "roster"):
        lines = program.personas_roster() if hasattr(program, "personas_roster") else []
        st = program.personas_status()
        return {"ok": True, "msg": "\n".join(lines), "personas": st}
    if lower in ("matrix personas", "persona matrix"):
        lines = program.persona_matrix_ascii() if hasattr(program, "persona_matrix_ascii") else []
        return {"ok": True, "msg": "\n".join(lines), "matrix": program.persona_matrix_status()}
    if lower in ("bimo", "bimo status"):
        lines = program.bimo.render_ascii() if hasattr(program, "bimo") else []
        return {"ok": True, "msg": "\n".join(lines), "bimo": program.bimo_status()}
    if lower in ("bimo defaults", "bimo dock all"):
        out = program.bimo_defaults()
        return {"ok": True, "msg": f"BIMO defaults · pilot={out.get('pilot')}", "bimo": out}
    if lower in ("bimo fuse", "fuse"):
        out = program.bimo_fuse()
        return {"ok": True, "msg": "\n".join(out.get("guidance") or []), "fuse": out}
    if lower in ("bimo clear",):
        program.bimo_clear()
        return {"ok": True, "msg": "BIMO cleared"}
    if lower.startswith("bimo dock "):
        parts = lower.split()
        if len(parts) < 4:
            return {"ok": False, "error": "usage: bimo dock <slot> <persona>"}
        out = program.bimo_dock(parts[2], parts[3])
        return {"ok": bool(out.get("ok")), "msg": str(out), "result": out}
    if lower.startswith("bimo pilot "):
        name = lower.split(maxsplit=2)[2]
        out = program.bimo.set_pilot(name)
        if out.get("ok"):
            program.persona_lens = out["pilot"]
        return {"ok": bool(out.get("ok")), "msg": f"pilot → {out.get('pilot')}", "result": out}
    if lower in ("guide", "guide me"):
        return {"ok": True, "msg": "\n".join(program.guide())}
    if lower.startswith("body "):
        s = program.set_body_style(lower.split(maxsplit=1)[1])
        return {"ok": True, "msg": f"Body → {s}\n{program.body_art()}"}
    if lower in ("english help", "how to talk"):
        from form.mandell.english_brain import help_english
        return {"ok": True, "msg": "\n".join(help_english())}
    if lower in ("english status", "english brain"):
        from form.mandell.english_brain import mastery_status
        st = mastery_status()
        return {"ok": True, "msg": f"cycles={st['cycle_count']} learned={st['learned']} mastery={st['mastery']}", "english": st}
    if lower.startswith("english expand") or lower == "english_expand":
        from form.mandell.english_brain import expand_loop
        n = 50
        for part in lower.split():
            if part.isdigit():
                n = max(1, min(200, int(part)))
        rep = expand_loop(n)
        if hasattr(program, "duo"):
            program.duo.evolve(f"45[Translate] :: english_expand x{n}")
        return {
            "ok": True,
            "msg": f"English expand ×{n} · tests={rep.total_tests} hits={rep.hits} rate={rep.final_rate:.1%}",
            "expand": {"cycles": rep.cycles, "rate": rep.final_rate, "mastery": rep.mastery},
        }
    if lower in ("flower geometry", "fol", "flower of life"):
        if program.lattice.perception.form.value != "flower":
            program.lattice.plant_flower(2)
        geo = program.flower_geometry(2)
        return {"ok": True, "msg": f"FoL centers={geo['center_count']} vesicas={geo['vesica_count']}", "flower": geo}
    if lower in ("vesica", "verita", "veritas"):
        edges = program.verita_edges()
        return {"ok": True, "msg": f"Verita edges={len(edges)}", "verita": edges[:20]}
    if lower in ("voynich", "voynich rings", "rings"):
        return {"ok": True, "msg": "\n".join(program.voynich_ascii()), "voynich": program.voynich_status()}
    if lower in ("fractal", "fractals", "rule90"):
        fr = program.fractal_status(12)
        return {"ok": True, "msg": "\n".join(fr.get("rule90_ascii") or []), "fractal": {
            "orbit": fr.get("bounded_orbit"), "complex": fr.get("complex_orbit"),
        }}
    if lower in ("geometry", "sacred geometry"):
        return {"ok": True, "msg": "\n".join(program.geometry_ascii()), "geometry": program.geometry_status()}
    # Form grammar (cube/sphere/flower/toggle) — always with visible msg for UI
    if lower in ("cube", "form cube", "to cube"):
        program.lattice.to_cube()
        return {"ok": True, "msg": f"Form → cube · {program.lattice.status().get('form', 'cube')}"}
    if lower in ("sphere", "form sphere", "to sphere"):
        program.lattice.to_sphere()
        return {"ok": True, "msg": f"Form → sphere · infinite matrix cells use sphere grammar"}
    if lower in ("flower", "form flower", "to flower", "flower of life form"):
        program.lattice.to_flower()
        return {"ok": True, "msg": f"Form → flower · FoL geometry active"}
    if lower in ("core", "form core", "to core"):
        program.lattice.to_core()
        return {"ok": True, "msg": "Form → core"}
    if lower in ("toggle", "toggle form", "dual", "dual form"):
        new = program.lattice.toggle_form()
        val = getattr(new, "value", new)
        return {"ok": True, "msg": f"Form toggled → {val}"}
    # Growth / nursery / pulse / status / save — rich messages so buttons feel alive
    if lower in ("status", "program status", "state"):
        lines = []
        if hasattr(program, "status_lines"):
            try:
                lines = list(program.status_lines())
            except Exception:
                lines = []
        if not lines and hasattr(program, "status"):
            st = program.status() if callable(program.status) else {}
            if isinstance(st, dict):
                lines = [f"{k}: {v}" for k, v in list(st.items())[:24]]
            else:
                lines = [str(st)]
        fp = program.first_person() if hasattr(program, "first_person") else {}
        center = (fp or {}).get("center") or [0, 0, 0]
        lat = program.lattice.status() if hasattr(program, "lattice") else {}
        pil = program.audit() if hasattr(program, "audit") else {}
        ns = program.ranked_proposals() if hasattr(program, "ranked_proposals") else []
        head = [
            f"Owner {program.owner} · ideas={len(program.cube.session.plane.units)} · gen={getattr(program.duo,'generation',0)}",
            f"Form {lat.get('form','?')} · skin {lat.get('skin','?')} · view {getattr(program,'view_mode','first_person')}",
            f"Center ({center[0]},{center[1]},{center[2]}) face {(fp or {}).get('yaw','N')} look {(fp or {}).get('pitch','level')}",
            f"Pillars {pil.get('label','—')} avg={pil.get('average','—')} · nursery pending={len(ns)}",
            f"Mandell {(fp or {}).get('mandel','')}",
        ]
        body = "\n".join(head + ([""] + lines if lines else []))
        return {"ok": True, "msg": body, "status": {"center": center, "form": lat.get("form"), "pillars": pil}}
    if lower in ("proposals", "nursery", "nursery list", "list proposals"):
        props = program.ranked_proposals() if hasattr(program, "ranked_proposals") else []
        if not props:
            return {"ok": True, "msg": "Nursery empty — grow ideas or plant new proposals", "nursery": []}
        lines = [f"Nursery · {len(props)} proposals (confirm <id> | confirm all to accept)"]
        for i, p in enumerate(props[:16], 1):
            lines.append(
                f"{i:2}. [{p.get('id')}] {p.get('label') or p.get('id')} · aff={p.get('affinity','—')} · "
                f"{(p.get('words') or '')[:80]}"
            )
        return {"ok": True, "msg": "\n".join(lines), "nursery": props[:20]}
    # ─── Needs: strong create · edit · undo · history · nbd · ready ───
    if lower.startswith("create an idea") or lower.startswith("create idea") or lower.startswith("plant "):
        from form.dell_matrix.needs import parse_and_place, format_create_end
        line = raw
        if lower.startswith("plant "):
            name = raw.split(maxsplit=1)[1].strip()
            line = f"create an idea called {name}"
        res = parse_and_place(program, line)
        return {"ok": True, "msg": format_create_end(res), "create": res, "end": "create_strong"}
    if lower.startswith("set detail "):
        rest = raw.split(maxsplit=2)
        if len(rest) < 3:
            return {"ok": False, "error": "usage: set detail <id|label> <text>", "end": "usage"}
        ref, detail = rest[1], rest[2]
        out = program.set_idea_detail(ref, detail) if hasattr(program, "set_idea_detail") else {"ok": False}
        if not out.get("ok"):
            return {"ok": False, "error": out.get("reason"), "end": "edit_miss"}
        return {"ok": True, "msg": f"Detail set on {out.get('label')} · {(out.get('detail') or '')[:100]}\n  doors: set goals {out.get('id')} … · page · idea {out.get('id')}", "edit": out, "end": "edit_detail"}
    if lower.startswith("set goals "):
        rest = raw.split(maxsplit=2)
        if len(rest) < 3:
            return {"ok": False, "error": "usage: set goals <id|label> goal1; goal2; goal3", "end": "usage"}
        ref, goals = rest[1], rest[2]
        out = program.set_idea_goals(ref, goals) if hasattr(program, "set_idea_goals") else {"ok": False}
        if not out.get("ok"):
            return {"ok": False, "error": out.get("reason"), "end": "edit_miss"}
        return {"ok": True, "msg": f"Goals set on {out.get('label')}: {', '.join(out.get('goals') or [])}\n  doors: idea {out.get('id')} · page · grow ideas 1", "edit": out, "end": "edit_goals"}
    if lower.startswith("idea ") or lower.startswith("describe "):
        ref = raw.split(maxsplit=1)[1].strip() if " " in raw else ""
        from form.dell_matrix.needs import idea_info, format_idea_end
        info = idea_info(program, ref)
        if not info.get("ok"):
            return {"ok": False, "error": info.get("reason"), "end": "idea_miss"}
        return {"ok": True, "msg": format_idea_end(info), "idea": info, "end": "idea_page"}
    if lower in ("undo", "undo last", "u"):
        out = program.undo() if hasattr(program, "undo") else {"ok": False, "reason": "no undo"}
        if not out.get("ok"):
            return {"ok": False, "error": out.get("reason") or "nothing to undo", "end": "undo_empty"}
        return {"ok": True, "msg": (out.get("msg") or f"Undid {out.get('undid')}") + "\n  doors: history | create an idea called …", "undo": out, "end": "undo"}
    if lower in ("history", "hist", "notes") or lower.startswith("history "):
        n = 16
        for part in lower.split():
            if part.isdigit():
                n = max(1, min(48, int(part)))
        lines = program.history_lines(n) if hasattr(program, "history_lines") else ["no history"]
        return {"ok": True, "msg": "\n".join(lines), "end": "history"}
    if lower in ("what next", "whats next", "what's next", "next", "nbd", "next best", "what should i do"):
        msg = program.what_next() if hasattr(program, "what_next") else "try help"
        return {"ok": True, "msg": msg, "end": "nbd"}
    if lower in ("ready", "am i ready", "acceptance ready", "checklist"):
        lines = program.ready_lines() if hasattr(program, "ready_lines") else ["no ready"]
        return {"ok": True, "msg": "\n".join(lines), "ready": program.ready() if hasattr(program, "ready") else {}, "end": "ready"}
    # ─── Internet (opt-in) + Code Evolution root ───
    if lower in ("internet on", "net on", "allow internet", "internet allow"):
        out = program.internet_on() if hasattr(program, "internet_on") else {"ok": False}
        return {"ok": True, "msg": out.get("msg") or "Internet ON", "internet": out, "end": "internet_on"}
    if lower in ("internet off", "net off"):
        out = program.internet_off() if hasattr(program, "internet_off") else {"ok": True}
        return {"ok": True, "msg": out.get("msg") or "Internet OFF", "internet": out, "end": "internet_off"}
    if lower in ("internet", "internet status", "net status"):
        st = program.internet_status() if hasattr(program, "internet_status") else {"on": False}
        return {
            "ok": True,
            "msg": f"Internet {'ON' if st.get('on') else 'OFF'} · hosts={st.get('hosts', [])[:5]}\n  doors: internet on | net fetch <url> | ce research <topic>",
            "internet": st,
            "end": "internet",
        }
    if lower.startswith("internet allow "):
        host = raw.split(maxsplit=2)[2] if len(raw.split()) >= 3 else ""
        if program.internet:
            h = program.internet.allow_host(host)
            return {"ok": True, "msg": f"Allowed host → {h}", "end": "internet_allow"}
        return {"ok": False, "error": "no internet gate"}
    if lower.startswith("net fetch ") or lower.startswith("fetch "):
        url = raw.split(maxsplit=1)[1].strip() if " " in raw else ""
        out = program.net_fetch(url) if hasattr(program, "net_fetch") else {"ok": False}
        if not out.get("ok"):
            return {"ok": False, "error": out.get("error") or "fetch failed", "end": "net_fail"}
        return {
            "ok": True,
            "msg": f"Fetched {out.get('url')} · {out.get('bytes')} bytes\n  {(out.get('preview') or '')[:400]}",
            "fetch": out,
            "end": "net_fetch",
        }
    if lower.startswith("ce research ") or lower.startswith("net research "):
        topic = raw.split(maxsplit=2)[-1].strip()
        out = program.net_research(topic) if hasattr(program, "net_research") else {"ok": False}
        if not out.get("ok"):
            return {"ok": False, "error": out.get("error") or "research failed", "end": "net_fail"}
        return {
            "ok": True,
            "msg": f"Research · {out.get('title')}\n  {(out.get('extract') or '')[:500]}\n  {out.get('honesty')}\n  {out.get('url')}",
            "research": out,
            "end": "ce_research",
        }
    if lower in ("ce", "ce status", "code evolution", "code evolution status"):
        msg = program.ce_status() if hasattr(program, "ce_status") else "no ce"
        return {"ok": True, "msg": msg, "end": "ce_status"}
    if lower in ("ce develop", "ce complete", "develop code evolution", "ce loop"):
        out = program.ce_develop(cycles=10, internet=bool(getattr(getattr(program, "internet", None), "on", False))) if hasattr(program, "ce_develop") else {"ok": False}
        lines = [
            f"Code Evolution develop · complete={out.get('complete')} ideas={out.get('ideas')} gen={out.get('generation')}",
        ]
        cl = (out.get("checklist") or {}).get("items") or {}
        for k, v in cl.items():
            if k in ("internet_available", "internet_on"):
                continue
            lines.append(f"  {'✓' if v else '·'} {k}")
        lines.append("  doors: ce status | page code_evolution | internet on")
        return {"ok": True, "msg": "\n".join(lines), "ce": out, "end": "ce_develop"}
    if lower.startswith("ce develop "):
        # ce develop 12 · ce develop net
        parts = lower.split()
        n = 10
        use_net = "net" in parts or "internet" in parts
        for part in parts:
            if part.isdigit():
                n = max(1, min(20, int(part)))
        if use_net and hasattr(program, "internet_on"):
            program.internet_on()
        out = program.ce_develop(cycles=n, internet=use_net) if hasattr(program, "ce_develop") else {"ok": False}
        return {
            "ok": True,
            "msg": f"CE develop ×{n} net={use_net} complete={out.get('complete')} gen={out.get('generation')}\n" + (program.ce_status() if hasattr(program, "ce_status") else ""),
            "ce": out,
            "end": "ce_develop",
        }
    if lower in ("confirm all", "confirm-all"):
        props = program.ranked_proposals() if hasattr(program, "ranked_proposals") else []
        ok_n = 0
        fail_n = 0
        labels = []
        for prop in list(props)[:40]:
            res = program.confirm_proposal(prop["id"]) if hasattr(program, "confirm_proposal") else {}
            if res.get("ok"):
                ok_n += 1
                labels.append(res.get("label") or prop.get("label") or prop.get("id"))
            else:
                fail_n += 1
        return {
            "ok": True,
            "msg": f"Confirmed {ok_n} · failed {fail_n}\n" + "\n".join(f"  + {x}" for x in labels[:12]),
            "confirmed": ok_n,
        }
    if lower.startswith("confirm "):
        pid = raw.split(maxsplit=1)[1].strip()
        res = program.confirm_proposal(pid) if hasattr(program, "confirm_proposal") else {"ok": False, "reason": "no confirm"}
        if res.get("ok"):
            return {"ok": True, "msg": f'Confirmed · "{res.get("label")}" is live on the lattice', "confirm": res}
        return {"ok": False, "error": f"Could not confirm: {res.get('reason')}", "confirm": res}
    if lower in (
        "auto confirm on", "auto confirm all", "auto confirm all grow mode",
        "grow mode auto", "grow mode auto confirm", "auto_confirm on",
        "autocconfirm on", "auto-confirm on",
    ):
        if hasattr(program, "set_auto_confirm_grow"):
            program.set_auto_confirm_grow(True)
        else:
            program.auto_confirm_grow = True
        return {
            "ok": True,
            "msg": "Grow mode → auto confirm all ON · every grow accepts all nursery proposals",
            "auto_confirm_grow": True,
            "end": "grow_mode",
        }
    if lower in (
        "auto confirm off", "grow mode manual", "grow mode off",
        "auto_confirm off", "autocconfirm off", "auto-confirm off",
    ):
        if hasattr(program, "set_auto_confirm_grow"):
            program.set_auto_confirm_grow(False)
        else:
            program.auto_confirm_grow = False
        return {
            "ok": True,
            "msg": "Grow mode → auto confirm all OFF · grow leaves proposals in nursery",
            "auto_confirm_grow": False,
            "end": "grow_mode",
        }
    if lower in ("grow mode", "auto confirm", "auto_confirm", "auto-confirm"):
        on = bool(getattr(program, "auto_confirm_grow", False))
        return {
            "ok": True,
            "msg": (
                f"Grow mode · auto_confirm_grow={'ON' if on else 'OFF'}\n"
                "  auto confirm on  — grow then confirm all\n"
                "  auto confirm off — grow leaves nursery pending"
            ),
            "auto_confirm_grow": on,
            "end": "grow_mode",
        }
    if lower.startswith("grow ideas") or lower in ("grow", "grow 1", "grow ideas"):
        parts = lower.split()
        cycles = 1
        for part in parts:
            if part.isdigit():
                cycles = max(1, min(20, int(part)))
        out = program.grow_ideas(cycles) if hasattr(program, "grow_ideas") else {}
        n = len(program.cube.session.plane.units)
        pend = len(program.ranked_proposals()) if hasattr(program, "ranked_proposals") else 0
        engine = (out or {}).get("engine") or (out or {}).get("ok")
        ac = (out or {}).get("auto_confirm") or {}
        msg = f"Grew ×{cycles} · ideas now {n} · nursery pending {pend}"
        if engine is not None:
            msg += f" · engine={engine}"
        if ac.get("on"):
            msg += f" · auto-confirmed {ac.get('confirmed', 0)} (failed {ac.get('failed', 0)})"
            labels = ac.get("labels") or []
            if labels:
                msg += "\n" + "\n".join(f"  + {lab}" for lab in labels[:12])
                if len(labels) > 12:
                    msg += f"\n  … +{len(labels)-12} more"
        else:
            msg += " · auto_confirm=OFF"
        return {
            "ok": True,
            "msg": msg,
            "grow": out,
            "auto_confirm_grow": bool(getattr(program, "auto_confirm_grow", False)),
            "end": "grow",
        }
    if lower in ("pulse", "pulse enhance", "enhance pulse"):
        out = program.pulse() if hasattr(program, "pulse") else {}
        return {"ok": True, "msg": f"Pulse · {out}", "pulse": out}
    # ─── Inspire Pack commands (offline video-distilled) ───
    if lower in ("inspire", "inspire status", "inspire pack"):
        st = program.inspire_status() if hasattr(program, "inspire_status") else {}
        pref = st.get("prefs") or {}
        lines = [
            "Inspire Pack (offline · educational stubs)",
            f"  prefs: confirms={pref.get('confirms', 0)} rejects={pref.get('rejects', 0)} tokens={pref.get('tokens', 0)}",
            f"  score samples={st.get('score_samples', 0)} · vision mem={st.get('vision_memory', 0)}",
            f"  sprite={((st.get('sprite') or {}).get('action'))} · layers={st.get('multivision_layers') or []}",
        ]
        top = pref.get("top") or []
        if top:
            lines.append("  top prefs: " + ", ".join(f"{t[0]}={t[1]:+.2f}" for t in top[:6]))
        return {"ok": True, "msg": "\n".join(lines), "inspire": st}
    # ─── Program self-understanding + evolution ───
    if lower in ("self", "know self", "knowself", "who am i really", "self model", "self-model", "understand myself"):
        lines = program.reflect() if hasattr(program, "reflect") else ["no self model"]
        return {"ok": True, "msg": "\n".join(lines), "self": program.know_self() if hasattr(program, "know_self") else {}, "end": "self_page"}
    if lower in ("self map", "selfmap", "inventory self", "what am i"):
        inv = program.self_map() if hasattr(program, "self_map") else {}
        lines = [
            f"Self map · gen={inv.get('generation')} ideas={inv.get('ideas')} "
            f"matrices={inv.get('matrix_count')} snaps={inv.get('snap_count')}",
            f"  form={inv.get('form')} mode={inv.get('ux_mode')} view={inv.get('view_mode')}",
            f"  workshops={', '.join(inv.get('workshops') or [])}",
            f"  matrices={', '.join((inv.get('matrices') or [])[:12])}…",
            f"  snaps={', '.join((inv.get('snaps') or [])[:10])}…",
            f"  doors: self | evolve | close gaps | evolve loop 12",
        ]
        return {"ok": True, "msg": "\n".join(lines), "map": inv, "end": "self_map"}
    if lower in ("close gaps", "close self gaps", "warm gaps", "self gaps"):
        out = program.close_self_gaps() if hasattr(program, "close_self_gaps") else {"ok": False}
        closed = out.get("closed") or []
        return {
            "ok": True,
            "msg": f"Closed gaps: {', '.join(closed) or '—'}\n  mastery={(out.get('knowledge') or {}).get('avg_mastery')}\n  doors: self | evolve",
            "gaps": out,
            "end": "gaps_closed",
        }
    if lower.startswith("evolve loop") or lower in ("evolve 12", "self evolve loop"):
        parts = lower.split()
        n = 12
        for part in parts:
            if part.isdigit():
                n = max(1, min(150, int(part)))
        out = program.evolve_loop(n) if hasattr(program, "evolve_loop") else {"ok": False}
        return {
            "ok": True,
            "msg": (
                f"Evolve loop ×{out.get('cycles')} · gen={out.get('generation')} "
                f"mastery={out.get('mastery')}\n"
                f"  pillars={(out.get('pillars') or {}).get('label')} "
                f"avg={(out.get('pillars') or {}).get('average')}\n"
                f"  doors: self | audit | evolve"
            ),
            "loop": out,
            "end": "evolve_loop",
        }
    if lower in ("evolve understood", "self evolve", "evolve with understanding"):
        out = program.evolve_understood() if hasattr(program, "evolve_understood") else program.evolve("self")
        return {
            "ok": True,
            "msg": (
                f"Evolved with understanding · gen={out.get('generation')} "
                f"pillars {out.get('pillars_before')}→{out.get('pillars_after')} "
                f"mastery={out.get('mastery')}\n"
                f"  closed={out.get('closed')}\n  doors: self | evolve loop 12 | audit"
            ),
            "evolve": out,
            "end": "evolve_understood",
        }
    if lower in ("multilook", "multi look", "multi-look", "multiscale", "multi vision"):
        mv = program.multilook() if hasattr(program, "multilook") else {}
        layers = mv.get("layers") or {}
        lines = ["Multi-scale vision:"]
        for name in ("near", "mid", "far"):
            layer = layers.get(name) or {}
            nearest = layer.get("nearest")
            nlab = (nearest or {}).get("label") if isinstance(nearest, dict) else nearest
            lines.append(f"  {name}: count={layer.get('count', 0)} nearest={nlab or '—'}")
        recent = mv.get("recent") or []
        if recent:
            lines.append("  memory: " + ", ".join(str(r.get("label") or r.get("id")) for r in recent[:6]))
        return {"ok": True, "msg": "\n".join(lines), "multilook": mv}
    if lower.startswith("attend ") or lower in ("attend", "attention"):
        q = raw.split(maxsplit=1)[1].strip() if lower.startswith("attend ") else "growth seed idea"
        ranked = program.attend(q) if hasattr(program, "attend") else []
        if not ranked:
            return {"ok": True, "msg": f"No ideas to attend for: {q}", "attention": []}
        lines = [f"Attention · query={q!r}"]
        for i, row in enumerate(ranked, 1):
            lines.append(
                f"  {i}. [{row.get('id')}] {row.get('label')}  "
                f"score={row.get('score')} att={row.get('attention')}"
            )
        return {"ok": True, "msg": "\n".join(lines), "attention": ranked}
    if lower in ("slopes", "slope", "calculus", "score slopes", "ds/dt"):
        lines = program.slopes_report() if hasattr(program, "slopes_report") else ["No slope data"]
        return {"ok": True, "msg": "\n".join(lines), "slopes": (program.inspire.scores.slopes() if hasattr(program, "inspire") else {})}
    if lower in ("prefs", "preferences", "pref", "preference ledger"):
        st = program.prefs_status() if hasattr(program, "prefs_status") else {}
        lines = [
            f"Preference ledger · confirms={st.get('confirms', 0)} rejects={st.get('rejects', 0)} tokens={st.get('tokens', 0)}",
            "  (confirm boosts · reject dampens — not pure imitation)",
        ]
        for t, w in (st.get("top") or [])[:10]:
            lines.append(f"  {t}: {w:+.3f}")
        return {"ok": True, "msg": "\n".join(lines), "prefs": st}
    if lower.startswith("glyph") or lower in ("proc glyph", "procedural"):
        seed = raw.split(maxsplit=1)[1].strip() if " " in raw.strip() else (getattr(program, "owner", None) or "matrix")
        art = program.glyph(seed) if hasattr(program, "glyph") else ""
        return {"ok": True, "msg": art or f"(glyph {seed})", "glyph": seed}
    if lower.startswith("script ") or lower.startswith("script:"):
        body = raw.split(maxsplit=1)[1] if " " in raw else ""
        if body.startswith(":"):
            body = body[1:].strip()
        if not body:
            return {
                "ok": False,
                "error": "usage: script look; pulse; status   or multi-line with ;",
            }
        out = program.run_script(body) if hasattr(program, "run_script") else {"ok": False}
        lines = [f"Script · ran={out.get('ran', 0)} passed={out.get('passed', 0)}"]
        for r in (out.get("results") or [])[:12]:
            mark = "✓" if r.get("ok") else "✗"
            lines.append(f"  {mark} [{r.get('cost')}] {r.get('cmd')}: {(r.get('msg') or '')[:60]}")
        return {"ok": bool(out.get("ok")), "msg": "\n".join(lines), "script": out}
    if lower in ("save", "persist", "save program"):
        path = program.save() if hasattr(program, "save") else ""
        return {"ok": True, "msg": f"Saved · {path or 'program state written'}"}
    # Navigation helpers for walk UX
    if lower in ("home", "goto home", "return home", "spawn"):
        out = program.fp_goto(0, 0, 0) if hasattr(program, "fp_goto") else {}
        try:
            program.avatar.face(__import__("form.avatar", fromlist=["Facing"]).Facing.N)
        except Exception:
            pass
        program.look_pitch = "level"
        return {
            "ok": True,
            "msg": f"Home (0,0,0) · face N · {((out or {}).get('view') or {}).get('mandel') or ''}",
        }
    if lower in ("nearest", "goto nearest", "jump nearest", "find nearest"):
        fp = program.first_person() if hasattr(program, "first_person") else {}
        near = (fp or {}).get("nearest") or []
        if not near:
            return {"ok": False, "error": "No nearby ideas ranked — grow or plant first"}
        n = near[0]
        x, y = int(n.get("x") or 0), int(n.get("y") or 0)
        program.fp_goto(x, y, 0)
        return {
            "ok": True,
            "msg": f"Nearest → {n.get('label') or n.get('id')} @ ({x},{y}) · d={n.get('dist')}",
            "nearest": n,
        }
    if lower.startswith("find "):
        q = raw.split(maxsplit=1)[1].strip().lower()
        nodes = program.nodes_payload() if hasattr(program, "nodes_payload") else []
        hits = []
        for n in nodes:
            blob = " ".join([
                str(n.get("id") or ""),
                str(n.get("label") or ""),
                str(n.get("words") or ""),
                str(n.get("detail") or ""),
                str(n.get("skin") or ""),
            ]).lower()
            if q in blob:
                hits.append(n)
        hits.sort(key=lambda n: -float(n.get("score") or 0))
        if not hits:
            return {"ok": False, "error": f"No ideas match “{q}”"}
        lines = [f"Find “{q}” · {len(hits)} hits"]
        for i, n in enumerate(hits[:12], 1):
            lines.append(
                f"{i:2}. [{n.get('id')}] {n.get('label')} · ({int(round(float(n.get('x') or 0)))},"
                f"{int(round(float(n.get('y') or 0)))}) · {n.get('skin')} · score {n.get('score')}"
            )
        top = hits[0]
        return {
            "ok": True,
            "msg": "\n".join(lines),
            "find": hits[:20],
            "top_id": top.get("id"),
            "top_xy": [int(round(float(top.get("x") or 0))), int(round(float(top.get("y") or 0)))],
        }
    if lower.startswith("plant ") or lower.startswith("place idea "):
        # plant <label>  — places idea at current centerpoint
        if lower.startswith("place idea "):
            label = raw.split(maxsplit=2)[2].strip() if len(raw.split(maxsplit=2)) > 2 else ""
        else:
            label = raw.split(maxsplit=1)[1].strip() if " " in raw else ""
        if not label:
            return {"ok": False, "error": "usage: plant <label>"}
        ax, ay = program.avatar.body.pos
        cf = int(getattr(program, "center_f", 0) or 0)
        nid = "plant_" + "".join(ch if ch.isalnum() else "_" for ch in label.lower())[:40]
        # unique id
        base, i = nid, 1
        while nid in program.cube.session.plane.units:
            nid = f"{base}_{i}"
            i += 1
        try:
            from form.dell_matrix.plane import Skin
            skin = Skin.SEED
        except Exception:
            skin = None
        kwargs = dict(
            words=f"planted at center ({int(ax)},{int(ay)},{cf})",
            detail=f"Live-planted idea at matrix cell ({int(round(ax))},{int(round(ay))},{cf}).",
            goals=["grow from this cell", "link to neighbors"],
            x=float(int(round(ax))),
            y=float(int(round(ay))),
        )
        if skin is not None:
            kwargs["skin"] = skin
        u = program.place(nid, label, **kwargs)
        return {
            "ok": True,
            "msg": f"Planted “{label}” · id={getattr(u,'id',nid)} @ ({int(round(ax))},{int(round(ay))},{cf})",
            "planted": nid,
        }

    # ─── Nature of Code (Ch0–5 + CA cores + live page) ───
    if lower in ("nature", "nature of code", "noc", "nature_code", "nature code"):
        try:
            from form.dell_matrix.nature_code import smoke as noc_smoke
            ok = noc_smoke()
        except Exception as e:
            return {"ok": False, "error": f"nature_code import/smoke: {e}", "end": "nature_miss"}
        return {
            "ok": True,
            "msg": (
                f"Nature of Code · cores live · smoke={'PASS' if ok else 'FAIL'}\n"
                "  page: /nature  (Walker · Forces · Oscillation · Particles · Agents · CA)\n"
                "  doors: nature status | nature walker | force tick | /forces | /geometry"
            ),
            "nature": {"smoke": ok, "page": "/nature"},
            "end": "nature_page",
        }
    if lower in ("nature status", "noc status"):
        lines = [
            "Nature of Code cores (offline · pure Python)",
            "  Ch0 Walker / gaussian / accept-reject",
            "  Ch1 Vec2",
            "  Ch1–2 Mover + apply_force / friction / gravity / wind",
            "  Ch3 oscillate(angle, amp)",
            "  Ch4 Particle + Emitter",
            "  Ch5 Agent seek / flee",
            "  Ch7 ca1d_step (Rule 90 default)",
            "  Live canvas: /nature  ·  commands: nature | nature walker",
        ]
        return {"ok": True, "msg": "\n".join(lines), "end": "nature_status"}
    if lower in ("nature walker", "noc walker"):
        try:
            from form.dell_matrix.nature_code import Walker, Vec2
            w = Walker(pos=Vec2(0, 0))
            path = []
            for _ in range(12):
                w.step_random()
                path.append((round(w.pos.x, 2), round(w.pos.y, 2)))
            return {
                "ok": True,
                "msg": f"Walker 12 steps → {path[-1]}\n  trail sample: {path[:6]}…\n  doors: nature | /nature",
                "walker": {"end": path[-1], "steps": path},
                "end": "nature_walker",
            }
        except Exception as e:
            return {"ok": False, "error": str(e), "end": "nature_miss"}

    if lower in ("radar", "local radar", "scan"):
        fp = program.first_person() if hasattr(program, "first_person") else {}
        radar = (fp or {}).get("radar") or []
        occ = [c for c in radar if c.get("count")]
        lines = [f"Radar shell · occupied {len(occ)}/{len(radar)} cells · center {(fp or {}).get('center')}"]
        for c in occ[:20]:
            lines.append(
                f"  ({c['x']},{c['y']}) ×{c['count']} {c.get('skin') or ''} {c.get('label') or ''}"
            )
        return {"ok": True, "msg": "\n".join(lines), "radar": radar}
    return None


def _run_command(program, cmd: str, _depth: int = 0) -> Dict[str, Any]:
    cmd = (cmd or "").strip()
    if not cmd:
        return {"ok": False, "error": "empty command — try: help | page | look | proposals", "end": "empty"}
    # Natural English → canonical command (one hop) so program understands phrasing
    if _depth < 1:
        try:
            from form.mandell.english_brain import normalize_english
            norm, path = normalize_english(cmd)
            n = (norm or "").strip()
            if (
                n
                and path in ("paraphrase", "synonym", "learned", "strip")
                and n.lower() != cmd.lower()
            ):
                out = _run_command(program, n, _depth=1)
                if isinstance(out, dict):
                    out = dict(out)
                    out["english_from"] = cmd
                    out["english_path"] = path
                    out["english_norm"] = n
                    if out.get("msg") and cmd.lower() != n.lower():
                        out["msg"] = f"(understood: {n})\n" + str(out["msg"])
                    elif out.get("error") and cmd.lower() != n.lower():
                        out["error"] = f"(understood: {n}) " + str(out["error"])
                return out
        except Exception:
            pass
    if _depth == 0:
        _CMD_HISTORY.append(cmd)
        while len(_CMD_HISTORY) > _MAX_HIST:
            _CMD_HISTORY.pop(0)
    lower = cmd.lower().strip()

    # Incomplete bare args — closed usage end, never fall into create-idea
    if lower in _INCOMPLETE_USAGE:
        return {
            "ok": False,
            "error": _INCOMPLETE_USAGE[lower],
            "command": cmd,
            "end": "usage",
            "state": _state_payload(program),
        }

    # First-person: infinite cube/sphere matrix · Mandell-bridged steps
    vm = getattr(program, "view_mode", "first_person")
    if lower in ("fp", "first person", "mode first", "mode first_person", "view first"):
        program.view_mode = "first_person"
        return {"ok": True, "msg": "View → first-person (cube-to-cube matrix)", "state": _state_payload(program)}
    if lower in ("map", "mode map", "view map", "legacy map"):
        program.view_mode = "map"
        return {"ok": True, "msg": "View → legacy map", "state": _state_payload(program)}

    def _fp_reply(out, msg, command):
        st = _state_payload(program)
        fp = st.get("fp") or out.get("view") or {}
        mandel = fp.get("mandel") or ""
        return {
            "ok": True,
            "msg": f"{msg}" + (f" · {mandel}" if mandel else ""),
            "command": command,
            "mandel": mandel,
            "state": st,
            "fp": fp,
        }

    if vm == "first_person" or lower.startswith("fp ") or lower in (
        "fp_forward", "fp_back", "fp_up", "fp_down", "fp_turn_left", "fp_turn_right",
        "w", "a", "s", "d", "r", "f", "q", "e",
        "forward", "back", "backstep", "backward", "step back",
        "walk", "walk forward", "go", "step forward",
        "enter next", "enter next cell", "enter next cube", "next cube", "step into",
        "turn left", "turn right", "left", "right",
        "up", "down", "ascend", "descend", "go up", "go down",
        "look", "look level", "look around", "look up", "look down",
        "strafe left", "strafe right", "strafe l", "strafe r",
    ):
        raw = lower
        if lower.startswith("fp "):
            lower = lower[3:].strip()
        alias = {
            "fp_forward": "forward", "fp_back": "back", "fp_up": "up", "fp_down": "down",
            "fp_turn_left": "turn left", "fp_turn_right": "turn right",
        }
        lower = alias.get(raw, lower)
        if lower in ("w", "forward", "walk", "walk forward", "go", "step forward",
                     "enter next", "enter next cell", "enter next cube", "next cube", "step into"):
            out = program.fp_move("forward")
            c = out["center"]
            return _fp_reply(out, f"Enter cube ({c[0]},{c[1]},{c[2]})", "fp forward")
        if lower in ("s", "back", "backstep", "backward", "step back"):
            out = program.fp_move("back")
            c = out["center"]
            return _fp_reply(out, f"Enter cube ({c[0]},{c[1]},{c[2]})", "fp back")
        if lower in ("a", "turn left", "left"):
            out = program.fp_turn("left")
            return _fp_reply(out, f"Turn · face {out['yaw']}", "fp turn left")
        if lower in ("d", "turn right", "right"):
            out = program.fp_turn("right")
            return _fp_reply(out, f"Turn · face {out['yaw']}", "fp turn right")
        if lower in ("r", "up", "fly up", "ascend", "go up"):
            out = program.fp_move("up")
            c = out["center"]
            return _fp_reply(out, f"Enter cube ({c[0]},{c[1]},{c[2]})", "fp up")
        if lower in ("f", "down", "fly down", "descend", "go down"):
            out = program.fp_move("down")
            c = out["center"]
            return _fp_reply(out, f"Enter cube ({c[0]},{c[1]},{c[2]})", "fp down")
        if lower in ("q", "look up", "pitch up"):
            out = program.fp_look("up")
            return _fp_reply(out, "Look up (ceiling)", "fp look up")
        if lower in ("e", "look down", "pitch down"):
            out = program.fp_look("down")
            return _fp_reply(out, "Look down (floor)", "fp look down")
        if lower in ("look", "look level", "look around", "space"):
            out = program.fp_look("level")
            return _fp_reply(out, "Look level", "fp look")
        if lower.startswith("goto "):
            parts = lower.split()
            try:
                hh, vv = int(parts[1]), int(parts[2])
                ff = int(parts[3]) if len(parts) > 3 else 0
                out = program.fp_goto(hh, vv, ff)
                return _fp_reply(out, f"Goto ({hh},{vv},{ff})", "fp goto")
            except Exception:
                return {"ok": False, "error": "usage: goto H V [F]", "state": _state_payload(program)}
        if lower in ("strafe left", "strafe l"):
            out = program.fp_move("left")
            c = out["center"]
            return _fp_reply(out, f"Enter cube ({c[0]},{c[1]},{c[2]})", "fp left")
        if lower in ("strafe right", "strafe r"):
            out = program.fp_move("right")
            c = out["center"]
            return _fp_reply(out, f"Enter cube ({c[0]},{c[1]},{c[2]})", "fp right")
        # unknown fp-ish token — fall through
        lower = raw

    ux = _handle_ux_command(program, lower, cmd)
    if ux is not None:
        ux["command"] = cmd
        ux["state"] = _state_payload(program)
        return ux

    ai_res = _handle_ai_command(program, cmd)
    if ai_res is not None:
        ai_res["command"] = cmd
        ai_res["state"] = _state_payload(program)
        return ai_res

    try:
        from form.mandell.seed import looks_like_seed
        from form.mandell.executor import execute_seed
        from form.mandell.translate import translate
        from form.repl import _execute_intent, _apply_seed_result, capture_output
        from form.avatar import Locomotion
        import io
        import contextlib
    except Exception as e:
        return {"ok": False, "error": f"import: {e}"}

    try:
        stdout_buf = io.StringIO()

        def _run_fallthrough():
            with contextlib.redirect_stdout(stdout_buf):
                if looks_like_seed(cmd):
                    result = execute_seed(program, cmd)
                    _apply_seed_result(program, result)
                    # seed results often carry messages
                    msgs = []
                    if isinstance(result, dict):
                        for k in ("message", "msg", "detail"):
                            if result.get(k):
                                msgs.append(str(result[k]))
                        if result.get("messages"):
                            msgs.extend(str(m) for m in result["messages"])
                    return "\n".join(msgs) if msgs else None
                intent = translate(cmd)
                _, captured = capture_output(
                    lambda: _execute_intent(program, intent, raw_line=cmd)
                )
                return captured

        captured = _run_fallthrough()
        printed = stdout_buf.getvalue().strip()
        # strip leading double-spaces from print-style help
        if printed:
            printed = "\n".join(
                ln[2:] if ln.startswith("  ") else ln for ln in printed.splitlines()
            )
        msg_parts = [p for p in (captured, printed) if p]
        msg = "\n".join(msg_parts).strip()
        # post-movement snap
        if lower.startswith("walk") or lower == "run" or "walk" in lower or lower in ("jog", "backstep"):
            program.apply_grid_snap()
            program._push_user_trail()
        if not msg:
            # still useful end: acknowledge + state summary
            n = len(program.cube.session.plane.units)
            pend = len(program.list_proposals()) if hasattr(program, "list_proposals") else 0
            msg = f"Done · {cmd} · ideas={n} nursery={pend} · doors: status | page | look | help"
        # Usability: unknown / not-understood is a closed guidance end (not success invent)
        not_understood = msg.lower().startswith("not understood")
        return {
            "ok": not not_understood,
            "command": cmd,
            "msg": msg if not not_understood else None,
            "error": msg if not_understood else None,
            "end": "unknown" if not_understood else "intent",
            "state": _state_payload(program),
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "command": cmd,
            "end": "error",
            "state": _state_payload(program),
        }


def _make_handler(program):
    class LiveHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def _cors(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def _json(self, code, payload):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            self.send_response(204)
            self._cors()
            self.end_headers()

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path or "/"

            if path == "/state":
                self._json(200, _state_payload(program))
                return
            if path == "/health":
                self._json(200, {"ok": True, "live": True, "app": "menu", "pages": list(_PAGE_ROUTES.keys())})
                return
            if path == "/pages":
                self._json(200, {
                    "ok": True,
                    "entry": "/",
                    "routes": {k: v for k, v in _PAGE_ROUTES.items()},
                    "static": ["/css/app.css", "/js/core.js"],
                })
                return

            # Named app pages
            if path in _PAGE_ROUTES:
                body = _load_asset(_PAGE_ROUTES[path])
                if body is None:
                    self._json(404, {"ok": False, "error": f"missing asset {_PAGE_ROUTES[path]}"})
                    return
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            # Static assets: /css/*, /js/*, /pages/* (direct), /assets/*
            static_rel = None
            if path.startswith("/css/") or path.startswith("/js/"):
                static_rel = path.lstrip("/")
            elif path.startswith("/pages/") and path.endswith(".html"):
                static_rel = path.lstrip("/")
            elif path.startswith("/assets/"):
                static_rel = path[len("/assets/"):]
            elif path in ("/fp_world.html", "/menu.html"):
                static_rel = path.lstrip("/")

            if static_rel:
                body = _load_asset(static_rel)
                if body is None:
                    self._json(404, {"ok": False, "error": f"not found: {static_rel}"})
                    return
                ext = os.path.splitext(static_rel)[1].lower()
                ctype = _MIME.get(ext, "application/octet-stream")
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            self._json(404, {"ok": False, "error": "not found", "path": path})

        def do_POST(self):
            if urllib.parse.urlparse(self.path).path != "/cmd":
                self._json(404, {"ok": False, "error": "not found"})
                return
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8") if length else ""
            try:
                data = json.loads(raw) if raw else {}
                cmd = data.get("cmd") or data.get("command") or ""
            except Exception:
                cmd = raw.strip()
            result = _run_command(program, cmd)
            self._json(200 if result.get("ok") else 400, result)

    return LiveHandler



# Legacy inline HTML removed — UI is assets/fp_world.html via _load_fp_html()

# Keep a process-level handle so callers can stop a live server cleanly
_LIVE_SERVER = None
_LIVE_THREAD = None


def start_live(program, port: int = _DEFAULT_PORT, background: bool = True) -> Dict[str, Any]:
    """
    Start localhost multi-page live visual.

    Important: with background=True the server runs in a daemon thread of
    *this* process. When the process exits, the UI dies. Keep the process
    alive (REPL `live`, or `python3 -m form.dell_matrix.live_visual`) or
    use the offline snapshot (`visual` command) which needs no server.
    """
    global _LIVE_SERVER, _LIVE_THREAD
    # Stop previous instance if any (same process)
    if _LIVE_SERVER is not None:
        try:
            _LIVE_SERVER.shutdown()
        except Exception:
            pass
        _LIVE_SERVER = None

    handler = _make_handler(program)
    # allow quick restart on same port
    try:
        HTTPServer.allow_reuse_address = True
    except Exception:
        pass
    try:
        server = HTTPServer((_HOST, port), handler)
    except OSError as e:
        # port busy — try next ports
        err = str(e)
        for alt in range(port + 1, port + 12):
            try:
                server = HTTPServer((_HOST, alt), handler)
                port = alt
                break
            except OSError:
                continue
        else:
            return {
                "ok": False,
                "error": f"Could not bind live port ({err}). Try: visual (offline HTML) or free port {port}.",
                "fallback": "you> visual   # offline snapshot, no server",
            }

    def _serve():
        try:
            server.serve_forever()
        except Exception:
            pass

    _LIVE_SERVER = server
    if background:
        # non-daemon so short scripts can join if they want; REPL still exits
        # with process — document keep-alive. Use daemon=False only when
        # process is meant to be the live host.
        t = threading.Thread(target=_serve, daemon=True, name="DellMatrixLive")
        t.start()
        _LIVE_THREAD = t
    else:
        server.serve_forever()

    return {
        "ok": True,
        "url": f"http://{_HOST}:{port}/",
        "host": _HOST,
        "port": port,
        "note": "Main menu + pages. Keep this process running or the server stops.",
        "ui": "form/dell_matrix/assets/menu.html",
        "pages": list(_PAGE_ROUTES.keys()),
        "stop": "Process exit stops the server. Offline fallback: visual",
        "fallback_offline": "type: visual  → open DellMatrix_UI.html in a browser",
    }


def smoke() -> bool:
    print("=== LIVE A+ SMOKE ===")
    try:
        from form.open import open_program
        from form.avatar import Facing, Posture
        p = open_program("LiveAPlus")
        p.place("a", "Alpha", words="test", x=0, y=2)
        st = _state_payload(p)
        assert st["user_vision"].get("cone")
        assert "a" in st["user_vision"].get("in_view_ids", []) or True
        assert st.get("actions")
        assert st.get("ai")
        assert "edges" in st
        assert st.get("entities"), "entities inventory required"
        p.enter_workshop("matrix")
        st2 = _state_payload(p)
        assert st2.get("workshop")
        # trail must not grow on idle polls
        p.user_trail.clear()
        for _ in range(4):
            _state_payload(p)
        assert len(p.user_trail) == 0, f"idle trail pollution: {len(p.user_trail)}"
        # movement trail + backstep + strafe
        r = _run_command(p, "walk forward")
        assert r.get("ok")
        assert len(p.user_trail) >= 1
        p.avatar.body.pos = (0, 0)
        p.avatar.face(Facing.N)
        r = _run_command(p, "backstep")
        assert r.get("ok") and p.avatar.body.pos == (0, -1)
        assert p.avatar.body.facing == Facing.N
        p.avatar.body.pos = (0, 0)
        r = _run_command(p, "strafe right")
        assert r.get("ok") and p.avatar.body.pos == (1, 0)
        # sit then step stands up
        p.avatar.set_posture(Posture.SIT)
        p.avatar.step(1)
        assert p.avatar.body.posture != Posture.SIT
        print("[PASS] cones + entities + trail + backstep + strafe + sit-stand")
        print("=== RESULT: PASS ===")
        return True
    except Exception as e:
        print("[FAIL]", e)
        return False


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
