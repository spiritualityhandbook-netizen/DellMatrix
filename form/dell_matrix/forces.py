#!/usr/bin/env python3
"""
Nature Forces — ported from src/forces/nature_forces.js into form/.

Modular matrices: water · growth · breath · gravity · time · weather · space
Forces snap into the main matrix, affect growth/resonance, and evolve with use.
Every tick starts with body_pulse (organ sense) so circulation knows the body.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time


FORCE_TYPES = ("water", "growth", "breath", "gravity", "time", "weather", "space")

_STAGES = ["seed", "sprout", "stem", "branch", "leaf", "fruit"]


def _body_pulse_safe() -> Dict[str, Any]:
    try:
        from form.dell_matrix.matrix_body import body_pulse
        return body_pulse()
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}", "missing": [], "decisions": []}


@dataclass
class ForceMatrix:
    name: str = "Force"
    type: str = "custom"
    intensity: float = 0.5
    description: str = ""
    active: bool = True
    evolution_level: float = 1.0
    resonance_log: List[Dict[str, Any]] = field(default_factory=list)

    def record(self, event: Dict[str, Any]) -> None:
        e = dict(event)
        e.setdefault("ts", time.time())
        e["intensity"] = self.intensity
        self.resonance_log.append(e)
        if len(self.resonance_log) > 80:
            self.resonance_log = self.resonance_log[-80:]

    def evolve(self, amount: float = 0.05) -> float:
        self.evolution_level = round(self.evolution_level + amount, 3)
        self.intensity = min(1.0, self.intensity + amount * 0.1)
        return self.evolution_level

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "intensity": round(self.intensity, 3),
            "description": self.description,
            "active": self.active,
            "evolution_level": self.evolution_level,
            "resonance_count": len(self.resonance_log),
        }


@dataclass
class WaterForce(ForceMatrix):
    streams: List[Dict[str, Any]] = field(default_factory=list)
    pools: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        self.name = "Water"
        self.type = "water"
        if not self.description:
            self.description = "Ideas flow like water. Streams merge into rivers."
        if self.intensity == 0.5:
            self.intensity = 0.7

    def flow(self, idea: str, source: str = "local") -> Dict[str, Any]:
        stream = {
            "id": f"stream-{len(self.streams)+1}",
            "idea": str(idea)[:80],
            "source": source,
            "volume": 1.0,
            "form": "stream",
            "merges": [],
        }
        self.streams.append(stream)
        self.record({"type": "flow", "idea": stream["idea"]})
        return stream

    def merge_last_two(self) -> Optional[Dict[str, Any]]:
        active = [s for s in self.streams if s.get("form") in ("stream", "river")]
        if len(active) < 2:
            return None
        a, b = active[-2], active[-1]
        merged = {
            "id": f"river-{len(self.streams)+1}",
            "idea": f"{a['idea']} ⇄ {b['idea']}",
            "source": "merge",
            "volume": a["volume"] + b["volume"],
            "form": "river",
            "parents": [a["id"], b["id"]],
            "merges": [],
        }
        self.streams.append(merged)
        self.evolve(0.08)
        self.record({"type": "merge", "result": merged["idea"]})
        return merged

    def settle(self, stream_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        stream = None
        if stream_id:
            stream = next((s for s in self.streams if s["id"] == stream_id), None)
        elif self.streams:
            stream = self.streams[-1]
        if not stream:
            return None
        stream["form"] = "pool"
        self.pools.append(stream)
        self.record({"type": "settle", "id": stream["id"]})
        return stream


@dataclass
class GrowthForce(ForceMatrix):
    plants: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        self.name = "Growth"
        self.type = "growth"
        if not self.description:
            self.description = "Ideas grow like trees: seed → sprout → stem → branch → leaf → fruit"
        if self.intensity == 0.5:
            self.intensity = 0.65

    def plant(self, idea: str, planter: str = "Operator") -> Dict[str, Any]:
        plant = {
            "id": f"plant-{len(self.plants)+1}",
            "idea": str(idea)[:80],
            "planter": planter,
            "stage": "seed",
            "height": 0.0,
            "age": 0,
            "history": [{"stage": "seed"}],
        }
        self.plants.append(plant)
        self.record({"type": "planted", "idea": plant["idea"]})
        return plant

    def grow_all(self, amount: float = 0.4) -> List[Dict[str, Any]]:
        grown = []
        for plant in self.plants:
            plant["age"] += 1
            plant["height"] = round(plant["height"] + amount * self.intensity, 2)
            idx = _STAGES.index(plant["stage"]) if plant["stage"] in _STAGES else 0
            threshold = (idx + 1) * 1.5
            if plant["height"] >= threshold and idx < len(_STAGES) - 1:
                plant["stage"] = _STAGES[idx + 1]
                plant["history"].append({"stage": plant["stage"], "height": plant["height"]})
                self.evolve(0.05)
                self.record({"type": "growth-stage", "stage": plant["stage"]})
            grown.append(dict(plant))
        return grown

    def map(self) -> List[str]:
        art = {
            "seed": "·", "sprout": "🌱", "stem": "｜",
            "branch": "Ｙ", "leaf": "🌿", "fruit": "🍎",
        }
        return [
            f"  {art.get(p['stage'], '?')} {p['idea'][:40]} [{p['stage']} h={p['height']}]"
            for p in self.plants
        ]


@dataclass
class BreathForce(ForceMatrix):
    phase: str = "inhale"
    cycle: int = 0

    def __post_init__(self):
        self.name = "Breath"
        self.type = "breath"
        if not self.description:
            self.description = "Inhale gathers. Exhale releases. Heartbeat is shared rhythm."
        if self.intensity == 0.5:
            self.intensity = 0.6

    def inhale(self, count: int = 0) -> Dict[str, Any]:
        self.phase = "inhale"
        self.cycle += 1
        self.record({"type": "inhale", "cycle": self.cycle, "count": count})
        return {"phase": "inhale", "cycle": self.cycle, "gathered": count}

    def exhale(self, count: int = 1) -> Dict[str, Any]:
        self.phase = "exhale"
        self.record({"type": "exhale", "cycle": self.cycle, "released": count})
        self.evolve(0.03)
        return {"phase": "exhale", "cycle": self.cycle, "released": count}

    def heartbeat(self, gathered: int = 0) -> Dict[str, Any]:
        inn = self.inhale(gathered)
        out = self.exhale(max(1, gathered // 2 or 1))
        return {"inhale": inn, "exhale": out}


@dataclass
class GravityForce(ForceMatrix):
    wells: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        self.name = "Gravity"
        self.type = "gravity"
        if not self.description:
            self.description = "Heavy ideas pull others toward them."
        if self.intensity == 0.5:
            self.intensity = 0.55

    def set_wells_from_scores(self, nodes: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
        ranked = sorted(nodes, key=lambda n: -float(n.get("score") or 0))[:top_n]
        self.wells = [
            {"id": n.get("id"), "label": n.get("label"), "mass": float(n.get("score") or 0) + 1.0}
            for n in ranked
        ]
        self.record({"type": "wells", "count": len(self.wells)})
        return list(self.wells)


@dataclass
class TimeForce(ForceMatrix):
    tick: int = 0

    def __post_init__(self):
        self.name = "Time"
        self.type = "time"
        if not self.description:
            self.description = "Everything ages. Cycles move only forward."

    def advance(self) -> int:
        self.tick += 1
        self.evolve(0.02)
        self.record({"type": "tick", "tick": self.tick})
        return self.tick


@dataclass
class WeatherForce(ForceMatrix):
    condition: str = "clear"  # clear | rain | storm | fog

    def __post_init__(self):
        self.name = "Weather"
        self.type = "weather"
        if not self.description:
            self.description = "Clear, rain (seeds), storm (shake), fog (reduced clarity)."

    def set_condition(self, condition: str) -> str:
        c = (condition or "clear").lower()
        if c not in ("clear", "rain", "storm", "fog"):
            c = "clear"
        self.condition = c
        self.record({"type": "weather", "condition": c})
        if c == "storm":
            self.evolve(0.04)
        return self.condition


@dataclass
class SpaceForce(ForceMatrix):
    def __post_init__(self):
        self.name = "Space"
        self.type = "space"
        if not self.description:
            self.description = "Negative space and voids between nodes — room to grow."


@dataclass
class ForceField:
    """All nature forces on a Program."""
    water: WaterForce = field(default_factory=WaterForce)
    growth: GrowthForce = field(default_factory=GrowthForce)
    breath: BreathForce = field(default_factory=BreathForce)
    gravity: GravityForce = field(default_factory=GravityForce)
    time: TimeForce = field(default_factory=TimeForce)
    weather: WeatherForce = field(default_factory=WeatherForce)
    space: SpaceForce = field(default_factory=SpaceForce)
    active: List[str] = field(default_factory=lambda: ["growth", "water", "breath"])

    def get(self, force_type: str) -> Optional[ForceMatrix]:
        return getattr(self, force_type, None) if force_type in FORCE_TYPES else None

    def list_forces(self) -> List[Dict[str, Any]]:
        out = []
        for t in FORCE_TYPES:
            f = self.get(t)
            if f:
                d = f.to_dict()
                d["field_active"] = t in self.active
                out.append(d)
        return out

    def activate(self, force_type: str) -> bool:
        if force_type not in FORCE_TYPES:
            return False
        if force_type not in self.active:
            self.active.append(force_type)
        f = self.get(force_type)
        if f:
            f.active = True
        return True

    def deactivate(self, force_type: str) -> bool:
        if force_type in self.active:
            self.active.remove(force_type)
        f = self.get(force_type)
        if f:
            f.active = False
        return True

    def tick(self, nodes: Optional[List[Dict[str, Any]]] = None, owner: str = "Operator") -> Dict[str, Any]:
        """One evolution pulse. Body senses organs first, then forces circulate."""
        nodes = nodes or []
        body = _body_pulse_safe()
        report: Dict[str, Any] = {
            "ok": True,
            "forces": [],
            "body": {
                "present": body.get("present"),
                "missing": body.get("missing"),
                "top_decision": (body.get("decisions") or [{}])[0],
            },
        }
        # Weather responds to body health
        missing = body.get("missing") or []
        if len(missing) >= 8:
            self.weather.set_condition("fog")
        elif len(missing) >= 4:
            self.weather.set_condition("rain")
        else:
            if self.weather.condition == "fog":
                self.weather.set_condition("clear")

        if "time" in self.active:
            report["time"] = self.time.advance()
            report["forces"].append("time")
        if "breath" in self.active:
            report["breath"] = self.breath.heartbeat(len(nodes))
            report["forces"].append("breath")
        if "growth" in self.active:
            known = {p["idea"] for p in self.growth.plants}
            for n in nodes[:8]:
                lab = str(n.get("label") or "")
                if lab and lab not in known:
                    self.growth.plant(lab, owner)
                    known.add(lab)
            # plant body restore labels when vital missing
            for d in (body.get("decisions") or [])[:3]:
                act = str(d.get("action") or "")
                if act.startswith("densify_or_restore:"):
                    organ = act.split(":", 1)[-1]
                    lab = f"Restore {organ}"
                    if lab not in known:
                        self.growth.plant(lab, owner)
                        known.add(lab)
            report["growth"] = self.growth.grow_all()
            report["forces"].append("growth")
        if "water" in self.active and nodes:
            for n in nodes[:3]:
                self.water.flow(str(n.get("label") or n.get("id")), owner)
            if len(self.water.streams) >= 2:
                report["water_merge"] = self.water.merge_last_two()
            report["forces"].append("water")
        if "gravity" in self.active and nodes:
            report["gravity"] = self.gravity.set_wells_from_scores(nodes)
            report["forces"].append("gravity")
        if "weather" in self.active:
            report["weather"] = self.weather.condition
            report["forces"].append("weather")
        report["law"] = "body pulse first · forces circulate · weather tracks organ health"
        return report

    def status(self) -> Dict[str, Any]:
        return {
            "active": list(self.active),
            "forces": self.list_forces(),
            "growth_map": self.growth.map()[:8],
            "water_streams": len(self.water.streams),
            "water_pools": len(self.water.pools),
            "breath": {"phase": self.breath.phase, "cycle": self.breath.cycle},
            "weather": self.weather.condition,
            "time_tick": self.time.tick,
            "gravity_wells": list(self.gravity.wells),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "active": list(self.active),
            "water": {"streams": len(self.water.streams), "pools": len(self.water.pools),
                      "intensity": self.water.intensity, "evolution_level": self.water.evolution_level},
            "growth": {"plants": len(self.growth.plants), "intensity": self.growth.intensity,
                       "evolution_level": self.growth.evolution_level},
            "breath": {"phase": self.breath.phase, "cycle": self.breath.cycle,
                       "evolution_level": self.breath.evolution_level},
            "gravity": {"wells": self.gravity.wells, "evolution_level": self.gravity.evolution_level},
            "time": {"tick": self.time.tick, "evolution_level": self.time.evolution_level},
            "weather": {"condition": self.weather.condition, "evolution_level": self.weather.evolution_level},
            "space": {"evolution_level": self.space.evolution_level},
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "ForceField":
        ff = cls()
        if not data:
            return ff
        ff.active = list(data.get("active") or ff.active)
        w = data.get("water") or {}
        ff.water.intensity = float(w.get("intensity", ff.water.intensity))
        ff.water.evolution_level = float(w.get("evolution_level", 1.0))
        g = data.get("growth") or {}
        ff.growth.intensity = float(g.get("intensity", ff.growth.intensity))
        ff.growth.evolution_level = float(g.get("evolution_level", 1.0))
        b = data.get("breath") or {}
        ff.breath.phase = str(b.get("phase") or "inhale")
        ff.breath.cycle = int(b.get("cycle") or 0)
        ff.breath.evolution_level = float(b.get("evolution_level", 1.0))
        t = data.get("time") or {}
        ff.time.tick = int(t.get("tick") or 0)
        ww = data.get("weather") or {}
        ff.weather.condition = str(ww.get("condition") or "clear")
        return ff


def smoke() -> bool:
    print("=== FORCES SMOKE ===")
    ff = ForceField()
    ff.growth.plant("Alpha")
    ff.growth.grow_all(2.0)
    ff.water.flow("A")
    ff.water.flow("B")
    m = ff.water.merge_last_two()
    ff.breath.heartbeat(2)
    report = ff.tick([{"id": "a", "label": "Test", "score": 1.0}])
    ok = m is not None and report.get("ok") and len(ff.list_forces()) == 7
    ok = ok and "body" in report
    print(f"[{'PASS' if ok else 'FAIL'}] 7 forces + tick + body")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
