#!/usr/bin/env python3
"""72-06 CURRENT-CONTRACT probe (added 2026-11-20, Director 7040506653).

The historical q06_probe.py (2026-11-05 census) is preserved byte-for-byte
and is NO LONGER executed against the live product: five of its checks pin
behavior the product has since deliberately changed. This probe pins the
CURRENT contract for exactly those five changed claims, at the same
PUBLIC_ENTRY_PATH the census used (translate -> route_intent on an
isolated Program), plus the unchanged digit controls.

  E19/E20  word-form counts are now HONORED (was: silent default to 1)
  A5       producer no longer clamps 9 -> 5 silently; count 9 is
           preserved upstream (execution enforces and REPORTS its own
           bound — proven at the REPL by q06_current_repl_probe.py)
  D17/D18  dead-arg production is GONE: zoom/weather produce NO args
           and route_intent refuses explicitly (ok=False, no seed)

Refused routes must not mutate owner state (checked here by idea-count
snapshot before/after). Usage: python3 q06_current_probe.py <run-tag>
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
    p = Program(owner=f"Q06CUR{tag}{idx}")
    before = len(getattr(p, "ideas", []) or [])
    r = route_intent(p, intent, phrase)
    after = len(getattr(p, "ideas", []) or [])
    return intent, r, before, after


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "r1"

    # ---- E19/E20: word-form counts honored (ALREADY_FIXED) ----
    i, r, _, _ = run(tag, 19, "cycle three times")
    check("E19.word_count_honored",
          i.args.get("count") == 3 and r.ok and r.seed == "06[Cycle] :: 3",
          f"args={i.args} seed={r.seed!r} (2026-11-05 census: count defaulted to 1)")
    i, r, _, _ = run(tag, 20, "grow three")
    check("E20.word_count_honored",
          i.args.get("cycles") == 3 and r.ok and r.seed == "13[Loop] :: 3",
          f"args={i.args} seed={r.seed!r} (2026-11-05 census: cycles defaulted to 1)")

    # ---- A5: no silent producer clamp (INTENTIONAL_GUARD) ----
    i, r, _, _ = run(tag, 5, "cycle 9")
    check("A5.count9_preserved_upstream",
          i.args.get("count") == 9 and r.seed == "06[Cycle] :: 9",
          f"args={i.args} seed={r.seed!r} (census: translate clamped 9 -> 5 in args; "
          "execution-side bound is enforced and reported at the REPL, see repl probe G9)")

    # ---- D17/D18: dead-arg production gone, explicit refusal, no mutation ----
    for idx, phrase in [(17, "zoom tokyo"), (18, "weather rain")]:
        i, r, before, after = run(tag, idx, phrase)
        check(f"D{idx}.no_dead_arg_explicit_refusal",
              i.args == {} and r.routed is False and r.ok is False
              and not r.seed and "refusing to guess" in str(r.error)
              and before == after,
              f"args={i.args} error={r.error!r} ideas {before}->{after} "
              "(census: dead arg produced, consumed nowhere)")

    # ---- Controls: digit forms unchanged ----
    i, r, _, _ = run(tag, 21, "cycle 3 times")
    check("CTL.digit_form_honored", i.args.get("count") == 3 and r.seed == "06[Cycle] :: 3",
          f"args={i.args} seed={r.seed!r}")
    i, r, _, _ = run(tag, 22, "grow 3")
    check("CTL.grow_digit_honored", i.args.get("cycles") == 3 and r.seed == "13[Loop] :: 3",
          f"args={i.args} seed={r.seed!r}")

    failed = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed"
          + (f"; FAILED: {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
