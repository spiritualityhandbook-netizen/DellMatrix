#!/usr/bin/env python3
"""
Inspire Pack — offline capabilities distilled from study links.

Videos studied (titles + public descriptions; not a claim of full auto-captions):
  1. YmLp8qe87A0  — I Built an LLM From Scratch (Syntax)
  2. iyux-TVToRU  — Everything About Calculus Explained Slowly
  3. eDpTtxFhP2s  — Intro to p5play 2.1 Sprites Animation
  4. vO6SWG-jxvE  — DeepMind Just Changed How AI Sees The World (Two Minute Papers)
  5. Qr3VsZYQy4s  — How I released a game that has no assets (Zanzlanz)
  6. ebqKYLKjL6U  — Verse: A New Scripting Language?
  7. ppQh4Tc9BmM  — The Billion Dollar AI Race Just Broke (Two Minute Papers)
  8. 8B05cy3UuSE  — NVIDIA's AI Learns Why Copying Humans Isn't Enough
  9. bm1BjOjS7sQ  — Another DeepSeek Moment Has Arrived (Two Minute Papers)

Implemented offline (no network, no external models):
  • Tiny tokenizer + bag embeddings + cosine "attention" over idea text (LLM pedagogy)
  • Score calculus: slopes / rates of change over pulse history
  • Sprite animation cycles (p5play-inspired frame states)
  • Multi-scale vision memory (hierarchical see + remember)
  • Procedural glyphs (zero external art assets)
  • Preference ledger from confirm/reject (not pure imitation)
  • Cheap-first efficiency router for commands
  • Mini matrix script runner (Verse-inspired batch ops)

Law: Floor locked · Nursery confirm · SIDE llm untouched · educational stubs only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math
import re
import time


# ─── 1. LLM-from-scratch pedagogy (tokenizer · embedding · attention) ─────

_WORD_RE = re.compile(r"[A-Za-z0-9_]+|[^\sA-Za-z0-9_]")


def tokenize(text: str) -> List[str]:
    """Simple educational tokenizer (Syntax / Karpathy-style intro)."""
    return [t.lower() for t in _WORD_RE.findall(text or "") if t.strip()]


def build_vocab(corpus: List[str], max_size: int = 512) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for doc in corpus:
        for t in tokenize(doc):
            counts[t] = counts.get(t, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[: max(8, max_size - 2)]
    vocab = {"<pad>": 0, "<unk>": 1}
    for i, (w, _) in enumerate(ranked, start=2):
        vocab[w] = i
    return vocab


def embed_bag(tokens: List[str], vocab: Dict[str, int], dim: int = 32) -> List[float]:
    """Hash-ish bag embedding: deterministic pseudo-embedding from token ids (no torch)."""
    vec = [0.0] * dim
    if not tokens:
        return vec
    for t in tokens:
        tid = vocab.get(t, 1)
        # spread id into dims with sin/cos features
        for d in range(dim):
            vec[d] += math.sin((tid + 1) * (d + 1) * 0.17) + math.cos((tid + 3) * (d + 2) * 0.11)
    n = float(len(tokens))
    return [v / n for v in vec]


def cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return max(-1.0, min(1.0, dot / (na * nb)))


def attention_rank(query: str, docs: List[Dict[str, str]], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Soft attention over idea documents: softmax-ish scores by cosine of bag embeddings.
    docs: [{id, text, label?}]
    """
    corpus = [query] + [d.get("text") or d.get("label") or "" for d in docs]
    vocab = build_vocab(corpus)
    qv = embed_bag(tokenize(query), vocab)
    scored = []
    for d in docs:
        text = d.get("text") or d.get("label") or ""
        dv = embed_bag(tokenize(text), vocab)
        s = cosine(qv, dv)
        scored.append({
            "id": d.get("id"),
            "label": d.get("label") or d.get("id"),
            "score": round(s, 4),
            "text_preview": (text or "")[:80],
        })
    scored.sort(key=lambda x: -x["score"])
    # temperature softmax for attention weights on top_k
    top = scored[:top_k]
    if top:
        mx = max(t["score"] for t in top)
        exps = [math.exp((t["score"] - mx) * 4.0) for t in top]
        z = sum(exps) or 1.0
        for t, e in zip(top, exps):
            t["attention"] = round(e / z, 4)
    return top


