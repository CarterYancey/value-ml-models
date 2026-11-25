# PLAN — architecture & design

This document holds the theory and architecture of `value-ml-models`.
Concrete tasks live in [TODO.md](TODO.md). The dataset contract lives
in [data/manual.md](data/manual.md).

## 1. Objective

The project trains classification models that predict, from
point-in-time fundamentals, whether a stock will meet return criteria
over multi-year horizons. It turns calibrated predictions into ranked
stock lists and portfolios.

The upstream label matrix defines the prediction cells. The horizons
are **H ∈ {1y, 2y, 3y, 5y}**. The absolute labels are
`label_{H}_cagr_ge_{0,5,8,10}`, with inclusive thresholds. The
relative label is `label_{H}_beat_spy`. One model is trained per
cell, where a cell is a horizon and a threshold. All cells share one
training and evaluation harness. Continuous variants `fwd_{H}_cagr` and
`fwd_{H}_excess_cagr` are available if the regression reframe (§8) is
ever pursued.

## 2. Design principles

- **The dataset is pinned and immutable.** Every experiment records the
  exact `dataset_vX.Y` it ran against. Upstream fixes data bugs, which
  produces a new version. Results across different dataset
  versions are never compared.
- **Splits come from upstream.** `splits.parquet` tags every row with a
  role for each scheme, fold and horizon. This repo *applies* tags and never
  constructs splits. Purge and embargo are already priced into the
  tags.
- **Explainability comes first.** The v1 models are single decision
  trees, because rules such as "P/B rank < X gives Y% probability of
  meeting the criteria" are the point. Interpretability is a feature
  requirement, not a nice-to-have.
- **Calibration matters more than accuracy.** Portfolio construction
  ranks by predicted probability. A model whose 0.7 means 70% is more
  useful than a slightly more accurate model whose probabilities are
  meaningless. Single trees are poorly calibrated. This is a known
  Phase-1 limitation, and Phase 3 addresses it.
- **Precision is preferred over recall, deliberately.** The strategy is
  a small number of extremely high-conviction picks. Compare two
  models:

  | model | picks | precision |
  |---|---|---|
  | preferred | 10 | 90% |
  | rejected | 200 | 60% |

  The preferred model beats the rejected one, even though the rejected
  one has far better recall and accuracy. This preference is tunable rather
  than aspirational. Every classifier exposes a
  numeric `class_weight`, which weights positives `w` against 1. A
  `w < 1` makes false positives expensive, so only very pure regions
  are called positive. The `precision_targets` table in any config
  reports the best recall achievable subject to a precision floor
  (`recall_at_prec_*`). It also reports the score threshold and pick
  count that achieve it, per fold, per era and pooled. Model
  selection ranks on recall at a precision floor rather than on
  accuracy. The era slices keep this honest. A 90%-precision rule that
  only picks in bull years is still a bull-market artifact.
- **Relative labels are expected to work better than absolute ones.**
  Absolute thresholds force an implicit market-level prediction. Train
  both and compare them. Be unsurprised if absolute-threshold models
  underperform out of time.
- **Everything is weighted.** Quarterly snapshots with multi-year
  horizons make rows heavily overlapping. The 5y serial label
  correlation at a lag of 4 quarters is about 0.82. The upstream
  `sample_weight_{H}y` uniqueness weights are passed as native sample
  weights in training. The effective sample size, which is the sum of
  the weights from `manifest.json["effective_rows"]`, is what gets
  reported. Raw row counts are never reported.
- **Missingness is information.** NULLs are meaningful. They mark no
  filing yet, history burn-in, structurally unclassified balance sheets
  and rank guards. Prefer models with native missing-value handling.
  Any imputation is fitted inside the training fold only and is
  disclosed in the report.

## 3. The data contract (summary)

The full contract is [data/manual.md](data/manual.md). These are the
load-bearing points:

- **The row grain** is `(permaticker, snapshot_date, snapshot_kind)`.
  There are three snapshots per stock-quarter, at the quarter's low,
  median and high adjusted-close touch dates. `permaticker` is the
  entity key, and `ticker` is display-only.
- **Training uses all three kinds**, which gives an entry-price
  gradient. **Evaluation uses median-kind rows only**, because a real
  portfolio enters at one price. The split tags already enforce this
  for test rows.
- **Roles**: train only on `role = 'train'`. The `purged` and
  `embargoed` rows exist to make the boundary cost measurable, not to
  be used.
