"""D1 reconciliation R5 — ARGUMENT_LOSS repaired end to end.

Director ruling 2026-10-29 (D1_TYPED_CONTRACT_RECONCILIATION,
exhibit #5): repair operand preservation end to end —
normalize command recognition WITHOUT lowercasing captured
operands, covering the paraphrase, synonym, and learned
paths. Circuit 3 had fixed extraction in translate/phrases
but left the generation layer: english_brain rewrote lines
to lowercase canonical text (so 'plant Garden Gate' arrived
as label 'garden gate'), and translate's get/find sites
slugged the store key (so 'get A' read 'a' and spaced keys
were unreachable). This suite proves the corrected
contract; the limitation record now reads RESOLVED.

Corrected contract:
- Brain: paraphrase templates fill their groups from the
  case-preserved original; synonym rewrites canonicalize
  only the command head and carry the operand tail in the
  user's case; learned canonicals return verbatim.
- Translate: get/find capture the store key verbatim
  (case AND spaces) from the original text.
- Real English execution: seed-stored keys 'A' and 'a'
  stay DISTINCT through English get; a spaced key written
  by seed Set is readable by English get; values return
  with their case intact.
- Guards unchanged: negated/conditional destructive
  English still refuses to route (UNKNOWN), and plain
  destructive English still routes.

House pattern: RESULTS + _rec; loud cleanup."""
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from form.mandell.dell_cards import DEEP_NOTES          # noqa: E402
from form.mandell.english_brain import (                 # noqa: E402
    learn, normalize_english)
from form.mandell.limitation_knowledge import LIMITATIONS  # noqa: E402
from form.mandell.translate import translate             # noqa: E402

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


def _english(p, line):
    from form.mandell.semantic_router import route_intent
    return route_intent(p, translate(line), line)


def main():
    # -- 1: brain paraphrase path preserves operand case
    norm, path = normalize_english("note down Garden Gate")
    _rec("paraphrase: 'note down Garden Gate' rewrites with "
         "the operand's case intact",
         norm == "create an idea called Garden Gate"
         and path == "paraphrase", f"{norm!r} via {path}")

    # -- 2: brain synonym path preserves operand case
    norm, path = normalize_english("plant Garden Gate")
    _rec("synonym: 'plant Garden Gate' canonicalizes only "
         "the head — operand stays 'Garden Gate'",
         norm == "create an idea called Garden Gate"
         and path == "synonym", f"{norm!r} via {path}")

    # -- 3: learned path returns the canonical verbatim
    learn("Shout About It", "create an idea called Shout About It")
    norm, path = normalize_english("shout about it")
    norm2, path2 = normalize_english("SHOUT ABOUT IT")
    _rec("learned: recognition is case-insensitive (lower "
         "and SHOUTING inputs both hit) while the canonical "
         "returns verbatim — operand case kept",
         norm == "create an idea called Shout About It"
         and path == "learned"
         and norm2 == norm and path2 == "learned",
         f"{norm!r} via {path}; {norm2!r} via {path2}")

    # -- 4: translate end to end
    _rec("translate: 'plant Garden Gate' yields label "
         "'Garden Gate' (the old residual, corrected)",
         translate("plant Garden Gate").args.get("label")
         == "Garden Gate",
         str(translate("plant Garden Gate").args))
    _rec("translate: get/find capture the key verbatim — "
         "'A', 'My Key', 'Alpha' survive",
         translate("get A").args.get("key") == "A"
         and translate("get My Key").args.get("key") == "My Key"
         and translate("find Alpha").args.get("key") == "Alpha",
         str(translate("get My Key").args))

    # -- 5: negation/conditional guards remain effective
    g1 = translate("delete the plan if empty")
    g2 = translate("don't delete the plan")
    d1 = translate("delete the plan")
    _rec("guards: conditional + negated destructive stay "
         "UNKNOWN; plain delete still routes (86, 'plan')",
         g1.action == "unknown" and g1.dell is None
         and g2.action == "unknown" and g2.dell is None
         and d1.dell == 86 and d1.args.get("key") == "plan",
         f"{g1.action}/{g2.action}/{d1.dell}")

    # -- 6: real English execution — A and a stay distinct
    owner = "D1Recon5"
    p = _program(owner)
    st = p.core_ii
    from form.mandell.executor import execute_seed
    execute_seed(p, "55[Set] :: A=AlphaVal")
    execute_seed(p, "55[Set] :: a=betaVal")
    execute_seed(p, "55[Set] :: My Key=Spaced Value")
    _english(p, "get A")
    va = (st.last_result or {}).get("value")
    _english(p, "get a")
    vb = (st.last_result or {}).get("value")
    _english(p, "get My Key")
    vm = (st.last_result or {}).get("value")
    _rec("real English: 'get A' and 'get a' return DIFFERENT "
         "values; the spaced key reads back its cased value",
         va == "AlphaVal" and vb == "betaVal"
         and vm == "Spaced Value",
         f"A={va!r} a={vb!r} MyKey={vm!r}")
    _cleanup(owner)

    # -- 7: REAL_USER_PATH — the literal REPL
    owner2 = "D1Recon5Repl"
    _cleanup(owner2)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner2],
        input="55[Set] :: A=hello\nget A\n",
        capture_output=True, text=True, cwd=_ROOT, timeout=120)
    out = proc.stdout or ""
    _rec("REPL: English 'get A' prints Get A='hello'",
         proc.returncode == 0 and "Get A='hello'" in out,
         out[-300:])
    _cleanup(owner2)

    # -- 8: docs/record pins
    by_id = {e["id"]: e for e in LIMITATIONS}
    _rec("limitation record: ARGUMENT_LOSS is RESOLVED",
         by_id["ARGUMENT_LOSS"]["status"] == "RESOLVED")
    _rec("proof card carries the R5 resolution (56)",
         "RESOLVED" in DEEP_NOTES[56])

    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_RECON5_ARGUMENT_LOSS: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
