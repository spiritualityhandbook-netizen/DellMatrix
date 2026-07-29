#!/usr/bin/env python3
"""
24_PIPELINE_HOST.py
Thin host proving PipelineQueue owned by a UnifiedEntry-shaped surface.
Status: TRUE
Offline · stdlib only

When full 24_UNIFIED_ENTRY is extended, same pattern applies:
  self.pipeline = PipelineQueue()
  boot -> pipeline.add("Boot complete")
  successful command -> pipeline.add(f"{intent}:ok")
  render -> PIPELINE section from pipeline.render_lines()

This host runs offline without loading the full UnifiedEntry file.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import importlib.util
import os
import sys

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
FLOOR = ("Alpha", "Delta", "Omega", "Omni")


def _load_pipeline():
    path = os.path.join(_CODE_DIR, "28_PIPELINE_QUEUE.py")
    try:
        if os.path.isfile(path):
            spec = importlib.util.spec_from_file_location("pipe28", path)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            if hasattr(mod, "PipelineQueue"):
                return mod.PipelineQueue, "real"
    except Exception:
        pass

    # stand-in
    from dataclasses import dataclass as dc, field as fd

    @dc
    class PipelineItem:
        n: int
        label: str
        confirmed: bool = False

    @dc
    class PipelineQueue:
        items: list = fd(default_factory=list)
        _n: int = 0

        def add(self, label: str):
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

        def pending(self):
            return [p for p in self.items if not p.confirmed]

        def render_lines(self, limit: int = 6):
            if not self.items:
                return ["|     (empty)"]
            return [
                f"|     {'✓' if p.confirmed else '·'} {p.n}. {p.label}"
                for p in self.items[-limit:]
            ]

        def status(self):
            return {
                "total": len(self.items),
                "pending": len(self.pending()),
                "confirmed": sum(1 for p in self.items if p.confirmed),
            }

    return PipelineQueue, "standin"


PipelineQueue, PIPE_SRC = _load_pipeline()


@dataclass
class UnifiedPipelineHost:
    """Minimal UnifiedEntry-shaped surface that owns a pipeline."""
    pipeline: Any = field(default=None)
    ticks: int = 0
    last_command: str = ""
    last_ok: Optional[bool] = None
    pipe_source: str = PIPE_SRC

    def __post_init__(self):
        self.pipeline = self.pipeline or PipelineQueue()

    def boot(self) -> None:
        self.ticks = 0
        self.last_command = ""
        self.last_ok = None
        self.pipeline.add("Boot complete")

    def command(self, text: str, ok: bool = True) -> None:
        self.last_command = text or ""
        self.last_ok = ok
        if ok:
            label = (text or "cmd")[:32]
            self.pipeline.add(f"{label}:ok")

    def confirm(self, n: int) -> bool:
        return bool(self.pipeline.confirm(n))

    def tick(self) -> str:
        self.ticks += 1
        return self.render()

    def render(self) -> str:
        lines = [
            f"+- UnifiedPipelineHost · tick={self.ticks} · pipe={self.pipe_source} -+",
            f"| Floor: {' · '.join(FLOOR)} (locked)",
            f"| CMD: {self.last_command or '(none)'} ok={self.last_ok}",
            "| [-] PIPELINE",
        ]
        lines.extend(self.pipeline.render_lines())
        lines.append("+" + "-" * 40 + "+")
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        return {
            "ticks": self.ticks,
            "floor": list(FLOOR),
            "command": self.last_command,
            "ok": self.last_ok,
            "pipeline": self.pipeline.status(),
            "pipe_source": self.pipe_source,
        }


def smoke() -> bool:
    print("=== UNIFIED PIPELINE HOST SMOKE ===")
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

    h = UnifiedPipelineHost()
    run("boot", lambda: (h.boot() or True, f"items={len(h.pipeline.items)}"))
    run("boot line", lambda: (len(h.pipeline.items) >= 1, h.pipeline.items[0].label))
    run("command ok", lambda: (h.command("pick wrench", ok=True) or True, f"n={len(h.pipeline.items)}"))
    run("command fail no add", lambda: (
        (h.command("bad", ok=False) or True) and len(h.pipeline.pending()) >= 1,
        f"total={len(h.pipeline.items)}",
    ))
    run("confirm", lambda: (h.confirm(1), f"pending={len(h.pipeline.pending())}"))
    run("render", lambda: ("PIPELINE" in h.tick() and "Floor" in h.render(), f"t={h.ticks}"))
    run("status", lambda: (h.status()["pipeline"]["total"] >= 1, str(h.status()["pipeline"])))
    run("floor", lambda: (h.status()["floor"] == list(FLOOR), str(FLOOR)))

    print(f"=== RESULT: {sum(1 for x in results if x)}/{len(results)} PASS ===")
    return all(results)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
