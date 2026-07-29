#!/usr/bin/env python3
"""
Market book — offline-capable universe + daily snapshot structure.

Live quotes: optional fetch if network available and user enables.
Never claims complete knowledge of the market.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json
import os
import random

# Small liquid-ish teaching universe (symbols only — not advice)
DEFAULT_UNIVERSE = [
    "SPY", "QQQ", "IWM", "AAPL", "MSFT", "NVDA", "TSLA", "AMD",
    "META", "GOOGL", "AMZN", "JPM", "XOM", "GLD", "TLT",
]

_STATE = os.path.join(os.path.dirname(__file__), "..", "state", "trading")
os.makedirs(_STATE, exist_ok=True)


@dataclass
class Quote:
    symbol: str
    price: float
    change_pct: float
    volume: int
    asof: str
    source: str  # "sim" | "live"


@dataclass
class MarketBook:
    quotes: Dict[str, Quote] = field(default_factory=dict)
    universe: List[str] = field(default_factory=lambda: list(DEFAULT_UNIVERSE))
    note: str = "Simulated or user-fed data — not financial advice"

    def top_movers(self, n: int = 5) -> List[Quote]:
        return sorted(self.quotes.values(), key=lambda q: abs(q.change_pct), reverse=True)[:n]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "note": self.note,
            "universe": self.universe,
            "quotes": {
                s: {
                    "symbol": q.symbol,
                    "price": q.price,
                    "change_pct": q.change_pct,
                    "volume": q.volume,
                    "asof": q.asof,
                    "source": q.source,
                }
                for s, q in self.quotes.items()
            },
        }


def sample_universe(seed: Optional[int] = None) -> MarketBook:
    """Deterministic-ish simulated session for paper trading / teaching."""
    rng = random.Random(seed if seed is not None else int(datetime.now(timezone.utc).strftime("%Y%m%d")))
    asof = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    book = MarketBook()
    base = {
        "SPY": 520.0, "QQQ": 450.0, "IWM": 200.0, "AAPL": 190.0, "MSFT": 420.0,
        "NVDA": 120.0, "TSLA": 180.0, "AMD": 160.0, "META": 500.0, "GOOGL": 170.0,
        "AMZN": 185.0, "JPM": 200.0, "XOM": 110.0, "GLD": 220.0, "TLT": 95.0,
    }
    for sym in book.universe:
        px = base.get(sym, 100.0) * (1 + rng.uniform(-0.02, 0.02))
        ch = rng.uniform(-3.5, 3.5)
        book.quotes[sym] = Quote(
            symbol=sym,
            price=round(px * (1 + ch / 100), 2),
            change_pct=round(ch, 2),
            volume=int(rng.uniform(1e6, 5e7)),
            asof=asof,
            source="sim",
        )
    return book


def daily_snapshot(book: MarketBook, owner: str) -> str:
    path = os.path.join(_STATE, f"daily_{owner}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(book.to_dict(), f, indent=2)
    latest = os.path.join(_STATE, f"latest_{owner}.json")
    with open(latest, "w", encoding="utf-8") as f:
        json.dump(book.to_dict(), f, indent=2)
    return path


def load_latest(owner: str) -> Optional[MarketBook]:
    latest = os.path.join(_STATE, f"latest_{owner}.json")
    if not os.path.isfile(latest):
        return None
    with open(latest, encoding="utf-8") as f:
        data = json.load(f)
    book = MarketBook(universe=list(data.get("universe") or DEFAULT_UNIVERSE))
    for s, q in (data.get("quotes") or {}).items():
        book.quotes[s] = Quote(
            symbol=q["symbol"],
            price=float(q["price"]),
            change_pct=float(q["change_pct"]),
            volume=int(q["volume"]),
            asof=q.get("asof", ""),
            source=q.get("source", "sim"),
        )
    return book
