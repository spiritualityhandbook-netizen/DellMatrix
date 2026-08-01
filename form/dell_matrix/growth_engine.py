#!/usr/bin/env python3
"""
DEPRECATED — do not use for new growth.

NBD 2026-08-01: One growth entrypoint.
Public growth path is RingedGrowth only (form.dell_matrix.ringed_growth).

This module remains for historical reference and smoke compatibility.
All new proposals, FOG cuts, lineage, and Nursery quarantine live in RingedGrowth.

Law:
1. Only live matrix ideas participate.
2. Proposals never auto-enter the matrix.
3. Nursery ideas cannot grow or influence.
4. Nothing in the live matrix is lost.
5. Every proposal carries parent lineage.
"""

from __future__ import annotations

from typing import Any, Dict
import warnings

from form.dell_matrix.nursery import Nursery
from form.dell_matrix.plane import Plane
from form.dell_matrix.ringed_growth import RingedGrowth

warnings.warn(
    "growth_engine.GrowthEngine is deprecated. Use form.dell_matrix.ringed_growth.RingedGrowth",
    DeprecationWarning,
    stacklevel=2,
)


class GrowthEngine:
    """Thin compatibility shim → RingedGrowth."""

    def __init__(self, nursery: Nursery | None = None, **_kwargs):
        self._engine = RingedGrowth(nursery=nursery or Nursery.load())

    def run(self, plane: Plane, cycles: int = 1) -> Dict[str, Any]:
        out = self._engine.run(plane, cycles=cycles)
        out["engine"] = "GrowthEngine→RingedGrowth (deprecated shim)"
        return out
