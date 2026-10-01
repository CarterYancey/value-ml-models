# The candidate, in one place

What is carried forward from the sessions of 2026-09-29 to 2026-10-01,
how it was measured, how to reproduce it and how to run it on today's
stocks. Decisions: [decision log](2026-09-29-decisions.md), 24 and 26.
Evidence: [backtests](2026-09-30-backtests.md).

## What it is

Three rankings of the investable stocks, averaged by rank:

1. **Cell C's forest**: `experiments/forest_nonloser_dd30_3y.toml`, a
   random forest on the 112 rank columns predicting "not a loser"
   (`fwd_3y_cagr >= 0 & fwd_3y_max_drawdown_from_entry < 0.3`).
   p@20 0.79 against a base rate of 0.39.
2. **12-month momentum**: `experiments/factor_mom_12_2_3y.toml`
   (highest `mom_12_2_rank`).
3. **Return on capital**: `experiments/factor_roc_greenblatt_3y.toml`
   (highest `roc_greenblatt_rank`; a stock without one ranks last on
   it, which is what keeps REITs out).

Each month: rank the stocks with `dollar_volume_3m >= 100000` on each
of the three, average the three ranks, buy the top 10 with at most 2
per sector, equal amounts. Base case: never sell. Variant: sell a
holding once it is outside the top 20% of the month's ranking
(`[sell] max_rank_pct = 0.2`).

## What it has shown (simulated, 35 bps a side, 1,000 a month)

| | final value | deposits | time-weighted | worst drawdown |
|---|---|---|---|---|
| SPY, buys 2005–2020, valued end 2023 | 732,110 | 192,000 | 9.58% | −52.9% |
| candidate, three forest seeds | 949,000–960,000 | 192,000 | 12.2% | −41% to −42% |
| candidate with the sell discipline, three seeds | 1,028,000–1,091,000 | 192,000 | 12.7–13.1% | −39.5% to −40.5% |
| SPY, buys through 2023 | 774,140 | 228,000 | 9.58% | −52.9% |
| candidate, buys through 2023 (year-end refits) | 985,668 | 228,000 | 12.21% | −41.2% |

- Per buy, over the three years after the trade: +0.025 a year over
  SPY (+0.034 for the buys of 2005–12, +0.013 to +0.016 for 2013–20);
  61% of buys beat SPY, 20% lost money.
- Checks passed: three forest seeds (12.23–12.26%); fractional shares
  (12.12%); a rank floor `dollar_volume_3m_rank >= 0.2` in place of
  the dollar floor (12.15%).
- About 9 buys a month, 235 distinct stocks in sixteen years;
  consumer defensive, industrials, technology, healthcare and
  consumer cyclical are 15–17% each; utilities and real estate 1.4%.
  Largest holding at the end 8% (AAPL), five largest 26%.
- Ahead of SPY in 12 of 19 years, including 2008 (+9.5 points) and
  2022 (+4.6); 9.5 points behind in 2021.

## What it has not shown

- **Anything outside 2005–2023.** It is the best of 31 backtest
  configurations on the same sixteen buy years; its forest was chosen
  from 80 configurations on those years; low risk, quality and
  momentum are known to have paid in this period. Expect the lead to
  shrink.
- **The first years it was not chosen on are mixed.** Trading on
  through 2023, the portfolio's years are −9.6, +4.3 and −2.2 points
  against SPY, and the buys of 2021 trailed SPY by 15 points over
  their first year (77% lost money), the worst cohort of the sample
  (2020: −13.5; 2006: −11.0). 2022's trailed by 2.8.
- **The sealed holdout.** Cell C's 3y cell is unopened.
- Costs beyond 35 bps a side, market impact, taxes.

## Reproduce it

```sh
uv run vml-run experiments/forest_nonloser_dd30_3y.toml       # ~5 min, saves the fold bundle
uv run vml-run experiments/factor_mom_12_2_3y.toml
uv run vml-run experiments/factor_roc_greenblatt_3y.toml
# put the three bundle directories (experiments/models/<name>_<run id>)
# into `bundles` of the portfolio config, then
uv run vml-backtest experiments/portfolios/bt_nonloser_mom_roc_top10_cap2.toml         # ~2 min
uv run vml-backtest experiments/portfolios/bt_nonloser_mom_roc_top10_cap2_sell20.toml
uv run vml-backtest experiments/portfolios/bt_nonloser_mom_roc_top10_cap2_to2023.toml  # refits 2021-23, ~15 min the first time
```

The forest is deterministic for a seed: run `53ceedd93e6d` (seed 23)
reproduced p@20 0.7875 and fold-mean PR-AUC 0.585 on every re-fit,
and every re-run backtest reproduced its figures to the cent. The
configs of the seed, fractional-share, rank-floor and other check
runs are on the lab branch `claude/lab-2026-09-30`
(`experiments/portfolios/`), with every report.

## Run it on today's stocks (not done yet)

```sh
uv run vml-train-deploy experiments/forest_nonloser_dd30_3y.toml
uv run vml-train-deploy experiments/factor_mom_12_2_3y.toml
uv run vml-train-deploy experiments/factor_roc_greenblatt_3y.toml
uv run vml-predict <forest bundle> <momentum bundle> <return-on-capital bundle> \
    data/datasets/inference_<date>
```

`vml-predict` with several bundles writes one CSV ordered by the mean
of the three ranks, which is the blend. Two things the backtest does
that `vml-predict` does not, to be applied by hand until they are
built: **keep only rows with `dollar_volume_3m >= 100000` before
ranking** (filter the inference parquet first; the mean rank is taken
over whatever rows are scored), and **walk down the list taking at
most 2 per sector**. A deployment fit has no test set: the CSV is a
ranking, never a performance figure. This path was not run in these
sessions; the first run should be checked against the latest
backtest month's picks.
