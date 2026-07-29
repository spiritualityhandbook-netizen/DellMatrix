#!/usr/bin/env python3
"""
Paper broker (real simulation) + Live stub (user API keys via env only).

Live never runs unless TRADING_LIVE=1 and keys present.
Not financial advice. Risk of loss.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json
import os

_STATE = os.path.join(os.path.dirname(__file__), "..", "state", "trading")
os.makedirs(_STATE, exist_ok=True)


@dataclass
class Position:
    symbol: str
    qty: float
    avg_price: float
    side: str = "long"

    def mtm(self, price: float) -> float:
        return (price - self.avg_price) * self.qty


@dataclass
class PaperBroker:
    owner: str
    cash: float = 10_000.0
    positions: Dict[str, Position] = field(default_factory=dict)
    fills: List[Dict[str, Any]] = field(default_factory=list)
    max_risk_per_trade: float = 50.0  # dollars risk budget hint
    mode: str = "paper"

    def equity(self, marks: Dict[str, float]) -> float:
        eq = self.cash
        for sym, pos in self.positions.items():
            px = marks.get(sym, pos.avg_price)
            eq += pos.qty * px
        return round(eq, 2)

    def order(self, symbol: str, qty: float, price: float, side: str = "buy") -> Dict[str, Any]:
        symbol = symbol.upper()
        notional = abs(qty) * price
        if side == "buy":
            if notional > self.cash:
                return {"ok": False, "reason": "insufficient cash", "mode": "paper"}
            if notional > self.max_risk_per_trade * 20:  # soft cap vs tiny account teaching
                return {"ok": False, "reason": "size exceeds teaching risk soft-cap", "mode": "paper"}
            self.cash -= notional
            if symbol in self.positions:
                p = self.positions[symbol]
                new_qty = p.qty + qty
                p.avg_price = (p.avg_price * p.qty + price * qty) / new_qty
                p.qty = new_qty
            else:
                self.positions[symbol] = Position(symbol, qty, price)
        elif side == "sell":
            if symbol not in self.positions or self.positions[symbol].qty < qty:
                return {"ok": False, "reason": "no position", "mode": "paper"}
            self.cash += notional
            self.positions[symbol].qty -= qty
            if self.positions[symbol].qty <= 1e-9:
                del self.positions[symbol]
        else:
            return {"ok": False, "reason": "side must be buy|sell"}
        fill = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "symbol": symbol,
            "qty": qty,
            "price": price,
            "side": side,
            "mode": "paper",
        }
        self.fills.append(fill)
        return {"ok": True, **fill, "cash": self.cash}

    def snapshot(self, marks: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        marks = marks or {s: p.avg_price for s, p in self.positions.items()}
        return {
            "mode": "paper",
            "owner": self.owner,
            "cash": round(self.cash, 2),
            "equity": self.equity(marks),
            "positions": {
                s: {"qty": p.qty, "avg": p.avg_price, "mtm": p.mtm(marks.get(s, p.avg_price))}
                for s, p in self.positions.items()
            },
            "fills": len(self.fills),
            "max_risk_per_trade": self.max_risk_per_trade,
        }

    def save(self) -> str:
        path = os.path.join(_STATE, f"broker_paper_{self.owner}.json")
        data = {
            "owner": self.owner,
            "cash": self.cash,
            "max_risk_per_trade": self.max_risk_per_trade,
            "positions": {
                s: {"qty": p.qty, "avg_price": p.avg_price, "side": p.side}
                for s, p in self.positions.items()
            },
            "fills": self.fills[-200:],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return path

    @classmethod
    def load(cls, owner: str) -> "PaperBroker":
        path = os.path.join(_STATE, f"broker_paper_{owner}.json")
        if not os.path.isfile(path):
            return cls(owner=owner)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        b = cls(
            owner=owner,
            cash=float(data.get("cash", 10_000)),
            max_risk_per_trade=float(data.get("max_risk_per_trade", 50)),
        )
        for s, p in (data.get("positions") or {}).items():
            b.positions[s] = Position(s, float(p["qty"]), float(p["avg_price"]), p.get("side", "long"))
        b.fills = list(data.get("fills") or [])
        return b


@dataclass
class LiveBrokerStub:
    """
    Live adapter — does NOT place orders unless fully configured.
    Put keys in environment variables, never in files committed to git.

    TRADING_LIVE=1
    TRADING_API_KEY=...
    TRADING_API_SECRET=...
    TRADING_BASE_URL=...   # broker REST base
    """

    owner: str
    mode: str = "live_stub"

    def enabled(self) -> bool:
        return os.environ.get("TRADING_LIVE", "").strip() == "1" and bool(
            os.environ.get("TRADING_API_KEY")
        )

    def status(self) -> Dict[str, Any]:
        return {
            "mode": "live",
            "enabled": self.enabled(),
            "has_key": bool(os.environ.get("TRADING_API_KEY")),
            "base_url": os.environ.get("TRADING_BASE_URL", ""),
            "warning": "Live trading risks capital. Paper first. Not advice.",
        }

    def order(self, symbol: str, qty: float, side: str = "buy") -> Dict[str, Any]:
        if not self.enabled():
            return {
                "ok": False,
                "reason": "live disabled — set TRADING_LIVE=1 and API key env vars",
                "mode": "live",
            }
        # Intentionally no generic live route: user must wire their broker SDK here.
        return {
            "ok": False,
            "reason": "wire your broker SDK in LiveBrokerStub.order (Alpaca/IBKR/etc.)",
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "mode": "live",
        }
