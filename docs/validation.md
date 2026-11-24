# Validation record

Validated on 2026-11-24 with Ubuntu 24.04 on WSL2, Bash, Starship 1.23.0,
fastfetch 2.71.0, tmux 3.4, fzf 0.75.0, zoxide 0.10.0, and bat 0.26.1.

- Automated tests: 4 passed. Covers repeat application, original bytes
  and modes, symlinks, later-edit conflicts, JSONC parsing, profile selection,
  unrelated Windows Terminal profiles, repeat merging, and fresh-shell NVM PATH
  resolution (major-version boundaries, LTS aliases, and inherited versions).
- Bash syntax check passed.
- A temporary-home installation loaded the theme and built bat's theme cache.
- fzf accepted its theme options; history/file search integration loaded.
- Starship rendered C++, CMake, and .NET fixture prompts without warnings.
- An isolated tmux server loaded the configuration and reported the expected
  status-bar colors. The test server was stopped afterward.
- The live installation changed only the selected Ubuntu profile and added the
  Violet Afterdark color scheme; the Windows Terminal default profile was retained.
- NVM deferred initialization worked: the first Node command loaded NVM, removed
  the wrapper functions, and selected Node 20.19.6. npm 11.21.3 remained available.
- With inherited NVM paths removed, a new shell found and ran Codex 0.172.0 before
  loading NVM, then successfully loaded NVM on the first Node command.
- Windows reported `0xProto Nerd Font Mono` as an installed font family.
- GCC 15.2.0, Rust 1.94.1, and .NET SDK 10.0.115 remained available.

## Startup timing

Measured wall time for `bash -i -c exit` with output redirected, so these numbers
exclude drawing the greeting, terminal-window startup, and the first Node command.
This compares shell configuration loading on the same machine, not full startup
latency on every machine.

| Configuration | Samples | Median |
|---|---:|---:|
| Previous setup | 3 | 438 ms |
| Violet Afterdark | 5 | 124 ms |

About 72% less startup time in this measurement. The final samples removed
inherited NVM PATH entries to exercise fresh-tab version resolution. NVM
initialization is deferred, not eliminated. The first Node/NVM command still pays
that cost.

## Visual review

The SVG in `assets/preview.svg` illustrates the palette and intended composition.
Actual Windows Terminal font rendering, acrylic, and desktop compositing need a
fresh Ubuntu tab on Windows to judge; the SVG is not evidence of a captured desktop.
