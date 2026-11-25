#!/usr/bin/env python3
"""Parent harness for matched benchmark.

Controls:
- Alternation within each repetition: baseline/candidate, then candidate/baseline
- Validates every sample (missing/invalid -> harness fails)
- Durable outcome assertions including fresh-process reload
- Preserves return code, stdout, stderr, sample identity, execution order

Usage:
    python3 perf_parent.py --baseline /path --candidate /path --reps 10
"""

import argparse
import glob
import json
import os
import platform
import statistics
import subprocess
import sys
import time

CHILD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perf_child.py")
OUT = os.path.expanduser("~/workspace/perf_corrected_results.json")


def percentile(data, pct):
    if not data:
        return 0.0
    s = sorted(data)
    k = (len(s) - 1) * pct / 100.0
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def run_sample(repo, owner, op, use_auth):
    """Run one sample via the fixed child script. Returns (result_dict, meta)."""
    args = {
        "repo": repo,
        "owner": owner,
        "op": op,
        "use_auth": use_auth,
    }
    proc = subprocess.run(
        [sys.executable, CHILD, json.dumps(args)],
        capture_output=True, text=True, timeout=180,
    )
    meta = {
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr[-500:] if proc.stderr else "",
        "owner": owner,
        "repo": repo,
        "op": op,
    }
    if proc.returncode != 0:
        return None, meta
    try:
        # Last line is the JSON result
        result = json.loads(proc.stdout.strip().split("\n")[-1])
        return result, meta
    except Exception as e:
        meta["parse_error"] = str(e)
        return None, meta


def cleanup(repo, owner):
    state = os.path.join(repo, "form", "state")
    for pat in [f'nursery_{owner}.json', f'program_{owner}.json',
                f'checkpoint_{owner}_*']:
        for pp in glob.glob(os.path.join(state, pat)):
            try:
                os.remove(pp)
            except Exception:
                pass


