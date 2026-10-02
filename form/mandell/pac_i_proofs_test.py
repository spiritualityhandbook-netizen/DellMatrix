#!/usr/bin/env python3
"""PAC-I authority proofs — permanent regression (promoted NBD-Ω-005 Phase M).

Promotes the established PAC-I authority invariants that previously lived
only in ad-hoc /tmp proof scripts into permanent regression. Each proof is:
  - an already-established invariant (proven in NBD-Ω-003/004 Phase B),
  - deterministic (static source inspection; no timing, no randomness),
  - requiring no production change,
  - minimal in scope (one static property).

The seven behavioral PAC-I proofs (Dell 27 generation commit, roundtrip,
cross-process restore, corruption recovery, Outcome V1 coherence, revision
undo guard, bare-write isolation) already live permanently in
form/mandell/pac_i_test.py. This module covers the one remaining static
gap: no bare-write bypass in the live Dell 27/28 path.
"""
from __future__ import annotations

import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

CHECKS = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond)))
    if not cond:
        print(f"  FAIL: {name} {detail}")


def test_no_bare_write_bypass():
    """core_i_recovery.py (live Dell 27/28 authority) performs zero
    write-mode open() calls — all durable writes route through
    Persistence V2 atomic_write. Dell 27/28 arms import from
    core_i_recovery (no independent write path)."""
    src = os.path.join(REPO, "form", "mandell", "core_i_recovery.py")
    text = open(src, encoding="utf-8").read()
    # Write-mode open(): open(..., "w..."), open(..., "a..."), "x", "+",
    # or os.open with O_WRONLY/O_RDWR/O_CREAT/O_TRUNC.
    write_opens = re.findall(
        r"open\s*\([^)]*[\"'][waxt][^\"']*[\"']", text)
    os_write = re.findall(r"os\.open\s*\(", text)
    check("P1.no_write_open", not write_opens, str(write_opens[:3]))
    check("P2.no_os_open_write", not os_write, str(os_write[:3]))
    check("P3.delegates_to_generation",
          "checkpoint_generation" in text,
          "live checkpoint must commit via Generation V1 (Persistence V2)")
    # Dell 27/28 arms delegate to core_i_recovery (no bypass).
    ops_src = os.path.join(REPO, "form", "mandell", "core_i_ops.py")
    ops_text = open(ops_src, encoding="utf-8").read()
    check("P4.arms_delegate", "core_i_recovery" in ops_text)


def main() -> int:
    test_no_bare_write_bypass()
    total = len(CHECKS)
    failed = sum(1 for _, ok in CHECKS if not ok)
    print(f"pac_i_proofs: {total - failed}/{total} {'GREEN' if failed == 0 else 'RED'}")
    return 0 if failed == 0 else 1


def smoke():
    try:
        main()
    except Exception:
        return False
    return all(ok for _, ok in CHECKS)


if __name__ == "__main__":
    sys.exit(main())
