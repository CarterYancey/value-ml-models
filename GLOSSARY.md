# Glossary

The shared vocabulary of value-ml-models. Every doc, note, logbook
entry, TODO item, config `note` and commit message uses these terms,
and uses one term per concept. A document does not define a glossary
term again inline. It links here once, at the top, and uses the term.

Each entry says what the thing *is*, in one or two sentences, and
lists the words to avoid for it. How the code implements a thing is in
`docs/experiments.md`, `docs/backtesting.md` and `docs/workflow.md`,
not here. Add a term the first time a document needs it, in the same
change. The format follows Matt Pocock's `domain-modeling` skill.

## Data

- **Dataset version** — one build of the upstream dataset, such as
  `dataset_v1.4`. Numbers from two versions are never compared.
  _Avoid_: "the data" when the version matters.
- **Patch version** — `X.Y.Z`: the same dataset code rebuilt on a newer
  raw snapshot, same column layout, different values (upstream
  decision 0021). A patch is a different dataset for comparison.
  `dataset_v1.4.1` is the dataset of record since 2026-11-24.
- **Dataset fingerprint** — `dataset_sha256`, the sha256 of
  `dataset.parquet` from the manifest's provenance block, logged with
  every run. Two builds can share a version label; they cannot share a
  fingerprint. "" for builds before decision 0021. _Avoid_: hash
  (alone), checksum.
- **Row** — one record at the grain `(permaticker, snapshot_date,
  snapshot_kind)`. _Avoid_: observation, sample, example.
- **Snapshot kind** — one of `low`, `median`, `high`: the three
  snapshots of a stock-quarter. Test rows are median-kind only.
- **Label** — the binary outcome a model is trained to predict, named
  by a label column or a label expression. _Avoid_: target, y.
- **Label expression** — a row-wise rule over label columns that
  defines a label, such as `fwd_3y_cagr >= 0`. Written by the
  config, evaluated by the loader.
- **Horizon** — the number of years a label looks forward: 1, 2, 3 or
  5. Written `3y`.
