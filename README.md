# darwin-utils

macOS terminal utilities.

## Scripts

### change_terminal_theme.py

Switch macOS Terminal.app themes via AppleScript.

```bash
./scripts/change_terminal_theme.py --list          # List available themes
./scripts/change_terminal_theme.py "Pro"           # Apply a theme
```

### change_ghostty_theme.py

Switch [Ghostty](https://ghostty.org) themes by updating the config and triggering a live reload.

```bash
./scripts/change_ghostty_theme.py --list           # List available themes
./scripts/change_ghostty_theme.py "Catppuccin Mocha"  # Apply a theme
./scripts/change_ghostty_theme.py --current        # Show current theme
```

## Requirements

- macOS
- Python 3.9+
- Ghostty (for the Ghostty script)

## License

Apache 2.0
