#!/usr/bin/env python3
"""Simple launcher — double-click or: python launch.py [OwnerName]"""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    owner = "Operator"
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        owner = sys.argv[1]
    print()
    print("  DellMatrix — ready for anyone")
    print("  Offline. Type help for examples, or:")
    print("  create an idea called test")
    print()
    from form.repl import run
    run(owner=owner)


if __name__ == "__main__":
    main()
