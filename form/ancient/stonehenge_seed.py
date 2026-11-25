#!/usr/bin/env python3
"""
Stonehenge → Dell Matrix structural seed

35[Discover] > 15[Map] >> 14[Bind] :: StonehengeSeed
Lenses: The_Ancient · Manelody (harmony / cycle tone)

NOT a decipherment of builder intent.
Maps public monument structure into plane ideas, Main tags, and grow fuel.

Run:
  python -m form.ancient.stonehenge_seed --owner Ace
  python -m form.ancient.stonehenge_seed --owner Sister --grow 5
"""

from __future__ import annotations

from typing import Any, Dict, List
import json
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.open import open_program
    from form.dell_matrix.plane import Skin
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.open import open_program
    from form.dell_matrix.plane import Skin

# Structural units — measurements/ideas as matrix food, not proven theology
STONES: List[Dict[str, Any]] = [
    {
        "id": "sh_floor",
        "label": "SalisburyFloor",
        "words": "landscape floor before stones — ditch bank open plain axis",
        "skin": Skin.CIRCLE,
        "x": 0.0,
        "y": 0.0,
        "dell": 0,
        "tag": "floor",
    },
    {
        "id": "sh_aubrey",
        "label": "Aubrey56",
        "words": "56 pits cycle counter candidate lunar 18.6 family 18.6*3~56 PROJECTED pattern",
        "skin": Skin.CIRCLE,
        "x": -1.2,
        "y": 0.8,
        "dell": 6,
        "tag": "cycle",
    },
    {
        "id": "sh_axis",
        "label": "SolsticeAxis",
        "words": "heel stone corridor midsummer sunrise midwinter sunset bind strong evidence",
        "skin": Skin.SEED,
        "x": 1.5,
        "y": 0.0,
        "dell": 14,
        "tag": "bind",
    },
    {
        "id": "sh_sarsen",
        "label": "SarsenRing",
        "words": "great circle trilithons lock frame local sarsen stone",
        "skin": Skin.CUBE,
        "x": 0.0,
        "y": 1.2,
        "dell": 23,
        "tag": "lock",
    },
    {
        "id": "sh_blue",
        "label": "BluestoneMerge",
        "words": "Preseli Wales long distance transport merge people stone path",
        "skin": Skin.FLOWER,
        "x": -1.5,
        "y": -0.5,
        "dell": 21,
        "tag": "merge",
    },
    {
        "id": "sh_altar",
        "label": "AltarStone",
        "words": "central slab geochemical far north Scotland line source research not full meaning",
        "skin": Skin.BUILDING,
        "x": 0.3,
        "y": -0.2,
        "dell": 15,
        "tag": "map",
    },
    {
        "id": "sh_phase",
        "label": "BuildPhases",
        "words": "centuries of rebuild earthen first then stone phases decay or change of goal",
        "skin": Skin.WORDS,
        "x": 1.0,
        "y": -1.0,
        "dell": 4,
        "tag": "transform",
    },
    {
        "id": "sh_gather",
        "label": "GatherRite",
        "words": "assembly burial seasonal gathering social power multiple functions likely",
        "skin": Skin.SPHERE,
        "x": -0.5,
        "y": -1.2,
        "dell": 25,
        "tag": "pulse",
    },
]

MAIN_TAGS = {
    "solstice": 1.0,
    "lunar_cycle": 0.8,
    "merge_distance": 0.9,
    "phase_rebuild": 0.7,
    "axis_bind": 1.0,
    "floor_landscape": 0.85,
    "resonance_model": 0.5,  # acoustic ideas = model fuel only
    "no_full_decode": 1.0,
}

ANCIENT_NOTE = (
    "The_Ancient: read duration and sequence before spectacle. "
    "Stonehenge is layered time, not one night of magic."
)
MANELODY_NOTE = (
    "Manelody: hear cycle and axis as harmony skeleton — "
    "56 as rhythm candidate, solstice as downbeat, merge as interval."
)


def seed(owner: str = "Operator", grow: int = 0) -> Dict[str, Any]:
    assert_floor_intact()
    p = open_program(owner)

    placed = []
    for s in STONES:
        p.place(
            s["id"],
            s["label"],
            words=s["words"],
            skin=s["skin"],
            x=s["x"],
            y=s["y"],
        )
        placed.append(s["id"])

    for tag, w in MAIN_TAGS.items():
        p.main.tags[tag] = p.main.tags.get(tag, 0.0) + float(w)

    # lens notes as words units
    p.place(
        "lens_ancient",
        "The_Ancient",
        words=ANCIENT_NOTE,
        skin=Skin.WORDS,
        x=-2.0,
        y=1.5,
    )
    p.place(
        "lens_manelody",
        "Manelody",
        words=MANELODY_NOTE,
        skin=Skin.WORDS,
        x=2.0,
        y=1.5,
    )

    evo = None
    if grow > 0:
        evo = p.grow_ideas(grow)

    path = p.save()
    vis = p.visual()

    return {
        "owner": owner,
        "floor": list(FLOOR),
        "placed": placed + ["lens_ancient", "lens_manelody"],
        "main_tags": dict(p.main.tags),
        "grow": evo[-1] if evo else None,
        "scores": p.scores() if grow else {},
        "save": path,
        "visual": vis,
        "claim_level": "structural_seed_only",
        "disclaimer": (
            "Not a decipherment of Stonehenge. "
            "Public structure mapped into Dell Matrix for pattern work and evolution fuel."
        ),
        "usable_for_matrix": [
            "cycle counter pattern (56 / lunar family) as Cycle dell practice",
            "axis bind as Bindell / solstice lock metaphor for enhance_scope",
            "long-distance merge (bluestone) as Main merge without clobber model",
            "phased rebuild as DuoBeta generation without species explosion",
            "floor-first: landscape before spectacle — Floor before Dell Matrix",
            "multiple functions — one plane many skins",
            "precision decay question — rank NBD on skill vs intent change",
        ],
    }


def main() -> None:
    owner = "Operator"
    grow = 0
    for i, a in enumerate(sys.argv):
        if a == "--owner" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
        if a == "--grow" and i + 1 < len(sys.argv):
            grow = int(sys.argv[i + 1])
    out = seed(owner, grow=grow)
    print("15[Map] : 18[Mirror] >> 50[Manifest] :: StonehengeSeed")
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
