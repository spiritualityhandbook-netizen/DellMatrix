"""Master plan P9 — Exchange v1: seed packets with receipts.

Proof standard (grounding packet): CROSS_PROCESS — a packet
exported by one owner, carried as a file, imported by a second
owner in a separate process, gated there, with provenance
intact. Reception law: import lands PENDING, never confirmed,
never auto-learned. Chain lint labels missing links precisely;
the mutant (a receipt with the test method removed) imports
labeled "method absent" and never presents as fully warranted.
Replication is counted (receipts / distinct origins), never
scored. A packet carrying an authority key is refused at the
boundary.
"""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402
from form import persist_rest  # noqa: E402
from form.dell_matrix import exchange as ex  # noqa: E402

RESULTS = []
A = "P9ExchA"
B = "P9ExchB"
TMP = tempfile.mkdtemp(prefix="p9exch_")


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:200]))


def _cleanup(owner):
    base = os.path.join(
        os.path.dirname(__file__), "..", "state")
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json"):
        for f in glob.glob(os.path.join(base, pat)):
            os.remove(f)
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            shutil.rmtree(d)


def _repl(owner, script, load=False):
    root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".."))
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if load:
        args.append("--load")
    return subprocess.run(args, input=script, capture_output=True,
                          text=True, cwd=root, timeout=300)


def smoke() -> bool:
    for o in (A, B):
        _cleanup(o)
    try:
        # --- Owner A: a Keep + two recorded runs (receipts) ---
        a = Program(owner=A)
        prop = a.nursery.add(
            "CountedSampleBeatsGuess",
            words="A counted sample beats an imagined number.",
            origin="host:ace",
            detail="KEEP: a counted sample beats an imagined "
                   "number; guess first, then count, then mirror "
                   "the gap.")
        pid = prop.id
        ex.record_receipt(a, pid, {
            "origin": "ace:paper", "guess": "90",
            "test_method": "count pulse for 15s, multiply by 4",
            "result": "68", "mirror": "-22 (guessed high)",
            "outcome": "keep earned"})
        ex.record_receipt(a, pid, {
            "origin": "teacher:class", "guess": "75",
            "test_method": "count pulse for 15s, multiply by 4",
            "result": "61", "mirror": "-14 (guessed high)",
            "outcome": "keep replicated"})
        a.save()
        a2 = persist_rest.load(A, activate=False)
        _rec("receipts_recorded_and_persisted",
             len(ex.receipts_for(a2, pid)) == 2)

        # --- Export at REAL_USER_PATH (fresh REPL process) ---
        packet_path = os.path.join(TMP, "heart_keep.json")
        r = _repl(A, f"exchange export {pid} {packet_path}\nquit\n",
                  load=True)
        _rec("repl_export_writes_packet",
             r.returncode == 0 and os.path.isfile(packet_path)
             and "2 receipt(s), 2 origin(s)" in r.stdout,
             r.stdout[-160:])
        packet = ex.read_packet(packet_path)
        lint = ex.lint_packet(packet)
        _rec("packet_lint_complete_replication_2x2",
             lint["complete"] is True and lint["receipts"] == 2
             and lint["distinct_origins"] == 2
             and packet["manifest"]["author_origin"] == "host:ace"
             and packet["seed"]["keep"].startswith("KEEP:"))

        # --- Import at REAL_USER_PATH (second owner, new process)
        r = _repl(B, f"exchange import {packet_path}\nproposals\n"
                     "quit\n")
        m = re.search(r"imported as PENDING proposal (\S+)", r.stdout)
        b_pid = m.group(1) if m else ""
        _rec("repl_import_lands_pending_with_warrant",
             r.returncode == 0 and bool(b_pid)
             and "replication: 2 receipt(s), 2 origin(s)" in r.stdout
             and "chain complete" in r.stdout, r.stdout[-200:])
        b = persist_rest.load(B, activate=False)
        bp = b.nursery.proposals.get(b_pid)
        _rec("import_provenance_intact_still_pending",
             bp is not None and bp.status == "pending"
             and bp.origin == "exchange:host:ace"
             and "RECEIPT 2 (teacher:class)" in bp.detail
             and "count pulse for 15s" in bp.detail,
             bp.origin if bp else "missing")

        # --- The receiver's own gate decides ---
        r = _repl(B, f"confirm {b_pid}\nquit\n", load=True)
        b2 = persist_rest.load(B, activate=False)
        _rec("receiver_gate_confirms_import",
             r.returncode == 0
             and b2.nursery.proposals[b_pid].status == "confirmed")

        # --- Chain lint: the mutant (method removed) ---
        broken = json.loads(json.dumps(packet))
        broken["receipts"][0]["test_method"] = ""
        blint = ex.lint_packet(broken)
        _rec("lint_labels_method_absent",
             blint["complete"] is False
             and "receipt 1: method absent" in blint["labels"])
        bout = ex.import_packet(b2, broken)
        bp2 = b2.nursery.proposals.get(bout.get("pid", ""))
        _rec("mutant_imports_labeled_not_warranted",
             bout.get("ok") is True and bp2 is not None
             and bp2.status == "pending"
             and "method absent" in bp2.reason, bp2.reason if bp2
             else "")
        empty = json.loads(json.dumps(packet))
        empty["receipts"] = []
        elint = ex.lint_packet(empty)
        _rec("lint_labels_no_receipts",
             elint["labels"] == ["no receipts"]
             and elint["receipts"] == 0)

        # --- Boundary discipline ---
        evil = json.loads(json.dumps(packet))
        evil["confirm"] = True
        try:
            ex.validate_packet(evil)
            refused = False
        except ex.ExchangeError:
            refused = True
        _rec("authority_key_packet_refused", refused)
        try:
            ex.record_receipt(a2, "no_such_pid", {
                "origin": "x", "guess": "", "test_method": "",
                "result": "", "mirror": "", "outcome": ""})
            refused2 = False
        except ex.ExchangeError:
            refused2 = True
        _rec("receipt_for_unknown_proposal_refused", refused2)
    finally:
        for o in (A, B):
            _cleanup(o)
        shutil.rmtree(TMP, ignore_errors=True)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name} | {detail}")
    print(f"\n=== RESULT: {passed}/{len(RESULTS)} PASS ===")
    return passed == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
