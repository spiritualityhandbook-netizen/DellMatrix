#!/usr/bin/env python3
"""
Trading CLI for sister matrix.

Windows:
  python -m form.trading.cli --owner Sister daily
  python -m form.trading.cli --owner Sister status
  python -m form.trading.cli --owner Sister buy SPY 1
  python -m form.trading.cli --owner Sister sell SPY 1
  python -m form.trading.cli --owner Sister evolve 10
"""

from __future__ import annotations

import json
import sys

from form.trading.session import TradingSession


def main() -> None:
    owner = "Sister"
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for i, a in enumerate(sys.argv):
        if a == "--owner" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]

    if not args:
        print("commands: daily | status | buy SYM QTY | sell SYM QTY | evolve [N] | refresh")
        print("disclaimer: educational paper trading — not financial advice")
        sys.exit(0)

    s = TradingSession(owner=owner)
    cmd = args[0].lower()

    if cmd == "daily":
        print(json.dumps(s.daily(), indent=2))
    elif cmd == "status":
        print(json.dumps(s.status(), indent=2))
    elif cmd == "refresh":
        b = s.refresh_market()
        print(json.dumps({"ok": True, "quotes": len(b.quotes), "top": [
            {"s": q.symbol, "ch": q.change_pct} for q in b.top_movers(5)
        ]}, indent=2))
    elif cmd == "evolve":
        n = int(args[1]) if len(args) > 1 else 5
        print(json.dumps(s.evolve(n), indent=2))
    elif cmd == "buy" and len(args) >= 3:
        print(json.dumps(s.paper_buy(args[1], float(args[2])), indent=2))
        s.paper.save()
    elif cmd == "sell" and len(args) >= 3:
        print(json.dumps(s.paper_sell(args[1], float(args[2])), indent=2))
        s.paper.save()
    else:
        print("unknown — daily | status | buy SYM QTY | sell SYM QTY | evolve [N] | refresh")
        sys.exit(1)


if __name__ == "__main__":
    main()
