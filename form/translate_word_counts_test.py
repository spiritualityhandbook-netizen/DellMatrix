#!/usr/bin/env python3
"""72-06 Class E — spelled-out counts silently defaulted to 1.

Defect (confirmed by the 72-06 census, PR #308; proven at the bare
REPL in the supplement transcripts): translate()'s count handling
was digit-only at every layer — the phrase patterns captured
(\\d+) only, english_brain's grow paraphrase/synonym rewrites
extracted (\\d+) only, and translate's args builders treated a
non-digit label as "no count". So "cycle three times" executed
06[Cycle] :: 1 and "grow three" executed 13[Loop] :: 1, both with
ok=True — the SM-11 dropped-count family in the word form the
digit certification never covered.

Repair (Ace FIX-FIRST, 2026-11-05): the count positions accept
the same number words the composite path already honored
(english_composer._WORD_NUM: once/twice/thrice, one..five):
  - form/mandell/phrases.py — grow / evolve-ideas / walk /
    english-expand patterns capture digits or number words;
  - form/mandell/english_brain.py — the four grow paraphrase
    rules and the grow synonym branch carry the word through
    instead of discarding it;
  - form/mandell/translate.py — _count_value() converts a digit
    or number word at exactly the count sites (phrase grow/walk/
    english_expand, fallback cycle). Conversion is positional
    only: user labels containing number words are never rewritten
    (pinned by the "add idea one star" case below).

Labels: translate()/route_intent checks are INTEGRATION; the REPL
subprocess checks are REAL_USER_PATH (cross-process).
"""
from __future__ import annotations

import subprocess
import sys
import uuid

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _owner():
    return "WC" + uuid.uuid4().hex[:10]


def smoke() -> bool:
    from form.open import Program
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent

    # translate level: word counts land in Intent.args
    word_cases = [
        ("grow three", "cycles", 3),
        ("grow ideas two", "cycles", 2),
        ("evolve ideas two", "cycles", 2),
        ("please grow three", "cycles", 3),
        ("let them grow four", "cycles", 4),
        ("advance the nursery five", "cycles", 5),
        ("walk three", "steps", 3),
        ("walk forward five", "steps", 5),
        ("english expand three", "cycles", 3),
        ("cycle three times", "count", 3),
        ("cycle five times", "count", 5),
    ]
    for phrase, key, want in word_cases:
        i = translate(phrase)
        check(f"word.{phrase.replace(' ', '_')}", i.args.get(key) == want,
              f"args={i.args}")

    # digit controls unchanged
    for phrase, key, want in [("grow 3", "cycles", 3),
                              ("cycle 3 times", "count", 3),
                              ("walk 2", "steps", 2)]:
        i = translate(phrase)
        check(f"digit.{phrase.replace(' ', '_')}", i.args.get(key) == want,
              f"args={i.args}")

    # no-count defaults unchanged
    check("default.grow_ideas", translate("grow ideas").args.get("cycles") == 1, "")

    # anti-corruption: number words inside user labels survive verbatim
    i = translate("add idea one star")
    check("label.one_star_preserved", i.args.get("label") == "one star",
          f"args={i.args}")

    # route level: the executed seed carries the word count
    for phrase, seed in [("cycle three times", "06[Cycle] :: 3"),
                         ("grow three", "13[Loop] :: 3")]:
        p = Program(owner=_owner())
        r = route_intent(p, translate(phrase), phrase)
        check(f"route.{phrase.replace(' ', '_')}", r.ok and r.seed == seed,
              f"seed={r.seed!r} ok={r.ok}")

    # REAL_USER_PATH: the bare REPL process executes the word count
    for phrase, needle in [("cycle three times", "Cycle x3"),
                           ("grow three", "Loop: requested 3, executed 3"),
                           ("cycle 3 times", "Cycle x3")]:
        cp = subprocess.run(
            [sys.executable, "-m", "form.repl", "--owner", _owner()],
            input=phrase + "\n", capture_output=True, text=True, timeout=120)
        out = cp.stdout + cp.stderr
        check(f"repl.{phrase.replace(' ', '_')}", needle in out and "RESULT: ok=True" in out,
              needle)

    failed = [n for n, ok in RESULTS if not ok]
    print(f"translate_word_counts: {len(RESULTS) - len(failed)}/{len(RESULTS)}")
    return not failed


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
