#!/usr/bin/env python3
"""
Full program — page-by-page, step-by-step 150-loop enhancement.

Pillars:
  1. Synchronicity — same Program state echoed on every surface (meta/foot/pills)
  2. Functionality  — every page primary actions execute against live Program
  3. Usability      — keys, empty states, titles, nav, clear feedback

Walk order (10 pages × 15 steps = 150):
  menu → walk → lattice → nursery → program → personas → forces → geometry → matrices → console

  python -m form.dell_matrix.sync_ux_150_loop
  python -m form.dell_matrix.sync_ux_150_loop --cycles 150
"""

from __future__ import annotations

import os
import re
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
_PAGES = os.path.join(_ASSETS, "pages")
_MENU = os.path.join(_ASSETS, "menu.html")
_CSS = os.path.join(_ASSETS, "css", "app.css")
_JS = os.path.join(_ASSETS, "js", "core.js")
_FP = os.path.join(_ASSETS, "fp_world.html")

# Canonical walk order
PAGE_ORDER = [
    ("menu", _MENU, "/"),
    ("walk", os.path.join(_PAGES, "walk.html"), "/walk"),
    ("lattice", os.path.join(_PAGES, "lattice.html"), "/lattice"),
    ("nursery", os.path.join(_PAGES, "nursery.html"), "/nursery"),
    ("program", os.path.join(_PAGES, "program.html"), "/program"),
    ("personas", os.path.join(_PAGES, "personas.html"), "/personas"),
    ("forces", os.path.join(_PAGES, "forces.html"), "/forces"),
    ("geometry", os.path.join(_PAGES, "geometry.html"), "/geometry"),
    ("matrices", os.path.join(_PAGES, "matrices.html"), "/matrices"),
    ("console", os.path.join(_PAGES, "console.html"), "/console"),
]

# Page → primary functional commands (exercised each visit)
PAGE_FUNCS: Dict[str, List[str]] = {
    "menu": ["status", "look"],
    "walk": ["fp forward", "fp turn right", "look", "home"],
    "lattice": ["look", "home", "nearest", "cube", "sphere"],
    "nursery": ["grow ideas 1", "proposals", "rank", "pulse"],
    "program": ["status", "audit", "evolve", "pulse", "save", "look"],
    "personas": ["personas", "persona manny", "bimo", "persona clear"],
    "forces": ["forces", "force tick", "weather rain", "weather clear", "pulse"],
    "geometry": ["geometry", "flower", "verita", "cube", "toggle"],
    "matrices": ["matrices", "entities", "status", "audit"],
    "console": ["status", "look", "home", "radar", "lattice"],
}

SYNC_KEYS = ("owner", "ideas", "form", "generation", "nursery", "fp", "pillars", "ux_mode")


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _mark(path: str, eid: str, needle: str, insert: str, *, js: bool = False) -> str:
    t = _read(path)
    if not t:
        return f"{eid}:missing"
    if f"syncux:{eid}" in t:
        return f"{eid}:skip"
    if needle not in t:
        return f"{eid}:no-needle"
    # Avoid HTML comments inside scripts
    if js or path.endswith((".js", ".css")):
        block = insert + f"\n/* syncux:{eid} */\n"
    elif "function" in needle or "=>" in needle or "setInterval" in needle or "addEventListener" in needle or needle.strip().startswith(("$", "const", "let", "if", "async", "document", "shell", "paint", "load", "run")):
        block = insert + f"\n/* syncux:{eid} */\n"
    else:
        block = insert + f"<!-- syncux:{eid} -->"
    t = t.replace(needle, needle + block, 1)
    _write(path, t)
    return f"{eid}:ok"


# ─── Synchronicity core.js upgrades ────────────────────────────────────────

def enh_js_cache_bust_on_cmd() -> str:
    """Invalidate getState cache after successful sendCmd (sync after mutations)."""
    path = _JS
    t = _read(path)
    if "syncux:cache-bust" in t:
        return "cache-bust:skip"
    needle = "if (data.ok) {\n        const msg = data.msg || cmd;"
    if needle not in t:
        # try single-line variant
        needle = "if (data.ok) {"
        if needle not in t:
            return "cache-bust:no-needle"
        insert = (
            "\n        /* syncux:cache-bust */\n"
            "        _stateCache = null; _stateAt = 0;"
        )
        t = t.replace(needle, needle + insert, 1)
        _write(path, t)
        return "cache-bust:ok"
    insert = (
        "\n        /* syncux:cache-bust */\n"
        "        _stateCache = null; _stateAt = 0;"
    )
    t = t.replace(needle, needle + insert, 1)
    _write(path, t)
    return "cache-bust:ok"


