#!/usr/bin/env python3
"""
Test graph-lib with real ping-monitor data.
"""

import sys

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from graph_lib.widgets.graph_widget import GraphWidget
from graph_lib.renderers.line_chart import LineChartRenderer
from graph_lib.providers.sqlite_provider import SQLiteProvider


class PingGraphWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("Ping Monitor - Latency Graph")
        self.set_default_size(900, 400)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(box)

        header = Adw.HeaderBar()
        box.append(header)

        # Graph container
        clamp = Adw.Clamp()
        clamp.set_maximum_size(1200)
        clamp.set_margin_top(24)
        clamp.set_margin_bottom(24)
        clamp.set_margin_start(24)
        clamp.set_margin_end(24)
        box.append(clamp)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        clamp.set_child(content)

        # Title
        title = Gtk.Label(label="Network Latency (Last 24 Hours)")
        title.add_css_class("title-2")
        content.append(title)

        # Create ping-monitor provider
        import os
        _systems_root = os.environ.get("SYSTEMS_ROOT", os.path.expanduser("~/Systems"))
        provider = SQLiteProvider(
            db_path=os.path.join(_systems_root, "tools", "ping-monitor", "history.db"),
            table="ping_results",
            value_column="avg_ms",
            time_column="timestamp",
            time_range_hours=24,
        )

        # Create renderer
        renderer = LineChartRenderer()
        renderer.configure(
            line_color=(0.208, 0.518, 0.894),
            show_fill=True,
            fill_color=(0.208, 0.518, 0.894, 0.15),
            y_min=0,
            show_grid=True,
        )

        # Create widget
        self.graph = GraphWidget(renderer, provider, refresh_interval_ms=60000)
        self.graph.set_size_request(-1, 250)

        # Frame around graph
        frame = Gtk.Frame()
        frame.set_child(self.graph)
        content.append(frame)

        # Status label
        data = provider.fetch()
        if data:
            latest = data[-1]
            status = Gtk.Label(label=f"Latest: {latest.value:.1f} ms  •  {len(data)} data points")
        else:
            status = Gtk.Label(label="No data available")
        status.add_css_class("dim-label")
        content.append(status)

        self.graph.start()


class TestApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.test.pinggraph")

    def do_activate(self):
        win = PingGraphWindow(application=self)
        win.present()


def main():
    app = TestApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
