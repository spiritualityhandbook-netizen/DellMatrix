#!/usr/bin/env python3
"""Critic Finding 9 — browser confirm review-context routing.

Finding (Critic, verified REAL first-hand by Uni 2026-11-25; build
authorized by Director disposition 7180713277 on issue #512):

  form/dell_matrix/live_visual.py's confirm branches (single + batch)
  called program.confirm_proposal(pid) with NO producer and NO review
  context, so the acceptance policy denied every browser-path confirm
  as anonymous (acceptance_policy_denied) — while the equivalent REPL
  path (form/repl.py: "confirm <id>" / "confirm all") issues a bound
  review context via make_review_context and confirms fine. Since the
  FI-011 door landed (#520), anonymous confirms are refused BY DESIGN;
  the browser path must PRESENT the authenticated human review context,
  never bypass the refusal.

Repair contract: the live server is the local human's own UI
(127.0.0.1, origin-checked POST /cmd) — its confirm dispatch is
trusted dispatch code exactly like the REPL's, so it issues the
review context the same way (producer "repl_user", reviewer
"repl_user") for the single AND batch forms. Anonymous /
context-free / forged-context confirms remain refused; no new
authority is created; confirmation remains the human's act.

Legs (browser legs go through the REAL HTTP entry point —
start_live + POST /cmd — not only handler calls):
  CTL  repl-style confirm with issued context works (control).
  A    browser single confirm via HTTP /cmd confirms.
  B    browser batch "confirm all" via HTTP /cmd confirms all.
  C    anonymous direct confirm (no producer, no context) refused,
       proposal stays pending (the #520 door, pre- and post-fix).
  D    forged (never-issued) review context refused.
  E    cross-origin POST /cmd confirm denied 403, stays pending.

Labels: INTEGRATION (real HTTP server + Program). State hygiene:
unique tagged owners, loud cleanup.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"CHECK {name}: {'PASS' if ok else 'FAIL'} - {detail}", flush=True)
    return bool(ok)


def cleanup(owner):
    # Standing rule: cleanup errors FAIL LOUDLY, never swallowed.
    for f in glob.glob(os.path.join(STATE_DIR, f"*{owner}*")):
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)


def build(owner):
    from form.open import open_program
    cleanup(owner)
    p = open_program(owner)
    plane = p.cube.session.plane
    plane.units.clear()
    plane.sandboxes.clear()
    p.nursery.proposals.clear()
    p.place("f9pa", "f9 parent a", words="harbor lantern parent a",
            x=0.0, y=0.0)
    p.place("f9pb", "f9 parent b", words="harbor lantern parent b",
            x=1.0, y=0.0)
    return p


def seed(p, label):
    prop = p.nursery.add(label=label, words=f"words for {label}",
                         kind="new", parents=["f9pa", "f9pb"],
                         origin="repl_user",
                         reason="critic f9 livevisual fixture")
    return prop.id


def status_of(p, pid):
    prop = p.nursery.proposals.get(pid)
    return getattr(prop, "status", None)


class Browser:
    """Real HTTP entry point: start_live + POST /cmd."""

    def __init__(self, program):
        from form.dell_matrix import live_visual
        self.live_visual = live_visual
        port = 19100 + (os.getpid() % 50)
        info = live_visual.start_live(program, port=port, background=True)
        if not info.get("ok"):
            raise RuntimeError(f"start_live failed: {info}")
        self.port = live_visual._LIVE_SERVER.server_address[1]

    def post(self, cmd, origin=None):
        headers = {"Content-Type": "application/json"}
        if origin is not None:
            headers["Origin"] = origin
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/cmd",
            data=json.dumps({"cmd": cmd}).encode(),
            headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode())

    def close(self):
        try:
            self.live_visual._LIVE_SERVER.shutdown()
            self.live_visual._LIVE_SERVER.server_close()
        except Exception:
            pass


def legs():
    # CTL — repl-style confirm with an issued context works.
    p = build("F9LVCTL")
    pid = seed(p, "f9 ctl manual control")
    res = p.confirm_proposal(
        pid, _producer="repl_user",
        _review_context=p.make_review_context(pid, "repl_user"))
    check("CTL_repl_style_confirm_works",
          bool(res.get("ok")) and status_of(p, pid) == "confirmed",
          f"ok={res.get('ok')} status={status_of(p, pid)}")

    # A — browser single confirm through the real HTTP entry point.
    p = build("F9LVA")
    pid = seed(p, "f9 browser single")
    b = Browser(p)
    try:
        status, body = b.post(f"confirm {pid}")
    finally:
        b.close()
    check("A_browser_single_confirm_confirms",
          status == 200 and body.get("ok") is True
          and status_of(p, pid) == "confirmed"
          and p.cube.session.plane.units.get(pid) is not None,
          f"http={status} ok={body.get('ok')} "
          f"error={body.get('error')} status_of={status_of(p, pid)}")

    # B — browser batch form ("confirm all") through HTTP.
    p = build("F9LVB")
    pid1 = seed(p, "f9 browser batch one")
    pid2 = seed(p, "f9 browser batch two")
    b = Browser(p)
    try:
        status, body = b.post("confirm all")
    finally:
        b.close()
    check("B_browser_batch_confirm_all_confirms",
          status == 200 and body.get("ok") is True
          and body.get("confirmed") == 2
          and status_of(p, pid1) == "confirmed"
          and status_of(p, pid2) == "confirmed",
          f"http={status} ok={body.get('ok')} "
          f"confirmed={body.get('confirmed')} "
          f"s1={status_of(p, pid1)} s2={status_of(p, pid2)}")

    # C — anonymous direct confirm stays refused (the #520 door).
    p = build("F9LVC")
    pid = seed(p, "f9 anonymous direct")
    res = p.confirm_proposal(pid)
    check("C_anonymous_direct_confirm_refused",
          not res.get("ok")
          and res.get("reason") == "acceptance_policy_denied"
          and status_of(p, pid) == "pending",
          f"ok={res.get('ok')} reason={res.get('reason')} "
          f"status={status_of(p, pid)}")

    # D — a forged, never-issued review context stays refused.
    p = build("F9LVD")
    pid = seed(p, "f9 forged context")
    forged = {"approval_id": "forged-never-issued", "reviewer": "repl_user",
              "operation": "confirm", "target": pid}
    res = p.confirm_proposal(pid, _producer="repl_user",
                             _review_context=forged)
    check("D_forged_context_refused",
          not res.get("ok")
          and res.get("reason") == "acceptance_policy_denied"
          and status_of(p, pid) == "pending",
          f"ok={res.get('ok')} reason={res.get('reason')} "
          f"status={status_of(p, pid)}")

    # E — cross-origin browser POST is denied before dispatch.
    p = build("F9LVE")
    pid = seed(p, "f9 cross origin")
    b = Browser(p)
    try:
        status, body = b.post(f"confirm {pid}",
                              origin="http://evil.example")
    finally:
        b.close()
    check("E_cross_origin_confirm_denied",
          status == 403 and body.get("ok") is False
          and status_of(p, pid) == "pending",
          f"http={status} ok={body.get('ok')} "
          f"status_of={status_of(p, pid)}")


def main() -> int:
    print("=== CRITIC F9 LIVE-VISUAL CONFIRM CONTEXT ===")
    legs()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"CRITIC_F9_LIVEVISUAL {passed}/{len(RESULTS)}")
    for name, ok in RESULTS:
        if not ok:
            print(f"  FAILING: {name}")
    return 0 if passed == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
