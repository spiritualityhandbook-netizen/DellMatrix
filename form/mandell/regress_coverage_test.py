#!/usr/bin/env python3
"""Regress coverage meta-suite (Ten-Phase P2, evidence integrity).

The regress is DellMatrix's evidence base. Before P2 it had a silent
hole: discovery matched only ``*_test.py``, so plural ``*_tests.py``
suites ran only via LIST, and twelve GDP-001 proof harnesses plus the
hard invariants ran nowhere at all — a contract could regress with
every suite green.

This suite makes coverage itself a checked contract:

1. Every test-like file on disk (``*_test.py``, ``*_tests.py``,
   ``*_proof.py``, ``*_circuit.py``, ``*_probe.py``, ``*_child.py``,
   plus three named harnesses whose names match no pattern) is either
   an intended regress entry (LIST ∪ discovery) or listed in
   ALLOWLIST below with a recorded reason.
2. Discovery covers the plural ``*_tests.py`` suffix directly.
3. ``form.invariants`` is registered (a production module whose
   smoke() is evidence; only LIST can carry it).
4. Every intended entry names a module file that exists on disk
   (no phantom registrations).
5. ALLOWLIST hygiene: an allowlisted module must exist and must NOT
   be registered — a stale entry fails, so the allowlist cannot
   become a place to hide a suite from the regress.
"""

from __future__ import annotations

import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from form import regress  # noqa: E402

# Deliberately unregistered, with reasons. Child/probe support files
# are executed by their registered parent suites (by import or by
# file path); registering them as standalone suites would run them
# outside the parent context that gives their checks meaning.
ALLOWLIST = {
    "form.mandell.r61_child": "child process support for the registered r61 suite",
    "form.mandell.r62_child": "child process support spawned by path from r62_docking_test",
    "form.mandell.r64_child": "child process support for the registered r64 suites",
    "form.mandell.r65_fresh_probe": "fresh-process probe spawned by the registered r65 suite",
    "form.mandell.r65_verify_probe": "verify probe spawned by the registered r65 suite",
}

# Harnesses whose names match no test-like suffix pattern.
NAMED_HARNESSES = {
    "form.mandell.confirm_crash_matrix",
    "form.mandell.p2_susx100",
    "form.mandell.english_brain_150_loop",
}

_SUFFIXES = ("_test", "_tests", "_proof", "_circuit", "_probe", "_child")


def _disk_modules() -> set:
    out = set()
    base = os.path.join(_ROOT, "form")
    for d, dirs, files in os.walk(base):
        dirs[:] = sorted(
            x for x in dirs
            if x not in regress._SKIP_DIRS and not (d == base and x == "state")
        )
        for f in sorted(files):
            if f.endswith(".py"):
                rel = os.path.relpath(os.path.join(d, f[:-3]), _ROOT)
                out.add(rel.replace(os.sep, "."))
    return out


def _test_like(mod: str) -> bool:
    name = mod.rsplit(".", 1)[-1]
    return any(name.endswith(s) for s in _SUFFIXES) or mod in NAMED_HARNESSES


def smoke() -> bool:
    checks = []

    def rec(name, ok, detail=""):
        checks.append((name, bool(ok)))
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))

    intended = {e.split(":")[0] for e in regress.intended_entries(_ROOT)}
    discovered = {e.split(":")[0] for e in regress.discovered_suites(_ROOT)}
    disk = _disk_modules()

    unaccounted = sorted(
        m for m in disk
        if _test_like(m) and m not in intended and m not in ALLOWLIST
    )
    rec("every_test_like_file_registered_or_allowlisted", not unaccounted,
        f"unaccounted={unaccounted}")

    plural = {"form.mandell.phrase_tests", "form.mandell.polyglot_tests"}
    rec("discovery_covers_plural_tests_suffix", plural <= discovered,
        f"missing={sorted(plural - discovered)}")

    rec("invariants_registered", "form.invariants" in intended)

    phantom = sorted(m for m in intended if m not in disk)
    rec("no_phantom_registrations", not phantom, f"phantom={phantom}")

    stale = sorted(
        m for m in ALLOWLIST if m not in disk or m in intended
    )
    rec("allowlist_exact", not stale, f"stale={stale}")

    npass = sum(1 for _, ok in checks if ok)
    print(f"regress_coverage_test: {npass}/{len(checks)}")
    return npass == len(checks)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
