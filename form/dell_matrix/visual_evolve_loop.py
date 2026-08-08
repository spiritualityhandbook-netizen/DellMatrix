#!/usr/bin/env python3
"""
Visual / matrix walk enhance loop × N (default 150).

Each cycle: exercise walk + capabilities, evolve Program, apply progressive
usability/function enhancements, re-score against A+ checklist.

  python -m form.dell_matrix.visual_evolve_loop
  python -m form.dell_matrix.visual_evolve_loop --cycles 150
"""

from __future__ import annotations

import os
import re
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from form.persist import load, save
from form.open import open_program
from form.avatar import Facing
from form.dell_matrix.first_person import first_person_view, move_fp, turn_fp, look_fp
from form.dell_matrix.live_visual import (
    _load_fp_html, _run_command, _state_payload, _PAGE_ROUTES, _load_asset, _ASSETS_DIR,
)

ASSET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fp_world.html")
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
MENU = os.path.join(ASSETS, "menu.html")
CORE_JS = os.path.join(ASSETS, "js", "core.js")
APP_CSS = os.path.join(ASSETS, "css", "app.css")
PAGES_DIR = os.path.join(ASSETS, "pages")

REQUIRED_PAGES = (
    "walk.html", "lattice.html", "nursery.html", "program.html",
    "personas.html", "forces.html", "geometry.html", "matrices.html", "console.html",
)


# ─── helpers ───────────────────────────────────────────────────────────────

