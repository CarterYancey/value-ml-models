# PLAN — architecture & design

Theory and architecture for `value-ml-models`. Concrete tasks live in
[TODO.md](TODO.md); the dataset contract lives in
[data/manual.md](data/manual.md).

## 1. Objective

Train classification models that predict, from point-in-time fundamentals,
whether a stock will meet return criteria over multi-year horizons, and turn
calibrated predictions into ranked stock lists / portfolios.

The upstream label matrix defines the prediction cells: horizons
**H ∈ {1y, 2y, 3y, 5y}**, targets `label_{H}_cagr_ge_{0,5,8,10}` (absolute,
inclusive thresholds) and `label_{H}_beat_spy` (relative). One model per
(horizon, threshold) cell, sharing a common training/evaluation harness.
Continuous variants (`fwd_{H}_cagr`, `fwd_{H}_excess_cagr`) are available if
the regression reframe (§8) is ever pursued.

## 2. Design principles

- **Dataset is pinned and immutable.** Every experiment records the exact
  `dataset_vX.Y` it ran against. Fixing data bugs happens upstream, producing
  a new version; results across different dataset versions are never compared.
- **Splits come from upstream.** `splits.parquet` tags every row with a role
  per (scheme, fold, horizon); this repo *applies* tags, never constructs
  splits. Purge and embargo are already priced into the tags.
- **Explainability first.** v1 models are single decision trees, because rules
  like "P/B rank < X → Y% probability of meeting criteria" are the point.
  Interpretability is a feature requirement, not a nice-to-have.
- **Calibration matters more than accuracy.** Portfolio construction ranks by
  predicted probability. A model whose 0.7 means 70% is more useful than a
  slightly more accurate model whose probabilities are meaningless. Single
  trees are poorly calibrated; this is a known Phase-1 limitation, addressed
  in Phase 3.
- **Relative labels are expected to work better than absolute ones.** Absolute
  thresholds force implicit market-level prediction. Train both; compare; be
  unsurprised if absolute-threshold models underperform out-of-time.
- **Weighted everything.** Quarterly snapshots with multi-year horizons make
  rows heavily overlapping (5y serial label correlation at lag 4 quarters is
  ~0.82). The upstream `sample_weight_{H}y` uniqueness weights are passed as
  native sample weights in training, and effective sample size
  (Σ weights, from `manifest.json["effective_rows"]`) is what gets reported —
  never raw row counts.
- **Missingness is information.** NULLs are meaningful (no filing yet,
  history burn-in, structurally unclassified balance sheets, rank guards).
  Prefer models with native missing-value handling; any imputation is fitted
  inside the training fold only and disclosed in the report.

## 3. The data contract (summary)

Full contract: [data/manual.md](data/manual.md). The load-bearing points:

- **Row grain** is `(permaticker, snapshot_date, snapshot_kind)` — three
  snapshots per stock-quarter at the quarter's low/median/high adjusted-close
  touch dates. `permaticker` is the entity key; `ticker` is display-only.
- **Training uses all three kinds** (an entry-price gradient);
  **evaluation uses median-kind rows only** — a real portfolio enters at one
  price. The split tags already enforce this for test rows.
- **Roles**: train only on `role = 'train'`. `purged`/`embargoed` rows exist
  to make the boundary cost measurable, not to be used.
- **Schemes**: `walkforward` (expanding-window, one fold per test year) is
  where all model selection happens. `holdout` (final ~3 years) is sealed —
  evaluated once per phase, after selection is frozen. `entity_holdout` and
  `random_kfold` are diagnostic-only (§7); `random_kfold` is deliberately
  leaky.
- **Delisted rows are labeled rows like any other** (final price carried at
  0% to the horizon). Filtering them out reintroduces survivorship bias and
  is the single worst thing you can do with this dataset.
- **Columns are selected via `manifest.json["columns"]`**, never by
  pattern-matching names.
- **No liquidity floor exists upstream** — deliberately. Investability is a
  downstream modeling decision, built from `log_marketcap`,
  `dollar_volume_3m`, and `amihud_12m`, and reported as part of the model
  definition.

## 4. Phase roadmap

### Phase 1 — Harness + baseline trees
- Experiment harness: load a pinned dataset directory, apply split tags,
  train, evaluate, log everything (params, dataset version, git SHA, seed,
  metrics) — MLflow or a plain results table.
- Baselines to beat, computed first: predict-majority-class; rank by a single
  factor (`book_to_market_rank`, `earnings_yield_rank`); random.
- Single decision trees (sklearn), depth-limited, trained with
  `sample_weight_{H}y`, class-weighted where needed. Deliverable per model:
  the tree diagram + extracted human-readable rules, checked into `reports/`.

### Phase 2 — Evaluation done right
- Metrics: precision/recall at top-K (portfolio-relevant), PR-AUC (base rates
  vary hugely by horizon/threshold/era — ROC-AUC misleads), calibration
  curves, Brier score.
