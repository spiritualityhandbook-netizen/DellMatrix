#!/usr/bin/env python3
"""80-99 object, transaction, and abstraction handlers."""
from __future__ import annotations

import copy
from typing import Any, Dict, List, Tuple

SPECTRUM_DELLS = set(range(80, 100))
COMPOSE_BOUND = 8
ACTIVE_TX = ("open", "failed", "caught")
TERMINAL_TX = ("committed", "reverted")


def _ckpt(st: Any) -> Dict[str, Any]:
    return {
        "scope": st.scope,
        "selected": list(st.selected),
        "store": copy.deepcopy(dict(st.store)),
        "groups": {k: list(v) for k, v in st.groups.items()},
        "defs": dict(st.defs),
        "aliases": dict(st.aliases),
        "compositions": dict(st.compositions),
        "weights": dict(st.weights),
        "context": st.context,
        "route": st.route,
        "refs": dict(st.refs),
        "causes": [tuple(x) for x in st.causes],
        "deps": [tuple(x) for x in st.deps],
        "last_assert": st.last_assert,
        "last_guard": st.last_guard,
    }


def _restore(st: Any, prev: Dict[str, Any]) -> None:
    st.scope = prev.get("scope", st.scope)
    st.selected = list(prev.get("selected") or [])
    st.store = copy.deepcopy(dict(prev.get("store") or {}))
    st.groups = {k: list(v) for k, v in (prev.get("groups") or {}).items()}
    st.defs = dict(prev.get("defs") or {})
    st.aliases = dict(prev.get("aliases") or {})
    st.compositions = dict(prev.get("compositions") or {})
    st.weights = dict(prev.get("weights") or {})
    st.context = prev.get("context", st.context)
    st.route = prev.get("route", st.route)
    st.refs = dict(prev.get("refs") or {})
    st.causes = [tuple(x) for x in (prev.get("causes") or [])]
    st.deps = [tuple(x) for x in (prev.get("deps") or [])]
    st.last_assert = prev.get("last_assert", st.last_assert)
    st.last_guard = prev.get("last_guard", st.last_guard)


def _open_tx(st: Any) -> List[Dict[str, Any]]:
    frames = getattr(st, "tx", None)
    if frames is None:
        st.tx = []
        frames = st.tx
    return frames


