# TODO

The backlog of code and tooling still to be built, and the requests
outstanding with the upstream dataset repository. Architecture and
rationale are in [PLAN.md](PLAN.md). This is not the research plan:
what to work on next is in [docs/next-steps.md](docs/next-steps.md),
and the decisions behind it are in [docs/decisions.md](docs/decisions.md).

Remove an item when it is built, and mention it in the logbook entry
of the run that first uses it. Every code change goes on its own
`claude/<topic>` branch with tests. What has already been built is
described in the docs (README.md, docs/experiments.md,
docs/backtesting.md, docs/deployment.md); its history is in git.

The backlog was rebuilt from the old phase-by-phase TODO on 2026-11-27.
The old file, with every completed item and the session-by-session
"Next" sections, is in git history before that date.

## Backtest engine

- [ ] **Cut a backtest's memory use** (decision 77.4). A backtest on
      `dataset_v1.5.1` peaks at 12.4 to 13.8 GB of the sandbox's 14 GB,
      because it loads every feature column of the dataset where the
      bundles' own columns would do. Until this is fixed, a v1.5.1
      backtest runs with nothing else in memory, and no unattended chain
      of them runs.
- [ ] Sell at the label's horizon (sell each buy three years after it
      was bought), as a `Strategy`.
- [ ] Buy quarterly instead of monthly.
- [ ] Gate one model's candidates by another model's rank inside
      `vml-backtest` (a two-stage portfolio). `vml-eval` already has
      `[[gate]]`; the backtest does not.
- [ ] A position cap: stop adding to a holding above a set share of the
      portfolio. Low priority; the candidate's largest holding is 8%.
- [ ] Other strategies behind the `Strategy` interface: a periodic full
      rebalance, stop-loss and trailing-stop sells, partial trimming.
- [ ] Realism, the part of the first audit not yet built (decisions 83.2
      and 84.4, [note](docs/notes/2026-11-27-backtest-realism.md)): a
      cost model that depends on size and era (35 basis points a side
      is high for large caps after 2010 and low for small caps before);
      taxes on dividends and realized gains, which matter only for
      selling rules; a market-impact model for small caps. None blocks
      current work.
- [ ] An equal-weighted benchmark leg: the investable universe, and its
      largest fifth, as a second comparison beside SPY. This could be
      built here from the panel, or requested upstream as a series
      (see "Upstream requests").

## Deployment

- [ ] `vml-predict --holdings <file>`: mark which held stocks the rank
      sell rule would sell this month, so that paper portfolio B's sells
      do not have to be read off the CSV by hand.
- [ ] Deployment-time calibration. A deployment refit has no
      out-of-sample history, so `vml-train-deploy` refuses calibrated
      configs. Design: fit the calibrator on the full walk-forward
      out-of-sample history of the same config and store it in the
      deployment bundle (a format change). Low priority: decision 46
      found calibration across years unreachable with these inputs.

## Harness, ledger and catalog

- [ ] A date filter in `FilterSpec`, so that a region or a universe can
      be a period of time. This finishes the "regime-emphasis training
      weights" idea of PLAN Phase 3.5: `[emphasis]` already does it for a
      region of feature columns.
- [ ] Ledger: a run whose process is killed outright (out of memory,
      `kill -9`) leaves no row, so the trial goes uncounted. Log a row
      when a run starts, once readers of the ledger can ignore it.
- [ ] A config hash that leaves out the sweep name (single configs
      already have `identity_hash`), recorded in the ledger, so that a
      re-run under another sweep name can be matched to the original.
- [ ] `vml-experiments verify`: expand each config under `experiments/`
      and compare its hashes with the ledger's, to report configs that
      no longer match their own runs (known today:
      `lgbm_random_search_3y`, `lgbm_cagr_quantile_3y`,
      `forest_random_search_3y`).
- [ ] `vml-experiments columns <run> <run>`: list the differences
      between the resolved feature columns of two runs, from their
      `*_config.json` records.
- [ ] `scripts/run_baselines.py --label "<expression>"`, so that a cell
      with a derived label gets its baselines without hand-written
      sweeps.
- [ ] The random-ranking baseline over several seeds in the standard
      grid. One seed scored p@20 0.39 on the 3-year beat-SPY cell
      against a base rate of 0.35, and the catalog measures lift
      against it.
- [ ] `vml-experiments sweeps` puts rows ranked on different metrics
      (p@10, p@20, p@50) in one table. Rank within one metric, or group
      by it.
- [ ] `vml-experiments list` reports eval configs (`experiments/eval_*.toml`)
      and `experiments/queue.toml` as broken experiment configs. Treat
      them as their own kinds.
- [ ] `vml-experiments`: a `--cell` filter (horizon and label), and a
      `similar <config>` subcommand that ranks configs by shared cell,
      model and features.
- [ ] Fill in the `note` of the tracked sample configs, so that the
      catalog's note column says what each one taught.
