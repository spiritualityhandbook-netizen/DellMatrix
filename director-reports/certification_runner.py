#!/usr/bin/env python3
"""Independent certification runner — DIR-2026-11-02-CONSOLIDATED-R1,
execution order item 2.

ONE COMMAND, from the root of ANY fresh clone of this repository:

    python3 director-reports/certification_runner.py [--out DIR]

What it does
------------
Executes, sequentially and as subprocesses from the repository
root, the targeted suite for each scope the Director source-
verified but could not execute (DIR-F12, DIR-F13, DIR-F14,
DIR-F15, DIR-F16, T2 incl. DIR-T2-R2, Step 10, Step 11), PLUS
independent boundary probes that exercise the underlying claims
directly instead of trusting the suites:

  probe_t2_omitted_node       the DIR-T2-R2 required
                              counterexample (plant A grown;
                              only unplanted node B supplied)
  probe_dirf16_send_boundary  pidfd send-boundary errno
                              injection on a live witnessed
                              process (EPERM/ENOSYS ->
                              "unavailable", ESRCH -> "refused")
  probe_dirf15_absent_vs_none the Director's Diff reproducer
                              through the public seed path
                              (stored None removed -> membership
                              change; retained None -> no change)
  probe_dirf13_malformed_count the count grammar directly and
                              through the public Loop path
                              (superscript / non-ASCII / oversized
                              counts refused, program stays usable)

Every item's raw stdout, stderr, and exit code is captured to a
timestamped output directory together with an environment header
(Python version, platform, the revision SHA the run executed at)
and a MANIFEST.sha256 whose digests let the reader verify the
bytes of every output file (C-Q2 standing format: a manifest
claim is not byte verification — the digests are the means to
verify).

Exit code: 0 only if EVERY suite and probe exits 0. Anything
else (failure, timeout, missing file) exits 1. This runner is
an execution instrument, not a certificate: certification is
the Director's act, performed on outputs he produced or can
reproduce with this script.

Standard library only. No network. Items run SEQUENTIALLY —
the suites share form/state and must never run concurrently.
Per-item timeout: 900 seconds (matches form/regress.py).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

TIMEOUT_S = 900

# (output id, scope label, module run as `python3 -m <module>`)
SUITES = [
    ("suite_dirf12", "DIR-F12 Exchange journal receipt",
     "form.dirf12_journal_receipt_test"),
    ("suite_dirf13", "DIR-F13 Loop count grammar",
     "form.dirf13_loop_count_test"),
    ("suite_dirf14", "DIR-F14 Catch consumed split",
     "form.dirf14_catch_consumed_test"),
    ("suite_dirf15", "DIR-F15 Diff absent-vs-None (step 9 suite)",
     "form.step9_diff_test"),
    ("suite_dirf16", "DIR-F16 pidfd send-boundary classes (DAF-09 suite)",
     "form.daf09_timeout_tree_test"),
    ("suite_t2", "T2 + DIR-T2-R2 growth-lens plant identity",
     "form.mandell.view_rooms_growth_test"),
    ("suite_step10", "Step 10 Resolve/Ungroup/Compose consistency",
     "form.step10_consistency_test"),
    ("suite_step11", "Step 11 public contracts",
     "form.step11_public_contracts_test"),
]

PROBE_T2 = r'''
import os, sys
sys.path.insert(0, os.getcwd())
from form.dell_matrix.forces import GrowthForce
from form.dell_matrix.view_rooms import filter_nodes_for_room

PREFIX = "Q" * 80
LABEL_A = PREFIX + " first-planted-idea"
LABEL_B = PREFIX + " never-planted-node"
fails = []

def case(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name
          + (" -- " + detail if detail else ""))
    if not cond:
        fails.append(name)

gf = GrowthForce()
gf.plant(LABEL_A)
for _ in range(4):
    gf.grow_all(2.0)
stage_a = gf.plants[0]["stage"]
case("sanity: plant A grew past seed", stage_a not in (None, "seed"),
     "A stage=%r" % (stage_a,))

out = filter_nodes_for_room(
    "growth", [{"id": "b", "label": LABEL_B, "score": 0.0}],
    plants=gf.plants)
case("DIR-T2-R2 counterexample: omitted node B never receives A's stage",
     out[0].get("stage") is None,
     "B stage=%r source=%r" % (out[0].get("stage"),
                               out[0].get("stage_source")))

out = filter_nodes_for_room(
    "growth", [{"id": "a", "label": LABEL_A, "score": 0.0}],
    plants=gf.plants)
case("positive control: node A resolves to A's own stage",
     out[0].get("stage") == stage_a
     and out[0].get("stage_source") == "growth_force",
     "A stage=%r source=%r" % (out[0].get("stage"),
                               out[0].get("stage_source")))

out = filter_nodes_for_room(
    "growth", [{"id": "b", "label": LABEL_B, "score": 0.0}],
    plants=[{"idea": PREFIX, "stage": "branch"}])
case("legacy prefix-only plant: B stays ambiguous, never attributed",
     out[0].get("stage") is None
     and out[0].get("stage_source") == "ambiguous",
     "B stage=%r source=%r" % (out[0].get("stage"),
                               out[0].get("stage_source")))

print("=== probe_t2_omitted_node: %d/4 ===" % (4 - len(fails)))
sys.exit(1 if fails else 0)
'''

PROBE_F16 = r'''
import errno, os, signal, subprocess, sys
sys.path.insert(0, os.getcwd())
import form.regress as R

fails = []

def case(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name
          + (" -- " + detail if detail else ""))
    if not cond:
        fails.append(name)

def boom(err):
    def _raise(fd, sig):
        raise OSError(err, os.strerror(err))
    return _raise

victim = subprocess.Popen([sys.executable, "-c",
                           "import time; time.sleep(60)"])
try:
    ident = (victim.pid, R._proc_starttime(victim.pid))
    case("sanity: witnessed identity captured", ident[1] is not None,
         "pid=%s starttime=%s" % ident)
    real_send = R._pidfd_send_signal
    for name, err, want in (("EPERM", errno.EPERM, "unavailable"),
                            ("ENOSYS", errno.ENOSYS, "unavailable"),
                            ("ESRCH", errno.ESRCH, "refused")):
        R._pidfd_send_signal = boom(err)
        try:
            outcome = R._signal_identity(ident[0], ident[1],
                                         signal.SIGKILL)
        finally:
            R._pidfd_send_signal = real_send
        case("send-%s classes %s" % (name, want), outcome == want,
             "outcome=%r" % (outcome,))
        case("send-%s: live victim not signalled" % name,
             victim.poll() is None)
finally:
    if victim.poll() is None:
        victim.terminate()
    victim.wait(timeout=10)

print("=== probe_dirf16_send_boundary: %d/7 ===" % (7 - len(fails)))
sys.exit(1 if fails else 0)
'''

PROBE_F15 = r'''
import glob, os, shutil, sys
sys.path.insert(0, os.getcwd())

fails = []

def case(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name
          + (" -- " + detail if detail else ""))
    if not cond:
        fails.append(name)

def cleanup(owner):
    base = os.path.join(os.getcwd(), "form", "state")
    for pat in ("program_%s.json", "nursery_%s.json",
                "checkpoint_%s.json", "confirm_journal_%s.json",
                "confirm_gen_%s.json", "confirm_current_%s.json"):
        for f in glob.glob(os.path.join(base, pat % owner)):
            os.remove(f)
    d = os.path.join(base, "ideas_%s" % owner)
    if os.path.isdir(d):
        shutil.rmtree(d)

def program(owner):
    cleanup(owner)
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    p = Program(owner=owner)
    attach(p)
    return p

def run(p, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(p, seed)

# Removal: stored None deleted -> membership change (Director's
# reproducer). None is seeded DIRECTLY into state: the store is
# Dict[str, Any] by design and no public string writer emits
# None. This is a state-seeding claim, not a public-writer claim.
owner = "CertRunnerF15Rem"
try:
    p = program(owner)
    st = p.core_ii
    st.store["nullable"] = None
    run(p, "86[Delete] :: nullable")
    r = run(p, "89[Diff]")
    case("stored-None removal is a membership change",
         r.get("ok") is True
         and st.last_diff.get("changed") == ["nullable"]
         and st.last_diff.get("before") == {"nullable": None}
         and st.last_diff.get("after") == {},
         "last_diff=%r" % (st.last_diff,))
finally:
    cleanup(owner)

# Guard: a None retained unchanged on both sides is NOT a change.
owner = "CertRunnerF15Retain"
try:
    p = program(owner)
    st = p.core_ii
    st.store["nullable"] = None
    run(p, "55[Set] :: a=1")
    r = run(p, "89[Diff]")
    case("retained None is absent from changed",
         r.get("ok") is True
         and st.last_diff.get("changed") == ["a"],
         "last_diff=%r" % (st.last_diff,))
finally:
    cleanup(owner)

print("=== probe_dirf15_absent_vs_none: %d/2 ===" % (2 - len(fails)))
sys.exit(1 if fails else 0)
'''

PROBE_F13 = r'''
import glob, os, shutil, sys
sys.path.insert(0, os.getcwd())
from form.mandell.executor_leaf import _parse_count

fails = []

def case(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name
          + (" -- " + detail if detail else ""))
    if not cond:
        fails.append(name)

case("grammar: superscript refused", _parse_count("²") is None)
case("grammar: Arabic-Indic digit refused", _parse_count("٣") is None)
case("grammar: oversized refused", _parse_count("9" * 100) is None)
case("grammar: empty refused", _parse_count("") is None)
case("grammar: '3' parses", _parse_count("3") == 3)
case("grammar: '0007' parses", _parse_count("0007") == 7)

def cleanup(owner):
    base = os.path.join(os.getcwd(), "form", "state")
    for pat in ("program_%s.json", "nursery_%s.json",
                "checkpoint_%s.json", "confirm_journal_%s.json",
                "confirm_gen_%s.json", "confirm_current_%s.json"):
        for f in glob.glob(os.path.join(base, pat % owner)):
            os.remove(f)
    d = os.path.join(base, "ideas_%s" % owner)
    if os.path.isdir(d):
        shutil.rmtree(d)

owner = "CertRunnerF13Loop"
try:
    cleanup(owner)
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    from form.mandell.executor import execute_seed
    p = Program(owner=owner)
    attach(p)
    execute_seed(p, "08[Create] :: Alpha")
    r = execute_seed(p, "13[Loop] :: ²")
    case("public path: Loop superscript refuses invalid_loop_count",
         r.get("ok") is False
         and r.get("error") == "invalid_loop_count",
         "result=%r" % ({k: r.get(k) for k in ("ok", "error")},))
    r = execute_seed(p, "13[Loop] :: 2")
    case("public path: program stays usable (lawful Loop runs)",
         r.get("ok") is True,
         "result=%r" % ({k: r.get(k) for k in ("ok", "error")},))
finally:
    cleanup(owner)

print("=== probe_dirf13_malformed_count: %d/8 ===" % (8 - len(fails)))
sys.exit(1 if fails else 0)
'''

PROBES = [
    ("probe_t2_omitted_node", "DIR-T2-R2 omitted-node counterexample",
     PROBE_T2),
    ("probe_dirf16_send_boundary", "DIR-F16 send-boundary errno classes",
     PROBE_F16),
    ("probe_dirf15_absent_vs_none", "DIR-F15 absent-vs-None comparator",
     PROBE_F15),
    ("probe_dirf13_malformed_count", "DIR-F13 malformed count refusal",
     PROBE_F13),
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def revision_sha(repo_root):
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root,
            capture_output=True, text=True, timeout=30)
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return "unknown (git unavailable or not a checkout)"


def run_item(item_id, argv, repo_root, out_dir, subdir):
    """Run one item, capture raw streams, return (exit_code, seconds)."""
    d = os.path.join(out_dir, subdir)
    os.makedirs(d, exist_ok=True)
    start = time.monotonic()
    try:
        proc = subprocess.run(
            argv, cwd=repo_root, capture_output=True, text=True,
            timeout=TIMEOUT_S)
        code, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        code = "TIMEOUT"
        out = (exc.stdout or b"").decode("utf-8", "replace") \
            if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = ((exc.stderr or b"").decode("utf-8", "replace")
               if isinstance(exc.stderr, bytes) else (exc.stderr or ""))
        err += f"\n[certification_runner] TIMEOUT after {TIMEOUT_S}s\n"
    secs = time.monotonic() - start
    with open(os.path.join(d, item_id + ".stdout.txt"), "w") as fh:
        fh.write(out)
    with open(os.path.join(d, item_id + ".stderr.txt"), "w") as fh:
        fh.write(err)
    return code, secs


def main():
    ap = argparse.ArgumentParser(
        description="Independent certification runner "
                    "(DIR-2026-11-02-CONSOLIDATED-R1 item 2).")
    ap.add_argument("--out", default=None,
                    help="output directory (default: "
                         "certification_run_<UTC timestamp> "
                         "under the current directory)")
    args = ap.parse_args()

    script_path = os.path.abspath(__file__)
    repo_root = os.path.dirname(os.path.dirname(script_path))
    if not os.path.isdir(os.path.join(repo_root, "form")):
        print("ERROR: form/ not found under derived repo root "
              f"{repo_root!r}; run from a DellMatrix checkout.",
              file=sys.stderr)
        return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.out or os.path.join(
        os.getcwd(), f"certification_run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    header = [
        "Independent certification run",
        "=============================",
        f"started_utc: {datetime.now(timezone.utc).isoformat()}",
        f"repo_root: {repo_root}",
        f"revision_sha: {revision_sha(repo_root)}",
        f"python: {sys.version.replace(chr(10), ' ')}",
        f"python_executable: {sys.executable}",
        f"platform: {platform.platform()}",
        f"runner_file: {script_path}",
        f"runner_sha256: {sha256_file(script_path)}",
        f"per_item_timeout_s: {TIMEOUT_S}",
        "items run sequentially; suites are subprocesses "
        "(python3 -m <module>) from the repo root; probes are "
        "the sources preserved under probe_sources/.",
        "",
    ]
    with open(os.path.join(out_dir, "environment.txt"), "w") as fh:
        fh.write("\n".join(header))
    print("\n".join(header))

    results = []  # (id, label, kind, exit_code, seconds)

    for item_id, label, module in SUITES:
        print(f"[run] suite {item_id} :: {label}", flush=True)
        code, secs = run_item(
            item_id, [sys.executable, "-m", module],
            repo_root, out_dir, "suites")
        results.append((item_id, label, "suite", code, secs))
        print(f"      exit={code} ({secs:.1f}s)", flush=True)

    src_dir = os.path.join(out_dir, "probe_sources")
    os.makedirs(src_dir, exist_ok=True)
    for item_id, label, source in PROBES:
        src_path = os.path.join(src_dir, item_id + ".py")
        with open(src_path, "w") as fh:
            fh.write(source.lstrip("\n"))
        print(f"[run] probe {item_id} :: {label}", flush=True)
        code, secs = run_item(
            item_id, [sys.executable, src_path],
            repo_root, out_dir, "probes")
        results.append((item_id, label, "probe", code, secs))
        print(f"      exit={code} ({secs:.1f}s)", flush=True)

    all_ok = all(r[3] == 0 for r in results)
    lines = ["Certification runner summary",
             "============================", ""]
    for item_id, label, kind, code, secs in results:
        verdict = "PASS" if code == 0 else "FAIL"
        lines.append(f"{verdict}  {kind:5s}  {item_id:28s} "
                     f"exit={code}  {secs:7.1f}s  {label}")
    lines += ["",
              f"OVERALL: {'PASS' if all_ok else 'FAIL'} "
              f"({sum(1 for r in results if r[3] == 0)}"
              f"/{len(results)} items exit 0)",
              "Raw streams: suites/ and probes/ beside this file. "
              "Verify bytes against MANIFEST.sha256.",
              "This summary reports execution only. "
              "Certification is the Director's act."]
    with open(os.path.join(out_dir, "summary.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))

    # Manifest last: digests of every output file except itself.
    entries = []
    for root, _dirs, files in os.walk(out_dir):
        for name in sorted(files):
            path = os.path.join(root, name)
            rel = os.path.relpath(path, out_dir)
            if rel == "MANIFEST.sha256":
                continue
            entries.append((rel, sha256_file(path)))
    with open(os.path.join(out_dir, "MANIFEST.sha256"), "w") as fh:
        fh.write("# SHA-256 of every file in this run directory "
                 "except this manifest.\n")
        fh.write("# Verify: sha256sum -c MANIFEST.sha256 "
                 "(from inside the run directory), ignoring this "
                 "comment header.\n")
        for rel, digest in sorted(entries):
            fh.write(f"{digest}  {rel}\n")
    print(f"\nOutputs in: {out_dir}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
