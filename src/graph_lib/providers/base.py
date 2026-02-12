"""
Base classes for data providers.

Providers fetch data and optionally stream real-time updates.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Optional


@dataclass
class DataPoint:
    """Single data point with timestamp and value."""

    timestamp: float  # Unix timestamp
    value: float
    label: Optional[str] = None


class DataProvider(ABC):
    """Base class for data providers."""

    def __init__(self):
        self._callback: Optional[Callable[[List[DataPoint]], None]] = None

    @abstractmethod
    def fetch(self) -> List[DataPoint]:
        """Fetch current/historical data (one-shot)."""
        pass

    def subscribe(self, callback: Callable[[List[DataPoint]], None]):
        """Subscribe to real-time updates."""
        self._callback = callback

    def unsubscribe(self):
        """Stop receiving updates."""
        self._callback = None

    def start(self):
        """Start real-time updates (for streaming providers)."""
        pass

    def stop(self):
        """Stop real-time updates."""
        pass

    def _notify(self, data: List[DataPoint]):
        """Notify subscriber of new data."""
        if self._callback:
            self._callback(data)
