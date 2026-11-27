# How an agent works in this repository

This file is the agent's manual for a session. It says what to read
first, how a session runs, where each kind of record is written, and how
work leaves the sandbox. Everything in CLAUDE.md applies without
exception: the hard invariants, the branch workflow and the rules under
"Before writing a conclusion". This file adds what CLAUDE.md does not
cover. Carter's one-time setup and his side of a session are in
[setup.md](setup.md).

## Start of a session

Read these, in this order:

1. [next-steps.md](next-steps.md): what to work on now, and what is
   waiting on Carter.
2. [decisions.md](decisions.md): the decisions that are still in force.
   Work that contradicts one of them needs a new decision first.
3. [findings.md](findings.md): what the project knows and where it
   stands.
4. [logbook.md](logbook.md): the newest entries. Run `vml-logbook
   unread` to list sweeps that finished with nobody reading them. Those
   come first.
5. [GLOSSARY.md](../GLOSSARY.md) for any term you do not know.

Then check the branch. A session can start with `Claude` checked out.
Create the lab branch with `uv run vml-queue new-lab` (see "Git"
below). If the previous session's results branch has merged and its lab
branch still exists, archive the lab branch first.

## Two ways of working

Carter's opening message says which one applies. If it does not say,
use the second: it has been the standing arrangement since 2026-10-01.

- **"Work the queue."** Run the loop and obey the stop rules below as
  written. Run what the queue holds, extend it only with items that
  next-steps.md already names, and stop at the first surprise.
- **"Do whatever is best to reach the goal."** A goal-directed session.
  You may open a new direction, write and run new configs, build code
  and continue experiments with it, and keep going after a prediction
  fails. In return you owe the record described in the next section.

In both, these stay Carter's: **a look at the sealed holdout, a
deployment, and any merge into `Claude` or `main`.**

## What a goal-directed session owes

The freedom depends on the record being complete.

1. **Log every decision before acting on it.** A decision is anything a
   later session would otherwise have to guess: a new direction, a new
   cell or universe, a criterion, a candidate carried forward or
   dropped, a rule about what will not be run. Write it as a numbered
   entry in the decision log (see "The records" below), saying what was
   decided, why, and what evidence it rests on. Then update
   decisions.md in the same commit.
2. **Write each run's prediction before the run**, in the config, with
   the rival explanation if there is one. The logbook entry says which
   predictions held.
3. **Read a failed prediction; do not skip it.** Write a note that
   lists the rival explanations and what would tell them apart. You may
   then run the experiment that tells them apart. A result far above
   its baseline may be leakage, and a result far below an earlier one
   may come from a changed input. Check either for a bug before
   building on it.
4. **Put code on a feature branch** named `claude/<topic>`, created
   from `Claude`, with tests, and push it. Merge it into the lab branch
   between runs and continue experiments from the lab branch. While a
   run is going, develop in a separate git worktree: each step of a
   chain is a new process and would pick up a half-edited `src/`.
5. **Write the criteria before the results.** What would send a
   candidate to a backtest, or carry it forward, goes in the decision
   log before the runs that are judged on it.
6. **Use each body of evidence once.** Years that a candidate was not
   chosen on, such as the holdout window or trading after the last
   fold, are read for that fixed candidate and never used to choose
   between variants. Any further portfolio or model run on those years
   needs a decision that explains why it is not a selection. State the
   number of configurations tried on a set of years with every figure
   taken from those years.
7. **Leave the record in order at the end** (see "End of a session").

Only a goal-directed session may open a new direction, extend the
queue beyond next-steps.md, promote results, or build the results
branch.

## The records

Each kind of record has one place. Write a thing in its place and link
to it from elsewhere; do not copy it.

| record | file | how it changes |
|---|---|---|
| what was done, run by run | `docs/logbook.md`, newest first | one entry per sweep or run, added with `vml-logbook add`; never edited afterwards |
| each decision in full | the decision log, `docs/notes/<date>-decisions.md` | numbered entries appended; never edited afterwards |
| decisions still in force | `docs/decisions.md` | updated in the commit that adds a decision |
| what is known, and where the project stands | `docs/findings.md` | rewritten when a conclusion changes |
| what to do next | `docs/next-steps.md` | rewritten at the end of every session |
| code still to be built | `TODO.md` | items added when found, removed when built |
| tables, checks, reasoning | `docs/notes/<date>-<topic>.md` | as long as needed; linked from the logbook, the decision log or findings |
| every run | the ledger, `experiments/ledger/<sandbox>.csv` | written by the harness |
| what exactly ran | the run's report directory: the config copy, `*_config.json`, `*_result.json` | written by the harness |

