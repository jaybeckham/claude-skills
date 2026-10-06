#!/usr/bin/env bash
# Copy every skill in this repo into ~/.claude/skills. Existing skills with the same name are kept.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$DEST"
installed=0 kept=0
while IFS= read -r skill_md; do
    dir="$(dirname "$skill_md")"
    name="$(basename "$dir")"
    if [ -e "$DEST/$name" ]; then
        echo "kept existing: $name"
        kept=$((kept + 1))
        continue
    fi
    cp -R "$dir" "$DEST/$name"
    installed=$((installed + 1))
done < <(find "$ROOT/skills" "$ROOT/third_party" -name SKILL.md -not -path '*/node_modules/*' | sort)
echo "Installed $installed skills into $DEST ($kept already present). Restart Claude Code to load them."
