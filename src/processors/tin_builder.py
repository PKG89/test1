"""TIN (Triangulated Irregular Network) builder."""

import numpy as np
from scipy.spatial import Delaunay
from typing import Optional, List

from src.models.point_data import TIN, Polyline


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
    
    def build(self, points: np.ndarray, breaklines: Optional[List[Polyline]] = None) -> TIN:
        """
        Build TIN using Delaunay triangulation with optional breakline constraints.
        
        Args:
            points: Nx3 array of points (X, Y, Z)
            breaklines: List of Polyline objects representing constrained edges
            
        Returns:
            TIN object with triangulated network
        """
        if len(points) < 3:
            return TIN(points=points, triangles=np.array([]), quality=0.0, breaklines=[])
        
        tri = Delaunay(points[:, :2])
        
        triangles = tri.simplices
        
        if breaklines and len(breaklines) > 0:
            triangles = self._enforce_breaklines(points, triangles, breaklines)
        
        triangles = self._filter_long_edges(points, triangles)
        
        quality = self._calculate_quality(points, triangles)
        
        return TIN(points=points, triangles=triangles, quality=quality, breaklines=breaklines or [])
    
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
    
    def _enforce_breaklines(self, points: np.ndarray, triangles: np.ndarray, 
                           breaklines: List[Polyline]) -> np.ndarray:
        """
        Enforce breaklines by removing triangles that cross them.
        
        Uses triangle rejection method: removes triangles whose edges cross breaklines.
        
        Args:
            points: Nx3 array of points
            triangles: Mx3 array of triangle indices
            breaklines: List of Polyline objects
            
        Returns:
            Filtered array of triangles
        """
        if len(triangles) == 0 or not breaklines:
            return triangles
        
        breakline_segments = []
        for polyline in breaklines:
            for i in range(len(polyline.vertices) - 1):
                p1 = polyline.vertices[i]
                p2 = polyline.vertices[i + 1]
                breakline_segments.append((p1, p2))
            if polyline.is_closed and len(polyline.vertices) > 2:
                p1 = polyline.vertices[-1]
                p2 = polyline.vertices[0]
                breakline_segments.append((p1, p2))
        
        valid_triangles = []
        for triangle in triangles:
            if not self._triangle_crosses_breaklines(points[triangle], breakline_segments):
                valid_triangles.append(triangle)
        
        return np.array(valid_triangles) if valid_triangles else np.array([])
    
    def _triangle_crosses_breaklines(self, triangle_points: np.ndarray, 
                                    breakline_segments: List[tuple]) -> bool:
        """
        Check if a triangle crosses any breakline segments.
        
        Args:
            triangle_points: 3x3 array of triangle vertex coordinates
            breakline_segments: List of (p1, p2) tuples representing breakline segments
            
        Returns:
            True if triangle crosses any breakline
        """
        triangle_edges = [
            (triangle_points[0, :2], triangle_points[1, :2]),
            (triangle_points[1, :2], triangle_points[2, :2]),
            (triangle_points[2, :2], triangle_points[0, :2])
        ]
        
        for t_edge in triangle_edges:
            for b_seg in breakline_segments:
                if self._segments_intersect(t_edge[0], t_edge[1], b_seg[0][:2], b_seg[1][:2]):
                    if not self._points_coincident(t_edge[0], b_seg[0][:2]) and \
                       not self._points_coincident(t_edge[0], b_seg[1][:2]) and \
                       not self._points_coincident(t_edge[1], b_seg[0][:2]) and \
                       not self._points_coincident(t_edge[1], b_seg[1][:2]):
                        return True
        
        return False
    
    def _segments_intersect(self, p1: np.ndarray, p2: np.ndarray, 
                          p3: np.ndarray, p4: np.ndarray) -> bool:
        """
        Check if two line segments intersect.
        
        Args:
            p1, p2: Endpoints of first segment
            p3, p4: Endpoints of second segment
            
        Returns:
            True if segments intersect
        """
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)
    
    def _points_coincident(self, p1: np.ndarray, p2: np.ndarray, tol: float = 1e-6) -> bool:
        """Check if two points are coincident within tolerance."""
        return np.linalg.norm(p1 - p2) < tol
