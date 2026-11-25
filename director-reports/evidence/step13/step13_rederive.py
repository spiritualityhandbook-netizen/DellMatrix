#!/usr/bin/env python3
"""Step 13 re-derivation overlay (classifier v4 dispositions).

Raw step13 sweep rows are evidence and are never edited.
This overlay records before/after for every changed row:

- R5 (Step 10 contract): 'ungroup_missing' is a designed
  refusal (Dell 83 named-missing refusal, STEP10_PACKET).
  In the historical classifier precedence, a designed error
  on A or B yields INTENDED_CLASH before the NOT_POSSIBLE /
  A_FAILED branches, and after the DEFECT branch (DEFECT
  count in the raw run is 0, so no row is overridden out
  of DEFECT).
- R6 (Step 6 B1 contract): 'enhance OFF' is the EnhanceGate
  designed refusal reason (form/dell_matrix/enhance_gate.py),
  surfaced honestly by Dell 16 Decay after Step 6. Same
  precedence argument as R5.
- Identity lens: a second-execution error that is a
  designed refusal (R5/R6) is IDENTITY_HONEST_REFUSAL
  (R4 precedent: 87->87 replace_missing).
- B=86 / B=42 baseline correction (Gate 2 R3/R4 precedent):
  the Gate 0 census standalone rows for 86 (and 41) were
  measured under pre-erratum invocations; recompute them
  under the battery invocations the sweep itself uses,
  overlay on a COPY of the step13 census, and re-run only
  the rows whose classification can change (B=86, B=42).
"""
import copy
import glob
import importlib.util
import json
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "sw13", os.path.join(HERE, "gate2_sweep.py"))
sw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sw)
g0 = sw.g0
p1 = sw.p1

from form.mandell.executor import execute_seed  # noqa: E402

DESIGNED_NEW = ("ungroup_missing", "enhance OFF")


def is_new_designed(err):
    e = err or ""
    return any(e.startswith(p) for p in DESIGNED_NEW)


def outcome_sig(res, p):
    st = p.core_ii
    return (res.get("ok"), str(res.get("error") or ""),
            len(st.selected), len(st.store),
            len(p.cube.session.plane.units))


def single_dell_census(dell):
    """Mirror of gate2_rederive.single_dell_census."""
    g0.cleanup(sw.OWNER)
    p = g0.build_world()
    s0 = g0.snapshot(p)
    res = execute_seed(p, sw.INV[dell])
    s1 = g0.snapshot(p)
    entry = {"dell": f"{dell:02d}", "ok": res.get("ok"),
             "error": str(res.get("error") or ""),
             "writes": g0.channels_of(g0.diff(s0, s1)),
             "sensitive_to": []}
    base = outcome_sig(res, p)
    names = [re.search(r"\[([^\]]+)\]",
                       sw.CENSUS[f"{i:02d}"]["seed"]).group(1)
             for i in range(100)]
    sens = []
    for other in range(100):
        g0.cleanup(sw.OWNER)
        p2 = g0.build_world()
        execute_seed(p2, sw.INV[other])
        res2 = execute_seed(p2, sw.INV[dell])
        if outcome_sig(res2, p2) != base:
            sens.append(names[other])
    entry["sensitive_to"] = sens
    return entry


def main():
    g0.OWNER = sw.OWNER
    raw = {}
    for f in sorted(glob.glob(os.path.join(HERE, "sweep",
                                           "block_*.json"))):
        for r in json.load(open(f))["rows"]:
            raw[r["pair"]] = r
    ident_raw = {r["pair"]: r for r in
                 json.load(open(os.path.join(
                     HERE, "sweep", "identity.json")))["rows"]}
    assert len(raw) == 9900 and len(ident_raw) == 100
    changes = []

    # --- B=86 / B=42 corrected-baseline re-run ---
    corrected = copy.deepcopy(sw.CENSUS)
    corr_info = {}
    for dell in (86, 41):
        e = single_dell_census(dell)
        corr_info[f"{dell:02d}"] = {
            "census_ok": sw.CENSUS[f"{dell:02d}"]["ok"],
            "census_error": sw.CENSUS[f"{dell:02d}"]["error"],
            "corrected_ok": e["ok"], "corrected_error": e["error"],
            "corrected_writes": e["writes"]}
        corrected[f"{dell:02d}"] = {
            "seed": sw.INV[dell], "ok": e["ok"],
            "error": e["error"], "writes": e["writes"],
            "sensitive_to": e["sensitive_to"]}
    sw.CENSUS = corrected
    final = dict(raw)
    for a in range(100):
        for b in (86, 42):
            if a == b:
                continue
            pair = f"{a:02d}->{b:02d}"
            new = sw.run_pair(a, b)
            if new["class"] != raw[pair]["class"]:
                changes.append({
                    "pair": pair, "before": raw[pair]["class"],
                    "after": new["class"],
                    "rule": "R86_41_BASELINE_CORRECTION",
                    "new_row": {k: new[k] for k in
                                ("a_ok", "a_error", "b_ok", "b_error",
                                 "q1", "q2")}})
            final[pair] = new
    g0.cleanup(sw.OWNER)

    # --- R5/R6 designed-prefix overlay on final classes ---
    for pair, r in sorted(final.items()):
        if r["class"] in ("NOT_POSSIBLE", "A_FAILED") and (
                is_new_designed(r.get("a_error")) or
                is_new_designed(r.get("b_error"))):
            changes.append({
                "pair": pair, "before": r["class"],
                "after": "INTENDED_CLASH",
                "rule": "R5_R6_DESIGNED_PREFIX",
                "a_error": r.get("a_error"), "b_error": r.get("b_error")})
            r = dict(r)
            r["class"] = "INTENDED_CLASH"
            r["class_overlay"] = "R5_R6_DESIGNED_PREFIX"
            final[pair] = r

    # --- identity overlay ---
    ident_final = dict(ident_raw)
    ident_changes = []
    for pair, r in sorted(ident_raw.items()):
        if r["class"] == "IDENTITY_FAILURE" and \
                is_new_designed(r.get("second_error")):
            ident_changes.append({
                "pair": pair, "before": r["class"],
                "after": "IDENTITY_HONEST_REFUSAL",
                "rule": "R5_R6_IDENTITY_DESIGNED",
                "second_error": r.get("second_error")})
            r = dict(r)
            r["class"] = "IDENTITY_HONEST_REFUSAL"
            r["class_overlay"] = "R5_R6_IDENTITY_DESIGNED"
            ident_final[pair] = r

    out = {
        "raw_pair_totals": dict(Counter(
            r["class"] for r in raw.values())),
        "final_pair_totals": dict(Counter(
            r["class"] for r in final.values())),
        "raw_identity_totals": dict(Counter(
            r["class"] for r in ident_raw.values())),
        "final_identity_totals": dict(Counter(
            r["class"] for r in ident_final.values())),
        "corrected_census": corr_info,
        "pair_changes": changes,
        "identity_changes": ident_changes,
        "final_rows": [final[f"{a:02d}->{b:02d}"]
                       for a in range(100) for b in range(100)
                       if a != b],
        "final_identity_rows": [ident_final[f"{a:02d}->{a:02d}"]
                                for a in range(100)],
    }
    path = os.path.join(HERE, "step13_rederived.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("pair changes:", len(changes))
    print("identity changes:", len(ident_changes))
    print("final pair totals:", out["final_pair_totals"])
    print("final identity totals:", out["final_identity_totals"])
    print("corrected census:", json.dumps(corr_info, indent=1))
    print("WROTE", path)


if __name__ == "__main__":
    main()
