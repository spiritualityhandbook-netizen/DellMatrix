#!/usr/bin/env python3
"""Track D planning census — READ-ONLY scan of every worktree's form/state.

Counts, per state dir and owner: Plane units (program files), Nursery
proposals by status, canonical Ideas (count + id shapes), graph log
entries + CONTAINS entries. Never writes. Checkpoints (_cp_) counted
separately. Output: JSON to stdout.
"""
import glob, json, os, re, sys
from collections import defaultdict

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"__error__": str(e)}

owners = defaultdict(lambda: {"units": 0, "program_files": 0, "checkpoints": 0,
                              "proposals": defaultdict(int), "ideas": 0,
                              "idea_id_shapes": defaultdict(int),
                              "graph_entries": 0, "graph_contains": 0,
                              "state_dirs": set()})
state_dirs = sorted(glob.glob(os.path.expanduser("~/workspace/*/form/state")) +
                    glob.glob(os.path.expanduser("~/workspace/form/state")))
for sd in state_dirs:
    for path in glob.glob(os.path.join(sd, "program_*.json")):
        base = os.path.basename(path)
        owner = base[len("program_"):-len(".json")]
        rec = owners[owner]; rec["state_dirs"].add(sd)
        if "_cp_" in owner:
            rec["checkpoints"] += 1
            continue
        rec["program_files"] += 1
        data = load_json(path)
        units = (((data or {}).get("plane") or {}).get("units") or {})
        rec["units"] += len(units)
    for path in glob.glob(os.path.join(sd, "nursery_*.json")):
        owner = os.path.basename(path)[len("nursery_"):-len(".json")]
        rec = owners[owner]; rec["state_dirs"].add(sd)
        data = load_json(path)
        props = data.get("proposals") if isinstance(data, dict) else None
        if isinstance(props, dict):
            items = props.values()
        elif isinstance(props, list):
            items = props
        else:
            items = []
        for p in items:
            if isinstance(p, dict):
                rec["proposals"][p.get("status", "?")] += 1
    for d in glob.glob(os.path.join(sd, "ideas_*")):
        if not os.path.isdir(d):
            continue
        owner = os.path.basename(d)[len("ideas_"):]
        rec = owners[owner]; rec["state_dirs"].add(sd)
        for fn in os.listdir(d):
            if fn.startswith("idea_") and fn.endswith(".json"):
                rec["ideas"] += 1
                data = load_json(os.path.join(d, fn))
                iid = (data or {}).get("id", "")
                rec["idea_id_shapes"]["uuid" if UUID_RE.match(str(iid)) else "non-uuid"] += 1
    for path in glob.glob(os.path.join(sd, "graph_*.json")):
        base = os.path.basename(path)
        if ".journal" in base:
            continue
        owner = base[len("graph_"):-len(".json")]
        rec = owners[owner]; rec["state_dirs"].add(sd)
        data = load_json(path)
        entries = data.get("relationships") if isinstance(data, dict) else None
        if isinstance(entries, list):
            rec["graph_entries"] += len(entries)
            rec["graph_contains"] += sum(1 for e in entries
                                          if isinstance(e, dict) and str(e.get("type")) in ("contains", "CONTAINS", "RelationshipType.CONTAINS"))

out = {}
for owner, rec in sorted(owners.items()):
    rec = dict(rec)
    rec["proposals"] = dict(rec["proposals"])
    rec["idea_id_shapes"] = dict(rec["idea_id_shapes"])
    rec["state_dirs"] = len(rec["state_dirs"])
    out[owner] = rec
summary = {
    "owners_total": len(out),
    "owners_with_units": sum(1 for r in out.values() if r["units"] > 0),
    "owners_with_ideas": sum(1 for r in out.values() if r["ideas"] > 0),
    "owners_with_both": sum(1 for r in out.values() if r["units"] > 0 and r["ideas"] > 0),
    "owners_units_no_ideas": sum(1 for r in out.values() if r["units"] > 0 and r["ideas"] == 0),
    "total_units": sum(r["units"] for r in out.values()),
    "total_ideas": sum(r["ideas"] for r in out.values()),
    "total_graph_contains": sum(r["graph_contains"] for r in out.values()),
}
print(json.dumps({"summary": summary, "owners": out}, indent=1, sort_keys=True))
