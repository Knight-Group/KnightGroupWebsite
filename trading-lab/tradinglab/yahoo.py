"""Yahoo Finance v8 chart API client. User-Agent is required."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable
from zoneinfo import ZoneInfo

from .config import YAHOO_CHART_HOSTS, YAHOO_USER_AGENT

ET = ZoneInfo("America/New_York")


@dataclass(frozen=True)
class Bar:
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float


def _chart_url(host: str, symbol: str, params: dict[str, str]) -> str:
    query = urllib.parse.urlencode(params)
    return f"https://{host}/v8/finance/chart/{urllib.parse.quote(symbol)}?{query}"


def fetch_chart(
    symbol: str,
    *,
    range_value: str = "max",
    interval: str = "1d",
    timeout: float = 30.0,
) -> list[Bar]:
    """Download daily bars from the Yahoo chart API (adjclose when present)."""
    params = {
        "range": range_value,
        "interval": interval,
        "events": "div,splits",
        "includeAdjustedClose": "true",
    }
    last_error: Exception | None = None
    for host in YAHOO_CHART_HOSTS:
        url = _chart_url(host, symbol, params)
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": YAHOO_USER_AGENT,
                "Accept": "application/json",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            return parse_chart_payload(payload)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            time.sleep(0.4)
    raise RuntimeError(f"Yahoo chart API failed for {symbol}: {last_error}") from last_error


def parse_chart_payload(payload: dict) -> list[Bar]:
    chart = payload.get("chart") or {}
    error = chart.get("error")
    if error:
        raise ValueError(f"Yahoo chart error: {error}")
    results = chart.get("result") or []
    if not results:
        raise ValueError("Yahoo chart returned no result")
    result = results[0]
    timestamps = result.get("timestamp") or []
    indicators = result.get("indicators") or {}
    quotes = (indicators.get("quote") or [{}])[0]
    adj_list = (indicators.get("adjclose") or [{}])
    adj = (adj_list[0] or {}).get("adjclose") or []
    opens = quotes.get("open") or []
    highs = quotes.get("high") or []
    lows = quotes.get("low") or []
    closes = quotes.get("close") or []
    volumes = quotes.get("volume") or []

    bars: list[Bar] = []
    n = len(timestamps)
    for i in range(n):
        ts = timestamps[i]
        raw_close = _num(closes[i] if i < len(closes) else None)
        adj_close = _num(adj[i] if i < len(adj) else None)
        close = adj_close if adj_close is not None else raw_close
        if ts is None or close is None or close <= 0:
            continue
        session = datetime.fromtimestamp(int(ts), tz=ET).date()
        bars.append(
            Bar(
                date=session,
                open=_num(opens[i] if i < len(opens) else None) or close,
                high=_num(highs[i] if i < len(highs) else None) or close,
                low=_num(lows[i] if i < len(lows) else None) or close,
                close=close,
                volume=_num(volumes[i] if i < len(volumes) else None) or 0.0,
            )
        )
    if len(bars) < 2:
        raise ValueError("Yahoo chart returned fewer than 2 valid bars")
    return bars


def _num(value: object) -> float | None:
    if value is None:
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if out != out:  # NaN
        return None
    return out


def fetch_universe(symbols: Iterable[str]) -> dict[str, list[Bar]]:
    out: dict[str, list[Bar]] = {}
    for i, symbol in enumerate(symbols):
        if i:
            time.sleep(0.25)
        out[symbol] = fetch_chart(symbol)
    return out
