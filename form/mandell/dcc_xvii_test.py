#!/usr/bin/env python3
"""DCC-XVII: Crash-safe persistence + durable state recovery (Persistence V2).

Success definition under test: a failed or interrupted save cannot turn a
previously valid canonical knowledge state into a partially serialized
generation under the documented filesystem assumptions. A fresh process sees
a complete old generation or a complete new generation, and load failure
never partially mutates live state.

Controls:
  A  normal save (nursery + program file); fresh process loads exactly G2; no temps
  B  serialization failure -> G1 unchanged
  C  temp-write failure -> canonical G1; partial temp cannot masquerade
  D  pre-replace crash (literal os._exit) -> G1            [cross-process]
  E  post-replace crash (literal os._exit) -> G2 complete  [cross-process]
  F  SIGKILL during temp write -> canonical G1 intact      [cross-process]
  G  repeated saves G1->G4; latest completed generation visible
  H  large payload preserves the generation boundary
  I  unicode/escaping round-trip
  J  legacy V1 JSON loads without migration; next save uses V2 mechanics
  K  corrupt canonical -> explicit honest failure (never empty state)
  L  IO/permission failures -> honest failure, canonical intact
  M  supersession integration: persistence interruption -> OLD or NEW COMPLETE
  N  lineage/dependency integration across a crash
  O  contextual routing reproduces across a save/load cycle [cross-process]
  P  owner isolation
  Q  temp isolation (no cross-owner load)
  R  determinism (save->load->save byte-identical)
  S  byte preservation for every pre-replace failure
  T  load failure atomicity (stage/validate before apply)
  U  literal cross-process matrix (distinct PIDs, no-memory canary)
  V  cleanup (no temp accumulation; stale-temp sweep)

AUTONOMY = NO.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from form.open import open_program
from form import persist_rest
from form.persist import _STATE_DIR
from form.dell_matrix import atomic_write as AW
from form.dell_matrix.atomic_write import (
    AtomicWriteError,
    sweep_stale_tmps,
    PERSISTENCE_PROTOCOL_VERSION,
)
from form.dell_matrix.nursery import (
    Nursery,
    NurseryLoadError,
    Proposal,
    owner_nursery_path,
)

STATE = Path(_STATE_DIR)
OWNERS: list[str] = []

CHECKS: list[tuple[str, bool]] = []


def check(name: str, cond: bool) -> None:
    CHECKS.append((name, bool(cond)))


def wipe_owner(owner: str) -> None:
    for f in STATE.glob(f"*{owner}*"):
        try:
            if f.is_file():
                f.unlink()
        except OSError:
            pass


def clean_tmps() -> None:
    for t in tmps_in_state():
        try:
            (STATE / t).unlink()
        except OSError:
            pass


def fresh_owner(owner: str):
    wipe_owner(owner)
    if owner not in OWNERS:
        OWNERS.append(owner)
    return open_program(owner)


def npath(owner: str) -> Path:
    return Path(owner_nursery_path(owner))


def read_bytes(p: Path) -> bytes:
    with open(p, "rb") as f:
        return f.read()


def tmps_in_state() -> list[str]:
    return [f.name for f in STATE.glob("*.dmtmp.*")] if STATE.is_dir() else []


# ---------------------------------------------------------------- CONTROL A
def control_a_normal_save() -> None:
    o = "DCCXVII_A"
    p = fresh_owner(o)
    pr = p.nursery.add("alpha base", words="alpha beta gamma")
    p.confirm_proposal(pr.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": pr.id})
    p.nursery.save()
    persist_rest.save(p)
    np, pp = npath(o), Path(persist_rest._path(p.owner))
    assert np.is_file() and pp.is_file()
    g2_nursery, g2_prog = read_bytes(np), read_bytes(pp)
    n2 = Nursery.load(str(np))
    assert set(n2.proposals) == set(p.nursery.proposals)
    p2 = persist_rest.load(o, activate=False)
    assert set(p2.cube.session.plane.units) == set(p.cube.session.plane.units)
    check("A.nursery_roundtrip", True)
    check("A.program_roundtrip", True)
    check("A.no_temp_artifacts", tmps_in_state() == [])
    check("A.g2_bytes_stable", read_bytes(np) == g2_nursery and read_bytes(pp) == g2_prog)
    print("  A normal save: GREEN")


# ---------------------------------------------------------------- CONTROL B
def control_b_serialize_failure() -> None:
    o = "DCCXVII_B"
    p = fresh_owner(o)
    pr = p.nursery.add("beta base", words="beta gamma")
    p.confirm_proposal(pr.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": pr.id})
    p.nursery.save()
    np = npath(o)
    g1 = read_bytes(np)
    try:
        p.nursery.save(_fail_at="serialize")
        raised = False
    except AtomicWriteError:
        raised = True
    check("B.raises", raised)
    check("B.canonical_untouched", read_bytes(np) == g1)
    n2 = Nursery.load(str(np))
    check("B.fresh_loads_g1", set(n2.proposals) == {pr.id})
    print("  B serialization failure: GREEN")


# ---------------------------------------------------------------- CONTROL C
def control_c_temp_write_failure() -> None:
    o = "DCCXVII_C"
    p = fresh_owner(o)
    pr = p.nursery.add("gamma base", words="gamma delta")
    p.nursery.save()
    np = npath(o)
    g1 = read_bytes(np)
    try:
        p.nursery.save(_fail_at="temp_write")
        raised = False
    except AtomicWriteError:
        raised = True
    check("C.raises", raised)
    check("C.canonical_is_g1_bytes", read_bytes(np) == g1)
    partials = [t for t in tmps_in_state() if np.name in t]
    check("C.partial_temp_left", len(partials) == 1)
    # the partial temp must not masquerade as canonical state
    n2 = Nursery.load(str(np))
    check("C.fresh_loads_g1", set(n2.proposals) == {pr.id})
    clean_tmps()
    print("  C temp-write failure: GREEN")


# ---------------------------------------------------------------- CONTROL G
def control_g_repeated_saves() -> None:
    o = "DCCXVII_G"
    p = fresh_owner(o)
    np = npath(o)
    gens = []
    for i in range(1, 5):
        pr = p.nursery.add(f"gen{i} idea", words=f"generation {i} alpha")
        p.confirm_proposal(pr.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": pr.id})
        p.nursery.save()
        gens.append(read_bytes(np))
        n2 = Nursery.load(str(np))
        check(f"G.gen{i}_visible", len(n2.proposals) == i)
    check("G.generations_distinct", len(set(gens)) == 4)
    check("G.no_stale_resurrection", read_bytes(np) == gens[-1])
    print("  G repeated saves: GREEN")


# ---------------------------------------------------------------- CONTROL H
def control_h_large_payload() -> None:
    o = "DCCXVII_H"
    p = fresh_owner(o)
    # materially larger nursery state (~1.5MB), built in memory, one save
    for i in range(3000):
        pid = f"bulk_{i:05d}"
        p.nursery.proposals[pid] = Proposal(
            id=pid,
            label=f"bulk payload idea {i}",
            words=("lorem ipsum dolor sit amet " * 12).strip(),
            kind="new",
        )
    p.nursery.save()
    np = npath(o)
    blob = read_bytes(np)
    check("H.materially_large", len(blob) > 1_000_000)
    try:
        p.nursery.save(_fail_at="replace")
        raised = False
    except AtomicWriteError:
        raised = True
    check("H.pre_replace_failure_raises", raised)
    check("H.canonical_intact", read_bytes(np) == blob)
    n2 = Nursery.load(str(np))
    check("H.fresh_loads_all", len(n2.proposals) == 3000)
    print(f"  H large payload ({len(blob)} bytes): GREEN")


# ---------------------------------------------------------------- CONTROL I
def control_i_unicode() -> None:
    o = "DCCXVII_I"
    p = fresh_owner(o)
    tricky = 'quotes "…", backslash \\, newline\nhere, unicode: héllo wörld 日本語 🌱, empty:, punct!?,.'
    pr = p.nursery.add("unicode probe", words=tricky)
    p.nursery.save()
    n2 = Nursery.load(str(npath(o)))
    check("I.roundtrip_exact", n2.proposals[pr.id].words == tricky)
    persist_rest.save(p)
    persist_rest.load(o, activate=False)
    check("I.program_file_valid", True)
    print("  I unicode/escaping: GREEN")


# ---------------------------------------------------------------- CONTROL J
def control_j_legacy_load() -> None:
    o = "DCCXVII_J"
    if o not in OWNERS:
        OWNERS.append(o)  # register so smoke()'s finally wipes it
    np = npath(o)
    wipe_owner(o)
    # hand-written Persistence V1 style JSON: no lifecycle fields at all
    legacy = {
        "legacy_one": {
            "id": "legacy_one", "label": "legacy idea one",
            "words": "legacy alpha", "kind": "new", "parents": [],
            "affinity": 0.0, "reason": "", "created": "2020-01-01T00:00:00Z",
            "status": "confirmed",
        },
        "legacy_two": {
            "id": "legacy_two", "label": "legacy idea two",
            "words": "legacy beta", "kind": "new", "parents": ["legacy_one"],
            "affinity": 0.5, "reason": "r", "created": "2020-01-02T00:00:00Z",
            "status": "pending",
        },
    }
    np.write_text(json.dumps(legacy, indent=2), encoding="utf-8")
    n = Nursery.load(str(np))
    check("J.legacy_loads", set(n.proposals) == {"legacy_one", "legacy_two"})
    check("J.legacy_defaults_active", n.proposals["legacy_one"].lifecycle_state == "active")
    # next successful save uses V2 mechanics; content preserved
    n.save()
    check("J.resave_no_tmps", tmps_in_state() == [])
    n2 = Nursery.load(str(np))
    check("J.resave_preserves", set(n2.proposals) == {"legacy_one", "legacy_two"})
    print("  J legacy load: GREEN")


# ---------------------------------------------------------------- CONTROL K
def control_k_corrupt_canonical() -> None:
    o = "DCCXVII_K"
    p = fresh_owner(o)
    p.nursery.add("kappa base", words="kappa lambda")
    p.nursery.save()
    np = npath(o)
    blob = read_bytes(np)
    np.write_bytes(blob[: len(blob) // 3])
    try:
        Nursery.load(str(np))
        raised = False
    except NurseryLoadError:
        raised = True
    check("K.truncated_raises", raised)
    np.write_bytes(b"\x00\xff not json \x00")
    try:
        Nursery.load(str(np))
        raised2 = False
    except NurseryLoadError:
        raised2 = True
    check("K.garbage_raises", raised2)
    # program file: honest failure too (never empty state)
    persist_rest.save(p)
    pp = Path(persist_rest._path(p.owner))
    pp.write_bytes(read_bytes(pp)[:40])
    try:
        persist_rest.load(o, activate=False)
        raised3 = False
    except Exception:
        raised3 = True
    check("K.program_corrupt_raises", raised3)
    print("  K corrupt canonical: GREEN")


# ---------------------------------------------------------------- CONTROL L
def control_l_io_failures() -> None:
    o = "DCCXVII_L"
    p = fresh_owner(o)
    pr = p.nursery.add("lambda base", words="lambda mu")
    p.nursery.save()
    np = npath(o)
    g1 = read_bytes(np)
    orig_open, orig_replace = os.open, os.replace
    # cannot create temp
    os.open = lambda *a, **k: (_ for _ in ()).throw(PermissionError("denied"))  # type: ignore
    try:
        p.nursery.save()
        r1 = False
    except AtomicWriteError:
        r1 = True
    finally:
        os.open = orig_open
    check("L.no_temp_raises", r1)
    check("L.canonical_intact_after_no_temp", read_bytes(np) == g1)
    # cannot replace target
    os.replace = lambda *a, **k: (_ for _ in ()).throw(OSError("replace denied"))  # type: ignore
    try:
        p.nursery.save()
        r2 = False
    except AtomicWriteError:
        r2 = True
    finally:
        os.replace = orig_replace
    check("L.no_replace_raises", r2)
    check("L.canonical_intact_after_no_replace", read_bytes(np) == g1)
    check("L.no_tmps_left", tmps_in_state() == [])
    print("  L IO failures: GREEN")


# ---------------------------------------------------------------- CONTROL P/Q
def control_pq_owner_isolation() -> None:
    a, b = "DCCXVII_PA", "DCCXVII_PB"
    pa, pb = fresh_owner(a), fresh_owner(b)
    pra = pa.nursery.add("owner a secret", words="alpha secret")
    prb = pb.nursery.add("owner b secret", words="beta secret")
    pa.nursery.save()
    pb.nursery.save()
    npa, npb = npath(a), npath(b)
    gb = read_bytes(npb)
    try:
        pa.nursery.save(_fail_at="replace")
    except AtomicWriteError:
        pass
    check("P.a_canonical_intact", set(Nursery.load(str(npa)).proposals) == {pra.id})
    check("P.b_canonical_untouched", read_bytes(npb) == gb)
    check("P.b_loads", set(Nursery.load(str(npb)).proposals) == {prb.id})
    # temp isolation: A's temp cannot cross-load into B (or into A)
    fake_tmp = STATE / (npa.name + ".dmtmp.99999998.deadbeef")
    fake_tmp.write_bytes(b'{"evil": "not-a-proposal-dict"}')
    try:
        nb = Nursery.load(str(npb))
        check("Q.b_ignores_a_temp", set(nb.proposals) == {prb.id})
        na = Nursery.load(str(npa))
        check("Q.a_ignores_own_temp", set(na.proposals) == {pra.id})
    finally:
        try:
            fake_tmp.unlink()
        except OSError:
            pass
    print("  P/Q owner + temp isolation: GREEN")


# ---------------------------------------------------------------- CONTROL R
def control_r_determinism() -> None:
    o = "DCCXVII_R"
    p = fresh_owner(o)
    for i in range(5):
        pr = p.nursery.add(f"det idea {i}", words=f"deterministic {i}")
        p.confirm_proposal(pr.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": pr.id})
    p.nursery.save()
    np = npath(o)
    b1 = read_bytes(np)
    n2 = Nursery.load(str(np))
    n2.save()
    b2 = read_bytes(np)
    check("R.save_load_save_identical", b1 == b2)
    print("  R determinism: GREEN")


# ---------------------------------------------------------------- CONTROL S
def control_s_byte_preservation() -> None:
    o = "DCCXVII_S"
    p = fresh_owner(o)
    pr = p.nursery.add("sigma base", words="sigma tau")
    p.confirm_proposal(pr.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": pr.id})
    p.nursery.save()
    persist_rest.save(p)
    np, pp = npath(o), Path(persist_rest._path(p.owner))
    gn, gp = read_bytes(np), read_bytes(pp)
    for hook in ("serialize", "temp_write", "replace"):
        try:
            p.nursery.save(_fail_at=hook)
        except AtomicWriteError:
            pass
        try:
            persist_rest.save(p, _fail_at=hook)
        except AtomicWriteError:
            pass
    check("S.nursery_bytes_preserved", read_bytes(np) == gn)
    check("S.program_bytes_preserved", read_bytes(pp) == gp)
    check("S.canonical_still_valid", set(Nursery.load(str(np)).proposals) == {pr.id})
    clean_tmps()
    print("  S byte preservation: GREEN")


# ---------------------------------------------------------------- CONTROL T
def control_t_load_failure_atomicity() -> None:
    o = "DCCXVII_T"
    p = fresh_owner(o)
    p.nursery.add("tau one", words="tau one")
    p.nursery.add("tau two", words="tau two")
    p.nursery.save()
    np = npath(o)
    raw = json.loads(read_bytes(np).decode("utf-8"))
    raw["tau_two_corrupt"] = "not-a-proposal-record"
    np.write_text(json.dumps(raw), encoding="utf-8")
    # one bad record -> the WHOLE load fails loudly; no partial nursery escapes
    try:
        n_bad = Nursery.load(str(np))
        raised = False
    except NurseryLoadError:
        raised, n_bad = True, None
    check("T.partial_record_raises", raised)
    check("T.no_partial_nursery", n_bad is None)
    # program file: failed load leaves the live program untouched
    before_units = set(p.cube.session.plane.units)
    persist_rest.save(p)
    pp = Path(persist_rest._path(p.owner))
    pp.write_bytes(b"{invalid json")
    try:
        persist_rest.load(o, activate=False)
        raised2 = False
    except Exception:
        raised2 = True
    check("T.program_load_raises", raised2)
    check("T.live_program_untouched", set(p.cube.session.plane.units) == before_units)
    print("  T load failure atomicity: GREEN")


# ---------------------------------------------------------------- CONTROL V
def control_v_cleanup() -> None:
    o = "DCCXVII_V"
    p = fresh_owner(o)
    p.nursery.add("upsilon base", words="upsilon")
    p.nursery.save()
    check("V.no_tmps_after_success", tmps_in_state() == [])
    try:
        p.nursery.save(_fail_at="serialize")
    except AtomicWriteError:
        pass
    check("V.no_tmps_after_fail", tmps_in_state() == [])
    # stale temp with a dead pid is swept; live pid is kept
    dead = STATE / ("sweep_probe.json.dmtmp.99999997.deadbeef")
    dead.write_bytes(b"partial")
    live = STATE / (f"sweep_probe.json.dmtmp.{os.getpid()}.livebeef")
    live.write_bytes(b"partial")
    try:
        res = sweep_stale_tmps(str(STATE))
        check("V.sweep_removes_dead", not dead.exists() and res["removed"] >= 1)
        check("V.sweep_keeps_live", live.exists())
    finally:
        for f in (dead, live):
            try:
                f.unlink()
            except OSError:
                pass
    print("  V cleanup: GREEN")


# ---------------------------------------------------------------- CONTROL M
def _fail_nth_save(nth: int, hook: str):
    """Monkeypatch AW.atomic_write_json so only the nth call trips the hook."""
    orig = AW.atomic_write_json
    state = {"n": 0}

    def wrapper(path, payload, *, _fail_at=None):
        state["n"] += 1
        if state["n"] == nth:
            return orig(path, payload, _fail_at=hook)
        return orig(path, payload)

    AW.atomic_write_json = wrapper
    return lambda: setattr(AW, "atomic_write_json", orig)


def control_m_supersession_integration() -> None:
    from form.mandell import supersession as S

    o = "DCCXVII_M"
    # M1: persistence interruption at the commit -> OLD COMPLETE, byte-identical
    p = fresh_owner(o)
    old = p.nursery.add("mu base", words="mu revision alpha")
    p.confirm_proposal(old.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": old.id})
    p.nursery.save()
    pre = read_bytes(npath(o))
    restore = _fail_nth_save(3, "replace")  # commit is the 3rd save (add=1st, confirm=2nd)
    try:
        S.supersede_proposal(p, old.id, "mu revision two alpha")
        outcome = "no_raise"
    except AtomicWriteError:
        outcome = "AtomicWriteError"
    except S.SupersedeError:
        outcome = "SupersedeError"
    finally:
        restore()
    check("M1.honest_failure", outcome in ("AtomicWriteError", "SupersedeError"))
    check("M1.bytes_identical", read_bytes(npath(o)) == pre)
    rec = S.inspect_revision(p, old.id)
    check("M1.old_complete", rec["lifecycle_state"] == "active"
          and rec["superseded_by_id"] is None
          and len(Nursery.load(str(npath(o))).proposals) == 1)
    print("  M1 supersession persistence-interrupt: GREEN")

    # M2: crash AFTER replace during the commit -> NEW COMPLETE (fresh process)
    o2 = o + "2"
    tmp = tempfile.mkdtemp(prefix="dccxvii_m2_")
    res = os.path.join(tmp, "res.json")
    script_a = (
        "import json, os, sys\n"
        f"sys.path.insert(0, {str(REPO)!r})\n"
        "from form.open import open_program\n"
        "from form import persist_rest\n"
        "from form.dell_matrix import atomic_write as AW\n"
        "from form.mandell import supersession as S\n"
        f"OWNER = {o2!r}; RES = {res!r}\n"
        "p = open_program(OWNER)\n"
        "old = p.nursery.add('mu2 base', words='mu2 revision alpha')\n"
        "p.confirm_proposal(old.id, _producer=\\\"test\\\", _review_context={\\\"reviewer\\\": \\\"test\\\", \\\"approved_pid\\\": old.id})\\n"
        "p.nursery.save(); persist_rest.save(p)\n"
        "with open(RES, 'w') as f:\n"
        "    json.dump({'pid_a': os.getpid(), 'old_id': old.id}, f)\n"
        "orig = AW.atomic_write_json; state = {'n': 0}\n"
        "def wrapper(path, payload, *, _fail_at=None):\n"
        "    state['n'] += 1\n"
        "    # R3: 5 writes total (create nursery, journal, Phase3 nursery,\n"
        "    # Phase3 program, Phase4 nursery). Crash on 5th (Phase 4 post-replace).\n"
        "    return orig(path, payload, _fail_at='crash_after_replace' if state['n'] == 5 else _fail_at)\n"
        "AW.atomic_write_json = wrapper\n"
        "S.supersede_proposal(p, old.id, 'mu2 revision two alpha')\n"
    )
    script_b = (
        "import json, os, sys\n"
        f"sys.path.insert(0, {str(REPO)!r})\n"
        "from form import persist_rest\n"
        "from form.mandell.supersession import inspect_revision\n"
        f"OWNER = {o2!r}; RES = {res!r}; OUT = {res!r} + \".out\"\n"
        "meta = json.load(open(RES))\n"
        "p = persist_rest.load(OWNER, activate=False)\n"
        "old = inspect_revision(p, meta['old_id'])\n"
        "new_id = old['superseded_by_id']\n"
        "new = inspect_revision(p, new_id)\n"
        "nprop = p.nursery.proposals.get(new_id)\n"
        "checks = {\n"
        "  'pid_distinct': meta['pid_a'] != os.getpid(),\n"
        "  'old_superseded': old['lifecycle_state'] == 'superseded',\n"
        "  'new_active': new['lifecycle_state'] == 'active' and new['supersedes_id'] == meta['old_id'],\n"
        "  'chain': new['chain'] == [meta['old_id'], new_id],\n"
        "  'links_bidirectional': old['superseded_by_id'] == new_id,\n"
        "  'new_confirmed': nprop is not None and nprop.status == 'confirmed',\n"
        "  'no_half_chain': not (old['lifecycle_state'] == 'superseded' and (nprop is None or nprop.status != 'confirmed')),\n"
        "}\n"
        "open(OUT, 'w').write(json.dumps(checks))\n"
    )
    pa, pb = os.path.join(tmp, "a.py"), os.path.join(tmp, "b.py")
    open(pa, "w").write(script_a)
    open(pb, "w").write(script_b)
    wipe_owner(o2)
    OWNERS.append(o2)
    ra = subprocess.run([sys.executable, pa], capture_output=True, text=True, timeout=180)
    assert ra.returncode == 42, f"M2 A did not crash as planned: {ra.returncode} {ra.stderr[-300:]}"
    rb = subprocess.run([sys.executable, pb], capture_output=True, text=True, timeout=180)
    assert rb.returncode == 0, rb.stderr[-500:]
    m2 = json.load(open(res + ".out"))
    for k, v in m2.items():
        check(f"M2.{k}", v)
    print("  M2 supersession post-replace crash: GREEN")


# ================================================================ CONTROL U
_SCRIPT_A = """
import json, os, sys
sys.path.insert(0, __REPO__)
from form.open import open_program
from form import persist_rest
from form.dell_matrix import atomic_write as AW
from form.dell_matrix.nursery import owner_nursery_path

