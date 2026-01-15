"""
Line chart renderer using Cairo.

Renders time series data as a connected line with optional fill,
labels, axis ticks, and configurable appearance.
"""

import math
from datetime import datetime
from typing import List, Optional, Tuple, Callable

from .base import GraphRenderer
from ..providers.base import DataPoint


class LineChartRenderer(GraphRenderer):
    """
    Time series line chart with labels, axes, and gradient fill.

    Configuration options:
        # Labels
        title: str - Chart title (top center)
        y_label: str - Y-axis label (left side, rotated)
        x_label: str - X-axis label (bottom center)
        unit: str - Unit suffix for Y values (e.g., "ms", "%", "MB")

        # Line styling
        line_color: tuple - RGB color for line
        line_width: float - Line thickness
        show_fill: bool - Fill area under line
        fill_color: tuple - RGBA color for fill

        # Axes
        y_min: float - Minimum Y value (None = auto)
        y_max: float - Maximum Y value (None = auto)
        show_axes: bool - Draw axis lines
        axis_color: tuple - RGBA color for axes

        # Grid
        show_grid: bool - Draw grid lines
        grid_color: tuple - RGBA color for grid
        grid_lines: int - Number of horizontal grid lines

        # Tick labels
        show_y_ticks: bool - Show Y axis value labels
        show_x_ticks: bool - Show X axis time labels
        tick_color: tuple - RGB color for tick labels
        y_tick_format: str - Format string for Y values (e.g., "{:.1f}")
        x_tick_format: str - Time format ("auto", "time", "date", "datetime")

        # Current value
        show_current: bool - Show current value in corner
        current_position: str - "top-right", "top-left", "bottom-right", "bottom-left"

        # Layout
        margin_top: int - Top margin (auto-calculated if None)
        margin_bottom: int - Bottom margin
        margin_left: int - Left margin
        margin_right: int - Right margin

        # Points
        show_points: bool - Draw circles at data points
        point_radius: float - Radius of point circles
    """

    def __init__(self):
        super().__init__()

        # Default configuration
        self.config = {
            # Labels
            "title": None,
            "y_label": None,
            "x_label": None,
            "unit": "",

            # Line styling
            "line_color": (0.208, 0.518, 0.894),  # Adwaita blue
            "line_width": 2.0,
            "show_fill": True,
            "fill_color": (0.208, 0.518, 0.894, 0.2),

            # Axes
            "y_min": None,
            "y_max": None,
            "show_axes": True,
            "axis_color": (0.4, 0.4, 0.4, 0.8),

            # Grid
            "show_grid": True,
            "grid_color": (0.5, 0.5, 0.5, 0.15),
            "grid_lines": 4,

            # Tick labels
            "show_y_ticks": True,
            "show_x_ticks": True,
            "tick_color": (0.4, 0.4, 0.4),
            "tick_font_size": 10,
            "y_tick_format": "{:.0f}",
            "x_tick_format": "auto",  # "auto", "time", "date", "datetime", "seconds"

            # Current value display
            "show_current": False,
            "current_position": "top-right",
            "current_format": "{:.1f}",
            "current_font_size": 14,

            # Layout (None = auto-calculate)
            "margin_top": None,
            "margin_bottom": None,
            "margin_left": None,
            "margin_right": None,
            "padding": 8,  # Inner padding

            # Points
            "show_points": False,
            "point_radius": 3,
        }

    def render(self, cr, width: int, height: int):
        """Render the line chart to a Cairo context."""
        if not self.data:
            self._render_empty(cr, width, height)
            return

        # Calculate margins based on what's shown
        margins = self._calculate_margins(cr)
        chart_x = margins["left"]
        chart_y = margins["top"]
        chart_width = width - margins["left"] - margins["right"]
        chart_height = height - margins["top"] - margins["bottom"]

        if chart_width <= 0 or chart_height <= 0:
            return

        # Calculate data ranges
        y_min, y_max = self._calculate_y_range()
        x_min, x_max = self._calculate_x_range()

        # Draw components back-to-front
        if self.config["show_grid"]:
            self._render_grid(cr, chart_x, chart_y, chart_width, chart_height, y_min, y_max)

        if self.config["show_axes"]:
            self._render_axes(cr, chart_x, chart_y, chart_width, chart_height)

        if self.config["show_y_ticks"]:
            self._render_y_ticks(cr, chart_x, chart_y, chart_width, chart_height, y_min, y_max)

        if self.config["show_x_ticks"]:
            self._render_x_ticks(cr, chart_x, chart_y, chart_width, chart_height, x_min, x_max)

        # Convert data to pixel coordinates
        points = self._data_to_pixels(
            chart_x, chart_y, chart_width, chart_height,
            x_min, x_max, y_min, y_max
        )

        # Draw data
        if self.config["show_fill"] and len(points) >= 2:
            self._render_fill(cr, points, chart_y, chart_height)

        self._render_line(cr, points)

        if self.config["show_points"]:
            self._render_points(cr, points)

        # Draw labels
        if self.config["title"]:
            self._render_title(cr, width, margins["top"])

        if self.config["y_label"]:
            self._render_y_label(cr, height, margins["left"])

        if self.config["x_label"]:
            self._render_x_label(cr, width, height, margins["bottom"])

        if self.config["show_current"]:
            self._render_current_value(cr, width, height, margins)

    def _calculate_margins(self, cr) -> dict:
        """Calculate margins based on what elements are shown."""
        cfg = self.config

        # Start with defaults
        top = cfg["margin_top"] if cfg["margin_top"] is not None else cfg["padding"]
        bottom = cfg["margin_bottom"] if cfg["margin_bottom"] is not None else cfg["padding"]
        left = cfg["margin_left"] if cfg["margin_left"] is not None else cfg["padding"]
        right = cfg["margin_right"] if cfg["margin_right"] is not None else cfg["padding"]

        # Add space for title
        if cfg["title"]:
            top = max(top, 24)

        # Add space for Y tick labels
        if cfg["show_y_ticks"]:
            # Estimate width needed for Y labels
            cr.set_font_size(cfg["tick_font_size"])
            sample = cfg["y_tick_format"].format(9999.9) + cfg["unit"]
            extents = cr.text_extents(sample)
            left = max(left, extents.width + 12)

        # Add space for Y axis label
        if cfg["y_label"]:
            left += 18

        # Add space for X tick labels
        if cfg["show_x_ticks"]:
            bottom = max(bottom, 22)

        # Add space for X axis label
        if cfg["x_label"]:
            bottom += 16

        return {"top": top, "bottom": bottom, "left": left, "right": right}

    def _calculate_y_range(self) -> Tuple[float, float]:
        """Calculate Y axis range from data or config."""
        values = [p.value for p in self.data]

        y_min = self.config["y_min"]
        y_max = self.config["y_max"]

        if y_min is None:
            y_min = min(values)
            y_range = max(values) - y_min
            y_min = max(0, y_min - y_range * 0.1)

        if y_max is None:
            y_max = max(values)
            y_range = y_max - min(values)
            y_max = y_max + y_range * 0.1

        # Ensure non-zero range
        if y_max == y_min:
            y_max = y_min + 1

        return y_min, y_max

    def _calculate_x_range(self) -> Tuple[float, float]:
        """Calculate X axis range from data."""
        x_min = min(p.timestamp for p in self.data)
        x_max = max(p.timestamp for p in self.data)

        if x_max == x_min:
            x_max = x_min + 1

        return x_min, x_max

    def _data_to_pixels(
        self, chart_x, chart_y, chart_width, chart_height,
        x_min, x_max, y_min, y_max
    ) -> List[Tuple[float, float]]:
        """Convert data points to pixel coordinates."""
        points = []
        for dp in self.data:
            x = chart_x + (dp.timestamp - x_min) / (x_max - x_min) * chart_width
            y = chart_y + (1 - (dp.value - y_min) / (y_max - y_min)) * chart_height
            points.append((x, y))
        return points

    def _render_empty(self, cr, width: int, height: int):
        """Render placeholder when no data."""
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.1)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        cr.set_source_rgba(0.5, 0.5, 0.5, 0.5)
        cr.select_font_face("Sans")
        cr.set_font_size(12)

        text = "No data"
        extents = cr.text_extents(text)
        cr.move_to((width - extents.width) / 2, (height + extents.height) / 2)
        cr.show_text(text)

    def _render_grid(self, cr, x, y, width, height, y_min, y_max):
        """Draw horizontal grid lines."""
        cr.set_source_rgba(*self.config["grid_color"])
        cr.set_line_width(1)

        num_lines = self.config["grid_lines"]
        for i in range(num_lines + 1):
            line_y = y + (i / num_lines) * height
            cr.move_to(x, line_y)
            cr.line_to(x + width, line_y)
            cr.stroke()

    def _render_axes(self, cr, x, y, width, height):
        """Draw axis lines."""
        cr.set_source_rgba(*self.config["axis_color"])
        cr.set_line_width(1)

        # Y axis (left)
        cr.move_to(x, y)
        cr.line_to(x, y + height)
        cr.stroke()

        # X axis (bottom)
        cr.move_to(x, y + height)
        cr.line_to(x + width, y + height)
        cr.stroke()

    def _render_y_ticks(self, cr, x, y, width, height, y_min, y_max):
        """Draw Y axis tick labels."""
        cr.set_source_rgb(*self.config["tick_color"])
        cr.select_font_face("Sans")
        cr.set_font_size(self.config["tick_font_size"])

        num_ticks = self.config["grid_lines"]
        fmt = self.config["y_tick_format"]
        unit = self.config["unit"]

        for i in range(num_ticks + 1):
            # Calculate value at this tick
            value = y_max - (i / num_ticks) * (y_max - y_min)
            label = fmt.format(value) + unit

            # Position
            tick_y = y + (i / num_ticks) * height
            extents = cr.text_extents(label)

            cr.move_to(x - extents.width - 4, tick_y + extents.height / 2 - 1)
            cr.show_text(label)

    def _render_x_ticks(self, cr, x, y, width, height, x_min, x_max):
        """Draw X axis time labels."""
        cr.set_source_rgb(*self.config["tick_color"])
        cr.select_font_face("Sans")
        cr.set_font_size(self.config["tick_font_size"])

        # Determine time format
        fmt = self.config["x_tick_format"]
        duration = x_max - x_min

        if fmt == "auto":
            if duration < 120:  # Less than 2 minutes
                fmt = "seconds"
            elif duration < 7200:  # Less than 2 hours
                fmt = "time"
            elif duration < 172800:  # Less than 2 days
                fmt = "datetime"
            else:
                fmt = "date"

        # Draw ticks at start, middle, end
        for i, t in enumerate([x_min, (x_min + x_max) / 2, x_max]):
            label = self._format_time(t, fmt)
            tick_x = x + (t - x_min) / (x_max - x_min) * width
            extents = cr.text_extents(label)

            # Adjust position based on which tick
            if i == 0:
                text_x = tick_x
            elif i == 2:
                text_x = tick_x - extents.width
            else:
                text_x = tick_x - extents.width / 2

            cr.move_to(text_x, y + height + extents.height + 4)
            cr.show_text(label)

    def _format_time(self, timestamp: float, fmt: str) -> str:
        """Format a timestamp for display."""
        dt = datetime.fromtimestamp(timestamp)

        if fmt == "seconds":
            return dt.strftime("%H:%M:%S")
        elif fmt == "time":
            return dt.strftime("%H:%M")
        elif fmt == "date":
            return dt.strftime("%m/%d")
        elif fmt == "datetime":
            return dt.strftime("%m/%d %H:%M")
        else:
            return dt.strftime(fmt)

    def _render_title(self, cr, width, margin_top):
        """Draw chart title."""
        cr.set_source_rgb(*self.config["tick_color"])
        cr.select_font_face("Sans", 0, 1)  # Bold
        cr.set_font_size(13)

        title = self.config["title"]
        extents = cr.text_extents(title)
        cr.move_to((width - extents.width) / 2, margin_top - 8)
        cr.show_text(title)

    def _render_y_label(self, cr, height, margin_left):
        """Draw Y axis label (rotated)."""
        cr.set_source_rgb(*self.config["tick_color"])
        cr.select_font_face("Sans")
        cr.set_font_size(11)

        label = self.config["y_label"]
        extents = cr.text_extents(label)

        cr.save()
        cr.translate(12, height / 2 + extents.width / 2)
        cr.rotate(-math.pi / 2)
        cr.move_to(0, 0)
        cr.show_text(label)
        cr.restore()

    def _render_x_label(self, cr, width, height, margin_bottom):
        """Draw X axis label."""
        cr.set_source_rgb(*self.config["tick_color"])
        cr.select_font_face("Sans")
        cr.set_font_size(11)

        label = self.config["x_label"]
        extents = cr.text_extents(label)
        cr.move_to((width - extents.width) / 2, height - 4)
        cr.show_text(label)

    def _render_current_value(self, cr, width, height, margins):
        """Draw current value indicator."""
        if not self.data:
            return

        current = self.data[-1].value
        fmt = self.config["current_format"]
        unit = self.config["unit"]
        label = fmt.format(current) + unit

        cr.select_font_face("Sans", 0, 1)  # Bold
        cr.set_font_size(self.config["current_font_size"])
        extents = cr.text_extents(label)

        pos = self.config["current_position"]
        padding = 8

        if "right" in pos:
            x = width - margins["right"] - extents.width - padding
        else:
            x = margins["left"] + padding

        if "top" in pos:
            y = margins["top"] + extents.height + padding
        else:
            y = height - margins["bottom"] - padding

        # Background
        cr.set_source_rgba(1, 1, 1, 0.8)
        cr.rectangle(x - 4, y - extents.height - 2, extents.width + 8, extents.height + 6)
        cr.fill()

        # Text
        cr.set_source_rgb(*self.config["line_color"])
        cr.move_to(x, y)
        cr.show_text(label)

    def _render_fill(self, cr, points, chart_y, chart_height):
        """Draw filled area under the line."""
        bottom_y = chart_y + chart_height

        cr.move_to(points[0][0], bottom_y)
        cr.line_to(points[0][0], points[0][1])

        for x, y in points[1:]:
            cr.line_to(x, y)

        cr.line_to(points[-1][0], bottom_y)
        cr.close_path()

        cr.set_source_rgba(*self.config["fill_color"])
        cr.fill()

    def _render_line(self, cr, points):
        """Draw the main line connecting points."""
        if len(points) < 2:
            return

        cr.set_source_rgb(*self.config["line_color"])
        cr.set_line_width(self.config["line_width"])
        cr.set_line_join(1)  # Round
        cr.set_line_cap(1)

        cr.move_to(points[0][0], points[0][1])
        for x, y in points[1:]:
            cr.line_to(x, y)
        cr.stroke()

    def _render_points(self, cr, points):
        """Draw circles at each data point."""
        cr.set_source_rgb(*self.config["line_color"])
        radius = self.config["point_radius"]

        for x, y in points:
            cr.arc(x, y, radius, 0, 2 * math.pi)
            cr.fill()
