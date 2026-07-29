#!/usr/bin/env python3
"""
Shared Main — multi-owner third field (local disk).

21[Merge] : 25[Pulse] >> 10[Keep] :: SharedMain

Many personal programs can contribute to one shared Main file.
- push: local Main tags/contributions → shared (merge weights)
- pull: shared tags → local Main only (not personal plane units)
- personal cubes never rewritten by shared Main

This is multi_main without a network server — same-machine / shared-folder ready.

Run:
  python -m form.dell_matrix.shared_main --smoke
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json
import os
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.main_field import MainField, MainContribution
    from form.open import open_program
    from form.dell_matrix.plane import Skin
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.main_field import MainField, MainContribution
    from form.open import open_program
    from form.dell_matrix.plane import Skin

_STATE = os.path.join(os.path.dirname(__file__), "..", "state")
os.makedirs(_STATE, exist_ok=True)
DEFAULT_SHARED = os.path.join(_STATE, "main_shared.json")

LEVEL = 3


def _empty() -> Dict[str, Any]:
    return {
        "type": "DellMatrixSharedMain",
        "version": 1,
        "level": LEVEL,
        "floor": list(FLOOR),
        "updated": "",
        "tags": {},
        "contributions": [],
        "owners_seen": [],
    }


def load_shared(path: str = DEFAULT_SHARED) -> Dict[str, Any]:
    if not os.path.isfile(path):
        return _empty()
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if data.get("floor") != list(FLOOR):
        raise RuntimeError("Shared Main Floor mismatch")
    return data


def save_shared(data: Dict[str, Any], path: str = DEFAULT_SHARED) -> str:
    data["floor"] = list(FLOOR)
    data["level"] = LEVEL
    data["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def push_to_shared(
    local: MainField,
    owner: str,
    path: str = DEFAULT_SHARED,
) -> Dict[str, Any]:
    """Merge local Main into shared. Does not touch personal planes."""
    assert_floor_intact()
    shared = load_shared(path)
    tags: Dict[str, float] = {k: float(v) for k, v in shared.get("tags", {}).items()}
    for k, v in local.tags.items():
        tags[k] = tags.get(k, 0.0) + float(v)
    contribs: List[Dict[str, Any]] = list(shared.get("contributions", []))
    for c in local.contributions:
        contribs.append(
            {
                "owner": owner,
                "from_units": list(c.from_units),
                "labels": list(c.labels),
                "note": c.note,
                "weight": c.weight,
                "ts": getattr(c, "ts", ""),
            }
        )
    owners = list(shared.get("owners_seen", []))
    if owner not in owners:
        owners.append(owner)
    shared["tags"] = tags
    shared["contributions"] = contribs[-200:]  # cap log
    shared["owners_seen"] = owners
    path_out = save_shared(shared, path)
    return {
        "ok": True,
        "path": path_out,
        "tag_count": len(tags),
        "owners": owners,
        "personal_clobber": False,
    }


def pull_from_shared(
    local: MainField,
    path: str = DEFAULT_SHARED,
    *,
    mode: str = "merge",
) -> Dict[str, Any]:
    """
    Bring shared tags into local Main only.
    mode=merge: add weights; mode=replace_tags: local tags become shared copy.
    Never mutates plane units.
    """
    assert_floor_intact()
    shared = load_shared(path)
    stags = {k: float(v) for k, v in shared.get("tags", {}).items()}
    if mode == "replace_tags":
        local.tags = dict(stags)
    else:
        for k, v in stags.items():
            local.tags[k] = local.tags.get(k, 0.0) + v
    return {
        "ok": True,
        "mode": mode,
        "shared_tags": len(stags),
        "local_tags": len(local.tags),
        "top": sorted(local.tags.items(), key=lambda kv: -kv[1])[:5],
        "personal_clobber": False,
    }


def shared_summary(path: str = DEFAULT_SHARED) -> Dict[str, Any]:
    data = load_shared(path)
    tags = data.get("tags", {})
    top = sorted(tags.items(), key=lambda kv: -float(kv[1]))[:8]
    return {
        "level": data.get("level", LEVEL),
        "updated": data.get("updated"),
        "owners_seen": data.get("owners_seen", []),
        "tag_count": len(tags),
        "contribution_count": len(data.get("contributions", [])),
        "top_tags": top,
        "floor": data.get("floor", list(FLOOR)),
        "path": path if os.path.isfile(path) else DEFAULT_SHARED,
    }


def smoke() -> bool:
    print("=== SHARED MAIN SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    # isolated path for test
    path = os.path.join(_STATE, "main_shared_smoke.json")
    if os.path.isfile(path):
        os.remove(path)

    a = open_program("OwnerA")
    b = open_program("OwnerB")
    a.place("biz", "Business", words="CRM", skin=Skin.BUILDING)
    b.place("art", "Design", words="logo", skin=Skin.SPHERE)
    # local sync into each Main then push
    from form.dell_matrix.main_field import sync_planes

    sync_planes(a.cube.session, b.cube.session, a.main, "biz", "art")
    before_words = a.cube.session.plane.units["biz"].words

    out = push_to_shared(a.main, "OwnerA", path)
    rec("push A", out.get("ok") is True)
    sync_planes(b.cube.session, a.cube.session, b.main, "art", "biz")
    push_to_shared(b.main, "OwnerB", path)
    summ = shared_summary(path)
    rec("owners", "OwnerA" in summ["owners_seen"] and "OwnerB" in summ["owners_seen"], str(summ["owners_seen"]))
    rec("tags", summ["tag_count"] >= 1)

    c = open_program("OwnerC")
    pull_from_shared(c.main, path)
    rec("C pulled tags", len(c.main.tags) >= 1, str(c.main.top_tags()))
    rec("no clobber A plane", a.cube.session.plane.units["biz"].words == before_words)
    rec("floor", summ["floor"] == list(FLOOR))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    print("21[Merge] : 25[Pulse] >> 10[Keep] :: SharedMain")
    print(json.dumps(shared_summary(), indent=2))


if __name__ == "__main__":
    main()
