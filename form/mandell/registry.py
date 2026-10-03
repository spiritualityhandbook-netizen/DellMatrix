"""True Dell registry — numbered operators + manors.

Namespaces
  CORE_I   00-50  locked action spine
  CORE_II  51-99  instruction architecture (formalized)
  ADDRESS  100-999 reserved until DVS promotion
"""

from __future__ import annotations
from typing import Dict, Any, Optional

from .core_ii import CORE_II

DELLS: Dict[int, Dict[str, str]] = {
    0: {"name": "Nova", "manor": "Origin / fresh start"},
    1: {"name": "Initiate", "manor": "Root command / entry"},
    2: {"name": "Persona", "manor": "Identity / role"},
    3: {"name": "Logic", "manor": "Rules / constraints"},
    4: {"name": "Transform", "manor": "Convert / reshape"},
    5: {"name": "Tone", "manor": "Vibe / style"},
    6: {"name": "Cycle", "manor": "Rhythm / timing"},
    7: {"name": "Link", "manor": "Connect / reference"},
    8: {"name": "Create", "manor": "Instantiate"},
    9: {"name": "Show", "manor": "Render / output"},
    10: {"name": "Keep", "manor": "Pin / persist"},
    11: {"name": "Architect", "manor": "Schema / blueprint"},
    12: {"name": "Test", "manor": "Validate / assert"},
    13: {"name": "Loop", "manor": "Iterate until"},
    14: {"name": "Bind", "manor": "Attach / semantic edge"},
    15: {"name": "Map", "manor": "Coordinate / index"},
    16: {"name": "Decay", "manor": "Discard / expire"},
    17: {"name": "Shadow", "manor": "Background parallel"},
    18: {"name": "Mirror", "manor": "Compare / diff"},
    19: {"name": "Drive", "manor": "Direction / intensity"},
    20: {"name": "Alpha", "manor": "Close / finalize"},
    21: {"name": "Merge", "manor": "Two → one"},
    22: {"name": "Split", "manor": "One → parts"},
    23: {"name": "Lock", "manor": "Freeze immutable"},
    24: {"name": "Unlock", "manor": "Release lock"},
    25: {"name": "Pulse", "manor": "Broadcast outward"},
    26: {"name": "Temp", "manor": "Cold / Warm / Hot planes"},
    27: {"name": "Checkpoint", "manor": "Snapshot state"},
    28: {"name": "Rollback", "manor": "Restore checkpoint"},
    29: {"name": "Compress", "manor": "Shrink payload"},
    30: {"name": "Expand", "manor": "Unfold"},
    31: {"name": "Simulate", "manor": "Dry-run"},
    32: {"name": "Pause", "manor": "Halt"},
    33: {"name": "Resume", "manor": "Continue"},
    34: {"name": "Stamp", "manor": "Time/order mark"},
    35: {"name": "Discover", "manor": "Scan structure"},
    36: {"name": "Inject", "manor": "Load into scope"},
    37: {"name": "Nurture", "manor": "Nursery lifecycle"},
    38: {"name": "Distill", "manor": "Summarize"},
    39: {"name": "Schema", "manor": "Validate shape"},
    40: {"name": "TokenCount", "manor": "Cost measure"},
    41: {"name": "Sanitize", "manor": "Strip secrets"},
    42: {"name": "Retry", "manor": "Re-attempt"},
    43: {"name": "Fallback", "manor": "Safe path"},
    44: {"name": "Bridge", "manor": "External tool"},
    45: {"name": "Translate", "manor": "EN ↔ Mandell"},
    46: {"name": "Rank", "manor": "Score"},
    47: {"name": "Embed", "manor": "Vectorize"},
    48: {"name": "Macro", "manor": "Shortcut sequence"},
    49: {"name": "Profile", "manor": "Benchmark"},
    50: {"name": "Manifest", "manor": "Make real / bring into form"},
}

for _n, _row in CORE_II.items():
    DELLS[_n] = {"name": _row["name"], "manor": _row["manor"]}

