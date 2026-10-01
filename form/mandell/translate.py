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
    "look": "look",
    "live": "live",
    "evolve": "evolve",
    "growth": "growth",
    "ledger": "ledger",
    "discover": "discover",
    # DCC-III: expanded semantic vocabulary
    "measure": "measure",
    "test": "test",
    "architect": "architect",
    "simulate": "simulate",
    "checkpoint": "checkpoint",
    "stamp": "stamp",
    "cycle": "cycle",
    "form": "form",
    "retry": "retry",
    "audit": "audit",
    "matrices": "matrices",
    "forces": "forces",
    "force_tick": "force_tick",
    "entities": "entities",
    "personas": "personas",
    "guide": "guide",
    "rooms": "rooms",
    "backstep": "backstep",
    "strafe": "strafe",
    "jog": "jog",
    "unzoom": "unzoom",
    "zoom": "zoom",
    "weather": "weather",
    "english_status": "english_status",
    "english_expand": "english_expand",
    "english_help": "english_help",
    "form_cube": "form",
    "form_sphere": "form",
    "form_core": "form",
    "form_flower": "form",
    "toggle_form": "toggle_form",
    "lattice": "lattice",
    "fp_forward": "fp_forward",
    "fp_back": "fp_back",
    "fp_up": "fp_up",
    "fp_down": "fp_down",
    "fp_turn_left": "fp_turn_left",
    "fp_turn_right": "fp_turn_right",
    # Nursery confirm/reject (must not fall to place)
    "confirm_all": "confirm_all",
    "reject_all": "reject_all",
    "rank": "rank",
    # Inspire + pages + workshops + geometry
    "page": "page",
    "home": "home",
    "nearest": "nearest",
    "multilook": "multilook",
    "attend": "attend",
    "slopes": "slopes",
    "prefs": "prefs",
    "glyph": "glyph",
    "inspire": "inspire",
    "workshops": "workshops",
    "workshop": "workshop",
    "workshop_leave": "workshop_leave",
    "bimo": "bimo",
    "bimo_fuse": "bimo_fuse",
    "bimo_defaults": "bimo_defaults",
    "geometry": "geometry",
    "verita": "verita",
    "voynich": "voynich",
    "fractal": "fractal",
    "mode": "mode",
    "view_first": "view_first",
    "view_map": "view_map",
    "ai_follow": "ai_follow",
    "ai_walk": "ai_walk",
    "ai_wander": "ai_wander",
    "ai_status": "ai_status",
    "force": "force",
    "recenter": "recenter",
    "lang_list": "lang_list",
}


