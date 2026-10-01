# Logbook

One entry per sweep or run, newest first: what was done, what came out,
what was concluded, what follows. Read this first. Conclusions that
span entries are in [findings.md](findings.md); tables and reasoning
are in the note an entry links to ([notes/](notes/)).

An entry that says **not yet read** was written by the machine when the
sweep ended. Its numbers exist (summary linked) and nobody has drawn a
conclusion from them.

Entries are never edited after the fact except to replace a **not yet
read** stub; a correction is a new entry that names the old one.

<!-- entries -->

### 2026-10-01 · a stand-in for the candidate on 1999-2004: Carter's bubble reading (decision 35)
git `1d5b4ec` · [note](notes/2026-10-01-out-of-sample.md)
- **Did:** Carter read the 2021-26 shortfall as a temporary change in market behaviour, perhaps a bubble a value strategy sits out. Tested on the one earlier bubble in the data, on years nothing here was ever run on: no fold model exists before 2005, so a stand-in (lowest 12-month volatility, momentum and return on capital by mean rank; the candidate's rule otherwise), every pick read against SPY and against same-month, same-size candidates, 1999-2026. Columns and the price panel only; nothing fitted, no label, no ledger row. Predictions in the decision log before the run.
- **Got:** The stand-in tracks the candidate in 2005-2026 (same-size lead +0.020 / +0.055 / -0.016 against +0.046 / +0.059 / -0.016). Buys of 1999, first year: -0.027 a year against SPY (29% beat it), -0.147 against same-size peers. Buys of 2000-02, three years: +0.092 a year against SPY and +0.092 against same-size peers (2000 / 2001 / 2002: +0.103 / +0.088 / +0.084), 25% lost money against 44% of their peers. The buys of 1999 over three years: +0.082 and +0.071. Buys of 2003-04: no lead (-0.027, +0.015). In 1999 the smaller half of the investable stocks beat SPY by 51 points over a year and the largest 5% matched it; in 2021-23 the smaller half trailed by 33 points a year and the largest 5% by 6.5.
- **Concluded:** The pattern Carter describes happened once before in this data with this kind of selection, on six cohorts no choice was made on: a lag in the last year of the run-up, then three cohorts 9 points a year ahead of the index and of same-size stocks. Predictions 1 and 3 held, 2 on return and not on losers. Limited support: one precedent, a stand-in, well-known factors, and a different kind of run-up (small stocks then, a few index giants now); and it cannot say whether or when the buys of 2021-23 recover against SPY. Recorded in findings as the leading hypothesis for 2021-26, not a conclusion; decision 34 is unchanged.
- **Next:** Carter's choices are as before; the reading is a reason to paper-trade the fixed candidate and for the market-state features upstream.

### 2026-10-01 · session close 2026-10-01 (second session)
git `0234c06`
- **Did:** Promoted 11 results (the candidate to 2026-08-21: buy and hold, the sell discipline, fractional shares; the sector sweep; the three large-cap sweeps; four evaluations against same-size peers). Wrote docs/notes/2026-10-01-out-of-sample.md and 2026-10-01-large-caps.md, decisions 27 to 34, three process issues, rewrote docs/findings.md, the next steps in TODO.md and docs/agents.md (the queue loop and the goal-directed session, with Carter's leave). Built claude/results-2026-10-01b for the pull request: five code changes (vml-predict's selection; calendar years in backtest reports; the buys against same-size candidates in backtest reports; sector as a model input; the screen's peer column), docs, promoted results, the ledger shard.
- **Got:** 35 backtest configurations on dataset_v1.4, four of them valued to 2026-08-21. Cell C: 87 configurations on all rows, 38 inside the 100k floor, 14 inside large caps; one holdout look (Carter's). 506 tests pass on the merged code.
- **Concluded:** The candidate is not shown to beat SPY; the forest's precision and loser avoidance held out of sample; selection is read against same-size peers from here on; the search on these columns is closed for now (decision 34). The record for the next session: docs/findings.md ('Next session: start here'), the two notes, the decision log 27-34, TODO.md.
- **Next:** Carter: the pull request; what the portfolio is for and its yardstick; whether to paper-trade the fixed candidate; the upstream requests.

### 2026-10-01 · forest_largecap_cells_3y
9 runs · `dataset_v1.4` · 3 cells · git `cca9ca0` · [summary](../reports/sweeps/forest_largecap_cells_3y/forest_largecap_cells_3y_summary.md) · [note](notes/2026-10-01-large-caps.md)
- **Did:** Decision 32: is there a ranking that chooses well among large companies? Trained and measured inside log_marketcap_rank >= 0.8 (about 790 investable stocks a month; 3,167 test rows a year), read on the screen against same-size peers: the candidate's forest on three targets (C not a loser; S beat SPY; CS beat SPY without a 30% fall), three seeds (this sweep, 9 hashes); seven single-factor bars (baseline_factors_largecap_3y, 21); LightGBM regressions on the excess return (lgbm_regressor_largecap_excess_3y, 6). The rule was fixed before the runs: a lead of 0.02 over same-size peers in both halves on every seed, and 0.01 above the best single factor's. All at git 88572e1. Trials: C inside large caps 14, beat SPY 16, CS 10.
- **Got:** Lead over same-size peers, entries of 2005-12 / 2013-20. Forests: C +0.022 / +0.021, +0.023 / +0.025, +0.022 / +0.020 (p@20 0.78 against a base rate of 0.57; losers 0.16 against 0.30); S +0.033 / +0.008, +0.039 / +0.013, +0.037 / -0.001 (PR-AUC 0.48 against a base rate of 0.45); CS +0.003 to +0.006 / +0.027 to +0.034 (p@20 0.27 to 0.30 against a base rate of 0.35). Regression: huber +0.016 to +0.024 / -0.024 to -0.036; quantile 0.25 +0.028 to +0.031 / +0.016 to +0.020. Single factors: return on capital +0.039 / +0.030; conservative score +0.031 / +0.029; lowest volatility -0.011 / +0.020; gross profitability -0.017 / +0.040; revenue growth -0.010 / +0.017; momentum -0.033 / -0.033; earnings yield -0.052 / -0.031. The all-rows forest measured here: +0.030 / +0.028.
- **Concluded:** No arm passes. Forest C meets the first condition and is 0.5 to 1.7 points a year below return on capital alone. 'Beat SPY' is not learned with size held fixed, and a regression on the size of the excess return is worse. Every arm that leads does so by 2 to 4 points through low risk or one quality factor; the forest's contribution is fewer losers, not more return. Predictions: no arm passes, S without skill after 2013 and momentum and earnings yield negative held; missed: C's p@20 (0.78, predicted 0.85), CS (no skill at its own label), and 'no single factor leads by 0.02 in both halves' (two do, in-sample: return on capital alone trailed its peers by 3.4 points for the buys of 2021-23). Decision 34: no new model is backtested, nothing more is run on 2021-26, and the search on these columns is closed for now.
- **Next:** Carter: what the portfolio is for and its yardstick; the pull request; whether to paper-trade the fixed candidate; the upstream requests (TODO.md).

### 2026-10-01 · lgbm_regressor_largecap_excess_3y
6 runs · `dataset_v1.4` · `fwd_3y_excess_cagr` · git `cca9ca0` · [summary](../reports/sweeps/lgbm_regressor_largecap_excess_3y/lgbm_regressor_largecap_excess_3y_summary.md)
- **Did:** See forest_largecap_cells_3y: LightGBM on the continuous fwd_3y_excess_cagr (huber and quantile 0.25, three seeds), measured on label_3y_beat_spy inside large caps. 6 hashes, 96 fold rows.
- **Got:** In that entry.
- **Concluded:** In that entry.

### 2026-10-01 · baseline_factors_largecap_3y
21 runs · `dataset_v1.4` · 3 cells · git `cca9ca0` · [summary](../reports/sweeps/baseline_factors_largecap_3y/baseline_factors_largecap_3y_summary.md)
- **Did:** See forest_largecap_cells_3y: the seven single-factor bars for the same three cells inside log_marketcap_rank >= 0.8, read against same-size peers. 21 hashes, 336 fold rows.
- **Got:** In that entry.
- **Concluded:** In that entry.

### 2026-10-01 · the candidate's bundles against same-size peers (vml-eval *_peers_dv100k, *_large) and the candidate's reports re-run with reference tables
git `cca9ca0` · [note](notes/2026-10-01-large-caps.md)
- **Did:** Built the same-size reference into the screen (claude/screen-size-peers: [pick_screen] peer_column, decision 33) and into the backtest report (claude/backtest-universe-outcomes: every candidate of every rebalance read as the buys are, vs_candidates and vs_peers). Evaluated the candidate's seed-23 bundle and its three blends inside the 100k floor and inside log_marketcap_rank >= 0.8 with the peer column (8 hashes), the six bundles of the sector sweep inside the 100k floor (6 hashes), and re-ran three of the candidate's backtests to 2026 for their reference tables (same config hashes, figures reproduced to the cent). Cell C: 38 configurations inside the 100k floor, 4 inside large caps before the sweeps.
- **Got:** Screen lead over same-size peers, entries of 2005-12 / 2013-20, inside the 100k floor: forest alone +0.030 / +0.027 (precision 0.71 / 0.83 against the peers' 0.53 / 0.60; losers 0.20 / 0.12 against 0.33 / 0.26); with return on capital +0.021 / +0.058; with momentum +0.018 / +0.019; all three +0.022 / +0.053. Against all rows the same screens lead by 0.058 to 0.135. Inside large caps: +0.030 / +0.028, +0.022 / +0.047, +0.015 / +0.023, +0.038 / +0.047. Backtest report, buy and hold, vs_peers over three years by buy year: positive in 14 of the 16 cohorts of 2005-2020 (+4.7 points pooled over all buys), -0.9 / -0.4 / -5.0 for 2021 / 2022 / 2023; with fractional shares -3.4 / +1.1 / -3.0, equal to the scratch diagnostic. The report's yearly table now prints calendar years (2021-26: -8.6 / +3.2 / -2.9 / -12.5 / -14.4 / -12.7).
- **Concluded:** Decision 33's predictions held: the screen, the scratch diagnostic and the backtest report agree on the candidate's lead over same-size stocks (2 to 6 points a year for 2005-2020, about zero after), and more than half of every lead over all rows was size. The forest's precision on its label survives the comparison (0.71 / 0.83 against 0.53 / 0.60 for same-size rows).
- **Next:** The large-cap sweeps (decision 32).

### 2026-10-01 · forest_sector_nonloser_3y
6 runs · `dataset_v1.4` · `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` · git `74c5637` · [summary](../reports/sweeps/forest_sector_nonloser_3y/forest_sector_nonloser_3y_summary.md) · [note](notes/2026-09-29-decisions.md)
- **Did:** Carter's question of 2026-10-01 (decisions 25.3 and 31): sector as a model input (claude/sector-feature: eleven 0/1 indicators against a fixed vocabulary, NULL kept; the other classification columns refused). Cell C, the candidate's forest, three seeds, the 112 ranks (fs0) against the ranks with sector (fs1, 123 model inputs), on every row, read on the portfolio screen. 6 hashes, 96 fold rows; cell C has 87 configurations on all rows (the count in the last run's report). Runs at git 9710e80 to f3eba2c (commits of docs and configs made while the sweep ran; the code is that of ad52395).
- **Got:** fs0 reproduces the candidate's forest on each seed (p@20 0.788 / 0.778 / 0.781, fold-mean PR-AUC 0.585). fs1: p@20 0.766 / 0.756 / 0.772, PR-AUC 0.585 on every seed. Screen, fs1 against fs0: precision 0.764 / 0.762 / 0.747 against 0.766 / 0.759 / 0.758; mean excess CAGR +0.003 / +0.003 / +0.002 against -0.000 / +0.004 / +0.004; losers 0.169 / 0.158 / 0.167 against 0.164 / 0.163 / 0.167. Utilities and real estate: 0.342 / 0.341 / 0.342 of fs1's screen picks, 0.348 / 0.350 / 0.342 of fs0's (0.088 of the test rows). The eleven sector indicators carry 0.9% of fs1's importance on each seed, real estate and utilities the two largest.
- **Concluded:** All five predictions held and Carter's rival is not supported: the forest with the sector in view picks the same stocks from the same two sectors, at the same precision and the same return. Its sector habit comes from the target (calm stocks did not lose), not from being unable to tell a REIT from an operating company. sector stays available as an input and out of the candidate's forest; the cap and return on capital remain what moves the picks.
- **Next:** Decisions 32 and 33: selection inside large caps, read against same-size peers.

### 2026-10-01 · bt_nonloser_mom_roc_top10_cap2_rankfloor_{to2026,sell20_to2026,frac_to2026,sell20_frac_to2026} (vml-backtest) and the diagnostics of decision 30
git `bd20cc5` · [note](notes/2026-10-01-out-of-sample.md)
- **Did:** Traded the fixed candidate (decision 24, with the rank floor Carter chose) and its sell-discipline variant to the end of the price panel, 2026-08-21, with year-end refits of the forest for 2021-26: the first backtests valued past 2023-12-29 (decision 28; backtests 32 and 33). Then, because buy and hold ended behind SPY: both again with fractional shares (34, 35), and a diagnostic outside the ledger that reads every pick of every combination of the three legs and every investable candidate of every month on the report's per-buy convention (decision 30). 35 backtest configurations on dataset_v1.4. The buy-and-hold path to the end of 2020 equals backtest 27's to the cent.
- **Got:** On 260,000 deposited: SPY 1,326,084 (10.93% time-weighted, -52.9%); buy and hold 1,193,902 (11.31%, -41.4%); sell discipline 1,344,630 (11.99%, -39.6%); fractional shares 1,172,560 and 1,329,280. Calendar years against SPY, buy and hold, 2021 to 2026: -8.6 / +3.2 / -2.9 / -12.5 / -14.4 / -12.7 (sell: -8.2 / +0.6 / -7.9 / -9.1 / -12.4 / -9.3). The buys of 2021 / 2022 / 2023 over three years: -0.116 / -0.109 / -0.169 a year against SPY, 41% / 32% / 38% lost money (2005-2020: +0.025, 20%). The average investable stock: -0.057 / -0.111 / -0.218 a year against SPY for 2005-12 / 2013-20 / 2021-23 cohorts; the largest 5% +0.002 / -0.025 / -0.065. The candidate's picks minus same-month, same-size candidates: +0.046 / +0.059 / -0.016; the forest alone +0.023 / +0.027 / +0.006, with 22% of its 2021-23 picks losing money against 34% of their peers.
- **Concluded:** The candidate is not shown to beat SPY: 37% ahead in money at the end of 2020, 10% behind in August 2026, over 21.6 years the index's return with three quarters of its worst drawdown. Not the whole-share rule. SPY outran equal-weighted stocks of every size in 2021-26 (the era, condition 2 of the thesis), and against stocks of their own size the candidate's lead of 2005-2020 was gone for the 2021-23 buys (the blend's increment over the forest reversed), while the forest kept avoiding losers. Most of every earlier 'lead over the average stock' was a preference for large companies. Predictions: 2021-23 years and the 2024 sign held; 2025, 2026, the final value and the cohorts' losers missed; the fractional-share predictions held. Found on the way: the reports' yearly table ran December to December (fixed, claude/backtest-calendar-years).
- **Next:** Decision 32: selection inside large caps (log_marketcap_rank >= 0.8), three targets, forests, a regression reframe and single-factor bars; the sector sweep of decision 31 first.

### 2026-10-01 · the holdout look in cell C, read (final eval forest_nonloser_dd30_3y, Carter)
git `bd20cc5` · [note](notes/2026-09-29-decisions.md)
- **Did:** Carter took the one sealed look in cell C's 3y cell on the host (look 1 of 1; run b6707d087996, config hash 419b84929382132f, git 62e021d; the walk-forward config unchanged, 47,012 test rows of 2021-2023). Read here from reports/final_eval/forest_nonloser_dd30_3y.md only (decision 29); no holdout row was read in the sandbox. The report has no baselines for the holdout scheme.
- **Got:** Top 20 a year: precision 0.75 / 0.65 / 0.55 for 2021 / 2022 / 2023, 0.65 pooled per year, against a base rate of 0.379 (walk-forward: 0.79 against 0.39). Top 50: 0.727. PR-AUC 0.564 (walk-forward fold mean 0.585); Brier ahead of the no-skill reference in all three years. The top 20: 28% lost money over three years (all rows 54%), 5% fell 40% from entry (53%), mean CAGR +0.050 (-0.103), mean excess CAGR -0.092 (-0.251), none compounded at 25%.
- **Concluded:** The forest predicts 'not a loser' on snapshots it was not chosen on at about the precision the thesis names, weaker at the very top than on walk-forward (inside the range of its last two walk-forward years). Its picks avoided the losers and trailed SPY by 9 points a year where the average row trailed by 25. The look tests the forest, not the blend. It stands as the cell's one look.
- **Next:** Trade the fixed candidate to the end of the price panel (decision 28).

### 2026-10-01 · session close 2026-10-01
git `af06d45`
- **Did:** Promoted 20 results (the candidate's backtests and its variants, the quality blend's, the feature-set, floor and bar sweeps, the 1-year cell, the calibrated run after the fix, four blend evaluations; two earlier backtests re-promoted with the per-buy table). Wrote docs/notes/2026-10-01-candidate.md (what the candidate is, its evidence, how to reproduce and run it), rewrote the next steps in TODO.md and the start of docs/findings.md. Built claude/results-2026-10-01 for the pull request: seven code changes, docs, promoted results, the ledger shard.
- **Got:** 31 backtest configurations on dataset_v1.4; cell C: 80 configurations on all rows, 23 inside the 100k floor, 15 inside 1m; the 1-year cell 6. 486 tests pass; scripts/check_tracked_configs.py reports nothing on the results branch.
- **Concluded:** The record for the next session is docs/findings.md ('Next session: start here'), docs/notes/2026-10-01-candidate.md, the decision log 14-26 and TODO.md. The lab branch claude/lab-2026-09-30 keeps every config and report; the results branch carries only what the tracked-configs check allows.
- **Next:** Carter: the pull request; a holdout look in cell C's 3y cell; the floor to deploy with; paper trading.

### 2026-10-01 · bt_nonloser_mom_roc_top10_cap2_{to2023,sell20_to2023,mcap,mcap_s232,mcap_s1776}, _rankfloor (vml-backtest)
git `8e0cdcd` · [note](notes/2026-09-29-decisions.md)
- **Did:** Carter's instructions and questions of 2026-10-01 (decision 26): the candidate trading on through 2023 with year-end refits, with and without the sell discipline; a capitalization-weighted variant (new `weighting = "marketcap"`, claude/backtest-marketcap-weighting) on three seeds; and the rank-floor check. 31 backtest configurations on dataset_v1.4.
- **Got:** Through 2023: 985,668 on 228,000 (SPY 774,140), 12.21%, -41.2%; 2021 -9.6, 2022 +4.3, 2023 -2.2 against SPY; the 2021 buys -15 points a year over their first year (77% lost money), 2022's -2.8. With sells: 1,054,924, 12.70%. Cap-weighted: 1,108,044 / 1,161,451 / 1,090,347, 13.8-14.4%, drawdown -37 to -39%, with 46% of the final portfolio in AAPL and 5.2 buys a month.
- **Concluded:** The refits and new buys change the path by under 0.3 points a year; the 2021 cohort is the worst one-year cohort of the sample, of a kind with 2006 and 2020, and is the first evidence from years the candidate was not chosen on. Capitalization weighting is a single-stock bet (prediction missed upwards on return and on drawdown); equal weights stay. The rank floor leaves the candidate unchanged.
- **Next:** Carter: the holdout look; the pull request from claude/backtest-marketcap-weighting (all seven branches); paper trading.

### 2026-10-01 · bt_nonloser_mom_roc_top10_cap2_rankfloor (vml-backtest); vml-predict applies the universe
git `204b348` · [note](notes/2026-09-29-decisions.md)
- **Did:** Carter's questions of 2026-10-01 (decision 25): made vml-predict rank only the inference rows inside a bundle's universe (claude/predict-universe, 485 tests), and ran the candidate with a within-quarter rank floor (dollar_volume_3m_rank >= 0.2) in place of the 100,000 dollar floor: the 27th backtest configuration on these years, a sensitivity check.
- **Got:** 965,380 against 948,956; time-weighted 12.15% against 12.24%; drawdown -41.4% against -41.2%; per buy +0.026 against +0.025; 3,237 candidates a month against 3,153.
- **Concluded:** As predicted (within a point and 10%): the candidate does not depend on the form of its floor. A rank floor is one config line and needs nothing upstream. The REIT cohorts of the forest-alone backtest, read per buy: 2005's REITs beat SPY by 0.055 a year over three years and 0.075 over seven; 2006's lost 0.119 a year over three and 0.030 over seven; sector as a model input is proposed in TODO.
- **Next:** Carter: which floor to deploy with; the pull request from claude/predict-universe.

### 2026-09-30 · backtests 14 to 26: the quality blend, the three-way blend, a rank sell discipline (vml-backtest)
git `0b8c053` · [note](notes/2026-09-30-backtests.md)
- **Did:** Built per-buy outcomes into the backtest report (claude/backtest-buy-outcomes) and a rank sell criterion (claude/backtest-rank-sell). Re-ran the eight capped backtests for the per-buy table (same hashes, figures reproduced to the cent). Thirteen new configurations under decision 6's template with the cap, judged on four criteria fixed beforehand (decision 21): the quality blend (forest + return on capital) on two more seeds; forest + momentum + return on capital on three seeds, with fractional shares and with a sell discipline on three seeds; the sell discipline on the quality blend (three seeds) and on the momentum blend. 26 backtest configurations tried on dataset_v1.4 in all.
- **Got:** SPY 732,110 / 9.58% time-weighted / -52.9%. Three-way blend, seeds 23 / 232 / 1776: 948,956 / 959,660 / 949,366; 12.24 / 12.26 / 12.23%; -41.2 / -41.3 / -42.0%; per buy over three years +0.025 / +0.026 / +0.024 a year over SPY (+0.034 for buys of 2005-12, +0.013 to +0.016 for 2013-20); fractional shares 936,540, 12.12%. With the sell discipline 1,090,591 / 1,042,252 / 1,028,085, 13.14 / 12.70 / 12.66%, costs 4 times. Quality blend 694,945 / 752,267 / 721,826, 9.65 / 10.18 / 10.04%, -41 to -42%, per buy +0.012 to +0.019; with the sell discipline 800,456 / 852,325 / 803,800, 10.64 / 11.09 / 10.79%. Momentum blend with the sell discipline: 674,817, 9.87%, -51.7%, costs 8.5 times.
- **Concluded:** Forest, momentum and return on capital by mean rank meets all four criteria on all three seeds and is the candidate (decision 24); the quality blend meets them with the sell discipline. The old candidate (forest + momentum) meets two: its lead was time-weighted and sat in 2005-11, and per buy it is negative for 2013-20. A rank sell discipline adds 0.4 to 1.0 points a year where the rank is stable and costs 1.2 where it is not. Predictions: ten matched; the three-way blend was predicted between its parents and came out above both, and its sell variant was predicted below buy and hold and came out above, so both were seed-checked before being read. Best of 26 on sixteen years: not shown to hold outside 2005-2023. No further backtest is run on these years.
- **Next:** Carter: a holdout look in cell C's 3y cell with the candidate's forest; pull requests for the five feature branches; whether the engine may trade 2021-23 for the candidate; paper trading. Proposed: a position cap; the upstream label request for delistings.

### 2026-09-30 · baseline_factors_nonloser_1y_dv100k
5 runs · `dataset_v1.4` · `fwd_1y_cagr >= 0.0 & fwd_1y_max_drawdown_from_entry < 0.2` · git `ba55f7d` · [summary](../reports/sweeps/baseline_factors_nonloser_1y_dv100k/baseline_factors_nonloser_1y_dv100k_summary.md) · [note](notes/2026-09-30-one-year-cell.md)
- **Did:** A one-year 'not a loser' cell (decision 22): fwd_1y_cagr >= 0 & fwd_1y_max_drawdown_from_entry < 0.2, folds 2005-2020, inside the 100k floor. Five single factors (this sweep), the candidate's forest configuration trained on the 1-year label with lagged isotonic calibration (forest_nonloser_dd20_1y, vml-run), and cell C's 3-year forest read on the same 1-year outcomes (vml-eval). Six configurations, the cell's first.
- **Got:** Screen, 1-year outcomes, losers / mean excess: 3-year forest 0.236 / +0.008; 1-year forest 0.275 / -0.004 (p@20 0.666, base 0.458); lowest volatility 0.250 / -0.024; conservative score 0.325 / +0.006. The 1-year forest's p@20 is 0.15, 0.05 and 0.05 for 2007, 2008 and 2019 entries. Rows at a calibrated 0.5 or more have a precision of 0.10 (2008) to 0.84 (2012) by year; none reaches 0.7 after 2008; calibrated Brier 0.248 against a no-skill 0.222.
- **Concluded:** The 3-year forest picks better for one year ahead than a forest trained on one year ahead, and the fresher label sees a crash no sooner. Predictions: the screen levels matched; p@20 (0.70-0.80 predicted), the two models being within 0.02 of each other, and momentum looking better at one year all missed; the rival (the 1-year model better in crash entries) is not supported. Neither condition of decision 22 holds: the 1-year cell is closed.
- **Next:** The seed and fractional-share checks of the two blends that met decision 21's criteria (decision 23).

### 2026-09-30 · forest_nonloser_dd30_isotonic_3y, forest_nonloser_dd30_isotonic_lag_3y (vml-run): calibration
git `e2c2e4a` · [note](notes/2026-09-30-blends-and-calibration.md)
- **Did:** Ran the candidate's forest with prequential isotonic calibration to read selection by confidence (decision 20). The first run contradicted its first prediction (p@20 0.650, predicted the uncalibrated 0.788), which exposed two defects in harness/calibration.py: each fold was calibrated on outcomes not yet known at its dates (every earlier fold, where a 3-year label is known three years late), and isotonic steps tied the top of the ranking. Fixed on claude/calibration-label-lag (fold Y uses folds up to Y-4 for a 3-year label; rows on a step keep their raw order; 481 tests), and ran again under a new name. One earlier calibrated run exists (host ledger, 2026-09-25); its row in the derived-label note carries a dated correction.
- **Got:** After the fix: p@20 0.7875 and PR-AUC 0.585, the uncalibrated run's. Folds 2005-08 raw, 2009-20 calibrated. Rows at a calibrated 0.5 or more: none in 2011-13 (top 20 right 95-100% of the time), 42-44% of all rows in 2017-19 at a precision of 0.31-0.48; no row reaches 0.7 after 2008. Brier 0.2266 calibrated, 0.2148 raw, 0.2200 no-skill.
- **Concluded:** An honest calibrator for a 3-year label is four years behind and follows the regime of four years before; an absolute confidence bar, calibrated or not, would have held cash through the best entry years and bought broadly before the worst. Selection stays by rank within the period for this label. The first run is not to be read. Predictions of the second run: ranking kept, held; the threshold predictions could not be tested as written (no row at 0.7 or 0.8 after 2008).
- **Next:** A 1-year cell, whose calibrator lags two folds (decision 22).

### 2026-09-30 · second rankings on the screen: blend evaluations (vml-eval), forest_winner15_fs4_dv100k_3y, factor_net_payout_yield_3y (vml-run)
git `e2c2e4a` · [note](notes/2026-09-30-blends-and-calibration.md)
- **Did:** Built blend in vml-eval (claude/eval-blend): two or three bundles as one ranking by mean rank within the test quarter. Checked the screen against the three blends whose backtests exist (decision 19), then read four new blends named beforehand. All inside the 100k floor, cell C's forest seed 23, screen top 10 per quarter, at most 2 per sector. 8 evaluation hashes and 2 new bundles; cell C has 80 configurations on all rows and 23 inside 100k.
- **Got:** Screen mean excess CAGR / losers: forest alone -0.001 / 0.156; with momentum -0.018 / 0.244; with return on capital +0.014 / 0.162; with earnings yield -0.030 / 0.283; momentum + net payout -0.010 / 0.262; momentum + return on capital +0.006 / 0.214; with a learned upside forest -0.031 / 0.256; momentum + upside -0.037 / 0.294. Return on capital is +0.016 for 2005-12 entries and +0.011 for 2013-20; every other blend is negative after 2013. The upside forest (fwd_3y_cagr >= 0.15) has p@20 0.29 against a base rate of 0.27.
- **Concluded:** The check failed as written: momentum was predicted 0.01 above the forest alone and is 0.017 below (return on capital 0.015 above, predicted within 0.01; earnings yield held). The backtests' own buys, read one by one over three years from the price panel, side with the screen on the order: per buy +0.001 forest alone, +0.005 momentum, +0.013 return on capital (+0.013 and +0.012 in the two halves), -0.032 earnings yield. Momentum's lead was a time-weighted figure from 2005-11. About a third of the screen's momentum gap is the label convention: 15% of its picks were acquired in the window and are carried flat. The upside model has no skill and is dropped. By decision 19's rule the screen alone does not choose second rankings.
- **Next:** Decision 21: per-buy outcomes in every backtest report; five backtests (the quality blend on two more seeds, forest + momentum + return on capital, a rank sell discipline on the quality blend and on the candidate).

### 2026-09-30 · forest_features_nonloser_dv1m_3y
5 runs · `dataset_v1.4` · `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` · git `1f0f79b` · [summary](../reports/sweeps/forest_features_nonloser_dv1m_3y/forest_features_nonloser_dv1m_3y_summary.md) · [note](notes/2026-09-30-features-and-floor.md)
- **Did:** See forest_features_nonloser_dv100k_3y: the same five sets trained inside the 1m floor.
- **Got:** In that entry.
- **Concluded:** In that entry.

### 2026-09-30 · forest_features_nonloser_dv100k_3y
5 runs · `dataset_v1.4` · `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` · git `1f0f79b` · [summary](../reports/sweeps/forest_features_nonloser_dv100k_3y/forest_features_nonloser_dv100k_3y_summary.md) · [note](notes/2026-09-30-features-and-floor.md)
- **Did:** The same five feature sets trained inside the 100k floor (and, in forest_features_nonloser_dv1m_3y, inside the 1m floor): the training-time liquidity floor of decision 13.1. Reference: the all-rows bundles measured inside the same floor. 10 hashes, 160 fold rows.
- **Got:** fs0 trained inside against trained on all rows, measured inside the floor: 100k p@20 0.769 / 0.784, PR-AUC 0.601 / 0.602, screen precision 0.753 / 0.766, screen mean excess -0.003 / -0.001; 1m 0.788 / 0.797, 0.615 / 0.618, 0.755 / 0.778, -0.002 / +0.002. Sets without risk ranks: at 1m the floor moves p@20 by +0.003 to +0.056 and mean excess by +0.004 to +0.013; at 100k by -0.031 to +0.012 and -0.004 to +0.005. No arm's screen mean excess is above fs0's in any universe.
- **Concluded:** The floor changes nothing for the ranks forest, as predicted (the rival, PR-AUC up 0.01 inside the floor, is not supported: -0.001 and -0.003). That it helps the fundamentals sets by 0.02 on p@20 held in one of four comparisons. Features and the floor are not where the upside is in cell C: the candidate's model stays the ranks forest trained on every row, the floor stays in the backtest and the screen. Trials: cell C 77 on all rows, 16 inside 100k, 15 inside 1m.
- **Next:** Decision 19: second rankings blended with the forest on the screen, first checked against the three blends whose backtests exist.

### 2026-09-30 · forest_features_nonloser_allrows_3y
5 runs · `dataset_v1.4` · `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` · git `1f0f79b` · [summary](../reports/sweeps/forest_features_nonloser_allrows_3y/forest_features_nonloser_allrows_3y_summary.md) · [note](notes/2026-09-30-features-and-floor.md)
- **Did:** Five feature sets in cell C on every row, the candidate's forest, seed 23 (decision 18): the ranks (fs0), ranks without technical (fs1), fs1 plus the 47 unranked scores, shares and flags (fs2, the theory-led set), ranks without the eight risk and liquidity ranks (fs3), fs3 plus the 47 (fs4). Bundles saved and each evaluated inside the 100k and the 1m floor with vml-eval. 15 hashes, 240 fold rows; fs0 reproduces the candidate (p@20 0.788, PR-AUC 0.585).
- **Got:** All rows, p@20 / screen precision / screen mean excess CAGR / losers: fs0 0.788 / 0.766 / -0.000 / 0.164; fs1 0.659 / 0.619 / -0.028 / 0.248; fs2 0.672 / 0.641 / -0.023 / 0.231; fs3 0.644 / 0.656 / -0.031 / 0.238; fs4 0.666 / 0.661 / -0.031 / 0.234. Inside the floors the same to within 0.01. 2013-20 entries: fs0 mean excess -0.019, the others -0.054 to -0.066 with picks beating SPY 0.28-0.32 of the time. Utilities and real estate are 35-39% of the screen's picks in every arm.
- **Concluded:** No set passes decision 16's rule; the theory-led sets pick worse on every outcome and pick the same two sectors, ranking on the trend and consistency of operating cash flow once volatility is gone. Predictions: matched for fs0, fs1 and for no arm beating fs0 on the screen; missed for fs2 over fs1 by 0.02 (0.013, PR-AUC lower), for fs3 between fs1 and fs0 (below fs1) and for the sector shares (0.37-0.38 predicted under 0.20). One seed, one forest configuration tuned on the ranks.
- **Next:** The floor-trained arms (forest_features_nonloser_dv100k_3y, dv1m).

### 2026-09-30 · baseline_factors_nonloser_dv1m_3y
5 runs · `dataset_v1.4` · `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` · git `1f0f79b` · [summary](../reports/sweeps/baseline_factors_nonloser_dv1m_3y/baseline_factors_nonloser_dv1m_3y_summary.md) · [note](notes/2026-09-30-features-and-floor.md)
- **Did:** See baseline_factors_nonloser_dv100k_3y: the same five factors inside the 1m floor.
- **Got:** In that entry.
- **Concluded:** In that entry.

### 2026-09-30 · baseline_factors_nonloser_dv100k_3y
5 runs · `dataset_v1.4` · `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` · git `1f0f79b` · [summary](../reports/sweeps/baseline_factors_nonloser_dv100k_3y/baseline_factors_nonloser_dv100k_3y_summary.md) · [note](notes/2026-09-30-features-and-floor.md)
- **Did:** Single-factor bars for cell C inside the 100k floor (and, in baseline_factors_nonloser_dv1m_3y, inside the 1m floor), with the new portfolio screen: top 10 per test quarter, at most 2 per sector. Five factors each, deterministic; 10 hashes, 160 fold rows.
- **Got:** Screen inside 100k, precision / losers / mean excess CAGR: conservative score 0.62 / 0.245 / -0.006; lowest 36-month volatility 0.74 / 0.167 / -0.025; return on capital 0.52 / 0.347 / -0.052; momentum 0.21 / 0.658 / -0.238; earnings yield 0.25 / 0.573 / -0.200. Inside 1m the same order (conservative 0.63 / 0.241 / -0.002). All test rows inside 100k: losers 0.423, mean excess -0.089.
- **Concluded:** As expected: the order of the factors is the all-rows order and every factor has fewer losers than on all rows. The conservative score matches the forest's mean excess with more losers and twice the big winners; lowest volatility has the forest's losers and 0.024 less return.
- **Next:** forest_features_nonloser_allrows_3y.

### 2026-09-29 · session close 2026-09-30
git `685c75e`
- **Did:** Promoted the candidate's forest run, the four sweeps behind it (feature sets, label rungs, pick anatomy, single-factor bars), the three searches in cell C and three backtests (uncapped, capped, capped with momentum). Recorded Carter's closing notes as decision 13 and as the next steps in TODO.md. Built the results branch for the pull request.
- **Got:** 13 promoted directories added under reports/promoted/. 13 backtest configurations and 72 walk-forward configurations in cell C in the sandbox shard.
- **Concluded:** The record for the next session is docs/findings.md ('Next session: start here'), the decision log, and TODO.md. Lab branch claude/lab-2026-09-28 keeps every config and report; the results branch carries only what the tracked-configs check allows.
- **Next:** Carter: the pull request; a holdout look in cell C when he would act on the candidate.

### 2026-09-29 · xgb_random_search_nonloser_3y
20 runs · `dataset_v1.4` · `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` · git `7e4ca71` · [summary](../reports/sweeps/xgb_random_search_nonloser_3y/xgb_random_search_nonloser_3y_summary.md) · [note](notes/2026-09-29-searches-nonloser.md)
- **Did:** Random search over XGBoost parameters in cell C on CPU, 20 draws, one seed, the 112 ranks, with pick outcomes. 20 hashes, 320 fold rows.
- **Got:** Fold-mean PR-AUC 0.567–0.581. p@20 0.63–0.75. Picks' losers 0.16–0.24, picks beat SPY 0.27–0.40, median excess CAGR −0.07 to −0.02. Brier beats the no-skill reference in 2 to 10 of 16 years (forest draws: 10–11).
- **Concluded:** XGBoost lands where LightGBM lands, as predicted (best draws 0.581 and 0.581), and below the forest. The best draws are not the shallow ones (depths 5, 7, 3, 9, 6; predicted 3–5). Across the three searches no draw exceeds the reference forest, so the candidate's model stays. Inside the boosted families PR-AUC and p@20 order the draws in opposite directions.
- **Next:** The queue is empty. The candidate (decision 10) waits for Carter: holdout look, promotion, pull request for the sector cap. Proposed in the decision log: a sell discipline and a 1y horizon, not run.

### 2026-09-29 · lgbm_random_search_nonloser_3y
20 runs · `dataset_v1.4` · `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` · git `7e4ca71` · [summary](../reports/sweeps/lgbm_random_search_nonloser_3y/lgbm_random_search_nonloser_3y_summary.md) · [note](notes/2026-09-29-searches-nonloser.md)
- **Did:** Random search over LightGBM parameters in cell C, 20 draws, one seed, the 112 ranks, with pick outcomes. 20 hashes, 320 fold rows.
- **Got:** Fold-mean PR-AUC 0.566–0.581 (reference forest 0.585). p@20 0.64–0.75 (forest 0.78–0.79). Picks' losers 0.15–0.25, picks beat SPY 0.25–0.36, median excess CAGR −0.07 to −0.03 (forest: 0.13, 0.46, about zero). The most boosted draws have the lowest PR-AUC and the highest p@20.
- **Concluded:** LightGBM does not reach the forest on PR-AUC and its picks are worse on every outcome; no draw goes further. Predictions: best draw in 0.565–0.590 matched; no draw with fewer losers than the forest matched; a span of 0.03 or more missed (0.015).
- **Next:** Read with xgb_random_search_nonloser_3y.

### 2026-09-29 · forest_random_search_nonloser_3y
20 runs · `dataset_v1.4` · `fwd_3y_cagr >= 0.0 & fwd_3y_max_drawdown_from_entry < 0.3` · git `fd131d3` · [summary](../reports/sweeps/forest_random_search_nonloser_3y/forest_random_search_nonloser_3y_summary.md)
- **Did:** Random search over forest parameters in cell C ('not a loser'), 20 draws, one seed, the 112 ranks, with pick outcomes (decision 11). 20 hashes, 320 fold rows in the shard. Read on fold-mean PR-AUC from the ledger.
- **Got:** Fold-mean PR-AUC 0.5806 to 0.5853 over the 20 draws; the reference forest has 0.585. p@20 0.72–0.78 (reference 0.78–0.79), 2013–20 0.77–0.84. Picks' losers 0.12–0.20, big winners 0.03–0.08, median drawdown 0.13–0.19. The six highest PR-AUCs include five of the seven entropy draws; the six lowest are all gini. Depth 3 to 12 appears at both ends.
- **Concluded:** No draw exceeds the reference, so none goes to three seeds or to a backtest: the candidate's forest stays as it is. Predictions: matched that the draws land within 0.010 of 0.585 (all 20, within 0.005) and none exceeds 0.600; missed on the picks' losers staying within 0.10–0.18 (three draws at 0.19–0.20); not supported that deep draws with small leaves are the lowest (criterion orders the draws, depth does not). Forest parameters are not where a better model is.
- **Next:** lgbm_random_search_nonloser_3y, then xgb_random_search_nonloser_3y.

### 2026-09-29 · bt_nonloser_{dd30,mom}_top10_cap2_s{232,1776} (vml-backtest); forest_nonloser_dd30_3y_s{232,1776} (vml-run)
git `6708518` · [note](notes/2026-09-29-factor-combinations.md)
- **Did:** Seed check (decision 9): cell C's forest on seeds 232 and 1776, and the forest alone and the forest with momentum backtested with each, cap 2. Thirteen backtest configurations tried on dataset_v1.4 in all.
- **Got:** Time-weighted CAGR, seeds 23 / 232 / 1776: forest alone 9.74 / 9.35 / 9.90%; with momentum 11.07 / 11.73 / 11.11%; SPY 9.58%. Worst drawdown −46.1 / −47.1 / −44.2% and −47.8 / −46.7 / −48.5%; SPY −52.9%. Final value with momentum 711,494 / 764,062 / 717,485; SPY 732,110. Forest p@20 0.788 / 0.778 / 0.781, fold-mean PR-AUC 0.585 on each.
- **Concluded:** As predicted: every figure within 0.7 points a year and 3 points of drawdown of seed 23, and the momentum portfolio leads the forest alone by 1.2 to 2.4 points a year on every seed. The seed moves a backtest by about half a point a year. The candidate is cell C's forest with momentum by mean rank, cap 2 per sector (decision 10). Not shown: that it holds outside 2005–2023; momentum was the best of three.
- **Next:** Carter's: holdout look, promotion, pull request for claude/backtest-sector-cap. Queue: parameter searches in cell C, 20 draws per family (decision 11).

### 2026-09-29 · bt_nonloser_{ey,mom,roc}_top10_cap2 (vml-backtest); factor_{earnings_yield,mom_12_2,roc_greenblatt}_3y (vml-run)
git `52f2ccd` · [note](notes/2026-09-29-factor-combinations.md)
- **Did:** Combined cell C's forest by mean rank with one single factor each, named before the runs: earnings yield (value), 12-month momentum, return on capital (quality). Template of decision 6 with a cap of 2 per sector. Nine backtest configurations tried on dataset_v1.4 in all. What would count was fixed beforehand: drawdown within 5 points of −46%, time-weighted CAGR of 10.7% or more, gain not confined to 2005–12.
- **Got:** Forest alone 633,757 / 9.74% time-weighted / −46.1% (SPY 732,110 / 9.58% / −52.9%). With momentum 711,494 / 11.07% / −47.8%. With quality 694,945 / 9.65% / −41.2%. With value 493,413 / 7.76% / −49.4%. Momentum's yearly excess over SPY sums to +44.8 points over 2005–12 and −9.8 over 2013–20 (forest alone +26.6 and −23.1). Alone on the screen, momentum's picks have 0.68 losers.
- **Concluded:** The forest with momentum meets all three criteria; quality meets the drawdown one and gives the shallowest drawdown so far; cheapness among calm stocks makes the portfolio worse. Momentum helps only among the stocks the forest ranks as safe. Predictions matched except quality's drawdown (4.9 points shallower, predicted within 3). Best of three and ninth of nine on one seed and one path: not carried forward until the seed check (decision 9) is read.
- **Next:** Decision 9: the forest alone and with momentum on seeds 232 and 1776.

### 2026-09-29 · bt_nonloser_dd30_top10_cap2, bt_cagr10_dd20_top10_cap2, bt_nonloser_dd30_top10_cap1 (vml-backtest)
git `499884b` · [note](notes/2026-09-29-sector-cap-backtests.md)
- **Did:** Built a sector cap at selection (max_per_group, branch claude/backtest-sector-cap, 458 tests pass) and a report of what was bought by sector. Re-ran the uncapped cell C backtest: same hash, same figures. Ran cell C with at most 2 and at most 1 buys per sector a month, and cell A with at most 2; the template is otherwise unchanged. Six backtest configurations tried on dataset_v1.4 in all.
- **Got:** Cell C, cap 2: final value 633,757 on 192,000 deposited (uncapped 518,612; SPY 732,110), time-weighted CAGR 9.74% (SPY 9.58%), money-weighted 10.4% (11.6%), worst drawdown −46.1% (uncapped −63.4%; SPY −52.9%). 2007 −4.5% and 2008 −29.8% (SPY +7.3% and −43.2%). Cap 1: 650,980, 9.69%, −42.8%. Cell A, cap 2: 605,182, 8.73%, −49.0%. Behind SPY by 9 points or more in 2007, 2013, 2020, 2021 and 2023; ahead in both of SPY's down years.
- **Concluded:** Sector concentration was the reason for the deep drawdown. Capped, the portfolio compounds at SPY's rate with a shallower drawdown and ends 11–13% below it in money, because its good years were early and most of the deposits were at work late. Less lost in falls, less gained in strong rises. Predictions matched except 2007 (11.8 and 14.4 points behind, predicted within 10) and cap 1's drawdown (better than predicted). In-sample to these sixteen years: the cap was chosen after the first three backtests.
- **Next:** Decision 8: cell C's forest combined by mean rank with a value, a momentum and a quality factor, cap 2.

### 2026-09-29 · bt_nonloser_dd30_top10, bt_cagr10_dd20_top10, bt_nonloser_and_cagr10_top10 (vml-backtest)
git `319144c` · [note](notes/2026-09-29-first-backtests.md)
- **Did:** Backtested cell C's forest, cell A's and the two by mean rank under one template fixed beforehand: top 10 a month, equal weights, buy and hold, 35 bps a side, dollar_volume_3m >= 100000, buys 2005–2020, valued end of 2023. Three backtest configurations on dataset_v1.4, all reported. Read the sectors of the buys from the dataset.
- **Got:** Final value on 192,000 deposited: 518,612 / 534,517 / 541,571 against SPY's 732,110 (money-weighted 8.7–9.1% against 11.6%). Worst drawdown −63% to −65% against −53%. 2007: −20.7% against +7.3%. Ahead of SPY in 10 of 19 years. Buys: utilities 0.49 and real estate 0.27 for cell C (0.03 and 0.06 of the universe); every buy of 2005 and 2006 a REIT.
- **Concluded:** Predictions missed: within 15% of SPY (29% below) and a shallower drawdown (deeper). The three portfolios are one portfolio, and the models are sector selectors: they rank on market-wide volatility ranks, so the calmest sectors fill the top. The screen's precision figures stand; 'distinct stocks' could not see that the picks were one sector. Costs are not the reason (1,442 in total).
- **Next:** Decision 7: a sector cap at selection, on claude/backtest-sector-cap; the three backtests again with it.

### 2026-09-29 · forest_nonloser_dd30_3y, forest_cagr10_dd20_3y (vml-run)
git `319144c` · [note](notes/2026-09-29-first-backtests.md)
- **Did:** Ran the 'not a loser' cell's forest and the primary cell's forest as regular configs so that their fold bundles are saved (decision 5). Seed 23, 112 rank columns, top_k up to 100 and score thresholds.
- **Got:** Cell C: p@20 0.7875, the sweep's seed-23 value; p@100 0.744. By score: 'score >= 0.8' selects 597 rows with a precision of 0.42, 'score >= 0.7' 9,763 rows with 0.53. The mean score of the top 20 is 0.81–0.85 for 2006–08 entries (precision 0.15–0.60) and 0.65–0.69 for 2011–13 (precision 0.95–1.0).
- **Concluded:** The score is highest in the years the model is most wrong, so a fixed score threshold selects the pre-crash years. Selection by a fixed score is not the route to higher precision with these models; top K per period is.
- **Next:** Backtests (decision 6).

### 2026-09-29 · forest_pick_anatomy_3y
18 runs · `dataset_v1.4` · 3 cells · git `320894b` · [summary](../reports/sweeps/forest_pick_anatomy_3y/forest_pick_anatomy_3y_summary.md) · [note](notes/2026-09-29-pick-anatomy.md)
- **Did:** One forest configuration, three seeds, in three cells (A primary; B excess CAGR above 0 with drawdown from entry under 0.2; C 'not a loser': CAGR of 0 or more with drawdown from entry under 0.3) × two feature sets (112 ranks; 97 without technical), with the tails of the picks' returns. 18 hashes, 288 fold rows; A with ranks reproduces the reference (p@20 0.500, PR-AUC 0.3267).
- **Got:** Top 20, ranks. A: losers 0.20, big losers 0.10, big winners 0.06 (all rows 0.45 / 0.32 / 0.15), beat SPY 0.50, median CAGR 0.088. C: p@20 0.782 (base 0.39; 2013–20 0.84; 0.83 or more in 11 of 16 years; under 0.60 for 2006–08 and 2019), losers 0.13, big losers 0.06, median drawdown 0.13, median CAGR 0.091, median excess +0.001, beat SPY 0.46. B: p@20 0.28 (base 0.20; 2013–20 0.18), beat SPY 0.38. Fundamentals only: beat SPY 0.63 for 2005–12 entries in A and 0.28 for 2013–20. p@5 0.51, p@10 0.51, p@50 0.48 in A.
- **Concluded:** Carter's reading holds: the picks have under half the losers and 40% of the big winners of the universe. The modest target is predicted with a precision of 0.78, and its picks match SPY on the median with a third of the average stock's drawdown; they beat it in and after market falls and lose to it in the long rise. A relative label makes the picks worse at beating the market. Predictions: 1, 5 and 6 matched; 2 on direction, not level (0.20, predicted under 0.15); 3 half (no pattern in big winners or losers); 4 missed (B 0.12 below A on beat SPY).
- **Next:** Carry cell C with ranks forward: vml-run bundle, selection by score, backtest against A's forest and the single factor. Separately, sweeps for the upside.

### 2026-09-29 · baseline_pick_anatomy_3y
4 runs · `dataset_v1.4` · `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2` · git `320894b` · [summary](../reports/sweeps/baseline_pick_anatomy_3y/baseline_pick_anatomy_3y_summary.md) · [note](notes/2026-09-29-pick-anatomy.md)
- **Did:** Four single factors in the primary cell with the tails of the picks' returns and top 5 / 10 / 20 / 50: highest conservative score, earnings yield, book to market, magic-formula score. Deterministic; 4 hashes, 64 fold rows in the shard.
- **Got:** Top 20, all years, against all test rows (losers 0.45, big losers 0.32, big winners 0.15, beat SPY 0.36). Conservative score: losers 0.27, big losers 0.12, big winners 0.13, beat SPY 0.49, median drawdown 0.26. The three value factors: losers 0.61–0.63, big losers 0.48–0.52, big winners 0.08–0.12, beat SPY 0.19–0.25, median excess CAGR −0.20 to −0.22.
- **Concluded:** The cheapest stocks are the worst picks on every measure, with fewer big winners than the universe (predicted: more). The conservative score halves the big losers and keeps most of the big winners; its losers are 0.60 of the all-row rate (predicted: under half). It fails for entry years 2017–20 (losers 0.35, beat SPY 0.20).
- **Next:** Read with forest_pick_anatomy_3y.

### 2026-09-29 · decisions: stop rules lifted, decision log opened
git `f5e064f` · [note](notes/2026-09-29-decisions.md)
- **Did:** Carter lifted the stop rules of agents.md for now (2026-09-29), restated the goal (a few high-precision, low-risk selections with upside; precision 0.65 or more on a modest target) and asked for every decision to be logged. Opened the decision log. Decisions 1 to 3: measure the tails of the picks' returns before searching parameters; add pick outcomes and top_k 5 and 10 to the three parameter searches, which had not run; keep the searches queued behind the new sweeps.
- **Got:** No run. Queue: baseline_pick_anatomy_3y (4 runs), forest_pick_anatomy_3y (18), then the three searches (40 each).
- **Concluded:** The hard invariants, the branch workflow and the holdout rules are not part of what was lifted and are kept.
- **Next:** baseline_pick_anatomy_3y.

### 2026-09-29 · forest_label_rungs_dd_entry_3y
27 runs · `dataset_v1.4` · 9 cells · git `6711efd` · [summary](../reports/sweeps/forest_label_rungs_dd_entry_3y/forest_label_rungs_dd_entry_3y_summary.md) · [note](notes/2026-09-29-label-rungs-dd-entry.md)
- **Did:** Ran one forest configuration on three seeds in nine cells, CAGR floor 0.08 / 0.10 / 0.15 × drawdown-from-entry cap 0.15 / 0.20 / 0.30, with pick outcomes. 27 hashes matched to the ledger shard (432 fold rows), 112 columns. The centre cell reproduces the reference (p@20 0.500, fold-mean PR-AUC 0.3267).
- **Got:** Picks' beat_spy hit rate 0.43–0.50 across the nine cells (bar 0.49, all rows 0.36); mean of yearly median excess CAGR −0.015 to +0.001 (bar −0.004); 2013–20: 0.42–0.48 (bar 0.44) and −0.008 to −0.022 (bar −0.019). Median drawdown of the picks 0.19–0.25 (bar 0.26). p@20 runs from 0.23 (floor 0.15) to 0.57 (0.08 / 0.30). Entry years 2013–16: hit rate 0.51–0.68; 2017–20: 0.28–0.36. No cell passes the rule on every seed: 0.08 / 0.20 and 0.10 / 0.20 pass on two seeds of three.
- **Concluded:** The label's thresholds move p@20 and PR-AUC and leave the picks' outcomes where they were; the forests' picks match the single factor's on excess return and SPY on the median, with a lower drawdown. Predictions: matched for the hit rate across caps, the 0.15 floor's p@20 and drawdown, and no cell above +0.03; missed for the cap lowering the picks' drawdown (flat at floors 0.08 and 0.10), for the cap lowering mean excess CAGR (not monotone) and for the 0.15 floor raising mean excess CAGR (it lowers it). Stopped by the stop rule: predictions contradicted.
- **Next:** Carter: whether the three parameter searches run as queued, and whether pick_outcomes goes into them first. Proposed, not run: overlap of picks between two cells from vml-run bundles; a backtest of the centre forest against the single factor once cost_bps and the filter are set.

### 2026-09-28 · baseline_pick_outcomes_3y
2 runs · `dataset_v1.4` · `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2` · git `6146e5f` · [summary](../reports/sweeps/baseline_pick_outcomes_3y/baseline_pick_outcomes_3y_summary.md)
- **Did:** Ran the two low-risk single factors in the primary cell with pick outcomes, through the ledger (sandbox shard): the bar for the pick-outcome screen. Deterministic, one run each; the cell now has 66 configurations.
- **Got:** Highest conservative_score_rank, top 20 per year, pooled: p@20 0.3875, picks beat SPY 0.4906 of the time (all test rows 0.363), median excess CAGR −0.0023 (all rows −0.073), mean −0.021, median drawdown from entry 0.19, 15.4 distinct stocks per 20 picks. By half: beat_spy hit rate 0.54 in 2005–12 and 0.44 in 2013–20 (all rows 0.41 and 0.30); fold mean of the yearly median excess CAGR +0.012 and −0.019. Entry years 2017–20: hit rate 0.10–0.35, median excess −0.02 to −0.12. Lowest vol_36m_rank: p@20 0.325, hit rate 0.378, median excess −0.026, 8.6 stocks per 20 picks.
- **Concluded:** As expected in the config: the three figures equal the smoke test of 2026-09-28, so the harness did not change. The bar a label's forest has to beat on the screen is a hit rate of 0.49 pooled and 0.44 in 2013–20, and a median excess CAGR of about zero pooled and −0.02 in 2013–20. The single factor's picks do not beat SPY after 2017. vol_36m_rank picks fewer than 9 stocks per 20 rows and is not the bar.
- **Next:** forest_label_rungs_dd_entry_3y (next in the queue).

### 2026-09-28 · forest_feature_sets_dd_entry_3y
30 runs · `dataset_v1.4` · `fwd_3y_cagr >= 0.1 & fwd_3y_max_drawdown_from_entry < 0.2` · run on the host at git `00ba3ec`, read 2026-09-29 · [note](notes/2026-09-29-feature-sets-dd-entry.md)
- **Did:** Read the feature-set sweep (run on the host): five arms against the 112 rank columns, two parameter sets, three seeds. All 30 config hashes matched to the ledger (480 fold rows); rows, effective sizes and base rates per fold equal the reference's; resolved column counts 97 / 15 / 109 / 125 / 172.
- **Got:** Fold-mean PR-AUC, reference 0.327: ranks + sector ranks 0.327; technical ranks alone 0.322; ranks + raw technical and trend 0.313–0.315; ranks without technical 0.311–0.312; ranks without the two volatility ranks and the conservative score 0.305–0.309. p@20 in the same order: 0.49–0.50 (reference 0.50), 0.46, 0.44–0.45, 0.40–0.42, 0.39. 2019 entries score 0.00–0.05 in every arm (base 0.09). The summary's pooled PR-AUC (0.24–0.27) is not the fold mean and is not comparable with 0.327.
- **Concluded:** No arm beats the 112 rank columns, which stay the feature set for the parameter search. Most of the signal is three columns: 15 technical ranks alone come within 0.005 PR-AUC, and removing vol_12m_rank, vol_36m_rank and conservative_score_rank costs as much as removing all 15. Predictions: matched for sector ranks and for PR-AUC of technical-alone; missed for p@20 of technical-alone (0.043 below, 0.03 predicted) and for the raw columns (PR-AUC 0.011–0.015 lower in 13 of 16 years, 0.005 predicted). Neither miss changes the feature set. Code differs from the reference (00ba3ec against 86ef0c4) and the reference was not re-run.
- **Next:** Queue as it stood (pick-outcome baseline, label rungs), then the parameter search per family in the primary cell on the 112 ranks, 40 draws each. Proposed, not queued: raw technical and raw trend as separate arms, to say which lowers PR-AUC.

### 2026-09-28 · harness: forest memory
git `feb0b55`
- **Did:** Profiled forest runs in the sandbox (14 GB, no swap) after Carter measured up to 18 GB on the host. Found that a fitted scikit-learn forest stores its sample weights, which were a view into the fold's training frame, so every fold model kept about 1 GB alive. Weights and targets are now copied.
- **Got:** Before: resident memory grew about 1.0 GB per fold (6.6 GB after two folds). After: a full 16-fold run of forest set1 in the from-entry cell peaks at 6.4 to 6.7 GB and takes 470 s with n_jobs 8. All 16 fold rows equal the ledger rows of the same configuration (forest_drawdown_compounder_seeds_3y, seed 23): counts, p@20, PR-AUC, ROC-AUC and Brier, difference 0.
- **Concluded:** Forest sweeps fit in the 14 GB sandbox. About 5 GB of the footprint is the dataset frame and split tags, loaded before any model is fitted. Probe runs used a scratch ledger and are not trials.
- **Next:** First unattended session end to end once the machine account can push.

### 2026-09-28 · harness: unattended runs
git `HEAD` of `claude/sweep-review-2026-09-28` · [how it works](agents.md)
- **Did:** Built the run queue (`vml-queue`), this logbook (`vml-logbook`), sweep resume (`vml-sweep --resume`), ledger shards (`experiments/ledger/`), checkpoints, and the pull-request check for working material. Split `findings.md` (1,165 lines) into this logbook, a 137-line findings file and notes.
- **Got:** 446 tests pass. No experiment run.
- **Concluded:** An agent can work a queue without polling and lose at most the run in flight. Not yet tried end to end in a sandbox.
- **Next:** Carter: sandbox memory, machine user, branch rules ([agents.md](agents.md), "Setting up").

### 2026-09-28 · harness: pick_outcomes
smoke test, scratch ledger, not a logged trial · git `362181a` · [how it works](experiments.md)
- **Did:** Built report-only outcomes of the top-K picks. Smoke test: highest `conservative_score_rank` in the from-entry cell.
- **Got:** p@20 0.3875, equal to the ledger's run of that baseline; picks' hit rate on `label_3y_beat_spy` 0.4906, equal to the same factor's p@20 in the beat_spy cell (a separate run). Picks: median excess CAGR −0.002, mean −0.021; all test rows −0.073 and −0.106. 15.4 distinct stocks per 20 picks.
- **Concluded:** The screen describes the right rows. The universe loses to SPY on average, so picks' excess return is read against zero.
- **Next:** `baseline_pick_outcomes_3y`, `forest_label_rungs_dd_entry_3y` (queued).

### 2026-09-28 · baseline_lowvol_rank_3y
12 runs · `dataset_v1.4` · 3 cells · git `3f2bfdf` · [note](notes/2026-09-28-drawdown-compounder-cells.md)
- **Did:** Four low-risk single factors as baselines in the two compounder cells and 3y beat_spy.
- **Got:** Best factor everywhere: `conservative_score_rank`. From entry 0.39 (forests 0.48–0.50, LightGBM 0.39–0.40); whole path 0.34 (forests 0.37–0.39); beat_spy 0.49 (forests 0.40–0.54). Lowest `vol_12m_rank`: p@20 0.09 with PR-AUC 0.31.
- **Concluded:** From entry, forests add 0.11 to a single factor and LightGBM nothing; whole path is close to a screen; on beat_spy no forest beats the factor. The between-readings result (0.39) was not one of the two outcomes written in the config.
- **Next:** Feature sets in the from-entry cell.

### 2026-09-28 · forest_v11_column_control_3y, forest_v14_unchanged_columns_3y
8 + 4 runs · `dataset_v1.1`, `dataset_v1.4` · `label_3y_beat_spy` · git `3f2bfdf` · [note](notes/2026-09-beat-spy-v11-to-v14.md)
- **Did:** v1.1 forests without the four dropped columns (120), and without the 17 columns whose values changed at v1.2 (103); the same 103 on v1.4.
- **Got:** 120 columns: 0.583 / 0.570, as with all 124 (0.589 / 0.583). 103 columns: 0.430 / 0.466, and all 64 fold rows identical between v1.1 and v1.4.
- **Concluded:** As predicted for the second outcome: the v1.1 edge is in the v1.1 form of the 17 re-mapped rank columns. Dropped columns ruled out; nothing else differs between the versions. Whether that form carried a quarter identifier or stock information is open.
- **Next:** Nothing on v1.1. Per-quarter picks if the question is ever worth a run.

### 2026-09-28 · forest_v11_code_control_3y
4 runs · `dataset_v1.1` · `label_3y_beat_spy` · git `86ef0c4` · [note](notes/2026-09-beat-spy-v11-to-v14.md)
- **Did:** Re-ran two August forest winners on v1.1 with today's code.
- **Got:** All 64 fold rows equal the August ledger rows.
- **Concluded:** As predicted: the code is not why v1.4 scores lower.

### 2026-09-28 · forest_drawdown_compounder_seeds_3y, lgbm_drawdown_compounder_seeds_3y, baseline_{random,rank_factor,majority}_drawdown_compounder_3y
24 + 12 + 12 runs · `dataset_v1.4` · 2 cells · git `86ef0c4` · [note](notes/2026-09-28-drawdown-compounder-cells.md)
- **Did:** Three seeds of two forest sets and one LightGBM set in the two compounder cells, with random and value-factor baselines.
- **Got:** From entry: forests 0.48–0.50, LightGBM 0.39–0.40, base 0.21. Whole path: 0.37–0.39, 0.33–0.35, base 0.11. Seed std at most 0.03. 2013–20 higher than 2005–12 for every candidate. At the base rate for entry years 2005–08 and 2019.
- **Concluded:** The single-seed results held and the lift is not a 2005–12 lift. Value factors are the wrong baseline for these labels (0.03–0.11).
- **Next:** A low-volatility baseline (done, above).

### 2026-09-28 · forest_feature_ablation_3y
8 runs, one seed · `dataset_v1.4` · `label_3y_beat_spy` · git `86ef0c4` · [note](notes/2026-09-beat-spy-v11-to-v14.md)
- **Did:** The v1.1 column set on v1.4 (arm fs0) and three other feature sets.
- **Got:** fs0 0.44 pooled against 0.60 for the same parameters and seed on v1.1. PR-AUC 0.42 in every arm; removing the 13 added columns raises it by 0.01–0.02 in 15 of 16 years. Arms span 0.44–0.54 and swap order between parameter sets.
- **Concluded:** Against the prediction (0.58 if the added columns were the cause): they are not. No arm can be told from another on one seed.
- **Next:** Column controls (done, above).

### 2026-09-27 · forest_candidate_sets_3y, xgb_candidate_sets_3y, v1.4 baseline grid
18 + 9 + 80 runs · `dataset_v1.4` · `label_3y_beat_spy` (baselines: 20 stored-label cells) · git `b649c58` · [note](notes/2026-09-beat-spy-v11-to-v14.md)
- **Did:** The August forest and xgboost winners on v1.4, three seeds.
- **Got:** Forests 0.42 pooled, 0.59 in 2005–12, 0.26 in 2013–20 (base 0.29); xgboost 0.37 / 0.54 / 0.20. On v1.1 the same forests scored 0.58.
- **Concluded:** No edge after 2013 on v1.4. First written up as "did not replicate", withdrawn on 2026-09-28: the two versions did not use the same columns. Cause since located (column controls, above).

### 2026-09-26 · review after the August/September hiatus
about 1,570 runs reviewed · `dataset_v1.0`, `v1.1`, `v1.4` · [v1.1 families](notes/2026-08-beat-spy-v11-families.md) · [earlier work](notes/2026-08-earlier-work.md) · [derived labels](notes/2026-09-derived-label-cells.md) · [process](notes/process-issues.md)
- **Did:** Reviewed the ledger, every sweep summary and the holdout record; promoted 7 results; cleared 87 untracked configs.
- **Got:** On v1.1, forests kept an edge after 2013 on 3y beat_spy (0.49 against a 0.29 base rate) where boosted families did not. Compounder labels 1.5–3× their base rate on one seed; large excess return no skill. 19 holdout looks, none at 3y.
- **Concluded:** Carry the v1.1 forest and xgboost winners forward to v1.4, and multi-seed the compounder labels.