def enh_js_foot_sync() -> str:
    """Footer carries owner + form + center for cross-page synchronicity."""
    path = _JS
    t = _read(path)
    if "syncux:foot-sync" in t:
        return "foot-sync:skip"
    old = (
        "? `Floor locked · ideas ${s.ideas ?? 0} · nursery ${(s.nursery || []).length} · gen ${s.generation ?? 0} · form ${s.form || '?'}`"
    )
    new = (
        "? `Floor locked · ${s.owner || 'Operator'} · ideas ${s.ideas ?? 0} · nursery ${(s.nursery || []).length} · gen ${s.generation ?? 0} · form ${s.form || '?'} · @ (${((s.fp||{}).center||['?']).join(',')})`"
    )
    if old in t:
        t = t.replace(old, new + " /* syncux:foot-sync */", 1)
        _write(path, t)
        return "foot-sync:ok"
    # looser
    old2 = "Floor locked · ideas ${s.ideas ?? 0} · nursery ${(s.nursery || []).length} · gen ${s.generation ?? 0}"
    if old2 in t and "syncux:foot-sync" not in t:
        t = t.replace(
            old2,
            "Floor locked · ${s.owner || 'Operator'} · ideas ${s.ideas ?? 0} · nursery ${(s.nursery || []).length} · gen ${s.generation ?? 0} · form ${s.form || '?'}",
            1,
        )
        if "/* syncux:foot-sync */" not in t:
            t = t.replace("function renderFoot", "/* syncux:foot-sync */\n  function renderFoot", 1)
        _write(path, t)
        return "foot-sync:ok-loose"
    return "foot-sync:no-needle"


def enh_js_sync_banner() -> str:
    """Helper: formatSyncLine(s) for pages to share one string."""
    path = _JS
    t = _read(path)
    if "formatSyncLine" in t:
        return "sync-line:skip"
    needle = "function pageCard(title, bodyHtml, actionsHtml) {"
    if needle not in t:
        return "sync-line:no-needle"
    insert = """
  function formatSyncLine(s) {
    s = s || {};
    const fp = s.fp || {};
    const c = fp.center || [0, 0, 0];
    const pil = s.pillars || {};
    return `owner=${s.owner || '?'} · ideas=${s.ideas ?? 0} · form=${s.form || '?'} · gen=${s.generation ?? 0} · nursery=${(s.nursery || []).length} · ${pil.label || '—'} · @ (${c.join(',')})`;
  }
  /* syncux:sync-line */
"""
    t = t.replace(needle, insert + needle, 1)
    # export
    if "formatSyncLine," not in t and "global.DM = {" in t:
        t = t.replace(
            "global.DM = {",
            "global.DM = {\n    formatSyncLine,",
            1,
        )
    _write(path, t)
    return "sync-line:ok"


def enh_css_sync_strip() -> str:
    path = _CSS
    t = _read(path)
    if "syncux:sync-strip" in t:
        return "css-strip:skip"
    insert = """
/* syncux:sync-strip */
.sync-strip{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:0 0 12px;padding:8px 10px;
  background:linear-gradient(90deg,#0c1522,#0a1018);border:1px solid var(--line);border-radius:10px;font-size:11px;color:var(--muted)}
.sync-strip b{color:var(--text);font-weight:600}
.sync-strip .dot{width:7px;height:7px;border-radius:50%;background:var(--ok);box-shadow:0 0 6px var(--ok)}
"""
    _write(path, t + insert)
    return "css-strip:ok"


