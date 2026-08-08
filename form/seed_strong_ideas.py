#!/usr/bin/env python3
"""
Plant strong foundation ideas (detail + goals) into a profile session.

Default owner: Worldwide (not Ace personal lore).
Does not touch Main auto-evolve.

Full worldwide catalog → DEV:
  python -m form.worldwide.plant_to_dev
"""

from __future__ import annotations

from typing import Any, Dict, List
import sys

try:
    from form.open import open_program
    from form.dell_matrix.plane import Skin
    from form.persist import save
    from form.idea_create import strength_score, grade_for
except ImportError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.open import open_program
    from form.dell_matrix.plane import Skin
    from form.persist import save
    from form.idea_create import strength_score, grade_for


SEEDS: List[Dict[str, Any]] = [
    {
        "id": "code_evolution",
        "label": "Code Evolution",
        "detail": (
            "Post-Boolean decision shells and post-static variable models; "
            "ultra-intuitive coding surface bound into Mandell. "
            "Boolean remains silicon substrate. Unknown claims stay PROJECTED_NOT_FACT."
        ),
        "goals": [
            "Exhaust Δ_known shells into runnable Mandell operators",
            "Map variables beyond static containers",
            "Minimal intuitive surface on current machines",
            "Honesty labels on projections",
            "Never break DEV Floor or Nursery law",
        ],
        "skin": Skin.CUBE,
    },
    {
        "id": "true_lore",
        "label": "True Lore Identifier",
        "detail": (
            "Deeper meanings of names, words, phrases, books, ideas, and real-life lore "
            "using LatinMandell morphology plus honest research. Pattern literacy, not fake decode."
        ),
        "goals": [
            "Clear deeper readings people can trust",
            "Teach morphology literacy",
            "Support lore clarity with evidence boundaries",
            "Possible loved name/history tools later",
        ],
        "skin": Skin.SEED,
    },
    {
        "id": "idea_law",
        "label": "Strong Idea Law",
        "detail": (
            "Every live idea carries detail and goals so growth is aimed, not random. "
            "Weak label-only ideas are incomplete."
        ),
        "goals": [
            "detail + goals on every important idea",
            "Growth biases toward stated goals",
            "Blank matrices inherit the same law",
        ],
        "skin": Skin.WORDS,
    },
    {
        "id": "decision_shells",
        "label": "Decision Shells",
        "detail": (
            "Runnable ternary and fuzzy decision surfaces for Mandell growth gates. "
            "Complements Boolean substrate; does not replace host bool."
        ),
        "goals": [
            "Soft gates for affinity and confirm ranking",
            "Keep silicon Boolean intact",
            "Feed Code Evolution Δ_known",
        ],
        "skin": Skin.CIRCLE,
    },
]


def plant(owner: str = "Worldwide", persist: bool = True) -> Dict[str, Any]:
    p = open_program(owner)
    planted = []
    for s in SEEDS:
        sc = strength_score(s["detail"], s["goals"])
        p.place(
            s["id"],
            s["label"],
            words=s["detail"][:200],
            detail=s["detail"],
            goals=list(s["goals"]),
            skin=s.get("skin", Skin.CUBE),
        )
        planted.append({
            "id": s["id"],
            "label": s["label"],
            "strength": sc,
            "grade": grade_for(sc),
        })
    path = save(p) if persist else ""
    return {"ok": True, "owner": owner, "planted": planted, "path": path}


def smoke() -> bool:
    print("=== SEED STRONG IDEAS SMOKE ===")
    out = plant("SeedSmoke", persist=False)
    ok = out.get("ok") and len(out.get("planted", [])) >= 4
    print(f"[{'PASS' if ok else 'FAIL'}] planted {len(out.get('planted', []))}")
    for row in out.get("planted", []):
        print(f"  {row['grade']:8} {row['strength']:.2f}  {row['label']}")
    return bool(ok)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    owner = "Worldwide"
    for i, a in enumerate(sys.argv):
        if a == "--owner" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
    out = plant(owner, persist=True)
    print(f"owner={out['owner']} path={out['path']}")
    for row in out["planted"]:
        print(f"  [{row['grade']}] {row['label']} strength={row['strength']}")


if __name__ == "__main__":
    main()
