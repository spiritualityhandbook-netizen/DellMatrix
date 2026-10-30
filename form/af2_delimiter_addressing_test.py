#!/usr/bin/env python3
"""AF-2: delimiter addressing — segment labels + longest-existing-key.

Before this circuit (audit AF-2, HT-01/HT-03/HT-04):
- parse_seed took the label by rpartition('::'): in
  "55[Set] :: k=v > 70[Count]" the whole tail became the label,
  Count never ran, and Set stored the chain text as its value.
  Composer-shaped programs (a label per segment) failed to parse
  at all through parse_seed, though flow_executor's tokenizer
  already segmented them correctly.
- Set/Patch split their label on the FIRST '=' and Move/Replace
  on the FIRST '>', so a store key that itself contains the
  delimiter (creatable via a Move destination) could be read
  (Get/Delete are verbatim) but never patched, set, moved, or
  replaced — write-orphaned.

Contract proven here (public entry path, execute_seed):
Form B (segment-first parsing):
1. HT-01 inverted: both atoms run; Set stores only its own
   segment's value.
2. B2 preservation: a label whose '>' is NOT followed by an atom
   is label DATA (Cause 'rain > flood' intact, relation stored).
3. B3 preservation: a trailing shared label still reaches the
   earlier atom (Set in "55 > 70 :: jk=jv" stores jk=jv).
4. Composer shape parses through parse_seed with per-atom
   segment labels (parse_program parity).
5. '::' followed by an atom is still the DeepFlowBy flow, and
   '::' inside a label is still a loud parse refusal (HT-02 /
   HT-10a shapes unchanged).
Form A (longest-existing-key partition):
6. HT-03 inverted: Patch and Set address the existing key
   'x=y'; no fragment key 'x' is created.
7. HT-04 inverted: Move and Replace address the existing key
   'x>y' as their source.
8. Longest wins: when both 'x' and 'x=y' exist, Patch aims at
   'x=y'.
9. Legacy fallback: when only the shorter key exists, the
   first-delimiter split is unchanged (Patch 'x=y=2' patches x;
   Move 'x>y>z' moves x to the literal destination 'y>z').
10. A3 preservation: plain Set/Patch creation + update unchanged;
    a fresh Set with '=' in the VALUE still splits at the first
    '=' (no existing longer key)."""
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