- **Schemes**: `walkforward` is an expanding window with one fold per
  test year, and all model selection happens there. `holdout` covers
  the final three years or so and is sealed. It is looked at once per
  cell, after selection on that cell is frozen. A cell is a label, a
  horizon and a holdout window. Any further look is disclosed. `entity_holdout` and
  `random_kfold` are diagnostic-only (§7). `random_kfold` is
  deliberately leaky.
- **Delisted rows are labeled rows like any other.** Their final price
  is carried at 0% to the horizon. Filtering them out reintroduces
  survivorship bias and is the single worst thing you can do with this
  dataset.
- **Columns are selected via `manifest.json["columns"]`**, never by
  pattern-matching names.
- **No liquidity floor exists upstream**, and that is deliberate.
  Investability is a downstream modeling decision. It is built from
  `log_marketcap`, `dollar_volume_3m` and `amihud_12m`, and it is
  reported as part of the model definition.

## 4. Phase roadmap

### Phase 1 — Harness + baseline trees

- The experiment harness loads a pinned dataset directory, applies the
  split tags, trains and evaluates. It logs the params, dataset
  version, git SHA, seed and metrics, to MLflow or to a plain results
  table.
- The baselines to beat are computed first: predict the majority
  class, rank by a single factor such as `book_to_market_rank` or
  `earnings_yield_rank`, and random.
- Single decision trees from sklearn are depth-limited, trained with
  `sample_weight_{H}y`, and class-weighted where needed. The
  deliverable per model is the tree diagram plus extracted
  human-readable rules, checked into `reports/`.

### Phase 2 — Evaluation done right

- The metrics are precision and recall at top-K, which are
  portfolio-relevant, PR-AUC, calibration curves and the Brier score.
  Base rates vary hugely by horizon, threshold and era, so ROC-AUC
  misleads.
- **Every metric is era-sliced.** The report gives it per year or
  regime, not just pooled. A model that only works 2009–2020 is a
  bull-market artifact.
- **Crash-era evaluation is first-class.** The project's core thesis
  is crash-resistant high-precision picks, and it is only testable in
  drawdown eras. The sample contains about four of them, and each is
  mechanically different:

  | drawdown era |
  |---|
  | 2000–02 |
  | 2008–09 |
  | 2020 |
  | 2022 |

  Report metrics on these eras separately, with honest uncertainty.
  Expect wide error bars, since precision@K on few, correlated picks
  carries the statistical weight of far fewer than K independent bets.
  Relative (beat-benchmark) labels are the primary lens here. Absolute
  labels cannot see "lost 5% when the market lost 15%."
- Walk-forward evaluation runs across the upstream `walkforward`
  folds. Each fold retrains on an expanding window and tests on the
  next year, with purge and embargo already applied by the tags. This
  is the honest estimate of live performance.
- Run the registered diagnostics (§7) to quantify what the purging
  discipline is buying.

### Phase 3 — Better models, kept interpretable

- Gradient-boosted trees (LightGBM) and random forests run under the
  same harness protocol as the Phase-1 tree. That protocol means
  mandatory uniqueness weights, native NULL routing and no imputation.
  **No early stopping** is used in the boosted models. Early stopping
  needs a held-out set, and carving one out locally would construct a
  split (invariant 1). Boosting rounds are an ordinary hyperparameter
  tuned across the upstream walk-forward folds.
- Post-hoc calibration is isotonic or Platt, fitted on a purged
  validation fold.
- SHAP values give global and per-prediction explanation. Compare the
  discovered structure against the single-tree rules from Phase 1.
- **Historical analogues via leaf co-membership**: one stock is scored
  by several deployment models, say the best 1y, 3y and 5y. For each
  model, retrieve the labeled historical rows that it routes to the
  *same leaves* as the stock, and show their realized outcomes,
  delistings included. With a single tree this reads as a rule plus its
  members. The rule is "stocks with P/B rank < X and …", and the
  members are those stocks and how they did. With forests and boosted trees it becomes a proximity,
  the share of trees where a row shares the stock's leaf. Similarity is
  defined by the model's own splits and NULL routing. So there is no
  distance metric or imputation to invent, and it works before SHAP
  exists. Feature-space nearest neighbors on rank columns are the
  fallback for leafless models. This explains a ranking and does not
  measure the model. The fit chose those leaves from those rows, so
  their outcome rate is in-sample. The tasks are under Deployment in
  TODO.md.
