# claude-skills

Skills and setup I use with Claude Code.

## What's here

| Folder | What it does |
|---|---|
| [`memory/`](memory/) | Memory that carries across Claude Code (and Codex) sessions, plus a `/get-started` interview that adapts the assistant to you. Python 3.10+, no keys, no network. |
| [`skills/product-frontend-design/`](skills/product-frontend-design/) | Review and design product sites and app UIs: five-second clarity, one CTA per view, hierarchy, then distinctive, non-generic visuals. |

## Install

```sh
git clone https://github.com/jaybeckham/claude-skills.git ~/tools/claude-skills
```

**Memory**, per project:

```sh
cd /path/to/your/project
bash ~/tools/claude-skills/memory/setup-memory.sh --timezone America/Chicago
```

Restart Claude Code, then run `/get-started`. Details in [`memory/README.md`](memory/README.md).

**Skills**, for every project:

```sh
mkdir -p ~/.claude/skills
cp -R ~/tools/claude-skills/skills/* ~/.claude/skills/
```

Or copy a skill folder into a single project's `.claude/skills/`.

## Credits

`product-frontend-design` adapts parts of Anthropic's
[frontend-design](https://github.com/anthropics/skills) skill (Apache 2.0); see its `NOTICE`.
