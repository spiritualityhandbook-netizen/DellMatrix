#!/usr/bin/env python3
"""
Main third-field — NBD from equation.

21[Merge] : 14[Bind] >> 10[Keep] :: MainThird

When units/cubes sync on the plane:
- Personal units are NOT rewritten
- A third field (Main) receives resonance contributions
- Pull from Main into a personal unit is voluntary only

Run:
  python -m form.dell_matrix.main_field --demo
  python -m form.dell_matrix.main_field --smoke
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import json
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Perspective, Skin, Unit
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Perspective, Skin, Unit


@dataclass
class MainContribution:
    """One sync contribution into Main — not a copy that owns personal units."""

    from_units: Tuple[str, str]
    labels: Tuple[str, str]
    note: str
    weight: float = 1.0


@dataclass
class MainField:
    """
    Shared third space.
    Exists because sync happened. Does not clobber personal planes.
    """

    contributions: List[MainContribution] = field(default_factory=list)
    tags: Dict[str, float] = field(default_factory=dict)  # resonance tags accumulated

    def understand(self) -> Dict[str, Any]:
        return {
            "self": "MainField",
            "role": "third space from sync — no personal clobber",
            "contribution_count": len(self.contributions),
            "tags": dict(self.tags),
            "floor": list(FLOOR),
        }


@dataclass
class MatrixSession:
    """Personal plane + optional link into Main."""

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
    """
    Sync check between two personal units across sessions (or same plane).
    Writes to Main only. Does not mutate unit identity/words/skin of either side.
    """
    assert_floor_intact()
    ua, ub = a.plane.units.get(unit_a), b.plane.units.get(unit_b)
    if not ua or not ub:
        return {"ok": False, "reason": "missing unit"}

    # Snapshot before — must equal after for personal fields
    snap_a = (ua.label, ua.words, ua.skin.value, ua.x, ua.y, ua.sandboxed)
    snap_b = (ub.label, ub.words, ub.skin.value, ub.x, ub.y, ub.sandboxed)

    note = f"sync({ua.label}⊗{ub.label})"
    contrib = MainContribution(
        from_units=(unit_a, unit_b),
        labels=(ua.label, ub.label),
        note=note,
        weight=1.0,
    )
    main.contributions.append(contrib)

    # accumulate soft tags from labels/words (resonance crumbs into Main only)
    for token in (ua.label, ub.label):
        main.tags[token] = main.tags.get(token, 0.0) + 0.5
    for w in (ua.words + " " + ub.words).split():
        if len(w) > 2:
            main.tags[w.lower()] = main.tags.get(w.lower(), 0.0) + 0.1

    # verify no clobber
    ua2, ub2 = a.plane.units[unit_a], b.plane.units[unit_b]
    snap_a2 = (ua2.label, ua2.words, ua2.skin.value, ua2.x, ua2.y, ua2.sandboxed)
    snap_b2 = (ub2.label, ub2.words, ub2.skin.value, ub2.x, ub2.y, ub2.sandboxed)
    if snap_a != snap_a2 or snap_b != snap_b2:
        return {"ok": False, "reason": "clobber detected"}

    return {
        "ok": True,
        "main_note": note,
        "personal_unchanged": True,
        "main_contributions": len(main.contributions),
    }


def voluntary_pull(
    session: MatrixSession,
    unit_id: str,
    main: MainField,
    tag: str,
) -> Dict[str, Any]:
    """
    Pull from Main into personal unit — only if caller asks.
    Appends a note to words; does not replace unit identity.
    """
    assert_floor_intact()
    u = session.plane.units.get(unit_id)
    if not u:
        return {"ok": False, "reason": "missing unit"}
    if tag not in main.tags:
        return {"ok": False, "reason": "tag not in Main"}
    # voluntary annotate — explicit pull
    crumb = f" [pulled:{tag}@{main.tags[tag]:.1f}]"
    if crumb.strip() not in u.words:
        u.words = (u.words + crumb).strip()
    return {"ok": True, "unit": u.id, "words": u.words}


def smoke() -> bool:
    print("=== MAIN FIELD SMOKE ===")
    r: List[bool] = []

    def rec(name: str, ok: bool, detail: str = "") -> None:
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    main = MainField()
    me = MatrixSession("me")
    friend = MatrixSession("friend")
    me.place("biz", "Business", words="CRM routes", skin=Skin.BUILDING, x=1)
    friend.place("art", "Design", words="brand kit", skin=Skin.SPHERE, x=-1)

    before = me.plane.units["biz"].words
    out = sync_planes(me, friend, main, "biz", "art")
    rec("sync ok", out.get("ok") is True, str(out))
    rec("no clobber", me.plane.units["biz"].words == before and out.get("personal_unchanged") is True)
    rec("main grew", len(main.contributions) == 1)
    rec("tags", "Business" in main.tags or "Design" in main.tags, str(main.tags))

    pull = voluntary_pull(me, "biz", main, "Design")
    rec("voluntary pull", pull.get("ok") is True, pull.get("words", ""))
    rec("pull changed only by request", "pulled:Design" in me.plane.units["biz"].words)

    # boxed unit still can sync into Main without rewriting box state
    me.place("cube1", "HarmonicCube", words="core", skin=Skin.CUBE)
    me.plane.box(["cube1"], "s1")
    boxed = me.plane.units["cube1"].sandboxed
    sync_planes(me, friend, main, "cube1", "art")
    rec("box preserved", me.plane.units["cube1"].sandboxed == boxed)

    rec("floor", main.understand()["floor"] == list(FLOOR))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def demo() -> None:
    print("21[Merge] : 14[Bind] >> 10[Keep] :: MainThird")
    print("English: Sync personal planes → Main third field; no clobber; pull voluntary.\n")
    main = MainField()
    me = MatrixSession("me")
    friend = MatrixSession("friend")
    me.place("biz", "Business", words="stain seal CRM", skin=Skin.BUILDING)
    me.place("music", "Music", words="Ep4", skin=Skin.SEED, x=-1)
    friend.place("art", "Design", words="logo system", skin=Skin.SPHERE)
    print("sync biz ⊗ art → Main")
    print(sync_planes(me, friend, main, "biz", "art"))
    print("sync music ⊗ art → Main")
    print(sync_planes(me, friend, main, "music", "art"))
    print("Main understand:", json.dumps(main.understand(), indent=2))
    print("voluntary pull Design into music:")
    print(voluntary_pull(me, "music", main, "Design"))
    print("music words:", me.plane.units["music"].words)
    print("biz words still:", me.plane.units["biz"].words)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()


if __name__ == "__main__":
    main()
