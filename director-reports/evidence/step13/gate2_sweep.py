#!/usr/bin/env python3
"""Gate 2 — full pairwise sweep (S1 battery), block-resumable.

9,900 ordered pairs (A != B) in 100 decade blocks + 100
identity rows under the R1 idempotence lens. Each block is
written as its own ledger file; existing block files are
skipped (resume-safe after interruption). Classifier v2:
pilot precedence + per-Dell designed-error table +
pair-context NOT_POSSIBLE reasons (R2) + UNIQUE candidates.
"""
import importlib.util
import json
import os
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "p1", os.path.join(HERE, "gate1_pilot.py"))
p1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p1)
g0 = p1.g0

from form.mandell.executor import execute_seed  # noqa: E402

OWNER = "Gate2Sweep"
OUTDIR = os.path.join(HERE, "sweep")
os.makedirs(OUTDIR, exist_ok=True)
CENSUS = p1.CENSUS
INV = p1.INV

DESIGNED_PREFIXES = (
    "acceptance_policy_denied", "bridge_unavailable",
    "embed_unavailable", "catch_illegal", "commit_without_try",
    "commit_illegal", "revert_illegal", "unrelated_revert",
    "delete_missing", "patch_miss", "scope_unknown",
    "replace_occupied", "replace_missing", "malformed_relation",
    "self_relation",
    "invalid_limit", "nonfinite_weight", "alias_missing",
    "alias_cycle", "malformed_composition", "compose_cycle",
    "compose_depth", "missing_source", "bound_reached",
    "rollback", "assert_fail", "guard_block", "move_missing",
    "type_mismatch", "empty", "copy_missing", "group_missing",
)


def designed(err):
    e = (err or "")
    return any(e.startswith(p) for p in DESIGNED_PREFIXES)


def chan_map(c):
    return {"selected": "core_ii.selected", "store": "core_ii.store",
            "weights": "core_ii.weights",
            "last_result": "core_ii.last_result",
            "groups": "core_ii.groups", "scope": "core_ii.scope",
            "plane": "plane"}.get(c, c)


def run_pair(a, b):
    g0.cleanup(OWNER)
    p = g0.build_world()
    s0 = g0.snapshot(p)
    t0 = time.perf_counter()
    ra = execute_seed(p, INV[a])
    s1 = g0.snapshot(p)
    rb = execute_seed(p, INV[b])
    s2 = g0.snapshot(p)
    dt = time.perf_counter() - t0
    row = {
        "pair": f"{a:02d}->{b:02d}",
        "a_seed": p1.scrub(INV[a]), "b_seed": p1.scrub(INV[b]),
        "a_ok": ra.get("ok"), "a_error": str(ra.get("error") or ""),
        "b_ok": rb.get("ok"), "b_error": str(rb.get("error") or ""),
        "a_writes_net": p1.net_channels(g0.diff(s0, s1)),
        "b_writes_net": p1.net_channels(g0.diff(s1, s2)),
        "store_b": p1.store_delta(s1["core_ii"]["store"],
                                  s2["core_ii"]["store"]),
        "secs": round(dt, 4),
    }
    row["class"], row["q1"], row["q2"] = classify(a, b, row, s1, s2)
    return row


