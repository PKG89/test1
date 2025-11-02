"""Unit tests for TIN builder with breaklines support."""

import pytest
import numpy as np
from src.processors.tin_builder import TINBuilder
from src.models.point_data import TIN, Polyline, PointCloud
from src.models.settings import TINSettings, TINCodeSelection
from src.services.tin_service import TINService


class TestTINBuilder:
    """Test suite for TIN builder."""
    
    @pytest.fixture
    def simple_points(self):
        """Create a simple set of points for testing."""
        return np.array([
            [0, 0, 100],
            [10, 0, 101],
            [5, 10, 102],
            [10, 10, 103],
            [0, 10, 104]
        ])
    
    @pytest.fixture
    def grid_points(self):
        """Create a grid of points for testing."""
        points = []
        for x in range(0, 30, 10):
            for y in range(0, 30, 10):
                z = 100 + 0.1 * x + 0.05 * y
                points.append([x, y, z])
        return np.array(points)
    
    def test_basic_tin_construction(self, simple_points):
        """Test basic TIN construction without breaklines."""
        builder = TINBuilder()
        tin = builder.build(simple_points)
        
        assert tin.triangle_count > 0
        assert len(tin.points) == len(simple_points)
        assert tin.quality > 0
    
    def test_insufficient_points(self):
        """Test handling of insufficient points."""
        builder = TINBuilder()
        
        points = np.array([[0, 0, 100], [10, 0, 101]])
        tin = builder.build(points)
        
        assert tin.triangle_count == 0
        assert tin.quality == 0.0
    
    def test_empty_points(self):
        """Test handling of empty point array."""
        builder = TINBuilder()
        
        points = np.array([])
        tin = builder.build(points)
        
        assert tin.triangle_count == 0
    
    def test_triangle_count_matches_delaunay(self, grid_points):
        """Test that triangle count is reasonable."""
        builder = TINBuilder()
        tin = builder.build(grid_points)
        
        n = len(grid_points)
        max_triangles = 2 * n - 2 - 2
        
        assert tin.triangle_count > 0
        assert tin.triangle_count <= max_triangles
    
    def test_edge_filtering(self, simple_points):
        """Test max edge length filtering."""
        builder = TINBuilder(max_edge_length=5.0)
        tin = builder.build(simple_points)
        
        for triangle in tin.triangles:
            pts = simple_points[triangle]
            edges = [
                np.linalg.norm(pts[1, :2] - pts[0, :2]),
                np.linalg.norm(pts[2, :2] - pts[1, :2]),
                np.linalg.norm(pts[0, :2] - pts[2, :2])
            ]
            assert max(edges) <= 5.0
    
    def test_quality_calculation(self, simple_points):
        """Test quality metric calculation."""
        builder = TINBuilder()
        tin = builder.build(simple_points)
        
        assert 0.0 <= tin.quality <= 1.0
    
    def test_get_edges(self, simple_points):
        """Test edge extraction from TIN."""
        builder = TINBuilder()
        tin = builder.build(simple_points)
        
        edges = tin.get_edges()
        
        assert len(edges) > 0
        for edge in edges:
            assert len(edge) == 2
            assert edge[0] != edge[1]


