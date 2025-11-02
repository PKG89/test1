"""Demonstration of the DXF geometry engine with scale management and 3D polylines."""

import tempfile
import os
from pathlib import Path

from src.dxf.generation_service import DXFGenerationService
from src.dxf.scale_settings import DrawingScale
from src.models.settings import DXFGenerationSettings


def demo_basic_usage():
    """Demonstrate basic usage of the geometry engine."""
    print("=== Demo 1: Basic DXF Generation ===")
    
    service = DXFGenerationService(scale=DrawingScale.SCALE_1_1000)
    
    print(f"Scale: {service.scale_manager.scale.value}")
    print(f"Text height: {service.scale_manager.get_text_height()}")
    print(f"Lineweight: {service.scale_manager.get_lineweight()}")
    
    points = [
        (1000.0, 2000.0, 150.250, 'bord'),
        (1005.0, 2000.0, 150.280, 'bord'),
        (1010.0, 2000.0, 150.310, 'bord'),
    ]
    
    for x, y, z, code in points:
        service.add_point_with_label(x, y, z, code, f'layer_{code}')
    
    output_file = tempfile.mktemp(suffix='_basic.dxf')
    service.save(output_file)
    
    print(f"✓ Saved to: {output_file}")
    print(f"  - Points: {len(points)}")
    print(f"  - Layers created: {len([l for l in service.doc.layers])}")
    print()


def demo_scale_comparison():
    """Demonstrate different scales affecting output."""
    print("=== Demo 2: Scale Comparison ===")
    
    scales = [
        DrawingScale.SCALE_1_500,
        DrawingScale.SCALE_1_1000,
        DrawingScale.SCALE_1_2000,
        DrawingScale.SCALE_1_5000,
    ]
    
    for scale in scales:
        service = DXFGenerationService(scale=scale)
        
        service.add_point_with_label(100, 200, 150, 'test', 'test_layer')
        
        output_file = tempfile.mktemp(suffix=f'_scale_{scale.value.replace(":", "_")}.dxf')
        service.save(output_file)
        
        print(f"✓ Scale {scale.value}:")
        print(f"  - Text height: {service.scale_manager.get_text_height()}")
        print(f"  - Lineweight: {service.scale_manager.get_lineweight()}")
        print(f"  - File: {os.path.basename(output_file)}")
    print()


def demo_3d_polylines():
    """Demonstrate 3D polyline generation with grouping."""
    print("=== Demo 3: 3D Polylines with Grouping ===")
    
    service = DXFGenerationService()
    
    points_data = [
        {'x': 1000.0, 'y': 2000.0, 'z': 150.0, 'code': 'bord', 'comment': '1'},
        {'x': 1010.0, 'y': 2000.0, 'z': 150.5, 'code': 'bord', 'comment': '1'},
        {'x': 1020.0, 'y': 2000.0, 'z': 151.0, 'code': 'bord', 'comment': '1'},
        {'x': 1000.0, 'y': 2010.0, 'z': 150.2, 'code': 'bord', 'comment': '2'},
        {'x': 1010.0, 'y': 2010.0, 'z': 150.7, 'code': 'bord', 'comment': '2'},
        {'x': 1000.0, 'y': 2020.0, 'z': 149.8, 'code': 'rels', 'comment': None},
        {'x': 1010.0, 'y': 2020.0, 'z': 150.3, 'code': 'rels', 'comment': None},
    ]
    
    polylines = service.build_3d_polylines(points_data, 'structures')
    
    output_file = tempfile.mktemp(suffix='_polylines.dxf')
    service.save(output_file)
    
    print(f"✓ Created {len(polylines)} polyline(s)")
    print(f"  - Input points: {len(points_data)}")
    print(f"  - Groups: bord_1, bord_2, rels")
    print(f"  - Break distance: {service.polyline_builder.break_distance}m")
    print(f"  - Saved to: {output_file}")
    print()


def demo_k_code_logic():
    """Demonstrate special k-code polyline logic."""
    print("=== Demo 4: K-code Special Logic ===")
    
    service = DXFGenerationService()
    
    points_data = [
        {'x': 1000.0, 'y': 2000.0, 'z': 150.0, 'code': 'k1', 'comment': None},
        {'x': 1010.0, 'y': 2005.0, 'z': 150.5, 'code': 'k1', 'comment': None},
        {'x': 1020.0, 'y': 2010.0, 'z': 151.0, 'code': 'k1', 'comment': None},
        {'x': 1005.0, 'y': 2015.0, 'z': 149.5, 'code': 'k2', 'comment': None},
        {'x': 1015.0, 'y': 2020.0, 'z': 150.0, 'code': 'k2', 'comment': None},
    ]
    
    polylines = service.build_3d_polylines(points_data, 'k_codes')
    
    output_file = tempfile.mktemp(suffix='_k_codes.dxf')
    service.save(output_file)
    
    print(f"✓ K-codes connected: k1, k2")
    print(f"  - All points with same k-code are connected")
    print(f"  - Created {len(polylines)} polyline(s)")
    print(f"  - Saved to: {output_file}")
    print()


