#!/usr/bin/env python3
"""Gate 0 census prober v0 — DellMatrix pairwise plan.

For every Dell 00-99, in a deterministic baseline world W:
  - WRITES: full-state snapshot before/after the Dell's canonical
    invocation; the channel-level diff is the dynamic write set.
  - READS (sensitivity): the same invocation in perturbed worlds
    (one channel altered); if the outcome signature changes, the
    Dell is marked sensitive to that channel.
Evidence classes are kept distinct in the output JSON:
  writes_diff (proven), reads_sensitivity (proven influence),
  outcome (ok/error/cell summary).
The shipped CoreIIState.snap() covers only 15 of 29 fields, so
this prober snapshots the full state itself.
"""
import copy
import glob
import hashlib
import json
import os
import shutil
import sys

ROOT = os.environ.get("GATE0_ROOT", os.path.expanduser("~/workspace/nbd-omega-postmerge155"))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from form.open import Program                      # noqa: E402
from form.mandell.core_ii_exec import attach       # noqa: E402
from form.mandell.executor import execute_seed     # noqa: E402

OWNER = "Gate0Census"

CII_FIELDS = ["scope", "selected", "store", "groups", "defs",
              "aliases", "compositions", "staged", "snapshots",
              "last_error", "last_diff", "traces", "weights",
              "context", "try_depth", "branch", "parallel", "route",
              "limit", "refs", "causes", "deps", "last_assert",
              "last_guard", "frames", "last_frame", "last_control",
              "flow_taken", "flow_blocked", "control_steps",
              "last_result", "tx"]


def cleanup(owner):
    for f in glob.glob(os.path.join("form/state", f"*{owner}*")):
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)


