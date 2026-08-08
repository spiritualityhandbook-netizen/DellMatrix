#!/usr/bin/env python3
"""
Plant Worldwide ideas into Worldwide profile, then import them into DEV (Operator).

DEV = DellMatrix development source of truth.
Worldwide ideas develop on DEV without becoming Ace personal lore.

Usage:
  python -m form.worldwide.plant_to_dev
  python -m form.worldwide.plant_to_dev --dev-only
  python -m form.worldwide.plant_to_dev --worldwide-only
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from form.open import open_program
from form.dell_matrix.plane import Skin
from form.persist import save, load
from form.idea_create import strength_score, grade_for
from form.worldwide.WORLDWIDE_IDEAS import WORLDWIDE_IDEAS

_SKIN = {
    "cube": Skin.CUBE,
    "sphere": Skin.SPHERE,
    "seed": Skin.SEED,
    "flower": Skin.FLOWER,
    "building": Skin.BUILDING,
    "words": Skin.WORDS,
    "circle": Skin.CIRCLE,
    "core": Skin.CORE,
}

DEV_OWNER = "Operator"  # DellMatrix DEV profile
WORLD_OWNER = "Worldwide"


def _place_catalog(program, ideas: List[Dict[str, Any]], *, prefix: str = "") -> List[Dict[str, Any]]:
    planted = []
    for s in ideas:
        uid = s["id"]
        if prefix and not uid.startswith(prefix):
            # keep stable ids; tag via words
            pass
        skin = _SKIN.get(str(s.get("skin") or "cube"), Skin.CUBE)
        detail = s.get("detail") or ""
        goals = list(s.get("goals") or [])
        words = s.get("words") or detail[:200]
        tags = list(s.get("tags") or [])
        if "worldwide" not in tags:
            tags.append("worldwide")
        if "dev" not in tags and program.owner == DEV_OWNER:
            tags.append("dev")
        # merge tags into words for searchability
        tag_s = " ".join(tags)
        word_blob = f"{words} [{tag_s}]".strip()
        sc = strength_score(detail, goals)
        # upsert: place overwrites unit id on plane
        program.place(
            uid,
            s["label"],
            words=word_blob[:500],
            detail=detail,
            goals=goals,
            skin=skin,
        )
        planted.append({
            "id": uid,
            "label": s["label"],
            "strength": sc,
            "grade": grade_for(sc),
            "owner": program.owner,
        })
        try:
            program.keys.remember(
                s["label"],
                meta={"id": uid, "origin": "worldwide", "owner": program.owner},
                payload=detail[:200],
            )
        except Exception:
            pass
    return planted


def plant_worldwide(persist: bool = True) -> Dict[str, Any]:
    p = open_program(WORLD_OWNER)
    planted = _place_catalog(p, WORLDWIDE_IDEAS)
    path = save(p) if persist else ""
    p.note_seed(8, "Create", f"worldwide_x{len(planted)}")
    return {"ok": True, "owner": WORLD_OWNER, "planted": planted, "path": path, "ideas": len(p.cube.session.plane.units)}


def plant_dev_from_worldwide(persist: bool = True, load_existing_dev: bool = True) -> Dict[str, Any]:
    """
    Import all worldwide catalog ideas into DEV Operator matrix for development.
    Optionally merge into existing Operator session if present.
    """
    state_path = os.path.join(
        os.path.dirname(__file__), "..", "state", f"program_{DEV_OWNER}.json"
    )
    state_path = os.path.abspath(state_path)
    if load_existing_dev and os.path.isfile(state_path):
        p = load(DEV_OWNER, state_path)
    else:
        p = open_program(DEV_OWNER)

    planted = _place_catalog(p, WORLDWIDE_IDEAS)
    # mark session intent
    p.note_seed(8, "Create", f"ww_to_dev_x{len(planted)}")
    p.duo.evolve(f"08[Create] > 15[Map] :: worldwide→DEV x{len(planted)}")
    # light evolve so pillars reflect new work
    try:
        p.evolve("worldwide ideas into DEV")
    except Exception:
        pass
    path = save(p) if persist else ""
    return {
        "ok": True,
        "owner": DEV_OWNER,
        "planted": planted,
        "path": path,
        "ideas": len(p.cube.session.plane.units),
        "pillars": p.audit() if hasattr(p, "audit") else {},
    }


def run(dev: bool = True, worldwide: bool = True) -> Dict[str, Any]:
    out: Dict[str, Any] = {"ok": True}
    if worldwide:
        out["worldwide"] = plant_worldwide(persist=True)
    if dev:
        out["dev"] = plant_dev_from_worldwide(persist=True)
    return out


def main() -> None:
    dev = True
    worldwide = True
    if "--dev-only" in sys.argv:
        worldwide = False
    if "--worldwide-only" in sys.argv:
        dev = False
    out = run(dev=dev, worldwide=worldwide)
    if out.get("worldwide"):
        w = out["worldwide"]
        print(f"WORLDWIDE · ideas={w['ideas']} path={w['path']}")
        for row in w["planted"]:
            print(f"  [{row['grade']:8}] {row['strength']:.2f}  {row['label']}")
    if out.get("dev"):
        d = out["dev"]
        print(f"\nDEV (Operator) · ideas={d['ideas']} path={d['path']}")
        for row in d["planted"]:
            print(f"  [{row['grade']:8}] {row['strength']:.2f}  {row['label']}")
        pil = d.get("pillars") or {}
        print(f"pillars={pil.get('label')} avg={pil.get('average')}")
    print("\nWorldwide ideas are now in DellMatrix DEV for development.")
    print("Launch DEV:  python launch.py")
    print("             python launch.py Operator")


if __name__ == "__main__":
    main()