- Feature ablations compare raw, rank and sector-rank feature sets,
  with and without technicals, and with and without classification
  columns. Mind the current-state caveat of the classification columns
  in [data/features.md](data/features.md).
- **Sweep harness for systematic search**: one TOML declares ranges and
  expands into ordinary experiment configs, all run through the
  standard runner (`vml-sweep`). The ranges cover several label cells,
  each a horizon and label pair, a model-parameter grid, alternative
  feature sets and several seeds. Per-run reports land under
  `reports/sweeps/<name>/` with a summary ranked by pooled
  `rank_metric`, whose default is recall at the first precision floor.
  Sweeps change how many configs get tried, not how any one of them is
  measured. See §5 for the accounting.
- **Random search over the continuous surfaces**: a `[random]` table of
  distributions takes `n_samples` joint draws, deterministic given
  `search_seed`. The distributions are log-uniform for scale
  parameters, integer ranges, and choices. Grids stay for coarse axes
  such as class weight and feature sets. Random search covers learning
  rate and regularization at full resolution under the same run budget,
  `max_runs`, and trial-ledger accounting.

### Phase 3.5 — Downturn specialization (crash-resistant picks)

The project's core thesis is high-precision picks that survive
drawdowns. So far it has been evaluated on crash-era slices but not
*targeted*. The models are trained on all eras and merely inspected on
the bad ones. This phase makes crash performance a first-class training
and selection objective, within the invariants of no local splits and
no feature engineering:

- **Regime-emphasis training weights.** Multiply the mandatory
  `sample_weight_{H}y` by a disclosed era-emphasis factor that
  up-weights training rows whose *label windows* overlap drawdown eras.
  This is a training-time weighting, not a split or a filter. Every row
  stays in, and the purge and embargo tags are untouched. The emphasis
  schedule is part of the config, so it is hashed and reported. One
  risk must be checked: up-weighting a handful of eras shrinks the
  effective sample size. Report the sum of the effective weights under
  the emphasis so the shrinkage is visible.
- **Crash-aware model selection.** Rank sweep candidates by crash-era
  metrics instead of pooled numbers. The crash-era metrics are
  precision and recall-at-precision restricted to the drawdown test
  years, as a `rank_metric` over the crash-era table. Wide Wilson
  intervals are expected. Selection across about four eras is weak
  evidence and gets reported as such.
- **Relative labels are the primary lens** (`beat_spy`).
  Absolute-threshold labels cannot see "lost 5% when the market lost
  15%". Phase 2 already states this. Here it becomes the default for
  the specialist models.
- **Two-stage survival gating.** Stage 1 is a "survival" model that
  predicts the *absence* of catastrophe over the horizon. Stage 2 is
  the return model, which ranks only the survivors. Upstream now ships
  the continuous path outcomes `fwd_{H}_max_drawdown` and
  `fwd_{H}_max_drawdown_from_entry` (decision 0017). The stage-1 target
  is a derived label that thresholds them, for example
  `fwd_3y_max_drawdown_from_entry < 0.3`. That is a re-threshold of a
  stored outcome, not a new computation from prices.
- **Regime-conditional evaluation, not regime prediction.** Predicting
  crashes themselves, which is market timing, is out of scope. The
  models must be *robust to* crashes, not forecast them. A market-state
  feature such as drawdown from high or index-level volatility may one
  day seem necessary. If so, it is an upstream feature request with its
  own point-in-time discipline.

### Phase 4 — Portfolio construction & backtest

- Turn top-K probability rankings into periodically rebalanced
  portfolios.
- The backtest uses transaction-cost assumptions and an explicit
  investability filter built from the liquidity columns
  `log_marketcap`, `dollar_volume_3m` and `amihud_12m`. The filter is
  part of the reported model definition.
- The comparison is against SPY and an equal-weight universe benchmark.
  It reports drawdowns and era-sliced results as well as CAGR.
- Explicitly test the "defensive" hypothesis from the project's
  motivation: in market-down years, do the selected stocks lose less?

**The backtest architecture** is implemented in `src/portfolio/`, with
the CLI `vml-backtest` and configs in `experiments/portfolios/`. The
design turns on four decisions:

