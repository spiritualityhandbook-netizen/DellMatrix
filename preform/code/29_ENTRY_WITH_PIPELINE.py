#!/usr/bin/env python3
"""
29_ENTRY_WITH_PIPELINE.py
Composes UnifiedEntry + PipelineQueue.
Status: TRUE
Offline · stdlib only

If 24_UNIFIED_ENTRY loads, wrap it; else minimal stand-in surface + pipeline.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import importlib.util
import os
import sys

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
FLOOR = ("Alpha", "Delta", "Omega", "Omni")


def _load(filename: str, attr: str):
    path = os.path.join(_CODE_DIR, filename)
    try:
        if not os.path.isfile(path):
            return None, "miss"
        name = f"ep_{os.path.splitext(filename)[0]}"
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        if hasattr(mod, attr):
            return getattr(mod, attr), "real"
    except Exception as e:
        return None, f"error:{type(e).__name__}"
    return None, "miss"


PipelineQueue, pq_src = _load("28_PIPELINE_QUEUE.py", "PipelineQueue")
UnifiedEntry, ue_src = _load("24_UNIFIED_ENTRY.py", "UnifiedEntry")

if PipelineQueue is None:
    from dataclasses import dataclass as dc, field as fd

    @dc
    class _Item:
        n: int
        label: str
        confirmed: bool = False

    @dc
    class PipelineQueue:
        items: list = fd(default_factory=list)
        _n: int = 0

        def add(self, label: str):
            self._n += 1
            it = _Item(self._n, label)
            self.items.append(it)
            return it

        def confirm(self, n: int) -> bool:
            for it in self.items:
                if it.n == n:
                    it.confirmed = True
                    return True
            return False

        def pending(self):
            return [i for i in self.items if not i.confirmed]

        def render_lines(self, limit: int = 6):
            if not self.items:
                return ["|     (empty)"]
            return [f"|     {'Y' if i.confirmed else '.'} {i.n}. {i.label}" for i in self.items[-limit:]]

        def status(self):
            return {
                "total": len(self.items),
                "pending": len(self.pending()),
                "confirmed": sum(1 for i in self.items if i.confirmed),
            }

    pq_src = "standin"


@dataclass
class EntryWithPipeline:
    entry: Any = None
    pipeline: Any = field(default=None)
    sources: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.sources = {"unified": ue_src, "pipeline": pq_src}
        self.pipeline = PipelineQueue()
        if UnifiedEntry is not None:
            try:
                self.entry = UnifiedEntry()
            except Exception:
                self.entry = None
        if self.entry is None:
            self.entry = _MiniEntry()

    def boot(self) -> None:
        if hasattr(self.entry, "boot"):
            self.entry.boot()
        self.pipeline.add("Boot complete")

    def command(self, text: str, intent: Optional[Any] = None, **payload) -> Any:
        notes = None
        if hasattr(self.entry, "command"):
            notes = self.entry.command(text, intent=intent, **payload)
        ok = getattr(self.entry, "last_intent_ok", True)
        label = f"{(intent or text or 'NOTE')}"
        if isinstance(label, str) and len(label) > 32:
            label = label[:32]
        self.pipeline.add(f"{label}:{'ok' if ok else 'fail'}")
        return notes

    def pipeline_add(self, label: str):
        return self.pipeline.add(label)

    def pipeline_confirm(self, n: int) -> bool:
        return self.pipeline.confirm(n)

    def pipeline_pending(self):
        return self.pipeline.pending()

    def search_dell(self, q: str):
        if hasattr(self.entry, "search_dell"):
            return self.entry.search_dell(q)
        return []

    def search_flow(self, q: str):
        if hasattr(self.entry, "search_flow"):
            return self.entry.search_flow(q)
        return []

    def tick(self) -> str:
        if hasattr(self.entry, "tick"):
            base = self.entry.tick()
        else:
            base = self.entry.render() if hasattr(self.entry, "render") else ""
        # append pipeline section
        lines = [base.rstrip(), "| [-] PIPELINE", *self.pipeline.render_lines(), "+" + "-" * 44 + "+"]
        return "\n".join(lines)

    def render(self) -> str:
        return self.tick() if False else self._render_only()

    def _render_only(self) -> str:
        base = self.entry.render() if hasattr(self.entry, "render") else ""
        lines = [base.rstrip(), "| [-] PIPELINE", *self.pipeline.render_lines(), "+" + "-" * 44 + "+"]
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        st = self.entry.status() if hasattr(self.entry, "status") else {}
        st = dict(st)
        st["pipeline"] = self.pipeline.status()
        st["sources_pipeline"] = self.sources
        st["floor"] = list(FLOOR)
        return st


class _MiniEntry:
    """Tiny fallback if UnifiedEntry missing."""

    def __init__(self):
        self.last_intent_ok = True
        self.ticks = 0

    def boot(self):
        pass

    def command(self, text, intent=None, **payload):
        self.last_intent_ok = True
        return []

    def tick(self):
        self.ticks += 1
        return self.render()

    def render(self):
        return f"+- MiniEntry tick={self.ticks} -+\n| Floor: {' · '.join(FLOOR)}"

    def status(self):
        return {"ticks": self.ticks, "floor": list(FLOOR)}


def smoke() -> bool:
    print("=== ENTRY WITH PIPELINE SMOKE ===")
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

    ep = EntryWithPipeline()
    run("init", lambda: (ep.pipeline is not None and ep.entry is not None, str(ep.sources)))
    run("boot", lambda: (ep.boot() or True, f"pipe={ep.pipeline.status()}"))
    run("command adds pipe", lambda: (
        (ep.command("pick", intent="PICK") or True)
        and len(ep.pipeline.items) >= 2,
        f"total={ep.pipeline.status()['total']}",
    ))
    run("confirm", lambda: (ep.pipeline_confirm(1), f"pending={len(ep.pipeline_pending())}"))
    run("render pipeline", lambda: ("PIPELINE" in ep._render_only(), "ok"))
    run("floor", lambda: (ep.status().get("floor") == list(FLOOR), str(FLOOR)))
    run("status pipeline", lambda: ("pipeline" in ep.status(), str(ep.status().get("pipeline"))))

    print(f"=== RESULT: {sum(1 for x in results if x)}/{len(results)} PASS ===")
    return all(results)


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    ep = EntryWithPipeline()
    ep.boot()
    ep.command("create and bind")
    print(ep._render_only())
    print("STATUS:", ep.status())
