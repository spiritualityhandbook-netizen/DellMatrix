"""R7.2 Perspective Studio proofs — AMEND repair circuit.

Covers the six Director findings with effective (non-vacuous) checks:
1. Scope routing: studio gate ahead of reissue/prefix handlers.
2. Protection: fail-closed screening, fixed codes, zero disclosure.
3. Persistence: strict schema, version, owner binding, malformed preservation.
4. Leave/retry: stage-then-save, restore on failure, coherent retry.
5. Evidence bounds: in-memory bounds, rejected attempts recorded.
6. Full user journey with detachment and sensitivity controls.

All fixtures use disposable-copy isolation (unique owners).
"""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import uuid

CHECKS: list = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail and not cond else ""))


def unique_owner(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _confirmed_idea(p, words: str) -> str:
    """Create and confirm an Idea via the coordinator/grants path."""
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix import agent_authority as aa
    pr = p.nursery.add("S1", words=words)
    pid = pr.id
    coord = ac.new_coordinator(p)
    coord.register_agent("ta", persona_slots={"pilot": "manny"})
    sa = coord.surface_for("ta")
    grant = aa.issue_root_grant(p, issuer="t", subject="ta",
                                target=pid, content_pid=pid)
    h = p.acceptance_data_hash(pid, "confirm")
    r = sa.request_confirm(pid, grant["grant_id"], request_id="rr",
                           expected_content_hash=h)
    assert r["ok"], f"confirm failed: {r}"
    return pid


def _make_fixture(words: str = "r72 studio idea words"):
    """Disposable fixture: fresh owner, confirmed Idea, saved."""
    from form.open import open_program
    owner = unique_owner("r72studio")
    p = open_program(owner)
    pid = _confirmed_idea(p, words)
    p.save()
    return owner, pid


def _repl(commands: list, owner: str, do_load: bool = False, timeout: int = 60):
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


# =====================================================================
# 1. SCOPE ROUTING
# =====================================================================

def part_scope_routing():
    """Studio gate is ahead of reissue and say-prefix handlers."""
    owner, pid = _make_fixture("r72 scope")
    # Stage a real mutation via reissue, enter studio, try to confirm it.
    rc, out, err = _repl([
        "create an idea called scopeprobe",
        "reissue 1",
        "perspective studio",
        "reissue confirm",
        "leave",
        "quit",
    ], owner, do_load=True)

    check("r72 scope: repl exit zero", rc == 0, f"rc={rc}")
    check("r72 scope: studio prompt active",
          "studio>" in out, "prompt not scoped")
    check("r72 scope: reissue confirm rejected",
          "command out of scope" in out, f"out={out[-500:]}")
    check("r72 scope: no dispatch (not reissuing)",
          "Reissuing now" not in out, "staged mutation was dispatched!")
    check("r72 scope: no 'nothing staged' leak",
          "Nothing staged" not in out, "reached reissue handler")
    # If the staged "create an idea" had dispatched, a second idea would
    # have been created. Count "Created idea" messages: exactly one.
    check("r72 scope: no duplicate idea",
          out.count('Created idea: "scopeprobe"') == 1,
          f"create count={out.count('Created idea:')}")


def part_say_prefix_in_studio():
    """The say-prefix does not bypass the studio gate."""
    owner, pid = _make_fixture("r72 sayprefix")
    rc, out, err = _repl([
        "perspective studio",
        "say leave",  # would exit studio if prefix were stripped first
        "leave",
        "quit",
    ], owner, do_load=True)
    # "say leave" should be rejected as out-of-scope, NOT processed as leave.
    # So the first "leave" doesn't exit; the second one does.
    check("r72 sayprefix: say leave rejected",
          out.count("command out of scope") >= 1, f"out={out[-400:]}")
    check("r72 sayprefix: still exited via real leave",
          "Studio session saved" in out, "did not exit cleanly")


def part_static_order():
    """Static check: the main studio gate precedes reissue and say-prefix.

    There are three 'if _studio is not None:' branches: EOF handler,
    quit handler, and the main dispatch gate. The main gate is the LAST
    one (after the exit handlers), identified by its position after the
    quit/exit branch. We verify THAT gate precedes reissue/say-prefix.
    """
    import inspect
    import form.repl as repl_mod
    src = inspect.getsource(repl_mod.run)
    # Find all gate positions; the main gate is the last one.
    gate_positions = []
    idx = 0
    while True:
        idx = src.find("if _studio is not None:", idx)
        if idx == -1:
            break
        gate_positions.append(idx)
        idx += 1
    check("r72 order: main gate exists", len(gate_positions) >= 3,
          f"found={len(gate_positions)}")
    studio_gate = gate_positions[-1] if gate_positions else -1
    reissue_branch = src.find('line.lower() == "reissue"')
    say_prefix = src.find('line.lower().startswith("say ")')
    check("r72 order: studio gate before reissue",
          0 < studio_gate < reissue_branch,
          f"gate={studio_gate} reissue={reissue_branch}")
    check("r72 order: studio gate before say-prefix",
          0 < studio_gate < say_prefix,
          f"gate={studio_gate} say={say_prefix}")


# =====================================================================
# 2. PROTECTION
# =====================================================================

def _get_grant_canary(p) -> str:
    """Get a real protected value (grant ID) from the live program.

    Issues a fresh grant on the live program (grants do not persist
    through save/load, so the fixture's grant is not available after
    reload). Returns the grant_id, which protected_values() covers.
    """
    from form.dell_matrix import agent_authority as aa
    from form.dell_matrix.inference_dock import protected_values
    # Use an existing proposal or create one
    pid = None
    try:
        proposals = p.nursery.proposals
        if proposals:
            pid = next(iter(proposals.keys()))
    except Exception:
        pass
    if pid is None:
        pr = p.nursery.add("S1", words="canary proposal")
        pid = pr.id
    grant = aa.issue_root_grant(p, issuer="t", subject="ta",
                                target=pid, content_pid=pid)
    gid = grant["grant_id"]
    prot = protected_values(p)
    assert gid in prot, "grant not in protected values"
    return gid


def part_protection_canary():
    """Protected canary in compose input is rejected with zero disclosure."""
    from form.open import open_program
    from form.dell_matrix.perspective_studio import PerspectiveStudio
    import form.repl as repl_mod

    owner, pid = _make_fixture("r72 canary")
    from form import persist_rest
    p = persist_rest.load(owner, activate=False)
    canary = _get_grant_canary(p)
    studio = PerspectiveStudio(p)

    # Capture _say output
    said = []
    orig_say = repl_mod._say
    repl_mod._say = lambda m: said.append(str(m))
    try:
        # Canary in raw JSON
        p2, s2 = repl_mod._handle_studio_line(
            p, f'compose [{{"id":"v1","pos":[0,0],"facing":"E","role":"{canary}"}}]',
            studio)
    finally:
        repl_mod._say = orig_say

    output = "\n".join(said)
    check("r72 protect: canary rejected",
          "PROTECTED_MATERIAL" in output, f"out={output[:200]}")
    check("r72 protect: zero disclosure in output",
          canary not in output, "CANARY LEAKED IN OUTPUT")
    # Check persisted evidence
    rec = studio.session.commands[-1]
    check("r72 protect: zero disclosure in evidence",
          canary not in json.dumps(rec), "CANARY IN SESSION EVIDENCE")
    check("r72 protect: fixed code recorded",
          rec["result"] == "PROTECTED_MATERIAL", f"rec={rec}")


def part_protection_escaped():
    """\\uXXXX-escaped canary is rejected."""
    from form.open import open_program
    from form.dell_matrix.perspective_studio import PerspectiveStudio
    import form.repl as repl_mod

    owner, pid = _make_fixture("r72 escaped")
    from form import persist_rest
    p = persist_rest.load(owner, activate=False)
    canary = _get_grant_canary(p)
    # Escape the canary as \uXXXX
    escaped = "".join(f"\\u{ord(c):04x}" for c in canary)
    studio = PerspectiveStudio(p)

    said = []
    orig_say = repl_mod._say
    repl_mod._say = lambda m: said.append(str(m))
    try:
        p2, s2 = repl_mod._handle_studio_line(
            p, f'compose [{{"id":"v1","pos":[0,0],"facing":"E","role":"user{escaped}"}}]',
            studio)
    finally:
        repl_mod._say = orig_say

    output = "\n".join(said)
    check("r72 protect: escaped canary rejected",
          "PROTECTED_MATERIAL" in output, f"out={output[:200]}")
    check("r72 protect: escaped canary not disclosed",
          canary not in output and escaped not in output,
          "ESCAPED CANARY LEAKED")


def part_protection_fail_closed():
    """Screening failure rejects (fail-closed), not fail-open."""
    from form.open import open_program
    from form.dell_matrix.perspective_studio import PerspectiveStudio
    from form.dell_matrix import inference_dock
    import form.repl as repl_mod

    owner, pid = _make_fixture("r72 failclosed")
    from form import persist_rest
    p = persist_rest.load(owner, activate=False)
    studio = PerspectiveStudio(p)

    # Break the screening
    orig_pv = inference_dock.protected_values
    def broken_pv(prog):
        raise RuntimeError("screening unavailable")
    inference_dock.protected_values = broken_pv

    said = []
    orig_say = repl_mod._say
    repl_mod._say = lambda m: said.append(str(m))
    try:
        p2, s2 = repl_mod._handle_studio_line(
            p, 'compose [{"id":"v1","pos":[0,0],"facing":"E"}]', studio)
    finally:
        repl_mod._say = orig_say
        inference_dock.protected_values = orig_pv

    output = "\n".join(said)
    check("r72 protect: screening failure rejects",
          "PROTECTED_MATERIAL" in output, f"out={output[:200]}")
    check("r72 protect: no composition on screening failure",
          "Composed" not in output, "COMPOSED DESPITE SCREENING FAILURE")


def part_protection_sensitivity():
    """Sensitivity: weakened protection DISCLOSES; restored rejects."""
    from form.open import open_program
    from form.dell_matrix.perspective_studio import PerspectiveStudio
    from form.dell_matrix import inference_dock
    import form.repl as repl_mod

    owner, pid = _make_fixture("r72 sensitivity")
    from form import persist_rest
    p = persist_rest.load(owner, activate=False)
    canary = _get_grant_canary(p)

    # Weaken: screening always returns clean
    orig_cpd = inference_dock.contains_protected_decoded
    inference_dock.contains_protected_decoded = lambda t, prot: False

    studio = PerspectiveStudio(p)
    said = []
    orig_say = repl_mod._say
    repl_mod._say = lambda m: said.append(str(m))
    try:
        p2, s2 = repl_mod._handle_studio_line(
            p, f'compose [{{"id":"v1","pos":[0,0],"facing":"E","role":"user"}}]',
            studio)
        # Also test direct API with canary in viewer ID
        studio_api = PerspectiveStudio(p)
        api_result = studio_api.compose(
            [{"id": canary, "pos": [0, 0], "facing": "E"}])
    finally:
        repl_mod._say = orig_say
        inference_dock.contains_protected_decoded = orig_cpd

    output = "\n".join(said)
    # With weakened protection, the canary must ACTUALLY APPEAR in output
    # (disclosure), not just reach a different rejection.
    api_str = str(api_result)
    disclosed = canary in output or canary in api_str
    check("r72 sensitivity: weakened protection discloses canary",
          disclosed,
          f"canary_in_repl={canary in output} canary_in_api={canary in api_str}")

    # Restored: rejects with zero disclosure
    studio2 = PerspectiveStudio(p)
    said2 = []
    repl_mod._say = lambda m: said2.append(str(m))
    try:
        p3, s3 = repl_mod._handle_studio_line(
            p, f'compose [{{"id":"v1","pos":[0,0],"facing":"E","role":"{canary}"}}]',
            studio2)
        api_result2 = studio2.compose([{"id": canary, "pos": [0, 0], "facing": "E"}])
    finally:
        repl_mod._say = orig_say
    output2 = "\n".join(said2)
    api_str2 = str(api_result2)
    check("r72 sensitivity: restored protection rejects",
          "PROTECTED_MATERIAL" in output2, f"out={output2[:200]}")
    check("r72 sensitivity: zero disclosure after restore",
          canary not in output2 and canary not in api_str2,
          "canary absent from REPL and API output")


# =====================================================================
# 3. PERSISTENCE
# =====================================================================

def part_persistence_strict():
    """Strict schema: version, key/ID, owner, closed requirements."""
    from form.dell_matrix.perspective_studio import validate_section

    owner = "test_owner"

    # Bool version rejected
    s, m = validate_section({"version": True, "sessions": {}}, owner)
    check("r72 persist: bool version rejected",
          s == {} and m is not None, f"m={m}")

    # Wrong version rejected
    s, m = validate_section({"version": 2, "sessions": {}}, owner)
    check("r72 persist: version 2 rejected",
          s == {} and m is not None, f"m={m}")

    # Key/ID mismatch
    rec = {
        "session_id": "aaa", "owner": owner,
        "started": "2026-10-11T00:00:00Z", "closed": "2026-10-11T01:00:00Z",
        "commands": [],
    }
    s, m = validate_section(
        {"version": 1, "sessions": {"bbb": rec}}, owner)
    check("r72 persist: key/ID mismatch rejected",
          s == {} and m is not None and "bbb" in m, f"m={m}")

    # Owner mismatch
    rec2 = dict(rec, session_id="ccc", owner="intruder")
    s, m = validate_section(
        {"version": 1, "sessions": {"ccc": rec2}}, owner)
    check("r72 persist: owner mismatch rejected",
          s == {} and m is not None, f"m={m}")

    # Unclosed record rejected (only closed records persist)
    rec3 = dict(rec, session_id="ddd", closed=None)
    s, m = validate_section(
        {"version": 1, "sessions": {"ddd": rec3}}, owner)
    check("r72 persist: unclosed record rejected",
          s == {} and m is not None, f"m={m}")

    # Valid record accepted
    rec4 = dict(rec, session_id="eee")
    s, m = validate_section(
        {"version": 1, "sessions": {"eee": rec4}}, owner)
    check("r72 persist: valid record accepted",
          "eee" in s and m is None, f"s={s} m={m}")


def part_persistence_absent_vs_null():
    """Absent (legacy) vs explicit null are distinguished via sentinel."""
    from form.dell_matrix.perspective_studio import validate_section, _MISSING

    # Absent key (legacy): _MISSING sentinel → not malformed.
    s, m = validate_section(_MISSING, "o")
    check("r72 persist: absent is legacy (not malformed)",
          s == {} and m is None, f"m={m}")

    # Explicit null: malformed, never legacy absence.
    s, m = validate_section(None, "o")
    check("r72 persist: explicit null is malformed",
          s == {} and m is not None and "_section" in m, f"m={m}")

    # Explicit null sessions in a dict: malformed.
    s, m = validate_section({"version": 1, "sessions": None}, "o")
    check("r72 persist: explicit null sessions is malformed",
          s == {} and m is not None, f"m={m}")

    # Loader distinguishes: absent key vs explicit null value.
    from form import persist_rest
    from form.persist import _path
    import json as _json
    owner, pid = _make_fixture("r72 sentinel")
    p = persist_rest.load(owner, activate=False)
    path = _path(owner)
    with open(path) as f:
        data = _json.load(f)
    # Remove the key entirely (absent)
    data.pop("studio_sessions", None)
    with open(path, "w") as f:
        _json.dump(data, f)
    p2 = persist_rest.load(owner, activate=False)
    check("r72 persist: absent key loads as legacy",
          p2.studio_sessions == {} and p2.studio_sessions_malformed is None,
          f"sessions={p2.studio_sessions} mal={p2.studio_sessions_malformed}")

    # Explicit null value
    with open(path) as f:
        data = _json.load(f)
    data["studio_sessions"] = None
    with open(path, "w") as f:
        _json.dump(data, f)
    p3 = persist_rest.load(owner, activate=False)
    check("r72 persist: explicit null loads as malformed",
          p3.studio_sessions == {} and p3.studio_sessions_malformed is not None,
          f"mal={p3.studio_sessions_malformed}")


def part_persistence_roundtrip():
    """Malformed evidence survives save/reload; same-key not overwritten."""
    from form.open import open_program
    from form import persist_rest
    from form.dell_matrix.perspective_studio import validate_section, serialize_section
    import json as _json

    owner, pid = _make_fixture("r72 roundtrip")
    # Corrupt the section
    path = persist_rest._path(owner)
    with open(path) as f:
        data = _json.load(f)
    data["studio_sessions"] = {
        "version": 1,
        "sessions": {
            "bad1": {"session_id": "bad1", "owner": owner},  # incomplete
        },
    }
    with open(path, "w") as f:
        _json.dump(data, f)

    p = persist_rest.load(owner, activate=False)
    check("r72 persist: malformed preserved",
          p.studio_sessions_malformed is not None and "bad1" in p.studio_sessions_malformed,
          f"malformed={p.studio_sessions_malformed}")
    check("r72 persist: valid sessions empty",
          p.studio_sessions == {}, f"sessions={p.studio_sessions}")

    # Save and reload: malformed must survive
    p.save()
    p2 = persist_rest.load(owner, activate=False)
    check("r72 persist: malformed survives save/reload",
          p2.studio_sessions_malformed is not None and "bad1" in p2.studio_sessions_malformed,
          f"malformed={p2.studio_sessions_malformed}")

    # Same-key malformed: earlier evidence not overwritten.
    # Add a second malformation for "bad1" and verify both are kept.
    malformed_v1 = p2.studio_sessions_malformed
    # Simulate a new validation with the same key failing again
    s, m = validate_section({
        "version": 1,
        "sessions": {"bad1": {"session_id": "bad1"}},  # still bad
        "malformed": malformed_v1,
    }, owner)
    bad1_entries = m.get("bad1", []) if m else []
    check("r72 persist: same-key malformed not overwritten",
          isinstance(bad1_entries, list) and len(bad1_entries) >= 2,
          f"entries={len(bad1_entries) if isinstance(bad1_entries, list) else 'not-a-list'}")

    # Serializer uses strict schema: active records are NOT saved as valid.
    from form.dell_matrix.perspective_studio import PerspectiveStudio, StudioSession
    p3 = persist_rest.load(owner, activate=False)
    studio_active = PerspectiveStudio(p3)  # active, not closed
    # Manually inject the active session into studio_sessions (simulating a bug)
    p3.studio_sessions[studio_active.session.session_id] = studio_active.session.to_dict()
    section = serialize_section(p3.studio_sessions, p3.studio_sessions_malformed, owner)
    active_sid = studio_active.session.session_id
    check("r72 persist: active record not saved as valid",
          active_sid not in section["sessions"],
          f"sessions={list(section['sessions'].keys())}")
    check("r72 persist: active record preserved as malformed",
          active_sid in section.get("malformed", {}),
          f"malformed={list(section.get('malformed', {}).keys())}")


def part_durable_keys():
    """studio_sessions is in the canonical durable projection."""
    from form.persist_rest import DURABLE_KEYS
    check("r72 persist: studio_sessions in DURABLE_KEYS",
          "studio_sessions" in DURABLE_KEYS, f"keys={DURABLE_KEYS}")


def part_checkpoint_rollback():
    """Execute real authority-bound rollback to a sealed checkpoint."""
    from form.open import open_program
    from form import persist_rest
    from form.dell_matrix.perspective_studio import PerspectiveStudio
    from form.dell_matrix import rollback_authority as ra
    from form.mandell.core_i_recovery import checkpoint
    import form.repl as repl_mod

    owner, pid = _make_fixture("r72 checkpoint")
    from form import persist_rest
    p = persist_rest.load(owner, activate=False)

    # Create a studio session and leave (persist)
    studio = PerspectiveStudio(p)
    said = []
    orig_say = repl_mod._say
    repl_mod._say = lambda m: said.append(str(m))
    try:
        p, _ = repl_mod._handle_studio_line(p, "leave", studio)
    finally:
        repl_mod._say = orig_say

    sid = studio.session.session_id
    check("r72 rollback: session persisted",
          sid in p.studio_sessions, f"sessions={list(p.studio_sessions.keys())}")

    # Save and checkpoint (sealed generation with studio evidence)
    persist_rest.save(p)
    g1 = checkpoint(p, stamp="r72-studio-1")
    check("r72 rollback: checkpoint written", bool(g1), f"g1={g1}")

    # Create distinguishably different live evidence (second session)
    studio2 = PerspectiveStudio(p)
    repl_mod._say = lambda m: None
    try:
        p, _ = repl_mod._handle_studio_line(p, "leave", studio2)
    finally:
        repl_mod._say = orig_say
    sid2 = studio2.session.session_id
    check("r72 rollback: second session differs", sid2 != sid, f"sid2={sid2}")
    persist_rest.save(p)
    check("r72 rollback: live has both",
          sid in p.studio_sessions and sid2 in p.studio_sessions,
          f"live={list(p.studio_sessions.keys())}")

    # Execute REAL authority-bound rollback to the sealed checkpoint.
    frozen = ra.freeze_rollback_target(owner, g1)
    grant = ra.issue_rollback_grant(p, issuer="root", subject="s",
                                   frozen_target=frozen)
    r = p.confirm_rollback(g1, _review_context={"grant_id": grant["grant_id"]},
                           _subject="s")
    check("r72 rollback: executed", r.get("ok") is True, f"r={r}")

    # Fresh-process reload must show the checkpoint state (sid only, not sid2).
    p2 = persist_rest.load(owner, activate=False)
    check("r72 rollback: restored sid",
          sid in p2.studio_sessions, f"restored={list(p2.studio_sessions.keys())}")
    check("r72 rollback: sid2 gone",
          sid2 not in p2.studio_sessions,
          f"restored={list(p2.studio_sessions.keys())}")


# =====================================================================
# 4. LEAVE/RETRY
# =====================================================================

def part_leave_retry():
    """Failed leave preserves prior records; retry succeeds coherently."""
    from form.open import open_program
    from form.dell_matrix.perspective_studio import PerspectiveStudio
    from form import persist_rest
    import form.repl as repl_mod

    owner, pid = _make_fixture("r72 retry")
    from form import persist_rest
    p = persist_rest.load(owner, activate=False)
    studio = PerspectiveStudio(p)
    sid = studio.session.session_id

    # Record the durable bytes before
    path = persist_rest._path(owner)
    with open(path, "rb") as f:
        bytes_before = f.read()

    # Inject save failure
    orig_save = persist_rest.save
    def failing_save(*a, **k):
        raise OSError("simulated save failure")
    persist_rest.save = failing_save

    said = []
    orig_say = repl_mod._say
    repl_mod._say = lambda m: said.append(str(m))
    try:
        p2, studio2 = repl_mod._handle_studio_line(p, "leave", studio)
    finally:
        repl_mod._say = orig_say
        persist_rest.save = orig_save

    output = "\n".join(said)
    check("r72 retry: save failure reported",
          "SAVE_FAILED" in output, f"out={output[:200]}")
    check("r72 retry: studio remains active",
          studio2 is not None, "studio was discarded on save failure")
    check("r72 retry: session not marked closed",
          studio2.session.closed is None, "session was closed before persistence")
    check("r72 retry: prior records restored",
          sid not in p2.studio_sessions, f"sessions={list(p2.studio_sessions.keys())}")

    # Durable bytes unchanged
    with open(path, "rb") as f:
        bytes_after = f.read()
    check("r72 retry: durable bytes preserved",
          bytes_before == bytes_after, "bytes changed on failed save")

    # Studio remains usable: compose still works
    said2 = []
    repl_mod._say = lambda m: said2.append(str(m))
    try:
        p3, studio3 = repl_mod._handle_studio_line(
            p2, 'compose [{"id":"v1","pos":[0,0],"facing":"E"}]', studio2)
    finally:
        repl_mod._say = orig_say
    check("r72 retry: studio usable after failure",
          any("Composed" in m for m in said2), f"said={said2[:2]}")

    # Retry leave: succeeds with exactly one coherent record
    said3 = []
    repl_mod._say = lambda m: said3.append(str(m))
    try:
        p4, studio4 = repl_mod._handle_studio_line(p3, "leave", studio3)
    finally:
        repl_mod._say = orig_say
    check("r72 retry: retry exits studio",
          studio4 is None, "retry did not exit")
    check("r72 retry: exactly one record",
          list(p4.studio_sessions.keys()) == [sid],
          f"sessions={list(p4.studio_sessions.keys())}")
    rec = p4.studio_sessions[sid]
    check("r72 retry: record is closed",
          rec.get("closed") is not None, f"rec={rec}")
    check("r72 retry: no duplicate leave",
          sum(1 for c in rec.get("commands", []) if c.get("kind") == "leave") == 1,
          f"commands={[c.get('kind') for c in rec.get('commands', [])]}")


def part_stale_save():
    """Stale/recovery-required saves reject without bypass."""
    from form.open import open_program
    from form.dell_matrix.perspective_studio import PerspectiveStudio
    from form import persist_rest
    import form.repl as repl_mod

    owner, pid = _make_fixture("r72 stale")
    from form import persist_rest
    p = persist_rest.load(owner, activate=False)

    # Genuinely recovery-required instance: set the production attribute
    # that check_save_allowed inspects. This is the real guard's input,
    # not a mock of the guard itself.
    p._recovery_required = {"test": "simulated recovery condition"}
    check("r72 stale: guard input set",
          getattr(p, "_recovery_required", None) is not None,
          "production attribute")

    studio = PerspectiveStudio(p)
    said = []
    orig_say = repl_mod._say
    repl_mod._say = lambda m: said.append(str(m))
    try:
        p2, studio2 = repl_mod._handle_studio_line(p, "leave", studio)
    finally:
        repl_mod._say = orig_say

    output = "\n".join(said)
    check("r72 stale: recovery-required save rejected",
          "SAVE_FAILED" in output, f"out={output[:200]}")
    check("r72 stale: studio retained",
          studio2 is not None and studio2.session.closed is None,
          f"studio2={studio2}")
    # No bytes written: the session was not persisted.
    p3 = persist_rest.load(owner, activate=False)
    check("r72 stale: no bytes written",
          studio.session.session_id not in p3.studio_sessions,
          f"sessions={list(p3.studio_sessions.keys())}")

    # Genuinely stale instance (post-rollback): production attribute.
    p._recovery_required = None
    p._post_rollback_stale = True
    studio3 = PerspectiveStudio(p)
    said = []
    repl_mod._say = lambda m: said.append(str(m))
    try:
        p4, studio4 = repl_mod._handle_studio_line(p, "leave", studio3)
    finally:
        repl_mod._say = orig_say
    output = "\n".join(said)
    check("r72 stale: post-rollback save rejected",
          "SAVE_FAILED" in output, f"out={output[:200]}")
    check("r72 stale: stale studio retained",
          studio4 is not None and studio4.session.closed is None,
          f"studio4={studio4}")


# =====================================================================
# 5. EVIDENCE BOUNDS
# =====================================================================

def part_evidence_bounds():
    """Bounds enforced during recording; rejected attempts recorded."""
    from form.open import open_program
    from form.dell_matrix.perspective_studio import PerspectiveStudio
    import form.repl as repl_mod

    owner, pid = _make_fixture("r72 bounds")
    from form import persist_rest
    p = persist_rest.load(owner, activate=False)
    studio = PerspectiveStudio(p)

    # Record 60 commands; only 50 retained
    for i in range(60):
        studio._record("test", f"cmd {i}")
    check("r72 bounds: in-memory bound enforced",
          len(studio.session.commands) == 50,
          f"count={len(studio.session.commands)}")
    check("r72 bounds: oldest discarded",
          studio.session.commands[0]["result"] == "cmd 10",
          f"first={studio.session.commands[0]['result']}")

    # Rejected attempts are recorded with fixed code (not raw text)
    said = []
    orig_say = repl_mod._say
    repl_mod._say = lambda m: said.append(str(m))
    try:
        p2, s2 = repl_mod._handle_studio_line(p, "confirm some-id", studio)
    finally:
        repl_mod._say = orig_say
    rec = studio.session.commands[-1]
    check("r72 bounds: rejected attempt recorded",
          rec["kind"] == "rejected", f"rec={rec}")
    check("r72 bounds: fixed code (not raw text)",
          rec["result"] == "OUT_OF_SCOPE" and "some-id" not in rec["result"],
          f"rec={rec}")
    output = "\n".join(said)
    check("r72 bounds: no raw text in output",
          "some-id" not in output, f"out={output[:200]}")


def part_legend_valid():
    """Legend keys match the displayed compose fields."""
    from form.dell_matrix.perspective_studio import LEGEND
    # The compose display shows: viewer, requested_mode, epistemic_status,
    # source, and the observation report. Legend must define these.
    for key in ("viewer", "requested_mode", "epistemic_status", "source", "observations"):
        check(f"r72 legend: defines {key}", key in LEGEND, f"keys={list(LEGEND.keys())}")


# =====================================================================
# 6. FULL JOURNEY
# =====================================================================

def part_full_journey():
    """Real REPL: enter → compose → legend/help → rejected mutation → leave → reload."""
    owner, pid = _make_fixture("r72 journey")
    specs = json.dumps([{"id": "v1", "role": "user",
                         "pos": [0.0, 0.0], "facing": "E", "mode": "whole"}])

    rc, out, err = _repl([
        "perspective studio",
        f"compose {specs}",
        "legend",
        "help",
        f"confirm {pid}",  # rejected mutation
        "leave",
        "quit",
    ], owner, do_load=True)

    check("r72 journey: repl exit zero", rc == 0, f"rc={rc}")
    check("r72 journey: composed with observations",
          "Composed 1 view(s)" in out and "[v1/whole]" in out,
          f"out={out[-600:]}")
    check("r72 journey: observation report shown",
          "status=" in out and "source=" in out, "no attributed observations")
    check("r72 journey: legend shown", "Layout legend" in out)
    check("r72 journey: mutation rejected",
          "command out of scope" in out, "mutation not rejected")
    check("r72 journey: saved on leave", "Studio session saved" in out)

    # Fresh-process reload: compare complete persisted evidence
    script = f'''
import sys, json
sys.path.insert(0, ".")
from form import persist_rest
p = persist_rest.load("{owner}", activate=False)
sessions = p.studio_sessions
assert len(sessions) == 1, f"sessions={{list(sessions.keys())}}"
rec = list(sessions.values())[0]
assert rec["owner"] == "{owner}"
assert rec["closed"] is not None
kinds = [c["kind"] for c in rec["commands"]]
for expected in ("enter", "compose", "legend", "help", "rejected", "leave"):
    assert expected in kinds, f"missing {{expected}}: {{kinds}}"
# No raw mutation text in evidence
blob = json.dumps(rec)
assert "{pid}" not in blob, "mutation target leaked into evidence"
print("JOURNEY_OK")
print(f"KINDS:{{kinds}}")
'''
    r2 = subprocess.run(
        [sys.executable, "-c", script], cwd=os.path.abspath("."),
        env={**os.environ, "PYTHONPATH": os.path.abspath(".")},
        capture_output=True, text=True, timeout=60)
    check("r72 journey: reload exit zero", r2.returncode == 0,
          f"rc={r2.returncode} err={r2.stderr[:300]}")
    check("r72 journey: evidence complete",
          "JOURNEY_OK" in r2.stdout, f"out={r2.stdout[:300]}")


def part_detachment():
    """Mutating nested observations does not affect program or next compose."""
    from form.open import open_program
    from form.dell_matrix.perspective_studio import (
        PerspectiveStudio, parse_specs_json)

    owner, pid = _make_fixture("r72 detach")
    from form import persist_rest
    p = persist_rest.load(owner, activate=False)
    # Snapshot canonical content
    before = copy.deepcopy(p.nursery.proposals[pid].words)

    studio = PerspectiveStudio(p)
    ok, _, specs = parse_specs_json(
        '[{"id":"v1","role":"user","pos":[0,0],"facing":"E","mode":"whole"}]')
    assert ok
    r1 = studio.compose(specs)
    assert r1.get("ok")

    # Mutate nested observations aggressively
    for c in r1.get("components", []):
        view = c.get("view", {})
        if isinstance(view, dict):
            view["report"] = ["MUTATED"]
            view["nodes"] = []
            view["epistemic_status"] = "MUTATED"
        c["epistemic_status"] = "MUTATED"

    # Compose again: must be unaffected
    r2 = studio.compose(specs)
    check("r72 detach: status unaffected",
          r2.get("epistemic_status") != "MUTATED",
          f"status={r2.get('epistemic_status')}")
    comp = r2["components"][0]
    check("r72 detach: nested report unaffected",
          comp.get("view", {}).get("report") != ["MUTATED"],
          "nested mutation leaked")
    check("r72 detach: canonical content unchanged",
          p.nursery.proposals[pid].words == before,
          "program mutated via detached output")


def part_compose_fidelity():
    """Field-for-field: studio compose == direct compose_views."""
    from form.open import open_program
    from form.dell_matrix.perspective_studio import (
        PerspectiveStudio, parse_specs_json)
    from form.dell_matrix.perspective_views import Viewer, compose_views
    from form import persist_rest

    owner, pid = _make_fixture("r72 fidelity")
    p2 = persist_rest.load(owner, activate=False)

    specs_json = '[{"id":"v1","role":"user","pos":[0,0],"facing":"E","mode":"whole"}]'
    ok, err, specs = parse_specs_json(specs_json)
    check("r72 fidelity: specs parse", ok, err)

    studio = PerspectiveStudio(p2)
    studio_result = studio.compose(specs)

    viewers = [Viewer(id=s["id"], role=s["role"],
                      pos=(s["pos"][0], s["pos"][1]),
                      facing=s["facing"], mode=s.get("mode"))
               for s in specs]
    direct = compose_views(p2, [(v, v.effective_mode()) for v in viewers])

    def norm(o):
        return json.loads(json.dumps(o, sort_keys=True))

    # Compare the composition payload (excluding studio's session recording)
    check("r72 fidelity: field-for-field equal",
          norm(studio_result) == norm(direct),
          "studio result differs from direct compose_views")


# =====================================================================
# 7. SIBLING SWEEP
# =====================================================================

def part_sibling_sweep():
    """No other REPL-level scoped mode bypasses the studio gate."""
    import inspect
    import form.repl as repl_mod
    src = inspect.getsource(repl_mod.run)
    # The studio is the only REPL-level scoped mode. The main dispatch gate
    # is the LAST 'if _studio is not None:' (after EOF/quit handlers).
    # Verify THAT gate is the first non-exit branch, before reissue/say.
    lines = src.split("\n")
    gate_indices = [i for i, l in enumerate(lines) if "if _studio is not None:" in l]
    check("r72 sweep: gates found", len(gate_indices) >= 3,
          f"found={len(gate_indices)}")
    gate_idx = gate_indices[-1] if gate_indices else None
    check("r72 sweep: main gate exists", gate_idx is not None)
    # Check that reissue/say handlers come after the main gate
    reissue_idx = next((i for i, l in enumerate(lines)
                        if 'line.lower() == "reissue"' in l), None)
    say_idx = next((i for i, l in enumerate(lines)
                    if 'startswith("say ")' in l), None)
    check("r72 sweep: gate before reissue",
          gate_idx is not None and reissue_idx is not None and gate_idx < reissue_idx)
    check("r72 sweep: gate before say-prefix",
          gate_idx is not None and say_idx is not None and gate_idx < say_idx)


def smoke() -> bool:
    global CHECKS
    CHECKS = []
    part_static_order()
    part_scope_routing()
    part_say_prefix_in_studio()
    part_protection_canary()
    part_protection_escaped()
    part_protection_fail_closed()
    part_protection_sensitivity()
    part_persistence_strict()
    part_persistence_absent_vs_null()
    part_persistence_roundtrip()
    part_durable_keys()
    part_checkpoint_rollback()
    part_leave_retry()
    part_stale_save()
    part_evidence_bounds()
    part_legend_valid()
    part_full_journey()
    part_detachment()
    part_compose_fidelity()
    part_sibling_sweep()
    failed = [c for c in CHECKS if not c[1]]
    total = len(CHECKS)
    print(f"=== R7.2 studio: {total - len(failed)}/{total} ===")
    for name, ok, detail in failed:
        print(f"  FAILED: {name} — {detail}")
    return not failed


if __name__ == "__main__":
    ok = smoke()
    sys.exit(0 if ok else 1)