- [ ] `experiments/sweeps/lgbm_candidate_sets_3y.toml` is pinned to
      `dataset_v1.0` and never ran. Re-pin it or drop it.
- [ ] Run `scripts/sync_data_docs.py --check` in the test session, or in
      a pre-commit hook, on machines that have the upstream checkout.

## Evaluation and diagnostics

- [ ] The leakage-gap experiment (a registered diagnostic, data/manual.md
      §7): the same model under `random_kfold`, `entity_holdout` and
      walk-forward, with the gaps between their scores reported. Run it
      on v1.2 or later. Two add-ons once it exists: global top-K against
      per-year top-K under `entity_holdout` (if pooled picks win, the
      model is timing eras, not choosing stocks), and the share of an
      entity-holdout model's score variance explained by the year.
- [ ] The boundary check on the zero-inflated rank columns of v1.2
      (upstream brief §8, second query): does the first non-zero rank
      still equal the cell's share of zeros? Record the answer in the
      brief's §10.
- [ ] The restated-variant ablation. It needs a restated dataset variant
      from upstream (upstream decision 0009); coordinate before
      starting.
- [ ] A crash-window line in the per-year table for path labels: entry
      years whose window holds a market crash (2005 to 2008 and 2019 at
      three years) are where the compounder models fall to the base
      rate.
- [ ] A crash-aware `rank_metric` for sweeps: rank candidates by
      precision restricted to the crash-era test years, with the
      Wilson-interval caveat in the summary.

## Models

- [ ] Other model families, once Carter has answered the two rules in
      docs/next-steps.md ("Waiting on Carter"): a weighted, regularized
      logistic regression on the ranks, then a multilayer perceptron,
      then k-nearest-neighbors and support-vector comparisons. They need
      fold-internal imputation, disclosed, and are judged on the screen
      first.
- [ ] Encode the remaining non-numeric feature columns (`industry`,
      `famaindustry`, `scalemarketcap`, the `Y`/`N` condition flags, the
      filing-date fields) so that models can use them. `sector` is done
      (decision 31). Prefer upstream encoding; a per-row recoding here is
      acceptable if argued; a statistic fitted across rows (target or
      frequency encoding) is never acceptable. The classification
      columns hold today's values, not point-in-time ones.
- [ ] Explanations beyond impurity and gain: SHAP, permutation
      importance on the training folds, and per-prediction reason codes
      as optional `vml-predict` columns.
- [ ] Deep learning goes through upstream first: it needs a
      sequence-shaped dataset variant (each stock's point-in-time
      history by quarter). History is never flattened here
      (invariant 4).

## Upstream requests

Requests to the dataset repository. Nothing here is built locally
(invariant 4). Carter forwards them.

- [ ] **Market-state columns per snapshot date** (decisions 46, 80.7,
      85.2): the one input that would let a model learn when to buy
      less. It is also what would separate the rare region's good years
      from its bad ones. Listed in
      [the calibration plan](docs/notes/2026-11-23-calibration-plan.md),
      "Upstream request".
- [ ] **An outcome and a label measured against same-size peers**
      (decisions 32, 46, 75): per horizon, the 3-year CAGR minus the
      mean of the same quarter's stocks in the same band of
      market-capitalization rank, and its sign as a label. A cross-row
      label, so it belongs upstream beside the split machinery.
- [ ] **A recovery label measured inside a region** (decisions 63, 80.7).
- [ ] **The Foamex price check** (decision 73,
      [request](docs/notes/2026-11-26-upstream-foamex-price-check.md)):
      a 1-cent price that rises 451-fold in four months.
- [ ] A 2-year or 3-year high (decision 71).
- [ ] Size-neutral ranks, and within-sector ranks, of the columns the
      models lean on (volatility, return on capital, momentum, the
      conservative score).
- [ ] Insider transactions and institutional holdings (Sharadar SF2 and
      SF3), point-in-time by filing date.
- [ ] An outcome that treats a delisting as a portfolio does: the
      delisting date, and a return with the proceeds held in the
      benchmark until the horizon.
- [ ] An equal-weighted benchmark series in the price panel.
- [ ] Watch: of the fourteen 8-K counts, the forest used two (earnings
      releases and officer changes in the trailing year); the counts are
      an era marker before 2005 (data/versions.md).
- [ ] Watch: the earliest trustworthy year (survivorship depth) is still
      unverified upstream. Treat cross-sections before 2000 with
      suspicion.
- [ ] Later: drop the stored `label_{H}_cagr_ge_*` and `excess_ge_*`
      rungs, each now a one-line label expression. This breaks existing
      configs, so migrate their labels first.
- [ ] Only if early stopping is ever needed: an `inner_val` role inside
      each walk-forward fold, shipped in `splits.parquet`. A local
      validation split is never acceptable (invariant 1).
