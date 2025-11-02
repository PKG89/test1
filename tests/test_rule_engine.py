"""Unit tests for rule engine service."""

import pytest
from src.services.rule_engine import RuleEngine
from src.models.point_data import SurveyPoint, PointType
from src.models.rule_data import RuleType, CommentHandling


class TestRuleEngine:
    """Test suite for rule engine."""
    
    @pytest.fixture
    def engine(self):
        """Create rule engine instance."""
        return RuleEngine()
    
    @pytest.fixture
    def sample_point(self):
        """Create sample survey point."""
        return SurveyPoint(
            x=100.0,
            y=200.0,
            z=150.5,
            metadata={'code': '1', 'number': 42}
        )
    
    def test_engine_initialization(self, engine):
        """Test rule engine initializes correctly."""
        info = engine.get_catalog_info()
        assert info['catalog_loaded'] is True
        assert info['statistics']['total_codes'] >= 60
    
    def test_process_single_known_code(self, engine, sample_point):
        """Test processing single point with known code."""
        instruction = engine.process_single_point(
            sample_point, code="1", comment="Test point", number=42
        )
        
        assert instruction.is_unknown is False
        assert instruction.code == "1"
        assert instruction.x == 100.0
        assert instruction.y == 200.0
        assert instruction.z == 150.5
        assert len(instruction.labels) > 0
        assert "N42" in instruction.labels[0]
    
    def test_process_unknown_code(self, engine, sample_point):
        """Test processing point with unknown code."""
        instruction = engine.process_single_point(
            sample_point, code="unknown_xyz", comment="Test"
        )
        
        assert instruction.is_unknown is True
        assert instruction.canonical_code == "unknown"
        assert instruction.point_marker is not None
        assert instruction.point_marker['layer'] == 'VK'
        assert instruction.point_marker['color'] == 1
        assert any('КОД:' in label for label in instruction.labels)
        assert any('Z:' in label for label in instruction.labels)
    
    def test_unknown_code_red_bold_text(self, engine, sample_point):
        """Test unknown code creates red bold text."""
        instruction = engine.process_single_point(
            sample_point, code="unknown_xyz", comment="Test comment"
        )
        
        assert len(instruction.texts) > 0
        text = instruction.texts[0]
        assert text.layer == "VK"
        assert text.color == 1
        assert text.bold is True
    
    def test_number_rule_with_number(self, engine, sample_point):
        """Test №-rule with number provided."""
        instruction = engine.process_single_point(
            sample_point, code="1", number=25
        )
        
        assert "N25" in instruction.labels[0]
        assert instruction.metadata['rule_type'] == RuleType.NUMBER_RULE.value
    
    def test_number_rule_without_number(self, engine, sample_point):
        """Test №-rule fallback when number missing."""
        instruction = engine.process_single_point(
            sample_point, code="1", number=None
        )
        
        assert "Nб/н" in instruction.labels[0]
    
    def test_km_rule_processing(self, engine, sample_point):
        """Test km-rule processing."""
        instruction = engine.process_single_point(
            sample_point, code="km", number=150
        )
        
        assert instruction.metadata['rule_type'] == RuleType.KM_RULE.value
        assert "км150" in instruction.labels[0]
    
    def test_vk_rule_processing(self, engine, sample_point):
        """Test VK-rule processing."""
        instruction = engine.process_single_point(
            sample_point, code="vk", number=10
        )
        
        assert instruction.metadata['rule_type'] == RuleType.VK_RULE.value
        assert "ВК10" in instruction.labels[0]
        assert instruction.block.layer == "VK"
        assert any(t.layer == "VK" for t in instruction.texts)
    
    def test_shurf_three_labels(self, engine, sample_point):
        """Test shurf generates three labels."""
        instruction = engine.process_single_point(
            sample_point, code="shurf", number=5
        )
        
        assert len(instruction.labels) == 3
        assert all("Ш5" in label for label in instruction.labels)
        assert instruction.metadata.get('special_behavior') == 'three_labels'
    
    def test_eskizRAZR_comment_in_block(self, engine, sample_point):
        """Test eskizRAZR places comment in block layer."""
        instruction = engine.process_single_point(
            sample_point, code="eskizRAZR", comment="Detailed description"
        )
        
        assert instruction.comment == "Detailed description"
        comment_texts = [t for t in instruction.texts if 'BLOCKS_ARCH' in t.layer]
        assert len(comment_texts) > 0
    
    def test_skulpt_comment_in_block(self, engine, sample_point):
        """Test skulpt places comment in block layer."""
        instruction = engine.process_single_point(
            sample_point, code="skulpt", comment="Statue description"
        )
        
        assert instruction.comment == "Statue description"
        comment_texts = [t for t in instruction.texts if 'BLOCKS_ARCH' in t.layer]
        assert len(comment_texts) > 0
    
    def test_k_code_custom_layers(self, engine, sample_point):
        """Test k-code uses custom layers."""
        instruction = engine.process_single_point(
            sample_point, code="k-kabel", number=12
        )
        
        assert instruction.block.layer == "K_KABEL"
        assert any("K_KABEL" in t.layer for t in instruction.texts)
        assert instruction.metadata.get('special_behavior') == 'k_code_layer'
    
    def test_comment_handling_separate(self, engine, sample_point):
        """Test comment handling with separate layer."""
        instruction = engine.process_single_point(
            sample_point, code="1", comment="Test comment"
        )
        
        assert instruction.comment == "Test comment"
        assert len(instruction.texts) >= 2
    
    def test_comment_handling_none(self, engine, sample_point):
        """Test no comment handling."""
        instruction = engine.process_single_point(
            sample_point, code="terrain", comment="Should be ignored"
        )
        
        assert instruction.comment is None
    
    def test_extract_code_from_string(self, engine):
        """Test code extraction from strings."""
        test_cases = [
            ("1", ("1", None)),
            ("vk25", ("vk", 25)),
            ("km+150", ("km+", 150)),
            ("shurf3", ("shurf", 3)),
            ("k-kabel42", ("k-kabel", 42)),
        ]
        
        for input_str, expected in test_cases:
            code, number = engine.extract_code_from_string(input_str)
            assert code == expected[0]
            assert number == expected[1]
    
    def test_process_multiple_points(self, engine):
        """Test processing multiple points."""
        points = [
            SurveyPoint(x=100, y=200, z=150, metadata={'code': '1', 'number': 1}),
            SurveyPoint(x=110, y=210, z=151, metadata={'code': 'vk', 'number': 10}),
            SurveyPoint(x=120, y=220, z=152, metadata={'code': 'unknown', 'number': 2}),
        ]
        
        result = engine.process_points(points)
        
        assert len(result.instructions) == 3
        assert result.statistics['total_points'] == 3
        assert result.statistics['known_codes'] == 2
        assert result.statistics['unknown_codes'] == 1
    
    def test_validate_instruction_known(self, engine, sample_point):
        """Test validation of valid instruction."""
        instruction = engine.process_single_point(
            sample_point, code="1", number=42
        )
        
        warnings = engine.validate_instruction(instruction)
        assert len([w for w in warnings if 'Unknown' in w]) == 0
    
    def test_validate_instruction_unknown(self, engine, sample_point):
        """Test validation catches unknown codes."""
        instruction = engine.process_single_point(
            sample_point, code="unknown_xyz"
        )
        
        warnings = engine.validate_instruction(instruction)
        assert any('Unknown' in w for w in warnings)
    
    def test_block_placement_structure(self, engine, sample_point):
        """Test block placement has correct structure."""
        instruction = engine.process_single_point(
            sample_point, code="zd", number=5
        )
        
        assert instruction.block is not None
        assert instruction.block.block_name == "ZDANIE"
        assert instruction.block.layer == "BLOCKS"
    
    def test_text_placement_structure(self, engine, sample_point):
        """Test text placement has correct structure."""
        instruction = engine.process_single_point(
            sample_point, code="1", number=1, comment="Test"
        )
        
        assert len(instruction.texts) >= 1
        for text in instruction.texts:
            assert text.layer is not None
            assert text.height > 0
    
    def test_label_generation_formats(self, engine, sample_point):
        """Test various label generation formats."""
        test_cases = [
            ("1", 1, "N1"),
            ("km", 100, "км100"),
            ("vk", 5, "ВК5"),
            ("der", 12, "Д12"),
            ("gr", 3, "Гр3"),
        ]
        
        for code, number, expected_label in test_cases:
            instruction = engine.process_single_point(
                sample_point, code=code, number=number
            )
            assert expected_label in instruction.labels[0]
    
    def test_fallback_labels(self, engine, sample_point):
        """Test fallback labels for missing data."""
        test_cases = [
            ("1", "Nб/н"),
            ("km", "кмб/н"),
            ("vk", "ВКб/н"),
            ("der", "Дб/н"),
        ]
        
        for code, expected_fallback in test_cases:
            instruction = engine.process_single_point(
                sample_point, code=code, number=None
            )
            assert expected_fallback in instruction.labels[0]
    
    def test_color_assignments(self, engine, sample_point):
        """Test color assignments are applied."""
        instruction = engine.process_single_point(
            sample_point, code="vk", number=1
        )
        
        assert any(t.color is not None for t in instruction.texts)
    
    def test_layer_assignments(self, engine, sample_point):
        """Test layer assignments for different code types."""
        test_cases = [
            ("vk", "VK"),
            ("k-kabel", "K_KABEL"),
            ("der", "TEXT_VEG"),
            ("shurf", "BLOCKS_ARCH"),
        ]
        
        for code, expected_layer_part in test_cases:
            instruction = engine.process_single_point(
                sample_point, code=code
            )
            
            has_layer = (
                (instruction.block and expected_layer_part in instruction.block.layer) or
                any(expected_layer_part in t.layer for t in instruction.texts)
            )
            assert has_layer


