# Deployment: train on everything, score today's stocks

During development, every measurement uses purged walk-forward splits.
The model that *ships* is refit on **all** labeled rows: every snapshot
kind, delistings included, no split filtering. Rule 7 in data/manual.md
section 4 allows this. The holdout and the purging only constrain how the harness measures a
model. They do not limit what the deployed model may learn from. A deployment fit
has no fold to test on, so its scores are rankings, never performance
numbers.

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

`vml-predict` writes the full ranking, in descending score order, to
`predictions/<inference>__<bundle>.csv`. The `--output` flag overrides
that path. It also writes a provenance sidecar, `.meta.json`, that holds
the bundle, the git SHA, the config hash and the row count. It prints the
top 50, and `--top` changes that count. With several bundles the combined
CSV goes to `predictions/<inference>__multi__<names>.csv`. Each model
still gets its own logged inference run, and the sidecar lists every
bundle. Each model's score is on its own probability or margin scale, so a
comparison across models uses the `rank_*` columns. `--trends` carries
the long-horizon trend columns verbatim from the inference data into
either CSV, after the score columns. Those columns are
`revenue_trend_20q`, `tangibles_trend_20q`, `ocf_trend_20q`,
`div_years_paid_10y` and `div_cuts_10y`. A bundle whose config has a
`[[universe]]` is refit inside it and ranks only the inference rows
inside it. docs/experiments.md describes universes. In a combined run
the ranked rows are the ones inside every model's universe. The sidecar
names the universe and counts the rows left out.

**`vml-predict` can apply the backtest's selection to the ranking.** A
backtest does three things between a ranking and a buy:

1. It leaves out the rows that fail its `[[investability]]` filters
   *before* it ranks the models.
2. It walks the ranking in order.
3. It skips a stock once `max_per_group` of the month's buys share its
   sector.

`vml-predict` does the same with

```sh
uv run vml-predict <forest> <momentum> <return-on-capital> \
    data/datasets/inference_2026-10-01 \
    --filter "dollar_volume_3m_rank >= 0.2" \
    --pick 10 --max-per-group 2
```

- `--filter 'COLUMN OP VALUE'` keeps only the rows that pass it. The
  flag is repeatable, the filters are ANDed, and a NULL fails. The filter
  applies after the bundles' universe and before `vml-predict` takes any
  rank, so
  `mean_rank` is the backtest's `combine = "mean_rank"` over its
  investable rows. A mean of ranks taken over every row and filtered
  afterwards is a different ranking. With an inference `manifest.json`
  the column must be in its `features`, `ranks` or `sector_ranks`
  groups.
- `--pick K` adds a `pick` column, numbered 1 to K down the ranking, and
  prints the picks instead of the top rows. `--max-per-group N` skips a
  row once N of the picks share its `--group-column`. The default group
  column is `sector`, and a NULL group counts as one group. This is the
  walk of `portfolio.strategy.capped_top_k`. Fewer than K picks come
  back when the groups run out. The CSV carries the group column.
- The sidecar records the filters, the rows they left out and the
  selection rule. `vml-predict` still writes the full ranking. The picks
  are a marked subset of it.

The list is what a backtest with the same rule would have bought on
that cross-section. It is not a result, because a deployment fit has no
fold to test on. `vml-predict` ranks an inference cross-section fresh on one
day, where the backtest ranks snapshots up to a quarter old. See
docs/backtesting.md.

## A deployment refit without the most recent years

`--train-end DATE` sets a training cutoff (decision 60). The refit then
fits only the labeled rows whose `snapshot_date` is before the date.
Every snapshot kind and every delisted row before the date stays in,
and no split tag is read. The cutoff is on the entry date, so a row
before it keeps its label even when the label's window runs past the
date. A forest that has seen no price from 2021 on therefore needs a
cutoff three years earlier, 2018-01-01 for a three-year label.

```sh
uv run vml-train-deploy experiments/forest_nonloser_dd30_3y_v141.toml --train-end 2021-01-01
```

The bundle records `train_end` and `last_snapshot_date`. The ledger row
has `labeled_before_2021-01-01` in its `fold` column where the full
refit has `all_labeled`. Every sidecar that `vml-predict` writes from
the bundle carries both fields and says so in its note. So a cutoff fit
is never mistaken for the full refit. A rank factor fits nothing, so a
cutoff changes nothing for it.

`scripts/compare_predictions.py` compares two `vml-predict` rankings
over the same inference dataset and the same flags:

```sh
python scripts/compare_predictions.py \
    predictions/inference_2026-11-20__candidate_full_v141.csv \
    predictions/inference_2026-11-20__candidate_pre2021_v141.csv \
    --label-a full --label-b pre2021
```

It reports five things:

- each ranking's picks, with their position under the other ranking
- how many of the top 10 to 200 the two share, by mean rank and by each leg that differs
- the Spearman correlation of the ranks
- the largest moves of the leg that differs
- the sector mix of the top 50

It refuses two rankings over different rows. Both rankings are deployment scores, so
the report says where they differ and nothing about which is better.

## Historical analogues: what today's picks resemble

`vml-analogues` takes the same bundles, inference data and selection
flags as `vml-predict`. For each pick it lists the historical stocks
most similar to it **as the models see it**, with what they went on
to do:

```sh
uv run vml-analogues <forest> <momentum> <return-on-capital> \
    data/datasets/inference_2026-10-01 \
    --filter "dollar_volume_3m_rank >= 0.2" --pick 10 --max-per-group 2
# or named stocks instead of the picks:
uv run vml-analogues <bundles...> <inference> --tickers JNJ,AAPL --top 25
```

- **Similarity is defined per model and averaged over the models of a
  blend.** For a tree model it is the share of trees in which the
  historical row lands in the same leaf as the pick. The tree models are
  the forest, the single tree, LightGBM and XGBoost. This uses the
  model's own thresholds and NULL routing, with no distance metric, no
  imputation and no scaling. For a rank factor the similarity is one
  minus the distance on its column, and NULL matches NULL.
- **The pool is the dataset version the bundles were trained on.** It
  holds median-kind rows with an observable outcome over the longest
  bundle horizon, from every era, delisted stocks included. The report
  lists one row per stock, its most similar snapshot. It leaves the
  pick's own history out unless the run passes `--include-self`.
- **The output sits beside the ranking that `vml-predict` would write.**
  The report, `..__analogues.md`, has a summary per pick against the
  whole pool. It lists the features the tree model split on along the
  pick's paths, with the pick's values. It lists the `--top` analogues,
  15 by default, with ticker, snapshot date, similarity per model,
  outcomes and those features. Every row goes to `..__analogues.csv`,
  and a `.meta.json` sidecar accompanies them.

**The analogues explain a pick and do not evaluate it.** The deployment
model learned from these very rows. The rows that share a pick's leaves
are the rows that made those leaves, so the analogues' outcome rates are
in-sample by construction. They say what kind of history a pick
resembles. They are not an accuracy or a probability for it, and nothing
here is ever a model input. Outcomes follow the dataset's label
convention, which carries a delisted stock's final price flat to the
horizon. Inference ranks are pooled over one day, where training ranks
are within a quarter.

The runner logs deployment training runs and inference runs to
`experiments/results.csv` under their own schemes, `deployment` and
`inference`. Walk-forward trial accounting therefore never counts them.
