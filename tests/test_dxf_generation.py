"""Tests for DXF generation service and geometry engine."""

import pytest
import tempfile
import os
from io import BytesIO
import ezdxf

from src.dxf.generation_service import DXFGenerationService
from src.dxf.scale_settings import DrawingScale, ScaleManager, ScaleParameters
from src.dxf.geometry_helpers import GeometryHelpers
from src.dxf.polyline_builder import Polyline3DBuilder, PointWithMetadata
from src.models.settings import DXFGenerationSettings


class TestScaleSettings:
    """Test scale management functionality."""
    
    def test_scale_parameters_1_500(self):
        """Test scale parameters for 1:500 scale."""
        params = ScaleParameters.from_scale(DrawingScale.SCALE_1_500)
        
        assert params.text_height == 1.8 * 0.5
        assert params.annotation_size == 1.0 * 0.5
        assert params.lineweight == int(25 * 0.5)
    
    def test_scale_parameters_1_1000(self):
        """Test scale parameters for 1:1000 scale."""
        params = ScaleParameters.from_scale(DrawingScale.SCALE_1_1000)
        
        assert params.text_height == 1.8
        assert params.annotation_size == 1.0
        assert params.lineweight == 25
    
    def test_scale_parameters_1_2000(self):
        """Test scale parameters for 1:2000 scale."""
        params = ScaleParameters.from_scale(DrawingScale.SCALE_1_2000)
        
        assert params.text_height == 1.8 * 2.0
        assert params.annotation_size == 1.0 * 2.0
        assert params.lineweight == int(25 * 2.0)
    
    def test_scale_parameters_1_5000(self):
        """Test scale parameters for 1:5000 scale."""
        params = ScaleParameters.from_scale(DrawingScale.SCALE_1_5000)
        
        assert params.text_height == 1.8 * 5.0
        assert params.annotation_size == 1.0 * 5.0
        assert params.lineweight == int(25 * 5.0)
    
    def test_scale_manager_text_height(self):
        """Test scale manager text height calculation."""
        manager = ScaleManager(DrawingScale.SCALE_1_1000)
        
        assert manager.get_text_height() == 1.8
        assert manager.get_text_height(2.0) == 1.8 * 2.0
    
    def test_scale_manager_dimension_scaling(self):
        """Test dimension scaling."""
        manager = ScaleManager(DrawingScale.SCALE_1_2000)
        
        scaled = manager.scale_dimension(10.0)
        assert scaled == 20.0


class TestGeometryHelpers:
    """Test geometry helper utilities."""
    
    @pytest.fixture
    def in_memory_doc(self):
        """Create an in-memory DXF document."""
        return ezdxf.new('R2018')
    
    @pytest.fixture
    def helpers(self, in_memory_doc):
        """Create geometry helpers instance."""
        return GeometryHelpers(in_memory_doc)
    
    def test_round_position(self, helpers):
        """Test position rounding."""
        rounded = helpers.round_position(1.23456, 2.34567, 3.45678, precision=3)
        
        assert rounded == (1.235, 2.346, 3.457)
    
    def test_place_point(self, helpers, in_memory_doc):
        """Test placing a point marker."""
        helpers.place_point(10.0, 20.0, 30.0, 'test_layer', color=1)
        
        msp = in_memory_doc.modelspace()
        circles = list(msp.query('CIRCLE'))
        
        assert len(circles) == 1
        assert circles[0].dxf.layer == 'test_layer'
        assert circles[0].dxf.color == 1
    
    def test_add_text_entity(self, helpers, in_memory_doc):
        """Test adding text entity."""
        helpers.add_text_entity(
            text="Test Text",
            insert_point=(10.0, 20.0),
            layer='text_layer',
            height=2.5,
            color=3
        )
        
        msp = in_memory_doc.modelspace()
        texts = list(msp.query('TEXT'))
        
        assert len(texts) == 1
        assert texts[0].dxf.layer == 'text_layer'
        assert texts[0].dxf.text == "Test Text"
        assert texts[0].dxf.height == 2.5
        assert texts[0].dxf.color == 3
    
    def test_add_z_label(self, helpers, in_memory_doc):
        """Test adding Z elevation label."""
        helpers.add_z_label(
            x=100.0, y=200.0, z=150.123,
            layer='elevation_layer',
            height=1.8,
            precision=2
        )
        
        msp = in_memory_doc.modelspace()
        texts = list(msp.query('TEXT'))
        
        assert len(texts) == 1
        assert texts[0].dxf.text == "150.12"
        assert texts[0].dxf.layer == 'elevation_layer'
    
    def test_create_3d_point(self, helpers, in_memory_doc):
        """Test creating 3D point entity."""
        helpers.create_3d_point(10.0, 20.0, 30.0, 'points_layer', color=5)
        
        msp = in_memory_doc.modelspace()
        points = list(msp.query('POINT'))
        
        assert len(points) == 1
        assert points[0].dxf.layer == 'points_layer'
        assert points[0].dxf.color == 5


