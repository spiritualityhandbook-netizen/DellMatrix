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
    bound_detail,
    eval_condition,
    find_else,
    find_join,
)
from .core_ii_exec import append_snapshot, attach, execute_core_ii
from .registry import get_dell, namespace_of


def _eff_label(atom: Any, seed: Any) -> str:
    """AF-2: an atom's effective label is its own segment label
    when its segment carried one, else the seed's (last segment's)
    label. This preserves the historical trailing-label shape —
    every atom falls back to the shared trailing label — while a
    mid-chain segment label now stays with its own atom instead of
    being swallowed into (or overwritten by) the trailing one."""
    lab = getattr(atom, "label", "") or ""
    return lab if lab else (getattr(seed, "label", "") or "")


def _sub_seed_text(seed: Any, atoms: Any, start: int, end: int) -> str:
    """Reconstruct the seed text for atoms[start:end] of a parsed
    seed (C13: a Simulate head's rehearsal operand). Segment
    labels are resolved per atom via _eff_label and baked in, so
    the reconstruction round-trips through parse_seed with the
    same dispatch-time labels (the AF-1 re-emission precedent)."""
    from dataclasses import replace as _replace
    from .seed import Seed as _Seed
    eff = [_eff_label(a, seed) for a in atoms[start:end]]
    flows = list(getattr(seed, "flows", []) or [])[start:end - 1]
    if any(eff[:-1]):
        sub_atoms = [_replace(a, label=lab)
                     for a, lab in zip(atoms[start:end], eff)]
        return _Seed(atoms=sub_atoms, flows=flows, label="").as_mandel()
    sub_atoms = [_replace(a, label="") for a in atoms[start:end]]
    return _Seed(atoms=sub_atoms, flows=flows,
                 label=eff[-1] if eff else "").as_mandel()


def _skip_receipt(n: int, reason: str) -> Dict[str, Any]:
    """Step 7 (DAF-08): occurrence-level receipt for an atom that
    did NOT execute for a lawful/control reason. Shape follows
    Director Decision 1 (ok=False, skipped=True, explicit reason)
    with error="" — a lawful conditional skip is not a failure,
    and Join failure counting excludes skipped receipts."""
    return {"dell": int(n), "ok": False, "skipped": True,
            "error": "", "reason": reason}


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
    payload = _eff_label(atom, seed)
    if raw_term and raw_term.lower() != canon:
        payload = raw_term
    # TOAM-I C3: Wire typed args into production execution.
    # If atom has typed args, validate and lower to lab format.
    # DAF-01: the validated+resolved roles ALSO ride to the
    # canonical handler as structured data (roles_arg) — the
    # lowered lab remains for trace/conflict compatibility, but
    # delimiter-bearing role values are never recovered by
    # re-splitting it.
    roles_arg = None
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
            # AF-1: a chainlink member term is a link slot, not a legacy
            # lab — it never counts as the legacy side of a conflict.
            typed_lab = lower_args_to_lab(n, resolved_args)
            legacy = payload
            if getattr(atom, "origin", "") == "chainlink":
                legacy = _eff_label(atom, seed)
            if legacy and legacy != typed_lab:
                err_msg = f"ARGUMENT_CONFLICT for {n:02d}[{shown}]: typed args lower to '{typed_lab}' but legacy lab is '{legacy}'"
                messages.append(err_msg)
                return program, {"ok": False, "error": "ARGUMENT_CONFLICT", "messages": messages}
            payload = typed_lab
            roles_arg = dict(resolved_args)
            messages.append(f"TOAM: typed args lowered to lab='{payload}'")
        else:
            # D1-UNSUPPORTED-ARG-GATE (Director MODE C repair,
            # 2026-11-03): typed args on an UNREGISTERED Core II
            # Dell refuse BEFORE the handler executes. Previously
            # the args were never read and the atom executed on
            # the legacy payload — silent success under a
            # default, label-wins, or a misleading handler
            # failure (PR #252 investigation, Q1). Diagnostics
            # name sorted role NAMES only; raw argument values
            # are never echoed (Director amendment).
            roles = ", ".join(sorted(atom_args))
            messages.append(
                f"TOAM: Dell {n:02d}[{shown}] has no registered "
                f"typed signature; typed arguments refused "
                f"before execution (roles: {roles})")
            return program, {"ok": False,
                             "error": f"UNSUPPORTED_ARGS: {roles}",
                             "messages": messages}
    term = shown
    messages.append(f"-- {n:02d}[{term}] ns={ns}")
    if 51 <= n <= 99:
        out = execute_core_ii(program, n, term, payload, messages, roles=roles_arg)
        return program, out
    if 0 <= n <= 50:
        leaf = f"{n:02d}[{atom.term}]"
        if atom_args:
            # AF-1: carry typed args into the leaf re-execution so the
            # leaf path's own TOAM authority (e.g. Dell 8 validation +
            # wiring in executor_leaf) sees exactly what the single-atom
            # path sees. Arg values originate from the seed parser's
            # quoted-string grammar, so re-emission parses identically.
            leaf += "(" + ", ".join(
                f'{k}="{v}"' for k, v in atom_args.items()) + ")"
        _leaf_label = _eff_label(atom, seed)
        if _leaf_label:
            leaf += f" :: {_leaf_label}"
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
    # DIRECTOR DECISION 1 (GDP-001 Phase-0 gate): unified atom truth.
    # A reserved/unexecuted atom did NOT successfully execute merely because
    # its containing chain is allowed to continue. Atom-level truth:
    #   ok=False, skipped=True, reason=<explicit honest reason>.
    # ATOM EXECUTION RESULT != CHAIN CONTINUATION POLICY: the chain continues
    # (execute_range does not abort), but the atom record is honest.
    # No consumer may infer ok=True for an operation that did not execute.
    return program, {"ok": False, "skipped": True,
                     "error": "reserved/not-active",
                     "reason": f"Dell {n}[{name}] is reserved/not-active; "
                               f"atom not executed (chain continues per policy)"}


