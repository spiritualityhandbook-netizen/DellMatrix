"""Phase K — Spanish/French user commands (README program).

README §2 listed Spanish / French commands as UNVERIFIED. The
polyglot bridge (form/mandell/polyglot.py) maps ES/FR phrases to
English intents, and polyglot_tests gates >= 0.90 per language —
but only at the MAPPING level. Nothing proved a user could run
the core loop in Spanish or French through the real REPL.

This suite proves it at REAL_USER_PATH standard, per language:
separate REPL subprocesses driving create -> grow -> proposals
-> rank -> confirm all -> show -> save, then a second process
(--load) verifying the created idea and the confirmed state
persisted, and that an unmapped phrase is an honest miss.

One gap found and fixed by this phase: an unmapped es/fr phrase
printed two empty lines ("english: " / "mandel:  ") and nothing
else — indistinguishable from a malfunction. The REPL handlers
now print the bridge's note ("no map yet for this
phrase/language") when a phrase has no map. The suite asserts
the note and that nothing executed.

Isolation: unique owner per language per run; state-file absence
verified up front; cleanup via canonical paths, failing loudly
on real errors.
"""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import uuid

CHECKS: list = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))


def _cleanup(owner: str) -> None:
    from form.dell_matrix.nursery import owner_nursery_path
    from form.persist import _path
    paths = [owner_nursery_path(owner), _path(owner)]
    paths += glob.glob(f"form/state/checkpoint_{owner}_*")
    errors = []
    for path in paths:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except OSError as exc:
            errors.append(f"{path}: {exc}")
    try:
        shutil.rmtree(f"form/state/ideas_{owner}")
    except FileNotFoundError:
        pass
    except OSError as exc:
        errors.append(f"ideas_{owner}: {exc}")
    if errors:
        raise AssertionError("cleanup failed: " + "; ".join(errors))


def _repl(commands: list, owner: str, load: bool,
          timeout: int = 120):
    cwd = os.path.abspath(".")
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if load:
        args.append("--load")
    env = {**os.environ, "PYTHONPATH": cwd}
    result = subprocess.run(
        args, cwd=cwd, env=env, input="\n".join(commands) + "\n",
        capture_output=True, text=True, timeout=timeout)
    return result.returncode, result.stdout


# Per-language core loop. {label} is the created idea's name as the
# user typed it; the bridge lowercases it into the English intent.
LANGS = {
    "es": {
        "create": "es crea una idea llamada Mareas del Sur",
        "grow": "es crece 2",
        "proposals": "es propuestas",
        "rank": "es clasifica",
        "confirm": "es confirma todo",
        "show": "es muestra",
        "save": "es guarda",
        "unmapped": "es baila conmigo",
        "label": "mareas del sur",
    },
    "fr": {
        "create": "fr crée une idée appelée Marées du Sud",
        "grow": "fr grandis 2",
        "proposals": "fr propositions",
        "rank": "fr classe",
        "confirm": "fr confirme tout",
        "show": "fr montre",
        "save": "fr sauvegarde",
        "unmapped": "fr danse avec moi",
        "label": "marées du sud",
    },
}


def _run_language(code: str, spec: dict) -> None:
    from form.persist import _path
    owner = f"polyglot{code}_{uuid.uuid4().hex[:8]}"
    try:
        check(f"{code}: owner state absent before session 1",
              not os.path.exists(_path(owner)))
        label = spec["label"]

        rc, out = _repl([spec["create"], spec["grow"],
                         spec["proposals"], spec["rank"],
                         spec["confirm"], spec["show"],
                         spec["save"], "quit"], owner, load=False)
        check(f"{code}: session 1 exits clean", rc == 0)
        check(f"{code}: bridge maps create to the English intent",
              f"english: create an idea called {label}" in out,
              out[-600:])
        check(f"{code}: idea created under its translated label",
              f'Created idea: "{label}"' in out, out[-600:])
        check(f"{code}: grow stages a nursery proposal",
              "Nursery pending: 1" in out, out[-600:])
        check(f"{code}: proposals lists the staged proposal",
              "Nursery has 1 proposal(s)" in out, out[-600:])
        check(f"{code}: rank ranks the proposal",
              "Ranked 1 proposals" in out, out[-600:])
        check(f"{code}: confirm all confirms it",
              "Confirmed 1 proposal(s)" in out, out[-600:])
        check(f"{code}: show renders the created idea",
              f"{label}@" in out, out[-600:])
        check(f"{code}: save persists the session",
              "Session saved." in out, out[-600:])

        rc, out = _repl([spec["show"], spec["proposals"],
                         spec["unmapped"], "quit"], owner, load=True)
        check(f"{code}: session 2 exits clean", rc == 0)
        check(f"{code}: reload restores the session",
              f"Loaded session for {owner}." in out, out[-600:])
        check(f"{code}: created idea survives the process boundary",
              f"{label}@" in out, out[-600:])
        check(f"{code}: confirmed state survives (nursery empty)",
              "Nursery is empty" in out, out[-600:])
        check(f"{code}: unmapped phrase is an honest miss",
              "(no map yet for this phrase/language)" in out,
              out[-600:])
        check(f"{code}: unmapped phrase executed nothing",
              "Created idea" not in out, out[-600:])
    finally:
        _cleanup(owner)


def smoke() -> bool:
    from form.mandell.polyglot import ES_MAP, FR_MAP, LA_MAP, bridge_lang

    # Construction parity: all three doors cover the same intents.
    es_i = sorted({t for _, t in ES_MAP})
    fr_i = sorted({t for _, t in FR_MAP})
    la_i = sorted({t for _, t in LA_MAP})
    check("parity: ES/FR/LA maps cover identical intent sets",
          es_i == fr_i == la_i,
          f"es-only={set(es_i) - set(fr_i)} fr-only={set(fr_i) - set(es_i)}")
    check("parity: maps are non-trivial (41 intents each)",
          len(ES_MAP) == len(FR_MAP) == len(LA_MAP) == 41)

    # Bridge spot checks (INTEGRATION): phrase -> English intent.
    rep = bridge_lang("es", "crea una idea llamada Prueba")
    check("bridge: es create maps",
          rep.get("ok") == "true"
          and rep.get("english") == "create an idea called prueba",
          str(rep))
    rep = bridge_lang("fr", "confirme tout")
    check("bridge: fr confirm maps",
          rep.get("ok") == "true" and rep.get("english") == "confirm all",
          str(rep))
    rep = bridge_lang("es", "baila conmigo")
    check("bridge: unmapped phrase reports no map",
          rep.get("ok") == "false"
          and "no map yet" in (rep.get("note") or ""), str(rep))

    for code, spec in LANGS.items():
        _run_language(code, spec)

    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"=== Polyglot user path: {passed}/{len(CHECKS)} ===")
    return passed == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