- **Era-sliced evaluation:** every metric reported per year/regime, not just
  pooled. A model that only works 2009–2020 is a bull-market artifact.
- **Crash-era evaluation is first-class:** the project's core thesis
  (crash-resistant high-precision picks) is only testable in drawdown eras,
  of which the sample contains ~4 (2000–02, 2008–09, 2020, 2022), each
  mechanically different. Report metrics on these eras separately, with
  honest uncertainty — and expect wide error bars, since precision@K on few,
  correlated picks carries the statistical weight of far fewer than K
  independent bets. Relative (beat-benchmark) labels are the primary lens
  here; absolute labels can't see "lost 5% when the market lost 15%."
- Walk-forward evaluation across the upstream `walkforward` folds: retrain on
  each expanding window, test on the next year, purge/embargo already applied
  by the tags. This is the honest estimate of live performance.
- Run the registered diagnostics (§7) to quantify what the purging discipline
  is buying.

### Phase 3 — Better models, kept interpretable
- Gradient-boosted trees (LightGBM) + post-hoc calibration (isotonic / Platt
  on a purged validation fold).
- SHAP values for global and per-prediction explanation; compare discovered
  structure against the single-tree rules from Phase 1.
- Feature ablations: raw vs. rank vs. sector-rank feature sets, with/without
  technicals, with/without classification columns (mind their current-state
  caveat — see [data/features.md](data/features.md)).

### Phase 4 — Portfolio construction & backtest
- Turn top-K probability rankings into quarterly-rebalanced portfolios.
- Backtest with transaction-cost assumptions and an explicit investability
  filter built from the liquidity columns (`log_marketcap`,
  `dollar_volume_3m`, `amihud_12m`); the filter is part of the reported model
  definition.
- Compare against SPY and an equal-weight universe benchmark; report
  drawdowns and era-sliced results, not just CAGR.
- Explicitly test the "defensive" hypothesis from the project's motivation:
  in market-down years, do selected stocks lose less?

## 5. Anti-overfitting rules

- The sealed `holdout` fold is touched once, at the end of a phase — never
  during model selection. A consumed holdout cannot be re-sealed.
- Every experiment is logged; failed experiments count. If 40 configurations
  were tried, the reported result accounts for that (deflated expectations,
  not the max). `split_folds.parquet` is cited in every report so
  trial-count / PBO accounting can't be undermined by quietly redefining
  folds.
- No feature engineering in this repo. If a model "needs" a new feature,
  that's an upstream change and a new dataset version.
- The model that ships is refit on all currently-eligible data — the
  purge/embargo/holdout discipline constrains *measurement*, not what the
  deployed model may learn from.

## 6. Repo layout (planned)

```
value-ml-models/
├── data/             # dataset docs (committed); datasets/ (git-ignored)
├── experiments/      # one config file per experiment, results logged
├── src/
│   ├── harness/      # dataset loading, split application, run logging
│   ├── models/       # tree, gbm, calibration wrappers
│   ├── eval/         # metrics, era-slicing, walk-forward
│   ├── explain/      # rule extraction, SHAP
│   └── portfolio/    # ranking → holdings, backtest
├── reports/          # generated evaluation reports per experiment
└── tests/
```

## 7. Registered experiments (deferred here from upstream)

These diagnostics were deliberately deferred to this repo by the dataset
design (see [data/manual.md](data/manual.md) §7). They are **diagnostic
only** — never model selection, never reported performance:

- **Leakage-gap experiment** (upstream decision 0010): train identical models
  under `random_kfold`, `entity_holdout`, and purged `walkforward` tags; the
  score gaps measure overlap leakage and firm-identity memorization.
- **Era-identifiability probe**: predict the calendar year from features
  alone (raw vs. rank sets); beating chance settles "you can't tell what date
  a sample comes from" negatively.
- **Restated-variant ablation** (upstream decision 0009): as-reported
  features are canonical; a restated-dimension variant may be trained as a
  diagnostic under the same purged splits, never shipped.

## 8. Open questions

- [ ] One model per (horizon, threshold) vs. predicting continuous CAGR and
      thresholding afterward (regression reframe). Start with classification
      as planned; revisit after Phase 2. If regressing 1y outcomes, note the
      upstream caveat: 1y label variance is dominated by a few extreme
      returns — winsorize or stay binary.
- [ ] Class-imbalance handling per cell (some cells are ~90/10). Any
      resampling must respect era boundaries (no synthetic samples mixing
      eras) and interact sanely with the uniqueness weights.
- [ ] Retraining cadence within walk-forward folds (annual is what the fold
      calendar gives; is quarterly refresh inside a fold worth it?).
- [ ] Transaction-cost model fidelity for microcaps (the universe is
      microcap-dominated with no upstream liquidity floor).
- [ ] How to treat pre-2000 training rows: 1997–99 have depressed filing
      coverage and history-gated features are NULL during burn-in; the
      upstream earliest-trustworthy-year verification is still open.
