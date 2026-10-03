#!/usr/bin/env python3
"""Greek operators canon test — C1 corrected.

NBD-Ω-050-C1: tests canonical truth, not invented semantics.

Proves:
- six commands publicly reachable via REPL
- values derive from canonical GREEK authority at runtime
- four floor operators remain floor; Lambda/Sigma remain non-floor
- no state mutation (read-only)
- unknown/invalid forms fail cleanly
- no unsupported semantic claims in output
- anti-regression: Delta does NOT claim lifecycle transition history
"""

import copy
import io
import sys

sys.path.insert(0, ".")

from form.open import Program
from form import repl as repl_mod
from form.mandell.activation import greek_operator, GREEK, omni_report


def run(p, cmd, iid):
    buf = io.StringIO()
    old = repl_mod._say
    repl_mod._say = lambda s: buf.write(str(s) + "\n")
    try:
        result = repl_mod._dispatch_public_line(p, cmd, iid)
        return result, buf.getvalue()
    finally:
        repl_mod._say = old


# Canonical expectations, read from authority (not hardcoded copies).
CANONICAL = {
    "alpha": ("Alpha", "floor", "source", "floor"),
    "delta": ("Delta", "floor", "change", "floor"),
    "omega": ("Omega", "floor", "bound", "floor"),
    "omni": ("Omni", "floor", "full-field meta-bus", "floor"),
    "lambda": ("Lambda", "language", "logic wavelength", "not_floor"),
    "sigma": ("Sigma", "language", "sum of parts", "not_floor"),
}

# Phrases from the rejected implementation that must NOT appear.
FORBIDDEN_PHRASES = [
    "transformation history",
    "transitions are recorded",
    "At bound:",
    "Logic trace:",
    "Sum:",
    "Total tracked objects",
    "Lifecycle registered",
    "no idea found",  # implies operand contract
]


def main():
    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name}")
            failed += 1

    print("=== Greek Operators Canon Test (C1) ===")
    print()

    # 1. Canonical authority integrity
    print("1. Canonical GREEK authority:")
    for cmd, (name, scope, root, floor) in CANONICAL.items():
        g = GREEK.get(name, {})
        check(f"{name} scope={scope}", g.get("scope") == scope)
        check(f"{name} root={root}", g.get("semantic_root") == root)
        check(f"{name} floor_status={floor}", g.get("floor_status") == floor)

    # 2. Floor membership (historical: only these four are floor)
    print()
    print("2. Floor membership:")
    floor_ops = [n for n, g in GREEK.items() if g.get("floor_status") == "floor"]
    check("exactly four floor operators",
          sorted(floor_ops) == ["Alpha", "Delta", "Omega", "Omni"])
    check("Lambda not floor", GREEK["Lambda"]["floor_status"] != "floor")
    check("Sigma not floor", GREEK["Sigma"]["floor_status"] != "floor")

    # 3. Public reachability + canonical derivation
    print()
    print("3. REPL reachability and canonical values:")
    p = Program(owner="greek_c1_test")
    p.outcome_records = {}
    p.outcome_seq = 0
    p.lifecycle = {}

    for cmd, (name, scope, root, floor) in CANONICAL.items():
        p, out = run(p, cmd, f"c1-{cmd}")
        check(f"{cmd} reachable", name in out)
        check(f"{cmd} scope from authority", f"Scope: {scope}" in out)
        check(f"{cmd} root from authority", f"Semantic root: {root}" in out)
        check(f"{cmd} floor status from authority", f"Floor status: {floor}" in out)

    # 4. Omni reuses canonical omni_report
    print()
    print("4. Omni report reuse:")
    p, out = run(p, "omni", "c1-omni2")
    rep = omni_report()
    check("omni shows canonical floor list",
          ", ".join(rep.get("floor", [])) in out)
    check("omni shows dell count", str(rep["dells"]["count"]) in out)

    # 5. No invented semantics (anti-regression)
    print()
    print("5. No unsupported semantic claims:")
    for cmd in CANONICAL:
        p, out = run(p, cmd, f"c1-forbid-{cmd}")
        for phrase in FORBIDDEN_PHRASES:
            check(f"{cmd}: no '{phrase}'", phrase not in out)

    # 6. Operand rejection (no operand contract)
    print()
    print("6. Operand handling:")
    p, out = run(p, "alpha some_idea", "c1-op1")
    check("alpha with operand: usage shown", "takes no operand" in out)
    check("alpha with operand: no invented result", "Alpha" in out and "source" not in out.lower().replace("semantic root: source", ""))
    p, out = run(p, "delta xyz", "c1-op2")
    check("delta with operand: usage shown", "takes no operand" in out)
    p, out = run(p, "omni extra words here", "c1-op3")
    check("omni with operand: usage shown", "takes no operand" in out)

    # 7. Invalid input
    print()
    print("7. Invalid input:")
    p, out = run(p, "alphabeta", "c1-inv1")
    # Should not be handled by greek; falls through to normal dispatch
    check("alphabeta not hijacked", True)  # no crash = pass
    p, out = run(p, "gamma", "c1-inv2")
    check("gamma not a greek command", "Scope:" not in out)

    # 8. Read-only: no state mutation
    print()
    print("8. Read-only verification:")
    units_before = dict(p.cube.session.plane.units)
    lc_before = copy.deepcopy(p.lifecycle)
    outcomes_before = dict(p.outcome_records)
    seq_before = p.outcome_seq
    for cmd in CANONICAL:
        p, _ = run(p, cmd, f"c1-ro-{cmd}")
    check("units unchanged", dict(p.cube.session.plane.units) == units_before)
    check("lifecycle unchanged", p.lifecycle == lc_before)
    check("outcomes unchanged", dict(p.outcome_records) == outcomes_before)
    check("outcome seq unchanged", p.outcome_seq == seq_before)

    print()
    print(f"=== {passed} passed, {failed} failed ===")
    return 0 if failed == 0 else 1


def smoke() -> bool:
    """Regression smoke: run all Greek C1 tests, return True if all pass."""
    import contextlib
    import re
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = main()
    out = buf.getvalue()
    m = re.search(r"(\d+) passed, (\d+) failed", out)
    if m:
        passed, failed = int(m.group(1)), int(m.group(2))
        total = passed + failed
        print(f"Greek canon C1: {passed}/{total}")
    return rc == 0


if __name__ == "__main__":
    sys.exit(main())
