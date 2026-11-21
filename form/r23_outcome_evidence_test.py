#!/usr/bin/env python3
"""GP-E02 / R23 — outcome evidence completeness + reachable search.

Edition 1 spec (02_EXECUTION_CIRCUITS.md, GP-E02): capture evidence
of executed actions without silently losing field text or message
counts. Preserve full bounded admitted evidence, or explicitly
reject before append; do not replace raw evidence with a fictional
summary.

Failing-first cases named by the spec, measured at main af2519b6
before this suite was written (form/mandell/outcome_ledger.py):
_bound() truncates silently at _MAX_INPUT=200, _MAX_ERROR=300,
_MAX_MESSAGE=200, _MAX_MESSAGES=12, _MAX_STATE_NOTE=300,
_MAX_FLOW_PROGRAM=500 (outcome_ledger.py:83-88, 362-404), and
find_outcomes() clamps any requested limit to 100 with no page,
cursor or total disclosure (outcome_ledger.py:471-498).

Contract asserted per field: the stored record carries the field
EXACTLY as supplied, or capture refuses (returns None / a record
carrying an explicit refusal) — a silently shortened field fails.
Search contract: 150 matching records with limit=500 requested
return all 150, or a truthful page that discloses the total.

Labels: INTEGRATION — build_outcome/capture_outcome exercised
directly on an in-memory host object (build_outcome is documented
pure; capture_outcome only needs outcome_records/outcome_seq).
No files, no persistent state.
"""
from __future__ import annotations

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _host():
    return SimpleNamespace(owner="R23Probe", outcome_seq=0,
                           outcome_records={}, last_outcome=None,
                           last_nurture=None)


def _receipt(**kw):
    base = dict(action="probe", mandell="00[Probe]", dell=0,
                semantic="", input="", error="", messages=[],
                state_note="")
    base.update(kw)
    return SimpleNamespace(**base)


def _field_exact_or_refused(rec, field, exact):
    if rec is None:
        return True  # explicit refusal before append is lawful
    if rec.get("refused") or rec.get("refusal"):
        return True
    return rec.get(field) == exact


