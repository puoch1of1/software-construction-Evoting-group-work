"""
Console output utilities for formatted display.
Handles all visual presentation in the terminal.
"""

import os
from .colors import (
    RESET, BOLD, DIM, RED, GREEN, YELLOW, GRAY, BRIGHT_WHITE
)
from ..config import HEADER_WIDTH


def colored(text, color):
    """Wrap text with ANSI color codes."""
    return f"{color}{text}{RESET}"


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pause():
    """Wait for user to press Enter."""
    input(f"\n  {DIM}Press Enter to continue...{RESET}")


def header(title, theme_color):
    """Display a prominent header with borders."""
    top = f"  {theme_color}{'═' * HEADER_WIDTH}{RESET}"
    mid = f"  {theme_color}{BOLD} {title.center(HEADER_WIDTH - 2)} {RESET}{theme_color} {RESET}"
    bot = f"  {theme_color}{'═' * HEADER_WIDTH}{RESET}"
    print(top)
    print(mid)
    print(bot)


def subheader(title, theme_color):
    """Display a subsection header."""
    print(f"\n  {theme_color}{BOLD}▸ {title}{RESET}")


def table_header(format_str, theme_color):
    """Display a table header row."""
    print(f"  {theme_color}{BOLD}{format_str}{RESET}")


def table_divider(width, theme_color):
    """Display a table divider line."""
    print(f"  {theme_color}{'─' * width}{RESET}")


def error(msg):
    """Display an error message."""
    print(f"  {RED}{BOLD} {msg}{RESET}")


def success(msg):
    """Display a success message."""
    print(f"  {GREEN}{BOLD} {msg}{RESET}")


def warning(msg):
    """Display a warning message."""
    print(f"  {YELLOW}{BOLD} {msg}{RESET}")


def info(msg):
    """Display an informational message."""
    print(f"  {GRAY}{msg}{RESET}")


def menu_item(number, text, color):
    """Display a numbered menu option."""
    print(f"  {color}{BOLD}{number:>3}.{RESET}  {text}")


def status_badge(text, is_good):
    """Return colored status text."""
    if is_good:
        return f"{GREEN}{text}{RESET}"
    return f"{RED}{text}{RESET}"


def prompt(text):
    """Display a prompt and get user input."""
    return input(f"  {BRIGHT_WHITE}{text}{RESET}").strip()
