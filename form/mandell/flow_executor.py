#!/usr/bin/env python3
"""DCC-IV: Composed Mandell program execution via verified flow operators.

Executes multiple semantic operations as one ordered program:
  INPUT > MANDELL PARSE > FLOW STRUCTURE > SEMANTIC NODES > VERIFIED ROUTER > DELL EXECUTION

Flow operators use existing Mandell authority (control_runtime.FLOW_CONTRACT):
  >   FlowTo   : sequential, always run next (EXECUTABLE_NOW)
  >>  FlowThru : blocking, skip next if prev failed (EXECUTABLE_NOW)

Other operators (>>>, :, ::, :>, <:, <:>, <<[Delta]) are classified as
REQUIRES_RUNTIME_SUPPORT, DESCRIPTIVE_ONLY, or UNSAFE and are refused.

The program is tokenized using the seed parser's _ATOM and _FLOW patterns
(not naive string split). Each node is validated by the real parse_seed.
Execution order comes from the parser's token structure.
Each node routes through the verified semantic_router (route_intent).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .seed import parse_seed, _ATOM, _FLOW
from .semantic_router import CORRESPONDENCE, route_intent

# Flow operators with executable semantics (from Mandell authority).
EXECUTABLE_FLOWS = {">", ">>"}

# Classification of all Mandell flow operators (from control_runtime.FLOW_CONTRACT).
FLOW_CLASSIFICATION = {
    ">": "EXECUTABLE_NOW",
    ">>": "EXECUTABLE_NOW",
    ">>>": "REQUIRES_RUNTIME_SUPPORT",
    ":": "DESCRIPTIVE_ONLY",
    "::": "DESCRIPTIVE_ONLY",
    ":>": "DESCRIPTIVE_ONLY",
    "<:": "DESCRIPTIVE_ONLY",
    "<:>": "UNSAFE/AMBIGUOUS",
    "<<[Delta]": "REQUIRES_RUNTIME_SUPPORT",
}


def _dell_to_action() -> Dict[int, str]:
    """Reverse lookup: Dell number -> semantic action (from verified CORRESPONDENCE)."""
    return {dell: action for (action, dell) in CORRESPONDENCE.keys()}


def _args_from_label(action: str, label: str) -> Dict[str, Any]:
    """Build typed args from a node's Mandell label."""
    label = (label or "").strip()
    if action == "stamp":
        return {"mark": label[:48] if label else "mark"}
    if action == "cycle":
        try:
            n = int(label)
            n = max(1, min(99, n))
        except (ValueError, TypeError):
            n = 1
        return {"count": n}
    if action == "form":
        f = label.lower() if label else "cube"
        if f not in ("cube", "sphere", "core", "flower"):
            f = "cube"
        return {"form": f}
    return {}


@dataclass
class FlowNode:
    mandel: str
    action: str
    dell: int
    term: str
    args: Dict[str, Any]


@dataclass
class FlowProgram:
    raw: str
    nodes: List[FlowNode]
    flows: List[str]


@dataclass
class StepResult:
    index: int
    mandel: str
    action: str
    dell: int
    arguments: Dict[str, Any]
    ok: bool
    error: str
    messages: List[str]
    skipped: bool = False
    skip_reason: str = ""


@dataclass
class FlowReceipt:
    program: str
    flows: List[str]
    steps: List[StepResult]
    completed: int
    failed: int
    skipped: int
    final_program: Any = None  # Updated program (e.g., after Dell 28 rollback).

    @property
    def ok(self) -> bool:
        return self.failed == 0


def _tokenize_program(raw: str):
    """Tokenize into (node_texts, flow_ops) using parser patterns.

    Distinguishes label-`::` (followed by non-atom) from flow-`::`
    (followed by atom). Not a naive split.
    """
    nodes_raw: List[str] = []
    flows: List[str] = []
    pos = 0
    n = len(raw)

    def skip_ws(p):
        while p < n and raw[p].isspace():
            p += 1
        return p

    pos = skip_ws(pos)
    while pos < n:
        pos = skip_ws(pos)
        # Expect atom.
        am = _ATOM.match(raw, pos)
        if not am:
            raise ValueError(f"expected Dell atom at {pos}: {raw[pos:pos+20]!r}")
        atom_start = pos
        pos = am.end()

        # Optional :: label (only if NOT followed by atom).
        node_end = pos
        p2 = skip_ws(pos)
        if raw[p2:p2+2] == "::":
            after = skip_ws(p2 + 2)
            if _ATOM.match(raw, after):
                # Flow ::, not a label. Leave for flow parsing.
                pass
            else:
                # Label ::. Find where label ends: next flow op followed by atom, or end.
                label_end = n
                for fm in _FLOW.finditer(raw, after):
                    op_end = fm.end()
                    if _ATOM.match(raw, skip_ws(op_end)):
                        label_end = fm.start()
                        break
                node_end = label_end
                pos = label_end

        node_text = raw[atom_start:node_end].strip()
        pos = skip_ws(pos)

        if pos >= n:
            nodes_raw.append(node_text)
            break

        # Expect flow operator.
        fm = _FLOW.match(raw, pos)
        if not fm:
            raise ValueError(f"expected flow at {pos}: {raw[pos:pos+20]!r}")
        op = fm.group(0)
        if op not in EXECUTABLE_FLOWS:
            cls = FLOW_CLASSIFICATION.get(op, "UNKNOWN")
            raise ValueError(f"flow '{op}' is {cls}, not executable")
        # Must be followed by atom.
        if not _ATOM.match(raw, skip_ws(fm.end())):
            raise ValueError(f"flow '{op}' not followed by atom")
        flows.append(op)
        nodes_raw.append(node_text)
        pos = fm.end()

    if len(nodes_raw) != len(flows) + 1:
        raise ValueError(f"malformed: {len(nodes_raw)} nodes, {len(flows)} flows")
    return nodes_raw, flows