- **Outcome** — what a stock went on to do after a row's date, read on
  any label column. A pick's outcome is distinct from the label the
  model was trained on. _Avoid_: result (reserved for a run's metrics).
- **Feature** — a column a model may read, taken from the manifest's
  feature columns. Features are built upstream only. _Avoid_: input,
  variable, predictor.
- **The ranks** — the cross-sectional rank columns (`*_rank`). In
  `dataset_v1.4` there are 112 of them. "The 112 ranks" is the
  candidate forest's feature set.
- **Factor** — a single feature used as a ranking on its own, such as
  12-month momentum (`mom_12_2`), return on capital or the
  conservative score. _Avoid_: signal, except for the nine Piotroski
  signals, which carry that name upstream.
- **Conservative score** — the upstream composite rank of low 36-month
  volatility, high 12-month momentum and high net payout yield
  (`conservative_score`).
- **Universe** — a declared row filter on feature columns: the rows a
  model is trained and evaluated on. Each universe has its own cells
  and baselines. _Avoid_: filter (alone), subset.
- **Liquidity floor** — a universe defined by trading volume. "The
  100k floor" is `dollar_volume_3m >= 100000`. "Carter's floor" is
  `dollar_volume_3m_rank >= 0.2`, used by the candidate. _Avoid_:
  investability filter.
- **Large caps** — the universe `log_marketcap_rank >= 0.8`: the
  largest fifth of companies by market capitalisation.
- **The larger half** — the universe `log_marketcap_rank >= 0.5`, on
  top of a liquidity floor. As a backtest filter it is the proposed
  change to the candidate (decision 58). _Avoid_: large stocks, big
  caps, when this exact band is meant.
- **The fallen universe (F50)** — the universe `dist_5y_high <= -0.5`
  on top of the 100k floor: liquid stocks that trade 50% or more below
  their own 5-year high. A stock with no 5-year price history is
  outside it. Introduced in decision 61. _Avoid_: drawdown stocks,
  beaten-down stocks, losers (that word means a pick whose CAGR was
  below zero).
- **The fresh-fall universe (W40)** — the universe `dist_52w_high <= -0.4`
  on top of the 100k floor: liquid stocks that fell 40% or more from
  their 52-week high. It measures a fall within the last year, where
  the fallen universe measures a state. Introduced in decision 64.
- **F30, F70, W30, W50, W70** — the same two universes at other depths:
  F followed by a number is `dist_5y_high <= -0.<number>` and W followed
  by a number is `dist_52w_high <= -0.<number>`, each on top of the 100k
  floor. Together with F50 and W40 they form the grid of decision 70.
- **The 2020 window** — a backtest window with buys from 2006 to 2020
  and the account valued on 2020-12-31, SPY on the same deposits. The
  fallen-stock program's comparison window from decision 70, chosen
  because Carter's working assumption is that the market since 2021 is
  a bubble. The same buys valued at the end of 2023 are "the 2023
  window". _Avoid_: pre-bubble window, early window.
- **Recovery label** — the label `fwd_3y_cagr >= 0.26`: the stock at
  least doubled within 3 years. Used inside the fallen universe.
  _Avoid_: doubler, 2x label.
- **Emphasis** — a training-time weight: the rows inside a declared
  region of feature columns carry `factor` times their mandatory
  sample weight, every other row and every test row untouched
  (`[emphasis]`, decision 78.6). Not a universe: every row stays in
  the fit and the run is counted in its label's own cell. _Avoid_:
  upweighting, oversampling (no row is duplicated or made up).
- **Same-size peers** — the rows in the same 5% band of
  `log_marketcap_rank` in the same month as a pick. Every selection
  is read against them, because company size explains most of a lead
  over all rows. _Avoid_: "all rows" as a comparison group.

## Splits and evaluation

- **Scheme** — the way rows are assigned to train and test:
  `walkforward` (all model selection), `holdout` (sealed),
  `entity_holdout` and `random_kfold` (diagnostic only).
- **Fold** — one walk-forward train/test split with a single test
  year. The 16 folds have test years 2005 to 2020 and are frozen in
  `split_folds.parquet`. _Avoid_: split (the general mechanism).
- **Test year** — the calendar year of a fold's test rows. An
  era-sliced table is one row per test year. _Avoid_: era, period,
  when a single fold is meant.
- **Fold mean** — a metric averaged over the 16 folds. The default
  form of every walk-forward number.
- **The two halves** — the test years 2005–12 and 2013–20. A result
  counts only if it holds in both.
- **Walk-forward number** — a fold mean from the walkforward scheme.
  It is selection-biased and never a result of record.
- **Holdout** — the sealed test years of a cell, evaluated by
  `scripts/run_final_eval.py`. For the 3-year label on
  `dataset_v1.4` they are 2021–23. _Avoid_: test set, validation set.
- **Look** — one evaluation of a cell on its holdout. The look count
  is part of every holdout number ("look 1 of 1", "20 looks in all"),
  because from the second look on the holdout is a validation set.
  _Avoid_: peek, check, evaluation (for the holdout).
- **Out of sample** — the years 2021 to 2026-08, which no model was
  selected on. The candidate's record there comes from the backtest
  and, going forward, from paper trading. _Avoid_: holdout (a
  narrower term), live.
- **Cell** — one combination of label, horizon and universe. It is the
  unit of the ledger, of baselines, of trial counts and of holdout
  looks. A universe makes a new cell: `label [universe: ...]`.
- **Cell C** — the 3-year "not a loser" label on all rows:
  `fwd_3y_cagr >= 0 & fwd_3y_max_drawdown_from_entry < 0.3`.
  The candidate's forest is trained on it.
- **Cells A and B** — the letters named different labels in different
  notes. In the [compounder note](docs/notes/2026-09-28-drawdown-compounder-cells.md)
  A is `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown < 0.3` and B is
  `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2`. Later
  notes reuse the letters; read each note's own definition. Do not
  use bare letters in new writing.
- **Not a loser** — the plain name of cell C's label: the stock did
  not lose money over three years and never fell more than 30% from
  the entry price.
- **Trial** — one configuration run in a cell, failures included.
  Trial counts accompany every number because they measure the
  selection bias.
- **Selection bias / selection-biased** — the upward bias of a number
  that is the best of N trials. The more trials, the larger the bias.
  Walk-forward numbers are selection-biased; a first holdout look is
  not. _Avoid_: optimistic, flatters, overfit (a property of a model,
  not a number).
- **Result of record** — a number that may be presented as the
  project's performance: a first holdout look, or a promoted
  backtest. _Avoid_: headline (that is the metric chosen to lead a
  report, not its status).
- **Base rate** — the share of rows in a cell whose label is true. It
  is the no-skill reference for precision and PR-AUC. _Avoid_:
  prevalence, prior, baseline.
- **Baseline** — a trivial model run in the same cell: majority class,
  single-factor rank, random. _Avoid_: base rate, benchmark.
- **Precision at K (p@K)** — among the top K rows per test year by
  score, the share whose label is true. p@20 leads every report.
  _Avoid_: hit rate, accuracy.
- **PR-AUC** — the area under the precision–recall curve, read against
  the base rate. The metric for a whole ranking.
- **Lead** — the picks' return minus a comparison group's, in CAGR
  points a year over the horizon: "+4.6 points a year against
  same-size peers". A lead is always named with its comparison group.
  _Avoid_: edge, alpha, outperformance, excess (an excess CAGR is a
  label column, measured against SPY).
- **Losers** — the share of picks, or of rows, whose CAGR over the
  horizon was below zero. _Avoid_: failures, misses.
- **Effective sample size** — the sum of the horizon's sample weights.
  Reported in place of row counts.

## Experiments and selection

- **Config** — one TOML file under `experiments/` that defines a run.
  A config that has run is never edited; it is copied under a new
  name.
- **Run** — one execution of a config: a fit per fold and its
  evaluation. Every run goes to the ledger.
- **Sweep** — a grid of configs run as one batch by `vml-sweep`. Each
  expanded config is a trial.
- **Ledger** — `experiments/results.csv`: every run ever, failures
  included.
- **Promoted** — staged into `reports/promoted/` by `vml-promote` as a
  result worth keeping, together with its config and note.
- **Forest** — a scikit-learn random forest classifier. "The forest"
  on its own means the candidate's forest: cell C, the 112 ranks.
  _Avoid_: RF, "the model" when a specific forest is meant.
- **Blend** — two or more rankings, such as a forest's scores and
  factors, combined by mean rank into one ranking.
- **The candidate** — the one strategy in paper trading, fixed by
  decision 24: the forest blended by mean rank with 12-month momentum
  and return on capital, buying the top 10 each month, at most 2 per
  sector, equal weights, inside Carter's floor. _Avoid_: the model,
  the strategy, the portfolio.
- **Sell discipline** — the candidate's variant that sells a holding
  once it is outside the top 20% of the month's ranking, or no longer
  ranked. The plain candidate buys and holds. _Avoid_: variant B.
- **Stand-in** — a factor-only blend (lowest 12-month volatility,
  momentum and return on capital by mean rank) that takes the
  candidate's place on years before 2005, where no fold model exists.
- **Arm** — one of the configurations compared in a pre-registered
  experiment, each with its own prediction. _Avoid_: variant, option,
  branch.
- **Prediction** — an expected result written in the config or the
  decision log before a run, and marked afterwards as held, missed or
  half held.
- **Decision** — a numbered entry in the decision log that records a
  choice, who made it, and why. Decisions 1 to 72 are in
  [the log of 2026-09-29](docs/notes/2026-09-29-decisions.md), which
  is closed and not edited again; decision 73 onward are in
  [the log of 2026-11-26](docs/notes/2026-11-26-decisions.md).
  "Decision 36" is Carter's direction of 2026-10-01.
- **Screen** — the report that applies the backtest's selection rule
  (top K per quarter, capped per sector) to a run's test rows and
  reads the picks' outcomes. Report-only, no costs, no cash. _Avoid_:
  portfolio screen, pick screen, in prose (`[pick_screen]` is the
  config table).
- **Backtest** — the simulated portfolio from `vml-backtest`: monthly
  buys, 35 bps a side, deposits, valued against SPY with the same
  deposits. The yardstick of record for comparing labels and
  strategies.
- **Paper trading** — running the candidate forward each month on new
  data with `vml-predict`, without money, as the out-of-sample
  evidence. Runbook: [docs/paper-trading.md](docs/paper-trading.md).
- **Deployment bundle** — a model refit on all labeled rows for
  `vml-predict`, or on the labeled rows before a training cutoff. Its
  scores are a ranking, never an evaluation.
- **Training cutoff** — a date given to `vml-train-deploy --train-end`.
  The deployment refit then fits only the labeled rows whose
  `snapshot_date` is before it. The cutoff is recorded in the bundle,
  in the ledger row and in every prediction sidecar (decision 60).
  _Avoid_: "pre-bubble model", "clean model", "untainted model".
- **Lab branch** — a branch named `claude/lab-<date>` that holds every
  config and report of one session. `vml-queue new-lab` creates it from
  `origin/Claude`. It is never created from another lab branch and never
  merged anywhere. Once the session's results branch has merged,
  `vml-queue archive-lab` tags the branch's last commit
  `archive/lab-<date>` and deletes the branch (decision 68).

## Backtests

- **Final value** — what the portfolio is worth at the end of a
  backtest, after deposits, costs and sells. It is the first number
  read for a backtest, with the CAGR beside it (decisions 53 and 72).
  _Avoid_: money, "in money", "on money".
- **CAGR of a backtest** — the metric of record for a backtest
  (decision 72): the annual rate at which the deposits compounded into
  the final value, the internal rate of return of the dated deposits
  and the final value (XIRR). It is `cagr` in the report's headline and
  `mwr_annualized` in the ledger, where the column keeps its old name.
  Both legs of a backtest get identical deposits, so the CAGR ranks
  them as the final value does. A label's CAGR is a different thing:
  the horizon return of one stock, `fwd_{H}y_cagr`. _Avoid_: MWR,
  money-weighted return, which named this number before decision 72.
- **TWR** — the time-weighted return, a year: the compound growth rate
  of one unit held from the first day to the last. Deposit timing does
  not affect it, so a month on a tiny early account counts as much as
  a month on a full one; the W70 portfolio of decision 71 had the
  program's highest TWR and its least money. It is not a metric of
  record. It stays in the report after the drawdown and in the
  per-year table, and is read only beside the final value, the CAGR
  and the per-year table (decisions 71 and 72).
- **MWR** — the old name of the CAGR of a backtest (before decision
  72). Use CAGR; the ledger column is still `mwr_annualized`.
- **Worst drawdown** — the largest fall from a peak to a later low in
  the portfolio's value over the run. _Avoid_: max drawdown, which
  names the label column `fwd_3y_max_drawdown_from_entry`.
- **Lead over same-size peers** — the buys' mean excess CAGR minus
  their same-size peers' mean excess CAGR, by cohort. It measures the
  selection and nothing else. _Avoid_: alpha, edge, "the selection"
  used as a number.

## The project

- **The thesis** — Carter's founding claim (2026-09-29): a model with
  high precision on a modest return target beats the market over the
  long run by avoiding big losers. It depends on three conditions:
  (1) precision of about 0.65 or more, (2) the era, since such
  strategies lead during and after market falls, and (3) the variance
  of the picks' returns.
- **Working assumption** — Carter's reading, adopted for planning by
  decision 36, that 2021–26 is a bubble led by stocks that fail a
  value investor's test, which a value strategy trails through and
  then waits out. It is an assumption, not a conclusion. _Avoid_:
  "Carter's reading" without saying what the reading is.
