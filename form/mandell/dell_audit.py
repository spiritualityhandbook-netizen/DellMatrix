#!/usr/bin/env python3
"""GP-E07 — whole addressed-Dell execution audit (Part II).

An evidence sweep over the public seed door, address by address,
for every Dell 00-99. It fuses the three existing authorities —
it creates no fourth:

- registry (form.mandell.registry): declared name/manor, and
  execution_standing()'s reconciled dispatch table;
- signatures (form.mandell.signatures): typed roles, declared
  output and failures, where established (17 of 100 today);
- dell_cards (form.mandell.dell_cards): the D1 survey's English
  reachability scan and deep-contract notes.

What this audit adds is the OBSERVED layer the plan requires:
each Dell's bare seed (NN[Name], no operands) is executed through
form.mandell.executor.execute_seed — the canonical public door —
on a fresh isolated owner, and the outcome is classified from
measured evidence:

- canonical state before/after (plane unit ids + sandbox flags,
  nursery pending ids, avatar status, enhance switch, owner
  files) — execution bookkeeping (program history) is measured
  and kept on the record (history_bookkeeping) but never counted
  as a Dell side effect and never rendered into the ledger:
  bookkeeping counts are executor mechanics, not Dell contract
  facts, and pinning them in the ledger made the ledger drift
  with journaling mechanics rather than with Dell contracts
  (repair note, gpe07_audit_test, 2026-11-21);
- the result envelope (named refusal reason, result payload
  keys beyond the standard envelope, chain atom outcome);
- a second invocation on the same owner after the field is
  enriched through the public doors (one created idea, one
  nursery proposal, one avatar drive) — a receipt that changes
  with the field is a state-derived read, not a narration.

Verdict rules (bare-probe scope; the ledger states this scope
on its face):

- DEFECT: the executor raised; a refusal with no named reason;
  a refusal that mutated canonical state; a dispatch the
  standing table names that does not resolve to a real handler.
- UNREACHABLE: the standing table gives a core address no
  executable path (RESERVED_NOT_ACTIVE / UNREGISTERED).
- CONTRACT_PROVEN: at least one evidence leg — named refusal
  with zero canonical change; canonical mutation; result
  payload; executed (not skipped) chain atom; a value minted
  by the call (timestamp / generation id in the receipt); or a
  field-sensitive receipt.
- MESSAGE_ONLY: ok=True with no leg — the bare invocation
  produced messages only: no canonical effect, no result
  payload, and a receipt independent of the field. This is the
  row #36 (SM-23) audit output: it names the bare case, and
  does not claim the Dell never executes with operands — the
  tests column cites the deeper per-Dell suites where they
  exist.

Registry ACTIVE remains reachability only; a verdict here is
about the observed bare contract, never a completion claim for
operand-bearing operation.

Isolation: one unique owner per address (GPE07Audit<n>), files
cleaned before and after via the D1 cleanup; the audit leaves
form/state byte-identical (proven by gpe07_audit_test).
"""
from __future__ import annotations

import glob
import importlib
import os
import re
from typing import Any, Dict, List, Optional

from .registry import DELLS, execution_standing, get_dell
from .signatures import get_signature

VERDICTS = ("CONTRACT_PROVEN", "DEFECT", "MESSAGE_ONLY", "UNREACHABLE")
DOOR = "form.mandell.executor.execute_seed (public seed door)"

_ENVELOPE = {"ok", "seed", "english", "primary", "messages",
             "new_program", "error", "atom_results", "skipped",
             "simulated", "partial", "partial_created"}

# Open design decisions the audit surfaces instead of silently
# repairing (plan GP-E07 build step 3: a defect becomes a bounded
# fix OR is escalated as a named question). Keyed by Dell.
OPEN_DECISIONS: Dict[int, str] = {
    1: ("Bare Initiate reports 'Initiated. owner=<owner>' and "
        "changes nothing observable: the execution session it "
        "names is opened by Program construction, before any seed "
        "runs. Recorded as measured; no ruling requested."),
    24: ("Bare Unlock writes sandboxed=False to every live unit; "
         "on a fresh (unlocked) field that write is value-identical, "
         "so no canonical change is observable at bare scope. Its "
         "mirror Lock (23) is observable precisely because the "
         "fresh field starts unlocked. Recorded as measured."),
    41: ("In chain position Sanitize screens the atoms that follow "
         "it (the executor's PP3 path); bare on an empty field it "
         "has nothing to screen and reports the empty result. "
         "Recorded as measured."),
    0: ("Nova's leaf arm is deliberately inert at the seed door "
        "('cheat/edge only — floor stays locked'); the Director "
        "baseline contract promises origin read/initialize. "
        "Director: settle whether inert-by-design is the contract."),
    4: ("The leaf arm executes avatar/form transforms (turn, sit, "
        "toggle form); the Director baseline contract promises a "
        "value transform with before/after receipt. Semantics "
        "divergence — Director ruling owed."),
    26: ("Bare Temp defaults to 'warm' and switches enhance ON; "
         "the receipt discloses it ('enhance ON'). The baseline "
         "warns against a hidden global enhance — disclosed here, "
         "recorded for the Director's awareness, not repaired."),
    50: ("Bare Manifest answers ok=True 'Manifest needs :: label.' "
         "with zero mutation. That behavior is PINNED as a D1 "
         "contract by d1_registry_leaf4_test; its tension with "
         "the unexecuted-atom honesty law (an atom that did not "
         "execute must not report ok=True) is named for a Director "
         "ruling — not unilaterally repaired here."),
}

_TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
_GEN_RE = re.compile(r"\bg[0-9a-f]{16,}\b")


def _resolve_handler(dispatch: str) -> (str, bool):
    """Resolve a standing-table dispatch string to a real
    module::callable. Returns (handler_name, resolved)."""
    targets = []
    if "core_i_ops.py::apply_core_i" in dispatch:
        targets.append(("form.mandell.core_i_ops", "apply_core_i"))
    elif "live_identity.py::" in dispatch:
        fn = dispatch.rsplit("::", 1)[1].strip()
        targets.append(("form.mandell.live_identity", fn))
    elif "executor_leaf.py::execute_seed" in dispatch:
        targets.append(("form.mandell.executor_leaf", "execute_seed"))
    elif "chain_exec.py::execute_chain" in dispatch:
        targets.append(("form.mandell.chain_exec", "execute_chain"))
        if "query_ops.apply_query" in dispatch:
            targets.append(("form.mandell.query_ops", "apply_query"))
        elif "inline (scope)" in dispatch:
            targets.append(("form.mandell.core_ii_exec", None))
        elif "_run_control" in dispatch:
            targets.append(("form.mandell.chain_exec", "_run_control"))
        elif "spectrum_ops.apply_spectrum" in dispatch:
            targets.append(("form.mandell.spectrum_ops", "apply_spectrum"))
        elif "core_ii_exec.py::execute_core_ii" in dispatch:
            targets.append(("form.mandell.core_ii_exec", "execute_core_ii"))
    names = []
    resolved = bool(targets)
    for mod_name, fn in targets:
        names.append(f"{mod_name}.{fn}" if fn else mod_name)
        try:
            mod = importlib.import_module(mod_name)
            if fn is not None and not callable(getattr(mod, fn, None)):
                resolved = False
        except Exception:
            resolved = False
    return " -> ".join(names), resolved


def _canonical(p: Any, state_dir: str) -> Dict[str, Any]:
    units = {}
    try:
        units = p.cube.session.plane.units or {}
    except Exception:
        units = {}
    unit_state = sorted(
        (str(k), str(getattr(v, "sandboxed", "")),
         str(getattr(getattr(v, "skin", ""), "name", getattr(v, "skin", ""))))
        for k, v in units.items())
    try:
        pending = sorted(str(x.id) for x in p.nursery.pending())
    except Exception:
        pending = []
    try:
        av = p.avatar_status()
        avatar = (av.get("describe"), av.get("look"))
    except Exception:
        avatar = None
    try:
        enhance = bool(p.enhance.on)
    except Exception:
        enhance = None
    files = sorted(os.path.basename(f) for f in
                   glob.glob(os.path.join(state_dir, f"*{p.owner}*")))
    return {"units": unit_state, "nursery_pending": pending,
            "avatar": avatar, "enhance": enhance, "files": files}


def _describe_change(before: Dict[str, Any], after: Dict[str, Any]) -> List[str]:
    out = []
    b_ids = {u[0] for u in before["units"]}
    a_ids = {u[0] for u in after["units"]}
    if a_ids - b_ids:
        out.append(f"ideas +{len(a_ids - b_ids)}")
    if b_ids - a_ids:
        out.append(f"ideas -{len(b_ids - a_ids)}")
    b_flags = {u[0]: u[1] for u in before["units"]}
    a_flags = {u[0]: u[1] for u in after["units"]}
    if any(b_flags.get(k) != a_flags.get(k) for k in b_ids & a_ids):
        out.append("unit sandbox flags changed")
    if len(after["nursery_pending"]) != len(before["nursery_pending"]):
        d = len(after["nursery_pending"]) - len(before["nursery_pending"])
        out.append(f"nursery_pending {d:+d}")
    if before["avatar"] != after["avatar"]:
        out.append("avatar state changed")
    if before["enhance"] != after["enhance"]:
        out.append(f"enhance {before['enhance']}->{after['enhance']}")
    b_f, a_f = set(before["files"]), set(after["files"])
    if a_f != b_f:
        # Qualitative, not counts: checkpoint generation rotation
        # makes exact member counts vary between runs, and the
        # ledger must render deterministically.
        out.append("owner files changed")
    return out


