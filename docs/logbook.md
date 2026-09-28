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

### 2026-09-28 · forest_feature_sets_dd_entry_3y
30 runs · `dataset_v1.4` · from-entry cell · started on the host 14:48, 13 of 30 done at 15:40
- **not yet read**: the sweep is running. Five feature sets against the all-ranks reference; predictions are in the config.

### 2026-09-28 · harness: unattended runs
git `HEAD` of `claude/sweep-review-2026-09-28` · [how it works](agents.md)
- **Did:** Built the run queue (`vml-queue`), this logbook (`vml-logbook`), sweep resume (`vml-sweep --resume`), ledger shards (`experiments/ledger/`), checkpoints, and the pull-request check for working material. Split `findings.md` (1,165 lines) into this logbook, a 137-line findings file and notes.
- **Got:** 446 tests pass. No experiment run.
- **Concluded:** An agent can work a queue without polling and lose at most the run in flight. Not yet tried end to end in a sandbox: forests need about 18 GB and the sandbox has 14.
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
