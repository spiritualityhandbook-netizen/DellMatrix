#!/usr/bin/env python3
"""REPL — Form front door. English → Mandell path active."""

from __future__ import annotations

import shlex
import sys

try:
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.blank_cube import BlankCube
    from form.persist import list_checkpoints
    from form.mandell.translate import translate
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.blank_cube import BlankCube
    from form.persist import list_checkpoints
    from form.mandell.translate import translate

HELP = """
DellMatrix FORM — type normal English or commands

  say <english>          ← natural language (recommended)
  place <id> <label> ...
  grow ideas [N]
  enhance on|off
  sandbox on|off
  pulse | show | visual | save | status
  help | quit

Examples:
  say create an idea called business plan
  say grow ideas 3
  say show me the matrix
  say enhance on and pulse
  visual
""".strip()


def _skin(name: str) -> Skin:
    try:
        return Skin(name.lower())
    except Exception:
        return Skin.CUBE


def _execute_intent(p: Program, intent) -> None:
    """Run a translated Intent against the live Program."""
    action = intent.action
    args = intent.args or {}

    print(f"  → {intent.mandel}")

    if action == "place":
        uid = args.get("id", "idea")
        label = args.get("label", uid)
        words = args.get("words", "")
        p.place(uid, label, words=words, skin=Skin.CUBE)
        u = p.cube.session.plane.units.get(uid)
        state = "sandboxed" if u and u.sandboxed else "connected"
        print(f"  placed {uid} ({state})")

    elif action == "grow":
        n = int(args.get("cycles", 1))
        out = p.grow_ideas(n)
        print({"cycles": len(out), "last": out[-1] if out else None})
        print(p.render())

    elif action == "show":
        print(p.render())

    elif action == "visual":
        paths = p.visual()
        print("Visual workspace written:")
        print("  HTML:", paths.get("html"))
        print("  SVG :", paths.get("svg"))
        print("Open the HTML file in any browser (works offline).")

    elif action == "enhance_on":
        p.enhance_on()
        print("enhance ON")

    elif action == "enhance_off":
        p.enhance_off()
        print("enhance OFF")

    elif action == "pulse":
        print(p.pulse())

    elif action == "sandbox_on":
        print(p.sandbox_on())

    elif action == "sandbox_off":
        print(p.sandbox_off())

    elif action == "save":
        print("saved", p.save())

    elif action == "status":
        print(p.status())

    elif action == "help":
        print(HELP)

    elif action == "raw_mandel":
        print("  raw seeds recognized:", intent.args.get("seeds"))
        print("  (no automatic execution for raw seeds yet — use place/grow/etc)")

    else:
        print("  intent not mapped to runtime action yet:", action)


