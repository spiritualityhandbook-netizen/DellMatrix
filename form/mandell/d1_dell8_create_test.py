"""D1 circuit 15 — Dell 8 (Create) DEEP CONTRACT.

executor_leaf.py place_idea (53-64) + primary==8 arm;
canonical slug/dedup in form/idea_create.py. Create is the
registry's idea-minting Dell and runs on the LEAF executor
(Core I), not Core II. Contract proven here:

- The unit id is the canonical slug of the name
  (lowercase, non-alnum runs -> '_', 40-char cap, fallback
  'idea'); the unit label is the name with '_' -> ' ' and
  words is the name exactly as passed.
- Collision DEDUP: creating an existing name mints
  <slug>_1, _2, ... and says so in the message ('(id: ...)');
  the original unit is never overwritten.
- Bare Create mints the name 'idea'.
- Typed law: name is required (MISSING_REQUIRED), unknown
  roles fail (UNKNOWN_ROLE), and a legacy label that
  differs from the typed name (and from its slug) fails
  with ARGUMENT_CONFLICT and creates nothing.
- SKIN (corrected contract, D1 reconciliation R4 —
  Director ruling replaced the circuit-15 exhibit):
  validate() checks enum membership for roles declaring
  values, and the executor resolves the typed skin and
  passes it to place_idea. skin='SPHERE' mints a SPHERE
  unit; skin='TRIANGLE' (not a canonical Skin member)
  refuses with INVALID_VALUE before any mutation. The
  accepted set derives from the canonical Skin enum —
  it has NO UNKNOWN member.
- Symbiosis seam: a created idea is immediately visible
  to Core II — Select (51) finds it on the plane.
- Persistence: creation is in-memory until Dell 10 (Save)
  writes program_<owner>.json; Program.load(owner) then
  restores the unit with label/words/skin intact. The
  Program constructor alone does not load.
- REAL_USER_PATH REPL evidence included. The English
  'create a garden' line takes the strong-idea door
  (form/idea_create.parse_create_line via dell_matrix
  needs): the WHOLE phrase becomes the name (id
  create_a_garden) with a strength report (0.0, missing
  detail/goals) — the '08[Create](name="garden") > 15[Map]'
  Mandell line the REPL prints is a translation echo, not
  the execution. Pinned as observed.

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


def _units(prog):
    return prog.cube.session.plane.units


def main():
    owner = "D1Dell8"
    p = _program(owner)

    # -- 1: basic create + slug/label/words/skin facts
    r = _run(p, "08[Create] :: Garden Gate")
    u = _units(p).get("garden_gate")
    _rec("create mints the slugged unit with the plain "
         "message", r.get("ok") is True and u is not None
         and 'Created idea: "Garden Gate"' in str(
             r.get("messages")), str(r.get("messages")))
    _rec("unit label/words/skin are name/name-as-passed/CUBE",
         u is not None and u.label == "Garden Gate"
         and u.words == "Garden Gate"
         and str(u.skin) == "Skin.CUBE",
         f"{u.label}|{u.words}|{u.skin}" if u else "missing")

    # -- 2: collision dedup never overwrites
    r2 = _run(p, "08[Create] :: Garden Gate")
    u2 = _units(p).get("garden_gate_1")
    _rec("duplicate create dedups to garden_gate_1 and says so",
         r2.get("ok") is True and u2 is not None
         and "(id: garden_gate_1)" in str(r2.get("messages")),
         str(r2.get("messages")))
    _rec("the original unit is untouched by the dedup",
         _units(p)["garden_gate"].label == "Garden Gate")
    _run(p, "08[Create] :: Garden Gate")
    _rec("a third create dedups to garden_gate_2",
         "garden_gate_2" in _units(p))

    # -- 3: bare + slug edge rules
    _run(p, "08[Create]")
    _rec("bare Create mints the fallback name 'idea'",
         "idea" in _units(p))
    _run(p, "08[Create] :: my_idea")
    um = _units(p).get("my_idea")
    _rec("underscored name: id keeps '_', label gains spaces, "
         "words keep the raw name",
         um is not None and um.label == "my idea"
         and um.words == "my_idea",
         f"{um.label}|{um.words}" if um else "missing")
    _run(p, "08[Create] :: A very long name that goes beyond "
            "forty characters for sure yes indeed")
    _rec("the slug is capped at 40 characters",
         "a_very_long_name_that_goes_beyond_forty_" in _units(p),
         str([k for k in _units(p) if "very" in k]))

    # -- 4: typed law
    r = _run(p, '08[Create](name="Typed Rose")')
    _rec("typed name is wired to Create",
         r.get("ok") is True and "typed_rose" in _units(p)
         and "wired to Create" in str(r.get("messages")),
         str(r.get("messages")))
    r = _run(p, '08[Create](name="Typed Rose") :: Other Label')
    _rec("typed name vs differing label: ARGUMENT_CONFLICT, "
         "nothing created",
         r.get("ok") is False
         and r.get("error") == "ARGUMENT_CONFLICT"
         and "other_label" not in _units(p), str(r.get("error")))
    r = _run(p, '08[Create](skin="SPHERE")')
    _rec("typed without name: MISSING_REQUIRED",
         r.get("ok") is False and "MISSING_REQUIRED" in str(
             r.get("error")), str(r.get("error")))
    r = _run(p, '08[Create](name="X", bogus="1")')
    _rec("unknown role: UNKNOWN_ROLE",
         r.get("ok") is False and "UNKNOWN_ROLE" in str(
             r.get("error")), str(r.get("error")))

    # -- 5: SKIN — enforced and wired (R4 corrected contract)
    r = _run(p, '08[Create](name="Sphere Wish", skin="SPHERE")')
    us = _units(p).get("sphere_wish")
    _rec("skin='SPHERE' is wired through: the unit carries "
         "Skin.SPHERE",
         r.get("ok") is True and us is not None
         and str(us.skin) == "Skin.SPHERE",
         f"skin={us.skin}" if us else "missing")
    before = set(_units(p))
    r = _run(p, '08[Create](name="Bad Skin", skin="TRIANGLE")')
    _rec("skin='TRIANGLE' (not a canonical Skin member) "
         "refuses with INVALID_VALUE and creates nothing",
         r.get("ok") is False
         and "INVALID_VALUE" in str(r.get("error"))
         and "bad_skin" not in _units(p)
         and set(_units(p)) == before,
         str(r.get("error")))

    # -- 6: symbiosis seam — Core II Select sees the new idea
    _run(p, "51[Select] :: garden")
    sel = list(p.core_ii.selected)
    _rec("created ideas are immediately selectable (51 finds "
         "the garden_gate family on the plane)",
         "garden_gate" in sel and "garden_gate_1" in sel,
         str(sel))

    # -- 7: persistence — explicit save + explicit load
    _run(p, "10[Save]")
    from form.open import Program
    p_ctor = Program(owner=owner)
    _rec("the constructor alone does NOT load saved units",
         "garden_gate" not in p_ctor.cube.session.plane.units)
    p_load = Program.load(owner=owner)
    ul = p_load.cube.session.plane.units.get("garden_gate")
    _rec("Program.load restores the created unit intact",
         ul is not None and ul.label == "Garden Gate"
         and ul.words == "Garden Gate"
         and str(ul.skin) == "Skin.CUBE")

    # -- 8: REAL_USER_PATH: REPL seed line + English create
    owner2 = "D1Dell8Repl"
    _cleanup(owner2)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner2],
        input="08[Create] :: Seed Path\ncreate a garden\n",
        capture_output=True, text=True, cwd=_ROOT, timeout=120)
    out = proc.stdout or ""
    _rec("REPL: the seed line creates ('Created idea: "
         "\"Seed Path\"')",
         proc.returncode == 0 and 'Created idea: "Seed Path"'
         in out, out[-300:])
    _rec("REPL: English 'create a garden' takes the "
         "strong-idea door — the whole phrase is the name "
         "(id create_a_garden, strength report shown); the "
         "typed-chain Mandell line is an echo, not the "
         "execution",
         'Created idea: "create a garden" '
         'id=create_a_garden' in out
         and "strength=0.0" in out, out[-300:])
    _cleanup(owner2)

    # -- 9: docs pins
    sig = get_signature(8)
    _rec("signature synced (place_idea:60-71; failures name "
         "the conflict + the INVALID_VALUE skin refusal)",
         "place_idea:60-71" in sig.derived_from
         and "ARGUMENT_CONFLICT" in sig.failures
         and "INVALID_VALUE" in sig.failures)
    _rec("proof card carries the circuit-15 deep note",
         "dedup" in DEEP_NOTES[8].lower()
         and "skin" in DEEP_NOTES[8].lower())

    _cleanup(owner)
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_DELL8_CREATE: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
