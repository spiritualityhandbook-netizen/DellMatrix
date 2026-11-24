#!/usr/bin/env python3
"""P0-S restore-refusal fixtures — the DECIDED contract for malformed
present values in the agent_audit / inspire / forces restore sections.

STATUS: FIXTURES ONLY. EXPECTED **RED** AGAINST CURRENT MAIN.
This suite expresses a contract that is DECIDED but NOT YET BUILT.
Its red legs are failing-first evidence for the Keeper's pre-build
review — they are NOT a regression in existing behavior, and nobody
should read them as one. The suite turns green only when the
separately authorized product build lands in form/persist_rest.py.

Authority — chat Director, wake-mode full pass 7136855959 on
issue #512 (2026-11-24):

    "Select staged, typed refusal for malformed present values that
    would otherwise clear a section. Preserve the existing supported
    legacy defaults, existing recoverable quarantine behavior and
    original bytes. Keeper's pre-build review should verify the
    boundary for all three sections, second-owner isolation and
    retention of already-preserved malformed records. Uni may
    prepare test fixtures now. Product work in the shared restore
    file awaits that review and the separate Director clearance."

Defect evidence — Uni record 7079514919 on issue #512 (executed proof
at main f60d19f5; full record P0S_AGENT_AUDIT_PROBES_2026-11-22.md):

  * agent_audit: a present non-finite sequence value (JSON tokens
    1e309 / -1e309 / Infinity, at the section counter or at one
    record) makes int() raise OverflowError, which escapes the two
    (TypeError, ValueError) cast guards in the restore block and hits
    its exception-agnostic outer reset: load SUCCEEDS SILENTLY with
    every valid record dropped, the counter reset to 0, and any
    previously preserved malformed originals erased. The next save
    makes the loss permanent.
  * inspire: one wrong-typed scalar (prefs.confirms = "bad") raises
    inside InspireState.from_dict; the restore-level except: pass
    silently substitutes a whole fresh section (valid weights and
    rejects lost).
  * forces: one wrong-typed scalar (water.intensity = "bad") raises
    inside ForceField.from_dict; same silent whole-section
    substitution (a valid evolution_level 2.0 falls back to 1.0).

Boundary (verified by census + a sweep at main 56f12c51): within
JSON-representable values, the section-clearing malformed class for
agent_audit is exactly the non-finite float family at the two cast
sites. Wrong-typed sequence values that the guards already catch
(string "bad", a dict, a list, a non-integer float, the NaN token)
normalize safely with all records intact; the boundary controls
below pin that behavior as UNCHANGED under the decided contract —
the refusal scope is values that would otherwise clear a section,
not every malformed value.

Fixture shapes: bases are writer-shaped (open_program +
capture_agent_action, the sole audit writer, + persist save), then
mutated at the JSON level only — the method of the 2026-11-22
probes. Non-finite tokens are written as literal JSON text via a
sentinel replacement, exactly as a crafted/corrupt file would carry
them. inspire/forces sections are set at the JSON level on the
writer-shaped base (the neighbor-probe method of record 7079514919).

Each refusal case asserts four legs:
  refused_typed    load raises persist_rest.ProgramLoadError
  bytes_unchanged  the load attempt writes nothing (sha256 equal)
  no_silent_clear  refusal, or the loaded state is whole
  resave_preserves refusal, or a save + reload keeps the section
                   whole (including preserved malformed originals)
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from form.open import open_program
from form.persist import save
from form.persist_rest import load, ProgramLoadError
from form.dell_matrix.agent_coordinator import (
    capture_agent_action, AUDIT_COMMITTED, AUDIT_DENIED, AUDIT_ATTEMPTED)

_SENT = "__P0S_TOKEN__"
_RESULTS = [AUDIT_COMMITTED, AUDIT_DENIED, AUDIT_ATTEMPTED]
_INSPIRE_VALID = {"prefs": {"weights": {"w1": 0.5}, "confirms": 3, "rejects": 2}}
_FORCES_VALID = {"active": [], "water": {"intensity": 0.7, "evolution_level": 2.0}}
_SHAPE_BAD = {"audit_id": "someone-else", "audit_seq": 9, "detail": "shape-bad"}


def _sha(path):
    if not os.path.isfile(path):
        return "ABSENT"
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _write(tmp, name, data, token=None):
    text = json.dumps(data, indent=2)
    if token is not None:
        text = text.replace(f'"{_SENT}"', token)
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def _audit_state(p):
    recs = getattr(p, "agent_audit_records", None) or {}
    mal = getattr(p, "agent_audit_malformed", None) or []
    return {
        "ids": sorted(recs.keys()),
        "seq": getattr(p, "agent_audit_seq", None),
        "malformed": mal,
        "malformed_notes": [m.get("note") if isinstance(m, dict) else repr(m)
                            for m in mal],
    }


def _inspire_state(p):
    st = getattr(p, "inspire", None)
    prefs = getattr(st, "prefs", None)
    return {
        "weights": dict(getattr(prefs, "weights", {}) or {}),
        "confirms": getattr(prefs, "confirms", None),
        "rejects": getattr(prefs, "rejects", None),
    }


def _forces_state(p):
    ff = getattr(p, "forces", None)
    water = getattr(ff, "water", None)
    return {
        "intensity": getattr(water, "intensity", None),
        "evolution": getattr(water, "evolution_level", None),
    }


def _attempt(owner, path):
    """One staged load. Returns (program|None, exception|None)."""
    try:
        return load(owner, path, activate=False), None
    except Exception as exc:  # noqa: BLE001 — the outcome IS the observation
        return None, exc


def smoke() -> bool:
    print("=== P0-S RESTORE REFUSAL FIXTURES (EXPECTED RED UNTIL THE "
          "AUTHORIZED BUILD) ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    pid = os.getpid()
    owner_a, owner_b = f"P0sFxA{pid}", f"P0sFxB{pid}"
    tmp = tempfile.mkdtemp(prefix="p0s_fixtures_")
    try:
        # ---- writer-shaped bases -------------------------------------
        pa = open_program(owner_a)
        ids_a = []
        for i in range(3):
            made = capture_agent_action(
                pa, subject=f"fixture-subject-{i + 1}",
                request_id=f"req-{owner_a}-{i + 1}", operation="fixture_op",
                target="fixture-target", result=_RESULTS[i],
                detail=f"base record {i + 1} for {owner_a}")
            ids_a.append(made["audit_id"])
        base_a_path = os.path.join(tmp, "base_a.json")
        save(pa, base_a_path)
        with open(base_a_path, encoding="utf-8") as f:
            base_a = json.load(f)

        pb = open_program(owner_b)
        ids_b = []
        for i in range(2):
            made = capture_agent_action(
                pb, subject=f"fixture-subject-b{i + 1}",
                request_id=f"req-{owner_b}-{i + 1}", operation="fixture_op",
                target="fixture-target", result=_RESULTS[i],
                detail=f"base record {i + 1} for {owner_b}")
            ids_b.append(made["audit_id"])
        base_b_path = os.path.join(tmp, "base_b.json")
        save(pb, base_b_path)
        b_sha0 = _sha(base_b_path)

        def fresh_a():
            return json.loads(json.dumps(base_a))

        def aa_whole(p):
            st = _audit_state(p)
            return st["ids"] == sorted(ids_a) and st["seq"] == 3 and st["malformed"] == []

        def aa_whole_a5(p):
            st = _audit_state(p)
            kept = any(isinstance(m, dict) and m.get("original") == _SHAPE_BAD
                       for m in st["malformed"])
            return st["ids"] == sorted(ids_a) and kept

        def inspire_whole(p):
            st = _inspire_state(p)
            return (st["weights"] == {"w1": 0.5} and st["confirms"] == 3
                    and st["rejects"] == 2)

        def forces_whole(p):
            st = _forces_state(p)
            return st["intensity"] == 0.7 and st["evolution"] == 2.0

        def describe(p, section):
            if section == "aa":
                st = _audit_state(p)
                return (f"records={len(st['ids'])}/3 seq={st['seq']} "
                        f"malformed={st['malformed_notes']}")
            if section == "inspire":
                return f"inspire={_inspire_state(p)}"
            return f"forces={_forces_state(p)}"

        # ---- refusal-case runner --------------------------------------
        def refusal_case(name, fixture_path, owner, whole, section):
            h0 = _sha(fixture_path)
            p, exc = _attempt(owner, fixture_path)
            refused = isinstance(exc, ProgramLoadError)
            if exc is not None:
                outcome = f"raised {type(exc).__name__}"
            else:
                outcome = "load ok; " + describe(p, section)
            rec(f"{name}_refused_typed", refused, outcome)
            rec(f"{name}_bytes_unchanged", _sha(fixture_path) == h0)
            rec(f"{name}_no_silent_clear",
                exc is not None or whole(p), outcome)
            if exc is not None:
                rec(f"{name}_resave_preserves", True, "refused: nothing to resave")
            else:
                out = os.path.join(tmp, name + "_resaved.json")
                save(p, out)
                q, exc2 = _attempt(owner, out)
                ok = exc2 is None and whole(q)
                rec(f"{name}_resave_preserves", ok,
                    "resave+reload: " + ("raised " + type(exc2).__name__
                                          if exc2 is not None else describe(q, section)))

        # ---- agent_audit refusal fixtures ------------------------------
        d = fresh_a(); d["agent_audit"]["audit_seq"] = _SENT
        refusal_case("aa_sec_seq_1e309", _write(tmp, "aa_sec_1e309.json", d, "1e309"),
                     owner_a, aa_whole, "aa")
        d = fresh_a(); d["agent_audit"]["audit_seq"] = _SENT
        refusal_case("aa_sec_seq_neg1e309", _write(tmp, "aa_sec_neg1e309.json", d, "-1e309"),
                     owner_a, aa_whole, "aa")
        d = fresh_a(); d["agent_audit"]["audit_seq"] = _SENT
        refusal_case("aa_sec_seq_infinity", _write(tmp, "aa_sec_inf.json", d, "Infinity"),
                     owner_a, aa_whole, "aa")
        d = fresh_a(); d["agent_audit"]["records"][ids_a[1]]["audit_seq"] = _SENT
        refusal_case("aa_rec_seq_1e309", _write(tmp, "aa_rec_1e309.json", d, "1e309"),
                     owner_a, aa_whole, "aa")
        # combined: per-record trigger + a shape-bad record whose complete
        # original the designed path preserves — the reset erases both the
        # valid records and the preserved evidence.
        d = fresh_a()
        d["agent_audit"]["records"]["badrec"] = dict(_SHAPE_BAD)
        d["agent_audit"]["records"][ids_a[1]]["audit_seq"] = _SENT
        refusal_case("aa_rec_inf_plus_shapebad",
                     _write(tmp, "aa_combined.json", d, "1e309"),
                     owner_a, aa_whole_a5, "aa")

        # ---- inspire / forces refusal fixtures --------------------------
        d = fresh_a()
        d["inspire"] = json.loads(json.dumps(_INSPIRE_VALID))
        d["inspire"]["prefs"]["confirms"] = "bad"
        refusal_case("inspire_confirms_bad", _write(tmp, "inspire_bad.json", d),
                     owner_a, inspire_whole, "inspire")
        d = fresh_a()
        d["forces"] = json.loads(json.dumps(_FORCES_VALID))
        d["forces"]["water"]["intensity"] = "bad"
        refusal_case("forces_intensity_bad", _write(tmp, "forces_bad.json", d),
                     owner_a, forces_whole, "forces")

        # ---- controls: behavior the contract PRESERVES ------------------
        p, exc = _attempt(owner_a, base_a_path)
        ok = exc is None and aa_whole(p)
        if ok:
            out = os.path.join(tmp, "ctl_roundtrip.json")
            save(p, out)
            q, exc2 = _attempt(owner_a, out)
            ok = exc2 is None and aa_whole(q)
            with open(out, encoding="utf-8") as f:
                saved_aa = json.load(f).get("agent_audit") or {}
            ok = ok and (saved_aa.get("records") or {}) == base_a["agent_audit"]["records"]
        rec("ctl_valid_base_roundtrips_whole", ok)

        d = fresh_a()
        for key in ("agent_audit", "inspire", "forces"):
            d.pop(key, None)
        p, exc = _attempt(owner_a, _write(tmp, "ctl_absent.json", d))
        st = _audit_state(p) if p is not None else {}
        rec("ctl_absent_sections_legacy_defaults",
            exc is None and st.get("ids") == [] and st.get("seq") == 0
            and st.get("malformed") == [] and _inspire_state(p)["weights"] == {},
            f"exc={exc!r} audit={st}")

        d = fresh_a(); d["agent_audit"] = None
        p, exc = _attempt(owner_a, _write(tmp, "ctl_null.json", d))
        st = _audit_state(p) if p is not None else {}
        rec("ctl_null_section_designed_note",
            exc is None and st.get("malformed") == [{
                "note": "agent_audit section: explicit null is malformed",
                "original": None}],
            f"exc={exc!r} malformed={st.get('malformed')}")

        # designed quarantine: a non-dict records value is preserved whole
        # as a malformed original and survives a save + reload.
        d = fresh_a(); d["agent_audit"]["records"] = [1, 2]
        p, exc = _attempt(owner_a, _write(tmp, "ctl_quarantine.json", d))
        kept = p is not None and any(
            isinstance(m, dict) and m.get("original") == [1, 2]
            for m in _audit_state(p)["malformed"])
        if kept:
            out = os.path.join(tmp, "ctl_quarantine_resaved.json")
            save(p, out)
            q, exc2 = _attempt(owner_a, out)
            kept = exc2 is None and any(
                isinstance(m, dict) and m.get("original") == [1, 2]
                for m in _audit_state(q)["malformed"])
        rec("ctl_quarantine_original_preserved_through_resave", bool(kept))

        # retention: a file that ALREADY carries a preserved malformed
        # original alongside valid records keeps both through load/save.
        d = fresh_a()
        d["agent_audit"]["malformed"] = [{
            "note": "agent_audit.records is not a dict",
            "type": "list", "original": [1, 2]}]
        p, exc = _attempt(owner_a, _write(tmp, "ctl_preserved.json", d))
        kept = p is not None and _audit_state(p)["ids"] == sorted(ids_a) and any(
            isinstance(m, dict) and m.get("original") == [1, 2]
            for m in _audit_state(p)["malformed"])
        if kept:
            out = os.path.join(tmp, "ctl_preserved_resaved.json")
            save(p, out)
            q, exc2 = _attempt(owner_a, out)
            kept = exc2 is None and _audit_state(q)["ids"] == sorted(ids_a) and any(
                isinstance(m, dict) and m.get("original") == [1, 2]
                for m in _audit_state(q)["malformed"])
        rec("ctl_previously_preserved_malformed_retained", bool(kept))

        # boundary controls: wrong-typed / non-finite values the guards
        # already catch normalize safely today and are NOT refusal cases
        # under the decided contract — behavior must stay exactly this.
        d = fresh_a(); d["agent_audit"]["audit_seq"] = "bad"
        p, exc = _attempt(owner_a, _write(tmp, "ctl_bnd_badstr.json", d))
        rec("ctl_boundary_section_seq_bad_string_normalizes",
            exc is None and aa_whole(p),
            "load ok; " + describe(p, "aa") if p is not None else f"exc={exc!r}")
        d = fresh_a(); d["agent_audit"]["records"][ids_a[1]]["audit_seq"] = {"v": 3}
        p, exc = _attempt(owner_a, _write(tmp, "ctl_bnd_dictseq.json", d))
        rec("ctl_boundary_record_seq_dict_normalizes",
            exc is None and aa_whole(p),
            "load ok; " + describe(p, "aa") if p is not None else f"exc={exc!r}")
        d = fresh_a(); d["agent_audit"]["audit_seq"] = _SENT
        p, exc = _attempt(owner_a, _write(tmp, "ctl_bnd_nan.json", d, "NaN"))
        rec("ctl_boundary_section_seq_nan_caught",
            exc is None and aa_whole(p),
            "load ok; " + describe(p, "aa") if p is not None else f"exc={exc!r}")

        d = fresh_a(); d["inspire"] = json.loads(json.dumps(_INSPIRE_VALID))
        p, exc = _attempt(owner_a, _write(tmp, "ctl_inspire_valid.json", d))
        ok = exc is None and inspire_whole(p)
        if ok:
            out = os.path.join(tmp, "ctl_inspire_resaved.json")
            save(p, out)
            q, exc2 = _attempt(owner_a, out)
            ok = exc2 is None and inspire_whole(q)
        rec("ctl_inspire_valid_roundtrips", ok)

        d = fresh_a(); d["forces"] = json.loads(json.dumps(_FORCES_VALID))
        p, exc = _attempt(owner_a, _write(tmp, "ctl_forces_valid.json", d))
        ok = exc is None and forces_whole(p)
        if ok:
            out = os.path.join(tmp, "ctl_forces_resaved.json")
            save(p, out)
            q, exc2 = _attempt(owner_a, out)
            ok = exc2 is None and forces_whole(q)
        rec("ctl_forces_valid_roundtrips", ok)

        # ---- second-owner isolation --------------------------------------
        d = fresh_a(); d["agent_audit"]["audit_seq"] = _SENT
        poisoned_a = _write(tmp, "iso_poisoned_a.json", d, "1e309")
        p, exc = _attempt(owner_a, poisoned_a)
        if p is not None:
            save(p, os.path.join(tmp, "iso_a_resaved.json"))
        rec("iso_other_owner_file_bytes_untouched", _sha(base_b_path) == b_sha0)
        q, exc_b = _attempt(owner_b, base_b_path)
        st = _audit_state(q) if q is not None else {}
        rec("iso_other_owner_loads_whole",
            exc_b is None and st.get("ids") == sorted(ids_b) and st.get("seq") == 2
            and st.get("malformed") == [],
            f"exc={exc_b!r} audit={st}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        try:
            from form.persist import _path
            from form.dell_matrix.nursery import owner_nursery_path
            for o in (owner_a, owner_b):
                for path in (_path(o), owner_nursery_path(o)):
                    if path and os.path.exists(path):
                        os.remove(path)
        except Exception:
            pass
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
