"""Paper-only configuration. Live brokerage is not a supported mode."""

from __future__ import annotations

# HARDCODED. Do not read this from the environment. There is no live path.
LIVE_TRADING = False

PAPER_BROKER_HOST = "paper-api.alpaca.markets"
PAPER_BROKER_BASE_URL = "https://paper-api.alpaca.markets"

# Live Alpaca hosts — always refused, including via env overrides.
REFUSED_BROKER_HOSTS = frozenset(
    {
        "api.alpaca.markets",
        "broker-api.alpaca.markets",
        "live.alpaca.markets",
    }
)

# Intentionally unused. Leftover live URLs must not override the allowlist.
IGNORED_BASE_URL_ENV = (
    "ALPACA_BASE_URL",
    "APCA_API_BASE_URL",
    "ALPACA_API_BASE_URL",
    "TRADIER_BASE_URL",
)

UNIVERSE = ("SPY", "QQQ", "IWM")
PAPER_SYMBOL = "SPY"

WALK_FORWARD_TRAIN_DAYS = 756
WALK_FORWARD_TEST_DAYS = 252
WALK_FORWARD_STEP_DAYS = 126

# 3-month momentum uses ~63 trading days.
MOMENTUM_LOOKBACK = 63
SMA_FAST = 10
SMA_SLOW = 50
INDICATOR_WARMUP = MOMENTUM_LOOKBACK

SLEEVES = (
    {"strategy": "dual_momentum_3m", "weight": 0.50, "symbol": PAPER_SYMBOL},
    {"strategy": "sma_10_50", "weight": 0.30, "symbol": PAPER_SYMBOL},
    {"strategy": "trend_pullback", "weight": 0.20, "symbol": PAPER_SYMBOL},
)

RISK_HALT_DRAWDOWN = 0.20

YAHOO_CHART_HOSTS = ("query1.finance.yahoo.com", "query2.finance.yahoo.com")
YAHOO_USER_AGENT = (
    "Mozilla/5.0 (compatible; TradingLab/1.0; paper-research; +https://finance.yahoo.com)"
)

RECENT_OOS_START = "2024-06-25"
RECENT_OOS_END = "2026-08-24"

DEFAULT_PAPER_EQUITY = 100_000.0


def assert_paper_only() -> None:
    """Fail closed if live trading is ever enabled."""
    if LIVE_TRADING is not False:
        raise RuntimeError("LIVE_TRADING is hardcoded False; live brokerage is disabled.")
