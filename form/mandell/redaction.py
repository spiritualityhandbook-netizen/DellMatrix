#!/usr/bin/env python3
"""DAF-02/B5: the ONE Sanitize redaction authority.

Dell 41[Sanitize] exists to keep secret-shaped values out of the
program's surfaces. Before this module the redaction regexes lived
only inside the Sanitize leaf arm, while the generic Mandell/English
echoes, the returned seed/english metadata, the chain echoes, the
execution observer's receipt, and the persisted outcome ledger all
carried the RAW input — so Sanitize disclosed exactly what it
redacted (Director DAF-02, executed on b352e39).

Every surface that echoes a seed containing a Sanitize atom uses
these helpers, so there is exactly one redaction semantics:

- ``sanitize_text`` — the canonical redaction (secret-key values
  and 12+ digit runs), unchanged from the historical OUT line.
- ``has_sanitize`` — does a parsed seed contain Dell 41?
- ``redacted_seed`` — a copy of the parsed seed whose label,
  per-atom segment labels, typed arg values, and raw text have
  been sanitized; echoes built from it cannot leak. Seeds without
  a Sanitize atom are returned unchanged (identity).

No digests are substituted for secrets: a digest of a guessable
secret is not confidentiality (Director DAF-02).
"""
from __future__ import annotations

import re
from dataclasses import replace
from typing import Any

_SECRET_RE = re.compile(
    r"(?i)(password|secret|token|api[_-]?key|bearer)\s*[:=]?\s*\S+")
_NUMBER_RE = re.compile(r"\b\d{12,}\b")

SANITIZE_DELL = 41


def sanitize_text(text: str) -> str:
    """Canonical Sanitize redaction of one text value."""
    out = _SECRET_RE.sub(r"\1=[REDACTED]", text or "")
    out = _NUMBER_RE.sub("[REDACTED_NUM]", out)
    return out


def has_sanitize(parsed: Any) -> bool:
    """True when any atom of the parsed seed is Dell 41[Sanitize]."""
    return any(int(getattr(a, "dell", -1)) == SANITIZE_DELL
               for a in (getattr(parsed, "atoms", None) or []))


def redacted_seed(parsed: Any) -> Any:
    """Echo-safe copy of a parsed seed (identity if no Sanitize)."""
    if parsed is None or not has_sanitize(parsed):
        return parsed
    atoms = []
    for a in parsed.atoms:
        atoms.append(replace(
            a,
            args={k: sanitize_text(v) for k, v in (a.args or {}).items()},
            label=sanitize_text(a.label or ""),
        ))
    return replace(
        parsed,
        atoms=atoms,
        label=sanitize_text(parsed.label or ""),
        raw=sanitize_text(parsed.raw or ""),
    )
