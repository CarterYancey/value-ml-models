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
the score columns. Both deployment
training and inference runs are logged to `experiments/results.csv` under
their own schemes (`deployment` / `inference`), so they never mix with
walk-forward trial accounting.
