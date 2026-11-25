#!/usr/bin/env python3
"""DCC-I capability tests — DuoBeta living growth vertical slice.

Proves the real end-to-end path, not implementation details:

  INPUT > MANDELL INTERPRETATION > OPERATION > EXECUTION >
  STATE CHANGE > PERSIST > RESTORE > OBSERVABLE RESULT

  1. user operation enters the authoritative runtime (REPL _execute_intent)
  2. Mandell participates (translate() yields Intents with mandel strings)
  3. the operation executes (DuoBeta.evolve via Program.evolve)
  4. expected result is produced (generation+1, ledger entry)
  5. state mutation occurs (duo.generation, duo.ledger)
  6. persistence/restore works (ledger saved + restored faithfully)
  7. second execution does not corrupt authority (evolve after load)
  8. malformed input fails safely (bad ledger in envelope, bad REPL input)
"""
from __future__ import annotations

import io
import json
import os
from contextlib import redirect_stdout

_OWNER = "DCCSliceProbe"


def _state_files():
    from form.persist import _path

    p = _path(_OWNER)
    return [p] + [p.replace(".json", "_cp_test.json")]


def _cleanup():
    for f in _state_files():
        try:
            os.remove(f)
        except OSError:
            pass


def smoke() -> bool:
    print("=== DUOBETA LIVE VERTICAL SLICE (DCC-I) ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    _cleanup()
    try:
        from form.open import open_program
        from form.persist import save
        from form.persist_rest import load
        from form.mandell.translate import translate
        from form import repl as repl_mod

        # --- 2. Mandell participates: translate() yields mandel-carrying Intents
        i_grow = translate("growth")
        i_led = translate("ledger")
        rec(
            "mandell_interprets_growth",
            i_grow.action == "growth" and "35[Discover]" in (i_grow.mandel or ""),
            f"action={i_grow.action} mandel={i_grow.mandel!r}",
        )
        rec(
            "mandell_interprets_ledger",
            i_led.action == "ledger" and "35[Discover]" in (i_led.mandel or ""),
            f"action={i_led.action} mandel={i_led.mandel!r}",
        )

        # --- 1+3+4+5. user operation enters runtime, executes, mutates state
        p = open_program(_OWNER)
        gen0 = p.duo.generation
        buf = io.StringIO()
        with redirect_stdout(buf):
            p = repl_mod._execute_intent(p, translate("evolve first intent"), raw_line="evolve first intent")
        out = buf.getvalue()
        rec(
            "evolve_enters_runtime_and_executes",
            p.duo.generation == gen0 + 1 and "Evolved" in out,
            f"gen {gen0}->{p.duo.generation}",
        )
        rec(
            "evolve_records_user_detail",
            p.duo.ledger and p.duo.ledger[-1].detail == "first intent",
            f"last={p.duo.ledger[-1].detail!r}" if p.duo.ledger else "empty",
        )

        # --- observability: growth + ledger commands
        buf = io.StringIO()
        with redirect_stdout(buf):
            repl_mod._execute_intent(p, translate("growth"), raw_line="growth")
        rec("growth_command_observable", "DuoBeta" in buf.getvalue() and "generation=" in buf.getvalue())
        buf = io.StringIO()
        with redirect_stdout(buf):
            repl_mod._execute_intent(p, translate("ledger"), raw_line="ledger")
        rec("ledger_command_observable", "first intent" in buf.getvalue())

        # --- 6. persistence: save carries the real ledger; restore is faithful
        with redirect_stdout(io.StringIO()):
            p = repl_mod._execute_intent(p, translate("evolve second intent"), raw_line="evolve second intent")
        save(p)
        from form.persist import _path

        data = json.load(open(_path(_OWNER), encoding="utf-8"))
        saved_details = [e["detail"] for e in data.get("duo_ledger", [])]
        rec(
            "save_persists_real_ledger",
            saved_details[-2:] == ["first intent", "second intent"],
            f"tail={saved_details[-2:]}",
        )

        p2 = load(_OWNER)
        restored = [(e.gen, e.detail) for e in p2.duo.ledger]
        rec(
            "restore_is_faithful",
            restored == [(e.gen, e.detail) for e in p.duo.ledger],
            f"restored={restored}",
        )
        rec(
            "restore_no_fabrication",
            not any("28[Rollback]" in d for _, d in restored),
            f"restored={restored}",
        )
        rec(
            "restore_generation_matches",
            p2.duo.generation == p.duo.generation,
            f"{p2.duo.generation} vs {p.duo.generation}",
        )

        # --- 7. second execution after restore does not corrupt authority
        with redirect_stdout(io.StringIO()):
            p2 = repl_mod._execute_intent(p2, translate("evolve third intent"), raw_line="evolve third intent")
        rec(
            "evolve_after_restore_continues",
            p2.duo.generation == p.duo.generation + 1
            and p2.duo.ledger[-1].detail == "third intent"
            and [e.gen for e in p2.duo.ledger] == sorted(e.gen for e in p2.duo.ledger),
        )

        # --- 8a. malformed duo_ledger in envelope refuses typed, fails closed
        # Gate-2 fail-closed contract (Director 7081067283): a PRESENT
        # malformed duo_ledger refuses the whole load with ProgramLoadError
        # before any state swap. The former skip-and-continue expectation
        # (load succeeds keeping only gen 5) was a legacy oracle for these
        # shapes, superseded by the legacy oracle correction (Director
        # 7081695306). Fixture kept intact from the original check.
        from form.persist_rest import ProgramLoadError

        bad = dict(data)
        bad["duo_ledger"] = [
            {"gen": "not-an-int", "detail": "x", "ts": "t"},
            {"gen": 5, "detail": "ok-entry", "ts": "t"},
            {"gen": 3, "detail": "out-of-order", "ts": "t"},
            "not-a-dict",
        ]
        bad_path = _path(_OWNER)
        json.dump(bad, open(bad_path, "w", encoding="utf-8"))
        bad_bytes = open(bad_path, "rb").read()
        refused = False
        try:
            load(_OWNER)
        except ProgramLoadError:
            refused = True
        rec(
            "malformed_ledger_fails_safe",
            refused and open(bad_path, "rb").read() == bad_bytes,
            "load did not refuse typed, or the refused load changed source bytes",
        )
        # No state swap: the good envelope still restores exactly afterwards.
        json.dump(data, open(bad_path, "w", encoding="utf-8"))
        p3 = load(_OWNER)
        rec(
            "malformed_ledger_no_state_swap",
            [(e.gen, e.detail) for e in p3.duo.ledger]
            == [(e.gen, e.detail) for e in p.duo.ledger]
            and p3.duo.generation == p.duo.generation,
            f"restored={[(e.gen, e.detail) for e in p3.duo.ledger]}",
        )

        # --- 8b. legacy envelope (no duo_ledger) restores honestly, no crash
        legacy = {k: v for k, v in data.items() if k != "duo_ledger"}
        legacy["duo_generation"] = 4
        json.dump(legacy, open(bad_path, "w", encoding="utf-8"))
        p4 = load(_OWNER)
        rec(
            "legacy_envelope_honest_restore",
            p4.duo.generation == 4
            and len(p4.duo.ledger) == 1
            and "28[Rollback]" not in p4.duo.ledger[0].detail,
            f"ledger={[e.detail for e in p4.duo.ledger]}",
        )

        # --- 8d. writer-shaped ledger with a lawful generation gap restores
        # exactly and continues (parity/continuity; generation gaps are
        # lawful — the counter can advance without an entry surviving).
        # Not pinned by the MEDIUM-four restore suite, whose clean base
        # ledger is contiguous.
        gap = dict(data)
        gap["duo_generation"] = 3
        gap["duo_ledger"] = [
            {"gen": 1, "detail": "gap-first", "ts": "2026-11-20T00:00:00Z",
             "meta": {"probe": "g1"}},
            {"gen": 3, "detail": "gap-third", "ts": "2026-11-22T00:00:00Z",
             "meta": {"probe": "g3"}},
        ]
        json.dump(gap, open(bad_path, "w", encoding="utf-8"))
        p5 = load(_OWNER)
        rec(
            "gapped_ledger_restores_exactly",
            [(e.gen, e.detail, dict(getattr(e, "meta", None) or {}))
             for e in p5.duo.ledger]
            == [(1, "gap-first", {"probe": "g1"}),
                (3, "gap-third", {"probe": "g3"})]
            and p5.duo.generation == 3,
            f"ledger={[(e.gen, e.detail) for e in p5.duo.ledger]} gen={p5.duo.generation}",
        )
        with redirect_stdout(io.StringIO()):
            p5 = repl_mod._execute_intent(p5, translate("evolve fourth intent"), raw_line="evolve fourth intent")
        rec(
            "gapped_ledger_continues_in_order",
            p5.duo.generation == 4
            and [e.gen for e in p5.duo.ledger] == [1, 3, 4]
            and p5.duo.ledger[-1].detail == "fourth intent",
            f"gens={[e.gen for e in p5.duo.ledger]} gen={p5.duo.generation}",
        )

        # --- 8c. malformed REPL input fails safely (no exception, no state change)
        buf = io.StringIO()
        with redirect_stdout(buf):
            repl_mod._execute_intent(p4, translate("evolve loop"), raw_line="evolve loop")
        rec(
            "evolve_loop_still_reachable",
            True,  # must not raise; loop path is separate
        )
        gen_before = p4.duo.generation
        buf = io.StringIO()
        with redirect_stdout(buf):
            repl_mod._execute_intent(p4, translate("ledger abc"), raw_line="ledger abc")
        rec(
            "ledger_bad_arg_fails_safe",
            p4.duo.generation == gen_before,
        )
    finally:
        _cleanup()

    ok = all(r)
    print(f"duobeta_live: {sum(r)}/{len(r)} {'GREEN' if ok else 'RED'}")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
