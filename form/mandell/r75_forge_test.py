"""R7.5 — BIMO Forge proofs.

The Forge adds what ad-hoc `bimo dock` cannot do: stage a BIMO
arrangement on a detached copy (live body untouched), preview its
fusion, and commit it — atomically — as the live body AND a named,
durable configuration. Extends BIMOBody (the docking authority) and
the proven scoped-session pattern; configurations store slot->persona
mappings and a pilot ONLY (behavior, never authority — R6.4/R6.5).

Covers: the full forge flow on the real REPL public path; staging
isolation (leave without save changes nothing live and stores no
configuration); commit atomicity (save failure restores live body AND
configurations); load/stage roundtrip; preview-on-empty staging the
default dock; the scoped gate (out-of-scope + say-prefixed lines
rejected before anything runs; protected material rejected fail-closed
with zero disclosure); honest EOF (session not saved, committed
configurations remain); mutual exclusion (forge cannot be entered
from inside a workshop); the strict section schemas (absent = legacy,
explicit null = malformed preserved, unknown slot / unknown persona /
foreign owner / key mismatch / extra authority fields all fail closed
and are never applied); invalid staged state rejected at commit;
retention bounds; and the pre-existing ad-hoc `bimo` commands
unchanged.

All fixtures use disposable-copy isolation (unique owners).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid

CHECKS: list = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail and not cond else ""))


def unique_owner(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _repl(commands: list, owner: str, do_load: bool = False, timeout: int = 120):
    """Run the real REPL with piped commands. Returns (rc, stdout, stderr)."""
    cwd = os.path.abspath(".")
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if do_load:
        args.append("--load")
    inp = "\n".join(commands) + "\n"
    result = subprocess.run(
        args, cwd=cwd, env={**os.environ, "PYTHONPATH": cwd},
        input=inp, capture_output=True, text=True, timeout=timeout)
    return result.returncode, result.stdout, result.stderr


def _state(owner: str) -> dict:
    from form.persist import _path
    with open(_path(owner)) as f:
        return json.load(f)


def _cleanup(owner: str) -> None:
    from form.persist import _path, _cp_path
    for path in (_path(owner), _cp_path(owner)):
        try:
            os.remove(path)
        except OSError:
            pass


def part_happy_path():
    owner = unique_owner("r75happy")
    try:
        rc, out, _ = _repl([
            "forge",
            "dock logic manny",
            "dock voice mansplainer",
            "pilot oracle",
            "preview",
            "save crew",
            "leave",
            "bimo",
            "quit",
        ], owner)
        check("happy: repl exits clean", rc == 0)
        check("happy: dock staged, live untouched wording",
              "Staged: 🕵️ Manny → slot [logic] (live body untouched)" in out)
        check("happy: preview fused the STAGED arrangement",
              "Threads (2)" in out and "Manny" in out
              and "Mansplainer" in out)
        check("happy: commit reported", "Committed 'crew'" in out)
        check("happy: live body adopted staged arrangement",
              "Filled 2/11" in out and "pilot=oracle" in out)
        st = _state(owner)
        cfg = st["bimo_configurations"]["configurations"].get("crew")
        check("happy: configuration stored", cfg is not None)
        if cfg:
            check("happy: configuration content exact",
                  cfg["slots"]["logic"] == "manny"
                  and cfg["slots"]["voice"] == "mansplainer"
                  and cfg["pilot"] == "oracle"
                  and cfg["owner"] == owner)
            check("happy: configuration carries no authority fields",
                  set(cfg) == {"name", "owner", "slots", "pilot", "saved"})
        check("happy: live bimo persisted",
              st["bimo"]["slots"]["logic"] == "manny"
              and st["bimo"]["pilot"] == "oracle")
        sessions = st["forge_sessions"]["sessions"]
        check("happy: one closed session record", len(sessions) == 1)
        if sessions:
            rec = next(iter(sessions.values()))
            kinds = [s["kind"] for s in rec["steps"]]
            check("happy: steps recorded in order",
                  kinds == ["enter", "dock", "dock", "pilot", "preview",
                            "save", "leave"], f"{kinds}")
            check("happy: closed is set", bool(rec["closed"]))
    finally:
        _cleanup(owner)


def part_staging_isolation():
    owner = unique_owner("r75iso")
    try:
        rc, out, _ = _repl([
            "forge", "dock logic manny", "clear", "dock growth melody",
            "leave", "bimo", "quit",
        ], owner)
        check("isolation: repl exits clean", rc == 0)
        st = _state(owner)
        check("isolation: no configuration stored without save",
              st["bimo_configurations"]["configurations"] == {})
        check("isolation: live body unchanged by staging",
              all(v is None for v in st["bimo"]["slots"].values()),
              f"{st['bimo']['slots']}")
        check("isolation: session evidence still recorded",
              len(st["forge_sessions"]["sessions"]) == 1)
    finally:
        _cleanup(owner)


def part_load_roundtrip():
    owner = unique_owner("r75load")
    try:
        _repl(["forge", "dock logic manny", "save crew", "leave", "quit"],
              owner)
        rc, out, _ = _repl([
            "forge", "configs", "clear", "load crew", "status",
            "save crew-two", "leave", "quit",
        ], owner, do_load=True)
        check("load: repl exits clean", rc == 0)
        check("load: configs listed", "crew · pilot=mathelody" in out)
        check("load: staged from stored configuration",
              "Staged configuration 'crew'" in out)
        check("load: second configuration committed",
              "Committed 'crew-two'" in out)
        st = _state(owner)
        cfgs = st["bimo_configurations"]["configurations"]
        check("load: both configurations stored",
              set(cfgs) == {"crew", "crew-two"}, f"{sorted(cfgs)}")
        check("load: reloaded configuration content matches",
              cfgs["crew-two"]["slots"]["logic"] == "manny")
        rc, out, _ = _repl(["forge", "load nope", "leave", "quit"],
                           owner, do_load=True)
        check("load: unknown configuration rejected honestly",
              "No stored configuration named 'nope'" in out)
    finally:
        _cleanup(owner)


def part_preview_empty_defaults():
    owner = unique_owner("r75prev")
    try:
        rc, out, _ = _repl(["forge", "preview", "status", "leave", "quit"],
                           owner)
        check("preview: fusion ran on empty staging", "BIMO FUSION" in out)
        check("preview: defaults staging disclosed",
              "the fusion pass staged the default dock" in out)
        check("preview: staged arrangement now filled",
              "Staged: filled 11/11" in out)
    finally:
        _cleanup(owner)


def part_gate_and_scope():
    owner = unique_owner("r75gate")
    try:
        rc, out, _ = _repl([
            "forge", "grow", "say dock logic manny",
            "dock nowhere manny", "dock logic nobody", "leave", "quit",
        ], owner)
        check("gate: out-of-scope rejected",
              "that is not a forge command here" in out)
        check("gate: say-prefixed line rejected, not executed",
              out.count("that is not a forge command here") >= 2)
        check("gate: unknown slot rejected with reason",
              "unknown slot" in out)
        check("gate: unknown persona rejected with reason",
              "unknown persona" in out)
        st = _state(owner)
        check("gate: nothing staged reached the live body",
              all(v is None for v in st["bimo"]["slots"].values()))
    finally:
        _cleanup(owner)


def part_protection():
    from form.open import open_program
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix import agent_authority as aa
    owner = unique_owner("r75prot")
    try:
        p = open_program(owner)
        pr = p.nursery.add("S1", words="r75 protection fixture idea")
        pid = pr.id
        coord = ac.new_coordinator(p)
        coord.register_agent("ta", persona_slots={"pilot": "manny"})
        grant = aa.issue_root_grant(p, issuer="t", subject="ta",
                                    target=pid, content_pid=pid)
        handle = grant["grant_id"]
        p.save()
        rc, out, _ = _repl(["forge", f"dock logic {handle}", "leave"],
                           owner)
        check("protected line rejected", "Rejected: PROTECTED_MATERIAL" in out)
        check("handle absent from REPL output", handle not in out)
        from form.persist import _path
        with open(_path(owner), "rb") as f:
            blob = f.read().decode("utf-8", "replace")
        check("handle absent from persisted evidence", handle not in blob)
        recs = _state(owner)["forge_sessions"]["sessions"]
        if recs:
            kinds = [(s["kind"], s["result"]) for s in
                     next(iter(recs.values()))["steps"]]
            check("protected attempt recorded with safe code only",
                  ("protected", "rejected: PROTECTED_MATERIAL") in kinds,
                  f"{kinds}")
    finally:
        _cleanup(owner)


def part_eof_honesty():
    owner = unique_owner("r75eof")
    try:
        rc, out, _ = _repl(["forge", "dock logic manny", "save kept"],
                           owner)  # EOF inside the forge (no leave/quit)
        check("eof: session-not-saved stated plainly",
              "Forge session NOT saved (EOF)" in out)
        check("eof: committed-configurations-remain stated",
              "remain saved" in out)
        st = _state(owner)
        check("eof: no session evidence persisted",
              st["forge_sessions"]["sessions"] == {})
        check("eof: mid-session commit DID persist",
              "kept" in st["bimo_configurations"]["configurations"])
        check("eof: live body kept the committed arrangement",
              st["bimo"]["slots"]["logic"] == "manny")
    finally:
        _cleanup(owner)


def part_mutual_exclusion():
    owner = unique_owner("r75mux")
    try:
        rc, out, _ = _repl(["workshop bimo", "forge", "leave", "quit"],
                           owner)
        check("mux: forge inside workshop rejected by workshop gate",
              "Out of scope for the bimo workshop" in out)
        st = _state(owner)
        check("mux: no forge session recorded",
              st["forge_sessions"]["sessions"] == {})
        check("mux: workshop session recorded instead",
              len(st["workshop_sessions"]["sessions"]) == 1)
    finally:
        _cleanup(owner)


def part_schema_strictness():
    from form.dell_matrix.bimo_forge import (
        validate_configurations_section, validate_sessions_section,
        _MISSING)
    owner = "schemaowner"
    valid, mal = validate_configurations_section(_MISSING, owner)
    check("schema: absent configurations = legacy", valid == {} and mal is None)
    valid, mal = validate_sessions_section(_MISSING, owner)
    check("schema: absent sessions = legacy", valid == {} and mal is None)
    valid, mal = validate_configurations_section(None, owner)
    check("schema: explicit null fails closed, preserved",
          valid == {} and mal is not None)
    good = {"name": "crew", "owner": owner,
            "slots": {"logic": "manny"}, "pilot": "mathelody",
            "saved": "2026-10-22T00:00:00Z"}
    bad_variants = {
        "unknown slot": {**good, "slots": {"nope": "manny"}},
        "unknown persona": {**good, "slots": {"logic": "ghost"}},
        "foreign owner": {**good, "owner": "someoneelse"},
        "unknown pilot": {**good, "pilot": "ghost"},
        "authority field": {**good, "grants": ["everything"]},
        "non-canonical name": {**good, "name": "Bad Name"},
    }
    for label, rec in bad_variants.items():
        section = {"version": 1, "configurations": {rec["name"]: rec}}
        valid, mal = validate_configurations_section(section, owner)
        check(f"schema: {label} rejected + preserved",
              valid == {} and mal is not None and rec["name"] in mal)
    section = {"version": 1, "configurations": {"other": good}}
    valid, mal = validate_configurations_section(section, owner)
    check("schema: key/name mismatch rejected + preserved",
          valid == {} and mal is not None)
    section = {"version": 1, "configurations": {"crew": good}}
    valid, mal = validate_configurations_section(section, owner)
    check("schema: valid configuration accepted",
          valid.get("crew", {}).get("slots", {}).get("logic") == "manny"
          and mal is None)
    section = {"version": True, "configurations": {}}
    valid, mal = validate_configurations_section(section, owner)
    check("schema: bool version fails closed", valid == {} and mal is not None)


def part_commit_validation_and_atomicity():
    import form.repl as repl_mod
    from form.open import open_program
    from form.dell_matrix.bimo_forge import ForgeSession
    owner = unique_owner("r75atom")
    try:
        p = open_program(owner)
        p.bimo.pilot = "ghost_pilot"  # hand-edited invalid live state
        session = ForgeSession.open(p.owner, dict(p.bimo.slots), p.bimo.pilot)
        said = []
        orig_say = repl_mod._say
        repl_mod._say = lambda m: said.append(str(m))
        try:
            repl_mod._commit_forge_config(p, session, "crew")
        finally:
            repl_mod._say = orig_say
        out = "\n".join(said)
        check("commit: invalid staged pilot rejected at commit",
              "Save rejected" in out)
        check("commit: nothing stored on invalid commit",
              not getattr(p, "bimo_configurations", None))

        p.bimo.set_pilot("mathelody")
        session2 = ForgeSession.open(p.owner, dict(p.bimo.slots), p.bimo.pilot)
        session2.staged_slots["logic"] = "manny"
        from form import persist_rest
        orig_save = persist_rest.save

        def _boom(prog, *a, **k):
            raise RuntimeError("simulated save failure")
        persist_rest.save = _boom
        said = []
        repl_mod._say = lambda m: said.append(str(m))
        try:
            repl_mod._commit_forge_config(p, session2, "crew")
            p2, s2 = repl_mod._finish_forge(p, session2)
        finally:
            persist_rest.save = orig_save
            repl_mod._say = orig_say
        out = "\n".join(said)
        check("commit: save failure reported as SAVE_FAILED",
              "SAVE_FAILED" in out)
        check("commit: live body restored on failure",
              p.bimo.slots.get("logic") is None)
        check("commit: configurations restored on failure",
              not getattr(p, "bimo_configurations", None))
        check("commit: forge stays open after failed leave-save",
              s2 is session2)
        kinds = [(s["kind"], s["result"]) for s in session2.steps]
        check("commit: failure recorded with fixed code",
              ("save", "rejected: SAVE_FAILED") in kinds, f"{kinds}")
    finally:
        _cleanup(owner)


def part_bounds():
    from form.dell_matrix.bimo_forge import (
        ForgeSession, serialize_configurations_section,
        make_configuration)
    s = ForgeSession.open("o", {}, "mathelody")
    for i in range(60):
        s.record("dock", "docked")
    check("bounds: steps capped at 50", len(s.steps) == 50)
    configs = {}
    for i in range(12):
        cfg = make_configuration(f"c{i:02d}", "o", {}, "mathelody")
        cfg["saved"] = f"2026-10-22T00:{i:02d}:00Z"
        configs[cfg["name"]] = cfg
    section = serialize_configurations_section(configs, None, "o")
    check("bounds: configurations capped at 10",
          len(section["configurations"]) == 10)
    check("bounds: most recent configurations kept",
          "c11" in section["configurations"]
          and "c00" not in section["configurations"])


def part_adhoc_bimo_unchanged():
    owner = unique_owner("r75adhoc")
    try:
        rc, out, _ = _repl(
            ["bimo dock logic manny", "bimo", "save", "quit"], owner)
        check("adhoc: direct dock still works", "Docked" in out)
        check("adhoc: status renders", "Filled 1/11" in out)
        st = _state(owner)
        check("adhoc: dock persisted via the normal save path",
              st["bimo"]["slots"]["logic"] == "manny")
        rc, out, _ = _repl(["bimo clear", "save", "quit"], owner,
                           do_load=True)
        st = _state(owner)
        check("adhoc: clear persisted as before",
              all(v is None for v in st["bimo"]["slots"].values()))
    finally:
        _cleanup(owner)


def smoke() -> bool:
    part_happy_path()
    part_staging_isolation()
    part_load_roundtrip()
    part_preview_empty_defaults()
    part_gate_and_scope()
    part_protection()
    part_eof_honesty()
    part_mutual_exclusion()
    part_schema_strictness()
    part_commit_validation_and_atomicity()
    part_bounds()
    part_adhoc_bimo_unchanged()
    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"=== R7.5 BIMO Forge: {passed}/{len(CHECKS)} ===")
    return passed == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
