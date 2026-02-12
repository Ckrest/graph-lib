#!/usr/bin/env python3
"""
Test script for graph-lib.

Run this to see line chart and gauge in a GTK4 window.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from graph_lib.widgets.graph_widget import GraphWidget
from graph_lib.renderers.line_chart import LineChartRenderer
from graph_lib.renderers.gauge import GaugeRenderer
from graph_lib.providers.static_provider import StaticProvider


class TestWindow(Adw.ApplicationWindow):
    """Test window showing various graph types."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("Graph Library Test")
        self.set_default_size(800, 500)

        # Main layout
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(box)

        # Header
        header = Adw.HeaderBar()
        box.append(header)

        # Content with two columns
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)
        box.append(content)

        # Line chart (left side, takes more space)
        line_frame = Gtk.Frame()
        line_frame.set_hexpand(True)

        line_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        line_frame.set_child(line_box)

        line_label = Gtk.Label(label="Line Chart (Sine Wave)")
        line_label.set_margin_top(8)
        line_box.append(line_label)

        # Create line chart
        line_provider = StaticProvider(generator="sine", num_points=60)
        line_renderer = LineChartRenderer()
        line_renderer.configure(
            line_color=(0.2, 0.6, 1.0),
            show_fill=True,
            fill_color=(0.2, 0.6, 1.0, 0.15),
            y_min=0,
            y_max=100,
        )

        self.line_graph = GraphWidget(line_renderer, line_provider, refresh_interval_ms=0)
        self.line_graph.set_size_request(400, 300)
        line_box.append(self.line_graph)

        content.append(line_frame)

        # Gauges (right side)
        gauge_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.append(gauge_box)

        # Gauge 1 - Normal value
        gauge1_frame = Gtk.Frame()
        gauge1_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        gauge1_frame.set_child(gauge1_box)

        gauge1_label = Gtk.Label(label="Gauge (Normal)")
        gauge1_label.set_margin_top(8)
        gauge1_box.append(gauge1_label)

        from graph_lib.providers.base import DataPoint
        gauge1_provider = StaticProvider(data=[DataPoint(timestamp=0, value=45)])
        gauge1_renderer = GaugeRenderer()
        gauge1_renderer.configure(label="CPU")

        self.gauge1 = GraphWidget(gauge1_renderer, gauge1_provider, refresh_interval_ms=0)
        self.gauge1.set_size_request(150, 150)
        gauge1_box.append(self.gauge1)
        gauge_box.append(gauge1_frame)

        # Gauge 2 - Warning value
        gauge2_frame = Gtk.Frame()
        gauge2_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        gauge2_frame.set_child(gauge2_box)

        gauge2_label = Gtk.Label(label="Gauge (Warning)")
        gauge2_label.set_margin_top(8)
        gauge2_box.append(gauge2_label)

        gauge2_provider = StaticProvider(data=[DataPoint(timestamp=0, value=78)])
        gauge2_renderer = GaugeRenderer()
        gauge2_renderer.configure(label="Memory")

        self.gauge2 = GraphWidget(gauge2_renderer, gauge2_provider, refresh_interval_ms=0)
        self.gauge2.set_size_request(150, 150)
        gauge2_box.append(self.gauge2)
        gauge_box.append(gauge2_frame)

        # Gauge 3 - Critical value
        gauge3_frame = Gtk.Frame()
        gauge3_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        gauge3_frame.set_child(gauge3_box)

        gauge3_label = Gtk.Label(label="Gauge (Critical)")
        gauge3_label.set_margin_top(8)
        gauge3_box.append(gauge3_label)

        gauge3_provider = StaticProvider(data=[DataPoint(timestamp=0, value=95)])
        gauge3_renderer = GaugeRenderer()
        gauge3_renderer.configure(label="Disk")

        self.gauge3 = GraphWidget(gauge3_renderer, gauge3_provider, refresh_interval_ms=0)
        self.gauge3.set_size_request(150, 150)
        gauge3_box.append(self.gauge3)
        gauge_box.append(gauge3_frame)

        # Start all graphs
        self.line_graph.start()
        self.gauge1.start()
        self.gauge2.start()
        self.gauge3.start()


class TestApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.test.graphlib")

    def do_activate(self):
        win = TestWindow(application=self)
        win.present()


def main():
    app = TestApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
