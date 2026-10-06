# claude-skills

Skills and setup I use with Claude Code.

## What's here

| Folder | What it does |
|---|---|
| [`memory/`](memory/) | Memory that carries across Claude Code (and Codex) sessions, plus a `/get-started` interview that adapts the assistant to you. Python 3.10+, no keys, no network. |
| [`skills/product-frontend-design/`](skills/product-frontend-design/) | Review and design product sites and app UIs: five-second clarity, one CTA per view, hierarchy, then distinctive, non-generic visuals. |
| [`third_party/superpowers/`](third_party/) | Brainstorming, writing and executing plans, TDD, systematic debugging, code review, worktrees (MIT, obra/superpowers). |
| [`third_party/skill-creator/`](third_party/) | Anthropic's skill for building and testing new skills (Apache 2.0). |

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

**Skills**, for every project (no plugin marketplace needed):

```sh
bash ~/tools/claude-skills/install.sh
```

It copies every skill into `~/.claude/skills/` and never overwrites one you already have.
Restart Claude Code afterwards. Or copy a single skill folder into a project's `.claude/skills/`.

**Word, Excel, PowerPoint and PDF skills** are not in this repo: Anthropic's license does not
allow redistributing them. They ship with Claude accounts as built-in skills. Run `/skills` to
check; if they are missing, an org admin turns on Skills in the Claude admin settings.

## Credits

Third-party skills are copied unmodified with their licenses; see [`third_party/README.md`](third_party/README.md).

`product-frontend-design` adapts parts of Anthropic's
[frontend-design](https://github.com/anthropics/skills) skill (Apache 2.0); see its `NOTICE`.
