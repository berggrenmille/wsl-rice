#!/usr/bin/env python3
"""Preview, apply, or restore Violet Afterdark; no root access required."""
import argparse
from datetime import datetime, timezone
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'config/bashrc': '.bashrc',
    'config/shell.bash': '.config/wsl-rice/shell.bash',
    'config/starship.toml': '.config/starship.toml',
    'config/fastfetch.jsonc': '.config/fastfetch/config.jsonc',
    'config/tmux.conf': '.tmux.conf',
    'config/bat.conf': '.config/bat/config',
    'config/Violet Afterdark.tmTheme': '.config/bat/themes/Violet Afterdark.tmTheme',
}


def jsonc_loads(text):
    """Remove JSONC comments and trailing commas while respecting JSON strings."""
    text = text.lstrip('\ufeff')
    out, i = [], 0
    while i < len(text):
        if text[i] == '"':
            start = i
            i += 1
            while i < len(text):
                if text[i] == '\\':
                    i += 2
                elif text[i] == '"':
                    i += 1
                    break
                else:
                    i += 1
            out.append(text[start:i])
        elif text[i:i+2] == '//':
            end = text.find('\n', i)
            i = len(text) if end < 0 else end
        elif text[i:i+2] == '/*':
            end = text.find('*/', i+2)
            if end < 0:
                raise ValueError('Unterminated JSONC comment')
            out.append(' ')
            i = end+2
        else:
            out.append(text[i])
            i += 1
    text = ''.join(out)
    out, i, in_string, escaped = [], 0, False, False
    while i < len(text):
        c = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif c == '\\':
                escaped = True
            elif c == '"':
                in_string = False
        elif c == '"':
            in_string = True
        elif c == ',':
            j = i+1
            while j < len(text) and text[j].isspace():
                j += 1
            if j < len(text) and text[j] in '}]':
                i += 1
                continue
        out.append(c)
        i += 1
    return json.loads(''.join(out))


def merge_terminal(raw, preset, profile_guid=None):
    settings = jsonc_loads(raw)
    profiles = settings.get('profiles', {}).get('list', [])
    if profile_guid:
        targets = [p for p in profiles if p.get('guid') == profile_guid]
    else:
        distro = os.environ.get('WSL_DISTRO_NAME', 'Ubuntu')
        targets = [p for p in profiles if p.get('name') == distro and not p.get('hidden', False)]
    if len(targets) != 1:
        raise ValueError('Cannot select exactly one visible distro profile; pass --profile-guid GUID')
    profile = targets[0]
    for key, value in preset['profile'].items():
        if isinstance(value, dict):
            profile.setdefault(key, {}).update(value)
        else:
            profile[key] = value
    schemes = settings.setdefault('schemes', [])
    schemes[:] = [s for s in schemes if s.get('name') != preset['scheme']['name']]
    schemes.append(preset['scheme'])
    return (json.dumps(settings, indent=4, ensure_ascii=False)+'\n').encode()


def find_terminal():
    local = subprocess.check_output(
        ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', '$env:LOCALAPPDATA'], text=True).strip()
    local = Path(subprocess.check_output(['wslpath', '-u', local], text=True).strip())
    candidates = list((local / 'Packages').glob('Microsoft.WindowsTerminal_*/LocalState/settings.json'))
    if len(candidates) != 1:
        raise ValueError('Cannot locate one stable Windows Terminal settings file; pass --windows-settings PATH')
    return candidates[0]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.violet-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        os.chmod(temp, mode)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def apply(changes, state):
    changes = [(p, d) for p, d in changes if not p.is_file() or p.read_bytes() != d]
    if not changes:
        print('Already up to date; no files changed.')
        return None
    backup = state / 'backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    backup.mkdir(parents=True, mode=0o700)
    entries = []
    # Snapshot all targets before touching any of them.
    for index, (path, data) in enumerate(changes):
        exists = path.exists() or path.is_symlink()
        entry = {'path': str(path), 'existed': exists, 'installed_sha256': sha(data), 'backup': str(index)}
        if exists:
            if path.is_symlink():
                entry['symlink'] = os.readlink(path)
            if path.exists():
                entry['mode'] = path.stat().st_mode & 0o777
                atomic_write(backup / str(index), path.read_bytes(), 0o600)
        entries.append(entry)
    manifest = backup / 'manifest.json'
    atomic_write(manifest, (json.dumps({'entries': entries}, indent=2)+'\n').encode(), 0o600)
    # Record the transaction before applying so interrupted installs can be recovered.
    atomic_write(state / 'latest', str(manifest).encode(), 0o600)
    for (path, data), entry in zip(changes, entries):
        atomic_write(path, data, entry.get('mode', 0o644))
        print(f'Installed {path}')
    print(f'Backup: {manifest}')
    return manifest


def restore(manifest):
    entries = json.loads(manifest.read_text())['entries']
    pending = []
    # Refuse the entire restore before changing anything if later edits are present.
    for entry in entries:
        path = Path(entry['path'])
        original = manifest.parent / entry['backup']
        exists = path.exists() or path.is_symlink()
        if entry.get('symlink') is not None and path.is_symlink() and os.readlink(path) == entry['symlink']:
            continue
        if not entry['existed'] and not exists:
            continue
        if entry['existed'] and not entry.get('symlink') and path.is_file() and original.exists() and path.read_bytes() == original.read_bytes():
            continue
        if path.is_symlink() or not path.is_file() or sha(path.read_bytes()) != entry['installed_sha256']:
            raise ValueError(f'Restore stopped: {path} has changed since installation. Save those edits first.')
        pending.append(entry)
    for entry in pending:
        path = Path(entry['path'])
        if entry.get('symlink') is not None:
            path.unlink()
            path.symlink_to(entry['symlink'])
        elif entry['existed']:
            atomic_write(path, (manifest.parent / entry['backup']).read_bytes(), entry.get('mode', 0o644))
        else:
            path.unlink()
        print(f'Restored {path}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['preview', 'apply', 'restore'])
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--windows', action='store_true', help='Also merge the current distro Windows Terminal profile')
    parser.add_argument('--windows-settings', type=Path)
    parser.add_argument('--profile-guid')
    parser.add_argument('--backup', type=Path, help='Specific manifest for restore; defaults to latest')
    args = parser.parse_args()
    home = args.home.absolute()
    state = home / '.local/state/wsl-rice'
    try:
        if args.action == 'restore':
            manifest = args.backup or Path((state / 'latest').read_text())
            restore(manifest)
            return
        changes = [(home / target, (ROOT / source).read_bytes()) for source, target in FILES.items()]
        if args.windows or args.windows_settings:
            path = (args.windows_settings or find_terminal()).absolute()
            preset = json.loads((ROOT / 'windows/terminal.json').read_text())
            changes.append((path, merge_terminal(path.read_text(encoding='utf-8-sig'), preset, args.profile_guid)))
        if args.action == 'preview':
            for path, data in changes:
                old = path.read_text() if path.is_file() else ''
                print(''.join(difflib.unified_diff(old.splitlines(True), data.decode().splitlines(True), fromfile=str(path), tofile=str(path)+' (Violet Afterdark)')), end='')
            return
        apply(changes, state)
        bat = shutil.which('bat') or shutil.which('batcat')
        if bat:
            subprocess.run([bat, 'cache', '--build'], check=True, env={**os.environ, 'HOME': str(home), 'XDG_CONFIG_HOME': str(home / '.config'), 'XDG_CACHE_HOME': str(home / '.cache')})
        print('Open a fresh terminal tab to load the theme.')
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
