#!/usr/bin/env python3
"""
20_SNAP_REGISTRY.py
Distribution / Snap-back support
Status: TRUE
Offline · stdlib only

Tracks local snap packs and validates Floor-safe manifests
before any propose-to-Main step.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import json
import os
import re

FLOOR = {"Alpha", "Delta", "Omega", "Omni"}

@dataclass
class SnapManifest:
    name: str
    author: str = ""
    path: str = ""
    floor_ok: bool = False
    offline_ok: bool = True
    notes: List[str] = field(default_factory=list)
    raw: str = ""

@dataclass
class SnapRegistry:
    root: str
    packs: List[SnapManifest] = field(default_factory=list)

    def scan(self, packs_dir: Optional[str] = None) -> List[SnapManifest]:
        packs_dir = packs_dir or self.root
        self.packs = []
        if not os.path.isdir(packs_dir):
            return self.packs
        for name in sorted(os.listdir(packs_dir)):
            p = os.path.join(packs_dir, name)
            if not os.path.isdir(p):
                continue
            man = os.path.join(p, "MANIFEST.md")
            if not os.path.isfile(man):
                continue
            self.packs.append(self._parse_manifest(man, name))
        return self.packs

    def _parse_manifest(self, path: str, folder: str) -> SnapManifest:
        try:
            raw = open(path, "r", encoding="utf-8").read()
        except Exception as e:
            return SnapManifest(name=folder, path=path, floor_ok=False, notes=[f"read error: {e}"])

        m = SnapManifest(name=folder, path=path, raw=raw)
        # author line
        am = re.search(r"\*\*Author:\*\*\s*(.+)", raw)
        if am:
            m.author = am.group(1).strip()
        nm = re.search(r"\*\*Name:\*\*\s*(.+)", raw)
        if nm:
            m.name = nm.group(1).strip() or folder

        # Floor checklist heuristics
        lower = raw.lower()
        m.floor_ok = (
            "floor untouched" in lower
            or ("alpha" in lower and "delta" in lower and "omega" in lower and "omni" in lower)
        )
        # Reject signals
        if "decipherment" in lower and "no decipherment" not in lower and "not decipherment" not in lower:
            m.notes.append("possible decipherment claim — review")
            m.floor_ok = False
        if "offline" in lower:
            m.offline_ok = True
        m.notes.append("parsed")
        return m

    def validate(self, manifest: SnapManifest) -> Tuple[bool, List[str]]:
        reasons = []
        if not manifest.floor_ok:
            reasons.append("Floor check not confirmed in MANIFEST")
        if not manifest.offline_ok:
            reasons.append("Offline capability unclear")
        if not manifest.name:
            reasons.append("Missing name")
        ok = len(reasons) == 0
        return ok, reasons

    def status(self) -> Dict[str, Any]:
        return {
            "packs": len(self.packs),
            "names": [p.name for p in self.packs],
            "floor_ok": sum(1 for p in self.packs if p.floor_ok),
        }


def smoke_snap() -> bool:
    print("=== SNAP REGISTRY SMOKE ===")
    results = []

    def record(n, p, d=""):
        print(f"[{len(results)+1}] {n}: {'PASS' if p else 'FAIL'}" + (f" | {d}" if d else ""))
        results.append(p)

    def run(n, fn):
        try:
            ok, d = fn()
            record(n, ok, d)
        except Exception as e:
            record(n, False, f"EXCEPTION {type(e).__name__}: {e}")

    # temp pack in memory via parse string
    reg = SnapRegistry(root="/tmp/not_used")
    sample = """# Snap Pack Manifest
**Name:** demo-pack
**Author:** tester
## Floor check
- [x] Floor untouched (Alpha · Delta · Omega · Omni)
- [x] Offline-capable
- [x] No decipherment claims
"""
    import tempfile
    td = tempfile.mkdtemp()
    pack = os.path.join(td, "demo-pack")
    os.makedirs(pack)
    with open(os.path.join(pack, "MANIFEST.md"), "w", encoding="utf-8") as f:
        f.write(sample)

    run("scan", lambda: (len(reg.scan(td)) == 1, f"n={len(reg.packs)}"))
    run("name", lambda: (reg.packs[0].name == "demo-pack", reg.packs[0].name))
    run("floor_ok", lambda: (reg.packs[0].floor_ok, str(reg.packs[0].floor_ok)))
    ok, reasons = reg.validate(reg.packs[0])
    run("validate", lambda: (ok, str(reasons)))
    run("status", lambda: (reg.status()["packs"] == 1, str(reg.status())))

    # bad pack: no floor
    bad = os.path.join(td, "bad")
    os.makedirs(bad)
    with open(os.path.join(bad, "MANIFEST.md"), "w", encoding="utf-8") as f:
        f.write("**Name:** bad\nno floor here\n")
    reg.scan(td)
    bad_m = next(p for p in reg.packs if p.name in ("bad", "bad"))
    vok, _ = reg.validate(bad_m)
    run("reject_bad_floor", lambda: (not vok, "rejected"))

    print(f"=== RESULT: {sum(results)}/{len(results)} PASS ===")
    return all(results)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke_snap() else 1)
