#!/usr/bin/env python3
"""P3 wiring proof — Program-surface closures (master plan P3).

Proves, on real paths, the P3 outcomes:
- TD-2: the five session-section modules share the kit's ONE sentinel.
- TD-5: cross-door id creation goes through idea_create.unique_unit_id.
- TD-6: tokenizer/Jaccard parity on the canonical text_metrics kit,
  with harmony's documented deliberate difference intact.
- TD-4: idea_grow.pair_affinity agreed with canonical ringed
  _affinity (P3); SD-5 retired idea_grow — the guard now checks
  the duplicate is gone and the canonical authority computes.
- TD-7: the seven _ts/_utcnow delegations share the utc_time format.
- Wires: smoke_ux on the Program, radial_drift forgetting far shells,
  kaomoji registry consulted by the face, Avatar.status via read_body,
  correction_candidates projection, help_lines renderer.
- Retirements: the deleted names are absent; the canonical siblings
  they shadowed are still present.
- REPL (real user path, subprocess): drift / corrections / actions.
"""
from __future__ import annotations

import contextlib
import io
import os
import re
import subprocess
import sys

OWNER = "P3Wiring"
REPL_OWNER = "P3WireRepl"


def _cleanup(owner: str) -> None:
    import shutil
    state = os.path.join("form", "state")
    if not os.path.isdir(state):
        return
    for name in os.listdir(state):
        if owner.lower() in name.lower():
            path = os.path.join(state, name)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)


