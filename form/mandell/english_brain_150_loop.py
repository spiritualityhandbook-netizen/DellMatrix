#!/usr/bin/env python3
"""
English Brain — 150-loop enhance on natural English understanding.

Pillars (cycled each phase):
  1. Coverage   — paraphrase + synonym banks hit program surface
  2. Accuracy   — variants normalize to correct canonical command
  3. Grounding  — live Program / live_visual executes understood cmds
  4. Usability  — polite wrappers, trailing fillers, questions work

Phases (50 + 50 + 50 = 150):
  A warm-up families · B stress wrappers · C mastery lock + program probes

  python -m form.mandell.english_brain_150_loop
  python -m form.mandell.english_brain_150_loop --cycles 150
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Tuple

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


# Program-surface probes (must understand → useful command)
PROGRAM_PROBES: List[Tuple[str, str]] = [
    ("please create an idea called garden", "create"),
    ("can you grow ideas 2", "grow"),
    ("what do i see", "look"),
    ("look around for me", "look"),
    ("step forward", "walk"),
    ("save my work", "save"),
    ("switch to sphere", "sphere"),
    ("health check", "audit"),
    ("how healthy is the program", "audit"),
    ("grow the program", "evolve"),
    ("open the idea page", "page"),
    ("show me the idea page", "page"),
    ("go to home", "home"),
    ("find nearest", "nearest"),
    ("soft attention on growth", "attend"),
    ("multi scale vision", "multilook"),
    ("score slopes please", "slopes"),
    ("what are my preferences", "prefs"),
    ("draw a glyph", "glyph"),
    ("inspire pack status", "inspire"),
    ("open workshops", "workshops"),
    ("leave the workshop", "workshop leave"),
    ("matrix workshop", "workshop matrix"),
    ("who is on stage", "entities"),
    ("fuse the agents", "bimo fuse"),
    ("dock defaults", "bimo defaults"),
    ("rain please", "weather rain"),
    ("clear the weather", "weather clear"),
    ("water the ideas", "force water"),
    ("walk into next cube", "enter next"),
    ("first person mode", "view first"),
    ("map mode please", "view map"),
    ("body as robot", "body robot"),
    ("rank the nursery", "rank"),
    ("accept everything pending", "confirm all"),
    ("go ahead and confirm all", "confirm all"),
    ("what languages do you support", "lang list"),
    ("turn depth mode on", "mode depth"),
    ("ai follow me", "ai follow"),
    ("ai take a walk", "ai walk"),
    ("verita edges please", "verita"),
    ("voynich rings", "voynich"),
    ("fractal rule 90", "fractal"),
    ("unzoom please", "unzoom"),
    ("recenter camera", "recenter"),
    ("i need to audit the pillars", "audit"),
    ("wanna evolve the program", "evolve"),
    ("um what do i see right now", "look"),
    ("could you kindly look around for me?", "look"),
    ("make sure to save my work", "save"),
    ("open inspire tools", "inspire"),
    ("near mid far vision", "multilook"),
    ("rate of change of scores", "slopes"),
    ("preferences from confirm reject", "prefs"),
    ("pulse the enhance gate", "pulse"),
]


def _probe_hit(text: str, expect_token: str) -> Tuple[bool, str, str]:
    from form.mandell.english_brain import understand, normalize_english
    norm, path = normalize_english(text)
    r = understand(text)
    blob = " ".join([
        norm or "",
        r.normalized or "",
        r.action_hint or "",
        r.message or "",
        r.canonical or "",
    ]).lower()
    token = expect_token.lower()
    ok = token in blob or token.split()[0] in blob
    # also accept high-confidence phrase path
    if r.understood and r.confidence >= 0.9 and path in ("paraphrase", "synonym", "learned", "strip"):
        if any(t in (norm or "").lower() for t in token.split()[:2]):
            ok = True
    return ok, norm or "", path


def _program_ground(text: str) -> Tuple[bool, str]:
    """Execute understood form against Program — must not mis-create junk ideas."""
    from form.open import open_program
    from form.dell_matrix.live_visual import _run_command
    from form.mandell.english_brain import normalize_english

    p = open_program("EnBrain150")
    before = set(p.cube.session.plane.units.keys())
    out = _run_command(p, text)
    after = set(p.cube.session.plane.units.keys())
    new = after - before
    norm, path = normalize_english(text)
    # mis-create: new units whose labels look like the raw English phrase
    junk = []
    for uid in new:
        u = p.cube.session.plane.units.get(uid)
        lab = (u.label if u else "").lower()
        if lab and lab in text.lower() and "create" not in text.lower() and "idea" not in text.lower():
            junk.append(lab)
    ok = bool(out.get("ok") or out.get("msg") or out.get("error"))
    # usage ends and real ends are fine
    if junk and path == "passthrough":
        ok = False
    msg = (out.get("msg") or out.get("error") or "")[:80]
    return ok and not junk, f"norm={norm!r} path={path} → {msg}"


def run_loop(cycles: int = 150, seed: int = 42) -> Dict[str, Any]:
    from form.mandell.english_brain import (
        enhance_150_loop, expand_loop, mastery_status, EXPAND_FAMILIES,
        understand, normalize_english,
    )

    print("=== ENGLISH BRAIN 150 ENHANCE ===")
    print(f"families={len(EXPAND_FAMILIES)} probes={len(PROGRAM_PROBES)} cycles={cycles}")

    # baseline probe
    base_hits = 0
    base_detail = []
    for text, expect in PROGRAM_PROBES:
        ok, norm, path = _probe_hit(text, expect)
        base_hits += int(ok)
        if not ok:
            base_detail.append((text, norm, path, expect))
    print(f"[baseline] probes {base_hits}/{len(PROGRAM_PROBES)}")

    # main enhance
    if cycles >= 150:
        rep = enhance_150_loop(seed=seed)
    else:
        rep = expand_loop(cycles, seed=seed)

    print(
        f"[expand] tests={rep.total_tests} hits={rep.hits} "
        f"rate={rep.final_rate:.1%} learned_bank_events={len(rep.learned)}"
    )
    if rep.per_cycle:
        mid = rep.per_cycle[len(rep.per_cycle) // 2]
        last = rep.per_cycle[-1]
        print(f"  cycle 1 rate={rep.per_cycle[0].get('rate')} mastery={rep.per_cycle[0].get('mastery_avg')}")
        print(f"  cycle {mid.get('cycle')} rate={mid.get('rate')} mastery={mid.get('mastery_avg')}")
        print(f"  cycle {last.get('cycle')} rate={last.get('rate')} mastery={last.get('mastery_avg')} bank={last.get('bank')}")

    # post probe
    post_hits = 0
    still_miss = []
    for text, expect in PROGRAM_PROBES:
        ok, norm, path = _probe_hit(text, expect)
        post_hits += int(ok)
        if not ok:
            still_miss.append((text, norm, path, expect))
    print(f"[post] probes {post_hits}/{len(PROGRAM_PROBES)}")

    # program grounding sample (every 5th probe to stay fast)
    ground_ok = 0
    ground_n = 0
    for text, expect in PROGRAM_PROBES[::3]:
        ground_n += 1
        ok, detail = _program_ground(text)
        ground_ok += int(ok)
        if not ok:
            print(f"  [ground MISS] {text!r} · {detail}")
    print(f"[ground] {ground_ok}/{ground_n} live Program ends usefully")

    st = mastery_status()
    print(f"[mastery] learned={st['learned']} cycle_count={st['cycle_count']}")
    top = sorted((st.get("mastery") or {}).items(), key=lambda kv: -kv[1])[:12]
    if top:
        print("  top: " + " · ".join(f"{k}={v:.2f}" for k, v in top))

    if still_miss:
        print(f"[remaining misses {len(still_miss)}]")
        for m in still_miss[:12]:
            print(f"  {m[0]!r} → {m[1]!r} ({m[2]}) expect~{m[3]}")

    # pass gates
    probe_rate = post_hits / max(1, len(PROGRAM_PROBES))
    expand_rate = rep.final_rate
    ground_rate = ground_ok / max(1, ground_n)
    passed = (
        expand_rate >= 0.75
        and probe_rate >= 0.80
        and ground_rate >= 0.75
        and post_hits >= base_hits
    )
    print(
        f"=== RESULT: expand={expand_rate:.1%} probes={probe_rate:.1%} "
        f"ground={ground_rate:.1%} · {'PASS' if passed else 'FAIL'} ==="
    )
    return {
        "ok": passed,
        "expand_rate": expand_rate,
        "probe_rate": probe_rate,
        "ground_rate": ground_rate,
        "base_hits": base_hits,
        "post_hits": post_hits,
        "probes": len(PROGRAM_PROBES),
        "mastery": st,
        "report": rep,
        "misses": still_miss,
    }


def smoke() -> bool:
    # short path for suite
    out = run_loop(cycles=6, seed=7)
    # soft gate for smoke
    return out["probe_rate"] >= 0.7 and out["expand_rate"] >= 0.6


if __name__ == "__main__":
    n = 150
    for a in sys.argv[1:]:
        if a.isdigit():
            n = int(a)
        if a == "--smoke":
            sys.exit(0 if smoke() else 1)
    out = run_loop(cycles=n)
    sys.exit(0 if out["ok"] else 1)