def _receipt(result: Optional[Dict[str, Any]]) -> str:
    if not result:
        return ""
    lines = [str(m) for m in (result.get("messages") or [])
             if not (str(m).startswith("Mandell:")
                     or str(m).startswith("English:"))]
    text = "\n".join(lines)
    text = _TS_RE.sub("<ts>", text)
    text = _GEN_RE.sub("<gen>", text)
    return text


def _normalize_receipt(text: str) -> str:
    return _GEN_RE.sub("<gen>", _TS_RE.sub("<ts>", text))


def _tests_for(n: int, deep_notes: Dict[int, str]) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    found = sorted(os.path.basename(f)[:-3] for f in
                   glob.glob(os.path.join(here, f"d1_dell{n}_*_test.py")))
    parts = list(found)
    if n in deep_notes:
        parts.append("D1 deep contract (dell_cards DEEP_NOTES)")
    parts.append("d1_proof_cards_test")
    parts.append("r2_registry_reconciliation_test")
    return ", ".join(parts)


def audit_dell(n: int, owner: str, state_dir: str,
               named: set, deep_notes: Dict[int, str]) -> Dict[str, Any]:
    from form.open import Program
    from .executor import execute_seed

    entry = get_dell(n)
    sig = get_signature(n)
    standing = execution_standing(n)
    handler, handler_resolved = _resolve_handler(standing["dispatch"])

    if sig is not None:
        required = [r.name for r in (sig.roles or []) if r.required]
        signature_txt = "present"
        required_txt = ", ".join(required) if required else "none required"
        expected_txt = (f"declared output: {sig.output} | declared "
                        f"failures: {sig.failures}")
    else:
        required_txt = "none declared (no typed signature)"
        signature_txt = "absent"
        expected_txt = "no typed signature established"

    record: Dict[str, Any] = {
        "dell": n,
        "name": entry["name"],
        "manor": entry["manor"],
        "namespace": entry["namespace"],
        "dispatch": standing["dispatch"],
        "handler": handler,
        "handler_resolved": handler_resolved,
        "standing": standing["standing"],
        "signature": signature_txt,
        "required_args": required_txt,
        "expected": expected_txt,
        "door": DOOR,
        "english_named": n in named,
        "tests": _tests_for(n, deep_notes),
        "open_decision": OPEN_DECISIONS.get(n, ""),
        "legs": [],
        "canonical_change": [],
        "side_effects": "none observed",
        "reason": "",
        "class": "",
        "bare_outcome": "",
        "verdict": "",
        "basis": "",
    }

    if standing["standing"] in ("RESERVED_NOT_ACTIVE", "UNREGISTERED"):
        record["bare_outcome"] = "not probed (no executable path)"
        record["class"] = "refusal"
        record["verdict"] = "UNREACHABLE"
        record["basis"] = (f"standing table: {standing['standing']} "
                           f"for a core address")
        return record

    seed = f"{n:02d}[{entry['name']}]"
    p = Program(owner)
    before = _canonical(p, state_dir)
    try:
        hist_before = len(p.history)
    except Exception:
        hist_before = None
    crash = None
    result = None
    try:
        result = execute_seed(p, seed)
    except Exception as e:  # an escaping exception is audit evidence
        crash = f"{type(e).__name__}: {e}"
    after = _canonical(p, state_dir)
    try:
        hist_after = len(p.history)
    except Exception:
        hist_after = None

    change = _describe_change(before, after)
    record["canonical_change"] = change
    bookkeeping = None
    if hist_before is not None and hist_after is not None:
        bookkeeping = hist_after - hist_before
    # The history delta is executor bookkeeping (entries the
    # executor journals per execution). It is measured and kept
    # on the record as evidence, but it is NOT a Dell side effect
    # (the rule stated in this module's docstring) and it is not
    # rendered into the ledger: bookkeeping counts are executor
    # mechanics, not a Dell contract fact, and a ledger that
    # byte-pins them drifts whenever journaling mechanics vary
    # without any Dell's contract changing (repair note,
    # gpe07_audit_test, 2026-11-21).
    record["history_bookkeeping"] = bookkeeping
    if change:
        record["side_effects"] = "; ".join(change)

    if crash is not None:
        record["bare_outcome"] = "crashed"
        record["reason"] = crash
        record["class"] = "defect"
        record["verdict"] = "DEFECT"
        record["basis"] = f"executor raised: {crash}"
        return record

    ok = bool(result.get("ok"))
    reason = str(result.get("error") or "")
    atom_executed = False
    atom_reason = ""
    for a in (result.get("atom_results") or []):
        if isinstance(a, dict):
            atom_reason = str(a.get("reason") or a.get("error") or "")
            if a.get("ok") and not a.get("skipped"):
                atom_executed = True
            break
    if not reason:
        reason = atom_reason
    record["reason"] = reason

    if not ok:
        record["bare_outcome"] = "refused"
        record["class"] = "refusal"
        if not reason:
            record["verdict"] = "DEFECT"
            record["basis"] = "refusal with no named reason"
        elif change:
            record["verdict"] = "DEFECT"
            record["basis"] = ("refusal mutated canonical state: "
                               + "; ".join(change))
        else:
            record["legs"] = ["named_refusal_no_mutation"]
            record["verdict"] = "CONTRACT_PROVEN"
            record["basis"] = f"bare refusal leg: named reason '{reason}'"
        return record

    record["bare_outcome"] = "executed"
    legs: List[str] = []
    if change:
        legs.append("canonical_mutation")
    payload = [k for k, v in result.items()
               if k not in _ENVELOPE and v not in (None, "", [], {})]
    if payload:
        legs.append("result_payload:" + ",".join(sorted(payload)))
    if atom_executed:
        legs.append("chain_atom_executed")
    receipt_a = _receipt(result)
    raw_receipt = "\n".join(str(m) for m in (result.get("messages") or []))
    if _TS_RE.search(raw_receipt) or _GEN_RE.search(raw_receipt):
        legs.append("minted_value_in_receipt")
    if not legs:
        # Field-sensitivity probe: enrich the field through the
        # public doors, then invoke the same bare seed again on
        # the same owner. A receipt that changes with the field
        # is a state-derived read.
        for prep in ("08[Create]", "37[Nurture] :: gpe07 audit proposal",
                     "19[Drive]"):
            try:
                execute_seed(p, prep)
            except Exception:
                pass
        try:
            result2 = execute_seed(p, seed)
            receipt_b = _receipt(result2)
            if result2.get("ok") and receipt_b != receipt_a:
                legs.append("field_sensitive_receipt")
        except Exception:
            pass
    record["legs"] = legs
    record["class"] = "mutation" if "canonical_mutation" in legs else "read"
    if legs:
        record["verdict"] = "CONTRACT_PROVEN"
        record["basis"] = "bare execution leg: " + ", ".join(legs)
    else:
        record["verdict"] = "MESSAGE_ONLY"
        record["basis"] = ("bare invocation produced messages only: no "
                           "canonical effect, no result payload, receipt "
                           "independent of the field")
    if not handler_resolved:
        record["verdict"] = "DEFECT"
        record["basis"] = ("standing table names a handler that does "
                           f"not resolve: {standing['dispatch']}")
    return record


