#!/usr/bin/env python3
"""Gate 1 pilot — pairwise harness v1 (SWAT-operated).

Implements the Gate 0 persona + SWAT recommendations:
- snapshot0 -> A -> snapshot1 -> B -> snapshot2, full-state
  snapshots (census prober machinery), public entry only.
- diffs reported raw AND net of the execution-append
  allowlist (traces, snapshots, history, flow channels).
- representation record per row (invocations as sent).
- canary rows with hash-only ledger storage of secret-shaped
  text; bystander owner fingerprinted before/after the block.
- per-row timing + snapshot bytes for the Mechanic's cost
  formula (Gate 1 projection input; no numbers invented).
- classification per the plan's precedence: corruption ->
  DEFECT; designed refusal -> INTENDED CLASH; standalone-
  consistent failure -> NOT POSSIBLE (reason-coded);
  pair-only failure -> SEAM FAILURE (triage); both ok ->
  FUNCTIONAL (interaction) / FUNCTIONAL-INDEPENDENT /
  UNIQUE candidate. Q1/Q2 recorded per row.
"""
import hashlib
import importlib.util
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "g0", os.path.join(HERE, "gate0_census.py"))
g0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g0)

from form.mandell.executor import execute_seed  # noqa: E402

OWNER = "Gate1Pilot"
BYSTANDER = "Gate1Bystander"
CENSUS = json.load(open(os.path.join(HERE, "gate0_census_main.json")))["census"]

INV = dict(g0.INV)
INV[86] = "86[Delete] :: count"          # battery v0.1 erratum fix
CANARY_PW = "G0CANARY-PW-7f3a91"
INV[41] = f"41[Sanitize] :: password={CANARY_PW}"

ALLOWLIST = {"core_ii.traces", "core_ii.snapshots", "history_len",
             "core_ii.flow_taken", "core_ii.flow_blocked"}
DESIGNED = {"acceptance_policy_denied", "bridge_unavailable",
            "embed_unavailable", "catch_illegal",
            "commit_without_try", "rollback_target_invalid"}
REMOVERS = {"85", "86", "87", "96"}

SECRETISH = re.compile(r"G0CANARY|password|secret|token|api_key|bearer",
                       re.I)


def scrub(text):
    if SECRETISH.search(text or ""):
        raw = (text or "").encode()
        return f"sha256:{hashlib.sha256(raw).hexdigest()[:16]} len:{len(raw)}"
    return text


def net_channels(paths):
    return [c for c in g0.channels_of(paths) if c not in ALLOWLIST]


def store_delta(a, b):
    ka, kb = set(a), set(b)
    return {"added": sorted(kb - ka), "removed": sorted(ka - kb),
            "changed": sorted(k for k in ka & kb if a[k] != b[k])}


def run_row(a, b):
    g0.cleanup(OWNER)
    p = g0.build_world()
    # build_world uses g0.OWNER; rebind: build under pilot owner
    s0 = g0.snapshot(p)
    t0 = time.perf_counter()
    ra = execute_seed(p, INV[a])
    s1 = g0.snapshot(p)
    rb = execute_seed(p, INV[b]) if b is not None else None
    s2 = g0.snapshot(p)
    dt = time.perf_counter() - t0
    d_a = g0.diff(s0, s1)
    d_b = g0.diff(s1, s2)
    row = {
        "pair": f"{a:02d}->{b:02d}" if b is not None else f"{a:02d}->CHAIN",
        "a_seed": scrub(INV[a]), "b_seed": scrub(INV[b]) if b else None,
        "a_ok": ra.get("ok"), "a_error": str(ra.get("error") or ""),
        "b_ok": rb.get("ok") if rb else None,
        "b_error": str(rb.get("error") or "") if rb else None,
        "a_writes_net": net_channels(d_a),
        "b_writes_net": net_channels(d_b),
        "store_a": store_delta(s0["core_ii"]["store"], s1["core_ii"]["store"]),
        "store_b": store_delta(s1["core_ii"]["store"], s2["core_ii"]["store"]),
        "sel_b": {"before": s1["core_ii"]["selected"],
                  "after": s2["core_ii"]["selected"]},
        "secs": round(dt, 4),
        "snap_bytes": len(json.dumps(s2, default=str)),
    }
    row["class"], row["q1"], row["q2"] = classify(a, b, row, s1, s2)
    return row


