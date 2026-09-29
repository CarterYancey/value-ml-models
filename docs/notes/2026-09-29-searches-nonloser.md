# Parameter searches in cell C

Detail behind the [logbook](../logbook.md) entries for
`{forest,lgbm,xgb}_random_search_nonloser_3y`, run and read
2026-09-29/30 in the sandbox. Decision 11 of the
[decision log](2026-09-29-decisions.md).

Cell C: `fwd_3y_cagr >= 0 & fwd_3y_max_drawdown_from_entry < 0.3`,
3y, `dataset_v1.4`, walk-forward, test years 2005–2020 (16 folds,
`split_folds.parquet` of `dataset_v1.4`), the `ranks` group (112
columns), base rate 0.39. 20 draws per family, one seed (23), equal
budgets. 72 configurations tried in the cell after the searches (12
before). Selection-biased by that count; none is a result of record.

Checked: 20 config hashes per sweep in the ledger shard, 320 fold
rows each, all completed, 16 folds per hash; git `829d6c3`
(forests), `f2caa98` (LightGBM), `68d3a2b` (XGBoost, `device =
"cpu"`), which differ by checkpoint commits only. PR-AUC is the mean
of the 16 fold values from the ledger, not the pooled figure of the
sweep summaries. Pick outcomes are for the top 20 per year.

## Results

Range over the 20 draws of each family:

| | forests | LightGBM | XGBoost | reference forest (3 seeds) |
|---|---|---|---|---|
| fold-mean PR-AUC | 0.581–0.585 | 0.566–0.581 | 0.567–0.581 | 0.585 |
| p@20 | 0.72–0.78 | 0.64–0.75 | 0.63–0.75 | 0.78–0.79 |
| p@20, 2013–20 | 0.77–0.84 | 0.65–0.86 | 0.64–0.83 | 0.84 |
| p@20, entry years 2006–08 and 2019 | | 0.10–0.34 | 0.14–0.33 | 0.42 |
| picks' losers (CAGR < 0) | 0.12–0.20 | 0.15–0.25 | 0.16–0.24 | 0.13 |
| picks' big losers (CAGR < −0.1) | 0.04–0.09 | 0.06–0.11 | 0.06–0.10 | 0.06 |
| picks' big winners (CAGR ≥ 0.25) | 0.03–0.08 | 0.01–0.03 | 0.01–0.05 | 0.03 |
| picks beat SPY | 0.40–0.49 | 0.25–0.36 | 0.27–0.40 | 0.46 |
| picks' median excess CAGR | −0.019 to +0.007 | −0.069 to −0.025 | −0.067 to −0.020 | +0.001 |
| years Brier beats the no-skill reference | 10–11 | 2–10 | 2–10 | 11 |

The reference forest's figure for 2006–08 and 2019 is the mean of
the by-year table in the
[pick-anatomy note](2026-09-29-pick-anatomy.md) (0.55, 0.23, 0.38,
0.53); it was not computed for the forest draws.

## Against the predictions in the configs

| family | prediction | measured | matched? |
|---|---|---|---|
| forests | at least 15 of 20 draws within 0.010 of 0.585, none above 0.600 | all 20 within 0.005; highest 0.5853 | yes |
| forests | picks' losers within 0.10–0.18 for those draws | 0.12–0.20; three draws at 0.19–0.20 | **no** |
| forests | deep draws with small leaves have the lowest PR-AUC | the six lowest are all gini; depth 3 to 12 at both ends | **no** |
| LightGBM | best draw between 0.565 and 0.590 | 0.581 | yes |
| LightGBM | the draws span at least 0.03 | 0.015 | **no** |
| LightGBM | no draw's picks have fewer losers than 0.13 | lowest 0.147 | yes |
| XGBoost | best draw within 0.005 of LightGBM's best | 0.581 and 0.581 | yes |
| XGBoost | no draw exceeds the forest's 0.585 by 0.01 | highest 0.581 | yes |
| XGBoost | the best draws are shallow (depth 3–5) | the five highest have depths 5, 7, 3, 9, 6 | **no** |

## Measured

1. **No draw of any family exceeds the reference forest's PR-AUC.**
   None goes to three seeds or to a backtest; the candidate's model
   stays as it is.
2. **Forest parameters move PR-AUC by 0.005.** The split criterion
   orders the draws (five of the six highest are entropy, the six
   lowest gini); depth, leaf size and the rest do not.
3. **The boosted families reach the forests' PR-AUC to within 0.004
   and pick worse.** Their top 20 hold more losers (0.15–0.25
   against 0.12–0.20), beat SPY less often (0.25–0.40 against
   0.40–0.49) and have a median excess CAGR of −0.02 to −0.07
   against about zero. In the entry years 2006–08 and 2019 their
   p@20 is 0.10–0.34.
4. **Inside the boosted families PR-AUC and p@20 point in opposite
   directions.** The draws with the most boosting (learning rate ×
   rounds above 30) have the lowest PR-AUC (0.566–0.570) and the
   highest p@20 (0.73–0.75; 2013–20 0.81–0.86); the least boosted
   have the highest PR-AUC and p@20 of 0.65–0.70. A ranking of
   boosted draws on PR-AUC picks the worse top of the list.
5. **Boosted scores are further from probabilities:** Brier beats
   the no-skill reference in as few as 2 of 16 years, against 10–11
   for every forest draw.

## What it might mean (hypotheses, not tested)

- *Why boosted models pick worse at the same PR-AUC.* PR-AUC is over
  all 16,000 test rows of a year; the portfolio needs the top 20.
  Forests average many shallow trees and are smooth at the top;
  boosted models fit residuals and may push a few unusual rows to
  the very top. Not tested; the top-K overlap between a forest and
  a boosted model's picks would show it.
- *Measured 4 says PR-AUC is the wrong ranking metric for this
  goal* inside the boosted families. For forests the two agree.
  p@20 on one seed has a standard error of about 0.03, so the
  pattern rests on the ordering of 20 draws, not on any pair.
