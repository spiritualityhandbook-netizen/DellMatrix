#!/usr/bin/env python3
"""GP-E08 — Caller/route integration evidence for the typed
admission layer (Part II, anchor row #24).

WHY THIS SUITE EXISTS: form/gpe08_admission_test.py proves the
admission layer (form/mandell/admission.py, public entry `admit`)
at API level, and proves the caller contract against route_intent
called directly. The Director's GP-E08 source disposition
(7069840264) accepted the layer at API scope only and required
"caller/route integration evidence including negative controls";
the Keeper's challenge pass (7073788601) named the same gap.

CALLER REALITY (CALLER_MAP.md, this circuit's staging record):
NO production caller imports or calls `admit` at this head — the
REPL dispatch (form/repl.py `_dispatch_public_line`) is NOT
rewired through the layer. So this suite proves the two things
that CAN be proven honestly at this head:

  A/B. THE MEDIATED ROUTE: a caller honoring the contract (route
       only admitted admissions) drives the layer's products
       through the SAME downstream machinery the real route uses —
       semantic_router.route_intent for English/LM intents (the
       function _execute_intent's routed arms call) and
       execution_observer.observe_seed_execution for seeds (the
       exact function the REPL's seed arms call) — on isolated
       owners, with agreement on verdict, seed, and effect.

  C.   NEGATIVE CONTROLS: every rejected line, driven through the
       caller contract, produces ZERO route/execution calls and a
       byte-identical owner-state fingerprint (ideas + history
       counts, snapshotted before/after — a fresh Program is never
       assumed empty).

  D.   DIFFERENTIAL AGAINST THE REAL ROUTE: the same battery is
       driven through the REPL's actual dispatch
       (_dispatch_public_line — the public line handler; precedent:
       greek/iri_i/lm4_tollbooth and ten sibling suites drive it
       directly, INTEGRATION / high-fidelity dispatch evidence).
       Admitted lines must traverse the real route without refusal
       or crash. For rejected lines the bare route's behavior is
       printed as the baseline record; one contrast is asserted —
       the malformed seed fragment "10[Keep", which the bare route
       classifies as English and EXECUTES (a save[Keep] intent is
       formed and the interaction recorded), while the mediated
       contract refuses it at the door with zero mutation. That
       fall-through is exactly what the admission layer exists to
       close; the layer's absence from the dispatch is a wiring
       fact (Director 7069840264), not relitigated here.

Isolation: every check uses its own uniquely-named Program owner;
state is fingerprinted before/after, never assumed empty.
"""

from __future__ import annotations

import contextlib
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def _snap(p):
    ideas = getattr(p, "ideas", None) or []
    hist = getattr(p, "history", None) or []
    return (len(ideas), len(hist))


class _Contract:
    """The caller contract, instrumented: route/execute ONLY an
    admitted admission, through the real route's own machinery."""

    def __init__(self):
        self.calls = 0

    def drive(self, program, line):
        from form.mandell.admission import admit
        from form.mandell.semantic_router import route_intent
        from form.mandell.execution_observer import observe_seed_execution
        adm = admit(line)
        if adm.verdict != "admitted":
            return adm, None
        self.calls += 1
        if adm.intent is not None:
            return adm, route_intent(program, adm.intent, line)
        if adm.seed is not None:
            return adm, observe_seed_execution(program, line)
        return adm, None


