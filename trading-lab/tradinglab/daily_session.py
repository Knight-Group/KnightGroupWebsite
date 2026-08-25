"""Daily paper session for the three SPY sleeves. Never live."""

from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .config import (
    DEFAULT_PAPER_EQUITY,
    LIVE_TRADING,
    SLEEVES,
    assert_paper_only,
)
from .ledger import FillLedger
from .paper_broker import PaperBroker, PaperBrokerError
from .strategies import signal_for
from .yahoo import Bar, fetch_chart

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "state"


def session_date(as_of: date | None = None) -> date:
    if as_of is not None:
        return as_of
    return datetime.now(ET).date()


def last_signal(name: str, bars: list[Bar]) -> tuple[int, Bar]:
    if len(bars) < 2:
        raise RuntimeError("Need at least 2 bars to size a session")
    closes = [b.close for b in bars]
    sig = signal_for(name, closes)
    # Yesterday's close signal trades today (same delay as backtests).
    return sig[-1], bars[-1]


def _client_order_id(strategy: str, symbol: str, session: date, side: str) -> str:
    raw = f"{strategy}-{symbol}-{session.isoformat()}-{side}"
    return raw[:48]


def _equity(broker: PaperBroker | None, submit: bool) -> float:
    env = os.environ.get("PAPER_EQUITY")
    fallback = float(env) if env else DEFAULT_PAPER_EQUITY
    if not submit or broker is None or not broker.has_credentials():
        return fallback
    account = broker.get_account()
    raw = account.get("equity") or account.get("portfolio_value") or fallback
    return float(raw)


def run_daily_session(
    *,
    as_of: date | None = None,
    submit_paper: bool = False,
    broker: PaperBroker | None = None,
    bars: list[Bar] | None = None,
    ledger: FillLedger | None = None,
    equity: float | None = None,
) -> dict[str, Any]:
    assert_paper_only()
    session = session_date(as_of)
    report: dict[str, Any] = {
        "live_trading": LIVE_TRADING,
        "session_date": session.isoformat(),
        "submit_paper": bool(submit_paper),
        "symbol": "SPY",
        "sleeves": [],
        "skipped": [],
        "submitted": [],
        "intended": [],
    }
    spy = bars if bars is not None else fetch_chart("SPY")
    spy = [b for b in spy if b.date <= session]
    if not spy:
        raise RuntimeError("No SPY bars on or before session date")

    ledger = ledger or FillLedger(STATE_DIR / "fill_ledger.json")
    sleeve_path = STATE_DIR / "sleeves.json"
    sleeve_state: dict[str, Any] = {}
    if sleeve_path.exists():
        sleeve_state = json.loads(sleeve_path.read_text(encoding="utf-8"))

    if submit_paper:
        broker = broker or PaperBroker()
        if not broker.has_credentials():
            raise PaperBrokerError(
                "Refusing paper submit without APCA_API_KEY_ID / APCA_API_SECRET_KEY"
            )

    nav = equity if equity is not None else _equity(broker, submit_paper)
    report["equity"] = nav
    last_price = spy[-1].close
    report["last_bar"] = {"date": spy[-1].date.isoformat(), "close": last_price}

    for sleeve in SLEEVES:
        strategy = sleeve["strategy"]
        symbol = sleeve["symbol"]
        weight = float(sleeve["weight"])
        signal, _bar = last_signal(strategy, spy)
        target_notional = round(nav * weight, 2) if signal == 1 else 0.0
        held = float((sleeve_state.get(strategy) or {}).get("qty") or 0.0)
        side = None
        reason = "hold"
        if signal == 1 and held <= 0:
            side = "buy"
            reason = "enter"
        elif signal == 0 and held > 0:
            side = "sell"
            reason = "exit"
        elif signal == 1 and held > 0:
            reason = "already_long"
        else:
            reason = "flat"

        sleeve_row = {
            "strategy": strategy,
            "symbol": symbol,
            "weight": weight,
            "signal": signal,
            "held_qty": held,
            "target_notional": target_notional,
            "action": side or "none",
            "reason": reason,
        }

        if side == "buy" and ledger.already_bought(strategy, symbol, session):
            sleeve_row["action"] = "skipped"
            sleeve_row["reason"] = "duplicate_buy_same_calendar_date"
            report["skipped"].append(sleeve_row)
            report["sleeves"].append(sleeve_row)
            continue

        order: dict[str, Any] | None = None
        if side == "buy":
            order = {
                "symbol": symbol,
                "notional": str(target_notional),
                "side": "buy",
                "type": "market",
                "time_in_force": "day",
                "client_order_id": _client_order_id(strategy, symbol, session, "buy"),
            }
        elif side == "sell":
            order = {
                "symbol": symbol,
                "qty": str(held),
                "side": "sell",
                "type": "market",
                "time_in_force": "day",
                "client_order_id": _client_order_id(strategy, symbol, session, "sell"),
            }

        if order:
            report["intended"].append(order)
            if submit_paper:
                assert broker is not None
                filled = broker.submit_order(order)
                sleeve_row["broker_order"] = {
                    "id": filled.get("id"),
                    "status": filled.get("status"),
                    "client_order_id": filled.get("client_order_id"),
                }
                report["submitted"].append(sleeve_row["broker_order"])
            extra = {"notional": order.get("notional"), "qty": order.get("qty"), "submitted": bool(submit_paper)}
            ledger.record(
                strategy=strategy,
                symbol=symbol,
                session=session,
                side=side,
                extra=extra,
            )
            if side == "buy":
                qty = target_notional / last_price if last_price else 0.0
                sleeve_state[strategy] = {
                    "symbol": symbol,
                    "qty": qty,
                    "last_buy_date": session.isoformat(),
                }
            else:
                sleeve_state[strategy] = {"symbol": symbol, "qty": 0.0, "last_sell_date": session.isoformat()}

        report["sleeves"].append(sleeve_row)

    sleeve_path.parent.mkdir(parents=True, exist_ok=True)
    sleeve_path.write_text(json.dumps(sleeve_state, indent=2) + "\n", encoding="utf-8")
    session_path = STATE_DIR / f"session-{session.isoformat()}.json"
    session_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report["state_file"] = str(session_path)
    return report


def main(argv: list[str] | None = None) -> int:
    import argparse

    assert_paper_only()
    parser = argparse.ArgumentParser(description="Daily paper session for SPY sleeves.")
    parser.add_argument("--as-of", default=None, help="Calendar date YYYY-MM-DD (default: today ET)")
    parser.add_argument(
        "--submit-paper",
        action="store_true",
        help="POST orders to paper-api.alpaca.markets (requires paper keys). Default is local ledger only.",
    )
    args = parser.parse_args(argv)
    as_of = date.fromisoformat(args.as_of) if args.as_of else None
    report = run_daily_session(as_of=as_of, submit_paper=bool(args.submit_paper))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