REPO = __REPO__; OWNER = __OWNER__; SCEN = __SCEN__; RES = __RES__
CANARY = "CANARY_" + os.urandom(8).hex()
out = {"pid_a": os.getpid(), "scenario": SCEN}
with open(RES, "w") as f:
    json.dump(out, f)

def npath():
    return owner_nursery_path(OWNER)

def snap(extra):
    with open(RES, "w") as f:
        json.dump(dict(out, **extra), f)

if SCEN in ("normal", "serialize_fail", "temp_write_fail", "crash_before_replace",
            "crash_after_replace", "corrupt_canonical", "repeated", "program_crash_before_replace"):
    p = open_program(OWNER)
    pr = p.nursery.add("cross base", words="cross alpha")
    p.confirm_proposal(pr.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": pr.id})
    p.nursery.save()
    g1 = open(npath(), "rb").read()
    if SCEN == "repeated":
        for i in range(2, 5):
            q = p.nursery.add(f"cross gen{i}", words=f"cross alpha {i}")
            p.confirm_proposal(q.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": q.id})
            p.nursery.save()
        snap({"note": "repeated"})
        raise SystemExit(0)
    if SCEN == "normal":
        q = p.nursery.add("cross two", words="cross beta")
        p.confirm_proposal(q.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": q.id})
        p.nursery.save()
        snap({})
        raise SystemExit(0)
    if SCEN == "program_crash_before_replace":
        persist_rest.save(p)
        AW._FAIL_AT = "crash_before_replace"
        persist_rest.save(p)
        raise SystemExit("should have exited")
    if SCEN == "corrupt_canonical":
        open(npath(), "wb").write(g1[: len(g1) // 4])
        snap({})
        raise SystemExit(0)
    if SCEN in ("crash_before_replace", "crash_after_replace"):
        # stage G2 purely in memory (no save), then die at the replace boundary
        from form.dell_matrix.nursery import Proposal
        p.nursery.proposals["cross_two"] = Proposal(
            id="cross_two", label="cross two", words="cross beta", kind="new", status="confirmed")
        p.nursery.save(_fail_at=SCEN)  # hook name == scenario name; os._exit(42), never returns
        raise SystemExit("should have exited")
    hook = {"serialize_fail": "serialize", "temp_write_fail": "temp_write"}[SCEN]
    try:
        p.nursery.save(_fail_at=hook)
        snap({"outcome": "no_raise"})
    except Exception as e:
        snap({"outcome": type(e).__name__})
    raise SystemExit(0)

if SCEN == "sigkill_mid_write":
    from form.dell_matrix.nursery import Proposal
    p = open_program(OWNER)
    pr = p.nursery.add("sigkill base", words="sigkill alpha")
    p.confirm_proposal(pr.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": pr.id})
    p.nursery.save()
    g1 = open(npath(), "rb").read()
    for i in range(4000):
        pid = f"sig_{i:05d}"
        p.nursery.proposals[pid] = Proposal(id=pid, label=f"sig payload {i}",
                                            words=("payload data " * 40).strip(), kind="new")
    payload = {k: v.to_dict() for k, v in p.nursery.proposals.items()}
    expected = len(json.dumps(payload, indent=2).encode("utf-8"))
    with open(RES + ".size", "w") as f:
        f.write(str(expected))
    with open(RES + ".g1", "wb") as f:
        f.write(g1)
    AW._FAIL_AT = "slow_write"
    p.nursery.save()
    snap({"outcome": "survived"})
    raise SystemExit(0)
raise SystemExit("unknown scenario")
"""

_SCRIPT_B = """
import json, os, sys, glob
sys.path.insert(0, __REPO__)
from form.dell_matrix.nursery import Nursery, NurseryLoadError, owner_nursery_path
from form import persist_rest

REPO = __REPO__; OWNER = __OWNER__; SCEN = __SCEN__; RES = __RES__; OUT = __OUT__
res = json.load(open(RES))
checks = []
def check(name, cond):
    checks.append((name, bool(cond)))

npath = owner_nursery_path(OWNER)
blob = open(npath, "rb").read() if os.path.exists(npath) else b""
check("pid_distinct", res.get("pid_a") not in (None, os.getpid()))
check("no_canary", b"CANARY_" not in blob)

if SCEN == "normal":
    n = Nursery.load(npath)
    check("loads_g2", len(n.proposals) == 2 and all(v.status == "confirmed" for v in n.proposals.values()))
elif SCEN == "serialize_fail":
    check("raised", res.get("outcome") == "AtomicWriteError")
    n = Nursery.load(npath)
    check("loads_g1", len(n.proposals) == 1)
elif SCEN == "temp_write_fail":
    check("raised", res.get("outcome") == "AtomicWriteError")
    n = Nursery.load(npath)
    check("loads_g1", len(n.proposals) == 1)
    tmps = glob.glob(npath + ".dmtmp.*")
    check("temp_present_but_ignored", len(tmps) == 1)
elif SCEN == "crash_before_replace":
    n = Nursery.load(npath)
    check("loads_g1", len(n.proposals) == 1)
elif SCEN == "crash_after_replace":
    n = Nursery.load(npath)
    check("loads_g2", len(n.proposals) == 2)
elif SCEN == "corrupt_canonical":
    try:
        Nursery.load(npath)
        check("honest_failure", False)
    except NurseryLoadError:
        check("honest_failure", True)
elif SCEN == "repeated":
    n = Nursery.load(npath)
    check("loads_g4", len(n.proposals) == 4)
elif SCEN == "program_crash_before_replace":
    p = persist_rest.load(OWNER, activate=False)
    check("program_g1_complete", len(p.cube.session.plane.units) >= 1)
    n = Nursery.load(npath)
    check("nursery_intact", len(n.proposals) >= 1)
elif SCEN == "sigkill_mid_write":
    g1 = open(RES + ".g1", "rb").read()
    expected = int(open(RES + ".size").read())
    check("canonical_is_g1_bytes", blob == g1)
    n = Nursery.load(npath)
    check("loads_g1", len(n.proposals) == 1)
    tmps = glob.glob(npath + ".dmtmp.*")
    check("partial_temp_exists", len(tmps) == 1)
    if tmps:
        check("temp_is_partial", os.path.getsize(tmps[0]) < expected)

with open(OUT, "w") as f:
    json.dump({"pid_b": os.getpid(), "checks": checks}, f)
"""

U_SCENARIOS = [
    "normal",
    "serialize_fail",
    "temp_write_fail",
    "crash_before_replace",
    "crash_after_replace",
    "sigkill_mid_write",
    "corrupt_canonical",
    "repeated",
    "program_crash_before_replace",
]


def _run_u_scenario(scen: str) -> bool:
    owner = f"DCCXVII_U_{scen}"
    wipe_owner(owner)
    OWNERS.append(owner)
    tmp = tempfile.mkdtemp(prefix="dccxvii_u_")
    res = os.path.join(tmp, "res.json")
    out = os.path.join(tmp, "out.json")

    def fill(script: str) -> str:
        return (script.replace("__REPO__", repr(str(REPO))).replace("__OWNER__", repr(owner))
                .replace("__SCEN__", repr(scen)).replace("__RES__", repr(res)).replace("__OUT__", repr(out)))

    pa = os.path.join(tmp, "a.py")
    pb = os.path.join(tmp, "b.py")
    open(pa, "w").write(fill(_SCRIPT_A))
    open(pb, "w").write(fill(_SCRIPT_B))
    if scen == "sigkill_mid_write":
        proc = subprocess.Popen([sys.executable, pa], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        npath_s = owner_nursery_path(owner)
        deadline = time.time() + 60
        import glob as _g
        while time.time() < deadline:
            if _g.glob(npath_s + ".dmtmp.*"):
                break
            if proc.poll() is not None:
                break
            time.sleep(0.05)
        time.sleep(0.5)
        if proc.poll() is None:
            proc.kill()  # SIGKILL mid temp-write
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=15)
    else:
        ra = subprocess.run([sys.executable, pa], capture_output=True, text=True, timeout=180)
        if scen.startswith("crash_") and ra.returncode != 42:
            print(f"    U.{scen}: process A did not crash as planned (rc={ra.returncode})")
            print("    stderr:", ra.stderr[-400:])
            return False
        if scen == "program_crash_before_replace" and ra.returncode != 42:
            print(f"    U.{scen}: process A did not crash as planned (rc={ra.returncode})")
            return False
    rb = subprocess.run([sys.executable, pb], capture_output=True, text=True, timeout=180)
    if rb.returncode != 0:
        print(f"    U.{scen}: process B failed rc={rb.returncode}")
        print("    stderr:", rb.stderr[-600:])
        return False
    result = json.load(open(out))
    meta = json.load(open(res))
    failed = [n for n, ok in result["checks"] if not ok]
    ok = not failed and result["pid_b"] != meta.get("pid_a")
    if not ok:
        print(f"    U.{scen}: FAILED {failed}")
    return ok


def control_u_cross_process_matrix() -> None:
    all_ok = True
    for scen in U_SCENARIOS:
        ok = _run_u_scenario(scen)
        check(f"U.{scen}", ok)
        all_ok = all_ok and ok
        print(f"    U.{scen}: {'GREEN' if ok else 'RED'}")
    print(f"  U cross-process matrix: {'GREEN' if all_ok else 'RED'}")


# ---------------------------------------------------------------- CONTROL N
def control_n_lineage_dependency() -> None:
    from form.mandell import supersession as S

    o = "DCCXVII_N"
    tmp = tempfile.mkdtemp(prefix="dccxvii_n_")
    res = os.path.join(tmp, "res.json")
    script_a = (
        "import json, os, sys\n"
        f"sys.path.insert(0, {str(REPO)!r})\n"
        "from form.open import open_program\n"
        "from form import persist_rest\n"
        "from form.dell_matrix import atomic_write as AW\n"
        "from form.mandell import supersession as S\n"
        f"OWNER = {o!r}; RES = {res!r}\n"
        "p = open_program(OWNER)\n"
        "a = p.nursery.add('n root', words='n root alpha')\n"
        "p.confirm_proposal(a.id, _producer=\\\"test\\\", _review_context={\\\"reviewer\\\": \\\"test\\\", \\\"approved_pid\\\": a.id})\\n"
        "b = p.nursery.add('n child', words='n child alpha', parents=[a.id])\n"
        "p.confirm_proposal(b.id, _producer=\\\"test\\\", _review_context={\\\"reviewer\\\": \\\"test\\\", \\\"approved_pid\\\": b.id})\\n"
        "c = p.nursery.add('n grandchild', words='n grandchild alpha', parents=[b.id])\n"
        "p.confirm_proposal(c.id, _producer=\\\"test\\\", _review_context={\\\"reviewer\\\": \\\"test\\\", \\\"approved_pid\\\": c.id})\\n"
        "r = S.supersede_proposal(p, a.id, 'n root revised alpha')\n"
        "assert r['ok']\n"
        "p.nursery.save(); persist_rest.save(p)\n"
        "ids = {'a': a.id, 'b': b.id, 'c': c.id, 'a2': r['new_id']}\n"
        "with open(RES, 'w') as f:\n"
        "    json.dump({'pid_a': os.getpid(), 'ids': ids}, f)\n"
        "d = p.nursery.add('n newcomer', words='n newcomer alpha', parents=[c.id])\n"
        "# in-memory-only change: never saved before the crash\n"
        "p.nursery.proposals[d.id].status = 'confirmed'\n"
        "AW._FAIL_AT = 'crash_before_replace'\n"
        "p.nursery.save()\n"
    )
    pa = os.path.join(tmp, "a.py")
    open(pa, "w").write(script_a)
    wipe_owner(o)
    OWNERS.append(o)
    ra = subprocess.run([sys.executable, pa], capture_output=True, text=True, timeout=180)
    assert ra.returncode == 42, f"A did not crash as planned: {ra.returncode} {ra.stderr[-300:]}"
    meta = json.load(open(res))
    assert meta["pid_a"] != os.getpid()
    # fresh process B (this process never saw A's memory)
    p = persist_rest.load(o, activate=False)
    ids = meta["ids"]
    from form.dell_matrix.lineage import inspect_lineage
    from form.mandell.dependency_validity import inspect_dependency
    plane = p.cube.session.plane
    lb = inspect_lineage(plane, ids["b"])
    lc = inspect_lineage(plane, ids["c"])
    check("N.lineage_parents", ids["a"] in lb["parents"] and ids["b"] in lc["parents"])
    check("N.no_cycle", not lb["cycle"] and not lc["cycle"])
    ra2, ra2n = S.inspect_revision(p, ids["a"]), S.inspect_revision(p, ids["a2"])
    check("N.revision_consistent",
          ra2["lifecycle_state"] == "superseded" and ra2["superseded_by_id"] == ids["a2"]
          and ra2n["lifecycle_state"] == "active" and ra2n["supersedes_id"] == ids["a"])
    db = inspect_dependency(p, ids["b"])
    # b's ancestor a was superseded: b is honestly dependency-invalid
    # (superseded ancestors are unqualified by design, DCC-XVI) -- the
    # generation is internally consistent about it.
    check("N.dependency_honest",
          db["dependency_status"] == "invalid"
          and db["dependency_reason"].startswith("superseded_dependency:"))
    n = Nursery.load(str(npath(o)))
    check("N.nursery_complete", all(
        (v.superseded_by_id is None) or (v.superseded_by_id in n.proposals) for v in n.proposals.values()))
    # the in-memory-only change died with the crashed process: d is still pending
    drec = next(v for k, v in n.proposals.items() if v.label == "n newcomer")
    check("N.unsaved_change_discarded", drec.status == "pending")
    print("  N lineage/dependency integration: GREEN")


# ---------------------------------------------------------------- CONTROL O
def control_o_contextual_routing() -> None:
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent

    o = "DCCXVII_O"
    tmp = tempfile.mkdtemp(prefix="dccxvii_o_")
    exp_path = os.path.join(tmp, "expected.json")

    def build(p):
        from form.mandell import supersession as S
        rv_old = p.nursery.add("river delta sediment flow", words="river delta sediment flow")
        p.confirm_proposal(rv_old.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": rv_old.id})
        r = S.supersede_proposal(p, rv_old.id, "river delta sediment flow revised")
        rv_new = r["new_id"]
        dep_ok = p.nursery.add("river tributary mapping", words="river tributary mapping",
                               parents=[rv_new])
        p.confirm_proposal(dep_ok.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": dep_ok.id})
        dep_bad = p.nursery.add("river ancient course", words="river ancient course",
                                parents=["ghost_parent_xyz"])
        p.confirm_proposal(dep_bad.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": dep_bad.id})
        cf1 = p.nursery.add("river flow increases erosion", words="river flow increases erosion")
        cf2 = p.nursery.add("river flow does not increase erosion",
                            words="river flow does not increase erosion")
        p.confirm_proposal(cf1.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": cf1.id})
        p.confirm_proposal(cf2.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": cf2.id})
        plain = p.nursery.add("river basin rainfall", words="river basin rainfall")
        p.confirm_proposal(plain.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": plain.id})
        return {"rv_old": rv_old.id, "rv_new": rv_new, "dep_ok": dep_ok.id,
                "dep_bad": dep_bad.id, "cf1": cf1.id, "cf2": cf2.id, "plain": plain.id}

    def ctx_snapshot(p):
        r = route_intent(p, translate("grow using knowledge about river flow"),
                         raw_line="grow using knowledge about river flow")
        assert r.ok
        n = p.last_nurture
        return {
            "selected_ids": sorted(n.get("selected_ids", [])),
            "consumer_scope_ids": sorted(n.get("consumer_scope_ids", [])),
            "quarantined_ids": sorted(n.get("quarantined_ids", [])),
            "dependency_exclusions": sorted(
                e["id"] for e in n.get("dependency_exclusions", []) if isinstance(e, dict)),
            "supersession_exclusions": sorted(
                e["id"] for e in n.get("supersession_exclusions", []) if isinstance(e, dict)),
        }

    p = fresh_owner(o)
    ids = build(p)
    p.nursery.save()
    persist_rest.save(p)
    expected = ctx_snapshot(p)
    with open(exp_path, "w") as f:
        json.dump({"expected": expected, "ids": ids}, f)

    script_b = (
        "import json, sys\n"
        f"sys.path.insert(0, {str(REPO)!r})\n"
        "from form import persist_rest\n"
        "from form.mandell.translate import translate\n"
        "from form.mandell.semantic_router import route_intent\n"
        f"OWNER = {o!r}; EXP = {exp_path!r}; OUT = {exp_path!r} + \".out\"\n"
        "p = persist_rest.load(OWNER, activate=False)\n"
        "r = route_intent(p, translate('grow using knowledge about river flow'),\n"
        "                 raw_line='grow using knowledge about river flow')\n"
        "n = p.last_nurture\n"
        "got = {'selected_ids': sorted(n.get('selected_ids', [])),\n"
        "       'consumer_scope_ids': sorted(n.get('consumer_scope_ids', [])),\n"
        "       'quarantined_ids': sorted(n.get('quarantined_ids', [])),\n"
        "       'dependency_exclusions': sorted(e['id'] for e in n.get('dependency_exclusions', []) if isinstance(e, dict)),\n"
        "       'supersession_exclusions': sorted(e['id'] for e in n.get('supersession_exclusions', []) if isinstance(e, dict))}\n"
        "open(OUT, 'w').write(json.dumps({'got': got, 'pid_b': __import__('os').getpid()}))\n"
    )
    pb = os.path.join(tmp, "b.py")
    open(pb, "w").write(script_b)
    rb = subprocess.run([sys.executable, pb], capture_output=True, text=True, timeout=180)
    assert rb.returncode == 0, rb.stderr[-500:]
    got = json.load(open(exp_path + ".out"))["got"]
    check("O.routing_reproduced", got == expected)
    check("O.superseded_excluded", ids["rv_old"] in expected["supersession_exclusions"]
          or ids["rv_old"] not in expected["consumer_scope_ids"])
    check("O.conflict_quarantined", {ids["cf1"], ids["cf2"]} <= set(expected["quarantined_ids"]))
    check("O.plain_routable", ids["plain"] in expected["consumer_scope_ids"])
    print("  O contextual routing: GREEN")


# ---------------------------------------------------------------- runner
def smoke() -> bool:
    global CHECKS
    CHECKS = []
    for owner in list(OWNERS):
        wipe_owner(owner)
    OWNERS.clear()
    clean_tmps()  # never inherit temp debris from an interrupted earlier run
    try:
        assert PERSISTENCE_PROTOCOL_VERSION == 2
        control_a_normal_save()
        control_b_serialize_failure()
        control_c_temp_write_failure()
        control_g_repeated_saves()
        control_h_large_payload()
        control_i_unicode()
        control_j_legacy_load()
        control_k_corrupt_canonical()
        control_l_io_failures()
        control_pq_owner_isolation()
        control_r_determinism()
        control_s_byte_preservation()
        control_t_load_failure_atomicity()
        control_v_cleanup()
        control_m_supersession_integration()
        control_n_lineage_dependency()
        control_o_contextual_routing()
        control_u_cross_process_matrix()
    finally:
        for owner in list(OWNERS):
            wipe_owner(owner)
        OWNERS.clear()
        clean_tmps()
    failed = [n for n, ok in CHECKS if not ok]
    total = len(CHECKS)
    passed = total - len(failed)
    print(f"DCC-XVII: {passed}/{total}")
    if failed:
        print("FAILED:", failed)
    return not failed and total > 0


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
