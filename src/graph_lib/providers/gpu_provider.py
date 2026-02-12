"""
GPU monitoring data provider using nvidia-smi.

Provides real-time GPU memory, utilization, and temperature data.
"""

import subprocess
import time
from typing import List, Optional, Dict
from collections import deque

from .base import DataProvider, DataPoint


class GPUProvider(DataProvider):
    """
    Real-time GPU statistics provider using nvidia-smi.

    Keeps a rolling window of historical data points.
    """

    def __init__(
        self,
        metric: str = "memory_used",
        history_seconds: int = 60,
        gpu_index: int = 0,
    ):
        """
        Args:
            metric: Which metric to track:
                - 'memory_used': GPU memory in MB
                - 'memory_percent': GPU memory as percentage
                - 'utilization': GPU compute utilization %
                - 'temperature': GPU temperature in Celsius
                - 'power': Power draw in Watts
            history_seconds: How many seconds of history to keep
            gpu_index: Which GPU (for multi-GPU systems)
        """
        super().__init__()

        self.metric = metric
        self.history_seconds = history_seconds
        self.gpu_index = gpu_index

        # Rolling buffer of data points
        self._history: deque = deque(maxlen=history_seconds)
        self._last_fetch = 0

    def fetch(self) -> List[DataPoint]:
        """Fetch current GPU stats and return history."""
        now = time.time()

        # Get current reading
        stats = self._query_nvidia_smi()
        if stats:
            value = self._extract_metric(stats)
            if value is not None:
                self._history.append(DataPoint(
                    timestamp=now,
                    value=value,
                ))

        return list(self._history)

    def _query_nvidia_smi(self) -> Optional[Dict]:
        """Query nvidia-smi for GPU statistics."""
        try:
            # Query specific fields for efficiency
            result = subprocess.run(
                [
                    "nvidia-smi",
                    f"--id={self.gpu_index}",
                    "--query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=2,
            )

            if result.returncode != 0:
                return None

            # Parse CSV output
            parts = result.stdout.strip().split(", ")
            if len(parts) >= 5:
                return {
                    "memory_used": float(parts[0]),
                    "memory_total": float(parts[1]),
                    "utilization": float(parts[2]),
                    "temperature": float(parts[3]),
                    "power": float(parts[4]) if parts[4] != "[N/A]" else 0,
                }

        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass

        return None

    def _extract_metric(self, stats: Dict) -> Optional[float]:
        """Extract the requested metric from stats."""
        if self.metric == "memory_used":
            return stats.get("memory_used")
        elif self.metric == "memory_percent":
            used = stats.get("memory_used", 0)
            total = stats.get("memory_total", 1)
            return (used / total) * 100
        elif self.metric == "utilization":
            return stats.get("utilization")
        elif self.metric == "temperature":
            return stats.get("temperature")
        elif self.metric == "power":
            return stats.get("power")
        return None


def get_gpu_info() -> Optional[Dict]:
    """Get static GPU information."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader",
            ],
            capture_output=True,
            text=True,
            timeout=2,
        )

        if result.returncode == 0:
            parts = result.stdout.strip().split(", ")
            if len(parts) >= 3:
                return {
                    "name": parts[0],
                    "memory_total": parts[1],
                    "driver": parts[2],
                }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return None
