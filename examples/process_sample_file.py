"""Example script to process sample survey data file."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.catalog_workflow import CatalogWorkflowService


def main():
    """Process sample survey data file."""
    sample_file = os.path.join(os.path.dirname(__file__), 'sample_survey_data.txt')
    
    print("=" * 70)
    print("PROCESSING SAMPLE SURVEY DATA")
    print("=" * 70)
    print(f"\nFile: {sample_file}\n")
    
    service = CatalogWorkflowService()
    
    validation = service.validate_file_format(sample_file)
    if validation['valid']:
        print(f"✓ File format valid: {validation['total_lines']} lines\n")
        print("Preview (first 5 points):")
        for item in validation['preview'][:5]:
            print(f"  {item['x']:8} {item['y']:8} {item['z']:8} "
                  f"{item['code']:12} {item['comment'] or ''}")
        print()
    
    print("Processing file with catalog...\n")
    result = service.process_file_with_catalog(sample_file)
    
    if result['success']:
        print("✓ Processing successful!\n")
        
        stats = result['statistics']
        print("Statistics:")
        print(f"  Total points:          {stats['total_points']}")
        print(f"  Known codes:           {stats['known_codes']}")
        print(f"  Unknown codes:         {stats['unknown_codes']}")
        print(f"  Missing data fallbacks: {stats['missing_data_fallbacks']}")
        print(f"  Special behaviors:     {stats['special_behaviors']}")
        print()
        
        payload = result['placement_payload']
        print("DXF Payload:")
        print(f"  Blocks:     {len(payload['blocks'])}")
        print(f"  Texts:      {len(payload['texts'])}")
        print(f"  Points:     {len(payload['points'])}")
        print(f"  Layers:     {len(payload['layers'])}")
        print()
        
        print("Layers used:")
        for layer in sorted(payload['layers'])[:15]:
            print(f"  - {layer}")
        if len(payload['layers']) > 15:
            print(f"  ... and {len(payload['layers']) - 15} more")
        print()
        
        print("Sample placement instructions (first 5):")
        for i, instruction in enumerate(result['instructions'][:5], 1):
            print(f"\n  {i}. Code: {instruction.code}")
            print(f"     Position: ({instruction.x:.1f}, {instruction.y:.1f}, {instruction.z:.1f})")
            if instruction.labels:
                print(f"     Labels: {', '.join(instruction.labels)}")
            if instruction.block:
                print(f"     Block: {instruction.block.block_name} on {instruction.block.layer}")
            if instruction.is_unknown:
                print(f"     ⚠ Unknown code - handled with point marker")
        
        if result['warnings']:
            print(f"\nWarnings ({len(result['warnings'])}):")
            for warning in result['warnings'][:5]:
                print(f"  ⚠ {warning}")
        
        from src.models.rule_data import RuleEngineResult
        rule_result = RuleEngineResult(
            instructions=result['instructions'],
            statistics=result['statistics'],
            warnings=result['warnings']
        )
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(service.generate_summary(rule_result))
        
    else:
        print(f"✗ Processing failed: {result.get('error')}")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
