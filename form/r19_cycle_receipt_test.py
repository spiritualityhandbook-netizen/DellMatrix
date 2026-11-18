"""R19 — Cycle count truthfulness: no silent clamp, no unruled ceiling.

Director ruling 2026-11-18 (R19 binding contract): Dell 06 Cycle,
including its flow-program route, uses the same 1..5 execution bound
as the other Cycle/Loop paths; the unruled flow ceiling of 99 is
removed. The repair must preserve what the user originally requested:
requesting 20 cycles may execute 5, but the receipt must explicitly
show 20 requested, 5 executed, 15 remaining, without implying the
full request succeeded. Invalid counts refuse without executing
growth on every door (ruling point 3: an explicitly malformed count
is a typed refusal, Loop B2 parity; only a genuinely omitted count
keeps the default of 1). Automatic continuation beyond five is NOT
authorized by the ruling.

Defects pinned here (all reproduced on main 3a8b1412 by the R19
census probe, hidden_files/R19_CENSUS_PROBE_2026-11-18.md):
  1. executor_leaf Cycle arm clamps and prints ONLY the clamped
     value (`Cycle x5` for a request of 20); the request is lost.
  2. semantic_router._seed_cycle clamps inside seed construction, so
     no downstream receipt can ever name the loss (Loop's seed
     builder applies no upper clamp — the precedent).
  3. translate.py clamps inside Intent construction the same way.
  4. flow_executor._args_from_label applies an UNRULED 99 ceiling;
     the flow step record (count 20) and the execution (5) disagree,
     undisclosed.

Labels: seed path = PUBLIC_ENTRY (real Program via
form.mandell.executor.execute_seed); router/translate/flow-args =
INTEGRATION (direct calls). Isolation: dedicated owner, canonical
state-file cleanup before/after (dirf13 pattern).
"""
import glob
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OWNER = "R19Test"
_RESULTS = []


def _rec(name, ok, detail=""):
    _RESULTS.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")


