"""DD-18 — Pulse receipt honesty (C1.PulseReceipt).

Defect: the Dell 25 leaf called program.pulse(), DISCARDED the
EnhanceGate's verdict, and appended "Pulse sent." unconditionally —
and execute_seed's fall-through reported ok=True. With the gate OFF
(or the pulse budget exhausted) nothing was sent, yet the receipt
claimed success. The gate itself was always honest
({ok: False, reason: "enhance OFF"}); the lie lived in the leaf
(and in the REPL's pulse action, fixed in the same pattern).

Contract after repair: the receipt reports the ACTUAL gate outcome —
"Pulse sent." only when a pulse executed; otherwise
"Pulse NOT sent (<gate reason>)." with ok=False. Temp's hot branch
discloses a refused pulse instead of claiming it. Targeting /
visibility of resonance stays with the design session (not here).
"""
import glob
import os
import shutil
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESULTS = []


def _rec(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name +
          ((": " + detail) if (detail and not ok) else ""), flush=True)


def _cleanup(owner):
    state = os.path.join(_ROOT, "form", "state")
    for f in glob.glob(os.path.join(state, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            raise RuntimeError(f"cleanup failed for {f}: {e}")


def _program(owner):
    from form.open import Program
    _cleanup(owner)
    prog = Program(owner=owner)
    from form.mandell.core_ii_exec import attach
    attach(prog)
    return prog


def _run(prog, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(prog, seed)


def _msgs(r):
    return [m for m in r.get("messages", [])
            if not m.startswith(("Mandell:", "English:"))]


def main():
    owner = "DD18" + uuid.uuid4().hex[:8].upper()
    p = _program(owner)
    try:
        # Seed a scored unit so a real pulse has something to move.
        p.enhance.state.scores["garden_gate"] = 1.0

        # 1-3. Gate OFF (default): receipt must report the refusal.
        r = _run(p, "25[Pulse]")
        _rec("gate_off_message_honest",
             _msgs(r) == ["Pulse NOT sent (enhance OFF)."], str(_msgs(r)))
        _rec("gate_off_result_not_ok",
             r.get("ok") is False and "enhance OFF" in str(r.get("error", "")),
             f"ok={r.get('ok')} error={r.get('error')}")
        _rec("gate_off_state_unchanged",
             p.enhance.on is False and p.enhance.session_pulses == 0
             and p.scores() == {"garden_gate": 1.0},
             f"pulses={p.enhance.session_pulses} scores={p.scores()}")

        # 4. Gate ON: a real pulse still reports "Pulse sent."
        _run(p, "25[Pulse] :: on")
        r = _run(p, "25[Pulse]")
        _rec("gate_on_pulse_sent",
             _msgs(r) == ["Pulse sent."] and r.get("ok") is True
             and p.enhance.session_pulses == 1,
             f"msgs={_msgs(r)} pulses={p.enhance.session_pulses}")

        # 5. Budget exhausted: refusal named, count does not move.
        p.enhance.max_pulses = 1
        r = _run(p, "25[Pulse]")
        _rec("budget_exhausted_refusal",
             _msgs(r) == ["Pulse NOT sent (pulse budget exhausted)."]
             and r.get("ok") is False and p.enhance.session_pulses == 1,
             f"msgs={_msgs(r)} pulses={p.enhance.session_pulses}")
        p.enhance.max_pulses = 0

        # 6. Arm labels unchanged (control).
        p.enhance_off()
        r = _run(p, "25[Pulse] :: on")
        r2 = _run(p, "25[Pulse] :: enhance_on")
        _rec("arm_labels_unchanged",
             _msgs(r) == ["Enhance ON."] and _msgs(r2) == ["Enhance ON."]
             and p.enhance.on is True, f"{_msgs(r)} / {_msgs(r2)}")

        # 7. Temp hot with exhausted budget: pulse refusal disclosed.
        p.enhance.max_pulses = p.enhance.session_pulses  # budget spent
        r = _run(p, "26[Temp] :: hot")
        m = _msgs(r)
        _rec("temp_hot_budget_refusal_disclosed",
             len(m) == 1 and "enhance ON" in m[0] and "pulse refused" in m[0]
             and "budget exhausted" in m[0], str(m))
        p.enhance.max_pulses = 0

        # 8. Temp hot normal (control): claims the pulse, pulse happens.
        before = p.enhance.session_pulses
        r = _run(p, "26[Temp] :: hot")
        _rec("temp_hot_normal",
             _msgs(r) == ["Temp → hot (enhance ON + pulse)"]
             and p.enhance.session_pulses == before + 1,
             f"msgs={_msgs(r)} pulses={p.enhance.session_pulses}")

        # 9. Program layer was always honest (wrong-layer guard).
        p.enhance_off()
        out = p.pulse()
        _rec("program_layer_honest",
             out.get("ok") is False and out.get("reason") == "enhance OFF",
             str(out))

        # 10. The exact _leaf result chain_exec consumes reports not-ok.
        from form.mandell.executor import execute_seed
        r = execute_seed(p, "25[Pulse]", _leaf=True)
        _rec("chain_input_contract_not_ok",
             r.get("ok") is False and _msgs(r) == ["Pulse NOT sent (enhance OFF)."],
             f"ok={r.get('ok')} msgs={_msgs(r)}")
    finally:
        _cleanup(owner)

    n = sum(1 for _, ok in RESULTS if ok)
    print(f"DD18_PULSE_RECEIPT: {n}/{len(RESULTS)}", flush=True)
    return 0 if n == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
