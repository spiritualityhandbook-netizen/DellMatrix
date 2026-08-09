#!/usr/bin/env python3
"""
Delta Pressure — change mechanics of the Floor spirit.

Delta asks: what known gap and unknown fuel move us?

Orbit (Code Evolution):
  C_{n+1} = C_n² + Δ_known + Δ_unknown

  Δ_known     permanent fuel — never closed (missing organs, residue, handicaps, failed checks)
  Δ_unknown   foresight pressure — always labeled PROJECTED_NOT_FACT

Pressure is not anxiety. It is structural difference that must discharge into:
  restore · densify · licensed growth · honest Omega close (when gaps allow)

Offline · Floor-aligned · Verita still judges local.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math
import time

# Vital organs weigh more in Δ_known
VITAL = {
    "floor", "pillars", "plane", "lattice", "nursery", "forces",
    "nature", "ringed_growth", "gate", "brain", "verita", "english_brain",
}

# Soft thresholds (aligned with growth gates)
PRESSURE_STANSTILL = 0.10
PRESSURE_EQUINOX = 0.28
PRESSURE_SOLSTICE = 0.55
PRESSURE_CRITICAL = 0.80


@dataclass
class DeltaKnown:
    """Permanent fuel — recorded gaps that never pretend to be closed until restored."""
    organ_gaps: List[str] = field(default_factory=list)
    vital_gaps: List[str] = field(default_factory=list)
    residue_count: int = 0
    handicaps: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def mass(self) -> float:
        """Scalar fuel mass from known gaps."""
        vital_w = 0.12 * len(self.vital_gaps)
        organ_w = 0.04 * max(0, len(self.organ_gaps) - len(self.vital_gaps))
        res_w = 0.03 * min(12, self.residue_count)
        hand_w = 0.05 * min(8, len(self.handicaps))
        fail_w = 0.06 * min(6, len(self.failed_checks))
        return round(min(1.5, vital_w + organ_w + res_w + hand_w + fail_w), 4)


@dataclass
class DeltaUnknown:
    """Foresight pressure — PROJECTED_NOT_FACT only."""
    projections: List[str] = field(default_factory=list)
    horizon: str = "near"  # near | mid | far
    confidence: float = 0.3  # never claim certainty

    @property
    def mass(self) -> float:
        base = 0.05 * min(6, len(self.projections))
        hz = {"near": 0.08, "mid": 0.12, "far": 0.18}.get(self.horizon, 0.1)
        return round(min(0.6, base + hz * float(self.confidence)), 4)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "projections": list(self.projections)[:8],
            "horizon": self.horizon,
            "confidence": self.confidence,
            "mass": self.mass,
            "label": "PROJECTED_NOT_FACT",
        }


@dataclass
class PressureReading:
    magnitude: float
    band: str
    delta_known: DeltaKnown
    delta_unknown: DeltaUnknown
    c_next_hint: float
    release: List[Dict[str, str]]
    law: str = "C_next ≈ C² + Δ_known + Δ_unknown"


def _band(mag: float) -> str:
    if mag >= PRESSURE_CRITICAL:
        return "critical"
    if mag >= PRESSURE_SOLSTICE:
        return "high"
    if mag >= PRESSURE_EQUINOX:
        return "elevated"
    if mag >= PRESSURE_STANSTILL:
        return "standstill"
    return "calm"


def sense_delta_known(
    *,
    missing: Optional[List[str]] = None,
    residue_count: int = 0,
    handicaps: Optional[List[str]] = None,
    failed_checks: Optional[List[str]] = None,
    notes: Optional[List[str]] = None,
) -> DeltaKnown:
    missing = list(missing or [])
    vital = [m for m in missing if m in VITAL]
    return DeltaKnown(
        organ_gaps=missing,
        vital_gaps=vital,
        residue_count=int(residue_count),
        handicaps=list(handicaps or []),
        failed_checks=list(failed_checks or []),
        notes=list(notes or []),
    )


def sense_delta_unknown(
    projections: Optional[List[str]] = None,
    *,
    horizon: str = "near",
    confidence: float = 0.3,
) -> DeltaUnknown:
    conf = max(0.0, min(0.7, float(confidence)))  # hard cap — never certain
    return DeltaUnknown(
        projections=list(projections or []),
        horizon=horizon if horizon in ("near", "mid", "far") else "near",
        confidence=conf,
    )


def orbit_step(c_now: float, d_known: float, d_unknown: float) -> float:
    """
    Discrete orbit hint: C_next = C² + Δk + Δu  (soft-clamped).
    C is normalized capability / coherence in [0, 1].
    Squaring amplifies strength when already coherent; gaps still add fuel.
    """
    c = max(0.0, min(1.0, float(c_now)))
    raw = c * c + max(0.0, float(d_known)) + max(0.0, float(d_unknown))
    # map back toward a usable [0, 1.5] then soft-cap for UI
    return round(min(1.5, raw), 4)


def release_valves(reading_mag: float, known: DeltaKnown) -> List[Dict[str, str]]:
    """What Delta pressure is allowed to discharge into."""
    acts: List[Dict[str, str]] = []
    if known.vital_gaps:
        top = known.vital_gaps[0]
        acts.append({
            "action": f"restore:{top}",
            "why": f"Vital Δ_known on '{top}' — highest discharge priority",
            "pillar": "Delta",
        })
    if known.organ_gaps and not known.vital_gaps:
        acts.append({
            "action": f"densify:{known.organ_gaps[0]}",
            "why": "Non-vital gap — densify before new fantasy rings",
            "pillar": "Delta",
        })
    if known.residue_count > 0:
        acts.append({
            "action": "examine_residue",
            "why": "Residue is structural Δ_known — re-check Verita mismatches",
            "pillar": "Delta",
        })
    if known.handicaps:
        acts.append({
            "action": "handicap_grow",
            "why": "Gate law: handicap → ↖ Recurdell growth seed",
            "pillar": "Delta",
        })
    if reading_mag < PRESSURE_EQUINOX and not known.vital_gaps:
        acts.append({
            "action": "licensed_grow",
            "why": "Pressure calm enough for Floor-licensed growth",
            "pillar": "Delta",
        })
    if reading_mag >= PRESSURE_CRITICAL:
        acts.append({
            "action": "omega_hold",
            "why": "Critical pressure — Omega forbids false cycle close",
            "pillar": "Omega",
        })
    if not acts:
        acts.append({
            "action": "hold_observe",
            "why": "Low pressure — look before move",
            "pillar": "Delta",
        })
    return acts


def measure_pressure(
    *,
    c_now: float = 0.4,
    missing: Optional[List[str]] = None,
    residue_count: int = 0,
    handicaps: Optional[List[str]] = None,
    failed_checks: Optional[List[str]] = None,
    projections: Optional[List[str]] = None,
    horizon: str = "near",
    confidence: float = 0.3,
    notes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Full Delta pressure reading."""
    known = sense_delta_known(
        missing=missing,
        residue_count=residue_count,
        handicaps=handicaps,
        failed_checks=failed_checks,
        notes=notes,
    )
    unknown = sense_delta_unknown(projections, horizon=horizon, confidence=confidence)
    # magnitude blends known mass (dominant) with unknown (capped)
    magnitude = round(min(1.0, 0.75 * min(1.0, known.mass) + 0.25 * min(1.0, unknown.mass / 0.6)), 4)
    c_next = orbit_step(c_now, known.mass, unknown.mass)
    band = _band(magnitude)
    release = release_valves(magnitude, known)
    return {
        "magnitude": magnitude,
        "band": band,
        "delta_known": {
            "mass": known.mass,
            "vital_gaps": known.vital_gaps,
            "organ_gaps": known.organ_gaps[:12],
            "residue_count": known.residue_count,
            "handicaps": known.handicaps[:8],
            "failed_checks": known.failed_checks[:6],
            "law": "Δ_known is permanent fuel — never closed until restored",
        },
        "delta_unknown": unknown.as_dict(),
        "orbit": {
            "c_now": round(float(c_now), 4),
            "c_next_hint": c_next,
            "formula": "C_next = C_now² + Δ_known.mass + Δ_unknown.mass",
        },
        "release": release,
        "top_action": release[0] if release else None,
        "pillar": "Delta",
        "asks": "What known gap and unknown fuel move us?",
        "ts": time.time(),
    }