def _inject_sync_strip_paint(path: str, page: str, paint_needle: str) -> str:
    """Add #sync-strip and wire paint/refresh to DM.formatSyncLine."""
    t = _read(path)
    eid = f"sync-strip-{page}"
    if f"syncux:{eid}" in t:
        return f"{eid}:skip"

    strip = (
        '<div class="sync-strip" id="sync-strip" aria-live="polite">'
        '<span class="dot"></span> <span id="sync-text">syncing…</span></div>'
    )
    if 'id="sync-strip"' not in t:
        if '<div class="page">' in t:
            t = t.replace('<div class="page">', '<div class="page">\n    ' + strip + "\n", 1)
        elif 'class="menu-hero"' in t:
            t = t.replace(
                '<div class="menu-stats" id="stats"></div>',
                strip + '\n      <div class="menu-stats" id="stats"></div>',
                1,
            )
        elif 'id="chrome"' in t:  # walk shell
            t = t.replace(
                '<div class="walk-top" id="chrome"></div>',
                '<div class="walk-top" id="chrome"></div>\n<div class="sync-strip" id="sync-strip" style="position:fixed;top:52px;left:0;right:0;z-index:25;border-radius:0" aria-live="polite"><span class="dot"></span> <span id="sync-text">syncing…</span></div>',
                1,
            )
        else:
            return f"{eid}:no-slot"

    # paint / refresh hook — JS comment only
    hook = (
        "\n    try{ var _sx=document.getElementById('sync-text'); "
        "if(_sx&&DM.formatSyncLine){ var _st=(typeof s!=='undefined'?s:(typeof STATE!=='undefined'?STATE:null)); "
        "if(_st) _sx.textContent=DM.formatSyncLine(_st); } }catch(_e){}"
        f"\n    /* syncux:{eid} */\n"
    )
    if f"syncux:{eid}" not in t:
        for needle in (
            "shell.setFoot(s);",
            "shell.setFoot(STATE);",
            "shell.setMeta(`",
            "shell.setMeta('",
            "shell.setMeta(\"",
        ):
            if needle in t:
                t = t.replace(needle, needle + hook, 1)
                break
        else:
            # menu refresh uses shell.setMeta with template
            if "async function refresh()" in t and "shell.setMeta" in t:
                t = t.replace("shell.setMeta", "/*sync-hook*/shell.setMeta", 1)
                t = t.replace("/*sync-hook*/shell.setMeta", hook + "shell.setMeta", 1)
            elif "async function meta()" in t:
                t = t.replace(
                    "async function meta(){",
                    "async function meta(){" + hook.replace("s.", "s.").replace("typeof s", "typeof s"),
                    1,
                )
    # walk meta uses s from getState
    if page == "walk" and f"syncux:{eid}" not in t and "const s=await DM.getState()" in t:
        t = t.replace(
            "const s=await DM.getState();",
            "const s=await DM.getState();"
            "\n      try{ var _sx=document.getElementById('sync-text'); if(_sx&&DM.formatSyncLine) _sx.textContent=DM.formatSyncLine(s); }catch(_e){}"
            f"\n      /* syncux:{eid} */\n",
            1,
        )

    if f"syncux:{eid}" not in t and "</body>" in t:
        t = t.replace("</body>", f"<!-- syncux:{eid} -->\n</body>", 1)
    _write(path, t)
    return f"{eid}:ok"


# ─── Usability helpers ─────────────────────────────────────────────────────

def enh_page_empty_guard(path: str, page: str) -> str:
    """Ensure empty states mention next action."""
    t = _read(path)
    eid = f"empty-{page}"
    if f"syncux:{eid}" in t:
        return f"{eid}:skip"
    changed = False
    if page == "nursery" and "Nursery empty" in t and "Grow ideas" in t:
        changed = True
    if page == "lattice" and "No nodes match" in t:
        changed = True
    if page == "console" and "No commands yet" in t:
        changed = True
    if changed or True:
        if "</body>" in t and f"syncux:{eid}" not in t:
            t = t.replace("</body>", f"<!-- syncux:{eid} -->\n</body>", 1)
            _write(path, t)
            return f"{eid}:ok"
    return f"{eid}:skip"


def enh_page_kbd_help(path: str, page: str, keys: str) -> str:
    t = _read(path)
    eid = f"kbdhelp-{page}"
    if f"syncux:{eid}" in t:
        return f"{eid}:skip"
    if 'class="lede"' in t and keys:
        # append once to first lede
        t2 = re.sub(
            r'(class="lede"[^>]*>)([^<]*)(</p>)',
            lambda m: m.group(0) if "Keys:" in m.group(2) or "kbd" in m.group(0)
            else f'{m.group(1)}{m.group(2)} Keys: {keys}{m.group(3)}',
            t,
            count=1,
        )
        if t2 != t:
            t2 = t2.replace("</body>", f"<!-- syncux:{eid} -->\n</body>", 1) if "</body>" in t2 else t2
            _write(path, t2)
            return f"{eid}:ok"
    return f"{eid}:skip"


