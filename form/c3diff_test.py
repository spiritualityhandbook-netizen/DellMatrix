"""C3.Diff — DD-51 Rings 1+2 (Ace ruling SS12.79c; Director
routing mail 1a1cb46c70141e21).

Contracts proven here, through the public seed path
(form.mandell.executor.execute_seed) on a real Program:

- RING 1: every content writer passes through the ONE
  _note_mutation door (spectrum_ops), capturing the _ckpt
  pre-state after refusal checks and immediately before its
  mutation: Weight (74), Normalize (75), Cause (78),
  Depend (79), Context (80), Reference (81), Group (82),
  Ungroup (83), Define (97), Alias (98), and the
  chain-layer flow writers of refs/context/route in
  chain_exec._apply_flow. ONE DOCUMENTED EXCLUSION:
  Compose's publication write (99) does not note —
  noting it makes Diff-bodied define-runs self-fulfilling
  and breaks B18's pinned suites (step10_consistency,
  define_compose_nonpublication); the publication is
  still reported by Diff(compositions) inside the
  standing baseline window. A REFUSED writer (non-
  finite Weight, duplicate Cause, missing Ungroup, missing
  Alias) captures nothing and mutates nothing.
- RING 2: Dell 89 Diff is aimed by a SCOPE WORD in its
  label (exact-match vocabulary): no word / "store" is the
  legacy store-only comparison, byte-identical in its
  legacy keys and message; a content-slice word compares
  that slice; "all" compares every content slice; "whole"
  (or "checkpoint") compares the whole _ckpt frame incl.
  working slices and verdicts. The widened receipt is
  ADDITIVE: legacy before/after/changed keep store
  semantics; new keys scope / slices / unexamined name
  what was compared and what was NOT examined — never
  silently skipped. An unmatched non-empty label refuses
  diff_scope_unknown and writes no last_diff.
- HONESTY (frozen): no baseline -> baseline_missing for
  EVERY scope; baseline stays session-only; last-move
  only, no archive.
- PRESERVED SEMANTICS (evidence over inventory recs):
  step9_diff_test pins that in-frame notes set the
  standalone baseline and that a frame Revert leaves it
  governing; _note_mutation therefore keeps its current
  unconditional shape, and Revert does not invalidate the
  baseline. This suite re-pins both behaviors per-slice.

Labels: INTEGRATION / PUBLIC_ENTRY (real Program via
form.open.Program, public executor).
"""
from __future__ import annotations

import glob
import os
import shutil
import sys

RESULTS: list = []

CONTENT = ["store", "weights", "groups", "refs", "causes",
           "deps", "defs", "aliases", "compositions"]
WORKING = ["scope", "selected", "context", "route",
           "last_assert", "last_guard"]


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


def _program(owner: str):
    _cleanup(owner)
    from form.open import Program
    prog = Program(owner=owner)
    from form.mandell.core_ii_exec import attach
    attach(prog)
    return prog


