#!/usr/bin/env python3
"""72-06 probe: English Intent.args end-to-end census.

For each case: translate(phrase) -> record Intent.args + mandel ->
route_intent on an isolated Program -> record the executed seed.
Checks pin the census classification:

  A  args consumed by the router's correspondence build_seed
     (grow.cycles, stamp.mark, cycle.count, form.form)
  B  operand mirrored in the mandel text; executed seed carries it
     (router never reads the args dict for these)
  C  REPL-only actions: route_intent honestly refuses (routed=False);
     the REPL direct handlers are the args consumers (static evidence
     in the report: form/repl.py arg reads)
  D  dead args: produced, consumed nowhere, absent from the mandel
     (zoom.ref, weather.condition) — operand survives at the REPL
     only via raw-line re-parse
  E  producer-side silent default (SM-11 family, word-form):
     spelled-out counts default to 1 and execute ok=True

Usage: python3 q06_probe.py <run-tag>
Exit 0 iff all checks pass; exit 2 on setup failure.
"""
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from form.open import Program
from form.mandell.translate import translate
from form.mandell.semantic_router import route_intent

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def run(tag, idx, phrase):
    intent = translate(phrase)
    p = Program(owner=f"Q06{tag}{idx}")
    r = route_intent(p, intent, phrase)
    return intent, r


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "r1"

    # ---- Class A: router consumes args ----
    i, r = run(tag, 1, "grow 3")
    check("A1.grow_cycles_used", i.args.get("cycles") == 3 and r.seed == "13[Loop] :: 3",
          f"args={i.args} seed={r.seed!r}")
    i, r = run(tag, 2, "stamp victory")
    check("A2.stamp_mark_used", i.args.get("mark") == "victory" and "victory" in (r.seed or ""),
          f"args={i.args} seed={r.seed!r}")
    i, r = run(tag, 3, "cycle 3")
    check("A3.cycle_count_used", i.args.get("count") == 3 and r.seed == "06[Cycle] :: 3",
          f"args={i.args} seed={r.seed!r}")
    i, r = run(tag, 4, "form sphere")
    check("A4.form_used", i.args.get("form") == "sphere" and r.seed == "15[Map] :: sphere",
          f"args={i.args} seed={r.seed!r}")
    i, r = run(tag, 5, "cycle 9")
    check("A5.cycle_clamped_at_producer", i.args.get("count") == 5 and r.seed == "06[Cycle] :: 5",
          "translate clamps 9 -> 5 in args itself (Dell 6 cap); no silent loss, a stated transform")

    # ---- Class B: operand mirrored in mandel, carried to execution ----
    b_cases = [
        (6, "move alpha to beta", "source", "alpha"),
        (7, "copy alpha", "source", "alpha"),
        (11, "get mykey", "key", "mykey"),
        (12, "select red", "predicate", "red"),
        (13, "search for red", "pattern", "red"),
        (14, "add idea bright star", "label", "bright star"),
    ]
    for idx, phrase, key, val in b_cases:
        i, r = run(tag, idx, phrase)
        check(f"B{idx}.mirrored_{i.action}",
              i.args.get(key) == val and val in (i.mandel or "") and val in (r.seed or ""),
              f"args[{key}]={val!r} travels in mandel and executed seed; router reads the mandel, not args")

    # ---- Class B-gated: destructive ops refused explicitly at the router ----
    for idx, phrase, key, val in [(8, "delete alpha", "key", "alpha"),
                                  (9, "replace old with new", "new", "new"),
                                  (10, "patch color to blue", "value", "blue")]:
        i, r = run(tag, idx, phrase)
        check(f"BG{idx}.gated_{i.action}",
              i.args.get(key) == val and val in (i.mandel or "")
              and r.routed is False
              and str(r.error).startswith("blocked_with_reason: destructive store mutation"),
              "operand intact in args+mandel; route refuses LOUDLY by design "
              "(operand-confirmation gate) — not a silent loss")

    # ---- Class C: REPL-only (router honestly refuses) ----
    for idx, phrase, key in [(15, "walk forward 3", "steps"),
                             (16, "turn left", "direction")]:
        i, r = run(tag, idx, phrase)
        check(f"C{idx}.repl_only_{i.action}",
              key in i.args and r.routed is False,
              f"args={i.args}; route_intent routed=False (explicit refusal); "
              "the REPL direct handler consumes args (static: form/repl.py)")

    # ---- Class D: dead args ----
    for idx, phrase, key, val in [(17, "zoom tokyo", "ref", "tokyo"),
                                  (18, "weather rain", "condition", "rain")]:
        i, r = run(tag, idx, phrase)
        check(f"D{idx}.dead_arg_{i.action}",
              i.args.get(key) == val and val not in (i.mandel or "") and r.routed is False,
              f"args[{key}]={val!r} produced, absent from mandel {i.mandel!r}, "
              "no consumer in form/ or gui/ (census grep); REPL serves the operand from raw line text")

    # ---- Class E: spelled-out counts silently default (SM-11 word-form) ----
    i, r = run(tag, 19, "cycle three times")
    check("E19.cycle_word_count_defaults",
          i.args.get("count") == 1 and r.ok and r.seed == "06[Cycle] :: 1",
          "operand 'three' present in English, default 1 executed with ok=True — "
          "the digit class is certified (SM-11); the word-form class was never covered")
    i, r = run(tag, 20, "grow three")
    check("E20.grow_word_count_defaults",
          i.args.get("cycles") == 1 and r.ok and r.seed == "13[Loop] :: 1",
          "same silent default on the grow path")

    # ---- Control: digit form of the same phrases is honored ----
    i, r = run(tag, 21, "cycle 3 times")
    check("CTL.digit_form_honored", i.args.get("count") == 3 and r.seed == "06[Cycle] :: 3",
          "isolates the gap to number WORDS, not the routing")

    failed = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed"
          + (f"; FAILED: {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
