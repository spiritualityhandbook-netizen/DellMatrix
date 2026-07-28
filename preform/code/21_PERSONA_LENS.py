#!/usr/bin/env python3
"""
21_PERSONA_LENS.py
Code Phase 4 · Cell 4C
Status: TRUE
Offline · Zero dependencies · Stdlib only

Runtime lenses over Thinks / notes / draft seeds.
Personas never override Floor (Alpha · Delta · Omega · Omni).

Lenses:
- Aetheris  — coherence / fog flag (primary)
- MANUELL   — syntax coach: suggest Dell/flow from raw English (read-only suggestions)
- The_Ancient — structural-only tags; never decipherment claims
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import re

FLOOR = ("Alpha", "Delta", "Omega", "Omni")

# Lightweight keyword → Dell hints (coach only, not execution)
DELL_HINTS: List[Tuple[str, int, str]] = [
    (r"\bcreate\b|\bmake\b|\bnew\b", 8, "Create"),
    (r"\bshow\b|\brender\b|\bdisplay\b", 9, "Show"),
    (r"\bbind\b|\battach\b|\blink\b", 14, "Bind"),
    (r"\btest\b|\bcheck\b|\bassert\b", 12, "Test"),
    (r"\block\b|\bfreeze\b", 23, "Lock"),
    (r"\btransform\b|\bchange\b|\bconvert\b", 4, "Transform"),
    (r"\bkeep\b|\bsave\b|\bpersist\b", 10, "Keep"),
    (r"\bmanifest\b|\bship\b|\breal\b", 50, "Manifest"),
    (r"\bmap\b|\bindex\b|\bcoord", 15, "Map"),
    (r"\bloop\b|\brepeat\b|\buntil\b", 13, "Loop"),
]

FLOW_HINTS: List[Tuple[str, str, str]] = [
    (r"\bthen\b|\bnext\b|\bdo\b", ">", "Primary"),
    (r"\bstrong\b|\bhard\b|\bforce\b", ">>", "Strong Primary"),
    (r"\bbind\b|\bwith\b|\band\b", ":", "Bind"),
    (r"\breverse\b|\bundo\b|\bcorrect\b", "<<[Delta]", "Retrograde"),
]


@dataclass
class LensNote:
    persona: str
    kind: str  # coherence | coach | structural
    text: str


@dataclass
class PersonaLens:
    """
    Optional lenses. All read-only suggestions / tags.
    Never executes Dells. Never claims decipherment.
    """
    aetheris_on: bool = True
    manu_on: bool = True
    ancient_on: bool = True
    notes: List[LensNote] = field(default_factory=list)

    def clear(self) -> None:
        self.notes = []

    # ----- Aetheris: coherence / fog -----

    def aetheris(self, text: str) -> List[LensNote]:
        if not self.aetheris_on:
            return []
        out: List[LensNote] = []
        t = (text or "").strip()
        if not t:
            out.append(LensNote("Aetheris", "coherence", "empty input — no structure to cohere"))
            self.notes.extend(out)
            return out
        fog = []
        if len(t) > 400:
            fog.append("long payload — consider Compress/Distill")
        if t.count("?") > 3:
            fog.append("many questions — split into one seed each")
        lower = t.lower()
        if "maybe" in lower or "somehow" in lower or "whatever" in lower:
            fog.append("hedge words — tighten intent before Manifest")
        if fog:
            out.append(LensNote("Aetheris", "coherence", "fog: " + "; ".join(fog)))
        else:
            out.append(LensNote("Aetheris", "coherence", "clear enough to Bind"))
        self.notes.extend(out)
        return out

    # ----- MANUELL: syntax coach -----

    def manu_ell(self, text: str) -> List[LensNote]:
        if not self.manu_on:
            return []
        out: List[LensNote] = []
        t = text or ""
        lower = t.lower()
        dells: List[str] = []
        for pat, num, name in DELL_HINTS:
            if re.search(pat, lower):
                dells.append(f"{num:02d}[{name}]")
        flows: List[str] = []
        for pat, sym, name in FLOW_HINTS:
            if re.search(pat, lower):
                flows.append(f"{sym} ({name})")
        if dells or flows:
            parts = []
            if dells:
                parts.append("Dells: " + ", ".join(dells[:5]))
            if flows:
                parts.append("Flows: " + ", ".join(flows[:4]))
            # suggest a minimal seed shape (display English + Mandel sketch)
            seed = " ".join(dells[:3]) if dells else "08[Create]"
            if flows:
                seed = f"{seed} {flows[0].split()[0]} …"
            out.append(LensNote("MANUELL", "coach", "; ".join(parts)))
            out.append(LensNote("MANUELL", "coach", f"sketch: {seed}"))
        else:
            out.append(LensNote("MANUELL", "coach", "no strong Dell/flow match — try Create/Show/Bind verbs"))
        self.notes.extend(out)
        return out

    # ----- The_Ancient: structural only -----

    def the_ancient(self, text: str) -> List[LensNote]:
        if not self.ancient_on:
            return []
        out: List[LensNote] = []
        t = text or ""
        # structural metrics only — no language decipherment
        words = re.findall(r"\S+", t)
        lines = t.splitlines() or [t]
        out.append(
            LensNote(
                "The_Ancient",
                "structural",
                f"tokens≈{len(words)} lines={len(lines)} chars={len(t)}",
            )
        )
        # reverse walk tag (boustrophedon-style marker, structural only)
        if words:
            tail = " ".join(words[::-1][:4])
            out.append(LensNote("The_Ancient", "structural", f"retrograde-head: {tail}"))
        out.append(
            LensNote(
                "The_Ancient",
                "structural",
                "structural pattern only — no decipherment claim",
            )
        )
        self.notes.extend(out)
        return out

    # ----- combined pass -----

    def examine(self, text: str) -> List[LensNote]:
        """Run active lenses. Floor is never modified."""
        self.clear()
        self.aetheris(text)
        self.manu_ell(text)
        self.the_ancient(text)
        return list(self.notes)

    def render(self, text: str = "") -> str:
        notes = self.examine(text) if text else self.notes
        lines = [
            "+- Persona Lens -+",
            f"| Floor: {' · '.join(FLOOR)} (locked)",
            f"| Aetheris={'on' if self.aetheris_on else 'off'} "
            f"MANUELL={'on' if self.manu_on else 'off'} "
            f"Ancient={'on' if self.ancient_on else 'off'}",
        ]
        for n in notes:
            lines.append(f"| [{n.persona}/{n.kind}] {n.text}")
        if not notes:
            lines.append("| (no notes)")
        lines.append("+" + "-" * 22 + "+")
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        return {
            "floor": list(FLOOR),
            "aetheris": self.aetheris_on,
            "manuell": self.manu_on,
            "ancient": self.ancient_on,
            "notes": len(self.notes),
        }


def smoke_lens() -> bool:
    print("=== PERSONA LENS SMOKE ===")
    results = []

    def record(name: str, passed: bool, detail: str = "") -> None:
        print(f"[{len(results)+1}] {name}: {'PASS' if passed else 'FAIL'}" + (f" | {detail}" if detail else ""))
        results.append(passed)

    def run(name, fn):
        try:
            ok, detail = fn()
            record(name, bool(ok), detail)
        except Exception as e:
            record(name, False, f"EXCEPTION {type(e).__name__}: {e}")

    lens = PersonaLens()

    run("floor locked constant", lambda: (lens.status()["floor"] == list(FLOOR), str(FLOOR)))
    run("examine returns notes", lambda: (len(lens.examine("create and bind the show")) >= 3, f"n={len(lens.notes)}"))
    run("manu suggests Create", lambda: (
        any("08" in n.text or "Create" in n.text for n in lens.notes if n.persona == "MANUELL"),
        "coach"
    ))
    run("aetheris present", lambda: (any(n.persona == "Aetheris" for n in lens.notes), "coherence"))
    run("ancient no decipherment", lambda: (
        all("decipherment claim" not in n.text.lower() or "no decipherment" in n.text.lower() for n in lens.notes),
        "structural-only"
    ))
    run("render", lambda: ("Persona Lens" in lens.render("test show"), "ok"))

    lens.manu_on = False
    lens.examine("create something")
    run("manu can disable", lambda: (not any(n.persona == "MANUELL" for n in lens.notes), "off"))

    print(f"=== RESULT: {sum(results)}/{len(results)} PASS ===")
    return all(results)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke_lens() else 1)