def run_all():
    from form.mandell.outcome_ledger import capture_outcome, find_outcomes

    host = _host()
    inp250 = "I" * 250
    rec = capture_outcome(host, _receipt(input=inp250))
    check("spec input 250 exact-or-refused",
          _field_exact_or_refused(rec, "input", inp250),
          f"stored len={len((rec or {}).get('input', ''))}")

    host = _host()
    err400 = "E" * 400
    rec = capture_outcome(host, _receipt(error=err400))
    check("spec error 400 exact-or-refused",
          _field_exact_or_refused(rec, "error", err400),
          f"stored len={len((rec or {}).get('error', ''))}")

    host = _host()
    msg250 = "M" * 250
    rec = capture_outcome(host, _receipt(messages=[msg250]))
    msgs = (rec or {}).get("messages") or []
    check("spec message 250 exact-or-refused",
          rec is None or msgs == [msg250],
          f"stored={[len(m) for m in msgs]}")

    host = _host()
    msgs15 = [f"m{i:02d}" for i in range(15)]
    rec = capture_outcome(host, _receipt(messages=msgs15))
    got = (rec or {}).get("messages") or []
    check("spec 15 messages all retained-or-refused",
          rec is None or got == msgs15,
          f"stored count={len(got)}")

    host = _host()
    note400 = "S" * 400
    rec = capture_outcome(host, _receipt(state_note=note400))
    check("spec state note 400 exact-or-refused",
          _field_exact_or_refused(rec, "state_note", note400),
          f"stored len={len((rec or {}).get('state_note', ''))}")

    host = _host()
    flow600 = "F" * 600
    rec = capture_outcome(host, _receipt(),
                          composition={"flow_program": flow600})
    stored_flow = ""
    if rec:
        comp = rec.get("composition") or {}
        stored_flow = comp.get("flow_program", "") or ""
    check("spec flow program 600 exact-or-refused",
          rec is None or stored_flow == flow600,
          f"stored len={len(stored_flow)}")

    host = _host()
    for i in range(150):
        capture_outcome(host, _receipt(input=f"zqxneedle record {i}"))
    found = find_outcomes(host, "zqxneedle", limit=500)
    check("spec search 150 matches at limit 500 all reachable",
          len(found) == 150,
          f"returned={len(found)} (silent 100 cap fails this)")

    # Regression pins: inside the historical bounds, capture is
    # exact today and must stay exact after the repair.
    host = _host()
    rec = capture_outcome(host, _receipt(input="short input",
                                         error="short error",
                                         messages=["one", "two"],
                                         state_note="short note"))
    check("pin: short evidence exact",
          rec is not None and rec.get("input") == "short input"
          and rec.get("error") == "short error"
          and rec.get("messages") == ["one", "two"]
          and rec.get("state_note") == "short note")
    found = find_outcomes(host, "short", limit=500)
    check("pin: small search returns the match", len(found) == 1)

    # --- GP-E02 correction (Director 7066282827, CORRECTION REQUIRED):
    # capture_outcome must not swallow EvidenceOverBudget into a bare
    # None indistinguishable from ledger-absent/invalid. Every capture
    # attempt leaves a typed diagnostic (status capture_unavailable +
    # reason) readable via outcome_ledger.last_capture_diagnostic, and
    # the budget binds at total-record level, not only per field/count.
    from form.mandell import outcome_ledger as _ol
    from form.mandell.outcome_ledger import get_outcome_by_seq, list_outcomes

    diag_of = getattr(_ol, "last_capture_diagnostic", None)
    total_cap = getattr(_ol, "_MAX_TOTAL_EVIDENCE", 1_000_000)

    def _diag(h):
        if diag_of is None:
            return None
        try:
            return diag_of(h)
        except Exception:
            return None

    # (1a) Oversized single field: zero append, seq unmoved, typed
    # budget provenance (field/length/budget), not a bare None.
    host = _host()
    ok_rec = capture_outcome(host, _receipt(input="baseline capture"))
    rec = capture_outcome(host, _receipt(input="B" * 100_001))
    d = _diag(host)
    check("gpe02 oversized input: zero append + typed budget provenance",
          rec is None and ok_rec is not None
          and len(host.outcome_records) == 1 and host.outcome_seq == 1
          and d is not None and d.get("status") == "capture_unavailable"
          and d.get("reason") == "evidence_over_budget"
          and d.get("field") == "input"
          and d.get("length") == 100_001
          and d.get("budget") == 100_000,
          f"diag={d}")

    # (1b) Oversized message count: zero append + typed provenance.
    host = _host()
    rec = capture_outcome(host, _receipt(messages=["m"] * 10_001))
    d = _diag(host)
    check("gpe02 oversized message count: zero append + typed provenance",
          rec is None and len(host.outcome_records) == 0
          and d is not None and d.get("reason") == "evidence_over_budget"
          and d.get("field") == "messages",
          f"diag={d}")

    # (5) Total-record budget: every field under its per-field cap and
    # the count under its cap, but the composed total over the total
    # cap -> typed refusal, zero append. (Pre-repair this CAPTURES:
    # 20 x 60,000 chars would be retained by the ledger.)
    host = _host()
    many = ["T" * 60_000 for _ in range(20)]
    rec = capture_outcome(host, _receipt(messages=many))
    d = _diag(host)
    check("gpe02 total-record budget: over total -> typed refusal",
          rec is None and len(host.outcome_records) == 0
          and d is not None and d.get("reason") == "evidence_over_budget"
          and d.get("field") == "total"
          and d.get("length") == 1_200_000
          and d.get("budget") == total_cap,
          f"diag={d}")

    # (1c) Budget refusal is distinguishable from ledger absent and
    # ledger invalid — three different typed reasons.
    host_absent = SimpleNamespace(owner="R23Probe", outcome_seq=0,
                                  outcome_records=None, last_outcome=None,
                                  last_nurture=None)
    rec_a = capture_outcome(host_absent, _receipt(input="x"))
    d_absent = _diag(host_absent)
    host_invalid = SimpleNamespace(owner="R23Probe", outcome_seq=0,
                                   outcome_records=[], last_outcome=None,
                                   last_nurture=None)
    rec_i = capture_outcome(host_invalid, _receipt(input="x"))
    d_invalid = _diag(host_invalid)
    check("gpe02 ledger absent/invalid reasons distinct from budget",
          rec_a is None and rec_i is None
          and d_absent is not None
          and d_absent.get("reason") == "ledger_absent"
          and d_invalid is not None
          and d_invalid.get("reason") == "ledger_invalid",
          f"absent={d_absent} invalid={d_invalid}")

    # (2) The observed action is unaffected: through the real
    # production observer caller, an already-executed action stands,
    # capture returns None without raising, refusal is typed.
    from form.mandell.execution_observer import observe_specialized_execution
    host = _host()
    effects = ["routing effect applied"]  # the action already ran
    out = observe_specialized_execution(host, action="probe",
                                        input_text="Z" * 100_001, ok=True)
    d = _diag(host)
    check("gpe02 observer path: action stands, refusal typed, no raise",
          out is None and effects == ["routing effect applied"]
          and len(host.outcome_records) == 0
          and d is not None and d.get("reason") == "evidence_over_budget",
          f"diag={d}")

    # (3) A refused capture leaves nothing a downstream consumer can
    # present as the captured record for that execution: no record at
    # the next seq, not findable, list unchanged; last_outcome still
    # points at the real prior capture while the diagnostic discloses
    # the latest attempt was unavailable (outcome_id None).
    host = _host()
    first = capture_outcome(host, _receipt(input="first captured"))
    marker = "UNIQUEOVERSIZEDMARKER" + "Q" * 100_001
    rec = capture_outcome(host, _receipt(input=marker))
    d = _diag(host)
    check("gpe02 refused capture: no presentable record, diagnostic discloses",
          rec is None and first is not None
          and get_outcome_by_seq(host, 2) is None
          and find_outcomes(host, "UNIQUEOVERSIZEDMARKER") == []
          and len(list_outcomes(host, limit=10)) == 1
          and host.last_outcome is first
          and d is not None and d.get("status") == "capture_unavailable"
          and d.get("outcome_id") is None,
          f"diag={d}")

    # (4) Valid near-cap evidence stays byte-exact, and a successful
    # capture reports a captured diagnostic naming the record.
    host = _host()
    inp = "V" * 99_999
    m1, m2 = "a" * 50_000, "b" * 49_999
    rec = capture_outcome(host, _receipt(input=inp, messages=[m1, m2]))
    d = _diag(host)
    check("gpe02 valid near-cap evidence byte-exact + captured diagnostic",
          rec is not None and rec.get("input") == inp
          and rec.get("messages") == [m1, m2]
          and d is not None and d.get("status") == "captured"
          and d.get("reason") is None
          and d.get("outcome_id") == rec.get("outcome_id"),
          f"diag={d}")


def main():
    run_all()
    ok_n = sum(1 for _, ok in RESULTS if ok)
    print(f"R23_OUTCOME_EVIDENCE {ok_n}/{len(RESULTS)}")
    return 0 if ok_n == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