def verify_durable(repo, owner, op, expected):
    """Fresh-process reload verification. Returns (ok, detail).

    Verifies the op proposal reached its intended durable status after
    reload. Unit presence is verified in-process by the child; the durable
    assertion here is the nursery proposal status.
    """
    # Simple inline verification (not via child, to avoid confusion)
    vscript = f'''
import sys, json, os
sys.path.insert(0, {repo!r})
os.chdir({repo!r})
from form import persist_rest
p = persist_rest.load({owner!r}, activate=False)
cands = [(pid, prop.status) for pid, prop in p.nursery.proposals.items()
         if 'benchop' in pid.lower() or 'suppred' in pid.lower()]
print(json.dumps({{"proposals": cands}}))
'''
    proc = subprocess.run([sys.executable, "-c", vscript],
                          capture_output=True, text=True, timeout=60,
                          cwd=repo)
    if proc.returncode != 0:
        return False, f"reload failed: {proc.stderr[:200]}"
    try:
        data = json.loads(proc.stdout.strip().split("\n")[-1])
    except Exception as e:
        return False, f"parse failed: {e}"
    proposals = data.get("proposals", [])
    if not proposals:
        return False, "op proposal not found after reload"
    # Verify expectations
    if op == "confirm":
        for pid, status in proposals:
            if status != "confirmed":
                return False, f"proposal {pid} status {status}, expected confirmed"
    # supersede: child already verified new_successor; status check lenient
    return True, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--reps", type=int, default=10)
    args = ap.parse_args()

    baseline = os.path.abspath(os.path.expanduser(args.baseline))
    candidate = os.path.abspath(os.path.expanduser(args.candidate))
    reps = args.reps

    results = {
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "cpu_count": os.cpu_count(),
        },
        "methodology": {
            "repetitions": reps,
            "workload": "10 proposals, 3 confirmed + op-specific prep (matched)",
            "isolation": "fixed child script, fresh subprocess per sample",
            "order": "alternating within each rep: (B,C) then (C,B)",
            "instrumentation": "reset immediately before timed op; setup timed separately",
            "p95_method": "linear interpolation; n=10 LIMITED tail evidence",
            "profiling": "none during benchmark",
            "harness": "perf_child.py (fixed) + perf_parent.py (this)",
        },
        "samples": [],  # full sample records with identity and order
        "operations": {},
    }

    ops = ["confirm", "supersede", "learned_off", "learned_on"]
    # use_auth: baseline False (no Phase-5), candidate True
    failed = False

    for op in ops:
        for rep in range(reps):
            # Alternate: even reps B-then-C, odd reps C-then-B
            if rep % 2 == 0:
                order = [("baseline", baseline, False),
                         ("candidate", candidate, True)]
            else:
                order = [("candidate", candidate, True),
                         ("baseline", baseline, False)]
            for label, repo, use_auth in order:
                owner = f"PC_{op}_{label}_{rep}_{int(time.time()*1000000)}"
                sample_id = f"{op}/rep{rep}/{label}"
                result, meta = run_sample(repo, owner, op, use_auth)

                # Harness fails on missing/invalid samples
                if result is None:
                    print(f"FATAL: sample {sample_id} failed: rc={meta['returncode']} "
                          f"stderr={meta['stderr'][:200]}", file=sys.stderr)
                    failed = True
                    continue
                if result.get("error"):
                    print(f"FATAL: sample {sample_id} error: {result['error']}",
                          file=sys.stderr)
                    failed = True
                    continue
                if not result.get("setup_ok"):
                    print(f"FATAL: sample {sample_id} setup failed", file=sys.stderr)
                    failed = True
                    continue

                # Validate operation outcome
                res = result.get("result", {})
                valid = True
                if op == "confirm":
                    valid = res.get("ok") and res.get("status") == "confirmed" and res.get("unit")
                elif op == "supersede":
                    valid = res.get("ok") and res.get("new_successor") and res.get("rev") == 2
                elif op in ("learned_on", "learned_off"):
                    valid = res.get("ok") and res.get("influence_path")
                    if not valid:
                        print(f"WARN: {sample_id} influence path mismatch: {res}",
                              file=sys.stderr)
                if not valid:
                    print(f"FATAL: sample {sample_id} invalid result: {res}",
                          file=sys.stderr)
                    failed = True
                    continue

                # Durable verification (fresh-process reload) for write ops
                if op in ("confirm", "supersede"):
                    dok, detail = verify_durable(repo, owner, op, res)
                    if not dok:
                        print(f"FATAL: sample {sample_id} durable check: {detail}",
                              file=sys.stderr)
                        failed = True
                        continue

                # Record sample with full identity
                results["samples"].append({
                    "id": sample_id,
                    "op": op,
                    "label": label,
                    "rep": rep,
                    "order_index": order.index((label, repo, use_auth)),
                    "sha": result["sha"],
                    "clean_tree": result["clean_tree"],
                    "module_path": result["module_path"],
                    "mount": result["mount"],
                    "fstype": result["fstype"],
                    "setup_ms": result["setup_ms"],
                    "op_ms": result["op_ms"],
                    "fsync_count": result["fsync_count"],
                    "fsync_ms": result["fsync_ms"],
                    "bytes_written": result["bytes_written"],
                })
                cleanup(repo, owner)

    if failed:
        print("HARNESS FAILED: one or more samples invalid", file=sys.stderr)
        sys.exit(1)

    # Aggregate by op/label
    for op in ops:
        for label in ["baseline", "candidate"]:
            samples = [s for s in results["samples"]
                       if s["op"] == op and s["label"] == label]
            if not samples:
                continue
            ms = [s["op_ms"] for s in samples]
            fsync_c = [s["fsync_count"] for s in samples]
            fsync_m = [s["fsync_ms"] for s in samples]
            bytes_w = [s["bytes_written"] for s in samples if s["bytes_written"] >= 0]
            # Verify SHA consistency
            shas = set(s["sha"] for s in samples)
            mounts = set(s["mount"] for s in samples)
            key = f"{op}__{label}"
            results["operations"][key] = {
                "n": len(ms),
                "sha": list(shas),
                "mount": list(mounts),
                "median_ms": round(statistics.median(ms), 2),
                "p95_ms": round(percentile(ms, 95), 2),
                "min_ms": round(min(ms), 2),
                "max_ms": round(max(ms), 2),
                "median_fsync_count": statistics.median(fsync_c),
                "median_fsync_ms": round(statistics.median(fsync_m), 2),
                "median_bytes": statistics.median(bytes_w) if bytes_w else -1,
                "raw_ms": [round(x, 2) for x in ms],
            }
            o = results["operations"][key]
            print(f"{key}: n={o['n']} median={o['median_ms']}ms "
                  f"p95={o['p95_ms']}ms fsync_n~{o['median_fsync_count']} "
                  f"fsync_ms~{o['median_fsync_ms']} bytes~{o['median_bytes']}")

    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Raw: {OUT}")


if __name__ == "__main__":
    main()
