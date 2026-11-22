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

import re
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


# Canonical alias map (extracted from normalize_persona_id so the
# user layer can refuse ids that would shadow an alias — an alias
# collision is a canonical collision).
_ALIASES: Dict[str, str] = {
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

# ---------------------------------------------------------------------------
# User persona layer — row #155 PERSONAMATRIX (Ace ruling 2026-11-20
# item 11): personamatrix is a user experimentation layer. Users may
# create new personas on the existing BIMO/persona machinery.
#
# Authority law (unchanged): the canonical PERSONAS roster above is
# the runtime authority for the built-in Psalm/persona pack and is
# READ-ONLY at runtime — nothing in this layer mutates it. Custom
# personas live in a UserPersonaLayer, resolve through the same
# lookup functions (canonical wins: a custom id may never shadow a
# canonical id or alias), and persist per owner through the Program
# save (persist section "custom_personas", activated on load).
#
# Isolation law (Director CORRECTION REQUIRED 7069171691): a layer is
# scoped to ONE owner/Program. Every Program owns its own layer;
# Program surfaces (create/remove/lens/matrix/BIMO/persist load)
# always address that layer, so two live Programs in one process can
# never read, overwrite, or remove each other's custom personas.
# The module-level functions keep working without a layer argument
# against the process DEFAULT layer (CUSTOM_PERSONAS) — the surface
# for single-program tools (REPL, vision, standalone BIMOBody); a
# Program never writes the default layer.
#
# A persona is a SETTING — guidance, directives, abilities, limits,
# preferred skins. Docking, fusing, or piloting a persona (built-in
# or custom) confers NO authority: it cannot confirm Nursery
# proposals or hold grants (cf. BIMOBody.effective_capabilities,
# presentation-only by design).
# ---------------------------------------------------------------------------

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_]{0,47}$")


def _clean_str_list(value: Any, field_name: str):
    """Return (list, None) for a non-empty list of non-empty strings,
    else (None, refusal reason)."""
    if not isinstance(value, (list, tuple)) or not value:
        return None, f"{field_name} must be a non-empty list of strings"
    out = []
    for v in value:
        if not isinstance(v, str) or not v.strip():
            return None, f"{field_name} entries must be non-empty strings"
        out.append(v.strip())
    return out, None


def _default_matrix(category: Optional[str]) -> Dict[str, int]:
    """Placement for a persona: its category's axis, shell 1."""
    cat = CATEGORIES.get(category) if isinstance(category, str) else None
    axis = (cat or {}).get("axis") or (0, 0)
    return {
        "h": int(round(float(axis[0]))),
        "v": int(round(float(axis[1]))),
        "shell": 1,
    }


def validate_custom_persona(record: Any) -> Optional[str]:
    """Return a refusal reason, or None when the record is a lawful
    user persona. Pure: never mutates anything."""
    if not isinstance(record, dict):
        return "persona record must be a mapping"
    pid = record.get("id")
    if not isinstance(pid, str) or not pid.strip():
        return "persona id is required"
    pid = pid.strip().lower()
    if pid in PERSONAS:
        return f"id {pid!r} collides with the canonical roster (read-only)"
    if pid in _ALIASES:
        return f"id {pid!r} collides with a canonical persona alias"
    if not _ID_RE.match(pid):
        return "persona id must be lowercase letters/digits/underscores"
    if not isinstance(record.get("name"), str) or not record["name"].strip():
        return "persona name is required"
    category = record.get("category")
    if not isinstance(category, str) or not category.strip():
        return "persona category is required"
    if category not in CATEGORIES:
        return f"unknown category: {category!r}"
    for f in ("role", "focus"):
        if not isinstance(record.get(f), str) or not record[f].strip():
            return f"{f} is required"
    for f in ("directives", "abilities", "limits"):
        _, reason = _clean_str_list(record.get(f), f)
        if reason:
            return reason
    skins = record.get("prefer_skins") or []
    if not isinstance(skins, (list, tuple)) or any(
        not isinstance(s, str) or not s.strip() for s in skins
    ):
        return "prefer_skins must be a list of strings"
    slot = record.get("bimo_slot")
    if slot is not None and slot not in BIMO_SLOTS:
        return f"unknown bimo slot: {slot!r}"
    m = record.get("matrix") or {}
    if not isinstance(m, dict):
        return "matrix must be a mapping {h, v, shell}"
    base = _default_matrix(record.get("category"))
    for k, lo, hi in (("h", -1, 1), ("v", -1, 1), ("shell", 0, 2)):
        v = m.get(k, base[k])
        if not isinstance(v, int) or isinstance(v, bool) or not (lo <= v <= hi):
            return f"matrix {k} must be an int in [{lo}, {hi}]"
    return None