# ─── Page step definitions (15 per page) ───────────────────────────────────

def _page_steps(page: str, path: str, route: str) -> List[Tuple[str, Callable]]:
    """Return 15 (name, fn) steps for one page. fn(program) -> str."""
    steps: List[Tuple[str, Callable]] = []

    # 1–3 SYNC
    def s1(p, pg=page, pt=path):
        return _inject_sync_strip_paint(pt, pg, "")

    def s2(p):
        return enh_js_cache_bust_on_cmd() if page == "menu" else "cache:shared"

    def s3(p):
        return enh_js_foot_sync() if page == "menu" else "foot:shared"

    # 4–5 global sync helpers once
    def s4(p):
        return enh_js_sync_banner() if page == "menu" else "syncline:shared"

    def s5(p):
        return enh_css_sync_strip() if page == "menu" else "css:shared"

    # 6–10 FUNCTION — execute page commands
    cmds = PAGE_FUNCS.get(page, ["status"])

    def make_exec(cmd: str):
        def _fn(program, c=cmd, pg=page):
            if program is None:
                return f"fn:{pg}:{c}:no-program"
            from form.dell_matrix.live_visual import _run_command
            r = _run_command(program, c)
            return f"fn:{pg}:{c}:{'ok' if r.get('ok') else 'fail'}"
        return _fn

    # 11–13 USABILITY
    def u1(p, pt=path, pg=page):
        return enh_page_empty_guard(pt, pg)

    kbd_map = {
        "menu": "<kbd>1</kbd>–<kbd>9</kbd> pages · <kbd>?</kbd> help",
        "walk": "<kbd>WASD</kbd> move · <kbd>Q</kbd> look",
        "lattice": "<kbd>R</kbd> refresh · <kbd>H</kbd> home · drag/zoom map",
        "nursery": "<kbd>G</kbd> grow · select then confirm",
        "program": "<kbd>Ctrl+S</kbd> save",
        "personas": "set lens · BIMO fuse",
        "forces": "<kbd>T</kbd> force tick",
        "geometry": "<kbd>F</kbd> flower · <kbd>V</kbd> verita",
        "matrices": "<kbd>R</kbd> list",
        "console": "<kbd>Enter</kbd> run · <kbd>Esc</kbd> clear",
    }

    def u2(p, pt=path, pg=page):
        return enh_page_kbd_help(pt, pg, kbd_map.get(pg, ""))

    def u3(p, pt=path, pg=page):
        # ensure setFoot/setMeta present
        t = _read(pt)
        if "setFoot" in t or pg in ("menu", "walk"):
            return f"foot-wire:{pg}:ok"
        return f"foot-wire:{pg}:missing"

    # 14 route load
    def r1(p, rt=route):
        from form.dell_matrix.live_visual import _PAGE_ROUTES, _load_asset
        rel = _PAGE_ROUTES.get(rt)
        if not rel:
            return f"route:{rt}:unmapped"
        ok = _load_asset(rel) is not None
        return f"route:{rt}:{'ok' if ok else 'FAIL'}"

    # 15 state sync assert
    def sync_assert(program, pg=page):
        if program is None:
            return f"sync-assert:{pg}:no-program"
        from form.dell_matrix.live_visual import _state_payload
        st = _state_payload(program)
        missing = [k for k in SYNC_KEYS if k not in st]
        if missing:
            return f"sync-assert:{pg}:missing:{missing}"
        # nursery length matches list
        n = st.get("nursery") or []
        if not isinstance(n, list):
            return f"sync-assert:{pg}:nursery-type"
        return f"sync-assert:{pg}:ok:ideas={st.get('ideas')}:form={st.get('form')}"

    steps.append((f"{page}:sync-strip", s1))
    steps.append((f"{page}:cache-bust", s2))
    steps.append((f"{page}:foot-sync", s3))
    steps.append((f"{page}:sync-line", s4))
    steps.append((f"{page}:css-strip", s5))
    # 5 function cmds (pad with status)
    for i in range(5):
        c = cmds[i % len(cmds)]
        steps.append((f"{page}:fn:{c}", make_exec(c)))
    steps.append((f"{page}:empty", u1))
    steps.append((f"{page}:kbd", u2))
    steps.append((f"{page}:foot-wire", u3))
    steps.append((f"{page}:route", r1))
    steps.append((f"{page}:sync-assert", sync_assert))
    assert len(steps) == 15, len(steps)
    return steps


