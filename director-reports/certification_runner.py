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


# ---------------------------------------------------------------------
# SM-07 (Part 0, register row #91): the unified merge-gate reconciler.
# Contract: director-reports/GATE_RECONCILIATION_RECORD_2026-11-20.md
# and director-reports/PART_0_PLAN_2026-11-20.md section 3.1.
# reconcile_gate(bundle) is a pure, offline, standard-library function:
# it consumes ONE evidence bundle for ONE frozen candidate and returns
# ONE verdict. It never raises on malformed input — a malformed bundle
# is a REFUSED bundle (fail-closed). It is an instrument, not a
# certificate: a RECONCILED verdict states that the evidence
# reconciles; certification remains the authorities' act.
# ---------------------------------------------------------------------

_HOLD_DISPOSITIONS = frozenset({
    "HOLD", "CORRECTION_REQUIRED", "INSUFFICIENT_EVIDENCE",
    # Legacy receipt alias (historical bundles): MAIL_HOLD reads as
    # AUTHORITY_HOLD; it is never a mandatory leg on the normal path.
    "MAIL_HOLD",
})

_FRESHNESS_REQUIRED = (
    "pr", "head_checked", "scan_timestamp", "latest_comment_id",
    "latest_review_id", "director_disposition", "keeper_disposition",
    "newest_ruling_id", "newest_ruling_disposition",
)


def _refused(refusals, legs):
    return {"verdict": "REFUSED", "refusals": refusals, "legs": legs}


