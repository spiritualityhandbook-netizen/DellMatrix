#!/usr/bin/env python3
"""
View Rooms — ported from src/snapins/view_rooms.js into form/.

Lenses only: they change HOW you look at the lattice, not the data.
growth · water · force · network · personal · shared · ancient_psalms
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

VIEW_ROOMS: Dict[str, Dict[str, Any]] = {
    "growth": {
        "id": "growth",
        "name": "Growth",
        "emoji": "🌱",
        "description": "Ideas as plants with stages",
        "theme": {"grid": "#1a2a18", "accent": "#3cb371"},
    },
    "water": {
        "id": "water",
        "name": "Water",
        "emoji": "💧",
        "description": "Ideas as streams that merge",
        "theme": {"grid": "#102030", "accent": "#38bdf8"},
    },
    "force": {
        "id": "force",
        "name": "Force",
        "emoji": "⚡",
        "description": "Forces in the voids between ideas",
        "theme": {"grid": "#2a2010", "accent": "#e6a817"},
    },
    "network": {
        "id": "network",
        "name": "Network",
        "emoji": "🕸",
        "description": "Connections and edge strength",
        "theme": {"grid": "#1a1a30", "accent": "#7c5cbf"},
    },
    "personal": {
        "id": "personal",
        "name": "Personal",
        "emoji": "◎",
        "description": "Only what you planted (local plane)",
        "theme": {"grid": "#1a2030", "accent": "#5b8def"},
    },
    "shared": {
        "id": "shared",
        "name": "Shared",
        "emoji": "◎◎",
        "description": "Ideas that resonated (shared main)",
        "theme": {"grid": "#201a28", "accent": "#e879f9"},
    },
    "ancient_psalms": {
        "id": "ancient_psalms",
        "name": "Ancient Psalms",
        "emoji": "🏺",
        "description": "Ledger lists, totals, reverse walk, short tokens (operators only)",
        "theme": {"grid": "#2a2418", "accent": "#c47c48"},
    },
}


def list_rooms() -> List[Dict[str, Any]]:
    return [dict(r) for r in VIEW_ROOMS.values()]


def get_room(room_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not room_id:
        return None
    key = room_id.lower().replace(" ", "_").strip()
    aliases = {"psalms": "ancient_psalms", "ancient": "ancient_psalms", "net": "network"}
    key = aliases.get(key, key)
    return dict(VIEW_ROOMS[key]) if key in VIEW_ROOMS else None


def filter_nodes_for_room(
    room_id: str,
    nodes: List[Dict[str, Any]],
    *,
    owner: str = "",
    scores: Optional[Dict[str, float]] = None,
    plants: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Apply view-room lens to a node list (does not mutate plane).

    Growth room (T2, workshop/theater circuit): a node's stage is
    the stage of its GrowthForce plant — the canonical growth
    authority (forces.GrowthForce plants node labels and grows
    them). Score never invents a stage. When no plant matches,
    the node carries no stage claim: stage=None with
    stage_source="unplanted" (a plant list was supplied) or
    stage_source="unavailable" (none was).

    Identity (T2 label-identity + DIR-T2-R2): a stage is
    attributed only where plant-to-node identity is PROVEN.
    plant() retains the exact identity as idea_full alongside
    the truncated display key idea=label[:80] (C-Q3), so:
    - a plant whose idea_full equals the node's full label is
      that node's plant (agreeing exact plants resolve;
      disagreeing ones report "ambiguous");
    - a legacy plant without idea_full resolves exactly only
      where its stored key equals the node's full label;
    - a plant whose idea_full differs from the node's label is
      provably another unit's plant and contributes nothing —
      an unplanted sibling never inherits its stage, even when
      it is the only node visible (DIR-T2-R2);
    - a legacy plant matching only by truncated prefix proves
      nothing, so the node reports "ambiguous" — agreeing
      stages do not prove identity (C-Q4).
    Residual limits: two distinct units sharing one identical
    full label remain one lens identity (no unit id reaches
    this boundary), and a legacy record whose stored key is
    exactly 80 chars is indistinguishable from a genuine
    80-char label under the stored-key rule.
    """
    scores = scores or {}
    room = (room_id or "growth").lower()
    if room == "personal":
        # All local plane nodes are "planted" — keep all, tag personal
        return [{**n, "view_tag": "personal"} for n in nodes]
    if room == "shared":
        # Prefer higher scores (resonance proxy)
        ranked = sorted(nodes, key=lambda n: -float(scores.get(n.get("id"), n.get("score") or 0)))
        return [{**n, "view_tag": "shared"} for n in ranked]
    if room == "growth":
        stages = ["seed", "sprout", "stem", "branch", "leaf", "fruit"]
        # Proven-identity candidates: full node label -> stages of
        # plants whose identity is proven for that exact label.
        exact_stages: Dict[str, set] = {}
        # Truncated keys carrying legacy plants (no idea_full):
        # such a plant proves identity only for a node whose full
        # label equals its stored key (handled via exact_stages);
        # for any longer label on the same key it is prefix-only.
        legacy_keys: set = set()
        if plants is not None:
            for p in plants:
                stage = str(p.get("stage") or "")
                if stage not in stages:
                    continue
                full = p.get("idea_full")
                if isinstance(full, str) and full:
                    exact_stages.setdefault(full, set()).add(stage)
                else:
                    stored = str(p.get("idea") or "")[:80]
                    if stored:
                        exact_stages.setdefault(stored, set()).add(stage)
                        legacy_keys.add(stored)
        out = []
        for n in nodes:
            label = str(n.get("label") or "")
            proven = exact_stages.get(label)
            if proven:
                if len(proven) == 1:
                    stage, source = next(iter(proven)), "growth_force"
                else:
                    # Proven plants for this very label disagree.
                    stage, source = None, "ambiguous"
            elif label[:80] in legacy_keys and label not in exact_stages:
                # Only a prefix-only legacy plant could be this
                # node's: identity unprovable (C-Q4).
                stage, source = None, "ambiguous"
            elif plants is not None:
                stage, source = None, "unplanted"
            else:
                stage, source = None, "unavailable"
            out.append({**n, "stage": stage, "stage_source": source,
                        "view_tag": "growth"})
        return out
    if room == "water":
        return [{**n, "form": "stream" if float(n.get("score") or 0) < 0.5 else "pool", "view_tag": "water"} for n in nodes]
    if room == "network":
        return [{**n, "view_tag": "network"} for n in nodes]
    if room == "force":
        return [{**n, "view_tag": "force"} for n in nodes]
    if room == "ancient_psalms":
        # Reverse order (retrograde walk) + short tokens
        rev = list(reversed(nodes))
        out = []
        for n in rev:
            label = str(n.get("label") or "")
            token = "".join(c for c in label if c.isalnum())[:6].upper() or "·"
            out.append({**n, "token": token, "view_tag": "ancient_psalms"})
        return out
    return list(nodes)


