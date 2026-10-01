# Paper trading the candidate

What is carried forward to paper trading, how to produce each month's
list, and how the record will be read. Decisions 24 (the candidate), 25
(the floor), 28 to 36 of the
[decision log](notes/2026-09-29-decisions.md). Evidence:
[backtests to 2023](notes/2026-09-30-backtests.md),
[the run to 2026](notes/2026-10-01-out-of-sample.md),
[same-size peers and large caps](notes/2026-10-01-large-caps.md).

Nothing here is a performance claim. The figures are simulated,
cost-adjusted and selection-biased (35 backtest configurations on the
same years); paper trading is the first evidence that will not be.

## What is traded

Two paper portfolios that buy the same ten stocks each month and
differ only in whether they sell:

| | buys | sells |
|---|---|---|
| **A, buy and hold** (the base case) | the month's 10 picks, equal amounts | never |
| **B, rank sell discipline** | the same | a holding is sold once it is outside the top 20% of the month's ranking, or no longer in it |

## The three models, and what "momentum" and "return on capital" are

The picks come from three rankings of the same stocks, averaged. Only
the first is a trained model. The other two are single columns of the
dataset wrapped as "models" (`rank_factor`: no parameters are learned,
the score is the column), so that the backtest, `vml-eval` and
`vml-predict` can treat all three alike and combine them by rank.

