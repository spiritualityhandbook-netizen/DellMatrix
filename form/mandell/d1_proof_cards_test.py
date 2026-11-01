#!/usr/bin/env python3
"""D1 circuit 2 — per-Dell proof cards over the full registry.

The Director's D1 denominator is the active Form registry:
100 entries, 15 typed signatures (the original 14 plus Dell
55 Set, registered by Director order step 4 / DAF-01 so its
typed operands are carried losslessly like Patch's) —
without implying the rest have defined contracts. This
suite regenerates every card
from live probes (dell_cards.build_all_cards) and pins the
survey distribution, so the accounting cannot drift silently:

- 100 cards, every dimension present (identity from the
  registry; typed signature present-or-absent; English-named
  present-or-absent; bare outcome executed-or-failed-with-
  reason). Dimensions are asserted separately — a card may
  not borrow strength from another dimension.
- The bare-invocation distribution observed at survey time:
  84 executed; exactly 16 failed, each with its recorded
  reason. (Bare invocation on an empty field in this
  runtime — operand/precondition failures are expected and
  are what the cards exist to record.)
- The committed DELL_PROOF_CARDS.md equals a fresh render.

Run: python3 -m form.mandell.d1_proof_cards_test
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.mandell.dell_cards import (  # noqa: E402
    build_all_cards, english_named_dells, render_cards_md)
from form.mandell.registry import DELLS  # noqa: E402
from form.mandell.signatures import get_signature  # noqa: E402

RESULTS = []

# Bare-invocation failures observed at survey (empty field):
# every one names its missing operand or precondition.
EXPECTED_BARE_FAILURES = {
    # Step 6 (B1/B4/B6): bare Decay now honestly refuses on the
    # enhance gate, bare Split refuses missing_source, and bare
    # Translate reports nothing_to_translate.
    16: "enhance OFF",
    21: "missing_source",
    22: "missing_source",
    45: "nothing_to_translate",
    28: "rollback_target_invalid",
    37: "add idea requires a label",
    44: "bridge_unavailable",
    47: "embed_unavailable",
    65: "bound_reached",
    78: "malformed_relation",
    79: "malformed_relation",
    85: "malformed_move",
    86: "delete_missing:empty",
    87: "replace_missing:",
    88: "patch_miss:",
    94: "catch_illegal",
    95: "commit_without_try",
    98: "alias_missing",
    99: "malformed_composition",
}


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))


def main():
    cards = build_all_cards(owner_prefix="D1CardT")
    by_dell = {c["dell"]: c for c in cards}

    _rec("one card per registry entry, dimensions complete",
         len(cards) == 100 and set(by_dell) == set(DELLS)
         and all(c["name"] and c["manor"] and c["namespace"]
                 and "typed_signature" in c and "english_named" in c
                 and c["bare"]["outcome"] in ("executed", "failed")
                 for c in cards))

    typed = {n for n in range(100) if get_signature(n) is not None}
    _rec("typed signatures: exactly the 15, cards agree",
         len(typed) == 15
         and {c["dell"] for c in cards
              if c["typed_signature"] is not None} == typed,
         f"typed={sorted(typed)}")

    named = english_named_dells()
    _rec("english-named: exactly the circuit-1 set of 29",
         len(named) == 29
         and {c["dell"] for c in cards if c["english_named"]} == named)

    failed = {c["dell"]: c["bare"]["error"]
              for c in cards if c["bare"]["outcome"] != "executed"}
    _rec("bare invocation: 81 executed, 19 named failures",
         len(failed) == 19
         and all(failed.get(n, "").startswith(prefix)
                 for n, prefix in EXPECTED_BARE_FAILURES.items())
         and set(failed) == set(EXPECTED_BARE_FAILURES),
         f"failed={ {k: failed[k][:24] for k in sorted(failed)} }")

    sig84 = by_dell[84]["typed_signature"] or {}
    _rec("card content: Dell 84 carries its signature contract",
         by_dell[84]["name"] == "Copy"
         and any(r["name"] == "source" for r in sig84.get("roles", []))
         and "copy_" in (sig84.get("output") or ""),
         str(sig84)[:160])

    doc_path = os.path.join(os.path.dirname(__file__),
                            "DELL_PROOF_CARDS.md")
    committed = open(doc_path, encoding="utf-8").read()
    _rec("committed DELL_PROOF_CARDS.md matches a fresh render",
         committed == render_cards_md(cards))

    ok = sum(1 for _, c, _ in RESULTS if c)
    for name, cond, detail in RESULTS:
        line = ("PASS " if cond else "FAIL ") + name
        if not cond and detail:
            line += " :: " + detail
        print(line)
    print(f"D1_PROOF_CARDS: {ok}/{len(RESULTS)}")
    return ok == len(RESULTS) and bool(RESULTS)


def smoke():
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
