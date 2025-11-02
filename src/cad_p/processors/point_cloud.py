"""Point cloud processing functionality."""

import numpy as np
from typing import List, Tuple
from scipy.spatial import cKDTree

from src.models.point_data import PointCloud, SurveyPoint, PointType


class PointCloudProcessor:
    """Processor for point cloud operations."""
    
    def load_from_file(self, filepath: str, parse_codes: bool = False) -> PointCloud:
        """
        Load point cloud from file.
        
        Supports .txt and .xyz formats with X Y Z coordinates.
        Extended format: X Y Z [CODE] [COMMENT]
        
        Args:
            filepath: Path to coordinate file
            parse_codes: If True, parse codes and comments from extended format
        """
        if parse_codes:
            points, metadata = self._parse_file_with_codes(filepath)
        else:
            points = self._parse_file(filepath)
            metadata = [{'type': PointType.ORIGINAL.value} for _ in range(len(points))]
        return PointCloud(points=points, point_metadata=metadata)
    
    def _parse_file(self, filepath: str) -> np.ndarray:
        """Parse coordinate file (basic format)."""
        points = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        x, y, z = map(float, parts[:3])
                        points.append([x, y, z])
                    except ValueError:
                        continue
        
        if not points:
            raise ValueError("No valid points found in file")
        
        return np.array(points)
    
    def _parse_file_with_codes(self, filepath: str) -> tuple:
        """
        Parse coordinate file with codes and comments.
        
        Format: X Y Z [CODE] [COMMENT...]
        
        Returns:
            Tuple of (points array, metadata list)
        """
        points = []
        metadata = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        x, y, z = map(float, parts[:3])
                        
                        point_meta = {'type': PointType.ORIGINAL.value}
                        
                        if len(parts) >= 4:
                            point_meta['code'] = parts[3]
                        
                        if len(parts) >= 5:
                            point_meta['comment'] = ' '.join(parts[4:])
                        
                        points.append([x, y, z])
                        metadata.append(point_meta)
                    except ValueError:
                        continue
        
        if not points:
            raise ValueError("No valid points found in file")
        
        return np.array(points), metadata
    
    def remove_duplicates(self, cloud: PointCloud, tolerance: float = 0.001) -> PointCloud:
        """Remove duplicate points within tolerance."""
        if cloud.count == 0:
            return cloud
        
        tree = cKDTree(cloud.points[:, :2])
        unique_indices = []
        seen = set()
        
        for i in range(cloud.count):
            if i not in seen:
                point = cloud.points[i]
                neighbors = tree.query_ball_point(point[:2], tolerance)
                unique_indices.append(i)
                seen.update(neighbors)
        
        new_metadata = [cloud.point_metadata[i] for i in unique_indices] if cloud.point_metadata else []
        return PointCloud(
            points=cloud.points[unique_indices],
            point_metadata=new_metadata,
            attributes=cloud.attributes
        )
    
    def filter_outliers(self, cloud: PointCloud, sigma: float = 3.0) -> PointCloud:
        """Filter outliers using 3-sigma method."""
        if cloud.count == 0:
            return cloud
        
        z_mean = cloud.points[:, 2].mean()
        z_std = cloud.points[:, 2].std()
        
        mask = np.abs(cloud.points[:, 2] - z_mean) <= sigma * z_std
        indices = np.where(mask)[0]
        
        new_metadata = [cloud.point_metadata[i] for i in indices] if cloud.point_metadata else []
        return PointCloud(
            points=cloud.points[mask],
            point_metadata=new_metadata,
            attributes=cloud.attributes
        )
    
    def calculate_spacing_statistics(self, cloud: PointCloud) -> dict:
        """Calculate spacing statistics for the point cloud."""
        if cloud.count < 2:
            return {'mean_spacing': 0, 'min_spacing': 0, 'max_spacing': 0}
        
        tree = cKDTree(cloud.points[:, :2])
        distances, _ = tree.query(cloud.points[:, :2], k=2)
        nearest_distances = distances[:, 1]
        
        return {
            'mean_spacing': float(np.mean(nearest_distances)),
            'min_spacing': float(np.min(nearest_distances)),
            'max_spacing': float(np.max(nearest_distances)),
            'median_spacing': float(np.median(nearest_distances))
        }
