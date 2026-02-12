"""
Generic command-based data provider.

Runs a shell command periodically and parses the output as numeric data.
Useful for any metric that can be obtained via command line.
"""

import json
import re
import shlex
import subprocess
import time
import threading
from collections import deque
from typing import Callable, List, Optional

from .base import DataProvider, DataPoint


class CommandProvider(DataProvider):
    """
    Data provider that runs a shell command and parses numeric output.

    Supports multiple parse modes:
    - 'float': Output is a single number
    - 'percent': Output is "X/Y" or "X of Y", returns percentage
    - 'json': Output is JSON, extracts value from specified key
    - 'regex': Extract number using regex pattern

    Maintains a rolling history buffer and supports real-time polling.
    """

    def __init__(
        self,
        command: str,
        parse_mode: str = "float",
        json_key: Optional[str] = None,
        regex_pattern: Optional[str] = None,
        history_seconds: int = 60,
        poll_interval_ms: int = 1000,
    ):
        """
        Args:
            command: Shell command to execute
            parse_mode: How to parse output - 'float', 'percent', 'json', 'regex'
            json_key: For json mode, the key path (e.g., "cpu.usage" for nested)
            regex_pattern: For regex mode, pattern with capture group for the number
            history_seconds: How many seconds of history to keep
            poll_interval_ms: Milliseconds between polls (for real-time mode)
        """
        super().__init__()

        self.command = command
        self.parse_mode = parse_mode
        self.json_key = json_key
        self.regex_pattern = regex_pattern
        self.history_seconds = history_seconds
        self.poll_interval_ms = poll_interval_ms

        # Rolling buffer of data points
        self._history: deque = deque(maxlen=history_seconds)

        # Real-time polling
        self._polling = False
        self._poll_thread: Optional[threading.Thread] = None

    def fetch(self) -> List[DataPoint]:
        """Fetch current value and return history."""
        value = self._run_command()
        if value is not None:
            self._history.append(DataPoint(
                timestamp=time.time(),
                value=value,
            ))
        return list(self._history)

    def start(self):
        """Start real-time polling."""
        if self._polling:
            return

        self._polling = True
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()

    def stop(self):
        """Stop real-time polling."""
        self._polling = False
        if self._poll_thread:
            self._poll_thread.join(timeout=2)
            self._poll_thread = None

    def _poll_loop(self):
        """Background polling loop."""
        interval = self.poll_interval_ms / 1000.0

        while self._polling:
            value = self._run_command()
            if value is not None:
                now = time.time()
                point = DataPoint(timestamp=now, value=value)
                self._history.append(point)
                self._notify([point])

            time.sleep(interval)

    def _run_command(self) -> Optional[float]:
        """Execute command and parse output."""
        try:
            result = subprocess.run(
                self.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return None

            output = result.stdout.strip()
            return self._parse_output(output)

        except (subprocess.TimeoutExpired, Exception):
            return None

    def _parse_output(self, output: str) -> Optional[float]:
        """Parse command output based on configured mode."""
        if not output:
            return None

        try:
            if self.parse_mode == "float":
                # Extract first number from output
                match = re.search(r'[-+]?\d*\.?\d+', output)
                if match:
                    return float(match.group())

            elif self.parse_mode == "percent":
                # Parse "X/Y" or "X of Y" format
                match = re.search(r'([\d.]+)\s*[/of]+\s*([\d.]+)', output, re.IGNORECASE)
                if match:
                    numerator = float(match.group(1))
                    denominator = float(match.group(2))
                    if denominator > 0:
                        return (numerator / denominator) * 100
                # Also try just extracting a percentage value
                match = re.search(r'([\d.]+)\s*%', output)
                if match:
                    return float(match.group(1))

            elif self.parse_mode == "json":
                data = json.loads(output)
                # Navigate to nested key if specified
                if self.json_key:
                    for key in self.json_key.split("."):
                        data = data[key]
                return float(data)

            elif self.parse_mode == "regex":
                if self.regex_pattern:
                    match = re.search(self.regex_pattern, output)
                    if match:
                        return float(match.group(1))

        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            pass

        return None

    def get_current_value(self) -> Optional[float]:
        """Get just the current value without adding to history."""
        return self._run_command()


def create_command_provider(config: dict) -> CommandProvider:
    """
    Factory function to create a CommandProvider from a config dict.

    Config keys:
        command: str - The shell command to run
        parse: str - Parse mode ('float', 'percent', 'json', 'regex')
        json_key: str - For JSON mode, the key path
        regex_pattern: str - For regex mode, the pattern
        poll_interval_ms: int - Polling interval in milliseconds
        history_seconds: int - How much history to keep

    Example configs:
        # Simple float output
        {"command": "cat /sys/class/thermal/thermal_zone0/temp", "parse": "float"}

        # Percentage from X/Y format
        {"command": "free | grep Mem", "parse": "percent"}

        # JSON output
        {"command": "curl -s http://api/stats", "parse": "json", "json_key": "cpu.usage"}

        # nvidia-smi with specific parsing
        {"command": "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits",
         "parse": "float", "poll_interval_ms": 500}
    """
    return CommandProvider(
        command=config["command"],
        parse_mode=config.get("parse", "float"),
        json_key=config.get("json_key"),
        regex_pattern=config.get("regex_pattern"),
        history_seconds=config.get("history_seconds", 60),
        poll_interval_ms=config.get("poll_interval_ms", 1000),
    )