def from_body(body_report: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
    """Convenience: measure pressure from a body_pulse-style report."""
    body = body_report or {}
    missing = list(body.get("missing") or [])
    present = float(body.get("present") or 0)
    organ_count = float(body.get("organ_count") or max(present, 1))
    c_now = present / organ_count if organ_count else 0.3
    return measure_pressure(c_now=c_now, missing=missing, **kwargs)


def smoke() -> bool:
    print("=== DELTA PRESSURE SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    calm = measure_pressure(c_now=0.8, missing=[], residue_count=0)
    rec("calm_band", calm["band"] in ("calm", "standstill"))

    hot = measure_pressure(
        c_now=0.3,
        missing=["floor", "nursery", "lattice", "gate"],
        residue_count=4,
        handicaps=["vital_missing:floor"],
        projections=["eventual full organ densify"],
        confidence=0.4,
    )
    rec("hot_elevated", hot["magnitude"] >= PRESSURE_EQUINOX)
    rec("vital_in_known", "floor" in hot["delta_known"]["vital_gaps"])
    rec("top_restore", (hot["top_action"] or {}).get("action", "").startswith("restore"))
    rec("unknown_labeled", hot["delta_unknown"]["label"] == "PROJECTED_NOT_FACT")
    rec("orbit_grows", hot["orbit"]["c_next_hint"] >= hot["orbit"]["c_now"] ** 2)

    print(f"magnitude={hot['magnitude']} band={hot['band']} top={hot['top_action']}")
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