def demo_break_distance():
    """Demonstrate polyline breaking at >70m distance."""
    print("=== Demo 5: Break Distance Logic ===")
    
    service = DXFGenerationService()
    
    points_data = [
        {'x': 0.0, 'y': 0.0, 'z': 100.0, 'code': 'bord', 'comment': None},
        {'x': 10.0, 'y': 0.0, 'z': 100.5, 'code': 'bord', 'comment': None},
        {'x': 20.0, 'y': 0.0, 'z': 101.0, 'code': 'bord', 'comment': None},
        {'x': 100.0, 'y': 0.0, 'z': 101.5, 'code': 'bord', 'comment': None},
        {'x': 110.0, 'y': 0.0, 'z': 102.0, 'code': 'bord', 'comment': None},
    ]
    
    polylines = service.build_3d_polylines(points_data, 'break_test')
    
    output_file = tempfile.mktemp(suffix='_break_distance.dxf')
    service.save(output_file)
    
    print(f"✓ Points with gap >70m are split into separate polylines")
    print(f"  - Input points: {len(points_data)}")
    print(f"  - Created polylines: {len(polylines)}")
    print(f"  - Expected: 2 (broken at x=100)")
    print(f"  - Saved to: {output_file}")
    print()


def demo_structural_layers():
    """Demonstrate structural layer colors."""
    print("=== Demo 6: Structural Layers with Colors ===")
    
    service = DXFGenerationService()
    
    structural_codes = ['bord', 'rels', 'bpl', 'cpl']
    
    for i, code in enumerate(structural_codes):
        x, y, z = 1000.0 + i * 10, 2000.0, 150.0 + i * 0.5
        service.add_point_with_label(x, y, z, code, f'layer_{code}')
    
    output_file = tempfile.mktemp(suffix='_structural.dxf')
    service.save(output_file)
    
    print(f"✓ Structural layers created:")
    for code in structural_codes:
        config = service.STRUCTURAL_LAYERS.get(code, {})
        color = config.get('color', 7)
        color_name = {0: 'Black', 3: 'Green', 7: 'White/Black'}.get(color, str(color))
        print(f"  - {code}: color {color} ({color_name})")
    print(f"  - Saved to: {output_file}")
    print()


def demo_special_codes():
    """Demonstrate special code rules (Fonar, Machta)."""
    print("=== Demo 7: Special Code Rules ===")
    
    service = DXFGenerationService()
    
    special_points = [
        {'x': 1000.0, 'y': 2000.0, 'z': 150.0, 'code': 'Fonar'},
        {'x': 1010.0, 'y': 2000.0, 'z': 150.5, 'code': 'Machta'},
    ]
    
    service.apply_special_code_rules(special_points, 'special')
    
    output_file = tempfile.mktemp(suffix='_special_codes.dxf')
    service.save(output_file)
    
    print(f"✓ Special code rules applied:")
    for code in ['Fonar', 'Machta']:
        rule = service.SPECIAL_CODE_RULES[code]
        print(f"  - {code}: color {rule['color']}, marker {rule['marker']}")
    print(f"  - Saved to: {output_file}")
    print()


def demo_complete_workflow():
    """Demonstrate complete workflow with all features."""
    print("=== Demo 8: Complete Workflow ===")
    
    settings = DXFGenerationSettings(
        enabled=True,
        drawing_scale='1:1000',
        show_z_labels=True,
        generate_3d_polylines=True,
        polyline_break_distance=70.0,
        coordinate_precision=3
    )
    
    service = DXFGenerationService(scale=DrawingScale.SCALE_1_1000)
    
    sample_points = [
        {'x': 1000.0, 'y': 2000.0, 'z': 150.250, 'code': 'bord', 'comment': '1'},
        {'x': 1005.0, 'y': 2000.0, 'z': 150.280, 'code': 'bord', 'comment': '1'},
        {'x': 1010.0, 'y': 2000.0, 'z': 150.310, 'code': 'bord', 'comment': '1'},
        {'x': 1000.0, 'y': 2005.0, 'z': 150.290, 'code': 'rels', 'comment': '1'},
        {'x': 1005.0, 'y': 2005.0, 'z': 150.320, 'code': 'rels', 'comment': '1'},
        {'x': 1010.0, 'y': 2005.0, 'z': 150.350, 'code': 'rels', 'comment': '1'},
    ]
    
    for point in sample_points:
        service.add_point_with_label(
            point['x'], point['y'], point['z'],
            point['code'], f"layer_{point['code']}",
            show_z_label=settings.show_z_labels
        )
    
    if settings.generate_3d_polylines:
        polylines = service.build_3d_polylines(sample_points, 'polylines')
    
    service.add_text_annotation('Sample Survey Data', 1000, 1995, 'annotations')
    
    output_file = tempfile.mktemp(suffix='_complete.dxf')
    service.save(output_file)
    
    print(f"✓ Complete workflow executed:")
    print(f"  - Points: {len(sample_points)}")
    print(f"  - Polylines: {len(polylines) if settings.generate_3d_polylines else 0}")
    print(f"  - Scale: {settings.drawing_scale}")
    print(f"  - Z labels: {'Yes' if settings.show_z_labels else 'No'}")
    print(f"  - Saved to: {output_file}")
    
    msp = service.doc.modelspace()
    print(f"\n  Entity counts:")
    print(f"    - Circles: {len(list(msp.query('CIRCLE')))}")
    print(f"    - Text: {len(list(msp.query('TEXT')))}")
    print(f"    - Polylines: {len(list(msp.query('POLYLINE')))}")
    print()


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("DXF Geometry Engine - Demonstration Suite")
    print("=" * 70 + "\n")
    
    demo_basic_usage()
    demo_scale_comparison()
    demo_3d_polylines()
    demo_k_code_logic()
    demo_break_distance()
    demo_structural_layers()
    demo_special_codes()
    demo_complete_workflow()
    
    print("=" * 70)
    print("All demonstrations completed successfully!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
