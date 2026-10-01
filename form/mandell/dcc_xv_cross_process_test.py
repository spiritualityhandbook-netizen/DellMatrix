#!/usr/bin/env python3
"""DCC-XV cross-process persistence: literal two-OS-process certification.

PROCESS A builds an isolated fixture (root A, derived B, contextual grow),
saves, and exits completely. PROCESS B starts as an independent interpreter,
loads only from persisted state, and recomputes lineage / dependency /
routing evidence. This test exists so the recurring "same-interpreter
save;del;load" caveat can never silently return: a real process boundary
is exercised on every run.

25 checks in the ad-hoc proof; this permanent suite keeps a fast subset.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

REPO_ROOT = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(0, REPO_ROOT)

from form.persist import _STATE_DIR  # noqa: E402
from form.dell_matrix.nursery import owner_nursery_path  # noqa: E402

OWNER = "DCCXV_XPROC_REG"

_SCRIPT_A = textwrap.dedent(
    """
    import json, os, sys, uuid
    sys.path.insert(0, __REPO__)
    from pathlib import Path
    from form.open import open_program
    from form.persist_rest import save
    from form.persist import _STATE_DIR
    from form.dell_matrix.nursery import owner_nursery_path
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent
    from form.mandell.dependency_validity import inspect_dependency
    from form.mandell.knowledge_lineage import lineage_record

    OWNER = __OWNER__
    CANARY = "canary-" + uuid.uuid4().hex

    for f in Path(_STATE_DIR).glob("*" + OWNER + "*"):
        try: f.unlink()
        except OSError: pass
    np_ = Path(owner_nursery_path(OWNER))
    if np_.is_file(): np_.unlink()

    p = open_program(OWNER)
    def confirm(prop):
        res = p.confirm_proposal(prop.id)
        assert res.get("ok"), res
        return prop.id
    aid = confirm(p.nursery.add("cross process root knowledge"))
    bid = confirm(p.nursery.add("cross process derived knowledge", parents=[aid]))

    r = route_intent(p, translate("grow using knowledge about cross process"),
                     raw_line="grow using knowledge about cross process")
    assert r.ok
    nur = dict(p.last_nurture)
    ev = {
        "pid": os.getpid(), "canary": CANARY, "owner": OWNER,
        "ids": {"A": aid, "B": bid},
        "lineage": {k: lineage_record(p, v) for k, v in (("A", aid), ("B", bid))},
        "dependency": {k: inspect_dependency(p, v) for k, v in (("A", aid), ("B", bid))},
        "selected_ids": sorted(nur.get("selected_ids", [])),
        "routable_selected_ids": sorted(nur.get("routable_selected_ids", [])),
        "consumer_scope_ids": sorted(nur.get("consumer_scope_ids", [])),
        "eligible_count": nur.get("eligible_count"),
        "persisted_path": save(p),
    }
    Path(__EVPATH__).write_text(json.dumps(ev, sort_keys=True), encoding="utf-8")
    raise SystemExit(0)
    """
)

_SCRIPT_B = textwrap.dedent(
    """
    import json, os, sys
    sys.path.insert(0, __REPO__)
    from form.persist_rest import load
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent
    from form.mandell.dependency_validity import inspect_dependency
    from form.mandell.knowledge_lineage import lineage_record

    ev = json.loads(open(__EVPATH__, encoding="utf-8").read())
    checks = []
    def check(name, cond):
        checks.append((name, bool(cond)))
    check("distinct_pid", os.getpid() != ev["pid"])
    check("canary_absent", ev["canary"] not in globals())
    p = load(ev["owner"])
    check("loaded_owner", p.owner == ev["owner"])
    for k, uid in ev["ids"].items():
        got = lineage_record(p, uid); want = ev["lineage"][k]
        check("lineage_" + k,
              got["parent_ids"] == want["parent_ids"]
              and got["root_ids"] == want["root_ids"]
              and got["depth"] == want["depth"]
              and got["status"] == want["status"])
        got = inspect_dependency(p, uid); want = ev["dependency"][k]
        check("dependency_" + k,
              got["dependency_status"] == "valid"
              and got["dependency_status"] == want["dependency_status"]
              and sorted(got["ancestor_ids"]) == sorted(want["ancestor_ids"]))
    r = route_intent(p, translate("grow using knowledge about cross process"),
                     raw_line="grow using knowledge about cross process")
    assert r.ok
    nur = p.last_nurture
    check("selected_ids", sorted(nur.get("selected_ids", [])) == ev["selected_ids"])
    check("routable_ids",
          sorted(nur.get("routable_selected_ids", [])) == ev["routable_selected_ids"])
    check("consumer_scope",
          sorted(nur.get("consumer_scope_ids", [])) == ev["consumer_scope_ids"])
    check("eligible_count", nur.get("eligible_count") == ev["eligible_count"])
    r = route_intent(p, translate("trace lineage " + ev["ids"]["B"]),
                     raw_line="trace lineage x")
    check("trace_lineage", p.last_discover.get("status") == "ok")
    r = route_intent(p, translate("trace dependency " + ev["ids"]["B"]),
                     raw_line="trace dependency x")
    check("trace_dependency", p.last_discover.get("dependency_status") == "valid")
    failed = [n for n, ok in checks if not ok]
    print(json.dumps({"passed": sum(1 for _, ok in checks if ok),
                      "total": len(checks), "failed": failed}))
    raise SystemExit(0 if not failed else 1)
    """
)


def _cleanup_owner():
    for f in Path(_STATE_DIR).glob(f"*{OWNER}*"):
        try:
            f.unlink()
        except OSError:
            pass
    np_ = Path(owner_nursery_path(OWNER))
    try:
        if np_.is_file():
            np_.unlink()
    except OSError:
        pass


def test_literal_cross_process_persistence():
    """Two real OS processes: A builds+saves+exits, B loads+recomputes.

    Returns the (passed, total) cross-process check counts for the
    regress runner's n/m accounting.
    """
    _cleanup_owner()
    try:
        with tempfile.TemporaryDirectory(prefix="dccxv_xproc_") as td:
            evpath = os.path.join(td, "evidence.json")
            path_a = os.path.join(td, "procA.py")
            path_b = os.path.join(td, "procB.py")
            def _fill(t):
                return (t.replace("__REPO__", repr(REPO_ROOT))
                         .replace("__OWNER__", repr(OWNER))
                         .replace("__EVPATH__", repr(evpath)))
            Path(path_a).write_text(_fill(_SCRIPT_A), encoding="utf-8")
            Path(path_b).write_text(_fill(_SCRIPT_B), encoding="utf-8")
            ra = subprocess.run([sys.executable, path_a], capture_output=True,
                                text=True, timeout=180)
            assert ra.returncode == 0, f"PROCESS A failed: {ra.stderr[-2000:]}"
            assert os.path.isfile(evpath), "PROCESS A must persist evidence"
            rb = subprocess.run([sys.executable, path_b], capture_output=True,
                                text=True, timeout=180)
            assert rb.returncode == 0, f"PROCESS B failed: {rb.stderr[-2000:]}"
            summary = json.loads(rb.stdout.strip().splitlines()[-1])
            assert summary["failed"] == [], f"cross-process checks failed: {summary}"
            assert summary["passed"] == summary["total"] > 0
            return summary["passed"], summary["total"]
    finally:
        _cleanup_owner()


def smoke() -> bool:
    try:
        passed, total = test_literal_cross_process_persistence()
    except AssertionError as e:
        print(f"[FAIL] literal_cross_process_persistence | {e}", flush=True)
        return False
    print(f"DCC-XV-XPROC: {passed}/{total}", flush=True)
    return True


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
