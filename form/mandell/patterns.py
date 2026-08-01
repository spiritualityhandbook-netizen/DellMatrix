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
        name="loop",
        nature="season cycle — return and continue",
        math="repeat while condition; iteration n → n+1",
        mandel="13[Loop]",
        english="do again until done",
        teach="Loop is lawful repetition. Growth uses Loop, not random noise.",
    ),
    "grow": Pattern(
        name="grow",
        nature="plant from seed → branch (never erase the seed)",
        math="propose new nodes from affinity; keep originals",
        mandel="13[Loop] > 04[Transform] :: grow",
        english="grow ideas into nursery proposals",
        teach="Grow creates proposals. Confirm brings them into the live matrix.",
    ),
    "merge": Pattern(
        name="merge",
        nature="two rivers → one stream",
        math="A ⊗ B → relation middle (vesica)",
        mandel="21[Merge] > 14[Bind]",
        english="combine two things into one binding",
        teach="Merge is two → one with a shared middle, not a delete.",
    ),
    "split": Pattern(
        name="split",
        nature="cell division",
        math="one → parts",
        mandel="22[Split]",
        english="divide one into parts",
        teach="Split is the inverse posture of Merge.",
    ),
    "pulse": Pattern(
        name="pulse",
        nature="heartbeat / breath out",
        math="broadcast delta to connected peers",
        mandel="25[Pulse]",
        english="send a wave through connected ideas",
        teach="Pulse moves energy along links. Sandbox walls block it.",
    ),
    "decay": Pattern(
        name="decay",
        nature="autumn leaves",
        math="score ← score × factor (0..1)",
        mandel="16[Decay]",
        english="fade scores over time",
        teach="Decay is gentle forgetting, not deletion of structure.",
    ),
    "ring": Pattern(
        name="ring",
        nature="tree rings / stone circle",
        math="ordered stages: Seed→Token→Body→Lens→Evolve",
        mandel="15[Map] > 13[Loop] > 04[Transform]",
        english="move through growth rings in order",
        teach="Rings are stages. Skip none; quarantine before live.",
    ),
    "bridge": Pattern(
        name="bridge",
        nature="stepping stones across water",
        math="map surface A → operator layer → surface B",
        mandel="45[Translate]",
        english="translate between English and Mandell",
        teach="Bridge keeps meaning; it changes surface form only.",
    ),
    "keep": Pattern(
        name="keep",
        nature="seed vault",
        math="serialize state; idempotent restore",
        mandel="10[Keep]",
        english="save the whole session",
        teach="Keep is memory. Load is return.",
    ),
    "lock": Pattern(
        name="lock",
        nature="winter ice / sealed jar",
        math="freeze mutability for a region",
        mandel="23[Lock]",
        english="sandbox / freeze",
        teach="Lock isolates. Unlock reconnects.",
    ),
    "lattice": Pattern(
        name="lattice",
        nature="crystal / Tonnetz tone-network",
        math="H=fifths V=thirds F=frequency; sparse coords",
        mandel="15[Map] > 14[Bind] :: lattice",
        english="H/V/F harmonic structural plane",
        teach="Lattice is the creativity ground. Overlay can be harmonic or pure math.",
    ),
    "chord": Pattern(
        name="chord",
        nature="several notes sounding as one color",
        math="neighborhood query on interval graph",
        mandel="07[Link] > 21[Merge] :: chord",
        english="pull related cells by harmonic neighborhood",
        teach="Chord retrieval is multi-topic without copying files.",
    ),
    "imagination": Pattern(
        name="imagination",
        nature="seed → engine → latch → charged form",
        math="ima (seed) + gin (loop) + at (coord) + ion (F expand)",
        mandel="08[Create] > 15[Map] > 50[Manifest] :: imagination",
        english="turn a raw idea into a latched 3D cell",
        teach="ima-gin-at-ion is the process, not a daydream: seed, generate, place, manifest.",
    ),
}


def get_pattern(name: str) -> Optional[Pattern]:
    return PATTERNS.get((name or "").lower().strip())


def list_patterns() -> List[Dict[str, str]]:
    return [
        {
            "name": p.name,
            "nature": p.nature,
            "math": p.math,
            "mandel": p.mandel,
            "english": p.english,
            "teach": p.teach,
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
