"""R24-L — create-door label losslessness (Director 7098988693).

Defect (Lane C package 7098540189, reproduced at main 88659c49):
`form/idea_create.py` sliced the authored label at 80 chars
(`label[:80]` in parse_create_line, reached via needs.parse_and_place),
so a 122-char authored label persisted as exactly 80 in the saved
state file and the create receipt printed the cut label as if
authored — no refusal, no disclosure.

Contract (no silent truncation, mirroring the canonical label law):
the system's documented label budget is 200 chars — Nursery Q-S2.1
(MAX_LABEL_CHARS = 200, NurseryLabelError BEFORE mutation) and the
inference dock's identical bound, both of which repudiated the
historical label[:80] silent cut as destroying admitted content.
So at the public create door:
  - labels up to 200 chars persist byte-exact and the receipt prints
    the authored label whole;
  - a label over 200 chars is refused with a typed, visible refusal
    BEFORE any mutation — nothing is placed, nothing persists.

Every case drives the PUBLIC door (piped `python3 -m form.repl`),
then reads the persisted state file bytes (plane.units labels).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = []


def rec(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
    RESULTS.append((name, bool(ok)))


def _label(prefix, n):
    return prefix + "x" * (n - len(prefix))


def _session(owner, lines, load=False):
    argv = [sys.executable, "-B", "-m", "form.repl", "--owner", owner]
    if load:
        argv.append("--load")
    p = subprocess.run(argv, input="\n".join(lines) + "\n",
                       capture_output=True, text=True, cwd=str(ROOT),
                       timeout=280)
    return p.stdout + p.stderr


def _persisted_labels(owner):
    f = ROOT / "form" / "state" / f"program_{owner}.json"
    if not f.exists():
        return []
    d = json.loads(f.read_text())
    units = ((d.get("plane") or {}).get("units") or {})
    return [str(u.get("label") or "") for u in units.values()]


def _create_case(owner, label, *, quoted=False, strong=False):
    shown = f"'{label}'" if quoted else label
    line = f"create an idea called {shown}"
    if strong:
        line += " detail: a detailed purpose for this idea goals: first goal; second goal"
    out = _session(owner, [line, "save"])
    return out


def smoke() -> bool:
    RESULTS.clear()

    # Control: exactly 80 chars — whole at main already.
    lab80 = _label("CaseEighty", 80)
    out = _create_case("R24L80", lab80)
    rec("80-char label: receipt prints the authored label whole",
        f'Created idea: "{lab80}"' in out)
    rec("80-char label: persisted byte-exact",
        lab80 in _persisted_labels("R24L80"))

    # 81 chars — one past the old silent cut.
    lab81 = _label("CaseEightyOne", 81)
    out = _create_case("R24L81", lab81)
    rec("81-char label: receipt prints the authored label whole",
        f'Created idea: "{lab81}"' in out,
        "receipt cut or missing")
    rec("81-char label: persisted byte-exact",
        lab81 in _persisted_labels("R24L81"),
        f"persisted={[len(x) for x in _persisted_labels('R24L81')]}")

    # 122 chars unquoted — the Lane C case.
    lab122 = _label("BoundaryLong", 122)
    out = _create_case("R24L122", lab122)
    rec("122-char label: receipt prints the authored label whole",
        f'Created idea: "{lab122}"' in out)
    rec("122-char label: persisted byte-exact",
        lab122 in _persisted_labels("R24L122"),
        f"persisted={[len(x) for x in _persisted_labels('R24L122')]}")
    # Cold reload: a fresh process loading the saved state shows it whole.
    out2 = _session("R24L122", ["proposals browse"], load=True)
    rec("122-char label: whole after cold reload",
        lab122 in out2, "reloaded surface shows the cut label only")

    # 122 chars quoted — wrapper quotes stripped, content whole.
    out = _create_case("R24L122Q", lab122, quoted=True)
    rec("122-char quoted label: receipt prints the authored label whole",
        f'Created idea: "{lab122}"' in out)
    rec("122-char quoted label: persisted byte-exact",
        lab122 in _persisted_labels("R24L122Q"))

    # 122 chars, strong form (detail:/goals: present).
    out = _create_case("R24L122S", lab122, strong=True)
    rec("122-char strong-form label: persisted byte-exact",
        lab122 in _persisted_labels("R24L122S"),
        f"persisted={[len(x) for x in _persisted_labels('R24L122S')]}")

    # 200 chars — the canonical budget boundary: preserved whole.
    lab200 = _label("CaseBudgetEdge", 200)
    out = _create_case("R24L200", lab200)
    rec("200-char label (canonical budget): receipt whole",
        f'Created idea: "{lab200}"' in out)
    rec("200-char label (canonical budget): persisted byte-exact",
        lab200 in _persisted_labels("R24L200"),
        f"persisted={[len(x) for x in _persisted_labels('R24L200')]}")

    # 201 chars — over budget: typed visible refusal BEFORE mutation.
    lab201 = _label("CaseOverBudget", 201)
    out = _create_case("R24L201", lab201)
    low = out.lower()
    rec("201-char label: no creation is claimed",
        f'Created idea: "{lab201}"' not in out
        and f'Created idea: "{lab201[:80]}"' not in out,
        "a Created receipt was printed for an over-budget label")
    rec("201-char label: refusal is visible and names the 200 bound",
        "refus" in low and "200" in out,
        "no refusal text naming the bound in the door output")
    persisted = _persisted_labels("R24L201")
    rec("201-char label: nothing persisted (no whole, no cut copy)",
        lab201 not in persisted and lab201[:80] not in persisted,
        f"persisted={[len(x) for x in persisted]}")

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"R24L LABEL LOSSLESS: {passed}/{len(RESULTS)} PASS")
    return all(ok for _, ok in RESULTS)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
