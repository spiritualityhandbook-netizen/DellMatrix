"""D1 circuit 14 — Dell 68 (All) DEEP CONTRACT.

query_ops.py:apply_query n==68 arm (query cluster).
Contract: All reads the SELECTION with the shared predicate
engine and answers whether EVERY selected id matches.
value = matched = the hit (a real bool); count = selection
size; source "all". On an EMPTY selection All is True for
every predicate — VACUOUS TRUTH, the classical dual of
Dell 67's empty-False. A bare predicate matches everything,
so bare All is True on any selection. All is READ-ONLY.
Typed and label encodings agree. No English surface.
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
    owner = "D1Dell68"
    p = _program(owner)
    st = p.core_ii

    def allv(lab=None):
        _run(p, "68[All]" if lab is None else f"68[All] :: {lab}")
        lr = st.last_result or {}
        return lr.get("value"), lr.get("matched"), lr.get(
            "count"), lr.get("source")

    # -- 1: empty selection: vacuous truth, even for zzz
    _rec("empty selection: all(zzz) is True (vacuous)",
         allv("zzz") == (True, True, 0, "all"))
    _rec("empty selection: bare All is True",
         allv() == (True, True, 0, "all"))

    p.place("garden_gate", "Garden Gate")
    p.place("garden_path", "Garden Path")
    p.place("river_stone", "River Stone")
    _run(p, "51[Select]")

    # -- 2: every-match semantics
    _rec("all(garden) is False (welcome/river do not match)",
         allv("garden") == (False, False, 4, "all"))
    _rec("bare All is True (empty predicate matches all)",
         allv() == (True, True, 4, "all"))
    _run(p, "58[Match] :: garden")
    _rec("on a garden-only selection, all(garden) is True",
         allv("garden") == (True, True, 2, "all"))
    _rec("all(zzz) is False on a non-empty selection",
         allv("zzz") == (False, False, 2, "all"))

    # -- 3: read-only
    before = list(st.selected)
    allv("garden")
    _rec("All is read-only (selection untouched)",
         list(st.selected) == before, str(st.selected))

    # -- 4: typed encoding + no English surface
    r = _run(p, '68[All](predicate="garden")')
    _rec("typed All agrees with the label encoding",
         r.get("ok") is True and (st.last_result or {}).get(
             "value") is True, str(r.get("ok")))
    from form.mandell.translate import translate
    it = translate("all garden")
    _rec("no English surface ('all garden' -> Dell 9)",
         it.dell == 9, f"dell={it.dell}")

    # -- 5: REAL_USER_PATH: the REPL prints the quantifier
    owner2 = "D1Dell68Repl"
    _cleanup(owner2)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner2],
        input="51[Select]\n68[All] :: zzz\n",
        capture_output=True, text=True, cwd=_ROOT, timeout=120)
    _rec("REPL: all(zzz) on [welcome] prints 'All False n=1' "
         "(the single id does not match, so All is False)",
         proc.returncode == 0 and "All False n=1" in proc.stdout,
         (proc.stdout or "")[-200:])
    _cleanup(owner2)

    # -- 6: docs pins
    _rec("signature synced to the arm (70-74)",
         "apply_query:70-74" in get_signature(68).derived_from
         and "vacuous" in get_signature(68).output.lower())
    _rec("proof card carries the circuit-14 deep note",
         "vacuous" in DEEP_NOTES[68].lower())

    _cleanup(owner)
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_DELL68_ALL: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
