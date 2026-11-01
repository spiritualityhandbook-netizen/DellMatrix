"""STEP 10 — consistency circuit: B11 Resolve, B12 Ungroup, B18 Compose.

Contracts proven here, through the public seed path
(form.mandell.executor.execute_seed) on a real Program, plus
direct registry.lookup witnesses for the shared-authority
hardening:

- B11 Resolve resolves its LABEL against the active registry
  (dells 0-99), never Resolve's own term via the manifest
  fallback. Hit: value=canonical name, matched=True,
  confidence=1.00, message carries the dell number. Miss
  (unknown, reserved, digit-like crash-bait): value=None,
  matched=False, confidence=0.00, error="missing". Bare:
  error="target_required". Atom ok stays True on hits and
  misses alike (Get 56 precedent — the cell carries the
  outcome). No label ever raises, never conf 0.40, never
  matched=True on a miss.
- registry.lookup hardening converts crashes into None and
  changes NO previously-successful resolution (ASCII digits
  with leading zeros, names, NAMED aliases unchanged).
- B12 Ungroup: a NAMED missing group refuses
  ok=False err=ungroup_missing:<name> with zero mutation;
  bare with no groups refuses ungroup_missing:empty; an
  existing EMPTY group ungroups ok=True released=0 (distinct
  from missing); populated ungroup adopts members into an
  empty selection; bare ungroups the last group; the active
  scope-group warning + Select scope_unknown contract
  survives; the refusal inside Try marks the frame failed
  (B15 hook) and Catch consumes it.
- B18 Compose: publication is run-before-publish. A failed
  define-run stores NOTHING and keeps the run's error; a
  failed redefinition RETAINS the prior body; messages state
  "not published" / "previous definition retained" and never
  imply rollback; a valid (re)definition publishes; a
  self-referencing redefinition stays compose_cycle with the
  prior body retained; Try + Revert still governs
  compositions via the established checkpoint contract.

Probe note: the failing-first probe's W-C2 line expected the
retained body string "55[Set] :: kk=vv" where its own setup
had stored "82[Group]" — a probe typo, verified first-hand
(post-fix run: comps={'keep': '82[Group]'} retained). This
suite asserts the setup's actual body.

Labels: INTEGRATION / PUBLIC_ENTRY (real Program).
"""
from __future__ import annotations

import glob
import os
import shutil

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
                f"confirm_current_{owner}.json",
                f"exchange_journal_{owner}.json"):
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


