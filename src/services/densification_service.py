"""Relief densification service."""

import numpy as np
from scipy.interpolate import LinearNDInterpolator, CloughTocher2DInterpolator, NearestNDInterpolator
from scipy.spatial import ConvexHull
from typing import Tuple, Dict, Any, List

from src.models.point_data import PointCloud, TIN, PointType
from src.models.settings import DensificationSettings, InterpolationMethod


class DensificationService:
    """Service for relief densification using gridding and interpolation."""
    
    def __init__(self, settings: DensificationSettings):
        """
        Initialize densification service.
        
        Args:
            settings: Densification configuration
        """
        self.settings = settings
    
    def densify(self, cloud: PointCloud, tin: TIN) -> Tuple[PointCloud, Dict[str, Any]]:
        """
        Densify point cloud by generating synthetic points in sparse regions.
        
        Args:
            cloud: Original point cloud
            tin: Triangulated network of original points
            
        Returns:
            Tuple of (densified point cloud, statistics dictionary)
        """
        if not self.settings.enabled or cloud.count < 3:
            return cloud, {'generated_points': 0, 'skipped': True}
        
        stats = {
            'original_points': cloud.count,
            'generated_points': 0,
            'skipped': False
        }
        
        sparse_regions = self._identify_sparse_regions(cloud, tin)
        stats['sparse_regions_found'] = len(sparse_regions)
        
        if not sparse_regions:
            return cloud, stats
        
        generated_points = self._generate_points_in_regions(
            cloud.points, sparse_regions
        )
        
        if len(generated_points) == 0:
            return cloud, stats
        
        if len(generated_points) > self.settings.max_points:
            generated_points = generated_points[:self.settings.max_points]
            stats['limited_by_max'] = True
        
        interpolator = self._create_interpolator(cloud.points)
        z_values = interpolator(generated_points[:, 0], generated_points[:, 1])
        
        valid_mask = ~np.isnan(z_values)
        valid_generated = np.column_stack([
            generated_points[valid_mask],
            z_values[valid_mask]
        ])
        
        stats['generated_points'] = len(valid_generated)
        
        combined_points = np.vstack([cloud.points, valid_generated])
        
        combined_metadata = cloud.point_metadata.copy()
        for _ in range(len(valid_generated)):
            combined_metadata.append({
                'type': PointType.GENERATED.value,
                'method': self.settings.interpolation_method.value,
                'grid_spacing': self.settings.grid_spacing
            })
        
        densified_cloud = PointCloud(
            points=combined_points,
            point_metadata=combined_metadata,
            attributes={**cloud.attributes, 'densified': True}
        )
        
        return densified_cloud, stats
    
    def _identify_sparse_regions(self, cloud: PointCloud, tin: TIN) -> List[np.ndarray]:
        """
        Identify sparse regions using convex hull and spacing threshold.
        
        Returns list of bounding boxes for sparse regions.
        """
        if tin.triangle_count == 0:
            return []
        
        sparse_regions = []
        
        for triangle in tin.triangles:
            tri_points = cloud.points[triangle]
            
            edge_lengths = [
                np.linalg.norm(tri_points[1, :2] - tri_points[0, :2]),
                np.linalg.norm(tri_points[2, :2] - tri_points[1, :2]),
                np.linalg.norm(tri_points[0, :2] - tri_points[2, :2])
            ]
            
            max_edge = max(edge_lengths)
            
            if max_edge > self.settings.min_spacing_threshold:
                min_x = tri_points[:, 0].min()
                max_x = tri_points[:, 0].max()
                min_y = tri_points[:, 1].min()
                max_y = tri_points[:, 1].max()
                
                sparse_regions.append(np.array([
                    [min_x, min_y],
                    [max_x, max_y],
                    tri_points[:, :2]
                ], dtype=object))
        
        return sparse_regions
    
    def _generate_points_in_regions(self, original_points: np.ndarray, 
                                   regions: List[np.ndarray]) -> np.ndarray:
        """Generate grid points in sparse regions."""
        all_generated = []
        
        hull = ConvexHull(original_points[:, :2])
        hull_points = original_points[hull.vertices, :2]
        
        for region in regions:
            bbox = region[:2]
            triangle_points = region[2]
            
            min_x, min_y = bbox[0]
            max_x, max_y = bbox[1]
            
            x_points = np.arange(min_x, max_x, self.settings.grid_spacing)
            y_points = np.arange(min_y, max_y, self.settings.grid_spacing)
            
            xx, yy = np.meshgrid(x_points, y_points)
            grid_points = np.column_stack([xx.ravel(), yy.ravel()])
            
            if len(triangle_points) >= 3:
                inside_mask = self._points_in_triangle(grid_points, triangle_points)
                grid_points = grid_points[inside_mask]
            
            inside_hull = self._points_in_convex_hull(grid_points, hull_points)
            grid_points = grid_points[inside_hull]
            
            if len(grid_points) > 0:
                all_generated.append(grid_points)
        
        if not all_generated:
            return np.array([])
        
        return np.vstack(all_generated)
    
    def _create_interpolator(self, points: np.ndarray):
        """Create interpolator based on settings."""
        xy = points[:, :2]
        z = points[:, 2]
        
        if self.settings.interpolation_method == InterpolationMethod.LINEAR:
            return LinearNDInterpolator(xy, z)
        elif self.settings.interpolation_method == InterpolationMethod.CUBIC:
            return CloughTocher2DInterpolator(xy, z)
        elif self.settings.interpolation_method == InterpolationMethod.NEAREST:
            return NearestNDInterpolator(xy, z)
        else:
            return LinearNDInterpolator(xy, z)
    
    def _points_in_triangle(self, points: np.ndarray, triangle: np.ndarray) -> np.ndarray:
        """Check if points are inside a triangle using barycentric coordinates."""
        if len(triangle) < 3:
            return np.zeros(len(points), dtype=bool)
        
        v0 = triangle[2] - triangle[0]
        v1 = triangle[1] - triangle[0]
        v2 = points - triangle[0]
        
        dot00 = np.dot(v0, v0)
        dot01 = np.dot(v0, v1)
        dot02 = np.dot(v2, v0)
        dot11 = np.dot(v1, v1)
        dot12 = np.dot(v2, v1)
        
        inv_denom = 1 / (dot00 * dot11 - dot01 * dot01) if (dot00 * dot11 - dot01 * dot01) != 0 else 0
        
        u = (dot11 * dot02 - dot01 * dot12) * inv_denom
        v = (dot00 * dot12 - dot01 * dot02) * inv_denom
        
        return (u >= 0) & (v >= 0) & (u + v <= 1)
    
    def _points_in_convex_hull(self, points: np.ndarray, hull_points: np.ndarray) -> np.ndarray:
        """Check if points are inside convex hull."""
        if len(points) == 0 or len(hull_points) < 3:
            return np.zeros(len(points), dtype=bool)
        
        try:
            hull = ConvexHull(hull_points)
            from scipy.spatial import Delaunay
            delaunay = Delaunay(hull_points)
            return delaunay.find_simplex(points) >= 0
        except:
            return np.ones(len(points), dtype=bool)