def _note_chain_failure(program: Any, out: Dict[str, Any]) -> None:
    """Step 8 (B15): chain-side call site of the ONE canonical
    outcome hook (spectrum_ops.note_atom_failure). Covers leaf
    atoms and pre-execution chain failures (TOAM validation,
    reference, argument conflict) that never reach
    execute_core_ii; Core II outcomes are re-noted
    idempotently (the hook preserves the first root cause and
    never duplicates the same error). Lawful skips carry
    skipped=True and are NOT failures — an atom that never
    ran cannot fail a frame."""
    if out.get("ok", True) or out.get("skipped"):
        return
    err = out.get("error") or ""
    if not err:
        return
    try:
        from form.mandell.spectrum_ops import note_atom_failure
        note_atom_failure(attach(program), err)
    except Exception:
        pass


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
    # DD-51 Ring 1: the flow operators below write Core II
    # slices (refs, context, route) outside Dell dispatch.
    # They pass through the ONE _note_mutation door with a
    # _ckpt captured immediately before the write, exactly
    # like every Dell writer — otherwise the standalone
    # baseline would silently misattribute a flow-written
    # change to whichever Dell noted last.
    from form.mandell.spectrum_ops import _ckpt as _flow_ckpt, \
        _note_mutation as _flow_note
    if flow == ":":
        term = getattr(next_atom, "term", "")
        pre = _flow_ckpt(st)
        st.context = term
        _flow_note(st, "flowby", term, pre)
        messages.append(f"FlowBy bind context={term}")
        return "run"
    if flow == "::":
        term = getattr(next_atom, "term", "")
        pre = _flow_ckpt(st)
        st.refs["deep"] = term
        _flow_note(st, "deepflowby", term, pre)
        messages.append(f"DeepFlowBy {term}")
        return "run"
    if flow == ":>":
        term = getattr(next_atom, "term", "")
        pre = _flow_ckpt(st)
        st.route = term or st.route
        _flow_note(st, "flowtowards", term, pre)
        messages.append(f"FlowTowards {st.route}")
        return "run"
    if flow == "<:":
        term = getattr(prev_atom, "term", "")
        pre = _flow_ckpt(st)
        st.refs["from"] = term
        _flow_note(st, "flowfrom", term, pre)
        messages.append(f"FlowFrom {term}")
        return "run"
    if flow == "<:>":
        pre = _flow_ckpt(st)
        st.refs["from"] = getattr(prev_atom, "term", "")
        st.route = getattr(next_atom, "term", "") or st.route
        _flow_note(st, "dynamicflow",
                   f"{st.refs.get('from')}->{st.route}", pre)
        messages.append(f"DynamicFlow {st.refs.get('from')}->{st.route}")
        return "run"
    if flow == "<<[Delta]":
        append_snapshot(st)
        messages.append(f"DeltaFlow checkpoint snapshots={len(st.snapshots)}")
        return "run"
    return "run"


