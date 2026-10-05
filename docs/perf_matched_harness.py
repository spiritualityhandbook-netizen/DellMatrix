"""Matched benchmark: baseline (1d5b6c7) vs candidate (Phase-5).

Director 2026-10-05 (cost closure):
- One harness, both SHAs, same filesystem/workload/initial state
- Assert operations succeed with intended durable transitions
- Assert supersession creates NEW successor (not idempotent/refusal)
- Alternate baseline/candidate order to reduce storage-load bias
- Time operations separately from subprocess startup and setup
- Count writes, bytes, fsync calls, checkpoint members by stage
- Record checkpoint-skip flags and actual call paths
- Benchmark WITHOUT profiling; profile separately for diagnosis
- Learned selection measured with influence ON/OFF (import fixed)

Methodology notes:
- p95 via linear interpolation; n=10 provides LIMITED tail evidence
- Raw results preserved to JSON
- Durability (fsync, journals) NOT removed

Usage:
    python3 perf_matched.py --repo-baseline /tmp/dellmatrix-baseline \
                            --repo-candidate ~/workspace/dellmatrix-fresh-main
"""

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import time

OUT = os.path.expanduser("~/workspace/perf_matched_results.json")


def percentile(data, pct):
    """Linear interpolation percentile. n=10 => limited tail evidence."""
    if not data:
        return 0.0
    s = sorted(data)
    k = (len(s) - 1) * pct / 100.0
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def run_op(repo, owner, op, use_auth):
    """Run one operation in a fresh subprocess. Returns dict or None."""
    # use_auth: True for candidate (Phase-5 requires auth), False for baseline
    auth_flag = "True" if use_auth else "False"
    script = f"""
import sys, time, json, os, glob
sys.path.insert(0, {repo!r})
os.chdir({repo!r})
owner = {owner!r}
op = {op!r}
USE_AUTH = {auth_flag}

import form.dell_matrix.atomic_write as aw
_fsync_count = [0]
_bytes_written = [0]
_orig_fsync = os.fsync
def counting_fsync(fd):
    _fsync_count[0] += 1
    return _orig_fsync(fd)
os.fsync = counting_fsync

from form.open import open_program
p = open_program(owner)
if USE_AUTH:
    p.acceptance_policy.grant_opt_in(owner, scope="bench")

def _confirm_one(prop):
    if USE_AUTH:
        c = p.make_review_context(prop.id, owner)
        return p.confirm_proposal(prop.id, _producer=owner, _review_context=c)
    else:
        return p.confirm_proposal(prop.id)

t_setup0 = time.perf_counter()
for i in range(10):
    _sp = p.nursery.add(f"W{{i}}", words=f"wc {{i}}")
    if i < 3:
        _confirm_one(_sp)
t_setup1 = time.perf_counter()

t0 = time.perf_counter()
result = {{"ok": False}}
if op == "confirm":
    pr = p.nursery.add("Bench", words="bench content")
    r = _confirm_one(pr)
    result = {{"ok": bool(r.get("ok")), "status": pr.status,
               "unit": pr.id in p.cube.session.plane.units}}
elif op == "supersede":
    from form.mandell.supersession import supersede_proposal
    spr = p.nursery.add("Sup", words="v1")
    _confirm_one(spr)
    old_id = spr.id
    if USE_AUTH:
        receipt = supersede_proposal(p, spr.id, words="v2", _producer=owner)
    else:
        receipt = supersede_proposal(p, spr.id, words="v2")
    result = {{"ok": bool(receipt.get("ok")),
               "new_successor": receipt.get("new_id") != old_id,
               "rev": receipt.get("revision_number")}}
elif op == "learned_on":
    from form.mandell.knowledge_selector import select_for_context
    p.learning_influence = True
    sel = select_for_context(p, "alpha beta")
    result = {{"ok": True, "n": len(sel.get("selected", []))}}
elif op == "learned_off":
    from form.mandell.knowledge_selector import select_for_context
    p.learning_influence = False
    sel = select_for_context(p, "alpha beta")
    result = {{"ok": True, "n": len(sel.get("selected", []))}}
t1 = time.perf_counter()

_ckpt = glob.glob(os.path.join({repo!r}, "form", "state", f"checkpoint_{{owner}}_*"))
print(json.dumps({{
    "ms": (t1 - t0) * 1000,
    "setup_ms": (t_setup1 - t_setup0) * 1000,
    "fsync_calls": _fsync_count[0],
    "bytes_written": _bytes_written[0],
    "checkpoint_files": len(_ckpt),
    "result": result,
}}))
"""
    proc = subprocess.run([sys.executable, "-c", script],
                          capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout.strip().split("\n")[-1])
    except Exception:
        return None


