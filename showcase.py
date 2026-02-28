#!/usr/bin/env python3
"""
graph-lib Feature Showcase

Renders a GTK4 window demonstrating all graph types, customization
options, and display features. Screenshot this window for the README.

Usage:
    python showcase.py
"""

import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Pango

from graph_lib.widgets.graph_widget import GraphWidget
from graph_lib.renderers.line_chart import LineChartRenderer
from graph_lib.renderers.gauge import GaugeRenderer
from graph_lib.providers.static_provider import StaticProvider
from graph_lib.providers.base import DataPoint


class ShowcaseWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("graph-lib \u2014 Feature Showcase")
        self.set_default_size(1050, 680)

        self._graphs = []

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        header = Adw.HeaderBar()
        main_box.append(header)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        content.set_margin_start(16)
        content.set_margin_end(16)
        main_box.append(content)

        # --- Row 1: Line Charts ---
        row1_label = Gtk.Label(label="Line Charts")
        row1_label.set_halign(Gtk.Align.START)
        row1_label.add_css_class("title-4")
        content.append(row1_label)

        row1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row1.set_homogeneous(True)
        content.append(row1)

        # 1) Sine wave — full labels
        row1.append(self._make_line_chart_full())

        # 2) Random walk — minimal/clean
        row1.append(self._make_line_chart_minimal())

        # 3) Linear ramp — custom colors
        row1.append(self._make_line_chart_custom())

        # --- Row 2: Gauges + compact chart ---
        row2_label = Gtk.Label(label="Gauges & Compact Widgets")
        row2_label.set_halign(Gtk.Align.START)
        row2_label.add_css_class("title-4")
        content.append(row2_label)

        row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row2.set_vexpand(True)
        content.append(row2)

        # Gauges
        gauge_grid = Gtk.Grid()
        gauge_grid.set_row_spacing(12)
        gauge_grid.set_column_spacing(12)
        gauge_grid.set_row_homogeneous(True)
        gauge_grid.set_column_homogeneous(True)
        row2.append(gauge_grid)

        gauge_grid.attach(self._make_gauge(35, "CPU"), 0, 0, 1, 1)
        gauge_grid.attach(self._make_gauge(78, "Memory"), 1, 0, 1, 1)
        gauge_grid.attach(self._make_gauge(95, "Disk"), 0, 1, 1, 1)
        gauge_grid.attach(self._make_gauge_custom(), 1, 1, 1, 1)

        # Compact line chart (red scheme, current value, no labels)
        row2.append(self._make_line_chart_compact())

        # Start all
        for g in self._graphs:
            g.start()

    # --- Line chart builders ---

    def _make_line_chart_full(self):
        """Sine wave with full labels, grid, axes, ticks."""
        provider = StaticProvider(generator="sine", num_points=60)
        renderer = LineChartRenderer()
        renderer.configure(
            title="Temperature",
            y_label="Celsius",
            x_label="Time",
            unit="\u00b0C",
            line_color=(0.208, 0.518, 0.894),
            show_fill=True,
            fill_color=(0.208, 0.518, 0.894, 0.2),
            y_min=0,
            y_max=100,
            show_grid=True,
            show_axes=True,
            show_y_ticks=True,
            show_x_ticks=True,
        )
        graph = GraphWidget(renderer, provider, refresh_interval_ms=0)
        graph.set_size_request(-1, 250)
        self._graphs.append(graph)

        frame = Gtk.Frame()
        frame.set_child(graph)
        return frame

    def _make_line_chart_minimal(self):
        """Random walk — no chrome, green line, points, current value."""
        provider = StaticProvider(generator="random", num_points=40)
        renderer = LineChartRenderer()
        renderer.configure(
            line_color=(0.204, 0.659, 0.325),
            line_width=3.0,
            show_fill=False,
            show_grid=False,
            show_axes=False,
            show_y_ticks=False,
            show_x_ticks=False,
            show_points=True,
            point_radius=4,
            show_current=True,
            current_position="top-right",
            current_format="{:.0f}",
        )
        graph = GraphWidget(renderer, provider, refresh_interval_ms=0)
        graph.set_size_request(-1, 250)
        self._graphs.append(graph)

        frame = Gtk.Frame()
        frame.set_child(graph)
        return frame

    def _make_line_chart_custom(self):
        """Linear ramp — purple/violet with custom tick formatting."""
        provider = StaticProvider(generator="linear", num_points=50)
        renderer = LineChartRenderer()
        renderer.configure(
            title="Progress",
            line_color=(0.6, 0.3, 0.8),
            show_fill=True,
            fill_color=(0.6, 0.3, 0.8, 0.3),
            show_grid=True,
            grid_lines=5,
            show_axes=True,
            show_y_ticks=True,
            show_x_ticks=False,
            y_tick_format="{:.1f}",
            tick_color=(0.9, 0.5, 0.1),
            unit="%",
            y_min=0,
            y_max=100,
        )
        graph = GraphWidget(renderer, provider, refresh_interval_ms=0)
        graph.set_size_request(-1, 250)
        self._graphs.append(graph)

        frame = Gtk.Frame()
        frame.set_child(graph)
        return frame

    def _make_line_chart_compact(self):
        """Compact red chart with current value in bottom-left."""
        provider = StaticProvider(generator="sine", num_points=30)
        renderer = LineChartRenderer()
        renderer.configure(
            line_color=(0.753, 0.110, 0.157),
            show_fill=True,
            fill_color=(0.753, 0.110, 0.157, 0.2),
            show_grid=True,
            grid_lines=3,
            show_axes=False,
            show_y_ticks=False,
            show_x_ticks=False,
            show_current=True,
            current_position="bottom-left",
            current_format="{:.1f}",
            unit="%",
        )
        graph = GraphWidget(renderer, provider, refresh_interval_ms=0)
        graph.set_hexpand(True)
        graph.set_vexpand(True)
        self._graphs.append(graph)

        frame = Gtk.Frame()
        frame.set_hexpand(True)
        frame.set_child(graph)
        return frame

    # --- Gauge builders ---

    def _make_gauge(self, value, label):
        """Standard gauge at given value with label."""
        provider = StaticProvider(data=[DataPoint(timestamp=0, value=value)])
        renderer = GaugeRenderer()
        renderer.configure(label=label)
        graph = GraphWidget(renderer, provider, refresh_interval_ms=0)
        graph.set_size_request(140, 140)
        self._graphs.append(graph)

        frame = Gtk.Frame()
        frame.set_child(graph)
        return frame

    def _make_gauge_custom(self):
        """Custom gauge — blue color, wider arc, watt unit."""
        provider = StaticProvider(data=[DataPoint(timestamp=0, value=185)])
        renderer = GaugeRenderer()
        renderer.configure(
            label="Power",
            max_value=450,
            warning_threshold=350,
            critical_threshold=420,
            normal_color=(0.208, 0.518, 0.894),
            arc_width=0.2,
            value_format="{:.0f}W",
        )
        graph = GraphWidget(renderer, provider, refresh_interval_ms=0)
        graph.set_size_request(140, 140)
        self._graphs.append(graph)

        frame = Gtk.Frame()
        frame.set_child(graph)
        return frame


class ShowcaseApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.graphlib.showcase")

    def do_activate(self):
        win = ShowcaseWindow(application=self)
        win.present()


def main():
    app = ShowcaseApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
