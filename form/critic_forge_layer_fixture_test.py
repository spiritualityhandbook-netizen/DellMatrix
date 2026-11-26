#!/usr/bin/env python3
"""Critic Finding 3 fixture — the BIMO Forge must stage the OWNER's
persona layer, not the process-default layer (Director disposition
7180713277, issue #512; build authorized as a separate repair).

Defect (verified REAL first-hand 2026-11-25): ForgeSession.open took
no persona layer and staged_body() built the staged BIMOBody with
layer=None, and the REPL entry (form/repl.py) never passed
p.persona_layer. For an owner whose live arrangement is ALL CUSTOM
personas, the staged body resolved none of them: fuse() found zero
docked personas and staged DEFAULT_DOCK instead, the preview adopted
the swap into the session, and 'save <name>' committed DEFAULT_DOCK
over the owner's arrangement. In-forge 'dock'/'pilot' of a custom
persona was likewise refused as "unknown persona".

Contract under test (all through the REAL REPL, piped stdin — the
r75_forge_test production path):
  * all-custom owner: forge preview fuses the CUSTOM arrangement
    (threads are the custom personas; the staged slots/pilot are
    unchanged by previewing);
  * all-custom owner: a custom persona can be docked inside the forge;
  * all-custom owner: 'save <name>' commits the CUSTOM arrangement —
    the live body and the stored configuration both hold the custom
    slots/pilot, byte-for-byte the staged arrangement;
  * the stored configuration survives a fresh-process reload as a
    VALID configuration (not malformed evidence) and can be staged
    again with 'load';
  * control: a DEFAULT_DOCK owner previews and saves unchanged;
  * control: a canonical non-default arrangement (one canonical
    persona docked) previews and saves unchanged — no overcorrection.

Isolation: unique owners; test-owner state files removed at the end.
The module-level default persona layer is never touched (custom
personas are created on each Program's own layer only).

Run: python3 -m form.critic_forge_layer_fixture_test
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))


def _owner(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _repl(commands, owner, do_load=False, timeout=180):
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if do_load:
        args.append("--load")
    result = subprocess.run(
        args, cwd=REPO, env={**os.environ, "PYTHONPATH": REPO},
        input="\n".join(commands) + "\n", capture_output=True,
        text=True, timeout=timeout)
    return result.returncode, result.stdout, result.stderr


def _state(owner):
    from form.persist import _path
    with open(_path(owner)) as f:
        return json.load(f)


def _cleanup(owner):
    from form.persist import _cp_path, _path
    for path in (_path(owner), _cp_path(owner)):
        try:
            os.remove(path)
        except OSError:
            pass


# (slot, name, category) for the all-custom arrangement: one custom
# persona per BIMO slot, so the staged body is custom end to end.
_CUSTOM_SLOTS = [
    ("logic", "F3 Logic Keeper", "PragLog"),
    ("growth", "F3 Growth Keeper", "EvoLog"),
    ("morph", "F3 Morph Keeper", "AutoLog"),
    ("fusion", "F3 Fusion Keeper", "AgentLog"),
    ("ancient", "F3 Ancient Keeper", "Ancient_Psalms"),
    ("language", "F3 Tongue Keeper", "LangLog"),
    ("quality", "F3 Quality Keeper", "DellLog"),
    ("voice", "F3 Voice Keeper", "LangLog"),
    ("execute", "F3 Hand Keeper", "DellLog"),
    ("watch", "F3 Watch Keeper", "AutoLog"),
    ("body", "F3 Body Keeper", "AgentLog"),
]
_PILOT_NAME = "F3 Fusion Keeper"
_LATE = ("watch", "F3 Late Keeper", "AutoLog")


def _pid(name):
    return name.lower().replace(" ", "_")


def _build_custom_owner(owner):
    """Create the all-custom live arrangement on a fresh Program and
    persist it. Returns (custom_slots, custom_pilot, late_pid)."""
    from form.open import open_program
    p = open_program(owner)
    for slot, name, category in _CUSTOM_SLOTS + [_LATE]:
        res = p.create_persona(
            name=name, category=category, role=f"{name} role",
            focus=f"{name} focus", directives=[f"{name} directive"],
            abilities=[f"{name} ability"], limits=[f"{name} limit"],
            prefer_skins=["sphere", "core"], bimo_slot=slot,
            matrix={"h": 0, "v": 0, "shell": 1})
        assert res.get("ok"), f"create_persona {name}: {res}"
    custom_slots = {}
    for slot, name, _cat in _CUSTOM_SLOTS:
        out = p.bimo.dock(slot, _pid(name))
        assert out.get("ok"), f"dock {slot}: {out}"
        custom_slots[slot] = _pid(name)
    out = p.bimo.set_pilot(_pid(_PILOT_NAME))
    assert out.get("ok"), f"set_pilot: {out}"
    p.save()
    return custom_slots, _pid(_PILOT_NAME), _pid(_LATE[1])


def part_custom_owner():
    from form.dell_matrix.personas import DEFAULT_DOCK
    owner = _owner("f3custom")
    try:
        custom_slots, custom_pilot, late_pid = _build_custom_owner(owner)
        expected = dict(custom_slots)
        expected[_LATE[0]] = late_pid  # docked inside the forge below

        rc, out, _ = _repl([
            "forge",
            "preview",
            "status",
            f"dock {_LATE[0]} {late_pid}",
            "save crew",
            "leave",
            "quit",
        ], owner, do_load=True)
        check("custom: repl exits clean", rc == 0)
        check("custom: preview fused the CUSTOM arrangement",
              "F3 Fusion Keeper" in out and "F3 Logic Keeper" in out,
              "fusion threads do not name the custom personas")
        check("custom: preview did not stage the default dock",
              "pilot=mathelody" not in out,
              "staged pilot was swapped to the canonical default")
        check("custom: in-forge dock of a custom persona staged",
              f"→ slot [{_LATE[0]}]" in out and "unknown persona" not in out,
              "custom persona refused inside the forge")
        check("custom: commit reported", "Committed 'crew'" in out)

        st = _state(owner)
        cfg = (st.get("bimo_configurations") or {}).get(
            "configurations", {}).get("crew")
        check("custom: configuration stored", cfg is not None)
        if cfg:
            check("custom: stored arrangement is the CUSTOM one",
                  cfg.get("slots") == expected
                  and cfg.get("pilot") == custom_pilot,
                  f"slots={cfg.get('slots')} pilot={cfg.get('pilot')}")
            check("custom: stored arrangement is NOT the default dock",
                  cfg.get("slots") != dict(DEFAULT_DOCK))
        check("custom: live body kept the CUSTOM arrangement",
              st["bimo"]["slots"] == expected
              and st["bimo"]["pilot"] == custom_pilot,
              f"live slots={st['bimo']['slots']} "
              f"pilot={st['bimo']['pilot']}")
        cmal = (st.get("bimo_configurations") or {}).get("malformed")
        check("custom: configuration not malformed after save",
              not cmal, f"malformed={cmal}")

        # Fresh-process reload: the stored configuration must still be
        # a valid, stageable configuration — not malformed evidence.
        rc, out, _ = _repl([
            "forge", "configs", "clear", "load crew", "status",
            "leave", "quit",
        ], owner, do_load=True)
        check("custom: reload repl exits clean", rc == 0)
        check("custom: configuration listed after reload",
              f"crew · pilot={custom_pilot}" in out,
              "stored configuration lost or invalid after reload")
        check("custom: configuration staged after reload",
              "Staged configuration 'crew'" in out)
        st = _state(owner)
        cmal = (st.get("bimo_configurations") or {}).get("malformed")
        check("custom: configuration not malformed after reload",
              not cmal, f"malformed={cmal}")
    finally:
        _cleanup(owner)


def part_default_control():
    from form.dell_matrix.personas import DEFAULT_DOCK
    owner = _owner("f3default")
    try:
        rc, out, _ = _repl([
            "forge", "defaults", "preview", "save stock", "leave",
            "bimo", "quit",
        ], owner)
        check("default: repl exits clean", rc == 0)
        check("default: preview fused the default dock",
              "Manny" in out and "Threads (11)" in out)
        check("default: commit reported", "Committed 'stock'" in out)
        st = _state(owner)
        cfg = (st.get("bimo_configurations") or {}).get(
            "configurations", {}).get("stock")
        check("default: stored arrangement is the default dock",
              cfg is not None and cfg.get("slots") == dict(DEFAULT_DOCK)
              and cfg.get("pilot") == "mathelody")
        check("default: live body is the default dock",
              st["bimo"]["slots"] == dict(DEFAULT_DOCK)
              and st["bimo"]["pilot"] == "mathelody")
    finally:
        _cleanup(owner)


def part_canonical_control():
    owner = _owner("f3canon")
    try:
        rc, out, _ = _repl([
            "forge", "dock logic manny", "preview", "save solo",
            "leave", "quit",
        ], owner)
        check("canonical: repl exits clean", rc == 0)
        check("canonical: preview fused the single docked persona",
              "Threads (1)" in out and "Manny" in out)
        check("canonical: commit reported", "Committed 'solo'" in out)
        st = _state(owner)
        cfg = (st.get("bimo_configurations") or {}).get(
            "configurations", {}).get("solo")
        check("canonical: stored arrangement exact",
              cfg is not None and cfg["slots"].get("logic") == "manny"
              and sum(1 for v in cfg["slots"].values() if v) == 1)
        check("canonical: live body exact",
              st["bimo"]["slots"].get("logic") == "manny"
              and sum(1 for v in st["bimo"]["slots"].values() if v) == 1)
    finally:
        _cleanup(owner)


def run_all():
    part_custom_owner()
    part_default_control()
    part_canonical_control()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"Critic Forge Layer Fixture: {passed}/{len(RESULTS)} "
          f"checks passed")


def smoke() -> bool:
    try:
        run_all()
        return all(ok for _, ok in RESULTS)
    except Exception as e:
        print(f"CRITIC FORGE LAYER SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
