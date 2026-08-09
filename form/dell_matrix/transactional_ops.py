#!/usr/bin/env python3
"""
Transactional ops — Verse-inspired commit-or-rollback (refined).

Semantics
---------
Two modes:

  deferred (default)
    · stage() only records intent + apply/undo closures
    · commit() runs apply() in order; on apply failure → auto-rollback of
      already-applied steps in reverse, then status=aborted
    · abort() discards staged work (no side effects if nothing was applied)

  eager
    · stage() runs apply() immediately and stores undo snapshot
    · abort() runs undo() in reverse order with a full RollbackReport
    · commit() seals state (undos dropped)

Savepoints: mark() / rollback_to(name) undo only steps after the mark.

Law: all-or-nothing for a closed transaction; partial failure never silent.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import time
import uuid

ApplyFn = Callable[[], Dict[str, Any]]
UndoFn = Callable[[], Dict[str, Any]]


@dataclass
class Staging:
    kind: str
    payload: Dict[str, Any]
    apply: Optional[ApplyFn] = None
    undo: Optional[UndoFn] = None
    applied: bool = False
    apply_result: Optional[Dict[str, Any]] = None
    undo_result: Optional[Dict[str, Any]] = None
    savepoint: Optional[str] = None  # name of savepoint this step sits after


@dataclass
class RollbackStep:
    kind: str
    ok: bool
    detail: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RollbackReport:
    tx_id: str
    steps: List[RollbackStep] = field(default_factory=list)
    clean: bool = True  # every undo ok
    mode: str = "deferred"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tx_id": self.tx_id,
            "clean": self.clean,
            "mode": self.mode,
            "steps": [
                {"kind": s.kind, "ok": s.ok, "detail": s.detail, "payload": s.payload}
                for s in self.steps
            ],
            "undone": sum(1 for s in self.steps if s.ok),
            "failed_undos": sum(1 for s in self.steps if not s.ok),
        }


@dataclass
class Transaction:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    mode: str = "deferred"  # deferred | eager
    staged: List[Staging] = field(default_factory=list)
    savepoints: Dict[str, int] = field(default_factory=dict)  # name → index in staged
    status: str = "open"  # open | committed | aborted
    opened_ts: float = field(default_factory=time.time)
    log: List[str] = field(default_factory=list)
    last_rollback: Optional[RollbackReport] = None

    def _require_open(self) -> None:
        if self.status != "open":
            raise RuntimeError(f"transaction {self.id} is {self.status}")

    def mark(self, name: str) -> str:
        """Savepoint: later rollback_to(name) undoes only steps after this mark."""
        self._require_open()
        name = (name or "").strip() or f"sp_{len(self.savepoints)}"
        self.savepoints[name] = len(self.staged)
        self.log.append(f"savepoint:{name}@{len(self.staged)}")
        return name

    def stage(
        self,
        kind: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        apply: Optional[ApplyFn] = None,
        undo: Optional[UndoFn] = None,
    ) -> Staging:
        self._require_open()
        st = Staging(
            kind=kind,
            payload=dict(payload or {}),
            apply=apply,
            undo=undo,
            savepoint=list(self.savepoints.keys())[-1] if self.savepoints else None,
        )
        if self.mode == "eager" and apply is not None:
            try:
                st.apply_result = apply() or {"ok": True}
                st.applied = True
                self.log.append(f"eager_apply:{kind}:ok")
            except Exception as e:
                st.apply_result = {"ok": False, "error": str(e)}
                st.applied = False
                self.log.append(f"eager_apply:{kind}:FAIL:{e}")
                # auto-rollback everything already applied in this tx
                self._rollback_applied(reason=f"eager_apply_failed:{kind}")
                self.status = "aborted"
                raise RuntimeError(f"eager apply failed for {kind}: {e}") from e
        self.staged.append(st)
        self.log.append(f"stage:{kind}")
        return st

    def _run_undo(self, st: Staging) -> RollbackStep:
        if not st.applied and self.mode == "deferred":
            # never applied — nothing to undo
            return RollbackStep(kind=st.kind, ok=True, detail="not_applied_skip")
        if st.undo is None:
            if st.applied:
                return RollbackStep(
                    kind=st.kind,
                    ok=False,
                    detail="applied_but_no_undo",
                    payload=dict(st.payload),
                )
            return RollbackStep(kind=st.kind, ok=True, detail="no_undo_needed")
        try:
            result = st.undo() or {"ok": True}
            st.undo_result = result
            st.applied = False
            ok = result.get("ok", True) is not False
            return RollbackStep(
                kind=st.kind,
                ok=ok,
                detail=str(result.get("detail") or result.get("error") or "undone"),
                payload=dict(st.payload),
            )
        except Exception as e:
            st.undo_result = {"ok": False, "error": str(e)}
            return RollbackStep(
                kind=st.kind,
                ok=False,
                detail=f"undo_exception:{type(e).__name__}:{e}",
                payload=dict(st.payload),
            )

    def _rollback_applied(self, *, reason: str = "", from_index: int = 0) -> RollbackReport:
        """Undo applied stages in reverse order from end down to from_index."""
        report = RollbackReport(tx_id=self.id, mode=self.mode)
        # reverse walk
        for i in range(len(self.staged) - 1, from_index - 1, -1):
            st = self.staged[i]
            if self.mode == "deferred" and not st.applied:
                report.steps.append(RollbackStep(kind=st.kind, ok=True, detail="deferred_discard"))
                continue
            step = self._run_undo(st)
            report.steps.append(step)
            if not step.ok:
                report.clean = False
                self.log.append(f"undo_fail:{st.kind}:{step.detail}")
            else:
                self.log.append(f"undo_ok:{st.kind}")
        self.log.append(f"rollback:{reason or 'abort'}:clean={report.clean}")
        self.last_rollback = report
        return report

    def rollback_to(self, savepoint: str) -> Dict[str, Any]:
        """Undo only steps after the named savepoint; tx stays open."""
        self._require_open()
        if savepoint not in self.savepoints:
            return {"ok": False, "error": f"unknown savepoint {savepoint}"}
        idx = self.savepoints[savepoint]
        report = self._rollback_applied(reason=f"savepoint:{savepoint}", from_index=idx)
        # drop staged entries after savepoint
        self.staged = self.staged[:idx]
        # drop savepoints that pointed past idx
        self.savepoints = {k: v for k, v in self.savepoints.items() if v <= idx}
        return {"ok": report.clean, "status": "open", "rollback": report.to_dict()}

    def abort(self) -> Dict[str, Any]:
        if self.status != "open":
            return {"ok": False, "status": self.status, "error": "not_open"}
        report = self._rollback_applied(reason="abort", from_index=0)
        self.staged.clear()
        self.savepoints.clear()
        self.status = "aborted"
        self.log.append("aborted")
        return {
            "ok": report.clean,
            "status": "aborted",
            "id": self.id,
            "rollback": report.to_dict(),
            "log": list(self.log),
            "law": "abort · reverse undo · report every step",
        }

    def commit(self) -> Dict[str, Any]:
        self._require_open()
        if self.mode == "deferred":
            # apply in order; on failure rollback applied prefix
            for i, st in enumerate(self.staged):
                if st.apply is None:
                    st.applied = True  # pure note
                    st.apply_result = {"ok": True, "detail": "note_only"}
                    self.log.append(f"commit_note:{st.kind}")
                    continue
                try:
                    st.apply_result = st.apply() or {"ok": True}
                    if st.apply_result.get("ok") is False:
                        raise RuntimeError(st.apply_result.get("error") or "apply returned ok=False")
                    st.applied = True
                    self.log.append(f"commit_apply:{st.kind}:ok")
                except Exception as e:
                    self.log.append(f"commit_apply:{st.kind}:FAIL:{e}")
                    report = self._rollback_applied(reason=f"commit_fail:{st.kind}", from_index=0)
                    self.status = "aborted"
                    return {
                        "ok": False,
                        "status": "aborted",
                        "id": self.id,
                        "failed_at": st.kind,
                        "error": str(e),
                        "rollback": report.to_dict(),
                        "log": list(self.log),
                        "law": "commit failure → full rollback",
                    }
        # eager: already applied; seal
        self.status = "committed"
        # drop undos so they cannot be re-run
        for st in self.staged:
            st.undo = None
        self.log.append("committed")
        return {
            "ok": True,
            "status": "committed",
            "id": self.id,
            "mode": self.mode,
            "effects": [s.kind for s in self.staged],
            "apply_results": [s.apply_result for s in self.staged],
            "log": list(self.log),
            "law": "all-or-nothing · Verse-style transaction",
        }


@dataclass
class TxManager:
    current: Optional[Transaction] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    default_mode: str = "deferred"

    def begin(self, mode: Optional[str] = None) -> Transaction:
        if self.current and self.current.status == "open":
            # nested open not allowed — abort prior
            self.current.abort()
        m = mode or self.default_mode
        if m not in ("deferred", "eager"):
            m = "deferred"
        self.current = Transaction(mode=m)
        return self.current

    def stage_nursery_confirm(self, label: str, words: str = "") -> Dict[str, Any]:
        """Stage nursery add+confirm. Deferred until commit unless eager mode."""
        tx = self.current or self.begin()
        box: Dict[str, Any] = {"label": label, "words": words, "pid": None}

        def apply() -> Dict[str, Any]:
            from form.dell_matrix.nursery import Nursery
            n = Nursery.load()
            p = n.add(label=label, words=words, kind="tx", reason="transactional")
            n.confirm(p.id)
            box["pid"] = p.id
            box["done"] = True
            return {"ok": True, "id": p.id, "detail": "confirmed"}

        def undo() -> Dict[str, Any]:
            pid = box.get("pid")
            if not pid:
                return {"ok": True, "detail": "nothing_to_undo"}
            from form.dell_matrix.nursery import Nursery
            n = Nursery.load()
            if pid in n.proposals:
                n.proposals[pid].status = "rejected"
                n.save()
                return {"ok": True, "detail": f"rejected:{pid}"}
            return {"ok": True, "detail": "pid_missing_already_clean"}

        st = tx.stage("nursery_confirm", box, apply=apply, undo=undo)
        return {
            "staged": True,
            "mode": tx.mode,
            "applied_now": st.applied,
            "label": label,
            "tx": tx.id,
        }

    def stage_view_mode(self, program, viewer_id: str, mode: str) -> Dict[str, Any]:
        tx = self.current or self.begin()
        prev_holder: Dict[str, Any] = {"prev": None}

        def apply() -> Dict[str, Any]:
            reg = getattr(program, "perspectives", None)
            if reg and viewer_id in reg.viewers:
                prev_holder["prev"] = reg.viewers[viewer_id].effective_mode()
            from form.dell_matrix.dynamic_view_switch import switch_to
            out = switch_to(program, mode, viewer_id=viewer_id, as_role="user", note="tx_apply")
            if not out.get("ok"):
                return {"ok": False, "error": out.get("error") or "switch_failed"}
            return {"ok": True, "to": mode, "prev": prev_holder["prev"]}

        def undo() -> Dict[str, Any]:
            prev = prev_holder.get("prev")
            if prev is None:
                return {"ok": True, "detail": "no_prev"}
            from form.dell_matrix.dynamic_view_switch import switch_to
            out = switch_to(program, prev, viewer_id=viewer_id, as_role="user", note="tx_rollback")
            return {"ok": bool(out.get("ok")), "detail": f"restored:{prev}"}

        st = tx.stage(
            "view_mode",
            {"viewer": viewer_id, "mode": mode},
            apply=apply,
            undo=undo,
        )
        return {
            "staged": True,
            "mode": tx.mode,
            "applied_now": st.applied,
            "viewer": viewer_id,
            "target_mode": mode,
            "tx": tx.id,
        }

    def stage_fn(
        self,
        kind: str,
        apply: ApplyFn,
        undo: UndoFn,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Staging:
        tx = self.current or self.begin()
        return tx.stage(kind, payload or {}, apply=apply, undo=undo)

    def mark(self, name: str) -> str:
        tx = self.current or self.begin()
        return tx.mark(name)

    def rollback_to(self, savepoint: str) -> Dict[str, Any]:
        if not self.current:
            return {"ok": False, "error": "no transaction"}
        return self.current.rollback_to(savepoint)

    def commit(self) -> Dict[str, Any]:
        if not self.current:
            return {"ok": False, "error": "no transaction"}
        res = self.current.commit()
        self.history.append(res)
        self.current = None
        return res

    def abort(self) -> Dict[str, Any]:
        if not self.current:
            return {"ok": False, "error": "no transaction"}
        res = self.current.abort()
        self.history.append(res)
        self.current = None
        return res


TX = TxManager()


def smoke() -> bool:
    print("=== TRANSACTIONAL ROLLBACK SMOKE (refined) ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(bool(ok))

    # deferred: abort has no side effects
    m = TxManager(default_mode="deferred")
    state = {"x": 0}

    def apply_x():
        state["x"] = 10
        return {"ok": True}

    def undo_x():
        state["x"] = 0
        return {"ok": True, "detail": "x=0"}

    m.begin("deferred")
    m.stage_fn("set_x", apply_x, undo_x)
    rec("deferred_not_applied_yet", state["x"] == 0)
    c = m.commit()
    rec("deferred_commit", c.get("ok") is True and state["x"] == 10)

    # deferred abort before commit
    state["x"] = 0
    m.begin("deferred")
    m.stage_fn("set_x", apply_x, undo_x)
    a = m.abort()
    rec("deferred_abort_no_effect", a.get("status") == "aborted" and state["x"] == 0)

    # commit failure rolls back prefix
    state["x"] = 0
    state["y"] = 0

    def apply_y_fail():
        state["y"] = 5
        return {"ok": False, "error": "forced_fail"}

    def undo_y():
        state["y"] = 0
        return {"ok": True}

    m.begin("deferred")
    m.stage_fn("set_x", apply_x, undo_x)
    m.stage_fn("set_y", apply_y_fail, undo_y)
    c2 = m.commit()
    rec("commit_fail_aborts", c2.get("ok") is False and c2.get("status") == "aborted")
    rec("prefix_rolled_back", state["x"] == 0)

    # eager + abort undoes
    state["x"] = 0
    m.begin("eager")
    m.stage_fn("set_x", apply_x, undo_x)
    rec("eager_applied", state["x"] == 10)
    a2 = m.abort()
    rec("eager_abort_undo", a2.get("status") == "aborted" and state["x"] == 0)
    rec("rollback_report", isinstance((a2.get("rollback") or {}).get("steps"), list))

    # savepoint
    state["x"] = 0
    state["y"] = 0

    def apply_y_ok():
        state["y"] = 3
        return {"ok": True}

    m.begin("eager")
    m.stage_fn("set_x", apply_x, undo_x)
    m.mark("after_x")
    m.stage_fn("set_y", apply_y_ok, undo_y)
    sp = m.rollback_to("after_x")
    rec("savepoint", sp.get("ok") is True and state["x"] == 10 and state["y"] == 0)
    m.commit()

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
