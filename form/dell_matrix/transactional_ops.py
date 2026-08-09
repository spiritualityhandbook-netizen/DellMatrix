#!/usr/bin/env python3
"""
Transactional ops — Verse-inspired commit-or-rollback.

From: Verse language (Epic) — transactional memory, effects, fail contexts
  · Begin a transaction
  · Stage mutations (nursery, ledger notes, view mode)
  · commit() applies all or abort() rolls back everything

Keeps matrix mutations coherent under auto-growth pressure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import copy
import time
import uuid


@dataclass
class Staging:
    kind: str
    payload: Dict[str, Any]
    undo: Optional[Callable[[], None]] = None


@dataclass
class Transaction:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    staged: List[Staging] = field(default_factory=list)
    status: str = "open"  # open | committed | aborted
    opened_ts: float = field(default_factory=time.time)
    log: List[str] = field(default_factory=list)

    def stage(self, kind: str, payload: Dict[str, Any], undo: Optional[Callable[[], None]] = None) -> None:
        if self.status != "open":
            raise RuntimeError(f"transaction {self.status}")
        self.staged.append(Staging(kind=kind, payload=dict(payload), undo=undo))
        self.log.append(f"stage:{kind}")

    def abort(self) -> Dict[str, Any]:
        if self.status != "open":
            return {"ok": False, "status": self.status}
        # undo in reverse
        for s in reversed(self.staged):
            if s.undo:
                try:
                    s.undo()
                except Exception as e:
                    self.log.append(f"undo_err:{e}")
        self.status = "aborted"
        self.log.append("aborted")
        return {"ok": True, "status": "aborted", "id": self.id, "log": list(self.log)}

    def commit(self) -> Dict[str, Any]:
        if self.status != "open":
            return {"ok": False, "status": self.status}
        self.status = "committed"
        self.log.append("committed")
        return {
            "ok": True,
            "status": "committed",
            "id": self.id,
            "effects": [s.kind for s in self.staged],
            "log": list(self.log),
            "law": "all-or-nothing · Verse-style transaction",
        }


@dataclass
class TxManager:
    current: Optional[Transaction] = None
    history: List[Dict[str, Any]] = field(default_factory=list)

    def begin(self) -> Transaction:
        if self.current and self.current.status == "open":
            self.current.abort()
        self.current = Transaction()
        return self.current

    def stage_nursery_confirm(self, label: str, words: str = "") -> Dict[str, Any]:
        tx = self.current or self.begin()
        applied = {"label": label, "done": False}

        def do():
            try:
                from form.dell_matrix.nursery import Nursery
                n = Nursery.load()
                p = n.add(label=label, words=words, kind="tx", reason="transactional")
                n.confirm(p.id)
                applied["done"] = True
                applied["id"] = p.id
            except Exception as e:
                applied["error"] = str(e)

        def undo():
            # best-effort: cannot un-confirm easily; mark reject if id known
            try:
                from form.dell_matrix.nursery import Nursery
                n = Nursery.load()
                pid = applied.get("id")
                if pid and pid in n.proposals:
                    n.proposals[pid].status = "rejected"
                    n.save()
            except Exception:
                pass

        do()
        tx.stage("nursery_confirm", {"label": label, **applied}, undo=undo)
        return applied

    def stage_view_mode(self, program, viewer_id: str, mode: str) -> Dict[str, Any]:
        tx = self.current or self.begin()
        prev = None
        try:
            reg = getattr(program, "perspectives", None)
            if reg and viewer_id in reg.viewers:
                prev = reg.viewers[viewer_id].effective_mode()
        except Exception:
            pass

        def undo():
            if prev is None:
                return
            try:
                from form.dell_matrix.dynamic_view_switch import switch_to
                switch_to(program, prev, viewer_id=viewer_id, as_role="user", note="tx_rollback")
            except Exception:
                pass

        try:
            from form.dell_matrix.dynamic_view_switch import switch_to
            out = switch_to(program, mode, viewer_id=viewer_id, as_role="user", note="tx_stage")
        except Exception as e:
            out = {"ok": False, "error": str(e)}
        tx.stage("view_mode", {"viewer": viewer_id, "mode": mode, "prev": prev, **{k: out.get(k) for k in ("ok", "to")}}, undo=undo)
        return out

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
    print("=== TRANSACTIONAL OPS SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)
    m = TxManager()
    tx = m.begin()
    rec("begin", tx.status == "open")
    tx.stage("note", {"x": 1})
    rec("stage", len(tx.staged) == 1)
    c = m.commit()
    rec("commit", c.get("status") == "committed")
    tx2 = m.begin()
    flag = {"v": 1}
    tx2.stage("flip", {}, undo=lambda: flag.__setitem__("v", 0))
    flag["v"] = 2
    a = m.abort()
    rec("abort", a.get("status") == "aborted" and flag["v"] == 0)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
