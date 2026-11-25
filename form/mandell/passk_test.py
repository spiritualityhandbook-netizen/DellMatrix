"""Phase F — pass^k reliability harness (README-program follow-on;
grokbot hypothesis H4).

`python3 -m form.regress --passk ENTRY K` runs ONE entry K times,
each in a FRESH private copy of the source tree (isolated state per
run), and reports p/k honestly: GREEN only at p == k. A single GREEN
can be luck or state coupling; pass^k is the reliability instrument
the Exchange program's replication accounting builds on.

This suite is self-contained: it builds a MINIATURE source tree
(a tiny form/ package with passing / failing / flaky / freshness-
sensitive suites) in a temp directory and drives regress.run_passk
and regress.main against it. The flaky suite is driven by a counter
file OUTSIDE the copied tree, passed via the PASSK_FLAKE_FILE
environment variable (run_entry inherits os.environ), so run 1 fails
and runs 2+ pass — proving per-run accounting (2/3), not all-or-
nothing. The freshness suite writes a marker beside its own module
inside the copy and fails if the marker already exists — it can
only pass k/k if every run truly got a fresh copy.

Usage errors (unknown entry, k outside 1..20, --passk combined with
--order/--twice, a regression copy as src) must run NOTHING and
fail with the usage/false result, verified by the absence of any
"PASSK run" lines in the captured output.
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import sys
import tempfile

CHECKS: list = []

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from form import regress  # noqa: E402

MINI_PASS = '''
def smoke():
    print("mini_pass: 1/1")
    return True
'''

MINI_FAIL = '''
def smoke():
    print("mini_fail: 0/1")
    return False
'''

MINI_FLAKY = '''
import os

def smoke():
    p = os.environ["PASSK_FLAKE_FILE"]
    try:
        n = int(open(p).read().strip() or "0")
    except Exception:
        n = 0
    open(p, "w").write(str(n + 1))
    ok = n >= 1
    print("mini_flaky: " + ("1/1" if ok else "0/1"))
    return ok
'''

MINI_FRESH = '''
import os

def smoke():
    marker = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "_fresh_marker.txt")
    if os.path.exists(marker):
        print("mini_fresh: 0/1")
        return False
    open(marker, "w").write("ran")
    print("mini_fresh: 1/1")
    return True
'''


def check(name: str, cond: bool, detail: str = "") -> bool:
    CHECKS.append((name, bool(cond), detail))
    return bool(cond)


def _build_mini(base: str) -> str:
    src = os.path.join(base, "minisrc")
    form = os.path.join(src, "form")
    os.makedirs(form)
    open(os.path.join(form, "__init__.py"), "w").close()
    for fname, body in (("mini_pass_test.py", MINI_PASS),
                        ("mini_fail_test.py", MINI_FAIL),
                        ("mini_flaky_test.py", MINI_FLAKY),
                        ("mini_fresh_test.py", MINI_FRESH)):
        with open(os.path.join(form, fname), "w", encoding="utf-8") as fh:
            fh.write(body)
    return src


def _run_passk(entry, k, src):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ok = regress.run_passk(entry, k, src=src)
    return ok, buf.getvalue()


def smoke() -> bool:
    CHECKS.clear()
    base = tempfile.mkdtemp(prefix="dm_passk_test_")
    old_env = os.environ.get("PASSK_FLAKE_FILE")
    try:
        src = _build_mini(base)

        ok, out = _run_passk("form.mini_pass_test", 3, src)
        check("passk_all_pass_green", ok and "3/3 -> GREEN" in out, out[-200:])

        ok, out = _run_passk("form.mini_fail_test", 2, src)
        check("passk_all_fail_red_counted", (not ok) and "0/2 -> RED" in out,
              out[-200:])

        counter = os.path.join(base, "flake_counter.txt")
        os.environ["PASSK_FLAKE_FILE"] = counter
        ok, out = _run_passk("form.mini_flaky_test", 3, src)
        check("passk_flaky_partial_count", (not ok) and "2/3 -> RED" in out,
              out[-200:])

        ok, out = _run_passk("form.mini_fresh_test", 3, src)
        check("passk_fresh_copy_per_run", ok and "3/3 -> GREEN" in out,
              out[-200:])

        ok, out = _run_passk("form.mini_nope_test", 2, src)
        check("passk_unknown_entry_runs_nothing",
              (not ok) and "unknown entry" in out and "PASSK run" not in out,
              out[-200:])

        ok0, out0 = _run_passk("form.mini_pass_test", 0, src)
        ok21, out21 = _run_passk("form.mini_pass_test", 21, src)
        check("passk_bad_k_runs_nothing",
              (not ok0) and (not ok21)
              and "PASSK run" not in out0 and "PASSK run" not in out21,
              (out0 + out21)[-200:])

        fake = os.path.join(base, "fakecopy")
        os.makedirs(fake)
        open(os.path.join(fake, regress.COPY_MARKER), "w").close()
        ok, out = _run_passk("form.mini_pass_test", 1, fake)
        check("passk_refuses_regression_copy_src",
              (not ok) and "regression copy" in out and "PASSK run" not in out,
              out[-200:])

        with contextlib.redirect_stderr(io.StringIO()):
            rc_conflict = regress.main(
                ["--passk", "form.mini_pass_test", "2", "--twice"])
            rc_badk = regress.main(["--passk", "form.mini_pass_test", "0"])
            rc_wordk = regress.main(["--passk", "form.mini_pass_test", "two"])
            rc_unknown = regress.main(
                ["--passk", "form.mandell.no_such_suite_xyz", "2"])
        check("cli_conflicts_and_bad_args_exit_2",
              rc_conflict == 2 and rc_badk == 2 and rc_wordk == 2
              and rc_unknown == 2,
              f"{rc_conflict} {rc_badk} {rc_wordk} {rc_unknown}")
    finally:
        if old_env is None:
            os.environ.pop("PASSK_FLAKE_FILE", None)
        else:
            os.environ["PASSK_FLAKE_FILE"] = old_env
        try:
            shutil.rmtree(base)
        except OSError as e:  # loud, per program cleanup law
            raise AssertionError(f"cleanup failed for {base}: {e}")
    failed = [(n, d) for n, ok_, d in CHECKS if not ok_]
    for n, ok_, d in CHECKS:
        print(f"  {'PASS' if ok_ else 'FAIL'}  {n}"
              + (f"  -- {d}" if (d and not ok_) else ""))
    print(f"passk_test: {len(CHECKS) - len(failed)}/{len(CHECKS)}")
    return not failed


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
