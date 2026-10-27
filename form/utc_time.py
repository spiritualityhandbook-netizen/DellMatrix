"""The one UTC timestamp helper (P3 / TD-7).

Every DellMatrix record timestamp uses "%Y-%m-%dT%H:%M:%SZ" in
UTC. Before P3 the one-liner was defined seven times across the
tree (nursery, shared_main, duobeta growth/selfgrow,
duobeta_learn, nbd_engine, agent_coordinator) and inlined in more
places. utc_now_str() is the single implementation; the historical
per-module _ts/_utcnow names delegate to it so their call sites
are unchanged.
"""

from __future__ import annotations

from datetime import datetime, timezone

UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def utc_now_str() -> str:
    """Current UTC time in the canonical record format."""
    return datetime.now(timezone.utc).strftime(UTC_FORMAT)
