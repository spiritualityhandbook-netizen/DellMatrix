#!/usr/bin/env python3
"""80-99 object, transaction, and abstraction handlers."""
from __future__ import annotations

import copy
from typing import Any, Dict, List, Tuple

from .predicate import partition_store_operand, result_cell

SPECTRUM_DELLS = set(range(80, 100))
COMPOSE_BOUND = 8
ACTIVE_TX = ("open", "failed", "caught")
TERMINAL_TX = ("committed", "reverted")
TERMINAL_TX_KEEP = 16


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


def _prune_tx(st: Any) -> None:
    """AF-5: prune TERMINAL frames only, keeping the newest
    TERMINAL_TX_KEEP plus ALL active frames (an un-terminated
    Try stack is user state, not garbage). The newest terminal
    frame is the refusal-identity witness for Commit/Revert
    and is always retained. Pruned count lands in the
    session-only st.tx_dropped_total, which also keeps frame
    ids monotonic: id = tx{tx_dropped_total + len(frames)}."""
    frames = _open_tx(st)
    terminal_idx = [i for i, f in enumerate(frames)
                    if f.get("status") in TERMINAL_TX]
    excess = len(terminal_idx) - TERMINAL_TX_KEEP
    if excess <= 0:
        return
    drop = set(terminal_idx[:excess])
    st.tx = [f for i, f in enumerate(frames) if i not in drop]
    st.tx_dropped_total = getattr(st, "tx_dropped_total", 0) + excess


def _sync_depth(st: Any) -> None:
    st.try_depth = len(_active(_open_tx(st)))


def _note_mutation(st: Any, op: str, lab: str, pre: Dict[str, Any]) -> None:
    """Step 9 (B14): the ONE shared diff-baseline authority.
    Every store writer — Set (55, via query_ops) and the
    spectrum writers 84-88 — calls this with pre=_ckpt(st)
    captured after all refusal checks and immediately
    before its mutation. It sets the standalone baseline
    (st.diff_baseline) that Diff reads when no transaction
    frame is active, and records the mutation on the
    innermost active frame's staged_changes ledger."""
    st.diff_baseline = pre
    frames = _active(_open_tx(st))
    if frames:
        frames[-1].setdefault("staged_changes", []).append({"op": op, "lab": lab})


def note_atom_failure(st: Any, err: str) -> None:
    """Step 8 (B15/B16): the ONE canonical outcome hook. Every
    executed atom failure — leaf, Core II, or composition —
    marks the INNERMOST active transaction frame failed.
    The first root cause is preserved in frame["error"]: a
    later failure on an already-failed frame (including a
    commit_illegal raised by a Commit attempt on that frame)
    is recorded in frame["extra_errors"] as additional
    evidence only and never overwrites the root cause. A
    failure after a Catch consumed the frame's error is a new
    root cause (the caught error survives in caught_error).
    Lawful skips and false-predicates-as-data never reach
    this hook — callers fire it only on ok=False outcomes."""
    if not err:
        return
    frames = _active(_open_tx(st))
    if not frames:
        return
    frame = frames[-1]
    if frame.get("status") == "failed":
        # Idempotent re-notes: the same outcome may reach this
        # hook from both the Core II tail and the chain layer;
        # an error already recorded (as root cause or as extra
        # evidence) is never recorded twice.
        if err != frame.get("error") \
                and err not in frame.get("extra_errors", []):
            frame.setdefault("extra_errors", []).append(err)
    else:
        frame["status"] = "failed"
        frame["error"] = err
    _sync_depth(st)


def _fail_open_tx(st: Any, err: str) -> None:
    # Assert/Guard keep their in-handler call, which now
    # delegates to the canonical hook (one authority, B15).
    note_atom_failure(st, err)


