#!/usr/bin/env python3
"""Part VI — Unknowns: current-main probe battery.

One read-only probe section per open question family, run at the
Part VI base pin (af2519b6). Every section either DISCHARGES the
Uni-owed evidence for its question or NARROWS the question to the
exact decision that remains. No production code is changed; all
Program work uses uuid owners in the clone's state dir with
exact-owner cleanup (a cleanup failure fails the suite).

Sections:
  119  Q-35.1 / row #119 — sweep_stale_tmps caller census (AST,
       form/**/*.py): production call sites, test call sites.
  175  Q-SNAP.3 / row #175 — entry-point SIGINT-disposition
       census + the inherited-SIG_IGN mechanism reproduced in
       this environment (background child vs foreground child).
  R21  DD-54 question — Core II caps behavioral verification:
       SNAPSHOTS_CAP 64 / TRACES_CAP 512 with counted evictions.
  42   Q-DD42.2 — While/Until unparseable-infix behavior at
       current main (three drives: While-infix, Until-infix,
       While-prefix control).
  18   Q-DD18.2 — refused Pulse inside a chain at current main:
       continuation + atom marking, observed exactly.
  QU   Q-U.3 / Q-U.4 / Q-U.5 (GS-4 residual) — confirm-placement
       behavior at current main: same-wall inheritance,
       mixed-wall manual choice, auto-confirm sweep treatment.
  GS1  Q-GS.1 — growth-entry production caller census (evidence
       enumeration for the default-flip blast radius).

Labels: UNIT (censuses, Core II) + PUBLIC_ENTRY_PATH
(execute_seed / Program doors) + CROSS_PROCESS (signal
inheritance micro-probe).
"""
from __future__ import annotations

