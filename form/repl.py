#!/usr/bin/env python3
"""REPL — Mandell Origin. English, seeds, lattice, polyglot, LatinMandell depth."""

from __future__ import annotations

import re
import sys
from typing import Optional

try:
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.mandell.translate import translate
    from form.mandell.seed import looks_like_seed
    from form.mandell.bridge import to_english, to_mandell, bridge
    from form.mandell.patterns import teach, list_patterns
    from form.mandell.polyglot import bridge_lang, list_langs
    from form.mandell.phrases import list_phrases, match_phrase
    from form.mandell.latinmandell import (
        format_explain, deepen, customize, list_customs, root_of,
    )
    from form.mandell.morpheme import force_mandell_morphemes, explain_morphemes
    from form.avatar import Facing, Posture, Locomotion, Expression
    from form.persist import load as persist_load
except ImportError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.mandell.translate import translate
    from form.mandell.seed import looks_like_seed
    from form.mandell.bridge import to_english, to_mandell, bridge
    from form.mandell.patterns import teach, list_patterns
    from form.mandell.polyglot import bridge_lang, list_langs
    from form.mandell.phrases import list_phrases, match_phrase
    from form.mandell.latinmandell import (
        format_explain, deepen, customize, list_customs, root_of,
    )
    from form.mandell.morpheme import force_mandell_morphemes, explain_morphemes
    from form.avatar import Facing, Posture, Locomotion, Expression
    from form.persist import load as persist_load

HELP_SHORT = """
Find capability by goal (type help <category> for exact syntax)

  help create     ideas, growth, proposals — make and develop
  help knowledge  why, trace, supersede — understand knowledge
  help learn      DuoBeta learning lifecycle — propose to apply
  help explain    outcomes, what happened — explanation
  help save       save, load, continue after restart
  help recover    history, undo, replay — recover and retry
  help look       look, page, zoom — inspect
  help dell       Mandell/Dell execution — run capabilities
  help system     modes, visual, tutorial — configure

  help more       full command reference (all commands)
""".strip()

HELP_MORE = """
Mandell Origin — English, seeds, or LatinMandell.

Ideas / Growth
  create an idea called test
  grow ideas 2
  proposals | confirm <id> | confirm all | reject all
  rank | lineage <id>
  distill <words> | macro [n] | replay [n]
  auto confirm on|off   grow mode: auto-confirm all after each grow
  grow mode             show auto_confirm_grow status

Knowledge / Learning
  proposals | confirm <id> | confirm all | reject all
  why used <kid> in <oid> · why not used <kid> [for <ctx>]
  why influence <kid> [in <oid>] [for <ctx>]
  learn propose <kind> <dell> from <oid> ... · learn inspect <pid>
  learn gate <pid> · learn apply <pid> confirm · learn ledger
  learning is stepwise: propose → inspect → gate → apply (confirm required)
  supersede idea <old-id> with <words> · trace dependency <id>
  discover [nursery]

Lattice / Perception / Looking
  cube | sphere | core | flower | toggle
  lattice | chord 0 0 | shell 0
  flower geometry | vesica | verita     Flower of Life + Verita edges
  voynich | rings                       structural 5-ring metaphor (not decrypt)
  fractal | rule90 | orbit              Rule 90 · bounded/complex orbit
  geometry                              full sacred-geometry status
  look                  directional vision from facing
  zoom <id|label> | page | unzoom
  alpha | delta | omega | omni | lambda | sigma   Greek floor: semantic observation
  snap on|off           grid snap when form is cube
  lens <skin>|clear     filter vision by skin
  persona <name>|clear  soft persona lens (manny, melody, …)
  personas | guide      full roster + active guidance
  persona <name>|clear  manny melody aetheris mathelody the_ancient
                        translator della mansplainer dell oracle bimo
  matrix personas       persona matrix map
  bimo | bimo defaults | bimo fuse | bimo dock <slot> <persona>
  bimo undock <slot> | bimo clear | bimo pilot <name>
  forge                 BIMO Forge: stage an arrangement, preview it,
                        save it as a named configuration
  connect               Connected World: gated fetch with provenance
                        evidence + docked inference (pending proposals)
  rooms | view <room>   view-rooms (growth water force network …)
  forces | force tick   nature forces field
  weather clear|rain|storm|fog
  spatial tick|settle [N]|explain <id>|status
                        canonical spatial authority (Phase 4)
  evolve                grow program gen + forces + pillars
  evolve <detail>       grow one generation with your intent recorded
  growth | duobeta     DuoBeta living-growth status
  ledger [N]           growth history (last N entries)
  audit                 6-pillar health
  discover [nursery]    inspect ideas/nursery via Dell 35
  matrices              inventory of all matrices
  english expand [N]    grow English understanding (default 50 cycles)
  english status|help   mastery / how to talk naturally
  self | know self      program self-understanding report
  self map              inventory of matrices · snaps · routes
  close gaps            warm cold capabilities
  evolve | self evolve  one generation (+ understanding)
  evolve loop [N]       N understand+evolve cycles (max 150)

Avatar / Movement
  walk | jog | run | backstep | strafe left|right
  turn left/right | sit | stand | smile | how do I look
  body stick|block|shadow|robot
  fp forward|back|up|down · fp turn left|right · fp look [up|down]
  goto H V [F]          first-person centerpoint jump
  view first | view map live display mode
  recenter              camera follow (legacy map)

AI companion
  ai walk | ai turn left|right | ai look
  ai follow | ai wander | ai manual | ai status | ai goto X Y

Workshops (depth mode)
  workshops | workshop matrix|perspective|mandel|persona|bimo|psalms|forces
  workshop leave

UX modes
  mode first-run|beginner|builder|depth
  onboard                 guided first moves (first-run onboarding)
  click inspect|confirm   (live node click)

LatinMandell (core depth)
  explain <word|phrase|Com-man-dell>
  deepen <phrase>
  morph <word>              force '-' morpheme split
  customize <label> [dell N] [sense ...]
  customs                   list custom bindings
  la <latin phrase>         same door as es/fr

Bridge
  mandell <english> | english <seed>
  es ... | fr ... | la ...
  lang list

Inspire Pack (offline · video-distilled pedagogy)
  attend [query]        soft attention over ideas (bag embeddings)
  multilook             near/mid/far vision + memory
  slopes                score calculus Δscore/Δt after pulses
  prefs                 confirm/reject preference ledger
  glyph [seed|label]    procedural art card (no assets)
  script cmd; cmd; …    batch matrix script
  inspire               pack status summary

System
  tutorial | start
  save | load | visual | live | status | enhance on/off | pulse
  acceptance
""".strip()

# CN-II: grouped navigation — intent-based categories with exact verified syntax.
# Presentation only; each example routes to an existing verified handler.
HELP_CATEGORIES = {
    "create": """
Create — make and develop ideas

  create an idea called <name>
  grow ideas <n>
  proposals | confirm <id> | confirm all | reject all
  rank | lineage <id>
""".strip(),
    "knowledge": """
Knowledge — understand what knowledge does

  why used <kid> in <oid>
  why not used <kid> [for <ctx>]
  why influence <kid> [in <oid>] [for <ctx>]
  trace dependency <id>
  supersede idea <old-id> with <words>
  discover [nursery]
""".strip(),
    "learn": """
Learn — DuoBeta learning lifecycle (stepwise, confirm required)

  learn propose <kind> <dell> from <oid> ...
  learn inspect <pid> · learn gate <pid>
  learn apply <pid> confirm · learn ledger
  propose → inspect → gate → apply (confirm required)
""".strip(),
    "explain": """
Explain — what happened

  outcomes · outcomes find <text> · outcome <seq>
  trace last · trace <seq>
  outcomes interaction <uuid>
  self | audit | status
""".strip(),
    "save": """
Save — persist and continue

  save · load
  restart with: python3 -m form.repl --load
""".strip(),
    "recover": """
Recover — history, undo, reissue

  history [n] · history find <text> · undo · replay [n]
  reissue <seq> · reissue confirm · reissue cancel
  what next | nbd
""".strip(),
    "look": """
Look — inspect the space

  look · page · zoom <id|label>
  alpha · delta · omega · omni · lambda · sigma
  (Greek floor operators — semantic observation, no operand)
""".strip(),
    "dell": """
Dell — execute capabilities via Mandell seeds

  NN[Name] :: <action>      e.g. 35[Discover] :: trace_dependency <id>
  use idea <pid>            explicit knowledge choice
""".strip(),
    "system": """
System — configure and orient

  tutorial · onboard · mode beginner|builder|depth · first-run (new owners)
  visual | live · help more
""".strip(),
}

_FACING = {
    "n": Facing.N, "north": Facing.N, "s": Facing.S, "south": Facing.S,
    "e": Facing.E, "east": Facing.E, "w": Facing.W, "west": Facing.W,
}
_EXPR = {
    "neutral": Expression.NEUTRAL, "focus": Expression.FOCUS,
    "joy": Expression.JOY, "calm": Expression.CALM,
    "intense": Expression.INTENSE, "curious": Expression.CURIOUS,
    "resolute": Expression.RESOLUTE, "soft": Expression.SOFT,
}


# When set (list), _say appends here instead of (or in addition to) printing.
# Live visual bridge uses this so every avenue returns a useful end message.
_OUT_CAPTURE: Optional[list] = None


def _say(msg: str) -> None:
    text = str(msg)
    if _OUT_CAPTURE is not None:
        _OUT_CAPTURE.append(text)
        return
    print(f"  {text}")


def capture_output(fn):
    """Run fn() capturing _say lines. Returns (result, joined_message)."""
    global _OUT_CAPTURE
    buf: list = []
    prev = _OUT_CAPTURE
    _OUT_CAPTURE = buf
    try:
        result = fn()
        return result, "\n".join(buf).strip()
    finally:
        _OUT_CAPTURE = prev


def _echo_seed(english: str = "", mandel: str = "") -> None:
    if mandel:
        _say(f"Mandell: {mandel}")
        return
    if english:
        hit = match_phrase(english)
        if hit and hit.get("mandel"):
            _say(f"Mandell: {hit['mandel']}")


def _print_route_receipt(receipt) -> None:
    """Print a DCC-III execution receipt v2 (honest: reports actual routing)."""
    _say(f"INPUT: {receipt.input}")
    _say(f"MANDELL: {receipt.mandell or '—'}")
    _say(f"SEMANTIC: {receipt.semantic or '—'}")
    if receipt.arguments:
        args_str = ", ".join(f"{k}={v}" for k, v in receipt.arguments.items())
        _say(f"ARGUMENTS: {args_str}")
    _say(f"ROUTE: {receipt.route}")
    if receipt.routed:
        _say(f"DELL: {receipt.dell} (executed via Dell authority)")
        for m in receipt.messages:
            _say(f"  {m}")
        _say(f"RESULT: ok={receipt.ok}")
        _say(f"STATE: {receipt.state_note}")
        if receipt.new_program is not None:
            _say("PROGRAM: restored from checkpoint (session replaced)")
    else:
        _say("DELL: none — not executed")
        _say(f"RESULT: {receipt.error or 'not routed'}")
        _say(f"STATE: {receipt.state_note}")


def _handle_latinmandell(p: Program, lower: str, raw: str):
    if lower.startswith("la ") or lower.startswith("latin "):
        text = raw.split(maxsplit=1)[1]
        rep = bridge_lang("la", text)
        _say(f"english: {rep.get('english')}")
        _say(f"mandel:  {rep.get('mandel')}")
        if rep.get("ok") == "true" and rep.get("english"):
            return ("__exec__", rep["english"])
        if rep.get("ok") != "true":
            _say("no LA map for that phrase yet — try explain / customize")
        return True

    if lower.startswith("explain ") or lower == "explain":
        text = raw.split(maxsplit=1)[1] if " " in raw else ""
        if not text:
            _say("Usage: explain <word|phrase|Com-man-dell>")
            return True
        print()
        print(format_explain(text))
        print()
        if hasattr(p, "note_seed"):
            p.note_seed(45, "Translate", "explain")
        return True

    if lower.startswith("deepen "):
        text = raw.split(maxsplit=1)[1]
        parts = deepen(text)
        if not parts:
            _say("No roots found — try hyphen form (Com-man-dell) or customize")
            return True
        for r in parts:
            dell = r.get("dell")
            d = f" dell={int(dell):02d}" if dell is not None else ""
            _say(f"{r.get('word')}: {r.get('la')} — {r.get('sense')}{d}")
        return True

    if lower.startswith("morph ") or lower.startswith("morpheme "):
        text = raw.split(maxsplit=1)[1]
        forced = force_mandell_morphemes(text)
        payload = explain_morphemes(forced)
        _say(f"forced: {forced}")
        for part in payload.get("parts") or []:
            _say(f"  - {part.get('morpheme')} ({part.get('kind')}): {part.get('sense')}")
        r = root_of(forced)
        if r:
            _say(f"combined: {r.get('sense')}")
        return True

    if lower in ("customs", "list customs", "custom list"):
        items = list_customs()
        if not items:
            _say("No custom LatinMandell bindings. Use: customize <label> dell N sense ...")
            return True
        for c in items:
            _say(f"  {c.get('label')}: la={c.get('la')} dell={c.get('dell')} — {c.get('sense')}")
        return True

    if lower.startswith("customize ") or lower.startswith("custom "):
        rest = raw.split(maxsplit=1)[1].strip()
        tokens = rest.split()
        if not tokens:
            _say("Usage: customize <label> [dell N] [sense ...]")
            return True
        label = tokens[0]
        dell = None
        sense_parts: list = []
        i = 1
        while i < len(tokens):
            t = tokens[i]
            if t.lower() in ("dell", "d") and i + 1 < len(tokens) and tokens[i + 1].isdigit():
                dell = int(tokens[i + 1])
                i += 2
                continue
            if t.lower() in ("sense", "as") and i + 1 < len(tokens):
                sense_parts = tokens[i + 1 :]
                break
            sense_parts.append(t)
            i += 1
        sense = " ".join(sense_parts).strip()
        out = customize(label, dell=dell, sense=sense or f"custom · {label}", la=label)
        if out.get("ok"):
            c = out["custom"]
            _say(f"Bound: {c.get('label')} → dell={c.get('dell')} · {c.get('sense')}")
            _say("Survives save/load.")
            if hasattr(p, "note_seed"):
                p.note_seed(14, "Bind", label[:24])
        else:
            _say(f"Could not customize: {out.get('error')}")
        return True

    return False


def _run_tutorial(p: Program) -> Program:
    # WO-5.1: Tutorial uses an explicitly isolated demo mode that cannot
    # accept into the user's ordinary owner state. The demo program has
    # its own acceptance policy; the user's program is untouched.
    from form.open import open_program
    demo_owner = f"DEMO_TUTORIAL_{p.owner}"
    dp = open_program(demo_owner)
    print()
    _say("Tutorial — offline acceptance path (~1 min)")
    _say(f"Demo mode: using isolated owner '{demo_owner}' (your '{p.owner}' state is untouched)")
    _say("Path: create → grow → confirm → sphere → save → load → visual")
    print()

    _say("Step 1 — create")
    dp.place("tutorial_seed", "Tutorial Seed", words="first idea", skin=Skin.CUBE)
    _say('Created idea: "Tutorial Seed"')
    print()

    _say("Step 2 — grow (Nursery only; live matrix unchanged)")
    out = dp.grow_ideas(1)
    _say(f"Proposed {out.get('proposed_new', 0)} new + {out.get('proposed_evolved', 0)} evolved.")
    _say(f"Nursery pending: {out.get('nursery', {}).get('pending', 0)}")
    print()

    _say("Step 3 — confirm (demo review: you are reviewing these)")
    pending = dp.list_proposals()
    n = 0
    for prop in list(pending):
        # Demo explicitly reviews each proposal before confirming.
        res = dp.confirm_proposal(
            prop["id"],
            _producer="tutorial_demo",
            _review_context=dp.make_review_context(prop["id"], "tutorial_demo"),
        )
        if res.get("ok"):
            n += 1
            _say(f'Confirmed: "{res.get("label", "")}"')
    if n == 0:
        _say("No proposals to confirm (still ok).")
    else:
        _say(f"Confirmed {n} proposal(s).")
    print()

    _say("Step 4 — sphere")
    dp.lattice.to_sphere()
    _say(f"Form → sphere  (skin={dp.lattice.perception.skin_name()})")
    print()

    _say("Step 5 — save")
    path = dp.save()
    _say(f"Demo session saved: {path}")
    print()

    _say("Step 6 — load")
    p2 = persist_load(dp.owner)
    _say(f"Demo session loaded for {p2.owner}. ideas={len(p2.cube.session.plane.units)}")
    print()

    _say("Step 7 — visual")
    paths = p2.visual()
    _say("Open this file in a browser (offline):")
    _say(paths.get("easy") or paths.get("html", ""))
    print()
    _say("Tutorial complete. Type help anytime. You are ready.")
    _say(f"(Demo used isolated owner '{demo_owner}'; your '{p.owner}' state was not modified.)")
    print()
    return p


def _show_proposals(p: Program) -> None:
    pending = p.list_proposals()
    if not pending:
        _say("Nursery is empty.")
        return
    _say(f"Nursery has {len(pending)} proposal(s):")
    for i, prop in enumerate(pending[:20], 1):
        aff = float(prop.get("affinity", 0))
        _say(f"  {i}. aff={aff:.3f} [{prop.get('kind')}] {prop['id']}")
        _say(f"      {prop['label']}")
    _say("Type: confirm <id> | confirm all | reject all | rank | lineage <id>")


