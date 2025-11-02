"""Integration tests for catalog workflow."""

import pytest
import tempfile
import os
from src.services.catalog_workflow import CatalogWorkflowService, DXFPayloadBuilder
from src.models.point_data import SurveyPoint, PointCloud
from src.models.rule_data import PlacementInstruction, TextPlacement, BlockPlacement


class TestCatalogWorkflowService:
    """Test suite for catalog workflow service."""
    
    @pytest.fixture
    def service(self):
        """Create workflow service instance."""
        return CatalogWorkflowService()
    
    @pytest.fixture
    def sample_file(self):
        """Create sample input file."""
        content = """# Sample survey data with codes and comments
100.0 200.0 150.5 1 First point
110.0 210.0 151.0 vk 25
120.0 220.0 152.5 km 100
130.0 230.0 153.0 shurf 3 Archaeological shurf
140.0 240.0 154.5 k-kabel 15 Cable line
150.0 250.0 155.0 unknown_code Unknown code test
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service.point_processor is not None
        assert service.rule_engine is not None
    
    def test_process_file_with_catalog(self, service, sample_file):
        """Test processing file with catalog."""
        result = service.process_file_with_catalog(sample_file)
        
        assert result['success'] is True
        assert result['points_loaded'] == 6
        assert 'instructions' in result
        assert 'statistics' in result
        assert 'placement_payload' in result
    
    def test_statistics_in_result(self, service, sample_file):
        """Test statistics are calculated correctly."""
        result = service.process_file_with_catalog(sample_file)
        
        stats = result['statistics']
        assert stats['total_points'] == 6
        assert stats['known_codes'] == 5
        assert stats['unknown_codes'] == 1
    
    def test_placement_instructions_generated(self, service, sample_file):
        """Test placement instructions are generated."""
        result = service.process_file_with_catalog(sample_file)
        
        instructions = result['instructions']
        assert len(instructions) == 6
        
        for instruction in instructions:
            assert hasattr(instruction, 'x')
            assert hasattr(instruction, 'y')
            assert hasattr(instruction, 'z')
            assert hasattr(instruction, 'code')
    
    def test_dxf_payload_structure(self, service, sample_file):
        """Test DXF payload has correct structure."""
        result = service.process_file_with_catalog(sample_file)
        
        payload = result['placement_payload']
        assert 'blocks' in payload
        assert 'texts' in payload
        assert 'points' in payload
        assert 'layers' in payload
    
    def test_unknown_code_handling(self, service, sample_file):
        """Test unknown code is handled properly."""
        result = service.process_file_with_catalog(sample_file)
        
        instructions = result['instructions']
        unknown_instructions = [i for i in instructions if i.is_unknown]
        
        assert len(unknown_instructions) == 1
        assert unknown_instructions[0].code == 'unknown_code'
        assert unknown_instructions[0].point_marker is not None
    
    def test_special_behavior_handling(self, service, sample_file):
        """Test special behaviors are triggered."""
        result = service.process_file_with_catalog(sample_file)
        
        stats = result['statistics']
        assert stats['special_behaviors'] >= 2
    
    def test_generate_summary(self, service, sample_file):
        """Test summary generation."""
        result = service.process_file_with_catalog(sample_file)
        instructions = result['instructions']
        
        from src.models.rule_data import RuleEngineResult
        rule_result = RuleEngineResult(
            instructions=instructions,
            statistics=result['statistics'],
            warnings=result['warnings']
        )
        
        summary = service.generate_summary(rule_result)
        
        assert "Processed 6 points" in summary
        assert "Known codes: 5" in summary
        assert "Unknown codes: 1" in summary
    
    def test_get_catalog_info(self, service):
        """Test getting catalog info."""
        info = service.get_catalog_info()
        
        assert info['catalog_loaded'] is True
        assert 'statistics' in info
        assert info['statistics']['total_codes'] >= 60
    
    def test_validate_file_format(self, service, sample_file):
        """Test file format validation."""
        result = service.validate_file_format(sample_file)
        
        assert result['valid'] is True
        assert len(result['preview']) > 0
        assert result['total_lines'] == 6
    
    def test_process_cloud_with_catalog(self, service):
        """Test processing point cloud directly."""
        points = [
            [100.0, 200.0, 150.0],
            [110.0, 210.0, 151.0],
        ]
        metadata = [
            {'code': '1', 'number': 1, 'comment': 'Point 1'},
            {'code': 'vk', 'number': 25, 'comment': 'Reference'},
        ]
        
        import numpy as np
        cloud = PointCloud(
            points=np.array(points),
            point_metadata=metadata
        )
        
        result = service.process_cloud_with_catalog(cloud)
        
        assert len(result.instructions) == 2
        assert result.statistics['total_points'] == 2


class TestDXFPayloadBuilder:
    """Test suite for DXF payload builder."""
    
    @pytest.fixture
    def sample_instructions(self):
        """Create sample placement instructions."""
        instructions = [
            PlacementInstruction(
                code="1",
                canonical_code="точка1",
                x=100.0,
                y=200.0,
                z=150.0,
                block=BlockPlacement(
                    block_name="TOCHKA",
                    layer="BLOCKS"
                ),
                texts=[
                    TextPlacement(
                        layer="TEXT",
                        height=2.5,
                        offset_x=0.5,
                        offset_y=0.5
                    )
                ],
                labels=["N1"],
                comment="Test point",
                metadata={'color': 7}
            ),
            PlacementInstruction(
                code="unknown",
                canonical_code="unknown",
                x=110.0,
                y=210.0,
                z=151.0,
                point_marker={'layer': 'VK', 'color': 1, 'type': 'POINT'},
                texts=[
                    TextPlacement(
                        layer="VK",
                        height=2.5,
                        color=1,
                        bold=True
                    )
                ],
                labels=["КОД: unknown"],
                is_unknown=True
            )
        ]
        return instructions
    
    def test_build_payload(self, sample_instructions):
        """Test building DXF payload."""
        payload = DXFPayloadBuilder.build(sample_instructions)
        
        assert 'entities' in payload
        assert 'layers' in payload
        assert 'blocks' in payload
        assert 'text_styles' in payload
    
    def test_entities_created(self, sample_instructions):
        """Test entities are created for instructions."""
        payload = DXFPayloadBuilder.build(sample_instructions)
        
        entities = payload['entities']
        assert len(entities) >= 3
        
        entity_types = [e['type'] for e in entities]
        assert 'BLOCK_INSERT' in entity_types
        assert 'TEXT' in entity_types
        assert 'POINT' in entity_types
    
    def test_layers_collected(self, sample_instructions):
        """Test layers are collected from instructions."""
        payload = DXFPayloadBuilder.build(sample_instructions)
        
        layers = payload['layers']
        assert 'BLOCKS' in layers
        assert 'TEXT' in layers
        assert 'VK' in layers
    
    def test_block_entity_structure(self, sample_instructions):
        """Test block entity has correct structure."""
        payload = DXFPayloadBuilder.build(sample_instructions)
        
        block_entities = [e for e in payload['entities'] if e['type'] == 'BLOCK_INSERT']
        assert len(block_entities) > 0
        
        block = block_entities[0]
        assert 'block_name' in block
        assert 'layer' in block
        assert 'location' in block
        assert len(block['location']) == 3
    
    def test_text_entity_structure(self, sample_instructions):
        """Test text entity has correct structure."""
        payload = DXFPayloadBuilder.build(sample_instructions)
        
        text_entities = [e for e in payload['entities'] if e['type'] == 'TEXT']
        assert len(text_entities) > 0
        
        text = text_entities[0]
        assert 'text' in text
        assert 'layer' in text
        assert 'location' in text
        assert 'height' in text
    
    def test_point_entity_structure(self, sample_instructions):
        """Test point entity has correct structure."""
        payload = DXFPayloadBuilder.build(sample_instructions)
        
        point_entities = [e for e in payload['entities'] if e['type'] == 'POINT']
        assert len(point_entities) > 0
        
        point = point_entities[0]
        assert 'layer' in point
        assert 'location' in point
        assert 'color' in point


class TestWorkflowIntegration:
    """Integration tests for complete workflow."""
    
    @pytest.fixture
    def service(self):
        """Create workflow service."""
        return CatalogWorkflowService()
    
    @pytest.fixture
    def diverse_codes_file(self):
        """Create file with diverse codes."""
        content = """# Diverse survey codes