1. **Models are walk-forward fold bundles, never static deployment
   bundles.** A deployment model is refit on all labeled history, so
   its scores have seen any backtest period. A trade date in year Y is
   scored by each bundle's fold-Y model, which was trained purged and
   embargoed on the years before Y. The "retrain at each year-end"
   cadence *is* the upstream fold calendar. The fold calendar stops
   where test labels stop being observable, but a live portfolio keeps
   trading. So the years past a bundle's last fold are served by the
   config's `model_update` policy. The default, `"refit"`, is a
   *simulated year-end deployment refit*. The bundle's config is refit
   on every row whose label window was fully observable by Jan 1 of the
   trade year. That is data/manual.md §4 rule 7 applied point-in-time.
   No split tags are read, no rows are held out for evaluation, and
   the scores are never label-evaluated. The alternative, `"frozen"`, keeps the last
   fold's model. Those later trade years, and all valuation past the
   last fold, overlap the sealed holdout era. The report marks the
   segment selection-toxic. Simulating there is what a live run
   requires, but feeding it back into model or strategy selection
   erodes the holdout.
2. **Cross-sections come from `dataset.parquet`, never from historical
   inference directories.** Inference builds are survivor-only by
   construction, as data/manual.md §9 explains. The training dataset keeps every
   later-delisted stock. The monthly point-in-time cross-section is each
   stock's latest *completed-quarter* median-kind snapshot, because the
   quarter's median touch date is unknowable mid-quarter. It is
   staleness-capped and carries only key, feature and rank columns.
   Labels are structurally out of the reach of filters and scorers.
   The disclosed approximation against live inference is that features
   are up to a quarter-plus stale, and ranks are relative to the
   snapshot's own quarter.
3. **Prices are a separate versioned artifact, extracted from the
   labels' own price source.** `data/datasets/prices_vX.Y/` carries
   daily total-return-adjusted closes per permaticker through each
   stock's final print. Its contract is in `src/portfolio/prices.py`.
   It also carries the benchmark series that defines the trading
   calendar. `scripts/build_price_panel.py` extracts it from the
   upstream raw tables, restricted to a pinned dataset's universe. It
   reads `SEP.closeadj` for stocks, `SFP` for SPY, and `TICKERS` for
   the ticker-to-permaticker resolution. This is the one sanctioned
   raw-table read in the repo, and it is narrow by construction.
   Forward price paths are the *outcome* a backtest measures, the same
   role `closeadj` plays in the upstream label build. They are never
   features. The raw-join ban protects the feature side, and
   cross-sections and filters structurally cannot see the panel.
   Delistings follow the upstream label convention: a position whose
   series goes silent is liquidated at its final print.
4. **The benchmark leg runs through the same engine**, with the same
   deposit dates, the same execution and cost mechanics, and the same
   valuation calendar. So any difference between the strategy and the
   benchmark comes from the strategy itself and never from the
   accounting.

The pieces compose config-first. One TOML per strategy is hashed and
logged under scheme `backtest`, and backtest configurations count as
trials. A config declares these parts:

- a score combination, one of `product`, `mean`, `min` or `mean_rank`,
  with an optional per-model floor.
- column filters plus a *mandatory* investability statement, either
  filters or an explicit, report-flagged `"none"`.
- a mandatory `cost_bps`.
- a `Strategy` interface, which maps candidates, cash and positions to
  orders. Richer portfolio management such as rebalancing, sells and
  position caps then plugs in without touching the engine.

Reports lead with money-weighted (XIRR) and time-weighted results,
drawdowns, the per-year era slice with crash tagging, the
defensive-hypothesis check, the candidate funnel, and full provenance.

## 5. Anti-overfitting rules

- The sealed `holdout` fold answers one question walk-forward cannot:
  what does the model score on rows nobody *selected on*? It keeps that
  meaning only while it is looked at once per cell. A cell is a label,
  a horizon and a holdout window. The window is the fold's test years
  in `split_folds.parquet`, not the dataset version, so a feature-only
  dataset bump does not re-seal the same rows. Run it when you would
  act on the model, never to choose between candidates. Choosing
  between candidates is walk-forward's job. A consumed cell cannot be
  re-sealed. It can be *re-opened* with a stated reason, and then every
  report in the cell says "holdout look k of N". N looks inflate the
  best number by roughly the top order statistic of N draws. At N = 5
  that is about 1.2 standard errors. Over a 3-year holdout that is on
  the order of 0.1 in precision@20. So the count is part of the
  result.
