#!/usr/bin/env python3
"""AF-1: typed arguments must survive chains and chainlinks.

Before this circuit (audit AF-1, HT-05/HT-06):
- chain_exec._run_atom ran TOAM validate+lower only for
  Dells 51-99; a Core I atom in a chain was re-executed
  from rebuilt seed text WITHOUT its args, so Dell 8's
  valid args were dropped (fallback unit "idea") and its
  invalid args were never validated (silently accepted).
- seed.py chainlink expansion built atoms without the
  parsed item_args, dropping args for ALL Dells.

Contract proven here (public entry path, execute_seed):
1. Chain, valid typed args: Create makes the named unit
   with the named skin — identical to the single atom.
2. Chain, invalid typed value: INVALID_VALUE refusal,
   no unit created by that atom.
3. Chainlink (2v2), valid args: both member atoms carry
   the args; named units created.
4. Chainlink, invalid value: validation refusal.
5. Chainlink, Core II typed args: Replace executes with
   its args (store effect), not a missing-operand error.
6. Single-atom behavior unchanged (valid + invalid).
7. Untyped Core I atom carrying args in a chain behaves
   exactly as the single-atom path (args ignored, ok).

AMENDMENT (2026-11-03, Director Core I contract ruling on
PR #256): check 7's silent-success parity is REPLACED by
refusal parity under the CORE-I-UNSUPPORTED-ARG-GATE repair.
The historical expectation above stands as the record of the
AF-1-era contract; the CURRENT contract is: an unregistered
Core I atom carrying typed args refuses with UNSUPPORTED_ARGS
on BOTH the single-atom and chained paths, identically
(per executing atom — never whole-chain). The amendment is
expressly authorized by that ruling; no other AF-1 check is
altered.
"""
import os
import shutil

RESULTS = []


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))


def _cleanup(owner):
    state = os.path.join("form", "state")
    if not os.path.isdir(state):
        return
    for fn in os.listdir(state):
        if owner in fn:
            p = os.path.join(state, fn)
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
    idir = os.path.join(state, f"ideas_{owner}")
    if os.path.isdir(idir):
        shutil.rmtree(idir)


def _units(p):
    u = p.cube.session.plane.units
    if isinstance(u, dict):
        return u
    out = {}
    for x in u:
        if isinstance(x, str):
            out[x] = {}
        else:
            out[x.id] = x
    return out


def _skin(p, uid):
    u = _units(p).get(uid)
    if u is None:
        return None
    s = getattr(u, "skin", None)
    if s is None and isinstance(u, dict):
        s = u.get("skin")
    return str(s)


def main():
    from form.open import Program
    from form.mandell.executor import execute_seed

    owner = "AF1Args"

    def fresh():
        _cleanup(owner)
        return Program(owner=owner)

    # 1. chain, valid args
    p = fresh()
    r = execute_seed(p, '08[Create](name="Chain Wish", skin="SPHERE") > 70[Count]')
    _rec("chain valid args ok", r.get("ok"), str(r.get("error")))
    _rec("chain valid args unit", "chain_wish" in _units(p),
         str(sorted(_units(p))))
    _rec("chain valid args skin", "SPHERE" in (_skin(p, "chain_wish") or ""),
         str(_skin(p, "chain_wish")))
    # 2. chain, invalid value
    p = fresh()
    r = execute_seed(p, '08[Create](name="Chain Wish", skin="TRIANGLE") > 70[Count]')
    _rec("chain invalid refused", not r.get("ok")
         and "INVALID_VALUE" in str(r.get("error")), str(r.get("error")))
    _rec("chain invalid zero mutation",
         "chain_wish" not in _units(p) and "idea" not in _units(p),
         str(sorted(_units(p))))
    # 3. chainlink, valid args
    p = fresh()
    r = execute_seed(p, '08[A • B](name="Link Wish", skin="SPHERE") > 51[C • D]')
    _rec("chainlink valid ok", r.get("ok"), str(r.get("error")))
    _rec("chainlink valid units",
         "link_wish" in _units(p) and "link_wish_1" in _units(p),
         str(sorted(_units(p))))
    # 4. chainlink, invalid value
    p = fresh()
    r = execute_seed(p, '08[A • B](name="Link Wish", skin="TRIANGLE") > 51[C • D]')
    _rec("chainlink invalid refused", not r.get("ok")
         and "INVALID_VALUE" in str(r.get("error")), str(r.get("error")))
    _rec("chainlink invalid zero mutation",
         not any(u.startswith("link_wish") or u == "idea"
                 for u in _units(p)), str(sorted(_units(p))))
    # 5. chainlink, Core II typed args (Replace): args apply to
    # every member atom (same rule as the ordinary multi-member
    # path). Member 1 replaces data->freshkey; member 2 honestly
    # refuses replace_missing:data — its error names the ARG,
    # where pre-fix it named the member TERM (replace_missing:B).
    p = fresh()
    execute_seed(p, "55[Set] :: data=real")
    r = execute_seed(p, '87[A • B](old="data", new="freshkey") > 51[C • D]')
    st = dict(p.core_ii.store)
    _rec("chainlink core2 args reach both members",
         st.get("freshkey") == "real" and "data" not in st
         and str(r.get("error")).startswith("replace_missing:data"),
         f"ok={r.get('ok')} err={r.get('error')} store={st}")
    # 6. single-atom anchors
    p = fresh()
    r = execute_seed(p, '08[Create](name="Solo Wish", skin="SPHERE")')
    _rec("single valid unchanged",
         r.get("ok") and "solo_wish" in _units(p), str(r.get("error")))
    p = fresh()
    r = execute_seed(p, '08[Create](name="Solo Wish", skin="TRIANGLE")')
    _rec("single invalid unchanged",
         not r.get("ok") and "INVALID_VALUE" in str(r.get("error")),
         str(r.get("error")))
    # 7. untyped Core I with args: chain == single.
    # AMENDED 2026-11-03 (Director ruling on PR #256): refusal
    # parity replaces silent-success parity — both paths refuse
    # UNSUPPORTED_ARGS, per executing atom.
    p = fresh()
    r1 = execute_seed(p, '43[Fallback](note="hi")')
    p = fresh()
    r2 = execute_seed(p, '43[Fallback](note="hi") > 70[Count]')
    _r2_43 = [a for a in (r2.get("atom_results") or [])
              if a.get("dell") == 43]
    _rec("untyped args refusal parity (amended 2026-11-03)",
         r1.get("ok") is False
         and str(r1.get("error")) == "UNSUPPORTED_ARGS: note"
         and r2.get("ok") is False
         and len(_r2_43) == 1
         and _r2_43[0].get("error") == "UNSUPPORTED_ARGS: note",
         f"single={r1.get('ok')}/{r1.get('error')} "
         f"chain={r2.get('ok')}/{r2.get('error')} rec={_r2_43}")

    _cleanup(owner)
    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"AF1_CHAIN_ARGS: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
