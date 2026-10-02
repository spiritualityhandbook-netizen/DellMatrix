"""TPP-I: Temporal Presence Projection I (NBD-Ω-048)

User-controlled presence layer for ideas. Does NOT modify Dell 10/16/34/26.
Does NOT fade protected evidence classes.

Presence model:
- ACTIVE / FADED (presence state)
- PINNED / UNPINNED (orthogonal retention flag)
- PINNED implies ACTIVE

Commands: pin, unpin, fade, unfade, age (read-only)
"""

from typing import Dict, Any, Optional, Tuple


# Protected classes that must never be faded
PROTECTED_PREFIXES = (
    "outcome:",
    "interaction:",
    "evolution:",
    "checkpoint:",
    "duobeta:",
    "knowledge:",
)


def ensure_lifecycle(p) -> Dict[str, Any]:
    """Initialize lifecycle metadata dict on Program if missing."""
    if not hasattr(p, "lifecycle") or p.lifecycle is None:
        p.lifecycle = {}
    return p.lifecycle


def _is_protected(ref: str) -> bool:
    """Check if a ref resolves to a protected evidence class."""
    low = ref.lower()
    return low.startswith(PROTECTED_PREFIXES)


def resolve_idea(p, ref: str):
    """Resolve ref to a Unit idea by id or label.

    Returns (unit, error_message). If error_message is not None, resolution failed.
    """
    if _is_protected(ref):
        return None, f"REFUSED: '{ref}' resolves to a protected evidence class. Lifecycle operations do not apply to canonical evidence."

    units = p.cube.session.plane.units
    # Try exact id match
    if ref in units:
        return units[ref], None
    # Try label match (case-insensitive)
    low = ref.lower()
    for uid, unit in units.items():
        label = getattr(unit, "label", "")
        if label and label.lower() == low:
            return unit, None
    return None, f"Unknown idea: '{ref}'"


def get_presence(p, unit_id: str) -> Dict[str, Any]:
    """Get presence metadata for a unit. Returns defaults if not set."""
    lc = ensure_lifecycle(p)
    return lc.get(unit_id, {
        "presence": "active",
        "pinned": False,
        "created_seq": None,  # Unknown for legacy items
    })


def set_presence(p, unit_id: str, presence: str = None, pinned: bool = None,
                created_seq: int = None):
    """Update presence metadata for a unit."""
    lc = ensure_lifecycle(p)
    meta = lc.get(unit_id, {
        "presence": "active",
        "pinned": False,
        "created_seq": created_seq,
    })
    if presence is not None:
        meta["presence"] = presence
    if pinned is not None:
        meta["pinned"] = pinned
    if created_seq is not None and meta.get("created_seq") is None:
        meta["created_seq"] = created_seq
    lc[unit_id] = meta
    return meta


def _make_outcome(p, operation: str, ref: str, unit_id: str,
                  interaction_id: str, success: bool, detail: str):
    """Create a canonical Outcome for a lifecycle mutation.

    Uses the existing specialized execution observation authority (SAOC-I/II pattern).
    Does NOT fabricate Dell/Mandell provenance.
    """
    from form.mandell.execution_observer import observe_specialized_execution

    outcome = observe_specialized_execution(
        p,
        action=operation,
        input_text=f"{operation} {ref}",
        ok=success,
        semantic=f"lifecycle[{operation}:{unit_id}]",
        interaction_id=interaction_id,
        messages=[detail],
    )
    return outcome


def do_pin(p, ref: str, interaction_id: str) -> Tuple[Any, str]:
    """Pin an idea: protect from fade, ensure active."""
    unit, err = resolve_idea(p, ref)
    if err:
        return p, err

    uid = unit.id
    meta = get_presence(p, uid)

    if meta["pinned"]:
        # Already pinned: idempotent, still create Outcome for observability
        outcome = _make_outcome(p, "pin", ref, uid, interaction_id, True,
                                f"Already pinned: {uid}")
        oid_str = outcome.get("outcome_id", "?") if outcome else "?"
        return p, f"Already pinned: {uid} (Outcome {oid_str})"

    # PINNED implies ACTIVE: if faded, restore to active
    was_faded = meta["presence"] == "faded"
    set_presence(p, uid, presence="active", pinned=True,
                 created_seq=p.outcome_seq)

    outcome = _make_outcome(p, "pin", ref, uid, interaction_id, True,
                            f"Pinned: {uid}" + (" (restored from faded)" if was_faded else ""))
    return p, f"Pinned: {uid}" + (" (restored from faded)" if was_faded else "")


def do_unpin(p, ref: str, interaction_id: str) -> Tuple[Any, str]:
    """Unpin an idea: remove protection. Does NOT fade."""
    unit, err = resolve_idea(p, ref)
    if err:
        return p, err

    uid = unit.id
    meta = get_presence(p, uid)

    if not meta["pinned"]:
        outcome = _make_outcome(p, "unpin", ref, uid, interaction_id, True,
                                f"Already unpinned: {uid}")
        oid_str = outcome.get("outcome_id", "?") if outcome else "?"
        return p, f"Already unpinned: {uid} (Outcome {oid_str})"

    set_presence(p, uid, pinned=False)
    outcome = _make_outcome(p, "unpin", ref, uid, interaction_id, True,
                            f"Unpinned: {uid} (remains active)")
    return p, f"Unpinned: {uid} (remains active, not faded)"


