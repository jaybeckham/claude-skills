# Validate Shared Memory Installation

From the active project root run:

```sh
python3 .agents/memory/project_memory.py validate
```

Verify the resolved memory directory contains nonempty MEMORY.md and sessions/;
the framework config and runtime exist; both agents have SessionStart,
PreCompact, Stop, and SessionEnd handlers; Codex also has Interrupt. Check
wrapper paths/executable bits and command skill adapters. Preserve unrelated
hooks and settings while fixing any issue.

Use Codex skills/list to confirm actual discovery and hooks/list or /hooks to
check enabled/trusted definitions and configuration errors/warnings. Trust is
not evidence that every event fired. Exercise save/reload only in an isolated
fixture, never seed fake test data into live memory.

Local search is part of the default installation. Semantic MCP is optional;
report its status separately, without calling absent credentials a failed local
installation. If configured, inspect both .mcp.json and Codex MCP registration
and verify project/path isolation. Do not print credentials.
