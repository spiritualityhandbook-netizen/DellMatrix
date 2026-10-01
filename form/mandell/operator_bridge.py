#!/usr/bin/env python3
"""CAC-I: Generalized operator resolution bridge (NBD-Ω-003).

ONE bridge. Registry-driven. No 49-case routing table. No new executor.

The bridge resolves canonical operator identity from EXISTING registry
metadata (registry.get_dell / registry.lookup / core_ii.contract) and
routes execution through EXISTING authority:

  Core-II  -> chain_exec.execute_chain > core_ii_exec.execute_core_ii
  Core-I   -> the existing CORRESPONDENCE entries via route_intent (unchanged)

Resolution order (Core-I nonregression by construction):
  1. CORRESPONDENCE hit -> delegate to route_intent, byte-for-byte unchanged.
  2. Core-II (51-99)    -> generalized registry resolution + execute_chain.
  3. Core-I without a correspondence entry -> legacy no-route refusal.
  4. Unknown / ambiguous / malformed / blocked -> explicit refusal.

The bridge chooses/accesses authority. It never becomes authority.

Fail-closed law: unknown operator, ambiguous operator, malformed flow,
blocked operator, and unsupported composition all produce a refusal
receipt. Nothing executes. Malformed syntax is never reinterpreted as
another operator.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from . import registry
from .core_ii import CORE_II

# --- Classification (verified against query_ops / spectrum_ops, 2026-10-01) ---

# Destructive session-store mutation. English access deferred pending an
# operand-confirmation policy. Raw Mandell executes them today.
BLOCKED_WITH_REASON = {86, 87, 88}
_BLOCK_REASONS = {
    86: "destructive store mutation via English composition is deferred "
        "pending operand-confirmation policy; raw Mandell only",
    87: "destructive store mutation via English composition is deferred "
        "pending operand-confirmation policy; raw Mandell only",
    88: "destructive store mutation via English composition is deferred "
        "pending operand-confirmation policy; raw Mandell only",
}

# Recursive higher-order program execution from English is a policy
# boundary, not a technical gap. Raw Mandell only, by design.
INTENTIONALLY_RAW_ONLY = {99}
_RAW_ONLY_REASONS = {
    99: "higher-order program composition from English is intentionally "
        "raw-Mandell-only by policy",
}

BRIDGE_VERSION = 1


@dataclass
class Resolution:
    """Identity resolution result. No execution performed."""
    ok: bool
    dell: Optional[int] = None
    name: str = ""
    namespace: str = ""
    authority: str = ""          # "correspondence" | "execute_chain>execute_core_ii"
    refusal_reason: str = ""     # set when not ok
    candidates: List[int] = field(default_factory=list)  # ambiguity only


@dataclass
class BridgeReceipt:
    """Structured evidence for a bridge routing attempt.

    Carries the RouteReceipt attribute shape (action, mandell, dell,
    semantic, input, routed, ok, error, messages, state_note) so the
    EXISTING outcome_ledger.capture_outcome can observe bridge executions
    without a parallel receipt system.
    """
    requested_action: str = ""
    requested_dell: Optional[int] = None
    requested_term: str = ""
    resolved_dell: Optional[int] = None
    resolved_name: str = ""
    namespace: str = ""
    authority: str = ""
    # RouteReceipt-compatible fields:
    action: str = ""
    mandell: str = ""
    dell: Optional[int] = None
    semantic: str = ""
    input: str = ""
    routed: bool = False
    ok: bool = False
    error: str = ""
    messages: List[str] = field(default_factory=list)
    state_note: str = ""
    seed: str = ""               # canonical Mandell executed ("" if none)
    refusal_reason: str = ""
    candidates: List[int] = field(default_factory=list)  # ambiguity only


def _refusal(action: str, dell: Optional[int], term: str,
             reason: str, candidates: Optional[List[int]] = None) -> BridgeReceipt:
    return BridgeReceipt(
        requested_action=action or "",
        requested_dell=dell,
        requested_term=term or "",
        action=action or "",
        dell=dell,
        input=term or "",
        routed=False,
        ok=False,
        error=reason,
        state_note="no state change (not routed)",
        refusal_reason=reason,
        candidates=list(candidates or []),
    )


def resolve(action: Optional[str] = None,
            dell: Optional[int] = None,
            term: Optional[str] = None) -> Resolution:
    """Resolve canonical operator identity from existing registry metadata.

    Identity only — no execution. Fail-closed on unknown/ambiguous.
    """
    from .semantic_router import CORRESPONDENCE

    act = (action or "").strip()
    trm = (term or "").strip()

    # 1. Existing correspondence wins (Core-I specialized behavior preserved).
    if act and dell is not None and (act, dell) in CORRESPONDENCE:
        corr = CORRESPONDENCE[(act, dell)]
        return Resolution(ok=True, dell=dell, name=corr.dell_name,
                          namespace="CORE_I", authority="correspondence")

    # 2. Registry-driven identity.
    rec = None
    if dell is not None:
        try:
            n = int(dell)
        except (TypeError, ValueError):
            return Resolution(ok=False, refusal_reason="unknown_operator: bad dell")
        rec = registry.get_dell(n)
        if rec is None:
            return Resolution(ok=False, refusal_reason="unknown_operator: no such dell")
    elif trm:
        rec = registry.lookup(trm)
        if rec is None:
            # Try manifest-word match for Core-II English terms.
            rec = _manifest_lookup(trm)
        if rec is None:
            return Resolution(ok=False, refusal_reason="unknown_operator")
    else:
        return Resolution(ok=False, refusal_reason="unknown_operator: empty request")

    n = int(rec["dell"])
    ns = str(rec.get("namespace", ""))
    name = str(rec.get("name", ""))

    if ns == "CORE_II":
        if n in BLOCKED_WITH_REASON:
            return Resolution(ok=False, dell=n, name=name, namespace=ns,
                              refusal_reason="blocked_with_reason: " + _BLOCK_REASONS[n])
        if n in INTENTIONALLY_RAW_ONLY:
            return Resolution(ok=False, dell=n, name=name, namespace=ns,
                              refusal_reason="intentionally_raw_only: " + _RAW_ONLY_REASONS[n])
        return Resolution(ok=True, dell=n, name=name, namespace=ns,
                          authority="execute_chain>execute_core_ii")
    if ns == "CORE_I":
        # No correspondence entry -> legacy refusal. Never generalized:
        # the DCC-II Semantic Safety Law keeps Core-I on the allowlist.
        return Resolution(ok=False, dell=n, name=name, namespace=ns,
                          refusal_reason="no verified correspondence "
                                         f"for ({act!r}, Dell {n}) — refusing to guess")
    status = str(rec.get("status", "") or "unknown")
    return Resolution(ok=False, dell=n, name=name, namespace=ns,
                      refusal_reason=f"operator {n} is {status}, not executable")


def _manifest_lookup(term: str) -> Optional[Dict[str, Any]]:
    """Single-word manifest lookup with collision -> None (ambiguous)."""
    w = term.strip().lower()
    hits = []
    for n, row in CORE_II.items():
        words = {str(row["name"]).lower()} | {str(x).lower() for x in row["manifests"]}
        if w in words:
            hits.append(n)
    if len(hits) == 1:
        return registry.get_dell(hits[0])
    return None


def route(program: Any,
          action: Optional[str] = None,
          dell: Optional[int] = None,
          term: Optional[str] = None,
          label: str = "",
          raw_line: str = "") -> BridgeReceipt:
    """Resolve and execute through EXISTING authority. Fail-closed."""
    from .semantic_router import CORRESPONDENCE, route_intent

    act = (action or "").strip()
    trm = (term or "").strip()
    lab = (label or "").strip()

    # Correspondence path: unchanged behavior, unchanged receipts.
    if act and dell is not None:
        try:
            dn = int(dell)
        except (TypeError, ValueError):
            dn = None
        if dn is not None and (act, dn) in CORRESPONDENCE:
            return route_intent(program, _intent(act, dn, trm, lab, raw_line),
                                raw_line=raw_line)

    res = resolve(action=act or None, dell=dell, term=trm or None)
    if not res.ok:
        return _refusal(act, dell, trm, res.refusal_reason,
                        candidates=res.candidates)

    # Generalized Core-II path: canonical seed -> existing chain authority.
    from .seed import parse_seed
    from .chain_exec import execute_chain

    seed_text = f"{res.dell:02d}[{res.name}]"
    if lab:
        seed_text += f" :: {lab}"
    seed = parse_seed(seed_text)
    if not seed.ok:
        return _refusal(act, res.dell, trm, f"malformed_program: {seed.error}")

    try:
        out = execute_chain(program, seed, seed_text)
    except Exception as exc:  # fail safe: report, do not propagate
        return BridgeReceipt(
            requested_action=act, requested_dell=res.dell, requested_term=trm,
            resolved_dell=res.dell, resolved_name=res.name,
            namespace=res.namespace, authority=res.authority,
            action=act, mandell=seed_text, dell=res.dell,
            semantic=f"{act}[{res.name}]", input=raw_line or trm,
            routed=False, ok=False, error=f"Dell execution raised: {exc}",
            state_note="no state change (execution raised)", seed=seed_text,
            refusal_reason=f"Dell execution raised: {exc}",
        )

    messages = list(out.get("messages") or [])
    ok = bool(out.get("ok", False))
    receipt = BridgeReceipt(
        requested_action=act, requested_dell=res.dell, requested_term=trm,
        resolved_dell=res.dell, resolved_name=res.name,
        namespace=res.namespace, authority=res.authority,
        action=act, mandell=seed_text, dell=res.dell,
        semantic=f"{act}[{res.name}]", input=raw_line or trm,
        routed=True, ok=ok,
        error="" if ok else (out.get("error") or "Dell execution failed"),
        messages=messages,
        state_note="; ".join(messages[-3:]) if messages else ("executed" if ok else "failed"),
        seed=seed_text,
    )
    # Outcome V1 observation through the EXISTING ledger (no parallel system).
    # nurture_fresh=False: Core-II arms do not populate last_nurture, so
    # knowledge/conflict provenance is honestly empty — the Outcome V1
    # boundary documented in Phase K.
    try:
        from .outcome_ledger import capture_outcome
        capture_outcome(program, receipt, nurture_fresh=False)
    except Exception:
        pass
    return receipt


def _intent(action: str, dell: int, term: str, label: str, raw_line: str):
    """Minimal Intent-shaped object for the correspondence delegation."""
    from .translate import Intent
    mandel = f"{dell:02d}[{term or action}]"
    if label:
        mandel += f" :: {label}"
    return Intent(action=action, dell=dell, term=term or action,
                  args={}, mandel=mandel, english=raw_line or mandel)


# --- English access: ONE registry-driven matcher, not 49 handlers ---

import re as _re

_WORD = _re.compile(r"[a-z0-9]+")


def _operator_words(n: int) -> set:
    row = CORE_II[n]
    return {str(row["name"]).lower()} | {str(w).lower() for w in row["manifests"]}


def english_to_intent(english: str):
    """English -> Intent via registry manifests. Fail-closed.

    Returns (Intent, "", []) on success, (None, reason, candidates)
    on refusal. Candidates is non-empty only for ambiguity.
    """
    from .translate import Intent

    text = (english or "").strip()
    if not text:
        return None, "empty input", []
    tokens = set(_WORD.findall(text.lower()))
    if not tokens:
        return None, "empty input", []

    scored = []
    for n in range(51, 100):
        hits = _operator_words(n) & tokens
        if hits:
            scored.append((len(hits), n, sorted(hits)))
    if not scored:
        return None, "unknown_operator", []
    scored.sort(key=lambda t: (-t[0], t[1]))
    top = scored[0][0]
    winners = [s for s in scored if s[0] == top]
    if len(winners) > 1:
        cands = sorted(s[1] for s in winners)
        return None, f"ambiguous_operator: candidates {cands}", cands
    _, n, hits = winners[0]
    if n in BLOCKED_WITH_REASON:
        return None, "blocked_with_reason: " + _BLOCK_REASONS[n], []
    if n in INTENTIONALLY_RAW_ONLY:
        return None, "intentionally_raw_only: " + _RAW_ONLY_REASONS[n], []

    # Label: text after the first matched operator word.
    first = min((text.lower().find(w) for w in hits if text.lower().find(w) >= 0),
                default=-1)
    label = ""
    if first >= 0:
        rest = text[first:]
        rest = _re.sub(r"^[a-z0-9]+", "", rest, count=1).strip()
        rest = _re.sub(r"^(the|a|an|of|to|for|with|on|in)\s+", "", rest).strip()
        label = rest[:120]
    name = CORE_II[n]["name"]
    action = hits[0]
    mandel = f"{n:02d}[{name}]"
    return Intent(action=action, dell=n, term=name, args={"label": label},
                  mandel=mandel, english=text), "", []


def execute_english(program: Any, english: str) -> BridgeReceipt:
    """English -> canonical identity -> existing execution authority."""
    intent, err, candidates = english_to_intent(english)
    if intent is None:
        return _refusal("", None, english, err, candidates=candidates)
    label = str((intent.args or {}).get("label", ""))
    return route(program, action=intent.action, dell=intent.dell,
                 term=intent.term, label=label, raw_line=english)


def compose_execute(program: Any, mandell_program: str) -> Dict[str, Any]:
    """Modern composition delegating to EXISTING chain_exec runtime.

    Full multi-atom programs with all nine flow operators execute with the
    tested chain_exec semantics. Malformed programs fail closed.
    This does not replace flow_executor (existing behavior preserved);
    it is the converged composition path.
    """
    from .seed import parse_seed
    from .chain_exec import execute_chain

    raw = (mandell_program or "").strip()
    if not raw:
        return {"ok": False, "error": "empty_program", "routed": False,
                "messages": []}
    seed = parse_seed(raw)
    if not seed.ok:
        return {"ok": False, "error": f"malformed_program: {seed.error}",
                "routed": False, "messages": []}
    # Bridge boundary: fail closed on unknown dells. The underlying
    # chain_exec leniently skips reserved/not-active dells; the bridge
    # composition entry refuses them instead. Existing raw-Mandell
    # behavior is untouched.
    for atom in seed.atoms:
        try:
            an = int(atom.dell)
        except (TypeError, ValueError):
            return {"ok": False, "error": "malformed_program: bad dell",
                    "routed": False, "messages": []}
        if registry.get_dell(an) is None:
            return {"ok": False, "error": f"unknown_dell:{an}",
                    "routed": False, "messages": []}
    try:
        out = execute_chain(program, seed, raw)
    except Exception as exc:
        return {"ok": False, "error": f"Dell execution raised: {exc}",
                "routed": False, "messages": []}
    out["routed"] = True
    # Outcome V1 observation per composed program (existing ledger).
    try:
        from .outcome_ledger import capture_outcome
        receipt = BridgeReceipt(
            action="compose", mandell=raw, dell=seed.primary_dell(),
            semantic="compose", input=raw, routed=True,
            ok=bool(out.get("ok", False)),
            error="" if out.get("ok") else (out.get("error") or ""),
            messages=list(out.get("messages") or []),
            state_note="composed execution",
            seed=raw,
        )
        capture_outcome(program, receipt,
                        composition={"flow_program": raw, "node_index": 0},
                        nurture_fresh=False)
    except Exception:
        pass
    return out
