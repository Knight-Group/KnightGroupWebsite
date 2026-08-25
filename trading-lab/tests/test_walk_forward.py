from __future__ import annotations

import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from tradinglab.walk_forward import run_walk_forward, walk_forward_symbol
from tradinglab.yahoo import Bar, parse_chart_payload


def _bars(n: int, start: date = date(2015, 1, 2), drift: float = 0.0004) -> list[Bar]:
    price = 100.0
    out: list[Bar] = []
    day = start
    for i in range(n):
        while day.weekday() >= 5:
            day += timedelta(days=1)
        price *= 1.0 + drift
        if i % 80 == 40:
            price *= 0.97
        out.append(Bar(date=day, open=price, high=price, low=price, close=price, volume=1_000_000))
        day += timedelta(days=1)
    return out


class WalkForwardTests(unittest.TestCase):
    def test_window_counts(self) -> None:
        # warmup 63 + a few folds
        n = 63 + 756 + 252 + 126 * 3
        folds = walk_forward_symbol(_bars(n), train_days=756, test_days=252, step_days=126)
        self.assertGreaterEqual(len(folds), 4)
        first = folds[0]
        self.assertEqual(first["fold"], 0)
        self.assertIn("dual_momentum_3m", first["train"])
        self.assertIn("sma_10_50", first["test"])

    def test_report_winners_and_live_flag(self) -> None:
        n = 63 + 756 + 252 + 126
        report = run_walk_forward({"SPY": _bars(n), "QQQ": _bars(n), "IWM": _bars(n)})
        self.assertIs(report["live_trading"], False)
        self.assertEqual(report["window"]["train_days"], 756)
        self.assertEqual(report["window"]["test_days"], 252)
        self.assertEqual(report["window"]["step_days"], 126)
        self.assertIn("overall_walk_forward_winner", report["winners"])
        self.assertIn("tactical_walk_forward_winner", report["winners"])
        self.assertTrue(report["symbols"]["SPY"]["folds"])


class YahooParseTests(unittest.TestCase):
    def test_rejects_monthly_granularity(self) -> None:
        payload = {
            "chart": {
                "result": [
                    {
                        "meta": {"dataGranularity": "1mo"},
                        "timestamp": [1600000000, 1600086400],
                        "indicators": {
                            "quote": [
                                {
                                    "open": [10.0, 11.0],
                                    "high": [10.5, 11.5],
                                    "low": [9.5, 10.5],
                                    "close": [10.2, 11.1],
                                    "volume": [100, 110],
                                }
                            ],
                            "adjclose": [{"adjclose": [10.2, 11.1]}],
                        },
                    }
                ],
                "error": None,
            }
        }
        with self.assertRaises(ValueError):
            parse_chart_payload(payload)

    def test_parse_chart_payload(self) -> None:
        payload = {
            "chart": {
                "result": [
                    {
                        "timestamp": [1600000000, 1600086400],
                        "indicators": {
                            "quote": [
                                {
                                    "open": [10.0, 11.0],
                                    "high": [10.5, 11.5],
                                    "low": [9.5, 10.5],
                                    "close": [10.2, 11.1],
                                    "volume": [100, 110],
                                }
                            ],
                            "adjclose": [{"adjclose": [10.2, 11.1]}],
                        },
                    }
                ],
                "error": None,
            }
        }
        bars = parse_chart_payload(payload)
        self.assertEqual(len(bars), 2)
        self.assertGreater(bars[1].close, bars[0].close)


if __name__ == "__main__":
    unittest.main()