def _handle_lattice(p: Program, lower: str, raw: str) -> bool:
    if lower in ("cube", "to cube", "form cube"):
        p.lattice.to_cube()
        _say(f"Form → cube  (skin={p.lattice.perception.skin_name()})")
        _echo_seed(mandel="15[Map] :: cube")
        return True
    if lower in ("sphere", "to sphere", "form sphere"):
        p.lattice.to_sphere()
        _say(f"Form → sphere  (skin={p.lattice.perception.skin_name()})")
        _echo_seed(mandel="15[Map] :: sphere")
        return True
    if lower in ("core", "to core", "form core"):
        p.lattice.to_core()
        _say(f"Form → core  (skin={p.lattice.perception.skin_name()})")
        _echo_seed(mandel="15[Map] :: core")
        return True
    if lower in ("flower", "to flower", "form flower"):
        n = p.lattice.plant_flower(2)
        geo = p.flower_geometry(2) if hasattr(p, "flower_geometry") else {}
        _say(f"Form → flower  planted {n} lattice cells · FoL centers={geo.get('center_count', '?')} vesicas={geo.get('vesica_count', '?')}")
        _echo_seed(mandel="15[Map] :: flower")
        return p

    if lower in ("flower geometry", "fol", "flower of life", "seed of life"):
        if p.lattice.perception.form.value != "flower":
            p.lattice.plant_flower(2)
        geo = p.flower_geometry(2)
        _say(f"Flower of Life · rings={geo['rings']} centers={geo['center_count']} circles={len(geo['circles'])}")
        _say(f"  Vesica pairs in FoL: {geo['vesica_count']}")
        _say(f"  Fruit of Life points: {len(geo.get('fruit') or [])}")
        # show top verita among FoL
        for v in (geo.get("vesicas") or [])[:4]:
            _say(f"  vesica verita={v.get('verita')} dist={v.get('distance')}")
        return p

    if lower in ("vesica", "verita", "veritas", "vesica edges"):
        edges = p.verita_edges() if hasattr(p, "verita_edges") else []
        _say(f"Verita/Vesica edges: {len(edges)} (coherence-of-meet between ideas)")
        for e in edges[:10]:
            _say(f"  {e.get('source')} ⇄ {e.get('target')}  verita={e.get('verita')}  [{e.get('type')}] d={e.get('distance')}")
        if not edges:
            _say("  (place nearby ideas or grow scores to form vesica meets)")
        return p

    if lower in ("voynich", "voynich rings", "rings", "five rings", "5 rings"):
        for line in p.voynich_ascii():
            _say(line)
        return p

    if lower in ("fractal", "fractals", "rule90", "rule 90"):
        fr = p.fractal_status(12)
        for line in fr.get("rule90_ascii") or []:
            _say(line)
        bo = fr.get("bounded_orbit") or {}
        _say(f"Bounded orbit C²+Δ final={bo.get('final')} series={bo.get('series')}")
        co = fr.get("complex_orbit") or {}
        _say(f"Complex z²+c |z|={co.get('final_mag')} escaped={co.get('escaped')}")
        _say(f"Sierpinski points={len(fr.get('sierpinski') or [])}")
        return p

    if lower in ("orbit", "bounded orbit", "coherence orbit"):
        fr = p.fractal_status(8)
        bo = fr.get("bounded_orbit") or {}
        _say(f"C_{'{n+1}'} = C_n² + Δ  · {bo.get('equation')}")
        _say(f"series={bo.get('series')}")
        _say(f"note: {bo.get('note')}")
        co = fr.get("complex_orbit") or {}
        _say(f"complex path steps={len(co.get('path') or [])} |z|={co.get('final_mag')}")
        return p

    if lower in ("geometry", "sacred geometry", "geometry status"):
        for line in p.geometry_ascii():
            _say(line)
        return p
        return True
    if lower in ("toggle", "toggle form", "dual"):
        new = p.lattice.toggle_form()
        _say(f"Form toggled → {new.value}")
        _echo_seed(mandel="04[Transform] :: toggle_form")
        return True
    if lower in ("lattice", "show lattice", "lattice status"):
        st = p.lattice.status()
        _say(f"size={st['size']} form={st['form']} dual={st['dual']} skin={st['skin']}")
        _say(f"cells={st['cells']} modules={st['modules']}")
        print()
        print(p.lattice.render_ascii())
        print()
        _echo_seed(mandel="09[Show] :: lattice")
        return True
    if lower.startswith("chord ") or lower == "chord":
        parts = raw.split()
        try:
            h = int(parts[1]) if len(parts) > 1 else 0
            v = int(parts[2]) if len(parts) > 2 else 0
            f = int(parts[3]) if len(parts) > 3 else 0
        except ValueError:
            h = v = f = 0
        chord = p.lattice.pull_chord(h, v, f)
        _say(f"Chord at ({h},{v},{f}):")
        for c in chord:
            mark = "●" if c["has_content"] else "·"
            _say(f"  {mark} {c['coords']}  {c['note']}  shell={c['shell']}  {c['label'] or '—'}")
        _echo_seed(mandel="35[Discover] :: chord")
        return True
    if lower.startswith("shell") or lower == "shell":
        parts = raw.split()
        try:
            n = int(parts[1]) if len(parts) > 1 else 0
        except ValueError:
            n = 0
        cells = p.lattice.cells_by_shell(n)
        _say(f"Shell {n}: {len(cells)} cell(s)")
        for c in cells[:24]:
            _say(f"  ({c.h},{c.v},{c.f})  {c.label or '—'}")
        return True
    return False


def _handle_ros_command(p: Program, raw: str) -> bool:
    """ROS-I read-only observability meta-commands.

    Returns True when the line was an observability command (handled).
    Every branch delegates to form/mandell/runtime_observe.py and only
    formats the result for display. No execution, no mutation, no
    persistence. Bare `trace` is deliberately NOT handled here.
    """
    from form.mandell import runtime_observe as ro

    lower = raw.strip().lower()
    parts = raw.strip().split()

    def _show_explain(arg: str) -> bool:
        e = ro.explain_dell(arg)
        if not e.get("ok"):
            _say(f"explain: {e.get('status')} — {e.get('detail')}")
            return True
        _say(f"Dell {e['address']} [{e['canonical_name']}] — {e['manor']}")
        _say(f"  class={e['classification']} · semantic={e['semantic_accessibility']}")
        _say(f"  authority: {e['execution_authority']}")
        pol = e.get("policy") or {}
        if pol.get("restriction") != "none":
            _say(f"  policy: {pol.get('restriction')} — {pol.get('reason')}")
        _say(f"  flows: {e['flow_compatibility']}")
        return True

    if lower.startswith("explain "):
        arg = parts[1] if len(parts) > 1 else ""
        # Only Dell addresses (numeric) are ROS-I; words/phrases fall through
        # to the existing latinmandell explainer (and live_visual's explain).
        import re as _re
        if _re.fullmatch(r"\d{1,3}", arg):
            return _show_explain(arg)
        return False

    if lower == "outcomes" or lower.startswith("outcomes "):
        # COO-I: subcommands for find/interaction; bare = recent list
        if lower.startswith("outcomes find "):
            query = raw.strip()[14:].strip()
            res = ro.find_outcomes(p, query)
            if not res.get("ok"):
                _say(f"outcomes find: {res.get('status')}")
                return True
            recs = res["outcomes"]
            if not recs:
                _say(f'No outcomes match "{query}".')
                return True
            _say(f'Outcomes matching "{query}" ({len(recs)}):')
            for r in recs:
                _say(f"  [{r.get('outcome_seq')}] {r.get('operation')}[{r.get('dell')}]"
                     f" · {r.get('result')} · {str(r.get('input') or '')[:50]}")
            _say("  inspect via: outcome <seq>  (e.g., outcome 5)")
            return True
        if lower.startswith("outcomes interaction "):
            ref = raw.strip()[21:].strip()
            # Accept seq or UUID for the interaction ref; resolve to ID
            # For now, treat ref as interaction_id directly (UUID)
            # TODO: allow seq-based interaction lookup if needed
            res = ro.outcomes_for_interaction(p, ref)
            if not res.get("ok"):
                _say(f"outcomes interaction: {res.get('status')}")
                return True
            recs = res["outcomes"]
            if not recs:
                _say(f"No outcomes for interaction {ref[:12]}...")
                return True
            _say(f"Interaction {ref[:12]}... → {len(recs)} outcome(s):")
            for r in recs:
                _say(f"  [{r.get('outcome_seq')}] {r.get('operation')}[{r.get('dell')}]"
                     f" · {r.get('result')}")
            _say("  (same originating interaction; siblings are not causally linked)")
            return True
        n = 10
        if len(parts) > 1 and parts[1].isdigit():
            n = int(parts[1])
        recs = ro.latest_outcomes(p, limit=n)
        if not recs:
            _say("No outcomes recorded.")
            return True
        _say(f"Latest {len(recs)} outcomes (observation only — not truth):")
        for r in recs:
            _say(f"  [{r.get('outcome_seq')}] {r.get('operation')}[{r.get('dell')}]"
                 f" · {r.get('result')}")
        _say("  inspect via: outcome <seq>  (e.g., outcome 5)")
        return True

    if lower.startswith("outcome "):
        ref = parts[1] if len(parts) > 1 else ""
        # COO-I: accept seq number or full UUID
        res = ro.resolve_outcome_ref(p, ref)
        if not res.get("ok"):
            _say(f"outcome: {res.get('status')} — {res.get('detail')}")
            return True
        r = res["outcome"]
        _say(f"[{r.get('outcome_seq')}] {r.get('outcome_id')}")
        _say(f"  {r.get('operation')}[{r.get('dell')}] · {r.get('result')}")
        _say(f"  input: {str(r.get('mandell') or r.get('input'))[:80]}")
        _say(f"  semantic: {r.get('semantic')}")
        iid = r.get("interaction_id")
        _say(f"  interaction: {iid[:12] + '...' if iid else 'UNKNOWN'}")
        if r.get("error"):
            _say(f"  error: {str(r.get('error'))[:80]}")
        return True

    if lower in ("trace last",) or (lower.startswith("trace ") and lower != "trace"):
        arg = raw.strip()[6:].strip()
        # COO-I: accept "last", seq number, or UUID
        oid = None
        if arg.lower() != "last":
            res = ro.resolve_outcome_ref(p, arg)
            if not res.get("ok"):
                _say(f"trace: {res.get('status')} — {res.get('detail')}")
                return True
            oid = res["outcome"]["outcome_id"]
        t = ro.execution_trace(p, outcome_id=oid)
        if not t.get("ok"):
            _say(f"trace: {t.get('status')} — {t.get('detail')}")
            return True
        _say(f"trace {t.get('outcome_id')} (observation only — not truth)")
        _say(f"  input: {str(t.get('input_understood'))[:80]}")
        rt = t.get("resolved_to") or {}
        _say(f"  resolved: {rt.get('operation')}[{rt.get('dell')}]")
        atoms = t.get("ordered_atoms") or []
        _say(f"  atoms: {' > '.join(a.get('mandell', '') for a in atoms) or '—'}")
        _say(f"  flow: {t.get('flow_used') or '—'}")
        wh = t.get("what_happened") or {}
        _say(f"  result: {wh.get('result')}")
        iid = t.get("interaction_id")
        _say(f"  interaction: {iid[:12] + '...' if iid and iid != 'UNKNOWN' else 'UNKNOWN'}")
        return True

    # ODCG-I: correction candidate explanation
    if lower.startswith("what fixed "):
        from form.mandell import correction_graph as cg
        oid = raw.strip()[11:].strip()
        exp = cg.explain_correction(p, oid)
        if not exp.get("ok"):
            _say(f"what fixed: {exp.get('explanation')}")
            return True
        _say(f"correction candidates for {oid} (correlation, not proven causation):")
        _say(f"  {exp.get('explanation')}")
        for c in exp.get("candidates", [])[:3]:
            _say(f"  → {c['later_outcome_id']} [{c['confidence']}]")
        for unk in exp.get("what_we_do_not_know", []):
            _say(f"  unknown: {unk}")
        return True

    if lower == "health":
        h = ro.runtime_health(owner=getattr(p, "owner", "Operator"))
        _say("runtime health (availability only — not intelligence/truth):")
        for name, c in (h.get("components") or {}).items():
            mark = "ok" if c.get("available") else "MISSING"
            _say(f"  [{mark}] {name}: {c.get('detail')}")
        return True

    if lower == "runtime":
        s = ro.runtime_state(p)
        _say(f"runtime state · owner={s.get('owner')}")
        _say(f"  generation: {s.get('current_generation')}")
        oc = (s.get("outcomes") or {})
        _say(f"  outcomes: total={oc.get('total')} counts={oc.get('counts')}")
        le = (s.get("last_execution") or {})
        _say(f"  last execution: {le.get('status')}"
             + (f" · {le.get('operation')}[{le.get('dell')}] {le.get('result')}"
                if le.get("status") == "known" else ""))
        return True

    # ── NBDE-I (NBD-Ω-009): read-only NBD inspection ───
    # Respects existing `nbd` (G2 next_directives); these are subcommands.
    if lower == "nbd rank" or lower == "nbd ranking":
        v = ro.nbd_view(p)
        if not v.get("ok"):
            _say(f"nbd: {v.get('error')}")
            return True
        _say(f"nbd ranking · {len(v['ranked'])} READY · "
             f"stale={v['stale']} · AUTONOMY={v['AUTONOMY']}")
        for r in v["ranked"][:8]:
            _say(f"  #{r['rank']} {r['candidate_id']}: "
                 f"NW={r['next_weight']} RV={r['route_value']}")
        if v.get("batches"):
            _say("batches (proposals, not mutations):")
            for b in v["batches"]:
                _say(f"  {b['batch_id']}: {', '.join(b['members'])}")
        top = v.get("top_proposal") or {}
        if top:
            _say(f"top: {top.get('candidate_id')} — "
                 f"{top.get('title')}")
        _say("DIRECTOR_DECISION_REQUIRED=YES · EXECUTION_AUTHORITY=NONE")
        return True

    if lower.startswith("nbd candidate "):
        cid = raw.strip()[14:].strip()
        v = ro.nbd_view(p, candidate_id=cid)
        if not v.get("ok"):
            _say(f"nbd: {v.get('error')}")
            return True
        c = v["candidate"]
        _say(f"nbd candidate {c['candidate_id']} · state={c['state']}")
        _say(f"  title: {c['title']}")
        _say(f"  target: {c['target_circuit']} · locality: {c['locality']}")
        if c.get("blocked_reason"):
            _say(f"  blocked: {c['blocked_reason']}")
        _say(f"  evidence: {len(c.get('evidence', []))} items")
        for e in c.get("evidence", [])[:4]:
            _say(f"    [{e.get('kind')}] {e.get('source')}: "
                 f"{e.get('detail')[:70]}")
        return True

    if lower == "nbd evidence":
        v = ro.nbd_view(p)
        if not v.get("ok"):
            _say(f"nbd: {v.get('error')}")
            return True
        _say(f"nbd evidence · fingerprint {v.get('fingerprint_hash')} "
             f"· stale={v['stale']}")
        _say("  (per-candidate evidence: nbd candidate <id>)")
        return True

    # ── LEAS-I (NBD-Ω-011): read-only circuit inspection ───
    if lower == "circuits":
        v = ro.circuits_view(p)
        _say(f"circuits · {v['total']} total (canonical ledger)")
        for state in sorted(v["by_state"]):
            ids = v["by_state"][state]
            _say(f"  {state}: {len(ids)} ({', '.join(ids[:6])}"
                 f"{'...' if len(ids) > 6 else ''})")
        return True

    if lower.startswith("circuit "):
        cid = raw.strip()[8:].strip().upper()
        v = ro.circuit_view(p, cid)
        if not v.get("found"):
            _say(f"circuit {cid}: not found")
            return True
        _say(f"circuit {v['circuit_id']} · state={v['state']} "
             f"· locality={v['locality']}")
        _say(f"  title: {v['title']}")
        _say(f"  evidence: {v['evidence']}")
        if v.get("closure_cycle"):
            _say(f"  closed by: {v['closure_cycle']}")
        if v.get("notes"):
            _say(f"  notes: {v['notes']}")
        return True

    return False


def _handle_learn_command(p: Program, raw: str) -> bool:
    """DLA-I: DuoBeta learning activation user surface.

    Wires the existing duobeta_learn.py lifecycle (extract → propose →
    gate → apply) to explicit user commands. AUTONOMY=NO: proposal and
    application are separate; apply requires explicit "confirm" and an
    ACCEPTED gate. Read-only inspection via existing ROS views.

    Returns True when the line was a learn command (handled).
    """
    from form.mandell import duobeta_learn as dl

    lower = raw.strip().lower()
    parts = raw.strip().split()
    if not lower.startswith("learn"):
        return False
    # "learn", "learned", "learning" (paraphrase stats) are not DLA-I commands.
    if lower == "learn" or not lower.startswith("learn "):
        return False

    sub = parts[1].lower() if len(parts) > 1 else ""

    if sub == "propose":
        # learn propose <kind> <dell> from <oid> [<oid> ...]
        # kind ∈ {preference, avoidance, blocked_association}
        if len(parts) < 6 or parts[4].lower() != "from":
            _say("usage: learn propose <kind> <dell> from <outcome-id> [<outcome-id> ...]")
            _say("  kind: preference | avoidance | blocked_association")
            return True
        kind = parts[2].lower()
        dell = parts[3]
        oids = parts[5:]
        res = dl.propose(p, kind, dell, evidence_outcome_ids=oids)
        if not res.get("ok"):
            _say(f"learn propose: failed — {res.get('reason') or res.get('detail')}")
            return True
        _say(f"proposal {res['proposal_id']} staged (PROPOSED — not yet gated, not applied)")
        _say(f"  kind={res['kind']} dell={res['dell']} knowledge={res['knowledge_id']}")
        _say(f"  evidence: {', '.join(res['evidence_outcome_ids']) or '—'}")
        _say(f"  next: learn gate {res['proposal_id']}")
        return True

    if sub == "inspect":
        # learn inspect <proposal-id>
        pid = parts[2] if len(parts) > 2 else ""
        prop = dl.get_proposal(p, pid)
        if not prop:
            _say(f"learn inspect: unknown proposal {pid!r}")
            return True
        _say(f"proposal {prop['proposal_id']} [{prop['status']}]")
        _say(f"  kind={prop['kind']} dell={prop['dell']} knowledge={prop['knowledge_id']}")
        _say(f"  evidence: {', '.join(prop['evidence_outcome_ids']) or '—'}")
        gate = prop.get("gate") or {}
        if gate:
            _say(f"  gate: {'ACCEPTED' if gate.get('accepted') else 'REJECTED'}"
                 f" — {gate.get('reason')}")
        if prop.get("reason"):
            _say(f"  reason: {prop['reason']}")
        return True

    if sub == "gate":
        # learn gate <proposal-id>
        pid = parts[2] if len(parts) > 2 else ""
        if not pid.isdigit():
            # CND-I: malformed input must not crash the REPL. Validate before
            # calling the authority; the authority contract for int(pid) is
            # unchanged.
            _say("usage: learn gate <proposal-id>")
            _say("  gate a PROPOSED learning proposal (see: learn ledger)")
            return True
        res = dl.gate_proposal(p, pid)
        if not res.get("ok"):
            _say(f"learn gate: {res.get('reason')}")
            return True
        if res.get("accepted"):
            _say(f"proposal {res['proposal_id']}: GATE ACCEPTED — {res.get('reason')}")
            _say(f"  supporting outcomes: {len(res.get('supporting') or [])}")
            _say(f"  next: learn apply {res['proposal_id']} confirm")
            _say("  (application requires explicit authorization)")
        else:
            _say(f"proposal {res['proposal_id']}: GATE REJECTED — {res.get('reason')}")
            _say("  (rejected proposals are retained with reason; they are not applied)")
        return True

    if sub == "apply":
        # learn apply <proposal-id> confirm
        # The "confirm" keyword is the explicit authorization. Without it,
        # nothing is applied.
        pid = parts[2] if len(parts) > 2 else ""
        confirmed = len(parts) > 3 and parts[3].lower() == "confirm"
        if not confirmed:
            prop = dl.get_proposal(p, pid)
            status = (prop or {}).get("status", "unknown")
            _say(f"learn apply {pid}: explicit authorization required.")
            _say(f"  proposal status: {status}")
            _say(f"  to apply, run: learn apply {pid} confirm")
            _say("  (only ACCEPTED proposals can be applied)")
            return True
        if not pid.isdigit():
            # CND-I: malformed input must not crash the REPL. Validate before
            # calling the authority; the authority contract for int(pid) is
            # unchanged.
            _say("usage: learn apply <proposal-id> confirm")
            _say("  apply an ACCEPTED learning proposal (explicit authorization)")
            return True
        res = dl.apply_proposal(p, pid)
        if not res.get("applied"):
            _say(f"learn apply: not applied — {res.get('reason')}")
            return True
        _say(f"proposal {res['proposal_id']}: APPLIED to DuoBeta learned state")
        _say("  (advisory influence only — not truth, not causation)")
        return True

    if sub == "ledger":
        # learn ledger — inspect learned state (read-only, via ROS)
        from form.mandell import runtime_observe as ro
        v = ro.learning_ledger_view(p)
        entries = v.get("entries") or []
        if not entries:
            _say("DuoBeta learning ledger: empty (no proposals yet)")
            return True
        _say(f"DuoBeta learning ledger ({len(entries)} entries):")
        for e in entries[-10:]:
            _say(f"  #{e.get('proposal_id')} [{e.get('status')}] {e.get('kind')}"
                 f" dell={e.get('dell')} knowledge={e.get('knowledge_id')}")
        return True

    _say("learn commands: propose | inspect | gate | apply | ledger")
    _say("  learn propose <kind> <dell> from <outcome-id> ...")
    _say("  learn inspect <proposal-id> · learn gate <proposal-id>")
    _say("  learn apply <proposal-id> confirm · learn ledger")
    return True


