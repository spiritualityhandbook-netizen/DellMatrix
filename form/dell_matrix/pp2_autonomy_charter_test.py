"""Post-plan PP2 / D4 — the autonomy charter, pinned on real paths.

Ace's rule (2026-10-27): decide what is automatic vs
authority-confirmed; nothing outside authority's awareness. The
charter document (~/workspace/PP2_AUTONOMY_CHARTER.md) inventories
every automatic behavior in form/ with evidence. This suite pins
the mechanically checkable claims so the charter cannot silently
drift from the code:

- machine producers are DENIED confirmation by default
  (AcceptancePolicy), for every producer id, while the human
  review-context path confirms — the gate is real, not a blanket
  refusal of everything;
- the grow_auto opt-in is what the gate answers to: granting it
  (set_auto_confirm_grow) lets that one producer confirm, and
  revoking it denies again;
- AutoGrowth._nursery_auto (the one machine path that DISPOSES of
  proposals: confirm-attempt or auto-reject) has NO production
  caller — a static scan keeps that dormancy true; if anyone
  wires it into production, this suite turns red and the charter
  must be re-ruled. Its disposition behavior in its own owner is
  pinned too: default flag OFF -> even a perfect judge is
  auto-rejected; flag ON + full judge -> confirm ATTEMPT, which
  the policy gate still denies without a producer opt-in;
- DuoBeta's gate refuses learning below MIN_EVIDENCE;
- a Director recommendation never changes a proposal's status,
  and after undock the Director surface refuses;
- bounded evidence stores evict their oldest entries at the cap
  (dock session proposals at 50, dock sessions at 10);
- the InternetGate starts OFF and never auto-enables.
"""
from __future__ import annotations

import glob
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402

RESULTS = []


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


def _pending_status(p, pid):
    for prop in p.list_proposals():
        if prop["id"] == pid:
            return prop["status"]
    return None


_IMPORT_AG = None  # compiled lazily in _check_dormancy


def _check_dormancy():
    """No production file may WIRE AutoGrowth: import the module,
    instantiate AutoGrowth, or touch _nursery_auto.

    Test/proof files are the contract harnesses and are excluded.
    Merely naming the "auto_growth" producer id (the policy gate
    in open.py does) is not wiring and is not flagged; wiring it
    into any other file turns this red.
    """
    import re
    global _IMPORT_AG
    if _IMPORT_AG is None:
        _IMPORT_AG = re.compile(
            r"(?:import\s+[\w.]*auto_growth\b)"
            r"|(?:from\s+[\w.]*auto_growth\s+import)")
    root = os.path.join(os.path.dirname(__file__), "..")
    offenders = []
    for path in glob.glob(os.path.join(root, "**", "*.py"),
                          recursive=True):
        name = os.path.basename(path)
        if name in ("auto_growth.py",
                    "pp2_autonomy_charter_test.py"):
            continue
        if "_test" in name or "_proof" in name:
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            src = f.read()
        if (_IMPORT_AG.search(src) or "AutoGrowth(" in src
                or "_nursery_auto" in src):
            offenders.append(os.path.relpath(path, root))
    _rec("autogrowth dormant: no production wiring",
         offenders == [], f"offenders={offenders}")


def _check_producer_gate(p):
    for prod in ("auto_growth", "code_evolution", "grow_auto",
                 "unknown_machine"):
        pr = p.nursery.add(f"charter {prod}", words="alpha beta gamma")
        r = p.confirm_proposal(pr.id, _producer=prod)
        _rec(f"producer {prod} denied by default",
             r.get("ok") is False
             and r.get("reason") == "acceptance_policy_denied"
             and _pending_status(p, pr.id) == "pending",
             f"ok={r.get('ok')} reason={r.get('reason')}")
    # Control: the human review-context path confirms, so the
    # denials above are the producer gate, not a broken confirm.
    pr = p.nursery.add("charter human", words="alpha beta gamma")
    ctx = p.make_review_context(pr.id, reviewer="human:ace")
    r = p.confirm_proposal(pr.id, _producer="pp2test",
                           _review_context=ctx)
    _rec("human review-context path confirms",
         r.get("ok") is True, f"ok={r.get('ok')} r={r}")


def _check_grow_auto_optin(p):
    pr = p.nursery.add("charter optin", words="alpha beta delta")
    p.set_auto_confirm_grow(True)
    r = p.confirm_proposal(pr.id, _producer="grow_auto")
    _rec("grow_auto confirms under explicit opt-in",
         r.get("ok") is True, f"ok={r.get('ok')}")
    pr2 = p.nursery.add("charter optin revoked", words="alpha beta eps")
    p.set_auto_confirm_grow(False)
    r = p.confirm_proposal(pr2.id, _producer="grow_auto")
    _rec("grow_auto denied again after revocation",
         r.get("ok") is False
         and _pending_status(p, pr2.id) == "pending",
         f"ok={r.get('ok')} reason={r.get('reason')}")


_HIGH_JUDGE = {"floor_accept": True, "verita_score": 0.95,
               "combined": 0.95, "grade": "strong",
               "reason": "restore strong signal"}
