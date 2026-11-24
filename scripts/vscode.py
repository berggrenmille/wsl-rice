#!/usr/bin/env python3
"""Select the installed Violet Afterdark VS Code theme with backup and restore."""
import argparse
import difflib
import json
from pathlib import Path
import subprocess

from install import apply, jsonc_loads, restore


def settings_path():
    roaming = subprocess.check_output(
        ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', '$env:APPDATA'], text=True).strip()
    roaming = Path(subprocess.check_output(['wslpath', '-u', roaming], text=True).strip())
    directory = roaming / 'Code/User'
    if not directory.is_dir():
        raise ValueError('Stable VS Code user directory not found; pass --settings PATH')
    return directory / 'settings.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['preview', 'apply', 'restore'])
    parser.add_argument('--settings', type=Path, help='Alternate user/profile settings.json')
    parser.add_argument('--terminal-font', help='Optionally set the integrated terminal font')
    parser.add_argument('--backup', type=Path, help='Specific restore manifest; defaults to latest VS Code backup')
    args = parser.parse_args()
    state = Path.home() / '.local/state/wsl-rice/vscode'
    try:
        if args.action == 'restore':
            restore(args.backup or Path((state / 'latest').read_text()))
            return
        path = (args.settings or settings_path()).absolute()
        raw = path.read_text(encoding='utf-8-sig') if path.exists() else '{}\n'
        settings = jsonc_loads(raw)
        settings['workbench.colorTheme'] = 'Violet Afterdark'
        if args.terminal_font:
            settings['terminal.integrated.fontFamily'] = args.terminal_font
        updated = json.dumps(settings, indent=4, ensure_ascii=False)+'\n'
        if args.action == 'preview':
            print(''.join(difflib.unified_diff(raw.splitlines(True), updated.splitlines(True), fromfile=str(path), tofile=str(path)+' (Violet Afterdark)')), end='')
        else:
            apply([(path, updated.encode())], state)
            print('Theme selected. If needed, run Developer: Reload Window in VS Code.')
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
