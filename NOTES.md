# Graph Library - Development Notes

## Project Status

Generic GTK4 graph visualization library with no Systems-specific dependencies. Implements clean hexagonal architecture - suitable for standalone distribution or PyPI package.

## Architecture

**Hexagonal architecture with clean separation:**
- **Domain (Core)**: Graph rendering logic in `renderers/`
- **Ports**: Abstract interfaces (`GraphRenderer`, `DataProvider`)
- **Adapters**: Concrete implementations
  - Data: `SQLiteProvider`, `RedisProvider`, `GPUProvider`, `StaticProvider`
  - UI: `GraphWidget` (GTK4)
  - Renderers: `LineChartRenderer`, `GaugeRenderer`

## Test Dependencies

**Test files use hardcoded paths:**
- `test_ping_graph.py` references local database paths

These are test-only and don't affect the library. For distribution, tests need rewriting to use fixtures.

## External Dependencies

**GTK4 stack:**
- `python3-gi`
- `gir1.2-gtk-4.0`
- Cairo for rendering

**Optional data sources:**
- SQLite (for `SQLiteProvider`)
- Redis (for `RedisProvider`)
- NVIDIA GPU libraries (for `GPUProvider`)

## Future Plans

**Optional enhancements:**
- Create fixture-based unit tests
- Consider PyPI publication
- Add more renderer types (bar chart, scatter plot)

**Potential uses:**
- System monitoring dashboards
- Real-time data visualization
- IoT sensor displays
- Performance metrics
- Any GTK4 app needing graphs

## Known Issues

None currently. Library is functional but needs more testing and documentation.