def _normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Fill cleaned lists + matrix defaults on a validated record."""
    rec = dict(record)
    rec["id"] = rec["id"].strip().lower()
    for f in ("directives", "abilities", "limits"):
        cleaned, _ = _clean_str_list(rec.get(f), f)
        rec[f] = cleaned
    rec["prefer_skins"] = [s.strip() for s in (rec.get("prefer_skins") or [])]
    base = _default_matrix(rec.get("category"))
    m = dict(rec.get("matrix") or {})
    rec["matrix"] = {k: int(m.get(k, base[k])) for k in ("h", "v", "shell")}
    rec["custom"] = True
    rec["origin"] = "user"
    return rec


def _create_in(records: Dict[str, Dict[str, Any]],
               name: Optional[str], category: Optional[str],
               role: Optional[str], focus: Optional[str],
               directives: Any, abilities: Any, limits: Any,
               prefer_skins: Optional[Any] = None,
               bimo_slot: Optional[str] = None,
               matrix: Optional[Dict[str, Any]] = None,
               emoji: str = "🧩",
               color: str = "#888888") -> Dict[str, Any]:
    """Create a user persona inside ONE layer's records dict."""
    raw_id = ""
    if isinstance(name, str):
        raw_id = name.lower().replace(" ", "_").replace("-", "_").strip()
    record = {
        "id": raw_id,
        "name": name.strip() if isinstance(name, str) else "",
        "emoji": emoji or "🧩",
        "category": category,
        "role": role,
        "focus": focus,
        "directives": directives,
        "abilities": abilities,
        "limits": limits,
        "prefer_skins": prefer_skins,
        "bimo_slot": bimo_slot,
        "matrix": matrix,
        "color": color or "#888888",
    }
    reason = validate_custom_persona(record)
    if reason:
        return {"ok": False, "reason": reason}
    if record["id"] in records:
        return {"ok": False,
                "reason": f"custom persona {record['id']!r} already exists — remove it first"}
    rec = _normalize_record(record)
    records[rec["id"]] = rec
    return {"ok": True, "persona": dict(rec)}


def _remove_from(records: Dict[str, Dict[str, Any]],
                 name: Optional[str]) -> Dict[str, Any]:
    """Remove a USER persona from ONE layer's records dict. Canonical
    ids (and aliases) are refused — the roster is read-only."""
    key = ""
    if isinstance(name, str):
        key = name.lower().replace(" ", "_").replace("-", "_").strip()
    if key in PERSONAS or key in _ALIASES:
        return {"ok": False,
                "reason": "canonical roster is read-only"}
    if key not in records:
        return {"ok": False, "reason": f"unknown custom persona: {name}"}
    del records[key]
    return {"ok": True, "removed": key}


class PersonaLoadError(Exception):
    """Fail-closed: malformed persisted user-persona state is never
    valid state. Raised by the persist restore path when the saved
    custom-persona section cannot be honored as recorded — the load
    refuses rather than presenting a silently emptied layer."""


