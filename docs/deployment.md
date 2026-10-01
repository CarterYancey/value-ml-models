# Deployment: train on everything, score today's stocks

Development measures with purged walk-forward splits; the model that
*ships* is refit on **all** labeled rows — every snapshot kind, delistings
included, no split filtering (data/manual.md §4 rule 7: the holdout/purge
discipline constrains measurement, not what the deployed model may learn
from). Deployment fits have no test set, so their scores are rankings,
never performance numbers.

```sh
# refit an already-selected config's model on all labeled data
# (the config's scheme/folds are ignored; saves a deployment bundle)
uv run vml-train-deploy experiments/tree_depth3_3y_beat_spy.toml

# score today's stocks: an inference dataset directory containing a
# dataset.parquet with the feature columns (no labels needed)
uv run vml-predict \
    experiments/models/<name>_deployment_<run_id> \
    data/datasets/inference_2026-07-22

# or several bundles at once: one combined CSV with a
# rank_<model>/score_<model> column pair per bundle, ordered by
# mean rank across the models
uv run vml-predict \
    experiments/models/<name_a>_deployment_<run_id> \
    experiments/models/<name_b>_deployment_<run_id> \
    data/datasets/inference_2026-07-22
```

`vml-predict` writes the full score-descending ranking to
`predictions/<inference>__<bundle>.csv` (override with `--output`), writes
a provenance sidecar `.meta.json` (bundle, git SHA, config hash, row
count), and prints the top 50 (`--top` to change). With several bundles
the combined CSV goes to `predictions/<inference>__multi__<names>.csv`,
each model still gets its own logged inference run, and the sidecar lists
every bundle; each model's score is its own probability/margin scale, so
cross-model comparison uses the `rank_*` columns. `--trends` carries the
long-horizon trend context columns (`revenue_trend_20q`,
`tangibles_trend_20q`, `ocf_trend_20q`, `div_years_paid_10y`,
`div_cuts_10y`) verbatim from the inference data into either CSV, after
the score columns. A bundle whose config has a `[[universe]]`
(docs/experiments.md) is refit inside it and ranks only the inference
rows inside it (a combined run, the rows inside every model's); the
sidecar names the universe and counts the rows left out.

**The backtest's selection, applied to the ranking.** A backtest does
three things between a ranking and a buy: it leaves out the rows that
fail its `[[investability]]` filters *before* the models are ranked, it
walks the ranking in order, and it skips a stock once `max_per_group`
of the month's buys share its sector. `vml-predict` does the same with

```sh
uv run vml-predict <forest> <momentum> <return-on-capital> \
    data/datasets/inference_2026-10-01 \
    --filter "dollar_volume_3m_rank >= 0.2" \
    --pick 10 --max-per-group 2
```

- `--filter 'COLUMN OP VALUE'` (repeatable, ANDed; a NULL fails) keeps
  only the rows passing it, after the bundles' universe and before any
  rank is taken, so `mean_rank` is the backtest's
  `combine = "mean_rank"` over its investable rows. A mean of ranks
  taken over every row and filtered afterwards is a different ranking.
  With an inference `manifest.json` the column must be in its
  `features`, `ranks` or `sector_ranks` groups.
- `--pick K` adds a `pick` column (1..K down the ranking) and prints
  the picks instead of the top rows; `--max-per-group N` skips a row
  once N of the picks share its `--group-column` (default `sector`; a
  NULL group counts as one group), the walk of
  `portfolio.strategy.capped_top_k`. Fewer than K picks come back when
  the groups run out. The group column is carried into the CSV.
- The sidecar records the filters, the rows they left out and the
  selection rule. The full ranking is still written: the picks are a
  marked subset of it.

The list is what a backtest with the same rule would have bought on
that cross-section, not a result: a deployment fit has no test set.
An inference cross-section is ranked fresh on one day, where the
backtest ranks snapshots up to a quarter old (docs/backtesting.md).

Both deployment
training and inference runs are logged to `experiments/results.csv` under
their own schemes (`deployment` / `inference`), so they never mix with
walk-forward trial accounting.