### The logbook

An entry has four parts, **Did / Got / Concluded / Next**, one or two
sentences each, with the numbers. It says whether the result matched
the prediction. A failed or pointless experiment gets an entry like any
other. If an entry needs a table, put the table in a note and link it.

### The decision log

Decisions are numbered in one sequence across files. Append each new
decision to the newest `docs/notes/*-decisions.md` file. When that file
passes about 1,500 lines, start a new one named after the day it
starts, add a closing line to the old one that names the new file, and
continue the numbering. A closed log file is never edited again; a
correction is a new decision that names the old one.

### decisions.md

decisions.md lists every decision that will affect future work, grouped
by subject. Each line says what is in force, why, and which numbered
decisions and notes hold the full reasoning. Keep it current in the
same commit as the decision log:

- A new standing decision (a rule, criterion, definition, working
  assumption or setting) gets a line in its group.
- When a decision changes or replaces an earlier one, rewrite the
  earlier line so that it states the current rule, and cite both
  numbers.
- A one-time decision ("run X", "build Y") goes under "Open actions"
  until the action is done, and is then removed. The logbook records
  that it was done.
- When a line of research is closed, add one line under "Closed lines
  of research" saying what was closed and why, so that no session
  repeats it without a new reason.
- A question put to Carter goes under "Waiting on Carter" until he
  answers. His answer becomes a decision like any other.

### findings.md

findings.md says what the project knows and where it stands. It holds
conclusions, not plans. Its own opening section states the rules for
what belongs in it.

### next-steps.md

next-steps.md is the plan for the next session. A reader with no
context should be able to start work from it. Rewrite it at the end of
every session: remove what was done, reorder what is left, and put each
item's first concrete action in the item. Long-term plans and the
reasons behind them belong in decisions.md; next-steps.md links there.

### TODO.md

TODO.md is the backlog of code and tooling still to be built: harness
features, engine gaps, catalog fixes, tests, and the upstream requests
that are outstanding. It is not a research plan. Remove an item when it
is built, and mention the change in the logbook entry of the run that
first uses it.

## The loop

One turn per finished sweep, and nothing in between.

1. **Find the next item.** `vml-queue status` says what is next.
2. **Launch it** as a background command, and end the turn:

   ```sh
   vml-queue run-next --push
   ```

   This runs the first queue item that is not done (resuming it if it
   was interrupted), writes a logbook entry marked **not yet read**
   from the facts alone, commits a checkpoint, pushes, and exits. The
   exit wakes the agent.
3. **Do not poll.** No progress checks, no sleeping loops, no "still
   running" turns. A fallback wake-up, if you set one, is one per sweep
   at no less than twice the sweep's expected duration, and its only job
   is to notice a process that has hung.
4. **Read the summary** when woken. Read the per-year table before the
   pooled number, and compare both with the predictions written in the
   config.
5. **Write the entry** that replaces the stub, and the note if the
   result needs tables:

   ```sh
   vml-logbook add --sweep experiments/sweeps/<name>.toml \
     --did "..." --got "..." --concluded "..." --next "..." \
     --note docs/notes/<date>-<name>.md
   ```

6. **Checkpoint:** `vml-queue checkpoint --push -m "lab: <name> read"`.
7. **Decide**, using the stop rules below, whether to launch the next
   item or stop.

## Stop rules

These bind a session that is working the queue. A goal-directed
session treats the second and third rules as "read the result and log
a decision" (see above) and keeps the rest.

Stop, and leave a logbook entry saying why, instead of launching the
next item, when:

- the queue is empty. You may extend the queue only with items that
  next-steps.md already names; a new direction is Carter's to choose;
- a result contradicts the prediction written in its config. Write a
  note with the rival explanations, and propose (do not run) the
  experiment that would tell them apart;
- a result is far above its baseline (suspect leakage first) or far
  below an earlier one (suspect a changed input first);
- a run failed for a reason you do not understand;
- a checkpoint could not be pushed twice in a row. Work that cannot
  leave the sandbox can be lost;
