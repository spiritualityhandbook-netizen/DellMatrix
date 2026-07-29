#!/usr/bin/env python3
"""
28_PIPELINE_QUEUE.py
Code Phase 4 · Pipeline confirm queue
Status: TRUE
Offline · stdlib only

Numbered pipeline items with confirm.
UnifiedEntry (or any host) can own a PipelineQueue and render it.

API:
  add(label) -> PipelineItem
  confirm(n) -> bool
  pending() -> list
  render_lines() -> list[str]
  status() -> dict

Run:
  python preform/code/28_PIPELINE_QUEUE.py
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class PipelineItem:
    n: int
    label: str
    confirmed: bool = False


@dataclass
class PipelineQueue:
    items: List[PipelineItem] = field(default_factory=list)
    _n: int = 0
    auto_log: List[str] = field(default_factory=list)

    def add(self, label: str) -> PipelineItem:
        self._n += 1
        item = PipelineItem(n=self._n, label=label or f"step-{self._n}")
        self.items.append(item)
        self.auto_log.append(f"pipe+{item.n}:{item.label}")
        self.auto_log = self.auto_log[-20:]
        return item

    def confirm(self, n: int) -> bool:
        for item in self.items:
            if item.n == n:
                item.confirmed = True
                self.auto_log.append(f"pipe✓{n}")
                self.auto_log = self.auto_log[-20:]
                return True
        return False

    def pending(self) -> List[PipelineItem]:
        return [p for p in self.items if not p.confirmed]

    def confirmed_items(self) -> List[PipelineItem]:
        return [p for p in self.items if p.confirmed]

    def clear_confirmed(self) -> int:
        before = len(self.items)
        self.items = [p for p in self.items if not p.confirmed]
        return before - len(self.items)

    def render_lines(self, limit: int = 6) -> List[str]:
        if not self.items:
            return ["|     (empty)"]
        lines = []
        for p in self.items[-limit:]:
            mark = "✓" if p.confirmed else "·"
            lines.append(f"|     {mark} {p.n}. {p.label}")
        return lines

    def status(self) -> Dict[str, Any]:
        return {
            "total": len(self.items),
            "pending": len(self.pending()),
            "confirmed": len(self.confirmed_items()),
            "next_n": self._n + 1,
        }


def attach_to_command_result(
    queue: PipelineQueue,
    label: str,
    ok: Optional[bool],
) -> Optional[PipelineItem]:
    """Helper: add a pipeline line when a command succeeds."""
    if ok:
        return queue.add(label)
    return None


def smoke() -> bool:
    print("=== PIPELINE QUEUE SMOKE ===")
    results: List[bool] = []

    def record(name: str, passed: bool, detail: str = "") -> None:
        print(f"[{len(results)+1}] {name}: {'PASS' if passed else 'FAIL'}" + (f" | {detail}" if detail else ""))
        results.append(bool(passed))

    def run(name, fn):
        try:
            ok, detail = fn()
            record(name, bool(ok), detail)
        except Exception as e:
            record(name, False, f"EXCEPTION {type(e).__name__}: {e}")

    q = PipelineQueue()
    run("add", lambda: (q.add("Boot complete").n == 1, f"n={q.items[0].n}"))
    run("add2", lambda: (q.add("PICK:ok").n == 2, f"total={len(q.items)}"))
    run("pending", lambda: (len(q.pending()) == 2, f"p={len(q.pending())}"))
    run("confirm 1", lambda: (q.confirm(1) and q.items[0].confirmed, "ok"))
    run("pending after", lambda: (len(q.pending()) == 1, f"p={len(q.pending())}"))
    run("confirm missing", lambda: (q.confirm(99) is False, "ok"))
    run("render", lambda: (any("Boot" in line for line in q.render_lines()), str(q.render_lines())))
    run("attach helper", lambda: (
        attach_to_command_result(q, "STOW:ok", True) is not None and len(q.items) == 3,
        f"total={len(q.items)}",
    ))
    run("status", lambda: (q.status()["pending"] >= 1 and q.status()["confirmed"] >= 1, str(q.status())))
    run("clear_confirmed", lambda: (q.clear_confirmed() >= 1, f"left={len(q.items)}"))

    print(f"=== RESULT: {sum(1 for x in results if x)}/{len(results)} PASS ===")
    return all(results)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