| leg | config | what it is | what it contributes |
|---|---|---|---|
| **the forest** | `experiments/forest_nonloser_dd30_3y.toml` | a random forest on the 112 rank columns, trained to predict "not a loser" (`fwd_3y_cagr >= 0 & fwd_3y_max_drawdown_from_entry < 0.3`) | few losers, shallow falls. Walk-forward p@20 0.79 against a base rate of 0.39; holdout (look 1 of 1) 0.65, top 50 0.73, against 0.38 |
| **momentum** | `experiments/factor_mom_12_2_3y.toml` | the column `mom_12_2_rank`: the stock's return over the past twelve months leaving out the latest, ranked against the other stocks; highest first | the winners the forest gives up. Useless alone (the worst factor on the screen) |
| **return on capital** | `experiments/factor_roc_greenblatt_3y.toml` | the column `roc_greenblatt_rank`: operating profit over the capital the business employs (Greenblatt's definition), ranked; highest first, a stock without one last | quality; and it is what moves the picks out of utilities and real estate (35% of the forest's own picks, 1% of the blend's) |

`vml-predict` given one bundle ranks today's stocks by that model, as
it always has. Given several, it ranks the stocks on each and writes
one list ordered by the **mean of the ranks**: that list is the
blend. So `vml-predict <forest> <momentum> <return-on-capital> ...`
means "the three bundle directories".

## The rule

Each month, on the stocks with `dollar_volume_3m_rank >= 0.2` (the
least-traded fifth is left out; Carter's choice of floor, decision
25): rank them on each of the three legs, average the three ranks,
walk down the list and take the first ten, skipping a stock once two
of the picks already share its sector. Equal amounts in each.

## Once: build the three deployment bundles

A deployment bundle is the config's model refit on every labeled row
(`docs/deployment.md`). Bundles are git-ignored and do not travel with
the repository, so build them where the paper trading runs:

```sh
uv run vml-train-deploy experiments/forest_nonloser_dd30_3y.toml     # about a minute
uv run vml-train-deploy experiments/factor_mom_12_2_3y.toml          # seconds: nothing is fitted
uv run vml-train-deploy experiments/factor_roc_greenblatt_3y.toml
```

Each prints its bundle directory
(`experiments/models/<name>_deployment_<run id>`). The forest is
deterministic for its seed. Refit the forest when a new dataset
version arrives, and at least once a year: the backtest's forest is
refit every year end, on the rows whose three-year outcome is known
by then.

## Each month: the list

1. Get the inference dataset from upstream (`make inference`:
   `data/datasets/inference_<date>/`). Check `manifest.json`: `as_of`
   is the day you expect and `rows_with_stale_price` is small
   (data/manual.md §9).
2. Produce the list:

   ```sh
   uv run vml-predict \
       experiments/models/forest_nonloser_dd30_3y_deployment_<id> \
       experiments/models/factor_mom_12_2_3y_deployment_<id> \
       experiments/models/factor_roc_greenblatt_3y_deployment_<id> \
       data/datasets/inference_<date> \
       --filter "dollar_volume_3m_rank >= 0.2" --pick 10 --max-per-group 2
   ```

   It prints the ten picks and writes the full ranking to
   `predictions/` with a `pick` column (1 to 10), the sector, and each
   leg's rank and score. The sidecar `.meta.json` records the bundles,
   the filter and the rule.
3. **Portfolio A:** buy the ten, equal amounts, on the next trading
   day. Keep the CSV: it is the record of what was chosen and why.
4. **Portfolio B:** buy the same ten. Then, for every stock already
   held, find its row in the full ranking. Sell it if it is not in
   the file, or if its position (row number divided by the number of
   rows) is beyond 0.20. In the backtest this sold about 15 holdings
   a year.

The backtest buys on the first trading day of the month with 35 bps
a side. Use fractional shares, or an amount per pick well above the
share prices: with whole shares at 100 a pick the backtest filled
only 64 to 87 of 120 orders a year after 2020 (it did not change the
result, but it is a rule nobody chose).

## Checked end to end (2026-10-01)

The three deployment bundles were built in the sandbox
(1,387,763 labeled rows, effective size 47,994) and `vml-predict` was
run with the flags above on the cross-section the backtest saw on
2026-08-03 (each stock's latest completed-quarter snapshot; 3,057
stocks after the floor, the backtest's own count). Nine of its ten
picks are the backtest's ten for that month (JCI, GOOGL, JNJ, EA, CW,
RPRX, AAPL, ESE, FTI; CAT where the backtest had PH). The one
difference is the forest: the deployment fit has seen more rows than
the backtest's year-end refit for 2026. This was a check of the path,
not a list to trade: a real run needs a real inference dataset, whose
ranks are taken fresh over that day's stocks.

## What it has shown

Simulated, 35 bps a side, 1,000 a month:

| | 2005–2020, a year | 2021 to 2026-08 | whole period | worst drawdown | final value on 260,000 |
|---|---|---|---|---|---|
| SPY, same deposits | 9.4% | 15.4% | 10.9% | −52.9% | 1,326,084 |
| A, buy and hold | 12.7% | 7.3% | 11.3% | −41.4% | 1,193,902 |
| B, sell discipline | 13.6% | 7.6% | 12.0% | −39.6% | 1,344,630 |

- 2005–2020: ahead of SPY by 3.3 (A) and 4.2 (B) points a year, in
  both halves (the dollar-floor version was repeated on three forest
  seeds); per buy, +2.5 points a year over three years, 61% of buys
  beating SPY, 20% losing money; against stocks of their own size,
  +4.6 and +5.9 points a year in the two halves.
- 2021–2026: behind SPY in five of six years (2022: ahead by 3.2
  points; 2024 to 2026: behind by 9 to 14). The buys of 2021–23
  trailed SPY by 11 to 17 points a year over three years, were about
  level with stocks of their own size (−1.6 points a year), and 32%
  to 41% lost money.
- The forest on the sealed holdout (2021–23 snapshots): top 20 a year
  right 0.65 of the time, top 50 0.73, base rate 0.38.

## The assumption it is traded under, and what would count against it

Carter's working assumption (decision 36): 2021–26 is a bubble led by
stocks that fail a value investor's test; a value strategy trails
through it and leads again during and after the correction. The
support and the limits are in decision 35: on 1999–2004 a stand-in
for the candidate led by 9 points a year for the buys of 2000–02;
the years in which that bubble grew are before the data.

So that the paper record can be read against something written
beforehand:

- *Expected under the assumption, while the market keeps rising as it
  has:* trailing SPY by something like the 9 to 14 points a year of
  2024–26, with the picks' share of losers staying well under the
  average stock's and their lead over same-size stocks near zero.
- *Expected in a correction:* ahead of SPY, by more than in 2022
  (+3.2 points) and towards 2008 (+11.4), and ahead of same-size
  stocks.
- *What would count against it:* a fall of 20% or more in SPY through
  which the portfolios are not ahead of it; or the picks losing money
  as often as stocks of their own size for a year or more (2021–23:
  22% of the forest's picks against 34% of their peers).

Read the record on three things, in this order: the picks against
stocks of their own size (`vs_peers`: selection), the share of picks
losing money, and the portfolios against SPY.

## Reproduce the evidence

```sh
uv run vml-run experiments/forest_nonloser_dd30_3y.toml          # the fold bundle, about 5 min
uv run vml-run experiments/factor_mom_12_2_3y.toml
uv run vml-run experiments/factor_roc_greenblatt_3y.toml
# point `bundles` in the portfolio configs at the three directories, then
uv run vml-backtest experiments/portfolios/bt_nonloser_mom_roc_top10_cap2_rankfloor_to2026.toml         # A
uv run vml-backtest experiments/portfolios/bt_nonloser_mom_roc_top10_cap2_rankfloor_sell20_to2026.toml  # B
```

Promoted reports: `reports/promoted/` (`forest_nonloser_dd30_3y`,
`factor_mom_12_2_3y`, `factor_roc_greenblatt_3y`, and the two
backtests `bt_nonloser_mom_roc_top10_cap2_rankfloor_to2026_*` and
`..._sell20_to2026_*`). The backtest reports print each year's buys
against all candidates and against same-size peers.
