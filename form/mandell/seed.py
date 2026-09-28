#!/usr/bin/env python3
"""Mandell seed language — parse, validate, explain. Atoms: 08[Create] or 151[Harmonic]."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import re
from .registry import get_dell, lookup, DELLS
from .manifest import Manifest, manifest_from_dell

BULLET = "\u2022"  # •  ManifestSet separator. Not comma. Not underscore.
_ATOM = re.compile(r"(\d{1,3})\[([^\]]*)\]")
_MEMBER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
FLOW_OPS = (
    "<<[Delta]",
    "<:>",
    ">>>",
    ">>",
    ":>",
    "<:",
    "::",
    ">",
    ":",
)
_FLOW = re.compile("|".join(re.escape(op) for op in FLOW_OPS))
CHAIN_DVS = {
    "name": "Chain",
    "necessity": 0.91,
    "decision": "GRAMMAR_OPERATOR",
    "number": None,
    "reason": "Same-Dell ordered ManifestSet. Existing Dell already carries gravity.",
}
CHAINLINK_DVS = {
    "name": "Chainlink",
    "necessity": 0.88,
    "decision": "GRAMMAR_OPERATOR",
    "number": None,
    "reason": "Positional zip across equal ManifestSets. Flow already exists.",
}
MANDELLMOJI = {"Chain": "⛓️‍💥", "Chainlink": "⛓️"}
CELLS: Dict[str, str] = {}
CELL_DEPTH = 8

@dataclass
class SeedAtom:
    dell: int
    term: str
    resolved_term: str = ""
    confidence: float = 1.0
    resolve_reason: str = "canonical"
    origin: str = "atom"
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

def _fail(raw: str, error: str) -> Seed:
    return Seed(ok=False, error=error, raw=raw)


def split_manifest_set(inner: str, raw: str) -> Any:
    if inner is None:
        return _fail(raw, "empty member")
    if "[" in inner or "]" in inner:
        return _fail(raw, "aggregate Dell conflict — use explicit atom form")
    if "," in inner:
        return _fail(raw, "• not ,")
    if "\u00b7" in inner or "\u2219" in inner or "\u30fb" in inner:
        return _fail(raw, "invalid unicode — ManifestSet separator is •")
    if not inner.strip():
        return _fail(raw, "empty member")
    if BULLET in inner:
        parts = inner.split(BULLET)
        if any(p.strip() == "" for p in parts):
            return _fail(raw, "empty member")
        members = [p.strip() for p in parts]
    else:
        members = [inner.strip()]
    for m in members:
        if not _MEMBER.match(m):
            return _fail(raw, f"invalid manifest member {m!r}")
    return members


def _resolve_term(n: int, term: str, label: str) -> tuple:
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
    return resolved_term, conf, reason


def _atom(n: int, term: str, label: str, origin: str) -> SeedAtom:
    resolved, conf, reason = _resolve_term(n, term, label)
    return SeedAtom(
        dell=n, term=term, resolved_term=resolved,
        confidence=conf, resolve_reason=reason, origin=origin,
    )


def parse_seed(text: str) -> Seed:
    raw = (text or "").strip()
    if not raw:
        return _fail(raw, "empty")
    label = ""
    body = raw
    if "::" in raw:
        head, _, rest = raw.rpartition("::")
        rest_s = rest.strip()
        if rest_s and not _ATOM.match(rest_s):
            label = rest_s
            body = head.strip()
    proto: List[Dict[str, Any]] = []
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
            inner = m.group(2)
            d = get_dell(n)
            if not d:
                return _fail(raw, f"unknown Dell {n}")
            members = split_manifest_set(inner, raw)
            if isinstance(members, Seed):
                return members
            proto.append({"dell": n, "members": members})
            last_was_atom = True
            pos = m.end()
            continue
        m2 = _FLOW.match(body, pos)
        if m2:
            op = m2.group(0)
            if op == "::" and not last_was_atom:
                pos = m2.end()
                continue
            if not last_was_atom:
                return _fail(raw, f"flow '{op}' without left atom")
            flows.append(op)
            last_was_atom = False
            pos = m2.end()
            continue
        return _fail(raw, f"unexpected at {pos}: {body[pos:pos+12]!r}")
    if not proto:
        return _fail(raw, "no Dell atoms found")
    if len(flows) > len(proto) - 1:
        return _fail(raw, "too many flow operators")
    atoms: List[SeedAtom] = []
    out_flows: List[str] = []

    if len(proto) == 2 and flows:
        ln, rn = len(proto[0]["members"]), len(proto[1]["members"])
        if ln != rn and (ln > 1 or rn > 1):
            return _fail(raw, f"chainlink cardinality mismatch {ln}!={rn}")
        if ln == rn and ln > 1:
            flow = flows[0]
            for k in range(ln):
                if atoms:
                    out_flows.append(flow)
                atoms.append(_atom(proto[0]["dell"], proto[0]["members"][k], label, "chainlink"))
                out_flows.append(flow)
                atoms.append(_atom(proto[1]["dell"], proto[1]["members"][k], label, "chainlink"))
            return Seed(atoms=atoms, flows=out_flows, label=label, raw=raw, ok=True)

    for i, item in enumerate(proto):
        members = item["members"]
        origin = "chain" if len(members) > 1 else "atom"
        for j, term in enumerate(members):
            if atoms:
                if j == 0 and i > 0:
                    out_flows.append(flows[i - 1])
                else:
                    out_flows.append(">")
            atoms.append(_atom(item["dell"], term, label, origin))
    return Seed(atoms=atoms, flows=out_flows, label=label, raw=raw, ok=True)

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


def define_cell(name: str, seed_text: str) -> Seed:
    text = seed_text or ""
    if "{{" in text or text.startswith("__cell__:"):
        CELLS[str(name)] = text
        return Seed(ok=True, raw=text)
    s = parse_seed(text)
    if s.ok:
        CELLS[str(name)] = text
    return s


def link_cell(name: str, target: str) -> None:
    CELLS[str(name)] = "__cell__:" + str(target)


def expand_cell(name: str, seen=None, depth: int = 0) -> Seed:
    raw = CELLS.get(str(name))
    if raw is None:
        return Seed(ok=False, error=f"unknown cell {name}", raw="")
    if depth > CELL_DEPTH:
        return Seed(ok=False, error="cell_depth", raw=str(name))
    seen = set(seen or [])
    key = str(name)
    if key in seen:
        return Seed(ok=False, error="cell_cycle", raw=key)
    seen.add(key)
    if raw.startswith("__cell__:"):
        return expand_cell(raw.split(":", 1)[1], seen, depth + 1)
    def _sub(m):
        inner = expand_cell(m.group(1), seen, depth + 1)
        if not inner.ok:
            raise ValueError(inner.error or "cell_expand")
        return inner.as_mandel()
    try:
        raw2 = re.sub(r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}", _sub, raw)
    except ValueError as e:
        return Seed(ok=False, error=str(e), raw=raw)
    return parse_seed(raw2)


def compression_report(verbose: str, compressed: str) -> Dict[str, Any]:
    v, c = parse_seed(verbose), parse_seed(compressed)
    v_atoms = [a.dell for a in v.atoms]
    c_atoms = [a.dell for a in c.atoms]
    v_terms = [a.term for a in v.atoms]
    c_terms = [a.term for a in c.atoms]
    v_len, c_len = len(verbose), len(compressed)
    pct = 0.0 if v_len == 0 else round(100.0 * (1.0 - (c_len / v_len)), 2)
    return {
        "ok": v.ok and c.ok,
        "equivalent": v.ok and c.ok and v_atoms == c_atoms and v_terms == c_terms,
        "verbose_chars": v_len,
        "compressed_chars": c_len,
        "verbose_atoms": len(v.atoms),
        "compressed_atoms": len(c.atoms),
        "compression_percent": pct,
        "positive": pct > 0,
    }