def smoke() -> bool:
    print("=== P3 WIRING PROOF ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    try:
        # ── TD-2: one sentinel across the session-section kit ────────
        from form.dell_matrix import session_section as kit
        from form.dell_matrix import (bimo_forge, connection_session,
                                      onboarding_session, perspective_studio,
                                      workshop_session)
        mods = (connection_session, workshop_session, perspective_studio,
                onboarding_session, bimo_forge)
        rec("td2_one_sentinel", all(m._MISSING is kit.MISSING for m in mods))
        rec("td2_kit_contract", kit.MISSING is not None
            and callable(kit.validate_records_section)
            and callable(kit.serialize_records_section))

        # ── TD-5: unique ids through the canonical helper ────────────
        from form.idea_create import slug_id, unique_unit_id
        units = {"wiring_probe": object()}
        rec("td5_slug", slug_id("My Cool Idea!") == "my_cool_idea")
        rec("td5_suffix", unique_unit_id(units, "Wiring Probe") == "wiring_probe_1")
        rec("td5_prefix", unique_unit_id({}, "Stem", prefix="plant_") == "plant_stem")
        rec("td5_child_start2", unique_unit_id({"base": 1, "base_2": 1}, "base",
                                               suffix_start=2) == "base_3")

        # ── TD-6: tokenizer parity on the kit ────────────────────────
        from form.dell_matrix import text_metrics as tm
        from form.dell_matrix import ringed_growth, verita
        from form.mandell import knowledge_selector as ks
        sample = "To be or not to be, an AI era"
        rec("td6_ks_is_kit", ks._tokens is tm.tokens and ks._jaccard is tm.jaccard)
        rec("td6_rg_is_kit", ringed_growth._tokens is tm.tokens_of
            and ringed_growth._jaccard is tm.jaccard)
        rec("td6_shared_vocab", ks._tokens(sample) == tm.tokens(sample) == {"era", "not"})
        # SD-5: floor_spirit (the third TD-6 delegator checked
        # here in P3) is retired with the dormant cluster; the
        # verita delegation remains.
        rec("td6_verita_floor", verita.tokens is tm.tokens)
        from form.dell_matrix import harmony
        rec("td6_harmony_keeps_own_tokenizer",
            harmony._TOKEN.pattern != tm.TOKEN_RE.pattern
            and harmony._pair_coherence({"a", "b"}, {"b", "c"})
            == tm.jaccard({"a", "b"}, {"b", "c"}))
        # TD-6 blast-radius binding: the canonical {3,} tokenizer must
        # not erase lexical signals other contracts own. DCC-XIII V1
        # names "no" a supported negation signal; conflict_router
        # detects negation on whole words, independent of the
        # similarity tokenizer.
        from form.mandell.conflict_router import detect_conflicts
        rec("td6_negation_signal_preserved",
            len(detect_conflicts([
                {"id": "a", "text": "plant growth needs no water"},
                {"id": "b", "text": "plant growth needs water"}])) == 1
            and len(detect_conflicts([
                {"id": "a", "text": "the sky is blue"},
                {"id": "b", "text": "the sky is not blue"}])) == 1
            and detect_conflicts([
                {"id": "a", "text": "plant growth needs water"},
                {"id": "b", "text": "plant growth needs water"}]) == [])

        # ── TD-7: one UTC format behind every _ts ────────────────────
        import form.utc_time as ut
        from form.dell_matrix import nursery, shared_main, agent_coordinator
        from form.mandell import duobeta_learn, nbd_engine
        from form.duobeta import growth as duo_growth, selfgrow
        stamps = [nursery._ts(), shared_main._ts(), duobeta_learn._ts(),
                  nbd_engine._ts(), agent_coordinator._utcnow(),
                  duo_growth.DuoBeta._ts(object()),
                  selfgrow.SelfGrow._ts(object())]
        pat = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        rec("td7_format_shared", ut.UTC_FORMAT == "%Y-%m-%dT%H:%M:%SZ"
            and len(stamps) == 7 and all(pat.match(s) for s in stamps))

        # ── Program-level wires ──────────────────────────────────────
        from form.open import open_program
        p = open_program(OWNER)
        try:
            rec("w1_smoke_ux", p.smoke_ux() is True)

            plane = p.cube.session.plane
            from form.dell_matrix import needs
            a = needs.parse_and_place(p, "create an idea called Wiring Probe detail: first")
            b = needs.parse_and_place(p, "create an idea called Wiring Probe detail: second")
            rec("td5_cross_door", a["id"] == "wiring_probe"
                and b["id"] == "wiring_probe_1" and a["id"] != b["id"],
                f"{a['id']} vs {b['id']}")

            # TD-4 closed in P3 by adapting idea_grow.pair_affinity
            # onto the canonical authority; SD-5 (P8) completed the
            # disposition by RETIRING idea_grow (zero production
            # callers). The guard now: the duplicate is gone and
            # the canonical authority computes.
            import importlib.util as _ilu
            ca = ringed_growth._affinity(plane, a["id"], b["id"])
            rec("td4_affinity_parity",
                _ilu.find_spec("form.dell_matrix.idea_grow") is None
                and ca["affinity"] >= 0.0 and "shared" in ca
                and "jaccard" in ca)

            p.place("far_unit", "FarUnit", words="payload words here",
                    x=9.0, y=9.0)
            out = p.radial_drift(outer_shell=1)
            far = plane.units.get("far_unit")
            cell_gone = True
            try:
                cell = p.lattice.cells.get((9, 9, 0)) or p.lattice.cells.get((9, 9))
                cell_gone = cell is None or getattr(cell, "content", None) is None
            except Exception:
                cell_gone = True
            rec("w2_drift_forgets", out.get("ok") is True
                and out.get("soft_forgotten", 0) >= 1 and cell_gone,
                f"forgotten={out.get('soft_forgotten')}")

            # W3: kaomoji consult — default untouched, then pack faces.
            from form.avatar.face import Expression, FaceController
            rec("w3_default_face", p.face.show() == "(·_·)")
            shown = p.face.set(Expression.SOFT)
            rec("w3_kaomoji_consult", p.kaomoji.active == "love"
                and shown == "(♥ω♥)", f"active={p.kaomoji.active} shown={shown}")
            bare = FaceController()
            rec("w3_bare_default", bare.set(Expression.SOFT) == "(◕‿◕)")

            # W5: correction projection, both branches.
            from form.mandell import runtime_observe as ro
            lst = ro.correction_candidates(p)
            one = ro.correction_candidates(p, "no-such-outcome")
            rec("w5_corrections", lst.get("ok") is True
                and lst.get("count") == len(lst.get("edges") or [])
                and one.get("ok") is False)
        finally:
            _cleanup(OWNER)

        # W4: Avatar.status built from read_body.
        import inspect
        from form.avatar.body import Avatar
        av = Avatar(name="Probe")
        av.body.holding = "lantern"
        st = av.status()
        rb = av.read_body()
        rec("w4_status_read_body", st["holding"] == "lantern"
            and st["pos"] == rb.pos and st["facing"] == rb.facing.name
            and "read_body()" in inspect.getsource(Avatar.status))

        # W6: registry text renderer.
        from form.dell_matrix.actions_registry import help_lines
        rec("w6_help_lines", help_lines("builder").startswith("Actions (mode=builder)")
            and help_lines("bogus").startswith("Actions (mode=builder)")
            and "Pulse: pulse" in help_lines("depth"))

        # ── Retirements absent; canonical siblings present ───────────
        import importlib
        checks = []
        m = importlib.import_module("form.open")
        checks.append(not hasattr(m.Program, "ce_ensure")
                      and not hasattr(m.Program, "command_cost")
                      and hasattr(m.Program, "smoke_ux")
                      and hasattr(m.Program, "radial_drift"))
        hc = importlib.import_module("form.dell_matrix.harmonic_core")
        checks.append(not hasattr(hc, "radial_drift_candidates")
                      and hasattr(hc, "apply_radial_soft_forget"))
        cl = importlib.import_module("form.dell_matrix.canonical_lifecycle")
        checks.append(not hasattr(cl, "filter_active") and hasattr(cl, "is_active"))
        bd = importlib.import_module("form.avatar.body")
        checks.append(not hasattr(bd.Avatar, "pick_up")
                      and not hasattr(bd.Avatar, "place_down")
                      and not hasattr(bd.Avatar, "set_reach")
                      and hasattr(bd.Avatar, "read_body"))
        cii = importlib.import_module("form.mandell.core_ii")
        checks.append(not hasattr(cii, "all_contracts")
                      and not hasattr(cii, "family_index")
                      and hasattr(cii, "contract"))
        sd = importlib.import_module("form.mandell.seed")
        checks.append(not hasattr(sd, "seed_from_dell_chain"))
        tr = importlib.import_module("form.mandell.translate")
        checks.append(not hasattr(tr, "translate_to_mandel") and hasattr(tr, "translate"))
        mf = importlib.import_module("form.mandell.manifest")
        checks.append(not hasattr(mf, "manifest_from_lookup")
                      and hasattr(mf, "manifest_from_dell"))
        rec_mod = importlib.import_module("form.mandell.core_i_recovery")
        pr = importlib.import_module("form.persist_rest")
        checks.append(not hasattr(rec_mod, "list_checkpoints")
                      and hasattr(pr, "list_checkpoints"))
        asp = importlib.import_module("form.mandell.address_space")
        checks.append(not hasattr(asp, "promotion_requirements"))
        led = importlib.import_module("form.mandell.circuit_ledger")
        checks.append(not hasattr(led, "closed_set") and hasattr(led, "ready_set"))
        ht = importlib.import_module("form.mandell.harmonic_truths")
        checks.append(not hasattr(ht, "truth_ids") and hasattr(ht, "truths"))
        mr = importlib.import_module("form.mandell.manifest_resolver")
        checks.append(not hasattr(mr, "keep_modifier") and hasattr(mr, "resolve_manifest"))
        sg = importlib.import_module("form.mandell.signatures")
        checks.append(not hasattr(sg, "list_signatures") and hasattr(sg, "get_signature"))
        cn = importlib.import_module("form.mandell.canonical")
        checks.append(not hasattr(cn, "cell_graph") and hasattr(cn, "seed_graph"))
        fp = importlib.import_module("form.dell_matrix.first_person")
        checks.append(not hasattr(fp, "face_toward")
                      and hasattr(fp, "first_person_view")
                      and isinstance(fp.neighbors_for_form("cube", 0, 0, 0), dict))
        for dead in ("form.realize", "form.dell_matrix.high_value_api"):
            try:
                importlib.import_module(dead)
                checks.append(False)
            except ModuleNotFoundError:
                checks.append(True)
        rec("retirements_absent", all(checks), f"{sum(checks)}/{len(checks)}")

        # KEEP evidence: code_evolution's five are develop_loop's steps.
        import inspect as _insp
        from form.dell_matrix import code_evolution as ce
        src = _insp.getsource(ce.develop_loop)
        rec("keep_code_evolution", all(hasattr(ce, n) for n in (
            "exhaust_shells", "grow_from_root", "research_with_internet",
            "completion_checklist", "mark_complete"))
            and all(f"{n}(" in src for n in (
                "exhaust_shells", "grow_from_root", "completion_checklist",
                "mark_complete")))

        # ── REPL real user path (subprocess, this tree) ──────────────
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "form.repl", "--owner", REPL_OWNER],
                input="drift 1\ncorrections\nactions\nquit\n",
                capture_output=True, text=True, timeout=180,
                cwd=os.getcwd())
            out_txt = proc.stdout + proc.stderr
            rec("repl_paths", "Radial drift (shell >= 1)" in out_txt
                and "correction candidates:" in out_txt
                and "Actions (mode=" in out_txt)
        finally:
            _cleanup(REPL_OWNER)
    except Exception:
        import traceback
        traceback.print_exc()
        rec("suite_completed", False)

    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r) and len(r) > 0


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
