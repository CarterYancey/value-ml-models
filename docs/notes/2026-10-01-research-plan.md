# Research plan after the run to 2026

Carter's directions of 2026-10-01 (decision 36 of the
[decision log](2026-09-29-decisions.md)), sorted: what each asks, what
the record already says, what exists in the code, what it needs, and
whether it is a queue item or a session of its own. The candidate and
its paper trading are in [docs/paper-trading.md](../paper-trading.md)
and are not reopened by anything here.

How every item is read (decision 36): walk-forward 2005–2020, the
screen against same-size peers (`peer_column`), both halves, three
seeds, the single-factor bar in the same universe, the rule written
before the run. 2021–26 is context, not a criterion. A new arm has to
lead the bar it is set against by 0.01 a year in both halves
(decision 34.3). The bars inside the 100k floor, entries of 2005–12 /
2013–20, lead over same-size peers: the forest +0.030 / +0.027
(losers 0.20 / 0.12), the candidate +0.022 / +0.053; inside large
caps, return on capital alone +0.039 / +0.030.

## Ready to run (in `experiments/queue.toml`; no new code)

### 1. Continuous models that predict growth

*Asked:* more weight on models that predict the size of the outcome,
not a binary label.
*Have:* `lightgbm_regressor` and `xgboost_regressor` (the regression
reframe: scores are predicted returns, measured on a binary
`eval_label`, no Brier). Objectives: mean, huber, quantile.
*Record:* inside large caps, on the excess return, huber had no lead
after 2013 and quantile 0.25 led by +0.016 to +0.020
([large caps](2026-10-01-large-caps.md)). Not yet run on every row,
on plain CAGR, or at other quantiles.
*Queued:* `lgbm_regressor_growth_allrows_3y`: 3y CAGR and 3y excess
CAGR, huber and quantiles 0.5 / 0.25 / 0.1, all rows, read inside the
100k floor against peers. The low quantiles are the interesting
ones: "whose bad case is best" is low risk and upside in one
objective, which no binary label here has managed (cell A, the
"beat SPY safely" cell).
*After it:* if a quantile arm passes, three seeds, then
`xgboost_regressor` and a small parameter search; if none does, the
reframe is closed with the classifier searches.

### 2. A model of over-priced stocks

*Asked:* a model very good at identifying stocks about to fall, for
a possible short side (risky, not preferred; worth it only at high
precision on something like a 50% fall from entry) and as a
market-state signal (many high-confidence calls: an era for cash).
*Have:* the label is one expression
(`fwd_1y_max_drawdown_from_entry >= 0.5`); `score_thresholds` gives
the number of rows at or above a score per year; the screen gives
the calls' outcomes.
*Record:* the candidate's forest read from the bottom is already
such a model: its lowest decile of investable stocks lost money 69%,
68% and 82% of the time over three years in 2005–12, 2013–20 and
2021–23 ([out of sample](2026-10-01-out-of-sample.md)). Two cautions
from earlier work: the label is mostly the market's year (inside the
liquid half the one-year rate runs from 0.04 to 0.53 by entry year),
and model confidence has lagged the regime (decision 20: the forest
scored highest for 2006–08 entries, where it was most wrong).
*Queued:* `baseline_factors_crash_dd50` and `forest_crash_dd50`
(one- and three-year cells, inside the more liquid half, three
seeds). Read on precision at the top by year, on what the calls did
(including the share that rose 30%: what a short loses on), and on
whether the count of high-confidence calls rises before 2008 and
2020 or after.
*Needs a decision before anything is traded on it:* a count of model
calls used as a cash rule is a portfolio rule computed from fold
models at the trade date, not a dataset feature, so invariant 4 does
not forbid it; it would be a new `Strategy` and its own backtests.
Shorting has costs the engine does not model (borrow, recalls,
unbounded loss): a short leg is a design session, not a config.

## Small code, then a sweep

### 3. Blends beyond the mean of ranks