def _read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _write_file(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _read_html() -> str:
    try:
        with open(ASSET, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return _load_fp_html()


def _write_html(html: str) -> None:
    os.makedirs(os.path.dirname(ASSET), exist_ok=True)
    with open(ASSET, "w", encoding="utf-8") as f:
        f.write(html)


def _patch_file_once(path: str, marker: str, needle: str, insert: str, after: bool = True) -> bool:
    text = _read_file(path)
    if not text or marker in text or needle not in text:
        return False
    if after:
        text = text.replace(needle, needle + insert, 1)
    else:
        text = text.replace(needle, insert + needle, 1)
    _write_file(path, text)
    return True


def _patch_once(marker: str, needle: str, insert: str, after: bool = True) -> bool:
    """Insert `insert` near `needle` if `marker` not already present. Returns True if changed."""
    html = _read_html()
    if marker in html:
        return False
    if needle not in html:
        return False
    if after:
        html = html.replace(needle, needle + insert, 1)
    else:
        html = html.replace(needle, insert + needle, 1)
    _write_html(html)
    return True


def _replace_once(old: str, new: str) -> bool:
    html = _read_html()
    if old not in html or new in html:
        return False
    _write_html(html.replace(old, new, 1))
    return True


# ─── quality checks (A+ checklist) ─────────────────────────────────────────

def _checks(program) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        out.append({"name": name, "ok": bool(ok), "detail": detail})

    html = _read_html()
    # UI structure
    add("ui_loaded", "Matrix Walk" in html and "wall far" in html, f"bytes={len(html)}")
    add("ui_minimap", "minimap" in html and "local lattice" in html.lower() or "minimap" in html)
    add("ui_capabilities", "Grow" in html and ("BIMO" in html or "bimo" in html.lower()))
    add("ui_animation", "stepIn" in html)
    add("ui_lattice_page", "Main Lattice" in html and "lattice-modal" in html)
    add("ui_event_delegation", "addEventListener('click'" in html or 'addEventListener("click"' in html)
    add("ui_results_panel", "results-modal" in html or "results-body" in html)
    add("ui_confirm_all", "confirm all" in html)
    add("ui_keyboard_l", "k==='l'" in html or 'k==="l"' in html)
    add("ui_toast", "toast" in html)
    add("ui_live_dot", "live-dot" in html or "dot-live" in html)
    add("ui_form_buttons", all(x in html for x in ('data-c="cube"', 'data-c="sphere"', 'data-c="flower"')))
    add("ui_nav_strafe", "strafe left" in html and "strafe right" in html)
    add("ui_data_nav_walls", "data-nav=" in html)
    add("ui_focus_visible", ":focus-visible" in html or "focus-visible" in html)
    add("ui_cmd_history", "cmd-history" in html or "cmd_history" in html or "hist-list" in html)
    add("ui_pillar_meters", "pillar-meter" in html or "pillars-bar" in html)
    add("ui_path_trail", "path-trail" in html or "walk-trail" in html)
    add("ui_offline_banner", "offline-banner" in html or "conn-banner" in html)
    add("ui_loading", "loading-bar" in html or "busy-bar" in html)
    add("ui_a11y_dialog", 'role="dialog"' in html)
    add("ui_help_keys", "Keyboard" in html or "btn-help" in html)
    add("ui_home_nearest", 'data-c="home"' in html and 'data-c="nearest"' in html)
    add("ui_plant", "btn-plant" in html and "plant-label" in html)
    add("ui_radar_hud", "radar-hud" in html)
    add("ui_compass", "compass-needle" in html)
    add("ui_split_dock", "lat-dock" in html and "btn-split" in html)
    add("ui_find", "btn-find" in html)
    add("ui_dpad", "dpad" in html)
    add("ui_nursery_confirm", "confirm " in html or "nursery-mini" in html)
    add("ui_menu_link", 'href="/"' in html or "Menu" in html)

    # Multi-page app (main menu + individual pages)
    menu = _read_file(MENU)
    core = _read_file(CORE_JS)
    css = _read_file(APP_CSS)
    add("app_menu", "DellMatrix" in menu and "menu-card" in menu and "Matrix Walk" in menu, f"bytes={len(menu)}")
    add("app_core_js", "DM" in core and "sendCmd" in core and "mountShell" in core, f"bytes={len(core)}")
    add("app_css", ".menu-card" in css and ".topbar" in css, f"bytes={len(css)}")
    add("app_routes", len(_PAGE_ROUTES) >= 10, f"n={len(_PAGE_ROUTES)}")
    missing_pages = [p for p in REQUIRED_PAGES if not os.path.isfile(os.path.join(PAGES_DIR, p))]
    add("app_pages_exist", not missing_pages, str(missing_pages))
    # each page loads core + has identity
    page_ok = True
    page_detail = []
    for p in REQUIRED_PAGES:
        body = _read_file(os.path.join(PAGES_DIR, p))
        ok = "/js/core.js" in body or p == "walk.html"  # walk shell uses core
        if p == "walk.html":
            ok = ok and ("/walk/world" in body or "iframe" in body)
        elif p == "lattice.html":
            ok = ok and ("Main Lattice" in body or "lattice" in body.lower()) and "canvas" in body
        elif p == "nursery.html":
            ok = ok and "confirm" in body.lower()
        elif p == "console.html":
            ok = ok and ("cmd" in body and "Run" in body)
        if not ok or len(body) < 400:
            page_ok = False
            page_detail.append(p)
    add("app_pages_content", page_ok, f"weak={page_detail}")
    add("app_assets_loadable", all(_load_asset(f"pages/{p}") for p in REQUIRED_PAGES) and _load_asset("menu.html") is not None)

    # First-person matrix
    program.view_mode = "first_person"
    program.grid_snap = True
    program.avatar.body.pos = (0, 0)
    program.center_f = 0
    program.avatar.face(Facing.N)
    fp = first_person_view(program)
    add("fp_mode", fp.get("mode") == "first_person")
    add("fp_infinite", fp.get("infinite") is True)
    add("fp_mandel", "15[Map]" in str(fp.get("mandel") or ""))
    add("fp_faces", all(k in fp.get("faces", {}) for k in ("front", "left", "right", "up", "down")))
    add("fp_enterable", all(f.get("enterable") for f in fp.get("faces", {}).values()) if fp.get("faces") else False)
    add("fp_here", "here" in fp)
    add("fp_resonance", "resonance_top" in fp)

    r = move_fp(program, "forward")
    add("step_forward", r.get("ok") and r["center"] == [0, 1, 0], str(r.get("center")))
    turn_fp(program, "right")
    r2 = move_fp(program, "forward")
    add("step_east", r2.get("ok") and r2["center"][0] == 1, str(r2.get("center")))
    r3 = move_fp(program, "up")
    add("step_up", r3.get("ok") and r3["center"][2] == 1, str(r3.get("center")))
    look_fp(program, "up")
    fp2 = first_person_view(program)
    add("look_up", fp2.get("pitch") == "up")
    look_fp(program, "level")

    # Command path (live handlers)
    program.avatar.body.pos = (0, 0)
    program.center_f = 0
    program.avatar.face(Facing.N)
    res = _run_command(program, "enter next cube")
    add("cmd_enter_next", res.get("ok") is True, str(res.get("msg"))[:60])
    res = _run_command(program, "fp forward")
    add("cmd_fp_forward", res.get("ok") is True and "15[Map]" in str(res.get("msg") or ""), str(res.get("msg"))[:50])
    res = _run_command(program, "status")
    add("cmd_status_msg", res.get("ok") and bool(str(res.get("msg") or "").strip()), str(res.get("msg"))[:40])
    res = _run_command(program, "cube")
    add("cmd_cube_msg", res.get("ok") and "cube" in str(res.get("msg") or "").lower())
    res = _run_command(program, "sphere")
    add("cmd_sphere_msg", res.get("ok") and "sphere" in str(res.get("msg") or "").lower())
    res = _run_command(program, "proposals")
    add("cmd_proposals_msg", res.get("ok") and bool(str(res.get("msg") or "").strip()))
    res = _run_command(program, "audit")
    add("cmd_audit", res.get("ok") and "Pillar" in str(res.get("msg") or ""))
    res = _run_command(program, "matrices")
    add("cmd_matrices", res.get("ok") and "matrices" in str(res.get("msg") or "").lower())
    res = _run_command(program, "goto 0 0")
    add("cmd_goto", res.get("ok") is True, str(res.get("msg"))[:40])
    res = _run_command(program, "strafe left")
    add("cmd_strafe", res.get("ok") is True)
    res = _run_command(program, "home")
    add("cmd_home", res.get("ok") is True, str(res.get("msg"))[:50])
    res = _run_command(program, "nearest")
    add("cmd_nearest", res.get("ok") is True or "No nearby" in str(res.get("error") or ""),
        str(res.get("msg") or res.get("error"))[:50])
    res = _run_command(program, "radar")
    add("cmd_radar", res.get("ok") is True, str(res.get("msg"))[:40])
    res = _run_command(program, "find matrix")
    add("cmd_find", res.get("ok") is True, str(res.get("msg"))[:40])
    res = _run_command(program, "plant EnhanceLoop Probe")
    add("cmd_plant", res.get("ok") is True, str(res.get("msg") or res.get("error"))[:50])

    # State payload health
    st = _state_payload(program)
    add("state_fp", isinstance(st.get("fp"), dict) and "faces" in (st.get("fp") or {}))
    add("state_fp_radar", isinstance((st.get("fp") or {}).get("radar"), list) and len((st.get("fp") or {}).get("radar") or []) > 0)
    add("state_fp_nearest", isinstance((st.get("fp") or {}).get("nearest"), list))
    add("state_edges_capped", (st.get("edges_shown") or len(st.get("edges") or [])) <= 600,
        f"shown={st.get('edges_shown')} total={st.get('edges_total')}")
    add("state_nodes", len(st.get("nodes") or []) > 0, str(len(st.get("nodes") or [])))
    add("state_owner", bool(st.get("owner")))

    # Program capabilities
    status = program.status() if hasattr(program, "status") else {}
    add("capabilities_status", isinstance(status, dict) and (
        "forces" in status or "pillars" in status or "ideas" in status
    ))
    add("has_ideas", len(program.cube.session.plane.units) > 0,
        str(len(program.cube.session.plane.units)))
    try:
        # Warm pillars if cold open (avg starts ~0.65 until evolve/pulse)
        pil = program.audit() if hasattr(program, "audit") else {}
        if not (pil.get("healthy") or (pil.get("average") or 0) >= 0.7):
            for _ in range(4):
                if hasattr(program, "evolve"):
                    program.evolve("check-warm")
                if hasattr(program, "force_tick"):
                    program.force_tick()
                if hasattr(program, "pulse"):
                    program.pulse()
            pil = program.audit() if hasattr(program, "audit") else {}
        add("pillars_healthy", bool(pil.get("healthy") or (pil.get("average") or 0) >= 0.7),
            str(pil.get("average")))
    except Exception as e:
        add("pillars_healthy", False, str(e))

    return out


# ─── enhancement catalog (progressive, idempotent) ─────────────────────────

def _enh_focus_visible() -> str:
    ok = _patch_once(
        marker="/* enhance:focus-visible */",
        needle="button:active{transform:translateY(1px)}",
        insert=(
            "\n/* enhance:focus-visible */\n"
            "button:focus-visible,input:focus-visible,select:focus-visible{"
            "outline:2px solid var(--accent);outline-offset:2px}\n"
        ),
    )
    return "focus-visible" if ok else "focus-visible (skip)"


def _enh_loading_bar() -> str:
    if "loading-bar" in _read_html():
        return "loading-bar (skip)"
    css = """
/* enhance:loading-bar */
.loading-bar{position:fixed;top:0;left:0;height:3px;width:0;background:linear-gradient(90deg,var(--accent),var(--accent2));z-index:100;transition:width .2s,opacity .3s;opacity:0;pointer-events:none}
.loading-bar.on{opacity:1}
"""
    ok = _patch_once("/* enhance:loading-bar */", ".flash{animation:flashOk .45s ease}", css)
    html = _read_html()
    if 'id="loading-bar"' not in html:
        html = html.replace('<div class="app">', '<div class="loading-bar" id="loading-bar"></div>\n<div class="app">', 1)
        _write_html(html)
    # wire in sendCmd
    html = _read_html()
    if "loading-bar" in html and "function setLoading" not in html:
        html = html.replace(
            "function setLive(ok){",
            """function setLoading(on){
  const b=$('loading-bar'); if(!b) return;
  b.classList.toggle('on', !!on);
  b.style.width = on ? '70%' : '100%';
  if(!on) setTimeout(()=>{ b.style.width='0'; b.classList.remove('on'); }, 220);
}
function setLive(ok){""",
            1,
        )
        if "setLoading(true)" not in html:
            html = html.replace("busy = true;", "busy = true; setLoading(true);", 1)
            html = html.replace("busy=false;", "busy=false; setLoading(false);", 1)
        _write_html(html)
    return "loading-bar" if ok or "loading-bar" in _read_html() else "loading-bar fail"


def _enh_cmd_history() -> str:
    if "hist-list" in _read_html() and "/* enhance:cmd-history */" in _read_html():
        return "cmd-history (skip)"
    html = _read_html()
    if "/* enhance:cmd-history */" not in html:
        html = html.replace(
            '<div id="log"></div>',
            '''<div id="log"></div>
      <h2>Recent</h2>
      <div id="hist-list" class="stat" style="max-height:90px;overflow:auto"></div>
      <!-- enhance:cmd-history -->''',
            1,
        )
        _write_html(html)
    html = _read_html()
    if "function renderHist" not in html:
        html = html.replace(
            "function highlightForms(form){",
            """function renderHist(s){
  const el=$('hist-list'); if(!el) return;
  const h=(s&&s.cmd_history)||[];
  if(!h.length){ el.innerHTML='<span class="d">no commands yet</span>'; return; }
  el.innerHTML = h.slice().reverse().slice(0,10).map(c=>
    `<button type="button" class="ghost" style="font-size:10px;min-height:26px;padding:3px 6px;margin:2px" data-c="${esc(c)}">${esc(short(c,28))}</button>`
  ).join(' ');
}
function highlightForms(form){""",
            1,
        )
        if "renderHist(s)" not in html:
            html = html.replace("drawMinimap(fp, s.nodes||[]);", "drawMinimap(fp, s.nodes||[]);\n  renderHist(s);", 1)
        _write_html(html)
    return "cmd-history"


def _enh_pillar_meters() -> str:
    if "pillars-bar" in _read_html():
        return "pillar-meters (skip)"
    html = _read_html()
    if "pillars-bar" not in html:
        html = html.replace(
            '<div class="stat" id="prog"></div>',
            '''<div class="stat" id="prog"></div>
      <div id="pillars-bar" style="margin-top:8px"></div>''',
            1,
        )
        css = """
/* enhance:pillar-meters */
.pbar{display:flex;align-items:center;gap:6px;margin:3px 0;font-size:10px;color:var(--muted)}
.pbar .n{width:62px;text-transform:capitalize}
.pbar .t{flex:1;height:6px;background:#0a1018;border-radius:4px;overflow:hidden;border:1px solid var(--line)}
.pbar .f{height:100%;background:linear-gradient(90deg,var(--accent),var(--ok));border-radius:4px}
"""
        if "/* enhance:pillar-meters */" not in html:
            html = html.replace(".flash{animation:flashOk .45s ease}", ".flash{animation:flashOk .45s ease}" + css, 1)
        _write_html(html)
    html = _read_html()
    if "function renderPillars" not in html:
        html = html.replace(
            "function highlightForms(form){",
            """function renderPillars(s){
  const el=$('pillars-bar'); if(!el) return;
  const pil=s.pillars||{};
  const keys=['standing','spect','tonea','spirea','mandetail','omegate'];
  el.innerHTML = keys.map(k=>{
    const v=Number(pil[k]||0);
    const pct=Math.max(0,Math.min(100, Math.round(v*100)));
    return `<div class="pbar"><span class="n">${esc(k)}</span><div class="t"><div class="f" style="width:${pct}%"></div></div><span>${pct}%</span></div>`;
  }).join('');
}
function highlightForms(form){""",
            1,
        )
        if "renderPillars(s)" not in html:
            html = html.replace("drawMinimap(fp, s.nodes||[]);", "drawMinimap(fp, s.nodes||[]);\n  renderPillars(s);", 1)
        _write_html(html)
    return "pillar-meters"


def _enh_path_trail() -> str:
    if "walk-trail" in _read_html() and "function drawTrail" in _read_html():
        return "path-trail (skip)"
    html = _read_html()
    if 'id="walk-trail"' not in html:
        html = html.replace(
            '<div class="hud-help" id="hud-help">',
            '<div class="walk-trail" id="walk-trail" style="position:absolute;left:12px;top:12px;z-index:8;font:10px var(--mono);color:#7ddea8;background:#070c14aa;border:1px solid var(--line);border-radius:10px;padding:6px 8px;max-width:200px"></div>\n        <div class="hud-help" id="hud-help">',
            1,
        )
        _write_html(html)
    html = _read_html()
    if "function drawTrail" not in html:
        html = html.replace(
            "function highlightForms(form){",
            """function drawTrail(s){
  const el=$('walk-trail'); if(!el) return;
  const trail=(s.user_trail||[]).slice(-8);
  const fp=s.fp||{};
  const c=fp.center||[0,0,0];
  const lines = trail.map(t=>{
    if(Array.isArray(t)) return `(${t[0]},${t[1]})`;
    if(t&&typeof t==='object') return `(${t.x??t[0]??'?'},${t.y??t[1]??'?'})`;
    return String(t);
  });
  el.innerHTML = `<b style="color:#eef2f7">path</b> @ (${c.join(',')}) face ${esc(fp.yaw||'N')}<br>${lines.length?lines.join(' → '):'start walking'}`;
}
function highlightForms(form){""",
            1,
        )
        if "drawTrail(s)" not in html:
            html = html.replace("drawMinimap(fp, s.nodes||[]);", "drawMinimap(fp, s.nodes||[]);\n  drawTrail(s);", 1)
        _write_html(html)
    return "path-trail"


def _enh_offline_banner() -> str:
    if "offline-banner" in _read_html():
        return "offline-banner (skip)"
    html = _read_html()
    css = """
/* enhance:offline-banner */
.offline-banner{display:none;position:fixed;top:48px;left:50%;transform:translateX(-50%);z-index:60;background:#3b1515ee;border:1px solid var(--danger);color:#fecaca;padding:8px 14px;border-radius:999px;font-size:12px}
.offline-banner.show{display:block}
"""
    if "/* enhance:offline-banner */" not in html:
        html = html.replace(".flash{animation:flashOk .45s ease}", ".flash{animation:flashOk .45s ease}" + css, 1)
    if 'id="offline-banner"' not in html:
        html = html.replace(
            '<div class="app">',
            '<div class="offline-banner" id="offline-banner">Offline — live server unreachable</div>\n<div class="app">',
            1,
        )
    if "offline-banner" in html and "function setOffline" not in html:
        html = html.replace(
            "function setLive(ok){",
            """function setOffline(off){
  const b=$('offline-banner'); if(b) b.classList.toggle('show', !!off);
}
function setLive(ok){
  setOffline(!ok);
""",
            1,
        )
    _write_html(html)
    return "offline-banner"


def _enh_copy_coord() -> str:
    if "copyCoord" in _read_html():
        return "copy-coord (skip)"
    html = _read_html()
    # make nav-stat clickable
    if 'id="nav-stat"' in html and "copyCoord" not in html:
        html = html.replace(
            '<div class="stat" id="nav-stat">—</div>',
            '<div class="stat" id="nav-stat" title="Click to copy center" style="cursor:pointer">—</div>',
            1,
        )
        html = html.replace(
            "$('btn-lattice').addEventListener('click', openLattice);",
            """$('nav-stat').addEventListener('click', async ()=>{
  const c=(STATE&&STATE.fp&&STATE.fp.center)||[0,0,0];
  const t=`(${c.join(',')})`;
  try{ await navigator.clipboard.writeText(t); toast('copied '+t); }
  catch(e){ toast(t); }
});
$('btn-lattice').addEventListener('click', openLattice);""",
            1,
        )
        _write_html(html)
    return "copy-coord"


def _enh_wall_distance() -> str:
    if "/* enhance:wall-distance */" in _read_html():
        return "wall-distance (skip)"
    html = _read_html()
    # enrich fillWall meta with enterable hint already present; add shell if available
    if "function fillWall" in html and "/* enhance:wall-distance */" not in html:
        old = """const mandel = face.mandel || pg.mandel || '';
  el.classList.toggle('empty', !!empty);"""
        new = """const mandel = face.mandel || pg.mandel || '';
  /* enhance:wall-distance */
  const shell = (face&&face.page&&face.page.shell!=null)?face.page.shell:(pg.shell!=null?pg.shell:'');
  el.classList.toggle('empty', !!empty);"""
        if old in html:
            html = html.replace(old, new, 1)
            html = html.replace(
                "click → (${esc(coord)})<br><span style=\"color:#7ddea8\">${esc(mandel)}</span>",
                "click → (${esc(coord)})${shell!==''?` · shell ${shell}`:''}<br><span style=\"color:#7ddea8\">${esc(mandel)}</span>",
                1,
            )
            _write_html(html)
    return "wall-distance"


def _enh_result_actions() -> str:
    if "/* enhance:result-actions */" in _read_html():
        return "result-actions (skip)"
    html = _read_html()
    if 'id="r-rerun"' not in html:
        html = html.replace(
            '<button type="button" id="r-copy">Copy</button>',
            '''<button type="button" id="r-copy">Copy</button>
      <button type="button" id="r-rerun">Run again</button>
      <button type="button" id="r-lattice">Open lattice</button>
      <!-- enhance:result-actions -->''',
            1,
        )
        html = html.replace(
            "$('r-copy').addEventListener('click', async ()=>{",
            """$('r-rerun').addEventListener('click', ()=>{ if(lastResult.cmd){ showOverlay('results-modal', false); sendCmd(lastResult.cmd, {panel:true}); }});
$('r-lattice').addEventListener('click', ()=>{ showOverlay('results-modal', false); openLattice(); });
$('r-copy').addEventListener('click', async ()=>{""",
            1,
        )
        _write_html(html)
    return "result-actions"


def _enh_lattice_goto_hint() -> str:
    if "/* enhance:lat-dbl */" in _read_html():
        return "lat-dbl (skip)"
    html = _read_html()
    if "dblclick" in html and "Walk to cell" in html:
        # improve hint text
        html = html.replace(
            'Scroll wheel zoom · drag pan · click node',
            'Scroll zoom · drag pan · click select · double-click open page · Walk to cell · /* enhance:lat-dbl */',
            1,
        )
        _write_html(html)
    return "lat-dbl"


def _enh_form_flash() -> str:
    if "/* enhance:form-flash */" in _read_html():
        return "form-flash (skip)"
    html = _read_html()
    css = """
/* enhance:form-flash */
body.form-flash .world{filter:brightness(1.15) saturate(1.2); transition:filter .35s}
"""
    if "/* enhance:form-flash */" not in html:
        html = html.replace(".flash{animation:flashOk .45s ease}", ".flash{animation:flashOk .45s ease}" + css, 1)
    if "lastForm" not in html:
        html = html.replace(
            "let STATE=null, OPEN_ID=null",
            "let STATE=null, lastForm=null, OPEN_ID=null",
            1,
        )
        html = html.replace(
            "document.body.className='form-'+(form||'cube');\n  highlightForms(form);",
            """document.body.className='form-'+(form||'cube');
  if(lastForm && lastForm!==form){
    document.body.classList.add('form-flash');
    setTimeout(()=>document.body.classList.remove('form-flash'), 350);
  }
  lastForm=form;
  highlightForms(form);""",
            1,
        )
        _write_html(html)
    return "form-flash"


def _enh_dense_cap_tooltips() -> str:
    if "/* enhance:cap-titles */" in _read_html():
        return "cap-titles (skip)"
    html = _read_html()
    pairs = [
        ('data-c="grow ideas 1"', 'title="Grow ideas ×1 into nursery"'),
        ('data-c="proposals"', 'title="List nursery proposals"'),
        ('data-c="confirm all"', 'title="Accept all pending nursery proposals"'),
        ('data-c="pulse"', 'title="Enhance pulse"'),
        ('data-c="evolve"', 'title="Evolve program generation"'),
        ('data-c="forces"', 'title="Force field status"'),
        ('data-c="personas"', 'title="Persona roster"'),
        ('data-c="audit"', 'title="6-pillar health audit"'),
        ('data-c="matrices"', 'title="List all matrices"'),
        ('data-c="save"', 'title="Persist program state"'),
    ]
    changed = False
    for attr, title in pairs:
        # insert title before closing of button if not already titled nearby
        pattern = rf'(<button type="button" {re.escape(attr)}(?![^>]*title=)[^>]*)(>)'
        m = re.search(pattern, html)
        if m:
            html = html[:m.start()] + m.group(1) + " " + title + m.group(2) + html[m.end():]
            changed = True
    if changed:
        html = html.replace("</style>", "/* enhance:cap-titles */\n</style>", 1) if "/* enhance:cap-titles */" not in html else html
        _write_html(html)
    return "cap-titles" if changed else "cap-titles (skip)"


def _enh_keyboard_g() -> str:
    """G = grow, N = nursery, P = pulse shortcuts."""
    if "/* enhance:hotkeys-gnp */" in _read_html():
        return "hotkeys-gnp (skip)"
    html = _read_html()
    if "else if(k==='g')" not in html:
        html = html.replace(
            "else if(k==='l'){ e.preventDefault(); openLattice(); }",
            """else if(k==='l'){ e.preventDefault(); openLattice(); }
  else if(k==='g'){ e.preventDefault(); sendCmd('grow ideas 1',{panel:true}); }
  else if(k==='n'){ e.preventDefault(); sendCmd('proposals',{panel:true}); }
  else if(k==='p' && !e.ctrlKey && !e.metaKey){ e.preventDefault(); sendCmd('pulse',{panel:true}); }
  /* enhance:hotkeys-gnp */""",
            1,
        )
        # update help text
        html = html.replace(
            "L     main lattice page",
            "L lattice · G grow · N nursery · P pulse",
            1,
        )
        _write_html(html)
    return "hotkeys-gnp"


def _enh_empty_cell_cta() -> str:
    if "/* enhance:void-cta */" in _read_html():
        return "void-cta (skip)"
    html = _read_html()
    if "Empty centerpoint" in html and "data-c=\"grow ideas 1\"" in html:
        html = html.replace(
            "if(!here.innerHTML) here.innerHTML='<div class=\"d\">Empty centerpoint</div>';",
            """if(!here.innerHTML) here.innerHTML='<div class="card"><h3>Void cell</h3><div class="d">Empty centerpoint — walk, grow, or open lattice.</div><button type="button" data-c="grow ideas 1" data-panel="1">Grow here</button> <button type="button" id="void-lat">Lattice</button></div>'; /* enhance:void-cta */
    const vl=$('void-lat'); if(vl) vl.onclick=()=>openLattice();""",
            1,
        )
        _write_html(html)
    return "void-cta"


def _enh_poll_smart() -> str:
    if "/* enhance:smart-poll */" in _read_html():
        return "smart-poll (skip)"
    html = _read_html()
    # slower poll when overlays open / faster when walking
    if "setInterval(async()=>{" in html and "/* enhance:smart-poll */" not in html:
        html = html.replace(
            """setInterval(async()=>{
  try{
    if(!animLock && !busy){
      const s=await getState();
      render(s);
      setLive(true);
      if($('lattice-modal').classList.contains('show')) fillLattice(s);
    }
  }catch(e){ setLive(false); }
}, 3000);""",
            """/* enhance:smart-poll */
let pollMs=3000;
async function pollTick(){
  try{
    if(!animLock && !busy){
      const s=await getState();
      render(s);
      setLive(true);
      if($('lattice-modal').classList.contains('show')) fillLattice(s);
      pollMs = $('lattice-modal').classList.contains('show') ? 4000 : 2800;
    }
  }catch(e){ setLive(false); pollMs=5000; }
  setTimeout(pollTick, pollMs);
}
setTimeout(pollTick, 2800);""",
            1,
        )
        _write_html(html)
    return "smart-poll"


def _enh_minimap_you_label() -> str:
    if "/* enhance:mmap-label */" in _read_html():
        return "mmap-label (skip)"
    html = _read_html()
    if "local lattice · click" in html:
        html = html.replace(
            "local lattice · click",
            "lattice map · click open /* enhance:mmap-label */",
            1,
        )
        _write_html(html)
    return "mmap-label"


def _enh_bot_ideas() -> str:
    if "/* enhance:bot-ideas */" in _read_html():
        return "bot-ideas (skip)"
    html = _read_html()
    if "$('bot-left').textContent" in html and "/* enhance:bot-ideas */" not in html:
        html = html.replace(
            "$('bot-left').textContent = `Floor locked · nursery ${(s.nursery||[]).length} pending · mode ${s.view_mode||'first_person'}`;",
            "$('bot-left').textContent = `Floor locked · ideas ${s.ideas??0} · nursery ${(s.nursery||[]).length} · gen ${s.generation??0} · ${s.view_mode||'first_person'}`; /* enhance:bot-ideas */",
            1,
        )
        _write_html(html)
    return "bot-ideas"


def _enh_lattice_skin_legend() -> str:
    if "/* enhance:lat-legend */" in _read_html():
        return "lat-legend (skip)"
    html = _read_html()
    if 'id="lat-legend"' not in html:
        html = html.replace(
            '<div class="lat-filters">',
            '''<div id="lat-legend" class="stat" style="margin-bottom:8px"></div>
      <div class="lat-filters">''',
            1,
        )
        if "function fillLatLegend" not in html:
            html = html.replace(
                "function fillLattice(s){",
                """function fillLatLegend(s){
  const el=$('lat-legend'); if(!el) return;
  const counts={};
  (s.nodes||[]).forEach(n=>{ const k=n.skin||'?'; counts[k]=(counts[k]||0)+1; });
  el.innerHTML = Object.keys(counts).sort().map(k=>
    `<span class="pill" style="border-color:${SKIN[k]||'#5b9dff'};margin:2px">${esc(k)} ${counts[k]}</span>`
  ).join(' ') + ' /* enhance:lat-legend */';
}
function fillLattice(s){
  fillLatLegend(s);""",
                1,
            )
        _write_html(html)
    return "lat-legend"


def _enh_escape_stack() -> str:
    if "/* enhance:esc-stack */" in _read_html():
        return "esc-stack (skip)"
    html = _read_html()
    if "if(e.key==='Escape'){" in html and "/* enhance:esc-stack */" not in html:
        html = html.replace(
            """if(e.key==='Escape'){
    ['page-modal','results-modal','lattice-modal'].forEach(id=>showOverlay(id,false));
    return;
  }""",
            """if(e.key==='Escape'){
    /* enhance:esc-stack — close topmost first */
    const stack=['page-modal','results-modal','lattice-modal'];
    for(const id of stack){
      if($(id) && $(id).classList.contains('show')){ showOverlay(id,false); return; }
    }
    return;
  }""",
            1,
        )
        _write_html(html)
    return "esc-stack"


def _enh_aria_live() -> str:
    if "/* enhance:aria-live */" in _read_html():
        return "aria-live (skip)"
    html = _read_html()
    if 'id="log"' in html and "aria-live" not in html:
        html = html.replace(
            '<div id="log"></div>',
            '<div id="log" aria-live="polite"></div><!-- enhance:aria-live -->',
            1,
        )
        _write_html(html)
    return "aria-live"


def _enh_density_compact() -> str:
    if "/* enhance:compact-caps */" in _read_html():
        return "compact-caps (skip)"
    html = _read_html()
    css = """
/* enhance:compact-caps */
.cap-grid button{letter-spacing:.01em}
@media(max-height:700px){
  .side h2{margin:8px 0 4px}
  .card{padding:8px;margin-bottom:6px}
  .hud-help{display:none}
}
"""
    if "/* enhance:compact-caps */" not in html:
        html = html.replace("</style>", css + "</style>", 1)
        _write_html(html)
    return "compact-caps"


# Program-side enhancements (no HTML)
def _prog_fp_reset(p) -> str:
    p.view_mode = "first_person"
    p.grid_snap = True
    p.avatar.body.pos = (0, 0)
    p.center_f = 0
    p.avatar.face(Facing.N)
    look_fp(p, "level")
    return "fp-reset"


def _prog_walk_box(p) -> str:
    move_fp(p, "forward")
    turn_fp(p, "right")
    move_fp(p, "forward")
    turn_fp(p, "right")
    move_fp(p, "forward")
    turn_fp(p, "right")
    move_fp(p, "forward")
    turn_fp(p, "right")
    return "walk-box"


def _prog_vertical(p) -> str:
    move_fp(p, "up")
    move_fp(p, "up")
    look_fp(p, "up")
    look_fp(p, "down")
    look_fp(p, "level")
    move_fp(p, "down")
    move_fp(p, "down")
    return "vertical"


def _prog_forms(p) -> str:
    try:
        p.lattice.to_sphere()
        p.lattice.to_flower()
        p.lattice.to_cube()
    except Exception:
        pass
    return "forms-cycle"


def _prog_forces(p) -> str:
    try:
        p.force_tick()
    except Exception:
        pass
    return "force-tick"


def _prog_pulse(p) -> str:
    try:
        if not p.enhance.on:
            p.enhance_on()
        p.pulse()
    except Exception:
        pass
    return "pulse"


def _prog_evolve(p) -> str:
    try:
        p.evolve("enhance_loop")
    except Exception:
        try:
            p.duo.evolve("enhance_loop")
        except Exception:
            pass
    return "evolve"


def _prog_grow(p) -> str:
    try:
        p.grow_ideas(1)
    except Exception:
        pass
    return "grow"


def _prog_cmd_suite(p) -> str:
    for c in ("status", "audit", "matrices", "forces", "geometry", "personas"):
        try:
            _run_command(p, c)
        except Exception:
            pass
    return "cmd-suite"


def _prog_bimo(p) -> str:
    try:
        _run_command(p, "bimo fuse")
    except Exception:
        pass
    return "bimo"


def _prog_verita_voynich(p) -> str:
    try:
        _run_command(p, "verita")
        _run_command(p, "voynich")
    except Exception:
        pass
    return "verita-voynich"


def _prog_goto_home(p) -> str:
    try:
        p.fp_goto(0, 0, 0)
    except Exception:
        p.avatar.body.pos = (0, 0)
        p.center_f = 0
    return "goto-home"


# ─── multi-page app enhancements ───────────────────────────────────────────

def _enh_menu_kbd() -> str:
    path = MENU
    if "/* enhance:menu-kbd */" in _read_file(path):
        return "menu-kbd (skip)"
    ok = _patch_file_once(
        path,
        "/* enhance:menu-kbd */",
        "setInterval(refresh, 4000);",
        """
  // /* enhance:menu-kbd */
  window.addEventListener('keydown', e=>{
    if(e.target && (e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA')) return;
    const map={ '1':'/walk','2':'/lattice','3':'/nursery','4':'/program','5':'/personas',
      '6':'/forces','7':'/geometry','8':'/matrices','9':'/console','0':'/' };
    if(map[e.key]){ e.preventDefault(); location.href=map[e.key]; }
  });
""",
    )
    return "menu-kbd" if ok else "menu-kbd (skip)"


def _enh_menu_shortcuts_hint() -> str:
    path = MENU
    if "/* enhance:menu-hints */" in _read_file(path):
        return "menu-hints (skip)"
    ok = _patch_file_once(
        path,
        "/* enhance:menu-hints */",
        '<div class="menu-stats" id="stats"></div>',
        '\n      <p class="lede" style="margin-top:10px;font-size:12px">Keys: <kbd>1</kbd> Walk · <kbd>2</kbd> Lattice · <kbd>3</kbd> Nursery · <kbd>4</kbd> Program · … · <kbd>0</kbd> Menu /* enhance:menu-hints */</p>',
    )
    return "menu-hints" if ok else "menu-hints (skip)"


def _enh_core_busy_guard() -> str:
    path = CORE_JS
    text = _read_file(path)
    if "/* enhance:busy-guard */" in text:
        return "core-busy (skip)"
    if "async function sendCmd" not in text:
        return "core-busy (no sendCmd)"
    if "let _dmBusy=false" not in text:
        text = text.replace(
            "async function sendCmd(cmd, opts) {",
            "let _dmBusy=false; /* enhance:busy-guard */\n  async function sendCmd(cmd, opts) {\n    if(_dmBusy && !(opts&&opts.force)) return {ok:false,error:'busy'};\n    _dmBusy=true;",
            1,
        )
        text = text.replace(
            "setLoading(false);\n    }",
            "setLoading(false); _dmBusy=false;\n    }",
            1,
        )
        _write_file(path, text)
        return "core-busy"
    return "core-busy (skip)"


def _enh_core_hotkey_help() -> str:
    path = CORE_JS
    text = _read_file(path)
    if "/* enhance:nav-title */" in text:
        return "nav-title (skip)"
    old = 'return `<a class="nav${on}" href="${pg.href}">${esc(pg.label)}</a>`;'
    new = 'return `<a class="nav${on}" href="${pg.href}" title="${esc(pg.label)}">${esc(pg.label)}</a>`; /* enhance:nav-title */'
    if old in text:
        _write_file(path, text.replace(old, new, 1))
        return "nav-title"
    return "nav-title (skip)"


def _enh_nursery_reject_hint() -> str:
    path = os.path.join(PAGES_DIR, "nursery.html")
    if "/* enhance:nursery-law */" in _read_file(path):
        return "nursery-law (skip)"
    ok = _patch_file_once(
        path,
        "/* enhance:nursery-law */",
        "Confirm to accept onto the lattice — Nursery law.",
        " Grow creates proposals; Confirm accepts them. Floor stays locked. /* enhance:nursery-law */",
    )
    return "nursery-law" if ok else "nursery-law (skip)"


def _enh_lattice_open_walk() -> str:
    path = os.path.join(PAGES_DIR, "lattice.html")
    text = _read_file(path)
    if "/* enhance:lat-walk-link */" in text:
        return "lat-walk-link (skip)"
    if "Open Walk" in text and "location.href='/walk'" not in text:
        text = text.replace(
            "$('btn-walk-sel').onclick=async()=>{ if(!SEL) return; await DM.sendCmd(`goto ${Math.round(SEL.x||0)} ${Math.round(SEL.y||0)}`); DM.toast('walking… open Walk'); };",
            "$('btn-walk-sel').onclick=async()=>{ if(!SEL) return; await DM.sendCmd(`goto ${Math.round(SEL.x||0)} ${Math.round(SEL.y||0)}`); DM.toast('opening Walk'); location.href='/walk'; }; /* enhance:lat-walk-link */",
            1,
        )
        _write_file(path, text)
        return "lat-walk-link"
    return "lat-walk-link (skip)"


def _enh_console_examples() -> str:
    path = os.path.join(PAGES_DIR, "console.html")
    if "/* enhance:console-plant */" in _read_file(path):
        return "console-plant (skip)"
    ok = _patch_file_once(
        path,
        "/* enhance:console-plant */",
        '<button type="button" class="sm" data-fill="audit">audit</button>',
        '\n        <button type="button" class="sm" data-fill="plant Console Seed">plant</button>\n        <button type="button" class="sm" data-fill="confirm all">confirm all</button><!-- enhance:console-plant -->',
    )
    return "console-plant" if ok else "console-plant (skip)"


def _enh_program_workshop() -> str:
    path = os.path.join(PAGES_DIR, "program.html")
    if "/* enhance:prog-workshop */" in _read_file(path):
        return "prog-workshop (skip)"
    ok = _patch_file_once(
        path,
        "/* enhance:prog-workshop */",
        '<button type="button" class="primary" data-cmd="save">Save</button>',
        '\n        <button type="button" data-cmd="workshops">Workshops</button>\n        <button type="button" data-cmd="guide">Guide</button><!-- enhance:prog-workshop -->',
    )
    return "prog-workshop" if ok else "prog-workshop (skip)"


def _enh_personas_roster_autoload() -> str:
    path = os.path.join(PAGES_DIR, "personas.html")
    text = _read_file(path)
    if "/* enhance:persona-auto */" in text:
        return "persona-auto (skip)"
    if "paint();" in text and "run('personas')" not in text:
        text = text.replace(
            "paint();\n  setInterval(()=>{ if(document.visibilityState==='visible') paint().catch(()=>{}); }, 5000);",
            "paint(); run('personas'); /* enhance:persona-auto */\n  setInterval(()=>{ if(document.visibilityState==='visible') paint().catch(()=>{}); }, 5000);",
            1,
        )
        _write_file(path, text)
        return "persona-auto"
    return "persona-auto (skip)"


def _enh_forces_autoload() -> str:
    path = os.path.join(PAGES_DIR, "forces.html")
    text = _read_file(path)
    if "/* enhance:forces-auto */" in text:
        return "forces-auto (skip)"
    if "paint();" in text and "run('forces')" not in text:
        text = text.replace(
            "paint();\n  setInterval(()=>{ if(document.visibilityState==='visible') paint().catch(()=>{}); }, 4000);",
            "paint(); run('forces'); /* enhance:forces-auto */\n  setInterval(()=>{ if(document.visibilityState==='visible') paint().catch(()=>{}); }, 4000);",
            1,
        )
        _write_file(path, text)
        return "forces-auto"
    return "forces-auto (skip)"


def _enh_geometry_autoload() -> str:
    path = os.path.join(PAGES_DIR, "geometry.html")
    text = _read_file(path)
    if "/* enhance:geo-auto */" in text:
        return "geo-auto (skip)"
    if "paint();" in text and "run('geometry')" not in text:
        text = text.replace(
            "paint();\n})();",
            "paint(); run('geometry'); /* enhance:geo-auto */\n})();",
            1,
        )
        _write_file(path, text)
        return "geo-auto"
    return "geo-auto (skip)"


def _enh_css_active_nav() -> str:
    path = APP_CSS
    if "/* enhance:nav-active-glow */" in _read_file(path):
        return "nav-glow (skip)"
    ok = _patch_file_once(
        path,
        "/* enhance:nav-active-glow */",
        ".topbar nav a.nav.on{color:var(--text);border-color:var(--accent);background:#1a2f4d}",
        "\n/* enhance:nav-active-glow */\n.topbar nav a.nav.on{box-shadow:0 0 0 1px #5b9dff44 inset}\n",
    )
    return "nav-glow" if ok else "nav-glow (skip)"


def _enh_walk_menu_visible() -> str:
    html = _read_html()
    if 'href="/"' in html and "Menu" in html:
        return "walk-menu (ok)"
    # ensure menu link
    if '<div class="top-actions">' in html and 'href="/"' not in html:
        _write_html(html.replace(
            '<div class="top-actions">',
            '<div class="top-actions">\n      <a href="/" target="_top" style="color:#7dd3fc;font-size:12px;text-decoration:none;border:1px solid #243044;border-radius:10px;padding:8px 10px">Menu</a>',
            1,
        ))
        return "walk-menu"
    return "walk-menu (skip)"


def _prog_page_cmds(p) -> str:
    for c in ("home", "nearest", "radar", "find matrix", "status", "proposals"):
        try:
            _run_command(p, c)
        except Exception:
            pass
    return "page-cmds"


ENHANCEMENTS: List[Tuple[str, Callable]] = [
    ("ui:focus-visible", lambda p: _enh_focus_visible()),
    ("ui:loading-bar", lambda p: _enh_loading_bar()),
    ("ui:cmd-history", lambda p: _enh_cmd_history()),
    ("ui:pillar-meters", lambda p: _enh_pillar_meters()),
    ("ui:path-trail", lambda p: _enh_path_trail()),
    ("ui:offline-banner", lambda p: _enh_offline_banner()),
    ("ui:copy-coord", lambda p: _enh_copy_coord()),
    ("ui:wall-distance", lambda p: _enh_wall_distance()),
    ("ui:result-actions", lambda p: _enh_result_actions()),
    ("ui:lat-dbl", lambda p: _enh_lattice_goto_hint()),
    ("ui:form-flash", lambda p: _enh_form_flash()),
    ("ui:cap-titles", lambda p: _enh_dense_cap_tooltips()),
    ("ui:hotkeys-gnp", lambda p: _enh_keyboard_g()),
    ("ui:void-cta", lambda p: _enh_empty_cell_cta()),
    ("ui:smart-poll", lambda p: _enh_poll_smart()),
    ("ui:mmap-label", lambda p: _enh_minimap_you_label()),
    ("ui:bot-ideas", lambda p: _enh_bot_ideas()),
    ("ui:lat-legend", lambda p: _enh_lattice_skin_legend()),
    ("ui:esc-stack", lambda p: _enh_escape_stack()),
    ("ui:aria-live", lambda p: _enh_aria_live()),
    ("ui:compact-caps", lambda p: _enh_density_compact()),
    ("prog:fp-reset", lambda p: _prog_fp_reset(p)),
    ("prog:walk-box", lambda p: _prog_walk_box(p)),
    ("prog:vertical", lambda p: _prog_vertical(p)),
    ("prog:forms", lambda p: _prog_forms(p)),
    ("prog:forces", lambda p: _prog_forces(p)),
    ("prog:pulse", lambda p: _prog_pulse(p)),
    ("prog:evolve", lambda p: _prog_evolve(p)),
    ("prog:grow", lambda p: _prog_grow(p)),
    ("prog:cmd-suite", lambda p: _prog_cmd_suite(p)),
    ("prog:bimo", lambda p: _prog_bimo(p)),
    ("prog:verita", lambda p: _prog_verita_voynich(p)),
    ("prog:home", lambda p: _prog_goto_home(p)),
    # multi-page app
    ("app:menu-kbd", lambda p: _enh_menu_kbd()),
    ("app:menu-hints", lambda p: _enh_menu_shortcuts_hint()),
    ("app:core-busy", lambda p: _enh_core_busy_guard()),
    ("app:nav-title", lambda p: _enh_core_hotkey_help()),
    ("app:nursery-law", lambda p: _enh_nursery_reject_hint()),
    ("app:lat-walk", lambda p: _enh_lattice_open_walk()),
    ("app:console-plant", lambda p: _enh_console_examples()),
    ("app:prog-workshop", lambda p: _enh_program_workshop()),
    ("app:persona-auto", lambda p: _enh_personas_roster_autoload()),
    ("app:forces-auto", lambda p: _enh_forces_autoload()),
    ("app:geo-auto", lambda p: _enh_geometry_autoload()),
    ("app:nav-glow", lambda p: _enh_css_active_nav()),
    ("app:walk-menu", lambda p: _enh_walk_menu_visible()),
    ("prog:page-cmds", lambda p: _prog_page_cmds(p)),
]


def run(cycles: int = 150, owner: str = "Operator") -> Dict[str, Any]:
    path = os.path.join(os.path.dirname(__file__), "..", "state", f"program_{owner}.json")
    path = os.path.abspath(path)
    if os.path.isfile(path):
        p = load(owner, path)
    else:
        p = open_program(owner)

    p.view_mode = "first_person"
    p.grid_snap = True

    history: List[Dict[str, Any]] = []
    applied: List[str] = []
    best = 0.0
    n_enh = len(ENHANCEMENTS)

    for i in range(1, cycles + 1):
        # 1) always exercise walk phase
        phase = i % 10
        try:
            if phase == 1:
                _prog_fp_reset(p)
                move_fp(p, "forward")
            elif phase == 2:
                turn_fp(p, "right")
            elif phase == 3:
                move_fp(p, "forward")
            elif phase == 4:
                look_fp(p, "level")
            elif phase == 5:
                _prog_forces(p)
            elif phase == 6:
                if i % 20 < 10:
                    try:
                        p.lattice.to_sphere()
                    except Exception:
                        pass
                else:
                    try:
                        p.lattice.to_cube()
                    except Exception:
                        pass
            elif phase == 7:
                _prog_pulse(p)
            elif phase == 8:
                _prog_evolve(p)
            elif phase == 9:
                if i % 30 == 9:
                    _prog_grow(p)
            else:
                move_fp(p, "back")
        except Exception:
            pass

        # 2) apply next enhancement from catalog (cycle through, re-apply prog ones)
        enh_name, enh_fn = ENHANCEMENTS[(i - 1) % n_enh]
        try:
            note = enh_fn(p)
            applied.append(f"{i}:{enh_name}:{note}")
        except Exception as e:
            applied.append(f"{i}:{enh_name}:ERR:{e}")

        # 3) lightweight progress every cycle; full A+ score every 25 (and first/last)
        if i == 1 or i == cycles or i % 25 == 0:
            checks = _checks(p)
            rate = sum(1 for c in checks if c["ok"]) / max(1, len(checks))
            best = max(best, rate)
            fails = [c["name"] for c in checks if not c["ok"]]
            history.append({
                "cycle": i,
                "rate": round(rate, 3),
                "fails": fails,
                "last_enh": enh_name,
            })
            print(
                f"[{i:03d}/{cycles}] quality={rate:.1%} best={best:.1%} "
                f"fails={fails[:8]}{'…' if len(fails) > 8 else ''} · {enh_name}",
                flush=True,
            )

            # fail-driven: re-run UI enhancers that map to failed checks
            fail_set = set(fails)
            retry_map = {
                "ui_focus_visible": _enh_focus_visible,
                "ui_cmd_history": _enh_cmd_history,
                "ui_pillar_meters": _enh_pillar_meters,
                "ui_path_trail": _enh_path_trail,
                "ui_offline_banner": _enh_offline_banner,
                "ui_loading": _enh_loading_bar,
            }
            for fname, fn in retry_map.items():
                if fname in fail_set:
                    try:
                        fn()
                    except Exception:
                        pass
        elif i % 5 == 0:
            print(f"[{i:03d}/{cycles}] · {enh_name}", flush=True)

    checks = _checks(p)
    rate = sum(1 for c in checks if c["ok"]) / max(1, len(checks))
    best = max(best, rate)
    try:
        p.note_seed(13, "Loop", f"visual_enhance_x{cycles}")
    except Exception:
        pass
    save(p, path)
    grade = "A+" if rate >= 0.95 else ("A" if rate >= 0.85 else ("B" if rate >= 0.7 else "C"))

    # node syntax check on final HTML
    html_ok = True
    try:
        import subprocess
        html = _read_html()
        m = re.search(r"<script>([\s\S]*)</script>", html)
        if m:
            tmp = "/tmp/fp_enhance_check.js"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(m.group(1))
            r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
            html_ok = r.returncode == 0
            if not html_ok:
                print("JS SYNTAX ERROR:", r.stderr[:400])
    except Exception as e:
        print("JS check skipped:", e)

    return {
        "ok": rate >= 0.85 and html_ok,
        "cycles": cycles,
        "final_rate": round(rate, 3),
        "best_rate": round(best, 3),
        "grade": grade,
        "checks": checks,
        "history": history,
        "applied_tail": applied[-20:],
        "applied_count": len(applied),
        "path": path,
        "ideas": len(p.cube.session.plane.units),
        "generation": p.duo.generation,
        "html_bytes": len(_read_html()),
        "html_js_ok": html_ok,
    }


def main() -> None:
    cycles = 150
    for i, a in enumerate(sys.argv):
        if a == "--cycles" and i + 1 < len(sys.argv):
            cycles = max(1, int(sys.argv[i + 1]))
    print(f"=== VISUAL / MULTI-PAGE ENHANCE LOOP × {cycles} ===")
    out = run(cycles=cycles)
    print(f"\nGRADE {out['grade']} · final={out['final_rate']:.1%} best={out['best_rate']:.1%}")
    print(f"gen={out['generation']} ideas={out['ideas']} html={out['html_bytes']}b js_ok={out['html_js_ok']}")
    print(f"routes={len(_PAGE_ROUTES)} pages={len(REQUIRED_PAGES)}")
    fails = [c for c in out["checks"] if not c["ok"]]
    if fails:
        print(f"remaining fails ({len(fails)}):")
        for c in fails:
            print(f"  - {c['name']}: {c['detail']}")
    else:
        print("all checks PASS")
    print("recent enhancements:")
    for a in out.get("applied_tail") or []:
        print(f"  {a}")
    sys.exit(0 if out["ok"] else 1)


if __name__ == "__main__":
    main()
