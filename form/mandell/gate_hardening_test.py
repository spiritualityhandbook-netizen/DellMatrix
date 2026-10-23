"""Phase C — InternetGate auto-enable hardening proofs.

Traced hazard (post-GDP audit, 2026-10-22): `search_far_wide` was
the gate's only auto-enable surface — while OFF it called
`ensure_on_for_auto()`, which succeeded on ANY gate because
`auto_allowed` defaulted to True, including the gate object the
Program itself carries. fetch_url and research_topic were already
hard-gated. No Program/REPL caller reaches search_far_wide today,
so the hazard was latent: any future Program path calling it would
have silently turned the user's gate on.

Hardening proven here:
- A default gate can never auto-enable: search_far_wide while OFF
  fails closed ("Internet OFF and auto not allowed") and the gate
  stays OFF. No network is attempted (the failure returns before
  any fetch machinery).
- The Program-carried gate is fail-closed the same way.
- Persisted legacy state cannot resurrect auto-enable: from_dict
  ignores a stored auto_allowed=True (it was only the former
  default round-tripping; no user surface sets it).
- The designed auto-growth behavior survives in its own lane:
  a gate explicitly constructed with auto_allowed=True (what
  AutoGrowth and MatrixAwake now do at their own construction
  sites) still auto-enables via ensure_on_for_auto.
- The hard gates did not move: fetch_url / research_topic while
  OFF still fail without enabling anything.
- Public path unchanged: a user can still turn the gate ON
  explicitly and search_far_wide then runs (shape check, local).

All checks are offline: every search_far_wide success-path check
runs against an explicitly-ON gate whose fetch layer is stubbed
at the instance level, so no real network is touched.
"""

from __future__ import annotations

import sys
import uuid

CHECKS: list = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail and not cond else ""))


def unique_owner(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _cleanup(owner: str) -> None:
    from form.persist import _path, _cp_path
    for path in (_path(owner), _cp_path(owner)):
        try:
            import os
            os.remove(path)
        except OSError:
            pass


def part_default_gate_fail_closed():
    from form.dell_matrix.internet_gate import InternetGate
    g = InternetGate()
    check("default: gate starts OFF", g.on is False)
    check("default: auto_allowed defaults False", g.auto_allowed is False)
    check("default: ensure_on_for_auto refuses", g.ensure_on_for_auto() is False)
    check("default: gate still OFF after ensure attempt", g.on is False)
    out = g.search_far_wide("eigenvalue")
    check("default: search_far_wide fails closed while OFF",
          out.get("ok") is False
          and "auto not allowed" in str(out.get("error")),
          f"{out}")
    check("default: gate still OFF after search_far_wide", g.on is False)


def part_program_gate_fail_closed():
    from form.open import open_program
    owner = unique_owner("gateprog")
    try:
        p = open_program(owner)
        check("program: carried gate exists", p.internet is not None)
        check("program: carried gate cannot auto-enable",
              p.internet is not None and p.internet.auto_allowed is False)
        out = p.internet.search_far_wide("eigenvalue")
        check("program: search_far_wide fails closed",
              out.get("ok") is False and p.internet.on is False)
    finally:
        _cleanup(owner)


def part_persisted_legacy_fail_closed():
    from form.dell_matrix.internet_gate import InternetGate
    legacy = {"on": False, "auto_allowed": True,
              "allowed_hosts": ["en.wikipedia.org"]}
    g = InternetGate.from_dict(legacy)
    check("persisted: legacy auto_allowed=True NOT restored",
          g.auto_allowed is False)
    check("persisted: ensure_on_for_auto refuses on loaded gate",
          g.ensure_on_for_auto() is False and g.on is False)
    check("persisted: allowlist still restored",
          "en.wikipedia.org" in g.allowed_hosts)
    g2 = InternetGate.from_dict({"on": True, "auto_allowed": True})
    check("persisted: explicit ON still restored (user's own act)",
          g2.on is True and g2.auto_allowed is False)
    g3 = InternetGate.from_dict(None)
    check("persisted: absent section loads fail-closed",
          g3.on is False and g3.auto_allowed is False)


def part_opt_in_lane_preserved():
    from form.dell_matrix.internet_gate import InternetGate
    g = InternetGate(auto_allowed=True)
    check("optin: explicit opt-in auto-enables",
          g.ensure_on_for_auto() is True and g.on is True)
    # The two designed auto-growth owners opt in at construction.
    import inspect
    from form.dell_matrix import auto_growth, matrix_awake
    check("optin: AutoGrowth constructs its gate with auto_allowed=True",
          "InternetGate(auto_allowed=True)" in inspect.getsource(auto_growth))
    check("optin: MatrixAwake constructs its gate with auto_allowed=True",
          "InternetGate(auto_allowed=True)" in inspect.getsource(matrix_awake))


def part_hard_gates_unmoved():
    from form.dell_matrix.internet_gate import InternetGate
    g = InternetGate()
    out = g.fetch_url("https://example.com/")
    check("hard: fetch_url while OFF fails, gate stays OFF",
          out.get("ok") is False and g.on is False)
    out = g.research_topic("eigenvalue")
    check("hard: research_topic while OFF fails, gate stays OFF",
          out.get("ok") is False and g.on is False)


def part_explicit_on_still_works():
    from form.dell_matrix.internet_gate import InternetGate
    g = InternetGate()
    g.turn_on()
    # Stub the instance fetch layer: shape proof without real network.
    g.search_public = lambda q: {"ok": True, "hits": [{  # type: ignore[method-assign]
        "title": "Eigenvalue", "text": "a scalar lambda",
        "source": "stub", "url": "http://127.0.0.1/x"}], "sources": ["stub"]}
    g.research_topic = lambda t: {"ok": True}  # type: ignore[method-assign]
    out = g.search_far_wide("eigenvalue")
    check("explicit-on: search_far_wide runs when the user turned it ON",
          out.get("ok") is True and out.get("count") == 1
          and out.get("internet_on") is True, f"{out}")


def smoke() -> bool:
    part_default_gate_fail_closed()
    part_program_gate_fail_closed()
    part_persisted_legacy_fail_closed()
    part_opt_in_lane_preserved()
    part_hard_gates_unmoved()
    part_explicit_on_still_works()
    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"=== Gate auto-enable hardening: {passed}/{len(CHECKS)} ===")
    return passed == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
