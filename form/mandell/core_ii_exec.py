#!/usr/bin/env python3
"""Core II runtime 51-99. Formalized executable state."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class CoreIIState:
    scope: str = "plane"
    selected: List[str] = field(default_factory=list)
    store: Dict[str, Any] = field(default_factory=dict)
    groups: Dict[str, List[str]] = field(default_factory=dict)
    defs: Dict[str, str] = field(default_factory=dict)
    aliases: Dict[str, str] = field(default_factory=dict)
    compositions: Dict[str, str] = field(default_factory=dict)
    staged: List[Dict[str, Any]] = field(default_factory=list)
    snapshots: List[Dict[str, Any]] = field(default_factory=list)
    last_error: str = ""
    last_diff: Dict[str, Any] = field(default_factory=dict)
    traces: List[str] = field(default_factory=list)
    weights: Dict[str, float] = field(default_factory=dict)
    context: str = ""
    try_depth: int = 0
    branch: Dict[str, Any] = field(default_factory=dict)
    parallel: List[str] = field(default_factory=list)
    route: str = "primary"
    limit: str = ""
    refs: Dict[str, str] = field(default_factory=dict)
    causes: List[tuple] = field(default_factory=list)
    deps: List[tuple] = field(default_factory=list)
    last_assert: str = ""
    last_guard: str = "ALLOW"
    frames: List[Dict[str, Any]] = field(default_factory=list)
    last_frame: Dict[str, Any] = field(default_factory=dict)
    last_control: Dict[str, Any] = field(default_factory=dict)
    flow_taken: List[str] = field(default_factory=list)
    flow_blocked: List[str] = field(default_factory=list)
    control_steps: int = 0
    last_result: Dict[str, Any] = field(default_factory=dict)
    tx: List[Dict[str, Any]] = field(default_factory=list)
    def snap(self) -> Dict[str, Any]:
        return {"scope": self.scope, "selected": list(self.selected), "store": dict(self.store),
                "groups": {k: list(v) for k, v in self.groups.items()}, "defs": dict(self.defs),
                "aliases": dict(self.aliases), "compositions": dict(self.compositions),
                "staged": len(self.staged), "try_depth": self.try_depth, "context": self.context,
                "route": self.route, "branch": dict(self.branch), "last_assert": self.last_assert,
                "last_guard": self.last_guard, "last_frame": dict(self.last_frame),
                "control_steps": self.control_steps}

def attach(program: Any) -> CoreIIState:
    st = getattr(program, "core_ii", None)
    if not isinstance(st, CoreIIState):
        st = CoreIIState()
        try: program.core_ii = st
        except Exception: pass
    return st

def _ids(program: Any) -> List[str]:
    try: return list(program.cube.session.plane.units.keys())
    except Exception: return list(getattr(program, "_units", {}).keys())

def _pred(label: str, uid: str) -> bool:
    lab = (label or "").lower(); u = str(uid).lower()
    return True if not lab else lab in u or u.startswith(lab.replace(" ", "_"))

def execute_core_ii(program: Any, n: int, term: str, label: str, messages: List[str]) -> Dict[str, Any]:
    st = attach(program); lab = label or ""; ok = True; err = ""
    def mark():
        st.traces.append(f"{n:02d}[{term}]::{lab}")
        if hasattr(program, "note_seed"):
            try: program.note_seed(n, term, lab or term)
            except Exception: pass
    def shot(): st.snapshots.append(st.snap())
    try:
        from .query_ops import QUERY_DELLS, apply_query
        if n in QUERY_DELLS:
            ok, err = apply_query(n, st, program, lab, term, messages, _ids, _pred, shot)
        elif n == 53:
            st.scope = lab or "plane"; messages.append(f"Scope -> {st.scope}")
        elif n == 60:
            from .control_runtime import ControlFrame, eval_condition
            taken = eval_condition(st, program, lab or "true")
            st.branch = {"cond": lab or "true", "taken": taken, "path": "true" if taken else "false"}
            frame = ControlFrame(id=f"br{len(st.frames)}", kind="branch", condition=lab or "true", status="taken" if taken else "skipped")
            st.last_frame = frame.as_dict(); st.frames.append(st.last_frame)
            messages.append(f"Branch cond={lab or 'true'} taken={taken} unchosen_not_run")
        elif n == 61:
            from .control_runtime import ControlFrame
            policy = (lab or "all").lower()
            incoming = list((st.last_frame or {}).get("results") or [])
            fails = [r for r in incoming if not r.get("ok", True)]
            if policy in ("any",):
                join_ok = (not incoming) or any(r.get("ok", True) for r in incoming)
            else:
                join_ok = not fails
            frame = ControlFrame(id=f"jn{len(st.frames)}", kind="join", condition=policy, status="ok" if join_ok else "fail", policy=policy, results=incoming)
            if not join_ok:
                ok = False
                err = "join_fail"
                frame.error = err
            st.last_frame = frame.as_dict(); st.frames.append(st.last_frame)
            messages.append(f"Join policy={policy} ok={join_ok} incoming={len(incoming)} fails={len(fails)}")
        elif n == 62:
            from .control_runtime import ControlFrame
            st.parallel = [p.strip() for p in lab.split(",") if p.strip()] or ["a", "b"]
            frame = ControlFrame(id=f"pr{len(st.frames)}", kind="parallel", status="pending")
            st.last_frame = frame.as_dict(); st.frames.append(st.last_frame)
            messages.append(f"Parallel n={len(st.parallel)} offline_deterministic")
        elif n == 63:
            from .control_runtime import ControlFrame
            frame = ControlFrame(id=f"sq{len(st.frames)}", kind="sequence", status="pending")
            st.last_frame = frame.as_dict(); st.frames.append(st.last_frame)
            messages.append(f"Sequence {lab or 'ordered'}")
        elif n == 64:
            from .control_runtime import ControlFrame, eval_condition, bound_of
            pred = eval_condition(st, program, lab or "false")
            frame = ControlFrame(id=f"un{len(st.frames)}", kind="until", condition=lab or "false", status="ready" if not pred else "zero")
            st.last_frame = frame.as_dict(); st.frames.append(st.last_frame)
            messages.append(f"Until cond={lab or 'false'} already={pred} bound={bound_of(st)}")
        elif n == 65:
            from .control_runtime import ControlFrame, eval_condition, bound_of
            pred = eval_condition(st, program, lab or "true")
            frame = ControlFrame(id=f"wh{len(st.frames)}", kind="while", condition=lab or "true", status="ready" if pred else "zero")
            st.last_frame = frame.as_dict(); st.frames.append(st.last_frame)
            messages.append(f"While cond={lab or 'true'} already={pred} bound={bound_of(st)}")
        elif n == 66:
            from .control_runtime import ControlFrame
            ids = list(st.selected or _ids(program))
            frame = ControlFrame(id=f"fe{len(st.frames)}", kind="foreach", status="pending", body=list(range(len(ids))))
            st.last_frame = frame.as_dict(); st.frames.append(st.last_frame)
            messages.append(f"ForEach n={len(ids)} op={lab or 'identity'} empty_ok={len(ids)==0}")
        elif 80 <= n <= 99:
            from .spectrum_ops import apply_spectrum
            ok, err = apply_spectrum(n, st, program, lab, term, messages, _ids, shot)
        else:
            ok=False; err=f"unmapped:{n}"; messages.append(f"Core II Dell {n} unmapped")
    except Exception as exc:
        ok=False; err=str(exc); st.last_error=err; messages.append(f"Core II fail {n}: {err}")
    if not ok: st.last_error = err or st.last_error
    mark()
    return {"ok": ok, "error": err, "dell": n, "core_ii": st.snap(), "result": dict(st.last_result or {})}
