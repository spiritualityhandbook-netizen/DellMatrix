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
        if n == 51:
            ids = _ids(program); st.selected = [i for i in ids if _pred(lab, i)] or list(ids)
            messages.append(f"Select scope={st.scope} n={len(st.selected)}")
        elif n == 52:
            before = list(st.selected or _ids(program)); st.selected = [i for i in before if _pred(lab, i)]
            messages.append(f"Filter {len(before)}->{len(st.selected)} cond={lab or '*'}")
        elif n == 53:
            st.scope = lab or "plane"; messages.append(f"Scope -> {st.scope}")
        elif n == 54:
            ids = st.selected or _ids(program); messages.append(f"Query scope={st.scope} hits={len(ids)} q={lab or '*'}")
        elif n == 55:
            key,_,val = lab.partition("="); key=(key or "value").strip(); shot(); st.store[key]=val.strip() if val else "1"
            messages.append(f"Set {key}={st.store[key]}")
        elif n == 56:
            key = lab or (list(st.store)[-1] if st.store else ""); messages.append(f"Get {key}={st.store.get(key)!r}")
        elif n == 57:
            parts=[p for p in lab.replace(","," ").split() if p]; a=parts[0] if parts else "a"; b=parts[1] if len(parts)>1 else "b"
            va,vb=st.store.get(a,a),st.store.get(b,b); rel="==" if str(va)==str(vb) else "!="
            messages.append(f"Compare {a}={va!r} {rel} {b}={vb!r}")
        elif n == 58:
            pat=lab.lower(); ids=st.selected or _ids(program)
            st.selected=[i for i in ids if pat in str(i).lower()] if pat else list(ids)
            messages.append(f"Match pattern={pat or '*'} hits={len(st.selected)}")
        elif n == 59:
            st.route = lab or "primary"; messages.append(f"Route -> {st.route}")
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
        elif n == 67:
            ids=st.selected or _ids(program); messages.append(f"Any {any(_pred(lab,i) for i in ids) if ids else False} n={len(ids)}")
        elif n == 68:
            ids=st.selected or _ids(program); messages.append(f"All {all(_pred(lab,i) for i in ids) if ids else True} n={len(ids)}")
        elif n == 69:
            ids=st.selected or _ids(program); messages.append(f"None {not any(_pred(lab,i) for i in ids)} n={len(ids)}")
        elif n == 70:
            ids=st.selected or _ids(program); messages.append(f"Count {len(ids)}")
        elif n == 71: messages.append(f"Measure {lab or 'selected'}={len(st.selected or _ids(program))}")
        elif n == 72: st.limit=lab or "max"; messages.append(f"Limit {st.limit}")
        elif n == 73: messages.append(f"Threshold {lab or 'boundary'}")
        elif n == 74:
            key,_,val=lab.partition("=")
            try: w=float(val) if val else 1.0
            except ValueError: w=1.0
            st.weights[(key or "target").strip()]=w; messages.append(f"Weight {key or 'target'}={w}")
        elif n == 75:
            ssum=sum(st.weights.values()) or 1.0; st.weights={k:v/ssum for k,v in st.weights.items()}
            messages.append(f"Normalize n={len(st.weights)}")
        elif n == 76:
            from .manifest_resolver import resolve_manifest
            try: num=int(lab.split()[0]) if lab[:1].isdigit() else n
            except Exception: num=n
            res=resolve_manifest(num, term, lab)
            messages.append(f"Resolve dell={res.dell} req={res.requested}->{res.resolved} conf={res.confidence:.2f} {res.reason}")
        elif n == 77: messages.append(f"Infer {lab or 'evidence'} PROJECTED_NOT_FACT")
        elif n == 78:
            a,_,b=lab.partition(">"); st.causes.append((a.strip(),b.strip())); messages.append(f"Cause {a.strip() or '?'}->{b.strip() or '?'}")
        elif n == 79:
            a,_,b=lab.partition(">"); st.deps.append((a.strip(),b.strip())); messages.append(f"Depend {a.strip() or '?'} requires {b.strip() or '?'}")
        elif n == 80: st.context=lab or st.scope; messages.append(f"Context -> {st.context}")
        elif n == 81:
            target=lab or (st.selected[0] if st.selected else ""); st.refs[target or "ref"]=target
            messages.append(f"Reference {target or '(none)'}")
        elif n == 82:
            name=lab or "group"; st.groups[name]=list(st.selected or _ids(program)); messages.append(f"Group {name} n={len(st.groups[name])}")
        elif n == 83:
            name=lab or (list(st.groups)[-1] if st.groups else ""); members=st.groups.pop(name, [])
            messages.append(f"Ungroup {name} released={len(members)}")
        elif n == 84:
            src=lab or (st.selected[0] if st.selected else "object"); st.store[f"copy_{src}"]=st.store.get(src, src)
            messages.append(f"Copy {src} original_intact")
        elif n == 85:
            src,_,dest=lab.partition(">"); src,dest=src.strip(),dest.strip()
            if src in st.store and dest: st.store[dest]=st.store.pop(src)
            messages.append(f"Move {src}->{dest or '(none)'} identity_preserved")
        elif n == 86:
            key=lab
            if key in st.store: shot(); st.store.pop(key, None); messages.append(f"Delete store[{key}]")
            elif key in st.groups: shot(); st.groups.pop(key, None); messages.append(f"Delete group[{key}]")
            else: ok=False; err=f"delete_missing:{key or 'empty'}"; messages.append(f"Delete miss {key or '(empty)'}")
        elif n == 87:
            old,_,new=lab.partition(">"); old,new=old.strip(),new.strip(); shot()
            if old in st.store: st.store[new or old]=st.store.pop(old)
            messages.append(f"Replace {old}->{new}")
        elif n == 88:
            key,_,val=lab.partition("="); key=key.strip()
            if key in st.store: shot(); st.store[key]=val; messages.append(f"Patch {key}={val}")
            else: ok=False; err=f"patch_miss:{key}"; messages.append(f"Patch miss {key}")
        elif n == 89:
            st.last_diff={"label":lab,"selected":list(st.selected),"store_keys":list(st.store)}
            messages.append(f"Diff keys={list(st.last_diff)}")
        elif n == 90:
            messages.append(f"Trace last {min(8,len(st.traces))}:")
            for t in st.traces[-8:]: messages.append(f"  · {t}")
            if not st.traces: messages.append("  (empty)")
        elif n == 91:
            passed=bool(st.selected or _ids(program) or st.store or lab=="true")
            if lab.lower() in ("fail","false"): passed=False
            st.last_assert="PASS" if passed else "FAIL"; messages.append(f"Assert {st.last_assert} {lab or 'nonempty'}")
            if not passed: ok=False; err="assert_fail"
        elif n == 92:
            allow=lab.lower() not in ("block","deny","false"); st.last_guard="ALLOW" if allow else "BLOCK"
            messages.append(f"Guard {st.last_guard} {lab or 'default'}")
            if not allow: ok=False; err="guard_block"
        elif n == 93:
            st.try_depth += 1; shot(); messages.append(f"Try depth={st.try_depth} {lab}")
        elif n == 94:
            messages.append(f"Catch {st.last_error or lab or '(no error)'}"); st.last_error=""
        elif n == 95:
            st.staged.append({"op":"commit","label":lab,"snap":st.snap()}); messages.append(f"Commit staged={len(st.staged)}")
        elif n == 96:
            if st.snapshots:
                prev=st.snapshots.pop()
                st.scope=prev.get("scope", st.scope)
                st.store=dict(prev["store"]) if "store" in prev else dict(st.store)
                st.selected=list(prev["selected"]) if "selected" in prev else list(st.selected)
                if st.try_depth: st.try_depth -= 1
                messages.append(f"Revert restored snapshots={len(st.snapshots)}")
            elif st.staged:
                st.staged.pop(); messages.append(f"Revert staged now={len(st.staged)}")
            else: messages.append("Revert nothing")
        elif n == 97:
            name,_,meaning=lab.partition("="); st.defs[(name or "def").strip()]=meaning or lab; messages.append(f"Define {name or 'def'}")
        elif n == 98:
            name,_,target=lab.partition("="); st.aliases[(name or "alias").strip()]=target or lab; messages.append(f"Alias {name or 'alias'}->{target or lab}")
        elif n == 99:
            name,_,body=lab.partition("="); st.compositions[(name or "compose").strip()]=body or lab; messages.append(f"Compose {name or 'compose'}={body or lab}")
        else:
            ok=False; err=f"unmapped:{n}"; messages.append(f"Core II Dell {n} unmapped")
    except Exception as exc:
        ok=False; err=str(exc); st.last_error=err; messages.append(f"Core II fail {n}: {err}")
    if not ok: st.last_error = err or st.last_error
    mark()
    return {"ok": ok, "error": err, "dell": n, "core_ii": st.snap()}
