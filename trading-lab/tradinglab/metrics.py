"""Return and risk metrics. rf = 0; 252 trading days per year."""

from __future__ import annotations

import math
from collections.abc import Sequence

TRADING_DAYS = 252


def daily_returns(closes: Sequence[float]) -> list[float]:
    rets = [0.0] * len(closes)
    for i in range(1, len(closes)):
        prev = closes[i - 1]
        rets[i] = closes[i] / prev - 1.0 if prev else 0.0
    return rets


def strategy_returns(signals: Sequence[int], asset_returns: Sequence[float]) -> list[float]:
    """Execute yesterday's close signal on today's close-to-close return."""
    n = min(len(signals), len(asset_returns))
    out = [0.0] * n
    for i in range(1, n):
        out[i] = signals[i - 1] * asset_returns[i]
    return out


def equity_curve(returns: Sequence[float], start: float = 1.0) -> list[float]:
    equity = start
    out = []
    for r in returns:
        equity *= 1.0 + r
        out.append(equity)
    return out


def max_drawdown(equity: Sequence[float]) -> float:
    peak = 0.0
    max_dd = 0.0
    for value in equity:
        if value > peak:
            peak = value
        if peak > 0:
            dd = value / peak - 1.0
            if dd < max_dd:
                max_dd = dd
    return max_dd


def cagr(returns: Sequence[float], periods_per_year: int = TRADING_DAYS) -> float:
    if not returns:
        return 0.0
    equity = 1.0
    for r in returns:
        equity *= 1.0 + r
    years = len(returns) / periods_per_year
    if years <= 0 or equity <= 0:
        return 0.0
    return equity ** (1.0 / years) - 1.0


def sharpe(returns: Sequence[float], periods_per_year: int = TRADING_DAYS) -> float:
    n = len(returns)
    if n < 2:
        return 0.0
    mean = sum(returns) / n
    var = sum((r - mean) ** 2 for r in returns) / (n - 1)
    std = math.sqrt(var)
    if std == 0:
        return 0.0
    return (mean / std) * math.sqrt(periods_per_year)


def time_in_market(signals: Sequence[int]) -> float:
    if not signals:
        return 0.0
    return sum(1 for s in signals if s) / len(signals)


def summarize(
    returns: Sequence[float],
    signals: Sequence[int] | None = None,
) -> dict[str, float]:
    eq = equity_curve(returns)
    dd = max_drawdown(eq)
    growth = cagr(returns)
    calmar = (growth / abs(dd)) if dd < 0 else 0.0
    out = {
        "cagr": round(growth, 6),
        "sharpe": round(sharpe(returns), 6),
        "max_drawdown": round(dd, 6),
        "calmar": round(calmar, 6),
        "total_return": round((eq[-1] - 1.0) if eq else 0.0, 6),
        "bars": float(len(returns)),
    }
    if signals is not None:
        aligned = signals[: len(returns)]
        out["time_in_market"] = round(time_in_market(aligned), 6)
    return out


def apply_risk_halt(
    signals: Sequence[int],
    asset_returns: Sequence[float],
    halt_dd: float,
    peak_closes: Sequence[float],
) -> list[int]:
    """Flatten after strategy DD hits halt_dd; resume only after price makes a new high.

    This is the risk-capped overlay. Unhalted buy-hold does not use it. Halting
    in 2020 and waiting for a new price high is why unhalted buy-hold still
    beats risk-capped systems on a full sample that includes that crash.
    """
    n = min(len(signals), len(asset_returns), len(peak_closes))
    out = [0] * n
    equity = 1.0
    peak_eq = 1.0
    halted = False
    halt_price_peak = 0.0
    running_price_peak = 0.0
    for i in range(n):
        price = peak_closes[i]
        if price > running_price_peak:
            running_price_peak = price
        if halted and price > halt_price_peak:
            halted = False
        out[i] = 0 if halted else int(signals[i])
        if i == 0:
            continue
        equity *= 1.0 + out[i - 1] * asset_returns[i]
        if equity > peak_eq:
            peak_eq = equity
        if peak_eq > 0 and equity / peak_eq - 1.0 <= -abs(halt_dd):
            halted = True
            halt_price_peak = running_price_peak
            out[i] = 0
    return out
