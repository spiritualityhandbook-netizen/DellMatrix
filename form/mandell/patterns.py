#!/usr/bin/env python3
"""Mandell pattern layer — math & nature as teachable forms."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Pattern:
    name: str
    nature: str
    math: str
    mandel: str
    english: str
    teach: str


PATTERNS: Dict[str, Pattern] = {
    "loop": Pattern(
        name="loop", nature="season cycle",
        math="iteration n → n+1", mandel="13[Loop]",
        english="do again until done",
        teach="Loop is lawful repetition.",
    ),
    "grow": Pattern(
        name="grow", nature="seed → branch",
        math="affinity proposals; keep originals",
        mandel="13[Loop] > 04[Transform] :: grow",
        english="grow ideas into nursery",
        teach="Grow proposes; confirm makes live.",
    ),
    "merge": Pattern(
        name="merge", nature="two rivers",
        math="A ⊗ B vesica", mandel="21[Merge] > 14[Bind]",
        english="combine with shared middle",
        teach="Merge is two → one without erase.",
    ),
    "split": Pattern(
        name="split", nature="cell division", math="one → parts",
        mandel="22[Split]", english="divide into parts",
        teach="Inverse posture of Merge.",
    ),
    "pulse": Pattern(
        name="pulse", nature="heartbeat", math="broadcast to peers",
        mandel="25[Pulse]", english="wave through links",
        teach="Sandbox walls block pulse.",
    ),
    "decay": Pattern(
        name="decay", nature="autumn leaves", math="score × factor",
        mandel="16[Decay]", english="gentle fade",
        teach="Forgetting without deleting structure.",
    ),
    "ring": Pattern(
        name="ring", nature="tree rings",
        math="Seed→Token→Body→Lens→Evolve",
        mandel="15[Map] > 13[Loop] > 04[Transform]",
        english="ordered growth stages",
        teach="Skip none; quarantine before live.",
    ),
    "bridge": Pattern(
        name="bridge", nature="stepping stones",
        math="surface A → Dell layer → surface B",
        mandel="45[Translate]", english="translate forms",
        teach="Meaning stays; surface changes.",
    ),
    "keep": Pattern(
        name="keep", nature="seed vault", math="serialize/restore",
        mandel="10[Keep]", english="save session",
        teach="Keep is memory. Load is return.",
    ),
    "lock": Pattern(
        name="lock", nature="sealed jar", math="freeze region",
        mandel="23[Lock]", english="sandbox",
        teach="Lock isolates. Unlock reconnects.",
    ),
    "lattice": Pattern(
        name="lattice", nature="crystal / Tonnetz",
        math="H=fifths V=thirds F=frequency",
        mandel="15[Map] > 14[Bind] :: lattice",
        english="H/V/F structural plane",
        teach="One lattice. Overlays and perceptions change reading only.",
    ),
    "chord": Pattern(
        name="chord", nature="notes as one color",
        math="interval neighborhood query",
        mandel="07[Link] > 21[Merge] :: chord",
        english="pull related cells",
        teach="Multi-topic without copying.",
    ),
    "imagination": Pattern(
        name="imagination", nature="seed→engine→latch→form",
        math="ima + gin + at + ion",
        mandel="08[Create] > 15[Map] > 50[Manifest] :: imagination",
        english="manifest an idea on the lattice",
        teach="ima-gin-at-ion is process: seed, generate, place, charge.",
    ),
    "flower": Pattern(
        name="flower", nature="Flower of Life",
        math="equal circles on triangular packing; centers share lattice",
        mandel="15[Map] > 08[Create] :: flower",
        english="plant flower centers on the lattice",
        teach="Flower is perception + packing. Same points can still read as grid.",
    ),
    "core": Pattern(
        name="core", nature="onion / radial shells",
        math="spherical distance shells from origin",
        mandel="15[Map] :: core",
        english="cube mode → core mode (radial)",
        teach="Core does not move cells; it changes distance to shells.",
    ),
    "sphere": Pattern(
        name="sphere", nature="bubble / globe",
        math="L2 radial metric on same coordinates as cube",
        mandel="04[Transform] :: sphere",
        english="perceive cubes as spheres",
        teach="Cube↔sphere dual: max-norm shells vs radial shells.",
    ),
    "circle": Pattern(
        name="circle", nature="ripple",
        math="L2 on HV plane; dual of square",
        mandel="04[Transform] :: circle",
        english="perceive squares as circles",
        teach="Square↔circle dual on the same centers.",
    ),
}


def get_pattern(name: str) -> Optional[Pattern]:
    return PATTERNS.get((name or "").lower().strip())


def list_patterns() -> List[Dict[str, str]]:
    return [
        {
            "name": p.name, "nature": p.nature, "math": p.math,
            "mandel": p.mandel, "english": p.english, "teach": p.teach,
        }
        for p in PATTERNS.values()
    ]


def teach(name: str) -> str:
    p = get_pattern(name)
    if not p:
        return f"Unknown pattern: {name}. Try: {', '.join(PATTERNS)}"
    return (
        f"{p.name}\n"
        f"  nature: {p.nature}\n"
        f"  math:   {p.math}\n"
        f"  mandel: {p.mandel}\n"
        f"  meaning:{p.english}\n"
        f"  lesson: {p.teach}"
    )
