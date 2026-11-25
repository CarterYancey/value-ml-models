# Unattended sessions

This file says how an agent runs experiments on its own in a sandbox,
and what Carter sets up once so that it can. The rules in CLAUDE.md all
apply. This file adds the ones that only matter when nobody is
watching.

## Two ways of working

Which one a session is in depends on what Carter asked for.

- **"Work the queue."** The session follows the loop and the stop
  rules below, as written. The agent runs what the queue holds,
  extends it only with items the plan in findings.md already names,
  and stops at the first surprise.
- **"Do whatever is best to reach the goal."** The session is
  goal-directed. The sessions of 2026-09-29 to 2026-10-01 worked this
  way, and Carter made it the standing arrangement on 2026-10-01. The
  agent may open a new direction, write and run new configs, and build
  code and continue experiments off it. A contradicted prediction does
  not stop it. What it owes in return is under "A goal-directed
  session".

In both, the hard invariants of CLAUDE.md, its branch workflow and
its rules under "Before writing a conclusion" hold without exception.
These stay Carter's: **a holdout look or re-look, deployment, and the
merge into `Claude`**.

## A goal-directed session

The goal is in findings.md ("State") and in the decision log
([notes/2026-09-29-decisions.md](notes/2026-09-29-decisions.md)).
The freedom is conditional on the record:

1. **Every decision is logged before it is acted on.** The log entry
   is a numbered entry in the decision log that says what was decided,
   why, and what it rests on. A decision is anything a later session
   would otherwise have to guess. Examples are a new direction, a new
   cell or universe, and a criterion. A candidate carried forward or
   dropped, and a rule about what will not be run, are decisions too.
2. **Every run carries its prediction**, written in the config before
   the run, with the rival explanation where there is one. The
   logbook entry says which predictions held.
3. **The agent reads a contradicted prediction instead of skipping
   it.** The prediction gets a note with the rival explanations and
   what would separate them. The session may then run the experiment
   that separates them. The agent checks a result far above its
   baseline as leakage first. It checks a result far below an earlier
   one as a changed input first. Either check comes before anything is
   built on the result.
4. **Code goes on a feature branch**, `claude/<topic>`, off `Claude`,
   with tests, and is pushed. The agent merges it into the lab branch
   between runs, and experiments continue off the lab branch. Develop
   in a separate worktree while a run is going. Each step of a chain
   is a new process and would pick up a half-edited `src/`.
5. **Criteria are written before results.** The decision log says
   what would send a candidate to a backtest, or carry it forward. It
   says so before the runs that are judged on it.
6. **Evidence is spent once.** The years a candidate was not chosen
   on are the holdout window and trading past the last fold. The agent
   reads them for the fixed candidate and never uses them to choose
   between variants. A further portfolio or model run on those years
   needs a decision that says why it is not a selection. The number of
   configurations tried on a set of years is stated with every figure
   from them.
7. **The session ends with the record in order.** The record in order
   means:
   - a logbook entry for every run
   - findings.md rewritten
   - TODO.md's next steps written for a reader with no context
   - results worth keeping promoted with `vml-promote`
   - a `claude/results-<date>` branch that passes
     `scripts/check_tracked_configs.py`, for Carter to open the pull
     request from

What a goal-directed session may do that the queue loop may not:
open a new direction, extend the queue or run configs outside it,
promote results, and build the results branch. What it still may not
do is listed above.

## The loop

The agent takes one turn per finished sweep, and nothing in between.

1. **The session starts with reading.** Read [logbook.md](logbook.md), then
   [findings.md](findings.md). `vml-logbook unread` lists sweeps that
   ended with nobody reading them: those come first. `vml-queue status`
   says what is next.
2. **Launch** the next sweep as a background command and end the turn:

   ```sh
   vml-queue run-next --push
   ```

   It runs the first queue item that is not done, and resumes it if it
   was interrupted. It writes a **not yet read** logbook entry from the
   facts, commits a checkpoint, pushes, and exits. The exit wakes the
   agent.
3. **Do not poll.** Make no progress checks, no sleeping loops, and no
   "still running" turns. A fallback wake-up, if set, is one per sweep
   and at least twice the sweep's expected duration. Its only job is
   to notice a hung process.
4. **Read** the summary when woken. Read the era table before the
   pooled number. Compare with the predictions written in the config.
5. **Write the entry** that replaces the stub, then the note if the
   result needs tables:

   ```sh
   vml-logbook add --sweep experiments/sweeps/<name>.toml \
     --did "..." --got "..." --concluded "..." --next "..." \
     --note docs/notes/<date>-<name>.md
   ```

