# Third-party skills

Copied unmodified from their upstream repos so they install without a plugin marketplace.
Each folder keeps its original license.

| Folder | Upstream | Commit | License |
|---|---|---|---|
| `superpowers/skills/` | https://github.com/obra/superpowers | `8ca22dba9a94f28898bbce59f2537ff4d87c747d` | MIT |
| `skill-creator/skill-creator/` | https://github.com/anthropics/skills (`skills/skill-creator`) | `683bc88e56f3e09ba94f7055977f3d3aa499f202` | Apache 2.0 |

Superpowers normally runs as a plugin with a session-start hook that loads `using-superpowers`.
Copied as plain skills, they work the same but do not auto-load; say "use the brainstorming
skill" or let Claude pick them by description. Skill names drop the `superpowers:` prefix.

To update, re-copy from upstream and change the commit above.
