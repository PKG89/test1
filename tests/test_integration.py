"""Integration tests for end-to-end workflow."""

import pytest
import numpy as np
import tempfile
import os
from pathlib import Path

from src.services.processing_service import ProcessingService
from src.models.settings import ProjectSettings, DensificationSettings, InterpolationMethod
from src.processors.point_cloud import PointCloudProcessor


class TestIntegration:
    """Integration tests for complete workflow."""
    
    @pytest.fixture
    def sample_data_file(self):
        """Create a temporary sample data file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# Sample coordinates\n")
            f.write("X Y Z\n")
            for x in range(0, 50, 10):
                for y in range(0, 50, 10):
                    z = 100 + 0.1 * x + 0.05 * y
                    f.write(f"{x} {y} {z}\n")
            temp_file = f.name
        
        yield temp_file
        
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    def test_full_workflow_without_densification(self, sample_data_file):
        """Test complete workflow without densification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.dxf")
            
            settings = ProjectSettings(
                scale=1.0,
                densification=DensificationSettings(enabled=False)
            )
            
            service = ProcessingService()
            results = service.process_project(sample_data_file, output_file, settings)
            
            assert results['success'] is True
            assert 'points_loaded' in results
            assert results['points_loaded'] > 0
            assert 'original_triangles' in results
            assert os.path.exists(output_file)
    
    def test_full_workflow_with_densification(self, sample_data_file):
        """Test complete workflow with densification enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.dxf")
            
            settings = ProjectSettings(
                scale=1.0,
                densification=DensificationSettings(
                    enabled=True,
                    grid_spacing=5.0,
                    interpolation_method=InterpolationMethod.LINEAR,
                    show_generated_layer=True,
                    show_triangles_layer=True,
                    min_spacing_threshold=8.0
                )
            )
            
            service = ProcessingService()
            results = service.process_project(sample_data_file, output_file, settings)
            
            assert results['success'] is True
            assert 'points_loaded' in results
            assert 'densification' in results
            assert results['densification']['generated_points'] > 0
            assert os.path.exists(output_file)
    
    def test_workflow_with_high_density_grid(self, sample_data_file):
        """Test workflow with high density grid spacing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.dxf")
            
            settings = ProjectSettings(
                scale=1.0,
                densification=DensificationSettings(
                    enabled=True,
                    grid_spacing=3.0,
                    max_points=200
                )
            )
            
            service = ProcessingService()
            results = service.process_project(sample_data_file, output_file, settings)
            
            assert results['success'] is True
            if 'densification' in results:
                generated = results['densification']['generated_points']
                assert generated <= 200
    
    def test_workflow_with_cubic_interpolation(self, sample_data_file):
        """Test workflow with cubic interpolation method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.dxf")
            
            settings = ProjectSettings(
                scale=1.0,
                densification=DensificationSettings(
                    enabled=True,
                    grid_spacing=5.0,
                    interpolation_method=InterpolationMethod.CUBIC
                )
            )
            
            service = ProcessingService()
            results = service.process_project(sample_data_file, output_file, settings)
            
            assert results['success'] is True
    
    def test_dxf_contains_all_required_layers(self, sample_data_file):
        """Test that output DXF contains all required layers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.dxf")
            
            settings = ProjectSettings(
                scale=1.0,
                densification=DensificationSettings(
                    enabled=True,
                    grid_spacing=5.0
                )
            )
            
            service = ProcessingService()
            results = service.process_project(sample_data_file, output_file, settings)
            
            assert results['success'] is True
            
            import ezdxf
            doc = ezdxf.readfile(output_file)
            
            layer_names = [layer.dxf.name for layer in doc.layers]
            assert "2 отредактированная поверхность" in layer_names
            assert "2 пикеты добавленные" in layer_names
            assert "1 исходная поверхность" in layer_names
            assert "1 пикеты исходные" in layer_names
    
    def test_file_statistics(self, sample_data_file):
        """Test file statistics retrieval."""
        service = ProcessingService()
        stats = service.get_file_statistics(sample_data_file)
        
        assert stats['success'] is True
        assert 'point_count' in stats
        assert stats['point_count'] > 0
        assert 'bounds' in stats
        assert 'spacing' in stats
        assert 'mean_spacing' in stats['spacing']
    
    def test_error_handling_invalid_file(self):
        """Test error handling for invalid input file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.dxf")
            invalid_file = os.path.join(tmpdir, "nonexistent.txt")
            
            settings = ProjectSettings()
            service = ProcessingService()
            
            results = service.process_project(invalid_file, output_file, settings)
            
            assert results['success'] is False
            assert 'error' in results
    
    def test_workflow_message_generation(self, sample_data_file):
        """Test that workflow generates appropriate messages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.dxf")
            
            settings = ProjectSettings(
                scale=1.0,
                densification=DensificationSettings(
                    enabled=True,
                    grid_spacing=5.0
                )
            )
            
            service = ProcessingService()
            results = service.process_project(sample_data_file, output_file, settings)
            
            assert results['success'] is True
            
            from src.bot.conversation import DensificationConversation
            
            if 'densification' in results:
                message = DensificationConversation.get_processing_message(
                    results['densification']
                )
                assert 'Денсификация завершена' in message or 'пропущена' in message


class TestSampleDataProcessing:
    """Test processing of actual sample data files."""
    
    def test_process_example_file(self):
        """Test processing of example coordinate file."""
        example_file = Path(__file__).parent.parent / "examples" / "sample_coordinates.txt"
        
        if not example_file.exists():
            pytest.skip("Example file not found")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.dxf")
            
            settings = ProjectSettings(
                scale=1.0,
                densification=DensificationSettings(
                    enabled=True,
                    grid_spacing=3.0,
                    interpolation_method=InterpolationMethod.LINEAR
                )
            )
            
            service = ProcessingService()
            results = service.process_project(str(example_file), output_file, settings)
            
            assert results['success'] is True
            assert results['points_loaded'] > 0
            
            if 'densification' in results:
                assert results['densification']['generated_points'] >= 0