def run_all():
    from form.open import Program
    from form.repl import _dispatch_public_line

    # ---------- A. Mediated route: English + LM intents ----------
    c = _Contract()
    p = Program(owner="GPE08INTGROW")
    adm, r = c.drive(p, "grow three")
    check("route_eng_grow_agreement",
          adm.verdict == "admitted" and r is not None and r.ok
          and r.seed == "13[Loop] :: 3",
          f"verdict={adm.verdict} ok={None if r is None else r.ok} "
          f"seed={None if r is None else r.seed!r}")

    p = Program(owner="GPE08INTCYCLE")
    adm, r = c.drive(p, "cycle three times")
    check("route_eng_cycle_agreement",
          adm.verdict == "admitted" and r is not None and r.ok
          and r.seed == "06[Cycle] :: 3",
          f"verdict={adm.verdict} ok={None if r is None else r.ok} "
          f"seed={None if r is None else r.seed!r}")

    p = Program(owner="GPE08INTLM")
    adm, r = c.drive(p, "la serva")
    check("route_lm_save_agreement",
          adm.verdict == "admitted" and adm.kind == "latinmandell"
          and r is not None and r.ok and r.seed == "10[Keep]",
          f"verdict={adm.verdict} kind={adm.kind} "
          f"ok={None if r is None else r.ok} "
          f"seed={None if r is None else r.seed!r}")

    # ---------- B. Mediated route: seed execution ----------
    p = Program(owner="GPE08INTSEEDCH")
    adm, res = c.drive(p, "10[Keep] > 27[Checkpoint]")
    check("route_seed_chain_executed",
          adm.verdict == "admitted" and adm.mode == "chain"
          and isinstance(res, dict) and res.get("ok") is True,
          f"verdict={adm.verdict} mode={adm.mode} "
          f"exec_ok={None if not isinstance(res, dict) else res.get('ok')}")

    p = Program(owner="GPE08INTSEED1")
    adm, res = c.drive(p, "10[Keep]")
    check("route_seed_single_executed",
          adm.verdict == "admitted" and isinstance(res, dict)
          and res.get("ok") is True,
          f"verdict={adm.verdict} "
          f"exec_ok={None if not isinstance(res, dict) else res.get('ok')}")

    # ---------- C. Negative controls: rejection before mutation --
    negatives = [
        ("10[Keep] > banana", "GPE08INTNEG1"),
        ("10[Keep", "GPE08INTNEG2"),
        ('47[Embed](path=)', "GPE08INTNEG3"),
        ("flibberty gibbet snarp", "GPE08INTNEG4"),
        ("delete the thing if it rains", "GPE08INTNEG5"),
        ("la zzqq", "GPE08INTNEG6"),
        ("   ", "GPE08INTNEG7"),
    ]
    for line, owner in negatives:
        c = _Contract()
        p = Program(owner=owner)
        before = _snap(p)
        adm, out = c.drive(p, line)
        after = _snap(p)
        tag = "neg_" + owner[-4:].lower()
        check(tag,
              adm.verdict == "rejected" and c.calls == 0
              and out is None and after == before,
              f"line={line!r} reason={adm.reason} calls={c.calls} "
              f"state {before} -> {after}")

    # ---------- D. Differential against the real dispatch --------
    # Admitted lines traverse the real route without crash/refusal.
    for line, owner in (("grow three", "GPE08INTDIF1"),
                        ("10[Keep]", "GPE08INTDIF2"),
                        ("la serva", "GPE08INTDIF3")):
        p = Program(owner=owner)
        buf = io.StringIO()
        err = ""
        try:
            with contextlib.redirect_stdout(buf):
                out_p = _dispatch_public_line(p, line,
                                              interaction_id="gpe08int")
        except Exception as e:  # noqa: BLE001 - evidence, not silence
            out_p, err = None, f"{type(e).__name__}: {e}"
        tag = "diff_admitted_" + owner[-4:].lower()
        check(tag,
              out_p is not None and not err,
              f"line={line!r} err={err!r} "
              f"out_head={[ln for ln in buf.getvalue().splitlines() if ln.strip()][:2]}")

    # Bare-route baseline for the rejected lines: never a crash;
    # the behavior is printed as the record of what the unwired
    # route does today.
    for line, owner in negatives[:6]:
        p = Program(owner=owner + "D")
        before = _snap(p)
        buf = io.StringIO()
        err = ""
        try:
            with contextlib.redirect_stdout(buf):
                out_p = _dispatch_public_line(p, line,
                                              interaction_id="gpe08int")
        except Exception as e:  # noqa: BLE001
            out_p, err = None, f"{type(e).__name__}: {e}"
        after = _snap(p)
        tag = "diff_bare_nocrash_" + owner[-4:].lower()
        check(tag,
              out_p is not None and not err,
              f"line={line!r} err={err!r} state {before} -> {after} "
              f"out_head={[ln for ln in buf.getvalue().splitlines() if ln.strip()][:2]}")

    # The asserted contrast: the bare route EXECUTES the malformed
    # seed fragment as English (interaction recorded: history
    # grows), while the mediated contract (section C, GPE08INTNEG2)
    # refused the same line with zero calls and zero mutation.
    p = Program(owner="GPE08INTFRAG")
    before = _snap(p)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _dispatch_public_line(p, "10[Keep", interaction_id="gpe08int")
    after = _snap(p)
    check("diff_fragment_fallthrough_contrast",
          after[1] > before[1],
          f"bare route on '10[Keep': history {before[1]} -> {after[1]} "
          f"(executed as English save[Keep]); mediated contract refused "
          f"it at the door — see neg_neg2")

    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"GP-E08 route integration: {passed}/{len(CHECKS)} checks passed")
    if passed != len(CHECKS):
        raise AssertionError(
            f"GP-E08 route integration: {len(CHECKS) - passed} check(s) "
            "failed: " + ", ".join(n for n, ok in CHECKS if not ok))


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"GP-E08 ROUTE INTEGRATION SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
