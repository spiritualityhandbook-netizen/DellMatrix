"""D1 reconciliation R1 — Scope is a real boundary (51/53).

Director ruling 2026-10-29 (D1_TYPED_CONTRACT_RECONCILIATION,
exhibit #1): implement actual selection filtering. This
suite replaces circuit 9's defect-preserving pin
("scope_is_a_label_not_a_filter") with the corrected
contract; the historical exhibit evidence stays in the
circuit-9 commit.

Corrected contract:
- Supported scope names are defined explicitly: "plane"
  (the whole plane — the default, and what a bare Dell 53
  restores) or the name of an EXISTING group (Dell 82).
- Dell 53 refuses an unknown scope name
  (scope_unknown:{name}, ok=False) and leaves the current
  scope unchanged. It never silently widens.
- Dell 51's universe is scope-bound: under a group scope,
  Select ranges over the group's membership intersected
  with the plane in plane order — outsiders are excluded
  even when the predicate would match them, and a
  predicate can narrow within the scope but never widen
  past it.
- A dangling scope (scope state naming no supported
  scope, e.g. after its group is ungrouped or from a
  stale save) makes Select refuse with scope_unknown —
  fail-closed, never a silent whole-plane selection.
- Ungrouping the active scope group warns in its message.
- The contract survives save/load: scope and groups are
  core_ii durable state; after Program.load, the scoped
  Select still excludes outsiders.

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
    owner = "D1Recon1"
    p = _program(owner)
    st = p.core_ii

    # Two disjoint families of ideas.
    for uid, label in [("flora_fern", "Flora Fern"),
                       ("flora_rose", "Flora Rose"),
                       ("ore_iron", "Ore Iron"),
                       ("ore_copper", "Ore Copper")]:
        p.place(uid, label)

    # -- 1: default plane behavior is explicit
    _rec("fresh scope is 'plane' (the explicit default)",
         st.scope == "plane", st.scope)
    _run(p, "51[Select]")
    _rec("under plane, bare Select ranges over the whole plane",
         st.selected == ["welcome", "flora_fern", "flora_rose",
                         "ore_iron", "ore_copper"],
         str(st.selected))

    # Build two disjoint groups from selections.
    _run(p, "51[Select] :: flora")
    _run(p, "82[Group] :: greens")
    _run(p, "51[Select] :: ore")
    _run(p, "82[Group] :: metals")
    _rec("two disjoint groups built from selections",
         st.groups.get("greens") == ["flora_fern", "flora_rose"]
         and st.groups.get("metals") == ["ore_iron", "ore_copper"],
         str(st.groups))

    # -- 2: a group scope excludes outsiders
    _run(p, "53[Scope] :: greens")
    _run(p, "51[Select]")
    _rec("scoped bare Select returns exactly the group members",
         st.selected == ["flora_fern", "flora_rose"],
         str(st.selected))
    _run(p, "51[Select] :: ore")
    _rec("a predicate cannot widen past the scope (ore under "
         "greens selects nothing)",
         st.selected == [], str(st.selected))
    _run(p, "51[Select] :: flora")
    _rec("a predicate narrows within the scope",
         st.selected == ["flora_fern", "flora_rose"],
         str(st.selected))
    _run(p, "53[Scope] :: metals")
    _run(p, "51[Select]")
    _rec("switching scope switches the universe",
         st.selected == ["ore_iron", "ore_copper"],
         str(st.selected))

    # -- 3: invalid scope refuses at set time
    r = _run(p, "53[Scope] :: nowhere")
    _rec("Dell 53 refuses an unknown scope, scope unchanged",
         r.get("ok") is False
         and "scope_unknown:nowhere" in str(r.get("error"))
         and st.scope == "metals",
         f"ok={r.get('ok')} err={r.get('error')} scope={st.scope}")

    # -- 4: a dangling scope refuses at select time (fail-closed)
    _run(p, "83[Ungroup] :: metals")
    r = _run(p, "51[Select]")
    _rec("after ungrouping the active scope, Select refuses "
         "(never silently widens to the plane)",
         r.get("ok") is False
         and "scope_unknown:metals" in str(r.get("error")),
         f"ok={r.get('ok')} err={r.get('error')}")
    msgs = r.get("messages") or []
    _rec("the refusal names the dangling scope",
         any("scope_unknown:metals" in m for m in msgs),
         str(msgs))
    _run(p, "53[Scope]")
    _rec("a bare Dell 53 restores the plane default explicitly",
         st.scope == "plane", st.scope)
    _run(p, "51[Select]")
    _rec("Select works again over the whole plane",
         len(st.selected) == 5, str(st.selected))

    # -- 5: the contract survives save/load
    _run(p, "53[Scope] :: greens")
    _run(p, "10[Save]")
    from form.open import Program
    p2 = Program.load(owner=owner)
    st2 = p2.core_ii
    _rec("scope and groups survive save/load",
         st2.scope == "greens"
         and st2.groups.get("greens") == ["flora_fern",
                                          "flora_rose"],
         f"scope={st2.scope}")
    _run(p2, "51[Select]")
    _rec("after load, scoped Select still excludes outsiders",
         list(st2.selected) == ["flora_fern", "flora_rose"],
         str(st2.selected))

    # -- 6: membership is plane-intersected (stale members drop)
    _run(p, "53[Scope] :: greens")
    st.groups["greens"] = ["flora_fern", "ghost_idea"]
    _run(p, "51[Select]")
    _rec("group members absent from the plane drop out of the "
         "universe (canonical plane membership governs)",
         st.selected == ["flora_fern"], str(st.selected))

    # -- 7: docs pins
    sig = get_signature(51)
    _rec("Dell 51 signature states the scope-bound universe",
         "scope-bound" in sig.output
         and "scope_unknown" in sig.failures)
    _rec("proof cards carry the R1 notes for 51 and 53",
         "scope" in DEEP_NOTES[51].lower()
         and "filter" in DEEP_NOTES[51].lower()
         and "scope_unknown" in DEEP_NOTES[53])

    _cleanup(owner)
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_RECON1_SCOPE: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