def _cleanup():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
    if not os.path.isdir(base):
        return
    for pat in (f"program_{OWNER}.json", f"nursery_{OWNER}.json",
                f"checkpoint_{OWNER}.json", f"confirm_journal_{OWNER}.json",
                f"confirm_gen_{OWNER}.json", f"confirm_current_{OWNER}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            os.remove(f)
    d = os.path.join(base, f"ideas_{OWNER}")
    if os.path.isdir(d):
        shutil.rmtree(d)


def _run():
    _cleanup()
    try:
        from form.open import Program
        from form.mandell.core_ii_exec import attach
        from form.mandell.executor import execute_seed

        def prog():
            p = Program(owner=OWNER)
            attach(p)
            return p

        def msgs(r):
            return [m for m in r.get("messages", [])
                    if not m.startswith(("Mandell:", "English:"))]

        def joined(r):
            return "\n".join(str(m) for m in msgs(r))

        p = prog()
        execute_seed(p, "08[Create] :: Alpha")

        # --- Face 1: seed Cycle receipts name requested/executed/remaining
        cases = [(0, 1), (1, 1), (5, 5), (6, 5), (20, 5), (100, 5)]
        for requested, executed in cases:
            r = execute_seed(prog(), f"06[Cycle] :: {requested}")
            j = joined(r)
            ok = (f"Cycle x{executed}:" in j
                  and f"requested {requested}" in j
                  and f"executed {executed}" in j)
            if requested > executed:
                ok = ok and f"remaining {requested - executed}" in j
            _rec(f"seed cycle {requested}: receipt truthful", ok,
                 j.replace("\n", " | ")[:160])

        # In-range request: no clamp note, no remaining.
        r = execute_seed(prog(), "06[Cycle] :: 3")
        j = joined(r)
        _rec("seed cycle 3: exact, unadorned",
             "requested 3" in j and "executed 3" in j
             and "remaining" not in j and "clamped" not in j, j[:120])

        # R19 point 3: a genuinely omitted count keeps the default of
        # 1; an explicitly malformed count is a typed refusal with no
        # growth (Loop B2 parity) — never a silent default.
        r = execute_seed(prog(), "06[Cycle]")
        _rec("seed cycle omitted: default x1 preserved",
             r.get("ok") is True and "Cycle x1:" in joined(r),
             joined(r)[:120])
        p_ref = prog()
        hist_before = len(list(getattr(p_ref, "history", []) or []))
        for bad in ("banana", "-3", "²", "２０", "9" * 5000, "20x"):
            r = execute_seed(p_ref, f"06[Cycle] :: {bad}")
            j = joined(r)
            _rec(f"seed cycle malformed {bad[:8]!r}: typed refusal, no growth",
                 r.get("ok") is False
                 and r.get("error") == "invalid_cycle_count"
                 and "Cycle x" not in j
                 and "Cycle refused:" in str(r.get("messages", "")),
                 f"ok={r.get('ok')} err={r.get('error')}")
        hist_after = len(list(getattr(p_ref, "history", []) or []))
        _rec("refusals left no growth trace in history",
             hist_after == hist_before, f"{hist_before} -> {hist_after}")

        # Loop arm regression guard: honest receipt unchanged.
        r = execute_seed(prog(), "13[Loop] :: 20")
        j = joined(r)
        _rec("seed loop 20: existing honest receipt unchanged",
             "Loop: requested 20, executed 5." in j, j[:160])

        # --- Face 2: router seed carries the requested count (Loop precedent)
        from form.mandell.semantic_router import _seed_cycle

        class _Intent:
            def __init__(self, count):
                self.args = {"count": count}

        class _Parsed:
            label = ""

        _rec("router seed cycle 20 carries 20",
             _seed_cycle(_Intent(20), _Parsed()) == "06[Cycle] :: 20",
             _seed_cycle(_Intent(20), _Parsed()))
        _rec("router seed cycle 150 carries 150 (no early ceiling)",
             _seed_cycle(_Intent(150), _Parsed()) == "06[Cycle] :: 150",
             _seed_cycle(_Intent(150), _Parsed()))
        _rec("router seed cycle 3 unchanged",
             _seed_cycle(_Intent(3), _Parsed()) == "06[Cycle] :: 3",
             _seed_cycle(_Intent(3), _Parsed()))
        _rec("router seed cycle 0 carries 0 (leaf discloses the clamp-up)",
             _seed_cycle(_Intent(0), _Parsed()) == "06[Cycle] :: 0",
             _seed_cycle(_Intent(0), _Parsed()))
        _rec("router seed cycle -3 carries -3 (leaf refuses the grammar)",
             _seed_cycle(_Intent(-3), _Parsed()) == "06[Cycle] :: -3",
             _seed_cycle(_Intent(-3), _Parsed()))
        _rec("router seed cycle 'banana' travels raw to the leaf refusal",
             _seed_cycle(_Intent("banana"), _Parsed()) == "06[Cycle] :: banana",
             _seed_cycle(_Intent("banana"), _Parsed()))
        r = execute_seed(prog(), _seed_cycle(_Intent("banana"), _Parsed()))
        _rec("router-carried malformed count refuses at the leaf",
             r.get("ok") is False
             and r.get("error") == "invalid_cycle_count",
             f"ok={r.get('ok')} err={r.get('error')}")

        # --- Face 3: translate keeps the requested count in the Intent
        from form.mandell.translate import translate

        intent = translate("cycle 20")
        _rec("translate 'cycle 20': args carry 20",
             (intent.args or {}).get("count") == 20, str(intent.args))
        _rec("translate 'cycle 20': mandel carries 20",
             intent.mandel == "06[Cycle] :: 20", str(intent.mandel))
        intent3 = translate("cycle 3")
        _rec("translate 'cycle 3' unchanged",
             (intent3.args or {}).get("count") == 3
             and intent3.mandel == "06[Cycle] :: 3", str(intent3.mandel))
        intent0 = translate("cycle 0")
        _rec("translate 'cycle 0': count 0 travels (leaf discloses)",
             (intent0.args or {}).get("count") == 0
             and intent0.mandel == "06[Cycle] :: 0", str(intent0.mandel))
        r = execute_seed(prog(), intent0.mandel)
        j = joined(r)
        _rec("english cycle 0 end-to-end: requested 0, executed 1",
             "requested 0" in j and "executed 1" in j, j[:140])

        # English end-to-end: the translated seed executes with a
        # truthful receipt.
        r = execute_seed(prog(), intent.mandel)
        j = joined(r)
        _rec("english cycle 20 end-to-end: receipt 20/5/15",
             "requested 20" in j and "executed 5" in j
             and "remaining 15" in j, j[:160])

        # --- Face 4: flow args carry the request; the 99 ceiling is gone
        from form.mandell.flow_executor import _args_from_label

        _rec("flow args cycle 20 -> 20",
             _args_from_label("cycle", "20") == {"count": 20},
             str(_args_from_label("cycle", "20")))
        _rec("flow args cycle 150 -> 150 (unruled 99 removed)",
             _args_from_label("cycle", "150") == {"count": 150},
             str(_args_from_label("cycle", "150")))
        _rec("flow args cycle 99 -> 99 (the old ceiling value travels)",
             _args_from_label("cycle", "99") == {"count": 99},
             str(_args_from_label("cycle", "99")))
        _rec("flow args cycle omitted -> default 1",
             _args_from_label("cycle", "") == {"count": 1},
             str(_args_from_label("cycle", "")))
        _rec("flow args cycle malformed travels raw (leaf refuses)",
             _args_from_label("cycle", "abc") == {"count": "abc"},
             str(_args_from_label("cycle", "abc")))
        seed = _seed_cycle(_Intent(_args_from_label("cycle", "abc")["count"]),
                           _Parsed())
        r = execute_seed(prog(), seed)
        _rec("flow malformed count refuses at the leaf, no growth",
             r.get("ok") is False
             and r.get("error") == "invalid_cycle_count"
             and "Cycle x" not in joined(r),
             f"seed={seed} ok={r.get('ok')} err={r.get('error')}")
        seed99 = _seed_cycle(_Intent(_args_from_label("cycle", "99")["count"]),
                             _Parsed())
        r = execute_seed(prog(), seed99)
        j = joined(r)
        _rec("flow 99 reconciled: receipt 99/5/94",
             seed99 == "06[Cycle] :: 99" and "requested 99" in j
             and "executed 5" in j and "remaining 94" in j,
             f"seed={seed99} receipt={j[:120]}")

        # Flow reconciliation end-to-end: flow args -> router seed ->
        # leaf execution; the step record and the receipt must agree.
        flow_args = _args_from_label("cycle", "20")
        seed = _seed_cycle(_Intent(flow_args["count"]), _Parsed())
        r = execute_seed(prog(), seed)
        j = joined(r)
        _rec("flow 20 reconciled: seed + receipt agree on requested 20",
             seed == "06[Cycle] :: 20" and "requested 20" in j
             and "executed 5" in j and "remaining 15" in j,
             f"seed={seed} receipt={j[:120]}")

        # --- Chain leg: a chain containing a Cycle atom at 20
        r = execute_seed(prog(), "06[Cycle] :: 20 >> 10[Keep]")
        j = joined(r)
        _rec("chain cycle 20: receipt 20/5/15",
             "requested 20" in j and "executed 5" in j
             and "remaining 15" in j, j[:200])

        # --- Chain leg: Loop atom in a chain keeps its honest receipt
        r = execute_seed(prog(), "13[Loop] :: 20 >> 10[Keep]")
        j = joined(r)
        _rec("chain loop 20: receipt requested 20, executed 5",
             "Loop: requested 20, executed 5." in j, j[:200])
    finally:
        _cleanup()
    return all(ok for _, ok in _RESULTS)


def smoke() -> bool:
    global _RESULTS
    _RESULTS = []
    try:
        return _run()
    except Exception as exc:  # noqa: BLE001 — surface, never swallow
        import traceback
        traceback.print_exc()
        print(f"FAIL  r19 suite raised: {exc!r}")
        return False


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
