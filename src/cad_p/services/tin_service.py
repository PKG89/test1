"""Service for TIN construction with breaklines support."""

import numpy as np
from typing import Dict, Any, List, Optional

from src.models.point_data import PointCloud, TIN, Polyline
from src.models.settings import TINSettings, TINCodeSelection
from src.processors.tin_builder import TINBuilder


class TINService:
    """Service for building TIN with code filtering and breakline support."""
    
    def __init__(self, settings: TINSettings):
        """
        Initialize TIN service.
        
        Args:
            settings: TIN construction settings
        """
        self.settings = settings
        self.builder = TINBuilder(max_edge_length=settings.max_edge_length)
    
    def build_tin(self, cloud: PointCloud) -> tuple[TIN, Dict[str, Any]]:
        """
        Build TIN from point cloud with code filtering and breaklines.
        
        Args:
            cloud: Input point cloud
            
        Returns:
            Tuple of (TIN object, statistics dictionary)
        """
        stats = {
            'skipped': False,
            'triangle_count': 0,
            'breakline_count': 0,
            'quality': 0.0,
            'points_used': 0,
            'points_filtered': 0
        }
        
        if not self.settings.enabled:
            stats['skipped'] = True
            empty_tin = TIN(points=np.array([]), triangles=np.array([]), quality=0.0)
            return empty_tin, stats
        
        if cloud.count < 3:
            stats['skipped'] = True
            stats['error'] = 'Insufficient points (need at least 3)'
            empty_tin = TIN(points=cloud.points, triangles=np.array([]), quality=0.0)
            return empty_tin, stats
        
        filtered_points = self._filter_points_by_code(cloud)
        stats['points_used'] = len(filtered_points)
        stats['points_filtered'] = cloud.count - len(filtered_points)
        
        if len(filtered_points) < 3:
            stats['skipped'] = True
            stats['error'] = 'Insufficient points after filtering'
            empty_tin = TIN(points=filtered_points, triangles=np.array([]), quality=0.0)
            return empty_tin, stats
        
        breaklines = []
        if self.settings.use_breaklines:
            breaklines = self._extract_breaklines(cloud)
            stats['breakline_count'] = len(breaklines)
        
        tin = self.builder.build(filtered_points, breaklines)
        
        stats['triangle_count'] = tin.triangle_count
        stats['quality'] = tin.quality
        
        return tin, stats
    
    def _filter_points_by_code(self, cloud: PointCloud) -> np.ndarray:
        """
        Filter points based on code selection settings.
        
        Args:
            cloud: Input point cloud
            
        Returns:
            Filtered array of points
        """
        if self.settings.code_selection == TINCodeSelection.ALL:
            return cloud.points
        
        if not cloud.point_metadata:
            return cloud.points
        
        selected_codes = self._get_selected_codes()
        
        indices = []
        for i, meta in enumerate(cloud.point_metadata):
            code = meta.get('code', 'other').lower()
            if code in selected_codes:
                indices.append(i)
        
        if not indices:
            return cloud.points
        
        return cloud.points[indices]
    
    def _get_selected_codes(self) -> List[str]:
        """Get list of codes to use based on settings."""
        if self.settings.code_selection == TINCodeSelection.ALL:
            return ['bpl', 'cpl', 'bord', 'terrain', 'other']
        elif self.settings.code_selection == TINCodeSelection.TERRAIN_ONLY:
            return ['terrain']
        elif self.settings.code_selection == TINCodeSelection.WITH_BREAKLINES:
            return ['terrain', 'bpl', 'cpl', 'bord']
        elif self.settings.code_selection == TINCodeSelection.CUSTOM:
            return self.settings.custom_codes
        else:
            return ['bpl', 'cpl', 'bord', 'terrain', 'other']
    
    def _extract_breaklines(self, cloud: PointCloud) -> List[Polyline]:
        """
        Extract breaklines from point cloud based on codes.
        
        Args:
            cloud: Input point cloud
            
        Returns:
            List of Polyline objects representing breaklines
        """
        if not cloud.point_metadata:
            return []
        
        breakline_codes = set(code.lower() for code in self.settings.breakline_codes)
        
        code_points = {}
        for i, meta in enumerate(cloud.point_metadata):
            code = meta.get('code', 'other').lower()
            if code in breakline_codes:
                if code not in code_points:
                    code_points[code] = []
                code_points[code].append(cloud.points[i])
        
        polylines = []
        for code, points in code_points.items():
            if len(points) >= 2:
                vertices = np.array(points)
                polylines.append(Polyline(
                    vertices=vertices,
                    code=code,
                    is_closed=False
                ))
        
        return polylines
