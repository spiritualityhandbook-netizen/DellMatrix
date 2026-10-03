#!/usr/bin/env python3
"""Multi-atom Mandell execution with control frames and flow contracts.

CORE_I atoms run the existing executor leaf path.
CORE_II atoms run core_ii_exec.
Control bodies 60-66 run until 61[Join].
Flows are parsed in seed.py and executed here — not the same thing.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .control_runtime import (
    CONTROL_HEADS,
    FLOW_CONTRACT,
    MAX_DEPTH,
    bound_of,
    eval_condition,
    find_else,
    find_join,
)
from .core_ii_exec import attach, execute_core_ii
from .registry import get_dell, namespace_of


def _flow_at(seed: Any, index: int) -> str:
    flows = list(getattr(seed, "flows", []) or [])
    if 0 <= index < len(flows):
        return flows[index]
    return ">"


def _run_atom(program: Any, atom: Any, seed: Any, messages: List[str]) -> Tuple[Any, Dict[str, Any]]:
    from form.mandell.executor import execute_seed

    n = int(atom.dell)
    shown = getattr(atom, "resolved_term", None) or atom.term
    raw_term = getattr(atom, "term", "") or shown
    ns = namespace_of(n)
    d = get_dell(n) or {}
    canon = str(d.get("name", "")).lower()
    payload = seed.label or ""
    if raw_term and raw_term.lower() != canon:
        payload = raw_term
    # TOAM-I C3: Wire typed args into production execution.
    # If atom has typed args, validate and lower to lab format.
    atom_args = getattr(atom, "args", None) or {}
    if atom_args and 51 <= n <= 99:
        from form.mandell.signatures import get_signature, lower_args_to_lab, has_signature
        if has_signature(n):
            sig = get_signature(n)
            errors = sig.validate(atom_args)
            if errors:
                # Validation failure: return canonical failure, ZERO mutation
                err_msg = f"TOAM validation failed for {n:02d}[{shown}]: {'; '.join(errors)}"
                messages.append(err_msg)
                return program, {"ok": False, "error": errors[0], "messages": messages}
            # C2: Resolve existing reference kinds in arg values.
            # Reuses predicate.py reference authority (last_result, store:, selected).
            # This enables composition: OP_A publishes to last_result, OP_B consumes it.
            resolved_args = {}
            st = getattr(program, "core_ii", None)
            for k, v in atom_args.items():
                resolved_v = v
                if st is not None and isinstance(v, str):
                    low = v.lower().strip()
                    if low in ("last_result", "result"):
                        # Resolve from existing st.last_result authority
                        lr = getattr(st, "last_result", None) or {}
                        if not lr.get("matched"):
                            err_msg = f"REFERENCE_FAILED for {n:02d}[{shown}]: last_result not matched (error: {lr.get('error', 'unknown')})"
                            messages.append(err_msg)
                            return program, {"ok": False, "error": "REFERENCE_FAILED", "messages": messages}
                        resolved_v = str(lr.get("value", ""))
                        messages.append(f"TOAM: resolved '{v}' -> '{resolved_v}' from last_result")
                    elif low.startswith("store:"):
                        # Resolve from existing store authority
                        key = v.split(":", 1)[1]
                        store = getattr(st, "store", {}) or {}
                        if key not in store:
                            err_msg = f"REFERENCE_FAILED for {n:02d}[{shown}]: store key '{key}' not found"
                            messages.append(err_msg)
                            return program, {"ok": False, "error": "REFERENCE_FAILED", "messages": messages}
                        resolved_v = key  # Reference the key itself, not the value
                        messages.append(f"TOAM: resolved '{v}' -> store key '{key}'")
                resolved_args[k] = resolved_v
            # Conflict law: if both typed args and legacy lab present with different values,
            # fail safely rather than silently choosing.
            typed_lab = lower_args_to_lab(n, resolved_args)
            if payload and payload != typed_lab:
                err_msg = f"ARGUMENT_CONFLICT for {n:02d}[{shown}]: typed args lower to '{typed_lab}' but legacy lab is '{payload}'"
                messages.append(err_msg)
                return program, {"ok": False, "error": "ARGUMENT_CONFLICT", "messages": messages}
            payload = typed_lab
            messages.append(f"TOAM: typed args lowered to lab='{payload}'")
    term = shown
    messages.append(f"-- {n:02d}[{term}] ns={ns}")
    if 51 <= n <= 99:
        out = execute_core_ii(program, n, term, payload, messages)
        return program, out
    if 0 <= n <= 50:
        leaf = f"{n:02d}[{atom.term}]"
        if seed.label:
            leaf += f" :: {seed.label}"
        out = execute_seed(program, leaf, _leaf=True)
        for msg in out.get("messages") or []:
            if msg.startswith("Mandell:") or msg.startswith("English:"):
                continue
            messages.append(msg)
        if out.get("new_program") is not None:
            program = out["new_program"]
        return program, out
    d = get_dell(n)
    name = (d or {}).get("name", str(n))
    messages.append(f"Dell {n}[{name}] reserved/not-active")
    return program, {"ok": True, "error": "", "skipped": True}


def _apply_flow(st: Any, flow: str, prev_ok: bool, prev_atom: Any, next_atom: Any, messages: List[str]) -> str:
    name = FLOW_CONTRACT.get(flow, "FlowTo")
    st.flow_taken.append(f"{flow}:{name}")
    if flow == ">>":
        if not prev_ok:
            st.flow_blocked.append(name)
            messages.append("FlowThru blocked after fail")
            return "skip"
        return "run"
    if flow == ">>>":
        messages.append("FlowOver boundary — skip until Join")
        st.flow_blocked.append(name)
        return "over"
    if flow == ":":
        term = getattr(next_atom, "term", "")
        st.context = term
        messages.append(f"FlowBy bind context={term}")
        return "run"
    if flow == "::":
        term = getattr(next_atom, "term", "")
        st.refs["deep"] = term
        messages.append(f"DeepFlowBy {term}")
        return "run"
    if flow == ":>":
        term = getattr(next_atom, "term", "")
        st.route = term or st.route
        messages.append(f"FlowTowards {st.route}")
        return "run"
    if flow == "<:":
        term = getattr(prev_atom, "term", "")
        st.refs["from"] = term
        messages.append(f"FlowFrom {term}")
        return "run"
    if flow == "<:>":
        st.refs["from"] = getattr(prev_atom, "term", "")
        st.route = getattr(next_atom, "term", "") or st.route
        messages.append(f"DynamicFlow {st.refs.get('from')}->{st.route}")
        return "run"
    if flow == "<<[Delta]":
        st.snapshots.append(st.snap())
        messages.append(f"DeltaFlow checkpoint snapshots={len(st.snapshots)}")
        return "run"
    return "run"


def _payload_cond(atom: Any, seed: Any, n: int) -> str:
    raw_term = getattr(atom, "term", "") or ""
    canon = str((get_dell(n) or {}).get("name", "")).lower()
    if raw_term and raw_term.lower() != canon:
        return raw_term
    return seed.label or ""


def execute_range(program, seed, atoms, start, end, depth, messages, ran, skipped, state):
    results = []
    st = attach(program)
    i = start
    last_ok = True
    while i < end:
        atom = atoms[i]
        n = int(atom.dell)
        if i > start:
            action = _apply_flow(st, _flow_at(seed, i - 1), last_ok, atoms[i - 1], atom, messages)
            if action == "skip":
                skipped.append(n)
                results.append({"dell": n, "ok": False, "error": "flow_thru_block"})
                last_ok = False
                i += 1
                continue
            if action == "over":
                while i < end and int(atoms[i].dell) != 61:
                    skipped.append(int(atoms[i].dell))
                    messages.append(f"skipped by FlowOver {int(atoms[i].dell)}")
                    i += 1
                continue
        if n in CONTROL_HEADS:
            if depth >= MAX_DEPTH:
                messages.append(f"control depth bound {MAX_DEPTH}")
                state["ok"] = False
                state["error"] = "depth_bound"
                results.append({"dell": n, "ok": False, "error": "depth_bound"})
                return program, results
            program, chunk = _run_control(program, seed, atoms, i, end, depth, messages, ran, skipped, state)
            results.extend(chunk)
            last_ok = all(r.get("ok", True) for r in chunk) if chunk else True
            join_at = find_join(atoms, i + 1, end)
            i = join_at + 1 if join_at < end and int(getattr(atoms[join_at], "dell", -1)) == 61 else join_at
            st = attach(program)
            continue
        program, out = _run_atom(program, atom, seed, messages)
        if out.get("skipped"):
            skipped.append(n)
        else:
            ran.append(n)
        if out.get("new_program") is not None:
            program = out["new_program"]
            state["new_program"] = program
        last_ok = bool(out.get("ok", True))
        results.append({"dell": n, "ok": last_ok, "error": out.get("error") or ""})
        if not last_ok:
            state["ok"] = False
            state["error"] = out.get("error") or state.get("error") or ""
        i += 1
    return program, results


def _run_control(program, seed, atoms, head, limit, depth, messages, ran, skipped, state):
    atom = atoms[head]
    n = int(atom.dell)
    program, head_out = _run_atom(program, atom, seed, messages)
    ran.append(n)
    st = attach(program)
    join_at = find_join(atoms, head + 1, limit)
    kind = {60: "branch", 62: "parallel", 63: "sequence", 64: "until", 65: "while", 66: "foreach"}[n]
    cond = _payload_cond(atom, seed, n)
    results = []
    iterations = 0
    status = "ok"
    err = ""
    if n == 60:
        else_kind, else_at = find_else(atoms, head + 1, join_at)
        if else_kind == "multi":
            status = "fail"
            err = "multiple_else"
            state["ok"] = False
            state["error"] = err
            messages.append("Branch multiple else — fail explicit")
            for j in range(head + 1, join_at):
                skipped.append(int(atoms[j].dell))
        else:
            taken = eval_condition(st, program, cond or "true")
            true_end = else_at if else_kind == "one" else join_at
            false_start = else_at + 1 if else_kind == "one" else join_at
            messages.append(f"control Branch taken={taken} else={else_kind}")
            if taken:
                program, results = execute_range(program, seed, atoms, head + 1, true_end, depth + 1, messages, ran, skipped, state)
                for j in range(false_start, join_at):
                    skipped.append(int(atoms[j].dell))
                if else_kind == "one":
                    skipped.append(59)
            else:
                for j in range(head + 1, true_end):
                    skipped.append(int(atoms[j].dell))
                if else_kind == "one":
                    skipped.append(59)
                    program, results = execute_range(program, seed, atoms, false_start, join_at, depth + 1, messages, ran, skipped, state)
                else:
                    status = "skipped"
                    messages.append("unchosen branch not executed")
    elif n == 62:
        program, results = execute_range(program, seed, atoms, head + 1, join_at, depth + 1, messages, ran, skipped, state)
        for r in results:
            if not r.get("ok", True):
                messages.append(f"parallel fail captured dell={r.get('dell')} err={r.get('error')}")
    elif n == 63:
        program, results = execute_range(program, seed, atoms, head + 1, join_at, depth + 1, messages, ran, skipped, state)
    elif n in (64, 65):
        loop_limit = bound_of(st)
        pred0 = eval_condition(st, program, cond)
        if n == 64 and pred0:
            status = "zero"
            messages.append("Until already true — zero iterations")
        elif n == 65 and not pred0:
            status = "zero"
            messages.append("While already false — zero iterations")
        else:
            while iterations < loop_limit:
                if n == 64 and eval_condition(st, program, cond):
                    messages.append("Until early exit")
                    break
                if n == 65 and not eval_condition(st, program, cond):
                    messages.append("While early exit")
                    break
                program, chunk = execute_range(program, seed, atoms, head + 1, join_at, depth + 1, messages, ran, skipped, state)
                results.extend(chunk)
                iterations += 1
                st.control_steps += 1
                st = attach(program)
                if n == 64 and eval_condition(st, program, cond):
                    messages.append("Until condition true after body")
                    break
                if n == 65 and not eval_condition(st, program, cond):
                    messages.append("While condition false after body")
                    break
            else:
                still = eval_condition(st, program, cond)
                if n == 64 and not still:
                    status = "bounded"
                    err = "bound_reached"
                    state["ok"] = False
                    state["error"] = err
                    messages.append(f"Until bound={loop_limit} reached")
                if n == 65 and still:
                    status = "bounded"
                    err = "bound_reached"
                    state["ok"] = False
                    state["error"] = err
                    messages.append(f"While bound={loop_limit} reached")
    elif n == 66:
        members = list(st.selected or [])
        prev_ctx = st.context
        prev_route = st.route
        if not members:
            status = "empty"
            messages.append("ForEach empty selection valid")
        for mid in members:
            st.context = str(mid)
            st.route = str(mid)
            messages.append(f"ForEach member={mid}")
            program, chunk = execute_range(program, seed, atoms, head + 1, join_at, depth + 1, messages, ran, skipped, state)
            for item in chunk:
                item["member"] = str(mid)
            results.extend(chunk)
            iterations += 1
            st = attach(program)
        st.context = prev_ctx
        st.route = prev_route
    if join_at < limit and int(getattr(atoms[join_at], "dell", -1)) == 61:
        program, jout = _run_atom(program, atoms[join_at], seed, messages)
        ran.append(61)
        results.append({"dell": 61, "ok": bool(jout.get("ok", True)), "error": jout.get("error") or "", "owned_by": kind})
    st = attach(program)
    st.last_frame = {"kind": kind, "condition": cond, "status": status, "iterations": iterations, "results": results, "error": err, "depth": depth}
    st.last_control = dict(st.last_frame)
    st.frames.append(dict(st.last_frame))
    return program, results


def execute_chain(program: Any, seed: Any, seed_text: str) -> Dict[str, Any]:
    messages = [f"Mandell: {seed.as_mandel()}", f"English: {seed.as_english()}"]
    messages.append(f"Chain atoms={len(seed.atoms)} label={seed.label or ''}")
    ran = []
    skipped = []
    state = {"ok": True, "error": "", "new_program": None}
    attach(program)
    program, _results = execute_range(program, seed, list(seed.atoms), 0, len(seed.atoms), 0, messages, ran, skipped, state)
    new_program = state.get("new_program")
    if new_program is not None:
        program = new_program
    ok = bool(state.get("ok", True))
    last_error = state.get("error") or ""
    st = getattr(program, "core_ii", None)
    # EOC-I: per-node evidence (additive; existing keys unchanged).
    atom_results = [dict(r) for r in (_results or []) if isinstance(r, dict)]
    return {"ok": ok, "error": last_error, "seed": seed.as_mandel(), "english": seed.as_english(), "primary": seed.primary_dell(), "messages": messages, "new_program": new_program, "chain_ran": ran, "chain_skipped": skipped, "atom_results": atom_results, "core_ii": st.snap() if st is not None else {}}
