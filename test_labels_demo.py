#!/usr/bin/env python3
"""
Demo of graph labels, axes, and runtime configuration.

Shows all the new meta controls and how to use them.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from widgets.graph_widget import GraphWidget
from renderers.line_chart import LineChartRenderer
from providers.gpu_provider import GPUProvider


class LabelsDemo(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("Graph Labels & Controls Demo")
        self.set_default_size(1000, 700)

        # Main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        header = Adw.HeaderBar()
        main_box.append(header)

        # Horizontal split: graph on left, controls on right
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        content.set_vexpand(True)
        main_box.append(content)

        # Left side: Graph
        graph_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        graph_box.set_hexpand(True)
        graph_box.set_margin_top(24)
        graph_box.set_margin_bottom(24)
        graph_box.set_margin_start(24)
        graph_box.set_margin_end(12)
        content.append(graph_box)

        # Create the graph with full labels
        provider = GPUProvider(metric="memory_used", history_seconds=60)
        renderer = LineChartRenderer()

        self.graph = GraphWidget(renderer, provider, refresh_interval_ms=500)
        self.graph.set_size_request(500, 400)

        # Configure with labels
        self.graph.configure(
            title="GPU Memory Usage",
            y_label="Memory",
            x_label="Time",
            unit=" MB",
            y_min=0,
            show_current=True,
            current_position="top-right",
            line_color=(0.2, 0.6, 1.0),
            fill_color=(0.2, 0.6, 1.0, 0.15),
            y_tick_format="{:.0f}",
        )

        frame = Gtk.Frame()
        frame.set_child(self.graph)
        graph_box.append(frame)

        # Right side: Controls panel
        controls_scroll = Gtk.ScrolledWindow()
        controls_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        controls_scroll.set_size_request(320, -1)
        content.append(controls_scroll)

        controls = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        controls.set_margin_top(24)
        controls.set_margin_bottom(24)
        controls.set_margin_start(12)
        controls.set_margin_end(24)
        controls_scroll.set_child(controls)

        # Labels section
        labels_group = Adw.PreferencesGroup()
        labels_group.set_title("Labels")
        controls.append(labels_group)

        # Title entry
        title_row = Adw.EntryRow()
        title_row.set_title("Title")
        title_row.set_text("GPU Memory Usage")
        title_row.connect("changed", lambda r: self.graph.set_title(r.get_text() or None))
        labels_group.add(title_row)

        # Y Label entry
        ylabel_row = Adw.EntryRow()
        ylabel_row.set_title("Y-Axis Label")
        ylabel_row.set_text("Memory")
        ylabel_row.connect("changed", lambda r: self.graph.set_y_label(r.get_text() or None))
        labels_group.add(ylabel_row)

        # Unit entry
        unit_row = Adw.EntryRow()
        unit_row.set_title("Unit")
        unit_row.set_text(" MB")
        unit_row.connect("changed", lambda r: self.graph.set_unit(r.get_text()))
        labels_group.add(unit_row)

        # Display section
        display_group = Adw.PreferencesGroup()
        display_group.set_title("Display")
        controls.append(display_group)

        # Show current value
        current_row = Adw.SwitchRow()
        current_row.set_title("Show Current Value")
        current_row.set_active(True)
        current_row.connect("notify::active", lambda r, _: self.graph.show_current_value(r.get_active()))
        display_group.add(current_row)

        # Show grid
        grid_row = Adw.SwitchRow()
        grid_row.set_title("Show Grid")
        grid_row.set_active(True)
        grid_row.connect("notify::active", lambda r, _: self.graph.set_grid(r.get_active()))
        display_group.add(grid_row)

        # Show axes
        axes_row = Adw.SwitchRow()
        axes_row.set_title("Show Axes")
        axes_row.set_active(True)
        axes_row.connect("notify::active", lambda r, _: self.graph.set_axes(r.get_active()))
        display_group.add(axes_row)

        # Show Y ticks
        yticks_row = Adw.SwitchRow()
        yticks_row.set_title("Show Y Tick Labels")
        yticks_row.set_active(True)
        yticks_row.connect("notify::active", lambda r, _: self.graph.set_ticks(y_ticks=r.get_active()))
        display_group.add(yticks_row)

        # Show X ticks
        xticks_row = Adw.SwitchRow()
        xticks_row.set_title("Show X Tick Labels")
        xticks_row.set_active(True)
        xticks_row.connect("notify::active", lambda r, _: self.graph.set_ticks(x_ticks=r.get_active()))
        display_group.add(xticks_row)

        # Show fill
        fill_row = Adw.SwitchRow()
        fill_row.set_title("Show Fill")
        fill_row.set_active(True)
        fill_row.connect("notify::active", lambda r, _: self.graph.configure(show_fill=r.get_active()))
        display_group.add(fill_row)

        # Y Range section
        range_group = Adw.PreferencesGroup()
        range_group.set_title("Y-Axis Range")
        controls.append(range_group)

        # Y Min
        ymin_adj = Gtk.Adjustment(value=0, lower=0, upper=24000, step_increment=1000)
        ymin_row = Adw.SpinRow()
        ymin_row.set_title("Y Minimum")
        ymin_row.set_adjustment(ymin_adj)
        ymin_row.connect("changed", lambda r: self._update_y_range())
        self.ymin_row = ymin_row
        range_group.add(ymin_row)

        # Y Max (0 = auto)
        ymax_adj = Gtk.Adjustment(value=0, lower=0, upper=24000, step_increment=1000)
        ymax_row = Adw.SpinRow()
        ymax_row.set_title("Y Maximum (0 = auto)")
        ymax_row.set_adjustment(ymax_adj)
        ymax_row.connect("changed", lambda r: self._update_y_range())
        self.ymax_row = ymax_row
        range_group.add(ymax_row)

        # Refresh section
        refresh_group = Adw.PreferencesGroup()
        refresh_group.set_title("Refresh")
        controls.append(refresh_group)

        # Refresh rate
        rate_adj = Gtk.Adjustment(value=500, lower=100, upper=5000, step_increment=100)
        rate_row = Adw.SpinRow()
        rate_row.set_title("Refresh Rate (ms)")
        rate_row.set_adjustment(rate_adj)
        rate_row.connect("changed", lambda r: self.graph.set_refresh_interval(int(r.get_value())))
        refresh_group.add(rate_row)

        # Color presets section
        color_group = Adw.PreferencesGroup()
        color_group.set_title("Color Presets")
        controls.append(color_group)

        colors = [
            ("Blue", (0.208, 0.518, 0.894)),
            ("Green", (0.204, 0.659, 0.325)),
            ("Orange", (0.898, 0.612, 0.0)),
            ("Red", (0.753, 0.110, 0.157)),
            ("Purple", (0.6, 0.3, 0.8)),
        ]

        for name, color in colors:
            btn_row = Adw.ActionRow()
            btn_row.set_title(name)
            btn_row.set_activatable(True)
            btn_row.connect("activated", lambda r, c=color: self.graph.set_color(c))

            # Color preview
            preview = Gtk.DrawingArea()
            preview.set_size_request(24, 24)
            preview.set_draw_func(lambda area, cr, w, h, c=color: self._draw_color_preview(cr, w, h, c))
            btn_row.add_suffix(preview)

            color_group.add(btn_row)

        # Start the graph
        self.graph.start()

    def _update_y_range(self):
        """Update Y range from spin buttons."""
        y_min = self.ymin_row.get_value()
        y_max = self.ymax_row.get_value()

        # 0 means auto
        self.graph.set_y_range(
            y_min if y_min > 0 else None,
            y_max if y_max > 0 else None,
        )

    def _draw_color_preview(self, cr, width, height, color):
        """Draw a color swatch."""
        cr.set_source_rgb(*color)
        cr.rectangle(0, 0, width, height)
        cr.fill()


class DemoApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.demo.graphlabels")

    def do_activate(self):
        win = LabelsDemo(application=self)
        win.present()


def main():
    app = DemoApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
