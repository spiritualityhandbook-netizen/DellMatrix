#!/usr/bin/env python3
"""Canonical regression authority (one list, one runner).

    python -m form.regress              # forward
    python -m form.regress --order rev  # reverse order
    python -m form.regress --twice      # run the list twice on the same state (exposes state coupling)
    python -m form.regress --help       # usage only (exit 0, no entry runs); any bad argument exits 2 unrun

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

import argparse
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
    "form.duobeta_live_test",
    "form.mandell.semantic_route_test",
    "form.mandell.flow_executor_test",
    "form.mandell.english_composer_test",
    "form.mandell.dcc_vi_test",
    "form.mandell.dcc_vii_test",
    "form.mandell.dcc_viii_test",
    "form.mandell.dcc_ix_test",
    "form.mandell.dcc_x_test",
    "form.mandell.dcc_xi_test",
    "form.mandell.dcc_xii_test",
    "form.mandell.dcc_xiii_test",
    "form.mandell.dcc_xiv_test",
    "form.mandell.dcc_xv_test",
    "form.mandell.dcc_xv_cross_process_test",
    "form.mandell.dcc_xvi_test",
    "form.mandell.dcc_xvi_atomicity_test",
    "form.mandell.dcc_xvii_test",
    "form.mandell.dcc_xviii_test",
    "form.mandell.dcc_xix_test",
    "form.mandell.dcc_xx_test",
    "form.mandell.p0r1_persist_test",
    "form.mandell.pac_i_test",
    "form.mandell.cac_i_test",
    "form.mandell.ssi_i_test",
    "form.mandell.eoc_i_test",
    "form.mandell.pac_i_proofs_test",
    "form.mandell.ros_i_test",
    "form.mandell.dbel_i_test",
    "form.mandell.asi_i_test",
    "form.mandell.nbde_i_test",
    "form.mandell.fcnd_i_test",
    "form.mandell.leas_i_test",
    "form.mandell.cdpc_i_test",
    "form.mandell.rccr_i_test",
    "form.mandell.iac_i_test",
    "form.mandell.dell37_nurture_test",
    "form.mandell.set_detail_goals_test",
    "form.mandell.live_response_integrity_test",
    "form.mandell.iac_isolation_test",
    "form.mandell.dell87_refusal_test",
    "form.mandell.cmd_hardening_test",
    "form.mandell.r2_registry_reconciliation_test",
    "form.mandell.r2_semantic_honesty_test",
    "form.mandell.hic_i_test",
    "form.mandell.ekc_i_test",
    "form.mandell.aec_i_test",
    "form.mandell.odcg_i_test",
    "form.mandell.dla_i_test",
    "form.mandell.kie_i_test",
    "form.cn_ii_nav_test",
    "form.irr_i_find_test",
    "form.iri_i_test",
    "form.saoc_ii_test",
    "form.tpp_i_test",
    "form.greek_test",
    "form.dell_matrix.program_strength",
    "form.mandell.core_ii_smoke",
]

TIMEOUT_S = 900
COPY_MARKER = ".dm_regress_copy"  # written into every private copy; run() refuses a copy as its src
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
    open(os.path.join(work, COPY_MARKER), "w").close()  # every regression copy is identifiable
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
    """Run entries (default LIST) against a private copy of ``src``. intended defaults to LIST + discovered.

    Recursion guard: a src that is itself a regression copy (COPY_MARKER present) is refused RED before anything
    is copied or run, whatever the entries, env or caller (self-entry, stubbed/re-spawned CLI, nested run())."""
    if os.path.exists(os.path.join(src, COPY_MARKER)):
        print(f"REGRESS: src {src} is a regression copy ({COPY_MARKER}); nested run refused -> RED", flush=True)
        return False
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


class _Once(argparse.Action):
    """Store an option at most once: a repeated or conflicting --order/--twice is a usage error."""

    def __call__(self, parser, namespace, values, option_string=None):
        seen = namespace.__dict__.setdefault("_given", set())
        if self.dest in seen:
            parser.error(f"{option_string} given more than once (repeated or conflicting)")
        seen.add(self.dest)
        setattr(namespace, self.dest, True if self.nargs == 0 else values)


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="python -m form.regress", allow_abbrev=False,
                                 description="Canonical regression runner (one list, one process per entry).")
    ap.add_argument("--order", choices=("fwd", "rev"), default="fwd", action=_Once,
                    help="entry order (fwd|rev); --order rev and --order=rev are equivalent")
    ap.add_argument("--twice", nargs=0, default=False, action=_Once,
                    help="run the list twice on the same state (exposes state coupling)")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    """Strict CLI: every argument is validated BEFORE any entry runs. --help/-h prints usage and exits 0 with
    zero entries run and no verdict; any unknown, malformed, abbreviated, repeated or extra token exits 2."""
    a = list(sys.argv[1:] if argv is None else argv)
    ap = _parser()
    if "--" in a:
        print(ap.format_usage().rstrip() + "\nerror: '--' is not accepted", file=sys.stderr)
        return 2
    try:
        ns = ap.parse_args(a)
    except SystemExit as e:
        return 0 if e.code in (0, None) else 2
    ok = run(order=ns.order, twice=ns.twice)
    print(f"REGRESS FINAL: {'GREEN' if ok else 'RED'} (order={ns.order}{', twice' if ns.twice else ''})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