class TestRuleEngineStatistics:
    """Test rule engine statistics."""
    
    @pytest.fixture
    def engine(self):
        """Create rule engine instance."""
        return RuleEngine()
    
    def test_statistics_structure(self, engine):
        """Test statistics have correct structure."""
        points = [
            SurveyPoint(x=100, y=200, z=150, metadata={'code': '1', 'number': 1}),
        ]
        
        result = engine.process_points(points)
        
        assert 'total_points' in result.statistics
        assert 'known_codes' in result.statistics
        assert 'unknown_codes' in result.statistics
        assert 'missing_data_fallbacks' in result.statistics
        assert 'special_behaviors' in result.statistics
    
    def test_statistics_counts(self, engine):
        """Test statistics count correctly."""
        points = [
            SurveyPoint(x=100, y=200, z=150, metadata={'code': '1', 'number': None}),
            SurveyPoint(x=110, y=210, z=151, metadata={'code': 'shurf', 'number': 1}),
            SurveyPoint(x=120, y=220, z=152, metadata={'code': 'unknown_xyz'}),
        ]
        
        result = engine.process_points(points)
        
        assert result.statistics['total_points'] == 3
        assert result.statistics['known_codes'] == 2
        assert result.statistics['unknown_codes'] == 1
        assert result.statistics['missing_data_fallbacks'] >= 1
        assert result.statistics['special_behaviors'] >= 1


