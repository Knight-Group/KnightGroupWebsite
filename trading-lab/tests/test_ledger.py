from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from tradinglab.ledger import FillLedger


class LedgerTests(unittest.TestCase):
    def test_blocks_second_buy_same_strategy_symbol_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = FillLedger(Path(tmp) / "ledger.json")
            session = date(2026, 8, 25)
            self.assertFalse(ledger.already_bought("dual_momentum_3m", "SPY", session))
            ledger.record(strategy="dual_momentum_3m", symbol="SPY", session=session, side="buy")
            self.assertTrue(ledger.already_bought("dual_momentum_3m", "SPY", session))
            self.assertFalse(ledger.already_bought("sma_10_50", "SPY", session))
            self.assertFalse(ledger.already_bought("dual_momentum_3m", "QQQ", session))
            self.assertFalse(ledger.already_bought("dual_momentum_3m", "SPY", date(2026, 8, 26)))


if __name__ == "__main__":
    unittest.main()
