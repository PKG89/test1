# TIN Surface Builder Feature

## Overview

The TIN (Triangulated Irregular Network) Surface Builder is a comprehensive feature for creating high-quality triangulated surfaces from survey points with support for structural lines (breaklines) as constrained edges.

## Features

### Core Capabilities

1. **Point Code Selection**
   - Select which point codes to include in TIN construction
   - Predefined selections: All points, Terrain only, With breaklines, Custom
   - Fine-grained control over which survey points participate in triangulation

2. **Breakline Support**
   - Integrate structural polylines (bpl, cpl, bord) as constrained edges
   - Triangle rejection method to enforce breakline constraints
   - Closed and open polyline support

3. **DXF Layer Generation**
   - `1 реальная поверхность` - TIN mesh triangles
   - `1 Отметки и точки реального рельефа` - Point annotations with elevations
   - Distinctive color coding (color 3 - cyan/green)

4. **Quality Control**
   - Triangle quality metrics
   - Max edge length filtering
   - Graceful handling of insufficient points
   - User feedback on construction results

## Architecture

### Models

#### `PointCode` Enum
```python
class PointCode(Enum):
    BPL = "bpl"      # Breakline
    CPL = "cpl"      # Centerline
    BORD = "bord"    # Border
    TERRAIN = "terrain"
    OTHER = "other"
```

#### `Polyline` Dataclass
Represents structural features:
- `vertices`: np.ndarray of 3D points
- `code`: String code identifier
- `is_closed`: Boolean for closed polygons

#### `TIN` Dataclass
Enhanced to include:
- `breaklines`: List[Polyline] for constrained edges

#### `TINSettings` Dataclass
Configuration for TIN construction:
- `enabled`: Toggle TIN generation
- `code_selection`: Which codes to use
- `custom_codes`: User-defined code list
- `use_breaklines`: Enable breakline constraints
- `breakline_codes`: Codes representing breaklines
- `max_edge_length`: Optional edge length filter
- `output_layers`: Include TIN in DXF output

### Services

#### `TINService`
High-level service for TIN construction:
- Filters points by code
- Extracts breaklines from point cloud
- Builds TIN with constraints
- Returns TIN and statistics

#### `TINBuilder`
Core triangulation engine:
- Delaunay triangulation using scipy
- Breakline enforcement via triangle rejection
- Edge filtering by length
- Quality calculation

### Conversation Flow

#### `TINConversation`
User interaction prompts:
- Initial TIN configuration
- Code selection
- Custom codes input
- Breaklines configuration
- Breakline codes selection
- Output layers toggle
- Summary and confirmation

## Usage

### Basic TIN Construction

```python
from src.services.tin_service import TINService
from src.models.settings import TINSettings, TINCodeSelection
from src.models.point_data import PointCloud

# Configure TIN settings
settings = TINSettings(
    enabled=True,
    code_selection=TINCodeSelection.ALL
)

# Build TIN
service = TINService(settings)
tin, stats = service.build_tin(point_cloud)

print(f"Triangles: {stats['triangle_count']}")
print(f"Quality: {stats['quality']:.3f}")
```

### TIN with Breaklines

```python
settings = TINSettings(
    enabled=True,
    code_selection=TINCodeSelection.WITH_BREAKLINES,
    use_breaklines=True,
    breakline_codes=['bpl', 'cpl', 'bord']
)

service = TINService(settings)
tin, stats = service.build_tin(point_cloud)

print(f"Breaklines: {stats['breakline_count']}")
```

### Custom Point Codes

```python
settings = TINSettings(
    enabled=True,
    code_selection=TINCodeSelection.CUSTOM,
    custom_codes=['terrain', 'bpl', 'special_feature']
)

service = TINService(settings)
tin, stats = service.build_tin(point_cloud)
```

### Full Workflow with DXF Export

```python
from src.services.processing_service import ProcessingService
from src.models.settings import ProjectSettings, TINSettings

settings = ProjectSettings(
    tin=TINSettings(
        enabled=True,
        code_selection=TINCodeSelection.WITH_BREAKLINES,
        use_breaklines=True,
        output_layers=True
    )
)

service = ProcessingService()
results = service.process_project(
    'input_points.txt',
    'output.dxf',
    settings
)

if results['success']:
    tin_stats = results['real_tin']
    print(f"TIN created with {tin_stats['triangle_count']} triangles")
```

## Algorithm Details

### Breakline Enforcement

The breakline enforcement uses a **triangle rejection method**:

1. Perform unconstrained Delaunay triangulation
2. For each triangle, check if any edge crosses a breakline segment
3. Remove triangles that violate breakline constraints
4. Segments that share vertices with breaklines are preserved

