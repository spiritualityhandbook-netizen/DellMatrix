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
import re
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

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"V08 TRUTH COUNTS: {passed}/{len(RESULTS)} PASS")
    return all(ok for _, ok in RESULTS)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
