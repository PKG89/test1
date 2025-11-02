# Code Catalog and Rule Engine Documentation

## Overview

The Code Catalog and Rule Engine system provides comprehensive mapping of 60+ survey codes to canonical block names, rule metadata, layer definitions, and special behaviors. It automates the generation of DXF placement instructions for survey points with codes and comments.

## Architecture

### Components

1. **Code Catalog** (`src/catalog/code_catalog.py`)
   - Comprehensive mapping of survey codes to rules
   - 60+ codes with aliases for flexibility
   - Rule metadata including block names, layers, colors

2. **Rule Engine** (`src/services/rule_engine.py`)
   - Processes survey points with codes and comments
   - Generates placement instructions
   - Handles special cases and unknown codes

3. **Catalog Workflow Service** (`src/services/catalog_workflow.py`)
   - Integrates rule engine with processing pipeline
   - Creates DXF-ready payloads
   - File parsing with extended format support

4. **Data Models** (`src/models/rule_data.py`)
   - CodeRule, PlacementInstruction, RuleEngineResult
   - TextPlacement, BlockPlacement structures

## Rule Types

### №-rule (Number Rules)
Standard numbered survey points (1, 2, 3, etc.)
- **Label format**: N{number}
- **Fallback**: Nб/н (when number missing)
- **Block**: TOCHKA
- **Layer**: BLOCKS, TEXT

### km-rule (Kilometer Rules)
Kilometer markers and pickets
- **Codes**: km, km+
- **Label format**: км{number}, пк{number}
- **Fallback**: кмб/н, пкб/н
- **Layer**: TEXT_KM

### VK-rule (Reference Point Rules)
Reference points, elevation marks, geodetic points
- **Codes**: vk, rp, trig, poly, opn
- **Label format**: ВК{number}, Рп{number}, etc.
- **Layer**: VK (all text and blocks on VK layer)
- **Color**: 1 (red)

### Standard Rules
General survey codes with standard behavior
- Various infrastructure, terrain, and feature codes
- Customizable layers and colors
- Optional label generation

## Special Behaviors

### Shurf (three_labels)
Archaeological shurf with three identical labels
```python
code="shurf"
labels = ["Ш{number}", "Ш{number}", "Ш{number}"]
layer="BLOCKS_ARCH"
```

### eskizRAZR and skulpt (comment_in_block)
Comments placed entirely in block layer
```python
comment_handling=CommentHandling.BLOCK_LAYER
text_layer="BLOCKS_ARCH"
comment_layer="BLOCKS_ARCH"
```

### k-codes (k_code_layer)
Communication/utility codes with custom layers
```python
k-kabel -> K_KABEL, K_KABEL_TEXT
k-tep   -> K_TEPLO, K_TEPLO_TEXT
k-voda  -> K_VODA, K_VODA_TEXT
k-kanal -> K_KANAL, K_KANAL_TEXT
k-gaz   -> K_GAZ, K_GAZ_TEXT
```

### Unknown Codes
Unknown codes create AutoCAD point + red bold text on VK layer
```python
point_marker = {'layer': 'VK', 'color': 1, 'type': 'POINT'}
labels = ["КОД: {code}", "Z: {z:.3f}", "{comment}"]
bold=True, color=1
```

## Code Categories

### Infrastructure
- **Buildings**: zd, str
- **Structures**: most, tun, plosh, lest
- **Utilities**: stolb, osvesh, luk
- **Boundaries**: ogr, gr, znak

### Communications (k-codes)
- **k-kabel**: Cables
- **k-tep**: Heat lines
- **k-voda**: Water pipes
- **k-kanal**: Sewage
- **k-gaz**: Gas pipes

### Vegetation
- **der**: Trees
- **kust**: Bushes
- **les**: Forest
- **sad**: Garden

### Water Features
- **ur-vod**: Water edge
- **kolod**: Well

### Terrain
- **otkos**: Slope
- **nasip**: Embankment
- **dor**: Road
- **trop**: Path