class TestRuleEngineIntegration:
    """Integration tests for rule engine with catalog."""
    
    @pytest.fixture
    def engine(self):
        """Create rule engine instance."""
        return RuleEngine()
    
    def test_all_catalog_codes_processable(self, engine):
        """Test all catalog codes can be processed."""
        sample_point = SurveyPoint(x=100, y=200, z=150)
        all_codes = engine.catalog.get_all_codes()
        
        for code in all_codes[:20]:
            instruction = engine.process_single_point(
                sample_point, code=code, number=1
            )
            assert instruction is not None
            assert instruction.is_unknown is False
    
    def test_representative_codes_coverage(self, engine):
        """Test representative codes across each rule type."""
        sample_point = SurveyPoint(x=100, y=200, z=150)
        
        test_codes = {
            RuleType.NUMBER_RULE: ["1", "2", "5"],
            RuleType.KM_RULE: ["km", "km+"],
            RuleType.VK_RULE: ["vk", "rp"],
            RuleType.STANDARD: ["shurf", "skulpt", "k-kabel"],
        }
        
        for rule_type, codes in test_codes.items():
            for code in codes:
                instruction = engine.process_single_point(
                    sample_point, code=code, number=1
                )
                assert instruction.metadata['rule_type'] == rule_type.value
    
    def test_edge_cases_handling(self, engine):
        """Test edge cases are handled properly."""
        sample_point = SurveyPoint(x=100, y=200, z=150)
        
        instruction = engine.process_single_point(
            sample_point, code="", number=None
        )
        assert instruction.is_unknown is True
        
        instruction = engine.process_single_point(
            sample_point, code="1", number=99999
        )
        assert "N99999" in instruction.labels[0]
