#!/usr/bin/env python3
"""
Dynamic view switching — smooth, logged, reversible perspective changes.

User/architect can cycle or jump modes at any time.
AI viewers follow assignment unless overridden.

  switch_to(program, 'whole')
  cycle(program)           # first → third → parts → whole → first
  undo(program)
  hotkey(program, '1')     # 1=first 2=third 3=parts 4=whole
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time

from form.dell_matrix.perspective_views import (
    MODES,
    see_as,
    sync_viewer_pose,
    bootstrap_default_viewers,
)

HOTKEYS = {"1": "first", "2": "third", "3": "parts", "4": "whole",
           "f": "first", "t": "third", "p": "parts", "w": "whole"}


@dataclass
class SwitchEvent:
    ts: float
    viewer_id: str
    from_mode: str
    to_mode: str
    by_role: str
    ok: bool
    note: str = ""


@dataclass
class DynamicViewSwitch:
    history: List[SwitchEvent] = field(default_factory=list)
    max_history: int = 64
    active_viewer: str = "user"
    transition_ms: int = 120  # soft handoff marker (UI can animate)

    def _reg(self, program):
        reg = getattr(program, "perspectives", None)
        if reg is None:
            reg = bootstrap_default_viewers(program)
            program.perspectives = reg
        return reg

    def current_mode(self, program, viewer_id: Optional[str] = None) -> str:
        reg = self._reg(program)
        vid = viewer_id or self.active_viewer
        v = reg.viewers.get(vid)
        return v.effective_mode() if v else "first"

    def switch_to(
        self,
        program,
        mode: str,
        *,
        viewer_id: Optional[str] = None,
        as_role: str = "user",
        note: str = "",
    ) -> Dict[str, Any]:
        mode = (mode or "").lower().strip()
        if mode not in MODES:
            return {"ok": False, "error": f"bad mode {mode}", "modes": list(MODES)}
        reg = self._reg(program)
        vid = viewer_id or self.active_viewer
        v = reg.viewers.get(vid)
        if v is None:
            return {"ok": False, "error": f"unknown viewer {vid}"}
        from_mode = v.effective_mode()
        result = reg.set_mode(vid, mode, as_role=as_role)
        ok = bool(result.get("ok"))
        ev = SwitchEvent(
            ts=time.time(),
            viewer_id=vid,
            from_mode=from_mode,
            to_mode=mode,
            by_role=as_role,
            ok=ok,
            note=note or result.get("error", ""),
        )
        self.history.append(ev)
        while len(self.history) > self.max_history:
            self.history.pop(0)
        if not ok:
            return {**result, "event": ev.__dict__}

        sync_viewer_pose(program, v)
        sight = see_as(program, v, mode=mode)
        return {
            "ok": True,
            "viewer": vid,
            "from": from_mode,
            "to": mode,
            "transition_ms": self.transition_ms,
            "sight": {
                "mode": sight.get("mode"),
                "scope": sight.get("scope"),
                "count": sight.get("count") or len((sight.get("vision") or {}).get("nodes") or []),
                "report_head": (sight.get("report") or [])[:5],
            },
            "event": ev.__dict__,
            "law": "user/architect may switch any viewer to any mode",
        }

    def cycle(self, program, *, viewer_id: Optional[str] = None, as_role: str = "user") -> Dict[str, Any]:
        cur = self.current_mode(program, viewer_id)
        try:
            i = MODES.index(cur)  # type: ignore
        except ValueError:
            i = 0
        nxt = MODES[(i + 1) % len(MODES)]
        return self.switch_to(program, nxt, viewer_id=viewer_id, as_role=as_role, note="cycle")

    def undo(self, program, *, as_role: str = "user") -> Dict[str, Any]:
        if len(self.history) < 1:
            return {"ok": False, "error": "no history"}
        last = self.history[-1]
        if not last.ok:
            self.history.pop()
            return self.undo(program, as_role=as_role)
        return self.switch_to(
            program,
            last.from_mode,
            viewer_id=last.viewer_id,
            as_role=as_role,
            note="undo",
        )

    def hotkey(self, program, key: str, *, viewer_id: Optional[str] = None) -> Dict[str, Any]:
        k = (key or "").lower().strip()
        if k == "c":
            return self.cycle(program, viewer_id=viewer_id)
        if k == "u":
            return self.undo(program)
        mode = HOTKEYS.get(k)
        if not mode:
            return {"ok": False, "error": f"unknown hotkey {key}", "hotkeys": HOTKEYS}
        return self.switch_to(program, mode, viewer_id=viewer_id, note=f"hotkey:{k}")

    def status(self, program) -> Dict[str, Any]:
        reg = self._reg(program)
        return {
            "active_viewer": self.active_viewer,
            "current_mode": self.current_mode(program),
            "viewers": reg.list_viewers(),
            "history_len": len(self.history),
            "last": self.history[-1].__dict__ if self.history else None,
            "hotkeys": {"1/f": "first", "2/t": "third", "3/p": "parts", "4/w": "whole", "c": "cycle", "u": "undo"},
        }


SWITCH = DynamicViewSwitch()


def switch_to(program, mode: str, **kwargs) -> Dict[str, Any]:
    return SWITCH.switch_to(program, mode, **kwargs)


def cycle(program, **kwargs) -> Dict[str, Any]:
    return SWITCH.cycle(program, **kwargs)


def undo(program, **kwargs) -> Dict[str, Any]:
    return SWITCH.undo(program, **kwargs)


def hotkey(program, key: str, **kwargs) -> Dict[str, Any]:
    return SWITCH.hotkey(program, key, **kwargs)


def smoke() -> bool:
    print("=== DYNAMIC VIEW SWITCH SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(bool(ok))

    class FakePlane:
        def all_nodes(self):
            return [{"id": "a", "label": "A", "x": 2, "y": 0, "skin": "core"},
                    {"id": "b", "label": "B", "x": 0, "y": 3, "skin": "edge"}]

    class FakeBody:
        pos = (0.0, 0.0)
        class facing:
            name = "E"

    class FakeProg:
        plane = FakePlane()
        avatar = type("A", (), {"body": FakeBody()})()
        perspectives = None

    p = FakeProg()
    s = DynamicViewSwitch()
    a = s.switch_to(p, "third")
    rec("to_third", a.get("ok") is True and a.get("to") == "third")
    b = s.cycle(p)
    rec("cycle", b.get("ok") is True)
    c = s.hotkey(p, "4")
    rec("hotkey_whole", c.get("ok") is True and c.get("to") == "whole")
    d = s.undo(p)
    rec("undo", d.get("ok") is True)
    st = s.status(p)
    rec("status", st.get("current_mode") in MODES)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
