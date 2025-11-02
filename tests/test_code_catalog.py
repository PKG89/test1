"""Unit tests for code catalog."""

import pytest
from src.catalog.code_catalog import CodeCatalog
from src.models.rule_data import RuleType, CommentHandling


class TestCodeCatalog:
    """Test suite for code catalog."""
    
    @pytest.fixture
    def catalog(self):
        """Create catalog instance."""
        return CodeCatalog()
    
    def test_catalog_initialization(self, catalog):
        """Test that catalog initializes with codes."""
        stats = catalog.get_catalog_statistics()
        assert stats['total_codes'] >= 60
        assert stats['total_aliases'] > 0
    
    def test_get_known_code(self, catalog):
        """Test retrieving known code."""
        rule = catalog.get_rule("1")
        assert rule is not None
        assert rule.code == "1"
        assert rule.canonical_name == "точка1"
    
    def test_get_code_by_alias(self, catalog):
        """Test retrieving code by alias."""
        rule = catalog.get_rule("т1")
        assert rule is not None
        assert rule.code == "1"
    
    def test_get_unknown_code(self, catalog):
        """Test that unknown code returns None."""
        rule = catalog.get_rule("unknown_xyz_123")
        assert rule is None
    
    def test_case_insensitive_lookup(self, catalog):
        """Test case-insensitive code lookup."""
        rule1 = catalog.get_rule("VK")
        rule2 = catalog.get_rule("vk")
        rule3 = catalog.get_rule("Vk")
        
        assert rule1 is not None
        assert rule1.code == rule2.code == rule3.code
    
    def test_number_rule_codes(self, catalog):
        """Test №-rule codes (numbered points)."""
        codes = catalog.get_codes_by_rule_type(RuleType.NUMBER_RULE)
        assert len(codes) >= 10
        assert "1" in codes
        assert "2" in codes
        assert "5" in codes
        
        rule = catalog.get_rule("1")
        assert rule.rule_type == RuleType.NUMBER_RULE
        assert rule.generate_label is True
        assert "{number}" in rule.label_format
    
    def test_km_rule_codes(self, catalog):
        """Test km-rule codes (kilometer markers)."""
        codes = catalog.get_codes_by_rule_type(RuleType.KM_RULE)
        assert len(codes) >= 2
        
        rule = catalog.get_rule("km")
        assert rule is not None
        assert rule.rule_type == RuleType.KM_RULE
        assert "км" in rule.label_format
    
    def test_vk_rule_codes(self, catalog):
        """Test VK-rule codes (reference points)."""
        codes = catalog.get_codes_by_rule_type(RuleType.VK_RULE)
        assert len(codes) >= 2
        
        rule = catalog.get_rule("vk")
        assert rule is not None
        assert rule.rule_type == RuleType.VK_RULE
        assert rule.block.layer == "VK"
        assert rule.text_layer == "VK"
    
    def test_shurf_special_behavior(self, catalog):
        """Test shurf with three labels special case."""
        rule = catalog.get_rule("shurf")
        assert rule is not None
        assert rule.special_behavior == "three_labels"
        assert rule.comment_handling == CommentHandling.SPECIAL
        assert rule.metadata.get('label_count') == 3
    
    def test_eskizRAZR_comment_handling(self, catalog):
        """Test eskizRAZR with comment in block layer."""
        rule = catalog.get_rule("eskizRAZR")
        assert rule is not None
        assert rule.comment_handling == CommentHandling.BLOCK_LAYER
        assert rule.text_layer == "BLOCKS_ARCH"
        assert rule.comment_layer == "BLOCKS_ARCH"
    
    def test_skulpt_comment_handling(self, catalog):
        """Test skulpt with comment in block layer."""
        rule = catalog.get_rule("skulpt")
        assert rule is not None
        assert rule.comment_handling == CommentHandling.BLOCK_LAYER
        assert rule.text_layer == "BLOCKS_ARCH"
        assert rule.comment_layer == "BLOCKS_ARCH"
    
    def test_k_code_custom_layers(self, catalog):
        """Test k-code custom layers and text placements."""
        k_codes = ["k-kabel", "k-tep", "k-voda", "k-kanal", "k-gaz"]
        
        for code in k_codes:
            rule = catalog.get_rule(code)
            assert rule is not None
            assert rule.special_behavior == "k_code_layer"
            assert rule.block.layer.startswith("K_")
            assert rule.text_layer.startswith("K_")
    
    def test_k_kabel_specific(self, catalog):
        """Test k-kabel specific configuration."""
        rule = catalog.get_rule("k-kabel")
        assert rule is not None
        assert rule.block.layer == "K_KABEL"
        assert rule.text_layer == "K_KABEL_TEXT"
        assert rule.color == 4
    
    def test_fallback_labels(self, catalog):
        """Test fallback labels for missing data."""
        rule = catalog.get_rule("1")
        assert rule.fallback_label == "Nб/н"
        
        rule = catalog.get_rule("km")
        assert "б/н" in rule.fallback_label
    
    def test_block_configurations(self, catalog):
        """Test block placement configurations."""
        rule = catalog.get_rule("zd")
        assert rule is not None
        assert rule.block is not None
        assert rule.block.block_name == "ZDANIE"
        assert rule.block.layer == "BLOCKS"
    
    def test_vegetation_codes(self, catalog):
        """Test vegetation codes."""
        veg_codes = ["der", "kust", "les", "sad"]
        
        for code in veg_codes:
            rule = catalog.get_rule(code)
            assert rule is not None
            assert "VEG" in rule.block.layer or "VEG" in rule.text_layer
    
    def test_infrastructure_codes(self, catalog):
        """Test infrastructure codes."""
        infra_codes = ["stolb", "osvesh", "luk"]
        
        for code in infra_codes:
            rule = catalog.get_rule(code)
            assert rule is not None
            assert rule.generate_label is True
    
    def test_water_feature_codes(self, catalog):
        """Test water feature codes."""
        rule = catalog.get_rule("ur-vod")
        assert rule is not None
        assert "HYDRO" in rule.block.layer or "HYDRO" in rule.text_layer
        
        rule = catalog.get_rule("kolod")
        assert rule is not None
        assert rule.generate_label is True
    
    def test_boundary_codes(self, catalog):
        """Test boundary marker codes."""
        rule = catalog.get_rule("gr")
        assert rule is not None
        assert rule.canonical_name == "граница"
        assert rule.generate_label is True
    
    def test_archaeological_codes(self, catalog):
        """Test archaeological codes."""
        arch_codes = ["shurf", "skulpt", "eskizRAZR", "raskop", "nahodka"]
        
        for code in arch_codes:
            rule = catalog.get_rule(code)
            assert rule is not None
            assert "ARCH" in rule.block.layer
    
    def test_special_technical_codes(self, catalog):
        """Test special technical codes."""
        rule = catalog.get_rule("trig")
        assert rule is not None
        assert rule.rule_type == RuleType.VK_RULE
        
        rule = catalog.get_rule("poly")
        assert rule is not None
        assert rule.rule_type == RuleType.VK_RULE
    
    def test_terrain_codes(self, catalog):
        """Test terrain feature codes."""
        terrain_codes = ["bpl", "cpl", "bord", "terrain"]
        
        for code in terrain_codes:
            rule = catalog.get_rule(code)
            assert rule is not None
    
    def test_color_assignments(self, catalog):
        """Test that color assignments are valid."""
        all_codes = catalog.get_all_codes()
        
        for code in all_codes[:20]:
            rule = catalog.get_rule(code)
            assert rule.color >= 1
            assert rule.color <= 9
    
    def test_layer_definitions(self, catalog):
        """Test layer definitions are consistent."""
        rule = catalog.get_rule("1")
        assert rule.text_layer is not None
        assert rule.comment_layer is not None
        assert rule.point_layer is not None
    
    def test_is_known_code(self, catalog):
        """Test is_known_code method."""
        assert catalog.is_known_code("1") is True
        assert catalog.is_known_code("vk") is True
        assert catalog.is_known_code("т1") is True
        assert catalog.is_known_code("unknown_xyz") is False
    
    def test_catalog_coverage(self, catalog):
        """Test catalog has 60+ codes."""
        all_codes = catalog.get_all_codes()
        assert len(all_codes) >= 60
    
    def test_aliases_work(self, catalog):
        """Test various aliases work correctly."""
        test_cases = [
            ("т1", "1"),
            ("VK", "vk"),
            ("КМ", "km"),
            ("DER", "der"),
        ]
        
        for alias, expected_code in test_cases:
            rule = catalog.get_rule(alias)
            assert rule is not None
            assert rule.code == expected_code


