"""
Gauge/meter renderer using Cairo.

Renders a single value as a circular arc gauge.
"""

import math
from typing import Tuple

from .base import GraphRenderer


class GaugeRenderer(GraphRenderer):
    """Circular gauge/meter for displaying single values."""

    def __init__(self):
        super().__init__()

        # Default configuration
        self.config = {
            # Value range
            "min_value": 0,
            "max_value": 100,
            # Thresholds for color changes
            "warning_threshold": 70,
            "critical_threshold": 90,
            # Colors
            "normal_color": (0.204, 0.659, 0.325),  # Green
            "warning_color": (0.898, 0.612, 0.0),   # Orange
            "critical_color": (0.753, 0.110, 0.157), # Red
            "background_color": (0.3, 0.3, 0.3, 0.3),
            "text_color": (0.2, 0.2, 0.2),
            # Appearance
            "arc_width": 0.15,  # Proportion of radius
            "start_angle": 135,  # Degrees from right, counter-clockwise
            "sweep_angle": 270,  # Total arc sweep in degrees
            # Label
            "show_value": True,
            "value_format": "{:.0f}",
            "label": None,
        }

    def render(self, cr, width: int, height: int):
        """Render the gauge to a Cairo context."""
        # Get current value (use latest data point if available)
        if self.data:
            value = self.data[-1].value
        else:
            value = self.config["min_value"]

        # Calculate dimensions
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 10
        arc_width = radius * self.config["arc_width"]

        if radius <= 0:
            return

        # Convert angles to radians
        start_angle = math.radians(self.config["start_angle"])
        sweep_angle = math.radians(self.config["sweep_angle"])

        # Draw background arc
        self._draw_arc(
            cr, center_x, center_y, radius, arc_width,
            start_angle, sweep_angle,
            self.config["background_color"]
        )

        # Calculate value proportion
        min_val = self.config["min_value"]
        max_val = self.config["max_value"]
        proportion = (value - min_val) / (max_val - min_val)
        proportion = max(0, min(1, proportion))  # Clamp 0-1

        # Determine color based on thresholds
        color = self._get_value_color(value)

        # Draw value arc
        value_sweep = sweep_angle * proportion
        self._draw_arc(
            cr, center_x, center_y, radius, arc_width,
            start_angle, value_sweep,
            (*color, 1.0)
        )

        # Draw value text
        if self.config["show_value"]:
            self._draw_value_text(cr, center_x, center_y, value, radius)

        # Draw label
        if self.config["label"]:
            self._draw_label(cr, center_x, center_y, radius)

    def _draw_arc(
        self, cr, cx: float, cy: float, radius: float, width: float,
        start: float, sweep: float, color: Tuple
    ):
        """Draw an arc segment."""
        cr.set_line_width(width)
        cr.set_line_cap(1)  # Round cap

        if len(color) == 4:
            cr.set_source_rgba(*color)
        else:
            cr.set_source_rgb(*color)

        # Cairo arcs go clockwise, we want counter-clockwise feel
        # Adjust by starting from bottom-left and going clockwise
        cr.arc(cx, cy, radius - width / 2, start, start + sweep)
        cr.stroke()

    def _get_value_color(self, value: float) -> Tuple[float, float, float]:
        """Get color based on value thresholds."""
        if value >= self.config["critical_threshold"]:
            return self.config["critical_color"]
        elif value >= self.config["warning_threshold"]:
            return self.config["warning_color"]
        else:
            return self.config["normal_color"]

    def _draw_value_text(self, cr, cx: float, cy: float, value: float, radius: float):
        """Draw the value in the center of the gauge."""
        text = self.config["value_format"].format(value)

        cr.set_source_rgb(*self.config["text_color"])
        cr.select_font_face("Sans", 0, 1)  # Normal, Bold
        cr.set_font_size(radius * 0.4)

        extents = cr.text_extents(text)
        x = cx - extents.width / 2
        y = cy + extents.height / 3

        cr.move_to(x, y)
        cr.show_text(text)

    def _draw_label(self, cr, cx: float, cy: float, radius: float):
        """Draw the label below the value."""
        text = self.config["label"]

        cr.set_source_rgba(*self.config["text_color"], 0.7)
        cr.select_font_face("Sans")
        cr.set_font_size(radius * 0.15)

        extents = cr.text_extents(text)
        x = cx - extents.width / 2
        y = cy + radius * 0.35

        cr.move_to(x, y)
        cr.show_text(text)
