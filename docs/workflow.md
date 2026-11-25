# Workflow: outputs, promotion, the catalog, the final eval

## What is tracked

Everything a run generates is working output, and git ignores it by
default. That covers reports and figures under `reports/`, model
bundles under `experiments/models/`, predictions under `predictions/`,
the local trial ledger `experiments/results.csv`, **and every new
config under `experiments/`**. Most configs get written, run once and
forgotten, so an untracked one is never a decision to make. A config
becomes tracked when its result is promoted. A sample worth keeping
without a report can be tracked with `git add -f experiments/<config>.toml`.
Configs already tracked stay tracked. Only two kinds of evaluation
output are tracked:

- **Promoted results** are results worth review, or good examples:

  ```sh
  uv run vml-promote <experiment-name> --note "one-line conclusion"
  git commit
  ```

  The command copies the report and all its artifacts, rules and
  figures included, into `reports/promoted/<name>/`. It adds a
  `config.toml` snapshot and a `promoted.json` provenance record. The
  record holds the run id, the config hash, the cell, and the headline
  against the best baseline. It writes the note into the config as `note = "..."`,
  outside the config hash. It stages the config with `git add -f` and
  the promoted directory. It regenerates `reports/promoted/README.md`,
  the index of everything promoted, which shows cell, headline against
  baseline and note per row. Sweeps promote too, by name:
  `vml-promote <sweep-name>` takes the summary and its CSVs, not the
  per-run reports. A candidate worth keeping is promoted by its own
  report path, `vml-promote reports/sweeps/<sweep>/<run>.md`.
  `vml-promote --list` shows what could be promoted, and `--index`
  rebuilds the index. You can delete everything else whenever it stops
  being useful, because the results ledger keeps the trial accounting
  either way.
- **The sealed final-eval record** is `reports/final_evals.csv` and
  `reports/final_eval/`. It is always tracked and never optional.

## Finding past work: the catalog

The catalog finds past work, so you do not have to grep TOML files:

```sh
uv run vml-experiments                 # every config, grouped by cell, ranked by lift
uv run vml-experiments list --model lightgbm --label beat_spy
uv run vml-experiments list --sort path   # the flat, path-ordered view
uv run vml-experiments runs            # ledger view: everything ever run
uv run vml-experiments show <config-or-name>   # one config, its runs, its cell's baselines
uv run vml-experiments sweeps --out reports/sweep_digest.md   # every sweep, digested
```

`sweeps` reads every `reports/sweeps/*/*_summary.csv` and writes one
markdown digest. For each cell the digest lists the top runs across
*all* sweeps, with these columns:

- sweep
- model
- feature set, as the sweep config describes it
- swept params
- metric
- lift over the cell's best baseline

Each cell also gets a "what wins" list: the mean metric by value for
the feature set, the model and each swept parameter. Continuous
random-search axes are binned into quartiles. The digest is pooled and
selection-biased, so it ranks candidates and settles hyperparameters.
It never reports a result. `--metric` picks the pooled metric, which
defaults to `precision_at_20` and falls back to the row's headline.
The `--label` option filters cells. Reading the digest beats reading thirty
summaries, for you and for anyone you paste it to.

The listing groups configs by *cell*, that is by label, horizon,
scheme and dataset version. Numbers across cells are not comparable,
so there is no global sort. Inside a cell the listing ranks configs by
**lift**. Lift is the headline metric of the latest completed run, as a fold
mean, minus the best baseline on that metric in the same cell. The headline metric is `p@K`, or else `recall@p…`. The
baselines come from the ledger's latest baseline runs, which
`scripts/run_baselines.py` writes. A cell without baselines reads
`none run`. Each row also shows the config's `note`. It shows whether
the sealed holdout has been consumed for the config, as `final_eval`:
`phase3 ✓`. It shows `★` when the config is promoted. The group header
flags restricted schemes with `holdout ⚠ final eval only`.

Before writing a new config, run `vml-experiments list --grep <something>`.
It answers "have I done this already, and what's closest to edit
from?", and it searches notes too.

## The sealed holdout: final eval

The runner refuses the sealed `holdout` scheme and the diagnostic
schemes `entity_holdout` and `random_kfold`. They raise errors unless
the dedicated entry points request them. `scripts/run_final_eval.py`
runs the holdout, one look per cell. `scripts/run_diagnostic.py` runs
the registered diagnostics, see [diagnostics.md](diagnostics.md).

The final eval takes the config you selected on walk-forward as it is.
There is no copied `*_holdout.toml`:

```sh
uv run python scripts/run_final_eval.py experiments/<selected>.toml
```

The script switches the scheme to `holdout` in memory. The run keeps
the experiment's name. The report lands in `reports/final_eval/`, the
row in `reports/final_evals.csv`, and `vml-experiments` shows
`✓ look 1/1` next to the config. The holdout is the one number nobody
selected on. It stays that only while it is looked at **once per
cell**. A cell is a label, a horizon and a holdout window, the fold's
test years from `split_folds.parquet`. A feature-only dataset bump
re-uses the same rows and does not re-seal them. Run it when you would
act on the model. Choosing between candidates is walk-forward's job.
The script refuses a second evaluation in a consumed cell unless you
say why:

```sh
uv run python scripts/run_final_eval.py experiments/<other>.toml \
    --reopen "new model family after the v1.4 relvalue features"
```

It then runs as look 2, and the script logs the reason. The report,
the ledger and the catalog all carry the count, as `✓ look 2/2`.
N looks inflate the best number by roughly the top order statistic of
N draws. So the count is part of the result and never hidden. The
script migrates ledgers written under the older `phase` column in
place. Their rows count as looks in their cell.
