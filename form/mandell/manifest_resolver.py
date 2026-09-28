#!/usr/bin/env python3
"""Manifest resolver. Number = family. Bracket = modifier. Low confidence -> canonical."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .registry import get_dell
from .core_ii import CORE_II

CONFIDENCE_KEEP = 0.72


@dataclass
class ResolvedManifest:
    dell: int
    requested: str
    resolved: str
    canonical: str
    confidence: float
    reason: str
    kept_modifier: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dell": self.dell,
            "requested_manifest": self.requested,
            "resolved_manifest": self.resolved,
            "canonical_manifest": self.canonical,
            "confidence": self.confidence,
            "reason": self.reason,
            "kept_modifier": self.kept_modifier,
        }


def _family_manifests(n: int) -> Dict[str, str]:
    out = {}
    d = get_dell(n)
    if d:
        out[d["name"].lower()] = d["name"]
    row = CORE_II.get(n)
    if row:
        for m in row.get("manifests", []):
            out[str(m).lower()] = str(m)
    return out


def resolve_manifest(n: int, term: str, context: str = "") -> ResolvedManifest:
    d = get_dell(n)
    canonical = d["name"] if d else f"Dell{n}"
    requested = (term or canonical).strip()
    if not requested:
        return ResolvedManifest(n, requested, canonical, canonical, 1.0, "empty->canonical", False)
    fam = _family_manifests(n)
    key = requested.lower()
    if key == canonical.lower():
        return ResolvedManifest(n, requested, canonical, canonical, 1.0, "canonical", True)
    if key in fam:
        return ResolvedManifest(n, requested, fam[key], canonical, 0.94, "family_manifest", True)
    stem = key[:4]
    for k, v in fam.items():
        if stem and (k.startswith(stem) or stem.startswith(k[:4])):
            return ResolvedManifest(n, requested, v, canonical, 0.78, "morphology", True)
    ctx = (context or "").lower()
    if ctx:
        for k, v in fam.items():
            if k in ctx:
                return ResolvedManifest(n, requested, v, canonical, 0.74, "context", True)
    return ResolvedManifest(n, requested, canonical, canonical, 0.40, "unknown_or_ambiguous->canonical", False)


def keep_modifier(res: ResolvedManifest) -> bool:
    return res.kept_modifier and res.confidence >= CONFIDENCE_KEEP