6. **Checkpoint:** `vml-queue checkpoint --push -m "lab: <name> read"`.
7. **Decide**, by the stop rules below, whether to launch the next
   item or stop.

## Stop rules

These bind a session working the queue. A goal-directed session
treats the second and third as "read it and log a decision" (above),
and keeps the rest.

Stop and leave a logbook entry saying why, instead of launching the
next item, when:

- the queue is empty. An agent extends the queue only with items the
  plan in findings.md already names. A new direction is Carter's.
- a result contradicts the prediction written in its config. The
  surprise gets a note with rival explanations. The next experiment
  is the one that separates them, proposed, not run.
- a result is far above its baseline, or far below an earlier one. The
  first is read as leakage first, the second as a changed input first.
- a run failed for a reason that is not understood.
- a checkpoint could not be pushed twice in a row. Work that cannot
  leave the sandbox is work that can be lost.
- the next step would touch the holdout, promote a result, open a pull
  request into `Claude`, or deploy. Those are Carter's.

## Where things are written

| what | where | size | who reads it |
|---|---|---|---|
| what was done, in order | `docs/logbook.md`, newest first | 4–5 lines per sweep | Carter, first; an agent at start of session |
| what is known now, and the plan | `docs/findings.md`, rewritten not appended | under ~150 lines | both |
| tables, checks, reasoning | `docs/notes/<date>-<topic>.md` | as long as needed | whoever follows a link |
| every run | the ledger (`experiments/ledger/<sandbox>.csv`) | one row per fold | the harness |
| what ran, exactly | the sweep's report directory (config copy, `*_config.json`, `*_result.json`) | | the harness, and anyone checking a claim |

A logbook entry is **Did / Got / Concluded / Next**, one sentence or
two each, numbers included, and says whether the result matched the
prediction. A failed or pointless experiment gets an entry like any
other. If an entry needs a table it needs a note.

findings.md changes when a conclusion changes, not when a sweep ends.
Most sweeps change the state table and nothing else.

## Git

- Work on a lab branch, `claude/lab-<date>`, created off the branch the
  session was given. Never commit to `Claude` or `main`.
- `vml-queue checkpoint` force-adds what a crash would take with it:
  the ledger shard, sweep summaries, config copies, result records,
  queued configs, the logbook, findings and notes. It refuses to run
  off a `claude/` branch.
- **Lab branches are not merged.** They hold working material. What
  reaches `Claude` goes on a separate `claude/<topic>` branch: code
  and tests, docs, promoted results. `scripts/check_tracked_configs.py`
  names anything else, `--fix` untracks it, and the `pr-hygiene`
  workflow runs the same check on every pull request into `Claude` or
  `main`.
- The agent pushes after every checkpoint. If a push fails, say so in
  the turn's output and try once more after the next sweep.

## The ledger

Runs append to the file named by `VML_RESULTS`, in a sandbox a shard
under `experiments/ledger/`, tracked and pushed with the checkpoint.
Every reader of the ledger reads the local `experiments/results.csv`,
every shard beside it, and the files named in `VML_LEDGER_READ`, each
row once. So trial counts are complete wherever the shards have been
fetched, and nothing has to be merged by hand.

In a clone-mode sandbox the host's ledger is mounted read-only:

```sh
export VML_RESULTS="experiments/ledger/$SANDBOX_VM_ID.csv"
export VML_LEDGER_READ="/run/sandbox/source/experiments/results.csv"
```

## Memory

A forest run over the 16 folds used to need about 18 GB. Every fitted
fold model kept its whole training frame alive through the sample
weights it stored. On 2026-09-28 the harness was changed to copy the
weights and targets. The fold metrics are identical after the fix. The
table gives the peak memory, measured in a 14 GB sandbox:

| run | peak memory |
|---|---|
| 16-fold forest, before the fix | about 18 GB |
| 16-fold forest, after the fix | 6.4–6.7 GB |

A sweep that is killed is resumed by running it again, with
`vml-queue run-next` or `vml-sweep --resume`. The resumed sweep reads
completed runs back from their result records and runs only the rest.

## Setting up (Carter, once)

### 1. A machine user for agents

1. Create a second GitHub account for agents. GitHub allows one
   machine account per person. Give it its own email address.
2. In the repository, open Settings → Collaborators and add the
   account with the **Write** role. Accept the invitation from the machine account.