class TestPolylineBuilder:
    """Test 3D polyline builder with grouping logic."""
    
    def test_group_by_code(self):
        """Test grouping points by code."""
        builder = Polyline3DBuilder()
        
        points = [
            PointWithMetadata(0, 0, 0, 'bord'),
            PointWithMetadata(10, 0, 0, 'bord'),
            PointWithMetadata(0, 10, 0, 'rels'),
            PointWithMetadata(10, 10, 0, 'rels'),
        ]
        
        grouped = builder.group_points(points)
        
        assert 'bord' in grouped
        assert 'rels' in grouped
        assert len(grouped['bord']) >= 1
        assert len(grouped['rels']) >= 1
    
    def test_group_by_code_and_comment(self):
        """Test grouping by code and first digit of comment."""
        builder = Polyline3DBuilder()
        
        points = [
            PointWithMetadata(0, 0, 0, 'bord', '1abc'),
            PointWithMetadata(10, 0, 0, 'bord', '1def'),
            PointWithMetadata(0, 10, 0, 'bord', '2abc'),
        ]
        
        grouped = builder.group_points(points)
        
        assert 'bord_1' in grouped
        assert 'bord_2' in grouped
    
    def test_break_distance_logic(self):
        """Test polyline breaking at >70m distance."""
        builder = Polyline3DBuilder(break_distance=70.0)
        
        points = [
            PointWithMetadata(0, 0, 0, 'bord'),
            PointWithMetadata(10, 0, 0, 'bord'),
            PointWithMetadata(100, 0, 0, 'bord'),  # >70m from previous
            PointWithMetadata(110, 0, 0, 'bord'),
        ]
        
        grouped = builder.group_points(points)
        
        segments = grouped['bord']
        assert len(segments) == 2  # Should be split into 2 segments
    
    def test_k_code_special_logic(self):
        """Test k-code special logic connects identical codes."""
        builder = Polyline3DBuilder()
        
        points = [
            PointWithMetadata(0, 0, 0, 'k1'),
            PointWithMetadata(10, 0, 0, 'k1'),
            PointWithMetadata(20, 0, 0, 'k1'),
        ]
        
        k_polylines = builder.apply_k_code_logic(points)
        
        assert 'k1' in k_polylines
        assert len(k_polylines['k1']) == 1
        assert len(k_polylines['k1'][0]) == 3
    
    def test_build_polylines_in_document(self):
        """Test building polylines in DXF document."""
        doc = ezdxf.new('R2018')
        builder = Polyline3DBuilder()
        
        points = [
            PointWithMetadata(0, 0, 0, 'bord'),
            PointWithMetadata(10, 0, 0, 'bord'),
            PointWithMetadata(20, 0, 0, 'bord'),
        ]
        
        polylines = builder.build_polylines_for_points(points, 'test_layer', doc)
        
        assert len(polylines) > 0
        
        msp = doc.modelspace()
        polylines_in_doc = list(msp.query('POLYLINE'))
        
        assert len(polylines_in_doc) > 0


