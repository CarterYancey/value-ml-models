# Experiment report — forest_random_search_3y-2seeds__label_3y_beat_spy__r30__s23

- run id: `3434648edf55`
- dataset version: `1.1` (pinned, immutable)
- config hash: `8179beb03d295321`
- git SHA: `e587a6697b9761cc80a5ed9f6c71a4b906cdf210`
- seed: 23
- model: `random_forest` params `{"bootstrap": true, "class_weight": 1, "criterion": "gini", "max_depth": 3, "max_features": 0.914775, "max_samples": 0.441152, "min_samples_leaf": 248, "n_estimators": 126, "n_jobs": 8}`
- label: `label_3y_beat_spy` — horizon 3y, scheme `walkforward`
- **configurations tried against this cell (dataset, scheme, horizon, label): 410** (from the append-only results store; failed runs count)

## Era-sliced metrics (one row per test year)

Sliced on the calendar year of each test row's `snapshot_date` (one walk-forward fold per year); crash eras are tagged inline. `conf_at_K` is the mean score of the top-K picks; `base_rate_brier` is the no-skill Brier the model must beat. \*The pooled row picks per year — per-fold model scores are not comparable, so a global top-K would just take the hottest-scoring fold's picks; it is context for the era rows, never a stand-alone result. ROC-AUC and recall@K are logged in the results store, not shown here.

| era          | n_test | base_rate | precision_at_20 | conf_at_20 | brier  | base_rate_brier | pr_auc |
| ------------ | ------ | --------- | --------------- | ---------- | ------ | --------------- | ------ |
| 2005         | 18684  | 0.4084    | 0.9500          | 0.8471     | 0.2919 | 0.2416          | 0.4974 |
| 2006         | 18404  | 0.4634    | 0.6500          | 0.8074     | 0.2601 | 0.2487          | 0.5798 |
| 2007         | 18091  | 0.4642    | 0.9500          | 0.7667     | 0.2557 | 0.2487          | 0.5840 |
| 2008 (GFC)   | 17456  | 0.4630    | 0.9500          | 0.7260     | 0.2432 | 0.2486          | 0.5737 |
| 2009 (GFC)   | 16575  | 0.4353    | 0.5500          | 0.6964     | 0.2381 | 0.2458          | 0.5248 |
| 2010         | 16052  | 0.3606    | 0.6500          | 0.6906     | 0.2403 | 0.2306          | 0.4454 |
| 2011         | 15517  | 0.3236    | 0.4500          | 0.6749     | 0.2474 | 0.2189          | 0.3834 |
| 2012         | 15168  | 0.3397    | 0.5500          | 0.6804     | 0.2487 | 0.2243          | 0.4058 |
| 2013         | 15055  | 0.3179    | 0.5000          | 0.6659     | 0.2429 | 0.2168          | 0.4081 |
| 2014         | 15378  | 0.3011    | 0.6000          | 0.6552     | 0.2328 | 0.2104          | 0.4001 |
| 2015         | 15511  | 0.2965    | 0.5500          | 0.6620     | 0.2305 | 0.2086          | 0.3793 |
| 2016         | 15094  | 0.3106    | 0.7500          | 0.6420     | 0.2350 | 0.2141          | 0.3641 |
| 2017         | 14846  | 0.2364    | 0.1500          | 0.6344     | 0.2279 | 0.1805          | 0.2612 |
| 2018         | 14833  | 0.2575    | 0.1000          | 0.6306     | 0.2250 | 0.1912          | 0.2681 |
| 2019         | 14743  | 0.2655    | 0.4000          | 0.6240     | 0.2155 | 0.1950          | 0.3079 |
| 2020 (COVID) | 14944  | 0.3273    | 0.8500          | 0.6130     | 0.2103 | 0.2202          | 0.4459 |
| pooled*      | 256351 | 0.3535    | 0.6000          | 0.6885     | 0.2415 | 0.2285          | 0.4609 |

## High-confidence picks (pooled)

How many high-confidence calls the model made, how confident it was, and how precise they were — no pre-chosen score threshold needed. `top N/yr` rows pick per test year; `score >= p` rows (probabilistic models) count every name at or above that probability, pooled.

| selection    | n_picks | picks_per_year | mean_score | precision | hits  |
| ------------ | ------- | -------------- | ---------- | --------- | ----- |
| top 5/yr     | 80      | 5              | 0.6892     | 0.6000    | 48    |
| top 10/yr    | 160     | 10             | 0.6890     | 0.6000    | 96    |
| top 20/yr    | 320     | 20             | 0.6885     | 0.6000    | 192   |
| top 50/yr    | 800     | 50             | 0.6876     | 0.5675    | 454   |
| score >= 0.9 | 0       | 0              | —          | —         | 0     |
| score >= 0.8 | 3707    | 231.7000       | 0.8209     | 0.5368    | 1990  |
| score >= 0.7 | 22698   | 1418.6000      | 0.7608     | 0.5337    | 12114 |
| score >= 0.6 | 61737   | 3858.6000      | 0.6837     | 0.4951    | 30563 |
| score >= 0.5 | 130573  | 8160.8000      | 0.6113     | 0.4339    | 56662 |

## Calibration

