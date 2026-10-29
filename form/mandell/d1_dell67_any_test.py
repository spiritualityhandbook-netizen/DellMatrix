"""D1 circuit 14 — Dell 67 (Any) DEEP CONTRACT.

query_ops.py:apply_query n==67 arm (query cluster).
Contract: Any reads the SELECTION with the shared predicate
engine and answers whether AT LEAST ONE selected id matches.
value = matched = the hit (a real bool); count = selection
size; source "any". On an EMPTY selection Any is False for
every predicate, including a bare one. The bare predicate on
a non-empty selection is True (the predicate engine matches
everything, so Any-with-no-predicate answers "is the
selection non-empty" — the Dell 67 signature's own
description). Any is READ-ONLY: the selection is never
mutated. Typed and label encodings agree. No English surface
("any garden" becomes the Dell 9 question intent).
REAL_USER_PATH REPL evidence included.

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
    from form.open import Program  # noqa: F401  (owner isolation)
    owner = "D1Dell67"
    p = _program(owner)
    st = p.core_ii

    def anyv(lab=None):
        _run(p, "67[Any]" if lab is None else f"67[Any] :: {lab}")
        lr = st.last_result or {}
        return lr.get("value"), lr.get("matched"), lr.get(
            "count"), lr.get("source")

    # -- 1: empty selection: Any is False, even bare
    v = anyv("zzz")
    _rec("empty selection: any(zzz) is False", v == (
        False, False, 0, "any"), str(v))
    v2 = anyv()
    _rec("empty selection: bare Any is False", v2 == (
        False, False, 0, "any"), str(v2))

    p.place("garden_gate", "Garden Gate")
    p.place("garden_path", "Garden Path")
    p.place("river_stone", "River Stone")
    _run(p, "51[Select]")

    # -- 2: at-least-one semantics
    _rec("any(garden) is True (two of four match)",
         anyv("garden") == (True, True, 4, "any"))
    _rec("any(gate) is True (one match suffices)",
         anyv("gate") == (True, True, 4, "any"))
    _rec("any(zzz) is False (no match)",
         anyv("zzz") == (False, False, 4, "any"))
    _rec("bare Any on a non-empty selection is True",
         anyv() == (True, True, 4, "any"))

    # -- 3: read-only + De Morgan partner (69) agreement
    before = list(st.selected)
    anyv("garden")
    _rec("Any is read-only (selection untouched)",
         list(st.selected) == before, str(st.selected))
    _run(p, "69[None] :: garden")
    none_hit = (st.last_result or {}).get("value")
    _rec("De Morgan: None(garden) == not Any(garden)",
         none_hit is False, str(none_hit))
    _run(p, "69[None] :: zzz")
    none_hit2 = (st.last_result or {}).get("value")
    _rec("De Morgan: None(zzz) == not Any(zzz)",
         none_hit2 is True, str(none_hit2))

    # -- 4: typed encoding + no English surface
    r = _run(p, '67[Any](predicate="gate")')
    _rec("typed Any agrees with the label encoding",
         r.get("ok") is True and (st.last_result or {}).get(
             "value") is True, str(r.get("ok")))
    from form.mandell.translate import translate
    it = translate("any garden")
    _rec("no English surface ('any garden' -> Dell 9)",
         it.dell == 9, f"dell={it.dell}")

    # -- 5: REAL_USER_PATH: the REPL prints the quantifier
    owner2 = "D1Dell67Repl"
    _cleanup(owner2)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner2],
        input="51[Select]\n67[Any] :: wel\n",
        capture_output=True, text=True, cwd=_ROOT, timeout=120)
    _rec("REPL: select then any prints 'Any True n=1'",
         proc.returncode == 0 and "Any True n=1" in proc.stdout,
         (proc.stdout or "")[-200:])
    _cleanup(owner2)

    # -- 6: docs pins
    _rec("signature synced to the arm (65-69)",
         "apply_query:65-69" in get_signature(67).derived_from
         and "empty selection" in get_signature(67).output)
    _rec("proof card carries the circuit-14 deep note",
         "at least one" in DEEP_NOTES[67].lower())

    _cleanup(owner)
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_DELL67_ANY: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
