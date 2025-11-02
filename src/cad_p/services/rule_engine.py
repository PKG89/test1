"""Rule engine service for processing survey points with codes and comments."""

from typing import List, Dict, Any, Optional
import re

from src.catalog.code_catalog import CodeCatalog
from src.models.point_data import SurveyPoint
from src.models.rule_data import (
    PlacementInstruction, RuleEngineResult, TextPlacement,
    BlockPlacement, RuleType, CommentHandling
)


class RuleEngine:
    """Engine for processing survey points according to catalog rules."""
    
    def __init__(self):
        """Initialize rule engine with code catalog."""
        self.catalog = CodeCatalog()
    
    def process_points(self, points: List[SurveyPoint]) -> RuleEngineResult:
        """
        Process survey points with codes and comments.
        
        Args:
            points: List of survey points with metadata
            
        Returns:
            RuleEngineResult with placement instructions
        """
        instructions = []
        statistics = {
            'total_points': len(points),
            'known_codes': 0,
            'unknown_codes': 0,
            'missing_data_fallbacks': 0,
            'special_behaviors': 0
        }
        warnings = []
        
        for point in points:
            code = point.metadata.get('code', 'unknown')
            comment = point.metadata.get('comment', '')
            number = point.metadata.get('number', None)
            
            instruction = self.process_single_point(point, code, comment, number)
            instructions.append(instruction)
            
            if instruction.is_unknown:
                statistics['unknown_codes'] += 1
            else:
                statistics['known_codes'] += 1
            
            if any('б/н' in label for label in instruction.labels):
                statistics['missing_data_fallbacks'] += 1
            
            if instruction.metadata.get('special_behavior'):
                statistics['special_behaviors'] += 1
        
        return RuleEngineResult(
            instructions=instructions,
            statistics=statistics,
            warnings=warnings
        )
    
    def process_single_point(self, 
                            point: SurveyPoint,
                            code: str,
                            comment: str = '',
                            number: Optional[int] = None) -> PlacementInstruction:
        """
        Process a single survey point.
        
        Args:
            point: Survey point
            code: Survey code
            comment: Optional comment
            number: Optional point number for label generation
            
        Returns:
            PlacementInstruction with all placement details
        """
        rule = self.catalog.get_rule(code)
        
        if rule is None:
            return self._handle_unknown_code(point, code, comment)
        
        return self._apply_rule(point, rule, comment, number)
    
    def _handle_unknown_code(self, 
                            point: SurveyPoint,
                            code: str,
                            comment: str) -> PlacementInstruction:
        """
        Handle unknown code with AutoCAD point and red bold text annotation.
        
        Creates point marker on VK layer with red bold text showing code, Z, and comment.
        """
        texts = []
        
        texts.append(TextPlacement(
            layer="VK",
            height=2.5,
            color=1,
            bold=True,
            offset_x=1.0,
            offset_y=1.0
        ))
        
        labels = [
            f"КОД: {code}",
            f"Z: {point.z:.3f}",
        ]
        if comment:
            labels.append(f"{comment}")
        
        return PlacementInstruction(
            code=code,
            canonical_code="unknown",
            x=point.x,
            y=point.y,
            z=point.z,
            block=None,
            texts=texts,
            point_marker={'layer': 'VK', 'color': 1, 'type': 'POINT'},
            labels=labels,
            comment=comment,
            metadata={'rule': 'unknown', 'style': 'red_bold'},
            is_unknown=True
        )
    
    def _apply_rule(self,
                   point: SurveyPoint,
                   rule,
                   comment: str,
                   number: Optional[int]) -> PlacementInstruction:
        """Apply catalog rule to generate placement instruction."""
        labels = []
        texts = []
        metadata = {
            'rule': rule.code,
            'rule_type': rule.rule_type.value,
            'canonical_name': rule.canonical_name
        }
        
        if rule.generate_label:
            label = self._generate_label(rule, number)
            labels.append(label)
        
        main_text = TextPlacement(
            layer=rule.text_layer,
            height=2.5,
            color=rule.color,
            offset_x=0.5,
            offset_y=0.5
        )
        texts.append(main_text)
        
        if comment and rule.comment_handling != CommentHandling.NO_COMMENT:
            comment_text = self._handle_comment(rule, comment)
            if comment_text:
                texts.append(comment_text)
        
        special_behavior = rule.special_behavior
        if special_behavior:
            metadata['special_behavior'] = special_behavior
            
            if special_behavior == 'three_labels':
                labels = self._generate_three_labels(rule, number)
            
            elif special_behavior == 'k_code_layer':
                pass
        
        return PlacementInstruction(
            code=rule.code,
            canonical_code=rule.canonical_name,
            x=point.x,
            y=point.y,
            z=point.z,
            block=rule.block,
            texts=texts,
            point_marker=None,
            labels=labels,
            comment=comment if rule.comment_handling != CommentHandling.NO_COMMENT else None,
            metadata=metadata,
            is_unknown=False
        )
    
    def _generate_label(self, rule, number: Optional[int]) -> str:
        """Generate label according to rule format."""
        if number is not None:
            return rule.label_format.format(number=number, code=rule.code)
        else:
            return rule.fallback_label
    
    def _generate_three_labels(self, rule, number: Optional[int]) -> List[str]:
        """Generate three labels for shurf special case."""
        base_label = self._generate_label(rule, number)
        return [base_label, base_label, base_label]
    
    def _handle_comment(self, rule, comment: str) -> Optional[TextPlacement]:
        """Handle comment text placement according to rule."""
        if rule.comment_handling == CommentHandling.NO_COMMENT:
            return None
        
        if rule.comment_handling == CommentHandling.BLOCK_LAYER:
            layer = rule.block.layer if rule.block else rule.text_layer
        else:
            layer = rule.comment_layer
        
        return TextPlacement(
            layer=layer,
            height=2.0,
            color=rule.color,
            offset_x=0.5,
            offset_y=-0.5
        )
    
    def extract_code_from_string(self, text: str) -> tuple[str, Optional[int]]:
        """
        Extract survey code and number from text string.
        
        Examples:
            "1" -> ("1", None)
            "vk25" -> ("vk", 25)
            "km+150" -> ("km+", 150)
            "shurf3" -> ("shurf", 3)
        
        Returns:
            Tuple of (code, number)
        """
        text = text.strip().lower()
        
        match = re.match(r'^([a-zа-я\-+]+?)(\d+)$', text)
        if match:
            return match.group(1), int(match.group(2))
        
        match = re.match(r'^(\d+)$', text)
        if match:
            return match.group(1), None
        
        return text, None
    
    def validate_instruction(self, instruction: PlacementInstruction) -> List[str]:
        """
        Validate placement instruction for completeness.
        
        Returns:
            List of validation warnings
        """
        warnings = []
        
        if instruction.is_unknown:
            warnings.append(f"Unknown code: {instruction.code}")
        
        if not instruction.labels and instruction.metadata.get('rule_type') == RuleType.NUMBER_RULE.value:
            warnings.append(f"Missing labels for number rule: {instruction.code}")
        
        if instruction.block and not instruction.block.block_name:
            warnings.append(f"Block placement missing block name for: {instruction.code}")
        
        return warnings
    
    def get_catalog_info(self) -> Dict[str, Any]:
        """Get information about the loaded catalog."""
        stats = self.catalog.get_catalog_statistics()
        return {
            'catalog_loaded': True,
            'statistics': stats,
            'available_codes': self.catalog.get_all_codes()[:10]
        }
