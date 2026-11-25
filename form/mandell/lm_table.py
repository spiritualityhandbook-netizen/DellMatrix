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

Pair binding (v2; PR #393 atomicity repair, Director mail
1a1cdca2f4dd89fe): the v2 table header carries a "pair" block
binding the exact bytes of the sibling collisions file and the
canonical bytes of the table's rows to a single generation id.
load_table() verifies that binding whenever the loaded table
carries one, and load_collisions() on the default path verifies
through it before returning. ANY mismatch -- mixed publish,
partial publish, tampered member, missing member -- raises
PairInconsistentError: an inconsistent pair is never served.
Absence is a different state and keeps the legacy contract:
a missing table loads as the empty table, without raising. An
inconsistent pair does NOT fall back to v1: v1 is a different,
smaller dataset, and silently serving it would be a silent
downgrade. The recovery is to re-run the build
(form/lm1_import.py), whose publish protocol converges the pair
to one consistent generation. The v1 artifacts carry no pair
block and behave exactly as before; explicit paths are honored
as given.

Read contract under concurrent publication (second repair
cycle, Director mail 1a1cdee092fdf580): every load reads each
artifact's bytes exactly once, verifies the binding against
those snapshots, and parses its return value from the same
snapshots -- no path is opened twice in a load. os.replace is
atomic per file, so a single file's snapshot is always one
whole generation; a publish landing between the two snapshot
reads therefore yields either one consistent generation
(served) or a binding mismatch (PairInconsistentError) --
never a mixed pair, and never bytes other than the ones that
were verified. The first repair's load_collisions() violated
this contract: it verified through load_table() and then
re-opened the collisions file to produce its return value, so
a publish landing between verification and the return read
could hand back an unverified generation. That second read is
gone; T-F in form/lm1_import_test.py pins the interleavings.
"""

from __future__ import annotations

import hashlib
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


class PairInconsistentError(RuntimeError):
    """The v2 table/collisions pair failed its generation
    binding check (mixed, partial, or tampered publish). Raised
    instead of ever serving an inconsistent pair; re-running
    form/lm1_import.py converges the pair."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_rows_bytes(rows) -> bytes:
    return json.dumps(rows, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def _sibling_collisions_path(table_path: str):
    """The collisions file bound to a v2 table path, or None for
    any other artifact name (the binding is defined only for the
    lm_table_v2.json / lm_table_v2.collisions.json pair)."""
    if os.path.basename(table_path) != "lm_table_v2.json":
        return None
    return os.path.join(os.path.dirname(table_path),
                        "lm_table_v2.collisions.json")


def _verify_pair(table_path: str, doc, collisions_bytes) -> None:
    """Fail closed unless collisions_bytes -- the sibling
    collisions bytes read in the SAME load call as the table
    bytes this doc was parsed from -- are exactly the ones this
    table generation binds. No pair block (v1, or an unbound
    artifact) -> nothing to verify, legacy behavior."""
    pair = (doc.get("header") or {}).get("pair")
    if not pair:
        return
    cpath = _sibling_collisions_path(table_path)
    if cpath is None:
        return
    fields = (pair.get("generation"), pair.get("collisions_sha256"),
              pair.get("rows_sha256"))
    if any(not isinstance(v, str) or len(v) != 64
           for v in fields):
        raise PairInconsistentError(
            f"lm_table pair inconsistent: {table_path} carries an "
            "incomplete pair binding; re-run form/lm1_import.py "
            "to converge the pair")
    if collisions_bytes is None:
        raise PairInconsistentError(
            f"lm_table pair inconsistent: {table_path} binds "
            f"collisions file {cpath}, which is missing; re-run "
            "form/lm1_import.py to converge the pair")
    if _sha256_bytes(collisions_bytes) != pair["collisions_sha256"]:
        raise PairInconsistentError(
            f"lm_table pair inconsistent: collisions file "
            f"{cpath} does not match the binding in "
            f"{table_path} (mixed or tampered pair); re-run "
            "form/lm1_import.py to converge the pair")
    rows_sha = _sha256_bytes(
        _canonical_rows_bytes(doc.get("rows", [])))
    if rows_sha != pair["rows_sha256"]:
        raise PairInconsistentError(
            f"lm_table pair inconsistent: rows of {table_path} "
            "do not match their pair binding (tampered table); "
            "re-run form/lm1_import.py to converge the pair")
    generation = _sha256_bytes(
        bytes.fromhex(pair["collisions_sha256"])
        + bytes.fromhex(rows_sha))
    if generation != pair["generation"]:
        raise PairInconsistentError(
            f"lm_table pair inconsistent: generation id in "
            f"{table_path} does not derive from its bound "
            "members; re-run form/lm1_import.py to converge "
            "the pair")


def _default_table_path() -> str:
    """The single read path: v2 when present, v1 fallback."""
    if os.path.exists(V2_TABLE_PATH):
        return V2_TABLE_PATH
    return V1_TABLE_PATH


def _default_collisions_path() -> str:
    if os.path.exists(V2_TABLE_PATH):
        return V2_COLLISIONS_PATH
    return V1_COLLISIONS_PATH


def _load_snapshot(table_path: str):
    """Load a table and its bound collisions file as ONE
    snapshot: each file's bytes are read exactly once, the pair
    binding is verified against those bytes, and both return
    values are parsed from those same bytes -- no path is opened
    twice in a load, so nothing a concurrent publish lands can
    enter a load after its verification.

    Returns (doc, collisions): collisions is the parsed
    collisions list when the table carries a pair binding for a
    sibling file, else None (v1 / unbound artifact -- the legacy
    separate-read behavior of load_collisions applies)."""
    with open(table_path, "rb") as f:
        table_bytes = f.read()
    doc = json.loads(table_bytes.decode("utf-8"))
    pair = (doc.get("header") or {}).get("pair")
    cpath = _sibling_collisions_path(table_path) if pair else None
    if not pair or cpath is None:
        return doc, None
    collisions_bytes = None
    if os.path.exists(cpath):
        with open(cpath, "rb") as f:
            collisions_bytes = f.read()
    _verify_pair(table_path, doc, collisions_bytes)
    # _verify_pair raised if the bound sibling was missing; the
    # bytes verified above are the bytes parsed here.
    return doc, json.loads(collisions_bytes.decode("utf-8"))


def load_table(path: Optional[str] = None) -> Dict[str, Any]:
    """Load the LM table (v2 when present, else v1). Missing file
    -> empty table, no raise: {'header': None, 'rows': []}
    (today's behavior, exactly). A table carrying a pair binding
    (v2) is verified against its sibling collisions file first:
    an inconsistent pair raises PairInconsistentError."""
    p = path or _default_table_path()
    if not os.path.exists(p):
        return {"header": None, "rows": []}
    doc, _collisions = _load_snapshot(p)
    return {"header": doc.get("header"), "rows": doc.get("rows", [])}


def load_collisions(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load the collision log paired with the active table.
    Missing file -> empty list. On the default path with a v2
    table present, table and collisions are read as one verified
    snapshot (see _load_snapshot) and the collisions returned are
    parsed from the very bytes the binding verified: a mixed
    pair raises PairInconsistentError rather than serving the
    collisions of another generation. An explicit path is
    honored as given."""
    if path is not None:
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    if os.path.exists(V2_TABLE_PATH):
        _doc, collisions = _load_snapshot(V2_TABLE_PATH)
        if collisions is not None:
            return collisions
        # A v2-named table with no pair binding is not a shipped
        # state; keep the legacy direct read, as before.
        with open(V2_COLLISIONS_PATH, encoding="utf-8") as f:
            return json.load(f)
    p = _default_collisions_path()
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
