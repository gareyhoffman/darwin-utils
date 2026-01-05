#!/usr/bin/env python3
"""
CLI tool for Ghostty theme switching.

Changes the theme in the Ghostty config file and sends SIGUSR2 to reload.
"""

from __future__ import annotations

import argparse
import os
import re
import signal
import subprocess
import sys
from pathlib import Path


def get_config_path() -> Path:
    """Return the Ghostty config file path."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return Path(xdg_config) / "ghostty" / "config"


def list_themes() -> list[str]:
    """Return available Ghostty themes."""
    result = subprocess.run(
        ["ghostty", "+list-themes"],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Unable to list Ghostty themes.")

    themes = []
    for line in result.stdout.splitlines():
        # Theme lines look like: "Theme Name (resources)" or "Theme Name (custom)"
        line = line.strip()
        if line:
            # Remove the source indicator in parentheses
            match = re.match(r"^(.+?)\s*\((resources|custom)\)$", line)
            if match:
                themes.append(match.group(1).strip())
            else:
                themes.append(line)
    return themes


def get_current_theme(config_path: Path) -> str | None:
    """Read the current theme from config, if any."""
    if not config_path.exists():
        return None

    content = config_path.read_text()
    # Match 'theme = value' but not commented lines
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#"):
            continue
        match = re.match(r"^theme\s*=\s*(.+)$", line)
        if match:
            return match.group(1).strip()
    return None


def apply_theme(theme: str) -> None:
    """Apply the theme by updating config and signaling Ghostty to reload."""
    available = list_themes()
    if theme not in available:
        raise RuntimeError(f"Theme '{theme}' not found. Use --list to see available themes.")

    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        content = config_path.read_text()
        # Replace existing theme line or add one
        if re.search(r"^theme\s*=", content, re.MULTILINE):
            content = re.sub(
                r"^theme\s*=.*$",
                f"theme = {theme}",
                content,
                flags=re.MULTILINE,
            )
        else:
            content = f"theme = {theme}\n{content}"
    else:
        content = f"theme = {theme}\n"

    config_path.write_text(content)

    # Signal Ghostty to reload config
    result = subprocess.run(
        ["pgrep", "-x", "ghostty"],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        for pid in result.stdout.strip().splitlines():
            try:
                os.kill(int(pid), signal.SIGUSR2)
            except (ProcessLookupError, ValueError):
                pass


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Change the Ghostty terminal theme.",
    )
    parser.add_argument(
        "theme",
        nargs="?",
        help="Name of the theme to apply (see `--list`).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_themes",
        help="List available themes and exit.",
    )
    parser.add_argument(
        "--current",
        action="store_true",
        help="Show current theme and exit.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    if args.list_themes:
        try:
            for theme_name in list_themes():
                print(theme_name)
        except RuntimeError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.current:
        current = get_current_theme(get_config_path())
        if current:
            print(current)
        else:
            print("No theme set")
        return 0

    if not args.theme:
        print("Error: theme name is required (see `--list`).", file=sys.stderr)
        return 1

    try:
        apply_theme(args.theme)
        print(f"Switched to theme: {args.theme}")
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
