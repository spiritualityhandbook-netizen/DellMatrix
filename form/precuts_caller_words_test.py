"""Q-S2.3 — caller-side [:240] pre-cut repairs (SYSTEM-002).

Two call sites silently cut words at 240 before handing them to the
Nursery, mirroring the store's old cut (creation-commit artifacts,
proven in SYSTEM_002_QS22_QS23_INVESTIGATION_2026-11-15.md):

- exchange.py import_packet: words=seed["keep"][:240] — keep is
  admitted to 2,000 chars (exchange.py:175) and the landed words
  become the confirmed unit's body (confirm_lineage.py:423).
- supersession.py supersede_proposal: words=words[:240] — the
  successor text is unbounded free user text and the operation's
  acceptance hash binds the FULL words (supersession.py:581), so
  approved and stored content silently diverged.

Both callers now pass their text WHOLE. These checks pin the CALLER
contract at the Nursery.add() boundary (the argument captured at the
call), plus the relational invariant that the caller introduces no
cut beyond the store's own admission, plus true end-to-end equality
for texts the store admits on any version.

STORE-DEPENDENCY HONESTY: on main the Nursery store itself still
cuts words at 240 (nursery.py:212) — that is SYS-C29's separate
repair (PR #429: admit to 5,000, refuse beyond). Against the
unrepaired store, a >240 text lands at the store's bound even with
these caller fixes; this suite never claims otherwise. The
relational checks compute the store's admission empirically (a
direct add() of the same text) so they hold on either store version
and become full end-to-end equality once SYS-C29 lands.

Labels: INTEGRATION (production public paths: import_packet,
supersede_proposal). Hygiene: uuid-unique owners; cleanup failures
fail the suite, never swallowed.
"""
from __future__ import annotations

import glob
import os
import shutil
import sys
import uuid

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:10]
OWNER_X = f"PCX{RUN}"
OWNER_S = f"PCS{RUN}"
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "state")


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name +
          (f"  {detail}" if detail and not cond else ""))


