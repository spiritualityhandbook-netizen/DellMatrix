#!/usr/bin/env python3
"""
Shared Main L3 — multi-owner third field (local disk).

21[Merge] : 25[Pulse] >> 10[Keep] :: SharedMain

L3: snapshot export, owners report, merge stamps, still no personal clobber.

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


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _empty() -> Dict[str, Any]:
    return {
        "type": "DellMatrixSharedMain",
        "version": 2,
        "level": LEVEL,
        "floor": list(FLOOR),
        "updated": "",
        "tags": {},
        "contributions": [],
        "owners_seen": [],
        "merges": [],
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
    data["version"] = 2
    data["updated"] = _ts()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def push_to_shared(
    local: MainField,
    owner: str,
    path: str = DEFAULT_SHARED,
) -> Dict[str, Any]:
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
                "ts": getattr(c, "ts", "") or _ts(),
            }
        )
    owners = list(shared.get("owners_seen", []))
    if owner not in owners:
        owners.append(owner)
    merges = list(shared.get("merges", []))
    merges.append({"op": "push", "owner": owner, "ts": _ts(), "tags_in": len(local.tags)})
    shared["tags"] = tags
    shared["contributions"] = contribs[-200:]
    shared["owners_seen"] = owners
    shared["merges"] = merges[-50:]
    path_out = save_shared(shared, path)
    return {
        "ok": True,
        "path": path_out,
        "level": LEVEL,
        "tag_count": len(tags),
        "owners": owners,
        "personal_clobber": False,
    }


def pull_from_shared(
    local: MainField,
    path: str = DEFAULT_SHARED,
    *,
    mode: str = "merge",
    owner: str = "",
) -> Dict[str, Any]:
    assert_floor_intact()
    shared = load_shared(path)
    stags = {k: float(v) for k, v in shared.get("tags", {}).items()}
    if mode == "replace_tags":
        local.tags = dict(stags)
    else:
        for k, v in stags.items():
            local.tags[k] = local.tags.get(k, 0.0) + v
    # stamp merge on shared log if path exists / will exist
    if os.path.isfile(path) or shared.get("owners_seen"):
        merges = list(shared.get("merges", []))
        merges.append({"op": f"pull:{mode}", "owner": owner or "?", "ts": _ts()})
        shared["merges"] = merges[-50:]
        save_shared(shared, path)
    return {
        "ok": True,
        "mode": mode,
        "level": LEVEL,
        "shared_tags": len(stags),
        "local_tags": len(local.tags),
        "top": sorted(local.tags.items(), key=lambda kv: -kv[1])[:5],
        "personal_clobber": False,
    }


def snapshot(path: str = DEFAULT_SHARED, dest: Optional[str] = None) -> str:
    """Freeze a copy of shared Main."""
    data = load_shared(path)
    dest = dest or os.path.join(
        _STATE, f"main_shared_snap_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    )
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return dest


def shared_summary(path: str = DEFAULT_SHARED) -> Dict[str, Any]:
    data = load_shared(path)
    tags = data.get("tags", {})
    top = sorted(tags.items(), key=lambda kv: -float(kv[1]))[:8]
    return {
        "level": data.get("level", LEVEL),
        "version": data.get("version", 1),
        "updated": data.get("updated"),
        "owners_seen": data.get("owners_seen", []),
        "owner_count": len(data.get("owners_seen", [])),
        "tag_count": len(tags),
        "contribution_count": len(data.get("contributions", [])),
        "merge_count": len(data.get("merges", [])),
        "top_tags": top,
        "floor": data.get("floor", list(FLOOR)),
        "path": path if os.path.isfile(path) else DEFAULT_SHARED,
    }


def smoke() -> bool:
    print("=== SHARED MAIN L3 SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    path = os.path.join(_STATE, "main_shared_l3_smoke.json")
    if os.path.isfile(path):
        os.remove(path)

    a = open_program("OwnerA")
    b = open_program("OwnerB")
    a.place("biz", "Business", words="CRM", skin=Skin.BUILDING)
    b.place("art", "Design", words="logo", skin=Skin.SPHERE)
    from form.dell_matrix.main_field import sync_planes

    sync_planes(a.cube.session, b.cube.session, a.main, "biz", "art")
    before = a.cube.session.plane.units["biz"].words
    rec("push", push_to_shared(a.main, "OwnerA", path).get("ok") is True)
    push_to_shared(b.main, "OwnerB", path)
    summ = shared_summary(path)
    rec("level 3", summ.get("level") == 3)
    rec("owners", summ["owner_count"] >= 2)
    rec("merges", summ["merge_count"] >= 1)
    snap = snapshot(path)
    rec("snapshot", os.path.isfile(snap), snap)
    c = open_program("OwnerC")
    pull_from_shared(c.main, path, owner="OwnerC")
    rec("pull", len(c.main.tags) >= 1)
    rec("no clobber", a.cube.session.plane.units["biz"].words == before)
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    print("21[Merge] : 25[Pulse] >> 10[Keep] :: SharedMain L3")
    print(json.dumps(shared_summary(), indent=2))


if __name__ == "__main__":
    main()
