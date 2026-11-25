"""UD-2 — English routing: an atom inside English prose is CONTENT.

Director ruling 7085151190 decision 5 (2026-11-22): a `NN[Term]`
sequence appearing inside English prose is content, not an
executable seed. The current `looks_like_seed = bool(_ATOM.search(...))`
is not a public routing authority. Public dispatch must use the
grammar-aware WHOLE-LINE CLAIM boundary already exercised on #506
(GP-E08 Scope A, Director 7079028132): a line is seed territory iff
every character of it is seed grammar material (atoms, typed arg
lists, flow operators, segment labels). Embedded atom fragments in
prose are content; malformed whole-line claims are refused as seed
claims before mutation, never rerouted to English.

Defect reproduced at main 8d361b6b (piped REPL, REAL_USER_PATH):
  `create an idea called 12[Harmonic]`
    -> "Seed error: unexpected at 0: 'create an id'", no idea created
       (the legacy looks_like_seed branch claimed the line on the
       embedded fragment alone; GP-E08's T9/T10 oracles on #506 pin
       exactly this legacy behavior as UD-2, a separate build).
  `12[Harmonic` (malformed claim)
    -> fell through to the English door ("Not understood") instead
       of a seed-claim refusal.

Contract pinned here:
  - `create an idea called 12[Harmonic]` (quoted or not) reaches the
    English door and creates an idea whose label is the exact
    literal `12[Harmonic]`; no Seed error, no seed execution.
  - A leading valid seed (`12[Harmonic]`, incl. a segment label)
    still executes through the seed door; nothing is created as an
    idea by the English door.
  - Malformed whole-line claims (`12[Harmonic`, `12[Harmonic] >`)
    are refused by the seed door (Seed error), never rerouted to
    English, and create nothing.
  - Prose carrying an atom fragment (plain, with operators, or with
    a typed-args atom) is never claimed by the seed door.

Realism: every check drives the literal program entry point
(`python3 -m form.repl`, piped stdin) = REAL_USER_PATH limited to
the piped REPL (precedent: GP-E08 T1, R24-L suite).

Isolation: each check uses its own uniquely-named Program owner;
that owner's state artifacts are removed before and after the check
(exact owner-scoped paths only).
"""
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "form" / "state"
RESULTS = []


def rec(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
    RESULTS.append((name, bool(ok)))


def _owner(tag):
    return f"UD2{tag}{uuid.uuid4().hex[:8]}"


def _cleanup(owner):
    # Exact owner-scoped artifacts only (canonical state paths).
    for path in (
        STATE_DIR / f"program_{owner}.json",
        STATE_DIR / f"ideas_{owner}",
        STATE_DIR / f"inbox_{owner}",
    ):
        try:
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            elif path.exists():
                path.unlink()
        except OSError:
            pass
    # Checkpoint siblings carry the same owner token in their name.
    if STATE_DIR.exists():
        for entry in STATE_DIR.iterdir():
            if owner in entry.name and entry.name.startswith("program_"):
                try:
                    entry.unlink()
                except OSError:
                    pass


def _session(owner, lines):
    _cleanup(owner)
    argv = [sys.executable, "-B", "-m", "form.repl", "--owner", owner]
    try:
        p = subprocess.run(argv, input="\n".join(lines) + "\n",
                           capture_output=True, text=True, cwd=str(ROOT),
                           timeout=280)
        return p.stdout + p.stderr
    finally:
        _cleanup(owner)


def smoke() -> bool:
    RESULTS.clear()

    # 1. The headline case: English create with an unquoted atom label.
    out = _session(_owner("A"), ["create an idea called 12[Harmonic]", "ideas"])
    rec("UD2-1 English create, unquoted atom label: idea created whole",
        'Created idea: "12[Harmonic]"' in out,
        "English door never received the line")
    rec("UD2-1 no Seed error on the English line",
        "Seed error" not in out)
    rec("UD2-1 created idea is listed with its literal label",
        "12[Harmonic]" in out.split("Created idea")[-1])

    # 2. Quoted variant: wrapper quotes are the English door's own
    # punctuation (R24-L precedent); the operand stays exact.
    out = _session(_owner("B"), ['create an idea called "12[Harmonic]"'])
    rec("UD2-2 English create, quoted atom label: idea created whole",
        'Created idea: "12[Harmonic]"' in out,
        "quoted English create misrouted or label altered")
    rec("UD2-2 no Seed error on the quoted English line",
        "Seed error" not in out)

    # 3. Leading valid seed still executes as a seed.
    out = _session(_owner("C"), ["12[Harmonic]"])
    rec("UD2-3 leading valid seed executes through the seed door",
        "Mandell: 12[" in out and "Seed error" not in out)
    rec("UD2-3 leading valid seed creates no English idea",
        "Created idea" not in out)

    # 4. Malformed whole-line claim: refused as a seed claim, never
    # rerouted to English.
    out = _session(_owner("D"), ["12[Harmonic", "ideas"])
    rec("UD2-4 malformed claim refused by the seed door",
        "Seed error" in out, "malformed claim fell through to English")
    rec("UD2-4 malformed claim not treated as English",
        "Not understood" not in out)
    rec("UD2-4 malformed claim creates nothing",
        "Created idea" not in out)

    # 5. Malformed claim with a trailing flow operator.
    out = _session(_owner("E"), ["12[Harmonic] >"])
    rec("UD2-5 trailing-flow claim refused by the seed door",
        "Seed error" in out, "trailing-flow claim not refused as seed")
    rec("UD2-5 trailing-flow claim creates nothing",
        "Created idea" not in out)

    # 6. Atom fragment inside plain prose is content.
    out = _session(_owner("F"), ["the token 12[Harmonic] is just a name here"])
    rec("UD2-6 embedded atom in prose: seed door does not claim it",
        "Seed error" not in out and "Mandell: 12[" not in out)

    # 7. Prose with operators AND an atom fragment is still prose.
    out = _session(_owner("G"), ["my result 3 > 2 mentions 12[Harmonic]"])
    rec("UD2-7 prose with operators + atom: seed door does not claim it",
        "Seed error" not in out and "Mandell: 12[" not in out)

    # 8. Typed-args atom inside prose is content.
    out = _session(_owner("H"), ['the syntax 08[Create](name="x") is neat'])
    rec("UD2-8 embedded args atom in prose: seed door does not claim it",
        "Seed error" not in out and "Created idea" not in out)

    # 9. Valid seed with a segment label still executes (claim
    # boundary must not shrink lawful seeds).
    out = _session(_owner("I"), ["12[Harmonic] :: checkup"])
    rec("UD2-9 valid seed with segment label executes",
        "Seed error" not in out and "Created idea" not in out
        and "Mandell: 12[" in out)

    # 10. Atom-free English control: dispatch unchanged.
    out = _session(_owner("J"), ["create an idea called plain witness"])
    rec("UD2-10 plain English create unchanged",
        'Created idea: "plain witness"' in out)

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"UD-2 english routing: {passed}/{len(RESULTS)}")
    return all(ok for _, ok in RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
