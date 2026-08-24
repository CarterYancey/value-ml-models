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
- **Precision over recall, deliberately.** The strategy is a small number of
  extremely high-conviction picks: a model that finds 10 stocks at 90%
  precision beats one that finds 200 at 60%, even though the latter has far
  better recall and accuracy. This is tunable, not aspirational: every
  classifier exposes a numeric `class_weight` (positives weighted `w` vs. 1;
  `w < 1` makes false positives expensive, so only very pure regions are
  called positive), and `precision_targets` in any config reports the best
  recall achievable subject to a precision floor (`recall_at_prec_*`), with
  the score threshold and pick count that achieve it — per fold, per era,
  and pooled. Model selection ranks on recall-at-precision-floor rather
  than accuracy. The era slices keep this honest: a 90%-precision rule that
  only picks in bull years is still a bull-market artifact.
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
- Gradient-boosted trees (LightGBM) and random forests, under the same
  harness protocol as the Phase-1 tree (mandatory uniqueness weights,
  native NULL routing, no imputation). **No early stopping** in the
  boosted models: early stopping needs a held-out set, and carving one
  out locally would construct a split (invariant 1) — boosting rounds are
  an ordinary hyperparameter tuned across the upstream walk-forward folds.
- Post-hoc calibration (isotonic / Platt on a purged validation fold).
- SHAP values for global and per-prediction explanation; compare discovered
  structure against the single-tree rules from Phase 1.
- Feature ablations: raw vs. rank vs. sector-rank feature sets, with/without
  technicals, with/without classification columns (mind their current-state
  caveat — see [data/features.md](data/features.md)).
- **Sweep harness for systematic search**: one TOML declares ranges —
  several label cells (horizon + label pairs), a model-parameter grid,
  alternative feature sets, several seeds — and expands into ordinary
  experiment configs, all run through the standard runner (`vml-sweep`).
  Per-run reports land under `reports/sweeps/<name>/` with a summary
  ranked by pooled `rank_metric` (default: recall at the first precision
  floor). Sweeps change how many configs get tried, not how any one of
  them is measured — see §5 for the accounting.

### Phase 3.5 — Downturn specialization (crash-resistant picks)

The project's core thesis — high-precision picks that survive drawdowns —
has so far been evaluated (crash-era slices) but not *targeted*: models
are trained on all eras and merely inspected on the bad ones. This phase
makes crash performance a first-class training and selection objective,
within the invariants (no local splits, no feature engineering):

- **Regime-emphasis training weights.** Multiply the mandatory
  `sample_weight_{H}y` by a disclosed era-emphasis factor that up-weights
  training rows whose *label windows* overlap drawdown eras. This is a
  training-time weighting, not a split or a filter — every row stays in,
  purge/embargo tags untouched — and the emphasis schedule is part of the
  config (hashed, reported). Risk to check: up-weighting a handful of
  eras shrinks effective sample size; report Σ(effective weights) under
  the emphasis so the shrinkage is visible.
- **Crash-aware model selection.** Rank sweep candidates by crash-era
  metrics (precision/recall-at-precision restricted to the drawdown test
  years) instead of pooled numbers — a `rank_metric` over the crash-era
  table. Wide Wilson intervals are expected; selection across ~4 eras is
  weak evidence and gets reported as such.
- **Relative labels as the primary lens** (`beat_spy`): absolute-threshold
  labels can't see "lost 5% when the market lost 15%" (already stated in
  Phase 2; here it becomes the default for the specialist models).
- **Two-stage survival gating.** Stage 1: a "survival" model predicting
  the *absence* of catastrophe over the horizon; stage 2: the return
  model ranks only the survivors. Needs upstream labels to do properly —
  e.g. `label_{H}_max_drawdown_le_{X}` or a delisting/large-loss outcome
  label — file the request upstream (never derived here). Until then an
  approximation is `{H}y_cagr_ge_0` as the stage-1 target.
- **Regime-conditional evaluation, not regime prediction.** Predicting
  crashes themselves (market timing) is out of scope; the models must be
  *robust to* crashes, not forecast them. If a market-state feature ever
  seems necessary (drawdown-from-high, index-level volatility), it is an
  upstream feature request with its own point-in-time discipline.

### Phase 4 — Portfolio construction & backtest
- Turn top-K probability rankings into periodically-rebalanced portfolios.
- Backtest with transaction-cost assumptions and an explicit investability
  filter built from the liquidity columns (`log_marketcap`,
  `dollar_volume_3m`, `amihud_12m`); the filter is part of the reported model
  definition.
- Compare against SPY and an equal-weight universe benchmark; report
  drawdowns and era-sliced results, not just CAGR.
- Explicitly test the "defensive" hypothesis from the project's motivation:
  in market-down years, do selected stocks lose less?

**Backtest architecture** (implemented in `src/portfolio/`, CLI
`vml-backtest`, configs in `experiments/portfolios/`). The design turns
on four decisions:

