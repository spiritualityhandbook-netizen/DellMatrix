"""Manifest = Term + Manor + Dell. Dual output boundary."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .registry import lookup, get_dell


@dataclass
class Manifest:
    term: str
    manor: str
    dell: int

    def as_mandel(self) -> str:
        """Structure inside — compact Mandel form."""
        return f"{self.dell:02d}[{self.term}]"

    def as_english(self) -> str:
        """Display only."""
        return f"{self.term}: {self.manor} (Dell {self.dell:02d})"

    def to_dict(self) -> Dict[str, Any]:
        return {"term": self.term, "manor": self.manor, "dell": self.dell}


def manifest_from_dell(n: int, term: Optional[str] = None) -> Optional[Manifest]:
    d = get_dell(n)
    if not d:
        return None
    return Manifest(term=term or d["name"], manor=d["manor"], dell=n)


def manifest_from_lookup(key) -> Optional[Manifest]:
    d = lookup(key)
    if not d:
        return None
    return Manifest(term=d["name"], manor=d["manor"], dell=d["dell"])
