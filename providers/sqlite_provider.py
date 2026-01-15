"""
SQLite data provider for historical data.

Fetches data from SQLite databases using configurable queries.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Union

from .base import DataProvider, DataPoint


class SQLiteProvider(DataProvider):
    """
    Fetch historical data from a SQLite database.

    The query should return rows with at least a timestamp and value column.
    """

    def __init__(
        self,
        db_path: Union[str, Path],
        table: str,
        value_column: str,
        time_column: str = "timestamp",
        time_range_hours: int = 24,
        where_clause: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ):
        """
        Args:
            db_path: Path to SQLite database file
            table: Table name to query
            value_column: Column name for Y values (e.g., 'avg_ms')
            time_column: Column name for timestamps (default: 'timestamp')
            time_range_hours: How many hours of history to fetch
            where_clause: Additional WHERE conditions (e.g., "host = '8.8.8.8'")
            order_by: ORDER BY clause (default: time_column ASC)
            limit: Maximum number of rows to return
        """
        super().__init__()

        self.db_path = Path(db_path)
        self.table = table
        self.value_column = value_column
        self.time_column = time_column
        self.time_range_hours = time_range_hours
        self.where_clause = where_clause
        self.order_by = order_by or f"{time_column} ASC"
        self.limit = limit

    def fetch(self) -> List[DataPoint]:
        """Fetch data from the database."""
        if not self.db_path.exists():
            return []

        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Build query
            query = self._build_query()
            cursor.execute(query)

            rows = cursor.fetchall()
            conn.close()

            # Convert to DataPoints
            return self._rows_to_datapoints(rows)

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return []

    def _build_query(self) -> str:
        """Build the SQL query string."""
        # Calculate time cutoff
        cutoff = datetime.now() - timedelta(hours=self.time_range_hours)
        cutoff_str = cutoff.isoformat()

        # Build WHERE clause
        conditions = [f"{self.time_column} > '{cutoff_str}'"]
        if self.where_clause:
            conditions.append(f"({self.where_clause})")

        where = " AND ".join(conditions)

        # Build full query
        query = f"""
            SELECT {self.time_column}, {self.value_column}
            FROM {self.table}
            WHERE {where}
            ORDER BY {self.order_by}
        """

        if self.limit:
            query += f" LIMIT {self.limit}"

        return query

    def _rows_to_datapoints(self, rows: List[sqlite3.Row]) -> List[DataPoint]:
        """Convert database rows to DataPoint objects."""
        points = []

        for row in rows:
            try:
                # Parse timestamp
                ts_str = row[self.time_column]
                if isinstance(ts_str, str):
                    # Try ISO format
                    try:
                        dt = datetime.fromisoformat(ts_str)
                    except ValueError:
                        # Try common formats
                        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                            try:
                                dt = datetime.strptime(ts_str, fmt)
                                break
                            except ValueError:
                                continue
                        else:
                            continue  # Skip unparseable timestamps

                    timestamp = dt.timestamp()
                else:
                    timestamp = float(ts_str)

                # Get value
                value = row[self.value_column]
                if value is None:
                    continue

                points.append(DataPoint(
                    timestamp=timestamp,
                    value=float(value),
                ))

            except (KeyError, TypeError, ValueError) as e:
                continue  # Skip bad rows

        return points


# Convenience factory for ping-monitor
def create_ping_provider(
    db_path: Union[str, Path] = None,
    host: Optional[str] = None,
    metric: str = "avg_ms",
    hours: int = 24,
) -> SQLiteProvider:
    """
    Create a provider for ping-monitor data.

    Args:
        db_path: Path to ping-monitor database (auto-detected if None)
        host: Filter by specific host (None for all hosts)
        metric: Which metric to graph: 'avg_ms', 'min_ms', 'max_ms', 'packet_loss_percent', 'jitter_ms'
        hours: Hours of history to show

    Returns:
        Configured SQLiteProvider
    """
    if db_path is None:
        # Try standard XDG location
        db_path = Path("~/.local/share/ping-monitor/history.db").expanduser()

    where = f"host = '{host}'" if host else None

    return SQLiteProvider(
        db_path=db_path,
        table="ping_results",
        value_column=metric,
        time_column="timestamp",
        time_range_hours=hours,
        where_clause=where,
    )
