#!/usr/bin/env python3
"""
45[Translate] — Mandell ↔ English bridge (bidirectional).

Humans may speak English.
Machines prefer seeds.
Both should meet here.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .seed import parse_seed, looks_like_seed, Seed, explain_seed
from .translate import translate, Intent
from .registry import get_dell


def to_english(mandell_or_english: str) -> str:
    """Any input → human-readable English."""
    text = (mandell_or_english or "").strip()
    if not text:
        return ""
    if looks_like_seed(text):
        s = parse_seed(text)
        if s.ok:
            return s.as_english()
        return f"(could not read seed: {s.error})"
    # already english-ish — return as intent english gloss
    intent = translate(text)
    if intent.mandel:
        s = parse_seed(intent.mandel)
        if s.ok:
            return s.as_english()
    return text


def to_mandell(english_or_seed: str) -> str:
    """Any input → Mandell seed string when possible."""
    text = (english_or_seed or "").strip()
    if not text:
        return ""
    if looks_like_seed(text):
        s = parse_seed(text)
        return s.as_mandel() if s.ok else text
    intent = translate(text)
    return intent.mandel or text


def bridge(text: str) -> Dict[str, Any]:
    """Full bridge report: both directions + parse."""
    text = (text or "").strip()
    is_seed = looks_like_seed(text)
    out: Dict[str, Any] = {
        "input": text,
        "looks_like_seed": is_seed,
        "mandel": "",
        "english": "",
        "intent_action": "",
        "ok": True,
    }
    if is_seed:
        info = explain_seed(text)
        out["ok"] = info["ok"]
        out["mandel"] = info["mandel"]
        out["english"] = info["english"]
        out["atoms"] = info.get("atoms")
        if not info["ok"]:
            out["error"] = info["error"]
    else:
        intent = translate(text)
        out["intent_action"] = intent.action
        out["mandel"] = intent.mandel
        out["english"] = to_english(intent.mandel) if intent.mandel else text
        out["args"] = intent.args
    return out
