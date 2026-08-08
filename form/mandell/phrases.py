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

    # bare "evolve" is program evolve (see below); "grow" is idea growth
    (r"^(?:grow)(?:\s+ideas?)?(?:\s+(\d+))?$",
     "13[Loop] > 04[Transform] :: grow", "grow"),
    (r"^(?:evolve\s+ideas?)(?:\s+(\d+))?$",
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

    # --- expanded natural English (english_brain feed) ---
    (r"^(?:look|see|vision|look\s+around|scan\s+ahead)$",
     "09[Show] :: look", "look"),
    (r"^(?:live|live\s+visual|open\s+live)$",
     "09[Show] :: live", "live"),
    (r"^(?:evolve|evolve\s+program|grow\s+program|level\s+up)$",
     "13[Loop] :: evolve", "evolve"),
    (r"^(?:audit|pillars|health\s+check|six\s+pillars)$",
     "35[Discover] :: audit", "audit"),
    (r"^(?:matrices|list\s+matrices|matrix\s+list)$",
     "35[Discover] :: matrices", "matrices"),
    (r"^(?:forces|force\s+status|nature\s+forces)$",
     "35[Discover] :: forces", "forces"),
    (r"^(?:force\s+tick|tick\s+forces|forces\s+tick)$",
     "25[Pulse] :: force_tick", "force_tick"),
    (r"^(?:entities|entity\s+list|who'?s\s+here)$",
     "35[Discover] :: entities", "entities"),
    (r"^(?:personas|persona\s+list|agents)$",
     "35[Discover] :: personas", "personas"),
    (r"^(?:guide|guide\s+me|coach)$",
     "09[Show] :: guide", "guide"),
    (r"^(?:rooms|view\s+rooms)$",
     "09[Show] :: rooms", "rooms"),
    (r"^(?:backstep|step\s+back|go\s+back)$",
     "19[Drive] :: backstep", "backstep"),
    (r"^strafe\s+(left|right)$",
     "19[Drive] :: strafe", "strafe"),
    (r"^jog$",
     "19[Drive] :: jog", "jog"),
    (r"^(?:unzoom|zoom\s+out|leave\s+page)$",
     "15[Map] :: unzoom", "unzoom"),
    (r"^zoom\s+(.+)$",
     "15[Map] :: zoom", "zoom"),
    (r"^weather\s+(clear|rain|storm|fog)$",
     "25[Pulse] :: weather", "weather"),
    (r"^(?:english\s+status|english\s+brain)$",
     "35[Discover] :: english_status", "english_status"),
    (r"^(?:english\s+expand)(?:\s+(\d+))?$",
     "13[Loop] :: english_expand", "english_expand"),
    (r"^(?:english\s+help|how\s+to\s+talk)$",
     "09[Show] :: english_help", "english_help"),

    # Inspire pack + end pages + workshops (english_brain feed)
    (r"^(?:page|idea\s+page|end\s+page|open\s+page)$",
     "15[Map] :: page", "page"),
    (r"^(?:home|go\s+home|return\s+home|spawn)$",
     "19[Drive] :: home", "home"),
    (r"^(?:nearest|goto\s+nearest|find\s+nearest)$",
     "19[Drive] :: nearest", "nearest"),
    (r"^(?:multilook|multi[\s-]?look|multi[\s-]?scale)$",
     "09[Show] :: multilook", "multilook"),
    (r"^(?:attend)(?:\s+(.+))?$",
     "09[Show] :: attend", "attend"),
    (r"^(?:slopes|score\s+slopes)$",
     "35[Discover] :: slopes", "slopes"),
    (r"^(?:prefs|preferences|preference\s+ledger)$",
     "35[Discover] :: prefs", "prefs"),
    (r"^(?:glyph)(?:\s+(.+))?$",
     "09[Show] :: glyph", "glyph"),
    (r"^(?:inspire|inspire\s+pack|inspire\s+status)$",
     "35[Discover] :: inspire", "inspire"),
    (r"^(?:workshops|workshop\s+list)$",
     "09[Show] :: workshops", "workshops"),
    (r"^(?:workshop\s+leave|leave\s+workshop)$",
     "32[Pause] :: workshop_leave", "workshop_leave"),
    (r"^(?:workshop\s+(matrix|perspective|mandel|persona|forces|bimo|psalms))$",
     "09[Show] :: workshop", "workshop"),
    (r"^(?:bimo\s+fuse|fuse\s+agents)$",
     "21[Merge] :: bimo_fuse", "bimo_fuse"),
    (r"^(?:bimo\s+defaults|dock\s+defaults)$",
     "14[Bind] :: bimo_defaults", "bimo_defaults"),
    (r"^(?:bimo|bimo\s+status)$",
     "09[Show] :: bimo", "bimo"),
    (r"^(?:geometry|sacred\s+geometry)$",
     "09[Show] :: geometry", "geometry"),
    (r"^(?:verita|verita\s+edges)$",
     "09[Show] :: verita", "verita"),
    (r"^(?:voynich|voynich\s+rings)$",
     "09[Show] :: voynich", "voynich"),
    (r"^(?:fractal|rule\s*90)$",
     "09[Show] :: fractal", "fractal"),
    (r"^(?:rank|rank\s+proposals|rank\s+nursery)$",
     "46[Rank]", "rank"),
    (r"^(?:mode\s+(beginner|builder|depth))$",
     "04[Transform] :: mode", "mode"),
    (r"^(?:view\s+first|first\s+person)$",
     "09[Show] :: view_first", "view_first"),
    (r"^(?:view\s+map|map\s+mode)$",
     "09[Show] :: view_map", "view_map"),
    (r"^(?:ai\s+follow)$", "19[Drive] :: ai_follow", "ai_follow"),
    (r"^(?:ai\s+walk)$", "19[Drive] :: ai_walk", "ai_walk"),
    (r"^(?:ai\s+wander)$", "19[Drive] :: ai_wander", "ai_wander"),
    (r"^(?:ai\s+status)$", "09[Show] :: ai_status", "ai_status"),
    (r"^(?:force\s+(growth|water|breath|gravity))$",
     "25[Pulse] :: force", "force"),
    (r"^(?:recenter|camera\s+home)$",
     "09[Show] :: recenter", "recenter"),
    (r"^(?:lang\s+list|languages|supported\s+languages)$",
     "35[Discover] :: lang_list", "lang_list"),

    # First-person cube-to-cube (Mandell bridge)
    (r"^(?:fp\s+)?(?:step\s+)?forward$",
     "19[Drive] :: fp_forward", "fp_forward"),
    (r"^(?:enter\s+next(?:\s+(?:cell|cube))?|next\s+cube|step\s+into)$",
     "19[Drive] :: fp_forward", "fp_forward"),
    (r"^(?:fp\s+)?(?:step\s+)?back(?:ward)?$|^(?:go\s+back\s+one)$",
     "19[Drive] :: fp_back", "fp_back"),
    (r"^(?:fp\s+)?(?:go\s+)?up$|^(?:ascend|climb)$",
     "19[Drive] :: fp_up", "fp_up"),
    (r"^(?:fp\s+)?(?:go\s+)?down$|^(?:descend)$",
     "19[Drive] :: fp_down", "fp_down"),
    (r"^(?:fp\s+)?turn\s+left$|^(?:face\s+left)$",
     "04[Transform] :: fp_turn_left", "fp_turn_left"),
    (r"^(?:fp\s+)?turn\s+right$|^(?:face\s+right)$",
     "04[Transform] :: fp_turn_right", "fp_turn_right"),
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
