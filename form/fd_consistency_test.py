#!/usr/bin/env python3
"""F-d consistency repair suite (failing-first origin: Boundary F-d
consistency audit, director-reports/FD_CONSISTENCY_AUDIT_2026-11-13.md,
published as PR #409; build authorized by Ace's build-all order,
2026-11-13 11:02 CST).

Canonical rule (Director F-d ruling, GS-4): the wall key is the pair
(sandboxed, sandbox_id):

- sandboxed=False + stale non-empty sandbox_id -> UNBOXED (the id is
  inert; the unit is a wall-mate of genuinely unboxed units).
- sandboxed=True + missing/invalid sandbox_id -> MALFORMED,
  fail-closed: refused, never silently collapsed to unboxed. Growth
  extends the malformed definition to claims unverifiable against
  the Plane's box records (no such Sandbox record, or the unit
  absent from the record's member_ids) —
  form/dell_matrix/ringed_growth.py _malformed_boxed, the GS-4
  house authority this repair reuses (no second definition).

The audit found exactly three inconsistent consumers (resonance a
fourth, by inheritance from enhance_scope):

1. Plane.enhance_scope silently treated a malformed unit as unboxed
   (the unit received a full unboxed scope while
   unit_containment._malformed_sandbox(unit) was True).
2. Plane.render crashed with TypeError on a zoomed malformed unit.
3. REPL group membership read sandbox_id ALONE — misfiring even on
   the F-d stale state itself (flag-False + stale id equal to a
   group's id was told "already in group" although canonically
   unboxed and absent from member_ids).

This suite converts the audit's three failing-first sketches into
checks, adds the F-d stale-state control at every repaired site
(the stale state must still read UNBOXED everywhere — the unanimous
F-d ruling the repair must not regress), pins the resonance
inheritance verdict at the pulse (the malformed unit must not send
resonance as an unboxed unit; the source refusal propagates), and
keeps genuine-member group controls green.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from form.dell_matrix.plane import Plane

try:
    from form.dell_matrix.plane import MalformedSandboxClaim
except ImportError:  # BEFORE code: the refusal type does not exist yet
    MalformedSandboxClaim = None

OWNER_TAG = "FDCONSIST1113"


def _cleanup(owner):
    import glob
    import shutil
    state = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
    for f in glob.glob(os.path.join(state, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            raise RuntimeError(f"cleanup failed for {f}: {e}")


def _field_plane():
    """free1/free2 unboxed; bad malformed (True, None); stale in the
    F-d state (False, stale id); m1/m2 genuinely boxed in vault1;
    claim (True, 'vault1') but absent from vault1.member_ids."""
    plane = Plane()
    plane.place("free1", "free one", words="alpha birch")
    plane.place("free2", "free two", words="alpha cedar")
    plane.place("bad", "bad claim", words="alpha durian")
    bad = plane.units["bad"]
    bad.sandboxed = True
    bad.sandbox_id = None
    plane.place("stale", "stale id", words="alpha elder")
    stale = plane.units["stale"]
    stale.sandboxed = False
    stale.sandbox_id = "ghost_box"
    plane.place("m1", "member one", words="alpha fig")
    plane.place("m2", "member two", words="alpha grape")
    plane.box(["m1", "m2"], "vault1", label="vault")
    plane.place("claim", "membership claim", words="alpha holly")
    claim = plane.units["claim"]
    claim.sandboxed = True
    claim.sandbox_id = "vault1"  # record exists; claim not in member_ids
    return plane


def _refusal_of(fn):
    """Run fn(); return (exception_or_None, result_or_None)."""
    try:
        return None, fn()
    except Exception as e:  # noqa: BLE001 - the check inspects the type
        return e, None


def _is_malformed_refusal(exc) -> bool:
    return (MalformedSandboxClaim is not None
            and isinstance(exc, MalformedSandboxClaim))


def smoke() -> bool:
    print("=== F-D CONSISTENCY REPAIR ===")
    fails = []
    total = 0

    def check(name, ok, detail):
        nonlocal total
        total += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} :: {detail}")
        if not ok:
            fails.append(name)

    # --- SITE 1: Plane.enhance_scope (audit sketch 1) ----------------
    plane = _field_plane()

    exc, scope = _refusal_of(lambda: plane.enhance_scope("bad"))
    check("s1_malformed_refused",
          _is_malformed_refusal(exc) and "bad" in str(exc),
          f"exc={type(exc).__name__ if exc else None} scope={scope}")

    scope_free1 = plane.enhance_scope("free1")
    check("s1_malformed_excluded_as_peer",
          "bad" not in scope_free1 and "free2" in scope_free1,
          f"scope(free1)={scope_free1}")

    scope_stale = plane.enhance_scope("stale")
    check("s1_stale_reads_unboxed",
          set(scope_stale) == {"free1", "free2"},
          f"scope(stale)={scope_stale} (F-d stale state = UNBOXED)")

    check("s1_genuine_box_scope_intact",
          plane.enhance_scope("m1") == ["m2"],
          f"scope(m1)={plane.enhance_scope('m1')}")

    exc, scope = _refusal_of(lambda: plane.enhance_scope("claim"))
    check("s1_membership_inconsistent_refused",
          _is_malformed_refusal(exc),
          f"exc={type(exc).__name__ if exc else None} scope={scope} "
          "(GS-4 _malformed_boxed extension, as growth applies it)")

    # --- SITE 1b: resonance inheritance (audit consumer #5) ---------
    from form.dell_matrix.resonance import ResonanceState, pulse
    rplane = Plane()
    rplane.place("free1", "free one", words="alpha birch")
    rplane.place("free2", "free two", words="alpha cedar")
    rplane.place("bad", "bad claim", words="alpha durian")
    rbad = rplane.units["bad"]
    rbad.sandboxed = True
    rbad.sandbox_id = None
    state = ResonanceState()
    exc, _ = _refusal_of(lambda: pulse(rplane, state))
    spread = {uid: state.scores.get(uid, 0.0) for uid in ("free1", "free2")}
    check("s1r_pulse_refusal_propagates_no_silent_spread",
          _is_malformed_refusal(exc),
          f"exc={type(exc).__name__ if exc else None} "
          f"scores_after={spread} (BEFORE: pulse returned normally and "
          "the malformed unit sent resonance as an unboxed unit)")

    # --- SITE 2: Plane.render (audit sketch 2) -----------------------
    plane2 = _field_plane()
    plane2.zoom_in("bad")
    exc, rendered = _refusal_of(lambda: plane2.render())
    state_lines = [ln for ln in (rendered or "").split("\n")
                   if "state:" in ln]
    check("s2_malformed_render_honest_refusal_no_crash",
          exc is None and isinstance(rendered, str)
          and any("UNVERIFIABLE" in ln or "REFUSED" in ln
                  for ln in state_lines)
          and "SANDBOX None" not in (rendered or ""),
          f"exc={type(exc).__name__ if exc else None} "
          f"state_lines={state_lines}")

    plane2.zoom_in("stale")
    rendered_stale = plane2.render()
    check("s2_stale_render_connected",
          "state: CONNECTED" in rendered_stale,
          "F-d stale state renders CONNECTED (unanimous F-d ruling)")

    plane2.zoom_in("m1")
    rendered_m1 = plane2.render()
    check("s2_genuine_box_render_intact",
          "state: SANDBOX vault1" in rendered_m1,
          "genuine member renders its box")

    # --- SITE 3: REPL group membership (audit sketch 3) --------------
    from form.open import open_program
    from form.repl import _handle_group_command, capture_output

    def build_program(tag):
        owner = f"{OWNER_TAG}{tag}"
        _cleanup(owner)
        p = open_program(owner)
        pl = p.cube.session.plane
        pl.units.clear()
        pl.sandboxes.clear()
        p.nursery.proposals.clear()
        _, msg = capture_output(
            lambda: _handle_group_command(
                p, "group create fdvault", "group create fdvault"))
        assert "Group created" in msg, msg
        return p, pl, pl.sandboxes["project_fdvault"]

    def group_cmd(p, line):
        _, msg = capture_output(
            lambda: _handle_group_command(p, line.lower(), line))
        return msg

    # F-d stale state: flag-False + stale id == group id, not a member.
    p, pl, sb = build_program("A")
    p.place("u_stale", "stale unit", words="alpha birch")
    u = pl.units["u_stale"]
    u.sandboxed = False
    u.sandbox_id = sb.id
    msg = group_cmd(p, "group add u_stale to fdvault")
    check("s3_stale_add_proceeds_and_boxes",
          "Added" in msg and pl.units["u_stale"].sandboxed
          and "u_stale" in sb.member_ids,
          f"msg={msg.strip()!r} (BEFORE: refused 'already in group')")

    p, pl, sb = build_program("B")
    p.place("u_stale", "stale unit", words="alpha birch")
    u = pl.units["u_stale"]
    u.sandboxed = False
    u.sandbox_id = sb.id
    msg = group_cmd(p, "group remove u_stale from fdvault")
    check("s3_stale_remove_honest_not_in_group",
          "is not in group" in msg
          and pl.units["u_stale"].sandbox_id == sb.id,
          f"msg={msg.strip()!r} (BEFORE: unboxed on a false premise)")

    # Malformed claim: add and remove both fail closed, state untouched.
    p, pl, sb = build_program("C")
    p.place("u_bad", "bad unit", words="alpha durian")
    u = pl.units["u_bad"]
    u.sandboxed = True
    u.sandbox_id = None
    msg = group_cmd(p, "group add u_bad to fdvault")
    check("s3_malformed_add_refused",
          ("malformed" in msg.lower() or "cannot be verified" in msg.lower()
           or "refus" in msg.lower())
          and pl.units["u_bad"].sandbox_id is None
          and "u_bad" not in sb.member_ids,
          f"msg={msg.strip()!r} (BEFORE: silently boxed the unit)")
    msg = group_cmd(p, "group remove u_bad from fdvault")
    check("s3_malformed_remove_refused",
          ("malformed" in msg.lower() or "cannot be verified" in msg.lower()
           or "refus" in msg.lower())
          and pl.units["u_bad"].sandboxed
          and pl.units["u_bad"].sandbox_id is None,
          f"msg={msg.strip()!r} (BEFORE: answered 'not in group', "
          "concealing the malformed claim)")

    # Genuine member controls: add, duplicate-add refusal, remove.
    p, pl, sb = build_program("D")
    p.place("u_free", "free unit", words="alpha cedar")
    msg1 = group_cmd(p, "group add u_free to fdvault")
    msg2 = group_cmd(p, "group add u_free to fdvault")
    msg3 = group_cmd(p, "group remove u_free from fdvault")
    u = pl.units["u_free"]
    check("s3_genuine_member_controls",
          "Added" in msg1 and "already in group" in msg2
          and "Removed" in msg3 and not u.sandboxed
          and u.sandbox_id is None and "u_free" not in sb.member_ids,
          f"add={msg1.strip()!r} dup={msg2.strip()!r} "
          f"remove={msg3.strip()!r}")

    passed = total - len(fails)
    print(f"FD CONSISTENCY: {passed}/{total} checks passed"
          + (f" — FAILING: {fails}" if fails else ""))
    return not fails


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
