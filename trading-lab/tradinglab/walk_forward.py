"""Walk-forward evaluation: 756 train / 252 test / 126 step."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

from .config import (
    INDICATOR_WARMUP,
    LIVE_TRADING,
    RECENT_OOS_END,
    RECENT_OOS_START,
    RISK_HALT_DRAWDOWN,
    UNIVERSE,
    WALK_FORWARD_STEP_DAYS,
    WALK_FORWARD_TEST_DAYS,
    WALK_FORWARD_TRAIN_DAYS,
    assert_paper_only,
)
from .metrics import apply_risk_halt, daily_returns, strategy_returns, summarize
from .strategies import STRATEGY_FNS, TACTICAL_STRATEGIES, signal_for
from .yahoo import Bar, fetch_universe

STRATEGIES = tuple(STRATEGY_FNS.keys())


def _slice_metrics(
    signals: list[int],
    asset_rets: list[float],
    start: int,
    end: int,
) -> dict[str, float]:
    sr = strategy_returns(signals, asset_rets)
    window_rets = sr[start:end]
    window_sig = signals[start:end]
    return summarize(window_rets, window_sig)


def walk_forward_symbol(
    bars: list[Bar],
    *,
    train_days: int = WALK_FORWARD_TRAIN_DAYS,
    test_days: int = WALK_FORWARD_TEST_DAYS,
    step_days: int = WALK_FORWARD_STEP_DAYS,
    warmup: int = INDICATOR_WARMUP,
    strategies: Iterable[str] = STRATEGIES,
) -> list[dict]:
    closes = [b.close for b in bars]
    dates = [b.date.isoformat() for b in bars]
    rets = daily_returns(closes)
    signals = {name: signal_for(name, closes) for name in strategies}
    n = len(closes)
    folds: list[dict] = []
    t = warmup
    fold_id = 0
    while t + train_days + test_days <= n:
        train_start, train_end = t, t + train_days
        test_start, test_end = train_end, train_end + test_days
        train_stats = {
            name: _slice_metrics(sig, rets, train_start, train_end)
            for name, sig in signals.items()
        }
        test_stats = {
            name: _slice_metrics(sig, rets, test_start, test_end)
            for name, sig in signals.items()
        }
        train_winner = _rank(train_stats)[0]
        test_winner = _rank(test_stats)[0]
        folds.append(
            {
                "fold": fold_id,
                "train_start": dates[train_start],
                "train_end": dates[train_end - 1],
                "test_start": dates[test_start],
                "test_end": dates[test_end - 1],
                "train": train_stats,
                "test": test_stats,
                "train_winner": train_winner,
                "test_winner": test_winner,
            }
        )
        fold_id += 1
        t += step_days
    return folds


def _rank(stats: dict[str, dict[str, float]]) -> list[str]:
    """Higher Sharpe, then higher CAGR, then shallower drawdown."""

    def key(name: str) -> tuple[float, float, float]:
        row = stats[name]
        return (row["sharpe"], row["cagr"], row["max_drawdown"])

    return sorted(stats, key=key, reverse=True)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def summarize_folds(folds: list[dict], strategies: Iterable[str] = STRATEGIES) -> dict:
    oos: dict[str, dict[str, list[float]]] = {
        name: {"sharpe": [], "cagr": [], "max_drawdown": []} for name in strategies
    }
    train_winners: list[str] = []
    test_winners: list[str] = []
    for fold in folds:
        train_winners.append(fold["train_winner"])
        test_winners.append(fold["test_winner"])
        for name in strategies:
            row = fold["test"][name]
            oos[name]["sharpe"].append(row["sharpe"])
            oos[name]["cagr"].append(row["cagr"])
            oos[name]["max_drawdown"].append(row["max_drawdown"])
    mean_oos = {
        name: {
            "mean_oos_sharpe": round(_mean(vals["sharpe"]), 6),
            "mean_oos_cagr": round(_mean(vals["cagr"]), 6),
            "mean_oos_max_drawdown": round(_mean(vals["max_drawdown"]), 6),
            "folds": len(vals["sharpe"]),
        }
        for name, vals in oos.items()
    }
    ranking = sorted(
        mean_oos,
        key=lambda n: (mean_oos[n]["mean_oos_sharpe"], mean_oos[n]["mean_oos_cagr"]),
        reverse=True,
    )
    return {
        "fold_count": len(folds),
        "train_winner_counts": dict(Counter(train_winners)),
        "test_winner_counts": dict(Counter(test_winners)),
        "most_frequent_train_winner": Counter(train_winners).most_common(1)[0][0]
        if train_winners
        else None,
        "mean_oos": mean_oos,
        "ranking_by_mean_oos_sharpe": ranking,
        "walk_forward_winner": ranking[0] if ranking else None,
    }


def window_stats(
    bars: list[Bar],
    start: date,
    end: date,
    strategies: Iterable[str] = TACTICAL_STRATEGIES,
) -> dict:
    closes = [b.close for b in bars]
    rets = daily_returns(closes)
    idx = [i for i, b in enumerate(bars) if start <= b.date <= end]
    if len(idx) < 2:
        return {"error": "insufficient bars in window", "start": start.isoformat(), "end": end.isoformat()}
    a, b = idx[0], idx[-1] + 1
    stats = {}
    for name in strategies:
        sig = signal_for(name, closes)
        stats[name] = _slice_metrics(sig, rets, a, b)
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "bars": b - a,
        "ranking_by_sharpe": _rank(stats),
        "stats": stats,
    }


def full_sample_risk_note(bars: list[Bar]) -> dict:
    closes = [b.close for b in bars]
    rets = daily_returns(closes)
    bh_sig = signal_for("buy_hold", closes)
    bh_rets = strategy_returns(bh_sig, rets)
    unhalted = summarize(bh_rets, bh_sig)
    capped = {}
    for name in TACTICAL_STRATEGIES:
        raw = signal_for(name, closes)
        halted = apply_risk_halt(raw, rets, RISK_HALT_DRAWDOWN, closes)
        sr = strategy_returns(halted, rets)
        capped[name] = summarize(sr, halted)
    unhalted_cagr = unhalted["cagr"]
    beat = all(unhalted_cagr >= row["cagr"] for row in capped.values())
    return {
        "risk_halt_drawdown": RISK_HALT_DRAWDOWN,
        "unhalted_buy_hold": unhalted,
        "risk_capped_tactical": capped,
        "unhalted_buy_hold_beats_risk_capped": beat,
        "note": (
            "Full-sample unhalted buy-hold still beats risk-capped systems because of 2020: "
            "a 20% strategy drawdown halt that waits for a new price high sits in cash through "
            "the V-recovery."
        ),
    }


def run_walk_forward(
    bars_by_symbol: dict[str, list[Bar]],
    *,
    train_days: int = WALK_FORWARD_TRAIN_DAYS,
    test_days: int = WALK_FORWARD_TEST_DAYS,
    step_days: int = WALK_FORWARD_STEP_DAYS,
) -> dict:
    assert_paper_only()
    per_symbol: dict[str, dict] = {}
    for symbol, bars in bars_by_symbol.items():
        folds = walk_forward_symbol(
            bars,
            train_days=train_days,
            test_days=test_days,
            step_days=step_days,
        )
        summary = summarize_folds(folds)
        recent = window_stats(
            bars,
            date.fromisoformat(RECENT_OOS_START),
            date.fromisoformat(RECENT_OOS_END),
        )
        per_symbol[symbol] = {
            "bars": len(bars),
            "first_bar": bars[0].date.isoformat() if bars else None,
            "last_bar": bars[-1].date.isoformat() if bars else None,
            "folds": folds,
            "summary": summary,
            "recent_oos": recent,
            "full_sample_risk": full_sample_risk_note(bars),
        }

    aggregate_scores: dict[str, list[float]] = defaultdict(list)
    winners: dict[str, str | None] = {}
    tactical_winners: dict[str, str | None] = {}
    for symbol, payload in per_symbol.items():
        winners[symbol] = payload["summary"]["walk_forward_winner"]
        mean_oos = payload["summary"]["mean_oos"]
        tactical_rank = [
            name
            for name in payload["summary"]["ranking_by_mean_oos_sharpe"]
            if name in TACTICAL_STRATEGIES
        ]
        tactical_winners[symbol] = tactical_rank[0] if tactical_rank else None
        payload["summary"]["tactical_ranking_by_mean_oos_sharpe"] = tactical_rank
        payload["summary"]["tactical_walk_forward_winner"] = tactical_winners[symbol]
        for name, row in mean_oos.items():
            aggregate_scores[name].append(row["mean_oos_sharpe"])
    aggregate_mean = {
        name: round(_mean(vals), 6) for name, vals in aggregate_scores.items()
    }
    overall_rank = sorted(aggregate_mean, key=aggregate_mean.get, reverse=True)
    tactical_rank = [name for name in overall_rank if name in TACTICAL_STRATEGIES]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "live_trading": LIVE_TRADING,
        "data_source": "yahoo_v8_chart",
        "user_agent_required": True,
        "universe": list(bars_by_symbol),
        "window": {
            "train_days": train_days,
            "test_days": test_days,
            "step_days": step_days,
            "warmup_days": INDICATOR_WARMUP,
        },
        "strategies": list(STRATEGIES),
        "execution": "signal at close t, return from close t to close t+1",
        "winners": {
            "by_symbol_mean_oos_sharpe": winners,
            "overall_ranking_by_mean_oos_sharpe": overall_rank,
            "overall_walk_forward_winner": overall_rank[0] if overall_rank else None,
            "tactical_by_symbol": tactical_winners,
            "tactical_ranking_by_mean_oos_sharpe": tactical_rank,
            "tactical_walk_forward_winner": tactical_rank[0] if tactical_rank else None,
            "aggregate_mean_oos_sharpe": aggregate_mean,
        },
        "symbols": per_symbol,
        "prior_oos_context": {
            "window": [RECENT_OOS_START, RECENT_OOS_END],
            "stated_rank": ["dual_momentum_3m", "sma_10_50", "trend_pullback"],
        },
    }


def winners_snapshot(report: dict) -> dict:
    recent_ranks = {
        symbol: payload["recent_oos"].get("ranking_by_sharpe")
        for symbol, payload in report["symbols"].items()
    }
    return {
        "generated_at": report["generated_at"],
        "live_trading": report["live_trading"],
        "window": report["window"],
        "walk_forward_winners": report["winners"],
        "recent_oos_rank_by_symbol": recent_ranks,
        "full_sample_unhalted_buy_hold_vs_risk_capped": {
            symbol: payload["full_sample_risk"]["unhalted_buy_hold_beats_risk_capped"]
            for symbol, payload in report["symbols"].items()
        },
    }


def write_report(report: dict, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    full_path = out_dir / "walk_forward.json"
    winners_path = out_dir / "walk_forward_winners.json"
    full_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    winners_path.write_text(json.dumps(winners_snapshot(report), indent=2) + "\n", encoding="utf-8")
    return full_path, winners_path


def main(argv: list[str] | None = None) -> int:
    import argparse

    assert_paper_only()
    parser = argparse.ArgumentParser(description="Walk-forward SPY/QQQ/IWM on Yahoo chart data.")
    parser.add_argument("--symbols", default=",".join(UNIVERSE))
    parser.add_argument("--out-dir", default=str(Path(__file__).resolve().parents[1] / "results"))
    args = parser.parse_args(argv)
    symbols = tuple(s.strip().upper() for s in args.symbols.split(",") if s.strip())
    bars = fetch_universe(symbols)
    report = run_walk_forward(bars)
    full_path, winners_path = write_report(report, Path(args.out_dir))
    print(json.dumps(report["winners"], indent=2))
    print(f"wrote {full_path}")
    print(f"wrote {winners_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
