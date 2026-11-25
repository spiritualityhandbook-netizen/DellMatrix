"""72-28 (= SM-35) — Program/Nursery pair-atomicity as ONE closed proof.

Register gap (NBD Master Objective Register, 72-28): pair-atomic
crash proof between Program and Nursery staged writes (never a
hybrid) — not evidenced as one closed proof. Two DIFFERENT pair
paths exist and this suite does not collapse them:

CHECKPOINT PATH (the pair-atomic contract): commit_checkpoint
journals intent and byte-preserves the live pair BEFORE the seal's
first durable write; the pointer swap is the commit boundary;
persist_rest.load() runs recover_checkpoint_intent FIRST and
converges to the complete old pair or the complete target pair.
This suite crashes a genuine child OS process at each stage
boundary (the product's own _fail_at="crash_*" seams are literal
os._exit(42) at real boundaries) and classifies the pair a FRESH
process then exposes:
  CP1 crash_save_nursery -> OLD_ONLY, load rewrites nothing
  CP2 crash_save_program -> OLD_ONLY, load restores preserved pair
  CP3 crash_pointer      -> OLD_ONLY, load restores preserved pair
  CP4 crash_after_commit -> NEW_PAIR
  CP0 clean commit (control) -> NEW_PAIR
  Never HYBRID, never a load error, on the checkpoint path.

ORDINARY PATH (bounded statement, NOT a pair-atomic claim):
Program.save() and Nursery.save() are independent per-file atomic
writes; atomic_write's own contract disclaims cross-file
transactions and ordinary saves write no journal. A child that
dies between the two ordinary saves therefore leaves a HYBRID
live pair that a fresh load exposes as-is, rewriting nothing:
  H1-A nursery save lands, crash before program save -> HYBRID
  H1-B program save lands, crash before nursery save -> HYBRID
These two checks assert the CURRENT documented behavior as a
bounded statement (per-file atomicity only), pending a Director
ruling on whether a repair is warranted — they do not bless the
hybrid as coherent, and no repair is built by this circuit.
Q1 scope (load-recovery locking, W1/W2/W3) is untouched.

Evidence class: CROSS_PROCESS throughout (genuine child OS
processes for setup, crash and verdict; verdicts read from the
fresh process's loaded view and on-disk hashes, never from the
parent's memory). Unique owner per case; cleanup uses canonical
state paths only and fails loudly on error.

Run: python3 -m form.sm35_pair_atomic_test
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys

RESULTS = []
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        raise AssertionError(name)


# ---------------- state hygiene (canonical paths only) ----------------

def _state_dir():
    return os.path.join(ROOT, "form", "state")


def _cleanup(owner):
    sd = _state_dir()
    errors, hits = [], []
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"graph_{owner}.json", f"ideas_{owner}"):
        hits += glob.glob(os.path.join(sd, pat))
    # checkpoint-generation files carry a namespaced owner prefix
    # (safe_owner + "." + hash prefix); match this owner's only
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


def _run_child(args):
    return subprocess.run(
        [sys.executable, "-m", "form.sm35_pair_atomic_test"] + args,
        capture_output=True, text=True, cwd=ROOT, timeout=300)


# ---------------- children (genuine separate OS processes) ----------------

def _prop_by_label(p, label):
    for pr in p.nursery.proposals.values():
        if pr.label == label:
            return pr
    return None


def _child_setup(owner):
    from form import persist_rest
    from form.open import open_program
    p = open_program(owner)
    p.cube.session.plane.units.clear()
    pr = p.nursery.add("sm35-old", words="old")
    p.place("sm35-old-unit", "SM35 Old Unit", x=3.0, y=3.0)
    persist_rest.save(p)
    print(f"SETUP_OK old_pid={pr.id}")
    return 0


def _stage_new_pair_in_memory(p):
    """Stage the paired change WITHOUT any save: new proposal object
    inserted directly (nursery.add would autosave) + new unit placed.
    Proposal IDs are slugified by nursery.add, so lookups are by
    label, never by raw dict key."""
    import dataclasses
    old = _prop_by_label(p, "sm35-old")
    assert old is not None, "old proposal missing at staging time"
    new = dataclasses.replace(old, id=old.id + "__sm35new",
                              label="sm35-new", words="new",
                              status="pending")
    p.nursery.proposals[new.id] = new
    p.place("sm35-new-unit", "SM35 New Unit", x=4.0, y=4.0)


def _child_h1a(owner):
    # nursery half lands (add autosaves), program half never saved
    from form import persist_rest
    p = persist_rest.load(owner, activate=False)
    p.nursery.add("sm35-new", words="new")
    p.place("sm35-new-unit", "SM35 New Unit", x=4.0, y=4.0)
    sys.stdout.flush()
    os._exit(42)


def _child_h1b(owner):
    # program half lands, nursery half never saved
    from form import persist_rest
    p = persist_rest.load(owner, activate=False)
    _stage_new_pair_in_memory(p)
    persist_rest.save(p)
    sys.stdout.flush()
    os._exit(42)


def _child_checkpoint(owner, fail_at):
    from form import persist_rest
    from form.mandell.checkpoint_generation import commit_checkpoint
    p = persist_rest.load(owner, activate=False)
    _stage_new_pair_in_memory(p)
    if fail_at == "none":
        receipt = commit_checkpoint(p, generation_id="sm35gen1")
        print(f"COMMIT_OK {receipt.get('generation_id')}")
        return 0
    commit_checkpoint(p, generation_id="sm35gen1", _fail_at=fail_at)
    print("NO_CRASH")  # crash seams must never return
    return 3


def _child_view(owner):
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
            "new_prop": _prop_by_label(p, "sm35-new") is not None,
            "old_prop": _prop_by_label(p, "sm35-old") is not None,
            "new_unit": "sm35-new-unit" in p.cube.session.plane.units,
            "old_unit": "sm35-old-unit" in p.cube.session.plane.units,
        }
    except Exception as e:
        view = {"outcome": "error", "error": f"{type(e).__name__}: {e}"}
    view["pre_load_shas"] = pre
    view["post_load_shas"] = {"nursery_sha": sha(owner_nursery_path(owner)),
                              "program_sha": sha(_path(owner))}
    print("VIEW " + json.dumps(view))
    return 0


# ---------------- parent ----------------

def _classify(view):
    if view.get("outcome") != "loaded":
        return "LOAD_ERROR"
    if view["new_prop"] and view["new_unit"]:
        return "NEW_PAIR"
    if not view["new_prop"] and not view["new_unit"]:
        return "OLD_ONLY"
    return "HYBRID"


def _one_case(case_id, owner, mode, fail_at=None):
    _cleanup(owner)
    r = _run_child(["setup", owner])
    check(f"{case_id}: setup in child process",
          "SETUP_OK" in r.stdout, (r.stdout + r.stderr)[-300:])
    if mode == "checkpoint":
        r = _run_child(["checkpoint", owner, fail_at])
        if fail_at == "none":
            check(f"{case_id}: clean commit reported",
                  "COMMIT_OK" in r.stdout, (r.stdout + r.stderr)[-300:])
        else:
            check(f"{case_id}: crash observed at seam (rc=42)",
                  r.returncode == 42, f"rc={r.returncode}")
    else:
        r = _run_child([mode, owner])
        check(f"{case_id}: crash observed between saves (rc=42)",
              r.returncode == 42, f"rc={r.returncode}")
    r = _run_child(["view", owner])
    view = None
    for line in r.stdout.splitlines():
        if line.startswith("VIEW "):
            view = json.loads(line[5:])
    check(f"{case_id}: fresh-process view produced", view is not None,
          (r.stdout + r.stderr)[-300:])
    verdict = _classify(view)
    rewrote = view["pre_load_shas"] != view["post_load_shas"]
    _cleanup(owner)
    return verdict, view, rewrote


def run_all():
    # Part B first: the ordinary-path bounded statement.
    v, view, rewrote = _one_case("H1-A", "SM35H1A", "h1a")
    check("H1-A: ordinary nursery-first crash exposes HYBRID pair "
          "(per-file atomicity only — bounded statement)",
          v == "HYBRID", f"verdict={v}")
    check("H1-A: old pair members still present",
          view["old_prop"] and view["old_unit"])
    check("H1-A: fresh load rewrote no files (no journal exists)",
          rewrote is False)

    v, view, rewrote = _one_case("H1-B", "SM35H1B", "h1b")
    check("H1-B: ordinary program-first crash exposes HYBRID pair "
          "(per-file atomicity only — bounded statement)",
          v == "HYBRID", f"verdict={v}")
    check("H1-B: old pair members still present",
          view["old_prop"] and view["old_unit"])
    check("H1-B: fresh load rewrote no files (no journal exists)",
          rewrote is False)

    # Part A: the checkpoint pair-atomic contract, never hybrid.
    cp_wants = [
        ("CP1", "SM35CP1", "crash_save_nursery", "OLD_ONLY", False),
        ("CP2", "SM35CP2", "crash_save_program", "OLD_ONLY", True),
        ("CP3", "SM35CP3", "crash_pointer", "OLD_ONLY", True),
        ("CP4", "SM35CP4", "crash_after_commit", "NEW_PAIR", None),
        ("CP0", "SM35CP0", "none", "NEW_PAIR", None),
    ]
    for case_id, owner, fail_at, want, want_rewrote in cp_wants:
        v, view, rewrote = _one_case(case_id, owner, "checkpoint", fail_at)
        check(f"{case_id}: checkpoint verdict is {want} (never HYBRID)",
              v == want, f"verdict={v}")
        check(f"{case_id}: fresh load succeeded (no fail-closed error)",
              view["outcome"] == "loaded", str(view.get("error", "")))
        check(f"{case_id}: old pair members still present",
              view["old_prop"] and view["old_unit"])
        if want_rewrote is not None:
            check(f"{case_id}: load rewrite behavior matches contract "
                  f"(rewrote={want_rewrote})", rewrote is want_rewrote,
                  f"rewrote={rewrote}")

    print(f"SM35: {sum(1 for _, c in RESULTS if c)}/{len(RESULTS)} GREEN")


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"SM35 SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "setup":
        sys.exit(_child_setup(sys.argv[2]))
    elif mode == "h1a":
        _child_h1a(sys.argv[2])
    elif mode == "h1b":
        _child_h1b(sys.argv[2])
    elif mode == "checkpoint":
        sys.exit(_child_checkpoint(sys.argv[2], sys.argv[3]))
    elif mode == "view":
        sys.exit(_child_view(sys.argv[2]))
    else:
        run_all()
        sys.exit(0)
