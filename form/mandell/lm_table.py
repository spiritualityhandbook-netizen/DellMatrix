#!/usr/bin/env python3
"""LM-1 table — additive, read-only loader (LM-1 harvest-only build).

Authorized by Director mail 1a1cc55119b5979f (2026-11-11) as part of
the ONE bounded in-repo HARVEST-ONLY LM-1 build. The table
(lm_table_v1.json, built by form/lm1_harvest.py from in-repo sources
only; the external roots table is under a Q-LM1.1 HOLD and was NOT
imported) is ADDITIVE data beside the existing authorities:

- If the table file is ABSENT, load_table() returns an empty table
  and every consumer behaves exactly as today. No existing module
  depends on this loader; nothing is wired into translate.py, the
  executor, or the REPL (that wiring is LM-4's circuit, not LM-1).
- latinmandell.py / morpheme.py behavior is untouched: their dicts,
  first-match rules, and customs handling are exactly as before.

Precedence (annotation only -- this loader changes no runtime
resolution): customs > ace_seed > inrepo > inrepo_force >
inrepo_legacy > candidate. Customs are runtime state (persist v7)
and are never in the shipped table; a bound custom outranks every
shipped stratum, exactly as root_of() already behaves.

lookup() returns the FULL row set for a piece, best-precedence
first, each row annotated with precedence_rank. It never silently
first-matches: callers (LM-2, later) see every stratum's claim,
including position_unresolved rows for quarantined pieces
(dell / man / re / alpha / delta / omega -- Q-LM1.3-Q-LM1.6 open).
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TABLE_PATH = os.path.join(_HERE, "lm_table_v1.json")
DEFAULT_COLLISIONS_PATH = os.path.join(_HERE,
                                       "lm_table_v1.collisions.json")

PRECEDENCE = ["customs", "ace_seed", "inrepo", "inrepo_force",
              "inrepo_legacy", "candidate"]
_RANK = {name: i for i, name in enumerate(PRECEDENCE)}


def _norm(piece: str) -> str:
    return (piece or "").strip().strip("-").lower()


def load_table(path: Optional[str] = None) -> Dict[str, Any]:
    """Load the LM-1 table. Missing file -> empty table, no raise:
    {'header': None, 'rows': []} (today's behavior, exactly)."""
    p = path or DEFAULT_TABLE_PATH
    if not os.path.exists(p):
        return {"header": None, "rows": []}
    with open(p, encoding="utf-8") as f:
        doc = json.load(f)
    return {"header": doc.get("header"), "rows": doc.get("rows", [])}


def load_collisions(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load the collision log. Missing file -> empty list."""
    p = path or DEFAULT_COLLISIONS_PATH
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def lookup(piece: str,
           table: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """ALL rows for a piece across strata, best precedence first.

    Each returned row is a copy annotated with 'precedence_rank'
    (lower = higher precedence; customs would rank 0 at runtime but
    are never shipped rows). Returns [] when the piece is unknown
    or the table is absent -- never raises, never first-matches.
    """
    t = table if table is not None else load_table()
    key = _norm(piece)
    if not key:
        return []
    out = []
    for row in t.get("rows", []):
        if row.get("piece") == key:
            annotated = dict(row)
            annotated["precedence_rank"] = _RANK.get(
                row.get("stratum"), len(PRECEDENCE))
            out.append(annotated)
    out.sort(key=lambda r: (r["precedence_rank"],
                            r.get("authored_position_class", "")))
    return out


def smoke() -> bool:
    print("=== LM TABLE LOADER SMOKE ===")
    r = []

    def rec(name, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        r.append(bool(ok))

    t = load_table()
    rec("table loads with rows", len(t["rows"]) > 0)
    rec("absent table -> empty, no raise",
        load_table(path=os.path.join(_HERE, "lm_table_v1.MISSING.json"))
        == {"header": None, "rows": []})
    dell = lookup("dell")
    rec("lookup('dell') returns full set (>=3)",
        len(dell) >= 3)
    rec("lookup unknown -> []", lookup("zzzzqqq") == [])
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