- The ledger logs every experiment, and failed experiments count. If 40
  configurations were tried, the reported result accounts for that,
  with deflated expectations rather than the max. `split_folds.parquet`
  is cited in every report so that trial-count and PBO accounting
  cannot be undermined by quietly redefining folds.
- Sweeps industrialize trying configurations, so they get extra
  friction. The sweep logs every expanded run, including failures,
  individually to the results store. The sweep summary restates each
  cell's all-time configurations-tried count. Expansion is capped by
  `max_runs`, with a default of 200, so blowing past it requires
  editing the sweep file. The summary itself states that its ranking is
  selection-biased. Sweep winners are candidates for the sealed
  holdout, never reportable results.
- There is no feature engineering in this repo. If a model "needs" a
  new feature, that is an upstream change and a new dataset version.
- The model that ships is refit on all currently eligible data. The
  discipline of purge, embargo and holdout constrains *measurement*,
  not what the deployed model may learn from.

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

The dataset design deliberately deferred these diagnostics to this repo.
See [data/manual.md](data/manual.md) §7. They are **diagnostic only**.
They are never model selection and never reported performance:

- **The leakage-gap experiment** (upstream decision 0010) trains
  identical models under `random_kfold`, `entity_holdout` and purged
  `walkforward` tags. The score gaps measure overlap leakage and
  firm-identity memorization.
- **The era-identifiability probe** predicts the calendar year from
  features alone, on the raw and on the rank sets. Beating chance
  settles "you can't tell what date a sample comes from" negatively.
- **The restated-variant ablation** (upstream decision 0009) treats
  as-reported features as canonical. A restated-dimension variant may
  be trained as a diagnostic under the same purged splits, never
  shipped.

## 8. Open questions

- [ ] Should there be one model per horizon and threshold, or one model
      that predicts continuous CAGR and thresholds afterward? The second
      is the regression reframe.
      Start with classification as planned, and revisit after Phase 2.
      If regressing 1y outcomes, note the upstream caveat: 1y label
      variance is dominated by a few extreme returns, so winsorize or
      stay binary.
- [ ] Class-imbalance handling per cell is open. Some cells are about
      90/10. Any resampling must respect era boundaries, so no synthetic
      samples may mix eras, and it must interact sanely with the
      uniqueness weights.
- [ ] The retraining cadence within walk-forward folds is open. Annual
      is what the fold calendar gives. Is a quarterly refresh inside a
      fold worth it?
- [ ] Transaction-cost model fidelity for microcaps is open. The
      universe is microcap-dominated with no upstream liquidity floor.
- [ ] How to treat pre-2000 training rows is open. The years 1997–99
      have depressed filing coverage, and history-gated features are
      NULL during burn-in. The upstream earliest-trustworthy-year
      verification is still open.
- [ ] **Other classifier families, namely KNN, SVM and logistic
      regression,** are worth a registered comparison, with eyes open
      about the fit. None of them
      handle NULLs natively, so imputation must be fold-internal and
      disclosed, a real friction given "missingness is information".
      Distance and margin methods need feature scaling. The rank
      features are already uniform, so use those. KNN and SVM scale
      poorly to folds of about 300k rows, and subsampling interacts with
      the uniqueness weights. A weighted, calibrated logistic regression
      on the rank set is the cheapest and most interpretable candidate,
      and it doubles as another baseline. KNN and SVM are curiosity
      experiments unless they beat the trees on the precision-floor
      metrics.
- [ ] **The regression reframe and deep learning are Phase 5
      candidates.** Regression on `fwd_{H}_cagr` or `fwd_{H}_excess_cagr`,
      whose columns already exist, followed by thresholding gives one
      model per horizon instead of per cell. Calibrated quantiles could
      drive the precision floor directly. The 1y variance is dominated
      by extreme returns, so winsorize or model quantiles, per the
      upstream caveat. *The mechanism is implemented*: `lightgbm_regressor`
      plus `eval_label` keeps evaluation in the precision@K frame (see
      TODO). The spike run and the classification comparison are what
      remain open. Deep learning belongs only where tabular DL has a
      real edge. That means sequence models over a stock's quarterly
      snapshot history, such as a TCN or a transformer, rather than
      MLPs on flat rows. It needs an upstream sequence-shaped dataset
      variant, with per-quarter history aligned point-in-time, plus
      embedding-based handling of categoricals. Both keep the same
      harness discipline: upstream splits, uniqueness weights and
      era-sliced reporting. The interpretability requirement makes SHAP
      or attention inspection mandatory.
