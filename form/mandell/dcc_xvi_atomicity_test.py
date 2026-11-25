#!/usr/bin/env python3
"""DCC-XVI-AR: crash/failure atomicity certification for supersession.

Certification rule under test: a supersession transaction may fail
before durable completion, and its receipt may fail after durable
completion, but a fresh process can NEVER observe a predecessor as
superseded unless the corresponding successor revision is completely
established.

Each scenario runs Process A (performs the operation, then either
crashes via os._exit at a precise boundary or raises via the injected
failure hook) followed by Process B (a NEW OS process: loads only
persisted state, inspects the revision chain, asserts).

Crash/failure matrix (durable state after fresh-process restore):

  crash_after_create   succ created(pending), crash before confirm
                       -> OLD COMPLETE (old active; succ pending, unlinked)
  crash_after_confirm  succ confirmed, crash before link preparation
                       -> OLD COMPLETE (old active; succ confirmed, unlinked)
  crash_before_commit  links prepared in memory, crash before the save
                       -> OLD COMPLETE (old active; succ confirmed, unlinked)
  crash_after_commit   links committed, crash before receipt
                       -> NEW COMPLETE (old superseded; succ confirmed+linked)
  inject_confirm       failure at successor confirmation -> rollback
                       -> OLD COMPLETE (old active; succ removed)
  inject_persist       failure at the final commit save -> rollback
                       -> OLD COMPLETE (old active; succ removed)
  inject_receipt       failure at receipt emission (post-commit)
                       -> NEW COMPLETE; retry is already_superseded, no dup
  success              no failure -> NEW COMPLETE

Forbidden in every scenario: predecessor superseded while the successor
is pending/unconfirmed/missing; one-way revision links; duplicate
revision numbers; the selector routing a non-active revision.

AUTONOMY = NO.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OWNER_BASE = "DCCXVI_AT"

SCENARIOS = [
    "crash_after_create",
    "crash_after_confirm",
    "crash_before_commit",
    "crash_after_commit",
    "inject_confirm",
    "inject_persist",
    "inject_receipt",
    "success",
]

# scenario -> (old_routable, succ_routable_or_None, old_lifecycle, succ_status_or_None)
EXPECT = {
    "crash_after_create": (True, False, "active", "pending"),
    "crash_after_confirm": (True, True, "active", "confirmed"),
    "crash_before_commit": (True, True, "active", "confirmed"),
    "crash_after_commit": (False, True, "superseded", "confirmed"),
    "inject_confirm": (True, None, "active", None),
    "inject_persist": (True, None, "active", None),
    "inject_receipt": (False, True, "superseded", "confirmed"),
    "success": (False, True, "superseded", "confirmed"),
}

_SCRIPT_A = """
import json, os, sys
sys.path.insert(0, __REPO__)
from pathlib import Path
from form.open import open_program
from form import persist_rest
from form.persist import _STATE_DIR
from form.dell_matrix.nursery import owner_nursery_path
from form.mandell import supersession as S

OWNER = __OWNER__
RES = __RES__
SCEN = __SCEN__

def wipe():
    for f in Path(_STATE_DIR).glob("*" + OWNER + "*"):
        try: f.unlink()
        except OSError: pass
    np_ = Path(owner_nursery_path(OWNER))
    try:
        if np_.is_file(): np_.unlink()
    except OSError: pass

wipe()
p = open_program(OWNER)
p.acceptance_policy.grant_opt_in("test", scope="test")
prop = p.nursery.add("atomicity base", words="atomicity base alpha")
ctx = p.make_review_context(prop.id, "test")
r = p.confirm_proposal(prop.id, _producer="test", _review_context=ctx)
assert r.get("ok"), r
aid = prop.id
persist_rest.save(p)

cell = {}

orig_add = p.nursery.add
def add_rec(*a, **k):
    s = orig_add(*a, **k)
    cell["succ_id"] = s.id
    return s
p.nursery.add = add_rec

orig_confirm = p.confirm_proposal
orig_ssave = S._save_nursery

def snap(op, at):
    open(RES, "w").write(json.dumps(
        {"op": op, "at": at, "aid": aid, "succ_id": cell.get("succ_id")}))

if SCEN == "crash_after_create":
    def crash_before_confirm(pid, **kwargs):
        persist_rest.save(p)
        snap("crashed", "before_confirm")
        os._exit(42)
    p.confirm_proposal = crash_before_confirm
    S.supersede_proposal(p, aid, "atomicity successor alpha", _producer="test")
