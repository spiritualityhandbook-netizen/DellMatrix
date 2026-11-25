#!/usr/bin/env python3
"""
29_COMPOSE_ENTRY.py
Recommended single offline runner for the living core.
Status: TRUE · lexer-aware

Composes body/reach, PersonaLens, Token Show Gate, Dell/flow search,
owned PipelineQueue, optional Tiny Lexer on seed-shaped commands.
Floor: Alpha · Delta · Omega · Omni

Run:
  python preform/code/29_COMPOSE_ENTRY.py
  python preform/code/29_COMPOSE_ENTRY.py --smoke
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import importlib.util
import json
import os
import re
import sys

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
FLOOR = ("Alpha", "Delta", "Omega", "Omni")
Coord = Tuple[int, int]


def _load_attr(filename: str, attr: str):
    path = os.path.join(_CODE_DIR, filename)
    try:
        if not os.path.isfile(path):
            return None, "miss"
        name = f"c29_{os.path.splitext(filename)[0]}"
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        if hasattr(mod, attr):
            return getattr(mod, attr), "real"
    except Exception as e:
        return None, f"error:{type(e).__name__}"
    return None, "miss"


def _load_registry() -> Dict[str, Any]:
    path = os.path.join(_CODE_DIR, "01_REGISTRY_DATA.json")
    try:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "dells" in data:
                return data
    except Exception:
        pass
    return {
        "status": "FALLBACK",
        "dells": [
            {"dell": 8, "name": "Create", "manor": "Instantiate"},
            {"dell": 9, "name": "Show", "manor": "Render"},
            {"dell": 14, "name": "Bind", "manor": "Attach"},
            {"dell": 50, "name": "Manifest", "manor": "Make real"},
        ],
        "flows": [
            {"symbol": ">", "name": "Primary"},
            {"symbol": ">>", "name": "Strong Primary"},
            {"symbol": ":", "name": "Bind"},
            {"symbol": "<<[Delta]", "name": "Retrograde"},
        ],
    }


REGISTRY = _load_registry()

# seed-shaped detector: digits, [Name], flow symbols
_SEED_HINT = re.compile(
    r"(\b\d{1,2}\b|\[\w+\]|>>?>?|::?|<<\[?\w*\]?)",
    re.UNICODE,
)


class Facing(Enum):
    N, E, S, W = range(4)

    @property
    def delta(self) -> Coord:
        return [(0, 1), (1, 0), (0, -1), (-1, 0)][self.value]


class Intent(Enum):
    MOVE = auto()
    TURN = auto()
    PICK = auto()
    PLACE = auto()
    STOW = auto()
    DRAW = auto()
    EXPRESS = auto()
    NOTE = auto()
    SHOW = auto()


@dataclass
class Body:
    pos: Coord = (0, 0)
    facing: Facing = Facing.N
    holding: Any = None


@dataclass
class Avatar:
    body: Body = field(default_factory=Body)

    def read_body(self) -> Body:
        return Body(pos=self.body.pos, facing=self.body.facing, holding=self.body.holding)

    def step(self, n: int = 1) -> Coord:
        dx, dy = self.body.facing.delta
        x, y = self.body.pos
        self.body.pos = (x + dx * n, y + dy * n)
        return self.body.pos

    def turn(self, n: int = 1) -> Facing:
        vals = list(Facing)
        self.body.facing = vals[(vals.index(self.body.facing) + n) % 4]
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
            item = self.slots[i]
            self.slots[i] = None
            return item
        return None

    def list_items(self) -> List[Any]:
        return [s for s in self.slots if s is not None]


class Reach:
    def __init__(self, avatar: Avatar, grid: Grid):
        self.avatar = avatar
        self.grid = grid
        self.inventory = Inventory()

    def can_reach(self, target: Coord) -> bool:
        a = self.avatar.body.pos
        return max(abs(a[0] - target[0]), abs(a[1] - target[1])) <= 1

    def pick(self, target: Coord) -> bool:
        b = self.avatar.body
        if b.holding is not None or not self.can_reach(target):
            return False
        cell = self.grid.get(*target)
        if cell["content"] is None:
            return False
        b.holding = cell["content"]
        self.grid.clear(*target)
        return True

    def place(self, target: Coord) -> bool:
        b = self.avatar.body
        if b.holding is None or not self.can_reach(target):
            return False
        if self.grid.get(*target)["content"] is not None:
            return False
        self.grid.set(*target, content=b.holding)
        b.holding = None
        return True

    def stow(self) -> bool:
        b = self.avatar.body
        if b.holding is None:
            return False
        if self.inventory.add(b.holding):
            b.holding = None
            return True
        return False

    def draw(self, i: int = 0) -> bool:
        b = self.avatar.body
        if b.holding is not None:
            return False
        item = self.inventory.remove(i)
        if item is None:
            return False
        b.holding = item
        return True


@dataclass
class LensNote:
    persona: str
    kind: str
    text: str


@dataclass
class StandinLens:
    notes: List[LensNote] = field(default_factory=list)

    def examine(self, text: str):
        t = (text or "").strip()
        self.notes = [
            LensNote("Aetheris", "coherence", "clear" if t else "empty"),
            LensNote("MANUELL", "coach", "sketch: 08[Create] > …"),
            LensNote("The_Ancient", "structural", "structural only — no decipherment claim"),
        ]
        return list(self.notes)


@dataclass
class StandinBudget:
    limit: int = 4096
    used: int = 0
    reserved: int = 64

    def estimate(self, text: str) -> int:
        return 0 if not text else max(1, len(text) // 4)

    def remaining(self) -> int:
        return max(0, self.limit - self.used - self.reserved)

    def can_afford(self, text: str) -> bool:
        return self.estimate(text) <= self.remaining()

    def charge(self, text: str) -> bool:
        c = self.estimate(text)
        if c > self.remaining():
            return False
        self.used += c
        return True

    def status(self):
        return {"limit": self.limit, "used": self.used, "remaining": self.remaining()}


@dataclass
class StandinGate:
    budget: StandinBudget = field(default_factory=StandinBudget)
    seed_strip: str = ""
    last_show: str = ""
    rejects: int = 0

    def set_seed_strip(self, text: str):
        text = text or ""
        if self.budget.can_afford(text):
            self.budget.charge(text)
            self.seed_strip = text
            return True, "set"
        self.rejects += 1
        return False, "rejected"

    def show(self, text: str):
        text = text or ""
        if self.budget.can_afford(text):
            self.budget.charge(text)
            self.last_show = text
            return True, text
        self.rejects += 1
        return False, ""

    def status(self):
        return {"budget": self.budget.status(), "rejects": self.rejects}


@dataclass
class StandinPipeItem:
    n: int
    label: str
    confirmed: bool = False


@dataclass
class StandinPipeline:
    items: List[StandinPipeItem] = field(default_factory=list)
    _n: int = 0

    def add(self, label: str):
        self._n += 1
        item = StandinPipeItem(n=self._n, label=label or f"step-{self._n}")
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


class StandinLexer:
    """Minimal offline token recognizer if 02 is missing."""

    def tokenize(self, text: str) -> List[Dict[str, Any]]:
        tokens: List[Dict[str, Any]] = []
        if not text:
            return tokens
        # longest-ish flow first
        i = 0
        s = text
        while i < len(s):
            if s.startswith("<<<", i) or s.startswith(">>>", i):
                tokens.append({"kind": "flow", "value": s[i : i + 3]})
                i += 3
                continue
            if s.startswith("<<", i) or s.startswith(">>", i) or s.startswith("::", i):
                tokens.append({"kind": "flow", "value": s[i : i + 2]})
                i += 2
                continue
            if s[i] in ">:<":
                tokens.append({"kind": "flow", "value": s[i]})
                i += 1
                continue
            m = re.match(r"\d{1,2}", s[i:])
            if m:
                tokens.append({"kind": "dell", "value": m.group(0)})
                i += len(m.group(0))
                continue
            m = re.match(r"\[([^\]]+)\]", s[i:])
            if m:
                tokens.append({"kind": "name", "value": m.group(1)})
                i += len(m.group(0))
                continue
            i += 1
        return tokens


@dataclass
class ComposeEntry:
    avatar: Avatar = field(default_factory=Avatar)
    grid: Grid = field(default_factory=Grid)
    reach: Optional[Reach] = None
    lens: Any = field(default=None)
    gate: Any = field(default=None)
    pipeline: Any = field(default=None)
    lexer: Any = field(default=None)
    registry: Dict[str, Any] = field(default_factory=lambda: REGISTRY)
    ticks: int = 0
    last_command: str = ""
    last_ok: Optional[bool] = None
    last_tokens: List[Dict[str, Any]] = field(default_factory=list)
    seed_strip: str = "08[Create] >> 14[Bind] :: compose"
    last_show: str = ""
    frame: str = "(·_·)"
    last_dell_hits: List[Dict[str, Any]] = field(default_factory=list)
    last_flow_hits: List[Dict[str, Any]] = field(default_factory=list)
    sources: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.reach = Reach(self.avatar, self.grid)
        LensCls, lens_src = _load_attr("21_PERSONA_LENS.py", "PersonaLens")
        GateCls, gate_src = _load_attr("18_TOKEN_SHOW_GATE.py", "ShowGate")
        PipeCls, pipe_src = _load_attr("28_PIPELINE_QUEUE.py", "PipelineQueue")
        # lexer: prefer class TinyLexer / Lexer / module-level tokenize
        LexCls, lex_src = _load_attr("02_TINY_LEXER.py", "TinyLexer")
        if LexCls is None:
            LexCls, lex_src2 = _load_attr("02_TINY_LEXER.py", "Lexer")
            if LexCls is not None:
                lex_src = lex_src2
        self.sources = {
            "lens": lens_src,
            "gate": gate_src,
            "pipeline": pipe_src,
            "lexer": lex_src if LexCls is not None else "standin",
        }
        self.lens = LensCls() if LensCls else StandinLens()
        self.gate = GateCls() if GateCls else StandinGate()
        self.pipeline = PipeCls() if PipeCls else StandinPipeline()
        if LexCls is not None:
            try:
                self.lexer = LexCls()
            except Exception:
                self.lexer = StandinLexer()
                self.sources["lexer"] = "standin"
        else:
            # try module-level tokenize function via load file
            fn, src = _load_attr("02_TINY_LEXER.py", "tokenize")
            if callable(fn):
                self.lexer = fn  # type: ignore
                self.sources["lexer"] = src
            else:
                self.lexer = StandinLexer()

    def _lex(self, text: str) -> List[Dict[str, Any]]:
        if not text:
            return []
        try:
            if callable(self.lexer) and not hasattr(self.lexer, "tokenize"):
                out = self.lexer(text)
            elif hasattr(self.lexer, "tokenize"):
                out = self.lexer.tokenize(text)
            else:
                out = StandinLexer().tokenize(text)
            # normalize to list of dicts
            norm: List[Dict[str, Any]] = []
            for t in out or []:
                if isinstance(t, dict):
                    norm.append(t)
                else:
                    norm.append({"kind": getattr(t, "kind", type(t).__name__), "value": str(t)})
            return norm
        except Exception:
            return StandinLexer().tokenize(text)

    def boot(self) -> None:
        self.ticks = 0
        self.last_command = ""
        self.last_ok = None
        self.last_tokens = []
        self.frame = "(·_·)"
        self.grid.set(1, 0, content={"kind": "tool", "name": "wrench"})
        self.grid.set(0, 1, content={"kind": "note", "name": "seed-card"})
        ok, _ = self.gate.set_seed_strip(self.seed_strip)
        if ok:
            self.seed_strip = getattr(self.gate, "seed_strip", self.seed_strip)
        self.lens.examine(self.seed_strip)
        self.last_tokens = self._lex(self.seed_strip)
        self.pipeline.add("Boot complete")

    def set_seed_strip(self, text: str) -> Tuple[bool, str]:
        ok, msg = self.gate.set_seed_strip(text or "")
        if ok:
            self.seed_strip = getattr(self.gate, "seed_strip", text or "")
            self.last_tokens = self._lex(self.seed_strip)
        return ok, msg

    def show(self, text: str) -> Tuple[bool, str]:
        ok, payload = self.gate.show(text or "")
        if ok:
            self.last_show = payload
            if len(payload) <= 8:
                self.frame = payload
        return ok, payload

    def search_dell(self, query: str) -> List[Dict[str, Any]]:
        q = (query or "").strip().lower()
        hits = []
        for d in self.registry.get("dells", []):
            if not q or q == str(d.get("dell", "")) or q in str(d.get("name", "")).lower() or q in str(d.get("manor", "")).lower():
                hits.append(d)
        self.last_dell_hits = hits[:12]
        return self.last_dell_hits

    def search_flow(self, query: str) -> List[Dict[str, Any]]:
        q = (query or "").strip().lower()
        hits = []
        for f in self.registry.get("flows", []):
            sym = str(f.get("symbol", "")).lower()
            name = str(f.get("name", "")).lower()
            if not q or q == sym or q in sym or q in name:
                hits.append(f)
        self.last_flow_hits = hits[:12]
        return self.last_flow_hits

    def pipeline_add(self, label: str):
        return self.pipeline.add(label)

    def pipeline_confirm(self, n: int) -> bool:
        return bool(self.pipeline.confirm(n))

    def _parse(self, text: str, intent: Optional[Any], payload: Dict[str, Any]):
        if isinstance(intent, Intent):
            return intent, payload
        if isinstance(intent, str) and intent.upper() in Intent.__members__:
            return Intent[intent.upper()], payload
        t = (text or "").lower()
        if t.startswith("move"):
            return Intent.MOVE, payload
        if t.startswith("turn"):
            return Intent.TURN, payload
        if t.startswith("pick"):
            return Intent.PICK, {"target": payload.get("target", (1, 0))}
        if t.startswith("place"):
            return Intent.PLACE, {"target": payload.get("target", (0, 1))}
        if t.startswith("stow"):
            return Intent.STOW, payload
        if t.startswith("draw"):
            return Intent.DRAW, payload
        if t.startswith("show "):
            return Intent.SHOW, {"text": text[5:].strip()}
        if "joy" in t or t.startswith("express"):
            return Intent.EXPRESS, payload
        return Intent.NOTE, payload

    def _exec(self, intent: Intent, payload: Dict[str, Any]) -> bool:
        assert self.reach is not None
        if intent == Intent.MOVE:
            self.avatar.step(int(payload.get("steps", 1)))
            self.frame = "(>_<)"
            return True
        if intent == Intent.TURN:
            self.avatar.turn(int(payload.get("steps", 1)))
            return True
        if intent == Intent.PICK:
            ok = self.reach.pick(tuple(payload.get("target", (1, 0))))  # type: ignore
            if ok:
                self.frame = "✧"
            return ok
        if intent == Intent.PLACE:
            return self.reach.place(tuple(payload.get("target", (0, 1))))  # type: ignore
        if intent == Intent.STOW:
            return self.reach.stow()
        if intent == Intent.DRAW:
            return self.reach.draw(int(payload.get("slot", 0)))
        if intent == Intent.EXPRESS:
            self.frame = "(^_^)"
            return True
        if intent == Intent.SHOW:
            ok, _ = self.show(str(payload.get("text", "")))
            return ok
        return True

    def command(self, text: str, intent: Optional[Any] = None, **payload) -> List[Any]:
        self.last_command = text or ""
        notes = self.lens.examine(self.last_command)
        # lexer pass when seed-shaped
        if text and _SEED_HINT.search(text):
            self.last_tokens = self._lex(text)
        else:
            self.last_tokens = []
        ienum, pay = self._parse(text, intent, payload)
        ok = self._exec(ienum, pay)
        self.last_ok = ok
        if ok:
            label = f"{ienum.name}:{text[:20] or 'ok'}"
            if self.last_tokens:
                kinds = ",".join(str(t.get("kind", "?")) for t in self.last_tokens[:4])
                label = f"{label}|lex:{kinds}"
            self.pipeline.add(label)
        return notes

    def tick(self) -> str:
        self.ticks += 1
        return self.render()

    def render(self) -> str:
        b = self.avatar.read_body()
        notes = getattr(self.lens, "notes", []) or []
        gate_st = {}
        try:
            gate_st = self.gate.status()
        except Exception:
            pass
        bud = gate_st.get("budget", {}) if isinstance(gate_st, dict) else {}
        lines = [
            f"+- ComposeEntry · tick={self.ticks} -+",
            f"| Floor: {' · '.join(FLOOR)} (locked)",
            f"| src {self.sources}",
            f"| Avatar pos={b.pos} facing={b.facing.name} frame={self.frame}",
            f"| Hand={b.holding} Inv={self.reach.inventory.list_items() if self.reach else []}",
            f"| Budget used={bud.get('used', '?')} rem={bud.get('remaining', '?')}",
            f"| SEED: {self.seed_strip}",
            f"| SHOW: {self.last_show or '(none)'}",
            f"| CMD:  {self.last_command or '(none)'} ok={self.last_ok}",
            f"| LEX:  {self.last_tokens[:6] if self.last_tokens else '(none)'}",
            "| [-] PIPELINE",
        ]
        lines.extend(self.pipeline.render_lines())
        lines.append("| [-] SEARCH")
        if self.last_dell_hits:
            for d in self.last_dell_hits[:3]:
                lines.append(f"|     DELL {d.get('dell')}: {d.get('name')}")
        else:
            lines.append("|     DELL (search_dell)")
        if self.last_flow_hits:
            for f in self.last_flow_hits[:3]:
                lines.append(f"|     FLOW {f.get('symbol')}: {f.get('name')}")
        else:
            lines.append("|     FLOW (search_flow)")
        lines.append("| [-] LENS")
        for n in list(notes)[:4]:
            lines.append(f"|     [{getattr(n,'persona','?')}/{getattr(n,'kind','?')}] {getattr(n,'text',n)}")
        lines.append("+" + "-" * 44 + "+")
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        b = self.avatar.read_body()
        gate_st = {}
        try:
            gate_st = self.gate.status()
        except Exception:
            pass
        return {
            "ticks": self.ticks,
            "floor": list(FLOOR),
            "pos": b.pos,
            "holding": b.holding,
            "inventory": self.reach.inventory.list_items() if self.reach else [],
            "command": self.last_command,
            "ok": self.last_ok,
            "tokens": self.last_tokens,
            "pipeline": self.pipeline.status(),
            "dell_hits": len(self.last_dell_hits),
            "flow_hits": len(self.last_flow_hits),
            "token_gate": gate_st,
            "sources": dict(self.sources),
        }


def smoke() -> bool:
    print("=== COMPOSE ENTRY SMOKE (lexer bind) ===")
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

    c = ComposeEntry()
    run("boot", lambda: (c.boot() or True, f"src={c.sources}"))
    run("boot tokens", lambda: (len(c.last_tokens) >= 1, str(c.last_tokens[:4])))
    run("seed lex", lambda: (
        (c.command("08[Create] >> 14[Bind]") or True) is not None and len(c.last_tokens) >= 1,
        str(c.last_tokens[:5]),
    ))
    run("pick", lambda: (c.command("pick", intent="PICK", target=(1, 0)) is not None and c.last_ok, f"hold={c.avatar.body.holding}"))
    run("pipeline", lambda: (c.pipeline.status()["total"] >= 2, str(c.pipeline.status())))
    run("dell search", lambda: (len(c.search_dell("Create")) >= 1, f"n={len(c.last_dell_hits)}"))
    run("render LEX", lambda: ("LEX:" in c.tick() and "PIPELINE" in c.render(), f"t={c.ticks}"))
    run("floor", lambda: (c.status()["floor"] == list(FLOOR), str(FLOOR)))

    print(f"=== RESULT: {sum(1 for x in results if x)}/{len(results)} PASS ===")
    return all(results)


def demo() -> None:
    c = ComposeEntry()
    c.boot()
    c.command("08[Create] >> 14[Bind]")
    c.command("pick", intent="PICK", target=(1, 0))
    print(c.tick())
    print("STATUS:", c.status())


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()