- the next step would touch the holdout, promote a result, open a pull
  request into `Claude`, or deploy. Those are Carter's.

## Running jobs in the sandbox

The sandbox has 24 cores, 14 GB of memory and no swap. These limits
shape how work is run.

- **One heavy job at a time.** About 5 GB is the dataset frame, loaded
  before any model is fitted. A 16-fold forest run takes about 4.5
  minutes and peaks at about 6.5 GB. A LightGBM regressor on all rows
  peaks near 8 GB. A backtest peaks at about 9.7 GB on
  `dataset_v1.4.1` and at 12.4 to 13.8 GB on `dataset_v1.5.1`, so
  nothing else may run beside a v1.5.1 backtest. On 2026-11-25 the
  sandbox died under an 11.6 GB backtest (decision 68). Measure a new
  kind of run on its own before putting it in a chain.
- **Keep `n_jobs` at or below the real core count.**
- **Launch long jobs with `run_in_background`.** The harness wakes the
  session when the process exits. Launch a chain script directly, not
  with `nohup ... &`, or the harness wakes on the launcher instead of
  the chain. Foreground `sleep` is blocked. Never wait with
  `while pgrep -f <name>`, and never `pkill -f` with a pattern that
  appears in your own command line: both match the calling shell.
- **A killed sweep is resumed by running it again** (`vml-queue
  run-next`, or `vml-sweep --resume`). Completed runs are read back
  from their result records and only the rest run.
- **Check paths and names before a chain runs.** Build config paths
  from the real file names and `test -f` each one. When copying a
  config under a new name, replace the exact old `name` line: a
  multi-line regular expression on `name = ".*"` also rewrites
  `[model] name`. Every failed run is a trial in its cell's count.
- **Count a new universe's training rows per fold before the sweep.**
  A column that needs history, such as `dist_5y_high`, leaves the
  early folds empty, and every run of the sweep then fails. Restrict
  `folds` in a copy of the file, because `vml-sweep` refuses a report
  directory whose config copy differs from the file.
- **Commands are in `.venv/bin`.** Call `.venv/bin/vml-...` directly
  if `vml-...` is not on the path. Read parquet with pandas or
  pyarrow; duckdb is not in the environment.

## Outputs, promotion and the catalog

### What is tracked

Everything a run generates is working output and is ignored by git:
reports and figures under `reports/`, model bundles under
`experiments/models/`, predictions under `predictions/`, the local
ledger `experiments/results.csv`, and every new config under
`experiments/`. Most configs are written, run once and forgotten, so an
untracked config is never a decision.

Two kinds of evaluation output are tracked:

- **Promoted results**, meaning results worth review or good examples.
  `uv run vml-promote <name> --note "one-line conclusion"` copies the
  report and its artifacts (rules, figures) into
  `reports/promoted/<name>/`, with a `config.toml` snapshot and a
  `promoted.json` provenance record (run id, config hash, cell, headline
  against the best baseline). It writes the note into the config, as
  `note = "..."` outside the config hash, stages the config and the
  promoted directory, and rebuilds the index
  `reports/promoted/README.md`. A sweep is promoted by name and brings
  its summary and CSVs, not its per-run reports. A single run of a sweep
  is promoted by its report path,
  `vml-promote reports/sweeps/<sweep>/<run>.md`. `vml-promote --list`
  shows what could be promoted, and `--index` rebuilds the index.
  Promoting a backtest or evaluation report by its path does not mark
  the config as promoted: add the config to `experiments/KEEP` so that
  `scripts/check_tracked_configs.py` passes.
- **The sealed final-eval record**, `reports/final_evals.csv` and
  `reports/final_eval/`. Always tracked.

A config becomes tracked when its result is promoted, or when it is
listed in `experiments/KEEP`. Never edit a config that has run: copy it
under a new `name`.

### Finding past work

Before writing a new config, check whether it, or something close, has
already run:

```sh
uv run vml-experiments                     # every config, grouped by cell, ranked by lift
uv run vml-experiments list --grep <text>  # searches names and notes
uv run vml-experiments list --model lightgbm --label beat_spy
uv run vml-experiments runs                # everything ever run, from the ledger
uv run vml-experiments show <config-or-name>
uv run vml-experiments sweeps --out reports/sweep_digest.md
```

