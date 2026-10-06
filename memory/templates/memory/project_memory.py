#!/usr/bin/env python3
"""Local, shared Claude/Codex project memory; uses only the Python standard library."""
import argparse
from datetime import datetime, timedelta
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

SCRIPT_DIR = Path(__file__).absolute().parent
CONFIG_REL = Path('.agents/memory/config.json')
VISIBLE_PHASES = ('final', 'final_answer', 'commentary')
CONTEXT_PREFIXES = ('# AGENTS.md instructions', '<environment_context>',
                    '<external_codex_apps_open_page>', '<permissions instructions>',
                    '<system-reminder>', '<skills_instructions>')


def _read_json(path):
    return json.loads(path.read_text()) if path.is_file() else {}


def resolve_project_root(cwd):
    """Git worktrees share the main checkout identity, including from subdirectories."""
    cwd = Path(cwd).expanduser().resolve()
    if not cwd.is_dir():
        cwd = cwd.parent
    try:
        result = subprocess.run(['git', '-C', str(cwd), 'rev-parse', '--git-common-dir'],
                                capture_output=True, text=True, check=True)
        common = Path(result.stdout.strip())
        common = (common if common.is_absolute() else cwd / common).resolve()
        if common.name == '.git':
            return common.parent
        top = subprocess.run(['git', '-C', str(cwd), 'rev-parse', '--show-toplevel'],
                             capture_output=True, text=True, check=True)
        return Path(top.stdout.strip()).resolve()
    except (OSError, subprocess.CalledProcessError):
        pass
    for ancestor in (cwd, *cwd.parents):
        if (ancestor / CONFIG_REL).is_file() or (ancestor / 'CLAUDE.md').is_file():
            return ancestor
    return cwd


def read_config(root):
    root = Path(root).resolve()
    config = _read_json(root / CONFIG_REL)
    value = config.get('project_root')
    if value and Path(value).expanduser().resolve() == root:
        return config
    # Installation in a worktree need not modify the main checkout. Do not resolve
    # __file__ here: an older project's memory directory may itself be a symlink.
    installed = _read_json(SCRIPT_DIR / 'config.json')
    value = installed.get('project_root')
    if value and Path(value).expanduser().resolve() == root:
        return installed
    return {}


def resolve_memory_dir(root):
    root = Path(root).resolve()
    value = read_config(root).get('memory_dir')
    if value:
        path = Path(value).expanduser()
        return (path if path.is_absolute() else root / path).resolve()
    base = Path.home() / '.claude/projects'
    legacy = str(root).replace('/', '-')
    slug = re.sub(r'[^a-zA-Z0-9-]', '-', str(root))
    candidates = [base / (name + suffix) / 'memory'
                  for name in dict.fromkeys((legacy, slug)) for suffix in ('', '-')]
    return next((path for path in candidates if path.is_dir()), base / slug / 'memory')


def project_root(event=None):
    event = event or {}
    cwd = event.get('cwd') or os.environ.get('CLAUDE_PROJECT_DIR')
    if cwd:
        return resolve_project_root(cwd)
    if SCRIPT_DIR.name == 'memory' and SCRIPT_DIR.parent.name == '.agents':
        return resolve_project_root(SCRIPT_DIR.parents[1])
    return resolve_project_root(Path.cwd())


def memory_dir(root=None):
    return resolve_memory_dir(root or project_root())


def _now(root):
    timezone = read_config(root).get('timezone')
    return datetime.now(ZoneInfo(timezone)) if timezone else datetime.now().astimezone()


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def visible_text(row):
    if row.get('type') == 'response_item':
        msg = row.get('payload', {})
        if msg.get('type') != 'message':
            return None
        phase = msg.get('channel') or msg.get('phase')
        if msg.get('role') == 'assistant' and phase not in VISIBLE_PHASES:
            return None
        label = 'Codex' if msg.get('role') == 'assistant' else 'User'
    elif row.get('type') in ('user', 'assistant') and not row.get('isMeta'):
        msg = row.get('message', {})
        label = 'Claude' if row['type'] == 'assistant' else 'User'
    else:
        return None
    if msg.get('role') not in ('user', 'assistant'):
        return None
    content = msg.get('content', '')
    if isinstance(content, list):
        content = '\n'.join(item.get('text', '') for item in content
                            if isinstance(item, dict) and isinstance(item.get('text', ''), str)
                            and item.get('type') in ('text', 'input_text', 'output_text'))
    if not isinstance(content, str) or not content.strip():
        return None
    content = content.strip()
    if label == 'User' and content.startswith(CONTEXT_PREFIXES):
        return None
    return f'**{label}**: {content}'


