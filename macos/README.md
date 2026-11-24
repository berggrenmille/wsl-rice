# Violet Afterdark on macOS

The Mac setup shares the WSL Starship prompt, terminal palette, and optional tmux
configuration. It uses Zsh and Homebrew. Ghostty is an optional terminal choice.
The same VS Code package offers Violet Afterdark and Violet AfterLight on macOS.

## Start on the Mac

Check the macOS version, architecture, and login shell before applying anything.

```zsh
sw_vers -productVersion
uname -m
printf '%s\n' "$SHELL"
command -v brew python3
```

Clone the private repository using your GitHub credentials. With Homebrew and
Python 3 installed, preview the changes, install the tools, and apply the config.
The Brewfile is separate so you can check it before downloading anything. The
bundle command skips upgrades of tools you already have.

```zsh
git clone https://github.com/berggrenmille/wsl-rice.git
cd wsl-rice
python3 scripts/macos.py preview
brew bundle install --no-upgrade --file=macos/Brewfile
python3 scripts/macos.py apply
```

Open a fresh Zsh tab. The installer adds a source line to `~/.zshrc` and copies
the configuration to `~/.config/violet-macos/`. Pass `--zshrc PATH` in both
commands if your active Zsh startup file is elsewhere. Review any existing prompt,
fzf, or zoxide setup in that file so each tool initializes once. Homebrew's
standard Apple Silicon and Intel locations are checked if `brew` is missing from
PATH. See [Homebrew installation](https://docs.brew.sh/Installation) for supported
macOS versions and [Brew Bundle](https://docs.brew.sh/Brew-Bundle-and-Brewfile)
for package options.

## Terminal appearance

Install the font with `brew install --cask font-0xproto-nerd-font`, then select
**0xProto Nerd Font Mono** in the terminal's preferences. Choose a dark terminal
profile for the prompt's neon accents. The font is available through [Homebrew](https://formulae.brew.sh/cask/font-0xproto-nerd-font).

If you use Ghostty, add `--ghostty` when previewing and applying to install the
Violet Afterdark color preset. In the Ghostty configuration file you already use,
add or update these settings and reload the configuration.

```ini
theme = Violet Afterdark
font-family = 0xProto Nerd Font Mono
font-size = 12
window-padding-x = 14
window-padding-y = 12
```

For fzf's `Alt-c` directory picker, Ghostty can use the left Option key as Alt
with `macos-option-as-alt = left`. This leaves the right Option key available for
typing symbols on a Swedish layout. See the [Ghostty configuration reference](https://ghostty.org/docs/config/reference).

## Everyday use

- `Ctrl-r` searches command history. `Ctrl-t` searches files and `Ctrl-/` toggles
  the preview while the picker is open. `z name` jumps to a remembered directory.
- `ll` lists files in detail and `lt` shows a two-level tree.
- For tmux, install it with `brew install tmux` and add `--tmux` when previewing
  and applying the config. Pass `--tmux-conf PATH` instead if tmux reads a custom
  config. `t` starts or reconnects to `dev`. Inside tmux, `Ctrl-b`, then `F1`
  opens help, `v` splits side by side, and `h` splits top and bottom. A running
  tmux server needs `tmux source-file ~/.tmux.conf` or the custom config path.
- For the optional system display, install `fastfetch` with Homebrew and run
  `violet-info` on demand.
- In VS Code, use **Extensions: Install from VSIX…** with the [shared package](../dist/violet-afterdark-0.2.0.vsix).
  Then choose **Violet Afterdark** or **Violet AfterLight** from **Preferences: Color Theme**.

## Restore

`python3 scripts/macos.py restore` restores the latest installer backup. Use
`--backup PATH` to choose an older manifest under `~/.local/state/violet-macos/backups/`.
If you applied several updates, restore their manifests in reverse order to
return to the original setup. The installer checks for later edits before writing.
Reset any manually edited Ghostty settings in Ghostty and select your original
theme in VS Code. Homebrew packages are managed separately.
