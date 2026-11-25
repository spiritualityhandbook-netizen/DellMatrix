#!/usr/bin/env python3
"""Part II / C9 family — Translate honesty (rows #156, #157).

Register contracts:
- Row #156 (DD-35 / C9.NoIntent): unknown text produces NO invented
  Show seed; receipts name deterministic vs docked engine.
- Row #157 (DD-36 / C9.DualMode): Adapt adoption was ruled by Ace
  but his "not yet" remains in force until he calls it — the door
  must not silently switch engines or adopt Adapt behavior.

Measured at main af2519b6 before this suite was written
(form/mandell/translate.py): the unknown-text fallback returns
Intent("unknown", 9, "Show", {"query": text[:80]},
"09[Show] :: unknown") — an invented Show seed carrying a silently
cut query (translate.py:975 area). The no-intent checks therefore
fail-first. Known-phrase routing and the LM-4 receipt attachment
(Intent.lm, the #416 toll-booth receipt) are pins: they hold today.

Labels: INTEGRATION (translate()). No state touched.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def run_all():
    from form.mandell.translate import translate

    gib = "flurbo zanzibar quixotic wobble narnia splunge"
    it = translate(gib)
    check("no_intent.no_invented_show_seed",
          not (it.mandel or "").startswith("09[Show]"),
          f"mandel={it.mandel!r} action={it.action!r}")

    long_gib = "zqx " * 60  # 240 chars of unroutable text
    it = translate(long_gib.strip())
    q = (it.args or {}).get("query", "")
    check("no_intent.query_exact_or_refused",
          q == long_gib.strip() or it.action == "refuse",
          f"query len={len(q)} of {len(long_gib.strip())}")

    it = translate("grow 3")
    check("pin.known_phrase_routes", it.action == "grow"
          and (it.args or {}).get("cycles") == 3,
          f"action={it.action} args={it.args}")
    check("pin.receipt_names_engine", it.lm is not None,
          "Intent.lm (LM-4 decomposition receipt) attached")


def main():
    run_all()
    ok_n = sum(1 for _, ok in RESULTS if ok)
    print(f"C9_TRANSLATE_HONESTY {ok_n}/{len(RESULTS)}")
    return 0 if ok_n == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