def classify(a, b, row, s1, s2):
    B = f"{b:02d}"
    b_alone = CENSUS[B]
    plane_ids = set(s2["plane"].keys())
    sel_bad = [x for x in s2["core_ii"]["selected"]
               if x not in plane_ids]
    removed = row["store_b"]["removed"]
    # R3: a re-execution Dell (42 Retry) re-runs the immediately
    # preceding atom; when that atom (A) is a remover and it
    # executed, B inherits its remover status for attribution.
    removers = set(p1.REMOVERS)
    if B == "42" and row["a_ok"] and f"{a:02d}" in p1.REMOVERS:
        removers.add("42")
    bad_removed = [k for k in removed if B not in removers]
    if sel_bad or bad_removed:
        return ("DEFECT", "corruption",
                f"sel_bad={sel_bad} bad_removed={bad_removed}")
    if designed(row["a_error"]) or designed(row["b_error"]):
        return ("INTENDED_CLASH", "designed refusal (catalogued)",
                row["b_error"] or row["a_error"])
    if row["b_ok"] is False:
        if b_alone["ok"]:
            return ("SEAM_FAILURE",
                    "B succeeds standalone, fails after A",
                    row["b_error"])
        return ("NOT_POSSIBLE",
                f"pair err '{row['b_error']}'; standalone err "
                f"'{b_alone['error']}' (R2 pair-context)",
                row["b_error"])
    if row["a_ok"] is False:
        return ("A_FAILED", "A errored (undesigned); B ran",
                row["a_error"])
    a_writes = set(row["a_writes_net"])
    touched = {chan_map(c) for c in CENSUS[B]["sensitive_to"]}
    b_alone_net = {c for c in b_alone["writes"]
                   if c not in p1.ALLOWLIST}
    interaction = bool(a_writes & touched) or \
        set(row["b_writes_net"]) != b_alone_net
    extra = set(row["b_writes_net"]) - b_alone_net - a_writes
    if extra and interaction:
        return ("UNIQUE_CANDIDATE",
                "joint effect outside A-alone + B-alone channels",
                f"extra channels {sorted(extra)}")
    if interaction:
        return ("FUNCTIONAL",
                "B's behavior depends on A's effects",
                f"net B writes {row['b_writes_net']}")
    return ("FUNCTIONAL_INDEPENDENT", "no emergent requirement",
            f"net B writes {row['b_writes_net']}")


def run_identity(a):
    g0.cleanup(OWNER)
    p = g0.build_world()
    s0 = g0.snapshot(p)
    r1 = execute_seed(p, INV[a])
    s1 = g0.snapshot(p)
    r2 = execute_seed(p, INV[a])
    s2 = g0.snapshot(p)
    plane_ids = set(s2["plane"].keys())
    sel_bad = [x for x in s2["core_ii"]["selected"]
               if x not in plane_ids]
    e2 = str(r2.get("error") or "")
    if sel_bad:
        cls = "DEFECT"
    elif r2.get("ok"):
        cls = "IDENTITY_IDEMPOTENT"
    elif designed(e2):
        cls = "IDENTITY_HONEST_REFUSAL"
    else:
        cls = "IDENTITY_FAILURE"
    return {"pair": f"{a:02d}->{a:02d}", "class": cls,
            "first_ok": r1.get("ok"), "second_ok": r2.get("ok"),
            "second_error": e2,
            "q1": "idempotence lens (R1)", "q2": cls}


def main():
    g0.OWNER = OWNER
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    done = 0
    for ba in range(10):
        for bb in range(10):
            tag = f"block_{ba}{bb}"
            path = os.path.join(OUTDIR, tag + ".json")
            if os.path.exists(path):
                continue
            if which != "all" and tag != which:
                continue
            rows = []
            t0 = time.perf_counter()
            for a in range(ba * 10, ba * 10 + 10):
                for b in range(bb * 10, bb * 10 + 10):
                    if a != b:
                        rows.append(run_pair(a, b))
            with open(path, "w") as f:
                json.dump({"block": tag, "rows": rows,
                           "secs": round(time.perf_counter() - t0, 1)},
                          f, indent=0)
            done += 1
            print(f"{tag} done rows={len(rows)} "
                  f"classes={dict(Counter(r['class'] for r in rows))}",
                  flush=True)
    ipath = os.path.join(OUTDIR, "identity.json")
    if not os.path.exists(ipath) and which in ("all", "identity"):
        rows = [run_identity(a) for a in range(100)]
        with open(ipath, "w") as f:
            json.dump({"block": "identity", "rows": rows}, f, indent=0)
        print("identity done",
              dict(Counter(r["class"] for r in rows)), flush=True)
    g0.cleanup(OWNER)
    print("SWEEP RUN COMPLETE (blocks written this run:", done, ")")


if __name__ == "__main__":
    main()
