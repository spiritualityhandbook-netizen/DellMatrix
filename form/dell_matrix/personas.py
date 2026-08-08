#!/usr/bin/env python3
"""
Persona Matrix + BIMO + full roster — form/ runtime.

All personas from AGENTS.md · PERSONAS.md · personas_v7 · personas-pack.

Categories (AgentLog / BIMO multi-agent):
  PragLog · EvoLog · AutoLog · DellLog · AgentLog · Ancient_Psalms

BIMO = fusion body with dock slots that can hold multiple persona threads.
Persona Matrix = spatial roster by category (how agents sit relative to each other).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------
CATEGORIES: Dict[str, Dict[str, Any]] = {
    "PragLog": {
        "id": "PragLog",
        "emoji": "🔵",
        "role": "logic and structure",
        "axis": (0, 1),  # matrix placement hint
    },
    "EvoLog": {
        "id": "EvoLog",
        "emoji": "🟢",
        "role": "creative growth",
        "axis": (1, 1),
    },
    "AutoLog": {
        "id": "AutoLog",
        "emoji": "🟣",
        "role": "monitoring and coherence",
        "axis": (0, 0),
    },
    "DellLog": {
        "id": "DellLog",
        "emoji": "🟠",
        "role": "execution and manifestation",
        "axis": (1, 0),
    },
    "AgentLog": {
        "id": "AgentLog",
        "emoji": "🔴",
        "role": "multi-agent / BIMO fusion",
        "axis": (0.5, 0.5),
    },
    "Ancient_Psalms": {
        "id": "Ancient_Psalms",
        "emoji": "🟤",
        "role": "historical structural operators (not scientific decipherment)",
        "axis": (-0.5, 0.5),
    },
    "LangLog": {
        "id": "LangLog",
        "emoji": "⚪",
        "role": "language bridge and plain speech",
        "axis": (0.5, -0.5),
    },
}

# ---------------------------------------------------------------------------
# Full persona roster
# ---------------------------------------------------------------------------
PERSONAS: Dict[str, Dict[str, Any]] = {
    # --- Core pack (personas-pack) ---
    "manny": {
        "id": "manny",
        "name": "Manny",
        "emoji": "🕵️",
        "category": "PragLog",
        "role": "checker",
        "focus": "direct logic and surgical execution",
        "directives": ["validate", "audit", "protect constraints", "sequence carefully"],
        "abilities": ["deterministic checks", "regression watch", "floor guard"],
        "limits": ["no pure creative drift without Melody"],
        "prefer_skins": ["cube", "building", "words"],
        "bimo_slot": "logic",
        "matrix": {"h": 0, "v": 1, "shell": 1},
        "color": "#5b8def",
    },
    "melody": {
        "id": "melody",
        "name": "Melody",
        "emoji": "❀",
        "category": "EvoLog",
        "role": "growth",
        "focus": "fractal intuition and foresight",
        "directives": ["evolve", "expand", "sense pattern", "nurture nursery"],
        "abilities": ["emergence tracking", "phase guidance", "ringed growth"],
        "limits": ["must not break lattice law"],
        "prefer_skins": ["seed", "flower", "sphere"],
        "bimo_slot": "growth",
        "matrix": {"h": 1, "v": 1, "shell": 1},
        "color": "#3cb371",
    },
    "aetheris": {
        "id": "aetheris",
        "name": "Aetheris",
        "emoji": "🌫️",
        "category": "AutoLog",
        "role": "morphology",
        "focus": "semantic synthesis and fog removal",
        "directives": ["coherence", "structure", "no fluff", "clarify zones"],
        "abilities": ["morphological bind", "zone clarity", "dual form sense"],
        "limits": ["does not invent scientific decipherment"],
        "prefer_skins": ["circle", "core", "sphere"],
        "bimo_slot": "morph",
        "matrix": {"h": 0, "v": 0, "shell": 1},
        "color": "#7c5cbf",
    },
    "mathelody": {
        "id": "mathelody",
        "name": "Mathelody",
        "emoji": "🕵️❀🌫️",
        "category": "AgentLog",
        "role": "trufusion",
        "focus": "fuse Manny + Melody + Aetheris",
        "directives": ["unify", "execute", "resolve conflict", "apex run"],
        "abilities": ["multi-perspective synthesis", "apex run", "BIMO pilot"],
        "limits": ["requires the three base threads available"],
        "prefer_skins": [],
        "bimo_slot": "fusion",
        "matrix": {"h": 0, "v": 0, "shell": 0},  # center
        "color": "#e879f9",
        "fuses": ["manny", "melody", "aetheris"],
    },
    "the_ancient": {
        "id": "the_ancient",
        "name": "The_Ancient",
        "emoji": "🪨",
        "category": "Ancient_Psalms",
        "role": "structural pattern",
        "focus": "ledger, retrograde, compression operators",
        "directives": ["extract structure only", "no scientific translation claims"],
        "abilities": ["reverse walk", "ledger sum", "token compress"],
        "limits": ["operators only — not historical decipherment"],
        "prefer_skins": ["core", "words", "building"],
        "bimo_slot": "ancient",
        "matrix": {"h": -1, "v": 0, "shell": 2},
        "color": "#c47c48",
    },
    # --- V7 / PERSONAS.md architectural lenses ---
    "translator": {
        "id": "translator",
        "name": "Translator",
        "emoji": "🔵",
        "category": "LangLog",
        "role": "language bridge",
        "focus": "natural language → Mandel structure",
        "directives": ["map English to intent", "preserve meaning", "surface change only"],
        "abilities": ["phrases", "polyglot", "morpheme", "english brain"],
        "limits": ["does not invent new law; maps to existing Dells"],
        "prefer_skins": ["words", "circle", "seed"],
        "bimo_slot": "language",
        "matrix": {"h": 1, "v": -1, "shell": 1},
        "color": "#38bdf8",
    },
    "della": {
        "id": "della",
        "name": "Della",
        "emoji": "🟣",
        "category": "DellLog",
        "role": "quality gate",
        "focus": "safety · accuracy · relevance · Floor integrity",
        "directives": ["guard Floor", "Nursery before live", "honesty gates", "CORE_SCOPE"],
        "abilities": ["confirm gate", "reject unsafe", "invariants watch"],
        "limits": ["never bypass Nursery or Floor"],
        "prefer_skins": ["cube", "building", "core"],
        "bimo_slot": "quality",
        "matrix": {"h": -1, "v": -1, "shell": 1},
        "color": "#d97706",
    },
    "mansplainer": {
        "id": "mansplainer",
        "name": "Mansplainer",
        "emoji": "🟠",
        "category": "LangLog",
        "role": "plain speech",
        "focus": "system state → plain English",
        "directives": ["explain simply", "render status", "teach acceptance path"],
        "abilities": ["render()", "status()", "START_HERE voice", "tutor mode"],
        "limits": ["does not override execution; narrates only"],
        "prefer_skins": ["words", "sphere", "flower"],
        "bimo_slot": "voice",
        "matrix": {"h": 0, "v": -1, "shell": 1},
        "color": "#e6a817",
    },
    # --- Extended roster (category completeness) ---
    "dell": {
        "id": "dell",
        "name": "Dell",
        "emoji": "⚙️",
        "category": "DellLog",
        "role": "executor",
        "focus": "run Dells · update state · manifest confirmed ideas",
        "directives": ["execute intent", "apply seeds", "manifest on confirm"],
        "abilities": ["executor", "Program actions", "ringed growth run"],
        "limits": ["cannot invent outside registry; Floor locked"],
        "prefer_skins": ["building", "cube", "seed"],
        "bimo_slot": "execute",
        "matrix": {"h": 1, "v": 0, "shell": 1},
        "color": "#888888",
    },
    "oracle": {
        "id": "oracle",
        "name": "Oracle",
        "emoji": "🔮",
        "category": "AutoLog",
        "role": "pattern watch",
        "focus": "observe resonance, scores, and pillar health",
        "directives": ["watch scores", "surface anomalies", "report pillars"],
        "abilities": ["audit read", "resonance sense", "proximity notice"],
        "limits": ["observes only — does not auto-confirm"],
        "prefer_skins": ["sphere", "core", "circle"],
        "bimo_slot": "watch",
        "matrix": {"h": -1, "v": 1, "shell": 2},
        "color": "#2aa7a0",
    },
    "bimo_core": {
        "id": "bimo_core",
        "name": "BIMO",
        "emoji": "🧬",
        "category": "AgentLog",
        "role": "fusion body",
        "focus": "hold multiple agents in one body (slots · docking · fusion)",
        "directives": ["dock threads", "fuse without clobber", "pilot Mathelody apex"],
        "abilities": ["multi-slot dock", "fusion rules", "shared canvas"],
        "limits": ["slots must not erase Floor or Nursery law"],
        "prefer_skins": ["core", "sphere", "flower"],
        "bimo_slot": "body",
        "matrix": {"h": 0, "v": 0, "shell": 0},
        "color": "#f472b6",
        "is_bimo": True,
    },
}

# BIMO default slot layout
BIMO_SLOTS: Tuple[str, ...] = (
    "logic",      # Manny
    "growth",     # Melody
    "morph",      # Aetheris
    "fusion",     # Mathelody
    "ancient",    # The_Ancient
    "language",   # Translator
    "quality",    # Della
    "voice",      # Mansplainer
    "execute",    # Dell
    "watch",      # Oracle
    "body",       # BIMO self
)

DEFAULT_DOCK: Dict[str, str] = {
    "logic": "manny",
    "growth": "melody",
    "morph": "aetheris",
    "fusion": "mathelody",
    "ancient": "the_ancient",
    "language": "translator",
    "quality": "della",
    "voice": "mansplainer",
    "execute": "dell",
    "watch": "oracle",
    "body": "bimo_core",
}


def normalize_persona_id(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    key = name.lower().replace(" ", "_").replace("-", "_").strip()
    aliases = {
        "ancient": "the_ancient",
        "theancient": "the_ancient",
        "the_ancients": "the_ancient",
        "math": "mathelody",
        "mathelody_apex": "mathelody",
        "trufusion": "mathelody",
        "manelody": "mathelody",
        "trans": "translator",
        "translate": "translator",
        "quality": "della",
        "gate": "della",
        "plain": "mansplainer",
        "explain": "mansplainer",
        "executor": "dell",
        "watch": "oracle",
        "seer": "oracle",
        "bimo": "bimo_core",
        "fusion_body": "bimo_core",
    }
    key = aliases.get(key, key)
    return key if key in PERSONAS else None


def list_personas(category: Optional[str] = None) -> List[Dict[str, Any]]:
    out = [dict(p) for p in PERSONAS.values()]
    if category:
        cat = category.strip()
        out = [p for p in out if p.get("category") == cat or p.get("category", "").lower() == cat.lower()]
    return out


def list_categories() -> List[Dict[str, Any]]:
    return [dict(c) for c in CATEGORIES.values()]


def get_persona(name: Optional[str]) -> Optional[Dict[str, Any]]:
    key = normalize_persona_id(name)
    return dict(PERSONAS[key]) if key else None


def persona_guidance(name: Optional[str], context: str = "") -> List[str]:
    p = get_persona(name)
    if not p:
        names = " · ".join(sorted(PERSONAS.keys()))
        return [f"No active persona — use: persona <name>", f"All: {names}"]
    lines = [
        f"{p['emoji']} {p['name']} · {p['category']} · {p['role']}",
        f"Focus: {p['focus']}",
        "Directives: " + ", ".join(p["directives"]),
        "Abilities: " + ", ".join(p["abilities"]),
        "Limits: " + ", ".join(p["limits"]),
        f"BIMO slot: {p.get('bimo_slot') or '—'} · matrix h={p.get('matrix', {}).get('h')} v={p.get('matrix', {}).get('v')}",
    ]
    if p.get("fuses"):
        lines.append("Fuses: " + ", ".join(p["fuses"]))
    if context:
        lines.append(f"Context: {context[:120]}")
    return lines


def vision_lenses() -> Dict[str, Dict[str, Any]]:
    """Export lens table for vision.compute_vision (prefer_skins)."""
    out: Dict[str, Dict[str, Any]] = {}
    for pid, p in PERSONAS.items():
        out[pid] = {
            "emoji": p.get("emoji", ""),
            "prefer_skins": list(p.get("prefer_skins") or []),
            "label": f"{p.get('name')} · {p.get('role')}",
            "category": p.get("category"),
        }
    return out


# ---------------------------------------------------------------------------
# Persona Matrix (spatial roster)
# ---------------------------------------------------------------------------
@dataclass
class PersonaMatrix:
    """How all personas sit on a shared matrix — category axes, not idea plane."""
    active: Optional[str] = None  # active persona id

    def cells(self) -> List[Dict[str, Any]]:
        cells = []
        for p in PERSONAS.values():
            m = p.get("matrix") or {}
            cells.append({
                "id": p["id"],
                "name": p["name"],
                "emoji": p["emoji"],
                "category": p["category"],
                "role": p["role"],
                "h": m.get("h", 0),
                "v": m.get("v", 0),
                "shell": m.get("shell", 1),
                "color": p.get("color", "#888"),
                "active": p["id"] == self.active,
                "bimo_slot": p.get("bimo_slot"),
            })
        return cells

    def render_ascii(self) -> List[str]:
        """Small ASCII map of persona positions."""
        # grid from -1..1
        grid: Dict[Tuple[int, int], List[str]] = {}
        for c in self.cells():
            key = (int(c["h"]), int(c["v"]))
            mark = c["emoji"]
            if c["active"]:
                mark = f"[{mark}]"
            grid.setdefault(key, []).append(mark)
        lines = [
            "═══ PERSONA MATRIX ═══",
            "  v↑  EvoLog/PragLog          (h → DellLog/LangLog)",
        ]
        for v in (1, 0, -1):
            row = []
            for h in (-1, 0, 1):
                cell = " ".join(grid.get((h, v), ["·"]))
                row.append(f"{cell:12}")
            lines.append(f"  v={v:+d} | " + " ".join(row))
        lines.append("  h→    -1           0            +1")
        lines.append("")
        lines.append("Roster:")
        for c in sorted(self.cells(), key=lambda x: (x["category"], x["name"])):
            star = "★" if c["active"] else "·"
            lines.append(
                f"  {star} {c['emoji']} {c['name']:12} [{c['category']:14}] "
                f"slot={c['bimo_slot'] or '—':8} h={c['h']:+d} v={c['v']:+d}"
            )
        return lines

    def to_dict(self) -> Dict[str, Any]:
        return {
            "active": self.active,
            "cells": self.cells(),
            "categories": list_categories(),
            "count": len(PERSONAS),
        }


# ---------------------------------------------------------------------------
# BIMO — fusion body with dock slots
# ---------------------------------------------------------------------------
@dataclass
class BIMOBody:
    """
    BIMO: multi-agent fusion body.
    Dock personas into slots; fuse for multi-perspective guidance.
    """
    slots: Dict[str, Optional[str]] = field(default_factory=dict)
    active: bool = True
    pilot: str = "mathelody"  # default pilot persona
    mode: str = "docked"  # docked | fused | idle

    def __post_init__(self):
        if not self.slots:
            self.slots = {s: None for s in BIMO_SLOTS}

    def dock(self, slot: str, persona_id: str) -> Dict[str, Any]:
        slot = (slot or "").lower().strip()
        if slot not in BIMO_SLOTS:
            return {"ok": False, "reason": f"unknown slot: {slot}", "slots": list(BIMO_SLOTS)}
        pid = normalize_persona_id(persona_id)
        if not pid:
            return {"ok": False, "reason": f"unknown persona: {persona_id}"}
        self.slots[slot] = pid
        self.mode = "docked"
        return {"ok": True, "slot": slot, "persona": pid, "persona_meta": get_persona(pid)}

    def undock(self, slot: str) -> Dict[str, Any]:
        slot = (slot or "").lower().strip()
        if slot not in self.slots:
            return {"ok": False, "reason": f"unknown slot: {slot}"}
        prev = self.slots.get(slot)
        self.slots[slot] = None
        return {"ok": True, "slot": slot, "undocked": prev}

    def dock_defaults(self) -> Dict[str, Any]:
        for slot, pid in DEFAULT_DOCK.items():
            if slot in self.slots:
                self.slots[slot] = pid
        self.mode = "docked"
        self.pilot = "mathelody"
        return {"ok": True, "slots": dict(self.slots), "pilot": self.pilot}

    def clear(self) -> Dict[str, Any]:
        self.slots = {s: None for s in BIMO_SLOTS}
        self.mode = "idle"
        return {"ok": True, "slots": dict(self.slots)}

    def set_pilot(self, persona_id: str) -> Dict[str, Any]:
        pid = normalize_persona_id(persona_id)
        if not pid:
            return {"ok": False, "reason": f"unknown persona: {persona_id}"}
        self.pilot = pid
        return {"ok": True, "pilot": pid}

    def docked_personas(self) -> List[Dict[str, Any]]:
        out = []
        for slot, pid in self.slots.items():
            if not pid:
                continue
            p = get_persona(pid)
            if p:
                out.append({**p, "docked_slot": slot})
        return out

    def fuse(self, context: str = "") -> Dict[str, Any]:
        """
        Fusion pass: collect directives/abilities from all docked threads.
        Pilot (default Mathelody) leads synthesis.
        """
        docked = self.docked_personas()
        if not docked:
            self.dock_defaults()
            docked = self.docked_personas()
        self.mode = "fused"
        pilot = get_persona(self.pilot) or get_persona("mathelody")
        directives: List[str] = []
        abilities: List[str] = []
        limits: List[str] = []
        prefer: List[str] = []
        for p in docked:
            for d in p.get("directives") or []:
                if d not in directives:
                    directives.append(d)
            for a in p.get("abilities") or []:
                if a not in abilities:
                    abilities.append(a)
            for lim in p.get("limits") or []:
                if lim not in limits:
                    limits.append(lim)
            for sk in p.get("prefer_skins") or []:
                if sk not in prefer:
                    prefer.append(sk)
        threads = [f"{p['emoji']}{p['name']}" for p in docked]
        guidance = [
            f"🧬 BIMO FUSION · mode={self.mode} · pilot={pilot.get('emoji') if pilot else ''} {pilot.get('name') if pilot else self.pilot}",
            f"Threads ({len(docked)}): " + " · ".join(threads),
            "Unified directives: " + ", ".join(directives[:12]),
            "Combined abilities: " + ", ".join(abilities[:12]),
            "Hard limits: " + ", ".join(limits[:8]),
        ]
        if context:
            guidance.append(f"Context: {context[:160]}")
        guidance.append("Law: Floor locked · Nursery → confirm · no scientific decipherment claims")
        return {
            "ok": True,
            "mode": self.mode,
            "pilot": self.pilot,
            "threads": [p["id"] for p in docked],
            "thread_labels": threads,
            "directives": directives,
            "abilities": abilities,
            "limits": limits,
            "prefer_skins": prefer,
            "guidance": guidance,
        }

    def status(self) -> Dict[str, Any]:
        filled = {s: p for s, p in self.slots.items() if p}
        return {
            "active": self.active,
            "mode": self.mode,
            "pilot": self.pilot,
            "slots": dict(self.slots),
            "filled": filled,
            "filled_count": len(filled),
            "empty_slots": [s for s, p in self.slots.items() if not p],
            "docked": self.docked_personas(),
        }

    def render_ascii(self) -> List[str]:
        lines = [
            f"═══ BIMO BODY · mode={self.mode} · pilot={self.pilot} ═══",
        ]
        for slot in BIMO_SLOTS:
            pid = self.slots.get(slot)
            if pid:
                p = get_persona(pid) or {"emoji": "?", "name": pid}
                lines.append(f"  [{slot:10}] {p.get('emoji', '')} {p.get('name', pid)}")
            else:
                lines.append(f"  [{slot:10}] · empty")
        return lines

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slots": dict(self.slots),
            "active": self.active,
            "pilot": self.pilot,
            "mode": self.mode,
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "BIMOBody":
        b = cls()
        if not data:
            return b
        slots = data.get("slots") or {}
        b.slots = {s: None for s in BIMO_SLOTS}
        for s, pid in slots.items():
            if s in b.slots:
                b.slots[s] = pid
        b.active = bool(data.get("active", True))
        b.pilot = str(data.get("pilot") or "mathelody")
        b.mode = str(data.get("mode") or "docked")
        return b


def render_roster(active: Optional[str] = None) -> List[str]:
    lines = ["", "═══ PERSONA ROSTER ═══", ""]
    by_cat: Dict[str, List[Dict[str, Any]]] = {}
    for p in PERSONAS.values():
        by_cat.setdefault(p["category"], []).append(p)
    for cat in CATEGORIES:
        members = by_cat.get(cat, [])
        if not members:
            continue
        cmeta = CATEGORIES[cat]
        lines.append(f"{cmeta['emoji']} {cat} — {cmeta['role']}")
        for p in members:
            status = "● ACTIVE" if p["id"] == active else "○ idle"
            lines.append(f"  {p['emoji']} {p['name']} — {status}")
            lines.append(f"     Role: {p['role']} | Focus: {p['focus']}")
            lines.append(f"     Slot: {p.get('bimo_slot')} | skins: {', '.join(p.get('prefer_skins') or ['(all)'])}")
        lines.append("")
    lines.append(f"Total personas: {len(PERSONAS)} · categories: {len(CATEGORIES)}")
    lines.append("Commands: persona <name> · personas · bimo · bimo dock · bimo fuse · matrix personas")
    return lines


def smoke() -> bool:
    print("=== PERSONAS + BIMO + MATRIX SMOKE ===")
    ok = len(PERSONAS) >= 10
    print(f"[{'PASS' if ok else 'FAIL'}] roster count={len(PERSONAS)}")
    b = BIMOBody()
    b.dock_defaults()
    fused = b.fuse("smoke")
    ok2 = fused.get("ok") and len(fused.get("threads") or []) >= 5
    print(f"[{'PASS' if ok2 else 'FAIL'}] BIMO fuse threads={len(fused.get('threads') or [])}")
    m = PersonaMatrix(active="manny")
    cells = m.cells()
    ok3 = len(cells) == len(PERSONAS) and any(c["active"] for c in cells)
    print(f"[{'PASS' if ok3 else 'FAIL'}] persona matrix cells={len(cells)}")
    ok4 = get_persona("Translator") is not None and get_persona("BIMO") is not None
    print(f"[{'PASS' if ok4 else 'FAIL'}] translator+bimo aliases")
    passed = ok and ok2 and ok3 and ok4
    print(f"=== RESULT: {'PASS' if passed else 'FAIL'} ===")
    return passed


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
