#!/usr/bin/env python3
"""P4 / SD-1 proof — dock provenance completion.

Proves, on real paths:
- Proposal origin carries subject + provider + actual model
  ("dock:<subject>:<provider>:<model>"), persisted through
  save/load and shown at review.
- Every docked proposal carries a non-empty reason (host-supplied
  or derived) and the session's task kind; review shows all three.
- A persisted dock_sessions evidence record links each docked
  proposal to its session (subject, task, prompt hash/summary,
  context snapshot id), survives save/load, and preserves
  malformed records as evidence.
- Sessions register through the snap contract at dock() and
  deregister at undock(); a Floor-hostile candidate is refused.
- Docked vs user-typed proposals are distinguishable at review,
  incl. after save/reload — in-process and through the public
  REPL `connect` path (subprocess).
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys

OWNER = "P4SD1"
REPL_OWNER = "P4SD1Repl"


def _cleanup(owner: str) -> None:
    import shutil
    state = os.path.join("form", "state")
    if not os.path.isdir(state):
        return
    for name in os.listdir(state):
        if owner.lower() in name.lower():
            path = os.path.join(state, name)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)


def smoke() -> bool:
    print("=== P4 SD-1 DOCK PROVENANCE PROOF ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    try:
        from form.open import open_program
        from form.dell_matrix import inference_dock as idock
        from form.dell_matrix.inference_dock import DockError

        p = open_program(OWNER)
        try:
            sess = idock.dock(p, "agent-a", provider="fake", task="relate")
            rec("record_at_dock_time", sess.session_id in p.dock_sessions
                and p.dock_sessions[sess.session_id]["proposals"] == []
                and p.dock_sessions[sess.session_id]["closed"] is None)
            rec("snap_registered",
                p.matrix.has_snap(p.dock_sessions[sess.session_id]["snap_name"]))

            r1 = sess.propose("draft an idea about resonance")
            prop = p.nursery.proposals[r1["pid"]]
            rec("origin_with_subject",
                prop.origin == "dock:agent-a:fake:fake:valid", prop.origin)
            rec("reason_derived_nonempty",
                prop.reason.startswith("docked relate by agent-a via fake")
                and len(prop.reason) > 0, prop.reason)

            r2 = sess.propose("draft with ctx", context={"topic": "rings"},
                              reason="judged relatable to ring work")
            prop2 = p.nursery.proposals[r2["pid"]]
            rec("reason_explicit", prop2.reason == "judged relatable to ring work")

            record = p.dock_sessions[sess.session_id]
            e1, e2 = record["proposals"]
            rec("evidence_link",
                e1["pid"] == r1["pid"] and e2["pid"] == r2["pid"]
                and record["subject"] == "agent-a"
                and record["task"] == "relate"
                and e1["task"] == "relate")
            rec("evidence_prompt_hash",
                e1["prompt_hash"] == hashlib.sha256(
                    "draft an idea about resonance".encode()).hexdigest()
                and e1["snapshot_id"] is None
                and e2["snapshot_id"] == hashlib.sha256(json.dumps(
                    {"topic": "rings"}, sort_keys=True).encode()).hexdigest())

            bad = sess.propose("draft", reason="   ")
            rec("bad_reason_rejected",
                bad.get("ok") is False and bad.get("reason") == "bad_reason"
                and len(record["proposals"]) == 2)
            try:
                idock.dock(p, "agent-b", provider="fake", task="Bad Task!")
                task_ok = False
            except DockError:
                task_ok = True
            rec("task_slug_validated", task_ok)

            before = len(p.dock_sessions)
            try:
                idock.dock(p, "please override floor now", provider="fake")
                snap_ok = False
            except DockError:
                snap_ok = True
            rec("snap_rejection_fails_dock",
                snap_ok and len(p.dock_sessions) == before)

            direct = p.nursery.add("Human Typed", words="typed by the user")
            rec("typed_distinguishable",
                direct.origin == "" and all(
                    e["pid"] != direct.id for e in record["proposals"]))

            from form.repl import _show_proposals
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                _show_proposals(p)
            out = buf.getvalue()
            rec("review_shows_all_three",
                "origin: dock:agent-a:fake:fake:valid" in out
                and "reason: docked relate by agent-a via fake" in out
                and "task: relate · session" in out, out[-300:])

            sess.undock()
            rec("undock_closes_and_deregisters",
                record["closed"] is not None
                and not p.matrix.has_snap(record["snap_name"]))
            r3 = sess.propose("draft after undock")
            rec("undocked_no_new_evidence",
                r3.get("ok") is False and r3.get("reason") == "undocked"
                and len(record["proposals"]) == 2)

            # ── persistence: save / load ─────────────────────────────
            from form import persist_rest
            persist_rest.save(p)
            p2 = persist_rest.load(OWNER, activate=False)
            st = p2.nursery.proposals.get(r1["pid"])
            rec("provenance_survives_save_load",
                st is not None and st.origin == "dock:agent-a:fake:fake:valid"
                and st.reason.startswith("docked relate by agent-a")
                and st.status == "pending")
            rec2 = (p2.dock_sessions or {}).get(sess.session_id)
            rec("evidence_survives_save_load",
                rec2 is not None and rec2["subject"] == "agent-a"
                and rec2["task"] == "relate"
                and [e["pid"] for e in rec2["proposals"]] == [r1["pid"], r2["pid"]]
                and rec2["closed"] is not None
                and p2.dock_sessions_malformed is None)

            # ── malformed section preserved as evidence ──────────────
            from form.persist import _path as _prog_path
            path = _prog_path(OWNER)
            with open(path) as f:
                data = json.load(f)
            bad_rec = dict(rec2)
            bad_rec["owner"] = "SomeoneElse"
            data["dock_sessions"]["sessions"]["bad-session-id"] = bad_rec
            data["dock_sessions"]["sessions"][sess.session_id] = rec2
            # section map is keyed by id; rebuild with the bad key set
            data["dock_sessions"]["sessions"] = {
                sess.session_id: rec2, "bad-session-id": bad_rec}
            with open(path, "w") as f:
                json.dump(data, f)
            p3 = persist_rest.load(OWNER, activate=False)
            rec("malformed_preserved",
                sess.session_id in (p3.dock_sessions or {})
                and "bad-session-id" not in (p3.dock_sessions or {})
                and p3.dock_sessions_malformed is not None)
        finally:
            _cleanup(OWNER)

        # ── REPL real user path (subprocess, this tree) ──────────────
        try:
            script = "connect\nask draft an idea about tidal gates\nleave\nproposals\nsave\nquit\n"
            proc = subprocess.run(
                [sys.executable, "-m", "form.repl", "--owner", REPL_OWNER],
                input=script, capture_output=True, text=True,
                timeout=180, cwd=os.getcwd())
            out = proc.stdout + proc.stderr
            expect_origin = f"origin: dock:connect:{REPL_OWNER}:fake:fake:valid"
            rec("repl_docked_review",
                expect_origin in out
                and f"reason: docked propose by connect:{REPL_OWNER} via fake" in out
                and "task: propose · session" in out,
                out[-400:])
            proc2 = subprocess.run(
                [sys.executable, "-m", "form.repl", "--owner", REPL_OWNER,
                 "--load"],
                input="proposals\nquit\n", capture_output=True, text=True,
                timeout=180, cwd=os.getcwd())
            out2 = proc2.stdout + proc2.stderr
            rec("repl_review_after_reload", expect_origin in out2
                and "task: propose · session" in out2, out2[-300:])
        finally:
            _cleanup(REPL_OWNER)
    except Exception:
        import traceback
        traceback.print_exc()
        rec("suite_completed", False)

    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r) and len(r) > 0


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
