#!/usr/bin/env python3
"""45[Translate] — English → Mandell (phrases first, then patterns)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import re

from .phrases import match_phrase


@dataclass
class Intent:
    action: str
    dell: Optional[int] = None
    term: str = ""
    args: Dict[str, Any] = field(default_factory=dict)
    mandel: str = ""
    english: str = ""


# hint → action used by REPL
_HINT_ACTION = {
    "place": "place",
    "grow": "grow",
    "show": "show",
    "visual": "visual",
    "save": "save",
    "load": "load",
    "walk": "walk",
    "run": "run",
    "stop": "stop",
    "turn_left": "turn",
    "turn_right": "turn",
    "sit": "sit",
    "stand": "stand",
    "jump": "jump",
    "express_joy": "express",
    "express_calm": "express",
    "express_focus": "express",
    "avatar_status": "avatar_status",
    "enhance_on": "enhance_on",
    "enhance_off": "enhance_off",
    "pulse": "pulse",
    "sandbox_on": "sandbox_on",
    "sandbox_off": "sandbox_off",
    "status": "status",
    "help": "help",
    "proposals": "proposals",
    "merge": "place",
    "link": "place",
    "distill": "place",
    "compress": "place",
}


def translate(english: str) -> Intent:
    text = english.strip()
    lower = text.lower().strip()

    # 1) Stable phrase dictionary (preferred)
    hit = match_phrase(text)
    if hit:
        hint = hit["hint"]
        action = _HINT_ACTION.get(hint, "place")
        args: Dict[str, Any] = {}
        if action == "place":
            label = hit.get("label") or "idea"
            uid = re.sub(r"[^a-z0-9]+", "_", label.lower())[:24] or "idea"
            args = {"id": uid, "label": label.replace("_", " "), "words": label}
        elif action == "grow":
            args = {"cycles": 1}
        elif action == "turn":
            args = {"direction": "left" if "left" in hint else "right"}
        elif action == "express":
            expr = "joy"
            if "calm" in hint:
                expr = "calm"
            elif "focus" in hint:
                expr = "focus"
            args = {"expression": expr}
        elif action == "walk":
            args = {"steps": 1}
        return Intent(
            action=action,
            mandel=hit["mandel"],
            english=text,
            args=args,
            term=hint,
        )

    # 2) Fallbacks (same spirit as before)
    if re.search(r"\b(save|keep|persist)(?:\s+session)?\b", lower):
        return Intent("save", 10, "Keep", {}, "10[Keep]", text)
    if re.search(r"\b(load|reload|restore)(?:\s+session)?\b", lower):
        return Intent("load", 28, "Rollback", {}, "28[Rollback] :: load", text)

    if re.search(r"\b(walk|go|move)\s+(forward|ahead)\b", lower) or lower in ("walk", "go forward"):
        return Intent("walk", 19, "Drive", {"steps": 1}, "19[Drive] :: walk", text)
    if re.search(r"\b(run|jog)\b", lower):
        return Intent("run", 19, "Drive", {}, "19[Drive] :: run", text)
    if re.search(r"\b(stop|halt|idle)\b", lower):
        return Intent("stop", 32, "Pause", {}, "32[Pause] :: stop", text)
    if re.search(r"\bturn\s+(left|right)\b", lower):
        d = "left" if "left" in lower else "right"
        return Intent("turn", 4, "Transform", {"direction": d}, f"04[Transform] :: turn_{d}", text)
    if re.search(r"\b(sit|sit\s+down)\b", lower):
        return Intent("sit", 4, "Transform", {}, "04[Transform] :: sit", text)
    if re.search(r"\b(stand|stand\s+up)\b", lower):
        return Intent("stand", 4, "Transform", {}, "04[Transform] :: stand", text)
    if re.search(r"\b(jump)\b", lower):
        return Intent("jump", 4, "Transform", {}, "04[Transform] :: jump", text)

    if re.search(r"\b(smile|happy|joy)\b", lower):
        return Intent("express", 5, "Tone", {"expression": "joy"}, "05[Tone] :: joy", text)
    if re.search(r"\b(calm|relax)\b", lower):
        return Intent("express", 5, "Tone", {"expression": "calm"}, "05[Tone] :: calm", text)
    if re.search(r"\b(focus)\b", lower):
        return Intent("express", 5, "Tone", {"expression": "focus"}, "05[Tone] :: focus", text)
    if re.search(r"\b(how\s+do\s+i\s+look)\b", lower):
        return Intent("avatar_status", 9, "Show", {}, "09[Show] :: avatar", text)

    m = re.search(r"(?:create|add|make|new|place)\s+(?:an?\s+)?(?:idea\s+)?(?:called\s+)?(.+)$", lower)
    if m:
        label = m.group(1).strip().strip("'")
        uid = re.sub(r"[^a-z0-9]+", "_", label.lower())[:24] or "idea"
        return Intent("place", 8, "Create", {"id": uid, "label": label, "words": label},
                      f"08[Create] > 15[Map] :: {uid}", text)

    if re.search(r"\b(grow|evolve)", lower):
        return Intent("grow", 13, "Loop", {"cycles": 1}, "13[Loop] > 04[Transform] :: grow", text)
    if re.search(r"\b(show|display)\b", lower):
        return Intent("show", 9, "Show", {}, "09[Show]", text)
    if re.search(r"\b(visual|workspace)\b", lower):
        return Intent("visual", 9, "Show", {}, "09[Show] >> 47[Embed] :: visual", text)
    if re.search(r"\benhance\s+on\b", lower):
        return Intent("enhance_on", 25, "Pulse", {}, "25[Pulse] :: enhance_on", text)
    if re.search(r"\benhance\s+off\b", lower):
        return Intent("enhance_off", 32, "Pause", {}, "32[Pause] :: enhance_off", text)
    if re.search(r"\bpulse\b", lower):
        return Intent("pulse", 25, "Pulse", {}, "25[Pulse]", text)
    if re.search(r"\bstatus\b", lower):
        return Intent("status", 35, "Discover", {}, "35[Discover]", text)
    if re.search(r"\bhelp\b", lower):
        return Intent("help", 9, "Show", {}, "09[Show] :: help", text)

    uid = "idea_" + str(abs(hash(text)) % 10000)
    return Intent("place", 8, "Create",
                  {"id": uid, "label": text[:48], "words": text},
                  "08[Create] > 15[Map] :: free", text)


def translate_to_mandel(english: str) -> str:
    return translate(english).mandel