def translate(english: str) -> Intent:
    text = english.strip()
    # DCC-VI: operational capabilities on RAW text (before english_brain
    # rewrites "add idea X" -> "create an idea called X").
    raw_lower = text.lower().strip()
    if re.search(r"\brevert\b", raw_lower):
        return Intent("load", 28, "Rollback", {}, "28[Rollback] :: load", text)
    if re.search(r"\bcount\s+nursery\b", raw_lower):
        return Intent("discover", 35, "Discover", {}, "35[Discover] :: count_nursery", text)
    if re.search(r"\blist\s+pending\b", raw_lower):
        return Intent("discover", 35, "Discover", {}, "35[Discover] :: list_pending", text)
    if re.search(r"\bcompare\s+nursery\b", raw_lower):
        return Intent("discover", 35, "Discover", {}, "35[Discover] :: compare_nursery", text)
    # DCC-XIV: lineage trace for one knowledge unit (before bare \btrace\b,
    # which would also match "trace lineage <id>" / "trace dependency <id>").
    m = re.search(r"\btrace\s+lineage\s+(\S+)", raw_lower)
    if m:
        return Intent("discover", 35, "Discover", {},
                      f"35[Discover] :: trace_lineage {m.group(1)}", text)
    # DCC-XV: dependency trace — historical lineage + current dependency status.
    m = re.search(r"\btrace\s+dependency\s+(\S+)", raw_lower)
    if m:
        return Intent("discover", 35, "Discover", {},
                      f"35[Discover] :: trace_dependency {m.group(1)}", text)
    # DCC-XVI: revision trace — which accepted version replaces which
    # (revision ancestry, not derivation ancestry).
    m = re.search(r"\btrace\s+revision\s+(\S+)", raw_lower)
    if m:
        return Intent("discover", 35, "Discover", {},
                      f"35[Discover] :: trace_revision {m.group(1)}", text)
    # DCC-XIX: conflict trace — detection evidence + operator disposition
    # for one stable conflict ID (before bare \btrace\b).
    m = re.search(r"\btrace\s+conflict\s+(\S+)", raw_lower)
    if m:
        return Intent("discover", 35, "Discover", {},
                      f"35[Discover] :: trace_conflict {m.group(1)}", text)
    # DCC-XX: outcome trace — one exact outcome by stable ID; list recent
    # outcomes; outcomes involving a specific knowledge ID.
    m = re.search(r"\btrace\s+outcome\s+(\S+)", raw_lower)
    if m:
        return Intent("discover", 35, "Discover", {},
                      f"35[Discover] :: trace_outcome {m.group(1)}", text)
    if re.search(r"\blist\s+outcomes\b", raw_lower):
        return Intent("discover", 35, "Discover", {},
                      "35[Discover] :: list_outcomes", text)
    if re.search(r"\bshow\s+last\s+outcome\b", raw_lower):
        return Intent("discover", 35, "Discover", {},
                      "35[Discover] :: list_outcomes", text)
    m = re.search(r"\boutcomes\s+for\s+idea\s+(\S+)", raw_lower)
    if m:
        return Intent("discover", 35, "Discover", {},
                      f"35[Discover] :: outcomes_for_idea {m.group(1)}", text)
    if re.search(r"\btrace\b", raw_lower):
        return Intent("discover", 35, "Discover", {}, "35[Discover] :: trace", text)
    # DCC-VII: query accepted/promoted knowledge.
    if re.search(r"\blist\s+confirmed\b", raw_lower):
        return Intent("discover", 35, "Discover", {}, "35[Discover] :: list_confirmed", text)
    if re.search(r"\bcount\s+confirmed\b", raw_lower):
        return Intent("discover", 35, "Discover", {}, "35[Discover] :: count_confirmed", text)
    m = re.search(r"\bfind\s+idea\s+(.+)$", raw_lower)
    if m:
        query = m.group(1).strip()[:60]
        if query:
            return Intent("discover", 35, "Discover", {},
                         f"35[Discover] :: find_idea {query}", text)
    # DCC-XVI: versioned supersession — one explicit operation:
    # "supersede idea <old_id> with <new words>". Must precede the
    # "use idea" pattern (both start with an idea verb + id).
    m = re.search(r"\bsupersede\s+idea\s+(\S+)\s+with\s+(.+)$", raw_lower)
    if m:
        old_id = m.group(1).strip()
        words = m.group(2).strip()[:240]
        if old_id and words:
            return Intent("nurture", 37, "Nurture", {},
                         f"37[Nurture] :: supersede {old_id} with {words}", text)
    # DCC-XIX: operator-governed conflict disposition — explicit routing
    # policy for one stable conflict, never a truth claim. Malformed IDs
    # are accepted here and refused honestly by the handler.
    m = re.search(r"\bresolve\s+conflict\s+(\S+)\s+prefer\s+(\S+)", raw_lower)
    if m:
        cid, fav = m.group(1).strip(), m.group(2).strip()
        if cid and fav:
            return Intent("nurture", 37, "Nurture", {},
                         f"37[Nurture] :: resolve_conflict {cid} prefer {fav}", text)
    m = re.search(r"\bresolve\s+conflict\s+(\S+)\s+coexist\b", raw_lower)
    if m:
        cid = m.group(1).strip()
        if cid:
            return Intent("nurture", 37, "Nurture", {},
                         f"37[Nurture] :: resolve_conflict {cid} coexist", text)
    m = re.search(r"\bclear\s+conflict\s+resolution\s+(\S+)", raw_lower)
    if m:
        cid = m.group(1).strip()
        if cid:
            return Intent("nurture", 37, "Nurture", {},
                         f"37[Nurture] :: clear_conflict_resolution {cid}", text)
    # DCC-VIII: explicit knowledge consumption.
    m = re.search(r"\buse\s+idea\s+(\S+)(?:\s+to\s+(\w+))?", raw_lower)
    if m:
        pid = m.group(1).strip()
        target = m.group(2) or "grow"
        if pid:
            return Intent("nurture", 37, "Nurture", {},
                         f"37[Nurture] :: use_idea {pid} to {target}", text)
    # DCC-IX: contextual knowledge selection.
    m = re.search(r"\bgrow\s+using\s+knowledge\s+about\s+(.+)$", raw_lower)
    if m:
        context = m.group(1).strip()[:80]
        if context:
            return Intent("nurture", 37, "Nurture", {},
                         f"37[Nurture] :: grow_using_knowledge_about {context}", text)
    m = re.search(r"\badd\s+idea\s+(.+)$", raw_lower)
    if m:
        label = m.group(1).strip()[:80]
        if not label:
            return Intent("unknown", None, "", {}, "09[Show] :: unknown", text)
        m_orig = re.search(r"\badd\s+idea\s+(.+)$", text, re.IGNORECASE)
        label_orig = m_orig.group(1).strip()[:80] if m_orig else label
        return Intent("nurture", 37, "Nurture", {"label": label_orig},
                      f"37[Nurture] :: {label_orig}", text)
    m = re.search(r"\bconfirm\s+(\S+)$", raw_lower)
    if m:
        pid = m.group(1).strip()
        return Intent("nurture", 37, "Nurture", {"pid": pid, "op": "confirm"},
                      f"37[Nurture] :: confirm {pid}", text)
    m = re.search(r"\breject\s+(\S+)$", raw_lower)
    if m:
        pid = m.group(1).strip()
        return Intent("nurture", 37, "Nurture", {"pid": pid, "op": "reject"},
                      f"37[Nurture] :: reject {pid}", text)
    # English brain: politeness strip + paraphrase + synonym rewrite
    try:
        from form.mandell.english_brain import normalize_english
        normalized, _path = normalize_english(text)
        if normalized:
            text = normalized
    except Exception:
        pass
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
        elif action == "strafe":
            args = {"direction": "left" if "left" in lower else "right"}
        elif action == "zoom":
            args = {"ref": hit.get("label") or ""}
        elif action == "weather":
            m = re.search(r"weather\s+(\w+)", lower)
            args = {"condition": m.group(1) if m else "clear"}
        elif action == "english_expand":
            n = 50
            if hit.get("label") and str(hit["label"]).isdigit():
                n = int(hit["label"])
            args = {"cycles": n}
        elif action == "grow" and hit.get("label") and str(hit["label"]).isdigit():
            args = {"cycles": int(hit["label"])}
        elif action == "form":
            # DCC-III: extract form name from hint (form_sphere) or mandel.
            form_name = "cube"
            if "_" in hint:
                form_name = hint.split("_", 1)[1]
            elif hit.get("mandel"):
                m = re.search(r"15\[Map\] :: (\w+)", hit["mandel"])
                if m:
                    form_name = m.group(1)
            args = {"form": form_name}
        # DCC-III: derive Dell term from mandel for honest semantic reporting.
        # The hint is for action routing; the term is the Dell's canonical name.
        dell_term = hint
        m_term = re.search(r"\[\s*([A-Za-z]+)\s*\]", hit.get("mandel", ""))
        if m_term:
            dell_term = m_term.group(1)
        return Intent(
            action=action,
            mandel=hit["mandel"],
            english=text,
            args=args,
            term=dell_term,
        )

    # 2) Fallbacks (same spirit as before)
    if re.search(r"\b(save|keep|persist)(?:\s+session)?\b", lower):
        return Intent("save", 10, "Keep", {}, "10[Keep]", text)
    if re.search(r"\b(load|reload|restore)(?:\s+session)?\b", lower):
        return Intent("load", 28, "Rollback", {}, "28[Rollback] :: load", text)

    if re.search(r"\b(walk|go|move)\s+(forward|ahead)\b", lower) or lower in ("walk", "go forward"):
        return Intent("walk", 19, "Drive", {"steps": 1}, "19[Drive] :: walk", text)
    if re.search(r"\b(backstep|back\s*step|step\s+back)\b", lower) or lower in ("s", "back"):
        return Intent("backstep", 19, "Drive", {"steps": 1}, "19[Drive] :: backstep", text)
    if re.search(r"\bstrafe\s+(left|right|l|r)\b", lower):
        d = "left" if re.search(r"\bleft\b|\bl\b", lower.split("strafe", 1)[-1]) else "right"
        return Intent("strafe", 19, "Drive", {"direction": d, "steps": 1}, f"19[Drive] :: strafe_{d}", text)
    if re.search(r"\bjog\b", lower):
        return Intent("jog", 19, "Drive", {}, "19[Drive] :: jog", text)
    if re.search(r"\brun\b", lower):
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

    m = re.search(r"(?:create|add|make|new|place|plant)\s+(?:an?\s+)?(?:idea\s+)?(?:called\s+)?(.+)$", lower)
    if m:
        # Keep original casing from text for label body; strong parse happens in handlers
        body = m.group(1).strip().strip("'")
        # strip detail/goals from id slug only
        label_only = re.split(r"\bdetail\s*:|\bgoals\s*:", body, maxsplit=1, flags=re.I)[0].strip()
        uid = re.sub(r"[^a-z0-9]+", "_", label_only.lower())[:24] or "idea"
        return Intent(
            "place",
            8,
            "Create",
            {"id": uid, "label": label_only or body[:48], "words": body[:120], "raw": text},
            f"08[Create] > 15[Map] :: {uid}",
            text,
        )

    if re.search(r"\b(evolve\s+program|grow\s+program|level\s+up)\b", lower) or lower == "evolve":
        return Intent("evolve", 13, "Loop", {}, "13[Loop] :: evolve", text)
    if re.search(r"\bgrow\b", lower) or re.search(r"\bevolve\s+ideas?\b", lower):
        return Intent("grow", 13, "Loop", {"cycles": 1}, "13[Loop] > 04[Transform] :: grow", text)
    # DCC-III: expanded semantic vocabulary (all route through Dell authority).
    # Note: stamp/cycle/form (with args) checked before bare nouns to avoid
    # substring matches (e.g. "test" in "test-mark").
    m = re.search(r"\b(stamp|mark)\s+(.+)$", lower)
    if m:
        mark = m.group(2).strip()[:48] or "mark"
        return Intent("stamp", 34, "Stamp", {"mark": mark}, f"34[Stamp] :: {mark}", text)
    if re.search(r"\b(measure|session\s+weight|how\s+heavy)\b", lower):
        return Intent("measure", 40, "TokenCount", {}, "40[TokenCount]", text)
    if re.search(r"\b(self[\s-]?test|check\s+systems|\btest\b)", lower):
        return Intent("test", 12, "Test", {}, "12[Test]", text)
    if re.search(r"\b(architect|show\s+schema)\b", lower):
        return Intent("architect", 11, "Architect", {}, "11[Architect]", text)
    if re.search(r"\b(simulate|dry[\s-]?run|what\s+would\s+happen)\b", lower):
        return Intent("simulate", 31, "Simulate", {}, "31[Simulate]", text)
    if re.search(r"\b(checkpoint|save\s+a\s+checkpoint|make\s+a\s+checkpoint)\b", lower):
        return Intent("checkpoint", 27, "Checkpoint", {}, "27[Checkpoint]", text)
    m = re.search(r"\b(cycle|run\s+cycles?)\b\s*(\d+)?", lower)
    if m:
        n = int(m.group(2)) if m.group(2) else 1
        n = max(1, min(n, 5))  # Dell 6 caps at 5
        return Intent("cycle", 6, "Cycle", {"count": n}, f"06[Cycle] :: {n}", text)
    m = re.search(r"\bform\s+(cube|sphere|core|flower)\b", lower)
    if m:
        form_name = m.group(1)
        return Intent("form", 15, "Map", {"form": form_name}, f"15[Map] :: {form_name}", text)
    if re.search(r"\b(retry|repeat\s+last)\b", lower):
        return Intent("retry", 42, "Retry", {}, "42[Retry]", text)
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

    # Explicit plant/note without create verb (short noun phrases only when intentional)
    # e.g. "plant Garden Gate" already handled as create synonym via english_brain.
    # Never free-hash unknown text into ideas — that destroys usability.
    return Intent(
        "unknown",
        9,
        "Show",
        {"query": text[:80]},
        "09[Show] :: unknown",
        text,
    )


def translate_to_mandel(english: str) -> str:
    return translate(english).mandel