def _run(prog, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(prog, seed)


def _msgs(r):
    return [m for m in r.get("messages", [])
            if not m.startswith(("Mandell:", "English:",
                                 "Chain atoms=", "-- "))]


def _slices(st):
    return (st.last_diff or {}).get("slices") or {}


def main() -> bool:
    # ============ RING 2 legacy preservation ============
    owner = "C3DiffLegacy"
    p = _program(owner)
    st = p.core_ii
    _run(p, "55[Set] :: a=1")
    r = _run(p, "89[Diff]")
    ld = st.last_diff
    _rec("legacy bare Diff: store keys + message byte-"
         "identical, widened keys additive (scope/slices/"
         "unexamined naming the other slices)",
         r.get("ok") is True
         and _msgs(r) == ["Diff changed=['a'] "
                          "baseline=immediate"]
         and ld.get("before") == {}
         and ld.get("after") == {"a": "1"}
         and ld.get("changed") == ["a"]
         and ld.get("label") == ""
         and ld.get("baseline") == "immediate"
         and ld.get("scope") == "store"
         and _slices(st).get("store", {}).get("changed") == ["a"]
         and sorted(ld.get("unexamined") or []) ==
         sorted([s for s in CONTENT + WORKING if s != "store"]),
         str(ld))
    r = _run(p, "89[Diff] :: store")
    _rec("explicit 'store' scope word == legacy bare Diff",
         r.get("ok") is True
         and st.last_diff.get("changed") == ["a"]
         and st.last_diff.get("scope") == "store"
         and _msgs(r) == ["Diff changed=['a'] "
                          "baseline=immediate"],
         str(st.last_diff))
    _cleanup(owner)

    # ============ baseline_missing for EVERY scope =====
    owner = "C3DiffMissing"
    p = _program(owner)
    st = p.core_ii
    missing_ok = True
    detail = ""
    for word, canon in (("weights", "weights"),
                        ("refs", "refs"),
                        ("all", "all"),
                        ("whole", "whole"),
                        ("store", "store")):
        r = _run(p, f"89[Diff] :: {word}")
        good = (r.get("ok") is False
                and r.get("error") == "baseline_missing"
                and st.last_diff.get("baseline") == "missing"
                and st.last_diff.get("available") is False
                and st.last_diff.get("changed") is None
                and st.last_diff.get("scope") == canon)
        if not good:
            missing_ok = False
            detail = f"{word}: {st.last_diff}"
    _rec("baseline_missing refuses EVERY scope on a fresh "
         "program, scope named in the receipt",
         missing_ok, detail)
    _cleanup(owner)

    # ============ unknown scope word refuses ============
    owner = "C3DiffUnknownScope"
    p = _program(owner)
    st = p.core_ii
    _run(p, "55[Set] :: a=1")
    _run(p, "89[Diff]")
    known = dict(st.last_diff)
    base_obj = st.diff_baseline
    r = _run(p, "89[Diff] :: bogus")
    _rec("unknown scope word refuses diff_scope_unknown, "
         "writes no last_diff, moves no baseline",
         r.get("ok") is False
         and r.get("error") == "diff_scope_unknown:bogus"
         and st.last_diff == known
         and st.diff_baseline is base_obj,
         str((r.get("error"), st.last_diff)))
    _cleanup(owner)

    # ============ RING 1: Weight (74) ==================
    owner = "C3DiffWeight"
    p = _program(owner)
    st = p.core_ii
    _run(p, "74[Weight] :: k=2")
    r = _run(p, "89[Diff] :: weights")
    w_ok = (r.get("ok") is True
            and st.last_diff.get("scope") == "weights"
            and st.last_diff.get("baseline") == "immediate"
            and _slices(st).get("weights", {}).get("changed") == ["k"]
            and _slices(st).get("weights", {}).get("before") == {}
            and _slices(st).get("weights", {}).get("after") == {"k": 2.0})
    r2 = _run(p, "89[Diff]")
    _rec("R1 Weight notes through the door: weights scope "
         "sees it; the standalone baseline moved (store "
         "Diff honest empty)",
         w_ok and r2.get("ok") is True
         and st.last_diff.get("changed") == []
         and st.last_diff.get("baseline") == "immediate",
         str(st.last_diff))
    _cleanup(owner)

    # refused Weight captures nothing
    owner = "C3DiffWeightRefused"
    p = _program(owner)
    st = p.core_ii
    r = _run(p, "74[Weight] :: k=inf")
    refused = (r.get("ok") is False
               and r.get("error") == "nonfinite_weight"
               and getattr(st, "diff_baseline", None) is None)
    r = _run(p, "89[Diff] :: weights")
    _rec("R1 refused (non-finite) Weight captures no "
         "baseline; weights Diff still missing",
         refused and r.get("ok") is False
         and r.get("error") == "baseline_missing",
         str(st.weights))
    _cleanup(owner)

    # ============ RING 1: Normalize (75) ================
    owner = "C3DiffNormalize"
    p = _program(owner)
    st = p.core_ii
    st.weights = {"a": 1.0, "b": 3.0}
    _run(p, "75[Normalize]")
    r = _run(p, "89[Diff] :: weights")
    _rec("R1 Normalize notes before the whole-dict rebind",
         r.get("ok") is True
         and sorted(_slices(st).get("weights", {})
                    .get("changed") or []) == ["a", "b"]
         and _slices(st).get("weights", {}).get("before")
         == {"a": 1.0, "b": 3.0}
         and _slices(st).get("weights", {}).get("after")
         == {"a": 0.25, "b": 0.75},
         str(st.last_diff))
    _cleanup(owner)

    # ============ RING 1: Cause / Depend (78/79) ========
    owner = "C3DiffCause"
    p = _program(owner)
    st = p.core_ii
    _run(p, "78[Cause] :: a>b")
    r = _run(p, "89[Diff] :: causes")
    c_ok = (r.get("ok") is True
            and _slices(st).get("causes", {}).get("changed")
            == [("a", "b")]
            and _slices(st).get("causes", {}).get("before") == [])
    base_obj = st.diff_baseline
    r2 = _run(p, "78[Cause] :: a>b")
    dup_ok = (r2.get("ok") is True
              and st.diff_baseline is base_obj)
    r3 = _run(p, "89[Diff] :: causes")
    _rec("R1 Cause notes via the shared _relation site; a "
         "duplicate Cause mutates nothing and does NOT "
         "re-note (baseline identity unchanged)",
         c_ok and dup_ok
         and _slices(st).get("causes", {}).get("changed")
         == [("a", "b")],
         str(st.last_diff))
    _cleanup(owner)

    owner = "C3DiffDepend"
    p = _program(owner)
    st = p.core_ii
    _run(p, "79[Depend] :: x>y")
    r = _run(p, "89[Diff] :: deps")
    _rec("R1 Depend notes through the same _relation door",
         r.get("ok") is True
         and _slices(st).get("deps", {}).get("changed")
         == [("x", "y")],
         str(st.last_diff))
    _cleanup(owner)

    # ============ RING 1: Context (80) via whole ========
    owner = "C3DiffContext"
    p = _program(owner)
    st = p.core_ii
    _run(p, "80[Context] :: ctxlab")
    r = _run(p, "89[Diff] :: whole")
    _rec("R1 Context notes; whole-checkpoint scope "
         "compares working slices and names none "
         "unexamined",
         r.get("ok") is True
         and st.last_diff.get("scope") == "whole"
         and _slices(st).get("context", {}).get("changed")
         == ["context"]
         and _slices(st).get("context", {}).get("after")
         == "ctxlab"
         and st.last_diff.get("unexamined") == [],
         str(st.last_diff))
    _cleanup(owner)

    # ============ RING 1: Reference (81) ================
    owner = "C3DiffReference"
    p = _program(owner)
    st = p.core_ii
    _run(p, "81[Reference] :: myref")
    r = _run(p, "89[Diff] :: refs")
    _rec("R1 Reference notes before the refs write",
         r.get("ok") is True
         and _slices(st).get("refs", {}).get("changed")
         == ["myref"]
         and _slices(st).get("refs", {}).get("after")
         == {"myref": "myref"},
         str(st.last_diff))
    _cleanup(owner)

    # ============ RING 1: Group / Ungroup (82/83) =======
    owner = "C3DiffGroup"
    p = _program(owner)
    st = p.core_ii
    st.selected = ["i1", "i2"]
    _run(p, "82[Group] :: g1")
    r = _run(p, "89[Diff] :: groups")
    g_ok = (r.get("ok") is True
            and _slices(st).get("groups", {}).get("changed")
            == ["g1"]
            and _slices(st).get("groups", {}).get("after")
            == {"g1": ["i1", "i2"]})
    _run(p, "83[Ungroup] :: g1")
    r = _run(p, "89[Diff] :: groups")
    _rec("R1 Group and Ungroup both note through the door",
         g_ok and r.get("ok") is True
         and _slices(st).get("groups", {}).get("changed")
         == ["g1"]
         and _slices(st).get("groups", {}).get("after") == {},
         str(st.last_diff))
    _cleanup(owner)

    owner = "C3DiffUngroupRefused"
    p = _program(owner)
    st = p.core_ii
    _run(p, "55[Set] :: a=1")
    base_obj = st.diff_baseline
    r = _run(p, "83[Ungroup] :: nope")
    _rec("R1 refused Ungroup (missing group) captures "
         "nothing: baseline identity unchanged",
         r.get("ok") is False
         and r.get("error") == "ungroup_missing:nope"
         and st.diff_baseline is base_obj,
         str(r.get("error")))
    _cleanup(owner)

    # ============ RING 1: Define / Alias (97/98) ========
    owner = "C3DiffDefineAlias"
    p = _program(owner)
    st = p.core_ii
    _run(p, "97[Define] :: d1=meaning")
    r = _run(p, "89[Diff] :: defs")
    d_ok = (r.get("ok") is True
            and _slices(st).get("defs", {}).get("changed")
            == ["d1"])
    _run(p, "98[Alias] :: a1=d1")
    r = _run(p, "89[Diff] :: aliases")
    _rec("R1 Define and Alias note through the door",
         d_ok and r.get("ok") is True
         and _slices(st).get("aliases", {}).get("changed")
         == ["a1"]
         and _slices(st).get("aliases", {}).get("after")
         == {"a1": "d1"},
         str(st.last_diff))
    _cleanup(owner)

    owner = "C3DiffAliasRefused"
    p = _program(owner)
    st = p.core_ii
    r = _run(p, "98[Alias] :: a1=ghost")
    _rec("R1 refused Alias (missing target) captures no "
         "baseline",
         r.get("ok") is False
         and r.get("error") == "alias_missing"
         and getattr(st, "diff_baseline", None) is None,
         str(r.get("error")))
    _cleanup(owner)

    # ============ RING 1: Compose publish (99) ==========
    # The publication write is the ONE documented ring-1
    # exclusion (it does not note — see Dell 99 in
    # spectrum_ops and the header): a publication is
    # reported by Diff(compositions) inside the standing
    # baseline window, and it manufactures no baseline of
    # its own, so a Diff-bodied define-run still fails
    # baseline_missing exactly as B18's suites pin.
    owner = "C3DiffCompose"
    p = _program(owner)
    st = p.core_ii
    _run(p, "55[Set] :: a=1")
    _run(p, "99[Compose] :: keep=70[Count]")
    r = _run(p, "89[Diff] :: compositions")
    pub_ok = (r.get("ok") is True
              and _slices(st).get("compositions", {})
              .get("changed") == ["keep"]
              and _slices(st).get("compositions", {})
              .get("after") == {"keep": "70[Count]"})
    _cleanup(owner)
    owner = "C3DiffComposeB18"
    p = _program(owner)
    st = p.core_ii
    _run(p, "99[Compose] :: good=70[Count]")
    r = _run(p, "99[Compose] :: good=89[Diff]")
    _rec("R1 Compose publication is visible to "
         "Diff(compositions) in the standing window, and "
         "manufactures no baseline: a Diff-bodied "
         "redefinition still fails baseline_missing and "
         "the prior body is retained (B18 preservation)",
         pub_ok and r.get("ok") is False
         and r.get("error") == "baseline_missing"
         and st.compositions.get("good") == "70[Count]",
         str((r.get("error"), st.compositions)))
    _cleanup(owner)

    # ============ RING 1: chain flow writers ============
    owner = "C3DiffFlowDeep"
    p = _program(owner)
    st = p.core_ii
    _run(p, "80[Context] :: 70[Count]")
    r = _run(p, "89[Diff] :: refs")
    _rec("R1 DeepFlowBy (chain ::) writes refs through "
         "the door: Diff(refs) sees the deep binding",
         r.get("ok") is True
         and _slices(st).get("refs", {}).get("changed")
         == ["deep"]
         and _slices(st).get("refs", {}).get("after")
         == {"deep": "Count"},
         str(st.last_diff))
    _cleanup(owner)

    owner = "C3DiffFlowFrom"
    p = _program(owner)
    st = p.core_ii
    _run(p, "70[Count] <: 54[Query]")
    r = _run(p, "89[Diff] :: refs")
    _rec("R1 FlowFrom (chain <:) writes refs through the "
         "door",
         r.get("ok") is True
         and _slices(st).get("refs", {}).get("changed")
         == ["from"]
         and _slices(st).get("refs", {}).get("after")
         == {"from": "Count"},
         str(st.last_diff))
    _cleanup(owner)

    owner = "C3DiffFlowBy"
    p = _program(owner)
    st = p.core_ii
    _run(p, "80[Context] : 70[Count]")
    r = _run(p, "89[Diff] :: whole")
    _rec("R1 FlowBy (chain :) context write is the noted "
         "last move under whole scope",
         r.get("ok") is True
         and _slices(st).get("context", {}).get("after")
         == "Count"
         and _slices(st).get("context", {}).get("changed")
         == ["context"],
         str(st.last_diff))
    _cleanup(owner)

    # ============ RING 2: 'all' last-move semantics =====
    owner = "C3DiffAll"
    p = _program(owner)
    st = p.core_ii
    _run(p, "55[Set] :: a=1")
    _run(p, "74[Weight] :: k=2")
    r = _run(p, "89[Diff] :: all")
    _rec("R2 'all' compares every content slice against "
         "the LAST move (Weight): store honestly unchanged "
         "in that window, weights changed; working slices "
         "named unexamined",
         r.get("ok") is True
         and st.last_diff.get("scope") == "all"
         and _slices(st).get("store", {}).get("changed") == []
         and _slices(st).get("weights", {}).get("changed")
         == ["k"]
         and sorted(st.last_diff.get("unexamined") or [])
         == sorted(WORKING),
         str(st.last_diff))
    _cleanup(owner)

    # ============ RING 2: whole-scope verdicts ==========
    owner = "C3DiffWholeVerdict"
    p = _program(owner)
    st = p.core_ii
    _run(p, "55[Set] :: a=1")
    _run(p, "91[Assert] :: true")
    r = _run(p, "89[Diff] :: whole")
    _rec("R2 whole scope compares verdict slices: the "
         "Assert stamp is visible against the Set baseline",
         r.get("ok") is True
         and _slices(st).get("last_assert", {}).get("changed")
         == ["last_assert"]
         and _slices(st).get("last_assert", {}).get("after")
         == "PASS",
         str(st.last_diff))
    _cleanup(owner)

    # ============ Transactions ==========================
    owner = "C3DiffTx"
    p = _program(owner)
    st = p.core_ii
    _run(p, "55[Set] :: base=1")
    _run(p, "93[Try]")
    _run(p, "74[Weight] :: tk=5")
    staged = list(st.tx[-1].get("staged_changes") or [])
    r = _run(p, "89[Diff] :: weights")
    tx_ok = (staged == [{"op": "weight", "lab": "tk=5"}]
             and r.get("ok") is True
             and st.last_diff.get("baseline") == "transaction"
             and _slices(st).get("weights", {}).get("changed")
             == ["tk"])
    _run(p, "95[Commit]")
    r = _run(p, "89[Diff] :: all")
    _rec("TX Weight inside a frame is staged through the "
         "door and Diff reads the frame checkpoint; after "
         "Commit the in-frame capture governs standalone "
         "(step9 semantics preserved, per-slice)",
         tx_ok and r.get("ok") is True
         and st.last_diff.get("baseline") == "immediate"
         and _slices(st).get("weights", {}).get("changed")
         == ["tk"]
         and _slices(st).get("store", {}).get("before")
         == {"base": "1"},
         str((staged, st.last_diff)))
    _cleanup(owner)

    # Post-Revert preserved semantics (step9 pin, per-slice)
    owner = "C3DiffTxRevert"
    p = _program(owner)
    st = p.core_ii
    _run(p, "55[Set] :: base=1")
    _run(p, "93[Try]")
    _run(p, "74[Weight] :: tk=5")
    _run(p, "96[Revert]")
    r = _run(p, "89[Diff] :: all")
    _rec("TX after Revert the state is restored and the "
         "in-frame capture governs standalone (step9 pin): "
         "weights honestly empty against it",
         r.get("ok") is True
         and st.weights == {}
         and st.last_diff.get("baseline") == "immediate"
         and _slices(st).get("weights", {}).get("changed")
         == []
         and _slices(st).get("store", {}).get("before")
         == {"base": "1"},
         str(st.last_diff))
    _cleanup(owner)

    # ============ Guard: Delete group branch (86) =======
    owner = "C3DiffDeleteGroup"
    p = _program(owner)
    st = p.core_ii
    st.selected = ["i1"]
    _run(p, "82[Group] :: g1")
    _run(p, "86[Delete] :: g1")
    r = _run(p, "89[Diff] :: groups")
    _rec("guard: Delete's group branch (already noting) "
         "is not double-noted; groups Diff sees the delete",
         r.get("ok") is True
         and _slices(st).get("groups", {}).get("changed")
         == ["g1"]
         and _slices(st).get("groups", {}).get("after") == {},
         str(st.last_diff))
    _cleanup(owner)

    _cleanup(owner)
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"C3DIFF: {passed}/{total}")
    return passed == total


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
