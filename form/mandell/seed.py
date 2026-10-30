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
# TOAM-I: argument list after atom: (role="value", role2="value2")
_ARGS = re.compile(r'\(\s*([A-Za-z_][A-Za-z0-9_]*\s*=\s*"[^"]*"\s*(?:,\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*"[^"]*"\s*)*)\)')
_ARG_PAIR = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"([^"]*)"')
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
    # TOAM-I: typed role/value arguments. Empty dict = no arguments (backward compat).
    args: Dict[str, str] = field(default_factory=dict)
    # AF-2: this atom's own segment label (the ":: label" written
    # directly after this atom in a multi-segment seed). Empty when
    # the segment carried no label; consumers fall back to Seed.label
    # (the LAST segment's label) — see chain_exec._eff_label.
    label: str = ""
    def as_mandel(self) -> str:
        width = 3 if self.dell > 99 else 2
        shown = self.resolved_term or self.term
        s = f"{self.dell:0{width}d}[{shown}]"
        if self.args:
            pairs = ", ".join(f'{k}="{v}"' for k, v in self.args.items())
            s += f"({pairs})"
        return s
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
        # AF-2: when a NON-final atom carries its own segment label,
        # reconstruct segment-first (each label stays with its atom)
        # so the string round-trips through parse_seed unchanged.
        # Otherwise keep the historical shape: one trailing label.
        if any(a.label for a in self.atoms[:-1]):
            parts = []
            for i, atom in enumerate(self.atoms):
                if i:
                    flow = self.flows[i - 1] if i - 1 < len(self.flows) else ">"
                    parts.append(f" {flow} ")
                s = atom.as_mandel()
                if atom.label:
                    s += f" :: {atom.label}"
                parts.append(s)
            return "".join(parts)
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


def _atom(n: int, term: str, label: str, origin: str, args: Optional[Dict[str, str]] = None, seg_label: str = "") -> SeedAtom:
    resolved, conf, reason = _resolve_term(n, term, label)
    return SeedAtom(
        dell=n, term=term, resolved_term=resolved,
        confidence=conf, resolve_reason=reason, origin=origin,
        args=args or {}, label=seg_label,
    )


def _scan_label_end(body: str, start: int) -> tuple:
    """AF-2 segment rule (same authority as flow_executor
    ._tokenize_program): a label ends at the next flow operator
    that is followed by an atom, or at end of text. Flow operators
    NOT followed by an atom are label DATA (e.g. Cause's
    'rain > flood'). A second '::' inside a label is an embedded
    label marker, not data: returns (embedded_index, -1) style
    signal via the second element. Returns (end, embedded) with
    exactly one of them >= 0 meaningful: end >= 0 is the label
    end; embedded >= 0 is the position of the inner '::'."""
    i = start
    n = len(body)
    while i < n:
        m = _FLOW.match(body, i)
        if m:
            op = m.group(0)
            after = m.end()
            while after < n and body[after].isspace():
                after += 1
            if _ATOM.match(body, after):
                return i, -1
            if op == "::":
                return -1, i
            i = m.end()
            continue
        i += 1
    return n, -1


def parse_seed(text: str) -> Seed:
    raw = (text or "").strip()
    if not raw:
        return _fail(raw, "empty")
    # AF-2: segment-first parsing. Each atom segment is
    #   atom [args] ["::" label]
    # where the label ends at the next flow operator followed by
    # an atom (flow_executor._tokenize_program's rule — ONE segment
    # authority, not two). A "::" followed by an atom is the
    # DeepFlowBy flow operator, never a label marker. Seed.label is
    # the LAST segment's label (single-atom seeds are unchanged).
    body = raw
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
            pos = m.end()
            # TOAM-I: parse optional argument list (role="value", ...)
            args: Dict[str, str] = {}
            am = _ARGS.match(body, pos)
            if am:
                for pair in _ARG_PAIR.finditer(am.group(1)):
                    args[pair.group(1)] = pair.group(2)
                pos = am.end()
            # AF-2: optional segment label.
            seg_label = ""
            p2 = pos
            while p2 < body_len and body[p2].isspace():
                p2 += 1
            if body[p2:p2 + 2] == "::":
                after = p2 + 2
                while after < body_len and body[after].isspace():
                    after += 1
                if not _ATOM.match(body, after):
                    end, embedded = _scan_label_end(body, p2 + 2)
                    if embedded >= 0:
                        if not body[p2 + 2:embedded].strip():
                            return _fail(raw, "too many flow operators")
                        return _fail(raw, f"unexpected at {after}: {body[after:after + 12]!r}")
                    seg_label = body[p2 + 2:end].strip()
                    if not seg_label:
                        return _fail(raw, "too many flow operators")
                    pos = end
            proto.append({"dell": n, "members": members,
                          "args": args, "label": seg_label})
            last_was_atom = True
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
    label = proto[-1]["label"]
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
                atoms.append(_atom(proto[0]["dell"], proto[0]["members"][k], proto[0]["label"] or label, "chainlink", proto[0].get("args", {}), proto[0]["label"]))
                out_flows.append(flow)
                atoms.append(_atom(proto[1]["dell"], proto[1]["members"][k], proto[1]["label"] or label, "chainlink", proto[1].get("args", {}), proto[1]["label"]))
            return Seed(atoms=atoms, flows=out_flows, label=label, raw=raw, ok=True)

    for i, item in enumerate(proto):
        members = item["members"]
        origin = "chain" if len(members) > 1 else "atom"
        item_args = item.get("args", {})
        for j, term in enumerate(members):
            if atoms:
                if j == 0 and i > 0:
                    out_flows.append(flows[i - 1])
                else:
                    out_flows.append(">")
            atoms.append(_atom(item["dell"], term, item["label"] or label, origin, item_args, item["label"]))
    return Seed(atoms=atoms, flows=out_flows, label=label, raw=raw, ok=True)

def looks_like_seed(text: str) -> bool:
    return bool(_ATOM.search(text or ""))

def explain_seed(text: str) -> Dict[str, Any]:
    s = parse_seed(text)
    return {"ok": s.ok, "error": s.error, "mandel": s.as_mandel() if s.ok else "", "english": s.as_english() if s.ok else "", "atoms": [{"dell": a.dell, "term": a.term, "resolved": a.resolved_term, "confidence": a.confidence, "reason": a.resolve_reason} for a in s.atoms], "label": s.label, "raw": s.raw}


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
