# Setting up agent sessions

This file is for Carter. It covers what to set up once so that an agent
can run experiments in a sandbox, how to start a session, and how to
bring a session's results into `Claude`. How the agent itself works is
in [agents.md](agents.md).

## 1. A machine user for agents

1. Create a second GitHub account for agents. GitHub allows one machine
   account per person. Give it its own email address.
2. In the repository, open Settings, then Collaborators, and add the
   account with the **Write** role. Accept the invitation from the
   machine account.
3. Signed in as the machine account, create a token. The kind depends
   on who owns the repository. (Check GitHub's current documentation;
   this is how it was understood in September 2026.)
   - **The repository is under your personal account** (the case
     today). A fine-grained token cannot reach a repository owned by
     another user, so use Settings, Developer settings, Personal access
     tokens, **Tokens (classic)**, with the `repo` scope only. The scope
     is broad, but a token can do no more than its account can, and the
     machine account has the Write role on this one repository. Do not
     tick `workflow`, `admin:*` or `delete_repo`.
   - **If you move the repository into an organization** (free). Use a
     **fine-grained token** whose resource owner is the organization,
     with repository access to `value-ml-models` only and two
     permissions: **Contents: Read and write** and **Pull requests:
     Read and write**. This is the tighter setup.
   - In either case, set an expiry of 90 days and a reminder to rotate
     the token.
4. On the host, give the sandbox that token instead of yours:

   ```sh
   sbx secret set github --sandbox <sandbox-name> -t "<the token>"
   ```

   `<sandbox-name>` is the value of `$SANDBOX_VM_ID` inside the sandbox.
5. Inside the sandbox, set the commit author, so commits carry the
   agent's name and not yours:

   ```sh
   git config user.name  "<machine account name>"
   git config user.email "<machine account email>"
   ```

6. The sandbox proxy adds credentials to HTTPS remotes. `origin` is an
   SSH URL today. If a push fails inside the sandbox, switch it:

   ```sh
   git remote set-url origin https://github.com/CarterYancey/value-ml-models.git
   ```

## 2. Branch rules

Open Settings, Rules, Rulesets, New branch ruleset, and create two
rulesets. Rulesets on a private repository need a paid plan on a
personal account. If Rulesets is not offered, the older branch
protection rules (Settings, Branches) can cover the first of the two.

**Protect the integration branches.** Target `main` and `Claude`.
Turn on: restrict deletions; block force pushes; require a pull request
before merging, with one required approval; require status checks to
pass, adding `tracked-configs` once the `pr-hygiene` workflow has run
once. Put yourself on the bypass list, since nobody else can approve
your pull requests. The machine account is not on the list, so its pull
requests wait for you.

**Keep agents in their own branch names.** Target all branches except
`claude/**`. Turn on: restrict creations, restrict updates, restrict
deletions. Put yourself (Repository admin) on the bypass list. The
machine account can then create and push `claude/**` branches and
nothing else, and it cannot merge its own pull request because it
cannot approve it.

With both rulesets in place, the worst an agent can do is leave a mess
of `claude/` branches, which deleting them undoes.

## 3. Sandbox size

The sandbox these sessions run in has 24 cores, 14 GB of memory, no
swap and a 20 GB disk. That fits one heavy job at a time. About 5 GB of
it is the dataset frame, which is loaded before any model is fitted. A
16-fold forest run peaks at about 6.5 GB, and a backtest on
`dataset_v1.5.1` at up to 13.8 GB. A larger sandbox would let two jobs
run at once; the queue runs one either way.

## 4. Starting a session

In the sandbox, from the repository root:

```sh
uv sync                       # or: uv pip install -e .
uv run vml-queue new-lab      # creates claude/lab-<today> from origin/Claude
cat >> /etc/sandbox-persistent.sh <<'EOF'
export VML_RESULTS="experiments/ledger/$SANDBOX_VM_ID.csv"
export VML_LEDGER_READ="/run/sandbox/source/experiments/results.csv"
EOF
uv run vml-queue status
```

Then tell the agent which way of working you want (agents.md, "Two
ways of working"):

- "Work the queue, following docs/agents.md." The agent runs what the
  queue holds and stops at the first surprise.
- "Do whatever is best to reach the goal." The agent may open new
  directions, as long as it logs every decision first. This has been
  the standing arrangement since 2026-10-01.

## 5. When you come back

Read in this order:

1. `docs/logbook.md`, from the top down, until you reach an entry you
   have seen.
2. `docs/next-steps.md`. Its section "Waiting on Carter" lists what
   needs your answer.
3. The decisions the session added to the decision log (the newest
   `docs/notes/*-decisions.md` file), if any need your review.

## 6. Bringing results into `Claude`

At the end of a session the agent builds a branch named
`claude/results-<date>` that carries the docs, code, promoted results
and ledger shard, and that passes `scripts/check_tracked_configs.py`.
You open the pull request from it:

```sh
gh pr create --base Claude --head claude/results-<date> --fill
```

Things only you do: merge into `Claude` or `main`, take a look at the
sealed holdout, deploy, and decide on anything listed under "Waiting on
Carter" in `docs/next-steps.md`. After the merge, the next session
archives the session's lab branch (agents.md, "Git").