def _activate_into(records: Dict[str, Dict[str, Any]],
                   recs: Any) -> Dict[str, Any]:
    """Replace ONE layer's contents with validated records (the
    Program load path). Mutates the dict in place. Invalid records
    are skipped and reported — never half-applied, never silently
    dropped without a count.

    Staging: every record is validated and normalized into a fresh
    dict BEFORE the layer is touched, and the swap is clear+update
    only after the whole loop succeeds — a failure mid-loop (e.g.
    inside normalization) leaves the prior layer fully intact,
    never cleared-and-partial."""
    staged: Dict[str, Dict[str, Any]] = {}
    activated: List[str] = []
    skipped: List[str] = []
    for rec in recs or []:
        if not isinstance(rec, dict):
            skipped.append("<non-mapping>")
            continue
        reason = validate_custom_persona(rec)
        if reason:
            skipped.append(f"{rec.get('id')}: {reason}")
            continue
        norm = _normalize_record(rec)
        staged[norm["id"]] = norm
        activated.append(norm["id"])
    records.clear()
    records.update(staged)
    return {"ok": True, "activated": activated, "skipped": skipped}


class UserPersonaLayer:
    """One scope's user-persona layer (row #155).

    The canonical seam for owner isolation: each Program owns exactly
    one layer, created with the Program and addressed by every
    Program surface. Layers share nothing mutable — the canonical
    PERSONAS roster stays the single read-only authority above all
    of them, and no layer is a parallel registry: lookups resolve
    canonical-first, then the addressed layer only.
    """

    def __init__(self) -> None:
        self.records: Dict[str, Dict[str, Any]] = {}

    def create(self, name: Optional[str], category: Optional[str],
               role: Optional[str], focus: Optional[str],
               directives: Any, abilities: Any, limits: Any,
               prefer_skins: Optional[Any] = None,
               bimo_slot: Optional[str] = None,
               matrix: Optional[Dict[str, Any]] = None,
               emoji: str = "🧩",
               color: str = "#888888") -> Dict[str, Any]:
        return _create_in(self.records, name, category, role, focus,
                          directives, abilities, limits,
                          prefer_skins=prefer_skins, bimo_slot=bimo_slot,
                          matrix=matrix, emoji=emoji, color=color)

    def remove(self, name: Optional[str]) -> Dict[str, Any]:
        return _remove_from(self.records, name)

    def activate(self, records: Any) -> Dict[str, Any]:
        return _activate_into(self.records, records)

    def all(self) -> List[Dict[str, Any]]:
        return [dict(p) for p in self.records.values()]

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        p = self.records.get(key)
        return dict(p) if p else None


# The process DEFAULT layer: module-level calls without a layer
# argument address it (single-program tools — REPL, vision,
# standalone BIMOBody). CUSTOM_PERSONAS is its records dict, kept as
# the historical name for that default surface. Programs NEVER write
# here; a Program's layer is its own UserPersonaLayer.
_DEFAULT_LAYER = UserPersonaLayer()
CUSTOM_PERSONAS: Dict[str, Dict[str, Any]] = _DEFAULT_LAYER.records


def _resolve_layer(layer: Optional[UserPersonaLayer]) -> UserPersonaLayer:
    return layer if layer is not None else _DEFAULT_LAYER


def create_custom_persona(name: Optional[str], category: Optional[str],
                          role: Optional[str], focus: Optional[str],
                          directives: Any, abilities: Any, limits: Any,
                          prefer_skins: Optional[Any] = None,
                          bimo_slot: Optional[str] = None,
                          matrix: Optional[Dict[str, Any]] = None,
                          emoji: str = "🧩",
                          color: str = "#888888",
                          layer: Optional[UserPersonaLayer] = None
                          ) -> Dict[str, Any]:
    """Create a user persona in the experimentation layer.

    The persona becomes resolvable/dockable immediately (same lookup
    functions as the canonical roster) and is carried in the caller's
    persisted records by the Program layer. Refusals: canonical id or
    alias collision, unknown category/slot, missing role/focus, empty
    directives/abilities/limits (every persona declares its fences),
    duplicate custom id (remove first — no silent overwrite).

    ``layer`` selects the owner scope; None addresses the process
    default layer (single-program tools). Programs always pass their
    own layer.
    """
    return _resolve_layer(layer).create(
        name, category, role, focus, directives, abilities, limits,
        prefer_skins=prefer_skins, bimo_slot=bimo_slot, matrix=matrix,
        emoji=emoji, color=color)


