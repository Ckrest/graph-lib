# Graph Library

> AI-assisted development with Claude

Embeddable GTK4 graph widgets for time series visualization and gauges. Features a pluggable architecture with separate providers (data sources) and renderers (visualization).

## Features

- **Line Charts** - Time series with fill, grid, axes, and labels
- **Gauges** - Circular gauge displays
- **Data Providers** - SQLite, static data, GPU metrics, Redis (extensible)
- **Runtime Configuration** - Update colors, labels, ranges without restart
- **Auto-refresh** - Configurable polling with real-time update hooks

## Installation

```bash
pip install .
```

Requires GTK4 and PyGObject. On Ubuntu/Debian:
```bash
sudo apt install libgtk-4-dev python3-gi python3-gi-cairo gir1.2-gtk-4.0
```

## Usage

```python
from graph_lib import GraphWidget, LineChartRenderer, SQLiteProvider

# Create components
provider = SQLiteProvider(
    db_path="./metrics.db",
    table="readings",
    value_column="temperature",
    time_column="timestamp",
    time_range_hours=24,
)
renderer = LineChartRenderer()

# Create widget
graph = GraphWidget(renderer, provider, refresh_interval_ms=1000)

# Configure appearance
graph.configure(
    title="Temperature",
    y_label="Celsius",
    unit="°C",
    show_current=True,
    y_min=0,
    y_max=100,
)

# Add to GTK container and start
container.append(graph)
graph.start()
```

## Architecture

```
graph_lib/
├── providers/          # Data sources
│   ├── base.py         # DataProvider, DataPoint
│   ├── sqlite_provider.py
│   ├── static_provider.py
│   └── gpu_provider.py
├── renderers/          # Visualization
│   ├── base.py         # GraphRenderer
│   ├── line_chart.py
│   └── gauge.py
├── widgets/            # GTK4 wrapper
│   └── graph_widget.py
└── theme.py            # Color definitions
```

## Creating Custom Providers

```python
from graph_lib.providers.base import DataProvider, DataPoint

class MyProvider(DataProvider):
    def fetch(self) -> list[DataPoint]:
        # Return list of DataPoint(timestamp, value)
        return [
            DataPoint(timestamp=time.time(), value=42.0),
        ]
```

## Runtime Configuration

```python
# Change colors
graph.set_color((0.2, 0.6, 0.3))  # RGB tuple

# Adjust Y range
graph.set_y_range(0, 100)  # Fixed range
graph.set_y_range(y_min=0)  # Auto max, fixed min

# Toggle features
graph.set_grid(show=True, lines=5)
graph.show_current_value(True, position="top-right")

# Swap data source
graph.set_provider(new_provider)
```

## Built With

- Python
- GTK4 / PyGObject
- Cairo (rendering)

## License

MIT License - see [LICENSE](LICENSE) for details.
