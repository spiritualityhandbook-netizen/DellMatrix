"""D1 reconciliation R3 — Match uses the shared predicate engine.

Director ruling 2026-10-29 (D1_TYPED_CONTRACT_RECONCILIATION,
exhibit #3): Dell 58 (Match) adopts the shared predicate
engine (_pred: case-insensitive substring OR
underscore-prefix) while preserving its current-selection
universe. This suite replaces circuit 13's divergence pin
with the corrected contract; the historical exhibit
evidence stays in that commit.

Corrected contract:
- Select("garden gate") then Match("garden gate") retains
  exactly the same IDs — one engine, one answer.
- Underscore and case behavior match the family engine.
- Empty pattern remains the identity; a nonmatching
  pattern remains a valid empty selection.
- The universe is STILL the current selection only:
  Match can narrow, never expand — an idea placed on the
  plane after selection is invisible to Match.
- The R2 cell contract is untouched: matched is bool,
  value carries the narrowed IDs, count the quantity.

House pattern: RESULTS + _rec; loud cleanup."""
import os
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
    owner = "D1Recon3"
    p = _program(owner)
    st = p.core_ii
    p.place("garden_gate", "Garden Gate")
    p.place("garden_path", "Garden Path")
    p.place("river_stone", "River Stone")

    # -- 1: the headline agreement — same phrase, same IDs
    _run(p, "51[Select] :: garden gate")
    via_select = list(st.selected)
    _run(p, "51[Select]")
    _run(p, "58[Match] :: garden gate")
    _rec("Select('garden gate') -> Match('garden gate') "
         "retains the same IDs",
         via_select == ["garden_gate"]
         and list(st.selected) == via_select,
         f"select={via_select} match={list(st.selected)}")

    # -- 2: family-engine behaviors
    _run(p, "51[Select]")
    _run(p, "58[Match] :: garden_gate")
    _rec("underscore pattern matches (substring leg)",
         list(st.selected) == ["garden_gate"], str(st.selected))
    _run(p, "51[Select]")
    _run(p, "58[Match] :: GARDEN GATE")
    _rec("uppercase spaced phrase matches (case-insensitive "
         "prefix leg)", list(st.selected) == ["garden_gate"],
         str(st.selected))
    _run(p, "51[Select]")
    _run(p, "58[Match] :: garden")
    _rec("plain substring still narrows as before",
         list(st.selected) == ["garden_gate", "garden_path"],
         str(st.selected))

    # -- 3: identity, nonmatch, and the R2 cell contract
    _run(p, "51[Select]")
    before = list(st.selected)
    _run(p, "58[Match]")
    _rec("empty pattern is still the identity",
         list(st.selected) == before, str(st.selected))
    r = _run(p, "58[Match] :: zzz")
    lr = st.last_result or {}
    _rec("nonmatching pattern is a valid empty selection "
         "with bool matched (R2 intact)",
         r.get("ok") and list(st.selected) == []
         and lr.get("matched") is False
         and lr.get("value") == [] and lr.get("count") == 0,
         str(lr))

    # -- 4: the universe is still the current selection
    _run(p, "51[Select] :: garden")
    p.place("garden_shed", "Garden Shed")
    _run(p, "58[Match] :: garden")
    _rec("no expansion beyond the selection: an idea "
         "placed on the plane afterwards is invisible",
         list(st.selected) == ["garden_gate", "garden_path"],
         str(st.selected))

    # -- 5: docs pins
    _rec("signature states the shared engine (58)",
         "SHARED predicate" in get_signature(58).output)
    _rec("proof card carries the R3 unification (58)",
         "SHARED predicate engine" in DEEP_NOTES[58])

    _cleanup(owner)
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_RECON3_MATCH_ENGINE: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