elif SCEN == "crash_after_confirm":
    def crash_after_confirm(pid, **kwargs):
        # Forward all args (producer/context/operation); assert the
        # confirmation actually succeeds before injecting the crash.
        res = orig_confirm(pid, **kwargs)
        assert res.get("ok"), f"confirm must succeed before crash: {res}"
        persist_rest.save(p)
        snap("crashed", "after_confirm")
        os._exit(42)
    p.confirm_proposal = crash_after_confirm
    S.supersede_proposal(p, aid, "atomicity successor alpha", _producer="test")
elif SCEN == "crash_before_commit":
    def crash_before_save(prog):
        persist_rest.save(prog)
        snap("crashed", "before_commit")
        os._exit(42)
    S._save_nursery = crash_before_save
    S.supersede_proposal(p, aid, "atomicity successor alpha", _producer="test")
elif SCEN == "crash_after_commit":
    def crash_after_save(prog):
        orig_ssave(prog)
        persist_rest.save(prog)
        snap("crashed", "after_commit")
        os._exit(42)
    S._save_nursery = crash_after_save
    S.supersede_proposal(p, aid, "atomicity successor alpha", _producer="test")
elif SCEN in ("inject_confirm", "inject_persist", "inject_receipt"):
    point = SCEN.split("_", 1)[1]
    try:
        S.supersede_proposal(p, aid, "atomicity successor alpha", _fail_at=point, _producer="test")
        outcome = "returned_unexpectedly"
    except S.SupersedeError as e:
        outcome = "raised:" + e.reason
    persist_rest.save(p)
    snap(outcome, "injected_" + point)
elif SCEN == "success":
    res = S.supersede_proposal(p, aid, "atomicity successor alpha", _producer="test")
    assert res.get("ok"), res
    persist_rest.save(p)
    snap("ok", "success")
raise SystemExit(0)
"""

_SCRIPT_B = """
import json, sys
sys.path.insert(0, __REPO__)
from form.persist_rest import load
from form.mandell import supersession as S
from form.mandell.supersession import inspect_revision, is_revision_active
from form.mandell.knowledge_selector import select_for_context

OWNER = __OWNER__
RES = __RES__
SCEN = __SCEN__
EXP = __EXP__

res = json.load(open(RES))
aid, succ_id = res["aid"], res.get("succ_id")
p = load(OWNER)
p.acceptance_policy.grant_opt_in("test", scope="test")
checks = []
def check(name, cond):
    checks.append((name, bool(cond)))

old = inspect_revision(p, aid)
sprop = p.nursery.proposals.get(succ_id) if succ_id else None
succ = inspect_revision(p, succ_id) if succ_id else None

def truly_routable(pid):
    pr = p.nursery.proposals.get(pid)
    return (pr is not None and getattr(pr, "status", None) == "confirmed"
            and pid in p.cube.session.plane.units
            and inspect_revision(p, pid)["lifecycle_state"] == "active")

# ---- universal: the forbidden half-state can never appear ----
check("no_half_state",
      not (old["lifecycle_state"] == "superseded"
           and (sprop is None or getattr(sprop, "status", None) != "confirmed")))
if succ is not None and succ["supersedes_id"]:
    check("succ_link_agrees", old["superseded_by_id"] == succ_id)
if old["superseded_by_id"]:
    check("old_link_agrees",
          succ is not None and succ["supersedes_id"] == aid)
for rec in (old, succ):
    if rec is not None and rec["malformed_reason"] is None and rec["chain"]:
        nums = [inspect_revision(p, c)["revision_number"] for c in rec["chain"]]
        check("unique_revision_numbers", len(set(nums)) == len(nums))
sel = select_for_context(p, "atomicity alpha")
sel_ids = [e.get("id") for e in sel.get("selected", [])]
for sid in sel_ids:
    check("selector_only_active", inspect_revision(p, sid)["lifecycle_state"] == "active")
check("selected_subset_of_routable",
      all(truly_routable(sid) for sid in sel_ids))

# ---- scenario-specific durable expectations ----
exp_old_rout, exp_succ_rout, exp_old_life, exp_succ_status = EXP
check("old_lifecycle", old["lifecycle_state"] == exp_old_life)
check("old_routable", truly_routable(aid) == exp_old_rout)
if exp_succ_status is None:
    check("succ_absent", sprop is None)
else:
    check("succ_status", getattr(sprop, "status", None) == exp_succ_status)
    check("succ_routable", truly_routable(succ_id) == exp_succ_rout)
    if exp_old_life == "superseded":
        check("succ_linked", succ["supersedes_id"] == aid
              and succ["revision_root_id"] == aid
              and succ["revision_number"] == old["revision_number"] + 1)
        check("old_linked", old["superseded_by_id"] == succ_id
              and old["revision_root_id"] == aid)
        check("old_not_routable", not truly_routable(aid))
        check("succ_selected", succ_id in sel_ids)
        check("old_excluded", aid not in sel_ids)
    else:
        check("old_unlinked", old["superseded_by_id"] is None)
        if sprop is not None:
            check("succ_unlinked", succ["supersedes_id"] is None)

