#!/usr/bin/env python3
"""72-36 — nested Core II version validation (bounded repair,
Director-authorized 2026-11-06, after 72-31).

Defect (reproduced by the Director on main, and by the scoping
probe hidden_files/72-36_probe.py at the merged base): the public
loader `persist_rest.load(owner, path=..., activate=False)`
accepted a nested `core_ii` member carrying ANY explicit version
— 999, true, "1", null, -1 — and bound its store, because
`restore_core_ii` never validated the member's version. The outer
Program envelope has enforced a strict version contract since
RTPH-I (`_validate_envelope_version`); the nested member had
none.

Contract pinned here (evidence: git archaeology,
hidden_files/72-36_q1_history_addendum.md — the member's writer
has stamped version 1 since its first commit 3e541a9 and no
other value was ever emitted; the proven legacy shape is the
ABSENT member, pinned by core_ii_persist_test's
old_v7_default_state):

  REFUSED (ProgramLoadError, prior binding + files preserved):
  - explicit version other than exact int 1: 999, true (bool
    trap: True == 1), "1", null, -1, 0, 2, 1.0
  - a present block with NO version field (never emitted by any
    writer; a present section without its version is malformed,
    per the agent_local precedent — distinct from the absent
    member, which is the legacy shape)
  - a present member that is not an object ("not-a-dict", null):
    wrong shape is malformed, NOT proven absence (this replaces
    the silent default-state fallback pinned by
    core_ii_persist_test's malformed_loads/malformed_fallback,
    a defect pin corrected in this same circuit)
  - present:False carrying an unsupported version: validation
    runs BEFORE the present shortcut — a future schema claiming
    "absent" is still an unknown schema
  - the same refusals on the bare-block restore path
    (data itself is the block)

  ACCEPTED (controls):
  - version 1 roundtrip through the public loader
  - absent member (legacy) -> default state
  - present:False with version 1 (the emitted absent shape)
  - unknown extra FIELDS inside a supported v1 block (unknown
    fields are not an unknown schema version)
  - malformed FIELD values inside a v1 block keep the existing
    field-level leniency (store as a list -> field defaulted)

Labels: INTEGRATION / public entry path (persist_rest.load).
State hygiene: uuid-unique owners; exact-path cleanup; cleanup
failures are reported in the final check, never swallowed.
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []
_TMP_FILES = []

from form.open import open_program  # noqa: E402
from form.persist import save  # noqa: E402
from form.persist_rest import ProgramLoadError, load  # noqa: E402
from form.persist_core_ii import restore_core_ii, serialize_core_ii  # noqa: E402
from form.mandell.core_ii_exec import attach  # noqa: E402

RUN = uuid.uuid4().hex[:8]
OWNER = f"T7236V{RUN}"
MARKER = {"director_probe": "future"}


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _track(path):
    _TMP_FILES.append(path)
    return path


def _write_tmp(data):
    fd, tmp = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return _track(tmp)


def _valid_envelope():
    p = open_program(OWNER)
    st = attach(p)
    st.store["origin"] = "valid"
    st.store["alpha"] = "1"
    path = save(p)
    _track(path)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _public_refusal(tag, envelope):
    tmp = _write_tmp(envelope)
    with open(tmp, "rb") as f:
        before = f.read()
    refused, err = False, None
    try:
        load(OWNER, path=tmp, activate=False)
    except ProgramLoadError as exc:
        refused, err = True, exc
    except Exception as exc:  # noqa: BLE001
        err = exc
    check(f"{tag}.public_refusal", refused,
          f"{type(err).__name__}: {err}" if err else "loaded")
    with open(tmp, "rb") as f:
        check(f"{tag}.file_bytes_unchanged", f.read() == before)


def _restore_refusal(tag, envelope):
    prog = open_program(f"T7236R{RUN}{tag}"[:40])
    st = attach(prog)
    st.store = {"prior": "binding"}
    refused = False
    try:
        restore_core_ii(prog, envelope)
    except ProgramLoadError:
        refused = True
    except Exception:  # noqa: BLE001
        refused = False
    check(f"{tag}.restore_refusal", refused)
    check(f"{tag}.prior_binding_preserved",
          prog.core_ii.store == {"prior": "binding"},
          str(prog.core_ii.store))


def _refusal_family(tag, member):
    env = copy.deepcopy(_BASE)
    env["core_ii"] = member
    _public_refusal(tag, env)
    _restore_refusal(tag, env)


_BASE = None


def main():
    global _BASE
    _BASE = _valid_envelope()

    # -- refusal family: the Director's verbatim values + family
    for tag, v in (("V999", 999), ("VBOOL", True), ("VSTR", "1"),
                   ("VNULL", None), ("VNEG", -1), ("VZERO", 0),
                   ("VTWO", 2), ("VFLOAT", 1.0)):
        _refusal_family(tag, {"version": v, "present": True,
                              "store": dict(MARKER)})
    # the refusal names the member (representative case)
    env = copy.deepcopy(_BASE)
    env["core_ii"] = {"version": 999, "present": True,
                      "store": dict(MARKER)}
    tmp = _write_tmp(env)
    msg = ""
    try:
        load(OWNER, path=tmp, activate=False)
    except ProgramLoadError as exc:
        msg = str(exc)
    check("V999.error_names_core_ii", "core_ii" in msg, msg)

    # -- refusal: present block without a version field
    _refusal_family("NOVERSION", {"present": True,
                                  "store": dict(MARKER)})
    # -- refusal: present member of the wrong shape
    _refusal_family("NONDICT", "not-a-dict")
    _refusal_family("NULLMEMBER", None)
    # -- refusal: present:False with an unsupported version
    _refusal_family("FALSE999", {"version": 999, "present": False})
    # -- refusal: bare-block restore path
    prog = open_program(f"T7236B{RUN}")
    st = attach(prog)
    st.store = {"prior": "binding"}
    refused = False
    try:
        restore_core_ii(prog, {"version": 999, "present": True,
                               "store": dict(MARKER)})
    except ProgramLoadError:
        refused = True
    except Exception:  # noqa: BLE001
        refused = False
    check("BARE999.restore_refusal", refused)
    check("BARE999.prior_binding_preserved",
          prog.core_ii.store == {"prior": "binding"},
          str(prog.core_ii.store))

    # -- controls
    p = load(OWNER, activate=False)
    check("V1.public_roundtrip",
          p.core_ii.store == {"origin": "valid", "alpha": "1"},
          str(p.core_ii.store))
    env = copy.deepcopy(_BASE)
    env.pop("core_ii", None)
    tmp = _write_tmp(env)
    p = load(OWNER, path=tmp, activate=False)
    check("ABSENT.loads_default_state", p.core_ii.store == {},
          str(p.core_ii.store))
    env = copy.deepcopy(_BASE)
    env["core_ii"] = {"version": 1, "present": False}
    tmp = _write_tmp(env)
    p = load(OWNER, path=tmp, activate=False)
    check("FALSE1.loads_default_state", p.core_ii.store == {},
          str(p.core_ii.store))
    env = copy.deepcopy(_BASE)
    env["core_ii"] = {"version": 1, "present": True,
                      "store": dict(MARKER), "future_field": {"x": 1}}
    tmp = _write_tmp(env)
    p = load(OWNER, path=tmp, activate=False)
    check("EXTRAFIELD.loads_and_binds",
          p.core_ii.store == MARKER, str(p.core_ii.store))
    env = copy.deepcopy(_BASE)
    env["core_ii"] = {"version": 1, "present": True,
                      "store": ["not", "a", "dict"]}
    tmp = _write_tmp(env)
    p = load(OWNER, path=tmp, activate=False)
    check("FIELDLEVEL.field_leniency_kept", p.core_ii.store == {},
          str(p.core_ii.store))
    prog = open_program(f"T7236C{RUN}")
    st = attach(prog)
    st.store = dict(MARKER)
    prog2 = open_program(f"T7236D{RUN}")
    restore_core_ii(prog2, serialize_core_ii(prog))
    check("BARE1.bare_block_binds",
          prog2.core_ii.store == MARKER, str(prog2.core_ii.store))
    # -- cross-process: the refusal holds from a fresh interpreter
    env = copy.deepcopy(_BASE)
    env["core_ii"] = {"version": 999, "present": True,
                      "store": dict(MARKER)}
    tmp = _write_tmp(env)
    fd, wpath = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    _track(wpath)
    with open(wpath, "w", encoding="utf-8") as f:
        f.write(
            "import sys\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from form.persist_rest import load\n"
            "try:\n"
            "    load(sys.argv[2], path=sys.argv[3],"
            " activate=False)\n"
            "    print('LOADED')\n"
            "except Exception as e:\n"
            "    print(type(e).__name__)\n"
        )
    import subprocess
    out = subprocess.run([sys.executable, wpath, REPO, OWNER, tmp],
                         capture_output=True, text=True, timeout=120)
    last = out.stdout.strip().splitlines()[-1] if out.stdout.strip() \
        else "no-output"
    check("CROSSPROCESS.refusal_in_fresh_process",
          last == "ProgramLoadError",
          f"rc={out.returncode} last={last} "
          f"stderr={out.stderr.strip()[-200:]}")
    p = load(OWNER, activate=False)
    check("RETRY.valid_still_binds_after_refusals",
          p.core_ii.store == {"origin": "valid", "alpha": "1"},
          str(p.core_ii.store))

    # -- cleanup: exact paths only; failures are evidence
    from form.persist_rest import _path as _program_path
    from form.dell_matrix.nursery import owner_nursery_path
    candidates = list(_TMP_FILES)
    for own in (OWNER,):
        candidates.append(_program_path(own))
        candidates.append(owner_nursery_path(own))
    for path in candidates:
        try:
            if os.path.isfile(path):
                os.remove(path)
        except Exception as exc:  # noqa: BLE001
            _CLEANUP_ERRORS.append(f"{path}:{type(exc).__name__}")
    check("cleanup.no_errors", not _CLEANUP_ERRORS,
          str(_CLEANUP_ERRORS))

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"core_ii_version_validation_test: "
          f"{passed}/{len(RESULTS)} PASS")
    return 0 if passed == len(RESULTS) else 1


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