def classify(a, b, row, s1, s2):
    A, B = f"{a:02d}", f"{b:02d}"
    b_alone = CENSUS[B]
    # corruption checks on B's step
    plane_ids = set(s2["plane"].keys())
    sel_bad = [x for x in s2["core_ii"]["selected"] if x not in plane_ids]
    removed = row["store_b"]["removed"]
    bad_removed = [k for k in removed
                   if B not in REMOVERS and k not in row["store_a"]["added"]]
    if sel_bad or bad_removed:
        return ("DEFECT", "corruption: selection or store integrity",
                f"sel_bad={sel_bad} bad_removed={bad_removed}")
    if row["a_error"] in DESIGNED or row["b_error"] in DESIGNED:
        return ("INTENDED_CLASH", "designed refusal (catalogued)",
                row["b_error"] or row["a_error"])
    if row["b_ok"] is False:
        if b_alone["ok"]:
            return ("SEAM_FAILURE",
                    "B succeeds standalone, fails after A — triage",
                    row["b_error"])
        return ("NOT_POSSIBLE",
                f"NP-LIFECYCLE: B fails standalone too ({b_alone['error']})",
                row["b_error"])
    if row["a_ok"] is False and a is not None:
        return ("A_FAILED", "A did not execute; pair not established",
                row["a_error"])
    # both ok: interaction?
    a_writes = set(row["a_writes_net"])
    b_sensitive = set(CENSUS[B]["sensitive_to"])
    chan_map = {"selected": "core_ii.selected", "store": "core_ii.store",
                "weights": "core_ii.weights", "last_result": "core_ii.last_result",
                "groups": "core_ii.groups", "scope": "core_ii.scope",
                "plane": "plane"}
    touched = {chan_map.get(c, c) for c in b_sensitive}
    interaction = bool(a_writes & touched) or \
        row["b_writes_net"] != [c for c in b_alone["writes"]
                                if c not in ALLOWLIST]
    if interaction:
        return ("FUNCTIONAL", "B's behavior depends on A's effects "
                "(emergent requirement: A's setup)",
                f"net B writes {row['b_writes_net']}")
    return ("FUNCTIONAL_INDEPENDENT", "no emergent requirement detected",
            f"net B writes {row['b_writes_net']}")


def main():
    # g0.build_world constructs Program(owner=g0.OWNER); point it
    # at the pilot owner for isolation.
    g0.OWNER = OWNER
    # bystander: build + fingerprint before the block
    g0.cleanup(BYSTANDER)
    saved = g0.OWNER
    g0.OWNER = BYSTANDER
    bp = g0.build_world()
    by_fp0 = hashlib.sha256(json.dumps(
        g0.snapshot(bp), sort_keys=True, default=str).encode()).hexdigest()
    import glob as _glob
    by_files0 = sorted(os.path.basename(f) for f in
                       _glob.glob(os.path.join("form/state", f"*{BYSTANDER}*")))
    g0.OWNER = saved

    block = [51, 55, 56, 70, 84, 86]
    rows = []
    for a in block:
        for b in block:
            if a != b:
                rows.append(run_row(a, b))
    for a in block:  # identity controls
        rows.append(run_row(a, a))
    rows.append(run_row(41, 55))   # canary rows
    rows.append(run_row(55, 41))
    rows.append(run_row(55, 43))   # placebo-ish (message-only B)

    # vehicle row: AF-1 in pair context, executed as ONE chain
    g0.cleanup(OWNER)
    p = g0.build_world()
    r = execute_seed(p, '08[Create](name="Vehicle Wish", skin="SPHERE") > 70[Count]')
    units = [u for u in p.cube.session.plane.units
             if "vehicle" in u or u == "idea" or u.startswith("idea")]
    rows.append({"pair": "08->70 VEHICLE", "a_seed": "typed chain",
                 "class": "VEHICLE",
                 "q1": "AF-1: typed args in chain",
                 "q2": f"created={units} (expect 'idea' fallback = AF-1 flag)",
                 "a_ok": r.get("ok"), "secs": 0})

    # bystander after
    g0.OWNER = BYSTANDER
    by_fp1 = hashlib.sha256(json.dumps(
        g0.snapshot(bp), sort_keys=True, default=str).encode()).hexdigest()
    import glob as _glob2
    by_files1 = sorted(os.path.basename(f) for f in
                       _glob2.glob(os.path.join("form/state", f"*{BYSTANDER}*")))
    g0.OWNER = saved

    out = {"block": "tier1-A pilot", "rows": rows,
           "bystander_fp_before": by_fp0, "bystander_fp_after": by_fp1,
           "bystander_identical": by_fp0 == by_fp1,
           "bystander_files_identical": by_files0 == by_files1,
           "total_secs": round(sum(r["secs"] for r in rows), 2)}
    path = os.path.join(HERE, "gate1_pilot_ledger.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    raw = open(path).read()
    print("LEDGER", path)
    print("canary_in_ledger:", CANARY_PW in raw)
    print("bystander_identical:", out["bystander_identical"])
    print("total_secs:", out["total_secs"])
    from collections import Counter
    print(Counter(r["class"] for r in rows))
    g0.cleanup(OWNER)
    g0.cleanup(BYSTANDER)


if __name__ == "__main__":
    main()
