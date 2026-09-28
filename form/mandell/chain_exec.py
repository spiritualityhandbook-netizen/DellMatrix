#!/usr/bin/env python3
"""Multi-atom Mandell execution.

CORE_I atoms run the existing executor leaf path.
CORE_II atoms run core_ii_exec.
Order of seed.atoms is preserved.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .core_ii_exec import execute_core_ii, attach
from .registry import get_dell, namespace_of


def execute_chain(program: Any, seed: Any, seed_text: str) -> Dict[str, Any]:
    from form.mandell.executor import execute_seed

    messages: List[str] = [f"Mandell: {seed.as_mandel()}", f"English: {seed.as_english()}"]
    messages.append(f"Chain atoms={len(seed.atoms)} label={seed.label or ''}")
    ran: List[int] = []
    skipped: List[int] = []
    blocked = False
    new_program = None
    ok = True
    last_error = ""

    attach(program)

    for i, atom in enumerate(seed.atoms):
        n = int(atom.dell)
        term = getattr(atom, "resolved_term", None) or atom.term
        ns = namespace_of(n)
        messages.append(f"-- atom[{i}] {n:02d}[{term}] ns={ns}")
        if blocked and n not in (61, 94, 96):
            skipped.append(n)
            messages.append("skipped after guard/assert block")
            continue
        if 51 <= n <= 99:
            out = execute_core_ii(program, n, term, seed.label or "", messages)
            ran.append(n)
            if not out.get("ok"):
                ok = False
                last_error = out.get("error") or last_error
                if n in (91, 92) and out.get("error") in ("assert_fail", "guard_block"):
                    blocked = True
        elif 0 <= n <= 50:
            leaf = f"{n:02d}[{atom.term}]"
            if seed.label:
                leaf += f" :: {seed.label}"
            out = execute_seed(program, leaf, _leaf=True)
            ran.append(n)
            for msg in out.get("messages") or []:
                if msg.startswith("Mandell:") or msg.startswith("English:"):
                    continue
                messages.append(msg)
            if out.get("new_program") is not None:
                new_program = out["new_program"]
                program = new_program
            if not out.get("ok", True):
                ok = False
                last_error = out.get("error") or last_error
        else:
            d = get_dell(n)
            name = (d or {}).get("name", str(n))
            messages.append(f"Dell {n}[{name}] reserved/not-active")
            skipped.append(n)

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
