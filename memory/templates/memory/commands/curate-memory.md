# Curate Memory -- Promote Session Learnings to Permanent Memory

First resolve this host's memory directory by running `python3 .agents/memory/project_memory.py path` from the active project root. Replace MEMORY_DIR below with the returned path.

Review recent session logs and promote durable learnings into permanent topic-based memory files. This keeps long-term memory accurate and up to date without manual effort.

## Step 1: Gather recent session logs

Read all files from the last 7 days in:

```
MEMORY_DIR/sessions/
```

Look for files matching these patterns:
- `YYYY-MM-DD.md` -- daily session logs
- `compaction-*.md` -- compacted conversation context
- `session-end-*.md` -- end-of-session summaries

If the sessions directory does not exist or contains no files from the last 7 days, report that and stop.

## Step 2: Extract durable learnings

For each session log, identify information worth remembering permanently. Look for:

- **API gotchas and workarounds** -- unexpected behavior, required parameters, error messages and fixes
- **Bug patterns and fixes** -- recurring issues and their solutions
- **Configuration quirks** -- settings that must be a certain way, non-obvious defaults
- **Workflow patterns** -- approaches that worked or failed
- **Tool usage tips** -- tool behavior, parameter gotchas, output limits
- **Architecture decisions** -- choices made and their rationale
- **Instance IDs and references** -- resource IDs, URLs, credential names
- **Integration notes** -- service-specific behavior

Skip anything that is:
- Purely session-specific (e.g., "activated feature X for client Y")
- Already a well-known fact
- Temporary status (e.g., "service is currently down")

## Step 3: Read existing topic memory files

Read all topic memory files that exist in `MEMORY_DIR/`. These are the canonical locations for permanent knowledge.

If a file does not exist yet, that is fine -- it will be created if needed.

## Step 4: Deduplicate against existing knowledge

For each extracted learning, check:

1. Does it already exist in one of the topic files? If yes, skip it (unless the session log has a more accurate or complete version -- in that case, update the existing entry).
2. Does it already exist in `MEMORY.md`? Learnings in MEMORY.md are fine to also have in topic files (topic files are the detailed version), but do not create duplicates within topic files.

## Step 5: Promote new learnings

For each new learning:

1. Determine the best topic file. If none of the existing categories fit, create a new topic file with a descriptive name (e.g., `api-notes.md`, `patterns.md`).
2. If the topic file does not exist, create it with a heading that describes its purpose:
   ```markdown
   # [Topic Name]

   [One-line description of what this file tracks.]

   - **Learning 1**: Description of the learning
   ```
3. If the topic file exists, append the new learning as a bullet point using the same format as existing entries (typically `- **Bold label**: Description`).
4. Keep entries concise but complete -- include enough context that a future session can understand and apply the learning without the original session log.

## Step 6: Clean up outdated entries

Review ALL entries in each topic file you touched (or all topic files if doing a full review). Remove or update entries that are:

- **Outdated** -- superseded by newer information from recent sessions
- **Incorrect** -- proven wrong by subsequent experience
- **Redundant** -- duplicated across files or within a file
- **No longer relevant** -- about features, workflows, or systems that no longer exist

When removing an entry, do not leave a "removed" marker -- just delete it cleanly.

## Step 7: Update MEMORY.md index

Check that `MEMORY.md` has references to all topic files that exist. The references should appear in a section that lists topic files. If a new topic file was created in Step 5, add a reference to it in MEMORY.md.

**Important**: Keep MEMORY.md under 200 lines. If adding references would push it over, consider whether any existing MEMORY.md content could be moved into a topic file instead.

## Step 8: Report summary

Output a clear summary of what was done:

```markdown
## Memory Curation Summary

### Sessions reviewed
- List each session file reviewed with its date

### New learnings promoted
- List each new learning added, which topic file it went to, and a one-line summary

### Entries updated
- List any existing entries that were updated with more accurate information

### Entries removed
- List any outdated or incorrect entries that were removed, with brief reason

### Topic files created
- List any new topic files that were created

### No changes needed
- If nothing was promoted, updated, or removed, say so explicitly
```

## Important

- This command is **additive and corrective** -- it promotes new knowledge and cleans up stale knowledge. It should never delete session logs.
- Do not modify session log files in the `sessions/` directory.
- Do not modify `PROJECT.md`, `CLAUDE.md`, or any other project files.
- Only modify files in the memory directory: `MEMORY_DIR/`
- If MEMORY.md is getting bloated (approaching 200 lines), proactively move detailed entries from MEMORY.md into the appropriate topic files, leaving only a brief reference in MEMORY.md.
