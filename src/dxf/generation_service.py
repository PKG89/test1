"""DXF generation service leveraging ezdxf with template support."""

import ezdxf
from ezdxf.document import Drawing
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import numpy as np

from src.dxf.scale_settings import ScaleManager, DrawingScale
from src.dxf.geometry_helpers import GeometryHelpers
from src.dxf.polyline_builder import Polyline3DBuilder, PointWithMetadata
from src.dxf.layer_manager import LayerManager


class DXFGenerationService:
    """Service for generating DXF drawings with template support."""
    
    STRUCTURAL_LAYERS = {
        'bord': {'color': 0, 'text_color': 0},  # Black
        'rels': {'color': 0, 'text_color': 0},  # Black
        'bpl': {'color': 7, 'text_color': 7},
        'cpl': {'color': 3, 'text_color': 3},
    }
    
    SPECIAL_CODE_RULES = {
        'Fonar': {'color': 6, 'marker': 'CIRCLE'},
        'Machta': {'color': 5, 'marker': 'SQUARE'},
    }
    
    def __init__(self, 
                 template_path: Optional[str] = None,
                 scale: DrawingScale = DrawingScale.SCALE_1_1000):
        """
        Initialize DXF generation service.
        
        Args:
            template_path: Path to template DXF file (optional)
            scale: Drawing scale for annotations and text
        """
        self.template_path = template_path
        self.scale_manager = ScaleManager(scale)
        self.doc = self._load_or_create_document()
        self.layer_manager = LayerManager(self.doc)
        self.geometry_helpers = GeometryHelpers(self.doc)
        self.polyline_builder = Polyline3DBuilder()
        self._setup_text_styles()
    
    def _load_or_create_document(self) -> Drawing:
        """Load template or create new document."""
        if self.template_path and Path(self.template_path).exists():
            try:
                return ezdxf.readfile(self.template_path)
            except Exception as e:
                print(f"Warning: Could not load template {self.template_path}: {e}")
                return ezdxf.new('R2018')
        else:
            return ezdxf.new('R2018')
    
    def _setup_text_styles(self):
        """Set up text styles for the document."""
        if 'STANDARD' not in self.doc.styles:
            self.doc.styles.new('STANDARD', dxfattribs={
                'font': 'Arial.ttf',
                'width': 1.0
            })
        
        if 'COORDINATES' not in self.doc.styles:
            self.doc.styles.new('COORDINATES', dxfattribs={
                'font': 'Arial.ttf',
                'width': 0.8
            })
    
    def ensure_layer_exists(self, layer_name: str, color: int = 7, 
                           lineweight: Optional[int] = None) -> None:
        """
        Ensure a layer exists in the document.
        
        Args:
            layer_name: Name of the layer
            color: Layer color (default: 7 - white/black)
            lineweight: Optional lineweight override
        """
        if layer_name not in self.doc.layers:
            layer = self.doc.layers.new(name=layer_name)
            layer.color = color
            layer.linetype = 'CONTINUOUS'
            
            if lineweight is None:
                lineweight = self.scale_manager.get_lineweight()
            
            layer.dxf.lineweight = lineweight
    
    def ensure_block_exists(self, block_name: str) -> bool:
        """
        Check if a block exists in the document.
        
        Args:
            block_name: Name of the block
            
        Returns:
            True if block exists, False otherwise
        """
        return block_name in self.doc.blocks
    
    def insert_point_with_block(self, x: float, y: float, z: float,
                                block_name: str, layer: str,
                                attributes: Optional[Dict[str, str]] = None) -> None:
        """
        Insert a point using a block reference.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
            block_name: Name of block to insert
            layer: Layer name
            attributes: Optional attribute values
        """
        if not self.ensure_block_exists(block_name):
            self.geometry_helpers.place_point(x, y, z, layer)
            return
        
        self.geometry_helpers.add_block_reference(
            block_name=block_name,
            insert_point=(x, y, z),
            attributes=attributes,
            layer=layer
        )
    
    def add_point_with_label(self, x: float, y: float, z: float,
                            code: str, layer: str,
                            show_z_label: bool = True) -> None:
        """
        Add a point with optional Z elevation label.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
            code: Point code for styling
            layer: Layer name
            show_z_label: Whether to show Z elevation label
        """
        layer_config = self.STRUCTURAL_LAYERS.get(code.lower(), {'color': 7, 'text_color': 7})
        color = layer_config.get('color', 7)
        text_color = layer_config.get('text_color', 7)
        
        self.ensure_layer_exists(layer, color=color)
        
        self.geometry_helpers.place_point(
            x, y, z,
            layer=layer,
            color=color,
            marker_size=self.scale_manager.get_annotation_size() * 0.5
        )
        
        if show_z_label:
            text_height = self.scale_manager.get_text_height()
            self.geometry_helpers.add_z_label(
                x, y, z,
                layer=layer,
                height=text_height,
                color=text_color if text_color == 0 else None  # Use explicit black or layer color
            )
    
    def add_text_annotation(self, text: str, x: float, y: float,
                           layer: str, color: Optional[int] = None) -> None:
        """
        Add a text annotation at specified location.
        
        Args:
            text: Text content
            x: X coordinate
            y: Y coordinate
            layer: Layer name
            color: Optional color override
        """
        self.ensure_layer_exists(layer)
        text_height = self.scale_manager.get_text_height()
        
        self.geometry_helpers.add_text_entity(
            text=text,
            insert_point=(x, y),
            layer=layer,
            height=text_height,
            color=color
        )
    
    def build_3d_polylines(self, points_data: List[Dict],
                          default_layer: str = '0') -> List:
        """
        Build 3D polylines from point data.
        
        Points are grouped by (code, first digit of comment) with
        break distance >70m and special k-code logic.
        
        Args:
            points_data: List of dicts with keys: x, y, z, code, comment
            default_layer: Default layer for polylines
            
        Returns:
            List of created polyline entities
        """
        points = []
        for data in points_data:
            point = PointWithMetadata(
                x=data['x'],
                y=data['y'],
                z=data['z'],
                code=data.get('code', 'default'),
                comment=data.get('comment')
            )
            points.append(point)
        
        code_layers = {}
        for code in self.STRUCTURAL_LAYERS.keys():
            layer_name = f"{default_layer}_{code}" if default_layer != '0' else code
            code_layers[code] = layer_name
            self.ensure_layer_exists(
                layer_name,
                color=self.STRUCTURAL_LAYERS[code]['color']
            )
        
        all_polylines = []
        
        code_groups = {}
        for point in points:
            code_key = point.code.lower()
            if code_key not in code_groups:
                code_groups[code_key] = []
            code_groups[code_key].append(point)
        
        for code, group_points in code_groups.items():
            layer = code_layers.get(code, default_layer)
            
            polylines = self.polyline_builder.build_polylines_for_points(
                group_points,
                layer,
                self.doc
            )
            all_polylines.extend(polylines)
        
        return all_polylines
    
    def apply_special_code_rules(self, points_data: List[Dict],
                                 layer: str = '0') -> None:
        """
        Apply special visual rules for specific codes (e.g., Fonar, Machta).
        
        Args:
            points_data: List of point data dictionaries
            layer: Layer name
        """
        for data in points_data:
            code = data.get('code', '')
            if code in self.SPECIAL_CODE_RULES:
                rule = self.SPECIAL_CODE_RULES[code]
                
                self.ensure_layer_exists(layer, color=rule['color'])
                
                x, y, z = data['x'], data['y'], data['z']
                
                if rule['marker'] == 'CIRCLE':
                    self.geometry_helpers.place_point(
                        x, y, z,
                        layer=layer,
                        color=rule['color'],
                        marker_size=self.scale_manager.get_annotation_size()
                    )
                elif rule['marker'] == 'SQUARE':
                    size = self.scale_manager.get_annotation_size()
                    msp = self.doc.modelspace()
                    square_points = [
                        (x - size, y - size),
                        (x + size, y - size),
                        (x + size, y + size),
                        (x - size, y + size),
                        (x - size, y - size)
                    ]
                    msp.add_lwpolyline(
                        square_points,
                        close=True,
                        dxfattribs={'layer': layer, 'color': rule['color']}
                    )
    
    def get_available_blocks(self) -> List[str]:
        """
        Get list of available block names from template.
        
        Returns:
            List of block names
        """
        return [block.name for block in self.doc.blocks if not block.name.startswith('*')]
    
    def save(self, filepath: str) -> None:
        """
        Save the DXF document.
        
        Args:
            filepath: Path to save the DXF file
        """
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.saveas(str(output_path))
