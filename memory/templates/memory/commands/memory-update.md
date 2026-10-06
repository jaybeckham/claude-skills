# Update Shared Memory Framework

Read `.agents/memory/config.json` for the configured source project and locate
its setup-memory.sh on this host. If that path moved, find the unzipped installer
folder; do not run a guessed path. From this project's root run the source
setup-memory.sh. The installer repairs framework files even at the same version
and preserves user memory, session logs, PROJECT.md, USER.md, SOUL.md, unrelated
hooks/settings, and existing semantic config.

Report the installer output, run `/validate-memory` or `$validate-memory`, and
remind the user to resume/restart and review changed Codex hooks in `/hooks`.
Installation doesn't grant trust. Don't automatically enable semantic services
or cross-project subscriptions as part of a framework update.
