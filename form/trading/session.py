#!/usr/bin/env python3
"""
TradingSession — ties market + paper broker + Dell Matrix plane + DuoBeta grow.

35[Discover] > 46[Rank] >> 50[Manifest] :: TradeSession
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import os
import sys

try:
    from form.open import open_program, Program
    from form.dell_matrix.plane import Skin
    from form.trading.market import sample_universe, daily_snapshot, load_latest, MarketBook
    from form.trading.broker import PaperBroker, LiveBrokerStub
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.open import open_program, Program
    from form.dell_matrix.plane import Skin
    from form.trading.market import sample_universe, daily_snapshot, load_latest, MarketBook
    from form.trading.broker import PaperBroker, LiveBrokerStub


@dataclass
class TradingSession:
    owner: str
    program: Program = field(init=False)
    paper: PaperBroker = field(init=False)
    live: LiveBrokerStub = field(init=False)
    book: MarketBook = field(init=False)

    def __post_init__(self):
        self.program = open_program(self.owner)
        self.paper = PaperBroker.load(self.owner)
        self.live = LiveBrokerStub(owner=self.owner)
        self.book = load_latest(self.owner) or sample_universe()

    def refresh_market(self, seed: Optional[int] = None) -> MarketBook:
        self.book = sample_universe(seed=seed)
        daily_snapshot(self.book, self.owner)
        return self.book

    def ideas_from_market(self) -> List[str]:
        """Place top movers as plane ideas — evolution food for IdeaGrow."""
        placed = []
        for q in self.book.top_movers(8):
            uid = f"eq_{q.symbol}"
            words = f"{q.symbol} px={q.price} ch={q.change_pct}% vol={q.volume} src={q.source}"
            self.program.place(uid, q.symbol, words=words, skin=Skin.CUBE)
            placed.append(uid)
        return placed

    def evolve(self, cycles: int = 5) -> Dict[str, Any]:
        """DuoBeta tick + IdeaGrow on trading ideas."""
        if len(self.program.cube.session.plane.units) < 2:
            self.ideas_from_market()
        grow = self.program.grow_ideas(cycles)
        self.program.grow(1)
        return {
            "grow_last": grow[-1] if grow else None,
            "generation": self.program.duo.generation,
            "scores": self.program.scores(),
        }

    def paper_buy(self, symbol: str, qty: float) -> Dict[str, Any]:
        q = self.book.quotes.get(symbol.upper())
        if not q:
            return {"ok": False, "reason": f"no quote for {symbol}"}
        return self.paper.order(symbol, qty, q.price, side="buy")

    def paper_sell(self, symbol: str, qty: float) -> Dict[str, Any]:
        q = self.book.quotes.get(symbol.upper())
        px = q.price if q else self.paper.positions.get(symbol.upper(), None)
        if q:
            price = q.price
        elif symbol.upper() in self.paper.positions:
            price = self.paper.positions[symbol.upper()].avg_price
        else:
            return {"ok": False, "reason": "no price"}
        return self.paper.order(symbol, qty, price, side="sell")

    def daily(self) -> Dict[str, Any]:
        """Full daily automation step: market → ideas → evolve → save."""
        self.refresh_market()
        placed = self.ideas_from_market()
        evo = self.evolve(5)
        marks = {s: q.price for s, q in self.book.quotes.items()}
        snap = self.paper.snapshot(marks)
        self.paper.save()
        self.program.save()
        return {
            "owner": self.owner,
            "placed": placed,
            "evolve": evo,
            "broker": snap,
            "top": [
                {"symbol": q.symbol, "ch": q.change_pct, "px": q.price}
                for q in self.book.top_movers(5)
            ],
            "disclaimer": "Educational simulation. Not financial advice. Past/sim ≠ future results.",
        }

    def status(self) -> Dict[str, Any]:
        marks = {s: q.price for s, q in self.book.quotes.items()}
        return {
            "owner": self.owner,
            "paper": self.paper.snapshot(marks),
            "live": self.live.status(),
            "quotes": len(self.book.quotes),
            "plane_units": list(self.program.cube.session.plane.units.keys())[:20],
            "generation": self.program.duo.generation,
            "disclaimer": "Not financial advice.",
        }
