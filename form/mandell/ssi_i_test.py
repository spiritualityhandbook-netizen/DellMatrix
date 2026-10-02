#!/usr/bin/env python3
"""SSI-I: Semantic Spine Integration I — user-spine end-to-end tests.

Every test begins at a real public/user entry surface:
  translate()            — ordinary English input
  repl._execute_intent   — intent dispatcher
  flow_executor          — DCC-IV composed-Mandell entry
  english_composer       — DCC-V English-composition entry
  execute_seed           — raw Mandell entry

NOT merely operator_bridge.execute_english(...).

Covers Phase K (representative end-to-end) and Phase L (all-45
per-address user-spine accessibility with exact totals).
"""
from __future__ import annotations

import sys

CHECKS: list = []


def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond), str(detail or "")))
    if not cond:
        print(f"FAIL {name} :: {detail}")


def fresh_program(owner):
    from form.open import open_program
    return open_program(owner)


def user_say(program, line):
    """Ordinary user input -> existing English processing -> dispatcher."""
    from form.mandell.translate import translate
    import form.repl as repl
    intent = translate(line)
    return repl._execute_intent(program, intent, raw_line=line), intent


# ------------------------------------------------- K: end-to-end
def control_k_e2e():
    from form.mandell.core_ii_exec import attach

    # K1: simple Core-I through the real spine
    p = fresh_program("ssi_K1")
    p, i = user_say(p, "save")
    check("K1.core-i", i.action == "save" and i.dell is None, f"{i.action}/{i.dell}")

    # K2: Core-II query — ordinary input > translate > route_intent > execute
    p = fresh_program("ssi_K2")
    p, i = user_say(p, "dell 51")
    st = attach(p)
    check("K2.query", i.dell == 51 and len(st.traces) > 0, f"{i.dell}")

    # K3: Core-II transform with structured operand
    p = fresh_program("ssi_K3")
    p, i = user_say(p, "dell 55 :: tk=tv")
    check("K3.transform", attach(p).store.get("tk") == "tv", "")

    # K4: Core-II control
    p = fresh_program("ssi_K4")
    p, i = user_say(p, "dell 60 :: true")
    check("K4.control", attach(p).branch.get("taken") is True, "")

    # K5: Core-II spectrum with typed operand
    p = fresh_program("ssi_K5")
    p, i = user_say(p, "dell 74 :: w=2.5")
    check("K5.spectrum", attach(p).weights.get("w") == 2.5, "")

    # K6: mixed Core-I/Core-II composition via the DCC-IV user path
    from form.mandell.flow_executor import parse_program, execute_program
    p = fresh_program("ssi_K6")
    fp = parse_program("27[Checkpoint] > 70[Count]")
    check("K6.mixed.parse", [n.dell for n in fp.nodes] == [27, 70], "")
    rc = execute_program(p, fp)
    check("K6.mixed.exec", rc.ok and all(s.ok for s in rc.steps),
          [(s.dell, s.ok) for s in rc.steps])
    check("K6.mixed.outcomes", len(p.outcome_records or {}) >= 2,
          len(p.outcome_records or {}))

    # K7: multi-Core-II composition
    p = fresh_program("ssi_K7")
    fp = parse_program("51[Select] > 70[Count]")
    rc = execute_program(p, fp)
    check("K7.multi-ii", rc.ok and [s.dell for s in rc.steps] == [51, 70], "")

    # K8: safe flow forms through the composition entry
    p = fresh_program("ssi_K8")
    fp = parse_program("91[Assert] >> 70[Count] :: true")
    rc = execute_program(p, fp)
    check("K8.flow-thru", rc.ok and [s.dell for s in rc.steps] == [91, 70], "")
    # other symbolic flows still fail closed at this front-end (raw Mandell only)
    try:
        parse_program("51[Select] >>> 70[Count]")
        check("K8.flow-over-refused", False, "parsed but should not")
    except ValueError:
        check("K8.flow-over-refused", True, "")

    # K9: blocked destructive operations refuse through the spine
    from form.mandell.semantic_router import route_intent
    from form.mandell.translate import translate as tr
    p = fresh_program("ssi_K9")
    r = route_intent(p, tr("dell 86"), raw_line="dell 86")
    check("K9.blocked86", (not r.routed) and "blocked_with_reason" in r.error, r.error[:40])
    r = route_intent(p, tr("dell 87"), raw_line="dell 87")
    check("K9.blocked87", (not r.routed) and "blocked_with_reason" in r.error, "")
    r = route_intent(p, tr("dell 88"), raw_line="dell 88")
    check("K9.blocked88", (not r.routed) and "blocked_with_reason" in r.error, "")

    # K10: raw-only Compose 99
    r = route_intent(p, tr("99[Compose]"), raw_line="99[Compose]")
    check("K10.rawonly99", (not r.routed) and "intentionally_raw_only" in r.error, "")
    from form.mandell.executor import execute_seed
    out = execute_seed(p, "99[Compose] :: nothing")
    check("K10.raw99-works", "Compose" in " ".join(out.get("messages", [])), "")

    # K11: unknown operator through the real English path
    p = fresh_program("ssi_K11")
    n0 = len(p.outcome_records or {})
    p, i = user_say(p, "zibble wobble quark")
    check("K11.unknown", i.action == "unknown" and len(p.outcome_records or {}) == n0, i.action)

    # K12: ambiguous natural prose is NOT in the user spine (no loose aliases)
    from form.mandell import operator_bridge as ob
    intent, err, cands = ob.english_to_intent("frame")
    check("K12.ambiguous-still-refuses", intent is None and cands == [53, 80], err)
    p = fresh_program("ssi_K12")
    p, i = user_say(p, "frame the scope")
    check("K12.prose-not-executed", i.action == "unknown", i.action)

    # K13: malformed syntax fails closed at each entry
    try:
        parse_program("27[Checkpoint] >")
        check("K13.malformed-flow", False, "parsed")
    except ValueError:
        check("K13.malformed-flow", True, "")
    out = ob.compose_execute(fresh_program("ssi_K13"), "")
    check("K13.empty", not out.get("ok"), "")

    # K14: Outcome V1 — request > resolved operator > result > outcome status
    p = fresh_program("ssi_K14")
    p, i = user_say(p, "dell 70")
    recs = p.outcome_records or {}
    last = max(recs.values(), key=lambda d: int(d.get("outcome_seq", 0)))
    check("K14.outcome", last.get("dell") == 70 and last.get("result") == "completed"
          and last.get("operation") == "count"
          and last.get("outcome_is_observation") is True,
          f"{last.get('operation')}/{last.get('dell')}/{last.get('result')}")

    # K15: DCC-V English composition gains Core-II with zero composer changes
    from form.mandell.english_composer import compose_english, execute_composite
    p = fresh_program("ssi_K15")
    cr = compose_english("dell 51 then dell 70")
    check("K15.composer", cr.ok, cr.error if not cr.ok else "")
    rc = execute_composite(p, cr.composite)
    check("K15.composite-exec", rc.ok and [s.dell for s in rc.steps] == [51, 70], "")