#### Segment Intersection Test

Uses the CCW (Counter-Clockwise) test:
```python
def segments_intersect(p1, p2, p3, p4):
    # Returns True if segment p1-p2 intersects p3-p4
    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and \
           ccw(p1, p2, p3) != ccw(p1, p2, p4)
```

### Quality Metric

Triangle quality is calculated as:

```
quality = (4 * sqrt(3) * area) / (sum of squared edge lengths)
```

This metric ranges from 0 (degenerate) to 1 (equilateral triangle).

## DXF Output

### Layer Structure

| Layer Name | Color | Purpose |
|------------|-------|---------|
| `1 реальная поверхность` | 3 (cyan) | TIN triangles and breaklines |
| `1 Отметки и точки реального рельефа` | 3 (cyan) | Survey points with elevation labels |

### Entity Types

- **TIN Triangles**: LWPOLYLINE (closed, 4 vertices)
- **Breaklines**: LWPOLYLINE (color 5, lineweight 50)
- **Points**: CIRCLE (radius 0.2)
- **Labels**: TEXT (elevation values)

## Testing

### Test Coverage

The feature includes comprehensive tests:

1. **Unit Tests** (`test_tin_builder.py`):
   - Basic TIN construction (7 tests)
   - Breakline enforcement (7 tests)
   - TIN service (9 tests)
   - Statistics validation (2 tests)

2. **Integration Tests** (`test_tin_integration.py`):
   - Full workflow integration (6 tests)
   - DXF layer configuration (2 tests)
   - File output validation (3 tests)

**Total: 36 tests for TIN feature**

### Running Tests

```bash
# Run all TIN tests
pytest tests/test_tin_builder.py tests/test_tin_integration.py -v

# Run specific test class
pytest tests/test_tin_builder.py::TestTINWithBreaklines -v

# Run with coverage
pytest tests/test_tin_builder.py --cov=src.processors.tin_builder
```

## Configuration Examples

### Default Settings (All Points, No Breaklines)

```python
TINSettings(
    enabled=True,
    code_selection=TINCodeSelection.ALL,
    use_breaklines=False,
    output_layers=True
)
```

### Terrain with Structural Lines

```python
TINSettings(
    enabled=True,
    code_selection=TINCodeSelection.WITH_BREAKLINES,
    use_breaklines=True,
    breakline_codes=['bpl', 'cpl', 'bord'],
    output_layers=True
)
```

### Custom Configuration with Edge Filtering

```python
TINSettings(
    enabled=True,
    code_selection=TINCodeSelection.CUSTOM,
    custom_codes=['terrain', 'survey_point'],
    use_breaklines=True,
    breakline_codes=['boundary'],
    max_edge_length=50.0,
    output_layers=True
)
```

## Error Handling

The service handles various error conditions gracefully:

1. **Insufficient Points**: Returns empty TIN with error message
2. **No Points After Filtering**: Skips TIN generation, reports filtering stats
3. **Empty Point Cloud**: Returns empty TIN with skip flag
4. **Disabled TIN**: Returns empty TIN with skip flag

All error conditions are reported in the statistics dictionary:
```python
{
    'skipped': True,
    'error': 'Insufficient points (need at least 3)',
    'triangle_count': 0
}
```

## Performance Considerations

- **Delaunay Triangulation**: O(n log n) using scipy
- **Breakline Enforcement**: O(n * m) where n=triangles, m=breakline segments
- **Memory**: ~100 bytes per point, ~150 bytes per triangle
- **Recommended Limits**: 
  - Max points: 100,000
  - Max breakline segments: 10,000

## Future Enhancements

Potential improvements for future versions:

1. **Advanced Breakline Algorithms**:
   - Constrained Delaunay triangulation (CDT)
   - Steiner point insertion along breaklines

2. **Additional Constraints**:
   - Exclusion zones
   - Minimum angle constraints
   - Custom triangulation rules

3. **3D Features**:
   - Export 3DFACE entities for 3D visualization
   - Z-value interpolation along breaklines

4. **Performance**:
   - Spatial indexing for large datasets
   - Parallel breakline checking
   - Progressive mesh generation

## References

- Delaunay, B. (1934). "Sur la sphère vide"
- Shewchuk, J. R. (1996). "Triangle: Engineering a 2D Quality Mesh Generator"
- Lee, D. T. and Schachter, B. J. (1980). "Two algorithms for constructing a Delaunay triangulation"

## Support

For issues or questions about the TIN Surface Builder:
- Check test examples in `tests/test_tin_builder.py`
- Review conversation flow in `src/bot/conversation.py`
- See integration examples in `tests/test_tin_integration.py`