### Archaeological
- **shurf**: Excavation pit
- **skulpt**: Sculpture
- **eskizRAZR**: Destruction sketch
- **raskop**: Excavation
- **nahodka**: Archaeological find

### Geodetic
- **vk**: Elevation mark
- **rp**: Reference point
- **trig**: Triangulation point
- **poly**: Traverse point
- **opn**: Support point

### Terrain Features
- **bpl**: Breakline
- **cpl**: Centerline
- **bord**: Border
- **terrain**: Relief point

## File Format

### Basic Format
```
X Y Z
```

### Extended Format
```
X Y Z CODE [NUMBER] [COMMENT...]
```

### Examples
```
100.0 200.0 150.5 1 First point
110.0 210.0 151.0 vk 25
120.0 220.0 152.5 km 100
130.0 230.0 153.0 shurf 3 Archaeological shurf
140.0 240.0 154.5 k-kabel 15 Cable line
150.0 250.0 155.0 unknown_code Test unknown
```

## Usage

### Basic Usage

```python
from src.services.catalog_workflow import CatalogWorkflowService

service = CatalogWorkflowService()

# Process file with codes
result = service.process_file_with_catalog('survey_data.txt')

if result['success']:
    print(f"Processed {result['points_loaded']} points")
    print(f"Known codes: {result['statistics']['known_codes']}")
    print(f"Unknown codes: {result['statistics']['unknown_codes']}")
    
    # Get DXF payload
    payload = result['placement_payload']
```

### Processing Point Cloud

```python
from src.models.point_data import PointCloud
import numpy as np

# Create point cloud with metadata
points = np.array([[100, 200, 150], [110, 210, 151]])
metadata = [
    {'code': '1', 'number': 1, 'comment': 'Point 1'},
    {'code': 'vk', 'number': 25}
]
cloud = PointCloud(points=points, point_metadata=metadata)

# Process with catalog
result = service.process_cloud_with_catalog(cloud)
```

### Working with Rule Engine Directly

```python
from src.services.rule_engine import RuleEngine
from src.models.point_data import SurveyPoint

engine = RuleEngine()

# Process single point
point = SurveyPoint(x=100, y=200, z=150)
instruction = engine.process_single_point(
    point, code='vk', comment='Reference', number=25
)

print(f"Block: {instruction.block.block_name}")
print(f"Labels: {instruction.labels}")
print(f"Layers: {[t.layer for t in instruction.texts]}")
```

### Creating DXF Payload

```python
from src.services.catalog_workflow import DXFPayloadBuilder

# Build DXF-ready payload
payload = DXFPayloadBuilder.build(result.instructions)

print(f"Entities: {len(payload['entities'])}")
print(f"Layers: {list(payload['layers'].keys())}")
```

## Layer Organization

### Standard Layers
- **BLOCKS**: Standard block insertions
- **TEXT**: Standard text annotations
- **POINTS**: Simple point markers
- **VK**: Reference points and elevation marks

### Specialized Layers
- **TEXT_KM**: Kilometer markers text
- **TEXT_VEG**: Vegetation text
- **TEXT_ARCH**: Archaeological text
- **TEXT_HYDRO**: Water features text
- **BLOCKS_ARCH**: Archaeological blocks
- **BLOCKS_VEG**: Vegetation blocks
- **BLOCKS_HYDRO**: Water features blocks

### Communication Layers
- **K_KABEL**, **K_KABEL_TEXT**: Cable
- **K_TEPLO**, **K_TEPLO_TEXT**: Heat
- **K_VODA**, **K_VODA_TEXT**: Water
- **K_KANAL**, **K_KANAL_TEXT**: Sewage
- **K_GAZ**, **K_GAZ_TEXT**: Gas

## Label Generation

### Format Patterns
- **N{number}**: Standard points (N1, N2, N3...)
- **км{number}**: Kilometers (км100, км150...)
- **пк{number}**: Pickets (пк10, пк50...)
- **ВК{number}**: Elevation marks (ВК1, ВК25...)
- **Ш{number}**: Shurf (Ш1, Ш2, Ш3...)
- **К{number}**: Cables (К15, К25...)

