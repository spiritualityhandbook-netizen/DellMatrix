#!/usr/bin/env python3
"""72-28 probes — Program/Nursery pair-atomicity (PROBE ONLY, no product change).

Run from a disposable clone of DellMatrix at main ed4ac00:
    python3 mr28_probe.py parent

Part B (H1, ORDINARY path): a paired logical change (new proposal in the
nursery file + new unit in the program file) is saved by the two ordinary
per-file saves in caller sequence; a genuine child process dies
(os._exit(42)) between the two saves. A fresh-process persist_rest.load()
then classifies the exposed pair:
    OLD_ONLY  = neither new marker visible
    NEW_PAIR  = both new markers visible
    HYBRID    = exactly one new marker visible  (H1 predicted for ordinary)
  H1-A: nursery save lands, crash before program save.
  H1-B: program save lands, crash before nursery save.

Part A (CHECKPOINT path): the same paired change is staged in memory and
commit_checkpoint is driven with its own _fail_at="crash_<stage>" seams
(literal os._exit(42) inside the product code at a real stage boundary):
  CP1 crash_save_nursery  (before the seal's first durable write)
  CP2 crash_save_program  (nursery staged write landed, program not)
  CP3 crash_pointer       (members+manifest sealed, pointer not swapped)
  CP4 crash_after_commit  (pointer swapped, journal cleared)
  CP0 control: successful commit_checkpoint, no crash.
Fresh-process load verdicts use the same classification; the checkpoint
contract predicts OLD_ONLY for CP1-CP3 and NEW_PAIR for CP4/CP0, never
HYBRID.

Children are genuine separate OS processes. Unique owner per case; the
parent cleans up only its own owners' state files (canonical names +
checkpoint-generation namespace files) and fails loudly on cleanup error.
Verdicts are read from the loaded view in a fresh process, not from the
parent's memory.
"""
import glob, json, os, shutil, subprocess, sys

ROOT = os.getcwd()
CASES = []  # (case_id, owner, mode)


def state_dir():
    return os.path.join(ROOT, "form", "state")


def cleanup(owner):
    sd = state_dir()
    errors = []
    pats = [f"program_{owner}.json", f"nursery_{owner}.json",
            f"graph_{owner}.json", f"ideas_{owner}"]
    hits = []
    for pat in pats:
        hits += glob.glob(os.path.join(sd, pat))
    # checkpoint-generation files carry a namespaced owner prefix
    # (safe_owner + "." + hash prefix); match this owner's namespace only
    for p in glob.glob(os.path.join(sd, "*")):
        base = os.path.basename(p)
        if base.startswith((f"current_{owner}.", f"gen_{owner}.",
                            f"nursery_{owner}.", f"program_{owner}.",
                            f"ideas_{owner}.", f"graph_{owner}.")) or \
           f"_{owner}." in base or f"checkpoint_{owner}" in base or \
           f"checkpoint_preserve_{owner}" in base:
            hits.append(p)
    for p in sorted(set(hits)):
        try:
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
        except OSError as e:
            errors.append(f"{p}: {e}")
    if errors:
        raise RuntimeError(f"cleanup failed for {owner}: {errors}")


def run_child(args, expect_exit=None):
    r = subprocess.run([sys.executable, os.path.abspath(__file__)] + args,
                       capture_output=True, text=True, cwd=ROOT, timeout=120)
    return r


# ---------------- children ----------------

def child_setup(owner):
    from form import persist_rest
    from form.open import open_program
    p = open_program(owner)
    p.cube.session.plane.units.clear()
    pr = p.nursery.add("mr28-old", words="old")
    p.place("mr28-old-unit", "MR28 Old Unit", x=3.0, y=3.0)
    persist_rest.save(p)
    print(f"SETUP_OK old_pid={pr.id}")
    return 0


def _prop_by_label(p, label):
    for pr in p.nursery.proposals.values():
        if pr.label == label:
            return pr
    return None


def _stage_new_pair_in_memory(p):
    """Stage the paired change WITHOUT any save: new proposal object in
    the nursery dict (nursery.add would autosave, so insert directly via
    dataclasses.replace of the old proposal) + new unit on the plane.
    Proposal IDs are slugified by nursery.add, so all lookups are by
    label, never by raw dict key."""
    import dataclasses
    old = _prop_by_label(p, "mr28-old")
    assert old is not None, "old proposal missing at staging time"
    new = dataclasses.replace(old, id=old.id + "__mr28new",
                              label="mr28-new", words="new",
                              status="pending")
    p.nursery.proposals[new.id] = new
    p.place("mr28-new-unit", "MR28 New Unit", x=4.0, y=4.0)


def child_h1a(owner):
    # nursery half lands (add autosaves), program half never saved
    from form import persist_rest
    p = persist_rest.load(owner, activate=False)
    p.nursery.add("mr28-new", words="new")
    p.place("mr28-new-unit", "MR28 New Unit", x=4.0, y=4.0)
    sys.stdout.flush()
    os._exit(42)


def child_h1b(owner):
    # program half lands, nursery half never saved
    from form import persist_rest
    p = persist_rest.load(owner, activate=False)
    _stage_new_pair_in_memory(p)
    persist_rest.save(p)
    sys.stdout.flush()
    os._exit(42)


