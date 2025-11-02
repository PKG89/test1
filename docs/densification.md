# Relief Densification Feature

## Overview

Relief densification is an advanced feature that automatically generates synthetic survey points in sparse regions of your dataset. This improves surface detail and creates more accurate terrain models.

## How It Works

### 1. Sparse Region Identification

The system identifies sparse regions using:
- **Convex Hull Analysis**: Determines the boundary of the survey area
- **Spacing Threshold**: Identifies triangles with edges longer than the configured threshold
- **TIN Analysis**: Uses the Triangulated Irregular Network to find areas needing densification

### 2. Point Generation

Synthetic points are generated using:
- **Grid-Based Generation**: Places points on a regular grid with configurable spacing
- **Triangle Constraints**: Only generates points within valid triangles
- **Boundary Constraints**: Ensures points stay within the convex hull of original data

### 3. Height Interpolation

Heights for generated points are computed using one of three methods:
- **Linear**: Fast, linear interpolation within triangles (default)
- **Cubic**: Smooth, higher-order interpolation using Clough-Tocher algorithm
- **Nearest**: Uses the height of the nearest original point

## Configuration Parameters

### Grid Spacing
- **Default**: 5.0 meters
- **Range**: 1.0 to 100.0 meters
- **Effect**: Smaller values create more points but increase processing time

**Recommendations**:
- High detail: 3 m
- Medium detail: 5 m (default)
- Low detail: 10 m

### Interpolation Method
- **Default**: Linear
- **Options**: Linear, Cubic, Nearest

**When to use**:
- **Linear**: General purpose, fast, good for most terrain
- **Cubic**: Smooth surfaces, gentle slopes
- **Nearest**: Preserving exact elevations, step-like terrain

### Min Spacing Threshold
- **Default**: 10.0 meters
- **Purpose**: Only densify areas where points are farther apart than this threshold
- **Effect**: Higher values = more selective densification

### Max Points
- **Default**: 10,000 points
- **Purpose**: Prevents excessive point generation
- **Effect**: Limits total number of generated points

### Layer Visibility

Control which layers appear in the output DXF:

#### Generated Points Layer
- **Name**: "2 пикеты добавленные"
- **Styling**: Red triangles with elevation annotations
- **Default**: Visible

#### Triangles Layer
- **Name**: "2 отредактированная поверхность"
- **Styling**: Red polylines forming TIN
- **Default**: Visible

## Layer Structure

### Output DXF Contains Four Layers:

1. **"1 исходная поверхность"** (Original Surface)
   - Original TIN triangles
   - Color: 7 (white/black)
   - Always included

2. **"1 пикеты исходные"** (Original Points)
   - Original survey points
   - Color: 7 (white/black)
   - Markers: Circles with elevation text
   - Always included

3. **"2 отредактированная поверхность"** (Edited Surface)
   - TIN with densified points
   - Color: 1 (red)
   - Optional (controlled by show_triangles_layer)

4. **"2 пикеты добавленные"** (Added Points)
   - Generated synthetic points
   - Color: 1 (red)
   - Markers: Triangles with elevation text
   - Optional (controlled by show_generated_layer)

## Usage Examples

### Command Line Interface

```bash
# Basic densification
python cli.py input.txt output.dxf --densify

# Custom grid spacing
python cli.py input.txt output.dxf --densify --grid-spacing 3.0

# Cubic interpolation with high detail
python cli.py input.txt output.dxf --densify --grid-spacing 3.0 --interpolation cubic

# Limit maximum points
python cli.py input.txt output.dxf --densify --max-points 5000

# Show statistics only
python cli.py input.txt output.dxf --stats
```

### Python API

```python
from src.services.processing_service import ProcessingService
from src.models.settings import ProjectSettings, DensificationSettings, InterpolationMethod

# Configure densification
densification = DensificationSettings(
    enabled=True,
    grid_spacing=5.0,
    interpolation_method=InterpolationMethod.LINEAR,
    show_generated_layer=True,
    show_triangles_layer=True,
    max_points=10000,
    min_spacing_threshold=10.0
)

settings = ProjectSettings(
    scale=1.0,
    densification=densification
)

# Process
service = ProcessingService()
results = service.process_project('input.txt', 'output.dxf', settings)

if results['success']:
    print(f"Generated {results['densification']['generated_points']} new points")
```

### Bot Conversation Flow

1. **Enable Densification**
   ```
   User: Yes, enable densification
   Bot: Shows grid spacing options
   ```

2. **Configure Grid Spacing**
   ```
   User: 5
   Bot: Shows interpolation method options
   ```

3. **Select Interpolation Method**
   ```
   User: Linear
   Bot: Shows layer visibility options
   ```

4. **Configure Layer Visibility**
   ```
   User: Both layers
   Bot: Shows summary and confirmation
   ```

5. **Process and Results**
   ```
   Bot: ✅ Densification completed
        📊 Original points: 25
        ➕ Generated points: 45
        🔍 Sparse regions found: 12
        📈 Density increase: +180%
   ```

## Safeguards

### Over-Generation Prevention

1. **Max Points Limit**: Hard cap on generated points (default: 10,000)
2. **Convex Hull Constraint**: Points only generated within survey boundary
3. **Triangle Constraint**: Points only in valid TIN triangles
4. **Spacing Threshold**: Only densify areas that need it

### Quality Checks

1. **NaN Filtering**: Invalid interpolated values are removed
2. **Bounds Checking**: Generated points stay within reasonable bounds
3. **Metadata Tagging**: All generated points tagged for traceability

## Performance Considerations

### Processing Time

- **Small datasets** (<100 points): < 1 second
- **Medium datasets** (100-1000 points): 1-5 seconds
- **Large datasets** (>1000 points): 5-30 seconds

### Memory Usage

- Scales with number of generated points
- Use max_points to limit memory consumption
- Typical usage: < 100 MB for most datasets

## Troubleshooting

### No Points Generated

**Possible causes**:
1. All areas already dense enough (below min_spacing_threshold)
2. Input has too few points (need at least 3)
3. Max points set too low

**Solutions**:
- Lower min_spacing_threshold
- Increase max_points
- Check input data quality

### Too Many Points Generated

**Solutions**:
- Increase grid_spacing
- Increase min_spacing_threshold  
- Lower max_points
- Use more selective densification

### Interpolation Errors

**Symptoms**: Missing or NaN values

**Solutions**:
- Use 'nearest' interpolation method
- Check for outliers in input data
- Ensure input points form valid triangles

## Testing

Run unit tests:
```bash
pytest tests/test_densification.py -v
pytest tests/test_layer_assignment.py -v
pytest tests/test_integration.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## API Reference

See inline documentation in:
- `src/services/densification_service.py` - Core densification logic
- `src/models/settings.py` - Configuration models
- `src/dxf/exporter.py` - DXF export with layers
- `src/bot/conversation.py` - User interaction flow
