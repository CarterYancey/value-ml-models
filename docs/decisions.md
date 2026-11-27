# Decisions in force

This file lists every decision that still affects future work: the
rules, criteria, settings and working assumptions that a session must
respect, the one-time actions that have been decided but not yet done,
the questions waiting on Carter, and the lines of research that are
closed. Each entry says what is in force, why, and which numbered
decisions hold the full reasoning.

The numbered decisions themselves are in the decision log:

- [notes/2026-09-29-decisions.md](notes/2026-09-29-decisions.md),
  decisions 1 to 72 (closed; never edited again);
- [notes/2026-11-26-decisions.md](notes/2026-11-26-decisions.md),
  decision 73 onward (open).

A link such as "(85.1)" means decision 85, item 1. How this file is
kept current is in [agents.md](agents.md), "The records". In short: a
new standing decision gets a line here in the same commit that logs it;
a changed decision has its line rewritten; a one-time action is removed
once done; a closed line of research gets one line at the end.

This file was built on 2026-11-27 from a review of decisions 1 to 85
(decision 86).

## The goal

- **The thesis.** A model with high precision on a modest return
  target beats the market over the long run by avoiding big losers.
  Precision of 0.65 is a reference point, not a minimum. (Preamble of
  the first log; [GLOSSARY](../GLOSSARY.md), "The thesis".)
- **The goal of record.** In principle, more money than SPY over the
  long run. For now a portfolio is judged on return per unit of risk,
  by the rule under "How a portfolio is judged". The stretch target is
  20% a year, and deep-value stocks are the direction to keep working.
  Carter's reasons: the present period looks like one in which value
  strategies trail and should recover, and a simulated final value
  depends heavily on deposits, fees and taxes. (83.1, 85.1;
  [why not the market](notes/2026-11-27-why-not-the-market.md).)
- **Money comes before the form of the thesis.** If more money needs a
  different approach from loser-avoidance, the approach changes, as
  long as the method stays principled. (43.2, 47.)
- **A manageable list.** The number of picks must suit one person
  working a few hours a week: tens a quarter is fine, a thousand is
  not. (Preamble of the first log.)

## How a portfolio is judged

- **The portfolio rule.** A portfolio is carried to three seeds, and
  then proposed to Carter, when over the walk-forward years 2005 to
  2020 it beats SPY on time-weighted return and on worst drawdown, and
  its buys pass the screen rule below against the control. Its return
  in 2021 to 2026 and its final value under the five deposit schedules
  are reported beside the rule as context. Beating SPY over the whole
  window remains the ideal and is said when it happens. The candidate,
  E10 and E11 pass. This replaced the rules of 21.2 and 81.2. (85.1,
  amending 83.1.)
- **The backtest template.** Monthly deposits, buy and hold, an SPY leg
  with identical deposits, 35 basis points a side, inside Carter's
  liquidity floor `dollar_volume_3m_rank >= 0.2`, buys and valuation to
  2026-08-21. Every backtest is a trial and is counted. The template is
  not tuned to each candidate, and the per-year table is read, not the
  final figure alone. (6, 25.2, 28.)
- **The metric of record for a backtest is the CAGR**, the
  money-weighted growth rate of the dated deposits into the final value
  (XIRR, shown as `cagr` in the report headline). The time-weighted
  return stays in the report and the per-year table, and is read beside
  the final value. (72, 73.3.) *Note:* the portfolio rule above judges
  on time-weighted return, not on the CAGR. No decision reconciles the
  two; this is listed under "Waiting on Carter".
- **Five deposit schedules.** Every backtest report shows the final
  value of the strategy and of SPY under five schedules (flat, growing
  3% a year, growing 6% a year, all at the start, flat to the end of
  the folds and nothing after), so that no single schedule's final
  value is read as the result. The schedule alone moves the candidate
  from 13% behind SPY to 1% ahead. Taxes and a cost model by size and
  era are not in the engine yet and are named in each report's caveats.
  (84.1, 84.4; [backtest realism](notes/2026-11-27-backtest-realism.md).)