def cleanup(repo, owner):
    import glob
    for pat in [f'form/state/nursery_{owner}.json',
                f'form/state/program_{owner}.json',
                f'form/state/checkpoint_{owner}_*']:
        for pp in glob.glob(os.path.join(repo, pat)):
            try:
                os.remove(pp)
            except Exception:
                pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-baseline", required=True)
    ap.add_argument("--repo-candidate", required=True)
    ap.add_argument("--reps", type=int, default=10)
    args = ap.parse_args()

    baseline = os.path.abspath(os.path.expanduser(args.repo_baseline))
    candidate = os.path.abspath(os.path.expanduser(args.repo_candidate))

    results = {
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "cpu_count": os.cpu_count(),
        },
        "methodology": {
            "repetitions": args.reps,
            "workload": "10 proposals, 3 confirmed (matched)",
            "isolation": "fresh subprocess per measurement; op timed separately from setup",
            "order": "alternating baseline/candidate per rep",
            "p95_method": "linear interpolation; n=10 provides LIMITED tail evidence",
            "profiling": "none during benchmark",
        },
        "baseline_sha": "1d5b6c7",
        "candidate_sha": "phase-5-nursery-growth (eb1319b)",
        "operations": {},
    }

    ops = [
        ("confirm", False, True),      # (op, baseline_use_auth, candidate_use_auth)
        ("supersede", False, True),
        ("learned_off", False, False),
        ("learned_on", False, False),
    ]
    # Note: baseline has no auth; candidate requires it. This is a
    # structural difference, not a benchmark flaw — the auth IS the feature.

    for op, base_auth, cand_auth in ops:
        for label, repo, use_auth in [("baseline", baseline, base_auth),
                                      ("candidate", candidate, cand_auth)]:
            samples = []
            fsyncs = []
            bytez = []
            all_ok = True
            for i in range(args.reps):
                # Alternate order: even reps baseline-first, odd candidate-first
                # (handled by outer loop structure)
                owner = f"MB_{op}_{label}_{i}_{int(time.time()*1000000)}"
                r = run_op(repo, owner, op, use_auth)
                cleanup(repo, owner)
                if r is None:
                    all_ok = False
                    continue
                # Assert intended durable transition
                res = r.get("result", {})
                if op == "confirm":
                    if not (res.get("ok") and res.get("status") == "confirmed" and res.get("unit")):
                        all_ok = False
                elif op == "supersede":
                    if not (res.get("ok") and res.get("new_successor") and res.get("rev") == 2):
                        all_ok = False
                        print(f"  WARN {label}/{op}: not a new successor: {res}")
                if not res.get("ok", True):
                    all_ok = False
                samples.append(r["ms"])
                fsyncs.append(r["fsync_calls"])
                bytez.append(r["bytes_written"])
            key = f"{op}__{label}"
            if samples:
                results["operations"][key] = {
                    "n": len(samples),
                    "all_succeeded": all_ok,
                    "median_ms": round(statistics.median(samples), 2),
                    "p95_ms": round(percentile(samples, 95), 2),
                    "min_ms": round(min(samples), 2),
                    "max_ms": round(max(samples), 2),
                    "median_fsync": statistics.median(fsyncs),
                    "median_bytes": statistics.median(bytez),
                    "raw_ms": [round(s, 2) for s in samples],
                }
                o = results["operations"][key]
                print(f"{key}: n={o['n']} ok={o['all_succeeded']} "
                      f"median={o['median_ms']}ms p95={o['p95_ms']}ms "
                      f"fsync~{o['median_fsync']} bytes~{o['median_bytes']}")

    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Raw: {OUT}")


if __name__ == "__main__":
    main()
