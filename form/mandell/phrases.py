#!/usr/bin/env python3
"""Stable Mandell phrase dictionary."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import re

PHRASES: List[Tuple[str, str, str]] = [
    (r"^(?:create|add|make|new)\s+(?:an?\s+)?(?:idea\s+)?(?:called\s+)?(.+)$",
     "08[Create] > 15[Map] :: {label}", "place"),
    (r"^place\s+(.+)$",
     "08[Create] > 15[Map] :: {label}", "place"),

    (r"^(?:grow|evolve)(?:\s+ideas?)?(?:\s+(\d+))?$",
     "13[Loop] > 04[Transform] :: grow", "grow"),

    (r"^(?:show|show\s+me|display)(?:\s+the\s+matrix)?$",
     "09[Show]", "show"),
    (r"^(?:visual|open\s+visual|workspace)$",
     "09[Show] >> 47[Embed] :: visual", "visual"),

    (r"^(?:save|keep|persist)(?:\s+session)?$",
     "10[Keep]", "save"),
    (r"^(?:load|reload|restore)(?:\s+session)?$",
     "28[Rollback] :: load", "load"),

    (r"^(?:walk|go|move)\s*(?:forward|ahead)?(?:\s+(\d+))?$",
     "19[Drive] :: walk", "walk"),
    (r"^run$", "19[Drive] :: run", "run"),
    (r"^(?:stop|halt|idle)$", "32[Pause] :: stop", "stop"),
    (r"^turn\s+left$", "04[Transform] :: turn_left", "turn_left"),
    (r"^turn\s+right$", "04[Transform] :: turn_right", "turn_right"),
    (r"^(?:sit|sit\s+down)$", "04[Transform] :: sit", "sit"),
    (r"^(?:stand|stand\s+up)$", "04[Transform] :: stand", "stand"),
    (r"^jump$", "04[Transform] :: jump", "jump"),

    (r"^(?:smile|happy|joy)$", "05[Tone] :: joy", "express_joy"),
    (r"^(?:calm|relax)$", "05[Tone] :: calm", "express_calm"),
    (r"^(?:focus|concentrate)$", "05[Tone] :: focus", "express_focus"),
    (r"^(?:how\s+do\s+i\s+look|avatar\s+status)$", "09[Show] :: avatar", "avatar_status"),

    (r"^enhance\s+on$", "25[Pulse] :: enhance_on", "enhance_on"),
    (r"^enhance\s+off$", "32[Pause] :: enhance_off", "enhance_off"),
    (r"^pulse$", "25[Pulse]", "pulse"),
    (r"^sandbox\s+on$", "23[Lock] :: sandbox_on", "sandbox_on"),
    (r"^sandbox\s+off$", "24[Unlock] :: sandbox_off", "sandbox_off"),
    (r"^(?:status|where\s+am\s+i)$", "35[Discover]", "status"),
    (r"^(?:help|what\s+can\s+i\s+do)$", "09[Show] :: help", "help"),
    (r"^(?:proposals|nursery|pending)$", "35[Discover] :: nursery", "proposals"),

    (r"^confirm\s+all$", "23[Lock] > 50[Manifest] :: confirm_all", "confirm_all"),
    (r"^reject\s+all$", "24[Unlock] :: reject_all", "reject_all"),

    (r"^(?:cube|form\s+cube|to\s+cube)$", "15[Map] :: cube", "form_cube"),
    (r"^(?:sphere|form\s+sphere|to\s+sphere)$", "15[Map] :: sphere", "form_sphere"),
    (r"^(?:core|form\s+core|to\s+core)$", "15[Map] :: core", "form_core"),
    (r"^(?:flower|form\s+flower|to\s+flower)$", "15[Map] :: flower", "form_flower"),
    (r"^(?:toggle|toggle\s+form|dual)$", "04[Transform] :: toggle_form", "toggle_form"),
    (r"^(?:lattice|show\s+lattice)$", "09[Show] :: lattice", "lattice"),
    (r"^chord(?:\s+(-?\d+)\s+(-?\d+)(?:\s+(-?\d+))?)?$", "35[Discover] :: chord", "chord"),
    (r"^shell(?:\s+(\d+))?$", "35[Discover] :: shell", "shell"),

    (r"^(?:merge|combine)\s+(.+?)\s+(?:and|with)\s+(.+)$",
     "21[Merge] > 14[Bind] :: {label}", "merge"),
    (r"^(?:link|connect)\s+(.+?)\s+(?:to|and|with)\s+(.+)$",
     "07[Link] > 14[Bind] :: {label}", "link"),

    (r"^(?:distill|summarize)(?:\s+(.+))?$",
     "38[Distill] :: {label}", "distill"),
    (r"^(?:compress)\s+(.+)$",
     "29[Compress] :: {label}", "compress"),

    (r"^(?:macro)(?:\s+(\d+))?$",
     "48[Macro] :: {label}", "macro"),
    (r"^(?:replay)(?:\s+(\d+))?$",
     "48[Macro] >> 13[Loop] :: replay", "replay"),
    (r"^(?:rank|rank\s+proposals)$",
     "46[Rank]", "rank"),

    (r"^(?:accept|acceptance|cold\s*start)$",
     "50[Manifest] :: acceptance", "acceptance"),
    (r"^(?:lang\s+list|languages)$",
     "35[Discover] :: lang_list", "lang_list"),
]


def match_phrase(english: str) -> Optional[Dict[str, str]]:
    text = (english or "").strip()
    lower = text.lower().strip()
    for pattern, seed_t, hint in PHRASES:
        m = re.match(pattern, lower, re.I)
        if not m:
            continue
        label = ""
        n = "1"
        if m.lastindex:
            g1 = m.group(1) if m.lastindex >= 1 else ""
            if g1 and g1.isdigit():
                n = g1
                label = g1
            else:
                label = (g1 or "").strip()
            if m.lastindex >= 2:
                g2 = (m.group(2) or "").strip()
                if g2:
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
    return [{"pattern": p, "mandel": s, "hint": h} for p, s, h in PHRASES]
