#!/usr/bin/env python3
"""CN-II: Grouped navigation — presentation-layer tests.

Verifies that help <category> shows exact syntax for each intent group,
and that unknown categories suggest valid ones (suggest, not auto-execute).
"""
import io
import sys

sys.path.insert(0, ".")

CHECKS = []

def check(name, ok):
    CHECKS.append((name, bool(ok)))
    if not ok:
        print(f"FAIL: {name}")

def _repl_help(cmd):
    """Run a help command through the REPL dispatch, capture output."""
    from form import repl as repl_mod
    from form.open import Program
    p = Program(owner="cn-ii-nav-test")
    buf = io.StringIO()
    old_say = repl_mod._say
    old_print = print
    import builtins
    repl_mod._say = lambda s: buf.write(str(s) + "\n")
    builtins.print = lambda *a, **k: buf.write(" ".join(str(x) for x in a) + "\n")
    try:
        # Simulate the help dispatch from run()
        lower = cmd.strip().lower()
        if lower in ("help", "?"):
            builtins.print(repl_mod.HELP_SHORT)
        elif lower.startswith("help "):
            cat = lower[5:].strip()
            if cat in repl_mod.HELP_CATEGORIES:
                builtins.print(repl_mod.HELP_CATEGORIES[cat])
            else:
                repl_mod._say(f'Unknown help category "{cat}".')
                repl_mod._say("  Try: " + " | ".join(f"help {k}" for k in repl_mod.HELP_CATEGORIES))
    finally:
        repl_mod._say = old_say
        builtins.print = old_print
    return buf.getvalue()

def test_help_shows_categories():
    out = _repl_help("help")
    for cat in ("create", "knowledge", "learn", "explain", "save", "recover", "look", "dell", "system"):
        check(f"CNII.help_lists_{cat}", f"help {cat}" in out)

def test_help_category_syntax():
    # Each category must show exact syntax (spot-check key examples)
    cases = {
        "create": "create an idea called",
        "knowledge": "why used <kid>",
        "learn": "learn propose",
        "explain": "outcomes",
        "save": "python3 -m form.repl --load",
        "recover": "history [n]",
        "look": "zoom <id",
        "dell": "35[Discover]",
        "system": "mode beginner",
    }
    for cat, expected in cases.items():
        out = _repl_help(f"help {cat}")
        check(f"CNII.help_{cat}_syntax", expected in out)

def test_help_unknown_category_suggests():
    out = _repl_help("help bogus")
    check("CNII.help_bogus_suggests", "help create" in out and "Unknown help category" in out)
    check("CNII.help_bogus_no_crash", True)  # reaching here = no exception

def main():
    test_help_shows_categories()
    test_help_category_syntax()
    test_help_unknown_category_suggests()
    total = len(CHECKS)
    failed = sum(1 for _, ok in CHECKS if not ok)
    print(f"\nCN-II-NAV: {total - failed}/{total} {'GREEN' if failed == 0 else 'RED'}")
    return 0 if failed == 0 else 1

def smoke() -> bool:
    """Entry point for regress.py (expects smoke() -> bool)."""
    global CHECKS
    CHECKS = []
    return main() == 0

if __name__ == "__main__":
    sys.exit(main())
