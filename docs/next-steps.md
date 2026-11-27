# Next steps

The plan for the next session, as of 2026-11-27. A session starts here
(see [agents.md](agents.md), "Start of a session") and rewrites this
file before it ends. The reasons behind the order are in
[decisions.md](decisions.md); what is known is in
[findings.md](findings.md).

## Before starting

1. The lab branch `claude/lab-2026-11-26` still exists on `origin`,
   although its archive tag `archive/lab-2026-11-26` was created at the
   same commit and its results branch merged (pull request 24). Delete
   it with `uv run vml-queue archive-lab claude/lab-2026-11-26 --delete`,
   or `git push origin --delete claude/lab-2026-11-26` if the tag
   already exists.
2. Create today's lab branch with `uv run vml-queue new-lab`.
3. The configs, reports, bundles and predictions of the last sessions
   are on the archived lab branch. Restore the ones a step needs with
   `git checkout archive/lab-2026-11-26 -- <path>`, then
   `git reset -q -- <path>` so they stay ignored.

## The order of work

The three remedies of decision 81 lead, in the order of the evidence
behind them (decision 85.2).

### 1. E11 on `dataset_v1.5.1` at three seeds, then its pick list

E11 is the candidate's ranking choosing the 50 highest-ranked large caps
with an earnings yield of 5% or more, weighted by market capitalization.
It holds at three seeds on `dataset_v1.4.1`; the step is to show it on
the dataset of record and then give it a paper-trading list beside the
candidate's (decision 83.3).

- The forest bundle at seed 23 exists on v1.5.1
  (`forest_nonloser_dd30_3y_v151`), and so do the two factor legs.
  Train the forest bundles at seeds 232 and 1776 on v1.5.1 with
  `vml-run`.
- Run the three E11 backtests one at a time. A v1.5.1 backtest peaks at
  up to 13.8 GB of the sandbox's 14 GB, so nothing else may run beside
  it.
- Write the predictions in the configs first. On v1.4.1, E11 earned
  12.1% to 12.3% time-weighted, with a worst drawdown of −37%.
- Then produce E11's list with `vml-predict --weighting marketcap` and
  E11's filters. A dry run of that list exists on the archived lab
  branch, in `predictions/inference_2026-11-20__e11_blend_mcap_top50_ey5.csv`
  and its sidecar. It chose 50 of the 120 large caps with an earnings
  yield of 5% or more; energy held 39% of the weight and technology 26%,
  and MU and XOM about 12.5% each. On that day the valuation floor did
  most of the choosing. Before anything is traded on the list, compare
  it with what the backtest held in 2025 and 2026.

### 2. A valuation floor tight enough to hold cash

The second remedy is a reason to buy less when the market is dear. Until
upstream provides market-state columns, the stand-in is an earnings-yield
floor on the equal-weighted candidate that is tight enough to leave
money uninvested. The floors of 5% and 8% held no cash, because ten
stocks always cleared them (decision 81). The 8% floor earned 12.6% a
year in 2021 to 2026 against the candidate's 7.1%, which is the reason
to look, and ended with 8% less money and a deeper drawdown, which is
the reason for caution.

- First write a decision with the thresholds (or a smaller candidate
  pool) and the predictions. Judge the result by the portfolio rule of
  decision 85.1.

### 3. The region search

The third remedy is more upside without more losers. Decision 85.3
reopened the search for a region of the universe inside which a model
separates the big winners better than it does across the whole
universe.

- First write a decision that lists the regions and the predictions.
  Carter's first region is stocks 30% or more below their one-year high
  (`dist_52w_high <= -0.3`), inside the liquidity floor.
- **That region has been trained in before.** It is the universe W30
  of round 6 of the fallen-stock program (decisions 70 and 71, on
  `dataset_v1.4.1`). The "not a loser" forest was trained inside it and
  backtested, and ended within 2% of SPY before 2021
  ([fallen stocks](notes/2026-11-25-fallen-stocks.md), round 6). The new
  decision should cite that run, say what the new runs add (the
  `[emphasis]` arm, `dataset_v1.5.1`, and reading the picks on the share
  that doubled), and predict against it.
