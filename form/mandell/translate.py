#!/usr/bin/env python3
"""45[Translate] — English → Mandell path (expanded for average users)"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import re

from .registry import lookup
from .manifest import Manifest, manifest_from_dell


@dataclass
class Intent:
    action: str
    dell: Optional[int] = None
    term: str = ""
    args: Dict[str, Any] = field(default_factory=dict)
    mandel: str = ""
    english: str = ""


def translate(english: str) -> Intent:
    text = english.strip()
    lower = text.lower().strip()

    # session
    if re.search(r"\b(save|keep|persist)(?:\s+session)?\b", lower):
        return Intent("save", 10, "Keep", {}, "10[Keep]", text)
    if re.search(r"\b(load|reload|restore)(?:\s+session)?\b", lower):
        return Intent("load", 28, "Rollback", {}, "28[Rollback] :: load", text)

    # movement
    if re.search(r"\b(walk|go|move)\s+(forward|ahead)\b", lower) or lower in ("walk", "go forward", "move forward"):
        steps = 1
        m = re.search(r"(\d+)\s*(steps?|times)?", lower)
        if m:
            steps = int(m.group(1))
        return Intent("walk", 19, "Drive", {"steps": steps}, f"19[Drive] :: walk x{steps}", text)

    if re.search(r"\b(run|jog)\b", lower):
        return Intent("run", 19, "Drive", {}, "19[Drive] :: run", text)
    if re.search(r"\b(stop|stand\s*still|idle|halt)\b", lower):
        return Intent("stop", 32, "Pause", {}, "32[Pause] :: stop", text)
    if re.search(r"\bturn\s+(left|right)\b", lower) or lower in ("turn left", "turn right"):
        direction = "left" if "left" in lower else "right"
        return Intent("turn", 4, "Transform", {"direction": direction}, f"04[Transform] :: turn {direction}", text)
    if re.search(r"\b(face|look)\s+(north|south|east|west|n|s|e|w)\b", lower):
        m = re.search(r"(north|south|east|west|n|s|e|w)\b", lower)
        d = m.group(1) if m else "n"
        return Intent("face", 15, "Map", {"direction": d}, f"15[Map] :: face {d}", text)
    if re.search(r"\b(sit|sit\s+down)\b", lower):
        return Intent("sit", 4, "Transform", {}, "04[Transform] :: sit", text)
    if re.search(r"\b(stand|stand\s+up|get\s+up)\b", lower):
        return Intent("stand", 4, "Transform", {}, "04[Transform] :: stand", text)
    if re.search(r"\b(jump|hop)\b", lower):
        return Intent("jump", 4, "Transform", {}, "04[Transform] :: jump", text)
    if re.search(r"\b(bend|bend\s+over)\b", lower):
        return Intent("bend", 4, "Transform", {}, "04[Transform] :: bend", text)
    if re.search(r"\b(pick\s+up|grab|take)\s+(.+)", lower):
        m = re.search(r"(?:pick\s+up|grab|take)\s+(.+)", lower)
        item = m.group(1).strip() if m else "item"
        return Intent("pick_up", 8, "Create", {"item": item}, f"08[Create] :: pick {item}", text)
    if re.search(r"\b(put\s+down|place\s+down|drop)\b", lower):
        return Intent("place_down", 9, "Show", {}, "09[Show] :: place down", text)

    # face
    if re.search(r"\b(smile|happy|joy)\b", lower):
        return Intent("express", 5, "Tone", {"expression": "joy"}, "05[Tone] :: joy", text)
    if re.search(r"\b(frown|mad|intense|serious)\b", lower):
        return Intent("express", 5, "Tone", {"expression": "intense"}, "05[Tone] :: intense", text)
    if re.search(r"\b(calm|relax|chill)\b", lower):
        return Intent("express", 5, "Tone", {"expression": "calm"}, "05[Tone] :: calm", text)
    if re.search(r"\b(curious|wonder|hmm)\b", lower):
        return Intent("express", 5, "Tone", {"expression": "curious"}, "05[Tone] :: curious", text)
    if re.search(r"\b(focus|concentrate)\b", lower):
        return Intent("express", 5, "Tone", {"expression": "focus"}, "05[Tone] :: focus", text)
    if re.search(r"\b(soft|gentle|kind)\b", lower):
        return Intent("express", 5, "Tone", {"expression": "soft"}, "05[Tone] :: soft", text)
    if re.search(r"\b(neutral|normal|reset\s+face)\b", lower):
        return Intent("express", 5, "Tone", {"expression": "neutral"}, "05[Tone] :: neutral", text)
    if re.search(r"\b(show\s+face|what\s+do\s+i\s+look\s+like|avatar\s+status|how\s+do\s+i\s+look)\b", lower):
        return Intent("avatar_status", 9, "Show", {}, "09[Show] :: avatar", text)

    # ideas
    m = re.search(r"(?:create|add|make|new|place)\s+(?:an?\s+)?(?:idea\s+)?(?:called\s+)?['\"]?([^'\"]+)['\"]?$", lower)
    if m or re.search(r"^(?:create|add|make)\s+.+", lower):
        label = m.group(1).strip() if m else re.sub(r"^(?:create|add|make|new|place)\s+(?:an?\s+)?(?:idea\s+)?", "", lower).strip()
        label = label.strip("'")
        uid = re.sub(r"[^a-z0-9]+", "_", label.lower())[:24] or "idea"
        return Intent("place", 8, "Create", {"id": uid, "label": label, "words": label}, f"08[Create] > 15[Map] :: {uid}", text)

    if re.search(r"\b(grow|evolve|expand)(?:\s+ideas?)?(?:\s+(\d+))?", lower):
        m = re.search(r"(\d+)", lower)
        n = int(m.group(1)) if m else 1
        return Intent("grow", 13, "Loop", {"cycles": n}, f"13[Loop] > 04[Transform] :: grow x{n}", text)

    if re.search(r"\b(show|display|render|see)\s*(me)?\s*(the\s+)?(matrix|everything|it)?\b", lower) or lower in ("show", "show me"):
        return Intent("show", 9, "Show", {}, "09[Show]", text)
    if re.search(r"\b(visual|open\s+visual|workspace|see\s+it)\b", lower):
        return Intent("visual", 9, "Show", {}, "09[Show] > 47[Embed] :: visual", text)

    if re.search(r"\benhance\s+on\b", lower):
        return Intent("enhance_on", 25, "Pulse", {}, "25[Pulse] :: enhance on", text)
    if re.search(r"\benhance\s+off\b", lower):
        return Intent("enhance_off", 32, "Pause", {}, "32[Pause] :: enhance off", text)
    if re.search(r"\b(pulse|resonate)\b", lower):
        return Intent("pulse", 25, "Pulse", {}, "25[Pulse]", text)
    if re.search(r"\bsandbox\s+on\b", lower):
        return Intent("sandbox_on", 23, "Lock", {}, "23[Lock] :: sandbox on", text)
    if re.search(r"\bsandbox\s+off\b", lower):
        return Intent("sandbox_off", 24, "Unlock", {}, "24[Unlock] :: sandbox off", text)
    if re.search(r"\b(status|what.?s\s+going\s+on|where\s+am\s+i|what.?s\s+happening)\b", lower):
        return Intent("status", 35, "Discover", {}, "35[Discover]", text)
    if re.search(r"\b(help|what\s+can\s+i\s+do|commands)\b", lower):
        return Intent("help", 9, "Show", {}, "09[Show] :: help", text)

    uid = "idea_" + str(abs(hash(text)) % 10000)
    return Intent("place", 8, "Create", {"id": uid, "label": text[:48], "words": text}, "08[Create] > 15[Map] :: free", text)


def translate_to_mandel(english: str) -> str:
    return translate(english).mandel
