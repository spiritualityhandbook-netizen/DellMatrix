"""Absence-vs-malformation matrix (Director 2026-10-05 close).

Table-driven: both helpers x ordinary/historical contexts x
constructor/load paths. Genuine legacy positives and valid controls
alongside malformed negatives. Invalid cases excluded with accurate
reasons. Fixtures use real persisted shapes for restart.

Evidence class: INTEGRATION (real Program where applicable).
"""

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(REPO))

from types import SimpleNamespace
from form.dell_matrix import canonical_lifecycle as cl
from form.dell_matrix.nursery import Proposal

CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" | {detail}" if detail and not cond else ""))


# Sentinel for 'do not set this attribute'
_SKIP = object()


def make_prog(lifecycle=_SKIP, proposals=_SKIP):
    ns = SimpleNamespace()
    if lifecycle is not _SKIP:
        ns.lifecycle = lifecycle
    if proposals is not _SKIP:
        ns.nursery = SimpleNamespace(proposals=proposals)
    return ns


# Each row: (name, lifecycle, proposals, expect_ordinary, expect_historical,
#            expect_malformed, reason_substring)
MATRIX = [
    # --- Genuine legacy positives ---
    ("legacy_no_attrs", _SKIP, _SKIP, True, True, False, ""),
    ("legacy_empty_dicts", {}, {}, True, True, False, ""),
    ("legacy_uid_absent", {"B": {"presence": "active"}}, {"B": Proposal(id="B", label="b", words="w", kind="new", status="confirmed")}, True, True, False, ""),

    # --- Valid controls ---
    ("valid_active", {"A": {"presence": "active"}}, {"A": Proposal(id="A", label="a", words="w", kind="new", status="confirmed")}, True, True, False, ""),
    ("valid_faded", {"A": {"presence": "faded"}}, {"A": Proposal(id="A", label="a", words="w", kind="new", status="confirmed")}, False, True, False, ""),
    ("valid_pending", {"A": {"presence": "active"}}, {"A": Proposal(id="A", label="a", words="w", kind="new", status="pending")}, False, False, False, "pending"),
    ("valid_rejected", {"A": {"presence": "active"}}, {"A": Proposal(id="A", label="a", words="w", kind="new", status="rejected")}, False, False, False, "rejected"),
    ("valid_presence_absent", {"A": {}}, {"A": Proposal(id="A", label="a", words="w", kind="new", status="confirmed")}, True, True, False, ""),

    # --- Director's five malformed cases ---
    ("mal_lifecycle_null_record", {"A": None}, {}, False, False, True, "null_record"),
    ("mal_presence_null_value", {"A": {"presence": None}}, {}, False, False, True, "null_value"),
    ("mal_lifecycle_wrong_container", [], {}, False, False, True, "wrong_container"),
    ("mal_proposals_null_record", {}, {"A": None}, False, False, True, "null_record"),
    ("mal_proposals_wrong_container", {}, [], False, False, True, "wrong_container"),

    # --- Additional malformed ---
    ("mal_presence_wrong_record", {"A": "faded"}, {}, False, False, True, "wrong_record_type"),
    ("mal_presence_invalid_value", {"A": {"presence": "vaporized"}}, {}, False, False, True, "invalid_value"),
    ("mal_status_null", {}, {"A": Proposal(id="A", label="a", words="w", kind="new", status=None)}, False, False, True, "null_value"),
    ("mal_status_invalid", {}, {"A": Proposal(id="A", label="a", words="w", kind="new", status="bogus")}, False, False, True, "invalid_value"),
    ("mal_status_wrong_record", {}, {"A": SimpleNamespace()}, False, False, True, "wrong_record_type"),
]


def test_matrix():
    for name, lc, props, exp_ord, exp_hist, exp_mal, reason_sub in MATRIX:
        p = make_prog(lifecycle=lc, proposals=props)
        got_ord = cl.is_participating(p, "A", "ordinary")
        got_hist = cl.is_participating(p, "A", "historical")
        _, pres_mal, pres_reason = cl._presence_state(p, "A")
        _, acc_mal, acc_reason = cl._acceptance_state(p, "A")
        got_mal = pres_mal or acc_mal
        # Prefer the malformed helper's reason; fall back to participation reason
        if pres_mal:
            reason = pres_reason
        elif acc_mal:
            reason = acc_reason
        else:
            reason = cl.participation_reason(p, "A", "ordinary")
        check(f"{name}:ordinary", got_ord == exp_ord,
              f"expected {exp_ord}, got {got_ord}")
        check(f"{name}:historical", got_hist == exp_hist,
              f"expected {exp_hist}, got {got_hist}")
        check(f"{name}:malformed", got_mal == exp_mal,
              f"expected malformed={exp_mal}, got {got_mal}")
        if reason_sub:
            check(f"{name}:reason", reason_sub in reason,
                  f"expected {reason_sub!r} in {reason!r}")


def test_restart_real_shapes():
    """Restart with real persisted malformed shapes stays excluded."""
    from form.open import open_program
    from form import persist_rest
    owner = "MATRIX_RST"
    for pat in [f'form/state/nursery_{owner}.json', f'form/state/program_{owner}.json']:
        pp = os.path.join(REPO, pat)
        if os.path.isfile(pp):
            os.remove(pp)
    p = open_program(owner)
    pr = p.nursery.add("MR", words="w")
    ctx = p.make_review_context(pr.id, "test")
    assert p.confirm_proposal(pr.id, _producer="test", _review_context=ctx).get("ok")
    pid = pr.id
    # Corrupt presence to explicit null (real persisted shape)
    from form.lifecycle import ensure_lifecycle
    lc = ensure_lifecycle(p)
    lc[pid] = {"presence": None, "pinned": False}
    p.nursery.save()
    persist_rest.save(p)
    p2 = persist_rest.load(owner, activate=False)
    check("restart_null_presence_excluded",
          not cl.is_participating(p2, pid, "ordinary")
          and not cl.is_participating(p2, pid, "historical"))
    check("restart_null_presence_reason",
          "malformed" in cl.participation_reason(p2, pid),
          cl.participation_reason(p2, pid))


def smoke():
    print("=== ABSENCE-VS-MALFORMATION MATRIX ===")
    try:
        test_matrix()
    except Exception as e:
        check("test_matrix", False, f"EXC {type(e).__name__}: {e}")
    try:
        test_restart_real_shapes()
    except Exception as e:
        check("test_restart_real_shapes", False, f"EXC {type(e).__name__}: {e}")
    n = sum(CHECKS)
    print(f"=== {n}/{len(CHECKS)} ===")
    return n == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