- Train the candidate's forest inside each region twice: once as a
  `[[universe]]`, and once with `[emphasis]` at a few factors, one file
  per factor. Read the picks on the control's outcomes (the lead over
  same-size peers, the share that lost money, the share that doubled),
  inside the region and against the control's picks.

### 4. Deep value

Beside or after step 3 (decision 83.5): `ncav_to_marketcap`, tangible
book value against market capitalization, and the earnings yield, each
as a floor and as a universe, with the forest as the gate and the
five-year horizon as the outcome. What the record already says: a deep
fall alone is a bet on the market's recovery (decision 80); the
earnings-yield ranking alone has 57% losers (sweep B of decision 78);
and a floor inside the safe set helped (E11). Each experiment gets its
own decision and predictions first.

### Throughout

- **Paper trading** of the candidate follows
  [paper-trading.md](paper-trading.md). The November 2026 list came from
  the v1.4.1 bundles on 2026-11-24. The v1.5.1 build gives the same
  forest, so nothing is refit.
- **The backtest's memory use** (TODO.md, first item) is worth fixing
  before any unattended chain of v1.5.1 backtests.

## Waiting on Carter

Listed with their reasons in [decisions.md](decisions.md), "Waiting on
Carter":

- the larger-half filter (decision 58);
- the training cutoff (decision 60);
- the F50 portfolio (decision 71.1);
- a price floor in the investability filter (decision 71.3);
- forwarding the upstream requests, the Foamex price check first
  (decision 73.1; TODO.md, "Upstream requests");
- the two rules for other model families (decision 36);
- which measure rules when the time-weighted return and the CAGR
  disagree (decisions 72 and 85.1);
- whether decision 70.1's caveat about the 2020 window still stands.

Also Carter's, from earlier sessions and not decisions:

- what is bought from the November 2026 list (RPRX, KO, EBAY, CHD,
  SAIC, V, HAS, NDSN, WAB, PSX; [paper-trading.md](paper-trading.md));
- reading the host's sandbox log for 2026-11-25, 02:55 to 03:00 local
  time, to confirm that memory killed the sandbox (decision 68);
- three tracked configs from decisions 74 to 76 that are neither
  promoted nor in `experiments/KEEP`: `baseline_v151_labels_3y`,
  `lgbm_v151_features_nonloser_3y` and `xgb_v151_features_nonloser_3y`;
- the leftover feature branches `claude/backtest-realism`,
  `claude/emphasis-weights` and `claude/predict-weights`, whose code is
  already in `Claude` through pull request 24. They can be deleted.

## Recorded, not next

Questions worth an experiment some day. None is in the plan.

- Why worst rank selects better and earns less: smaller stocks, holding
  past three years, or the 2008 fall (decision 51). Low priority.
- Why the screen is about 0.02 a year harsher on blends with momentum
  than the backtests' own buys. A third is the delisting convention;
  entry timing is the untested rest.
- Does the candidate's edge survive a longer wait between the snapshot
  and the buy? The backtest buys one to six months after the snapshot.
- Why the plain-ranks forest of `calib_levels_nonloser_plain_3y` screens
  differently from the candidate's forest bundle with the same
  parameters. Compare the expanded configs and hashes before using
  either as a bar again.
- Re-read `year_balance` against plain ranks under the screen rule. Both
  forests need refitting on the current dataset.
- Seeds 232 and 1776 of the huber regressors on CAGR and on excess CAGR,
  to test whether their difference is chance (decision 39).
- A looser selling band (selling below the top half) for cap-weighted
  books (decision 82.6).
- A baseline on the holdout rows of cell C. It would be the cell's
  second look, and that look is Carter's.
- On `dataset_v1.1`: was the edge of the 17 re-mapped columns a quarter
  identifier or stock information? Needs per-quarter metrics.
- The backtest count in findings.md, "The portfolios of record", needs
  restating from the ledger.
