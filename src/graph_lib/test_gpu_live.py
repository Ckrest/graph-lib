#!/usr/bin/env python3
"""
Live GPU monitoring test.

Shows real-time GPU memory and utilization with fast refresh.
"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from graph_lib.widgets.graph_widget import GraphWidget
from graph_lib.renderers.line_chart import LineChartRenderer
from graph_lib.renderers.gauge import GaugeRenderer
from graph_lib.providers.gpu_provider import GPUProvider, get_gpu_info
from graph_lib.providers.base import DataPoint


class GPUMonitorWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("GPU Monitor - Live")
        self.set_default_size(900, 600)

        self._graphs = []

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(box)

        # Header
        header = Adw.HeaderBar()
        box.append(header)

        # GPU info banner
        gpu_info = get_gpu_info()
        if gpu_info:
            banner = Adw.Banner()
            banner.set_title(f"{gpu_info['name']} • {gpu_info['memory_total']} • Driver {gpu_info['driver']}")
            banner.set_revealed(True)
            box.append(banner)

        # Main content
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        box.append(scrolled)

        clamp = Adw.Clamp()
        clamp.set_maximum_size(1000)
        clamp.set_margin_top(24)
        clamp.set_margin_bottom(24)
        clamp.set_margin_start(24)
        clamp.set_margin_end(24)
        scrolled.set_child(clamp)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        clamp.set_child(content)

        # Row 1: Gauges
        gauge_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        gauge_box.set_halign(Gtk.Align.CENTER)
        content.append(gauge_box)

        # Memory gauge
        mem_gauge = self._create_gauge(
            "Memory",
            GPUProvider(metric="memory_percent", history_seconds=1),
            suffix="%"
        )
        gauge_box.append(mem_gauge)

        # Utilization gauge
        util_gauge = self._create_gauge(
            "GPU Load",
            GPUProvider(metric="utilization", history_seconds=1),
            suffix="%"
        )
        gauge_box.append(util_gauge)

        # Temperature gauge
        temp_gauge = self._create_gauge(
            "Temperature",
            GPUProvider(metric="temperature", history_seconds=1),
            suffix="°C",
            max_val=100,
            warning=70,
            critical=85
        )
        gauge_box.append(temp_gauge)

        # Power gauge
        power_gauge = self._create_gauge(
            "Power",
            GPUProvider(metric="power", history_seconds=1),
            suffix="W",
            max_val=450,  # RTX 4090 TDP
            warning=350,
            critical=420
        )
        gauge_box.append(power_gauge)

        # Row 2: Memory usage line chart
        mem_group = Adw.PreferencesGroup()
        mem_group.set_title("Memory Usage (Last 60 seconds)")
        content.append(mem_group)

        mem_graph = self._create_line_chart(
            GPUProvider(metric="memory_used", history_seconds=60),
            color=(0.2, 0.6, 1.0),
            y_min=0,
            y_max=24576,  # 24GB for RTX 4090
        )
        mem_graph.set_size_request(-1, 150)
        mem_group.add(self._wrap_graph(mem_graph))

        # Row 3: GPU utilization line chart
        util_group = Adw.PreferencesGroup()
        util_group.set_title("GPU Utilization (Last 60 seconds)")
        content.append(util_group)

        util_graph = self._create_line_chart(
            GPUProvider(metric="utilization", history_seconds=60),
            color=(0.4, 0.8, 0.4),
            y_min=0,
            y_max=100,
        )
        util_graph.set_size_request(-1, 150)
        util_group.add(self._wrap_graph(util_graph))

        # Start all graphs
        for graph in self._graphs:
            graph.start()

    def _create_gauge(self, label, provider, suffix="", max_val=100, warning=70, critical=90):
        """Create a gauge widget."""
        renderer = GaugeRenderer()
        renderer.configure(
            label=label,
            max_value=max_val,
            warning_threshold=warning,
            critical_threshold=critical,
            value_format=f"{{:.0f}}{suffix}",
        )

        graph = GraphWidget(renderer, provider, refresh_interval_ms=500)
        graph.set_size_request(140, 140)
        self._graphs.append(graph)

        frame = Gtk.Frame()
        frame.set_child(graph)
        return frame

    def _create_line_chart(self, provider, color, y_min=None, y_max=None):
        """Create a line chart widget."""
        renderer = LineChartRenderer()
        renderer.configure(
            line_color=color,
            show_fill=True,
            fill_color=(*color, 0.15),
            y_min=y_min,
            y_max=y_max,
            show_grid=True,
            line_width=2,
        )

        graph = GraphWidget(renderer, provider, refresh_interval_ms=500)
        self._graphs.append(graph)
        return graph

    def _wrap_graph(self, graph):
        """Wrap graph in a box with margins."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_bottom(12)
        box.append(graph)
        return box


class GPUMonitorApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.test.gpumonitor")

    def do_activate(self):
        win = GPUMonitorWindow(application=self)
        win.present()


def main():
    app = GPUMonitorApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
