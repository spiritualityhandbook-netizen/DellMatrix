#!/usr/bin/env python3
"""
Stable Mandell phrase dictionary.

Common human intents → canonical Mandell seeds.
This is the teachable surface for everyday use.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import re

# (pattern, seed_template, action_hint)
# Templates may use {label} {n}
PHRASES: List[Tuple[str, str, str]] = [
    # create / place
    (r"^(?:create|add|make|new)\s+(?:an?\s+)?(?:idea\s+)?(?:called\s+)?(.+)$",
     "08[Create] > 15[Map] :: {label}", "place"),
    (r"^place\s+(.+)$",
     "08[Create] > 15[Map] :: {label}", "place"),

    # grow / evolve
    (r"^(?:grow|evolve)(?:\s+ideas?)?(?:\s+(\d+))?$",
     "13[Loop] > 04[Transform] :: grow",
     "grow"),

    # show / visual
    (r"^(?:show|show\s+me|display)(?:\s+the\s+matrix)?$",
     "09[Show]", "show"),
    (r"^(?:visual|open\s+visual|workspace)$",
     "09[Show] >> 47[Embed] :: visual", "visual"),

    # save / load
    (r"^(?:save|keep|persist)(?:\s+session)?$",
     "10[Keep]", "save"),
    (r"^(?:load|reload|restore)(?:\s+session)?$",
     "28[Rollback] :: load", "load"),

    # movement
    (r"^(?:walk|go|move)\s*(?:forward|ahead)?(?:\s+(\d+))?$",
     "19[Drive] :: walk", "walk"),
    (r"^run$", "19[Drive] :: run", "run"),
    (r"^(?:stop|halt|idle)$", "32[Pause] :: stop", "stop"),
    (r"^turn\s+left$", "04[Transform] :: turn_left", "turn_left"),
    (r"^turn\s+right$", "04[Transform] :: turn_right", "turn_right"),
    (r"^(?:sit|sit\s+down)$", "04[Transform] :: sit", "sit"),
    (r"^(?:stand|stand\s+up)$", "04[Transform] :: stand", "stand"),
    (r"^jump$", "04[Transform] :: jump", "jump"),

    # tone / face
    (r"^(?:smile|happy|joy)$", "05[Tone] :: joy", "express_joy"),
    (r"^(?:calm|relax)$", "05[Tone] :: calm", "express_calm"),
    (r"^(?:focus|concentrate)$", "05[Tone] :: focus", "express_focus"),
    (r"^(?:how\s+do\s+i\s+look|avatar\s+status)$", "09[Show] :: avatar", "avatar_status"),

    # system
    (r"^enhance\s+on$", "25[Pulse] :: enhance_on", "enhance_on"),
    (r"^enhance\s+off$", "32[Pause] :: enhance_off", "enhance_off"),
    (r"^pulse$", "25[Pulse]", "pulse"),
    (r"^sandbox\s+on$", "23[Lock] :: sandbox_on", "sandbox_on"),
    (r"^sandbox\s+off$", "24[Unlock] :: sandbox_off", "sandbox_off"),
    (r"^(?:status|where\s+am\s+i)$", "35[Discover]", "status"),
    (r"^(?:help|what\s+can\s+i\s+do)$", "09[Show] :: help", "help"),
    (r"^(?:proposals|nursery|pending)$", "35[Discover] :: nursery", "proposals"),

    # merge / link ideas (language-forward)
    (r"^(?:merge|combine)\s+(.+?)\s+(?:and|with)\s+(.+)$",
     "21[Merge] > 14[Bind] :: {label}", "merge"),
    (r"^(?:link|connect)\s+(.+?)\s+(?:to|and|with)\s+(.+)$",
     "07[Link] > 14[Bind] :: {label}", "link"),

    # distill / compress
    (r"^(?:distill|summarize)\s+(.+)$",
     "38[Distill] :: {label}", "distill"),
    (r"^(?:compress)\s+(.+)$",
     "29[Compress] :: {label}", "compress"),
]


def match_phrase(english: str) -> Optional[Dict[str, str]]:
    """Match English to a stable Mandell phrase."""
    text = (english or "").strip()
    lower = text.lower().strip()
    for pattern, seed_t, hint in PHRASES:
        m = re.match(pattern, lower, re.I)
        if not m:
            continue
        label = ""
        n = "1"
        if m.lastindex:
            # last group often label or count
            g1 = m.group(1) if m.lastindex >= 1 else ""
            if g1 and g1.isdigit():
                n = g1
            else:
                label = (g1 or "").strip()
            if m.lastindex >= 2:
                g2 = m.group(2).strip()
                label = f"{label}_x_{g2}".strip("_")
        label = label or "item"
        seed = seed_t.replace("{label}", label.replace(" ", "_")[:40]).replace("{n}", n)
        return {
            "english": text,
            "mandel": seed,
            "hint": hint,
            "label": label,
        }
    return None


def list_phrases() -> List[Dict[str, str]]:
    """Teachable list for humans."""
    out = []
    for pattern, seed, hint in PHRASES:
        out.append({"pattern": pattern, "mandel": seed, "hint": hint})
    return out
