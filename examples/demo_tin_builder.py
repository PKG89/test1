"""Demonstration of TIN Surface Builder functionality."""

import numpy as np
from pathlib import Path

from src.models.point_data import PointCloud, Polyline
from src.models.settings import TINSettings, TINCodeSelection
from src.services.tin_service import TINService
from src.dxf.exporter import DXFExporter


def create_sample_terrain():
    """Create sample terrain with breaklines."""
    print("Creating sample terrain data...")
    
    # Generate grid of terrain points
    points = []
    metadata = []
    
    # Main terrain grid
    for x in range(0, 100, 10):
        for y in range(0, 100, 10):
            z = 100 + 0.1 * x + 0.05 * y + np.random.randn() * 0.5
            points.append([x, y, z])
            
            # Assign codes based on position
            if x == 50:  # Vertical breakline
                metadata.append({'code': 'bpl'})
            elif y == 50:  # Horizontal centerline
                metadata.append({'code': 'cpl'})
            elif x == 0 or x == 90 or y == 0 or y == 90:  # Borders
                metadata.append({'code': 'bord'})
            else:
                metadata.append({'code': 'terrain'})
    
    return PointCloud(points=np.array(points), point_metadata=metadata)


def demo_basic_tin():
    """Demonstrate basic TIN construction."""
    print("\n" + "="*60)
    print("Demo 1: Basic TIN Construction (All Points)")
    print("="*60)
    
    cloud = create_sample_terrain()
    
    settings = TINSettings(
        enabled=True,
        code_selection=TINCodeSelection.ALL,
        use_breaklines=False
    )
    
    service = TINService(settings)
    tin, stats = service.build_tin(cloud)
    
    print(f"✓ Points used: {stats['points_used']}")
    print(f"✓ Triangles created: {stats['triangle_count']}")
    print(f"✓ Quality metric: {stats['quality']:.3f}")
    print(f"✓ Breaklines: {stats['breakline_count']}")


def demo_terrain_only():
    """Demonstrate terrain-only TIN construction."""
    print("\n" + "="*60)
    print("Demo 2: Terrain Points Only")
    print("="*60)
    
    cloud = create_sample_terrain()
    
    settings = TINSettings(
        enabled=True,
        code_selection=TINCodeSelection.TERRAIN_ONLY,
        use_breaklines=False
    )
    
    service = TINService(settings)
    tin, stats = service.build_tin(cloud)
    
    print(f"✓ Total points: {cloud.count}")
    print(f"✓ Points used: {stats['points_used']}")
    print(f"✓ Points filtered: {stats['points_filtered']}")
    print(f"✓ Triangles created: {stats['triangle_count']}")


def demo_with_breaklines():
    """Demonstrate TIN with breakline constraints."""
    print("\n" + "="*60)
    print("Demo 3: TIN with Breaklines")
    print("="*60)
    
    cloud = create_sample_terrain()
    
    settings = TINSettings(
        enabled=True,
        code_selection=TINCodeSelection.WITH_BREAKLINES,
        use_breaklines=True,
        breakline_codes=['bpl', 'cpl', 'bord']
    )
    
    service = TINService(settings)
    tin, stats = service.build_tin(cloud)
    
    print(f"✓ Points used: {stats['points_used']}")
    print(f"✓ Triangles created: {stats['triangle_count']}")
    print(f"✓ Breaklines detected: {stats['breakline_count']}")
    print(f"✓ Quality metric: {stats['quality']:.3f}")
    
    if len(tin.breaklines) > 0:
        print(f"\nBreakline details:")
        for i, bl in enumerate(tin.breaklines):
            print(f"  - Breakline {i+1}: {len(bl.vertices)} vertices, code='{bl.code}'")


def demo_custom_codes():
    """Demonstrate custom code selection."""
    print("\n" + "="*60)
    print("Demo 4: Custom Code Selection")
    print("="*60)
    
    cloud = create_sample_terrain()
    
    settings = TINSettings(
        enabled=True,
        code_selection=TINCodeSelection.CUSTOM,
        custom_codes=['terrain', 'bpl'],
        use_breaklines=True,
        breakline_codes=['bpl']
    )
    
    service = TINService(settings)
    tin, stats = service.build_tin(cloud)
    
    print(f"✓ Custom codes: terrain, bpl")
    print(f"✓ Points used: {stats['points_used']}")
    print(f"✓ Triangles created: {stats['triangle_count']}")
    print(f"✓ Breaklines: {stats['breakline_count']}")


def demo_dxf_export():
    """Demonstrate DXF export with TIN."""
    print("\n" + "="*60)
    print("Demo 5: DXF Export with TIN Layers")
    print("="*60)
    
    cloud = create_sample_terrain()
    
    settings = TINSettings(
        enabled=True,
        code_selection=TINCodeSelection.WITH_BREAKLINES,
        use_breaklines=True,
        output_layers=True
    )
    
    service = TINService(settings)
    tin, stats = service.build_tin(cloud)
    
    # Export to DXF
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "demo_tin.dxf"
    
    exporter = DXFExporter()
    exporter.export_full_project(
        original_cloud=cloud,
        original_tin=tin,
        real_tin=tin,
        show_original=False,
        show_real_tin=True
    )
    
    exporter.save(str(output_file))
    
    print(f"✓ DXF file created: {output_file}")
    print(f"✓ Layers:")
    print(f"  - 1 реальная поверхность (Real Surface)")
    print(f"  - 1 Отметки и точки реального рельефа (Real Points)")
    print(f"✓ Triangles exported: {stats['triangle_count']}")
    print(f"✓ Points exported: {stats['points_used']}")


def demo_error_handling():
    """Demonstrate error handling."""
    print("\n" + "="*60)
    print("Demo 6: Error Handling")
    print("="*60)
    
    # Test with insufficient points
    print("\nTest 1: Insufficient points (< 3)")
    points = np.array([[0, 0, 100], [10, 0, 101]])
    cloud = PointCloud(points=points, point_metadata=[])
    
    settings = TINSettings(enabled=True)
    service = TINService(settings)
    tin, stats = service.build_tin(cloud)
    
    if stats['skipped']:
        print(f"✓ Handled gracefully: {stats.get('error', 'No error message')}")
    
    # Test with empty cloud
    print("\nTest 2: Empty point cloud")
    empty_cloud = PointCloud(points=np.array([]), point_metadata=[])
    tin, stats = service.build_tin(empty_cloud)
    
    if stats['skipped']:
        print(f"✓ Handled gracefully: Skipped={stats['skipped']}")
    
    # Test with disabled TIN
    print("\nTest 3: TIN disabled")
    settings = TINSettings(enabled=False)
    service = TINService(settings)
    cloud = create_sample_terrain()
    tin, stats = service.build_tin(cloud)
    
    if stats['skipped']:
        print(f"✓ Handled gracefully: TIN disabled, Skipped={stats['skipped']}")


def main():
    """Run all demonstrations."""
    print("\n" + "="*60)
    print("TIN Surface Builder - Feature Demonstration")
    print("="*60)
    print("\nThis demo showcases the TIN Surface Builder capabilities:")
    print("- Basic triangulation")
    print("- Point code filtering")
    print("- Breakline constraints")
    print("- Custom code selection")
    print("- DXF export")
    print("- Error handling")
    
    try:
        demo_basic_tin()
        demo_terrain_only()
        demo_with_breaklines()
        demo_custom_codes()
        demo_dxf_export()
        demo_error_handling()
        
        print("\n" + "="*60)
        print("All demonstrations completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