def _payload_cond(atom: Any, seed: Any, n: int) -> str:
    raw_term = getattr(atom, "term", "") or ""
    canon = str((get_dell(n) or {}).get("name", "")).lower()
    if raw_term and raw_term.lower() != canon:
        return raw_term
    return _eff_label(atom, seed)


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
                # DIRECTOR DECISION 1: flow-blocked atoms are unexecuted —
                # ok=False with explicit reason, consistent with reserved skips.
                results.append({"dell": n, "ok": False, "error": "flow_thru_block",
                                "skipped": True,
                                "reason": f"Dell {n} blocked by FlowThru (previous atom did not succeed); not executed"})
                last_ok = False
                i += 1
                continue
            if action == "over":
                while i < end and int(atoms[i].dell) != 61:
                    skipped.append(int(atoms[i].dell))
                    # Step 7 (DAF-08): a FlowOver-skipped occurrence
                    # gets its own receipt, in atom order — the
                    # aggregates derive from atom_results, so a
                    # skipped list entry alone left any_skipped and
                    # partial contradicting chain_skipped.
                    results.append(_skip_receipt(
                        int(atoms[i].dell),
                        "skipped by FlowOver (>>> — skip forward to Join); not executed"))
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
            program, chunk, head_receipt = _run_control(program, seed, atoms, i, end, depth, messages, ran, skipped, state)
            # Step 7 (DAF-08): the control HEAD occurrence carries
            # its own receipt, inserted here (its caller) so the
            # frame's results list inside _run_control keeps its
            # established body+join shape while atom_results is
            # occurrence-complete and atom-ordered.
            results.append(head_receipt)
            results.extend(chunk)
            last_ok = all(r.get("ok", True) for r in [head_receipt] + chunk) if chunk or head_receipt else True
            join_at = find_join(atoms, i + 1, end)
            i = join_at + 1 if join_at < end and int(getattr(atoms[join_at], "dell", -1)) == 61 else join_at
            st = attach(program)
            continue
        if n == 31 and i + 1 < end:
            # C13 (DD-21): Dell 31 [Simulate] is a rehearsal head —
            # the atoms after it in this range are its operand (a
            # "::" followed by an atom is the DeepFlowBy operator,
            # so the grammar hands them to this head the way Loop's
            # body follows Loop). The simulate board rehearses them
            # against an isolated copy; none executes live, and
            # their receipts ride atom_results marked
            # simulated=True. The head's own truth: ok iff the
            # rehearsal ran; a refusal (parse / external-effect /
            # unsupported domain / nested Simulate) is an
            # unexecuted atom — ok=False, skipped=True, reason.
            from form.dell_matrix.simulate_board import run_simulation
            rcpt = run_simulation(
                program, _sub_seed_text(seed, atoms, i + 1, end))
            for _line in rcpt.get("lines") or []:
                messages.append(_line)
            state["simulate"] = rcpt
            _sim_ok = bool(rcpt.get("ok"))
            results.append({"dell": 31, "ok": _sim_ok,
                            "error": rcpt.get("error") or "",
                            "skipped": not _sim_ok,
                            "reason": rcpt.get("reason") or "",
                            "simulated": False})
            for _a in rcpt.get("atom_results") or []:
                results.append({**_a, "simulated": True})
            if _sim_ok:
                ran.append(31)
                last_ok = True
            else:
                skipped.append(31)
                last_ok = False
                state["ok"] = False
                state["error"] = rcpt.get("error") or state.get("error") or ""
            i = end
            continue
        program, out = _run_atom(program, atom, seed, messages)
        _note_chain_failure(program, out)
        if out.get("skipped"):
            skipped.append(n)
        else:
            ran.append(n)
        if out.get("new_program") is not None:
            program = out["new_program"]
            state["new_program"] = program
            # Step 3b: the Sanitize redaction flag rides a program swap.
            try:
                from .redaction import has_sanitize as _hs
                if _hs(seed):
                    program._chain_sanitize_redact = True
            except Exception:
                pass
        # Step 3c (DAF-02, Director Mode D): NO in-place
        # sanitization of the atom's result cell. last_result is
        # EXECUTABLE state — downstream atoms resolve operands
        # from it (predicate included) — so the live cell keeps
        # the real values exactly as a non-Sanitize control
        # leaves them. Step 3b sanitized predicate/error here in
        # place; the Director's probes showed a later Set using
        # last_result then copied "password=[REDACTED]" as data.
        # Disclosure is handled at the detached evidence
        # boundaries (RedactingMessages traces, the sanitized
        # returned snapshot/atom_results, history/outcome
        # writers), never by rewriting canonical state.
        last_ok = bool(out.get("ok", True))
        # 72-17 R-B: an atom's structured directive (bare Show's
        # "render") rides the shared chain state to the chain result;
        # the minimal atom receipts stay unchanged.
        if out.get("directive"):
            state["directive"] = out["directive"]
        # DIRECTOR DECISION 1: atom record carries unified truth —
        # ok=False, skipped=True, reason=<explicit> for unexecuted atoms.
        # The chain continues (no abort); the aggregate reflects the truth.
        results.append({"dell": n, "ok": last_ok, "error": out.get("error") or "",
                        "skipped": bool(out.get("skipped", False)),
                        "reason": out.get("reason") or out.get("error") or ""})
        if not last_ok:
            state["ok"] = False
            state["error"] = out.get("error") or state.get("error") or ""
        if n == 13 and last_ok and not out.get("skipped") and i + 1 < end:
            # DD-14: Dell 13[Loop] is a chain repetition head. The
            # leaf ran Loop's own ringed growth ONCE with the full
            # count (its receipt line claims requested/executed);
            # the atoms AFTER Loop in this range are its body and
            # must execute `executed` times in total. The main loop
            # has NOT run them yet at this point (Loop is the atom
            # under execution), so the body range executes here,
            # `executed` times, and the main loop then skips past
            # it. The
            # count grammar is the leaf's own (_parse_count,
            # DIR-F13) over the same effective label the leaf saw,
            # clamped identically (1..5); an unparseable label
            # already failed the leaf above, so no repetition is
            # owed. Repetition stops at the first body failure
            # (first-failure truth, 72-19). Nested Loops recurse
            # through execute_range itself; control heads inside
            # the body keep their frame semantics per round.
            from .executor_leaf import _parse_count
            _raw = (_eff_label(atom, seed) or "").strip()
            _parsed = _parse_count(_raw) if _raw else 1
            if _parsed is not None:
                _executed = max(1, min(_parsed, 5))
                for _round in range(_executed):
                    program, chunk = execute_range(
                        program, seed, atoms, i + 1, end, depth,
                        messages, ran, skipped, state)
                    results.extend(chunk)
                    if chunk:
                        last_ok = bool(chunk[-1].get("ok", True))
                    if any(not r.get("ok", True) and not r.get("skipped")
                           for r in chunk):
                        break
                i = end - 1
        i += 1
    return program, results


