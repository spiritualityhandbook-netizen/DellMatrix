#!/usr/bin/env python3
"""Q-S2.2 — Nursery reason bound: admitted reasons stored losslessly
to the admitted 1,000-char bound; beyond it, explicit refusal before
any mutation or save.

The defect (failing-first, reproduced on the unrepaired head):
the inference dock admits a proposal reason up to 1,000 chars at
three admission points (inference_dock.py: host reason in propose(),
host reason at the semantic-verb entry, model reason in
validate_semantic_output), and director_session.py declares the same
bound (MAX_REASON_CHARS = 1000) — but Nursery.add() stored
reason[:160], silently destroying admitted content. The dock-session
evidence validator (dock_session.py) mirrored the 160 cut even
though its entries carry the stored reason verbatim; it is
reconciled to the shared bound in the same circuit (R6).

Checks (isolated temp paths throughout; no owner state touched):
- R1 admitted-max 1,000-char reason stored EXACTLY (memory + disk).
- R2 boundaries 160 / 161 stored exactly (161 was cut before).
- R3 1,001 chars refused with NurseryReasonError BEFORE mutation:
  in-memory proposal count unchanged, on-disk bytes byte-identical,
  fresh load unchanged.
- R4 unicode reason stored exactly (chars, not bytes).
- R5 legacy record (a 160-char reason as the old code wrote it)
  loads intact and round-trips through a later save.
- R6 dock_session validator accepts a 500-char reason end-to-end
  (record built via new_record + append_proposal, the same shapes
  inference_dock._record_evidence writes), and still refuses a
  1,001-char reason entry.
- R7 fresh-process reload: a separate interpreter loads the file
  and exact-compares every stored reason.
- R8 (Q-S2.2-R.1, Director mail 1a1df854c1938a47): exchange
  public-path atomicity. import_packet composes its reason from
  the packet's lint labels with NO pre-cut; a degenerate packet
  (10 receipts with blank guess/method/result/mirror/outcome ->
  50 lint labels) composes a reason past the 1,000 bound, so
  Nursery.add refuses mid-import. The import must surface that
  refusal typed and land NOTHING: nursery count and file bytes,
  program file bytes, recorded receipts/seeds and the import
  journal all unchanged, and a normal import still lands after.

Labels: UNIT_SYNTHETIC / INTEGRATION (direct Nursery + dock_session
authorities, isolated temp files; R8 drives a real Program +
exchange import under a per-owner isolated state name with loud
cleanup, the af6 harness pattern). No dock session is driven; the
public dock path is covered by the dock suites in the neighbor set.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _reason(n, seed_text="evidence for the judgment: "):
    """A deterministic n-char reason."""
    reps = (seed_text * (n // len(seed_text) + 1))[:n]
    assert len(reps) == n
    return reps


def _fresh_nursery(tmp, name="nursery_t.json"):
    from form.dell_matrix.nursery import Nursery
    return Nursery.load(os.path.join(tmp, name)), os.path.join(tmp, name)


def smoke() -> bool:
    from form.dell_matrix.nursery import (
        MAX_REASON_CHARS, Nursery, NurseryReasonError)

    tmp = tempfile.mkdtemp(prefix="nursery_reason_bound_")
    assert MAX_REASON_CHARS == 1000, MAX_REASON_CHARS

    # R1: admitted-max stored exactly, memory + disk.
    n, path = _fresh_nursery(tmp, "r1.json")
    r1000 = _reason(1000)
    p = n.add("admitted max", words="w", reason=r1000)
    check("R1.admitted1000_exact_memory", p.reason == r1000,
          f"len={len(p.reason)}")
    fresh = Nursery.load(path)
    check("R1.admitted1000_exact_disk",
          fresh.proposals[p.id].reason == r1000)

    # R2: boundaries 160 / 161 both stored exactly (161 was cut).
    n, path = _fresh_nursery(tmp, "r2.json")
    p160 = n.add("boundary 160", words="w", reason=_reason(160))
    p161 = n.add("boundary 161", words="w", reason=_reason(161))
    check("R2.boundary160_161_exact",
          p160.reason == _reason(160) and p161.reason == _reason(161),
          f"160:{len(p160.reason)} 161:{len(p161.reason)}")

    # R3: 1,001 refused BEFORE mutation — memory, disk, fresh load.
    before_count = len(n.proposals)
    with open(path, "rb") as f:
        before_bytes = f.read()
    refused = None
    try:
        n.add("oversize", words="w", reason=_reason(1001))
    except NurseryReasonError as e:
        refused = e
    except Exception as e:  # wrong error type is a failure, not a pass
        refused = None
        check("R3.refused_error_type", False, f"wrong error: {type(e)}")
    check("R3.refused_explicitly", isinstance(refused, NurseryReasonError),
          "reason-error" if refused else "no-raise")
    check("R3.no_inmemory_mutation", len(n.proposals) == before_count,
          f"count={len(n.proposals)}")
    with open(path, "rb") as f:
        after_bytes = f.read()
    check("R3.no_disk_mutation", before_bytes == after_bytes,
          f"bytes {len(before_bytes)} -> {len(after_bytes)}")
    fresh = Nursery.load(path)
    check("R3.fresh_load_unchanged",
          len(fresh.proposals) == before_count
          and fresh.proposals[p161.id].reason == _reason(161))

    # R4: unicode stored exactly (char-exact, incl. multibyte + emoji).
    n, path = _fresh_nursery(tmp, "r4.json")
    uni = ("raison d'être — l'évidence est claire, "
           "理由は明確です, and the gate reads it all 🎯 ") 
    uni = (uni * 12)[:600]
    assert len(uni) == 600
    p = n.add("unicode reason", words="w", reason=uni)
    fresh = Nursery.load(path)
    check("R4.unicode600_exact",
          p.reason == uni and fresh.proposals[p.id].reason == uni,
          f"len={len(p.reason)}")

    # R5: legacy record (160-char reason, as pre-repair code wrote it)
    # loads intact and round-trips through a later save.
    n, path = _fresh_nursery(tmp, "r5.json")
    legacy_reason = _reason(160)
    lp = n.add("legacy record", words="w", reason=legacy_reason)
    n2 = Nursery.load(path)
    ok_load = n2.proposals[lp.id].reason == legacy_reason
    n2.add("later arrival", words="w", reason=_reason(500))
    n3 = Nursery.load(path)
    check("R5.legacy_loads_and_roundtrips",
          ok_load and n3.proposals[lp.id].reason == legacy_reason
          and len(n3.proposals) == 2,
          f"legacy len={len(n3.proposals[lp.id].reason)}")

    # R6: dock_session validator, end-to-end at the shared bound.
    from form.dell_matrix import dock_session as ds
    owner = "reason-bound-owner"
    rec = ds.new_record(owner, "host", "fake", "model-x", "propose",
                        "snap")
    entry = {
        "pid": p.id,
        "ts": "2026-11-15T00:00:00Z",
        "task": "propose",
        "reason": _reason(500),
        "origin": "dock:fake:model-x",
        "prompt_hash": hashlib.sha256(b"prompt").hexdigest(),
        "prompt_summary": "a prompt",
        "prompt_chars": 6,
        "snapshot_id": None,
        "model": "model-x",
    }
    ds.append_proposal(rec, dict(entry))
    ok500, err500 = ds.validate(rec, owner)
    check("R6.validator_accepts_500", ok500, err500)
    rec_bad = ds.new_record(owner, "host", "fake", "model-x",
                            "propose", "snap")
    bad = dict(entry)
    bad["reason"] = _reason(1001)
    ds.append_proposal(rec_bad, bad)
    ok1001, _ = ds.validate(rec_bad, owner)
    check("R6.validator_refuses_1001", not ok1001)

    # R7: fresh-process reload exact-compares every stored reason.
    n, path = _fresh_nursery(tmp, "r7.json")
    expected = {}
    for i, ln in enumerate((160, 161, 500, 1000)):
        pp = n.add(f"reload {ln}", words="w", reason=_reason(ln))
        expected[pp.id] = _reason(ln)
    code = (
        "import json, sys\n"
        "from form.dell_matrix.nursery import Nursery\n"
        f"n = Nursery.load({path!r})\n"
        "out = {pid: p.reason for pid, p in n.proposals.items()}\n"
        "sys.stdout.write(json.dumps(out, sort_keys=True))\n"
    )
    r = subprocess.run([sys.executable, "-c", code],
                       capture_output=True, text=True)
    import json as _json
    got = _json.loads(r.stdout) if r.returncode == 0 else {}
    check("R7.fresh_process_exact_compare", got == expected,
          f"proposals={sorted(got)} rc={r.returncode}")

    # R8: exchange public-path atomicity (Q-S2.2-R.1). Real
    # Program, per-owner isolated state, loud cleanup (af6
    # pattern). import_packet traced at exchange.py:688: validate
    # -> protected screen -> preflight (read-only) -> journal
    # intent -> nursery.add -> receipts/seeds -> one save. The
    # add() refusal fires before any of the post-landing stages.
    import glob
    import shutil
    from form import persist as _persist
    from form import persist_rest as _persist_rest
    from form.dell_matrix import exchange as _exchange
    from form.dell_matrix.nursery import NurseryReasonError as _NRE
    from form.open import Program as _Program

    def _cleanup_r8(owner):
        base = os.path.join("form", "state")
        if not os.path.isdir(base):
            return
        failed = []
        pats = (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*",
                f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json",
                f"exchange_import_{owner}.journal.json",
                f"gen_{owner}_*", f"current_{owner}.json")
        for pat in pats:
            for f in glob.glob(os.path.join(base, pat)):
                try:
                    os.remove(f)
                except OSError as e:
                    failed.append(f"{f}: {e}")
        for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
            if os.path.isdir(d):
                try:
                    shutil.rmtree(d)
                except OSError as e:
                    failed.append(f"{d}: {e}")
        if failed:
            raise RuntimeError(
                "R8 cleanup failed: " + "; ".join(failed))

    def _r8_packet(label, receipts):
        return {
            "version": 1,
            "seed": {"label": label, "chain": "", "keep": "R8-KEEP"},
            "manifest": {"author_origin": "r8:origin",
                         "created": "2026-11-15T00:00:00Z",
                         "registry": "core1:00-50,core2:51-99",
                         "requirements": []},
            "receipts": receipts,
        }

    def _filled_receipt():
        return {"origin": "r8:origin", "guess": "g",
                "test_method": "m", "result": "r", "mirror": "mi",
                "outcome": "o"}

    def _blank_receipt():
        # Valid at the boundary (origin non-empty, rest strings
        # within bounds) but every linted field blank -> 5 lint
        # labels per receipt.
        return {"origin": "r8:origin", "guess": "",
                "test_method": "", "result": "", "mirror": "",
                "outcome": ""}

    owner8 = "ReasonBoundR8"
    _cleanup_r8(owner8)
    try:
        prog = _Program(owner=owner8)
        # Baseline: a normal import lands whole, so the state the
        # degenerate import must preserve is real, not empty.
        base = _exchange.import_packet(
            prog, _r8_packet("r8-baseline",
                             [_filled_receipt(), _filled_receipt()]))
        check("R8.baseline_import_lands", base.get("ok") is True,
              str(base)[:120])
        npath = prog.nursery.path
        ppath = _persist._path(owner8)
        jpath = _exchange._import_journal_path(owner8)

        def _snap():
            with open(npath, "rb") as f:
                nb = f.read()
            with open(ppath, "rb") as f:
                pb = f.read()
            return {
                "proposals": len(prog.nursery.proposals),
                "receipts": len(getattr(prog, "exchange_receipts",
                                        {}) or {}),
                "seeds": len(getattr(prog, "exchange_seeds",
                                     {}) or {}),
                "nursery_bytes": nb,
                "program_bytes": pb,
                "journal_present": os.path.isfile(jpath),
            }

        before = _snap()
        check("R8.baseline_journal_cleared",
              not before["journal_present"])

        # Degenerate packet: 10 blank receipts -> 50 lint labels.
        # Self-verify the composed reason really passes the bound,
        # recomposed exactly as import_packet composes it.
        degen = _r8_packet("r8-degenerate",
                           [_blank_receipt() for _ in range(10)])
        lint = _exchange.lint_packet(_exchange.validate_packet(degen))
        man = degen["manifest"]
        composed = (
            f"exchange import from {man['author_origin']} · "
            f"replication: {lint['receipts']} receipt(s), "
            f"{lint['distinct_origins']} distinct origin(s) · "
            f"lint: {'; '.join(lint['labels'])}")
        check("R8.degenerate_reason_past_bound",
              len(composed) > MAX_REASON_CHARS,
              f"composed len={len(composed)} labels={len(lint['labels'])}")

        # Drive the public import path. What the caller receives
        # today (traced at exchange.py:780-793): import_packet
        # clears the intent journal and re-raises the store's
        # typed NurseryReasonError unwrapped — a named exception
        # whose message states the bound and "refused, nothing
        # stored". Assert exactly that surface.
        raised = None
        returned = None
        try:
            returned = _exchange.import_packet(prog, degen)
        except Exception as e:  # captured for assertion below
            raised = e
        check("R8.refusal_surfaces_typed",
              isinstance(raised, _NRE) and returned is None,
              f"raised={type(raised).__name__ if raised else None} "
              f"returned={returned}")
        check("R8.refusal_names_bound",
              raised is not None
              and str(MAX_REASON_CHARS) in str(raised),
              str(raised)[:120] if raised else "no-raise")

        after = _snap()
        check("R8.no_proposal_landed",
              after["proposals"] == before["proposals"],
              f"{before['proposals']} -> {after['proposals']}")
        check("R8.no_receipts_or_seeds_recorded",
              after["receipts"] == before["receipts"]
              and after["seeds"] == before["seeds"],
              f"receipts {before['receipts']}->{after['receipts']} "
              f"seeds {before['seeds']}->{after['seeds']}")
        check("R8.nursery_file_bytes_unchanged",
              after["nursery_bytes"] == before["nursery_bytes"],
              f"{len(before['nursery_bytes'])} -> "
              f"{len(after['nursery_bytes'])} bytes")
        check("R8.program_file_bytes_unchanged",
              after["program_bytes"] == before["program_bytes"],
              f"{len(before['program_bytes'])} -> "
              f"{len(after['program_bytes'])} bytes")
        check("R8.no_journal_residue",
              not after["journal_present"]
              and _exchange._read_import_journal(owner8) is None)
        reloaded = _persist_rest.load(owner8, activate=False)
        check("R8.fresh_load_unchanged",
              len(reloaded.nursery.proposals) == before["proposals"],
              f"reloaded={len(reloaded.nursery.proposals)}")

        # The importer remains usable: a normal import lands
        # after the refused one.
        post = _exchange.import_packet(
            prog, _r8_packet("r8-after", [_filled_receipt()]))
        check("R8.importer_usable_after_refusal",
              post.get("ok") is True
              and len(prog.nursery.proposals)
              == before["proposals"] + 1,
              str(post)[:120])
    finally:
        _cleanup_r8(owner8)

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"nursery_reason_bound_test: {passed}/{len(RESULTS)} PASS")
    return passed == len(RESULTS)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
