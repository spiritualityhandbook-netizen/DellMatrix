#!/usr/bin/env python3
"""
Boot — harmony fix: one path into the program.

Delegates to form.open so operators never get a second, thinner matrix.
"""

from __future__ import annotations

import json
import sys

from form.open import open_program, smoke as open_smoke


def boot(owner: str = "Operator"):
    p = open_program(owner)
    return p.status()


def smoke() -> bool:
    return open_smoke()


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    owner = "Operator"
    for i, a in enumerate(sys.argv):
        if a == "--owner" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
    print(json.dumps(boot(owner), indent=2, default=str))


if __name__ == "__main__":
    main()