def reconcile_gate(bundle):
    """Reconcile one evidence bundle into one gate verdict.

    Returns {"verdict": "RECONCILED" | "REFUSED",
             "refusals": [<refusal code>, ...],
             "legs": {leg name -> state}}.
    Never raises: any malformed input returns REFUSED.
    """
    legs = {}
    refusals = []

    def refuse(code):
        if code not in refusals:
            refusals.append(code)

    try:
        if not isinstance(bundle, dict):
            return _refused(["BUNDLE_INCOMPLETE"], legs)
        phase = bundle.get("phase")
        if phase not in ("pre", "post"):
            refuse("BUNDLE_INCOMPLETE")
            legs["phase"] = {"phase": phase, "state": "unknown"}
            return _refused(refusals, legs)
        legs["phase"] = {"phase": phase, "state": "ok"}

        # --- frozen candidate identity -------------------------------
        head = bundle.get("head")
        tree = bundle.get("tree")
        frozen_head = bundle.get("frozen_head")
        frozen_tree = bundle.get("frozen_tree")
        if bundle.get("pr") is None or head is None or tree is None \
                or frozen_head is None or frozen_tree is None:
            refuse("BUNDLE_INCOMPLETE")
        if head is not None and frozen_head is not None \
                and head != frozen_head:
            refuse("HEAD_DRIFT")
        if tree is not None and frozen_tree is not None \
                and tree != frozen_tree:
            refuse("TREE_DRIFT")
        legs["exact_head"] = {
            "head": head, "frozen_head": frozen_head,
            "tree": tree, "frozen_tree": frozen_tree,
            "state": "refused" if ("HEAD_DRIFT" in refusals
                                   or "TREE_DRIFT" in refusals)
            else "ok",
        }

        # --- checks leg (exact-head CI) ------------------------------
        classifications = {}
        checks_state = "ok"
        checks = bundle.get("checks")
        red_classes = bundle.get("red_classifications")
        if not isinstance(checks, list) \
                or not isinstance(red_classes, dict) \
                or "allow_preexisting" not in bundle:
            refuse("BUNDLE_INCOMPLETE")
            checks_state = "incomplete"
            checks = checks if isinstance(checks, list) else []
            red_classes = red_classes if isinstance(red_classes, dict) \
                else {}
        allow_pre = bundle.get("allow_preexisting") is True
        for chk in checks:
            if not isinstance(chk, dict) or "name" not in chk:
                refuse("BUNDLE_INCOMPLETE")
                checks_state = "incomplete"
                continue
            name = chk.get("name")
            sources = chk.get("sources")
            if isinstance(sources, dict) and len(sources) >= 2 \
                    and len(set(sources.values())) > 1:
                refuse("SOURCE_DISAGREEMENT")
                checks_state = "refused"
            if chk.get("status") != "completed":
                refuse("CHECK_NOT_TERMINAL")
                checks_state = "refused"
                continue
            conclusion = chk.get("conclusion")
            if conclusion == "success":
                continue
            if conclusion != "failure":
                # A terminal state that is neither a pass nor a
                # classified red is not a passed check.
                refuse("CHECK_NOT_TERMINAL")
                checks_state = "refused"
                continue
            cls = red_classes.get(name)
            if cls is not None:
                classifications[name] = cls
            if cls == "candidate-caused":
                refuse("CHECK_FAILED_CANDIDATE")
                checks_state = "refused"
            elif cls == "pre-existing":
                if not allow_pre:
                    refuse("CHECK_FAILED_PREEXISTING_UNAUTHORIZED")
                    checks_state = "refused"
            else:
                # Missing, "unexplained", or unrecognized: every red
                # check must carry an adequate classification.
                refuse("CHECK_FAILED_UNCLASSIFIED")
                checks_state = "refused"
        legs["checks"] = {"state": checks_state,
                          "classifications": classifications}

        # --- merge-tree leg ------------------------------------------
        merge_tree = bundle.get("merge_tree")
        if not isinstance(merge_tree, dict):
            refuse("BUNDLE_INCOMPLETE")
            legs["merge_tree"] = {"state": "incomplete"}
        elif merge_tree.get("clean") is not True \
                or merge_tree.get("conflicts"):
            refuse("MERGE_TREE_CONFLICT")
            legs["merge_tree"] = {"state": "refused",
                                  "conflicts": merge_tree.get("conflicts")}
        else:
            legs["merge_tree"] = {"state": "ok"}

        # --- authority freshness leg (GitHub-first, section 32) ------
        fresh = bundle.get("authority_freshness")
        fresh_state = "ok"
        if not isinstance(fresh, dict):
            refuse("GITHUB_UNCHECKED")
            fresh_state = "missing"
        else:
            source = fresh.get("source")
            if source == "github":
                if any(fresh.get(k) is None for k in _FRESHNESS_REQUIRED) \
                        or fresh.get("pr") != bundle.get("pr") \
                        or fresh.get("head_checked") != frozen_head:
                    refuse("GITHUB_UNCHECKED")
                    fresh_state = "incomplete"
            elif source == "email_exception":
                # Exception-only transport (AGENTS.md section 44):
                # accepted only with a named GitHub outage/rollback
                # authority receipt in the bundle; without one it
                # refuses like any missing scan and never falls back
                # to cached mail.
                if not fresh.get("exception_receipt"):
                    refuse("GITHUB_UNCHECKED")
                    fresh_state = "exception_without_receipt"
            else:
                # Cached mail alone (or any other transport) never
                # satisfies the operative GitHub leg.
                refuse("GITHUB_UNCHECKED")
                fresh_state = "not_github"
            if fresh_state == "ok":
                for key in ("newest_ruling_disposition",
                            "director_disposition",
                            "keeper_disposition"):
                    if fresh.get(key) in _HOLD_DISPOSITIONS:
                        refuse("AUTHORITY_HOLD")
                        fresh_state = "hold"
                        break
        legs["authority_freshness"] = {"state": fresh_state}

        # --- post-merge + fresh-clone legs (phase "post" only) -------
        if phase == "post":
            post = bundle.get("post_merge")
            if not isinstance(post, dict):
                refuse("BUNDLE_INCOMPLETE")
                legs["post_merge"] = {"state": "incomplete"}
            else:
                post_state = "ok"
                merge_commit = post.get("merge_commit")
                if post.get("merged") is not True \
                        or merge_commit is None \
                        or merge_commit != post.get("expected_merge_commit") \
                        or post.get("main_head_after") != merge_commit:
                    refuse("POST_MERGE_MISMATCH")
                    post_state = "refused"
                post_checks = post.get("post_checks")
                if not isinstance(post_checks, list):
                    refuse("BUNDLE_INCOMPLETE")
                    post_state = "incomplete"
                else:
                    for chk in post_checks:
                        if not isinstance(chk, dict) \
                                or chk.get("status") != "completed" \
                                or chk.get("conclusion") != "success":
                            refuse("POST_MERGE_MISMATCH")
                            post_state = "refused"
                            break
                legs["post_merge"] = {"state": post_state,
                                      "merge_commit": merge_commit}
            fc = bundle.get("fresh_clone")
            if not isinstance(fc, dict) or fc.get("ran") is not True:
                refuse("FRESH_CLONE_MISSING")
                legs["fresh_clone"] = {"state": "missing"}
            elif fc.get("result") != "success":
                refuse("FRESH_CLONE_FAILED")
                legs["fresh_clone"] = {"state": "failed"}
            elif isinstance(post, dict) \
                    and fc.get("revision") != post.get("merge_commit"):
                refuse("FRESH_CLONE_REVISION")
                legs["fresh_clone"] = {"state": "wrong_revision"}
            else:
                legs["fresh_clone"] = {"state": "ok"}

        if refusals:
            return _refused(refusals, legs)
        return {"verdict": "RECONCILED", "refusals": [], "legs": legs}
    except Exception:
        # Fail-closed: the reconciler never raises.
        return _refused(["BUNDLE_INCOMPLETE"], legs)


def main():
    ap = argparse.ArgumentParser(
        description="Independent certification runner "
                    "(DIR-2026-11-02-CONSOLIDATED-R1 item 2).")
    ap.add_argument("--out", default=None,
                    help="output directory (default: "
                         "certification_run_<UTC timestamp> "
                         "under the current directory)")
    ap.add_argument("--reconcile", default=None, metavar="BUNDLE_JSON",
                    help="SM-07 gate reconciliation only: read one "
                         "evidence-bundle JSON file, print the "
                         "reconcile_gate verdict as JSON, and exit "
                         "(0 = RECONCILED, 1 = REFUSED); the full "
                         "certification run is skipped")
    args = ap.parse_args()

    if args.reconcile is not None:
        import json
        try:
            with open(args.reconcile) as fh:
                bundle = json.load(fh)
        except Exception as exc:
            bundle = None
            print(f"[reconcile] bundle unreadable: {exc}",
                  file=sys.stderr)
        verdict = reconcile_gate(bundle)
        print(json.dumps(verdict, indent=2, sort_keys=True))
        return 0 if verdict.get("verdict") == "RECONCILED" else 1

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
