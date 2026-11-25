"""D1 reconciliation R4 — Create skin enforced and wired.

Director ruling 2026-10-29 (D1_TYPED_CONTRACT_RECONCILIATION,
exhibit #4): Dell 8's skin role is enforced and wired —
declared argument values are validated BEFORE mutation
and the resolved skin passes through the existing
placement path. The canonical Skin enum has NO UNKNOWN
member; the accepted set derives from the enum itself
(no new enum, no silent CUBE substitution). This suite
replaces circuit 15's exhibit assertions with the
corrected contract; the historical exhibit evidence
stays in that commit.

Corrected contract:
- The signature's skin values equal [s.name for s in
  Skin] exactly — all eight canonical members.
- validate() refuses a non-member with INVALID_VALUE;
  the executor returns before any mutation (the unit
  census is unchanged by a refused create).
- Every canonical member, passed typed, lands on the
  created unit as that Skin.
- The untyped label path still defaults to Skin.CUBE.
- A wired skin persists: Save + Program.load restores
  the unit with its non-default skin intact.
- Dedup keeps skins per unit: a second create of the
  same name with a different skin mints the _1 unit
  with its own skin; the original is untouched.

House pattern: RESULTS + _rec; loud cleanup."""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from form.dell_matrix.plane import Skin                 # noqa: E402
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


def _units(prog):
    return prog.cube.session.plane.units


def main():
    owner = "D1Recon4"
    p = _program(owner)
    sig = get_signature(8)
    skin_role = [r for r in sig.roles if r.name == "skin"][0]

    # -- 1: the accepted set derives from the canonical enum
    _rec("signature skin values == the canonical Skin enum "
         "names (all 8, no UNKNOWN)",
         skin_role.values == [s.name for s in Skin]
         and "UNKNOWN" not in (skin_role.values or []),
         str(skin_role.values))

    # -- 2: validate() enforces membership directly
    errs_ok = sig.validate({"name": "X", "skin": "SPHERE"})
    errs_bad = sig.validate({"name": "X", "skin": "TRIANGLE"})
    errs_unk = sig.validate({"name": "X", "skin": "UNKNOWN"})
    _rec("validate(): a member passes; TRIANGLE and UNKNOWN "
         "fail with INVALID_VALUE",
         errs_ok == []
         and any("INVALID_VALUE" in e for e in errs_bad)
         and any("INVALID_VALUE" in e for e in errs_unk),
         f"ok={errs_ok} bad={errs_bad} unk={errs_unk}")

    # -- 3: every canonical member wires through to its unit
    all_wired = True
    detail = []
    for member in Skin:
        nm = f"Skin {member.name.title()}"
        r = _run(p, f'08[Create](name="{nm}", '
                    f'skin="{member.name}")')
        u = _units(p).get(f"skin_{member.name.lower()}")
        good = (r.get("ok") is True and u is not None
                and u.skin is member)
        all_wired = all_wired and good
        detail.append(f"{member.name}={u.skin if u else None}")
    _rec("all 8 canonical skins land on their created units",
         all_wired, "; ".join(detail))

    # -- 4: refusal happens BEFORE mutation (census frozen)
    before = set(_units(p))
    r = _run(p, '08[Create](name="Tri Wish", skin="TRIANGLE")')
    r2 = _run(p, '08[Create](name="Lower Wish", skin="sphere")')
    _rec("TRIANGLE refuses (INVALID_VALUE) and lowercase "
         "'sphere' is not silently accepted either — both "
         "leave the unit census unchanged",
         r.get("ok") is False
         and "INVALID_VALUE" in str(r.get("error"))
         and r2.get("ok") is False
         and set(_units(p)) == before,
         f"err={r.get('error')} err2={r2.get('error')}")

    # -- 5: the untyped label path still defaults to CUBE
    _run(p, "08[Create] :: Plain Path")
    u = _units(p).get("plain_path")
    _rec("label-path create (no typed skin) defaults to "
         "Skin.CUBE", u is not None and u.skin is Skin.CUBE,
         f"skin={u.skin}" if u else "missing")

    # -- 6: dedup keeps each unit's own skin
    _run(p, '08[Create](name="Twin", skin="SEED")')
    _run(p, '08[Create](name="Twin", skin="CORE")')
    u1 = _units(p).get("twin")
    u2 = _units(p).get("twin_1")
    _rec("dedup: twin keeps SEED, twin_1 carries CORE",
         u1 is not None and u1.skin is Skin.SEED
         and u2 is not None and u2.skin is Skin.CORE,
         f"{u1.skin if u1 else None}|{u2.skin if u2 else None}")

    # -- 7: a wired skin persists through Save + load
    _run(p, "10[Save]")
    from form.open import Program
    p_load = Program.load(owner=owner)
    ul = p_load.cube.session.plane.units.get("skin_sphere")
    _rec("Program.load restores the SPHERE unit with its "
         "skin intact",
         ul is not None and ul.skin is Skin.SPHERE,
         f"skin={ul.skin}" if ul else "missing")

    # -- 8: docs pins
    _rec("signature failures name the INVALID_VALUE refusal "
         "(no UNENFORCED exhibit text remains)",
         "INVALID_VALUE" in sig.failures
         and "UNENFORCED" not in sig.failures)
    _rec("proof card carries the R4 corrected contract (8)",
         "INVALID_VALUE" in DEEP_NOTES[8]
         and "NO UNKNOWN member" in DEEP_NOTES[8])

    _cleanup(owner)
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_RECON4_CREATE_SKIN: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