def _active(frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [f for f in frames if f.get("status") in ACTIVE_TX]


def _sync_depth(st: Any) -> None:
    st.try_depth = len(_active(_open_tx(st)))


def _note_mutation(st: Any, op: str, lab: str, pre: Dict[str, Any]) -> None:
    st.diff_baseline = pre
    frames = _active(_open_tx(st))
    if frames:
        frames[-1].setdefault("staged_changes", []).append({"op": op, "lab": lab})


def _fail_open_tx(st: Any, err: str) -> None:
    frames = _active(_open_tx(st))
    if frames:
        frames[-1]["status"] = "failed"
        frames[-1]["error"] = err
    _sync_depth(st)


def apply_spectrum(n: int, st: Any, program: Any, lab: str, term: str, messages: List[str], ids_fn, shot_fn) -> Tuple[bool, str]:
    ok, err = True, ""
    if n == 80:
        st.context = lab or st.scope
        messages.append(f"Context -> {st.context}")
    elif n == 81:
        target = lab or (st.selected[0] if st.selected else "")
        name = target or "ref"
        st.refs[name] = target
        messages.append(f"Reference {name} -> {target or '(none)'} no_copy")
    elif n == 82:
        name = lab or "group"
        st.groups[name] = list(st.selected or ids_fn(program))
        messages.append(f"Group {name} n={len(st.groups[name])}")
    elif n == 83:
        name = lab or (list(st.groups)[-1] if st.groups else "")
        members = st.groups.pop(name, [])
        if members and not st.selected:
            st.selected = list(members)
        messages.append(f"Ungroup {name} released={len(members)}")
    elif n == 84:
        src = lab or (st.selected[0] if st.selected else "object")
        dest = f"copy_{src}"
        pre = _ckpt(st)
        st.store[dest] = copy.deepcopy(st.store.get(src, src))
        _note_mutation(st, "copy", lab, pre)
        messages.append(f"Copy {src}->{dest} original_intact")
    elif n == 85:
        src, _, dest = lab.partition(">")
        src, dest = src.strip(), dest.strip()
        if not src or not dest:
            ok, err = False, "malformed_move"
            messages.append("Move malformed")
        elif src not in st.store:
            ok, err = False, "move_missing"
            messages.append(f"Move miss {src}")
        elif dest != src:
            pre = _ckpt(st)
            st.store[dest] = st.store.pop(src)
            _note_mutation(st, "move", lab, pre)
            messages.append(f"Move {src}->{dest} identity_preserved")
        else:
            messages.append("Move same identity")
    elif n == 86:
        key = lab
        if key in st.store:
            pre = _ckpt(st)
            shot_fn()
            st.store.pop(key, None)
            _note_mutation(st, "delete", lab, pre)
            messages.append(f"Delete store[{key}]")
        elif key in st.groups:
            pre = _ckpt(st)
            shot_fn()
            st.groups.pop(key, None)
            _note_mutation(st, "delete", lab, pre)
            messages.append(f"Delete group[{key}]")
        else:
            ok, err = False, f"delete_missing:{key or 'empty'}"
            messages.append(f"Delete miss {key or '(empty)'}")
    elif n == 87:
        old, _, new = lab.partition(">")
        old, new = old.strip(), new.strip()
        if old not in st.store:
            ok, err = False, f"replace_missing:{old}"
            messages.append(f"Replace miss {old}")
        else:
            pre = _ckpt(st)
            shot_fn()
            st.store[new or old] = st.store.pop(old)
            _note_mutation(st, "replace", lab, pre)
            messages.append(f"Replace {old}->{new}")
    elif n == 88:
        key, _, val = lab.partition("=")
        key = key.strip()
        if key not in st.store:
            ok, err = False, f"patch_miss:{key}"
            messages.append(f"Patch miss {key}")
        else:
            pre = _ckpt(st)
            shot_fn()
            st.store[key] = val
            _note_mutation(st, "patch", lab, pre)
            messages.append(f"Patch {key}={val}")
    elif n == 89:
        frames = _active(_open_tx(st))
        if frames:
            before = frames[-1].get("checkpoint") or _ckpt(st)
            source = "transaction"
        elif getattr(st, "diff_baseline", None):
            before = st.diff_baseline
            source = "immediate"
        else:
            before = _ckpt(st)
            source = "current"
        after = _ckpt(st)
        changed = [k for k in set(list(before.get("store", {})) + list(after.get("store", {}))) if before.get("store", {}).get(k) != after.get("store", {}).get(k)]
        st.last_diff = {"before": before.get("store", {}), "after": after.get("store", {}), "changed": changed, "label": lab, "baseline": source}
        messages.append(f"Diff changed={changed} baseline={source}")
    elif n == 90:
        messages.append(f"Trace last {min(8, len(st.traces))}:")
        for item in st.traces[-8:]:
            messages.append(f"  · {item}")
        if not st.traces:
            messages.append("  (empty)")
        st.last_result = {"source": "trace", "value": list(st.traces), "count": len(st.traces), "matched": True}
    elif n == 91:
        from .control_runtime import eval_condition
        passed = eval_condition(st, program, lab or "true")
        st.last_assert = "PASS" if passed else "FAIL"
        messages.append(f"Assert {st.last_assert} {lab or 'true'}")
        if not passed:
            ok, err = False, "assert_fail"
            _fail_open_tx(st, err)
    elif n == 92:
        from .control_runtime import eval_condition
        allow = eval_condition(st, program, lab or "true")
        if lab.lower() in ("block", "deny"):
            allow = False
        st.last_guard = "ALLOW" if allow else "BLOCK"
        messages.append(f"Guard {st.last_guard} {lab or 'default'}")
        if not allow:
            ok, err = False, "guard_block"
            _fail_open_tx(st, err)
    elif n == 93:
        frames = _open_tx(st)
        frame = {"id": f"tx{len(frames)}", "checkpoint": _ckpt(st), "staged_changes": [], "status": "open", "error": "", "depth": len(_active(frames))}
        frames.append(frame)
        _sync_depth(st)
        messages.append(f"Try id={frame['id']} depth={frame['depth']}")
    elif n == 94:
        frames = _open_tx(st)
        captured = st.last_error or lab or ""
        active = _active(frames)
        if not active:
            ok, err = False, "catch_illegal"
            messages.append("Catch illegal")
        else:
            active[-1]["status"] = "caught"
            active[-1]["error"] = captured
            _sync_depth(st)
            messages.append(f"Catch {captured or '(no error)'}")
    elif n == 95:
        frames = _open_tx(st)
        active = _active(frames)
        if not active:
            last = frames[-1] if frames else {}
            ok, err = False, "commit_illegal" if last.get("status") in TERMINAL_TX else "commit_without_try"
            messages.append("Commit illegal")
        elif active[-1].get("status") not in ("open", "caught"):
            ok, err = False, "commit_illegal"
            messages.append(f"Commit illegal from {active[-1].get('status')}")
        else:
            frame = active[-1]
            frame["status"] = "committed"
            frame["accepted"] = copy.deepcopy(dict(st.store))
            st.staged.append({"op": "commit", "id": frame["id"], "accepted": True})
            _sync_depth(st)
            messages.append(f"Commit {frame['id']} accepted")
    elif n == 96:
        frames = _open_tx(st)
        active = _active(frames)
        if active:
            frame = active[-1]
            _restore(st, frame.get("checkpoint") or {})
            frame["status"] = "reverted"
            _sync_depth(st)
            messages.append(f"Revert {frame['id']} exact")
        elif frames and frames[-1].get("status") == "committed":
            ok, err = False, "unrelated_revert"
            messages.append("Revert refused committed transaction")
        elif frames and frames[-1].get("status") == "reverted":
            ok, err = False, "revert_illegal"
            messages.append("Revert illegal on reverted frame")
        elif st.snapshots:
            _restore(st, st.snapshots.pop())
            messages.append(f"Revert snapshot snapshots={len(st.snapshots)}")
        else:
            messages.append("Revert nothing")
    elif n == 97:
        name, _, meaning = lab.partition("=")
        name = (name or "def").strip()
        st.defs[name] = meaning or lab
        messages.append(f"Define {name}")
    elif n == 98:
        name, _, target = lab.partition("=")
        name, target = (name or "alias").strip(), (target or "").strip()
        if not target:
            ok, err = False, "alias_missing"
            messages.append("Alias missing target")
        else:
            _cycle, _resolved, aerr = _alias_resolve(st, target, {name})
            if aerr == "alias_cycle":
                ok, err = False, "alias_cycle"
                messages.append(f"Alias cycle {name}")
            elif aerr == "alias_missing":
                ok, err = False, "alias_missing"
                messages.append(f"Alias missing {target}")
            else:
                st.aliases[name] = target
                messages.append(f"Alias {name}->{target}")
    elif n == 99:
        name, _, body = lab.partition("=")
        name, body = (name or "compose").strip(), (body or "").strip()
        if body:
            parsed, perr = _compose_seed(st, body, stack={name} if name else set(), depth=0)
            if perr:
                ok, err = False, perr
                messages.append(f"Compose {perr}")
            elif not parsed:
                ok, err = False, "malformed_composition"
                messages.append(f"Compose malformed {body}")
            else:
                st.compositions[name] = body
                out = _run_compose(program, parsed)
                if not out.get("ok", True):
                    ok, err = False, out.get("error") or "compose_fail"
                messages.append(f"Compose {name}={body} ran={out.get('chain_ran')}")
        else:
            resolved = _resolve_name(st, name) or name
            body = st.compositions.get(name) or st.compositions.get(resolved) or st.defs.get(resolved, "")
            parsed, perr = _compose_seed(st, body, stack={name, resolved}, depth=0)
            if perr:
                ok, err = False, perr
                messages.append(f"Compose {perr}")
            elif not parsed:
                ok, err = False, "malformed_composition"
                messages.append("Compose missing body")
            else:
                out = _run_compose(program, parsed)
                if not out.get("ok", True):
                    ok, err = False, out.get("error") or "compose_fail"
                messages.append(f"Compose exec {name} ran={out.get('chain_ran')}")
    return ok, err


def _alias_resolve(st: Any, name: str, seen) -> Tuple[bool, str, str]:
    seen = set(seen or [])
    cur = name
    while True:
        if cur in seen:
            return True, cur, "alias_cycle"
        seen.add(cur)
        if cur in st.aliases:
            cur = st.aliases[cur]
            continue
        if cur in st.defs or cur in st.compositions:
            return False, cur, ""
        return False, cur, "alias_missing"


def _resolve_name(st: Any, name: str) -> str:
    _, resolved, err = _alias_resolve(st, name, set())
    return resolved if not err else ""


def _compose_bound(st: Any) -> int:
    from .predicate import validate_bound
    ok, n, _err = validate_bound(getattr(st, "limit", "") or "")
    return n if ok else COMPOSE_BOUND


def _compose_seed(st: Any, body: str, stack=None, depth: int = 0) -> Tuple[str, str]:
    raw = (body or "").strip()
    if not raw:
        return "", "malformed_composition"
    bound = _compose_bound(st)
    if depth > bound:
        return "", "compose_depth"
    if "[" in raw:
        return raw, ""
    stack = set(stack or [])
    parts = [p.strip() for p in raw.replace(",", ">").split(">") if p.strip()]
    atoms = []
    for part in parts:
        if part.isdigit():
            atoms.append(f"{int(part):02d}[ComposeStep]")
            continue
        if part in stack:
            return "", "compose_cycle"
        if part in st.defs or part in st.compositions or part in st.aliases:
            resolved = _resolve_name(st, part) or part
            if resolved in stack or part in stack:
                return "", "compose_cycle"
            inner = st.compositions.get(part) or st.compositions.get(resolved) or st.defs.get(resolved, "")
            if not inner:
                return "", "malformed_composition"
            nested, nerr = _compose_seed(st, inner, stack | {part, resolved}, depth + 1)
            if nerr:
                return "", nerr
            if nested:
                atoms.append(nested)
        else:
            return "", "malformed_composition"
    return " > ".join(atoms), ""


def _run_compose(program: Any, seed_text: str) -> Dict[str, Any]:
    from .executor import execute_seed
    return execute_seed(program, seed_text)
