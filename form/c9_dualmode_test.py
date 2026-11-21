#!/usr/bin/env python3
"""C9 — Translate dual-mode (DD-36 / SS12.34a-b) + DD-35 honest no-intent.

Ace sequencing: DD-36's "not yet" (2026-11-09) was lifted by Ace's
2026-11-20 ruling (item 10): "Row #157 Adapt: NOW — DualMode build
authorized." Design of record: ACE_FUTURE_DEVELOPMENT_PLAN SS12.34a/b
+ the C9 circuit block.

Contract under test:
- Inside Dell 45 (Translate), a deterministic Adapt-architecture
  intent layer sits IN FRONT OF the existing pattern router: the
  router's families are the layer's vocabulary/entities; the layer
  determines intent type + entities + confidence; the canonical
  cascade still CONSTRUCTS the Intent (no second operand authority).
- translate_dual() is the dual-mode door. UNDOCKED: deterministic
  layers only. DOCKED: the canonical cascade stands in for the docked
  AI's understanding; residue is marked proposal-only (the dock may
  propose a translation as pending work — the door never invents one).
- Every dual-door result carries an engine receipt naming the layer
  that translated (adapt / router / dock / guard / none) + confidence
  where meaningful (DD-36 receipt labeling).
- DD-35 in both modes: text beyond the honest deterministic subset
  yields an explicit no_intent at the dual door — dell None, mandel
  "" — never an invented Show seed. Safety guards (conditional /
  negation + destructive) bind both modes.
- adapt_determine() is Translate as a tool (SS12.34b item 3): the
  deterministic layer callable on its own; it never calls translate
  (no Translate<->dock loop by construction).
- Canonical translate() is behavior-unchanged: no receipt attached,
  unknown text still returns the canonical unknown Intent (existing
  consumers depend on it); the dual door owns DD-35/DD-36.

Labels: UNIT/INTEGRATION (pure functions, no program state).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CHECKS = []


def check(name, cond):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def run_all():
    from form.mandell import adapt_intent
    from form.mandell.adapt_intent import build_default_engine, ADAPT_CREDIT
    from form.mandell.translate import translate, translate_dual, adapt_determine

    engine = build_default_engine()

    # --- the deterministic layer itself -------------------------------
    d = engine.determine("grow 3")
    check("c9_engine_grow_count",
          d is not None and d.intent_type == "GrowIntent"
          and d.action == "grow" and "3" in d.entities.get("Count", [])
          and d.confidence >= 0.9)
    d = engine.determine("walk forward 3")
    check("c9_engine_walk_entities",
          d is not None and d.intent_type == "WalkIntent"
          and "forward" in d.entities.get("Direction", [])
          and "3" in d.entities.get("Count", []))
    check("c9_engine_turn_requires_direction",
          engine.determine("turn") is None
          and engine.determine("turn left") is not None
          and engine.determine("turn left").intent_type == "TurnIntent")
    check("c9_engine_prose_none",
          engine.determine("the weather is nice today") is None
          and engine.determine("flibberty gibbet") is None)
    d1 = engine.determine("grow 3")
    d2 = engine.determine("grow 3")
    check("c9_engine_deterministic_confidence",
          d1 is not None and d2 is not None
          and d1.confidence == d2.confidence
          and d1.intent_type == d2.intent_type)
    import inspect
    src = inspect.getsource(adapt_intent)
    check("c9_engine_no_translate_import",
          "from .translate" not in src and "import translate" not in src
          and getattr(adapt_intent, "translate", None) is None)
    check("c9_credit_present",
          "Mycroft" in ADAPT_CREDIT and "Sean Fitzgerald" in ADAPT_CREDIT
          and "Apache-2.0" in ADAPT_CREDIT)

    # --- dual door, undocked ------------------------------------------
    i = translate_dual("grow 3")
    check("c9_dual_grow_adapt_layer",
          i.action == "grow" and i.args.get("cycles") == 3
          and i.engine is not None and i.engine.get("layer") == "adapt"
          and i.engine.get("mode") == "undocked"
          and (i.engine.get("confidence") or 0) >= 0.9
          and i.engine.get("intent_type") == "GrowIntent")
    i = translate_dual("walk forward 3")
    check("c9_dual_walk_adapt_layer",
          i.action == "walk" and i.args.get("steps") == 3
          and i.engine.get("layer") == "adapt")
    i = translate_dual("stamp victory")
    check("c9_dual_stamp_operands",
          i.action == "stamp" and i.args.get("mark") == "victory"
          and i.engine.get("layer") == "adapt")
    i = translate_dual("confirm all")
    check("c9_dual_confirm_adapt_layer",
          i.action == "nurture" and i.args.get("op") == "confirm"
          and i.engine.get("layer") == "adapt")
    i = translate_dual("show")
    check("c9_dual_show_adapt_layer",
          i.action == "show" and i.engine.get("layer") == "adapt")
    i = translate_dual("place the oak")
    check("c9_dual_place_agreement",
          i.action == "place" and i.engine.get("layer") == "adapt")
    i = translate_dual("grow 2 then show")
    check("c9_dual_compound_router_layer",
          i.action == "sequence" and " > " in i.mandel
          and i.engine.get("layer") == "router")
    i = translate_dual("the weather is nice today")
    check("c9_dual_no_intent_prose",
          i.action == "no_intent" and i.dell is None and i.mandel == ""
          and i.engine.get("layer") == "none")
    i = translate_dual("flibberty gibbet")
    check("c9_dual_no_intent_gibberish",
          i.action == "no_intent" and i.dell is None and i.mandel == "")
    check("c9_dual_empty",
          translate_dual("").action == "nothing_to_translate")
    i = translate_dual("don't delete the oak")
    check("c9_dual_guard_negation",
          i.action == "unknown" and i.engine.get("layer") == "guard")
    i = translate_dual("delete the oak if it rains")
    check("c9_dual_guard_conditional",
          i.action == "unknown" and i.engine.get("layer") == "guard")

    # --- dual door, docked ---------------------------------------------
    i = translate_dual("grow 3", docked=True)
    check("c9_dual_docked_grow",
          i.action == "grow" and i.args.get("cycles") == 3
          and i.engine.get("layer") == "dock"
          and i.engine.get("mode") == "docked"
          and i.engine.get("residue") is False)
    i = translate_dual("the weather is nice today", docked=True)
    c = translate("the weather is nice today")
    check("c9_dual_docked_residue_proposal_only",
          i.action == "unknown" and i.mandel == c.mandel
          and i.engine.get("residue") is True
          and i.engine.get("proposal_only") is True)

    # --- Translate as the dock's tool ----------------------------------
    d = adapt_determine("save")
    check("c9_tool_face",
          d is not None and d.intent_type == "SaveIntent"
          and adapt_determine("flibberty gibbet") is None)

    # --- canonical path untouched --------------------------------------
    i = translate("grow 3")
    check("c9_canonical_receipt_absent",
          i.engine is None and i.args.get("cycles") == 3
          and translate("the weather is nice today").action == "unknown")

    print(f"C9 dual-mode: {len(CHECKS)}/{len(CHECKS)} checks passed")


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"C9 SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
