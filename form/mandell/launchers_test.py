"""Phase L — Windows/Mac launchers (README program).

README §2 listed the Windows/Mac launchers as UNVERIFIED:
"`Launch DellMatrix.bat` / `.command` exist but not executed".

Findings from grounding:
- `Launch DellMatrix.command` is a bash script: it runs for real
  in this environment. The suite executes it end-to-end (banner
  -> REPL as owner Operator -> a real command -> quit -> the
  closing `read` satisfied by EOF) and its failure branch (no
  python3 on PATH -> the install hint prints).
- One defect fixed by this phase: git recorded the .command as
  mode 100644. A macOS .command needs the execute bit for Finder
  double-click launching; a fresh clone produced a file that
  would open in a text editor instead. The phase sets 100755 and
  this suite asserts the bit so it cannot silently regress.
- `Launch DellMatrix.bat` targets cmd.exe, which does not exist
  in this environment (no wine) — it CANNOT be executed here,
  and this suite does not pretend otherwise. What is verified:
  structural equivalence with the executed .command (same
  banner, same REPL entry `python -m form.repl --owner
  Operator`, an errorlevel branch) and that every path it
  references exists (docs\\INSTALL.md). Execution on real
  Windows remains UNVERIFIED and Phase O's README text says
  exactly that.
- `launch.py` (the third launcher, already README-verified) is
  executed once as a regression guard.

The .command runs the REPL as the hardcoded owner "Operator";
the sessions here never issue `save`, so no state persists.
"""

from __future__ import annotations

import os
import stat
import subprocess
import sys

CHECKS: list = []

ROOT = os.path.abspath(".")
COMMAND = os.path.join(ROOT, "Launch DellMatrix.command")
BAT = os.path.join(ROOT, "Launch DellMatrix.bat")
LAUNCH_PY = os.path.join(ROOT, "launch.py")


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))


def _run(args, inp, env=None, timeout=120):
    result = subprocess.run(
        args, cwd=ROOT, env=env, input=inp,
        capture_output=True, text=True, timeout=timeout)
    return result.returncode, result.stdout + result.stderr


def smoke() -> bool:
    with open(COMMAND, encoding="utf-8") as fh:
        command_src = fh.read()
    with open(BAT, encoding="utf-8") as fh:
        bat_src = fh.read()

    # ── .command: executable bit (the Finder double-click door) ──
    mode = os.stat(COMMAND).st_mode
    check("command: execute bit set (git mode 100755)",
          bool(mode & stat.S_IXUSR), oct(mode))

    # ── .command: end-to-end execution ──────────────────────────
    # Faithful simulation of the double-click path: a PTY (via
    # util-linux `script`), typed commands, and the final Enter
    # at the "Press Enter to close..." prompt. A plain pipe
    # cannot express that Enter — Python buffers the piped stdin,
    # so bash's closing `read` sees EOF and the script exits 1
    # even after a fully successful session; that artifact is a
    # property of pipes, not of the launcher.
    import shlex
    import shutil as _shutil
    typed = "create an idea called Launcher Suite Probe\nquit\n\n"
    if _shutil.which("script"):
        rc, out = _run(
            ["script", "-qec",
             f"bash {shlex.quote(COMMAND)}", "/dev/null"], typed)
        check("command: exits clean (interactive simulation)",
              rc == 0, out[-300:])
        check("command: reaches the press-enter close prompt",
              "Press Enter to close" in out, out[-300:])
    else:
        rc, out = _run(["bash", COMMAND], typed)
        check("command: session succeeds under a pipe "
              "(exit is the read-at-EOF artifact)",
              rc in (0, 1) and "Goodbye." in out, out[-300:])
    check("command: prints the launcher banner",
          "DellMatrix — ready for anyone" in out, out[-300:])
    check("command: starts the real REPL",
          "DellMatrix — Mandell Origin" in out, out[-300:])
    check("command: REPL executes a real command",
          'Created idea: "Launcher Suite Probe"' in out, out[-300:])

    # ── .command: failure branch (python3 missing) ───────────────
    import tempfile
    with tempfile.TemporaryDirectory() as empty_bin:
        env = {**os.environ, "PATH": empty_bin}
        rc, out = _run(["/bin/bash", COMMAND], "quit\n", env=env)
    check("command: missing python prints the install hint",
          "Python could not start. Install Python 3 and see "
          "docs/INSTALL.md" in out, out[-300:])
    check("command: hint target docs/INSTALL.md exists",
          os.path.isfile(os.path.join(ROOT, "docs", "INSTALL.md")))

    # ── .bat: structural equivalence (NOT execution) ─────────────
    check("bat: enters its own directory",
          'cd /d "%~dp0"' in bat_src)
    check("bat: same banner as the executed .command",
          "DellMatrix — ready for anyone" in bat_src
          and "DellMatrix — ready for anyone" in command_src)
    check("bat: invokes the same REPL entry as .command",
          "python -m form.repl --owner Operator" in bat_src
          and "python3 -m form.repl --owner Operator" in command_src)
    check("bat: has a python-failure branch",
          "errorlevel 1" in bat_src and "Python could not start."
          in bat_src)
    check("bat: referenced docs\\INSTALL.md exists",
          "docs\\INSTALL.md" in bat_src
          and os.path.isfile(os.path.join(ROOT, "docs", "INSTALL.md")))

    # ── launch.py: regression guard execution ────────────────────
    rc, out = _run([sys.executable, LAUNCH_PY, "LauncherSuite"],
                   "quit\n")
    check("launch.py: exits clean with its banner",
          rc == 0 and "DellMatrix — ready for anyone" in out,
          out[-300:])

    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"=== Launchers: {passed}/{len(CHECKS)} ===")
    return passed == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
