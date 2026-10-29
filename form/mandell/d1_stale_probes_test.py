#!/usr/bin/env python3
"""D1 canonical probes — the two stale limitation records.

History: circuit 1 reproduced both limitations at eb3389c.
Circuit 3 FIXED the ARGUMENT_LOSS extraction sites (translate
+ phrases re-match argument patterns against the original
text and take case-preserved captures — the add-idea m_orig
precedent, generalized) and this suite became the fix's
proof: the named extraction sites now preserve case, the
guards still hold, and the one residual (english_brain's
canonical rewrites produce lowercased paraphrase text — a
generation layer, not extraction) is pinned as observed so
the record's MITIGATED status stays honest.

The ENGLISH_UNREACHABLE measurements are unchanged from
circuit 1 (the fix touched capture case, not routing).

Run: python3 -m form.mandell.d1_stale_probes_test
"""
from __future__ import annotations

import ast
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.mandell.translate import translate  # noqa: E402
from form.mandell.limitation_knowledge import LIMITATIONS  # noqa: E402

ENG_PROBE_BASE = "eb3389c122f301006b10fa770173ea08c2066d7d"
FIX_PROBE_BASE = "c573b7036082105467128722c668baede2386ff3"

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

    # --- ARGUMENT_LOSS: extraction now preserves case.
    cases = [
        ("copy A", lambda it: it.args.get("source") == "A"),
        ("copy My Field Notes",
         lambda it: it.args.get("source") == "My Field Notes"),
        ("find idea Bright Idea",
         lambda it: "find_idea Bright Idea" in (it.mandel or "")),
        ("trace lineage ABC123",
         lambda it: "trace_lineage ABC123" in (it.mandel or "")),
        ("move Alpha to Beta",
         lambda it: it.args.get("source") == "Alpha"
         and it.args.get("destination") == "Beta"),
        ("delete MyPlan", lambda it: it.args.get("key") == "MyPlan"),
        ("replace OldKey with New Value",
         lambda it: it.args.get("old") == "OldKey"
         and it.args.get("new") == "New Value"),
        ("patch MyKey to NewVal",
         lambda it: it.args.get("key") == "MyKey"
         and it.args.get("value") == "NewVal"),
        ("select Color=Red",
         lambda it: it.args.get("predicate") == "Color=Red"),
        ("search for Golden Gate",
         lambda it: it.args.get("pattern") == "Golden Gate"),
        ("supersede idea OldID with New Words",
         lambda it: "supersede OldID with New Words"
         in (it.mandel or "")),
        ("resolve conflict C9 prefer SideB",
         lambda it: "resolve_conflict C9 prefer SideB"
         in (it.mandel or "")),
        ("outcomes for idea IdeaX",
         lambda it: "outcomes_for_idea IdeaX" in (it.mandel or "")),
        ("create an idea called Test",
         lambda it: it.args.get("label") == "Test"
         and it.args.get("words") == "Test"),
        ("stamp Version One",
         lambda it: it.args.get("mark") == "Version One"),
        ("confirm PID9", lambda it: it.args.get("pid") == "PID9"),
    ]
    bad = [ph for ph, ok_fn in cases if not ok_fn(translate(ph))]
    _rec("argument_loss fixed: extraction preserves case (16 sites)",
         not bad, f"still losing: {bad}")
    n1 = translate("add idea Test")
    _rec("nurture path still preserves case (precedent intact)",
         n1.dell == 37 and n1.args.get("label") == "Test",
         str(n1.args))
    g56 = translate("get My Key")
    _rec("deliberate normalizations kept: store keys + slugs",
         g56.args.get("key") == "my_key"
         and translate("create an idea called Test").args.get("id")
         == "test",
         str(g56.args))
    brain = translate("plant Garden Gate")
    _rec("residual pinned: brain canonical rewrites still lowercase",
         brain.args.get("label") == "garden gate",
         str(brain.args))
    _rec("record: ARGUMENT_LOSS MITIGATED at fix probe base",
         by_id["ARGUMENT_LOSS"]["status"] == "MITIGATED"
         and by_id["ARGUMENT_LOSS"]["last_verified_against"]
         == FIX_PROBE_BASE)

    # --- Guards preserved.
    g1 = translate("delete the plan if empty")
    g2 = translate("don't delete the plan")
    _rec("guards: conditional + negated destructive stay UNKNOWN",
         g1.action == "unknown" and g1.dell is None
         and g2.action == "unknown" and g2.dell is None,
         f"{g1.action}/{g2.action}")
    d1 = translate("delete the plan")
    mv = translate("move forward")
    _rec("guards do not overreach: delete routes, move-forward drives",
         d1.dell == 86 and d1.args.get("key") == "plan"
         and mv.action == "walk" and "19[Drive]" in (mv.mandel or ""),
         f"{d1.dell}/{mv.action}")

    # --- ENGLISH_UNREACHABLE_OPERATION: unchanged measurements.
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
         ["last_verified_against"] == ENG_PROBE_BASE
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