import ast
import glob
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
OWNERS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _cleanup(owner):
    state = os.path.join(REPO, "form", "state")
    for f in glob.glob(os.path.join(state, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            _CLEANUP_ERRORS.append(f"{f}: {e}")


def _owner(tag):
    o = f"P6{tag}{RUN}"
    OWNERS.append(o)
    _cleanup(o)
    return o


def _ast_callers(func_name, defining_rel):
    prod, test = [], []
    for path in sorted(Path(REPO, "form").rglob("*.py")):
        rel = str(path.relative_to(REPO))
        if rel == defining_rel:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                f = node.func
                if (isinstance(f, ast.Name) and f.id == func_name) or (
                        isinstance(f, ast.Attribute)
                        and f.attr == func_name):
                    (test if path.name.endswith("_test.py")
                     else prod).append(rel)
                    break
    return prod, test


# ---------------------------------------------------------------- 119
def section_119():
    print("--- 119 / Q-35.1: sweep_stale_tmps caller census ---")
    prod, test = _ast_callers("sweep_stale_tmps",
                              "form/dell_matrix/atomic_write.py")
    print(f"  production callers: {prod}")
    print(f"  test callers: {test}")
    check("119_no_production_caller", prod == [],
          f"prod={prod}")
    check("119_test_callers_exist", len(test) >= 1,
          f"test={test}")


# ---------------------------------------------------------------- 175
def section_175():
    print("--- 175 / Q-SNAP.3: SIGINT disposition census + mechanism ---")
    entries = []
    for path in sorted(Path(REPO, "form").rglob("*.py")):
        if path.name.endswith("_test.py"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if '__name__ == "__main__"' in text or \
                '__name__ == \'__main__\'' in text:
            hardens = ("signal.signal" in text and "SIGINT" in text)
            entries.append((str(path.relative_to(REPO)), hardens))
    for rel in ("form/repl.py", "form/regress.py"):
        if rel not in [e[0] for e in entries]:
            text = Path(REPO, rel).read_text(encoding="utf-8")
            entries.append(
                (rel, "signal.signal" in text and "SIGINT" in text))
    print("  entry-point census (module, installs SIGINT handling):")
    for rel, h in entries:
        print(f"    {rel}: {h}")
    check("175_census_enumerated", len(entries) >= 5,
          f"{len(entries)} entry modules")
    hardened = [r for r, h in entries if h]
    check("175_hardened_set_measured", True,
          f"hardened={hardened} (the measured set IS the evidence)")

    probe = ("import signal; "
             "print(int(signal.getsignal(signal.SIGINT) == "
             "signal.SIG_IGN))")
    bg = subprocess.run(
        ["bash", "-c", f"python3 -c '{probe}' & wait"],
        capture_output=True, text=True, timeout=60)
    fg = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True, text=True, timeout=60)
    check("175_background_child_inherits_sig_ign",
          bg.stdout.strip().endswith("1"),
          f"bg stdout={bg.stdout.strip()!r}")
    check("175_foreground_child_default",
          fg.stdout.strip().endswith("0"),
          f"fg stdout={fg.stdout.strip()!r}")


# ---------------------------------------------------------------- R21
def section_r21():
    print("--- R21 / DD-54: Core II caps at current main ---")
    from form.mandell.core_ii_exec import (
        CoreIIState, append_snapshot, _trim_oldest,
        SNAPSHOTS_CAP, TRACES_CAP)
    st = CoreIIState()
    for _ in range(SNAPSHOTS_CAP + 1):
        append_snapshot(st)
    check("R21_snapshots_cap_64_counted",
          len(st.snapshots) == 64
          and st.snapshots_dropped_total == 1,
          f"kept={len(st.snapshots)} "
          f"dropped={st.snapshots_dropped_total}")
    st2 = CoreIIState()
    st2.traces.extend(f"t{i}" for i in range(TRACES_CAP + 1))
    dropped = _trim_oldest(st2.traces, TRACES_CAP)
    check("R21_traces_cap_512_counted",
          len(st2.traces) == 512 and dropped == 1,
          f"kept={len(st2.traces)} dropped={dropped}")


# ------------------------------------------------------------- drives
def _program(tag):
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    p = Program(owner=_owner(tag))
    attach(p)
    return p


def _run(p, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(p, seed)


def _msgs(r):
    return [m for m in r.get("messages", [])
            if not m.startswith(("Mandell:", "English:"))]


# ---------------------------------------------------------------- 42
def section_42():
    print("--- Q-DD42.2: While/Until infix at current main ---")
    p = _program("DD42")
    _run(p, "55[Set] :: level=5")

    r = _run(p, "65[While] :: level lt 99 > 55[Set] :: tick=1 "
                "> 61[Join]")
    atoms = {a["dell"]: a for a in r.get("atom_results", [])}
    check("42_while_infix_silently_false",
          r.get("ok") is True and r.get("error") == ""
          and atoms.get(65, {}).get("ok") is True
          and atoms.get(55, {}).get("skipped") is True,
          "infix 'level lt 99' (true if parsed) read as already-"
          "false: zero iterations, head ok=True, NO error, NO "
          "refusal receipt")

    r = _run(p, "64[Until] :: level gt 99 > 55[Set] :: tick=1 "
                "> 61[Join]")
    atoms = {a["dell"]: a for a in r.get("atom_results", [])}
    check("42_until_infix_bound_refusal_misattributed",
          atoms.get(64, {}).get("error") == "bound_unspecified",
          "Until+infix refuses on the BOUND (DD-44), never on the "
          "unparseable condition — cause misattributed")

    r = _run(p, "65[While] :: gt:level 3 > 55[Set] :: tick=1 "
                "> 61[Join]")
    atoms = {a["dell"]: a for a in r.get("atom_results", [])}
    check("42_while_prefix_control_honest_refusal",
          atoms.get(65, {}).get("error") == "bound_unspecified"
          and any("nothing ran" in m for m in _msgs(r)),
          "prefix-true control: honest bound_unspecified refusal "
          "with receipt (DD-44 contract intact)")


# ---------------------------------------------------------------- 18
def section_18():
    print("--- Q-DD18.2: refused Pulse in a chain at current main ---")
    p = _program("DD18")
    r = _run(p, "25[Pulse] > 55[Set] :: after_pulse=yes > 61[Join]")
    atoms = {a["dell"]: a for a in r.get("atom_results", [])}
    msgs = _msgs(r)
    check("18_chain_continues_after_refused_pulse",
          any("Set after_pulse=yes" in m for m in msgs)
          and atoms.get(61, {}).get("ok") is True,
          "the Set atom EXECUTED after the refused Pulse; Join ran")
    check("18_pulse_atom_marked_not_ok",
          atoms.get(25, {}).get("ok") is False
          and any("Pulse NOT sent (enhance OFF)." in m for m in msgs)
          and r.get("ok") is False,
          "pulse atom ok=False with honest receipt; chain result "
          "ok=False (continuation is NOT silent success)")


# ---------------------------------------------------------------- QU
_FIELD = [
    ("in_a", "harbor lantern inkeep",
     "harbor lantern craft timber copper kettle song inkeep cellar "
     "vault"),
    ("in_b", "harbor lantern inforge",
     "harbor lantern craft timber copper kettle song inforge cellar "
     "vault"),
    ("out_a", "harbor lantern outkeep",
     "harbor lantern craft timber copper kettle song outkeep cellar "
     "vault axolotl azurite"),
    ("out_b", "harbor copper outdrift",
     "harbor lantern craft copper song outdrift axolotl azurite "
     "basalt"),
    ("out_c", "glacier tundra outpost",
     "glacier tundra obsidian wolf outpost fjord"),
]


def _field(tag, box_first):
    from form.open import open_program
    p = open_program(_owner(tag))
    plane = p.cube.session.plane
    plane.units.clear()
    plane.sandboxes.clear()
    p.nursery.proposals.clear()
    for uid, label, words in _FIELD:
        p.place(uid, label, words=words, x=0.0, y=0.0)
    if box_first:
        plane.box(["in_a", "in_b"], "vault1", label="vault")
    return p, plane


def _members(plane, box="vault1"):
    sb = plane.sandboxes.get(box)
    if sb is None:
        return []
    if isinstance(sb, dict):
        return list(sb.get("member_ids") or [])
    return list(getattr(sb, "member_ids", []) or [])


def section_qu():
    print("--- Q-U.3/.4/.5: confirm placement at current main ---")
    # Q-U.3: same-wall parents, no placement named -> inherited wall
    p, plane = _field("QU3", box_first=True)
    p.grow_ideas(1)
    pid = [k for k, pr in p.nursery.proposals.items()
           if set(pr.parents or []) == {"in_a", "in_b"}][0]
    r = p.confirm_proposal(
        pid, _producer="repl_user",
        _review_context=p.make_review_context(pid, "repl_user"))
    check("QU3_same_wall_inherits",
          r.get("ok") is True
          and (r.get("placement") or {}).get("mode")
          == "inherited_wall"
          and pid in _members(plane),
          f"placement={r.get('placement')} members={_members(plane)}")

    # Q-U.4: mixed-wall parents, no placement -> choice required
    p, plane = _field("QU4", box_first=False)
    p.grow_ideas(1)
    mixed = [k for k, pr in p.nursery.proposals.items()
             if any(x in ("in_a", "in_b") for x in (pr.parents or []))
             and any(x.startswith("out") for x in (pr.parents or []))]
    plane.box(["in_a", "in_b"], "vault1", label="vault")
    pid = mixed[0]
    r = p.confirm_proposal(
        pid, _producer="repl_user",
        _review_context=p.make_review_context(pid, "repl_user"))
    refused = r.get("ok") is False and \
        r.get("reason") == "placement_choice_required"
    r2 = p.confirm_proposal(
        pid, _producer="repl_user",
        _review_context=p.make_review_context(pid, "repl_user"),
        _placement="outside")
    check("QU4_mixed_wall_choice_required_then_honored",
          refused and r2.get("ok") is True
          and (r2.get("placement") or {}).get("mode")
          == "manual_choice",
          f"no-placement reason={r.get('reason')}; "
          f"with choice: ok={r2.get('ok')} "
          f"placement={r2.get('placement')}")

    # Q-U.5: auto-confirm sweep over the same mixed field
    p, plane = _field("QU5", box_first=False)
    p.grow_ideas(1)
    plane.box(["in_a", "in_b"], "vault1", label="vault")
    p.set_auto_confirm_grow(True)
    res = p.grow_ideas(1)
    ac = res.get("auto_confirm") or {}
    boxed_offspring_in = [u for u in _members(plane)
                          if u not in ("in_a", "in_b")]
    check("QU5_sweep_skips_mixed_confirms_same_wall_in",
          ac.get("skipped_noneligible", 0) >= 1
          and ac.get("confirmed", 0) >= 1
          and len(boxed_offspring_in) >= 1,
          f"auto_confirm={ac}; vault members={_members(plane)}")


# ---------------------------------------------------------------- GS1
def section_gs1():
    print("--- Q-GS.1: growth-entry production caller census ---")
    prod, test = _ast_callers("grow_ideas", "form/open.py")
    print(f"  grow_ideas production callers: {prod}")
    print(f"  grow_ideas test callers: {len(test)} files")
    check("GS1_census_measured", len(prod) >= 1,
          f"prod_callers={prod} (the enumeration IS the blast-"
          f"radius evidence for the Q-GS.1 default ruling)")


def main() -> int:
    print("=== PART VI UNKNOWNS PROBE BATTERY (base af2519b6) ===")
    section_119()
    section_175()
    section_r21()
    section_42()
    section_18()
    section_qu()
    section_gs1()
    for o in OWNERS:
        _cleanup(o)
    check("ZZ_cleanup_clean", not _CLEANUP_ERRORS,
          f"errors={_CLEANUP_ERRORS}")
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"PART6_UNKNOWNS_PROBE {passed}/{len(RESULTS)}")
    return 0 if passed == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
