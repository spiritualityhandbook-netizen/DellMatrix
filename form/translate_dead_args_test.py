#!/usr/bin/env python3
"""72-06 Class D — dead Intent.args: zoom.ref / weather.condition.

Defect (confirmed by the 72-06 census, PR #308): translate() produces
args {"ref": ...} for zoom and {"condition": ...} for weather, but
the mandel carries NO operand ("15[Map] :: zoom",
"25[Pulse] :: weather") and NO code in form/ or gui/ reads either
key (exhaustive grep in the census ENUMERATION.md). The operand
survives at the REPL only because separate raw-line handlers
re-parse the user's text (repl.py zoom/weather handlers). A
programmatic consumer of Intent.args finds plausible-looking
values that do nothing — the channel lies; the user path does not.

Repair shape (SLEEP v2 queue item 2, Ace FIX-FIRST): make the
mandel carry the operand and retire the dead args.
  - form/mandell/phrases.py — zoom / weather phrase seeds carry
    the captured operand as the seed label
    ("15[Map] :: zoom {label}", "25[Pulse] :: weather {label}");
  - form/mandell/translate.py — the phrase branch no longer
    produces the dead "ref" / "condition" args.

Labels: translate()/parse_seed checks are INTEGRATION; the REPL
subprocess checks are REAL_USER_PATH (cross-process) and are
controls — the user path already works via the raw-line handlers
and must keep working identically after the repair.
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
    return "DA" + uuid.uuid4().hex[:10]


def smoke() -> bool:
    from form.mandell.translate import translate
    from form.mandell.seed import parse_seed

    # mandel carries the operand; dead args retired
    cases = [
        ("zoom beta", "15[Map] :: zoom beta", "ref"),
        ("zoom my idea", "15[Map] :: zoom my_idea", "ref"),
        ("focus on beta", "15[Map] :: zoom beta", "ref"),
        ("weather rain", "25[Pulse] :: weather rain", "condition"),
        ("weather storm", "25[Pulse] :: weather storm", "condition"),
        ("weather clear", "25[Pulse] :: weather clear", "condition"),
        ("weather fog", "25[Pulse] :: weather fog", "condition"),
        ("make it rain", "25[Pulse] :: weather rain", "condition"),
    ]
    for phrase, want_mandel, dead_key in cases:
        i = translate(phrase)
        tag = phrase.replace(" ", "_")
        check(f"mandel.{tag}", i.mandel == want_mandel,
              f"mandel={i.mandel!r}")
        check(f"deadarg.{tag}", dead_key not in (i.args or {}),
              f"args={i.args}")

    # the executed-seed parser sees the operand in the label
    for phrase, want_label_part in [("zoom beta", "beta"),
                                    ("weather rain", "rain")]:
        i = translate(phrase)
        r = parse_seed(i.mandel)
        label = r.atoms[0].label if r.ok and r.atoms else ""
        check(f"seedlabel.{phrase.replace(' ', '_')}",
              r.ok and want_label_part in label,
              f"label={label!r}")

    # neighbours unchanged: unzoom carries no operand and no args
    i = translate("unzoom")
    check("neighbour.unzoom", i.mandel == "15[Map] :: unzoom"
          and not i.args, f"mandel={i.mandel!r} args={i.args}")

    # REAL_USER_PATH controls: the bare REPL path already works via
    # its raw-line handlers and must keep working identically.
    cp = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", _owner()],
        input="create an idea called beta\nzoom beta\nweather rain\n",
        capture_output=True, text=True, timeout=120)
    out = cp.stdout + cp.stderr
    check("repl.zoom_beta", "Idea page · beta" in out, "")
    check("repl.weather_rain", "Weather → rain" in out, "")

    failed = [n for n, ok in RESULTS if not ok]
    print(f"translate_dead_args: {len(RESULTS) - len(failed)}/{len(RESULTS)}")
    return not failed


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
