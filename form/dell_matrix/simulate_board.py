#!/usr/bin/env python3
"""C13 Simulate board — Dell 31's real dry-run rehearsal (DD-21).

Ace's ruling (plan §12.16, 2026-11-09): Simulate becomes a REAL
dry-run — hand it a command or a chain and it shows what WOULD
happen, the receipts and the changes, committing none of it.
DD-21's contract: the argument executes against an isolated copy
of program state; the would-be receipts and a scoped state diff
are reported; live state — including history — is bit-identical
afterward, proven by test.

FORM (v1, grounded defaults; Q-C13.1-.7 ride the circuit report):

- GRAMMAR: Mandell already parses `31[Simulate] :: A > B` as a
  chain headed by Simulate (a "::" followed by an atom is the
  DeepFlowBy flow operator, seed.py) — the same head position
  Dell 13 [Loop] uses for its body. chain_exec's execute_range
  therefore hands every atom after a Dell 31 in its range to
  this board as the rehearsed seed; the leaf arm receives only
  a bare/label-only Simulate, which has nothing to rehearse.
- ISOLATION (C13.Executor): the copy is a deepcopy of the live
  program, rebound to a disposable owner — program.owner, and
  the Nursery's file binding (path + seen-signature) — with the
  disposable Nursery file established up front, so any write a
  rehearsed atom performs lands in disposable state files that
  are deleted afterward. The live object is never executed
  against and never reverted (this is a copy, not Try+Revert).
  The baseline is captured WITHOUT write-on-read paths: no
  status()/persona_matrix_status() anywhere on this path; the
  live fingerprint is form.persist.serialize (the program's own
  serializer) plus the live owner's durable file hashes.
- EFFECT INVENTORY (C13.Inventory) / BOUNDED SUBSET (C13.DryRun):
  IN — Core I atoms (00-50) executing against the copy, incl.
  control flow (Loop bodies, flow operators) via the canonical
  front door. REFUSED BEFORE DISPATCH, atom and reason named —
  durable/external classes whose effects a copy cannot honestly
  contain: 27 Checkpoint (durable checkpoint write), 28 Rollback
  (durable restore), 36 Inject (durable load / program swap),
  44 Bridge (external tool call), 47 Embed (provider call).
  Unsupported domains are named, never silently run: Core II
  (51-99) and reserved (100+) atoms refuse as unsupported_domain.
  A nested 31 Simulate refuses (a rehearsal never recurses).
  An unparseable seed rehearses as a refusal receipt.
- RECEIPT: per-atom outcomes are the executor's own atom_results
  from running the canonical front door on the copy; the scoped
  diff covers Plane units (created/removed/modified), Nursery
  proposals (added/status-changed) and the copy's history delta
  — in the spirit of C3.Diff, not a raw state dump. The receipt
  carries no clock readings, so identical simulations on
  unchanged state produce byte-identical receipts. The board
  verifies the live fingerprint before returning and reports it
  on the receipt (live_fingerprint_unchanged).
- ATOM TRUTH: a rehearsed atom that did not execute reports
  ok=False skipped=True with its reason (the executor's own
  records, carried through). Simulate's own atom reports
  ok=False skipped=True when no rehearsal could run (no
  argument, parse refusal, refused class) — never a fake success.

The board never raises: a harness-level failure returns a
receipt with outcome "error" and the error class named.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from itertools import count as _count
from typing import Any, Dict, List, Optional

_STATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "state")
_RUN_COUNTER = _count(1)

# C13.Inventory — durable/external-effect atoms, refused before
# dispatch (dell -> (name, class)). A network/durable effect
# followed by a revert is not a simulation (§14.3 C13 card).
EXTERNAL_EFFECT_ATOMS: Dict[int, tuple] = {
    27: ("Checkpoint", "durable_write"),
    28: ("Rollback", "durable_restore"),
    36: ("Inject", "durable_load"),
    44: ("Bridge", "external_call"),
    47: ("Embed", "provider_call"),
}

SIMULATE_DELL = 31


# ------------------------------------------------------------------
# Snapshots / fingerprints — serializer-based, never status().
# ------------------------------------------------------------------

def _live_fingerprint(program: Any) -> str:
    from form import persist
    blob = json.dumps(persist.serialize(program), sort_keys=True,
                      default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _file_hash(path: Optional[str]) -> Optional[str]:
    if not path or not os.path.isfile(path):
        return None
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _live_files(program: Any) -> Dict[str, Optional[str]]:
    from form.persist import _path
    from form.dell_matrix.nursery import owner_nursery_path
    owner = getattr(program, "owner", "")
    return {
        "program": _file_hash(_path(owner)),
        "nursery": _file_hash(owner_nursery_path(owner)),
    }


def _snapshot(program: Any) -> Dict[str, Any]:
    """Scoped state view for the diff: Plane units, Nursery
    proposals, history. Reads object state directly — no status
    providers, no write-on-read surfaces."""
    units: Dict[str, str] = {}
    try:
        for uid, unit in program.cube.session.plane.units.items():
            material = "|".join([
                str(getattr(unit, "label", "")),
                str(getattr(unit, "words", "")),
                str(getattr(unit, "skin", "")),
            ])
            units[str(uid)] = hashlib.sha256(
                material.encode("utf-8")).hexdigest()
    except Exception:
        pass
    proposals: Dict[str, str] = {}
    try:
        for pid, prop in program.nursery.proposals.items():
            proposals[str(pid)] = str(getattr(prop, "status", ""))
    except Exception:
        pass
    history = list(getattr(program, "history", []) or [])
    return {"units": units, "proposals": proposals, "history": history}


def _scoped_diff(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    bu, au = before["units"], after["units"]
    bp, ap = before["proposals"], after["proposals"]
    return {
        "units_created": sorted(set(au) - set(bu)),
        "units_removed": sorted(set(bu) - set(au)),
        "units_modified": sorted(
            u for u in set(bu) & set(au) if bu[u] != au[u]),
        "proposals_added": sorted(set(ap) - set(bp)),
        "proposals_changed": sorted(
            p for p in set(bp) & set(ap) if bp[p] != ap[p]),
        "history_before": len(before["history"]),
        "history_after": len(after["history"]),
        "history_delta": len(after["history"]) - len(before["history"]),
    }


# ------------------------------------------------------------------
# Disposable copy lifecycle
# ------------------------------------------------------------------

def _disposable_owner() -> str:
    return f"C13Sim{os.getpid()}_{next(_RUN_COUNTER)}"


def _dispose(owner: str) -> Optional[str]:
    """Remove every state artifact of a disposable owner. Returns
    an error string on failure, None on success; never raises —
    a cleanup failure is disclosed on the receipt."""
    import glob
    import shutil
    try:
        for f in glob.glob(os.path.join(_STATE_DIR, f"*{owner}*")):
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        return None
    except OSError as e:
        return f"cleanup failed for {owner}: {type(e).__name__}: {e}"


def _make_copy(program: Any, owner: str) -> Any:
    """Deepcopy the live program and rebind every durable file
    binding the copy carries to the disposable owner, so a
    rehearsed atom's writes land in disposable files only:
    program.owner (program/checkpoint paths derive from it at
    call time) and the Nursery's (path, seen-signature) pair —
    established against the disposable file up front so the
    Nursery's optimistic-concurrency check passes on its own
    file, never the live one."""
    clone = copy.deepcopy(program)
    clone.owner = owner
    try:
        from form.dell_matrix.nursery import owner_nursery_path, _disk_sig
        nursery = getattr(clone, "nursery", None)
        if nursery is not None and hasattr(nursery, "path"):
            nursery.path = owner_nursery_path(owner)
            nursery._seen = _disk_sig(nursery.path)
            nursery.save()
    except Exception:
        # A copy whose Nursery cannot be rebound must not be
        # executed against: its writes could reach the live file.
        raise
    return clone


# ------------------------------------------------------------------
# Receipts
# ------------------------------------------------------------------

def _base_receipt(seed_text: str) -> Dict[str, Any]:
    return {
        "ok": False,
        "kind": "SIMULATION",
        "outcome": "error",
        "seed": seed_text,
        "error": "",
        "reason": "",
        "refused_atoms": [],
        "atom_results": [],
        "would_ok": None,
        "diff": None,
        "lines": [],
        "live_fingerprint_unchanged": None,
    }


def no_argument_receipt() -> Dict[str, Any]:
    """Bare / label-only Simulate: nothing was handed over, so
    nothing can be rehearsed. The atom is unexecuted — reported
    as such, never as a status echo under a no-mutation banner."""
    rcpt = _base_receipt("")
    rcpt["outcome"] = "no_argument"
    rcpt["error"] = "no_argument"
    rcpt["reason"] = (
        "Simulate needs a seed/chain to rehearse "
        "(31[Simulate] :: <seed>); none was given — atom not executed")
    rcpt["lines"] = [
        "Simulate (dry-run): no argument — nothing rehearsed.",
        f"  {rcpt['reason']}",
    ]
    return rcpt


def _refusal(seed_text: str, outcome: str, refused: List[Dict[str, Any]],
             reason: str) -> Dict[str, Any]:
    rcpt = _base_receipt(seed_text)
    rcpt["outcome"] = outcome
    rcpt["error"] = outcome
    rcpt["reason"] = reason
    rcpt["refused_atoms"] = refused
    lines = [f"Simulate (dry-run): REFUSED — {reason}"]
    for item in refused:
        lines.append(
            f"  refused atom {item['dell']:02d}[{item['name']}]: "
            f"{item['class']}")
    rcpt["lines"] = lines
    return rcpt


def _prescan(seed_text: str) -> Optional[Dict[str, Any]]:
    """Refusal gate, run BEFORE any copy is made or any atom is
    dispatched. Returns a refusal receipt, or None to proceed."""
    from form.mandell.seed import parse_seed
    parsed = parse_seed(seed_text)
    if not parsed.ok:
        return _refusal(
            seed_text, "refused_parse", [],
            f"seed could not be parsed: {parsed.error}")
    if not parsed.atoms:
        return no_argument_receipt()
    refused: List[Dict[str, Any]] = []
    outcome = ""
    for atom in parsed.atoms:
        n = int(atom.dell)
        if n == SIMULATE_DELL:
            refused.append({"dell": n, "name": "Simulate",
                            "class": "nested_simulate"})
            outcome = "refused_nested_simulate"
        elif n in EXTERNAL_EFFECT_ATOMS:
            name, klass = EXTERNAL_EFFECT_ATOMS[n]
            refused.append({"dell": n, "name": name, "class": klass})
            outcome = outcome or "refused_external_effect"
        elif n > 50:
            from form.mandell.registry import get_dell
            d = get_dell(n)
            refused.append({
                "dell": n,
                "name": (d or {}).get("name", str(n)),
                "class": "unsupported_domain"})
            outcome = outcome or "refused_unsupported_domain"
    if refused:
        if outcome == "refused_nested_simulate":
            reason = "nested Simulate is not rehearsed (a rehearsal never recurses)"
        elif outcome == "refused_external_effect":
            reason = ("durable/external-effect atoms are refused "
                      "before dispatch — their effects cannot be "
                      "contained by a copy")
        else:
            reason = ("unsupported domain for the C13 v1 bounded "
                      "subset (Core I only); named, not run")
        return _refusal(seed_text, outcome, refused, reason)
    return None


# ------------------------------------------------------------------
# The rehearsal
# ------------------------------------------------------------------

def run_simulation(program: Any, seed_text: str) -> Dict[str, Any]:
    """Rehearse ``seed_text`` against an isolated copy of
    ``program``'s current state. Never raises; never mutates the
    live program (verified on the receipt)."""
    seed_text = (seed_text or "").strip()
    if not seed_text:
        return no_argument_receipt()
    refused = _prescan(seed_text)
    if refused is not None:
        return refused

    rcpt = _base_receipt(seed_text)
    owner = _disposable_owner()
    cleanup_error: Optional[str] = None
    try:
        fp_before = _live_fingerprint(program)
        files_before = _live_files(program)
        clone = _make_copy(program, owner)
        snap_before = _snapshot(clone)
        from form.mandell.executor import execute_seed
        out = execute_seed(clone, seed_text)
        effective = out.get("new_program") or clone \
            if isinstance(out, dict) else clone
        snap_after = _snapshot(effective)
        diff = _scoped_diff(snap_before, snap_after)

        atoms: List[Dict[str, Any]] = []
        if isinstance(out, dict) and out.get("atom_results"):
            atoms = [{
                "dell": int(a.get("dell", -1)),
                "ok": bool(a.get("ok", False)),
                "skipped": bool(a.get("skipped", False)),
                "error": str(a.get("error", "") or ""),
                "reason": str(a.get("reason", "") or ""),
            } for a in out["atom_results"] if isinstance(a, dict)]
        elif isinstance(out, dict):
            # Single-atom execution carries no atom_results list;
            # the atom's own outcome is the execution's outcome.
            from form.mandell.seed import parse_seed
            first = parse_seed(seed_text).atoms
            atoms = [{
                "dell": int(first[0].dell) if first else -1,
                "ok": bool(out.get("ok", False)),
                "skipped": bool(out.get("skipped", False)),
                "error": str(out.get("error", "") or ""),
                "reason": str(out.get("reason", "")
                              or out.get("error", "") or ""),
            }]

        rcpt["ok"] = True
        rcpt["outcome"] = "executed"
        rcpt["atom_results"] = atoms
        rcpt["would_ok"] = bool(out.get("ok", False)) \
            if isinstance(out, dict) else False
        rcpt["diff"] = diff

        fp_after = _live_fingerprint(program)
        files_after = _live_files(program)
        rcpt["live_fingerprint_unchanged"] = (
            fp_before == fp_after and files_before == files_after)

        n_ok = sum(1 for a in atoms if a["ok"])
        n_fail = sum(1 for a in atoms if not a["ok"] and not a["skipped"])
        n_skip = sum(1 for a in atoms if a["skipped"])
        lines = [
            f"Simulate (dry-run): rehearsed {seed_text}",
            f"  atoms: n={len(atoms)} ok={n_ok} failed={n_fail} "
            f"skipped={n_skip}",
        ]
        from form.mandell.registry import get_dell
        for a in atoms:
            d = get_dell(a["dell"])
            name = (d or {}).get("name", str(a["dell"]))
            if a["skipped"]:
                lines.append(
                    f"  atom {a['dell']:02d}[{name}]: SKIPPED — "
                    f"{a['reason'] or a['error']}")
            elif a["ok"]:
                lines.append(f"  atom {a['dell']:02d}[{name}]: ok")
            else:
                lines.append(
                    f"  atom {a['dell']:02d}[{name}]: FAILED — "
                    f"{a['error'] or a['reason']}")
        if diff["units_created"]:
            lines.append(
                f"  would_create: {', '.join(diff['units_created'])}")
        if diff["units_removed"]:
            lines.append(
                f"  would_remove: {', '.join(diff['units_removed'])}")
        if diff["units_modified"]:
            lines.append(
                f"  would_modify: {', '.join(diff['units_modified'])}")
        if diff["proposals_added"]:
            lines.append(
                f"  proposals_added: {', '.join(diff['proposals_added'])}")
        if diff["proposals_changed"]:
            lines.append(
                "  proposals_changed: "
                f"{', '.join(diff['proposals_changed'])}")
        lines.append(
            f"  history_delta: {diff['history_delta']:+d} (copy only)")
        lines.append(
            "  live state: "
            + ("UNCHANGED (fingerprint verified)"
               if rcpt["live_fingerprint_unchanged"]
               else "CHANGED — ISOLATION FAILURE"))
        rcpt["lines"] = lines
    except Exception as e:  # the board never raises
        rcpt["ok"] = False
        rcpt["outcome"] = "error"
        rcpt["error"] = f"{type(e).__name__}: {e}"
        rcpt["reason"] = rcpt["error"]
        rcpt["lines"] = [
            f"Simulate (dry-run): ERROR — {rcpt['error']}"]
    finally:
        cleanup_error = _dispose(owner)
    if cleanup_error:
        rcpt["lines"].append(f"  cleanup: {cleanup_error}")
    return rcpt