100 200 150 1 Numbered point
110 210 151 2
120 220 152 5
130 230 153 vk 10 Reference point
140 240 154 km 100 Kilometer marker
150 250 155 shurf 3 Shurf excavation
160 260 156 skulpt Sculpture
170 270 157 eskizRAZR Destruction sketch
180 280 158 k-kabel 25 Cable
190 290 159 k-tep 30 Heat line
200 300 160 zd 5 Building
210 310 161 der 12 Tree
220 320 162 ur-vod 8 Water edge
230 330 163 gr 15 Boundary
240 340 164 trig 100 Triangulation
250 350 165 unknown1 Unknown code 1
260 360 166 unknown2 Unknown code 2
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_diverse_codes_processing(self, service, diverse_codes_file):
        """Test processing file with diverse codes."""
        result = service.process_file_with_catalog(diverse_codes_file)
        
        assert result['success'] is True
        assert result['points_loaded'] == 17
    
    def test_all_rule_types_covered(self, service, diverse_codes_file):
        """Test all rule types are represented."""
        result = service.process_file_with_catalog(diverse_codes_file)
        
        instructions = result['instructions']
        rule_types = set(i.metadata.get('rule_type') for i in instructions if not i.is_unknown)
        
        assert 'standard' in rule_types or len(rule_types) >= 2
    
    def test_special_cases_handled(self, service, diverse_codes_file):
        """Test special cases are handled."""
        result = service.process_file_with_catalog(diverse_codes_file)
        
        instructions = result['instructions']
        
        shurf_instructions = [i for i in instructions if i.code == 'shurf']
        if shurf_instructions:
            assert len(shurf_instructions[0].labels) == 3
        
        k_instructions = [i for i in instructions if i.code.startswith('k-')]
        assert len(k_instructions) >= 2
    
    def test_edge_cases_handling(self, service):
        """Test edge cases."""
        content = """100 200 150
110 210 151 1
120 220 152 vk
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = service.process_file_with_catalog(temp_path)
            assert result['success'] is True
        finally:
            os.unlink(temp_path)
    
    def test_empty_file_handling(self, service):
        """Test empty file handling."""
        content = """# Empty file with only comments
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            result = service.process_file_with_catalog(temp_path)
            assert result['success'] is False
        finally:
            os.unlink(temp_path)
