"""TIN (Triangulated Irregular Network) builder."""

import numpy as np
from scipy.spatial import Delaunay
from typing import Optional

from src.models.point_data import TIN


class TINBuilder:
    """Builder for Triangulated Irregular Network."""
    
    def __init__(self, max_edge_length: Optional[float] = None):
        """
        Initialize TIN builder.
        
        Args:
            max_edge_length: Maximum allowed edge length. Triangles with edges
                           longer than this will be filtered out.
        """
        self.max_edge_length = max_edge_length
    
    def build(self, points: np.ndarray) -> TIN:
        """
        Build TIN using Delaunay triangulation.
        
        Args:
            points: Nx3 array of points (X, Y, Z)
            
        Returns:
            TIN object with triangulated network
        """
        if len(points) < 3:
            return TIN(points=points, triangles=np.array([]), quality=0.0)
        
        tri = Delaunay(points[:, :2])
        
        triangles = self._filter_long_edges(points, tri.simplices)
        
        quality = self._calculate_quality(points, triangles)
        
        return TIN(points=points, triangles=triangles, quality=quality)
    
    def _filter_long_edges(self, points: np.ndarray, triangles: np.ndarray) -> np.ndarray:
        """Filter triangles with edges longer than max_edge_length."""
        if self.max_edge_length is None or len(triangles) == 0:
            return triangles
        
        valid_triangles = []
        for triangle in triangles:
            pts = points[triangle]
            edge_lengths = [
                np.linalg.norm(pts[1, :2] - pts[0, :2]),
                np.linalg.norm(pts[2, :2] - pts[1, :2]),
                np.linalg.norm(pts[0, :2] - pts[2, :2])
            ]
            
            if max(edge_lengths) <= self.max_edge_length:
                valid_triangles.append(triangle)
        
        return np.array(valid_triangles) if valid_triangles else np.array([])
    
    def _calculate_quality(self, points: np.ndarray, triangles: np.ndarray) -> float:
        """Calculate average triangle quality coefficient."""
        if len(triangles) == 0:
            return 0.0
        
        qualities = []
        
        for triangle in triangles:
            pts = points[triangle, :2]
            
            area = 0.5 * abs(
                pts[0, 0] * (pts[1, 1] - pts[2, 1]) +
                pts[1, 0] * (pts[2, 1] - pts[0, 1]) +
                pts[2, 0] * (pts[0, 1] - pts[1, 1])
            )
            
            edges = [
                np.linalg.norm(pts[1] - pts[0]),
                np.linalg.norm(pts[2] - pts[1]),
                np.linalg.norm(pts[0] - pts[2])
            ]
            
            perimeter_sq = sum(e**2 for e in edges)
            quality = 4 * np.sqrt(3) * area / perimeter_sq if perimeter_sq > 0 else 0
            qualities.append(quality)
        
        return float(np.mean(qualities))
