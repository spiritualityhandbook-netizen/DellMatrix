"""Trading matrix — paper first, live only with explicit opt-in."""
from .broker import PaperBroker, LiveBrokerStub, Position
from .market import MarketBook, sample_universe, daily_snapshot
from .session import TradingSession

__all__ = [
    "PaperBroker",
    "LiveBrokerStub",
    "Position",
    "MarketBook",
    "sample_universe",
    "daily_snapshot",
    "TradingSession",
]
