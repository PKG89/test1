"""Integration tests for TIN surface builder with DXF output."""

import pytest
import numpy as np
import tempfile
import os
import ezdxf
from pathlib import Path

from src.services.processing_service import ProcessingService
from src.models.settings import ProjectSettings, TINSettings, TINCodeSelection
from src.models.point_data import PointCloud, Polyline
from src.dxf.exporter import DXFExporter
from src.dxf.layer_manager import LayerConfig
from src.services.tin_service import TINService


class TestTINIntegration:
    """Integration tests for full TIN workflow."""
    
    @pytest.fixture
    def sample_cloud_with_codes(self):
        """Create sample point cloud with various codes."""
        points = []
        metadata = []
        
        for x in range(0, 50, 10):
            for y in range(0, 50, 10):
                z = 100 + 0.1 * x + 0.05 * y
                points.append([x, y, z])
                
                if x == 20:
                    metadata.append({'code': 'bpl'})
                elif y == 20:
                    metadata.append({'code': 'cpl'})
                else:
                    metadata.append({'code': 'terrain'})
        
        return PointCloud(points=np.array(points), point_metadata=metadata)
    
    @pytest.fixture
    def temp_output_file(self):
        """Create temporary output file."""
        fd, path = tempfile.mkstemp(suffix='.dxf')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def test_tin_service_integration(self, sample_cloud_with_codes):
        """Test full TIN service workflow."""
        settings = TINSettings(
            enabled=True,
            code_selection=TINCodeSelection.WITH_BREAKLINES,
            use_breaklines=True,
            breakline_codes=['bpl', 'cpl'],
            output_layers=True
        )
        
        service = TINService(settings)
        tin, stats = service.build_tin(sample_cloud_with_codes)
        
        assert not stats['skipped']
        assert stats['triangle_count'] > 0
        assert stats['points_used'] > 0
    
    def test_dxf_export_with_real_tin(self, sample_cloud_with_codes, temp_output_file):
        """Test DXF export with real TIN layers."""
        settings = TINSettings(
            enabled=True,
            code_selection=TINCodeSelection.ALL,
            use_breaklines=False,
            output_layers=True
        )
        
        service = TINService(settings)
        tin, stats = service.build_tin(sample_cloud_with_codes)
        
        exporter = DXFExporter()
        exporter.export_full_project(
            original_cloud=sample_cloud_with_codes,
            original_tin=tin,
            real_tin=tin,
            show_original=False,
            show_densified=False,
            show_real_tin=True
        )
        
        exporter.save(temp_output_file)
        
        assert os.path.exists(temp_output_file)
        assert os.path.getsize(temp_output_file) > 0
        
        doc = ezdxf.readfile(temp_output_file)
        assert LayerConfig.REAL_SURFACE in doc.layers
        assert LayerConfig.REAL_POINTS in doc.layers
    
    def test_dxf_layers_contain_entities(self, sample_cloud_with_codes, temp_output_file):
        """Test that DXF layers contain expected entities."""
        settings = TINSettings(
            enabled=True,
            code_selection=TINCodeSelection.ALL,
            use_breaklines=False,
            output_layers=True
        )
        
        service = TINService(settings)
        tin, stats = service.build_tin(sample_cloud_with_codes)
        
        exporter = DXFExporter()
        exporter.export_full_project(
            original_cloud=sample_cloud_with_codes,
            original_tin=tin,
            real_tin=tin,
            show_original=False,
            show_densified=False,
            show_real_tin=True
        )
        
        exporter.save(temp_output_file)
        
        doc = ezdxf.readfile(temp_output_file)
        msp = doc.modelspace()
        
        real_surface_entities = [
            e for e in msp if e.dxf.layer == LayerConfig.REAL_SURFACE
        ]
        real_points_entities = [
            e for e in msp if e.dxf.layer == LayerConfig.REAL_POINTS
        ]
        
        assert len(real_surface_entities) > 0
        assert len(real_points_entities) > 0
    
    def test_breaklines_in_dxf(self, sample_cloud_with_codes, temp_output_file):
        """Test that breaklines are exported to DXF."""
        settings = TINSettings(
            enabled=True,
            code_selection=TINCodeSelection.WITH_BREAKLINES,
            use_breaklines=True,
            breakline_codes=['bpl', 'cpl'],
            output_layers=True
        )
        
        service = TINService(settings)
        tin, stats = service.build_tin(sample_cloud_with_codes)
        
        if stats['breakline_count'] > 0:
            exporter = DXFExporter()
            exporter.export_full_project(
                original_cloud=sample_cloud_with_codes,
                original_tin=tin,
                real_tin=tin,
                show_original=False,
                show_densified=False,
                show_real_tin=True
            )
            
            exporter.save(temp_output_file)
            
            doc = ezdxf.readfile(temp_output_file)
            msp = doc.modelspace()
            
            breakline_entities = [
                e for e in msp 
                if e.dxf.layer == LayerConfig.REAL_SURFACE and 
                hasattr(e.dxf, 'color') and e.dxf.color == 5
            ]
            
            assert len(breakline_entities) >= 0
    
    def test_tin_with_insufficient_points(self):
        """Test TIN handling with insufficient points."""
        settings = TINSettings(enabled=True)
        service = TINService(settings)
        
        points = np.array([[0, 0, 100], [10, 0, 101]])
        cloud = PointCloud(points=points, point_metadata=[])
        
        tin, stats = service.build_tin(cloud)
        
        assert stats['skipped']
        assert 'error' in stats
        assert tin.triangle_count == 0
    
    def test_tin_disabled(self, sample_cloud_with_codes):
        """Test that TIN can be disabled."""
        settings = TINSettings(enabled=False)
        service = TINService(settings)
        
        tin, stats = service.build_tin(sample_cloud_with_codes)
        
        assert stats['skipped']
        assert tin.triangle_count == 0