def do_fade(p, ref: str, interaction_id: str) -> Tuple[Any, str]:
    """Fade an idea: reduce active presence. Refuses if pinned."""
    unit, err = resolve_idea(p, ref)
    if err:
        return p, err

    uid = unit.id
    meta = get_presence(p, uid)

    if meta["pinned"]:
        # REFUSE: cannot fade pinned items
        outcome = _make_outcome(p, "fade", ref, uid, interaction_id, False,
                                f"REFUSED: {uid} is pinned")
        return p, f"REFUSED: Cannot fade pinned idea '{uid}'. Unpin first."

    if meta["presence"] == "faded":
        outcome = _make_outcome(p, "fade", ref, uid, interaction_id, True,
                                f"Already faded: {uid}")
        oid_str = outcome.get("outcome_id", "?") if outcome else "?"
        return p, f"Already faded: {uid} (Outcome {oid_str})"

    set_presence(p, uid, presence="faded", created_seq=p.outcome_seq)
    outcome = _make_outcome(p, "fade", ref, uid, interaction_id, True,
                            f"Faded: {uid} (recoverable via unfade)")
    return p, f"Faded: {uid} (use 'unfade {ref}' to restore)"


def do_unfade(p, ref: str, interaction_id: str) -> Tuple[Any, str]:
    """Unfade an idea: restore to active. Same identity, no reconstruction."""
    unit, err = resolve_idea(p, ref)
    if err:
        return p, err

    uid = unit.id
    meta = get_presence(p, uid)

    if meta["presence"] == "active":
        outcome = _make_outcome(p, "unfade", ref, uid, interaction_id, True,
                                f"Already active: {uid}")
        oid_str = outcome.get("outcome_id", "?") if outcome else "?"
        return p, f"Already active: {uid} (Outcome {oid_str})"

    set_presence(p, uid, presence="active")
    outcome = _make_outcome(p, "unfade", ref, uid, interaction_id, True,
                            f"Restored: {uid} (same identity)")
    return p, f"Restored: {uid} (same idea, same content)"


def do_age(p, ref: str) -> Tuple[Any, str]:
    """Report lifecycle age. Read-only, no mutation, no Outcome."""
    unit, err = resolve_idea(p, ref)
    if err:
        return p, err

    uid = unit.id
    meta = get_presence(p, uid)
    created = meta.get("created_seq")

    if created is None:
        return p, f"Age of '{uid}': UNKNOWN (predates lifecycle tracking)"

    current = p.outcome_seq
    age = current - created
    presence = meta["presence"]
    pinned = "pinned" if meta["pinned"] else "unpinned"
    return p, f"Age of '{uid}': {age} interactions (created at seq {created}, now {current}); {presence}, {pinned}"


def list_ideas(p, show: str = "active") -> str:
    """List ideas with presence filtering.

    show: 'active' (default), 'faded', 'all'
    """
    units = p.cube.session.plane.units
    lines = []

    for uid, unit in units.items():
        meta = get_presence(p, uid)
        presence = meta["presence"]
        pinned = meta["pinned"]

        if show == "active" and presence != "active":
            continue
        if show == "faded" and presence != "faded":
            continue
        # show == "all": include everything

        label = getattr(unit, "label", uid)
        flags = []
        if pinned:
            flags.append("PINNED")
        if presence == "faded":
            flags.append("FADED")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        lines.append(f"  {uid}: {label}{flag_str}")

    if not lines:
        if show == "active":
            return "No active ideas. (Use 'ideas faded' or 'ideas all' to see more.)"
        elif show == "faded":
            return "No faded ideas."
        else:
            return "No ideas."

    header = {"active": "Active ideas:", "faded": "Faded ideas:", "all": "All ideas:"}[show]
    return header + "\n" + "\n".join(lines)


def handle_lifecycle_command(p, line: str, interaction_id: str) -> Tuple[bool, Any, str]:
    """Handle pin/unpin/fade/unfade/age/ideas commands.

    Returns (handled, program, message).
    """
    low = line.strip().lower()

    # ideas [faded|all]
    if low == "ideas" or low.startswith("ideas "):
        parts = low.split()
        show = "active"
        if len(parts) > 1:
            if parts[1] == "faded":
                show = "faded"
            elif parts[1] == "all":
                show = "all"
            else:
                return True, p, f"Usage: ideas [faded|all]"
        return True, p, list_ideas(p, show)

    # pin <ref> (also handle bare "pin")
    if low == "pin" or low.startswith("pin "):
        ref = line.strip()[3:].strip()
        if not ref:
            return True, p, "Usage: pin <idea>"
        p, msg = do_pin(p, ref, interaction_id)
        return True, p, msg

    # unpin <ref> (also handle bare "unpin")
    if low == "unpin" or low.startswith("unpin "):
        ref = line.strip()[6:].strip()
        if not ref:
            return True, p, "Usage: unpin <idea>"
        p, msg = do_unpin(p, ref, interaction_id)
        return True, p, msg

    # fade <ref> (also handle bare "fade")
    if low == "fade" or low.startswith("fade "):
        ref = line.strip()[4:].strip()
        if not ref:
            return True, p, "Usage: fade <idea>"
        p, msg = do_fade(p, ref, interaction_id)
        return True, p, msg

    # unfade <ref> (also handle bare "unfade")
    if low == "unfade" or low.startswith("unfade "):
        ref = line.strip()[6:].strip()
        if not ref:
            return True, p, "Usage: unfade <idea>"
        p, msg = do_unfade(p, ref, interaction_id)
        return True, p, msg

    # age <ref> (also handle bare "age")
    if low == "age" or low.startswith("age "):
        ref = line.strip()[3:].strip()
        if not ref:
            return True, p, "Usage: age <idea>"
        p, msg = do_age(p, ref)
        return True, p, msg

    return False, p, ""
