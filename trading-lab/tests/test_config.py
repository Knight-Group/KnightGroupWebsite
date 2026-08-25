from __future__ import annotations

import unittest

from tradinglab.config import LIVE_TRADING, PAPER_BROKER_HOST, REFUSED_BROKER_HOSTS, assert_paper_only


class ConfigTests(unittest.TestCase):
    def test_live_trading_hardcoded_false(self) -> None:
        self.assertIs(LIVE_TRADING, False)
        self.assertEqual(LIVE_TRADING, False)
        assert_paper_only()

    def test_paper_host_is_not_live(self) -> None:
        self.assertEqual(PAPER_BROKER_HOST, "paper-api.alpaca.markets")
        self.assertIn("api.alpaca.markets", REFUSED_BROKER_HOSTS)
        self.assertNotEqual(PAPER_BROKER_HOST, "api.alpaca.markets")

    def test_source_does_not_read_tradier(self) -> None:
        from pathlib import Path

        root = Path(__file__).resolve().parents[1] / "tradinglab"
        for path in root.glob("*.py"):
            text = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("tradier_access_token", text)
            self.assertNotIn("tradier.com", text)


if __name__ == "__main__":
    unittest.main()
