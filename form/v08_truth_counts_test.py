"""V-08 bounded truth-in-counts fixes (Director 7095187541).

Two presentation lies, both verified at main 88659c49:
1. The live payload ships nursery[:20] with no total, and the client
   foot/status lines print the SHOWN count (<=20) as the nursery count.
2. The server caps Plane edges at 480 and discloses edges_total /
   edges_shown, then the client silently draws only slice(0, 400),
   so the disclosed shown number is not what is drawn.

Contract: every count a view prints is the count it means — shown and
total travel together, and the drawing renders exactly the edges the
server sent and disclosed.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

from form.open import open_program
from form.dell_matrix import live_visual

RESULTS = []


def rec(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
    RESULTS.append((name, bool(ok)))


def _payload_with(n):
    p = open_program("V08TruthCounts")
    props = [{"id": f"prop-{i}", "label": f"Proposal {i}"} for i in range(n)]
    p.ranked_proposals = lambda: props  # instance stub: count contract only
    return live_visual._state_payload(p)


def smoke() -> bool:
    RESULTS.clear()
    pay = _payload_with(25)
    rec("payload discloses nursery_total == 25 when 25 proposals exist",
        pay.get("nursery_total") == 25, f"got {pay.get('nursery_total')!r}")
    rec("payload discloses nursery_shown == 20 (the shipped slice)",
        pay.get("nursery_shown") == 20 and len(pay.get("nursery") or []) == 20,
        f"got shown={pay.get('nursery_shown')!r} len={len(pay.get('nursery') or [])}")
    pay3 = _payload_with(3)
    rec("payload under the cap: total == shown == 3, nothing invented",
        pay3.get("nursery_total") == 3 and pay3.get("nursery_shown") == 3
        and len(pay3.get("nursery") or []) == 3)
    rec("edge disclosure consistent: edges_shown == len(edges) <= edges_total",
        pay.get("edges_shown") == len(pay.get("edges") or [])
        and (pay.get("edges_total") or 0) >= (pay.get("edges_shown") or 0))

    core = Path("form/dell_matrix/assets/js/core.js").read_text()
    rec("client draws exactly the edges the server sent (no silent slice(0, 400))",
        "edges.slice(0, 400)" not in core and "edges.slice(0,400)" not in core)
    rec("client foot/status lines use the disclosed nursery_total when present",
        "nursery_total" in core)
    rec("client no longer prints the shown slice length as the nursery count",
        "(s.nursery || []).length" not in core)

    # --- Graph-render proof (Director challenge 7097430407) ---
    # edges_shown must equal the number of edges the renderer can
    # actually draw: an edge draws only when BOTH endpoints resolve in
    # the shipped node set (core.js drawLatticeMap byId lookup).
    def _drawn(pay):
        ids = {str(n.get("id")) for n in (pay.get("nodes") or [])}
        d = 0
        for e in (pay.get("edges") or []):
            a = str(e.get("a") or e.get("source") or e.get("from"))
            b = str(e.get("b") or e.get("target") or e.get("to"))
            if a in ids and b in ids:
                d += 1
        return d

    # Real graph with boxed units: build_view emits sandbox-kind edges
    # whose target is a sandbox id — never a shipped node.
    gp = open_program("V08TruthCountsGraph")
    gpl = gp.cube.session.plane
    for i in range(5):
        gpl.place(f"v08g-{i}", f"V08 graph {i}", x=float(i * 10), y=0.0)
    gpl.box(["v08g-3", "v08g-4"], "v08box")
    from form.dell_matrix.graph_view import build_view as _bv
    raw_kinds = [e.kind for e in _bv(gpl).edges]
    gpay = live_visual._state_payload(gp)
    rec("real graph fixture actually contains sandbox-kind edges upstream",
        "sandbox" in raw_kinds, f"kinds={sorted(set(raw_kinds))}")
    rec("every shipped edge resolves in the shipped node set (drawn == shown)",
        _drawn(gpay) == gpay.get("edges_shown") == len(gpay.get("edges") or []),
        f"drawn={_drawn(gpay)} shown={gpay.get('edges_shown')} len={len(gpay.get('edges') or [])}")
    rec("unresolvable shipped-edge exclusions are disclosed, not silent",
        (gpay.get("edges_unresolvable") or 0) >= 1
        and (gpay.get("edges_total") or 0)
        == (gpay.get("edges_unresolvable") or 0)
        + len([e for e in _bv(gpl).edges
               if str(e.source) in {str(n.get('id')) for n in gpay['nodes']}
               and str(e.target) in {str(n.get('id')) for n in gpay['nodes']}]),
        f"unresolvable={gpay.get('edges_unresolvable')!r} total={gpay.get('edges_total')!r}")

    # Negative dangling-endpoint case + cap boundary fixtures, via a
    # stubbed view (build_view is imported at call time in _state_payload).
    import form.dell_matrix.graph_view as _gv

    class _StubView:
        def __init__(self, edges):
            self.edges = edges

    def _stub_payload(n_edges, dangling=0):
        edges = []
        for i in range(n_edges):
            edges.append(_gv.ViewEdge(source="v08g-0", target="v08g-1", kind="enhance"))
        for i in range(dangling):
            edges.append(_gv.ViewEdge(source="v08g-0", target="no-such-node", kind="enhance"))
        orig = _gv.build_view
        _gv.build_view = lambda plane, scores=None: _StubView(edges)
        try:
            return live_visual._state_payload(gp)
        finally:
            _gv.build_view = orig

    dp = _stub_payload(10, dangling=2)
    rec("dangling-endpoint edges are excluded from the shipped list and disclosed",
        len(dp.get("edges") or []) == 10 and dp.get("edges_shown") == 10
        and dp.get("edges_unresolvable") == 2 and _drawn(dp) == 10,
        f"len={len(dp.get('edges') or [])} shown={dp.get('edges_shown')} "
        f"unresolvable={dp.get('edges_unresolvable')!r} drawn={_drawn(dp)}")
    for n in (400, 401, 480, 481):
        bp = _stub_payload(n)
        rec(f"cap boundary {n}: shipped == min(n, 480), all drawn, total honest",
            len(bp.get("edges") or []) == min(n, 480)
            and bp.get("edges_shown") == min(n, 480)
            and bp.get("edges_total") == n
            and _drawn(bp) == min(n, 480),
            f"n={n} len={len(bp.get('edges') or [])} shown={bp.get('edges_shown')} "
            f"total={bp.get('edges_total')} drawn={_drawn(bp)}")

    # --- Nursery counts against real payloads, footer text executed ---
    node_bin = shutil.which("node")
    rec("node available to exercise the client footer text", node_bin is not None)
    if node_bin:
        m = re.search(r"function nurseryCountText\(s\) \{.*?\n  \}", core, re.S)
        cases = []
        for n, want in ((0, "0"), (20, "20"), (21, "20/21")):
            pay_n = _payload_with(n)
            cases.append({"nursery": pay_n.get("nursery"),
                          "nursery_total": pay_n.get("nursery_total"),
                          "want": want, "n": n})
        driver = (
            m.group(0)
            + "\nconst cases = JSON.parse(process.argv[1]);"
            + "\nlet bad = 0;"
            + "\nfor (const c of cases) { const got = nurseryCountText(c);"
            + " if (got !== c.want) { bad++; console.log('MISMATCH n=' + c.n + ' got=' + got + ' want=' + c.want); } }"
            + "\nprocess.exit(bad ? 1 : 0);"
        )
        r = subprocess.run([node_bin, "-e", driver, json.dumps(cases)],
                           capture_output=True, text=True, timeout=60)
        rec("footer nursery text vs real payloads: empty=0, 20=20, 21=20/21",
            r.returncode == 0, (r.stdout + r.stderr).strip()[:200])

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"V08 TRUTH COUNTS: {passed}/{len(RESULTS)} PASS")
    return all(ok for _, ok in RESULTS)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
