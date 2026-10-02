#!/usr/bin/env python3
"""IRR-I: history find — deterministic literal search tests.

Verifies display-only recall: no execution, no mutation, no new persistence.
"""
import io
import sys

sys.path.insert(0, ".")

CHECKS = []

def check(name, ok):
    CHECKS.append((name, bool(ok)))
    if not ok:
        print(f"FAIL: {name}")

def _repl_history_find(cmds, history=None):
    """Drive actual production _execute_intent for history find, capture output.
    
    DIVG-I hardening: previously simulated the dispatch branch; now exercises
    the real production code path via _execute_intent with _normalized=True.
    """
    from form import repl as repl_mod
    from form.open import Program
    from form.mandell.translate import Intent
    p = Program(owner="irr-i-test")
    # Seed history directly (simulates prior commands)
    p.history = history if history is not None else [
        "08[Create] :: alpha test", "09[Show] :: look", "08[Create] :: beta test"]
    buf = io.StringIO()
    old_say = repl_mod._say
    repl_mod._say = lambda s: buf.write(str(s) + "\n")
    try:
        for cmd in cmds:
            # Drive the REAL production branch via _execute_intent.
            # _normalized=True skips English rerouting; history branch uses raw_line.
            dummy_intent = Intent(action="unknown", dell=None, term="", args={},
                                mandel="", english="")
            repl_mod._execute_intent(p, dummy_intent, raw_line=cmd, _normalized=True)
    finally:
        repl_mod._say = old_say
    return buf.getvalue(), p

def test_history_find_basic():
    out, _ = _repl_history_find(["history find alpha"])
    check("IRR.find_basic", "08[Create] :: alpha test" in out and "(1)" in out)

def test_history_find_multiple():
    out, _ = _repl_history_find(["history find create"])
    check("IRR.find_multiple", "(2)" in out)

def test_history_find_case_insensitive():
    out, _ = _repl_history_find(["history find ALPHA"])
    check("IRR.find_case_insensitive", "alpha test" in out)

def test_history_find_no_match():
    out, _ = _repl_history_find(["history find zzzzzz"])
    check("IRR.find_no_match", "No history matches" in out)

def test_history_find_bare_usage():
    out, _ = _repl_history_find(["history find"])
    check("IRR.find_bare_usage", "usage: history find" in out)

def test_history_find_no_execution():
    # Display-only: history must be unchanged after find (real production path)
    from form.open import Program
    before_hist = ["test command"]
    out, p = _repl_history_find(["history find test"], history=list(before_hist))
    check("IRR.find_no_mutation", list(p.history) == before_hist)

def main():
    test_history_find_basic()
    test_history_find_multiple()
    test_history_find_case_insensitive()
    test_history_find_no_match()
    test_history_find_bare_usage()
    test_history_find_no_execution()
    total = len(CHECKS)
    failed = sum(1 for _, ok in CHECKS if not ok)
    print(f"\nIRR-I-FIND: {total - failed}/{total} {'GREEN' if failed == 0 else 'RED'}")
    return 0 if failed == 0 else 1

def smoke() -> bool:
    global CHECKS
    CHECKS = []
    return main() == 0

if __name__ == "__main__":
    sys.exit(main())
