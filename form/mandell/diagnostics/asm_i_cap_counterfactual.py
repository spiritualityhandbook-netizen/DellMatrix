#!/usr/bin/env python3
"""ASM-I/AEC-I: Adaptive Selection Measurement — cap counterfactual diagnostic.

Measures the effect of learned-score bounding on selection ordering
WITHOUT changing production code or persisting any learning.

ASM-I: measured ASI_LEARNED_CAP values via monkey-patch.
AEC-I: compares old hard clamp vs new monotonic saturation.

Method: monkey-patch duobeta_learn transform per evaluation,
run select_for_context, record ordering. Restore after each run.

NO production change. NO learning persisted. NO state mutation.
"""

import sys
import time
from typing import Any, Dict, List

CAPS = [1, 3, 5, 8, 10, None]  # None = uncapped


def _make_program() -> Any:
    from form.open import Program
    return Program()


def _add_knowledge(p: Any, kid: str, label: str, detail: str = "") -> None:
    prop = type("obj", (), {"status": "confirmed", "label": label, "id": kid})()
    p.nursery.proposals[kid] = prop
    unit = type("obj", (), {"label": label, "detail": detail,
                           "words": (label + " " + detail).lower()})()
    p.cube.session.plane.units[kid] = unit


def _apply_learning(p: Any, dell: int, kid: str, success: int = 0,
                    failure: int = 0, blocked: int = 0) -> None:
    """Inject learning entries via structured ledger (test setup only).
    Uses _append_learn_entry with APPLIED status. No duo.evolve."""
    from form.mandell import duobeta_learn as dl
    def _add(kind, proposal_kind, n):
        if n <= 0:
            return
        dl._append_learn_entry(
            p, f"LEARN APPLIED {kind} (asm-i measurement)",
            {"kind": "learn", "proposal_kind": proposal_kind, "dell": dell,
             "knowledge_id": kid, "status": "APPLIED",
             "evidence": {"supporting": [f"t{i}" for i in range(n)]},
             "gate": {"accepted": True}, "reason": "asm-i",
             "proposed_ts": "t", "applied_ts": "t"})
    _add("preference", "preference", success)
    _add("avoidance", "avoidance", failure)
    _add("blocked", "blocked_association", blocked)


def measure_scenario(name: str, setup_fn, context: str = "test context",
                     explicit_ids: List[str] = None) -> Dict[str, Any]:
    """Run one scenario across all cap values. Returns per-cap results."""
    import form.mandell.duobeta_learn as dl
    from form.mandell.knowledge_selector import select_for_context

    original_cap = dl.ASI_LEARNED_CAP
    results = {"scenario": name, "caps": {}}

    try:
        for cap in CAPS:
            # Set cap (None = uncapped = very large)
            dl.ASI_LEARNED_CAP = 10**9 if cap is None else cap

            # Fresh program per cap (isolation)
            p = _make_program()
            setup_fn(p)

            t0 = time.perf_counter()
            r = select_for_context(p, context, explicit_ids=explicit_ids)
            dt = time.perf_counter() - t0

            selected = [s["id"] for s in r["selected"]]
            learned_scores = r.get("learned_scores", {})

            results["caps"][str(cap)] = {
                "selected": selected,
                "learned_scores": dict(learned_scores),
                "explicit_choice": r.get("explicit_choice"),
                "runtime_ms": round(dt * 1000, 3),
                "eligible_count": r.get("eligible_count"),
            }
    finally:
        dl.ASI_LEARNED_CAP = original_cap  # Restore

    return results


def analyze_suppression(results: Dict[str, Any]) -> Dict[str, Any]:
    """Detect if cap=5 suppresses ordering vs uncapped."""
    caps = results["caps"]
    baseline = caps["None"]["selected"]  # uncapped = ground truth ordering
    cap5 = caps["5"]["selected"]

    suppressed = baseline != cap5
    return {
        "uncapped_order": baseline,
        "cap5_order": cap5,
        "suppressed": suppressed,
        "suppressed_ids": [i for i in baseline if i not in cap5] if suppressed else [],
        "reordered": baseline != cap5 and set(baseline) == set(cap5),
    }


# ── Scenario definitions ──────────────────────────────────────────

def setup_cold_start(p):
    for i in range(8):
        _add_knowledge(p, f"k{i}", f"Knowledge Item {i}", "test context data")


def setup_small_set(p):
    for i in range(3):
        _add_knowledge(p, f"k{i}", f"Item {i}", "test context")


def setup_exactly_five(p):
    for i in range(5):
        _add_knowledge(p, f"k{i}", f"Item {i}", "test context")


def setup_large_set(p):
    for i in range(20):
        _add_knowledge(p, f"k{i}", f"Item {i} with test context words")


def setup_strong_preference_inside(p):
    # Strong preference (10 successes) for k1, moderate for others
    for i in range(8):
        _add_knowledge(p, f"k{i}", f"Item {i}", "test context")
    _apply_learning(p, 37, "k1", success=10)
    _apply_learning(p, 37, "k2", success=3)
    _apply_learning(p, 37, "k3", success=2)


def setup_strong_preference_outside(p):
    # k7 has 10 successes but low relevance (may be outside top selection)
    for i in range(8):
        _add_knowledge(p, f"k{i}", f"Item {i}", "test context alpha")
    _add_knowledge(p, "k7", "Item 7", "completely different zebra words")
    _apply_learning(p, 37, "k7", success=10)
    _apply_learning(p, 37, "k1", success=2)


