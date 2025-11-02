"""Unit tests for DXF layer assignments."""

import pytest
import numpy as np
import tempfile
import os
from pathlib import Path

from src.dxf.exporter import DXFExporter
from src.dxf.layer_manager import LayerManager, LayerConfig
from src.models.point_data import PointCloud, TIN, PointType
from src.processors.tin_builder import TINBuilder


class TestLayerAssignment:
    """Test suite for layer assignments in DXF export."""
    
    @pytest.fixture
    def sample_points(self):
        """Create sample points for testing."""
        return np.array([
            [0, 0, 100],
            [10, 0, 101],
            [5, 10, 102],
            [10, 10, 103]
        ])
    
    @pytest.fixture
    def sample_cloud_with_generated(self):
        """Create point cloud with both original and generated points."""
        original = np.array([
            [0, 0, 100],
            [10, 0, 101],
            [5, 10, 102]
        ])
        generated = np.array([
            [5, 5, 101.5],
            [7, 7, 101.8]
        ])
        
        all_points = np.vstack([original, generated])
        metadata = [
            {'type': PointType.ORIGINAL.value},
            {'type': PointType.ORIGINAL.value},
            {'type': PointType.ORIGINAL.value},
            {'type': PointType.GENERATED.value, 'method': 'linear'},
            {'type': PointType.GENERATED.value, 'method': 'linear'}
        ]
        
        return PointCloud(points=all_points, point_metadata=metadata)
    
    def test_layer_creation(self):
        """Test that required layers are created."""
        exporter = DXFExporter()
        
        assert LayerConfig.EDITED_SURFACE in exporter.doc.layers
        assert LayerConfig.ADDED_POINTS in exporter.doc.layers
        assert LayerConfig.ORIGINAL_SURFACE in exporter.doc.layers
        assert LayerConfig.ORIGINAL_POINTS in exporter.doc.layers
    
    def test_layer_colors(self):
        """Test that layers have correct colors."""
        exporter = DXFExporter()
        
        edited_layer = exporter.doc.layers.get(LayerConfig.EDITED_SURFACE)
        added_layer = exporter.doc.layers.get(LayerConfig.ADDED_POINTS)
        
        assert edited_layer.color == 1
        assert added_layer.color == 1
    
    def test_original_points_on_correct_layer(self, sample_points):
        """Test that original points are placed on correct layer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test.dxf")
            
            exporter = DXFExporter()
            metadata = [{'type': PointType.ORIGINAL.value} for _ in range(len(sample_points))]
            exporter._export_points(sample_points, LayerConfig.ORIGINAL_POINTS, metadata)
            exporter.save(output_file)
            
            import ezdxf
            doc = ezdxf.readfile(output_file)
            
            entities_on_layer = [e for e in doc.modelspace() 
                                if e.dxf.layer == LayerConfig.ORIGINAL_POINTS]
            assert len(entities_on_layer) > 0
    
    def test_generated_points_on_correct_layer(self):
        """Test that generated points are placed on correct layer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test.dxf")
            
            generated_points = np.array([[5, 5, 101.5], [7, 7, 101.8]])
            metadata = [
                {'type': PointType.GENERATED.value},
                {'type': PointType.GENERATED.value}
            ]
            
            exporter = DXFExporter()
            exporter._export_generated_points(generated_points, LayerConfig.ADDED_POINTS, metadata)
            exporter.save(output_file)
            
            import ezdxf
            doc = ezdxf.readfile(output_file)
            
            entities_on_layer = [e for e in doc.modelspace() 
                                if e.dxf.layer == LayerConfig.ADDED_POINTS]
            assert len(entities_on_layer) > 0
    
    def test_generated_points_have_red_color(self):
        """Test that generated points have red color (color code 1)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test.dxf")
            
            generated_points = np.array([[5, 5, 101.5]])
            
            exporter = DXFExporter()
            exporter._export_generated_points(generated_points, LayerConfig.ADDED_POINTS)
            exporter.save(output_file)
            
            import ezdxf
            doc = ezdxf.readfile(output_file)
            
            red_entities = [e for e in doc.modelspace() 
                          if hasattr(e.dxf, 'color') and e.dxf.color == 1]
            assert len(red_entities) > 0
    
    def test_triangles_on_correct_layers(self, sample_points):
        """Test that triangles are placed on correct layers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test.dxf")
            
            builder = TINBuilder()
            tin = builder.build(sample_points)
            
            exporter = DXFExporter()
            exporter._export_tin_triangles(tin, LayerConfig.ORIGINAL_SURFACE)
            exporter.save(output_file)
            
            import ezdxf
            doc = ezdxf.readfile(output_file)
            
            entities_on_layer = [e for e in doc.modelspace() 
                                if e.dxf.layer == LayerConfig.ORIGINAL_SURFACE]
            assert len(entities_on_layer) > 0
    
    def test_full_export_layer_separation(self, sample_cloud_with_generated):
        """Test that full export properly separates original and generated data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test.dxf")
            
            builder = TINBuilder()
            original_points = sample_cloud_with_generated.get_points_by_type(PointType.ORIGINAL)
            all_points = sample_cloud_with_generated.points
            
            original_tin = builder.build(original_points)
            densified_tin = builder.build(all_points)
            
            exporter = DXFExporter()
            exporter.export_full_project(
                original_cloud=PointCloud(points=original_points, point_metadata=[]),
                original_tin=original_tin,
                densified_cloud=sample_cloud_with_generated,
                densified_tin=densified_tin,
                show_original=True,
                show_densified=True
            )
            exporter.save(output_file)
            
            import ezdxf
            doc = ezdxf.readfile(output_file)
            
            original_points_layer = [e for e in doc.modelspace() 
                                     if e.dxf.layer == LayerConfig.ORIGINAL_POINTS]
            added_points_layer = [e for e in doc.modelspace() 
                                 if e.dxf.layer == LayerConfig.ADDED_POINTS]
            
            assert len(original_points_layer) > 0
            assert len(added_points_layer) > 0
    
    def test_layer_visibility_toggles(self, sample_cloud_with_generated):
        """Test that layer visibility can be toggled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test_no_densified.dxf")
            
            builder = TINBuilder()
            original_points = sample_cloud_with_generated.get_points_by_type(PointType.ORIGINAL)
            original_tin = builder.build(original_points)
            
            exporter = DXFExporter()
            exporter.export_full_project(
                original_cloud=PointCloud(points=original_points, point_metadata=[]),
                original_tin=original_tin,
                densified_cloud=sample_cloud_with_generated,
                densified_tin=None,
                show_original=True,
                show_densified=False
            )
            exporter.save(output_file)
            
            import ezdxf
            doc = ezdxf.readfile(output_file)
            
            added_points_layer = [e for e in doc.modelspace() 
                                 if e.dxf.layer == LayerConfig.ADDED_POINTS]
            
            assert len(added_points_layer) == 0


class TestGeneratedPointsStyling:
    """Test suite for styling of generated points."""
    
    def test_generated_points_have_triangle_markers(self):
        """Test that generated points are marked with triangles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test.dxf")
            
            generated_points = np.array([[5, 5, 101.5]])
            
            exporter = DXFExporter()
            exporter._export_generated_points(generated_points, LayerConfig.ADDED_POINTS)
            exporter.save(output_file)
            
            import ezdxf
            doc = ezdxf.readfile(output_file)
            
            polylines = [e for e in doc.modelspace() 
                        if e.dxftype() == 'LWPOLYLINE']
            assert len(polylines) > 0
    
    def test_generated_points_have_text_labels(self):
        """Test that generated points have text annotations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test.dxf")
            
            generated_points = np.array([[5, 5, 101.5]])
            
            exporter = DXFExporter()
            exporter._export_generated_points(generated_points, LayerConfig.ADDED_POINTS)
            exporter.save(output_file)
            
            import ezdxf
            doc = ezdxf.readfile(output_file)
            
            texts = [e for e in doc.modelspace() 
                    if e.dxftype() == 'TEXT']
            assert len(texts) > 0
            
            text_values = [e.dxf.text for e in texts]
            assert any('101.5' in str(t) for t in text_values)