def _run_control(program, seed, atoms, head, limit, depth, messages, ran, skipped, state):
    atom = atoms[head]
    n = int(atom.dell)
    program, head_out = _run_atom(program, atom, seed, messages)
    _note_chain_failure(program, head_out)
    ran.append(n)
    # Step 7 (DAF-08): the head occurrence's receipt is returned
    # to execute_range (which inserts it in atom order); it is
    # NOT part of the frame's results (body + join shape kept).
    head_receipt = {"dell": n, "ok": bool(head_out.get("ok", True)),
                    "error": head_out.get("error") or "",
                    "skipped": bool(head_out.get("skipped", False)),
                    "reason": head_out.get("reason") or head_out.get("error") or ""}
    st = attach(program)
    join_at = find_join(atoms, head + 1, limit)
    kind = {60: "branch", 62: "parallel", 63: "sequence", 64: "until", 65: "while", 66: "foreach"}[n]
    cond = _payload_cond(atom, seed, n)
    results = []
    iterations = 0
    status = "ok"
    err = ""
    head_err = head_out.get("error") or ""
    if head_err.startswith("UNSUPPORTED_ARGS"):
        # D1 gate, Q-D2 Option A: a refused control head never
        # runs its body on the label condition (that would be
        # the same dishonesty class the gate exists to close).
        # Body occurrences receipt honest skips, the frame
        # fails, zero iterations; the Join below still closes
        # the frame and publishes this status. An earlier root
        # cause in state is never overwritten.
        status = "fail"
        err = head_err
        state["ok"] = False
        if not state.get("error"):
            state["error"] = head_err
        messages.append(
            f"control head {n:02d} refused ({head_err}) — body not executed")
        for j in range(head + 1, join_at):
            skipped.append(int(atoms[j].dell))
            results.append(_skip_receipt(
                int(atoms[j].dell),
                f"control head refused: {head_err}; "
                f"body occurrence not executed"))
    elif n == 60 and head_err == "condition_unparseable":
        # DD-42: the Branch head atom refused its condition —
        # the same wholesale-refusal shape as the D1 gate
        # above: no arm executes, body occurrences receipt
        # honest skips, the frame fails with the engine error.
        status = "fail"
        err = head_err
        state["ok"] = False
        if not state.get("error"):
            state["error"] = head_err
        messages.append(
            f"control head {n:02d} refused ({head_err}) — body not executed")
        for j in range(head + 1, join_at):
            skipped.append(int(atoms[j].dell))
            results.append(_skip_receipt(
                int(atoms[j].dell),
                f"control head refused: {head_err}; "
                f"body occurrence not executed"))
    elif n == 60:
        else_kind, else_at = find_else(atoms, head + 1, join_at)
        if else_kind == "multi":
            status = "fail"
            err = "multiple_else"
            state["ok"] = False
            state["error"] = err
            messages.append("Branch multiple else — fail explicit")
            for j in range(head + 1, join_at):
                skipped.append(int(atoms[j].dell))
                results.append(_skip_receipt(
                    int(atoms[j].dell),
                    "branch body not executed — multiple else markers (multiple_else)"))
        else:
            taken = eval_condition(st, program, cond or "true")
            true_end = else_at if else_kind == "one" else join_at
            false_start = else_at + 1 if else_kind == "one" else join_at
            messages.append(f"control Branch taken={taken} else={else_kind}")
            if taken:
                program, results = execute_range(program, seed, atoms, head + 1, true_end, depth + 1, messages, ran, skipped, state)
                # Step 7 (DAF-08): unchosen occurrences get receipts
                # in atom order (Else marker before the false arm);
                # the chain_skipped list order is unchanged.
                if else_kind == "one":
                    results.append(_skip_receipt(
                        59, "else marker — branch arm separator; not executed as Route"))
                for j in range(false_start, join_at):
                    results.append(_skip_receipt(
                        int(atoms[j].dell),
                        "branch arm not taken; not executed"))
                for j in range(false_start, join_at):
                    skipped.append(int(atoms[j].dell))
                if else_kind == "one":
                    skipped.append(59)
            else:
                for j in range(head + 1, true_end):
                    skipped.append(int(atoms[j].dell))
                    results.append(_skip_receipt(
                        int(atoms[j].dell),
                        "branch arm not taken; not executed"))
                if else_kind == "one":
                    skipped.append(59)
                    results.append(_skip_receipt(
                        59, "else marker — branch arm separator; not executed as Route"))
                    program, _false_results = execute_range(program, seed, atoms, false_start, join_at, depth + 1, messages, ran, skipped, state)
                    results.extend(_false_results)
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
        pred0 = eval_condition(st, program, cond)
        if n == 64 and pred0:
            status = "zero"
            messages.append("Until already true — zero iterations")
            # Step 7 (DAF-08): zero-iteration body occurrences are
            # recorded, not omitted — one skipped receipt each.
            for j in range(head + 1, join_at):
                skipped.append(int(atoms[j].dell))
                results.append(_skip_receipt(
                    int(atoms[j].dell),
                    "until condition already true — zero iterations; body occurrence not executed"))
        elif n == 65 and not pred0:
            status = "zero"
            messages.append("While already false — zero iterations")
            for j in range(head + 1, join_at):
                skipped.append(int(atoms[j].dell))
                results.append(_skip_receipt(
                    int(atoms[j].dell),
                    "while condition already false — zero iterations; body occurrence not executed"))
        else:
            # DD-44: the loop WOULD iterate — its bound must be
            # one the user stated. Unspecified refuses with the
            # ask (what was asked, what is missing, what ran:
            # nothing); an invalid stored limit refuses with
            # its own error. Neither silently becomes 8.
            _bd = bound_detail(st)
            if _bd["status"] != "specified":
                _berr = "bound_unspecified" if _bd["status"] == "unspecified" else _bd["error"]
                status = "fail"
                err = _berr
                state["ok"] = False
                if not state.get("error"):
                    state["error"] = _berr
                head_receipt["ok"] = False
                head_receipt["error"] = _berr
                head_receipt["reason"] = _berr
                messages.append(
                    f"control head {n:02d} refused ({_berr}) — "
                    f"loop bound not specified: state the iteration "
                    f"count with Limit (72) before running "
                    f"{'Until' if n == 64 else 'While'}; nothing ran")
                for j in range(head + 1, join_at):
                    skipped.append(int(atoms[j].dell))
                    results.append(_skip_receipt(
                        int(atoms[j].dell),
                        f"control head refused: {_berr}; "
                        f"body occurrence not executed"))
                loop_limit = 0
            else:
                loop_limit = int(_bd["value"])
            if _bd["status"] == "specified":
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
            # Step 7 (DAF-08/B9): empty selection = zero iterations;
            # body occurrences are recorded as skipped, not omitted.
            for j in range(head + 1, join_at):
                skipped.append(int(atoms[j].dell))
                results.append(_skip_receipt(
                    int(atoms[j].dell),
                    "foreach empty selection — zero iterations; body occurrence not executed"))
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
        # Step 7 (B7): publish the completed block's ACTUAL results
        # to last_frame BEFORE the Join atom runs — the core Join
        # arm reads its incoming from last_frame, so running the
        # Join first (the old order) made its verdict vacuous
        # (incoming=0) whenever children had run.
        st = attach(program)
        st.last_frame = {"kind": kind, "condition": cond, "status": status,
                         "iterations": iterations, "results": list(results),
                         "error": err, "depth": depth}
        program, jout = _run_atom(program, atoms[join_at], seed, messages)
        ran.append(61)
        join_receipt = {"dell": 61, "ok": bool(jout.get("ok", True)), "error": jout.get("error") or "", "owned_by": kind}
        results.append(join_receipt)
        if not join_receipt["ok"]:
            # The frame verdict represents the Join failure; the
            # chain's state error keeps the FIRST root cause
            # (join_fail never overwrites an earlier atom error).
            if status == "ok":
                status = "fail"
            join_err = join_receipt["error"] or ""
            if join_err.startswith("UNSUPPORTED_ARGS"):
                # D1 gate: the Join atom itself was refused
                # before execution — frame/chain error names
                # that refusal rather than masking it as a
                # generic join_fail.
                err = err or join_err
                if state.get("ok", True):
                    state["ok"] = False
                    state["error"] = join_err
            else:
                err = err or "join_fail"
                if state.get("ok", True):
                    state["ok"] = False
                    state["error"] = "join_fail"
    st = attach(program)
    st.last_frame = {"kind": kind, "condition": cond, "status": status, "iterations": iterations, "results": results, "error": err, "depth": depth}
    if n in (64, 65):
        # Step 7 (B8): the frame exposes the bound alongside the
        # actual iterations. DD-44: the stated number, or the
        # honest word "unspecified" — never a phantom default.
        _bd = bound_detail(st)
        st.last_frame["bound"] = _bd["value"] if _bd["status"] == "specified" else _bd["status"]
    st.last_control = dict(st.last_frame)
    st.frames.append(dict(st.last_frame))
    return program, results, head_receipt


