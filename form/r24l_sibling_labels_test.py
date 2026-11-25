"""R24-L siblings — label losslessness at the two remaining 80-char cuts.

Director authorization 7136782069 (chat Director, on PR #506):
independent 80-character cuts on main in (1) the English `add idea` /
Nurture route (`form/mandell/translate.py`: the authored label and its
case-preserved twin were both sliced to 80 before the Intent was built)
and (2) the successor label before `nursery.add` in
`form/mandell/supersession.py` (sliced to 80). The canonical Nursery
admits labels through 200 chars (MAX_LABEL_CHARS = 200, NurseryLabelError
BEFORE mutation) and refuses longer labels; merged PR #522 repaired the
same defect class on the create door. These two doors were outside it.

Characterization at main 56f12c51 (failing-first witnesses below):
  - Translate door, driven through its normal caller chain
    (translate() -> Intent -> semantic_router.route_intent -> Dell 37
    Nurture -> nursery.add): a 150-char authored label persisted as
    exactly 80 chars with an ok=True receipt — silent truncation. A
    201-char label likewise persisted cut to 80 with ok=True — no
    refusal at all.
  - Supersession door, driven through its normal caller chain
    (translate() -> route_intent -> Dell 37 supersede branch ->
    supersede_proposal): `make_supersede_context` binds the successor
    approval to the FULL effective label ("revision of {old label}"),
    but `_supersede_impl` created the successor with the label cut to
    80, so any generated label over 80 chars failed the whole supersede
    with the opaque "derived content does not match the approved
    successor payload" — a lawful supersede was impossible, and an
    over-budget generated label was refused only by that accident,
    never by the typed label law.

Contract (mirroring #522 / the canonical Nursery law):
  - labels up to 200 chars are preserved byte-exact (case included)
    across save/reload at both doors, generated labels included;
  - a label over 200 chars — authored, explicit, or generated —
    surfaces a typed `label_over_budget` refusal through the normal
    caller BEFORE any mutation; a supersession refusal preserves the
    predecessor and leaves no partial successor, no supersede intent
    journal, and no supersession receipt.
Context-query and display excerpts have separate semantics and are
not touched.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = []


def rec(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
    RESULTS.append((name, bool(ok)))


def _label(prefix, n):
    return prefix + "x" * (n - len(prefix))


def _clean(owner):
    from form.dell_matrix.nursery import owner_nursery_path
    from form.mandell.core_i_recovery import _supersede_journal_path
    for path in (str(ROOT / "form" / "state" / f"program_{owner}.json"),
                 owner_nursery_path(owner),
                 _supersede_journal_path(owner)):
        try:
            os.unlink(path)
        except OSError:
            pass


def _fresh_program(owner):
    _clean(owner)
    from form.open import open_program
    return open_program(owner)


def _make_predecessor(p, lab):
    prop = p.nursery.add(lab, words="original predecessor words")
    ctx = p.make_review_context(prop.id, "sib")
    r = p.confirm_proposal(prop.id, _producer="sib", _review_context=ctx)
    assert r.get("ok"), f"predecessor setup failed: {r}"
    return prop.id


def _save(p):
    from form import persist_rest
    p.nursery.save()
    persist_rest.save(p)


def _cold_reload_labels(owner):
    """Fresh process: load the saved state, return {pid: (label, status)}."""
    code = (
        "import json\n"
        "from form import persist_rest\n"
        f"p = persist_rest.load({owner!r}, activate=False)\n"
        "out = {pid: (pr.label, pr.status) for pid, pr in p.nursery.proposals.items()}\n"
        "print(json.dumps(out))\n"
    )
    r = subprocess.run([sys.executable, "-B", "-c", code],
                       capture_output=True, text=True, cwd=str(ROOT), timeout=280)
    assert r.returncode == 0, f"cold reload failed: {r.stderr[-800:]}"
    return json.loads(r.stdout.strip().splitlines()[-1])


def _route(p, line):
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent
    return route_intent(p, translate(line), raw_line=line)


def _refusal_text(rc, p):
    parts = [str(getattr(rc, "error", "") or "")]
    parts += [str(m) for m in (getattr(rc, "messages", None) or [])]
    parts.append(str(getattr(p, "last_nurture", None)))
    return " ".join(parts)


def _translate_cases():
    # Control: exactly 80 chars — whole at main already.
    lab80 = _label("SibEighty", 80)
    p = _fresh_program("SIBR24T80")
    rc = _route(p, f"add idea {lab80}")
    props = list(p.nursery.proposals.values())
    rec("T 80-char label: routed ok, proposal stored whole",
        rc.ok and len(props) == 1 and props[0].label == lab80,
        f"ok={rc.ok} labels={[len(pr.label or '') for pr in props]}")

    # 150 chars, mixed case — the authored label must survive byte-exact.
    lab150 = "SibTranslate" + "Ab" * 60 + "TailEnd"
    lab150 = lab150 + "z" * (150 - len(lab150))
    assert len(lab150) == 150
    p = _fresh_program("SIBR24T150")
    rc = _route(p, f"add idea {lab150}")
    props = list(p.nursery.proposals.values())
    rec("T 150-char mixed-case label: proposal stored byte-exact (case preserved)",
        rc.ok and len(props) == 1 and props[0].label == lab150,
        f"ok={rc.ok} labels={[len(pr.label or '') for pr in props]}")
    _save(p)
    cold = _cold_reload_labels("SIBR24T150")
    rec("T 150-char label: byte-exact after save + cold reload (fresh process)",
        any(lab == lab150 for lab, _ in cold.values()),
        f"cold={[len(l or '') for l, _ in cold.values()]}")

    # 200 chars — the canonical budget boundary: preserved whole.
    lab200 = _label("SibBudgetEdge", 200)
    p = _fresh_program("SIBR24T200")
    rc = _route(p, f"add idea {lab200}")
    props = list(p.nursery.proposals.values())
    rec("T 200-char label (canonical budget): proposal stored byte-exact",
        rc.ok and len(props) == 1 and props[0].label == lab200,
        f"ok={rc.ok} labels={[len(pr.label or '') for pr in props]}")

    # 201 chars — over budget: typed refusal through the normal caller,
    # before any mutation; nothing persists.
    lab201 = _label("SibOverBudget", 201)
    p = _fresh_program("SIBR24T201")
    rc = _route(p, f"add idea {lab201}")
    rec("T 201-char label: refusal (receipt not ok, names label_over_budget)",
        (not rc.ok) and "label_over_budget" in _refusal_text(rc, p),
        f"ok={rc.ok} error={getattr(rc, 'error', '')!r}")
    rec("T 201-char label: zero mutation (no proposal, whole or cut)",
        len(p.nursery.proposals) == 0,
        f"proposals={[(pr.id, len(pr.label or '')) for pr in p.nursery.proposals.values()]}")
    _save(p)
    cold = _cold_reload_labels("SIBR24T201")
    rec("T 201-char label: nothing persisted after save + cold reload",
        len(cold) == 0, f"cold={list(cold)}")


def _supersession_cases():
    from form.mandell.core_i_recovery import _supersede_journal_path
    from form.mandell.supersession import supersede_proposal, SupersedeError

    # Control: short predecessor — generated label whole at main already.
    p = _fresh_program("SIBR24SCTL")
    pid = _make_predecessor(p, "ShortPredSib")
    rc = _route(p, f"supersede idea {pid} with revised control words")
    succ = [pr for pr in p.nursery.proposals.values() if pr.id != pid]
    rec("S control: supersede ok, generated label whole",
        rc.ok and len(succ) == 1 and succ[0].label == "revision of ShortPredSib",
        f"ok={rc.ok} error={getattr(rc, 'error', '')!r} succ={[(s.id, s.label) for s in succ]}")

    # Generated label 162 (predecessor 150): lawful, must persist whole.
    lab_p150 = _label("SibPredOneFifty", 150)
    gen162 = f"revision of {lab_p150}"
    assert len(gen162) == 162
    p = _fresh_program("SIBR24S150")
    pid = _make_predecessor(p, lab_p150)
    rc = _route(p, f"supersede idea {pid} with revised successor words")
    succ = [pr for pr in p.nursery.proposals.values() if pr.id != pid]
    rec("S generated 162-char label: supersede ok through the normal caller",
        rc.ok, f"ok={rc.ok} error={getattr(rc, 'error', '')!r}")
    rec("S generated 162-char label: successor stored byte-exact",
        len(succ) == 1 and succ[0].label == gen162,
        f"succ={[(s.id, len(s.label or '')) for s in succ]}")
    _save(p)
    cold = _cold_reload_labels("SIBR24S150")
    rec("S generated 162-char label: byte-exact after save + cold reload",
        any(lab == gen162 for lab, _ in cold.values()),
        f"cold={[len(l or '') for l, _ in cold.values()]}")

    # Generated label 212 (predecessor 200): typed refusal; predecessor
    # preserved; no partial successor, no journal, no receipt.
    lab_p200 = _label("SibPredTwoHundred", 200)
    p = _fresh_program("SIBR24S200")
    pid = _make_predecessor(p, lab_p200)
    n_before = len(p.nursery.proposals)
    rc = _route(p, f"supersede idea {pid} with revised successor words")
    rec("S generated 212-char label: refusal names label_over_budget",
        (not rc.ok) and "label_over_budget" in _refusal_text(rc, p),
        f"ok={rc.ok} error={getattr(rc, 'error', '')!r}")
    pred = p.nursery.proposals.get(pid)
    rec("S generated 212-char label: predecessor preserved (confirmed, active)",
        pred is not None and pred.status == "confirmed"
        and getattr(pred, "lifecycle_state", None) == "active",
        f"pred={None if pred is None else (pred.status, getattr(pred, 'lifecycle_state', None))}")
    rec("S generated 212-char label: no partial successor created",
        len(p.nursery.proposals) == n_before,
        f"before={n_before} after={len(p.nursery.proposals)}")
    rec("S generated 212-char label: no supersede intent journal left",
        not os.path.exists(_supersede_journal_path(p.owner)),
        f"journal exists at {_supersede_journal_path(p.owner)}")
    _save(p)
    cold = _cold_reload_labels("SIBR24S200")
    rec("S generated 212-char label: cold reload — predecessor only, still confirmed",
        len(cold) == n_before and cold.get(pid, (None, None))[1] == "confirmed",
        f"cold={ {k: (len(l or ''), s) for k, (l, s) in cold.items()} }")

    # Explicit label 150 via the public API + bound review context.
    lab_e150 = _label("SibExplicit", 150)
    p = _fresh_program("SIBR24SE150")
    pid = _make_predecessor(p, "ShortPredExplicit")
    ctx = p.make_supersede_context(pid, "sib", "revised words", label=lab_e150)
    res, raised = None, None
    try:
        res = supersede_proposal(p, pid, "revised words", label=lab_e150,
                                 _producer="sib", _review_context=ctx)
    except Exception as e:  # at main: ApprovalError from the payload binding
        raised = f"{type(e).__name__}: {e}"
    succ = [pr for pr in p.nursery.proposals.values() if pr.id != pid]
    rec("S explicit 150-char label: supersede ok, successor byte-exact",
        res is not None and res.get("ok") is True
        and len(succ) == 1 and succ[0].label == lab_e150,
        f"raised={raised} res_ok={None if res is None else res.get('ok')} "
        f"succ={[(s.id, len(s.label or '')) for s in succ]}")

    # Explicit label 201 via the public API: typed SupersedeError,
    # predecessor preserved, no successor, no journal.
    lab_e201 = _label("SibExplicitOver", 201)
    p = _fresh_program("SIBR24SE201")
    pid = _make_predecessor(p, "ShortPredExplicitOver")
    ctx = p.make_supersede_context(pid, "sib", "revised words", label=lab_e201)
    reason = None
    try:
        supersede_proposal(p, pid, "revised words", label=lab_e201,
                           _producer="sib", _review_context=ctx)
    except SupersedeError as e:
        reason = e.reason
    except Exception as e:  # at main: ApprovalError, not the typed refusal
        reason = f"{type(e).__name__}: {e}"
    pred = p.nursery.proposals.get(pid)
    rec("S explicit 201-char label: SupersedeError reason == label_over_budget",
        reason == "label_over_budget", f"reason={reason!r}")
    rec("S explicit 201-char label: predecessor preserved, no successor, no journal",
        pred is not None and pred.status == "confirmed"
        and len(p.nursery.proposals) == 1
        and not os.path.exists(_supersede_journal_path(p.owner)),
        f"pred={None if pred is None else pred.status} n={len(p.nursery.proposals)}")


def smoke() -> bool:
    RESULTS.clear()
    _translate_cases()
    _supersession_cases()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"R24L-SIBLING {passed}/{len(RESULTS)}")
    return all(ok for _, ok in RESULTS)