def apply_spectrum(n: int, st: Any, program: Any, lab: str, term: str, messages: List[str], ids_fn, shot_fn, roles: Any = None) -> Tuple[bool, str]:
    # DAF-01: `roles` carries the validated typed arguments
    # losslessly from chain_exec. When present for Move/Replace/
    # Patch, operand resolution uses the roles directly — the
    # delimiter-flattened lab is never re-split, so a value or
    # destination containing '=' or '>' cannot retarget the
    # operation onto a colliding neighbor key. The handlers
    # below remain the only executors; roles change only how
    # their operands are resolved.
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
        if name and st.scope == name:
            messages.append(
                f"Ungroup warning: scope {name!r} is now undefined; "
                "Select will refuse until the scope is reset")
    elif n == 84:
        src = lab or (st.selected[0] if st.selected else "object")
        dest = f"copy_{src}"
        pre = _ckpt(st)
        st.store[dest] = copy.deepcopy(st.store.get(src, src))
        _note_mutation(st, "copy", lab, pre)
        messages.append(f"Copy {src}->{dest} original_intact")
        # C2: Publish produced value via existing last_result authority.
        # The dest key is the authoritative produced value.
        st.last_result = result_cell(value=dest, matched=True, count=1,
                                     source="copy", predicate=lab or "*",
                                     trace="84")
    elif n == 85:
        if roles is not None:
            src, dest, _amb = roles.get("source", ""), roles.get("destination", ""), False
        else:
            src, dest, _amb = partition_store_operand(st.store, lab, ">")
            src, dest = src.strip(), dest.strip()
        if _amb:
            ok, err = False, "ambiguous_move"
            messages.append("Move ambiguous — use typed roles (source=..., destination=...)")
            st.last_result = result_cell(value=None, matched=False, source="move",
                                         predicate=lab or "*", error="ambiguous_move",
                                         trace="85")
        elif not src or not dest:
            ok, err = False, "malformed_move"
            messages.append("Move malformed")
            # C2: Failed producer must not expose a successful result.
            st.last_result = result_cell(value=None, matched=False, source="move",
                                         predicate=lab or "*", error="malformed_move",
                                         trace="85")
        elif src not in st.store:
            ok, err = False, "move_missing"
            messages.append(f"Move miss {src}")
            st.last_result = result_cell(value=None, matched=False, source="move",
                                         predicate=lab or "*", error="move_missing",
                                         trace="85")
        elif dest != src:
            pre = _ckpt(st)
            st.store[dest] = st.store.pop(src)
            _note_mutation(st, "move", lab, pre)
            messages.append(f"Move {src}->{dest} identity_preserved")
            # C2: Publish produced value. The dest key holds the moved value.
            st.last_result = result_cell(value=dest, matched=True, count=1,
                                         source="move", predicate=lab or "*",
                                         trace="85")
        else:
            messages.append("Move same identity")
            st.last_result = result_cell(value=src, matched=True, count=1,
                                         source="move", predicate=lab or "*",
                                         trace="85")
    elif n == 86:
        key = lab
        # C2: Delete has NO_AUTHORITATIVE_RESULT.
        # Deletion produces nothing; there is no value to publish.
        # We set last_result to explicit non-matched to prevent stale results
        # from masquerading as this operation's result.
        if key in st.store:
            pre = _ckpt(st)
            shot_fn()
            st.store.pop(key, None)
            _note_mutation(st, "delete", lab, pre)
            messages.append(f"Delete store[{key}]")
            st.last_result = result_cell(value=None, matched=False, source="delete",
                                         predicate=key or "*", trace="86")
        elif key in st.groups:
            pre = _ckpt(st)
            shot_fn()
            st.groups.pop(key, None)
            _note_mutation(st, "delete", lab, pre)
            messages.append(f"Delete group[{key}]")
            st.last_result = result_cell(value=None, matched=False, source="delete",
                                         predicate=key or "*", trace="86")
        else:
            ok, err = False, f"delete_missing:{key or 'empty'}"
            messages.append(f"Delete miss {key or '(empty)'}")
            st.last_result = result_cell(value=None, matched=False, source="delete",
                                         predicate=key or "*",
                                         error=f"delete_missing:{key or 'empty'}",
                                         trace="86")
    elif n == 87:
        if roles is not None:
            old, new, _amb = roles.get("old", ""), roles.get("new", ""), False
        else:
            old, new, _amb = partition_store_operand(st.store, lab, ">")
            old, new = old.strip(), new.strip()
        if _amb:
            ok, err = False, "ambiguous_replace"
            messages.append("Replace ambiguous — use typed roles (old=..., new=...)")
            st.last_result = result_cell(value=None, matched=False, source="replace",
                                         predicate=lab or "*",
                                         error="ambiguous_replace",
                                         trace="87")
        elif old not in st.store:
            ok, err = False, f"replace_missing:{old}"
            messages.append(f"Replace miss {old}")
            st.last_result = result_cell(value=None, matched=False, source="replace",
                                         predicate=lab or "*",
                                         error=f"replace_missing:{old}",
                                         trace="87")
        else:
            result_key = new or old
            if result_key != old and result_key in st.store:
                # MPC-012 §0 / MPC-011 J-decision: occupied destination REFUSES
                # BY DEFAULT. Honest failure, zero mutation, no silent
                # destruction. No overwrite flag in this round.
                ok, err = False, f"replace_occupied:{result_key}"
                messages.append(f"Replace refused {old}->{result_key} (occupied)")
                st.last_result = result_cell(value=None, matched=False, source="replace",
                                             predicate=lab or "*",
                                             error=f"replace_occupied:{result_key}",
                                             trace="87")
            else:
                pre = _ckpt(st)
                shot_fn()
                st.store[result_key] = st.store.pop(old)
                _note_mutation(st, "replace", lab, pre)
                messages.append(f"Replace {old}->{new}")
                # C2: Publish produced value. The result_key holds the replaced value.
                st.last_result = result_cell(value=result_key, matched=True, count=1,
                                             source="replace", predicate=lab or "*",
                                             trace="87")
    elif n == 88:
        if roles is not None:
            key, val, _amb = roles.get("key", ""), roles.get("value", ""), False
        else:
            key, val, _amb = partition_store_operand(st.store, lab, "=")
            key = key.strip()
        if _amb:
            ok, err = False, "ambiguous_patch"
            messages.append("Patch ambiguous — use typed roles (key=..., value=...)")
            st.last_result = result_cell(value=None, matched=False, source="patch",
                                         predicate=lab or "*",
                                         error="ambiguous_patch",
                                         trace="88")
        elif key not in st.store:
            ok, err = False, f"patch_miss:{key}"
            messages.append(f"Patch miss {key}")
            st.last_result = result_cell(value=None, matched=False, source="patch",
                                         predicate=lab or "*",
                                         error=f"patch_miss:{key}",
                                         trace="88")
        else:
            pre = _ckpt(st)
            shot_fn()
            st.store[key] = val
            _note_mutation(st, "patch", lab, pre)
            messages.append(f"Patch {key}={val}")
            # C2: Publish produced value. The key was mutated; it is the result.
            st.last_result = result_cell(value=key, matched=True, count=1,
                                         source="patch", predicate=lab or "*",
                                         trace="88")
    elif n == 89:
        # Step 9 (B13/B14): one baseline lifecycle for every
        # writer. An active transaction frame's checkpoint
        # governs; otherwise the standalone baseline captured
        # by _note_mutation immediately before the most
        # recent store mutation (Set 55 included). There is
        # NO fallback to the current state: with no baseline
        # captured in this session Diff refuses
        # baseline_missing and claims NO change-set (changed
        # is None, never []). Reading Diff never captures,
        # replaces, or clears a baseline, so repeated reads
        # return the identical result.
        frames = _active(_open_tx(st))
        if frames:
            before = frames[-1].get("checkpoint") or _ckpt(st)
            source = "transaction"
        elif getattr(st, "diff_baseline", None):
            before = st.diff_baseline
            source = "immediate"
        else:
            before = None
            source = "missing"
        after = _ckpt(st)
        if before is None:
            ok, err = False, "baseline_missing"
            st.last_diff = {"before": None, "after": after.get("store", {}), "changed": None, "label": lab, "baseline": "missing", "available": False, "error": "baseline_missing"}
            messages.append("Diff baseline_missing (no baseline captured)")
        else:
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
        frame = {"id": f"tx{getattr(st, 'tx_dropped_total', 0) + len(frames)}", "checkpoint": _ckpt(st), "staged_changes": [], "status": "open", "error": "", "depth": len(_active(frames))}
        frames.append(frame)
        _prune_tx(st)
        _sync_depth(st)
        messages.append(f"Try id={frame['id']} depth={frame['depth']}")
    elif n == 94:
        frames = _open_tx(st)
        active = _active(frames)
        if not active:
            ok, err = False, "catch_illegal"
            messages.append("Catch illegal")
        else:
            # Step 8 (B16): Catch consumes THIS frame's error —
            # never the sticky global st.last_error and never
            # its own label. A frame with no error of its own
            # reports that explicitly and consumes nothing:
            # its status and error stay exactly as they were.
            # DIR-F14: pending and consumed are distinct state.
            # frame["error"] is the PENDING slot; on consumption
            # it is EMPTIED and the error moves to the archive
            # (caught_error = latest, caught_history = every
            # catch in order). A later Catch therefore finds
            # nothing pending and reports "Catch (no error)";
            # a failure noted after the Catch is a new pending
            # root cause (note_atom_failure, B15) and never
            # erases the archive.
            frame = active[-1]
            captured = frame.get("error") or ""
            if frame.get("status") == "failed" or captured:
                frame["status"] = "caught"
                frame["caught_error"] = captured
                frame.setdefault("caught_history", []).append(captured)
                frame["error"] = ""
                _sync_depth(st)
                messages.append(f"Catch {captured}")
            else:
                messages.append("Catch (no error)")
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
            _prune_tx(st)
            _sync_depth(st)
            messages.append(f"Commit {frame['id']} accepted")
    elif n == 96:
        frames = _open_tx(st)
        active = _active(frames)
        if active:
            frame = active[-1]
            _restore(st, frame.get("checkpoint") or {})
            frame["status"] = "reverted"
            _prune_tx(st)
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
