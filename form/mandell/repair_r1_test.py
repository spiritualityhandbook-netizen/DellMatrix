"""Director review repair R1 — session/evidence integrity.

Independent review (Mode D, 2026-10-27) declined two segments
for defects the phase suites missed:

* PR #112 (dock provenance): a docked proposal survived reload,
  but its session evidence disappeared unless a later explicit
  Program.save() happened — nursery.add autosaves the proposal,
  while the dock_sessions section only reached disk on an
  unrelated save. Fixed: DockedSession persists program state
  (best-effort, mirroring design_loop.record_event) when the
  session record is created at dock(), when each evidence entry
  lands, and when the record closes at undock().
* PR #115 (Director dock): after undock(), the DirectorSession
  still read snapshots and wrote recommendations. Fixed: the
  endpoint is closed when it undocks OR the wrapped session is
  undocked by any path; every allowlist method then refuses
  (session_closed) with NO read and NO write — not even a
  refusal record. The wrapped DockedSession.field_snapshot()
  also fails closed (None) after undock.

The persistence checks are CROSS_PROCESS: child processes dock,
propose, and exit WITHOUT saving; a fresh process must find the
evidence on disk.
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402
from form import persist_rest  # noqa: E402
from form.dell_matrix import director_session as ds  # noqa: E402
from form.dell_matrix import inference_dock as idock  # noqa: E402

RESULTS = []
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:200]))


def _cleanup(owner):
    base = os.path.join(os.path.dirname(__file__), "..", "state")
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json",
                f"gen_{owner}_*", f"current_{owner}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            shutil.rmtree(d)


def _child(owner, script):
    r = subprocess.run([sys.executable, "-c", script],
                       cwd=ROOT, capture_output=True, text=True,
                       timeout=120)
    assert r.returncode == 0, r.stderr[-600:]
    return r.stdout


def smoke() -> bool:
    owner = "RepairR1"
    _cleanup(owner)
    try:
        # ── 1. CROSS_PROCESS: propose, exit WITHOUT save; the
        # session record AND its evidence entry must be on disk.
        out = _child(owner, f"""
import sys
sys.path.insert(0, ".")
from form.open import Program
from form.dell_matrix import inference_dock as idock
p = Program(owner="{owner}")
s = idock.dock(p, trusted_subject="agent:repair", provider="fake",
               task="probe")
r = s.propose("propose an idea about durable session evidence")
assert r.get("ok"), r
print(r["pid"], r["session_id"])
""")
        pid, sid = out.split()
        p2 = persist_rest.load(owner, activate=False)
        sessions = getattr(p2, "dock_sessions", None) or {}
        record = sessions.get(sid)
        _rec("evidence_record_survives_unsaved_exit", record is not None,
             f"sessions={list(sessions)}")
        entries = (record or {}).get("proposals") or []
        _rec("evidence_entry_survives_unsaved_exit",
             any(e.get("pid") == pid for e in entries),
             f"entries={entries}")
        props = [pr.id for pr in p2.nursery.pending()]
        _rec("proposal_and_evidence_together", pid in props)

        # ── 2. CROSS_PROCESS: undock's close also persists without
        # a later explicit save.
        _child(owner, f"""
import sys
sys.path.insert(0, ".")
from form.open import Program
from form.dell_matrix import inference_dock as idock
p = Program(owner="{owner}")
s = idock.dock(p, trusted_subject="agent:repair", provider="fake",
               task="probe")
s.propose("propose an idea about durable session evidence")
s.undock()
print(s.session_id)
""")
        p3 = persist_rest.load(owner, activate=False)
        sessions3 = getattr(p3, "dock_sessions", None) or {}
        closed = [r for r in sessions3.values()
                  if r.get("closed") is not None]
        _rec("undock_close_survives_unsaved_exit", len(closed) >= 1,
             f"records={len(sessions3)} closed={len(closed)}")

        # ── 3. Director lifecycle: after undock, no reads, no
        # writes (records count frozen), every verb refused.
        dev = Program(owner=owner)
        d = ds.bind_director(dev, provider="fake",
                             subject="director:dev", scope_owner=owner)
        agent = idock.dock(dev, trusted_subject="agent:repair",
                           provider="fake", task="probe")
        made = agent.propose("propose an idea for director lifecycle")
        target = made["pid"]
        warm = d.recommend(target, "accept", "sound while docked")
        _rec("director_works_while_docked", warm.get("ok") is True,
             str(warm))
        before = len(getattr(dev, "director_records", None) or {})
        d.undock()
        _rec("director_snapshot_closed", d.snapshot() == {})
        for name, call in (
                ("review", lambda: d.review(target)),
                ("recommend", lambda: d.recommend(target, "accept",
                                                  "too late")),
                ("request_evidence",
                 lambda: d.request_evidence(target, "more")),
                ("directive", lambda: d.directive("late directive"))):
            out = call()
            _rec(f"director_{name}_refused_after_undock",
                 out.get("ok") is False
                 and out.get("reason") == "session_closed", str(out))
        after = len(getattr(dev, "director_records", None) or {})
        _rec("director_no_writes_after_undock", after == before,
             f"before={before} after={after}")
        _rec("director_undock_idempotent",
             d.undock().get("ok") is True)

        # ── 4. Wrapped session undocked directly: the Director
        # endpoint dies with it.
        d2 = ds.bind_director(dev, provider="fake",
                              subject="director:dev", scope_owner=owner)
        d2._session.undock()
        out = d2.recommend(target, "accept", "after wrapped undock")
        _rec("director_dies_with_wrapped_session",
             out.get("ok") is False
             and out.get("reason") == "session_closed", str(out))
        _rec("director_snapshot_dies_with_wrapped",
             d2.snapshot() == {})

        # ── 5. A plain docked session reads nothing after undock.
        s5 = idock.dock(dev, trusted_subject="agent:repair",
                        provider="fake", task="probe")
        s5.undock()
        _rec("field_snapshot_none_after_undock",
             s5.field_snapshot() is None)
    finally:
        _cleanup(owner)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'} {name} {detail}")
    print(f"repair_r1_test {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