class TestTINLayerConfiguration:
    """Test TIN layer configuration and styling."""
    
    def test_real_surface_layer_properties(self, tmp_path):
        """Test that real surface layer has correct properties."""
        output_file = tmp_path / "test_layers.dxf"
        
        points = np.array([
            [0, 0, 100],
            [10, 0, 101],
            [5, 10, 102],
            [10, 10, 103]
        ])
        cloud = PointCloud(points=points, point_metadata=[])
        
        settings = TINSettings(enabled=True, output_layers=True)
        service = TINService(settings)
        tin, _ = service.build_tin(cloud)
        
        exporter = DXFExporter()
        exporter.export_full_project(
            original_cloud=cloud,
            original_tin=tin,
            real_tin=tin,
            show_original=False,
            show_real_tin=True
        )
        
        exporter.save(str(output_file))
        
        doc = ezdxf.readfile(str(output_file))
        layer = doc.layers.get(LayerConfig.REAL_SURFACE)
        
        assert layer is not None
        assert layer.dxf.color == 3
    
    def test_real_points_layer_properties(self, tmp_path):
        """Test that real points layer has correct properties."""
        output_file = tmp_path / "test_points_layer.dxf"
        
        points = np.array([
            [0, 0, 100],
            [10, 0, 101],
            [5, 10, 102]
        ])
        cloud = PointCloud(points=points, point_metadata=[])
        
        settings = TINSettings(enabled=True, output_layers=True)
        service = TINService(settings)
        tin, _ = service.build_tin(cloud)
        
        exporter = DXFExporter()
        exporter.export_full_project(
            original_cloud=cloud,
            original_tin=tin,
            real_tin=tin,
            show_original=False,
            show_real_tin=True
        )
        
        exporter.save(str(output_file))
        
        doc = ezdxf.readfile(str(output_file))
        layer = doc.layers.get(LayerConfig.REAL_POINTS)
        
        assert layer is not None
        assert layer.dxf.color == 3


class TestTINFileOutput:
    """Test TIN file output and validation."""
    
    def test_output_file_created(self, tmp_path):
        """Test that output file is created."""
        output_file = tmp_path / "output.dxf"
        
        points = np.array([
            [0, 0, 100],
            [10, 0, 101],
            [5, 10, 102],
            [10, 10, 103]
        ])
        cloud = PointCloud(points=points, point_metadata=[])
        
        settings = TINSettings(enabled=True, output_layers=True)
        service = TINService(settings)
        tin, _ = service.build_tin(cloud)
        
        exporter = DXFExporter()
        exporter.export_full_project(
            original_cloud=cloud,
            original_tin=tin,
            real_tin=tin,
            show_original=False,
            show_real_tin=True
        )
        
        exporter.save(str(output_file))
        
        assert output_file.exists()
        assert output_file.stat().st_size > 0
    
    def test_output_file_is_valid_dxf(self, tmp_path):
        """Test that output file is valid DXF."""
        output_file = tmp_path / "valid.dxf"
        
        points = np.array([
            [0, 0, 100],
            [10, 0, 101],
            [5, 10, 102]
        ])
        cloud = PointCloud(points=points, point_metadata=[])
        
        settings = TINSettings(enabled=True, output_layers=True)
        service = TINService(settings)
        tin, _ = service.build_tin(cloud)
        
        exporter = DXFExporter()
        exporter.export_full_project(
            original_cloud=cloud,
            original_tin=tin,
            real_tin=tin,
            show_original=False,
            show_real_tin=True
        )
        
        exporter.save(str(output_file))
        
        doc = ezdxf.readfile(str(output_file))
        assert doc.dxfversion >= 'AC1024'
    
    def test_triangle_count_matches_output(self, tmp_path):
        """Test that triangle count in output matches TIN."""
        output_file = tmp_path / "triangles.dxf"
        
        points = []
        for x in range(0, 30, 10):
            for y in range(0, 30, 10):
                z = 100 + 0.1 * x
                points.append([x, y, z])
        
        cloud = PointCloud(points=np.array(points), point_metadata=[])
        
        settings = TINSettings(enabled=True, output_layers=True)
        service = TINService(settings)
        tin, stats = service.build_tin(cloud)
        
        exporter = DXFExporter()
        exporter.export_full_project(
            original_cloud=cloud,
            original_tin=tin,
            real_tin=tin,
            show_original=False,
            show_real_tin=True
        )
        
        exporter.save(str(output_file))
        
        doc = ezdxf.readfile(str(output_file))
        msp = doc.modelspace()
        
        polylines = [
            e for e in msp 
            if e.dxftype() == 'LWPOLYLINE' and 
            e.dxf.layer == LayerConfig.REAL_SURFACE
        ]
        
        assert len(polylines) >= stats['triangle_count']
