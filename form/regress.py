#!/usr/bin/env python3
"""Canonical regression authority (one list, one runner).

    python -m form.regress              # forward
    python -m form.regress --order rev  # reverse order
    python -m form.regress --twice      # run the list twice on the same state (exposes state coupling)

Each entry "module[:function]" (default function: smoke) runs in its own process:
    python -B -c "r = getattr(importlib.import_module(M), F)(); print(<per-run token> if r is True ...); sys.exit(...)"
All entries of one invocation run in ONE private temporary copy of the source tree (fresh form/state, no
writes to the checkout); --twice reuses that copy for the second pass. The copy is removed afterwards.

Entry GREEN only if: rc == 0 AND the function returned True (token printed after return) AND the last "n/m" count printed has m > 0 and
n == m AND no traceback was emitted. Run GREEN only if the list is non-empty, has no duplicate
(normalized) entries, covers every intended entry (LIST + every form/**/*_test.py), and every entry
executed GREEN. Anything else is RED (exit 1).
"""
from __future__ import annotations

import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
from typing import Iterable, List, Optional, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 4 CI entries (form-smoke.yml history) + 17 *_test suites + core_ii_smoke.
LIST = [
    "form.open",
    "form.mandell.phrase_tests",
    "form.mandell.polyglot_tests",
    "form.accept:run",
    "form.dell_matrix.core_test",
    "form.foundation_acceptance_test",
    "form.lineage_authority_test",
    "form.lineage_semantic_closure_test",
    "form.mandell.control_runtime_test",
    "form.mandell.core_i_maturity_test",
    "form.mandell.core_ii_persist_test",
    "form.mandell.language_efficiency_test",
    "form.mandell.mandell_activation_test",
    "form.mandell.mandell_authority_convergence_test",
    "form.mandell.mandell_canonical_engine_test",
    "form.mandell.mandell_final_runtime_test",
    "form.mandell.mandell_meta_runtime_test",
    "form.mandell.query_reasoning_test",
    "form.mandell.spectrum_closure_test",
    "form.mandell.unified_runtime_test",
    "form.persist_full_roundtrip_test",
    "form.mandell.core_ii_smoke",
]

TIMEOUT_S = 900
_NM = re.compile(r"(\d+)\s*/\s*(\d+)")
_SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def normalize(entry: str) -> str:
    mod, _, fn = entry.strip().partition(":")
    return f"{mod.strip()}:{(fn.strip() or 'smoke')}"


def discovered_suites(src: str = ROOT) -> List[str]:
    """Every tracked-style form/**/*_test.py suite as a normalized entry."""
    out = []
    base = os.path.join(src, "form")
    for d, dirs, files in os.walk(base):
        dirs[:] = sorted(x for x in dirs if x not in _SKIP_DIRS and not (d == base and x == "state"))
        for f in sorted(files):
            if f.endswith("_test.py"):
                rel = os.path.relpath(os.path.join(d, f[:-3]), src)
                out.append(normalize(rel.replace(os.sep, ".")))
    return out


def intended_entries(src: str = ROOT) -> List[str]:
    seen, out = set(), []
    for e in [normalize(x) for x in LIST] + discovered_suites(src):
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out


def _copy_tree(src: str) -> str:
    dst = tempfile.mkdtemp(prefix="dm_regress_")
    state = os.path.join(src, "form", "state")

    def ignore(d, names):
        skip = {n for n in names if n in _SKIP_DIRS or n.endswith((".pyc", ".pyo"))}
        if os.path.abspath(d) == os.path.abspath(os.path.dirname(state)) and "state" in names:
            skip.add("state")
        return skip

    work = os.path.join(dst, "src")
    shutil.copytree(src, work, ignore=ignore, symlinks=True)
    return dst


def run_entry(entry: str, cwd: str) -> Tuple[bool, str]:
    mod, _, fn = normalize(entry).partition(":")
    token = secrets.token_hex(8)  # proves the function RETURNED True (an early sys.exit(0) cannot print it)
    code = ("import importlib,sys; "
            f"r = getattr(importlib.import_module({mod!r}), {fn!r})(); "
            f"print('REGRESS_RETURNED_TRUE:{token}' if r is True else 'REGRESS_RETURNED_NOT_TRUE', flush=True); "
            "sys.exit(0 if r is True else 1)")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    try:
        r = subprocess.run([sys.executable, "-B", "-c", code], cwd=cwd, env=env,
                           capture_output=True, text=True, timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    hits = _NM.findall(r.stdout)
    n, m = (int(hits[-1][0]), int(hits[-1][1])) if hits else (0, 0)
    tb = "Traceback (most recent call last)" in (r.stdout + r.stderr)
    returned = f"REGRESS_RETURNED_TRUE:{token}" in r.stdout
    ok = r.returncode == 0 and returned and bool(hits) and m > 0 and n == m and not tb
    why = f"rc={r.returncode} last={n}/{m}"
    if not returned:
        why += " NOT_RETURNED_TRUE"
    if not hits:
        why += " NO_COUNT"
    if tb:
        why += " TRACEBACK"
    if not ok and r.stderr.strip():
        why += " err=" + r.stderr.strip().splitlines()[-1][:90]
    return ok, why


def run_pass(entries: List[str], intended: Iterable[str], cwd: str, label: str = "") -> bool:
    norm = [normalize(e) for e in entries]
    if not norm:
        print(f"REGRESS{label}: EMPTY LIST -> RED")
        return False
    dups = sorted({e for e in norm if norm.count(e) > 1})
    if dups:
        print(f"REGRESS{label}: DUPLICATE ENTRY {dups} -> RED")
        return False
    omitted = [e for e in (normalize(x) for x in intended) if e not in set(norm)]
    if omitted:
        print(f"REGRESS{label}: OMITTED INTENDED ENTRY {omitted} -> RED")
        return False
    bad, executed = [], 0
    for e in norm:
        ok, why = run_entry(e, cwd)
        executed += 1
        print(f"{'OK ' if ok else 'RED'} {e:58s} {why}", flush=True)
        if not ok:
            bad.append(e)
    green = not bad and executed == len(norm)
    print(f"REGRESS{label}: {executed - len(bad)}/{len(norm)} -> {'GREEN' if green else 'RED'}"
          + (f" red={bad}" if bad else ""), flush=True)
    return green


def run(entries: Optional[List[str]] = None, intended: Optional[Iterable[str]] = None,
        src: str = ROOT, order: str = "fwd", twice: bool = False) -> bool:
    """Run entries (default LIST) against a private copy of ``src``. intended defaults to LIST + discovered."""
    entries = list(LIST if entries is None else entries)
    intended = list(intended_entries(src) if intended is None else intended)
    if order == "rev":
        entries.reverse()
    tmp = _copy_tree(src)
    try:
        cwd = os.path.join(tmp, "src")
        ok = run_pass(entries, intended, cwd, " pass1" if twice else "")
        if twice:
            ok = run_pass(entries, intended, cwd, " pass2") and ok
        return ok
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv: Optional[List[str]] = None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    order = "fwd"
    if "--order" in a:
        i = a.index("--order")
        order = a[i + 1] if i + 1 < len(a) else ""
        if order not in ("fwd", "rev"):
            print(f"REGRESS: bad --order {order!r} (fwd|rev) -> RED")
            return 1
    ok = run(order=order, twice="--twice" in a)
    print(f"REGRESS FINAL: {'GREEN' if ok else 'RED'} (order={order}{', twice' if '--twice' in a else ''})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
