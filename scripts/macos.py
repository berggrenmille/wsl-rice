#!/usr/bin/env python3
"""Preview, apply, or restore the Violet Afterdark macOS setup."""
import argparse
import difflib
import json
import os
from pathlib import Path
import platform

from install import ROOT, apply, restore


def append_hook(path, line):
    # A dotfiles symlink should keep pointing to the user's managed file.
    path = path.resolve()
    original = path.read_bytes() if path.exists() else b''
    hook = line.encode()
    if hook in original.splitlines():
        return path, original
    separator = b'\n' if original and not original.endswith(b'\n') else b''
    return path, original + separator + b'\n# Violet Afterdark\n' + hook + b'\n'


def ghostty_theme():
    scheme = json.loads((ROOT / 'windows/terminal.json').read_text())['scheme']
    colors = {
        'background': 'background',
        'foreground': 'foreground',
        'cursor-color': 'cursorColor',
        'selection-background': 'selectionBackground',
    }
    lines = [f'{key} = {scheme[name]}' for key, name in colors.items()]
    ansi = ['black', 'red', 'green', 'yellow', 'blue', 'purple', 'cyan', 'white']
    ansi += ['bright' + name.title() for name in ansi]
    lines += [f'palette = {index}={scheme[name]}' for index, name in enumerate(ansi)]
    return ('\n'.join(lines) + '\n').encode()


def changes_for(home, zshrc, ghostty_config=None, tmux_conf=None):
    configs = home / '.config/violet-macos'
    changes = [
        (configs / 'shell.zsh', (ROOT / 'macos/shell.zsh').read_bytes()),
        (configs / 'starship.toml', (ROOT / 'config/starship.toml').read_bytes()),
        (configs / 'fastfetch.jsonc', (ROOT / 'config/fastfetch.jsonc').read_bytes()),
    ]
    if ghostty_config is not None:
        changes.append((ghostty_config / 'themes/Violet Afterdark', ghostty_theme()))
    if tmux_conf is not None:
        tmux_settings = (ROOT / 'config/tmux.conf').read_bytes()
        # Reload this include directly so the binding also works with XDG tmux config.
        tmux_settings = tmux_settings.replace(b'~/.tmux.conf', b'~/.config/violet-macos/tmux.conf')
        tmux_settings += b"\nset -as terminal-features ',xterm-ghostty:RGB'\n"
        changes.append((configs / 'tmux.conf', tmux_settings))
        changes.append(append_hook(tmux_conf, 'source-file ~/.config/violet-macos/tmux.conf'))
    changes.append(append_hook(zshrc, 'source "$HOME/.config/violet-macos/shell.zsh"'))
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['preview', 'apply', 'restore'])
    parser.add_argument('--zshrc', type=Path, help='Path to the active .zshrc if it is outside your home')
    parser.add_argument('--ghostty', action='store_true', help='Install the Ghostty color theme')
    parser.add_argument('--tmux', action='store_true', help='Add the shared theme and keybindings to ~/.tmux.conf')
    parser.add_argument('--tmux-conf', type=Path, help='Add tmux settings to this file instead')
    parser.add_argument('--backup', type=Path, help='Restore a specific manifest instead of the latest Mac backup')
    args = parser.parse_args()
    home = Path.home()
    state = home / '.local/state/violet-macos'

    if args.action != 'preview' and platform.system() != 'Darwin':
        parser.error('Apply or restore this setup from macOS.')
    try:
        if args.action == 'restore':
            restore(args.backup or Path((state / 'latest').read_text()))
            return

        zshrc = args.zshrc or home / '.zshrc'
        tmux_conf = args.tmux_conf or (home / '.tmux.conf' if args.tmux else None)
        ghostty_config = None
        if args.ghostty:
            ghostty_config = Path(os.environ.get('XDG_CONFIG_HOME') or home / '.config') / 'ghostty'
        changes = changes_for(home, zshrc, ghostty_config, tmux_conf)
        if args.action == 'preview':
            for path, data in changes:
                original = path.read_bytes() if path.exists() else b''
                old = original.decode('utf-8', errors='replace').splitlines(keepends=True)
                new = data.decode('utf-8', errors='replace').splitlines(keepends=True)
                diff = difflib.unified_diff(old, new, fromfile=str(path), tofile=f'{path} (Violet)')
                print(''.join(diff), end='')
            return

        apply(changes, state)
        print('Open a new Zsh terminal to load Violet Afterdark.')
        if args.ghostty:
            print('In your Ghostty config, set theme = Violet Afterdark and reload it.')
    except (OSError, ValueError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
