#!/usr/bin/env python3
"""LM-1 table — additive, read-only loader.

History: the v1 table (lm_table_v1.json, built by form/lm1_harvest.py
from in-repo sources only) was authorized by Director mail
1a1cc55119b5979f (2026-11-11) as the ONE bounded in-repo
HARVEST-ONLY LM-1 build, with the external roots table held under
Q-LM1.1. The v2 table (lm_table_v2.json, built by form/lm1_import.py)
adds the external stratum under Ace's license ruling of 2026-11-11
(PR #390), the Director-reviewed boundary (PR #391) and execution
design (PR #392), and Director GO mail 1a1cd7d53c3ec395.

Read path (ONE path, v2 supersedes v1): with no explicit path,
load_table() reads lm_table_v2.json when it is present and falls
back to lm_table_v1.json when v2 is absent — in which case behavior
is exactly the pre-import behavior. load_collisions() follows the
same pairing. An explicit path is always honored as given.

- If the resolved table file is ABSENT, load_table() returns an
  empty table and every consumer behaves exactly as today. No
  existing module depends on this loader; nothing is wired into
  translate.py, the executor, or the REPL (that wiring is LM-4's
  circuit, not LM-1).
- latinmandell.py / morpheme.py behavior is untouched: their dicts,
  first-match rules, and customs handling are exactly as before.

Precedence (annotation only -- this loader changes no runtime
resolution): customs > ace_seed > inrepo > inrepo_force >
inrepo_legacy > candidate > external_wikipedia. Customs are
runtime state (persist v7) and are never in the shipped table; a
bound custom outranks every shipped stratum, exactly as root_of()
already behaves. The external stratum is the LOWEST shipped
stratum and never wins a lookup.

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
V1_TABLE_PATH = os.path.join(_HERE, "lm_table_v1.json")
V2_TABLE_PATH = os.path.join(_HERE, "lm_table_v2.json")
V1_COLLISIONS_PATH = os.path.join(_HERE,
                                  "lm_table_v1.collisions.json")
V2_COLLISIONS_PATH = os.path.join(_HERE,
                                  "lm_table_v2.collisions.json")
DEFAULT_TABLE_PATH = V1_TABLE_PATH
DEFAULT_COLLISIONS_PATH = V1_COLLISIONS_PATH

PRECEDENCE = ["customs", "ace_seed", "inrepo", "inrepo_force",
              "inrepo_legacy", "candidate", "external_wikipedia"]
_RANK = {name: i for i, name in enumerate(PRECEDENCE)}


def _norm(piece: str) -> str:
    return (piece or "").strip().strip("-").lower()


def _default_table_path() -> str:
    """The single read path: v2 when present, v1 fallback."""
    if os.path.exists(V2_TABLE_PATH):
        return V2_TABLE_PATH
    return V1_TABLE_PATH


def _default_collisions_path() -> str:
    if os.path.exists(V2_TABLE_PATH):
        return V2_COLLISIONS_PATH
    return V1_COLLISIONS_PATH


def load_table(path: Optional[str] = None) -> Dict[str, Any]:
    """Load the LM table (v2 when present, else v1). Missing file
    -> empty table, no raise: {'header': None, 'rows': []}
    (today's behavior, exactly)."""
    p = path or _default_table_path()
    if not os.path.exists(p):
        return {"header": None, "rows": []}
    with open(p, encoding="utf-8") as f:
        doc = json.load(f)
    return {"header": doc.get("header"), "rows": doc.get("rows", [])}


def load_collisions(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load the collision log paired with the active table.
    Missing file -> empty list."""
    p = path or _default_collisions_path()
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
