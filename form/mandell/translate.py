#!/usr/bin/env python3
"""
45[Translate] — English → Mandell path

Takes normal English and returns structured Mandell intents
that the runtime can execute.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import re

from .registry import DELLS, lookup
from .manifest import Manifest, manifest_from_dell


@dataclass
class Intent:
    action: str
    dell: Optional[int] = None
    term: str = ""
    args: Dict[str, Any] = None
    mandel: str = ""
    english: str = ""

    def __post_init__(self):
        if self.args is None:
            self.args = {}


# Simple pattern → intent map (expandable)
_PATTERNS = [
    # place / create
    (r"(?:place|add|create|put)\s+(?:an?\s+)?(?:idea\s+)?['\"]?([\w\-]+)['\"]?(?:\s+called\s+['\"]?(.+?)['\"]?)?(?:\s+(.+))?$",
     "place"),
    (r"(?:make|new)\s+(?:an?\s+)?idea\s+['\"]?(.+?)['\"]?$",
     "place_simple"),

    # grow
    (r"(?:grow|evolve|expand)(?:\s+ideas?)?(?:\s+(\d+))?",
     "grow"),

    # show / visual
    (r"(?:show|display|render|visual(?:ize)?)(?:\s+me)?(?:\s+the\s+matrix)?",
     "show"),
    (r"(?:open\s+)?visual(?:\s+workspace)?",
     "visual"),

    # enhance / pulse
    (r"enhance\s+on", "enhance_on"),
    (r"enhance\s+off", "enhance_off"),
    (r"(?:pulse|resonate)", "pulse"),

    # sandbox
    (r"sandbox\s+on", "sandbox_on"),
    (r"sandbox\s+off", "sandbox_off"),

    # save / status
    (r"(?:save|keep|persist)", "save"),
    (r"(?:status|what.?s\s+going\s+on|where\s+am\s+i)", "status"),
    (r"(?:help|what\s+can\s+i\s+do)", "help"),
]


def _extract_dell_mentions(text: str) -> List[Manifest]:
    """Find explicit Dell references like 08[Create] or 'create'."""
    found = []
    for m in re.finditer(r"(\d{1,2})\[([A-Za-z_]+)\]", text):
        n = int(m.group(1))
        man = manifest_from_dell(n, m.group(2))
        if man:
            found.append(man)
    # also try bare names
    for word in re.findall(r"\b([A-Za-z]{3,})\b", text):
        d = lookup(word)
        if d:
            found.append(Manifest(term=d["name"], manor=d["manor"], dell=d["dell"]))
    return found


def translate(english: str) -> Intent:
    """
    Core English → Mandell translation.
    Returns an Intent the runtime can act on.
    """
    text = english.strip()
    lower = text.lower()

    # explicit Mandell already present
    seeds = re.findall(r"\d{1,2}\[[A-Za-z_]+\]", text)
    if seeds and not any(p[0] for p in _PATTERNS if re.search(p[0], lower)):
        return Intent(
            action="raw_mandel",
            mandel=" ".join(seeds),
            english=text,
            args={"seeds": seeds},
        )

    for pattern, action in _PATTERNS:
        m = re.search(pattern, lower, re.I)
        if not m:
            continue

        if action == "place":
            uid = m.group(1) or "idea"
            label = (m.group(2) or uid).strip()
            words = (m.group(3) or "").strip()
            return Intent(
                action="place",
                dell=8,
                term="Create",
                mandel=f"08[Create] > 15[Map] :: {uid}",
                english=text,
                args={"id": uid, "label": label, "words": words},
            )

        if action == "place_simple":
            label = m.group(1).strip()
            uid = re.sub(r"[^a-z0-9]+", "_", label.lower())[:24] or "idea"
            return Intent(
                action="place",
                dell=8,
                term="Create",
                mandel=f"08[Create] > 15[Map] :: {uid}",
                english=text,
                args={"id": uid, "label": label, "words": label},
            )

        if action == "grow":
            n = int(m.group(1)) if m.lastindex and m.group(1) else 1
            return Intent(
                action="grow",
                dell=13,
                term="Loop",
                mandel=f"13[Loop] > 04[Transform] :: grow x{n}",
                english=text,
                args={"cycles": n},
            )

        if action in ("show", "visual"):
            return Intent(
                action=action,
                dell=9,
                term="Show",
                mandel="09[Show] > 15[Map] >> 47[Embed]",
                english=text,
            )

        if action == "enhance_on":
            return Intent(action="enhance_on", dell=25, term="Pulse", mandel="25[Pulse] :: enhance on", english=text)
        if action == "enhance_off":
            return Intent(action="enhance_off", dell=32, term="Pause", mandel="32[Pause] :: enhance off", english=text)
        if action == "pulse":
            return Intent(action="pulse", dell=25, term="Pulse", mandel="25[Pulse]", english=text)
        if action == "sandbox_on":
            return Intent(action="sandbox_on", dell=23, term="Lock", mandel="23[Lock] :: sandbox on", english=text)
        if action == "sandbox_off":
            return Intent(action="sandbox_off", dell=24, term="Unlock", mandel="24[Unlock] :: sandbox off", english=text)
        if action == "save":
            return Intent(action="save", dell=10, term="Keep", mandel="10[Keep]", english=text)
        if action == "status":
            return Intent(action="status", dell=35, term="Discover", mandel="35[Discover]", english=text)
        if action == "help":
            return Intent(action="help", dell=9, term="Show", mandel="09[Show] :: help", english=text)

    # fallback: treat as place with the whole phrase as words
    uid = "idea_" + str(abs(hash(text)) % 10000)
    return Intent(
        action="place",
        dell=8,
        term="Create",
        mandel=f"08[Create] > 15[Map] :: free",
        english=text,
        args={"id": uid, "label": text[:40], "words": text},
    )


def translate_to_mandel(english: str) -> str:
    """Convenience: just return the Mandell string."""
    return translate(english).mandel
