#!/usr/bin/env python3
"""C7.Schema board — Dell 39's read-only nervous system (DD-29).

The board reports every needed subsystem of a live Program with
three checks each — EXISTS / CONNECTED / AVAILABLE — plus the
organ's own state line:

- EXISTS: the organ is present (for attribute organs, the
  attribute status() itself guards on; for the global providers
  — floor, truths, pulse — the provider is importable).
- CONNECTED: a live READ-ONLY probe of the organ's own status
  provider returns a well-formed report (the anchor keys its
  status() contract guarantees). Mere attribute presence is
  never connection. A probe that raises reports UNKNOWN with
  the error class named; a malformed report reports NO.
- AVAILABLE: the organ can do its work now, read from its own
  report. A designed-off organ (the enhance gate) reports
  OFF-by-design — healthy, never "down". A report carrying an
  explicit error marker reports DEGRADED with the organ's own
  reason. Anything unprovable reports UNKNOWN, never inferred.

The inventory is DD-29's 16 named systems, seeded from
Program.status()'s own aggregation IN ITS OWN ORDER — this
module declares the list (the circuit's contract answer) but
derives no data itself: every organ's state comes from that
organ's existing status provider, the same expressions
Program.status() calls. No second status authority, registry,
or inventory is created.

Verdict: VALID only when every inventoried organ passes all
three checks (OFF-by-design counts as healthy-by-design);
otherwise INVALID, and the board's second line NAMES the
failing organs and checks. The verdict vocabulary and the
note_seed tokens ("valid" / "invalid") preserve the historical
stub's forms; the receipt '39[Schema] :: valid' still lands in
history for a healthy program.

PROBE PURITY (the C7 acceptance: testing health never mutates
user work): every provider below was audited as a pure read.
Two documented exceptions to calling status()'s exact wrapper:
Program.persona_matrix_status() WRITES persona_matrix.active
on read, and Program.personas_status() nests that call — so
the board reads persona_matrix.to_dict() directly and assembles
the personas report from the same registry reads
personas_status() uses (get_persona / PERSONAS /
list_categories) minus the writing sub-reports, which are
separate organs on this board anyway. If a future provider is
found to mutate on read, its organ's connected check falls
back to UNKNOWN with the reason recorded — purity first.

Per-organ isolation: each organ is probed inside its own
try/except. One organ's failure can neither crash the board
nor be swallowed into a pass.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

YES = "YES"
NO = "NO"
UNKNOWN = "UNKNOWN"
OFF_BY_DESIGN = "OFF-by-design"
DEGRADED = "DEGRADED"

# DD-29's 16 named systems, in Program.status()'s aggregation
# order (§12.28's seed list; ideas is status()'s plane count).
INVENTORY: Tuple[str, ...] = (
    "floor", "truths", "avatar", "companion", "inspire",
    "self_knowledge", "nursery", "ideas", "enhance", "lattice",
    "keys", "pulse", "forces", "personas", "bimo",
    "persona_matrix",
)


# ------------------------------------------------------------------
# Organ probes — each returns the organ's own status report,
# using the same expression Program.status() uses (see the
# module docstring for the two purity-driven deviations).
# ------------------------------------------------------------------

def _probe_floor(program: Any) -> Dict[str, Any]:
    from form.mandell.floor import floor_status
    return floor_status()


def _probe_truths(program: Any) -> Dict[str, Any]:
    from form.mandell.harmonic_truths import status as truths_status
    return truths_status()


def _probe_avatar(program: Any) -> Dict[str, Any]:
    return program.avatar_status()


def _probe_companion(program: Any) -> Dict[str, Any]:
    return program.companion.to_dict()


def _probe_inspire(program: Any) -> Dict[str, Any]:
    return program.inspire_status()


def _probe_self_knowledge(program: Any) -> Dict[str, Any]:
    return program.self_knowledge.to_dict()


def _probe_nursery(program: Any) -> Dict[str, Any]:
    return program.nursery.summary()


def _probe_ideas(program: Any) -> Dict[str, Any]:
    return {"units": len(program.cube.session.plane.units)}


def _probe_enhance(program: Any) -> Dict[str, Any]:
    return program.enhance.status()


def _probe_lattice(program: Any) -> Dict[str, Any]:
    return program.lattice.status()


def _probe_keys(program: Any) -> Dict[str, Any]:
    return program.keys.status()


def _probe_pulse(program: Any) -> Dict[str, Any]:
    from form.dell_matrix.harmonic_core import pulse_status
    return pulse_status()


def _probe_forces(program: Any) -> Dict[str, Any]:
    return program.forces.status()


def _probe_personas(program: Any) -> Dict[str, Any]:
    # personas_status() itself is NOT called: it nests
    # persona_matrix_status(), which writes on read (see the
    # module docstring). These are the same registry reads
    # personas_status() assembles, minus the writing parts.
    from form.dell_matrix.personas import (
        PERSONAS, get_persona, list_categories)
    lens = getattr(program, "persona_lens", None)
    return {
        "active": get_persona(lens) if lens else None,
        "count": len(PERSONAS),
        "categories": list_categories(),
    }


def _probe_bimo(program: Any) -> Dict[str, Any]:
    return program.bimo_status()


def _probe_persona_matrix(program: Any) -> Dict[str, Any]:
    # persona_matrix_status() writes .active on read; the
    # organ's own to_dict() is the pure report it wraps.
    return program.persona_matrix.to_dict()


# ------------------------------------------------------------------
# State lines — short, deterministic, from the organ's report.
# ------------------------------------------------------------------

def _state_floor(rep: Dict[str, Any]) -> str:
    return f"floor={'/'.join(str(x) for x in rep.get('floor') or [])} locked={rep.get('locked')}"


def _state_truths(rep: Dict[str, Any]) -> str:
    t = rep.get("truths")
    n = len(t) if isinstance(t, (list, tuple, set, dict)) else "?"
    return f"truths={n} locked={rep.get('locked')}"


def _state_avatar(rep: Dict[str, Any]) -> str:
    return (f"pos={rep.get('pos')} facing={rep.get('facing')} "
            f"posture={rep.get('posture')}")


def _state_companion(rep: Dict[str, Any]) -> str:
    return (f"name={rep.get('name')} mode={rep.get('mode')} "
            f"doing={rep.get('doing')}")


def _state_inspire(rep: Dict[str, Any]) -> str:
    return (f"samples={rep.get('score_samples')} "
            f"vision={rep.get('vision_memory')}")


def _state_self_knowledge(rep: Dict[str, Any]) -> str:
    return (f"probes={rep.get('probes')} hits={rep.get('hits')} "
            f"rate={rep.get('hit_rate')}")


def _state_nursery(rep: Dict[str, Any]) -> str:
    return (f"pending={rep.get('pending')} total={rep.get('total')} "
            f"confirmed={rep.get('confirmed')} rejected={rep.get('rejected')}")


def _state_ideas(rep: Dict[str, Any]) -> str:
    return f"units={rep.get('units')}"


def _state_enhance(rep: Dict[str, Any]) -> str:
    return (f"on={rep.get('on')} level={rep.get('level')} "
            f"pulses={rep.get('session_pulses')}")


def _state_lattice(rep: Dict[str, Any]) -> str:
    return (f"size={rep.get('size')} cells={rep.get('cells')} "
            f"form={rep.get('form')}")


def _state_keys(rep: Dict[str, Any]) -> str:
    return f"keys={rep.get('keys')} payload={rep.get('with_payload')}"


def _state_pulse(rep: Dict[str, Any]) -> str:
    return f"ratio={rep.get('ratio')} sync={rep.get('sync_lock_default')}"


def _state_forces(rep: Dict[str, Any]) -> str:
    active = rep.get("active") or []
    return (f"active={','.join(str(a) for a in active) or '-'} "
            f"weather={rep.get('weather')}")


def _state_personas(rep: Dict[str, Any], program: Any) -> str:
    lens = getattr(program, "persona_lens", None)
    return f"count={rep.get('count')} lens={lens or '-'}"


def _state_bimo(rep: Dict[str, Any]) -> str:
    return (f"mode={rep.get('mode')} pilot={rep.get('pilot')} "
            f"filled={rep.get('filled_count')}")


def _state_persona_matrix(rep: Dict[str, Any]) -> str:
    return f"count={rep.get('count')} active={rep.get('active') or '-'}"


# ------------------------------------------------------------------
# Organ specs: (name, anchor attribute or None for the global
# providers, probe, anchor keys, state renderer, availability
# hook or None). The availability hook maps a well-formed
# report to an availability verdict; the default is YES.
# ------------------------------------------------------------------

def _attr(name: str) -> Callable[[Any], bool]:
    return lambda program: getattr(program, name, None) is not None


def _importable(module: str, attr: str) -> Callable[[Any], bool]:
    def _check(program: Any) -> bool:
        try:
            mod = __import__(module, fromlist=[attr])
            return getattr(mod, attr, None) is not None
        except Exception:
            return False
    return _check


def _personas_exists(program: Any) -> bool:
    return (_importable("form.dell_matrix.personas", "PERSONAS")(program)
            and hasattr(program, "persona_lens"))


def _ideas_exists(program: Any) -> bool:
    try:
        units = program.cube.session.plane.units
        return units is not None and hasattr(units, "__len__")
    except Exception:
        return False


def _enhance_availability(rep: Dict[str, Any]) -> str:
    # The enhance gate's designed state is OFF (Ace's plan:
    # off-by-design, not down). On -> ready; off -> by design.
    return OFF_BY_DESIGN if rep.get("on") is False else YES


class _Spec:
    def __init__(self, name, exists, probe, anchors, state,
                 availability=None, state_takes_program=False):
        self.name = name
        self.exists = exists
        self.probe = probe
        self.anchors = anchors
        self.state = state
        self.availability = availability
        self.state_takes_program = state_takes_program


_SPECS: Tuple[_Spec, ...] = (
    _Spec("floor", _importable("form.mandell.floor", "floor_status"),
          _probe_floor, ("floor", "locked"), _state_floor),
    _Spec("truths", _importable("form.mandell.harmonic_truths", "status"),
          _probe_truths, ("truths", "locked"), _state_truths),
    _Spec("avatar", _attr("avatar"),
          _probe_avatar, ("describe", "pos"), _state_avatar),
    _Spec("companion", _attr("companion"),
          _probe_companion, ("name", "pos"), _state_companion),
    _Spec("inspire", _attr("inspire"),
          _probe_inspire, ("score_samples", "sprite"), _state_inspire),
    _Spec("self_knowledge", _attr("self_knowledge"),
          _probe_self_knowledge, ("probes", "hit_rate"),
          _state_self_knowledge),
    _Spec("nursery", _attr("nursery"),
          _probe_nursery, ("pending", "total"), _state_nursery),
    _Spec("ideas", _ideas_exists,
          _probe_ideas, ("units",), _state_ideas),
    _Spec("enhance", _attr("enhance"),
          _probe_enhance, ("on", "level"), _state_enhance,
          availability=_enhance_availability),
    _Spec("lattice", _attr("lattice"),
          _probe_lattice, ("size", "cells"), _state_lattice),
    _Spec("keys", _attr("keys"),
          _probe_keys, ("keys", "with_payload"), _state_keys),
    _Spec("pulse", _importable("form.dell_matrix.harmonic_core", "pulse_status"),
          _probe_pulse, ("core_pulse", "ratio"), _state_pulse),
    _Spec("forces", _attr("forces"),
          _probe_forces, ("active", "weather"), _state_forces),
    _Spec("personas", _personas_exists,
          _probe_personas, ("count", "categories"), _state_personas,
          state_takes_program=True),
    _Spec("bimo", _attr("bimo"),
          _probe_bimo, ("mode", "filled_count"), _state_bimo),
    _Spec("persona_matrix", _attr("persona_matrix"),
          _probe_persona_matrix, ("cells", "count"),
          _state_persona_matrix),
)

assert tuple(s.name for s in _SPECS) == INVENTORY, "spec/inventory drift"


def _probe_organ(spec: _Spec, program: Any) -> Dict[str, Any]:
    """One organ, fully isolated: this function never raises."""
    out = {"name": spec.name, "exists": NO, "connected": NO,
           "available": NO, "state": "absent"}
    try:
        if not spec.exists(program):
            return out
    except Exception as e:  # the presence check itself failed
        out.update(exists=UNKNOWN, connected=UNKNOWN,
                   available=UNKNOWN,
                   state=f"presence check raised {type(e).__name__}: {e}"[:120])
        return out
    out["exists"] = YES
    try:
        rep = spec.probe(program)
    except Exception as e:
        out.update(connected=UNKNOWN, available=UNKNOWN,
                   state=f"probe raised {type(e).__name__}: {e}"[:120])
        return out
    if not isinstance(rep, dict):
        out.update(state="malformed report (not a mapping)")
        return out
    missing = [k for k in spec.anchors if k not in rep]
    if missing:
        out.update(state=f"malformed report (missing {', '.join(missing)})")
        return out
    out["connected"] = YES
    try:
        state = (spec.state(rep, program) if spec.state_takes_program
                 else spec.state(rep))
    except Exception as e:
        state = f"state line raised {type(e).__name__}: {e}"[:120]
    err = rep.get("error") or (rep.get("reason") if rep.get("ok") is False else None)
    if rep.get("ok") is False or rep.get("error"):
        out["available"] = DEGRADED
        out["state"] = f"{state} · organ reports error: {err}"[:160]
        return out
    out["available"] = (spec.availability(rep) if spec.availability
                        else YES)
    out["state"] = state
    return out


def _organ_passes(organ: Dict[str, Any]) -> bool:
    return (organ["exists"] == YES and organ["connected"] == YES
            and organ["available"] in (YES, OFF_BY_DESIGN))


def build_schema_board(program: Any) -> Dict[str, Any]:
    """Assemble the Dell 39 board for ``program``. Read-only;
    never raises. Returns the structured board (also rendered
    into ``lines`` for the human receipt)."""
    organs = [_probe_organ(spec, program) for spec in _SPECS]
    failing = []
    for organ in organs:
        if _organ_passes(organ):
            continue
        checks = []
        if organ["exists"] != YES:
            checks.append(f"exists={organ['exists']}")
        if organ["connected"] != YES:
            checks.append(f"connected={organ['connected']}")
        if organ["available"] not in (YES, OFF_BY_DESIGN):
            checks.append(f"available={organ['available']}")
        failing.append({"name": organ["name"], "checks": checks})
    verdict = "VALID" if not failing else "INVALID"
    passing = len(organs) - len(failing)
    lines = [f"Schema: {verdict}"]
    board_line = (f"  board: {len(organs)} systems examined · "
                  f"{passing}/{len(organs)} pass")
    if failing:
        named = ", ".join(
            f"{f['name']}({', '.join(f['checks'])})" for f in failing)
        board_line += f" · failing: {named}"
    lines.append(board_line)
    for organ in organs:
        lines.append(
            f"  · {organ['name']}: exists={organ['exists']} "
            f"connected={organ['connected']} "
            f"available={organ['available']} — {organ['state']}")
    return {
        "dell": 39,
        "verdict": verdict,
        "examined": len(organs),
        "passing": passing,
        "failing": failing,
        "organs": organs,
        "lines": lines,
    }


def smoke() -> bool:
    print("=== SCHEMA BOARD SMOKE ===")
    from form.open import open_program
    p = open_program("SchemaBoardSmoke")
    board = build_schema_board(p)
    ok = (board["verdict"] == "VALID" and board["examined"] == 16
          and len(board["lines"]) == 18)
    print(f"verdict={board['verdict']} examined={board['examined']}")
    print(f"=== {'1/1' if ok else '0/1'} ===")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