def main():
    from form.open import Program
    from form.mandell.executor import execute_seed
    from form.mandell.seed import parse_seed

    owner = "AF2Addr"

    def fresh():
        _cleanup(owner)
        return Program(owner=owner)

    def atoms(r):
        return [a.get("dell") for a in r.get("atom_results", [])]

    # 1. HT-01 inverted
    p = fresh()
    r = execute_seed(p, "55[Set] :: k=v > 70[Count]")
    _rec("ht01 both atoms run", atoms(r) == [55, 70] and r.get("ok"),
         f"atoms={atoms(r)} ok={r.get('ok')} err={r.get('error')}")
    _rec("ht01 set stores own segment value",
         p.core_ii.store.get("k") == "v", str(dict(p.core_ii.store)))

    # 2. B2: '>' as label data
    sd = parse_seed("78[Cause] :: rain > flood")
    _rec("cause label intact", sd.ok and sd.label == "rain > flood"
         and [a.dell for a in sd.atoms] == [78],
         f"ok={sd.ok} label={sd.label!r}")
    p = fresh()
    r = execute_seed(p, "78[Cause] :: rain > flood")
    _rec("cause relation stored",
         r.get("ok") and ("rain", "flood") in
         [tuple(x) for x in p.core_ii.causes],
         f"ok={r.get('ok')} causes={p.core_ii.causes}")

    # 3. B3: trailing shared label reaches the earlier atom
    p = fresh()
    r = execute_seed(p, "55[Set] > 70[Count] :: jk=jv")
    _rec("trailing label reaches set",
         atoms(r) == [55, 70] and p.core_ii.store.get("jk") == "jv",
         f"atoms={atoms(r)} store={dict(p.core_ii.store)}")

    # 4. Composer shape through parse_seed
    sd = parse_seed("15[Map] :: sphere > 34[Stamp] :: created > 10[Keep]")
    _rec("composer shape parses", sd.ok
         and [a.dell for a in sd.atoms] == [15, 34, 10]
         and sd.flows == [">", ">"],
         f"ok={sd.ok} err={sd.error}")
    _rec("composer segment labels",
         [a.label for a in sd.atoms] == ["sphere", "created", ""],
         str([a.label for a in sd.atoms]))
    _rec("composer mandel roundtrip",
         sd.as_mandel() == "15[Map] :: sphere > 34[Stamp] :: created > 10[Keep]",
         sd.as_mandel())

    # 5. '::' dual role + embedded-'::' refusal preserved
    sd = parse_seed("80[Context] :: 70[Count]")
    _rec("deepflowby still a flow", sd.ok and sd.flows == ["::"]
         and [a.dell for a in sd.atoms] == [80, 70],
         f"flows={sd.flows}")
    _rec("embedded coloncolon refused",
         not parse_seed("55[Set] :: k=a::b").ok, "")
    _rec("compose coloncolon body refused",
         not parse_seed("99[Compose] :: swall=55[Set] :: k=v > 70[Count]").ok, "")

    # 6. HT-03 inverted
    p = fresh()
    execute_seed(p, "55[Set] :: a=real")
    execute_seed(p, "85[Move] :: a>x=y")
    r = execute_seed(p, "88[Patch] :: x=y=2")
    _rec("ht03 patch addresses x=y", r.get("ok")
         and p.core_ii.store.get("x=y") == "2",
         f"ok={r.get('ok')} err={r.get('error')} store={dict(p.core_ii.store)}")
    r = execute_seed(p, "55[Set] :: x=y=3")
    _rec("ht03 set addresses x=y, no fragment",
         r.get("ok") and p.core_ii.store.get("x=y") == "3"
         and "x" not in p.core_ii.store,
         f"store={dict(p.core_ii.store)}")
    r = execute_seed(p, "56[Get] :: x=y")
    _rec("ht03 get verbatim still reads x=y",
         r.get("ok") and (p.core_ii.last_result or {}).get("value") == "3",
         f"lr={p.core_ii.last_result}")

    # 7. HT-04 inverted
    p = fresh()
    execute_seed(p, "55[Set] :: a=real")
    execute_seed(p, "85[Move] :: a>x>y")
    r = execute_seed(p, "85[Move] :: x>y>z")
    _rec("ht04 move addresses x>y", r.get("ok")
         and p.core_ii.store.get("z") == "real"
         and "x>y" not in p.core_ii.store,
         f"ok={r.get('ok')} err={r.get('error')} store={dict(p.core_ii.store)}")
    execute_seed(p, "55[Set] :: b=real2")
    execute_seed(p, "85[Move] :: b>x>y")
    r = execute_seed(p, "87[Replace] :: x>y>w")
    _rec("ht04 replace addresses x>y", r.get("ok")
         and p.core_ii.store.get("w") == "real2"
         and "x>y" not in p.core_ii.store,
         f"ok={r.get('ok')} err={r.get('error')} store={dict(p.core_ii.store)}")

    # 8. Longest wins when both prefixes exist
    p = fresh()
    execute_seed(p, "55[Set] :: x=short")
    execute_seed(p, "55[Set] :: a=real")
    execute_seed(p, "85[Move] :: a>x=y")
    r = execute_seed(p, "88[Patch] :: x=y=9")
    _rec("longest existing key wins", r.get("ok")
         and p.core_ii.store.get("x=y") == "9"
         and p.core_ii.store.get("x") == "short",
         f"store={dict(p.core_ii.store)}")

    # 9. Legacy fallback when only the shorter key exists
    p = fresh()
    execute_seed(p, "55[Set] :: x=1")
    r = execute_seed(p, "88[Patch] :: x=y=2")
    _rec("fallback patch aims at x", r.get("ok")
         and p.core_ii.store.get("x") == "y=2"
         and "x=y" not in p.core_ii.store,
         f"store={dict(p.core_ii.store)}")
    r = execute_seed(p, "85[Move] :: x>y>z")
    _rec("fallback move aims at x, literal dest", r.get("ok")
         and p.core_ii.store.get("y>z") == "y=2"
         and "x" not in p.core_ii.store,
         f"ok={r.get('ok')} err={r.get('error')} store={dict(p.core_ii.store)}")

    # 10. A3 plain + fresh creation unchanged
    p = fresh()
    execute_seed(p, "55[Set] :: plain=1")
    r = execute_seed(p, "88[Patch] :: plain=2")
    _rec("plain set/patch unchanged", r.get("ok")
         and p.core_ii.store.get("plain") == "2",
         f"store={dict(p.core_ii.store)}")
    r = execute_seed(p, "55[Set] :: fresh=a=b")
    _rec("fresh set splits at first equals", r.get("ok")
         and p.core_ii.store.get("fresh") == "a=b"
         and "fresh=a" not in p.core_ii.store,
         f"store={dict(p.core_ii.store)}")
    r = execute_seed(p, "88[Patch] :: nosuch=1")
    _rec("patch miss identity unchanged",
         not r.get("ok") and str(r.get("error")).startswith("patch_miss:nosuch"),
         f"err={r.get('error')}")

    _cleanup(owner)
    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"AF2_DELIMITER_ADDRESSING: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
