"""Configuration and settings models."""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class InterpolationMethod(Enum):
    """Interpolation method for densification."""
    LINEAR = "linear"
    CUBIC = "cubic"
    NEAREST = "nearest"


class TINCodeSelection(Enum):
    """Preset code selections for TIN construction."""
    ALL = "all"
    TERRAIN_ONLY = "terrain_only"
    WITH_BREAKLINES = "with_breaklines"
    CUSTOM = "custom"


@dataclass
class DensificationSettings:
    """Settings for relief densification."""
    enabled: bool = False
    grid_spacing: float = 5.0  # Default grid spacing in meters
    interpolation_method: InterpolationMethod = InterpolationMethod.LINEAR
    show_generated_layer: bool = True
    show_triangles_layer: bool = True
    max_points: int = 10000  # Maximum number of generated points
    min_spacing_threshold: float = 10.0  # Minimum spacing to trigger densification
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'enabled': self.enabled,
            'grid_spacing': self.grid_spacing,
            'interpolation_method': self.interpolation_method.value,
            'show_generated_layer': self.show_generated_layer,
            'show_triangles_layer': self.show_triangles_layer,
            'max_points': self.max_points,
            'min_spacing_threshold': self.min_spacing_threshold
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DensificationSettings':
        """Create from dictionary."""
        return cls(
            enabled=data.get('enabled', False),
            grid_spacing=data.get('grid_spacing', 5.0),
            interpolation_method=InterpolationMethod(
                data.get('interpolation_method', 'linear')
            ),
            show_generated_layer=data.get('show_generated_layer', True),
            show_triangles_layer=data.get('show_triangles_layer', True),
            max_points=data.get('max_points', 10000),
            min_spacing_threshold=data.get('min_spacing_threshold', 10.0)
        )


@dataclass
class TINSettings:
    """Settings for TIN surface construction."""
    enabled: bool = True
    code_selection: TINCodeSelection = TINCodeSelection.ALL
    custom_codes: List[str] = field(default_factory=list)
    use_breaklines: bool = True
    breakline_codes: List[str] = field(default_factory=lambda: ['bpl', 'cpl', 'bord'])
    max_edge_length: Optional[float] = None
    output_layers: bool = True
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'enabled': self.enabled,
            'code_selection': self.code_selection.value,
            'custom_codes': self.custom_codes,
            'use_breaklines': self.use_breaklines,
            'breakline_codes': self.breakline_codes,
            'max_edge_length': self.max_edge_length,
            'output_layers': self.output_layers
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TINSettings':
        """Create from dictionary."""
        return cls(
            enabled=data.get('enabled', True),
            code_selection=TINCodeSelection(data.get('code_selection', 'all')),
            custom_codes=data.get('custom_codes', []),
            use_breaklines=data.get('use_breaklines', True),
            breakline_codes=data.get('breakline_codes', ['bpl', 'cpl', 'bord']),
            max_edge_length=data.get('max_edge_length'),
            output_layers=data.get('output_layers', True)
        )


@dataclass
class DXFGenerationSettings:
    """Settings for DXF generation."""
    enabled: bool = True
    drawing_scale: str = "1:1000"  # One of: 1:500, 1:1000, 1:2000, 1:5000
    use_template: bool = False
    show_z_labels: bool = True
    generate_3d_polylines: bool = True
    polyline_break_distance: float = 70.0
    round_coordinates: bool = True
    coordinate_precision: int = 3
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'enabled': self.enabled,
            'drawing_scale': self.drawing_scale,
            'use_template': self.use_template,
            'show_z_labels': self.show_z_labels,
            'generate_3d_polylines': self.generate_3d_polylines,
            'polyline_break_distance': self.polyline_break_distance,
            'round_coordinates': self.round_coordinates,
            'coordinate_precision': self.coordinate_precision
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DXFGenerationSettings':
        """Create from dictionary."""
        return cls(
            enabled=data.get('enabled', True),
            drawing_scale=data.get('drawing_scale', '1:1000'),
            use_template=data.get('use_template', False),
            show_z_labels=data.get('show_z_labels', True),
            generate_3d_polylines=data.get('generate_3d_polylines', True),
            polyline_break_distance=data.get('polyline_break_distance', 70.0),
            round_coordinates=data.get('round_coordinates', True),
            coordinate_precision=data.get('coordinate_precision', 3)
        )


@dataclass
class ProjectSettings:
    """Project-level settings."""
    scale: float = 1.0
    densification: DensificationSettings = field(default_factory=DensificationSettings)
    tin: TINSettings = field(default_factory=TINSettings)
    dxf_generation: DXFGenerationSettings = field(default_factory=DXFGenerationSettings)
    template_path: Optional[str] = None
    output_format: str = 'dxf'
