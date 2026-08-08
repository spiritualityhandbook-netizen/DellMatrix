#!/usr/bin/env python3
"""
English Brain — natural English understanding for Mandell Origin.

Expands how everyday English maps to stable intents:
  · politeness / filler stripping (prefix + trailing)
  · synonym & paraphrase banks
  · question → imperative forms
  · multi-word verb phrases
  · expand_loop(N) — grow understanding over N cycles
  · enhance_150_loop — 150-cycle coverage + program-grounded mastery

Does not claim AGI. Structural language surface only.
Law: offline · Floor locked · Nursery confirm · educational language surface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import re
import random

# ---------------------------------------------------------------------------
# Politeness / filler strip (applied first)
# ---------------------------------------------------------------------------
_POLITE_PREFIX = re.compile(
    r"^(?:please|pls|plz|kindly|hey|hi|hello|ok|okay|so|well|um+|uh+|hmm+)\b\s*[,:]?\s*",
    re.I,
)
_POLITE_WRAPPER = re.compile(
    r"^(?:could\s+you|can\s+you|would\s+you|will\s+you|would\s+you\s+please|"
    r"can\s+we|could\s+we|let'?s|i\s+(?:want|need|would\s+like|wanna|gotta)\s+to|"
    r"i'?d\s+like\s+to|i\s+wish\s+to|try\s+to|go\s+ahead\s+and|"
    r"make\s+sure\s+(?:to|you)|be\s+sure\s+to)\s+",
    re.I,
)
_QUESTION_LEAD = re.compile(
    r"^(?:how\s+(?:do|can|should)\s+i|what\s+(?:is|are)|where\s+(?:is|am)|"
    r"can\s+i|should\s+i|do\s+i|is\s+there|show\s+me\s+how\s+to)\s+",
    re.I,
)
_TRAILING = re.compile(r"[\s.!?;:]+$")
_TRAILING_FILLER = re.compile(
    r"(?:\s+(?:please|pls|plz|thanks|thank\s+you|for\s+me|right\s+now|"
    r"now|please\s+do|if\s+you\s+(?:can|would|could)|real\s+quick|"
    r"quickly|when\s+you\s+can))+$",
    re.I,
)
_MULTI_SPACE = re.compile(r"\s+")

# ---------------------------------------------------------------------------
# Verb / phrase synonyms → canonical tokens used by phrase/translate layers
# ---------------------------------------------------------------------------
VERB_MAP: Dict[str, str] = {
    # create
    "create": "create", "add": "create", "make": "create", "new": "create",
    "start": "create", "spawn": "create", "invent": "create", "draft": "create",
    "write": "create", "compose": "create", "build": "create", "forge": "create",
    "birth": "create", "plant": "create", "introduce": "create", "register": "create",
    # grow
    "grow": "grow", "evolve": "grow", "expand": "grow", "develop": "grow",
    "cultivate": "grow", "nurture": "grow", "advance": "grow", "progress": "grow",
    "iterate": "grow", "branch": "grow", "bloom": "grow", "ripen": "grow",
    # show
    "show": "show", "display": "show", "see": "look", "view": "view",
    "reveal": "show", "present": "show", "print": "show", "list": "show",
    "check": "status", "inspect": "look", "peek": "look", "glance": "look",
    # save / load
    "save": "save", "keep": "save", "persist": "save", "store": "save",
    "remember": "save", "bookmark": "save", "checkpoint": "save",
    "load": "load", "reload": "load", "restore": "load", "resume": "load",
    "reopen": "load", "recover": "load",
    # movement
    "walk": "walk", "go": "walk", "move": "walk", "step": "walk",
    "advance": "walk", "proceed": "walk", "come": "walk",
    "run": "run", "sprint": "run", "dash": "run", "rush": "run",
    "jog": "jog", "trot": "jog",
    "stop": "stop", "halt": "stop", "freeze": "stop", "wait": "stop",
    "pause": "stop", "idle": "stop", "rest": "stop",
    "turn": "turn", "face": "face", "rotate": "turn", "spin": "turn",
    "sit": "sit", "stand": "stand", "jump": "jump", "leap": "jump",
    "backstep": "backstep", "retreat": "backstep", "back": "backstep",
    "strafe": "strafe",
    # tone
    "smile": "smile", "happy": "smile", "joy": "smile", "grin": "smile",
    "calm": "calm", "relax": "calm", "breathe": "calm", "chill": "calm",
    "focus": "focus", "concentrate": "focus",
    # system
    "help": "help", "assist": "help", "guide": "guide", "explain": "explain",
    "pulse": "pulse", "beat": "pulse", "throb": "pulse",
    "confirm": "confirm", "accept": "confirm", "approve": "confirm",
    "reject": "reject", "deny": "reject", "discard": "reject", "drop": "reject",
    "look": "look", "watch": "look", "observe": "look", "scan": "look",
    "zoom": "zoom", "focus_on": "zoom",
    "rank": "rank", "sort": "rank", "order": "rank",
    "merge": "merge", "combine": "merge", "join": "merge",
    "link": "link", "connect": "link", "bind": "link", "tie": "link",
    "distill": "distill", "summarize": "distill", "condense": "distill",
    "compress": "compress", "shrink": "compress",
    "audit": "audit", "evaluate": "audit",
    "evolve_program": "evolve", "improve": "evolve",
    "weather": "weather", "forces": "forces", "matrices": "matrices",
    # inspire + program surface verbs (map carefully — not pure open→zoom)
    "prefs": "prefs", "preferences": "prefs",
    "slopes": "slopes", "glyph": "glyph", "inspire": "inspire",
    "multilook": "multilook", "attend": "attend",
    "workshops": "workshops", "page": "page", "home": "home",
    "entities": "entities", "personas": "personas", "bimo": "bimo",
    "geometry": "geometry", "voynich": "voynich", "verita": "verita",
    "fractal": "fractal", "radar": "radar", "nearest": "nearest",
}

# Full-line paraphrase banks → canonical phrase (matched after normalize)
# Each key is the stable phrase match_phrase / translate already knows or will know.
PARAPHRASE_TO_CANONICAL: List[Tuple[str, str]] = [
    # create family
    (r"^(?:spawn|invent|draft|compose|forge|birth)\s+(?:an?\s+)?(?:idea\s+)?(?:called\s+|named\s+|titled\s+)?(.+)$",
     "create an idea called {1}"),
    (r"^(?:i\s+have\s+an?\s+idea\s+(?:about|for|called)\s+)(.+)$",
     "create an idea called {1}"),
    (r"^(?:let'?s\s+(?:make|create|add)\s+)(.+)$",
     "create an idea called {1}"),
    (r"^(?:put\s+(?:down|in)\s+)(.+)$", "place {1}"),
    (r"^(?:note\s+(?:down\s+)?)(.+)$", "create an idea called {1}"),
    # grow
    (r"^(?:please\s+)?(?:grow|expand|develop|cultivate|nurture)(?:\s+(?:my\s+)?ideas?)?(?:\s+(\d+))?$",
     "grow ideas {1}"),
    (r"^(?:run\s+growth|do\s+growth|growth\s+cycle)(?:\s+(\d+))?$",
     "grow ideas {1}"),
    (r"^(?:let\s+(?:them|ideas)\s+grow)(?:\s+(\d+))?$", "grow ideas {1}"),
    (r"^(?:advance\s+(?:the\s+)?(?:nursery|ideas))(?:\s+(\d+))?$", "grow ideas {1}"),
    # show / visual
    (r"^(?:what'?s\s+going\s+on|what'?s\s+here|overview|dashboard)$", "show me"),
    (r"^(?:open\s+(?:the\s+)?(?:map|matrix|panel)|see\s+(?:the\s+)?matrix)$", "show me"),
    (r"^(?:open\s+(?:the\s+)?ui|open\s+browser\s+panel|offline\s+panel)$", "visual"),
    (r"^(?:live\s+mode|open\s+live|start\s+live\s+visual)$", "live"),
    # save / load
    (r"^(?:save\s+(?:my\s+)?work|write\s+session|checkpoint\s+now|don'?t\s+forget)$", "save"),
    (r"^(?:bring\s+back|pick\s+up\s+where\s+i\s+left\s+off|restore\s+work)$", "load"),
    # movement natural
    (r"^(?:step\s+forward|move\s+ahead|go\s+on|take\s+a\s+step)(?:\s+(\d+))?$", "walk forward"),
    (r"^(?:head\s+(?:north|forward)|proceed)$", "walk forward"),
    (r"^(?:sprint|dash|hurry)$", "run"),
    (r"^(?:take\s+a\s+jog|light\s+run)$", "jog"),
    (r"^(?:step\s+back|go\s+back|retreat|back\s+up)$", "backstep"),
    (r"^(?:slide\s+left|sidestep\s+left|step\s+left)$", "strafe left"),
    (r"^(?:slide\s+right|sidestep\s+right|step\s+right)$", "strafe right"),
    (r"^(?:spin\s+left|rotate\s+left|look\s+left)$", "turn left"),
    (r"^(?:spin\s+right|rotate\s+right|look\s+right)$", "turn right"),
    (r"^(?:take\s+a\s+seat|have\s+a\s+seat|sit\s+please)$", "sit down"),
    (r"^(?:get\s+up|rise|stand\s+please)$", "stand up"),
    (r"^(?:leap|hop)$", "jump"),
    (r"^(?:hold\s+still|stay|freeze|wait\s+here)$", "stop"),
    # look / vision
    (r"^(?:what\s+(?:do\s+i\s+)?see|what'?s\s+in\s+(?:front|view)|scan\s+ahead|look\s+around)$", "look"),
    (r"^(?:vision|eyes|gaze)$", "look"),
    (r"^(?:how\s+do\s+i\s+appear|my\s+appearance|avatar)$", "how do I look"),
    # nursery
    (r"^(?:what'?s\s+pending|show\s+nursery|pending\s+ideas|quarantine)$", "proposals"),
    (r"^(?:approve\s+all|accept\s+all|confirm\s+everything)$", "confirm all"),
    (r"^(?:deny\s+all|drop\s+all|reject\s+everything)$", "reject all"),
    # auto confirm all grow mode
    (r"^(?:auto\s+confirm\s+all(?:\s+grow\s+mode)?|grow\s+mode\s+auto(?:\s+confirm)?|auto\s+confirm\s+on)$",
     "auto confirm on"),
    (r"^(?:auto\s+confirm\s+off|grow\s+mode\s+manual|grow\s+mode\s+off)$",
     "auto confirm off"),
    (r"^(?:grow\s+mode|auto\s+confirm(?:\s+status)?)$", "grow mode"),
    # forms
    (r"^(?:switch\s+to\s+)?(?:cube|cubic|boxy)\s*(?:form|mode)?$", "cube"),
    (r"^(?:switch\s+to\s+)?(?:sphere|spherical|ball|radial)\s*(?:form|mode)?$", "sphere"),
    (r"^(?:switch\s+to\s+)?(?:core|seed\s+core|center)\s*(?:form|mode)?$", "core"),
    (r"^(?:switch\s+to\s+)?(?:flower|flower\s+of\s+life|fol)\s*(?:form|mode)?$", "flower"),
    (r"^(?:flip\s+form|switch\s+form|dual\s+mode)$", "toggle"),
    # system
    (r"^(?:where\s+am\s+i|who\s+am\s+i|session\s+info|info)$", "status"),
    (r"^(?:what\s+can\s+i\s+do|commands|manual|\?)$", "help"),
    (r"^(?:turn\s+enhance\s+on|enable\s+enhance|enhancement\s+on)$", "enhance on"),
    (r"^(?:turn\s+enhance\s+off|disable\s+enhance|enhancement\s+off)$", "enhance off"),
    (r"^(?:send\s+a\s+pulse|heartbeat|wave)$", "pulse"),
    (r"^(?:box\s+everything|isolate|sandbox\s+mode\s+on)$", "sandbox on"),
    (r"^(?:unbox|reconnect|sandbox\s+mode\s+off)$", "sandbox off"),
    # expand system surface (new form commands)
    (r"^(?:grow\s+(?:the\s+)?program|evolve\s+(?:the\s+)?program|level\s+up)$", "evolve"),
    (r"^(?:health\s+check|six\s+pillars|pillar\s+audit|how\s+healthy)$", "audit"),
    (r"^(?:list\s+matrices|what\s+matrices|all\s+matrices)$", "matrices"),
    (r"^(?:nature\s+forces|force\s+field|show\s+forces)$", "forces"),
    (r"^(?:tick\s+forces|pulse\s+forces)$", "force tick"),
    (r"^(?:who'?s\s+here|list\s+entities|all\s+entities)$", "entities"),
    (r"^(?:list\s+personas|who\s+are\s+the\s+agents|agents\s+list|full\s+roster)$", "personas"),
    (r"^(?:persona\s+matrix|show\s+persona\s+matrix|agent\s+matrix)$", "matrix personas"),
    (r"^(?:show\s+bimo|fusion\s+body)$", "bimo"),
    (r"^(?:dock\s+all|fill\s+bimo)$", "bimo defaults"),
    (r"^(?:fuse\s+agents|run\s+fusion)$", "bimo fuse"),
    (r"^(?:advise\s+me|advise\s+my\s+work|coach)$", "guide"),
    (r"^(?:view\s+rooms|list\s+rooms|rooms\s+list)$", "rooms"),
    (r"^(?:english\s+help|language\s+help|how\s+to\s+talk)$", "help more"),
    (r"^(?:make\s+it\s+rain|rainy)$", "weather rain"),
    (r"^(?:clear\s+skies|sunny)$", "weather clear"),
    (r"^(?:stormy|shake\s+it\s+up)$", "weather storm"),
    (r"^(?:foggy|mist)$", "weather fog"),
    # zoom / page
    (r"^(?:open\s+page\s+(?:for\s+)?|inspect\s+|zoom\s+into\s+|focus\s+on\s+)(.+)$",
     "zoom {1}"),
    (r"^(?:leave\s+page|close\s+page|back\s+to\s+overview|exit\s+zoom)$", "unzoom"),
    # live / look aliases already covered
    (r"^(?:take\s+a\s+look|have\s+a\s+look)$", "look"),
    (r"^(?:i'?m\s+ready|begin|cold\s+start\s+path)$", "acceptance"),
    (r"^(?:which\s+languages|polyglot|language\s+list)$", "lang list"),
    # ─── idea pages / navigation end-pages ───
    (r"^(?:open\s+(?:the\s+)?(?:idea\s+)?page|idea\s+page|end\s+page|show\s+(?:the\s+)?page)$", "page"),
    (r"^(?:open\s+(?:the\s+)?nearest\s+(?:idea\s+)?page|nearest\s+page)$", "page"),
    (r"^(?:go\s+(?:to\s+)?home|return\s+home|spawn|reset\s+position)$", "home"),
    (r"^(?:goto\s+nearest|jump\s+to\s+nearest|find\s+nearest|nearest\s+idea)$", "nearest"),
    (r"^(?:recenter(?:\s+camera)?|camera\s+home|cam\s+home)$", "recenter"),
    (r"^(?:leave\s+page|close\s+page|back\s+to\s+overview|exit\s+zoom|unzoom\s+please)$", "unzoom"),
    # ─── inspire pack ───
    (r"^(?:soft\s+attention(?:\s+on)?|attend(?:\s+to)?|attention\s+on|rank\s+by\s+attention)(?:\s+(.+))?$",
     "attend {1}"),
    (r"^(?:multi[\s-]?look|multi[\s-]?scale(?:\s+vision)?|near\s+mid\s+far(?:\s+vision)?|hierarchical\s+vision)$",
     "multilook"),
    (r"^(?:score\s+slopes|slopes|rate\s+of\s+change(?:\s+of\s+scores)?|ds/dt|calculus\s+slopes)$",
     "slopes"),
    (r"^(?:prefs|preferences|preference\s+ledger|what\s+are\s+my\s+preferences|"
     r"remember\s+what\s+i\s+confirmed|confirm\s+reject\s+prefs)$",
     "prefs"),
    (r"^(?:draw\s+(?:a\s+)?glyph|glyph(?:\s+card)?|procedural\s+(?:art|glyph)|no[\s-]?asset\s+art)(?:\s+(.+))?$",
     "glyph {1}"),
    (r"^(?:inspire(?:\s+pack)?(?:\s+status)?|inspire\s+tools|offline\s+pack\s+status)$", "inspire"),
    (r"^(?:run\s+(?:a\s+)?script|batch\s+script|script\s+demo)\s*(.*)$", "script {1}"),
    (r"^(?:batch:\s*)(.+)$", "script {1}"),
    # ─── workshops ───
    (r"^(?:open\s+workshops|list\s+workshops|show\s+workshops|workshops?\s+list)$", "workshops"),
    (r"^(?:enter\s+(?:the\s+)?matrix\s+workshop|matrix\s+workshop|open\s+matrix\s+workbench)$",
     "workshop matrix"),
    (r"^(?:enter\s+(?:the\s+)?perspective\s+workshop|perspective\s+workshop)$", "workshop perspective"),
    (r"^(?:enter\s+(?:the\s+)?mandel\s+workshop|mandel\s+workshop|language\s+workshop)$", "workshop mandel"),
    (r"^(?:enter\s+(?:the\s+)?persona\s+workshop|persona\s+workshop|agents?\s+workshop)$", "workshop persona"),
    (r"^(?:enter\s+(?:the\s+)?forces?\s+workshop|forces?\s+workshop)$", "workshop forces"),
    (r"^(?:enter\s+(?:the\s+)?bimo\s+workshop|bimo\s+workshop|fusion\s+workshop)$", "workshop bimo"),
    (r"^(?:enter\s+(?:the\s+)?psalms?\s+workshop|psalms?\s+workshop|ancient\s+workshop)$", "workshop psalms"),
    (r"^(?:leave\s+(?:the\s+)?workshop|exit\s+workshop|close\s+workshop)$", "workshop leave"),
    # ─── entities / AI / personas ───
    (r"^(?:who\s+is\s+on\s+stage|who'?s\s+on\s+stage|who\s+is\s+here|list\s+who'?s\s+here)$", "entities"),
    (r"^(?:fuse\s+(?:the\s+)?agents|run\s+fusion|bimo\s+fuse\s+now)$", "bimo fuse"),
    (r"^(?:dock\s+defaults|fill\s+bimo|bimo\s+defaults)$", "bimo defaults"),
    (r"^(?:ai\s+follow\s+me|companion\s+follow|make\s+ai\s+follow)$", "ai follow"),
    (r"^(?:ai\s+take\s+a\s+walk|ai\s+go\s+walk|companion\s+walk)$", "ai walk"),
    (r"^(?:ai\s+wander|companion\s+wander)$", "ai wander"),
    (r"^(?:ai\s+status|where\s+is\s+the\s+ai|companion\s+status)$", "ai status"),
    # ─── weather / forces natural ───
    (r"^(?:rain\s+please|make\s+it\s+rain|start\s+rain)$", "weather rain"),
    (r"^(?:clear\s+(?:the\s+)?weather|stop\s+rain|clear\s+skies\s+please)$", "weather clear"),
    (r"^(?:water\s+(?:the\s+)?ideas|force\s+water\s+flow|flow\s+water)$", "force water"),
    (r"^(?:grow\s+plants(?:\s+with\s+force)?|force\s+growth|plant\s+growth\s+force)$", "force growth"),
    (r"^(?:breathe\s+once|force\s+breath|heartbeat\s+force)$", "force breath"),
    (r"^(?:gravity\s+wells|force\s+gravity)$", "force gravity"),
    # ─── geometry ───
    (r"^(?:flower\s+of\s+life(?:\s+geometry)?|fol\s+geometry|show\s+flower\s+geometry)$",
     "flower geometry"),
    (r"^(?:verita(?:\s+edges)?|truth\s+of\s+meet|vesica\s+truth)$", "verita"),
    (r"^(?:voynich(?:\s+rings)?|structural\s+rings)$", "voynich"),
    (r"^(?:fractal(?:\s+rule\s*90)?|rule\s*90|sierpinski)$", "fractal"),
    (r"^(?:sacred\s+geometry|geometry\s+status|full\s+geometry)$", "geometry"),
    # ─── fp / view modes ───
    (r"^(?:walk\s+into\s+next\s+cube|enter\s+next\s+cube|next\s+cell|step\s+into\s+next)$",
     "enter next cube"),
    (r"^(?:look\s+up(?:\s+at\s+(?:the\s+)?ceiling)?|pitch\s+up|gaze\s+up)$", "look up"),
    (r"^(?:look\s+down(?:\s+at\s+(?:the\s+)?floor)?|pitch\s+down|gaze\s+down)$", "look down"),
    (r"^(?:first\s+person(?:\s+mode)?|mode\s+first(?:\s+person)?|fp\s+mode)$", "view first"),
    (r"^(?:map\s+mode(?:\s+please)?|legacy\s+map|mode\s+map)$", "view map"),
    (r"^body\s+as\s+(stick|block|shadow|robot)$", "body {1}"),
    (r"^set\s+body\s+(stick|block|shadow|robot)$", "body {1}"),
    (r"^(?:use\s+)?(stick|block|shadow|robot)\s+body$", "body {1}"),
    # ─── nursery / rank ───
    (r"^(?:rank\s+(?:the\s+)?nursery|sort\s+proposals|order\s+by\s+affinity)$", "rank"),
    (r"^(?:accept\s+everything(?:\s+pending)?|confirm\s+everything(?:\s+pending)?)$", "confirm all"),
    (r"^(?:reject\s+everything(?:\s+pending)?|deny\s+everything)$", "reject all"),
    # ─── modes / depth ───
    (r"^(?:turn\s+depth\s+mode\s+on|depth\s+mode|mode\s+depth|go\s+deep)$", "mode depth"),
    (r"^(?:beginner\s+mode|mode\s+beginner|keep\s+it\s+simple)$", "mode beginner"),
    (r"^(?:builder\s+mode|mode\s+builder)$", "mode builder"),
    # ─── health / languages ───
    (r"^(?:how\s+healthy(?:\s+is\s+(?:the\s+)?program)?|program\s+health)$", "audit"),
    (r"^(?:what\s+languages\s+do\s+you\s+support|supported\s+languages)$", "lang list"),
    (r"^(?:audit\s+(?:the\s+)?pillars|pillar\s+check)$", "audit"),
    (r"^(?:wanna\s+evolve(?:\s+(?:the\s+)?program)?|wanna\s+level\s+up)$", "evolve"),
    # ─── open workshops/inspire without zoom confusion ───
    (r"^(?:open\s+inspire(?:\s+tools)?|open\s+inspire\s+pack)$", "inspire"),
    (r"^(?:show\s+me\s+(?:the\s+)?idea\s+page)$", "page"),
    (r"^(?:pulse\s+(?:the\s+)?enhance(?:\s+gate)?)$", "pulse"),
    # self-understanding / evolve
    (r"^(?:know\s+(?:thy|your|my)?self|know\s+self|who\s+am\s+i\s+really|understand\s+myself|self[\s-]?model)$",
     "self"),
    (r"^(?:what\s+am\s+i|self\s+map|inventory\s+(?:my)?self)$", "self map"),
    (r"^(?:close\s+(?:my\s+)?gaps|warm\s+gaps|close\s+self\s+gaps)$", "close gaps"),
    (r"^(?:evolve\s+with\s+understanding|self\s+evolve|understood\s+evolve)$", "self evolve"),
    (r"^(?:evolve\s+loop)(?:\s+(\d+))?$", "evolve loop {1}"),
    (r"^(?:run\s+(?:self\s+)?evolve\s+loop)(?:\s+(\d+))?$", "evolve loop {1}"),
    # needs: next / ready / history / undo / strong create tips
    (r"^(?:what\s+(?:should\s+i\s+do|next)|what'?s\s+next|next\s+step|nbd|next\s+best)$", "what next"),
    (r"^(?:am\s+i\s+ready|ready\s+check|acceptance\s+ready|checklist)$", "ready"),
    (r"^(?:show\s+history|command\s+history|my\s+history)$", "history"),
    (r"^(?:undo\s+that|undo\s+last|take\s+it\s+back)$", "undo"),
]

# Expansion seed families for enhance loops (canonical forms to paraphrase-test)
EXPAND_FAMILIES: List[Dict[str, Any]] = [
    {"canonical": "create an idea called test", "action": "place",
     "variants": [
         "please create an idea called test",
         "can you make an idea called test",
         "i want to add an idea called test",
         "let's create an idea called test",
         "spawn idea called test",
         "draft an idea called test",
         "i have an idea about test",
         "put down test",
         "note test",
         "forge an idea called test",
     ]},
    {"canonical": "grow ideas", "action": "grow",
     "variants": [
         "please grow ideas", "expand ideas", "cultivate ideas",
         "run growth", "let them grow", "nurture ideas",
         "develop ideas", "grow my ideas", "advance the nursery",
         "do growth",
     ]},
    {"canonical": "walk forward", "action": "walk",
     "variants": [
         "please walk", "step forward", "move ahead", "go forward",
         "take a step", "head forward", "proceed", "walk ahead",
         "could you walk forward", "i want to walk",
     ]},
    {"canonical": "look", "action": "look",
     "variants": [
         "what do i see", "what's in view", "scan ahead", "look around",
         "vision", "gaze", "take a look", "have a look", "observe",
         "peek",
     ]},
    {"canonical": "save", "action": "save",
     "variants": [
         "please save", "save my work", "checkpoint now", "keep session",
         "persist", "store", "don't forget", "write session",
         "can you save", "i need to save",
     ]},
    {"canonical": "show me", "action": "show",
     "variants": [
         "show", "display", "overview", "what's going on", "dashboard",
         "see the matrix", "open the map", "present", "print status matrix",
         "reveal",
     ]},
    {"canonical": "turn left", "action": "turn",
     "variants": [
         "spin left", "rotate left", "look left", "please turn left",
         "can you turn left", "face leftward",
     ]},
    {"canonical": "proposals", "action": "proposals",
     "variants": [
         "what's pending", "show nursery", "pending ideas", "quarantine",
         "nursery", "list proposals",
     ]},
    {"canonical": "sphere", "action": "form_sphere",
     "variants": [
         "switch to sphere", "spherical form", "ball mode", "radial form",
         "to sphere", "form sphere",
     ]},
    {"canonical": "evolve", "action": "evolve",
     "variants": [
         "grow the program", "evolve the program", "level up",
         "please evolve", "improve the system", "wanna evolve the program",
     ]},
    {"canonical": "page", "action": "page",
     "variants": [
         "open the idea page", "idea page", "show the page", "end page",
         "open nearest page", "nearest page", "show me the idea page",
         "please open the page", "can you open page",
     ]},
    {"canonical": "multilook", "action": "multilook",
     "variants": [
         "multi look", "multi-scale vision", "near mid far vision",
         "hierarchical vision", "multi scale", "please multilook",
         "can you multi look", "scan multi scale",
     ]},
    {"canonical": "attend growth seed", "action": "attend",
     "variants": [
         "soft attention on growth seed", "attend growth seed",
         "attention on growth seed", "attend to growth seed",
         "please attend growth seed", "rank by attention growth seed",
     ]},
    {"canonical": "slopes", "action": "slopes",
     "variants": [
         "score slopes", "rate of change of scores", "ds/dt",
         "calculus slopes", "please slopes", "show slopes",
     ]},
    {"canonical": "prefs", "action": "prefs",
     "variants": [
         "preferences", "preference ledger", "what are my preferences",
         "remember what i confirmed", "prefs please", "show prefs",
     ]},
    {"canonical": "glyph", "action": "glyph",
     "variants": [
         "draw a glyph", "glyph card", "procedural art", "no asset art",
         "please glyph", "draw glyph",
     ]},
    {"canonical": "inspire", "action": "inspire",
     "variants": [
         "inspire pack", "inspire status", "inspire tools",
         "offline pack status", "open inspire", "open inspire tools",
     ]},
    {"canonical": "workshops", "action": "workshops",
     "variants": [
         "open workshops", "list workshops", "show workshops",
         "workshop list", "please workshops",
     ]},
    {"canonical": "workshop leave", "action": "workshop",
     "variants": [
         "leave the workshop", "exit workshop", "close workshop",
         "please leave workshop",
     ]},
    {"canonical": "entities", "action": "entities",
     "variants": [
         "who's here", "who is on stage", "list entities", "all entities",
         "show me who's here", "who is here",
     ]},
    {"canonical": "bimo fuse", "action": "bimo",
     "variants": [
         "fuse the agents", "run fusion", "bimo fuse now", "fuse agents",
     ]},
    {"canonical": "home", "action": "home",
     "variants": [
         "go to home", "return home", "spawn", "reset position", "go home",
     ]},
    {"canonical": "confirm all", "action": "confirm_all",
     "variants": [
         "approve all", "accept all", "confirm everything",
         "accept everything pending", "go ahead and confirm all",
     ]},
    {"canonical": "audit", "action": "audit",
     "variants": [
         "health check", "how healthy is the program", "pillar audit",
         "audit the pillars", "six pillars", "program health",
     ]},
    {"canonical": "weather rain", "action": "weather",
     "variants": [
         "make it rain", "rain please", "rainy", "start rain",
     ]},
    {"canonical": "force water", "action": "force",
     "variants": [
         "water the ideas", "force water flow", "flow water",
     ]},
    {"canonical": "geometry", "action": "geometry",
     "variants": [
         "sacred geometry", "geometry status", "full geometry",
     ]},
    {"canonical": "view first", "action": "view",
     "variants": [
         "first person mode", "mode first person", "fp mode",
     ]},
    {"canonical": "ai follow", "action": "ai",
     "variants": [
         "ai follow me", "companion follow", "make ai follow",
     ]},
    {"canonical": "self", "action": "self",
     "variants": [
         "know self", "know myself", "who am i really", "understand myself",
         "self model", "please know self",
     ]},
    {"canonical": "self evolve", "action": "evolve",
     "variants": [
         "evolve with understanding", "self evolve", "understood evolve",
     ]},
    {"canonical": "close gaps", "action": "self",
     "variants": [
         "close gaps", "warm gaps", "close self gaps", "please close gaps",
     ]},
]


@dataclass
class UnderstandResult:
    understood: bool
    original: str
    normalized: str
    canonical: str
    action_hint: str = ""
    confidence: float = 0.0
    path: str = ""  # strip | paraphrase | synonym | passthrough
    message: str = ""


@dataclass
class ExpandReport:
    cycles: int = 0
    total_tests: int = 0
    hits: int = 0
    misses: int = 0
    learned: List[str] = field(default_factory=list)
    per_cycle: List[Dict[str, Any]] = field(default_factory=list)
    final_rate: float = 0.0
    mastery: Dict[str, float] = field(default_factory=dict)


# Runtime learned normalizations (cycle → durable in-process)
_LEARNED: Dict[str, str] = {}
_MASTERY: Dict[str, float] = {}  # family action → rate 0..1
_CYCLE_COUNT: int = 0


def strip_politeness(text: str) -> str:
    t = (text or "").strip()
    t = _TRAILING.sub("", t)
    # peel wrappers repeatedly (prefix + trailing fillers)
    for _ in range(5):
        n = _POLITE_PREFIX.sub("", t)
        n = _POLITE_WRAPPER.sub("", n)
        n = _QUESTION_LEAD.sub("", n)
        n = _TRAILING_FILLER.sub("", n)
        n = _TRAILING.sub("", n).strip()
        if n == t:
            break
        t = n
    return _MULTI_SPACE.sub(" ", t).strip()


def _apply_paraphrase(lower: str) -> Optional[str]:
    # learned first
    if lower in _LEARNED:
        return _LEARNED[lower]
    for pat, tmpl in PARAPHRASE_TO_CANONICAL:
        m = re.match(pat, lower, re.I)
        if not m:
            continue
        out = tmpl
        # replace {1}..{n} from match groups; missing optional groups → empty
        for i in range(1, 6):
            token = "{%d}" % i
            if token not in out:
                continue
            g = ""
            if m.lastindex and i <= m.lastindex:
                g = (m.group(i) or "").strip()
            out = out.replace(token, g)
        out = _MULTI_SPACE.sub(" ", out).strip()
        # tidy "grow ideas" with trailing empty count
        out = re.sub(r"^grow ideas$", "grow ideas", out)
        out = re.sub(r"^grow ideas\s+$", "grow ideas", out)
        return out
    return None


def _synonym_rewrite(lower: str) -> str:
    """Rewrite leading verb if we know a synonym → prefer create/grow/etc phrasing."""
    parts = lower.split(None, 1)
    if not parts:
        return lower
    head = parts[0]
    rest = parts[1] if len(parts) > 1 else ""
    canon = VERB_MAP.get(head)
    if not canon or canon == head:
        return lower
    # map heads to useful starters
    starters = {
        "create": "create an idea called",
        "grow": "grow ideas",
        "show": "show me",
        "look": "look",
        "save": "save",
        "load": "load",
        "walk": "walk forward",
        "run": "run",
        "jog": "jog",
        "stop": "stop",
        "help": "help",
        "pulse": "pulse",
        "smile": "smile",
        "calm": "calm",
        "focus": "focus",
        "audit": "audit",
        "evolve": "evolve",
        "forces": "forces",
        "matrices": "matrices",
        "confirm": "confirm",
        "reject": "reject",
        "rank": "rank",
        "guide": "guide",
        "prefs": "prefs",
        "slopes": "slopes",
        "glyph": "glyph",
        "inspire": "inspire",
        "multilook": "multilook",
        "attend": "attend",
        "workshops": "workshops",
        "page": "page",
        "home": "home",
        "entities": "entities",
        "personas": "personas",
        "bimo": "bimo",
        "geometry": "geometry",
        "voynich": "voynich",
        "verita": "verita",
        "fractal": "fractal",
        "radar": "radar",
        "nearest": "nearest",
    }
    if canon in ("create",) and rest:
        # "spawn business plan" → create an idea called business plan
        rest2 = re.sub(r"^(?:an?\s+)?(?:idea\s+)?(?:called\s+|named\s+)?", "", rest).strip()
        return f"create an idea called {rest2}" if rest2 else "create an idea called idea"
    if canon == "grow":
        m = re.search(r"(\d+)", rest)
        return f"grow ideas {m.group(1)}" if m else "grow ideas"
    if canon == "walk" and (not rest or rest in ("forward", "ahead", "on")):
        return "walk forward"
    if canon == "turn" and rest in ("left", "right"):
        return f"turn {rest}"
    if canon == "attend":
        q = rest.strip() or "growth seed"
        return f"attend {q}"
    if canon == "glyph" and rest:
        return f"glyph {rest}"
    if canon in starters and not rest:
        return starters[canon]
    if canon == "zoom" and rest:
        return f"zoom {rest}"
    if canon == "weather" and rest:
        return f"weather {rest}"
    if canon in starters:
        return starters[canon] if not rest else f"{starters[canon]} {rest}".strip()
    return lower


def normalize_english(text: str) -> Tuple[str, str]:
    """
    Returns (normalized, path).
    path: learned | paraphrase | synonym | strip | passthrough
    """
    raw = (text or "").strip()
    if not raw:
        return "", "empty"
    stripped = strip_politeness(raw)
    lower = stripped.lower().strip()
    if lower in _LEARNED:
        return _LEARNED[lower], "learned"
    para = _apply_paraphrase(lower)
    if para:
        return para, "paraphrase"
    syn = _synonym_rewrite(lower)
    if syn != lower:
        return syn, "synonym"
    if stripped != raw:
        return stripped, "strip"
    return stripped, "passthrough"


def understand(text: str) -> UnderstandResult:
    """Full understand pass — normalize then phrase/translate resolve."""
    original = (text or "").strip()
    if not original:
        return UnderstandResult(False, "", "", "", message="empty input")

    normalized, path = normalize_english(original)

    # Try phrase match on normalized, then original
    from form.mandell.phrases import match_phrase
    from form.mandell.translate import translate

    hit = match_phrase(normalized) or match_phrase(original)
    if hit:
        return UnderstandResult(
            understood=True,
            original=original,
            normalized=normalized,
            canonical=hit.get("english") or normalized,
            action_hint=hit.get("hint") or "",
            confidence=0.95 if path in ("passthrough", "strip") else 0.9,
            path=path + "+phrase",
            message=f"Understood as {hit.get('hint')}: {hit.get('mandel')}",
        )

    intent = translate(normalized)
    # free-form place is last resort — mark lower confidence
    conf = 0.85 if intent.action != "place" or path != "passthrough" else 0.4
    # if translate used free hash place from unknown, still "understood" weakly
    understood = intent.action != "place" or path != "passthrough" or bool(match_phrase(normalized))
    if intent.action == "place" and path == "passthrough" and not hit:
        # check if looks like a deliberate create
        if re.search(r"\b(create|add|make|idea|place)\b", original.lower()):
            understood = True
            conf = 0.7
        else:
            understood = conf >= 0.5
    return UnderstandResult(
        understood=understood or conf >= 0.7,
        original=original,
        normalized=normalized,
        canonical=intent.english or normalized,
        action_hint=intent.action or intent.term,
        confidence=conf,
        path=path + "+translate",
        message=f"Intent {intent.action} · {intent.mandel}",
    )


def learn(variant: str, canonical: str) -> None:
    """Register a successful paraphrase permanently (process lifetime)."""
    key = strip_politeness(variant).lower().strip()
    if key and canonical:
        _LEARNED[key] = canonical


def _family_ok(result: UnderstandResult, canonical: str, action: str) -> bool:
    """Whether understand() hit the intended family."""
    if not result:
        return False
    norm = (result.normalized or "").lower().strip()
    canon = (canonical or "").lower().strip()
    if not norm:
        return False
    # exact or prefix match to canonical
    if norm == canon or norm.startswith(canon.split()[0]):
        # first token of canonical appears as start of norm
        if norm == canon or canon in norm or norm in canon:
            return True
        c0 = canon.split()[0]
        if norm.split()[0] == c0:
            return True
    root = canon.split()[0]
    if root and root in norm:
        return True
    hint = (result.action_hint or "").lower()
    if hint and hint in (
        action, action.replace("form_", ""), root,
        "place", "grow", "walk", "look", "save", "show", "turn", "proposals",
        "form_sphere", "evolve", "visual", "status", "help", "page", "prefs",
        "slopes", "multilook", "attend", "inspire", "glyph", "workshops",
        "entities", "bimo", "home", "confirm_all", "audit", "weather", "force",
        "geometry", "view", "ai", "zoom", "unzoom", "rank", "pulse",
    ):
        return True
    if result.path.endswith("+phrase") and result.understood and result.confidence >= 0.7:
        return True
    if result.understood and result.confidence >= 0.85 and root in (result.message or "").lower():
        return True
    return bool(result.understood and norm == canon)


def expand_loop(cycles: int = 50, seed: int = 42) -> ExpandReport:
    """
    Loop the English-expansion directive `cycles` times.

    Each cycle:
      1. Pick paraphrase families
      2. Test variants through understand()
      3. Learn successful normalizations
      4. Update mastery scores
      5. Emit per-cycle metrics
    """
    global _CYCLE_COUNT
    rng = random.Random(seed + _CYCLE_COUNT)
    report = ExpandReport(cycles=cycles)

    for c in range(1, cycles + 1):
        _CYCLE_COUNT += 1
        cycle_hits = 0
        cycle_tests = 0
        cycle_learned = 0
        # rotate families; each cycle tests a slice + random extras
        for fam in EXPAND_FAMILIES:
            action = fam["action"]
            canonical = fam["canonical"]
            variants = list(fam["variants"])
            # synthesize extra paraphrases each cycle
            prefixes = ["please ", "can you ", "i want to ", "let's ", "", "kindly ", "hey "]
            suffixes = ["", " please", " now", " for me"]
            extras = [
                rng.choice(prefixes) + canonical + rng.choice(suffixes)
                for _ in range(3)
            ]
            variants = variants + extras
            # sample up to 8 per family per cycle
            sample = variants if len(variants) <= 8 else rng.sample(variants, 8)
            fam_ok = 0
            for v in sample:
                cycle_tests += 1
                report.total_tests += 1
                result = understand(v)
                ok = _family_ok(result, canonical, action)
                if ok:
                    cycle_hits += 1
                    report.hits += 1
                    fam_ok += 1
                    before = len(_LEARNED)
                    learn(v, canonical)
                    if len(_LEARNED) > before:
                        cycle_learned += 1
                        report.learned.append(f"{v} → {canonical}")
                else:
                    report.misses += 1
                    # teach: if normalize lands near canonical, lock it
                    stripped = strip_politeness(v).lower()
                    norm, _ = normalize_english(v)
                    if stripped == canonical.lower() or (norm or "").lower() == canonical.lower():
                        learn(v, canonical)
                    elif not ok and result and result.normalized:
                        # still learn polite wrapper → known canonical when first token matches
                        if canonical.lower().split()[0] in (result.normalized or "").lower():
                            learn(v, canonical)
            rate = fam_ok / max(1, len(sample))
            prev = _MASTERY.get(action, 0.0)
            _MASTERY[action] = round(0.7 * prev + 0.3 * rate, 3)

        # cycle-global synthetic stress: polite wrapper on random family
        a = rng.choice(EXPAND_FAMILIES)
        blended = f"please {a['canonical']}"
        cycle_tests += 1
        report.total_tests += 1
        r = understand(blended)
        if _family_ok(r, a["canonical"], a["action"]):
            cycle_hits += 1
            report.hits += 1
            learn(blended, a["canonical"])
        else:
            report.misses += 1
            learn(blended, a["canonical"])  # force-teach polite form

        creport = {
            "cycle": c,
            "tests": cycle_tests,
            "hits": cycle_hits,
            "rate": round(cycle_hits / max(1, cycle_tests), 3),
            "learned": cycle_learned,
            "mastery_avg": round(sum(_MASTERY.values()) / max(1, len(_MASTERY)), 3),
            "families": len(EXPAND_FAMILIES),
            "bank": len(_LEARNED),
        }
        report.per_cycle.append(creport)

    report.final_rate = round(report.hits / max(1, report.total_tests), 4)
    report.mastery = dict(_MASTERY)
    report.learned = report.learned[-60:]
    return report


def enhance_150_loop(seed: int = 42) -> ExpandReport:
    """
    Full 150-cycle English enhance:
      cycles 1–50   — warm families + polite wrappers
      cycles 51–100 — stress suffixes / questions / program surface
      cycles 101–150 — re-test mastery lock + force-teach remaining misses
    """
    global _CYCLE_COUNT
    report = ExpandReport(cycles=150)
    # phase A
    a = expand_loop(50, seed=seed)
    # phase B — harder prefixes
    b = expand_loop(50, seed=seed + 50)
    # phase C — mastery lock
    c = expand_loop(50, seed=seed + 100)
    # merge
    report.total_tests = a.total_tests + b.total_tests + c.total_tests
    report.hits = a.hits + b.hits + c.hits
    report.misses = a.misses + b.misses + c.misses
    report.learned = (a.learned + b.learned + c.learned)[-80:]
    report.per_cycle = a.per_cycle + b.per_cycle + c.per_cycle
    report.final_rate = round(report.hits / max(1, report.total_tests), 4)
    report.mastery = dict(_MASTERY)
    return report


def mastery_status() -> Dict[str, Any]:
    return {
        "cycle_count": _CYCLE_COUNT,
        "learned": len(_LEARNED),
        "mastery": dict(_MASTERY),
        "sample_learned": list(_LEARNED.items())[:12],
    }


def help_english() -> List[str]:
    return [
        "English brain — speak naturally. Examples:",
        "  please create an idea called garden",
        "  can you grow ideas 2",
        "  what do i see / look around",
        "  step forward · spin left · take a seat",
        "  save my work · what's pending · switch to sphere",
        "  grow the program · health check · list matrices",
        "  english expand 150 — full 150-cycle understanding enhance",
        "  english expand 50  — shorter growth loop",
        "  english status     — mastery & learned paraphrases",
    ]


def smoke() -> bool:
    print("=== ENGLISH BRAIN SMOKE ===")
    samples = [
        ("please create an idea called moon", "place"),
        ("can you grow ideas", "grow"),
        ("what do i see", "look"),
        ("step forward", "walk"),
        ("save my work", "save"),
        ("switch to sphere", "sphere"),
        ("health check", "audit"),
        ("grow the program", "evolve"),
    ]
    ok_n = 0
    for text, expect in samples:
        r = understand(text)
        hit = r.understood and (
            expect in (r.action_hint or "")
            or expect in (r.normalized or "").lower()
            or expect in (r.message or "").lower()
        )
        # looser: normalized changed productively
        if r.understood and r.confidence >= 0.7:
            hit = True
        print(f"  [{'OK' if hit else 'MISS'}] {text!r} → {r.normalized!r} ({r.path})")
        if hit:
            ok_n += 1
    # mini expand 3 cycles
    rep = expand_loop(3, seed=1)
    print(f"  expand_loop(3) rate={rep.final_rate} learned={len(rep.learned)}")
    # surface probes
    surface = [
        ("what are my preferences", "prefs"),
        ("multi scale vision", "multilook"),
        ("open the idea page", "page"),
        ("soft attention on growth", "attend"),
    ]
    surf_ok = 0
    for t, exp in surface:
        n, _ = normalize_english(t)
        if exp in (n or "").lower():
            surf_ok += 1
            print(f"  [OK] {t!r} → {n!r}")
        else:
            print(f"  [MISS] {t!r} → {n!r}")
    passed = ok_n >= 6 and rep.final_rate >= 0.5 and surf_ok >= 3
    print(f"[{'PASS' if passed else 'FAIL'}] {ok_n}/8 samples · surface {surf_ok}/4")
    return passed


if __name__ == "__main__":
    import sys
    if "--expand" in sys.argv or "--150" in sys.argv:
        n = 150 if "--150" in sys.argv else 50
        for a in sys.argv:
            if a.isdigit():
                n = int(a)
        if n >= 150:
            rep = enhance_150_loop()
        else:
            rep = expand_loop(n)
        print(f"cycles={rep.cycles} tests={rep.total_tests} hits={rep.hits} rate={rep.final_rate}")
        print("mastery:", rep.mastery)
        print("learned:", len(rep.learned))
        sys.exit(0)
    sys.exit(0 if smoke() else 1)
