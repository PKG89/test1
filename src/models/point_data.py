"""Point data models for survey points and TIN structures."""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict, Any
from enum import Enum


class PointType(Enum):
    """Type of survey point."""
    ORIGINAL = "original"
    GENERATED = "generated"
    EDITED = "edited"


@dataclass
class SurveyPoint:
    """A single survey point with coordinates and metadata."""
    x: float
    y: float
    z: float
    point_type: PointType = PointType.ORIGINAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array [x, y, z]."""
        return np.array([self.x, self.y, self.z])
    
    @classmethod
    def from_array(cls, arr: np.ndarray, point_type: PointType = PointType.ORIGINAL, 
                   metadata: Optional[Dict[str, Any]] = None) -> 'SurveyPoint':
        """Create from numpy array [x, y, z]."""
        return cls(
            x=float(arr[0]),
            y=float(arr[1]),
            z=float(arr[2]),
            point_type=point_type,
            metadata=metadata or {}
        )


@dataclass
class PointCloud:
    """Collection of survey points."""
    points: np.ndarray
    point_metadata: List[Dict[str, Any]] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def count(self) -> int:
        """Number of points in the cloud."""
        return len(self.points)
    
    @property
    def bounds(self) -> Tuple[float, float, float, float, float, float]:
        """Bounding box: (min_x, max_x, min_y, max_y, min_z, max_z)."""
        if self.count == 0:
            return (0, 0, 0, 0, 0, 0)
        min_vals = self.points.min(axis=0)
        max_vals = self.points.max(axis=0)
        return (float(min_vals[0]), float(max_vals[0]), 
                float(min_vals[1]), float(max_vals[1]),
                float(min_vals[2]), float(max_vals[2]))
    
    def get_points_by_type(self, point_type: PointType) -> np.ndarray:
        """Get points filtered by type."""
        if not self.point_metadata:
            return self.points if point_type == PointType.ORIGINAL else np.array([])
        
        indices = [i for i, meta in enumerate(self.point_metadata) 
                  if meta.get('type') == point_type.value]
        return self.points[indices] if indices else np.array([])


@dataclass
class TIN:
    """Triangulated Irregular Network model."""
    points: np.ndarray
    triangles: np.ndarray
    quality: float = 0.0
    
    @property
    def triangle_count(self) -> int:
        """Number of triangles in the TIN."""
        return len(self.triangles)
    
    def get_edges(self) -> List[Tuple[int, int]]:
        """Get all unique edges in the TIN."""
        edges = set()
        for triangle in self.triangles:
            edges.add(tuple(sorted([triangle[0], triangle[1]])))
            edges.add(tuple(sorted([triangle[1], triangle[2]])))
            edges.add(tuple(sorted([triangle[2], triangle[0]])))
        return list(edges)