_LOW_JUDGE = {"floor_accept": False, "verita_score": 0.1,
              "combined": 0.1, "grade": "weak", "reason": "thin"}


def _check_autogrowth_disposition():
    from form.dell_matrix.auto_growth import AutoGrowth
    from form.persist import load as pload
    owner = "PP2Auto"
    _cleanup(owner)
    try:
        ag = AutoGrowth(owner=owner)
        _rec("autogrowth acceptance flag defaults OFF",
             ag.auto is False, f"auto={ag.auto}")
        out = ag._nursery_auto("pp2 high", "words one two",
                               dict(_HIGH_JUDGE), "pp2test")
        _rec("flag OFF: even a full judge is auto-rejected",
             out.get("status") == "auto_rejected",
             f"status={out.get('status')}")
        ag2 = AutoGrowth(owner=owner)
        ag2.auto = True
        out = ag2._nursery_auto("pp2 high armed", "words three four",
                                dict(_HIGH_JUDGE), "pp2test")
        _rec("flag ON + full judge: confirm attempt, policy denies",
             out.get("status") == "auto_confirm_failed",
             f"status={out.get('status')}")
        pa = pload(owner, activate=False)
        summ = pa.nursery.summary()
        _rec("denied attempt leaves the proposal pending, none confirmed",
             summ.get("pending") == 1 and summ.get("confirmed") == 0,
             f"summary={summ}")
        out = ag2._nursery_auto("pp2 low armed", "words five six",
                                dict(_LOW_JUDGE), "pp2test")
        _rec("flag ON + low judge: auto-rejected",
             out.get("status") == "auto_rejected",
             f"status={out.get('status')}")
    finally:
        _cleanup(owner)


def _check_duobeta_gate(p):
    from form.mandell import duobeta_learn as dbl
    prop = dbl.propose(p, "preference", 10, evidence_outcome_ids=[])
    g = dbl.gate_proposal(p, prop["proposal_id"])
    _rec("duobeta gate refuses below MIN_EVIDENCE",
         g.get("accepted") is False
         and g.get("reason") == "insufficient_evidence",
         f"gate={g}")
    after = dbl.get_proposal(p, prop["proposal_id"])
    _rec("refused learning proposal is REJECTED, not applied",
         after is not None and after.get("status") == "REJECTED",
         f"after={after and after.get('status')}")


def _check_director(p):
    from form.dell_matrix.director_session import bind_director
    pr = p.nursery.add("charter director", words="alpha beta eta")
    ds = bind_director(p)
    rec = ds.recommend(pr.id, "accept", "charter recommendation")
    _rec("director recommend is a record, never a confirmation",
         rec.get("ok") is True
         and rec.get("effect") == "recommendation_only"
         and _pending_status(p, pr.id) == "pending",
         f"rec={rec}")
    ds.undock()
    rec2 = ds.recommend(pr.id, "accept", "after undock")
    _rec("director surface refuses after undock",
         rec2.get("ok") is False
         and rec2.get("reason") == "session_closed",
         f"rec2={rec2}")


def _check_bounds():
    from form.dell_matrix import dock_session as dks
    rec = dks.new_record("PP2Charter", "subj", "fake", "m", "t", "s")
    for i in range(51):
        dks.append_proposal(rec, {"pid": f"p{i}", "kind": "new"})
    props = rec["proposals"]
    _rec("session proposal entries capped at 50, oldest dropped",
         len(props) == 50 and props[0].get("pid") == "p1",
         f"len={len(props)} first={props[0] if props else None}")
    recs = {}
    for i in range(11):
        r_i = dks.new_record("PP2Charter", "subj", "fake", "m", "t", "s")
        r_i["started"] = f"2026-10-28T00:{i:02d}:00Z"
        recs[r_i["session_id"]] = r_i
    first_sid = list(recs.keys())[0]
    sec = dks.serialize_section(recs, None, "PP2Charter")
    sess = sec.get("sessions") or {}
    _rec("dock sessions capped at 10 per owner, oldest dropped",
         len(sess) == 10 and first_sid not in sess,
         f"kept={len(sess)}")


def _check_internet_gate(p):
    from form.dell_matrix.internet_gate import InternetGate
    gate = InternetGate()
    carried = getattr(p, "internet", None)
    _rec("internet gate starts OFF and never auto-enables",
         gate.on is False
         and carried is not None and carried.on is False
         and getattr(carried, "auto_allowed", None) is False,
         f"new={gate.on} carried={getattr(carried, 'on', None)}")


def main():
    _check_dormancy()
    owner = "PP2Charter"
    _cleanup(owner)
    try:
        p = Program(owner)
        _check_producer_gate(p)
        _check_grow_auto_optin(p)
        _check_duobeta_gate(p)
        _check_director(p)
        _check_internet_gate(p)
    finally:
        _cleanup(owner)
    _check_autogrowth_disposition()
    _check_bounds()
    ok = sum(1 for _, c, _ in RESULTS if c)
    for name, cond, detail in RESULTS:
        print(f"{'PASS' if cond else 'FAIL'} {name}"
              + (f" :: {detail}" if not cond else ""))
    print(f"PP2_CHARTER: {ok}/{len(RESULTS)}")
    return ok == len(RESULTS)


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
