#!/usr/bin/env python3
"""
Alpha spirit — compatibility face of the whole Floor spirit.

Prefer: form.dell_matrix.floor_spirit

Alpha is the origin pillar. The whole spirit is Alpha · Delta · Omega · Omni.
This module re-exports FloorSpirit so older imports keep working.
"""
from __future__ import annotations

from form.dell_matrix.floor_spirit import (
    FLOOR_SPIRIT,
    FloorSpirit,
    FloorOrientation,
    bigger_picture,
    license,
    DEFAULT_ORIENTATION,
    PILLAR_ROLES,
)

# Historical name: Alpha was the first face
AlphaSpirit = FloorSpirit
AlphaOrientation = FloorOrientation
ALPHA = FLOOR_SPIRIT

__all__ = [
    "ALPHA",
    "AlphaSpirit",
    "AlphaOrientation",
    "FLOOR_SPIRIT",
    "FloorSpirit",
    "bigger_picture",
    "license",
    "DEFAULT_ORIENTATION",
    "PILLAR_ROLES",
]