CORE_I_MAX = 50
CORE_II_MAX = 99
ADDRESS_MAX = 999

NAMED = {
    "Bindell": 14,
    "Formadell": 8,
    "Evoludell": 4,
    "Harmonidell": 151,
    "Mirrordell": 18,
}


def namespace_of(n: int) -> str:
    if 0 <= n <= CORE_I_MAX:
        return "CORE_I"
    if CORE_I_MAX < n <= CORE_II_MAX:
        return "CORE_II"
    if CORE_II_MAX < n <= ADDRESS_MAX:
        return "ADDRESS_RESERVED"
    return "OUT_OF_RANGE"


def get_dell(n: int) -> Optional[Dict[str, Any]]:
    d = DELLS.get(n)
    if d:
        return {"dell": n, **d, "namespace": namespace_of(n)}
    if CORE_II_MAX < n <= ADDRESS_MAX:
        try:
            from .address_space import get_reserved
            return get_reserved(n)
        except Exception:
            return None
    return None


def lookup(name_or_num) -> Optional[Dict[str, Any]]:
    if isinstance(name_or_num, int):
        return get_dell(name_or_num)
    s = str(name_or_num).strip()
    if s.isdigit():
        return get_dell(int(s))
    if s in NAMED:
        return get_dell(NAMED[s])
    for n, d in DELLS.items():
        if d["name"].lower() == s.lower():
            return get_dell(n)
    try:
        from .address_space import RESERVED_DOMAIN
        for n, d in RESERVED_DOMAIN.items():
            if d["name"].lower() == s.lower():
                return get_dell(n)
    except Exception:
        pass
    return None


def active_core_count() -> int:
    return sum(1 for n in DELLS if n <= CORE_II_MAX)


# ---------------------------------------------------------------------------
# R2 execution standing (GDP-001 Phase 0, Requirement 2, Objective 0.2.1).
#
# Reconciliation of the registered Dell set against the real dispatch code,
# verified 2026-10-03 against the MPC-011-merged base. This table records
# WHERE each Dell executes; it does not duplicate the executors.
#
# Dispatch rules (mirror of form/mandell/executor.py::execute_seed):
#   n in CORE_I_CLOSABLE        -> form/mandell/core_i_ops.py::apply_core_i
#   n in (21, 22)               -> form/mandell/live_identity.py
#                                  (merge_live / split_live)
#   51 <= n <= 99                -> form/mandell/chain_exec.py::execute_chain
#                                  -> form/mandell/core_ii_exec.py
#   0 <= n <= 50 (otherwise)    -> form/mandell/executor_leaf.py::execute_seed
#   100 <= n <= 999 (reserved)   -> NOT executable; address_space marks
#                                  RESERVED_NOT_ACTIVE ("not erased and not
#                                  silently active")
#
# Standing vocabulary:
#   ACTIVE            reachable executor path exists (includes read-only arms
#                     and arms whose real effect is small; effect size is
#                     assessed in docs/LANGUAGE_COMPLETION_MATRIX.md, not here)
#   ACTIVE_REFUSAL    path exists and honestly refuses (ok=False + named
#                     error); Dell 44 Bridge and Dell 47 Embed (offline origin)
#   RESERVED_NOT_ACTIVE
#                     registered only as a historical alias; must not execute
#   UNREGISTERED      not in the registry at all
#
# Historical note: MPC-012 described Dells 27, 28, 34, 35, 40, 44, 47 as
# "dead leaf branches". They are not dead: since the closable-arms change
# they execute through core_i_ops.apply_core_i, which the dispatcher checks
# BEFORE the leaf (even for _leaf=True chain re-entry). The old leaf arms
# for those Dells are shadowed in every production path.
# ---------------------------------------------------------------------------

# Must equal form.mandell.core_i_ops.HANDLED (pinned by r2 registry test).
CORE_I_CLOSABLE = frozenset({27, 28, 34, 35, 37, 40, 44, 47})

# Dells whose production path is live_identity (checked before the leaf).
CORE_I_LIVE_IDENTITY = frozenset({21, 22})