The listing groups configs by cell (label, horizon, scheme, dataset
version), because numbers from different cells cannot be compared.
Inside a cell it ranks configs by **lift**: the headline metric of the
latest completed run minus the best baseline on the same metric in the
same cell (`scripts/run_baselines.py` produces the baselines; a cell
without them reads `none run`). Each row also shows the config's note,
whether the holdout has been looked at for it, and a star if it was
promoted.

`sweeps` reads every sweep summary and writes one markdown digest: per
cell, the top runs across all sweeps, and the mean metric for each
feature set, model and swept parameter. It is pooled and
selection-biased. Use it to rank candidates and settle parameters,
never to report a result.

Search the ledger by `config_path` as well as by name: runs with a
derived name do not carry the config's file name.

### The sealed holdout

An agent never runs `scripts/run_final_eval.py`. Carter takes each
look. How a look works, and how further looks are counted, is in
[experiments.md](experiments.md), "The sealed holdout".

## Git

- **Lab branches.** Work on a lab branch named `claude/lab-<date>`,
  created with `vml-queue new-lab`, which branches from `origin/Claude`.
  Never commit to `Claude` or `main`. Never create a lab branch from
  another lab branch, and never merge one lab branch into another
  (decision 68). `vml-queue checkpoint` refuses to run on a lab branch
  whose history holds the last commit of another lab branch, live or
  archived.
- **Checkpoints.** `vml-queue checkpoint` force-adds what a crash would
  take with it: the ledger shard, sweep summaries, config copies,
  result records, queued configs, the logbook, the decision records,
  findings, next steps and notes. Backtest reports and their CSVs must
  be added with `git add -f` first. It refuses to run off a `claude/`
  branch. Push after every checkpoint; if a push fails, say so and try
  again after the next sweep.
- **Lab branches are not merged.** They hold working material. What
  reaches `Claude` goes on a results branch, `claude/results-<date>`:
  code and tests, docs, promoted results and the ledger shard.
  `scripts/check_tracked_configs.py` names anything else, `--fix`
  untracks it, and the `pr-hygiene` workflow runs the same check on
  every pull request into `Claude` or `main`.
- **Building the results branch.** Create it from the code branch or
  `Claude`, then bring over the session's records:
  `git checkout <lab> -- docs TODO.md experiments/ledger
  experiments/queue.toml experiments/KEEP reports/promoted`, plus the
  configs named in each `promoted.json` and in `KEEP`. Run `vml-promote`
  in the main checkout on the lab branch first, because it needs the
  reports on disk. `scripts/check_tracked_configs.py` must print
  "nothing added". Push it. Carter opens the pull request.
- **Archive a finished lab branch.** Once the session's results branch
  has merged into `Claude`, run
  `uv run vml-queue archive-lab claude/lab-<date> --delete` from any
  other branch. It tags the branch's last commit `archive/lab-<date>`
  and deletes the branch. The configs and reports stay reachable
  through the tag.
- **Switching branches removes the lab's tracked files from disk.** To
  get a config back as an ignored file:
  `git checkout origin/claude/lab-<date> -- <config>`, then
  `git reset -q -- <config>`.

## The ledger

Runs append to the file named by `VML_RESULTS`. In a sandbox this is a
shard under `experiments/ledger/`, tracked and pushed with each
checkpoint. Every reader of the ledger reads the local
`experiments/results.csv`, every shard beside it, and the files named in
`VML_LEDGER_READ`, each row once. Trial counts are therefore complete
wherever the shards have been fetched, and nothing is merged by hand.
In a clone-mode sandbox the host's ledger is mounted read-only:

```sh
export VML_RESULTS="experiments/ledger/$SANDBOX_VM_ID.csv"
export VML_LEDGER_READ="/run/sandbox/source/experiments/results.csv"
```

If the sandbox dies while a run writes its row, the shard ends in a
partial row and the reader raises `LedgerError` naming the file. Delete
the fragment and run that config again.

## End of a session

Before the session ends:

1. Every run has a logbook entry. No **not yet read** stub is left.
2. Every decision is in the decision log, and decisions.md matches it.
3. findings.md is rewritten if a conclusion changed.
4. next-steps.md is rewritten for a reader with no context, including
   what is waiting on Carter.
5. TODO.md has the code items the session found or finished.
6. Results worth keeping are promoted.
7. A `claude/results-<date>` branch that passes
   `scripts/check_tracked_configs.py` is pushed for Carter to open the
   pull request from.
