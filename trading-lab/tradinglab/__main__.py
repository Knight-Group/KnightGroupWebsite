"""CLI: python -m tradinglab {walk-forward,daily-session}"""

from __future__ import annotations

import argparse
import sys

from .config import LIVE_TRADING, assert_paper_only


def main(argv: list[str] | None = None) -> int:
    assert_paper_only()
    parser = argparse.ArgumentParser(
        prog="python -m tradinglab",
        description="Paper-only trading lab. LIVE_TRADING is hardcoded False.",
    )
    parser.add_argument(
        "command",
        choices=("walk-forward", "daily-session"),
        help="walk-forward writes JSON results; daily-session sizes SPY sleeves",
    )
    parser.add_argument("rest", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    rest = list(args.rest)
    if rest and rest[0] == "--":
        rest = rest[1:]

    if args.command == "walk-forward":
        from .walk_forward import main as wf_main

        return wf_main(rest)
    from .daily_session import main as session_main

    return session_main(rest)


if __name__ == "__main__":
    if LIVE_TRADING is not False:
        print("LIVE_TRADING is disabled", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main())
