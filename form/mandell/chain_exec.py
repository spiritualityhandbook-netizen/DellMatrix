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
    FLOW_CONTRACT,
    bound_of,
    eval_condition,
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


def _run_body(program: Any, seed: Any, atoms: List[Any], start: int, end: int, messages: List[str]) -> Tuple[Any, List[Dict[str, Any]]]:
    results: List[Dict[str, Any]] = []
    i = start
    while i < end:
        atom = atoms[i]
        program, out = _run_atom(program, atom, seed, messages)
        results.append({"dell": int(atom.dell), "ok": bool(out.get("ok", True)), "error": out.get("error") or ""})
        i += 1
    return program, results


def execute_chain(program: Any, seed: Any, seed_text: str) -> Dict[str, Any]:
    messages: List[str] = [f"Mandell: {seed.as_mandel()}", f"English: {seed.as_english()}"]
    messages.append(f"Chain atoms={len(seed.atoms)} label={seed.label or ''}")
    ran: List[int] = []
    skipped: List[int] = []
    blocked = False
    over = False
    new_program = None
    ok = True
    last_error = ""
    last_ok = True

    st = attach(program)
    atoms = list(seed.atoms)
    i = 0
    while i < len(atoms):
        atom = atoms[i]
        n = int(atom.dell)
        if i > 0:
            action = _apply_flow(st, _flow_at(seed, i - 1), last_ok, atoms[i - 1], atom, messages)
            if action == "skip":
                skipped.append(n)
                last_ok = False
                i += 1
                continue
            if action == "over":
                over = True
        if over and n != 61:
            skipped.append(n)
            messages.append(f"skipped by FlowOver {n}")
            i += 1
            continue
        if blocked and n not in (61, 94, 96):
            skipped.append(n)
            messages.append("skipped after join/guard block")
            i += 1
            continue

        if n in (60, 62, 63, 64, 65, 66):
            program, head = _run_atom(program, atom, seed, messages)
            ran.append(n)
            if head.get("new_program") is not None:
                new_program = head["new_program"]
                program = new_program
            st = attach(program)
            join_at = find_join(atoms, i + 1)
            body_atoms = atoms[i + 1:join_at]
            kind = {60: "branch", 62: "parallel", 63: "sequence", 64: "until", 65: "while", 66: "foreach"}[n]
            raw_term = getattr(atom, "term", "") or ""
            canon = str((get_dell(n) or {}).get("name", "")).lower()
            cond = raw_term if raw_term.lower() != canon else (seed.label or "")
            results: List[Dict[str, Any]] = []
            iterations = 0
            status = "ok"
            err = ""

            if n == 60:
                taken = eval_condition(st, program, cond or "true")
                messages.append(f"control Branch taken={taken}")
                if taken:
                    program, results = _run_body(program, seed, atoms, i + 1, join_at, messages)
                    ran.extend(int(a.dell) for a in body_atoms)
                else:
                    skipped.extend(int(a.dell) for a in body_atoms)
                    messages.append("unchosen branch not executed")
                    status = "skipped"
            elif n == 62:
                program, results = _run_body(program, seed, atoms, i + 1, join_at, messages)
                ran.extend(int(a.dell) for a in body_atoms)
                for r in results:
                    if not r.get("ok", True):
                        messages.append(f"parallel fail captured dell={r.get('dell')} err={r.get('error')}")
            elif n == 63:
                program, results = _run_body(program, seed, atoms, i + 1, join_at, messages)
                ran.extend(int(a.dell) for a in body_atoms)
            elif n in (64, 65):
                limit = bound_of(st)
                pred0 = eval_condition(st, program, cond)
                if n == 64 and pred0:
                    status = "zero"
                    messages.append("Until already true — zero iterations")
                elif n == 65 and not pred0:
                    status = "zero"
                    messages.append("While already false — zero iterations")
                else:
                    while iterations < limit:
                        if n == 64 and eval_condition(st, program, cond):
                            break
                        if n == 65 and not eval_condition(st, program, cond):
                            break
                        program, chunk = _run_body(program, seed, atoms, i + 1, join_at, messages)
                        results.extend(chunk)
                        iterations += 1
                        st.control_steps += 1
                    else:
                        if n == 64 and not eval_condition(st, program, cond):
                            status = "bounded"
                            err = "bound_reached"
                            ok = False
                            last_error = err
                            messages.append(f"Until bound={limit} reached")
                        if n == 65 and eval_condition(st, program, cond):
                            status = "bounded"
                            err = "bound_reached"
                            ok = False
                            last_error = err
                            messages.append(f"While bound={limit} reached")
                    ran.extend(int(a.dell) for a in body_atoms)
            elif n == 66:
                members = list(st.selected or [])
                prev_ctx = st.context
                if not members:
                    status = "empty"
                    messages.append("ForEach empty selection valid")
                for mid in members:
                    st.context = str(mid)
                    st.route = str(mid)
                    messages.append(f"ForEach member={mid}")
                    program, chunk = _run_body(program, seed, atoms, i + 1, join_at, messages)
                    for item in chunk:
                        item["member"] = str(mid)
                    results.extend(chunk)
                    iterations += 1
                if members:
                    ran.extend(int(a.dell) for a in body_atoms)
                st.context = prev_ctx

            st.last_frame = {
                "kind": kind,
                "condition": cond,
                "status": status,
                "iterations": iterations,
                "results": results,
                "error": err,
            }
            st.last_control = dict(st.last_frame)
            st.frames.append(dict(st.last_frame))
            last_ok = status not in ("bounded", "fail")
            i = join_at
            continue

        program, out = _run_atom(program, atom, seed, messages)
        if out.get("skipped"):
            skipped.append(n)
        else:
            ran.append(n)
        if out.get("new_program") is not None:
            new_program = out["new_program"]
            program = new_program
        last_ok = bool(out.get("ok", True))
        if not last_ok:
            ok = False
            last_error = out.get("error") or last_error
            if n in (91, 92) and out.get("error") in ("assert_fail", "guard_block"):
                if _flow_at(seed, i) == ">>":
                    blocked = True
            if n == 61 and out.get("error") == "join_fail":
                blocked = True
        if n == 61:
            over = False
            blocked = blocked and out.get("error") == "join_fail"
        i += 1

    st = getattr(program, "core_ii", None)
    return {
        "ok": ok,
        "error": last_error,
        "seed": seed.as_mandel(),
        "english": seed.as_english(),
        "primary": seed.primary_dell(),
        "messages": messages,
        "new_program": new_program,
        "chain_ran": ran,
        "chain_skipped": skipped,
        "core_ii": st.snap() if st is not None else {},
    }