def remove_custom_persona(name: Optional[str],
                          layer: Optional[UserPersonaLayer] = None
                          ) -> Dict[str, Any]:
    """Remove a USER persona from the experimentation layer. Canonical
    ids (and aliases) are refused — the roster is read-only."""
    return _resolve_layer(layer).remove(name)


def activate_custom_personas(records: Any,
                             layer: Optional[UserPersonaLayer] = None
                             ) -> Dict[str, Any]:
    """Replace a layer's contents with validated records (the Program
    load path). Invalid records are skipped and reported — never
    half-applied, never silently dropped without a count."""
    return _resolve_layer(layer).activate(records)


def custom_personas(layer: Optional[UserPersonaLayer] = None
                    ) -> List[Dict[str, Any]]:
    """Copies of a user layer (canonical roster excluded)."""
    return _resolve_layer(layer).all()


def all_personas(layer: Optional[UserPersonaLayer] = None
                 ) -> List[Dict[str, Any]]:
    """Canonical roster first (authority), then the user layer."""
    return [dict(p) for p in PERSONAS.values()] + custom_personas(layer)


def normalize_persona_id(name: Optional[str],
                         layer: Optional[UserPersonaLayer] = None
                         ) -> Optional[str]:
    if not name:
        return None
    key = name.lower().replace(" ", "_").replace("-", "_").strip()
    key = _ALIASES.get(key, key)
    if key in PERSONAS or key in _resolve_layer(layer).records:
        return key
    return None


def list_personas(category: Optional[str] = None,
                  layer: Optional[UserPersonaLayer] = None
                  ) -> List[Dict[str, Any]]:
    out = all_personas(layer)
    if category:
        cat = category.strip()
        out = [p for p in out if p.get("category") == cat or p.get("category", "").lower() == cat.lower()]
    return out


def list_categories() -> List[Dict[str, Any]]:
    return [dict(c) for c in CATEGORIES.values()]


def get_persona(name: Optional[str],
                layer: Optional[UserPersonaLayer] = None
                ) -> Optional[Dict[str, Any]]:
    key = normalize_persona_id(name, layer=layer)
    if not key:
        return None
    if key in PERSONAS:
        return dict(PERSONAS[key])
    return _resolve_layer(layer).get(key)


def persona_guidance(name: Optional[str], context: str = "",
                     layer: Optional[UserPersonaLayer] = None) -> List[str]:
    p = get_persona(name, layer=layer)
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


