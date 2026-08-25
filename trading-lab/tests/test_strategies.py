from __future__ import annotations

import unittest

from tradinglab.strategies import buy_hold, dual_momentum_3m, sma, sma_10_50, trend_pullback


class StrategyTests(unittest.TestCase):
    def test_sma(self) -> None:
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        out = sma(values, 3)
        self.assertIsNone(out[1])
        self.assertEqual(out[2], 2.0)
        self.assertEqual(out[4], 4.0)

    def test_dual_momentum_long_after_rise(self) -> None:
        closes = [100.0] * 63 + [110.0]
        sig = dual_momentum_3m(closes)
        self.assertEqual(sig[-1], 1)
        self.assertEqual(sig[0], 0)

    def test_dual_momentum_flat_after_drop(self) -> None:
        closes = [100.0] * 63 + [90.0]
        sig = dual_momentum_3m(closes)
        self.assertEqual(sig[-1], 0)

    def test_sma_cross(self) -> None:
        # Slow start then a persistent uptrend so SMA10 > SMA50.
        closes = [100.0] * 50 + [120.0] * 20
        sig = sma_10_50(closes)
        self.assertEqual(sig[-1], 1)
        self.assertEqual(sig[10], 0)

    def test_trend_pullback_needs_dip_then_recross(self) -> None:
        up = [100 + i for i in range(60)]
        dip = [up[-1] - 3, up[-1] - 6, up[-1] - 2, up[-1] + 1]
        closes = [float(x) for x in up + dip]
        sig = trend_pullback(closes)
        self.assertIn(1, sig[-6:])

    def test_buy_hold_always_long(self) -> None:
        self.assertEqual(buy_hold([1.0, 2.0, 3.0]), [1, 1, 1])


if __name__ == "__main__":
    unittest.main()
