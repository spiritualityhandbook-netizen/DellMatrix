"""DIR-F13 — Loop count grammar (Unicode-digit refusal).

Contracts proven here, through the public seed path
(form.mandell.executor.execute_seed) on a real Program:

- The count grammar is DEFINED: a Loop count label is valid iff
  empty (means 1) or 1..9 ASCII decimal digits, checked BEFORE any
  int() conversion (executor_leaf._parse_count is the one owner,
  shared by Dells 6/13/48).
- Superscript '²' (isdigit True, int() raises) REFUSES
  invalid_loop_count with zero nursery growth, and the program
  stays usable (a lawful Loop runs afterwards).
- Non-ASCII decimal digits ('٣' Arabic-Indic, '５' fullwidth)
  are REFUSED by the same defined grammar — never silently
  converted, never a crash.
- Oversized ASCII strings ('9'*100, '9'*5000) REFUSE before
  conversion (length gate) with zero growth.
- Ordinary counts are unchanged (step-6 B2 regression): '' -> 1,
  '3' -> 3, '99' -> clamped 5, requested/executed receipt intact;
  malformed 'abc'/'2.5'/'-3' refuse exactly as before.
- Siblings keep their existing default semantics, crash-free:
  Cycle (6) with '²' runs the default x1; Macro (48) with a '²'
  label/token does not raise; Decay (16) with a '²' factor does
  not raise (default factor path / gate verdict, never ValueError).
- Chain path: a chained Loop '²' reports the atom failed, not ok.

Labels: INTEGRATION / PUBLIC_ENTRY (real Program, real growth).
"""
from __future__ import annotations

import glob
import os
import shutil
import sys

RESULTS: list = []


def _rec(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))


def _cleanup(owner: str) -> None:
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "state")
    if not os.path.isdir(base):
        return
    errors = []
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}.json",
                f"confirm_journal_{owner}.json",
                f"confirm_gen_{owner}.json",
                f"confirm_current_{owner}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(f)
            except OSError as e:
                errors.append(f"{f}: {e}")
    d = os.path.join(base, f"ideas_{owner}")
    if os.path.isdir(d):
        try:
            shutil.rmtree(d)
        except OSError as e:
            errors.append(f"{d}: {e}")
    if errors:
        raise RuntimeError(f"cleanup failed for {owner}: {errors}")


def _prog(owner: str):
    _cleanup(owner)
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    p = Program(owner=owner)
    attach(p)
    return p