def render_room_ascii(room_id: str, nodes: List[Dict[str, Any]], limit: int = 12,
                      plants: Optional[List[Dict[str, Any]]] = None) -> List[str]:
    room = get_room(room_id) or VIEW_ROOMS["growth"]
    lines = [f"{room['emoji']} View room: {room['name']} — {room['description']}"]
    filtered = filter_nodes_for_room(room["id"], nodes, plants=plants)
    if not filtered:
        lines.append("  (empty)")
        return lines
    for n in filtered[:limit]:
        extra = n.get("stage") or n.get("form") or n.get("token") or n.get("skin") or ""
        lines.append(f"  · {n.get('label')} [{extra}]")
    if len(filtered) > limit:
        lines.append(f"  … +{len(filtered) - limit} more")
    return lines


def smoke() -> bool:
    print("=== VIEW ROOMS SMOKE ===")
    nodes = [{"id": "a", "label": "Alpha", "skin": "seed", "score": 0.2}]
    ok = len(list_rooms()) == 7 and get_room("water") is not None
    # No plants supplied: no stage may be claimed (T2).
    g = filter_nodes_for_room("growth", nodes)
    ok = ok and g[0].get("stage") is None and g[0].get("stage_source") == "unavailable"
    # With a GrowthForce plant, the stage is the plant's own stage.
    plants = [{"idea": "Alpha", "stage": "branch"}]
    g = filter_nodes_for_room("growth", nodes, plants=plants)
    ok = ok and g[0].get("stage") == "branch" and g[0].get("stage_source") == "growth_force"
    print(f"[{'PASS' if ok else 'FAIL'}] 7 rooms + growth stage from GrowthForce plants only")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