# ─── 2. Calculus: rates of change ──────────────────────────────────────────

@dataclass
class ScoreHistory:
    """Track scores over pulses; compute discrete derivatives (slopes)."""
    samples: List[Dict[str, Any]] = field(default_factory=list)  # {t, scores: {id: float}}
    max_samples: int = 48

    def push(self, scores: Dict[str, float], t: Optional[float] = None) -> None:
        self.samples.append({"t": float(t if t is not None else time.time()), "scores": dict(scores or {})})
        while len(self.samples) > self.max_samples:
            self.samples.pop(0)

    def slope(self, unit_id: str) -> Optional[float]:
        """Δscore / Δt for last two samples containing unit_id.

        When pulses fire in the same wall-clock instant, fall back to
        per-pulse discrete derivative (Δscore / 1 pulse) so slopes stay readable.
        """
        pts = []
        for s in self.samples:
            if unit_id in s["scores"]:
                pts.append((s["t"], float(s["scores"][unit_id])))
        if len(pts) < 2:
            return None
        (t0, y0), (t1, y1) = pts[-2], pts[-1]
        dt = t1 - t0
        if abs(dt) < 1e-3:
            # sub-ms: treat as one pulse step
            return y1 - y0
        return (y1 - y0) / dt

    def slopes(self) -> Dict[str, float]:
        ids = set()
        for s in self.samples:
            ids.update(s["scores"].keys())
        out = {}
        for uid in ids:
            sl = self.slope(uid)
            if sl is not None:
                out[uid] = round(sl, 6)
        return out

    def report(self) -> List[str]:
        sl = self.slopes()
        if not sl:
            return ["No slope data yet — pulse twice after scoring."]
        ranked = sorted(sl.items(), key=lambda x: -abs(x[1]))[:12]
        lines = ["Score calculus (Δscore/Δt):"]
        for uid, v in ranked:
            arrow = "↑" if v > 0 else ("↓" if v < 0 else "→")
            lines.append(f"  {arrow} {uid}: {v:+.5f}")
        return lines


# ─── 3. Sprite animation (p5play-inspired) ─────────────────────────────────

# Walk cycle overlays for stick body mid-row
_WALK_CYCLE = {
    0: " /|\\ ",
    1: " /|\\ ",
    2: "  |  ",
    3: " /|\\ ",
}
_WALK_LEGS = {
    0: " / \\ ",
    1: " /|  ",
    2: "  |  ",
    3: "  |\\ ",
}