def parse_program(raw: str) -> FlowProgram:
    """Parse a composed Mandell program via the real parser."""
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("empty program")
    nodes_raw, flows = _tokenize_program(raw)
    dell_to_action = _dell_to_action()
    nodes: List[FlowNode] = []
    for node_text in nodes_raw:
        seed = parse_seed(node_text)
        if not seed.ok:
            raise ValueError(f"node parse failed {node_text!r}: {seed.error}")
        if len(seed.atoms) != 1:
            raise ValueError(f"node must be single atom: {node_text!r}")
        dell = seed.primary_dell()
        action = dell_to_action.get(dell)
        if action is None:
            raise ValueError(f"Dell {dell} has no verified correspondence: {node_text!r}")
        term = getattr(seed.atoms[0], "term", "") or ""
        args = _args_from_label(action, seed.label)
        nodes.append(FlowNode(mandel=node_text, action=action, dell=dell, term=term, args=args))
    return FlowProgram(raw=raw, nodes=nodes, flows=flows)


def execute_program(program: Any, flow_program: FlowProgram) -> FlowReceipt:
    """Execute via the verified semantic router. Flow: > always, >> blocks on fail."""
    from form.mandell.translate import Intent

    steps: List[StepResult] = []
    completed = 0
    failed = 0
    skipped = 0
    prev_ok = True
    cur = program

    for i, node in enumerate(flow_program.nodes):
        if i > 0 and flow_program.flows[i - 1] == ">>" and not prev_ok:
            steps.append(StepResult(
                index=i + 1, mandel=node.mandel, action=node.action, dell=node.dell,
                arguments=dict(node.args), ok=False, error="", messages=[],
                skipped=True, skip_reason="FlowThru blocked after previous failure",
            ))
            skipped += 1
            prev_ok = False
            continue

        intent = Intent(action=node.action, dell=node.dell, term=node.term,
                        args=node.args, mandel=node.mandel, english=node.mandel)
        # DCC-XX: pass flow composition context so each node outcome records
        # which composed program and node index it belongs to. Additive only;
        # routing behavior unchanged.
        receipt = route_intent(cur, intent, raw_line=node.mandel,
                               composition={"flow_program": flow_program.raw,
                                            "node_index": i})
        if receipt.new_program is not None:
            cur = receipt.new_program
        step_ok = bool(receipt.ok and receipt.routed)
        # DCC-VI: log to program history for TRACE capability.
        # Uses existing note_seed authority; does not change Dell behavior.
        if hasattr(cur, "note_seed"):
            try:
                label = node.mandel.split("::", 1)[1].strip() if "::" in node.mandel else ""
                cur.note_seed(node.dell, node.term, label)
            except Exception:
                pass
        steps.append(StepResult(
            index=i + 1, mandel=node.mandel, action=node.action, dell=node.dell,
            arguments=dict(node.args), ok=step_ok,
            error=receipt.error or "", messages=list(receipt.messages or []),
        ))
        if step_ok:
            completed += 1
        else:
            failed += 1
        prev_ok = step_ok

    return FlowReceipt(program=flow_program.raw, flows=list(flow_program.flows),
                       steps=steps, completed=completed, failed=failed, skipped=skipped,
                       final_program=cur)


def format_receipt(receipt: FlowReceipt) -> str:
    """Format a composite flow receipt."""
    lines = ["PROGRAM:", f"  {receipt.program}", "FLOW:",
             f"  {' '.join(receipt.flows) if receipt.flows else '(single)'}", ""]
    for s in receipt.steps:
        lines.append(f"STEP {s.index}:")
        lines.append(f"  MANDELL: {s.mandel}")
        lines.append(f"  DELL: {s.dell} [{s.action}]")
        if s.arguments:
            lines.append("  ARGUMENTS: " + ", ".join(f"{k}={v}" for k, v in s.arguments.items()))
        if s.skipped:
            lines.append(f"  RESULT: SKIPPED ({s.skip_reason})")
        else:
            lines.append(f"  RESULT: ok={s.ok}" + (f" error={s.error}" if s.error else ""))
        lines.append("")
    lines.append("FINAL:")
    lines.append(f"  completed={receipt.completed}")
    lines.append(f"  failed={receipt.failed}")
    lines.append(f"  skipped={receipt.skipped}")
    return "\n".join(lines)
