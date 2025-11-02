"""Scale management for DXF generation."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class DrawingScale(Enum):
    """Supported drawing scales."""
    SCALE_1_500 = "1:500"
    SCALE_1_1000 = "1:1000"
    SCALE_1_2000 = "1:2000"
    SCALE_1_5000 = "1:5000"


@dataclass
class ScaleParameters:
    """Parameters affected by scale."""
    text_height: float
    annotation_size: float
    lineweight: int
    
    @classmethod
    def from_scale(cls, scale: DrawingScale) -> 'ScaleParameters':
        """
        Create scale parameters based on drawing scale.
        
        Base: 1.8mm text height at 1:1000, scaled proportionally.
        
        Args:
            scale: Drawing scale
            
        Returns:
            ScaleParameters instance
        """
        base_text_height = 1.8
        base_annotation_size = 1.0
        base_lineweight = 25
        
        scale_factors = {
            DrawingScale.SCALE_1_500: 0.5,
            DrawingScale.SCALE_1_1000: 1.0,
            DrawingScale.SCALE_1_2000: 2.0,
            DrawingScale.SCALE_1_5000: 5.0,
        }
        
        factor = scale_factors.get(scale, 1.0)
        
        return cls(
            text_height=base_text_height * factor,
            annotation_size=base_annotation_size * factor,
            lineweight=int(base_lineweight * factor)
        )


class ScaleManager:
    """Manager for scale-dependent parameters."""
    
    def __init__(self, scale: DrawingScale = DrawingScale.SCALE_1_1000):
        """
        Initialize scale manager.
        
        Args:
            scale: Drawing scale (default: 1:1000)
        """
        self.scale = scale
        self.parameters = ScaleParameters.from_scale(scale)
    
    def get_text_height(self, custom_factor: float = 1.0) -> float:
        """
        Get text height for current scale.
        
        Args:
            custom_factor: Additional scaling factor
            
        Returns:
            Text height in drawing units
        """
        return self.parameters.text_height * custom_factor
    
    def get_annotation_size(self) -> float:
        """Get annotation size for current scale."""
        return self.parameters.annotation_size
    
    def get_lineweight(self) -> int:
        """Get lineweight for current scale."""
        return self.parameters.lineweight
    
    def scale_dimension(self, base_dimension: float) -> float:
        """
        Scale a dimension based on current scale.
        
        Args:
            base_dimension: Base dimension value
            
        Returns:
            Scaled dimension
        """
        scale_factors = {
            DrawingScale.SCALE_1_500: 0.5,
            DrawingScale.SCALE_1_1000: 1.0,
            DrawingScale.SCALE_1_2000: 2.0,
            DrawingScale.SCALE_1_5000: 5.0,
        }
        return base_dimension * scale_factors.get(self.scale, 1.0)
