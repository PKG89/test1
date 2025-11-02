"""DXF layer management."""

import ezdxf
from ezdxf.document import Drawing
from typing import Dict, Optional


class LayerConfig:
    """Configuration for specific DXF layers."""
    
    EDITED_SURFACE = "2 отредактированная поверхность"
    ADDED_POINTS = "2 пикеты добавленные"
    ORIGINAL_SURFACE = "1 исходная поверхность"
    ORIGINAL_POINTS = "1 пикеты исходные"
    
    LAYER_CONFIGS = {
        EDITED_SURFACE: {
            'color': 1,
            'linetype': 'CONTINUOUS',
            'lineweight': 25
        },
        ADDED_POINTS: {
            'color': 1,
            'linetype': 'CONTINUOUS',
            'lineweight': 35
        },
        ORIGINAL_SURFACE: {
            'color': 7,
            'linetype': 'CONTINUOUS',
            'lineweight': 25
        },
        ORIGINAL_POINTS: {
            'color': 7,
            'linetype': 'CONTINUOUS',
            'lineweight': 35
        }
    }


class LayerManager:
    """Manager for DXF layers."""
    
    def __init__(self, doc: Drawing):
        """
        Initialize layer manager.
        
        Args:
            doc: ezdxf Drawing document
        """
        self.doc = doc
        self._setup_layers()
    
    def _setup_layers(self):
        """Set up required layers with proper styling."""
        for layer_name, config in LayerConfig.LAYER_CONFIGS.items():
            if layer_name not in self.doc.layers:
                layer = self.doc.layers.new(name=layer_name)
                layer.color = config['color']
                layer.linetype = config['linetype']
                if 'lineweight' in config:
                    layer.dxf.lineweight = config['lineweight']
    
    def ensure_layer_exists(self, layer_name: str, color: int = 7):
        """Ensure a layer exists, create if not."""
        if layer_name not in self.doc.layers:
            layer = self.doc.layers.new(name=layer_name)
            layer.color = color
    
    def get_layer_for_point_type(self, point_type: str) -> str:
        """Get appropriate layer name for point type."""
        if point_type == 'generated':
            return LayerConfig.ADDED_POINTS
        else:
            return LayerConfig.ORIGINAL_POINTS
    
    def get_layer_for_triangle_type(self, is_densified: bool) -> str:
        """Get appropriate layer name for triangle type."""
        if is_densified:
            return LayerConfig.EDITED_SURFACE
        else:
            return LayerConfig.ORIGINAL_SURFACE