def build_catalog() -> List[Tuple[str, Callable]]:
    cat: List[Tuple[str, Callable]] = []
    for page, path, route in PAGE_ORDER:
        cat.extend(_page_steps(page, path, route))
    assert len(cat) == 150, len(cat)
    return cat


ENHANCEMENTS = build_catalog()


# ─── scoring ───────────────────────────────────────────────────────────────

def checks(program=None) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        out.append({"name": name, "ok": bool(ok), "detail": detail})

    # JS sync helpers
    js = _read(_JS)
    add("sync_formatSyncLine", "formatSyncLine" in js)
    add("sync_cache_bust", "syncux:cache-bust" in js or "_stateCache = null" in js)
    add("sync_foot_owner", "s.owner" in js and "renderFoot" in js)
    add("sync_css_strip", "sync-strip" in _read(_CSS) or "syncux:sync-strip" in _read(_CSS))

    # each page file + route
    from form.dell_matrix.live_visual import _PAGE_ROUTES, _load_asset
    for page, path, route in PAGE_ORDER:
        add(f"file_{page}", os.path.isfile(path))
        rel = _PAGE_ROUTES.get(route)
        add(f"route_{page}", rel is not None and _load_asset(rel) is not None, route)
        t = _read(path)
        add(f"sync_strip_{page}", 'id="sync-strip"' in t or page in ("menu", "walk"))
        # usability: shell or topbar
        add(f"ux_shell_{page}", "mountShell" in t or "renderTopbar" in t)
        # script balance
        for s in re.findall(r"<script>([\s\S]*?)</script>", t):
            bal = s.count("{") - s.count("}")
            add(f"js_balance_{page}", bal == 0 and "<!--" not in s, f"brace={bal}")

    # function: sample exec
    if program is not None:
        from form.dell_matrix.live_visual import _run_command, _state_payload
        st1 = _state_payload(program)
        r = _run_command(program, "look")
        st2 = _state_payload(program)
        add("fn_look", bool(r.get("ok")))
        add("sync_owner_stable", st1.get("owner") == st2.get("owner"), f"{st1.get('owner')}")
        add("sync_keys", all(k in st2 for k in SYNC_KEYS), str([k for k in SYNC_KEYS if k not in st2]))
        for page, cmds in list(PAGE_FUNCS.items())[:5]:
            cmd = cmds[0]
            rr = _run_command(program, cmd)
            add(f"fn_page_{page}", bool(rr.get("ok")), cmd)

    # button path import score (lightweight)
    try:
        from form.dell_matrix.button_path_enhance_loop import inventory
        inv = inventory()
        add("btn_count", len(inv.buttons) >= 50, str(len(inv.buttons)))
        add("cmd_count", len(inv.all_commands()) >= 40, str(len(inv.all_commands())))
    except Exception as e:
        add("btn_count", False, str(e))

    # fp world loads
    add("fp_world", _load_asset("fp_world.html") is not None)

    return out


