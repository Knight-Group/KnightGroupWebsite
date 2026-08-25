"""Long/flat tactical sleeves. Signals are computed on the close (no lookahead)."""

from __future__ import annotations

from collections.abc import Sequence

from .config import MOMENTUM_LOOKBACK, SMA_FAST, SMA_SLOW


def sma(values: Sequence[float], window: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if window <= 0:
        raise ValueError("SMA window must be positive")
    running = 0.0
    for i, price in enumerate(values):
        running += price
        if i >= window:
            running -= values[i - window]
        if i >= window - 1:
            out[i] = running / window
    return out


def dual_momentum_3m(closes: Sequence[float], lookback: int = MOMENTUM_LOOKBACK) -> list[int]:
    """Absolute 3-month momentum: long if close / close[t-63] - 1 > 0, else cash."""
    n = len(closes)
    sig = [0] * n
    for i in range(lookback, n):
        prior = closes[i - lookback]
        if prior > 0 and closes[i] / prior - 1.0 > 0:
            sig[i] = 1
    return sig


def sma_10_50(
    closes: Sequence[float],
    fast: int = SMA_FAST,
    slow: int = SMA_SLOW,
) -> list[int]:
    """Long while SMA(fast) > SMA(slow), else cash."""
    fast_ma = sma(closes, fast)
    slow_ma = sma(closes, slow)
    sig = [0] * len(closes)
    for i, (a, b) in enumerate(zip(fast_ma, slow_ma)):
        if a is not None and b is not None and a > b:
            sig[i] = 1
    return sig


def trend_pullback(
    closes: Sequence[float],
    fast: int = SMA_FAST,
    slow: int = SMA_SLOW,
) -> list[int]:
    """Uptrend (close > SMA slow), buy the recross of SMA fast after a pullback.

    Exit when close drops back through the slow SMA.
    """
    fast_ma = sma(closes, fast)
    slow_ma = sma(closes, slow)
    n = len(closes)
    sig = [0] * n
    in_pos = False
    pullback = False
    for i in range(n):
        fast_v = fast_ma[i]
        slow_v = slow_ma[i]
        if fast_v is None or slow_v is None:
            continue
        uptrend = closes[i] > slow_v
        if not uptrend:
            in_pos = False
            pullback = False
            sig[i] = 0
            continue
        if in_pos:
            sig[i] = 1
            if closes[i] < fast_v:
                pullback = True
            continue
        if closes[i] < fast_v:
            pullback = True
            sig[i] = 0
            continue
        if pullback and closes[i] >= fast_v:
            in_pos = True
            pullback = False
            sig[i] = 1
        else:
            sig[i] = 0
    return sig


def buy_hold(closes: Sequence[float]) -> list[int]:
    return [1] * len(closes)


STRATEGY_FNS = {
    "dual_momentum_3m": dual_momentum_3m,
    "sma_10_50": sma_10_50,
    "trend_pullback": trend_pullback,
    "buy_hold": buy_hold,
}

TACTICAL_STRATEGIES = ("dual_momentum_3m", "sma_10_50", "trend_pullback")


def signal_for(name: str, closes: Sequence[float]) -> list[int]:
    try:
        fn = STRATEGY_FNS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown strategy: {name}") from exc
    return fn(closes)
