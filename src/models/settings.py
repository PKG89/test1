"""Configuration and settings models."""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class InterpolationMethod(Enum):
    """Interpolation method for densification."""
    LINEAR = "linear"
    CUBIC = "cubic"
    NEAREST = "nearest"


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
class ProjectSettings:
    """Project-level settings."""
    scale: float = 1.0
    densification: DensificationSettings = field(default_factory=DensificationSettings)
    template_path: Optional[str] = None
    output_format: str = 'dxf'
