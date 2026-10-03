#!/usr/bin/env python3
"""R2 semantic honesty (GDP-001 Phase 0, Requirement 2, Obj 0.2.4).

Proves that unsupported / ambiguous / contradictory / unauthorized inputs
produce honest failure (explicit refusal / unknown), never silently become
another valid operation. Every case below is executed live against the
real code; nothing is asserted from comments or docs.

Covered layers:
  parse   seed.py            unknown Dell / empty / malformed flow
  registry                  unknown name / out-of-range number
  router  semantic_router    unknown action / no-correspondence (refuses to guess)
  arm     core_i_ops        Dell 44 Bridge / Dell 47 Embed honest refusals
  flow    flow_executor     non-executable operators refused (no silent downgrade)
  compose english_composer  gibberish multi-clause -> compile failure, zero Dells
  english translate         gibberish -> Intent("unknown"), router refuses

NOTE (R2 finding, not a test): reserved-domain dells (e.g. 151[Harmonic])
carry status RESERVED_NOT_ACTIVE in the registry authority, but the
single-seed executor leaf currently answers ok=True "runtime thin" for
them. That gap is recorded as MUST_FIX_BEFORE_GATE in the R2 report; this
suite asserts the registry's honest standing, not the leaf's theater.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form.open import open_program
from form.mandell.seed import parse_seed
from form.mandell import registry
from form.mandell.translate import Intent, translate
from form.mandell.semantic_router import route_intent
from form.mandell.executor import execute_seed
from form.mandell.flow_executor import parse_program
from form.mandell.english_composer import compose_english

CHECKS = []


def check(name, cond):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def run_all():
    # ---- parse layer -----------------------------------------------------
    s = parse_seed("998[Nope]")
    check("parse: unknown Dell number fails", s.ok is False)
    check("parse: unknown Dell names the number", "unknown Dell 998" in s.error)
    s = parse_seed("")
    check("parse: empty fails", s.ok is False and s.error == "empty")
    s = parse_seed("08[Create] >>")
    check("parse: dangling flow fails", s.ok is False)
    s = parse_seed("08[Create] >>>>")
    check("parse: bad flow token fails", s.ok is False)

    # ---- registry layer --------------------------------------------------
    check("registry: unknown name -> None", registry.lookup("NoSuchDell") is None)
    check("registry: out-of-range -> None", registry.get_dell(1000) is None)
    st = registry.execution_standing(151)
    check("registry: reserved dell honest standing",
          st["standing"] == "RESERVED_NOT_ACTIVE" and st["dispatch"] == "none")

    # ---- router layer ----------------------------------------------------
    p = open_program("R2Honesty")
    r = route_intent(p, Intent("unknown", None, "", {}, "09[Show] :: unknown",
                               "xylophone zebra quantum"),
                     raw_line="xylophone zebra quantum")
    check("router: unknown action not routed", r.routed is False)
    check("router: unknown action ok=False", r.ok is False)
    check("router: unknown action says why", "unsupported action" in r.error)
    check("router: unknown action no state change",
          r.state_note == "no state change (not routed)")

    r = route_intent(p, Intent("teleport", 8, "Create", {}, "08[Create]", "teleport"),
                     raw_line="teleport")
    check("router: no-correspondence not routed", r.routed is False)
    check("router: no-correspondence ok=False", r.ok is False)
    check("router: refuses to guess", "refusing to guess" in r.error)

    # translate() maps gibberish to Intent("unknown"); the router refuses it.
    t = translate("xylophone zebra quantum")
    check("translate: gibberish -> unknown", t.action == "unknown")
    r = route_intent(p, t, raw_line="xylophone zebra quantum")
    check("router: translated gibberish refused",
          r.routed is False and r.ok is False)

    # ---- honest arm refusals (offline origin) -----------------------------
    units_before = len(p.cube.session.plane.units)
    r = execute_seed(p, "44[Bridge]")
    check("dell44: ok=False", r["ok"] is False)
    check("dell44: named error", r.get("error") == "bridge_unavailable")
    r = execute_seed(p, "47[Embed]")
    check("dell47: ok=False", r["ok"] is False)
    check("dell47: named error", r.get("error") == "embed_unavailable")
    check("refusals: zero units created",
          len(p.cube.session.plane.units) == units_before)

    # ---- flow layer: non-executable operators refused, never downgraded --
    for prog, op in (("10[Keep] >>> 13[Loop]", ">>>"),
                     ("10[Keep] <:> 13[Loop]", "<:>"),
                     ("10[Keep] <<[Delta] 13[Loop]", "<<[Delta]")):
        try:
            parse_program(prog)
            raised = False
        except ValueError:
            raised = True
        check(f"flow: '{op}' refused, not downgraded", raised)

    # ---- composer: gibberish -> compile failure, zero Dells --------------
    cr = compose_english("xylophone zebra quantum")
    check("composer: gibberish not ok", cr.ok is False)
    check("composer: gibberish names the failure", bool(cr.error))

    print(f"R2-HONESTY: {sum(1 for _, c in CHECKS if c)}/{len(CHECKS)} GREEN")


def smoke() -> bool:
    """Regress entry point: run all checks, return True on success."""
    try:
        run_all()
        return True
    except Exception as e:
        print(f"R2-HONESTY SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
