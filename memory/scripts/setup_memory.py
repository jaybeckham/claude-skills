#!/usr/bin/env python3
"""Install the versioned local memory framework without external dependencies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

BEGIN = '<!-- BEGIN CLAUDEBOT MEMORY -->'
END = '<!-- END CLAUDEBOT MEMORY -->'
ADAPTER = '<!-- claude-memory-command-adapter -->'
HOOK_NAMES = {'session-start-load.sh', 'session-end-save.sh', 'pre-compact-save.sh',
              'session-end-clear.sh', 'session-end-save.py', 'interrupt-save.sh'}


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    target = path.resolve() if path.is_symlink() else path
    fd, name = tempfile.mkstemp(dir=target.parent, prefix='.' + target.name)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, target)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def read_json(path):
    return json.loads(path.read_text()) if path.exists() else {}


def project_root(path):
    try:
        git = subprocess.run(['git', '-C', str(path), 'rev-parse', '--git-common-dir'],
                             text=True, capture_output=True, check=True).stdout.strip()
        common = (path / git).resolve()
        if common.name == '.git':
            return common.parent
        return Path(subprocess.check_output(['git', '-C', str(path), 'rev-parse', '--show-toplevel'], text=True).strip())
    except (OSError, subprocess.CalledProcessError):
        for parent in (path, *path.parents):
            if (parent / '.agents/memory/config.json').is_file():
                return parent
            if (parent / 'CLAUDE.md').is_file():
                return parent
        return path


def memory_path(root, install):
    for config in [install / '.agents/memory/config.json', root / '.agents/memory/config.json',
                   install / '.agents/memory-config.json', root / '.agents/memory-config.json']:
        if config.exists():
            data = read_json(config)
            if Path(data.get('project_root', '')).expanduser().resolve() == root:
                directory = Path(data['memory_dir']).expanduser()
                return (directory if directory.is_absolute() else root / directory).resolve()
    legacy = str(root).replace('/', '-')
    slug = re.sub('[^a-zA-Z0-9-]', '-', str(root))
    for name in [legacy, legacy + '-', slug, slug + '-']:
        path = Path.home() / '.claude/projects' / name / 'memory'
        if path.is_dir():
            return path
    return Path.home() / '.claude/projects' / slug / 'memory'


def substitute(text, values):
    for key, value in values.items():
        text = text.replace('__' + key + '__', str(value))
    return text


def merge_section(path, section):
    if path.is_symlink() and not path.exists():
        raise ValueError(f'Cannot update broken instruction link: {path}')
    text = path.read_text() if path.exists() else ''
    block = BEGIN + '\n' + section.strip() + '\n' + END
    if BEGIN in text:
        if END not in text:
            raise ValueError(f'Incomplete managed memory section: {path}')
        text = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END), lambda _: block, text, flags=re.S)
    elif '## Memory System' in text:
        # Migrate the old unmarked section up to the next unrelated H2.
        text = re.sub(r'^## Memory System\n.*?(?=^## |\Z)', lambda _: block + '\n\n', text, count=1, flags=re.S | re.M)
    else:
        text = text.rstrip() + '\n\n' + block + '\n'
    atomic_write(path, text.lstrip('\n'))


def owned_hook(command, install, prior_roots=(), legacy_runtime=False):
    if not isinstance(command, str):
        return False
    projects = [install, *prior_roots]
    runtime_paths = [str(p / '.agents/memory/project_memory.py') for p in projects]
    if legacy_runtime:
        runtime_paths.append(str(install / 'scripts/project_memory.py'))
    absolute_owned = set(runtime_paths)
    absolute_owned.update(str(p / folder / name) for p in projects
                          for folder in ['.claude/hooks', '.codex/hooks'] for name in HOOK_NAMES)
    try:
        if any(token in absolute_owned for token in shlex.split(command)):
            return True
    except ValueError:
        pass
    if any(re.search(r'(?<![\w/.-])' + re.escape(path) + r'(?:[\s\"\']|$)', command)
           for path in runtime_paths):
        return True
    # Match the project's own framework scripts, never a peer/plugin script
    # that happens to have the same basename.
    roots = [str(p / folder) for p in projects for folder in ['.claude/hooks', '.codex/hooks']]
    roots += ['$CLAUDE_PROJECT_DIR/.claude/hooks', '"$CLAUDE_PROJECT_DIR"/.claude/hooks',
             '$(git rev-parse --show-toplevel)/.codex/hooks', '.codex/hooks', '.claude/hooks']
    return any(re.search(r'(?<![\w/.-])' + re.escape(prefix) + '/' + re.escape(name) + r'(?:[\s\"\']|$)', command)
               for prefix in roots for name in HOOK_NAMES)


def merge_hooks(existing, incoming, install, prior_roots=(), legacy_runtime=False):
    result = dict(existing)
    hooks = {}
    for event, groups in existing.get('hooks', {}).items():
        keep = []
        for group in groups:
            handlers = [h for h in group.get('hooks', [])
                        if not owned_hook(h.get('command'), install, prior_roots, legacy_runtime)]
            if handlers:
                keep.append({**group, 'hooks': handlers})
        if keep:
            hooks[event] = keep
    for event, groups in incoming['hooks'].items():
        hooks.setdefault(event, []).extend(groups)
    result['hooks'] = hooks
    return result


def share_skills(install, sources):
    claude = install / '.claude/skills'
    agents = install / '.agents/skills'
    if claude.is_symlink() and not claude.exists():
        if claude.resolve() == agents.resolve():
            agents.mkdir(parents=True, exist_ok=True)
        else:
            raise ValueError(f'Broken Claude skills registry: {claude}')
    claude.mkdir(parents=True, exist_ok=True)
    if not agents.exists() and not agents.is_symlink():
        agents.symlink_to('../.claude/skills', target_is_directory=True)
    elif agents.is_symlink() and not agents.exists():
        raise ValueError(f'Broken Codex skills registry: {agents}')
    # Existing independent registries are both preserved. Codex links missing
    # Claude entries, keeping one canonical body without moving user files.
    if agents.resolve() != claude.resolve():
        for entry in claude.iterdir():
            dest = agents / entry.name
            if not dest.exists() and not dest.is_symlink():
                dest.symlink_to(entry.resolve(), target_is_directory=entry.is_dir())
    for source in sources:
        source = source.expanduser().resolve()
        entries = [source] if (source / 'SKILL.md').is_file() else [p.parent for p in source.glob('*/SKILL.md')]
        if not entries:
            raise ValueError(f'No SKILL.md packages found: {source}')
        for entry in entries:
            dest = claude / entry.name
            if dest.exists() or dest.is_symlink():
                print(f'Preserved existing skill: {dest}')
                continue
            shutil.copytree(entry, dest, symlinks=True, ignore=shutil.ignore_patterns('__pycache__', 'archive-v1'))
            if agents.resolve() != claude.resolve() and not (agents / entry.name).exists():
                (agents / entry.name).symlink_to(dest.resolve(), target_is_directory=True)
    return agents


def install_semantic(source, install, mem, project_name):
    server = source / 'claude-memory/server.py'
    python = source / 'claude-memory/.venv/bin/python'
    if not server.is_file() or not python.is_file():
        raise ValueError('--semantic requires ClaudeBot\'s configured claude-memory server and healthy .venv; local memory works without it.')
    subprocess.run([str(python), '-c', 'import fastmcp, httpx, watchdog, pydantic_settings, dotenv, numpy'], check=True)
    env = {'MEMORY_DIR': str(mem), 'PROJECT_NAME': project_name, 'EXTRA_PATHS': '', 'JSONL_DIR': ''}
    path = install / '.mcp.json'
    data = read_json(path)
    data.setdefault('mcpServers', {})['memory-search'] = {'command': str(python), 'args': [str(server)], 'env': env}
    config = install / '.codex/config.toml'
    text = config.read_text() if config.exists() else ''
    begin, end = '# BEGIN CLAUDEBOT MEMORY MCP', '# END CLAUDEBOT MEMORY MCP'
    block = '\n'.join([begin, '[mcp_servers.memory-search]', f'command = {json.dumps(str(python))}',
                       f'args = [{json.dumps(str(server))}]', '[mcp_servers.memory-search.env]',
                       *[f'{k} = {json.dumps(v)}' for k, v in env.items()], end])
    if begin in text:
        if end not in text:
            raise ValueError('Incomplete managed Codex MCP block')
        text = re.sub(re.escape(begin) + '.*?' + re.escape(end), lambda _: block, text, flags=re.S)
    elif re.search(r'\[mcp_servers\.(?:"memory-search"|memory-search)', text):
        raise ValueError('Existing custom Codex memory-search config: migrate it explicitly before using --semantic.')
    else:
        text = text.rstrip() + '\n\n' + block + '\n'
    atomic_write(config, text.lstrip('\n'))
    atomic_write(path, json.dumps(data, indent=2) + '\n')


def install(args):
    source = args.source.expanduser().resolve()
    target = (args.project or Path.cwd()).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    canonical = project_root(target)
    mem = memory_path(canonical, target)
    templates = source / 'templates/memory'
    version = (templates / 'VERSION').read_text().strip()
    # Parse existing JSON before installing framework files; malformed settings
    # must not be overwritten or silently replaced with defaults.
    old_claude = read_json(target / '.claude/settings.json')
    old_codex = read_json(target / '.codex/hooks.json')
    installed_config = read_json(target / '.agents/memory/config.json')
    legacy_config = read_json(target / '.agents/memory-config.json')
    legacy_runtime = bool(legacy_config.get('project_root') and
                          Path(legacy_config['project_root']).expanduser().resolve() == canonical)
    prior_roots = []
    if installed_config.get('project_root'):
        prior_roots.append(Path(installed_config['project_root']).expanduser().resolve())
    timezone = args.timezone or installed_config.get('timezone') or (legacy_config.get('timezone') if legacy_runtime else None)
    if timezone:
        ZoneInfo(timezone)
    values = {'PROJECT_DIR': target, 'MEMORY_DIR': mem, 'SESSIONS_DIR': mem / 'sessions',
              'CLAUDEBOT_DIR': source, 'PYTHON_COMMAND': shlex.quote(sys.executable),
              'RUNTIME_PATH': shlex.quote(str(target / '.agents/memory/project_memory.py')),
              'USER_TIMEZONE': timezone or 'system local time'}
    framework = target / '.agents/memory'
    if framework.is_symlink() and framework.resolve() == mem and legacy_runtime:
        # Earlier Writing installs aliased the whole native memory directory.
        # Replace only the alias; preserve all native data and old read paths.
        framework.unlink()
        framework.mkdir(parents=True, exist_ok=True)
        for entry in mem.iterdir():
            if entry.suffix == '.md' or entry.name in {'sessions', 'topics', 'VERSION'}:
                (framework / entry.name).symlink_to(entry, target_is_directory=entry.is_dir())
    framework.mkdir(parents=True, exist_ok=True)
    atomic_write(framework / 'project_memory.py', (templates / 'project_memory.py').read_text())
    config = {'project_root': str(canonical), 'memory_dir': str(mem), 'timezone': timezone,
              'source_project': str(source), 'template_version': version}
    atomic_write(framework / 'config.json', json.dumps(config, indent=2) + '\n')
    (mem / 'sessions').mkdir(parents=True, exist_ok=True)
    for dest, template in [(mem / 'MEMORY.md', 'MEMORY.md.template'), (target / 'PROJECT.md', 'PROJECT.md.template'),
                           (target / 'SOUL.md', 'SOUL.md.template'), (target / 'USER.md', 'USER.md.template')]:
        if not dest.exists():
            atomic_write(dest, substitute((templates / template).read_text(), values))
    section = substitute((templates / 'CLAUDE.md.section').read_text(), values)
    merge_section(target / 'CLAUDE.md', section)
    agents_file = target / 'AGENTS.md'
    if not agents_file.exists() and not agents_file.is_symlink():
        agents_file.symlink_to('CLAUDE.md')
    elif agents_file.resolve() != (target / 'CLAUDE.md').resolve():
        merge_section(agents_file, section)
    for folder in ['hooks', 'codex/hooks']:
        dest_root = target / ('.claude/hooks' if folder == 'hooks' else '.codex/hooks')
        for file in (templates / folder).glob('*.sh'):
            dest = dest_root / file.name
            atomic_write(dest, substitute(file.read_text(), values))
            dest.chmod(0o755)
    incoming_claude = read_json(templates / 'settings.json.template')
    incoming_codex = read_json(templates / 'codex/hooks.json')
    for incoming, folder in [(incoming_claude, '.claude'), (incoming_codex, '.codex')]:
        for groups in incoming['hooks'].values():
            for group in groups:
                for handler in group['hooks']:
                    handler['command'] = 'bash ' + shlex.quote(str(target / folder / 'hooks' / handler['command']))
    atomic_write(target / '.claude/settings.json', json.dumps(merge_hooks(old_claude, incoming_claude, target, prior_roots, legacy_runtime), indent=2) + '\n')
    atomic_write(target / '.codex/hooks.json', json.dumps(merge_hooks(old_codex, incoming_codex, target, prior_roots, legacy_runtime), indent=2) + '\n')
    codex_config = target / '.codex/config.toml'
    if not codex_config.exists():
        # Codex discovers project hooks through an active project config layer.
        atomic_write(codex_config, '# Project hooks are configured in hooks.json.\n')
    agents = share_skills(target, args.skills_from)
    commands = []
    for file in sorted((templates / 'commands').glob('*.md')):
        name = file.stem
        command = target / '.claude/commands' / file.name
        atomic_write(command, substitute(file.read_text(), values))
        skill = agents / name / 'SKILL.md'
        if skill.exists() and ADAPTER not in skill.read_text():
            print(f'Preserved custom Codex skill {name}; canonical command is {command}')
            continue
        description = f'Run the {name} project memory workflow. Use when the user requests {name.replace("-", " ") }.'
        text = f'---\nname: {name}\ndescription: {json.dumps(description)}\n---\n\n{ADAPTER}\n\nRead and follow the canonical command at {json.dumps(str(command))}. In Codex invoke this as ${name}; remaining user text supplies arguments. Map Claude tool names to available tools. Resolve memory dynamically with the installed runtime; never guess a host-specific memory path.\n'
        atomic_write(skill, text)
        commands.append(name)
    if args.link_wiki:
        wiki = target / 'wiki'
        if not (source / 'wiki').is_dir():
            raise ValueError(f'Wiki source unavailable: {source / "wiki"}')
        if not wiki.exists() and not wiki.is_symlink():
            wiki.symlink_to(source / 'wiki', target_is_directory=True)
        elif wiki.resolve() != (source / 'wiki').resolve():
            print(f'Preserved existing wiki: {wiki}')
    if args.semantic:
        name = re.sub('[^a-z0-9-]', '-', canonical.name.lower()).strip('-') or 'project'
        name += '-' + hashlib.sha256(str(canonical).encode()).hexdigest()[:8]
        install_semantic(source, target, mem, name)
    ignore = target / '.gitignore'
    text = ignore.read_text() if ignore.exists() else ''
    for entry in ['.mcp.json', '.env', 'USER.md', '.agents/memory/__pycache__/', '.agents/memory/*.pyc']:
        if entry not in text.splitlines():
            text = text.rstrip('\n') + '\n' + entry + '\n'
    atomic_write(ignore, text.lstrip('\n'))
    atomic_write(mem / 'VERSION', version + '\n')
    print(f'Installed shared memory v{version} in {target}\nMemory: {mem}\nCommands: ' + ', '.join('/' + n + ' / $' + n for n in commands))
    print('Local memory and search are ready. Resume/restart Claude and Codex for updated context.')
    print('New here? Restart, then run /get-started (Claude) or $get-started (Codex) for a short setup interview.')
    print('Codex activation: trust the project if needed, then review/trust the new definitions in /hooks. The installer does not change global trust or bypass review.')
    if not args.semantic:
        print('Semantic MCP is optional (not included in this package); existing MCP settings are preserved.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--project', type=Path)
    parser.add_argument('--force', action='store_true', help='Compatibility flag; repeated installs always repair framework files')
    parser.add_argument('--timezone', help='IANA timezone; default is existing config or system local time')
    parser.add_argument('--skills-from', type=Path, action='append', default=[], help='Import a skill directory or collection without overwriting existing skills')
    parser.add_argument('--link-wiki', action='store_true', help='Link the source ClaudeBot wiki if the project has no wiki')
    parser.add_argument('--semantic', action='store_true', help='Register the configured shared semantic MCP runtime for both agents')
    args = parser.parse_args()
    try:
        install(args)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'Memory install failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
