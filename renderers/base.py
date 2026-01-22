"""
Base classes for graph renderers.

Renderers handle drawing graphs to a Cairo context.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..providers.base import DataPoint


class GraphRenderer(ABC):
    """Base class for all graph renderers."""

    def __init__(self):
        self.data: List[DataPoint] = []
        self.config: Dict[str, Any] = {}

    @abstractmethod
    def render(self, cr, width: int, height: int):
        """
        Render the graph to a Cairo context.

        Args:
            cr: Cairo context
            width: Available width in pixels
            height: Available height in pixels
        """
        pass

    def set_data(self, data: List[DataPoint]):
        """Update the data to render."""
        self.data = data

    def configure(self, **kwargs):
        """Update rendering configuration."""
        self.config.update(kwargs)
