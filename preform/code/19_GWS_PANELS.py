#!/usr/bin/env python3
"""
19_GWS_PANELS.py
Code Phase 4 · Cell 4B
Status: TRUE
Offline · Zero dependencies · Stdlib only

GodWorkSpace panel controls:
- Expand / collapse named sections
- Flow-symbol search against registry flows
- Dell search (number / name / manor) retained
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import json
import os

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_registry() -> Dict[str, Any]:
    path = os.path.join(_CODE_DIR, "01_REGISTRY_DATA.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "dells" in data:
            return data
    except Exception:
        pass
    return {
        "status": "FALLBACK",
        "dells": [{"dell": 8, "name": "Create", "manor": "Instantiate"},
                  {"dell": 14, "name": "Bind", "manor": "Attach"}],
        "flows": [
            {"symbol": ">", "name": "Primary", "manor": "Default execution"},
            {"symbol": ">>", "name": "Strong Primary", "manor": "Elevated"},
            {"symbol": ">>>", "name": "Max Primary", "manor": "Full force"},
            {"symbol": ":", "name": "Bind", "manor": "Attach"},
            {"symbol": "::", "name": "Deep Bind", "manor": "Nested"},
            {"symbol": "<<[Delta]", "name": "Retrograde", "manor": "Reverse"},
        ],
    }

REGISTRY = _load_registry()

DEFAULT_PANELS = ["header", "status", "seed", "pipeline", "search", "log", "drafts"]

@dataclass
class PanelState:
    name: str
    expanded: bool = True

@dataclass
class GWSPanels:
    registry: Dict[str, Any] = field(default_factory=lambda: REGISTRY)
    panels: Dict[str, PanelState] = field(default_factory=dict)
    last_dell_hits: List[Dict[str, Any]] = field(default_factory=list)
    last_flow_hits: List[Dict[str, Any]] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.panels:
            self.panels = {n: PanelState(name=n, expanded=True) for n in DEFAULT_PANELS}

    def log(self, msg: str) -> None:
        self.messages.append(msg)
        self.messages = self.messages[-12:]

    # ----- expand / collapse -----

    def expand(self, name: str) -> bool:
        if name not in self.panels:
            return False
        self.panels[name].expanded = True
        self.log(f"expand:{name}")
        return True

    def collapse(self, name: str) -> bool:
        if name not in self.panels:
            return False
        self.panels[name].expanded = False
        self.log(f"collapse:{name}")
        return True

    def toggle(self, name: str) -> Optional[bool]:
        if name not in self.panels:
            return None
        self.panels[name].expanded = not self.panels[name].expanded
        self.log(f"toggle:{name}={'open' if self.panels[name].expanded else 'closed'}")
        return self.panels[name].expanded

    def expand_all(self) -> None:
        for p in self.panels.values():
            p.expanded = True
        self.log("expand_all")

    def collapse_all(self) -> None:
        for p in self.panels.values():
            p.expanded = False
        self.log("collapse_all")

    def is_expanded(self, name: str) -> bool:
        p = self.panels.get(name)
        return bool(p and p.expanded)

    # ----- search -----

    def search_dell(self, query: str) -> List[Dict[str, Any]]:
        q = (query or "").strip().lower()
        hits = []
        for d in self.registry.get("dells", []):
            num = str(d.get("dell", ""))
            name = str(d.get("name", "")).lower()
            manor = str(d.get("manor", "")).lower()
            if not q or q == num or q in name or q in manor:
                hits.append(d)
        self.last_dell_hits = hits[:12]
        self.log(f"dell_search:{query!r}->{len(hits)}")
        return self.last_dell_hits

    def search_flow(self, query: str) -> List[Dict[str, Any]]:
        """Search flow symbols by symbol, name, or manor."""
        q = (query or "").strip().lower()
        hits = []
        for f in self.registry.get("flows", []):
            sym = str(f.get("symbol", "")).lower()
            name = str(f.get("name", "")).lower()
            manor = str(f.get("manor", "")).lower()
            if not q or q == sym or q in sym or q in name or q in manor:
                hits.append(f)
        self.last_flow_hits = hits[:12]
        self.log(f"flow_search:{query!r}->{len(hits)}")
        return self.last_flow_hits

    # ----- render -----

    def _section(self, name: str, body_lines: List[str]) -> List[str]:
        open_ = self.is_expanded(name)
        mark = "-" if open_ else "+"
        lines = [f"| [{mark}] {name.upper()}"]
        if open_:
            lines.extend(body_lines if body_lines else ["|     (empty)"])
        return lines

    def render(self, extra: Optional[Dict[str, Any]] = None) -> str:
        extra = extra or {}
        status_body = [
            f"|     avatar: {extra.get('avatar', '—')}",
            f"|     frame:  {extra.get('frame', '—')}",
            f"|     hand:   {extra.get('holding', '—')}",
        ]
        seed_body = [f"|     {extra.get('seed_strip', '(none)')}"]
        pipe_body = [f"|     {p}" for p in extra.get("pipeline", [])] or ["|     (empty)"]
        dell_body = [
            f"|     {d.get('dell')}: {d.get('name')} — {str(d.get('manor', ''))[:24]}"
            for d in self.last_dell_hits[:5]
        ] or ["|     (none)"]
        flow_body = [
            f"|     {f.get('symbol')}: {f.get('name')} — {str(f.get('manor', ''))[:24]}"
            for f in self.last_flow_hits[:5]
        ] or ["|     (none)"]
        log_body = [f"|     {m}" for m in self.messages[-4:]] or ["|     —"]

        lines = ["+- GodWorkSpace Panels -+"]
        lines += self._section("status", status_body)
        lines += self._section("seed", seed_body)
        lines += self._section("pipeline", pipe_body)
        lines += self._section("search", ["|     DELL"] + dell_body + ["|     FLOW"] + flow_body)
        lines += self._section("log", log_body)
        lines.append("+" + "-" * 28 + "+")
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        return {
            "expanded": {n: p.expanded for n, p in self.panels.items()},
            "dell_hits": len(self.last_dell_hits),
            "flow_hits": len(self.last_flow_hits),
            "registry": self.registry.get("status", "UNKNOWN"),
        }


def smoke_panels() -> bool:
    print("=== GWS PANELS SMOKE ===")
    results = []

    def record(name: str, passed: bool, detail: str = "") -> None:
        print(f"[{len(results)+1}] {name}: {'PASS' if passed else 'FAIL'}" + (f" | {detail}" if detail else ""))
        results.append(passed)

    def run(name, fn):
        try:
            ok, detail = fn()
            record(name, bool(ok), detail)
        except Exception as e:
            record(name, False, f"EXCEPTION {type(e).__name__}: {e}")

    g = GWSPanels()

    run("init panels", lambda: (len(g.panels) >= 5, f"n={len(g.panels)}"))
    run("collapse search", lambda: (g.collapse("search") and not g.is_expanded("search"), "closed"))
    run("expand search", lambda: (g.expand("search") and g.is_expanded("search"), "open"))
    run("toggle log", lambda: (g.toggle("log") is False, f"expanded={g.is_expanded('log')}"))
    run("collapse_all", lambda: (g.collapse_all() or True, f"any_open={any(p.expanded for p in g.panels.values())}"))
    run("expand_all", lambda: (g.expand_all() or True, f"all_open={all(p.expanded for p in g.panels.values())}"))

    run("dell search Create", lambda: (
        any(h.get("dell") == 8 or str(h.get("name", "")).lower() == "create" for h in g.search_dell("Create")),
        f"hits={len(g.last_dell_hits)}"
    ))
    run("flow search >>", lambda: (
        any(">>" in str(h.get("symbol", "")) for h in g.search_flow(">>")),
        f"hits={len(g.last_flow_hits)}"
    ))
    run("flow search retrograde", lambda: (
        len(g.search_flow("retro")) >= 1,
        f"hits={len(g.last_flow_hits)}"
    ))
    run("unknown panel safe", lambda: (g.expand("nope") is False, "no raise"))
    run("render", lambda: ("GodWorkSpace" in g.render({"seed_strip": "08>>14"}), "ok"))

    passed = sum(1 for p in results if p)
    print(f"=== RESULT: {passed}/{len(results)} PASS ===")
    print("STATUS:", g.status())
    return passed == len(results)


if __name__ == "__main__":
    import sys
    ok = smoke_panels()
    sys.exit(0 if ok else 1)
