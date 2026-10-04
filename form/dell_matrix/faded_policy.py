#!/usr/bin/env python3
"""P3 R3.5.2: faded-state exclusion policy for resonance/affinity computation.

Ideas whose lifecycle state is FADED (canonical owner:
``form/mandell/idea.py::LifecycleState``) must not participate in
resonance computation: they contribute nothing to pair scoring
(``_affinity``) and are excluded from diffusion (``pulse``).

This module is the single policy point. Wired call sites:
  - ``form/dell_matrix/ringed_growth.py::_affinity`` (pair scoring)
  - ``form/dell_matrix/resonance.py::pulse`` (diffusion)

Not wired (explicit): ``form/dell_matrix/harmony.py::harmony_score``
lands via Stream B; the merge coordinator wires ``exclude_faded``
there. This module deliberately does NOT create a competing
harmony.py.

Attribute convention: ``is_faded(obj)`` reads a ``lifecycle_state``
attribute (nursery proposals carry it as a plain str; other objects
may carry the ``LifecycleState`` enum) and falls back to
``idea_state`` (the ``Idea`` class exposes its own lifecycle as
``idea_state``). Objects carrying neither attribute (e.g. plane
``Unit``s, which have no lifecycle state) are never faded. That is an
explicit limitation, documented here: exclusion is active exactly
where the state is carried; it never invents faded-ness.

All-faded input yields empty/zero results, never an exception.
"""

from __future__ import annotations

from typing import Iterable, List, TypeVar

from form.mandell.idea import LifecycleState

_T = TypeVar("_T")

_FADED_VALUE = LifecycleState.FADED.value  # "faded"


def _state_of(obj: object):
    """Lifecycle state of obj, or None when the object carries none."""
    for attr in ("lifecycle_state", "idea_state"):
        try:
            st = getattr(obj, attr, None)
        except Exception:
            st = None
        if st is not None:
            return st
    return None


def is_faded(obj: object) -> bool:
    """True iff obj carries lifecycle_state == FADED.

    Accepts the ``LifecycleState`` enum member or the plain string
    ``"faded"`` (case/whitespace tolerant). Never raises; objects
    without lifecycle state are not faded.
    """
    if obj is None:
        return False
    st = _state_of(obj)
    if st is None:
        return False
    if isinstance(st, LifecycleState):
        return st is LifecycleState.FADED
    try:
        return str(st).strip().lower() == _FADED_VALUE
    except Exception:
        return False


def exclude_faded(ideas: Iterable[_T]) -> List[_T]:
    """Return the non-faded members of ``ideas``, in original order.

    Never raises on empty input; all-faded input yields [].
    """
    return [i for i in (ideas or []) if not is_faded(i)]
