"""Idempotent fill ledger: one buy per strategy+symbol+calendar date."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


def _key(strategy: str, symbol: str, session: date, side: str) -> str:
    return f"{strategy}|{symbol.upper()}|{session.isoformat()}|{side.lower()}"


class FillLedger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._rows: list[dict[str, Any]] = []
        if self.path.exists():
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                self._rows = loaded

    def already_bought(self, strategy: str, symbol: str, session: date) -> bool:
        want = _key(strategy, symbol, session, "buy")
        return any(_key(r["strategy"], r["symbol"], date.fromisoformat(r["date"]), r["side"]) == want for r in self._rows)

    def record(
        self,
        *,
        strategy: str,
        symbol: str,
        session: date,
        side: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        row = {
            "strategy": strategy,
            "symbol": symbol.upper(),
            "date": session.isoformat(),
            "side": side.lower(),
        }
        if extra:
            row.update(extra)
        self._rows.append(row)
        self._flush()
        return row

    def _flush(self) -> None:
        self.path.write_text(json.dumps(self._rows, indent=2) + "\n", encoding="utf-8")
