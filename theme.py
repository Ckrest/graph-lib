"""
Theme integration for graph styling.

Extracts colors from the current GTK/Adwaita theme.
"""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk


def rgba_to_tuple(rgba: Gdk.RGBA) -> tuple:
    """Convert Gdk.RGBA to (r, g, b, a) tuple with values 0-1."""
    return (rgba.red, rgba.green, rgba.blue, rgba.alpha)


def get_theme_colors() -> dict:
    """
    Extract colors from current GTK theme.

    Returns dict with color tuples (r, g, b, a) for common semantic colors.
    """
    # Default colors (Adwaita-like)
    colors = {
        "accent": (0.208, 0.518, 0.894, 1.0),  # Blue
        "success": (0.204, 0.659, 0.325, 1.0),  # Green
        "warning": (0.898, 0.612, 0.0, 1.0),  # Yellow/Orange
        "error": (0.753, 0.110, 0.157, 1.0),  # Red
        "text": (0.0, 0.0, 0.0, 1.0),
        "text_dim": (0.5, 0.5, 0.5, 1.0),
        "background": (1.0, 1.0, 1.0, 1.0),
        "surface": (0.98, 0.98, 0.98, 1.0),
    }

    # Try to get actual theme colors
    try:
        display = Gdk.Display.get_default()
        if display:
            # Check if dark mode
            settings = Gtk.Settings.get_default()
            if settings:
                prefer_dark = settings.get_property("gtk-application-prefer-dark-theme")
                if prefer_dark:
                    colors["text"] = (1.0, 1.0, 1.0, 1.0)
                    colors["text_dim"] = (0.7, 0.7, 0.7, 1.0)
                    colors["background"] = (0.12, 0.12, 0.12, 1.0)
                    colors["surface"] = (0.18, 0.18, 0.18, 1.0)
    except Exception:
        pass  # Use defaults

    return colors


def get_accent_color() -> tuple:
    """Get the accent color as (r, g, b) tuple."""
    colors = get_theme_colors()
    rgba = colors["accent"]
    return (rgba[0], rgba[1], rgba[2])


def get_text_color() -> tuple:
    """Get the text color as (r, g, b) tuple."""
    colors = get_theme_colors()
    rgba = colors["text"]
    return (rgba[0], rgba[1], rgba[2])
