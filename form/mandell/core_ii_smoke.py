#!/usr/bin/env python3
"""Core II + chain smoke. Offline. No Form Program required."""
from __future__ import annotations

import inspect

from .registry import get_dell, namespace_of, active_core_count
from .seed import parse_seed
from .manifest_resolver import resolve_manifest
from .core_ii import CORE_II, dvs_floor
from .address_space import RESERVED_DOMAIN, family_of, OLD_TO_NEW
from .core_ii_exec import CoreIIState, execute_core_ii, attach
from .chain_exec import execute_chain
from .executor import execute_seed
from . import executor_leaf


class _P:
    def __init__(self):
        self.core_ii = CoreIIState()
        self.history = []
        self._units = {"alpha": "a", "beta": "b", "nursery_hot": "n"}

    def note_seed(self, n, name, extra=""):
        self.history.append((n, name, extra))


def smoke() -> bool:
    print("=== CORE_II EXEC SMOKE ===")
    r = []

    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}")
        r.append(bool(ok))

    rec("core_ii_count_49", len(CORE_II) == 49)
    rec("registry_51", get_dell(51) and get_dell(51)["name"] == "Select")
    rec("registry_99", get_dell(99) and get_dell(99)["name"] == "Compose")
    rec("ns_core_i", namespace_of(12) == "CORE_I")
    rec("ns_core_ii", namespace_of(76) == "CORE_II")
    rec("ns_addr", namespace_of(560) == "ADDRESS_RESERVED")
    rec("active_100", active_core_count() == 100)
    rec("migrate_51", OLD_TO_NEW.get(51) == 151)
    rec("family_560", family_of(560) == "NATURE_PHYSICS")
    rec("omega_999", 999 in RESERVED_DOMAIN)

    s = parse_seed("51[Select] > 52[Filter] > 66[ForEach] :: nursery")
    rec("parse_chain", s.ok and [a.dell for a in s.atoms] == [51, 52, 66])
    rec("order_preserved", [a.dell for a in s.atoms] == [51, 52, 66])

    s2 = parse_seed("05[Enlighten] :: tone")
    rec("parse_1digit_ok", s2.ok and s2.atoms[0].dell == 5)
    res = resolve_manifest(5, "Enlighten", "tone")
    rec("manifest_fallback_or_family", res.canonical == "Tone")

    s3 = parse_seed("52[Exclude] :: weak")
    rec("filter_manifest", s3.ok and s3.atoms[0].resolved_term in ("Filter", "Exclude"))

    s4 = parse_seed("151[Harmonic]")
    rec("parse_3digit_reserved", s4.ok and s4.atoms[0].dell == 151)

    s5 = parse_seed("200[Nope]")
    rec("unknown_200_rejected", not s5.ok)

    p = _P()
    msgs = []
    execute_core_ii(p, 53, "Scope", "Nursery", msgs)
    execute_core_ii(p, 51, "Select", "nursery", msgs)
    execute_core_ii(p, 70, "Count", "", msgs)
    rec("runtime_scope", p.core_ii.scope == "Nursery")
    rec("runtime_select", len(p.core_ii.selected) >= 1)

    p2 = _P()
    execute_core_ii(p2, 55, "Set", "k=1", [])
    execute_core_ii(p2, 56, "Get", "k", [])
    execute_core_ii(p2, 55, "Set", "k=2", [])
    execute_core_ii(p2, 96, "Revert", "", [])
    rec("set_get_revert", p2.core_ii.store.get("k") == "1")

    p3 = _P()
    execute_core_ii(p3, 82, "Group", "g1", [])
    n1 = len(p3.core_ii.groups.get("g1", []))
    execute_core_ii(p3, 83, "Ungroup", "g1", [])
    rec("group_ungroup", n1 >= 1 and "g1" not in p3.core_ii.groups)

    p4 = _P()
    execute_core_ii(p4, 55, "Set", "x=old", [])
    execute_core_ii(p4, 84, "Copy", "x", [])
    execute_core_ii(p4, 85, "Move", "x>y", [])
    rec("copy_move", "copy_x" in p4.core_ii.store and "y" in p4.core_ii.store and "x" not in p4.core_ii.store)

    p5 = _P()
    execute_core_ii(p5, 93, "Try", "op", [])
    execute_core_ii(p5, 55, "Set", "t=bad", [])
    execute_core_ii(p5, 96, "Revert", "", [])
    rec("try_revert", "t" not in p5.core_ii.store and p5.core_ii.try_depth == 0)

    p6 = _P()
    seed = parse_seed("53[Scope] > 51[Select] > 52[Filter] > 70[Count] :: nursery")
    out = execute_chain(p6, seed, seed.raw)
    rec("chain_ok", out["ok"] and out.get("chain_ran") == [53, 51, 52, 70])
    rec("chain_multi", len(out.get("chain_ran") or []) == 4)

    p7 = _P()
    execute_core_ii(p7, 97, "Define", "Complete=35>18>39>12", [])
    execute_core_ii(p7, 98, "Alias", "Done=Complete", [])
    execute_core_ii(p7, 99, "Compose", "Complete=35>18>39>12", [])
    rec("higher_order", "Complete" in p7.core_ii.defs and "Done" in p7.core_ii.aliases and "Complete" in p7.core_ii.compositions)

    p8 = _P()
    dispatched = execute_seed(p8, "53[Scope] > 51[Select] > 70[Count] :: nursery")
    rec("executor_front_door_chain", dispatched.get("chain_ran") == [53, 51, 70])

    p9 = _P()
    single = execute_seed(p9, "51[Select] :: nursery")
    rec("executor_front_door_single_core_ii", single.get("chain_ran") == [51])

    rec("dvs_formalized", dvs_floor()["core_ii_status"] == "FORMALIZED")

    leaf_src = inspect.getsource(executor_leaf.execute_seed)
    rec("leaf_not_placeholder", "CORE_I_LEAF_NOT_RESTORED" not in leaf_src)
    rec("leaf_has_00", "primary == 0" in leaf_src)
    rec("leaf_has_12", "primary == 12" in leaf_src)
    rec("leaf_has_50", "primary == 50" in leaf_src)
    missing = [n for n in range(0, 51) if f"primary == {n}" not in leaf_src]
    # MPC-011 E: Dell37's dead Stream leaf branch was intentionally removed.
    # Core-I HANDLED authority intercepts those Dells on every production
    # route, so a missing leaf branch is legitimate IFF the Dell is HANDLED.
    # Any missing NON-handled branch is a regression.
    from .core_i_ops import HANDLED as _CORE_I_HANDLED
    rec("leaf_has_00_50_branches", set(missing) <= (set(_CORE_I_HANDLED) & set(range(0, 51))))
    rec("front_door_still_dispatches", "execute_chain" in inspect.getsource(execute_seed))

    print(f"=== {sum(r)}/{len(r)} ===")
    if missing:
        print("missing CORE_I branches:", missing)
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
