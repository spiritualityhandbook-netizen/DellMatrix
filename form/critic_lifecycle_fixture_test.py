"""Critic Findings 5+6 — paired lifecycle repair fixture.

Director disposition 7180713277 (issue #512): ONE lifecycle repair with
SEPARATE restore-side and consumer-side assertions; preserve lawful
legacy absence; refuse malformed present data before binding; keep
selection consistent with the participation verdict.

Finding 5 (consumer side): canonical_lifecycle.is_active() ignored
malformed presence — a record with presence=None (or a whole null
record) yielded is_active=True while is_participating()=False, and
knowledge selection (which gates on is_active) SELECTED the malformed
idea.

Finding 6 (restore side): persist_rest's lifecycle restore filtered
entries with isinstance(v, dict), silently DROPPING whole-entry-null
lifecycle records -> participation flipped to True via the
legacy-absence fallback, and the next re-save erased the evidence.

This fixture pins both defects and the controls:
- lawful legacy ABSENCE (no lifecycle section / no entry) keeps its
  existing treatment before AND after the repair;
- lawful present records round-trip unchanged;
- malformed PRESENT data of entry/section SHAPE (null entry,
  non-dict entry, null/wrong-type section) refuses typed
  (ProgramLoadError) BEFORE binding on restore;
- malformed presence VALUES (null/invalid) follow the settled
  absence-matrix contract: the record loads, is preserved, and is
  excluded by both consumer verdicts — never active, never
  participating, never selected.

Evidence class: INTEGRATION (real Program, real persist_rest
save/load, real knowledge selector; isolated owners).
"""

import hashlib
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(REPO))
os.chdir(REPO)

from form.open import open_program
from form.dell_matrix import canonical_lifecycle as cl
from form.lifecycle import set_presence
from form import persist_rest
from form.persist import _path as program_path

OWNER5 = "CRITF56C"   # consumer-side owner
OWNER6 = "CRITF56R"   # restore-side owner
CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" | {detail}" if detail and not cond else ""))


def clean(owner):
    from form.dell_matrix.nursery import owner_nursery_path
    for p in (program_path(owner), owner_nursery_path(owner)):
        if os.path.isfile(p):
            os.remove(p)


def _confirm(p, pr, producer="test"):
    ctx = p.make_review_context(pr.id, producer)
    r = p.confirm_proposal(pr.id, _producer=producer, _review_context=ctx)
    assert r.get("ok"), r
    return pr.id


def _selected_ids(p, context):
    from form.mandell.knowledge_selector import select_for_context
    out = select_for_context(p, context, "grow")
    ids = [s["id"] for s in out.get("selected", [])]
    ids += [i for i in out.get("baseline_selected_ids", []) if i not in ids]
    return ids


# ---------------------------------------------------------------- F5

def test_f5_consumer_side():
    clean(OWNER5)
    p = open_program(OWNER5)
    # Control: a healthy confirmed idea is active, participating, selected.
    good = _confirm(p, p.nursery.add("GoodIdea",
                                     words="zephyr quill lantern"))
    check("f5_control_active", cl.is_active(p, good))
    check("f5_control_participating",
          cl.is_participating(p, good, "ordinary"))
    check("f5_control_selected",
          good in _selected_ids(p, "zephyr quill lantern"))

    # Malformed presence=None on a confirmed, revision-active idea.
    bad = _confirm(p, p.nursery.add("BadPresence",
                                    words="zephyr quill lantern"))
    p.lifecycle[bad] = {"presence": None, "pinned": False,
                        "registered_seq": None}
    check("f5_malformed_presence_not_participating",
          not cl.is_participating(p, bad, "ordinary")
          and not cl.is_participating(p, bad, "historical"))
    check("f5_malformed_presence_not_active",
          not cl.is_active(p, bad),
          f"is_active={cl.is_active(p, bad)}")
    check("f5_verdicts_agree",
          cl.is_active(p, bad)
          == cl.is_participating(p, bad, "ordinary"))
    check("f5_selection_excludes_malformed",
          bad not in _selected_ids(p, "zephyr quill lantern"),
          f"selected={_selected_ids(p, 'zephyr quill lantern')}")
    check("f5_reason_names_malformed",
          "malformed" in cl.participation_reason(p, bad),
          cl.participation_reason(p, bad))

    # Whole null record in memory: same law.
    bad2 = _confirm(p, p.nursery.add("NullRecord",
                                     words="zephyr quill lantern"))
    p.lifecycle[bad2] = None
    check("f5_null_record_not_active", not cl.is_active(p, bad2),
          f"is_active={cl.is_active(p, bad2)}")
    check("f5_null_record_not_participating",
          not cl.is_participating(p, bad2, "ordinary"))
    check("f5_null_record_not_selected",
          bad2 not in _selected_ids(p, "zephyr quill lantern"))

    # Legacy absence control (consumer side): no record at all still
    # participates under the documented legacy policy.
    check("f5_legacy_absence_participates",
          cl.is_participating(p, "legacy_ghost_f56", "ordinary")
          and cl.is_active(p, "legacy_ghost_f56"))


# ---------------------------------------------------------------- F6

def _load_refusal(owner):
    """Return the ProgramLoadError a load raises, or None."""
    try:
        persist_rest.load(owner, activate=False)
    except persist_rest.ProgramLoadError as e:
        return e
    return None


