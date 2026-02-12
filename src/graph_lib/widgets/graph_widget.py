"""
GTK4 widget wrapper for graphs.

Combines a renderer with a data provider into an embeddable widget.
Provides methods for runtime configuration and control.
"""

import logging
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

from ..providers.base import DataProvider
from ..renderers.base import GraphRenderer
from typing import Callable, Optional, Any

logger = logging.getLogger(__name__)


class GraphWidget(Gtk.DrawingArea):
    """
    Embeddable GTK4 widget combining renderer and data provider.

    Provides runtime configuration methods for:
    - Changing renderer settings (colors, labels, axes)
    - Adjusting refresh rate
    - Swapping providers
    - Manual refresh

    Hooks/callbacks for:
    - on_data_update: Called when new data is fetched
    - on_error: Called when provider fails
    """

    def __init__(
        self,
        renderer: GraphRenderer,
        provider: DataProvider,
        refresh_interval_ms: int = 1000,
    ):
        super().__init__()

        self.renderer = renderer
        self.provider = provider
        self.refresh_interval_ms = refresh_interval_ms
        self._timer_id = None
        self._started = False

        # Hooks
        self._on_data_hook: Optional[Callable] = None
        self._on_error_hook: Optional[Callable] = None

        # GTK4 uses set_draw_func instead of connect("draw", ...)
        self.set_draw_func(self._on_draw)

        # Default size
        self.set_size_request(200, 100)
        self.set_hexpand(True)
        self.set_vexpand(True)

    # --- Configuration Methods ---

    def configure(self, **kwargs):
        """
        Update renderer configuration at runtime.

        Example:
            graph.configure(
                title="CPU Usage",
                y_label="Percent",
                unit="%",
                y_min=0,
                y_max=100,
                show_current=True,
            )
        """
        self.renderer.configure(**kwargs)
        self.queue_draw()

    def set_title(self, title: str):
        """Set chart title."""
        self.configure(title=title)

    def set_y_label(self, label: str):
        """Set Y-axis label."""
        self.configure(y_label=label)

    def set_x_label(self, label: str):
        """Set X-axis label."""
        self.configure(x_label=label)

    def set_unit(self, unit: str):
        """Set unit suffix for values (e.g., 'ms', '%', 'MB')."""
        self.configure(unit=unit)

    def set_y_range(self, y_min: float = None, y_max: float = None):
        """
        Set Y-axis range. Pass None for auto-calculate.

        Example:
            graph.set_y_range(0, 100)  # Fixed 0-100
            graph.set_y_range(y_min=0)  # Auto max, fixed min at 0
            graph.set_y_range()  # Full auto
        """
        self.configure(y_min=y_min, y_max=y_max)

    def set_color(self, color: tuple, fill_color: tuple = None):
        """
        Set line and fill colors.

        Args:
            color: RGB tuple (0-1) for line
            fill_color: RGBA tuple (0-1) for fill, or None to auto-generate
        """
        if fill_color is None:
            fill_color = (*color, 0.15)
        self.configure(line_color=color, fill_color=fill_color)

    def show_current_value(self, show: bool = True, position: str = "top-right"):
        """
        Toggle current value display.

        Args:
            show: Whether to show
            position: "top-right", "top-left", "bottom-right", "bottom-left"
        """
        self.configure(show_current=show, current_position=position)

    def set_grid(self, show: bool = True, lines: int = 4):
        """Configure grid display."""
        self.configure(show_grid=show, grid_lines=lines)

    def set_axes(self, show: bool = True):
        """Toggle axis lines."""
        self.configure(show_axes=show)

    def set_ticks(self, y_ticks: bool = True, x_ticks: bool = True):
        """Toggle axis tick labels."""
        self.configure(show_y_ticks=y_ticks, show_x_ticks=x_ticks)

    # --- Provider/Refresh Control ---

    def set_refresh_interval(self, ms: int):
        """Change refresh interval. Takes effect on next timer cycle."""
        self.refresh_interval_ms = ms

        # Restart timer if running
        if self._started and self._timer_id:
            GLib.source_remove(self._timer_id)
            if ms > 0:
                self._timer_id = GLib.timeout_add(ms, self._on_timer)

    def set_provider(self, provider: DataProvider):
        """
        Swap data provider at runtime.

        Stops the old provider and starts the new one if widget is active.
        """
        was_started = self._started

        if was_started:
            self.provider.stop()
            self.provider.unsubscribe()

        self.provider = provider

        if was_started:
            self.provider.subscribe(self._on_data_update)
            self.provider.start()
            self._refresh()

    def refresh(self):
        """Manually trigger a data refresh and redraw."""
        self._refresh()

    # --- Hooks ---

    def on_data(self, callback: Callable[[list], None]):
        """
        Set callback for data updates.

        Callback receives list of DataPoints after each fetch.
        """
        self._on_data_hook = callback

    def on_error(self, callback: Callable[[Exception], None]):
        """Set callback for provider errors."""
        self._on_error_hook = callback

    # --- Lifecycle ---

    def start(self):
        """Start auto-refresh timer and provider."""
        if self._started:
            return

        self._started = True

        # Subscribe to real-time updates
        self.provider.subscribe(self._on_data_update)
        self.provider.start()

        # Initial fetch
        self._refresh()

        # Start periodic refresh
        if self.refresh_interval_ms > 0:
            self._timer_id = GLib.timeout_add(
                self.refresh_interval_ms, self._on_timer
            )

    def stop(self):
        """Stop auto-refresh and provider."""
        if not self._started:
            return

        self._started = False

        if self._timer_id:
            GLib.source_remove(self._timer_id)
            self._timer_id = None

        self.provider.stop()
        self.provider.unsubscribe()

    @property
    def is_running(self) -> bool:
        """Check if the graph is actively updating."""
        return self._started

    @property
    def current_data(self) -> list:
        """Get the current data points from renderer."""
        return self.renderer.data

    @property
    def current_value(self) -> Optional[float]:
        """Get the most recent data value, or None if no data."""
        if self.renderer.data:
            return self.renderer.data[-1].value
        return None

    # --- Internal ---

    def _on_draw(self, area, cr, width, height):
        """Called when widget needs redrawing."""
        self.renderer.render(cr, width, height)

    def _on_timer(self):
        """Periodic refresh callback."""
        if not self._started:
            return False  # Stop timer

        self._refresh()
        return True  # Continue timer

    def _refresh(self):
        """Fetch data and redraw."""
        try:
            data = self.provider.fetch()
            self.renderer.set_data(data)
            self.queue_draw()

            if self._on_data_hook:
                self._on_data_hook(data)

        except Exception as e:
            logger.exception("Graph refresh failed: %s", e)
            if self._on_error_hook:
                self._on_error_hook(e)

    def _on_data_update(self, data):
        """Real-time update callback from provider."""
        self.renderer.set_data(data)
        GLib.idle_add(self.queue_draw)

        if self._on_data_hook:
            GLib.idle_add(self._on_data_hook, data)