def execute_chain(program: Any, seed: Any, seed_text: str) -> Dict[str, Any]:
    # DAF-02/B5: echoes of a chain containing Dell 41[Sanitize] are
    # built from the redacted seed copy (identity for other chains).
    # Step 3b (DAF-02 reopened): the redaction requirement is also
    # CARRIED through the chain — every atom trace appended to the
    # messages list is sanitized at append time, history/traces
    # writers see the transient _chain_sanitize_redact flag, and
    # returned evidence is sanitized before it leaves. Operands
    # execute unchanged; only evidence surfaces are redacted.
    from .redaction import (RedactingMessages, redacted_seed,
                            sanitize_evidence, sanitize_text, has_sanitize)
    _redact = has_sanitize(seed)
    _echo = redacted_seed(seed)
    messages = (RedactingMessages if _redact else list)(
        [f"Mandell: {_echo.as_mandel()}", f"English: {_echo.as_english()}"])
    messages.append(f"Chain atoms={len(seed.atoms)} label={_echo.label or ''}")
    ran = []
    skipped = []
    state = {"ok": True, "error": "", "new_program": None}
    attach(program)
    if _redact:
        try:
            program._chain_sanitize_redact = True
        except Exception:
            pass
    if not getattr(seed, "ok", True):
        # DD-45: a seed the parser REFUSED (ok=False, atoms=[])
        # must never execute as a vacuous success. The front door
        # (executor.execute_seed) checks seed.ok before dispatch;
        # the chain authority enforces the same refusal for direct
        # callers: zero atoms execute; no idea, plane, store,
        # selection, or Nursery state mutates; the parse error is
        # named in the result; exactly one PP3 unknowns-register
        # entry is recorded (in memory now, persisted on the next
        # ordinary save — proven in dd45_recon_test.py). At base this guard
        # was absent — a create+Select seed whose trailing empty
        # label failed parsing returned ok=True here with no atom
        # executed, and the never-created units read as erased
        # state (tour finding DD-45, §12.57a).
        err = getattr(seed, "error", "") or "seed_parse_failed"
        messages.append(f"Chain refused: seed parse failed: {err}")
        try:
            from .executor import _note_unknown
            _note_unknown(program, f"seed: {seed_text[:160]}",
                          f"Seed could not be parsed: {err}",
                          "chain_exec:parse")
        except Exception:
            pass
        st = getattr(program, "core_ii", None)
        _snap = st.snap() if st is not None else {}
        if _redact:
            err = sanitize_text(err)
            _snap = sanitize_evidence(_snap)
        return {"ok": False, "error": err, "seed": _echo.as_mandel(),
                "english": _echo.as_english(),
                "primary": seed.primary_dell(), "messages": messages,
                "new_program": None, "chain_ran": [], "chain_skipped": [],
                "atom_results": [], "partial": False,
                "any_skipped": False, "core_ii": _snap, "directive": None}
    try:
        program, _results = execute_range(program, seed, list(seed.atoms), 0, len(seed.atoms), 0, messages, ran, skipped, state)
    finally:
        if _redact:
            for _p in (program, state.get("new_program")):
                try:
                    if _p is not None:
                        _p._chain_sanitize_redact = False
                except Exception:
                    pass
    new_program = state.get("new_program")
    if new_program is not None:
        program = new_program
    ok = bool(state.get("ok", True))
    last_error = state.get("error") or ""
    if _redact:
        last_error = sanitize_text(last_error)
    st = getattr(program, "core_ii", None)
    # Step 3c (DAF-02, Director Mode D): NO in-place sanitization
    # of canonical state at chain end either. last_result /
    # last_frame / last_control / frames are EXECUTABLE state —
    # later executions resolve operands from last_result and
    # Revert restores from frame/snapshot checkpoints — so they
    # keep the real values exactly as a non-Sanitize control
    # leaves them. Step 3b sanitized them in place here; the
    # Director's probes showed a later Set using last_result
    # copying "password=[REDACTED]" as data and Revert restoring
    # a redacted value. Disclosure is handled below on DETACHED
    # copies only: atom_results and the returned core_ii
    # snapshot are sanitized before they leave, and messages /
    # traces / history / saved JSON are redacted at their own
    # writers.
    # EOC-I: per-node evidence (additive; existing keys unchanged).
    atom_results = [dict(r) for r in (_results or []) if isinstance(r, dict)]
    # DIRECTOR DECISION 1: aggregate chain Outcome must expose
    # partial/skipped/failure state honestly. partial=True when some atoms
    # executed and others did not (mirrors RouteReceipt.partial semantics).
    # Step 7 (DAF-08) documented semantics: atom_results is now
    # occurrence-complete (control heads, unchosen Branch arms, Else
    # markers, FlowOver skips and zero-iteration bodies all carry
    # receipts), and the aggregates derive from those records alone.
    # partial means OCCURRENCE-LEVEL INCOMPLETENESS — at least one
    # occurrence executed successfully and at least one occurrence
    # did not execute (lawful conditional skip, flow skip, reserved)
    # or failed. partial is NOT a failure verdict: a lawful
    # Branch/FlowOver/zero-iteration chain can be ok=True AND
    # partial=True with any_skipped=True; `ok` is governed by state.
    _oks = [bool(r.get("ok", True)) for r in atom_results]
    _partial = bool(atom_results) and any(_oks) and not all(_oks)
    _any_skipped = any(bool(r.get("skipped", False)) for r in atom_results)
    if _redact:
        atom_results = sanitize_evidence(atom_results)
    _snap = st.snap() if st is not None else {}
    if _redact:
        _snap = sanitize_evidence(_snap)
    # 72-17 R-B: a structured directive set by any atom (bare Show's
    # "render") propagates to the chain result; it never rides messages.
    _directive = state.get("directive") or None
    result = {"ok": ok, "error": last_error, "seed": _echo.as_mandel(), "english": _echo.as_english(), "primary": seed.primary_dell(), "messages": messages, "new_program": new_program, "chain_ran": ran, "chain_skipped": skipped, "atom_results": atom_results, "partial": _partial, "any_skipped": _any_skipped, "core_ii": _snap, "directive": _directive}
    # C13 (DD-21): a Simulate head's rehearsal receipt rides the
    # chain result under "simulate" (present only when a Dell 31
    # head ran in this chain).
    if state.get("simulate") is not None:
        result["simulate"] = sanitize_evidence(state["simulate"]) \
            if _redact else state["simulate"]
    # PP5: keep the last chain execution on the program
    # (runtime-only) so the flow renderer can draw what actually
    # ran. Best-effort — rendering support must never break
    # execution.
    try:
        program.last_flow = {
            "seed_text": sanitize_text(seed_text) if has_sanitize(seed) else seed_text,
            "seed": result["seed"],
            "atom_results": [dict(r) for r in atom_results],
            "ok": ok,
            "partial": _partial,
        }
    except Exception:
        pass
    return result