class TestCodeCatalogStatistics:
    """Test catalog statistics."""
    
    @pytest.fixture
    def catalog(self):
        """Create catalog instance."""
        return CodeCatalog()
    
    def test_statistics_structure(self, catalog):
        """Test statistics return structure."""
        stats = catalog.get_catalog_statistics()
        
        assert 'total_codes' in stats
        assert 'total_aliases' in stats
        assert 'number_rules' in stats
        assert 'km_rules' in stats
        assert 'vk_rules' in stats
        assert 'standard_rules' in stats
    
    def test_statistics_values(self, catalog):
        """Test statistics have reasonable values."""
        stats = catalog.get_catalog_statistics()
        
        assert stats['total_codes'] >= 60
        assert stats['number_rules'] >= 10
        assert stats['km_rules'] >= 2
        assert stats['vk_rules'] >= 2
        assert stats['standard_rules'] > 0
    
    def test_rule_type_coverage(self, catalog):
        """Test all rule types are represented."""
        number_codes = catalog.get_codes_by_rule_type(RuleType.NUMBER_RULE)
        km_codes = catalog.get_codes_by_rule_type(RuleType.KM_RULE)
        vk_codes = catalog.get_codes_by_rule_type(RuleType.VK_RULE)
        standard_codes = catalog.get_codes_by_rule_type(RuleType.STANDARD)
        
        assert len(number_codes) > 0
        assert len(km_codes) > 0
        assert len(vk_codes) > 0
        assert len(standard_codes) > 0