class TestDXFGenerationService:
    """Test main DXF generation service."""
    
    def test_service_initialization(self):
        """Test service initialization without template."""
        service = DXFGenerationService()
        
        assert service.doc is not None
        assert service.scale_manager is not None
        assert service.geometry_helpers is not None
        assert service.polyline_builder is not None
    
    def test_service_with_scale(self):
        """Test service initialization with specific scale."""
        service = DXFGenerationService(scale=DrawingScale.SCALE_1_2000)
        
        assert service.scale_manager.scale == DrawingScale.SCALE_1_2000
        text_height = service.scale_manager.get_text_height()
        assert text_height == 1.8 * 2.0
    
    def test_ensure_layer_exists(self):
        """Test layer creation."""
        service = DXFGenerationService()
        
        service.ensure_layer_exists('test_layer', color=3, lineweight=50)
        
        assert 'test_layer' in service.doc.layers
        layer = service.doc.layers.get('test_layer')
        assert layer.color == 3
        assert layer.dxf.lineweight == 50
    
    def test_add_point_with_label(self):
        """Test adding point with Z label."""
        service = DXFGenerationService()
        
        service.add_point_with_label(
            x=100.0, y=200.0, z=150.5,
            code='bord', layer='points',
            show_z_label=True
        )
        
        msp = service.doc.modelspace()
        circles = list(msp.query('CIRCLE'))
        texts = list(msp.query('TEXT'))
        
        assert len(circles) > 0
        assert len(texts) > 0
        assert '150.500' in texts[0].dxf.text or '150.5' in texts[0].dxf.text
    
    def test_structural_layer_colors(self):
        """Test structural layer color assignments."""
        service = DXFGenerationService()
        
        assert service.STRUCTURAL_LAYERS['bord']['color'] == 0  # Black
        assert service.STRUCTURAL_LAYERS['rels']['color'] == 0  # Black
    
    def test_special_code_rules(self):
        """Test special code rules application."""
        service = DXFGenerationService()
        
        points_data = [
            {'x': 100.0, 'y': 200.0, 'z': 150.0, 'code': 'Fonar'},
        ]
        
        service.apply_special_code_rules(points_data, 'special_layer')
        
        msp = service.doc.modelspace()
        entities = list(msp)
        
        assert len(entities) > 0
    
    def test_build_3d_polylines_from_data(self):
        """Test building 3D polylines from point data."""
        service = DXFGenerationService()
        
        points_data = [
            {'x': 0.0, 'y': 0.0, 'z': 100.0, 'code': 'bord', 'comment': None},
            {'x': 10.0, 'y': 0.0, 'z': 100.5, 'code': 'bord', 'comment': None},
            {'x': 20.0, 'y': 0.0, 'z': 101.0, 'code': 'bord', 'comment': None},
        ]
        
        polylines = service.build_3d_polylines(points_data, 'polylines')
        
        assert len(polylines) > 0
    
    def test_save_to_file(self):
        """Test saving DXF to file."""
        service = DXFGenerationService()
        
        service.add_point_with_label(100, 200, 150, 'test', 'layer1')
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'test_output.dxf')
            service.save(output_file)
            
            assert os.path.exists(output_file)
            
            doc = ezdxf.readfile(output_file)
            assert doc is not None


class TestIntegrationWithSettings:
    """Test integration with settings models."""
    
    def test_dxf_generation_settings(self):
        """Test DXF generation settings."""
        settings = DXFGenerationSettings(
            enabled=True,
            drawing_scale='1:2000',
            generate_3d_polylines=True,
            polyline_break_distance=80.0
        )
        
        assert settings.drawing_scale == '1:2000'
        assert settings.polyline_break_distance == 80.0
    
    def test_settings_to_dict(self):
        """Test settings serialization."""
        settings = DXFGenerationSettings(drawing_scale='1:5000')
        
        data = settings.to_dict()
        
        assert data['drawing_scale'] == '1:5000'
        assert 'enabled' in data
        assert 'generate_3d_polylines' in data
    
    def test_settings_from_dict(self):
        """Test settings deserialization."""
        data = {
            'enabled': True,
            'drawing_scale': '1:1000',
            'polyline_break_distance': 75.0
        }
        
        settings = DXFGenerationSettings.from_dict(data)
        
        assert settings.enabled is True
        assert settings.drawing_scale == '1:1000'
        assert settings.polyline_break_distance == 75.0


