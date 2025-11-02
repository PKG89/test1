"""Geometry helper utilities for DXF generation."""

import numpy as np
from typing import Dict, Optional, Tuple
from ezdxf.document import Drawing


class GeometryHelpers:
    """Helper utilities for placing geometry in DXF."""
    
    def __init__(self, doc: Drawing):
        """
        Initialize geometry helpers.
        
        Args:
            doc: ezdxf Drawing document
        """
        self.doc = doc
        self.msp = doc.modelspace()
    
    def round_position(self, x: float, y: float, z: float, 
                       precision: int = 3) -> Tuple[float, float, float]:
        """
        Round position coordinates to specified precision.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
            precision: Number of decimal places
            
        Returns:
            Tuple of rounded coordinates
        """
        return (
            round(x, precision),
            round(y, precision),
            round(z, precision)
        )
    
    def place_point(self, x: float, y: float, z: float, 
                   layer: str, color: Optional[int] = None,
                   marker_size: float = 0.5) -> None:
        """
        Place a point marker at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
            layer: Layer name
            color: Optional color index
            marker_size: Size of the marker
        """
        attribs = {'layer': layer}
        if color is not None:
            attribs['color'] = color
        
        self.msp.add_circle(
            center=(x, y),
            radius=marker_size,
            dxfattribs=attribs
        )
    
    def add_block_reference(self, block_name: str, 
                           insert_point: Tuple[float, float, float],
                           attributes: Optional[Dict[str, str]] = None,
                           layer: str = '0',
                           rotation: float = 0.0,
                           scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)) -> None:
        """
        Add a block reference with attributes.
        
        Args:
            block_name: Name of the block to insert
            insert_point: Insertion point (x, y, z)
            attributes: Dictionary of attribute tags and values
            layer: Layer name
            rotation: Rotation angle in degrees
            scale: Scale factors (x, y, z)
        """
        if block_name not in self.doc.blocks:
            return
        
        block_ref = self.msp.add_blockref(
            block_name,
            insert_point,
            dxfattribs={
                'layer': layer,
                'rotation': rotation,
                'xscale': scale[0],
                'yscale': scale[1],
                'zscale': scale[2]
            }
        )
        
        if attributes and block_ref.has_attrib:
            for tag, value in attributes.items():
                if block_ref.has_attdef(tag):
                    block_ref.set_attrib(tag, value)
    
    def add_text_entity(self, text: str, 
                       insert_point: Tuple[float, float],
                       layer: str,
                       height: float = 1.8,
                       color: Optional[int] = None,
                       rotation: float = 0.0,
                       halign: int = 0,
                       valign: int = 0,
                       style: str = 'STANDARD') -> None:
        """
        Add a text entity with specified properties.
        
        Args:
            text: Text content
            insert_point: Insertion point (x, y)
            layer: Layer name
            height: Text height
            color: Optional color index (None for layer color, 0 for black)
            rotation: Rotation angle in degrees
            halign: Horizontal alignment (0=left, 1=center, 2=right)
            valign: Vertical alignment (0=baseline, 1=bottom, 2=middle, 3=top)
            style: Text style name
        """
        attribs = {
            'layer': layer,
            'height': height,
            'rotation': rotation,
            'style': style,
            'insert': insert_point,
            'halign': halign,
            'valign': valign
        }
        
        if color is not None:
            attribs['color'] = color
        
        self.msp.add_text(text, dxfattribs=attribs)
    
    def _get_alignment_string(self, halign: int, valign: int) -> str:
        """Convert alignment integers to ezdxf alignment string."""
        h_map = {0: 'LEFT', 1: 'CENTER', 2: 'RIGHT'}
        v_map = {0: 'BASELINE', 1: 'BOTTOM', 2: 'MIDDLE', 3: 'TOP'}
        
        h_str = h_map.get(halign, 'LEFT')
        v_str = v_map.get(valign, 'BASELINE')
        
        if h_str == 'LEFT' and v_str == 'BASELINE':
            return 'LEFT'
        elif v_str == 'BASELINE':
            return h_str
        else:
            return f"{v_str}_{h_str}"
    
    def add_z_label(self, x: float, y: float, z: float,
                   layer: str, height: float = 1.8,
                   offset_x: float = 0.0, offset_y: float = -1.0,
                   color: Optional[int] = None,
                   precision: int = 3) -> None:
        """
        Add elevation (Z) label at specified location.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            z: Z elevation value to display
            layer: Layer name
            height: Text height
            offset_x: X offset from point
            offset_y: Y offset from point
            color: Optional color index
            precision: Number of decimal places for Z value
        """
        label = f"{z:.{precision}f}"
        self.add_text_entity(
            text=label,
            insert_point=(x + offset_x, y + offset_y),
            layer=layer,
            height=height,
            color=color,
            halign=1  # Center
        )
    
    def create_3d_point(self, x: float, y: float, z: float,
                       layer: str, color: Optional[int] = None) -> None:
        """
        Create a 3D point entity.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
            layer: Layer name
            color: Optional color index
        """
        attribs = {'layer': layer}
        if color is not None:
            attribs['color'] = color
        
        self.msp.add_point((x, y, z), dxfattribs=attribs)
