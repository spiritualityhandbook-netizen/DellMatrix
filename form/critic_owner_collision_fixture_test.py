#!/usr/bin/env python3
"""Critic P1 / F7 — owner-namespace collision, NURSERY-FIRST order
(the circuit's regression suite; born as the failing-first fixture).

This suite expresses the isolation contract for the one order the
existing owner_namespace_collision_test never exercises: the first
owner writes ONLY nursery state (nursery.add persists immediately)
and never saves a program file before the second owner constructs.
As the prepared fixture it ran EXPECTED RED 4/7 against main
91eaa5a5 — failing exactly F2.second_owner_sees_none_of_first,
F2.private_detail_never_crosses, F3.first_owner_not_locked_out.
The authorized build (nursery owner binding: the nursery file
records its raw owner under a reserved section and the load /
add / save doors enforce it with OwnerCollisionError, extending
the program file's 72-34/DD-12 identity doctrine) turns it 7/7
GREEN; it now stands as the circuit's regression suite.

Authority / evidence trail:

  * Critic Master Critique, PR #530 review 6066727800, finding
    comment 4702349097 (P1): form/persist.py _safe_owner collapses
    distinct raw owners ("Fresh/Owner", "Fresh_Owner") onto one
    safe name, hence one nursery file; nursery.add persists
    immediately while no program file exists, so the second owner's
    fresh Program is constructed holding the first owner's proposal
    INCLUDING private detail; after the second owner saves, the
    first owner is locked out with OwnerCollisionError.
  * Uni verdict 7178450928 on issue #512: CONFIRMED_BEHAVIOR, REAL.
  * Uni first-hand reproduction at main 91eaa5a5 (2026-11-25):
    leak=True, detail_leak=True, first-owner lockout=True
    (hidden_files/critic_fixes_2026-11-25/repro_output.txt).
  * Director authorization 7180713277 on issue #512 (2026-11-25):
    "For 7, authorize a bounded owner-isolation repair covering
    the nursery-first path and preservation of existing owners'
    data."
  * Correction inside PR #531: Critic finding 4703303960 on
    PR #531 (Uni verdict 7181105320, REAL) — the F7 build itself
    regressed the empty-string owner: the writer stamps
    {"owner": ""} (lawful at the program door; _safe_owner("")
    maps to "operator"; pre-F7 main round-trips it) while the
    loader demanded a non-empty owner string and
    stored_nursery_owner() returned None for the same record, so
    a saved empty-owner nursery was unreachable. The E-series
    checks below pin the corrected contract: the recorded
    identity is the exact raw owner string, validity is
    isinstance(owner, str), and "" binds only to "".
  * Director scope ruling 7181859606 on PR #531 (2026-11-25):
    scope CONFIRM at 6a57faf6 stands, release HELD on one
    distinction — the no-proof legacy adoption guard checked
    `staged` (proposals) only, while the loader separately
    applies staged dispositions, organization edit receipts and
    grant-use receipts to the adopted nursery, so zero proposals
    did not prove "nothing exists to hand over." Uni first-hand
    probe (hidden_files/critic_fixes_2026-11-25/
    legacy_adoption_probe.py, output saved alongside): CONFIRMED
    on all three sections — a records-only legacy file was
    silently adopted by the colliding namesake, who read the
    first owner's records and whose next save restamped the file
    as his own with the records intact. The L-series checks below
    pin the repaired rule: no-proof adoption requires EVERY
    owner-scoped section the loader applies to be empty/absent;
    the genuinely empty and proven-owner controls still adopt.
    The L legs ran EXPECTED RED against the unrepaired loader
    (the six refusal/crossing checks failing, controls green)
    before the repair turned them green.

  * Director CORRECTION_REQUIRED 7185483691 on PR #531
    (2026-11-26): release withheld at 2ae49747 on a new
    exact-source discrepancy — form/mandell/core_i_recovery.py
    _eager_converge_live emits OWNER_SECTION_KEY only
    `if getattr(nursery, "owner", None):`, a truthiness check
    that excludes the lawful empty-string owner, so a rollback
    silently UNBINDS the "" owner's nursery. Uni first-hand
    verification widened the seam to the whole failure class
    (owner truthiness contradicting the isinstance-str contract
    on the "" owner's save/load/rollback path): the rollback
    never even reached the converge line, because
    persist_rest._validate_program_data rejects a present ""
    owner ("'owner' must be a non-empty string") when staging
    the generation's program member — the same rejection hits a
    plain persist_rest.load("") of the file save() just wrote —
    and persist.stored_program_owner returns None for a
    ""-recorded program file, erasing the sibling proof the
    L-series adoption guard relies on. The R-series checks below
    pin the repaired class: None (absent) is distinguished from
    "" (a lawful recorded identity) at all three sites; the
    rollback completes, the identity record and the owner-scoped
    records survive it, and the colliding named load refuses.

Mechanism (verified against this tree):

  * form/persist.py:50-51 — _safe_owner maps every character that
    is not alphanumeric / '-' / '_' to '_'; it is many-to-one.
  * form/dell_matrix/nursery.py — owner_nursery_path keys the
    nursery file by the safe name ALONE:
    nursery_<_safe_owner(owner)>.json. Before this circuit the
    nursery file recorded no raw owner anywhere in its payload
    (verified: proposal records carry no owner field), so the
    nursery door had no identity to check even in principle. The
    build adds the OWNER_SECTION_KEY identity record, enforced by
    Nursery.load(path, owner=...) / add() / save().
  * form/dell_matrix/nursery.py (Nursery.add, tail) — add() calls
    self.save(): a proposal is durable the moment it is added.
  * form/open.py — Program.__post_init__ loads the live nursery
    with owner=self.owner, so the nursery identity record is
    enforced at construction exactly as the program file's is.
  * The original identity guard, persist.assert_program_owner_access
    (form/persist.py, called at Program construction), checks ONLY
    the program file program_<safe>.json. In the nursery-first
    order that file does not exist yet, the guard sees no proven
    owner and passes — which is why the nursery door needed its
    own binding. Once the second owner saved a program file, the
    same guard then locked the FIRST owner out.

Why the existing suite is green: owner_namespace_collision_test
build() always calls save(p) for the first owner before the second
owner loads, so the program-file guard fires and isolation holds.
The nursery-first branch is the uncovered seam.

Contract under test (shape-agnostic — a repair may either give
colliding owners disjoint namespaces OR refuse the foreign nursery
loudly at the nursery door; both satisfy isolation, silent
adoption satisfies neither):

- F1 premise: the chosen pair is distinct raw and DOES collide
  under _safe_owner; the control pair does not.
- F2 nursery-first no-adoption: owner A adds a proposal carrying
  private detail and never saves a program; constructing owner B
  must raise, or B's nursery must contain NONE of A's proposals
  (and in particular not the private detail).
- F3 no first-owner lockout: after B's flow completes (construct,
  and save if construction was allowed), A must still construct
  successfully and still hold its own proposal.
- K1 control: two NON-colliding owners stay fully isolated
  through the same nursery-first flow (A adds only; B constructs
  empty; B saves; A still constructs with its proposal intact).
- L records-only legacy adoption (Director 7181859606): a legacy
  file (no __owner__ section, no sibling program-file proof)
  holding ZERO proposals but a nonempty dispositions, edit-
  receipt, or grant-use-receipt section must REFUSE the colliding
  namesake's named load (bytes preserved) — no owner-scoped
  section may cross without proof. Controls: a genuinely empty
  legacy file still adopts; a records-bearing legacy file whose
  sibling program file PROVES the requester still adopts.

Labels: INTEGRATION in-process.
Hygiene: uuid-unique owners; exact-pattern cleanup (files + the
ideas_<safe> directory); cleanup failures reported as a failing
check, never swallowed.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import shutil
import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

from form.persist import _STATE_DIR, _path, _safe_owner, save
from form.dell_matrix.nursery import (
    Nursery, owner_nursery_path, stored_nursery_owner)
from form.open import open_program

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]

A = f"CF{RUN}/A"   # raw owner with a separator (nursery-first)
B = f"CF{RUN}_A"   # distinct raw owner, same safe name
P = f"CF{RUN}P"    # non-colliding control pair
Q = f"CF{RUN}Q"
SECRET = "alpha private detail — must never cross owners"
LA = f"LG{RUN}/A"  # legacy records-only pair (Director 7181859606)
LB = f"LG{RUN}_A"  # distinct raw owner, same safe name as LA


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")


def cleanup():
    for f in glob.glob(os.path.join(_STATE_DIR, f"*{RUN}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.unlink(f)
        except OSError as e:
            _CLEANUP_ERRORS.append(f"{f}: {e}")


def construct_or_none(owner):
    """Return (program, raised) — a loud refusal is a legitimate
    isolation outcome; silent foreign adoption is not."""
    try:
        return open_program(owner), False
    except Exception:
        return None, True


def main():
    cleanup()
    check("F1.collision_premise",
          A != B and _safe_owner(A) == _safe_owner(B)
          and owner_nursery_path(A) == owner_nursery_path(B)
          and _path(P) != _path(Q),
          f"safe={_safe_owner(A)}")

    # --- Nursery-first: A adds ONLY; no program save ----------
    pa = open_program(A)
    prop = pa.nursery.add("alpha private idea", "alpha words",
                          detail=SECRET)
    check("F1.nursery_first_premise",
          os.path.isfile(owner_nursery_path(A))
          and not os.path.isfile(_path(A)),
          "nursery durable, program file absent")

    # --- F2: B must not adopt A's nursery ---------------------
    pb, b_raised = construct_or_none(B)
    leaked = (pb is not None and prop.id in pb.nursery.proposals)
    detail_leaked = bool(
        leaked and pb.nursery.proposals[prop.id].detail == SECRET)
    check("F2.second_owner_sees_none_of_first",
          b_raised or not leaked,
          f"raised={b_raised} leaked={leaked}")
    check("F2.private_detail_never_crosses",
          b_raised or not detail_leaked,
          f"detail_leaked={detail_leaked}")

    # --- F3: B saves (if allowed); A must not be locked out ---
    if pb is not None:
        try:
            save(pb)
        except Exception:
            pass  # a loud save refusal also protects A — F3 judges A
    pa2, a_raised = construct_or_none(A)
    check("F3.first_owner_not_locked_out",
          not a_raised and pa2 is not None and pa2.owner == A
          and prop.id in pa2.nursery.proposals,
          f"a_raised={a_raised}")

    cleanup()

    # --- K1: non-colliding control, same nursery-first flow ---
    pp = open_program(P)
    p_prop = pp.nursery.add("papa idea", "papa words",
                            detail="papa detail")
    pq, q_raised = construct_or_none(Q)
    k1a = not q_raised and pq is not None \
        and p_prop.id not in pq.nursery.proposals
    if pq is not None:
        try:
            save(pq)
        except Exception:
            k1a = False
    pp2, p_raised = construct_or_none(P)
    k1b = not p_raised and pp2 is not None \
        and p_prop.id in pp2.nursery.proposals
    check("K1.noncolliding_nursery_first_isolated", k1a and k1b)

    cleanup()

    # --- L: records-only legacy adoption (Director 7181859606) -
    # A legacy file (no __owner__ section) with ZERO proposals but
    # a nonempty owner-scoped section must not cross to the
    # colliding namesake without proof. The named load exercised
    # here is Nursery.load(path, owner=...) — the exact call
    # form/open.py makes at Program construction.
    l_path = owner_nursery_path(LA)
    check("L0.legacy_pair_premise",
          LA != LB and owner_nursery_path(LA) == owner_nursery_path(LB)
          and not os.path.isfile(_path(LA)),
          f"safe={_safe_owner(LA)}")

    def write_legacy(payload):
        with open(l_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        with open(l_path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()

    def named_load_or_none(owner):
        try:
            return Nursery.load(l_path, owner=owner), False
        except Exception:
            return None, True

    def file_sha():
        with open(l_path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()

    L_DISP = f"legacy-{RUN}-disposition-note"
    L_EDIT = f"legacy-{RUN}-edit-topic"
    L_GRANT = f"legacy-{RUN}-grant-note"
    l_sections = [
        ("dispositions",
         {"__conflict_dispositions__": {"conflict-1": {
             "decision": "keep_mine", "decided_by": LA,
             "note": L_DISP, "at": "2026-11-20T00:00:00Z"}}},
         "conflict_dispositions", L_DISP),
        ("edit_receipts",
         {"__organization_edit_receipts__": {"op-1": {
             "operation_id": "op-1", "actor": LA,
             "proposal_id": "p-x",
             "before": {"topic": L_EDIT, "tags": [], "cluster": None},
             "after": {"topic": "renamed", "tags": [], "cluster": None},
             "kind": "human_organization_edit",
             "created": "2026-11-20T00:00:00Z"}}},
         "organization_edit_receipts", L_EDIT),
        ("grant_receipts",
         {"__grant_use_receipts__": {"rcpt-1": {
             "receipt_id": "rcpt-1", "grant_id": "grant-1",
             "actor": LA, "proposal_id": "p-x", "note": L_GRANT,
             "used_at": "2026-11-20T00:00:00Z"}}},
         "grant_use_receipts", L_GRANT),
    ]
    for sname, payload, attr, marker in l_sections:
        digest = write_legacy(payload)
        ln, l_raised = named_load_or_none(LB)
        crossed = bool(
            ln is not None
            and marker in json.dumps(getattr(ln, attr)))
        check(f"L.records_only_{sname}_refused_without_proof",
              l_raised and file_sha() == digest,
              f"raised={l_raised} bytes_preserved={file_sha() == digest}")
        check(f"L.records_only_{sname}_never_crosses",
              l_raised or not crossed,
              f"crossed={crossed}")

    # Control: a genuinely empty legacy file still adopts.
    write_legacy({})
    ln, l_raised = named_load_or_none(LB)
    check("L.genuinely_empty_legacy_adopts",
          not l_raised and ln is not None
          and not ln.proposals and not ln.conflict_dispositions
          and not ln.organization_edit_receipts
          and not ln.grant_use_receipts,
          f"raised={l_raised}")

    # Control: a records-bearing legacy file whose sibling program
    # file PROVES the requester still adopts, records included.
    write_legacy(l_sections[0][1])
    with open(_path(LB), "w", encoding="utf-8") as fh:
        json.dump({"owner": LB}, fh)
    ln, l_raised = named_load_or_none(LB)
    check("L.proven_owner_legacy_adopts",
          not l_raised and ln is not None
          and L_DISP in json.dumps(ln.conflict_dispositions),
          f"raised={l_raised}")

    cleanup()

    # --- E: the empty-string owner round-trips ---------------
    # Critic finding 4703303960 on PR #531 (a regression #531
    # itself introduced; Uni verdict 7181105320, REAL): the F7
    # writer stamps {"owner": ""} for the empty owner — lawful at
    # the program door, _safe_owner("") == "operator", and a
    # lawful round-trip on pre-F7 main — while the F7 loader's
    # shape check demanded a NON-EMPTY owner string and raised
    # NurseryLoadError, and stored_nursery_owner() returned None
    # for the same record. The saved nursery was unreachable.
    # Contract: the recorded identity is the exact raw owner
    # string; validity is isinstance(owner, str); "" binds only
    # to "". The operator-named state files carry no RUN uuid,
    # so this section snapshots them and restores them exactly.
    op_snapshot = {}
    for f in glob.glob(os.path.join(_STATE_DIR, "*operator*")):
        if os.path.isfile(f):
            with open(f, "rb") as fh:
                op_snapshot[f] = fh.read()
    try:
        e_path = owner_nursery_path("")
        check("E1.empty_owner_premise",
              _safe_owner("") == "operator"
              and e_path.endswith("nursery_operator.json"),
              f"path={os.path.basename(e_path)}")
        pe = open_program("")
        e_prop = pe.nursery.add("empty owner idea", "empty words",
                                detail="empty-owner detail")
        check("E1.empty_owner_add_persists",
              os.path.isfile(e_path),
              "nursery durable under the operator safe name")
        check("E2.stored_owner_is_empty_string",
              stored_nursery_owner(e_path) == ""
              and stored_nursery_owner(e_path) is not None,
              f"stored={stored_nursery_owner(e_path)!r}")
        pe2, e_raised = construct_or_none("")
        check("E3.empty_owner_reopen_roundtrip",
              not e_raised and pe2 is not None and pe2.owner == ""
              and e_prop.id in pe2.nursery.proposals,
              f"raised={e_raised}")
        try:
            e_ownerless = Nursery.load(e_path)
            e4 = e_prop.id in e_ownerless.proposals
        except Exception:
            e4 = False
        check("E4.ownerless_load_agrees", e4,
              "ownerless Nursery.load reads the ''-stamped file")
    finally:
        for f in glob.glob(os.path.join(_STATE_DIR, "*operator*")):
            try:
                if f in op_snapshot:
                    with open(f, "wb") as fh:
                        fh.write(op_snapshot[f])
                elif os.path.isfile(f):
                    os.unlink(f)
            except OSError as e:
                _CLEANUP_ERRORS.append(f"{f}: {e}")

    cleanup()

    # --- R: rollback preserves the "" owner's identity -------
    # Director 7185483691: _eager_converge_live's truthiness
    # check dropped the __owner__ record for the lawful
    # empty-string owner; first-hand verification found the
    # same truthiness class blocking the path earlier
    # (persist_rest program validation refuses a present ""
    # owner; persist.stored_program_owner erases it). The real
    # rollback exercised here is the canonical
    # core_i_recovery.rollback primitive Program.confirm_rollback
    # routes to, with the mediation token minted directly as
    # the repo's own rollback suites do (p0r1_persist_test).
    # The operator-named state files carry no RUN uuid, so this
    # section snapshots them and restores them exactly (the
    # E-series arrangement).
    from form.mandell.core_i_recovery import checkpoint as _ckpt
    from form.mandell.core_i_recovery import rollback as _rollback
    from form import persist_rest as _persist_rest
    from form.persist import stored_program_owner as _stored_prog_owner
    r_snapshot = {}
    for f in glob.glob(os.path.join(_STATE_DIR, "*operator*")):
        if os.path.isfile(f):
            with open(f, "rb") as fh:
                r_snapshot[f] = fh.read()
    try:
        r_path = owner_nursery_path("")
        rp = open_program("")
        r_prop = rp.nursery.add("rollback identity idea",
                                "first words", detail="rb detail")
        rp.nursery.conflict_dispositions["rb-conflict-1"] = {
            "disposition": "prefer", "preferred_ids": [r_prop.id],
            "note": "rb-owner-scoped-record"}
        rp.nursery.save()
        g1 = _ckpt(rp, stamp="f7rb1")
        rp.nursery.add("post checkpoint idea", "second words")
        _ckpt(rp, stamp="f7rb2")
        check("R1.rollback_premise_identity_bound",
              stored_nursery_owner(r_path) == ""
              and stored_nursery_owner(r_path) is not None
              and _stored_prog_owner(_path("")) == "",
              f"nursery_owner={stored_nursery_owner(r_path)!r} "
              f"program_owner={_stored_prog_owner(_path(''))!r}")
        restored = None
        rb_error = ""
        try:
            restored = _rollback(
                "", g1,
                _mediation={"operation": "checkpoint.rollback",
                            "owner": "", "generation_id": g1})
        except Exception as exc:
            rb_error = f"{type(exc).__name__}: {exc}"
        check("R2.rollback_completes_for_empty_owner",
              restored is not None, rb_error)
        check("R3.identity_survives_rollback",
              stored_nursery_owner(r_path) == ""
              and stored_nursery_owner(r_path) is not None,
              f"stored={stored_nursery_owner(r_path)!r}")
        r_labels = (sorted(x.label for x in
                           restored.nursery.proposals.values())
                    if restored is not None else [])
        check("R4.rollback_state_and_records_survive",
              restored is not None
              and r_labels == ["rollback identity idea"]
              and "rb-conflict-1" in restored.nursery.conflict_dispositions,
              f"labels={r_labels}")
        try:
            Nursery.load(r_path, owner="operator")
            r5_refused = False
        except Exception:
            r5_refused = True
        check("R5.colliding_named_load_refuses", r5_refused,
              "owner='operator' vs the ''-bound file")
        try:
            rn = Nursery.load(r_path, owner="")
            rp2 = _persist_rest.load("", activate=False)
            r6 = (rn.owner == ""
                  and "rb-conflict-1" in rn.conflict_dispositions
                  and rp2 is not None and rp2.owner == "")
        except Exception:
            r6 = False
        check("R6.empty_owner_reload_agrees", r6,
              "Nursery.load + persist_rest.load both resolve ''")
    finally:
        for f in glob.glob(os.path.join(_STATE_DIR, "*operator*")):
            try:
                if f in r_snapshot:
                    with open(f, "wb") as fh:
                        fh.write(r_snapshot[f])
                elif os.path.isfile(f):
                    os.unlink(f)
            except OSError as e:
                _CLEANUP_ERRORS.append(f"{f}: {e}")

    cleanup()
    check("Z.cleanup_complete", not _CLEANUP_ERRORS,
          "; ".join(_CLEANUP_ERRORS))

    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"critic_owner_collision_fixture: "
          f"{len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        print("FAILURES:", ", ".join(failed))
    return 1 if failed else 0


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