def run(owner: str = "Operator", do_load: bool = False) -> None:
    print("DellMatrix FORM — English → Mandell active")
    print(f"owner={owner}")
    print("Type normal English after 'say', or use commands. Type help.\n")
    p = Program.load(owner) if do_load else open_program(owner)
    print(p.render())

    while True:
        try:
            line = input("matrix> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue

        # Natural language path
        if line.lower().startswith("say "):
            english = line[4:].strip()
            intent = translate(english)
            _execute_intent(p, intent)
            continue

        # Also accept free English if it doesn't start with a known command
        try:
            parts = shlex.split(line)
        except ValueError as e:
            print("parse error:", e)
            continue

        if not parts:
            continue
        cmd = parts[0].lower()

        known = {
            "quit", "exit", "q", "help", "?", "tutorial", "realize", "show", "status",
            "scores", "main", "shared", "sandbox", "network", "net_push", "net_pull",
            "ambient", "intake", "verify", "health", "place", "words", "skin", "move",
            "remove", "box", "unbox", "neighbors", "perspective", "zoom", "enhance",
            "pulse", "decay", "clear", "pull", "push_main", "pull_main", "snapshot_main",
            "visual", "checkpoint", "checkpoints", "pack", "save", "load", "grow", "say",
        }

        if cmd not in known:
            # treat entire line as English
            intent = translate(line)
            _execute_intent(p, intent)
            continue

        if cmd in ("quit", "exit", "q"):
            break
        elif cmd in ("help", "?"):
            print(HELP)
        elif cmd == "tutorial":
            print("say create an idea called test")
            print("say grow ideas 3")
            print("say show me the matrix")
            print("visual")
        elif cmd == "realize":
            from form.realize import realize
            rep = realize(owner)
            p = Program.load(owner)
            print(rep["render"])
        elif cmd == "show":
            print(p.render())
        elif cmd == "status":
            print(p.status())
        elif cmd == "scores":
            print(p.scores())
        elif cmd == "main":
            print(p.main.summary())
        elif cmd == "shared":
            print(p.shared_main_summary())
        elif cmd == "sandbox":
            if len(parts) < 2:
                print(p.sandbox.status())
            elif parts[1] == "on":
                print(p.sandbox_on())
            elif parts[1] == "off":
                print(p.sandbox_off())
            else:
                print("sandbox on|off")
        elif cmd == "network" and len(parts) >= 2:
            p.set_network(parts[1])
            print("network", p.network_url)
        elif cmd == "net_push":
            print(p.net_push())
        elif cmd == "net_pull":
            print(p.net_pull())
        elif cmd == "ambient":
            if len(parts) == 1:
                print(p.ambient.status())
            elif parts[1] == "on":
                p.ambient.turn_on()
                print("ambient ON")
            elif parts[1] == "off":
                p.ambient.turn_off()
                print("ambient OFF")
            elif len(parts) >= 3 and parts[2] == "on":
                print("ok" if p.ambient.enable_source(parts[1]) else "bad")
            elif len(parts) >= 3 and parts[2] == "off":
                print("ok" if p.ambient.disable_source(parts[1]) else "bad")
        elif cmd == "intake":
            print(p.ambient_intake(apply=True))
        elif cmd == "verify":
            print(p.matrix.verify())
        elif cmd == "health":
            print({"sandbox": p.sandbox.on, "enhance": p.enhance.on, "net": p.network_url or None})
        elif cmd == "place" and len(parts) >= 3:
            p.place(parts[1], parts[2], words=" ".join(parts[3:]), skin=Skin.CUBE)
            u = p.cube.session.plane.units[parts[1]]
            print("placed", parts[1], "sandboxed" if u.sandboxed else "connected")
        elif cmd == "words" and len(parts) >= 3:
            u = p.cube.session.plane.units.get(parts[1])
            if u:
                u.words = " ".join(parts[2:])
                print("ok")
            else:
                print("missing")
        elif cmd == "skin" and len(parts) >= 3:
            print("ok" if p.cube.session.plane.set_skin(parts[1], _skin(parts[2])) else "missing")
        elif cmd == "move" and len(parts) >= 4:
            print("ok" if p.cube.session.plane.move(parts[1], float(parts[2]), float(parts[3])) else "missing")
        elif cmd == "remove" and len(parts) >= 2:
            print("ok" if p.cube.session.plane.remove(parts[1]) else "missing")
        elif cmd == "box" and len(parts) >= 2:
            p.box(parts[1:])
            print("boxed", parts[1:])
        elif cmd == "unbox" and len(parts) >= 2:
            print("ok" if p.cube.session.plane.unbox(parts[1]) else "missing")
        elif cmd == "neighbors" and len(parts) >= 2:
            print(p.cube.session.plane.neighbors(parts[1]))
        elif cmd == "perspective" and len(parts) >= 2:
            print("ok" if p.set_perspective(parts[1]) else "bad")
        elif cmd == "zoom" and len(parts) >= 2:
            if parts[1] == "out":
                p.cube.session.plane.zoom_out()
            else:
                p.cube.session.plane.zoom_in(parts[1])
            print("ok")
        elif cmd == "enhance" and len(parts) >= 2:
            if parts[1] == "on":
                p.enhance_on()
                print("enhance ON")
            else:
                p.enhance_off()
                print("enhance OFF")
        elif cmd == "pulse":
            print(p.pulse())
        elif cmd == "decay":
            print(p.enhance.decay(float(parts[1]) if len(parts) > 1 else 0.9))
        elif cmd == "clear":
            print(p.enhance.clear())
        elif cmd == "pull" and len(parts) >= 3:
            print(p.pull(parts[1], parts[2]))
        elif cmd == "push_main":
            print(p.push_main())
        elif cmd == "pull_main":
            print(p.pull_main())
        elif cmd == "snapshot_main":
            print(p.snapshot_main())
        elif cmd == "visual":
            paths = p.visual()
            print("Visual workspace written:")
            print("  HTML:", paths.get("html"))
            print("  SVG :", paths.get("svg"))
            print("Open the HTML file in any browser (works offline).")
        elif cmd == "checkpoint":
            print(p.checkpoint())
        elif cmd == "checkpoints":
            print(list_checkpoints(owner))
        elif cmd == "pack":
            pack_cube = BlankCube(owner=p.owner, clean=True)
            pack_cube.session = p.cube.session
            print("pack", pack_cube.write_pack())
        elif cmd == "save":
            print("saved", p.save())
        elif cmd == "load":
            p = Program.load(owner)
            print(p.render())
        elif cmd == "grow":
            if len(parts) >= 2 and parts[1] == "ideas":
                n = int(parts[2]) if len(parts) > 2 else 1
                out = p.grow_ideas(n)
                print({"cycles": len(out), "last": out[-1] if out else None})
                print(p.render())
            else:
                p.grow(1)
                print("gen", p.duo.generation)
        else:
            print("unknown — type help or use: say <english>")

    print("session end")


def main() -> None:
    owner = "Operator"
    do_load = "--load" in sys.argv
    for i, a in enumerate(sys.argv):
        if a == "--owner" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
    run(owner, do_load)


if __name__ == "__main__":
    main()