# ---- receipt-failure boundary: retry must refuse deterministically ----
if SCEN == "inject_receipt":
    check("receipt_op_raised", res["op"] == "raised:injected_failure")
    n_before = len(p.nursery.proposals)
    r2 = S.supersede_proposal(p, aid, "retry words", _producer="test")
    check("retry_refused", r2.get("ok") is False and r2.get("reason") == "already_superseded")
    check("retry_points_at_succ", r2.get("superseded_by_id") == succ_id)
    check("no_duplicate", len(p.nursery.proposals) == n_before)

failed = [n for n, ok in checks if not ok]
print(json.dumps({"passed": sum(1 for _, ok in checks if ok),
                  "total": len(checks), "failed": failed,
                  "pid": __import__("os").getpid(), "scenario": SCEN}))
raise SystemExit(0 if not failed else 1)
"""


def _fill(tpl: str, owner: str, res: str, scen: str, exp=None) -> str:
    out = (tpl.replace("__REPO__", repr(str(REPO)))
              .replace("__OWNER__", repr(owner))
              .replace("__RES__", repr(res))
              .replace("__SCEN__", repr(scen)))
    if exp is not None:
        out = out.replace("__EXP__", repr(exp))
    return out


def _wipe(owner: str) -> None:
    sys.path.insert(0, str(REPO))
    from form.persist import _STATE_DIR
    from form.dell_matrix.nursery import owner_nursery_path
    for f in Path(_STATE_DIR).glob(f"*{owner}*"):
        try:
            f.unlink()
        except OSError:
            pass
    np_ = Path(owner_nursery_path(owner))
    try:
        if np_.is_file():
            np_.unlink()
    except OSError:
        pass


def run_scenario(scen: str):
    """Run one crash/failure scenario; return (passed_names, failed_names)."""
    owner = f"{OWNER_BASE}_{scen}"
    passed, failed = [], []
    with tempfile.TemporaryDirectory(prefix="dccxvi_atomic_") as td:
        res = os.path.join(td, "res.json")
        pa = os.path.join(td, "a.py")
        pb = os.path.join(td, "b.py")
        Path(pa).write_text(_fill(_SCRIPT_A, owner, res, scen), encoding="utf-8")
        Path(pb).write_text(
            _fill(_SCRIPT_B, owner, res, scen, EXPECT[scen]), encoding="utf-8")
        ra = subprocess.run([sys.executable, pa], capture_output=True,
                            text=True, timeout=180)
        if scen.startswith("crash_"):
            ok_a = ra.returncode == 42
            detail_a = "" if ok_a else f"rc={ra.returncode} err={ra.stderr[-500:]}"
        else:
            ok_a = ra.returncode == 0 and os.path.isfile(res)
            detail_a = "" if ok_a else f"rc={ra.returncode} err={ra.stderr[-500:]}"
        if not ok_a:
            return passed, [f"{scen}.process_a:{detail_a}"]
        rb = subprocess.run([sys.executable, pb], capture_output=True,
                            text=True, timeout=180)
        if rb.returncode != 0 or not rb.stdout.strip():
            return passed, [f"{scen}.process_b:rc={rb.returncode} err={rb.stderr[-500:]}"]
        summary = json.loads(rb.stdout.strip().splitlines()[-1])
        total = summary["total"]
        passed = [f"{scen}.{i}" for i in range(summary["passed"])]
        failed = [f"{scen}.{n}" for n in summary["failed"]]
        assert summary["passed"] + len(summary["failed"]) == total
    _wipe(owner)
    return passed, failed


def main() -> int:
    passed_all, failed_all = [], []
    for scen in SCENARIOS:
        p_ok, p_fail = run_scenario(scen)
        passed_all.extend(p_ok)
        failed_all.extend(p_fail)
        tag = "ok" if not p_fail else "FAILED"
        print(f"[scenario] {scen}: {tag} ({len(p_ok)} checks)")
    print(f"\nDCC-XVI-ATOMIC: {len(passed_all)} passed, {len(failed_all)} failed")
    if failed_all:
        print("FAILURES:")
        for n in failed_all:
            print(f"  {n}")
    # Final n/m count line for the canonical regress runner.
    print(f"DCC-XVI-ATOMIC: {len(passed_all)}/{len(passed_all) + len(failed_all)}",
          flush=True)
    return 0 if not failed_all else 1


def smoke() -> bool:
    """Regress entry point: run the full crash/failure matrix once."""
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
