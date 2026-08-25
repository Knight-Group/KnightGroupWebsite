# Paper-only trading lab

This lab backtests and **papers** three sleeves. It does **not** place live brokerage orders.

`LIVE_TRADING = False` is hardcoded in `tradinglab/config.py`. The broker client allowlists **only** `paper-api.alpaca.markets` and refuses `api.alpaca.markets`. Environment variables such as `APCA_API_BASE_URL` are ignored so a leftover live URL cannot override the host. Old Tradier tokens are not used and `TRADIER_*` is never read.

Prior OOS context (2024-06-25 to 2026-08-24) ranked `dual_momentum_3m`, then `sma_10_50`, then `trend_pullback`. Full-sample **unhalted buy-hold** still beats **risk-capped** systems because a 20% drawdown halt that waits for a new price high sits out the 2020 V-recovery.

## Setup

Python 3.10+ standard library only. No brokerage SDKs.

```bash
cd trading-lab
cp .env.example .env   # paper keys only; never commit .env
```

## Walk-forward (Yahoo chart API)

756-day train / 252-day test / 126-day step on **SPY, QQQ, IWM**. Prices come from the Yahoo v8 chart API; a User-Agent is required.

```bash
cd trading-lab
python3 -m tradinglab walk-forward
python3 -m tradinglab walk-forward -- --symbols SPY,QQQ,IWM --out-dir results
```

Writes:

- `results/walk_forward.json` — per-fold train/test metrics
- `results/walk_forward_winners.json` — compact winner snapshot

## Daily paper session (SPY sleeves)

Weights: `dual_momentum_3m` 50%, `sma_10_50` 30%, `trend_pullback` 20%. One buy per strategy+symbol+calendar date (ledger + Alpaca `client_order_id`).

```bash
cd trading-lab
python3 -m tradinglab daily-session
python3 -m tradinglab daily-session -- --as-of 2026-08-25
python3 -m tradinglab daily-session -- --submit-paper
```

`--submit-paper` POSTs to `https://paper-api.alpaca.markets` only, and only with `APCA_API_KEY_ID` / `APCA_API_SECRET_KEY` (or `ALPACA_API_KEY` / `ALPACA_SECRET_KEY`). Without that flag the session writes intended orders to `state/` and does not call a broker.

## Tests

```bash
cd trading-lab
python3 -m unittest discover -s tests -v
```

## Strategies

| Name | Rule |
| --- | --- |
| `dual_momentum_3m` | Long SPY if 63-day (≈3 month) return > 0, else cash |
| `sma_10_50` | Long while SMA(10) > SMA(50) |
| `trend_pullback` | In an uptrend (close > SMA(50)), buy the recross of SMA(10) after a pullback; exit under SMA(50) |

Execution in research: signal at close *t*, return from close *t* to close *t+1*.

## Safety

- Live Alpaca host `api.alpaca.markets` is refused.
- Only HTTPS to `paper-api.alpaca.markets` is allowlisted.
- Do not commit `.env`, API keys, or `state/` ledgers.
- Do not paste old Tradier tokens into this project.
