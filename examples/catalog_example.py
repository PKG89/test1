"""Example demonstrating the code catalog and rule engine feature."""

from src.services.catalog_workflow import CatalogWorkflowService
from src.services.rule_engine import RuleEngine
from src.models.point_data import SurveyPoint


def example_basic_usage():
    """Basic usage example."""
    print("=== Basic Usage Example ===\n")
    
    service = CatalogWorkflowService()
    
    catalog_info = service.get_catalog_info()
    print(f"Catalog loaded: {catalog_info['catalog_loaded']}")
    print(f"Total codes: {catalog_info['statistics']['total_codes']}")
    print(f"Sample codes: {', '.join(catalog_info['available_codes'])}\n")


def example_process_single_point():
    """Process a single survey point."""
    print("=== Single Point Processing ===\n")
    
    engine = RuleEngine()
    
    point = SurveyPoint(
        x=100.0,
        y=200.0,
        z=150.5,
        metadata={'code': 'vk', 'number': 25, 'comment': 'Reference point'}
    )
    
    instruction = engine.process_single_point(
        point, 
        code='vk', 
        number=25, 
        comment='Reference point'
    )
    
    print(f"Code: {instruction.code}")
    print(f"Canonical name: {instruction.canonical_code}")
    print(f"Block: {instruction.block.block_name if instruction.block else 'None'}")
    print(f"Labels: {instruction.labels}")
    print(f"Layers: {[t.layer for t in instruction.texts]}")
    print(f"Comment: {instruction.comment}\n")


def example_multiple_codes():
    """Process multiple points with different codes."""
    print("=== Multiple Codes Example ===\n")
    
    engine = RuleEngine()
    
    test_cases = [
        ('1', 42, 'Standard point'),
        ('km', 100, 'Kilometer marker'),
        ('shurf', 3, 'Archaeological shurf'),
        ('k-kabel', 15, 'Cable line'),
        ('der', 8, 'Tree'),
    ]
    
    for code, number, comment in test_cases:
        point = SurveyPoint(x=100, y=200, z=150)
        instruction = engine.process_single_point(point, code, comment, number)
        
        print(f"{code:10} -> {instruction.labels[0]:15} "
              f"Layer: {instruction.texts[0].layer if instruction.texts else 'N/A':20} "
              f"Special: {instruction.metadata.get('special_behavior', '-')}")
    
    print()


def example_unknown_code():
    """Handle unknown code."""
    print("=== Unknown Code Handling ===\n")
    
    engine = RuleEngine()
    
    point = SurveyPoint(x=100, y=200, z=150.5)
    instruction = engine.process_single_point(
        point, 
        code='UNKNOWN_XYZ', 
        comment='This is an unknown code'
    )
    
    print(f"Is unknown: {instruction.is_unknown}")
    print(f"Point marker: {instruction.point_marker}")
    print(f"Labels:")
    for label in instruction.labels:
        print(f"  - {label}")
    print(f"Text properties: bold={instruction.texts[0].bold}, "
          f"color={instruction.texts[0].color}\n")


def example_special_cases():
    """Demonstrate special case handling."""
    print("=== Special Cases ===\n")
    
    engine = RuleEngine()
    point = SurveyPoint(x=100, y=200, z=150)
    
    shurf_inst = engine.process_single_point(point, 'shurf', 'Excavation', 5)
    print(f"Shurf (three labels): {shurf_inst.labels}")
    
    k_inst = engine.process_single_point(point, 'k-kabel', 'Cable', 25)
    print(f"k-kabel custom layer: {k_inst.block.layer}")
    
    eskiz_inst = engine.process_single_point(point, 'eskizRAZR', 'Destruction')
    print(f"eskizRAZR comment layer: {eskiz_inst.texts[0].layer}")
    print()


def example_statistics():
    """Show statistics from processing."""
    print("=== Statistics Example ===\n")
    
    engine = RuleEngine()
    
    points = [
        SurveyPoint(x=100, y=200, z=150, metadata={'code': '1', 'number': 1}),
        SurveyPoint(x=110, y=210, z=151, metadata={'code': 'vk', 'number': 25}),
        SurveyPoint(x=120, y=220, z=152, metadata={'code': '3'}),
        SurveyPoint(x=130, y=230, z=153, metadata={'code': 'unknown'}),
        SurveyPoint(x=140, y=240, z=154, metadata={'code': 'shurf', 'number': 1}),
    ]
    
    result = engine.process_points(points)
    
    print("Statistics:")
    for key, value in result.statistics.items():
        print(f"  {key}: {value}")
    print()


def example_code_extraction():
    """Extract codes from strings."""
    print("=== Code Extraction ===\n")
    
    engine = RuleEngine()
    
    test_strings = [
        "vk25",
        "km+150",
        "shurf3",
        "k-kabel42",
        "1",
    ]
    
    for text in test_strings:
        code, number = engine.extract_code_from_string(text)
        print(f"{text:15} -> code: {code:10} number: {number}")
    
    print()


def main():
    """Run all examples."""
    print("=" * 60)
    print("CODE CATALOG AND RULE ENGINE EXAMPLES")
    print("=" * 60)
    print()
    
    example_basic_usage()
    example_process_single_point()
    example_multiple_codes()
    example_unknown_code()
    example_special_cases()
    example_statistics()
    example_code_extraction()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()
