# Workflow: outputs, promotion, the catalog, the final eval

## What is tracked

Everything a run generates is working output, git-ignored by default:
reports and figures under `reports/`, model bundles under
`experiments/models/`, predictions under `predictions/`, the local trial
ledger `experiments/results.csv` — **and every new config under
`experiments/`**. Most configs get written, run once and forgotten, so an
untracked one is never a decision to make. A config becomes tracked when
its result is promoted (or, for a sample worth keeping without a
report, `git add -f experiments/<config>.toml`; configs already tracked
stay tracked). Only two kinds of evaluation output are tracked:

- **Promoted results** — a result worth review or a good example:

  ```sh
  uv run vml-promote <experiment-name> --note "one-line conclusion"
  git commit
  ```

  copies the report and all its artifacts (rules, figures) into
  `reports/promoted/<name>/` together with a `config.toml` snapshot and a
  `promoted.json` provenance record (run id, config hash, cell, headline
  vs. best baseline), writes the note into the config (`note = "..."`,
  outside the config hash), stages the config (`git add -f`) and the
  promoted directory, and regenerates `reports/promoted/README.md` — the
  index of everything promoted, with cell, headline vs. baseline and
  note per row. Sweeps promote too, by name
  (`vml-promote <sweep-name>` takes the summary and its CSVs, not the
  per-run reports — a candidate worth keeping is promoted by its own
  report path, `vml-promote reports/sweeps/<sweep>/<run>.md`); `vml-promote --list`
  shows what could be promoted, `--index` rebuilds the index. Everything
  else can be deleted whenever it stops being useful — the results ledger
  keeps the trial accounting either way.
- **The sealed final-eval record** (`reports/final_evals.csv` and
  `reports/final_eval/`) — always tracked, never optional.

## Finding past work: the catalog

To find your way around past work instead of grepping TOML files:

```sh
uv run vml-experiments                 # every config, grouped by cell, ranked by lift
uv run vml-experiments list --model lightgbm --label beat_spy
uv run vml-experiments list --sort path   # the flat, path-ordered view
uv run vml-experiments runs            # ledger view: everything ever run
uv run vml-experiments show <config-or-name>   # one config, its runs, its cell's baselines
uv run vml-experiments sweeps --out reports/sweep_digest.md   # every sweep, digested
```

`sweeps` reads every `reports/sweeps/*/*_summary.csv` and writes one
markdown digest: per cell, the top runs across *all* sweeps (sweep,
model, feature set as the sweep config describes it, swept params,
metric, lift over the cell's best baseline) and a "what wins" list —
the mean metric by value for the feature set, the model and each swept
parameter (continuous random-search axes are binned into quartiles).
It is pooled and selection-biased, so it ranks candidates and settles
hyperparameters; it never reports a result. `--metric` picks the pooled
metric (default `precision_at_20`, falling back to the row's headline),
`--label` filters cells. Reading the digest beats reading thirty
summaries, for you and for anyone you paste it to.

The listing groups configs by *cell* (label · horizon · scheme · dataset
version) — numbers across cells are not comparable, so there is no global
sort — and inside a cell ranks them by **lift**: the headline metric
(`p@K`, else `recall@p…`, fold mean of the latest completed run) minus the
best baseline on that same metric in the same cell, taken from the
ledger's latest baseline runs (`scripts/run_baselines.py`; a cell without
baselines reads `none run`). Each row also shows the config's `note`,
whether the sealed holdout has been consumed for it (`final_eval`:
`phase3 ✓`), and `★` when promoted. Restricted schemes are flagged in the
group header (`holdout ⚠ final eval only`).

Before writing a new config, `vml-experiments list --grep <something>`
answers "have I done this already, and what's closest to edit from?" —
notes are searched too.

## The sealed holdout: final eval

The sealed `holdout` scheme and the diagnostic schemes (`entity_holdout`,
`random_kfold`) are refused by the runner — they raise errors unless
requested via the dedicated entry points: `scripts/run_final_eval.py`
(holdout, one look per cell) and `scripts/run_diagnostic.py` (the registered
diagnostics, see [diagnostics.md](diagnostics.md)).

The final eval takes the config you selected on walk-forward as it is —
no copied `*_holdout.toml`:

```sh
uv run python scripts/run_final_eval.py experiments/<selected>.toml
```

The scheme is switched to `holdout` in memory; the run keeps the
experiment's name (the report lands in `reports/final_eval/`, the row in
`reports/final_evals.csv`, and `vml-experiments` shows `✓ look 1/1` next
to the config). The holdout is the one number nobody selected on, and it
stays that only while it is looked at **once per cell** — label, horizon
and holdout window (the fold's test years from `split_folds.parquet`; a
feature-only dataset bump re-uses the same rows and does not re-seal
them). Run it when you would act on the model; choosing between
candidates is walk-forward's job. A second evaluation in a consumed cell
is refused unless you say why:

```sh
uv run python scripts/run_final_eval.py experiments/<other>.toml \
    --reopen "new model family after the v1.4 relvalue features"
```

It then runs as look 2, the reason is logged, and the report, the ledger
and the catalog (`✓ look 2/2`) all carry the count — N looks inflate the
best number by roughly the top order statistic of N draws, so the count
is part of the result, never hidden. Ledgers written under the older
`phase` column are migrated in place; their rows count as looks in
their cell.