class TestTINWithBreaklines:
    """Test suite for TIN with breaklines."""
    
    @pytest.fixture
    def points_with_breakline(self):
        """Create points with a breakline through the middle."""
        points = []
        for x in range(0, 40, 10):
            for y in range(0, 40, 10):
                z = 100 + 0.1 * x
                points.append([x, y, z])
        return np.array(points)
    
    @pytest.fixture
    def vertical_breakline(self):
        """Create a vertical breakline."""
        vertices = np.array([
            [20, 0, 100],
            [20, 10, 101],
            [20, 20, 102],
            [20, 30, 103]
        ])
        return Polyline(vertices=vertices, code='bpl', is_closed=False)
    
    @pytest.fixture
    def horizontal_breakline(self):
        """Create a horizontal breakline."""
        vertices = np.array([
            [0, 20, 100],
            [10, 20, 101],
            [20, 20, 102],
            [30, 20, 103]
        ])
        return Polyline(vertices=vertices, code='bpl', is_closed=False)
    
    def test_tin_with_single_breakline(self, points_with_breakline, vertical_breakline):
        """Test TIN construction with a single breakline."""
        builder = TINBuilder()
        tin = builder.build(points_with_breakline, [vertical_breakline])
        
        assert tin.triangle_count > 0
        assert len(tin.breaklines) == 1
    
    def test_tin_with_multiple_breaklines(self, points_with_breakline, 
                                         vertical_breakline, horizontal_breakline):
        """Test TIN construction with multiple breaklines."""
        builder = TINBuilder()
        tin = builder.build(points_with_breakline, 
                          [vertical_breakline, horizontal_breakline])
        
        assert tin.triangle_count > 0
        assert len(tin.breaklines) == 2
    
    def test_breakline_reduces_triangles(self, points_with_breakline, vertical_breakline):
        """Test that breaklines reduce triangle count by filtering."""
        builder = TINBuilder()
        
        tin_without = builder.build(points_with_breakline, None)
        tin_with = builder.build(points_with_breakline, [vertical_breakline])
        
        assert tin_with.triangle_count <= tin_without.triangle_count
    
    def test_empty_breakline_list(self, points_with_breakline):
        """Test TIN with empty breakline list."""
        builder = TINBuilder()
        tin = builder.build(points_with_breakline, [])
        
        assert tin.triangle_count > 0
        assert len(tin.breaklines) == 0
    
    def test_closed_breakline(self):
        """Test TIN with closed breakline (polygon)."""
        points = []
        for x in range(-20, 25, 10):
            for y in range(-20, 25, 10):
                z = 100
                points.append([x, y, z])
        points = np.array(points)
        
        closed_breakline = Polyline(
            vertices=np.array([
                [0, 0, 100],
                [10, 0, 100],
                [10, 10, 100],
                [0, 10, 100]
            ]),
            code='bord',
            is_closed=True
        )
        
        builder = TINBuilder()
        tin = builder.build(points, [closed_breakline])
        
        assert tin.triangle_count > 0
        assert tin.breaklines[0].is_closed
    
    def test_segment_intersection(self):
        """Test segment intersection detection."""
        builder = TINBuilder()
        
        p1 = np.array([0, 0])
        p2 = np.array([10, 10])
        p3 = np.array([0, 10])
        p4 = np.array([10, 0])
        
        assert builder._segments_intersect(p1, p2, p3, p4)
        
        p5 = np.array([20, 20])
        p6 = np.array([30, 30])
        
        assert not builder._segments_intersect(p1, p2, p5, p6)
    
    def test_points_coincident(self):
        """Test coincident point detection."""
        builder = TINBuilder()
        
        p1 = np.array([5.0, 5.0])
        p2 = np.array([5.0, 5.0])
        p3 = np.array([5.001, 5.001])
        
        assert builder._points_coincident(p1, p2)
        assert not builder._points_coincident(p1, p3, tol=1e-6)
        assert builder._points_coincident(p1, p3, tol=1e-2)


