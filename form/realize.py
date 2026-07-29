#!/usr/bin/env python3
"""
Realize — run the full Form path end-to-end.

50[Manifest] :: Realize

Opens the program, places ideas, pulses resonance, shared Main,
visual export, checkpoint, ambient inbox sample, verify.
"""

from __future__ import annotations

import json
import os
import sys

from form.open import open_program
from form.dell_matrix.plane import Skin
from form.dell_matrix.ambient_gate import _INBOX


def realize(owner: str = "Operator") -> dict:
    print("50[Manifest] :: Realize")
    print(f"English: Realizing Dell Matrix for {owner}\n")

    p = open_program(owner)

    # core ideas
    p.place("biz", "Business", words="Ultimate Stain and Seal — routes CRM", skin=Skin.BUILDING, x=1.0)
    p.place("music", "Music", words="Bombs Away Ep4", skin=Skin.SEED, x=-1.0)
    p.place("cube", "HarmonicCube", words="holdable perspective core", skin=Skin.CUBE, y=1.0)

    # resonance
    p.enhance_on()
    pulse1 = p.pulse()
    pulse2 = p.pulse()

    # sandbox demo
    p.box(["cube"], "sandbox_A")

    # shared main
    push = p.push_main()

    # ambient: seed inbox + intake
    os.makedirs(_INBOX, exist_ok=True)
    sample = os.path.join(_INBOX, "realize_note.txt")
    with open(sample, "w", encoding="utf-8") as f:
        f.write("Note from inbox — ambient files path realized.")
    p.ambient.turn_on()
    p.ambient.enable_source("files")
    amb = p.ambient_intake(apply=True)

    # visual + persist
    vis = p.visual()
    path = p.save()
    cp = p.checkpoint()
    verify = p.matrix.verify()

    report = {
        "owner": owner,
        "units": list(p.cube.session.plane.units.keys()),
        "scores": p.scores(),
        "pulse": {"ok": pulse2.get("ok"), "count": p.enhance.state.pulse_count},
        "shared_push": push,
        "ambient_placed": amb.get("placed", []),
        "visual": vis,
        "save": path,
        "checkpoint": cp,
        "verify": verify,
        "render": p.render(),
    }
    return report


def main() -> None:
    owner = "Operator"
    for i, a in enumerate(sys.argv):
        if a == "--owner" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
    rep = realize(owner)
    print(rep["render"])
    print("\n--- REALIZE REPORT ---")
    print(json.dumps({k: v for k, v in rep.items() if k != "render"}, indent=2, default=str))
    print("\nOpen HTML:", rep["visual"].get("html"))
    print("Done. Floor locked. Form realized.")


if __name__ == "__main__":
    main()