def _cleanup(owner):
    for f in glob.glob(os.path.join(STATE, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except Exception as e:  # reported, never swallowed
            _CLEANUP_ERRORS.append(f"{f}: {e}")


def _exact_text(sentence, n):
    s = (sentence * (n // len(sentence) + 1))[:n].strip()
    return s + "x" * (n - len(s))


def _capture_add(nursery):
    captured = []
    orig = nursery.add

    def wrapper(*a, **kw):
        if "words" in kw:
            captured.append(kw["words"])
        elif len(a) > 1:
            captured.append(a[1])
        else:
            captured.append(None)
        return orig(*a, **kw)

    nursery.add = wrapper
    return captured, orig


def _exchange_checks():
    from form.open import open_program
    from form.dell_matrix import exchange as ex

    keep = _exact_text("kept body text carries the full idea. ", 1500)
    packet = {
        "version": ex.PACKET_VERSION,
        "seed": {"label": "Precut Probe", "chain": "", "keep": keep},
        "manifest": {"author_origin": "host:probe",
                     "created": "2026-11-15T00:00:00Z",
                     "registry": ex.REGISTRY_STAMP, "requirements": []},
        "receipts": [{"origin": "probe:local", "guess": "g",
                      "test_method": "m", "result": "r",
                      "mirror": "mi", "outcome": "o"}],
    }
    try:
        recv = open_program(OWNER_X)
        captured, orig = _capture_add(recv.nursery)
        try:
            out = ex.import_packet(recv, packet)
        finally:
            recv.nursery.add = orig
        prop = recv.nursery.proposals.get(out.get("pid", ""))
        _rec("X1.exchange_caller_passes_keep_whole",
             bool(captured) and captured[-1] == keep,
             f"captured len={len(captured[-1]) if captured else 'none'}")
        # The store's own admission of the same text, probed directly:
        probe = recv.nursery.add("StoreProbe", words=keep)
        _rec("X2.exchange_no_cut_beyond_store",
             prop is not None and prop.words == probe.words,
             f"landed={len(prop.words) if prop else 'none'} "
             f"store={len(probe.words)}")
        # End-to-end exact where the store admits on any version:
        packet2 = dict(packet)
        packet2["seed"] = {"label": "Precut Short", "chain": "",
                           "keep": _exact_text("short kept text. ", 200)}
        out2 = ex.import_packet(recv, packet2)
        prop2 = recv.nursery.proposals.get(out2.get("pid", ""))
        _rec("X3.exchange_short_keep_end_to_end_exact",
             prop2 is not None
             and prop2.words == packet2["seed"]["keep"],
             f"landed len={len(prop2.words) if prop2 else 'none'}")
    finally:
        _cleanup(OWNER_X)


def _supersession_checks():
    from form.open import open_program
    from form.mandell import supersession as sup
    from form.dell_matrix.acceptance_policy import canonical_hash

    words = _exact_text("The successor revises the predecessor fully. ",
                        1000)
    try:
        p = open_program(OWNER_S)
        try:
            p.acceptance_policy.grant_opt_in(OWNER_S, scope="test")
        except AttributeError:
            pass
        pred = p.nursery.add("PredLong", words="predecessor content")
        ctx = p.make_review_context(pred.id, OWNER_S)
        r = p.confirm_proposal(pred.id, _producer=OWNER_S,
                               _review_context=ctx)
        _rec("S0.supersession_setup_pred_confirmed", bool(r.get("ok")),
             f"confirm={r}")
        eff_label = f"revision of {pred.label}"
        _rec("S1.acceptance_hash_binds_full_text",
             canonical_hash({"label": eff_label, "words": words})
             != canonical_hash({"label": eff_label,
                                "words": words[:240]}))
        captured, orig = _capture_add(p.nursery)
        try:
            receipt = sup.supersede_proposal(
                p, pred.id, words=words, _producer=OWNER_S)
        finally:
            p.nursery.add = orig
        succ = p.nursery.proposals.get(receipt.get("new_id", ""))
        _rec("S2.supersession_caller_passes_words_whole",
             bool(captured) and captured[-1] == words,
             f"captured len={len(captured[-1]) if captured else 'none'}")
        probe = p.nursery.add("StoreProbe", words=words)
        _rec("S3.supersession_no_cut_beyond_store",
             succ is not None and succ.words == probe.words,
             f"stored={len(succ.words) if succ else 'none'} "
             f"store={len(probe.words)}")
        # End-to-end exact where the store admits on any version:
        short = _exact_text("A brief successor statement. ", 200)
        pred2 = p.nursery.add("PredShort", words="predecessor two")
        ctx2 = p.make_review_context(pred2.id, OWNER_S)
        p.confirm_proposal(pred2.id, _producer=OWNER_S,
                           _review_context=ctx2)
        rec2 = sup.supersede_proposal(p, pred2.id, words=short,
                                      _producer=OWNER_S)
        succ2 = p.nursery.proposals.get(rec2.get("new_id", ""))
        _rec("S4.supersession_short_text_end_to_end_exact",
             succ2 is not None and succ2.words == short,
             f"stored len={len(succ2.words) if succ2 else 'none'}")
        # Scope guard: the sibling label slice at the same site is NOT
        # part of this circuit (Q-S2.1's field) — a 100-char explicit
        # label still lands at the unchanged 80-char bound.
        pred3 = p.nursery.add("PredLabel", words="predecessor three")
        ctx3 = p.make_review_context(pred3.id, OWNER_S)
        p.confirm_proposal(pred3.id, _producer=OWNER_S,
                           _review_context=ctx3)
        rec3 = sup.supersede_proposal(
            p, pred3.id, words="label scope probe",
            label="L" * 100, _producer=OWNER_S)
        succ3 = p.nursery.proposals.get(rec3.get("new_id", ""))
        _rec("S5.sibling_label_slice_untouched",
             succ3 is not None and len(succ3.label) == 80,
             f"label len={len(succ3.label) if succ3 else 'none'}")
    finally:
        _cleanup(OWNER_S)


def smoke() -> bool:
    for owner in (OWNER_X, OWNER_S):
        _cleanup(owner)
    _exchange_checks()
    _supersession_checks()
    for e in _CLEANUP_ERRORS:
        _rec("cleanup", False, e)
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"precuts_caller_words_test: {passed}/{len(RESULTS)} PASS")
    return all(ok for _, ok in RESULTS) and len(RESULTS) > 0


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
