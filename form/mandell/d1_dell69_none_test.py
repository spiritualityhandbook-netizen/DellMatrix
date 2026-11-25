"""D1 circuit 14 — Dell 69 (None) DEEP CONTRACT.

query_ops.py:apply_query n==69 arm (query cluster).
Contract: None reads the SELECTION with the shared predicate
engine and answers whether NO selected id matches:
hit = not any(predicate hits). value = matched = the hit
(a real bool); count = selection size; source "none".
On an EMPTY selection None is True for every predicate.
None is the exact De Morgan dual of Dell 67: on every state,
None(lab) == not Any(lab). A bare predicate matches
everything, so bare None is True exactly when the selection
is empty — the Dell 69 signature's own description ("empty
checks empty selection"). None is READ-ONLY. Typed and
label encodings agree. No English surface. REAL_USER_PATH
REPL evidence included.

House pattern: RESULTS + _rec; loud cleanup."""
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from form.mandell.dell_cards import DEEP_NOTES          # noqa: E402
from form.mandell.signatures import get_signature        # noqa: E402

RESULTS = []


def _rec(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def _cleanup(owner):
    import glob
    import shutil
    state = os.path.join(_ROOT, "form", "state")
    pats = [f"program_{owner}.json", f"nursery_{owner}.json",
            f"checkpoint_{owner}.json",
            f"confirm_journal_{owner}.json",
            f"confirm_gen_{owner}.json",
            f"confirm_current_{owner}.json"]
    for pat in pats:
        for f in glob.glob(os.path.join(state, pat)):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
            except OSError as e:
                raise RuntimeError(f"cleanup failed for {f}: {e}")
    d = os.path.join(state, f"ideas_{owner}")
    if os.path.isdir(d):
        shutil.rmtree(d)


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


def main():
    owner = "D1Dell69"
    p = _program(owner)
    st = p.core_ii

    def nonev(lab=None):
        _run(p, "69[None]" if lab is None else f"69[None] :: {lab}")
        lr = st.last_result or {}
        return lr.get("value"), lr.get("matched"), lr.get(
            "count"), lr.get("source")

    def anyv(lab):
        _run(p, f"67[Any] :: {lab}")
        return (st.last_result or {}).get("value")

    # -- 1: empty selection: None is True, even bare
    _rec("empty selection: none(zzz) is True",
         nonev("zzz") == (True, True, 0, "none"))
    _rec("empty selection: bare None is True",
         nonev() == (True, True, 0, "none"))

    p.place("garden_gate", "Garden Gate")
    p.place("garden_path", "Garden Path")
    p.place("river_stone", "River Stone")
    _run(p, "51[Select]")

    # -- 2: no-match semantics
    _rec("none(zzz) is True (nothing matches)",
         nonev("zzz") == (True, True, 4, "none"))
    _rec("none(garden) is False (two match)",
         nonev("garden") == (False, False, 4, "none"))
    _rec("bare None on a non-empty selection is False",
         nonev() == (False, False, 4, "none"))

    # -- 3: De Morgan duality with Dell 67 across states
    dual = True
    for lab in ("garden", "gate", "zzz", "stone"):
        dual = dual and (nonev(lab)[0] == (not anyv(lab)))
    _rec("De Morgan: None(lab) == not Any(lab) on 4 states",
         dual)

    # -- 4: read-only + typed + no English surface
    before = list(st.selected)
    nonev("garden")
    _rec("None is read-only (selection untouched)",
         list(st.selected) == before, str(st.selected))
    r = _run(p, '69[None](predicate="zzz")')
    _rec("typed None agrees with the label encoding",
         r.get("ok") is True and (st.last_result or {}).get(
             "value") is True, str(r.get("ok")))
    from form.mandell.translate import translate
    it = translate("none garden")
    _rec("no English surface ('none garden' -> Dell 9)",
         it.dell == 9, f"dell={it.dell}")

    # -- 5: REAL_USER_PATH: the REPL prints the quantifier
    owner2 = "D1Dell69Repl"
    _cleanup(owner2)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner2],
        input="51[Select]\n69[None] :: zzz\n",
        capture_output=True, text=True, cwd=_ROOT, timeout=120)
    _rec("REPL: none(zzz) on [welcome] prints 'None True n=1'",
         proc.returncode == 0 and "None True n=1" in proc.stdout,
         (proc.stdout or "")[-200:])
    _cleanup(owner2)

    # -- 6: docs pins
    _rec("signature synced to the arm (75-79)",
         "apply_query:75-79" in get_signature(69).derived_from
         and "De Morgan" in get_signature(69).output)
    _rec("proof card carries the circuit-14 deep note",
         "de morgan" in DEEP_NOTES[69].lower())

    _cleanup(owner)
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_DELL69_NONE: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
