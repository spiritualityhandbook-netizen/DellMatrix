"""Shared helpers for the Core I contract review probes.

Run with cwd = the worktree root (~/workspace/nbd-omega-corei) so
form/state resolves to the worktree's own state dir. Probes use
throwaway owners only and clean them by the af1-established
owner-scan pattern over canonical state paths.
"""
import glob
import hashlib
import json
import os
import re
import shutil

ROOT = os.path.expanduser("~/workspace/nbd-omega-corei")
EVDIR = os.path.expanduser(
    "~/workspace/goals/dellmatrix-capability-circuits/hidden_files/"
    "core_i_contract_review")
STATE_DIR = os.path.join(ROOT, "form", "state")
PROBE_OWNERS = ["CoreIRev", "CoreIRepl"]


def cleanup(owner):
    for f in glob.glob(os.path.join(STATE_DIR, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass


def state_snapshot(exclude_owners):
    snap = {}
    if not os.path.isdir(STATE_DIR):
        return snap
    for fn in sorted(os.listdir(STATE_DIR)):
        if any(o in fn for o in exclude_owners):
            continue
        p = os.path.join(STATE_DIR, fn)
        if os.path.isfile(p):
            with open(p, "rb") as fh:
                snap[fn] = hashlib.sha256(fh.read()).hexdigest()
        elif os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for x in files:
                    xp = os.path.join(root, x)
                    rel = os.path.relpath(xp, STATE_DIR)
                    with open(xp, "rb") as fh:
                        snap[rel] = hashlib.sha256(fh.read()).hexdigest()
    return snap


VOL_KEYS = {"ts", "generation_id", "compensating_generation_id",
            "created_at", "updated_at", "time", "timestamp"}


def scrub(obj):
    if isinstance(obj, dict):
        return {k: ("<V>" if k in VOL_KEYS else scrub(v))
                for k, v in obj.items()}
    if isinstance(obj, list):
        return [scrub(x) for x in obj]
    return obj


TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")


def norm_text(s):
    return TS_RE.sub("<TS>", str(s))


def _msgs(result):
    out = []
    for m in (result.get("messages") or []):
        m = str(m)
        if m.startswith("Mandell:") or m.startswith("English:"):
            continue  # seed echo lines carry the input text itself
        out.append(norm_text(m))
    return out


def witness(result, p):
    """Business-state witness: (ok, error, state digest, messages).

    Echo lines are excluded from messages (they reproduce the input,
    including typed args — echo is not consumption). Volatile fields
    (timestamps, generation ids) are scrubbed before comparison.
    """
    w = {}
    try:
        units = p.cube.session.plane.units
        if isinstance(units, dict):
            items = list(units.items())
        else:
            items = [(getattr(u, "id", str(i)), u)
                     for i, u in enumerate(units)]
        w["units"] = sorted(f"{uid}:{getattr(u, 'skin', '')}"
                            for uid, u in items)
    except Exception as exc:  # noqa: BLE001
        w["units"] = f"<err:{exc}>"
    try:
        w["store"] = {k: str(v) for k, v in
                      sorted((p.core_ii.store or {}).items())}
    except Exception:  # noqa: BLE001
        w["store"] = {}
    try:
        w["groups"] = sorted((p.core_ii.groups or {}).keys())
    except Exception:  # noqa: BLE001
        w["groups"] = []
    try:
        w["nursery_pending"] = p.nursery.summary().get("pending")
    except Exception:  # noqa: BLE001
        w["nursery_pending"] = None
    for attr in ("last_core_i", "last_stamp", "last_nurture",
                 "last_measure"):
        try:
            val = getattr(p, attr, None)
            w[attr] = scrub(json.loads(json.dumps(val, default=str)))
        except Exception:  # noqa: BLE001
            w[attr] = None
    try:
        w["history_len"] = len(getattr(p, "history", []) or [])
    except Exception:  # noqa: BLE001
        w["history_len"] = None
    return (bool(result.get("ok")), norm_text(result.get("error") or ""),
            json.dumps(scrub(w), sort_keys=True, default=str),
            json.dumps(_msgs(result)))