Reliability curve on pooled test predictions (each fold's model is refit on its own expanding window). Downstream ranking trusts these probabilities; single trees are expected to calibrate poorly (known Phase-1 limitation, PLAN §2).

![calibration curve](forest_random_search_3y-2seeds__label_3y_beat_spy__r30__s23_calibration.png)

## Baseline comparison

**No baseline runs recorded for this cell.** Run `scripts/run_baselines.py` first; a result without its baselines is not reportable.

## Interpretability artifacts

- per-fold feature importances: [forest_random_search_3y-2seeds__label_3y_beat_spy__r30__s23_importances.csv](forest_random_search_3y-2seeds__label_3y_beat_spy__r30__s23_importances.csv) — impurity/gain-based, so a triage list for feature subsets (which count as configurations tried), not an explanation; the top of the ranking:

| feature                 | mean_importance |
| ----------------------- | --------------- |
| ocf_yield_rank          | 0.2801          |
| vol_12m                 | 0.2236          |
| ret_6m                  | 0.0740          |
| rnd_to_assets_rank      | 0.0588          |
| cfo_to_assets_rank      | 0.0559          |
| ebitda_to_ev_rank       | 0.0431          |
| dividend_yield_rank     | 0.0414          |
| ret_1m                  | 0.0311          |
| ffo_to_liabilities_rank | 0.0288          |
| conservative_score      | 0.0227          |

## Appendix — provenance & accounting

The material every report must carry (honest-evaluation checklist), kept out of the reading path.

### Fold definition (cited from `split_folds.parquet`)

Frozen fold manifest for the folds evaluated above — boundaries and role counts as built upstream; this report is invalid if the folds are redefined.

| fold | test_start | test_end   | embargo_days | n_train | n_test | n_purged | n_embargoed |
| ---- | ---------- | ---------- | ------------ | ------- | ------ | -------- | ----------- |
| 2005 | 2005-01-01 | 2006-01-01 | 30           | 299982  | 18684  | 174048   | 4434        |
| 2006 | 2006-01-01 | 2007-01-01 | 30           | 361098  | 18404  | 169731   | 3687        |
| 2007 | 2007-01-01 | 2008-01-01 | 30           | 417875  | 18091  | 167697   | 4156        |
| 2008 | 2008-01-01 | 2009-01-01 | 30           | 474239  | 17456  | 165537   | 4225        |
| 2009 | 2009-01-01 | 2010-01-01 | 30           | 530702  | 16575  | 161853   | 3814        |
| 2010 | 2010-01-01 | 2011-01-01 | 30           | 585955  | 16052  | 156366   | 3773        |
| 2011 | 2011-01-01 | 2012-01-01 | 30           | 639990  | 15517  | 150249   | 4011        |
| 2012 | 2012-01-01 | 2013-01-01 | 30           | 693610  | 15168  | 144432   | 2759        |
| 2013 | 2013-01-01 | 2014-01-01 | 30           | 742572  | 15055  | 140211   | 3522        |
| 2014 | 2014-01-01 | 2015-01-01 | 30           | 790688  | 15378  | 137220   | 3562        |
| 2015 | 2015-01-01 | 2016-01-01 | 30           | 837864  | 15511  | 136803   | 2937        |
| 2016 | 2016-01-01 | 2017-01-01 | 30           | 883177  | 15094  | 137832   | 3128        |
| 2017 | 2017-01-01 | 2018-01-01 | 30           | 928008  | 14846  | 137949   | 3462        |
| 2018 | 2018-01-01 | 2019-01-01 | 30           | 973897  | 14833  | 136353   | 3707        |
| 2019 | 2019-01-01 | 2020-01-01 | 30           | 1020662 | 14743  | 134319   | 3475        |
| 2020 | 2020-01-01 | 2021-01-01 | 30           | 1066158 | 14944  | 133266   | 3261        |

### Effective sample size

Σ `sample_weight_{H}y` over the rows actually fitted — the honest sample size under overlapping label windows; raw row counts are shown only for reconciliation.

| fold | train_rows | effective_train_size | test_rows |
| ---- | ---------- | -------------------- | --------- |
| 2005 | 299982     | 12690.9998           | 18684     |
| 2006 | 361098     | 14627.4294           | 18404     |
| 2007 | 417875     | 16397.6923           | 18091     |
| 2008 | 474239     | 18195.5038           | 17456     |
| 2009 | 530702     | 20014.2244           | 16575     |
| 2010 | 585955     | 21805.5178           | 16052     |
| 2011 | 639990     | 23582.5204           | 15517     |
| 2012 | 693610     | 25294.6522           | 15168     |
| 2013 | 742572     | 26821.9914           | 15055     |
| 2014 | 790688     | 28347.4439           | 15378     |
| 2015 | 837864     | 29839.0997           | 15511     |
| 2016 | 883177     | 31271.0955           | 15094     |
| 2017 | 928008     | 32701.4481           | 14846     |
| 2018 | 973897     | 34195.1179           | 14833     |
| 2019 | 1020662    | 35731.1885           | 14743     |
| 2020 | 1066158    | 37197.5720           | 14944     |

Cross-check: `manifest.json["effective_rows"]` for 3y = 47994.0 (whole dataset; every per-fold effective size above must be ≤ this).

### Crash-era metrics (with intervals)

Drawdown eras broken out with uncertainty — the same years are tagged in the era table above. Intervals are Wilson 95% on precision@K treating the K picks as independent; they are not — same-year picks share sectors, factor bets and overlapping windows, so true uncertainty is wider than shown.

| era         | n_test | effective_n | base_rate | pr_auc | roc_auc | brier  | base_rate_brier | precision_at_20 | conf_at_20 | recall_at_20 | precision_at_20_ci95 |
| ----------- | ------ | ----------- | --------- | ------ | ------- | ------ | --------------- | --------------- | ---------- | ------------ | -------------------- |
| GFC 2008-09 | 34031  | 1068.7700   | 0.4497    | 0.5539 | 0.6190  | 0.2407 | 0.2475          | 0.7500          | 0.7112     | 0.0019       | [0.60, 0.86]         |
| COVID 2020  | 14944  | 487.9190    | 0.3273    | 0.4459 | 0.6724  | 0.2103 | 0.2202          | 0.8500          | 0.6130     | 0.0032       | [0.64, 0.95]         |