def setup_runaway(p):
    # Extreme reinforcement: 50 successes for k1
    for i in range(8):
        _add_knowledge(p, f"k{i}", f"Item {i}", "test context")
    _apply_learning(p, 37, "k1", success=50)
    _apply_learning(p, 37, "k2", success=6)
    _apply_learning(p, 37, "k3", success=5)


def setup_tie_at_cap(p):
    # Two items that would tie at cap=5 but differ uncapped
    for i in range(5):
        _add_knowledge(p, f"k{i}", f"Item {i}", "test context")
    _apply_learning(p, 37, "k1", success=10)  # raw 10, capped to 5
    _apply_learning(p, 37, "k2", success=6)   # raw 6, capped to 5


def setup_ekc_with_preference(p):
    for i in range(8):
        _add_knowledge(p, f"k{i}", f"Item {i}", "test context")
    _apply_learning(p, 37, "k5", success=8)
    _apply_learning(p, 37, "k6", success=7)


SCENARIOS = [
    ("cold_start", setup_cold_start, "test context", None),
    ("small_set", setup_small_set, "test context", None),
    ("exactly_five", setup_exactly_five, "test context", None),
    ("large_set", setup_large_set, "test context words", None),
    ("strong_preference_inside", setup_strong_preference_inside, "test context", None),
    ("strong_preference_outside", setup_strong_preference_outside, "test context alpha", None),
    ("runaway", setup_runaway, "test context", None),
    ("tie_at_cap", setup_tie_at_cap, "test context", None),
    ("ekc_with_preference", setup_ekc_with_preference, "test context", ["k0"]),
]


def main():
    all_results = []
    for name, setup, ctx, explicit in SCENARIOS:
        r = measure_scenario(name, setup, ctx, explicit)
        r["suppression"] = analyze_suppression(r)
        all_results.append(r)

    # Summary
    print("=" * 70)
    print("ASM-I COUNTERFACTUAL MEASUREMENT SUMMARY")
    print("=" * 70)
    for r in all_results:
        s = r["suppression"]
        print(f"\nScenario: {r['scenario']}")
        print(f"  Uncapped order: {s['uncapped_order']}")
        print(f"  Cap-5 order:    {s['cap5_order']}")
        print(f"  Suppressed: {s['suppressed']}")
        if s["reordered"]:
            print(f"  (Reordering only, same set)")
        if s["suppressed_ids"]:
            print(f"  Suppressed IDs: {s['suppressed_ids']}")

    # Cap sweep detail for tie_at_cap
    print("\n" + "=" * 70)
    print("TIE_AT_CAP: Score values across caps")
    print("=" * 70)
    for r in all_results:
        if r["scenario"] == "tie_at_cap":
            for cap, data in r["caps"].items():
                print(f"  cap={cap}: scores={data['learned_scores']}, "
                      f"order={data['selected']}")

    return all_results


if __name__ == "__main__":
    main()


# ── AEC-I: old vs new comparison ──────────────────────────────────
def compare_old_vs_new():
    """Demonstrate elimination of the ASM-I suppression case.

    BEFORE (hard clamp at 5): raw 6/10 → 5/5 → false tie
    AFTER (saturation): raw 6/10 → 5.66/9.09 → distinct, correct order
    """
    import form.mandell.duobeta_learn as dl
    from form.mandell.knowledge_selector import select_for_context
    from form.open import Program

    def setup(p):
        for kid in ["k0", "k1"]:
            prop = type("obj", (), {"status": "confirmed", "label": "Item alpha", "id": kid})()
            p.nursery.proposals[kid] = prop
            unit = type("obj", (), {"label": "Item alpha", "detail": "beta",
                                   "words": "item alpha beta"})()
            p.cube.session.plane.units[kid] = unit
        for kid, n in [("k0", 6), ("k1", 10)]:
            dl._append_learn_entry(p, "test",
                {"kind": "learn", "proposal_kind": "preference", "dell": 37,
                 "knowledge_id": kid, "status": "APPLIED",
                 "evidence": {"supporting": [f"t{j}" for j in range(n)]},
                 "gate": {"accepted": True}, "reason": "t",
                 "proposed_ts": "t", "applied_ts": "t"})

    # OLD: hard clamp
    orig_sat = dl.saturate_learned_score
    dl.saturate_learned_score = lambda raw: max(-5, min(5, raw))
    p = Program()
    setup(p)
    r = select_for_context(p, "alpha")
    old_scores = dict(r["learned_scores"])
    old_order = [s["id"] for s in r["selected"]]

    # NEW: saturation (restore)
    dl.saturate_learned_score = orig_sat
    p = Program()
    setup(p)
    r = select_for_context(p, "alpha")
    new_scores = dict(r["learned_scores"])
    new_order = [s["id"] for s in r["selected"]]

    print("=" * 60)
    print("AEC-I: OLD (hard clamp) vs NEW (saturation)")
    print("=" * 60)
    print(f"Raw evidence: k0=6, k1=10")
    print(f"OLD scores: k0={old_scores.get('k0')}, k1={old_scores.get('k1')}")
    print(f"OLD order: {old_order} (false tie: {old_scores.get('k0') == old_scores.get('k1')})")
    print(f"NEW scores: k0={new_scores.get('k0'):.4f}, k1={new_scores.get('k1'):.4f}")
    print(f"NEW order: {new_order} (distinct: {new_scores.get('k0') != new_scores.get('k1')})")
    print(f"Suppression eliminated: {new_order[0] == 'k1'}")


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "--compare":
    compare_old_vs_new()
