# End-of-Session Summary

Resolve the current host's memory directory from the active project root:

```sh
python3 .agents/memory/project_memory.py path
```

Read today's session log in that directory's `sessions/`. Use the configured
project timezone (or system local timezone) for YYYY-MM-DD and HH:MM. Append a
structured entry; preserve existing log contents.

```markdown
## Session -- HH:MM

### What was worked on
- Tasks, drafts, or investigations and their outcomes.

### Key decisions
- Supported decisions and rationale, or None.

### Problems encountered and solutions
- What failed and how it was resolved, or None.

### Current state
- What is complete, in progress, or blocked.

### Next actions
- Concrete next steps.
```

If the daily log is absent, create it with `# Sessions -- YYYY-MM-DD`. Separate
new entries with `---`. Promote supported durable lessons to topic files and
update MEMORY.md's index when needed; keep MEMORY.md under 200 lines.

Update PROJECT.md's Implementation Status only if project status materially
changed. Keep task lists/next actions in the session log or configured board.
Sync a configured task board only within existing user authorization. Confirm
which files were saved and give the user the concise handoff.
