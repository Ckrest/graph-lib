"""
Static data provider for testing and demos.
"""

import time
import math
from typing import List, Callable, Optional

from .base import DataProvider, DataPoint


class StaticProvider(DataProvider):
    """
    Provider that returns static or generated test data.

    Can generate various patterns for testing renderers.
    """

    def __init__(
        self,
        data: Optional[List[DataPoint]] = None,
        generator: Optional[str] = None,
        num_points: int = 50,
    ):
        """
        Args:
            data: Static list of DataPoints to return
            generator: Name of built-in generator: 'sine', 'random', 'linear'
            num_points: Number of points for generators
        """
        super().__init__()
        self._static_data = data
        self._generator = generator
        self._num_points = num_points

    def fetch(self) -> List[DataPoint]:
        """Return static data or generate test data."""
        if self._static_data is not None:
            return self._static_data

        if self._generator == "sine":
            return self._generate_sine()
        elif self._generator == "random":
            return self._generate_random()
        elif self._generator == "linear":
            return self._generate_linear()
        else:
            return self._generate_sine()  # Default

    def _generate_sine(self) -> List[DataPoint]:
        """Generate a sine wave."""
        now = time.time()
        points = []

        for i in range(self._num_points):
            t = now - (self._num_points - i) * 60  # One point per minute
            value = 50 + 40 * math.sin(i * 0.2)  # 10-90 range
            points.append(DataPoint(timestamp=t, value=value))

        return points

    def _generate_random(self) -> List[DataPoint]:
        """Generate random data with some smoothing."""
        import random

        now = time.time()
        points = []
        value = 50

        for i in range(self._num_points):
            t = now - (self._num_points - i) * 60
            value += random.uniform(-10, 10)
            value = max(0, min(100, value))  # Clamp 0-100
            points.append(DataPoint(timestamp=t, value=value))

        return points

    def _generate_linear(self) -> List[DataPoint]:
        """Generate linear ramp data."""
        now = time.time()
        points = []

        for i in range(self._num_points):
            t = now - (self._num_points - i) * 60
            value = (i / self._num_points) * 100
            points.append(DataPoint(timestamp=t, value=value))

        return points
