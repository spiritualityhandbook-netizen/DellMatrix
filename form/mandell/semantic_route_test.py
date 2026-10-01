#!/usr/bin/env python3
"""DCC-II capability tests: Mandell -> Dell semantic routing.

Proves English reaches real Dell execution through the typed semantic
boundary — not decorative Mandell, not a duplicate dispatcher.
"""

from __future__ import annotations

import io
import os
import sys
from contextlib import redirect_stdout

RESULTS = []


def rec(name: str, ok: bool) -> None:
    RESULTS.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}", flush=True)


def _snapshot(p):
    """Capture mutable state for the read-mutation check."""
    return {
        "units": set(p.cube.session.plane.units.keys()),
        "gen": p.duo.generation,
        "ledger": len(p.duo.ledger),
        "history": len(p.history),
    }


def _domain_snapshot(p):
    """Domain state excluding the append-only history log.

    Dell arms call note_seed() which appends to history (expected logging).
    Domain mutation is units/duo generation/ledger.
    """
    s = _snapshot(p)
    return {k: v for k, v in s.items() if k != "history"}


def smoke() -> int:
    from form.open import open_program
    from form.mandell.translate import translate
    from form.mandell.seed import parse_seed
    from form.mandell.semantic_router import route_intent, CORRESPONDENCE
    from form import repl as repl_mod

    # --- 1. English produces expected Mandell semantics
    cases = {
        "save": ("save", "10[Keep]", 10),
        "grow": ("grow", "13[Loop]", 13),
        "discover": ("discover", "35[Discover]", 35),
        "discover nursery": ("discover", "35[Discover]", 35),
        # DCC-III: expanded vocabulary
        "measure": ("measure", "40[TokenCount]", 40),
        "test": ("test", "12[Test]", 12),
        "architect": ("architect", "11[Architect]", 11),
        "simulate": ("simulate", "31[Simulate]", 31),
        "checkpoint": ("checkpoint", "27[Checkpoint]", 27),
        "retry": ("retry", "42[Retry]", 42),
        "load": ("load", "28[Rollback]", 28),
    }
    for text, (exp_action, exp_frag, exp_dell) in cases.items():
        i = translate(text)
        s = parse_seed(i.mandel)
        rec(
            f"semantics_{text.replace(' ', '_')}",
            i.action == exp_action
            and exp_frag in i.mandel
            and s.ok
            and s.primary_dell() == exp_dell,
        )
    # DCC-III: argument-bearing intents
    i = translate("stamp my-milestone")
    rec(
        "semantics_stamp",
        i.action == "stamp" and "34[Stamp]" in i.mandel
        and i.args.get("mark") == "my-milestone"
        and parse_seed(i.mandel).primary_dell() == 34,
    )
    i = translate("cycle 3")
    rec(
        "semantics_cycle",
        i.action == "cycle" and "06[Cycle]" in i.mandel
        and i.args.get("count") == 3
        and parse_seed(i.mandel).primary_dell() == 6,
    )
    i = translate("form sphere")
    rec(
        "semantics_form",
        i.action == "form" and "15[Map]" in i.mandel
        and i.args.get("form") == "sphere"
        and parse_seed(i.mandel).primary_dell() == 15,
    )

    p = open_program("DCCIIRoute")

    # --- 2. Mandell semantic result reaches the routing boundary
    i = translate("save")
    r = route_intent(p, i, raw_line="save")
    rec(
        "reaches_boundary",
        r.mandell == "10[Keep]" and r.action == "save" and r.dell == 10,
    )

    # --- 3. Correct Dell/runtime operation is selected
    for text, exp_dell in [("save", 10), ("grow", 13), ("discover", 35),
                           ("measure", 40), ("test", 12), ("architect", 11),
                           ("simulate", 31), ("checkpoint", 27), ("retry", 42),
                           ("load", 28)]:
        r = route_intent(p, translate(text), raw_line=text)
        rec(
            f"selects_dell_{exp_dell}",
            r.routed and r.dell == exp_dell and r.ok,
        )
    # DCC-III: argument-bearing routes
    for text, exp_dell in [("stamp my-milestone", 34), ("cycle 2", 6), ("form sphere", 15)]:
        r = route_intent(p, translate(text), raw_line=text)
        rec(
            f"selects_dell_{exp_dell}_args",
            r.routed and r.dell == exp_dell and r.ok,
        )

    # --- 4. Wrong semantic operation cannot silently select another Dell
    i = translate("save")
    # Forge a mismatched composition: action says save, Mandell says Dell 13
    i.mandel = "13[Loop] :: forged"
    r = route_intent(p, i, raw_line="save")
    rec("mismatch_refused", (not r.routed) and r.dell == 13 and not r.ok)
    # Unknown action never routes
    i2 = translate("blarg nonsense xyz")
    r2 = route_intent(p, i2, raw_line="blarg nonsense xyz")
    rec("unknown_refused", (not r2.routed) and not r2.ok)

    # --- 5. Read operation does not mutate state unexpectedly
    before = _snapshot(p)
    r = route_intent(p, translate("discover"), raw_line="discover")
    after = _snapshot(p)
    rec(
        "read_no_mutation",
        r.routed and r.ok and before == after,
    )
    r = route_intent(p, translate("discover nursery"), raw_line="discover nursery")
    after2 = _snapshot(p)
    rec(
        "read_nursery_no_mutation",
        r.routed and r.ok and before == after2,
    )

    # --- 6. State-changing operation changes the expected authority
    # save writes the state file via program.save()
    r = route_intent(p, translate("save"), raw_line="save")
    from form.persist import _path as _state_path

    rec(
        "save_writes_state",
        r.routed and r.ok and os.path.exists(_state_path("DCCIIRoute")),
    )
    # grow runs program.grow_ideas (state authority), receipt shows it
    r = route_intent(p, translate("grow"), raw_line="grow")
    rec(
        "grow_runs_authority",
        r.routed and r.ok and "Ringed growth" in " ".join(r.messages),
    )

    # --- 7. Execution receipt reflects the actual route
    r = route_intent(p, translate("discover"), raw_line="discover")
    rec(
        "receipt_honest",
        r.input == "discover"
        and r.mandell == "35[Discover] :: inventory"
        and r.route == "discover/35 [Discover]"
        and r.seed == "35[Discover] :: inventory"
        and r.dell == 35
        and r.routed,
    )
    # A non-routed receipt must say so (no fake Dell)
    i3 = translate("save")
    i3.mandel = "13[Loop] :: forged"
    r3 = route_intent(p, i3, raw_line="save")
    rec(
        "receipt_honest_no_route",
        (not r3.routed) and r3.dell == 13 and "no verified correspondence" in r3.error,
    )

    # --- 8. Malformed/unsupported semantics fail safely (no exception, no mutation)
    before = _snapshot(p)

    class _Bad:
        action = "save"
        mandel = "not a seed [[["
        args = {}

    r = route_intent(p, _Bad(), raw_line="save")
    rec("malformed_fails_safe", (not r.routed) and not r.ok and "parse failed" in r.error)

    class _Empty:
        action = "save"
        mandel = ""
        args = {}

    r = route_intent(p, _Empty(), raw_line="save")
    rec("empty_fails_safe", (not r.routed) and not r.ok)
    after = _snapshot(p)
    rec("fail_safe_no_mutation", before == after)

    # --- 9. Persistence survives where applicable (save via router -> load)
    r = route_intent(p, translate("save"), raw_line="save")
    from form.persist_rest import load as persist_load

    p2 = persist_load("DCCIIRoute")
    rec(
        "persist_roundtrip",
        r.routed and p2 is not None and p2.owner == "DCCIIRoute",
    )

    # --- 10. DCC-I evolve/ledger capability remains intact
    buf = io.StringIO()
    with redirect_stdout(buf):
        repl_mod._execute_intent(p, translate("evolve test intent"), raw_line="evolve test intent")
    out = buf.getvalue()
    rec(
        "dcc_i_evolve_intact",
        "Evolved" in out and p.duo.generation >= 2,
    )
    buf = io.StringIO()
    with redirect_stdout(buf):
        repl_mod._execute_intent(p, translate("ledger"), raw_line="ledger")
    rec("dcc_i_ledger_intact", "Growth ledger" in buf.getvalue())

    # --- REPL-level: routed operations print honest receipts
    buf = io.StringIO()
    with redirect_stdout(buf):
        repl_mod._execute_intent(p, translate("discover"), raw_line="discover")
    out = buf.getvalue()
    rec(
        "repl_receipt",
        "INPUT: discover" in out
        and "MANDELL: 35[Discover] :: inventory" in out
        and "ROUTE: discover/35" in out
        and "DELL: 35" in out,
    )

    # Correspondence table is documented (evidence present, no bare name-match)
    # DCC-III: 13 correspondences (3 DCC-II + 10 DCC-III)
    expected_keys = {
        ("save", 10), ("grow", 13), ("discover", 35),
        ("measure", 40), ("test", 12), ("architect", 11), ("simulate", 31),
        ("checkpoint", 27), ("stamp", 34), ("cycle", 6), ("form", 15),
        ("load", 28), ("retry", 42), ("nurture", 37),
    }
    rec(
        "correspondence_documented",
        all(
            c.evidence and len(c.evidence) > 40
            for c in CORRESPONDENCE.values()
        )
        and set(CORRESPONDENCE) == expected_keys,
    )

    # --- DCC-III: argument preservation through Mandell
    r = route_intent(p, translate("stamp my-milestone"), raw_line="stamp my-milestone")
    rec(
        "args_stamp_preserved",
        r.routed and r.ok and "my-milestone" in r.seed and r.arguments.get("mark") == "my-milestone",
    )
    r = route_intent(p, translate("cycle 3"), raw_line="cycle 3")
    rec(
        "args_cycle_preserved",
        r.routed and r.ok and "06[Cycle] :: 3" in r.seed and r.arguments.get("count") == 3,
    )
    r = route_intent(p, translate("form sphere"), raw_line="form sphere")
    rec(
        "args_form_preserved",
        r.routed and r.ok and "15[Map] :: sphere" in r.seed and r.arguments.get("form") == "sphere",
    )

    # --- DCC-III: read operations do not mutate domain state
    # (history log may grow by note_seed; units/duo/ledger must not)
    for text in ["measure", "test", "architect", "simulate"]:
        before = _domain_snapshot(p)
        r = route_intent(p, translate(text), raw_line=text)
        after = _domain_snapshot(p)
        rec(f"read_{text}_no_mutation", r.routed and r.ok and before == after)

    # --- DCC-III: state-changing operations work
    r = route_intent(p, translate("stamp test-mark-iii"), raw_line="stamp test-mark-iii")
    rec("stamp_changes_state", r.routed and r.ok and getattr(p, "last_stamp", {}).get("mark") == "test-mark-iii")

    # --- DCC-III: checkpoint + rollback (control)
    r = route_intent(p, translate("checkpoint"), raw_line="checkpoint")
    rec("checkpoint_writes", r.routed and r.ok and "Checkpoint written" in " ".join(r.messages))
    r = route_intent(p, translate("load"), raw_line="load")
    rec(
        "rollback_restores",
        r.routed and r.ok and r.new_program is not None and "restored" in " ".join(r.messages).lower(),
    )

    # --- DCC-III: adversarial — correct action + wrong Dell refused
    i = translate("measure")
    i.mandel = "12[Test] :: forged"  # action=measure, Dell=12 (wrong)
    r = route_intent(p, i, raw_line="measure")
    rec("adv_wrong_dell_refused", (not r.routed) and r.dell == 12)

    # --- DCC-III: adversarial — correct Dell + wrong action refused
    i = translate("test")
    i.action = "measure"  # Dell=12, action=measure (wrong)
    i.mandel = "12[Test]"
    r = route_intent(p, i, raw_line="test")
    rec("adv_wrong_action_refused", (not r.routed) and r.dell == 12)

    # --- DCC-III: adversarial — unsupported Mandell refused
    i = translate("measure")
    i.mandel = "99[Unknown] :: foo"
    i.action = "measure"
    r = route_intent(p, i, raw_line="measure")
    rec("adv_unsupported_refused", (not r.routed) and "no verified correspondence" in r.error)

    # --- DCC-III: adversarial — malformed arguments fail safe
    i = translate("stamp my-milestone")
    i.args = {"mark": ""}  # empty mark
    r = route_intent(p, i, raw_line="stamp")
    # Should use safe default, not crash
    rec("adv_empty_arg_safe", r.routed and r.ok)

    # --- DCC-III: receipt v2 has semantic and arguments
    r = route_intent(p, translate("stamp v2-test"), raw_line="stamp v2-test")
    rec(
        "receipt_v2",
        r.semantic and "stamp" in r.semantic and isinstance(r.arguments, dict),
    )

    # Cleanup probe state
    import glob
    for f in (
        "form/state/program_DCCIIRoute.json",
        "form/state/program_DCCIIRoute.json.bak",
    ):
        try:
            os.remove(f)
        except OSError:
            pass
    for f in glob.glob("form/state/program_DCCIIRoute_cp_*.json"):
        try:
            os.remove(f)
        except OSError:
            pass

    passed = sum(1 for _, ok in RESULTS if ok)
    total = len(RESULTS)
    ok = passed == total
    print(f"semantic_route: {passed}/{total} {'GREEN' if ok else 'RED'}")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
