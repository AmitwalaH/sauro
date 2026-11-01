# For Claude Code

Read, in this order, before doing anything:

1. `METHOD.md`. How work is done here. It never bends.
2. `PROJECT.md`. Where the project is. Stack, layout, check suite, frozen things, off-limits,
   and the only conditions under which you may commit.
3. The open task file in `tasks/`. The newest one by date. It holds the goal, the latest
   handoff, what is off-limits today, and what "done" means.

Then run the check suite from `PROJECT.md` before touching anything and record what is already
red.

Stop and wait at the three checkpoints: after the plan (Step 4), whenever you do not understand
something (rule 6), and at the report (Step 12).

Never commit to `main`. Never push. Never edit `bench/baseline.json`, a fixture marked
`reviewed: true`, or `bench/LABELING.md` once task 1 is approved. Never label a fixture with a
model, including yourself.

Writing style in every file and message: plain, short sentences, no em dashes.