1. **Models: walk-forward fold bundles, never deployment bundles.** A
   deployment model is refit on all labeled history, so its scores have
   seen any backtest period. A trade date in year Y is scored by each
   bundle's fold-Y model (trained purged/embargoed on years before Y) —
   the "retrain at each year-end" cadence *is* the upstream fold
   calendar. Corollary: buy decisions are structurally confined to fold
   years — the sealed holdout years have no fold model and can never
   host a decision (valuation of held positions may run past the last
   fold year; the report flags that tuning on this tail erodes the
   holdout).
2. **Cross-sections: from `dataset.parquet`, never from historical
   inference directories.** Inference builds are survivor-only by
   construction (data/manual.md §9); the training dataset keeps every
   later-delisted stock. The monthly point-in-time cross-section is each
   stock's latest *completed-quarter* median-kind snapshot (the quarter's
   median touch date is unknowable mid-quarter), staleness-capped, and
   carries only key/feature/rank columns — labels are structurally out of
   filters' and scorers' reach. Disclosed approximation vs. live
   inference: features up to a quarter-plus stale, ranks relative to the
   snapshot's own quarter.
3. **Prices: a separate versioned artifact, extracted from the labels'
   own price source.** `data/datasets/prices_vX.Y/` (contract in
   `src/portfolio/prices.py`) carries daily total-return-adjusted closes
   per permaticker through each stock's final print, plus the benchmark
   series that defines the trading calendar.
   `scripts/build_price_panel.py` extracts it from the upstream raw
   tables (`SEP.closeadj` for stocks, `SFP` for SPY, `TICKERS` for the
   ticker→permaticker resolution) restricted to a pinned dataset's
   universe. This is the one sanctioned raw-table read in the repo, and
   it is narrow by construction: forward price paths are the *outcome* a
   backtest measures — the same role `closeadj` plays in the upstream
   label build — never features (the raw-join ban protects the feature
   side, and cross-sections/filters structurally cannot see the panel).
   Delistings follow the upstream label convention: a position whose
   series goes silent is liquidated at its final print.
4. **The benchmark leg runs through the same engine** — same deposit
   dates, same execution/cost mechanics, same valuation calendar — so
   strategy-vs-benchmark differences are strategy, not accounting.

The pieces compose config-first (one TOML per strategy, hashed and
logged under scheme `backtest` — backtest configurations count as trials):
declared score combination (`product`/`mean`/`min`/`mean_rank`) with an
optional per-model floor; declared column filters plus a *mandatory*
investability statement (filters or an explicit, report-flagged
`"none"`); mandatory `cost_bps`; and a `Strategy` interface (candidates +
cash + positions → orders) so richer portfolio management (rebalancing,
sells, position caps) plugs in without touching the engine. Reports lead
with money-weighted (XIRR) and time-weighted results, drawdowns, the
per-year era slice with crash tagging, the defensive-hypothesis check,
the candidate funnel, and full provenance.

## 5. Anti-overfitting rules

- The sealed `holdout` fold is touched once, at the end of a phase — never
  during model selection. A consumed holdout cannot be re-sealed.
- Every experiment is logged; failed experiments count. If 40 configurations
  were tried, the reported result accounts for that (deflated expectations,
  not the max). `split_folds.parquet` is cited in every report so
  trial-count / PBO accounting can't be undermined by quietly redefining
  folds.
- Sweeps industrialize trying configurations, so they get extra friction:
  every expanded run (including failures) is logged individually to the
  results store; the sweep summary restates each cell's all-time
  configurations-tried count; expansion is capped by `max_runs` (default
  200) so blowing past it requires editing the sweep file; and the summary
  itself states that its ranking is selection-biased — sweep winners are
  candidates for the sealed holdout, never reportable results.
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
- [ ] **Other classifier families (KNN, SVM, logistic).** Worth a
      registered comparison, with eyes open about the fit: none of them
      handle NULLs natively (imputation must be fold-internal and
      disclosed — a real friction given "missingness is information"),
      distance/margin methods need feature scaling (the rank features are
      already uniform — use those), and KNN/SVM scale poorly to ~300k-row
      folds (subsampling interacts with the uniqueness weights). A
      weighted, calibrated logistic regression on the rank set is the
      cheapest and most interpretable candidate and doubles as another
      baseline; KNN/SVM are curiosity experiments unless they beat the
      trees on the precision-floor metrics.
- [ ] **Regression reframe & deep learning (Phase 5 candidates).**
      Regression on `fwd_{H}_cagr` / `fwd_{H}_excess_cagr` (columns
      already exist) then thresholding: gives one model per horizon
      instead of per cell, calibrated quantiles could drive the
      precision floor directly; 1y variance is dominated by extreme
      returns (winsorize or model quantiles, per the upstream caveat).
      Deep learning only where tabular DL has a real edge: sequence
      models over a stock's quarterly snapshot history
      (TCN/transformer) rather than MLPs on flat rows — that needs an
      upstream sequence-shaped dataset variant (per-quarter history
      aligned point-in-time), plus embedding-based handling of
      categoricals. Both keep the same harness discipline: upstream
      splits, uniqueness weights, era-sliced reporting; interpretability
      requirement means SHAP/attention inspection is mandatory, not
      optional.
