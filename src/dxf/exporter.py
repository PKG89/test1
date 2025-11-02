"""DXF export functionality."""

import ezdxf
from ezdxf.document import Drawing
import numpy as np
from typing import Optional, List

from src.models.point_data import PointCloud, TIN, PointType
from src.dxf.layer_manager import LayerManager, LayerConfig


class DXFExporter:
    """Exporter for DXF format with support for densified data."""
    
    def __init__(self, template_path: Optional[str] = None):
        """
        Initialize DXF exporter.
        
        Args:
            template_path: Path to DXF template file (optional)
        """
        if template_path:
            self.doc = ezdxf.readfile(template_path)
        else:
            self.doc = ezdxf.new('R2018')
        
        self.msp = self.doc.modelspace()
        self.layer_manager = LayerManager(self.doc)
        self._setup_text_styles()
    
    def _setup_text_styles(self):
        """Set up text styles for labels."""
        if 'COORDINATES' not in self.doc.styles:
            self.doc.styles.new('COORDINATES', dxfattribs={
                'font': 'Arial.ttf',
                'width': 0.8
            })
    
    def export_full_project(self, original_cloud: PointCloud, 
                          original_tin: TIN,
                          densified_cloud: Optional[PointCloud] = None,
                          densified_tin: Optional[TIN] = None,
                          show_original: bool = True,
                          show_densified: bool = True):
        """
        Export complete project with original and densified data.
        
        Args:
            original_cloud: Original point cloud
            original_tin: TIN from original points
            densified_cloud: Densified point cloud (optional)
            densified_tin: TIN from densified points (optional)
            show_original: Whether to include original data
            show_densified: Whether to include densified data
        """
        if show_original:
            self._export_points(
                original_cloud.points,
                LayerConfig.ORIGINAL_POINTS,
                original_cloud.point_metadata
            )
            self._export_tin_triangles(
                original_tin,
                LayerConfig.ORIGINAL_SURFACE
            )
        
        if show_densified and densified_cloud is not None:
            generated_points = densified_cloud.get_points_by_type(PointType.GENERATED)
            if len(generated_points) > 0:
                generated_metadata = [
                    meta for meta in densified_cloud.point_metadata 
                    if meta.get('type') == PointType.GENERATED.value
                ]
                self._export_generated_points(
                    generated_points,
                    LayerConfig.ADDED_POINTS,
                    generated_metadata
                )
            
            if densified_tin is not None:
                self._export_tin_triangles(
                    densified_tin,
                    LayerConfig.EDITED_SURFACE,
                    color=1
                )
    
    def _export_points(self, points: np.ndarray, layer: str, 
                      metadata: Optional[List[dict]] = None):
        """Export points as circles with elevation labels."""
        for i, point in enumerate(points):
            self.msp.add_circle(
                center=(point[0], point[1]),
                radius=0.2,
                dxfattribs={'layer': layer}
            )
            
            text = self.msp.add_text(
                f"{point[2]:.3f}",
                dxfattribs={
                    'layer': layer,
                    'style': 'COORDINATES',
                    'height': 0.3,
                    'insert': (point[0], point[1] - 0.5),
                    'halign': 1
                }
            )
    
    def _export_generated_points(self, points: np.ndarray, layer: str,
                                metadata: Optional[List[dict]] = None):
        """Export generated points with distinctive red triangle markers."""
        for i, point in enumerate(points):
            triangle_points = [
                (point[0], point[1] + 0.3),
                (point[0] - 0.26, point[1] - 0.15),
                (point[0] + 0.26, point[1] - 0.15),
                (point[0], point[1] + 0.3)
            ]
            
            self.msp.add_lwpolyline(
                triangle_points,
                close=True,
                dxfattribs={
                    'layer': layer,
                    'color': 1
                }
            )
            
            text = self.msp.add_text(
                f"{point[2]:.3f}",
                dxfattribs={
                    'layer': layer,
                    'style': 'COORDINATES',
                    'height': 0.3,
                    'color': 1,
                    'insert': (point[0], point[1] - 0.8),
                    'halign': 1
                }
            )
    
    def _export_tin_triangles(self, tin: TIN, layer: str, color: Optional[int] = None):
        """Export TIN as triangles."""
        for triangle in tin.triangles:
            pts = tin.points[triangle]
            
            triangle_points = [
                (pts[0, 0], pts[0, 1]),
                (pts[1, 0], pts[1, 1]),
                (pts[2, 0], pts[2, 1]),
                (pts[0, 0], pts[0, 1])
            ]
            
            attribs = {'layer': layer}
            if color is not None:
                attribs['color'] = color
            
            self.msp.add_lwpolyline(triangle_points, close=True, dxfattribs=attribs)
    
    def save(self, filepath: str):
        """Save DXF file."""
        self.doc.saveas(filepath)
