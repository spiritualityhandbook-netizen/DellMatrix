#!/usr/bin/env python3
"""Perspective runtime-truth tests (GDP-001 Phase 0, Requirement 5).

Laws under test (docs/RUNTIME_TRUTH_INVARIANTS.md):
  R5-1  No view may report a confident empty over unverified state.
  R5-2  Every reported view carries its epistemic status.
  R5-3  Every computed display value traces to a read of real state.
  R5-4  Status labels are exhaustive: REAL/PARTIAL/UNAVAILABLE/UNKNOWN/UNSUPPORTED.

Runs under form.regress in a private temp copy (fresh form/state).
"""
from __future__ import annotations

import uuid

from form.dell_matrix.perspective_views import (
    EPISTEMIC_STATUSES,
    REAL, PARTIAL, UNAVAILABLE, UNKNOWN, UNSUPPORTED,
    PerspectiveRegistry,
    Viewer,
    _probe_nodes,
    bootstrap_default_viewers,
    see_as,
    see_first,
    see_third,
    see_parts,
    see_whole,
)


def _real_path_program(units):
    """Synthetic program shaped like the canonical real path:
    program.cube.session.plane.units (id -> node)."""
    class P:
        pass
    p = P()
    plane = type("Plane", (), {"units": dict(units)})()
    session = type("Session", (), {"plane": plane})()
    p.cube = type("Cube", (), {"session": session})()
    return p


def _legacy_plane_program(nodes):
    class FakePlane:
        def all_nodes(self):
            return list(nodes)
    class P:
        plane = FakePlane()
    return P()


def _blind_program():
    class P:
        pass
    return P()


def smoke() -> bool:
    print("=== PERSPECTIVE RUNTIME TRUTH ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(bool(ok))

    # 1. Canonical real path -> REAL with correct inventory.
    units = {
        "a": {"id": "a", "label": "Alpha", "x": 1.0, "y": 2.0, "skin": "cube"},
        "b": {"id": "b", "label": "Beta", "x": -1.0, "y": 0.5, "skin": "sphere"},
    }
    rp = _real_path_program(units)
    nodes, src, status = _probe_nodes(rp)
    rec("real_probe_status", status == REAL and src == "program.cube.session.plane.units")
    rec("real_probe_nodes", len(nodes) == 2 and {n["id"] for n in nodes} == {"a", "b"})
    reg = bootstrap_default_viewers(rp)
    w = see_as(rp, reg.viewers["architect"], "whole")
    rec("real_whole", w.get("ok") is True and w.get("count") == 2
        and w.get("epistemic_status") == REAL)
    rec("real_whole_labels", [n["label"] for n in w["nodes"]] == ["Alpha", "Beta"])
    t = see_as(rp, reg.viewers["user"], "third")
    rec("real_third", t.get("epistemic_status") == REAL and t.get("count") == 2)
    pa = see_as(rp, reg.viewers["user"], "parts")
    rec("real_parts", pa.get("epistemic_status") == REAL and "count" in pa)
    f = see_as(rp, reg.viewers["user"], "first")
    rec("real_first", f.get("epistemic_status") == REAL and "vision" in f)

    # 2. Legacy adapter path -> PARTIAL (honest about being non-canonical).
    lp = _legacy_plane_program([
        {"id": "x", "label": "X", "x": 0, "y": 0, "skin": "core"},
    ])
    lnodes, lsrc, lstatus = _probe_nodes(lp)
    rec("legacy_probe", lstatus == PARTIAL and len(lnodes) == 1)
    lw = see_whole(lp, Viewer(id="v", role="architect", mode="whole"))
    rec("legacy_whole_partial", lw.get("epistemic_status") == PARTIAL
        and lw.get("count") == 1)

    # 3. Blind program -> UNKNOWN, NEVER a confident zero (all four modes).
    bp = _blind_program()
    bnodes, bsrc, bstatus = _probe_nodes(bp)
    rec("blind_probe", bstatus == UNKNOWN and bnodes == [])
    bv = Viewer(id="v", role="architect", mode="whole")
    for fn, name in ((see_whole, "whole"), (see_third, "third"),
                     (see_parts, "parts"), (see_first, "first")):
        out = fn(bp, bv)
        text = " ".join(out.get("report") or [])
        rec(f"blind_{name}_honest",
            out.get("epistemic_status") == UNKNOWN
            and "count" not in out
            and "0 nodes" not in text
            and "cannot verify" in text)

    # 4. Unreadable source -> UNAVAILABLE (plane present, units not a dict).
    class BadPlane:
        units = None
    class BadProg:
        cube = type("C", (), {"session": type("S", (), {"plane": BadPlane()})()})()
    _, _, ustatus = _probe_nodes(BadProg())
    rec("unavailable_probe", ustatus == UNAVAILABLE)
    uw = see_whole(BadProg(), bv)
    rec("unavailable_no_count", uw.get("epistemic_status") == UNAVAILABLE
        and "count" not in uw)

    # 5. Error paths carry UNSUPPORTED / UNKNOWN.
    bad_mode = see_as(rp, bv, "nope")
    rec("bad_mode_unsupported", bad_mode.get("epistemic_status") == UNSUPPORTED
        and bad_mode.get("ok") is False)
    sm = reg.set_mode("ghost", "whole", as_role="user")
    rec("unknown_viewer", sm.get("epistemic_status") == UNKNOWN)
    sm2 = reg.set_mode("user", "nope", as_role="user")
    rec("unknown_mode_set", sm2.get("epistemic_status") == UNSUPPORTED)

    # 6. Status labels are exhaustive: every view output carries a known label.
    for out in (w, t, pa, f, lw):
        rec("label_exhaustive", out.get("epistemic_status") in EPISTEMIC_STATUSES
            and isinstance(out.get("data_source"), str))

    # 7. Real Program integration: actual open_program + place() must be VISIBLE.
    #    (regress runs in a private temp copy with fresh form/state.)
    from form.open import open_program
    owner = "R5TruthTest_" + uuid.uuid4().hex[:8]
    prog = open_program(owner)
    prog.place("t1", "TruthOne", words="one", x=3.0, y=3.0)
    prog.place("t2", "TruthTwo", words="two", x=-2.0, y=1.0)
    real_units = prog.cube.session.plane.units
    reg2 = bootstrap_default_viewers(prog)
    iw = see_as(prog, reg2.viewers["architect"], "whole")
    rec("real_program_visible",
        iw.get("epistemic_status") == REAL
        and iw.get("count") == len(real_units) >= 2
        and {"TruthOne", "TruthTwo"} <= {n["label"] for n in iw["nodes"]})
    it = see_as(prog, reg2.viewers["user"], "third")
    rec("real_program_third", it.get("epistemic_status") == REAL)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