### Fallback Labels (Missing Data)
When number is not provided, fallback labels are used:
- **Nб/н**: Standard points
- **кмб/н**: Kilometers
- **ВКб/н**: Elevation marks
- **Шб/н**: Shurf
- **Кб/н**: Cables

"б/н" = "без номера" (without number)

## Color Coding

| Color | Usage |
|-------|-------|
| 1 (Red) | Reference points (VK), unknown codes |
| 2 (Yellow) | Kilometer markers, centerlines |
| 3 (Green) | Vegetation, terrain features |
| 4 (Cyan) | Cables, breaklines |
| 5 (Blue) | Water features, archaeological |
| 6 (Magenta) | Archaeological (shurf, raskop) |
| 7 (White) | Standard points, buildings |
| 8 (Gray) | Secondary features |

## Error Handling

### Unknown Codes
- Creates AutoCAD point on VK layer
- Red bold text with code, Z, and comment
- Statistics track unknown codes count
- Warnings generated for validation

### Missing Numbers
- Fallback labels used (Nб/н format)
- Statistics track missing data
- Processing continues without errors

### Invalid Data
- Validation warnings generated
- Graceful degradation
- Error messages in results

## Testing

Comprehensive test coverage (81 tests):
- 30 tests for code catalog
- 29 tests for rule engine
- 22 tests for catalog workflow

```bash
# Run all catalog tests
pytest tests/test_code_catalog.py -v

# Run rule engine tests
pytest tests/test_rule_engine.py -v

# Run workflow integration tests
pytest tests/test_catalog_workflow.py -v
```

## API Reference

### CatalogWorkflowService

#### process_file_with_catalog(filepath: str) -> Dict
Process survey file with code catalog.

**Returns:**
```python
{
    'success': bool,
    'points_loaded': int,
    'instructions': List[PlacementInstruction],
    'statistics': Dict[str, int],
    'warnings': List[str],
    'placement_payload': Dict
}
```

#### process_cloud_with_catalog(cloud: PointCloud) -> RuleEngineResult
Process point cloud with metadata.

#### validate_file_format(filepath: str) -> Dict
Validate file format and preview codes.

### RuleEngine

#### process_points(points: List[SurveyPoint]) -> RuleEngineResult
Process multiple survey points.

#### process_single_point(point, code, comment, number) -> PlacementInstruction
Process single point with code and comment.

#### extract_code_from_string(text: str) -> Tuple[str, Optional[int]]
Extract code and number from text string.

### CodeCatalog

#### get_rule(code: str) -> Optional[CodeRule]
Get rule for survey code (case-insensitive, supports aliases).

#### get_all_codes() -> List[str]
Get list of all primary survey codes.

#### get_codes_by_rule_type(rule_type: RuleType) -> List[str]
Get codes matching specific rule type.

#### is_known_code(code: str) -> bool
Check if code is known in catalog.

## Statistics

The rule engine tracks comprehensive statistics:

```python
{
    'total_points': 100,
    'known_codes': 95,
    'unknown_codes': 5,
    'missing_data_fallbacks': 10,
    'special_behaviors': 3
}
```

## Catalog Coverage

- **Total codes**: 60+
- **Total aliases**: 150+
- **Number rules**: 10+
- **KM rules**: 2
- **VK rules**: 5
- **Standard rules**: 40+

## Best Practices

1. **Use aliases**: Codes are case-insensitive, use what's convenient
2. **Provide numbers**: Avoid fallback labels by including point numbers
3. **Add comments**: Rich comments improve documentation
4. **Validate files**: Use `validate_file_format()` before processing
5. **Check statistics**: Monitor unknown codes and warnings
6. **Handle errors**: Check `success` flag in results

## Future Extensions

Potential areas for extension:
- Custom catalogs per project
- Dynamic rule loading from configuration
- User-defined special behaviors
- Multi-language support
- CAD-specific export optimizations
