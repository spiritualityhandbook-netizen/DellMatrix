#!/usr/bin/env python3
"""Flow visuals — PP5/D3: render a chain execution as a static
trace and as text animation frames in the preform Anim shape.

Grounding: Ace's preform material (PHASE3_ASCII_ANIMATION +
code/10_ASCII_ANIMATION): an Anim is {id, fps, frames, loop}
where each frame is a text string; playback is a redraw of
successive frames. The chain moji ⛓️ comes from the existing
MANDELLMOJI vocabulary in seed.py.

This module renders ONLY what a canonical execution reported
(chain_exec's atom_results, aligned with the parsed seed). It
never executes anything, never re-runs a chain, and never
invents an outcome: when the reported results cannot be
aligned with the seed's atoms, the rendering says so
(aligned=False) and falls back to the verbatim seed text plus
the aggregate outcome instead of decorating atoms it cannot
account for.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .registry import get_dell
from .seed import MANDELLMOJI, parse_seed

_LINK = MANDELLMOJI.get("Chainlink", "⛓️")

_GLYPH = {"executed": "✓", "skipped": "⊘", "failed": "✗"}


def _status_of(result: Dict[str, Any]) -> str:
    if result.get("skipped"):
        return "skipped"
    return "executed" if result.get("ok") else "failed"


def _dell_text(dell: Any) -> str:
    try:
        n = int(dell)
    except (TypeError, ValueError):
        return f"??[{dell}]"
    d = get_dell(n)
    name = (d or {}).get("name") or "?"
    width = 3 if n > 99 else 2
    return f"{n:0{width}d}[{name}]"


def _steps(seed_text: str, atom_results: List[Dict[str, Any]]):
    """Align reported results with the parsed seed's atoms.

    Returns (seed, steps, aligned). Each step: {atom, flow_in,
    status, reason}. flow_in is the operator written before the
    atom in the seed ("" for the first atom)."""
    seed = parse_seed(seed_text or "")
    results = [r for r in (atom_results or []) if isinstance(r, dict)]
    aligned = (
        seed.ok
        and len(results) == len(seed.atoms)
        and all(int(getattr(a, "dell", -1)) == int(r.get("dell", -2))
                for a, r in zip(seed.atoms, results))
    )
    steps = []
    if aligned:
        for i, (atom, r) in enumerate(zip(seed.atoms, results)):
            steps.append({
                "atom": atom.as_mandel(),
                "flow_in": seed.flows[i - 1] if i > 0 else "",
                "status": _status_of(r),
                "reason": str(r.get("reason") or r.get("error") or ""),
            })
    else:
        for r in results:
            steps.append({
                "atom": _dell_text(r.get("dell")),
                "flow_in": "",
                "status": _status_of(r),
                "reason": str(r.get("reason") or r.get("error") or ""),
            })
    return seed, steps, aligned


def _counts(steps: List[Dict[str, Any]]) -> Dict[str, int]:
    out = {"executed": 0, "skipped": 0, "failed": 0}
    for s in steps:
        out[s["status"]] += 1
    return out


def _verdict(steps: List[Dict[str, Any]]) -> str:
    if not steps:
        return "no execution recorded"
    c = _counts(steps)
    if c["executed"] == len(steps):
        word = "complete"
    elif c["executed"] > 0:
        word = "partial"
    else:
        word = "failed"
    return (f"{word} — {c['executed']} executed, "
            f"{c['skipped']} skipped, {c['failed']} failed")


def _chain_line(seed, steps, aligned: bool, seed_text: str,
                highlight: int = -1, mark_done: bool = False) -> str:
    """The chain as one line: atom texts joined by the operators
    exactly as written. With highlight >= 0, that atom is wrapped
    ▸…◂; with mark_done, atoms before the highlight (or all, when
    highlight == len(steps)) carry their status glyph."""
    if not aligned:
        return seed_text or ""
    parts = []
    for i, s in enumerate(steps):
        text = s["atom"]
        if mark_done and (highlight < 0 or i < highlight
                          or highlight == len(steps)):
            text = text + _GLYPH[s["status"]]
        if i == highlight:
            text = f"▸{text}◂"
        if i > 0:
            parts.append(f" {s['flow_in']} {text}")
        else:
            parts.append(text)
    return "".join(parts)


def render_trace(seed_text: str,
                 atom_results: List[Dict[str, Any]]) -> List[str]:
    """Static trace lines: the chain, one line per atom in
    execution order with its outcome, and a verdict footer."""
    seed, steps, aligned = _steps(seed_text, atom_results)
    head = seed.as_mandel() if aligned and seed.atoms else (seed_text or "")
    lines = [f"{_LINK} {head}" if head else f"{_LINK} (empty seed)"]
    for s in steps:
        prefix = f"{s['flow_in']} " if s["flow_in"] else ""
        line = (f"  {prefix}{s['atom']} {_GLYPH[s['status']]} "
                f"{s['status']}")
        if s["reason"] and s["status"] != "executed":
            line += f" ({s['reason']})"
        lines.append(line)
    lines.append(f"■ {_verdict(steps)}")
    return lines


def render_anim(seed_text: str,
                atom_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Preform Anim-shaped frames: frame 0 is the chain at rest;
    each following frame highlights one atom in execution order
    and states its reported outcome; the final frame shows every
    outcome glyph and the verdict. Text frames only — playback
    is a redraw, exactly as the preform model defines."""
    seed, steps, aligned = _steps(seed_text, atom_results)
    frames = []
    if not steps:
        frames.append(f"{seed_text or ''}\n■ no execution recorded")
    elif not aligned:
        frames.append(f"{seed_text or ''}\n"
                      f"{_LINK} execution recorded (unaligned with "
                      f"the seed's atoms)")
        frames.append(f"{seed_text or ''}\n■ {_verdict(steps)}")
    else:
        frames.append(
            f"{_chain_line(seed, steps, True, seed_text)}\n"
            f"{_LINK} chain ready — {len(steps)} atoms")
        for i, s in enumerate(steps):
            line = _chain_line(seed, steps, True, seed_text,
                               highlight=i, mark_done=True)
            status = (f"step {i + 1}/{len(steps)}: {s['atom']} "
                      f"{_GLYPH[s['status']]} {s['status']}")
            if s["reason"] and s["status"] != "executed":
                status += f" ({s['reason']})"
            frames.append(f"{line}\n{status}")
        frames.append(
            f"{_chain_line(seed, steps, True, seed_text, highlight=len(steps), mark_done=True)}\n"
            f"■ {_verdict(steps)}")
    return {
        "id": f"flow:{seed_text[:40]}" if seed_text else "flow:empty",
        "fps": 2,
        "frames": frames,
        "loop": False,
        "aligned": aligned,
        "trace": render_trace(seed_text, atom_results),
    }
