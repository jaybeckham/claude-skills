# Claude memory installer (v3.0.0)

Gives Claude Code (and Codex) memory that carries across sessions, plus a short
setup interview so the assistant adapts to you. Needs only Python 3.10+.
No API keys, no packages, no network.

## Install

1. Unzip somewhere permanent, e.g. `~/tools/claude-memory-installer`.
   Keep the folder: `/memory-update` reinstalls from it.
2. `cd` into the project you want memory in.
3. Run (use your own timezone):

   ```sh
   bash ~/tools/claude-memory-installer/setup-memory.sh --timezone America/Chicago
   ```

   Or target a project from anywhere with `--project /path/to/project`.
4. Restart Claude Code in that project.
5. Run **`/get-started`**. It asks about ten questions (your role, the project,
   how you like answers, what needs your approval) and writes `USER.md`,
   `SOUL.md` and `PROJECT.md` from your answers. Rerun it any time.
6. Optional: `/validate-memory` to check the install.

Repeat steps 2-5 per project. Re-running the installer is safe; it never
overwrites your memory files.

## What lives where

- `USER.md`: you. Gitignored, stays on your machine.
- `SOUL.md`, `PROJECT.md`: how the assistant behaves here, and project goals.
  These sit in the project root and can be committed, so in a shared repo the
  interview keeps your personal preferences in `USER.md` instead.
- Memory notes and session logs: `~/.claude/projects/<project>/memory/`.

## Useful commands

`/session-end` (handoff for next time) · `/memory-search` · `/learn` ·
`/curate-memory` · `/get-started`

Windows: run from Git Bash or WSL. Full docs: `docs/memory-system.md`.