def _handle_why_command(p: Program, raw: str) -> bool:
    """KIE-I: Knowledge Influence explanation commands.

    Read-only. Delegates to ROS knowledge_influence_view / why_used_view /
    why_not_used_view. Never selects, scores, or mutates.

    Commands:
      why used <knowledge-id> in <outcome-id>
      why not used <knowledge-id> [for <context>]
      why influence <knowledge-id> [in <outcome-id>] [for <context>]
    """
    from form.mandell import runtime_observe as ro

    lower = raw.strip().lower()
    if lower == "why":
        # Bare `why`: teach the syntax. No conflict: no other handler or
        # test claims bare "why" (verified CND-I).
        _say("why commands (read-only explanation):")
        _say("  why used <knowledge-id> in <outcome-id>")
        _say("  why not used <knowledge-id> [for <context>]")
        _say("  why influence <knowledge-id> [in <outcome-id>] [for <context>]")
        return True
    if not lower.startswith("why "):
        return False
    parts = raw.strip().split()

    def _fmt_chain(chain: dict) -> None:
        order = ["STORED", "ELIGIBLE", "SELECTED", "ROUTABLE", "USED", "OBSERVED", "LEARNED"]
        for state in order:
            s = chain.get(state) or {}
            status = s.get("status", "?")
            if status == "FACT":
                detail = s.get("reason") or s.get("detail") or ""
                if s.get("eligible") is False:
                    detail = f"NOT ELIGIBLE: {s.get('reason')}"
                elif s.get("selected") is True:
                    detail = f"selected (rank {s.get('rank')})"
                elif s.get("selected") is False:
                    detail = f"not selected: {s.get('reason')}"
                _say(f"  {state}: {detail or 'yes'}")
            elif status == "DERIVED_FACT":
                _say(f"  {state}: {s.get('reason', '')} (derived)")
            else:
                _say(f"  {state}: UNKNOWN — {s.get('reason', '')}")

    # why used <kid> in <oid>
    if len(parts) >= 5 and parts[1].lower() == "used" and parts[3].lower() == "in":
        kid, oid = parts[2], parts[4]
        res = ro.why_used_view(p, kid, oid)
        if res.get("error"):
            _say(f"why used: {res['error']}")
            return True
        _say(f"{res.get('question')}")
        ans = res.get("answer", {})
        used = ans.get("used", {})
        _say(f"  recorded as used: {used.get('reason', '')}")
        _say(f"  outcome: {ans.get('observed_in')}")
        _say(f"  revision: {ans.get('revision')}")
        _say(f"  {res.get('epistemic', '')}")
        return True

    # why not used <kid> [for <context...>]
    if len(parts) >= 4 and parts[1].lower() == "not" and parts[2].lower() == "used":
        kid = parts[3]
        ctx = None
        if "for" in [w.lower() for w in parts]:
            fi = [w.lower() for w in parts].index("for")
            ctx = " ".join(parts[fi + 1:])
        res = ro.why_not_used_view(p, kid, context=ctx)
        if res.get("error"):
            _say(f"why not used: {res['error']}")
            return True
        _say(f"{res.get('question')}")
        for b in res.get("blocking_reasons", []):
            _say(f"  blocked at {b['state']}: {b['reason']}")
        if not res.get("blocking_reasons"):
            _say("  no blocking reasons found (may be eligible)")
        return True

    # why influence <kid> [in <oid>] [for <context>]
    if len(parts) >= 3 and parts[1].lower() == "influence":
        kid = parts[2]
        oid = None
        ctx = None
        low = [w.lower() for w in parts]
        if "in" in low:
            ii = low.index("in")
            if ii + 1 < len(parts):
                oid = parts[ii + 1]
        if "for" in low:
            fi = low.index("for")
            ctx = " ".join(parts[fi + 1:])
        res = ro.knowledge_influence_view(p, kid, outcome_id=oid, context=ctx)
        if res.get("error"):
            _say(f"why influence: {res['error']}")
            return True
        _say(f"knowledge influence for {kid} ({res.get('mode', '?')}):")
        _fmt_chain(res.get("chain", {}))
        return True

    _say("why commands (read-only explanation):")
    _say("  why used <knowledge-id> in <outcome-id>")
    _say("  why not used <knowledge-id> [for <context>]")
    _say("  why influence <knowledge-id> [in <outcome-id>] [for <context>]")
    return True


def _handle_macro_rank(p: Program, lower: str, raw: str) -> bool:
    if lower in ("rank", "rank proposals"):
        ranked = p.ranked_proposals() if hasattr(p, "ranked_proposals") else p.list_proposals()
        if not ranked:
            _say("Nursery is empty.")
            return True
        _say(f"Ranked {len(ranked)} proposals:")
        for i, prop in enumerate(ranked[:12], 1):
            _say(
                f"  {i}. aff={float(prop.get('affinity', 0)):.3f} "
                f"[{prop.get('kind')}] {prop.get('id')} — {prop.get('label')}"
            )
        _echo_seed(mandel="46[Rank]")
        return True

    if lower == "macro" or lower.startswith("macro "):
        parts = raw.split()
        n = 5
        if len(parts) > 1 and parts[1].isdigit():
            n = int(parts[1])
        seed = p.macro_seed(n)
        _say(seed)
        _say(f"history={len(p.history)}")
        _echo_seed(mandel=f"48[Macro] :: {n}")
        return True

    if lower == "replay" or lower.startswith("replay "):
        parts = raw.split()
        n = 3
        if len(parts) > 1 and parts[1].isdigit():
            n = int(parts[1])
        if hasattr(p, "replay_exec"):
            out = p.replay_exec(n)
            _say(f"Replay n={n} ran={len(out.get('ran', []))} skipped={len(out.get('skipped', []))}")
            for item in out.get("ran", [])[:8]:
                _say(f"  · {item}")
            for item in out.get("skipped", [])[:4]:
                _say(f"  skip {item}")
        else:
            for item in p.replay(n):
                _say(f"  · {item}")
        _echo_seed(mandel="48[Macro] >> 13[Loop] :: replay")
        return True

    if lower.startswith("distill") or lower.startswith("summarize"):
        text = raw.split(maxsplit=1)[1] if " " in raw else ""
        if not text and p.cube.session.plane.units:
            last = list(p.cube.session.plane.units.values())[-1]
            text = f"{last.label} {last.words}"
        short = p.distill_label(text)
        p.place(short, short.replace("_", " "), words=text or short, skin=Skin.SEED)
        _say(f"Distilled → {short}")
        _echo_seed(mandel=f"38[Distill] :: {short}")
        return True

    return False


def _apply_seed_result(p: Program, result: dict) -> Program:
    for msg in result.get("messages") or []:
        if msg == "__RENDER__":
            print()
            print(p.render())
        else:
            _say(msg)
    if result.get("new_program") is not None:
        p2 = result["new_program"]
        print()
        print(p2.render())
        return p2
    return p


