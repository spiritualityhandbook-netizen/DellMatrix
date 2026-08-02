#!/usr/bin/env python3
"""
Practical Harmonic Core slice for Origin.

Implements only what scores high on:
  practicality × Origin-relatedness × leverage × safety

Includes:
  - pulse ratio constants (Subkey 4 : Core 1 : Relay 0.25)
  - size policy 12 | 14
  - permanent keys (address never deleted)
  - radial soft-forget of cell payloads by shell

Does NOT include: NPC agendas, social feeds, full relay scheduler threads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

# Pulse ratios from Harmonic form JSON
SUBKEY_PULSE = 4.0
CORE_PULSE = 1.0
RELAY_SWEEP = 0.25  # 1 relay per 4 core
SYNC_LOCK_DEFAULT = True

# Lattice sizes: 12 = chromatic convenience · 14 = Harmonic form geometry
SIZE_CHROMATIC = 12
SIZE_HARMONIC = 14
ALLOWED_SIZES = (SIZE_CHROMATIC, SIZE_HARMONIC)


def pulse_status() -> Dict[str, Any]:
    return {
        "subkey_pulse": SUBKEY_PULSE,
        "core_pulse": CORE_PULSE,
        "relay_sweep": RELAY_SWEEP,
        "ratio": f"{int(SUBKEY_PULSE)}:{int(CORE_PULSE)}:{RELAY_SWEEP}",
        "sync_lock_default": SYNC_LOCK_DEFAULT,
        "note": "constants for future schedulers · Origin-safe",
    }


def normalize_size(size: int) -> int:
    s = int(size)
    if s in ALLOWED_SIZES:
        return s
    # snap to nearest allowed
    return SIZE_CHROMATIC if abs(s - SIZE_CHROMATIC) <= abs(s - SIZE_HARMONIC) else SIZE_HARMONIC


@dataclass
class KeyLedger:
    """
    Permanent keys — Existence rule.
    Payload may soft-forget; key (address) never deleted.
    """
    keys: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def remember(self, key: str, *,
                 meta: Optional[Dict[str, Any]] = None,
                 payload: Any = None) -> str:
        k = (key or "").strip()
        if not k:
            return ""
        prev = self.keys.get(k, {})
        entry = {
            "key": k,
            "hits": int(prev.get("hits", 0)) + 1,
            "meta": dict(meta or prev.get("meta") or {}),
            "has_payload": payload is not None,
            # payload kept only while active; soft_forget clears it
            "payload": payload if payload is not None else prev.get("payload"),
        }
        self.keys[k] = entry
        return k

    def touch(self, key: str) -> bool:
        k = (key or "").strip()
        if k not in self.keys:
            return False
        self.keys[k]["hits"] = int(self.keys[k].get("hits", 0)) + 1
        return True

    def soft_forget(self, key: str) -> bool:
        """Drop payload; keep key address (Existence)."""
        k = (key or "").strip()
        if k not in self.keys:
            return False
        self.keys[k]["payload"] = None
        self.keys[k]["has_payload"] = False
        return True

    def recall(self, key: str) -> Optional[Dict[str, Any]]:
        k = (key or "").strip()
        return dict(self.keys[k]) if k in self.keys else None

    def has_key(self, key: str) -> bool:
        return (key or "").strip() in self.keys

    def list_keys(self) -> List[str]:
        return sorted(self.keys.keys())

    def status(self) -> Dict[str, Any]:
        active = sum(1 for v in self.keys.values() if v.get("has_payload"))
        return {
            "keys": len(self.keys),
            "with_payload": active,
            "soft_forgotten": len(self.keys) - active,
            "rule": "keys permanent · payload may drift",
        }

    def to_dict(self) -> Dict[str, Any]:
        # persist keys + meta; payloads optional
        out = {}
        for k, v in self.keys.items():
            out[k] = {
                "hits": v.get("hits", 0),
                "meta": v.get("meta") or {},
                "has_payload": bool(v.get("has_payload")),
                # payloads not forced into persist blob unless small str
                "payload": v.get("payload") if isinstance(v.get("payload"), (str, int, float, type(None))) else None,
            }
        return out

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "KeyLedger":
        led = cls()
        if not data:
            return led
        for k, v in data.items():
            led.keys[k] = {
                "key": k,
                "hits": int(v.get("hits", 0)),
                "meta": dict(v.get("meta") or {}),
                "has_payload": bool(v.get("has_payload")),
                "payload": v.get("payload"),
            }
        return led


def radial_drift_candidates(
    cells: Dict[Tuple[int, int, int], Any],
    *,
    shell_fn,
    outer_shell: int = 6,
    min_shell: int = 3,
) -> List[Tuple[int, int, int]]:
    """
    Cells on outer shells are drift candidates (payload soft-forget).
    Inner shells (near Zero/origin) are protected.
    """
    out = []
    for coord, cell in cells.items():
        try:
            sh = int(shell_fn(*coord))
        except Exception:
            continue
        if sh >= min_shell and sh >= outer_shell:
            out.append(coord)
    return out


def apply_radial_soft_forget(lattice, ledger: KeyLedger, *,
                             outer_shell: int = 6) -> Dict[str, Any]:
    """
    Soft-forget payloads on far shells; register permanent keys from labels.
    Does not delete cells or keys.
    """
    forgotten = 0
    keyed = 0
    for (h, v, f), cell in list(lattice.cells.items()):
        label = getattr(cell, "label", "") or ""
        content = getattr(cell, "content", None)
        key = label or (str(content) if content is not None else "")
        if key:
            ledger.remember(key, meta={"coords": [h, v, f]}, payload=content)
            keyed += 1
        try:
            sh = lattice.perception.shell(h, v, f)
        except Exception:
            sh = 0
        if sh >= outer_shell and content is not None:
            cell.content = None
            if key:
                ledger.soft_forget(key)
            forgotten += 1
    return {
        "ok": True,
        "keyed": keyed,
        "soft_forgotten": forgotten,
        "outer_shell": outer_shell,
        "ledger": ledger.status(),
    }


def smoke() -> bool:
    print("=== HARMONIC CORE SLICE SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}")
        r.append(bool(ok))
    rec("pulse ratios", SUBKEY_PULSE == 4 and RELAY_SWEEP == 0.25)
    rec("size 14 allowed", normalize_size(14) == 14)
    rec("size snap", normalize_size(13) in ALLOWED_SIZES)
    led = KeyLedger()
    led.remember("business", payload="crm")
    led.soft_forget("business")
    rec("key remains", led.has_key("business"))
    rec("payload gone", led.recall("business").get("payload") is None)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
