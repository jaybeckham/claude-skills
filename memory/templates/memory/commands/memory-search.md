# Search Project Memory

Resolve the active project root, then run its local runtime:

```sh
python3 .agents/memory/project_memory.py search "<query>" -n 10
```

Use `--since YYYY-MM-DD` and `--until YYYY-MM-DD` for session-date filters.
Read matching source files around returned line numbers before synthesizing.
Report no matches honestly. This is lexical search; it is available without
semantic services or credentials. If an explicitly configured semantic MCP
is available, it can supplement the local results; distinguish the sources.
