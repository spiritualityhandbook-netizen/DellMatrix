#!/usr/bin/env python3
"""FI-012 row 9 — Nursery label admission + duplicate-intake receipts.

Authority — chat Director bounded build APPROVAL 7203152996 on
PR #508 (2026-11-26), from the failing-first evidence 7198763617:

    "Restrict input validation to the label: reject non-string and
    empty labels with the named typed refusal before mutation.
    Preserve existing lawful labels and other fields' supported
    types. Keep duplicate proposals distinct, uniquely identified
    and independently confirmable; record duplicate intake in memory
    with the established receipt lifecycle. Prove refused inputs
    preserve bytes and live state and that duplicate receipts do
    not persist across reload."

Defects on current main (probe: fi012_evidence/fi012_probe.py):

  * LEG A — add(label=123) raises an UNTYPED AttributeError inside
    _slug ('int' object has no attribute 'lower'): the historical
    isinstance-guards let a non-string label fall through to the
    slugger. No typed refusal exists.
  * LEG B — add(label="") is STORED SILENTLY: only the over-bound
    length check exists, so an empty label is admitted.
  * LEG C — two identical adds (same label/seed/words) are both
    stored with NO receipt or signal: main's Nursery has no
    duplicate_receipts mechanism at all, so the duplicate event is
    silent (the duplicates themselves are lawful — DCC-VII:
    duplicates allowed, unique IDs, both confirmable).

Contract pinned here:

  * A non-string label and an empty label raise NurseryLabelError
    BEFORE any mutation or save; the owner file's bytes and the
    live in-memory state are exactly preserved.
  * Validation is LABEL-ONLY: lawful labels (including exactly
    MAX_LABEL_CHARS) are admitted as before, the over-bound refusal
    is unchanged, and other fields keep their supported types
    (words as a token list — the lock-order census usage — is
    still admitted).
  * A duplicate intake is still stored as its own proposal with a
    distinct ID, and the event is receipted in-memory in
    duplicate_receipts (same lifecycle as suppression_receipts).
    Receipts are NEVER serialized into the owner file and do not
    survive a reload; the stored proposals do.
"""
import hashlib
import json
import os
import tempfile