def _run(p, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(p, seed)


def _msgs(r):
    return [m for m in r.get("messages", [])
            if not m.startswith(("Mandell:", "English:"))]


def _pending(p):
    return p.nursery.summary()["pending"]


SUPER2 = "²"
ARABIC3 = "٣"
FULLWIDTH5 = "５"


def _loop_refusals() -> None:
    p = _prog("F13Loop")
    _run(p, "08[Create] :: Alpha")
    base = _pending(p)
    for label, tag in ((SUPER2, "superscript"),
                       (ARABIC3, "arabic-indic"),
                       (FULLWIDTH5, "fullwidth")):
        try:
            r = _run(p, f"13[Loop] :: {label}")
            _rec(f"W-refusal {tag}: ok=False invalid_loop_count, "
                 f"zero growth, no exception",
                 r.get("ok") is False
                 and r.get("error") == "invalid_loop_count"
                 and _pending(p) == base
                 and any("no cycles run" in m for m in _msgs(r)),
                 f"{r.get('ok')} / {r.get('error')} / {_msgs(r)}")
        except Exception as e:  # the defect: a raw ValueError escape
            _rec(f"W-refusal {tag}: ok=False invalid_loop_count, "
                 f"zero growth, no exception", False,
                 f"RAISED {type(e).__name__}: {e}")
    for label, tag in (("9" * 100, "oversized-100"),
                       ("9" * 5000, "oversized-5000")):
        try:
            r = _run(p, f"13[Loop] :: {label}")
            _rec(f"W-oversized {tag}: refusal before conversion, "
                 f"zero growth, no exception",
                 r.get("ok") is False
                 and r.get("error") == "invalid_loop_count"
                 and _pending(p) == base,
                 f"{r.get('ok')} / {r.get('error')}")
        except Exception as e:
            _rec(f"W-oversized {tag}: refusal before conversion, "
                 f"zero growth, no exception", False,
                 f"RAISED {type(e).__name__}: {e}")
    # program stays usable after every refusal
    r = _run(p, "13[Loop] :: 2")
    _rec("W-usable: lawful Loop runs after refusals (delta == 2 "
         "cycles' growth, receipt intact)",
         r.get("ok") is True and _pending(p) > base
         and any("requested 2, executed 2" in m for m in _msgs(r)),
         f"{r.get('ok')} / {_msgs(r)}")
    _cleanup("F13Loop")


def _loop_ordinary() -> None:
    p = _prog("F13Ord")
    _run(p, "08[Create] :: Alpha")
    r = _run(p, "13[Loop]")
    _rec("W-ordinary bare Loop: requested 1, executed 1",
         r.get("ok") is True
         and any("requested 1, executed 1" in m for m in _msgs(r)),
         str(_msgs(r)))
    r = _run(p, "13[Loop] :: 99")
    _rec("W-ordinary 99: clamped to 5 with receipt (B2 regression)",
         r.get("ok") is True
         and any("requested 99, executed 5" in m
                 and "clamped to 1..5" in m for m in _msgs(r)),
         str(_msgs(r)))
    base = _pending(p)
    for label in ("abc", "2.5", "-3", "3" + SUPER2):
        try:
            r = _run(p, f"13[Loop] :: {label}")
            _rec(f"W-malformed {label!r}: refusal unchanged, zero growth",
                 r.get("ok") is False
                 and r.get("error") == "invalid_loop_count"
                 and _pending(p) == base,
                 f"{r.get('ok')} / {r.get('error')}")
        except Exception as e:
            _rec(f"W-malformed {label!r}: refusal unchanged, zero growth",
                 False, f"RAISED {type(e).__name__}: {e}")
    _cleanup("F13Ord")


def _siblings() -> None:
    p = _prog("F13Sib")
    _run(p, "08[Create] :: Alpha")
    try:
        r = _run(p, f"06[Cycle] :: {SUPER2}")
        _rec("W-cycle superscript: no crash, default x1 runs",
             r.get("ok") is True
             and any("Cycle x1" in m for m in _msgs(r)),
             f"{r.get('ok')} / {_msgs(r)}")
    except Exception as e:
        _rec("W-cycle superscript: no crash, default x1 runs", False,
             f"RAISED {type(e).__name__}: {e}")
    try:
        r = _run(p, f"06[Cycle] :: {'9' * 5000}")
        _rec("W-cycle oversized: no crash, default x1 runs",
             r.get("ok") is True
             and any("Cycle x1" in m for m in _msgs(r)),
             f"{r.get('ok')} / {_msgs(r)}")
    except Exception as e:
        _rec("W-cycle oversized: no crash, default x1 runs", False,
             f"RAISED {type(e).__name__}: {e}")
    try:
        r = _run(p, f"48[Macro] :: {SUPER2}")
        _rec("W-macro superscript label: no crash",
             r.get("ok") is True, f"{r.get('ok')} / {r.get('error')}")
    except Exception as e:
        _rec("W-macro superscript label: no crash", False,
             f"RAISED {type(e).__name__}: {e}")
    try:
        r = _run(p, f"16[Decay] :: {SUPER2}")
        _rec("W-decay superscript factor: no ValueError escape "
             "(gate verdict path)",
             r.get("error") != "ValueError"
             and not any("could not convert" in m for m in _msgs(r)),
             f"{r.get('ok')} / {r.get('error')} / {_msgs(r)}")
    except Exception as e:
        _rec("W-decay superscript factor: no ValueError escape "
             "(gate verdict path)", False,
             f"RAISED {type(e).__name__}: {e}")
    _cleanup("F13Sib")


def _chain() -> None:
    p = _prog("F13Chain")
    _run(p, "08[Create] :: Alpha")
    base = _pending(p)
    try:
        r = _run(p, f"08[Create] :: Beta > 13[Loop] :: {SUPER2}")
        loop_res = [a for a in r.get("atom_results") or []
                    if a.get("dell") == 13]
        _rec("W-chain: chained Loop superscript atom reports "
             "failed (not ok), zero growth",
             bool(loop_res) and loop_res[0].get("ok") is False
             and _pending(p) == base,
             str(loop_res)[:300])
    except Exception as e:
        _rec("W-chain: chained Loop superscript atom reports "
             "failed (not ok), zero growth", False,
             f"RAISED {type(e).__name__}: {e}")
    _cleanup("F13Chain")


def main() -> bool:
    _loop_refusals()
    _loop_ordinary()
    _siblings()
    _chain()
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"DIRF13_LOOP_COUNT: {passed}/{total}")
    return passed == total


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
