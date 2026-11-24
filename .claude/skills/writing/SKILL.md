---
name: writing
description: Use before writing or editing anything a person will read in this repository - docs/*.md, findings.md, a note, the decision log, a TODO item, a logbook entry, a promote note, a commit message, and every reply to Carter. Do not use it while reading code, debugging, planning an experiment or reasoning about results. It gives the vocabulary, the sentence rules, the examples Carter rejected, and the check a draft must pass.
---

# Writing for Carter

Carter reads this repository's records after weeks away. On 2026-11-24
Carter called findings.md and the logbook "almost unreadable". The same
day, after a first set of written rules was in place, Carter called a
closing message unreadable in the same way. The failures were not jargon.
They were sentences without a verb, shorthand coined on the spot,
aphorisms, and clauses hidden in parentheses. This skill is the
procedure that stops them. It applies to prose only. Code, configs,
tool calls and your own reasoning are not its business.

## The procedure, every time

1. Write the draft.
2. Run the check on it. A file goes through `uv run vml-writing <file>`.
   A reply or a logbook field goes through `uv run vml-writing --text`
   on stdin. The command exits 1 while an error remains.
3. Fix every error. Read the warnings and fix the ones you can.
4. Save the file, or send the reply, only after the check passes.

`vml-logbook add` and `vml-promote --note` run the check themselves and
refuse text that fails it. Without spaCy installed the check skips the
verb and noun-stack rules and says so. Install it with
`uv pip install -e '.[writing]'` and
`uv run python -m spacy download en_core_web_sm`.

## The vocabulary

[GLOSSARY.md](../../../GLOSSARY.md) holds one term per concept and the
words to avoid for it. Use its terms exactly, and never a synonym or a
paraphrase. A precise term the reader can look up beats a plain
substitute: write "selection-biased", and look up what its entry says
to avoid. When a document needs a concept the glossary lacks, add the
entry in the same change and do not define the term inline.

`docs/writing_denylist.toml` lists the phrases Carter has objected to,
with the date and the quote. The check refuses every one of them. When
Carter objects to a phrase, add it there the same day. Never remove an
entry.

## The sentence rules

The check enforces these. The rules come from Simplified Technical
English, structural rules only.

| rule | write | do not write |
|---|---|---|
| Every sentence has a subject and a finite verb. | "I refit the three legs on dataset_v1.4.1." | "Three legs refit, two screens, three backtests." |
| At most 25 words in a sentence. One idea per sentence. | two sentences | one sentence with "and ... and ..., with ..." |
| No semicolon. | a full stop | "the top 20 met it 65%; the top 50, 73%" |
| No clause in parentheses. A decision number, a seed, a date or a file name may stand in parentheses. | "Carter reads this as a bubble." | "(Carter's reading)" |
| At most two measurements in a sentence. Three or more go in a table. | a table with a header row | "+0.046 / +0.059 / −0.016 for 2005–12 / 2013–20 / 2021–23" |
| No phrase from the denylist. | "by final value" | "in money" |
| No aphorism. Say what was measured, then what it means. | "The picks lead their same-size peers by the same margin with or without the filter, so the extra return comes from the larger stocks themselves." | "The gain is the band, not the selection." |
| No gendered pronoun for anyone here. | "Carter", "they" | "he", "his" |
| No dash between clauses. | two sentences, or a comma | "the filter earned more — on all three seeds" |
| A list item that completes a sentence ending in a colon needs no verb. Any other list item is a sentence. | "- Carter decides on the larger-half filter." | "- Larger-half filter for Carter" |

Passive voice and four nouns in a row are warnings. Prefer the active
voice and say who did it.

## Rules the check cannot apply

- Record a person's view in their own words. Carter's view of 2021–26
  is "a bubble that deflates". "The index's largest members stop
  leading" was my mechanism for that view, and Carter called it
  inaccurate.
- Keep every hedge and qualifier. A shorter sentence that turns "may"
  into "is" states a different claim.
- Say what was measured as fact and what it might mean as a hypothesis,
  in separate sentences.
- Copy every number, count and column name from the ledger or the
  report. Never write one from memory.
- Numbers go in a table. A sequence of three or more steps or
  conditions goes in a list.
- A bold lead-in to a paragraph or a list item is a sentence with a
  verb. "**The seeds confirm the gap.**" is one. "**Readings.**" is a
  label and is not.

## Replies to Carter

A reply follows the same rules, and these as well:

- Lead with the outcome. Say first what was found or done, then what
  Carter has to decide, then what is left.
- Name the files and branches Carter must open. Keep code and command
  lines in fenced blocks.
- Say who decides what: "Carter decides what is bought", and never
  "what is bought is yours".
- Progress lines during a task are prose too. "Building the checker
  now." is a fragment. "I am building the checker now." is a sentence.
- Do not quote a denylisted phrase in a reply. Describe the habit
  instead, or point to the denylist entry.

## Examples Carter rejected, and the rewrite

| rejected on 2026-11-24 | rewrite |
|---|---|
| "The size band in money." | "The size band, read by final value." |
| "The picture is unchanged in kind." | "The shape of the record is the same on v1.4.1: ahead of SPY through 2020, behind by August 2026." |
| "Not carried forward on money." | "I did not carry it forward, because the final value did not improve." |
| "What is bought is yours." | "Carter decides what is bought." |
| "Kept short on purpose:" | delete it, or "This section is short because the tables are in the note." |
| "(20 looks; the counts are part of every holdout number)" | "The holdout has been looked at 20 times. The look count is part of every holdout number." |
| "the money was the same as the candidate's, but 4 points fewer buys lost money" | "The final value was the same as the candidate's. Four points fewer of the buys lost money." |

What is not fixed by any rule here: a hollow paragraph in full
sentences is still hollow. If there is nothing to say, say nothing.
