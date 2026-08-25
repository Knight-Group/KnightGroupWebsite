from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from tradinglab.daily_session import run_daily_session
from tradinglab.ledger import FillLedger
from tradinglab.paper_broker import PaperBroker
from tradinglab.yahoo import Bar


def _uptrend_bars(n: int = 120) -> list[Bar]:
    price = 200.0
    out: list[Bar] = []
    day = date(2026, 1, 2)
    for i in range(n):
        while day.weekday() >= 5:
            day += timedelta(days=1)
        price += 0.8
        if i == n - 8:
            price -= 6.0
        out.append(Bar(date=day, open=price, high=price, low=price, close=price, volume=1_000_000))
        day += timedelta(days=1)
    return out


class DailySessionTests(unittest.TestCase):
    def test_does_not_double_buy_same_day(self) -> None:
        bars = _uptrend_bars()
        session = bars[-1].date
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = FillLedger(tmp_path / "ledger.json")
            with patch("tradinglab.daily_session.STATE_DIR", tmp_path):
                first = run_daily_session(
                    as_of=session,
                    submit_paper=False,
                    bars=bars,
                    ledger=ledger,
                    equity=100_000,
                )
                second = run_daily_session(
                    as_of=session,
                    submit_paper=False,
                    bars=bars,
                    ledger=ledger,
                    equity=100_000,
                )
        self.assertIs(first["live_trading"], False)
        buys = [row for row in first["sleeves"] if row["action"] == "buy"]
        self.assertTrue(buys)
        second_buys = [row for row in second["sleeves"] if row["action"] == "buy"]
        self.assertEqual(second_buys, [])
        self.assertEqual(second["submitted"], [])

    def test_ledger_blocks_buy_when_sleeve_qty_reset(self) -> None:
        bars = _uptrend_bars()
        session = bars[-1].date
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = FillLedger(tmp_path / "ledger.json")
            with patch("tradinglab.daily_session.STATE_DIR", tmp_path):
                first = run_daily_session(
                    as_of=session,
                    submit_paper=False,
                    bars=bars,
                    ledger=ledger,
                    equity=100_000,
                )
                (tmp_path / "sleeves.json").write_text("{}\n", encoding="utf-8")
                second = run_daily_session(
                    as_of=session,
                    submit_paper=False,
                    bars=bars,
                    ledger=ledger,
                    equity=100_000,
                )
        buys = [row for row in first["sleeves"] if row["action"] == "buy"]
        skipped = [row for row in second["sleeves"] if row["reason"] == "duplicate_buy_same_calendar_date"]
        self.assertEqual(len(skipped), len(buys))
        self.assertTrue(skipped)

    def test_submit_paper_posts_only_to_allowlisted_host(self) -> None:
        bars = _uptrend_bars()
        session = bars[-1].date
        seen: list[str] = []

        def opener(req, timeout: float):
            seen.append(req.full_url)
            body = {"id": "ord-1", "status": "accepted", "client_order_id": "x"}
            return 200, {}, json.dumps(body).encode("utf-8")

        broker = PaperBroker(api_key="paper-key", api_secret="paper-secret", opener=opener)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = FillLedger(tmp_path / "ledger.json")
            with patch("tradinglab.daily_session.STATE_DIR", tmp_path):
                report = run_daily_session(
                    as_of=session,
                    submit_paper=True,
                    broker=broker,
                    bars=bars,
                    ledger=ledger,
                    equity=50_000,
                )
        self.assertTrue(report["submitted"])
        self.assertTrue(seen)
        for url in seen:
            self.assertTrue(url.startswith("https://paper-api.alpaca.markets/"))
            self.assertNotIn("://api.alpaca.markets", url)


if __name__ == "__main__":
    unittest.main()
