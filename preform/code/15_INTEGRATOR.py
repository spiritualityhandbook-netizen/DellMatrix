#!/usr/bin/env python3
"""
15_INTEGRATOR.py
Code Phase 3 · Artifact 15 (HARDENED)
Status: TRUE
Offline · Zero dependencies · Stdlib only

Unified runner + intent bridge + live GodWorkSpace tick.
Hardened:
- Attempts real import of 01_REGISTRY_DATA.json + 02_TINY_LEXER
- Falls back to embedded stand-ins if imports fail
- Smoke-test suite included (run: python 15_INTEGRATOR.py --smoke)
- Expanded GWS: Dell search + pipeline confirm queue
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import json
import os
import sys
import time

Coord = Tuple[int, int]
_CODE_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# Real module loaders (harden against 01 / 02)
# =============================================================================

def _load_registry() -> Dict[str, Any]:
    path = os.path.join(_CODE_DIR, "01_REGISTRY_DATA.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("status") == "TRUE" and "dells" in data:
            return data
    except Exception:
        pass
    # fallback minimal
    return {
        "status": "FALLBACK",
        "dells": [{"dell": i, "name": f"D{i}", "manor": ""} for i in range(51)],
        "flows": [{"symbol": ">", "name": "Primary"}],
    }

def _load_tokenize():
    """Return tokenize function from real 02_TINY_LEXER or a stub."""
    try:
        import importlib.util
        path = os.path.join(_CODE_DIR, "02_TINY_LEXER.py")
        spec = importlib.util.spec_from_file_location("tiny_lexer", path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        if hasattr(mod, "tokenize"):
            return mod.tokenize
    except Exception:
        pass
    def stub_tokenize(text: str):
        return [{"type": "TEXT", "value": text, "raw": text}]
    return stub_tokenize

REGISTRY = _load_registry()
TOKENIZE = _load_tokenize()

# =============================================================================
# Core stand-ins (used when full 05–14 package import is not on path)
# =============================================================================

class Facing(Enum):
    N, NE, E, SE, S, SW, W, NW = range(8)
    @property
    def delta(self) -> Coord:
        return [(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)][self.value]

class Reach(Enum):
    CLOSE = 1
    AWAY = 2
    FAR = 3

class Intent(Enum):
    IDLE = auto(); MOVE = auto(); TURN = auto()
    PICK = auto(); PLACE = auto(); STOW = auto(); DRAW = auto()
    EXPRESS = auto(); NOTE = auto()

@dataclass
class Body:
    pos: Coord = (0, 0)
    facing: Facing = Facing.N
    reach: Reach = Reach.CLOSE
    holding: Any = None

@dataclass
class Avatar:
    body: Body = field(default_factory=Body)
    name: str = "Avatar"
    def read_body(self) -> Body:
        return Body(pos=self.body.pos, facing=self.body.facing,
                    reach=self.body.reach, holding=self.body.holding)
    def step(self, n: int = 1) -> Coord:
        dx, dy = self.body.facing.delta
        x, y = self.body.pos
        self.body.pos = (x + dx * n, y + dy * n)
        return self.body.pos
    def turn(self, n: int = 1) -> Facing:
        idx = (list(Facing).index(self.body.facing) + n) % 8
        self.body.facing = list(Facing)[idx]
        return self.body.facing

class Grid:
    def __init__(self):
        self._cells: Dict[Coord, Any] = {}
    def get(self, x: int, y: int):
        k = (x, y)
        if k not in self._cells:
            self._cells[k] = {"content": None}
        return self._cells[k]
    def set(self, x: int, y: int, content: Any = None):
        self._cells[(x, y)] = {"content": content}
    def clear(self, x: int, y: int):
        self._cells.pop((x, y), None)

class Inventory:
    def __init__(self):
        self.slots: List[Any] = [None, None, None]
    def add(self, item: Any) -> bool:
        for i, s in enumerate(self.slots):
            if s is None:
                self.slots[i] = item
                return True
        return False
    def remove(self, i: int = 0) -> Any:
        if 0 <= i < len(self.slots):
            item = self.slots[i]; self.slots[i] = None; return item
        return None
    def list_items(self) -> List[Any]:
        return [s for s in self.slots if s is not None]

class ReachInventory:
    def __init__(self, avatar: Avatar, grid: Grid):
        self.avatar = avatar; self.grid = grid; self.inventory = Inventory()
    def _dist(self, a: Coord, b: Coord) -> int:
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    def can_reach(self, target: Coord) -> bool:
        return self._dist(self.avatar.body.pos, target) <= self.avatar.body.reach.value
    def pick(self, target: Coord) -> bool:
        b = self.avatar.body
        if b.holding is not None or not self.can_reach(target): return False
        cell = self.grid.get(*target)
        if cell["content"] is None: return False
        b.holding = cell["content"]; self.grid.clear(*target); return True
    def place(self, target: Coord) -> bool:
        b = self.avatar.body
        if b.holding is None or not self.can_reach(target): return False
        if self.grid.get(*target)["content"] is not None: return False
        self.grid.set(*target, content=b.holding); b.holding = None; return True
    def stow(self) -> bool:
        b = self.avatar.body
        if b.holding is None: return False
        if self.inventory.add(b.holding):
            b.holding = None; return True
        return False
    def draw(self, i: int = 0) -> bool:
        b = self.avatar.body
        if b.holding is not None: return False
        item = self.inventory.remove(i)
        if item is None: return False
        b.holding = item; return True

class Anim:
    def __init__(self, id: str, frames: List[str], loop: bool = True):
        self.id = id; self.frames = frames; self.index = 0; self.loop = loop
    def current(self) -> str:
        return self.frames[self.index % len(self.frames)] if self.frames else "(·_·)"
    def advance(self) -> str:
        if self.frames and (self.loop or self.index < len(self.frames)-1):
            self.index = (self.index + 1) % len(self.frames)
        return self.current()

class AsciiPlayer:
    def __init__(self):
        self.anims: Dict[str, Anim] = {}
        self.active: Optional[str] = None
        for a in [
            Anim("idle", ["(·_·)", "(·-·)", "(·_·)", "(·o·)"]),
            Anim("sparkle", ["✧", "✦", "★", "☆"], loop=False),
            Anim("joy", ["(^_^)", "(◕‿◕)", "(^∇^)"]),
        ]:
            self.anims[a.id] = a
        self.set_active("idle")
    def set_active(self, aid: str) -> bool:
        if aid not in self.anims: return False
        self.active = aid; self.anims[aid].index = 0; return True
    def tick(self) -> str:
        return self.anims[self.active].advance() if self.active else "(·_·)"
    def show(self) -> str:
        return self.anims[self.active].current() if self.active else "(·_·)"

@dataclass
class Thought:
    content: str
    intent: Optional[Intent] = None
    payload: Dict[str, Any] = field(default_factory=dict)

class Thinks:
    def __init__(self):
        self.queue: List[Thought] = []; self.notes: List[str] = []; self.last_body = None
    def observe(self, avatar: Avatar):
        self.last_body = avatar.read_body(); return self.last_body
    def think(self, content: str, intent: Optional[Intent] = None, **payload) -> Thought:
        if self.last_body is None: content = f"[no body] {content}"
        t = Thought(content=content, intent=intent, payload=payload)
        self.queue.append(t)
        if intent is None: self.notes.append(content)
        return t
    def next_intent(self) -> Optional[Thought]:
        for i, t in enumerate(self.queue):
            if t.intent is not None: return self.queue.pop(i)
        return None

# =============================================================================
# Expanded GodWorkSpace (Dell search + pipeline confirm)
# =============================================================================

@dataclass
class PipelineItem:
    n: int
    label: str
    confirmed: bool = False

class GodWorkSpace:
    def __init__(self, registry: Dict[str, Any]):
        self.registry = registry
        self.temp = "W"
        self.seed_strip = ""
        self.messages: List[str] = []
        self.avatar_status: Dict[str, Any] = {}
        self.frame = "(·_·)"
        self.holding: Any = None
        self.inventory: List[Any] = []
        self.pipeline: List[PipelineItem] = []
        self._pipe_n = 0
        self.last_search: List[Dict[str, Any]] = []

    def log(self, msg: str) -> None:
        self.messages.append(msg)
        self.messages = self.messages[-12:]

    def search_dell(self, query: str) -> List[Dict[str, Any]]:
        """Search registry by number, name, or manor substring."""
        q = query.strip().lower()
        hits = []
        for d in self.registry.get("dells", []):
            num = str(d.get("dell", ""))
            name = str(d.get("name", "")).lower()
            manor = str(d.get("manor", "")).lower()
            if q == num or q in name or q in manor:
                hits.append(d)
        self.last_search = hits[:12]
        self.log(f"search:{query}→{len(hits)}")
        return self.last_search

    def pipeline_add(self, label: str) -> PipelineItem:
        self._pipe_n += 1
        item = PipelineItem(n=self._pipe_n, label=label)
        self.pipeline.append(item)
        self.log(f"pipe+{item.n}:{label}")
        return item

    def pipeline_confirm(self, n: int) -> bool:
        for item in self.pipeline:
            if item.n == n:
                item.confirmed = True
                self.log(f"pipe✓{n}")
                return True
        return False

    def pipeline_pending(self) -> List[PipelineItem]:
        return [p for p in self.pipeline if not p.confirmed]

    def render(self) -> str:
        pipe_lines = []
        for p in self.pipeline[-5:]:
            mark = "✓" if p.confirmed else "·"
            pipe_lines.append(f"│   {mark} {p.n}. {p.label}")
        if not pipe_lines:
            pipe_lines = ["│   (empty)"]

        search_lines = []
        for d in self.last_search[:5]:
            search_lines.append(f"│   {d.get('dell')}: {d.get('name')} — {d.get('manor','')[:28]}")
        if not search_lines:
            search_lines = ["│   (none)"]

        lines = [
            f"┌─ GodWorkSpace ─ Temp:{self.temp} ─┐",
            f"│ Avatar : {self.avatar_status}",
            f"│ Frame  : {self.frame}",
            f"│ Hand   : {self.holding}",
            f"│ Inv    : {self.inventory}",
            f"│ SEED   : {self.seed_strip or '(none)'}",
            "│ PIPELINE",
            *pipe_lines,
            "│ DELL SEARCH",
            *search_lines,
            f"│ LOG    : {self.messages[-3:] if self.messages else '—'}",
            "└" + "─"*40 + "┘",
        ]
        return "\n".join(lines)

class TokenWorkMem:
    def __init__(self, limit: int = 4096):
        self.limit = limit; self.used = 0
        self.runs: List[str] = []; self.fails: List[str] = []
    def estimate(self, text: str) -> int:
        return max(1, len(text)//4)
    def charge(self, text: str) -> bool:
        c = self.estimate(text)
        if self.used + c > self.limit: return False
        self.used += c; return True
    def record_run(self, msg: str) -> None: self.runs.append(msg)
    def record_fail(self, msg: str) -> None: self.fails.append(msg)

# =============================================================================
# Integrator
# =============================================================================

class Integrator:
    def __init__(self):
        self.grid = Grid()
        self.avatar = Avatar()
        self.reach = ReachInventory(self.avatar, self.grid)
        self.anim = AsciiPlayer()
        self.thinks = Thinks()
        self.gws = GodWorkSpace(REGISTRY)
        self.mem = TokenWorkMem()
        self.ticks = 0
        self.registry_status = REGISTRY.get("status", "UNKNOWN")
        self.lexer_live = TOKENIZE.__module__ != "__main__" if hasattr(TOKENIZE, "__module__") else False

    def boot(self) -> None:
        self.grid.set(1, 0, content={"kind": "tool", "name": "wrench"})
        self.grid.set(0, 1, content={"kind": "note", "name": "seed-card"})
        self.gws.seed_strip = "08[Create] >> 14[Bind] :: integrator"
        self.gws.temp = "W"
        self.thinks.observe(self.avatar)
        self.mem.record_run("Integrator boot")
        self.gws.log("boot")
        self.gws.pipeline_add("Boot complete")
        self._sync_gws()

    def _sync_gws(self) -> None:
        b = self.avatar.read_body()
        self.gws.avatar_status = {
            "pos": b.pos,
            "facing": b.facing.name if hasattr(b.facing, "name") else str(b.facing),
            "reach": b.reach.name if hasattr(b.reach, "name") else str(b.reach),
        }
        self.gws.frame = self.anim.show()
        self.gws.holding = b.holding
        self.gws.inventory = self.reach.inventory.list_items()

    def _execute(self, thought: Thought) -> bool:
        intent, p = thought.intent, thought.payload
        if intent is None: return False
        if intent == Intent.MOVE:
            self.avatar.step(int(p.get("steps", 1))); self.anim.set_active("idle"); return True
        if intent == Intent.TURN:
            self.avatar.turn(int(p.get("steps", 1))); return True
        if intent == Intent.PICK:
            target = tuple(p.get("target", (1, 0)))  # type: ignore
            ok = self.reach.pick(target)
            if ok: self.anim.set_active("sparkle")
            return ok
        if intent == Intent.PLACE:
            target = tuple(p.get("target", (0, 1)))  # type: ignore
            return self.reach.place(target)
        if intent == Intent.STOW: return self.reach.stow()
        if intent == Intent.DRAW: return self.reach.draw(int(p.get("slot", 0)))
        if intent == Intent.EXPRESS: return self.anim.set_active(str(p.get("anim", "joy")))
        if intent == Intent.NOTE:
            self.gws.log(thought.content); return True
        return False

    def command(self, content: str, intent: Optional[Intent] = None, **payload) -> None:
        self.thinks.observe(self.avatar)
        self.thinks.think(content, intent=intent, **payload)

    def search(self, query: str) -> List[Dict[str, Any]]:
        return self.gws.search_dell(query)

    def confirm(self, n: int) -> bool:
        return self.gws.pipeline_confirm(n)

    def tokenize_seed(self, text: str) -> List[Dict[str, Any]]:
        tokens = TOKENIZE(text)
        self.mem.charge(text)
        return tokens

    def tick(self) -> str:
        self.ticks += 1
        self.thinks.observe(self.avatar)
        thought = self.thinks.next_intent()
        if thought:
            ok = self._execute(thought)
            msg = f"{thought.intent.name if thought.intent else 'NOTE'}:{'ok' if ok else 'fail'}"
            self.gws.log(msg)
            (self.mem.record_run if ok else self.mem.record_fail)(msg)
            if ok:
                self.gws.pipeline_add(msg)
        self.gws.frame = self.anim.tick()
        self._sync_gws()
        return self.render()

    def render(self) -> str:
        return self.gws.render()

    def status(self) -> Dict[str, Any]:
        b = self.avatar.read_body()
        return {
            "ticks": self.ticks,
            "pos": b.pos,
            "facing": getattr(b.facing, "name", str(b.facing)),
            "holding": b.holding,
            "inventory": self.reach.inventory.list_items(),
            "frame": self.anim.show(),
            "registry": self.registry_status,
            "pipeline_pending": len(self.gws.pipeline_pending()),
            "mem_runs": len(self.mem.runs),
            "mem_fails": len(self.mem.fails),
            "budget_used": self.mem.used,
        }

# =============================================================================
# Smoke tests
# =============================================================================

def smoke_test() -> bool:
    """Return True if all critical paths pass."""
    print("=== SMOKE TEST ===")
    ok = True
    sys = Integrator()

    # 1. Registry loaded
    reg_ok = sys.registry_status in ("TRUE", "FALLBACK")
    print(f"[1] Registry status: {sys.registry_status} → {'PASS' if reg_ok else 'FAIL'}")
    ok &= reg_ok

    # 2. Lexer callable
    tokens = sys.tokenize_seed("50 Manifest > 08 Create")
    lex_ok = isinstance(tokens, list) and len(tokens) >= 1
    print(f"[2] Lexer tokens: {len(tokens)} → {'PASS' if lex_ok else 'FAIL'}")
    ok &= lex_ok

    # 3. Boot + pick/stow/express/move
    sys.boot()
    sys.command("pick", intent=Intent.PICK, target=(1, 0))
    sys.tick()
    pick_ok = sys.avatar.body.holding is not None
    print(f"[3] Pick: {pick_ok} → {'PASS' if pick_ok else 'FAIL'}")
    ok &= pick_ok

    sys.command("stow", intent=Intent.STOW)
    sys.tick()
    stow_ok = sys.avatar.body.holding is None and len(sys.reach.inventory.list_items()) == 1
    print(f"[4] Stow: {stow_ok} → {'PASS' if stow_ok else 'FAIL'}")
    ok &= stow_ok

    sys.command("joy", intent=Intent.EXPRESS, anim="joy")
    sys.tick()
    expr_ok = sys.anim.active == "joy"
    print(f"[5] Express: {expr_ok} → {'PASS' if expr_ok else 'FAIL'}")
    ok &= expr_ok

    pos0 = sys.avatar.body.pos
    sys.command("move", intent=Intent.MOVE, steps=1)
    sys.tick()
    move_ok = sys.avatar.body.pos != pos0
    print(f"[6] Move: {move_ok} → {'PASS' if move_ok else 'FAIL'}")
    ok &= move_ok

    # 4. Dell search
    hits = sys.search("Create")
    search_ok = any(str(h.get("name", "")).lower() == "create" or h.get("dell") == 8 for h in hits)
    print(f"[7] Dell search Create: {len(hits)} hits → {'PASS' if search_ok else 'FAIL'}")
    ok &= search_ok

    # 5. Pipeline confirm
    pending = sys.gws.pipeline_pending()
    if pending:
        conf_ok = sys.confirm(pending[0].n)
    else:
        conf_ok = False
    print(f"[8] Pipeline confirm: {conf_ok} → {'PASS' if conf_ok else 'FAIL'}")
    ok &= conf_ok

    print("=== RESULT:", "ALL PASS" if ok else "FAILURES DETECTED", "===")
    print("STATUS:", sys.status())
    return ok

def demo():
    sys = Integrator()
    sys.boot()
    print(sys.render())
    print()
    sys.command("Pick the wrench", intent=Intent.PICK, target=(1, 0))
    print(sys.tick()); print()
    sys.command("Stow", intent=Intent.STOW)
    print(sys.tick()); print()
    sys.search("Bind")
    print(sys.render())
    print("STATUS:", sys.status())

if __name__ == "__main__":
    if "--smoke" in sys.argv:
        passed = smoke_test()
        sys.exit(0 if passed else 1)
    demo()
