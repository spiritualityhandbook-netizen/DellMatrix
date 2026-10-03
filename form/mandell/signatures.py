"""Typed Operator Argument Model (TOAM-I).

Minimal typed signatures for Dell operations with established runtime behavior.

LAW: Signatures derived from ACTUAL executable code, not from Dell names.
UNKNOWN stays UNKNOWN. Do not signature Dells without established contracts.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Role:
    """A semantic role in an operator signature."""
    name: str
    type: str = "string"  # "string" | "integer" | "boolean" | "enum" | "unknown"
    required: bool = False
    description: str = ""
    # For enum types, the allowed values if established
    values: Optional[List[str]] = None


@dataclass
class OperatorSignature:
    """Typed signature for a Dell operation."""
    dell: int
    name: str
    roles: List[Role] = field(default_factory=list)
    # Source of this signature: code reference, not name inference
    derived_from: str = ""
    # What happens on success (from code)
    output: str = ""
    # Known failure modes (from code), UNKNOWN if not established
    failures: str = "UNKNOWN"

    def required_roles(self) -> List[Role]:
        return [r for r in self.roles if r.required]

    def optional_roles(self) -> List[Role]:
        return [r for r in self.roles if not r.required]

    def validate(self, args: Dict[str, str]) -> List[str]:
        """Validate arguments against signature. Returns list of errors."""
        errors = []
        role_names = {r.name for r in self.roles}
        # Missing required
        for r in self.required_roles():
            if r.name not in args:
                errors.append(f"MISSING_REQUIRED: {r.name}")
        # Unknown roles
        for k in args:
            if k not in role_names:
                errors.append(f"UNKNOWN_ROLE: {k}")
        # Duplicate roles (can't happen in dict, but check for safety)
        return errors


# Registry of signatures with ESTABLISHED runtime behavior.
# Derived from form/mandell/executor_leaf.py, NOT from Dell names.
_SIGNATURES: Dict[int, OperatorSignature] = {}


def _register(sig: OperatorSignature) -> None:
    _SIGNATURES[sig.dell] = sig


# Dell 8 (Create) — derived from executor_leaf.py:place_idea
# def place_idea(name: str, skin: Skin = Skin.CUBE) -> None:
#     uid = name.replace(" ", "_")[:24] or "idea"
#     program.place(uid, name.replace("_", " "), words=name, skin=skin)
_register(OperatorSignature(
    dell=8,
    name="Create",
    roles=[
        Role(name="name", type="string", required=True,
             description="Name of the idea to create"),
        Role(name="skin", type="enum", required=False,
             description="Visual skin for the idea",
             values=["CUBE", "SPHERE", "UNKNOWN"]),  # Skin enum values from code
    ],
    derived_from="form/mandell/executor_leaf.py:place_idea",
    output="Creates idea with uid, name, words, skin",
    failures="UNKNOWN",
))


# Dell 84 (Copy) — derived from spectrum_ops.py:apply_spectrum (n==84)
#   src = lab or (st.selected[0] if st.selected else "object")
#   dest = f"copy_{src}"  # DERIVED, not caller-controlled
#   st.store[dest] = copy.deepcopy(st.store.get(src, src))
_register(OperatorSignature(
    dell=84,
    name="Copy",
    roles=[
        Role(name="source", type="string", required=False,
             description="Source key to copy (falls back to selected[0], then 'object')"),
    ],
    derived_from="form/mandell/spectrum_ops.py:apply_spectrum:103-109",
    output="Creates st.store['copy_'+src] as deepcopy of source; original intact",
    failures="None established (always succeeds; missing src copies the string itself)",
))
# NOTE: destination is runtime-derived as "copy_{src}", NOT a caller argument.
# Signature must NOT claim caller-controlled destination.

# Dell 85 (Move) — derived from spectrum_ops.py:apply_spectrum (n==85)
#   src, _, dest = lab.partition(">")
#   if not src or not dest: ok=False, err="malformed_move"
#   elif src not in st.store: ok=False, err="move_missing"
#   elif dest != src: st.store[dest] = st.store.pop(src)
_register(OperatorSignature(
    dell=85,
    name="Move",
    roles=[
        Role(name="source", type="string", required=True,
             description="Source key to move"),
        Role(name="destination", type="string", required=True,
             description="Destination key"),
    ],
    derived_from="form/mandell/spectrum_ops.py:apply_spectrum:110-125",
    output="Moves st.store[src] to st.store[dest]; identity preserved",
    failures="malformed_move (missing src/dest), move_missing (src not in store)",
))
# Existing encoding: lab = "source>destination"

# Dell 86 (Delete) — derived from spectrum_ops.py:apply_spectrum (n==86)
#   key = lab
#   if key in st.store: st.store.pop(key)
#   elif key in st.groups: st.groups.pop(key)
#   else: ok=False, err=f"delete_missing:{key}"
_register(OperatorSignature(
    dell=86,
    name="Delete",
    roles=[
        Role(name="key", type="string", required=True,
             description="Key to delete from store or groups"),
    ],
    derived_from="form/mandell/spectrum_ops.py:apply_spectrum:126-142",
    output="Removes key from st.store or st.groups",
    failures="delete_missing:{key} (key not found)",
))
# NOTE: No selected/default fallback in code. Key is required for typed invocation.

# Dell 87 (Replace) — derived from spectrum_ops.py:apply_spectrum (n==87)
#   old, _, new = lab.partition(">")
#   if old not in st.store: ok=False, err=f"replace_missing:{old}"
#   else: st.store[new or old] = st.store.pop(old)
_register(OperatorSignature(
    dell=87,
    name="Replace",
    roles=[
        Role(name="old", type="string", required=True,
             description="Existing key to replace"),
        Role(name="new", type="string", required=False,
             description="New key (if empty, uses old — legacy no-op fallback)"),
    ],
    derived_from="form/mandell/spectrum_ops.py:apply_spectrum:143-154",
    output="Atomically substitutes st.store[old] with st.store[new or old]",
    failures="replace_missing:{old} (old not in store)",
))
# NOTE: Empty new → uses old (st.store[old] = st.store.pop(old), effectively no-op).
# This is legacy fallback behavior, not meaningful optionality.

# Dell 88 (Patch) — derived from spectrum_ops.py:apply_spectrum (n==88)
#   key, _, val = lab.partition("=")
#   if key not in st.store: ok=False, err=f"patch_miss:{key}"
#   else: st.store[key] = val
_register(OperatorSignature(
    dell=88,
    name="Patch",
    roles=[
        Role(name="key", type="string", required=True,
             description="Key to patch"),
        Role(name="value", type="string", required=True,
             description="New value (may be empty string)"),
    ],
    derived_from="form/mandell/spectrum_ops.py:apply_spectrum:155-166",
    output="Sets st.store[key] = value (partial targeted modification)",
    failures="patch_miss:{key} (key not in store)",
))
# NOTE: Empty value is allowed (st.store[key] = ""). Value must be present
# in the partition but can be empty string.
# Existing encoding: lab = "key=value"


# Dell 51 (Select) — derived from query_ops.py:apply_query (n==51)
#   ids = ids_fn(program)
#   st.selected = list(ids) if not lab else [i for i in ids if pred_fn(lab, i)]
#   st.last_result = result_cell(value=list(st.selected), ...)
_register(OperatorSignature(
    dell=51,
    name="Select",
    roles=[
        Role(name="predicate", type="string", required=False,
             description="Selection predicate (empty selects all)"),
    ],
    derived_from="form/mandell/query_ops.py:apply_query:18-21",
    output="Sets st.selected to matching IDs; publishes to last_result",
    failures="None established (empty predicate selects all)",
))
# Existing encoding: lab = predicate (or "" for all)

# Dell 54 (Query) — derived from query_ops.py:apply_query (n==54)
#   ids = list(st.selected)
#   hits = [i for i in ids if pred_fn(lab, i)] if lab else list(ids)
#   st.last_result = result_cell(value=hits, ...)
_register(OperatorSignature(
    dell=54,
    name="Query",
    roles=[
        Role(name="predicate", type="string", required=False,
             description="Query predicate (empty queries all selected)"),
    ],
    derived_from="form/mandell/query_ops.py:apply_query:24-27",
    output="Publishes matching IDs to last_result; st.selected unchanged",
    failures="None established (empty result is valid)",
))
# Existing encoding: lab = predicate (or "" for all)

# Dell 56 (Get) — derived from query_ops.py:apply_query (n==56)
#   key = lab or (list(st.store)[-1] if st.store else "")
#   if key not in st.store: matched=False, error="missing"
#   else: val = st.store[key]; publishes to last_result
_register(OperatorSignature(
    dell=56,
    name="Get",
    roles=[
        Role(name="key", type="string", required=True,
             description="Store key to retrieve"),
    ],
    derived_from="form/mandell/query_ops.py:apply_query:29-38",
    output="Publishes st.store[key] to last_result; read-only",
    failures="missing (key not in store; matched=False, no mutation)",
))
# Existing encoding: lab = key
# NOTE: Read-only. Never mutates store.

# Dell 58 (Match) — derived from query_ops.py:apply_query (n==58)
#   pat = lab.lower()
#   st.selected = [i for i in ids if pat in str(i).lower()] if pat else list(ids)
#   st.last_result = result_cell(value=list(st.selected), ...)
_register(OperatorSignature(
    dell=58,
    name="Match",
    roles=[
        Role(name="pattern", type="string", required=False,
             description="Substring pattern (empty matches all)"),
    ],
    derived_from="form/mandell/query_ops.py:apply_query:44-47",
    output="Sets st.selected to pattern matches; publishes to last_result",
    failures="None established (empty result is valid)",
))
# Existing encoding: lab = pattern (or "" for all)


# Dell 57 (Compare) — derived from query_ops.py:apply_query (n==57)
#   head = lab.lower().split(":")[0].split(" ")[0]
#   expr = lab if head in (...) else ("eq:" + ...)
#   cmpd = eval_predicate(st, program, expr)
_register(OperatorSignature(
    dell=57,
    name="Compare",
    roles=[
        Role(name="expression", type="string", required=True,
             description="Predicate expression (e.g., 'eq: x 5')"),
    ],
    derived_from="form/mandell/query_ops.py:apply_query:39-43",
    output="Publishes comparison result to last_result",
    failures="type_mismatch (incompatible types)",
))
# Existing encoding: lab = expression

# Dell 67 (Any) — derived from query_ops.py:apply_query (n==67)
#   ids = list(st.selected)
#   hit = any(pred_fn(lab, i) for i in ids) if ids else False
_register(OperatorSignature(
    dell=67,
    name="Any",
    roles=[
        Role(name="predicate", type="string", required=False,
             description="Predicate (empty checks non-empty selection)"),
    ],
    derived_from="form/mandell/query_ops.py:apply_query:48-51",
    output="Publishes boolean to last_result",
    failures="None established",
))
# Existing encoding: lab = predicate (or "")

# Dell 68 (All) — derived from query_ops.py:apply_query (n==68)
#   hit = all(pred_fn(lab, i) for i in ids) if ids else True
_register(OperatorSignature(
    dell=68,
    name="All",
    roles=[
        Role(name="predicate", type="string", required=False,
             description="Predicate (empty checks all)"),
    ],
    derived_from="form/mandell/query_ops.py:apply_query:52-55",
    output="Publishes boolean to last_result",
    failures="None established",
))
# Existing encoding: lab = predicate (or "")

# Dell 69 (None) — derived from query_ops.py:apply_query (n==69)
#   hit = not any(pred_fn(lab, i) for i in ids)
_register(OperatorSignature(
    dell=69,
    name="None",
    roles=[
        Role(name="predicate", type="string", required=False,
             description="Predicate (empty checks empty selection)"),
    ],
    derived_from="form/mandell/query_ops.py:apply_query:56-59",
    output="Publishes boolean to last_result",
    failures="None established",
))
# Existing encoding: lab = predicate (or "")


def get_signature(dell: int) -> Optional[OperatorSignature]:
    """Get signature for a Dell, or None if not established."""
    return _SIGNATURES.get(dell)


def has_signature(dell: int) -> bool:
    """Whether a Dell has an established signature."""
    return dell in _SIGNATURES


def list_signatures() -> List[int]:
    """Dells with established signatures."""
    return sorted(_SIGNATURES.keys())


def lower_args_to_lab(dell: int, args: Dict[str, str]) -> str:
    """Lower typed SeedAtom.args to the existing lab representation.

    This is the canonical bridge between TOAM-I typed syntax and the
    existing spectrum_ops.py executor contracts. It does NOT create
    a second executor — it produces the lab string that apply_spectrum
    already understands.

    Raises ValueError if required args are missing (validate first).
    """
    if dell == 84:
        # Copy: lab = source (or "" for fallback chain)
        return args.get("source", "")
    elif dell == 85:
        # Move: lab = "source>destination"
        src = args.get("source", "")
        dst = args.get("destination", "")
        return f"{src}>{dst}"
    elif dell == 86:
        # Delete: lab = key
        return args.get("key", "")
    elif dell == 87:
        # Replace: lab = "old>new"
        old = args.get("old", "")
        new = args.get("new", "")
        return f"{old}>{new}"
    elif dell == 88:
        # Patch: lab = "key=value"
        key = args.get("key", "")
        val = args.get("value", "")
        return f"{key}={val}"
    elif dell == 51:
        # Select: lab = predicate (or "" for all)
        return args.get("predicate", "")
    elif dell == 54:
        # Query: lab = predicate (or "" for all)
        return args.get("predicate", "")
    elif dell == 56:
        # Get: lab = key
        return args.get("key", "")
    elif dell == 58:
        # Match: lab = pattern (or "" for all)
        return args.get("pattern", "")
    elif dell == 57:
        # Compare: lab = expression
        return args.get("expression", "")
    elif dell == 67:
        # Any: lab = predicate (or "")
        return args.get("predicate", "")
    elif dell == 68:
        # All: lab = predicate (or "")
        return args.get("predicate", "")
    elif dell == 69:
        # None: lab = predicate (or "")
        return args.get("predicate", "")
    else:
        # Dell 8 uses place_idea (different executor); others have no lab contract
        raise ValueError(f"No lab lowering for Dell {dell}")
