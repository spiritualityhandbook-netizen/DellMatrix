#!/usr/bin/env python3
"""D1 canonical probes — the two stale limitation records,
reproduced at exact current source.

Director completion order: reproduce ARGUMENT_LOSS and
ENGLISH_UNREACHABLE_OPERATION at exact current source; update
status/SHA only after execution; keep signature presence,
English-pattern presence and operational closure as separate
evidence dimensions; preserve the negation / conditional /
destructive guards.

PROBE_BASE is the main commit these probes were executed
against. The limitation records carry the same SHA. If
translate.py changes, the pinned measurements below are
expected to fail loudly — that failure IS the re-verification
trigger, not a nuisance.

Run: python3 -m form.mandell.d1_stale_probes_test
"""
from __future__ import annotations

import ast
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.mandell.translate import translate  # noqa: E402
from form.mandell.limitation_knowledge import LIMITATIONS  # noqa: E402

PROBE_BASE = "eb3389c122f301006b10fa770173ea08c2066d7d"

RESULTS = []


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))


def _intent_dell_set():
    path = os.path.join(os.path.dirname(__file__), "translate.py")
    tree = ast.parse(open(path, encoding="utf-8").read())
    dells = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and getattr(node.func, "id", "") == "Intent"
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)
                and isinstance(node.args[1].value, int)):
            dells.add(node.args[1].value)
    return dells


def main():
    by_id = {e["id"]: e for e in LIMITATIONS}

    # --- ARGUMENT_LOSS: reproduced at the translation boundary.
    # Captures taken from the lowercased working text lose case;
    # the loss is site-specific, not universal (contrast site).
    c1 = translate("copy A")
    c2 = translate("copy My Field Notes")
    _rec("argument_loss: copy argument lowercased",
         c1.dell == 84 and c1.args.get("source") == "a"
         and c2.args.get("source") == "my field notes",
         f"{c1.args} / {c2.args}")
    f1 = translate("find idea Bright Idea")
    t1 = translate("trace lineage ABC123")
    _rec("argument_loss: label-carried arguments lowercased",
         "bright idea" in (f1.mandel or "")
         and "abc123" in (t1.mandel or ""),
         f"{f1.mandel} / {t1.mandel}")
    p1 = translate("create an idea called Test")
    _rec("argument_loss: place path lowercases id/label",
         p1.args.get("id") == "test" and p1.args.get("label") == "test",
         str(p1.args))
    n1 = translate("add idea Test")
    _rec("argument_loss is site-specific: nurture preserves case",
         n1.dell == 37 and n1.args.get("label") == "Test",
         str(n1.args))
    _rec("record: ARGUMENT_LOSS verified at probe base",
         by_id["ARGUMENT_LOSS"]["status"] == "KNOWN"
         and by_id["ARGUMENT_LOSS"]["last_verified_against"]
         == PROBE_BASE)

    # --- Guards preserved (the order's hard requirement).
    g1 = translate("delete the plan if empty")
    g2 = translate("don't delete the plan")
    _rec("guards: conditional + negated destructive stay UNKNOWN",
         g1.action == "unknown" and g1.dell is None
         and g2.action == "unknown" and g2.dell is None,
         f"{g1.action}/{g2.action}")
    d1 = translate("delete the plan")
    _rec("guards do not overreach: plain destructive still routes",
         d1.dell == 86 and d1.args.get("key") == "plan",
         f"{d1.dell} {d1.args}")

    # --- ENGLISH_UNREACHABLE_OPERATION: measured, three tiers.
    routed = _intent_dell_set()
    expected = {4, 5, 6, 8, 9, 10, 11, 12, 13, 15, 19, 25, 27, 28,
                31, 32, 34, 35, 37, 40, 42, 51, 56, 58, 84, 85, 86,
                87, 88}
    _rec("english coverage: translate() names exactly 29 Dells",
         routed == expected,
         f"extra={sorted(routed - expected)} "
         f"missing={sorted(expected - routed)}")
    unrouted = set(range(100)) - routed
    _rec("english coverage: 71 Dells have no translate() Intent path",
         len(unrouted) == 71 and {0, 50, 60, 99} <= unrouted,
         f"count={len(unrouted)}")
    dyn = {84: translate("copy A").dell,
           86: translate("delete the plan").dell,
           87: translate("replace a with b").dell,
           35: translate("count nursery").dell,
           9: translate("show the field").dell,
           37: translate("add idea Test").dell}
    _rec("english coverage: dynamic sample routes as statically read",
         all(dyn[k] == k for k in dyn), str(dyn))
    tier2 = {a: translate(a).action
             for a in ("save", "checkpoint", "grow", "ledger")}
    _rec("english coverage: action tier (dell unnamed) kept separate",
         all(translate(a).dell is None for a in tier2)
         and set(tier2.values()) == {"save", "checkpoint", "grow",
                                     "ledger"},
         str(tier2))
    _rec("record: ENGLISH_UNREACHABLE verified at probe base",
         by_id["ENGLISH_UNREACHABLE_OPERATION"]["status"]
         == "IN_PROGRESS"
         and by_id["ENGLISH_UNREACHABLE_OPERATION"]
         ["last_verified_against"] == PROBE_BASE
         and "29" in by_id["ENGLISH_UNREACHABLE_OPERATION"]
         ["mitigation"])

    ok = sum(1 for _, c, _ in RESULTS if c)
    for name, cond, detail in RESULTS:
        line = ("PASS " if cond else "FAIL ") + name
        if not cond and detail:
            line += " :: " + detail
        print(line)
    print(f"D1_STALE_PROBES: {ok}/{len(RESULTS)}")
    return ok == len(RESULTS) and bool(RESULTS)


def smoke():
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