from form.dell_matrix.nursery import (
    MAX_LABEL_CHARS,
    Nursery,
    NurseryLabelError,
)


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def smoke() -> bool:
    print("=== FI-012 ROW 9 — LABEL ADMISSION + DUPLICATE RECEIPTS ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}"
              + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    pid = os.getpid()
    tmp = tempfile.mkdtemp(prefix="fi012_row9_")
    try:
        # ---- base nursery: one lawful proposal --------------------
        path_a = os.path.join(tmp, f"a{pid}.json")
        na = Nursery.load(path_a)
        base = na.add(label="base idea", seed="1", words="w")
        sha0 = _sha(path_a)
        ids0 = sorted(na.proposals)

        # ---- LEG A: non-string label -> typed refusal -------------
        for bad in (123, None, ["x"], 4.5):
            try:
                na.add(label=bad, seed="1", words="w")
                rec(f"a_nonstring_refused_{type(bad).__name__}", False,
                    "add returned normally (stored silently)")
            except NurseryLabelError:
                rec(f"a_nonstring_refused_{type(bad).__name__}", True)
            except Exception as e:  # untyped crash = the defect
                rec(f"a_nonstring_refused_{type(bad).__name__}", False,
                    f"raised {type(e).__name__}, not NurseryLabelError")
        rec("a_refusal_preserves_bytes", _sha(path_a) == sha0)
        rec("a_refusal_preserves_state",
            sorted(na.proposals) == ids0
            and na.proposals[base.id].label == "base idea")

        # ---- LEG B: empty label -> typed refusal ------------------
        try:
            na.add(label="", seed="1", words="w")
            rec("b_empty_refused", False,
                "add returned normally (stored silently)")
        except NurseryLabelError:
            rec("b_empty_refused", True)
        except Exception as e:
            rec("b_empty_refused", False,
                f"raised {type(e).__name__}, not NurseryLabelError")
        rec("b_refusal_preserves_bytes", _sha(path_a) == sha0)
        rec("b_refusal_preserves_state", sorted(na.proposals) == ids0)

        # ---- label-only scope: lawful labels + other fields -------
        ok200 = na.add(label="x" * MAX_LABEL_CHARS, seed="2", words="w")
        rec("b_label_at_bound_admitted",
            na.proposals[ok200.id].label == "x" * MAX_LABEL_CHARS)
        try:
            na.add(label="x" * (MAX_LABEL_CHARS + 1), seed="2", words="w")
            rec("b_label_over_bound_still_refused", False,
                "add returned normally")
        except NurseryLabelError:
            rec("b_label_over_bound_still_refused", True)
        toks = na.add(label="token words idea", seed="3",
                      words=["tok1", "tok2"])
        rec("b_words_token_list_still_admitted",
            na.proposals[toks.id].words == ["tok1", "tok2"])

        # ---- LEG C: duplicate intake receipted, still stored ------
        path_c = os.path.join(tmp, f"c{pid}.json")
        nc = Nursery.load(path_c)
        rec("c_receipts_start_empty",
            getattr(nc, "duplicate_receipts", None) == [])
        first = nc.add(label="dup idea", seed="7", words="w1")
        rec("c_first_add_no_receipt",
            getattr(nc, "duplicate_receipts", None) == [])
        second = nc.add(label="dup idea", seed="7", words="w1")
        rec("c_duplicate_still_stored_distinct",
            second.id != first.id
            and first.id in nc.proposals and second.id in nc.proposals)
        rec("c_both_pending_independent",
            nc.proposals[first.id].status == "pending"
            and nc.proposals[second.id].status == "pending")
        receipts = getattr(nc, "duplicate_receipts", None) or []
        rec("c_one_receipt_recorded", len(receipts) == 1,
            f"receipts={receipts!r}")
        if receipts:
            rc0 = receipts[0]
            rec("c_receipt_names_both_ids",
                rc0.get("original_id") == first.id
                and rc0.get("duplicate_id") == second.id
                and rc0.get("reason") == "duplicate_intake",
                f"receipt={rc0!r}")
        else:
            rec("c_receipt_names_both_ids", False, "no receipt recorded")
        third = nc.add(label="dup idea", seed="7", words="w1")
        receipts = getattr(nc, "duplicate_receipts", None) or []
        rec("c_third_add_second_receipt",
            len(receipts) == 2 and third.id not in (first.id, second.id)
            and third.id in nc.proposals)
        # near-duplicates are NOT duplicates: same label, other words
        # or other seed record no receipt.
        nc.add(label="dup idea", seed="7", words="different")
        nc.add(label="dup idea", seed="8", words="w1")
        nc.add(label="other idea", seed="7", words="w1")
        receipts = getattr(nc, "duplicate_receipts", None) or []
        rec("c_near_duplicates_no_receipt", len(receipts) == 2,
            f"receipts={len(receipts)}")

        # ---- receipts never persist; proposals do ------------------
        with open(path_c, encoding="utf-8") as f:
            blob = f.read()
        rec("c_receipts_not_serialized",
            "duplicate_receipts" not in blob
            and "duplicate_intake" not in blob)
        reloaded = Nursery.load(path_c)
        rec("c_receipts_empty_after_reload",
            getattr(reloaded, "duplicate_receipts", None) == [])
        rec("c_proposals_survive_reload",
            first.id in reloaded.proposals
            and second.id in reloaded.proposals
            and third.id in reloaded.proposals)
        payload = json.loads(blob)
        rec("c_file_holds_proposals_only_plus_sections",
            all(isinstance(v, dict) for v in payload.values()))
    finally:
        for name in os.listdir(tmp):
            os.unlink(os.path.join(tmp, name))
        os.rmdir(tmp)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)