# Core II dispatch families inside core_ii_exec (checked by r2 registry test
# against query_ops.QUERY_DELLS and control_runtime.CONTROL_HEADS).
CORE_II_QUERY_FAMILY = frozenset(
    {51, 52, 54, 55, 56, 57, 58, 59, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79}
)
CORE_II_INLINE = frozenset({53})
CORE_II_CONTROL = frozenset({60, 61, 62, 63, 64, 65, 66})
CORE_II_SPECTRUM = frozenset(range(80, 100))

# Dells with an honest built-in refusal (ok=False + named error).
HONEST_REFUSALS = {
    44: "bridge_unavailable",
    47: "embed_unavailable",
}


def execution_standing(n: int) -> Dict[str, Any]:
    """Reconciled execution standing for a Dell number.

    Returns {"dell", "standing", "dispatch", "evidence"}. Standing is one of
    ACTIVE / ACTIVE_REFUSAL / RESERVED_NOT_ACTIVE / UNREGISTERED. The
    dispatch names the executing module path (or "none"); evidence cites
    the dispatch code that establishes it.
    """
    try:
        n = int(n)
    except (TypeError, ValueError):
        return {"dell": n, "standing": "UNREGISTERED",
                "dispatch": "none",
                "evidence": "not an integer Dell address"}
    if 0 <= n <= CORE_I_MAX:
        if n in CORE_I_CLOSABLE:
            return {"dell": n,
                    "standing": "ACTIVE_REFUSAL" if n in HONEST_REFUSALS else "ACTIVE",
                    "dispatch": "form/mandell/core_i_ops.py::apply_core_i",
                    "evidence": ("executor.py checks HANDLED before the leaf; "
                                 + (f"honest refusal '{HONEST_REFUSALS[n]}'"
                                    if n in HONEST_REFUSALS else
                                    "real closable arm"))}
        if n in CORE_I_LIVE_IDENTITY:
            op = "merge_live" if n == 21 else "split_live"
            return {"dell": n, "standing": "ACTIVE",
                    "dispatch": f"form/mandell/live_identity.py::{op}",
                    "evidence": "executor.py intercepts 21/22 before the leaf"}
        return {"dell": n, "standing": "ACTIVE",
                "dispatch": "form/mandell/executor_leaf.py::execute_seed",
                "evidence": "executor.py single-atom Core I leaf path"}
    if CORE_I_MAX < n <= CORE_II_MAX:
        if n in CORE_II_QUERY_FAMILY:
            fam = "query_ops.apply_query"
        elif n in CORE_II_INLINE:
            fam = "core_ii_exec inline (scope)"
        elif n in CORE_II_CONTROL:
            fam = "control_runtime frames via chain_exec._run_control"
        elif n in CORE_II_SPECTRUM:
            fam = "spectrum_ops.apply_spectrum"
        else:  # pragma: no cover - guarded by the r2 reconciliation test
            return {"dell": n, "standing": "ACTIVE",
                    "dispatch": "form/mandell/core_ii_exec.py::execute_core_ii (unmapped)",
                    "evidence": "falls to unmapped branch (honest ok=False)"}
        return {"dell": n, "standing": "ACTIVE",
                "dispatch": f"form/mandell/chain_exec.py::execute_chain -> {fam}",
                "evidence": "executor.py routes Core II seeds to chain_exec"}
    if CORE_II_MAX < n <= ADDRESS_MAX:
        rec = get_dell(n)
        if rec is not None:
            return {"dell": n, "standing": "RESERVED_NOT_ACTIVE",
                    "dispatch": "none",
                    "evidence": (f"address_space RESERVED_DOMAIN "
                                 f"status={rec.get('status')}")}
        return {"dell": n, "standing": "UNREGISTERED",
                "dispatch": "none",
                "evidence": "no registry entry; parse_seed fails 'unknown Dell'"}
    return {"dell": n, "standing": "UNREGISTERED",
            "dispatch": "none",
            "evidence": "out of Dell address range 0-999"}
