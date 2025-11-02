"""Catalog workflow service integrating rule engine with processing pipeline."""

from typing import Dict, Any, List
from pathlib import Path

from src.processors.point_cloud import PointCloudProcessor
from src.services.rule_engine import RuleEngine
from src.models.point_data import SurveyPoint, PointCloud
from src.models.rule_data import RuleEngineResult, PlacementInstruction


class CatalogWorkflowService:
    """Service integrating code catalog and rule engine with workflow."""
    
    def __init__(self):
        """Initialize catalog workflow service."""
        self.point_processor = PointCloudProcessor()
        self.rule_engine = RuleEngine()
    
    def process_file_with_catalog(self, filepath: str) -> Dict[str, Any]:
        """
        Process survey file with code catalog and rule engine.
        
        Args:
            filepath: Path to input file with format: X Y Z [CODE] [COMMENT]
            
        Returns:
            Dictionary with processing results and placement instructions
        """
        results = {
            'success': False,
            'filepath': filepath
        }
        
        try:
            cloud = self.point_processor.load_from_file(filepath, parse_codes=True)
            results['points_loaded'] = cloud.count
            
            survey_points = self._cloud_to_survey_points(cloud)
            
            rule_result = self.rule_engine.process_points(survey_points)
            
            results['success'] = True
            results['instructions'] = rule_result.instructions
            results['statistics'] = rule_result.statistics
            results['warnings'] = rule_result.warnings
            results['placement_payload'] = self._create_dxf_payload(rule_result)
            
        except Exception as e:
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def process_cloud_with_catalog(self, cloud: PointCloud) -> RuleEngineResult:
        """
        Process point cloud with code catalog.
        
        Args:
            cloud: Point cloud with metadata containing codes and comments
            
        Returns:
            RuleEngineResult with placement instructions
        """
        survey_points = self._cloud_to_survey_points(cloud)
        return self.rule_engine.process_points(survey_points)
    
    def _cloud_to_survey_points(self, cloud: PointCloud) -> List[SurveyPoint]:
        """Convert point cloud to survey points with metadata."""
        survey_points = []
        
        for i in range(cloud.count):
            point_data = cloud.points[i]
            metadata = cloud.point_metadata[i] if i < len(cloud.point_metadata) else {}
            
            survey_point = SurveyPoint(
                x=float(point_data[0]),
                y=float(point_data[1]),
                z=float(point_data[2]),
                metadata=metadata
            )
            survey_points.append(survey_point)
        
        return survey_points
    
    def _create_dxf_payload(self, rule_result: RuleEngineResult) -> Dict[str, Any]:
        """
        Create structured payload for DXF generation service.
        
        Args:
            rule_result: Result from rule engine
            
        Returns:
            Structured payload ready for DXF generation
        """
        payload = {
            'blocks': [],
            'texts': [],
            'points': [],
            'layers': set(),
            'statistics': rule_result.statistics
        }
        
        for instruction in rule_result.instructions:
            if instruction.block:
                payload['blocks'].append({
                    'name': instruction.block.block_name,
                    'layer': instruction.block.layer,
                    'x': instruction.x,
                    'y': instruction.y,
                    'z': instruction.z,
                    'scale': instruction.block.scale,
                    'rotation': instruction.block.rotation,
                    'attributes': instruction.block.attributes
                })
                payload['layers'].add(instruction.block.layer)
            
            for i, text_placement in enumerate(instruction.texts):
                label_text = instruction.labels[i] if i < len(instruction.labels) else ""
                if instruction.comment and i == len(instruction.texts) - 1:
                    label_text = instruction.comment
                
                payload['texts'].append({
                    'text': label_text,
                    'layer': text_placement.layer,
                    'x': instruction.x + text_placement.offset_x,
                    'y': instruction.y + text_placement.offset_y,
                    'z': instruction.z,
                    'height': text_placement.height,
                    'color': text_placement.color,
                    'bold': text_placement.bold,
                    'rotation': text_placement.rotation,
                    'style': text_placement.style
                })
                payload['layers'].add(text_placement.layer)
            
            if instruction.point_marker:
                payload['points'].append({
                    'x': instruction.x,
                    'y': instruction.y,
                    'z': instruction.z,
                    'layer': instruction.point_marker['layer'],
                    'color': instruction.point_marker['color'],
                    'type': instruction.point_marker.get('type', 'POINT')
                })
                payload['layers'].add(instruction.point_marker['layer'])
        
        payload['layers'] = list(payload['layers'])
        
        return payload
    
    def generate_summary(self, rule_result: RuleEngineResult) -> str:
        """
        Generate human-readable summary of processing results.
        
        Args:
            rule_result: Result from rule engine
            
        Returns:
            Summary string
        """
        stats = rule_result.statistics
        
        summary_lines = [
            f"Processed {stats['total_points']} points",
            f"Known codes: {stats['known_codes']}",
            f"Unknown codes: {stats['unknown_codes']}",
            f"Missing data fallbacks: {stats['missing_data_fallbacks']}",
            f"Special behaviors: {stats['special_behaviors']}"
        ]
        
        if rule_result.warnings:
            summary_lines.append(f"\nWarnings ({len(rule_result.warnings)}):")
            for warning in rule_result.warnings[:5]:
                summary_lines.append(f"  - {warning}")
        
        return "\n".join(summary_lines)
    
    def get_catalog_info(self) -> Dict[str, Any]:
        """Get information about loaded catalog."""
        return self.rule_engine.get_catalog_info()
    
    def validate_file_format(self, filepath: str) -> Dict[str, Any]:
        """
        Validate file format and preview codes.
        
        Args:
            filepath: Path to input file
            
        Returns:
            Validation results
        """
        results = {
            'valid': False,
            'preview': []
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            preview_data = []
            for line in lines[:10]:
                parts = line.split()
                if len(parts) >= 3:
                    preview_item = {
                        'x': parts[0],
                        'y': parts[1],
                        'z': parts[2],
                        'code': parts[3] if len(parts) >= 4 else None,
                        'comment': ' '.join(parts[4:]) if len(parts) >= 5 else None
                    }
                    preview_data.append(preview_item)
            
            results['valid'] = True
            results['preview'] = preview_data
            results['total_lines'] = len(lines)
            
        except Exception as e:
            results['error'] = str(e)
        
        return results


class DXFPayloadBuilder:
    """Builder for creating DXF-ready payloads from placement instructions."""
    
    @staticmethod
    def build(instructions: List[PlacementInstruction]) -> Dict[str, Any]:
        """
        Build DXF payload from placement instructions.
        
        Args:
            instructions: List of placement instructions
            
        Returns:
            DXF-ready payload dictionary
        """
        payload = {
            'entities': [],
            'layers': {},
            'blocks': {},
            'text_styles': {}
        }
        
        for instruction in instructions:
            if instruction.block:
                entity = {
                    'type': 'BLOCK_INSERT',
                    'block_name': instruction.block.block_name,
                    'layer': instruction.block.layer,
                    'location': (instruction.x, instruction.y, instruction.z),
                    'scale': instruction.block.scale,
                    'rotation': instruction.block.rotation,
                    'attributes': instruction.block.attributes
                }
                payload['entities'].append(entity)
                
                payload['layers'][instruction.block.layer] = {
                    'color': instruction.metadata.get('color', 7)
                }
            
            for i, text in enumerate(instruction.texts):
                text_content = ""
                if i < len(instruction.labels):
                    text_content = instruction.labels[i]
                elif instruction.comment:
                    text_content = instruction.comment
                
                entity = {
                    'type': 'TEXT',
                    'layer': text.layer,
                    'location': (
                        instruction.x + text.offset_x,
                        instruction.y + text.offset_y,
                        instruction.z
                    ),
                    'text': text_content,
                    'height': text.height,
                    'rotation': text.rotation,
                    'style': text.style,
                    'color': text.color,
                    'bold': text.bold
                }
                payload['entities'].append(entity)
                
                if text.layer not in payload['layers']:
                    payload['layers'][text.layer] = {
                        'color': text.color if text.color else 7
                    }
            
            if instruction.point_marker:
                entity = {
                    'type': 'POINT',
                    'layer': instruction.point_marker['layer'],
                    'location': (instruction.x, instruction.y, instruction.z),
                    'color': instruction.point_marker['color']
                }
                payload['entities'].append(entity)
                
                payload['layers'][instruction.point_marker['layer']] = {
                    'color': instruction.point_marker['color']
                }
        
        return payload
