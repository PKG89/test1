"""Unit tests for densification service."""

import pytest
import numpy as np
from src.services.densification_service import DensificationService
from src.models.settings import DensificationSettings, InterpolationMethod
from src.models.point_data import PointCloud, TIN, PointType
from src.processors.tin_builder import TINBuilder


class TestDensificationService:
    """Test suite for densification service."""
    
    @pytest.fixture
    def sample_sparse_points(self):
        """Create a sparse grid of points for testing."""
        points = []
        for x in range(0, 50, 10):
            for y in range(0, 50, 10):
                z = 100 + 0.1 * x + 0.05 * y
                points.append([x, y, z])
        return np.array(points)
    
    @pytest.fixture
    def sample_cloud(self, sample_sparse_points):
        """Create sample point cloud."""
        metadata = [{'type': PointType.ORIGINAL.value} for _ in range(len(sample_sparse_points))]
        return PointCloud(
            points=sample_sparse_points,
            point_metadata=metadata
        )
    
    @pytest.fixture
    def sample_tin(self, sample_sparse_points):
        """Create sample TIN."""
        builder = TINBuilder()
        return builder.build(sample_sparse_points)
    
    def test_densification_disabled(self, sample_cloud, sample_tin):
        """Test that densification can be disabled."""
        settings = DensificationSettings(enabled=False)
        service = DensificationService(settings)
        
        result_cloud, stats = service.densify(sample_cloud, sample_tin)
        
        assert stats['skipped'] is True
        assert stats['generated_points'] == 0
        assert result_cloud.count == sample_cloud.count
    
    def test_densification_enabled(self, sample_cloud, sample_tin):
        """Test that densification generates new points."""
        settings = DensificationSettings(
            enabled=True,
            grid_spacing=5.0,
            min_spacing_threshold=8.0
        )
        service = DensificationService(settings)
        
        result_cloud, stats = service.densify(sample_cloud, sample_tin)
        
        assert stats['generated_points'] > 0
        assert result_cloud.count > sample_cloud.count
        assert stats['original_points'] == sample_cloud.count
    
    def test_sparse_region_identification(self, sample_cloud, sample_tin):
        """Test identification of sparse regions."""
        settings = DensificationSettings(
            enabled=True,
            min_spacing_threshold=8.0
        )
        service = DensificationService(settings)
        
        sparse_regions = service._identify_sparse_regions(sample_cloud, sample_tin)
        
        assert len(sparse_regions) > 0
    
    def test_max_points_limit(self, sample_cloud, sample_tin):
        """Test that max_points limit is enforced."""
        settings = DensificationSettings(
            enabled=True,
            grid_spacing=2.0,
            max_points=50
        )
        service = DensificationService(settings)
        
        result_cloud, stats = service.densify(sample_cloud, sample_tin)
        
        generated = result_cloud.count - sample_cloud.count
        assert generated <= settings.max_points
    
    def test_linear_interpolation(self, sample_cloud, sample_tin):
        """Test linear interpolation method."""
        settings = DensificationSettings(
            enabled=True,
            interpolation_method=InterpolationMethod.LINEAR,
            grid_spacing=5.0
        )
        service = DensificationService(settings)
        
        result_cloud, stats = service.densify(sample_cloud, sample_tin)
        
        if stats['generated_points'] > 0:
            generated_points = result_cloud.get_points_by_type(PointType.GENERATED)
            assert len(generated_points) > 0
            assert not np.any(np.isnan(generated_points))
    
    def test_cubic_interpolation(self, sample_cloud, sample_tin):
        """Test cubic interpolation method."""
        settings = DensificationSettings(
            enabled=True,
            interpolation_method=InterpolationMethod.CUBIC,
            grid_spacing=5.0
        )
        service = DensificationService(settings)
        
        result_cloud, stats = service.densify(sample_cloud, sample_tin)
        
        assert 'generated_points' in stats
    
    def test_metadata_tagging(self, sample_cloud, sample_tin):
        """Test that generated points are properly tagged with metadata."""
        settings = DensificationSettings(
            enabled=True,
            grid_spacing=5.0,
            interpolation_method=InterpolationMethod.LINEAR
        )
        service = DensificationService(settings)
        
        result_cloud, stats = service.densify(sample_cloud, sample_tin)
        
        if stats['generated_points'] > 0:
            generated_count = 0
            for meta in result_cloud.point_metadata:
                if meta.get('type') == PointType.GENERATED.value:
                    generated_count += 1
                    assert 'method' in meta
                    assert 'grid_spacing' in meta
                    assert meta['method'] == 'linear'
                    assert meta['grid_spacing'] == 5.0
            
            assert generated_count == stats['generated_points']
    
    def test_convex_hull_constraint(self, sample_cloud, sample_tin):
        """Test that generated points are within convex hull of original points."""
        settings = DensificationSettings(
            enabled=True,
            grid_spacing=3.0
        )
        service = DensificationService(settings)
        
        result_cloud, stats = service.densify(sample_cloud, sample_tin)
        
        original_bounds = sample_cloud.bounds
        result_bounds = result_cloud.bounds
        
        assert result_bounds[0] >= original_bounds[0] - 1.0
        assert result_bounds[1] <= original_bounds[1] + 1.0
        assert result_bounds[2] >= original_bounds[2] - 1.0
        assert result_bounds[3] <= original_bounds[3] + 1.0
    
    def test_empty_point_cloud(self):
        """Test handling of empty point cloud."""
        settings = DensificationSettings(enabled=True)
        service = DensificationService(settings)
        
        empty_cloud = PointCloud(points=np.array([]), point_metadata=[])
        empty_tin = TIN(points=np.array([]), triangles=np.array([]))
        
        result_cloud, stats = service.densify(empty_cloud, empty_tin)
        
        assert result_cloud.count == 0
        assert stats['generated_points'] == 0
    
    def test_insufficient_points(self):
        """Test handling of insufficient points (less than 3)."""
        settings = DensificationSettings(enabled=True)
        service = DensificationService(settings)
        
        points = np.array([[0, 0, 100], [10, 0, 101]])
        cloud = PointCloud(points=points, point_metadata=[{'type': 'original'}, {'type': 'original'}])
        tin = TIN(points=points, triangles=np.array([]))
        
        result_cloud, stats = service.densify(cloud, tin)
        
        assert result_cloud.count == 2
        assert stats['generated_points'] == 0


class TestDensificationStatistics:
    """Test suite for densification statistics."""
    
    def test_statistics_keys(self):
        """Test that all expected statistics keys are present."""
        settings = DensificationSettings(enabled=True, grid_spacing=5.0)
        service = DensificationService(settings)
        
        points = np.array([[0, 0, 100], [10, 0, 101], [5, 10, 102], [15, 10, 103]])
        metadata = [{'type': PointType.ORIGINAL.value} for _ in range(len(points))]
        cloud = PointCloud(points=points, point_metadata=metadata)
        
        builder = TINBuilder()
        tin = builder.build(points)
        
        _, stats = service.densify(cloud, tin)
        
        assert 'original_points' in stats
        assert 'generated_points' in stats
        assert 'skipped' in stats
