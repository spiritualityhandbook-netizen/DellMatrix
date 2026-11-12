#!/usr/bin/env python3
"""C7.Schema — DD-29 baseline (MWL 148): Dell 39 [Schema] as the
Matrix's read-only nervous-system board.

Contract (plan §12.28 DD-29 + §14.3 C7 card acceptance):
- 39[Schema] reports every needed subsystem with three checks
  each — EXISTS / CONNECTED (a live read-only probe of the organ's
  own status provider, never mere attribute presence) /
  AVAILABLE — plus the organ's current state line.
- The inventory is DD-29's 16 named systems, seeded from
  Program.status()'s own aggregation (floor, truths, avatar,
  companion, inspire, self_knowledge, nursery, ideas, enhance,
  lattice, keys, pulse, forces, personas, bimo, persona_matrix).
- Verdict: blanket VALID only when every organ passes; otherwise
  INVALID and the verdict block NAMES the failing organs and
  checks. OFF-by-design (enhance gate off) is healthy-by-design,
  never "down". A probe that raises reports the organ UNKNOWN
  with the error class named — never a pass, never a crash.
- Probing NEVER mutates user work: no writes, no lazy init that
  persists, no provider contact. The one sanctioned append is
  the atom's own history receipt ('39[Schema] :: valid|invalid'),
  exactly as the historical stub noted its verdict.
- The label is ignored: Schema interrogates the program, not
  the operand. Bare and labeled runs return the same board.

Adaptation note (brief test 4): the brief's presence-is-not-
connection setup used `growth`, which is not one of DD-29's 16
named systems; the same property is pinned here on an
inventoried organ (forces replaced by an inert husk).

Purity finding pinned by test 7: Program.persona_matrix_status()
writes persona_matrix.active on read (and personas_status()
nests that call), so the board reads persona_matrix.to_dict()
and the personas registry directly. A probe that routes through
the writing wrapper changes the digest and fails test 7.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from form.open import open_program
from form.mandell.executor import execute_seed

EXPECTED_ORGANS = [
    "floor", "truths", "avatar", "companion", "inspire",
    "self_knowledge", "nursery", "ideas", "enhance", "lattice",
    "keys", "pulse", "forces", "personas", "bimo", "persona_matrix",
]

_ORGAN_LINE = re.compile(
    r"^  · (\w+): exists=(\S+) connected=(\S+) available=(\S+) — (.*)$")


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


def _program(owner):
    _cleanup(owner)
    return open_program(owner)


def _msgs(r):
    return [m for m in r.get("messages", [])
            if not m.startswith(("Mandell:", "English:"))]


def _board(r):
    """Parse a Schema result into (verdict_line, count_line, organs)."""
    lines = _msgs(r)
    organs = {}
    for ln in lines:
        m = _ORGAN_LINE.match(ln)
        if m:
            organs[m.group(1)] = {
                "exists": m.group(2), "connected": m.group(3),
                "available": m.group(4), "state": m.group(5),
            }
    return (lines[0] if lines else "",
            lines[1] if len(lines) > 1 else "",
            organs)


def smoke() -> bool:
    print("=== C7.SCHEMA (DD-29) ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}"
              + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    # -- 1. Board, not blanket: healthy program -> full board, VALID.
    p = _program("C7SchemaT1")
    res = execute_seed(p, "39[Schema]")
    verdict, count_line, organs = _board(res)
    rec("t1_executed_ok", res.get("ok") is True, str(res.get("error")))
    rec("t1_verdict_valid", verdict == "Schema: VALID", verdict)
    rec("t1_count_line", "16 systems examined" in count_line, count_line)
    rec("t1_all_organs_named", sorted(organs) == sorted(EXPECTED_ORGANS),
        f"got {sorted(organs)}")
    rec("t1_all_checks_pass",
        all(o["exists"] == "YES" and o["connected"] == "YES"
            and o["available"] in ("YES", "OFF-by-design")
            for o in organs.values()),
        str({k: v for k, v in organs.items()
             if not (v["exists"] == "YES" and v["connected"] == "YES"
                     and v["available"] in ("YES", "OFF-by-design"))}))
    rec("t1_state_lines_present",
        all(o["state"] for o in organs.values()),
        str([k for k, v in organs.items() if not v["state"]]))
    detail = res.get("schema_board") or {}
    rec("t1_structured_detail",
        detail.get("verdict") == "VALID"
        and detail.get("examined") == 16
        and len(detail.get("organs") or []) == 16
        and all({"name", "exists", "connected", "available", "state"}
                <= set(o) for o in detail.get("organs") or []),
        str(detail)[:200])

    # -- 2. Label changes nothing: the mixtape is not "validated".
    pa = _program("C7SchemaT2A")
    pb = _program("C7SchemaT2B")
    ra = execute_seed(pa, "39[Schema]")
    rb = execute_seed(pb, "39[Schema]:: validate my mixtape")
    rec("t2_label_ignored_board_identical", _msgs(ra) == _msgs(rb),
        f"bare={_msgs(ra)[:2]} labeled={_msgs(rb)[:2]}")

    # -- 3. Deleted organ named: forces removed -> exists=NO, INVALID.
    p = _program("C7SchemaT3")
    del p.forces
    res = execute_seed(p, "39[Schema]")
    verdict, count_line, organs = _board(res)
    rec("t3_verdict_invalid", verdict == "Schema: INVALID", verdict)
    rec("t3_forces_exists_no",
        (organs.get("forces") or {}).get("exists") == "NO",
        str(organs.get("forces")))
    rec("t3_verdict_names_forces", "forces" in count_line, count_line)
    rec("t3_board_complete_despite_hole", len(organs) == 16,
        f"{len(organs)} organ lines")

    # -- 4. Presence is not connection: inert husk is not health.
    p = _program("C7SchemaT4")
    p.forces = object()  # present for hasattr, incapable of reporting
    res = execute_seed(p, "39[Schema]")
    verdict, count_line, organs = _board(res)
    f4 = organs.get("forces") or {}
    rec("t4_husk_exists_but_not_connected",
        f4.get("exists") == "YES" and f4.get("connected") != "YES",
        str(f4))
    rec("t4_verdict_invalid_and_names",
        verdict == "Schema: INVALID" and "forces" in count_line,
        f"{verdict} | {count_line}")

    # -- 5. OFF-by-design is not down: enhance off by default.
    p = _program("C7SchemaT5")
    res = execute_seed(p, "39[Schema]")
    verdict, _cl, organs = _board(res)
    e5 = organs.get("enhance") or {}
    rec("t5_enhance_off_by_design",
        e5.get("available") == "OFF-by-design", str(e5))
    rec("t5_verdict_still_valid", verdict == "Schema: VALID", verdict)

    # -- 6. Raising organ isolated: UNKNOWN with the error named.
    class _Bomb:
        def status(self):
            raise RuntimeError("c7 bomb")

    p = _program("C7SchemaT6")
    p.lattice = _Bomb()
    try:
        res = execute_seed(p, "39[Schema]")
        raised = ""
    except Exception as e:  # Schema itself must not raise
        res, raised = {}, f"{type(e).__name__}: {e}"
    verdict, count_line, organs = _board(res)
    l6 = organs.get("lattice") or {}
    rec("t6_schema_does_not_raise", not raised, raised)
    rec("t6_organ_unknown_error_named",
        l6.get("connected") == "UNKNOWN" and "RuntimeError" in l6.get("state", ""),
        str(l6))
    rec("t6_other_organs_still_reported",
        len(organs) == 16 and verdict == "Schema: INVALID",
        f"{len(organs)} lines, {verdict}")

    # -- 7. Read-only proof: digest identical around a Schema run
    #       (the atom's own history receipt is the one sanctioned
    #       append, exactly the historical note).
    p = _program("C7SchemaT7")
    execute_seed(p, "50[Manifest] :: c7_keepsake")
    execute_seed(p, "37[Nurture] :: C7 Read Only Rose")
    p.persona_lens = "manny"  # persona_matrix.active stays None:
    # any probe routing through persona_matrix_status() flips it.

    def digest(prog):
        return {
            "units": sorted((u, getattr(x, "label", ""))
                            for u, x in prog.cube.session.plane.units.items()),
            "nursery": prog.nursery.summary(),
            "history": list(prog.history),
            "enhance": (prog.enhance.on, prog.enhance.level,
                        prog.enhance.session_pulses,
                        dict(prog.enhance.state.scores)),
            "pm_active": prog.persona_matrix.active,
            "lens": prog.persona_lens,
            "sprite": (prog.inspire.sprite.frame, prog.inspire.sprite.tick,
                       len(prog.inspire.scores.samples)),
            "forces": (prog.forces.time.tick, prog.forces.breath.cycle,
                       prog.forces.weather.condition),
            "keys": len(prog.keys.keys),
            "lattice": (len(prog.lattice.cells), prog.lattice.size),
            "generation": prog.duo.generation,
            "bimo": (dict(prog.bimo.slots), prog.bimo.mode),
            "avatar_pos": tuple(prog.avatar.body.pos),
            "companion": (prog.companion.mode, prog.companion.doing),
            "selfk": (prog.self_knowledge.probes, prog.self_knowledge.hits),
            "embed_binding": getattr(prog, "embed_binding", None),
        }

    before = digest(p)
    res = execute_seed(p, "39[Schema]")
    after = digest(p)
    hist_ok = after.pop("history") == before.pop("history") + ["39[Schema] :: valid"]
    rec("t7_digest_identical", after == before,
        str({k: (before[k], after[k]) for k in before
             if before[k] != after[k]})[:300])
    rec("t7_only_sanctioned_history_append", hist_ok,
        f"history tail {list(p.history)[-2:]}")
    rec("t7_no_provider_contact",
        getattr(p, "embed_binding", None) is None)

    # -- 8. No silent skips: printed set == declared inventory,
    #       and a vanished organ still appears on the board.
    p = _program("C7SchemaT8")
    del p.keys
    res = execute_seed(p, "39[Schema]")
    _v, count_line, organs = _board(res)
    rec("t8_printed_set_is_inventory",
        sorted(organs) == sorted(EXPECTED_ORGANS)
        and "16 systems examined" in count_line,
        f"{sorted(organs)} | {count_line}")
    rec("t8_vanished_organ_still_listed",
        (organs.get("keys") or {}).get("exists") == "NO",
        str(organs.get("keys")))

    # -- 9. Neighbours hold: Dell 12, Program.status(), the
    #       history receipt, and repeat bare calls.
    p = _program("C7SchemaT9")
    t_before = _msgs(execute_seed(p, "12[Test]"))
    execute_seed(p, "39[Schema]")
    t_after = _msgs(execute_seed(p, "12[Test]"))
    rec("t9_dell12_unchanged",
        t_before == t_after and t_before
        and re.match(r"Test: \d/5", t_before[-1]) is not None,
        f"{t_before[:1]} vs {t_after[:1]}")
    st = p.status()
    rec("t9_status_authority_unchanged",
        all(k in st for k in EXPECTED_ORGANS) and "owner" in st
        and len(st) == 32,  # status()'s key count at this SHA
        f"{len(st)} keys")
    rec("t9_history_receipt_preserved",
        "39[Schema] :: valid" in list(p.history), str(list(p.history)[-3:]))
    r9a = execute_seed(p, "39[Schema]")
    r9b = execute_seed(p, "39[Schema]")
    rec("t9_repeat_bare_calls_ok",
        r9a.get("ok") is True and r9b.get("ok") is True)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
