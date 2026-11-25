#!/usr/bin/env python3
"""GP-E01 / R24 — English translation must not rewrite operands.

Edition 1 spec (02_EXECUTION_CIRCUITS.md, GP-E01; design base
a8786f9c): preserve every admitted raw user operand byte-for-byte
through Intent and typed Seed; invalid operands reject explicitly
with original length and bound, without executing anything. Parsing
may normalize whitespace required by a declared grammar, but cannot
silently take a prefix, change an identity, lose quoted text or
change a hash.

Failing-first cases named by the spec, measured at main af2519b6
before this suite was written (form/mandell/translate.py):
(1) 100-character create label becomes 80 — add-idea branch slices
    the label [:80] (translate.py:538,542).
(2) 300-character supersession body becomes 240 — supersede branch
    slices words [:240] (translate.py:491).
(3) 80-character find phrase becomes 60 — find-idea branch slices
    the query [:60] (translate.py:480).
Further pre-cut sites in the same file, same failure class:
grow-context [:80] (:532), replace-with value [:60] (:712),
patch-to value [:60] (:721), stamp mark [:48] (:883), and the
unknown-query fallback text[:80] (:975).

Contract asserted per site: the operand arrives EXACTLY as typed,
or the Intent is an explicit refusal (action "unknown" carrying a
bound/length disclosure). A silent prefix cut fails. Short operands
inside every historical bound are regression pins: they pass today
and must keep passing after the repair.

Labels: INTEGRATION (translate() is the public English door's first
stage; downstream object-level parity is specified in the Part II
plan and lands with the code stage). No state is touched: translate
is pure.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _preserved_or_refused(intent, exact):
    """True when the operand survived byte-for-byte somewhere in the
    Intent's seed text / args, or the Intent is an explicit refusal
    that discloses a bound. A silent cut returns False."""
    hay = " ".join([str(intent.mandel or ""),
                    " ".join(str(v) for v in (intent.args or {}).values())])
    if exact in hay:
        return True
    if intent.action == "unknown":
        blob = str(intent.args or {})
        if "bound" in blob or "length" in blob or "refus" in blob:
            return True
    return False


def run_all():
    from form.mandell.translate import translate

    label100 = "L" * 100
    it = translate(f"add idea {label100}")
    check("spec(1) add-idea label 100 exact-or-refused",
          _preserved_or_refused(it, label100),
          f"got label len={len((it.args or {}).get('label', ''))}")

    body300 = "B" * 300
    it = translate(f"supersede idea K1 with {body300}")
    check("spec(2) supersede body 300 exact-or-refused",
          _preserved_or_refused(it, body300),
          f"mandel carries {it.mandel.count('B')} of 300 body chars")

    phrase80 = "P" * 80
    it = translate(f"find idea {phrase80}")
    check("spec(3) find-idea phrase 80 exact-or-refused",
          _preserved_or_refused(it, phrase80),
          f"mandel carries {it.mandel.count('P')} of 80 phrase chars")

    ctx120 = "C" * 120
    it = translate(f"grow using knowledge about {ctx120}")
    check("grow-context 120 exact-or-refused",
          _preserved_or_refused(it, ctx120),
          f"mandel carries {it.mandel.count('C')} of 120 context chars")

    new100 = "N" * 100
    it = translate(f"replace alpha with {new100}")
    check("replace-with value 100 exact-or-refused",
          _preserved_or_refused(it, new100),
          f"got new len={len((it.args or {}).get('new', ''))}")

    val100 = "V" * 100
    it = translate(f"patch alpha to {val100}")
    check("patch-to value 100 exact-or-refused",
          _preserved_or_refused(it, val100),
          f"got value len={len((it.args or {}).get('value', ''))}")

    mark80 = "M" * 80
    it = translate(f"stamp {mark80}")
    check("stamp mark 80 exact-or-refused",
          _preserved_or_refused(it, mark80),
          f"got mark len={len((it.args or {}).get('mark', ''))}")

    uni100 = "é" * 100
    it = translate(f"add idea {uni100}")
    check("add-idea multibyte label 100 exact-or-refused",
          _preserved_or_refused(it, uni100),
          f"got label len={len((it.args or {}).get('label', ''))}")

    # Regression pins: operands inside every historical bound pass
    # exactly today and must keep passing after the repair.
    it = translate("add idea roses are red")
    check("pin: short add-idea label exact",
          (it.args or {}).get("label") == "roses are red")
    it = translate("find idea roses")
    check("pin: short find-idea phrase exact", "roses" in it.mandel)
    it = translate("supersede idea K1 with fresh words here")
    check("pin: short supersede body exact",
          "fresh words here" in it.mandel)


def main():
    run_all()
    ok_n = sum(1 for _, ok in RESULTS if ok)
    print(f"R24_OPERAND_INTEGRITY {ok_n}/{len(RESULTS)}")
    return 0 if ok_n == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
