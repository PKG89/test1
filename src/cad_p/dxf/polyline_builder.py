"""3D polyline builder with grouping logic."""

import numpy as np
from typing import List, Dict, Tuple, Optional
from scipy.spatial.distance import cdist
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class PointWithMetadata:
    """Point with code and comment metadata."""
    x: float
    y: float
    z: float
    code: str
    comment: Optional[str] = None
    
    @property
    def position(self) -> np.ndarray:
        """Get position as numpy array."""
        return np.array([self.x, self.y, self.z])
    
    @property
    def comment_first_digit(self) -> Optional[str]:
        """Get first digit from comment if available."""
        if self.comment:
            for char in str(self.comment):
                if char.isdigit():
                    return char
        return None


class Polyline3DBuilder:
    """Builder for 3D polylines with intelligent grouping."""
    
    def __init__(self, break_distance: float = 70.0):
        """
        Initialize 3D polyline builder.
        
        Args:
            break_distance: Distance threshold for breaking polylines (default: 70m)
        """
        self.break_distance = break_distance
    
    def group_points(self, points: List[PointWithMetadata]) -> Dict[str, List[List[PointWithMetadata]]]:
        """
        Group points by (code, comment_first_digit) and create polyline segments.
        
        Points are grouped by:
        1. Code (e.g., 'bord', 'rels')
        2. First digit of comment (when applicable)
        3. Break distance >70m creates new segment
        4. Special k-code logic: connect identical codes
        
        Args:
            points: List of points with metadata
            
        Returns:
            Dictionary mapping group keys to lists of polyline segments
        """
        if not points:
            return {}
        
        grouped = self._group_by_code_and_comment(points)
        
        polylines = {}
        for group_key, group_points in grouped.items():
            segments = self._create_segments(group_points)
            if segments:
                polylines[group_key] = segments
        
        return polylines
    
    def _group_by_code_and_comment(self, points: List[PointWithMetadata]) -> Dict[str, List[PointWithMetadata]]:
        """Group points by code and first digit of comment."""
        groups = defaultdict(list)
        
        for point in points:
            if point.code.lower().startswith('k'):
                group_key = f"{point.code}"
            else:
                digit = point.comment_first_digit
                if digit:
                    group_key = f"{point.code}_{digit}"
                else:
                    group_key = point.code
            
            groups[group_key].append(point)
        
        return dict(groups)
    
    def _create_segments(self, points: List[PointWithMetadata]) -> List[List[PointWithMetadata]]:
        """
        Create polyline segments from grouped points.
        
        Segments are broken when distance between consecutive points exceeds break_distance.
        Points are ordered to minimize total path length.
        """
        if len(points) < 2:
            return [[points[0]]] if points else []
        
        ordered_points = self._order_points_by_proximity(points)
        
        segments = []
        current_segment = [ordered_points[0]]
        
        for i in range(1, len(ordered_points)):
            prev_point = ordered_points[i - 1]
            curr_point = ordered_points[i]
            
            distance = self._calculate_distance(prev_point, curr_point)
            
            if distance > self.break_distance:
                if len(current_segment) >= 2:
                    segments.append(current_segment)
                current_segment = [curr_point]
            else:
                current_segment.append(curr_point)
        
        if len(current_segment) >= 2:
            segments.append(current_segment)
        
        return segments
    
    def _order_points_by_proximity(self, points: List[PointWithMetadata]) -> List[PointWithMetadata]:
        """
        Order points to minimize total path length (nearest neighbor approach).
        """
        if len(points) <= 1:
            return points
        
        positions = np.array([p.position for p in points])
        
        ordered = [points[0]]
        remaining_indices = set(range(1, len(points)))
        
        while remaining_indices:
            current_pos = ordered[-1].position
            
            remaining_positions = positions[list(remaining_indices)]
            distances = np.linalg.norm(remaining_positions - current_pos, axis=1)
            
            min_idx_in_remaining = np.argmin(distances)
            actual_idx = list(remaining_indices)[min_idx_in_remaining]
            
            ordered.append(points[actual_idx])
            remaining_indices.remove(actual_idx)
        
        return ordered
    
    def _calculate_distance(self, p1: PointWithMetadata, p2: PointWithMetadata) -> float:
        """Calculate Euclidean distance between two points."""
        return np.linalg.norm(p1.position - p2.position)
    
    def apply_k_code_logic(self, points: List[PointWithMetadata]) -> Dict[str, List[List[PointWithMetadata]]]:
        """
        Apply special logic for k-codes: connect all points with identical k-codes.
        
        Args:
            points: List of points with metadata
            
        Returns:
            Dictionary mapping k-code to polyline segments
        """
        k_points = [p for p in points if p.code.lower().startswith('k')]
        
        if not k_points:
            return {}
        
        k_groups = defaultdict(list)
        for point in k_points:
            k_groups[point.code].append(point)
        
        result = {}
        for code, group_points in k_groups.items():
            if len(group_points) >= 2:
                ordered = self._order_points_by_proximity(group_points)
                result[code] = [ordered]
        
        return result
    
    def build_polylines_for_points(self, points: List[PointWithMetadata], 
                                   layer: str,
                                   doc) -> List:
        """
        Build 3D polylines and add them to the DXF document.
        
        Args:
            points: List of points with metadata
            layer: Layer name for polylines
            doc: ezdxf Drawing document
            
        Returns:
            List of created polyline entities
        """
        msp = doc.modelspace()
        polylines_created = []
        
        grouped_polylines = self.group_points(points)
        
        for group_key, segments in grouped_polylines.items():
            for segment in segments:
                if len(segment) >= 2:
                    vertices = [(p.x, p.y, p.z) for p in segment]
                    
                    polyline = msp.add_polyline3d(
                        vertices,
                        dxfattribs={'layer': layer}
                    )
                    polylines_created.append(polyline)
        
        k_polylines = self.apply_k_code_logic(points)
        for code, segments in k_polylines.items():
            for segment in segments:
                if len(segment) >= 2:
                    vertices = [(p.x, p.y, p.z) for p in segment]
                    
                    polyline = msp.add_polyline3d(
                        vertices,
                        dxfattribs={'layer': layer}
                    )
                    polylines_created.append(polyline)
        
        return polylines_created
