#!/usr/bin/env python3
"""
Mandell Gate Discipline — recursive constant growth on handicap.

Law:
  Input → Mandel seeds → tags → Dual Lattice route → English out
  Any handicap / missing Dell / tool failure → ↖ Retrograde + Recurdell growth
  Never leave a gap unseeded. Bridge man ↔ computer for everything that can happen.

Layers:
  · Primary Dell 00–50 (most common / necessary)
  · Extended Dell 51–99 (on-demand densify)
  · Symbolic Dell for background processes (Shadow 17, Stream 37, …)
  · Mandellmoji compound seeds for advanced manor
  · One body: no matrix part excluded from execution path

Offline · Boolean host · Floor · Nursery intact.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import time

# ---------------------------------------------------------------------------
# Flows
# ---------------------------------------------------------------------------
FLOW_PRIMARY = "↘"      # default execution
FLOW_NEGATIVE = "↙"     # mirror / adversarial
FLOW_COMPLEX = "↗"      # scope elevation
FLOW_RETROGRADE = "↖"   # recursion / error-correction

# ---------------------------------------------------------------------------
# Primary Dell 00–50 (locked names — most necessary)
# ---------------------------------------------------------------------------
PRIMARY_DELL: Dict[int, str] = {
    0: "Nova", 1: "Initiate", 2: "Persona", 3: "Logic", 4: "Transform",
    5: "Tone", 6: "Cycle", 7: "Link", 8: "Create", 9: "Show",
    10: "Keep", 11: "Architect", 12: "Test", 13: "Loop", 14: "Bind",
    15: "Map", 16: "Decay", 17: "Shadow", 18: "Mirror", 19: "Drive",
    20: "Alpha", 21: "Merge", 22: "Split", 23: "Lock", 24: "Unlock",
    25: "Pulse", 26: "Temp", 27: "Checkpoint", 28: "Rollback", 29: "Compress",
    30: "Expand", 31: "Simulate", 32: "Pause", 33: "Resume", 34: "Stamp",
    35: "Discover", 36: "Inject", 37: "Stream", 38: "Distill", 39: "Schema",
    40: "TokenCount", 41: "Sanitize", 42: "Retry", 43: "Fallback", 44: "Bridge",
    45: "Translate", 46: "Rank", 47: "Embed", 48: "Macro", 49: "Profile",
    50: "Manifest",
}

# ---------------------------------------------------------------------------
# Extended Dell 51–99 — reserved path (densify only on handicap demand)
# ---------------------------------------------------------------------------
EXTENDED_DELL_RESERVE: Dict[int, str] = {
    51: "Harmonic",      # frequency / Fourier bind
    52: "Chess",         # precise pathing (named legacy)
    53: "Checkers",      # probabilistic pathing
    54: "Hypo",          # under-surface foresight
    55: "Hypothermia",   # deep foresight
    56: "ManifestAct",   # Manifest action pair
    57: "Eigen",         # stability spectrum
    58: "Logistic",      # growth intensity / chaos regime
    59: "Fourier",       # DFT / spectrum
    60: "Nature",        # nature-force tick
    61: "Lattice",       # Dual Lattice op
    62: "Verita",        # coherence gate
    63: "Orbit",         # orbit step C²+Δ
    64: "Nursery",       # quarantine grow
    65: "Floor",         # boolean host lock
    66: "EnglishBrain",  # paraphrase / verb map
    67: "Seed",          # Mandel seed emit
    68: "Tag",           # intent/lattice/persona tags
    69: "Route",         # Dell router plan
    70: "Audit",         # incorporation / universal props
    71: "Grow",          # recursive language growth
    72: "Handicap",      # detect limitation
    73: "OneBody",       # unify all parts
    74: "Background",    # symbolic bg process
    75: "Mandellmoji",   # compound visual seed
    76: "Polyglot",      # multi-lang bridge
    77: "Residue",       # stigmergic signal
    78: "Workshop",      # structured edit session
    79: "Fusion",        # multi-persona bind
    80: "SnapIn",        # capability registry
    81: "Offline",       # local-only path
    82: "Vision",        # act-on-seen
    83: "Force",         # ForceField tick
    84: "Particle",      # NoC particle
    85: "Agent",         # seek/flee
    86: "CA",            # cellular automata
    87: "Fractal",       # ringed growth
    88: "NeuroEvo",      # evolution loop
    89: "Trade",         # trading matrix
    90: "Business",      # US&S bridge
    91: "Sister",        # family deploy path
    92: "Oracle",        # projection (PROJECTED_NOT_FACT)
    93: "SUS",           # Superior Ultimate Standard
    94: "Lupe",          # multi-pass loop
    95: "NBD",           # note-build-deploy stamp
    96: "Unify",         # one initiative
    97: "Depth",         # deep stack walk
    98: "Horizon",       # context horizon
    99: "Omega",         # terminal / full cycle close
}

NAMED_OPS = {
    "Bindell": 14, "Duodell": 2, "Evoludell": 4, "Flora-dell": 8,
    "Fluxdell": 25, "Formadell": 9, "Harmonidell": 51, "Limindell": 54,
    "Lumindell": 9, "Mandell-dell": 67, "Mirrordell": 18, "Nature-dell": 60,
    "Pinned-dell": 12, "Prosopadell": 2, "Pulsadell": 25, "Pure-dell": 23,
    "Recurdell": 13, "Sharp-dell": 12, "Transdell": 4,
}

# ---------------------------------------------------------------------------
# Mandellmoji — advanced compound seeds (glyph + Dell + manor)
# ---------------------------------------------------------------------------
MANDELLMOJI: Dict[str, Dict[str, Any]] = {
    "🌱08": {"dell": 8, "manor": "Create", "glyph": "seed-plant"},
    "🔗14": {"dell": 14, "manor": "Bind", "glyph": "vesica-link"},
    "🔄13": {"dell": 13, "manor": "Loop", "glyph": "recur"},
    "🪞18": {"dell": 18, "manor": "Mirror", "glyph": "reflect"},
    "📡25": {"dell": 25, "manor": "Pulse", "glyph": "broadcast"},
    "🛡15": {"dell": 15, "manor": "Map/Guard", "glyph": "protect-index"},
    "🌀51": {"dell": 51, "manor": "Harmonic", "glyph": "frequency"},
    "📈58": {"dell": 58, "manor": "Logistic", "glyph": "growth-chaos"},
    "🌊60": {"dell": 60, "manor": "Nature", "glyph": "force-tick"},
    "🧠70": {"dell": 70, "manor": "Audit", "glyph": "universal-check"},
    "♻71": {"dell": 71, "manor": "Grow", "glyph": "language-expand"},
    "⚠72": {"dell": 72, "manor": "Handicap", "glyph": "limitation"},
    "🕸73": {"dell": 73, "manor": "OneBody", "glyph": "unify"},
    "👁82": {"dell": 82, "manor": "Vision", "glyph": "act-on-seen"},
    "Ω99": {"dell": 99, "manor": "Omega", "glyph": "cycle-close"},
}


@dataclass
class Seed:
    text: str
    dell: int = 0
    flow: str = FLOW_PRIMARY
    tags: Dict[str, str] = field(default_factory=dict)
    mandellmoji: str = ""
    background: bool = False

    def stamp(self) -> Dict[str, Any]:
        name = PRIMARY_DELL.get(self.dell) or EXTENDED_DELL_RESERVE.get(self.dell) or f"Dell{self.dell}"
        return {
            "seed": self.text,
            "dell": self.dell,
            "name": name,
            "flow": self.flow,
            "tags": dict(self.tags),
            "mandellmoji": self.mandellmoji,
            "background": self.background,
        }


@dataclass
class HandicapRecord:
    kind: str
    detail: str
    ts: float = field(default_factory=time.time)
    growth_seed: Optional[Dict[str, Any]] = None


class GateDiscipline:
    """
    Enforces Mandell-inside discipline and grows language on every handicap.
    """

    def __init__(self) -> None:
        self.handicaps: List[HandicapRecord] = []
        self.growth_log: List[Dict[str, Any]] = []
        self.bg_processes: Dict[str, Dict[str, Any]] = {}
        self.unified_parts: List[str] = [
            "nature", "forces", "linear_algebra", "eigen_stability",
            "logistic", "fourier", "harmonic", "lattice", "english_brain",
            "vision", "neuroevo", "nursery", "floor", "live_visual",
            "personas", "trading", "audit",
        ]

    # ----- seed pipeline -----
    def to_seeds(self, user_input: str) -> List[Seed]:
        """Minimal seed extraction — expand via English Brain when bound."""
        text = (user_input or "").strip()
        seeds = [Seed(text=text[:240], dell=1, flow=FLOW_PRIMARY, tags={"intent": "user"})]
        # tag common verbs lightly
        low = text.lower()
        if any(w in low for w in ("test", "audit", "check")):
            seeds.append(Seed("validate", dell=12, flow=FLOW_PRIMARY, tags={"intent": "test"}))
        if any(w in low for w in ("grow", "expand", "evolve")):
            seeds.append(Seed("grow", dell=71, flow=FLOW_PRIMARY, tags={"intent": "grow"}, mandellmoji="♻71"))
        if any(w in low for w in ("unify", "one body", "all parts")):
            seeds.append(Seed("onebody", dell=73, flow=FLOW_COMPLEX, tags={"intent": "unify"}, mandellmoji="🕸73"))
        if any(w in low for w in ("fourier", "spectrum", "frequency")):
            seeds.append(Seed("fourier", dell=59, flow=FLOW_PRIMARY, tags={"domain": "signal"}))
        if any(w in low for w in ("eigen", "stability")):
            seeds.append(Seed("eigen", dell=57, flow=FLOW_PRIMARY, tags={"domain": "stability"}))
        if any(w in low for w in ("nature", "force", "tick")):
            seeds.append(Seed("nature", dell=60, flow=FLOW_PRIMARY, tags={"domain": "physics"}))
        return seeds

    def route(self, seeds: List[Seed]) -> List[Dict[str, Any]]:
        plan = []
        for s in seeds:
            plan.append(s.stamp())
        return plan

    # ----- handicap → growth -----
    def register_handicap(self, kind: str, detail: str) -> Dict[str, Any]:
        """
        Every difficulty becomes language growth.
        Emits ↖ Retrograde · Recurdell(13) · Grow(71) · Handicap(72).
        """
        growth = Seed(
            text=f"HANDICAP→GROW::{kind}::{detail[:120]}",
            dell=71,
            flow=FLOW_RETROGRADE,
            tags={
                "handicap": kind,
                "detail": detail[:80],
                "paired": "72",
                "recur": "13",
            },
            mandellmoji="⚠72",
        )
        # densify extended Dell if kind maps to a free slot concept
        densify = self._maybe_densify(kind)
        rec = HandicapRecord(kind=kind, detail=detail, growth_seed=growth.stamp())
        self.handicaps.append(rec)
        entry = {
            "handicap": kind,
            "detail": detail[:200],
            "growth": growth.stamp(),
            "densify": densify,
            "flow": FLOW_RETROGRADE,
            "law": "limitation expands language",
        }
        self.growth_log.append(entry)
        return entry

    def _maybe_densify(self, kind: str) -> Optional[Dict[str, Any]]:
        """If handicap names a domain, mark corresponding 51–99 Dell as demanded."""
        key = kind.lower().replace(" ", "_")
        for code, name in EXTENDED_DELL_RESERVE.items():
            if name.lower() in key or key in name.lower():
                return {"dell": code, "name": name, "status": "demand_densify"}
        # generic grow slot
        return {"dell": 71, "name": "Grow", "status": "demand_densify"}

    # ----- symbolic Dell background -----
    def bg_start(self, name: str, dell: int = 17, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Symbolic background process under Shadow/Stream Dells."""
        self.bg_processes[name] = {
            "dell": dell,
            "name": PRIMARY_DELL.get(dell) or EXTENDED_DELL_RESERVE.get(dell, str(dell)),
            "meta": meta or {},
            "ts": time.time(),
            "symbolic": True,
        }
        return self.bg_processes[name]

    def bg_list(self) -> Dict[str, Any]:
        return dict(self.bg_processes)

    # ----- one body -----
    def one_body_status(self) -> Dict[str, Any]:
        """No part excluded — report unified initiative surface."""
        return {
            "parts": list(self.unified_parts),
            "count": len(self.unified_parts),
            "initiative": "one body mind universal",
            "dell": 73,
            "mandellmoji": "🕸73",
            "primary_dell_count": len(PRIMARY_DELL),
            "extended_reserve": len(EXTENDED_DELL_RESERVE),
            "path_to_99": True,
        }

    def mandellmoji_resolve(self, token: str) -> Optional[Dict[str, Any]]:
        return MANDELLMOJI.get(token)

    def full_cycle(self, user_input: str) -> Dict[str, Any]:
        """
        Complete gate turn:
          seeds → tags → route → (optional handicap growth) → English-facing report
        """
        seeds = self.to_seeds(user_input)
        plan = self.route(seeds)
        return {
            "input_preview": (user_input or "")[:120],
            "seeds": [s.stamp() for s in seeds],
            "plan": plan,
            "one_body": self.one_body_status(),
            "bg": self.bg_list(),
            "growth_events": len(self.growth_log),
            "handicaps": len(self.handicaps),
            "law": "Mandel-inside · English-out · handicap→grow",
        }


# module singleton for matrix-wide use
GATE = GateDiscipline()


def gate_turn(user_input: str) -> Dict[str, Any]:
    return GATE.full_cycle(user_input)


def on_handicap(kind: str, detail: str) -> Dict[str, Any]:
    return GATE.register_handicap(kind, detail)


def smoke() -> bool:
    print("=== GATE_DISCIPLINE SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    g = GateDiscipline()
    out = g.full_cycle("unify all parts and run audit on fourier eigen")
    rec("seeds_produced", len(out["seeds"]) >= 1)
    rec("one_body", out["one_body"]["dell"] == 73)
    rec("extended_to_99", 99 in EXTENDED_DELL_RESERVE)

    h = g.register_handicap("missing_module", "form.open not in sparse pull")
    rec("handicap_grows", h["growth"]["dell"] == 71 and h["flow"] == FLOW_RETROGRADE)

    g.bg_start("force_tick_shadow", dell=17)
    rec("bg_symbolic", "force_tick_shadow" in g.bg_list())

    mj = g.mandellmoji_resolve("♻71")
    rec("mandellmoji", mj is not None and mj["dell"] == 71)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
