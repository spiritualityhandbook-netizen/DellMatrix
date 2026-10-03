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


def get_signature(dell: int) -> Optional[OperatorSignature]:
    """Get signature for a Dell, or None if not established."""
    return _SIGNATURES.get(dell)


def has_signature(dell: int) -> bool:
    """Whether a Dell has an established signature."""
    return dell in _SIGNATURES


def list_signatures() -> List[int]:
    """Dells with established signatures."""
    return sorted(_SIGNATURES.keys())