## How a model or a selection is judged

- **Read every selection against same-size peers.** Company size
  decides more than any model, so a selection is compared with stocks
  of the same size, never only with all rows or with SPY. Backtests
  report `vs_peers`; the screen uses `peer_column =
  "log_marketcap_rank"`. Picks are not asked to foresee crashes; crash
  years are read like any other. (32, 50.)
- **The screen rule.** An arm's picks are compared with same-size peers
  on two outcomes: the lead (the picks' mean three-year CAGR minus their
  peers') and the share of picks that lost money. The comparison is
  paired by test year with the control, which is the candidate's forest
  in cell C on the 112 old rank columns inside the 100k floor (p@20
  0.75, a lead of +0.029 a year, 17% losers against 30% for its peers,
  on `dataset_v1.5.1`). An arm passes when its gain over the control is
  positive at about two standard errors, ahead in ten or more of the
  sixteen years, and no worse than noise in either half (2005 to 2012,
  2013 to 2020), on both outcomes. A passing arm goes to three seeds,
  then to a backtest. (74.4, building on 16, 33, 34.3, 50.)
- **The control runs inside every sweep.** Cell C, the 112 old ranks,
  seed 23, `universe_scope = "test"`, so that every pairing stays
  within one file. The control at three seeds is the `dataset_v1.5.1`
  reference for cell C inside the floor. (75.3, 78.1.)
- **A screen gain is not a money gain.** An arm goes from the screen
  to seeds and a backtest, never straight into the candidate. This has
  failed three times: the 8-K counts led by 1.1 points a year at three
  seeds and ended with 5% to 9% less money. `vml-backtest` is the
  yardstick of record. (47, 51, 77.)
- **Precision ranks a model only on its own label.** p@20 and PR-AUC
  say how well an arm predicts its label. They do not say what a
  portfolio of its picks does: LightGBM matches the forest's p@20 and
  its picks have no lead over their peers. A new label is read on lead
  and losers, never on its own precision. (74.4, 76, 78.1.)
- **Three seeds before anything is carried forward.** A result that
  fails on seeds 232 or 1776 is not carried. (9, 36, 74.4.)
- **A bar set before a run is a prediction, not a gate.** It is
  written down and graded; a miss is read, not used to discard an arm
  that is better than noise. (50.)
- **Report the mean beside the median.** An equal-weighted portfolio
  earns the mean. Holding cash when nothing clears a bar is a valid
  strategy, and the number of picks at a threshold is part of the
  result. (13.2.)
- **Each blend is its own configuration** in its cell's trial count.
  (19.)

## Evidence and the years it comes from

- **2021 to 2026 is not used to choose.** Those years are the only
  stretch no choice was made on. They are read for fixed candidates and
  reported as context; a further run on them needs a decision saying
  why it is not a selection. (28, 36, 85.1.)
- **1999 to 2004 is untouched by any search** and may be used once, as
  a check, for whatever is carried forward. It has not been used since
  decision 35's test. (36.)
- **The sealed holdout belongs to Carter.** One look per cell; a
  further look is counted and disclosed. Look counts are kept with
  every holdout number but do not hold experiments back. A baseline
  computed on the holdout rows of cell C would be that cell's second
  look. (13.3, 29; CLAUDE.md invariant 2.)
- **Data before 1998 is closed.** Sharadar starts in 1998 and nothing
  comparable goes further back. (36.)

## Data

- **New work uses `dataset_v1.5.1`.** No v1.4.1 number is compared with
  a v1.5.1 number. The candidate's record stays on `dataset_v1.4.1`,
  and the v1.5.1 build reproduces it to the dollar, so the candidate's
  legs are not refit until upstream changes a column the candidate
  reads. (55, 74.1, 77.2.)
- **Compare builds by fingerprint.** Two builds can share a version
  label. Before comparing two runs, check `dataset_sha256`, not only
  the version string. Numbers logged on `dataset_v1.4` before
  2026-11-23 belong to a build that no longer exists and are context
  only. (54, 55; CLAUDE.md invariant 3.)
- **An extreme price move is an upstream data question.** Nothing in
  this repo corrects a price. The Foamex path (a 1-cent stock that rises
  451-fold in four months) is unverified, and every record that cites
  the W70 run says so. (73.1;
  [request](notes/2026-11-26-upstream-foamex-price-check.md).)
- **Boolean flags enter models as 1.0 or 0.0, with NULL kept** as
  missing. Strings and dates stay out. `sector` enters as 11 fixed
  indicator columns, with the caveat that it holds today's value; the
  other classification columns are refused, because `scalemarketcap`
  would carry today's size into a firm's past. (17, 31.)
- **A universe applies everywhere a model is used.** A run inside a
  universe is its own ledger cell and is never compared with a run over
  all rows. The universe applies to training, testing, deployment and
  inference alike, and a backtest refuses a bundle trained inside a
  universe unless it filters on the same columns. A holdout look inside
  a universe uses up the whole label's cell. (15, 25.1.)

## The candidate and paper trading

- **The candidate** is a forest trained on cell C, the label "not a
  loser" (`fwd_3y_cagr >= 0 & fwd_3y_max_drawdown_from_entry < 0.3`),
  combined by mean rank with 12-month momentum and return on capital.
  The portfolio buys the ten highest-ranked stocks each month, at most
  two per sector, with equal weights, inside the floor
  `dollar_volume_3m_rank >= 0.2`. All three legs were refit on
  `dataset_v1.4.1`. (24, 25.2, 55, 77.2.)
- **The sector cap stays** as a safeguard, though it rarely binds now
  that return on capital is in the blend. (7, 25.3.)
- **Paper trading.** The fixed candidate is paper-traded as it is, in
  two portfolios: A, buy and hold, and B, the rank sell discipline
  (sell once a holding is outside the top 20% of the month's ranking).
  The runbook is [paper-trading.md](paper-trading.md). (21, 24, 36.)
- **E11 is a second portfolio, not a replacement.** After its three
  seeds on `dataset_v1.5.1`, E11 gets its own pick list beside the
  candidate's. The dry-run list of 2026-11-20 is not a commitment.
  Every pick list for a portfolio carries each pick's weight
  (`vml-predict --weighting`). (83.3, 85.4.)
- **The training cutoff is for deployment only.** `vml-train-deploy
  --train-end DATE` may be used in the deployment path, never in
  `vml-run`, `vml-eval` or a backtest. A ranking produced under a
  cutoff is not a performance claim. (60.)
- **A cap-weighted ten-stock book is a single-stock bet**, so the
  ten-stock candidate stays equal-weighted. Cap weighting works for a
  book of about 50 large caps (E11). (26, 81.)
- **Historical analogues are not estimates.** Their outcomes are
  in-sample for the deployment forest, and nothing `vml-analogues`
  produces may become a model input. (37.)

## Direction

- **The working assumption** is that 2021 to 2026 is a bubble led by
  stocks that fail a value investor's test. A value strategy trails
  through such a period, leads again during and after the correction,
  and should be waited out. It is an assumption, not a conclusion.
  (36, 83.4.)
- **The three remedies lead the plan**, in the order of the evidence
  behind them (81, 85.2):
  1. Put the model's loser-avoidance inside the index's cap-weighted
     structure. E11 is the first instance.
  2. Give the portfolio a reason to buy less when the market is dear:
     the market-state columns from upstream, or a valuation floor on
     each row tight enough to make the portfolio hold cash.
  3. Raise the picks' upside without raising their losers.
- **No threshold rule on model scores.** "Buy every stock above score
  X" buys most at market tops, because every forest's score level is
  highest there. This holds for any model built from the current
  inputs. `year_balance` and `year_calib_*` stay as reported numbers.
  (46, 81.3.)
- **The region search is open again.** A model is trained inside a
  region of the universe to see whether it separates the big winners
  there better than the same model does across the universe. Each
  region is tried two ways: as a `[[universe]]` (its own cell, read
  against in-region peers) and with `[emphasis]` (every row kept, the
  region's training weight multiplied, one file per factor). The picks
  are read on the control's outcomes: the lead over same-size peers,
  the share that lost money and the share that doubled, inside the
  region and against the control's picks. The regions and the
  predictions are written in a decision before any run. Carter's first
  region is stocks 30% or more below their one-year high
  (`dist_52w_high <= -0.3`). (85.3.)
- **Deep value.** Graham's measures (`ncav_to_marketcap`, tangible book
  value against market capitalization, the earnings yield) are tried as
  floors and as universes, with the forest's loser-avoidance as the
  gate and the five-year horizon as the outcome. Each experiment gets
  its own decision and predictions first. (83.5.)
- **Downside models are kept, as filters.** A downside model is judged
  by whether dropping its worst-scored stocks lowers another model's
  losers without cutting their lead. (43.1.)
- **If the forest is retrained anyway**, prefer `label_3y_cagr_ge_0`
  ("the stock came back"): it is equivalent to cell C in money and fits
  the thesis better. Do not swap it in on its own. (53.)
- **If work on fundamentals-based feature sets resumes**, start from the
  rank columns without the technical family plus the 28 unranked
  history columns (162 columns). It matched the control's lead with 5.6
  points more losers. (78.)

## How sessions work

- **Goal-directed sessions are the standing arrangement.** An agent may
  open new directions and build code on feature branches, provided
  every decision is logged before it is acted on and every run carries
  its prediction. It may promote results and build the results branch.
  A holdout look, a deployment and any merge into `Claude` stay
  Carter's. (27; [agents.md](agents.md).)
- **The records layout.** Decisions are logged in the dated decision
  log and summarized here; findings.md says what is known; next-steps.md
  says what to do next; TODO.md lists code still to build; agents.md is
  the agent's manual and setup.md is Carter's. (73.2, 86.)
- **Lab branches.** Created from `origin/Claude` with `vml-queue
  new-lab`, never from another lab branch, and archived with `vml-queue
  archive-lab --delete` once the session's results branch has merged.
  (68.)
- **One heavy job at a time.** A `dataset_v1.5.1` backtest peaks at up
  to 13.8 GB of the sandbox's 14 GB and runs with nothing else in
  memory. No unattended chain of v1.5.1 backtests runs until the
  backtest's memory use is cut. (68, 77.4.)
- **No writing-check machinery.** No program, hook, skill or denylist
  that checks prose, and no gate on commands. Write plainly. (66.)

## Open actions

One-time actions that are decided and not yet done. Each is removed
when done. The order of work and the first concrete step of each are
in [next-steps.md](next-steps.md).

- Run E11 on `dataset_v1.5.1` at three seeds, then produce its pick
  list beside the candidate's. (83.3.)
- Write the decision for a valuation floor tight enough to hold cash,
  with predictions, then run it. (85.2.)
- Write the decision for the region search, with the regions and the
  predictions, then run it. (85.3.)
- Write the decisions for the deep-value experiments. (83.5.)
- Cut the backtest's memory use. (77.4; TODO.md.)
- Finish the backtest realism audit: a cost model by size and era,
  taxes, market impact. None blocks current work. (83.2; TODO.md.)

## Waiting on Carter

- **The larger-half filter** (58). Adding `log_marketcap_rank >= 0.5` to
  the candidate's investability filter earned more on all three seeds
  (+0.59 points a year time-weighted, against a seed spread of 0.42)
  with a shallower drawdown. The gain comes from the size band, not
  from better selection. If confirmed, the paper-trading list gains a
  second `--filter`.
- **The training cutoff** (60). Whether paper trading uses the deployed
  forest or one trained with a cutoff, and which date. The cutoff-2021
  November list differs from the deployed one in one pick of ten, the
  cutoff-2018 list in two.
- **The F50 portfolio** (71.1). Whether the portfolio of fallen stocks
  runs beside the candidate. It beat SPY before 2021 at three seeds by
  0.3 to 0.6 points of CAGR, with a drawdown of −58%, and is far behind
  the candidate.
- **A price floor** in the backtest's investability filter (71.3,
  73.3). It would change every backtest's universe.
- **Forward the upstream requests**: the Foamex price check (73.1), the
  market-state columns (46, 80.7) and the others listed in TODO.md,
  "Upstream requests".
- **Two rules for other model families** (36; research plan item 7):
  fold-internal median imputation with an is-missing indicator, for
  models that cannot take NULLs; and whether a learned transform
  (clusters, embeddings) is allowed when it is fitted on the fold's
  training rows and saved in the fold's bundle. Also whether PyTorch
  may join the dependencies.
- **The time-weighted return or the CAGR?** Found in the review of
  2026-11-27. Decision 72 made the CAGR the metric of record, and the
  portfolio rule of 85.1 judges on time-weighted return. Which one
  rules when they disagree?
- **Does the 2020 window still need challenging?** Decision 70.1 chose
  to judge the fallen-stock portfolios on years before 2021 and called
  that a risk to be challenged once the bubble question is answered.
  Decision 85.1 now judges every portfolio over 2005 to 2020 and does
  not repeat the caveat. Confirm that the caveat is retired, or keep it.

## Closed lines of research

Each line was closed on the evidence named. Reopening one needs a new
decision that says what has changed.

- **Parameter searches** for forests, LightGBM and XGBoost in cell C: no
  draw beat the reference forest. (12.)
- **Theory-led and fundamentals-only feature sets**: no set without the
  risk ranks matches the 112 ranks; they cost losers without gaining
  lead. Confirmed on `dataset_v1.5.1`. (13.1, 18, 78, 80.)
- **A training-time liquidity floor** changes nothing for the ranks
  forest. (13.1, 18.)
- **Selection by calibrated confidence**: an honest calibrator for a
  three-year label lags four years, and score levels track the market.
  (20, 22, 44, 46.)
- **The one-year "not a loser" cell**: the three-year forest picks
  better one year ahead. (22.)
- **A learned upside model** as a second leg. (21.4.)
- **More second rankings on 2005 to 2020**: the factors were fixed
  before the runs, and trying more on those years would be fitting
  them. (8, 23.)
- **`sector` as a model input**: same picks, same sectors, same
  precision. (31.)
- **Selection inside large caps**: no forest leads peers by more than
  return on capital alone, and "beat SPY" is not learned with size held
  fixed. (34.1.)
- **A short leg or crash model**: the 12-month volatility rank predicts
  a fall as well as the forest does. (39, 45.)
- **The huber regressor**, as a candidate or as a leg, and its blend
  with the forest. Its within-band skill among small stocks would need a
  hedge the engine does not have. (40, 49.)
- **Concentration and score weighting** (a monthly top 5, weights by
  score). (42, 56.)
- **The fallen-stock program** and its recovery label (doubling in
  three years), in every universe, at every depth tried and with deeper
  trees and LightGBM. Inside a fallen region the forest finds the stocks
  that fall least. Only an upstream change would reopen it. (61 to 71.)
- **The new columns of `dataset_v1.5.1`** (history, trend and 8-K event
  counts) and its market-relative labels: nothing beats the control.
  (75, 77.)
- **The rare region of decision 80** (40% or more below the five-year
  high, positive operating cash flow in 18 of 20 quarters): it is the
  market's recovery, and every selection that buys it loses more often.
  This closes that region only; the search for a better one is open
  (85.3). (80.)
- **The reversal forest** ("doubled without a crash" on the 112 ranks):
  a lead over stocks that lose, with 38% losers. If a short-horizon
  reversal model is ever wanted, it starts there. (80.6.)
- **Emphasis weights, subspace forests and column sub-sampling** do not
  change what a forest buys. (80.4.)
- **Inside the cap-weighted book**: cuts deeper than the top 50, and the
  forest alone without the blend (it buys utilities, REITs and staples).
  (81.8.)
- **The rank sell discipline on a cap-weighted book of 50**: it sold
  about 5,800 times and paid half the deposits in costs. It belongs to
  equal-weighted books. A looser selling band is a possible later test.
  (82.6.)
