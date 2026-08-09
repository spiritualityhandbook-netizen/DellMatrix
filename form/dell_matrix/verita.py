#!/usr/bin/env python3
"""
Verita — structural truth checks.

  Pair Verita  = truth-of-overlap between two ideas (vesica + tokens)
  Solo Verita  = integrity of ONE idea standing alone
                 (clarity, density, self-agreement, non-fog, goal load)

Not paranormal. Structural signal only.
Residue marks weak solos and rejected pairs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import re
import time

_TOKEN = re.compile(r"[a-z0-9_]{3,}", re.I)
_FOG = ("asdf", "test123", "xxx", "???", "null", "undefined", "lorem", "TODO_ONLY")


def tokens(text: str) -> Set[str]:
    return {m.group(0).lower() for m in _TOKEN.finditer(text or "")}


# ---------------------------------------------------------------------------
# Geometry vesica (pair)
# ---------------------------------------------------------------------------

def vesica_strength(r1: float, r2: float, distance: float) -> Dict[str, Any]:
    r1, r2 = max(1e-9, float(r1)), max(1e-9, float(r2))
    d = max(0.0, float(distance))
    ssum, diff = r1 + r2, abs(r1 - r2)
    if d >= ssum:
        return {"strength": 0.0, "type": "separate", "distance": d}
    if d <= diff:
        return {"strength": 1.0, "type": "contained", "distance": d}
    strength = 1.0 - (d - diff) / (ssum - diff)
    return {"strength": round(strength, 4), "type": "vesica", "distance": d}


# ---------------------------------------------------------------------------
# Solo Verita — one idea at a time
# ---------------------------------------------------------------------------

def verita_of_one(
    label: str,
    *,
    words: str = "",
    goals: Optional[List[str]] = None,
    detail: str = "",
) -> Dict[str, Any]:
    """
    Integrity of a single idea.

    Axes (0..1 each, then weighted):
      clarity   — length in healthy band, no fog fragments
      density   — enough meaningful tokens
      agreement — label tokens overlap words/detail (self-consistent)
      goal_load — has goals or strong directional language
      structure — not pure punctuation / empty shell
    """
    label = (label or "").strip()
    words = (words or "").strip()
    detail = (detail or "").strip()
    goals = list(goals or [])
    blob = f"{label} {words} {detail} {' '.join(goals)}"
    toks = tokens(blob)
    lab_t = tokens(label)
    body_t = tokens(f"{words} {detail}")

    # clarity: length band + anti-fog
    n = len(label)
    if n < 3:
        clarity = 0.1
    elif n > 72:
        clarity = 0.35
    else:
        clarity = 0.55 + 0.45 * min(1.0, n / 24.0)
    low = label.lower()
    if any(f in low for f in _FOG) or label.count("?") > 2:
        clarity *= 0.35

    # density: token count
    density = min(1.0, len(toks) / 6.0)

    # agreement: label shares meaning with body text
    if not lab_t:
        agreement = 0.2
    elif not body_t:
        agreement = 0.45  # label-only idea is partial but valid seed
    else:
        agreement = len(lab_t & body_t) / max(1, len(lab_t))
        agreement = 0.3 + 0.7 * agreement

    # goal_load
    if goals:
        goal_load = min(1.0, 0.4 + 0.2 * len(goals))
    else:
        directional = {"grow", "restore", "build", "ship", "heal", "unify", "toward", "goal"}
        goal_load = 0.55 if (toks & directional) else 0.25

    # structure: has alphanumeric substance
    structure = 0.9 if lab_t else 0.15
    if not any(c.isalnum() for c in label):
        structure = 0.05

    score = (
        0.25 * clarity
        + 0.20 * density
        + 0.25 * agreement
        + 0.15 * goal_load
        + 0.15 * structure
    )
    score = round(max(0.0, min(1.0, score)), 4)

    # thresholds aligned with soft gates
    if score >= 0.55:
        grade = "strong"
        accept = True
    elif score >= 0.35:
        grade = "viable"
        accept = True
    elif score >= 0.18:
        grade = "weak"
        accept = False  # residue — needs densify
    else:
        grade = "fog"
        accept = False

    return {
        "type": "verita_solo",
        "score": score,
        "grade": grade,
        "accept": accept,
        "axes": {
            "clarity": round(clarity, 3),
            "density": round(density, 3),
            "agreement": round(agreement, 3),
            "goal_load": round(goal_load, 3),
            "structure": round(structure, 3),
        },
        "tokens": sorted(toks)[:12],
        "label": label[:80],
        "note": "solo integrity · one idea at a time",
    }


# ---------------------------------------------------------------------------
# Pair Verita
# ---------------------------------------------------------------------------

def verita_of_pair(
    label_a: str,
    label_b: str,
    *,
    tokens_a: Optional[Set[str]] = None,
    tokens_b: Optional[Set[str]] = None,
    distance: float = 1.0,
    radius: float = 1.0,
    min_jaccard: float = 0.08,
) -> Dict[str, Any]:
    ta = tokens_a if tokens_a is not None else tokens(label_a)
    tb = tokens_b if tokens_b is not None else tokens(label_b)
    inter = len(ta & tb)
    union = len(ta | tb) or 1
    jaccard = inter / union
    geo = vesica_strength(radius, radius, distance)
    # require a whisper of language share OR strong geometry+labels
    score = 0.60 * jaccard + 0.40 * geo["strength"]
    if jaccard < min_jaccard and geo["strength"] < 0.85:
        score *= 0.5  # penalize empty language pairs
    score = round(score, 4)
    accept = score >= 0.18 and (jaccard >= min_jaccard or geo["type"] == "contained")
    return {
        "type": "verita_pair",
        "score": score,
        "jaccard": round(jaccard, 4),
        "vesica": geo,
        "accept": accept,
        "note": "pair coherence · truth-of-overlap",
    }


@dataclass
class ResidueMark:
    location: str
    kind: str
    detail: str
    score: float
    ts: float = field(default_factory=time.time)


class VeritaField:
    def __init__(self) -> None:
        self.links: List[Dict[str, Any]] = []
        self.solos: List[Dict[str, Any]] = []
        self.residue: List[ResidueMark] = []

    def evaluate_one(self, label: str, **kwargs) -> Dict[str, Any]:
        v = verita_of_one(label, **kwargs)
        if v["accept"]:
            self.solos.append({**v, "ts": time.time()})
        else:
            self.residue.append(ResidueMark(
                location=label[:60] or "(empty)",
                kind=f"solo_{v['grade']}",
                detail=f"score={v['score']}",
                score=v["score"],
            ))
        v["residue_count"] = len(self.residue)
        return v

    def evaluate_link(self, a: str, b: str, **kwargs) -> Dict[str, Any]:
        v = verita_of_pair(a, b, **kwargs)
        if v["accept"]:
            self.links.append({"a": a, "b": b, **v, "ts": time.time()})
        else:
            self.residue.append(ResidueMark(
                location=f"{a[:30]}|{b[:30]}",
                kind="pair_mismatch",
                detail=f"score={v['score']}",
                score=v["score"],
            ))
        v["residue_count"] = len(self.residue)
        v["link_count"] = len(self.links)
        return v

    def residue_summary(self) -> Dict[str, Any]:
        return {
            "count": len(self.residue),
            "tail": [
                {"location": r.location, "kind": r.kind, "score": r.score}
                for r in self.residue[-8:]
            ],
            "law": "residue = structural signal from Verita mismatch",
        }


def smoke() -> bool:
    print("=== VERITA SMOKE (solo + pair) ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    strong = verita_of_one(
        "Restore floor skeleton",
        words="vital organ densify foundation",
        goals=["coherence", "offline body"],
    )
    rec("solo_strong", strong["accept"] and strong["grade"] in ("strong", "viable"))

    fog = verita_of_one("??", words="asdf")
    rec("solo_fog", not fog["accept"] and fog["grade"] in ("fog", "weak"))

    seed = verita_of_one("Alpha")
    rec("solo_seed_partial", seed["score"] > 0.15)

    pair_ok = verita_of_pair("Alpha structure grow", "structure clarity grow")
    rec("pair_accept", pair_ok["accept"])

    pair_bad = verita_of_pair("zzz", "qqq", distance=2.0)
    rec("pair_reject", not pair_bad["accept"])

    vf = VeritaField()
    vf.evaluate_one("??")
    vf.evaluate_link("a", "b", distance=3.0)
    rec("residue_logged", vf.residue_summary()["count"] >= 1)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