@dataclass
class SpriteAnimator:
    """Frame-based animation state for avatar bodies."""
    body_type: str = "stick"
    facing: str = "N"
    action: str = "idle"  # idle | walk | turn | jump
    frame: int = 0
    tick: int = 0

    def set_action(self, action: str) -> None:
        if action != self.action:
            self.action = action
            self.frame = 0

    def step(self) -> str:
        self.tick += 1
        if self.action == "walk":
            self.frame = (self.frame + 1) % 4
        elif self.action == "turn":
            self.frame = (self.frame + 1) % 2
        elif self.action == "jump":
            self.frame = min(self.frame + 1, 2)
            if self.frame >= 2:
                self.action = "idle"
                self.frame = 0
        return self.render()

    def render(self) -> str:
        from form.dell_matrix.ascii_bodies import render_body, DIRS
        base = render_body(self.body_type, self.facing)
        lines = base.split("\n")
        if len(lines) < 3:
            return base
        if self.action == "walk":
            lines[1] = _WALK_CYCLE.get(self.frame, lines[1])
            lines[2] = _WALK_LEGS.get(self.frame, lines[2])
        elif self.action == "jump":
            # lift head
            lines = [" " + lines[0].strip() + " ", lines[1], "  ·  "]
        elif self.action == "idle" and (self.tick // 6) % 2 == 0:
            # subtle breath
            if lines[0].strip().startswith("o") or "o" in lines[0]:
                lines[0] = lines[0].replace("o", "O", 1).replace("°", "*", 1)
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        return {
            "body_type": self.body_type,
            "facing": self.facing,
            "action": self.action,
            "frame": self.frame,
            "tick": self.tick,
            "art": self.render(),
        }


# ─── 4. Multi-scale vision memory (DeepMind-inspired hierarchy) ────────────

@dataclass
class VisionMemory:
    """
    Hierarchical vision:
      near  — tight cone / short range
      mid   — normal cone
      far   — wide soft awareness
    Remembers last-seen ideas with recency.
    """
    seen: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # id -> {label, t, scale, dist}
    max_memory: int = 64

    def observe(
        self,
        nodes: List[Dict[str, Any]],
        pos: List[float],
        facing: str,
        *,
        scales: Optional[List[Tuple[str, float, float]]] = None,
    ) -> Dict[str, Any]:
        """
        scales: list of (name, range, half_angle)
        """
        from form.dell_matrix.vision import compute_vision

        scales = scales or [
            ("near", 2.5, 35.0),
            ("mid", 5.5, 55.0),
            ("far", 9.0, 75.0),
        ]
        layers = {}
        now = time.time()
        for name, rng, half in scales:
            v = compute_vision(pos, facing, nodes, range_=rng, half_angle=half)
            layers[name] = {
                "count": v["pattern"]["count"],
                "nearest": v["pattern"].get("nearest"),
                "ids": list(v.get("in_view_ids") or []),
                "nodes": v.get("nodes") or [],
            }
            for n in v.get("nodes") or []:
                nid = str(n.get("id"))
                self.seen[nid] = {
                    "id": nid,
                    "label": n.get("label"),
                    "skin": n.get("skin"),
                    "dist": n.get("dist"),
                    "scale": name,
                    "t": now,
                }
        # trim memory by age
        if len(self.seen) > self.max_memory:
            ordered = sorted(self.seen.items(), key=lambda x: x[1].get("t", 0))
            for k, _ in ordered[: len(self.seen) - self.max_memory]:
                self.seen.pop(k, None)
        return {
            "layers": layers,
            "memory_size": len(self.seen),
            "recent": self.recent(8),
        }

    def recent(self, n: int = 8) -> List[Dict[str, Any]]:
        items = sorted(self.seen.values(), key=lambda x: -x.get("t", 0))
        return items[:n]

    def recall(self, query: str = "") -> List[Dict[str, Any]]:
        items = list(self.seen.values())
        if not query:
            return self.recent(12)
        q = query.lower()
        hits = [x for x in items if q in str(x.get("label") or "").lower() or q in str(x.get("id") or "")]
        hits.sort(key=lambda x: -x.get("t", 0))
        return hits[:12]


# ─── 5. Procedural assets (no external art) ────────────────────────────────

_GLYPHS = "·:+*#@░▒▓█▀▄▌▐│─┌┐└┘╭╮╰╯╱╲╳✦✧✩✪✫✬✭✮✯✰✶✹"

def procedural_glyph(seed: str, width: int = 9, height: int = 5) -> str:
    """Deterministic pure-code glyph from seed string — zero image files."""
    h = sum((i + 1) * ord(c) for i, c in enumerate(seed or "x")) & 0xFFFFFFFF
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            v = (h * 1103515245 + 12345 + x * 17 + y * 31) & 0x7FFFFFFF
            if x == width // 2 and y == height // 2:
                row.append("●")
            elif v % 7 == 0:
                row.append(_GLYPHS[v % len(_GLYPHS)])
            elif v % 5 == 0:
                row.append("·")
            else:
                row.append(" ")
        rows.append("".join(row))
    return "\n".join(rows)


def procedural_idea_card(label: str, skin: str = "cube", score: float = 0.0) -> str:
    g = procedural_glyph(f"{label}:{skin}", 11, 5)
    return f"[{skin}] {label} sc={score:.2f}\n{g}"


# ─── 6. Preference learning (confirm/reject ≠ pure imitation) ──────────────

@dataclass
class PreferenceLedger:
    """
    NVIDIA-inspired: copying user moves isn't enough — track preferences.
    confirm → boost token weights; reject → dampen.
    """
    weights: Dict[str, float] = field(default_factory=dict)
    confirms: int = 0
    rejects: int = 0

    def observe_confirm(self, text: str, affinity: float = 1.0) -> None:
        self.confirms += 1
        for t in tokenize(text):
            self.weights[t] = self.weights.get(t, 0.0) + 0.15 * max(0.2, float(affinity))

    def observe_reject(self, text: str) -> None:
        self.rejects += 1
        for t in tokenize(text):
            self.weights[t] = self.weights.get(t, 0.0) - 0.12

    def score_text(self, text: str) -> float:
        toks = tokenize(text)
        if not toks:
            return 0.0
        return sum(self.weights.get(t, 0.0) for t in toks) / len(toks)

    def rank_proposals(self, proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out = []
        for p in proposals:
            text = " ".join([
                str(p.get("label") or ""),
                str(p.get("words") or ""),
                str(p.get("detail") or ""),
            ])
            pref = self.score_text(text)
            base = float(p.get("affinity") or 0.0)
            blended = 0.65 * base + 0.35 * (math.tanh(pref))
            row = dict(p)
            row["pref_score"] = round(pref, 4)
            row["blended"] = round(blended, 4)
            out.append(row)
        out.sort(key=lambda x: -float(x.get("blended") or 0))
        return out

    def top_weights(self, n: int = 12) -> List[Tuple[str, float]]:
        return sorted(self.weights.items(), key=lambda x: -abs(x[1]))[:n]

    def status(self) -> Dict[str, Any]:
        return {
            "confirms": self.confirms,
            "rejects": self.rejects,
            "tokens": len(self.weights),
            "top": self.top_weights(8),
        }


# ─── 7. Efficiency router (cheap-first) ────────────────────────────────────

# Commands that never need heavy path
_CHEAP = {
    "status", "look", "home", "help", "lattice", "proposals", "rank",
    "cube", "sphere", "core", "flower", "toggle", "radar", "entities",
}


def route_cost(cmd: str) -> str:
    """Return 'cheap' | 'medium' | 'heavy' for command routing."""
    c = (cmd or "").strip().lower()
    if not c:
        return "cheap"
    if c in _CHEAP or c.startswith("persona ") or c.startswith("weather "):
        return "cheap"
    if c.startswith("grow") or c in ("evolve", "pulse", "confirm all", "audit"):
        return "heavy"
    if c.startswith("fp ") or c.startswith("ai ") or c.startswith("plant "):
        return "medium"
    return "medium"


# ─── 8. Mini matrix script (Verse-inspired) ────────────────────────────────

_SCRIPT_HELP = """Matrix script (one command per line or ; separated):
  look
  grow 1
  pulse
  cube | sphere | flower
  home
  status
  # comments ignored
"""


def run_matrix_script(program, script: str) -> Dict[str, Any]:
    """Run a tiny offline script against Program via live command bridge."""
    from form.dell_matrix.live_visual import _run_command

    raw = (script or "").replace(";", "\n")
    lines = []
    for line in raw.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        # sugar
        if s.startswith("grow ") and s[5:].isdigit():
            s = f"grow ideas {s[5:]}"
        elif s == "grow":
            s = "grow ideas 1"
        lines.append(s)

    results = []
    for cmd in lines[:40]:
        cost = route_cost(cmd)
        r = _run_command(program, cmd)
        results.append({
            "cmd": cmd,
            "cost": cost,
            "ok": bool(r.get("ok")),
            "msg": (r.get("msg") or r.get("error") or "")[:120],
        })
    ok_n = sum(1 for r in results if r["ok"])
    return {
        "ok": ok_n == len(results) and len(results) > 0,
        "ran": len(results),
        "passed": ok_n,
        "results": results,
        "help": _SCRIPT_HELP,
    }


# ─── Program-facing facade ─────────────────────────────────────────────────

@dataclass
class InspireState:
    scores: ScoreHistory = field(default_factory=ScoreHistory)
    vision_mem: VisionMemory = field(default_factory=VisionMemory)
    prefs: PreferenceLedger = field(default_factory=PreferenceLedger)
    sprite: SpriteAnimator = field(default_factory=SpriteAnimator)
    last_attention: List[Dict[str, Any]] = field(default_factory=list)
    last_multivision: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prefs": {
                "weights": dict(list(self.prefs.weights.items())[:128]),
                "confirms": self.prefs.confirms,
                "rejects": self.prefs.rejects,
            },
            "scores": {
                "samples": list(self.scores.samples)[-24:],
            },
            "vision_recent": self.vision_mem.recent(16),
            "sprite": {
                "body_type": self.sprite.body_type,
                "facing": self.sprite.facing,
                "action": self.sprite.action,
                "frame": self.sprite.frame,
                "tick": self.sprite.tick,
            },
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "InspireState":
        st = cls()
        if not data or not isinstance(data, dict):
            return st
        pref = data.get("prefs") or {}
        if isinstance(pref, dict):
            st.prefs.weights = {
                str(k): float(v)
                for k, v in (pref.get("weights") or {}).items()
                if isinstance(v, (int, float))
            }
            st.prefs.confirms = int(pref.get("confirms") or 0)
            st.prefs.rejects = int(pref.get("rejects") or 0)
        sc = data.get("scores") or {}
        if isinstance(sc, dict):
            samples = sc.get("samples") or []
            st.scores.samples = [s for s in samples if isinstance(s, dict)][-48:]
        for item in data.get("vision_recent") or []:
            if isinstance(item, dict) and item.get("id"):
                st.vision_mem.seen[str(item["id"])] = dict(item)
        sp = data.get("sprite") or {}
        if isinstance(sp, dict):
            st.sprite.body_type = str(sp.get("body_type") or "stick")
            st.sprite.facing = str(sp.get("facing") or "N")
            st.sprite.action = str(sp.get("action") or "idle")
            st.sprite.frame = int(sp.get("frame") or 0)
            st.sprite.tick = int(sp.get("tick") or 0)
        return st

    def status(self) -> Dict[str, Any]:
        return {
            "prefs": self.prefs.status(),
            "score_samples": len(self.scores.samples),
            "slopes": self.scores.slopes(),
            "vision_memory": len(self.vision_mem.seen),
            "sprite": self.sprite.status(),
            "last_attention_n": len(self.last_attention),
            "multivision_layers": list((self.last_multivision.get("layers") or {}).keys()),
        }


def smoke() -> bool:
    print("=== INSPIRE PACK SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}")
        r.append(bool(ok))
    toks = tokenize("Hello Matrix 08[Create]")
    rec("tokenize", "hello" in toks and "matrix" in toks)
    docs = [
        {"id": "a", "label": "Alpha", "text": "growth seed flower"},
        {"id": "b", "label": "Beta", "text": "cube building structure"},
    ]
    att = attention_rank("seed growth", docs)
    rec("attention", att and att[0]["id"] == "a")
    sh = ScoreHistory()
    sh.push({"a": 1.0})
    sh.push({"a": 1.5})
    rec("slope", sh.slope("a") is not None)
    sp = SpriteAnimator()
    sp.set_action("walk")
    art = sp.step()
    rec("sprite", len(art.splitlines()) >= 2)
    vm = VisionMemory()
    nodes = [{"id": "a", "label": "A", "skin": "seed", "x": 0, "y": 2, "score": 1}]
    mv = vm.observe(nodes, [0, 0], "N")
    rec("multivision", "layers" in mv and "near" in mv["layers"])
    g = procedural_glyph("test")
    rec("procedural", len(g) > 5)
    pref = PreferenceLedger()
    pref.observe_confirm("growth seed idea", 0.9)
    pref.observe_reject("noise spam")
    rec("prefs", pref.score_text("growth seed") > pref.score_text("noise spam"))
    rec("router", route_cost("look") == "cheap" and route_cost("grow ideas 2") == "heavy")
    print(f"=== {sum(r)}/{len(r)} PASS ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