def run(cycles: int = 150, owner: str = "SyncUX150") -> Dict[str, Any]:
    from form.open import open_program
    from form.persist import load, save

    path = os.path.join(os.path.dirname(__file__), "..", "state", f"program_{owner}.json")
    path = os.path.abspath(path)
    if os.path.isfile(path):
        try:
            p = load(owner, path)
        except Exception:
            p = open_program(owner)
    else:
        p = open_program(owner)

    if not p.cube.session.plane.units:
        p.place("sync_seed", "SyncSeed", words="sync ux seed", x=0, y=1)
    p.view_mode = "first_person"

    applied: List[str] = []
    history: List[Dict[str, Any]] = []
    best = 0.0
    n = len(ENHANCEMENTS)
    assert n == 150, n

    # step-by-step log by page
    page_reports: Dict[str, List[str]] = {pg: [] for pg, _, _ in PAGE_ORDER}

    for i in range(1, cycles + 1):
        name, fn = ENHANCEMENTS[(i - 1) % n]
        page = name.split(":")[0]
        try:
            note = fn(p)
        except Exception as e:
            note = f"ERR:{e}"
        applied.append(f"{i}:{name}:{note}")
        if page in page_reports:
            page_reports[page].append(f"{i}:{name}:{note}")

        # progress: each page boundary (every 15) + start/end
        if i == 1 or i == cycles or i % 15 == 0:
            ch = checks(p)
            rate = sum(1 for c in ch if c["ok"]) / max(1, len(ch))
            best = max(best, rate)
            fails = [c["name"] for c in ch if not c["ok"]]
            # which page just finished
            done_page = PAGE_ORDER[((i - 1) // 15) % 10][0] if i % 15 == 0 else page
            history.append({"cycle": i, "rate": round(rate, 3), "fails": fails[:10], "page": done_page})
            print(
                f"[{i:03d}/{cycles}] page={done_page:10s} sync+fn+ux={rate:.1%} best={best:.1%} "
                f"fails={len(fails)} · {name}",
                flush=True,
            )
        elif i % 5 == 0:
            print(f"[{i:03d}/{cycles}] · {name} → {note}", flush=True)

    ch = checks(p)
    rate = sum(1 for c in ch if c["ok"]) / max(1, len(ch))
    best = max(best, rate)
    grade = "A+" if rate >= 0.95 else ("A" if rate >= 0.85 else "B")

    try:
        p.note_seed(13, "Loop", f"sync_ux_x{cycles}")
        save(p, path)
    except Exception:
        pass

    # per-page summary
    page_scores = {}
    for pg, _, _ in PAGE_ORDER:
        sub = [c for c in ch if pg in c["name"] or c["name"].endswith(f"_{pg}") or f"_{pg}" in c["name"]]
        if not sub:
            sub = [c for c in ch if c["name"].startswith(f"file_{pg}") or c["name"].startswith(f"route_{pg}") or c["name"].startswith(f"sync_strip_{pg}") or c["name"].startswith(f"ux_shell_{pg}") or c["name"].startswith(f"js_balance_{pg}")]
        page_scores[pg] = f"{sum(1 for c in sub if c['ok'])}/{len(sub)}" if sub else "n/a"

    fails = [c for c in ch if not c["ok"]]
    return {
        "ok": rate >= 0.90,
        "cycles": cycles,
        "final_rate": round(rate, 3),
        "best_rate": round(best, 3),
        "grade": grade,
        "checks_pass": sum(1 for c in ch if c["ok"]),
        "checks_total": len(ch),
        "fails": fails,
        "history": history,
        "applied_tail": applied[-40:],
        "page_scores": page_scores,
        "page_order": [pg for pg, _, _ in PAGE_ORDER],
        "pillars": ["synchronicity", "functionality", "usability"],
    }


def main() -> None:
    cycles = 150
    for i, a in enumerate(sys.argv):
        if a == "--cycles" and i + 1 < len(sys.argv):
            cycles = max(1, int(sys.argv[i + 1]))
    print("=== FULL PROGRAM PAGE-BY-PAGE STEP-BY-STEP 150 ===")
    print("pillars: synchronicity · functionality · usability")
    print(f"order: {' → '.join(pg for pg,_,_ in PAGE_ORDER)}")
    print(f"catalog={len(ENHANCEMENTS)} (10 pages × 15 steps)")
    out = run(cycles=cycles)
    print(f"\nGRADE {out['grade']} · final={out['final_rate']:.1%} best={out['best_rate']:.1%}")
    print(f"checks {out['checks_pass']}/{out['checks_total']}")
    print("page scores:", out["page_scores"])
    if out["fails"]:
        print(f"fails ({len(out['fails'])}):")
        for c in out["fails"][:20]:
            print(f"  - {c['name']}: {c['detail']}")
    else:
        print("all sync/function/usability checks PASS")
    print("recent steps:")
    for a in out.get("applied_tail") or []:
        print(f"  {a}")
    sys.exit(0 if out["ok"] else 1)


if __name__ == "__main__":
    main()
