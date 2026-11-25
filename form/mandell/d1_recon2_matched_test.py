"""D1 reconciliation R2 — matched is a Boolean (54/58).

Director ruling 2026-10-29 (D1_TYPED_CONTRACT_RECONCILIATION,
exhibit #2): standardize on Boolean. Keep hit IDs in the
existing value list and quantity in count; no duplicate
hits field. This suite replaces circuits 10/13's
defect-preserving list pins with the corrected contract;
the historical exhibit evidence stays in those commits.

Corrected contract:
- Dell 54 (Query): matched = bool(hits) — an exact bool,
  True/False, for nonempty AND empty results. value still
  carries the hit IDs; count the quantity; confidence
  still 1.0/0.0. Query remains READ-ONLY.
- Dell 58 (Match): matched = bool(narrowed selection);
  value carries the narrowed IDs; Match still UPDATES
  the selection (the R2 change is the cell type only —
  the engine unification is R3's separate repair).
- Family consistency: the query-family cells (51, 54,
  58, 67, 68, 69) now all publish bool matched, matching
  result_cell's own default type.
- Consumer compatibility: Compare's last_result
  resolution reads the Query cell correctly, and the
  cell survives a JSON round-trip with its type intact.
- Persistence compatibility: save/load preserves the
  selection the cells describe, and a Query issued after
  load publishes the identical cell shape.

House pattern: RESULTS + _rec; loud cleanup."""
import json
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
    owner = "D1Recon2"
    p = _program(owner)
    st = p.core_ii
    p.place("garden_gate", "Garden Gate")
    p.place("garden_path", "Garden Path")
    p.place("river_stone", "River Stone")
    _run(p, "51[Select]")

    # -- 1: Query — exact Boolean type, both directions
    _run(p, "54[Query] :: garden")
    lr = st.last_result or {}
    _rec("Query nonempty: matched is exactly bool True",
         type(lr.get("matched")) is bool
         and lr.get("matched") is True, repr(lr.get("matched")))
    _rec("Query nonempty: IDs stay in value, quantity in count",
         lr.get("value") == ["garden_gate", "garden_path"]
         and lr.get("count") == 2, str(lr.get("value")))
    sel_before = list(st.selected)
    _run(p, "54[Query] :: zzz")
    lr = st.last_result or {}
    _rec("Query empty: matched is exactly bool False",
         type(lr.get("matched")) is bool
         and lr.get("matched") is False
         and lr.get("value") == [] and lr.get("count") == 0,
         repr(lr.get("matched")))
    _rec("Query remains read-only under the new cell type",
         list(st.selected) == sel_before, str(st.selected))

    # -- 2: Match — exact Boolean type; selection still updates
    _run(p, "58[Match] :: garden")
    lr = st.last_result or {}
    _rec("Match nonempty: matched is exactly bool True, "
         "value carries the narrowed IDs",
         type(lr.get("matched")) is bool
         and lr.get("matched") is True
         and lr.get("value") == ["garden_gate", "garden_path"]
         and lr.get("count") == 2, repr(lr.get("matched")))
    _rec("Match still updates the selection (R2 changed the "
         "cell type only)",
         list(st.selected) == ["garden_gate", "garden_path"],
         str(st.selected))
    _run(p, "58[Match] :: zzz")
    lr = st.last_result or {}
    _rec("Match empty: matched is exactly bool False",
         type(lr.get("matched")) is bool
         and lr.get("matched") is False
         and lr.get("value") == [] and lr.get("count") == 0,
         repr(lr.get("matched")))

    # -- 3: family consistency — every query-family cell is bool
    _run(p, "51[Select]")
    fam = {}
    for seed in ("51[Select] :: garden", "52[Filter] :: gate",
                 "54[Query] :: garden",
                 "67[Any] :: garden", "68[All] :: garden",
                 "69[None] :: zzz"):
        _run(p, seed)
        fam[seed] = type((st.last_result or {}).get(
            "matched")) is bool
    _rec("query-family cells (51/52/54/67/68/69) all publish "
         "bool matched", all(fam.values()), str(fam))

    # -- 4: consumer compatibility
    _run(p, "54[Query] :: garden")
    cell = dict(st.last_result or {})
    rt = json.loads(json.dumps(cell))
    _rec("the Query cell survives a JSON round-trip with "
         "matched still bool",
         type(rt.get("matched")) is bool
         and rt.get("matched") is True)
    _run(p, "57[Compare] :: eq: last_result true")
    lr = st.last_result or {}
    _rec("Compare reads the Query cell via last_result "
         "(consumer compatibility)",
         lr.get("value") is True, str(lr))

    # -- 5: persistence compatibility
    _run(p, "51[Select]")
    _run(p, "10[Save]")
    from form.open import Program
    p2 = Program.load(owner=owner)
    st2 = p2.core_ii
    _run(p2, "54[Query] :: garden")
    lr2 = st2.last_result or {}
    _rec("after save/load, Query publishes the identical "
         "cell (bool matched, same value/count)",
         type(lr2.get("matched")) is bool
         and lr2.get("matched") is True
         and lr2.get("value") == ["garden_gate", "garden_path"]
         and lr2.get("count") == 2, str(lr2))

    # -- 6: docs pins
    _rec("signatures state the Boolean standard (54 + 58)",
         "Boolean" in get_signature(54).output
         and "Boolean" in get_signature(58).output)
    _rec("proof cards carry the R2 standardization (54 + 58)",
         "Boolean" in DEEP_NOTES[54]
         and "Boolean" in DEEP_NOTES[58])

    _cleanup(owner)
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_RECON2_MATCHED: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
