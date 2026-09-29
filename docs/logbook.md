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