class TestSmokeTestWithSampleData:
    """Smoke test with realistic sample dataset."""
    
    def test_complete_workflow(self):
        """Test complete workflow with sample data."""
        service = DXFGenerationService(scale=DrawingScale.SCALE_1_1000)
        
        points_data = [
            {'x': 1000.0, 'y': 2000.0, 'z': 150.250, 'code': 'bord', 'comment': '1'},
            {'x': 1005.0, 'y': 2000.0, 'z': 150.280, 'code': 'bord', 'comment': '1'},
            {'x': 1010.0, 'y': 2000.0, 'z': 150.310, 'code': 'bord', 'comment': '1'},
            {'x': 1000.0, 'y': 2005.0, 'z': 150.290, 'code': 'rels', 'comment': '2'},
            {'x': 1005.0, 'y': 2005.0, 'z': 150.320, 'code': 'rels', 'comment': '2'},
        ]
        
        for point in points_data:
            service.add_point_with_label(
                point['x'], point['y'], point['z'],
                point['code'], f"layer_{point['code']}",
                show_z_label=True
            )
        
        polylines = service.build_3d_polylines(points_data)
        
        msp = service.doc.modelspace()
        entities = list(msp)
        
        assert len(entities) > 0
        
        circles = list(msp.query('CIRCLE'))
        texts = list(msp.query('TEXT'))
        polylines_in_doc = list(msp.query('POLYLINE'))
        
        assert len(circles) == len(points_data)
        assert len(texts) == len(points_data)
        assert len(polylines_in_doc) > 0
    
    def test_scale_consistency_in_output(self):
        """Test that scale affects output entities consistently."""
        service_1000 = DXFGenerationService(scale=DrawingScale.SCALE_1_1000)
        service_2000 = DXFGenerationService(scale=DrawingScale.SCALE_1_2000)
        
        service_1000.add_point_with_label(100, 200, 150, 'test', 'layer1')
        service_2000.add_point_with_label(100, 200, 150, 'test', 'layer1')
        
        texts_1000 = list(service_1000.doc.modelspace().query('TEXT'))
        texts_2000 = list(service_2000.doc.modelspace().query('TEXT'))
        
        height_1000 = texts_1000[0].dxf.height
        height_2000 = texts_2000[0].dxf.height
        
        assert height_2000 == height_1000 * 2.0
    
    def test_save_complete_dxf(self):
        """Test saving complete DXF with all features."""
        service = DXFGenerationService(scale=DrawingScale.SCALE_1_1000)
        
        points_data = [
            {'x': 1000.0, 'y': 2000.0, 'z': 150.0, 'code': 'bord', 'comment': None},
            {'x': 1010.0, 'y': 2000.0, 'z': 150.5, 'code': 'bord', 'comment': None},
            {'x': 1020.0, 'y': 2000.0, 'z': 151.0, 'code': 'bord', 'comment': None},
        ]
        
        for point in points_data:
            service.add_point_with_label(
                point['x'], point['y'], point['z'],
                point['code'], 'survey_points'
            )
        
        service.build_3d_polylines(points_data)
        
        service.add_text_annotation('Test Annotation', 1000, 2010, 'annotations')
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'complete_output.dxf')
            service.save(output_file)
            
            assert os.path.exists(output_file)
            
            doc = ezdxf.readfile(output_file)
            msp = doc.modelspace()
            
            assert len(list(msp.query('CIRCLE'))) == 3
            assert len(list(msp.query('TEXT'))) >= 3
            assert len(list(msp.query('POLYLINE'))) > 0