def _execute_intent(p: Program, intent, raw_line: str = "", _normalized: bool = False,
                  interaction_id: Optional[str] = None) -> Program:
    # MPC-008: macro-definition capability is not established. A request to
    # make/create a macro must not masquerade as idea creation (the synonym
    # layer would rewrite it to "create an idea called macro"). Fail honestly
    # with no mutation. Literal "create an idea called macro" (contains
    # "idea") remains legitimate idea creation. Checked on the raw line:
    # normalization would erase the distinction.
    if not _normalized and raw_line and re.search(
            r"\b(make|create)\s+(?:a\s+)?macros?\b", raw_line, re.IGNORECASE) \
            and not re.search(r"\bidea\b", raw_line, re.IGNORECASE):
        _say("Macro definition is not supported in this build.")
        _echo_seed(mandel="09[Show] :: unknown")
        return p
    # EIC-I: interaction_id is accepted (not minted) here, forwarded to
    # route_intent calls. None = UNKNOWN (direct/API callers).
    # DCC-I: program-evolution ("evolve") is documented as growing the program
    # (DuoBeta generation + forces + pillars), but the english_brain synonym
    # "evolve"->"grow" reroutes it to idea growth before any handler runs.
    # Intercept the raw program-evolve intents here so the documented operation
    # is actually reachable; idea growth stays on "grow".
    if not _normalized and raw_line:
        el = raw_line.lower().strip()
        if el in ("evolve", "evolve program", "grow program", "level up") or (
            el.startswith("evolve ") and not el.startswith("evolve loop")
        ):
            detail = "manual evolve"
            if el.startswith("evolve "):
                detail = raw_line.split(None, 1)[1].strip()[:120] or detail
            out = p.evolve(detail)
            _say(f"Evolved · generation={out.get('generation')}")
            _say(f"Ledger: {detail}")
            pillars = out.get("pillars") or {}
            _say(f"Pillars {pillars.get('label')} avg={pillars.get('average')}")
            # SAOC-II: observe specialized program evolution. Existing
            # execution unchanged; this only captures Outcome evidence with
            # the public interaction_id. Honest: no Dell/Mandell fabricated.
            try:
                from form.mandell.execution_observer import observe_specialized_execution
                ok = bool(out.get("ok", True))
                observe_specialized_execution(
                    p,
                    action="evolve",
                    input_text=raw_line,
                    ok=ok,
                    error="" if ok else str(out.get("error") or out.get("pillars_error") or ""),
                    messages=[
                        f"Evolved · generation={out.get('generation')}",
                        f"Pillars {(out.get('pillars') or {}).get('label')}",
                    ],
                    semantic="evolve[program:specialized]",
                    interaction_id=interaction_id,
                )
            except Exception:
                pass
            return p

    # Program understanding: re-route natural English → canonical command handlers
    # MPC-008: checkpoint-restore language must survive synonym normalization
    # ("restore" -> "load" would otherwise erase the checkpoint reading, and
    # the recursive call receives only normalized text). "revert" keeps Dell28
    # (translate.py:198; dcc_vi_test pins revert -> 28[Rollback]). Bare or
    # checkpoint-qualified "restore" keeps Dell28 ("Restore checkpoint" is
    # Dell28's canonical English — genuinely ambiguous, not guessed). The
    # session family (resume/reload/reopen/recover/load, "restore ... session/
    # work") goes to persist_load per Director ruling: silent checkpoint
    # rollback on ordinary "resume" destroyed uncommitted work (proven
    # PUBLIC_END_TO_END).
    _checkpoint_lang = False
    if not _normalized and raw_line:
        _rl = raw_line.lower()
        if re.search(r"\brevert\b", _rl):
            _checkpoint_lang = True
        elif re.search(r"\brestore\b", _rl) and not re.search(
                r"\bsession\b|\bwork\b", _rl):
            _checkpoint_lang = True
        try:
            from form.mandell.english_brain import normalize_english
            from form.mandell.translate import translate as _tr
            norm, path = normalize_english(raw_line)
            n = (norm or "").strip()
            if (
                n
                and path in ("paraphrase", "synonym", "learned", "strip")
                and n.lower() != raw_line.lower().strip()
                and not _checkpoint_lang
            ):
                return _execute_intent(p, _tr(n), raw_line=n, _normalized=True,
                                       interaction_id=interaction_id)
        except Exception:
            pass

    # R6.3: intercept "restore confirm <generation>" BEFORE translate
    # (the word "confirm" would otherwise route to Dell 37/Nurture).
    # Bare "restore"/"revert" also handled here: freeze+describe, never
    # execute. Typing "restore" alone is never approval.
    if _checkpoint_lang and raw_line:
        from form.dell_matrix import rollback_authority as _ra
        _m = re.search(r"\bconfirm\s+([A-Za-z0-9_.\-]+)",
                       raw_line, re.IGNORECASE)
        if _m:
            _gen = _m.group(1)
            try:
                _frozen = _ra.freeze_rollback_target(p.owner, _gen)
            except _ra.RollbackTargetError as _exc:
                _say(f"Restore denied: cannot freeze target: {_exc}")
                return p
            _policy = getattr(p, "acceptance_policy", None)
            if _policy is None:
                _say("Restore denied: no acceptance policy (fail closed).")
                return p
            _live = _ra._live_fingerprints(p.owner)
            _data = _ra.rollback_content(_frozen, _live)
            _issued = _policy.issue_approval(
                operation=_ra.ROLLBACK_OPERATION, target=_gen,
                reviewer="human", data=_data,
                note="repl-human restore confirm")
            _res = p.confirm_rollback(
                _gen,
                _review_context={"approval_id":
                                 _issued["context"]["approval_id"]},
                _subject="human", _producer="repl-human")
            if _res.get("ok"):
                _say(f"Restored generation {_res['generation_id']}.")
                _say(f"  Compensating checkpoint: "
                     f"{_res['compensating_generation_id']}")
                _say("  (Pre-rollback state preserved; "
                     "restore it to undo.)")
                from form import persist_rest as _pr
                return _pr.load(p.owner)
            _say(f"Restore denied ({_res.get('reason')}): "
                 f"{_res.get('detail', '')[:200]}")
            return p
        # Bare restore/revert: freeze and describe; do not execute.
        if re.search(r"\b(restore|revert)\b", raw_line, re.IGNORECASE):
            try:
                _frozen = _ra.freeze_rollback_target(p.owner, None)
            except _ra.RollbackTargetError as _exc:
                _say(f"Restore unavailable: {_exc}")
                return p
            _say("Restore requires explicit approval. This would:")
            _say(f"  - roll back to generation {_frozen['generation_id']}")
            _say(f"  - seal a safety checkpoint of current state first")
            _say(f"  - discard uncommitted work after the safety checkpoint")
            _say(f"To approve, type: restore confirm {_frozen['generation_id']}")
            return p

    action = intent.action
    args = intent.args or {}
    lower = raw_line.lower().strip()

    if lower in ("tutorial", "start", "walkthrough"):
        return _run_tutorial(p)

    if lower in ("help", "?"):
        print()
        print(HELP_SHORT)
        print()
        return p

    if lower in ("help more", "help full", "more"):
        print()
        print(HELP_MORE)
        print()
        return p

    if lower.startswith("help "):
        # CN-II: grouped navigation — help <category> shows exact syntax.
        cat = lower[5:].strip()
        if cat in HELP_CATEGORIES:
            print()
            print(HELP_CATEGORIES[cat])
            print()
            return p
        # Unknown category: suggest valid ones (suggest, not auto-execute).
        _say(f'Unknown help category "{cat}".')
        _say("  Try: " + " | ".join(f"help {k}" for k in HELP_CATEGORIES))
        return p

    # Live two-way visual (opt-in) — first-person centerpoint walk
    if lower in ("live", "visual live", "live visual", "livevisual"):
        if hasattr(p, "live_visual"):
            p.view_mode = "first_person"
            p.grid_snap = True
            out = p.live_visual()
            _say("Live visual started (localhost only) — FIRST PERSON inside the matrix.")
            _say(out.get("url", ""))
            _say("You are at a centerpoint. Move block-to-block. Look for pages (not a vision cone).")
            _say("Keys: WASD move/turn · R/F up/down · Q/E look · Space level")
            _echo_seed(mandel="09[Show] :: live_visual")
        else:
            _say("live_visual not available on this Program build.")
        return p

    if lower in ("view first", "first person", "fp mode"):
        p.view_mode = "first_person"
        _say("View mode → first_person (inside centerpoints)")
        return p
    if lower in ("view map", "map mode"):
        p.view_mode = "map"
        _say("View mode → map (legacy)")
        return p

    if lower.startswith("fp ") or lower in ("fp",):
        from form.dell_matrix import first_person as fpmod
        rest = lower[3:].strip() if lower.startswith("fp ") else "look"
        if rest in ("forward", "back", "left", "right", "up", "down"):
            out = p.fp_move(rest)
            _say(f"Center → {out.get('center')} ({rest})")
        elif rest in ("turn left", "left turn"):
            out = p.fp_turn("left")
            _say(f"Face {out.get('yaw')}")
        elif rest in ("turn right", "right turn"):
            out = p.fp_turn("right")
            _say(f"Face {out.get('yaw')}")
        elif rest.startswith("look"):
            pitch = rest.split()[1] if len(rest.split()) > 1 else "level"
            out = p.fp_look(pitch)
            _say(f"Look {out.get('pitch')}")
            v = out.get("view") or {}
            for pg in (v.get("looking") or {}).get("pages") or []:
                if not pg.get("empty"):
                    _say(f"  · {pg.get('title')} [{pg.get('skin')}] res={pg.get('resonance')}")
        else:
            v = p.first_person()
            _say(f"At {v.get('center')} face {v.get('yaw')} pitch {v.get('pitch')} form={v.get('form')}")
            _say(v.get("hint", ""))
        return p

    if lower.startswith("goto "):
        parts = lower.split()
        try:
            hh, vv = int(parts[1]), int(parts[2])
            ff = int(parts[3]) if len(parts) > 3 else 0
            out = p.fp_goto(hh, vv, ff)
            _say(f"Goto center {out.get('center')}")
        except Exception:
            _say("usage: goto H V [F]")
        return p

    # Looking / pages / UX (Phases A–E)
    if lower in ("look", "see", "vision", "look around"):
        for line in p.look_report():
            _say(line)
        return p

    # Inspire Pack (offline · video-distilled)
    if lower in ("inspire", "inspire status", "inspire pack"):
        st = p.inspire_status() if hasattr(p, "inspire_status") else {}
        pref = st.get("prefs") or {}
        _say("Inspire Pack (offline · educational stubs)")
        _say(f"  prefs: confirms={pref.get('confirms', 0)} rejects={pref.get('rejects', 0)} tokens={pref.get('tokens', 0)}")
        _say(f"  score samples={st.get('score_samples', 0)} · vision mem={st.get('vision_memory', 0)}")
        _say(f"  sprite action={((st.get('sprite') or {}).get('action'))} · layers={st.get('multivision_layers') or []}")
        for t, w in (pref.get("top") or [])[:6]:
            _say(f"  pref {t}: {w:+.3f}")
        return p

    if lower in ("multilook", "multi look", "multi-look", "multiscale"):
        mv = p.multilook() if hasattr(p, "multilook") else {}
        layers = mv.get("layers") or {}
        _say("Multi-scale vision:")
        for name in ("near", "mid", "far"):
            layer = layers.get(name) or {}
            nearest = layer.get("nearest")
            nlab = (nearest or {}).get("label") if isinstance(nearest, dict) else nearest
            _say(f"  {name}: count={layer.get('count', 0)} nearest={nlab or '—'}")
        for r in (mv.get("recent") or [])[:6]:
            _say(f"  mem · {r.get('label') or r.get('id')} ({r.get('scale')})")
        return p

    if lower.startswith("attend ") or lower in ("attend", "attention"):
        q = raw_line.split(maxsplit=1)[1].strip() if lower.startswith("attend ") else "growth seed idea"
        ranked = p.attend(q) if hasattr(p, "attend") else []
        if not ranked:
            _say(f"No ideas to attend for: {q}")
            return p
        _say(f"Attention · query={q!r}")
        for i, row in enumerate(ranked, 1):
            _say(
                f"  {i}. [{row.get('id')}] {row.get('label')}  "
                f"score={row.get('score')} att={row.get('attention')}"
            )
        return p

    if lower in ("slopes", "slope", "calculus", "score slopes", "ds/dt"):
        for line in (p.slopes_report() if hasattr(p, "slopes_report") else ["No slope data"]):
            _say(line)
        return p

    if lower in ("prefs", "preferences", "pref", "preference ledger"):
        st = p.prefs_status() if hasattr(p, "prefs_status") else {}
        _say(
            f"Preference ledger · confirms={st.get('confirms', 0)} "
            f"rejects={st.get('rejects', 0)} tokens={st.get('tokens', 0)}"
        )
        _say("  (confirm boosts · reject dampens — not pure imitation)")
        for t, w in (st.get("top") or [])[:10]:
            _say(f"  {t}: {w:+.3f}")
        return p

    if lower.startswith("glyph") or lower in ("proc glyph", "procedural"):
        seed = raw_line.split(maxsplit=1)[1].strip() if " " in raw_line.strip() else (p.owner or "matrix")
        art = p.glyph(seed) if hasattr(p, "glyph") else ""
        for line in (art or f"(glyph {seed})").splitlines():
            _say(line)
        return p

    if lower.startswith("script ") or lower.startswith("script:"):
        body = raw_line.split(maxsplit=1)[1] if " " in raw_line else ""
        if body.startswith(":"):
            body = body[1:].strip()
        if not body:
            _say("usage: script look; pulse; status")
            return p
        out = p.run_script(body) if hasattr(p, "run_script") else {"ok": False}
        _say(f"Script · ran={out.get('ran', 0)} passed={out.get('passed', 0)}")
        for r in (out.get("results") or [])[:12]:
            mark = "ok" if r.get("ok") else "fail"
            _say(f"  [{mark}/{r.get('cost')}] {r.get('cmd')}: {(r.get('msg') or '')[:60]}")
        return p

    if lower in ("entities", "entity list", "what is here", "who's here", "who is here"):
        ents = p.all_entities() if hasattr(p, "all_entities") else []
        by: dict = {}
        for e in ents:
            by.setdefault(e.get("kind") or "?", []).append(e)
        for kind, items in sorted(by.items()):
            _say(f"[{kind}] ×{len(items)}")
            for e in items[:12]:
                pos = e.get("pos")
                pos_s = f" @ {pos}" if pos is not None else ""
                extra = e.get("skin") or e.get("mode") or e.get("form") or e.get("doing") or ""
                extra_s = f" · {extra}" if extra else ""
                _say(f"  · {e.get('label') or e.get('id')}{pos_s}{extra_s}")
        return p

    # --- src/ matrices ported: rooms, forces, personas, evolve, audit, matrices ---
    if lower in ("rooms", "view rooms", "viewrooms"):
        for line in (p.view_status().get("ascii") or []):
            _say(line)
        _say("Rooms: " + ", ".join(r["id"] for r in p.view_status().get("rooms") or []))
        return p

    if lower.startswith("view "):
        room = lower.split(maxsplit=1)[1].strip()
        out = p.set_view(room)
        if not out.get("ok"):
            _say(f"Unknown room: {room}")
            _say("Try: " + ", ".join(r["id"] for r in out.get("rooms") or []))
        else:
            v = out["view"]
            _say(f"View room → {v.get('emoji')} {v.get('name')}: {v.get('description')}")
            for line in p.view_status().get("ascii") or []:
                _say(line)
        return p

    if lower in ("forces", "force status", "nature forces"):
        st = p.force_status()
        _say(f"Active forces: {', '.join(st.get('active') or [])}")
        _say(f"Breath {st.get('breath')} · weather {st.get('weather')} · time tick {st.get('time_tick')}")
        _say(f"Water streams={st.get('water_streams')} pools={st.get('water_pools')}")
        for line in st.get("growth_map") or []:
            _say(line)
        if st.get("gravity_wells"):
            _say("Gravity wells: " + ", ".join(
                f"{w.get('label')}(m={w.get('mass'):.1f})" for w in st["gravity_wells"][:5]
            ))
        return p

    if lower in ("force tick", "forces tick", "tick forces"):
        rep = p.force_tick()
        _say(f"Force tick · active {', '.join(rep.get('forces') or [])}")
        if rep.get("breath"):
            _say(f"  breath cycle {rep['breath'].get('inhale', {}).get('cycle')}")
        return p

    # Phase 4: canonical spatial authority — public REPL surface
    if lower in ("spatial tick", "tick spatial"):
        rep = p.force_tick()["spatial"]
        _say(f"Spatial tick {rep.get('tick')} · moved {rep.get('moved')} · "
             f"max_disp {rep.get('max_displacement', 0):.4f} · "
             f"state {rep.get('state')}")
        return p
    if lower.startswith("spatial settle"):
        parts = lower.split()
        n = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 200
        s = p.spatial_settle(n)
        _say(f"Settle · ticks {s['ticks_run']} · "
             f"converged {s['converged']} · "
             f"honestly_non_convergent {s['honestly_non_convergent']}")
        return p
    if lower.startswith("spatial explain "):
        iid = lower.split(maxsplit=2)[2].strip()
        e = p.spatial_explain(iid)
        if not e.get("present"):
            _say(f"No placement record for '{iid}'")
        else:
            pl = e["placement"]
            _say(f"{iid} @ ({e['x']:.2f}, {e['y']:.2f}) · "
                 f"cause {pl.get('cause')} · anchors {pl.get('anchors')}")
        return p
    if lower in ("spatial status", "spatial"):
        s = p.spatial
        _say(f"Spatial · tick {s.tick_count} · temp {s.temperature:.4f} · "
             f"tracked {len(s.velocities)} · placements {len(s.placements)}")
        return p

    if lower.startswith("force "):
        which = lower.split(maxsplit=1)[1].strip()
        if which in ("growth", "grow"):
            p.forces.activate("growth")
            for u in list(p.cube.session.plane.units.values())[:8]:
                known = {pl["idea"] for pl in p.forces.growth.plants}
                if u.label not in known:
                    p.forces.growth.plant(u.label, p.owner)
            p.forces.growth.grow_all(0.6)
            for line in p.forces.growth.map()[:8]:
                _say(line)
        elif which in ("water", "flow"):
            p.forces.activate("water")
            for u in list(p.cube.session.plane.units.values())[:3]:
                p.forces.water.flow(u.label, p.owner)
            if len(p.forces.water.streams) >= 2:
                m = p.forces.water.merge_last_two()
                if m:
                    _say(f"Merged → {m['idea'][:60]}")
            _say(f"Streams={len(p.forces.water.streams)} pools={len(p.forces.water.pools)}")
        elif which in ("breath", "heartbeat"):
            p.forces.activate("breath")
            r = p.forces.breath.heartbeat(len(p.cube.session.plane.units))
            _say(f"Breath cycle {r['inhale']['cycle']} · phase {p.forces.breath.phase}")
        elif which in ("gravity",):
            p.forces.activate("gravity")
            wells = p.forces.gravity.set_wells_from_scores(p.nodes_payload())
            _say("Wells: " + ", ".join(f"{w['label']}" for w in wells))
        else:
            _say("force growth|water|breath|gravity  or  force tick")
        return p

    if lower.startswith("weather "):
        cond = lower.split(maxsplit=1)[1].strip()
        c = p.set_weather(cond)
        _say(f"Weather → {c}")
        return p

    # DCC-I: DuoBeta living-growth boundary — inspectable from the REPL
    if lower in ("growth", "duobeta", "duo status", "show growth"):
        st = p.duo.status() if hasattr(p, "duo") else {}
        _say(f"DuoBeta · generation={st.get('generation')} ledger={st.get('ledger_len')}")
        _say(f"Rings: {' → '.join(st.get('rings') or [])}")
        _say(f"Mode: {st.get('mode')}")
        last = (p.duo.ledger or [None])[-1]
        if last is not None:
            _say(f"Last: gen {last.gen} · {last.detail}")
        else:
            _say("No growth recorded yet — try: evolve <your intent>")
        return p

    if lower == "ledger" or lower.startswith("ledger "):
        n = 10
        rest = lower[len("ledger"):].strip()
        if rest.isdigit():
            n = max(1, min(200, int(rest)))
        entries = list(getattr(p.duo, "ledger", []) or [])[-n:]
        if not entries:
            _say("Ledger is empty — try: evolve <your intent>")
            return p
        _say(f"Growth ledger · last {len(entries)} of {len(p.duo.ledger)}:")
        for e in entries:
            _say(f"  gen {e.gen} · {e.detail} [{e.ts}]")
        return p

    # ─── Needs: strong create · edit · undo · history · nbd · ready ───
    if lower.startswith("create an idea") or lower.startswith("create idea") or lower.startswith("plant "):
        from form.dell_matrix.needs import parse_and_place, format_create_end
        raw = raw_line
        if lower.startswith("plant "):
            name = raw_line.split(maxsplit=1)[1].strip()
            raw = f"create an idea called {name}"
        res = parse_and_place(p, raw)
        for line in format_create_end(res).splitlines():
            _say(line)
        # SAOC-I: observe specialized Create. Existing execution unchanged;
        # this only captures Outcome evidence with the public interaction_id.
        try:
            from form.mandell.execution_observer import observe_specialized_execution
            observe_specialized_execution(
                p,
                action="place",
                input_text=raw,
                ok=bool(res.get("ok", True)),
                error="" if res.get("ok", True) else str(res.get("error") or ""),
                messages=[f"Created idea: {res.get('label', '')} id={res.get('id', '')}"],
                semantic="place[Create:specialized]",
                interaction_id=interaction_id,
            )
        except Exception:
            pass
        return p

    if lower.startswith("set detail "):
        rest = raw_line[len("set detail "):].strip().split(None, 1)
        if len(rest) < 2:
            _say("usage: set detail <id|label> <text>")
            return p
        out = p.set_idea_detail(rest[0], rest[1])
        _say(f"Detail → {out.get('label')}: {(out.get('detail') or '')[:100]}" if out.get("ok") else out.get("reason"))
        return p

    if lower.startswith("set goals "):
        rest = raw_line[len("set goals "):].strip().split(None, 1)
        if len(rest) < 2:
            _say("usage: set goals <id|label> goal1; goal2")
            return p
        out = p.set_idea_goals(rest[0], rest[1])
        if out.get("ok"):
            _say(f"Goals → {out.get('label')}: {', '.join(out.get('goals') or [])}")
        else:
            _say(out.get("reason"))
        return p

    if lower.startswith("idea ") or lower.startswith("describe "):
        ref = raw_line.split(maxsplit=1)[1].strip()
        from form.dell_matrix.needs import idea_info, format_idea_end
        for line in format_idea_end(idea_info(p, ref)).splitlines():
            _say(line)
        return p

    if lower in ("undo", "undo last"):
        out = p.undo() if hasattr(p, "undo") else {"ok": False, "reason": "no undo"}
        _say(out.get("msg") or out.get("reason") or "undo")
        return p

    if lower in ("history", "hist", "notes") or lower.startswith("history "):
        # IRR-I: history find <text> — deterministic literal search (display only).
        # No execution, no mutation, no new persistence. User reissues via normal input.
        if lower == "history find" or lower.startswith("history find "):
            query = raw_line.strip()[12:].strip() if len(raw_line.strip()) > 12 else ""
            if not query:
                _say("usage: history find <text>")
                _say("  literal substring search over command history (display only)")
                return p
            hist = list(getattr(p, "history", []) or [])
            ql = query.lower()
            matches = [(i + 1, h) for i, h in enumerate(hist) if ql in h.lower()]
            if not matches:
                _say(f'No history matches for "{query}".')
                return p
            _say(f"History matches for \"{query}\" ({len(matches)}):")
            for num, h in matches:
                _say(f"  {num:2}. {h}")
            _say("  reissue by retyping the command (explicit action)")
            return p
        n = 16
        for part in lower.split():
            if part.isdigit():
                n = max(1, min(48, int(part)))
        for line in (p.history_lines(n) if hasattr(p, "history_lines") else []):
            _say(line)
        return p

    if lower in ("what next", "whats next", "what's next", "next", "nbd", "next best", "what should i do"):
        for line in (p.what_next() if hasattr(p, "what_next") else "try help").splitlines():
            _say(line)
        return p

    if lower in ("ready", "am i ready", "acceptance ready", "checklist"):
        for line in (p.ready_lines() if hasattr(p, "ready_lines") else []):
            _say(line)
        return p

    # Internet opt-in + Code Evolution root
    if lower in ("internet on", "net on", "allow internet"):
        out = p.internet_on() if hasattr(p, "internet_on") else {}
        _say(out.get("msg") or "Internet ON")
        return p
    if lower in ("internet off", "net off"):
        out = p.internet_off() if hasattr(p, "internet_off") else {}
        _say(out.get("msg") or "Internet OFF")
        return p
    if lower in ("internet", "internet status", "net status"):
        st = p.internet_status() if hasattr(p, "internet_status") else {}
        _say(f"Internet {'ON' if st.get('on') else 'OFF'}")
        _say(f"  hosts: {', '.join((st.get('hosts') or [])[:8])}")
        return p
    if lower.startswith("internet allow "):
        host = raw_line.split(maxsplit=2)[2] if len(raw_line.split()) >= 3 else ""
        if p.internet:
            _say(f"Allowed host → {p.internet.allow_host(host)}")
        return p
    if lower.startswith("net fetch ") or lower.startswith("fetch "):
        url = raw_line.split(maxsplit=1)[1].strip()
        out = p.net_fetch(url)
        if out.get("ok"):
            _say(f"Fetched {out.get('url')} ({out.get('bytes')} bytes)")
            _say((out.get("preview") or "")[:400])
        else:
            _say(out.get("error") or "fetch failed")
        return p
    if lower.startswith("ce research ") or lower.startswith("net research "):
        topic = raw_line.split(maxsplit=2)[-1].strip()
        out = p.net_research(topic)
        if out.get("ok"):
            _say(f"{out.get('title')}")
            _say((out.get("extract") or "")[:500])
            _say(out.get("honesty") or "")
        else:
            _say(out.get("error") or "research failed")
        return p
    if lower in ("ce", "ce status", "code evolution", "code evolution status"):
        for line in (p.ce_status() if hasattr(p, "ce_status") else "no ce").splitlines():
            _say(line)
        return p
    if lower in ("ce develop", "ce complete", "develop code evolution") or lower.startswith("ce develop "):
        parts = lower.split()
        n = 10
        use_net = "net" in parts or "internet" in parts
        for part in parts:
            if part.isdigit():
                n = max(1, min(20, int(part)))
        if use_net:
            p.internet_on()
            _say("Internet ON for CE develop")
        _say(f"Developing Code Evolution ×{n}…")
        out = p.ce_develop(cycles=n, internet=use_net)
        _say(f"complete={out.get('complete')} ideas={out.get('ideas')} gen={out.get('generation')}")
        for line in p.ce_status().splitlines():
            _say(line)
        return p

    if lower in ("self", "know self", "knowself", "self model", "understand myself", "who am i really"):
        for line in (p.reflect() if hasattr(p, "reflect") else ["no self model"]):
            _say(line)
        return p

    if lower in ("self map", "selfmap", "what am i", "inventory self"):
        inv = p.self_map() if hasattr(p, "self_map") else {}
        _say(f"Self map · gen={inv.get('generation')} ideas={inv.get('ideas')} matrices={inv.get('matrix_count')} snaps={inv.get('snap_count')}")
        _say(f"  form={inv.get('form')} · workshops={', '.join(inv.get('workshops') or [])}")
        mats = inv.get("matrices") or []
        _say(f"  matrices: {', '.join(mats[:16])}{'…' if len(mats) > 16 else ''}")
        return p

    if lower in ("close gaps", "close self gaps", "warm gaps"):
        out = p.close_self_gaps() if hasattr(p, "close_self_gaps") else {}
        _say(f"Closed: {', '.join(out.get('closed') or []) or '—'}")
        _say(f"Mastery: {(out.get('knowledge') or {}).get('avg_mastery')}")
        return p

    if lower in ("self evolve", "evolve understood", "evolve with understanding"):
        out = p.evolve_understood() if hasattr(p, "evolve_understood") else p.evolve("self")
        _say(f"Evolved w/ understanding · gen={out.get('generation')} mastery={out.get('mastery')}")
        _say(f"  pillars {out.get('pillars_before')} → {out.get('pillars_after')} · closed={out.get('closed')}")
        return p

    if lower.startswith("evolve loop") or lower in ("self evolve loop",):
        n = 12
        for part in lower.split():
            if part.isdigit():
                n = max(1, min(150, int(part)))
        out = p.evolve_loop(n) if hasattr(p, "evolve_loop") else {}
        _say(f"Evolve loop ×{out.get('cycles')} · gen={out.get('generation')} mastery={out.get('mastery')}")
        pil = out.get("pillars") or {}
        _say(f"  pillars {pil.get('label')} avg={pil.get('average')}")
        return p

    if lower in ("audit", "pillars", "six pillars", "6 pillars"):
        for line in p.audit_lines():
            _say(line)
        return p

    if lower in ("matrices", "matrix list", "list matrices"):
        _say(p.matrices_summary())
        for m in p.matrices():
            _say(f"  [{m['kind']}] {m['id']}: {m['desc'][:60]}")
        return p

    if lower in ("personas", "persona list", "agents", "roster"):
        for line in p.personas_roster():
            if line:
                _say(line)
        return p

    if lower in ("matrix personas", "persona matrix", "personas matrix"):
        for line in p.persona_matrix_ascii():
            _say(line)
        return p

    if lower in ("bimo", "bimo status", "show bimo"):
        for line in p.bimo.render_ascii():
            _say(line)
        st = p.bimo_status()
        _say(f"Filled {st['filled_count']}/{len(st['slots'])} · mode={st['mode']} · pilot={st['pilot']}")
        return p

    if lower in ("bimo defaults", "bimo dock all", "bimo reset"):
        out = p.bimo_defaults()
        _say(f"BIMO defaults docked · pilot={out.get('pilot')}")
        for line in p.bimo.render_ascii()[:14]:
            _say(line)
        return p

    if lower in ("bimo fuse", "fuse", "bimo fusion"):
        out = p.bimo_fuse()
        for line in out.get("guidance") or []:
            _say(line)
        return p

    if lower in ("bimo clear", "bimo empty"):
        p.bimo_clear()
        _say("BIMO slots cleared.")
        return p

    if lower.startswith("bimo dock "):
        rest = lower[len("bimo dock "):].strip().split()
        if len(rest) < 2:
            _say("Usage: bimo dock <slot> <persona>")
            _say("Slots: logic growth morph fusion ancient language quality voice execute watch body")
            return p
        out = p.bimo_dock(rest[0], rest[1])
        if out.get("ok"):
            pe = out.get("persona_meta") or {}
            _say(f"Docked {pe.get('emoji', '')} {pe.get('name', rest[1])} → slot [{rest[0]}]")
        else:
            _say(f"Fail: {out.get('reason')}")
        return p

    if lower.startswith("bimo undock "):
        slot = lower.split(maxsplit=2)[2].strip()
        out = p.bimo_undock(slot)
        _say(f"Undocked [{slot}] was {out.get('undocked')}")
        return p

    if lower.startswith("bimo pilot "):
        name = lower.split(maxsplit=2)[2].strip()
        out = p.bimo.set_pilot(name)
        if out.get("ok"):
            _say(f"BIMO pilot → {out['pilot']}")
            p.persona_lens = out["pilot"]
            p.persona_matrix.active = out["pilot"]
        else:
            _say(f"Fail: {out.get('reason')}")
        return p

    if lower in ("guide", "guide me", "persona guide"):
        for line in p.guide():
            _say(line)
        return p

    if lower.startswith("body "):
        style = lower.split(maxsplit=1)[1].strip()
        s = p.set_body_style(style)
        _say(f"Body style → {s}")
        print(p.body_art())
        return p

    # --- English brain expand / status / help ---
    if lower in ("english help", "how to talk", "english_help"):
        from form.mandell.english_brain import help_english
        for line in help_english():
            _say(line)
        return p

    if lower in ("english status", "english brain", "english_status"):
        from form.mandell.english_brain import mastery_status
        st = mastery_status()
        _say(f"English brain · cycles={st['cycle_count']} learned={st['learned']}")
        for k, v in (st.get("mastery") or {}).items():
            _say(f"  mastery {k}: {v:.2f}")
        for a, b in st.get("sample_learned") or []:
            _say(f"  learn: {a!r} → {b!r}")
        return p

    if lower.startswith("english expand") or lower in ("english_expand", "expand english", "english enhance"):
        from form.mandell.english_brain import expand_loop, enhance_150_loop
        n = 150 if "enhance" in lower or "150" in lower else 50
        parts = lower.split()
        for part in parts:
            if part.isdigit():
                n = max(1, min(300, int(part)))
        _say(f"Expanding English understanding · {n} cycles…")
        if n >= 150:
            rep = enhance_150_loop()
            _say("Phase A+B+C (warm · stress · mastery lock)")
        else:
            rep = expand_loop(n)
        if hasattr(p, "duo"):
            p.duo.evolve(f"45[Translate] :: english_expand x{n}")
        if hasattr(p, "note_seed"):
            p.note_seed(45, "Translate", f"en_x{n}")
        _say(f"Done · tests={rep.total_tests} hits={rep.hits} rate={rep.final_rate:.1%}")
        _say(f"Learned paraphrases this run: {len(rep.learned)} (total bank grows in-process)")
        # show bookend + mid cycle rates
        pcs = rep.per_cycle or []
        for c in ([pcs[0]] if pcs else []) + pcs[len(pcs)//2:len(pcs)//2+1] + pcs[-3:]:
            if c:
                _say(f"  cycle {c['cycle']}: rate={c['rate']} mastery_avg={c['mastery_avg']} bank={c.get('bank', '—')}")
        top = sorted((rep.mastery or {}).items(), key=lambda kv: -kv[1])[:8]
        if top:
            _say("Mastery: " + " · ".join(f"{k}={v:.2f}" for k, v in top))
        _say("Try natural speech: what do i see · open the idea page · score slopes please")
        return p

    if lower.startswith("zoom "):
        ref = raw_line.split(maxsplit=1)[1].strip()
        out = p.zoom_to(ref)
        if out.get("ok"):
            card = out.get("page") or p.page_card()
            for line in (p.format_page_end(card) if hasattr(p, "format_page_end") else "").splitlines():
                _say(line)
        else:
            units = list(p.cube.session.plane.units.keys())[:8]
            hint = f" · live: {', '.join(units)}" if units else " · create an idea first"
            _say(f"Could not zoom: {out.get('reason')}{hint}")
        return p

    if lower in ("page", "page status", "show page", "open page", "idea page", "end page"):
        out = p.open_page() if hasattr(p, "open_page") else {"ok": False, "reason": "no open_page"}
        if not out.get("ok"):
            _say(out.get("reason") or "No ideas yet — create an idea called <name>")
        else:
            card = out.get("page") or p.page_card()
            if out.get("auto"):
                _say(f"Auto-opened nearest idea · {out.get('id')}")
            for line in (p.format_page_end(card) if hasattr(p, "format_page_end") else "").splitlines():
                _say(line)
        return p

    if lower.startswith("page "):
        ref = raw_line.split(maxsplit=1)[1].strip()
        out = p.open_page(ref) if hasattr(p, "open_page") else p.zoom_to(ref)
        if out.get("ok"):
            card = out.get("page") or p.page_card()
            for line in (p.format_page_end(card) if hasattr(p, "format_page_end") else "").splitlines():
                _say(line)
        else:
            _say(out.get("reason") or "Could not open page")
        return p

    if lower in ("unzoom", "zoom out", "leave page"):
        p.unzoom()
        _say("Unzoomed · overview · doors: page | look | proposals | home")
        return p

    # Incomplete bare commands — usage end, never mis-create
    _bare_usage = {
        "confirm": "usage: confirm <id> | confirm all",
        "reject": "usage: reject <id> | reject all",
        "create an idea called": "usage: create an idea called <name>",
        "create an idea": "usage: create an idea called <name>",
        "create": "usage: create an idea called <name>",
        "zoom": "usage: zoom <id|label>  ·  or: page",
        "lineage": "usage: lineage <id>",
        "shell": "usage: shell <n>",
        "chord": "usage: chord <h> <v>",
        "distill": "usage: distill <words>",
        "explain": "usage: explain <word>",
        "script": "usage: script look; pulse; status",
        "supersede": "usage: supersede idea <old-id> with <words>",
        "trace_dependency": "usage: trace dependency <id>",
    }
    if lower in _bare_usage:
        _say(_bare_usage[lower])
        return p

    if lower.startswith("mode "):
        m = p.set_ux_mode(lower.split(maxsplit=1)[1])
        _say(f"UX mode → {m}")
        return p

    if lower in ("snap on", "grid snap on"):
        p.grid_snap = True
        _say("Grid snap ON (active when form is cube/square).")
        return p
    if lower in ("snap off", "grid snap off"):
        p.grid_snap = False
        _say("Grid snap OFF.")
        return p

    if lower.startswith("lens "):
        f = p.set_skin_filter(lower.split(maxsplit=1)[1])
        _say(f"Skin filter → {f or 'clear'}")
        return p

    if lower.startswith("persona "):
        name = lower.split(maxsplit=1)[1].strip()
        if name in ("list", "all", "roster"):
            for line in p.personas_roster():
                if line:
                    _say(line)
            return p
        pe = p.set_persona_lens(name)
        if pe:
            meta = None
            try:
                from form.dell_matrix.personas import get_persona
                meta = get_persona(pe)
            except Exception:
                pass
            if meta:
                _say(f"Persona → {meta.get('emoji')} {meta.get('name')} · {meta.get('category')} · {meta.get('role')}")
                _say(f"  {meta.get('focus')}")
            else:
                _say(f"Persona lens → {pe}")
        else:
            _say("Persona lens → clear")
        return p

    if lower in ("workshops", "workshop list"):
        st = p.workshops_status()
        for w in st["list"]:
            mark = " *" if st["active"] and st["active"]["id"] == w["id"] else ""
            _say(f"{w['id']}: {w['name']}{mark} — {w.get('description','')}")
        return p

    if lower.startswith("workshop "):
        rest = lower.split(maxsplit=1)[1].strip()
        if rest in ("leave", "exit", "close"):
            left = p.leave_workshop().get("left")
            _say(f"Left workshop {left or '—'}.")
            return p
        out = p.enter_workshop(rest)
        if not out.get("ok"):
            _say(out.get("reason", "unknown workshop"))
            return p
        w = out["workshop"]
        _say(f"Entered {w['name']}: {w.get('description','')}")
        for c in w.get("commands") or []:
            _say(f"  {c['label']}: {c['cmd']}")
        return p

    if lower in ("recenter", "center"):
        p.camera_follow = True
        _say("Camera follow ON (live panel recenters on YOU).")
        return p

    if lower in ("click inspect", "inspect mode"):
        p.click_mode = "inspect"
        _say("Click mode → inspect (zoom on node).")
        return p
    if lower in ("click confirm", "confirm mode"):
        p.click_mode = "confirm"
        _say("Click mode → confirm.")
        return p

    # AI companion commands
    if lower.startswith("ai "):
        rest = lower[3:].strip()
        c = p.companion
        if rest in ("walk", "step", "forward"):
            pos = c.step(1)
            _say(f"AI walked to {pos}.")
        elif rest in ("turn left", "left"):
            _say(f"AI turned left → {c.turn(-1)}")
        elif rest in ("turn right", "right"):
            _say(f"AI turned right → {c.turn(1)}")
        elif rest in ("look", "see"):
            c.doing = "looking"
            c.last_action = "looked"
            _say("AI looked.")
        elif rest in ("follow", "wander", "manual"):
            _say(f"AI mode → {c.set_mode(rest)}")
        elif rest in ("status", "where"):
            _say(f"AI at {c.pos} face {c.facing} mode={c.mode} · {c.doing}")
        elif rest.startswith("goto "):
            parts = rest.split()
            try:
                _say(f"AI moved to {c.goto(float(parts[1]), float(parts[2]))}")
            except Exception:
                _say("usage: ai goto X Y")
        else:
            _say(f"Unknown ai command: {rest}")
        return p

    lm = _handle_latinmandell(p, lower, raw_line)
    if lm is True:
        return p
    if isinstance(lm, tuple) and lm and lm[0] == "__exec__":
        eng = lm[1]
        return _execute_intent(p, translate(eng), raw_line=eng)

    if _handle_lattice(p, lower, raw_line):
        return p
    if _handle_macro_rank(p, lower, raw_line):
        return p

    if lower in ("proposals", "nursery", "void", "pending"):
        _show_proposals(p)
        return p

    if lower in ("lang list", "langs", "languages"):
        _say("Supported: " + ", ".join(list_langs()) + " · en (primary)")
        _say("LatinMandell: explain · deepen · morph · customize · la …")
        _echo_seed(mandel="35[Discover] :: lang_list")
        return p

    if lower.startswith("lineage "):
        pid = raw_line.split(maxsplit=1)[1].strip()
        prop = p.nursery.proposals.get(pid)
        if prop:
            _say(f"Proposal {prop.id} [{prop.kind}] {prop.label}")
            _say(f"  parents: {prop.parents or '—'}")
            _say(f"  affinity: {prop.affinity:.3f}")
            _say(f"  status: {prop.status}")
            return p
        unit = p.cube.session.plane.units.get(pid)
        if unit:
            _say(f"Live idea {pid}: {unit.label}")
            kids = [pr for pr in p.nursery.proposals.values() if pid in (pr.parents or [])]
            _say(f"  nursery children: {len(kids)}")
            return p
        _say(f"No proposal or idea for id: {pid}")
        return p

    if lower in (
        "auto confirm on", "auto confirm all", "auto confirm all grow mode",
        "grow mode auto", "grow mode auto confirm", "auto_confirm on",
        "auto-confirm on",
    ):
        if hasattr(p, "set_auto_confirm_grow"):
            p.set_auto_confirm_grow(True)
        else:
            p.auto_confirm_grow = True
        _say("Grow mode → auto confirm all ON · every grow accepts all nursery proposals")
        return p

    if lower in (
        "auto confirm off", "grow mode manual", "grow mode off",
        "auto_confirm off", "auto-confirm off",
    ):
        if hasattr(p, "set_auto_confirm_grow"):
            p.set_auto_confirm_grow(False)
        else:
            p.auto_confirm_grow = False
        _say("Grow mode → auto confirm all OFF · grow leaves proposals in nursery")
        return p

    if lower in ("grow mode", "auto confirm", "auto_confirm", "auto-confirm"):
        on = bool(getattr(p, "auto_confirm_grow", False))
        _say(f"Grow mode · auto_confirm_grow={'ON' if on else 'OFF'}")
        _say("  auto confirm on  — grow then confirm all")
        _say("  auto confirm off — grow leaves nursery pending")
        return p

    if lower in ("confirm all", "confirm-all"):
        pending = p.list_proposals()
        if not pending:
            _say("Nursery is empty.")
            return p
        n = 0
        for prop in list(pending):
            # WO-5.1: User typed "confirm all" — explicit review context.
            res = p.confirm_proposal(
                prop["id"],
                _producer="repl_user",
                _review_context=p.make_review_context(prop["id"], "repl_user"),
            )
            if res.get("ok"):
                n += 1
                _say(f'Confirmed: "{res["label"]}"')
        _say(f"Confirmed {n} proposal(s).")
        return p

    if lower in ("reject all", "reject-all"):
        pending = p.list_proposals()
        n = 0
        for prop in list(pending):
            if p.reject_proposal(prop["id"]).get("ok"):
                n += 1
        _say(f"Rejected {n} proposal(s).")
        return p

    if lower.startswith("confirm "):
        pid = raw_line.split(maxsplit=1)[1].strip()
        # WO-5.1: User typed "confirm <id>" — explicit review context.
        res = p.confirm_proposal(
            pid,
            _producer="repl_user",
            _review_context=p.make_review_context(pid, "repl_user"),
        )
        _say(f'Confirmed. "{res["label"]}" is live.' if res.get("ok") else f"Could not confirm: {res.get('reason')}")
        return p

    if lower.startswith("reject "):
        pid = raw_line.split(maxsplit=1)[1].strip()
        res = p.reject_proposal(pid)
        _say("Rejected." if res.get("ok") else f"Could not reject: {res.get('reason')}")
        return p

    if lower in ("acceptance", "accept", "cold start", "coldstart"):
        _say("Acceptance: create → grow → confirm → sphere → save → load → visual")
        _say("Or type: tutorial")
        return p

    if lower.startswith("teach "):
        print()
        print(teach(raw_line.split(maxsplit=1)[1].strip()))
        print()
        return p

    if lower in ("patterns", "pattern list"):
        for pat in list_patterns():
            _say(f"{pat['name']}: {pat['mandel']} — {pat['english']}")
        return p

    if lower in ("phrases", "phrase list"):
        for ph in list_phrases()[:30]:
            _say(f"{ph['hint']}: {ph['mandel']}")
        return p

    if lower.startswith("mandell ") or lower.startswith("to mandell "):
        _say(to_mandell(raw_line.split(maxsplit=1)[1]))
        return p

    if lower.startswith("english ") or lower.startswith("to english "):
        _say(to_english(raw_line.split(maxsplit=1)[1]))
        return p

    if lower.startswith("bridge "):
        rep = bridge(raw_line.split(maxsplit=1)[1])
        _say(f"mandel:  {rep.get('mandel')}")
        _say(f"english: {rep.get('english')}")
        return p

    if lower.startswith("es ") or lower.startswith("spanish "):
        text = raw_line.split(maxsplit=1)[1]
        rep = bridge_lang("es", text)
        _say(f"english: {rep.get('english')}")
        _say(f"mandel:  {rep.get('mandel')}")
        if rep.get("ok") == "true" and rep.get("english"):
            return _execute_intent(p, translate(rep["english"]), raw_line=rep["english"])
        return p

    if lower.startswith("fr ") or lower.startswith("french "):
        text = raw_line.split(maxsplit=1)[1]
        rep = bridge_lang("fr", text)
        _say(f"english: {rep.get('english')}")
        _say(f"mandel:  {rep.get('mandel')}")
        if rep.get("ok") == "true" and rep.get("english"):
            return _execute_intent(p, translate(rep["english"]), raw_line=rep["english"])
        return p

    if action == "place":
        # Prefer strong-create parse when raw line has create/detail/goals
        raw = raw_line or intent.english or ""
        if re.search(r"\b(create|plant)\b", raw, re.I) or "detail:" in raw.lower() or "goals:" in raw.lower():
            from form.dell_matrix.needs import parse_and_place, format_create_end
            res = parse_and_place(p, raw if re.search(r"\bcreate\b", raw, re.I) else f"create an idea called {raw}")
            for line in format_create_end(res).splitlines():
                _say(line)
            _echo_seed(raw_line, intent.mandel or "")
            # SAOC-I: observe specialized Create (rich path). Existing execution
            # unchanged; this only captures Outcome evidence.
            try:
                from form.mandell.execution_observer import observe_specialized_execution
                observe_specialized_execution(
                    p,
                    action="place",
                    input_text=raw,
                    ok=bool(res.get("ok", True)),
                    error="" if res.get("ok", True) else str(res.get("error") or ""),
                    messages=[f"Created idea: {res.get('label', '')} id={res.get('id', '')}"],
                    semantic="place[Create:specialized]",
                    interaction_id=interaction_id,
                )
            except Exception:
                pass
        else:
            uid = args.get("id", "idea")
            label = args.get("label", uid)
            p.place(uid, label, words=args.get("words", ""), skin=Skin.CUBE)
            from form.dell_matrix.needs import push_action
            push_action(p, {"kind": "place", "id": uid, "label": label})
            _say(f'Created idea: "{label}"')
            _say("  tip: add detail/goals → set detail <id> … · set goals <id> a; b")
            _echo_seed(raw_line, intent.mandel or "")
            # SAOC-I: observe specialized Create (simple path).
            try:
                from form.mandell.execution_observer import observe_specialized_execution
                observe_specialized_execution(
                    p,
                    action="place",
                    input_text=raw,
                    ok=True,
                    messages=[f'Created idea: "{label}"'],
                    semantic="place[Create:specialized]",
                    interaction_id=interaction_id,
                )
            except Exception:
                pass

    elif action == "grow":
        # DCC-II: route through the Mandell->Dell semantic boundary.
        # The Intent's Mandell composition selects the Dell; execution goes
        # through the existing Dell authority (execute_seed), not a duplicate.
        from form.mandell.semantic_router import route_intent
        receipt = route_intent(p, intent, raw_line, interaction_id=interaction_id)
        _print_route_receipt(receipt)
        return p

    # MPC-008: session-restore family -> persist_load. Without this branch the
    # DCC-III vocabulary branch below routes action=="load" to Dell28, so
    # ordinary English "resume" silently discards uncommitted work through
    # checkpoint rollback (Director ruling: session/persistence semantics).
    # Checkpoint language ("revert", bare/checkpoint-qualified "restore")
    # keeps Dell28 via _checkpoint_lang above.
    # R6.3: checkpoint-restore language ("revert", bare/checkpoint-qualified
    # "restore") is authority-mediated. Typing "restore" alone is NEVER
    # approval: the first step freezes the target and shows what would be
    # restored. The second step ("restore confirm <generation>") issues an
    # explicit human approval bound to the frozen target and executes
    # through Program.confirm_rollback (the single enforcement point).
    elif action == "load" and not _checkpoint_lang:
        # ARGUS vector 9: claiming "Session loaded." when no save file exists
        # would silently replace the live program with a fresh one. Check
        # first; if nothing was ever saved, say so honestly and preserve the
        # current program.
        from form.persist import _path as _persist_path
        import os as _os
        if _os.path.isfile(_persist_path(p.owner)):
            p2 = persist_load(p.owner)
            _say("Session loaded.")
            print()
            print(p2.render())
            return p2
        _say("No saved session found — nothing to resume.")
        _say('  Tip: "save" stores the current session first.')
        return p

    # DCC-III: expanded semantic vocabulary — all route through Dell authority.
    elif action in ("measure", "test", "architect", "simulate", "checkpoint",
                    "stamp", "cycle", "form", "load", "retry"):
        from form.mandell.semantic_router import route_intent
        receipt = route_intent(p, intent, raw_line, interaction_id=interaction_id)
        _print_route_receipt(receipt)
        # Dell 28 (rollback) returns a restored program; swap it in.
        if receipt.new_program is not None:
            return receipt.new_program
        return p

    elif action == "show":
        print()
        print(p.render())

    elif action == "visual":
        paths = p.visual()
        _say("Visual ready — open this file in a browser (offline):")
        _say(paths.get("easy") or paths.get("html", ""))

    elif action == "walk":
        steps = int(args.get("steps", 1))
        p.avatar.set_locomotion(Locomotion.WALK)
        pos = p.avatar.step(steps)
        if hasattr(p, "apply_grid_snap"):
            p.apply_grid_snap()
            pos = p.avatar.body.pos
        if hasattr(p, "_push_user_trail"):
            p._push_user_trail()
        if hasattr(p, "note_seed"):
            p.note_seed(19, "Drive", "walk")
        _say(f"You walked forward {steps}. Now at {pos}.")

    elif action == "run":
        p.avatar.set_locomotion(Locomotion.RUN)
        pos = p.avatar.step(2)
        if hasattr(p, "apply_grid_snap"):
            p.apply_grid_snap()
            pos = p.avatar.body.pos
        if hasattr(p, "_push_user_trail"):
            p._push_user_trail()
        if hasattr(p, "note_seed"):
            p.note_seed(19, "Drive", "run")
        _say(f"You ran to {pos}.")

    elif action == "jog":
        p.avatar.set_locomotion(Locomotion.JOG)
        pos = p.avatar.step(1)
        if hasattr(p, "apply_grid_snap"):
            p.apply_grid_snap()
            pos = p.avatar.body.pos
        if hasattr(p, "_push_user_trail"):
            p._push_user_trail()
        if hasattr(p, "note_seed"):
            p.note_seed(19, "Drive", "jog")
        _say(f"You jogged to {pos}.")

    elif action == "backstep":
        pos = p.avatar.backstep(int(args.get("steps", 1)))
        if hasattr(p, "apply_grid_snap"):
            p.apply_grid_snap()
            pos = p.avatar.body.pos
        if hasattr(p, "_push_user_trail"):
            p._push_user_trail()
        if hasattr(p, "note_seed"):
            p.note_seed(19, "Drive", "backstep")
        _say(f"You backstepped to {pos}.")

    elif action == "strafe":
        direction = str(args.get("direction", "right")).lower()
        side = -1 if direction in ("left", "l", "west") else 1
        pos = p.avatar.strafe(side, int(args.get("steps", 1)))
        if hasattr(p, "apply_grid_snap"):
            p.apply_grid_snap()
            pos = p.avatar.body.pos
        if hasattr(p, "_push_user_trail"):
            p._push_user_trail()
        if hasattr(p, "note_seed"):
            p.note_seed(19, "Drive", f"strafe_{direction}")
        _say(f"You strafed {direction} to {pos}.")

    elif action == "stop":
        p.avatar.set_locomotion(Locomotion.IDLE)
        if hasattr(p, "note_seed"):
            p.note_seed(32, "Pause", "stop")
        _say("You stopped.")

    elif action == "turn":
        direction = args.get("direction", "right")
        facing = p.avatar.turn_left() if direction == "left" else p.avatar.turn_right()
        if hasattr(p, "note_seed"):
            p.note_seed(4, "Transform", f"turn_{direction}")
        _say(f"You turned {direction}. Facing {facing}.")

    elif action == "face":
        d = str(args.get("direction", "n")).lower()
        facing = _FACING.get(d, Facing.N)
        p.avatar.face(facing)
        _say(f"Facing {facing.name}.")

    elif action == "sit":
        p.avatar.set_posture(Posture.SIT)
        if hasattr(p, "note_seed"):
            p.note_seed(4, "Transform", "sit")
        _say("You sat down.")

    elif action == "stand":
        p.avatar.set_posture(Posture.STAND)
        if hasattr(p, "note_seed"):
            p.note_seed(4, "Transform", "stand")
        _say("You stood up.")

    elif action == "jump":
        p.avatar.set_posture(Posture.JUMP)
        p.avatar.set_posture(Posture.STAND)
        _say("You jumped.")

    elif action == "bend":
        p.avatar.set_posture(Posture.BEND)
        _say("You bent over.")

    elif action == "express":
        name = args.get("expression", "neutral")
        face = p.face.set(_EXPR.get(name, Expression.NEUTRAL))
        if hasattr(p, "note_seed"):
            p.note_seed(5, "Tone", name)
        _say(f"{face}  You look {name}.")

    elif action == "avatar_status":
        st = p.avatar_status()
        _say(f"{st['look']}  {st['describe']}")

    elif action == "enhance_on":
        p.enhance_on()
        if hasattr(p, "note_seed"):
            p.note_seed(25, "Pulse", "enhance_on")
        _say("Enhance ON.")

    elif action == "enhance_off":
        p.enhance_off()
        if hasattr(p, "note_seed"):
            p.note_seed(32, "Pause", "enhance_off")
        _say("Enhance OFF.")

    elif action == "pulse":
        p.pulse()
        if hasattr(p, "note_seed"):
            p.note_seed(25, "Pulse")
        _say("Pulse sent.")

    elif action == "sandbox_on":
        p.sandbox_on()
        _say("Sandbox ON.")

    elif action == "sandbox_off":
        p.sandbox_off()
        _say("Sandbox OFF.")

    elif action == "save":
        # DCC-II: route through the Mandell->Dell semantic boundary (Dell 10).
        from form.mandell.semantic_router import route_intent
        receipt = route_intent(p, intent, raw_line, interaction_id=interaction_id)
        _print_route_receipt(receipt)
        return p

    elif action == "discover":
        # DCC-II: read-only inspection routed through Dell 35.
        from form.mandell.semantic_router import route_intent
        receipt = route_intent(p, intent, raw_line, interaction_id=interaction_id)
        _print_route_receipt(receipt)
        return p

    elif action == "nurture":
        # CND-I: the English intent layer produces "nurture" intents
        # (use idea / supersede idea / resolve conflict / grow using knowledge).
        # Route through the canonical semantic router, like save/discover.
        # Previously these died as 'Not understood action "nurture"'.
        from form.mandell.semantic_router import route_intent
        receipt = route_intent(p, intent, raw_line, interaction_id=interaction_id)
        _print_route_receipt(receipt)
        return p

    elif action == "load":
        p2 = persist_load(p.owner)
        _say("Session loaded.")
        print()
        print(p2.render())
        return p2

    elif action == "status":
        st = p.avatar_status()
        ns = p.nursery.summary()
        lat = p.lattice.status()
        _say(f"{st['look']}  {st['describe']}")
        _say(f"ideas={len(p.cube.session.plane.units)} nursery={ns['pending']}")
        _say(f"lattice form={lat['form']} cells={lat['cells']} history={len(p.history)}")

    elif action == "help":
        print()
        print(HELP_SHORT)
        print()
        _say("Type: help more")

    elif getattr(intent, "dell", None) is not None and 51 <= int(getattr(intent, "dell", 0) or 0) <= 99:
        # SSI-I: explicit canonical Core-II reference (translate() recognized
        # `dell NN` / `NN[Name]`) → canonical router. Identity and policy
        # (blocked/raw-only) via the bridge fallback inside route_intent;
        # Outcome V1 captured by the wrapper. No new router.
        from form.mandell.semantic_router import route_intent
        receipt = route_intent(p, intent, raw_line, interaction_id=interaction_id)
        _print_route_receipt(receipt)
        return p

    elif action == "unknown":
        q = (args.get("query") or intent.english or raw_line or "").strip()
        _say(f'Not understood: "{q[:60]}"')
        _say("Try: create an idea called <name> · grow ideas 2 · look · page · self · help")
        _say("Natural: what do i see · open the idea page · save my work · health check")
        _echo_seed(mandel="09[Show] :: unknown")

    else:
        # Unknown action — do not invent ideas (function + usability guard)
        _say(f'Not understood action "{action}" for: {(raw_line or intent.english or "")[:50]}')
        _say("Try: help · create an idea called <name> · look · self · status")

    return p


def _dispatch_public_line(p: Program, line: str, interaction_id: str) -> Program:
    """IRI-I: Canonical public execution boundary for one input line.

    This is the SAME dispatch sequence run() uses for newly typed input:
    ROS → learn → why → flow → seed → composite → translate/_execute_intent.
    Reissue feeds recovered historical source through here with a FRESH
    interaction_id. All current parsing, routing, eligibility, guards, and
    special authorities apply. No historical authority is reused.
    """
    # ROS-I: read-only observability meta-commands.
    if _handle_ros_command(p, line):
        return p

    # DLA-I: DuoBeta learning activation.
    if _handle_learn_command(p, line):
        return p

    # KIE-I: Knowledge Influence explanation. Read-only.
    if _handle_why_command(p, line):
        return p

    # TPP-I: Temporal Presence Projection (NBD-Ω-048).
    # User-controlled pin/fade/unfade/age for ideas. Does not modify Dells.
    from form.lifecycle import handle_lifecycle_command
    handled, p, msg = handle_lifecycle_command(p, line, interaction_id)
    if handled:
        _say(msg)
        return p

    # GREEK: Mandell floor operators made public (canon).
    # Alpha (source), Delta (change), Omega (bound), Omni (full-field),
    # Lambda (logic), Sigma (sum). Read-only observation. Does not modify Dells.
    from form.greek import handle_greek_command
    handled, p, msg = handle_greek_command(p, line, interaction_id)
    if handled:
        _say(msg)
        return p

    # DCC-IV: composed Mandell program (flow operators) -> flow executor.
    if ">" in line or ":" in line:
        try:
            from form.mandell.flow_executor import (
                parse_program, execute_program, format_receipt,
            )
            fp = parse_program(line)
            if len(fp.nodes) > 1:
                receipt = execute_program(p, fp, interaction_id=interaction_id)
                print()
                print(format_receipt(receipt))
                print()
                if receipt.final_program is not None:
                    return receipt.final_program
                return p
        except ValueError:
            pass  # Not a valid flow program; fall through.

    if looks_like_seed(line):
        # EOC-I: raw execution with Outcome V1 observation.
        from form.mandell.execution_observer import observe_seed_execution
        result = observe_seed_execution(p, line, interaction_id=interaction_id)
        return _apply_seed_result(p, result)

    # DCC-V: natural English multi-step instruction -> Mandell program.
    import re as _re
    if _re.search(r"\b(?:and then|after that|then)\b", line, _re.IGNORECASE):
        try:
            from form.mandell.english_composer import (
                compose_english, execute_composite, format_composite_receipt,
            )
            cr = compose_english(line)
            if cr.ok:
                receipt = execute_composite(p, cr.composite, interaction_id=interaction_id)
                print()
                print(format_composite_receipt(cr.composite, receipt))
                print()
                if receipt.final_program is not None:
                    return receipt.final_program
                return p
            # Compile failure: report honestly, execute zero Dells.
            print()
            print(f"COMPILE FAILURE: {cr.error}")
            print("Zero Dells executed.")
            print()
            return p
        except Exception as e:
            print(f"Composition error: {e}")
            return p

    intent = translate(line)
    return _execute_intent(p, intent, raw_line=line, interaction_id=interaction_id)


def _handle_reissue(p: Program, line: str, pending: Optional[str]) -> tuple:
    """IRI-I: Staged reissue — inspect/show, then explicit confirm.

    Returns (program, new_pending). The pending source is session-only;
    it is never persisted and never leaves this REPL session.

    - `reissue <ref>`: resolve Outcome via COO-I selectors, verify exact
      source, SHOW it with a current-state warning. Stages the source.
      Never executes (R2).
    - `reissue confirm`: execute the staged source through the canonical
      public boundary with a FRESH interaction_id. Clears the stage.
    - `reissue cancel`: discard the staged source.
    """
    from form.mandell.runtime_observe import resolve_outcome_ref

    low = line.strip().lower()
    rest = line.strip()[7:].strip()  # after "reissue"

    # --- confirm: execute staged source ---
    if low == "reissue confirm":
        if not pending:
            _say("Nothing staged. Use: reissue <outcome-ref> first.")
            return p, None
        import uuid as _uuid
        new_id = str(_uuid.uuid4())
        source = pending
        _say(f"Reissuing now with new interaction {new_id[:8]}...")
        try:
            p = _dispatch_public_line(p, source, new_id)
        except Exception as e:
            _say(f"Reissue execution error: {e}")
        return p, None

    # --- cancel: discard staged ---
    if low == "reissue cancel":
        if pending:
            _say("Staged reissue discarded.")
        else:
            _say("Nothing staged.")
        return p, None

    # --- bare: usage ---
    if not rest or low == "reissue":
        _say("usage: reissue <outcome-ref>  — show exact historical source")
        _say("       reissue confirm        — execute the staged source now")
        _say("       reissue cancel         — discard the staged source")
        _say("Find refs via: outcomes · outcome <seq>")
        return p, pending

    # --- inspect/show: resolve, verify, stage (never execute) ---
    res = resolve_outcome_ref(p, rest)
    if not res.get("ok"):
        _say(f"reissue: {res.get('detail', res.get('status', 'unknown'))}")
        return p, pending

    rec = res["outcome"]
    source = rec.get("input", "") or ""
    # R3/R4: source must be exact public input. Empty/missing → refuse.
    if not source.strip():
        _say(f"reissue: outcome [{rec.get('outcome_seq', '?')}] has no exact")
        _say("public source recorded — not reissuable.")
        return p, pending

    seq = rec.get("outcome_seq", "?")
    oid = rec.get("outcome_id", "") or ""
    _say(f"Reissue candidate from outcome [{seq}] ({oid[:18]}...):")
    _say(f"  source: {source}")
    _say("  Runs now against current state; result may differ.")
    _say("  Type 'reissue confirm' to execute, 'reissue cancel' to discard.")
    return p, source


def _studio_screen_input(p, text: str) -> bool:
    """R7.2: fail-closed protection screen for raw studio input text.

    Screens the raw text and its decoded form. Returns True if clean.
    Returns False (reject) if protected material is found OR if screening
    cannot be performed. Never raises. The structured specs are screened
    again by PerspectiveStudio.compose via the shared helper.
    """
    try:
        from form.dell_matrix.inference_dock import (
            protected_values, contains_protected_decoded)
        protected = protected_values(p)
        if contains_protected_decoded(text, protected):
            return False
        return True
    except Exception:
        # Fail closed: if we cannot screen, we reject.
        return False


def _handle_studio_line(p, line: str, studio):
    """R7.2: handle one input line while Perspective Studio is active.

    Only studio commands are accepted: compose, legend, help, leave.
    Everything else is rejected explicitly before normal dispatch.
    No mutations route from this circuit.

    Protection is fail-closed: input is screened before reflection or
    recording; screening failure rejects. All failure messages are fixed
    bounded codes; raw input text is never reflected.

    Returns (program, studio_or_None). On leave, the closed record is
    staged, then persisted via the canonical save. The studio is discarded
    only after successful save. On save failure, prior in-memory records
    are restored and the studio remains active for retry.
    """
    from form.dell_matrix.perspective_studio import (
        parse_specs_json, STUDIO_COMMANDS, FAIL_PROTECTED, FAIL_OUT_OF_SCOPE,
        FAIL_SAVE)

    stripped = line.strip()
    lower = stripped.lower()

    # leave: stage closed record, save, discard studio only on success.
    if lower == "leave":
        # Stage: build the closed record without mutating the studio.
        closed_record = studio.prepare_leave()
        sid = closed_record["session_id"]
        # Save prior in-memory records for restoration on failure.
        prior = dict(getattr(p, "studio_sessions", None) or {})
        prior_malformed = getattr(p, "studio_sessions_malformed", None)
        # Merge: new record plus retention (10 most recent).
        merged = dict(prior)
        merged[sid] = closed_record
        if len(merged) > 10:
            ordered = sorted(merged.items(),
                             key=lambda kv: str(kv[1].get("started", "")),
                             reverse=True)[:10]
            merged = dict(ordered)
        p.studio_sessions = merged
        # Canonical save with existing recovery/stale-writer guards.
        # Report saved/exited only after success.
        try:
            from form import persist_rest
            persist_rest.save(p)
            _say(f"Studio session saved ({sid[:8]}...). Exited.")
            return p, None
        except Exception as exc:
            # Save failure: restore prior records, keep studio active.
            # The studio was not marked closed; retry is coherent.
            p.studio_sessions = prior
            p.studio_sessions_malformed = prior_malformed
            _say(f"{FAIL_SAVE}: {type(exc).__name__}. "
                 f"Session retained ({sid[:8]}...); "
                 f"still in studio — 'leave' to retry.")
            return p, studio

    if lower == "legend":
        legend = studio.legend()
        _say("Layout legend (descriptive only):")
        for k in sorted(legend.keys()):
            _say(f"  {k}: {legend[k]}")
        return p, studio

    if lower == "help":
        _say(studio.help_text())
        return p, studio

    if lower.startswith("compose"):
        rest = stripped[7:].strip()
        if not rest:
            studio._record("compose", "rejected: missing specs")
            _say("compose: missing JSON specs.")
            return p, studio
        # Screen raw input BEFORE parsing, reflecting, or recording.
        # Fail-closed: screening failure rejects. Structured specs are
        # screened again by PerspectiveStudio.compose (shared contract).
        if not _studio_screen_input(p, rest):
            studio._record("compose", FAIL_PROTECTED)
            _say(f"compose rejected: {FAIL_PROTECTED}.")
            return p, studio
        ok, err, specs = parse_specs_json(rest)
        if not ok:
            studio._record("compose", f"rejected: {err}")
            _say(f"compose rejected: {err}.")
            return p, studio
        result = studio.compose(specs)
        if not result.get("ok"):
            _say(f"compose rejected: {result.get('status')}.")
            return p, studio
        # Display attributed observations, retaining status and provenance.
        # Uses the compositor's report lines; does not invent counts.
        _say(f"Composed {len(result.get('components', []))} view(s) "
             f"[{result.get('epistemic_status')}]:")
        for c in result.get("components", []):
            vid = c.get("viewer", "?")
            mode = c.get("requested_mode", "?")
            status = c.get("epistemic_status", "?")
            source = c.get("source", "?")
            _say(f"[{vid}/{mode}] status={status} source={source}")
            view = c.get("view", {})
            report = view.get("report", []) if isinstance(view, dict) else []
            if isinstance(report, list):
                for rline in report[:12]:
                    _say(f"  {rline}")
            elif isinstance(report, str):
                _say(f"  {report[:200]}")
        return p, studio

    # Out-of-scope: explicit rejection before normal dispatch.
    # Mutations (confirm, grant, reissue, etc.) never route from the studio.
    # Fixed message: never reflect raw input text.
    studio._record("rejected", FAIL_OUT_OF_SCOPE)
    _say(f"Studio: command out of scope. "
         f"Studio commands: {', '.join(STUDIO_COMMANDS)}.")
    return p, studio


def _handle_workshop_line(p, line: str, wsession):
    """R7.3: handle one input line while a workshop session is active.

    General workshop contract: while a workshop session is open, only
    that workshop's own commands (stems derived from its registry entry)
    plus meta commands run; everything else is rejected out-of-scope
    BEFORE normal dispatch. In-scope lines route through the SAME public
    dispatcher as outside — the workshop grants nothing new. Input is
    screened before scope decisions or recording (fail-closed); only
    command stems and fixed result codes are recorded, never raw lines.
    """
    from form.dell_matrix.workshop_session import (
        scope_stems, FAIL_PROTECTED, FAIL_OUT_OF_SCOPE, FAIL_SAVE)

    stripped = line.strip()
    lower = stripped.lower()

    # Screen raw input BEFORE scope decision, dispatch, or recording.
    if not _studio_screen_input(p, stripped):
        wsession.record("protected", f"rejected: {FAIL_PROTECTED}")
        _say(f"Rejected: {FAIL_PROTECTED}.")
        return p, wsession

    # leave: stage closed record, save, discard session only on success.
    if lower in ("leave", "workshop leave", "workshop exit"):
        closed_record = wsession.closed_copy()
        sid = closed_record["session_id"]
        prior = dict(getattr(p, "workshop_sessions", None) or {})
        prior_malformed = getattr(p, "workshop_sessions_malformed", None)
        prev_flag = p.active_workshop
        merged = dict(prior)
        merged[sid] = closed_record
        if len(merged) > 10:
            ordered = sorted(merged.items(),
                             key=lambda kv: str(kv[1].get("started", "")),
                             reverse=True)[:10]
            merged = dict(ordered)
        p.workshop_sessions = merged
        # Clear the active flag BEFORE save so persisted state is
        # coherent (not in a workshop, with a closed session record).
        # Restored on failure.
        p.leave_workshop()
        try:
            from form import persist_rest
            persist_rest.save(p)
            _say(f"Workshop session saved ({sid[:8]}...). "
                 f"Exited {wsession.workshop} workshop.")
            return p, None
        except Exception as exc:
            p.workshop_sessions = prior
            p.workshop_sessions_malformed = prior_malformed
            p.active_workshop = prev_flag
            _say(f"{FAIL_SAVE}: {type(exc).__name__}. "
                 f"Session retained ({sid[:8]}...); "
                 f"still in {wsession.workshop} workshop — 'leave' to retry.")
            return p, wsession

    if lower == "help":
        from form.dell_matrix.workshops import get_workshop
        w = get_workshop(wsession.workshop) or {}
        _say(f"{w.get('name', wsession.workshop)} — scoped session. "
             f"Only this workshop's commands run here:")
        for c in w.get("commands") or []:
            _say(f"  {c['label']}: {c['cmd']}")
        _say("Meta: workshops · leave (saves session and exits)")
        wsession.record("help", "shown")
        return p, wsession

    if lower in ("workshops", "workshop list"):
        wsession.record("workshops", "dispatched")
        import uuid as _uuid
        p = _dispatch_public_line(p, stripped, str(_uuid.uuid4()))
        return p, wsession

    if lower.startswith("workshop "):
        # Entering another workshop (or re-entering) from inside one:
        # one scoped environment at a time.
        wsession.record("workshop", f"rejected: {FAIL_OUT_OF_SCOPE}")
        _say("Already in a scoped workshop session. 'leave' first, "
             "then enter another workshop.")
        return p, wsession

    token = lower.split()[0] if lower.split() else ""
    if token and token in scope_stems(wsession.workshop):
        # In scope: route through the SAME public dispatcher.
        wsession.record(token, "dispatched")
        import uuid as _uuid
        p = _dispatch_public_line(p, stripped, str(_uuid.uuid4()))
        return p, wsession

    # Out-of-scope: explicit rejection before normal dispatch.
    # Fixed message: never reflect raw input text.
    wsession.record(token or "unknown", f"rejected: {FAIL_OUT_OF_SCOPE}")
    _say(f"Out of scope for the {wsession.workshop} workshop. "
         f"Type 'help' for its commands; 'leave' to exit.")
    return p, wsession


def _onboarding_show(p, session, move) -> None:
    """R7.4 (D2 Show): demonstrate the move in the isolated demo owner.

    Mirrors the tutorial's demo machinery: the demo program is
    DEMO_TUTORIAL_<owner>; only demo state is touched. The invoking
    owner's state changes only through their own Try steps. One demo
    instance serves the whole session (cached on the session object,
    runtime-only), so the demo accumulates across moves exactly like
    the tutorial's single demo program.
    """
    from form.open import open_program
    dp = getattr(session, "_demo", None)
    if dp is None:
        dp = open_program(f"DEMO_TUTORIAL_{p.owner}")
        session._demo = dp
    mid = move["id"]
    if mid == "create":
        dp.place("onboarding_demo", "Onboarding Demo",
                 words="shown example", skin=Skin.CUBE)
        _say('Show: in the demo, an idea "Onboarding Demo" was created.')
    elif mid == "grow_confirm":
        out = dp.grow_ideas(1)
        _say(f"Show: the demo grew — +{out.get('proposed_new', 0)} new "
             f"+{out.get('proposed_evolved', 0)} evolved proposed; "
             f"nursery pending {out.get('nursery', {}).get('pending', 0)}.")
        n = 0
        for prop in list(dp.list_proposals()):
            res = dp.confirm_proposal(
                prop["id"], _producer="onboarding_demo",
                _review_context=dp.make_review_context(
                    prop["id"], "onboarding_demo"))
            if res.get("ok"):
                n += 1
        _say(f"Show: the demo confirmed {n} proposal(s) into its matrix.")
    elif mid == "look":
        v = dp.look_around()
        seen = v.get("in_view_ids") or []
        _say(f"Show: the demo looks — facing {v.get('facing', '?')}, "
             f"sees {len(seen)} idea(s) in view.")
    elif mid == "save_load":
        path = dp.save()
        p2 = persist_load(dp.owner)
        _say(f"Show: the demo saved ({path}) and loaded back with "
             f"{len(p2.cube.session.plane.units)} idea(s).")


def _present_onboarding_move(p, session) -> None:
    """R7.4 (D2): present the current move — Show, then Explain."""
    from form.dell_matrix.onboarding_session import MOVES
    move = MOVES[session.move_index]
    print()
    _say(f"Move {session.move_index + 1} of {len(MOVES)} — {move['title']}")
    _onboarding_show(p, session, move)
    session.record(f"show:{move['id']}", "shown")
    _say(f"Why: {move['explain']}")
    session.record(f"explain:{move['id']}", "explained")
    _say(f"Your try: {move['try_hint']}")
    _say("('help' repeats this move · 'leave' ends without completing)")


def _verify_onboarding_try(p, move_id: str, stem: str,
                           before_units: int, before_pending: int) -> bool:
    """R7.4 (D2 Verify): check the observable result of the user's Try.

    Executed against live program state (or a fresh load of the saved
    state for save/load). A Try that changed nothing does not verify.
    """
    units = len(p.cube.session.plane.units)
    pending = (p.nursery.summary() or {}).get("pending", 0)
    if move_id == "create":
        return units > before_units
    if move_id == "grow_confirm":
        if stem == "grow":
            return pending > before_pending or units > before_units
        return units > before_units or pending < before_pending
    if move_id == "look":
        v = p.look_around()
        return isinstance(v, dict) and "in_view_ids" in v
    if move_id == "save_load":
        try:
            import os as _os
            from form.persist import _path as _persist_path
            if not _os.path.isfile(_persist_path(p.owner)):
                return False
            from form.persist_rest import load as _rest_load
            p2 = _rest_load(p.owner, activate=False)
            return len(p2.cube.session.plane.units) == units
        except Exception:
            return False
    return False


def _finish_onboarding(p, session, completed: bool):
    """R7.4: stage the closed record, save, exit only on success.

    Mirrors the studio/workshop stage-then-save: the closed record is
    built without mutating the session; graduation (first-run ->
    beginner) is applied BEFORE the save so persisted state is
    coherent; on save failure everything is restored and the session
    remains active for retry.
    """
    from form.dell_matrix.onboarding_session import FAIL_SAVE
    closed_record = session.closed_copy(completed)
    sid = closed_record["session_id"]
    prior = dict(getattr(p, "onboarding_sessions", None) or {})
    prior_malformed = getattr(p, "onboarding_sessions_malformed", None)
    prior_begun = getattr(p, "onboarding_begun", False)
    prior_completed = getattr(p, "onboarding_completed", False)
    prior_mode = p.ux_mode
    merged = dict(prior)
    merged[sid] = closed_record
    if len(merged) > 10:
        ordered = sorted(merged.items(),
                         key=lambda kv: str(kv[1].get("started", "")),
                         reverse=True)[:10]
        merged = dict(ordered)
    p.onboarding_sessions = merged
    p.onboarding_begun = True
    if completed:
        p.onboarding_completed = True
        if p.ux_mode == "first-run":
            p.set_ux_mode("beginner")
    try:
        from form import persist_rest
        persist_rest.save(p)
        if completed:
            _say(f"Onboarding complete — all moves verified in your "
                 f"own state. Session saved ({sid[:8]}...).")
            _say(f"Disclosure level: first-run → {p.ux_mode}. "
                 f"Type 'help' to see your wider surface.")
        else:
            _say(f"Onboarding session saved ({sid[:8]}...). Exited. "
                 f"Not complete — your level stays {p.ux_mode} until "
                 f"every move verifies.")
        return p, None
    except Exception as exc:
        p.onboarding_sessions = prior
        p.onboarding_sessions_malformed = prior_malformed
        p.onboarding_begun = prior_begun
        p.onboarding_completed = prior_completed
        p.ux_mode = prior_mode
        _say(f"{FAIL_SAVE}: {type(exc).__name__}. "
             f"Session retained ({sid[:8]}...); "
             f"still onboarding — 'leave' to retry.")
        return p, session


def _handle_onboarding_line(p, line: str, session):
    """R7.4: handle one input line while onboarding is active.

    Scoped-session gate (same position and discipline as the studio /
    workshop gates): input is screened fail-closed before any scope
    decision or recording; only the current move's Try stems route —
    through the SAME public dispatcher — plus bounded meta lines
    (help, proposals, status, leave). Everything else is rejected
    out-of-scope before dispatch. Only step kinds and fixed result
    codes are recorded, never raw lines.
    """
    from form.dell_matrix.onboarding_session import (
        MOVES, FAIL_PROTECTED, FAIL_OUT_OF_SCOPE)

    stripped = line.strip()
    lower = stripped.lower()

    if not _studio_screen_input(p, stripped):
        session.record("protected", f"rejected: {FAIL_PROTECTED}")
        _say(f"Rejected: {FAIL_PROTECTED}.")
        return p, session

    if lower in ("leave", "onboard leave", "onboard exit"):
        return _finish_onboarding(p, session, completed=False)

    if lower == "help":
        session.record("help", "shown")
        _present_onboarding_move(p, session)
        return p, session

    move = MOVES[session.move_index]
    parts = lower.split()
    token = parts[0] if parts else ""

    # Bounded meta: read-only orientation lines dispatch but never
    # count as a Try and never verify a move.
    if token in ("proposals", "status"):
        session.record(token, "dispatched")
        import uuid as _uuid
        p = _dispatch_public_line(p, stripped, str(_uuid.uuid4()))
        return p, session

    if token in move["try_stems"]:
        before_units = len(p.cube.session.plane.units)
        before_pending = (p.nursery.summary() or {}).get("pending", 0)
        session.record(f"try:{move['id']}", "dispatched")
        import uuid as _uuid
        p = _dispatch_public_line(p, stripped, str(_uuid.uuid4()))
        if _verify_onboarding_try(p, move["id"], token,
                                   before_units, before_pending):
            session.record(f"verify:{move['id']}", "verified")
            _say(f"Verified: {move['title']} — it happened in your "
                 f"own state.")
            session.move_index += 1
            if session.move_index >= len(MOVES):
                return _finish_onboarding(p, session, completed=True)
            _present_onboarding_move(p, session)
            return p, session
        session.record(f"verify:{move['id']}", "not verified")
        _say(f"Not verified: that did not change your state yet. "
             f"Try: {move['try_hint']}")
        return p, session

    session.record(token or "unknown", f"rejected: {FAIL_OUT_OF_SCOPE}")
    _say(f"Onboarding: that is not this move's try. "
         f"{move['title']} — your try: {move['try_hint']} "
         f"(or 'help' / 'leave').")
    return p, session


_FORGE_COMMANDS = (
    "Forge commands:",
    "  status              staged arrangement (live body untouched)",
    "  dock <slot> <persona> · undock <slot> · pilot <name>",
    "  defaults · clear    stage the default dock / empty slots",
    "  preview             fuse the STAGED arrangement",
    "  configs             named configurations",
    "  load <name>         stage a named configuration",
    "  save <name>         commit: staged arrangement becomes the live",
    "                      body AND a named configuration (one save)",
    "  help · leave        leave saves session evidence and exits;",
    "                      unsaved staging is discarded",
)


def _forge_present(session) -> None:
    """R7.5: show the staged arrangement (never the live body)."""
    body = session.staged_body()
    for line in body.render_ascii():
        _say(line)
    st = body.status()
    _say(f"Staged: filled {st['filled_count']}/{len(st['slots'])} · "
         f"pilot={st['pilot']} · live body untouched until 'save <name>'")


def _finish_forge(p, session):
    """R7.5: stage the closed record, save, exit only on success.

    Mirrors the studio/workshop/onboarding stage-then-save: on save
    failure the priors are restored and the forge stays open for
    retry. Configurations committed during the session were saved at
    commit time and are not affected by this save either way.
    """
    from form.dell_matrix.bimo_forge import FAIL_SAVE
    closed_record = session.closed_copy()
    sid = closed_record["session_id"]
    prior = dict(getattr(p, "forge_sessions", None) or {})
    prior_malformed = getattr(p, "forge_sessions_malformed", None)
    merged = dict(prior)
    merged[sid] = closed_record
    if len(merged) > 10:
        ordered = sorted(merged.items(),
                         key=lambda kv: str(kv[1].get("started", "")),
                         reverse=True)[:10]
        merged = dict(ordered)
    p.forge_sessions = merged
    try:
        from form import persist_rest
        persist_rest.save(p)
        _say(f"Forge session saved ({sid[:8]}...). Exited. "
             f"Configurations saved during the session remain stored "
             f"and live.")
        return p, None
    except Exception as exc:
        p.forge_sessions = prior
        p.forge_sessions_malformed = prior_malformed
        _say(f"{FAIL_SAVE}: {type(exc).__name__}. "
             f"Session retained ({sid[:8]}...); "
             f"still in the forge — 'leave' to retry.")
        return p, session


def _commit_forge_config(p, session, raw_name: str):
    """R7.5: commit the staged arrangement as a named configuration.

    One canonical save applies BOTH effects — the live body adopts the
    staged slots/pilot, and the named configuration is stored — with
    stage-then-save semantics: on failure every prior is restored, so
    neither effect can land alone. The configuration is validated
    against the strict schema BEFORE anything is applied, so staged
    state the schema would reject (e.g. an unknown persona reference
    inherited from hand-edited live state) fails here, honestly,
    instead of being silently preserved as malformed on save.
    """
    from form.dell_matrix.bimo_forge import (
        FAIL_SAVE, make_configuration, normalize_config_name,
        validate_configuration)
    from form.dell_matrix.personas import BIMO_SLOTS
    name = normalize_config_name(raw_name)
    if name is None:
        session.record("save", "rejected: invalid configuration name")
        _say("Save rejected: a configuration name is 1-48 chars of "
             "a-z, 0-9, '-' or '_', starting with a letter or digit.")
        return p
    config = make_configuration(name, p.owner, session.staged_slots,
                                session.staged_pilot)
    ok, err = validate_configuration(config, p.owner)
    if not ok:
        session.record("save", "rejected: staged arrangement invalid")
        _say(f"Save rejected: {err}. Fix the staged arrangement "
             f"('status' shows it) and save again.")
        return p
    prior_slots = dict(p.bimo.slots)
    prior_pilot = p.bimo.pilot
    prior_mode = p.bimo.mode
    prior_lens = getattr(p, "persona_lens", None)
    prior_matrix = (p.persona_matrix.active
                    if getattr(p, "persona_matrix", None) is not None
                    else None)
    prior_configs = dict(getattr(p, "bimo_configurations", None) or {})
    prior_cmalformed = getattr(p, "bimo_configurations_malformed", None)
    merged = dict(prior_configs)
    merged[name] = config
    if len(merged) > 10:
        ordered = sorted(merged.items(),
                         key=lambda kv: str(kv[1].get("saved", "")),
                         reverse=True)[:10]
        merged = dict(ordered)
    p.bimo.slots = {s: session.staged_slots.get(s) for s in BIMO_SLOTS}
    p.bimo.mode = "docked"
    if session.staged_pilot != prior_pilot:
        p.bimo.set_pilot(session.staged_pilot)
        p.persona_lens = session.staged_pilot
        if getattr(p, "persona_matrix", None) is not None:
            p.persona_matrix.active = session.staged_pilot
    p.bimo_configurations = merged
    try:
        from form import persist_rest
        persist_rest.save(p)
    except Exception as exc:
        p.bimo.slots = prior_slots
        p.bimo.pilot = prior_pilot
        p.bimo.mode = prior_mode
        p.persona_lens = prior_lens
        if getattr(p, "persona_matrix", None) is not None:
            p.persona_matrix.active = prior_matrix
        p.bimo_configurations = prior_configs
        p.bimo_configurations_malformed = prior_cmalformed
        session.record("save", f"rejected: {FAIL_SAVE}")
        _say(f"{FAIL_SAVE}: {type(exc).__name__}. Nothing committed — "
             f"the live body and stored configurations are unchanged; "
             f"the staged arrangement is retained.")
        return p
    session.record("save", f"configuration committed: {name}")
    _say(f"Committed '{name}': the staged arrangement is now the live "
         f"BIMO body and is stored as a named configuration.")
    return p


def _handle_forge_line(p, line: str, session):
    """R7.5: handle one input line while the BIMO Forge is active.

    Scoped-session gate in the same position as the studio / workshop
    / onboarding gates: input is screened fail-closed before any scope
    decision or recording. Commands operate on the session's STAGED
    copy through BIMOBody's own methods (one docking authority); the
    live body changes only via an explicit 'save <name>' commit.
    Nothing here routes to the public dispatcher. Only step kinds and
    fixed result summaries are recorded, never raw lines.
    """
    from form.dell_matrix.bimo_forge import (
        FAIL_OUT_OF_SCOPE, FAIL_PROTECTED, normalize_config_name)

    stripped = line.strip()
    lower = stripped.lower()
    parts = lower.split()
    token = parts[0] if parts else ""

    if not _studio_screen_input(p, stripped):
        session.record("protected", f"rejected: {FAIL_PROTECTED}")
        _say(f"Rejected: {FAIL_PROTECTED}.")
        return p, session

    if lower in ("leave", "forge leave", "forge exit"):
        return _finish_forge(p, session)

    if lower == "help":
        session.record("help", "shown")
        for ln in _FORGE_COMMANDS:
            _say(ln)
        return p, session

    if lower == "status":
        session.record("status", "shown")
        _forge_present(session)
        return p, session

    if lower == "preview":
        body = session.staged_body()
        was_empty = not any(body.slots.values())
        out = body.fuse()
        session.adopt(body)
        session.record("preview", "fused staged arrangement")
        for ln in out.get("guidance") or []:
            _say(ln)
        if was_empty:
            _say("(The staged arrangement was empty; the fusion pass "
                 "staged the default dock, as 'bimo fuse' does.)")
        return p, session

    if token == "dock" and len(parts) == 3:
        body = session.staged_body()
        out = body.dock(parts[1], parts[2])
        if out.get("ok"):
            session.adopt(body)
            session.record("dock", "docked")
            pe = out.get("persona_meta") or {}
            _say(f"Staged: {pe.get('emoji', '')} "
                 f"{pe.get('name', parts[2])} → slot [{parts[1]}] "
                 f"(live body untouched)")
        else:
            reason = str(out.get("reason") or "")
            code = ("unknown slot" if "unknown slot" in reason
                    else "unknown persona")
            session.record("dock", f"rejected: {code}")
            _say(f"Fail: {out.get('reason')}")
        return p, session

    if token == "undock" and len(parts) == 2:
        body = session.staged_body()
        out = body.undock(parts[1])
        if out.get("ok"):
            session.adopt(body)
            session.record("undock", "undocked")
            _say(f"Staged: slot [{parts[1]}] emptied "
                 f"(was {out.get('undocked')})")
        else:
            session.record("undock", "rejected: unknown slot")
            _say(f"Fail: {out.get('reason')}")
        return p, session

    if token == "pilot" and len(parts) == 2:
        body = session.staged_body()
        out = body.set_pilot(parts[1])
        if out.get("ok"):
            session.adopt(body)
            session.record("pilot", "pilot staged")
            _say(f"Staged pilot → {out['pilot']} (applies on save)")
        else:
            session.record("pilot", "rejected: unknown persona")
            _say(f"Fail: {out.get('reason')}")
        return p, session

    if lower == "defaults":
        body = session.staged_body()
        body.dock_defaults()
        session.adopt(body)
        session.record("defaults", "default dock staged")
        _forge_present(session)
        return p, session

    if lower == "clear":
        body = session.staged_body()
        body.clear()
        session.adopt(body)
        session.record("clear", "slots cleared in staging")
        _say("Staged: all slots cleared (live body untouched).")
        return p, session

    if lower == "configs":
        session.record("configs", "listed")
        configs = getattr(p, "bimo_configurations", None) or {}
        if not configs:
            _say("No named configurations stored yet. "
                 "'save <name>' stores the staged arrangement.")
        for nm in sorted(configs):
            cfg = configs[nm]
            filled = sum(1 for v in (cfg.get("slots") or {}).values() if v)
            _say(f"  {nm} · pilot={cfg.get('pilot')} · "
                 f"{filled} slot(s) filled · saved {cfg.get('saved')}")
        return p, session

    if token == "load" and len(parts) == 2:
        name = normalize_config_name(parts[1])
        configs = getattr(p, "bimo_configurations", None) or {}
        cfg = configs.get(name) if name else None
        if cfg is None:
            session.record("load", "rejected: unknown configuration")
            _say(f"No stored configuration named '{parts[1]}'. "
                 f"'configs' lists what exists.")
            return p, session
        from form.dell_matrix.personas import BIMO_SLOTS
        session.staged_slots = {s: (cfg.get("slots") or {}).get(s)
                                for s in BIMO_SLOTS}
        session.staged_pilot = cfg["pilot"]
        session.record("load", "configuration staged")
        _say(f"Staged configuration '{name}' (live body untouched "
             f"until 'save <name>').")
        _forge_present(session)
        return p, session

    if token == "save" and len(parts) == 2:
        return _commit_forge_config(p, session, parts[1]), session

    session.record(token or "unknown", f"rejected: {FAIL_OUT_OF_SCOPE}")
    _say("Forge: that is not a forge command here. 'help' lists the "
         "forge commands; the live body changes only via 'save <name>'.")
    return p, session


_CONNECT_COMMANDS = (
    "Connect commands:",
    "  status              gate state, provider, dock, pending count",
    "  internet on|off     the existing gate (default OFF, allowlist",
    "                      enforced by the gate itself)",
    "  allow <host>        add a host to the gate allowlist",
    "  fetch <url>         gated fetch; records provenance evidence",
    "                      (host, status, bytes) — never content",
    "  provider <name>     select the inference provider BY NAME only",
    "                      (default 'fake': deterministic, offline;",
    "                      credentials are read from the host",
    "                      environment, never entered here)",
    "  ask <prompt>        docked inference -> a PENDING Nursery",
    "                      proposal (never auto-confirmed)",
    "  help · leave        leave saves session evidence and exits",
)


def _connect_status(p, session) -> None:
    st = p.internet_status() if hasattr(p, "internet_status") else {}
    _say(f"Internet gate: {'ON' if st.get('on') else 'OFF'} · "
         f"hosts allowed: {st.get('host_count', 0)}")
    _say(f"Provider: {session.provider} "
         f"({'offline deterministic' if session.provider == 'fake' else 'host bridge, explicit name'}) · "
         f"docked: {'yes' if session.docked is not None else 'no'}")
    pend = (p.nursery.summary() or {}).get("pending", 0)
    _say(f"Nursery proposals pending review: {pend}")


def _finish_connection(p, session):
    """R7.6: stage the closed record, save, exit only on success.

    Mirrors the other scoped sessions' stage-then-save. The dock
    handle is runtime-only: it is undocked after a successful save;
    on failure the session (and its dock) stays intact for retry.
    Gate changes made during the session persist with this save —
    the gate's own durable section carries them.
    """
    from form.dell_matrix.connection_session import FAIL_SAVE
    closed_record = session.closed_copy()
    sid = closed_record["session_id"]
    prior = dict(getattr(p, "connection_sessions", None) or {})
    prior_malformed = getattr(p, "connection_sessions_malformed", None)
    merged = dict(prior)
    merged[sid] = closed_record
    if len(merged) > 10:
        ordered = sorted(merged.items(),
                         key=lambda kv: str(kv[1].get("started", "")),
                         reverse=True)[:10]
        merged = dict(ordered)
    p.connection_sessions = merged
    try:
        from form import persist_rest
        persist_rest.save(p)
    except Exception as exc:
        p.connection_sessions = prior
        p.connection_sessions_malformed = prior_malformed
        _say(f"{FAIL_SAVE}: {type(exc).__name__}. "
             f"Session retained ({sid[:8]}...); "
             f"still connected — 'leave' to retry.")
        return p, session
    if session.docked is not None:
        try:
            session.docked.undock()
        except Exception:
            pass
        session.docked = None
    _say(f"Connection session saved ({sid[:8]}...). Exited.")
    return p, None


def _handle_connect_line(p, line: str, session):
    """R7.6: handle one input line while the connect session is active.

    Scoped-session gate in the same position as the other scoped
    gates: input is screened fail-closed before any scope decision or
    recording. Commands route ONLY to the two existing authorities —
    the InternetGate (via the Program's gate methods) and the
    inference dock (via its host dock() + DockedSession.propose()).
    Nothing here routes to the public dispatcher. Only step kinds and
    fixed result summaries are recorded: never prompts, never fetched
    content, never credentials.
    """
    from form.dell_matrix.connection_session import (
        FAIL_DOCK, FAIL_OUT_OF_SCOPE, FAIL_PROTECTED)

    stripped = line.strip()
    lower = stripped.lower()
    parts = lower.split()
    token = parts[0] if parts else ""

    if not _studio_screen_input(p, stripped):
        session.record("protected", f"rejected: {FAIL_PROTECTED}")
        _say(f"Rejected: {FAIL_PROTECTED}.")
        return p, session

    if lower in ("leave", "connect leave", "connect exit"):
        return _finish_connection(p, session)

    if lower == "help":
        session.record("help", "shown")
        for ln in _CONNECT_COMMANDS:
            _say(ln)
        return p, session

    if lower == "status":
        session.record("status", "shown")
        _connect_status(p, session)
        return p, session

    if lower in ("internet on", "internet off"):
        on = lower.endswith(" on")
        out = p.internet_on() if on else p.internet_off()
        session.record("internet", "gate on" if on else "gate off")
        _say(out.get("msg") or ("Internet ON" if on else "Internet OFF"))
        return p, session

    if token == "allow" and len(parts) == 2:
        host = p.internet.allow_host(parts[1]) if p.internet else ""
        session.record("allow", "host allowed")
        _say(f"Allowed host → {host}")
        return p, session

    if token == "fetch" and len(parts) == 2:
        url = stripped.split(maxsplit=1)[1].strip()
        out = p.net_fetch(url)
        if out.get("ok"):
            from urllib.parse import urlparse
            host = urlparse(out.get("url") or url).hostname or "unknown"
            session.record(
                "fetch",
                f"host={host} status={out.get('status')} "
                f"bytes={out.get('bytes')}")
            _say(f"Fetched {out.get('url')} ({out.get('bytes')} bytes)")
            _say((out.get("preview") or "")[:400])
            _say("(Provenance recorded: host, status, bytes. Content "
                 "is not stored as knowledge.)")
        else:
            err = str(out.get("error") or "")
            code = ("gate off" if "OFF" in err
                    else "host not allowed" if "not allowed" in err
                    else "fetch failed")
            session.record("fetch", f"rejected: {code}")
            _say(err or "fetch failed")
        return p, session

    if token == "provider" and len(parts) == 2:
        name = parts[1]
        if not all(c.isalnum() or c in "_-" for c in name):
            session.record("provider", "rejected: invalid provider name")
            _say("Provider rejected: a provider is selected by a single "
                 "name token only. Credentials are never entered here — "
                 "providers read them from the host environment.")
            return p, session
        if session.docked is not None:
            try:
                session.docked.undock()
            except Exception:
                pass
            session.docked = None
        session.provider = name
        session.record("provider", "provider selected")
        _say(f"Provider → {name}. It takes effect on the next 'ask'.")
        return p, session

    if token == "ask" and len(parts) >= 2:
        prompt = stripped.split(maxsplit=1)[1]
        if session.docked is None:
            from form.dell_matrix.inference_dock import DockError, dock
            try:
                session.docked = dock(
                    p, trusted_subject=f"connect:{p.owner}",
                    provider=session.provider)
            except DockError as e:
                session.record("ask", f"rejected: {FAIL_DOCK}")
                _say(f"{FAIL_DOCK}: {e}")
                return p, session
            except Exception as e:
                session.record("ask", f"rejected: {FAIL_DOCK}")
                _say(f"{FAIL_DOCK}: {type(e).__name__}")
                return p, session
        out = session.docked.propose(prompt)
        if out.get("ok"):
            session.record("ask", "proposal pending")
            _say(f"Proposal {out.get('pid')} created — PENDING in the "
                 f"Nursery (provider={out.get('provider')}, "
                 f"model={out.get('model')}). It is not confirmed and "
                 f"carries no authority; review it with 'proposals'.")
        else:
            reason = str(out.get("reason") or "failed")
            if len(reason) > 32 or not all(
                    c.isalnum() or c in "_-" for c in reason):
                reason = "failed"
            session.record("ask", f"rejected: {reason}")
            _say(f"Ask failed ({reason}): {out.get('detail') or ''}")
        return p, session

    session.record(token or "unknown", f"rejected: {FAIL_OUT_OF_SCOPE}")
    _say("Connect: that is not a connect command here. 'help' lists "
         "the connect commands.")
    return p, session


def run(owner: str = "Operator", do_load: bool = False) -> None:
    print()
    print("  DellMatrix — Mandell Origin")
    print("  Offline · Type tutorial  or  help")
    print("  Try: create an idea called test")
    print("  Depth: explain create · la cresce 2")
    print("  Live: live  · look  · zoom <id>  · mode first-run|beginner|builder|depth")
    print()
    _session_existed = False
    if do_load:
        # M (CA01-MISSING-SESSION): persist.load() intentionally yields a fresh
        # owner when no file exists, so the receipt must not claim a load that
        # never happened. Mirrors the in-REPL load guard (~line 2267).
        from form.persist import _path as _persist_path
        import os as _os
        _session_existed = _os.path.isfile(_persist_path(owner))
        p = persist_load(owner)
    else:
        p = open_program(owner)
    if not do_load:
        from form.mandell.language import bind
        bind(p)  # Q-022: explicit owner binding BEFORE any customize, so customize > save > --load restores it
        # R7.4 (D1): a REPL start with no persisted state file is a
        # brand-new owner — they start at the first-run level with
        # onboarding begun. (An owner WITH a state file who starts
        # without --load keeps the pre-existing fresh in-memory start;
        # their persisted level is governed by the load path.)
        from form.persist import _path as _repl_state_path
        import os as _repl_os
        if not _repl_os.path.isfile(_repl_state_path(owner)):
            from form.dell_matrix.onboarding_session import mark_new_owner
            mark_new_owner(p)
    if do_load:
        _say(f"Loaded session for {owner}." if _session_existed
             else f"No saved session for {owner}; started fresh.")
    print(p.render())
    print()

    # IRI-I: staged reissue source. Session-only; never persisted.
    _pending_reissue: Optional[str] = None

    # R7.2: active Perspective Studio. Session-only; never persisted.
    # Reload restores closed session records, not the active mode.
    _studio = None

    # R7.3: active general workshop session. Session-only like the
    # studio: reload restores closed session records, never the mode.
    _wsession = None

    # R7.4: active onboarding session. Session-only like the studio /
    # workshop modes: reload restores closed session records and the
    # begun/completed facts, never the active flow.
    _osession = None

    # R7.5: active BIMO Forge session. Session-only like the other
    # scoped modes: reload restores closed session records and named
    # configurations, never the active staging.
    _forge = None

    # R7.6: active Connected World session. Session-only like the
    # other scoped modes: reload restores closed session records,
    # never the active session, its provider selection, or its dock.
    _connect = None

    while True:
        # R7.2/R7.3/R7.4: scoped prompts. Active scoped modes are
        # session-only.
        if _studio is not None:
            _prompt = "studio> "
        elif _wsession is not None:
            _prompt = f"workshop:{_wsession.workshop}> "
        elif _osession is not None:
            _prompt = "onboard> "
        elif _forge is not None:
            _prompt = "forge> "
        elif _connect is not None:
            _prompt = "connect> "
        else:
            _prompt = "you> "
        try:
            line = input(_prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            # R7.2: explicit EOF behavior in studio mode. Unsaved studio
            # evidence is NOT persisted; state this plainly.
            if _studio is not None:
                _say("Studio session NOT saved (EOF). "
                     "Use 'leave' inside the studio to persist evidence.")
            if _wsession is not None:
                _say("Workshop session NOT saved (EOF). "
                     "Use 'leave' inside the workshop to persist evidence.")
            if _osession is not None:
                _say("Onboarding session NOT saved (EOF). "
                     "Use 'leave' inside onboarding to persist evidence.")
            if _forge is not None:
                _say("Forge session NOT saved (EOF). Staged changes are "
                     "discarded; configurations saved with 'save <name>' "
                     "during the session remain saved.")
            if _connect is not None:
                _say("Connection session NOT saved (EOF). Nothing from "
                     "this session was persisted — use 'leave' inside "
                     "connect to persist the session.")
            break
        if not line:
            continue
        if line.lower() in ("quit", "exit", "q"):
            # R7.2: explicit quit behavior in studio mode.
            if _studio is not None:
                _say("Studio session NOT saved (quit). "
                     "Use 'leave' inside the studio to persist evidence.")
            if _wsession is not None:
                _say("Workshop session NOT saved (quit). "
                     "Use 'leave' inside the workshop to persist evidence.")
            if _osession is not None:
                _say("Onboarding session NOT saved (quit). "
                     "Use 'leave' inside onboarding to persist evidence.")
            if _forge is not None:
                _say("Forge session NOT saved (quit). Staged changes are "
                     "discarded; configurations saved with 'save <name>' "
                     "during the session remain saved.")
            if _connect is not None:
                _say("Connection session NOT saved (quit). Nothing from "
                     "this session was persisted — use 'leave' inside "
                     "connect to persist the session.")
            _say("Goodbye.")
            break

        # R7.2: Perspective Studio mode. Session-only; the active studio is
        # never persisted (reload restores closed session records, not the
        # mode). While active, ALL inputs pass through the scoped command
        # handler before normal dispatch. This gate is ahead of every
        # non-exit special handler (say-prefix, reissue, etc.): a reissue
        # staged before studio entry cannot execute inside the studio, and
        # a reissue requested inside the studio cannot reach dispatch.
        # No mutations route from this circuit.
        if _studio is not None:
            p, _studio = _handle_studio_line(p, line, _studio)
            continue

        # R7.3: general workshop session mode. Same gate position as the
        # studio: ahead of say-prefix, reissue, and normal dispatch, so
        # nothing staged or prefixed outside can execute inside, and
        # nothing inside can reach dispatch except the workshop's own
        # commands through the same public dispatcher.
        if _wsession is not None:
            p, _wsession = _handle_workshop_line(p, line, _wsession)
            continue

        # R7.4: onboarding session mode. Same gate position as the
        # studio / workshop gates: ahead of say-prefix, reissue, and
        # normal dispatch, so nothing staged or prefixed outside can
        # execute inside, and inside only the current move's Try (plus
        # bounded meta lines) reaches the public dispatcher.
        if _osession is not None:
            p, _osession = _handle_onboarding_line(p, line, _osession)
            continue

        # R7.5: BIMO Forge session mode. Same gate position as the
        # other scoped gates: ahead of say-prefix, reissue, and normal
        # dispatch. Inside the forge, commands stage a detached BIMO
        # arrangement; the live body changes only via an explicit
        # commit inside the session.
        if _forge is not None:
            p, _forge = _handle_forge_line(p, line, _forge)
            continue

        # R7.6: Connected World session mode. Same gate position as
        # the other scoped gates: ahead of say-prefix, reissue, and
        # normal dispatch. Inside, commands route only to the
        # InternetGate and the inference dock — the public dispatcher
        # is not reachable from here.
        if _connect is not None:
            p, _connect = _handle_connect_line(p, line, _connect)
            continue

        # R7.3: entering a workshop opens a scoped session. Intercepted
        # here (like the studio entry) so the gate owns the session from
        # the first line. Unknown ids fall through to normal dispatch,
        # which reports them exactly as before.
        if line.lower().startswith("workshop "):
            _wid = line.lower().split(maxsplit=1)[1].strip()
            from form.dell_matrix.workshops import get_workshop as _get_ws
            if _get_ws(_wid) is not None:
                _out = p.enter_workshop(_wid)
                if _out.get("ok"):
                    from form.dell_matrix.workshop_session import (
                        WorkshopSession as _WS)
                    _wsession = _WS.open(p.owner, _wid)
                    _wsession.record("enter", "workshop entered")
                    _w = _out["workshop"]
                    _say(f"Entered {_w['name']}: {_w.get('description','')}")
                    for _c in _w.get("commands") or []:
                        _say(f"  {_c['label']}: {_c['cmd']}")
                    _say("Scoped session: only this workshop's commands "
                         "run here. 'leave' saves the session and exits.")
                    continue

        # R7.4: entering onboarding opens the scoped teach-rhythm
        # session. Intercepted here (like the studio / workshop
        # entries) so the gate owns the session from the first line.
        if line.lower() == "onboard":
            if getattr(p, "onboarding_completed", False):
                _say("Onboarding already complete for this owner — "
                     "every move was verified in your own state. "
                     f"Disclosure level: {p.ux_mode}.")
                continue
            from form.dell_matrix.onboarding_session import (
                OnboardingSession as _OS)
            p.onboarding_begun = True
            _osession = _OS.open(p.owner)
            _osession.record("enter", "onboarding entered")
            _say("Onboarding — learn by doing. Four moves; for each: "
                 "I show it in an isolated demo, explain why, you try "
                 "it in your own state, and I verify it happened.")
            _present_onboarding_move(p, _osession)
            continue

        # R7.5: entering the BIMO Forge opens the scoped staging
        # session. Intercepted here (like the other scoped entries) so
        # the gate owns the session from the first line; the entry is
        # below every scoped gate, so the forge cannot be entered from
        # inside the studio, a workshop, or onboarding.
        if line.lower() == "forge":
            from form.dell_matrix.bimo_forge import ForgeSession as _FS
            _forge = _FS.open(p.owner, dict(p.bimo.slots), p.bimo.pilot)
            _forge.record("enter", "forge entered")
            _say("BIMO Forge — build a BIMO arrangement on a staged "
                 "copy. The live body does not change until you commit "
                 "with 'save <name>', which also stores the arrangement "
                 "as a named configuration.")
            for _ln in _FORGE_COMMANDS:
                _say(_ln)
            _forge_present(_forge)
            continue

        # R7.6: entering Connected World opens the scoped connection
        # session. Intercepted here (like the other scoped entries) so
        # the gate owns the session from the first line; the entry is
        # below every scoped gate, so it cannot be entered from inside
        # the studio, a workshop, onboarding, or the forge.
        if line.lower() == "connect":
            from form.dell_matrix.connection_session import (
                ConnectionSession as _CS)
            _connect = _CS.open(p.owner)
            _connect.record("enter", "connection entered")
            _say("Connected World — the gated public path to the "
                 "internet gate and the inference dock. The gate is "
                 "OFF until you turn it on; fetches record provenance "
                 "evidence (host, status, bytes), never content; "
                 "docked inference creates PENDING proposals only; "
                 "credentials are never entered here — providers read "
                 "them from the host environment.")
            for _ln in _CONNECT_COMMANDS:
                _say(_ln)
            _connect_status(p, _connect)
            continue

        if line.lower().startswith("say "):
            line = line[4:].strip()

        # IRI-I: staged reissue — inspect/show, then explicit confirm.
        # Handled here (not in _dispatch_public_line): reissue is session
        # control, not semantic input. The staged source itself, when
        # confirmed, goes through _dispatch_public_line below.
        # NOTE: this is AFTER the studio gate above. While the studio is
        # active, reissue commands are rejected as out-of-scope and never
        # reach this handler.
        if line.lower() == "reissue" or line.lower().startswith("reissue "):
            p, _pending_reissue = _handle_reissue(p, line, _pending_reissue)
            continue

        if line.lower() == "perspective studio":
            from form.dell_matrix.perspective_studio import PerspectiveStudio
            _studio = PerspectiveStudio(p)
            _studio._record("enter", "studio entered")
            _say("Perspective Studio — scoped composition workshop.")
            _say("Type 'help' for studio commands, 'leave' to exit.")
            continue

        # EIC-I: mint interaction identity for this public attempt.
        # One ID per submitted line, before dispatch. UUIDv4: unique,
        # opaque, no timestamp leakage. This ID is propagated explicitly
        # to Outcome-creating paths; zero-Outcome paths simply don't use it.
        # Minting authority is HERE (public orchestration), not in routing/
        # execution/observation layers (those ACCEPT identity).
        import uuid as _uuid
        interaction_id = str(_uuid.uuid4())

        # IRI-I: canonical public execution boundary. Reissue confirm feeds
        # recovered source through this same function with a fresh ID.
        p = _dispatch_public_line(p, line, interaction_id)

    print()


def main() -> None:
    owner = "Operator"
    do_load = "--load" in sys.argv
    for i, a in enumerate(sys.argv):
        if a == "--owner" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
    run(owner, do_load)


if __name__ == "__main__":
    main()
