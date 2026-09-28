#!/usr/bin/env python3
"""Mandell seed language — parse, validate, explain. Atoms: 08[Create] or 151[Harmonic]."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import re
from .registry import get_dell, lookup, DELLS
from .manifest import Manifest, manifest_from_dell

_ATOM = re.compile(r"(\d{1,3})\[([A-Za-z_][A-Za-z0-9_]*)\]")
_FLOW = re.compile(r"(>>|>|:|::)")

@dataclass
class SeedAtom:
    dell: int
    term: str
    resolved_term: str = ""
    confidence: float = 1.0
    resolve_reason: str = "canonical"
    def as_mandel(self) -> str:
        width = 3 if self.dell > 99 else 2
        shown = self.resolved_term or self.term
        return f"{self.dell:0{width}d}[{shown}]"
    def as_english(self) -> str:
        d = get_dell(self.dell)
        manor = d["manor"] if d else "?"
        shown = self.resolved_term or self.term
        return f"{shown} ({manor})"

@dataclass
class Seed:
    atoms: List[SeedAtom] = field(default_factory=list)
    flows: List[str] = field(default_factory=list)
    label: str = ""
    raw: str = ""
    ok: bool = True
    error: str = ""
    def as_mandel(self) -> str:
        if not self.atoms:
            return ""
        parts = [self.atoms[0].as_mandel()]
        for i, flow in enumerate(self.flows):
            if i + 1 < len(self.atoms):
                parts.append(f" {flow} {self.atoms[i+1].as_mandel()}")
        s = "".join(parts)
        if self.label:
            s += f" :: {self.label}"
        return s
    def as_english(self) -> str:
        if not self.atoms:
            return "(empty seed)"
        body = " then ".join(a.as_english() for a in self.atoms)
        if self.label:
            body += f" → {self.label}"
        return body
    def primary_dell(self) -> Optional[int]:
        return self.atoms[0].dell if self.atoms else None

def parse_seed(text: str) -> Seed:
    raw = (text or "").strip()
    if not raw:
        return Seed(ok=False, error="empty", raw=raw)
    label = ""
    body = raw
    if "::" in raw:
        body, _, rest = raw.partition("::")
        label = rest.strip()
        body = body.strip()
    atoms: List[SeedAtom] = []
    flows: List[str] = []
    pos = 0
    body_len = len(body)
    last_was_atom = False
    while pos < body_len:
        while pos < body_len and body[pos].isspace():
            pos += 1
        if pos >= body_len:
            break
        m = _ATOM.match(body, pos)
        if m:
            n = int(m.group(1))
            term = m.group(2)
            d = get_dell(n)
            if not d:
                return Seed(ok=False, error=f"unknown Dell {n}", raw=raw)
            resolved_term = term
            conf = 1.0
            reason = "passthrough"
            try:
                from .manifest_resolver import resolve_manifest
                res = resolve_manifest(n, term, label)
                resolved_term = res.resolved
                conf = res.confidence
                reason = res.reason
            except Exception:
                pass
            atoms.append(SeedAtom(dell=n, term=term, resolved_term=resolved_term, confidence=conf, resolve_reason=reason))
            last_was_atom = True
            pos = m.end()
            continue
        m2 = _FLOW.match(body, pos)
        if m2:
            op = m2.group(1)
            if op == "::":
                pos = m2.end()
                continue
            if not last_was_atom:
                return Seed(ok=False, error=f"flow '{op}' without left atom", raw=raw)
            flows.append(op)
            last_was_atom = False
            pos = m2.end()
            continue
        return Seed(ok=False, error=f"unexpected at {pos}: {body[pos:pos+12]!r}", raw=raw)
    if not atoms:
        return Seed(ok=False, error="no Dell atoms found", raw=raw)
    if len(flows) > len(atoms) - 1:
        return Seed(ok=False, error="too many flow operators", raw=raw)
    return Seed(atoms=atoms, flows=flows, label=label, raw=raw, ok=True)

def looks_like_seed(text: str) -> bool:
    return bool(_ATOM.search(text or ""))

def explain_seed(text: str) -> Dict[str, Any]:
    s = parse_seed(text)
    return {"ok": s.ok, "error": s.error, "mandel": s.as_mandel() if s.ok else "", "english": s.as_english() if s.ok else "", "atoms": [{"dell": a.dell, "term": a.term, "resolved": a.resolved_term, "confidence": a.confidence, "reason": a.resolve_reason} for a in s.atoms], "label": s.label, "raw": s.raw}

def seed_from_dell_chain(dells: List[int], label: str = "", flows: Optional[List[str]] = None) -> Seed:
    atoms = []
    for n in dells:
        d = get_dell(n)
        if not d:
            continue
        atoms.append(SeedAtom(dell=n, term=d["name"], resolved_term=d["name"]))
    fl_list = list(flows) if isinstance(flows, list) else []
    while len(fl_list) < len(atoms) - 1:
        fl_list.append(">")
    return Seed(atoms=atoms, flows=fl_list[: max(0, len(atoms) - 1)], label=label, ok=bool(atoms))
