from __future__ import annotations

import json
import os
import unittest
import urllib.request
from typing import Any

from tradinglab.paper_broker import PaperBroker, PaperBrokerError, validate_broker_url


class ValidateUrlTests(unittest.TestCase):
    def test_allows_paper_host(self) -> None:
        validate_broker_url("https://paper-api.alpaca.markets/v2/orders")

    def test_refuses_live_host(self) -> None:
        with self.assertRaises(PaperBrokerError) as ctx:
            validate_broker_url("https://api.alpaca.markets/v2/orders")
        self.assertIn("api.alpaca.markets", str(ctx.exception))

    def test_refuses_live_host_casefold(self) -> None:
        with self.assertRaises(PaperBrokerError):
            validate_broker_url("https://API.ALPACA.MARKETS/v2/account")

    def test_refuses_lookalike_host(self) -> None:
        with self.assertRaises(PaperBrokerError):
            validate_broker_url("https://paper-api.alpaca.markets.evil.example/v2/orders")

    def test_refuses_http(self) -> None:
        with self.assertRaises(PaperBrokerError):
            validate_broker_url("http://paper-api.alpaca.markets/v2/orders")

    def test_env_live_base_url_does_not_override(self) -> None:
        os.environ["APCA_API_BASE_URL"] = "https://api.alpaca.markets"
        os.environ["ALPACA_BASE_URL"] = "https://api.alpaca.markets"
        try:
            broker = PaperBroker(api_key="k", api_secret="s", opener=_reject_opener)
            self.assertEqual(broker.base_url, "https://paper-api.alpaca.markets")
            with self.assertRaises(PaperBrokerError):
                validate_broker_url(os.environ["APCA_API_BASE_URL"] + "/v2/orders")
        finally:
            os.environ.pop("APCA_API_BASE_URL", None)
            os.environ.pop("ALPACA_BASE_URL", None)


class PaperBrokerRequestTests(unittest.TestCase):
    def test_submit_uses_paper_host_only(self) -> None:
        seen: dict[str, str] = {}

        def opener(req: urllib.request.Request, timeout: float) -> tuple[int, dict[str, str], bytes]:
            seen["url"] = req.full_url
            payload = {"id": "paper-1", "status": "accepted", "client_order_id": "cid"}
            return 200, {}, json.dumps(payload).encode("utf-8")

        broker = PaperBroker(api_key="k", api_secret="s", opener=opener)
        result = broker.submit_order(
            {
                "symbol": "SPY",
                "notional": "1000",
                "side": "buy",
                "type": "market",
                "time_in_force": "day",
            }
        )
        self.assertEqual(result["id"], "paper-1")
        self.assertTrue(seen["url"].startswith("https://paper-api.alpaca.markets/"))
        self.assertNotIn("https://api.alpaca.markets", seen["url"])


def _reject_opener(req: urllib.request.Request, timeout: float) -> tuple[int, dict[str, str], bytes]:
    raise AssertionError(f"network should not run: {req.full_url}")


if __name__ == "__main__":
    unittest.main()
