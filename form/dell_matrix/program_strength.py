#!/usr/bin/env python3
"""
Program strength suite — function + usability gates.

Checks:
  · every depth action returns a useful end (msg/error)
  · workshops / pages / capabilities warm
  · natural English maps to real cmds
  · garbage text does NOT invent ideas
  · incomplete bare cmds return usage
  · HTML surfaces load without glue corruption
  · self-model + acceptance path

  python -m form.dell_matrix.program_strength
  python -m form.dell_matrix.program_strength --smoke
"""

from __future__ import annotations

import os
import re
import sys
from typing import Any, Dict, List, Tuple

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def run_strength() -> Dict[str, Any]:
    from form.open import open_program
    from form.dell_matrix.actions_registry import actions_flat
    from form.dell_matrix.workshops import list_workshops
    from form.dell_matrix.live_visual import _run_command, _PAGE_ROUTES
    from form.dell_matrix.self_model import CAPABILITIES, probe_capability
    from form.mandell.english_brain import normalize_english
    from form.dell_matrix import live_visual as lv

    print("=== PROGRAM STRENGTH (function + usability) ===")
    issues: List[Tuple[str, str, str]] = []
    scores: Dict[str, Any] = {}

    p = open_program("Strength")
    p.set_ux_mode("depth")
    p.place("s1", "StrongSeed", words="usable strong", x=0, y=2)
    p.enhance.turn_on()
    p.grow_ideas(1)
    props = p.list_proposals()
    pid = props[0]["id"] if props else None

    def fill(cmd: str) -> str:
        c = (cmd or "").rstrip()
        if c == "create an idea called ":
            return "create an idea called StrengthIdea"
        if c == "confirm ":
            return f"confirm {pid}" if pid else "confirm all"
        if c == "reject ":
            pend = p.list_proposals()
            return f"reject {pend[-1]['id']}" if len(pend) > 1 else "reject all"
        return c

    # 1) Actions
    ok_a = 0
    seen = set()
    for item in actions_flat("depth"):
        cmd = fill(item["cmd"])
        if cmd in seen or cmd.lower() in ("live", "tutorial"):
            continue
        seen.add(cmd)
        out = _run_command(p, cmd)
        msg = (out.get("msg") or out.get("error") or "").strip()
        if not msg:
            issues.append(("action_empty", cmd, item["group"]))
        elif "created idea" in msg.lower() and not cmd.lower().startswith("create"):
            issues.append(("action_miscreate", cmd, msg[:60]))
        else:
            ok_a += 1
    scores["actions_ok"] = ok_a
    scores["actions_checked"] = len(seen)
    print(f"[actions] {ok_a}/{len(seen)}")

    # 2) Garbage guard
    p2 = open_program("GarbageGuard")
    before = set(p2.cube.session.plane.units.keys())
    g_ok = 0
    for g in ["asdfghjkl", "blue banana moonlight", "????", "xyzzy"]:
        _run_command(p2, g)
        after = set(p2.cube.session.plane.units.keys())
        if after - before:
            issues.append(("garbage_miscreate", g, str(after - before)))
        else:
            g_ok += 1
        before = after
    # real create still works
    out = _run_command(p2, "create an idea called KeepMe")
    if not out.get("ok") and "created" not in (out.get("msg") or "").lower():
        # create may report via msg only
        if "KeepMe" not in str(p2.cube.session.plane.units) and "keepme" not in str(
            [u.label.lower() for u in p2.cube.session.plane.units.values()]
        ):
            issues.append(("create_broken", "create an idea called KeepMe", out.get("msg") or ""))
    scores["garbage_blocked"] = g_ok
    print(f"[garbage] blocked {g_ok}/4")

    # 3) Incomplete usage
    inc_ok = 0
    for bare in ("confirm", "reject", "create", "zoom", "shell"):
        out = _run_command(p, bare)
        msg = (out.get("error") or out.get("msg") or "").lower()
        if "usage" in msg or out.get("end") == "usage":
            inc_ok += 1
        elif "created" in msg:
            issues.append(("incomplete_miscreate", bare, msg[:60]))
        else:
            issues.append(("incomplete_weak", bare, msg[:60]))
    scores["incomplete_ok"] = inc_ok
    print(f"[incomplete] {inc_ok}/5")

    # 4) English
    en = [
        ("what do i see", "look"),
        ("open the idea page", "page"),
        ("know myself", "self"),
        ("save my work", "save"),
        ("health check", "audit"),
        ("score slopes please", "slopes"),
    ]
    en_ok = 0
    for text, exp in en:
        n, _ = normalize_english(text)
        if exp in (n or "").lower():
            en_ok += 1
        else:
            issues.append(("english_miss", text, n or ""))
    scores["english_ok"] = en_ok
    print(f"[english] {en_ok}/{len(en)}")

    # 5) Capabilities
    cap_ok = 0
    for cap in CAPABILITIES:
        r = probe_capability(p, cap)
        if r.get("ok"):
            cap_ok += 1
        else:
            issues.append(("cap_weak", cap["id"], r.get("msg") or ""))
    scores["caps_ok"] = cap_ok
    scores["caps_total"] = len(CAPABILITIES)
    print(f"[caps] {cap_ok}/{len(CAPABILITIES)}")

    # 6) Pages HTML
    assets = os.path.join(os.path.dirname(lv.__file__), "assets")
    page_ok = 0
    for route, rel in _PAGE_ROUTES.items():
        path = os.path.join(assets, rel)
        if not os.path.isfile(path):
            issues.append(("page_missing", route, rel))
            continue
        body = open(path, encoding="utf-8", errors="ignore").read()
        if re.search(r"</button>\s*[a-zA-Z]", body) or re.search(r"</span>\s*[a-zA-Z=]", body):
            # allow </button></a>
            if re.search(r"</button>\s*data-|</button>\s*id=|</span>\s*id=", body):
                issues.append(("page_corrupt", route, "glue attrs"))
                continue
        if len(body) < 150:
            issues.append(("page_thin", route, str(len(body))))
            continue
        page_ok += 1
    scores["pages_ok"] = page_ok
    scores["pages_total"] = len(_PAGE_ROUTES)
    print(f"[pages] {page_ok}/{len(_PAGE_ROUTES)}")

    # 7) Self + key surfaces
    for cmd in ("self", "inspire", "page", "status", "help"):
        out = _run_command(p, cmd)
        if not (out.get("msg") or out.get("error")):
            issues.append(("surface_empty", cmd, ""))

    # 8) Mode progressive disclosure
    b0 = len(actions_flat("beginner"))
    b1 = len(actions_flat("builder"))
    b2 = len(actions_flat("depth"))
    if not (b0 < b1 <= b2 and b0 >= 20):
        issues.append(("modes", f"{b0}/{b1}/{b2}", "disclosure"))
    scores["modes"] = {"beginner": b0, "builder": b1, "depth": b2}
    print(f"[modes] beginner={b0} builder={b1} depth={b2}")

    passed = len(issues) == 0 and g_ok == 4 and en_ok >= 5 and cap_ok >= len(CAPABILITIES) - 2
    print(f"\n=== STRENGTH: issues={len(issues)} · {'PASS' if passed else 'FAIL'} ===")
    for i in issues[:25]:
        print(f"  {i}")
    return {"ok": passed, "issues": issues, "scores": scores}


def smoke() -> bool:
    out = run_strength()
    return bool(out.get("ok"))


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    out = run_strength()
    sys.exit(0 if out["ok"] else 1)