def vision_lenses(layer: Optional[UserPersonaLayer] = None
                  ) -> Dict[str, Dict[str, Any]]:
    """Export lens table for vision.compute_vision (prefer_skins)."""
    out: Dict[str, Dict[str, Any]] = {}
    for pid, p in {**PERSONAS, **_resolve_layer(layer).records}.items():
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
    # Owner scope for the user layer (None = process default layer).
    # Bound by the owning Program; a runtime binding, never persisted.
    layer: Optional[UserPersonaLayer] = field(default=None, repr=False,
                                              compare=False)

    def cells(self) -> List[Dict[str, Any]]:
        cells = []
        for p in all_personas(self.layer):
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
        cells = self.cells()
        return {
            "active": self.active,
            "cells": cells,
            "categories": list_categories(),
            "count": len(cells),
            "canonical_count": len(PERSONAS),
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
    # Owner scope for the user layer (None = process default layer).
    # Bound by the owning Program; a runtime binding, never persisted.
    layer: Optional[UserPersonaLayer] = field(default=None, repr=False,
                                              compare=False)

    def __post_init__(self):
        if not self.slots:
            self.slots = {s: None for s in BIMO_SLOTS}

    def dock(self, slot: str, persona_id: str) -> Dict[str, Any]:
        slot = (slot or "").lower().strip()
        if slot not in BIMO_SLOTS:
            return {"ok": False, "reason": f"unknown slot: {slot}", "slots": list(BIMO_SLOTS)}
        pid = normalize_persona_id(persona_id, layer=self.layer)
        if not pid:
            return {"ok": False, "reason": f"unknown persona: {persona_id}"}
        self.slots[slot] = pid
        self.mode = "docked"
        return {"ok": True, "slot": slot, "persona": pid, "persona_meta": get_persona(pid, layer=self.layer)}

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
        pid = normalize_persona_id(persona_id, layer=self.layer)
        if not pid:
            return {"ok": False, "reason": f"unknown persona: {persona_id}"}
        self.pilot = pid
        return {"ok": True, "pilot": pid}

    def docked_personas(self) -> List[Dict[str, Any]]:
        out = []
        for slot, pid in self.slots.items():
            if not pid:
                continue
            p = get_persona(pid, layer=self.layer)
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
        pilot = get_persona(self.pilot, layer=self.layer) or get_persona("mathelody", layer=self.layer)
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

    def effective_capabilities(
        self, grants: Dict[str, List[str]]
    ) -> List[str]:
        """PRESENTATION UTILITY ONLY — not an enforcement mechanism.

        R6.5 (AMEND): Caller-supplied capability name lists are
        DESCRIPTIVE data, not validated grants. This method computes
        the intersection for display purposes (e.g., showing what a
        BIMO fusion *would* be able to do if all constituents held
        those grants).

        It does NOT:
        - Validate grants against the AcceptancePolicy
        - Bind operations, targets, or content
        - Enforce anything at execution time

        Real authority comes ONLY from grants issued through the
        trusted host path (agent_authority.issue_root_grant) and
        validated at dispatch time by the coordinator.

        Persona docking must never change permission. This method
        exists for UI/guidance; it is never consulted for decisions.
        """
        docked = self.docked_personas()
        if not docked:
            return []
        # Start with the first persona's grants, intersect with the rest.
        common = None
        for p in docked:
            pid = p.get("id", "")
            granted = set(grants.get(pid, []))
            if common is None:
                common = granted
            else:
                common &= granted
            if not common:
                break
        return sorted(common or [])

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


def render_roster(active: Optional[str] = None,
                  layer: Optional[UserPersonaLayer] = None) -> List[str]:
    lines = ["", "═══ PERSONA ROSTER ═══", ""]
    by_cat: Dict[str, List[Dict[str, Any]]] = {}
    for p in all_personas(layer):
        by_cat.setdefault(p["category"], []).append(p)
    for cat in CATEGORIES:
        members = by_cat.get(cat, [])
        if not members:
            continue
        cmeta = CATEGORIES[cat]
        lines.append(f"{cmeta['emoji']} {cat} — {cmeta['role']}")
        for p in members:
            status = "● ACTIVE" if p["id"] == active else "○ idle"
            if p.get("custom"):
                status += " · custom"
            lines.append(f"  {p['emoji']} {p['name']} — {status}")
            lines.append(f"     Role: {p['role']} | Focus: {p['focus']}")
            lines.append(f"     Slot: {p.get('bimo_slot')} | skins: {', '.join(p.get('prefer_skins') or ['(all)'])}")
        lines.append("")
    _n_custom = len(_resolve_layer(layer).records)
    lines.append(f"Total personas: {len(PERSONAS) + _n_custom} "
                 f"(canonical {len(PERSONAS)} · custom {_n_custom}) "
                 f"· categories: {len(CATEGORIES)}")
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
    ok3 = len(cells) == len(PERSONAS) + len(CUSTOM_PERSONAS) and any(c["active"] for c in cells)
    print(f"[{'PASS' if ok3 else 'FAIL'}] persona matrix cells={len(cells)}")
    ok4 = get_persona("Translator") is not None and get_persona("BIMO") is not None
    print(f"[{'PASS' if ok4 else 'FAIL'}] translator+bimo aliases")
    passed = ok and ok2 and ok3 and ok4
    print(f"=== RESULT: {'PASS' if passed else 'FAIL'} ===")
    return passed


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
