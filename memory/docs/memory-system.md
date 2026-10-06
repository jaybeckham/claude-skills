# Shared Claude and Codex memory

From the project folder, run:

```sh
bash /path/to/claude-memory-installer/setup-memory.sh
```

Python 3.10+ is the only dependency for local continuity and lexical search.
No packages, external credentials, or semantic service are needed. The installer
works in a Git repository, linked worktree, or ordinary folder, including paths
with spaces. Use `--project /path/to/project` to specify a different destination.

Claude and Codex share one native Claude project-memory namespace. Git worktrees
use the main checkout identity; existing legacy namespaces and user memory are
preserved. Framework code and configuration live in `.agents/memory/`.
Old Writing-style memory directory aliases migrate to a real framework directory,
with compatibility links to the original memory files and sessions. Existing
timezone settings carry forward.

```sh
python3 .agents/memory/project_memory.py path
python3 .agents/memory/project_memory.py search "past decision" -n 10
python3 .agents/memory/project_memory.py validate
```

Search returns source paths and line numbers. Read those sources before answering
from recall. This is lexical search; it does not imply semantic similarity.

## Skills, commands, and wiki links

The installer shares existing `.claude/skills` with Codex through `.agents/skills`.
Existing independent registries or inverse symlinks are preserved. Each template
command gets a matching Codex `$name` skill adapter pointing to the canonical
Claude `.claude/commands/name.md` body. Custom colliding skills are retained and
reported instead of overwritten.

Commands include `session-end`, `curate-memory`, `memory-search`, `memory-get`,
`memory-save`, `memory-management`, `memory-style`, `learn`, `validate-memory`,
`memory-update`, and `get-started` (setup interview). Claude uses
`/name`; Codex uses `$name`. Installation does not start channel setup or send
messages.

Optional imports keep source selection explicit:

```sh
bash /path/to/claude-memory-installer/setup-memory.sh \
  --skills-from /path/to/selected/skill-or-collection \
  --link-wiki --timezone America/Chicago
```

`--skills-from` copies complete immediate skill packages and supporting files
without replacing existing skills; repeat the flag for more collections.
`--link-wiki` links ClaudeBot's live wiki only when the destination has no wiki.
Existing wiki content stays in place. Linked pages retain their original owners;
read them as reference and edit only within the user's requested scope.

## Hooks and activation

Both agents receive SessionStart, PreCompact, Stop, and SessionEnd handlers.
Codex also receives Interrupt; startup reloads cover resume, clear, and compact.
Stop is a completed-turn save, not just a session-close event. The structured
`session-end` command adds a concise handoff beyond the automatic visible excerpts.

Saving uses locks, atomic replacement, durable-write-before-cursor ordering, and
retry markers. Current Codex phase metadata and older channel metadata are
supported alongside Claude transcripts. Internal reasoning, tool payloads and
injected agent/environment context are excluded. Startup reads MEMORY.md and
recent daily/source-suffixed logs with a bounded context budget. Set an IANA
timezone with `--timezone`; otherwise dates follow the local system timezone.

After installation, resume/restart to load updated startup context. In Codex,
trust the project if needed, then review and trust new or changed definitions in
`/hooks`. The installer does not write global trust or bypass review. `skills/list`
and `hooks/list` establish discovery and trust; actual event execution is a
separate check. Existing disabled settings and managed policy still apply.
The installer creates a minimal `.codex/config.toml` when none exists so Codex
discovers the project hook layer; existing project configuration stays intact.

## Upgrades and optional services

Re-run setup to upgrade or repair missing framework files. The legacy `--force`
flag remains accepted, but repeated plain installs also repair. Managed instruction
sections and owned hook handlers are updated; unrelated handlers, configuration,
and user memory, sessions, PROJECT.md, SOUL.md, and USER.md are retained. An existing
real AGENTS.md receives the same managed section without replacing its other text.

No legacy server directory or central `.env` is deleted or rewritten. Existing
semantic MCP settings are left alone by a local install. To register ClaudeBot's
already configured, healthy semantic runtime in both agents, opt in:

```sh
bash /path/to/claude-memory-installer/setup-memory.sh --semantic
```

This reuses `claude-memory/.venv` and its configured credentials. Each destination
gets a distinct stable project identity, its own MEMORY_DIR, and cleared inherited
EXTRA_PATHS/JSONL_DIR. Semantic search indexes memory text in Supabase and may send
text to the configured embedding provider. Missing runtime dependencies produce
an actionable failure; the installer never silently installs packages or claims
semantic search is working. Custom preexisting Codex memory-search TOML should be
migrated explicitly rather than overwritten.

Cross-project publication remains opt-in via `<memory-dir>/.shared_memory`.
Subscriptions remain opt-in per peer via `.shared_memory_subscribe`; new installs
enable neither automatically. Existing flags are preserved. Bare peer names are
validated and a project never reads its own outbox back as peer context.

## Template verification

```sh
python3 -m unittest discover -s tests -v
bash -n setup-memory.sh
```

Fixtures use temporary homes/projects and do not seed live memory or grant trust.
The suite covers fresh installs, same-version repair, upgrades, settings/data
preservation, actual configured-handler roundtrips, difficult paths, registry and
wiki links, worktree identity, semantic project isolation, and save failure/retry
behavior. CI runs these tests on Linux and macOS with supported Python versions.
