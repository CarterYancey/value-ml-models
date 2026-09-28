# Unattended sessions

How an agent runs experiments on its own in a sandbox, and what Carter
sets up once so that it can. The rules in CLAUDE.md all apply; this file
adds the ones that only matter when nobody is watching.

## The loop

One turn per finished sweep. Nothing in between.

1. **Start of session.** Read [logbook.md](logbook.md), then
   [findings.md](findings.md). `vml-logbook unread` lists sweeps that
   ended with nobody reading them: those come first. `vml-queue status`
   says what is next.
2. **Launch** the next sweep as a background command and end the turn:

   ```sh
   vml-queue run-next --push
   ```

   It runs the first queue item that is not done (resuming it if it was
   interrupted), writes a **not yet read** logbook entry from the facts,
   commits a checkpoint, pushes, and exits. The exit wakes the agent.
3. **Do not poll.** No progress checks, no sleeping loops, no "still
   running" turns. If a fallback wake-up is set, one per sweep, at
   least twice the sweep's expected duration, and its only job is to
   notice a hung process.
4. **Read** the summary when woken. Era table before the pooled
   number. Compare with the predictions written in the config.
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

Stop and leave a logbook entry saying why, instead of launching the
next item, when:

- the queue is empty. An agent extends the queue only with items the
  plan in findings.md already names; a new direction is Carter's;
- a result contradicts the prediction written in its config. The
  surprise gets a note with rival explanations, and the next
  experiment is the one that separates them, proposed, not run;
- a result is far above its baseline (leakage first) or far below an
  earlier one (a changed input first);
- a run failed for a reason that is not understood;
- a checkpoint could not be pushed twice in a row: work that cannot
  leave the sandbox is work that can be lost;
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
- Push after every checkpoint. If a push fails, say so in the turn's
  output and try once more after the next sweep.

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

A 16-fold forest run used to need about 18 GB: every fitted fold model
kept its whole training frame alive through the sample weights it
stored. Fixed 2026-09-28 (weights and targets are copied). See the
logbook for the measured footprint since. A sweep that is killed is
resumed by running it again (`vml-queue run-next`, or
`vml-sweep --resume`): completed runs are read back from their result
records and only the rest is run.

## Setting up (Carter, once)

### 1. A machine user for agents

1. Create a second GitHub account for agents (GitHub allows one
   machine account per person). Give it its own email address.
2. In the repository: Settings → Collaborators → add the account with
   the **Write** role. Accept the invitation from the machine account.
3. Signed in as the machine account, create a token. Which kind
   depends on who owns the repository (check GitHub's current
   documentation; this is as understood in September 2026):
   - **The repository is under your personal account** (today): a
     fine-grained token cannot reach a repository owned by another
     user, so use Settings → Developer settings → Personal access
     tokens → **Tokens (classic)** with the `repo` scope only. The
     scope is broad, but a token can do no more than its account can,
     and the machine account has been invited to this one repository
     with the Write role. Do not tick `workflow`, `admin:*` or
     `delete_repo`.
   - **If you move the repository into an organization** (free): use a
     **fine-grained token**, resource owner the organization,
     repository access only `value-ml-models`, permissions
     **Contents: Read and write** and **Pull requests: Read and
     write**, nothing else. This is the tighter setup.
   - Either way: an expiry of 90 days, and a reminder to rotate it.
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
   is an SSH URL today; inside the sandbox, if a push fails:

   ```sh
   git remote set-url origin https://github.com/CarterYancey/value-ml-models.git
   ```

### 2. Branch rules

Settings → Rules → Rulesets → New branch ruleset, twice.

Rulesets on a private repository need a paid plan on a personal
account (public repositories and organizations on a paid plan have
them); if Rulesets is not offered, the older Settings → Branches →
branch protection rules cover the first of the two below.

**Protect the integration branches.** Target: `main` and `Claude`.
Rules: Restrict deletions; Block force pushes; Require a pull request
before merging (required approvals: 1); Require status checks to pass
→ add `tracked-configs` once the `pr-hygiene` workflow has run once.
Bypass list: yourself, since nobody else can approve your own pull
requests. The machine account is not on it, so its pull requests wait
for you.

**Keep agents in their namespace.** Target: all branches, *excluding*
`claude/**`. Rules: Restrict creations, Restrict updates, Restrict
deletions. Bypass list: yourself (Repository admin). The machine
account then can create and push `claude/**` branches and nothing
else, and cannot merge its own pull request because it cannot approve
it.

With both in place the worst an agent can do is make a mess under
`claude/`, which deleting the branches undoes.

### 3. Sandbox resources

The sandbox this was written in has 24 cores, 14 GB of memory, no swap
and a 20 GB disk. After the memory fix a forest run fits; check the
logbook entry for the number before sizing. Leave headroom for the
dataset frame (about 5 GB resident before any model is fitted), and
keep `n_jobs` at or below the cores the sandbox really has.

### 4. Starting a session

In the sandbox, from the repository root:

```sh
git fetch origin && git checkout -b claude/lab-$(date +%F) origin/Claude
uv sync    # or: uv pip install -e .
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
