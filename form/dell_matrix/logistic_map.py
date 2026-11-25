#!/usr/bin/env python3
"""
Logistic map — Veritasium 'This equation will change how you see the world'
(https://youtu.be/ovJcsL7vyrk)

x → r x (1 - x)

Bifurcation / onset of chaos drives growth intensity and weather-like variability
in DellMatrix ForceField. Offline · educational dynamics only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import random


def logistic_step(x: float, r: float) -> float:
    return r * x * (1.0 - x)


def iterate(x0: float = 0.5, r: float = 3.2, n: int = 50) -> List[float]:
    x = max(1e-9, min(1 - 1e-9, float(x0)))
    out = [x]
    for _ in range(max(1, n)):
        x = logistic_step(x, r)
        out.append(x)
    return out


def classify_regime(r: float) -> str:
    """Rough regime labels (classic logistic map)."""
    if r < 0:
        return "invalid"
    if r < 1:
        return "extinction"
    if r < 3:
        return "stable_fixed"
    if r < 3.45:
        return "period_2"
    if r < 3.57:
        return "period_doubling"
    if r <= 4:
        return "chaos"
    return "divergent"


@dataclass
class LogisticDriver:
    """Stateful driver: map trajectory → ForceField intensity nudges."""
    r: float = 3.2
    x: float = 0.5
    history: List[float] = field(default_factory=list)
    history_max: int = 64

    def step(self) -> float:
        self.x = logistic_step(self.x, self.r)
        self.history.append(self.x)
        if len(self.history) > self.history_max:
            self.history = self.history[-self.history_max :]
        return self.x

    def regime(self) -> str:
        return classify_regime(self.r)

    def set_r(self, r: float) -> str:
        self.r = max(0.0, min(4.0, float(r)))
        return self.regime()

    def intensity_hint(self) -> float:
        """Map x in (0,1) to force intensity-ish [0.15, 0.95]."""
        return round(0.15 + 0.8 * max(0.0, min(1.0, self.x)), 3)

    def apply_to_forces(self, program) -> Dict[str, Any]:
        """Nudge growth + weather from logistic state."""
        val = self.step()
        intensity = self.intensity_hint()
        regime = self.regime()
        report: Dict[str, Any] = {"x": val, "r": self.r, "regime": regime, "intensity": intensity}
        ff = getattr(program, "forces", None)
        if not ff:
            return report
        try:
            if hasattr(ff, "growth") and ff.growth:
                ff.growth.intensity = intensity
            if hasattr(ff, "weather") and ff.weather:
                # chaos → storm tendency; stable → clear
                if regime == "chaos":
                    ff.weather.set_condition("storm")
                elif regime.startswith("period"):
                    ff.weather.set_condition("rain")
                elif regime == "stable_fixed":
                    ff.weather.set_condition("clear")
                else:
                    ff.weather.set_condition("fog")
            report["forces"] = ff.status() if hasattr(ff, "status") else {}
        except Exception as e:
            report["error"] = str(e)
        try:
            program.note_seed(13, "Loop", f"logistic_{regime}")
        except Exception:
            pass
        return report

    def bifurcation_sample(self, r_min: float = 2.5, r_max: float = 4.0, steps: int = 40, settle: int = 30) -> List[Dict[str, float]]:
        """Sample attractor points across r for visualization / analysis."""
        pts = []
        for i in range(steps):
            r = r_min + (r_max - r_min) * i / max(1, steps - 1)
            x = 0.5
            for _ in range(settle):
                x = logistic_step(x, r)
            for _ in range(8):
                x = logistic_step(x, r)
                pts.append({"r": round(r, 4), "x": round(x, 5)})
        return pts

    def status(self) -> Dict[str, Any]:
        return {
            "r": self.r,
            "x": self.x,
            "regime": self.regime(),
            "intensity": self.intensity_hint(),
            "history_len": len(self.history),
            "source": "Veritasium logistic map · educational",
        }


_DRIVER = LogisticDriver()


def logistic_tick(program, r: Optional[float] = None) -> Dict[str, Any]:
    if r is not None:
        _DRIVER.set_r(r)
    return _DRIVER.apply_to_forces(program)


def logistic_status() -> Dict[str, Any]:
    return _DRIVER.status()


def smoke() -> bool:
    print("=== LOGISTIC_MAP SMOKE ===")
    xs = iterate(0.5, 2.5, 20)
    ok1 = all(0 <= x <= 1 for x in xs)
    d = LogisticDriver(r=3.9, x=0.5)
    for _ in range(10):
        d.step()
    ok2 = d.regime() == "chaos"
    ok3 = 0.15 <= d.intensity_hint() <= 0.95
    print(f"[{'PASS' if ok1 and ok2 and ok3 else 'FAIL'}] iterate + chaos regime")
    return ok1 and ok2 and ok3


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