def _cleanup_thorough(owner: str, state_dir: str) -> None:
    """D1 cleanup PLUS the checkpoint generation-member files
    (program_<owner>.<fp>.g_<gen>.json and its nursery sibling)
    that the D1 glob set does not cover — Dell 27's probe writes
    them, and the audit must leave no residue (isolation law)."""
    from .dell_cards import _cleanup
    _cleanup(owner, state_dir)
    for f in glob.glob(os.path.join(state_dir, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                import shutil
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass


def run_audit(owner_prefix: str = "GPE07Audit") -> List[Dict[str, Any]]:
    from .dell_cards import DEEP_NOTES, english_named_dells
    from form.persist import _STATE_DIR

    named = english_named_dells()
    records = []
    for n in sorted(DELLS):
        owner = f"{owner_prefix}{n}"
        _cleanup_thorough(owner, _STATE_DIR)
        try:
            records.append(audit_dell(n, owner, _STATE_DIR,
                                      named, DEEP_NOTES))
        finally:
            _cleanup_thorough(owner, _STATE_DIR)
    return records


def render_ledger_md(records: List[Dict[str, Any]]) -> str:
    counts: Dict[str, int] = {}
    for r in records:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    n_i = sum(1 for r in records if r["namespace"] == "CORE_I")
    n_ii = sum(1 for r in records if r["namespace"] == "CORE_II")
    sig_n = sum(1 for r in records if r["signature"] == "present")
    eng_n = sum(1 for r in records if r["english_named"])
    lines = [
        "# PART II — GP-E07 AUDIT LEDGER (2026-11-21)",
        "",
        "Whole addressed-Dell execution audit, run as one body at the",
        "Part II code-stage head that carries form/mandell/dell_audit.py.",
        "Generated by `form/mandell/dell_audit.py::render_ledger_md` from",
        "a live sweep; gpe07_audit_test fails if this file drifts from a",
        "fresh sweep. Do not hand-edit.",
        "",
        "## Scope and rules",
        "",
        "- Door: the canonical public seed door",
        "  (form.mandell.executor.execute_seed). Probe per address: the",
        "  bare seed NN[Name] on a fresh isolated owner, plus a second",
        "  invocation after the field is enriched through the public",
        "  doors (field-sensitivity leg). Operand-bearing operation is",
        "  evidenced by the per-Dell suites in the Tests column, not",
        "  re-run here.",
        "- Verdicts: CONTRACT_PROVEN (at least one measured evidence",
        "  leg), DEFECT (crash / unnamed refusal / refusal that",
        "  mutated / unresolvable handler), MESSAGE_ONLY (bare door",
        "  produced messages only — the row #36 / SM-23 audit output),",
        "  UNREACHABLE (standing table gives no executable path).",
        "- Registry ACTIVE = reachability only, never completion;",
        "  no verdict in this ledger is a completion claim.",
        "- The Side effects column lists canonical changes only.",
        "  Executor history bookkeeping (entries journaled per",
        "  execution) is excluded by design: it is not a Dell side",
        "  effect, and its count is executor mechanics — a fact",
        "  that may vary without any Dell contract changing — so",
        "  it is not a ledger fact and is never byte-pinned here.",
        "- Reconciliation: 51 Core I (00-50) + 49 Core II (51-99) =",
        "  100 addresses. Address 151 (Harmonidell) is a reserved",
        "  alias, standing RESERVED_NOT_ACTIVE — not a core Dell,",
        "  never counted, never deleted.",
        "",
        "## Counts",
        "",
        f"- Addresses audited: {len(records)} (Core I {n_i}, Core II {n_ii})",
        f"- CONTRACT_PROVEN: {counts.get('CONTRACT_PROVEN', 0)}",
        f"- MESSAGE_ONLY: {counts.get('MESSAGE_ONLY', 0)}",
        f"- DEFECT: {counts.get('DEFECT', 0)}",
        f"- UNREACHABLE: {counts.get('UNREACHABLE', 0)}",
        f"- Typed signatures established: {sig_n} of 100",
        f"- English-named (translate() can name the Dell): {eng_n} of 100",
        "",
        "## Per-address records",
        "",
        "| # | Name | Manor | Handler | Sig | Required args | Class | Bare outcome | Reason / legs | Side effects (bare) | English | Tests | Verdict |",
        "|---:|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in records:
        outcome = r["bare_outcome"]
        if outcome == "refused":
            outcome = f"refused: {r['reason']}"
        elif outcome == "executed":
            outcome = "executed: " + (", ".join(r["legs"]) or "no leg")
        elif outcome == "crashed":
            outcome = f"crashed: {r['reason']}"
        lines.append(
            f"| {r['dell']:02d} | {r['name']} | {r['manor']} | "
            f"{r['handler']} | {r['signature']} | {r['required_args']} | "
            f"{r['class']} | {outcome} | {r['basis']} | "
            f"{r['side_effects']} | "
            f"{'yes' if r['english_named'] else 'no'} | {r['tests']} | "
            f"{r['verdict']} |")
    lines += ["", "## Declared contracts (typed signatures)", ""]
    for r in records:
        if r["signature"] == "present":
            lines.append(f"- **{r['dell']:02d} {r['name']}** — {r['expected']}")
    lines += ["", "## Open design decisions (escalated, not repaired)", ""]
    any_decision = False
    for r in records:
        if r["open_decision"]:
            any_decision = True
            lines.append(f"- **{r['dell']:02d} {r['name']}** — "
                         f"{r['open_decision']}")
    if not any_decision:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    recs = run_audit()
    from collections import Counter
    print(Counter(r["verdict"] for r in recs))
    for r in recs:
        if r["verdict"] != "CONTRACT_PROVEN":
            print(r["dell"], r["name"], r["verdict"], "|", r["basis"],
                  "|", r["side_effects"])