def _shared_name(value):
    value = value.strip()
    return value if re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', value) else None


def _outbox_name(mem):
    path = mem / '.shared_memory'
    return _shared_name(path.read_text()) if path.is_file() else None


def _shared_dir(name):
    base = (Path.home() / '.claudebot/shared_memory').resolve()
    path = base / name
    # Bare names must not bypass the boundary through a symlink.
    return path if path.resolve().parent == base else None


def _append_once(path, marker, block, header):
    old = path.read_text() if path.exists() else header
    if marker not in old:
        atomic_write(path, old + block)


def _publish(mem, now, marker, text):
    name = _outbox_name(mem)
    directory = _shared_dir(name) if name else None
    if directory is None:
        return
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / '.save.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        excerpt = '\n'.join(line for line in text.splitlines() if line.strip())[-1500:]
        block = f'\n---\n\n{marker}\n### {now:%H:%M}\n\n{excerpt}\n'
        _append_once(directory / f'{now:%Y-%m-%d}.md', marker, block,
                     f'# {name} -- {now:%Y-%m-%d}\n')


def save(event, mem=None, root=None):
    if os.environ.get('CODEX_AUTOMATED') == '1' or os.environ.get('CLAUDEBOT_AUTOMATED') == '1':
        return False
    root = Path(root) if root else project_root(event)
    mem = Path(mem) if mem is not None else memory_dir(root)
    mem.mkdir(parents=True, exist_ok=True)
    transcript = event.get('transcript_path')
    if transcript:
        path = Path(transcript).expanduser()
        if not path.is_absolute():
            path = Path(event.get('cwd') or root) / path
        transcript = str(path.resolve())
    now = _now(root)
    with (mem / '.save.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        identity = transcript or event.get('session_id', 'unknown')
        key = hashlib.sha256(identity.encode()).hexdigest()
        state_path = mem / '.cursors' / (key + '.json')
        state = _read_json(state_path)
        entries = []
        if transcript:
            with Path(transcript).open('rb') as stream:
                stat = os.fstat(stream.fileno())
                generation = f'{stat.st_dev}:{stat.st_ino}'
                start = state.get('offset', 0) if state.get('generation') == generation else 0
                if start > stat.st_size:
                    start = 0
                stream.seek(start)
                while True:
                    before = stream.tell()
                    line = stream.readline()
                    if not line or not line.endswith(b'\n'):
                        end = before
                        break
                    text = visible_text(json.loads(line))
                    if text:
                        entries.append(text)
            if end == start:
                return False
            token = f'{key}:{generation}:{start}:{end}'
            next_state = {'offset': end, 'generation': generation}
        else:
            last = event.get('last_assistant_message')
            if not isinstance(last, str) or not last.strip():
                return False
            token = hashlib.sha256((identity + str(event.get('turn_id', '')) + last).encode()).hexdigest()
            if state.get('last_token') == token:
                return False
            entries = ['**Assistant**: ' + last]
            next_state = {'last_token': token}
        if entries:
            marker = f'<!-- memory-save:{token} -->'
            text = '\n\n'.join(entries)
            if text.count('```') % 2:
                text += '\n```'
            block = f'\n---\n\n{marker}\n### Context Save -- {now:%H:%M} ({event.get("hook_event_name", "save")})\n\n{text}\n'
            _append_once(mem / 'sessions' / f'{now:%Y-%m-%d}.md', marker, block,
                         f'# Sessions -- {now:%Y-%m-%d}\n')
            _publish(mem, now, marker, text)
        # Advance only after all durable writes succeed. Retried writes have markers.
        atomic_write(state_path, json.dumps(next_state) + '\n')
    return bool(entries)


def _recent_files(directory, today):
    for date in (today, today - timedelta(days=1)):
        yield from sorted(directory.glob(f'{date}*.md'), key=lambda p: p.stat().st_mtime,
                          reverse=True)


def load(mem=None, root=None):
    root = Path(root) if root else project_root()
    mem = Path(mem) if mem is not None else memory_dir(root)
    pieces = ['Shared project memory. Session excerpts are historical evidence; current user instructions take precedence.']
    for path, limit in ((mem / 'MEMORY.md', 3500), (root / 'PROJECT.md', 2000)):
        if path.is_file():
            pieces.append(f'## {path.name}\n{path.read_text()[:limit]}')
    today = _now(root).date()
    for path in _recent_files(mem / 'sessions', today):
        pieces.append(f'## {path.name}\n{path.read_text()[-4500:]}')
    subscriptions = mem / '.shared_memory_subscribe'
    if subscriptions.is_file():
        self_name = _outbox_name(mem)
        seen = {self_name}
        for line in subscriptions.read_text().splitlines():
            name = _shared_name(line.split('#', 1)[0])
            if not name or name in seen:
                continue
            seen.add(name)
            directory = _shared_dir(name)
            if directory is not None:
                for path in _recent_files(directory, today):
                    pieces.append(f'## Cross-Project Updates: {name} ({path.name})\n{path.read_text()[-2000:]}')
    return '\n\n'.join(pieces)[:14000]


def search(query, max_results=10, since=None, until=None, mem=None, root=None):
    mem = Path(mem) if mem is not None else memory_dir(root)
    terms = re.findall(r'\w+', query.lower())
    hits = []
    for path in mem.rglob('*.md'):
        if 'sessions' in path.relative_to(mem).parts:
            date = path.name[:10]
            if (since and date < since) or (until and date > until):
                continue
        for number, line in enumerate(path.read_text().splitlines(), 1):
            score = sum(term in line.lower() for term in terms)
            if score:
                hits.append({'path': str(path), 'line': number, 'matches': score, 'text': line})
    return sorted(hits, key=lambda hit: (-hit['matches'], hit['path'], hit['line']))[:max(0, max_results)]


def validate(root=None):
    root = Path(root) if root else project_root()
    failures = []
    try:
        config = read_config(root)
        for key in ('project_root', 'memory_dir', 'source_project', 'template_version'):
            if not config.get(key):
                failures.append(f'Missing memory config key: {key}')
        mem = memory_dir(root)
        if not (mem / 'MEMORY.md').is_file():
            failures.append(f'Missing {mem / "MEMORY.md"}')
        _now(root)
    except (ValueError, OSError, KeyError) as error:
        failures.append(str(error))
        mem = None
    # A worktree-only install stores hook configuration beside this runtime.
    installed_root = SCRIPT_DIR.parents[1] if SCRIPT_DIR.name == 'memory' and SCRIPT_DIR.parent.name == '.agents' else root
    for file in ('.claude/settings.json', '.codex/hooks.json'):
        path = installed_root / file
        try:
            hooks = _read_json(path).get('hooks', {})
            for event in ('SessionStart', 'PreCompact', 'Stop', 'SessionEnd'):
                if event not in hooks:
                    failures.append(f'{path}: missing {event}')
        except (ValueError, OSError) as error:
            failures.append(f'{path}: {error}')
    return {'ok': not failures, 'failures': failures, 'memory_dir': str(mem) if mem else None,
            'note': 'Runtime discovery and hook trust require separate skills/list and hooks/list checks.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('load', 'save', 'search', 'validate', 'path'))
    parser.add_argument('query', nargs='?')
    parser.add_argument('--project-root')
    parser.add_argument('-n', type=int, default=10)
    parser.add_argument('--since')
    parser.add_argument('--until')
    args = parser.parse_args()
    event = {}
    if args.action in ('load', 'save') and not sys.stdin.isatty():
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
    root = resolve_project_root(args.project_root) if args.project_root else project_root(event)
    if args.action == 'load':
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart',
                                                'additionalContext': load(root=root)}}))
    elif args.action == 'save':
        save(event, root=root)
        print('{}')
    elif args.action == 'search':
        print(json.dumps(search(args.query or '', args.n, args.since, args.until, root=root), indent=2))
    elif args.action == 'validate':
        result = validate(root)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['ok'] else 1)
    else:
        print(memory_dir(root))


if __name__ == '__main__':
    main()