*Asked:* for example only stocks in both models' top 100; more
creative portfolio construction.
*Have:* `combine` = `product`, `mean`, `min`, `mean_rank`; per-model
score floors; column filters; the sector cap; the rank sell rule.
*Record:* mean rank of two and three legs, 35 backtests. The blend's
increment over the forest was +2 to +3 points a year against
same-size stocks in 2005–2020 and reversed for the buys of 2021–23.
*Build:* `combine = "worst_rank"` (rank by the worse of the models'
ranks: the stocks every model ranks highly, which is "in both top
N" for any N at once) in the backtest and in `vml-eval`'s `blend`,
so it is read on the screen before a backtest. One branch, small.
*Then:* the candidate's three legs by worst rank against by mean
rank, on the screen with peers. Portfolio rules worth one backtest
each afterwards, each named before it is run: a position cap; fewer,
larger positions (top 5); a cash rule from item 2.

### 4. A cell that needs no blend

*Asked:* move the creativity to the label, so one model does it.
*Record:* tried and closed: "CAGR ≥ 10% and drawdown < 20%" (cell A:
the same calm picks), "beat SPY and drawdown < 20%" (B: worse at
beating SPY), "beat SPY and drawdown < 30%" inside large caps (p@20
below its base rate), "CAGR ≥ 15%" (no skill). Every label with an
upside clause has been learned as its risk clause.
*What is left:* the upstream label measured against same-size peers
(TODO, upstream requests): the one target that asks for selection
and whose base rate does not move with the market. And item 1's low
quantiles, which are a label-free way to ask for the same thing.

### 5. The Piotroski signals against the F-score

Run on 2026-10-01 (`forest_piotroski_3y`); result in the logbook.

## Sessions of their own

### 6. Calibration, and a confidence-weighted strategy

*Asked:* models whose confidence scores are accurate, then sizing by
confidence; only when that is exhausted, market-state features for
holding cash.
*Record* ([blends and calibration](2026-09-30-blends-and-calibration.md),
[1y cell](2026-09-30-one-year-cell.md)): prequential isotonic
calibration works mechanically and does not help. An honest
calibrator for a 3-year label only knows outcomes four years old (two
for a 1-year label); it gave no row 0.5 in 2011–13, when the top 20
were right 95% of the time, and gave 0.5 to 43% of rows in 2017–19 at
a precision of 0.31 to 0.48.
*Why, and so where to look:* the label's base rate is a market
outcome (cell C: 0.16 to 0.59 by entry year). No function of a
stock's own columns can be calibrated to a quantity that moves that
much with the year. Three routes, in the order they could be tried:
1. **A target whose base rate does not move**: "beat stocks of its
   own size" is about half in every year by construction. A model of
   it could be calibrated across eras. It is a cross-row label and
   has to come from upstream; `label_3y_beat_spy` is the nearest
   thing on disk, and the share of investable stocks beating SPY
   over three years still runs from 0.29 to 0.53 by entry year.
2. **Confidence as a rank within the date, not a probability**: size
   by position in the month's ranking. Testable now
   (`weighting = "score"` exists for probabilistic single models).
   The record is not encouraging: the top of the forest's ranking is
   no purer than its top 20, and among large caps its top four
   quintiles earn the same.
3. **Conditioning on market state**, which is the upstream request
   Carter puts last.
*Session plan:* first measure, for the candidate's forest, whether
outcome rises with rank *inside* the top 50 of a month at all
(reliability by rank bucket, per year). If it does not, sizing by
confidence has nothing to work with whatever the calibration, and
the session moves to route 1's design with upstream.

### 7. Other model families: linear, neural, unsupervised

*Asked:* consider other models, neural nets, unsupervised models;
explainability may give way to performance.
*Have:* trees, forests, LightGBM, XGBoost (all take NULLs natively
and the sample weight).
*Needs, and the decisions inside it:*
- **A missing-value policy.** Linear models and neural nets cannot
  take NULLs. The dataset contract allows fold-internal imputation
  only, disclosed; a rank column is already 0 to 1, so the natural
  form is "impute the fold's median and add an is-missing indicator".
  That indicator is a per-row recoding like the flags (decision 17);
  the imputation is a fitted, fold-internal step and belongs inside
  the model wrapper.
- **A dependency.** scikit-learn's MLP is in the environment and
  takes sample weights; anything larger means PyTorch, which
  CLAUDE.md's "keep the dependency list short" makes Carter's call.
- **Unsupervised models and invariant 4.** A cluster label or an
  embedding fed to a model is a derived feature. Learned inside the
  fold, as a stage of the model, it is model architecture and reads
  nothing the model could not read; learned once over all rows it
  would be look-ahead. Proposed rule for Carter to accept or not: a
  transform is allowed when it is fitted on the fold's training rows
  only and saved in the fold's bundle, and never otherwise.
*First experiments, in order of cost:* a regularised logistic
regression on the ranks (the missing linear baseline: it says how
much of the forest is additive); an MLP on the same inputs; then a
fold-internal clustering as an extra input to the forest.
*Expectation, stated so it can be wrong:* three searches over
forests, LightGBM and XGBoost moved PR-AUC by 0.005 in cell C, and
three model families land within 0.02 of each other; a fourth family
on the same 112 columns is more likely to match them than to beat
them. The case for the session is the continuous and peer-relative
targets, where the tree models have been tried least.

### 8. Market-state features, and when to hold cash

Carter's order: after calibration is exhausted. Upstream (PLAN 5.6).
Item 2's count of high-confidence calls is the one version that can
be tried here first.

## Closed

- **Data before 1998** (Carter, 2026-10-01): Sharadar's history
  starts there and nothing of the same quality goes further back.
  The growth of the dot-com bubble cannot be tested; decision 35's
  result covers its last year and its aftermath.

## Order proposed

1. Now: paper trading set up on the host from
   [docs/paper-trading.md](../paper-trading.md) (Carter); the queue
   (items 1 and 2: "work the queue").
2. Next session: read the queue's results; item 3's `worst_rank`
   and its screen.
3. A design session on calibration (item 6), starting from the
   rank-bucket measurement.
4. A session on model families (item 7), once the missing-value rule
   and the dependency are decided.