def child_checkpoint(owner, fail_at):
    from form import persist_rest
    from form.mandell.checkpoint_generation import commit_checkpoint
    p = persist_rest.load(owner, activate=False)
    _stage_new_pair_in_memory(p)
    if fail_at == "none":
        receipt = commit_checkpoint(p, generation_id="mr28gen1")
        print(f"COMMIT_OK {receipt.get('generation_id')}")
        return 0
    commit_checkpoint(p, generation_id="mr28gen1", _fail_at=fail_at)
    print("NO_CRASH")  # crash seams must never return
    return 3


def child_view(owner):
    import hashlib
    from form import persist_rest
    from form.persist import _path
    from form.dell_matrix.nursery import owner_nursery_path
    def sha(path):
        if not os.path.isfile(path):
            return "absent"
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    pre = {"nursery_sha": sha(owner_nursery_path(owner)),
           "program_sha": sha(_path(owner))}
    try:
        p = persist_rest.load(owner, activate=False)
        view = {
            "outcome": "loaded",
            "new_prop": _prop_by_label(p, "mr28-new") is not None,
            "old_prop": _prop_by_label(p, "mr28-old") is not None,
            "new_unit": "mr28-new-unit" in p.cube.session.plane.units,
            "old_unit": "mr28-old-unit" in p.cube.session.plane.units,
        }
    except Exception as e:
        view = {"outcome": "error", "error": f"{type(e).__name__}: {e}"}
    view["pre_load_shas"] = pre
    view["post_load_shas"] = {"nursery_sha": sha(owner_nursery_path(owner)),
                              "program_sha": sha(_path(owner))}
    print("VIEW " + json.dumps(view))
    return 0


# ---------------- parent ----------------

def classify(view):
    if view.get("outcome") != "loaded":
        return "LOAD_ERROR"
    np_, nu = view["new_prop"], view["new_unit"]
    if np_ and nu:
        return "NEW_PAIR"
    if not np_ and not nu:
        return "OLD_ONLY"
    return "HYBRID"


def one_case(case_id, owner, mode, fail_at=None):
    cleanup(owner)
    r = run_child(["setup", owner])
    if "SETUP_OK" not in r.stdout:
        return {"case": case_id, "verdict": "SETUP_FAILED",
                "detail": (r.stdout + r.stderr)[-400:]}
    if mode == "checkpoint":
        r = run_child(["checkpoint", owner, fail_at])
        if fail_at == "none":
            if "COMMIT_OK" not in r.stdout:
                return {"case": case_id, "verdict": "COMMIT_FAILED",
                        "detail": (r.stdout + r.stderr)[-400:]}
        elif r.returncode != 42:
            return {"case": case_id, "verdict": "CRASH_NOT_OBSERVED",
                    "rc": r.returncode, "detail": (r.stdout + r.stderr)[-400:]}
    else:
        r = run_child([mode, owner])
        if r.returncode != 42:
            return {"case": case_id, "verdict": "CRASH_NOT_OBSERVED",
                    "rc": r.returncode, "detail": (r.stdout + r.stderr)[-400:]}
    r = run_child(["view", owner])
    view = None
    for line in r.stdout.splitlines():
        if line.startswith("VIEW "):
            view = json.loads(line[5:])
    if view is None:
        return {"case": case_id, "verdict": "VIEW_FAILED",
                "detail": (r.stdout + r.stderr)[-400:]}
    verdict = classify(view)
    files_changed_by_load = (view["pre_load_shas"] != view["post_load_shas"])
    out = {"case": case_id, "verdict": verdict, "view": view,
           "load_rewrote_files": files_changed_by_load}
    cleanup(owner)
    return out


def parent():
    results = []
    plan = [
        ("H1-A", "MR28H1A", "h1a", None),
        ("H1-B", "MR28H1B", "h1b", None),
        ("CP1", "MR28CP1", "checkpoint", "crash_save_nursery"),
        ("CP2", "MR28CP2", "checkpoint", "crash_save_program"),
        ("CP3", "MR28CP3", "checkpoint", "crash_pointer"),
        ("CP4", "MR28CP4", "checkpoint", "crash_after_commit"),
        ("CP0", "MR28CP0", "checkpoint", "none"),
    ]
    for case_id, owner, mode, fail_at in plan:
        res = one_case(case_id, owner, mode, fail_at)
        results.append(res)
        print(f"{case_id}: {res['verdict']}", flush=True)
    print("RESULTS_JSON " + json.dumps(results, indent=1))
    return 0


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "parent":
        sys.exit(parent())
    elif mode == "setup":
        sys.exit(child_setup(sys.argv[2]))
    elif mode == "h1a":
        child_h1a(sys.argv[2])
    elif mode == "h1b":
        child_h1b(sys.argv[2])
    elif mode == "checkpoint":
        sys.exit(child_checkpoint(sys.argv[2], sys.argv[3]))
    elif mode == "view":
        sys.exit(child_view(sys.argv[2]))
    else:
        print(f"unknown mode {mode}")
        sys.exit(2)