def _run(prog, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(prog, seed)


def _msgs(r):
    return [m for m in r.get("messages", [])
            if not m.startswith(("Mandell:", "English:",
                                 "Chain atoms=", "-- "))]


def _cell(p):
    return dict(p.core_ii.last_result or {})


def _hit(p, value):
    lr = _cell(p)
    return (lr.get("value") == value and lr.get("matched") is True
            and abs(float(lr.get("confidence") or 0) - 1.0) < 1e-9
            and not lr.get("error"))


def _miss(p, error="missing"):
    lr = _cell(p)
    return (lr.get("value") is None and lr.get("matched") is False
            and float(lr.get("confidence") or 0) == 0.0
            and lr.get("error") == error)


def _resolve() -> None:
    p = _prog("Step10Res")
    st = p.core_ii
    r = _run(p, "76[Resolve] :: Select")
    _rec("R1 Resolve :: Select -> Select conf 1.00 matched=True, atom ok",
         r.get("ok") is True and _hit(p, "Select"), str(_cell(p)))
    r = _run(p, "76[Resolve] :: 51")
    _rec("R2 Resolve :: 51 -> Select conf 1.00",
         r.get("ok") is True and _hit(p, "Select"), str(_cell(p)))
    r = _run(p, "76[Resolve] :: 076")
    _rec("R3 Resolve :: 076 (leading zeros) -> Resolve dell 76 hit",
         r.get("ok") is True and _hit(p, "Resolve")
         and any("dell=76" in m for m in _msgs(r)),
         f"{_cell(p)} / {_msgs(r)}")
    r = _run(p, "76[Resolve] :: sElEcT")
    _rec("R4 Resolve :: sElEcT (mixed case) -> Select hit",
         _hit(p, "Select"), str(_cell(p)))
    r = _run(p, "76[Resolve] :: Bindell")
    _rec("R5 Resolve :: Bindell (NAMED alias) -> Bind dell 14 hit",
         _hit(p, "Bind") and any("dell=14" in m for m in _msgs(r)),
         f"{_cell(p)} / {_msgs(r)}")
    r = _run(p, "76[Resolve] :: Loop")
    _rec("R6 Resolve :: Loop (CORE_I name) -> Loop hit",
         _hit(p, "Loop"), str(_cell(p)))
    r = _run(p, "76[Resolve] :: bogusname")
    _rec("R7 Resolve :: bogusname -> honest miss, atom still ok",
         r.get("ok") is True and _miss(p), str(_cell(p)))
    r = _run(p, "76[Resolve]")
    _rec("R8 bare Resolve -> target_required miss",
         r.get("ok") is True and _miss(p, "target_required"),
         str(_cell(p)))
    r = _run(p, "76[Resolve] :: 151")
    _rec("R9 Resolve :: 151 (reserved) -> honest miss, not a hit",
         _miss(p), str(_cell(p)))
    r = _run(p, "76[Resolve] :: 999")
    _rec("R10 Resolve :: 999 (reserved) -> honest miss",
         _miss(p), str(_cell(p)))
    r = _run(p, "76[Resolve] :: Select trailing words")
    _rec("R11 Resolve :: 'Select trailing words' -> clean miss, no crash",
         _miss(p), str(_cell(p)))
    try:
        r = _run(p, "76[Resolve] :: ²")
        _rec("R12 Resolve :: superscript-two -> miss, never ValueError",
             _miss(p), str(_cell(p)))
    except Exception as e:  # noqa: BLE001 - witness, not handler
        _rec("R12 Resolve :: superscript-two -> miss, never ValueError",
             False, f"raised {type(e).__name__}: {e}")
    try:
        r = _run(p, "76[Resolve] :: " + "9" * 5000)
        _rec("R13 Resolve :: 5000-digit label -> miss, never ValueError",
             _miss(p), str(_cell(p)))
    except Exception as e:  # noqa: BLE001
        _rec("R13 Resolve :: 5000-digit label -> miss, never ValueError",
             False, f"raised {type(e).__name__}: {e}")
    # Chain agreement: the cell after a chain ending in Resolve
    # is Resolve's cell (consumers read the cell, step 3c).
    r = _run(p, "55[Set] :: kk=vv > 56[Get] :: kk > 76[Resolve] :: Select")
    lr = _cell(p)
    _rec("R14 chain Get > Resolve: last_result cell is Resolve's hit",
         r.get("ok") is True and lr.get("source") == "resolve"
         and _hit(p, "Select"), str(lr))
    _cleanup("Step10Res")


def _lookup() -> None:
    from form.mandell.registry import lookup
    try:
        v = lookup("²")
        _rec("L1 lookup(superscript-two) -> None, never ValueError",
             v is None, str(v))
    except Exception as e:  # noqa: BLE001
        _rec("L1 lookup(superscript-two) -> None, never ValueError",
             False, f"raised {type(e).__name__}: {e}")
    try:
        v = lookup("9" * 5000)
        _rec("L2 lookup(5000 digits) -> None, never ValueError",
             v is None, str(v))
    except Exception as e:  # noqa: BLE001
        _rec("L2 lookup(5000 digits) -> None, never ValueError",
             False, f"raised {type(e).__name__}: {e}")
    _rec("L3 lookup unchanged: 'Select'/'51'/'076'/'Bindell'/'Loop'",
         lookup("Select", )["dell"] == 51
         and lookup("51")["dell"] == 51
         and lookup("076")["dell"] == 76
         and lookup("Bindell")["dell"] == 14
         and lookup("Loop")["dell"] == 13,
         str([lookup(x) for x in ("Select", "51", "076")]))


def _ungroup() -> None:
    p = _prog("Step10Ung")
    st = p.core_ii
    st.groups["other"] = ["x"]
    before = {k: list(v) for k, v in st.groups.items()}
    r = _run(p, "83[Ungroup] :: nosuchgroup")
    _rec("U1 Ungroup missing name -> ok=False ungroup_missing, zero mutation",
         r.get("ok") is False
         and r.get("error") == "ungroup_missing:nosuchgroup"
         and st.groups == before,
         f"{r.get('ok')} / {r.get('error')} / {st.groups}")
    st.groups["emptyg"] = []
    r = _run(p, "83[Ungroup] :: emptyg")
    _rec("U2 Ungroup existing EMPTY group -> ok=True released=0, group gone",
         r.get("ok") is True and "emptyg" not in st.groups
         and any("released=0" in m for m in _msgs(r)),
         f"{r.get('ok')} / {_msgs(r)}")
    st.groups["popg"] = ["a", "b"]
    st.selected = []
    r = _run(p, "83[Ungroup] :: popg")
    _rec("U3 Ungroup populated -> members adopt empty selection",
         r.get("ok") is True and "popg" not in st.groups
         and st.selected == ["a", "b"],
         f"{r.get('ok')} / {st.selected}")
    st.groups["first"] = ["1"]
    st.groups["lastg"] = ["2"]
    r = _run(p, "83[Ungroup]")
    _rec("U4 bare Ungroup -> last group released",
         r.get("ok") is True and "lastg" not in st.groups
         and "first" in st.groups,
         f"{r.get('ok')} / {st.groups}")
    _cleanup("Step10Ung")

    p = _prog("Step10UngBare")
    st = p.core_ii
    r = _run(p, "83[Ungroup]")
    _rec("U5 bare Ungroup with NO groups -> ungroup_missing:empty",
         r.get("ok") is False
         and r.get("error") == "ungroup_missing:empty",
         f"{r.get('ok')} / {r.get('error')}")
    _cleanup("Step10UngBare")

    p = _prog("Step10UngScope")
    st = p.core_ii
    st.groups["g1"] = ["a"]
    _run(p, "53[Scope] :: g1")
    r = _run(p, "83[Ungroup] :: g1")
    _rec("U6 Ungroup active scope group -> ok, warning issued",
         r.get("ok") is True
         and any("now undefined" in m for m in _msgs(r)),
         str(_msgs(r)))
    r = _run(p, "51[Select]")
    _rec("U7 Select after scope-group ungroup refuses scope_unknown",
         r.get("ok") is False
         and r.get("error") == "scope_unknown:g1",
         f"{r.get('ok')} / {r.get('error')}")
    _cleanup("Step10UngScope")

    p = _prog("Step10UngTry")
    st = p.core_ii
    _run(p, "93[Try]")
    r = _run(p, "83[Ungroup] :: nosuchgroup")
    f = st.tx[-1]
    _rec("U8 Ungroup refusal inside Try marks frame failed (B15 hook)",
         r.get("ok") is False and f.get("status") == "failed"
         and f.get("error") == "ungroup_missing:nosuchgroup",
         str(f))
    r = _run(p, "94[Catch]")
    _rec("U9 Catch consumes the ungroup_missing root cause",
         _msgs(r) == ["Catch ungroup_missing:nosuchgroup"]
         and st.tx[-1].get("status") == "caught",
         f"{_msgs(r)} / {st.tx[-1]}")
    _cleanup("Step10UngTry")


def _compose() -> None:
    p = _prog("Step10Cmp")
    st = p.core_ii
    r = _run(p, "99[Compose] :: badone=89[Diff]")
    _rec("C1 failing define-run -> ok=False, name NOT stored, "
         "message says not published",
         r.get("ok") is False and r.get("error") == "baseline_missing"
         and "badone" not in st.compositions
         and any("not published" in m for m in _msgs(r)),
         f"{r.get('ok')} / {r.get('error')} / {st.compositions} / {_msgs(r)}")
    r = _run(p, "99[Compose] :: good=70[Count]")
    _rec("C2 valid define -> ok=True, stored",
         r.get("ok") is True
         and st.compositions.get("good") == "70[Count]",
         f"{r.get('ok')} / {st.compositions}")
    r = _run(p, "99[Compose] :: good=89[Diff]")
    _rec("C3 failing REdefinition -> prior body retained, "
         "message says so, no rollback language",
         r.get("ok") is False
         and st.compositions.get("good") == "70[Count]"
         and any("previous definition retained" in m for m in _msgs(r))
         and not any("rollback" in m.lower() or "revert" in m.lower()
                     for m in _msgs(r)),
         f"{r.get('ok')} / {st.compositions} / {_msgs(r)}")
    r = _run(p, "99[Compose] :: good=82[Group]")
    _rec("C4 valid redefinition -> body replaced",
         r.get("ok") is True
         and st.compositions.get("good") == "82[Group]",
         f"{r.get('ok')} / {st.compositions}")
    r = _run(p, "99[Compose] :: good=good")
    _rec("C5 self-referencing redefinition -> compose_cycle, prior retained",
         r.get("ok") is False and r.get("error") == "compose_cycle"
         and st.compositions.get("good") == "82[Group]",
         f"{r.get('ok')} / {r.get('error')} / {st.compositions}")
    r = _run(p, "99[Compose] :: selfy=selfy")
    _rec("C6 self-reference define -> compose_cycle, nothing stored",
         r.get("ok") is False and r.get("error") == "compose_cycle"
         and "selfy" not in st.compositions,
         f"{r.get('ok')} / {r.get('error')} / {st.compositions}")
    _cleanup("Step10Cmp")

    p = _prog("Step10CmpTx")
    st = p.core_ii
    _run(p, "99[Compose] :: keep=70[Count]")
    _run(p, "93[Try]")
    _run(p, "99[Compose] :: keep=82[Group]")
    _rec("C7 inside Try: valid redefinition published (checkpoint taken)",
         st.compositions.get("keep") == "82[Group]",
         str(st.compositions))
    _run(p, "96[Revert]")
    _rec("C8 Revert restores compositions to the Try checkpoint",
         st.compositions.get("keep") == "70[Count]",
         str(st.compositions))
    _cleanup("Step10CmpTx")


def main() -> bool:
    _resolve()
    _lookup()
    _ungroup()
    _compose()
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"STEP10_CONSISTENCY: {passed}/{total}")
    return passed == total


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
