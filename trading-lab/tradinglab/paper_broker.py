"""Alpaca paper broker. Allowlists only paper-api.alpaca.markets.

This client never reads APCA_API_BASE_URL / ALPACA_BASE_URL, so a leftover live
URL cannot override the host. Live host api.alpaca.markets is always refused.
Tradier is not used.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable
from urllib.parse import urlparse

from .config import (
    LIVE_TRADING,
    PAPER_BROKER_BASE_URL,
    PAPER_BROKER_HOST,
    REFUSED_BROKER_HOSTS,
    assert_paper_only,
)

HttpOpener = Callable[[urllib.request.Request, float], tuple[int, dict[str, str], bytes]]


class PaperBrokerError(RuntimeError):
    """Raised when a request is not allowed or the paper API fails."""


def validate_broker_url(url: str) -> None:
    """Refuse anything that is not https://paper-api.alpaca.markets/..."""
    assert_paper_only()
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https":
        raise PaperBrokerError(f"Refusing non-HTTPS broker URL: {url}")
    if parsed.username or parsed.password:
        raise PaperBrokerError("Refusing broker URL with embedded credentials")
    if host in REFUSED_BROKER_HOSTS or host == "api.alpaca.markets":
        raise PaperBrokerError(f"Refusing live brokerage host: {host}")
    if host != PAPER_BROKER_HOST:
        raise PaperBrokerError(
            f"Host {host!r} is not allowlisted. Only {PAPER_BROKER_HOST} is permitted."
        )


class PaperBroker:
    """HTTPS client pinned to the Alpaca paper host."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_secret: str | None = None,
        opener: HttpOpener | None = None,
        timeout: float = 20.0,
    ) -> None:
        assert_paper_only()
        if LIVE_TRADING is not False:
            raise PaperBrokerError("LIVE_TRADING must remain False")
        self.base_url = PAPER_BROKER_BASE_URL
        self.timeout = timeout
        self._opener = opener or _default_opener
        self.api_key = api_key if api_key is not None else os.environ.get("APCA_API_KEY_ID", "")
        self.api_secret = (
            api_secret if api_secret is not None else os.environ.get("APCA_API_SECRET_KEY", "")
        )
        if not self.api_key:
            self.api_key = os.environ.get("ALPACA_API_KEY", "")
        if not self.api_secret:
            self.api_secret = os.environ.get("ALPACA_SECRET_KEY", "")

    def has_credentials(self) -> bool:
        return bool(self.api_key and self.api_secret)

    def request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> tuple[int, Any]:
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        validate_broker_url(url)
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret,
        }
        req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
        try:
            status, _resp_headers, raw = self._opener(req, self.timeout)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace") if exc.fp else str(exc)
            raise PaperBrokerError(f"Paper API HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise PaperBrokerError(f"Paper API transport error: {exc}") from exc
        parsed: Any = None
        if raw:
            try:
                parsed = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                parsed = raw.decode("utf-8", errors="replace")
        return status, parsed

    def get_account(self) -> dict[str, Any]:
        status, payload = self.request("GET", "/v2/account")
        if status >= 400:
            raise PaperBrokerError(f"Account lookup failed: {payload}")
        if not isinstance(payload, dict):
            raise PaperBrokerError("Unexpected account payload")
        return payload

    def submit_order(self, order: dict[str, Any]) -> dict[str, Any]:
        if str(order.get("side", "")).lower() not in {"buy", "sell"}:
            raise PaperBrokerError("Order side must be buy or sell")
        status, payload = self.request("POST", "/v2/orders", order)
        if status >= 400:
            raise PaperBrokerError(f"Paper order rejected: {payload}")
        if not isinstance(payload, dict):
            raise PaperBrokerError("Unexpected order payload")
        return payload


def _default_opener(req: urllib.request.Request, timeout: float) -> tuple[int, dict[str, str], bytes]:
    validate_broker_url(req.full_url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return int(resp.status), dict(resp.headers.items()), resp.read()
