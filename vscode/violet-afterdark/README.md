# Violet Afterdark & AfterLight

Two coordinated purple themes in one extension:

- **Violet Afterdark**: near-black violet surfaces, neon violet accents, orchid
  types, cyan functions, and comfortable lavender text. Matches the WSL theme.
- **Violet AfterLight**: pale lavender surfaces, deep violet accents, dark orchid
  types, teal functions, and dark plum text. The integrated terminal is light too.

## Install

In VS Code, open the Command Palette and run **Extensions: Install from VSIX…**.
Choose `violet-afterdark-0.2.0.vsix`, then select **Violet Afterdark** or
**Violet AfterLight** from **Preferences: Color Theme**. On Windows, open the
picker with **Ctrl-K**, release, then **Ctrl-T**.

This updates the original extension rather than installing a second one. Your
currently selected theme remains selected after the update.

The extension colors the editor, tabs, sidebar, activity bar, status bar,
integrated terminal, diffs, search, menus, and common syntax and semantic tokens.
It contains only theme data. It has no executable extension code or dependencies
at runtime, and does not change your keyboard shortcuts, fonts, or settings.

## Suggested fonts

- Editor: JetBrains Mono.
- Integrated terminal: 0xProto Nerd Font Mono.

Fonts are optional and installed separately on the computer running VS Code.
To return to another look, choose any other theme from the Color Theme picker.

## Palette

| Role | Afterdark | AfterLight |
|---|---|---|
| Background | `#0D0914` | `#FAF7FD` |
| Surface | `#211332` | `#EDE4F4` |
| Violet | `#B56CFF` | `#7339B6` |
| Orchid | `#E06CDB` | `#963781` |
| Cyan / teal | `#62D6E8` | `#076F80` |
| Text | `#DDD5E8` | `#352441` |

AfterLight's syntax colors meet a 4.5:1 contrast target against the editor's
normal background. Selected primary interface text pairs meet 4.5:1 or better.
These measurements cover the theme's own colors, not every extension decoration
or highlighted combination. Terminal programs that emit explicit truecolor
values can keep their own palette; VS Code's
[minimum-contrast setting](https://code.visualstudio.com/docs/terminal/appearance)
helps keep terminal text readable.

Built for personal use and distributed as a local VSIX in the private
[wsl-rice repository](https://github.com/berggrenmille/wsl-rice).
