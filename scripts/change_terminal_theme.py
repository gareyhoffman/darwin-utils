#!/usr/bin/env python3
"""
CLI tool for macOS Terminal.theme switching within the current session.

The script shells out to AppleScript (osascript) so it only works on macOS.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from textwrap import dedent


def run_osascript(source: str) -> subprocess.CompletedProcess[str]:
    """Execute AppleScript via osascript and return the completed process."""
    return subprocess.run(
        ["osascript", "-e", source],
        check=False,
        text=True,
        capture_output=True,
    )


def list_themes() -> list[str]:
    """Return available Terminal themes."""
    script = dedent(
        """
        set text item delimiters to "\\n"
        tell application "Terminal"
            set themeNames to name of settings sets
        end tell
        return themeNames as text
        """
    ).strip()
    result = run_osascript(script)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Unable to read Terminal themes.")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def escape_applescript_string(text: str) -> str:
    """Escape characters that would break AppleScript string literals."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def apply_theme(theme: str) -> None:
    """Apply the theme to the current Terminal window."""
    escaped_theme = escape_applescript_string(theme)
    script = dedent(
        f'''
        on run
            tell application "Terminal"
                if not (exists settings set "{escaped_theme}") then
                    error "Terminal theme '{escaped_theme}' not found."
                end if

                if (count of windows) is 0 then
                    do script ""
                end if

                set current settings of front window to settings set "{escaped_theme}"
                activate
            end tell
        end run
        '''
    ).strip()
    result = run_osascript(script)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to change Terminal theme.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Change the macOS Terminal theme for the active session.",
    )
    parser.add_argument(
        "theme",
        nargs="?",
        help="Name of the Terminal theme to apply (see `--list`).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_themes",
        help="List available Terminal themes and exit.",
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

    if not args.theme:
        print("Error: theme name is required (see `--list`).", file=sys.stderr)
        return 1

    try:
        apply_theme(args.theme)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
