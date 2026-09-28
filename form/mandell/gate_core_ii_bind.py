#!/usr/bin/env python3
"""Rebind gate_discipline 51-99 to Core II without deleting domain concepts."""
from __future__ import annotations

from .core_ii import CORE_II
from .address_space import RESERVED_DOMAIN, OLD_TO_NEW


def bind() -> dict:
    from . import gate_discipline as g

    g.EXTENDED_DELL_RESERVE = {n: CORE_II[n]["name"] for n in range(51, 100)}
    g.DOMAIN_RESERVED = {n: row["name"] for n, row in RESERVED_DOMAIN.items()}
    g.OLD_EXTENDED_TO_DOMAIN = dict(OLD_TO_NEW)
    g.NAMED_OPS = dict(g.NAMED_OPS)
    g.NAMED_OPS["Harmonidell"] = 151
    g.NAMED_OPS["Limindell"] = 654
    g.NAMED_OPS["Mandell-dell"] = 167
    g.NAMED_OPS["Nature-dell"] = 560
    return {
        "extended": len(g.EXTENDED_DELL_RESERVE),
        "domain_reserved": len(g.DOMAIN_RESERVED),
        "select": g.EXTENDED_DELL_RESERVE[51],
        "compose": g.EXTENDED_DELL_RESERVE[99],
    }


def smoke() -> bool:
    info = bind()
    return info["select"] == "Select" and info["compose"] == "Compose" and info["extended"] == 49
