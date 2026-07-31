#!/usr/bin/env python3
"""Simple launcher — double-click or: python launch.py"""

import os
import sys

# Make sure we run from the project root
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def main():
    owner = "Ace"
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        owner = sys.argv[1]
    print()
    print("  DellMatrix")
    print("  Just talk normally. Type help for examples.")
    print()
    from form.repl import run
    run(owner=owner)

if __name__ == "__main__":
    main()