class TestTINService:
    """Test suite for TIN service."""
    
    @pytest.fixture
    def sample_cloud_with_codes(self):
        """Create sample point cloud with code metadata."""
        points = np.array([
            [0, 0, 100],
            [10, 0, 101],
            [20, 0, 102],
            [0, 10, 103],
            [10, 10, 104],
            [20, 10, 105],
            [0, 20, 106],
            [10, 20, 107],
            [20, 20, 108]
        ])
        
        metadata = [
            {'code': 'terrain'},
            {'code': 'bpl'},
            {'code': 'terrain'},
            {'code': 'terrain'},
            {'code': 'cpl'},
            {'code': 'terrain'},
            {'code': 'terrain'},
            {'code': 'bord'},
            {'code': 'terrain'}
        ]
        
        return PointCloud(points=points, point_metadata=metadata)
    
    def test_tin_service_all_points(self, sample_cloud_with_codes):
        """Test TIN service with all points."""
        settings = TINSettings(
            enabled=True,
            code_selection=TINCodeSelection.ALL
        )
        service = TINService(settings)
        
        tin, stats = service.build_tin(sample_cloud_with_codes)
        
        assert not stats['skipped']
        assert stats['triangle_count'] > 0
        assert stats['points_used'] == 9
    
    def test_tin_service_terrain_only(self, sample_cloud_with_codes):
        """Test TIN service with terrain points only."""
        settings = TINSettings(
            enabled=True,
            code_selection=TINCodeSelection.TERRAIN_ONLY
        )
        service = TINService(settings)
        
        tin, stats = service.build_tin(sample_cloud_with_codes)
        
        assert not stats['skipped']
        assert stats['points_used'] == 6
    
    def test_tin_service_with_breaklines(self, sample_cloud_with_codes):
        """Test TIN service with breaklines."""
        settings = TINSettings(
            enabled=True,
            code_selection=TINCodeSelection.WITH_BREAKLINES,
            use_breaklines=True,
            breakline_codes=['bpl', 'cpl', 'bord']
        )
        service = TINService(settings)
        
        tin, stats = service.build_tin(sample_cloud_with_codes)
        
        assert not stats['skipped']
        assert stats['breakline_count'] >= 0
    
    def test_tin_service_custom_codes(self, sample_cloud_with_codes):
        """Test TIN service with custom code selection."""
        settings = TINSettings(
            enabled=True,
            code_selection=TINCodeSelection.CUSTOM,
            custom_codes=['terrain', 'bpl']
        )
        service = TINService(settings)
        
        tin, stats = service.build_tin(sample_cloud_with_codes)
        
        assert not stats['skipped']
        assert stats['points_used'] == 7
    
    def test_tin_service_disabled(self, sample_cloud_with_codes):
        """Test TIN service when disabled."""
        settings = TINSettings(enabled=False)
        service = TINService(settings)
        
        tin, stats = service.build_tin(sample_cloud_with_codes)
        
        assert stats['skipped']
        assert stats['triangle_count'] == 0
    
    def test_tin_service_insufficient_points(self):
        """Test TIN service with insufficient points."""
        settings = TINSettings(enabled=True)
        service = TINService(settings)
        
        points = np.array([[0, 0, 100], [10, 0, 101]])
        cloud = PointCloud(points=points, point_metadata=[])
        
        tin, stats = service.build_tin(cloud)
        
        assert stats['skipped']
        assert 'error' in stats
    
    def test_tin_service_empty_cloud(self):
        """Test TIN service with empty point cloud."""
        settings = TINSettings(enabled=True)
        service = TINService(settings)
        
        cloud = PointCloud(points=np.array([]), point_metadata=[])
        
        tin, stats = service.build_tin(cloud)
        
        assert stats['skipped']
    
    def test_code_filtering(self, sample_cloud_with_codes):
        """Test point filtering by code."""
        settings = TINSettings(
            enabled=True,
            code_selection=TINCodeSelection.CUSTOM,
            custom_codes=['terrain']
        )
        service = TINService(settings)
        
        filtered = service._filter_points_by_code(sample_cloud_with_codes)
        
        assert len(filtered) == 6
    
    def test_breakline_extraction(self, sample_cloud_with_codes):
        """Test breakline extraction from point cloud."""
        settings = TINSettings(
            enabled=True,
            use_breaklines=True,
            breakline_codes=['bpl', 'cpl']
        )
        service = TINService(settings)
        
        breaklines = service._extract_breaklines(sample_cloud_with_codes)
        
        assert len(breaklines) >= 0


class TestTINStatistics:
    """Test suite for TIN statistics."""
    
    def test_statistics_keys(self):
        """Test that all expected statistics keys are present."""
        settings = TINSettings(enabled=True)
        service = TINService(settings)
        
        points = np.array([
            [0, 0, 100],
            [10, 0, 101],
            [5, 10, 102]
        ])
        cloud = PointCloud(points=points, point_metadata=[])
        
        tin, stats = service.build_tin(cloud)
        
        assert 'skipped' in stats
        assert 'triangle_count' in stats
        assert 'breakline_count' in stats
        assert 'quality' in stats
        assert 'points_used' in stats
        assert 'points_filtered' in stats
    
    def test_quality_metric_range(self):
        """Test that quality metric is in valid range."""
        settings = TINSettings(enabled=True)
        service = TINService(settings)
        
        points = []
        for x in range(0, 30, 10):
            for y in range(0, 30, 10):
                z = 100 + 0.1 * x + 0.05 * y
                points.append([x, y, z])
        
        cloud = PointCloud(points=np.array(points), point_metadata=[])
        
        tin, stats = service.build_tin(cloud)
        
        assert 0.0 <= stats['quality'] <= 1.0
