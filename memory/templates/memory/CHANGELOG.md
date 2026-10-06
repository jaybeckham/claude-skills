# Changelog

## 3.0.0

- Local continuity and lexical memory search now work with Python 3.10+ alone. The installer no longer installs packages, creates credentials, deletes legacy servers, or mutates the central semantic runtime. Existing MCP configuration is preserved; `--semantic` registers a configured healthy runtime for both agents with separate project identity and scoped paths.
- Shared Python runtime handles current Codex phase metadata, older channel metadata, and Claude transcripts. Internal reasoning and tool bodies are excluded. Saves lock, write atomically, deduplicate across lifecycle events/retries, and advance cursors after successful writes.
- Hooks work without Git and from subdirectories. Linked worktrees resolve one memory namespace through Git common-directory identity. Startup includes MEMORY.md and recent daily/source-suffixed logs; existing outbox and per-peer subscription semantics remain supported.
- Claude commands get discoverable Codex skill adapters. Existing Claude skills are shared through .agents/skills without duplicating their bodies.
- Upgrades replace only owned hook handlers, preserve unrelated groups/settings, and retain user MEMORY.md, sessions, SOUL.md, USER.md and PROJECT.md. Re-running repairs missing framework files even at the same version. Separate AGENTS.md gets the same managed instructions without replacing its other content.
- Hook timeouts use seconds; Codex saves on PreCompact, Stop, SessionEnd (all reasons), and Interrupt, and reloads on startup/resume/clear/compact. New definitions require normal project/hook trust review; installation never grants trust.
- Optional `--skills-from` and `--link-wiki` make local writing/project setup repeatable without importing unrelated tools.

## 2.4.0

- **Cross-project reads are now per-peer, not all-or-nothing.** `.shared_memory` stays the OUTBOX (publish under this name); a new `.shared_memory_subscribe` is the INBOX — one peer project name per line, `#` comments allowed. Publishing used to imply subscribing to the entire ledger, so a project read every other repo's session excerpts plus its own posts echoed straight back, every startup. A project also no longer reads its own outbox name, and a subscription must be a bare directory name (entries containing `/` or starting with `.` are rejected).
- **BREAKING for existing installs:** the inbox is deliberately not seeded, so after upgrading, a project reads nothing cross-project until you create `<memory-dir>/.shared_memory_subscribe`. That is the intended default — declare only the peers whose context you actually want.
- Ported into both the Claude and Codex `session-start-load.sh`.

## 2.3.0

- **Memory dir now resolves to the path Claude Code actually uses.** Claude Code slugifies a project path by replacing every non-alphanumeric character with a dash, so `/Users/me/Development/my_app` lives in `-Users-me-Development-my-app`. The installer and all four Claude hooks only replaced `/`, which stranded memory in a sibling dir Claude Code never reads — a split brain for any project with `_` or `.` in its path. Both now prefer an existing dir on the old spelling (so already-installed projects keep their data) and otherwise use the slug. Codex hooks got the same fix.
- **`settings.json.template` now wires the `/clear` hook.** Fresh installs shipped `session-end-clear.sh` but only registered three of the four hooks, so `/clear` silently discarded the conversation instead of saving it. Projects installed over an existing `settings.json` were unaffected (the jq merge already added it).
- **`AGENTS.md` is now symlinked to `CLAUDE.md`** on install, matching the convention already used in ClaudeBot, outreach-ai, and creator-finder-v2. Codex reads `AGENTS.md`, and since 2.2.0 this installer drops Codex hooks — without the symlink those repos got Codex session-saving with no instructions behind it. An existing symlink or a real `AGENTS.md` file is left untouched.
- **Dropped the inverted "underscore→hyphen bug" migration** in `setup-memory.sh`. Its premise was backwards: it copied data *away* from the slug path Claude Code uses. Path probing now handles every case.

## 2.2.0

- **`shared_memory` read is now opt-in** (matches the existing opt-in write semantics): `session-start-load.sh` only loads cross-project posts from `~/.claudebot/shared_memory/` if `<project>/memory/.shared_memory` exists. Previously the read was unconditional, so a fresh project not participating in the shared ledger would still pull every other project's posts at session start — pure noise. Drop a `memory/.shared_memory` file containing the project name to opt in to bidirectional cross-project sync.
- **Codex hooks now ship from this template** under `templates/memory/codex/`. `setup-memory.sh` installs `.codex/hooks/{session-start-load,session-end-save}.sh` + `.codex/hooks.json` alongside the existing `.claude/hooks/`. Both Claude Code and Codex sessions auto-load and auto-save against the same `memory/sessions/` dir; cross-project sync also follows the same `.shared_memory` opt-in.
- **Known: per-project copies installed before 2.2.0 still have the old unconditional read.** They're benign for participating projects (since they DO have `.shared_memory`) but technically still buggy. Re-run `setup-memory.sh` in any spoke to refresh hooks from the now-fixed template.

## 2.1.0

- **User message truncation**: 300 -> 1500 chars (preserves context that was being lost)
- **Session load budgets**: Yesterday 3k -> 5k, Today 6k -> 10k chars (richer startup context)
- **Code fence fix**: All save hooks now close unclosed code fences from mid-block truncation
- **SOUL.md + USER.md**: Now created on fresh install (personality + user prefs persistence)

## 2.0.0

- **New hooks**: SessionStart (auto-load session context), SessionEnd (save on /clear)
- **CLAUDE.md injection**: Setup appends Memory System section to project's CLAUDE.md
- **MEMORY.md migration**: Adds Key Paths section if missing from existing installs
- **Centralized MCP server**: Uses `claude-memory/` in ClaudeBot repo instead of per-project `memory-search-mcp/`
- **`.env` management**: Creates and manages `claude-memory/.env` for embedding provider config
- **Dependency verification**: Full import verification for all MCP server dependencies
- **Smarter settings.json merging**: Detects existing hook configs before adding new ones
- **`/memory-update` command**: Now runs setup-memory.sh directly (no manual steps)

## 1.1.0

- Initial template-based installation
- PreCompact and Stop hooks
- Per-project MCP server at `memory-search-mcp/`
- VERSION tracking and changelog display on update
