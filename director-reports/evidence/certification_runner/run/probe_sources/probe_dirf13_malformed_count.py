import glob, os, shutil, sys
sys.path.insert(0, os.getcwd())
from form.mandell.executor_leaf import _parse_count

fails = []

def case(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name
          + (" -- " + detail if detail else ""))
    if not cond:
        fails.append(name)

case("grammar: superscript refused", _parse_count("²") is None)
case("grammar: Arabic-Indic digit refused", _parse_count("٣") is None)
case("grammar: oversized refused", _parse_count("9" * 100) is None)
case("grammar: empty refused", _parse_count("") is None)
case("grammar: '3' parses", _parse_count("3") == 3)
case("grammar: '0007' parses", _parse_count("0007") == 7)

def cleanup(owner):
    base = os.path.join(os.getcwd(), "form", "state")
    for pat in ("program_%s.json", "nursery_%s.json",
                "checkpoint_%s.json", "confirm_journal_%s.json",
                "confirm_gen_%s.json", "confirm_current_%s.json"):
        for f in glob.glob(os.path.join(base, pat % owner)):
            os.remove(f)
    d = os.path.join(base, "ideas_%s" % owner)
    if os.path.isdir(d):
        shutil.rmtree(d)

owner = "CertRunnerF13Loop"
try:
    cleanup(owner)
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    from form.mandell.executor import execute_seed
    p = Program(owner=owner)
    attach(p)
    execute_seed(p, "08[Create] :: Alpha")
    r = execute_seed(p, "13[Loop] :: ²")
    case("public path: Loop superscript refuses invalid_loop_count",
         r.get("ok") is False
         and r.get("error") == "invalid_loop_count",
         "result=%r" % ({k: r.get(k) for k in ("ok", "error")},))
    r = execute_seed(p, "13[Loop] :: 2")
    case("public path: program stays usable (lawful Loop runs)",
         r.get("ok") is True,
         "result=%r" % ({k: r.get(k) for k in ("ok", "error")},))
finally:
    cleanup(owner)

print("=== probe_dirf13_malformed_count: %d/8 ===" % (8 - len(fails)))
sys.exit(1 if fails else 0)
