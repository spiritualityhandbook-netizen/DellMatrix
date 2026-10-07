#!/usr/bin/env python3
"""R6.1 fresh-process proof scripts (fixed; case data via JSON arguments).

Invoked as:
    python -m form.mandell.r61_child <command> '<json-args>'

Commands:
    issue         {owner, label, subject, max_depth?} -> {grant_id, pid}
    confirm       {owner, pid, grant_id, subject} -> {ok, reason, detail}
    reload_check  {owner, pid} -> {on_plane, status, label_ok}

Each invocation runs in its own OS process with a fresh
AcceptancePolicy (fresh session). Grants are session-scoped: a handle
issued in one process MUST NOT authorize in another.

Evidence class: CROSS_PROCESS (separate OS process per case).
"""

import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(REPO))


def cmd_issue(args):
    from form.open import open_program
    from form.dell_matrix import agent_authority as aa
    p = open_program(args["owner"])
    pr = p.nursery.add(args["label"], words=args.get("words", "w"))
    g = aa.issue_root_grant(
        p, issuer="human:ace", subject=args["subject"],
        max_depth=int(args.get("max_depth", 1)))
    print(json.dumps({"grant_id": g["grant_id"], "pid": pr.id}))


def cmd_confirm(args):
    from form.open import open_program
    from form.dell_matrix import agent_authority as aa
    p = open_program(args["owner"])
    r = aa.agent_confirm(p, args["pid"], args["grant_id"], args["subject"])
    print(json.dumps({"ok": bool(r.get("ok")),
                      "reason": r.get("reason"),
                      "detail": r.get("detail"),
                      "stage": r.get("stage")}))


def cmd_reload_check(args):
    from form import persist_rest
    p = persist_rest.load(args["owner"], activate=False)
    prop = p.nursery.proposals.get(args["pid"])
    on_plane = args["pid"] in p.cube.session.plane.units
    unit = p.cube.session.plane.units.get(args["pid"])
    print(json.dumps({
        "on_plane": bool(on_plane),
        "status": prop.status if prop else None,
        "label_ok": bool(unit) and unit.label == args.get("label", ""),
    }))


_COMMANDS = {
    "issue": cmd_issue,
    "confirm": cmd_confirm,
    "reload_check": cmd_reload_check,
}


def main(argv):
    if len(argv) != 3 or argv[1] not in _COMMANDS:
        print(json.dumps({"error": "usage: r61_child <issue|confirm|reload_check> '<json>'"}))
        return 2
    try:
        args = json.loads(argv[2])
    except Exception as e:
        print(json.dumps({"error": f"bad json: {e}"}))
        return 2
    try:
        _COMMANDS[argv[1]](args)
    except Exception as e:
        print(json.dumps({"error": f"{type(e).__name__}: {e}"}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
