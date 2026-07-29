#!/usr/bin/env python3
"""
28_PIPELINE_QUEUE.py
Code Phase 4 · Pipeline confirm queue
Status: TRUE
Offline · stdlib only

Numbered pipeline items with confirm / pending.
Used by UnifiedEntry composition (29) and available standalone.
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

    def add(self, label: str) -> PipelineItem:
        self._n += 1
        item = PipelineItem(n=self._n, label=label or f"step-{self._n}")
        self.items.append(item)
        return item

    def confirm(self, n: int) -> bool:
        for item in self.items:
            if item.n == n:
                item.confirmed = True
                return True
        return False

    def pending(self) -> List[PipelineItem]:
        return [i for i in self.items if not i.confirmed]

    def clear_confirmed(self) -> int:
        before = len(self.items)
        self.items = [i for i in self.items if not i.confirmed]
        return before - len(self.items)

    def render_lines(self, limit: int = 6) -> List[str]:
        if not self.items:
            return ["|     (empty)"]
        lines = []
        for item in self.items[-limit:]:
            mark = "Y" if item.confirmed else "."
            lines.append(f"|     {mark} {item.n}. {item.label}")
        return lines

    def status(self) -> Dict[str, Any]:
        return {
            "total": len(self.items),
            "pending": len(self.pending()),
            "confirmed": sum(1 for i in self.items if i.confirmed),
            "next_n": self._n + 1,
        }


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
    run("add", lambda: (q.add("Boot complete").n == 1, f"n={q._n}"))
    run("add2", lambda: (q.add("PICK:ok").n == 2, f"pending={len(q.pending())}"))
    run("confirm", lambda: (q.confirm(1) and q.items[0].confirmed, "ok"))
    run("pending", lambda: (len(q.pending()) == 1 and q.pending()[0].n == 2, str(q.status())))
    run("confirm missing", lambda: (q.confirm(99) is False, "ok"))
    run("render", lambda: (len(q.render_lines()) >= 1 and "Boot" in q.render_lines()[0], q.render_lines()[0]))
    run("status", lambda: (q.status()["confirmed"] == 1 and q.status()["pending"] == 1, str(q.status())))

    print(f"=== RESULT: {sum(1 for x in results if x)}/{len(results)} PASS ===")
    return all(results)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
