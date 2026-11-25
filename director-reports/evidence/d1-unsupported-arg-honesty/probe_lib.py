"""Shared helpers for D1-UNSUPPORTED-ARG-HONESTY probes.

Twin-program methodology: legacy and typed forms run on separate
fresh owners with identical setup; observable Core II state and
receipts are compared. Cleanup deletes exactly the state entries
created during the run for the throwaway owners (listed before
deletion), never a guessed glob over pre-existing state.
"""
import os
import shutil
import sys

ROOT = os.path.expanduser("~/workspace/nbd-omega-arghonesty")
sys.path.insert(0, ROOT)
STATE = os.path.join(ROOT, "form", "state")


def state_listing():
    return set(os.listdir(STATE)) if os.path.isdir(STATE) else set()


def cleanup(owner, before):
    removed = []
    for name in sorted(state_listing() - before):
        if owner in name:
            path = os.path.join(STATE, name)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            removed.append(name)
    return removed


BASELINE_UNITS = {"welcome"}


def fresh(owner):
    """Open a program for a throwaway owner and VERIFY its starting
    state (a fresh name is a claim, not proof — AGENTS s.8/s.9).
    Observed at base 91ebe20: a new Program is NOT empty — it is
    seeded with exactly one 'welcome' unit. Probes must treat
    BASELINE_UNITS as the floor, never assume emptiness."""
    from form.open import open_program
    p = open_program(owner)
    units = set(p.cube.session.plane.units)
    assert units == BASELINE_UNITS, \
        f"owner {owner} unexpected start state: {sorted(units)}"
    return p


def st(p):
    from form.mandell.core_ii_exec import attach
    return attach(p)


def snap(p):
    s = st(p)
    return {
        "store": dict(getattr(s, "store", {}) or {}),
        "groups": {k: list(v) for k, v in
                   (getattr(s, "groups", {}) or {}).items()},
        "selected": list(getattr(s, "selected", []) or []),
        "scope": getattr(s, "scope", None),
        "defs": dict(getattr(s, "defs", {}) or {}),
        "causes": [tuple(x) for x in (getattr(s, "causes", []) or [])],
        "last_result": dict(getattr(s, "last_result", {}) or {}),
    }


def setup_plane(p):
    p.place("garden_gate", "Garden Gate")
    p.place("garden_fern", "Garden Fern")
    p.place("river_stone", "River Stone")


def verdict(tag, confirmed, detail):
    print(f"[{'CONFIRMED' if confirmed else 'REFUTED'}] {tag}: {detail}")
    return bool(confirmed)
