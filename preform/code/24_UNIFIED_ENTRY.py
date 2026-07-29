#!/usr/bin/env python3
"""
24_UNIFIED_ENTRY.py
Code Phase 4 · Unified offline entry (deep-bind + token gate)
Status: TRUE
Offline · stdlib only

- Prefer Integrator 15 when loadable
- PersonaLens 21 + GWS panels 19 when loadable
- Token Show Gate 18 on seed-strip / Show paths when loadable
- Stand-ins otherwise

Run:
  python preform/code/24_UNIFIED_ENTRY.py
  python preform/code/24_UNIFIED_ENTRY.py --smoke
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import importlib.util
import os
import sys

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
FLOOR = ("Alpha", "Delta", "Omega", "Omni")
Coord = Tuple[int, int]


def _load_attr(filename: str, attr: str):
    path = os.path.join(_CODE_DIR, filename)
    try:
        if not os.path.isfile(path):
            return None, "miss"
        name = f"ue_{os.path.splitext(filename)[0]}"
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        if hasattr(mod, attr):
            return getattr(mod, attr), "real"
    except Exception as e:
        return None, f"error:{type(e).__name__}"
    return None, "miss"


# ----- stand-ins -----

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
        idx = (vals.index(self.body.facing) + n) % len(vals)
        self.body.facing = vals[idx]
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


class ReachInventory:
    def __init__(self, avatar: Avatar, grid: Grid):
        self.avatar = avatar
        self.grid = grid
        self.inventory = Inventory()

    def _dist(self, a: Coord, b: Coord) -> int:
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def can_reach(self, target: Coord) -> bool:
        return self._dist(self.avatar.body.pos, target) <= 1

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
    manu_on: bool = True
    ancient_on: bool = True
    notes: List[LensNote] = field(default_factory=list)

    def examine(self, text: str) -> List[LensNote]:
        t = (text or "").strip()
        self.notes = [LensNote("Aetheris", "coherence", "clear" if t else "empty")]
        if self.manu_on and t:
            self.notes.append(LensNote("MANUELL", "coach", "sketch: 08[Create] > …"))
        if self.ancient_on:
            self.notes.append(
                LensNote("The_Ancient", "structural", "structural only — no decipherment claim")
            )
        return list(self.notes)


@dataclass
class Panel:
    name: str
    expanded: bool = True


@dataclass
class StandinGWS:
    panels: Dict[str, Panel] = field(default_factory=dict)
    messages: List[str] = field(default_factory=list)

    def __post_init__(self):
        for n in ("status", "seed", "pipeline", "search", "log", "lens"):
            self.panels.setdefault(n, Panel(n))

    def expand(self, name: str) -> bool:
        if name not in self.panels:
            return False
        self.panels[name].expanded = True
        return True

    def collapse(self, name: str) -> bool:
        if name not in self.panels:
            return False
        self.panels[name].expanded = False
        return True

    def is_expanded(self, name: str) -> bool:
        p = self.panels.get(name)
        return bool(p and p.expanded)

    def log(self, msg: str) -> None:
        self.messages.append(msg)
        self.messages = self.messages[-12:]


@dataclass
class StandinTokenBudget:
    limit: int = 4096
    used: int = 0
    reserved: int = 64

    def estimate(self, text: str) -> int:
        if not text:
            return 0
        return max(1, len(text) // 4)

    def remaining(self) -> int:
        return max(0, self.limit - self.used - self.reserved)

    def can_afford(self, text: str) -> bool:
        return self.estimate(text) <= self.remaining()

    def charge(self, text: str) -> bool:
        cost = self.estimate(text)
        if cost > self.remaining():
            return False
        self.used += cost
        return True

    def status(self) -> Dict[str, int]:
        return {
            "limit": self.limit,
            "used": self.used,
            "reserved": self.reserved,
            "remaining": self.remaining(),
        }


@dataclass
class StandinShowGate:
    budget: StandinTokenBudget = field(default_factory=StandinTokenBudget)
    mode: str = "strict"
    seed_strip: str = ""
    last_show: str = ""
    rejects: int = 0
    trims: int = 0

    def _trim(self, text: str) -> str:
        rem = self.budget.remaining()
        if rem <= 0:
            return ""
        max_chars = rem * 4
        if len(text) <= max_chars:
            return text
        return text[: max(0, max_chars - 1)] + "…"

    def set_seed_strip(self, text: str) -> Tuple[bool, str]:
        text = text or ""
        if self.budget.can_afford(text):
            self.budget.charge(text)
            self.seed_strip = text
            return True, "seed_strip set"
        if self.mode == "soft":
            trimmed = self._trim(text)
            if trimmed and self.budget.charge(trimmed):
                self.seed_strip = trimmed
                self.trims += 1
                return True, "seed_strip trimmed"
        self.rejects += 1
        return False, "seed_strip rejected"

    def show(self, text: str) -> Tuple[bool, str]:
        text = text or ""
        if self.budget.can_afford(text):
            self.budget.charge(text)
            self.last_show = text
            return True, text
        if self.mode == "soft":
            trimmed = self._trim(text)
            if trimmed and self.budget.charge(trimmed):
                self.last_show = trimmed
                self.trims += 1
                return True, trimmed
        self.rejects += 1
        return False, ""

    def status(self) -> Dict[str, Any]:
        return {
            "budget": self.budget.status(),
            "mode": self.mode,
            "rejects": self.rejects,
            "trims": self.trims,
            "seed_len": len(self.seed_strip),
            "show_len": len(self.last_show),
        }


# ---------------------------------------------------------------------------
# Unified Entry
# ---------------------------------------------------------------------------

@dataclass
class UnifiedEntry:
    integrator: Any = None
    avatar: Optional[Avatar] = None
    grid: Optional[Grid] = None
    reach: Optional[ReachInventory] = None
    lens: Any = field(default=None)
    gws: Any = field(default=None)
    show_gate: Any = field(default=None)
    ticks: int = 0
    last_command: str = ""
    last_intent_ok: Optional[bool] = None
    seed_strip: str = "08[Create] >> 14[Bind] :: unified"
    sources: Dict[str, str] = field(default_factory=dict)
    frame: str = "(·_·)"
    mode: str = "standin"
    last_show: str = ""

    def __post_init__(self):
        IntegratorCls, integ_src = _load_attr("15_INTEGRATOR.py", "Integrator")
        LensCls, lens_src = _load_attr("21_PERSONA_LENS.py", "PersonaLens")
        GwsCls, gws_src = _load_attr("19_GWS_PANELS.py", "GWSPanels")
        ShowGateCls, gate_src = _load_attr("18_TOKEN_SHOW_GATE.py", "ShowGate")

        self.sources = {
            "integrator": integ_src,
            "lens": lens_src,
            "gws": gws_src,
            "token_gate": gate_src,
        }
        self.lens = LensCls() if LensCls else StandinLens()
        self.gws = GwsCls() if GwsCls else StandinGWS()
        self.show_gate = ShowGateCls() if ShowGateCls else StandinShowGate()

        if IntegratorCls is not None:
            try:
                self.integrator = IntegratorCls()
                self.mode = "integrator"
            except Exception:
                self.integrator = None
                self.mode = "standin"
        else:
            self.mode = "standin"

        if self.mode == "standin":
            self.avatar = Avatar()
            self.grid = Grid()
            self.reach = ReachInventory(self.avatar, self.grid)

        if hasattr(self.gws, "panels") and "lens" not in getattr(self.gws, "panels", {}):
            try:
                self.gws.panels["lens"] = Panel("lens", True)
            except Exception:
                pass

    def boot(self) -> None:
        self.ticks = 0
        self.last_command = ""
        self.last_intent_ok = None
        self.frame = "(·_·)"
        self.last_show = ""
        if self.mode == "integrator" and self.integrator is not None:
            try:
                self.integrator.boot()
            except Exception:
                pass
        elif self.grid is not None:
            self.grid.set(1, 0, content={"kind": "tool", "name": "wrench"})
            self.grid.set(0, 1, content={"kind": "note", "name": "seed-card"})
        # charge initial seed under gate
        ok, msg = self.set_seed_strip(self.seed_strip)
        if hasattr(self.gws, "log"):
            self.gws.log(f"boot:{msg}")
        self.lens.examine(self.seed_strip)

    def set_seed_strip(self, text: str) -> Tuple[bool, str]:
        ok, msg = self.show_gate.set_seed_strip(text or "")
        if ok:
            self.seed_strip = getattr(self.show_gate, "seed_strip", text or "")
        return ok, msg

    def show(self, text: str) -> Tuple[bool, str]:
        ok, payload = self.show_gate.show(text or "")
        if ok:
            self.last_show = payload
            self.frame = payload if len(payload) <= 8 else self.frame
        return ok, payload

    def _parse_intent(self, text: str, intent: Optional[Any], payload: Dict[str, Any]):
        if intent is not None:
            if isinstance(intent, Intent):
                return intent, payload
            if isinstance(intent, str):
                name = intent.upper()
                if name in Intent.__members__:
                    return Intent[name], payload
        t = (text or "").lower()
        if t.startswith("move") or t.startswith("step"):
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
            return Intent.SHOW, {"text": text[5:].strip() or payload.get("text", "")}
        if "joy" in t or t.startswith("express"):
            return Intent.EXPRESS, payload
        return Intent.NOTE, payload

    def _standin_execute(self, intent: Intent, payload: Dict[str, Any]) -> bool:
        assert self.avatar is not None and self.reach is not None
        if intent == Intent.MOVE:
            self.avatar.step(int(payload.get("steps", 1)))
            self.frame = "(>_<)"
            return True
        if intent == Intent.TURN:
            self.avatar.turn(int(payload.get("steps", 1)))
            return True
        if intent == Intent.PICK:
            target = tuple(payload.get("target", (1, 0)))  # type: ignore
            ok = self.reach.pick(target)
            if ok:
                self.frame = "✧"
            return ok
        if intent == Intent.PLACE:
            target = tuple(payload.get("target", (0, 1)))  # type: ignore
            return self.reach.place(target)
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
        if intent == Intent.NOTE:
            if hasattr(self.gws, "log"):
                self.gws.log(payload.get("text", self.last_command))
            return True
        return False

    def command(self, text: str, intent: Optional[Any] = None, **payload) -> List[Any]:
        self.last_command = text or ""
        notes = self.lens.examine(self.last_command)

        if self.mode == "integrator" and self.integrator is not None:
            try:
                if hasattr(self.integrator, "command"):
                    integ_intent = intent
                    IntentCls, _ = _load_attr("15_INTEGRATOR.py", "Intent")
                    if IntentCls is not None and isinstance(intent, str):
                        if intent.upper() in IntentCls.__members__:
                            integ_intent = IntentCls[intent.upper()]
                    self.integrator.command(text, intent=integ_intent, **payload)
                    if hasattr(self.integrator, "tick"):
                        self.integrator.tick()
                    self.last_intent_ok = True
                    if hasattr(self.integrator, "anim") and hasattr(self.integrator.anim, "show"):
                        try:
                            self.frame = self.integrator.anim.show()
                        except Exception:
                            pass
                else:
                    self.last_intent_ok = False
            except Exception:
                self.last_intent_ok = False
        else:
            ienum, pay = self._parse_intent(text, intent, payload)
            self.last_intent_ok = self._standin_execute(ienum, pay)

        if hasattr(self.gws, "log"):
            self.gws.log(f"cmd:{self.last_command[:24]}")
        return notes

    def tick(self) -> str:
        self.ticks += 1
        if self.mode == "integrator" and self.integrator is not None and hasattr(self.integrator, "tick"):
            try:
                self.integrator.tick()
            except Exception:
                pass
        return self.render()

    def _body_snapshot(self) -> Dict[str, Any]:
        if self.mode == "integrator" and self.integrator is not None:
            try:
                st = self.integrator.status() if hasattr(self.integrator, "status") else {}
                return {
                    "pos": st.get("pos", "?"),
                    "facing": st.get("facing", "?"),
                    "holding": st.get("holding"),
                    "inventory": st.get("inventory", []),
                }
            except Exception:
                pass
        assert self.avatar is not None
        b = self.avatar.read_body()
        inv = self.reach.inventory.list_items() if self.reach else []
        return {
            "pos": b.pos,
            "facing": getattr(b.facing, "name", str(b.facing)),
            "holding": b.holding,
            "inventory": inv,
        }

    def render(self) -> str:
        notes = getattr(self.lens, "notes", []) or []
        lens_open = True
        if hasattr(self.gws, "is_expanded"):
            try:
                lens_open = bool(self.gws.is_expanded("lens"))
            except Exception:
                lens_open = True
        mark = "-" if lens_open else "+"
        body = self._body_snapshot()
        gate_st = {}
        try:
            gate_st = self.show_gate.status()
        except Exception:
            gate_st = {}
        bud = gate_st.get("budget", {}) if isinstance(gate_st, dict) else {}

        lines = [
            f"+- UnifiedEntry · mode={self.mode} · tick={self.ticks} -+",
            f"| Floor: {' · '.join(FLOOR)} (locked)",
            f"| src integ={self.sources.get('integrator')} lens={self.sources.get('lens')} "
            f"gws={self.sources.get('gws')} gate={self.sources.get('token_gate')}",
            f"| Avatar pos={body.get('pos')} facing={body.get('facing')} frame={self.frame}",
            f"| Hand={body.get('holding')} Inv={body.get('inventory')}",
            f"| Budget used={bud.get('used', '?')} rem={bud.get('remaining', '?')} "
            f"rejects={gate_st.get('rejects', 0)} trims={gate_st.get('trims', 0)}",
            f"| SEED: {self.seed_strip}",
            f"| SHOW: {self.last_show or '(none)'}",
            f"| CMD:  {self.last_command or '(none)'} ok={self.last_intent_ok}",
            f"| [{mark}] LENS",
        ]
        if lens_open:
            if notes:
                for n in list(notes)[:6]:
                    persona = getattr(n, "persona", "?")
                    kind = getattr(n, "kind", "?")
                    text = getattr(n, "text", str(n))
                    lines.append(f"|     [{persona}/{kind}] {text}")
            else:
                lines.append("|     (no notes)")
        lines.append("+" + "-" * 44 + "+")
        return "\n".join(lines)

    def expand_lens(self) -> bool:
        return bool(hasattr(self.gws, "expand") and self.gws.expand("lens"))

    def collapse_lens(self) -> bool:
        return bool(hasattr(self.gws, "collapse") and self.gws.collapse("lens"))

    def status(self) -> Dict[str, Any]:
        body = self._body_snapshot()
        gate_st = {}
        try:
            gate_st = self.show_gate.status()
        except Exception:
            gate_st = {}
        return {
            "mode": self.mode,
            "ticks": self.ticks,
            "floor": list(FLOOR),
            "pos": body.get("pos"),
            "holding": body.get("holding"),
            "inventory": body.get("inventory"),
            "frame": self.frame,
            "command": self.last_command,
            "intent_ok": self.last_intent_ok,
            "notes": len(getattr(self.lens, "notes", []) or []),
            "token_gate": gate_st,
            "sources": dict(self.sources),
        }


def smoke() -> bool:
    print("=== UNIFIED ENTRY SMOKE (token bind) ===")
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

    ue = UnifiedEntry()
    run("init", lambda: (ue.show_gate is not None and ue.lens is not None, str(ue.sources)))
    run("boot", lambda: (ue.boot() or True, f"seed={ue.seed_strip[:24]}"))
    run("seed charged", lambda: (
        ue.status().get("token_gate", {}).get("budget", {}).get("used", 0) >= 0,
        str(ue.status().get("token_gate", {}).get("budget")),
    ))
    run("show ok", lambda: (ue.show("(^_^)")[0], f"last={ue.last_show}"))
    run("command lens", lambda: (len(ue.command("create and bind")) >= 1, f"n={len(ue.lens.notes)}"))
    run("pick", lambda: (
        (ue.command("pick", intent="PICK", target=(1, 0)) or True) is not None,
        f"ok={ue.last_intent_ok} holding={ue.status().get('holding')}",
    ))
    run("stow", lambda: (
        (ue.command("stow", intent="STOW") or True) is not None,
        f"ok={ue.last_intent_ok}",
    ))
    run("tick render", lambda: ("Budget" in ue.tick() and "Floor" in ue.render(), f"t={ue.ticks}"))
    run("floor", lambda: (ue.status()["floor"] == list(FLOOR), str(FLOOR)))

    # oversize seed reject/trim should not raise
    def oversize():
        gate = StandinShowGate(budget=StandinTokenBudget(limit=40, reserved=5), mode="strict")
        ok, msg = gate.set_seed_strip("x" * 500)
        return (not ok), msg

    run("strict reject oversize", oversize)

    print(f"=== RESULT: {sum(1 for x in results if x)}/{len(results)} PASS ===")
    return all(results)


def demo() -> None:
    ue = UnifiedEntry()
    ue.boot()
    print(ue.render())
    print()
    ue.command("pick", intent="PICK", target=(1, 0))
    ue.command("stow", intent="STOW")
    ue.show("(^_^)")
    print(ue.tick())
    print("STATUS:", ue.status())


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()
