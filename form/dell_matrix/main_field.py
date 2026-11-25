#!/usr/bin/env python3
"""
Main third-field — L3.

21[Merge] : 14[Bind] >> 10[Keep] :: MainThird

Sync → Main only. No personal clobber. Voluntary pull.
L3: ranked tags, pull log, summary, weight stack on repeat syncs.

Run:
  python -m form.dell_matrix.main_field --smoke
  python -m form.dell_matrix.main_field --demo
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
import json
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin, Unit
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin, Unit


@dataclass
class MainContribution:
    from_units: Tuple[str, str]
    labels: Tuple[str, str]
    note: str
    weight: float = 1.0
    ts: str = ""

    def __post_init__(self):
        if not self.ts:
            self.ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class PullRecord:
    unit_id: str
    tag: str
    weight: float
    ts: str


@dataclass
class MainField:
    """Shared third space — L3."""

    contributions: List[MainContribution] = field(default_factory=list)
    tags: Dict[str, float] = field(default_factory=dict)
    pulls: List[PullRecord] = field(default_factory=list)
    level: int = 3

    def top_tags(self, n: int = 5) -> List[Tuple[str, float]]:
        return sorted(self.tags.items(), key=lambda kv: -kv[1])[:n]

    def summary(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "contributions": len(self.contributions),
            "tag_count": len(self.tags),
            "pull_count": len(self.pulls),
            "top_tags": self.top_tags(),
            "floor": list(FLOOR),
        }

    def understand(self) -> Dict[str, Any]:
        return {
            "self": "MainField",
            "level": self.level,
            "role": "third space from sync — no personal clobber",
            "contribution_count": len(self.contributions),
            "tags": dict(self.tags),
            "top_tags": self.top_tags(),
            "pull_count": len(self.pulls),
            "floor": list(FLOOR),
        }


@dataclass
class MatrixSession:
    name: str
    plane: Plane = field(default_factory=Plane)

    def place(self, *args, **kwargs) -> Unit:
        return self.plane.place(*args, **kwargs)


def sync_planes(
    a: MatrixSession,
    b: MatrixSession,
    main: MainField,
    unit_a: str,
    unit_b: str,
) -> Dict[str, Any]:
    assert_floor_intact()
    ua, ub = a.plane.units.get(unit_a), b.plane.units.get(unit_b)
    if not ua or not ub:
        return {"ok": False, "reason": "missing unit"}

    snap_a = (ua.label, ua.words, ua.skin.value, ua.x, ua.y, ua.sandboxed)
    snap_b = (ub.label, ub.words, ub.skin.value, ub.x, ub.y, ub.sandboxed)

    note = f"sync({ua.label}⊗{ub.label})"
    # stack weight if same pair note already exists
    weight = 1.0
    for c in main.contributions:
        if c.note == note:
            weight = c.weight + 0.25
            c.weight = weight  # latest stack on last matching
    contrib = MainContribution(
        from_units=(unit_a, unit_b),
        labels=(ua.label, ub.label),
        note=note,
        weight=weight,
    )
    main.contributions.append(contrib)

    for token in (ua.label, ub.label):
        main.tags[token] = main.tags.get(token, 0.0) + 0.5 * weight
    for w in (ua.words + " " + ub.words).split():
        if len(w) > 2 and not w.startswith("[pulled:"):
            main.tags[w.lower()] = main.tags.get(w.lower(), 0.0) + 0.1 * weight

    ua2, ub2 = a.plane.units[unit_a], b.plane.units[unit_b]
    snap_a2 = (ua2.label, ua2.words, ua2.skin.value, ua2.x, ua2.y, ua2.sandboxed)
    snap_b2 = (ub2.label, ub2.words, ub2.skin.value, ub2.x, ub2.y, ub2.sandboxed)
    if snap_a != snap_a2 or snap_b != snap_b2:
        return {"ok": False, "reason": "clobber detected"}

    return {
        "ok": True,
        "main_note": note,
        "weight": weight,
        "personal_unchanged": True,
        "main_contributions": len(main.contributions),
        "top_tags": main.top_tags(3),
    }


def voluntary_pull(
    session: MatrixSession,
    unit_id: str,
    main: MainField,
    tag: str,
) -> Dict[str, Any]:
    assert_floor_intact()
    u = session.plane.units.get(unit_id)
    if not u:
        return {"ok": False, "reason": "missing unit"}
    if tag not in main.tags:
        return {"ok": False, "reason": "tag not in Main"}
    w = main.tags[tag]
    crumb = f" [pulled:{tag}@{w:.1f}]"
    if crumb.strip() not in u.words:
        u.words = (u.words + crumb).strip()
    main.pulls.append(
        PullRecord(
            unit_id=unit_id,
            tag=tag,
            weight=w,
            ts=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
    )
    return {"ok": True, "unit": u.id, "words": u.words, "pull_count": len(main.pulls)}


def smoke() -> bool:
    print("=== MAIN L3 SMOKE ===")
    r: List[bool] = []

    def rec(name: str, ok: bool, detail: str = "") -> None:
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    main = MainField()
    rec("level 3", main.level == 3)
    me = MatrixSession("me")
    friend = MatrixSession("friend")
    me.place("biz", "Business", words="CRM routes", skin=Skin.BUILDING, x=1)
    friend.place("art", "Design", words="brand kit", skin=Skin.SPHERE, x=-1)

    before = me.plane.units["biz"].words
    out = sync_planes(me, friend, main, "biz", "art")
    rec("sync ok", out.get("ok") is True)
    rec("no clobber", me.plane.units["biz"].words == before)
    out2 = sync_planes(me, friend, main, "biz", "art")
    rec("weight stack", out2.get("weight", 1) > 1.0, str(out2.get("weight")))
    rec("top_tags", len(main.top_tags()) >= 1)

    pull = voluntary_pull(me, "biz", main, "Design")
    rec("pull + log", pull.get("ok") is True and len(main.pulls) == 1)
    rec("summary", main.summary()["pull_count"] == 1 and main.summary()["level"] == 3)
    rec("floor", main.understand()["floor"] == list(FLOOR))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def demo() -> None:
    print("21[Merge] : 14[Bind] >> 10[Keep] :: MainThird L3")
    main = MainField()
    me = MatrixSession("me")
    friend = MatrixSession("friend")
    me.place("biz", "Business", words="CRM", skin=Skin.BUILDING)
    friend.place("art", "Design", words="logo", skin=Skin.SPHERE)
    print(sync_planes(me, friend, main, "biz", "art"))
    print(sync_planes(me, friend, main, "biz", "art"))
    print(json.dumps(main.summary(), indent=2))


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()


if __name__ == "__main__":
    main()
