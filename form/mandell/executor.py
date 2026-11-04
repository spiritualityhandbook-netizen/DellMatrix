#!/usr/bin/env python3
"""Mandell seed executor — front door.

Multi-atom seeds and Core II (51-99) run through chain_exec so every atom executes.
Single-atom CORE_I (00-50) uses the original leaf implementation in executor_leaf.py.
Closable Core I recovery/measure/external contracts run through core_i_ops.
Dell 21/22 live-unit transforms use live_identity lineage.
"""
from __future__ import annotations

from typing import Any, Dict

from .seed import parse_seed


def _note_unknown(program: Any, subject: str, question: str,
                  source: str) -> None:
    """PP3: record an encountered unknown on the program's register.
    Best-effort by design — capture must never break execution
    (the note_seed precedent below). Programs without the register
    API are simply skipped."""
    try:
        note = getattr(program, "note_unknown_encounter", None)
        if callable(note):
            note(subject, question, source)
    except Exception:
        pass


def execute_seed(program: Any, seed_text: str, _leaf: bool = False) -> Dict[str, Any]:
    s = parse_seed(seed_text)
    if not s.ok:
        _note_unknown(program, f"seed: {seed_text[:160]}",
                      f"Seed could not be parsed: {s.error}",
                      "executor:parse")
        return {"ok": False, "error": s.error, "messages": [f"Seed error: {s.error}"]}

    # CORE-I-UNSUPPORTED-ARG-GATE (Director MODE C repair, Core I
    # contract ruling on PR #256, 2026-11-03): typed args on an
    # UNREGISTERED Core I Dell refuse BEFORE any dispatch. The
    # judgment is per EXECUTING atom: this funnel only ever
    # dispatches a single atom itself (intercept, live_identity,
    # or leaf), so the gate fires only for a single-atom seed and
    # inspects THAT atom's args. Multi-atom seeds are never judged
    # here — chain_exec re-enters this entry point per Core I atom
    # (_leaf=True) with that atom's own args, so a mixed chain is
    # never rejected for another atom's sake (the Director's
    # per-atom correction; the reverse AF-1 parity defect).
    # Diagnostics name sorted role NAMES only; raw argument
    # values are never echoed (Q-C2 boundary, as certified for
    # Core II in PR #253).
    if len(s.atoms) == 1:
        _atom0 = s.atoms[0]
        _n0 = int(_atom0.dell)
        _args0 = getattr(_atom0, "args", None) or {}
        if _args0 and 0 <= _n0 <= 50:
            from .signatures import has_signature
            if not has_signature(_n0):
                from .redaction import redacted_seed
                _echo = redacted_seed(s)
                _roles = ", ".join(sorted(_args0))
                _term0 = getattr(_atom0, "term", "") or ""
                return {
                    "ok": False,
                    "error": f"UNSUPPORTED_ARGS: {_roles}",
                    "messages": [
                        f"Mandell: {_echo.as_mandel()}",
                        f"English: {_echo.as_english()}",
                        f"TOAM: Dell {_n0:02d}[{_term0}] has no "
                        f"registered typed signature; typed "
                        f"arguments refused before execution "
                        f"(roles: {_roles})"],
                }

    from .core_i_ops import HANDLED, apply_core_i
    primary = s.primary_dell()
    if primary in HANDLED and len(s.atoms) == 1:
        handled = apply_core_i(program, seed_text, s)
        if handled is not None:
            return handled

    # PRISM C2 (GDP-001 P0 audit): guard multi-atom seeds. Without the
    # len==1 guard, a 21/22-primary multi-atom seed was consumed here and
    # later atoms were silently dropped (no receipt, no partial flag).
    # chain_exec routes each atom through this same intercept, so the
    # authority is unchanged — only the dispatch is corrected.
    if primary in (21, 22) and len(s.atoms) == 1:
        from .live_identity import merge_live, split_live
        rec = merge_live(program, s.label or "") if primary == 21 else split_live(program, s.label or "")
        messages = [f"Mandell: {s.as_mandel()}", f"English: {s.as_english()}"]
        if not rec.get("ok"):
            messages.append(f"{'Merge' if primary == 21 else 'Split'} failed: {rec.get('error')}")
            # GDP-001 0.3.3: merge_live/split_live can place child units and
            # STILL return ok=False (parent/source mutated mid-operation).
            # Never silently swallow that partial mutation — report it.
            _created = rec.get("created") or ([rec["id"]] if rec.get("id") else [])
            _created = [c for c in _created if c]
            if _created:
                messages.append(
                    f"PARTIAL: unit(s) {', '.join(_created)} were placed before "
                    f"the abort; the merge/split did not complete.")
            return {
                "ok": False,
                "error": rec.get("error") or "missing_source",
                "seed": s.as_mandel(),
                "english": s.as_english(),
                "primary": primary,
                "messages": messages,
                "new_program": None,
                "partial": bool(_created),
                "partial_created": _created,
            }
        if primary == 21:
            messages.append(f"Merged → {rec['id']} parents={rec['parents']}")
        else:
            messages.append(f"Split → {' + '.join(rec['created'])}")
        if hasattr(program, "note_seed"):
            # GDP-001 0.3.3: history bookkeeping must not mask a completed
            # mutation. If note_seed fails, report honestly but keep ok=True.
            try:
                program.note_seed(primary, "Merge" if primary == 21 else "Split", rec.get("id") or rec.get("source") or "")
            except Exception as _nse:
                messages.append(f"note_seed failed (mutation completed): {_nse}")
        return {
            "ok": True,
            "seed": s.as_mandel(),
            "english": s.as_english(),
            "primary": primary,
            "messages": messages,
            "new_program": None,
        }

    if not _leaf:
        primary = s.primary_dell()
        multi = len(s.atoms) > 1
        core_ii = primary is not None and 51 <= int(primary) <= 99
        if multi or core_ii:
            from .chain_exec import execute_chain
            out = execute_chain(program, s, seed_text)
            # PP3: an atom that did not execute is an encountered
            # unknown — record it (deduped) on the active program.
            target = out.get("new_program") or program
            # Step 3b: a skipped atom in a Sanitize chain must not
            # carry the raw seed text into the unknown register.
            _subj = f"seed: {seed_text[:160]}"
            if any(int(getattr(a, "dell", -1)) == 41 for a in s.atoms):
                from .redaction import sanitize_text as _stx
                _subj = _stx(_subj)
            for r in out.get("atom_results") or []:
                if isinstance(r, dict) and r.get("skipped"):
                    _note_unknown(
                        target, _subj,
                        f"Dell {r.get('dell')} did not execute: "
                        f"{r.get('reason') or 'no reason recorded'}",
                        "executor:skip")
            return out

    from .executor_leaf import execute_seed as execute_leaf
    return execute_leaf(program, seed_text)
