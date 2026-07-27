#!/usr/bin/env python3
"""
14_TOKEN_WORKMEM.py
Code Phase 3 · Artifact 14
Status: TRUE
Offline · Zero dependencies · Stdlib only

Grows from page 09 Memory / RAG practical fold:
- Work memory (what ran, failed, corrections) preferred
- Context budget / chunking helpers
- Lightweight work-context graph (seed · file · correction + Bind edges)
- Law: never answer only from summary when raw exists
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import time
import hashlib

# ---------- Token Budget ----------

@dataclass
class TokenBudget:
    """
    Simple offline token counter and budget gate.
    Does not call any external tokenizer — uses rough char/4 heuristic
    or an injected counter for tests.
    """
    limit: int = 4096
    used: int = 0
    reserved: int = 0          # reserved for system / seed strip

    def estimate(self, text: str) -> int:
        """Rough offline estimate (chars / 4). Replace later if needed."""
        return max(1, len(text) // 4)

    def can_afford(self, text: str) -> bool:
        return (self.used + self.reserved + self.estimate(text)) <= self.limit

    def charge(self, text: str) -> bool:
        cost = self.estimate(text)
        if self.used + self.reserved + cost > self.limit:
            return False
        self.used += cost
        return True

    def reset(self) -> None:
        self.used = 0

    def remaining(self) -> int:
        return max(0, self.limit - self.used - self.reserved)

    def status(self) -> Dict[str, int]:
        return {
            "limit": self.limit,
            "used": self.used,
            "reserved": self.reserved,
            "remaining": self.remaining(),
        }

# ---------- Work Memory ----------

class MemKind(Enum):
    RUN        = auto()   # what executed
    FAIL       = auto()   # what failed
    CORRECTION = auto()   # what was fixed
    ARTIFACT   = auto()   # produced file / object
    NOTE       = auto()   # free cognitive note

@dataclass
class WorkEntry:
    kind: MemKind
    content: str
    source: str = ""          # traceable origin
    raw: Optional[str] = None # prefer raw over summary
    timestamp: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)

@dataclass
class WorkMemory:
    """
    Main-matrix work/coherence memory.
    Preference/taste profiles stay out (personal matrix only).
    """
    entries: List[WorkEntry] = field(default_factory=list)
    max_entries: int = 256

    def add(self, kind: MemKind, content: str, source: str = "",
            raw: Optional[str] = None, tags: Optional[List[str]] = None) -> WorkEntry:
        e = WorkEntry(
            kind=kind,
            content=content,
            source=source,
            raw=raw or content,
            tags=tags or [],
        )
        self.entries.append(e)
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        return e

    def recent(self, n: int = 10, kind: Optional[MemKind] = None) -> List[WorkEntry]:
        items = self.entries if kind is None else [e for e in self.entries if e.kind == kind]
        return items[-n:]

    def failures(self, n: int = 5) -> List[WorkEntry]:
        return self.recent(n, MemKind.FAIL)

    def corrections(self, n: int = 5) -> List[WorkEntry]:
        return self.recent(n, MemKind.CORRECTION)

# ---------- Work Context Graph ----------

@dataclass
class GraphNode:
    id: str
    kind: str                 # seed | file | correction | artifact
    label: str
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GraphEdge:
    src: str
    dst: str
    relation: str             # caused | fixed | derived-from | bind

@dataclass
class WorkGraph:
    """
    Lightweight offline graph.
    Nodes: seed · file · correction · artifact
    Edges: Bind-style relations
    """
    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    edges: List[GraphEdge] = field(default_factory=list)

    def _id(self, kind: str, label: str) -> str:
        h = hashlib.sha1(f"{kind}:{label}".encode()).hexdigest()[:10]
        return f"{kind}_{h}"

    def add_node(self, kind: str, label: str, **data) -> GraphNode:
        nid = self._id(kind, label)
        if nid not in self.nodes:
            self.nodes[nid] = GraphNode(id=nid, kind=kind, label=label, data=data)
        else:
            self.nodes[nid].data.update(data)
        return self.nodes[nid]

    def bind(self, src_label: str, dst_label: str,
             src_kind: str = "seed", dst_kind: str = "artifact",
             relation: str = "bind") -> GraphEdge:
        src = self.add_node(src_kind, src_label)
        dst = self.add_node(dst_kind, dst_label)
        edge = GraphEdge(src=src.id, dst=dst.id, relation=relation)
        self.edges.append(edge)
        return edge

    def neighbors(self, node_id: str) -> List[Tuple[GraphEdge, GraphNode]]:
        out = []
        for e in self.edges:
            if e.src == node_id and e.dst in self.nodes:
                out.append((e, self.nodes[e.dst]))
            elif e.dst == node_id and e.src in self.nodes:
                out.append((e, self.nodes[e.src]))
        return out

    def status(self) -> Dict[str, int]:
        return {"nodes": len(self.nodes), "edges": len(self.edges)}

# ---------- Combined helper ----------

@dataclass
class TokenWorkMem:
    """Single entry point for budget + work memory + graph."""
    budget: TokenBudget = field(default_factory=TokenBudget)
    memory: WorkMemory = field(default_factory=WorkMemory)
    graph: WorkGraph = field(default_factory=WorkGraph)

    def record_run(self, content: str, source: str = "") -> None:
        self.memory.add(MemKind.RUN, content, source=source)

    def record_fail(self, content: str, source: str = "") -> None:
        self.memory.add(MemKind.FAIL, content, source=source)

    def record_correction(self, content: str, source: str = "") -> None:
        self.memory.add(MemKind.CORRECTION, content, source=source)

    def link(self, src: str, dst: str, relation: str = "derived-from") -> None:
        self.graph.bind(src, dst, relation=relation)

    def status(self) -> Dict[str, Any]:
        return {
            "budget": self.budget.status(),
            "memory_entries": len(self.memory.entries),
            "recent_fails": [e.content for e in self.memory.failures(3)],
            "graph": self.graph.status(),
        }

# ---------- Demo ----------

def demo():
    tw = TokenWorkMem()
    tw.budget.limit = 512

    text = "08[Create] >> 14[Bind] :: demo seed"
    print("Can afford?", tw.budget.can_afford(text))
    tw.budget.charge(text)
    print("Budget:", tw.budget.status())

    tw.record_run("Artifact 14 created", source="NBD")
    tw.record_fail("Earlier dual-source attempt rejected", source="Gate")
    tw.record_correction("Folded only non-clashing forms", source="Architect")
    tw.link("Artifact 14", "page 09 Memory fold", relation="derived-from")

    print("Status:", tw.status())
    print("Recent corrections:", [e.content for e in tw.memory.corrections()])

if __name__ == "__main__":
    demo()