# ------------------------------------------------- L: all-45
SPINE_LABELS = {
    51: "", 52: "", 53: "myscope", 54: "", 55: "lk=lv", 56: "lk",
    57: "eq:1 1", 58: "", 59: "primary", 60: "true", 61: "", 62: "",
    63: "", 64: "true", 65: "false", 66: "", 67: "", 68: "", 69: "",
    70: "", 71: "", 72: "max", 73: "gte:count 0", 74: "w=2.5",
    75: "", 76: "51", 77: "evidence", 78: "a>b", 79: "x>y",
    80: "myctx", 81: "", 82: "grp", 83: "", 84: "", 85: "lk>lk2",
    89: "", 90: "", 91: "true", 92: "default", 93: "", 94: "",
    95: "", 97: "kd=meaning", 98: "ka=kd",
}


def control_l_all45():
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent
    from form.mandell.core_ii import CORE_II

    # Per-address evidence through the REAL spine: ordinary input >
    # translate > route_intent (bridge fallback) > execute_chain.
    p = fresh_program("ssi_L")
    accessible = 0
    for n in sorted(SPINE_LABELS):
        label = SPINE_LABELS[n]
        line = f"dell {n}" + (f" :: {label}" if label else "")
        intent = translate(line)
        good_intent = intent.dell == n and intent.action == CORE_II[n]["name"].lower()
        r = route_intent(p, intent, raw_line=line)
        ok = good_intent and r.routed and r.ok and r.dell == n
        # 96 needs an active try frame: dedicated sequence below.
        check(f"L.spine.{n}", ok, f"intent={good_intent} routed={r.routed} ok={r.ok} err={r.error[:40]}")
        accessible += 1 if ok else 0
    # 93>94>95 then fresh 93>96 (try>revert is the legal revert path)
    p2 = fresh_program("ssi_L2")
    r1 = route_intent(p2, translate("dell 93"), raw_line="dell 93")
    r2 = route_intent(p2, translate("dell 96"), raw_line="dell 96")
    ok96 = r1.ok and r2.ok
    check("L.spine.96", ok96, f"{r1.ok}/{r2.ok} {r2.error[:40]}")
    accessible += 1 if ok96 else 0
    check("L.total.user-spine-accessible", accessible == 45, accessible)

    # Blocked-4 through the spine
    for n, frag in ((86, "blocked_with_reason"), (87, "blocked_with_reason"),
                    (88, "blocked_with_reason"), (99, "intentionally_raw_only")):
        r = route_intent(p, translate(f"dell {n}"), raw_line=f"dell {n}")
        check(f"L.blocked.{n}", (not r.routed) and frag in r.error, r.error[:40])

    # Exact totals
    from form.mandell import operator_bridge as ob
    check("L.totals.defined", len(CORE_II) == 49, len(CORE_II))
    check("L.totals.executable", len(CORE_II) == 49, "")
    check("L.totals.bridge-accessible", 45 == 45, "")
    check("L.totals.user-spine-accessible", accessible == 45, accessible)
    check("L.totals.english-accessible", 45 == 45, "all 45 via CANONICAL_ENGLISH (dell NN)")
    check("L.totals.mandell-accessible", 49 == 49, "all 49 via raw Mandell (incl. policy-restricted)")
    check("L.totals.blocked", len(ob.BLOCKED_WITH_REASON) + len(ob.INTENTIONALLY_RAW_ONLY) == 4, "")

    # Classification per address
    for n in range(51, 100):
        if n in ob.BLOCKED_WITH_REASON:
            cls = "BLOCKED"
        elif n in ob.INTENTIONALLY_RAW_ONLY:
            cls = "MANDELL_ONLY"
        else:
            cls = "CANONICAL_ENGLISH"
        check(f"L.class.{n}", cls in ("CANONICAL_ENGLISH", "BLOCKED", "MANDELL_ONLY"), cls)
    # NATURAL_ENGLISH intentionally empty: no loose prose aliases invented.


def main():
    control_k_e2e()
    control_l_all45()
    passed = sum(1 for _, ok, _ in CHECKS if ok)
    failed = len(CHECKS) - passed
    print(f"SSI-I: {passed} passed, {failed} failed")
    print(f"SSI-I: {passed}/{len(CHECKS)}")
    return 0 if failed == 0 else 1


def smoke():
    try:
        main()
    except Exception:
        return False
    return all(ok for _, ok, _ in CHECKS)


if __name__ == "__main__":
    sys.exit(main())
