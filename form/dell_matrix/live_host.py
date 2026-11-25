#!/usr/bin/env python3
"""
Persistent live HTML host for DellMatrix.

Why this exists:
  start_live(..., background=True) runs a daemon thread. When the Python
  process that called it exits, the browser URL dies. This module keeps
  the process alive so http://127.0.0.1:8765/ stays up.

Usage:
  python3 -m form.dell_matrix.live_host
  python3 -m form.dell_matrix.live_host --port 8765 --owner Operator
  python3 -m form.dell_matrix.live_host --load   # load saved session

Offline fallback (no server):
  python3 -c "from form.persist import load; load('Operator').visual()"
  → open DellMatrix_UI.html in a browser
"""

from __future__ import annotations

import argparse
import os
import sys
import time

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="DellMatrix live HTML host")
    ap.add_argument("--owner", default="Operator")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--load", action="store_true", help="Load saved session if present")
    ap.add_argument("--grow", action="store_true", help="Run grow×1 after open")
    args = ap.parse_args(argv)

    from form.open import open_program
    from form.dell_matrix.live_visual import start_live

    p = None
    if args.load:
        try:
            from form.persist import load as persist_load
            p = persist_load(args.owner)
            print(f"Loaded session for {args.owner}")
        except Exception as e:
            print(f"Load failed ({e}) — opening fresh")
    if p is None:
        p = open_program(args.owner)

    if args.grow:
        try:
            out = p.grow_ideas(1)
            print(f"Grew · pending nursery={out.get('nursery', {}).get('pending')}")
        except Exception as e:
            print(f"grow skip: {e}")

    # Also write offline snapshot so something always works offline
    try:
        paths = p.visual()
        print(f"Offline snapshot: {paths.get('easy') or paths.get('html')}")
    except Exception as e:
        print(f"snapshot skip: {e}")

    info = start_live(p, port=args.port, background=True)
    if not info.get("ok"):
        print("LIVE FAILED:", info.get("error"))
        print("Fallback:", info.get("fallback") or info.get("fallback_offline"))
        return 1

    print()
    print("  DellMatrix LIVE (keep this terminal open)")
    print(f"  Open:  {info['url']}")
    print(f"  Pages: walk lattice nursery program personas forces geometry matrices workshops inspire console")
    print(f"  Offline snapshot always available: DellMatrix_UI.html (from project root)")
    print("  Ctrl+C to stop server")
    print()

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\nLive stopped.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
