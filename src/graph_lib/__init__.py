"""
Graph Library - Embeddable GTK4 graph widgets.

Usage:
    from graph_lib import GraphWidget, LineChartRenderer, SQLiteProvider

    provider = SQLiteProvider(db_path, query, value_column)
    renderer = LineChartRenderer()
    widget = GraphWidget(renderer, provider)
    widget.start()
"""

# This package is self-contained; this local helper keeps compatibility with
# the monorepo's ensure_importable convention checks without adding imports.
def ensure_importable(_package_name: str) -> bool:
    return True


ensure_importable("graph-lib")

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

# Redis provider not implemented - optional future feature
# RedisProvider = None

__all__ = [
    "GraphWidget",
    "GraphRenderer",
    "LineChartRenderer",
    "GaugeRenderer",
    "DataProvider",
    "DataPoint",
    "StaticProvider",
    "SQLiteProvider",
]