def test_f6_restore_side():
    clean(OWNER6)
    p = open_program(OWNER6)
    pid = _confirm(p, p.nursery.add("FadedIdea", words="w"))
    set_presence(p, pid, presence="faded")
    p.nursery.save()
    persist_rest.save(p)
    path = program_path(OWNER6)
    with open(path, "rb") as f:
        good_bytes = f.read()
    good_data = json.loads(good_bytes.decode("utf-8"))
    assert good_data["lifecycle"][pid]["presence"] == "faded"

    # Lawful present record: loads, record preserved, faded law holds.
    p2 = persist_rest.load(OWNER6, activate=False)
    check("f6_lawful_record_loads",
          p2.lifecycle.get(pid, {}).get("presence") == "faded")
    check("f6_lawful_record_faded_law",
          cl.is_faded(p2, pid) and not cl.is_active(p2, pid))

    def mutated(mutate):
        data = json.loads(good_bytes.decode("utf-8"))
        mutate(data)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def bytes_now():
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    # Whole-entry-null record: typed refusal before binding, bytes and
    # evidence preserved (no silent drop, no re-save erasure).
    h = mutated(lambda d: d["lifecycle"].__setitem__(pid, None))
    err = _load_refusal(OWNER6)
    check("f6_null_entry_refuses_typed", err is not None)
    check("f6_null_entry_refusal_names_lifecycle",
          err is not None and "lifecycle" in str(err), str(err))
    check("f6_null_entry_bytes_preserved", bytes_now() == h)
    with open(path, encoding="utf-8") as f:
        still = json.load(f)
    check("f6_null_entry_evidence_not_erased",
          pid in still["lifecycle"] and still["lifecycle"][pid] is None)

    # Non-dict entry: typed refusal.
    mutated(lambda d: d["lifecycle"].__setitem__(pid, "faded"))
    err = _load_refusal(OWNER6)
    check("f6_nondict_entry_refuses_typed",
          err is not None and "lifecycle" in str(err), str(err))

    # Present null section: typed refusal (malformed, not absence).
    mutated(lambda d: d.__setitem__("lifecycle", None))
    err = _load_refusal(OWNER6)
    check("f6_null_section_refuses_typed",
          err is not None and "lifecycle" in str(err), str(err))

    # Wrong-type section: typed refusal.
    mutated(lambda d: d.__setitem__("lifecycle", ["faded"]))
    err = _load_refusal(OWNER6)
    check("f6_wrongtype_section_refuses_typed",
          err is not None and "lifecycle" in str(err), str(err))

    # Presence VALUES are the consumer layer's malformed family, per
    # the settled absence-matrix contract (absence_matrix_test
    # test_restart_real_shapes persists presence=None through the
    # real writer): the record LOADS, is PRESERVED (never silently
    # dropped or erased), and is excluded by both consumer verdicts.
    mutated(lambda d: d["lifecycle"][pid].__setitem__("presence", None))
    try:
        p4 = persist_rest.load(OWNER6, activate=False)
        err = None
    except persist_rest.ProgramLoadError as e:
        p4, err = None, e
    check("f6_null_presence_loads", err is None and p4 is not None,
          str(err))
    check("f6_null_presence_record_preserved",
          p4 is not None and pid in p4.lifecycle
          and p4.lifecycle[pid].get("presence") is None)
    check("f6_null_presence_excluded_both_verdicts",
          p4 is not None and not cl.is_active(p4, pid)
          and not cl.is_participating(p4, pid, "ordinary")
          and "malformed" in cl.participation_reason(p4, pid))

    # Invalid presence value: same load-preserve-exclude law.
    mutated(lambda d: d["lifecycle"][pid].__setitem__(
        "presence", "vaporized"))
    try:
        p5 = persist_rest.load(OWNER6, activate=False)
        err = None
    except persist_rest.ProgramLoadError as e:
        p5, err = None, e
    check("f6_invalid_presence_loads_and_excluded",
          err is None and p5 is not None
          and pid in p5.lifecycle
          and not cl.is_active(p5, pid)
          and not cl.is_participating(p5, pid, "ordinary"),
          str(err))

    # Lawful legacy ABSENCE control: section deleted entirely -> the
    # existing legacy treatment, unchanged. Loads; the confirmed idea
    # participates (presence absence = not faded).
    mutated(lambda d: d.pop("lifecycle", None))
    try:
        p3 = persist_rest.load(OWNER6, activate=False)
        err = None
    except persist_rest.ProgramLoadError as e:
        p3, err = None, e
    check("f6_legacy_absence_loads", err is None and p3 is not None,
          str(err))
    check("f6_legacy_absence_participates",
          p3 is not None and cl.is_participating(p3, pid, "ordinary")
          and cl.is_active(p3, pid))

    # Restore the lawful file for any later consumer of this owner.
    with open(path, "wb") as f:
        f.write(good_bytes)


def smoke():
    print("=== CRITIC F5+F6 LIFECYCLE FIXTURE ===")
    for fn in (test_f5_consumer_side, test_f6_restore_side):
        try:
            fn()
        except Exception as e:
            import traceback
            traceback.print_exc()
            check(fn.__name__, False, f"EXC {type(e).__name__}: {e}")
    n = sum(CHECKS)
    print(f"=== {n}/{len(CHECKS)} ===")
    return n == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
