# Get Started

Interview the user so the assistant adapts to them, then write what you learned into the memory files. Run this on a fresh install, or again whenever the user wants to change how the assistant works with them.

## Before asking anything

1. Read `USER.md`, `SOUL.md` and `PROJECT.md` in the project root, and `MEMORY.md` in the directory returned by `python3 .agents/memory/project_memory.py path`.
2. If they are still blank templates, run the full interview. If they already hold answers, summarize what is there in a few lines and ask what has changed; only interview on those parts.
3. Look around the project briefly (README, package files, top-level folders) so you can ask informed questions instead of generic ones, and can propose answers the user just confirms.

## The interview

Ask **one question at a time**. Use AskUserQuestion when it is available (offer 2-4 likely answers, the user can always type their own); otherwise ask in plain text. Keep it to about ten questions. Skip any question the user has already answered or the project makes obvious, and follow up when an answer opens something worth knowing ("I'm new to this codebase" → which parts they'll touch first).

Cover these, in roughly this order:

1. **Name and how to address them**, and their pronouns if they want to share them (optional; use they/them otherwise).
2. **Role and team**: what they do, and who they hand work to or receive it from.
3. **What this project is** and what they are trying to get done in it over the next few weeks.
4. **Experience**: with this codebase, with the language/stack, and with AI coding assistants. This sets how much you explain.
5. **Answer style**: short and direct, or detailed with reasoning; code first or explanation first.
6. **Autonomy**: should you just make changes, propose first and wait, or decide by size of change? What always needs their approval (commits, pushes, deleting files, running migrations, anything outside the repo)?
7. **Tone**: casual, neutral or formal; humor welcome or not.
8. **Working rules**: conventions to follow (tests, linting, branch names, ticket IDs in commits, review process), and the tools they use (issue tracker, CI, docs).
9. **Hard nos**: anything you must never do or say, and topics that are off-limits.
10. **Is this repo shared with teammates?** This decides where their personal preferences are stored (see below).

Stay on work. Do not ask about family, health, finances, or anything a manager or teammate wouldn't expect a work tool to know. If the user volunteers something personal, keep only what helps you do the work.

## Write the files

Show the user a short summary of what you'll write and get a yes before writing.

- **`USER.md`** (gitignored, private to this machine): name, address, pronouns if given, timezone, role, team, experience, and their personal preferences (answer style, tone, autonomy, approvals, hard nos).
- **`SOUL.md`**: how the assistant behaves in this project. Keep the Core Truths, and rewrite Vibe and Boundaries from their answers. **If the repo is shared**, keep SOUL.md to team-wide behavior only; their personal preferences stay in USER.md, so a teammate's install isn't shaped by one person's answers.
- **`PROJECT.md`**: overview, current goals as Next Actions, and the working rules and tools from question 8.
- **`MEMORY.md`**: add one line under Critical reminders pointing at the hard nos and approval rules, so they load every session.

Keep each file short and in plain language; these are instructions you will read every session. Never copy in secrets, credentials, customer data or other people's personal details.

## Finish

Tell the user which files you wrote, that they can edit them directly any time, and that `/get-started` can be rerun to change anything. Then apply the new preferences from your very next reply.