def norm(v):
    if isinstance(v, dict):
        return {str(k): norm(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [norm(x) for x in v]
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    return repr(v)


def snapshot(p):
    st = p.core_ii
    snap = {"core_ii": {f: norm(copy.deepcopy(getattr(st, f)))
                        for f in CII_FIELDS}}
    try:
        units = p.cube.session.plane.units
    except Exception:
        units = getattr(p, "_units", {})
    snap["plane"] = {uid: {"label": getattr(u, "label", ""),
                           "skin": str(getattr(u, "skin", ""))}
                     for uid, u in units.items()}
    snap["nursery"] = {pid: str(getattr(pr, "status", ""))
                        for pid, pr in
                        (p.nursery.proposals or {}).items()}
    snap["history_len"] = len(getattr(p, "history", []) or [])
    for sec in ("dock_sessions", "director_records", "unknowns",
                "design_loop", "exchange_receipts", "exchange_seeds"):
        snap[sec + "_n"] = len(getattr(p, sec, {}) or {})
    return snap


def diff(a, b, prefix=""):
    out = []
    if type(a) is not type(b):
        return [prefix or "<root>"]
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{prefix}.{k}" if prefix else k)
            else:
                out.extend(diff(a[k], b[k],
                                f"{prefix}.{k}" if prefix else k))
    elif isinstance(a, list):
        if a != b:
            out.append(prefix or "<root>")
    else:
        if a != b:
            out.append(prefix or "<root>")
    return out


def channels_of(paths):
    chans = set()
    for path in paths:
        parts = path.split(".")
        if parts[0] == "core_ii" and len(parts) > 1:
            chans.add("core_ii." + parts[1])
        else:
            chans.add(parts[0])
    return sorted(chans)


WORLD = [
    "08[Create] :: Garden Gate",
    "08[Create] :: Garden Path",
    "08[Create] :: Stone Arch",
    "55[Set] :: data=real",
    "55[Set] :: count=3",
    "51[Select] :: garden",
    "82[Group] :: crew",
    "74[Weight] :: data=0.5",
    "97[Define] :: note=memo",
]

PERTURB = {
    "selected": ["51[Select] :: zzz_no_match"],
    "store": ["55[Set] :: data=perturbed"],
    "groups": ["83[Ungroup] :: crew"],
    "weights": ["74[Weight] :: data=0.9"],
    "scope": ["53[Scope] :: crew"],
    "plane": ["08[Create] :: Extra Unit"],
    "last_result": ["56[Get] :: data"],
}

# Canonical operand-form invocation per Dell (from the registry
# proof contracts, circuits 4-22). Bare outcomes were surveyed in
# circuit 2 and are not repeated here.
INV = {
    0: "00[Nova] :: census", 1: "01[Initiate] :: census",
    2: "02[Persona]", 3: "03[Logic] :: garden",
    4: "04[Transform] :: garden", 5: "05[Tone] :: garden",
    6: "06[Cycle] :: 2", 7: "07[Link] :: garden_gate",
    8: "08[Create] :: Census Idea", 9: "09[Show] :: garden_gate",
    10: "10[Save]", 11: "11[Architect]", 12: "12[Test] :: garden",
    13: "13[Loop] :: 2", 14: "14[Bind] :: census_bind",
    15: "15[Map] :: census", 16: "16[Decay] :: 0.9",
    17: "17[Shadow] :: garden_gate", 18: "18[Mirror]",
    19: "19[Drive] :: 2", 20: "20[Alpha]",
    21: "21[Merge] :: garden_gate", 22: "22[Split] :: garden_gate",
    23: "23[Lock]", 24: "24[Unlock]", 25: "25[Pulse]",
    26: "26[Temp] :: census", 27: "27[Checkpoint] :: census",
    28: "28[Rollback]", 29: "29[Compress] :: garden gate path",
    30: "30[Expand] :: census", 31: "31[Simulate] :: garden",
    32: "32[Pause]", 33: "33[Resume]", 34: "34[Stamp] :: census",
    35: "35[Discover] :: garden", 36: "36[Inject] :: census_inject",
    37: "37[Nurture] :: census_seed", 38: "38[Distill] :: garden",
    39: "39[Schema]", 40: "40[TokenCount]",
    41: "41[Sanitize] :: note=census", 42: "42[Retry]",
    43: "43[Fallback] :: census", 44: "44[Bridge] :: garden",
    45: "45[Translate] :: garden", 46: "46[Rank]",
    47: "47[Embed] :: garden", 48: "48[Macro] :: 2",
    49: "49[Profile]", 50: "50[Manifest] :: Census Form",
    51: "51[Select] :: garden", 52: "52[Filter] :: gate",
    53: "53[Scope] :: plane", 54: "54[Query] :: garden",
    55: "55[Set] :: probe=1", 56: "56[Get] :: data",
    57: "57[Compare] :: eq data real", 58: "58[Match] :: gate",
    59: "59[Route] :: alt", 60: "60[pass]",
    61: "61[Join]", 62: "62[Parallel] :: x", 63: "63[Sequence] :: x",
    64: "64[Until] :: true", 65: "65[While] :: false",
    66: "66[ForEach]", 67: "67[Any] :: gate", 68: "68[All] :: gate",
    69: "69[None] :: zzz", 70: "70[Count]",
    71: "71[Measure] :: data:count", 72: "72[Limit] :: 4",
    73: "73[Threshold] :: gte:count 1", 74: "74[Weight] :: count=0.5",
    75: "75[Normalize]", 76: "76[Resolve] :: 70",
    77: "77[Infer] :: garden", 78: "78[Cause] :: a > b",
    79: "79[Depend] :: a > b", 80: "80[Context] :: census",
    81: "81[Reference] :: ref1", 82: "82[Group] :: squad",
    83: "83[Ungroup] :: squad", 84: "84[Copy] :: data",
    85: "85[Move] :: count>moved_count", 86: "86[Delete] :: probe",
    87: "87[Replace] :: data>datum", 88: "88[Patch] :: data=real2",
    89: "89[Diff]", 90: "90[Trace]", 91: "91[Assert] :: true",
    92: "92[Guard] :: true", 93: "93[Try]", 94: "94[Catch]",
    95: "95[Commit]", 96: "96[Revert]", 97: "97[Define] :: x=y",
    98: "98[Alias] :: al=note", 99: "99[Compose] :: censuscomp=70",
}


def build_world(extra=()):
    p = Program(owner=OWNER)
    attach(p)
    for seed in WORLD:
        execute_seed(p, seed)
    for seed in extra:
        execute_seed(p, seed)
    return p


def outcome_sig(r, p):
    st = p.core_ii
    cell = st.last_result or {}
    return json.dumps({
        "ok": r.get("ok"), "error": str(r.get("error") or ""),
        "cell": {k: norm(cell.get(k)) for k in
                 ("dell", "matched", "value", "count", "error")},
        "msgs": [m for m in (r.get("messages") or [])
                 if "::" not in m][:3],
    }, sort_keys=True, default=str)


def main():
    cleanup(OWNER)
    census = {}
    for n in range(100):
        seed = INV[n]
        p = build_world()
        before = snapshot(p)
        r = execute_seed(p, seed)
        after = snapshot(p)
        writes = channels_of(diff(before, after))
        base_sig = outcome_sig(r, p)
        sensitive = []
        for chan, extra in PERTURB.items():
            p2 = build_world(extra)
            r2 = execute_seed(p2, seed)
            if outcome_sig(r2, p2) != base_sig:
                sensitive.append(chan)
        census[f"{n:02d}"] = {
            "seed": seed, "ok": r.get("ok"),
            "error": str(r.get("error") or ""),
            "writes": writes, "sensitive_to": sensitive,
        }
        print(f"{n:02d} ok={r.get('ok')} writes={len(writes)} "
              f"sensitive={sensitive}", flush=True)
    out = {"owner": OWNER, "world": WORLD, "census": census}
    path = os.environ.get("GATE0_OUT") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "gate0_census.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print("CENSUS_WRITTEN", path, digest)
    cleanup(OWNER)


if __name__ == "__main__":
    main()