3. Signed in as the machine account, create a token. Which kind
   depends on who owns the repository. Check GitHub's current
   documentation, because this is as understood in September 2026:
   - **The repository is under your personal account**, which is the
     case today. A fine-grained token cannot reach a repository owned
     by another user. So use Settings → Developer settings → Personal
     access tokens → **Tokens (classic)** with the `repo` scope only.
     The scope is broad, but a token can do no more than its account
     can. The machine account has been invited to this one repository
     with the Write role. Do not tick `workflow`, `admin:*` or
     `delete_repo`.
   - **If you move the repository into an organization**, which is
     free, use a **fine-grained token**. Its resource owner is the
     organization, and its repository access is only
     `value-ml-models`. Its permissions are **Contents: Read and
     write** and **Pull requests: Read and write**, nothing else. This
     is the tighter setup.
   - Either way, set an expiry of 90 days, and a reminder to rotate it.
4. On the host, give the sandbox that token instead of yours:

   ```sh
   sbx secret set github --sandbox <sandbox-name> -t "<the token>"
   ```

   `<sandbox-name>` is `$SANDBOX_VM_ID` inside the sandbox.
5. Inside the sandbox, so commits carry the agent's name and not yours:

   ```sh
   git config user.name  "<machine account name>"
   git config user.email "<machine account email>"
   ```

6. The sandbox proxy injects credentials for HTTPS remotes. `origin`
   is an SSH URL today. Inside the sandbox, if a push fails, switch it:

   ```sh
   git remote set-url origin https://github.com/CarterYancey/value-ml-models.git
   ```

### 2. Branch rules

Settings → Rules → Rulesets → New branch ruleset, twice.

Rulesets on a private repository need a paid plan on a personal
account. Public repositories, and organizations on a paid plan, have
them. If Rulesets is not offered, the older Settings → Branches →
branch protection rules cover the first of the two below.

**Protect the integration branches.** The ruleset targets `main` and
`Claude`. It has these rules:

- Restrict deletions
- Block force pushes
- Require a pull request before merging, with 1 required approval
- Require status checks to pass, and add `tracked-configs` once the
  `pr-hygiene` workflow has run once

The bypass list holds yourself, since nobody else can approve your
own pull requests. The machine account is not on it, so its pull
requests wait for you.

**Keep agents in their namespace.** The ruleset targets all branches,
*excluding* `claude/**`. Its rules are Restrict creations, Restrict
updates and Restrict deletions. The bypass list holds yourself, as
Repository admin. The machine account then can create and push
`claude/**` branches and nothing else. It cannot merge its own pull
request because it cannot approve it.

With both in place the worst an agent can do is make a mess under
`claude/`, which deleting the branches undoes.

### 3. Sandbox resources

The sandbox this was written in has no swap and these resources:

| resource | size |
|---|---|
| cores | 24 |
| memory | 14 GB |
| disk | 20 GB |

After the memory fix a forest run over the 16 folds has the peak
memory in the table under "Memory" above. So 14 GB is enough for one
sweep at a time. About 5 GB of that is the
dataset frame, which is resident before any model is fitted. LightGBM
and XGBoost have not been measured. Two sweeps at once need twice the
memory, so the queue runs one. Keep `n_jobs` at or below the cores
the sandbox really has.

### 4. Starting a session

Run these commands in the sandbox, from the repository root:

```sh
git fetch origin && git checkout -b claude/lab-$(date +%F) origin/Claude
uv sync    # or: uv pip install -e .
uv pip install -e '.[writing]' && uv run python -m spacy download en_core_web_sm   # the writing check that the `writing` skill runs
cat >> /etc/sandbox-persistent.sh <<'EOF'
export VML_RESULTS="experiments/ledger/$SANDBOX_VM_ID.csv"
export VML_LEDGER_READ="/run/sandbox/source/experiments/results.csv"
EOF
vml-queue status
```

Then tell the agent: "Work the queue, following docs/agents.md."
What to read when you come back: `docs/logbook.md`, top down, until
you reach an entry you have seen.

### 5. Bringing results into `Claude`

```sh
git fetch origin
git checkout -b claude/results-<date> origin/Claude
git checkout origin/claude/lab-<date> -- docs/ experiments/ledger/
vml-promote <name> --note "..."        # for each result worth keeping
python scripts/check_tracked_configs.py   # must print "nothing added"
git commit -m "..." && git push -u origin claude/results-<date>
gh pr create --base Claude --fill
```
