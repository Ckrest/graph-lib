"""
Graph Library - Embeddable GTK4 graph widgets.

Usage:
    from graph_lib import GraphWidget, LineChartRenderer, SQLiteProvider

    provider = SQLiteProvider(db_path, query, value_column)
    renderer = LineChartRenderer()
    widget = GraphWidget(renderer, provider)
    widget.start()
"""

from .widgets.graph_widget import GraphWidget
from .renderers.base import GraphRenderer
from .renderers.line_chart import LineChartRenderer
from .renderers.gauge import GaugeRenderer
from .providers.base import DataProvider, DataPoint
from .providers.static_provider import StaticProvider

# Optional imports (may not be available)
try:
    from .providers.sqlite_provider import SQLiteProvider
except ImportError:
    SQLiteProvider = None

try:
    from .providers.redis_provider import RedisProvider
except ImportError:
    RedisProvider = None

__all__ = [
    "GraphWidget",
    "GraphRenderer",
    "LineChartRenderer",
    "GaugeRenderer",
    "DataProvider",
    "DataPoint",
    "StaticProvider",
    "SQLiteProvider",
    "RedisProvider",
]
